#!/usr/bin/env python3
"""Translate every reading line the book would otherwise print as 〔中譯待補〕.

Three different gaps, one pass. The upper volume's ten liturgical formulas and
the closing Ordo Missae had been left blank on purpose; Jerome's Tobit has verses
the Studium Biblicum edition does not, because his Latin is an independent
recension; and the five readings joined to a published translation by section
number carry that translation only on the paragraph that opens each section, so
every continuation paragraph was blank.

The owner asked for all of them filled (2026-08-27), so all of them are filled
here and every line records that it is 自譯.

Liturgical lines get a stricter gate than prose, because that is where the
machine did real damage. Asked for 「R. Et cum spiritu tuo.」 it once returned
「執事：願天主與你們同在。R. 及與你的聖神同在。」 — a versicle that is not in the
Latin. So a line marked V. or R. must come back with the same single marker and
nothing else, must not introduce a speaker the Latin does not name, and must not
run to several sentences where the Latin is one short line. A line that fails
stays blank rather than shipping an invention.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import original_reader_llm as llm  # noqa: E402
from translate_latin_readings_zh import GLOSSARY, has_simplified, parse  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
MASTER = CACHE / "latin-reader-two-volumes.json"
OUTPUT = CACHE / "reading-gap-zh.json"

MARKER = re.compile(r"^(V|R)\.\s*")
SPEAKERS = ("執事", "主祭", "司鐸", "會眾", "領經", "全體", "信友")
NOTE = "自譯（研讀用，非教會核准禮儀譯本）"

PROSE_PROMPT = """你是天主教中文譯者，把下面這一段拉丁文譯成**繁體中文**。

""" + GLOSSARY + """
規則：
1. 只輸出譯文本身，不要原文、不要標題、不要說明、不要 markdown 圍欄。
2. 忠實直譯，句子讀得通順；不要改寫成演繹，不要加原文沒有的話。
3. 只用繁體中文；音譯的中間點用「‧」。
4. 段首若有編號（如「12.」），譯文保留該編號。

拉丁原文：
"""

LITURGY_PROMPT = """你是天主教中文譯者，把下面這一句禮儀經文譯成**繁體中文**。

""" + GLOSSARY + """
這是彌撒或短禱的經文，規則比一般段落嚴格：
1. 只輸出這一句的譯文，一句對一句。
2. 原文開頭若是「V.」就保留「V.」，是「R.」就保留「R.」，原文沒有就不要加。
3. **絕對不可以增加原文沒有的內容**——不可以自行補上另一方的答句，
   不可以加「執事」「主祭」「會眾」這類稱謂，除非拉丁原文裡就有那個字。
4. 方括號內是動作指示，照譯並保留方括號。
5. 只用繁體中文，不要註解、不要說明、不要 markdown 圍棧。

