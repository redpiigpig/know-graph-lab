#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
祆教經典取源管線 —— 從 avesta.org 抓阿維斯陀語轉寫與《東方聖書》英譯，
逐節對齊後寫成 data/avesta/sources/text/{slug}.json（reader 直接吃）。

用法：
    python scripts/avesta_fetch.py vendidad            # 萬迪達德 22 章
    python scripts/avesta_fetch.py vendidad --only 1 3 # 只抓第 1、3 章
    python scripts/avesta_fetch.py --list              # 列出已實作的書

═══════════════ 這支腳本會踩到的三個坑，動它之前先讀完 ═══════════════

一、**腳註與經文都以數字開頭。**
    英譯頁是兩欄表格：<TD VALIGN=TOP> 是經文，<TD CLASS="NOTE"> 是腳註，
    兩邊的段落都長成「3. 某某……」。若整頁抓下來再用正規表達式找數字，
    腳註會被當成經文節塞進去——而版面看起來完全正常，只是第 3 節變成了
    達梅斯特對第 3 節的註解。**一定要先按 TD 切開再解析。**

二、**兩邊的節數不一定一樣。**
    轉寫依蓋爾德納校本分節，英譯依達梅斯特分節，偶有一方多切或少切一節。
    對不齊時本腳本**不猜**：以節號為鍵各自入位，缺的那一欄留空，
    並在 stdout 報出差異。硬湊成一對一會造成整章往下錯位一格。

三、**轉寫方案不是霍夫曼式。**
    avesta.org 用蓋爾德納舊式羅馬轉寫（mraot ahurô mazdå），
    故一律寫入 orig_scheme='geldner-roman'。站上據此**不開**阿維斯陀字母切換
    ——舊式的 sh／ng 需語音學判斷才拆得開，機器硬轉會拼錯而畫面照樣好看。
    見 data/avesta/sources/index.ts 的 TranslitScheme。

引擎政策：本腳本不用 LLM。繁中翻譯是另一支（avesta_translate.py），
走 Gemini → NVIDIA → Haiku，見 [[feedback_engine_nvidia_no_haiku]]。
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "avesta" / "sources" / "text"
BASE = "https://www.avesta.org"

UA = "Mozilla/5.0 (compatible; know-graph-lab/1.0; scripture research)"
SLEEP = 1.5  # 對一個由個人維護了三十年的站，別跑太快


# ────────────────────────── 純函式：解析 ──────────────────────────

