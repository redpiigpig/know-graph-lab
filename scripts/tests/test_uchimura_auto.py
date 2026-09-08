# -*- coding: utf-8 -*-
"""uchimura_auto 的譯文品質閘。

這兩組守的都是**看起來完全正常**的錯：章名多一截 markdown 標記、
中文欄位裡放著日文原文。頁面照排、結構完美，只有讀者看得出不對。
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uchimura_auto as ua  # noqa: E402


class TestCleanHeading:
    def test_engine_echoing_the_source_heading_is_trimmed(self):
        # 引擎常把原標題連著譯文一起吐回來
        assert ua.clean_heading("門をたたけ 叩門吧", "門をたたけ") == "叩門吧"

    def test_markdown_marker_is_stripped(self):
        # clean_zh_output 刻意放行 `## ` 開頭（正文的內嵌小標要留著），
        # 但那條規則走到章名這一層，目錄就會長出「## 二　耶穌的聖召」。
        # 線上實際出現過 9 筆。
        assert ua.clean_heading("## 二　耶穌的聖召", "二　イエスの召命") == "二　耶穌的聖召"
        assert ua.clean_heading("### 第三節 地域的發展",
                                "第三節　地域的発展") == "第三節 地域的發展"

    def test_source_echo_trimming_still_applies_after_stripping_the_marker(self):
        # 剝掉標記之後才比對原標題，兩道規則的順序不能顛倒
        assert ua.clean_heading("## 第三節 地域的發展", "第三節") == "地域的發展"

    def test_marker_plus_source_echo_together(self):
        assert ua.clean_heading("## 門をたたけ 叩門吧", "門をたたけ") == "叩門吧"

    def test_empty_output_falls_back_to_the_source_heading(self):
        assert ua.clean_heading("", "序") == "序"
        assert ua.clean_heading("##", "序") == "序"

    def test_hash_inside_the_title_is_not_touched(self):
        assert ua.clean_heading("第 3 號 # 的意義", "その意味") == "第 3 號 # 的意義"


class TestKanaLeak:
    """引擎有時只翻一半、有時整段回抄原文，兩種都會原樣寫進譯文欄。
    中文正文不會有假名，所以「譯文帶假名」是很乾淨的判準。"""

    def test_untranslated_japanese_is_a_leak(self):
        assert ua._kana_leak("神は愛なり。", "神は愛なり。")

    def test_partial_translation_is_a_leak(self):
        assert ua._kana_leak("彼は王族の出ではなかった。",
                             "耶穌是平民。彼は王族の出ではなかった。")

    def test_clean_chinese_is_not_a_leak(self):
        assert not ua._kana_leak("神は愛なり。", "神就是愛。")

    def test_blank_output_is_not_a_leak(self):
        # 留白是防呆刻意的結果，不該再被判成滲漏而重試
        assert not ua._kana_leak("神は愛なり。", "")

    @pytest.mark.parametrize("src", ["＊　　　＊　　　＊", "In Deutschland geboren,"])
    def test_non_japanese_source_is_exempt(self, src):
        # 原文本來就不是日文散文（分隔符號、德文詩行），原樣留著是對的
        ua.use_author("uchimura")
        assert not ua._kana_leak(src, src)
