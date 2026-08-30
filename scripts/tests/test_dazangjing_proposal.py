# -*- coding: utf-8 -*-
"""基督教大藏經待審提案的四道清理閘（純函式）。

回歸的是 2026-08-28 那份提案的四個真實錯誤：
  ① 作者資料夾被當成作品收進來（《殉教者遊斯丁》《羅馬的革利免》）
  ② 早就在藏的書又推一次（《上帝之城》《懺悔錄》）
  ③ 同名異書被誤判成重複（奧古斯丁 vs 希拉流的《論三位一體》）
  ④ 英中作者對不攏而漏判（`Augustine of Hippo` vs「奧古斯丁」）
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "dz_proposal", ROOT / "scripts" / "dazangjing_proposal.py")
dz = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dz)


@pytest.fixture(scope="module")
def glossary():
    return dz.load_people()


# ── ① 書名其實是人名 ────────────────────────────────────────────────────────
@pytest.mark.parametrize("title_zh,title_orig", [
    ("殉教者遊斯丁", "Justin Martyr"),
    ("羅馬的革利免", "Clement of Rome"),
    ("里昂的愛任紐", "Irenaeus of Lyon"),
])
def test_person_as_title_rejected(glossary, title_zh, title_orig):
    people_en, _, _ = glossary
    assert people_en, "詞庫快取讀不到，這組測試沒有意義"
    assert dz.looks_like_person(
        {"title_zh": title_zh, "title_orig": title_orig, "author": "x"}, people_en)


@pytest.mark.parametrize("title_zh,title_orig,author", [
    ("上帝之城", "De civitate Dei", "希波的奧古斯丁"),
    ("徐光啟集", "徐光啟集", "徐光啟"),          # 文集以作者命名，是書不是人
    ("馬相伯集", "馬相伯集", "馬相伯"),
])
def test_real_works_kept(glossary, title_zh, title_orig, author):
    people_en, _, _ = glossary
    assert not dz.looks_like_person(
        {"title_zh": title_zh, "title_orig": title_orig, "author": author}, people_en)


# ── ②③④ 與現有全藏比對 ─────────────────────────────────────────────────────
CORPUS = [
    {"era": "ancient", "coll": "lun", "canon": "zheng",
     "title_zh": "上帝之城", "title_orig": "De civitate Dei", "author": "奧古斯丁"},
    {"era": "ancient", "coll": "lun", "canon": "zheng",
     "title_zh": "論三位一體", "title_orig": "De Trinitate", "author": "希拉流"},
    {"era": "modern", "coll": "shuxin", "canon": "zheng",
     "title_zh": "百年通諭", "title_orig": "Centesimus Annus", "author": "教宗若望保祿二世"},
]


@pytest.fixture(scope="module")
def idx():
    return dz.build_corpus_index(CORPUS)


def test_same_book_dropped(glossary, idx):
    """英文作者欄靠詞庫橋接到漢語定名，仍要判成同一部。"""
    _, _, en2zh = glossary
    hit = dz.already_in_canon(
        {"title_zh": "上帝之城", "title_orig": "De Civitate Dei contra paganos",
         "author": "Augustine of Hippo"}, *idx, en2zh)
    assert hit and hit[0] == "same"
    assert hit[1]["title_zh"] == "上帝之城"


def test_same_title_different_author_is_suspect_not_dropped(glossary, idx):
    """奧古斯丁的《論三位一體》不是希拉流那部——只能標疑似，不可自動剔。"""
    _, _, en2zh = glossary
    hit = dz.already_in_canon(
        {"title_zh": "論三位一體", "title_orig": "the Trinity",
         "author": "希波的奧古斯丁 Augustine of Hippo"}, *idx, en2zh)
    assert hit and hit[0] == "suspect"


def test_unreconcilable_author_is_suspect(glossary, idx):
    """教宗名不在教父詞庫裡，英中對不攏；不可靜靜放行，要送人工。"""
    _, _, en2zh = glossary
    hit = dz.already_in_canon(
        {"title_zh": "《百年通諭》", "title_orig": "Centesimus Annus",
         "author": "Pope John Paul II (Karol Wojtyła)"}, *idx, en2zh)
    assert hit and hit[0] == "suspect"


def test_new_work_passes(glossary, idx):
    _, _, en2zh = glossary
    assert dz.already_in_canon(
        {"title_zh": "論基督徒的自由", "title_orig": "De libertate christiana",
         "author": "馬丁路德"}, *idx, en2zh) is None


# ── 作者詞元 ────────────────────────────────────────────────────────────────
def test_author_tokens_splits_de():
    """「的」不切開，「希波的奧古斯丁」就對不上藏內只寫「奧古斯丁」的那筆。"""
    assert "奧古斯丁" in dz.author_tokens("希波的奧古斯丁")


def test_same_person_allows_partial_chinese_name():
    assert dz.same_person({"托馬斯", "阿奎那"}, {"阿奎那"})
    assert not dz.same_person({"奧古斯丁"}, {"希拉流"})
