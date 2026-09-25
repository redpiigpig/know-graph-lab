# -*- coding: utf-8 -*-
r"""全站既有譯文的共用修正工具（2026-09-25）。

為什麼有這支
------------
2026-09-25 全站稽核（記憶檔 project_translation_audit_2026_09_25）找到六類問題，
使用者當天逐項定了處理方式。各語料的譯文散在四種地方（Drive JSONL、DB 三張表、
repo 的 data/*/sources），以前每修一類就寫一支一次性腳本，判準各寫各的、測試也沒有。
這支把**判準**收成一組純函式（測試鎖在 scripts/tests/test_translation_fix.py），
**讀寫**收成各語料一個 adapter，其他 agent 修自己的語料時直接拿來用。

規則（使用者 2026-09-25 的決定，照做、不擴大）
------------------------------------------------
確定性修正（改字，不清空）：
  numerals     只改三位以上有效數字的四位數以上數字（一千兩百三十四→1,234）與
               「一千零三十六年」這類年數（→1036年）。不改：經文語料、世紀／年代、
               兩位有效數字（四千五百、二十五萬）、逐位寫的西元年月日（一九六九年，
               這次不批改）、非西元紀年（年號、民國、佛曆）、詩句與成語（一千零一夜）、
               序數（第一千二百五十條）。
  middle_dot   中文人名之間的「·」「・」→「‧」。英文、數字、書名號裡的點不動。
  zhi          「隻能／隻是／隻有／隻要」→「只…」，量詞（每隻、一隻、船隻）不動。
  toufa        「頭發」→「頭髮」，「開頭發表」「帶頭發起」這種不動。
  variants     大陸／舊字形 爲衆着裏綫… → 台灣字形。含假名的段落整段不碰（日文原字形）。
  quotes       彎引號 “ ” ‘ ’ → 「」『』。引號裡是英文（英文引文、書目篇名）就保留。
  heading      章名黏正文（`## 第一章當我…`）→ 從原文 heading 的邊界切回獨立一行；
               章名後只隔一個換行（reader 會把整段吃進標題）→ 補空行。

清空（交給補譯 agent 重譯，不在這裡改字）：
  meta         模型拒答／回話（「請提供完整的文段內容」「我注意到您提供的…」）
  think        `<think>` 外洩、推理外洩、自我商議
  fffd         U+FFFD 亂碼字元
  untranslated 該譯而未譯的外文段（英文整段、日文殘段）

不在本輪：譯名統一（另案）、聖經直譯（經文不動）。

用法
----
  python -X utf8 scripts/translation_fix.py scan --corpus lit_review
  python -X utf8 scripts/translation_fix.py scan --corpus all            # 全語料，寫報告
  python -X utf8 scripts/translation_fix.py scan --corpus books --ids <ebook_id> ...
  python -X utf8 scripts/translation_fix.py apply --corpus books --ids <ebook_id> --dry-run
  python -X utf8 scripts/translation_fix.py apply --corpus gnostic --ids 12 34 --rules fixes
  python -X utf8 scripts/translation_fix.py lanes                        # 看哪些書正被 lane 寫

scan 永遠唯讀。apply 預設**所有**規則（修正＋清空）；`--rules fixes` 只做確定性修正，
`--rules clear` 只做清空，也可以逐條列：`--rules zhi,toufa,meta`。
輸出（scan 報告、清空清單）在 output/translation_fix/（不進 git）。

🚨 apply 會跳過「正在被 fleet lane 寫」的書：讀 scripts/state/fleet_*.pid，程序還活著
就從它的命令列（--author／--work／UUID）推出它負責的書；另外 JSONL 30 分鐘內動過的
一律跳過。兩道都是保守判斷，寧可少修一本，不可跟 lane 搶寫同一個檔。
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATE_DIR = SCRIPTS / "state"
OUT_DIR = ROOT / "output" / "translation_fix"
CHUNKS_DIR = Path(os.environ.get(
    "EBOOK_CHUNKS_DIR", r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks"))

_HAN = "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
_HAN_RE = re.compile(f"[{_HAN}]")
_KANA_RE = re.compile(r"[ぁ-ゖァ-ヺ]")
_LATIN_RE = re.compile(r"[A-Za-zÀ-ɏ]")


# ═════════════════════════════════════════════════════════════════════════════
#  一、確定性修正（純函式：text → (新 text, 命中數)）
# ═════════════════════════════════════════════════════════════════════════════

# ── 1. 數字 ─────────────────────────────────────────────────────────────────
_NUM_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_NUM_UNIT = {"十": 10, "百": 100, "千": 1000}
_NUM_BIG = {"萬": 10_000, "億": 100_000_000}
_NUM_CHARS = "".join(_NUM_DIGIT) + "".join(_NUM_UNIT) + "".join(_NUM_BIG)
# 開頭必須是數字字（一～九、兩）——「千百年來」「千萬不要」「萬一」不是數字。
_NUM_RUN = re.compile(f"[一二兩三四五六七八九十][{_NUM_CHARS}]*")
# 前面接這些就不是一般數量：序數、非西元紀年、已經是阿拉伯數字的延續。
_NUM_BAD_PREFIX = re.compile(
    r"(第|民國|民国|佛曆|佛紀|皇紀|紀元|回曆|伊曆|希吉拉曆|猶太曆|創世紀元|建城|羅馬建城"
    r"|明治|大正|昭和|平成|令和|光緒|宣統|同治|咸豐|道光|嘉慶|乾隆|康熙|開元|貞觀)$")
# 成語、書名、固定說法：整串原樣保留。
_NUM_IDIOMS = ("一千零一夜", "一千零一", "八萬四千", "三千大千", "十萬八千")


def parse_zh_number(s: str) -> int | None:
    """位值寫法的中文數字 → int。不是位值寫法（例如逐位的「一九六九」）回 None。"""
    if not s:
        return None
    if not any(c in _NUM_UNIT or c in _NUM_BIG for c in s):
        return None  # 逐位寫法（一九六九）或單個數字：不是本規則的對象
    total, section, digit = 0, 0, None
    last_unit = 10 ** 9
    for c in s:
        if c in _NUM_DIGIT:
            if digit is not None and c not in "〇零":
                return None  # 兩個數字字連在一起（一二百）：不是規範寫法
            digit = _NUM_DIGIT[c] if c not in "〇零" else None
        elif c in _NUM_UNIT:
            u = _NUM_UNIT[c]
            if u >= last_unit:
                return None
            last_unit = u
            section += (digit if digit is not None else 1) * u
            digit = None
        elif c in _NUM_BIG:
            section += digit or 0
            digit = None
            if section == 0:
                return None
            total += section * _NUM_BIG[c]
            section = 0
            last_unit = 10 ** 9
        else:
            return None
    section += digit or 0
    return total + section


def significant_digits(n: int) -> int:
    s = str(n).rstrip("0")
    return len(s)


def fix_numerals(text: str) -> tuple[str, int]:
    """三位以上有效數字的四位數以上數字 → 阿拉伯數字。後接「年」且落在 1000–2999
    的當年份寫（1036年），其餘加千分位（1,234人）。"""
    if not text:
        return text, 0
    hits = 0
    out: list[str] = []
    pos = 0
    for m in _NUM_RUN.finditer(text):
        s, e = m.start(), m.end()
        run = m.group(0)
        # 「六十年代」「十九世紀」本身不到四位數，自然不會中；這裡只擋會中的例外。
        window = text[max(0, s - 6):s]
        if _NUM_BAD_PREFIX.search(window):
            continue
        ctx = text[max(0, s - 3):e + 3]
        if any(idiom in ctx and idiom.startswith(run[:2]) for idiom in _NUM_IDIOMS):
            continue
        # 尾巴的「零」「〇」不算數字的一部分（「一千二百三十零」不存在，但防呆）
        n = parse_zh_number(run)
        if n is None or n < 1000 or significant_digits(n) < 3:
            continue
        nxt = text[e:e + 1]
        after2 = text[e:e + 2]
        if nxt == "年" and after2 != "年代" and 1000 <= n <= 2999:
            rep = str(n)
        else:
            rep = f"{n:,}"
        out.append(text[pos:s])
        out.append(rep)
        pos = e
        hits += 1
    if not hits:
        return text, 0
    out.append(text[pos:])
    return "".join(out), hits


# ── 2. 中間點 ───────────────────────────────────────────────────────────────
# 只換「兩側都是漢字」的點。英文（J·S）、數字（3·14）兩側不是漢字，自然不中。
_DOT_RE = re.compile(f"(?<=[{_HAN}])[·・•∙⋅](?=[{_HAN}])")


def fix_middle_dot(text: str) -> tuple[str, int]:
    """中文人名之間的點統一成「‧」（U+2027）。書名號《》〈〉裡的點不動（書目），
    含假名的段落不動（日文的「・」是本字）。"""
    if not text or _KANA_RE.search(text):
        return text, 0
    hits = 0
    out = []
    depth = 0
    for i, ch in enumerate(text):
        if ch in "《〈":
            depth += 1
        elif ch in "》〉":
            depth = max(0, depth - 1)
        if depth == 0 and ch in "·・•∙⋅" and _DOT_RE.match(text, i):
            out.append("‧")
            hits += 1
        else:
            out.append(ch)
    return ("".join(out), hits) if hits else (text, 0)


# ── 3. 隻能／隻是／隻有／隻要 ─────────────────────────────────────────────────
# 前一個字是數詞、「每」或「船／艦」時，「隻」是量詞或名詞的一部分，不是「只」。
# 🚨「這隻是／那隻是」**要改**：量詞「這隻」後面接的是名詞（這隻羊），直接接「是」
# 幾乎一定是「這只是」被轉壞——這是全站最常見的一種。
_ZHI_RE = re.compile(r"隻(?=[能是有要])")
_ZHI_MEASURE_PREV = set("一二兩三四五六七八九十百千萬幾每某半數多整各單零0123456789０１２３４５６７８９船艦舟")


def fix_zhi(text: str) -> tuple[str, int]:
    if not text or "隻" not in text:
        return text, 0
    hits = 0
    chars = list(text)
    for m in _ZHI_RE.finditer(text):
        i = m.start()
        prev = text[i - 1] if i else ""
        if prev in _ZHI_MEASURE_PREV:
            continue
        chars[i] = "只"
        hits += 1
    return ("".join(chars), hits) if hits else (text, 0)


# ── 4. 頭發 → 頭髮 ──────────────────────────────────────────────────────────
# 「頭」＋「發X」的動詞複合詞（開頭發表、帶頭發起、從頭發展）不是頭髮。
_FA_VERB_NEXT = set("表起展生現出動佈布射言明給放行售揮芽酵燒熱怒抖亮光作送電願誓號財達難愁覺掘揚病覺配散聲問")
_FA_PREV_BLOCK = set("開帶起源從為領打出口念苗鏡")


def fix_toufa(text: str) -> tuple[str, int]:
    if not text or "頭發" not in text:
        return text, 0
    hits = 0
    chars = list(text)
    for m in re.finditer("頭發", text):
        i = m.start()
        nxt = text[i + 2:i + 3]
        prev = text[i - 1:i]
        if nxt in _FA_VERB_NEXT or prev in _FA_PREV_BLOCK:
            continue
        chars[i + 1] = "髮"
        hits += 1
    return ("".join(chars), hits) if hits else (text, 0)


# ── 5. 大陸／舊字形 → 台灣字形 ──────────────────────────────────────────────
# 只收「台灣標準一定用右邊那個字」的單字對。OpenCC t2tw 會連「纔→才」「喫→吃」
# 一起改，那兩個在台灣是合法用字，所以不用 t2tw、自己列。
VARIANTS = {
    "爲": "為",  # 爲→為
    "衆": "眾",  # 衆→眾
    "着": "著",  # 着→著
    "裏": "裡",  # 裏→裡
    "綫": "線",  # 綫→線
    "羣": "群",  # 羣→群
    "啓": "啟",  # 啓→啟
    "敎": "教",  # 敎→教
    "僞": "偽",  # 僞→偽
    "眞": "真",  # 眞→真
    "峯": "峰",  # 峯→峰
    "鷄": "雞",  # 鷄→雞
    "牀": "床",  # 牀→床
    "竪": "豎",  # 竪→豎
    "衞": "衛",  # 衞→衛
    "户": "戶",  # 户→戶
    "説": "說",  # 説→說
    "麪": "麵",  # 麪→麵
    "敍": "敘",  # 敍→敘
    "奬": "獎",  # 奬→獎
    "愼": "慎",  # 愼→慎
    "鎭": "鎮",  # 鎭→鎮
    "顚": "顛",  # 顚→顛
    "塡": "填",  # 塡→填
    "値": "值",  # 値→值
    "悦": "悅",  # 悦→悅
    "脱": "脫",  # 脱→脫
    "税": "稅",  # 税→稅
    "鋭": "銳",  # 鋭→銳
    "閲": "閱",  # 閲→閱
}
VARIANTS = {k: v for k, v in VARIANTS.items() if k != v}
_VARIANT_TABLE = str.maketrans(VARIANTS)
_VARIANT_RE = re.compile("[" + "".join(VARIANTS) + "]")


def fix_variants(text: str) -> tuple[str, int]:
    """含假名的段落不碰：日文原文與日文書名照原漢字（記憶檔
    feedback_translation_register_and_titles）。"""
    if not text or _KANA_RE.search(text):
        return text, 0
    n = len(_VARIANT_RE.findall(text))
    return (text.translate(_VARIANT_TABLE), n) if n else (text, 0)


# ── 6. 彎引號 ───────────────────────────────────────────────────────────────
_DQ_RE = re.compile(r"“([^“”\n]*)”")
_SQ_RE = re.compile(r"‘([^‘’\n]*)’")


def _is_cjk_quote(inner: str) -> bool:
    """引號內容以漢字為主 → 中文引號。英文引文、英文篇名（書目）→ 保留。"""
    han = len(_HAN_RE.findall(inner))
    lat = len(_LATIN_RE.findall(inner))
    return han > 0 and han >= lat


def _depth_before(text: str, i: int) -> int:
    return max(0, text.count("「", 0, i) - text.count("」", 0, i))


def fix_curly_quotes(text: str) -> tuple[str, int]:
    if not text or not any(c in text for c in "“”‘’"):
        return text, 0
    hits = 0

    def dq(m: re.Match) -> str:
        nonlocal hits
        inner = m.group(1)
        if not _is_cjk_quote(inner):
            return m.group(0)
        hits += 1
        inner = _SQ_RE.sub(lambda mm: ("『" + mm.group(1) + "』") if _is_cjk_quote(mm.group(1))
                           else mm.group(0), inner)
        return "「" + inner + "」"

    text = _DQ_RE.sub(dq, text)

    def sq(m: re.Match) -> str:
        nonlocal hits
        inner = m.group(1)
        if not _is_cjk_quote(inner):
            return m.group(0)  # 英文撇號（don’t）與英文單引號引文都不中
        hits += 1
        nested = _depth_before(m.string, m.start()) > 0
        return ("『" + inner + "』") if nested else ("「" + inner + "」")

    text = _SQ_RE.sub(sq, text)
    return text, hits


# ── 7. 章名黏正文 ───────────────────────────────────────────────────────────
_HEAD_LINE = re.compile(r"(?m)^(#{1,6})[ \t]+(.+)$")
_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
_SRC_NUM_HEAD = re.compile(
    r"^(chapter|chap\.?|book|section|sect\.?|part|letter|epistle|homily|sermon|"
    r"psalm|question|article|lecture|oration|discourse|treatise|canon|kapitel|buch|"
    r"lib\.?|liber|caput|cap\.?)\s+([ivxlcdm]+|\d+)\.?\s*$", re.I)
# 譯文裡這種章名的樣子：第＋中文或阿拉伯數字＋量詞
_ZH_NUM_HEAD = re.compile(
    r"^(第[〇零一二兩三四五六七八九十百千0-9０-９]+[章卷篇節封講書部條問題款課])")


def _is_title_like(line: str) -> bool:
    return len(line) <= 40 and "。" not in line


def _src_number(tok: str) -> int | None:
    tok = tok.strip().upper()
    if tok.isdigit():
        return int(tok)
    if not tok or any(c not in _ROMAN for c in tok):
        return None
    total = 0
    for i, c in enumerate(tok):
        v = _ROMAN[c]
        total += -v if i + 1 < len(tok) and _ROMAN[tok[i + 1]] > v else v
    return total


_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


def _heading_number(zh_head: str) -> int | None:
    """「第十七章」→ 17、「第17章」→ 17。"""
    core = zh_head[1:-1].translate(_FULLWIDTH_DIGITS)
    if core.isdigit():
        return int(core)
    if core in _NUM_DIGIT:
        return _NUM_DIGIT[core]
    if core.startswith("十"):
        core = "一" + core
    return parse_zh_number(core)


def para_count(text: str) -> int:
    return len([p for p in re.split(r"\n\s*\n", text or "") if p.strip()])


def split_glued_heading(zh: str, src: str = "") -> tuple[str, int]:
    """兩種黏法：
      A. `## 標題\n正文`：標題後只隔一個換行。reader 的標題規則吃到下一個空行為止，
         整段正文會變成一個巨大的標題 → 補一個空行。這種不需要原文。
      B. `## 第一章當我與…`：標題與正文在同一行。從**原文**的 heading 判斷邊界：
         原文那一行只有「Chapter I.」這種編號標題時，譯文標題就是開頭的「第一章」，
         在那裡切開。原文標題還帶別的文字時判不出邊界，**不動**（scan 報告另計）。
    """
    if not zh or "#" not in zh:
        return zh, 0
    hits = 0
    src_heads = [m.group(2).strip() for m in _HEAD_LINE.finditer(src or "")]
    lines = zh.split("\n")
    out: list[str] = []
    hidx = -1
    for k, line in enumerate(lines):
        m = _HEAD_LINE.match(line)
        if not m:
            out.append(line)
            continue
        hidx += 1
        marks, body = m.group(1), m.group(2).strip()
        sh = src_heads[hidx] if hidx < len(src_heads) else ""
        # B：同一行
        sm = _SRC_NUM_HEAD.match(sh) if sh else None
        if not _is_title_like(body) and sm:
            zm = _ZH_NUM_HEAD.match(body)
            if (zm and len(body) > len(zm.group(1)) + 1
                    and _heading_number(zm.group(1)) == _src_number(sm.group(2))):
                title = zm.group(1)
                rest = body[len(title):].lstrip(" 　：:．.—-")
                out.append(f"{marks} {title}")
                out.append("")
                out.append(rest)
                hits += 1
                # 後面若緊接正文（單換行），交給 A 處理不到——這裡的 rest 已是正文，
                # 下一行若不是空行，補一個空行保持段落分隔。
                if k + 1 < len(lines) and lines[k + 1].strip():
                    out.append("")
                continue
        out.append(line)
        # A：標題後只隔一個換行就接正文
        if k + 1 < len(lines):
            nxt = lines[k + 1]
            if nxt.strip() and not _HEAD_LINE.match(nxt):
                out.append("")
                hits += 1
    return ("\n".join(out), hits) if hits else (zh, 0)


def glued_heading_unresolved(zh: str, src: str = "") -> int:
    """標題行長得像正文（>40 字且有句號）、但 split_glued_heading 判不出邊界的數目。
    只報告，不修——交給人或補譯 agent。"""
    fixed, _ = split_glued_heading(zh, src)
    return sum(1 for m in _HEAD_LINE.finditer(fixed) if not _is_title_like(m.group(2).strip()))


# ═════════════════════════════════════════════════════════════════════════════
#  二、清空判準（純函式：回傳原因字串，空字串＝不必清）
# ═════════════════════════════════════════════════════════════════════════════
# 開頭 40 字內出現才算——拒答與回話一律是開場白。沿用
# audit_llm_meta_replies.META_MARKERS 的收詞原則：只收「指涉任務／輸入」的字串。
META_MARKERS = (
    "我無法翻譯", "我無法完成", "您提供的", "請提供", "請貼上", "請輸入",
    "我需要澄清", "並非英文", "不是英文", "似乎不是英文",
    "無法進行翻譯", "這段文字似乎", "作為一個 AI", "作為一個語言模型", "作為一個人工智慧",
    "提供的英文", "提供的文本", "提供的原文", "您給的", "你提供", "無法提供準確翻譯",
    "無法進行準確", "無法提供翻譯", "我在提供的", "我需要指出", "似乎是亂碼",
    "非標準拼寫", "似乎不完整", "看起來是梵文", "而非英文", "我已準備好", "我準備好",
    "閣下提供的", "此處英文原文", "好的，以下是", "以下是翻譯", "以下是譯文", "以下為翻譯",
    "文段內容",
    "I'm ready to", "I am ready to", "I appreciate your",
    "I cannot translate", "I can't translate", "I'm unable to", "As an AI",
    "The text you provided", "Please provide", "I need to clarify",
    "Here is the translation", "Sure, here",
)
# 這幾個字本身在正常譯文裡也會出現（小說對白「抱歉，我來晚了」），
# 要同一個開頭視窗裡還提到任務（翻譯／原文／提供／文本）才算回話。
META_WEAK = ("我注意到", "抱歉", "我很遺憾", "似乎不是", "I notice", "I apologize",
             "It appears that the")
META_TASK_WORDS = ("翻譯", "譯文", "原文", "提供", "文本", "文段", "translat", "text")
META_WINDOW = 40
_THINK_RE = re.compile(r"</?think>|</?thinking>|◁/?think▷", re.I)
_COT_MARKERS = (
    "we need to translate", "we must not add", "let me translate",
    "following all the rules", "just output the translation",
    "the user wants", "i need to translate", "thus final output",
    "we should translate", "the given english paragraph",
    "we need to preserve", "choose whichever reads naturally",
)
_EN_FUNCTION_RE = re.compile(
    r"\b(the|of|and|to|is|are|was|were|that|which|with|from|this|these|there"
    r"|we|it|in|by|as|not|but|have|has|been|would|could)\b", re.I)
_DE_FUNCTION_RE = re.compile(
    r"\b(der|die|das|und|ist|nicht|mit|von|zu|den|dem|ein|eine|sich|auf|für|auch|wird)\b", re.I)
_FR_FUNCTION_RE = re.compile(
    r"\b(le|la|les|et|est|des|une|dans|qui|que|pour|pas|sur|avec|il|elle|nous)\b", re.I)
_ALLCAPS_RE = re.compile(r"\b[A-ZÀ-Þ]{3,}\b")
_JA_HEAD_CHARS = 12
_JA_MIN_RATIO = 0.25
BILINGUAL_SEP = "　／　"


def clear_reason(zh: str, src: str = "", *, allow_japanese: bool = False) -> str:
    """這段譯文該不該清空重譯。回傳 'meta' / 'think' / 'fffd' / 'untranslated' / ''。

    `src` 用來判斷「未譯」：譯文跟原文幾乎一樣、而原文是外文，就是沒譯。
    `allow_japanese=True` 給本來就該是日文的欄位（不會用到 zh 欄，保留給呼叫端）。
    """
    t = (zh or "").strip()
    if not t:
        return ""
    if _THINK_RE.search(t):
        return "think"
    low = t.lower()
    if any(m in low for m in _COT_MARKERS):
        return "think"
    head = t[:META_WINDOW]
    if any(m in head for m in META_MARKERS):
        return "meta"
    if any(m in head for m in META_WEAK):
        wide = t[:META_WINDOW * 2].lower()
        if any(w in wide for w in META_TASK_WORDS):
            return "meta"
    if "\ufffd" in t:
        return "fffd"
    if BILINGUAL_SEP in t:
        return ""  # 並列體例「原文　／　中譯」是刻意留原文
    # 日文殘段：假名多、而且一開頭就是日文（並列體例一律中譯在前）
    if not allow_japanese:
        kana = len(_KANA_RE.findall(t))
        if kana / len(t) >= _JA_MIN_RATIO and _KANA_RE.search(t[:_JA_HEAD_CHARS]):
            return "untranslated"
    han = len(_HAN_RE.findall(t))
    lat = len(_LATIN_RE.findall(t))
    if lat >= 40 and han * 3 < lat:
        if len(_ALLCAPS_RE.findall(t)) >= 2 and han == 0 and _looks_bibliographic(t):
            return ""  # 西文書目條目：書名本來就留原文
        dens = max(len(_EN_FUNCTION_RE.findall(t)), len(_DE_FUNCTION_RE.findall(t)),
                   len(_FR_FUNCTION_RE.findall(t))) / (lat / 100)
        if dens >= 4.0:
            return "untranslated"
    # 譯文與原文逐字相同（>=30 字、原文是外文）＝原樣吐回
    s = (src or "").strip()
    if s and len(t) >= 30 and t == s and han * 3 < lat:
        return "untranslated"
    return ""


_BIB_RE = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b|pp?\.\s*\d|\bed\.|\beds\.|\bvol\.|\btrans\.", re.I)


def _looks_bibliographic(t: str) -> bool:
    return len(_BIB_RE.findall(t)) >= 2


# ═════════════════════════════════════════════════════════════════════════════
#  三、規則表與套用
# ═════════════════════════════════════════════════════════════════════════════
FIX_RULES: dict[str, Callable[[str], tuple[str, int]]] = {
    "numerals": fix_numerals,
    "middle_dot": fix_middle_dot,
    "zhi": fix_zhi,
    "toufa": fix_toufa,
    "variants": fix_variants,
    "quotes": fix_curly_quotes,
}
HEADING_RULE = "heading"
CLEAR_RULES = ("meta", "think", "fffd", "untranslated")
ALL_FIX = tuple(FIX_RULES) + (HEADING_RULE,)
ALL_RULES = ALL_FIX + CLEAR_RULES


def parse_rules(spec: str | None) -> set[str]:
    if not spec or spec == "all":
        return set(ALL_RULES)
    out: set[str] = set()
    for tok in spec.split(","):
        tok = tok.strip()
        if tok == "fixes":
            out |= set(ALL_FIX)
        elif tok == "clear":
            out |= set(CLEAR_RULES)
        elif tok in ALL_RULES:
            out.add(tok)
        elif tok:
            raise SystemExit(f"不認得的規則：{tok}（可用：{', '.join(ALL_RULES)}, fixes, clear）")
    return out


@dataclass
class SegResult:
    text: str                      # 修正後（清空時為 ""）
    hits: dict[str, int]           # 規則 → 命中數
    clear: str = ""                # 清空原因
    heading_unresolved: int = 0


def fix_segment(zh: str, src: str = "", *, rules: set[str] | None = None,
                scripture: bool = False, heading: bool = True) -> SegResult:
    """一段譯文跑全部規則。先判清空（清空就不必再修字），再依序套確定性修正。

    scripture=True：經文語料（東方聖書、諾斯底、次經、阿維斯陀…）不套數字規則。
    heading=False：這個語料的段落本來就不是 markdown（DB 表），跳過章名規則。
    """
    rules = set(ALL_RULES) if rules is None else rules
    hits: dict[str, int] = {}
    reason = clear_reason(zh, src)
    if reason and reason in rules:
        hits[reason] = 1
        return SegResult("", hits, clear=reason)
    t = zh or ""
    for name, fn in FIX_RULES.items():
        if name not in rules:
            continue
        if name == "numerals" and scripture:
            continue
        t, n = fn(t)
        if n:
            hits[name] = n
    unresolved = 0
    if heading and HEADING_RULE in rules:
        t2, n = split_glued_heading(t, src)
        if n and src:
            # 多語 reader 用「\n\n 段序」對齊原文。切章名會多出一段：原文那邊本來就是
            # 分開的（段數比譯文多）才切；原文也黏在一起就不切，免得把對齊弄歪。
            s_cnt, before, after = para_count(src), para_count(t), para_count(t2)
            if abs(s_cnt - after) > abs(s_cnt - before):
                t2, n = t, 0
        if n:
            t = t2
            hits[HEADING_RULE] = n
        unresolved = sum(1 for m in _HEAD_LINE.finditer(t)
                         if not _is_title_like(m.group(2).strip()))
    return SegResult(t, hits, clear="", heading_unresolved=unresolved)


# ═════════════════════════════════════════════════════════════════════════════
#  四、fleet lane 保護：正在被 lane 寫的書不碰
# ═════════════════════════════════════════════════════════════════════════════
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
RECENT_WRITE_SECS = 30 * 60


@dataclass
class Lane:
    name: str
    pid: int
    cmdline: str
    locked_ids: set[str] = field(default_factory=set)
    locked_slugs: set[str] = field(default_factory=set)


def _process_cmdlines() -> dict[int, str]:
    """pid → 命令列。Windows 走 CIM（wmic 已被移除），其他平台讀 /proc。"""
    out: dict[int, str] = {}
    if os.name == "nt":
        import subprocess
        ps = ("Get-CimInstance Win32_Process | ForEach-Object "
              "{ \"$($_.ProcessId)`t$($_.CommandLine)\" }")
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                               capture_output=True, timeout=60)
            text = r.stdout.decode("utf-8", errors="replace")
        except Exception:
            return out
        for line in text.splitlines():
            pid, _, cmd = line.partition("\t")
            if pid.strip().isdigit():
                out[int(pid)] = cmd.strip()
        return out
    for p in Path("/proc").glob("[0-9]*"):
        try:
            out[int(p.name)] = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", errors="replace")
        except OSError:
            pass
    return out


def _arg(cmd: str, flag: str) -> str | None:
    m = re.search(rf"{re.escape(flag)}[ =]+\"?([^\s\"]+)", cmd)
    return m.group(1) if m else None


def lane_locks_from_cmdline(cmd: str, scripts_dir: Path = SCRIPTS) -> tuple[set[str], set[str]]:
    """從一條 lane 的命令列推出它負責的書（ebook_id 集合、work slug 集合）。純函式
    （只讀 driver 原始碼），測試用假命令列即可。

    規則：
      - 命令列裡直接出現的 UUID。
      - `--work W`：driver 原始碼裡 `"W"` 那個 dict 區塊內的 UUID（panikkar_auto 的 WORKS）。
      - `--author A`（uchimura_auto）：AUTHOR_MODULES[A] 那支 registry 模組裡所有 UUID。
      - 兩者都沒有：driver 原始碼裡所有 UUID（保守）。
    """
    ids = {u.lower() for u in _UUID_RE.findall(cmd)}
    slugs: set[str] = set()
    m = re.search(r"scripts[\\/]([\w\-]+\.py)", cmd)
    if not m:
        return ids, slugs
    driver = scripts_dir / m.group(1)
    try:
        src = driver.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ids, slugs
    work = _arg(cmd, "--work")
    author = _arg(cmd, "--author")
    if work:
        slugs.add(work)
        k = src.find(f'"{work}"')
        if k >= 0:
            block = src[k:k + 1500]
            nxt = re.search(r'\n\s{0,8}"[\w\-]+":\s*\{', block[len(work) + 2:])
            if nxt:
                block = block[:len(work) + 2 + nxt.start()]
            ids |= {u.lower() for u in _UUID_RE.findall(block)}
    elif author:
        slugs.add(author)
        mm = re.search(rf'"{re.escape(author)}"\s*:\s*"([\w]+)"', src)
        mod = scripts_dir / f"{mm.group(1)}.py" if mm else None
        if mod and mod.exists():
            ids |= {u.lower() for u in _UUID_RE.findall(mod.read_text(encoding="utf-8", errors="replace"))}
        else:
            ids |= {u.lower() for u in _UUID_RE.findall(src)}
    else:
        ids |= {u.lower() for u in _UUID_RE.findall(src)}
    return ids, slugs


def live_lanes(state_dir: Path = STATE_DIR) -> list[Lane]:
    cmds = _process_cmdlines()
    lanes = []
    for pf in sorted(state_dir.glob("fleet_*.pid")):
        try:
            pid = int(pf.read_text(encoding="utf-8", errors="replace").strip() or 0)
        except ValueError:
            continue
        cmd = cmds.get(pid)
        if not cmd:
            continue  # 程序已死
        ids, slugs = lane_locks_from_cmdline(cmd)
        lanes.append(Lane(pf.stem.removeprefix("fleet_"), pid, cmd, ids, slugs))
    return lanes


def recently_written(path: Path, now: float | None = None,
                     window: float = RECENT_WRITE_SECS) -> bool:
    try:
        return ((now or time.time()) - path.stat().st_mtime) < window
    except OSError:
        return False


class LaneGuard:
    """apply 前問一句「這本現在能不能動」。"""

    def __init__(self, lanes: list[Lane] | None = None):
        self.lanes = live_lanes() if lanes is None else lanes
        self.ids = set().union(*(l.locked_ids for l in self.lanes)) if self.lanes else set()
        self.slugs = set().union(*(l.locked_slugs for l in self.lanes)) if self.lanes else set()

    def why_locked(self, item_id: str, path: Path | None = None, slug: str = "") -> str:
        if item_id.lower() in self.ids:
            owner = [l.name for l in self.lanes if item_id.lower() in l.locked_ids]
            return f"lane {','.join(owner)} 正在寫"
        if slug and slug in self.slugs:
            return f"lane 正在寫 {slug}"
        if path is not None and recently_written(path):
            return "30 分鐘內剛被寫過"
        return ""


# ═════════════════════════════════════════════════════════════════════════════
#  五、語料 adapter：讀、判、（apply 時）寫
# ═════════════════════════════════════════════════════════════════════════════
# 各語料「未譯」的表示法不同，清空一定要照它自己的表示法，否則 reader 會壞、
# 補譯流程也找不到（2026-09-25 逐一查過）：
#
#   語料         存放                                     清空＝                         補譯流程怎麼找到
#   fathers      Drive _chunks/{id}.jsonl content        整個 chunk 的 content 設回英文    fathers_retranslate_untranslated
#                                                                                         （判準：content 是英文散文）
#   books        Drive _chunks/{id}.jsonl content        段序對得上 → 該段換回原文段；    清單（translate_ebook_to_zh 的
#                （translate_ebook_to_zh、全集 JSONL）    對不上 → 整個 chunk 設回原文      resume 只看 title_en 在不在）
#   collected／  .claude/skills/ebook-collected-works/   zh[j]="" ；章名 title_zh=""；   driver 的 `not zh[j]`
#   sbe          *_data/<work>/sec{i}.json               sbe 另把 fail[j] 歸 0            （JSONL 由 driver 從 sec 重建，
#                                                                                         **直接改 JSONL 會被蓋掉**）
#   lit_review   DB lit_review_sections（version_code    DELETE 那一列 zh，               ingest_lit_review 的
#                ='zh' 一段一列）                        entry 狀態 translated→fetched     done_zh_indices（缺列＝未譯）
#   gnostic      DB gnostic_sections（version_code='zh'） text=''（**不可 DELETE**）      fix_gnostic_quality 的 "empty"
#   apocrypha    DB apocrypha_sections（version_code=    text=''                         無自動流程，看清單
#                'kgl_zh'，目前只有猶大福音）
#   sources      data/{avesta,hellenika,manichaean}/     segments[i].zh=""               avesta_translate／hellenika_* 的
#                sources/**/*.json                                                         `not zh`
#   accs         DB accs_commentary.body_zh              不清（沒有原文可退回），只列清單   —
#
# reader 那一側：JSONL 的段若設成空字串，兩個 reader 都會把空段吃掉、後面整欄錯位
# （lib/ebook-render.ts、collected-works/[work].vue 的 filter(Boolean)），所以 JSONL
# 一律「換回原文」而不是清成空字串；DB 與 data 的空欄 reader 顯示「—」或「待譯」。

SCRIPTURE_CORPORA = {"sbe", "gnostic", "apocrypha", "sources"}
CORPORA = ("fathers", "books", "collected", "sbe", "lit_review", "gnostic",
           "apocrypha", "accs", "sources")
CW_DATA = ROOT / ".claude" / "skills" / "ebook-collected-works"
DATA_SOURCES = [ROOT / "data" / d / "sources" for d in ("avesta", "hellenika", "manichaean")]
# 這些 driver 從 sec*.json 重建 JSONL：它們的 ebook_id 不可走 books（會被下一輪重建蓋掉）
SEC_DRIVER_MODULES = ("panikkar_auto", "sbe_translate", "mueller_auto", "uchimura_build",
                      "yanaihara_build", "uchimura_en_build", "howes_build", "husserl_build",
                      "sekine_build", "uchimura_zenshu_works", "azegami_build", "kagawa_build",
                      "ndl_build")
EXCERPT = 120


def _load_env() -> dict:
    env = dict(os.environ)
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


class Rest:
    """PostgREST 小包裝。🚨 一律帶 limit 並用 keyset 分頁（id=gt.X）——沒帶 limit
    會靜默截在 1000 筆（記憶檔 feedback_postgrest_silent_1000_cap）。"""

    PAGE = 1000

    def __init__(self):
        import requests
        self.rq = requests
        env = _load_env()
        self.url = env["SUPABASE_URL"].rstrip("/") + "/rest/v1"
        key = env["SUPABASE_SERVICE_ROLE_KEY"]
        self.h = {"apikey": key, "Authorization": f"Bearer {key}",
                  "Content-Type": "application/json"}

    def _get(self, path: str, params: str):
        for attempt in range(4):
            try:
                r = self.rq.get(f"{self.url}/{path}?{params}", headers=self.h, timeout=120)
                if r.status_code >= 500 and attempt < 3:
                    time.sleep(3 * (attempt + 1))
                    continue
                r.raise_for_status()
                return r.json()
            except self.rq.RequestException:
                if attempt == 3:
                    raise
                time.sleep(3 * (attempt + 1))

    def paged(self, table: str, select: str, filt: str = "", start="0") -> Iterator[dict]:
        last = start  # uuid 主鍵的表傳 "00000000-0000-0000-0000-000000000000"
        while True:
            q = f"select={select}&order=id.asc&limit={self.PAGE}&id=gt.{last}"
            if filt:
                q += "&" + filt
            rows = self._get(table, q)
            yield from rows
            if len(rows) < self.PAGE:
                return
            last = rows[-1]["id"]

    def patch(self, table: str, filt: str, body: dict) -> None:
        r = self.rq.patch(f"{self.url}/{table}?{filt}", headers={**self.h, "Prefer": "return=minimal"},
                          data=json.dumps(body), timeout=60)
        r.raise_for_status()

    def delete(self, table: str, filt: str) -> None:
        r = self.rq.delete(f"{self.url}/{table}?{filt}", headers={**self.h, "Prefer": "return=minimal"},
                           timeout=60)
        r.raise_for_status()


# ── 統計與清空清單 ───────────────────────────────────────────────────────────
@dataclass
class CorpusStats:
    corpus: str
    items: int = 0                 # 書／作品／文件數
    segments: int = 0              # 分母：段數（有譯文的段）
    rule_segments: collections.Counter = field(default_factory=collections.Counter)
    rule_hits: collections.Counter = field(default_factory=collections.Counter)
    clear: collections.Counter = field(default_factory=collections.Counter)
    pending_untranslated: int = 0  # 已經是「未譯」表示法（內容＝原文），不必寫、但列入清單
    heading_unresolved: int = 0
    locked: list = field(default_factory=list)
    changed_items: int = 0
    changed_segments: int = 0
    notes: list = field(default_factory=list)

    def add(self, res: "SegResult") -> None:
        for k, v in res.hits.items():
            if k in CLEAR_RULES:
                continue
            self.rule_segments[k] += 1
            self.rule_hits[k] += v
        if res.clear:
            self.clear[res.clear] += 1
        self.heading_unresolved += res.heading_unresolved

    def to_dict(self) -> dict:
        return {
            "corpus": self.corpus, "items": self.items, "segments": self.segments,
            "rule_segments": dict(self.rule_segments), "rule_hits": dict(self.rule_hits),
            "clear": dict(self.clear), "clear_total": sum(self.clear.values()),
            "pending_untranslated": self.pending_untranslated,
            "heading_unresolved": self.heading_unresolved,
            "locked": self.locked, "changed_items": self.changed_items,
            "changed_segments": self.changed_segments, "notes": self.notes,
        }


class ClearSink:
    """清空清單：一段一行 JSONL，給補譯 agent 用。"""

    def __init__(self, path: Path | None):
        self.path = path
        self.fh = None
        self.count = collections.Counter()
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.fh = path.open("w", encoding="utf-8")

    def emit(self, corpus: str, reason: str, loc: dict, zh: str, src: str,
             action: str) -> None:
        self.count[corpus] += 1
        if self.fh:
            self.fh.write(json.dumps({
                "corpus": corpus, "reason": reason, "action": action, **loc,
                "zh_excerpt": (zh or "")[:EXCERPT], "src_excerpt": (src or "")[:EXCERPT],
            }, ensure_ascii=False) + "\n")

    def close(self):
        if self.fh:
            self.fh.close()


class SampleSink:
    """每語料每規則留幾筆改前／改後，給人抽查（誤改最怕的是看不到）。"""

    def __init__(self, path: Path | None, per_rule: int = 8):
        self.path, self.per_rule = path, per_rule
        self.seen = collections.Counter()
        self.rows: list[dict] = []

    def offer(self, corpus: str, loc: dict, before: str, res: "SegResult") -> None:
        for rule in res.hits:
            if rule in CLEAR_RULES:
                continue
            k = (corpus, rule)
            if self.seen[k] >= self.per_rule:
                continue
            self.seen[k] += 1
            i = _first_diff(before, res.text)
            self.rows.append({"corpus": corpus, "rule": rule, **loc,
                              "before": before[max(0, i - 30):i + 60],
                              "after": res.text[max(0, i - 30):i + 60]})

    def close(self):
        if self.path and self.rows:
            self.path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in self.rows) + "\n",
                                 encoding="utf-8")


def _first_diff(a: str, b: str) -> int:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


@dataclass
class RunCtx:
    rules: set
    apply: bool
    dry_run: bool
    guard: "LaneGuard | None"
    sink: ClearSink
    samples: SampleSink
    fffd_mode: str = "clear"
    push: bool = True
    rebuild: bool = False
    limit: int | None = None


def _run_segment(ctx: RunCtx, corpus: str, zh: str, src: str, *, heading: bool) -> SegResult:
    rules = set(ctx.rules)
    if ctx.fffd_mode == "strip":
        rules.discard("fffd")
    res = fix_segment(zh, src, rules=rules, scripture=corpus in SCRIPTURE_CORPORA,
                      heading=heading)
    if ctx.fffd_mode == "strip" and not res.clear and "\ufffd" in res.text:
        stripped = strip_fffd(res.text)
        if stripped is None:           # 剝不乾淨（連續或落在結尾）→ 還是清空
            res = SegResult("", {"fffd": 1}, clear="fffd")
        else:
            res.hits["fffd_strip"] = res.text.count("\ufffd")
            res.text = stripped
    return res


def strip_fffd(text: str) -> str | None:
    """U+FFFD 是模型 byte-fallback 多插進來的字元，後面那個字是完整的（「\ufffd請」）。
    每一個 U+FFFD 後面都緊接一個非空白、非 U+FFFD 的字時才能安全剝掉；否則回 None。"""
    for m in re.finditer("\ufffd", text):
        nxt = text[m.end():m.end() + 1]
        if not nxt or nxt.isspace() or nxt == "\ufffd":
            return None
    return text.replace("\ufffd", "")


# ── JSONL（fathers／books）───────────────────────────────────────────────────
_PARA_SPLIT = re.compile(r"\n[ \t]*\n")


def chunk_source(ch: dict) -> str:
    srcs = ch.get("sources") or {}
    order = ch.get("source_order") or list(srcs)
    for k in (["en"] + list(order)):
        v = srcs.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ch.get("source_text") or ""


def process_chunk(ctx: RunCtx, corpus: str, ch: dict, loc: dict,
                  st: CorpusStats, *, chunk_level_clear: bool,
                  allow_clear: bool = True) -> tuple[dict, bool]:
    """回傳 (新 chunk, 有沒有改)。純邏輯（不碰檔案），測試直接餵 dict。"""
    content = ch.get("content") or ""
    src = chunk_source(ch)
    if not content.strip():
        return ch, False
    zparas = content.split("\n\n")
    sparas = src.split("\n\n") if src else []
    aligned = bool(src) and len(zparas) == len(sparas)
    new_paras: list[str] = []
    changed = False
    clear_chunk = ""
    for j, p in enumerate(zparas):
        if not p.strip():
            new_paras.append(p)
            continue
        st.segments += 1
        sp = sparas[j] if aligned else ""
        res = _run_segment(ctx, corpus, p, sp, heading=False)
        if res.clear:
            if not allow_clear:
                ctx.sink.emit(corpus, res.clear, {**loc, "para": j}, p, sp, "report-only")
                st.clear[res.clear] += 1
                new_paras.append(p)
                continue
            already = src and (p.strip() == sp.strip() or p.strip() in src)
            if already:
                st.pending_untranslated += 1
                ctx.sink.emit(corpus, res.clear, {**loc, "para": j}, p, sp, "already-source")
                new_paras.append(p)
                continue
            st.add(res)
            if not src:
                ctx.sink.emit(corpus, res.clear, {**loc, "para": j}, p, "", "no-source-kept")
                new_paras.append(p)
                continue
            if chunk_level_clear or not aligned:
                clear_chunk = clear_chunk or res.clear
                ctx.sink.emit(corpus, res.clear, {**loc, "para": j}, p, sp or src[:EXCERPT],
                              "chunk-to-source")
                new_paras.append(p)
                continue
            ctx.sink.emit(corpus, res.clear, {**loc, "para": j}, p, sp, "para-to-source")
            new_paras.append(sp)
            changed = True
            st.changed_segments += 1
            continue
        st.add(res)
        if res.text != p:
            ctx.samples.offer(corpus, {**loc, "para": j}, p, res)
            changed = True
            st.changed_segments += 1
        new_paras.append(res.text)
    new_content = "\n\n".join(new_paras)
    if clear_chunk:
        new_content = src
        changed = True
    elif HEADING_RULE in ctx.rules:
        fixed, n = split_glued_heading(new_content, src)
        if n and src:
            s_cnt, before, after = para_count(src), para_count(new_content), para_count(fixed)
            if abs(s_cnt - after) > abs(s_cnt - before):
                fixed, n = new_content, 0
        if n:
            st.rule_segments[HEADING_RULE] += 1
            st.rule_hits[HEADING_RULE] += n
            ctx.samples.offer(corpus, loc, new_content, SegResult(fixed, {HEADING_RULE: n}))
            new_content = fixed
            changed = True
        st.heading_unresolved += sum(
            1 for m in _HEAD_LINE.finditer(new_content) if not _is_title_like(m.group(2).strip()))
    if not changed or new_content == content:
        return ch, False
    out = dict(ch)
    out["content"] = new_content
    return out, True


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl_atomic(path: Path, rows: list[dict]) -> None:
    bak = path.with_suffix(".jsonl.tfix.bak")
    if not bak.exists():
        bak.write_bytes(path.read_bytes())
    tmp = path.with_suffix(".jsonl.tfix.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def sec_backed_ids() -> set[str]:
    ids: set[str] = set()
    for mod in SEC_DRIVER_MODULES:
        p = SCRIPTS / f"{mod}.py"
        if p.exists():
            ids |= {u.lower() for u in _UUID_RE.findall(p.read_text(encoding="utf-8", errors="replace"))}
    return ids


def fathers_ids(rest: "Rest") -> dict[str, str]:
    """教父＝ebooks.subcategory 含 Schaff 或 ACCS（pages/fathers/index.vue 同一條）。
    回傳 id → 'schaff' | 'accs'。ACCS 是出版社中文 OCR，不是機翻：只修字、不清空。"""
    out = {}
    for row in rest.paged("ebooks", "id,subcategory",
                          "or=(subcategory.ilike.*Schaff*,subcategory.ilike.*ACCS*)",
                          start="00000000-0000-0000-0000-000000000000"):
        out[row["id"].lower()] = "accs" if "ACCS" in (row.get("subcategory") or "") else "schaff"
    return out


def translated_book_ids(exclude: set[str], limit: int | None = None) -> list[Path]:
    """_chunks 裡「有原文欄」的書（translate_ebook_to_zh 與全集 JSONL）。只讀每本前幾行判斷。"""
    out = []
    files = sorted(CHUNKS_DIR.glob("*.jsonl"))
    if not files:
        raise SystemExit(f"⛔ {CHUNKS_DIR} 一個 .jsonl 都沒有——G: 沒掛？先 Test-Path 'G:\\我的雲端硬碟'")
    for f in files:
        if f.stem.lower() in exclude:
            continue
        try:
            with f.open(encoding="utf-8") as fh:
                for _ in range(6):
                    line = fh.readline()
                    if not line:
                        break
                    if '"source_text"' in line or '"sources"' in line:
                        out.append(f)
                        break
        except (OSError, UnicodeDecodeError):
            continue
        if limit and len(out) >= limit:
            break
    return out


def process_jsonl_corpus(ctx: RunCtx, corpus: str, paths: list[Path], st: CorpusStats,
                         kinds: dict[str, str] | None = None) -> None:
    for path in paths:
        eid = path.stem
        kind = (kinds or {}).get(eid.lower(), "")
        why = ctx.guard.why_locked(eid, path) if (ctx.apply and ctx.guard) else ""
        if why:
            st.locked.append({"id": eid, "why": why})
            continue
        try:
            rows = read_jsonl(path)
        except (OSError, ValueError) as e:
            st.notes.append(f"{eid}: 讀不動 {e.__class__.__name__}")
            continue
        st.items += 1
        new_rows, dirty = [], False
        for line_no, ch in enumerate(rows):
            loc = {"id": eid, "line": line_no, "chunk_index": ch.get("chunk_index"),
                   "chapter_path": (ch.get("chapter_path") or "")[:60]}
            nch, chg = process_chunk(ctx, corpus, ch, loc, st,
                                     chunk_level_clear=(corpus == "fathers"),
                                     allow_clear=(kind != "accs"))
            new_rows.append(nch)
            dirty |= chg
        if dirty:
            st.changed_items += 1
            if ctx.apply and not ctx.dry_run:
                write_jsonl_atomic(path, new_rows)
                if ctx.push:
                    _push_book(eid, path, new_rows)


def _push_book(eid: str, path: Path, rows: list[dict]) -> None:
    """照 repo 既有做法：R2 走 standardize_ebook.push_to_r2（gzip 整本覆寫），
    DB 只 PATCH ebooks.total_chars（ebook_chunks preview 表 2026-09-16 已退場）。"""
    sys.path.insert(0, str(SCRIPTS))
    import standardize_ebook as se
    se.push_to_r2(eid, path)
    Rest().patch("ebooks", f"id=eq.{eid}", {"total_chars": sum(len(r.get("content") or "") for r in rows)})


# ── sec*.json（全集／東方聖書）────────────────────────────────────────────────
def sec_work_dirs(corpus: str) -> list[Path]:
    out = []
    for d in sorted(CW_DATA.glob("*_data")):
        for w in sorted(p for p in d.iterdir() if p.is_dir()):
            if not any(w.glob("sec*.json")):
                continue
            is_sbe = d.name == "mueller_data" and w.name.startswith("sbe-")
            if (corpus == "sbe") == is_sbe:
                out.append(w)
    return out


def _sec_sort_key(p: Path) -> int:
    m = re.search(r"(\d+)", p.stem)
    return int(m.group(1)) if m else 0


def process_sec_file(ctx: RunCtx, corpus: str, data: dict, loc: dict,
                     st: CorpusStats) -> bool:
    """改 sec dict（就地）。回傳有沒有改。純邏輯，測試直接餵 dict。"""
    zh = data.get("zh") or []
    src = data.get("src") or data.get("en") or []
    engines = data.get("engines") or []
    fail = data.get("fail")
    changed = False
    for j, z in enumerate(zh):
        if not isinstance(z, str) or not z.strip():
            continue
        if j < len(engines) and engines[j] == "blank-unusable-source":
            continue
        st.segments += 1
        s = src[j] if j < len(src) and isinstance(src[j], str) else ""
        res = _run_segment(ctx, corpus, z, s, heading=False)
        st.add(res)
        if res.clear:
            ctx.sink.emit(corpus, res.clear, {**loc, "idx": j}, z, s, "sec-zh-empty")
            zh[j] = ""
            if isinstance(fail, list) and j < len(fail):
                fail[j] = 0      # mueller_auto 只重譯 fail[j] < MAX_FAIL 的段
            changed = True
            st.changed_segments += 1
        elif res.text != z:
            ctx.samples.offer(corpus, {**loc, "idx": j}, z, res)
            zh[j] = res.text
            changed = True
            st.changed_segments += 1
    for tkey, hkey in (("title_zh", "heading"), ("title_zh", "title")):
        t = data.get(tkey)
        if not isinstance(t, str) or not t.strip():
            continue
        h = data.get(hkey) or ""
        st.segments += 1
        res = _run_segment(ctx, corpus, t, h, heading=False)
        st.add(res)
        if res.clear:
            ctx.sink.emit(corpus, res.clear, {**loc, "field": tkey}, t, h, "sec-title-empty")
            data[tkey] = ""      # driver：`cache.get("title_zh") or None` → 重譯章名
            changed = True
            st.changed_segments += 1
        elif res.text != t:
            ctx.samples.offer(corpus, {**loc, "field": tkey}, t, res)
            data[tkey] = res.text
            changed = True
            st.changed_segments += 1
        break
    if changed:
        data["zh"] = zh
    return changed


def process_sec_corpus(ctx: RunCtx, corpus: str, st: CorpusStats, ids: list[str] | None) -> None:
    for wdir in sec_work_dirs(corpus):
        wid = f"{wdir.parent.name}/{wdir.name}"
        if ids and wdir.name not in ids and wid not in ids:
            continue
        if ctx.apply and ctx.guard:
            why = ctx.guard.why_locked(wdir.name, None, slug=wdir.name) or _sec_dir_locked(ctx.guard, wdir)
            if why:
                st.locked.append({"id": wid, "why": why})
                continue
        st.items += 1
        work_changed = False
        for sf in sorted(wdir.glob("sec*.json"), key=_sec_sort_key):
            try:
                raw = sf.read_text(encoding="utf-8")
                data = json.loads(raw)
            except (OSError, ValueError):
                st.notes.append(f"{wid}/{sf.name}: 讀不動")
                continue
            if not isinstance(data, dict):
                continue
            loc = {"id": wid, "file": sf.name}
            if process_sec_file(ctx, corpus, data, loc, st):
                work_changed = True
                if ctx.apply and not ctx.dry_run:
                    _write_json_like(sf, raw, data)
        if work_changed:
            st.changed_items += 1
            if ctx.apply:
                cmd = rebuild_command(wdir)
                msg = f"{wid}: sec 已改，重建並上傳 → {cmd or '（找不到 driver，手動重建）'}"
                st.notes.append(msg)
                if ctx.rebuild and cmd and not ctx.dry_run:
                    import subprocess
                    subprocess.run(cmd, cwd=str(ROOT), shell=True, check=False)


def _sec_dir_locked(guard: "LaneGuard", wdir: Path) -> str:
    dirkey = f"dir:{wdir.parent.name}"
    if dirkey in guard.slugs:
        return f"lane 正在寫 {wdir.parent.name}"
    newest = max((p.stat().st_mtime for p in wdir.glob("sec*.json")), default=0)
    if time.time() - newest < RECENT_WRITE_SECS:
        return "30 分鐘內剛被寫過"
    return ""


def rebuild_command(wdir: Path) -> str:
    """sec 改完後重建 JSONL＋推 R2 的指令（各 driver 自己的入口）。"""
    py = r"C:\Users\user\AppData\Local\Python\bin\python.exe -X utf8"
    data_dir, work = wdir.parent.name, wdir.name
    if data_dir == "panikkar_data":
        return f'{py} -c "import sys; sys.path.insert(0,\'scripts\'); import panikkar_auto as p; p.build_and_upload(\'{work}\', do_upload=True)"'
    if data_dir == "mueller_data":
        mod = "sbe_translate" if work.startswith("sbe-") else "mueller_auto"
        return (f'{py} -c "import sys; sys.path.insert(0,\'scripts\'); import mueller_auto as m, {mod} as d; '
                f'w=[x for x in d.WORKS if x[\'slug\']==\'{work}\'][0]; m.assemble_and_upload(w)"')
    ua = (SCRIPTS / "uchimura_auto.py").read_text(encoding="utf-8", errors="replace")
    authors = dict(re.findall(r'"([\w\-]+)"\s*:\s*"(\w+)"', ua[ua.find("AUTHOR_MODULES"):ua.find("AUTHOR_MODULES") + 800]))
    for author, mod in authors.items():
        p = SCRIPTS / f"{mod}.py"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'DATA_DIRNAME\s*=\s*"(\w+)"', text)
        ddir = m.group(1) if m else "uchimura_data"
        if ddir == data_dir and f'"{work}"' in text:
            return f"{py} scripts/uchimura_auto.py --author {author} --work {work} --build-only --upload"
    return ""


def _write_json_like(path: Path, raw: str, data) -> None:
    """照原檔的縮排與結尾換行寫回，免得整檔 diff。"""
    indent = None
    m = re.match(r"[\[{]\r?\n([ \t]+)", raw)
    if m:
        indent = len(m.group(1))
    text = json.dumps(data, ensure_ascii=False, indent=indent)
    if raw.endswith("\n"):
        text += "\n"
    tmp = path.with_suffix(path.suffix + ".tfix.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


# ── data/*/sources（avesta／hellenika／manichaean）────────────────────────────
def process_sources_corpus(ctx: RunCtx, st: CorpusStats, ids: list[str] | None) -> None:
    for root in DATA_SOURCES:
        for f in sorted(root.rglob("*.json")):
            if ids and f.stem not in ids:
                continue
            try:
                raw = f.read_text(encoding="utf-8")
                data = json.loads(raw)
            except (OSError, ValueError):
                continue
            segs = data.get("segments") if isinstance(data, dict) else None
            if not isinstance(segs, list) or not any(isinstance(s, dict) and "zh" in s for s in segs):
                continue
            st.items += 1
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            changed = False
            for i, s in enumerate(segs):
                z = s.get("zh") if isinstance(s, dict) else None
                if not isinstance(z, str) or not z.strip():
                    continue
                st.segments += 1
                src = s.get("en") or s.get("greek") or s.get("orig") or ""
                res = _run_segment(ctx, "sources", z, src, heading=False)
                st.add(res)
                loc = {"id": rel, "idx": i, "ref": s.get("ref") or s.get("line_from")}
                if res.clear:
                    ctx.sink.emit("sources", res.clear, loc, z, src, "zh-empty")
                    s["zh"] = ""
                    changed = True
                    st.changed_segments += 1
                elif res.text != z:
                    ctx.samples.offer("sources", loc, z, res)
                    s["zh"] = res.text
                    changed = True
                    st.changed_segments += 1
            if changed:
                st.changed_items += 1
                if ctx.apply and not ctx.dry_run:
                    _write_json_like(f, raw, data)
    if ctx.apply and st.changed_items and not ctx.dry_run:
        st.notes.append("data/*/sources 是打包進站的：改完要 git commit＋部署才會上線")


# ── DB：lit_review／gnostic／apocrypha／accs ───────────────────────────────────
def _db_lock_reason(patterns: tuple[str, ...], lockfiles: tuple[str, ...] = ()) -> str:
    cmds = _process_cmdlines()
    for pid, cmd in cmds.items():
        if pid == os.getpid():
            continue
        if any(p in cmd for p in patterns) and "translation_fix" not in cmd:
            return f"程序 {pid} 正在跑（{cmd[:80]}）"
    for lf in lockfiles:
        p = Path(lf)
        try:
            pid = int(p.read_text().strip())
        except (OSError, ValueError):
            continue
        if pid in cmds:
            return f"鎖檔 {lf} 的程序 {pid} 還活著"
    return ""


def process_db_pairs(ctx: RunCtx, corpus: str, st: CorpusStats, *, table: str,
                     group: str, zh_code: str, src_codes: tuple[str, ...],
                     ids: list[str] | None, lock_patterns: tuple[str, ...],
                     lock_files: tuple[str, ...] = (), clear_mode: str) -> None:
    """一段一列、以 (group, order_index) 配對原文與譯文的表。"""
    if ctx.apply and ctx.guard:
        why = _db_lock_reason(lock_patterns, lock_files)
        if why:
            st.locked.append({"id": table, "why": why})
            return
    rest = Rest()
    codes = (zh_code,) + src_codes
    filt = f"version_code=in.({','.join(codes)})"
    if ids:
        filt += f"&{group}=in.({','.join(ids)})"
    zh_rows: list[dict] = []
    src_map: dict[tuple, str] = {}
    for r in rest.paged(table, f"id,{group},version_code,order_index,text", filt):
        key = (r[group], r["order_index"])
        if r["version_code"] == zh_code:
            zh_rows.append(r)
        elif key not in src_map:
            src_map[key] = r.get("text") or ""
    groups = {r[group] for r in zh_rows}
    st.items = len(groups)
    touched_groups: set = set()
    for n, r in enumerate(zh_rows):
        if ctx.limit and n >= ctx.limit:
            break
        z = r.get("text") or ""
        if not z.strip():
            continue
        st.segments += 1
        src = src_map.get((r[group], r["order_index"]), "")
        res = _run_segment(ctx, corpus, z, src, heading=False)
        st.add(res)
        loc = {"id": r[group], "row_id": r["id"], "order_index": r["order_index"]}
        if res.clear:
            ctx.sink.emit(corpus, res.clear, loc, z, src, clear_mode)
            st.changed_segments += 1
            touched_groups.add(r[group])
            if ctx.apply and not ctx.dry_run:
                if clear_mode == "delete-row":
                    rest.delete(table, f"id=eq.{r['id']}")
                else:
                    rest.patch(table, f"id=eq.{r['id']}", {"text": "", "char_count": 0})
        elif res.text != z:
            ctx.samples.offer(corpus, loc, z, res)
            st.changed_segments += 1
            touched_groups.add(r[group])
            if ctx.apply and not ctx.dry_run:
                rest.patch(table, f"id=eq.{r['id']}", {"text": res.text, "char_count": len(res.text)})
    st.changed_items = len(touched_groups)
    if corpus == "lit_review" and ctx.apply and not ctx.dry_run:
        cleared_entries = {e for e in touched_groups}
        for eid in cleared_entries:
            # 整篇已標 translated 的，--resume 會整篇跳過；刪了 zh 列要改回 fetched 才會補譯
            rest.patch("lit_review_entries", f"id=eq.{eid}&fulltext_status=eq.translated",
                       {"fulltext_status": "fetched"})


def process_accs(ctx: RunCtx, st: CorpusStats, ids: list[str] | None) -> None:
    """accs_commentary.body_zh：沒有英文欄，清空會讓 reader 整格空白，所以**只修字、
    清空類只列清單**。"""
    rest = Rest()
    filt = f"id=in.({','.join(ids)})" if ids else ""
    books = set()
    for n, r in enumerate(rest.paged("accs_commentary", "id,book_code,body_zh", filt,
                                          start="00000000-0000-0000-0000-000000000000")):
        if ctx.limit and n >= ctx.limit:
            break
        z = r.get("body_zh") or ""
        if not z.strip():
            continue
        books.add(r.get("book_code"))
        st.segments += 1
        res = _run_segment(ctx, "accs", z, "", heading=True)
        loc = {"id": r["id"], "book": r.get("book_code")}
        if res.clear:
            st.clear[res.clear] += 1
            ctx.sink.emit("accs", res.clear, loc, z, "", "report-only")
            continue
        st.add(res)
        if res.text != z:
            ctx.samples.offer("accs", loc, z, res)
            st.changed_segments += 1
            if ctx.apply and not ctx.dry_run:
                rest.patch("accs_commentary", f"id=eq.{r['id']}", {"body_zh": res.text})
    st.items = len(books)


# ═════════════════════════════════════════════════════════════════════════════
#  六、CLI
# ═════════════════════════════════════════════════════════════════════════════
def run_corpus(ctx: RunCtx, corpus: str, ids: list[str] | None) -> CorpusStats:
    st = CorpusStats(corpus)
    t0 = time.time()
    if corpus in ("fathers", "books"):
        rest = Rest()
        kinds = fathers_ids(rest)
        if corpus == "fathers":
            want = set(i.lower() for i in ids) if ids else set(kinds)
            paths = [CHUNKS_DIR / f"{i}.jsonl" for i in sorted(want) if (CHUNKS_DIR / f"{i}.jsonl").exists()]
            st.notes.append(f"教父書目 {len(kinds)} 本（Schaff {sum(1 for v in kinds.values() if v == 'schaff')}"
                            f"／ACCS {sum(1 for v in kinds.values() if v == 'accs')}），有 JSONL 的 {len(paths)} 本")
            process_jsonl_corpus(ctx, corpus, paths, st, kinds)
        else:
            exclude = set(kinds) | sec_backed_ids()
            if ids:
                paths = [CHUNKS_DIR / f"{i}.jsonl" for i in ids if (CHUNKS_DIR / f"{i}.jsonl").exists()]
            else:
                paths = translated_book_ids(exclude, ctx.limit)
            st.notes.append(f"有原文欄的譯本 {len(paths)} 本（已排除教父與 sec 重建的全集／東方聖書）")
            process_jsonl_corpus(ctx, corpus, paths, st)
    elif corpus in ("collected", "sbe"):
        process_sec_corpus(ctx, corpus, st, ids)
    elif corpus == "lit_review":
        process_db_pairs(ctx, corpus, st, table="lit_review_sections", group="entry_id",
                         zh_code="zh", src_codes=("orig",), ids=ids,
                         lock_patterns=("ingest_lit_review", "lit_review_quality_reviewer"),
                         clear_mode="delete-row")
    elif corpus == "gnostic":
        process_db_pairs(ctx, corpus, st, table="gnostic_sections", group="doc_slug",
                         zh_code="zh", src_codes=("gnosis_en",), ids=ids,
                         lock_patterns=("ingest_gnostic", "fix_gnostic_quality"),
                         lock_files=(r"c:\tmp\gnostic_loop.lock",), clear_mode="text-empty")
    elif corpus == "apocrypha":
        process_db_pairs(ctx, corpus, st, table="apocrypha_sections", group="doc_slug",
                         zh_code="kgl_zh", src_codes=("gospelsnet_en",), ids=ids,
                         lock_patterns=("ingest_gospel_of_judas",), clear_mode="text-empty")
    elif corpus == "accs":
        process_accs(ctx, st, ids)
    elif corpus == "sources":
        process_sources_corpus(ctx, st, ids)
    else:
        raise SystemExit(f"不認得的語料：{corpus}（可用：{', '.join(CORPORA)}, all）")
    st.notes.append(f"耗時 {time.time() - t0:.0f} 秒")
    return st


def render_report(stats: list[CorpusStats], *, mode: str, rules: set[str]) -> str:
    cols = [r for r in ALL_FIX if r in rules] + [c for c in CLEAR_RULES if c in rules]
    extra = ["fffd_strip"] if any(s.rule_segments.get("fffd_strip") for s in stats) else []
    lines = [f"# 譯文修正 {mode}（{_dt.datetime.now():%Y-%m-%d %H:%M}）", "",
             "每格＝命中段數／分母段數（括號內是命中處數）。清空欄是要清空重譯的段數。", ""]
    head = ["語料", "件數", "分母段數"] + cols + extra + ["清空合計", "已是原文", "章名判不出"]
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "---|" * len(head))
    for s in stats:
        row = [s.corpus, f"{s.items:,}", f"{s.segments:,}"]
        for c in cols + extra:
            if c in CLEAR_RULES:
                row.append(f"{s.clear.get(c, 0):,}")
            else:
                row.append(f"{s.rule_segments.get(c, 0):,}（{s.rule_hits.get(c, 0):,}）")
        row += [f"{sum(s.clear.values()):,}", f"{s.pending_untranslated:,}", f"{s.heading_unresolved:,}"]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    for s in stats:
        if s.locked or s.notes:
            lines.append(f"## {s.corpus}")
            for n in s.notes:
                lines.append(f"- {n}")
            if s.locked:
                lines.append(f"- 跳過（lane 保護）{len(s.locked)} 件：" +
                             "、".join(f"{x['id']}（{x['why']}）" for x in s.locked[:20]))
            lines.append("")
    return "\n".join(lines)


def cmd_scan_apply(args, apply: bool) -> int:
    rules = parse_rules(args.rules)
    corpora = list(CORPORA) if args.corpus == "all" else args.corpus.split(",")
    if apply and args.corpus == "all":
        raise SystemExit("apply 一次只准一個語料（--corpus X），而且要帶 --ids")
    if apply and not args.ids:
        raise SystemExit("apply 必須指定 --ids（整語料一次改完風險太大；先 scan 看清單）")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M")
    tag = "scan" if not apply else ("dryrun" if args.dry_run else "apply")
    base = f"{tag}-{stamp}-{'all' if args.corpus == 'all' else args.corpus.replace(',', '+')}"
    sink = ClearSink(OUT_DIR / f"{base}.clear.jsonl")
    samples = SampleSink(OUT_DIR / f"{base}.samples.jsonl")
    guard = LaneGuard() if apply else None
    if guard and guard.lanes:
        print(f"lane 保護：{len(guard.lanes)} 條 lane 活著，鎖住 {len(guard.ids)} 個 ebook_id、"
              f"{len(guard.slugs)} 個 slug", flush=True)
    ctx = RunCtx(rules=rules, apply=apply, dry_run=args.dry_run if apply else True,
                 guard=guard, sink=sink, samples=samples, fffd_mode=args.fffd_mode,
                 push=not args.no_push, rebuild=args.rebuild, limit=args.limit)
    stats = []
    for c in corpora:
        print(f"== {c} …", flush=True)
        try:
            st = run_corpus(ctx, c, args.ids)
        except SystemExit:
            raise
        except Exception as e:  # 一個語料壞了不要拖垮整輪，但要大聲說
            st = CorpusStats(c)
            st.notes.append(f"⛔ 失敗：{e.__class__.__name__}: {e}")
        stats.append(st)
        print(f"   {c}: 件數 {st.items:,}　分母 {st.segments:,} 段　清空 {sum(st.clear.values()):,}　"
              f"修正段 {sum(v for k, v in st.rule_segments.items()):,}　"
              f"{'（' + st.notes[-1] + '）' if st.notes else ''}", flush=True)
        if st.segments == 0:
            print(f"   ⚠ {c} 分母是 0——迴圈可能沒跑到（G: 沒掛？查錯表？），不要當成「沒問題」", flush=True)
    sink.close()
    samples.close()
    report = render_report(stats, mode=tag, rules=rules)
    (OUT_DIR / f"{base}.md").write_text(report, encoding="utf-8")
    (OUT_DIR / f"{base}.json").write_text(json.dumps([s.to_dict() for s in stats], ensure_ascii=False,
                                                     indent=1), encoding="utf-8")
    print()
    print(report)
    print(f"\n報告 → {OUT_DIR / (base + '.md')}")
    print(f"清空清單 → {sink.path}（{sum(sink.count.values()):,} 段）")
    return 0


def cmd_lanes(_args) -> int:
    lanes = live_lanes()
    print(f"活著的 fleet lane：{len(lanes)} 條")
    for l in lanes:
        print(f"  {l.name:22} pid {l.pid:>6}  鎖 {len(l.locked_ids)} 本  {sorted(l.locked_slugs)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--corpus", required=True, help=f"{', '.join(CORPORA)}；scan 可用 all 或逗號分隔")
        p.add_argument("--ids", nargs="*", default=None,
                       help="ebook_id／work slug／entry_id／doc_slug／檔名（依語料）")
        p.add_argument("--rules", default="all", help="all | fixes | clear | 逗號分隔的規則名")
        p.add_argument("--fffd-mode", choices=("clear", "strip"), default="clear",
                       help="U+FFFD：clear＝清空重譯（使用者 09-25 決定）；strip＝只剝掉那個字元"
                            "（查證後發現後面的字是完整的，剝掉即無損，見 SKILL.md）")
        p.add_argument("--limit", type=int, default=None, help="只處理前 N 件／列（抽樣）")
        p.add_argument("--dry-run", action="store_true", help="apply 時只算不寫")
        p.add_argument("--no-push", action="store_true", help="apply 寫 JSONL 後不推 R2／不 PATCH DB")
        p.add_argument("--rebuild", action="store_true", help="sec 語料改完順手跑 driver 重建＋上傳")
    sub.add_parser("lanes")
    args = ap.parse_args(argv)
    if args.cmd == "lanes":
        return cmd_lanes(args)
    return cmd_scan_apply(args, apply=(args.cmd == "apply"))


if __name__ == "__main__":
    raise SystemExit(main())
