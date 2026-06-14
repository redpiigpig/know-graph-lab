"""hsingyun_build 純解析函式測試（零 network/DB）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hsingyun_build as hb  # noqa: E402

# 仿 /ArticleDetail/artcle{N}：breadcrumb 階層 + txtContent（<b>小標 + <br><br>分段）。
ART = """<html><body>
<ul class="breadcrumb">
  <li><a href="/">回首頁</a></li>
  <li>第八類【日記】 / </li>
  <li>279-280海天遊踪(共2冊) / </li>
  <li>280海天遊踪2：一九六三 / </li>
  <li>p008　新加坡：八月三日至八月十日</li>
</ul>
<div class="txtContent borStyleA">
    <p>
        <b>八月三日<br/><br/>華僑的世界</b><br/><br/>我們今天從馬來亞到新加坡。<br/><br/>新加坡只有一七○萬人口。
    </p>
</div>
</body></html>"""

# 索引頁（無 第N類）→ 應被 parse_article 視為 None。
INDEX = """<ul class="breadcrumb"><li>回首頁</li><li>大師全集</li>
<li>星雲大師全集十二大類的書目</li></ul><div class="txtContent">x</div>"""

REDIR = """<html><body>no breadcrumb here</body></html>"""


def test_parse_article_breadcrumb_excludes_home():
    r = hb.parse_article(ART)
    assert r["breadcrumb"][0].startswith("第八類")
    assert "回首頁" not in r["breadcrumb"]


def test_parse_article_paragraphs_split_on_br():
    r = hb.parse_article(ART)
    assert "我們今天從馬來亞到新加坡。" in r["paras"]
    assert "新加坡只有一七○萬人口。" in r["paras"]
    # 小標抓出
    assert r["heading"] and "華僑的世界" in r["heading"]


def test_parse_article_index_page_returns_none():
    assert hb.parse_article(INDEX) is None


def test_parse_article_redirect_returns_none():
    assert hb.parse_article(REDIR) is None


def test_classify_breadcrumb():
    items = ["第八類【日記】", "279-280海天遊踪(共2冊)", "280海天遊踪2：一九六三", "p008　新加坡"]
    c = hb.classify_breadcrumb(items)
    assert c["parent_volume"] == "第八類【日記】"
    assert c["book_key"] == "279-280海天遊踪(共2冊)"
    assert c["title"] == "p008　新加坡"
    assert c["chapter_parts"][0] == "279-280海天遊踪(共2冊)"


def test_clean_book_title_strips_number_and_count():
    assert hb.clean_book_title("279-280海天遊踪(共2冊)") == "海天遊踪"
    assert hb.clean_book_title("025佛法滿人間") == "佛法滿人間"
    assert hb.clean_book_title("004-005金剛經講話(共2冊)") == "金剛經講話"


def test_book_sort_key_numeric():
    assert hb.book_sort_key("004-005金剛經講話(共2冊)") < hb.book_sort_key("025佛法滿人間")


def test_group_books_merges_multivolume():
    arts = [
        {"n": 1, "breadcrumb": ["第八類【日記】", "279-280海天遊踪(共2冊)", "279海天遊踪1", "p001"], "paras": ["a"]},
        {"n": 2, "breadcrumb": ["第八類【日記】", "279-280海天遊踪(共2冊)", "280海天遊踪2", "p008"], "paras": ["b"]},
    ]
    books = hb.group_books(arts)
    assert len(books) == 1
    b = books["279-280海天遊踪(共2冊)"]
    assert b["title"] == "海天遊踪" and len(b["arts"]) == 2


def test_article_chunk_extracts_page_number():
    a = {"paras": ["x"], "_class": {"title": "p008　新加坡", "chapter_parts": ["279-280海天遊踪(共2冊)", "280海天遊踪2", "p008　新加坡"]}}
    ch = hb._article_chunk(a, 1, "海天遊踪", "第八類【日記】")
    assert ch["page_number"] == 8
    assert ch["volume"] == "海天遊踪"


def test_article_chunk_no_sources():
    a = {"paras": ["x"], "_class": {"title": "p1", "chapter_parts": ["b", "p1"]}}
    ch = hb._article_chunk(a, 1, "b", "第一類【經義】")
    assert "sources" not in ch
