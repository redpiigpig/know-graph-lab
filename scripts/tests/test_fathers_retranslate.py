# -*- coding: utf-8 -*-
"""教父卷補譯的純函式測試。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fathers_retranslate_untranslated import needs_retranslate, promote_content_to_en  # noqa: E402

EN = ("than which no more blooming colour was ever seen, then let corporeal beauty be "
      "cultivated too, symmetry of limbs and members, with a fair complexion. " * 4)
ZH = "因此，那些精通奧祕的人也禁止吃心臟；教導我們不應當通過懶惰和煩擾而啃食和消耗靈魂。" * 6


def test_needs_retranslate_catches_english_in_the_chinese_column():
    assert needs_retranslate({"content": EN})


def test_needs_retranslate_passes_real_chinese():
    assert not needs_retranslate({"content": ZH})


def test_needs_retranslate_ignores_english_footnotes_under_the_separator():
    """🚨 教父卷的註腳大量是原樣保留的英文書目。連同正文一起算漢字率，正文明明
    譯好的段也會被判成未譯——實測 ANF 第二卷 #8 正文 483 個漢字、註腳 1,093 個
    拉丁字母，整段只有 0.26。"""
    mixed = ZH + "\n\n" + "-" * 20 + "\n\n" + EN
    assert not needs_retranslate({"content": mixed})


def test_needs_retranslate_ignores_number_only_index_pages():
    """頁碼索引整段只有數字，沒東西可譯（實測 #2033 2,981 字只有 4 個拉丁字母）。"""
    assert not needs_retranslate({"content": " ".join(str(i) for i in range(300, 700))})


def test_needs_retranslate_ignores_short_fragments():
    assert not needs_retranslate({"content": "Book III."})


def test_needs_retranslate_blank():
    assert not needs_retranslate({"content": ""})
    assert not needs_retranslate({})


# ── promote_content_to_en ───────────────────────────────────────────────────

def test_promote_moves_english_into_the_source_column():
    c = {"content": EN, "sources": {}}
    assert promote_content_to_en(c) is True
    assert c["sources"]["en"] == EN.strip()
    assert c["source_text"] == EN.strip()
    assert c["source_lang"] == "en"


def test_promote_refuses_when_the_english_column_already_has_text():
    """🚨 英文欄已經有東西就不動——那代表狀況不是「沒翻」，亂搬會把真正的英文
    原文蓋掉，而且蓋掉之後查不回來。"""
    c = {"content": EN, "sources": {"en": "the real English source"}}
    assert promote_content_to_en(c) is False
    assert c["sources"]["en"] == "the real English source"


def test_promote_creates_the_sources_dict_when_missing():
    c = {"content": EN}
    assert promote_content_to_en(c) is True
    assert c["sources"]["en"]


def test_promote_keeps_an_existing_source_lang():
    c = {"content": EN, "sources": {}, "source_lang": "la"}
    promote_content_to_en(c)
    assert c["source_lang"] == "la"


def test_promote_noop_on_blank_content():
    c = {"content": "   ", "sources": {}}
    assert promote_content_to_en(c) is False
