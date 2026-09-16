#!/usr/bin/env python3
"""The reader's ten appendix tables, split between its two volumes.

Fifty lessons of twenty words leave no room for the words a reader meets
constantly but never has to drill, and frequency counting handles them badly
besides: left in, Israel and Moyses take the top of any Vulgate list and push
out vocabulary; left out, someone opening Judith meets Holofernes with nothing
to go on.  So they go into appendices, arranged by kind rather than by
frequency, to be consulted rather than memorised.

Five tables face the Bible and five face the church, because this reader spans
fifteen centuries and its two halves need different reference shelves.  A reader
of the Vulgate needs the Roman measures and the biblical feasts; a reader of a
papal bull needs the Kalends, the abbreviations of the curia, and the Latin
names of modern countries.  Two of these tables have no counterpart in the
Hebrew or Greek readers at all -- how the Holy See writes today's nation-states,
and how it dates a document -- and they are the part of this reader that could
not have been carried over from either.

Chinese for the proper names is read out of the aligned translation rather than
recalled.  The Studium Biblicum edition underlines every proper name in its
verse text, so a Latin name's Chinese is whichever underlined name appears in
most of the verses that Latin name appears in, and is rare elsewhere.  That is
evidence.  Where the evidence does not reach -- a name outside the fifty printed
chapters -- the cell stays empty, and every filled cell records how it was
filled.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import latin_dictionary as W  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
CHURCH = CACHE / "latin-church"
SIGAO = CACHE / "sigao-zh.json"
SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
EXTRA_CHAPTERS = CACHE / "sigao-extra-chapters.json"
OUTPUT = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-appendices.json"

SENTENCE_RE = __import__('re').compile(r'[.;:?!]')

NAME_MINIMUM = 8          # below this a name is a walk-on part, not a fixture

# Titles of God rather than names of people, and the reader learns them as
# vocabulary in the first units.  They are still harvested -- they are
# capitalised throughout the Vulgate -- but the table says what they are so the
# name list does not open with five words that are not names of anybody.
DIVINE = {"dominus", "deus", "christus", "iesus", "spiritus sanctus", "altissimus",
          "emmanuel", "messias", "sabaoth", "adonai", "pater", "agnus"}
CAPITAL_RATIO = 0.8

# 辭典把這些收成「大寫開頭的名詞」——Graecus 是「一個希臘人」、Biblia 是「聖經」——
# 所以辭典那一關放行了它們，但一張**專名表**不是它們該待的地方：族稱形容詞
# （Graecus／Italus／Siculus／Parthus／Hebraeus／Afer／Atheniensis）、地名形容詞
# （Alexandrinus／Antiochenus）、教派形容詞（Arianus）、普通名詞（Biblia）
# 與稱號（Deipara 天主之母）。它們的中文屬於課內詞表或既有的職分表。
NOT_A_NAME = {
    "graecus", "italus", "siculus", "parthus", "hebraeus", "afer", "atheniensis",
    "alexandrinus", "antiochenus", "arianus", "biblia", "deipara",
}

# 聖經人名不進譯名詞庫：這本讀本的聖經譯名權威是思高譯本，與上冊那張表走同一條路
# （上冊是逐節對位讀出來的）。這五個沒出現在讀本的五十章裡，對位讀不到，所以照
# 思高的定名列在這裡，路徑一樣記成「思高譯本」。
# 🚨 鍵一定要經過 L.fold：它把 v 折成 u，Eva 的鍵是 eua 不是 eva，寫死字面
# 會永遠對不上而且看起來像「思高也沒有這個名字」。
SIGAO_NAMES = {
    L.fold(latin): zh
    for latin, zh in (
        ("Eva", "厄娃"), ("Emmanuel", "厄瑪奴耳"), ("Ezechiel", "厄則克耳"),
        ("Saulus", "掃祿"), ("Cornelius", "科爾乃略"),
    )
}

# 同名者的裁決：這批語料裡「Theophilus」指的是誰。
# 🚨 只記**哪一列**，不記譯名——譯名的權威在詞庫，不在這支腳本。詞庫有三位
# Theophilus（安提阿、凱撒利亞、亞歷山大），而語料二十五次全部標明
# episcopus Alexandrinus。沒有這張表，歧義閘會把它留白；留白比指錯人好，但
# 有證據時就該填對的那一位。
CORPUS_REFERENT = {
    L.fold("Theophilus"): "Theophilus of Alexandria",
}

# 真的是好幾個人共用的羅馬名，指認任何一位都是錯的：
#   Julianus  語料至少六人——背教者尤利安、埃克拉努姆的猶利安、科斯的猶利安、
#             佩特拉總主教、欽戈利主教、蒙科尼永的真福茱莉安娜。
#   Saturninus 語料至少七人——佩爾佩圖亞同伴的殉道者、亞爾勒主教、梅南德派的
#             諾斯底教師、法學家克勞狄烏斯、森提烏斯、處死西利丘殉道者的總督
#             維革利烏斯，以及一座聖撒圖爾尼努斯堂。
# 這種只給音譯。附錄在這裡的職責是告訴讀者這個字怎麼念，不是替他認人。
# 🚨 Saturninus 詞庫兩列的寫法本身就不一致（薩圖爾努斯／撒圖爾尼努（非洲總督）），
# 前者看起來是漏掉了 -in-；這裡取貼合拉丁的 撒圖爾尼努斯，待擁有者裁定後再回寫詞庫。
SHARED_NAME = {
    L.fold("Julianus"): "尤利安",
    L.fold("Saturninus"): "撒圖爾尼努斯",
}

CURATED_UPPER = {
    "numerals": {
        "title": "數字、羅馬數字與度量衡",
        "groups": {
            "基數": "unus duo tres quattuor quinque sex septem octo novem decem undecim "
                    "duodecim viginti triginta quadraginta quinquaginta sexaginta "
                    "septuaginta octoginta nonaginta centum ducenti trecenti "
                    "quadringenti quingenti mille",
            "序數": "primus secundus tertius quartus quintus sextus septimus octavus "
                    "nonus decimus undecimus duodecimus novissimus",
            "分配數與數副詞": "singuli bini terni quaterni semel bis ter quater quinquies "
                    "decies centies milies dimidium tertia pars",
            "長度與容量": "cubitus palmus digitus stadium milia passuum modius satum "
                    "batus corus hin gomor sextarius mensura",
            "錢幣與重量": "talentum mina denarius drachma stater as quadrans minutum "
                    "siclus argentum aurum libra uncia",
        },
    },
    "kinship": {
        "title": "親屬稱謂",
        "groups": {
            "直系": "pater mater filius filia parens avus avia proavus nepos neptis "
                    "primogenitus unigenitus infans puer puella",
            "旁系": "frater soror patruus amita avunculus matertera consobrinus "
                    "cognatus propinquus gemini",
            "姻親": "vir uxor maritus sponsus sponsa socer socrus gener nurus levir "
                    "vidua orphanus nuptiae",
            "家族與世系": "familia domus tribus cognatio generatio semen stirps posteritas "
                    "haeres hereditas",
        },
    },
    "calendar": {
        "title": "羅馬曆、月份與聖經節期",
        "groups": {
            "羅馬記日法": "kalendae nonae idus pridie postridie ante diem annus mensis dies "
                    "hora vigilia saeculum",
            "月份": "Ianuarius Februarius Martius Aprilis Maius Iunius Iulius Augustus "
                    "September October November December",
            "聖經節期": "pascha azyma pentecoste scenopegia expiatio neomenia sabbatum "
                    "iubilaeus encaenia",
            "時段": "mane vesper meridies nox hodie cras heri semper aeternum",
        },
    },
}

CURATED_LOWER = {
    "offices": {
        "title": "教會職分、聖統與禮儀用語",
        "groups": {
            "聖統": "papa pontifex episcopus archiepiscopus patriarcha cardinalis "
                    "presbyter sacerdos diaconus subdiaconus clericus laicus "
                    "abbas prior monachus monialis",
            "職務與機構": "curia congregatio dicasterium synodus concilium conclave "
                    "dioecesis paroecia provincia sedes cathedra vicarius legatus "
                    "nuntius protonotarius",
            "彌撒各部": "introitus kyrie gloria collecta lectio graduale alleluia "
                    "evangelium homilia credo offertorium praefatio sanctus canon "
                    "consecratio communio postcommunio benedictio",
            "聖事與禮儀": "sacramentum baptismus confirmatio eucharistia paenitentia "
                    "unctio ordo matrimonium missa liturgia officium breviarium "
                    "altare hostia calix",
        },
    },
    "liturgical_year": {
        "title": "禮儀年與時辰誦讀",
        "groups": {
            "禮儀時節": "adventus nativitas epiphania quadragesima passio resurrectio "
                    "ascensio pentecoste tempus per annum",
            "慶典等級": "sollemnitas festum memoria feria dominica vigilia octava",
            "時辰": "matutinum laudes prima tertia sexta nona vesperae completorium "
                    "horae psalterium antiphona responsorium hymnus canticum",
        },
    },
    "documents": {
        "title": "教廷文獻體裁與公文用語",
        "groups": {
            "文獻體裁": "bulla breve constitutio decretum decretalis encyclica exhortatio "
                    "epistula allocutio motu proprio rescriptum indultum privilegium",
            "公文套語": "datum actum praesentibus venerabilis dilectus salutem "
                    "apostolica benedictio perpetuam memoriam mandamus statuimus "
                    "declaramus definimus promulgamus",
            "法律用語": "canon ius lex praeceptum obligatio dispensatio censura "
                    "excommunicatio anathema irritus nullus vigor",
        },
    },
    "scholastic": {
        "title": "經院哲學與神學術語",
        "groups": {
            "存有與本質": "ens essentia existentia substantia accidens natura suppositum "
                    "quidditas subsistentia persona",
            "因果與變化": "causa effectus actus potentia forma materia finis principium "
                    "motus generatio corruptio",
            "認識": "intellectus ratio voluntas species phantasma abstractio conceptus "
                    "scientia sapientia fides",
            "神學": "gratia natura meritum praedestinatio iustificatio satisfactio "
                    "transsubstantiatio processio missio visio beatifica",
        },
    },
}


def harvest_names(units, lm, minimum: int) -> dict[str, int]:
    """Find the names in a corpus given as units of running text.

    Three things have to be right or the table fills with words that are not
    names.  Capitalisation has to be counted away from the start of a unit,
    because ``Cumque`` opens hundreds of Vulgate verses and is a conjunction.
    Counting has to be by lemma, or ``Dominus``, ``Domini``, ``Domino``,
    ``Dominum`` and ``Domine`` arrive as five separate names.  And a token that
    the treebanks already know as a common word is not promoted to a name however
    it is capitalised.
    """
    seen: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for unit in units:
        # Split into sentences first: a whole encyclical has one first word, and
        # judging capitalisation against that would let every sentence-initial
        # word through.
        for sentence in SENTENCE_RE.split(unit):
            words = L.words(sentence)
            for position, word in enumerate(words):
                lemma = lm.lemma(word)
                key = L.fold(lemma) if lemma else L.fold(word)
                seen[key][0] += 1
                if position and word[:1].isupper():
                    seen[key][1] += 1
    return {
        key: total
        for key, (total, upper) in seen.items()
        if total >= minimum and upper / total >= CAPITAL_RATIO
    }


def surface_forms(corpus_words, lm=None) -> dict[str, Counter]:
    """Every capitalised spelling seen for each folded key, counted once.

    Built in a single pass on purpose.  Asking for one name's commonest spelling
    by re-scanning the corpus is fine; asking it five hundred times over three
    million words is a quarter of a billion comparisons, and it is why the first
    version of this script never finished.

    🚨 索引必須與 `harvest_names` 用同一把鍵，也就是**詞形還原後**的折疊。原本
    這裡按原樣詞形折疊，詞條卻按 lemma 折疊，兩邊對不上時 `display_form` 就把
    lemma 本身當詞條印出去——書上因此印過 `iohannes`、`iordanes`、`zebedaeus`
    這種小寫又 I/U 化的怪拼法（武加大印的是 Joannes、Jordanes、Zebedæus），
    最糟的一條是 `aelius`：辭典收了羅馬氏族名 Aelius，詞形還原就把 `Eliam`
    （厄里亞，二十六次）認成它的變化形，於是聖經專名表裡多出一個羅馬人。
    """
    forms: dict[str, Counter] = defaultdict(Counter)
    for word in corpus_words:
        if word[:1].isupper():
            lemma = lm.lemma(word) if lm else None
            forms[L.fold(lemma) if lemma else L.fold(word)][word] += 1
    return forms


def display_form(forms: dict[str, Counter], folded: str) -> str:
    """Print the name the way the edition prints it, not the way we folded it.

    An all-capital spelling is passed over while any other exists: the council
    documents end in pages of signatures set in caps (``IOSEPHUS``,
    ``FRANCISCUS``), and taking the commonest spelling made those the entry.
    """
    seen = forms.get(folded)
    if not seen:
        return folded
    mixed = [form for form, _ in seen.most_common() if not form.isupper()]
    return mixed[0] if mixed else seen.most_common(1)[0][0]


def proper_noun_keys() -> set[str]:
    """Folded keys the Latin dictionary itself lists as a capitalised noun.

    The test is the dictionary's own capitalisation, not its part-of-speech
    code: ``Vergilius`` and ``Antonius`` are also listed as adjectives, and
    refusing anything with an adjective reading would throw Virgil out of a
    table of names.  What it does refuse is ``cardinalis``, ``redemptor``,
    ``orientalis``, ``encyclicus`` -- common words that a capitalised sentence
    position promoted to names.
    """
    return {
        L.fold(entry.lemma)
        for entry in W.load()
        if entry.pos == "N" and entry.lemma[:1].isupper()
    }


# 思高逐節對位搆不到的，依思高譯本體例人工補上。
# 擁有者 2026-09-16：「思高無法就你自己翻譯啊，不能沒有中文。」
#
# 🚨 這些的 zhRoute 一律標「思高體例（人工補）」，與逐節對位來的分得開。
# 對位有證據、這裡沒有；混在同一個標籤底下，日後就沒有人能重驗哪一條是查出來的、
# 哪一條是寫上去的。括號裡記的是它為什麼補得出來——變格還原，或哪一節定的順序。
VULGATE_NAMES_ZH: dict[str, tuple[str, str]] = {
    "Pharaonis": ("法郎", "Pharao 的屬格"),
    "Pharaonem": ("法郎", "Pharao 的賓格"),
    "Simon": ("西滿", "新約作西滿；瑪加伯上下作息孟"),
    "Manasse": ("默納協", "Manasses 的奪格"),
    "Galaad": ("基肋阿得", ""),
    "Tobias": ("多俾亞", "多俾亞傳；父子同名，思高父作托彼特、子作多俾亞"),
    "Jerosolymis": ("耶路撒冷", "Jerosolyma 的複數奪格"),
    "Jerosolymam": ("耶路撒冷", "Jerosolyma 的賓格"),
    "Israëli": ("以色列", "Israel 的與格"),
    "Ananias": ("阿納尼雅", ""),
    "Satanas": ("撒殫", ""),
    "Libano": ("黎巴嫩", "Libanus 的奪格"),
    "Medorum": ("瑪待人", "Medi 的屬格複數"),
    "Maacha": ("瑪阿加", ""),
    "Nathanaël": ("納塔乃耳", ""),
    "Ægyptiis": ("埃及人", "Ægyptii 的與格／奪格複數"),
    "Capharnaum": ("葛法翁", ""),
    "Sidrach": ("沙得辣客", "達 1:7 三人順序：Sidrach、Misach、Abdenago"),
    "Misach": ("默沙客", "達 1:7 三人順序：Sidrach、Misach、Abdenago"),
    "Abdenago": ("阿貝得乃哥", "達 1:7 三人順序：Sidrach、Misach、Abdenago"),
    "Israëlitæ": ("以色列人", "Israëlita 的複數"),
    "Chananæi": ("客納罕人", "Chananæus 的複數"),
    "Nahasson": ("納赫雄", ""),
    "Zebedæi": ("載伯德", "Zebedæus 的屬格"),
    "Galilæus": ("加里肋亞人", ""),
    "Hevæi": ("希威人", "Hevæus 的複數"),
    "Saphat": ("沙法特", ""),
    "Rages": ("辣革斯", "多俾亞傳的瑪待城邑"),
}


LOOKUP_NAME_MINIMUM = 50
"""讀本沒出現的名字要多常見才收進附錄。

