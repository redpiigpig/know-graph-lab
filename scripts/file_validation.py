#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-ingest file integrity gate.

Inspired by raul23/organize-ebooks: validate that an ebook file actually
opens before it enters the pipeline, so corrupt / zero-filled / truncated
downloads get quarantined instead of silently producing empty chunks (the
current "49 OCR-rescue candidates" problem — files whose body extraction
failed because the PDF was broken, not because it was scanned).

The check is intentionally cheap and offline:
  - .pdf  → open with PyMuPDF (fitz); needs ≥1 page; reject password-locked
  - .epub → must be a valid zip containing mimetype + META-INF/container.xml
  - .mobi/.azw3/.azw → magic-byte sniff (can't fully parse, but catch garbage)
  - any   → reject zero-byte and absurdly tiny files

`validate_ebook()` does the IO; the per-format deciders are split out so the
logic is unit-testable against real temp files (no network/DB).

Return contract: `Verdict(ok: bool, reason: str, detail: str)`.
  ok=True            → safe to ingest
  ok=False           → quarantine; `reason` is a stable machine code
`reason` codes: "ok", "missing", "zero_byte", "too_small",
  "pdf_unreadable", "pdf_no_pages", "pdf_encrypted",
  "epub_not_zip", "epub_no_mimetype", "epub_bad_mimetype",
  "mobi_bad_magic", "unknown_ext".
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

# Catch zero-filled / truncated downloads and saved HTML error pages. Kept low
# on purpose — the real integrity signal is the per-format parser below, so this
# is only a fast pre-filter for near-empty files, not a page-count heuristic.
MIN_PLAUSIBLE_BYTES = 200

EBOOK_EXTS = {".pdf", ".epub", ".mobi", ".azw3", ".azw"}

# MOBI / Kindle container magic. PDB header has the type/creator at offset 60.
_MOBI_MAGICS = (b"BOOKMOBI", b"TPZ3", b"TPZ0")


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reason: str
    detail: str = ""

    def __bool__(self) -> bool:  # allow `if validate_ebook(p):`
        return self.ok


# ── per-format pure-ish deciders (operate on a path that already exists) ──

def _validate_pdf(path: Path) -> Verdict:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        # No parser available — fall back to a header sniff so we still catch
        # obviously-broken files without claiming false confidence.
        head = path.read_bytes()[:5]
        if head[:4] != b"%PDF":
            return Verdict(False, "pdf_unreadable", "no %PDF header (fitz unavailable)")
        return Verdict(True, "ok", "header-only check (fitz unavailable)")
    try:
        doc = fitz.open(str(path))
    except Exception as e:  # corrupt / truncated / not really a pdf
        return Verdict(False, "pdf_unreadable", f"{type(e).__name__}: {e}")
    try:
        if doc.needs_pass:
            return Verdict(False, "pdf_encrypted", "password-protected")
        if doc.page_count < 1:
            return Verdict(False, "pdf_no_pages", "0 pages")
    finally:
        doc.close()
    return Verdict(True, "ok")


def _validate_epub(path: Path) -> Verdict:
    if not zipfile.is_zipfile(path):
        return Verdict(False, "epub_not_zip", "not a zip container")
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            if "mimetype" not in names:
                # Some EPUBs omit the (optional-by-spec) mimetype entry but are
                # still valid; require container.xml as the real signal.
                if "META-INF/container.xml" not in names:
                    return Verdict(False, "epub_no_mimetype",
                                   "no mimetype and no META-INF/container.xml")
                return Verdict(True, "ok", "no mimetype entry but container.xml present")
            mt = zf.read("mimetype").strip()
            if mt != b"application/epub+zip":
                return Verdict(False, "epub_bad_mimetype", mt.decode("latin-1", "replace")[:40])
            if "META-INF/container.xml" not in names:
                return Verdict(False, "epub_no_mimetype", "missing META-INF/container.xml")
    except zipfile.BadZipFile as e:
        return Verdict(False, "epub_not_zip", str(e))
    return Verdict(True, "ok")


def _validate_mobi(path: Path) -> Verdict:
    head = path.read_bytes()[:80]
    # New-style: magic somewhere in the first record header.
    if any(m in head for m in _MOBI_MAGICS):
        return Verdict(True, "ok")
    # Old PDB: bytes 60..68 carry the type+creator (e.g. b"BOOKMOBI").
    if len(head) >= 68 and head[60:68] in (b"BOOKMOBI", b"TEXtREAd"):
        return Verdict(True, "ok")
    return Verdict(False, "mobi_bad_magic", head[:16].hex())


# ── public entry ─────────────────────────────────────────────────────────

def validate_ebook(path) -> Verdict:
    """Validate one ebook file on disk. Pure of network/DB; touches only `path`."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return Verdict(False, "missing", str(p))
    size = p.stat().st_size
    if size == 0:
        return Verdict(False, "zero_byte")
    if size < MIN_PLAUSIBLE_BYTES:
        return Verdict(False, "too_small", f"{size} bytes")

    ext = p.suffix.lower()
    if ext == ".pdf":
        return _validate_pdf(p)
    if ext == ".epub":
        return _validate_epub(p)
    if ext in (".mobi", ".azw3", ".azw"):
        return _validate_mobi(p)
    return Verdict(False, "unknown_ext", ext)


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("usage: python scripts/file_validation.py <file> [<file> ...]")
        raise SystemExit(2)
    bad = 0
    for arg in sys.argv[1:]:
        v = validate_ebook(arg)
        mark = "OK  " if v.ok else "BAD "
        if not v.ok:
            bad += 1
        print(f"{mark} [{v.reason}] {arg}" + (f"  ({v.detail})" if v.detail else ""))
    raise SystemExit(1 if bad else 0)
