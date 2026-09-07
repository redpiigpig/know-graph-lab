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


class TestSectionPayload:
    """OCR 完的頁面 → 與 uchimura／howes 同形的 section JSON。

    形狀必須一致（heading／title_zh／src／zh），否則接不上 uchimura_auto 的
    checkpoint／翻譯／上架那一段。
    """

    def test_shape_matches_the_other_authors(self):
        sec = {"title": "第一　教派ではない", "start": 3, "end": 4}
        out = nb.section_payload(sec, {3: "無教會主義は教派ではない。"})
        assert list(out) == ["heading", "title_zh", "src", "zh"]
        assert out["heading"] == "第一　教派ではない"
        assert out["src"] == ["無教會主義は教派ではない。"]
        assert out["zh"] == []

    def test_pages_in_range_are_joined_into_paragraphs(self):
        sec = {"title": "第四", "start": 6, "end": 8}
        pages = {6: "教會に對する抗議として", 7: "無教會は起った。", 9: "別章の内容"}
        out = nb.section_payload(sec, pages)
        # 6 沒有句末標點 → 與 7 接回同一段；9 不在範圍內不可混進來
        assert out["src"] == ["教會に對する抗議として無教會は起った。"]

    def test_missing_page_is_skipped_not_crashed(self):
        sec = {"title": "第九", "start": 15, "end": 18}
        out = nb.section_payload(sec, {15: "傳道法。", 17: "續き。"})
        assert out["src"] == ["傳道法。", "續き。"]

    def test_title_zh_defaults_to_the_japanese_heading(self):
        """繁中章名還沒譯時先擺日文原題，不要留空字串（reader 目錄會變空白）。"""
        out = nb.section_payload({"title": "第二　起源", "start": 4, "end": 5}, {})
        assert out["title_zh"] == "第二　起源"
        assert out["src"] == []


class TestEmptyBuildGate:
    """OCR 還沒跑就 build，會寫出一堆結構正確但全空的 secN.json —— 頁面完全正常、
    目錄也在，只是每一章都沒有字。這是最難發現的一種失敗，寧可直接擋下來。"""

    def test_all_empty_is_refused(self):
        secs = [{"title": "第一", "start": 3, "end": 4},
                {"title": "第二", "start": 4, "end": 5}]
        assert nb.refuse_empty_build(secs, {}) is True

    def test_all_empty_even_with_blank_strings_is_refused(self):
        secs = [{"title": "第一", "start": 3, "end": 4}]
        assert nb.refuse_empty_build(secs, {3: "   \n\n"}) is True

    def test_any_real_text_passes(self):
        secs = [{"title": "第一", "start": 3, "end": 4},
                {"title": "第二", "start": 4, "end": 5}]
        assert nb.refuse_empty_build(secs, {3: "無教會主義は教派ではない。"}) is False


class TestSpread:
    """NDL 的掃描是**兩頁合成一張**（橫幅）。整張丟給 OCR 等於每頁只剩一半解析度，
    密排直書舊字讀不動，模型就開始編 —— 第一次試跑就編出一份完全不存在的目次。
    """

    def test_landscape_is_a_spread(self):
        assert nb.is_spread(3575, 2787) is True

    def test_portrait_is_a_single_page(self):
        assert nb.is_spread(1200, 1900) is False

    def test_right_half_comes_first(self):
        """日文直書右起：右半頁是前一頁，必須先讀。順序反了整本文意就倒著接。"""
        boxes = nb.split_spread_boxes(1000, 800)
        assert boxes == [(500, 0, 1000, 800), (0, 0, 500, 800)]

    def test_odd_width_loses_no_column(self):
        boxes = nb.split_spread_boxes(1001, 800)
        right, left = boxes
        assert left[0] == 0 and right[2] == 1001
        assert left[2] == right[0]      # 中線一致，不重疊也不漏


class TestTocCanary:
    """幻覺偵測：拿 NDL 目次 API 當獨立真值，去驗 OCR 到底有沒有在讀圖。

    這批材料（直排舊字舊假名）最危險的失敗不是讀不出來，而是**部分錨定的編造**
    —— 模型讀到零星字詞，再用通順日文把中間補起來，整頁看起來毫無異狀。
    唯一能自動抓到的辦法，是我們剛好有一頁的內容是已知的：目次頁。
    """

    TITLES = ["第一　教派ではない", "第二　起源", "第三　現状", "第四　教會に對する抗議"]

    def test_real_toc_page_passes(self):
        ocr = "目次 第一　教派ではない…一 第二　起源…二 第三　現状…四 第四　教會に對する抗議…六"
        assert nb.toc_match_ratio(ocr, self.TITLES) == 1.0

    def test_hallucinated_toc_is_caught(self):
        """實際踩到的那次：OCR 吐出一份完全不存在的目次。"""
        ocr = ("目次 第一　無教會主義の本質…一 第二　信仰的基礎としての無教會主義…三〇 "
               "第三　無教會主義の組織法…五九")
        assert nb.toc_match_ratio(ocr, self.TITLES) == 0.0

    def test_partial_match_is_measured(self):
        ocr = "第一　教派ではない と 第二　起源 だけ読めた"
        assert nb.toc_match_ratio(ocr, self.TITLES) == 0.5

    def test_whitespace_and_dot_leaders_ignored(self):
        """目次的點線與空白不該影響比對。"""
        ocr = "第一 教派ではない......一\n第二 起源...二\n第三 現状...四\n第四 教會に對する抗議...六"
        assert nb.toc_match_ratio(ocr, self.TITLES) == 1.0

    def test_no_titles_is_not_a_pass(self):
        assert nb.toc_match_ratio("なんらかの文章", []) == 0.0


class TestQuotaClassifier:
    """🚨 兩次連續 429 就退（[[feedback_ocr_two_strike_quota]]）這條規矩的本意是
    「池子乾了就別再捶」，不是「試兩把就放棄」。本機有 7 把 key，舊寫法在第二把
    429 時就 raise，另外 5 把從沒試過 —— 這個 bug 讓我誤判成「今天沒額度了」，
    白繞一大圈去試 Haiku。**要全部試完才算乾**。
    """

    def test_429_is_quota(self):
        assert nb.is_quota_error("429 RESOURCE_EXHAUSTED") is True

    def test_resource_exhausted_is_quota(self):
        assert nb.is_quota_error("RESOURCE_EXHAUSTED: quota") is True

    def test_quota_word_is_quota(self):
        assert nb.is_quota_error("You exceeded your current Quota") is True

    def test_503_is_not_quota(self):
        assert nb.is_quota_error("503 UNAVAILABLE") is False

    def test_auth_error_is_not_quota(self):
        assert nb.is_quota_error("401 unauthorized") is False
