#!/usr/bin/env python3
"""替通用希臘文讀本挖「引用題」——每課十題翻譯練習裡定錨的那三題。

規格見 `skills/build-original-language-reader/references/exercise-sets.md`：
每課十題＝七題自撰＋三題經典原句。本檔只做原句那一種（`kind: "quoted"`），
自撰那一種由作者執筆、`compose_greek_sentences.py` 驗。

與希伯來版同一個作法：本檔供的是**候選定錨**，一課挖六句，印出來的是三句。
多挖是給組裝那一步留餘地——引用題的中文取既有譯本，沒有現成譯文的那幾句要能丟掉。
二十詞全覆蓋是自撰題與引用題合起來達成的，不是在這裡達成的。

挖的條件只有一條硬的：**全句每個詞都已教過**。沒有生字，不補腳註。
單位是語料自己的一節（新約、七十士）或一句（教父、教會文獻）；太長就依原文
自己的停頓（ἄνω τελεία 與句末標點）切出子句。逗號不切——切下來的是半句話。

詞位從哪來，決定這件事可不可靠：

* 新約走 MorphGNT，每個詞的詞位是編者標的，金標；
* 七十士與教父走 `build_greek_lemma_corpus.py` 產的 `lemma-corpus-*.json`，
  每個 token 都記了它的詞位是三層裡的哪一層決定的。
  預設**排除含 `surface-fold` token 的句子**：那一層等於「查不到，拿字形充數」，
  用它判「這個詞已經教過」等於拿猜的當已知。要看放寬後的數字加 `--allow-unresolved`。

中文不在這裡翻。引用題的中文取既有譯本，由後續步驟補上。

用法：

    PYTHONIOENCODING=utf-8 python scripts/build_greek_exercises.py --volume 1 --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_source_texts as gs  # noqa: E402
from build_greek_lemma_corpus import (  # noqa: E402
    CACHE,
    LAYER_SURFACE,
    OUTPUT as CORPUS_OUTPUT,
    ROOT,
    bare,
    crasis_components,
    fold_key,
    is_word,
)

READER = CACHE / "greek-reader-two-volumes.json"
EXERCISE_OUTPUT = {
    1: CACHE / "exercises-greek-vol1.json",
    2: CACHE / "exercises-greek-vol2.json",
}

CANDIDATES_PER_LESSON = 6
PRINTED_ANCHORS = 3
LESSON_COUNT = 50
MIN_WORDS = 3
MAX_WORDS = 12
HALF_LAST_LESSON = 25

LAYER_GOLD = "morphgnt-gold"

# ἄνω τελεία 與句末標點是原文自己的停頓；逗號不是，切在逗號上會得到半句話。
CLAUSE_SPLIT_RE = re.compile(r"(?<=[·;;.!:])\s+")
BRACKET_RE = re.compile(r"[\[\]⟨⟩⟦⟧⸀-⸏]")
DIGIT_RE = re.compile(r"\d")
# 收尾必須停在原文自己的停頓上。停在逗號的是半句：詩歌體一行一句印，
# 「καὶ Δεσπότην νοοῦντες αὐτόν,」的主要動詞在上一行。
# 這與 select_greek_memory_sentences.py 的 SENTENCE_END_RE 是同一條規矩。
PAUSE_END_RE = re.compile(r"[·;;.!?]\s*$")

# 神名不計入專名扣分：它們在這批語料裡是常詞，不是敘事裡的人名地名。
DIVINE_KEYS = {
    fold_key(name)
    for name in (
        "θεός", "θεοῦ", "θεῷ", "θεόν", "κύριος", "κυρίου", "κυρίῳ", "κύριον", "κύριε",
        "χριστός", "χριστοῦ", "χριστῷ", "χριστόν", "Ἰησοῦς", "Ἰησοῦ", "Ἰησοῦν",
        "πνεῦμα", "πνεύματος", "πνεύματι", "πατήρ", "πατρός", "πατρί", "πατέρα",
        "υἱός", "υἱοῦ", "υἱῷ", "υἱόν",
    )
}


# --------------------------------------------------------------------------
# 詞表
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class VocabItem:
    volume: int
    lesson: int
    slot: int
    ordinal: int
    headword: str
    lemma: str
    gloss_zh: str
    pos: str

    @property
    def keys(self) -> frozenset[str]:
        """這個生字認得的詞位鍵：詞條形與詞位形各折一次。"""
        return frozenset(key for key in (fold_key(self.lemma), fold_key(self.headword)) if key)

    def public_record(self) -> dict[str, Any]:
        return {
            "volume": self.volume,
            "lesson": self.lesson,
            "slot": self.slot,
            "ordinal": self.ordinal,
            "headword": self.headword,
            "lemma": self.lemma,
            "glossZh": self.gloss_zh,
            "pos": self.pos,
        }


def load_vocabulary(path: Path = READER) -> dict[int, dict[int, list[VocabItem]]]:
    """讀本詞表：{冊: {課: [二十個生字]}}。"""
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: dict[int, dict[int, list[VocabItem]]] = {}
    for volume in payload["volumes"]:
        number = volume["volume"]
        lessons: dict[int, list[VocabItem]] = {}
        for lesson in volume["lessons"]:
            lessons[lesson["lesson"]] = [
                VocabItem(
                    volume=number,
                    lesson=lesson["lesson"],
                    slot=entry.get("slot") or entry.get("lessonSlot") or 0,
                    ordinal=entry.get("ordinal", 0),
                    headword=entry.get("headword", ""),
                    lemma=entry.get("lemma", ""),
                    gloss_zh=entry.get("glossZh", ""),
                    pos=entry.get("pos", ""),
                )
                for entry in lesson["vocabulary"]
            ]
        out[number] = lessons
    return out


def cumulative_sets(
    vocabulary: dict[int, dict[int, list[VocabItem]]], volume: int
) -> list[tuple[int, list[VocabItem], set[str]]]:
    """每課的（課次、本課二十詞、到這一課為止教過的所有詞位鍵）。

    下冊接在上冊後面：讀下冊第一課的人已經學過上冊一千詞，所以 `known` 從
    前面各冊的全部生字起算。這一條是本檔的設計判斷，未經作者裁定。
    """
    known: set[str] = set()
    for earlier in sorted(vocabulary):
        if earlier >= volume:
            break
        for lesson in sorted(vocabulary[earlier]):
            for item in vocabulary[earlier][lesson]:
                known |= item.keys
    rows: list[tuple[int, list[VocabItem], set[str]]] = []
    for lesson in sorted(vocabulary[volume]):
        items = vocabulary[volume][lesson]
        for item in items:
            known |= item.keys
        rows.append((lesson, items, set(known)))
    return rows


# --------------------------------------------------------------------------
# 語料
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class CorpusUnit:
    """語料的一個單位：一節（聖經）或一句（教父、教會文獻）。"""

    ref: str
    corpus: str
    source: str
    book: str
    text: str
    tokens: tuple[tuple[str, str, str], ...]  # (字形, 詞位, 決定它的那一層)
    lesson: int | None = None

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(fold_key(lemma) for _, lemma, _ in self.tokens if lemma)

    @property
    def word_count(self) -> int:
        return len(self.tokens)


def nt_units() -> Iterator[CorpusUnit]:
    """新約走 MorphGNT：詞位是編者標的，不經三層解析。"""
    for book in gs.SBLGNT_BOOKS:
        path = gs.sblgnt_path(book)
        if not path.exists():
            continue
        grouped: dict[str, list[tuple[str, str, str]]] = {}
        order: list[str] = []
        printed: dict[str, list[str]] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) != 7:
                continue
            code, _pos, _parsing, text, word, _normalized, lemma = parts
            ref = f"{book}.{int(code[2:4])}.{int(code[4:6])}"
            if ref not in grouped:
                grouped[ref] = []
                printed[ref] = []
                order.append(ref)
            grouped[ref].append(
                (bare(word), unicodedata.normalize("NFC", lemma), LAYER_GOLD)
            )
            printed[ref].append(unicodedata.normalize("NFC", text))
        for ref in order:
            yield CorpusUnit(
                ref=ref,
                corpus="new-testament",
                source="sblgnt",
                book=ref.split(".", 1)[0],
                text=" ".join(printed[ref]),
                tokens=tuple(grouped[ref]),
            )


def tagged_units(corpus: str) -> Iterator[CorpusUnit]:
    """七十士與教父：讀 build_greek_lemma_corpus.py 產出的詞位標記語料。"""
    path = CORPUS_OUTPUT[corpus]
    if not path.exists():
        raise FileNotFoundError(
            f"缺少 {path.name}；先跑 build_greek_lemma_corpus.py --corpus {corpus} --write"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    for unit in payload["units"]:
        yield CorpusUnit(
            ref=unit["ref"],
            corpus=corpus,
            source=unit.get("source", corpus),
            book=unit.get("book", ""),
            text=unit["text"],
            tokens=tuple((row[0], row[1], row[2]) for row in unit["tokens"]),
            lesson=unit.get("lesson"),
        )


VOLUME_CORPORA = {
    1: ("new-testament", "septuagint"),
    2: ("new-testament", "septuagint", "patristic"),
}

# 哪一半的課用哪一批語料，與讀本的半冊規則一致。
VOLUME_HALVES = {
    1: {"first": "new-testament", "second": "septuagint"},
    2: {"first": "patristic", "second": "patristic"},
}


def load_units(names: Sequence[str]) -> list[CorpusUnit]:
    units: list[CorpusUnit] = []
    for name in names:
        units.extend(nt_units() if name == "new-testament" else tagged_units(name))
    return units


# --------------------------------------------------------------------------
# 切子句與可讀性
# --------------------------------------------------------------------------

def split_clauses(unit: CorpusUnit) -> list[CorpusUnit]:
    """依原文自己的停頓切子句，印出來的字一個都不改。

    切完之後把 token 重新對回去是逐詞走的：子句裡有幾個詞就取幾個 token。
    對不齊就整個單位不切——寧可少一個候選，也不要印出一句原文沒有的話。
    """
    pieces = [part.strip() for part in CLAUSE_SPLIT_RE.split(unit.text) if part.strip()]
    if len(pieces) < 2:
        return []
    cursor = 0
    out: list[CorpusUnit] = []
    for index, piece in enumerate(pieces, start=1):
        count = sum(1 for chunk in piece.split() if is_word(chunk))
        if not count:
            continue
        taken = unit.tokens[cursor : cursor + count]
        cursor += count
        if len(taken) != count:
            return []
        out.append(
            CorpusUnit(
                ref=f"{unit.ref}~{index}",
                corpus=unit.corpus,
                source=unit.source,
                book=unit.book,
                text=piece,
                tokens=taken,
                lesson=unit.lesson,
            )
        )
    if cursor != unit.word_count:
        return []
    return out


def printable_reason(unit: CorpusUnit) -> str | None:
    """挑不出題的理由，挑得出就回 None。"""
    if not (MIN_WORDS <= unit.word_count <= MAX_WORDS):
        return "長度不合"
    if DIGIT_RE.search(unit.text) or BRACKET_RE.search(unit.text):
        return "含校勘符號或數字"
    if not PAUSE_END_RE.search(unit.text):
        return "沒有停在原文的停頓上"
    lemma_counts = Counter(key for key in (fold_key(lemma) for _, lemma, _ in unit.tokens) if key)
    if len(lemma_counts) < 3:
        return "實詞太少"
    if max(lemma_counts.values()) >= 3:
        return "重複用詞"
    words = [chunk for chunk in unit.text.split() if is_word(chunk)]
    proper = 0
    for position, word in enumerate(words):
        stripped = bare(word)
        if not position or not stripped:
            continue
        if stripped[:1].isupper() and stripped.upper() != stripped:
            if fold_key(stripped) not in DIVINE_KEYS:
                proper += 1
    if proper >= 3:
        return "專名列舉"
    return None


def readable(unit: CorpusUnit, known: set[str], allow_unresolved: bool) -> bool:
    """全句每個詞都已教過，而且每個詞的詞位不是猜的。"""
    for form, lemma, layer in unit.tokens:
        if layer == LAYER_SURFACE and not allow_unresolved:
            return False
        key = fold_key(lemma) if lemma else ""
        if key and key in known:
            continue
        components = crasis_components(form)
        if components and all(fold_key(part) in known for part in components):
            continue
        return False
    return True


def build_candidates(
    units: Iterable[CorpusUnit],
) -> tuple[list[CorpusUnit], Counter[str]]:
    pool: list[CorpusUnit] = []
    rejected: Counter[str] = Counter()
    for unit in units:
        reason = printable_reason(unit)
        if reason is None:
            pool.append(unit)
        else:
            rejected[reason] += 1
        if unit.word_count > MAX_WORDS:
            for clause in split_clauses(unit):
                clause_reason = printable_reason(clause)
                if clause_reason is None:
                    pool.append(clause)
                else:
                    rejected[clause_reason] += 1
    return pool, rejected


# --------------------------------------------------------------------------
# 選題
# --------------------------------------------------------------------------

@dataclass
class Scored:
    unit: CorpusUnit
    targets: list[VocabItem] = field(default_factory=list)


def lesson_corpus(volume: int, lesson: int) -> str:
    halves = VOLUME_HALVES[volume]
    return halves["first"] if lesson <= HALF_LAST_LESSON else halves["second"]


def select_for_lesson(
    lesson_items: Sequence[VocabItem],
    known: set[str],
    pool: Sequence[CorpusUnit],
    used_refs: set[str],
    preferred_corpus: str,
    allow_unresolved: bool,
    limit: int = CANDIDATES_PER_LESSON,
) -> tuple[list[Scored], list[VocabItem]]:
    by_key: dict[str, VocabItem] = {}
    for item in lesson_items:
        for key in item.keys:
            by_key.setdefault(key, item)
    candidates: list[Scored] = []
    for unit in pool:
        if unit.ref.split("~", 1)[0] in used_refs:
            continue
        hits = {by_key[key].ordinal: by_key[key] for key in unit.keys & set(by_key)}
        if not hits:
            continue
        if not readable(unit, known, allow_unresolved):
            continue
        candidates.append(Scored(unit=unit, targets=sorted(hits.values(), key=lambda row: row.slot)))

    chosen: list[Scored] = []
    remaining = {item.ordinal for item in lesson_items}
    seen_texts: set[str] = set()
    taken_roots: set[str] = set()
    while len(chosen) < limit and candidates:
        def rank(scored: Scored) -> tuple:
            fresh = len([item for item in scored.targets if item.ordinal in remaining])
            return (
                -fresh,
                0 if scored.unit.corpus == preferred_corpus else 1,
                0 if "~" not in scored.unit.ref else 1,
                abs(scored.unit.word_count - 6),
                scored.unit.ref,
            )

        candidates.sort(key=rank)
        best = candidates.pop(0)
        root = best.unit.ref.split("~", 1)[0]
        if root in taken_roots or best.unit.text in seen_texts:
            continue
        chosen.append(best)
        taken_roots.add(root)
        seen_texts.add(best.unit.text)
        remaining -= {item.ordinal for item in best.targets}
        candidates = [row for row in candidates if row.unit.ref.split("~", 1)[0] not in taken_roots]
    missed = [item for item in lesson_items if item.ordinal in remaining]
    return chosen, missed


def item_record(index: int, scored: Scored) -> dict[str, Any]:
    unit = scored.unit
    return {
        "no": index,
        "kind": "quoted",
        "uid": unit.ref,
        "ref": unit.ref.split("~", 1)[0],
        "clause": unit.ref.split("~", 1)[1] if "~" in unit.ref else None,
        "corpus": unit.corpus,
        "source": unit.source,
        "text": unit.text,
        "tokenCount": unit.word_count,
        "lemmaLayers": dict(Counter(layer for _, _, layer in unit.tokens)),
        "targetWords": [item.public_record() for item in scored.targets],
        "chinese": "",
        "chineseSource": "",
        "answerStatus": "pending_chinese",
        "reviewedBy": "machine",
    }


def build(volume: int, allow_unresolved: bool) -> dict[str, Any]:
    vocabulary = load_vocabulary()
    units = load_units(VOLUME_CORPORA[volume])
    pool, rejected = build_candidates(units)

    lessons_out: list[dict[str, Any]] = []
    used_refs: set[str] = set()
    total_words = 0
    total_practised = 0
    short: list[int] = []

    for lesson, items, known in cumulative_sets(vocabulary, volume):
        chosen, missed = select_for_lesson(
            items, known, pool, used_refs, lesson_corpus(volume, lesson), allow_unresolved
        )
        for scored in chosen:
            used_refs.add(scored.unit.ref.split("~", 1)[0])
        records = [item_record(index, scored) for index, scored in enumerate(chosen, start=1)]
        practised = len(items) - len(missed)
        total_words += len(items)
        total_practised += practised
        if len(records) < PRINTED_ANCHORS:
            short.append(lesson)
        lessons_out.append(
            {
                "lesson": lesson,
                "id": f"grc-v{volume}-lesson-{lesson:02d}",
                "corpus": lesson_corpus(volume, lesson),
                "items": records,
                "coverage": {
                    "lessonWords": len(items),
                    "practised": practised,
                    "notPractised": [item.public_record() for item in missed],
                },
            }
        )

    return {
        "schemaVersion": "1.0.0",
        "language": "Koine Greek",
        "languageCode": "grc",
        "volume": volume,
        "generatedOn": date.today().isoformat(),
        "direction": "original-to-chinese",
        "candidatesPerLesson": CANDIDATES_PER_LESSON,
        "printedAnchorsPerLesson": PRINTED_ANCHORS,
        "kind": "quoted-only",
        "policy": {
            "composition": "none",
            "note": "每題都是語料既有的一節或依原文停頓切出的子句；中文取既有譯本，本管線不翻譯。",
            "unknownWords": "不允許：題目中每個詞都必須已在本課或先前課教過。",
            "lemmaCertainty": (
                "允許 surface-fold 詞位" if allow_unresolved
                else "排除任何含 surface-fold 詞位的句子：那一層等於查不到"
            ),
        },
        "corpora": list(VOLUME_CORPORA[volume]),
        "counts": {
            "candidatePool": len(pool),
            "rejectedByReason": dict(rejected),
            "lessons": len(lessons_out),
            "items": sum(len(row["items"]) for row in lessons_out),
            "lessonWords": total_words,
            "practised": total_practised,
            "coverageRate": round(total_practised / total_words, 4) if total_words else 0.0,
            "lessonsShortOfAnchors": short,
        },
        "lessons": lessons_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="挖通用希臘文讀本的引用題")
    parser.add_argument("--volume", type=int, choices=[1, 2], default=1)
    parser.add_argument("--write", action="store_true", help="寫出 exercises-greek-vol*.json")
    parser.add_argument(
        "--allow-unresolved",
        action="store_true",
        help="連詞位只能靠折疊字形猜的句子也收，用來看放寬後的數字",
    )
    args = parser.parse_args()

    payload = build(args.volume, args.allow_unresolved)
    counts = payload["counts"]
    print(f"第 {args.volume} 冊：候選 {counts['candidatePool']} 句")
    print(f"  題目 {counts['items']} 題 / {counts['lessons']} 課")
    print(f"  本課字涵蓋 {counts['practised']}/{counts['lessonWords']}（{counts['coverageRate']:.1%}）")
    if counts["lessonsShortOfAnchors"]:
        print(f"  ⚠️ 連 {PRINTED_ANCHORS} 句定錨都湊不出的課：{counts['lessonsShortOfAnchors']}")
    for row in payload["lessons"][:3]:
        print(f"    L{row['lesson']:02d} {len(row['items'])} 題，練到 "
              f"{row['coverage']['practised']}/{row['coverage']['lessonWords']}")

    if args.write:
        path = EXERCISE_OUTPUT[args.volume]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  已寫出 {path.relative_to(ROOT)}")
    else:
        print("  （未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
