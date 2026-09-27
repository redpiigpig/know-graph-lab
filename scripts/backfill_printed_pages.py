#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""替「有文字層、一頁一塊」的 PDF 回填原書印刷頁碼 `printed_page`（2026-09-27）。

背景：專案慣例 `page_number`＝PDF 實體頁序，`printed_page`＝書上印的頁碼（見 mineru_ocr.to_chunks）。
MinerU 管線會填 printed_page，但有文字層、走舊解析的 PDF（稽核時約 1,748 本）只有實體頁序——
前言用羅馬數字、插頁不編號時兩者錯開，照實體頁序引用會引錯頁。

做法（只加欄位，不動 content）：
  1. 每頁取頭兩行、末兩行找頁碼：單獨數字「12」「- 12 -」、書眉＋數字「導論 12」、數字＋書眉「12 導論」
  2. 跟前後鄰居的位移（實體頁序 − 印刷頁碼）對不上的丟掉（同 mineru_ocr.drop_isolated_printed_pages）
  3. 全書驗證過的頁不到 30% → 整本放棄（寧可留空，假頁碼比沒有更糟）

  python -X utf8 scripts/backfill_printed_pages.py --dry-run          # 全館統計
  python -X utf8 scripts/backfill_printed_pages.py --apply [--ids ...] # 寫 JSONL（留 .jsonl.bak_printed）＋推 R2
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
MIN_COVERAGE = 0.30
_NUM_ONLY = re.compile(r"^[\-–—\s·•\[\(（]*(\d{1,4})[\-–—\s·•\]\)）]*$")
_NUM_HEAD = re.compile(r"^(\d{1,4})\s{1,6}\S.{0,40}$")
_HEAD_NUM = re.compile(r"^\S.{0,40}?\s{1,6}(\d{1,4})$")


def candidate(text: str) -> int | None:
    """一頁的內容 → 候選印刷頁碼（找不到回 None）。純函式。"""
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    if not lines:
        return None
    # 先首行、末行，再第二行、倒數第二行：倒數第二行常是單獨的註腳號「1」（2026-09-27 抽查）
    probe = [lines[0], lines[-1]] + lines[1:2] + lines[-2:-1]
    for l in probe:
        m = _NUM_ONLY.match(l)
        if m:
            return int(m.group(1))
    for l in probe:
        m = _NUM_HEAD.match(l) or _HEAD_NUM.match(l)
        if m and len(l) <= 45:
            return int(m.group(1))
    return None


def validate(cands: list[tuple[int, int | None]]) -> dict[int, int]:
    """[(實體頁序, 候選)] → {實體頁序: 印刷頁碼}，只留跟前後鄰居位移一致的。純函式。"""
    numbered = [(pg, c) for pg, c in cands if c]
    offsets = [pg - c for pg, c in numbered]
    out = {}
    for i, (pg, c) in enumerate(numbered):
        nb = offsets[max(0, i - 1):i] + offsets[i + 1:i + 2]
        if nb and offsets[i] in nb:
            out[pg] = c
    return out


def fill_book(chunks: list[dict]) -> tuple[int, int]:
    """就地填 printed_page；回傳 (填了幾頁, 頁數)。覆蓋率不足時不動，回傳 (0, 頁數)。"""
    pages = [c for c in chunks if c.get("chunk_type") == "page" and isinstance(c.get("page_number"), int)]
    if not pages:
        return 0, 0
    got = validate([(c["page_number"], candidate(c.get("content") or "")) for c in pages])
    if len(got) < MIN_COVERAGE * len(pages):
        return 0, len(pages)
    for c in pages:
        c["printed_page"] = got.get(c["page_number"])
    return len(got), len(pages)


def eligible(chunks: list[dict]) -> bool:
    if not chunks or any("printed_page" in c for c in chunks[:50]):
        return False
    pages = sum(1 for c in chunks if c.get("chunk_type") == "page")
    return pages >= 10 and pages >= 0.6 * len(chunks)


def main() -> int:
    apply = "--apply" in sys.argv
    ids = sys.argv[sys.argv.index("--ids") + 1:] if "--ids" in sys.argv else None
    files = [CH / f"{i}.jsonl" for i in ids] if ids else sorted(CH.glob("*.jsonl"))
    stat = {"books": 0, "filled_books": 0, "low_coverage": 0, "pages": 0, "filled_pages": 0}
    rows = []
    if apply:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import standardize_ebook as se  # noqa: E402
    for n, p in enumerate(files):
        try:
            chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception:  # noqa: BLE001
            continue
        if not eligible(chunks):
            continue
        stat["books"] += 1
        filled, total = fill_book(chunks)
        stat["pages"] += total
        if not filled:
            stat["low_coverage"] += 1
            continue
        stat["filled_books"] += 1
        stat["filled_pages"] += filled
        rows.append(f"{p.stem}\t{filled}\t{total}")
        if apply:
            bak = p.with_suffix(".jsonl.bak_printed")
            if not bak.exists():
                shutil.copy2(p, bak)
            tmp = p.with_suffix(".jsonl.tmp")
            tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n", encoding="utf-8")
            tmp.replace(p)
            se.push_to_r2(p.stem, p)
        if n % 500 == 0:
            print(n, stat, flush=True)
    out = Path(__file__).resolve().parents[1] / "output" / "toc_audit" / "printed_pages.tsv"
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("SUMMARY", stat, flush=True)
    print("PRINTED_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
