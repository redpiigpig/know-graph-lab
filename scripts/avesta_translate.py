#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""祆教經典逐段繁中翻譯 —— 以公有領域英譯為中介，把 zh 欄逐段補起來。

    python scripts/avesta_translate.py --refresh-names   # 從詞庫拉專名表（先跑這個）
    python scripts/avesta_translate.py --all             # 翻全部未譯段落
    python scripts/avesta_translate.py --only vendidad-03
    python scripts/avesta_translate.py --all --limit 40  # 只翻 40 段（試水溫）

引擎鏈沿用 hellenika_intro.ask()：Gemini → NVIDIA → OpenRouter → Haiku。
見 [[feedback_engine_nvidia_no_haiku]]。

═══════════ 這支腳本與 hellenika_align.py 的唯一體例差別 ═══════════

**專名表不讓 LLM 現編，改從 /translation-glossary 拉。**
希臘那邊是先請模型抽專名再逐批沿用；祆教這邊的 111 條定名已經入庫（2026-09-06），
讓模型自己想名字等於繞過詞庫——而詞庫是絕對權威（[[feedback_glossary_strict_authority]]）。
故 --refresh-names 把 deities／theological_terms／place_names 裡的祆教條目拉成
data/avesta/sources/names.json（進版控、看得見、可人工改），翻譯時整份塞進 prompt。

═══════════════════ 這批材料的三個翻譯陷阱 ═══════════════════

一、**祓魔法典是極度公式化的文本。**
    「O Maker of the material world, thou Holy One!」「Ahura Mazda answered:」
    這兩句在 22 章裡出現數百次。同一個公式若在不同批次被譯成不同說法，
    整本書會讀起來像好幾個人翻的——而逐段對照的版面會把這件事放到最大。
    故 prompt 明列固定譯法，且 batch 內外一律不得改寫。

二、**數字與刑罰額度是這本書的實質內容。**
    「四百鞭」「三步」「九夜」「一千五百枚銀幣」——祓魔法典的宗教意義幾乎全在
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

# 詞庫收的是專名；這些是祓魔法典高頻的**普通名詞**，其定譯同樣不能逐批各譯各的。
EXTRA = {
    "the Holy One": "持阿沙的聖者",
    "Maker of the material world": "物質世界的造主",
    "the Bountiful Immortals": "不朽聖者",
    "the Evil Spirit": "惡靈",
    "the Good Spirit": "善靈",
    "the Bridge of Judgment": "裁判之橋",
    "Tower of Silence": "寂靜之塔",
    "corpse-demon": "屍魔納蘇",
    "clean": "潔淨",
    "unclean": "不潔",
    "purification": "淨禮",
    "Peshotanu": "佩紹坦努罪",
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

    # ── 祓魔法典第 1 章的十六邦國（全書反覆出現，不定死會逐批各譯各的）──
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
    就是白跑一趟。祓魔法典第 2、19 章有數段逾千字。"""
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
    han = sum(1 for c in z if "一" <= c <= "鿿")
    if han < max(2, len(z) * 0.25):
        return "漢字比例過低，疑為未翻譯"
    return None


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

## 專名定譯（**務必逐字沿用，不得另創**）

{names}

## 待譯段落

{items}

## 輸出

只輸出 JSON 物件，鍵為段落編號（字串），值為該段繁體中文譯文。不要 markdown 圍欄、不要任何說明文字。
"""


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
    for chunk in make_batches(todo):
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
        for idx, s in chunk:
            zh = got.get(str(idx)) or got.get(idx)
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
    a = ap.parse_args()

    if a.refresh_names:
        refresh_names()
        if not (a.all or a.only):
            return 0

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
