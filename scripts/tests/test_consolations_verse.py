# -*- coding: utf-8 -*-
"""《基督信徒的慰藉》引詩的「原文　／　中譯」並列。

內村直接引英德文詩，`needs_translation` 判它們不是日文而整批跳過，中文欄留白。
使用者 2026-09-10 定調原文＋中譯並列。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fix_consolations_verse as fv  # noqa: E402


def test_original_and_translation_are_joined():
    assert fv.bilingual("In Deutschland geboren,", "生於德意志，") == \
        "In Deutschland geboren,　／　生於德意志，"


def test_gaiji_umlaut_is_restored():
    """青空文庫把德文變音符號輸出成「※」。既然要並列原文，就補回可讀的樣子。"""
    assert fv.bilingual("Ein B※rger der Welt.", "世界的公民。").startswith(
        "Ein Bürger der Welt.")
    assert "mächtigsten" in fv.bilingual("Der starke ist m※chtigsten allein.", "強者獨處之時最強。")


def test_whitespace_is_trimmed():
    assert fv.bilingual("  a  ", "  甲  ") == "a　／　甲"


def test_every_entry_has_a_chinese_side():
    """表裡不可留空的中譯——那就回到原本「中文欄是英文」的問題了。"""
    for _sec, _idx, _head, zh in fv.VERSE:
        assert zh.strip()


def test_entries_are_keyed_by_source_prefix_not_only_index():
    """段落編號不是穩定鍵（[[feedback_reader_silent_failures]]），
    所以每一筆都要帶原文開頭供比對。"""
    for _sec, _idx, head, _zh in fv.VERSE:
        assert head.strip()


def test_no_duplicate_targets():
    seen = {(sec, idx) for sec, idx, _h, _z in fv.VERSE}
    assert len(seen) == len(fv.VERSE)
