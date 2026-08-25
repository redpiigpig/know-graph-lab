#!/usr/bin/env python3
"""Traditional-Chinese for the readings that have none, in Catholic register.

Twenty-seven of the lower volume's fifty readings already have Chinese, because
they are this repository's own papal and conciliar documents. The other
twenty-three are the patristic and medieval texts fetched from The Latin
Library, and the Ordo Missae that closes the volume. This translates those.

Register is the whole problem. A general-purpose Chinese Bible vocabulary is
Protestant, and putting it beside the Vulgate produces a reader that says 上帝
where the printed Chinese says 天主, 聖靈 for 聖神, 使徒 for 宗徒, 恩典 for 恩寵,
稱義 for 成義. Those are not stylistic preferences; they are the difference
between the two Chinese Christian vocabularies, and mixing them inside one book
makes it belong to neither. So the terminology is fixed in the prompt, not left
to the model, and it follows the Studium Biblicum usage that the upper volume
already prints.

**These are study translations, labelled 自譯.** The Chinese-speaking Church has
its own approved liturgical translation of the Mass (《感恩祭典》), and this is
not it. A reader must be able to tell a rendering made for study from the text a
congregation actually says, so every unit carries that label and the Ordo
carries it twice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opencc  # noqa: E402

import latin_source_texts as L  # noqa: E402
import original_reader_llm as llm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
CHURCH_PLAN = CACHE / "church-plan.json"
LITURGY = CACHE / "liturgy.json"
OUTPUT = CACHE / "readings-zh.json"

_S2T = opencc.OpenCC("s2t")

# Roughly a page of Latin at a time: long enough for the model to see the
# argument, short enough that a failure costs one segment.
SEGMENT_WORDS = 110

GLOSSARY = """天主教中文定名（必須照用，不得換成新教用語）：
Deus 天主（不是上帝、不是神）｜Spiritus Sanctus 聖神（不是聖靈）
apostolus 宗徒（不是使徒）｜gratia 恩寵（不是恩典）｜iustificatio 成義（不是稱義）
gloria 光榮（不是榮耀）｜caritas 愛德｜fides 信德｜spes 望德
ecclesia 教會｜episcopus 主教｜sacerdos 司祭｜presbyter 司鐸｜diaconus 執事
sacramentum 聖事｜baptismus 聖洗｜eucharistia 聖體｜confessio 告明
paenitentia 懺悔｜missa 彌撒｜altare 祭台｜hostia 祭品
oratio 祈禱｜psalmus 聖詠｜evangelium 福音｜propheta 先知｜angelus 天使
regnum caelorum 天國｜resurrectio 復活｜salus 救恩｜peccatum 罪過
anima 靈魂｜caro 肉身｜Verbum 聖言｜monachus 隱修士｜abbas 院長｜regula 會規
Iesus 耶穌｜Christus 基督｜Maria 瑪利亞｜Ioannes 若望｜Petrus 伯多祿
Paulus 保祿｜Moyses 梅瑟｜David 達味｜Israel 以色列｜Ierusalem 耶路撒冷
"""

PROMPT_HEAD = """你是天主教中文譯者，把下列拉丁文譯成**繁體中文**。

""" + GLOSSARY + """
翻譯要求：
1. 逐段對應：輸入幾段就輸出幾段，不合併也不拆開。
2. 忠實直譯為主，句子要讀得通順，不要改寫成白話演繹，也不要加原文沒有的話。
3. 只用繁體中文。人名地名用上面的定名；沒列到的專名用天主教慣用譯法，
   音譯的中間點用「‧」。
4. 禮儀對答保留 V.／R. 標記，方括號內的動作指示照譯並保留方括號。
5. 拉丁原文若有明顯訛誤，照你判斷的正確讀法翻譯，不要另加註。
6. 不要輸出原文，不要加標題、註解或 markdown 圍欄。

原文每段前面都有 [1] [2] [3] 這樣的編號。輸出 JSON 陣列，
**元素個數必須與段號個數完全相同**，第 n 個元素就是第 n 段的譯文，
譯文裡不要再寫段號。寧可一段譯得短，也不要把兩段併成一段。

