# -*- coding: utf-8 -*-
"""laijohn 抓取的編碼嗅探。

這一項屬於「看起來像成功的失敗」：`errors="replace"` 讓解錯碼也不會拋例外，
抓取、寫檔、產索引全都回報成功，只有內容是亂碼。實際代價是已收的 4,221 篇
裡有 1,930 篇題名壞掉，而且過了好幾個月才被發現。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import laijohn_biographies as lj  # noqa: E402

ZH = "洪瑞鋒函述洪茂德的裔"


def test_decodes_big5_pages():
    assert lj.decode(ZH.encode("big5")) == ZH


def test_decodes_utf8_pages():
    assert lj.decode(ZH.encode("utf-8")) == ZH


def test_decodes_utf8_with_bom():
    # /archives/pj/pj-contents.htm 就是這一種：沒有 meta charset、但帶 BOM
    assert lj.decode(b"\xef\xbb\xbf" + ZH.encode("utf-8")) == ZH


def test_never_returns_replacement_chars_for_valid_input():
    for enc in ("big5", "utf-8"):
        assert "\ufffd" not in lj.decode(ZH.encode(enc))
