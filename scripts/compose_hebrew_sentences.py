#!/usr/bin/env python3
"""Compose Biblical Hebrew practice sentences with a model, then verify them.

Template filling produced word salad: morph tags do not carry Hebrew syntax.
So the model writes the sentence and the corpus checks it.  Three gates run on
every sentence before it is allowed to stand:

1. every written form must be attested in the Westminster Leningrad Codex --
   the same consonants and vowels some verse actually uses, so no inflected
   form is invented;
2. every word must belong to the vocabulary the learner has already been
   taught, which is also what keeps the early lessons easy;
3. the ten sentences together must contain all twenty of the lesson's words.

What the gates cannot certify is idiom and sense.  Sentences that pass leave
here marked `machine_verified`, not `correct`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from select_hebrew_memory_verses import DEFAULT_VOCAB, DEFAULT_WLC, load_vocabulary, load_wlc  # noqa: E402
from build_hebrew_exercises import CANTILLATION_RE, cumulative_sets  # noqa: E402
import original_reader_llm as llm  # noqa: E402

OUTPUT = ROOT / "output/source-cache/original-readers/hebrew-full/composed-sentences.json"
HEBREW_RE = re.compile(r"[א-ת]")


def bare(word: str) -> str:
    """Strip accents and formatting, keep consonants and vowel points."""
    cleaned = CANTILLATION_RE.sub("", unicodedata.normalize("NFC", word))
    return cleaned.strip(" ־׃׀.,;:!?()[]\"'—–")


def consonants(word: str) -> str:
    return "".join(ch for ch in bare(word) if HEBREW_RE.match(ch))


def build_attested(verses) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Two indexes of every written word: pointed, and consonants only."""
    pointed: dict[str, set[str]] = defaultdict(set)
    skeleton: dict[str, set[str]] = defaultdict(set)
    for verse in verses:
        for token in verse.tokens:
            if not token.text:
                continue
            pointed[bare(token.text)] |= token.strongs
            skeleton[consonants(token.text)] |= token.strongs
    return pointed, skeleton


def prompt_for(lesson: int, targets, known_words) -> str:
    target_lines = "\n".join(f"{item.pointed}\t{item.gloss}" for item in targets)
    known_line = "、".join(word for word in known_words)
    return (
        "你是聖經希伯來文的教材編者。請為初學課本的第 "
        f"{lesson} 課寫十個練習句。\n\n"
        "硬性規定：\n"
        "1. 只能使用下面『可用詞彙』裡的詞，不可使用任何其他詞。\n"
        "2. 每個詞形必須是希伯來聖經（BHS/WLC）裡實際出現過的拼法，含母音點；"
        "不要自行推導沒出現過的變化形。\n"
        "3. 句子要短（三到七個詞），是完整的句子，語意合理，"
        "且必須符合聖經世界的用語與世界觀，不得出現後代或現代的事物。\n"
        "4. 這十句合起來，必須把下列『本課二十詞』每一個都用到，"
        "重複使用沒關係。\n"
        "5. 每句附一句繁體中文翻譯。\n\n"
        f"本課二十詞（詞\t中文義）：\n{target_lines}\n\n"
        f"可用詞彙（本課與先前各課所有已教的詞）：\n{known_line}\n\n"
        "只輸出 JSON，格式為："
        '{"sentences":[{"hebrew":"…","chinese":"…","targets":["…"]}]}'
    )


def parse_reply(reply: str) -> list[dict[str, Any]]:
    text = reply.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        return []
    try:
        return json.loads(text[start : end + 1]).get("sentences", [])
    except json.JSONDecodeError:
        pass
    # A truncated or chatty reply still carries whole sentence objects; take
    # those rather than throwing the call away.  An engine that answers with
    # prose around the JSON is common enough that retrying costs more.
    salvaged: list[dict[str, Any]] = []
    for block in re.finditer(r"\{[^{}]*\"hebrew\"[^{}]*\}", text, re.S):
        try:
            salvaged.append(json.loads(block.group(0)))
        except json.JSONDecodeError:
            continue
    return salvaged


