#!/usr/bin/env python3
"""單字卡正面該印多少：只有推不出來的名詞才印完整詞典形。

讀本印完整的詞典形（`σκηνή, ῆς, ἡ`），那是詞典的體例，也是查閱要用的。單字卡不
同：正面是要作答的那一面，印進去的每一個字元都在佔走詞頭的字級，而**第一、二變格
的屬格從詞尾加性別就推得出來**——θεός 是陽性 -ος，屬格必然是 θεοῦ，印出來也是白印。

所以規則是：**規則變化的名詞只印詞頭，推不出來的才印完整形。** 推不出來有兩種：

* **屬格幹變了**——第三變格。σῶμα→σώματος、πατήρ→πατρός、σάρξ→σαρκός、
  πίστις→πίστεως、γένος→γένους。其中 γένος 最要緊：主格與 λόγος 一模一樣，
  屬格卻差得遠，不印就分不出來。
* **性別不照詞尾**——ὁδός、ἔρημος 是 -ος 卻是陰性；προφήτης、μαθητής 是 -ης 卻是
  陽性；δόξα、θάλασσα 是不純 -α，屬格收 -ης 不是 -ας。

判斷用的屬格與冠詞，先取詞表自己的 `printedEntry`（Mounce 那 500 詞有），沒有就查
Dodson（CC0，倉庫已凍結）。兩邊都查不到就只印詞頭——**不自己推一個屬格出來**，
那正是這一系列裡最貴的那種錯：印在紙上、看起來完全正常、學的人無從察覺。
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DODSON = ROOT / "output/source-cache/original-readers/greek-full/sources/dodson/dodson.xml"

ARTICLES = {"ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά"}

# 詞尾 -> (預期的屬格詞尾, 預期的冠詞)。第一、二變格就這四條。
EXPECTED = {
    "ος": ("ου", "ὁ"),
    "ον": ("ου", "τό"),
    "η": ("ης", "ἡ"),
    "α": ("ας", "ἡ"),
}

_ORTH: dict[str, str] | None = None
_ENTRY_RE = re.compile(r'<entry n="([^"|]+?) \| \d+">\s*<orth>([^<]+)</orth>')


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def dodson_citation(lemma: str) -> str:
    """Dodson 的 `<orth>`，例如 `γένος, ους, τό`。查無則空字串。"""
    global _ORTH
    if _ORTH is None:
        _ORTH = {}
        if DODSON.exists():
            for match in _ENTRY_RE.finditer(DODSON.read_text(encoding="utf-8")):
                _ORTH.setdefault(match.group(1).strip(), match.group(2).strip())
    return _ORTH.get(lemma, "")


def split_citation(citation: str) -> tuple[str, str, str]:
    """把 `σῶμα, ατος, τό` 拆成 (主格, 屬格, 冠詞)；拆不出來回三個空字串。

    Dodson 偶爾給兩個性別（`παῖς, παιδός, ὁ, ἡ`），取第一個；詞表偶爾把冠詞寫成
    `-ὁ`，那個連字號是排版不是詞形。
    """
    bits = [bit.strip().lstrip("-").strip() for bit in citation.split(",")]
    articles = [index for index, bit in enumerate(bits) if bit in ARTICLES]
    if len(bits) < 3 or not articles:
        return "", "", ""
    return bits[0], bits[1], bits[articles[0]]


def is_regular_noun(nominative: str, genitive: str, article: str) -> bool:
    """屬格與性別是否都由詞尾推得出來。"""
    folded_nominative, folded_genitive = fold(nominative), fold(genitive)
    for ending, (expected_genitive, expected_article) in EXPECTED.items():
        if not folded_nominative.endswith(ending):
            continue
        if article != expected_article:
            return False
        # 屬格只該是那個詞尾本身（`ου`），或者連著幹一起寫（`λόγου`）。長度差太多
        # 就是幹變了，例如 πίστις 的 πίστεως。
        return folded_genitive.endswith(expected_genitive) and (
            len(folded_genitive) <= len(expected_genitive) + 1
            or folded_genitive == fold(nominative[: -len(ending)]) + expected_genitive
        )
    # 詞尾不在第一、二變格的四條裡，就是第三變格。
    return False


def card_headword(entry: dict, part_of_speech: str) -> str:
    """單字卡正面該印的字串。"""
    lemma = entry["lemma"].strip()
    printed = (entry.get("printedEntry") or "").strip()

    if part_of_speech != "名詞":
        return printed or lemma

    citation = printed if printed and printed != lemma else dodson_citation(lemma)
    nominative, genitive, article = split_citation(citation)
    if not article:
        # 七十士與教父獨有、詞典沒收的詞：只印詞頭，不猜。
        return lemma
    if is_regular_noun(nominative, genitive, article):
        return lemma
    return f"{nominative}, {genitive}, {article}"
