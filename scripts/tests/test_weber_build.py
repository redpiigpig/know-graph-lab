# -*- coding: utf-8 -*-
"""weber_build 的純解析函式（零 network/DB）。

盯著一個具體的失敗：這兩本 EPUB 的正文整篇裝在一個 xhtml 裡，只按檔案切會得到
一個三萬字的 chunk，reader 上就是一整片牆——所以錨點切節這一段必須綁住。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from weber_build import ncx_entries, spine_hrefs, split_by_anchors  # noqa: E402

OPF = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <manifest>
    <item id="cover" href="Text/cover.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="Text/nav.xhtml" media-type="application/xhtml+xml"/>
    <item id="intro" href="Text/Introduction.xhtml" media-type="application/xhtml+xml"/>
    <item id="body" href="Text/01.xhtml" media-type="application/xhtml+xml"/>
    <item id="review" href="Text/Review.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="cover"/><itemref idref="nav"/><itemref idref="intro"/>
    <itemref idref="body"/><itemref idref="review"/>
  </spine>
</package>"""

NCX = """<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <navMap>
    <navPoint><navLabel><text>導讀</text></navLabel>
      <content src="Text/Introduction.xhtml"/></navPoint>
    <navPoint><navLabel><text>【以學術為志業】</text></navLabel>
      <content src="Text/01.xhtml"/></navPoint>
    <navPoint><navLabel><text>1. 私聘講師</text></navLabel>
      <content src="Text/01.xhtml#sigil_toc_id_1"/></navPoint>
    <navPoint><navLabel><text>2. 學者選拔</text></navLabel>
      <content src="Text/01.xhtml#sigil_toc_id_2"/></navPoint>
  </navMap>
</ncx>"""


def test_spine_skips_cover_nav_and_review():
    assert spine_hrefs(OPF) == ["Text/Introduction.xhtml", "Text/01.xhtml"]


def test_ncx_entries_keep_anchors_in_order():
    assert ncx_entries(NCX) == [
        ("Introduction.xhtml", None, "導讀"),
        ("01.xhtml", None, "【以學術為志業】"),
        ("01.xhtml", "sigil_toc_id_1", "1. 私聘講師"),
        ("01.xhtml", "sigil_toc_id_2", "2. 學者選拔"),
    ]


def test_split_by_anchors_cuts_one_file_into_sections():
    html = ('<h1>以學術為志業</h1><p>開場白</p>'
            '<h2 id="sigil_toc_id_1">私聘講師</h2><p>甲</p>'
            '<h2 id="sigil_toc_id_2">學者選拔</h2><p>乙</p>')
    parts = split_by_anchors(html, ["sigil_toc_id_1", "sigil_toc_id_2"])
    assert [a for a, _ in parts] == [None, "sigil_toc_id_1", "sigil_toc_id_2"]
    assert "開場白" in parts[0][1]
    assert "甲" in parts[1][1] and "乙" not in parts[1][1]


def test_split_by_anchors_falls_back_to_whole_file():
    html = "<p>沒有任何錨點</p>"
    assert split_by_anchors(html, ["missing"]) == [(None, html)]


def test_split_by_anchors_follows_document_order_not_toc_order():
    """目錄順序不保證等於文件順序；切點得照文件裡真正的先後。"""
    html = '<h2 id="b">乙</h2><p>x</p><h2 id="a">甲</h2><p>y</p>'
    assert [a for a, _ in split_by_anchors(html, ["a", "b"])] == ["b", "a"]
