#!/usr/bin/env python3
"""Check hand-written Japanese practice sentences against the reader's corpus.

The Japanese counterpart of `compose_hebrew_sentences.py`.  The author writes
the seven composed items of a lesson; this runs the three machine gates the
exercise contract lays down (`references/exercise-sets.md`) and says which of
them each sentence fails:

1. **形必須有語料為證** — every content word's base form must actually occur in
   the reader's corpus (`lemma-corpus.json`);
2. **每個詞必須已教過** — every word must be in the lesson's cumulative
   vocabulary, or be one of the grammar words the reader itself teaches;
3. **十題合起來涵蓋本課二十詞** — reported per lesson.

There is no model in this script.  Composition is the author's job as of
2026-09-11 and the machine only checks; that also means no engine can quietly
turn a gate into a suggestion.

## 日文放寬了第一道閘：查基本形，不查表層形

希伯來那本要求**寫出來的那個形**在 WLC 裡出現過，母音點都要一樣，因為希伯來
的變化形不規則到無法安全推導，捏一個出來看不出破綻。日文不是這樣：現代日語的
活用是規則的，讀む→読みます→読んで→読まなければ 由辭書形機械地推得出來，而
語料再大也不可能把每個詞的每個活用形都收齊。照希伯來的規矩辦，「本を読みます」
會因為語料裡只出現過「読んだ」而被退回——正確的句子整批誤判，閘就廢了。

所以日文這一閘查的是**基本形（辭書形）在語料中出現過**。表層形有沒有出現過仍然
會算，但只印在 `unseenForms` 供作者參考，不構成退回理由。要靠這一閘擋住的是
「這個詞是不是真的存在、真的有人這樣用」，那一點基本形就答得了。

    python -X utf8 scripts/compose_japanese_sentences.py --lesson 13 --check draft.json

輸入檔長這樣（`volume` 省略時，`lesson` 直接用 1–100 的通編）：

    {"volume": 1, "lesson": 13, "author": "…",
     "sentences": [{"japanese": "…", "chinese": "…"}]}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_japanese_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_PATH,
    PUNCT_POS,
    Segmenter,
    Token,
    Vocabulary,
    global_lesson,
    is_grammar,
    is_word,
    iter_units,
    load_corpus,
    load_vocabulary,
    may_consult_wordlist,
)

OUTPUT = ROOT / "output/source-cache/original-readers/japanese-full/composed-sentences.json"
MIN_TOKENS = 3
LESSONS_PER_VOLUME = 50

# 讀不到正本時的救急表。正本是逐詞對譯層的 CLOSED_CLASS——那是全書印出來的說法，
# 抄第二份一定會漂。這裡只留最基本的一小撮，並且會印警告，免得「閘變鬆了」
# 這件事無聲發生。
FALLBACK_GRAMMAR = frozenset(
    """は が を に へ と で から まで より の も や か ね よ な ぞ ば て ても
    けれど ので のに し ながら ばかり だけ など こそ さえ しか ずつ とも ども
    つつ のみ にて だ です である ます た ない ぬ ず う よう らしい べし べき
    まい たい れる られる せる させる き けり つ る り む らむ けむ なり たり
    ごとし しむ ん じ らし として における において について によって による
    にとって とともに に対して に関して ということ といふ を以て により""".split()
)


def taught_grammar() -> frozenset[str]:
    """本讀本自己教的文法詞：助詞、助動詞與學術機能語。

    正本是 `build_japanese_interlinear.py` 的 `CLOSED_CLASS`，也就是全書逐詞
    對譯層實際印出來的那一張表；附錄二的文語助動詞表也在裡面。直接讀正本而
    不抄一份，是因為兩份表遲早會不一樣，而不一樣的那一天沒有人會發現。
    """
    try:
        from build_japanese_interlinear import CLOSED_CLASS  # noqa: PLC0415

        return frozenset(key for key in CLOSED_CLASS if key.strip())
    except Exception as error:  # pragma: no cover - 依環境
        print(f"讀不到逐詞對譯層的封閉詞類表（{error}），改用救急表", file=sys.stderr)
        return FALLBACK_GRAMMAR


def resolve_lesson(lesson: int, volume: int | None) -> int:
    """課次身分一律攤平成 1–100 的通編。

    `--volume 2 --lesson 3` 與 `--lesson 53` 是同一課。冊次是第一冊／第二冊，
    不是上下冊（合約明定），課次本身不是穩定鍵，所以兩種寫法都收，內部只留一種。
    """
    if volume:
        if not 1 <= lesson <= LESSONS_PER_VOLUME:
            raise SystemExit(f"第 {volume} 冊只有 {LESSONS_PER_VOLUME} 課，收到 {lesson}")
        return (volume - 1) * LESSONS_PER_VOLUME + lesson
    return lesson


def describe_lesson(number: int) -> str:
    volume = (number - 1) // LESSONS_PER_VOLUME + 1
    inside = (number - 1) % LESSONS_PER_VOLUME + 1
    return f"第{'一二'[volume - 1]}冊第 {inside} 課（通編 {number}）"


def lesson_targets(vocabulary: Vocabulary, lesson: int) -> list[dict[str, Any]]:
    return [entry for entry in vocabulary.entries if global_lesson(entry) == lesson]


def taught_upto(vocabulary: Vocabulary, lesson: int) -> set[int]:
    """已教過的詞，用 id() 之外的穩定身分：詞表裡的序位。"""
    return {
        index
        for index, entry in enumerate(vocabulary.entries)
        if global_lesson(entry) <= lesson
    }


def entry_key(entry: dict[str, Any]) -> str:
    """假名＋漢字這組身分，不是序號——序號一動全書的鍵就換人。"""
    return f"{entry.get('kana', '')}|{entry.get('kanji', '')}"


def headword(entry: dict[str, Any]) -> str:
    return (entry.get("kanji") or "").strip() or (entry.get("kana") or "").strip()


def verify_tokens(
    tokens: list[Token],
    *,
    vocabulary: Vocabulary,
    lemmas: dict[str, Any],
    lesson: int,
    grammar: Iterable[str],
) -> dict[str, Any]:
    """兩道逐詞閘跑在一串 token 上，回報哪一個詞卡在哪一道。

    拆成吃 token 的純函式，是為了讓挖句器直接用 `lemma-corpus.json` 裡已經斷好
    的那一份，不必再斷一次——同一句話斷兩次而結果不同，是這系列最難查的一種錯。
    """
    grammar = frozenset(grammar)
    unattested: list[str] = []
    untaught: list[str] = []
    unseen_forms: list[str] = []
    used_grammar: list[str] = []
    hit_keys: list[str] = []
    counted = 0

    # 掃法與挖句器、語料建置共用 `iter_units`：課本的詞條常常跨好幾個詞素
    # （一緒に、いつも、それから、サッカーを します），逐個 token 查一定查不到。
    for span, entry in iter_units(tokens, vocabulary):
        token = span[0]
        if token.pos in PUNCT_POS:
            continue
        counted += 1
        if len(span) > 1:
            surface = "".join(part.surface for part in span)
            if entry is not None and global_lesson(entry) <= lesson:
                hit_keys.append(entry_key(entry))
            else:
                untaught.append(surface)
            continue

        if not is_word(token) and not is_grammar(token):
            # 數字與拉丁字母：斷詞器會標成名詞，它們不是要教的詞。
            unattested.append(token.surface)
            continue

        # entry 就是 iter_units 對這一個 token 查出來的結果，不再查第二次。
        if is_grammar(token):
            if token.base in grammar or token.surface in grammar:
                used_grammar.append(token.base or token.surface)
                continue
            # 兩個字以上的助詞助動詞可以回退查詞表（「という」「ながら」）；
            # 單假名的一律不查，那是「は→齒」的路。
            if entry is not None and may_consult_wordlist(token):
                if global_lesson(entry) <= lesson:
                    hit_keys.append(entry_key(entry))
                    continue
                untaught.append(token.surface)
                continue
            untaught.append(token.surface)
            continue

        record = lemmas.get(token.base)
        if record is None:
            # 語料沒收，但課本收了。課本是權威，不是捏造——「朝ご飯」戰前的作家
            # 寫「朝飯」「朝御飯」，語料因此查不到，可是那是本讀本第 13 課要教的
            # 詞。這一閘要擋的是憑空造出來的詞，不是課本與語料的用字習慣不同。
            if entry is None:
                unattested.append(token.surface)
                continue
        elif token.surface != token.base and token.surface not in (record.get("surfaces") or []):
            # 活用形沒在語料裡見過。日文的活用是規則的，這不是退回的理由，
            # 只是給作者的一個提醒。
            unseen_forms.append(token.surface)
        if entry is None:
            untaught.append(token.surface)
            continue
        if global_lesson(entry) > lesson:
            untaught.append(token.surface)
            continue
        hit_keys.append(entry_key(entry))

    return {
        "tokenCount": len(tokens),
        "words": counted,
        "unattested": unattested,
        "untaught": untaught,
        "unseenForms": unseen_forms,
        "grammar": used_grammar,
        "vocabulary": hit_keys,
        "passed": not unattested and not untaught and counted >= MIN_TOKENS,
    }


def verify(
    sentence: str,
    *,
    segmenter: Segmenter,
    vocabulary: Vocabulary,
    lemmas: dict[str, Any],
    lesson: int,
    grammar: Iterable[str],
) -> dict[str, Any]:
    """三道閘的前兩道，跑在一句寫好的話上。"""
    return verify_tokens(
        segmenter.tokenize(sentence),
        vocabulary=vocabulary,
        lemmas=lemmas,
        lesson=lesson,
        grammar=grammar,
    )


def coverage_for(
    reports: list[dict[str, Any]], targets: list[dict[str, Any]]
) -> dict[str, Any]:
    """第三道閘：十題合起來有沒有把本課二十詞都用到。"""
    seen = {key for report in reports for key in report["vocabulary"]}
    missing = [entry for entry in targets if entry_key(entry) not in seen]
    return {
        "lessonWords": len(targets),
        "practised": len(targets) - len(missing),
        "notPractised": [
            {"headword": headword(entry), "kana": entry.get("kana", ""),
             "glossZh": entry.get("glossZh", "")}
            for entry in missing
        ],
    }


def read_draft(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sentences = payload.get("sentences") or []
    rows = []
    for row in sentences:
        text = row.get("japanese") or row.get("text") or row.get("ja") or ""
        rows.append({**row, "japanese": text})
    return rows, payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True, help="課次；不給 --volume 時是 1–100 通編")
    parser.add_argument("--volume", type=int, choices=(1, 2), help="冊次：第一冊／第二冊")
    parser.add_argument("--check", type=Path, required=True, help="要檢查的手寫稿 JSON")
    parser.add_argument("--corpus", type=Path, default=CORPUS_PATH)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    lesson = resolve_lesson(args.lesson, args.volume)
    corpus = load_corpus(args.corpus)
    vocabulary = load_vocabulary()
    lemmas = corpus["lemmas"]
    grammar = taught_grammar()
    segmenter = Segmenter()
    if segmenter.name != corpus["tokenizer"]["name"]:
        print(
            f"⚠ 語料是用 {corpus['tokenizer']['name']} 斷的，現在跑的是 "
            f"{segmenter.name}；基本形對不上會整批誤判，先重建語料",
            file=sys.stderr,
        )

    sentences, payload = read_draft(args.check)
    targets = lesson_targets(vocabulary, lesson)
    print(
        f"{describe_lesson(lesson)}：本課 {len(targets)} 詞，"
        f"檢查 {args.check.name} 的 {len(sentences)} 句"
    )
    print(f"語料：{corpus['counts']['distinctBaseForms']} 種基本形"
          f"（斷詞器 {corpus['tokenizer']['name']} {corpus['tokenizer']['version']}）")

    rows: list[dict[str, Any]] = []
    for index, row in enumerate(sentences, start=1):
        report = verify(
            row["japanese"],
            segmenter=segmenter,
            vocabulary=vocabulary,
            lemmas=lemmas,
            lesson=lesson,
            grammar=grammar,
        )
        rows.append({**row, "verification": report})
        mark = "通過" if report["passed"] else "退回"
        print(f"{index:2d} [{mark}] {row['japanese']}")
        print(f"     {row.get('chinese', '')}")
        if report["unattested"]:
            print(f"     ✗ 語料裡查無此詞：{'、'.join(report['unattested'])}")
        if report["untaught"]:
            print(f"     ✗ 尚未教過：{'、'.join(report['untaught'])}")
        if report["unseenForms"]:
            print(f"     · 活用形未見於語料（不退回）：{'、'.join(report['unseenForms'])}")

    coverage = coverage_for([row["verification"] for row in rows], targets)
    passed = sum(1 for row in rows if row["verification"]["passed"])
    print(f"\n通過機器驗證 {passed}/{len(rows)} 句")
    print(f"本課詞涵蓋 {coverage['practised']}/{coverage['lessonWords']}")
    if coverage["notPractised"]:
        names = "、".join(row["headword"] for row in coverage["notPractised"])
        print(f"還沒練到：{names}")
    print("提醒：過閘不等於正確。句法與語感機器看不出來，自撰題一律要作者逐句複核。")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(
                {
                    "lesson": lesson,
                    "volume": (lesson - 1) // LESSONS_PER_VOLUME + 1,
                    "author": payload.get("author", "hand-written"),
                    "tokenizer": corpus["tokenizer"],
                    "sentences": rows,
                    "coverage": coverage,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"寫入 {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
