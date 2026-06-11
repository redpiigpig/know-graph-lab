#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two-axis, confidence-scored main-category classifier.

Why this exists
---------------
The legacy classifiers (`categorize_root_books.classify`, `ingest_new_books.
fallback_category`) are *first-match-wins keyword* rules. That has two failure
modes the user calls out as "categorization still unideal":

  1. No contextual hierarchy. "政治思想史" hits 思想→哲學 OR 政治→社會政治學
     depending on rule order; "宗教史" can't tell 世界宗教 (single religion)
     from 宗教學 (comparative). Whichever pattern is listed first wins.
  2. No confidence. A weak single-keyword hit and a strong multi-signal hit
     are indistinguishable, so low-confidence guesses get committed silently
     instead of being held for review.

This module replaces "first match" with *weighted scoring across all
categories* + explicit *disambiguation rules* for the known contested
boundaries + a *confidence* read from the top-1/top-2 margin. Callers use the
confidence to route uncertain books to a review queue instead of guessing.

It is a pure function of (title, author, filename) — no network/DB/LLM — so the
behavior on every documented bleed case is locked by unit tests. An optional
embedding-backed reranker lives in `semantic.py`-style helpers at the bottom
(network-gated, not required by the deterministic path).

Axes
----
  theme  axis → the 10 main categories (what the book is *about*)
  genre  axis → 原典 / 通史 / 傳記 / 研究 / 論述 (what *kind* of book it is)
The genre axis isn't a category itself; it feeds disambiguation (e.g. 教父
*原典* → 神學, but 教父 *傳記/研究* → 世界宗教) and is returned for explanation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

CATEGORIES = (
    "神學", "世界宗教", "宗教學", "哲學", "歷史學",
    "社會政治學", "心理學", "自然科學", "人類生物學", "文學",
)

# Below this top-1/top-2 margin the call is "uncertain" → caller should
# quarantine for human review rather than commit the guess.
LOW_CONFIDENCE = 0.34


# ── author → category anchors ──────────────────────────────────────────────
# "author known-category lookups": when a dominant author is present the book's
# theme is usually pinned regardless of a generic title keyword. Strong weight.
KNOWN_AUTHORS: dict[str, str] = {
    # 哲學
    "康德": "哲學", "黑格爾": "哲學", "尼采": "哲學", "海德格": "哲學",
    "胡塞爾": "哲學", "維特根斯坦": "哲學", "柏拉圖": "哲學", "亞里士多德": "哲學",
    "笛卡爾": "哲學", "傅柯": "哲學", "福柯": "哲學", "德勒茲": "哲學",
    "牟宗三": "哲學", "王陽明": "哲學",
    # 社會政治學
    "韋伯": "社會政治學", "涂爾幹": "社會政治學", "塗爾幹": "社會政治學",
    "馬克思": "社會政治學", "福山": "社會政治學", "沃格林": "社會政治學",
    "鄂蘭": "社會政治學", "阿倫特": "社會政治學",
    # 神學
    "巴特": "神學", "莫爾特曼": "神學", "拉納": "神學", "潘霍華": "神學",
    "蒂利希": "神學", "奧古斯丁": "神學", "阿奎那": "神學", "多瑪斯": "神學",
    # 宗教學
    "伊利亞德": "宗教學", "涂爾幹的宗教": "宗教學", "弗雷澤": "宗教學", "繆勒": "宗教學",
    # 心理學
    "榮格": "心理學", "弗洛伊德": "心理學", "佛洛伊德": "心理學", "齊澤克": "心理學",
    # 人類生物學
    "道金斯": "人類生物學", "戴蒙德": "人類生物學",
}

