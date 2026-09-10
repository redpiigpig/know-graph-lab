#!/usr/bin/env python3
"""Build the Japanese reader's appendix tables out of the reader's own corpus.

The contract lists ten appendices; until today the book printed three. The other
seven were not missing because nobody had written them — they were missing
because a generic list of 「宗教學術語」 copied from somewhere else is not an
appendix to *this* book. An appendix indexes the work: every row here is a form
that actually occurs in the hundred readings, and carries how often and where.

Nine tables come out of this script:

* 舊字→新字 and 舊假名→新假名, derived rather than typed. OpenCC ships the
  shinjitai mapping in both directions, so the old forms are whatever the corpus
  uses that `t2jp` rewrites; the kana table is a rule table checked against real
  words from volume two.
* 助数詞, 親屬稱謂, 年號與曆法 — pattern-matched, then filtered to what occurs.
  An era name only counts when a number follows it: 文化 and 文明 are ordinary
  nouns in this corpus, and a bare string match puts them in the era table.
* 學術文體機能語 — a fixed list of academic connectives, kept only where attested.
* 宗教學術語, 佛教用語, 基督教用語, 史學用語 — classified by the model from the
  corpus's own kanji compounds, using the Chinese meanings the interlinear layer
  already settled. Nothing is glossed twice, so the appendix and the gloss row
  can never disagree.

    python -X utf8 scripts/build_japanese_appendices.py            # 看統計
    python -X utf8 scripts/build_japanese_appendices.py --write
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from dotenv import load_dotenv
from opencc import OpenCC

import original_reader_llm as llm
from translate_ebook_to_zh import _to_traditional as to_traditional

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
READINGS = CACHE / "readings.json"
INTERLINEAR = CACHE / "interlinear.json"
CLASSIFIED = CACHE / "appendix-classified.json"
VERIFIED = CACHE / "appendix-verified.json"
OUTPUT = ROOT / "data/originalReaders/vocabulary/japanese-appendices.json"

KANJI = re.compile(r"[一-鿿]+")
MIN_FREQ = 3
BATCH = 50

# 助数詞只認「數字＋量詞」的形；單看一個「人」字，全書每個「人」都會進表。
COUNTER_RE = re.compile(
    r"[一二三四五六七八九十百千万0-9０-９]+"
    r"([人匹頭羽本枚冊回度番目年月日時分秒円歳才個箇件名軒台通条巻章節句首坪里町]) "
    .strip()
)

KINSHIP = ["父", "母", "兄", "姉", "姊", "弟", "妹", "祖父", "祖母", "夫", "妻",
           "息子", "娘", "孫", "伯父", "叔父", "伯母", "叔母", "甥", "姪",
           "舅", "姑", "嫁", "婿", "親", "両親", "家族", "一族", "親族", "子孫"]

ERAS = ["明治", "大正", "昭和", "慶応", "元治", "文久", "万延", "安政", "嘉永",
        "弘化", "天保", "文政", "文化", "享和", "寛政", "天明", "安永", "明和",
        "宝暦", "享保", "元禄", "延宝", "寛文", "慶安", "寛永", "元和", "慶長",
        "文禄", "天正", "永禄", "天文", "享禄", "大永", "永正", "明応", "文明",
        "応仁", "天平", "延暦", "弘仁", "貞観", "延喜", "天暦", "治承", "建久",
        "承久", "文永", "弘安", "建武", "応永", "永享"]

CALENDAR = ["元号", "年号", "改元", "旧暦", "新暦", "太陰暦", "太陽暦", "節句",
            "彼岸", "盂蘭盆", "大晦日", "元日", "朔日", "望月", "十五夜",
            "正月", "節分", "立春", "夏至", "冬至", "月次", "歳時記"]

FUNCTION_WORDS = [
    "にほかならない", "に他ならない", "と言えよう", "といえよう", "にとどまらず",
    "にすぎない", "というのは", "にあたって", "に際して", "をめぐって",
    "において", "における", "によって", "による", "に対して", "に関して",
    "としての", "として", "とともに", "のみならず", "ばかりでなく",
    "にもかかわらず", "ながらも", "わけではない", "に基づいて", "をもって",
    "といっても", "ということ", "であろう", "でなければならない",
    "なければならない", "かもしれない", "に違いない", "はずである", "のである",
    "わけである", "に他ならぬ", "といふ", "しからば", "すなわち", "すなはち",
    "あるいは", "あるひは", "および", "ならびに", "したがって", "ゆえに", "ゆゑに",
]

# 舊假名遣的對應規則。左邊是語料裡的寫法，右邊是現代寫法；例詞在下面從語料抓。
KANA_RULES = [
    ("ゐ", "い", "ゐる（居る）、用ゐる"),
    ("ゑ", "え", "こゑ（声）、ゆゑ（故）"),
    ("ヰ", "イ", "片假名同理"),
    ("ヱ", "エ", "片假名同理"),
    ("ぢ", "じ", "はぢ（恥）、まぢか"),
    ("づ", "ず", "まづ（先づ）、いづれ"),
    ("くわ", "か", "くわん（観）、くわい（会）"),
    ("ぐわ", "が", "ぐわん（願）"),
    ("〜ふ", "〜う", "思ふ→思う、言ふ→言う"),
    ("〜ひ", "〜い", "思ひ→思い、給ひ→給い"),
    ("〜へ", "〜え", "考へ→考え、答へ→答え"),
    ("〜は", "〜わ", "言はば→言わば（語中語尾のハ行）"),
    ("〜ほ", "〜お", "たほれる→たおれる"),
    ("〜む", "〜ん", "なむ→なん（助動詞・助詞）"),
]

BUCKETS = {
    "buddhist": "佛教用語",
    "christian": "基督教用語",
    "religious_studies": "宗教學術語",
    "history": "史學用語",
}

PROMPT = """你是宗教學日文讀本的附錄編輯。下面 {count} 個日文詞取自讀本正文，\
請判斷每個詞屬於哪一類：

