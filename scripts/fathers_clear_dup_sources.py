#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「同一塊文字重複掛在連續好幾段」的來源欄清成空字串。

  python scripts/fathers_clear_dup_sources.py --book 709f43f9-… --lang la          # 只驗
  python scripts/fathers_clear_dup_sources.py --book 709f43f9-… --lang la --apply

## 為什麼要清

2026-09-11 稽核查到三本書的原典欄是**整卷**重複：希拉里《論三位一體》一塊 48,823 字
的拉丁文掛在連續 36 段上，讀者翻到卷六任何一頁，原典欄都是整卷。病灶是
`chapter_path` 被正文吞掉（見 `fathers_repair_chapter_paths.py`），對齊器認不出那些
段就跳過，於是它們留著建書當初掛上的整卷。

路徑修好之後要跑這一支，再跑 `fathers_add_original.py --apply` 逐段重建。順序不能反：
對齊器只會覆寫它對得上的段，對不上的段會**原樣留著整卷**——不先清，修完仍有一半是錯的。

🚨 **清成空字串，不是刪掉整個 key**。reader 的 `normalizeSources` 會拿 `source_order`
   去查 `sources`，key 不見時的行為與空字串不同；而且空字串正是這條線的既定作法——
   對不上就留空，不猜（[[feedback_transcribe_page_numbers]] 同一個原則）。

🚨 **只清「整塊重複」的，不清短的**。兩封信引同一句經文（23–42 字）本來就會重複，
   清掉是真的丟資料。門檻與稽核工具同步，預設 500 字。
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DUP_MIN_CHARS = 500


def dup_indices(chunks: list[dict], lang: str, min_chars: int = DUP_MIN_CHARS) -> list[int]:
    """回傳「該語言欄與別段一字不差、且夠長」的段序（在 chunks 裡的位置）。"""
    groups: dict[tuple[int, str], list[int]] = collections.defaultdict(list)
    for i, c in enumerate(chunks):
        text = ((c.get("sources") or {}).get(lang)) or ""
        if len(text) < min_chars:
            continue
        groups[(len(text), text[:120])].append(i)
    out: list[int] = []
    for idxs in groups.values():
        if len(idxs) > 1:
            out.extend(idxs)
    return sorted(out)


def clear_langs(chunk: dict, lang: str) -> bool:
    """把該段的某語言來源欄清成空字串；有動到回 True。

    `source_text`／`source_lang` 是給舊兩欄 reader 的鏡射，指到同一個語言時要一起清，
    不然舊 reader 照樣顯示整卷。
    """
    src = chunk.get("sources")
    if not isinstance(src, dict) or not (src.get(lang) or "").strip():
        return False
    src[lang] = ""
    if chunk.get("source_lang") == lang:
        chunk["source_text"] = ""
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--lang", required=True, help="la / grc / en")
    ap.add_argument("--min-chars", type=int, default=DUP_MIN_CHARS)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    raw = os.environ.get("EBOOK_CHUNKS_DIR") or ""
    if not raw:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("EBOOK_CHUNKS_DIR="):
                raw = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not raw:
        print("EBOOK_CHUNKS_DIR 沒設（.env 讀不到？）")
        return 1
    path = Path(raw) / f"{a.book}.jsonl"
    if not path.exists():
        print(f"找不到 {path}")
        return 1

    chunks = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    chunks.sort(key=lambda c: c.get("chunk_index", 0))
    idxs = dup_indices(chunks, a.lang, a.min_chars)
    print(f"{a.book[:8]}  {a.lang}：共 {len(chunks)} 段，整塊重複 {len(idxs)} 段")
    if idxs:
        print(f"  段序 #{chunks[idxs[0]]['chunk_index']} … #{chunks[idxs[-1]]['chunk_index']}")

    if not a.apply:
        print("（只驗不寫。確認無誤後加 --apply）")
        return 0
    if not idxs:
        return 0

    bak = path.with_suffix(f".jsonl.bak_dup_{a.lang}")
    if not bak.exists():
        shutil.copy2(path, bak)
        print(f"備份 → {bak.name}")
    n = sum(1 for i in idxs if clear_langs(chunks[i], a.lang))
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                   encoding="utf-8")
    tmp.replace(path)
    print(f"已清空 {n} 段的 {a.lang} 欄")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
