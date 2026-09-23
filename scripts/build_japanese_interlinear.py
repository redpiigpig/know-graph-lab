#!/usr/bin/env python3
"""Build the word-by-word Traditional-Chinese layer for the Japanese reader.

**Second design (2026-09-23).** The first version segmented with janome and
glossed *per lemma*, one context-free answer shared by every occurrence. The
page-by-page proofread of the printed books showed why that cannot work here:

- janome knows modern orthography only. On 歴史的仮名遣い it cut なんぢ into
  なん＋ぢ (glossed 難處), たまふ into たま＋ふ (glossed 球), 言ふ into 言＋ふ,
  and the large-つ 促音 (あつた) into あつ＋た (glossed 燙). More than a hundred
  distinct splits of this kind, on almost every 文語 page.
- A lemma glossed without its sentence gets the wrong sense and keeps it on
  every page: 子→私生子 (also in 神の子), 行→行政區域 (in 行ふ), ある→存在
  (in である, 100+ times), が→（主格） even when it means "but".

So this version asks the model for **segmentation and gloss together, one
sentence at a time, in context**, the way the Hebrew, Greek and Latin layers
already work — and it enforces the one thing a segmenter must never get wrong:
**the surfaces joined back together are the original text, character for
character.** A unit that fails that check is retried with the diff, and left
unglossed (never half-glossed) if it still fails.

Consistency, which the per-lemma design bought, is kept two ways: the lesson
vocabulary is handed to the model as the preferred renderings, and particles /
auxiliaries are labelled from the closed-class table below (the builder's
auxiliary appendix prints that same table).

    python -X utf8 scripts/build_japanese_interlinear.py --limit 8     # 試跑
    python -X utf8 scripts/build_japanese_interlinear.py               # 全書
    python -X utf8 scripts/build_japanese_interlinear.py --assemble-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm
from translate_ebook_to_zh import _to_traditional as to_traditional

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
READINGS = CACHE / "readings.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
UNIT_CACHE = CACHE / "interlinear-units.json"
OUTPUT = CACHE / "interlinear.json"

KANA = re.compile(r"[ぁ-ゟァ-ヿー]")
LATIN = re.compile(r"[A-Za-z]")
SPACE = re.compile(r"\s+")
BATCH = 4
GLOSS_MAX = 12
ROLES = {"詞", "助", "名", "符"}

# 助詞與助動詞：現代語與文語一起收。文語那一批是合約附錄二點名要教的
# （き・けり・つ・ぬ・たり・り・べし・ず・む・らむ・けむ・なり），讀本正文裡
# 到處都是。這張表是給模型的**標記字典**（同一個功能全書同一種寫法），也是
# builder 附錄印的那張表；模型在句中判定功能，表只管寫法。
CLOSED_CLASS = {
    "は": "（主題）", "が": "（主格）", "を": "（受格）", "に": "（方向·對象）",
    "へ": "（往）", "と": "（和·引語）", "で": "（在·以）", "から": "（從）",
    "まで": "（到）", "より": "（比·從）", "の": "（的）", "も": "（也）",
    "や": "（或·啊）", "か": "（嗎）", "ね": "（呢）", "よ": "（喔）",
    "な": "（呀·別）", "ぞ": "（強調）", "ば": "（若）", "ても": "（即使）",
    "けれど": "（可是）", "ので": "（因為）", "のに": "（卻）", "し": "（又）",
    "て": "（接續）", "たり": "（又…又／完成）", "ながら": "（一邊）",
    "ばかり": "（只·剛）", "だけ": "（只）", "など": "（等）", "こそ": "（正是）",
    "さえ": "（連）", "しか": "（只有）", "ずつ": "（各）", "とも": "（縱使）",
    "ど": "（雖）", "ども": "（雖然）", "つつ": "（一邊·持續）", "ゆゑ": "（因為）",
    "だ": "（是）", "です": "（是·敬）", "である": "（是）", "ます": "（敬體）",
    "た": "（過去）", "ない": "（不）", "ぬ": "（不·完成）", "ず": "（不）",
    "う": "（意志·推量）", "よう": "（推量·樣）", "らしい": "（似乎）",
    "そうだ": "（聽說·看來）", "べし": "（應當）", "べき": "（應當）",
    "まい": "（不會·不打算）", "たい": "（想）", "れる": "（被·可能·敬）",
    "られる": "（被·可能·敬）", "せる": "（使）", "させる": "（使）",
    "き": "（過去·親見）", "けり": "（過去·傳聞·詠嘆）", "つ": "（完成）",
    "り": "（完成·存續）", "む": "（推量·意志）", "らむ": "（現在推量）",
    "けむ": "（過去推量）", "なり": "（是·斷定）", "たし": "（想）",
    "ごとし": "（如同）", "しむ": "（使）", "る": "（被·自發）", "らる": "（被·可能）",
    "けむや": "（豈曾）", "まし": "（反實推量）", "めり": "（看來）",
    "なむ": "（強調·願）", "こそあれ": "（雖則）", "ものの": "（雖然）",
    "。": "", "、": "", "「": "", "」": "", "『": "", "』": "", "・": "",
    "（": "", "）": "", "！": "", "？": "", "…": "", "─": "", "ー": "",
    # 學術文體的機能語（合約附錄四）。
    "として": "（作為）", "における": "（在…的）", "において": "（在…）",
    "について": "（關於）", "によって": "（由於·藉由）", "による": "（依據）",
    "にとって": "（對…而言）", "とともに": "（與…一同）", "にほかならない": "（無非是）",
    "に対して": "（對於）", "に関して": "（就…而言）", "ということ": "（這件事）",
    # 文語的助詞助動詞與慣用連語，第二冊每一頁都在用。
    "のみ": "（只）", "にて": "（在·以）", "といふ": "（叫做·所謂）",
    "とか": "（之類）", "かも": "（也許）", "を以て": "（以）",
    "に対する": "（對…的）", "により": "（依據）", "如き": "（如同的）",
    "如く": "（如同）", "ごとき": "（如同的）", "ん": "（推量·意志）",
    "じ": "（不會·否定推量）", "ましか": "（反實推量）",
    "らし": "（推定）", "つる": "（完成）", "ぬる": "（完成）", "たる": "（的·完成）",
    "なる": "（的·斷定）", "せ": "（使·過去）",
    # 青空文庫與舊活字的疊字記號：它們是符號不是詞，別讓模型去猜。
    "ゝ": "", "ゞ": "", "〳": "", "〵": "", "〴": "", "／": "", "＼": "",
    "″": "", "　": "", " ": "",
}

# 給模型看的功能標記表：只列會在句中反覆出現、而且過去印錯過的那些。
# 表外的功能由模型自擬括號標記。
LABEL_GUIDE = """は（主題）　が（主格）／接續用法的が（但是）　を（受格）　に（方向·對象）／に 作副詞語尾（地）
へ（往）　と（和·引語）／條件的と（一…就）　で（在·以）／て形濁化的で（接續）／だ的連用形で（是）
の（的）／形式名詞の（的·事）　も（也）　か（嗎）／疑問詞＋か（某）　ね（呢）　よ（喔）　な（呀·別）　ぞ（強調）
ば（若）　ても（即使）　けれど（可是）　ので（因為）　のに（卻）　て（接續）　ながら（一邊）　だけ（只）　など（等）
だ／です／である／なり（斷定）→（是）　ます（敬體）　ません 的 ん（否定）　た（過去）　ない／ぬ／ず（不）
う／よう／む（意志·推量）　らしい（似乎）　べし（應當）　たい（想）　れる／られる／る／らる（被·可能·敬）
せる／させる／しむ（使）　き（過去·親見）　けり（過去·傳聞·詠嘆）　つ／ぬ／り／たり（完成）　けむ（過去推量）　らむ（現在推量）
ごとし（如同）　補助動詞：ている／ておる／ゐる（正在·狀態）　てしまう（…完了）　ておく（先…）　てみる（試著）　てあげる／てくれる／てもらう（授受）
給ふ／たまふ（敬語）　奉る／申す（謙讓）　ございます（敬體）　文語形容詞語尾 かり／かる／けれ 與語幹合為一詞"""

PROMPT = """你是日文宗教學讀本的逐詞對譯編輯。下面有 {count} 段日文，每段先斷詞，再逐詞給繁體中文詞義。

