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


def failures_for_lesson(
    lesson: dict[str, Any],
    *,
    language_code: str | None = None,
    notices: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Rules about the lesson as a whole rather than any one item.

    `language_code` decides how a coverage gap is treated. Hebrew and Japanese
    (`FULL_COVERAGE_LANGUAGES`) have to cover all twenty lesson words -- a gap
    there is a hard failure appended to the returned list. Greek and Latin do
    not: their gaps are real and owner-accepted (see `FULL_COVERAGE_LANGUAGES`
    for the 2026-09-17 ruling this replaces), so a gap there is written to
    `notices` instead -- printed by `report()`, never blocking. `language_code`
    left unset (as every direct caller in `test_reader_exercises.py` does)
    keeps the strict behaviour, so those tests do not have to know about
    languages that do not exist for them.
    """
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
    if missing:
        names = "、".join(
            str(row.get("pointed") or row.get("headword") or row) for row in missing
        )
        if language_code is None or language_code in FULL_COVERAGE_LANGUAGES:
            problems.append(
                f"第 {number} 課只練到 {coverage_ratio(coverage):.0%} 的本課詞，"
                f"未達全覆蓋，沒練到的有 {len(missing)} 個：{names}"
            )
        elif notices is not None:
            notices.append({"lesson": number, "count": len(missing), "names": names})
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
    # 全覆蓋是不是硬性要求，看語言——見 FULL_COVERAGE_LANGUAGES。
    for item in items:
        problems.extend(failures_for_item(item))
    return problems


FULL_COVERAGE_LANGUAGES = {"hbo", "ja"}
"""哪些語言要求本課二十詞一個不漏（`languageCode`）。

本來全系列都要求二十個字一個不漏。教父讀文改成節錄之後這一條在希臘／拉丁跟自己
打架了：生詞是從讀文選出來的，讀文砍掉一半，有些字在讀本裡根本不再出現，十題
再怎麼挑也練不到——擁有者 2026-09-17 因此裁定「覆蓋率下降沒關係，有到 50-75%
就好」，一度改成比例門檻（`MIN_COVERAGE`，已移除）。2026-09-27 覆核發現這個
門檻在自撰題改寫後被兩冊都撞穿（希臘下冊從 37 課 59 詞退步到 44 課 86 詞），
而希伯來、日文並沒有教父讀文那個「讀文被砍」的理由，全覆蓋對它們仍然可行也仍然
是要求。於是拆成兩條路：希伯來／日文留在這個集合裡，任何缺口都是硬錯；希臘／
拉丁的缺口改成印出每課缺詞清單、在總結報數，不擋——`report()` 印 notices，
`failures_for_lesson` 不把它們放進 problems。
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


def failures_for_payload(
    payload: dict[str, Any], *, notices: list[dict[str, Any]] | None = None
) -> list[str]:
    problems: list[str] = []
    language_code = payload.get("languageCode")
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
        problems.extend(
            failures_for_lesson(lesson, language_code=language_code, notices=notices)
        )
    return problems


def report(
    problems: Iterable[str],
    *,
    label: str,
    notices: list[dict[str, Any]] | None = None,
) -> int:
    problems = list(problems)
    notices = list(notices or [])
    if not problems:
        print(f"{label}：全綠")
    else:
        print(f"{label}：{len(problems)} 項不合格")
        for problem in problems[:60]:
            print(f"  - {problem}")
        if len(problems) > 60:
            print(f"  …另有 {len(problems) - 60} 項")
    if notices:
        # 這裡的缺口不擋（見 FULL_COVERAGE_LANGUAGES）：印出每課缺詞，總結報總數，
        # 交給人看，不算進 exit code。
        total_missing = sum(notice["count"] for notice in notices)
        print(f"{label}：{len(notices)} 課有生詞缺口未練到，共 {total_missing} 個（不擋，見 FULL_COVERAGE_LANGUAGES）：")
        for notice in notices[:60]:
            print(f"  · 第 {notice['lesson']} 課沒練到 {notice['count']} 個：{notice['names']}")
        if len(notices) > 60:
            print(f"  …另有 {len(notices) - 60} 課")
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="+", help="exercises.json files")
    args = parser.parse_args()
    worst = 0
    for path in args.path:
        payload = json.loads(path.read_text(encoding="utf-8"))
        notices: list[dict[str, Any]] = []
        problems = failures_for_payload(payload, notices=notices)
        worst |= report(problems, label=path.name, notices=notices)
    return worst


if __name__ == "__main__":
    sys.exit(main())
