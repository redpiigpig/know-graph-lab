"""Transcription — EPUB body extraction (HTML → markdown).

el_to_md / html_to_markdown decide how the source body becomes reader
markdown. Wrong mappings here corrupt 正文 (headings flatten, footnote refs
vanish, decorative svg/img leak in). Asserts the contract documented in the
ebook-pipeline SKILL: h1→##, h2→###, h3/h4→####, b→**, em→*, blockquote→>,
<sup>(N)</sup>→[^N], decorative tags stripped.
"""
import standardize_ebook as se


def md_of(html: str) -> str:
    md, _plain = se.html_to_markdown(html.encode("utf-8"))
    return md


class TestHeadingLevels:
    def test_h1_to_h2(self):
        assert md_of("<h1>標題</h1>") == "## 標題"

    def test_h2_to_h3(self):
        assert md_of("<h2>小節</h2>") == "### 小節"

    def test_h3_and_h4_to_h4(self):
        assert md_of("<h3>子節</h3>") == "#### 子節"
        assert md_of("<h4>更深</h4>") == "#### 更深"


class TestInlineMarkup:
    def test_bold(self):
        assert "**重點**" in md_of("<p><b>重點</b></p>")
        assert "**x**" in md_of("<p><strong>x</strong></p>")

    def test_italic(self):
        assert "*書名*" in md_of("<p><em>書名</em></p>")
        assert "*y*" in md_of("<p><i>y</i></p>")

    def test_empty_bold_em_collapse(self):
        assert md_of("<p><b></b></p>") == ""


class TestBlockElements:
    def test_blockquote(self):
        assert md_of("<blockquote>引文一段</blockquote>") == "> 引文一段"

    def test_paragraph_whitespace_collapsed(self):
        assert md_of("<p>多   個     空白</p>") == "多 個 空白"

    def test_hr(self):
        assert md_of("<hr/>") == "---"


class TestFootnoteRefs:
    def test_sup_numeric_paren_to_pandoc_ref(self):
        assert md_of("<p>文字<sup>(5)</sup></p>") == "文字[^5]"

    def test_decorative_sup_dropped(self):
        # <sup>e</sup> (1559 版本 marker etc.) must NOT become a ref.
        assert md_of("<p>文字<sup>e</sup></p>") == "文字"

    def test_anchored_sup_ref_preserved(self):
        # EPUB back-link <a><sup>(7)</sup></a> keeps the ref number.
        assert md_of('<p>文字<a href="#fn7"><sup>(7)</sup></a></p>') == "文字[^7]"


class TestDecorativeStripping:
    def test_svg_and_img_removed(self):
        assert md_of('<p>前<svg><path/></svg><img src="x.png"/>後</p>') == "前後"

    def test_script_style_removed(self):
        assert md_of("<p>內文</p><script>bad()</script><style>.x{}</style>") == "內文"
