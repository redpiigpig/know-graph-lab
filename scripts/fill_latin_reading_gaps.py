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
    "Kyrie eleison.": "上主，求祢垂憐。",
    "Christe eleison.": "基督，求祢垂憐。",
    "Oremus.": "請大家祈禱。",
    "Verbum Domini.": "上主的話。",
    "Deo gratias.": "感謝天主。",
    "Gloria tibi, Domine.": "主，願光榮歸於祢。",
    "Laus tibi, Christe.": "基督，願讚美歸於祢。",
    "Ite, missa est.": "彌撒禮成。",
    "Pax Domini sit semper vobiscum.": "願主的平安常與你們同在。",
    "Lectio sancti Evangelii secundum N.": "恭讀聖 N 所載主耶穌基督的福音。",
    "Benedicat vos omnipotens Deus, Pater, et Filius, et Spiritus Sanctus.":
        "願全能的天主，聖父、聖子、聖神降福你們。",
    "Agnus Dei, qui tollis peccata mundi: miserere nobis.":
        "除免世罪的天主羔羊，求祢垂憐我們。",
    "Agnus Dei, qui tollis peccata mundi: dona nobis pacem.":
        "除免世罪的天主羔羊，求賜我們平安。",
    "Corpus Christi.": "基督聖體。",
    "Sanguis Christi.": "基督聖血。",
    "Offerte vobis pacem.": "請大家互祝平安。",
    "Mysterium fidei:": "信德的奧蹟：",
    # The two the congregation says word for word, and where a machine rendering
    # drifts into 文言 (「願爾名見聖」) or clips a clause.
    "Pater noster, qui es in caelis, sanctificetur nomen tuum; adveniat regnum "
    "tuum; fiat voluntas tua, sicut in caelo et in terra. Panem nostrum "
    "cotidianum da nobis hodie; et dimitte nobis debita nostra, sicut et nos "
    "dimittimus debitoribus nostris; et ne nos indicas in tentationem; sed "
    "libera nos a malo.":
        "我們的天父，願祢的名受顯揚；願祢的國來臨；願祢的旨意奉行在人間，"
        "如同在天上。求祢今天賞給我們日用的食糧；求祢寬恕我們的罪過，"
        "如同我們寬恕別人一樣；不要讓我們陷於誘惑；但救我們免於凶惡。",
    "Sanctus, Sanctus, Sanctus Dominus Deus Sabaoth. Pleni sunt caeli et terra "
    "gloria tua. Hosanna in excelsis. Benedictus qui venit in nomine Domini. "
    "Hosanna in excelsis.":
        "聖、聖、聖，上主、萬有的天主。祢的光榮充滿天地。歡呼之聲，響徹雲霄。"
        "奉上主名而來的，當受讚美。歡呼之聲，響徹雲霄。",
}


def received(latin: str) -> str:
    """The published wording, if this line is one of the fixed responses."""
    key = re.sub(r"^[VRXy]\.\s*", "", latin.strip())
    key = re.sub(r"\s+", " ", key)
    return RECEIVED.get(key, "")


def liturgical_flaws(latin: str, zh: str) -> str:
    """Reject an answer that says more than the Latin said."""
    if not zh.strip():
        return "空白"
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


def prose_flaws(latin: str, zh: str) -> str:
    if not zh.strip():
        return "空白"
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
    supplied = 0
    for number, row in enumerate(pending, start=1):
        fixed = received(row["latin"]) if row["liturgical"] else ""
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
