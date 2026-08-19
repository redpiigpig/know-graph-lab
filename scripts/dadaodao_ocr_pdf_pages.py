#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumable page OCR for the three large scanned Dadaodao PDFs.

Each successful page is immediately checkpointed to R2 under
``dadaodao-fulltext-pages/<relative PDF path>.pNNNN.txt``.  The normal
``dadaodao-fulltext/<relative PDF path>.txt`` object is created only after
every page exists, so downstream consumers never see a partial book.

Examples (run only after acquiring/confirming a free model lane):
  python -X utf8 scripts/dadaodao_ocr_pdf_pages.py --engine gemini --max-new-pages 10
  python -X utf8 scripts/dadaodao_ocr_pdf_pages.py --engine sonnet --book 浩蕩赴前程
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402


PAGE_PREFIX = "dadaodao-fulltext-pages"
PDF_NAMES = (
    "釋昭慧，人間佛教試煉場.pdf",
    "釋昭慧，浩蕩赴前程.pdf",
    "釋昭慧，獨留情義落江湖.pdf",
)


def object_text(key: str) -> str:
    obj = df.s3.get_object(Bucket=df.R2_BUCKET, Key=key)
    return obj["Body"].read().decode("utf-8")


def page_key(rel: str, page_no: int) -> str:
    return f"{PAGE_PREFIX}/{rel}.p{page_no:04d}.txt"


def ocr_png(png: bytes, engine: str, pace: float) -> tuple[str, str]:
    fd, name = tempfile.mkstemp(suffix=".png")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(png)
        return df.ocr_file(Path(name), "image/png", pace=pace, engine=engine)
    finally:
        Path(name).unlink(missing_ok=True)


def find_books(selector: str) -> list[Path]:
    wanted = [n for n in PDF_NAMES if not selector or selector in n]
    found = []
    for name in wanted:
        matches = list(df.SRC_ROOT.rglob(name))
        if len(matches) != 1:
            raise RuntimeError(f"expected one source for {name!r}, found {len(matches)}")
        found.append(matches[0])
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default="", help="filename substring; blank selects all three books")
    ap.add_argument("--engine", choices=("gemini", "sonnet", "auto"))
    ap.add_argument("--gemini-lane", type=int, default=0,
                    help="1-based Gemini key matching an acquired gemini-N lane")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--pace", type=float, default=2.0)
    ap.add_argument("--max-new-pages", type=int, default=0,
                    help="safe batch cap across selected books; 0 means no cap")
    ap.add_argument("--status", action="store_true", help="report checkpoints only; make no OCR calls")
    args = ap.parse_args()
    if not args.status and not args.engine:
        ap.error("--engine is required unless --status is used")
    if args.gemini_lane:
        if args.engine != "gemini":
            ap.error("--gemini-lane requires --engine gemini")
        if not 1 <= args.gemini_lane <= len(df.GEMINI_KEYS):
            ap.error(f"--gemini-lane must be 1..{len(df.GEMINI_KEYS)}")
        df.GEMINI_KEY_INDEX = args.gemini_lane - 1

    existing_pages = df.r2_existing_keys(PAGE_PREFIX)
    existing_full = df.r2_existing_keys(df.TEXT_PREFIX)
    new_pages = failures = completed_books = 0

    if args.status:
        for pdf in find_books(args.book):
            rel = str(pdf.relative_to(df.SRC_ROOT)).replace("\\", "/")
            doc = fitz.open(str(pdf))
            total = doc.page_count
            doc.close()
            have = sum(page_key(rel, i) in existing_pages for i in range(1, total + 1))
            complete = f"{df.TEXT_PREFIX}/{rel}.txt" in existing_full
            print(f"{rel}: pages {have}/{total}, fulltext={complete}")
        return

    for pdf in find_books(args.book):
        rel = str(pdf.relative_to(df.SRC_ROOT)).replace("\\", "/")
        final_key = f"{df.TEXT_PREFIX}/{rel}.txt"
        if final_key in existing_full:
            print(f"  ↷ complete: {rel}", flush=True)
            continue

        doc = fitz.open(str(pdf))
        total = doc.page_count
        print(f"\n{rel} — {total} pages", flush=True)
        for idx in range(total):
            key = page_key(rel, idx + 1)
            if key in existing_pages:
                continue
            if args.max_new_pages and new_pages >= args.max_new_pages:
                doc.close()
                print(f"\nBATCH LIMIT — new pages {new_pages}, failures {failures}", flush=True)
                return
            try:
                png = doc[idx].get_pixmap(dpi=args.dpi, alpha=False).tobytes("png")
                text, used = ocr_png(png, args.engine, args.pace)
                if not text.strip():
                    raise RuntimeError("empty OCR result")
                df.r2_put_text(key, text.strip())
                existing_pages.add(key)
                new_pages += 1
                print(f"  ✓ p{idx + 1}/{total} [{used}] {len(text)} chars", flush=True)
            except (df.RateLimited, df.BothLimited) as exc:
                doc.close()
                print(f"  ⏸ quota at p{idx + 1}: {exc}", flush=True)
                print(f"\nSTOP — checkpointed new pages {new_pages}, failures {failures}", flush=True)
                return
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"  ✗ p{idx + 1}/{total}: {type(exc).__name__}: {str(exc)[:180]}", flush=True)
                doc.close()
                print("STOP — fix/retry failed page before continuing to keep the book complete", flush=True)
                return
        doc.close()

        keys = [page_key(rel, i) for i in range(1, total + 1)]
        if all(k in existing_pages for k in keys):
            full = "\n\n".join(object_text(k).strip() for k in keys).strip()
            if not full:
                raise RuntimeError(f"empty assembled OCR: {rel}")
            df.r2_put_text(final_key, full)
            existing_full.add(final_key)
            completed_books += 1
            print(f"  ✓ assembled → {final_key} ({len(full)} chars)", flush=True)
        time.sleep(args.pace)

    print(f"\nDONE — new pages {new_pages}, completed books {completed_books}, failures {failures}", flush=True)


if __name__ == "__main__":
    main()
