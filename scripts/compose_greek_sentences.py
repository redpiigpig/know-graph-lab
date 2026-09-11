#!/usr/bin/env python3
"""驗通用希臘文讀本的自撰練習句——作者寫句子，語料驗句子。

每課十題＝七題自撰＋三題經典原句（規格見
`skills/build-original-language-reader/references/exercise-sets.md`）。
定錨那三題由 `build_greek_exercises.py` 從語料挖；自撰那七題由作者執筆，
本檔是它的機器閘。**本檔不造句**，也不叫模型：希伯來版那一輪已經驗證過，
模型寫的十句有八句過閘、其中三句仍有真錯，所以造句這件事回到作者手上，
機器只負責「作者寫的這句，機械上站不站得住」。

三道閘，全部是機械判定：

1. **每個詞形必須在權威語料中實際出現過。** 上冊查新約（MorphGNT 金標）
   與七十士，下冊再加教父與教會文獻。捏造的變化形一律退回。
2. **每個詞必須已教過。** 詞形先經語料還原成詞位，再比對本課與先前各課的詞表。
   只比字形是不夠的——ἀναμιμνήσκωμεν 與詞表裡的 ἀναμιμνήσκω 一個字母都對不上。
3. **十題合起來必須涵蓋本課二十詞。**

擋不住的是句法與語感。過閘不等於正確，自撰題一律要作者逐句複核。

希臘文的坑，全部發生在「比對前的正規化」這一步，而且全部只影響比對：

* **重音與氣號**：ἐξ（從）與 ἕξ（六）折疊後同形，氣號就是整個詞，
  所以先查重音敏感的一層，查不到才折疊，並把「字母對、重音不對」標出來。
* **crasis**：κἀγώ 是 καί ＋ ἐγώ 寫成一個詞。它本身查不到詞表時拆成成分再比一次，
  這是希伯來 maqqef 連寫那個坑的希臘版——不拆，正確的句子會被整批誤判。
* **elision**：δι᾽ 的省音號在本 repo 的各份語料裡有五種寫法
  （U+2019 / U+1FBD / U+1FBF / U+1FFD / ASCII），不統一就查不到。
* **詞尾 sigma**：ς 與 σ 在折疊那一層一律歸 σ。
* **下標 iota**：ᾳ 分解後的 U+0345 是結合字元，折疊時一併去掉。

🚨 **正規化只用於比對。** 印出來、寫進 JSON 的 `greek` 一律是作者寫的原樣，
一個重音、一個省音號都不改。`scripts/tests/test_greek_exercises.py` 有一條
測試專門釘住這一點。

用法：

    PYTHONIOENCODING=utf-8 python scripts/compose_greek_sentences.py \\
        --volume 1 --lesson 13 --check my-sentences.json --write

待驗檔的格式：

    {"volume": 1, "lesson": 13, "author": "作者",
     "sentences": [{"greek": "…", "chinese": "…"}, …]}
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_greek_lemma_corpus import (  # noqa: E402
    CACHE,
    ROOT,
    bare,
    crasis_components,
    fold_key,
    split_words,
)
from build_greek_exercises import (  # noqa: E402
    VOLUME_CORPORA,
    CorpusUnit,
    VocabItem,
    cumulative_sets,
    load_units,
    load_vocabulary,
)

MIN_WORDS = 3
MAX_WORDS = 8  # 規格：三到八個詞，短句優先


def output_path(volume: int, lesson: int) -> Path:
    """一課一檔。希伯來版共用一個檔，跑第二課就把第一課蓋掉了。"""
    return CACHE / f"composed-greek-sentences-v{volume}-l{lesson:02d}.json"


# --------------------------------------------------------------------------
# 語料證據
# --------------------------------------------------------------------------

class Attestation:
    """語料裡實際寫過的字形，兩個索引：重音敏感的，與折疊的。"""

    def __init__(self) -> None:
        self.exact: dict[str, set[str]] = defaultdict(set)
        self.folded: dict[str, set[str]] = defaultdict(set)

    @classmethod
    def from_units(cls, units: Iterable[CorpusUnit]) -> "Attestation":
        index = cls()
        for unit in units:
            for form, lemma, _layer in unit.tokens:
                key = fold_key(lemma) if lemma else ""
                printed = bare(form)
                if not printed:
                    continue
                if key:
                    index.exact[printed].add(key)
                    index.folded[fold_key(printed)].add(key)
                else:
                    index.exact.setdefault(printed, set())
                    index.folded.setdefault(fold_key(printed), set())
        return index

    def look_up(self, word: str) -> tuple[set[str] | None, str]:
        """回傳（這個字形對應的詞位鍵，比對方式）。查不到回 (None, "none")。"""
        printed = bare(word)
        if printed in self.exact:
            return self.exact[printed], "exact"
        folded = fold_key(printed)
        if folded in self.folded:
            return self.folded[folded], "folded"
        return None, "none"


# --------------------------------------------------------------------------
# 三道閘
# --------------------------------------------------------------------------

def verify_sentence(
    sentence: str, known: set[str], attestation: Attestation
) -> dict[str, Any]:
    """閘一與閘二。回傳的 `words` 是原樣字形，不是正規化過的。"""
    words = split_words(sentence)
    unattested: list[str] = []
    untaught: list[str] = []
    accent_variants: list[str] = []
    lemmas: set[str] = set()
    for word in words:
        found, how = attestation.look_up(word)
        if found is None:
            unattested.append(word)
            continue
        if how == "folded":
            accent_variants.append(word)
        taught = found & known
        if taught:
            lemmas |= taught
            continue
        components = crasis_components(word)
        if components and all(fold_key(part) in known for part in components):
            lemmas |= {fold_key(part) for part in components}
            continue
        untaught.append(word)
    length_ok = MIN_WORDS <= len(words) <= MAX_WORDS
    return {
        "words": len(words),
        "unattested": unattested,
        "untaught": untaught,
        "accentVariants": accent_variants,
        "lemmas": sorted(lemmas),
        "lengthOk": length_ok,
        "passed": not unattested and not untaught and len(words) >= MIN_WORDS,
    }


def coverage_report(
    lesson_items: Sequence[VocabItem], reports: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    """閘三：十題合起來把本課二十詞都用到了沒有。"""
    seen: set[str] = set()
    for report in reports:
        seen |= set(report["lemmas"])
    practised = [item for item in lesson_items if item.keys & seen]
    missing = [item for item in lesson_items if not (item.keys & seen)]
    return {
        "lessonWords": len(lesson_items),
        "practised": len(practised),
        "notPractised": [item.public_record() for item in missing],
        "passed": not missing,
    }


def load_check_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "sentences" not in payload:
        raise ValueError(f"{path.name} 沒有 sentences 欄位")
    return payload


def review(
    volume: int,
    lesson: int,
    payload: dict[str, Any],
    lesson_items: Sequence[VocabItem],
    known: set[str],
    attestation: Attestation,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(payload.get("sentences", []), start=1):
        written = entry.get("greek", "")
        report = verify_sentence(written, known, attestation)
        rows.append(
            {
                "no": index,
                "kind": "composed",
                # 原樣，一個字元都沒改。
                "greek": written,
                "chinese": entry.get("chinese", ""),
                "chineseSource": "",
                "verification": report,
                "reviewedBy": entry.get("reviewedBy", "pending_author_review"),
            }
        )
    coverage = coverage_report(lesson_items, [row["verification"] for row in rows])
    return {
        "schemaVersion": "1.0.0",
        "language": "Koine Greek",
        "languageCode": "grc",
        "volume": volume,
        "lesson": lesson,
        "generatedOn": date.today().isoformat(),
        "author": payload.get("author", "hand-written"),
        "corpora": list(VOLUME_CORPORA[volume]),
        "gateNote": (
            "三道閘：詞形須在語料出現過、詞須已教過、十題合起來涵蓋二十詞。"
            "句法與語感擋不住，過閘不等於正確，自撰題一律要作者逐句複核。"
        ),
        "sentences": rows,
        "coverage": coverage,
        "counts": {
            "sentences": len(rows),
            "passed": sum(1 for row in rows if row["verification"]["passed"]),
        },
    }


def report_lines(result: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for row in result["sentences"]:
        report = row["verification"]
        mark = "通過" if report["passed"] else "退回"
        lines.append(f"{row['no']:2d} [{mark}] {row['greek']}")
        lines.append(f"     {row['chinese']}")
        if report["unattested"]:
            lines.append(f"     ✗ 語料查無此形：{'、'.join(report['unattested'])}")
        if report["untaught"]:
            lines.append(f"     ✗ 尚未教過：{'、'.join(report['untaught'])}")
        if report["accentVariants"]:
            lines.append(
                f"     ⚠️ 字母對但重音／氣號與語料不同：{'、'.join(report['accentVariants'])}"
            )
        if not report["lengthOk"]:
            lines.append(f"     ⚠️ 長度 {report['words']} 詞，規格是三到八詞")
    counts, coverage = result["counts"], result["coverage"]
    lines.append("")
    lines.append(f"通過機器驗證 {counts['passed']}/{counts['sentences']} 句")
    lines.append(
        f"本課二十詞練到 {coverage['practised']}/{coverage['lessonWords']}"
        + ("" if coverage["passed"] else "，未涵蓋："
           + "、".join(row["headword"] for row in coverage["notPractised"]))
    )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="驗通用希臘文讀本的自撰練習句")
    parser.add_argument("--volume", type=int, choices=[1, 2], default=1)
    parser.add_argument("--lesson", type=int, required=True)
    parser.add_argument(
        "--check",
        type=Path,
        required=True,
        help='待驗的手寫句子檔：{"lesson": n, "sentences": [{"greek": …, "chinese": …}]}',
    )
    parser.add_argument("--write", action="store_true", help="寫出驗證結果 JSON")
    args = parser.parse_args()

    vocabulary = load_vocabulary()
    if args.lesson not in vocabulary[args.volume]:
        raise SystemExit(f"第 {args.volume} 冊沒有第 {args.lesson} 課")

    payload = load_check_file(args.check)
    declared = payload.get("lesson")
    if declared is not None and declared != args.lesson:
        raise SystemExit(f"待驗檔寫的是第 {declared} 課，命令列給的是第 {args.lesson} 課")

    print(f"讀語料（第 {args.volume} 冊：{'、'.join(VOLUME_CORPORA[args.volume])}）…")
    attestation = Attestation.from_units(load_units(VOLUME_CORPORA[args.volume]))
    print(f"  語料字形 {len(attestation.exact)} 種（折疊後 {len(attestation.folded)} 種）")

    for lesson, items, known in cumulative_sets(vocabulary, args.volume):
        if lesson != args.lesson:
            continue
        print(f"檢查 {args.check.name}，{len(payload['sentences'])} 句；已教詞位 {len(known)}")
        result = review(args.volume, lesson, payload, items, known, attestation)
        print("\n".join(report_lines(result)))
        if args.write:
            path = output_path(args.volume, lesson)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"寫入 {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
