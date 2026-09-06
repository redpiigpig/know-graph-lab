#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""祆教經典逐段繁中翻譯 —— 以公有領域英譯為中介，把 zh 欄逐段補起來。

    python scripts/avesta_translate.py --refresh-names   # 從詞庫拉專名表（先跑這個）
    python scripts/avesta_translate.py --all             # 翻全部未譯段落
    python scripts/avesta_translate.py --only vendidad-03
    python scripts/avesta_translate.py --all --limit 40  # 只翻 40 段（試水溫）
    python scripts/avesta_translate.py --all --engine haiku  # 免費池乾掉時走 Haiku

引擎鏈沿用 hellenika_intro.ask()：Gemini → NVIDIA → OpenRouter → Haiku。
見 [[feedback_engine_nvidia_no_haiku]]。

═══════════ 這支腳本與 hellenika_align.py 的唯一體例差別 ═══════════

**專名表不讓 LLM 現編，改從 /translation-glossary 拉。**
希臘那邊是先請模型抽專名再逐批沿用；祆教這邊的 111 條定名已經入庫（2026-09-06），
讓模型自己想名字等於繞過詞庫——而詞庫是絕對權威（[[feedback_glossary_strict_authority]]）。
故 --refresh-names 把 deities／theological_terms／place_names 裡的祆教條目拉成
data/avesta/sources/names.json（進版控、看得見、可人工改），翻譯時整份塞進 prompt。

═══════════════════ 這批材料的三個翻譯陷阱 ═══════════════════

一、**萬迪達德是極度公式化的文本。**
    「O Maker of the material world, thou Holy One!」「Ahura Mazda answered:」
    這兩句在 22 章裡出現數百次。同一個公式若在不同批次被譯成不同說法，
    整本書會讀起來像好幾個人翻的——而逐段對照的版面會把這件事放到最大。
    故 prompt 明列固定譯法，且 batch 內外一律不得改寫。

二、**數字與刑罰額度是這本書的實質內容。**
    「四百鞭」「三步」「九夜」「一千五百枚銀幣」——萬迪達德的宗教意義幾乎全在
    這些量詞上。約略化（「重罰」「數日」）等於把這本書的內容刪掉。

三、**不可潤飾成流暢散文。**
    達梅斯特的英譯本身就是硬譯，句子笨重、重複、羅列。那是原文的樣子，不是譯者的失手。
    改寫成通順中文會抹掉它與利未記潔淨法的可比性——那正是這本書最重要的學術用途。
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hellenika_intro import ask  # noqa: E402  引擎鏈 Gemini → NVIDIA → OpenRouter → Haiku

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_DIR = os.path.join(ROOT, "data", "avesta", "sources", "text")
NAMES_PATH = os.path.join(ROOT, "data", "avesta", "sources", "names.json")


# ─────────────────────── 專名表：從詞庫拉 ───────────────────────

def refresh_names() -> int:
    """把詞庫裡的祆教條目拉成 names.json。進版控，可人工改。"""
    import requests
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}

    table: dict[str, str] = {}
    # 神祇／概念／人物
    for row in requests.get(
            f"{url}/rest/v1/deities?religion=like.*祆教*"
            f"&select=name_english,name_recommended,name_variants",
            headers=h, timeout=60).json():
        if not row.get("name_recommended"):
            continue
        table[row["name_english"]] = row["name_recommended"]
        # 🚨 變體也要當鍵。英譯用的拼法常與詞庫鍵不同（Ahriman vs Angra Mainyu），
        #    只收主鍵的話那些段落比不到，模型就自己另譯一個名字。
        for v in _variant_keys(row.get("name_variants")):
            table.setdefault(v, row["name_recommended"])
    # 經典與文獻名（只取本批來源，免得把基督教作品名一起拉進來）
    for row in requests.get(
            f"{url}/rest/v1/theological_terms?entity_type=eq.work&first_source=like.*avesta*"
            f"&select=term_english,zh_recommended", headers=h, timeout=60).json():
        if row.get("zh_recommended"):
            table[row["term_english"]] = row["zh_recommended"]
    # 地名：波斯相關的那一批
    for row in requests.get(
            f"{url}/rest/v1/place_names?select=name_english,name_recommended",
            headers=h, timeout=60).json():
        if row.get("name_recommended") and row["name_english"] in PLACES_WANTED:
            table[row["name_english"]] = row["name_recommended"]

    table.update(EXTRA)   # 詞庫沒有、但本書高頻的通用詞
    io.open(NAMES_PATH, "w", encoding="utf-8").write(
        json.dumps(dict(sorted(table.items())), ensure_ascii=False, indent=1) + "\n")
    print(f"✓ 專名表 {len(table)} 條 → {NAMES_PATH}")
    return len(table)


