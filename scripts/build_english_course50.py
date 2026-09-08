"""替國小英語課本產生 50 課 × 20 字的課程內容。

原本的課本與 /english 網站是 20 課 × 50 字；單字卡那份是 50 課 × 20 字。
使用者定案課本改跟單字卡對齊，所以整套課文／文法／對話／例句要重新生成成
50 課份，另外每課加 54 題練習（30 選擇 + 10 填空 + 8 造句 + 6 重組）。

分課以 data/originalReaders/vocabulary/english-1000.json 為準（那份已人工校過，
且 1000 張卡全部有配圖）；文法進程沿用舊 20 課的 theme -> grammar 對照當骨架。

每課兩次呼叫（課程主體、練習題），逐課寫檔可續跑；有品質閘，沒過的課不落地。

用法：
    python scripts/build_english_course50.py            # 跑沒做過的課
    python scripts/build_english_course50.py --only 3   # 只跑第 3 課
    python scripts/build_english_course50.py --redo     # 重做（含已完成的）
    python scripts/build_english_course50.py --check    # 只驗現有產出
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import random
import re
import sys
import time

import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import original_reader_llm as llm  # noqa: E402
import translate_ebook_to_zh as engines  # noqa: E402

# 2026-09-07 實測：共用模組列的三個 NVIDIA 模型只剩 nemotron 活著（llama-3.1-70b、
# llama-3.3-70b、qwen3-next 一律 HTTP 410，deepseek-v4-flash-0731 掛住不回）。
# nemotron 本身很快，但一課的題目要寫兩千多個 token，40 秒的逾時會誤判成「模型塞住」
# 而把它冷凍半小時，於是整批掉到 Haiku 去燒 Max 額度。這裡只改本行程的設定，
# 不動共用模組——過夜艦隊正在用它。
llm.NVIDIA_MODELS = ("nvidia/nemotron-3-super-120b-a12b",)
llm.NVIDIA_TIMEOUT = 240

REPO = ROOT.parent
VOCAB = REPO / "data" / "originalReaders" / "vocabulary" / "english-1000.json"
OLD_LESSONS = REPO / "public" / "content" / "english" / "lessons.json"
OUT_DIR = REPO / "public" / "content" / "english" / "course50"

N_MCQ, N_FILL, N_TRANSLATE, N_UNSCRAMBLE = 30, 10, 8, 6

# 常見簡體字，用來擋掉引擎偶爾吐簡體。不用 OpenCC 反向比對——
# 那個會把「祢」之類的正體字誤判成簡體（見 feedback_reader_silent_failures）。
SIMPLIFIED = set("们个这来说时对开关国车东车马鸟鱼员问间学习书写练习汉语课让点电话请问题种钟头饭觉觉给还没现认识爱乐种类样长间门问闻业务农产会记录师从众丽万与专业东乡习乡")


def load_lessons() -> list[dict]:
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))["entries"]
    old = {l["title_en"]: l for l in json.loads(OLD_LESSONS.read_text(encoding="utf-8"))}
    lessons: dict[int, dict] = {}
    for entry in vocab:
        no = entry["lesson"]
        lessons.setdefault(no, {"no": no, "theme": entry["theme"],
                                "theme_zh": entry["themeZh"], "words": []})
        lessons[no]["words"].append({"en": entry["en"], "zh": entry["zh"]})
    ordered = [lessons[n] for n in sorted(lessons)]
    # 同一主題橫跨數課，標出這是該主題的第幾課，好讓文法有前後進程
    by_theme: dict[str, list[dict]] = {}
    for lesson in ordered:
        by_theme.setdefault(lesson["theme"], []).append(lesson)
    for theme, group in by_theme.items():
        source = old.get(theme, {})
        for i, lesson in enumerate(group, 1):
            lesson["part"] = i
            lesson["part_of"] = len(group)
            lesson["theme_grammar"] = source.get("grammar", "")
    return ordered


_BODY_HEAD = """你是台灣國小英語教材的資深編寫者。請替一本自編課本寫第 {no} 課的內容。

【本課主題】{theme}（{theme_zh}）
【進度位置】這是「{theme_zh}」這個主題的第 {part} 課（共 {part_of} 課）
【主題文法範圍】{theme_grammar}
【本課必教的 20 個單字】
{words}

