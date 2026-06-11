"""Pre-ingest integrity gate (file_validation.validate_ebook).

Locks the quarantine contract: zero-byte / truncated / non-zip-epub /
garbage-mobi files are rejected with a stable `reason` code, while a
minimally-valid container passes. Real temp files, no network/DB.
"""
import zipfile

import pytest

import file_validation as fv


# ── generic size / existence gates ────────────────────────────────────────

def test_missing_file(tmp_path):
    v = fv.validate_ebook(tmp_path / "nope.pdf")
    assert not v.ok and v.reason == "missing"
    assert not bool(v)  # __bool__ falls through to .ok


def test_zero_byte(tmp_path):
    p = tmp_path / "empty.pdf"
    p.write_bytes(b"")
    v = fv.validate_ebook(p)
    assert not v.ok and v.reason == "zero_byte"


def test_too_small(tmp_path):
    p = tmp_path / "stub.epub"
    p.write_bytes(b"a few bytes")
    assert fv.validate_ebook(p).reason == "too_small"


def test_unknown_extension(tmp_path):
    p = tmp_path / "thing.txt"
    p.write_bytes(b"x" * 2048)
    assert fv.validate_ebook(p).reason == "unknown_ext"


# ── EPUB ──────────────────────────────────────────────────────────────────

def _make_epub(path, *, mimetype=b"application/epub+zip", with_container=True):
    with zipfile.ZipFile(path, "w") as zf:
        if mimetype is not None:
            zf.writestr("mimetype", mimetype)
        if with_container:
            zf.writestr("META-INF/container.xml", "<container/>")
        zf.writestr("OEBPS/ch1.xhtml", "<html><body>hi</body></html>")


def test_valid_epub(tmp_path):
    p = tmp_path / "good.epub"
    _make_epub(p)
    v = fv.validate_ebook(p)
    assert v.ok and v.reason == "ok"


def test_epub_not_zip(tmp_path):
    p = tmp_path / "fake.epub"
    p.write_bytes(b"PK-but-not-really" + b"\x00" * 2048)
    assert fv.validate_ebook(p).reason == "epub_not_zip"


def test_epub_bad_mimetype(tmp_path):
    p = tmp_path / "wrong.epub"
    _make_epub(p, mimetype=b"application/zip")
    assert fv.validate_ebook(p).reason == "epub_bad_mimetype"


def test_epub_missing_container(tmp_path):
    p = tmp_path / "nocontainer.epub"
    _make_epub(p, with_container=False)
    assert fv.validate_ebook(p).reason == "epub_no_mimetype"


def test_epub_no_mimetype_but_container_ok(tmp_path):
    # mimetype entry is omitted but container.xml is present → still valid.
    p = tmp_path / "loose.epub"
    _make_epub(p, mimetype=None, with_container=True)
    assert fv.validate_ebook(p).ok


# ── MOBI / AZW ────────────────────────────────────────────────────────────

def test_valid_mobi_magic(tmp_path):
    p = tmp_path / "book.mobi"
    # PDB header: 60 bytes of name/attrs then type+creator "BOOKMOBI".
    p.write_bytes(b"\x00" * 60 + b"BOOKMOBI" + b"\x00" * 2048)
    assert fv.validate_ebook(p).ok


def test_garbage_mobi(tmp_path):
    p = tmp_path / "junk.azw3"
    p.write_bytes(b"\xff" * 2048)
    assert fv.validate_ebook(p).reason == "mobi_bad_magic"


# ── PDF (skipped cleanly if PyMuPDF isn't installed) ──────────────────────

fitz = pytest.importorskip("fitz", reason="PyMuPDF not installed")


def test_valid_pdf(tmp_path):
    p = tmp_path / "good.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(p))
    doc.close()
    assert fv.validate_ebook(p).ok


def test_corrupt_pdf(tmp_path):
    p = tmp_path / "broken.pdf"
    # Has a %PDF header so it passes the size gate but fitz can't parse it.
    p.write_bytes(b"%PDF-1.4\n" + b"\x00garbage\xff" * 256)
    v = fv.validate_ebook(p)
    assert not v.ok and v.reason in ("pdf_unreadable", "pdf_no_pages")