## 斷詞規矩
1. 照「詞」切，不照詞素切：名詞、副詞、連體詞、複合詞、片假名外來語（含「・」連接的整串）各為一個詞，不可拆。
2. 動詞、形容詞：語幹連同活用語尾為一詞（「起こっ」「読ま」「美しく」「言ひ」），後面的助動詞、助詞、補助動詞各自一詞（「た」「ます」「ない」「ている」）。「ません」切成「ませ」＋「ん」。
3. 舊假名遣（歷史的假名遣）：ゐ・ゑ・ぢ・づ・ハ行轉呼（言ふ、たまふ、思へ、なんぢ、とこしへ、さうして、やう）都是詞的一部分，**絕對不可把一個詞切成兩半**。大書的促音つ（あつた、いつて、だつた）算在動詞語幹裡：「あつ」＋「た」。
4. 專名（人名、地名、書名、神名、經名、教派名）整個一詞；日本人名「姓＋名」合為一詞。
5. 標點、括號、空白（全形空白「　」也算）、踊り字（ゝ ゞ 〳 〵 ／＼）、外字記號（※ 及其後的［＃…］）都各自一個 token，role 填「符」。
6. **所有 surface 依序連接起來必須與原文一字不差**（含標點與空白）。不可增刪改任何字元。

