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


class TestTocCanaryVariants:
    """canary 比對前要先正規化異體字，否則會低估好的 OCR。

    實測：Gemini 把 9 個章名全讀對了，canary 卻只給 56%——因為書上印的是
    「敎」「現狀」，NDL 索引寫的是「教」「現状」。這種差異不是 OCR 錯，
    真要說 OCR 還更貼近原書。canary 太嚴會讓人誤以為要重跑。
    """

    def test_kyou_variant_matches(self):
        assert nb.toc_match_ratio("第六　聖書的基督敎の提唱", ["第六　聖書的基督教の提唱"]) == 1.0

    def test_jou_variant_matches(self):
        assert nb.toc_match_ratio("第三　現狀", ["第三　現状"]) == 1.0

    def test_genuine_dropped_character_still_fails(self):
        """「起源」被讀成「源」是真的漏字，不可以被正規化蓋掉。"""
        assert nb.toc_match_ratio("第二　源", ["第二　起源"]) == 0.0


class TestStripBeforeHeading:
    """一節的第一張影像常常還印著別的東西（目次、前一章結尾、書名頁），
    整張的 OCR 直接當內文的話，目次會整份被吞進第一章。

    規則：正文從**該節自己的章名之後**開始。
    """

    def test_toc_before_the_heading_is_dropped(self):
        text = "目次第一 教派ではない …… 一第二 起源 …… 二第一 教派ではない近頃「無教會主義」と"
        out = nb.strip_before_heading(text, "第一　教派ではない")
        assert out == "近頃「無教會主義」と"

    def test_uses_the_last_occurrence(self):
        """章名在目次裡也會出現一次，要取**最後**一次（真正的章首）。"""
        text = "目次 第三 現状 …… 三 本文開始前 第三 現状 これが本文"
        assert nb.strip_before_heading(text, "第三　現状") == "これが本文"

    def test_heading_absent_leaves_text_untouched(self):
        text = "章名が読み取れなかったページ"
        assert nb.strip_before_heading(text, "第九　無教會主義の傳道法") == text

    def test_variant_characters_still_match(self):
        text = "第六 聖書的基督敎の提唱 本文はここから"
        assert nb.strip_before_heading(text, "第六　聖書的基督教の提唱") == "本文はここから"

    def test_does_not_eat_the_whole_page(self):
        """章名出現在頁尾（下一章從這頁最後開始）時，不可以把整頁清空。"""
        text = "前の章の終わりの文章がここにある。第二　起源"
        assert nb.strip_before_heading(text, "第二　起源") == text


class TestBuildDoesNotEatTranslations:
    """`ndl_data/{slug}/secN.json` 同時是 ndl_build 的產出與翻譯的 checkpoint：
    `src` 由 ndl_build 寫、`zh` 由 uchimura_auto 填。所以修完 OCR 再 build 一次，
    會把已經翻好的 zh 整批清成 []。翻到一半才發現 OCR 有錯時最容易踩。
    """

    def test_existing_translation_blocks_rebuild(self):
        assert nb.has_translations([{"src": ["a"], "zh": ["甲"]}]) is True

    def test_empty_zh_does_not_block(self):
        assert nb.has_translations([{"src": ["a"], "zh": []}]) is False

    def test_all_null_zh_does_not_block(self):
        assert nb.has_translations([{"src": ["a", "b"], "zh": [None, None]}]) is False

    def test_partial_translation_blocks(self):
        assert nb.has_translations([{"src": ["a", "b"], "zh": [None, "乙"]}]) is True


