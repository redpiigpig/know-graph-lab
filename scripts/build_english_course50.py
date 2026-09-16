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
import collections
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
SYLLABUS = REPO / "data" / "english" / "course50-syllabus.json"
OUT_DIR = REPO / "public" / "content" / "english" / "course50"

# 使用者 2026-09-08 定案：每課印 10 題選擇題（原本 30）。早生成的那批仍存 30 題，
# 出書時由 build_english_textbook.pick_mcq 分層挑 10 題，不必重跑。
N_MCQ, N_FILL, N_TRANSLATE, N_UNSCRAMBLE = 10, 10, 8, 6

# 常見簡體字，用來擋掉引擎偶爾吐簡體。不用 OpenCC 反向比對——
# 那個會把「祢」之類的正體字誤判成簡體（見 feedback_reader_silent_failures）。
SIMPLIFIED = set("们个这来说时对开关国车东车马鸟鱼员问间学习书写练习汉语课让点电话请问题种钟头饭觉觉给还没现认识爱乐种类样长间门问闻业务农产会记录师从众丽万与专业东乡习乡")


def load_lessons() -> list[dict]:
    """每課 = 20 個字 + 大綱指定的那一個文法點。

    🚨 文法一定要按「課」綁定，不可以按「主題」。2026-09-08 那一版是拿舊 20 課版
    lessons.json 的 theme -> grammar 對照當骨架，一個主題只有一條文法，同主題的
    2～3 課就全部共用它：L01/02/03 都在教 be 動詞、L06/07/08 都是 What color/shape、
    L16/17/18 連字面都幾乎一樣，50 課實際只有 17 個文法點。提示詞裡那句「同主題第
    2 課以後要往下推進」模型根本不理。改成讀 data/english/course50-syllabus.json，
    一課一個點、寫死在提示裡。
    """
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))["entries"]
    syllabus = {l["no"]: l for l in
                json.loads(SYLLABUS.read_text(encoding="utf-8"))["lessons"]}
    lessons: dict[int, dict] = {}
    for entry in vocab:
        no = entry["lesson"]
        lessons.setdefault(no, {"no": no, "theme": entry["theme"],
                                "theme_zh": entry["themeZh"], "words": []})
        lessons[no]["words"].append({"en": entry["en"], "zh": entry["zh"]})
    ordered = [lessons[n] for n in sorted(lessons)]
    for lesson in ordered:
        plan = syllabus[lesson["no"]]
        lesson["focus"] = plan["focus"]
        lesson["grammar"] = plan["grammar"]
        lesson["patterns"] = plan["patterns"]
        lesson["points"] = plan["points"]
        # 前面教過什麼，寫進提示當「不可以重教」的清單
        lesson["taught"] = [syllabus[n]["focus"] for n in range(1, lesson["no"])]
    return ordered


_BODY_HEAD = """你是台灣國小英語教材的資深編寫者。請替一本自編課本寫第 {no} 課的內容。

【本課主題】{theme}（{theme_zh}）
【本課文法點】{focus}——{grammar}
【本課句型】{patterns}
【本課必教的 20 個單字】
{words}

🚨 **文法只准教上面那一個點**。前面 {no_1} 課已經教過下列這些，本課一律不可以
再拿來當重點或當考點（單純用到不算）：
{taught}

共同要求：
1. 全部中文一律「繁體中文」，而且要**台灣用語**。寫早安／午安／晚安不寫早上好／
   下午好／晚上好；馬鈴薯不寫土豆（台灣的土豆是花生）；橡皮擦不寫橡皮；尺不寫尺子。
2. 讀者是台灣國小中高年級學生，句子要短、具體、生活化。**絕對不要加 KK 音標或任何音標**。
3. 只輸出 JSON，不要任何說明文字，不要包在程式碼區塊裡。
"""


def _body_head(lesson: dict) -> str:
    taught = lesson["taught"]
    return _BODY_HEAD.format(
        no=lesson["no"], no_1=lesson["no"] - 1,
        theme=lesson["theme"], theme_zh=lesson["theme_zh"],
        focus=lesson["focus"], grammar=lesson["grammar"],
        patterns=" ／ ".join(lesson["patterns"]),
        taught="（這是第一課，沒有前課）" if not taught
               else "、".join(taught),
        words="\n".join(f"- {w['en']}　{w['zh']}" for w in lesson["words"]))