## 詞義規矩
- gloss 是「這個詞在這一句裡」的意思，繁體中文，最多 {maxlen} 個字，不可有假名或英文，不加詞性、不加註解。
- 助詞、助動詞、補助動詞、接尾辭、助數詞：role 填「助」，gloss 用括號功能標記，寫法照下面的標記表；表裡沒有的自擬括號標記。
- 專名：role 填「名」，gloss 給通行中譯（聖經人名地名照和合本；日本人名照漢字；西洋人名音譯）。
- 其餘實詞：role 填「詞」。詞表給了譯法而且語意相同時照用；語意不同時照句意（例如「時」在句中是「時候」就不寫「點鐘」，「本」作助數詞就是「（支·本）」）。
- 同形異義要看句子：「子」在「神の子」是「兒子」；「行ふ」是「進行、舉行」；「である」的「ある」是斷定不是存在。
- 標點與空白：gloss 空字串。
- lemma 填辭書形（現代假名遣）；助詞助動詞填自身；標點填自身。
- 判不出意思就把 gloss 留空字串，不要編。

## 功能標記表
{labels}

## 輸出
只輸出一個 JSON 物件。鍵是題號字串，值是 token 陣列，每個 token 是 [surface, lemma, role, gloss]：
{{"1": [["イエス","イエス","名","耶穌"],["群衆","群衆","詞","群眾"],["を","を","助","（受格）"],["見","見る","詞","看見"],["て","て","助","（接續）"],["、","、","符",""]]}}

