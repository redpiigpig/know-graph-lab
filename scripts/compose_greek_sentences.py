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
import re
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

# 擁有者 2026-09-16 的裁定：**「已教過」不再是退回的理由**。
# 「按照程度來看，簡單的都可以先練習，沒有限制一定要本課教過的才行。」
# 一個詞排在第幾課是難度排序的結果，不是它本身難不難；把課次當成硬牆，會讓
# 一課的二十個詞裡有幾個永遠寫不進任何句子（拉丁 86、希臘 6、日文 34），
# 而那些缺口補不起來的理由是排序，不是語言。
#
# 這一關沒有刪掉，只是不再擋人：`untaught` 仍照實記錄哪些詞超出本課進度，
# 供日後要標注或分級時取用；`passed` 不再看它。語料那一關（第一道）沒有動——
# 捏一個語料裡不存在的形，仍然是錯的。
MIN_WORDS = 3
MAX_WORDS = 8  # 規格：三到八個詞，短句優先

# --------------------------------------------------------------------------
# 2026-09-25 交接第 5 點補強的三道句法閘（機械、近似，擋不住的仍要作者複核）
# --------------------------------------------------------------------------
#
# 覆核報告發現希臘自撰題最大宗的病不是詞形或詞義，是**沒有謂語**——把本課
# 生詞串成一堆名詞／不定詞／分詞，三道原有的閘（詞形、已教過、覆蓋）全部
# 放行，因為它們誰都不問「這句話有沒有一個動詞在挑大樑」。這裡補的三道閘
# 都是近似的：句法不是重音那種能全對全錯的東西，擋不住的仍要作者逐句複核
# （檔頭已經這樣寫，這裡沒有改變那個前提）。

# 不定詞與關身／被動分詞的字尾。這兩類永遠不是限定動詞：不定詞沒有人稱，
# 分詞是形容詞。四個不定詞字尾在通用希臘文裡不會是名詞或形容詞的字尾
# （沒有名詞用 -ειν／-ναι／-σθαι／-σαι 收尾），所以拿字尾判定是安全的。
NONFINITE_INFINITIVE_SUFFIXES = ("ειν", "ναι", "σθαι", "σαι")
# 關身／被動分詞（-μενος 一族）：判準看字尾是不是「μεν＋格位變化」。
# 🚨 格位字尾不能省略（不能寫成 `?`）：直陳語氣第一人稱複數（ἐσμέν、λέγομεν、
# ἦμεν）與不少根不定過去式的第三人稱單數（ἔδραμεν：ἔ-δραμ-εν，字根恰好收在
# μ，加上人稱字尾 -εν 之後尾三個字母也拼成「μεν」）都是真正的限定動詞，
# 光看「結尾是 μεν」會把它們也判成分詞——實測 ἔδραμεν 就中了這一坑。
PARTICIPLE_MEDIOPASSIVE_RE = re.compile(r"μεν(ος|η|ον|ου|ης|ω|οι|αι|α|ων|οις|αις)$")

# 句首不可放的連接詞／語氣詞：δέ／γάρ／οὖν 天生是句中連接詞，句首出現就是
# 詞序錯（希臘文正常語序把它們放在句子第二個詞之後）。
SENTENCE_INITIAL_BAN = {"δε", "γαρ", "ουν"}

# 後面必須接假設語氣的引導詞：ἵνα（含省音 ἵν’）、ὅπως、ἐάν、ὅταν、μήποτε。
MOOD_TRIGGER_PARTICLES = {"ινα", "ιν", "οπως", "εαν", "οταν", "μηποτε"}
# 直陳語氣才有的字尾（現在時 -ω 動詞）：現在假設語氣把 ε／ο 全部換成 η／ω
# （λέγει→λέγῃ、λέγομεν→λέγωμεν、λέγουσιν→λέγωσιν）。折疊只去重音不去母音，
# 所以這個對照在折疊字形上依然看得出來，可以當一道近似閘。
INDICATIVE_ONLY_SUFFIXES = ("ει", "εις", "ετε", "ομεν", "ουσιν", "ουσι")
# 這幾個詞本身以 -ει／-ομεν 收尾但不是直陳動詞（否定詞、代名詞等），
# 白名單排除，否則會誤判引導詞後面接的是受詞或副詞。
MOOD_CHECK_SKIP = {"μη", "ου", "ουκ", "ουχ", "και", "τε", "δε", "τις", "τι"}


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

