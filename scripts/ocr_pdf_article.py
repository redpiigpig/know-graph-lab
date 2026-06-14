#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""數位化本地 PDF 期刊論文 → 逐頁繁中全文（引擎 = Haiku 4.5 vision）。

給「文字層損毀／自訂字型亂碼」的 PDF（如林建德〈印順及聖嚴「如來藏」…〉）用：
直接把每頁 render 成圖片再 OCR，繞過壞掉的 text layer。輸出格式與
ocr_interview_book.py 一致（<out>/p###.txt，開頭【頁 N】），可共用
ingest_interview_sections.py 入庫。

論文＝完整連續轉錄（不可省略接續句、保留註腳）；保留印刷頁碼【頁 N】、略過圖表圖說。

  python -X utf8 scripts/ocr_pdf_article.py --pdf "<x.pdf>" --out scripts/data/<slug> \
      --title "印順及聖嚴「如來藏」觀點之對比考察" [--zoom 2.5] [--resume] [--limit N]
"""
import argparse
import base64
import sys
import time
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dadaodao_fulltext import anthropic_client, _is_quota

HAIKU = "claude-haiku-4-5"
PROMPT_TMPL = (
    "這是學術論文《{title}》的第 {n}／{N} 頁。請**完整**轉錄頁面中的繁體中文正文，作為研究參考資料。\n"
    "要求：\n"
    "1. 逐字、完整轉錄（含標題、內文、**註腳**）；這是整篇論文的一頁，**不要省略接續句**、不要摘要、不要翻譯、不要加任何說明。\n"
    "2. 保留段落與標題結構；**忽略圖片／表格的圖說文字**。\n"
    "3. 若頁面看得到**印刷頁碼**，在最前面用「【頁 N】」標出；看不到就寫「【頁 ?】」。\n"
    "只輸出轉錄文字（含開頭的頁碼標記），不要任何前言。"
)


def ocr_page(png_b64: str, prompt: str) -> str:
    client = anthropic_client()
    msg = client.messages.create(
        model=HAIKU, max_tokens=8000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": png_b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--zoom", type=float, default=2.5)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pace", type=float, default=0.5)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.pdf)
    N = doc.page_count
    mat = fitz.Matrix(args.zoom, args.zoom)
    print(f"{N} pages in {Path(args.pdf).name}", flush=True)
    done = fail = strikes = 0
    for i in range(N):
        dst = out / f"p{i+1:03d}.txt"
        if args.resume and dst.exists() and dst.read_text(encoding="utf-8").strip():
            continue
        try:
            png = doc[i].get_pixmap(matrix=mat).tobytes("png")
            b64 = base64.standard_b64encode(png).decode()
            text = ocr_page(b64, PROMPT_TMPL.format(title=args.title, n=i + 1, N=N))
            strikes = 0
            dst.write_text(text, encoding="utf-8")
            done += 1
            head = text.splitlines()[0] if text else ""
            print(f"  ✓ [{i+1}/{N}] → {len(text)} chars  {head[:36]}", flush=True)
            if args.limit and done >= args.limit:
                break
            time.sleep(args.pace)
        except Exception as e:  # noqa: BLE001
            if _is_quota(e):
                strikes += 1
                print(f"  ⏸ quota strike {strikes}/2 — p{i+1}", flush=True)
                if strikes >= 2:
                    print("\n2-strike 停機；--resume 可接續。", flush=True)
                    break
                time.sleep(20)
            else:
                fail += 1
                print(f"  ✗ p{i+1}: {type(e).__name__}: {str(e)[:160]}", flush=True)
    doc.close()
    print(f"\nDONE — ocr {done}, failed {fail}; output → {out}", flush=True)


if __name__ == "__main__":
    main()