def prompt_intro(lesson: dict) -> str:
    return _body_head(lesson) + """
請寫課名、導言與課文。課文 reading 要 8～10 句，是一個有頭有尾的小故事或情境。
**上面列的 20 個單字，至少要用掉 16 個在課文裡**——這是本課唯一一篇課文，
沒被用到的字學生整課都不會再遇到。寧可句子多一點，也不要漏字。

🚨 課文要有**人物、地點與情節**，不可以只是把句型換主詞抄十遍。
反例（不合格）：「Hello! I am OK. ／ He is fine. ／ She is sure. ／ It is OK. ／
We are fine. ／ They are welcome.」——這不是課文，是代名詞表換行印出來。
- 平均一句至少 6 個字，其中要有幾句用 and／but／because 串成兩個子句。
- 給人物名字（Mei、Tom、Lily…），讓他們在某個場景裡做某件事。

🚨 慣用語要照台灣課本的譯法，不可以逐字硬翻：
- `You are welcome.` ＝「不客氣」（**不是**「你很受歡迎」）
- `How are you?` ＝「你好嗎？」　`Excuse me.` ＝「不好意思」

JSON 格式：
{
  "title_en": "英文課名（3～5 個字）",
  "title_zh": "中文課名（6～12 字）",
  "intro_zh": "本課導言，60～90 字，要點出上面那個文法點",
  "can_do": ["學完能做到的事1", "…2", "…3"],
  "reading": {"title_en": "課文英文標題", "title_zh": "課文中文標題",
    "sentences": [{"en": "英文句", "zh": "中文翻譯"}]}
}"""


def prompt_grammar(lesson: dict, intro: dict) -> str:
    return _body_head(lesson) + f"""
請寫文法解說、情境對話與例句，全部圍繞「{lesson['focus']}」這一個點。

兩個 grammar_points 分別寫：
① {lesson['points'][0]}——一定要附 table（第一列是表頭）
② {lesson['points'][1]}——一定要附 examples

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
sentences 要 8 句，dialogue 要 4～6 句。
**sentences 是另外一區，不可以跟上面 grammar_points 的 examples 重複**——
重複的話學生等於只讀到一半的例句量。換情境、換人物、換動詞寫新的八句。"""


_EX_HEAD = """你是台灣國小英語教材的資深編寫者，正在替第 {no} 課出練習題。

【本課文法】{focus}——{grammar}
【本課 20 個單字】{words}

共同要求：
- 只能用本課與前面幾課學過的字，超綱字不要用。
- 全部中文一律繁體中文（台灣用字）。**不要 KK 音標**。
- 每題答案必須唯一且正確。
- 只輸出 JSON，不要說明文字，不要包在程式碼區塊裡。

🚨 題目的語言方向是固定的，違反的題目會被退回：
1. **選項一律是英文**。不可以出「她______一名士兵。」配選項「是／不是／會／能」——
   那題整題沒有一個英文字，考不到任何東西。
2. 考單字意思時**一律「中文題幹→選英文」**：「士兵 的英文是？」選項 soldier / king…。
   **不可以**寫成「soldier 的英文是？」——題幹已經把答案寫出來了。
3. 文法題的題幹是英文句子挖空，中文提示放在括號裡。
"""


def _ex_head(lesson: dict, body: dict) -> str:
    return _EX_HEAD.format(no=lesson["no"], focus=lesson["focus"],
                           grammar=lesson["grammar"],
                           words="、".join(w["en"] for w in lesson["words"]))


MCQ_BATCH = 10
MCQ_STYLES = [
    "以單字中譯、英文釋義、看中文選英文為主",
    "以文法選填、詞形變化為主",
    "以句意理解、情境問答、看圖說話式的情境判斷為主",
]