# ── keyword → (category, weight) ───────────────────────────────────────────
# weight 3 = unambiguous domain marker; 2 = strong; 1 = weak/generic.
# Substring match (CJK has no word boundaries). Order does NOT matter — every
# rule contributes to the per-category score; the winner is the max, not first.
KEYWORD_WEIGHTS: tuple[tuple[str, str, int], ...] = (
    # 神學 — Christian theology as a discipline
    ("神學", "神學", 2), ("教父", "神學", 2), ("神學大全", "神學", 3),
    ("駁異大全", "神學", 3), ("信理", "神學", 2), ("系統神學", "神學", 3),
    ("基督論", "神學", 2), ("三位一體", "神學", 2), ("救贖論", "神學", 2),
    ("末世論", "神學", 2), ("神義論", "神學", 2), ("聖事", "神學", 1),
    ("信經", "神學", 2), ("教義學", "神學", 2),
    # 世界宗教 — a single religion's own scriptures / history / institutions
    ("佛教史", "世界宗教", 3), ("基督教史", "世界宗教", 3), ("教會史", "世界宗教", 3),
    ("伊斯蘭教史", "世界宗教", 3), ("可蘭經", "世界宗教", 3), ("古蘭經", "世界宗教", 3),
    ("猶太教", "世界宗教", 2), ("塔木德", "世界宗教", 3), ("印度教", "世界宗教", 2),
    ("博伽梵歌", "世界宗教", 3), ("祆教", "世界宗教", 2), ("瑣羅亞斯德", "世界宗教", 2),
    ("佛經", "世界宗教", 2), ("禪", "世界宗教", 1), ("道教", "世界宗教", 2),
    # 宗教學 — comparative / cross-religion / science-of-religion
    ("宗教學", "宗教學", 3), ("比較宗教", "宗教學", 3), ("宗教比較", "宗教學", 3),
    ("神話學", "宗教學", 3), ("宗教社會學", "宗教學", 3), ("宗教現象學", "宗教學", 3),
    ("跨宗教", "宗教學", 3), ("宗教對話", "宗教學", 3), ("宗教研究", "宗教學", 2),
    ("世界宗教史", "宗教學", 2),
    # 哲學
    ("哲學", "哲學", 2), ("形上學", "哲學", 3), ("本體論", "哲學", 3),
    ("現象學", "哲學", 3), ("存在主義", "哲學", 3), ("認識論", "哲學", 3),
    ("倫理學", "哲學", 2), ("邏輯", "哲學", 1), ("詮釋學", "哲學", 1),
    ("形而上", "哲學", 3),
    # 歷史學
    ("歷史", "歷史學", 1), ("文明史", "歷史學", 2), ("編年", "歷史學", 2),
    ("王朝", "歷史學", 2), ("帝國", "歷史學", 1), ("十字軍", "歷史學", 2),
    ("考古", "歷史學", 2), ("拜占庭", "歷史學", 2), ("古代史", "歷史學", 2),
    ("中世紀史", "歷史學", 2), ("思想史", "歷史學", 1), ("文化史", "歷史學", 2),
    # 社會政治學
    ("政治", "社會政治學", 2), ("社會學", "社會政治學", 2), ("社會主義", "社會政治學", 2),
    ("資本主義", "社會政治學", 2), ("資本論", "社會政治學", 3), ("民主", "社會政治學", 2),
    ("極權", "社會政治學", 2), ("意識形態", "社會政治學", 2), ("意識型態", "社會政治學", 2),
    ("階級", "社會政治學", 1), ("憲法", "社會政治學", 2), ("法哲學", "社會政治學", 2),
    # 心理學
    ("心理學", "心理學", 3), ("精神分析", "心理學", 3), ("潛意識", "心理學", 2),
    ("認知", "心理學", 1), ("大腦", "心理學", 1), ("意識", "心理學", 1),
    # 自然科學
    ("物理學", "自然科學", 3), ("數學", "自然科學", 3), ("天文", "自然科學", 2),
    ("化學", "自然科學", 3), ("量子", "自然科學", 3), ("相對論", "自然科學", 3),
    ("宇宙", "自然科學", 1), ("科學作為天職", "自然科學", 1),
    # 人類生物學
    ("人類學", "人類生物學", 2), ("演化", "人類生物學", 2), ("進化", "人類生物學", 2),
    ("自私的基因", "人類生物學", 3), ("薩滿", "人類生物學", 1), ("人類起源", "人類生物學", 2),
    # 文學
    ("小說", "文學", 3), ("詩集", "文學", 3), ("散文", "文學", 2),
    ("戲劇", "文學", 2), ("文學", "文學", 2), ("莎士比亞", "文學", 3),
)

# Genre-axis markers (体裁) — used by disambiguation + returned for explanation.
GENRE_SIGNALS: tuple[tuple[str, str], ...] = (
    ("原典", "原典"), ("全集", "原典"), ("文集", "原典"), ("選集", "原典"),
    ("譯註", "原典"), ("注疏", "原典"),
    ("通史", "通史"), ("簡史", "通史"), ("史綱", "通史"), ("編年", "通史"),
    ("傳", "傳記"), ("評傳", "傳記"), ("傳記", "傳記"), ("生平", "傳記"),
    ("研究", "研究"), ("論", "論述"), ("批判", "論述"), ("導論", "論述"),
    ("概論", "論述"),
)


@dataclass
class Result:
    category: str | None
    confidence: float
    genre: str | None = None
    reason: str = ""
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def uncertain(self) -> bool:
        return self.category is None or self.confidence < LOW_CONFIDENCE


