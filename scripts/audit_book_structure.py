#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only transcription-structure audit (no writes).

Answers the question "did standardization actually capture 目錄 / 分段分行 /
小標題 for the existing books?" using signals already in the DB (char_count +
chapter_path are stored per chunk even though full content lives in JSONL/R2).

Per book it computes:
  - heading structure : # distinct non-empty chapter_path  → 小標題/目錄抓到沒
  - over-fragmentation : share of chunks with char_count < TINY → 分段碎裂
  - under-segmentation : any chunk char_count > GIANT        → 巨塊沒切開
  - per-page chunking  : chunk_count ≈ total_pages (PDF)     → Plan A,無章節結構

Flags (a book can carry several):
  NO_HEADINGS, OVER_FRAGMENTED, UNDER_SEGMENTED, PER_PAGE_ONLY,
  NOT_STANDARDIZED, NEEDS_OCR, PATH_BROKEN

Output: console summary + _structure_audit.txt (per-flag book lists).
Usage:  python scripts/audit_book_structure.py
"""
import collections
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TINY = 150          # chars; below this a chunk is a fragment
GIANT = 80_000       # chars; above this a chunk is an unsegmented blob
HEADING_MIN = 2      # distinct chapter_path values to count as "has structure"

BENIGN_PARSE_ERRORS = ("split from set",)
OCR_MARKERS = ("no extractable text", "pending_oversized")
PATH_MARKERS = ("file not found", "Failed to open", "WinError 2")


def load_env():
    env = {}
    for line in open(Path(__file__).parent.parent / ".env", encoding="utf-8-sig"):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _paginate(url_base, headers, select, step=10000):
    rows, off = [], 0
    while True:
        c = requests.get(f"{url_base}?select={select}&order=id&offset={off}&limit={step}",
                         headers=headers, timeout=120).json()
        rows.extend(c)
        if len(c) < step:
            break
        off += step
    return rows


def main():
    env = load_env()
    URL, KEY = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

    print("fetching ebooks meta…")
    books = {b["id"]: b for b in _paginate(
        f"{URL}/rest/v1/ebooks", H,
        "id,title,file_type,total_pages,chunk_count,standardized_at,parse_error", 1000)}

    print(f"fetching chunk stats for {len(books)} books (182K chunks, paginated)…")
    # per-book accumulators
    cnt = collections.Counter()
    tiny = collections.Counter()
    giant = collections.Counter()
    headings = collections.defaultdict(set)
    off, step = 0, 10000
    while True:
        c = requests.get(
            f"{URL}/rest/v1/ebook_chunks?select=ebook_id,char_count,chapter_path"
            f"&order=id&offset={off}&limit={step}", headers=H, timeout=180).json()
        for ch in c:
            eid = ch["ebook_id"]
            cnt[eid] += 1
            cc = ch.get("char_count") or 0
            if cc < TINY:
                tiny[eid] += 1
            if cc > GIANT:
                giant[eid] += 1
            cp = (ch.get("chapter_path") or "").strip()
            if cp:
                headings[eid].add(cp)
        if len(c) < step:
            break
        off += step
        print(f"  …{off} chunks scanned")

    flags = collections.defaultdict(list)
    for eid, b in books.items():
        pe = b.get("parse_error") or ""
        if any(m in pe for m in BENIGN_PARSE_ERRORS):
            continue  # set children — not a structure problem
        if any(m in pe for m in PATH_MARKERS):
            flags["PATH_BROKEN"].append(b); continue
        if any(m in pe for m in OCR_MARKERS):
            flags["NEEDS_OCR"].append(b); continue
        if not b.get("standardized_at"):
            flags["NOT_STANDARDIZED"].append(b)

        n = cnt.get(eid, 0)
        if n == 0:
            continue
        nhead = len(headings.get(eid, ()))
        if nhead < HEADING_MIN and n > 3:
            flags["NO_HEADINGS"].append(b)
        if tiny.get(eid, 0) / n > 0.5 and n > 5:
            flags["OVER_FRAGMENTED"].append(b)
        if giant.get(eid, 0) > 0:
            flags["UNDER_SEGMENTED"].append(b)
        tp = b.get("total_pages") or 0
        if b.get("file_type") == "pdf" and tp > 20 and n >= tp * 0.9 and nhead < HEADING_MIN:
            flags["PER_PAGE_ONLY"].append(b)

    out = Path("_structure_audit.txt")
    order = ["NO_HEADINGS", "OVER_FRAGMENTED", "UNDER_SEGMENTED", "PER_PAGE_ONLY",
             "NOT_STANDARDIZED", "NEEDS_OCR", "PATH_BROKEN"]
    desc = {
        "NO_HEADINGS": "目錄/小標題沒抓到（chapter_path 幾乎全空或單一）",
        "OVER_FRAGMENTED": "分段碎裂（>50% chunk < 150 字，多半 page-level 切碎）",
        "UNDER_SEGMENTED": "有巨塊沒切（單 chunk > 80K 字）",
        "PER_PAGE_ONLY": "PDF 純逐頁切、無章節結構（chunk≈頁數）",
        "NOT_STANDARDIZED": "從未標準化（standardized_at 空）",
        "NEEDS_OCR": "無可擷取文字，待 OCR",
        "PATH_BROKEN": "Drive 檔案路徑壞掉 / 開不了",
    }
    with out.open("w", encoding="utf-8") as f:
        f.write(f"ebooks total: {len(books)}\n\n")
        for k in order:
            f.write(f"=== {k}  ({len(flags[k])}) — {desc[k]} ===\n")
            for b in sorted(flags[k], key=lambda x: -(x.get("chunk_count") or 0)):
                f.write(f"  [{b.get('file_type')}] pages={b.get('total_pages')} "
                        f"chunks={b.get('chunk_count')} | {(b.get('title') or '')[:60]!r}\n")
            f.write("\n")

    print("\n=== STRUCTURE AUDIT SUMMARY ===")
    for k in order:
        print(f"  {len(flags[k]):5d}  {k}  — {desc[k]}")
    print(f"\nfull report -> {out}")


if __name__ == "__main__":
    main()
