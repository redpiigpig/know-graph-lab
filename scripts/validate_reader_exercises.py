#!/usr/bin/env python3
"""Gate the ten-item translation exercise set of any original-language reader.

The contract is `skills/build-original-language-reader/references/exercise-sets.md`.
Four readers feed this one validator, so the rules live here as pure functions
over the exercise payload and know nothing about Hebrew, Greek, Latin or
Japanese in particular.

The gate exists because of what the per-language checks cannot see.  A sentence
whose every form is attested and whose every word has been taught can still be
ungrammatical, so `reviewedBy` is part of the contract: a composed item that no
author has read is not releasable however clean its machine verification looks.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

ITEMS_PER_LESSON = 10
MIN_QUOTED_PER_LESSON = 3


def failures_for_item(item: dict[str, Any]) -> list[str]:
    """Every rule an individual exercise has to satisfy."""
    problems: list[str] = []
    number = item.get("no", "?")
    kind = item.get("kind")
    if kind not in {"quoted", "composed"}:
        problems.append(f"第 {number} 題 kind 是 {kind!r}，只能是 quoted 或 composed")
    if not (item.get("text") or "").strip():
        problems.append(f"第 {number} 題沒有原文")
    # A translation printed beside the exercise would answer it.  The Chinese
    # belongs to the reading, which is the model text; the exercise is the part
    # the learner does.  Only the reference is kept, so an answer booklet can be
    # set later from the published translation.
    if (item.get("chinese") or "").strip():
        problems.append(f"第 {number} 題印了中文，等於把答案印在題目旁邊")
    if kind == "quoted":
        if not (item.get("ref") or "").strip():
            problems.append(f"第 {number} 題是引用卻沒有出處")
        if not (item.get("answerKeyRef") or item.get("ref") or "").strip():
            problems.append(f"第 {number} 題沒有可據以編解答的出處")
    if kind == "composed" and item.get("reviewedBy") != "author":
        problems.append(f"第 {number} 題是自撰卻未經作者逐句複核")
    verification = item.get("verification") or {}
    if not verification.get("passed"):
        problems.append(f"第 {number} 題沒有通過語料驗證")
    # 只剩「語料中查無此形」是硬錯。超出本課進度的詞（verification.untaught）
    # 照記不照擋——擁有者 2026-09-16 裁定：簡單的詞可以先練，課次不是硬牆。
    offenders = verification.get("unattested") or []
    if offenders:
        problems.append(f"第 {number} 題語料中查無此形：{'、'.join(offenders)}")
    # 自撰題要練到本課的詞——那是它存在的理由。引錨不必：擁有者 2026-09-17
    # 「可以用前面的造句來補，選文就沒有一定要覆蓋」。讀文改成節錄之後，有幾課
    # 挑不出「既在書上印過、又含本課生詞」的原句，逼它兩者兼具只會把引錨換成
    # 讀者在書裡找不到的句子——那比練不到一個詞嚴重得多。
    if item.get("kind") != "quoted" and not (item.get("targetWords") or []):
        problems.append(f"第 {number} 題沒有標出練到的本課詞")
    return problems


def failures_for_lesson(lesson: dict[str, Any]) -> list[str]:
    """Rules about the lesson as a whole rather than any one item."""
    problems: list[str] = []
    number = lesson.get("lesson", "?")
    items = lesson.get("items") or []
    # 多於十題一律是錯；少於十題適用這一系列既有的原則：不足是允許的，不說明才
    # 不允許。拉丁下冊改節錄之後，第 42、48 課挑不出第三則「書上印過」的原句，
    # 自撰七題加起來只有九題。硬湊第十題的辦法只有兩種——引一句讀者在書裡找不到
    # 的話，或把已經用過的原句再印一次——兩種都比少一題糟。
    if len(items) > ITEMS_PER_LESSON:
        problems.append(f"第 {number} 課有 {len(items)} 題，多於 {ITEMS_PER_LESSON} 題")
    elif len(items) < ITEMS_PER_LESSON and not (lesson.get("note") or "").strip():
        problems.append(
            f"第 {number} 課只有 {len(items)} 題（應為 {ITEMS_PER_LESSON}），"
            "少於十題必須在 note 說明原因"
        )
    quoted = sum(1 for item in items if item.get("kind") == "quoted")
    if quoted < MIN_QUOTED_PER_LESSON and not (lesson.get("note") or "").strip():
        # The earliest lessons of every reader can run out of quotable text:
        # twenty nouns and no verb leave nothing in the corpus that uses only
        # them.  Falling short is allowed, saying nothing about it is not.
        problems.append(
            f"第 {number} 課只有 {quoted} 題引用經典原句，少於 {MIN_QUOTED_PER_LESSON} 題時必須在 note 說明原因"
        )
    coverage = lesson.get("coverage") or {}
    missing = coverage.get("notPractised") or []
    if missing and coverage_ratio(coverage) < MIN_COVERAGE:
        names = "、".join(
            str(row.get("pointed") or row.get("headword") or row) for row in missing
        )
        problems.append(
            f"第 {number} 課只練到 {coverage_ratio(coverage):.0%} 的本課詞"
            f"（低於 {MIN_COVERAGE:.0%}），沒練到的有 {len(missing)} 個：{names}"
        )
    # A word with no attested form cannot be practised by a sentence whose every
    # form must be attested: gate one and gate three contradict each other for
    # it, and no sentence can satisfy both.  Latin has thirty such words out of
    # two thousand -- Kyrie, eléison, tellus, the month names -- because its
    # vocabulary comes from a textbook and its corpus from the Vulgate, which is
    # not the book the textbook teaches out of.  Falling short is allowed here
    # for the same reason it is allowed for the anchors: saying nothing is not.
    unattested_words = coverage.get("notAttested") or []
    if unattested_words and not (lesson.get("note") or "").strip():
        names = "、".join(
            str(row.get("pointed") or row.get("headword") or row) for row in unattested_words
        )
        problems.append(
            f"第 {number} 課有 {len(unattested_words)} 個詞在本冊語料中無任何字形"
            f"（{names}），必須在 note 說明"
        )
    # 全覆蓋不再是硬性要求，見 MIN_COVERAGE。
    for item in items:
        problems.extend(failures_for_item(item))
    return problems


MIN_COVERAGE = 0.50
"""十題至少要練到本課多少比例的生詞。