共同要求：
1. 全部中文一律「繁體中文」（台灣用字，例如「裡」不寫「里」）。
2. 讀者是台灣國小中高年級學生，句子要短、具體、生活化。**絕對不要加 KK 音標或任何音標**。
3. 只輸出 JSON，不要任何說明文字，不要包在程式碼區塊裡。
"""


def _body_head(lesson: dict) -> str:
    return _BODY_HEAD.format(
        no=lesson["no"], theme=lesson["theme"], theme_zh=lesson["theme_zh"],
        part=lesson["part"], part_of=lesson["part_of"],
        theme_grammar=lesson["theme_grammar"],
        words="\n".join(f"- {w['en']}　{w['zh']}" for w in lesson["words"]))


def prompt_intro(lesson: dict) -> str:
    return _body_head(lesson) + """
請寫課名、導言與課文。課文 reading 要 8～10 句，是一個有頭有尾的小故事或情境。
**上面列的 20 個單字，至少要用掉 16 個在課文裡**——這是本課唯一一篇課文，
沒被用到的字學生整課都不會再遇到。寧可句子多一點，也不要漏字。

JSON 格式：
{
  "title_en": "英文課名（3～5 個字）",
  "title_zh": "中文課名（6～12 字）",
  "grammar": "本課文法重點一句話",
  "intro_zh": "本課導言，60～90 字",
  "can_do": ["學完能做到的事1", "…2", "…3"],
  "reading": {"title_en": "課文英文標題", "title_zh": "課文中文標題",
    "sentences": [{"en": "英文句", "zh": "中文翻譯"}]}
}"""


def prompt_grammar(lesson: dict, intro: dict) -> str:
    return _body_head(lesson) + f"""
本課文法重點已定為：{intro.get('grammar', '')}

請寫文法解說、情境對話與例句。文法寫 2 個 grammar_points：第一個一定要附 table
（第一列是表頭），第二個一定要附 examples。若這是同主題的第 2 課以後，
文法要接續前一課往下推進，不要重複同一個點。

JSON 格式：
{{
  "grammar_points": [
    {{"title_zh": "① 文法點標題", "explain_zh": "說明",
      "table": [["表頭1","表頭2","表頭3"], ["…","…","…"]]}},
    {{"title_zh": "② 文法點標題", "explain_zh": "說明",
      "examples": [{{"en": "英文例句", "zh": "中文"}}]}}
  ],
  "dialogue": {{"title_zh": "情境對話標題",
    "lines": [{{"sp": "人名", "en": "英文", "zh": "中文"}}]}},
  "sentences": [{{"en": "例句英文", "zh": "中文"}}]
}}
sentences 要 8 句，dialogue 要 4～6 句。"""


_EX_HEAD = """你是台灣國小英語教材的資深編寫者，正在替第 {no} 課出練習題。

【本課文法】{grammar}
【本課 20 個單字】{words}

共同要求：
- 只能用本課與前面幾課學過的字，超綱字不要用。
- 全部中文一律繁體中文（台灣用字）。**不要 KK 音標**。
- 每題答案必須唯一且正確。
- 只輸出 JSON，不要說明文字，不要包在程式碼區塊裡。
"""


def _ex_head(lesson: dict, body: dict) -> str:
    return _EX_HEAD.format(no=lesson["no"], grammar=body.get("grammar", ""),
                           words="、".join(w["en"] for w in lesson["words"]))


MCQ_BATCH = 10
MCQ_STYLES = [
    "以單字中譯、英文釋義、看中文選英文為主",
    "以文法選填、詞形變化為主",
    "以句意理解、情境問答、看圖說話式的情境判斷為主",
]


def prompt_mcq(lesson: dict, body: dict, n: int, style: str, avoid: list[str]) -> str:
    # NVIDIA 那層的輸出上限是 4000 token，30 題一次出會在半路被截斷成不合法 JSON，
    # 於是整批掉到 Haiku 去燒 Max 額度。分批出才留得住免費層。
    dodge = ""
    if avoid:
        dodge = "\n\n下列題目已經出過，不要重複或只改一個字：\n" + "\n".join(
            f"- {q}" for q in avoid)
    return _ex_head(lesson, body) + f"""
