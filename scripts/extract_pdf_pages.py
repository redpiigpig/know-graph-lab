#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文字層乾淨的 PDF 期刊論文 → 逐頁文字（免 OCR，PyMuPDF 直接抽）。

輸出格式與 ocr_*.py 一致（<out>/p###.txt，開頭【頁 N】），共用
ingest_interview_sections.py 入庫。印刷頁碼 = --page-start + 物理頁序-1
（期刊抽印本物理頁與印刷頁多為 1:1）。

  python -X utf8 scripts/extract_pdf_pages.py --pdf "<x.pdf>" --out scripts/data/<slug> \
      --page-start 131
"""
import argparse
from pathlib import Path

import fitz  # PyMuPDF


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--page-start", type=int, required=True,
                    help="印刷頁碼起始（對應物理第 1 頁）")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.pdf)
    total = doc.page_count
    n = 0
    for i in range(total):
        text = doc[i].get_text().strip()
        if not text:
            continue
        printed = args.page_start + i
        body = f"【頁 {printed}】\n\n{text}"
        (out / f"p{i+1:03d}.txt").write_text(body, encoding="utf-8")
        n += 1
    doc.close()
    print(f"extracted {n}/{total} pages → {out}")


if __name__ == "__main__":
    main()