拉丁原文：
"""


def prompt_for(unit_title: str, latin_title: str) -> str:
    """Tell the model which work this is, in the reader's own naming.

    Left to itself the model rendered Vincentius Lirinensis as 利林的文森特,
    a Protestant-style transliteration, while the reader's own table of contents
    calls him 肋令的味增爵. The title is not decoration in the prompt: it is the
    register the translation has to match.
    """
    return (PROMPT_HEAD
            + f"本篇是《{unit_title}》（{latin_title}）。"
              f"篇中人名、書名的中文一律與這個篇名一致，不要另創譯名。" + chr(10) * 2
            + "拉丁原文：" + chr(10))


ENGLISH_HEADER = re.compile(
    r"\b(cent|A\.D\.|B\.C\.|century|edited|translated|Library|LIRINENSIS)\b", re.I)


def strip_header(text: str) -> str:
    """Drop The Latin Library's masthead before the work begins.

    Each file opens with the author in capitals, a floruit in English, and the
    work's title in capitals -- "VINCENT LIRINENSIS (5th cent. A.D.) ADVERSUS
    PROFANAS ..." -- and an excerpt taken from the top of the file translates
    that instead of the Commonitorium.
    """
    lines = text.splitlines()
    start = 0
    for index, line in enumerate(lines[:12]):
        stripped = line.strip()
        if not stripped:
            continue
        letters = [c for c in stripped if c.isalpha()]
        shouting = letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.7
        if shouting or ENGLISH_HEADER.search(stripped):
            start = index + 1
            continue
        break
    return chr(10).join(lines[start:]).strip()


def segments(text: str, size: int = SEGMENT_WORDS) -> list[list[str]]:
    """Group paragraphs into batches of roughly `size` Latin words."""
    paragraphs = [re.sub(r"\s+", " ", p).strip()
                  for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return []
    # A paragraph longer than the whole budget has to be cut, or the request
    # asks for more text than the model can return and the answer comes back
    # as truncated JSON.  Several of the Latin Library files are one
    # paragraph from first word to last.
    split: list[str] = []
    for paragraph in paragraphs:
        if len(L.words(paragraph)) <= size:
            split.append(paragraph)
            continue
        chunk: list[str] = []
        count = 0
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            words = len(L.words(sentence))
            if chunk and count + words > size:
                split.append(" ".join(chunk))
                chunk, count = [], 0
            chunk.append(sentence)
            count += words
        if chunk:
            split.append(" ".join(chunk))
    paragraphs = split
    # One paragraph per request.  Sending several and asking for the same
    # number back does not work with this tier: told four times, in numbered
    # form, to return four paragraphs, it returned two.  A request that contains
    # one paragraph cannot come back misaligned, and the cost of the extra calls
    # is a night rather than a wrong parallel text.
    return [[paragraph] for paragraph in paragraphs]


def parse(text: str) -> list[str]:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = text.split(chr(10), 1)[-1]
    if text.endswith(fence):
        text = text.rsplit(chr(10), 1)[0]
    rows = json.loads(text.strip())
    return [str(r).strip() for r in rows]


LATIN_LEAK = re.compile(r"[A-Za-z]{4,}")


def flaws(latin: list[str], chinese: list[str]) -> str:
    if len(chinese) != len(latin):
        return f"段數不符（拉丁 {len(latin)}，中文 {len(chinese)}）"
    for row in chinese:
        if not row.strip():
            return "有空白段"
        if _S2T.convert(row) != row:
            return "含簡體字"
        if LATIN_LEAK.search(row.replace("V.", "").replace("R.", "")):
            return "殘留拉丁文"
    return ""


def translate(latin: list[str], prompt: str) -> tuple[list[str], str]:
    body = "\n\n".join(latin)
    for attempt in range(3):
        try:
            answer = parse(llm.call_model(prompt + body, max_tokens=6000))
        except Exception as exc:  # noqa: BLE001
            if attempt == 2:
                raise
            time.sleep(8)
            continue
        # One paragraph in, one paragraph out.  The model sometimes returns a
        # long paragraph as two array elements; that is a formatting choice, not
        # a misalignment, so the pieces are rejoined rather than rejected.
        if len(latin) == 1 and len(answer) > 1:
            answer = ["".join(answer)]
        problem = flaws(latin, answer)
        if not problem:
            return answer, llm.current_model()
        if attempt == 2:
            raise ValueError(problem)
        time.sleep(3)
    raise ValueError("譯文未通過檢查")


def pending_readings() -> list[dict]:
    plan = json.loads(CHURCH_PLAN.read_text(encoding="utf-8"))
    rows = []
    for reading in plan["readings"]:
        if reading["chineseParallel"] == "repo-existing":
            continue
        path = ROOT / reading["sourcePath"]
        if not path.exists():
            continue
        # Strip the masthead first, then take the excerpt, so the nine hundred
        # words the reader prints are nine hundred words of the work.
        text = strip_header(path.read_text(encoding="utf-8", errors="replace"))
        # Translate what the reader prints: the same complete divisions the
        # plan measured, cut the same way.
        import build_latin_church_plan as plan_module
        if reading.get("section"):
            text = plan_module.section(text, tuple(reading["section"]))
        if reading["extent"] == "excerpt":
            text, _, _ = plan_module.complete_unit(text)
        rows.append({
            "key": f"reading:{reading['sourceRef']}",
            "title": reading["title"], "latinTitle": reading["latinTitle"],
            "lesson": reading["lesson"], "extent": reading["extent"],
            "excerptRule": reading.get("excerptRule", ""),
            "text": text,
        })
    return rows


def liturgy_units() -> list[dict]:
    if not LITURGY.exists():
        return []
    data = json.loads(LITURGY.read_text(encoding="utf-8"))
    rows = [{
        "key": f"formula:{row['id']}", "title": row["title"],
        "latinTitle": row["latinTitle"], "lesson": 0, "extent": row["extent"],
        "text": "\n\n".join(row["lines"]),
    } for row in data["formulas"]]
    rows.append({
        "key": "ordo:missa", "title": "常年期主日彌撒經文",
        "latinTitle": "Ordo Missae, tempus per annum", "lesson": 0,
        "extent": data["ordoMissae"]["extent"],
        "text": "\n\n".join(data["ordoMissae"]["lines"]),
    })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only", default="", help="只譯 key 含這段字串的單元")
    ap.add_argument("--max-units", type=int, default=0)
    args = ap.parse_args()

    store = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {"units": {}}
    units = liturgy_units() + pending_readings()
    if args.only:
        units = [u for u in units if args.only in u["key"]]
    print(f"待譯單元 {len(units)}；已完成 {len(store['units'])}")

    done = 0
    for unit in units:
        if args.max_units and done >= args.max_units:
            break
        batches = segments(unit["text"])
        # Fingerprint the Latin.  When the excerpt rule changed from "the first
        # nine hundred words" to "whole chapters", every reading's text moved,
        # and a cache keyed only on the unit name would have gone on printing
        # the old translation beside the new original.
        fingerprint = hashlib.sha256(unit["text"].encode("utf-8")).hexdigest()[:16]
        existing = store["units"].get(unit["key"])
        if existing and existing.get("sourceFingerprint") != fingerprint:
            print(f"  {unit['title']}：原文已變更，作廢舊譯 {len(existing['segments'])} 段",
                  flush=True)
            store["units"].pop(unit["key"])
        record = store["units"].setdefault(unit["key"], {
            "sourceFingerprint": fingerprint,
            "title": unit["title"], "latinTitle": unit["latinTitle"],
            "extent": unit["extent"], "excerptRule": unit.get("excerptRule", ""),
            "translationNote": "自譯（研讀用，非教會核准禮儀譯本）",
            "segments": [],
        })
        if len(record["segments"]) >= len(batches):
            continue
        print(f"  {unit['title']}（{len(batches)} 段）", flush=True)
        for index in range(len(record["segments"]), len(batches)):
            latin = batches[index]
            try:
                chinese, engine = translate(
                    latin, prompt_for(unit["title"], unit["latinTitle"]))
            except Exception as exc:  # noqa: BLE001
                print(f"    第 {index + 1} 段失敗：{exc}", flush=True)
                break
            record["segments"].append({
                "latin": latin, "zh": chinese, "engine": engine,
            })
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            store["generatedOn"] = date.today().isoformat()
            OUTPUT.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        done += 1
        print(f"    完成 {len(record['segments'])}/{len(batches)} 段", flush=True)

    total = sum(len(u["segments"]) for u in store["units"].values())
    print(f"單元 {len(store['units'])}；譯出段落 {total}")
    if args.write:
        store["generatedOn"] = date.today().isoformat()
        OUTPUT.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