class TestMergeTranslations:
    """精修 OCR 之後重建：**只有被改到的段落**該失效重譯，其餘譯文留著。

    先前的作法是「有譯文就拒絕重建」，那只是擋住而已 —— 真要修 OCR 還是得
    整本重譯。改成逐段比對 src：一樣的沿用舊譯，不一樣的把 zh 設回 None。
    """

    def test_unchanged_paragraph_keeps_its_translation(self):
        old = {"src": ["甲", "乙"], "zh": ["A", "B"]}
        new = {"src": ["甲", "乙"], "zh": []}
        assert nb.merge_translations(new, old)["zh"] == ["A", "B"]

    def test_edited_paragraph_loses_its_translation(self):
        old = {"src": ["歡ばしい", "乙"], "zh": ["可喜", "B"]}
        new = {"src": ["歎かはしい", "乙"], "zh": []}
        assert nb.merge_translations(new, old)["zh"] == [None, "B"]

    def test_inserted_paragraph_gets_none(self):
        old = {"src": ["甲"], "zh": ["A"]}
        new = {"src": ["新", "甲"], "zh": []}
        assert nb.merge_translations(new, old)["zh"] == [None, "A"]

    def test_deleted_paragraph_drops_its_translation(self):
        old = {"src": ["甲", "乙"], "zh": ["A", "B"]}
        new = {"src": ["乙"], "zh": []}
        assert nb.merge_translations(new, old)["zh"] == ["B"]

    def test_no_old_file_is_all_untranslated(self):
        new = {"src": ["甲", "乙"], "zh": []}
        assert nb.merge_translations(new, {})["zh"] == [None, None]

    def test_duplicate_source_paragraphs_do_not_cross_wire(self):
        """同樣的原文出現兩次時，兩邊各自對到自己的譯文，不可以互相串。"""
        old = {"src": ["同", "同"], "zh": ["一", "二"]}
        new = {"src": ["同", "同"], "zh": []}
        assert nb.merge_translations(new, old)["zh"] == ["一", "二"]


class TestOldFormRestore:
    """1934 年的書全是舊字體 —— 新字體是 1946 年才有的。
    所以 OCR 吐出來的任何新字體都是錯，這一整類可以確定性修掉，不必逐字看圖。

    🚨 只收**一對一**的字。像「弁」對應辨／瓣／辯三個舊字，靠字形無法判斷，
    收進來只會製造新的錯 —— 這張表寧可漏也不可錯。
    """

    def test_restores_old_forms(self):
        assert nb.restore_old_forms("斯様な言葉が出来て満足") == "斯樣な言葉が出來て滿足"

    def test_already_old_is_untouched(self):
        s = "斯樣な言葉が出來て滿足"
        assert nb.restore_old_forms(s) == s

    def test_kana_is_not_touched(self):
        """假名的新舊（加えて／加へて）要看語詞，不能靠字表換。"""
        s = "われらはすでに加えて"
        assert nb.restore_old_forms(s) == s

    def test_ambiguous_chars_are_excluded(self):
        """弁→辨/瓣/辯 三選一，不可自動換。"""
        assert "弁" not in nb.OLD_FORM_FIXES

    def test_mapping_is_one_to_one(self):
        vals = list(nb.OLD_FORM_FIXES.values())
        assert len(vals) == len(set(vals))
        assert all(len(k) == 1 and len(v) == 1 for k, v in nb.OLD_FORM_FIXES.items())


class TestFillPlaceholders:
    """NDL 官方 OCR 的字句遠比視覺模型準，但它把字集裡沒有的舊字體印成「〓」
    （本書 397 處：無〓會＝教、聖書之〓究＝研）。兩邊剛好互補：
    NDL 給正確的字句，Gemini 給它編不出的字形。逐字對齊後把 〓 填回去。
    """

    def test_fills_from_reference(self):
        out = nb.fill_placeholders("無〓會主義", "無敎會主義")
        assert out == "無敎會主義"

    def test_fills_different_characters_by_position(self):
        """〓 不是固定同一個字，要照位置各填各的。"""
        out = nb.fill_placeholders("〓派と聖書之〓究", "敎派と聖書之硏究")
        assert out == "敎派と聖書之硏究"

    def test_leaves_placeholder_when_reference_disagrees_in_length(self):
        """對不齊就留著 〓 —— 寧可留記號也不要填錯字。"""
        out = nb.fill_placeholders("無〓會主義", "まつたく違ふ文章")
        assert "〓" in out

    def test_does_not_touch_other_text(self):
        out = nb.fill_placeholders("これは正しい文である", "これは正しい文である")
        assert out == "これは正しい文である"

    def test_reference_missing_is_safe(self):
        assert nb.fill_placeholders("無〓會主義", "") == "無〓會主義"

    def test_never_fills_with_a_placeholder(self):
        """參照本身也是 〓 的話不能填。"""
        assert nb.fill_placeholders("無〓會", "無〓會") == "無〓會"


