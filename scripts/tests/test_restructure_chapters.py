import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import restructure_chapters as r  # noqa: E402


def test_labels_ordinal_mode_uses_names_only_for_parts():
    titles = ["總導讀韓松的『鬼魅中國』", "宇宙墓碑", "燦爛文化", "後記　邂逅科技時代的文學"]
    assert r.chapter_labels(titles) == ["總導讀", "1", "2", "後記"]


def test_labels_numbered_mode():
    titles = ["導論", "第一章　臺灣", "第二章　慈濟", "Chapter 3 Foo", "結論"]
    assert r.chapter_labels(titles) == ["導論", "1", "2", "3", "結論"]


def test_labels_are_unique():
    assert r.chapter_labels(["序", "甲篇", "序"]) == ["序", "1", "序(2)"]


def test_is_countable_skips_markers_and_notes():
    assert not r.is_countable("一")
    assert not r.is_countable("上篇")
    assert not r.is_countable("[1]雙生子佯謬，一個思想實驗。")
    assert not r.is_countable("{{p:12}}")
    assert r.is_countable("“那是什麼？”")


def test_junk_title_detection():
    assert r.JUNK_TITLE.search("第一部分諾斯底福音書間η")
    assert r.JUNK_TITLE.search("第二部分救贖主對話篇J")
    assert not r.JUNK_TITLE.search("第一章　Taiwan 的宗教")


def test_build_chapter_headings_numbers_and_notes():
    cs = [
        {"chapter_path": "第一章　甲 / 第一節", "content": "第一章甲第一節正文一句。\n\n———————————————\n\n(1) 註一"},
        {"chapter_path": "第一章　甲 / 第二節", "content": "第二節續寫[^1]。\n\n———————————————\n\n(1) 另一條註"},
    ]
    text = r.build_chapter("1", "第一章　甲", cs, {})
    assert text.startswith("## 第一章　甲\n\n### 第一節\n\n{{s:1-1-1}}正文一句。")
    assert "### 第二節\n\n{{s:1-2-1}}續寫[^2]。" in text        # 重複註號重編
    assert "(1) 註一" in text and "(2) 另一條註" in text


def test_promote_flat_sections_groups_under_numbered_chapters():
    cs = [{"chapter_path": t, "content": "x"} for t in
          ["目錄", "導言", "伊本的理論", "第一章 帝國的誕生", "亞述", "羅馬", "第二章 排斥暴力", "流行病", "結語", "定居的世界"]]
    out = [c["chapter_path"] for c in r.promote_flat_sections(cs)]
    assert out == ["目錄", "導言", "導言 / 伊本的理論", "第一章 帝國的誕生", "第一章 帝國的誕生 / 亞述",
                   "第一章 帝國的誕生 / 羅馬", "第二章 排斥暴力", "第二章 排斥暴力 / 流行病", "結語", "結語 / 定居的世界"]


def test_promote_flat_sections_leaves_unnumbered_books_alone():
    cs = [{"chapter_path": t, "content": "x"} for t in ["宇宙墓碑", "燦爛文化", "後記"]]
    assert [c["chapter_path"] for c in r.promote_flat_sections(cs)] == ["宇宙墓碑", "燦爛文化", "後記"]
