"""Pure parsing / slug / alignment helpers for the /canon-law (教會法規)
ingestion pipeline.

Mirrors scripts/gnostic_library.py: DB-backed three-table model
(canon_law_{documents,versions,sections}), EN↔ZH↔LA aligned per canon number.

Sources (vatican.va official 繁中 primary):
  - CIC 1983  天主教法典   — vatican.va/chinese/cic/  (37 per-canon-range PDFs)
  - CCC       天主教教理   — vatican.va/chinese/ccc/  (34 PDFs)
  - Apostolic Canons 85    — Schaff ANF Vol 8 (en/grc already on site)
  - Pedalion               — archive.org (Cummings 1957, en)

Import-safe, no network; bs4 / pdf libs lazy-imported inside the parsers.
Tested by scripts/tests/test_canon_law.py.
"""
from __future__ import annotations

import re

VATICAN_ROOT = "https://www.vatican.va/"


# ── Taxonomy: the four MVP corpora ───────────────────────────────────────────
# dedup_against_existing=True → the doc overlaps /creeds (Apostolic / Trent
# canons already there); ingest should skip duplicates by normalized title.
CORPORA: list[dict] = [
    {
        "slug": "cic-1983", "tradition": "catholic", "corpus": "code",
        "title_zh": "天主教法典", "title_zh_short": "法典",
        "title_en": "Code of Canon Law (1983)",
        "title_lat": "Codex Iuris Canonici",
        "structure_note": "7 卷 / 1752 條", "promulgated_year": 1983,
        "langs": ["la", "en", "zh"], "display_order": 10,
        "dedup_against_existing": False,
    },
    {
        "slug": "ccc", "tradition": "catholic", "corpus": "catechism",
        "title_zh": "天主教教理", "title_zh_short": "教理",
        "title_en": "Catechism of the Catholic Church",
        "title_lat": "Catechismus Catholicae Ecclesiae",
        "structure_note": "4 卷 / 2865 段", "promulgated_year": 1992,
        "langs": ["la", "en", "zh"], "display_order": 20,
        "dedup_against_existing": False,
    },
    {
        "slug": "apostolic-canons-85", "tradition": "orthodox",
        "corpus": "ancient-canons",
        "title_zh": "使徒教規（85 條）", "title_zh_short": "使徒教規",
        "title_en": "The Apostolic Canons", "title_lat": "Canones Apostolorum",
        "structure_note": "85 條", "promulgated_year": 380,
        "langs": ["grc", "en", "zh"], "display_order": 30,
        "dedup_against_existing": True,
    },
    {
        "slug": "pedalion", "tradition": "orthodox", "corpus": "ancient-canons",
        "title_zh": "東正教教規彙編（船舵）", "title_zh_short": "船舵",
        "title_en": "The Pedalion (The Rudder)", "title_lat": "",
        "structure_note": "使徒/大公/地方會議/教父教規 + 註解",
        "promulgated_year": 1800,
        "langs": ["en", "zh"], "display_order": 40,
        "dedup_against_existing": True,
    },
]

CORPUS_BY_SLUG = {c["slug"]: c for c in CORPORA}


# ── vatican.va Chinese CIC PDFs (curated — names are irregular per book) ──────
# Bare basenames under /chinese/cic/; full list scraped from cic_zh.htm.
CIC_ZH_PDFS: list[str] = [
    "cic-libro-I-cann1-6_zh-t.pdf",
    "cic-libro-I-cann7-22_zh-t.pdf",
    "cic-libro-I-cann23-28-tit-II_zh-t.pdf",
    "cic-libro-I-cann29-34-tit-III_zh-t.pdf",
    "cic-libro-I-cann35-93-tit-IV_zh-t.pdf",
    "cic-libro-I-cann94-95-tit-V_zh-t.pdf",
    "cic-libro-I-cann96-123-tit-VI_zh-t.pdf",
    "cic-libro-I-cann124-128-tit-VII_zh-t.pdf",
    "cic-libro-I-cann129-144-tit-VIII_zh-t.pdf",
    "cic-libro-I-cann145-196-tit-IX_zh-t.pdf",
    "cic-libro-I-cann197-199-tit-X_zh-t.pdf",
    "cic-libro-I-cann200-203-tit-XI_zh-t.pdf",
    "cic-libro-II-ParteI-cann204-329_zh-t.pdf",
    "cic-libro-II-ParteII-cann330-572_zh-t.pdf",
    "cic-libro-II-ParteIII-cann573-746_zh-t.pdf",
    "cic-libro-III-cann747-755_zh-t.pdf",
    "cic-libro-III-cann756-780-tit-I_zh-t.pdf",
    "cic-libro-III-cann781-792-tit-II_zh-t.pdf",
    "cic-libro-III-cann793-821-tit-III_zh-t.pdf",
    "cic-libro-III-cann822-832-tit-IV_zh-t.pdf",
    "cic-libro-III-cann833-tit-V_zh-t.pdf",
    "cic-libro-IV-cann834-839_zh-t.pdf",
    "cic-libro-IV-cann840-1165-ParteI_zh-t.pdf",
    "cic-libro-IV-cann1166-1204-ParteII_zh-t.pdf",
    "cic-libro-IV-cann1205-1253-ParteIII_zh-t.pdf",
    "cic-libro-V-cann1254-1258_zh-t.pdf",
    "cic-libro-V-cann1259-1272-tit-I_zh-t.pdf",
    "cic-libro-V-cann1273-1289-tit-II_zh-t.pdf",
    "cic-libro-V-cann1290-1298-tit-III_zh-t.pdf",
    "cic-libro-V-cann1299-1310-tit-IV_zh-t.pdf",
    "cic-libro-VI-cann1311-1363-ParteI_zh-t.pdf",
    "cic-libro-VI-cann1364-1399-ParteII_zh-t.pdf",
    "cic-libro-VII-cann1400-1500-ParteI_zh-t.pdf",
    "cic-libro-VII-cann1501-1670-ParteII_zh-t.pdf",
    "cic-libro-VII-cann1671-1716-ParteIII_zh-t.pdf",
    "cic-libro-VII-cann1717-1731-ParteIV_zh-t.pdf",
    "cic-libro-VII-cann1732-1752-ParteV_zh-t.pdf",
]

