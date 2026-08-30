#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替站上的教父卷補上第三欄「原文」（拉丁／希臘），成為 中文 / 英文 / 原文 三欄對照。

  python scripts/fathers_add_original.py --work augustine-confessions          # 只驗，不寫
  python scripts/fathers_add_original.py --work augustine-confessions --apply  # 寫回 JSONL

站上教父卷本來就是兩欄：content 是繁中精修，source_text 是 Schaff 英譯。本腳本
補的是第三欄原典，對齊靠古典分章（liber.caput），不做語意對齊。

流程：
  ① 抓原典 → 按 卷.章 切段（scripts/fathers_original.py 的純函式）
  ② **覆蓋率閘**：站上章節 vs 原典章節，缺章或多章一律先報出來
  ③ 逐段組裝 sources[原文語言]；範圍內任何一章缺就整段留白
  ④ --apply 才寫回 {id}.jsonl，並鏡射 source_text/source_lang 給舊的兩欄 reader

🚨 覆蓋率閘不是形式。首跑《懺悔錄》就靠它抓到站上卷一只到第 18 章、第 19–20 章
   中英文都不存在。沒有閘的話那兩章拉丁文會被併進第 18 章那一段，三欄看起來齊、
   內容從那裡開始錯位，而畫面上完全看不出來。

🚨 只讀寫 {id}.jsonl。同目錄下的 .en.bak.jsonl 與 .bak_pre_merge 是翻譯前的英文
   原檔，段數對不上（Augustine Confessions 正式檔 68 段、英文備份 481 段）。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fathers_original", ROOT / "scripts" / "fathers_original.py")
FO = importlib.util.module_from_spec(_spec)
sys.modules["fathers_original"] = FO
_spec.loader.exec_module(FO)


# ── 取源登錄 ────────────────────────────────────────────────────────────────
# 每一部著作登記：站上是哪一本 ebook、原文語言、原典從哪裡抓、每卷幾章。
# `chapters` 是原典的權威章數，用來判站上有沒有缺章——不可以拿站上的章數回填。
WORKS: dict[str, dict] = {
    "augustine-confessions": {
        "label": "奧古斯丁《懺悔錄》",
        "ebook_id": "9edb7c37-4231-412b-83bd-78f3f793cc0a",
        "prefix": "懺悔錄",
        "lang": "la",
        "urls": [f"https://www.thelatinlibrary.com/augustine/conf{b}.shtml"
                 for b in range(1, 14)],
        "chapters": {1: 20, 2: 10, 3: 12, 4: 16, 5: 14, 6: 16, 7: 21,
                     8: 12, 9: 13, 10: 43, 11: 31, 12: 32, 13: 38},
        "source": "The Latin Library（Corpus Christianorum 系 Verheijen 校本，公有領域）",
    },
}


