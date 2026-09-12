# -*- coding: utf-8 -*-
"""《心靈的交會》build 的純函式（零 I/O）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chaohwei_build import (  # noqa: E402
    audit_pages,
    drop_repeated_header,
    fill_one_page_gaps,
    strip_inline_markers,
    unescape_linebreaks,
    build_chunks,
    is_apparatus_page,
    is_note,
    is_note_continuation,
    mark_speaker,
    merge_units,
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

    def test_is_note_continuation(self):
        assert is_note_continuation("[^續]: 接下去的註文") is True
        assert is_note_continuation("[^4]: 一般註文") is False

    def test_notes_come_after_the_body_and_keep_the_page_anchor(self):
        pages = tag_chapters(_pages(
            (1, "59", ["辛格：正文[^4]。", "[^4]: 註文全文"]),
        ), CHS)
        units = stitch_pages(pages)
        assert [u[0] for u in units] == ["59", "59"]
        assert is_note(units[1][1])

    def test_continuation_note_rejoins_the_note_it_came_from(self):
        pages = tag_chapters(_pages(
            (1, "59", ["[^14]: 《攝大乘論》卷上：「如是緣起，於大乘中極細甚深。復有十"]),
            (2, "60", ["[^續]: 二支緣起，是名分別愛非愛緣起。」（大正三一‧一三四下）"]),
        ), CHS)
        units = stitch_pages(pages)
        assert len(units) == 1
        assert units[0][0] == "59"  # anchor 留在註開始的那一頁
        assert units[0][1].startswith("[^14]:")
        assert units[0][1].endswith("（大正三一‧一三四下）")

    def test_orphan_continuation_does_not_invent_a_note_number(self):
        pages = tag_chapters(_pages((1, "59", ["[^續]: 找不到前一條註"])), CHS)
        units = stitch_pages(pages)
        assert units[0][1] == "找不到前一條註"

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

    def test_title_page_without_a_dialogue_number_is_dropped(self):
        # 「對談尾聲」那一頁沒有 Dialogue N 可認，只能靠章名表
        assert is_apparatus_page("對談尾聲的總結與回顧\nA Concluding Reflection", "",
                                 ["對談尾聲的總結與回顧"])

    def test_a_titled_page_that_carries_a_folio_is_body(self):
        # 同一個標題出現在章的第一頁（有頁碼、後面接正文）→ 那是正文
        assert not is_apparatus_page("對談尾聲的總結與回顧\n昭慧:在本書告竣的此時", "217",
                                     ["對談尾聲的總結與回顧"])

    def test_titles_are_optional(self):
        assert not is_apparatus_page("對談尾聲的總結與回顧", "")

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

    def test_parens_completed_only_by_stitching_still_get_normalized(self):
        # 左括號在前一頁、右括號在後一頁 —— 逐頁那一關看到的都是半邊，配不成對
        units = [("161", "內容(如《攝大乘論》所謂：世間雜染、出世清淨等不成之論)也", 2)]
        out = split_chapters(units, CHS)
        assert "（如《攝大乘論》" in out[0]["paras"][1]
        assert "(" not in out[0]["paras"][1]

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

class TestMergeUnits:
    """序言整篇一塊、對話一次發言一塊（使用者 2026-09-11 定調）。"""

    def test_one_block_per_speaker_turn(self):
        units = [
            ("59", "辛格：第一段問題。", 2),
            ("59", "接著同一個人繼續講。", 2),
            ("60", "昭慧：換我回答。", 2),
        ]
        out = merge_units(units)
        assert len(out) == 2
        assert out[0][1].startswith("〔辛格〕")
        assert "接著同一個人繼續講" in out[0][1]
        assert out[1][1].startswith("〔昭慧〕")

    def test_speaker_marked_before_merging(self):
        # 🚨 順序反了就抓不到換人：mark_speaker 若留到之後才做，
        # merge 看到的還是「昭慧：」，整章會被併成一整塊
        units = [("1", "辛格：甲。", 2), ("1", "昭慧：乙。", 2)]
        assert len(merge_units(units)) == 2

    def test_preface_becomes_one_block(self):
        units = [("a", "序的第一段。", 0), ("a", "第二段。", 0), ("b", "第三段。", 0)]
        out = merge_units(units)
        assert len(out) == 1
        assert out[0][0] == "a"

    def test_page_change_leaves_an_inline_marker(self):
        # 合併之後仍要引得出「第幾頁」
        units = [("a", "序的第一段。", 0), ("b", "第二頁開始的一段。", 0)]
        out = merge_units(units)
        assert "【頁 b】" in out[0][1]

    def test_same_page_gets_no_marker(self):
        units = [("a", "第一段。", 0), ("a", "同一頁的第二段。", 0)]
        assert "【頁" not in merge_units(units)[0][1]

    def test_heading_stays_its_own_block(self):
        units = [("", "## 對話三：婦女與平等", 2), ("59", "辛格：您好。", 2)]
        out = merge_units(units)
        assert len(out) == 2
        assert out[0][1].startswith("##")

    def test_never_merges_across_chapters(self):
        units = [("d", "序的結尾。", 0), ("1", "對話一的開頭。", 2)]
        assert len(merge_units(units)) == 2


class TestFullwidthParens:
    def test_chinese_content_gets_fullwidth_parens(self):
        assert to_fullwidth_punct("(一)識緣名色") == "（一）識緣名色"

    def test_latin_content_keeps_halfwidth_parens(self):
        # 書裡的西文夾注照排版慣例留半形
        assert to_fullwidth_punct("效益主義(Bentham)的") == "效益主義(Bentham)的"
        assert to_fullwidth_punct("彌勒(Maitreya)") == "彌勒(Maitreya)"

    def test_year_and_number_keep_halfwidth(self):
        assert to_fullwidth_punct("法界出版社(2021)") == "法界出版社(2021)"

    def test_citation_with_chinese_converts(self):
        assert (to_fullwidth_punct("依此(大正二九・一五九上)可知")
                == "依此（大正二九・一五九上）可知")

    def test_pair_spanning_one_linebreak(self):
        # 括號被版面切到下一行，兩邊都要換
        assert (to_fullwidth_punct("引文(《雜\n阿含經》卷十)如是")
                == "引文（《雜\n阿含經》卷十）如是")

    def test_never_pairs_across_a_footnote_boundary(self):
        # 這個 `)` 屬於別處；跨過註號硬配對會換錯一半
        src = "見(大正四三・一下\n[^21]: 某註)"
        assert to_fullwidth_punct(src) == src

    def test_unmatched_paren_left_alone(self):
        assert to_fullwidth_punct("唯識(未閉合") == "唯識(未閉合"

    def test_line_initial_enumeration_converts(self):
        assert to_fullwidth_punct("(1)「種子與種姓」方面") == "（1）「種子與種姓」方面"

    def test_mid_line_latin_numbering_untouched(self):
        # SN.35.93/(10) 這種西文引註不是列舉號
        assert to_fullwidth_punct("SN.35.93/(10).也是") == "SN.35.93/(10).也是"


class TestUnescapeLinebreaks:
    def test_page_written_entirely_with_escaped_newlines(self):
        # 這兩頁的 OCR 存成字面的反斜線 n，一個真換行都沒有
        src = "\\n【眉 對話一】\\n話，回收廠根本沒地方可以蓋"
        assert unescape_linebreaks(src) == "\n【眉 對話一】\n話，回收廠根本沒地方可以蓋"

    def test_page_with_real_newlines_is_left_alone(self):
        # 已經有真換行 → 裡面的反斜線 n 是內容，不是壞掉的換行
        src = "第一行\n提到 \\n 這個跳脫序列"
        assert unescape_linebreaks(src) == src

    def test_plain_text_untouched(self):
        assert unescape_linebreaks("辛格：一般正文") == "辛格：一般正文"

    def test_empty(self):
        assert unescape_linebreaks("") == ""


class TestDropRepeatedHeader:
    def test_first_line_equal_to_the_running_head_goes(self):
        assert (drop_repeated_header("對話八：死刑與戰爭中的殺戮\n〔辛格〕前面的對話中",
                                     "對話八：死刑與戰爭中的殺戮")
                == "〔辛格〕前面的對話中")

    def test_punctuation_and_spacing_differences_still_match(self):
        # header 欄是 `對話一:…` 半形冒號，正文那行是全形
        assert (drop_repeated_header("對話一：倫理學的基礎理論\n辛格：佛教倫理學",
                                     "對話一:倫理學的基礎理論")
                == "辛格：佛教倫理學")

    def test_body_that_merely_starts_with_the_head_is_kept(self):
        # 只是開頭幾個字像，不是整行 —— 那是正文
        src = "對話八：死刑與戰爭中的殺戮是本章的主題，我們先從美國談起"
        assert drop_repeated_header(src, "對話八：死刑與戰爭中的殺戮") == src

    def test_no_header_is_a_no_op(self):
        assert drop_repeated_header("正文第一行\n第二行", "") == "正文第一行\n第二行"

    def test_only_the_first_line_is_considered(self):
        src = "正文第一行\n對話八：死刑與戰爭中的殺戮"
        assert drop_repeated_header(src, "對話八：死刑與戰爭中的殺戮") == src

    def test_empty_body(self):
        assert drop_repeated_header("", "對話八") == ""


class TestStripInlineMarkers:
    def test_page_marker_recovers_the_folio(self):
        body, folio = strip_inline_markers("【頁 91}\n【眉 參考資料}\n害。據此判斷", "")
        assert folio == "91"
        assert body == "害。據此判斷"

    def test_existing_printed_wins(self):
        body, folio = strip_inline_markers("【頁 91}\n正文", "95")
        assert folio == "95"

    def test_fullwidth_bracket_variant(self):
        body, folio = strip_inline_markers("【眉 對話一:倫理學的基礎理論】\n話,回收廠", "11")
        assert body == "話,回收廠"
        assert folio == "11"

    def test_no_marker_is_untouched(self):
        assert strip_inline_markers("一般正文", "7") == ("一般正文", "7")

    def test_page_mark_inserted_by_merge_units_is_not_a_header(self):
        # merge_units 自己插的 `【頁 N】` 行內標記不能被這一步吃掉
        body, folio = strip_inline_markers("前段\n\n【頁 12】後段", "11")
        assert "【頁 12】" in body


class TestFillOnePageGaps:
    def test_single_gap_between_known_neighbours_is_filled(self):
        assert fill_one_page_gaps(["13", "", "15"]) == ["13", "14", "15"]

    def test_two_missing_in_a_row_is_left_alone(self):
        # 推不出唯一解就不推 —— 假頁碼比沒有更糟
        assert fill_one_page_gaps(["13", "", "", "16"]) == ["13", "", "", "16"]

    def test_real_gap_is_not_papered_over(self):
        assert fill_one_page_gaps(["47", "49"]) == ["47", "49"]

    def test_misread_folio_between_consistent_neighbours_is_corrected(self):
        # OCR 把 97 讀成 17，前後兩頁都說它該是 97
        assert fill_one_page_gaps(["96", "17", "98"]) == ["96", "97", "98"]

    def test_a_folio_that_agrees_with_neighbours_is_never_touched(self):
        assert fill_one_page_gaps(["96", "97", "98"]) == ["96", "97", "98"]

    def test_non_numeric_folios_are_left_alone(self):
        assert fill_one_page_gaps(["a", "", "c"]) == ["a", "", "c"]

    def test_edges_are_never_extrapolated(self):
        assert fill_one_page_gaps(["", "2", "3", ""]) == ["", "2", "3", ""]
