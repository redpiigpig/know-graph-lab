"""Denzinger 分段器純函式測試。

segment_denzinger.py 在 import 時會載入 ocr_with_gemini（讀 SUPABASE_URL 等
環境變數）與 requests，conftest.py 已先放好假環境變數，所有網路/DB 呼叫都在
函式內部，因此純啟發式（語言分類、DH 標記判定、分塊、TOC 偵測、整頁分段）可
直接 import 並執行，不碰網路、DB、檔案系統。
"""
import segment_denzinger as sd


# ── classify_lang / cjk_ratio — 拉丁 / 中文 / 混合 判定 ─────────────────
class TestClassifyLang:
    def test_pure_latin_is_lat(self):
        assert sd.classify_lang("Credo in unum Deum patrem omnipotentem") == "lat"

    def test_pure_chinese_is_zh(self):
        assert sd.classify_lang("我信獨一上帝聖父全能者創造天地萬物的主宰") == "zh"

    def test_mixed_is_mixed(self):
        # CJK 佔比落在 0.1 ~ 0.4 中間帶 → mixed。
        assert sd.classify_lang("Credo Deum 我信獨一上帝全能 patrem") == "mixed"

    def test_empty_is_lat(self):
        # 空字串 cjk_ratio=0.0 < 0.1 → lat（current behaviour）
        assert sd.classify_lang("") == "lat"


# ── is_valid_dh — DH 1-99 只在第一部分信經（page < 115）且須拉/希臘大寫開頭 ──
class TestIsValidDh:
    def test_low_dh_without_page_rejected(self):
        # pn=None 時，低號 DH 無法定位在信經頁，必須拒絕。
        assert sd.is_valid_dh(50, None, "Credo") is False

    def test_low_dh_in_creed_pages_with_latin_start_accepted(self):
        assert sd.is_valid_dh(50, 80, "Credo in unum Deum") is True

    def test_low_dh_with_chinese_start_rejected(self):
        # 信經頁的低號 DH 後面接中文 → 是行內交叉引用，不是真正條目開頭。
        assert sd.is_valid_dh(50, 80, "我信獨一上帝") is False

    def test_low_dh_past_creed_pages_rejected(self):
        assert sd.is_valid_dh(50, 300, "Credo") is False

    def test_high_dh_always_valid(self):
        # >=100 不受頁碼/開頭字限制。
        assert sd.is_valid_dh(500, 300, "") is True
        assert sd.is_valid_dh(500, None, "我信") is True


# ── split_into_blocks — 逐行掃描，DH 行起新塊，前置行成 preamble ───────────
class TestSplitIntoBlocks:
    def test_preamble_then_two_dh_blocks(self):
        text = "preamble line\n500 Credo in unum\nmore latin\n501 Iesum Christum"
        blocks = sd.split_into_blocks(text, pn=80)
        kinds = [b["kind"] for b in blocks]
        assert kinds == ["preamble", "dh", "dh"]
        assert blocks[1]["dh_number"] == 500
        # DH 塊內含後續非 DH 行（more latin 歸給 DH 500）。
        assert "more latin" in blocks[1]["text"]
        assert blocks[2]["dh_number"] == 501

    def test_blocks_carry_lang_label(self):
        blocks = sd.split_into_blocks("500 Credo in unum Deum patrem", pn=80)
        assert blocks[0]["kind"] == "dh"
        assert blocks[0]["lang"] == "lat"

    def test_empty_page_yields_no_blocks(self):
        assert sd.split_into_blocks("", pn=80) == []


# ── is_toc_page — 詳細目錄 標頭，或 >20% 行帶點引線 ──────────────────────
class TestIsTocPage:
    def test_explicit_header(self):
        assert sd.is_toc_page("詳細目錄\n第一章 ...... 5") is True

    def test_dot_leaders_majority(self):
        toc = "\n".join(f"第{i}章 ..........{i}" for i in range(1, 11))
        assert sd.is_toc_page(toc) is True

    def test_real_latin_page_not_toc(self):
        assert sd.is_toc_page("Credo in unum Deum patrem omnipotentem") is False

    def test_recolumn_zh_block_header(self):
        content = f"{sd.LAT_DIVIDER}\nfoo\n{sd.ZH_DIVIDER}\n目錄\n第一章"
        assert sd.is_toc_page(content) is True