# μένω 及其複合詞（παραμένω、ἀναμένω、ἐπιμένω、ὑπομένω…）字根本身就是
# 「μεν」，1sg 現在／未來主動態（μένω／μενῶ）折疊後跟關身／被動分詞字尾撞形——
# 分詞是「詞幹＋μεν＋格位」，這幾個詞是「介詞疊加＋μεν＋人稱字尾」，字串長得
# 一樣，純看字尾分不出來。這批詞閉集，直接列出更安全，不動一般分詞判準。
_MENO_ROOT_FINITE = {
    fold_key(prefix + root)
    for prefix in ("", "ανα", "επι", "παρα", "υπο", "δια", "προσ", "εμ", "κατα", "περι", "συμ", "συν")
    for root in ("μενω", "μενει", "μενον", "μενειτε")
}


def _is_nonfinite_form(folded: str) -> bool:
    """折疊字形是不是不定詞或關身／被動分詞——兩者都不是限定動詞。"""
    if folded in _MENO_ROOT_FINITE:
        return False
    if folded.endswith(NONFINITE_INFINITIVE_SUFFIXES):
        return True
    return bool(PARTICIPLE_MEDIOPASSIVE_RE.search(folded))


def _has_finite_verb(
    words: Sequence[str], resolved: Sequence[frozenset[str]], verb_keys: frozenset[str]
) -> bool:
    """閘四：這句話有沒有一個限定動詞在挑大樑。

    `verb_keys` 空集合＝本課為止一個動詞都還沒教過（目前只有上冊第一課），
    這種課本來就只能寫名詞句，不要求動詞。
    """
    if not verb_keys:
        return True
    for word, keys in zip(words, resolved):
        if not (keys & verb_keys):
            continue
        if not _is_nonfinite_form(fold_key(bare(word))):
            return True
    return False


def _sentence_initial_particle(words: Sequence[str]) -> str | None:
    """閘五：δέ／γάρ／οὖν 是句中連接詞，不能放句首。"""
    if not words:
        return None
    first = fold_key(bare(words[0]))
    return words[0] if first in SENTENCE_INITIAL_BAN else None


def _mood_after_conjunction(
    words: Sequence[str], resolved: Sequence[frozenset[str]], verb_keys: frozenset[str]
) -> list[str]:
    """閘六：ἵνα／ὅπως／ἐάν／ὅταν／μήποτε 後面應該是假設語氣，不是直陳語氣。

    近似判準：折疊字形保留母音（只去重音），現在時直陳的 ε／ο 換成假設語氣的
    η／ω 在折疊後仍看得出來。抓的是最明顯的一種錯，不是完整的語氣分析——
    詳見檔頭關於句法閘擋不住什麼的說明。
    """
    flagged: list[str] = []
    for index, word in enumerate(words):
        trigger = fold_key(bare(word))
        if trigger not in MOOD_TRIGGER_PARTICLES:
            continue
        for later_word, later_keys in zip(words[index + 1 :], resolved[index + 1 :]):
            later_folded = fold_key(bare(later_word))
            if later_folded in MOOD_CHECK_SKIP:
                continue
            is_verb = bool(later_keys & verb_keys) if verb_keys else True
            if not is_verb:
                # 還沒遇到動詞，可能是否定詞或受詞，繼續往後找同一子句裡的動詞。
                continue
            if later_folded.endswith(INDICATIVE_ONLY_SUFFIXES) and not _is_nonfinite_form(
                later_folded
            ):
                flagged.append(f"{word}…{later_word}")
            break
    return flagged