擁有者 2026-09-16：「名字除了聖經和教會常見的其他不用。」原本這張表收五百
八十五條，其中四百七十七條讀本五十章根本不出現，末端是 Jeroham、Machir、
Beor 這種只在系譜裡出現一兩次的人——查閱價值近乎零，卻佔掉一半篇幅，而且
正是這批補不出中文。門檻只管這一批：讀本實際出現的一律全留，不論多罕見。
"""


def printable_names(rows: list[dict]) -> list[dict]:
    """讀本所見的全留；只作查閱的，武加大頻次夠高才留。再把人工譯名補上。"""
    kept = [
        row for row in rows
        if row.get("tier") == "讀本所見"
        or row.get("vulgateFrequency", 0) >= LOOKUP_NAME_MINIMUM
    ]
    for row in kept:
        if (row.get("zh") or "").strip():
            continue
        hit = VULGATE_NAMES_ZH.get(row["headword"])
        if hit:
            row["zh"], row["zhRoute"] = hit[0], "思高體例（人工補）"
            if hit[1]:
                row["zhEvidence"] = hit[1]
    return kept


GLOSS_CACHE = (ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
               / "appendix-gloss-zh.json")


def reapply_gloss_cache(payload: dict) -> int:
    """把 gloss_latin_appendices_zh.py 存下來的中文貼回剛重建的表。

    🚨 這一步不是最佳化，是防止重建變成退步。這支腳本重算的是**字形與語料佐證**，
    中文是另一支問模型問出來的；重建一次，數字、親屬、曆法、動詞主要部分那幾張表
    的一千一百九十二條中文就全部歸零，而版面照排、稽核照過，印出來是一千兩百條
    「（中文待補）」——書本身看起來完全正常。已經發生過兩次。
    快取的鍵與那支相同（去長音、I/J 與 U/V 同字），所以這裡零模型呼叫就能補回。
    補不回來的才留白：那是真的還沒問過，不是被自己洗掉的。
    """
    if not GLOSS_CACHE.exists():
        return 0
    # 🚨 快取的鍵是**原樣的詞條**，不是折疊過的字形（gloss_latin_appendices_zh
    # 那支就是 cache.get(headword)）。自作主張套一個 fold 會補回一千零六十二條、
    # 漏掉一百三十條帶長音與逗號的——而漏掉的長相與「本來就沒有中文」一模一樣。
    cache = json.loads(GLOSS_CACHE.read_text(encoding="utf-8"))
    restored = 0
    for section in ("upper", "lower"):
        for table in payload.get(section, {}).values():
            for entry in table.get("entries", []):
                if (entry.get("zh") or "").strip():
                    continue
                hit = cache.get(entry.get("headword", ""))
                if hit and (hit.get("zh") or "").strip():
                    entry["zh"] = hit["zh"]
                    entry.setdefault("zhRoute", hit.get("route", "gloss 快取"))
                    restored += 1
    return restored


def latin_register_zh() -> dict[str, tuple[str, str]]:
    """折疊後的拉丁字形 → （已定的中文名，哪一份登錄說的）。

    專名的中文一律從登錄取，不從模型取——這一條是這系列付過代價才立的：信望愛
    那條路徑把字典釋義當成名字，四十九筆錯的印在紙上，每一筆看起來都正常。

    一列只出一個中文（依該表的欄位優先序），再拿**跨列**的結果比對：
    同一個拉丁字形對到兩個不同的人就不填。詞庫裡有兩位 Saturninus（迦太基
    殉道者、非洲總督）、兩位 Julianus（背教者、埃克拉努姆的）、兩位 Theophilus
    （凱撒利亞的、亞歷山卓的）——挑一個等於在附錄裡指認錯人，而印出來完全看不
    出來。留白再問。
    🚨 比對要以「列」為單位，不是以「欄」：同一列的 name_catholic_sgs 與
    name_recommended 本來就可能寫法不同（奧利振／俄利根），照欄位比會把一個
    人判成兩個人，Origenes 就是這樣被判成歧義而空掉的。
    """
    from proper_name_categories import fold as fold_zh, fold_latin, load_registers  # noqa: PLC0415

    # 表 → （取中文的欄位優先序，提供字形的欄位）
    SOURCES = (
        ("deities", ("name_recommended",), ("name_original", "name_english")),
        ("place_names", ("name_recommended",), ("name_original", "name_english")),
        ("rulers", ("name_recommended",), ("name_original", "name_english")),
        ("philosophers", ("name_recommended",), ("name_original", "name_english")),
        ("scientists", ("name_recommended",), ("name_original", "name_english")),
        ("theologians", ("name_catholic_sgs", "name_recommended", "name_protestant"),
         ("name_original", "name_latin_std", "name_english")),
    )
    candidates: dict[str, set[tuple[str, str]]] = {}
    registers = load_registers()
    for group, zh_fields, form_fields in SOURCES:
        for row in registers.get(group, []):
            zh = next((v for v in ((row.get(f) or "").strip() for f in zh_fields) if v), "")
            if not zh:
                continue
            english = (row.get("name_english") or "").strip()
            forms = [(row.get(field) or "").strip() for field in form_fields]
            # 同一個實體的拉丁拼法常常掛在變體欄（Ἰταλία 那一列的變體是 Italia）。
            forms += [part.strip() for part in (row.get("name_variants") or "").split("／")]
            for value in forms:
                if not value:
                    continue
                for key in {fold_zh(value), fold_latin(value), L.fold(value)}:
                    if key:
                        candidates.setdefault(key, set()).add((zh, group, english))

    out: dict[str, tuple[str, str]] = {}
    for key, rows in candidates.items():
        wanted = CORPUS_REFERENT.get(key)
        if wanted:
            picked = [(zh, group) for zh, group, english in rows if english == wanted]
            if len(picked) == 1:
                out[key] = picked[0]
                continue
            # 指名的那一列不在詞庫裡（或有兩列同名）——別退回去隨便挑一列，
            # 那正是這張表要防的事。留白，讓缺口看得見。
            continue
        if len({zh for zh, _, _ in rows}) == 1:
            zh, group, _ = next(iter(rows))
            out[key] = (zh, group)
    return out


def latin_register_keys() -> set[str]:
    """Folded name forms the registers vouch for, **from their Latin columns only**.

    🚨 Not ``name_english``/``name_en``.  The episcopal register is English-only,
    and letting it vouch put ``Peter``, ``France`` and ``Seneca`` into a table of
    Latin names — the English spellings had leaked into the corpus from the
    editions' own front matter and the register then confirmed them.
    """
    from proper_name_categories import fold as fold_zh, fold_latin, load_registers  # noqa: PLC0415

    keys: set[str] = set()
    registers = load_registers()
    for group, fields in (
        ("deities", ("name_original",)),
        ("place_names", ("name_original",)),
        ("rulers", ("name_original",)),
        ("theologians", ("name_original", "name_latin_std")),
    ):
        for row in registers.get(group, []):
            for field in fields:
                value = (row.get(field) or "").strip()
                if value:
                    keys |= {fold_zh(value), fold_latin(value), L.fold(value)}
    return {key for key in keys if key}


def align_chinese(latin_names: set[str], lm) -> dict[str, dict]:
    """Read each name's Chinese out of the aligned Studium Biblicum chapters.

    The edition underlines its proper names, so each verse offers a small
    candidate set rather than a whole sentence to guess from.  A Latin name is
    matched to whichever candidate shares the most verses with it, provided that
    candidate is not simply common everywhere.
    """
    if not SIGAO.exists():
        return {}
    data = json.loads(SIGAO.read_text(encoding="utf-8"))
    latin_chapters = L.vulgate_chapters()

    by_latin: dict[str, Counter] = defaultdict(Counter)
    latin_verse_total: Counter = Counter()
    chinese_verse_total: Counter = Counter()

    # Match on book and chapter, never on lesson number.  Lesson numbers are
    # assigned by the difficulty sort, so they move whenever the vocabulary
    # changes, while the Chinese export keeps the numbers it was written with.
    # Keying on them silently pairs Exodus 3 with John 17 and the alignment
    # collapses from fifty-six names to one -- which is exactly what happened.
    pages = [(c["book"], c["latinChapter"], c["verses"]) for c in data["chapters"]]
    # Chapters fetched purely to name the appendix.  The reader does not print
    # them, but the edition underlines its proper names in them just the same,
    # and that is all the alignment needs.
    if EXTRA_CHAPTERS.exists():
        for key, page in json.loads(EXTRA_CHAPTERS.read_text(encoding="utf-8")).items():
            book, chapter = key.split(".")
            pages.append((book, int(chapter), page["verses"]))

    for book, latin_chapter, chinese_verses in pages:
        verses = latin_chapters.get((book, latin_chapter))
        if not verses:
            continue
        chinese = {v["verse"]: v for v in chinese_verses}
        for number, text in verses.items():
            target = chinese.get(number)
            if not target:
                continue
            words = L.words(text)
            names_here = set()
            for position, word in enumerate(words):
                if not position or not word[:1].isupper():
                    continue
                lemma = lm.lemma(word)
                key = L.fold(lemma) if lemma else L.fold(word)
                if key in latin_names:
                    names_here.add(key)
            zh_here = {n for n in target["properNames"] if n}
            for name in names_here:
                latin_verse_total[name] += 1
                for zh in zh_here:
                    by_latin[name][zh] += 1
            for zh in zh_here:
                chinese_verse_total[zh] += 1

    resolved: dict[str, dict] = {}
    for name, counts in by_latin.items():
        # 🚨 平手不能交給 most_common 決定。候選是從 `properNames` 的 **set** 累進
        # 來的，set of str 的走訪順序每個行程都不一樣（PYTHONHASHSEED），同分的
        # 兩個候選誰先進 Counter 就跟著變。實測同一份輸入連跑兩次，附錄的中文會
        # 漂五筆左右——有的換人，有的因為換到的候選過不了下面那兩道閘而整格變空。
        # 靠字面排序把它釘死：同分時取哪一個可以再議，但不能每次都不一樣。
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        best, hits = ranked[0]
        appearances = latin_verse_total[name]
        runner_up = ranked[1][1] if len(ranked) > 1 else 0
        # 三道閘，各擋一種假對位：
        #   1. 候選要跟著這個名字走過它大部分的節。
        #   2. 候選不能是「到處都跟著」的陪襯詞（以色列、耶穌、耶路撒冷）。
        #   3. 候選要**明顯**贏過第二名，不能只是並列出現的同伴。
        #
        # 🚨 倍率 2.5 太緊，誤殺的正好是最常見的名字：Judas 八十節裡七十六節
        # 跟著「猶大」，卻因為猶大全書出現兩百四十一次而被擋（241 > 76×2.5）；
        # 厄里叟十四節全中也一樣被擋。書上因此 Judas（語料 319 次）整格空白。
        # 放寬到 8 之後，以色列（612 次）那種陪襯詞照樣擋得住。
        #
        # 🚨 第三道閘是新加的，擋的是另一種錯：達尼爾書那三個人總是並列出現，
        # Sidrach、Misach、Abdenago 的候選完全相同（阿貝得乃哥 12、沙得辣客 12、
        # 默沙客 11），原本三個都判成「沙得辣客」——三條裡有兩條是印錯的人名，
        # 而印出來完全看不出來。分不出來就該留白。
        if hits < max(2, appearances * 0.6):
            continue
        if chinese_verse_total[best] > hits * 8:
            continue
        if hits < runner_up * 1.3:
            continue
        resolved[name] = {
            "zh": best, "sharedVerses": hits, "latinVerses": appearances,
            "route": "sigao-underline-alignment",
        }
    return resolved


def taught_headwords() -> set[str]:
    path = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {L.fold(entry["headword"]) for entry in data["entries"]}


def names_in_printed_chapters(latin_names: set[str], lm) -> set[str]:
    """The subset a reader of these fifty chapters will actually run into."""
    if not SCRIPTURE_PLAN.exists():
        return set()
    plan = json.loads(SCRIPTURE_PLAN.read_text(encoding="utf-8"))
    chapters = L.vulgate_chapters()
    seen: set[str] = set()
    for row in plan["chapters"]:
        # The volume now opens with ten liturgical formulas, which carry no book
        # or chapter; only the forty Bible chapters have names to find.
        if row.get("kind") == "liturgy" or not row.get("book"):
            continue
        for text in chapters[(row["book"], row["chapter"])].values():
            for position, word in enumerate(L.words(text)):
                if not position or not word[:1].isupper():
                    continue
                lemma = lm.lemma(word)
                key = L.fold(lemma) if lemma else L.fold(word)
                if key in latin_names:
                    seen.add(key)
    return seen


def curated_table(spec: dict, counts: Counter, words_index) -> dict:
    rows = []
    for group, words in spec["groups"].items():
        for word in words.split():
            hits = words_index.get(L.fold(word), [])
            best = hits[0] if hits else None
            rows.append({
                "group": group,
                "headword": best.lemma if best else word,
                "forms": best.form if best else word,
                "glossEn": best.definition if best else "",
                "pos": best.pos if best else "",
                "ecclesiastical": bool(best and best.ecclesiastical),
                "corpusFrequency": counts.get(L.fold(word), 0),
                "attested": counts.get(L.fold(word), 0) > 0,
                "dictionaryRoute": "whitakers-words" if best else "missing",
            })
    return {"title": spec["title"], "entries": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lm = Lemmatiser()
    words_index = W.index_by_lemma(W.load())

    vulgate_words = [w for text in L.vulgate_verses().values() for w in L.words(text)]
    church_words: list[str] = []
    for doc in L.church_documents():
        church_words.extend(L.words(doc["text"]))
    for path in sorted(CHURCH.rglob("*.txt")):
        church_words.extend(L.words(path.read_text(encoding="utf-8", errors="replace")))

    vulgate_counts = Counter(L.fold(w) for w in vulgate_words)
    church_counts = Counter(L.fold(w) for w in church_words)

    vulgate_forms = surface_forms(vulgate_words, lm)
    church_forms = surface_forms(church_words, lm)

    biblical_names = harvest_names(L.vulgate_verses().values(), lm, NAME_MINIMUM)
    chinese = align_chinese(set(biblical_names), lm)
    # Which names the reader actually meets is the number that matters.  A rate
    # quoted against every name in the Vulgate says the alignment failed when
    # what really happened is that five hundred of those names are in chapters
    # this reader does not print.
    in_reader = names_in_printed_chapters(set(biblical_names), lm)
    # The contract keeps names and lessons disjoint.  Deus, Christus, Israel and
    # Evangelium are capitalised throughout the Vulgate and so are harvested as
    # names, but Collins teaches them as vocabulary; a word cannot be in both.
    taught = taught_headwords()
    biblical_names = {k: v for k, v in biblical_names.items() if k not in taught}
    name_rows = []
    for folded, count in sorted(biblical_names.items(), key=lambda kv: -kv[1]):
        match = chinese.get(folded, {})
        name_rows.append({
            "headword": display_form(vulgate_forms, folded),
            "folded": folded,
            "vulgateFrequency": count,
            "type": "divine" if folded in DIVINE else "",
            "tier": "讀本所見" if folded in in_reader else "武加大其餘",
            "zh": match.get("zh", ""),
            "zhRoute": match.get("route", ""),
            "zhEvidence": (f"{match['sharedVerses']}/{match['latinVerses']} 節同現"
                           if match else ""),
        })

    # A name the Vulgate never uses but the modern curia does -- Taiuania,
    # Foederatae Civitates -- is the one register no earlier reader in this
    # series had to cover, so it gets a table of its own.
    modern_units = [doc["text"] for doc in L.church_documents()]
    modern_units += [path.read_text(encoding="utf-8", errors="replace")
                     for path in sorted(CHURCH.rglob("*.txt"))]
    modern_names = harvest_names(modern_units, lm, NAME_MINIMUM * 2)
    modern_names = {k: v for k, v in modern_names.items() if k not in taught}
    # 🚨 大寫是線索，不是證據。只靠「句中大寫且夠常見」收下來的四百條裡，有三百
    # 一十九條不是專名：縮寫（Psal、Joan、Virg、W）、副詞與形容詞（Graece、Latine、
    # Cardinalis）、普通名詞的變化形（Redemptoris、Orientalium、Novembris、
    # Encyclicae）、英文（God、Lord、Page），以及簽名頁的全大寫（IOSEPHUS）。
    # 那張表因此四百條全部沒有中文，也沒有人能替它補中文——該修的是表本身。
    #
    # 一個詞要留下來，得有一份東西替它作證，兩條路擇一：
    #   1. 專名登錄的**拉丁欄**認得它（英文欄不算，見 latin_register_keys）；
    #   2. 拉丁辭典把它收成**大寫開頭的名詞**。
    # 兩條都不過就不收。寧可表短而每一條都是名字，也不要四百條裡三百多條不是。
    vouched = latin_register_keys() | proper_noun_keys()
    # 中文也從登錄取，跟上冊那張表從思高逐節對位取是同一個原則：是證據，不是翻譯。
    # 上冊那五百八十五條已經定出來的中文先用（同一個名字在兩張表必須讀起來一樣），
    # 其次才問登錄；兩邊都沒有就留白。
    register_zh = latin_register_zh()
    biblical_zh = {row["folded"]: row for row in name_rows if row.get("zh")}
    modern_rows = []
    for folded, count in sorted(modern_names.items(), key=lambda kv: -kv[1]):
        if folded in biblical_names or folded not in vouched or folded in NOT_A_NAME:
            continue
        zh, route = "", ""
        if folded in SIGAO_NAMES:
            zh, route = SIGAO_NAMES[folded], "思高譯本"
        elif folded in biblical_zh:
            zh, route = biblical_zh[folded]["zh"], "上冊專名表"
        elif folded in register_zh:
            zh, route = register_zh[folded]
        elif folded in SHARED_NAME:
            zh, route = SHARED_NAME[folded], "音譯（語料中數人同名）"
        modern_rows.append(
            {"headword": display_form(church_forms, folded), "folded": folded,
             "churchFrequency": count, "zh": zh, "zhRoute": route}
        )

    principal_parts = [
        {"headword": e.lemma, "forms": e.form, "glossEn": e.definition,
         "conjugation": " ".join(e.codes[:2]), "kind": e.codes[2] if len(e.codes) > 2 else ""}
        for e in W.load()
        if e.pos == "V" and e.freq in {"A", "B"} and church_counts.get(L.fold(e.lemma), 0) + vulgate_counts.get(L.fold(e.lemma), 0) > 0
    ]

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "upper": {
            "names": {"title": "人名、地名、民族與國名（武加大）",
                      "entries": printable_names(name_rows)},
            **{key: curated_table(spec, vulgate_counts, words_index)
               for key, spec in CURATED_UPPER.items()},
            "principalParts": {"title": "動詞主要部分與不規則變化",
                               "entries": sorted(principal_parts, key=lambda r: r["headword"])},
        },
        "lower": {
            **{key: curated_table(spec, church_counts, words_index)
               for key, spec in CURATED_LOWER.items()},
            "modernNames": {"title": "近現代教廷拉丁的地名、機構名與專名",
                            "entries": modern_rows},
        },
    }

    # 🚨 報實際印出來的那張表，不報過濾前的池子。這一行曾經寫「讀本所見 108，
    # 已由思高逐節對位定出中文 108（100%）」——其中二十八條是人工補的，而且分母
    # 報的是砍表前的 585。數字全對，講的卻是另一張表。
    printed = printable_names(name_rows)
    routes = Counter(r.get("zhRoute") or "（無）" for r in printed)
    print(f"聖經專名：語料採得 {len(name_rows)}，實際印出 {len(printed)}"
          f"（讀本所見全留；只作查閱的要武加大 ≥{LOOKUP_NAME_MINIMUM} 次）")
    for route, count in routes.most_common():
        print(f"    {route}：{count}")
    named_modern = sum(1 for row in modern_rows if row["zh"])
    print(f"近現代專名 {len(modern_rows)}（登錄或辭典作證過的才收），"
          f"其中 {named_modern} 條由登錄定出中文")
    for section in ("upper", "lower"):
        for key, table in payload[section].items():
            entries = table["entries"]
            attested = sum(1 for e in entries if e.get("attested", True))
            print(f"  {section:5s} {table['title']:<28s} {len(entries):>5} 條"
                  f"{'' if 'attested' not in (entries[0] if entries else {}) else f'，語料佐證 {attested}'}")
    restored = reapply_gloss_cache(payload)
    if restored:
        print(f"由 gloss 快取還原中文 {restored} 條")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
