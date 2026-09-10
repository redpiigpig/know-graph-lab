# -*- coding: utf-8 -*-
"""胡塞爾《觀念一》Vision OCR 後處理的純函式測試。

樣本取自實跑（gemini-2.5-flash 對 in.ernet.dli.2015.188260 的 pp60–65、pp98–101），
包含真的出現過的兩種毛病：書眉黏在頁碼後面、行末斷詞沒接回。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from husserl_build import (  # noqa: E402
    batches, is_chapter_head, looks_line_broken, paged_units, parse_page,
    split_sections,
)


# ── batches ─────────────────────────────────────────────────────────────────

def test_batches_covers_every_page_once():
    bs = batches(20, 8)
    assert bs == [(1, 8), (9, 16), (17, 20)]
    assert sum(hi - lo + 1 for lo, hi in bs) == 20


def test_batches_exact_multiple():
    assert batches(16, 8) == [(1, 8), (9, 16)]


# ── parse_page ──────────────────────────────────────────────────────────────

def test_parse_page_pulls_folio_and_body():
    folio, units = parse_page("[[p 62]]\nthe function of supplying a logical ground.")
    assert folio == "62"
    assert units == [{"kind": "body", "text": "the function of supplying a logical ground."}]


def test_parse_page_unknown_folio_is_none_not_guessed():
    """🚨 章首頁沒印頁碼就是沒有。假頁碼比沒有更糟——會讓人照著寫進論文。"""
    folio, _units = parse_page("[[p ?]]\n## FIRST CHAPTER")
    assert folio is None


def test_parse_page_separates_notes_and_puts_them_last():
    folio, units = parse_page(
        "[[p 63]]\nbody one\n[note] 1 Cf. Logische Untersuchungen II\nbody two")
    assert [u["kind"] for u in units] == ["body", "body", "note"]
    assert units[-1]["text"] == "1 Cf. Logische Untersuchungen II"


def test_parse_page_joins_soft_hyphen_left_by_ocr():
    """實跑殘留：「I experi- ence it」。真連字號後面不會有空白，所以分得開。"""
    _f, units = parse_page("[[p 61]]\nI discover it immediately, I experi- ence it.")
    assert units[0]["text"] == "I discover it immediately, I experience it."


def test_parse_page_keeps_real_hyphens():
    _f, units = parse_page("[[p 61]]\nof temporo-spatial reality and self-evidence")
    assert units[0]["text"] == "of temporo-spatial reality and self-evidence"


def test_parse_page_strips_stray_folio_markers_mid_page():
    """同一批偶爾把兩頁併成一則，殘留的 [[p N]] 不可以留在正文裡。"""
    _f, units = parse_page("[[p 61]]\nfirst page body\n[[p 62]] second page body")
    assert all("[[p" not in u["text"] for u in units)


def test_parse_page_blank():
    folio, units = parse_page("")
    assert folio is None and units == []


def test_parse_page_drops_empty_note():
    _f, units = parse_page("[[p 1]]\nbody\n[note]   ")
    assert [u["kind"] for u in units] == ["body"]


# ── paged_units ─────────────────────────────────────────────────────────────

def test_paged_units_fills_chapter_opening_folio_backwards():
    """章首頁不印書眉；由下一頁減一推回來。"""
    pages = [{"page": 1, "text": "[[p ?]]\n## FIRST CHAPTER"},
             {"page": 2, "text": "[[p 102]]\nbody"}]
    units = paged_units(pages)
    assert [u["page"] for u in units] == ["101", "102"]


def test_paged_units_carries_folio_to_notes_on_same_page():
    pages = [{"page": 1, "text": "[[p 20]]\nbody\n[note] 1 Cf. Marett"}]
    units = paged_units(pages)
    assert all(u["page"] == "20" for u in units)


def test_paged_units_leaves_unknown_folio_null_when_nothing_to_infer_from():
    units = paged_units([{"page": 1, "text": "[[p ?]]\nfront matter"}])
    assert units[0]["page"] is None


# ── 章節切分 ────────────────────────────────────────────────────────────────

def test_is_chapter_head_accepts_chapter_level_titles():
    assert is_chapter_head("FIRST CHAPTER")
    assert is_chapter_head("SECOND SECTION")
    assert is_chapter_head("INTRODUCTION")
    assert is_chapter_head("Author's Preface")


def test_is_chapter_head_rejects_section_level_titles():
    """🚨 § 是章內小節。拿它當章界會切出兩百多個只有一段的「章」。"""
    assert not is_chapter_head("§ 27. THE WORLD OF THE NATURAL STANDPOINT")
    assert not is_chapter_head("§ 8. INTERDEPENDENCE OF THE SCIENCES")


def test_split_sections_breaks_only_on_chapter_heads():
    units = [
        {"kind": "body", "text": "## FIRST CHAPTER", "page": "101"},
        {"kind": "body", "text": "## § 27. THE WORLD OF THE NATURAL STANDPOINT", "page": "101"},
        {"kind": "body", "text": "Our first outlook upon life", "page": "101"},
        {"kind": "body", "text": "## SECOND CHAPTER", "page": "120"},
        {"kind": "body", "text": "next chapter body", "page": "120"},
    ]
    secs = split_sections(units)
    assert [s["heading"] for s in secs] == ["FIRST CHAPTER", "SECOND CHAPTER"]
    # § 標題留在正文裡當一行，不被吃掉
    assert secs[0]["paras"][0].startswith("## § 27.")
    assert len(secs[0]["paras"]) == 2


def test_split_sections_keeps_pages_aligned_with_paras():
    units = [{"kind": "body", "text": f"para {i}", "page": str(100 + i)} for i in range(4)]
    secs = split_sections(units)
    assert len(secs) == 1
    assert len(secs[0]["paras"]) == len(secs[0]["pages"]) == 4


def test_split_sections_drops_trailing_empty_chapter():
    units = [{"kind": "body", "text": "## INDEX", "page": "460"}]
    assert split_sections(units) == []


# ── 一行一段閘門（真跑出來才發現的第一號坑）────────────────────────────────

def _para(t):
    return {"kind": "body", "text": t}


def test_looks_line_broken_catches_line_per_paragraph():
    """實跑 b0017：中位段長 64、句尾完整率 6%。每一「段」其實是半句話，
    逐句送去翻譯會得到把殘句當完整句翻的胡話。"""
    lines = ["menological reduction, that is, through Epoché. I might have",
             "been better advised if, without altering the essential connexions",
             "of the exposition, I had left open the final decision in favour of",
             "transcendental Idealism, and contented myself with making clear"]
    assert looks_line_broken([_para(t) for t in lines * 6])


def test_looks_line_broken_passes_real_paragraphs():
    """實跑 b0009：中位段長 593。跨頁續段讓句尾完整率只有 50%，不可誤判。"""
    para = ("Our first outlook upon life is that of natural human beings, imaging, judging, "
            "feeling, willing, from the natural standpoint. " * 6)
    units = [_para(para) for _ in range(20)] + [_para("continues onto the next page and")] * 20
    assert not looks_line_broken(units)


def test_looks_line_broken_spares_short_front_matter():
    """🚨 扉頁、目錄、獻詞本來就是短行且句句完整。只看段長會把它們全誤判掉
    （實跑 b0001：中位 64 字，但句尾完整率 81%）。"""
    units = [_para(f"CHAPTER {i}. THE THESIS OF THE NATURAL STANDPOINT.") for i in range(30)]
    assert not looks_line_broken(units)


def test_looks_line_broken_ignores_tiny_batches():
    """樣本太少判不準，一律放行——寧可漏，不可把好的批砍掉重跑燒配額。"""
    assert not looks_line_broken([_para("short") for _ in range(5)])


def test_looks_line_broken_ignores_headings():
    units = [{"kind": "body", "text": "## § 27. THE WORLD"} for _ in range(30)]
    assert not looks_line_broken(units)