擁有者 2026-09-17：「覆蓋率下降沒關係，有到 50-75% 就好。」

本來要求二十個字一個不漏。教父讀文改成節錄之後這一條就跟自己打架了：生詞是從
讀文選出來的，讀文砍掉一半，有些字在讀本裡根本不再出現，十題再怎麼挑也練不到。
放寬之後實測希臘下冊五十課全部落在 85–100%，離下限還很遠——真正掉到 50% 以下
才值得攔。
"""


def coverage_ratio(coverage: dict) -> float:
    """練到的比例；語料中無任何字形的詞不算在分母裡（那是閘一與閘三的矛盾）。"""
    total = coverage.get("lessonWords")
    practised = coverage.get("practised")
    if not total:
        return 1.0
    unattested = len(coverage.get("notAttested") or [])
    denominator = max(1, total - unattested)
    return min(1.0, (practised or 0) / denominator)


def failures_for_payload(payload: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if payload.get("direction") != "original-to-chinese":
        problems.append("direction 必須是 original-to-chinese：本系列不做中譯原文")
    if payload.get("itemsPerLesson") != ITEMS_PER_LESSON:
        problems.append(f"itemsPerLesson 應為 {ITEMS_PER_LESSON}")
    lessons = payload.get("lessons") or []
    if not lessons:
        problems.append("沒有任何課次")
    seen: set[int] = set()
    for lesson in lessons:
        number = lesson.get("lesson")
        if number in seen:
            problems.append(f"第 {number} 課重複出現")
        seen.add(number)
        problems.extend(failures_for_lesson(lesson))
    return problems


def report(problems: Iterable[str], *, label: str) -> int:
    problems = list(problems)
    if not problems:
        print(f"{label}：全綠")
        return 0
    print(f"{label}：{len(problems)} 項不合格")
    for problem in problems[:60]:
        print(f"  - {problem}")
    if len(problems) > 60:
        print(f"  …另有 {len(problems) - 60} 項")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="+", help="exercises.json files")
    args = parser.parse_args()
    worst = 0
    for path in args.path:
        payload = json.loads(path.read_text(encoding="utf-8"))
        worst |= report(failures_for_payload(payload), label=path.name)
    return worst


if __name__ == "__main__":
    sys.exit(main())
