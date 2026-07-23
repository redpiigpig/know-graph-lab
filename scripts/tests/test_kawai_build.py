"""kawai_build 純解析函式測試（零 network/DB）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kawai_build as kb  # noqa: E402

# 仿 OEBPS/Text/partNNNN.xhtml：<p> 段落 + 書名頁殘留的套書總標題。
PART = """<html><body>
  <p>河合隼雄心理学经典（读客熊猫君出品，套装共6册）</p>
  <h2>孩提时代</h2>
  <p>自孩提时代起，我就相当喜欢读书。</p>
  <p>不论《汤姆的午夜庭院》，都令我着迷。</p>
</body></html>"""

# 仿 toc.ncx 兩層 navMap：章（深度0）→ 節（深度1）。
NCX = """<?xml version="1.0"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/">
 <navMap>
  <navPoint><navLabel><text>儿童文学与灵魂</text></navLabel>
    <content src="Text/part0004.xhtml#filepos7261"/>
    <navPoint><navLabel><text>孩提时代</text></navLabel>
      <content src="Text/part0004.xhtml#filepos7358"/></navPoint>
    <navPoint><navLabel><text>和儿童文学家们的交流</text></navLabel>
      <content src="Text/part0005.xhtml#filepos13542"/></navPoint>
  </navPoint>
  <navPoint><navLabel><text>后记</text></navLabel>
    <content src="Text/part0064.xhtml#filepos1"/></navPoint>
 </navMap>
</ncx>"""


def test_extract_drops_set_title_page():
    paras = kb.extract_part_text(PART)
    assert all(not p.startswith("河合隼雄心理学经典") for p in paras)


def test_extract_keeps_body_paragraphs_separately():
    paras = kb.extract_part_text(PART)
    assert "孩提时代" in paras
    assert "自孩提时代起，我就相当喜欢读书。" in paras
    assert len(paras) == 3  # heading + 2 body paras（套書標題已去）


def test_chapter_map_level0_is_chapter():
    m = kb.build_chapter_map(NCX)
    assert m["part0064.xhtml"] == ("后记", None)


def test_chapter_map_part_takes_first_nav_chapter_only():
    # part0004 同時被章(儿童文学与灵魂)與節(孩提时代)指向 → 取章、節留空（章起始頁）。
    m = kb.build_chapter_map(NCX)
    assert m["part0004.xhtml"] == ("儿童文学与灵魂", None)


def test_chapter_map_level1_carries_parent_chapter():
    m = kb.build_chapter_map(NCX)
    assert m["part0005.xhtml"] == ("儿童文学与灵魂", "和儿童文学家们的交流")


def test_split_paras_blank_line_between():
    assert kb.split_paras(["甲", "乙"]) == "甲\n\n乙"
