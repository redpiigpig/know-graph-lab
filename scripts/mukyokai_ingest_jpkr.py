# -*- coding: utf-8 -*-
"""把 mukyokai_fetch_jpkr 抓下來的日／韓文全文批次收進 /research-data 無教會卡。

`mukyokai_sources.py --add` 是一次一件的介面（來源零星、每件都要人工寫 note）。
這批 74 篇是機器抓的，書目欄位帳本裡都有，所以另走批次——但**收錄的規格完全一樣**，
底層就是呼叫 `mukyokai_sources.add()`，不另開一套。

使用者不讀日文（[[feedback_traditional_chinese_only]]），所以題名一律譯成繁中放
`title`、原文題名放 `titleOriginal`；頁面兩行都會顯示。

🚨 **可續跑**。筆電會通勤休眠（[[feedback_laptop_sleeps_design_for_resume]]），
而且每件都要抽全文＋上 R2＋可能 OCR。所以：
  - 已經在 index 裡的 stem 直接跳過
  - 題名中譯另存快取，重跑不重譯（一次 LLM 呼叫都不浪費）
  - 單件失敗只記下來繼續跑，不讓整批停在第 40 件

  python -X utf8 scripts/mukyokai_ingest_jpkr.py --dry-run
  python -X utf8 scripts/mukyokai_ingest_jpkr.py --limit 10
  python -X utf8 scripts/mukyokai_ingest_jpkr.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LEDGER = SCRIPT_DIR / "state" / "mukyokai_jpkr_ledger.jsonl"
TITLE_CACHE = SCRIPT_DIR / "state" / "mukyokai_jpkr_titles.json"

LANG_NAME = {"ja": "日文", "ko": "韓文", "en": "英文"}

TITLE_PROMPT = """把下列{lang}的學術論文題名翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）。只輸出譯好的題名，不要引號、不要說明、不要原文。
2. 無教會主義的專門語彙照既有定名：無教會主義／無教會／聖書（不作「聖經」）／
   傳道／信仰／內村鑑三／矢內原忠雄／金教臣／塚本虎二／高橋三郎。
3. 人名地名用既有中譯；韓文人名用漢字（김교신＝金教臣、함석헌＝**咸錫憲**，
   注意是「咸」不是「鹹」；류영모＝柳永模、최태용＝崔泰瑢、김범부＝金凡父）。
3b. 🚨 咸錫憲的核心概念 **씨알**（日文論文寫作「シアル」）一律譯作 **種子思想**
   （2026-09-11 使用者定名）。不可音譯成「西爾」「希亞爾」「西阿爾」，
   也不可留著假名不譯。
4. 副題用破折號「——」接，不要用冒號堆疊。
5. **西元年份用阿拉伯數字。**
6. 🚨 **書評要譯成書評的樣子**。原題長成「○○著,『書名』, 出版社, 年月刊, 判型,
   頁數, 定價」的是書評，不是論文——只譯出書名等於把書評者掛成那本書的作者。
   請譯成「書評：○○《書名》」，出版社頁數定價一律略去。
7. 引號一律用「」，書名用《》，**必須成對**。原題用『』或「」框住的整體書名，
   中譯用《》。

