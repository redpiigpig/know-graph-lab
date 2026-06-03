"""Pure core for the 「翻譯定名」glossary (/translation-glossary, promoted to a
top-level card). Domain taxonomy + the 名根一致性 (name-root consistency) rule +
variant parsing. No DB / no network — tested by tests/test_glossary_naming.py.

Architecture (user decision 2026-06-03): keep the two theology tables, ADD one
table per new domain. A `name_root` (canonical Chinese root substring, e.g.
「塞琉」/「密特」/「亞歷山」) ties together names derived from the same source root
so their Chinese renderings stay consistent — every entry tagged with a root
must contain that root string in its recommended translation.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable


# ── Domain taxonomy ──────────────────────────────────────────────────────────
# `is_page` marks the static 翻譯原則 page (no table). Everything else is a tab
# backed by a DB table. theology tables are kept as-is; the rest are new.
DOMAINS: list[dict] = [
    {"key": "principles",        "label_zh": "翻譯原則",       "is_page": True,  "table": None,                "order": 0},
    {"key": "biblical_people",   "label_zh": "聖經人物",       "table": "theologians",        "filter": {"role": "聖經人物"}, "order": 10},
    {"key": "theologians",       "label_zh": "教父與神學家",   "table": "theologians",        "order": 20},
    {"key": "theological_terms", "label_zh": "神學名詞",       "table": "theological_terms",  "order": 30},
    {"key": "philosophers",      "label_zh": "哲學家",         "table": "philosophers",       "order": 40},
    {"key": "scientists",        "label_zh": "科學家",         "table": "scientists",         "order": 50},
    {"key": "rulers",            "label_zh": "歷代帝王",       "table": "historical_rulers",  "order": 60},
    {"key": "places",            "label_zh": "國名與城市",     "table": "place_names",        "order": 70},
    {"key": "deities",           "label_zh": "神祇與宗教名詞", "table": "deities",            "order": 80},
]

DOMAIN_BY_KEY = {d["key"]: d for d in DOMAINS}


# ── Variant parsing ──────────────────────────────────────────────────────────
_VARIANT_SEP = re.compile(r"[；;]")


def split_variants(value: str | None) -> list[str]:
    """Split a 「；」/「;」-separated variant string into trimmed, non-empty parts."""
    if not value:
        return []
    return [p.strip() for p in _VARIANT_SEP.split(value) if p.strip()]


# ── Name-root consistency ────────────────────────────────────────────────────
def root_key(root: str | None) -> str:
    """Normalize a name_root for grouping (trim; ascii roots case-folded)."""
    if not root:
        return ""
    r = root.strip()
    # ascii (romanized) roots compare case-insensitively; CJK roots stay as-is
    return r.lower() if r.isascii() else r


def group_by_root(entries: Iterable[dict]) -> dict[str, list[dict]]:
    """Bucket entries by normalized name_root. Rootless entries are dropped."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        k = root_key(e.get("name_root"))
        if k:
            groups[k].append(e)
    return dict(groups)


def check_root_consistency(entries: Iterable[dict]) -> list[dict]:
    """Flag entries whose recommended translation does NOT honour their name_root.

    The rule (user 2026-06-03): names sharing a root render that root the same
    way — every entry tagged name_root=R must contain R in name_recommended.
    塞琉古/塞琉西亞 (root 塞琉) ✓; 西流基 ✗.  Returns the offending entries with
    their root attached. Rootless entries are ignored.
    """
    bad: list[dict] = []
    for e in entries:
        root = (e.get("name_root") or "").strip()
        if not root:
            continue
        rec = e.get("name_recommended") or ""
        if root not in rec:
            bad.append({**e, "name_root": root})
    return bad
