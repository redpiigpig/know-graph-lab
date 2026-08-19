"""Probe Claude Haiku Vision for ACCS OCR without touching checkpoint or DB."""

from __future__ import annotations

import argparse
import json

import fitz

from ingest_accs_genesis import ocr_batch_claude, render_page


def parse_pages(spec: str) -> list[int]:
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(part))
    return pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--pages", required=True)
    ap.add_argument("--model", default="haiku", choices=["haiku", "sonnet"])
    args = ap.parse_args()

    pdf = fitz.open(args.pdf)
    for page in parse_pages(args.pages):
        print(f"== page {page} model={args.model} ==", flush=True)
        png = render_page(pdf, page - 1)
        entries = ocr_batch_claude([png], model=args.model)
        print(json.dumps(entries, ensure_ascii=False, indent=2), flush=True)
    pdf.close()


if __name__ == "__main__":
    main()
