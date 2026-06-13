"""shengyen_build 純解析函式測試（零 network/DB）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import shengyen_build as sb  # noqa: E402

# 仿 ddc.shengyen.org/html/{doc}.html：pb 頁碼 span + lb 空行碼 span + p.h2 標題 + p.indent 正文。
CONTENT = """<div>
  <span id="313" data-page="313" data-vol="03-05" class="pb"></span><span class="lb"></span>
  <div type="article" class="article" id="div_96">
    <span class="lb"></span><p class="h2">《聖嚴法師心靈環保》自序</p>
    <p class="indent"><span class="lb"></span>近年來，由於臺灣社會處於轉型期間，發展成<span class="lb"></span>多樣化的人間現象。</p>
    <p class="indent"><span class="lb"></span>其實，自從釋迦牟尼世尊在人間出現。</p>
    <p class="byline">聖嚴</p>
  </div>
</div>"""

# 仿 tree_menu/toc.html 巢狀：書 > 下篇 自序 > 篇。
TOC = """<ul>
 <li><a html_file="03-05-001.html">他序篇一</a></li>
 <li><a href="#">下篇　自序</a>
   <ul>
     <li><a html_file="03-05-096.html">《聖嚴法師心靈環保》自序</a></li>
   </ul>
 </li>
</ul>"""


def test_parse_content_extracts_page_number():
    ch = sb.parse_content_html(CONTENT, book_title="書序", toc_path=["下篇　自序", "《聖嚴法師心靈環保》自序"])
    assert ch["page_number"] == 313


def test_lb_spans_stripped_text_continuous():
    ch = sb.parse_content_html(CONTENT, book_title="書序", toc_path=["《聖嚴法師心靈環保》自序"])
    assert "近年來，由於臺灣社會處於轉型期間，發展成多樣化的人間現象。" in ch["content"]


def test_heading_becomes_markdown():
    ch = sb.parse_content_html(CONTENT, book_title="書序", toc_path=["《聖嚴法師心靈環保》自序"])
    assert "### 《聖嚴法師心靈環保》自序" in ch["content"]  # h2 → ###（level+1）


def test_body_paragraphs_joined_blankline():
    ch = sb.parse_content_html(CONTENT, book_title="書序", toc_path=["序"])
    # h2 + 兩段 indent + byline = 4 塊 → 3 個空行分隔
    assert ch["content"].count("\n\n") == 3


def test_chapter_path_book_plus_toc():
    ch = sb.parse_content_html(CONTENT, book_title="書序",
                               toc_path=["下篇　自序", "《聖嚴法師心靈環保》自序"])
    assert ch["chapter_path"] == "書序 · 下篇　自序 · 《聖嚴法師心靈環保》自序"


def test_empty_content_returns_none():
    assert sb.parse_content_html("<div><p class='indent'>  </p></div>",
                                 book_title="x", toc_path=["x"]) is None


def test_no_sources_field_single_language():
    ch = sb.parse_content_html(CONTENT, book_title="書序", toc_path=["序"])
    assert "sources" not in ch and "source_text" not in ch


def test_build_chapter_paths_nesting():
    paths = sb.build_chapter_paths(TOC)
    assert paths["03-05-096.html"] == ["下篇　自序", "《聖嚴法師心靈環保》自序"]
    assert paths["03-05-001.html"] == ["他序篇一"]


def test_clean_preserves_fullwidth_space():
    assert sb._clean("下篇　自序\n  ") == "下篇　自序"