請出 **剛好 {n} 題**選擇題，每題 4 個選項，{style}。
ans 必須**逐字**等於 opts 其中一個，四個選項不可重複。

JSON 格式：
{{"mcq": [{{"q": "題目", "opts": ["A", "B", "C", "D"], "ans": "正確選項原文"}}]}}{dodge}"""


def prompt_drills(lesson: dict, body: dict) -> str:
    return _ex_head(lesson, body) + f"""
請出三種題目：
1. fill：**剛好 {N_FILL} 題**填空，題幹英文句挖一個空（用 ____ 表示），
   括號內給中文提示，答案是一個英文單字。
2. translate：**剛好 {N_TRANSLATE} 題**造句翻譯，給中文句子，答案是英文句子。
3. unscramble：**剛好 {N_UNSCRAMBLE} 題**句子重組，題幹是打散的單字用 " / " 隔開
   （含最後的標點），答案是正確句子。

JSON 格式：
{{
  "fill": [{{"q": "I ____ a student.（我是學生）", "ans": "am"}}],
  "translate": [{{"q": "中文句子", "ans": "English sentence."}}],
  "unscramble": [{{"q": "am / I / Leo / .", "ans": "I am Leo."}}]
}}"""


def parse_json(raw: str) -> dict:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("回應裡沒有 JSON")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return salvage_json(text[start:])


def salvage_json(text: str) -> dict:
    """救回被輸出上限砍斷的清單。

    NVIDIA 那層寫到一半就停，尾巴是半個題目。砍回最後一個完整的物件、
    自己補上收尾括號，通常就救得回來；救不回來的交給呼叫端重試。
    """
    closes = [i for i, ch in enumerate(text) if ch == "}"]
    for cut in reversed(closes):
        for tail in ("", "]}", "}]}", "]}}"):
            try:
                return json.loads(text[:cut + 1] + tail)
            except json.JSONDecodeError:
                continue
    raise ValueError("JSON 無法解析也救不回來")


def check_simplified(obj) -> list[str]:
    found = set()

    def walk(node):
        if isinstance(node, str):
            found.update(ch for ch in node if ch in SIMPLIFIED)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(obj)
    return sorted(found)


def validate_intro(body: dict) -> list[str]:
    errs = []
    for key in ("title_en", "title_zh", "grammar", "intro_zh", "can_do", "reading"):
        if not body.get(key):
            errs.append(f"缺 {key}")
    reading = body.get("reading") or {}
    if len(reading.get("sentences") or []) < 6:
        errs.append("課文少於 6 句")
    return errs + _common_errs(body)


def _common_errs(obj) -> list[str]:
    errs = []
    if "KK" in json.dumps(obj, ensure_ascii=False):
        errs.append("出現 KK 音標")
    bad = check_simplified(obj)
    if bad:
        errs.append("簡體字：" + "".join(bad))
    return errs


def validate_grammar(body: dict) -> list[str]:
    errs = []
    for key in ("grammar_points", "dialogue", "sentences"):
        if not body.get(key):
            errs.append(f"缺 {key}")
    points = body.get("grammar_points") or []
    if len(points) < 2:
        errs.append("文法點少於 2 個")
    else:
        if not points[0].get("table"):
            errs.append("第一個文法點沒有 table")
        if not points[1].get("examples"):
            errs.append("第二個文法點沒有 examples")
    if len(body.get("sentences") or []) < 6:
        errs.append("例句少於 6 句")
    if len((body.get("dialogue") or {}).get("lines") or []) < 4:
        errs.append("對話少於 4 句")
    return errs + _common_errs(body)


def validate_exercises(ex: dict, keys: dict[str, int] | None = None) -> list[str]:
    errs = []
    wanted = keys or {"mcq": N_MCQ, "fill": N_FILL, "translate": N_TRANSLATE,
                      "unscramble": N_UNSCRAMBLE}
    for key, n in wanted.items():
        items = ex.get(key) or []
        if len(items) != n:
            errs.append(f"{key} 應 {n} 題，實得 {len(items)}")
        for i, item in enumerate(items, 1):
            if not item.get("q") or not item.get("ans"):
                errs.append(f"{key} 第 {i} 題缺 q/ans")
    for i, item in enumerate(ex.get("mcq") or [], 1):
        opts = item.get("opts") or []
        if len(opts) != 4:
            errs.append(f"mcq 第 {i} 題選項不是 4 個")
        elif item.get("ans") not in opts:
            errs.append(f"mcq 第 {i} 題答案不在選項裡")
        elif len(set(opts)) != 4:
            errs.append(f"mcq 第 {i} 題選項重複")
    for i, item in enumerate(ex.get("fill") or [], 1):
        if "____" not in (item.get("q") or ""):
            errs.append(f"fill 第 {i} 題沒有空格")
    questions = [item.get("q") for item in ex.get("mcq") or []]
    dupes = {q for q in questions if questions.count(q) > 1}
    if dupes:
        errs.append(f"選擇題重複 {len(dupes)} 題：{next(iter(dupes))}")
    bad = check_simplified(ex)
    if bad:
        errs.append("簡體字：" + "".join(bad))
    return errs


VERBOSE = False

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "nvidia/nemotron-3-super-120b-a12b"
_keys = None


def _nvidia_json(prompt: str, max_tokens: int = 8000, tries: int = 4) -> str:
    """直接向 nemotron 要 JSON。

    共用模組那條路對這份工作有兩個問題：輸出上限寫死 4000，而 nemotron 是推理模型，
    長提示會把額度花在思考上，剝掉 think 標籤後常常一個字都不剩（「回應裡沒有 JSON」）；
    而且它不開 response_format，模型有時改用散文回答。這裡把上限放寬並開 JSON 模式，
    實測解析成功率從三分之一變成全中。真的失敗才回落共用鏈（Gemini/Haiku）。
    """
    global _keys
    if _keys is None:
        _keys = list(engines.NVIDIA_KEYS)
    last = "?"
    for i in range(tries):
        key = _keys[(_nvidia_json.calls + i) % len(_keys)]
        try:
            response = requests.post(
                NVIDIA_URL,
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                json={"model": NVIDIA_MODEL,
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": max_tokens, "temperature": 0.3,
                      "response_format": {"type": "json_object"}},
                timeout=300)
        except requests.exceptions.RequestException as error:
            last = type(error).__name__
            continue
        finally:
            _nvidia_json.calls += 1
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"]
            return engines._THINK_RE.sub("", text).strip()
        last = f"HTTP {response.status_code}"
        if response.status_code == 503:   # 過載，換把 key 等一下再試
            time.sleep(5)
    raise RuntimeError(f"NVIDIA JSON 模式失敗（{last}）")


_nvidia_json.calls = 0


LAST_ENGINE = "?"
FALLBACK_TIMEOUT = 900


def _generate(prompt: str) -> tuple[str, str]:
    """先走 NVIDIA JSON 模式，失敗才回落共用鏈。

    回落那條路會掛住：2026-09-07 夜裡兩條工人各卡在同一次呼叫超過 13 小時
    （一條停在 gemini-flash-latest，一條停在共用模組的 nemotron），完全沒有逾時。
    共用模組是別的任務也在用的，不去改它，改成在這裡加看門狗——時間到就當這次
    失敗、由上層重試，那個執行緒自己去慢慢等。
    """
    global LAST_ENGINE
    try:
        text, LAST_ENGINE = _nvidia_json(prompt), "nvidia:nemotron(json)"
        return text, LAST_ENGINE
    except Exception:  # noqa: BLE001
        pass
    with futures.ThreadPoolExecutor(max_workers=1) as pool:
        task = pool.submit(llm.call_model, prompt, 16000)
        try:
            text = task.result(timeout=FALLBACK_TIMEOUT)
        except futures.TimeoutError:
            LAST_ENGINE = "回落逾時"
            raise RuntimeError(f"回落引擎超過 {FALLBACK_TIMEOUT}s 沒回應")
        finally:
            pool.shutdown(wait=False)
    LAST_ENGINE = llm.current_model()
    return text, LAST_ENGINE


def ask(prompt: str, validate, attempts: int = 4, stage: str = ""):
    last = []
    for attempt in range(1, attempts + 1):
        started = time.time()
        engine = "?"
        try:
            raw, engine = _generate(prompt)
            data = parse_json(raw)
        except Exception as exc:  # noqa: BLE001
            last = [f"解析失敗：{exc}"]
            if VERBOSE:
                print(f"    {stage} 第{attempt}次 {time.time() - started:.0f}s "
                      f"{engine} ✗ {exc}", flush=True)
            time.sleep(3)
            continue
        if VERBOSE:
            print(f"    {stage} 第{attempt}次 {time.time() - started:.0f}s "
                  f"{engine}", flush=True)
        errs = validate(data)
        if not errs:
            return data, []
        last = errs
        prompt += "\n\n上一次的輸出有這些問題，請修正後重出完整 JSON：\n- " + "\n- ".join(errs)
        time.sleep(2)
    return None, last


MIN_COVERAGE = 0.8


def build_lesson(lesson: dict, rounds: int = 2) -> tuple[dict | None, list[str]]:
    """整課生成，並用單字覆蓋率把關。

    覆蓋率原本只印出來看，不擋。L19 就這樣過關了——20 個字裡只有 7 個真的出現在
    課文與題目裡，其餘 13 個學生整課都不會遇到第二次，但每一項結構檢查都是綠的。
    這是典型的「看起來成功的失敗」，所以低於門檻要重做整課。
    """
    worst = None
    for attempt in range(1, rounds + 1):
        data, errs = _build_once(lesson)
        if data is None:
            return None, errs
        got = coverage(data)
        if got >= MIN_COVERAGE:
            return data, []
        worst = data
        if VERBOSE:
            print(f"    單字覆蓋只有 {got:.0%}，第 {attempt} 次重做整課", flush=True)
    return worst, [f"單字覆蓋僅 {coverage(worst):.0%}，已重做仍未達 {MIN_COVERAGE:.0%}"]


def _build_once(lesson: dict) -> tuple[dict | None, list[str]]:
    intro, errs = ask(prompt_intro(lesson), validate_intro, stage="課文")
    if intro is None:
        return None, ["課名與課文：" + "；".join(errs)]
    grammar, errs = ask(prompt_grammar(lesson, intro), validate_grammar, stage="文法")
    if grammar is None:
        return None, ["文法與例句：" + "；".join(errs)]
    body = {**intro, **grammar}

    questions: list[dict] = []
    for batch, style in enumerate(MCQ_STYLES):
        want = min(MCQ_BATCH, N_MCQ - len(questions))
        if want <= 0:
            break
        part, errs = ask(
            prompt_mcq(lesson, body, want, style, [q["q"] for q in questions]),
            lambda d, n=want: validate_exercises(d, {"mcq": n}),
            stage=f"選擇題{batch + 1}")
        if part is None:
            return None, [f"選擇題第 {batch + 1} 批：" + "；".join(errs)]
        questions.extend(part["mcq"])
    mcq = {"mcq": questions[:N_MCQ]}

    drills, errs = ask(prompt_drills(lesson, body),
                       lambda d: validate_exercises(
                           d, {"fill": N_FILL, "translate": N_TRANSLATE,
                               "unscramble": N_UNSCRAMBLE}),
                       stage="填空造句")
    if drills is None:
        return None, ["填空造句：" + "；".join(errs)]
    ex = {**mcq, **drills}
    rebuild_scrambles(ex, seed=lesson["no"])
    body.update({"no": lesson["no"], "theme": lesson["theme"],
                 "theme_zh": lesson["theme_zh"], "words": lesson["words"],
                 "exercises": ex, "engine": LAST_ENGINE})
    return body, []


def rebuild_scrambles(ex: dict, seed: int = 0) -> int:
    """句子重組的題幹改由答案機械重排。

    引擎自己打散時會漏字或多字（'eight / and / four / equals / plus / .' 的答案是
    'Four plus eight equals twelve.'——twelve 不見了，and 是多的），學生照題目怎麼排
    都排不出答案。答案才是權威，題幹重生成就不會對不上。
    """
    fixed = 0
    rng = random.Random(seed)
    for i, item in enumerate(ex.get("unscramble") or []):
        answer = (item.get("ans") or "").strip()
        if not answer:
            continue
        match = re.search(r"[.?!]$", answer)
        tail = match.group(0) if match else "."
        words = answer[:-len(tail)].split() if match else answer.split()
        if not words:
            continue
        pieces = words + [tail]
        shuffled = pieces[:]
        for _ in range(8):
            rng.shuffle(shuffled)
            if shuffled != pieces:
                break
        wanted = " / ".join(shuffled)
        if item.get("q") != wanted:
            item["q"] = wanted
            fixed += 1
    return fixed


def dedupe_mcq(ex: dict) -> int:
    seen, kept = set(), []
    for item in ex.get("mcq") or []:
        key = (item.get("q") or "").strip()
        if key in seen:
            continue
        seen.add(key)
        kept.append(item)
    dropped = len(ex.get("mcq") or []) - len(kept)
    ex["mcq"] = kept
    return dropped


def coverage(lesson: dict) -> float:
    """本課單字有多少真的出現在課文／例句／題目裡。"""
    blob = json.dumps({k: v for k, v in lesson.items() if k != "words"},
                      ensure_ascii=False).lower()
    hit = 0
    for word in lesson["words"]:
        for part in re.split(r"[/、]", word["en"]):
            if part.strip().lower() in blob:
                hit += 1
                break
    return hit / len(lesson["words"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, action="append", help="只跑指定課次")
    ap.add_argument("--range", help="課次範圍，例如 20-29；多開幾條工人分攤時用")
    ap.add_argument("--redo", action="store_true", help="連已完成的也重做")
    ap.add_argument("--check", action="store_true", help="只驗現有產出")
    ap.add_argument("--fix", action="store_true",
                    help="修既有檔：重建重組題題幹、去除重複選擇題並補題")
    ap.add_argument("-v", "--verbose", action="store_true", help="印出每次呼叫的耗時與引擎")
    args = ap.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lessons = load_lessons()

    if args.check:
        done = bad = 0
        for lesson in lessons:
            path = OUT_DIR / f"L{lesson['no']:02d}.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            errs = (validate_intro(data) + validate_grammar(data)
                    + validate_exercises(data.get("exercises") or {}))
            done += 1
            if errs:
                bad += 1
                print(f"L{lesson['no']:02d} ✗ " + "；".join(errs))
            else:
                print(f"L{lesson['no']:02d} ✓ 單字覆蓋 {coverage(data):.0%}　{data.get('title_zh')}")
        print(f"\n{done}/50 課已產出，{bad} 課有問題")
        return

    if args.fix:
        for lesson in lessons:
            path = OUT_DIR / f"L{lesson['no']:02d}.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            ex = data["exercises"]
            scrambles = rebuild_scrambles(ex, seed=lesson["no"])
            dropped = dedupe_mcq(ex)
            topped = 0
            while len(ex["mcq"]) < N_MCQ:
                want = N_MCQ - len(ex["mcq"])
                part, errs = ask(
                    prompt_mcq(lesson, data, want, MCQ_STYLES[-1],
                               [q["q"] for q in ex["mcq"]]),
                    lambda d, n=want: validate_exercises(d, {"mcq": n}),
                    stage="補選擇題")
                if part is None:
                    print(f"L{lesson['no']:02d} ⚠ 補題失敗：{'；'.join(errs)}", flush=True)
                    break
                before = len(ex["mcq"])
                ex["mcq"].extend(part["mcq"])
                dedupe_mcq(ex)
                topped += len(ex["mcq"]) - before
                if len(ex["mcq"]) == before:   # 補不出新題就別空轉
                    break
            if scrambles or dropped:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                encoding="utf-8")
                print(f"L{lesson['no']:02d} 重組題修 {scrambles} 題　"
                      f"重複刪 {dropped} 題　補回 {topped} 題　"
                      f"現有 {len(ex['mcq'])} 題", flush=True)
        return

    targets = [l for l in lessons if not args.only or l["no"] in args.only]
    if args.range:
        lo, _, hi = args.range.partition("-")
        lo, hi = int(lo), int(hi or lo)
        targets = [l for l in targets if lo <= l["no"] <= hi]
    for lesson in targets:
        path = OUT_DIR / f"L{lesson['no']:02d}.json"
        if path.exists() and not args.redo:
            continue
        started = time.time()
        data, errs = build_lesson(lesson)
        if data is None:
            print(f"L{lesson['no']:02d} ✗ {'；'.join(errs)}", flush=True)
            continue
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"L{lesson['no']:02d} ✓ {data['title_zh']}　"
              f"覆蓋 {coverage(data):.0%}　{time.time() - started:.0f}s　"
              f"{data['engine']}", flush=True)


if __name__ == "__main__":
    main()