def _variant_keys(variants: str | None) -> list[str]:
    """從 name_variants 取出可當比對鍵的**拉丁拼法**。

    變體欄形如「阿里曼(Ahriman)；索魯什（Sorush）；天狼星神」——中文變體對比對無用
    （比對的是英譯全文），只取括號裡的拉丁字。
    """
    if not variants:
        return []
    out: list[str] = []
    for chunk in re.split(r"[；;]", variants):
        for m in re.finditer(r"[（(]\s*([A-Za-zÀ-ɏ' -]{3,40})\s*[）)]", chunk):
            out.append(m.group(1).strip())
        bare = re.sub(r"[（(].*?[）)]", "", chunk).strip()
        if bare and re.fullmatch(r"[A-Za-zÀ-ɏ' -]{3,40}", bare):
            out.append(bare)
    return out


# 詞庫的 place_names 有 268 筆，全塞進 prompt 是浪費；只取本書會出現的。
PLACES_WANTED = {
    "Airyanem Vaejah", "Bisotun", "Naqsh-e Rostam", "Paikuli", "Yazd", "Kerman",
    "Sanjan", "Navsari", "Susa", "Ecbatana", "Media", "Parthia", "Persepolis",
    "Achaemenid Empire", "Sasanian Empire", "Babylon", "Nineveh", "India",
}

# 詞庫收的是專名；這些是萬迪達德高頻的**普通名詞**，其定譯同樣不能逐批各譯各的。
EXTRA = {
    "the Holy One": "持阿沙的聖者",
    "Maker of the material world": "物質世界的造主",
    "the Bountiful Immortals": "不朽聖者",
    "the Evil Spirit": "惡靈",
    "the Good Spirit": "善靈",
    "the Bridge of Judgment": "裁判之橋",
    "Tower of Silence": "寂靜之塔",
    # 🚨 原本寫「屍魔納蘇」，與詞庫的 druj→德魯格 打架，全書 33 段因此違例。
    #    詞庫是絕對權威，改依詞庫；Druj Nasu 是專名（屍體女魔），不作意譯。
    "Druj Nasu": "德魯格‧納蘇",
    "corpse-demon": "德魯格‧納蘇",
    "clean": "潔淨",
    "unclean": "不潔",
    "purification": "淨禮",
    # 兼指該罪與犯此罪者（「整個世界將只剩一個佩紹坦努」），故不綴「罪」
    "Peshotanu": "佩紹坦努",
    "Tanafuhr": "塔納弗爾罪",
    "Aspahe-astra": "馬鞭",
    "Sraosho-carana": "斯勞沙鞭",
    "Dashtan": "經期",
    "Barashnum": "巴爾什農",
    "Hathra": "哈特拉（長度單位）",
    "Vitasti": "維塔斯提（指距）",

    # ── 達梅斯特的拼法與詞庫鍵不同者 ──
    # 🚨 這一組是實測補的。首輪試譯 Vd 1 時，詞庫鍵 "Airyanem Vaejah" 比不上
    #    英譯寫的 "Airyana Vaeja"，模型就自己譯成「艾利亞納‧維賈」——
    #    與詞庫定的「艾里亞納‧瓦埃賈」不同，而版面完全正常。
    "Airyana Vaeja": "艾里亞納‧瓦埃賈",
    "Spitama": "斯皮塔瑪",
    "Ahriman": "安格拉‧曼紐",
    "Ormazd": "阿胡拉‧馬茲達",
    "Vanguhi Daitya": "萬古希‧戴提亞河",
    "Sraosha": "斯勞沙",
    "Rashnu": "拉什努",
    "Ashi Vanguhi": "阿希",
    "Drvaspa": "德爾瓦斯帕",
    "Chista": "奇斯塔",
    "Vayu": "瓦尤",

    # ── 萬迪達德第 1 章的十六邦國（全書反覆出現，不定死會逐批各譯各的）──
    "Sughdha": "蘇格達（粟特）",
    "Mouru": "莫魯（木鹿）",
    "Bakhdhi": "巴赫迪",
    "Nisaya": "尼薩亞",
    "Haroyu": "哈羅尤",
    "Vaekereta": "瓦埃克雷塔",
    "Urva": "烏爾瓦",
    "Khnenta": "赫嫩塔",
    "Harahvaiti": "哈拉赫瓦提",
    "Haetumant": "海圖曼特",
    "Ragha": "拉加",
    "Chakhra": "查赫拉",
    "Varena": "瓦雷納",
    "Hapta Hindu": "哈普塔‧亨杜（七河之地）",
    "Rangha": "蘭哈",
}


