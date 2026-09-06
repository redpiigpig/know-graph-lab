# -*- coding: utf-8 -*-
"""Test-first lock for the NDL デジタルコレクション source module.

無教會譜系裡戰前那批（畔上賢造 16 部、矢內原忠雄 9 部、藤井武 7 部）都是公有領域，
但青空文庫沒有、libgen 沒有——只有 NDL 的掃描本。NDL 有三層公開範圍，只有
「インターネット公開」那一層能用（IIIF manifest 回 200；館內限定回 404）。

取源的兩個入口：
  * `https://lab.ndl.go.jp/dl/api/book/{pid}` —— 次世代デジタルライブラリー的書誌，
    帶 **index（目次）**，每一條是「章名／印刷頁 (NNNN.jp2)」，分章直接靠它。
  * `https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json` —— 影像；Lab API 偶爾
    page=0（例：矢內原《內村鑑三與新渡戶稻造》pid 1057723），得回頭數 canvas。

這些鎖 PURE helper —— 零網路、零 OCR、零 DB。
"""
import ndl_build as nb


class TestParseTocEntry:
    """NDL 目次一條的三種寫法都要吃得下。"""

    def test_title_slash_page_then_image(self):
        e = nb.parse_toc_entry("第一　教派ではない/1  (0003.jp2)")
        assert e == {"title": "第一　教派ではない", "printed_page": "1", "image": 3}

    def test_spaced_slash_form(self):
        e = nb.parse_toc_entry("舊新約の二大預言とその成就 / 1 (0006.jp2)")
        assert e == {"title": "舊新約の二大預言とその成就", "printed_page": "1", "image": 6}

    def test_no_printed_page(self):
        e = nb.parse_toc_entry("充さるべき預言 / (0006.jp2)")
        assert e == {"title": "充さるべき預言", "printed_page": "", "image": 6}

    def test_front_matter(self):
        assert nb.parse_toc_entry("標題  (0002.jp2)") == {"title": "標題", "printed_page": "", "image": 2}

    def test_unparseable_returns_none(self):
        assert nb.parse_toc_entry("") is None
        assert nb.parse_toc_entry("何かの行") is None


class TestSectionsFromIndex:
    INDEX = [
        "標題  (0002.jp2)",
        "目次  (0003.jp2)",
        "第一　教派ではない/1  (0003.jp2)",
        "第二　起源/2  (0004.jp2)",
        "第三　現状/4  (0005.jp2)",
    ]

    def test_front_matter_dropped(self):
        secs = nb.sections_from_index(self.INDEX, total_images=18)
        assert [s["title"] for s in secs] == ["第一　教派ではない", "第二　起源", "第三　現状"]

    def test_ranges_are_contiguous_and_last_runs_to_the_end(self):
        secs = nb.sections_from_index(self.INDEX, total_images=18)
        assert (secs[0]["start"], secs[0]["end"]) == (3, 4)
        assert (secs[1]["start"], secs[1]["end"]) == (4, 5)
        assert (secs[2]["start"], secs[2]["end"]) == (5, 19)  # end 為 exclusive

    def test_no_index_falls_back_to_one_whole_book_section(self):
        secs = nb.sections_from_index([], total_images=12, fallback_title="全書")
        assert len(secs) == 1
        assert (secs[0]["title"], secs[0]["start"], secs[0]["end"]) == ("全書", 1, 13)


class TestImageUrl:
    def test_iiif_full_size(self):
        assert nb.image_url("1099766", 3) == \
            "https://dl.ndl.go.jp/api/iiif/1099766/R0000003/full/full/0/default.jpg"

    def test_iiif_scaled_width(self):
        assert nb.image_url("1099766", 12, width=1800) == \
            "https://dl.ndl.go.jp/api/iiif/1099766/R0000012/full/1800,/0/default.jpg"


class TestCleanOcrText:
    def test_strips_ruby_parentheses_and_fullwidth_indent(self):
        # 直排舊書 OCR 常把振り仮名括進來；行首全形空白是排版縮排不是內容
        assert nb.clean_ocr_text("　基督教（キリストけう）は") == "基督教は"

    def test_drops_page_number_only_lines(self):
        assert nb.clean_ocr_text("一二三\n\n本文である。\n\n4") == "本文である。"

    def test_keeps_real_paragraphs(self):
        assert nb.clean_ocr_text("第一段である。\n\n第二段である。") == "第一段である。\n\n第二段である。"


class TestParagraphsFromPages:
    def test_sentence_continuing_across_a_page_is_rejoined(self):
        # 前一頁末沒有句點 → 與下一頁首段接回去（直排書換頁不換段是常態）
        out = nb.paragraphs_from_pages(["前のページの終りの文が", "つづいて終る。"])
        assert out == ["前のページの終りの文がつづいて終る。"]

    def test_completed_sentence_starts_a_new_paragraph(self):
        out = nb.paragraphs_from_pages(["一つ目の段落である。", "二つ目の段落である。"])
        assert out == ["一つ目の段落である。", "二つ目の段落である。"]

    def test_blank_pages_skipped(self):
        out = nb.paragraphs_from_pages(["本文。", "", "   ", "つづき。"])
        assert out == ["本文。", "つづき。"]
