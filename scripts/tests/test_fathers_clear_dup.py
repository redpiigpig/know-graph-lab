# -*- coding: utf-8 -*-
"""整塊重複來源欄清除的純函式測試。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fathers_clear_dup_sources import clear_langs, dup_indices  # noqa: E402

BLOCK = "Haeresis Ariana late serpens aegre depelli potest. " * 20   # ~1000 字


def C(i, la=None, en=None, source_lang=None):
    c = {"chunk_index": i, "sources": {}}
    if la is not None:
        c["sources"]["la"] = la
    if en is not None:
        c["sources"]["en"] = en
    if source_lang:
        c["source_lang"] = source_lang
        c["source_text"] = c["sources"].get(source_lang, "")
    return c


def test_dup_indices_finds_the_repeated_block():
    chunks = [C(0, la=BLOCK), C(1, la=BLOCK), C(2, la=BLOCK + "尾巴不同")]
    assert dup_indices(chunks, "la") == [0, 1]


def test_dup_indices_ignores_short_shared_quotations():
    """🚨 兩封信引同一句經文（23–42 字）本來就會重複，清掉是真的丟資料。
    巴西流《書信集》曾因此被誤報 5 組。"""
    short = "ἐν ἀρχῇ ἦν ὁ λόγος"
    chunks = [C(0, la=short), C(1, la=short)]
    assert dup_indices(chunks, "la") == []


def test_dup_indices_ignores_unique_blocks():
    chunks = [C(0, la=BLOCK), C(1, la=BLOCK.replace("Ariana", "Sabelliana"))]
    assert dup_indices(chunks, "la") == []


def test_dup_indices_handles_missing_sources():
    chunks = [{"chunk_index": 0}, C(1, la=BLOCK), C(2, la=BLOCK)]
    assert dup_indices(chunks, "la") == [1, 2]


def test_clear_langs_blanks_the_column():
    c = C(0, la=BLOCK)
    assert clear_langs(c, "la") is True
    assert c["sources"]["la"] == ""


def test_clear_langs_keeps_the_key():
    """🚨 清成空字串，不是刪掉 key。reader 拿 source_order 去查 sources，
    key 不見時的行為與空字串不同。"""
    c = C(0, la=BLOCK)
    clear_langs(c, "la")
    assert "la" in c["sources"]


def test_clear_langs_also_clears_the_legacy_mirror():
    """source_text/source_lang 是舊兩欄 reader 的鏡射；不一起清，舊 reader 照樣整卷。"""
    c = C(0, la=BLOCK, source_lang="la")
    clear_langs(c, "la")
    assert c["source_text"] == ""


def test_clear_langs_leaves_other_languages_alone():
    c = C(0, la=BLOCK, en="English text here")
    clear_langs(c, "la")
    assert c["sources"]["en"] == "English text here"


def test_clear_langs_noop_when_already_empty():
    c = C(0, la="")
    assert clear_langs(c, "la") is False
