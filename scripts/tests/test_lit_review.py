"""Test-first contract for scripts/lit_review.py.

Pure functions only — markdown / PDF-text / HTML fixtures are inline, no
network. Covers the /works 研究回顧 (literature-review) ingestion pipeline:

  - make_ref_key            stable url-safe key per bibliography entry
  - detect_language         語言 label (英文/中文/德文…) → ISO code
  - THEMES                  the report's 4 thematic section headers
  - parse_entry_block       one 【作者】（年）〈題〉… block → structured dict
  - parse_review_report     whole 文獻綜述 markdown → {summary, gaps, entries}
  - extract_paragraphs_*    fetched PDF-text / HTML full-text → paragraph list
  - align_ok / assert_aligned   the 1:1 中譯↔原文 per-paragraph gate

Mirrors scripts/tests/test_gnostic_library.py (the analogous /gnostic pipeline).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import lit_review as lr  # noqa: E402


# ── ref_key ─────────────────────────────────────────────────────────────────
def test_make_ref_key_for_english_author_is_readable_and_url_safe():
    k = lr.make_ref_key("【Anālayo】", 2016, "The Foundation History of the Nuns' Order")
    assert k.startswith("analayo-2016-the-foundation")
    assert k == k.lower()
    assert all(ch.isalnum() or ch == "-" for ch in k)
    assert "--" not in k and not k.startswith("-") and not k.endswith("-")
    assert "ā" not in k  # accents transliterated away (ā → a)


def test_make_ref_key_disambiguates_same_author_same_year_by_title():
    # Anālayo published THREE JBE articles in 2013 — keys must differ.
    a = lr.make_ref_key("【Anālayo】", 2013, "The Gurudharma on Bhikṣuṇī Ordination")
    b = lr.make_ref_key("【Anālayo】", 2013, "The Revival of the Bhikkhunī Order")
    c = lr.make_ref_key("【Anālayo】", 2013, "The Legality of Bhikkhunī Ordination")
    assert a != b != c and a != c


def test_make_ref_key_for_cjk_only_author_is_stable_and_url_safe():
    k1 = lr.make_ref_key("【林崇安】", 2013, "八敬法的演變")
    k2 = lr.make_ref_key("【林崇安】", 2013, "八敬法的演變")
    k3 = lr.make_ref_key("【釋惠敏】", 1999, "比丘尼受戒法與傳承之考察")
    assert k1 == k2                       # deterministic
    assert k1 != k3                       # distinct entries → distinct keys
    assert all(ch.isalnum() or ch == "-" for ch in k1)
    assert "2013" in k1 and "1999" in k3


def test_make_ref_key_without_year_still_valid():
    k = lr.make_ref_key("【吳一忠】", None, "從《摩奴法典》到「八敬法」")
    assert k and all(ch.isalnum() or ch == "-" for ch in k)


def test_make_ref_key_caps_length_at_word_boundary():
    long = ("The Validity of Bhikkhunī Ordination by Bhikkhus Only According to "
            "the Pāli Vinaya as Discussed at Great Length in the Commentaries")
    k = lr.make_ref_key("【Anālayo】", 2017, long)
    assert len(k) <= 100
    assert not k.endswith("-")


# ── language detection ────────────────────────────────────────────────────────
@pytest.mark.parametrize("label,code", [
    ("英文", "en"), ("中文", "zh"), ("德文", "de"),
    ("英文 ", "en"), ("法文", "fr"), ("日文", "ja"),
])
def test_detect_language(label, code):
    assert lr.detect_language(label) == code


def test_detect_language_unknown_falls_back_to_other():
    assert lr.detect_language("梵文") == "other"


# ── themes ────────────────────────────────────────────────────────────────────
def test_themes_cover_the_four_report_sections():
    labels = {t["label"] for t in lr.THEMES}
    assert {"文本考證與來源研究", "女性議題與比丘尼制度",
            "詮釋爭論與真偽問題", "跨傳統比較"} <= labels
    for t in lr.THEMES:
        assert t["key"] and isinstance(t["order"], int)


def test_doc_type_themes_cover_the_seven_bibliography_sections():
    # A paper's real 參考文獻 is grouped by document type, not by subject theme.
    labels = {t["label"] for t in lr.DOC_TYPE_THEMES}
    assert {"佛典與檔案", "專書著作", "期刊文章", "研討會與專書論文",
            "學位論文", "報刊與雜誌", "網路文章"} <= labels
    # the header families are disjoint and all feed SECTION_LABELS
    assert lr.THEME_LABELS.isdisjoint(lr.DOC_TYPE_LABELS)
    assert lr.SUPPLEMENT_LABELS.isdisjoint(lr.THEME_LABELS | lr.DOC_TYPE_LABELS)
    assert lr.SECTION_LABELS == lr.THEME_LABELS | lr.DOC_TYPE_LABELS | lr.SUPPLEMENT_LABELS


def test_parse_review_report_assigns_supplement_section_as_theme():
    md = """#某論文英文改寫補充