題名：{source}"""


import re

# 題名開頭的體例標記：<特集論文>／[論説]／【原著論文】。那是欄位不是題名的一部分，
# 留著會讓書目排序與檢索都對不上。
_KIND_TAG = re.compile(r"^\s*[<\[【〔（(]\s*(特集論文|研究ノート|論説|原著論文|資料|書評|"
                       r"翻訳|研究報告|史料紹介|論文|note|article)\s*[>\]】〕）)]\s*",
                       re.I)
_CJK = re.compile(r"[　-鿿]")
_HANGUL = re.compile(r"[가-힣]")


_KO_NAMES_PATH = SCRIPT_DIR.parent / "data" / "mukyokai" / "ko-author-names.json"


def _ko_names() -> dict:
    if not hasattr(_ko_names, "_c"):
        try:
            _ko_names._c = json.loads(_KO_NAMES_PATH.read_text(encoding="utf-8"))
        except Exception:
            _ko_names._c = {}
    return _ko_names._c


def display_author(hangul: str) -> str:
    """韓文作者名 → 可讀又可對照的顯示形式。

    使用者要的是「漢字（諺文）」：漢字給人讀，諺文當對照的錨。問題是**漢字查不到**
    ——KCI 的 metadata 只給羅馬拼音，PDF 首頁印的漢字是論文談論的人物（內村鑑三、
    金敎臣）而不是作者本人。23 位裡只有徐正敏找得到一手來源。

    🚨 剩下 22 位不可以用推的。同音漢字太多，猜下去就是把真人的名字寫錯——
    「咸錫憲」被 OpenCC 改成「鹹錫憲」那次已經示範過一次了。
    所以查得到漢字的寫「漢字（諺文）」，查不到的退成「諺文（KCI 官方拼音）」
    ——兩半都有出處。日後查到漢字就補進 data/mukyokai/ko-author-names.json。
    """
    e = _ko_names().get(hangul)
    if not e:
        return hangul
    if e.get("hanja"):
        return f"{e['hanja']}（{hangul}）"
    if e.get("romaji"):
        return f"{hangul}（{e['romaji']}）"
    return hangul


def clean_author(raw: str) -> str:
    """🚨 帳本的作者欄有三種寫法，不統一會在 index 裡收出重複的一件。

    「呉 敬姫」「朴, 賢淑」「朴, 賢淑／Park, HyunSuk」——而 index 裡既有那筆
    寫的是「呉敬姫」。stem 是 md5(author/title)，差一個空格就是另一個 stem，
    於是同一篇論文會被收兩次、R2 也上兩份。
    """
    s = (raw or "").strip()
    # 羅馬字並列的話只留漢字那半（使用者讀的是中文書目）
    for part in re.split(r"[／/]", s):
        if _CJK.search(part):
            s = part
            break
    s = re.sub(r"[,，]\s*", "", s)     # 「朴, 賢淑」姓名之間的逗號
    if _CJK.search(s):
        return re.sub(r"\s+", "", s)
    s = re.sub(r"\s+", "", s)
    # 純諺文 → 補上可讀的一半（漢字或 KCI 官方拼音）
    return display_author(s) if _HANGUL.search(s) else s.strip()


# 書評的招牌：原題長成「○○著,『書名』, 出版社, 年月刊, 判型, 頁數, 定價」。
# 🚨 不判出來的話，題名只會譯出被評的那本書，於是**書評者被掛成那本書的作者**
# ——2026-09-11 星野靖二與小原克博兩筆就是這樣掛錯的，比錯字嚴重。
_REVIEW = re.compile(r"(著|編)[,，]\s*[『「《]|[0-9〇一二三四五六七八九十]+円")


def is_review(title_original: str) -> bool:
    return bool(_REVIEW.search(title_original or ""))


_PAIRS = (("《", "》"), ("「", "」"), ("『", "』"), ("（", "）"), ("〈", "〉"))


def balance_brackets(t: str) -> str:
    """把成對符號補齊。

    🚨 這件事**不能交給 prompt**。2026-09-11 已經在 prompt 裡明寫「必須成對」，
    模型照樣吐出「書評：赤江達也《「紙上教會」與日本近代－…」（缺兩個收尾）
    與「全球史》中的內村鑑三」（有收尾沒開頭，因為原題用的是「」不是《》）。
    少一個收尾就補在尾巴，少一個開頭就補在最前面——兩種都出現過。

    🚨 要用堆疊，不能逐對獨立補。「…《以無教會為教會…「個人・信仰共同體・社會」
    少了 」 和 》 兩個，逐對處理會補成「…社會》」」——收尾順序反了；
    後開的要先收。
    """
    s = t or ""
    opens = {o: c for o, c in _PAIRS}
    closes = {c: o for o, c in _PAIRS}
    stack, prefix = [], []
    for ch in s:
        if ch in opens:
            stack.append(ch)
        elif ch in closes:
            if stack and stack[-1] == closes[ch]:
                stack.pop()
            else:
                prefix.append(closes[ch])   # 有收尾沒開頭 → 開頭補到最前面
    # 還沒收的，由內而外依序補在尾巴
    return "".join(prefix) + s + "".join(opens[o] for o in reversed(stack))


# 日文舊字體／新字體 → 繁體。書目欄位跟譯文走同一套字形規矩。
_JA_VARIANT = str.maketrans({
    "釈": "釋", "継": "繼", "沢": "澤", "桜": "櫻", "応": "應", "実": "實",
    "気": "氣", "覚": "覺", "読": "讀", "売": "賣", "学": "學", "国": "國",
    "円": "圓", "衆": "眾", "敍": "敘", "説": "說", "巖": "岩", "産": "產",
})


def clean_title(raw: str) -> str:
    s = _KIND_TAG.sub("", (raw or "").strip())
    return re.sub(r"\s+", " ", s).strip()


def load_ledger() -> list[dict]:
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("status") == "ok" and r.get("file"):
            r["author"] = clean_author(r.get("author", ""))
            r["title"] = clean_title(r.get("title", ""))
            rows.append(r)
    # 帳本可能有重跑的重複列，同一個 url 只留最後一筆
    dedup = {r.get("url") or r["file"]: r for r in rows}
    return list(dedup.values())


def load_titles() -> dict:
    if TITLE_CACHE.exists():
        return json.loads(TITLE_CACHE.read_text(encoding="utf-8"))
    return {}


def save_titles(d: dict) -> None:
    TITLE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TITLE_CACHE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def zh_title(raw: str, lang: str, cache: dict) -> str:
    """題名 → 繁中。快取命中就不呼叫引擎。"""
    if raw in cache:
        return cache[raw]
    import translate_ebook_to_zh as te
    old = te.PROMPT_TMPL
    try:
        te.PROMPT_TMPL = TITLE_PROMPT.replace("{lang}", LANG_NAME.get(lang, "外文"))
        out = te.gemini_with_nvidia_fallback(raw)
    finally:
        te.PROMPT_TMPL = old
    # 🚨 NVIDIA 會在輸出開頭夾雜 U+FFFD／BOM 雜訊字元。`uchimura_build.clean_zh_output`
    # 早就在處理這個，但那是走 build 模組的路徑——這裡直接呼叫引擎就漏掉了，
    # 於是 5 筆書目的題名（連帶 R2 key 與 Drive 檔名）開頭都是一個「�」。
    out = out.replace("�", "").replace("﻿", "").strip().strip("《》「」\"' ")
    out = balance_brackets(out.translate(_JA_VARIANT))
    # 🚨 輸出閘：題名太短，整段判準抓不到壞輸出，所以這裡自己再驗一次——
    # 譯不出中文就寧可留原文，不要把模型的碎念寫進書目。
    if not out or not any("一" <= c <= "鿿" for c in out):
        out = raw
    cache[raw] = out
    save_titles(cache)
    return out


def compose_note(r: dict) -> str:
    lang = LANG_NAME.get(r.get("lang", ""), "外文")
    bits = [f"{lang}。"]
    if r.get("titleOriginal") or r.get("title"):
        bits.append(f"原文題名：{r.get('title')}。")
    if r.get("url"):
        bits.append(f"全文取自 {r['url']}。")
    return "".join(bits)


def publisher_of(r: dict) -> str:
    parts = [r.get("venue") or ""]
    if r.get("volume"):
        parts.append(f"第 {r['volume']} 號")
    if r.get("pages"):
        parts.append(f"頁 {r['pages']}")
    return "，".join(p for p in parts if p)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    import mukyokai_sources as ms

    rows = load_ledger()
    index = ms.load_index()
    done = {r["stem"] for r in index}
    # 🚨 光比 stem 不夠。stem 是用**中譯**題名算的，而同一篇論文的中譯每次未必
    # 一字不差；index 裡既有的〈内村鑑三と金教臣〉與帳本那筆只差一個破折號寫法。
    # 所以另外用「原文題名去掉所有標點與空白」當指紋比一次。
    def fingerprint(s: str) -> str:
        return re.sub(r"[^\w　-鿿]", "", (s or "")).lower()

    seen_orig = {fingerprint(r.get("titleOriginal") or r.get("title")) for r in index}
    cache = load_titles()
    todo, skipped = [], 0
    for r in rows:
        if fingerprint(r["title"]) in seen_orig:
            skipped += 1
            continue
        title_zh = cache.get(r["title"], "")
        if title_zh and ms.stem_for(title_zh, r.get("author", "")) in done:
            skipped += 1
            continue
        todo.append(r)
    if args.limit:
        todo = todo[:args.limit]

    print(f"帳本 {len(rows)} 筆，已收 {skipped} 筆，本輪要處理 {len(todo)} 筆")
    if args.dry_run:
        for r in todo[:15]:
            print(f"  [{r.get('lang')}] {r.get('year')} {r.get('author')}　{r.get('title')[:56]}")
        return

    ok, failed = 0, []
    for i, r in enumerate(todo, 1):
        src = Path(r["file"])
        if not src.exists():
            failed.append((r.get("title", "?"), "檔案不在了"))
            continue
        try:
            t_zh = zh_title(r["title"], r.get("lang", ""), cache)
            print(f"[{i}/{len(todo)}] {r.get('author')}　{t_zh[:46]}", flush=True)
            ms.add(
                path=src,
                title=t_zh,
                author=r.get("author", ""),
                year=r.get("year", ""),
                kind="review" if is_review(r["title"]) else (r.get("kind") or "article"),
                note=compose_note({**r, "titleOriginal": r["title"]}),
                publisher=publisher_of(r),
                title_original=r["title"],
                lang=r.get("lang", ""),
            )
            ok += 1
        except Exception as e:  # 單件失敗不讓整批停下來
            failed.append((r.get("title", "?")[:50], f"{type(e).__name__}: {str(e)[:90]}"))
            print(f"   ✗ {type(e).__name__}: {str(e)[:110]}", flush=True)

    print(f"\n收進 {ok} 件；失敗 {len(failed)} 件")
    for t, why in failed:
        print(f"   ✗ {t}　{why}")
    if failed:
        print("🚨 失敗的重跑本支即可（已收的會自動跳過）")


if __name__ == "__main__":
    main()
