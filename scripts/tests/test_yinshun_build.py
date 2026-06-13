"""yinshun_build 純解析函式測試（零 network/DB）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yinshun_build as yb  # noqa: E402

TEI = "http://www.tei-c.org/ns/1.0"
CB = "http://www.cbeta.org/ns/1.0"

# 最小 CBETA TEI 樣本：書名 + 自序(平鋪) + 一章>一節>一目(巢狀)，含 lb 邊碼與 note 夾注。
SAMPLE = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xmlns:cb="{CB}">
 <teiHeader><fileDesc><titleStmt>
   <title level="s" xml:lang="zh-Hant">印順法師佛學著作集</title>
   <title level="m" xml:lang="zh-Hant">佛法概論</title>
 </titleStmt></fileDesc></teiHeader>
 <text><body>
   <p>卷首散段（body 直屬）。</p>
   <cb:div type="other"><cb:mulu level="1"/><head>自序</head>
     <p>自序第一段<lb n="a001a01" ed="Y"/>接續文字<note place="inline">夾注不入文</note>結束。</p>
     <p>自序第二段。</p>
   </cb:div>
   <cb:div type="other"><cb:mulu level="1"/><head>第一章　法</head>
     <p>章前引言一段。</p>
     <cb:div type="other"><cb:mulu level="2"/><head>第一節　法</head>
       <cb:div type="other"><cb:mulu level="3"/><head>文義法</head>
         <p>文義法正文。</p>
       </cb:div>
     </cb:div>
   </cb:div>
 </body></text>
</TEI>"""


def test_book_title_prefers_chinese_m_level():
    book, _ = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    assert book == "佛法概論"


def test_chunk_count_one_per_div_with_direct_paras():
    # body直屬 + 自序 + 章前引言 + 文義法 = 4 個含直屬<p>的節點
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    assert len(chunks) == 4


def test_note_stripped_lb_dropped_text_continuous():
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    serial = chunks[1]["content"]  # 自序
    assert "夾注不入文" not in serial
    assert "a001a01" not in serial
    assert "自序第一段接續文字結束。" in serial


def test_paragraphs_joined_with_blank_line():
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    assert chunks[1]["content"].count("\n\n") == 1  # 自序兩段


def test_chapter_path_is_ancestor_head_stack():
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集",
                                    book_prefix="佛法概論")
    leaf = [c for c in chunks if "文義法" in c["chapter_path"]][0]
    assert leaf["chapter_path"] == "佛法概論 · 第一章　法 · 第一節　法 · 文義法"


def test_single_language_no_sources_field():
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    assert "sources" not in chunks[0]
    assert "source_text" not in chunks[0]


def test_volume_metadata_propagated():
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    assert all(c["volume"] == "佛法概論" and c["parent_volume"] == "妙雲集" for c in chunks)


def test_chunk_index_sequential_from_one():
    _, chunks = yb.parse_tei_chunks(SAMPLE, volume="佛法概論", parent_volume="妙雲集")
    assert [c["chunk_index"] for c in chunks] == [1, 2, 3, 4]