def prompt_mcq(lesson: dict, body: dict, n: int, style: str, avoid: list[str],
               used_opts: list[list[str]] | None = None) -> str:
    # NVIDIA 那層的輸出上限是 4000 token，30 題一次出會在半路被截斷成不合法 JSON，
    # 於是整批掉到 Haiku 去燒 Max 額度。分批出才留得住免費層。
    dodge = ""
    if avoid:
        dodge = "\n\n下列題目已經出過，不要重複或只改一個字：\n" + "\n".join(
            f"- {q}" for q in avoid)
    if used_opts:
        # 三批是分開呼叫的，不告訴它前面用過哪些選項組，它會在第二批把
        # am/is/are/be 再出一次，合起來仍是十題長一樣
        dodge += "\n\n下列這幾組選項已經用過，本批不可以再用：\n" + "\n".join(
            f"- {' / '.join(o)}" for o in used_opts)
    return _ex_head(lesson, body) + f"""
請出 **剛好 {n} 題**選擇題，每題 4 個選項，{style}。
ans 必須**逐字**等於 opts 其中一個，四個選項不可重複。
🚨 **不可以整批題目共用同一組選項、只換主詞**（例如連續五題都是
I/She/They ___ 而選項一律 am/is/are/have）——那對學生等於同一題寫五次。
每一題換不同的考點、不同的句子結構，四個選項也要跟著換：
**同一組四個選項最多只能出現在一題裡**。
🚨 誘答項要是「有可能被選錯」的字。問「你長大的地方叫什麼？」而誘答項放
wink／whisper／greeting 沒有意義，那三個一看就不是地方；要放 hometown 的
同類字（neighbor、birthday、nickname）才考得出東西。

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

🚨 三區要考不同的東西，不可以同一批句子寫兩遍：
- **unscramble 的八個答案，不可以跟 translate 的答案重複**。50 課裡有 24 課
  兩區答案 100% 相同，等於整區白放。換人物、換動詞、換情境另外寫。
- **fill 十題不可以十題都填同一個字**。L43 有九題答案都一樣、L21 有八題。
  十題要涵蓋至少四個不同的考點（動詞、名詞、介系詞、形容詞…）。
- fill 的題幹要是**英文句子**挖空，中文只放在括號裡當提示。
  「我 ___ 學生。」這種整句中文夾一個英文空格不行，學生看不出要填什麼詞類。

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


# 繁體字對了不等於台灣用語對了。這些是實際踩到的：L02 整課用「早上好／下午好／
# 晚上好」（台灣說早安／午安／晚安）、L18 把 potato 譯成「土豆」（台灣的土豆是花生，
# 而這批單字裡剛好也有 peanut）、L06/L21 的「橡皮」「尺子」。
# 檢查簡體字的那支抓不到這一類，因為每個字本身都是正體。
MAINLAND_TERMS = {
    "早上好": "早安", "下午好": "午安", "晚上好": "晚安",
    "土豆": "馬鈴薯", "西紅柿": "番茄", "尺子": "尺",
    "自行車": "腳踏車", "公交車": "公車", "出租車": "計程車",
    "視頻": "影片", "信息": "訊息", "質量": "品質", "網絡": "網路",
    "軟件": "軟體", "屏幕": "螢幕", "打印": "列印", "冰箱": "冰箱",
}


def check_usage(obj) -> list[str]:
    text = json.dumps(obj, ensure_ascii=False)
    bad = []
    for term, good in MAINLAND_TERMS.items():
        if term == good:
            continue
        if term in text:
            bad.append(f"中國用語「{term}」要改成「{good}」")
    # 橡皮單用是中國說法，橡皮擦才是台灣說法
    if re.search(r"橡皮(?!擦)", text):
        bad.append("中國用語「橡皮」要改成「橡皮擦」")
    # 慣用語逐字硬翻。You are welcome 是「不客氣」，重出的 L01 譯成「你很受歡迎」，
    # 連 fill 的中文提示都寫「你歡迎」。
    if re.search(r"(?:You|you|They|they|We|we)\s+are\s+welcome", text) and "不客氣" not in text:
        bad.append("You are welcome. 要譯成「不客氣」，不是「你很受歡迎」")
    return bad


def validate_intro(body: dict) -> list[str]:
    errs = []
    # grammar 不再由模型自己想，改由 course50-syllabus.json 綁定，所以不列在這裡
    for key in ("title_en", "title_zh", "intro_zh", "can_do", "reading"):
        if not body.get(key):
            errs.append(f"缺 {key}")
    reading = body.get("reading") or {}
    sentences = reading.get("sentences") or []
    if len(sentences) < 6:
        errs.append("課文少於 6 句")
    errs += validate_reading(sentences)
    return errs + _common_errs(body)


MIN_AVG_TOKENS = 6.0
MAX_SAME_SHAPE = 0.5


def validate_reading(sentences: list[dict]) -> list[str]:
    """課文要是有情節的短文，不是同一個句型抄十遍。

    2026-09-16 重出的 L01 十句是：Hello! I am OK. ／ Hi! You are welcome. ／
    He is fine. ／ She is sure. ／ It is OK. ／ We are fine. ／ They are welcome. …
    每一項既有檢查都綠（句數夠、單字覆蓋 100%），但它不是課文，是人稱代名詞表
    換行印出來。平均 3.7 個字一句。
    """
    if not sentences:
        return []
    errs = []
    counts = [len((s.get("en") or "").split()) for s in sentences]
    avg = sum(counts) / len(counts)
    if avg < MIN_AVG_TOKENS:
        errs.append(f"課文平均一句只有 {avg:.1f} 個字，太短不成故事"
                    f"（要 {MIN_AVG_TOKENS:.0f} 個字以上）")
    # 句型骨架：把每句的字數與第二個字（多半是動詞）當指紋
    shapes = collections.Counter(
        (len(w), w[1].lower().rstrip(".,!?") if len(w) > 1 else "")
        for w in ((s.get("en") or "").split() for s in sentences))
    shape, hits = shapes.most_common(1)[0]
    if hits / len(sentences) > MAX_SAME_SHAPE:
        errs.append(f"課文有 {hits}/{len(sentences)} 句是同一個句型（{shape[0]} 個字、"
                    f"第二個字都是 {shape[1]}），請換句型與情節")
    return errs


def _common_errs(obj) -> list[str]:
    errs = []
    if "KK" in json.dumps(obj, ensure_ascii=False):
        errs.append("出現 KK 音標")
    bad = check_simplified(obj)
    if bad:
        errs.append("簡體字：" + "".join(bad))
    return errs + check_usage(obj)


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
        if len(items) < n:
            errs.append(f"{key} 應至少 {n} 題，實得 {len(items)}")
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
    errs += validate_direction(ex)
    errs += validate_variety(ex)
    errs += validate_overlap(ex)
    bad = check_simplified(ex)
    if bad:
        errs.append("簡體字：" + "".join(bad))
    return errs + check_usage(ex)


HAS_ZH = re.compile(r"[一-鿿]")
SELF_ANSWER = re.compile(r"^\s*([A-Za-z][A-Za-z \-'()]*?)\s*的英文")


def validate_direction(ex: dict) -> list[str]:
    """擋掉中英方向錯亂的題目。

    2026-09-16 使用者在第一、二、三課就抓到三種：
      ① L03「wink 的英文是？」——題幹已經是英文，答案直接寫在題目上（24 題），
         其中一題連標準答案都填錯（「whisper 的英文是？」答案寫 wink）。
      ② L08/L10/L27/L45「她______一名士兵。」選項是「是／不是／會／能」——
         整題沒有一個英文字。
      ③ L25 題幹 not easy 是英文，選項卻是中文。
    """
    errs = []
    for i, item in enumerate(ex.get("mcq") or [], 1):
        q, opts, ans = item.get("q") or "", item.get("opts") or [], item.get("ans") or ""
        zh_opts = [o for o in opts if HAS_ZH.search(o)]
        if zh_opts:
            errs.append(f"mcq 第 {i} 題選項是中文：{zh_opts[0]}")
        hit = SELF_ANSWER.match(q)
        if hit:
            errs.append(f"mcq 第 {i} 題題幹是英文卻問「的英文是」，答案寫在題目上：{q[:24]}")
        elif ans and not HAS_ZH.search(q) and ans in q.split():
            errs.append(f"mcq 第 {i} 題答案出現在題幹裡：{q[:24]}")
    for i, item in enumerate(ex.get("translate") or [], 1):
        if not HAS_ZH.search(item.get("q") or ""):
            errs.append(f"translate 第 {i} 題題幹不是中文：{(item.get('q') or '')[:24]}")
        if HAS_ZH.search(item.get("ans") or ""):
            errs.append(f"translate 第 {i} 題答案不是英文：{(item.get('ans') or '')[:24]}")
    for key in ("fill", "unscramble"):
        for i, item in enumerate(ex.get(key) or [], 1):
            if HAS_ZH.search(item.get("ans") or ""):
                errs.append(f"{key} 第 {i} 題答案不是英文：{(item.get('ans') or '')[:24]}")
    return errs


MAX_OVERLAP = 1 / 3
MAX_SAME_FILL = 0.4
MIN_DISTINCT_FILL = 5
MIN_EN_WORDS = 2


def validate_overlap(ex: dict) -> list[str]:
    """擋掉「四個練習區其實在考同一件事」。

    2026-09-16 量出來：50 課裡有 24 課的「句子重組」與「造句翻譯」答案 **100% 重疊**
    ——同樣六到八個句子寫兩遍，等於整區白放。L43 有 90% 的填空答案是同一個字，
    L21 是 80%、L14 與 L42 是 70%。另外 L23 與 L42 各有 20 題選擇題的題幹是
    「我 ___ 學生。」這種整句中文夾一個英文空格，學生看不出要填什麼詞類。
    """
    errs = []
    norm = lambda s: re.sub(r"[^a-z ]", "", (s or "").lower()).strip()
    trans = {norm(x.get("ans")) for x in ex.get("translate") or []}
    unscr = {norm(x.get("ans")) for x in ex.get("unscramble") or []}
    trans.discard("")
    unscr.discard("")
    if trans and unscr:
        share = len(trans & unscr) / min(len(trans), len(unscr))
        if share > MAX_OVERLAP:
            errs.append(f"造句翻譯與句子重組有 {share:.0%} 的答案是同一句，"
                        f"請把重組題換成不同的句子")

    fills = [(x.get("ans") or "").strip().lower() for x in ex.get("fill") or []]
    if fills:
        word, hits = collections.Counter(fills).most_common(1)[0]
        if hits / len(fills) > MAX_SAME_FILL:
            errs.append(f"填空有 {hits}/{len(fills)} 題答案都是「{word}」，請換考點")
        # 只看「最多的那個」不夠：重出的 L01 是 is 四題、are 四題、am 兩題，
        # 最多的只佔 40% 剛好過關，但十題其實只考了三個字。
        if len(set(fills)) < MIN_DISTINCT_FILL:
            errs.append(f"填空十題只有 {len(set(fills))} 個不同答案"
                        f"（{'、'.join(sorted(set(fills)))}），至少要 {MIN_DISTINCT_FILL} 個")

    for i, item in enumerate(ex.get("mcq") or [], 1):
        q = item.get("q") or ""
        if "___" in q and len(re.findall(r"[A-Za-z]+", q)) < MIN_EN_WORDS:
            errs.append(f"mcq 第 {i} 題是中文句子夾一個英文空格，題幹要用英文句：{q[:24]}")
    return errs


MAX_SAME_OPTS = 1


def validate_variety(ex: dict) -> list[str]:
    """擋掉「十題長得一模一樣」。

    排版腳本的 pick_mcq 本來就會避開重複選項，但那是在爛牌裡挑——池子本身
    am/is/are/be 這一組在全書出現 27 次、橫跨 5 課，怎麼挑都還是同一題。
    要在生成這一端就擋。
    """
    seen: dict[tuple, int] = {}
    for item in ex.get("mcq") or []:
        key = tuple(sorted(item.get("opts") or []))
        seen[key] = seen.get(key, 0) + 1
    over = [(k, v) for k, v in seen.items() if v > MAX_SAME_OPTS]
    return [f"選擇題有 {v} 題共用同一組選項 {' / '.join(k)}" for k, v in over]


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
        # 把總題數攤到三種題型上（10 題 -> 4/3/3），避免整份考卷只剩背單字
        want = N_MCQ // len(MCQ_STYLES) + (1 if batch < N_MCQ % len(MCQ_STYLES) else 0)
        want = min(want, MCQ_BATCH, N_MCQ - len(questions))
        if want <= 0:
            break
        part, errs = ask(
            prompt_mcq(lesson, body, want, style, [q["q"] for q in questions],
                       [sorted(q["opts"]) for q in questions]),
            lambda d, n=want, seen=[sorted(q["opts"]) for q in questions]:
                validate_exercises(d, {"mcq": n})
                + [f"這組選項前面已經用過：{' / '.join(o)}"
                   for o in (sorted(x.get("opts") or []) for x in d.get("mcq") or [])
                   if o in seen],
            stage=f"選擇題{batch + 1}")
        if part is None:
            return None, [f"選擇題第 {batch + 1} 批：" + "；".join(errs)]
        questions.extend(part["mcq"])
    mcq = {"mcq": questions[:N_MCQ]}
    # 選項多樣性要整課一起看。三批是分開出的，每批各自都合格，合起來仍可能
    # 十題共用 am/is/are/be——批次內的檢查抓不到跨批重複。
    cross = validate_variety(mcq)
    if cross:
        return None, ["選擇題跨批重複：" + "；".join(cross)]

    drills, errs = ask(prompt_drills(lesson, body),
                       lambda d: validate_exercises(
                           d, {"fill": N_FILL, "translate": N_TRANSLATE,
                               "unscramble": N_UNSCRAMBLE}),
                       stage="填空造句")
    if drills is None:
        return None, ["填空造句：" + "；".join(errs)]
    ex = {**mcq, **drills}
    rebuild_scrambles(ex, seed=lesson["no"])
    shuffle_options(ex, seed=lesson["no"])
    body.update({"no": lesson["no"], "theme": lesson["theme"],
                 "theme_zh": lesson["theme_zh"], "words": lesson["words"],
                 "focus": lesson["focus"], "grammar": lesson["grammar"],
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


def shuffle_options(ex: dict, seed: int = 0) -> int:
    """把選擇題的四個選項洗牌，讓正確答案平均落在 A～D。

    🚨 引擎幾乎都把正確答案寫在第一個：全書 1355 題裡有 1005 題（74%）答案是 (A)，
    而排版與網站兩邊都沒有洗牌，所以原樣印到紙上——學生一路猜 A 就有七成分。
    這裡用課號當種子，重跑結果一樣，改版時 diff 不會整本翻掉。
    """
    rng = random.Random(1000 + seed)
    items = ex.get("mcq") or []
    slots = [i % 4 for i in range(len(items))]
    rng.shuffle(slots)
    for item, slot in zip(items, slots):
        opts, ans = item.get("opts") or [], item.get("ans")
        if len(opts) != 4 or ans not in opts:
            continue
        rest = [o for o in opts if o != ans]
        rng.shuffle(rest)
        item["opts"] = rest[:slot] + [ans] + rest[slot:]
    return len(items)


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


def word_forms(en: str):
    """詞條可能出現在課文裡的各種寫法。

    詞表把複數寫成 apple(s)、peach(es)、mango(es)，課文裡當然是 apple／peaches。
    只切「/」和「、」的話這些字永遠比對不到——L19 就因此被判成覆蓋率 35%、
    白白整課重做兩次，其實課文一直是好的。
    """
    for chunk in re.split(r"[/、]", en):
        chunk = chunk.strip()
        if not chunk:
            continue
        yield chunk.lower()
        match = re.match(r"^(.*?)\(([A-Za-z]+)\)$", chunk)
        if match:
            stem, suffix = match.group(1).strip(), match.group(2)
            yield stem.lower()
            yield (stem + suffix).lower()


def coverage(lesson: dict) -> float:
    """本課單字有多少真的出現在課文／例句／題目裡。"""
    blob = json.dumps({k: v for k, v in lesson.items() if k != "words"},
                      ensure_ascii=False).lower()
    hit = sum(1 for word in lesson["words"]
              if any(form in blob for form in word_forms(word["en"])))
    return hit / len(lesson["words"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, action="append", help="只跑指定課次")
    ap.add_argument("--range", help="課次範圍，例如 20-29；多開幾條工人分攤時用")
    ap.add_argument("--redo", action="store_true", help="連已完成的也重做")
    ap.add_argument("--check", action="store_true", help="只驗現有產出")
    ap.add_argument("--requiz", action="store_true",
                    help="只重出選擇題（配 --only 用），課文文法不動")
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

    if args.requiz:
        for lesson in lessons:
            if args.only and lesson["no"] not in args.only:
                continue
            path = OUT_DIR / f"L{lesson['no']:02d}.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            fresh, failed = [], False
            for batch, style in enumerate(MCQ_STYLES):
                want = N_MCQ // len(MCQ_STYLES) + (1 if batch < N_MCQ % len(MCQ_STYLES) else 0)
                part, errs = ask(
                    prompt_mcq(lesson, data, want, style, [q["q"] for q in fresh]),
                    lambda d, n=want: validate_exercises(d, {"mcq": n}),
                    stage=f"選擇題{batch + 1}")
                if part is None:
                    print(f"L{lesson['no']:02d} ✗ {'；'.join(errs)}", flush=True)
                    failed = True
                    break
                fresh.extend(part["mcq"])
            if failed:
                continue
            data["exercises"]["mcq"] = fresh
            dedupe_mcq(data["exercises"])
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                            encoding="utf-8")
            print(f"L{lesson['no']:02d} ✓ 選擇題重出 {len(data['exercises']['mcq'])} 題",
                  flush=True)
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
            shuffle_options(ex, seed=lesson["no"])
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