def fold(s: str) -> str:
    """去附加符號並轉小寫，供專名比對用。

    🚨 詞庫的鍵按原文寫（daēva、Škand-gumānīg、Vərəθraγna），達梅斯特的英譯
       卻寫 Daeva、Shkand、Verethraghna。直接用子字串比對的話，
       最該出現的那幾條專名反而一條都進不了 prompt——而翻譯照樣跑完，
       只是「迭瓦」變成模型自己想的名字。
    """
    import unicodedata
    # 🚨 順序決定成敗：**先映射二合字母，再剝附加符號**。
    #    反過來的話 NFD 會先把 š 拆成 s＋caron 再把 caron 剝掉，只剩 s——
    #    於是《破疑釋惑》的鍵折成 skand，而英譯寫的是 Shkand，永遠比不到。
    #    ə／θ／γ 沒有分解形，所以那幾條碰巧會過，掩蓋了這個錯。
    n = unicodedata.normalize("NFC", s).lower()
    for a, b in (("θ", "th"), ("δ", "d"), ("γ", "gh"), ("β", "b"), ("ŋ", "ng"),
                 ("ə", "e"), ("š", "sh"), ("ž", "zh"), ("č", "ch"),
                 ("ṣ", "s"), ("ẏ", "y"), ("x", "kh")):
        n = n.replace(a, b)
    n = unicodedata.normalize("NFD", n)
    n = "".join(c for c in n if not unicodedata.combining(c))
    return n


def mentions(key: str, folded_blob: str) -> bool:
    """本篇英譯有沒有提到這個專名。

    鍵含「/」時任一側命中即算（Vendidad / Videvdad、magi / magus）。
    多詞書名另試第一個詞：英譯常只寫 "the Shkand"，而鍵是完整書名
    「Škand-gumānīg Wizār」——不試首詞的話這條就漏了，模型會自己另譯書名。
    首詞須 ≥5 字母，免得 "Sad Dar" 的 "sad" 一類短詞到處命中。
    """
    for part in key.split("/"):
        p = fold(part).strip()
        if len(p) >= 3 and p in folded_blob:
            return True
        words = [w for w in re.split(r"[-\s]+", p) if w]
        # 前兩個詞（英譯常省略書名末尾的 nāmag／yasn 一類通名）
        if len(words) >= 2 and " ".join(words[:2]) in folded_blob:
            return True
        # 單一首詞須 ≥5 字母，免得 "Sad Dar" 的 "sad" 一類短詞到處命中
        if len(words[0]) >= 5 and words[0] in folded_blob:
            return True
    return False


def cites(key: str, folded_blob: str) -> bool:
    """稽核用的**嚴格**比對：整個鍵須以完整詞出現。

    🚨 與 mentions() 分開是刻意的，兩者的錯誤代價相反：
       · mentions() 供**塞 prompt** 用——寧可多給，多一條定名無害。
       · cites() 供**稽核**用——寧可少報，誤報會把人帶去改本來就對的譯文。
       用 mentions() 稽核會得出荒謬的數字：鍵 "the Good Spirit" 的前兩詞
       "the good" 命中 "the good lands"，鍵 "Ard" 命中 "toward"，
       2026-09-06 首次稽核就這樣虛報了數百段。
    """
    p = fold(key.split("/")[0]).strip()
    if len(p) < 4:
        return False
    return re.search(rf"(?<![a-z]){re.escape(p)}(?![a-z])", folded_blob) is not None


# 稽核時略過的鍵：普通名詞或語義可變，不強制字面對應。
AUDIT_SKIP = {"clean", "unclean", "purification", "the Holy One", "the Good Spirit",
              "the Evil Spirit", "Maker of the material world", "corpse-demon",
              "Hathra", "Vitasti", "the Bountiful Immortals"}


def audit() -> int:
    """全書掃一遍：英譯提到的專名，中譯有沒有照詞庫定名。回違例段次。"""
    names = load_names()
    viol: dict[tuple[str, str], list[str]] = {}
    for f in sorted(glob.glob(os.path.join(TEXT_DIR, "*.json"))):
        d = json.loads(io.open(f, encoding="utf-8").read())
        for seg in d["segments"]:
            en, zh = (seg.get("en") or ""), (seg.get("zh") or "")
            if not (en and zh):
                continue
            # 起句引錄（Vd 10.4、10.8）的專名本來就該保留轉寫不譯，不納入稽核
            if is_citation_list(en):
                continue
            fb = fold(en)
            for k, v in names.items():
                if k in AUDIT_SKIP:
                    continue
                if cites(k, fb) and v.split("（")[0] not in zh:
                    viol.setdefault((k, v), []).append(seg["ref"])
    total = sum(len(r) for r in viol.values())
    if not total:
        print("✓ 專名全數照詞庫定名")
        return 0
    print(f"專名未照詞庫定名：{total} 段次")
    for (k, v), refs in sorted(viol.items(), key=lambda x: -len(x[1])):
        print(f"  {k:28s} 應作「{v}」　{len(refs)} 段　例 {refs[:3]}")
    return total