拉丁原文：
"""



# The fixed responses of the Mass have a received Chinese wording, and a machine
# renders them unevenly: this run produced 「心向上」 for Sursum corda, 「我們有向主」
# for Habemus ad Dominum -- which is not Chinese -- and expanded
# "Lectio sancti Evangelii secundum N." into 「聖若望福音」, inventing an evangelist
# where the Latin prints a placeholder. So the fixed lines are supplied here and
# marked `received-wording`, the way the flashcard deck hand-picks a picture
# where the automatic route is unreliable. They are what a Chinese-speaking
# congregation says; check them against 《感恩祭典》 before printing.
RECEIVED: dict[str, str] = {
    "In nomine Patris, et Filii, et Spiritus Sancti.": "因父、及子、及聖神之名。",
    "Amen.": "亞孟。",
    "Dominus vobiscum.": "願主與你們同在。",
    "Et cum spiritu tuo.": "也與你的心靈同在。",
    "Sursum corda.": "請舉心向上。",
    "Habemus ad Dominum.": "我們全心歸向上主。",
    "Gratias agamus Domino Deo nostro.": "我們要感謝上主、我們的天主。",
    "Dignum et justum est.": "這是理所當然的。",
    "Kyrie eleison.": "上主，求你垂憐。",
    "Christe eleison.": "基督，求你垂憐。",
    "Oremus.": "請大家祈禱。",
    "Verbum Domini.": "上主的話。",
    "Deo gratias.": "感謝天主。",
    "Gloria tibi, Domine.": "主，願光榮歸於你。",
    "Laus tibi, Christe.": "基督，願讚美歸於你。",
    "Ite, missa est.": "彌撒禮成。",
    "Pax Domini sit semper vobiscum.": "願主的平安常與你們同在。",
    "Lectio sancti Evangelii secundum N.": "恭讀聖 N 所載主耶穌基督的福音。",
    "Benedicat vos omnipotens Deus, Pater, et Filius, et Spiritus Sanctus.":
        "願全能的天主，聖父、聖子、聖神，降福你們。",
    "Agnus Dei, qui tollis peccata mundi: miserere nobis.":
        "除免世罪的天主羔羊，求你垂憐我們。",
    "Agnus Dei, qui tollis peccata mundi: dona nobis pacem.":
        "除免世罪的天主羔羊，求你賜給我們平安。",
    "Corpus Christi.": "基督聖體。",
    "Sanguis Christi.": "基督聖血。",
    "Offerte vobis pacem.": "請大家互祝平安。",
    "Mysterium fidei:": "信德的奧蹟：",
    "Ipse enim in qua nocte tradebatur accepta panem et tibi gratias agens "
    "benedixit, fregit, deditque discipulis suis, dicens: Accipite et manducate "
    "ex hoc omnes; hoc est enim Corpus meum, quod pro vobis defertur.":
        "他在被出賣的那天晚上，拿起麵餅，感謝了你，把麵餅分開、交給他的門徒說："
        "你們大家拿去吃：這就是我的身體，將為你們而犧牲。",
    "Domine, non sum dignus, ut intres sub tectum meum, sed tantum dic verbo, "
    "et sanabitur anima mea.":
        "主，我當不起你到我心裏來，只要你說一句話，我的靈魂就會痊癒。",
    # The two the congregation says word for word, and where a machine rendering
    # drifts into 文言 (「願爾名見聖」) or clips a clause.
}


# Nostra Aetate ends with the fifty-nine subscriptions of the Council fathers,
# and every one of them is a personal name, a see and an office. A model asked
# to translate that invents Chinese for cardinals nobody has transliterated --
# and one of them collapsed outright, returning 「聖事聖殿聖祭司聖座聖禮聖宗座聖
# 盛典聖聖聖…」 for six hundred characters, which the apparatus exemption then
# waved past the length check.
#
# So the offices are translated from a closed table and the names and sees stay
# in the Latin the document prints. This is what Chinese editions of the council
# documents do, it invents nothing a reader cannot check, and it is deterministic
# -- the model is never asked.
SUBSCRIPTION = re.compile(r"^(†\s*)?Ego\s+(.+?)\.?$")

OFFICES: list[tuple[str, str]] = [
    (r"Catholicae Ecclesiae Episcopus", "公教會主教"),
    (r"Archiepiscopus Primas", "首席總主教"),
    (r"Episcopus Primas", "首席主教"),
    (r"Concilii Secretarius Generalis", "公會議秘書長"),
    (r"Sacri Collegii Decanus", "樞機團團長"),
    (r"Protodiaconus Cardinalis", "首席執事級樞機"),
    (r"Presbyter Cardinalis", "司鐸級樞機"),
    (r"Diaconus Cardinalis", "執事級樞機"),
    (r"Administrator Perpetuus", "永久署理"),
    (r"Archiepiscopus tit\.", "領銜總主教"),
    (r"Episcopus tit\.", "領銜主教"),
    (r"Archiepiscopus", "總主教"),
    (r"Patriarcha", "宗主教"),
    (r"Episcopus", "主教"),
    (r"Cardinalis", "樞機"),
    (r"Primas", "首席主教"),
    (r"tituli|titulo", "領銜"),
    (r"\bSsmi\b", "至聖"),
    (r"\bSs\.", "諸聖"),
    (r"\bS\.", "聖"),
    (r"\bac\b|\bet\b", "暨"),
    (r"\bin\b", "於"),
    (r"\bde\b", "de"),
]


def subscription_zh(latin: str) -> str:
    """A council father's signature, with the office translated and the name kept."""
    match = SUBSCRIPTION.match(latin.strip())
    if not match:
        return ""
    body = match.group(2)
    for pattern, chinese in OFFICES:
        body = re.sub(pattern, chinese, body)
    body = re.sub(r"\s*,\s*", "，", body)
    body = re.sub(r"\s+", " ", body).strip()
    return f"† 我，{body}。"

PUBLISHED = ROOT / "data" / "originalReaders" / "latin-liturgy-received-zh.json"


def published_blocks() -> dict[str, str]:
    """The formulas whose Chinese comes from a printed missal, keyed by id.

    Six of the ten are one continuous text -- the Confiteor, the Gloria, the
    Creed, the Sanctus, the Agnus Dei, the Lord's Prayer -- and a published
    Chinese Order of Mass prints each as one block. Setting the block against the
    whole formula is exact; splitting it to match Collins's column breaks would
    not be.
    """
    if not PUBLISHED.exists():
        return {}
    return json.loads(PUBLISHED.read_text(encoding="utf-8"))["formulas"]


def formula_of_lesson() -> dict[int, str]:
    plan = CACHE / "scripture-plan.json"
    if not plan.exists():
        return {}
    return {row["lesson"]: row["id"]
            for row in json.loads(plan.read_text(encoding="utf-8"))["chapters"]
            if row.get("kind") == "liturgy"}


