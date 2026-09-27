# -*- coding: utf-8 -*-
"""ncx_to_toc：nav.xhtml 被 Google Books 頁碼錨點弄丟條目時改用 NCX（2026-09-27《資本的世界史》）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import standardize_ebook as se  # noqa: E402

NCX = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><navMap>
 <navPoint id="p1"><navLabel><text>封面</text></navLabel><content src="Text/Cover.xhtml"/></navPoint>
 <navPoint id="p4"><navLabel><text>第一篇　資本的崛起</text></navLabel><content src="Text/Part1.xhtml"/>
  <navPoint id="p5"><navLabel><text>第一章　成長奇蹟</text></navLabel><content src="Text/Ch01.xhtml"/></navPoint>
  <navPoint id="p6"><navLabel><text>第二章　古羅馬人</text></navLabel><content src="Text/Ch02.xhtml#a1"/></navPoint>
 </navPoint>
</navMap></ncx>"""


def test_ncx_to_toc_keeps_every_chapter_and_nesting():
    toc = se.ncx_to_toc(NCX)
    assert toc[0].title == "封面" and toc[0].href == "Text/Cover.xhtml"
    sec, kids = toc[1]
    assert sec.title == "第一篇　資本的崛起"
    assert [k.title for k in kids] == ["第一章　成長奇蹟", "第二章　古羅馬人"]
    assert kids[1].href == "Text/Ch02.xhtml#a1"
    assert se.toc_entry_count(toc) == 4


def test_ncx_href_resolved_against_ncx_dir():
    toc = se.ncx_to_toc(NCX, "sub")
    assert toc[0].href == "sub/Text/Cover.xhtml"


def test_toc_entry_count_tolerates_single_link_level():
    from ebooklib import epub
    assert se.toc_entry_count(epub.Link("a.xhtml", "一", "1")) == 1
    assert se.toc_entry_count([(epub.Section("篇", "p.xhtml"), epub.Link("c.xhtml", "章", "2"))]) == 2