def fetch_original(spec: dict) -> dict[tuple[int | None, int, int | None], str]:
    """抓原典並切成 {(卷, 章, 節): 原文}。"""
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (know-graph-lab fathers-original)"
    out: dict[tuple[int | None, int, int | None], str] = {}
    for i, url in enumerate(spec["urls"], 1):
        r = s.get(url, timeout=45)
        r.raise_for_status()
        got = FO.parse_numbered_text(FO.strip_html(r.text), default_book=i)
        out.update(got)
        print(f"  抓 {url.rsplit('/', 1)[-1]:16} → {len(got)} 節")
    return out


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, choices=sorted(WORKS))
    ap.add_argument("--chunks-dir", default=None)
    ap.add_argument("--apply", action="store_true", help="寫回 JSONL（預設只驗不寫）")
    a = ap.parse_args()

    spec = WORKS[a.work]
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))
    raw = a.chunks_dir or os.environ.get("EBOOK_CHUNKS_DIR") or ""
    # 🚨 別偷懶寫 Path(raw).is_dir()——Path("") 等於「.」，在 Windows 上是存在的，
    # 環境變數沒讀到時會安靜地把工作目錄當成 chunks 目錄，然後報「找不到檔案」。
    if not raw:
        print("EBOOK_CHUNKS_DIR 沒設（.env 讀不到？）")
        return 1
    chunks_dir = Path(raw)
    if not chunks_dir.is_dir():
        print(f"找不到 chunks 目錄 {chunks_dir}（Drive 沒掛？）")
        return 1
    path = chunks_dir / f"{spec['ebook_id']}.jsonl"
    if not path.exists():
        print(f"找不到 {path}")
        return 1

    print(f"《{spec['label']}》 原文 {spec['lang']} ← {spec['source']}")
    sections = fetch_original(spec)
    chapters = FO.by_chapter(sections)     # 覆蓋率閘看章
    paragraphs = FO.by_paragraph(sections)  # 逐段對齊看節
    print(f"原典共 {len(chapters)} 章 / {len(paragraphs)} 節\n")

    chunks = load_chunks(path)
    spans: dict[int, FO.Span] = {}
    for c in chunks:
        cp = c.get("chapter_path") or ""
        if not cp.startswith(spec["prefix"]):
            continue
        # 「卷二」整卷一段時要餵該卷章數才解得出範圍
        book_hint = None
        m = FO.CHAPTER_PATH.search(cp)
        if m and m.group(2) is None:
            book_hint = spec["chapters"].get(FO.ZH_NUM.get(m.group(1), -1))
        s = FO.parse_chapter_path(cp, chapters_in_book=book_hint)
        if s:
            spans[c["chunk_index"]] = s

    print(f"站上可對齊段落 {len(spans)} / 全書 {len(chunks)} 段")

    covs = FO.coverage(list(spans.values()), chapters)
    bad = [c for c in covs if not c.ok]
    print(f"\n覆蓋率閘：{len(covs) - len(bad)} / {len(covs)} 卷齊全")
    for c in bad:
        print(f"  ⚠ 卷 {c.book}：站上缺第 {c.missing} 章"
              + (f"；站上多出第 {c.extra} 章" if c.extra else ""))

    done = 0
    hit_total = num_total = 0
    updated: list[dict] = []
    for c in chunks:
        s = spans.get(c["chunk_index"])
        if not s:
            updated.append(c)
            continue
        body = FO.split_body(c.get("content") or "")
        col, hit, numbered = FO.align_by_paragraph_number(body, s.book, paragraphs)
        hit_total += hit
        num_total += numbered
        if not hit:
            # 一節都對不上 → 那一段的節號跟原典編號體系不一致，別硬塞
            print(f"  ⚠ 「{c['chapter_path']}」{numbered} 個帶節號的段落全對不上，跳過")
            updated.append(c)
            continue
        if hit < numbered:
            print(f"  · 「{c['chapter_path']}」{hit}/{numbered} 節配到原文，其餘留白")
        sources, order = FO.build_sources(
            c.get("sources"), c.get("source_text"), c.get("source_lang"),
            FO.render_column(col), spec["lang"])
        updated.append({**c, "sources": sources, "source_order": order,
                        # 舊的兩欄 reader 讀 source_text/source_lang，主欄仍是英譯
                        "source_lang": order[0], "source_text": sources[order[0]]})
        done += 1

    pct = f"{hit_total / num_total:.0%}" if num_total else "—"
    print(f"\n補上原文欄 {done} 段；逐節命中 {hit_total} / {num_total}（{pct}）")

    if not a.apply:
        print("\n（只驗不寫。確認無誤後加 --apply）")
        return 0

    backup = path.with_suffix(".jsonl.bak_pre_original")
    if not backup.exists():
        shutil.copy2(path, backup)
        print(f"備份 → {backup.name}")
    path.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in updated) + "\n",
        encoding="utf-8")
    print(f"寫回 {path.name}（{len(updated)} 段）")
    print("🚨 線上還要把 JSONL 推到 R2 才會生效（見 server/utils/ebook-chunks.ts）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