def audit_refs() -> set[str]:
    """稽核違例的段落 ref。與 audit() 同一判準，只是回集合供 --refix 用。"""
    names = load_names()
    bad: set[str] = set()
    for f in sorted(glob.glob(os.path.join(TEXT_DIR, "*.json"))):
        d = json.loads(io.open(f, encoding="utf-8").read())
        for seg in d["segments"]:
            en, zh = (seg.get("en") or ""), (seg.get("zh") or "")
            if not (en and zh):
                continue
            if is_citation_list(en):
                continue
            fb = fold(en)
            for k, v in names.items():
                if k in AUDIT_SKIP:
                    continue
                if cites(k, fb) and v.split("（")[0] not in zh:
                    bad.add(seg["ref"])
                    break
    return bad


def load_names() -> dict[str, str]:
    if not os.path.exists(NAMES_PATH):
        print("✗ 找不到 names.json，先跑 --refresh-names", file=sys.stderr)
        sys.exit(1)
    return json.loads(io.open(NAMES_PATH, encoding="utf-8").read())


# ─────────────────────── 分批 ───────────────────────

BATCH = 8            # 單批段數上限
BATCH_CHARS = 3000   # 單批英譯字數上限——超長會讓回傳 JSON 被截斷，整批報廢
SOLO_CHARS = 700     # 超過這個長度的段落單獨成批


def make_batches(todo: list[tuple[int, dict]]) -> list[list[tuple[int, dict]]]:
    """依字數動態分批。固定段數在長段落上會撐爆回傳長度，整批 JSON 解析失敗
    就是白跑一趟。萬迪達德第 2、19 章有數段逾千字。"""
    out: list[list[tuple[int, dict]]] = []
    cur: list[tuple[int, dict]] = []
    n = 0
    for item in todo:
        size = len(item[1].get("en") or "")
        if size > SOLO_CHARS:
            if cur:
                out.append(cur)
                cur, n = [], 0
            out.append([item])
            continue
        if cur and (n + size > BATCH_CHARS or len(cur) >= BATCH):
            out.append(cur)
            cur, n = [], 0
        cur.append(item)
        n += size
    if cur:
        out.append(cur)
    return out


# ─────────────────────── 落地前的閘 ───────────────────────

# 挑幾個在繁體中絕不會出現、且不與異體字混淆的簡體字當哨兵。
# 🚨 不用 OpenCC 全文比對——它會把「祢」判成簡體（見 feedback_reader_silent_failures）。
SIMPLIFIED_SENTINELS = "这么么们个国说时来对开会没后学动应产东车问题龙凤书图师"

BAD_PATTERNS = [
    (re.compile(r"^\s*(?:抱歉|對不起|作為|我無法|I(?:'m| am) sorry|As an AI)", re.I),
     "回的是拒絕或自我介紹，不是譯文"),
    (re.compile(r"```"), "含 markdown 圍欄"),
    (re.compile(r"[぀-ゟ゠-ヿ]"), "混入日文假名"),
]


def normalise_keys(got: object) -> dict[str, str]:
    """把模型回傳的鍵正規化成純數字字串。

    🚨 各引擎的習慣不同：Gemini／NVIDIA 回 "2"，**Haiku 回 "[2]"**（照抄 prompt
       裡的段落標記）。只查 "2" 的話，整批譯文全部對不上而一個字都不印——
       2026-09-06 首次切到 Haiku 就是這樣靜靜空轉了兩輪。
    """
    if not isinstance(got, dict):
        return {}
    out: dict[str, str] = {}
    for k, v in got.items():
        if not isinstance(v, str):
            continue
        m = re.search(r"\d+", str(k))
        if m:
            out[m.group(0)] = v
    return out


def join_parts(got: dict[str, str]) -> str:
    """把模型拆碎的一段譯文按鍵序併回。單段批次專用。"""
    parts = sorted(got.items(), key=lambda kv: int(kv[0]))
    return "\n".join(v.strip() for _, v in parts if v.strip())


