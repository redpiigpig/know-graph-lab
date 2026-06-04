"""翻譯後潤飾 — polish_translated_book 的純函式。

translate_ebook_to_zh 的輸出常有兩個結構性 bug：
  1. 過長 chapter_path — LLM 把「#### 標題」和首段內文塞在同一行，標題吞掉整段。
     clean_chapter_path 在合理邊界（句號／逗號／body-starter 片語／硬上限）切回標題。
  2. 缺父作品分組 — detect_volume 從 source_text 的 H3 標題對應到中文卷名。
這兩個都是純文字啟發式，無網路／DB。
"""
import polish_translated_book as pl


class TestCleanChapterPath:
    def test_short_title_kept_as_is(self):
        # 已夠短 → 原樣不動，未截斷。
        out, trunc = pl.clean_chapter_path("第一章 緒論")
        assert out == "第一章 緒論"
        assert trunc is False

    def test_frontmatter_word_truncates_to_heading_word(self):
        # 「前言」後面接著內文，截到只剩「前言」。
        out, trunc = pl.clean_chapter_path("前言本卷所收錄的內容等同於愛丁堡系列")
        assert out == "前言"
        assert trunc is True

    def test_mashed_chapter_subtitle_cut_at_period(self):
        # 「第N章——副標。內文…」在句號處截斷，保留章前綴 + 副標。
        raw = "第三章——論信德的根基。既然我看到你最為卓越的狄奧格尼圖極其渴慕要學習真道"
        out, trunc = pl.clean_chapter_path(raw)
        assert trunc is True
        assert out.startswith("第三章")
        assert "論信德的根基" in out
        assert "既然" not in out

    def test_body_starter_phrase_cuts_overlong_subtitle(self):
        # 沒有句號，但有 body-starter「因此，」→ 在該處切。
        raw = "第二章——基督的恩典因此，我們應當持守所領受的道理直到末了不可動搖"
        out, trunc = pl.clean_chapter_path(raw)
        assert trunc is True
        assert out.startswith("第二章")
        assert "因此" not in out

    def test_no_prefix_overlong_cut_at_hard_cap(self):
        # 無章前綴、無句號、非 front-matter → 砍到 FRONTMATTER_CAP。
        raw = "一段沒有任何章節前綴也沒有句號的超長標題文字一直延伸下去而且還停不下來繼續寫了很多很多字超過上限"
        out, trunc = pl.clean_chapter_path(raw)
        assert trunc is True
        assert len(out) <= pl.FRONTMATTER_CAP


class TestDetectVolume:
    def test_h3_direct_match_returns_chinese_volume(self):
        src = "### First Epistle of Clement\n\nThe Church of God which sojourns..."
        assert pl.detect_volume(src) == "革利免致哥林多人前書"

    def test_the_prefix_stripped_before_match(self):
        # 「The Shepherd of Hermas」要先去掉 The 再比對。
        src = "### The Shepherd of Hermas\n\nThe vision which I saw..."
        assert pl.detect_volume(src) == "黑馬牧者書"

    def test_introductory_note_resolves_to_parent_work(self):
        # 「Introductory Note to X」要解析出 X 的卷名。
        src = "### Introductory Note to the Epistle of Barnabas\n\nThe writer..."
        assert pl.detect_volume(src) == "巴拿巴書信"

    def test_no_h3_returns_none(self):
        assert pl.detect_volume("just some plain body text, no markdown heading") is None

    def test_unknown_h3_returns_none(self):
        src = "### Some Totally Unknown Work Title\n\nbody"
        assert pl.detect_volume(src) is None

    def test_empty_source_returns_none(self):
        assert pl.detect_volume("") is None
        assert pl.detect_volume(None) is None
