#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find books that should switch to 原頁模式 (display_mode='page-image').

Philosophy (見交接): 掃描／無TOC／版面亂、轉錄怎麼調都跑掉的「問題書」，與其跟
轉錄死磕，不如用 pdf.js 即時渲染真實 PDF 頁面（忠實原貌），右側 OCR 文字僅供
搜尋/複製。翻譯/對照書（教父/Denzinger/全集）仍走文字 reader，不在此列。

A book is a page-image candidate when ALL of:
  - file_type == 'pdf'            （epub 原樣渲染另走 epub.js，暫不納入）
  - file_path is set             （pdf.js 要有原檔才能渲染；PATH_BROKEN 排除）
  - display_mode != 'bilingual-parallel'  （對照書排除）
  - 轉錄品質差，符合至少一項：
      NEEDS_OCR        無可擷取文字（掃描檔，OCR 還沒跑或跑不出）→ 最該讀真頁
      PER_PAGE_ONLY    PDF 純逐頁切、無章節結構（chunk≈頁數）
      NO_HEADINGS      目錄/小標題整本抓不到（chapter_path 幾乎全空）且未標準化

Read-only. Writes a review file _page_image_review.md (勾選後給
_apply_page_image.py 套用). 不直接改 DB。

Usage:  python scripts/audit_page_image_candidates.py
"""
import collections
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HEADING_MIN = 2
OCR_MARKERS = ("no extractable text", "pending_oversized")
PATH_MARKERS = ("file not found", "Failed to open", "WinError 2")
BENIGN_PARSE_ERRORS = ("split from set",)

REVIEW = Path("_page_image_review.md")


def load_env():
    env = {}
    for line in open(Path(__file__).parent.parent / ".env", encoding="utf-8-sig"):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main():
    env = load_env()
    URL, KEY = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

    print("fetching ebooks meta…")
    books = {}
    off, step = 0, 1000
    sel = ("id,title,file_type,file_path,total_pages,chunk_count,"
           "standardized_at,parse_error,display_mode,category,subcategory")
    while True:
        c = requests.get(f"{URL}/rest/v1/ebooks?select={sel}&order=id&offset={off}&limit={step}",
                         headers=H, timeout=120).json()
        for b in c:
            books[b["id"]] = b
        if len(c) < step:
            break
        off += step

    print(f"fetching chunk stats for {len(books)} books…")
    cnt = collections.Counter()
    headings = collections.defaultdict(set)
    off = 0
    step = 10000
    while True:
        c = requests.get(
            f"{URL}/rest/v1/ebook_chunks?select=ebook_id,chapter_path"
            f"&order=id&offset={off}&limit={step}", headers=H, timeout=180).json()
        for ch in c:
            eid = ch["ebook_id"]
            cnt[eid] += 1
            cp = (ch.get("chapter_path") or "").strip()
            if cp:
                headings[eid].add(cp)
        if len(c) < step:
            break
        off += step
        print(f"  …{off} chunks scanned")

    candidates = []   # (confidence, reason, book)
    already = []
    for eid, b in books.items():
        if b.get("display_mode") == "page-image":
            already.append(b)
            continue
        if b.get("file_type") != "pdf":
            continue
        if not b.get("file_path"):
            continue  # no renderable original
        if b.get("display_mode") == "bilingual-parallel":
            continue
        pe = b.get("parse_error") or ""
        if any(m in pe for m in BENIGN_PARSE_ERRORS):
            continue
        if any(m in pe for m in PATH_MARKERS):
            continue  # can't render a broken path

        n = cnt.get(eid, 0)
        nhead = len(headings.get(eid, ()))
        tp = b.get("total_pages") or 0

        reason = None
        conf = None
        if any(m in pe for m in OCR_MARKERS):
            reason = "NEEDS_OCR 無可擷取文字（掃描檔）→ 讀真頁最合適"
            conf = "strong"
        elif b.get("file_type") == "pdf" and tp > 20 and n >= tp * 0.9 and nhead < HEADING_MIN:
            reason = f"PER_PAGE_ONLY 純逐頁切無章節（{n} chunk ≈ {tp} 頁）"
            conf = "strong"
        elif nhead < HEADING_MIN and n > 3 and not b.get("standardized_at"):
            reason = f"NO_HEADINGS 目錄整本抓不到（{nhead} 個 chapter_path）且未標準化"
            conf = "maybe"

        if reason:
            candidates.append((conf, reason, b))

    strong = [c for c in candidates if c[0] == "strong"]
    maybe = [c for c in candidates if c[0] == "maybe"]

    def fmt(b, reason):
        title = (b.get("title") or "").replace("\n", " ")[:70]
        cat = b.get("subcategory") or b.get("category") or "—"
        pg = b.get("total_pages") or "?"
        return (f"- [ ] `{b['id']}`  **{title}**  · {cat} · {pg}頁\n"
                f"      ↳ {reason}\n")

    with REVIEW.open("w", encoding="utf-8") as f:
        f.write("# 原頁模式（page-image）候選審查\n\n")
        f.write("把要切成「原頁模式」的書勾成 `[x]`，存檔後跑：\n")
        f.write("`python scripts/_apply_page_image.py`（只套已勾選的；不勾的不動）\n\n")
        f.write(f"目前已是 page-image：{len(already)} 本　|　")
        f.write(f"高信心候選：{len(strong)} 本　|　待確認：{len(maybe)} 本\n\n")
        f.write("> 哲學：掃描/無TOC/版面亂的問題書讀真頁；翻譯/對照書（教父/Denzinger/全集）仍走文字 reader。\n\n")

        f.write(f"## 🟢 高信心候選（{len(strong)}）— 掃描檔/純逐頁，轉錄無望\n\n")
        for _, reason, b in sorted(strong, key=lambda x: -(x[2].get("total_pages") or 0)):
            f.write(fmt(b, reason))
        f.write("\n")

        f.write(f"## 🟡 待確認（{len(maybe)}）— 目錄沒抓到但可能轉錄堪用\n\n")
        for _, reason, b in sorted(maybe, key=lambda x: -(x[2].get("total_pages") or 0)):
            f.write(fmt(b, reason))
        f.write("\n")

        if already:
            f.write(f"## ✅ 已是原頁模式（{len(already)}）\n\n")
            for b in sorted(already, key=lambda x: (x.get("title") or "")):
                f.write(f"- `{b['id']}`  {(b.get('title') or '')[:70]}\n")

    print("\n=== PAGE-IMAGE CANDIDATES ===")
    print(f"  已是 page-image : {len(already)}")
    print(f"  🟢 高信心候選   : {len(strong)}")
    print(f"  🟡 待確認       : {len(maybe)}")
    print(f"\nreview -> {REVIEW}")


if __name__ == "__main__":
    main()