def reject_reason(zh: str, en: str) -> str | None:
    """這一段譯文能不能落地。回 None 表示可以。

    🚨 存在的理由：翻壞的段落落地之後，版面看起來完全正常——中文欄有字、
       段數也對——只有真的去讀才發現那是英文原樣、是拒絕語、或是簡體。
    """
    z = zh.strip()
    if not z:
        return "空白"
    if len(z) < 2:
        return "過短"
    for pat, why in BAD_PATTERNS:
        if pat.search(z):
            return why
    bad = [c for c in z if c in SIMPLIFIED_SENTINELS]
    if bad:
        return f"含簡體字 {''.join(sorted(set(bad)))}"
    # 整段幾乎沒有漢字＝根本沒翻（回了英文原樣）
    #
    # 🚨 例外：**起句引錄**。萬迪達德第 10 章逐條列出該誦幾遍的伽薩詩句，
    #    英譯就是一串阿維斯陀語起句加經文出處（`ahya yasa ... urvanem (Y28.2)`）。
    #    那些字**本來就該保留轉寫不譯**，漢字自然少——2026-09-06 全書跑完，
    #    僅存的兩段未譯（Vd 10.4、10.8）就是被這條誤殺的。
    #    故依「英譯來源本身是不是引錄」放寬，而不是全域調低門檻。
    ratio = 0.06 if is_citation_list(en) else 0.25
    han = sum(1 for c in z if "一" <= c <= "鿿")
    if han < max(2, len(z) * ratio):
        return "漢字比例過低，疑為未翻譯"

    # 🚨 長段落被摘要掉。模型面對六百字以上的段落會「講重點」而不是逐句譯，
    #    結果中文欄有字、段數也對、讀起來還很通順——只有跟英譯並排才看得出
    #    少了三分之二。2026-09-06 全書跑完有 11 段這樣（最慘的 1303 字只剩 47 字）。
    #    全書長段的中英字數比中位數 0.31，0.20 以下與其上有明顯斷崖，故取 0.20。
    if len(en) > TRUNCATION_MIN_EN and len(z) < len(en) * TRUNCATION_RATIO:
        return f"疑為摘要而非全譯（中{len(z)}字／英{len(en)}字＝{len(z) / len(en):.2f}）"
    return None


TRUNCATION_MIN_EN = 200    # 短段落的字數比波動大，不適用
TRUNCATION_RATIO = 0.20


CITATION_REF = re.compile(r"\(Y\s?\d+\.\d+\)")


def is_citation_list(en: str) -> bool:
    """這一段的英譯是不是「起句引錄」——一串原文起句加經文出處。

    判準取兩個同時成立的訊號：兩處以上的經文出處標記，且有省略號。
    只看其中一個會誤放行普通段落（正文也會偶爾夾一個出處）。
    """
    return len(CITATION_REF.findall(en)) >= 2 and "..." in en


# ─────────────────────── 翻譯 ───────────────────────

PROMPT = """把下列祆教經典的英譯逐段翻成**繁體中文**。這是要收進本站《祆教經典》的三欄逐段對照（原文轉寫／英譯／繁中），讀者會並排比對，因此**段落必須逐一對應，不可合併、不可拆分、不可增刪**。

篇名：{title}（{siglum}）
英譯者：{translator}

## 翻譯規矩（違反即為錯譯）

1. **公式句必須逐次完全相同。** 本書極度公式化，同一句在全書出現數百次；若不同段落譯法不一，逐段對照的版面會把這件事放到最大。固定譯法如下，一字不改：
   - "O Maker of the material world, thou Holy One!" → 「物質世界的造主啊，持阿沙的聖者啊！」
   - "Ahura Mazda answered:" → 「阿胡拉‧馬茲達答道：」
   - "Zarathushtra asked Ahura Mazda:" → 「查拉圖斯特拉問阿胡拉‧馬茲達：」
   - "Thus said Ahura Mazda" → 「阿胡拉‧馬茲達如此說」
2. **數字、刑罰額度、長度、日數一律照抄，不可約略化。** 「四百鞭」不可寫成「重罰」，「九夜」不可寫成「數日」，「三十步」不可寫成「數步」。本書的宗教意義幾乎全在這些量詞上。
3. **不可潤飾成流暢散文。** 達梅斯特的英譯句子笨重、重複、羅列——那是原文的樣子，不是譯者的失手。改寫成通順中文會抹掉它與利未記潔淨法的可比性。**寧可生硬，不可漂亮。**
4. **問答體保留一問一答的分行**，不要併成一段敘述。
5. **英譯裡的圓括號（編者補充）保留為中文全形括號**；方括號〔〕表示原文已缺而由編者補入，若英譯有就保留。
6. 中間點用「‧」；**全文繁體，不得出現簡體字或日文漢字寫法**。
7. **不得增補英譯沒有的內容。** 看不懂的專名照音譯，寧可生硬不可臆造；不要加註解、不要加背景說明。
8. **也不得刪減。長段落必須逐句譯完，不可摘要、不可只譯開頭。** 本書有些段落逾千字且極度重複（同一問答換一個對象問十次），那個重複正是原文的體例；「講重點」等於把內容刪掉。譯文長度應與英譯相當，短於英譯三分之一即為漏譯。

## 專名定譯（**務必逐字沿用，不得另創**）

{names}

## 待譯段落

{items}

## 輸出

只輸出 JSON 物件，鍵為段落編號（字串），值為該段繁體中文譯文。不要 markdown 圍欄、不要任何說明文字。
"""


