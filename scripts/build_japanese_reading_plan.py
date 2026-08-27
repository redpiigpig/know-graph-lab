#!/usr/bin/env python3
"""Choose the hundred readings of the Japanese reader, and say why each was chosen.

The contract fixes what these have to be: every lesson reads one piece, the
pieces are religious studies or religious history, 第一冊 reads modern-orthography
Japanese and 第二冊 reads the pre-war writing this reader exists to open up —
文語, 舊字舊假名, 漢文訓讀.

Three constraints decide the list, and two of them exist because of what the
corpus actually turned out to be:

* **An author cap.** 折口信夫 alone is 234 of the 433 works. Taking the best
  scoring pieces would produce a folklore reader with a religious-studies title.
  No author may hold more than a sixth of either volume.
* **A subject score, not a subject guess.** A piece earns its place by how much
  religious-studies vocabulary it actually contains — 宗教, 信仰, 祭, 神道, 佛,
  基督, 聖書, 儀禮, 巫 and the rest — measured per thousand characters so a long
  work does not out-score a dense short one.
* **A complete piece, or nothing.** A reading is a whole work, or a whole
  numbered section of one. Anything too long for a lesson is cut at its own
  divisions and the extent is recorded (「全五節之第一節」), never at a word count.
  Works with no internal divisions and over the ceiling are simply not eligible.

Nothing here is written to the master; this produces the plan for review, which
is the step the other three readers each had.

    python -X utf8 scripts/build_japanese_reading_plan.py
    python -X utf8 scripts/build_japanese_reading_plan.py --write
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
MANIFEST = CACHE / "aozora/manifest.json"
PLAN = CACHE / "reading-plan.json"

PER_VOLUME = 50
MIN_CHARS, MAX_CHARS = 400, 4000
AUTHOR_CAP = PER_VOLUME // 6

# 宗教學與宗教史的用語。分數是「每千字命中次數」，長文不會因為長而勝出。
SUBJECT = re.compile(
    "宗教|信仰|神道|神社|神話|祭|祝詞|巫|霊魂|靈魂|他界|仏教|佛教|禅|禪|念仏|念佛|"
    "経典|經典|浄土|淨土|基督|耶蘇|聖書|教会|教會|福音|宣教|司祭|牧師|"
    "儀礼|儀禮|供犠|供犧|呪|穢|禊|斎|齋|神学|神學|教義|信条|信條|"
    "民間信仰|習合|廃仏|廢佛|巡礼|巡禮|修行|悟|涅槃|因果|輪廻|輪迴"
)

# 舊字舊假名／新字舊假名是第二冊要的；新字新假名是第一冊。
MODERN = {"新字新仮名"}


def divisions(text: str) -> list[tuple[str, str]]:
    """The work's own sections, if it prints any.

    青空文庫 marks a section as a line that is short, standalone and often a
    number or a bare noun. Only two shapes are trusted: a numbered heading
    （一、二、三 or 1 2 3）and a line wrapped in 「」-free 〔〕. Everything else
    is treated as having no divisions, because guessing a division and cutting
    there is how a reading ends up starting mid-argument.
    """

    pattern = re.compile(r"^\s*(?:[一二三四五六七八九十]+|[0-9]{1,2})\s*$", re.M)
    marks = [m.start() for m in pattern.finditer(text)]
    if len(marks) < 2:
        return []
    spans = []
    for index, start in enumerate(marks):
        end = marks[index + 1] if index + 1 < len(marks) else len(text)
        label = text[start:end].strip().split("\n")[0].strip()
        body = text[start:end].strip()
        if len(body) >= MIN_CHARS:
            spans.append((label, body))
    return spans


def score(text: str) -> float:
    if not text:
        return 0.0
    return len(SUBJECT.findall(text)) * 1000 / len(text)


def candidates() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for work_id, item in manifest.items():
        text = (ROOT / item["file"]).read_text(encoding="utf-8")
        density = score(text)
        if density < 1.0:
            continue
        whole_ok = MIN_CHARS <= len(text) <= MAX_CHARS
        parts = [] if whole_ok else divisions(text)
        if whole_ok:
            rows.append(
                {
                    "workId": work_id,
                    "title": item["title"],
                    "author": item["author"],
                    "orthography": item["orthography"],
                    "extent": "全文",
                    "chars": len(text),
                    "score": round(density, 2),
                    "sourceUrl": item["sourceUrl"],
                }
            )
            continue
        for label, body in parts:
            if not (MIN_CHARS <= len(body) <= MAX_CHARS):
                continue
            rows.append(
                {
                    "workId": work_id,
                    "title": item["title"],
                    "author": item["author"],
                    "orthography": item["orthography"],
                    "extent": f"第 {label} 節（完整，共 {len(parts)} 節）",
                    "chars": len(body),
                    "score": round(score(body), 2),
                    "sourceUrl": item["sourceUrl"],
                }
            )
    return sorted(rows, key=lambda r: -r["score"])


def pick(rows: list[dict], modern: bool) -> list[dict]:
    wanted = [r for r in rows if (r["orthography"] in MODERN) == modern]
    chosen: list[dict] = []
    per_author: dict[str, int] = {}
    used_works: set[str] = set()
    for row in wanted:
        if len(chosen) >= PER_VOLUME:
            break
        if per_author.get(row["author"], 0) >= AUTHOR_CAP:
            continue
        # 同一篇作品不重複入選，即使它有好幾節夠格。
        if row["workId"] in used_works:
            continue
        chosen.append(row)
        used_works.add(row["workId"])
        per_author[row["author"]] = per_author.get(row["author"], 0) + 1
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = candidates()
    print(f"合格候選 {len(rows)} 筆（宗教學用語密度 ≥1／千字，長度 {MIN_CHARS}–{MAX_CHARS} 字）")

    first = pick(rows, modern=True)
    second = pick(rows, modern=False)
    for label, chosen in (("第一冊・現代語", first), ("第二冊・文語舊假名", second)):
        by_author: dict[str, int] = {}
        for row in chosen:
            by_author[row["author"]] = by_author.get(row["author"], 0) + 1
        print(f"\n{label}：選出 {len(chosen)}／{PER_VOLUME}（每位作者上限 {AUTHOR_CAP}）")
        print("  " + "、".join(f"{a} {c}" for a, c in sorted(by_author.items(), key=lambda kv: -kv[1])))
        for row in chosen[:8]:
            print(f'    {row["score"]:>5.1f}／千字  {row["author"]}〈{row["title"]}〉{row["extent"]}  {row["chars"]} 字')
        if len(chosen) < PER_VOLUME:
            print(f"  ⚠ 差 {PER_VOLUME - len(chosen)} 篇。候選不足或被作者上限擋住，"
                  f"要補來源（姉崎正治、文語訳聖書、佛典訓讀）再跑一次。")

    if not args.write:
        print("\n（未寫入；加 --write）")
        return 0

    PLAN.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "note": "日文讀本讀文計畫（待人工覆核）。分數＝宗教學用語每千字命中次數。",
                "rules": {
                    "perVolume": PER_VOLUME,
                    "authorCap": AUTHOR_CAP,
                    "charRange": [MIN_CHARS, MAX_CHARS],
                    "completeness": "整篇或整節，不以字數截斷",
                },
                "volumes": [
                    {"volume": 1, "register": "現代語（新字新仮名）", "readings": first},
                    {"volume": 2, "register": "文語・舊字舊假名", "readings": second},
                ],
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\n已寫入 {PLAN.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