# ── is_section_header — 章節標題模式 ───────────────────────────────────
class TestIsSectionHeader:
    def test_council_header_matches(self):
        assert sd.is_section_header("尼西亞大公會議") == "大公會議"

    def test_plain_line_no_header(self):
        assert sd.is_section_header("這只是一句普通的話") is None


# ── looks_like_toc_entry — 點引線 或 單行短中文 ────────────────────────
class TestLooksLikeTocEntry:
    def test_dot_leader_entry(self):
        assert sd.looks_like_toc_entry("第一章 .......... 5") is True

    def test_short_single_line_zh_entry(self):
        assert sd.looks_like_toc_entry("短中文行") is True

    def test_long_latin_not_toc_entry(self):
        assert sd.looks_like_toc_entry(
            "Credo in unum Deum patrem omnipotentem factorem caeli"
        ) is False


# ── segment_page — 整頁 → 分類子塊（happy path + 邊界）─────────────────
class TestSegmentPage:
    def test_toc_page_emits_single_header(self):
        out = sd.segment_page({"page_number": 10, "content": "詳細目錄\n第一章 ...... 5"})
        assert len(out) == 1
        assert out[0]["section_type"] == "header"
        assert out[0]["chapter_path"] == "詳細目錄"

    def test_plain_entry_page_emits_entries_per_dh(self):
        page = {
            "page_number": 80,
            "content": "500 Credo in unum Deum patrem\n501 Iesum Christum filium",
        }
        out = sd.segment_page(page)
        assert [c["chapter_path"] for c in out] == ["DH 500", "DH 501"]
        assert all(c["section_type"] == "entry" for c in out)
        assert all(c["dh_number"] in (500, 501) for c in out)

    def test_divider_page_pairs_latin_and_chinese_by_dh(self):
        # 中譯欄無 DH 號，靠空行分段後與左欄拉丁 DH 1:1 對齊；中文段需 >30 字才
        # 不被 looks_like_toc_entry 當成 TOC 殘行濾掉。
        zh1 = "我信獨一的上帝就是全能的父創造天地和一切有形無形萬物的主宰阿們"
        zh2 = "我信獨一的主耶穌基督上帝的獨生子在萬世以前為父所生是神出於神光出於光"
        content = (
            f"{sd.LAT_DIVIDER}\n"
            "500 Credo in unum Deum patrem omnipotentem\n"
            "501 Iesum Christum filium Dei unigenitum\n"
            f"{sd.ZH_DIVIDER}\n{zh1}\n\n{zh2}"
        )
        out = sd.segment_page({"page_number": 80, "content": content})
        assert [c["dh_number"] for c in out] == [500, 501]
        assert out[0]["content"] == zh1
        assert out[0]["source_text"] == "Credo in unum Deum patrem omnipotentem"
        assert out[0]["source_lang"] == "lat"


# ── consolidate_across_pages — 跨頁合併 + chunk_index 重編 ─────────────
class TestConsolidateAcrossPages:
    def test_same_dh_entry_spilled_across_pages_merged(self):
        page1 = [{
            "section_type": "entry", "chunk_type": "section", "chapter_path": "DH 500",
            "content": "前半", "source_text": "Credo", "source_lang": "lat",
            "dh_number": 500, "page_number": 80, "page_numbers": [80],
        }]
        page2 = [{
            "section_type": "entry", "chunk_type": "section", "chapter_path": "DH 500",
            "content": "後半", "source_text": "Deum", "source_lang": "lat",
            "dh_number": 500, "page_number": 81, "page_numbers": [81],
        }]
        flat = sd.consolidate_across_pages([page1, page2])
        assert len(flat) == 1
        assert flat[0]["content"] == "前半\n後半"
        assert flat[0]["page_numbers"] == [80, 81]
        assert flat[0]["chunk_index"] == 0

    def test_entry_then_commentary_folds_with_sentinel(self):
        per_page = [[
            {"section_type": "entry", "chunk_type": "section", "chapter_path": "DH 11",
             "content": "正文", "dh_number": 11, "page_number": 80, "page_numbers": [80]},
            {"section_type": "commentary", "chunk_type": "section", "chapter_path": "註解",
             "content": "這是一段相當長的中文註解內容說明本條目的背景", "page_number": 80,
             "page_numbers": [80]},
        ]]
        flat = sd.consolidate_across_pages(per_page)
        assert len(flat) == 1
        assert "<<COMMENTARY>>" in flat[0]["content"]
        assert flat[0]["content"].startswith("正文")