_CIC_NAME_RE = re.compile(r"libro-([IVXLCDM]+).*?cann(\d+)(?:-(\d+))?", re.I)

# CIC 7-book structure with canon ranges → clean Chinese book labels for the
# reader sidebar tree (independent of OCR; stamped on every version's rows).
CIC_BOOKS: list[dict] = [
    {"label": "第一卷 總則",        "low": 1,    "high": 203},
    {"label": "第二卷 天主子民",     "low": 204,  "high": 746},
    {"label": "第三卷 教會訓導職",   "low": 747,  "high": 833},
    {"label": "第四卷 教會聖化職務", "low": 834,  "high": 1253},
    {"label": "第五卷 教會財產",     "low": 1254, "high": 1310},
    {"label": "第六卷 教會刑法",     "low": 1311, "high": 1399},
    {"label": "第七卷 程序法",       "low": 1400, "high": 1752},
]


def cic_book_for(canon_no: int):
    """A CIC canon number → its 卷 label ('第一卷 總則'), or None if out of range."""
    for b in CIC_BOOKS:
        if b["low"] <= canon_no <= b["high"]:
            return b["label"]
    return None


def cic_zh_url(basename: str) -> str:
    """Bare CIC PDF basename → full vatican.va Chinese URL."""
    return VATICAN_ROOT + "chinese/cic/" + basename


def parse_cic_basename(name: str) -> dict:
    """'cic-libro-III-cann822-832-tit-IV_zh-t.pdf' →
    {book:'III', cann_low:822, cann_high:832}. Single-canon files
    ('...cann833...') give cann_low == cann_high."""
    m = _CIC_NAME_RE.search(name)
    if not m:
        raise ValueError(f"not a CIC PDF basename: {name!r}")
    low = int(m.group(2))
    high = int(m.group(3)) if m.group(3) else low
    return {"book": m.group(1).upper(), "cann_low": low, "cann_high": high}


# ── Slug + dedup key (identical posture to gnostic_library) ───────────────────
_LEADING_THE = re.compile(r"^the\s+", re.I)
_PARENS = re.compile(r"\([^)]*\)")
_NONWORD = re.compile(r"[^a-z0-9]+")
_SLUG_MAX = 110


def _strip_title(title: str) -> str:
    t = title.strip()
    t = _PARENS.sub(" ", t)
    t = _LEADING_THE.sub("", t.strip())
    return t.strip().lower()


def make_slug(title: str) -> str:
    t = _strip_title(title)
    s = _NONWORD.sub("-", t).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > _SLUG_MAX:
        s = s[:_SLUG_MAX].rsplit("-", 1)[0]
    return s.strip("-")


def normalize_title(title: str) -> str:
    t = _strip_title(title)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def is_duplicate(title: str, existing) -> bool:
    key = normalize_title(title)
    return any(key == normalize_title(e) for e in existing)


# ── Roman numerals (for 'Canon LXXXV.') ──────────────────────────────────────
_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> int:
    total, prev = 0, 0
    for ch in reversed(s.upper()):
        v = _ROMAN_VALUES.get(ch, 0)
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


# ── Canon / paragraph label parsing ──────────────────────────────────────────
_CJK_CANON_RE = re.compile(r"^第\s*(\d+)\s*條\b")
_LAT_CANON_RE = re.compile(r"^Can\.\s*(\d+)\s*(?:§\s*(\d+))?", re.I)
_ROMAN_CANON_RE = re.compile(r"^Canon\s+([IVXLCDM]+)\b", re.I)
_PLAIN_NUM_RE = re.compile(r"^(\d+)\.\s*$")


