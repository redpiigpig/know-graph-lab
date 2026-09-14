# -*- coding: utf-8 -*-
"""獵書佇列的「指定作家插隊」比對（zlib_wanted._is_focus）。

🚨 比對是**子字串包含**，中文譯名一旦短就會咬到別人：指定「伯格」（Peter Berger）
會把**潘能伯格**（Wolfhart Pannenberg，德國神學家）與**斯邦伯格**（Alan Sponberg）
一起提到佇列最前面 —— 實測前 12 名裡就有兩筆是潘能伯格。
插隊名額本來就少，被別人佔走等於使用者點名的那位還是拿不到。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import zlib_wanted as zw  # noqa: E402


def _item(who="", zh="", query=""):
    return {"who": who, "zh": zh, "query": query}


class TestIsFocus:
    def test_named_author_matches(self):
        assert zw._is_focus(_item(who="Peter Berger", zh="伯格《資本主義革命》"))
        assert zw._is_focus(_item(who="彼得·贝格尔", zh="貝格爾《神聖的帷幕》"))
        assert zw._is_focus(_item(who="Thomas Luckmann", zh="盧克曼《無形的宗教》"))

    def test_case_insensitive(self):
        assert zw._is_focus(_item(query="peter berger sacred canopy"))

    def test_matches_on_any_of_the_three_fields(self):
        assert zw._is_focus(_item(who="", zh="", query="Luckmann Invisible Religion"))

    def test_pannenberg_is_not_berger(self):
        # 🚨 潘能伯格是另一個人（Wolfhart Pannenberg）
        assert not zw._is_focus(_item(who="Wolfhart Pannenberg", zh="潘能伯格《系統神學》"))
        assert not zw._is_focus(_item(who="Pannenberg", zh="潘能伯格《科學理論與神學》"))

    def test_sponberg_is_not_berger(self):
        assert not zw._is_focus(
            _item(who="Alan Sponberg", zh="斯邦伯格《早期佛教對女性與陰性的態度》"))

    def test_bergson_is_not_berger(self):
        # 🚨 柏格森（Henri Bergson）≠ 柏格（Berger 的另一種譯名），差一個字
        assert not zw._is_focus(_item(who="柏格森", zh="柏格森《心力：論心靈與身體的關係》"))
        assert not zw._is_focus(_item(who="Henri Bergson", query="Bergson Matter and Memory"))

    def test_oldenberg_is_not_berger(self):
        assert not zw._is_focus(
            _item(who="Hermann Oldenberg", zh="奧登伯格《佛陀：他的生平、教說與教團》"))

    def test_unrelated_author_untouched(self):
        assert not zw._is_focus(_item(who="Mary Douglas", zh="道格拉斯《潔淨與危險》"))

    def test_empty_item(self):
        assert not zw._is_focus(_item())
