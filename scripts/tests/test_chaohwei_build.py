# -*- coding: utf-8 -*-
"""《心靈的交會》build 的純函式（零 I/O）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chaohwei_build import (  # noqa: E402
    audit_pages,
    build_chunks,
    is_apparatus_page,
    is_note,
    mark_speaker,
    normalize_page_text,
    page_sort_key,
    split_body_and_notes,
    split_chapters,
    stitch_pages,
    normalize_printed,
    strip_page_header,
    tag_chapters,
    to_fullwidth_punct,
)

CHS = [
    {"title": "彼得‧辛格　自序", "start": "a", "end": "d"},
    {"title": "在這交會時互放的光芒（釋昭慧　自序）", "start": "i", "end": "iii"},
    {"title": "對話三：婦女與平等", "start": "59", "end": "78"},
]


def _pages(*specs):
    """(work_page, printed, [paras]) → pages dict list。"""
    return [{"work_page": w, "printed": p, "paras": list(ps)} for w, p, ps in specs]


class TestFullwidthPunct:
    def test_comma_after_cjk_becomes_fullwidth(self):
        assert to_fullwidth_punct("同時,我對佛教也有疑問") == "同時，我對佛教也有疑問"

    def test_all_five_marks(self):
        assert to_fullwidth_punct("甲,乙;丙:丁?戊!") == "甲，乙；丙：丁？戊！"

    def test_latin_context_untouched(self):
        # 書裡的英文引文與數字不能被動到
        assert to_fullwidth_punct("Singer, Peter") == "Singer, Peter"
        assert to_fullwidth_punct("共 1,000 人") == "共 1,000 人"

    def test_space_between_cjk_and_punct_absorbed(self):
        assert to_fullwidth_punct("同時 ,我") == "同時，我"

    def test_empty(self):
        assert to_fullwidth_punct("") == ""


class TestNormalizePageText:
    def test_blank_marker_becomes_empty(self):
        assert normalize_page_text("（無正文）") == ""

    def test_long_dash_run_collapses(self):
        assert normalize_page_text("筆譯————包括後續") == "筆譯——包括後續"

    def test_two_dashes_kept(self):
        assert normalize_page_text("筆譯——包括") == "筆譯——包括"


class TestStripPageHeader:
    def test_book_title_header_removed(self):
        t = "ii 心靈交會山間對話\n方思考更加成熟的契機。"
        assert strip_page_header(t, "ii") == "方思考更加成熟的契機。"

    def test_chapter_header_removed(self):
        t = "對話二：佛法的核心概念：業與涅槃\n辛格：現在談到「業」的概念。"
        assert strip_page_header(t, "23") == "辛格：現在談到「業」的概念。"

    def test_stray_edge_character_removed(self):
        assert strip_page_header("i\n必須與他們易地而處。", "12") == "必須與他們易地而處。"

    def test_chapter_title_page_is_never_stripped(self):
        # 章名頁沒有印刷頁碼 → 整頁原樣保留，那是真標題不是頁眉
        t = "對話二\nDialogue 2\n佛法的核心概念"
        assert strip_page_header(t, "") == t

    def test_body_first_line_kept(self):
        t = "辛格：佛教倫理學到了哪個程度開始成為效益主義？"
        assert strip_page_header(t, "1") == t

    def test_stops_at_first_non_header_line(self):
        t = "心靈交會山間對話\n正文第一段。\n心靈交會山間對話"
        assert strip_page_header(t, "8").endswith("心靈交會山間對話")

    def test_header_glued_to_body_only_loses_the_header(self):
        # 🚨 OCR 把頁眉和正文吐成同一行；沒有長度上限的版本會把整頁 454 字刪光
        t = "對話六：動物福利辛格：在探討終結生命的不同觀點之後，讓我們進入下一個主題。"
        out = strip_page_header(t, "151")
        assert out.startswith("辛格：在探討終結生命")

    def test_a_long_line_is_never_deleted_wholesale(self):
        t = "對話六：動物福利" + "正文" * 40
        assert len(strip_page_header(t, "151")) > 40


class TestNotes:
    def test_note_line_is_pulled_out_of_the_body(self):
        t = ("依此而合理化自己對「他者」的傷害[^4]，因此有必要劃一道界限\n"
             "[^4]: 中央通訊社報導：〈00後性別比例失衡〉，2018/09/05")
        body, notes = split_body_and_notes(t)
        assert "[^4]:" not in body
        assert notes == ["[^4]: 中央通訊社報導：〈00後性別比例失衡〉，2018/09/05"]

    def test_note_continuation_line_joins_the_same_note(self):
        t = "[^4]: 中央通訊社報導：\n〈00後性別比例失衡〉，2018/09/05"
        _, notes = split_body_and_notes(t)
        assert notes == ["[^4]: 中央通訊社報導：〈00後性別比例失衡〉，2018/09/05"]

    def test_page_without_notes(self):
        body, notes = split_body_and_notes("辛格：這一頁沒有註。")
        assert body == "辛格：這一頁沒有註。"
        assert notes == []

    def test_is_note(self):
        assert is_note("[^4]: 註文") is True
        assert is_note("正文[^4]提到") is False

    def test_notes_come_after_the_body_and_keep_the_page_anchor(self):
        pages = tag_chapters(_pages(
            (1, "59", ["辛格：正文[^4]。", "[^4]: 註文全文"]),
        ), CHS)
        units = stitch_pages(pages)
        assert [u[0] for u in units] == ["59", "59"]
        assert is_note(units[1][1])

    def test_body_after_a_note_never_joins_onto_it(self):
        pages = tag_chapters(_pages(
            (1, "59", ["[^4]: 註文沒有句號結尾"]), (2, "60", ["下一頁的正文。"]),
        ), CHS)
        assert len(stitch_pages(pages)) == 2


class TestMarkSpeaker:
    def test_fullwidth_colon(self):
        assert mark_speaker("辛格：剛才那頓飯真是美味") == "〔辛格〕剛才那頓飯真是美味"

    def test_halfwidth_colon(self):
        assert mark_speaker("昭慧: 沒錯。") == "〔昭慧〕沒錯。"

    def test_already_marked_is_idempotent(self):
        assert mark_speaker("〔昭慧〕沒錯。") == "〔昭慧〕沒錯。"

    def test_non_speech_untouched(self):
        p = "佛教不相信神或神聖的造物主。"
        assert mark_speaker(p) == p

    def test_speaker_name_inside_sentence_untouched(self):
        p = "我耳聞辛格：這句話並非開頭"
        assert mark_speaker(p) == p


class TestApparatusPage:
    def test_chapter_title_page_dropped(self):
        assert is_apparatus_page("對話二\nDialogue 2\n佛法的核心概念", "") is True

    def test_chapter_title_page_dropped_even_with_a_misread_page_number(self):
        # 模型把「Dialogue.4」讀成頁碼 75 → 沒有這一條就會變成「頁 75 重複」
        assert is_apparatus_page("對話四:\nDialogue.4\n情欲\nSexuality,", "75") is True

    def test_contents_page_dropped(self):
        assert is_apparatus_page("目次CONTENTS\n對話一：倫理學的基礎理論……1-22", "") is True

    def test_half_title_page_dropped(self):
        assert is_apparatus_page("心靈的交會——山間對話\nMeeting of Minds", "") is True

    def test_body_page_kept(self):
        assert is_apparatus_page("辛格：現在談到「業」的概念。", "23") is False

    def test_body_mentioning_dialogue_is_not_apparatus(self):
        assert is_apparatus_page("昭慧：這場 Dialogue 對話很難得。", "60") is False


class TestStitchPages:
    def test_unfinished_paragraph_joins_next_page(self):
        pages = tag_chapters(_pages(
            (1, "59", ["辛格：剛才那頓飯真是美味，同時我也很高興"]),
            (2, "60", ["看到我們的享受並非建築在動物的死亡上。"]),
        ), CHS)
        units = stitch_pages(pages)
        assert len(units) == 1
        assert units[0][0] == "59"  # anchor 取段落**起始**那一頁
        assert units[0][1].endswith("動物的死亡上。")

    def test_sentence_end_starts_new_paragraph(self):
        pages = tag_chapters(_pages(
            (1, "59", ["沒錯。"]), (2, "60", ["我相當欣賞這個做法。"]),
        ), CHS)
        assert [a for a, _, _ in stitch_pages(pages)] == ["59", "60"]

    def test_new_speaker_never_joins(self):
        pages = tag_chapters(_pages(
            (1, "59", ["……這個地方真美"]), (2, "60", ["昭慧：沒錯。"]),
        ), CHS)
        assert len(stitch_pages(pages)) == 2

    def test_never_joins_across_a_chapter_boundary(self):
        # 章末殘句不可以把下一章的第一段吃進來
        pages = tag_chapters(_pages(
            (1, "d", ["序的最後一句沒有句號"]), (2, "59", ["對話三的第一段。"]),
        ), CHS)
        units = stitch_pages(pages)
        assert len(units) == 2
        assert units[1][2] == 2

    def test_only_first_para_of_a_page_can_join(self):
        pages = tag_chapters(_pages(
            (1, "59", ["未完的句子"]), (2, "60", ["接上去的話", "另一段沒句號"]),
        ), CHS)
        units = stitch_pages(pages)
        assert len(units) == 2
        assert units[1][0] == "60"


class TestNormalizePrinted:
    def test_uppercase_front_matter_letter_lowered(self):
        assert normalize_printed("C") == "c"

    def test_roman_lowered(self):
        assert normalize_printed("II") == "ii"

    def test_digits_untouched(self):
        assert normalize_printed("151") == "151"

    def test_blank(self):
        assert normalize_printed("  ") == ""


class TestPageSortKey:
    def test_arabic_numeric_order(self):
        assert page_sort_key("9") < page_sort_key("10")

    def test_roman(self):
        assert page_sort_key("iv") < page_sort_key("ix")

    def test_unknown_sorts_last(self):
        assert page_sort_key("") == (9, 0)


class TestAuditPages:
    def test_duplicate_keeps_the_cleaner_scan_not_the_longer_text(self):
        # 被黑邊吃掉的那一份 OCR 反而更長（多吐亂碼）→ 只比字數會選錯
        recs = [
            {"work_page": 72, "printed": "56", "text": "髒" * 60, "quality": 14},
            {"work_page": 74, "printed": "56", "text": "乾淨" * 25, "quality": 19},
        ]
        rep = audit_pages(recs)
        assert rep["duplicates"] == [{"printed": "56", "keep": 74, "drop": [72]}]
        assert rep["keep"] == [74]

    def test_falls_back_to_length_without_quality(self):
        recs = [
            {"work_page": 3, "printed": "59", "text": "短"},
            {"work_page": 9, "printed": "59", "text": "比較長的正文"},
        ]
        assert audit_pages(recs)["duplicates"][0]["keep"] == 9

    def test_real_gap_is_reported(self):
        recs = [
            {"work_page": 1, "printed": "1", "text": "a"},
            {"work_page": 2, "printed": "4", "text": "b"},
        ]
        rep = audit_pages(recs)
        assert rep["missing"] == [2, 3]
        assert rep["blank_gaps"] == []

    def test_blank_page_between_chapters_is_not_a_missing_page(self):
        recs = [
            {"work_page": 1, "printed": "21", "text": "正文"},
            {"work_page": 2, "printed": "22", "text": "（無正文）"},
            {"work_page": 3, "printed": "23", "text": "下一章"},
        ]
        rep = audit_pages(recs)
        assert rep["blank_gaps"] == [22]
        assert rep["missing"] == []

    def test_apparatus_page_never_counts_as_a_duplicate(self):
        recs = [
            {"work_page": 95, "printed": "75", "text": "正文正文"},
            {"work_page": 99, "printed": "75", "text": "對話四:\nDialogue.4\n情欲"},
        ]
        rep = audit_pages(recs)
        assert rep["duplicates"] == []
        assert rep["apparatus"] == [99]
        assert rep["keep"] == [95, 99]

    def test_no_numeric_pages_gives_no_range(self):
        recs = [{"work_page": 1, "printed": "a", "text": "x"}]
        assert audit_pages(recs)["printed_range"] is None


class TestTagChapters:
    def test_front_matter_letters_do_not_get_read_as_roman_numerals(self):
        # 'c' 與 'd' 也是羅馬數字 100／500；把頁碼轉成數字比大小就會判錯章
        pages = tag_chapters(_pages(
            (3, "a", ["辛格序一"]), (5, "c", ["辛格序三"]), (6, "d", ["辛格序四"]),
            (7, "i", ["昭慧序一"]), (9, "iii", ["昭慧序三"]),
        ), CHS)
        assert [p["chapter"] for p in pages] == [0, 0, 0, 1, 1]

    def test_pages_before_the_first_chapter_are_front_matter(self):
        pages = tag_chapters(_pages((1, "", ["扉頁"]), (3, "a", ["序"])), CHS)
        assert [p["chapter"] for p in pages] == [-1, 0]

    def test_pages_after_the_last_chapter_are_back_matter(self):
        pages = tag_chapters(_pages(
            (1, "59", ["正文"]), (2, "78", ["章末"]), (3, "", ["法界出版社出版圖書目錄"]),
        ), CHS)
        assert [p["chapter"] for p in pages] == [2, 2, 3]

    def test_missing_start_page_falls_forward(self):
        # 頁 59 的頁碼被 OCR 讀錯 → 用 60 當切點，整章才不會併進前一章
        pages = tag_chapters(_pages((1, "a", ["序"]), (2, "60", ["對話三的正文"])), CHS)
        assert [p["chapter"] for p in pages] == [0, 2]

    def test_start_points_must_advance(self):
        # 正文裡若又出現一個 '59'，不能倒回去重開一次對話三
        pages = tag_chapters(_pages(
            (1, "59", ["章首"]), (2, "60", ["續"]), (3, "59", ["OCR 讀錯的頁"]),
        ), CHS)
        assert [p["chapter"] for p in pages] == [2, 2, 2]


class TestSplitChapters:
    def test_paragraphs_land_in_their_chapter(self):
        pages = tag_chapters(_pages(
            (3, "a", ["辛格：序。"]), (10, "59", ["辛格：您好。"]), (11, "60", ["昭慧：沒錯。"]),
        ), CHS)
        chs = split_chapters(stitch_pages(pages), CHS)
        assert [c["title"] for c in chs] == ["彼得‧辛格　自序", "對話三：婦女與平等"]
        assert chs[1]["paras"][0] == "## 對話三：婦女與平等"
        assert chs[1]["paras"][1] == "〔辛格〕您好。"

    def test_front_and_back_matter_get_no_heading_row(self):
        pages = tag_chapters(_pages((1, "", ["扉頁一句。"]), (3, "a", ["序。"])), CHS)
        chs = split_chapters(stitch_pages(pages), CHS)
        assert chs[0]["title"] == "卷首"
        assert chs[0]["paras"][0] == "扉頁一句。"


class TestBuildChunks:
    def _chunks(self):
        pages = tag_chapters(_pages(
            (10, "59", ["辛格：您好。"]), (11, "60", ["昭慧：沒錯。"]),
        ), CHS)
        return build_chunks(split_chapters(stitch_pages(pages), CHS))

    def test_cover_first(self):
        assert self._chunks()[0]["chunk_type"] == "cover"

    def test_page_number_is_the_printed_page_not_the_index(self):
        c = self._chunks()[1]
        assert c["chunk_index"] == 1
        assert c["page_number"] == 59  # 不是 chunk_index+1

    def test_anchors_align_with_paragraphs(self):
        c = self._chunks()[1]
        paras = c["content"].split("\n\n")
        assert len(c["anchors"]) == len(paras)
        assert c["anchors"] == ["", "59", "60"]  # 標題那一列不掛頁碼

    def test_page_number_none_for_a_chapter_with_no_arabic_page(self):
        pages = tag_chapters(_pages((3, "a", ["辛格：序。"])), CHS)
        chunks = build_chunks(split_chapters(stitch_pages(pages), CHS))
        assert chunks[1]["page_number"] is None
        assert chunks[1]["anchors"] == ["", "a"]
