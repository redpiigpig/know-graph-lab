#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR a single scanned PDF → one plain-text file, via Gemini Vision.

Standalone counterpart to scripts/ocr_with_gemini.py (which is DB-driven and
targets ebooks already ingested in Supabase). This one takes a loose PDF on
disk and writes its OCR'd text to a .txt — exactly what
scripts/panikkar_build.py consumes via --src / --zh-src for the collected-works
REFERENCE pipeline (existing 中譯 + 英文原典 逐段對照).

  python scripts/ocr_pdf_to_text.py --pdf <in.pdf> --out <out.txt>
  python scripts/ocr_pdf_to_text.py --pdf <in.pdf> --out sample.txt --pages 5-8   # validate a few pages

Uses the same Gemini Files API + per-page JSON schema as ocr_with_gemini, with
key rotation on quota. Page texts are concatenated in page order with blank
lines so chapter headings land on their own lines (panikkar_build's CJK-heading
split depends on that). Only stats are printed — never the OCR'd content.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))


def pages_to_text(pages: list[dict]) -> str:
    """Join per-page OCR dicts ({page:int, text:str}) into ONE text blob, in page
    order, blank-line separated, dropping empty pages and trimming each page's
    edges (keeps internal \\n\\n so headings/paragraphs survive). Pure — locked by
    tests; the reader/splitter downstream depends on this exact shape."""
    out: list[str] = []
    for p in sorted(pages, key=lambda x: x.get("page", 0)):
        t = (p.get("text") or "").strip()
        if t:
            out.append(t)
    return "\n\n".join(out)


def _gemini_keys() -> list[str]:
    keys, seen = [], set()
    names = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    for n in [""] + [f"_{i}" for i in range(1, 11)]:
        for base in names:
            v = os.environ.get(f"{base}{n}")
            if v:
                for piece in v.split(","):
                    k = piece.strip()
                    if k and k not in seen:
                        seen.add(k)
                        keys.append(k)
                break
    return keys


def _ascii_tmp(suffix: str = ".pdf") -> Path:
    """An ASCII-only temp path. The genai SDK puts the upload filename into an
    HTTP header, which httpx encodes as ascii → a non-ASCII source filename (e.g.
    中文書名) raises UnicodeEncodeError. So we always upload from an ASCII copy."""
    fd, name = tempfile.mkstemp(prefix="ocr_pdf_", suffix=suffix)
    os.close(fd)
    return Path(name)


def _slice_pdf(src: Path, start: int, end: int) -> Path:
    """Copy 1-based inclusive page range [start,end] to an ASCII-named temp PDF
    (for --pages sampling). Requires pymupdf."""
    import fitz
    doc = fitz.open(src)
    out = fitz.open()
    out.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
    tmp = _ascii_tmp()
    out.save(tmp)
    out.close()
    doc.close()
    return tmp


PROMPT = """\
This PDF is a scanned book that may contain Chinese (Traditional or Simplified) and/or English text.

Extract the FULL text from EVERY page. Output ONLY a JSON object: {"pages":[{"page":1,"text":"..."}]}.
- "page" is the 1-based PDF page number within THIS file.
- "text" is the complete extracted text, preserving paragraph breaks with \\n and keeping chapter/section
  headings (导论/第一章/前言…) on their own line.
- Skip purely decorative pages but still include them with empty "text".
- DO NOT translate, summarize, or interpret. Output the original text only. No markdown, no commentary.
"""

PAGES_SCHEMA = {
    "type": "object",
    "properties": {
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"page": {"type": "integer"}, "text": {"type": "string"}},
                "required": ["page", "text"],
            },
        }
    },
    "required": ["pages"],
}


def ocr_pdf(src: Path, *, model: str, pages: tuple[int, int] | None = None) -> list[dict]:
    """OCR one PDF (optionally a page slice) → list of {page,text}. Rotates Gemini
    keys on quota. Network/LLM boundary — not unit-tested."""
    from google import genai
    from google.genai import types

    keys = _gemini_keys()
    if not keys:
        raise RuntimeError("no Gemini keys in .env (Gemini_API_Key_1..)")

    if pages:
        upload_src = _slice_pdf(src, *pages)
    else:
        import shutil
        upload_src = _ascii_tmp()
        shutil.copyfile(src, upload_src)
    try:
        last_err = ""
        for ki, key in enumerate(keys):
            client = genai.Client(api_key=key)
            try:
                up = client.files.upload(
                    file=upload_src,
                    config=types.UploadFileConfig(display_name="ocr.pdf", mime_type="application/pdf"),
                )
                resp = client.models.generate_content(
                    model=model,
                    contents=[up, PROMPT],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json", response_schema=PAGES_SCHEMA,
                    ),
                )
                try:
                    client.files.delete(name=up.name)
                except Exception:
                    pass
                data = json.loads(resp.text)
                return [p for p in data.get("pages", []) if isinstance(p, dict)]
            except Exception as e:  # noqa: BLE001
                last_err = str(e)[:200]
                low = last_err.lower()
                if any(k in low for k in ("quota", "resource_exhausted", "429")) and ki + 1 < len(keys):
                    print(f"  ⟳ key #{ki + 1} quota; rotating", flush=True)
                    time.sleep(2)
                    continue
                raise
        raise RuntimeError(f"all keys exhausted: {last_err}")
    finally:
        try:
            upload_src.unlink()
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", default=None, help="1-based inclusive range, e.g. 5-8 (sample/validate)")
    ap.add_argument("--model", default="gemini-2.5-flash")
    args = ap.parse_args()

    src = Path(args.pdf)
    if not src.exists():
        ap.error(f"not found: {src}")
    pages = None
    if args.pages:
        a, b = args.pages.split("-")
        pages = (int(a), int(b))

    t0 = time.time()
    page_dicts = ocr_pdf(src, model=args.model, pages=pages)
    text = pages_to_text(page_dicts)
    Path(args.out).write_text(text, encoding="utf-8")
    ne = sum(1 for p in page_dicts if (p.get("text") or "").strip())
    print(f"OCR {src.name}  pages={len(page_dicts)} non-empty={ne} chars={len(text)} "
          f"{time.time() - t0:.0f}s → {args.out}", flush=True)


if __name__ == "__main__":
    main()
