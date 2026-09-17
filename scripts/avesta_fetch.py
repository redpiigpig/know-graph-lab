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

# Windows 主控台預設 cp950，印 ✓ ✗ ⚠ 會讓整支在「已經抓完寫完」之後才炸掉——
# 看起來像抓取失敗，其實檔案已經寫好了。這類假失敗最浪費時間，故一律先設好編碼。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
    # 起始值是 -1 不是 0。亞什特各首都有「第 0 節」（開誦前的禮儀引文），
    # 起始給 0 的話第 0 節會被 _absorb_verses 的「節號不得倒退」規則當成
    # 重複而丟掉——少一節，而頁面完全正常。
    last = -1

    # 🚨 **第一個 <TD> 之前的那一段也是經文，不可以跳過。**
    #    整書頁把章標題與接下來的頭幾節放在同一個 <TD> 裡，
    #    而本函式收到的章塊是從標題錨點之後切起的——於是那個 <TD> 的開頭
    #    落在章塊之外，只認 <TD> 的話開頭幾節整段消失。
    #    實測：亞斯納第 31 章（伽薩‧道路的詰問）23 節只抓到 1 節，
    #    第 1–3 節就是這樣掉的；全書有 18 章中招，而每一章都照樣寫出檔案。
    head = re.split(r"<TD\b", page, maxsplit=1, flags=re.I)[0]
    head_text = strip_tags(head)
    if head_text:
        last = _absorb_verses(head_text, verses, last)

    # 逐個 TD 切；經文欄的特徵是不帶 CLASS="NOTE"
    # 🚨 結尾的 `|$` 不可省。章塊是從標題錨點切到下一個標題錨點，
    #    最後一個 <TD> 的 </TD></TR> 往往落在切點之外——沒有 $ 這個出口，
    #    那一格**整格比對失敗而被跳過**，不是少幾個字而是少一整段。
    #    實測：亞斯納第 31 章的第 5–22 節（23 節裡的 18 節）就這樣不見，
    #    而檔案照寫、前 4 節好端端的，看起來只像「後面沒譯」。
    for m in re.finditer(r"<TD\b([^>]*)>(.*?)(?=<TD\b|</TR>|</TABLE>|$)", page, re.I | re.S):
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

    if not verses:
        # 🚨 avesta.org 的英譯頁有**兩種版型**，這件事第一版沒發現：
        #      萬迪達德  兩欄表格（經文欄＋ CLASS="NOTE" 腳註欄）
        #      亞什特    <DL COMPACT><DT>N.<DD>正文  定義列表，沒有表格
        #    只認表格的話，亞什特全部 21 首的英譯欄都會是空的——
        #    而檔案照樣寫出、頁面照樣顯示、轉寫欄還好端端的，
        #    看起來只是「這幾首剛好沒英譯」。實際上是解析器沒認出版型。
        #    （實測：第 1 首轉寫 34 節、英譯 0 節，就是這個原因。）
        for (start, _end), text in _parse_definition_list(page).items():
            verses[start] = text

    if not verses:
        # 🚨 第三種版型：連定義列表都沒有，就是一連串 <P>N. 正文</P>
        #    （第 9 首 Gosh Yasht 是這一型，那一頁還是改版過的新版面）。
        #    三種版型都要試過才能說「這一首沒有英譯」——
        #    只試一種就下結論，會把「解析器不認得」誤報成「來源沒有」。
        #
        # 🚨🚨 而且**必須先把大標題拿掉**。這一頁的 <H2> 是
        #      「9. GOSH YASHT (Drvasp Yasht).」——它長得跟節號一模一樣。
        #      不拿掉的話 _absorb_verses 會先讀到 n=9 把 last 推到 9，
        #      接著真正的第 0–8 節因為「節號不得倒退」全部被併進第 9 節，
        #      結果是 34 節的一首只剩 24 節，而且**開頭那幾節的內容還被黏在第 9 節裡**。
        #      實測就是這樣掉了 9 節，頁面照樣好看。
        _absorb_verses(strip_tags(_drop_page_headings(page)), verses, -1)
    return verses