LONG_CHARS = 500       # 超過此長度改走「切塊分譯再併回」
PIECE_CHARS = 380      # 每小塊的目標長度
PIECES_PER_CALL = 6    # 一次呼叫至多幾塊（多了模型會漏塊）


def split_long_en(en: str) -> list[str]:
    """把過長的英譯切成數小塊，供分別翻譯後併回。

    🚨 為什麼要切：合併段（Vd 7.5-8、Vd 12.22-24 一類涵蓋數節者）的英譯有
       八百到一千六百字，模型面對這種長度一律「講重點」而非逐句譯——
       即使 prompt 明令不可摘要也一樣，實測連退三輪都不收斂。
       切成四百字上下的小塊、各自成為一個 JSON 值，模型就會老實譯完。

    先按換行切（原文本來就分節），還太長的再按句號切；不在句中斷開。
    """
    out: list[str] = []
    for para in [p.strip() for p in en.split(chr(10)) if p.strip()]:
        if len(para) <= PIECE_CHARS * 1.6:
            out.append(para)
            continue
        cur = ""
        for sent in re.split(r"(?<=[.!?])\s+", para):
            if cur and len(cur) + len(sent) > PIECE_CHARS:
                out.append(cur.strip())
                cur = ""
            cur += (" " if cur else "") + sent
        if cur.strip():
            out.append(cur.strip())
    return out or [en]


def translate_doc(doc: dict, names: dict[str, str], budget: list[int]) -> tuple[int, int]:
    """翻一篇。回 (成功段數, 退回段數)。budget 是可變的剩餘段數上限。"""
    segs = doc["segments"]
    todo = [(i, s) for i, s in enumerate(segs)
            if (s.get("en") or "").strip() and not (s.get("zh") or "").strip()]
    if budget[0] is not None:
        todo = todo[:max(0, budget[0])]
    if not todo:
        return 0, 0

    # 只把本篇實際出現的專名塞進 prompt——全表 144 條會稀釋掉真正相關的那幾條。
    blob = fold(" ".join((s.get("en") or "") for _, s in todo))
    hit = {k: v for k, v in names.items() if mentions(k, blob)}
    hit.update({k: v for k, v in names.items() if k in EXTRA})   # 通用詞一律附上
    name_lines = "\n".join(f"- {k} → {v}" for k, v in sorted(hit.items())) or "（無，依基礎詞庫）"

    ok = rejected = 0

    # 長段先單獨處理：切塊分譯再併回。留在一般批次裡只會一再被摘要退回。
    long_items = [(i, seg) for i, seg in todo if len(seg.get("en") or "") > LONG_CHARS]
    for idx, seg in long_items:
        zh = translate_long(seg, name_lines, doc)
        if not zh:
            rejected += 1
            continue
        why = reject_reason(zh, seg["en"])
        if why:
            print(f"    ⚠ {seg['ref']} 退回（{why}）", flush=True)
            rejected += 1
            continue
        seg["zh"] = zh
        ok += 1
        if budget[0] is not None:
            budget[0] -= 1
    todo = [(i, seg) for i, seg in todo if len(seg.get("en") or "") <= LONG_CHARS]

    batches = make_batches(todo)
    if todo and not batches:
        print(f"    ✗ {doc.get('siglum')} 有 {len(todo)} 段待譯卻切不出批次", flush=True)
    for chunk in batches:
        items = "\n\n".join(
            f"[{idx}]（{s['ref']}）\n英譯：{s['en']}"
            + (f"\n原文轉寫（供參照，不必譯）：{s['orig'][:300]}" if s.get("orig") else "")
            for idx, s in chunk)
        prompt = PROMPT.format(title=doc.get("title_zh") or doc.get("title_en"),
                               siglum=doc.get("siglum", ""),
                               translator=doc.get("en_translator", ""),
                               names=name_lines, items=items)
        try:
            raw = ask(prompt)
        except Exception as e:  # noqa: BLE001
            print(f"    ✗ 本批失敗：{e}", flush=True)
            continue
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
        try:
            got = json.loads(raw)
        except json.JSONDecodeError:
            print("    ✗ 回傳非 JSON，跳過本批", flush=True)
            continue
        got = normalise_keys(got)
        # 🚨 單段批次（長段落）Haiku 常不理會段落標記，逕自把那一長段拆成
        #    數小塊回 1,2,3,4 —— 鍵對不上，整段就譯不到。整份回應本來就只講
        #    這一段，故按鍵序併回同一段。2026-09-06 全書 18 段卡在這裡。
        if len(chunk) == 1 and got and str(chunk[0][0]) not in got:
            got = {str(chunk[0][0]): join_parts(got)}
        # 🚨 回了合法 JSON 但鍵對不上時，下面的迴圈會一路 continue，
        #    整批 0 段落地而**一個字都不印**——首次跑 Haiku 就這樣靜靜空轉。
        #    故先檢查鍵有沒有交集，沒有就把實際拿到的鍵印出來。
        wanted = {str(idx) for idx, _ in chunk}
        if not (wanted & set(got)):
            print(f"    ✗ 回傳鍵對不上：要 {sorted(wanted)[:4]}…，"
                  f"拿到 {sorted(got)[:4]}…", flush=True)
            continue

        for idx, s in chunk:
            zh = got.get(str(idx))
            if not isinstance(zh, str):
                continue
            zh = zh.strip().replace("・", "‧")
            why = reject_reason(zh, s.get("en") or "")
            if why:
                print(f"    ⚠ {s['ref']} 退回（{why}）", flush=True)
                rejected += 1
                continue
            s["zh"] = zh
            ok += 1
            if budget[0] is not None:
                budget[0] -= 1
        time.sleep(1.2)
    return ok, rejected


