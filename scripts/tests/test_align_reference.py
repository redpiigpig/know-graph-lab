# -*- coding: utf-8 -*-
"""Pure-function tests for scripts/align_reference.py.

跑法：`pytest scripts/tests/test_align_reference.py -q`（或 `npm run test:py`）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import align_reference as ar  # noqa: E402


# ---------------------------------------------------------------------------
# 數字解析
# ---------------------------------------------------------------------------

def test_roman_to_int():
    assert ar.roman_to_int("IV") == 4
    assert ar.roman_to_int("xii") == 12
    assert ar.roman_to_int("MCMXCIX") == 1999
    assert ar.roman_to_int("") is None
    assert ar.roman_to_int("abc") is None


def test_cjk_num_to_int_rejects_ambiguous_concatenation():
    # 「十六十七」是兩個章節編號串接，不是合法的單一中文數字（不該算成 77）
    assert ar.cjk_num_to_int("十六十七") is None
    assert ar.cjk_num_to_int("十一十二十三") is None
    assert ar.cjk_num_to_int("十四十五") is None
    # 但正常的三位數合章（一個十）要照樣算對
    assert ar.cjk_num_to_int("三百六十五") == 365


def test_split_cjk_number_run():
    assert ar.split_cjk_number_run("十六十七") == [16, 17]
    assert ar.split_cjk_number_run("十一十二十三") == [11, 12, 13]
    assert ar.split_cjk_number_run("十四十五") == [14, 15]
    assert ar.split_cjk_number_run("十二") == [12]  # 單一數字不受影響


def test_extract_anchor_cjk_concatenated_lecture_numbers():
    assert ar.extract_anchor_keys("第十六十七講 ”神秘主義") == [
        ("chapter", 16), ("chapter", 17)]
    assert ar.extract_anchor_keys("第十一十二十三講聖徒性") == [
        ("chapter", 11), ("chapter", 12), ("chapter", 13)]


def test_cjk_num_to_int():
    assert ar.cjk_num_to_int("一") == 1
    assert ar.cjk_num_to_int("十二") == 12
    assert ar.cjk_num_to_int("二十一") == 21
    assert ar.cjk_num_to_int("三十") == 30
    assert ar.cjk_num_to_int("100") == 100
    assert ar.cjk_num_to_int("") is None
    assert ar.cjk_num_to_int("abc") is None


# ---------------------------------------------------------------------------
# 章節錨點抽取
# ---------------------------------------------------------------------------

def test_extract_anchor_single_english_chapter():
    assert ar.extract_anchor_keys("Chapter III. On Memory") == [("chapter", 3)]


def test_extract_anchor_single_lecture_multiline():
    # OCR/markdown 常把關鍵字與數字斷在兩行
    assert ar.extract_anchor_keys("### Lecture\nI\n\nReligion and Neurology") == [("chapter", 1)]


def test_extract_anchor_multi_lectures_and():
    assert ar.extract_anchor_keys("Lectures IV and V") == [("chapter", 4), ("chapter", 5)]


def test_extract_anchor_multi_lectures_comma_and():
    assert ar.extract_anchor_keys("Lectures XI, XII and XIII") == [
        ("chapter", 11), ("chapter", 12), ("chapter", 13)]


def test_extract_anchor_cjk_lecture():
    assert ar.extract_anchor_keys("第一講 ”宗教與神經病學") == [("chapter", 1)]
    assert ar.extract_anchor_keys("第二講 論題的範圍 19") == [("chapter", 2)]


def test_extract_anchor_cjk_chapter():
    assert ar.extract_anchor_keys("第三章 神正論的問題") == [("chapter", 3)]
    assert ar.extract_anchor_keys("第十二章") == [("chapter", 12)]


def test_extract_anchor_section_sign():
    assert ar.extract_anchor_keys("§ 12") == [("section", 12)]


def test_extract_anchor_bare_numbered_title_requires_allow_bare():
    # "1. Religion and World-Construction" 這種沒有 Chapter/Section 關鍵字、
    # 單靠「數字＋句點」當標題的寫法，預設不觸發（怕正文列舉句誤判）
    assert ar.extract_anchor_keys("1. Religion and World-Construction") == []
    assert ar.extract_anchor_keys("1. Religion and World-Construction", allow_bare=True) == [
        ("chapter", 1)]
    assert ar.extract_anchor_keys("7. Secularization and the Problem of Legitimation",
                                   allow_bare=True) == [("chapter", 7)]


def test_anchor_keys_for_chunk_prefers_clean_chapter_path_field():
    chunk = {"chapter_path": "3. The Problem of Theodicy",
             "content": "For to exist in a socially..."}
    assert ar.anchor_keys_for_chunk(chunk) == [("chapter", 3)]


def test_extract_anchor_no_match():
    assert ar.extract_anchor_keys("這是普通的一段內文，沒有章節標記。") == []
    assert ar.extract_anchor_keys("") == []


def test_extract_anchor_part_vs_chapter_distinct():
    # Part 1 不該跟 Chapter 1 混在一起
    assert ar.extract_anchor_keys("Part I") == [("part", 1)]
    assert ar.extract_anchor_keys("Book II") == [("book", 2)]


def test_extract_anchor_does_not_fire_on_prose_mention():
    # 正文提到「第三章」以外的詞不該誤觸發（沒有『第N章/節/…』结构就不算）
    assert ar.extract_anchor_keys("chapters of history are long") == []


# ---------------------------------------------------------------------------
# build_blocks：帶著走分組
# ---------------------------------------------------------------------------

def _c(idx, chapter_path="", content=""):
    return {"chunk_index": idx, "chapter_path": chapter_path, "content": content}


def test_build_blocks_basic_transitions():
    chunks = [
        _c(0, "Cover", "cover text"),
        _c(1, "Chapter I", "chapter one body"),
        _c(2, "", "chapter one continues"),
        _c(3, "Chapter II", "chapter two body"),
    ]
    blocks = ar.build_blocks(chunks)
    assert [b["keys"] for b in blocks] == [(), (("chapter", 1),), (("chapter", 2),)]
    assert len(blocks[1]["chunks"]) == 2  # chunk1+chunk2 帶著走併入
    assert len(blocks[2]["chunks"]) == 1


def test_build_blocks_repeated_running_head_stays_one_block():
    # OCR 每頁都印一次同樣的章名書眉，不該被拆成很多個 block
    chunks = [
        _c(0, "", "第一講 宗教與神經病學\n內文1"),
        _c(1, "", "第一講 宗教與神經病學 3\n內文2"),
        _c(2, "", "第一講 宗教與神經病學 5\n內文3"),
        _c(3, "", "第二講 論題的範圍 19\n內文4"),
    ]
    blocks = ar.build_blocks(chunks)
    assert [b["keys"] for b in blocks] == [(("chapter", 1),), (("chapter", 2),)]
    assert len(blocks[0]["chunks"]) == 3
    assert len(blocks[1]["chunks"]) == 1


def test_build_blocks_multi_key_block():
    chunks = [_c(0, "Lectures IV and V", "big combined chapter text")]
    blocks = ar.build_blocks(chunks)
    assert blocks[0]["keys"] == (("chapter", 4), ("chapter", 5))


def test_chapter_zone():
    chunks = [
        _c(0, "Cover", "x"),
        _c(1, "Chapter I", "a"),
        _c(2, "Chapter II", "b"),
        _c(3, "Endnotes", "c"),
    ]
    blocks = ar.build_blocks(chunks)
    lo, hi = ar.chapter_zone(blocks)
    assert blocks[lo]["keys"] == (("chapter", 1),)
    assert blocks[hi]["keys"] == (("chapter", 2),)


def test_chapter_zone_no_chapters():
    blocks = ar.build_blocks([_c(0, "Cover", "x")])
    assert ar.chapter_zone(blocks) == (-1, -1)


# ---------------------------------------------------------------------------
# classify_zone
# ---------------------------------------------------------------------------

def test_classify_zone_variants():
    assert ar.classify_zone("Endnotes") == "notes"
    assert ar.classify_zone("尾註") == "notes"
    assert ar.classify_zone("Bibliography") == "bibliography"
    assert ar.classify_zone("參考書目") == "bibliography"
    assert ar.classify_zone("Index") == "index"
    assert ar.classify_zone("索引") == "index"
    assert ar.classify_zone("譯者序") == "translator_note"
    assert ar.classify_zone("Preface") == "preface"
    assert ar.classify_zone("隨便的章名") is None
    assert ar.classify_zone("") is None


# ---------------------------------------------------------------------------
# 譯者註標記統一
# ---------------------------------------------------------------------------

def test_normalize_translator_notes_prefixes():
    text = "譯者按：這是譯者加的說明。"
    new_text, n = ar.normalize_translator_notes(text)
    assert n == 1
    assert new_text.startswith("〔譯注〕")


def test_normalize_translator_notes_multiple_variants():
    text = "正文。\n译者注：第一條。\n更多正文。\n譯注：第二條。"
    new_text, n = ar.normalize_translator_notes(text)
    assert n == 2
    assert "〔譯注〕第一條" in new_text
    assert "〔譯注〕第二條" in new_text


def test_normalize_translator_notes_does_not_fire_midsentence():
    # 「作者提到譯者」這種正文敘述不該被誤判成譯注起手式
    text = "作者在這裡感謝譯者的辛勞。"
    new_text, n = ar.normalize_translator_notes(text)
    assert n == 0
    assert new_text == text


# ---------------------------------------------------------------------------
# 註腳：抽取與參照標記
# ---------------------------------------------------------------------------

def test_extract_footnote_entries():
    text = "1. First note text here.\n2. Second note, longer text.\n3. Third."
    entries = ar.extract_footnote_entries(text)
    assert entries[1] == "First note text here."
    assert entries[2] == "Second note, longer text."
    assert entries[3] == "Third."


def test_find_footnote_refs_bracket_caret():
    text = "這裡有一個註腳[^3]，這裡還有一個〔7〕。"
    assert ar.find_footnote_refs(text) == {3, 7}


def test_find_footnote_refs_none():
    assert ar.find_footnote_refs("沒有任何註腳標記的一段話。") == set()


# ---------------------------------------------------------------------------
# align_book：端對端合成測試
# ---------------------------------------------------------------------------

def _zh(idx, chapter_path, content):
    return {"chunk_index": idx, "chapter_path": chapter_path, "content": content,
            "chunk_type": "chapter", "page_number": None, "format": "markdown"}


def _en(idx, chapter_path, content):
    return {"chunk_index": idx, "chapter_path": chapter_path, "content": content,
            "chunk_type": "chapter", "page_number": None, "format": "markdown"}


def test_align_book_basic_chapter_matching():
    en = [
        _en(0, "Cover", "Cover page."),
        _en(1, "Preface", "This is the English preface. " * 5),
        _en(2, "Chapter I", ("First chapter paragraph one. " * 8) + "\n\n" +
                              ("First chapter paragraph two. " * 8)),
        _en(3, "Chapter II", "Second chapter English text. " * 10),
    ]
    zh = [
        _zh(0, "封面", "封面"),
        _zh(1, "前言", "這是中文前言。"),
        _zh(2, "第一章", "中文第一章第一段。"),
        _zh(3, "", "中文第一章第二段。"),
        _zh(4, "第二章", "中文第二章內容。"),
    ]
    result = ar.align_book(en, zh)
    report = result["report"]
    assert report["chapter_coverage"] == 1.0
    filled = result["zh_chunks"]
    # chapter I 有兩個既有中文段落，應該都拿到非空的英文對照
    assert filled[2]["source_text"].strip()
    assert filled[3]["source_text"].strip()
    assert filled[4]["source_text"].strip()
    assert filled[0]["chapter_path"] == "封面"


def test_align_book_never_touches_zh_content():
    en = [_en(0, "Chapter I", "English body text here. " * 5)]
    zh = [_zh(0, "第一章", "中文內容一字不改。")]
    result = ar.align_book(en, zh)
    assert result["zh_chunks"][0]["content"] == "中文內容一字不改。"


def test_align_book_gap_chapter_left_blank():
    en = [
        _en(0, "Chapter I", "Chapter one text. " * 5),
        _en(1, "Chapter II", "Chapter two text. " * 5),
    ]
    zh = [
        _zh(0, "第一章", "中文第一章。"),
        # 中譯本沒有第二章對應內容 —— 故意製造缺口
    ]
    result = ar.align_book(en, zh)
    report = result["report"]
    assert report["chapter_coverage"] < 1.0
    assert len(report["gap_chapters"]) == 1
    assert report["gap_chapters"][0][0] == (("chapter", 2),)


def test_align_book_zh_only_front_matter_flagged():
    en = [
        _en(0, "Chapter I", "Chapter one text. " * 5),
    ]
    zh = [
        _zh(0, "譯者序", "這是中譯本獨有的譯者序。"),
        _zh(1, "第一章", "中文第一章。"),
    ]
    result = ar.align_book(en, zh)
    zh_chunks = result["zh_chunks"]
    assert zh_chunks[0].get("zh_only") is True
    assert "（中譯本獨有）" in zh_chunks[0]["chapter_path"]
    assert not zh_chunks[0].get("source_text")
    # 有對應章節的仍正常配對
    assert zh_chunks[1].get("source_text")


def test_align_book_omitted_appendix_reported_not_index():
    en = [
        _en(0, "Chapter I", "Chapter one text. " * 5),
        _en(1, "Appendix I. Extra Material", "Appendix content that translation dropped. " * 5),
        _en(2, "Index", "A\nB\nC"),
    ]
    zh = [
        _zh(0, "第一章", "中文第一章。"),
    ]
    result = ar.align_book(en, zh)
    report = result["report"]
    zones = {o["zone"] for o in report["omitted_in_translation"]}
    assert "appendix" in zones
    assert "index" not in zones  # 索引不計入刪節


def test_align_book_multi_key_english_chapter_splits_across_zh_chapters():
    en = [
        _en(0, "Lectures IV and V",
            ("Lecture four paragraph. " * 10) + "\n\n" + ("Lecture five paragraph. " * 10)),
    ]
    zh = [
        _zh(0, "第四講", "中文第四講。"),
        _zh(1, "第五講", "中文第五講。"),
    ]
    result = ar.align_book(en, zh)
    filled = result["zh_chunks"]
    assert filled[0]["source_text"].strip()
    assert filled[1]["source_text"].strip()
    assert result["report"]["chapter_coverage"] == 1.0


def test_align_book_footnote_numbered_pairing():
    en = [
        _en(0, "Chapter I", "Chapter text. " * 5),
        _en(1, "Endnotes", "1. Note about chapter one.\n2. Another note."),
    ]
    zh = [
        _zh(0, "第一章", "中文第一章內文提到了[^1]這個註腳。"),
        _zh(1, "尾註", "中文尾註區塊，含〔2〕標記。"),
    ]
    result = ar.align_book(en, zh)
    fn = result["report"]["footnotes"]
    assert fn["original_footnotes"] == 2
    assert fn["numbered_pairing"] is True
    assert fn["retained_in_translation"] == 2
    zh_chunks = result["zh_chunks"]
    assert "Note about chapter one" in zh_chunks[0]["source_text"]
    assert "Another note" in zh_chunks[1]["source_text"]


def test_align_book_footnote_no_original_notes_section():
    en = [_en(0, "Chapter I", "Chapter text. " * 5)]
    zh = [_zh(0, "第一章", "中文第一章。")]
    result = ar.align_book(en, zh)
    fn = result["report"]["footnotes"]
    assert fn["original_footnotes"] == 0
    assert fn["numbered_pairing"] is False