def received(latin: str) -> str:
    """The published wording, if this line is one of the fixed responses."""
    key = re.sub(r"^[VRXy]\.\s*", "", latin.strip())
    key = re.sub(r"\s+", " ", key)
    return RECEIVED.get(key, "")


def liturgical_flaws(latin: str, zh: str) -> str:
    """Reject an answer that says more than the Latin said."""
    if not zh.strip():
        return "空白"
    if repeats(zh):
        return "譯文重複退化"
    if has_simplified(zh):
        return "含簡體字"

    latin_marker = MARKER.match(latin.strip())
    zh_markers = re.findall(r"\b([VR])\.", zh)
    if latin_marker:
        wanted = latin_marker.group(1)
        if zh_markers != [wanted]:
            return f"對答標記不符（原文 {wanted}.，譯文 {zh_markers}）"
    elif zh_markers:
        return f"原文沒有對答標記，譯文卻有 {zh_markers}"

    # The speaker check belongs to versicles only.  A rubric's whole job is to
    # say who does what -- "[Psalmista seu cantor psalmum dicit, populo responsum
    # proferente.]" names the cantor and the people -- so comparing a Chinese
    # 會眾 against a Latin populo can never pass, and the check rejected every
    # rubric in the Mass.
    # The speaker check is for versicles.  A long Eucharistic Prayer paragraph
    # names ministers and assemblies in its own right, and holding it to the
    # same rule rejects a sound translation of the anaphora.
    is_rubric = latin.strip().startswith("[")
    if not is_rubric and len(L.words(latin)) <= 20:
        for speaker in SPEAKERS:
            if speaker in zh and speaker not in latin:
                return f"譯文自行加入稱謂「{speaker}」"

    # A short versicle cannot legitimately become several sentences -- but the
    # Amen that closes so many of them is its own sentence in Chinese and must
    # not count as evidence of padding.
    latin_words = len(L.words(latin))
    body = re.sub(r"(亞孟|阿們|阿門)。?$", "", zh.strip()).strip()
    if not is_rubric and latin_words <= 12 and len(re.findall(r"[。！？]", body)) > 1:
        return "原文一句，譯文多句"
    if len(zh) > max(24, latin_words * 6):
        return f"譯文過長（原文 {latin_words} 詞，譯文 {len(zh)} 字）"
    return ""


# A signature line and a footnote citation are mostly names and abbreviations,
# and a faithful rendering of them keeps some of that: 「參閱智 8:1；宗 14:17」 is
# the citation, not a failure to translate it.
APPARATUS_LINE = re.compile(r"^(†|\(\d+\)|Cfr\.|Cf\.)")


def repeats(zh: str) -> bool:
    """A model that has lost the thread says the same four characters for ever.

    This is the one check no exemption lifts: 「聖事聖殿聖祭司聖座聖禮聖宗座…」 is
    not a signature, a citation or a creed, whatever the line it came from.
    """
    body = re.sub(r"[，。、；：？！「」（）()\s]", "", zh)
    if len(body) < 24:
        return False
    # Counting repetitions alone flags good prose: Deus Caritas Est says 「之間的
    # 愛」 five times because the Latin says `de amore inter` five times. What
    # separates degeneration is how much of the line the repetition *is* -- half
    # of it or more, against a fifth for the parallelism.
    worst = max((len(re.findall(re.escape(body[i:i + 4]), body))
                 for i in range(len(body) - 3)), default=0)
    if worst * 4 > len(body) * 0.5:
        return True
    # The collapse that actually happened was not a repeated phrase but a
    # repeated character: 聖 was seven characters in ten of a six-hundred-
    # character line. No Chinese sentence does that; the densest real line in
    # this book is the Creed at two in ten.
    from collections import Counter
    return Counter(body).most_common(1)[0][1] > len(body) * 0.35


def prose_flaws(latin: str, zh: str) -> str:
    if not zh.strip():
        return "空白"
    if repeats(zh):
        return "譯文重複退化"
    if has_simplified(zh):
        return "含簡體字"
    if (not APPARATUS_LINE.match(latin.strip())
            and re.search(r"[A-Za-z]{4,}", zh.replace("V.", "").replace("R.", ""))):
        return "殘留拉丁文"
    # A citation renders longer than its Latin: 「(2) 參閱智慧篇 8:1；宗徒大事錄
    # 14:17」 spells out book names the Latin abbreviates.
    if (not APPARATUS_LINE.match(latin.strip())
            and len(zh) > max(40, len(L.words(latin)) * 8)):
        return "譯文過長"
    return ""