def _canon_match(s: str):
    """Internal: (order_index, label, num_end, base_label) for a canon-opening
    line, else None.
      - label      = full marker incl. any §N ('Can. 1 §2')   ← display of a sub-marker
      - num_end    = offset just past the canon NUMBER (before §)  ← split keeps §N+body
      - base_label = canon marker without §N ('Can. 1')        ← one section per canon
    """
    m = _CJK_CANON_RE.match(s)
    if m:
        n = int(m.group(1))
        return n, f"第 {n} 條", m.end(), f"第 {n} 條"
    m = _LAT_CANON_RE.match(s)
    if m:
        n = int(m.group(1))
        base = f"Can. {n}"
        label = base + (f" §{m.group(2)}" if m.group(2) else "")
        return n, label, m.end(1), base
    m = _ROMAN_CANON_RE.match(s)
    if m:
        lab = f"Canon {m.group(1).upper()}"
        return roman_to_int(m.group(1)), lab, m.end(), lab
    m = _PLAIN_NUM_RE.match(s)
    if m:
        return int(m.group(1)), m.group(1), m.end(1), m.group(1)
    return None


def parse_canon_label(line: str):
    """A line → (order_index:int, label:str) if it opens a canon / paragraph,
    else None. Handles 'Can. 1 §2.', '第 1 條', 'Canon LXXXV.', '748.'."""
    res = _canon_match(line.strip())
    return (res[0], res[1]) if res else None


# ── Hierarchy heading parsing (卷/編/題/章 + LIBER/Pars/Titulus/Caput) ─────────
_CJK_NUM = r"[一二三四五六七八九十百千零兩０-９0-9]"
_CJK_HEADING_RE = re.compile(rf"^第\s*(?:{_CJK_NUM}\s*)+(卷|編|題|章)\b")
_CJK_LEVEL = {"卷": "book", "編": "part", "題": "title", "章": "chapter"}
_LAT_HEADING_RE = re.compile(r"^(LIBER|Pars|Titulus|Caput)\b", re.I)
_LAT_LEVEL = {"liber": "book", "pars": "part", "titulus": "title", "caput": "chapter"}


def parse_hierarchy(line: str):
    """A line → {level, label} if it is a 卷/編/題/章 (or Latin LIBER/Pars/
    Titulus/Caput) heading, else None. label is the whitespace-collapsed line."""
    s = " ".join(line.split())
    if not s:
        return None
    m = _CJK_HEADING_RE.match(s)
    if m:
        return {"level": _CJK_LEVEL[m.group(1)], "label": s}
    m = _LAT_HEADING_RE.match(s)
    if m:
        return {"level": _LAT_LEVEL[m.group(1).lower()], "label": s}
    return None


# ── Split extracted text lines into aligned section dicts ─────────────────────
def split_into_sections(lines, lang: str) -> list[dict]:
    """Extracted text lines (from PDF/HTML) → content section dicts:
        {order_index, label, book_label, chapter_label, text}
    order_index == canon / paragraph number (the EN↔ZH↔LA alignment key).
    The reader derives its 卷/題 sidebar tree by grouping rows on
    book_label / chapter_label (mirrors /apocrypha — no separate heading rows).
    """
    body_sep = "" if lang == "zh" else " "
    out: list[dict] = []
    book_label = None
    chapter_label = None
    cur: dict | None = None
    body: list[str] = []

    def flush():
        nonlocal cur, body
        if cur is not None:
            cur["text"] = body_sep.join(b for b in body if b).strip()
            out.append(cur)
        cur, body = None, []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        h = parse_hierarchy(line)
        if h:
            if h["level"] == "book":
                book_label = h["label"]
                chapter_label = None
            else:
                chapter_label = h["label"]
            continue
        lab = _canon_match(line)
        if lab:
            n, _label, num_end, base_label = lab
            rest = line[num_end:].lstrip(" .：:")  # §N + inline body after the number
            if cur is not None and cur["order_index"] == n:
                # a §-subsection of the SAME canon → keep one row, append to body
                if rest:
                    body.append(rest)
                continue
            flush()
            cur = {
                "order_index": n,
                "label": base_label,
                "book_label": book_label,
                "chapter_label": chapter_label,
                "text": "",
            }
            if rest:
                body.append(rest)
            continue
        if cur is not None:
            body.append(line)
    flush()
    return out


# ── Alignment gate (la ↔ en ↔ zh, keyed by canon number) ──────────────────────
def _content_orders(rows) -> set:
    return {r["order_index"] for r in rows if not r.get("is_heading")}


def align_report(by_lang: dict) -> dict:
    """{lang: sections} → {ok, counts, missing}. `missing[lang]` lists the
    canon numbers present in some other version but absent from `lang`."""
    sets = {lang: _content_orders(rows) for lang, rows in by_lang.items()}
    union: set = set().union(*sets.values()) if sets else set()
    missing = {lang: sorted(union - s) for lang, s in sets.items()}
    counts = {lang: len(s) for lang, s in sets.items()}
    return {"ok": all(not m for m in missing.values()), "counts": counts, "missing": missing}


def assert_aligned(by_lang: dict) -> None:
    rep = align_report(by_lang)
    if not rep["ok"]:
        gaps = {k: v for k, v in rep["missing"].items() if v}
        raise ValueError(f"canon alignment mismatch: counts={rep['counts']} missing={gaps}")
