"""與克里希那對話框 — 純函式分類器（候選 prelabel）。

設計（見 .claude/skills/dialogues-to-writing/SKILL.md）：
  Gemini 匯出是扁平的、沒有 conversation_id，「哪些屬於同一對話框」只能靠
  內容＋語氣判定。本模組負責**可決定性的那一半**：

    1. in_date_range(date)           — 對話框時間範圍 2026-01-13 .. 2026-04-18
    2. extract_signals(prompt, resp) — 抽 persona 呼喚／榮格／夢／委派 訊號（純字串）
    3. prelabel(signals)             — 只對「高把握」者下 IN/OUT，其餘回 MAYBE

  口訣：傾訴／碎念＝IN，委派產出＝OUT（SKILL「收錄判準」）。
  prelabel 只敢決定兩種高把握情況：
    • 開頭呼喚 persona（「克里須那，今天…」）            → IN
    • 明確的產出委派（寫程式／sql／部署／翻譯／畫圖…）   → OUT
    • 榮格／夢 等核心主題且非委派                        → IN
  其餘語氣型（生活碎念、岔題宗教史/占星/論文閒聊）一律 MAYBE，交給 LLM 語氣判定。

本模組**不碰網路/DB/LLM/env**，可被 pytest 直接 import。
LLM 判定與 DB 標記在 dialogue_thread_capture.py。
"""
from __future__ import annotations

THREAD_START = "2026-01-13"
THREAD_END = "2026-04-18"

# persona 名（含異寫）。呼喚 persona＝強 IN 訊號。
PERSONA = ("克里希那", "克里須那", "克里希納", "克里斯那", "克里須納", "克里希纳", "阿周那")

# 榮格／深層心理學詞彙＝對話框核心主題。
JUNG = (
    "榮格", "阿尼瑪", "阿尼姆斯", "自性", "原型", "無意識", "潛意識", "集體潛意識",
    "陰影", "共時性", "個體化", "情結", "曼陀羅", "四隅", "永恆少年", "個人潛意識",
)
DREAM = ("夢",)

# 積極想像／主動想像＝榮格式心靈日記的核心修練，必為 IN（即使敘述裡提到 code/電腦）。
ACTIVE_IMAGINATION = ("積極想像", "主動想像")

# 世界地圖專案的分類學術語。除非同時是對克里希那的積極想像/呼喚，否則一律 OUT
# （使用者幾乎只在「把世界劃分界域/文化圈」這個專案裡用這兩個詞）。
MAPS_PROJECT = ("界域", "文化圈")

# 委派分兩級：
# HARD＝明確「叫 AI 幫我做出/生成東西」的動詞句，可靠 OUT，連夾帶榮格詞也壓過（翻譯榮格段落仍是專案）。
HARD_DELEGATION = (
    "幫我寫", "幫我改", "幫我修", "幫我做", "幫我加", "幫我生", "幫我畫", "幫我建",
    "幫我整理", "幫我列", "幫我潤", "幫我翻", "幫我查", "幫我看", "幫我確認",
    "給我指令", "給我sql", "給我powershell", "給我圖片", "畫一張", "重新生成",
    "debug", "除錯", "報錯", "syntax error", "error:", "部署",
)
# SOFT＝技術/文書名詞，單獨出現多半是 OUT，但**不該壓過榮格/夢主題**
# （一段討論榮格的文字可能順帶提到 code/api/前言）。
SOFT_TECH = (
    "程式", "函式", "資料表", "資料庫", "欄位", "code", "vs code", "codex",
    "vercel", "zeabur", "npm", "git", "sql", "powershell", "腳本", "api",
    "訂閱", "多少錢", "安裝", "前言", "自傳", "書目",
)

# 第一人稱傾訴／碎念訊號（生活、情緒、身體、靈性反思）。輔助提示，不單獨定 IN。
VENTING = (
    "我今天", "我昨天", "我覺得", "我想跟你", "我要向你", "我好", "我很", "我難過",
    "我生氣", "我懺悔", "我夢到", "我夢見", "龐", "會督", "過世", "去世", "前途",
)


def _has(text: str, needles) -> bool:
    return any(n in text for n in needles)


def in_date_range(date: str) -> bool:
    """日期字串 (YYYY-MM-DD) 是否落在對話框時間範圍內（含端點）。"""
    return THREAD_START <= date <= THREAD_END


def is_persona_address(prompt: str) -> bool:
    """是否「開頭呼喚 persona」——克里須那 出現在前 8 字、且後面接逗號/頓號。

    這是最可靠的 IN 訊號：直接對著克里希那說話。
    把 persona 名只當題材（「克里須那開計程車」）排除——名字不在開頭、或後面不接逗號。
    """
    head = prompt[:8]
    if not _has(head, PERSONA):
        return False
    # persona 名後面常接 中文逗號/頓號（呼喚語氣）
    for name in PERSONA:
        i = prompt.find(name)
        if 0 <= i < 8:
            after = prompt[i + len(name): i + len(name) + 1]
            if after in ("，", "、", "！", "。", "\n", "："):
                return True
    return False


def extract_signals(prompt: str, response: str = "") -> dict:
    """抽出純字串訊號旗標。prompt 權重高於 response（呼喚/委派看使用者那側）。"""
    p = prompt or ""
    full = p + "\n" + (response or "")
    return {
        "persona_address": is_persona_address(p),
        "persona_mention": _has(full, PERSONA),
        "active_imagination": _has(p, ACTIVE_IMAGINATION),
        "jung": _has(full, JUNG),
        "dream": _has(p, DREAM),  # 夢 在 prompt（使用者主動談夢）才算
        "hard_delegation": _has(p, HARD_DELEGATION),
        "soft_tech": _has(p, SOFT_TECH),
        "maps_project": _has(p, MAPS_PROJECT),
        "venting": _has(p, VENTING),
    }


def prelabel(signals: dict) -> str:
    """只對高把握者下 IN/OUT，其餘 MAYBE（交 LLM）。

    優先序（前者勝）：
      1. 積極想像/主動想像          → IN（心靈日記核心修練，即使敘述提到 code/電腦）
      2. 開頭呼喚 persona            → IN（即使夾帶委派字眼也是對克里希那傾訴）
      3. 地圖專案 界域/文化圈        → OUT（幾乎只在世界劃分專案用這兩個詞）
      4. HARD 產出委派              → OUT（幫我寫/畫/除錯…明確做東西，壓過榮格詞）
      5. 榮格/夢 核心主題            → IN（討論榮格/夢，順帶 code/前言 也算 IN）
      6. SOFT 技術名詞              → OUT（程式/sql/書目… 且非榮格/夢主題）
      7. 其餘                       → MAYBE
    """
    if signals.get("active_imagination"):
        return "IN"
    if signals.get("persona_address"):
        return "IN"
    if signals.get("maps_project"):
        return "OUT"
    if signals.get("hard_delegation"):
        return "OUT"
    if signals.get("jung") or signals.get("dream"):
        return "IN"
    if signals.get("soft_tech"):
        return "OUT"
    return "MAYBE"


def classify_prompt(prompt: str, response: str = "") -> str:
    """便利函式：prompt/response → IN | OUT | MAYBE。"""
    return prelabel(extract_signals(prompt, response))