def _line(order, y, h=1760, s="本文です", t="本文", x=2000):
    return {"order": order, "x": x, "y": y, "height": h, "type": t, "string": s}


class TestLayoutParagraphs:
    """NDL layouttext XML → 段落。

    直排書的段落線索有兩個：**首行縮排**（Y 比同段其他行大一個字）與
    **段末行較短**（HEIGHT 明顯不足一欄）。NDL 給的是行不是段，
    不還原段落的話整頁會變成一大段，reader 讀起來是一堵牆。
    """

    def test_indented_line_starts_a_new_paragraph(self):
        # 🚨 只有段落**第一行**縮排，續行回到欄頂 —— 不是整段都低一格
        lines = [_line(0, 504), _line(1, 506), _line(2, 505),
                 _line(3, 549), _line(4, 505)]
        out = nb.lines_to_layout_paras(lines)
        assert len(out) == 2
        assert out[0].count("本文です") == 3

    def test_no_indent_stays_one_paragraph(self):
        lines = [_line(0, 504), _line(1, 506), _line(2, 505)]
        assert len(nb.lines_to_layout_paras(lines)) == 1

    def test_lines_are_ordered_by_order_not_input_sequence(self):
        lines = [_line(2, 505, s="丙"), _line(0, 504, s="甲"), _line(1, 506, s="乙")]
        assert nb.lines_to_layout_paras(lines) == ["甲乙丙"]

    def test_non_body_lines_are_dropped(self):
        """柱（書名／章名的重複）與ノンブル不是正文。"""
        lines = [_line(0, 504, s="正文"), _line(1, 505, s="二", t="ノンブル"),
                 _line(2, 506, s="つづき")]
        assert nb.lines_to_layout_paras(lines) == ["正文つづき"]

    def test_title_lines_are_dropped_from_body(self):
        """章名另有權威來源（NDL 目次 API），版面上這一行常常還是亂序的
        （實例：『第二　起源』被讀成『第二 源 起』），不要放進正文。"""
        lines = [_line(0, 504, s="前の章の終り"),
                 _line(1, 505, s="第二 源 起", t="タイトル本文"),
                 _line(2, 506, s="次の章の始め")]
        assert nb.lines_to_layout_paras(lines) == ["前の章の終り", "次の章の始め"]

    def test_spaces_inside_a_line_are_removed(self):
        """NDL 在標點後插空白（『である。 われらは』），中日文不需要。"""
        lines = [_line(0, 504, s="である。 われらは、 さう思ふ")]
        assert nb.lines_to_layout_paras(lines) == ["である。われらは、さう思ふ"]

    def test_empty_input(self):
        assert nb.lines_to_layout_paras([]) == []


class TestParseLayoutXml:
    XML = b"""<OCRDATASET>
  <PAGE IMAGENAME="1099766_R0000004.jp2" WIDTH="3575" HEIGHT="2787">
    <TEXTBLOCK CONF="0.944">
      <LINE TYPE="\xe6\x9c\xac\xe6\x96\x87" X="2994" Y="504" WIDTH="79" HEIGHT="1756" ORDER="0" STRING="\xe7\x94\xb2" />
      <LINE TYPE="\xe6\x9c\xac\xe6\x96\x87" X="2927" Y="549" WIDTH="76" HEIGHT="1765" ORDER="1" STRING="\xe4\xb9\x99" />
    </TEXTBLOCK>
  </PAGE>
</OCRDATASET>"""

    def test_extracts_lines_with_geometry(self):
        lines = nb.parse_layout_xml(self.XML)
        assert len(lines) == 2
        a = lines[0]
        assert a["order"] == 0 and a["x"] == 2994 and a["y"] == 504
        assert a["type"] == "本文" and a["string"] == "甲"

    def test_feeds_straight_into_paragraph_grouping(self):
        paras = nb.lines_to_layout_paras(nb.parse_layout_xml(self.XML))
        assert paras == ["甲", "乙"]     # 第二行縮排 → 另起一段

    def test_missing_attributes_do_not_crash(self):
        xml = b'<OCRDATASET><PAGE><TEXTBLOCK><LINE STRING="x" /></TEXTBLOCK></PAGE></OCRDATASET>'
        assert nb.parse_layout_xml(xml) == []