- buddhist：佛教的專門用語（教義、儀軌、宗派、僧職、經典名、佛菩薩名）
- christian：基督宗教的專門用語（教義、禮儀、職分、聖經相關、宗派）
- religious_studies：宗教學／宗教史／民俗學的學術用語（宗教現象、研究概念、神道與民間信仰的術語）
- history：史學用語（時代區分、制度、官職、史料類別、曆法）
- none：以上皆非（一般詞彙、日常語、與宗教學無關的專業詞）

判準要嚴：一般詞不要因為含有「経」「業」「罪」這種字就算進去。\
「経験」是一般詞不是佛教用語，「事業」也不是。

只輸出 JSON 物件，鍵是題號字串，值是類別代號：{{"1": "buddhist", "2": "none"}}

{items}"""


VERIFY_PROMPT = """下面 {count} 個日文詞被歸進「{title}」。請逐個判斷它**是不是這一類的
專門術語**——一般詞彙、日常語、泛用的抽象名詞一律回 no。

例：「制度」「歷史」「國民」「審判」是一般詞，不是史學專門術語，回 no；
「幕府」「律令」「石高」才是。「実在」「根本」是哲學泛稱，不是佛教專門術語，回 no；
「念佛」「彼岸會」「愚禿」才是。

只輸出 JSON 物件，鍵是題號字串，值是 yes 或 no：{{"1": "yes", "2": "no"}}