def translate_long(seg: dict, name_lines: str, doc: dict) -> str:
    """長段落：切塊分譯再按序併回。回空字串表示失敗。"""
    pieces = split_long_en(seg["en"])
    got: dict[str, str] = {}

    # 🚨 一次送太多塊，模型會漏塊。實測 12 塊漏 4 塊、20 塊漏 4 塊——
    #    而漏掉的塊若不檢查就會併出一段讀來通順卻少了三分之一的譯文。
    #    故分多次呼叫，每次至多 PIECES_PER_CALL 塊。
    for start in range(0, len(pieces), PIECES_PER_CALL):
        group = list(enumerate(pieces[start:start + PIECES_PER_CALL], start + 1))
        items = (chr(10) * 2).join(
            f"[{i}]（{seg['ref']} 第 {i} 塊，全段共 {len(pieces)} 塊）"
            f"{chr(10)}英譯：{p}" for i, p in group)
        prompt = PROMPT.format(title=doc.get("title_zh") or doc.get("title_en"),
                               siglum=doc.get("siglum", ""),
                               translator=doc.get("en_translator", ""),
                               names=name_lines, items=items)
        try:
            raw = ask(prompt)
        except Exception as e:  # noqa: BLE001
            print(f"    ✗ {seg['ref']} 分譯失敗：{e}", flush=True)
            return ""
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
        try:
            got.update(normalise_keys(json.loads(raw)))
        except json.JSONDecodeError:
            print(f"    ✗ {seg['ref']} 分譯回傳非 JSON", flush=True)
            return ""
        time.sleep(1.0)

    def _missing() -> list[int]:
        return [i for i in range(1, len(pieces) + 1) if not (got.get(str(i)) or "").strip()]

    # 塊數多時模型仍會零星漏塊（十四、五塊的段落每輪漏一兩塊）。
    # 只把漏掉的那幾塊重問，每次至多三塊，最多兩輪。
    for _ in range(2):
        miss = _missing()
        if not miss:
            break
        for k in range(0, len(miss), 3):
            grp = miss[k:k + 3]
            items = (chr(10) * 2).join(
                f"[{i}]（{seg['ref']} 第 {i} 塊，全段共 {len(pieces)} 塊）"
                f"{chr(10)}英譯：{pieces[i - 1]}" for i in grp)
            prompt = PROMPT.format(title=doc.get("title_zh") or doc.get("title_en"),
                                   siglum=doc.get("siglum", ""),
                                   translator=doc.get("en_translator", ""),
                                   names=name_lines, items=items)
            try:
                raw = ask(prompt)
            except Exception:  # noqa: BLE001
                continue
            raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
            try:
                got.update(normalise_keys(json.loads(raw)))
            except json.JSONDecodeError:
                continue
            time.sleep(1.0)

    # 🚨 缺塊就整段不落地。少一塊而其餘照常顯示，正是最難發現的漏譯。
    miss = _missing()
    if miss:
        print(f"    ✗ {seg['ref']} 分譯缺第 {','.join(map(str, miss))} 塊"
              f"（共 {len(pieces)} 塊，已重試兩輪）", flush=True)
        return ""
    return join_parts(got)