def _drop_page_headings(page: str) -> str:
    """去掉 <TITLE> 與 <H1>／<H2> 大標題。

    avesta.org 的篇名格式是「10. Mihr Yasht」——與節號同形，
    留著會被當成節號。<H3> 不動：那是段落標記（[1]、[2] 的 karda 分節），
    不含「數字＋句點」的形式，且拿掉會丟失章節分界資訊。

    >>> _drop_page_headings('<H2>9. GOSH YASHT.</H2><P>0. May Ahura')
    ' <P>0. May Ahura'
    """
    out = re.sub(r"<TITLE\b[^>]*>.*?</TITLE>", " ", page, flags=re.I | re.S)
    return re.sub(r"<H[12]\b[^>]*>.*?</H[12]>", " ", out, flags=re.I | re.S)


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
        # 🚨 同一段裡還可能藏著**排在句中**的節號。米爾斯把亞斯納的儀節章
        #    排成連續散文，第 2 節接在第 1 節句末後面（「…Hadhanaepata. 2. And, as…」），
        #    不換行。只認行首的話，27 節的一章只會抓到 2 節——
        #    而檔案照寫、頁面照常顯示，看起來像「這一章大半沒譯」。
        n, chunk = _split_inline_verses(n, chunk, verses)
        verses[n] = f"{verses[n]}\n{chunk}" if n in verses else chunk
        last = n
    return last


def _split_inline_verses(n: int, chunk: str, verses: dict[int, str]) -> tuple[int, str]:
    """把一段裡句中出現的後續節號切出來，塞進 verses，回 (最後節號, 該節正文)。

    🚨 **只認「剛好是下一號」的**。句中的數字太多了（年份、數量、互見），
       放寬成「任何比目前大的數字」會把正文切得七零八落，而且看不出來。
       限定 n+1 等於是要求它接得上序列，誤判的機會極低。
    """
    while True:
        m = re.search(rf"(?<=[.!?])\s+{n + 1}\.\s+", chunk)
        if not m:
            return n, chunk.strip()
        verses[n] = chunk[:m.start()].strip()
        chunk = chunk[m.end():]
        n += 1


def parse_sbe_book(page: str, chapter_anchor: str = "chapt") -> dict[int, dict[int, str]]:
    """解析 avesta.org 的英譯**整書**頁（維斯帕拉德 vrsbe.htm 是這一型），回 {章: {節: 英譯}}。

    章界沿用 _chapter_marks（錨點與標題兩種都收）。切出章塊後先用表格解析
    （SBE 頁多為經文欄＋腳註欄的兩欄表），表格解不出東西時退回裸文字切節。

    🚨 為什麼不直接整頁切節：整書頁的節號**每章都從 1 重來**。
       整頁一次切的話後面各章的第 1 節會覆蓋前面的，而總節數看起來仍然很多，
       完全看不出內容錯位。一定要先切章。
    """
    out: dict[int, dict[int, str]] = {}
    marks = _chapter_marks(page, chapter_anchor)
    for i, (start, chap) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(page)
        chunk = page[start:end]
        verses = parse_sbe_chapter(chunk)
        if not verses:
            verses = {}
            _absorb_verses(strip_tags(chunk), verses, 0)
        out[chap] = verses
    return out


# 互見有兩種寫法，兩種都要認：
#   (See Y61.)                                   ← 多數章
#   (This chapter is identical with Yasna 37. )   ← 第 5 章
# 只認第一種的話，第 5 章的英譯欄會空著而且沒有任何說明，
# 看起來就是抓取失敗。
XREF = re.compile(
    r"\([^)]*(?:see|identical with)\s+Y(?:asna)?[\s.]*\d[^)]*\)", re.I)


