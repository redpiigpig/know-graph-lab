# -*- coding: utf-8 -*-
"""Test-first 契約：scripts/mukyokai_translate.py 的純函式。

無教會 collection 收的日文研究（赤江達也、呉敬姫…）是 J-STAGE 那批 2000 年代的
掃描本，文字層是舊 OCR：同一個視覺行被拆成好幾個片段、固定的一組誤字、頁碼與
書眉的字級比正文小。這幾支就是處理這些的，全部不碰網路／PDF／LLM。

模組本身的 docstring 早就指著這個檔，但它一直不存在——2026-09-10 補上。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mukyokai_translate as mt  # noqa: E402


def _page(*lines):
    """(y, x0, size, text) → PyMuPDF get_text("dict") 的最小可用形狀。"""
    return {"blocks": [{"lines": [
        {"bbox": [x0, y, x0 + 100, y + 10],
         "spans": [{"text": t, "size": size}]}
        for y, x0, size, t in lines]}]}


# ── 版面幾何 ──────────────────────────────────────────────────────────────────
def test_fragments_on_the_same_visual_line_are_rejoined():
    """舊 OCR 一遇括號就斷片；不併回去，一段會被切成幾十段。"""
    out = mt.visual_lines(_page((100.0, 60.0, 8.0, "内村鑑三は"),
                                (100.5, 200.0, 8.0, "(1861-1930)"),
                                (100.2, 300.0, 8.0, "である。")))
    assert out == [(60.0, "内村鑑三は(1861-1930)である。")]


def test_lines_far_apart_are_not_merged():
    out = mt.visual_lines(_page((100.0, 60.0, 8.0, "第一行"),
                                (120.0, 60.0, 8.0, "第二行")))
    assert [t for _x0, t in out] == ["第一行", "第二行"]


def test_headers_below_size_threshold_are_dropped():
    """書眉 6.0 濾掉；註釋 7.0 要留（赤江最關鍵的判斷在註 16）。"""
    out = mt.visual_lines(_page((36.0, 60.0, 6.0, "年報筑波社会学"),
                                (400.0, 60.0, 7.0, "(16)ここでは…")))
    assert [t for _x0, t in out] == ["(16)ここでは…"]


def test_indent_starts_a_paragraph_and_flush_continues_it():
    out = mt.paragraphs_from_lines([(60.0, "あたらしい段落が"), (50.0, "つづく。"),
                                    (60.0, "つぎの段落。")])
    assert out == ["あたらしい段落がつづく。", "つぎの段落。"]


def test_bare_page_number_line_is_dropped_from_the_text():
    assert mt.paragraphs_from_lines([(60.0, "本文である。"), (236.0, "1")]) == ["本文である。"]


# ── 跨頁接合 ──────────────────────────────────────────────────────────────────
def test_heal_rejoins_a_paragraph_split_by_a_page_break():
    """段落首行的縮排在換頁處判不出來（新的一頁一律從版心起算）。"""
    assert mt.heal(["前半に句点はなく", "後半がつづく。"]) == ["前半に句点はなく後半がつづく。"]


def test_heal_keeps_paragraphs_that_ended_properly():
    assert mt.heal(["おわった。", "つぎ。"]) == ["おわった。", "つぎ。"]


def test_heal_pairs_keeps_the_page_where_the_paragraph_started():
    """跨頁的段落算在它**開始**的那一頁——引註的通例。"""
    assert mt.heal_pairs([("前半に句点はなく", "3"), ("後半がつづく。", "4")]) == \
        [("前半に句点はなく後半がつづく。", "3")]


def test_heal_pairs_leaves_separate_paragraphs_with_their_own_pages():
    assert mt.heal_pairs([("おわった。", "3"), ("つぎ。", "4")]) == \
        [("おわった。", "3"), ("つぎ。", "4")]


# ── 印刷頁碼 ──────────────────────────────────────────────────────────────────
def test_folio_read_from_the_foot_of_the_page():
    assert mt.folio_of([(60.0, "本文のおわり。"), (236.0, "7")]) == "7"


def test_folio_takes_the_last_numeric_line_not_a_number_inside_the_body():
    """正文裡的年號（1890）在前面，頁碼在最後一行——由後往前找才對。"""
    assert mt.folio_of([(60.0, "1890"), (60.0, "本文。"), (236.0, "5")]) == "5"


def test_folio_absent_returns_none():
    """抓不到就 None，不可捏——[[feedback_transcribe_page_numbers]]。"""
    assert mt.folio_of([(60.0, "本文だけのページ。")]) is None


# ── OCR 誤字 ──────────────────────────────────────────────────────────────────
def test_known_ocr_confusions_are_fixed():
    assert mt.clean_ocr("原理にもとつく") == "原理にもとづく"
    assert mt.clean_ocr("勅語を漢発する") == "勅語を渙発する"
    assert mt.clean_ocr("良心の答めを感じ") == "良心の咎めを感じ"


def test_spaces_inserted_by_ocr_inside_words_are_removed():
    assert mt.clean_ocr("内 村　鑑 三") == "内村鑑三"


def test_citation_bracket_period_misread_as_zero():
    assert mt.clean_ocr("[鈴木1993a:79]0") == "[鈴木1993a:79]。"


def test_english_word_boundaries_survive():
    """除空白只能吃日文那一側。無差別拿掉會把論文的英文摘要碾成一團
    （「The'Hesitant'BodyintheRitualSpace」），而且看起來只是「沒有空格」。"""
    assert mt.clean_ocr("The 'Hesitant' Body in the Ritual Space") == \
        "The 'Hesitant' Body in the Ritual Space"


def test_mixed_script_keeps_the_latin_side():
    assert mt.clean_ocr("内村 and Uchimura は同じ") == "内村 and Uchimura は同じ"


def test_runs_of_spaces_collapse_to_one():
    assert mt.clean_ocr("Uchimura    Kanzo") == "Uchimura Kanzo"
