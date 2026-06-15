# -*- coding: utf-8 -*-
"""逐頁 OCR 一本掃描型弘誓雙月刊（整本 PDF 過大 → 413 時用此）。
把每頁 render 成 PNG 送 Gemini Vision，串接後存 R2 `yinshun-hongshi-fulltext/弘誓雙月刊/<stem>.txt`。

  python -X utf8 scripts/hongshi_ocr_pages.py --issue 103
"""
import argparse
import sys
import time
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # reuse .env / s3 / GEMINI_KEYS / OCR_PROMPT

SRC = Path(r"G:\我的雲端硬碟\公事\印順學派與弘誓研究資料\弘誓雙月刊")
PREFIX = "yinshun-hongshi-fulltext/弘誓雙月刊"


def gemini_image_ocr(png: bytes) -> str:
    from google import genai
    from google.genai import types
    last = None
    for off in range(len(df.GEMINI_KEYS)):
        idx = (df._gem_idx + off) % len(df.GEMINI_KEYS)
        try:
            client = genai.Client(api_key=df.GEMINI_KEYS[idx])
            resp = client.models.generate_content(
                model=df.GEMINI_MODEL,
                contents=[types.Part.from_bytes(data=png, mime_type="image/png"), df.OCR_PROMPT],
            )
            df._gem_idx = (idx + 1) % len(df.GEMINI_KEYS)
            return (resp.text or "").strip()
        except Exception as e:  # noqa: BLE001
            last = e
            if df._is_quota(e):
                continue
            raise
    raise df.RateLimited(f"all gemini keys limited: {last}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", type=int, required=True)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    p = SRC / f"弘誓雙月刊-{args.issue:03d}.pdf"
    if not p.exists():
        sys.exit(f"not found: {p}")
    key = f"{PREFIX}/{p.stem}.txt"
    doc = fitz.open(str(p))
    parts = []
    for i, pg in enumerate(doc):
        png = pg.get_pixmap(dpi=args.dpi).tobytes("png")
        for attempt in range(3):
            try:
                txt = gemini_image_ocr(png)
                break
            except df.RateLimited:
                wait = 30 * (attempt + 1)
                print(f"    quota — wait {wait}s (p{i+1})", flush=True)
                time.sleep(wait)
                txt = ""
        parts.append(txt)
        print(f"  p{i+1}/{doc.page_count}: {len(txt)} chars", flush=True)
        time.sleep(1.0)
    doc.close()
    full = "\n\n".join(t for t in parts if t).strip()
    if not full:
        sys.exit("empty OCR result")
    df.r2_put_text(key, full)
    print(f"\n✓ {p.name} → {key}  {len(full)} chars ({doc.page_count} pages)", flush=True)


if __name__ == "__main__":
    main()
