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


def test_merge_epigraphs_into_one_quote():
    ps = ["人類在四五萬年中沒有任何變化。", "——斯蒂芬·傑伊·古爾德（Stephen Jay Gould）", "正文開始。"]
    assert r.merge_epigraphs(ps) == ["> 人類在四五萬年中沒有任何變化。\n> ——斯蒂芬·傑伊·古爾德（Stephen Jay Gould）",
                                     "正文開始。"]


def test_place_figures_caption_and_anchor():
    import epub_figures as ef
    cs = [{"content": "前面這一段正文到這裡結束了喔喔喔。\n\n{{p:6}}維倫多夫的維納斯，約公元前23000年燒製\n\n後文"}]
    figs = [ef.Figure("a.jpeg", "OEBPS/a.jpeg", "维伦多夫的维纳斯，约公元前23000年烧制", ""),
            ef.Figure("b.jpeg", "OEBPS/b.jpeg", "", ef.norm("前面這一段正文到這裡結束了喔喔喔。")[-20:])]
    out, used, miss = ef.place_figures(cs, figs, "x")
    ps = out[0]["content"].split("\n\n")
    assert ps[1] == "![](/api/ebooks/x/image/b.jpeg)"
    assert ps[2] == "{{p:6}}![維倫多夫的維納斯，約公元前23000年燒製](/api/ebooks/x/image/a.jpeg)"
    assert len(used) == 2 and miss == 0


def test_paginate_about_5000_per_page_with_notes():
    import rebuild_reference_bilingual as rb
    text = ("## 第一章\n\n{{s:1-0-1}}引言。\n\n### 甲\n\n{{s:1-1-1}}" + "甲" * 4000 + "[^1]\n\n{{s:1-1-2}}" + "丙" * 3000
            + "\n\n### 乙\n\n{{s:1-2-1}}" + "乙" * 2000 + "[^2]\n\n" + rb.FOOT_RULE + "\n\n(1) 註一\n\n(2) 註二")
    pages = r.paginate(text, "第一章", {"page_number": 5}, {})
    assert [p["chapter_path"] for p in pages] == ["第一章", "第一章", "第一章 / 乙"]
    assert pages[1]["content"].startswith("{{s:1-1-2}}")          # 節太長：段落交界換頁，續頁沿用路徑
    assert "(1) 註一" in pages[0]["content"] and "(2) 註二" in pages[2]["content"]
    assert all(len(p["content"]) < 7000 for p in pages)


def test_paginate_short_chapter_untouched():
    assert len(r.paginate("## 甲\n\n{{s:1}}短。", "甲", {}, {})) == 1


def test_paginate_trailing_heading_page_keeps_previous_pages():
    paras = [f"{{{{s:1-{k}}}}}" + "字" * 3000 for k in range(1, 5)] + ["### p. 52"]
    text = "## 章\n\n" + "\n\n".join(paras)
    pages = r.paginate(text, "章", {}, {})
    joined = "\n\n".join(p["content"] for p in pages)
    assert all(f"{{{{s:1-{k}}}}}" in joined for k in range(1, 5))
    assert len({p["content"] for p in pages}) == len(pages)


def test_numbered_points_outside_rule_stay_in_body():
    import rebuild_reference_bilingual as rb
    body, notes = r.split_notes_keep_order("正文開頭。\n\n(1) 第一個分點論述。\n\n(2) 第二點。\n\n"
                                           + rb.FOOT_RULE + "\n\n(1) 真正的註。")
    assert body == ["正文開頭。", "(1) 第一個分點論述。", "(2) 第二點。"]
    assert notes == ["(1) 真正的註。"]