def verify_sentence(
    sentence: str,
    known: set[str],
    attestation: Attestation,
    taught_forms: frozenset[str] | set[str] = frozenset(),
    verb_keys: frozenset[str] = frozenset(),
    strict: bool = False,
) -> dict[str, Any]:
    """閘一、閘二，加上 2026-09-25 補的三道句法閘（閘四／五／六，`strict=True` 才開）。

    回傳的 `words` 是原樣字形，不是正規化過的。

    `taught_forms` 是「生字自己印出來的那個形」那一層，只在詞位那一層答不出來
    時才問：`εἶπεν` 的詞位是 λέγω，照詞位比對會把本課自己教的詞判成沒教過。

    `verb_keys` 是「動詞」詞性的詞位鍵集合，供閘四（有無限定動詞）與閘六
    （引導詞後面是不是動詞）使用；空集合表示本課為止還沒教過任何動詞。

    `strict` 只給**自撰題**開：閘四／五／六抓的是「一堆生詞湊句子」那種病，
    引用題是從語料真正的停頓切出來的子句，本來就可能沒有限定動詞（詩歌體、
    詩篇的標題行），套同一套閘會把可靠的原句判成退回。`strict=False`（預設）
    時這三道閘完全不跑，行為與 2026-09-25 之前一致。
    """
    words = split_words(sentence)
    unattested: list[str] = []
    untaught: list[str] = []
    accent_variants: list[str] = []
    lemmas: set[str] = set()
    forms: set[str] = set()
    written_all: set[str] = set()
    resolved: list[frozenset[str]] = []
    for word in words:
        written_all.add(fold_key(bare(word)))
        found, how = attestation.look_up(word)
        if found is None:
            unattested.append(word)
            resolved.append(frozenset())
            continue
        if how == "folded":
            accent_variants.append(word)
        taught = found & known
        if taught:
            lemmas |= taught
            resolved.append(frozenset(taught) | frozenset(found))
            continue
        written = fold_key(bare(word))
        if written in taught_forms:
            forms.add(written)
            # 這條路線本來就是為「詞條印出來的形跟語料標的詞位不一樣」設計的
            # （εἶπεν 的詞位是 λέγω），所以 verb_keys 這種依 VocabItem.keys
            # （詞條自己的 lemma／headword）建的集合，要靠 written 本身這把鑰匙
            # 才找得到它——只給 found（語料的詞位）會漏掉這整類詞。
            resolved.append(frozenset(found) | {written})
            continue
        components = crasis_components(word)
        if components and all(fold_key(part) in known for part in components):
            component_keys = {fold_key(part) for part in components}
            lemmas |= component_keys
            resolved.append(frozenset(component_keys) | frozenset(found))
            continue
        untaught.append(word)
        resolved.append(frozenset(found))
    length_ok = MIN_WORDS <= len(words) <= MAX_WORDS
    if strict:
        has_finite_verb = _has_finite_verb(words, resolved, verb_keys)
        initial_particle = _sentence_initial_particle(words)
        mood_violations = _mood_after_conjunction(words, resolved, verb_keys)
    else:
        has_finite_verb = True
        initial_particle = None
        mood_violations = []
    return {
        "words": len(words),
        "unattested": unattested,
        "untaught": untaught,
        "accentVariants": accent_variants,
        "lemmas": sorted(lemmas),
        "forms": sorted(forms),
        # Every word's own spelling, whichever route vouched for it.  A
        # two-word headword such as ``εἰ μή`` is only practised when both
        # halves stand in one sentence, and each half has a lemma of its own,
        # so neither the lemma route nor the form route can see the pair.
        "written": sorted(written_all),
        "lengthOk": length_ok,
        "hasFiniteVerb": has_finite_verb,
        "sentenceInitialParticle": initial_particle,
        "moodAfterConjunction": mood_violations,
        # 「已教過」不再擋人（見檔頭 2026-09-16 的裁定）；untaught 照記不照擋。
        # 閘四／五／六是 2026-09-25 補的，擋句法而不是詞形。
        "passed": (
            not unattested
            and len(words) >= MIN_WORDS
            and has_finite_verb
            and initial_particle is None
            and not mood_violations
        ),
    }