{items}"""


GLOSSARY_FIELDS = ("zh_recommended", "zh_protestant", "zh_catholic_sgs",
                   "zh_orthodox", "zh_tw", "zh_hk")


def glossary_rows() -> list[dict]:
    """`/translation-glossary` 的神學名詞表。接不上就回空，不要讓附錄卡在網路上。"""
    load_dotenv(".env")
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        print("  ⚠ 沒有 Supabase 連線設定，跳過詞庫對接")
        return []
    try:
        reply = requests.get(
            f"{url}/rest/v1/theological_terms"
            "?select=term_english,term_original,zh_recommended,zh_protestant,"
            "zh_catholic_sgs,zh_orthodox,zh_tw,zh_hk&limit=2000",
            headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=60)
        reply.raise_for_status()
        return reply.json()
    except Exception as error:  # noqa: BLE001
        print(f"  ⚠ 詞庫讀不到（{type(error).__name__}），跳過對接")
        return []


def attach_variants(rows: list[dict]) -> tuple[int, list[str]]:
    """把新教／天主教兩傳統的譯名接到基督教用語表上。

    權威是 `/translation-glossary`，不是這支腳本：只認**完全相同**的比對——中文對
    中文，或英文詞條一字不差。模糊比對會把「聖書」接到 canon (of scripture)、把
    「使徒」接到 Apostles' Creed，看起來有來源，其實是編出來的。詞庫沒收的就留白，
    並回報是哪幾個，讓人決定要不要往詞庫補。
    """
    glossary = glossary_rows()
    if not glossary:
        # 讀不到詞庫與「詞庫沒收這些詞」長得一模一樣：兩者都是這一欄空著。第一次
        # 就這樣——網路瞬斷，報「接上 0／14」，看起來像詞庫真的一條都沒有。所以
        # 讀不到就沿用上一版已經接好的，並且講出來。
        previous = {}
        if OUTPUT.exists():
            for table in load(OUTPUT)["tables"]:
                if table["id"] == "christian":
                    previous = {e["form"]: e for e in table["entries"]}
        carried = 0
        for row in rows:
            old = previous.get(row["form"], {})
            if old.get("variants"):
                row.update({k: old[k] for k in ("variants", "zhProtestant", "zhCatholic")
                            if k in old})
                carried += 1
        print(f"  ⚠ 詞庫這一輪沒讀到，沿用上一版已接上的 {carried} 條（不是詞庫沒有）")
        return carried, []
    index: dict[str, dict] = {}
    for record in glossary:
        for field in GLOSSARY_FIELDS:
            value = (record.get(field) or "").strip()
            if value:
                index.setdefault(value, record)
        english = (record.get("term_english") or "").strip().lower()
        if english:
            index.setdefault(english, record)
    attached, missing = 0, []
    for row in rows:
        record = index.get(row["zh"]) or index.get(row["form"])
        protestant = (record or {}).get("zh_protestant", "").strip()
        catholic = (record or {}).get("zh_catholic_sgs", "").strip()
        if record and protestant and catholic and protestant == catholic:
            # 「兩傳統同形」與「詞庫沒收」是兩件事，欄位都空著就分不出來。
            row["variants"] = "兩傳統同形"
            attached += 1
            continue
        if record and protestant and catholic and protestant != catholic:
            row["zhProtestant"] = protestant
            row["zhCatholic"] = catholic
            # 標出是詞庫哪一條在裁定：聖霊 接到的是 pneuma 那一條，「靈／聖神」
            # 不寫出處會看不懂為什麼新教那一欄不是「聖靈」。
            english = (record.get("term_english") or "").strip()
            row["variants"] = f"{protestant}／{catholic}" + (f"（{english}）" if english else "")
            row["glossaryTerm"] = record.get("term_english") or ""
            attached += 1
        else:
            missing.append(f"{row['form']}／{row['zh']}")
    return attached, missing


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(bucket: str, title: str, rows: list[dict], cached: dict[str, str]) -> list[dict]:
    """第二道：分類寬鬆，這一道專門把一般詞踢出去。

    第一版把「制度」「歷史」「國民」收進史學用語、「実在」「根本」收進佛教用語。
    附錄印的是術語表，混進泛稱就等於沒有分類。
    """
    todo = [r for r in rows if f"{bucket}|{r['form']}" not in cached]
    for start in range(0, len(todo), BATCH):
        batch = todo[start : start + BATCH]
        items = "\n".join(f"{i}. {r['form']}（{r['zh']}）" for i, r in enumerate(batch, start=1))
        reply = llm.call_model(
            VERIFY_PROMPT.format(count=len(batch), title=title, items=items), max_tokens=1200)
        match = re.search(r"\{.*\}", reply or "", re.S)
        if not match:
            continue
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        for key, value in payload.items():
            if key.strip().isdigit():
                index = int(key) - 1
                if 0 <= index < len(batch):
                    cached[f"{bucket}|{batch[index]['form']}"] = str(value).strip().lower()
        VERIFIED.write_text(json.dumps(cached, ensure_ascii=False, indent=0), encoding="utf-8")
    return [r for r in rows if cached.get(f"{bucket}|{r['form']}", "yes") == "yes"]


def corpus() -> tuple[str, list[tuple[int, int, str]]]:
    data = load(READINGS)
    per_lesson = []
    for volume in data["volumes"]:
        for lesson in volume["lessons"]:
            body = "".join(unit["text"] for unit in lesson["units"])
            per_lesson.append((volume["volume"], lesson["lesson"], body))
    return "".join(body for _, _, body in per_lesson), per_lesson


def where(term: str, per_lesson: list[tuple[int, int, str]]) -> str:
    """哪一冊哪一課出現過——附錄的每一列都要能回到書裡。"""
    hits = [f"{volume}-{lesson:02d}" for volume, lesson, body in per_lesson if term in body]
    if not hits:
        return ""
    return "、".join(hits[:3]) + ("…" if len(hits) > 3 else "")


def compounds(interlinear: dict) -> tuple[collections.Counter, dict[str, str], dict[str, str]]:
    freq: collections.Counter = collections.Counter()
    gloss: dict[str, str] = {}
    for unit in interlinear["units"].values():
        for token in unit["tokens"]:
            word = token["word"]
            if len(word) >= 2 and KANJI.fullmatch(word):
                freq[word] += 1
                if token["glossZh"]:
                    gloss.setdefault(word, token["glossZh"])
    return freq, gloss, {}


def classify(words: list[str], gloss: dict[str, str], cached: dict[str, str]) -> dict[str, str]:
    todo = [w for w in words if w not in cached]
    for start in range(0, len(todo), BATCH):
        batch = todo[start : start + BATCH]
        items = "\n".join(f"{i}. {w}（{gloss.get(w, '')}）" for i, w in enumerate(batch, start=1))
        reply = llm.call_model(PROMPT.format(count=len(batch), items=items), max_tokens=1500)
        match = re.search(r"\{.*\}", reply or "", re.S)
        if not match:
            print(f"    · 第 {start // BATCH + 1} 批沒有回 JSON，跳過")
            continue
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        for key, value in payload.items():
            if key.strip().isdigit():
                index = int(key) - 1
                if 0 <= index < len(batch) and value in {*BUCKETS, "none"}:
                    cached[batch[index]] = value
        CLASSIFIED.write_text(json.dumps(cached, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"    · 已分類 {len(cached):,}／{len(words):,}")
    return cached


PROPER_PROMPT = """下面 {count} 個日文詞取自宗教學讀本的正文。請判斷每個是不是**專名**
——地名、人名、氏族名、寺社名、年號、政權名都算 yes；一般的制度、身分、時代區分等
普通名詞回 no。

