#!/usr/bin/env python3
"""替七十士（Swete）與下冊教父／教會文獻建逐句的詞位標記語料。

新約有 MorphGNT，每個詞都由編者標好詞位，是金標；另外兩批沒有。上冊有一半的
生字屬七十士，下冊一千詞全部屬教父與教會文獻，所以那兩批必須先自己標一次，
`compose_greek_sentences.py` 與 `build_greek_exercises.py` 才有東西可查。

詞位解析沿用本 repo 既有的三層：

1. `koine-lexicon.json` —— 新約與七十士的編者標註折出來的字形→詞位表。
   先查重音敏感的 `exactForms`（ἕξ 與 ἐξ 折疊後同形，氣號就是整個詞），
   再查折疊字形的 `forms`。
2. `lemma-index.json` —— Morpheus。⚠️ 它是**雅典方言優先**，問 ἐγένετο 會答
   γίγνομαι，不是通用希臘文讀本要教的 γίνομαι，所以只在前一層查無時才問，
   而且標出來讓人看得見。
3. 折疊字形本身當詞位。這一層等於「不知道」，輸出裡照樣記一筆，
   讓不確定度是個可以數的數字而不是一句話。

每個 token 都帶 `layer`，就是上面四個標籤之一（第一層分成 exact／folded 兩記）。

希臘文特有的坑，在進表之前就要處理掉，否則整批靜默落到第三層：

* **省音符號有五種寫法**。Swete 用 U+1FBD（᾽）寫了 5,061 處省音，
  koine-lexicon 卻是拿 U+2019（’）建的；不統一，那 5,061 個 καθ᾽／δι᾽
  一個都查不到。教父那批更雜，同一份檔裡 ’ 、 ' 、 ᾽ 、 ᾿ 、 ´ 五種都有。
  這是希伯來 maqqef 那個坑的希臘版。
* **Swete 帶校勘符號**：`πετόμεν[α]`、`⸂⸆⸃`、`[1]` 這種註號。
  補字的方括號要去掉（字是字），純符號與純數字的 token 直接不算詞。
* **大寫無重音的篇首**：Swete 開頭寫 `ΕΝ ΑΡΧΗ`，折疊會小寫化所以查得到，
  但重音敏感那一層查不到——這是正常的，記成 folded 層即可。

輸出：`lemma-corpus-septuagint.json`、`lemma-corpus-patristic.json`。
token 以三元組緊湊寫出（欄位名在 `tokenFields`），六十萬 token 的檔才不會爆掉。

用法：

    PYTHONIOENCODING=utf-8 python scripts/build_greek_lemma_corpus.py --corpus both --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_greek_vocab_lexicon import fold  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
SWETE_DIR = CACHE / "sources" / "swete"
KOINE_LEXICON = CACHE / "koine-lexicon.json"
MORPHEUS_INDEX = CACHE / "lemma-index.json"
PATRISTIC_PLAN = CACHE / "patristic-plan.json"
LITURGY = CACHE / "liturgy-chrysostom.json"
CREEDS = CACHE / "creeds-greek.json"

OUTPUT = {
    "septuagint": CACHE / "lemma-corpus-septuagint.json",
    "patristic": CACHE / "lemma-corpus-patristic.json",
}

TOKEN_FIELDS = ["form", "lemma", "layer"]

LAYER_KOINE_EXACT = "koine-exact"
LAYER_KOINE_FOLDED = "koine-folded"
LAYER_MORPHEUS = "morpheus"
LAYER_SURFACE = "surface-fold"
LAYERS = (LAYER_KOINE_EXACT, LAYER_KOINE_FOLDED, LAYER_MORPHEUS, LAYER_SURFACE)

LAYER_NOTES = {
    LAYER_KOINE_EXACT: "koine-lexicon 重音敏感表命中（金標語料的編者標註）",
    LAYER_KOINE_FOLDED: "koine-lexicon 折疊字形表命中（金標語料的編者標註）",
    LAYER_MORPHEUS: "Morpheus 命中；⚠️ 雅典方言優先，通用希臘文用途須視為待查",
    LAYER_SURFACE: "三層都查不到，以折疊字形充當詞位；⚠️ 等同未解析，是不確定度本身",
}

# 省音（elision）與冠詞省略在各檔裡有五種寫法。統一成 U+2019，
# 因為 koine-lexicon 是拿那一種建的。
APOSTROPHE_CODEPOINTS = (
    0x2019,  # ’ RIGHT SINGLE QUOTATION MARK：koine-lexicon 的寫法
    0x1FBD,  # ᾽ GREEK KORONIS：Swete 的寫法
    0x1FBF,  # ᾿ GREEK PSILI
    0x1FFD,  # ´ GREEK OXIA（被當省音號誤用）
    0x02BC,  # ʼ MODIFIER LETTER APOSTROPHE
    0x02BB,  # ʻ MODIFIER LETTER TURNED COMMA
    0x2018,  # ‘ LEFT SINGLE QUOTATION MARK
    0x0027,  # ' ASCII APOSTROPHE
    0x00B4,  # ´ ACUTE ACCENT
)
CANONICAL_APOSTROPHE = "’"
APOSTROPHES = {chr(code) for code in APOSTROPHE_CODEPOINTS}

# 校勘符號：方括號是補字（字要留、括號不留）；U+2E00–U+2E0F 那一排是
# SBLGNT 與 Swete 的異文記號（⸀⸁⸂⸃⸆…），黏在詞前後但不是詞的一部分。
EDITORIAL_MARKS = "[]{}⟨⟩⟦⟧" + "".join(chr(code) for code in range(0x2E00, 0x2E10))
EDGE_PUNCTUATION = " \t\r\n.,·;;!?:—–-()«»\"“”…*†‡"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
DIGIT_RE = re.compile(r"\d")

# 希臘文的句末標點只有句點、問號（;／;）與驚嘆號。
# ἄνω τελεία（·）做的是冒號或分號的事，不切句——`select_greek_memory_sentences.py`
# 已經為此踩過一次，切下來的是例外子句不是句子。
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.;;!])\s+")

# Crasis：κἀγώ 是兩個詞寫成一個。查不到本身的詞位時，拆成成分再查一次——
# 這是希伯來 maqqef 連寫的希臘版。表只收通用希臘文實際用得到的幾個。
CRASIS_EXACT: dict[str, tuple[str, ...]] = {
    "καγω": ("καί", "ἐγώ"),
    "καμε": ("καί", "ἐγώ"),
    "καμοι": ("καί", "ἐγώ"),
    "καμου": ("καί", "ἐγώ"),
    "καν": ("καί", "ἐάν"),
    "κακ": ("καί", "ἐκ"),
    "κακει": ("καί", "ἐκεῖ"),
    "κακειθεν": ("καί", "ἐκεῖθεν"),
    "καπειτα": ("καί", "ἔπειτα"),
    "τουναντιον": ("ὁ", "ἐναντίος"),
    "τουνομα": ("ὁ", "ὄνομα"),
    "ταυτα": ("ὁ", "αὐτός"),
    "ταυτο": ("ὁ", "αὐτός"),
    "ταυτον": ("ὁ", "αὐτός"),
    "χαι": ("καί", "ὁ"),
}
CRASIS_PREFIX: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("κακειν", ("καί", "ἐκεῖνος")),
)


# --------------------------------------------------------------------------
# 正規化：全部是純函式，而且全部只用於「比對」，不碰印出來的字
# --------------------------------------------------------------------------

def unify_apostrophes(word: str) -> str:
    """把五種省音符號統一成 U+2019，其餘一個字元都不動。"""
    return "".join(CANONICAL_APOSTROPHE if ch in APOSTROPHES else ch for ch in word)


def strip_editorial(word: str) -> str:
    """去掉校勘括號與異文記號，補字本身留著。"""
    return "".join(ch for ch in word if ch not in EDITORIAL_MARKS)


def bare(word: str) -> str:
    """印刷字形去掉前後標點與校勘符號，重音、氣號、下標 iota 全部保留。

    這是「比對用的原樣」：還看得出重音，所以 koine-lexicon 的重音敏感表查得到；
    但已經沒有逗號句點，不會因為一個句點就查無此字。
    """
    cleaned = unicodedata.normalize("NFC", word)
    cleaned = strip_editorial(unify_apostrophes(cleaned))
    return cleaned.strip(EDGE_PUNCTUATION)


def fold_key(word: str) -> str:
    """去重音、去氣號、去下標 iota、小寫化、ς→σ 的比對鍵。"""
    return fold(bare(word))


def no_apostrophe(key: str) -> str:
    return key.replace(CANONICAL_APOSTROPHE, "")


def is_word(word: str) -> bool:
    """真的是個詞，不是校勘註號也不是純標點。"""
    stripped = bare(word)
    if not stripped or not GREEK_RE.search(stripped):
        return False
    return not DIGIT_RE.search(stripped)


def split_words(text: str) -> list[str]:
    """依空白切詞，只留下真的是詞的那些；回傳的是**原樣**（含標點已去除的字形）。"""
    return [bare(chunk) for chunk in unicodedata.normalize("NFC", text).split() if is_word(chunk)]


def crasis_components(word: str) -> tuple[str, ...]:
    """κἀγώ → (καί, ἐγώ)。不是 crasis 就回空。"""
    key = fold_key(word)
    if key in CRASIS_EXACT:
        return CRASIS_EXACT[key]
    for prefix, lemmas in CRASIS_PREFIX:
        if key.startswith(prefix):
            return lemmas
    return ()


def split_sentences(text: str) -> list[str]:
    """依希臘文句末標點切句，印出來的字一個都不改。"""
    out: list[str] = []
    for part in SENTENCE_SPLIT_RE.split(unicodedata.normalize("NFC", text)):
        part = part.strip()
        if part and GREEK_RE.search(part):
            out.append(part)
    return out


# --------------------------------------------------------------------------
# 三層詞位解析
# --------------------------------------------------------------------------

class Lemmatizer:
    """三層 Koine 詞位解析，並回報是哪一層決定的。"""

    def __init__(self, koine: dict[str, Any], morpheus: dict[str, Any] | None) -> None:
        self.exact: dict[str, list[str]] = koine.get("exactForms", {})
        self.forms: dict[str, list[str]] = koine.get("forms", {})
        self.morpheus: dict[str, list[str]] = (morpheus or {}).get("forms", {})
        self.counts: Counter[str] = Counter()

    @classmethod
    def load(cls, use_morpheus: bool = True) -> "Lemmatizer":
        if not KOINE_LEXICON.exists():
            raise FileNotFoundError(
                f"缺少通用希臘文詞位表：{KOINE_LEXICON}；先跑 build_greek_koine_lexicon.py --write"
            )
        koine = json.loads(KOINE_LEXICON.read_text(encoding="utf-8"))
        morpheus = None
        if use_morpheus and MORPHEUS_INDEX.exists():
            morpheus = json.loads(MORPHEUS_INDEX.read_text(encoding="utf-8"))
        return cls(koine, morpheus)

    def candidates(self, word: str) -> tuple[list[str], str]:
        """回傳（詞位清單，決定它的那一層）。清單最前面的是最可能的那個。"""
        printed = bare(word)
        if not printed:
            return [], LAYER_SURFACE
        folded = fold(printed)
        for key in self._exact_keys(printed):
            hit = self.exact.get(key)
            if hit:
                return list(hit), LAYER_KOINE_EXACT
        for key in self._folded_keys(folded):
            hit = self.forms.get(key)
            if hit:
                return list(hit), LAYER_KOINE_FOLDED
        for key in self._folded_keys(folded):
            hit = self.morpheus.get(key)
            if hit:
                return list(hit), LAYER_MORPHEUS
        return ([folded] if folded else []), LAYER_SURFACE

    @staticmethod
    def _exact_keys(printed: str) -> Iterator[str]:
        yield printed
        if CANONICAL_APOSTROPHE in printed:
            yield printed.replace(CANONICAL_APOSTROPHE, "")

    @staticmethod
    def _folded_keys(folded: str) -> Iterator[str]:
        if not folded:
            return
        yield folded
        if CANONICAL_APOSTROPHE in folded:
            yield no_apostrophe(folded)

    def resolve(self, word: str) -> tuple[str, str]:
        """單一詞位＋層別；一形多位時取語料裡最常見的那個。"""
        lemmas, layer = self.candidates(word)
        self.counts[layer] += 1
        return (lemmas[0] if lemmas else ""), layer


# --------------------------------------------------------------------------
# 兩批語料的讀取
# --------------------------------------------------------------------------

def read_swete_words() -> dict[int, str]:
    path = SWETE_DIR / "01-Swete_word_with_punctuations.csv"
    if not path.exists():
        raise FileNotFoundError(f"缺少 Swete 原文：{path}")
    words: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        index, _, word = line.partition("\t")
        if word:
            words[int(index)] = unicodedata.normalize("NFC", word)
    return words


def read_swete_refs() -> list[tuple[int, str]]:
    path = SWETE_DIR / "00-Swete_versification.csv"
    if not path.exists():
        raise FileNotFoundError(f"缺少 Swete 分節表：{path}")
    refs: list[tuple[int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        index, _, ref = line.partition("\t")
        refs.append((int(index), ref.strip()))
    refs.sort()
    return refs


def septuagint_units() -> Iterator[dict[str, Any]]:
    """Swete 七十士：一節一個 unit，`ref` 就是 Swete 自己的節號。"""
    words = read_swete_words()
    refs = read_swete_refs()
    last = max(words)
    for position, (start, ref) in enumerate(refs):
        end = refs[position + 1][0] - 1 if position + 1 < len(refs) else last
        printed = [words[index] for index in range(start, end + 1) if index in words]
        if not printed:
            continue
        book = ref.split(".", 1)[0]
        yield {"ref": ref, "book": book, "source": "swete", "text": " ".join(printed)}


def patristic_units() -> Iterator[dict[str, Any]]:
    """下冊語料：教父／教會文獻讀文、金口若望禮儀、希臘文信經，逐句切開。"""
    if PATRISTIC_PLAN.exists():
        plan = json.loads(PATRISTIC_PLAN.read_text(encoding="utf-8"))
        for reading in plan.get("readings", []):
            for segment in reading.get("segments", []):
                text = segment.get("displayText") or segment.get("sourceText") or ""
                for index, sentence in enumerate(split_sentences(text), start=1):
                    yield {
                        "ref": f"patristic-plan:{reading['ordinal']}:{segment.get('ref')}#{index}",
                        "book": reading.get("titleGrc") or reading.get("titleZh") or "",
                        "source": "patristic-plan",
                        "category": reading.get("category", ""),
                        "lesson": reading.get("lesson"),
                        "text": sentence,
                    }
    if LITURGY.exists():
        liturgy = json.loads(LITURGY.read_text(encoding="utf-8"))
        for step in liturgy.get("steps", []):
            text = step.get("displayText") or step.get("sourceText") or ""
            for index, sentence in enumerate(split_sentences(text), start=1):
                yield {
                    "ref": f"liturgy-chrysostom:{step['ordinal']}#{index}",
                    "book": liturgy.get("titleGrc", "金口若望禮儀"),
                    "source": "liturgy-chrysostom",
                    "category": "liturgy",
                    "lesson": None,
                    "text": sentence,
                }
    if CREEDS.exists():
        creeds = json.loads(CREEDS.read_text(encoding="utf-8"))
        for document in creeds.get("documents", []):
            for segment in document.get("segments", []):
                text = segment.get("displayText") or segment.get("sourceText") or ""
                for index, sentence in enumerate(split_sentences(text), start=1):
                    yield {
                        "ref": f"creeds:{document['slug']}:{segment.get('ordinal')}#{index}",
                        "book": document.get("titleGrc") or document.get("titleZh") or "",
                        "source": "creeds-greek",
                        "category": "creed-or-decree",
                        "lesson": None,
                        "text": sentence,
                    }


CORPUS_READERS = {
    "septuagint": septuagint_units,
    "patristic": patristic_units,
}

CORPUS_SOURCES = {
    "septuagint": [
        "Henry Barclay Swete, The Old Testament in Greek according to the Septuagint (1930)，"
        "eliranwong/LXX-Swete-1930 逐詞檔；原檔只有詞與標點，無詞位標記"
    ],
    "patristic": [
        "patristic-plan.json（使徒教父、希臘教父、法規集、禮儀詩歌、信經與教令讀文）",
        "liturgy-chrysostom.json（金口若望聖禮儀）",
        "creeds-greek.json（希臘文信經）",
    ],
}


# --------------------------------------------------------------------------
# 標記
# --------------------------------------------------------------------------

def tag_units(units: Iterable[dict[str, Any]], lemmatizer: Lemmatizer) -> tuple[list[dict], Counter]:
    tagged: list[dict[str, Any]] = []
    layer_counts: Counter[str] = Counter()
    for unit in units:
        rows: list[list[str]] = []
        for word in split_words(unit["text"]):
            lemma, layer = lemmatizer.resolve(word)
            layer_counts[layer] += 1
            rows.append([word, lemma, layer])
        if not rows:
            continue
        record = {key: value for key, value in unit.items() if key != "text" and value is not None}
        record["text"] = unit["text"]
        record["tokens"] = rows
        tagged.append(record)
    return tagged, layer_counts


def build(corpus: str, lemmatizer: Lemmatizer) -> dict[str, Any]:
    units, layer_counts = tag_units(CORPUS_READERS[corpus](), lemmatizer)
    total = sum(layer_counts.values())
    uncertain = layer_counts[LAYER_SURFACE]
    return {
        "schemaVersion": "1.0.0",
        "corpus": corpus,
        "language": "Koine Greek",
        "languageCode": "grc",
        "generatedOn": date.today().isoformat(),
        "sources": CORPUS_SOURCES[corpus],
        "tokenFields": TOKEN_FIELDS,
        "resolution": {
            "order": list(LAYERS),
            "layerNotes": LAYER_NOTES,
            "counts": {layer: layer_counts.get(layer, 0) for layer in LAYERS},
            "tokens": total,
            "unresolvedTokens": uncertain,
            "unresolvedRate": round(uncertain / total, 4) if total else 0.0,
            "note": (
                "unresolvedTokens 是三層都查不到、只能拿折疊字形充當詞位的 token 數，"
                "也就是本語料詞位標記的不確定度。morpheus 那一層是雅典方言優先，"
                "用在通用希臘文須另行複核。"
            ),
        },
        "counts": {"units": len(units), "tokens": total},
        "units": units,
    }


def summarise(payload: dict[str, Any]) -> str:
    resolution = payload["resolution"]
    counts = resolution["counts"]
    lines = [
        f"{payload['corpus']}：{payload['counts']['units']} 個單位、{resolution['tokens']} 個 token",
    ]
    for layer in LAYERS:
        number = counts.get(layer, 0)
        share = number * 100 / resolution["tokens"] if resolution["tokens"] else 0
        lines.append(f"  {layer:<13s} {number:>7d}（{share:5.1f}%）")
    lines.append(
        f"  ⚠️ 靠折疊字形猜的 {resolution['unresolvedTokens']} 個"
        f"（{resolution['unresolvedRate']:.1%}），這是不確定度"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="替七十士與教父語料建詞位標記")
    parser.add_argument("--corpus", choices=["septuagint", "patristic", "both"], default="both")
    parser.add_argument("--write", action="store_true", help="寫出 lemma-corpus-*.json")
    parser.add_argument(
        "--no-morpheus",
        action="store_true",
        help="不查 Morpheus 那一層，看看純 Koine 詞典能解到什麼程度",
    )
    args = parser.parse_args()

    lemmatizer = Lemmatizer.load(use_morpheus=not args.no_morpheus)
    targets = ["septuagint", "patristic"] if args.corpus == "both" else [args.corpus]
    for corpus in targets:
        payload = build(corpus, lemmatizer)
        print(summarise(payload))
        if args.write:
            path = OUTPUT[corpus]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            print(f"  已寫出 {path.relative_to(ROOT)}（{path.stat().st_size / 1_048_576:.1f} MB）")
        else:
            print("  （未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