def coverage_report(
    lesson_items: Sequence[VocabItem], reports: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    """閘三：十題合起來把本課二十詞都用到了沒有。"""
    seen: set[str] = set()
    seen_forms: set[str] = set()
    per_sentence: list[set[str]] = []
    for report in reports:
        seen |= set(report["lemmas"])
        seen_forms |= set(report.get("forms") or ())
        per_sentence.append(set(report.get("written") or ()))

    def hit(item) -> bool:
        if item.keys & seen or item.written_keys & seen_forms:
            return True
        # The entry's own spelling, wherever it stands.  ``ἦν`` is this reader's
        # word and εἰμί is the corpus's lemma for it, so a sentence containing
        # ἦν resolves through the lemma route and never reaches the form one --
        # the word is written on the page and still counted as unpractised.
        if item.written_keys & {key for written in per_sentence for key in written}:
            return True
        # A phrase is practised only when all of it stands in one sentence --
        # crediting ``εἰ μή`` to any sentence containing μή would make the
        # coverage gate stop meaning anything for it.
        return len(item.written_keys) > 1 and any(
            item.written_keys <= written for written in per_sentence
        )

    practised = [item for item in lesson_items if hit(item)]
    missing = [item for item in lesson_items if not hit(item)]
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


def taught_forms_through(
    vocabulary: dict[int, dict[int, list[VocabItem]]], volume: int, lesson: int
) -> frozenset[str]:
    """每個生字自己印出來的那個形，累積到這一課為止（下冊含上冊）。"""
    keys: set[str] = set()
    for earlier in sorted(vocabulary):
        if earlier > volume:
            break
        for number in sorted(vocabulary[earlier]):
            if earlier == volume and number > lesson:
                break
            for item in vocabulary[earlier][number]:
                keys |= item.written_keys
    return frozenset(keys)


def verb_keys_through(
    vocabulary: dict[int, dict[int, list[VocabItem]]], volume: int, lesson: int
) -> frozenset[str]:
    """詞性為「動詞」的詞位鍵，累積到這一課為止（下冊含上冊）。

    供閘四／閘六用。空集合＝到這一課為止一個動詞都還沒教過——實測只有上冊
    第一課，那一課本來就只能寫名詞句。
    """
    keys: set[str] = set()
    for earlier in sorted(vocabulary):
        if earlier > volume:
            break
        for number in sorted(vocabulary[earlier]):
            if earlier == volume and number > lesson:
                break
            for item in vocabulary[earlier][number]:
                if item.pos == "動詞":
                    keys |= item.keys
    return frozenset(keys)


def review(
    volume: int,
    lesson: int,
    payload: dict[str, Any],
    lesson_items: Sequence[VocabItem],
    known: set[str],
    attestation: Attestation,
    taught_forms: frozenset[str] = frozenset(),
    verb_keys: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(payload.get("sentences", []), start=1):
        written = entry.get("greek", "")
        report = verify_sentence(
            written, known, attestation, taught_forms, verb_keys, strict=True
        )
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
        if not report.get("hasFiniteVerb", True):
            lines.append("     ✗ 沒有限定動詞（不定詞／分詞不算）")
        if report.get("sentenceInitialParticle"):
            lines.append(f"     ✗ 句首連接詞：{report['sentenceInitialParticle']}")
        if report.get("moodAfterConjunction"):
            lines.append(
                f"     ✗ 引導詞後疑似直陳語氣：{'、'.join(report['moodAfterConjunction'])}"
            )
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
        result = review(
            args.volume, lesson, payload, items, known, attestation,
            taught_forms_through(vocabulary, args.volume, lesson),
            verb_keys_through(vocabulary, args.volume, lesson),
        )
        print("\n".join(report_lines(result)))
        if args.write:
            path = output_path(args.volume, lesson)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"寫入 {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
