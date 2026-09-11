#!/usr/bin/env python3
"""Segment the Japanese reader's corpus once, and keep the result on disk.

The Japanese reader (`japanese-reader-contract.md`) needs the same thing the
Hebrew one gets free from MorphHB: an authority that can answer "is this word
really used, and in what shape".  Japanese has no gold-tagged corpus here, so
this script builds one by running the reader's own sources through a
morphological analyser and writing out

* `lemmas` — every base form the corpus attests, with its part of speech, the
  base-form reading, how often it occurs and in how many documents.  This is
  what `compose_japanese_sentences.py` checks a hand-written sentence against;
* `sentences` — the token string of every sentence that could ever become an
  exercise, each token carrying surface form, base form, part of speech and
  reading.  This is what `build_japanese_exercises.py` mines quotations from.

**Why `sentences` is filtered and `lemmas` is not.**  The three source trees
hold 21.8 million characters, about 14 million morphemes; a per-token dump of
all of it would be most of a gigabyte and nothing would ever read it.  The
lemma index costs almost nothing and breadth is a virtue there, so it covers
everything.  A sentence, on the other hand, is only ever useful to this project
if it is short and if every word in it is either grammar or one of the reader's
own 2,000 lesson words — that is the contract's "生字零" rule.  Sentences
outside that band can never be quoted, so they are counted and dropped.  Pass
`--keep-all-sentences` to get the unfiltered dump anyway, and expect the size.

**Tokeniser.**  fugashi + unidic-lite is the default, janome the fallback, and
whichever ran is recorded in the output — mixing the two silently would be a
real bug, because they disagree about exactly the words this reader teaches.
UniDic knows the 文語 paradigms: it reads 「見給ひき」 as 見る／給ふ／き, where
janome cuts it into 見／給／ひき and then invents dictionary forms like ふる and
ひる for the pieces (that is how an earlier pass printed 「揮舞」 226 times).
UniDic also gives the reading of the *base* form (`kanaBase`) and not only of
the surface, which janome does not — 見る→みん is the known trap.

    python -X utf8 scripts/build_japanese_lemma_corpus.py --write
    python -X utf8 scripts/build_japanese_lemma_corpus.py --limit 30   # 試跑
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
OUTPUT = CACHE / "lemma-corpus.json"

# 三個語料樹，全部進 lemma 索引。aozora＝青空文庫戰前宗教學，scripture＝文語訳
# 聖書與佛典訓読，manyoshu＝萬葉集（鹿持雅澄訓訂）。
SOURCE_DIRS = (
    ("aozora", CACHE / "aozora/texts", CACHE / "aozora/manifest.json"),
    ("scripture", CACHE / "scripture", CACHE / "scripture/manifest.json"),
    ("manyoshu", CACHE / "manyoshu", CACHE / "manyoshu/manifest.json"),
)

# 可引用的句子帶幾個詞素。下限三是合約的最短句，上限二十四是「三到八個詞」
# 加上助詞助動詞與標點之後的寬鬆上界——挖句器自己還會再收窄。
MIN_SENTENCE_TOKENS = 3
MAX_SENTENCE_TOKENS = 24

# UniDic 的封閉詞類。這幾類不是「生詞」，是文法：助詞助動詞在附錄二的文語助動詞表
# 與課本文法裡教，標點不是詞。janome 的 pos1 只有「助詞／助動詞／記号」，UniDic
# 另有「補助記号」與「空白」，兩套都列進來，換斷詞器不會換判準。
GRAMMAR_POS = frozenset({"助詞", "助動詞", "補助記号", "記号", "空白"})
PUNCT_POS = frozenset({"補助記号", "記号", "空白"})

KANA_RE = re.compile(r"[ぁ-ゖァ-ヺー]")
KANJI_RE = re.compile(r"[一-鿿々]")
LATIN_RE = re.compile(r"[A-Za-z]")
# 萬葉集與維基文庫的振假名：漢字後面括號裡的假名。留著會斷出「（」「こ」「）」。
FURIGANA_RE = re.compile(r"（[ぁ-ゖァ-ヺー・]+）")
# 聖書各章的節號自成一行；青空的〔〕註記同理。
NUMBER_LINE_RE = re.compile(r"^[0-9０-９\s.:：]+$")
POEM_NUMBER_RE = re.compile(r"^[0-9０-９]{3,5}[　\s]+")
SENTENCE_END_RE = re.compile(r"(?<=[。．！？!?])")
SENTENCE_FINAL = "。．！？!?"
# 舊活字的疊字記號。它們是符號不是詞，一整句只剩它們就成了「花のいろ／＼」
# 這種挖出來也沒法當題目的東西。
REPEAT_MARKS = "ゝゞ〳〵〴／＼〃"
QUOTE_PAIRS = (("「", "」"), ("『", "』"), ("（", "）"), ("〔", "〕"), ("《", "》"))

# 全形／半形的數字與符號。斷詞器把「2304」與「（」都標成名詞，第一版逐詞對譯
# 因此印出「二千三百零四」與「左括號」——萬葉集的歌番號被當成生詞在教。
DIGITS = set("0123456789０１２３４５６７８９")

# 文語的字面特徵：舊假名（ヱ・ヰ・ゐ・ゑ）、文語助動詞與活用語尾、舊字體。
# 這些在現代語譯本裡幾乎不出現，反過來也一樣。
BUNGO_RE = re.compile(
    r"ヱ|ヰ|ゐ|ゑ|なりき|なりけり|たまひ|たまふ|たまへ|給[ふひへは]|けり|べし"
    r"|ざりき|いふ|いへ|なんぢ|われら|かれら|れり|せり|をもて|而して|ごとし"
    r"|傳|眞|國|學|體|靈|榮|舊|齒|觀|聲|讀|實|變|對|發|會|來|萬|圍|縁|鑄"
)
# 現代語譯本（口語訳・新共同訳）的特徵：です・ます体與現代的助動詞連用。
MODERN_RE = re.compile(
    r"である|であった|ています|ました|ません|なさい|ではない|している"
    r"|していた|れている|でした|ください|だろう|という"
)
# 短篇（信經、偈頌）樣本少，一個特徵就算數；長篇要三個以上才算。
SHORT_TEXT = 800


class Token(NamedTuple):
    """One morpheme.  `base` is the written base form, `reading` its reading.

    `reading` is deliberately the reading of the **base** form, not of the
    surface: 見る's surface 見 reads ミ but the word reads ミル, and printing the
    surface reading in a dictionary column invents a word that does not exist.
    """

    surface: str
    base: str
    pos: str
    sub: str
    reading: str

    def as_json(self) -> dict[str, str]:
        return {
            "surface": self.surface,
            "base": self.base,
            "pos": self.pos,
            "sub": self.sub,
            "reading": self.reading,
        }


# --------------------------------------------------------------------------
# 斷詞器
# --------------------------------------------------------------------------


def _clean_lemma(lemma: str) -> str:
    """UniDic 的 lemma 帶語義標記：給う-尊敬、行く-行、方-ホウ。標記不是詞的一部分。"""
    return lemma.split("-")[0] if lemma and lemma != "*" else ""


def _katakana_to_hiragana(text: str) -> str:
    return "".join(
        chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in text
    )


def to_hiragana(text: str) -> str:
    """讀音一律轉平假名再比對——詞表寫平假名，UniDic 回片假名。"""
    return _katakana_to_hiragana(text or "")


class Segmenter:
    """fugashi 為主、janome 為輔，用了哪一個一律記在輸出裡。"""

    def __init__(self, engine: str = "auto") -> None:
        self.name = ""
        self.version = ""
        self.dictionary = ""
        self._tagger = None
        self._janome = None
        if engine in ("auto", "fugashi"):
            try:
                self._load_fugashi()
            except Exception as error:  # pragma: no cover - 環境相關
                if engine == "fugashi":
                    raise
                print(f"fugashi 起不來（{error}），退回 janome", file=sys.stderr)
        if not self.name:
            self._load_janome()

    def _load_fugashi(self) -> None:
        import fugashi  # noqa: PLC0415
        # fugashi 自己會找到 unidic-lite，這一行是「字典真的裝了」的檢查：
        # 沒裝的話 Tagger() 的錯訊是 MeCab 那一層的，看不出缺的是字典。
        import unidic_lite  # noqa: F401,PLC0415

        self._tagger = fugashi.Tagger()
        self.name = "fugashi"
        self.version = _package_version("fugashi")
        self.dictionary = f"unidic-lite {_package_version('unidic-lite')}"

    def _load_janome(self) -> None:
        from janome.tokenizer import Tokenizer  # noqa: PLC0415

        self._janome = Tokenizer()
        self.name = "janome"
        self.version = _package_version("janome")
        self.dictionary = "ipadic（janome 內建）"

    def describe(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version, "dictionary": self.dictionary}

    def tokenize(self, text: str) -> list[Token]:
        if self._tagger is not None:
            return [self._from_fugashi(word) for word in self._tagger(text)]
        return [self._from_janome(word) for word in self._janome.tokenize(text)]

    @staticmethod
    def _from_fugashi(word: Any) -> Token:
        feature = word.feature
        base = (
            (getattr(feature, "orthBase", "") or "").strip("*")
            or _clean_lemma(getattr(feature, "lemma", ""))
            or word.surface
        )
        reading = to_hiragana(
            (getattr(feature, "kanaBase", "") or "").strip("*")
            or (getattr(feature, "kana", "") or "").strip("*")
        )
        return Token(
            surface=word.surface,
            base=base,
            pos=(feature.pos1 or "").strip("*"),
            sub=(feature.pos2 or "").strip("*"),
            reading=reading,
        )

    @staticmethod
    def _from_janome(word: Any) -> Token:
        fields = word.part_of_speech.split(",")
        base = word.base_form if word.base_form and word.base_form != "*" else word.surface
        # janome 的 reading 是表面形的讀音，不是辭書形的；這裡照實留著，並在輸出
        # 的 tokenizer 欄記下用的是 janome，讀者才知道這一欄的品質不同。
        reading = to_hiragana((word.reading or "").strip("*"))
        return Token(
            surface=word.surface,
            base=base,
            pos=fields[0],
            sub=(fields[1] if len(fields) > 1 else "").strip("*"),
            reading=reading,
        )


def _package_version(name: str) -> str:
    import importlib.metadata as metadata  # noqa: PLC0415

    try:
        return metadata.version(name)
    except Exception:  # pragma: no cover - 環境相關
        return "?"


# --------------------------------------------------------------------------
# 純函式：什麼算詞、什麼可以查詞表
# --------------------------------------------------------------------------


def classify_register(text: str) -> dict[str, Any]:
    """這段文字是文語還是現代語——機械判準，不靠人逐篇看。

    🚨 這道閘的由來：`bible_以賽亞書_001.txt` 掛著「文語訳・公有領域」的標籤，
    內容卻是現代語譯本（「アモツの子イザヤが……治世のことである」），而同一卷
    第 2 章是貨真價實的文語（「すゑの日にヱホバの家の山は……堅立ち」）。維基文庫
    那一頁的第 1 章本身就被換成了現代語譯文，重抓也是同一份。這不只是體例錯：
    口語訳（1954/55）與新共同訳（1987）仍在著作權內，掛錯標籤等於把有版權的
    文字當公有領域收進語料。

    一章混得進來就可能有第二章，所以判準要是純函式、跑得了全庫、進得了測試，
    而不是人工逐一看——人工逐一看正是這個系列最會出事的做法。

    回傳 `register` 為 `文語`／`現代語`／`不確定`，附上兩邊各撞到幾次，
    好讓報告說得出「憑什麼這樣判」。
    """
    bungo = len(BUNGO_RE.findall(text))
    modern = len(MODERN_RE.findall(text))
    size = len(text)
    if modern > bungo:
        register = "現代語"
    elif bungo >= 3 or (bungo >= 1 and size < SHORT_TEXT):
        register = "文語"
    else:
        register = "不確定"
    return {
        "register": register,
        "bungoHits": bungo,
        "modernHits": modern,
        "chars": size,
    }


def is_word(token: Token) -> bool:
    """數字、拉丁字母與符號不是詞。

    斷詞器把「2304」與「（」都標成名詞。放著不管，挖句器會把萬葉集的歌番號
    當成句子的一部分，逐詞對譯層則會印出「二千三百零四」「左括號」。
    """
    base = (token.base or "").strip()
    if not base:
        return False
    if token.pos in PUNCT_POS:
        return False
    if all(ch in DIGITS for ch in base):
        return False
    if base.isascii():
        return False
    return True


def is_grammar(token: Token) -> bool:
    """助詞、助動詞與標點：文法與版面，不是課內生詞。"""
    return token.pos in GRAMMAR_POS


def may_consult_wordlist(token: Token) -> bool:
    """助詞助動詞能不能拿去查那張 2,000 詞的表。

    不能，除非它有兩個字以上。要擋的是單假名的同形碰撞：詞表裡「は」是齒、
    「や」是屋、「が」是蛾，照假名比中，全書每個主題助詞都會印成「牙齒」。
    這個坑在逐詞對譯層已經踩過一次（見 `build_japanese_interlinear.py`
    的 `gloss_for`），這裡照同一條規矩。

    兩個字以上要能回退查表，因為「ある」「という」「ながら」被標成助動詞或
    助詞時，詞表裡的說法正是要用的那一個，一律不查會空掉上千處。
    """
    if not is_grammar(token):
        return True
    return len(token.base) >= 2 and token.pos not in PUNCT_POS


# --------------------------------------------------------------------------
# 詞表
# --------------------------------------------------------------------------


class Vocabulary:
    """讀本自己的 2,000 課內詞，兩個索引分開放。

    `written` 是漢字與辭書形這種強鍵，`kana` 是假名這種弱鍵。分開是為了讓
    `may_consult_wordlist` 擋得住的東西真的擋得住——假名索引裡有「は→歯」。
    """

    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = entries
        self.written: dict[str, dict[str, Any]] = {}
        self.kana: dict[str, dict[str, Any]] = {}
        self.phrases: dict[str, dict[str, Any]] = {}
        for entry in entries:
            for key in (entry.get("kanji"), entry.get("dictionaryForm")):
                key = (key or "").strip()
                if key:
                    self.written.setdefault(key, entry)
                    self._add_phrase(key, entry)
            kana = (entry.get("kana") or "").strip()
            if kana:
                self.kana.setdefault(kana, entry)
                self._add_phrase(kana, entry)
                # 漢字欄空的詞（かつて、ながら…）假名就是它的寫法，算強鍵。
                if not (entry.get("kanji") or "").strip():
                    self.written.setdefault(kana, entry)

    def _add_phrase(self, key: str, entry: dict[str, Any]) -> None:
        """課本的詞條常常不是一個詞素：一緒に、いつも、それから、サッカーを します。

        斷詞器把它們拆成 一緒／に、いつ／も、それ／から、サッカー／を／し／ます，
        逐個 token 去查詞表就查不到，於是課本教過的詞被判成「尚未教過」。這張
        表存的是把空白去掉之後的整串寫法，驗證時把相鄰幾個 token 的表層形接起來
        比對。`サッカーを します` 詞表裡帶一個空格，接起來的沒有，所以一律先去空白。
        """
        flat = "".join(key.split())
        if len(flat) >= 2:
            self.phrases.setdefault(flat, entry)

    def lookup(self, token: Token) -> dict[str, Any] | None:
        if not may_consult_wordlist(token):
            return None
        entry = self.written.get(token.base) or self.written.get(token.surface)
        if entry is not None:
            return entry
        if is_grammar(token):
            # 助詞助動詞永遠不走假名索引，長度不論——那正是「は→歯」的路。
            return None
        reading = to_hiragana(token.reading)
        return self.kana.get(reading) if reading else None

    def lookup_phrase(self, tokens: list[Token]) -> dict[str, Any] | None:
        """相鄰幾個 token 合起來是不是課本的一個詞條。

        兩道保險：整串不得含標點，且其中至少要有一個實詞。後者擋的還是「は」那
        一類——純助詞接出來的「には」「では」若哪天撞進詞表，不會被當成課內詞。
        """
        if not tokens or any(token.pos in PUNCT_POS for token in tokens):
            return None
        if all(is_grammar(token) for token in tokens):
            return None
        flat = "".join(token.surface for token in tokens)
        return self.phrases.get(flat)

    def __contains__(self, token: Token) -> bool:
        return self.lookup(token) is not None


# 課本詞條最長幾個詞素。「サッカーを します」斷成 サッカー／を／し／ます 是四個。
MAX_PHRASE_TOKENS = 5


def iter_units(
    tokens: list[Token], vocabulary: Vocabulary
) -> Iterator[tuple[list[Token], dict[str, Any] | None]]:
    """把 token 串掃成「一個詞條一段」，長的詞組先吃。

    驗證與挖句共用同一個掃法。兩邊各掃一次遲早會掃出不同的結果，而不同的那
    一天不會有任何跡象——這一系列最貴的錯就是這種。回傳的 entry 是詞表裡的
    那一條，查不到就是 None（標點也回 None，由呼叫端自己跳過）。
    """
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.pos in PUNCT_POS:
            yield [token], None
            index += 1
            continue
        matched = None
        span = 1
        for width in range(min(MAX_PHRASE_TOKENS, len(tokens) - index), 1, -1):
            matched = vocabulary.lookup_phrase(tokens[index : index + width])
            if matched is not None:
                span = width
                break
        if matched is None:
            matched = vocabulary.lookup(token)
        yield tokens[index : index + span], matched
        index += span


def load_vocabulary(path: Path = VOCAB) -> Vocabulary:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return Vocabulary(payload["entries"])


def global_lesson(entry: dict[str, Any]) -> int:
    """課次身分＝冊次＋冊內課次，攤平成 1–100。

    序號本身不是穩定鍵（這條在三本讀本害過人），所以攤平的算式寫在這裡一份，
    誰要用都從這裡拿，不要各自再算一次。
    """
    volume = int(entry.get("volume") or 1)
    lesson = int(entry.get("readerLesson") or entry.get("lesson") or 0)
    return (volume - 1) * 50 + lesson


# --------------------------------------------------------------------------
# 讀語料
# --------------------------------------------------------------------------


def load_manifest(path: Path) -> dict[str, dict[str, Any]]:
    """manifest 的鍵各家不同，一律改用檔名當鍵。"""
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    by_file: dict[str, dict[str, Any]] = {}
    for key, meta in payload.items():
        target = meta.get("file")
        if not target:
            continue
        by_file[Path(target).name] = {**meta, "manifestKey": key}
    return by_file


def clean_line(line: str) -> str:
    line = FURIGANA_RE.sub("", line)
    line = POEM_NUMBER_RE.sub("", line)
    line = line.replace("　", " ").strip()
    if not line or NUMBER_LINE_RE.match(line):
        return ""
    return line


def balance_quotes(text: str) -> str:
    """落單的引號拿掉。

    按句號切開之後，「誰方？ 這種開了沒關的引號會整串留在句首，印成題目就是
    半句話。成對的引號留著，落單的一律刪。
    """
    for opener, closer in QUOTE_PAIRS:
        if text.count(opener) != text.count(closer):
            text = text.replace(opener, "").replace(closer, "")
    return text.strip()


def split_sentences(text: str) -> Iterator[str]:
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        for piece in SENTENCE_END_RE.split(line):
            piece = balance_quotes(piece.strip())
            if piece:
                yield piece


def iter_documents(limit: int | None = None) -> Iterator[tuple[str, str, dict[str, Any], str]]:
    """(source, docId, meta, text) —— 每一篇語料一次。"""
    seen = 0
    for source, directory, manifest_path in SOURCE_DIRS:
        if not directory.exists():
            print(f"缺語料目錄：{directory}", file=sys.stderr)
            continue
        manifest = load_manifest(manifest_path)
        for path in sorted(directory.glob("*.txt")):
            meta = manifest.get(path.name, {})
            text = path.read_text(encoding="utf-8", errors="replace")
            yield source, path.stem, meta, text
            seen += 1
            if limit and seen >= limit:
                return


# --------------------------------------------------------------------------
# 可引用的句子
# --------------------------------------------------------------------------


def sentence_is_keepable(text: str, tokens: list[Token], vocabulary: Vocabulary) -> bool:
    """這句有沒有可能成為練習題。

    合約的「生字零」是硬條件：題目裡每個詞都要教過。所以一句話只要含一個
    不在 2,000 詞表也不在文法封閉類裡的詞，它永遠挖不出來，存著只是佔位。

    另外三件事是第一版挖出來才看到的，都不是「詞」的問題而是「句」的問題：

    * **沒有句末標點的不是句子。** 以讀點結尾的（娘はすぐに、）是換行切出來的
      半句，詩行則根本沒有標點。印成題目就是叫學習者翻譯半句話。
    * **一個假名都沒有的不是日文。** 與謝野晶子遊記裡引的漢文「殊方言欲稽」
      整句是漢字，詞表比中「方言」就過關了，可是那是中文。
    * **疊字記號不成詞**，見 `REPEAT_MARKS`。
    """
    if not text or text[-1] not in SENTENCE_FINAL:
        return False
    if not KANA_RE.search(text):
        return False
    if any(mark in text for mark in REPEAT_MARKS):
        return False
    if not (MIN_SENTENCE_TOKENS <= len(tokens) <= MAX_SENTENCE_TOKENS):
        return False
    content = 0
    spoken = 0
    for span, entry in iter_units(tokens, vocabulary):
        if span[0].pos in PUNCT_POS:
            continue
        spoken += 1
        surface = "".join(token.surface for token in span)
        if LATIN_RE.search(surface) or all(ch in DIGITS for ch in surface):
            return False
        if entry is not None:
            content += 1
            continue
        if len(span) == 1 and is_grammar(span[0]):
            continue
        return False
    return content >= 2 and spoken >= MIN_SENTENCE_TOKENS


def build(limit: int | None, keep_all: bool, engine: str) -> dict[str, Any]:
    segmenter = Segmenter(engine)
    vocabulary = load_vocabulary()
    print(f"斷詞器：{segmenter.name} {segmenter.version}（{segmenter.dictionary}）")

    lemma_pos: dict[str, str] = {}
    lemma_reading: dict[str, str] = {}
    lemma_count: Counter[str] = Counter()
    lemma_docs: defaultdict[str, set[str]] = defaultdict(set)
    lemma_surfaces: defaultdict[str, Counter[str]] = defaultdict(Counter)

    sentences: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    scanned_tokens = 0
    scanned_sentences = 0

    rejected: list[dict[str, Any]] = []
    for source, doc_id, meta, text in iter_documents(limit):
        stats = sources.setdefault(
            source, {"documents": 0, "sentences": 0, "tokens": 0, "kept": 0, "rejected": 0}
        )
        # 語體閘：掛著「文語訳」的檔案若判為現代語，整份不收。理由見
        # `classify_register`——那不只是體例錯，是把仍有著作權的譯文當公有領域用。
        if meta.get("excluded") or (
            meta.get("group") in ("bible", "creed")
            and classify_register(text)["register"] == "現代語"
        ):
            stats["rejected"] += 1
            rejected.append(
                {"source": source, "docId": doc_id, "title": meta.get("titleZh", doc_id),
                 **classify_register(text)}
            )
            continue
        stats["documents"] += 1
        doc_key = f"{source}:{doc_id}"
        index = 0
        for sentence in split_sentences(text):
            tokens = segmenter.tokenize(sentence)
            if not tokens:
                continue
            index += 1
            scanned_sentences += 1
            stats["sentences"] += 1
            stats["tokens"] += len(tokens)
            scanned_tokens += len(tokens)
            for token in tokens:
                if not is_word(token):
                    continue
                base = token.base
                lemma_count[base] += 1
                lemma_docs[base].add(doc_key)
                lemma_surfaces[base][token.surface] += 1
                lemma_pos.setdefault(base, token.pos)
                if token.reading and base not in lemma_reading:
                    lemma_reading[base] = token.reading
            if keep_all or sentence_is_keepable(sentence, tokens, vocabulary):
                stats["kept"] += 1
                sentences.append(
                    {
                        "id": f"{doc_key}:s{index:04d}",
                        "source": source,
                        "docId": doc_id,
                        "title": meta.get("titleZh") or meta.get("title") or doc_id,
                        "author": meta.get("author", ""),
                        "ref": meta.get("manifestKey", doc_key),
                        "sourceUrl": meta.get("sourceUrl", ""),
                        # 佛典訓読的譯者與年份未查證，合約的 stop condition 說
                        # 未查證前不得當成公有領域。挖句器預設不引這一批。
                        "rightsChecked": bool(meta.get("rightsChecked", True)),
                        "text": sentence,
                        "tokens": [token.as_json() for token in tokens],
                    }
                )

    lemmas = {
        base: {
            "pos": lemma_pos.get(base, ""),
            "reading": lemma_reading.get(base, ""),
            "count": count,
            "docs": len(lemma_docs[base]),
            "surfaces": [form for form, _ in lemma_surfaces[base].most_common(6)],
        }
        for base, count in lemma_count.most_common()
    }

    return {
        "schemaVersion": "1.0.0",
        "note": (
            "日文讀本的斷詞語料。lemmas 涵蓋全部語料，是「基本形出現過沒有」那道閘的"
            "依據；sentences 只留可能成為練習題的句子（三到二十四個詞素、每個實詞都在"
            "本讀本 2,000 詞表內），其餘句子只計數不留 token 串。"
        ),
        "tokenizer": segmenter.describe(),
        "sources": sources,
        # 被語體閘擋下的檔案，留著名字與憑據，不要無聲消失。
        "rejected": rejected,
        "counts": {
            "documents": sum(row["documents"] for row in sources.values()),
            "sentencesScanned": scanned_sentences,
            "tokensScanned": scanned_tokens,
            "sentencesKept": len(sentences),
            "distinctBaseForms": len(lemmas),
        },
        "lemmas": lemmas,
        "sentences": sentences,
    }


def load_corpus(path: Path = OUTPUT) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(
            f"找不到 {path}，先跑 python -X utf8 scripts/build_japanese_lemma_corpus.py --write"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="寫進 lemma-corpus.json")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 篇，試跑用")
    parser.add_argument(
        "--keep-all-sentences",
        action="store_true",
        help="連挖不出題的句子也留 token 串；輸出會大好幾百倍",
    )
    parser.add_argument("--engine", default="auto", choices=("auto", "fugashi", "janome"))
    args = parser.parse_args()

    payload = build(args.limit or None, args.keep_all_sentences, args.engine)
    counts = payload["counts"]
    print(
        f"語料 {counts['documents']} 篇、{counts['sentencesScanned']} 句、"
        f"{counts['tokensScanned']} 個詞素，基本形 {counts['distinctBaseForms']} 種"
    )
    print(f"可引用的句子留下 {counts['sentencesKept']} 句")
    for source, stats in payload["sources"].items():
        print(
            f"  {source:10s} {stats['documents']:5d} 篇 "
            f"{stats['tokens']:9d} 詞素 留 {stats['kept']:6d} 句"
            f"{'　語體閘退回 %d 篇' % stats['rejected'] if stats.get('rejected') else ''}"
        )
    for row in payload["rejected"]:
        print(
            f"  ✗ 語體閘退回 {row['title']}：判為{row['register']}"
            f"（文語特徵 {row['bungoHits']}、現代語特徵 {row['modernHits']}）"
        )
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        size = OUTPUT.stat().st_size / 1e6
        print(f"寫入 {OUTPUT.relative_to(ROOT)}（{size:.1f} MB）")


if __name__ == "__main__":
    main()
