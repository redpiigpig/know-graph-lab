#!/usr/bin/env python3
"""Gate the Latin reader's data master against its frozen contract.

Every check here exists because the corresponding mistake is easy to make and
invisible afterwards.  A lesson quietly holding nineteen words, a name that
slipped into a lesson slot and is therefore taught twice, a chapter whose Chinese
never arrived, a reading called complete that is really an excerpt: none of these
announce themselves in a JSON file, and all of them would reach print.

Run it before layout, and after any change to vocabulary, plan, or appendix.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-appendices.json"
SCRIPTURE = CACHE / "scripture-plan.json"
CHURCH = CACHE / "church-plan.json"
SIGAO = CACHE / "sigao-zh.json"
MEMORY = CACHE / "memory-units.json"

LESSONS = 50
PER_LESSON = 20


def load(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    vocab = load(VOCABULARY)
    if vocab is None:
        failures.append("詞表未產生")
    else:
        entries = vocab["entries"]
        for volume in ("上冊", "下冊"):
            rows = [e for e in entries if e["volume"] == volume]
            if len(rows) != LESSONS * PER_LESSON:
                failures.append(f"{volume} 有 {len(rows)} 詞，契約要求 {LESSONS * PER_LESSON}")
            sizes = Counter(e["lesson"] for e in rows)
            odd = {lesson: n for lesson, n in sizes.items() if n != PER_LESSON}
            if odd:
                failures.append(f"{volume} 課次字數不是 {PER_LESSON}：{dict(list(odd.items())[:5])}")
            if rows and sorted(sizes) != list(range(1, LESSONS + 1)):
                failures.append(f"{volume} 課次不是 1..{LESSONS}")

        # Compare whole dictionary lines, not headwords.  Latin homographs that
        # only a macron separates are separate lexemes the contract preserves --
        # occīdō "kill" beside occidō "set" -- and a headword-only comparison
        # reports every one of them as a duplicate.
        lines = [L.fold(e.get("forms") or e["headword"]) for e in entries]
        duplicates = [line for line, n in Counter(lines).items() if n > 1]
        if duplicates:
            failures.append(f"重複詞條 {len(duplicates)}：{duplicates[:8]}")

        blank = [e["headword"] for e in entries if not (e.get("forms") or "").strip()]
        if blank:
            failures.append(f"{len(blank)} 條沒有詞形：{blank[:6]}")

        unattested = [e["headword"] for e in entries if e.get("attested") is False]
        if unattested:
            warnings.append(f"{len(unattested)} 條語料與字典皆無佐證，待人工覆核："
                            f"{', '.join(unattested[:6])}")

        no_gloss = [e["headword"] for e in entries if not (e.get("glossZh") or "").strip()]
        if no_gloss:
            warnings.append(f"{len(no_gloss)} 條尚無繁中釋義")

        # Capitalisation is not the test.  Collins capitalises Deus, the
        # nationality adjectives and the liturgical nouns, and all of those are
        # vocabulary.  The invariant is that lessons and the name appendix do
        # not overlap, which is checked against the appendix below.

    appendices = load(APPENDICES)
    if appendices is None:
        failures.append("附錄未產生")
    elif vocab is not None:
        taught = {L.fold(e["headword"]) for e in vocab["entries"]}
        names = {row["folded"] for row in appendices["upper"]["names"]["entries"]}
        overlap = taught & names
        if overlap:
            failures.append(f"專名同時佔了課次詞位 {len(overlap)}：{sorted(overlap)[:8]}")
        resolved = sum(1 for r in appendices["upper"]["names"]["entries"] if r["zh"])
        total = len(appendices["upper"]["names"]["entries"])
        warnings.append(f"聖經專名中文 {resolved}/{total}")

    scripture = load(SCRIPTURE)
    if scripture is None:
        failures.append("上冊讀本計畫未產生")
    else:
        if len(scripture["chapters"]) != LESSONS:
            failures.append(f"上冊讀本 {len(scripture['chapters'])} 章，應為 {LESSONS}")
        halves = Counter(row["corpus"] for row in scripture["chapters"])
        if set(halves.values()) != {25}:
            failures.append(f"上冊兩半不是各 25 章：{dict(halves)}")

    chinese = load(SIGAO)
    if chinese is None:
        failures.append("上冊中文未匯出")
    elif scripture is not None:
        # Key on the chapter, not the lesson: lesson numbers come from the
        # difficulty sort and move whenever the vocabulary changes, so a check
        # written against them passes while the two files disagree about which
        # chapter a lesson is.
        got = {(row["book"], row["latinChapter"]) for row in chinese["chapters"]}
        missing = {(row["book"], row["chapter"]) for row in scripture["chapters"]} - got
        if missing:
            failures.append(f"這些章沒有中文：{sorted(missing)}")
        stale = [c["title"] for c in chinese["chapters"]
                 if c["lesson"] != next((r["lesson"] for r in scripture["chapters"]
                                         if r["book"] == c["book"]
                                         and r["chapter"] == c["latinChapter"]), None)]
        if stale:
            warnings.append(f"{len(stale)} 章的中文檔課次編號已過期，重跑匯出即可")
        mismatched = [c["title"] for c in chinese["chapters"] if c["alignmentNote"]]
        if mismatched:
            warnings.append(f"{len(mismatched)} 章節數與拉丁不一致（已逐章記錄）")

    church = load(CHURCH)
    if church is None:
        failures.append("下冊讀本計畫未產生")
    else:
        readings = church["readings"]
        if len(readings) != LESSONS:
            failures.append(f"下冊讀本 {len(readings)} 篇，應為 {LESSONS}")
        unlabelled = [r["title"] for r in readings if r["extent"] not in {"complete", "excerpt"}]
        if unlabelled:
            failures.append(f"未標完整／節錄：{unlabelled[:5]}")
        pending = [r["title"] for r in readings if r["chineseParallel"] != "repo-existing"]
        if pending:
            warnings.append(f"下冊 {len(pending)} 篇尚無中譯，需自譯並標記")
        if church["terminalSection"]["status"] != "ready":
            warnings.append(f"終卷《{church['terminalSection']['title']}》"
                            f"狀態 {church['terminalSection']['status']}")

    memory = load(MEMORY)
    if memory is None:
        warnings.append("記憶單元尚未產生")
    else:
        for volume in ("上冊", "下冊"):
            rows = memory[volume]
            sizes = Counter(r["lesson"] for r in rows)
            short = [l for l in range(1, LESSONS + 1) if sizes.get(l, 0) < memory["perLesson"]]
            if short:
                warnings.append(f"{volume} 記憶單元 {len(rows)}/{LESSONS * memory['perLesson']}；"
                                f"不足的課 {short[:10]}")
            over = [l for l, n in sizes.items() if n > memory["perLesson"]]
            if over:
                failures.append(f"{volume} 有課超過每課 {memory['perLesson']} 句：{over[:5]}")

    for note in warnings:
        print(f"[注意] {note}")
    for note in failures:
        print(f"[失敗] {note}")
    if failures:
        print(f"\n{len(failures)} 項未過，{len(warnings)} 項待辦")
        return 1
    print(f"\n全部硬性檢查通過；{len(warnings)} 項待辦")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
