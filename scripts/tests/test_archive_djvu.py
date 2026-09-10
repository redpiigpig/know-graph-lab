# -*- coding: utf-8 -*-
"""archive.org djvu.xml 解析層的純函式測試。

真實座標取自奧托《The Idea of the Holy》兩種掃描本（1923 in.ernet.dli.2015.262513、
1924 in.ernet.dli.2015.22259），兩刷的版面習慣不同，所以每個判準都要兩刷都過。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from archive_djvu import (  # noqa: E402
    fill_folios, folio_int, folio_of, is_indented, is_junk, normalize,
    page_units, reflow, repair_folios, split_notes, strip_head,
)


def L(text, top, h=65, x0=300, bottom=None):
    return {"text": text, "top": top, "bottom": bottom if bottom is not None else top + h,
            "h": h, "x0": x0, "x1": x0 + 2000}


# ── folio_of ────────────────────────────────────────────────────────────────

def test_folio_own_line_verso():
    """1924 刷：頁碼自成一行，左上角。"""
    page = [L("20", 226, x0=257), L("MYSTERIUM TREMENDUM", 221, x0=856),
            L("2. The element of Overpoweringness", 392), L("We have been attempting", 519)]
    assert folio_of(page) == "20"


def test_folio_own_line_recto():
    page = [L("MYSTERIUM TREMENDUM", 213, x0=864), L("21", 215, x0=2578),
            L("in his sections upon Creation", 377)]
    assert folio_of(page) == "21"


def test_folio_trailing_token():
    """1923 刷：頁碼黏在書眉字串尾端。"""
    page = [L("THE ELEMENTS IN THE 'nUMINOUs' 9", 196),
            L("Schleiermacher has the credit", 322)]
    assert folio_of(page) == "9"


def test_folio_leading_token():
    page = [L("24 ' MYSTERIUM TREMENDUM '", 196), L("union of majesty", 331)]
    assert folio_of(page) == "24"


def test_folio_roman_only_as_its_own_line():
    """羅馬頁碼只在整行就是頁碼時才認。黏在書眉字串裡的羅馬數字多半是章號
    （「Chapter III」），認了會讓整章頁碼變成 iii。"""
    assert folio_of([L("xii", 200), L("PREFACE", 210), L("body", 400)]) == "xii"
    assert folio_of([L("Chapter III", 200), L("body", 400)]) is None


def test_folio_ignores_numbered_subhead_in_body():
    """🚨 正文第一行的編號小標不是頁碼。奧托每章都有「2. The element of…」，
    誤認會讓整章頁碼變成 1,2,3——看起來完全正常的假頁碼。"""
    page = [L("MYSTERIUM TREMENDUM", 221, x0=856),
            L("2. The element of Overpoweringness", 392), L("We have been", 519)]
    assert folio_of(page) is None


def test_folio_none_on_chapter_opening():
    """章首頁照排版慣例不印書眉。"""
    page = [L("Chapter III", 425, x0=1399), L("THE ELEMENTS IN THE NUMINOUS", 575),
            L("Creature-Feeling", 738), L("The reader is invited", 848)]
    assert folio_of(page) is None


def test_folio_empty_page():
    assert folio_of([]) is None


# ── folio_int / fill_folios ─────────────────────────────────────────────────

def test_folio_int_arabic_and_roman():
    assert folio_int("21") == 21
    assert folio_int("xii") is None      # 羅馬頁碼不進整數欄
    assert folio_int(None) is None


def test_fill_folios_forward():
    assert fill_folios(["8", None, None, "11"]) == ["8", "9", "10", "11"]


def test_fill_folios_backward_for_chapter_opening():
    """該節第一頁多半就是章首頁，只能由下一頁減一。"""
    assert fill_folios([None, "9", "10"]) == ["8", "9", "10"]


def test_fill_folios_never_goes_below_one():
    assert fill_folios([None, "1", "2"]) == [None, "1", "2"]


def test_fill_folios_does_not_do_roman_arithmetic():
    assert fill_folios(["xii", None]) == ["xii", None]


def test_fill_folios_all_none_stays_none():
    assert fill_folios([None, None]) == [None, None]


# ── split_notes ─────────────────────────────────────────────────────────────

def _body_run(n, start=400, step=100, h=76, x0=230):
    return [L(f"body line {i}", start + i * step, h=h, x0=x0) for i in range(n)]


def test_split_notes_finds_trailing_footnote_block():
    lines = _body_run(8) + [L("1 Cf. R. R. Marett, 'The Birth of Humility'", 1330, h=62, x0=308),
                            L("2nd ed., 1914. [Tr.]", 1424, h=62, x0=226)]
    body, notes = split_notes(lines)
    assert len(notes) == 2 and notes[0]["text"].startswith("1 Cf.")
    assert len(body) == 8


def test_split_notes_needs_a_marker():
    """行距大、字也小，但開頭不是註腳記號 → 那是正文，不是註腳。"""
    lines = _body_run(8) + [L("and so the argument closes here", 1330, h=62, x0=308)]
    body, notes = split_notes(lines)
    assert notes == [] and len(body) == 9


def test_split_notes_needs_a_gap():
    """行距一如往常、只是開頭剛好是數字（『2. The element of…』那種編號小標）
    → 不是註腳。"""
    lines = _body_run(8) + [L("2. The element of Overpoweringness", 1200, h=62, x0=308)]
    body, notes = split_notes(lines)
    assert notes == []


def test_split_notes_needs_small_type():
    lines = _body_run(8) + [L("1 This is set in body type", 1330, h=90, x0=308)]
    body, notes = split_notes(lines)
    assert notes == []


def test_split_notes_ignores_top_of_page():
    """頁面上半部不找註腳。"""
    lines = [L("1 not a footnote", 200, h=50)] + _body_run(8)
    body, notes = split_notes(lines)
    assert notes == []


def test_split_notes_short_page_returns_all_body():
    lines = _body_run(2)
    body, notes = split_notes(lines)
    assert notes == [] and len(body) == 2


# ── reflow ──────────────────────────────────────────────────────────────────

def test_is_indented_uses_local_baseline():
    """🚨 掃描歪斜：左緣一路右漂，但沒有任何一行是新段落。拿全頁最小 x0 當基準
    會把後半頁每一行都判成新段落。"""
    # 實測奧托 1924 那刷：一頁三十多行，左緣一路漂約四十個單位（每行一兩個）。
    lines = [L("a", 100, x0=469), L("b", 200, x0=467), L("c", 300, x0=464),
             L("d", 400, x0=462), L("e", 500, x0=459), L("f", 600, x0=457)]
    assert not any(is_indented(lines, i) for i in range(len(lines)))


def test_is_indented_catches_real_indent():
    lines = [L("a", 100, x0=383), L("b", 200, x0=381), L("c", 300, x0=469),
             L("d", 400, x0=385), L("e", 500, x0=384)]
    assert is_indented(lines, 2)


def test_reflow_joins_hyphenated_line_break():
    lines = [L("this important discovery of de-", 100, x0=300),
             L("pendence is open to criticism", 200, x0=300)]
    assert reflow(lines) == ["this important discovery of dependence is open to criticism"]


def test_reflow_splits_on_indent():
    lines = [L("first paragraph runs on", 100, x0=300),
             L("and finishes here.", 200, x0=300),
             L("Second paragraph starts.", 300, x0=390),
             L("and runs on.", 400, x0=300)]
    out = reflow(lines)
    assert len(out) == 2 and out[1].startswith("Second paragraph")


def test_normalize_collapses_ocr_double_spaces():
    assert normalize("We  have  been  attempting ,  and") == "We have been attempting, and"


def test_reflow_drops_empty():
    assert reflow([L("   ", 100)]) == []


# ── page_units ──────────────────────────────────────────────────────────────

def test_page_units_tags_notes_and_carries_folio():
    lines = _body_run(8) + [L("1 Cf. Marett, The Threshold of Religion", 1330, h=62, x0=308)]
    units = page_units(lines, "20")
    assert [u["kind"] for u in units][-1] == "note"
    assert all(u["page"] == "20" for u in units)


def test_page_units_note_block_is_not_split_by_indent():
    """註腳每一條的首行本來就縮排，不可以再拿縮排去切段——那會把一條註腳
    切成好幾段，段落數一亂，中英對照就錯位。"""
    notes = [L("1 Cf. Marett", 1330, h=62, x0=308), L("2nd ed., 1914.", 1424, h=62, x0=226)]
    units = page_units(_body_run(8) + notes, "20")
    assert sum(1 for u in units if u["kind"] == "note") == 1


# ── strip_head / is_junk / repair_folios（真檔跑出來才發現的四個坑）─────────

def test_strip_head_removes_running_head_from_body():
    """🚨 撈完頁碼不代表事情結束——書眉還在 lines 裡，不拿掉會黏在該頁第一段
    最前面（「MYSTERIUM TREMENDUM 20 2. The element of…」）。"""
    page = [L("20", 226, x0=257), L("MYSTERIUM TREMENDUM", 221, x0=856),
            L("We have been attempting", 392), L("to unfold the implications", 490)]
    body = strip_head(page)
    assert [ln["text"] for ln in body] == ["We have been attempting", "to unfold the implications"]


def test_strip_head_keeps_page_with_no_body():
    page = [L("20", 226), L("MYSTERIUM TREMENDUM", 221)]
    assert strip_head(page) == page


def test_is_junk_catches_scan_noise():
    assert is_junk("$r b I £ £")
    assert is_junk("— - — -")
    assert is_junk("x")
    assert not is_junk("We have been attempting to unfold the implications")
    assert not is_junk("1 Cf. R. R. Marett, The Threshold of Religion, 2nd ed., 1914.")


def test_repair_folios_drops_ocr_misreads():
    """實測 258 頁裡有 20 處跳號，最誇張的把某頁讀成「1」。錯頁碼比沒頁碼糟。"""
    assert repair_folios(["18", "19", "1", "21", "22"]) == ["18", "19", None, "21", "22"]


def test_repair_folios_keeps_a_clean_run():
    assert repair_folios(["18", "19", "20", "21"]) == ["18", "19", "20", "21"]


def test_repair_folios_tolerates_gaps_from_unnumbered_pages():
    """章首頁沒印頁碼，中間空一格是正常的，不可以把兩邊也打掉。"""
    assert repair_folios(["18", None, "20", "21"]) == ["18", None, "20", "21"]


def test_reflow_hyphen_beats_indent():
    """續行的 x0 因掃描歪斜偶爾會超過縮排門檻；上一行以連字號收尾時不可切段。"""
    lines = [L("Here we must revert to his expres-", 100, x0=300),
             L("sion for what we call creature-feeling", 200, x0=400)]
    assert reflow(lines) == ["Here we must revert to his expression for what we call creature-feeling"]


def test_is_indented_rejects_mid_line_ocr_fragment():
    """🚨 OCR 把同一條印刷行拆成兩筆時，後半截 x0 右移五百以上。那不是段落縮排。
    沒有上界的話，每個碎片都變成一個新段落，中英兩欄立刻錯位。"""
    lines = [L("God's character as all-causi-", 100, x0=287),
             L("conditioning. But a sense of this", 105, x0=896),
             L("into that immediate emotion", 200, x0=288)]
    assert not is_indented(lines, 1)


def test_is_indented_still_accepts_a_real_em_indent():
    lines = [L("a", 100, x0=383), L("New paragraph here.", 200, x0=469), L("c", 300, x0=385)]
    assert is_indented(lines, 1)


def test_reflow_merges_fragment_on_the_same_printed_line():
    """兩筆的 top 幾乎相同＝同一條印刷行被拆開，一律接續，不看縮排。"""
    lines = [L("first line of the paragraph", 100, x0=287),
             L("continued on the same line", 104, x0=1500),
             L("second line of the paragraph", 200, x0=288)]
    assert len(reflow(lines)) == 1