def strip_tags(fragment: str) -> str:
    """去標籤、還原實體、壓平空白。<SUP> 註標整個丟掉——那是註號不是經文。"""
    s = re.sub(r"<SUP\b[^>]*>.*?</SUP>", "", fragment, flags=re.I | re.S)
    s = re.sub(r"<BR\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<P\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t ]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def parse_sbe_chapter(page: str) -> dict[int, str]:
    """
    解析 avesta.org 的英譯單章頁，回 {節號: 英譯}。

    🚨 先按 TD 切開再解析（見檔首坑一）。只取 <TD VALIGN=TOP> 的經文欄，
       <TD CLASS="NOTE"> 的腳註欄整個丟掉。
    """
    verses: dict[int, str] = {}
    last = 0
    # 逐個 TD 切；經文欄的特徵是不帶 CLASS="NOTE"
    for m in re.finditer(r"<TD\b([^>]*)>(.*?)(?=<TD\b|</TR>|</TABLE>)", page, re.I | re.S):
        attrs, body = m.group(1), m.group(2)
        if re.search(r'CLASS\s*=\s*"?NOTE', attrs, re.I):
            continue
        text = strip_tags(body)
        if not text:
            continue
        # 🚨 一格常裝**好幾節**（第 4 章有一格從第 23 節排到第 45 節）。
        #    只取每格第一節的話，55 節的一章只會抓到 30 節——而頁面完全正常，
        #    沒有任何地方看得出少了。故格內再按「行首的 N.」切一次。
        last = _absorb_verses(text, verses, last)
    return verses


def _absorb_verses(text: str, verses: dict[int, str], last: int) -> int:
    """把一格文字按行首「N.」切成數節塞進 verses，回傳最後看到的節號。

    節號必須遞增；倒退者多半是正文裡的列舉，併回上一節而不另開新節。
    無節號的格若接在某節之後，視為該節的續段（羅馬數字小標除外）。
    """
    parts = re.split(r"(?:^|\n)\s*(\d{1,3})\.\s+", text)

    lead = parts[0].strip()
    if lead and last in verses and not re.fullmatch(r"[IVXLC]+[a-z]?\.?", lead):
        verses[last] = f"{verses[last]}\n{lead}".strip()

    for i in range(1, len(parts) - 1, 2):
        n = int(parts[i])
        chunk = parts[i + 1].strip()
        if not chunk:
            continue
        if n <= last:
            if last in verses:
                verses[last] = f"{verses[last]} {parts[i]}. {chunk}".strip()
            continue
        verses[n] = f"{verses[n]}\n{chunk}" if n in verses else chunk
        last = n
    return last


def parse_translit_book(page: str, chapter_anchor: str = "chapt") -> dict[int, dict[tuple[int, int], str]]:
    """
    解析 avesta.org 的整書轉寫頁（vd.htm／yasna 等），回 {章: {節: 轉寫}}。

    章以 <H3 id=chaptN> 錨點或標題分界，節以 <DT>N<DD>正文 的定義列表分界；
    沒有 DL 結構時退回裸數字切法。
    """
    out: dict[int, dict[tuple[int, int], str]] = {}
    marks = _chapter_marks(page, chapter_anchor)
    for i, (start, chap) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(page)
        chunk = page[start:end]
        verses = _parse_definition_list(chunk)
        if not verses:
            # 沒有 <DL> 結構時退回裸數字切法（供其他書／其他頁型使用）
            text = strip_tags(chunk)
            text = re.sub(r"^\s*(Fargard|Yasna|Yasht|Visperad)\s+[\dIVX]+\.?\s*", "", text, flags=re.I)
            verses = {(n, n): t for n, t in _split_verses(text).items()}
        out[chap] = verses
    return out


def _parse_definition_list(chunk: str) -> dict[tuple[int, int], str]:
    """解析 avesta.org 轉寫頁的 <DT>節號<DD>正文 定義列表，回 {(起,訖): 正文}。

    🚨 兩件事會讓整章安靜地變空或變殘：
       一、節號有帶句點與不帶句點兩種寫法，同一份檔案裡混用
           （第 1–16 章多為 `<DT>1 `，第 17 章以後多為 `<DT>1. `）。
       二、**節號可以是區間**（`<DT>3-4`、`<DT>22-24`）——蓋爾德納把數節合成
           一段轉寫。只認純數字的話這些條目整條被跳過：第 12 章的 13 個條目裡
           有 10 個是區間，於是只剩 3 節，而頁面照樣顯示。
       兩者都在 2026-09-06 首次抓取時真的發生過。
    """
    verses: dict[tuple[int, int], str] = {}
    for m in re.finditer(
        r"<DT>\s*(\d+)\s*(?:[-–]\s*(\d+))?\s*\.?\s*(?:</DT>)?\s*<DD>(.*?)(?=<DT\b|</DL>|\Z)",
        chunk, re.I | re.S,
    ):
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        if end < start:
            end = start
        text = strip_tags(m.group(3))
        if not text:
            continue
        key = (start, end)
        verses[key] = f"{verses[key]}\n{text}" if key in verses else text
    return verses


def _chapter_marks(page: str, chapter_anchor: str) -> list[tuple[int, int]]:
    """找出各章的起點，回 [(位置, 章號), …]，依位置排序且章號嚴格遞增。

    🚨 **不可只認 anchor。** avesta.org 的 vd.htm 只有 chapter1–chapter9 有錨點，
       第 10 章以後只剩「Fargard N.」標題。只認錨點的話後 13 章的原文整段消失，
       而書目頁與 reader 都照常顯示、只是原文欄空著——第一版就是這樣掉了 13 章。
       故錨點與標題兩種都收，同章取最早出現者。
    """
    found: list[tuple[int, int]] = []
    # 錨點：vd.htm 實際用的是 id=chapt12（無引號、chapt 不是 chapter），
    # 故前綴接受 chapt 與 chapter 兩種寫法。
    for m in re.finditer(rf'(?:NAME|ID)\s*=\s*["\']?{chapter_anchor}(?:er)?(\d+)["\']?', page, re.I):
        found.append((m.end(), int(m.group(1))))
    # 標題：只認出現在 <H1>–<H4> 裡的，避免把正文或註解中的互見（「參 Fargard 13」）
    # 當成章界——那會把前一章從互見處硬生生截斷，而頁面照常顯示。
    for m in re.finditer(
        r"<H[1-4]\b[^>]*>\s*(?:Fargard|Yasna|Yasht|Visperad|Chapter)\s+(\d+)\s*\.?\s*</H[1-4]>",
        page, re.I,
    ):
        found.append((m.start(), int(m.group(1))))

    found.sort()
    marks: list[tuple[int, int]] = []
    seen: set[int] = set()
    last = 0
    for pos, chap in found:
        if chap in seen or chap <= last:
            continue
        marks.append((pos, chap))
        seen.add(chap)
        last = chap
    return marks


def _split_verses(text: str) -> dict[int, str]:
    """把「1 詞詞詞 2 詞詞詞」切成 {1: '詞詞詞', 2: '詞詞詞'}。

    只認「空白＋數字＋空白」的裸數字，且節號必須從 1 開始遞增——
    轉寫正文裡不會出現裸阿拉伯數字，但保險起見仍檢查遞增性，
    遇到倒退就當它不是節號（多半是頁碼或註記）。
    """
    verses: dict[int, str] = {}
    parts = re.split(r"(?:(?<=\s)|^)(\d+)\s+", text)
    if len(parts) < 3:
        return verses
    # parts = [前言, '1', 內文, '2', 內文, ...]
    expected = None
    for i in range(1, len(parts) - 1, 2):
        n = int(parts[i])
        chunk = parts[i + 1].strip()
        if expected is not None and n <= expected:
            # 節號倒退：把這一段併回上一節，別開新節
            if expected in verses:
                verses[expected] = f"{verses[expected]} {parts[i]} {chunk}".strip()
            continue
        verses[n] = chunk
        expected = n
    return verses


# ────────────────────────── 書目設定 ──────────────────────────

@dataclass
class BookSpec:
    """一部書怎麼抓。新增書只要加一筆，解析邏輯共用。"""
    key: str
    canon: str
    volume: str
    slug_prefix: str
    siglum_prefix: str
    title_zh: str
    title_en: str
    chapters: range
    en_url: str            # {n} 代入章號
    translit_url: str      # 整書一頁
    en_translator: str
    en_source: str
    chapter_anchor: str = "chapt"
    names: dict[str, str] = field(default_factory=dict)


BOOKS: dict[str, BookSpec] = {
    "vendidad": BookSpec(
        key="vendidad",
        canon="avestan",
        volume="vendidad",
        slug_prefix="vendidad",
        siglum_prefix="Vd",
        title_zh="萬迪達德",
        title_en="Vendidad",
        chapters=range(1, 23),
        en_url=f"{BASE}/vendidad/vd{{n}}sbe.htm",
        translit_url=f"{BASE}/vendidad/vd.htm",
        en_translator="達梅斯特（James Darmesteter）",
        en_source="《東方聖書》第 4 卷，1880／美國版 1898；公有領域",
        names={
            "Ahura Mazda": "阿胡拉‧馬茲達",
            "Angra Mainyu": "安格拉‧曼紐",
            "Zarathushtra": "查拉圖斯特拉",
            "Spitama": "斯皮塔瑪",
            "Airyana Vaeja": "艾里亞納‧瓦埃賈",
            "Yima": "伊瑪",
            "Nasu": "納蘇",
            "daeva": "迭瓦",
        },
    ),
}

# 章題：書目那邊只給禮儀分部，逐章的中文名寫在這裡（本站擬定）
CHAPTER_TITLES: dict[str, dict[int, str]] = {
    "vendidad": {
        1: "十六邦國", 2: "伊瑪的地窖", 3: "大地的悅與不悅", 4: "契約與傷害",
        5: "屍體污染（一）", 6: "屍體污染（二）與寂靜之塔", 7: "屍體污染（三）與醫者",
        8: "屍體的搬運與淨火", 9: "九夜大淨禮（巴爾什農）", 10: "驅魔誦詞",
        11: "各處所的潔淨", 12: "喪期", 13: "犬（上）", 14: "犬（下）與贖罪",
        15: "重罪與棄嬰", 16: "經期婦女", 17: "髮與甲的處置", 18: "假祭司與公雞",
        19: "誘惑查拉圖斯特拉", 20: "特里塔與醫術之始", 21: "雲、雨與諸水",
        22: "阿胡拉求治於曼特拉‧斯彭塔",
    },
}


# ────────────────────────── 抓取與組裝 ──────────────────────────

def get(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=60, headers={"User-Agent": UA})
    r.raise_for_status()
    # avesta.org 多為 latin-1／windows-1252，宣告不一定準；讓 requests 猜再退回 utf-8
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def _normalise_units(orig: dict) -> list[tuple[int, int, str]]:
    """把轉寫的鍵一律正規化成 (起, 訖, 正文)。鍵可以是 int 或 (int, int)。"""
    units: list[tuple[int, int, str]] = []
    for key, text in orig.items():
        if isinstance(key, tuple):
            units.append((key[0], key[1], text))
        else:
            units.append((key, key, text))
    return sorted(units)


def build_chapter(spec: BookSpec, chap: int, en: dict[int, str],
                  orig: dict[tuple[int, int], str] | dict[int, str]) -> dict:
    """把一章的兩欄併成 reader 吃的 JSON。對不齊時留空，不猜。

    轉寫的節號可以是區間（蓋爾德納把數節合成一段）。區間會把它涵蓋的英譯
    各節併成同一列，ref 記作「Vd 12.3-4」——這是編者本來就會做的事。
    區間外的英譯節各自成列。**任何情況下都不按序號硬配對**：那會讓整章
    往下錯一格，而版面完全正常。
    """
    units = _normalise_units(orig)
    covered = {n for s, e, _ in units for n in range(s, e + 1)}
    for n in sorted(set(en) - covered):
        units.append((n, n, ""))
    units.sort()

    segments = []
    for start, end, orig_text in units:
        en_parts = [en[n] for n in range(start, end + 1) if n in en]
        segments.append({
            "chapter": chap,
            "verse": start if start == end else f"{start}-{end}",
            "ref": f"{spec.siglum_prefix} {chap}.{start}"
                   + ("" if start == end else f"-{end}"),
            "orig": orig_text,
            "en": "\n".join(en_parts),
            "zh": "",
        })
    title = CHAPTER_TITLES.get(spec.key, {}).get(chap)
    return {
        "slug": f"{spec.slug_prefix}-{chap:02d}",
        "siglum": f"{spec.siglum_prefix} {chap}",
        "title_zh": f"{spec.title_zh} 第 {chap} 章" + (f"‧{title}" if title else ""),
        "title_en": f"{spec.title_en} {chap}",
        "canon": spec.canon,
        "volume": spec.volume,
        "orig_scheme": "geldner-roman",
        "orig_source": "avesta.org，蓋爾德納校本轉寫（舊式羅馬轉寫）",
        "orig_url": spec.translit_url,
        "en_source": spec.en_source,
        "en_translator": spec.en_translator,
        "en_url": spec.en_url.format(n=chap),
        "licence": "原文轉寫與英譯均取自 avesta.org（Joseph H. Peterson 編）；"
                   "英譯為《東方聖書》舊譯，已入公有領域。繁中為本站自譯。",
        "pivot": "sbe-eng",
        "pivot_note": None,
        "names": spec.names,
        "segments": segments,
    }


def run(spec: BookSpec, only: list[int] | None) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    print(f"[{spec.key}] 抓轉寫整書：{spec.translit_url}")
    translit_all = parse_translit_book(get(session, spec.translit_url), spec.chapter_anchor)
    print(f"[{spec.key}] 轉寫解析出 {len(translit_all)} 章")

    chapters = [c for c in spec.chapters if not only or c in only]
    written = 0
    for chap in chapters:
        url = spec.en_url.format(n=chap)
        try:
            en = parse_sbe_chapter(get(session, url))
        except requests.HTTPError as exc:
            print(f"  ✗ 第 {chap} 章英譯抓不到：{exc}")
            continue
        orig = translit_all.get(chap, {})

        if not en and not orig:
            print(f"  ✗ 第 {chap} 章兩欄都空，跳過")
            continue

        # 坑二：節數不一致要報出來，不可默默併掉
        covered = {n for s, e, _ in _normalise_units(orig) for n in range(s, e + 1)}
        only_en = sorted(set(en) - covered)
        only_orig = sorted(covered - set(en))
        flag = ""
        if only_en or only_orig:
            flag = f"  ⚠ 僅英譯有 {only_en or '—'}／僅轉寫有 {only_orig or '—'}"

        doc = build_chapter(spec, chap, en, orig)
        path = OUT_DIR / f"{doc['slug']}.json"
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        written += 1
        print(f"  ✓ 第 {chap:2d} 章：{len(doc['segments'])} 節"
              f"（英譯 {len(en)}／轉寫 {len(orig)}）{flag}")
        time.sleep(SLEEP)

    print(f"[{spec.key}] 完成，寫出 {written} 章 → {OUT_DIR}")
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="祆教經典取源")
    ap.add_argument("book", nargs="?", help="書名 key，見 --list")
    ap.add_argument("--only", nargs="*", type=int, help="只抓這幾章")
    ap.add_argument("--list", action="store_true", help="列出已實作的書")
    args = ap.parse_args()

    if args.list or not args.book:
        print("已實作：")
        for k, v in BOOKS.items():
            print(f"  {k:12s} {v.title_zh}（{len(list(v.chapters))} 章）")
        return 0

    spec = BOOKS.get(args.book)
    if not spec:
        print(f"未知的書：{args.book}（--list 看清單）", file=sys.stderr)
        return 1
    run(spec, args.only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