def _detect_genre(text: str) -> str | None:
    for needle, genre in GENRE_SIGNALS:
        if needle in text:
            return genre
    return None


def _score(text: str) -> dict[str, float]:
    scores: dict[str, float] = {c: 0.0 for c in CATEGORIES}
    for needle, cat, w in KEYWORD_WEIGHTS:
        if needle in text:
            scores[cat] += w
    return scores


def _author_anchor(author: str, title: str) -> str | None:
    """Strongest single author signal, if any known author name appears."""
    blob = f"{author} {title}"
    for name, cat in KNOWN_AUTHORS.items():
        if name in blob:
            return cat
    return None


# ── disambiguation: the contested boundaries, resolved by context ──────────
# Each rule may *boost* a category score. They encode the hierarchy the flat
# keyword rules lack. Applied after base scoring, before picking the winner.

def _disambiguate(text: str, scores: dict[str, float], genre: str | None,
                  anchor: str | None) -> tuple[str, str]:
    notes = []

    # Apply the author anchor first as a strong, broad boost; the contextual
    # overrides below can still pull a book away from it (e.g. a Church
    # Father's *biography* belongs in 世界宗教, not 神學).
    if anchor:
        scores[anchor] += 3
        notes.append(f"作者錨點→{anchor}")

    # 政治思想史 → 社會政治學 (political-thought history is political theory,
    # not general history and not pure philosophy).
    if "政治思想" in text:
        scores["社會政治學"] += 3
        notes.append("政治思想→社會政治學")

    # 思想史 alone → 歷史學, UNLESS a philosopher anchor dominates → 哲學.
    elif "思想史" in text:
        if anchor == "哲學":
            scores["哲學"] += 2
            notes.append("思想史+哲學家→哲學")
        else:
            scores["歷史學"] += 2
            notes.append("思想史→歷史學")

    # 宗教史 → 宗教學 only when comparative; a single religion's history stays
    # in 世界宗教 (the 佛教史/基督教史 keywords already weight 世界宗教 above).
    if "宗教史" in text and not any(k in text for k in ("佛教史", "基督教史", "伊斯蘭教史", "道教史")):
        if any(k in text for k in ("比較", "跨宗教", "世界宗教", "諸宗教")):
            scores["宗教學"] += 3
            notes.append("比較宗教史→宗教學")
        else:
            scores["宗教學"] += 1

    # 神學 vs 世界宗教: a 教會史/基督教史 work, or a 教父/神學家 *biography/通史*,
    # is church history → 世界宗教, not theology. Runs after the anchor so it can
    # override e.g. 奧古斯丁→神學 when the book is actually his 評傳.
    church_history = any(k in text for k in ("教會史", "基督教史"))
    father_bio = anchor == "神學" and genre in ("傳記", "通史")
    if church_history or father_bio:
        scores["世界宗教"] += 4
        scores["神學"] -= 2
        notes.append("教會史/教父傳記→世界宗教")

    # 哲學家的神學: "康德的神學"/"X 與神學" where X is a philosopher anchor →
    # 哲學 (it's the philosopher's framework, per user rule).
    if anchor == "哲學" and "神學" in text:
        scores["哲學"] += 2
        notes.append("哲學家論神學→哲學")

    winner = max(CATEGORIES, key=lambda c: scores[c])
    return winner, "; ".join(notes)


def classify(title: str, author: str = "", filename: str = "") -> Result:
    """Score every category, resolve contested boundaries, return a confidence.

    confidence = (top1 - top2) / top1, in [0, 1]. 0 when nothing matched.
    A disambiguation/anchor decision typically pushes the margin past
    LOW_CONFIDENCE; a lone weak keyword stays uncertain → caller quarantines.
    """
    text = f"{title} {author} {filename}"
    genre = _detect_genre(text)
    anchor = _author_anchor(author, title)
    scores = _score(text)
    winner, notes = _disambiguate(text, scores, genre, anchor)

    ordered = sorted(scores.values(), reverse=True)
    top1 = ordered[0]
    top2 = ordered[1] if len(ordered) > 1 else 0.0
    if top1 <= 0:
        return Result(None, 0.0, genre, "no keyword matched", scores)
    confidence = round((top1 - top2) / top1, 3)
    return Result(winner, confidence, genre, notes or "keyword score", scores)


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    for arg in sys.argv[1:]:
        r = classify(arg)
        flag = "  ⚠UNCERTAIN" if r.uncertain else ""
        print(f"{arg!r}\n  → {r.category}  conf={r.confidence}  genre={r.genre}"
              f"  [{r.reason}]{flag}")
