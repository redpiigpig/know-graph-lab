# -*- coding: utf-8 -*-
"""弘誓雙月刊全文：抽 PDF 文字層（免 API，116/117 乾淨）→ 掃描檔退 Gemini Vision OCR。
存 R2 `yinshun-hongshi-fulltext/弘誓雙月刊/<檔名>.txt`（仿 dadaodao 全文管線）。

冪等：R2 已有 .txt 跳過。OCR 引擎與 R2 client 沿用 dadaodao_fulltext。

  python -X utf8 scripts/hongshi_ocr_magazine.py [--limit N] [--force-ocr]
"""
import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hongshi as h            # noqa: E402  pure helpers (pdf_text_sufficient)
import dadaodao_fulltext as df  # noqa: E402  reuse .env / s3 / gemini→sonnet OCR

SRC = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\弘誓雙月刊")
PREFIX = "yinshun-hongshi-fulltext/弘誓雙月刊"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force-ocr", action="store_true", help="即使有文字層也跑 Vision OCR")
    args = ap.parse_args()

    pdfs = sorted(SRC.glob("*.pdf"))
    done = skip = ocr = fail = 0
    strikes = 0
    for p in pdfs:
        key = f"{PREFIX}/{p.stem}.txt"
        if df.r2_exists(key):
            skip += 1
            continue
        try:
            doc = fitz.open(str(p))
            n = doc.page_count
            txt = "".join(pg.get_text() for pg in doc)
            doc.close()
            if not args.force_ocr and h.pdf_text_sufficient(txt, n):
                df.r2_put_text(key, txt.strip())
                done += 1
                strikes = 0
                print(f"  ✓ {p.name} [text-layer] {len(txt)} chars", flush=True)
            else:
                text, eng = df.ocr_file(p, "application/pdf")
                if not text.strip():
                    print(f"  ∅ empty OCR: {p.name}", flush=True); fail += 1; continue
                df.r2_put_text(key, text.strip())
                ocr += 1
                strikes = 0
                print(f"  ✓ {p.name} [vision-ocr:{eng}] {len(text)} chars", flush=True)
            if args.limit and (done + ocr) >= args.limit:
                break
        except df.BothLimited:
            strikes += 1
            print(f"  ⏸ quota strike {strikes}/2 — {p.name}", flush=True)
            if strikes >= 2:
                print("\n2-strike 配額停機；稍後重跑可接續。", flush=True)
                break
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"  ✗ {p.name}: {type(e).__name__}: {str(e)[:160]}", flush=True)
    print(f"\nDONE text-layer {done}, vision-ocr {ocr}, skipped {skip}, failed {fail}", flush=True)


if __name__ == "__main__":
    main()