def process(path: str, names: dict[str, str], budget: list[int]) -> None:
    doc = json.loads(io.open(path, encoding="utf-8").read())
    before = len(doc["segments"])
    have0 = sum(1 for s in doc["segments"] if (s.get("zh") or "").strip())

    ok, rej = translate_doc(doc, names, budget)
    if not ok:
        if rej:
            print(f"  {os.path.basename(path)}：0 段落地（{rej} 段退回）", flush=True)
        return

    # 🚨 落地前的最後一道：段數絕不可變。變了就是整份對照錯位，而頁面完全正常。
    assert len(doc["segments"]) == before, f"{path} 段數由 {before} 變成 {len(doc['segments'])}"
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    have = sum(1 for s in doc["segments"] if (s.get("zh") or "").strip())
    print(f"  ✓ {os.path.basename(path)}：+{ok} 段"
          f"（{have}/{before}，{have / before:.0%}）"
          + (f"　⚠ 退回 {rej}" if rej else ""), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="祆教經典逐段繁中翻譯")
    ap.add_argument("--refresh-names", action="store_true", help="從詞庫重拉專名表")
    ap.add_argument("--all", action="store_true", help="翻全部未譯段落")
    ap.add_argument("--only", nargs="*", help="只翻這幾個 slug")
    ap.add_argument("--limit", type=int, help="本輪最多翻幾段")
    ap.add_argument("--reset", action="store_true",
                    help="把指定篇章的 zh 清空後重譯（專名表更新後修既有譯文用）")
    ap.add_argument("--refix", action="store_true",
                    help="稽核出違例段落 → 清空 → 以更新後的專名表重譯")
    ap.add_argument("--audit", action="store_true",
                    help="掃全書：英譯提到的專名，中譯有沒有照詞庫定名")
    ap.add_argument("--engine", choices=["auto", "haiku"], default="auto",
                    help="auto＝Gemini→NVIDIA→OpenRouter→Haiku 全鏈；"
                         "haiku＝直接走 Haiku（Max 方案不另計費，免費池乾掉時用）")
    a = ap.parse_args()

    # ask() 以 HELLENIKA_ENGINE 判斷是否強制走 Haiku（見 hellenika_intro.ask）。
    # 🚨 Haiku 一律只在使用者明確下令時啟用，見 [[feedback_ocr_strategy]]。
    if a.engine == "haiku":
        os.environ["HELLENIKA_ENGINE"] = "haiku"
        print("引擎：Haiku（使用者指定）", flush=True)

    if a.refresh_names:
        refresh_names()
        if not (a.all or a.only or a.audit):
            return 0

    if a.audit:
        audit()
        return 0                       # 稽核只報告，不改動、不當失敗

    if a.refix:
        bad = audit_refs()
        if not bad:
            print("✓ 無違例段落")
            return 0
        n = 0
        for f in sorted(glob.glob(os.path.join(TEXT_DIR, "*.json"))):
            d = json.loads(io.open(f, encoding="utf-8").read())
            hit = False
            for seg in d["segments"]:
                if seg["ref"] in bad and (seg.get("zh") or "").strip():
                    seg["zh"] = ""
                    n += 1
                    hit = True
            if hit:
                io.open(f, "w", encoding="utf-8").write(
                    json.dumps(d, ensure_ascii=False, indent=2) + "\n")
        print(f"↻ 清空 {n} 段違例譯文，改以更新後的專名表重譯", flush=True)
        a.all = True

    if not (a.all or a.only):
        ap.print_help()
        return 0

    names = load_names()
    paths = sorted(glob.glob(os.path.join(TEXT_DIR, "*.json")))
    if a.only:
        paths = [p for p in paths
                 if os.path.basename(p).replace(".json", "") in set(a.only)]
    if not paths:
        print("沒有符合的篇章。")
        return 1

    if a.reset:
        # 專名表更新後，既有譯文裡的舊譯名不會自己改掉——清空重譯才會。
        n = 0
        for p in paths:
            d = json.loads(io.open(p, encoding="utf-8").read())
            for seg in d["segments"]:
                if (seg.get("zh") or "").strip():
                    seg["zh"] = ""
                    n += 1
            io.open(p, "w", encoding="utf-8").write(
                json.dumps(d, ensure_ascii=False, indent=2) + "\n")
        print(f"↻ 已清空 {n} 段譯文，準備重譯", flush=True)

    budget = [a.limit]
    total_todo = 0
    for p in paths:
        d = json.loads(io.open(p, encoding="utf-8").read())
        total_todo += sum(1 for s in d["segments"]
                          if (s.get("en") or "").strip() and not (s.get("zh") or "").strip())
    print(f"待譯 {total_todo} 段 / {len(paths)} 篇"
          + (f"（本輪上限 {a.limit} 段）" if a.limit else ""), flush=True)

    for p in paths:
        if budget[0] is not None and budget[0] <= 0:
            break
        process(p, names, budget)

    done = todo = 0
    for p in sorted(glob.glob(os.path.join(TEXT_DIR, "*.json"))):
        d = json.loads(io.open(p, encoding="utf-8").read())
        for s in d["segments"]:
            if (s.get("en") or "").strip():
                todo += 1
                if (s.get("zh") or "").strip():
                    done += 1
    print(f"\n全區進度：{done}/{todo}（{done / todo:.1%}）" if todo else "\n無可譯段落")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