{items}"""

_lock = threading.Lock()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def signature(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# vocabulary hints
# --------------------------------------------------------------------------

def vocabulary_forms() -> list[tuple[str, str]]:
    """(form, gloss) pairs to hand the model when the form occurs in a sentence.

    Kana-only forms shorter than three characters are not used: 「は」is in the
    table as 歯 and 「や」as 屋, and matching those by kana is how the first
    print run glossed every topic particle as 牙齒.
    """
    out: dict[str, str] = {}
    for entry in load(VOCAB)["entries"]:
        zh = (entry.get("glossZh") or "").strip()
        if not zh:
            continue
        for form in (entry.get("kanji"), entry.get("dictionaryForm")):
            form = (form or "").strip()
            if not form or form in out:
                continue
            if len(form) < 3 and not re.search(r"[一-鿿]", form):
                continue  # kana-only and short: は＝齒、や＝屋 must not reach the model
            out[form] = zh
        kana = (entry.get("kana") or "").strip()
        if kana and not entry.get("kanji") and len(kana) >= 3 and kana not in out:
            out[kana] = zh
    # longest first so 宗教学 is offered before 宗教
    return sorted(out.items(), key=lambda kv: -len(kv[0]))


def hints_for(text: str, forms: list[tuple[str, str]], cap: int = 30) -> str:
    seen: list[str] = []
    for form, zh in forms:
        if form in text:
            seen.append(f"{form}＝{zh}")
            if len(seen) >= cap:
                break
    return "、".join(seen)


# --------------------------------------------------------------------------
# validation and repair
# --------------------------------------------------------------------------

def clean_gloss(role: str, gloss: str) -> str:
    # 「云」（說）與「余」（我）要護住，opencc s2tw 會把它們轉成「雲」「餘」。
    gloss = (gloss or "").strip().strip("。，,、 ").replace("云", "").replace("余", "")
    gloss = to_traditional(gloss).replace("", "云").replace("", "余")
    if role == "符":
        return ""
    if not gloss or len(gloss) > GLOSS_MAX or KANA.search(gloss) or LATIN.search(gloss):
        return ""
    if role == "助" and not gloss.startswith("（"):
        gloss = f"（{gloss.strip('()（）')}）"
    return gloss


def align(text: str, tokens: list[list]) -> list[dict] | str:
    """Walk the text with the model's surfaces; return tokens or an error string.

    Whitespace the model dropped is re-inserted as its own token, because the
    printed page needs it and models routinely eat it. Anything else that does
    not line up is an error the model has to fix.
    """
    out: list[dict] = []
    pos = 0
    for item in tokens:
        if not isinstance(item, list) or len(item) < 4:
            return f"token 格式錯：{item!r}"
        surface, lemma, role, gloss = (str(x) for x in item[:4])
        if role not in ROLES:
            role = "詞"
        if not surface:
            continue
        # swallow whitespace the model skipped
        while pos < len(text) and text[pos].isspace() and not surface.startswith(text[pos]):
            out.append({"word": text[pos], "trailing": "", "glossZh": "", "role": "符", "lemma": text[pos]})
            pos += 1
        if not text.startswith(surface, pos):
            got = text[pos:pos + max(len(surface), 6)]
            return f"第 {len(out) + 1} 個 token「{surface}」對不上原文此處的「{got}」"
        pos += len(surface)
        out.append({"word": surface, "trailing": "", "glossZh": clean_gloss(role, gloss), "role": role, "lemma": lemma})
    while pos < len(text) and text[pos].isspace():
        out.append({"word": text[pos], "trailing": "", "glossZh": "", "role": "符", "lemma": text[pos]})
        pos += 1
    if pos != len(text):
        return f"原文尾端「{text[pos:pos + 12]}」沒有被切到"
    return out


def parse_reply(reply: str) -> dict:
    match = re.search(r"\{.*\}", reply or "", re.S)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


# --------------------------------------------------------------------------
# asking
# --------------------------------------------------------------------------

def ask(batch: list[dict], forms: list[tuple[str, str]], feedback: dict[int, str] | None = None) -> dict[str, list[dict]]:
    """One call for a batch of units -> {signature: tokens} for the ones that verified."""
    lines = []
    for index, unit in enumerate(batch, start=1):
        hint = hints_for(unit["text"], forms)
        note = f"　語體：{unit['orthography']}"
        if hint:
            note += f"　詞表：{hint}"
        if feedback and index in feedback:
            note += f"\n　🚨 上一次的輸出有誤：{feedback[index]}。請重新斷詞，確保 surface 連起來等於原文。"
        lines.append(f"{index}.（{unit['ref']}{note}）\n{unit['text']}")
    prompt = PROMPT.format(count=len(batch), maxlen=GLOSS_MAX, labels=LABEL_GUIDE, items="\n\n".join(lines))
    reply = llm.call_model(prompt, max_tokens=8000)
    engine = llm.current_model()
    payload = parse_reply(reply)
    out: dict[str, list[dict]] = {}
    errors: dict[int, str] = {}
    for key, value in payload.items():
        if not str(key).strip().isdigit():
            continue
        index = int(key)
        if not 1 <= index <= len(batch):
            continue
        unit = batch[index - 1]
        result = align(unit["text"], value if isinstance(value, list) else [])
        if isinstance(result, str):
            errors[index] = result
        else:
            out[unit["sig"]] = {"engine": engine, "tokens": result}
    for index in range(1, len(batch) + 1):
        if index not in errors and batch[index - 1]["sig"] not in out:
            errors[index] = "沒有回答這一段"
    out["__errors__"] = errors  # type: ignore[assignment]
    return out


def gloss_batch(batch: list[dict], forms: list[tuple[str, str]], cache: dict, tries: int = 3) -> tuple[int, int]:
    """Ask, retry the failures with their diagnostics, write the cache. Returns (ok, failed)."""
    pending = list(batch)
    feedback: dict[int, str] = {}
    ok = 0
    for attempt in range(tries):
        if not pending:
            break
        try:
            got = ask(pending, forms, feedback)
        except Exception as error:  # noqa: BLE001 - every engine down; keep the run alive
            print(f"    · 引擎全部沒回應：{type(error).__name__} {str(error)[:80]}", flush=True)
            got = {"__errors__": {i: "引擎沒回應" for i in range(1, len(pending) + 1)}}
        errors = got.pop("__errors__", {})
        with _lock:
            for sig, entry in got.items():
                cache[sig] = entry
                ok += 1
            UNIT_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
        still = [pending[i - 1] for i in sorted(errors)]
        feedback = {n + 1: errors[i] for n, i in enumerate(sorted(errors))}
        if still and attempt + 1 < tries:
            print(f"    · {len(still)} 段沒過對齊檢查，重問（{list(feedback.values())[:2]}）", flush=True)
        pending = still
    for unit in pending:
        print(f"    ✗ 放棄 {unit['id']}：{unit['text'][:30]}…", flush=True)
    return ok, len(pending)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def unglossed_pieces(text: str, width: int = 10) -> list[str]:
    """Split a unit that got no gloss row into wrappable pieces: at punctuation, then every `width` chars."""
    pieces: list[str] = []
    for chunk in re.split(r"(?<=[、。，．！？」』）])", text):
        chunk = chunk.strip()
        while len(chunk) > width:
            pieces.append(chunk[:width])
            chunk = chunk[width:]
        if chunk:
            pieces.append(chunk)
    return pieces or [text]


def every_unit(readings: dict) -> list[dict]:
    units: list[dict] = []
    for volume in readings["volumes"]:
        for lesson in volume["lessons"]:
            groups = [("reading", lesson["units"]), ("memory", lesson["memoryUnits"])]
            for group, rows in groups:
                for index, unit in enumerate(rows, start=1):
                    unit_id = unit.get("id") or f"v{volume['volume']}-l{lesson['lesson']:02d}-m{index:03d}"
                    units.append({
                        "id": unit_id,
                        "group": group,
                        "text": unit["text"],
                        "sig": signature(unit["text"]),
                        "ref": f"{lesson['title']}　{unit.get('label') or ''}".strip(),
                        "orthography": lesson.get("orthography") or "現代語",
                    })
    return units


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="最多處理幾段（試跑用）")
    parser.add_argument("--batch", type=int, default=BATCH)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--assemble-only", action="store_true", help="只用快取重組 interlinear.json，不問模型")
    parser.add_argument("--redo", default="", help="重做 id 含此字串的段（例 v2-l42）")
    args = parser.parse_args()

    readings = load(READINGS)
    forms = vocabulary_forms()
    units = every_unit(readings)
    cache: dict = load(UNIT_CACHE) if UNIT_CACHE.exists() else {}
    if args.redo:
        for unit in units:
            if args.redo in unit["id"]:
                cache.pop(unit["sig"], None)

    todo = [] if args.assemble_only else [u for u in units if u["sig"] not in cache]
    if args.limit:
        todo = todo[: args.limit]
    print(f"單元 {len(units):,}　已快取 {len(units) - len([u for u in units if u['sig'] not in cache]):,}　本輪 {len(todo):,}", flush=True)

    batches = [todo[i : i + args.batch] for i in range(0, len(todo), args.batch)]
    done = failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for number, (ok, bad) in enumerate(pool.map(lambda b: gloss_batch(b, forms, cache), batches), start=1):
            done += ok
            failed += bad
            print(f"  批 {number}/{len(batches)}　過 {ok}/{ok + bad}　累計 {done:,}（放棄 {failed}）　引擎 {llm.current_model()}", flush=True)

    # 組裝。快取裡沒有的段整段留白（印原文、不印詞義），不用舊的 janome 結果頂替。
    out_units: dict[str, dict] = {}
    missing_units = 0
    total = blank = 0
    for unit in units:
        entry = cache.get(unit["sig"])
        if entry:
            tokens = [{"word": t["word"], "trailing": t.get("trailing", ""), "glossZh": t["glossZh"]} for t in entry["tokens"]]
            for t in entry["tokens"]:
                if t.get("role") != "符":
                    total += 1
                    blank += not t["glossZh"]
        else:
            missing_units += 1
            # 整段當一個 token 會超出版心（排版按 token 寬度切行，一個比行還寬的
            # token 就直接凸出去——2026-09-24 第二冊 49 處）。沒有對譯的段照標點與
            # 每十字切成無詞義的小塊，至少能換行。
            tokens = [{"word": piece, "trailing": "", "glossZh": ""} for piece in unglossed_pieces(unit["text"])]
        out_units[unit["id"]] = {"ref": unit["ref"], "group": unit["group"], "tokens": tokens}

    OUTPUT.write_text(
        json.dumps(
            {
                "schemaVersion": "2.0.0",
                "language": "Japanese",
                "languageCode": "ja",
                "engine": "逐句上下文斷詞＋對譯（Gemini／NVIDIA／Haiku），對齊閘：surface 連接＝原文",
                "count": len(out_units),
                "units": out_units,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"寫出 {OUTPUT.relative_to(ROOT)}：{len(out_units):,} 段（未對譯 {missing_units}）、"
          f"{total:,} 詞、留白 {blank:,}（{blank / max(total, 1):.1%}）", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
