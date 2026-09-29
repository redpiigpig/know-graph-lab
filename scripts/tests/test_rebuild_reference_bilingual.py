import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rebuild_reference_bilingual as r  # noqa: E402


def test_strip_page_furniture_drops_running_header_and_folio():
    lines = ["6 ; The Taiwanese Religious Context", "of the past two millennia, orthodox", "body text.", "16"]
    out = r.strip_page_furniture(lines, {"The Taiwanese Religious Context"})
    assert out == ["of the past two millennia, orthodox", "body text."]


def test_strip_page_furniture_keeps_body_line():
    lines = ["In the infamous Kaohsiung incident the KMT government crushed"]
    assert r.strip_page_furniture(lines, {"Tzu Chi"}) == lines


def test_pages_to_blocks_dehyphenates_and_detects_heading():
    text = "\n".join([
        "TZU CHI AND DEMOCRACY",
        "A tightly knit organization with a religious ideology led by a charis-",
        "matic leader does not seem promising for an emerging democracy.",
        "Short end.",
        "Next paragraph starts here and runs on for a whole long line of text",
        "and ends.",
    ])
    blocks = r.pages_to_blocks([(45, 17, text)], set())
    assert blocks[0] == ("h", "Tzu Chi and Democracy")
    assert "charismatic" in blocks[1][1] and blocks[1][1].startswith("{{p:17}}")
    assert blocks[2][1].startswith("Next paragraph")


def test_html_single_column_table_becomes_paragraphs():
    t = "<table><tr><td>書名</td></tr><tr><td>ISBN 978</td></tr></table>"
    assert r.html_tables_to_md(t) == "書名\n\nISBN 978"


def test_fold_empty_moves_page_marker_forward_and_drops_noise():
    assert r.fold_empty(["{{p:54}}", "### 節", "正文", "|"]) == ["### 節", "{{p:54}}正文"]


def test_insert_headings_needs_paragraph_start():
    body = "前文提到研究程序很重要。\n\n研究程序表面上，這些實踐"
    out, missing = r.insert_headings(body, ["研究程序"])
    assert not missing
    assert "\n\n### 研究程序\n\n表面上" in out
    assert out.startswith("前文提到研究程序很重要。")


def test_align_merges_when_translator_joins_paragraphs():
    en = ["a" * 300, "b" * 300, "c" * 300]
    zh = ["甲" * 150, "乙" * 300]          # 譯者把後兩段併成一段（中英字數比約 1:2）
    rows = r.align(zh, en)
    assert [(len(z), len(e)) for z, e in rows] == [(1, 1), (1, 2)]


def test_build_part_numbers_by_original_paragraphs():
    zh = "## 第一章\n\n### 節一\n\n" + "\n\n".join(["甲" * 100, "乙" * 200])
    en = [("h", "Section One"), ("p", "a" * 200), ("p", "b" * 200), ("p", "c" * 200)]
    zc, ec, warns = r.build_part("1", zh, en, "Chapter 1")
    assert not warns
    assert "{{s:1-1-1}}" in zc and "{{s:1-1-2–3}}" in zc
    assert r.paras(zc).__len__() == r.paras(ec).__len__()
