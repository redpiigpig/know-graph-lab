"""taixu_build pure parser tests; no network or database access."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import taixu_build as tb  # noqa: E402

TEI = "http://www.tei-c.org/ns/1.0"
CB = "http://www.cbeta.org/ns/1.0"

SAMPLE = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI}" xmlns:cb="{CB}">
 <teiHeader><fileDesc><titleStmt>
  <title level="m" xml:lang="zh-Hant">太虛大師全書．測試編</title>
 </titleStmt><publicationStmt><date>2025-06-16</date></publicationStmt></fileDesc>
 <encodingDesc><charDecl><char xml:id="CB00001"><charProp>
  <localName>composition</localName><value>[木*石]</value>
 </charProp></char></charDecl></encodingDesc></teiHeader>
 <text><body>
  <cb:div><cb:mulu level="1">第一章</cb:mulu><head>第一章</head>
   <byline>——測試講記——</byline>
   <p>正文<lb n="1"/>接續<note>校注不入文</note><app><lem>正字</lem><rdg>異文</rdg></app><g ref="#CB00001"/>。</p>
   <list><item>甲項</item><item>乙項</item></list>
   <lg><l>第一句<caesura/>下半句</l><l>第二句</l></lg>
   <dialog><sp><speaker>甲</speaker><p>問。</p></sp><sp><speaker>乙</speaker><p>答。</p></sp></dialog>
   <table><row><cell>欄一</cell><cell>欄二</cell></row></table>
   <cb:div><head>第一節</head><p>節正文。</p></cb:div>
  </cb:div>
 </body></text>
</TEI>"""


def parse():
    return tb.parse_tei_chunks(
        SAMPLE,
        volume="測試編",
        parent_volume="法藏",
        book_prefix="測試編",
        source_stem="TX99n9999",
    )


def test_title_and_nested_paths():
    title, chunks = parse()
    assert title == "太虛大師全書．測試編"
    assert chunks[0]["chapter_path"] == "測試編 · 第一章"
    assert chunks[-1]["chapter_path"] == "測試編 · 第一章 · 第一節"


def test_notes_and_apparatus_are_not_duplicated():
    _, chunks = parse()
    content = chunks[0]["content"]
    assert "校注不入文" not in content
    assert "異文" not in content
    assert "正文接續正字[木*石]。" in content


def test_structured_blocks_are_preserved():
    _, chunks = parse()
    content = chunks[0]["content"]
    assert "- 甲項\n- 乙項" in content
    assert "第一句　下半句\n第二句" in content
    assert "〔甲〕問。" in content and "〔乙〕答。" in content
    assert "欄一　│　欄二" in content


def test_metadata_and_indices_are_stable():
    _, chunks = parse()
    assert [c["chunk_index"] for c in chunks] == [1, 2]
    assert [c["page_number"] for c in chunks] == [1, 2]
    assert all(c["volume"] == "測試編" for c in chunks)
    assert all(c["parent_volume"] == "法藏" for c in chunks)
    assert all(c["source_id"] == "TX99n9999" for c in chunks)


def test_long_content_is_bounded():
    huge = SAMPLE.replace("節正文。", "文" * (tb.MAX_CHARS * 2 + 123))
    _, chunks = tb.parse_tei_chunks(
        huge,
        volume="測試編",
        parent_volume="法藏",
        book_prefix="測試編",
    )
    assert len(chunks) >= 3
    assert max(len(c["content"]) for c in chunks) <= tb.MAX_CHARS
    assert any("續 2" in c["chapter_path"] for c in chunks)


def test_registry_is_complete_and_uses_all_40_xml_files():
    registry = tb.load_registry()
    assert list(registry)[0] == "TXA001"
    assert list(registry)[-1] == "TX0020"
    assert len(registry) == 21
    assert sum(len(meta["sources"]) for meta in registry.values()) == 40
    assert len({meta["ebook_id"] for meta in registry.values()}) == 21
