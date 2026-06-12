"""Pure parsing / normalisation helpers for the ACCS patristic-commentary layer
of the /scripture reader (古代基督信仰聖經註釋叢書 → accs_commentary table).

The heavy lifting (OCR of the scanned 校園 Chinese ACCS pages → raw structured
entries) is done by Gemini in ingest_accs_genesis.py. THIS module is the
deterministic, import-safe, test-covered core that turns those raw entries into
ordered DB rows:

  - parse_verse_range("1:1-2", 1)          → (1, 2)
  - normalize_father(" 金口约翰 ")          → "金口若望"   (variant → glossary)
  - build_rows(book, chapter, entries)     → list of accs_commentary dict rows
                                             with pericope_order / entry_order

No env reads, no network, no heavy deps. Tested by
scripts/tests/test_accs_commentary.py.
"""
from __future__ import annotations

import re
from typing import Optional, TypedDict


# ── Father-name variants → glossary 主譯 ─────────────────────────────────────
# ACCS 中文版偶用與本站詞庫不同的譯名（或簡體殘留）。收斂到 theologians 主譯，
# 與 /fathers 全集一致。只收「同一人不同寫法」，不碰同名異人。
FATHER_FIXES: dict[str, str] = {
    "屈梭多模": "金口若望",
    "金口约翰": "金口若望",
    "金口約翰": "金口若望",
    "约翰·屈梭多模": "金口若望",
    "奥古斯丁": "奧古斯丁",
    "區利羅": "區利羅",
    "西里尔": "區利羅",
    "巴西略": "巴西流",
    "大巴西流": "巴西流",
    "俄利根": "俄利根",
    "奥利金": "俄利根",
    "耶柔米": "耶柔米",
    "希耶羅尼穆斯": "耶柔米",
    "盎博羅削": "安波羅修",
    "安波羅斯": "安波羅修",
    "亚他那修": "亞他那修",
    "爱任纽": "愛任紐",
    "特土良": "特土良",
}

SECTION_KINDS = {"overview", "comment"}


class RawEntry(TypedDict, total=False):
    """One entry as emitted by the OCR/structuring step (before ordering)."""
    ref: str            # 經文範圍，如 "1:1-2" / "1:1" / "創 1:1-2"
    kind: str           # 'overview' | 'comment'
    heading: str        # 主題小標（可空）
    father: str         # 教父名（comment 必填；overview 空）
    father_en: str      # 教父英文名（可空）
    work: str           # 作品名（comment 用；可空）
    body: str           # 繁中正文


# ── Verse-range parsing ──────────────────────────────────────────────────────

_REF_RE = re.compile(
    r"""
    (?:(?P<chap>\d+)\s*[:：]\s*)?   # 可選章號（'1:'）
    (?P<v1>\d+)                     # 起節
    (?:\s*[-–—~]\s*                 # 連字（hyphen / en/em dash / 波浪）
       (?:(?P<chap2>\d+)\s*[:：]\s*)?
       (?P<v2>\d+))?               # 迄節（可選）
    """,
    re.VERBOSE,
)


def parse_full_ref(ref: str) -> Optional[tuple[Optional[int], int, int]]:
    """Like parse_verse_range but also returns the chapter when the ref carries
    one: '1:1-2' → (1, 1, 2) · '2:4' → (2, 4, 4) · '5' → (None, 5, 5).

    Used by build_rows_auto() to route a whole-book OCR run (all chapters in one
    pass) to the right chapter. chapter is None when the ref is a bare verse.
    """
    if not ref:
        return None
    m = _REF_RE.search(ref.strip())
    if not m:
        return None
    chap = int(m.group("chap")) if m.group("chap") else None
    v1 = int(m.group("v1"))
    v2_s = m.group("v2")
    chap2 = m.group("chap2")
    if v2_s is None:
        return (chap, v1, v1)
    v2 = int(v2_s)
    if chap2 is not None and m.group("chap") is not None and chap2 != m.group("chap"):
        return (chap, v1, v1)  # cross-chapter → clamp to start chapter
    if v2 < v1:
        return (chap, v1, v1)
    return (chap, v1, v2)


def parse_verse_range(ref: str, chapter: int) -> Optional[tuple[int, int]]:
    """'1:1-2' → (1, 2) · '1:1' → (1, 1) · '創 1:5' → (5, 5).

    - chapter 號若出現且與 `chapter` 不符 → 以 ref 內為準仍回 (v1, v2)，
      但跨章範圍（chap2 != chap1）截斷到本章末段：只取本章起節，end=v1。
    - 解析不出數字 → None。
    """
    if not ref:
        return None
    # 去掉書卷中文/英文前綴（'創' 'Gen' 等），只留章節數字片段
    m = _REF_RE.search(ref.strip())
    if not m:
        return None
    v1 = int(m.group("v1"))
    v2_s = m.group("v2")
    chap2 = m.group("chap2")
    if v2_s is None:
        return (v1, v1)
    v2 = int(v2_s)
    # 跨章（如 '1:30-2:3'）→ 不跨表，夾到本章：end = v1（保守，留給人工或下段接續）
    if chap2 is not None and m.group("chap") is not None and chap2 != m.group("chap"):
        return (v1, v1)
    if v2 < v1:
        return (v1, v1)
    return (v1, v2)


