"""Translation quality auto-fix — sweep_book_quality.

These pure fixers run after consolidation to repair the LLM-quality bugs the
structural pipeline can't catch: T1 heading-bleed (title swallowed the first
body sentence), T2 first-h3 vs volume drift, T3 straight→CJK quotes. They are
the auto-fix half of the transcription/translation quality gate.
"""
import sweep_book_quality as sw


class TestFindBleedSplit:
    def test_clean_short_title_not_split(self):
        # ≤25 chars and closes with 」/。→ a real descriptive title.
        assert sw.find_bleed_split("第一章—書信寫作的契機。") is None

    def test_body_marker_bleed_split(self):
        # 「既然」starts a new clause that bled into the title.
        res = sw.find_bleed_split("第一章—書信寫作的契機既然我看到你最為卓越的")
        assert res is not None
        title, body = res
        assert title == "第一章—書信寫作的契機"
        assert body.startswith("既然")

    def test_non_chapter_heading_returns_none(self):
        # No 「第X章—」prefix → not a recognised bleed shape.
        assert sw.find_bleed_split("一段普通的標題文字") is None


class TestSweepT1:
    def test_bleed_moved_to_following_paragraph(self):
        content = (
            "#### 第一章—書信寫作的契機既然我看到你\n\n"
            "，最為卓越的狄奧格尼圖，極其渴慕要學習。"
        )
        out, fixes = sw.sweep_t1(content)
        assert fixes == 1
        assert "#### 第一章—書信寫作的契機\n" in out
        assert "既然我看到你" in out
        # The heading line itself no longer carries the bled sentence.
        heading_line = out.splitlines()[0]
        assert "既然" not in heading_line

    def test_clean_content_untouched(self):
        content = "#### 第一章—書信寫作的契機\n\n既然我看到你。"
        out, fixes = sw.sweep_t1(content)
        assert fixes == 0
        assert out == content


class TestSweepT3:
    def test_straight_double_quotes_toggle_to_corner_brackets(self):
        content = '他說 "你好" 然後離開。'
        out, n, ok = sw.sweep_t3(content)
        assert ok is True
        assert "「你好」" in out
        assert '"' not in out
        assert n == 2

    def test_odd_quote_count_flagged_not_ok(self):
        content = '他說 "你好 然後離開。'
        out, n, ok = sw.sweep_t3(content)
        assert ok is False  # unbalanced — caller should report

    def test_no_quotes_no_change(self):
        content = "沒有任何引號的文字。"
        out, n, ok = sw.sweep_t3(content)
        assert n == 0 and ok is True and out == content


class TestSweepT2:
    def test_first_h3_renamed_to_volume(self):
        content = "### 致狄奧格尼圖書\n\n正文。"
        out, n = sw.sweep_t2(content, volume="致丟格那妥書")
        assert n == 1
        assert "### 致丟格那妥書" in out

    def test_matching_h3_left_alone(self):
        content = "### 致丟格那妥書\n\n正文。"
        out, n = sw.sweep_t2(content, volume="致丟格那妥書")
        assert n == 0

    def test_multiple_h3s_skipped(self):
        # Cross-work bleed — needs a chunk split, not a rename.
        content = "### 第一封\n\n正文一。\n\n### 第二封\n\n正文二。"
        out, n = sw.sweep_t2(content, volume="某卷")
        assert n == 0

    def test_late_positioned_h3_skipped(self):
        # h3 past 30% of content = next-letter intro; renaming would corrupt.
        body = "正文" * 200
        content = f"{body}\n\n### 下一封信的標題\n\n更多內文"
        out, n = sw.sweep_t2(content, volume="本卷")
        assert n == 0