def parse_sbe_xrefs(page: str, chapter_anchor: str = "chapt") -> dict[int, str]:
    """抓出英譯整書頁裡「本章不另譯，見某章」的互見說明，回 {章: 說明}。

    🚨 這不是可有可無的裝飾。米爾斯的《東方聖書》譯本對亞斯納後段
       （63、64、67、69、72 等）根本沒有另譯，原頁面只寫一句「(See Y61.)」。
       不收的話那幾章的英譯欄是空的，看起來像**抓取失敗**；
       收了才看得出那是**譯本本來就沒有**，而且指得出去哪裡找。
       兩者在版面上長得一模一樣，差別只在讀者會不會以為站壞了。
    """
    out: dict[int, str] = {}
    marks = _chapter_marks(page, chapter_anchor)
    for i, (start, chap) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(page)
        hits = XREF.findall(strip_tags(page[start:end]))
        if hits:
            out[chap] = " ".join(dict.fromkeys(hits))
    return out


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
    #
    # 🚨 標題的寫法在同一個站上有四種，四種都要認：
    #      <H3>Fargard 1.</H3>                              萬迪達德
    #      <H3>YASNA - Chapter 1. </H3>                      亞斯納轉寫（書名 - 章）
    #      <H3><A NAME="chapter3">YASNA - Chapter 3. </A></H3>  同上但包在錨點裡
    #      <H3>0. Introduction </H3>                          亞斯納第 0 章
    #    只認第一種時，亞斯納 12 個轉寫頁會「解析出 0 章」——
    #    而腳本不報錯、照樣把英譯欄寫滿，只是轉寫欄全空（維斯帕拉德就是這樣）。
    for m in re.finditer(
        r"<H[1-4]\b[^>]*>(?:\s*<A\b[^>]*>)?\s*"
        r"(?:[A-Z]{3,10}\s*[-–—]\s*)?"
        r"(?:Fargard|Yasna|Yasht|Visperad|Chapter|Ha)\s+(\d+)\s*\.?\s*",
        page, re.I,
    ):
        found.append((m.start(), int(m.group(1))))
    # 「0. Introduction」這種「數字＋句點＋詞」的章標題，只在 <H2>/<H3> 裡認，
    # 且數字必須是行首——否則正文裡的節號會被當成章界。
    for m in re.finditer(
        r"<H[23]\b[^>]*>(?:\s*<A\b[^>]*>)?\s*(\d{1,2})\.\s+[A-Z]", page, re.I,
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
    # avesta.org 的頁型不只一種，三個旗標對應三種實際存在的排法：
    #   萬迪達德  轉寫整書一頁、英譯逐章一頁          （兩者皆 False）
    #   亞什特    轉寫逐章一頁、英譯逐章一頁          （translit_per_chapter）
    #   維斯帕拉德 轉寫整書一頁、英譯**整書一頁**      （en_whole_book）
    # 猜錯頁型的後果不是報錯，是抓到空的或抓到別章的內容，而版面完全正常。
    translit_per_chapter: bool = False
    en_whole_book: bool = False
    # 第四種頁型：轉寫**散在多頁、每頁涵蓋一段章次**（亞斯納是這一型：
    # y0to8.htm、y9to11.htm、y28to34.htm…共 12 頁涵蓋 0–72 章）。
    # 設了這個就不讀 translit_url，改逐頁抓、各自切章後合併。
    translit_pages: list[str] = field(default_factory=list)
    # 篇章的量詞。祆教各書的單位不同：萬迪達德分「章」（法爾迦爾德）、
    # 亞什特分「首」。寫死成「章」會讓亞什特的篇名變成「亞什特 第 10 章」，
    # 與書目頁的「第 10 首」對不起來。
    unit: str = "章"


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
    "yasna": BookSpec(
        key="yasna",
        canon="avestan",
        volume="yasna",
        slug_prefix="yasna",
        siglum_prefix="Y",
        title_zh="亞斯納",
        title_en="Yasna",
        chapters=range(1, 73),
        # 🚨 英譯**整本都在 yasna.htm 這一頁**（米爾斯譯，表格版型，錨點 id=yN）。
        #    舊的逐段英譯頁（y0to8s.htm 等）現在只剩一句「LINK MOVED.」的殼——
        #    抓它會得到 1,184 bytes 的空頁而不報錯。
        en_url=f"{BASE}/yasna/yasna.htm",
        en_whole_book=True,
        chapter_anchor="y",
        # 轉寫散在 12 頁，每頁涵蓋一段章次。
        translit_url=f"{BASE}/yasna/y0to8.htm",
        translit_pages=[
            f"{BASE}/yasna/y0to8.htm",
            f"{BASE}/yasna/y9to11.htm",
            f"{BASE}/yasna/y12.htm",
            f"{BASE}/yasna/y13to27.htm",
            f"{BASE}/yasna/y28to34.htm",
            f"{BASE}/yasna/y35to42.htm",
            f"{BASE}/yasna/y43to46.htm",
            f"{BASE}/yasna/y47to50.htm",
            f"{BASE}/yasna/y51.htm",
            f"{BASE}/yasna/y52.htm",
            f"{BASE}/yasna/y53.htm",
            f"{BASE}/yasna/y54to72.htm",
        ],
        en_translator="米爾斯（L. H. Mills）",
        en_source="《東方聖書》第 31 卷，1887；公有領域",
        names={
            "Ahura Mazda": "阿胡拉‧馬茲達",
            "Angra Mainyu": "安格拉‧曼紐",
            "Zarathushtra": "查拉圖斯特拉",
            "Spitama": "斯皮塔瑪",
            "Amesha Spenta": "阿姆沙‧斯彭塔",
            "Vohu Mano": "沃胡‧馬納",
            "Asha Vahishta": "阿沙‧瓦希什塔",
            "Khshathra Vairya": "赫沙特拉‧瓦伊里亞",
            "Spenta Armaiti": "斯彭塔‧阿爾邁提",
            "Haurvatat": "豪爾瓦塔特",
            "Ameretat": "阿梅雷塔特",
            "Haoma": "豪麻",
            "Sraosha": "斯魯沙",
            "fravashi": "弗拉瓦希",
            "daeva": "迭瓦",
            "yazata": "雅扎塔",
        },
    ),
    "yasht": BookSpec(
        key="yasht",
        canon="avestan",
        volume="yasht",
        slug_prefix="yasht",
        siglum_prefix="Yt",
        title_zh="亞什特",
        title_en="Yasht",
        unit="首",
        chapters=range(1, 22),
        en_url=f"{BASE}/ka/yt{{n}}sbe.htm",
        translit_url=f"{BASE}/ka/yt{{n}}.htm",
        translit_per_chapter=True,
        en_translator="達梅斯特（James Darmesteter）",
        en_source="《東方聖書》第 23 卷，1883；公有領域",
        names={
            "Ahura Mazda": "阿胡拉‧馬茲達",
            "Angra Mainyu": "安格拉‧曼紐",
            "Zarathushtra": "查拉圖斯特拉",
            "Spitama": "斯皮塔瑪",
            "Mithra": "密特拉",
            "Anahita": "阿娜希塔",
            "Tishtrya": "提什特里亞",
            "Verethraghna": "韋雷特拉格納",
            "Vayu": "瓦尤",
            "Rashnu": "拉什努",
            "Sraosha": "斯魯沙",
            "fravashi": "弗拉瓦希",
            "khvarenah": "赫瓦雷納",
            "daeva": "迭瓦",
            "yazata": "雅扎塔",
        },
    ),
    "visperad": BookSpec(
        key="visperad",
        canon="avestan",
        volume="visperad",
        slug_prefix="visperad",
        siglum_prefix="Vr",
        title_zh="維斯帕拉德",
        title_en="Visperad",
        chapters=range(1, 25),
        # 🚨 本書兩欄都是「整書一頁」，而且英譯頁的錨點是 chap 不是 chapt。
        en_url=f"{BASE}/visperad/vrsbe.htm",
        en_whole_book=True,
        # 🚨 別用 vr_tc.htm——那是**目次頁**（Table of Contents），不是正文。
        #    抓它不會報錯：頁面在、解析器跑完、寫出 23 個檔，只是轉寫欄全空。
        #    正文在 visperad.htm（238 個 DT/DD 條目）。
        translit_url=f"{BASE}/visperad/visperad.htm",
        chapter_anchor="chap",
        en_translator="達梅斯特（James Darmesteter）",
        en_source="《東方聖書》第 31 卷，1887；公有領域",
        names={
            "Ahura Mazda": "阿胡拉‧馬茲達",
            "Zarathushtra": "查拉圖斯特拉",
            "Amesha Spenta": "阿姆沙‧斯彭塔",
            "ratu": "拉圖",
            "yazata": "雅扎塔",
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
    # 🚨 這些名字必須與 data/avesta/avestan.ts 書目裡的一致。
    #    書目那邊未命名的章一律作「亞斯納 第 N 章」，build_chapter 會自動產生同樣的字串，
    #    所以這裡只列有專名的 46 章。
    "yasna": {
        1: "呼名獻祭", 8: "肉供與信眾分食", 9: "豪麻讚（上）", 10: "豪麻讚（中）", 11: "豪麻讚（下）", 12: "信仰宣示",
        19: "阿胡納‧瓦伊里亞釋義", 20: "阿舍姆‧沃胡釋義", 21: "燕赫‧哈坦釋義", 28: "伽薩‧祈求聆聽", 29: "伽薩‧牛魂的哀訴",
        30: "伽薩‧兩靈", 31: "伽薩‧道路的詰問", 32: "伽薩‧斥迭瓦與其祭司", 33: "伽薩‧先知的獻身", 34: "伽薩‧求得永生",
        35: "七章禱‧讚阿胡拉與不朽聖者", 36: "七章禱‧向阿胡拉與火", 37: "七章禱‧向聖造與弗拉瓦希", 38: "七章禱‧向大地與聖水",
        39: "七章禱‧向牛魂", 40: "七章禱‧求助佑", 41: "七章禱‧向阿胡拉為王", 42: "七章禱補遺", 43: "伽薩‧幸福歸於",
        44: "伽薩‧二十問", 45: "伽薩‧我要宣講", 46: "伽薩‧我往何處去", 47: "伽薩‧豐饒之靈", 48: "伽薩‧真理勝虛妄",
        49: "伽薩‧斥敵者", 50: "伽薩‧我魂何依", 51: "伽薩‧善的王權", 52: "求聖潔與其果報", 53: "伽薩‧最好的願望", 54: "艾里亞曼禱",
        56: "斯魯沙讚前引", 57: "斯魯沙讚", 58: "繁盛頌詞", 59: "互祝", 62: "火讚", 65: "向阿爾德維‧蘇拉‧阿娜希塔與諸水",
        66: "向阿胡拉之女（水）", 70: "向不朽聖者與教制", 71: "祭典將畢", 72: "結祭",
    },
    # 🚨 這 21 個名字必須與 data/avesta/avestan.ts 書目裡的一致。
    #    兩邊不一致時，書目頁與 reader 會顯示不同的篇名——而兩邊都不會報錯。
    "yasht": {
        1: "阿胡拉‧馬茲達讚", 2: "七不朽聖者讚", 3: "阿沙‧瓦希什塔讚",
        4: "豪爾瓦塔特讚", 5: "阿娜希塔讚（水神讚）", 6: "太陽讚", 7: "月讚",
        8: "提什特里亞讚（天狼星讚）", 9: "德爾瓦斯帕讚（牲畜守護讚）",
        10: "密特拉讚", 11: "斯魯沙讚", 12: "拉什努讚", 13: "弗拉瓦希讚",
        14: "韋雷特拉格納讚（勝利神讚）", 15: "瓦尤讚（風神讚）",
        16: "奇斯塔讚（宗教女神讚）", 17: "阿希讚（福運女神讚）",
        18: "阿什塔德讚", 19: "扎姆亞德讚（王者神光讚）", 20: "瓦南特讚",
        21: "豪麻讚（亞什特本）",
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
                  orig: dict[tuple[int, int], str] | dict[int, str],
                  en_xref: str = "") -> dict:
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
        "title_zh": f"{spec.title_zh} 第 {chap} {spec.unit}" + (f"‧{title}" if title else ""),
        "title_en": f"{spec.title_en} {chap}",
        "canon": spec.canon,
        "volume": spec.volume,
        "orig_scheme": "geldner-roman",
        "orig_source": "avesta.org，蓋爾德納校本轉寫（舊式羅馬轉寫）",
        "orig_url": (spec.translit_url.format(n=chap) if spec.translit_per_chapter
                     else _translit_page_of(spec, chap)),
        "en_source": spec.en_source,
        "en_translator": spec.en_translator,
        "en_url": spec.en_url if spec.en_whole_book else spec.en_url.format(n=chap),
        "licence": "原文轉寫與英譯均取自 avesta.org（Joseph H. Peterson 編）；"
                   "英譯為《東方聖書》舊譯，已入公有領域。繁中為本站自譯。",
        "pivot": "sbe-eng",
        # 本章英譯只有互見、沒有正文時，把那句互見寫在版面上。
        # 空白的英譯欄看起來像抓取失敗，「見 Y 61」才看得出是譯本本來就沒有。
        "pivot_note": (
            f"米爾斯的《東方聖書》譯本未另譯本章，原書註明 {en_xref}。"
            f"英譯欄因此從缺——這是譯本的處理方式，不是本站漏抓。"
            if en_xref and not en else None
        ),
        "names": spec.names,
        "segments": segments,
    }


def _translit_page_of(spec: "BookSpec", chap: int) -> str:
    """多頁轉寫時，回傳這一章所屬的那一頁網址；單頁書就回本來的 translit_url。

    網址裡的 yNtoM 就是它涵蓋的章次區間，直接讀出來用，不另外維護一張對照表
    （對照表會跟網址不同步，而不同步時看不出來）。
    """
    if not spec.translit_pages:
        return spec.translit_url
    for url in spec.translit_pages:
        name = url.rsplit("/", 1)[-1].removesuffix(".htm")
        m = re.fullmatch(r"y(\d+)to(\d+)", name)
        if m and int(m.group(1)) <= chap <= int(m.group(2)):
            return url
        if re.fullmatch(rf"y{chap}", name):
            return url
    return spec.translit_pages[0]


def _carry_over_zh(path: Path, doc: dict) -> int:
    """重抓時把既有的繁中譯文搬回新檔，回傳搬了幾段。

    🚨 **沒有這一步，重抓一次就會洗掉全部譯文。**
       build_chapter 產出的 zh 一律是空字串（它只管原文與英譯兩欄），
       所以「為了修一個解析 bug 而重抓某一章」會靜靜地把那一章的中譯清空——
       檔案照樣寫出、頁面照樣顯示，只是中文欄變成一排「—」。
       萬迪達德 22 章 830 段的中譯就是這樣一次可以全丟掉。

    以 ref 為鍵搬移，不以索引：重抓後節數可能變（正是重抓的理由），
    按位置搬會讓譯文整段錯位——那比清空更糟，因為看不出來。
    """
    if not path.exists():
        return 0
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    prev = {s.get("ref"): s.get("zh", "") for s in old.get("segments", [])}
    kept = 0
    for seg in doc["segments"]:
        zh = prev.get(seg["ref"], "")
        if zh:
            seg["zh"] = zh
            kept += 1
    return kept


def run(spec: BookSpec, only: list[int] | None) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    translit_all: dict[int, dict] = {}
    if spec.translit_pages:
        for url in spec.translit_pages:
            part = parse_translit_book(get(session, url), spec.chapter_anchor)
            # 🚨 各頁的章次不重疊；真重疊代表切章規則抓錯了，要吵出來而不是靜靜覆蓋。
            dupes = sorted(set(part) & set(translit_all))
            if dupes:
                print(f"  ⚠ {url} 與前面各頁章次重疊：{dupes}（切章規則可能有誤）")
            translit_all.update(part)
            print(f"  · {url.rsplit('/', 1)[-1]:16s} 解析出 {len(part)} 章 {sorted(part)}")
            time.sleep(SLEEP)
        print(f"[{spec.key}] 轉寫共 {len(translit_all)} 章")
    elif not spec.translit_per_chapter:
        print(f"[{spec.key}] 抓轉寫整書：{spec.translit_url}")
        translit_all = parse_translit_book(get(session, spec.translit_url), spec.chapter_anchor)
        print(f"[{spec.key}] 轉寫解析出 {len(translit_all)} 章")

    en_all: dict[int, dict[int, str]] = {}
    en_xrefs: dict[int, str] = {}
    if spec.en_whole_book:
        print(f"[{spec.key}] 抓英譯整書：{spec.en_url}")
        en_page = get(session, spec.en_url)
        en_all = parse_sbe_book(en_page, spec.chapter_anchor)
        en_xrefs = parse_sbe_xrefs(en_page, spec.chapter_anchor)
        print(f"[{spec.key}] 英譯解析出 {len(en_all)} 章"
              + (f"，其中 {sum(1 for c, v in en_all.items() if not v and en_xrefs.get(c))} 章只有互見" if en_xrefs else ""))

    chapters = [c for c in spec.chapters if not only or c in only]
    written = 0
    for chap in chapters:
        if spec.en_whole_book:
            en = en_all.get(chap, {})
        else:
            url = spec.en_url.format(n=chap)
            try:
                en = parse_sbe_chapter(get(session, url))
            except requests.HTTPError as exc:
                # 🚨 英譯缺一章不代表整章要放棄：亞什特第 20 首就是沒有 SBE 英譯的
                #    （韋斯特未收）。轉寫仍然抓得到，照寫，英譯欄留空。
                #    這裡若 continue，那一首會連書目都對不上而整章消失。
                print(f"  · 第 {chap} 章無英譯（{exc.response.status_code if exc.response is not None else '?'}），只寫轉寫")
                en = {}

        if spec.translit_per_chapter:
            turl = spec.translit_url.format(n=chap)
            try:
                orig = _parse_definition_list(get(session, turl))
            except requests.HTTPError as exc:
                print(f"  ✗ 第 {chap} 章轉寫抓不到：{exc}")
                orig = {}
            time.sleep(SLEEP)
        else:
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

        doc = build_chapter(spec, chap, en, orig, en_xrefs.get(chap, ""))
        path = OUT_DIR / f"{doc['slug']}.json"
        kept = _carry_over_zh(path, doc)
        if kept:
            flag += f"  ↻ 保留既有中譯 {kept} 段"
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