# ── Father-name normalisation ────────────────────────────────────────────────

def normalize_father(name: Optional[str]) -> Optional[str]:
    """Trim + collapse whitespace + map known variants to glossary 主譯.

    None / 空字串 → None（overview 無作者）。
    """
    if not name:
        return None
    n = re.sub(r"\s+", "", name.strip())
    # 去掉外圍書名號/括號雜訊
    n = n.strip("「」『』()（）")
    if not n:
        return None
    return FATHER_FIXES.get(n, n)


# ── Row assembly ─────────────────────────────────────────────────────────────

def _pericope_key(rng: tuple[int, int]) -> tuple[int, int]:
    return rng


def build_rows(
    book_code: str,
    chapter: int,
    entries: list[RawEntry],
    source_vol: str,
) -> list[dict]:
    """Turn ordered raw entries into accs_commentary DB rows.

    - 段落（pericope）依**首次出現順序**編號 pericope_order（1,2,3…），同 ref 共享。
    - entry_order 在每個段落內由 0 起累加（overview 通常排在 comments 前，但本函式
      尊重輸入順序，不重排 kind）。
    - 跳過 body 空白的 entry。
    - section_kind 不合法 → 視為 'comment'。
    """
    rows: list[dict] = []
    pericope_order: dict[tuple[int, int], int] = {}
    entry_counter: dict[tuple[int, int], int] = {}

    for e in entries:
        body = (e.get("body") or "").strip()
        if not body:
            continue
        rng = parse_verse_range(e.get("ref", ""), chapter)
        if rng is None:
            continue
        key = _pericope_key(rng)
        if key not in pericope_order:
            pericope_order[key] = len(pericope_order) + 1
            entry_counter[key] = 0

        kind = e.get("kind", "comment")
        if kind not in SECTION_KINDS:
            kind = "comment"

        father = normalize_father(e.get("father")) if kind == "comment" else None
        work = (e.get("work") or "").strip() or None if kind == "comment" else None
        heading = (e.get("heading") or "").strip() or None
        father_en = (e.get("father_en") or "").strip() or None if kind == "comment" else None

        rows.append({
            "book_code": book_code,
            "chapter": chapter,
            "verse_start": rng[0],
            "verse_end": rng[1],
            "pericope_order": pericope_order[key],
            "entry_order": entry_counter[key],
            "section_kind": kind,
            "heading": heading,
            "father_name": father,
            "father_name_en": father_en,
            "work_title": work,
            "body_zh": body,
            "source_vol": source_vol,
        })
        entry_counter[key] += 1

    return rows


def build_rows_auto(
    book_code: str,
    entries: list[RawEntry],
    source_vol: str,
    default_chapter: Optional[int] = None,
) -> list[dict]:
    """Whole-book variant of build_rows: chapter comes from each entry's `ref`
    (parse_full_ref), so a single OCR pass over a multi-chapter PDF routes rows
    to the correct chapter. Bare-verse refs (no chapter) carry forward the most
    recently seen chapter (entries are processed in page/source order).

    pericope_order / entry_order are assigned **per chapter**.
    """
    rows: list[dict] = []
    # per-chapter ordering state
    pericope_order: dict[int, dict[tuple[int, int], int]] = {}
    entry_counter: dict[int, dict[tuple[int, int], int]] = {}
    last_chapter = default_chapter

    for e in entries:
        body = (e.get("body") or "").strip()
        if not body:
            continue
        parsed = parse_full_ref(e.get("ref", ""))
        if parsed is None:
            continue
        chap, v1, v2 = parsed
        if chap is None:
            chap = last_chapter
        if chap is None:
            continue  # no chapter context yet → skip
        last_chapter = chap

        pericope_order.setdefault(chap, {})
        entry_counter.setdefault(chap, {})
        key = (v1, v2)
        if key not in pericope_order[chap]:
            pericope_order[chap][key] = len(pericope_order[chap]) + 1
            entry_counter[chap][key] = 0

        kind = e.get("kind", "comment")
        if kind not in SECTION_KINDS:
            kind = "comment"
        father = normalize_father(e.get("father")) if kind == "comment" else None
        work = (e.get("work") or "").strip() or None if kind == "comment" else None
        heading = (e.get("heading") or "").strip() or None
        father_en = (e.get("father_en") or "").strip() or None if kind == "comment" else None

        rows.append({
            "book_code": book_code,
            "chapter": chap,
            "verse_start": v1,
            "verse_end": v2,
            "pericope_order": pericope_order[chap][key],
            "entry_order": entry_counter[chap][key],
            "section_kind": kind,
            "heading": heading,
            "father_name": father,
            "father_name_en": father_en,
            "work_title": work,
            "body_zh": body,
            "source_vol": source_vol,
        })
        entry_counter[chap][key] += 1

    return rows