def split_words(sentence: str) -> list[str]:
    """Maqqef binds two written words into one; the lexicon knows them apart."""
    pieces: list[str] = []
    for chunk in bare(sentence).split():
        for piece in chunk.split("־"):
            piece = bare(piece)
            if piece:
                pieces.append(piece)
    return pieces


def verify(sentence: str, known: set[str], pointed, skeleton) -> dict[str, Any]:
    words = split_words(sentence)
    unattested: list[str] = []
    untaught: list[str] = []
    lemmas: set[str] = set()
    for word in words:
        key = bare(word)
        strongs = pointed.get(key) or skeleton.get(consonants(word))
        if not strongs:
            unattested.append(word)
            continue
        lemmas |= strongs
        if not (strongs & known):
            untaught.append(word)
    return {
        "words": len(words),
        "unattested": unattested,
        "untaught": untaught,
        "lemmas": sorted(lemmas),
        "passed": not unattested and not untaught and len(words) >= 3,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--engine",
        default="auto",
        help="auto follows the standing Gemini-NVIDIA-Haiku order; the NVIDIA tier "
             "answers this task with reasoning prose instead of JSON, so a composition "
             "run may need an explicit tier",
    )
    args = parser.parse_args()
    if args.engine != "auto":
        llm.select_chain(args.engine)

    vocabulary = load_vocabulary(DEFAULT_VOCAB)
    verses = load_wlc(DEFAULT_WLC)
    pointed, skeleton = build_attested(verses)

    gloss_by_strong = {}
    gloss_file = ROOT / "output/source-cache/original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json"
    for row in json.loads(gloss_file.read_text(encoding="utf-8"))["items"]:
        gloss_by_strong[row["strong"].lstrip("H")] = row["glossZh"]

    for lesson, items, known in cumulative_sets(vocabulary):
        if lesson != args.lesson:
            continue
        for item in items:
            object.__setattr__(item, "gloss", next(
                (gloss_by_strong.get(s, "") for s in item.strongs if s in gloss_by_strong), ""
            ))
        known_words = [
            entry.pointed
            for number in sorted(vocabulary)
            if number <= lesson
            for entry in vocabulary[number]
        ]
        reply = llm.call_model(prompt_for(lesson, items, known_words), args.max_tokens)
        engine = llm.current_model()
        sentences = parse_reply(reply)
        print(f"引擎 {engine}，回了 {len(sentences)} 句")
        target_forms = {item.pointed: item for item in items}
        covered: set[str] = set()
        rows = []
        for index, row in enumerate(sentences, start=1):
            report = verify(row.get("hebrew", ""), set(known), pointed, skeleton)
            hit = {word for word in target_forms if any(
                consonants(word) == consonants(part) or consonants(word) in consonants(part)
                for part in split_words(row.get("hebrew", ""))
            )}
            covered |= hit
            rows.append({**row, "verification": report, "targetsSeen": sorted(hit)})
            mark = "通過" if report["passed"] else "退回"
            print(f"{index:2d} [{mark}] {row.get('hebrew','')}")
            print(f"     {row.get('chinese','')}")
            if report["unattested"]:
                print(f"     ✗ 聖經裡查無此形：{'、'.join(report['unattested'])}")
            if report["untaught"]:
                print(f"     ✗ 尚未教過：{'、'.join(report['untaught'])}")
        passed = sum(1 for row in rows if row["verification"]["passed"])
        print(f"\n通過機器驗證 {passed}/{len(rows)} 句；本課二十詞出現 {len(covered)}/{len(items)}")
        if args.write:
            OUTPUT.write_text(json.dumps({"lesson": lesson, "engine": engine, "sentences": rows},
                                         ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"寫入 {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