#性別與佛教理論框架（英文改寫補充）

【Alan Sponberg】（1992）〈Attitudes toward Women and the Feminine in Early Buddhism〉，《Buddhism, Sexuality, and Gender》。
語言：英文
摘要：提出佛教看待女性的「四種態度」類型學。
"""
    r = lr.parse_review_report(md)
    e = r["entries"][0]
    assert e["theme"] == "性別與佛教理論框架（英文改寫補充）"
    assert e["authors"] == "Alan Sponberg" and e["year"] == 1992


# ── one entry block ───────────────────────────────────────────────────────────
ENTRY_ARTICLE = """【Anālayo】（2015）〈The Cullavagga on Bhikkhunī Ordination〉，《Journal of Buddhist Ethics》，第 22 卷，頁 401–448。
語言：英文
所屬面向：文本考證 / 詮釋爭論
立場：主張八敬法非佛陀親制（或非完整佛制）
摘要：本文詳細分析《小品》（Cullavagga X）中比丘尼受戒的敘述，與漢譯各傳本逐條比對，揭示差異。
> **全文**：[漢堡大學 PDF](https://blogs.dickinson.edu/buddhistethics/files/2015/JBE-Anaalayo.pdf)
"""


def test_parse_entry_block_article_extracts_all_fields():
    e = lr.parse_entry_block(ENTRY_ARTICLE)
    assert e["authors"] == "Anālayo"
    assert e["year"] == 2015
    assert e["title"] == "The Cullavagga on Bhikkhunī Ordination"
    assert e["venue"] == "Journal of Buddhist Ethics"
    assert e["language"] == "en"
    assert e["dimension"] == "文本考證 / 詮釋爭論"
    assert e["stance"] and "非佛陀親制" in e["stance"]
    assert "Cullavagga" in e["abstract"]
    assert e["fulltext_url"] == "https://blogs.dickinson.edu/buddhistethics/files/2015/JBE-Anaalayo.pdf"


ENTRY_BOOK = """【I. B. Horner】（1930）《Women Under Primitive Buddhism: Laywomen and Almswomen》，Routledge 出版，London。
語言：英文
所屬面向：文本考證 / 女性議題
摘要：西方學術界最早系統研究巴利文獻中佛教女性地位的奠基性著作。
"""


def test_parse_entry_block_book_uses_double_bracket_title():
    # A book: title is in 《》 (no 〈〉 article title), venue = publisher line.
    e = lr.parse_entry_block(ENTRY_BOOK)
    assert e["authors"] == "I. B. Horner"
    assert e["year"] == 1930
    assert "Women Under Primitive Buddhism" in e["title"]
    assert e["language"] == "en"
    assert e["stance"] is None          # no 立場 line → None
    assert e["fulltext_url"] is None    # no 全文 link → None


ENTRY_CJK = """【林崇安】（2013）〈八敬法的演變〉，《內觀雜誌》，第 100 期，頁 2–7。
語言：中文
所屬面向：文本考證 / 跨傳統比較
摘要：以《僧祇律》為底本，比較南傳、漢傳各律藏中八敬法條文的排列順序與內容異同。
> **全文**：[NTU 佛學全文](http://www.ss.ncu.edu.tw/~calin/article2008/13_5.pdf)
"""


def test_parse_entry_block_chinese_entry():
    e = lr.parse_entry_block(ENTRY_CJK)
    assert e["authors"] == "林崇安"
    assert e["year"] == 2013
    assert e["title"] == "八敬法的演變"
    assert e["venue"] == "內觀雜誌"
    assert e["language"] == "zh"
    assert e["fulltext_url"].endswith("13_5.pdf")
    assert e["ref_key"]  # block parse fills ref_key too


# ── whole report ──────────────────────────────────────────────────────────────
MINI_REPORT = """#八敬法（aṭṭhagarudhammā）學術文獻綜述報告
> 搜尋日期：2026-05-31
> 精選文獻：3 筆

## 執行摘要
八敬法研究在過去三十年間形成了三條主要學術脈絡。

主要研究空白包括：
1. #形式批判與編輯批判方法的中文應用：較少運用 form criticism。
2. #日文學界的系統性整理：尚缺乏系統引介。
3. #反對廢除立場的學術論著：維護其律制正當性的系統性學術論著相對缺乏。

#文本考證與來源研究

【Anālayo】（2016）〈The Foundation History of the Nuns' Order〉，《Hamburg Buddhist Studies》，第 6 冊，Projektverlag 出版，Bochum。
語言：英文
所屬面向：文本考證 / 詮釋爭論
摘要：本書為迄今最完整的比丘尼建立史比較研究。

【林崇安】（2013）〈八敬法的演變〉，《內觀雜誌》，第 100 期，頁 2–7。
語言：中文
所屬面向：文本考證 / 跨傳統比較
摘要：以《僧祇律》為底本，比較南傳、漢傳各律藏中八敬法條文。
> **全文**：[NTU 佛學全文](http://www.ss.ncu.edu.tw/~calin/article2008/13_5.pdf)

#女性議題與比丘尼制度

【釋昭慧】（2001）〈廢除八敬法宣言〉，宣讀於中央研究院。
語言：中文
所屬面向：詮釋爭論 / 女性議題
立場：主張八敬法非佛說，應予廢除
摘要：釋昭慧以「八敬法顯非佛說」為核心論點。
"""


def test_parse_review_report_extracts_summary_and_gaps():
    r = lr.parse_review_report(MINI_REPORT)
    assert "三條主要學術脈絡" in r["summary"]
    assert isinstance(r["gaps"], list) and len(r["gaps"]) == 3
    assert any("形式批判" in g for g in r["gaps"])


def test_parse_review_report_extracts_all_entries():
    r = lr.parse_review_report(MINI_REPORT)
    assert len(r["entries"]) == 3
    titles = [e["title"] for e in r["entries"]]
    assert "The Foundation History of the Nuns' Order" in titles
    assert "八敬法的演變" in titles
    assert "廢除八敬法宣言" in titles


def test_parse_review_report_assigns_theme_from_section_header():
    r = lr.parse_review_report(MINI_REPORT)
    by_title = {e["title"]: e for e in r["entries"]}
    assert by_title["八敬法的演變"]["theme"] == "文本考證與來源研究"
    assert by_title["廢除八敬法宣言"]["theme"] == "女性議題與比丘尼制度"


def test_parse_review_report_ref_keys_are_unique():
    r = lr.parse_review_report(MINI_REPORT)
    keys = [e["ref_key"] for e in r["entries"]]
    assert len(keys) == len(set(keys))


# ── doc-type (參考文獻 / works-cited) report ──────────────────────────────────
DOCTYPE_REPORT = """#某論文參考文獻

## 執行摘要
本份為論文實際引用之書目，按文獻類型分組。

#專書著作

【釋昭慧】（1999）《律學今詮》，法界，台北。
語言：中文
所屬面向：改革實踐型
立場：主張廢除八敬法
摘要：昭慧法師戒律學思想的代表作。

#網路文章

【林建德】（2019）〈女眾剃度男眾之可能？！〉，林建德網誌（2019.11.17）。
語言：中文
摘要：探討女眾為男眾剃度授戒的可能性。
> **全文**：[mind-breath.blogspot.com](https://mind-breath.blogspot.com/2019/11/blog-post_15.html)
"""


def test_parse_review_report_assigns_doc_type_section_as_theme():
    r = lr.parse_review_report(DOCTYPE_REPORT)
    by_title = {e["title"]: e for e in r["entries"]}
    assert by_title["律學今詮"]["theme"] == "專書著作"
    assert by_title["女眾剃度男眾之可能？！"]["theme"] == "網路文章"


def test_parse_review_report_doc_type_book_and_web_fields():
    r = lr.parse_review_report(DOCTYPE_REPORT)
    by_title = {e["title"]: e for e in r["entries"]}
    book = by_title["律學今詮"]
    assert book["authors"] == "釋昭慧" and book["year"] == 1999
    assert book["venue"].startswith("法界")
    assert book["language"] == "zh" and book["stance"] == "主張廢除八敬法"
    web = by_title["女眾剃度男眾之可能？！"]
    assert web["fulltext_url"].endswith("blog-post_15.html")


# ── PDF-text → paragraphs ─────────────────────────────────────────────────────
PDF_TEXT = """The Foundation History of the Nuns' Order

This study examines the canonical accounts of how the order of nuns came
into being, comparing the Pāli, Chinese, and Tibetan versions of the
narrative.

42

Journal of Buddhist Ethics

The eight garudhammas appear in all extant versions, but their inter-
nal ordering differs considerably across the transmissions.
"""


def test_extract_paragraphs_from_text_joins_wrapped_lines():
    paras = lr.extract_paragraphs_from_text(PDF_TEXT)
    # the intro paragraph's three wrapped lines join into one
    intro = next(p for p in paras if "canonical accounts" in p)
    assert "\n" not in intro
    assert "came into being" in intro


def test_extract_paragraphs_from_text_drops_page_numbers_and_running_headers():
    paras = lr.extract_paragraphs_from_text(PDF_TEXT)
    assert all(p.strip() != "42" for p in paras)
    assert all(p.strip() != "Journal of Buddhist Ethics" for p in paras)


def test_extract_paragraphs_from_text_dehyphenates_across_linebreaks():
    paras = lr.extract_paragraphs_from_text(PDF_TEXT)
    assert any("internal ordering" in p for p in paras)
    assert all("inter- nal" not in p and "inter-nal" not in p for p in paras)


# ── HTML → paragraphs ─────────────────────────────────────────────────────────
HTML_FULLTEXT = """
<html><head><title>x</title><style>p{}</style></head><body>
  <div class="nav"><a href="#">Home</a></div>
  <p>The revival of the bhikkhunī order has been a contested topic.</p>
  <p>&nbsp;</p>
  <p>This paper argues that single ordination is canonically valid.</p>
  <script>var y=1;</script>
</body></html>
"""


def test_extract_paragraphs_from_html_keeps_content_drops_chrome():
    paras = lr.extract_paragraphs_from_html(HTML_FULLTEXT)
    assert any("contested topic" in p for p in paras)
    assert any("single ordination" in p for p in paras)
    for p in paras:
        assert "var y" not in p
        assert p.replace("\xa0", "").strip() != ""


# ── resumable translation ─────────────────────────────────────────────────────
def test_missing_indices_returns_untranslated_positions_in_order():
    # paragraphs 0..5; 0,1,3 already translated → resume 2,4,5
    assert lr.missing_indices({0, 1, 3}, 6) == [2, 4, 5]


def test_missing_indices_empty_when_all_done():
    assert lr.missing_indices({0, 1, 2}, 3) == []


def test_missing_indices_all_when_none_done():
    assert lr.missing_indices(set(), 4) == [0, 1, 2, 3]


# ── alignment gate ────────────────────────────────────────────────────────────
def test_align_ok_requires_equal_length():
    assert lr.align_ok(["a", "b"], ["甲", "乙"])
    assert not lr.align_ok(["a", "b"], ["甲"])


def test_assert_aligned_raises_on_mismatch():
    with pytest.raises(ValueError):
        lr.assert_aligned(["a", "b", "c"], ["甲", "乙"])
    lr.assert_aligned(["a"], ["甲"])  # no raise on match
