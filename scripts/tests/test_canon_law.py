"""Test-first contract for scripts/canon_law.py.

Pure functions only — no network, all fixtures inline. Mirrors the style of
scripts/tests/test_gnostic_library.py. Covers:
  - CORPORA taxonomy (the four MVP corpora: CIC / CCC / Apostolic Canons / Pedalion)
  - vatican.va URL helpers (cic_zh_url / parse_cic_basename / CIC_ZH_PDFS coverage)
  - parse_canon_label (Can. 1 §2 / 第 1 條 / 748. / Canon I. → order_index + label)
  - parse_hierarchy (卷/編/題/章 + LIBER/Pars/Titulus/Caput → heading level)
  - split_into_sections (extracted lines → numbered + heading section dicts)
  - make_slug / normalize_title / is_duplicate (slug + dedup vs /creeds)
  - align_report / assert_aligned (per-canon three-language alignment gate)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import canon_law as cl  # noqa: E402


# ── Taxonomy ──────────────────────────────────────────────────────────────
def test_corpora_cover_the_four_mvp_documents():
    slugs = {c["slug"] for c in cl.CORPORA}
    assert {"cic-1983", "ccc", "apostolic-canons-85", "pedalion"} <= slugs


def test_each_corpus_has_required_fields():
    valid_trad = {"catholic", "orthodox", "protestant", "anglican"}
    valid_corpus = {"code", "catechism", "ancient-canons", "church-order"}
    for c in cl.CORPORA:
        assert c["title_zh"] and isinstance(c["title_zh"], str)
        assert c["tradition"] in valid_trad
        assert c["corpus"] in valid_corpus
        assert isinstance(c["display_order"], int)
        assert c["langs"], "each corpus must declare its version codes"
        assert set(c["langs"]) <= {"la", "grc", "en", "zh"}


def test_cic_and_ccc_are_catholic_apostolic_canons_orthodox():
    by = {c["slug"]: c for c in cl.CORPORA}
    assert by["cic-1983"]["tradition"] == "catholic"
    assert by["cic-1983"]["corpus"] == "code"
    assert by["ccc"]["corpus"] == "catechism"
    assert by["apostolic-canons-85"]["tradition"] == "orthodox"
    assert by["apostolic-canons-85"]["corpus"] == "ancient-canons"


def test_apostolic_canons_dedup_against_creeds():
    # 使徒教規 / Trent canons already live in /creeds — flag so ingest can dedup.
    by = {c["slug"]: c for c in cl.CORPORA}
    assert by["apostolic-canons-85"].get("dedup_against_existing") is True
    assert by["cic-1983"].get("dedup_against_existing") in (False, None)


# ── vatican.va Chinese CIC PDF helpers ────────────────────────────────────
def test_cic_zh_url_builds_official_vatican_path():
    url = cl.cic_zh_url("cic-libro-III-cann822-832-tit-IV_zh-t.pdf")
    assert url == ("https://www.vatican.va/chinese/cic/"
                   "cic-libro-III-cann822-832-tit-IV_zh-t.pdf")


@pytest.mark.parametrize("name,book,low,high", [
    ("cic-libro-III-cann822-832-tit-IV_zh-t.pdf", "III", 822, 832),
    ("cic-libro-III-cann747-755_zh-t.pdf", "III", 747, 755),
    ("cic-libro-II-ParteII-cann330-572_zh-t.pdf", "II", 330, 572),
    ("cic-libro-IV-cann1205-1253-ParteIII_zh-t.pdf", "IV", 1205, 1253),
])
def test_parse_cic_basename(name, book, low, high):
    info = cl.parse_cic_basename(name)
    assert info["book"] == book
    assert info["cann_low"] == low
    assert info["cann_high"] == high


def test_cic_zh_pdfs_curated_list_is_sorted_and_covers_to_1752():
    pdfs = cl.CIC_ZH_PDFS
    assert len(pdfs) >= 30, "CIC is split into dozens of per-canon-range PDFs"
    ranges = [cl.parse_cic_basename(n) for n in pdfs]
    # every entry parses
    assert all(r["cann_high"] >= r["cann_low"] for r in ranges)
    # canon ranges march forward, no backward jumps, ending at the last canon 1752
    lows = [r["cann_low"] for r in ranges]
    assert lows == sorted(lows)
    assert max(r["cann_high"] for r in ranges) == 1752


# ── CIC 7-book structure map (clean Chinese book labels by canon range) ───
def test_cic_books_cover_1_to_1752_without_gaps():
    books = cl.CIC_BOOKS
    assert len(books) == 7
    assert books[0]["low"] == 1
    assert books[-1]["high"] == 1752
    for prev, nxt in zip(books, books[1:]):
        assert nxt["low"] == prev["high"] + 1  # contiguous, no gaps/overlap
    assert all(b["label"].startswith("第") and "卷" in b["label"] for b in books)


@pytest.mark.parametrize("canon,expected", [
    (1, "第一卷 總則"),
    (203, "第一卷 總則"),
    (204, "第二卷 天主子民"),
    (748, "第三卷 教會訓導職"),
    (1752, "第七卷 程序法"),
])
def test_cic_book_for(canon, expected):
    assert cl.cic_book_for(canon) == expected


def test_cic_book_for_out_of_range():
    assert cl.cic_book_for(0) is None
    assert cl.cic_book_for(9999) is None


# ── CCC structure + Chinese PDFs ──────────────────────────────────────────
def test_ccc_parts_cover_1_to_2865():
    parts = cl.CCC_PARTS
    assert len(parts) == 4
    assert parts[0]["low"] == 1 and parts[-1]["high"] == 2865
    for prev, nxt in zip(parts, parts[1:]):
        assert nxt["low"] == prev["high"] + 1
    assert all(p["label"].startswith("卷") for p in parts)


@pytest.mark.parametrize("para,expected", [
    (1, "卷一 信仰的宣認"),
    (1065, "卷一 信仰的宣認"),
    (1066, "卷二 基督奧跡的慶典"),
    (1691, "卷三 在基督內的生活"),
    (2865, "卷四 基督徒的祈禱"),
])
def test_ccc_part_for(para, expected):
    assert cl.ccc_part_for(para) == expected


def test_ccc_zh_url_and_basenames():
    assert cl.ccc_zh_url("01_0001-0025_ccc_zh.pdf") == \
        "https://www.vatican.va/chinese/ccc/01_0001-0025_ccc_zh.pdf"
    pdfs = cl.CCC_ZH_PDFS
    assert len(pdfs) >= 40
    lo, hi = cl.parse_ccc_basename(pdfs[0]), cl.parse_ccc_basename(pdfs[-1])
    assert lo["low"] == 1 and hi["high"] == 2865


# ── parse_canon_label ─────────────────────────────────────────────────────
@pytest.mark.parametrize("line,order,label", [
    ("Can. 1", 1, "Can. 1"),
    ("Can. 1 §2.", 1, "Can. 1 §2"),
    ("Can. 1752", 1752, "Can. 1752"),
    ("第 1 條", 1, "第 1 條"),
    ("第1條", 1, "第 1 條"),
    ("第 748 條", 748, "第 748 條"),
    ("748.", 748, "748"),
    ("2865.", 2865, "2865"),
    ("Canon I.", 1, "Canon I"),
    ("Canon LXXXV.", 85, "Canon LXXXV"),
])
def test_parse_canon_label_extracts_number(line, order, label):
    res = cl.parse_canon_label(line)
    assert res is not None
    assert res[0] == order
    assert res[1] == label


@pytest.mark.parametrize("line", [
    "主基督曾將信仰寶庫託給教會",          # body prose, no number
    "the faithful are bound to",
    "",
    "Titulus I",                            # a heading, not a canon
])
def test_parse_canon_label_rejects_non_canon(line):
    assert cl.parse_canon_label(line) is None


# ── parse_hierarchy ───────────────────────────────────────────────────────
@pytest.mark.parametrize("line,level", [
    ("第一卷 總則", "book"),
    ("第 二 卷 天主子民", "book"),
    ("第二編 教會聖統制", "part"),
    ("第一題 大眾傳播工具及出版書刊", "title"),
    ("第一章 最高權力", "chapter"),
    ("LIBER I", "book"),
    ("Pars I", "part"),
    ("Titulus IV", "title"),
    ("Caput II", "chapter"),
])
def test_parse_hierarchy_classifies_heading(line, level):
    h = cl.parse_hierarchy(line)
    assert h is not None
    assert h["level"] == level
    assert h["label"]


@pytest.mark.parametrize("line", ["Can. 1", "第 1 條", "748.", "some body text"])
def test_parse_hierarchy_rejects_non_heading(line):
    assert cl.parse_hierarchy(line) is None


# ── split_into_sections ───────────────────────────────────────────────────
_CIC_ZH_FIXTURE = [
    "第一卷 總則",
    "第一題 教會法律",
    "第 1 條",
    "本法典的法律只涉及拉丁教會。",
    "第 2 條",
    "法典通常不規定禮儀應遵守的禮節。",
    "第二題 習慣",
    "第 5 條",
    "現行違反法典規定的習慣，應予廢除。",
]


def test_split_into_sections_tracks_hierarchy_and_numbers():
    secs = cl.split_into_sections(_CIC_ZH_FIXTURE, "zh")
    assert [c["order_index"] for c in secs] == [1, 2, 5]
    # canon 1 carries its body and the enclosing book / title labels
    c1 = secs[0]
    assert "拉丁教會" in c1["text"]
    assert c1["book_label"] == "第一卷 總則"
    assert c1["chapter_label"] == "第一題 教會法律"
    # canon 5 picked up the second 題 as its nearest title heading
    assert secs[-1]["chapter_label"] == "第二題 習慣"


def test_split_into_sections_exposes_tree_pairs():
    # reader builds the sidebar 卷/題 tree by grouping content rows on labels —
    # no separate heading rows (mirrors /apocrypha).
    secs = cl.split_into_sections(_CIC_ZH_FIXTURE, "zh")
    pairs = {(s["book_label"], s["chapter_label"]) for s in secs}
    assert ("第一卷 總則", "第一題 教會法律") in pairs
    assert ("第一卷 總則", "第二題 習慣") in pairs


def test_split_into_sections_inline_english_body():
    # vatican.va English CIC puts marker + body on one line: 'Can. 1 The canons…'
    lines = ["BOOK I", "Can. 1 The canons of this Code regard only the Latin Church.",
             "Can. 2 For the most part the Code does not define the rites."]
    secs = cl.split_into_sections(lines, "en")
    assert [s["order_index"] for s in secs] == [1, 2]
    assert secs[0]["text"].startswith("The canons of this Code")
    assert secs[1]["text"].startswith("For the most part")


def test_split_into_sections_merges_subsections_one_row_per_canon():
    # 'Can. 5 §1.' and 'Can. 5 §2.' are the SAME canon → one row (order_index 5),
    # both § bodies kept (else duplicate-PK 409 on insert).
    lines = ["Can. 5 §1. A custom contrary to the law.",
             "Can. 5 §2. Centenary customs can be tolerated.",
             "Can. 6 The following are abrogated."]
    secs = cl.split_into_sections(lines, "en")
    assert [s["order_index"] for s in secs] == [5, 6]
    assert secs[0]["label"] == "Can. 5"
    assert "§1" in secs[0]["text"] and "§2" in secs[0]["text"]


def test_split_into_sections_ccc_plain_numbers():
    lines = ["748.", "基督為萬民之光。", "749.", "聖神是教會的靈魂。"]
    secs = cl.split_into_sections(lines, "zh")
    assert [s["order_index"] for s in secs] == [748, 749]


# ── Slug / dedup ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("title,expected", [
    ("The Apostolic Canons", "apostolic-canons"),
    ("Code of Canon Law (1983)", "code-of-canon-law"),
    ("The Pedalion", "pedalion"),
])
def test_make_slug(title, expected):
    assert cl.make_slug(title) == expected


def test_is_duplicate_against_creeds_titles():
    existing = ["The Canons of the Council of Trent", "Apostolic Canons"]
    assert cl.is_duplicate("Apostolic Canons", existing) is True
    assert cl.is_duplicate("Code of Canon Law", existing) is False


# ── Alignment gate (la ↔ en ↔ zh, keyed by canon number) ──────────────────
def _mk(orders):
    return [{"order_index": o, "is_heading": False, "text": "x"} for o in orders]


def test_align_report_all_aligned():
    rep = cl.align_report({"zh": _mk([1, 2, 3]), "en": _mk([1, 2, 3]), "la": _mk([1, 2, 3])})
    assert rep["ok"] is True
    assert rep["counts"] == {"zh": 3, "en": 3, "la": 3}
    assert all(not m for m in rep["missing"].values())


def test_align_report_flags_missing_canon():
    rep = cl.align_report({"zh": _mk([1, 2, 3]), "en": _mk([1, 3])})
    assert rep["ok"] is False
    assert 2 in rep["missing"]["en"]


def test_assert_aligned_raises_on_mismatch():
    with pytest.raises(ValueError):
        cl.assert_aligned({"zh": _mk([1, 2, 3]), "en": _mk([1, 2])})


def test_assert_aligned_ignores_heading_rows():
    zh = _mk([1, 2]) + [{"order_index": 0, "is_heading": True, "text": ""}]
    en = _mk([1, 2])
    cl.assert_aligned({"zh": zh, "en": en})  # must not raise