def translate(latin: str, liturgical: bool) -> tuple[str, str]:
    prompt = (LITURGY_PROMPT if liturgical else PROSE_PROMPT) + latin
    problem = ""
    for attempt in range(3):
        try:
            raw = llm.call_model(prompt, max_tokens=1200)
        except Exception as exc:  # noqa: BLE001
            problem = f"{type(exc).__name__}"
            time.sleep(6)
            continue
        text = raw.strip()
        if text.startswith("["):
            try:
                text = " ".join(parse(text))
            except Exception:  # noqa: BLE001
                pass
        text = text.strip().strip('"')
        problem = liturgical_flaws(latin, text) if liturgical else prose_flaws(latin, text)
        if not problem:
            return text, llm.current_model()
        time.sleep(2)
    raise ValueError(problem or "未通過檢查")


def save(store: dict) -> None:
    """Write through a temporary file.

    A run killed mid-write leaves a truncated cache, and the next run reads it
    as "almost nothing done" and starts again: three hundred and fifteen filled
    lines came back as sixteen once. Replacing atomically makes a kill lose at
    most the current line.
    """
    temporary = OUTPUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
    temporary.replace(OUTPUT)


def gaps(master: dict) -> list[dict]:
    rows: list[dict] = []
    for volume in master["volumes"]:
        for lesson in volume["lessons"]:
            liturgical = lesson["lesson"] <= 10 and volume["volume"] == 1
            for index, row in enumerate(lesson["reading"]):
                if row["zh"]:
                    continue
                rows.append({
                    "key": f"v{volume['volume']}:l{lesson['lesson']}:{index}",
                    "latin": row["latin"], "liturgical": liturgical,
                    "where": f"{volume['name']} 第 {lesson['lesson']} 課　{lesson['title']}",
                })
    terminal = master["terminal"]
    for index, row in enumerate(terminal["segments"]):
        if row["zh"]:
            continue
        rows.append({
            "key": f"terminal:{index}", "latin": row["latin"],
            "liturgical": True, "where": terminal["title"],
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    # The shared Gemini/NVIDIA chain takes minutes a line when the overnight
    # fleet has it, and its liturgical output was the reason these lines were
    # left blank in the first place.  Named explicitly, the Anthropic tier
    # answers in a second or two and returns the received wording: it renders
    # 「V. In nomine Patris」 as 「因父、及子、及聖神之名」 and 「Sursum corda」 as
    # 「舉心向上」, which is what the congregation actually says.
    ap.add_argument("--engine", default="auto")
    args = ap.parse_args()

    if args.engine != "auto":
        llm.select_chain(args.engine)

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    store = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {"lines": {}}
    pending = [row for row in gaps(master) if row["key"] not in store["lines"]]
    if args.limit:
        pending = pending[: args.limit]
    print(f"待補 {len(gaps(master))} 段；本輪處理 {len(pending)}；已完成 {len(store['lines'])}")

    failures: list[str] = []
    blocks = published_blocks()
    lesson_formula = formula_of_lesson()
    supplied = 0
    for number, row in enumerate(pending, start=1):
        fixed = received(row["latin"]) if row["liturgical"] else ""
        hand = "" if fixed else subscription_zh(row["latin"])
        if not fixed and row["key"].startswith("v1:l"):
            lesson = int(row["key"].split(":")[1][1:])
            index = int(row["key"].split(":")[2])
            formula = lesson_formula.get(lesson)
            if index == 0 and formula in blocks:
                fixed = blocks[formula]
        if fixed:
            marker = MARKER.match(row["latin"].strip())
            prefix = f"{marker.group(1)}. " if marker else ""
            store["lines"][row["key"]] = {
                "zh": prefix + fixed, "engine": "received-wording",
                "note": "教會通行本文（付印前請對照《感恩祭典》）",
                "liturgical": True, "latin": row["latin"],
            }
            supplied += 1
            continue
        if hand:
            store["lines"][row["key"]] = {
                "zh": hand, "engine": "hand-translated", "note": NOTE,
                "liturgical": row["liturgical"], "latin": row["latin"],
            }
            continue
        try:
            zh, engine = translate(row["latin"], row["liturgical"])
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{row['where']}｜{row['latin'][:40]}｜{exc}")
            continue
        store["lines"][row["key"]] = {
            "zh": zh, "engine": engine, "note": NOTE,
            "liturgical": row["liturgical"], "latin": row["latin"],
        }
        if number % 10 == 0 or number == len(pending):
            save(store)
            print(f"  {number}/{len(pending)}　累計 {len(store['lines'])}", flush=True)

    store["generatedOn"] = date.today().isoformat()
    save(store)
    print(f"完成 {len(store['lines'])}／{len(gaps(master))}；其中通行本文 {supplied}；本輪未過 {len(failures)}")
    for line in failures[:10]:
        print("   ", line)
    if args.write:
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
