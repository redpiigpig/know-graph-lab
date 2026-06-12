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

# Heading-marking variant: makes chapter/section titles into Markdown `## ` lines
# so panikkar_build's split_sections detects them consistently in BOTH the English
# original and the Chinese translation → chapters pair up for 逐段對照. Used by the
# collected-works REFERENCE pipeline (--mark-headings).
PROMPT_MARK_HEADINGS = """\
This PDF is a book that may contain Chinese (Traditional or Simplified) and/or English text.

Extract the FULL text from EVERY page. Output ONLY a JSON object: {"pages":[{"page":1,"text":"..."}]}.
- "page" is the 1-based PDF page number within THIS file.
- "text" is the complete extracted text, preserving paragraph breaks with \\n.
- IMPORTANT: put every chapter or major section TITLE on its own line, prefixed with "## "
  (e.g. "## The Dialogical Dialogue", "## 第一章 對話的修辭", "## Introduction", "## 导论").
  Mark ONLY genuine chapter/section titles this way — NOT running heads, page numbers, or footnotes.
- Skip purely decorative pages but still include them with empty "text".
- DO NOT translate, summarize, or interpret. Output the original text only. No commentary.
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


_MAX_OUTPUT_TOKENS = 32768  # whole-book single calls truncate at the 8K default → lost pages


def _pdf_page_count(src: Path) -> int:
    import fitz
    doc = fitz.open(src)
    n = len(doc)
    doc.close()
    return n


def _ocr_one_call(src_slice: Path, *, model: str, prompt: str, keys: list[str]) -> list[dict]:
    """OCR a single (ASCII-named) PDF in one Gemini call, rotating keys on quota.
    Salvages truncated JSON via json_repair when available."""
    from google import genai
    from google.genai import types
    try:
        import json_repair
    except Exception:
        json_repair = None
    last_err = ""
    ki = 0
    transient_tries = 0
    while ki < len(keys):
        client = genai.Client(api_key=keys[ki])
        try:
            up = client.files.upload(
                file=src_slice,
                config=types.UploadFileConfig(display_name="ocr.pdf", mime_type="application/pdf"),
            )
            resp = client.models.generate_content(
                model=model,
                contents=[up, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=PAGES_SCHEMA,
                    max_output_tokens=_MAX_OUTPUT_TOKENS,
                ),
            )
            try:
                client.files.delete(name=up.name)
            except Exception:
                pass
            try:
                data = json.loads(resp.text)
            except json.JSONDecodeError:
                if json_repair:
                    data = json_repair.loads(resp.text)
                    if not isinstance(data, dict):
                        data = {"pages": []}
                else:
                    raise
            return [p for p in data.get("pages", []) if isinstance(p, dict)]
        except Exception as e:  # noqa: BLE001
            last_err = str(e)[:200]
            low = last_err.lower()
            if any(k in low for k in ("quota", "resource_exhausted", "429")):
                ki += 1  # daily/RPM cap on this key — move to the next key
                if ki < len(keys):
                    print(f"  ⟳ key #{ki} quota; rotating", flush=True)
                    time.sleep(2)
                continue
            if any(k in low for k in ("503", "unavailable", "500", "internal",
                                      "overloaded", "deadline", "timeout", "connection")):
                # transient Gemini spike — back off + retry SAME key (up to 6×)
                transient_tries += 1
                if transient_tries <= 6:
                    wait = min(10 * transient_tries, 60)
                    print(f"  ↻ transient ({last_err[:60]}); retry in {wait}s", flush=True)
                    time.sleep(wait)
                    continue
                ki += 1  # give up on this key, try next
                transient_tries = 0
                continue
            raise
    raise RuntimeError(f"all keys exhausted: {last_err}")


def ocr_pdf(src: Path, *, model: str, pages: tuple[int, int] | None = None,
            mark_headings: bool = False, batch: int = 0) -> list[dict]:
    """OCR a PDF → list of {page,text} (global 1-based page numbers). Rotates
    Gemini keys on quota. When batch>0 and the range exceeds it, OCRs in page
    batches (whole-book single calls truncate past the output-token limit) and
    renumbers pages globally. Network/LLM boundary — not unit-tested."""
    keys = _gemini_keys()
    if not keys:
        raise RuntimeError("no Gemini keys in .env (Gemini_API_Key_1..)")
    prompt = PROMPT_MARK_HEADINGS if mark_headings else PROMPT

    total = _pdf_page_count(src)
    lo, hi = (pages[0], pages[1]) if pages else (1, total)
    lo, hi = max(1, lo), min(total, hi)

    if batch and (hi - lo + 1) > batch:
        ranges = [(s, min(s + batch - 1, hi)) for s in range(lo, hi + 1, batch)]
    else:
        ranges = [(lo, hi)]

    out: list[dict] = []
    for bi, (rs, re_) in enumerate(ranges, 1):
        sl = _slice_pdf(src, rs, re_)
        try:
            page_dicts = _ocr_one_call(sl, model=model, prompt=prompt, keys=keys)
        finally:
            try:
                sl.unlink()
            except OSError:
                pass
        for p in page_dicts:  # slice-local page (1..k) → global (rs..)
            p["page"] = rs + (int(p.get("page", 1)) - 1)
        out.extend(page_dicts)
        if len(ranges) > 1:
            ne = sum(1 for p in page_dicts if (p.get("text") or "").strip())
            print(f"  batch {bi}/{len(ranges)} pp{rs}-{re_}: {ne} pages", flush=True)
    return out


def extract_text_layer(src: Path, *, pages: tuple[int, int] | None = None) -> list[dict]:
    """Pull the EMBEDDED text layer (no OCR) from a born-digital PDF → list of
    {page,text}. For text-layer PDFs (e.g. the English Intrareligious Dialogue),
    this is faster, free, and cleaner than Gemini OCR. Use --engine gemini only
    for scanned books with no text layer."""
    from pypdf import PdfReader
    r = PdfReader(str(src))
    n = len(r.pages)
    lo, hi = (pages[0] - 1, pages[1]) if pages else (0, n)
    out: list[dict] = []
    for i in range(max(0, lo), min(n, hi)):
        out.append({"page": i + 1, "text": (r.pages[i].extract_text() or "")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", default=None, help="1-based inclusive range, e.g. 5-8 (sample/validate)")
    ap.add_argument("--engine", default="gemini", choices=["gemini", "text"],
                    help="gemini = OCR scanned PDF; text = pull embedded text layer (born-digital)")
    ap.add_argument("--mark-headings", action="store_true",
                    help="mark chapter/section titles as Markdown ## (for collected-works alignment)")
    ap.add_argument("--batch", type=int, default=20,
                    help="pages per Gemini call (0 = whole file; >0 avoids output-token truncation)")
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
    if args.engine == "text":
        page_dicts = extract_text_layer(src, pages=pages)
    else:
        page_dicts = ocr_pdf(src, model=args.model, pages=pages,
                             mark_headings=args.mark_headings, batch=args.batch)
    text = pages_to_text(page_dicts)
    Path(args.out).write_text(text, encoding="utf-8")
    ne = sum(1 for p in page_dicts if (p.get("text") or "").strip())
    print(f"OCR {src.name}  pages={len(page_dicts)} non-empty={ne} chars={len(text)} "
          f"{time.time() - t0:.0f}s → {args.out}", flush=True)


if __name__ == "__main__":
    main()
