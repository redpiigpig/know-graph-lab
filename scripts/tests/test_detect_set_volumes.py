"""套書卷邊界偵測純函式測試。

detect_set_volumes.py 在 import 時會載入 anthropic、standardize_ebook、
standardize_pdf_lite、split_ebook_set 等模組，這些都靠 conftest.py 的假環境變數
（SUPABASE_URL 等）成功 import；所有 LLM / 網路 / R2 呼叫都在函式內部。本檔只測
不碰外部資源的純函式：get_first_heading / build_toc / rewrite_chunks_with_volume。
"""
import detect_set_volumes as dsv


# ── get_first_heading — 取 chunk 首個 markdown 標題 (level, text) ──────
class TestGetFirstHeading:
    def test_h2_heading(self):
        assert dsv.get_first_heading("## 第一卷 局外人\n內文") == (2, "第一卷 局外人")

    def test_h4_heading_level(self):
        assert dsv.get_first_heading("#### 小節\n內文") == (4, "小節")

    def test_no_heading_returns_none(self):
        assert dsv.get_first_heading("沒有標題的一段內文") is None

    def test_empty_returns_none(self):
        assert dsv.get_first_heading("") is None


# ── build_toc — 過濾前置內容/章節/過深/過長標題後的候選卷標題 ───────────
class TestBuildToc:
    def test_keeps_volume_titles_drops_frontmatter_and_deep(self):
        chunks = [
            {"content": "## 封面"},                  # 前置內容 → 濾掉
            {"content": "## 局外人（1942年）\n正文"},   # 卷
            {"content": "## 鼠疫（1947年）\n正文"},     # 卷
            {"content": "#### 太深\n小節"},           # level>3 → 濾掉
        ]
        toc = dsv.build_toc(chunks)
        # 回傳 (chunk_index, level, clean_title)
        texts = [t[2] for t in toc]
        assert "封面" not in texts
        assert "太深" not in texts
        assert "局外人（1942年）" in texts
        assert "鼠疫（1947年）" in texts
        # chunk_index 為枚舉索引，需保留原位置
        assert toc[0][0] == 1

    def test_arabic_digit_chapter_filtered_as_non_volume(self):
        # NON_VOLUME_HEADING_RX 用阿拉伯數字章 (第1章) 判定章節，過濾不當成卷。
        chunks = [
            {"content": "## 卷一\n正文"},
            {"content": "## 第1章\n章內容"},
            {"content": "## 卷二\n正文"},
        ]
        texts = [t[2] for t in dsv.build_toc(chunks)]
        assert texts == ["卷一", "卷二"]

    def test_cjk_numeral_chapter_filtered_as_non_volume(self):
        # 中文數字章 (第一章) 也要過濾——與阿拉伯數字章一致（2026-06-04 修補）。
        chunks = [
            {"content": "## 卷一\n正文"},
            {"content": "## 第一章\n章內容"},
            {"content": "## 第十二章\n章內容"},
            {"content": "## 卷二\n正文"},
        ]
        texts = [t[2] for t in dsv.build_toc(chunks)]
        assert texts == ["卷一", "卷二"]

    def test_long_title_skipped(self):
        # >60 字標題視為內文片段，非標題。
        assert dsv.build_toc([{"content": "## " + "字" * 70}]) == []

    def test_footnote_marker_skipped(self):
        assert dsv.build_toc([{"content": "## [12]\n註腳內容"}]) == []


# ── rewrite_chunks_with_volume — 依邊界 chunk_index 把卷名灌到各 chunk ──
class TestRewriteChunksWithVolume:
    def test_propagates_volume_per_boundary(self):
        chunks = [{"content": "a"}, {"content": "b"}, {"content": "c"}, {"content": "d"}]
        volumes = [
            {"chunk_index": 1, "volume_title": "局外人"},
            {"chunk_index": 3, "volume_title": "鼠疫"},
        ]
        out = dsv.rewrite_chunks_with_volume(chunks, volumes)
        # 邊界前 → None；邊界後沿用該卷名。
        assert [c["volume"] for c in out] == [None, "局外人", "局外人", "鼠疫"]

    def test_unsorted_boundaries_handled(self):
        # 邊界亂序傳入，內部會 sort by chunk_index。
        chunks = [{"content": str(i)} for i in range(4)]
        volumes = [
            {"chunk_index": 3, "volume_title": "鼠疫"},
            {"chunk_index": 1, "volume_title": "局外人"},
        ]
        out = dsv.rewrite_chunks_with_volume(chunks, volumes)
        assert [c["volume"] for c in out] == [None, "局外人", "局外人", "鼠疫"]

    def test_no_volumes_returns_chunks_unchanged(self):
        chunks = [{"content": "a"}]
        assert dsv.rewrite_chunks_with_volume(chunks, []) is chunks