例：江戸・鎌倉・徳川・源氏・明治 回 yes；大名・百姓・近世・敵討 回 no。

只輸出 JSON 物件，鍵是題號字串，值是 yes 或 no：{{"1": "yes", "2": "no"}}

{items}"""


def split_proper(rows: list[dict], cached: dict[str, str]) -> tuple[list[dict], list[dict]]:
    """把地名、人名、氏族名從史學用語裡分出來。

    語料自己的專名（江戶、德川、源氏、鎌倉）本來就該進專名表；課本那份專名只有
    三十八條國名與都市名，讀本正文裡的專名一條都沒有。混在史學用語裡，兩張表就
    都不對：術語表混進名字，專名表少了整本書的名字。
    """
    todo = [r for r in rows if f"proper|{r['form']}" not in cached]
    for start in range(0, len(todo), BATCH):
        batch = todo[start : start + BATCH]
        items = "\n".join(f"{i}. {r['form']}（{r['zh']}）" for i, r in enumerate(batch, start=1))
        reply = llm.call_model(
            PROPER_PROMPT.format(count=len(batch), items=items), max_tokens=1200)
        match = re.search(r"\{.*\}", reply or "", re.S)
        if not match:
            # 靜默跳過會讓整批留在原表裡，看起來像「這批沒有專名」。再問一次，
            # 還是不行就講出來——沒判過與判成不是，是兩件事。
            reply = llm.call_model(
                PROPER_PROMPT.format(count=len(batch), items=items), max_tokens=1200)
            match = re.search(r"\{.*\}", reply or "", re.S)
        if not match:
            print(f"    ⚠ 專名分流第 {start // BATCH + 1} 批問不到答案，{len(batch)} 條留在原表")
            continue
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        for key, value in payload.items():
            if key.strip().isdigit():
                index = int(key) - 1
                if 0 <= index < len(batch):
                    cached[f"proper|{batch[index]['form']}"] = str(value).strip().lower()
        VERIFIED.write_text(json.dumps(cached, ensure_ascii=False, indent=0), encoding="utf-8")
    names = [r for r in rows if cached.get(f"proper|{r['form']}") == "yes"]
    rest = [r for r in rows if cached.get(f"proper|{r['form']}") != "yes"]
    return names, rest


def build(write: bool) -> dict:
    whole, per_lesson = corpus()
    interlinear = load(INTERLINEAR)
    freq, gloss, _ = compounds(interlinear)
    t2jp, jp2t = OpenCC("t2jp"), OpenCC("jp2t")
    tables = []

    # 1. 舊字 → 新字
    kanji_freq = collections.Counter(ch for ch in whole if KANJI.fullmatch(ch))
    rows = []
    for ch, count in kanji_freq.most_common():
        modern = t2jp.convert(ch)
        if modern != ch:
            rows.append({"form": ch, "modern": modern, "count": count,
                         "lessons": where(ch, per_lesson)})
    tables.append({"id": "kyujitai", "title": "舊字體 → 新字體",
                   "note": "取自本讀本正文實際出現的字形，對應由 OpenCC 的 t2jp 推導。"
                           "第三、四冊的文本用舊字體印，這一張表是讀它們時的對照。",
                   "entries": rows})

    # 2. 舊假名遣
    rows = []
    for old, new, example in KANA_RULES:
        probe = old.replace("〜", "")
        rows.append({"form": old, "modern": new, "example": example,
                     "count": whole.count(probe)})
    tables.append({"id": "kyukana", "title": "舊假名遣 → 現代假名遣",
                   "note": "規則表；右欄的次數是該假名在本讀本正文出現的次數，"
                           "「〜」開頭的幾條是語中語尾的規則，次數含一般用法。",
                   "entries": rows})

    # 3. 學術文體機能語
    rows = [{"form": f, "count": whole.count(f), "lessons": where(f, per_lesson)}
            for f in FUNCTION_WORDS if whole.count(f)]
    rows.sort(key=lambda r: -r["count"])
    tables.append({"id": "function_words", "title": "學術文體機能語",
                   "note": "只收本讀本正文裡出現過的；讀學術日文卡住的多半不是名詞，是這些。",
                   "entries": rows})

    # 4–7. 四張語意表
    # 種子詞表挑不出這幾張表。第一版用宗教關鍵字過濾，1,176 個複合詞裡只留下 122
    # 個候選——「供養」「開祖」「幕藩」這些沒有共同字根的術語全數漏掉，而附錄漏掉
    # 的東西不會有任何跡象。改成把出現三次以上的複合詞全部交給模型判，讓它說不是，
    # 比我先猜哪些可能是可靠。
    candidates = sorted(w for w, c in freq.items() if c >= MIN_FREQ)
    print(f"  待分類 {len(candidates):,} 詞（漢字複合詞 {len(freq):,} 個，出現 {MIN_FREQ} 次以上的）")
    cached = load(CLASSIFIED) if CLASSIFIED.exists() else {}
    verified = load(VERIFIED) if VERIFIED.exists() else {}
    if write:
        cached = classify(candidates, gloss, cached)
    names: list[dict] = []
    for bucket, title in BUCKETS.items():
        rows = []
        for word in candidates:
            if cached.get(word) != bucket:
                continue
            zh = gloss.get(word, "")
            if not zh:
                continue
            rows.append({"form": word, "zh": to_traditional(zh), "count": freq[word],
                         "lessons": where(word, per_lesson)})
        rows.sort(key=lambda r: -r["count"])
        if write:
            before = len(rows)
            rows = verify(bucket, title, rows, verified)
            print(f"    {title}：複核後 {len(rows)}／{before}")
            if bucket in ("history", "religious_studies"):
                found, rows = split_proper(rows, verified)
                names.extend(found)
                print(f"    {title}：分出 {len(found)} 條專名")
        note = ("詞取自本讀本正文，中文沿用逐詞對譯層已定的譯法——"
                "同一個詞在課文裡與附錄裡不會有兩種說法。")
        if bucket == "christian" and write:
            attached, missing = attach_variants(rows)
            note += ("　兩傳統譯名取自本站《翻譯定名》的神學名詞表；"
                     "該表沒有收的詞就留白，不自行填。")
            print(f"    基督教用語：詞庫接上 {attached}／{len(rows)} 條")
            if missing:
                print("      詞庫沒收：" + "、".join(missing))
        tables.append({"id": bucket, "title": title, "note": note, "entries": rows})

    if names:
        names.sort(key=lambda r: -r["count"])
        tables.append({"id": "proper_corpus", "title": "專名（正文所見）",
                       "note": "讀本正文自己的專名——地名、人名、氏族、寺社、年號。"
                               "課本那份專名表只有國名與都市，這一張補的是書裡真正出現的。",
                       "entries": names})
        print(f"  專名（正文所見）：{len(names)} 條，自史學與宗教學兩表分出")

    # 8. 數字・助数詞
    counters = collections.Counter(m.group(1) for m in COUNTER_RE.finditer(whole))
    rows = [{"form": form, "count": count,
             "example": (re.search(r"[一二三四五六七八九十百千万0-9０-９]+" + form, whole) or [None])
             and (re.search(r"[一二三四五六七八九十百千万0-9０-９]+" + form, whole).group(0)),
             "lessons": where(form, per_lesson)}
            for form, count in counters.most_common()]
    tables.append({"id": "counters", "title": "數字與助数詞",
                   "note": "只收「數字＋量詞」的實例；例欄印的是正文裡的原句片段。",
                   "entries": rows})

    # 9. 親屬稱謂
    rows = []
    for term in KINSHIP:
        count = whole.count(term)
        if count:
            rows.append({"form": term, "zh": to_traditional(gloss.get(term, "")),
                         "count": count, "lessons": where(term, per_lesson)})
    rows.sort(key=lambda r: -r["count"])
    tables.append({"id": "kinship", "title": "親屬稱謂",
                   "note": "取自本讀本正文；沒有出現的稱謂不列，這張表不是通用親屬表。",
                   "entries": rows})

    # 10. 年號與曆法
    rows = []
    for era in ERAS:
        count = len(re.findall(era + r"[一二三四五六七八九十元\d]", whole))
        if count:
            rows.append({"form": era, "kind": "年號", "count": count,
                         "lessons": where(era, per_lesson)})
    for term in CALENDAR:
        count = whole.count(term)
        if count:
            rows.append({"form": term, "kind": "曆法", "zh": to_traditional(gloss.get(term, "")),
                         "count": count, "lessons": where(term, per_lesson)})
    tables.append({"id": "era_calendar", "title": "年號與曆法",
                   "note": "年號要後面接得上數字才算——「文化」「文明」在這本書裡是普通名詞，"
                           "光比對字串會把它們收成年號。干支在本讀本正文裡一次都沒出現，故不立表。",
                   "entries": rows})

    payload = {
        "schemaVersion": "1.0.0",
        "note": "日文讀本的附錄表。每一列都取自本讀本正文，並記出現次數與課次；"
                "中文沿用逐詞對譯層已定的譯法。",
        "corpusChars": len(whole),
        "tables": tables,
    }
    for table in tables:
        print(f"  {table['title']}：{len(table['entries'])} 條")
    if write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"已寫入 {OUTPUT.relative_to(ROOT)}")
    else:
        print("（未寫入；加 --write）")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    build(args.write)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
