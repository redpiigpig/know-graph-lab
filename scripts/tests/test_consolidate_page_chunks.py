# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import consolidate_page_chunks as cp  # noqa: E402

PAGE = ("傳統（此為十世紀5°的百丈禪師所創）證嚴上人\n靠著自己的勞力過活。食品添加物，51並於各分會出售。52此外，1967年搬遷。\n\n"
        "———————————————\n50譯註：此處應為八或九世紀。\n51譯註：該添加物品名為「二十二味五穀粉」。\n52譯註：該商店即「靜思書軒」。")


def test_split_page_notes():
    body, notes = cp.split_page(PAGE)
    assert [n for n, _ in notes] == [50, 51, 52]
    assert notes[0][1].startswith("譯註：此處應為")


def test_link_markers_including_degree_ocr_and_skips_years():
    body, notes = cp.split_page(PAGE)
    out, found = cp.link_markers(body, [n for n, _ in notes])
    assert found == [50, 51, 52]
    assert "十世紀[^50]的" in out and "添加物，[^51]並於" in out and "1967年" in out


def test_consolidate_merges_same_section_and_collects_notes():
    chunks = [
        {"chunk_index": 0, "chunk_type": "page", "page_number": 10, "printed_page": 3, "chapter_path": "第一章 / 甲", "content": "正文第一頁，句子未完"},
        {"chunk_index": 1, "chunk_type": "page", "page_number": 11, "printed_page": 4, "chapter_path": "第一章 / 甲", "content": PAGE},
        {"chunk_index": 2, "chunk_type": "page", "page_number": 12, "printed_page": 5, "chapter_path": "第一章 / 乙", "content": "下一節。"},
    ]
    out = cp.consolidate(chunks)
    assert len(out) == 2
    a = out[0]
    assert a["page_numbers"] == [10, 11] and a["page_number"] == 10 and a["printed_page"] == 3
    assert "句子未完{{p:4}}傳統" in a["content"]          # 句中跨頁直接接上
    assert "\n\n(50) 譯註" in a["content"] and "(52) 譯註" in a["content"]
    assert out[1]["chunk_index"] == 1 and out[1]["content"].startswith("{{p:5}}")
