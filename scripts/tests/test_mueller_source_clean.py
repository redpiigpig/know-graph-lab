"""Tests for the Müller source-column OCR cleaner (en/de only; zh untouched)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mueller_source_clean import clean_source, is_junk_para, clean_section


# ── clean_source ─────────────────────────────────────────────────────────────

def test_strips_ocr_junk_symbols():
    assert clean_source("Meaning of Pakayajna *■ XIV") == "Meaning of Pakayajna * XIV"
    assert "•" not in clean_source("Page • Traces •")
    assert "€" not in clean_source("Vedanga € possess")


def test_joins_lowercase_hyphen_wrap():
    assert clean_source("Brahmana- sakhas") == "Brahmanasakhas"
    # capitalised second half is likely a real compound → keep the hyphen
    assert clean_source("Kalpa- Sutras") == "Kalpa- Sutras"


def test_removes_scan_boilerplate():
    out = clean_source("15 EAST 16th STREET Digitized by the Internet Archive "
                       "in 2008 with funding from Microsoft Corporation")
    assert "Digitized" not in out and out.startswith("15 EAST")


def test_removes_archive_url_and_ocr_mangled_boilerplate():
    # bare archive.org URL (no "Digitized by" prefix), keeps real PREFACE text
    out = clean_source("rights reserved} http://www.archive.org/details/"
                       "anthropologicalrOOml PREFACE, In lecturing")
    assert "archive.org" not in out and "PREFACE, In lecturing" in out
    # OCR-mangled: "Arciiive", "littp", "arcliive.org"
    out2 = clean_source("Digitized by tine Internet Arciiive in 2007 witii funding "
                        "from IVIicrosoft Corporation littp://www.arcliive.org/"
                        "details/auldlangsyneOOmluoft AULD LANG SYNE")
    assert "Corporation" not in out2 and "arcliive.org" not in out2
    assert out2.strip().endswith("AULD LANG SYNE")


def test_german_low_quote_preserved_only_in_de():
    assert "„" in clean_source("Er sagte: „Gott ist Liebe", "de")
    assert "„" not in clean_source("„ 45. line Dvaraka.", "en")


def test_clean_prose_unchanged():
    prose = "There is no plot in them to excite our curiosity."
    assert clean_source(prose) == prose


# ── is_junk_para ─────────────────────────────────────────────────────────────

def test_toc_line_is_junk():
    assert is_junk_para("Totemism . . . . . .198 Ancestor-Worship .... 202")
    assert is_junk_para("Absence of Synchronistic Dates . . . . . .11 History . . .12")


def test_bare_page_and_running_head_are_junk():
    assert is_junk_para("xxxiv.")
    assert is_junk_para("ii. 845.")
    assert is_junk_para("CONTENTS.")
    assert is_junk_para("INDEX")


def test_real_prose_survives():
    # ellipsis without a trailing page number must NOT be flagged
    assert not is_junk_para(
        "Adam Gifford, sometime one of the Senators of the College of "
        "Justice, Scotland, . . .")
    assert not is_junk_para(
        "they advanced into Spain and Italy. The Gothic language died out "
        "in the ninth century.")
    assert not is_junk_para(
        "158 COMPARATIVE MYTHOLOGY The rippling wave is like her arching brow")


# ── clean_section (parallel-list integrity) ──────────────────────────────────

def test_section_drops_junk_pair_keeps_alignment():
    cache = {
        "en": ["Totemism . . . . . .198 Worship .... 202",  # junk → drop
               "Real prose about the Veda.",
               "Another •clean• paragraph."],
        "zh": ["圖騰制……（目錄）", "關於吠陀的真正散文。", "另一段乾淨段落。"],
        "fail": [0, 0, 0],
    }
    out, cleaned, dropped, _ = clean_section(cache)
    assert dropped == 1
    assert out["en"] == ["Real prose about the Veda.", "Another clean paragraph."]
    assert out["zh"] == ["關於吠陀的真正散文。", "另一段乾淨段落。"]
    assert len(out["en"]) == len(out["zh"]) == len(out["fail"])
    assert cleaned == 1  # the •…• paragraph was symbol-cleaned


def test_section_never_edits_chinese():
    cache = {"en": ["a •b•"], "zh": ["中文原樣不動"], "fail": [0]}
    out, _, _, _ = clean_section(cache)
    assert out["zh"] == ["中文原樣不動"]
