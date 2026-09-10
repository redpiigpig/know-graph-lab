# -*- coding: utf-8 -*-
"""archive.org `_djvu.xml` → 帶**真印刷頁碼**與**註腳**的行／段。

為什麼要這一支：全集那條線既有的 archive.org 取源（`mueller_auto.fetch_djvu`）讀的是
`_djvu.txt`——那份文字沒有頁界、沒有幾何，所以它只能把書眉與頁碼**當雜訊丟掉**，
`page_number` 一律填 None。使用者 2026-09-09 定調轉錄必須帶得回原書頁碼與註釋
（[[feedback_transcribe_page_numbers]]、[[feedback_transcribe_notes_and_bibliography]]），
`_djvu.txt` 這條路就走不通了。`_djvu.xml` 保留了逐頁、逐行、逐字的座標，頁碼與註腳
都能從版面幾何撈回來。

座標格式：`coords="left,bottom,right,top,baseline"`，y 由頁面上緣往下遞增
（所以 bottom > top，字高 = bottom - top）。

三件事，都是純函式，測試在 scripts/tests/test_archive_djvu.py：

  folio_of()    書眉那一區撈印刷頁碼。頁碼可能自成一行（1924 年那刷），也可能
                黏在書眉字串的頭或尾（1923 年那刷）。羅馬頁碼原樣回傳字串。
  split_notes() 頁末那一串註腳與正文切開。判準是**三個條件同時成立**，不是任一：
                字高不大於正文、前面有異常大的行距、開頭是註腳記號。少任何一個
                都會把正文末段誤判成註腳（掃描歪斜會讓行距忽大忽小）。
  reflow()      斷詞接回、空白正規化、依**局部**首行縮排切段。局部是關鍵——
                掃描頁往往整頁傾斜，同一頁左緣可以漂移一百多個單位，拿全頁
                最小 x0 當基準會把後半頁每一行都判成新段落。
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from statistics import median

# 註腳記號：阿拉伯數字、星號、劍號，以及 OCR 把上標數字認成的那幾個符號。
_NOTE_MARK = re.compile(r"^\s*(?:[0-9]{1,2}|[*†‡§¶^■»]|[\[(]\s*[0-9]{1,2}\s*[\])])[\s.)]")
_ROMAN = re.compile(r"^[ivxlcdm]+$", re.I)
_ARABIC = re.compile(r"^[0-9]{1,4}$")
# OCR 常把頁碼旁的髒點一起吃進來（"20." "[21]" "‘22’"）
_STRIP = " .,:;'’‘\"“”()[]{}|/\\-—–_*"


# ── 解析 ─────────────────────────────────────────────────────────────────────

def parse_pages(xml_path: str | Path) -> list[list[dict]]:
    """`_djvu.xml` → 每個掃描頁一份 line dict 清單（依版面由上而下）。

    line dict：text / top / bottom / h（字高）/ x0 / x1。
    iterparse + clear()：這種 xml 動輒五到十 MB，整棵樹讀進來沒必要。
    """
    pages: list[list[dict]] = []
    for _ev, el in ET.iterparse(str(xml_path), events=("end",)):
        if el.tag != "OBJECT":
            continue
        pages.append(_lines_of(el))
        el.clear()
    return pages


def _lines_of(obj) -> list[dict]:
    lines: list[dict] = []
    for ln in obj.iter("LINE"):
        words, tops, bots, xs = [], [], [], []
        for w in ln.iter("WORD"):
            parts = (w.get("coords") or "").split(",")
            if len(parts) >= 4:
                try:
                    x1, yb, x2, yt = (int(float(v)) for v in parts[:4])
                except ValueError:
                    pass
                else:
                    tops.append(yt); bots.append(yb); xs += [x1, x2]
            if w.text:
                words.append(w.text)
        text = " ".join(words).strip()
        if not text:
            continue
        lines.append({
            "text": text,
            "top": min(tops) if tops else 0,
            "bottom": max(bots) if bots else 0,
            "h": (max(bots) - min(tops)) if tops else 0,
            "x0": min(xs) if xs else 0,
            "x1": max(xs) if xs else 0,
        })
    lines.sort(key=lambda d: d["top"])
    return lines


# ── 印刷頁碼 ─────────────────────────────────────────────────────────────────

def _as_folio(tok: str) -> str | None:
    t = tok.strip(_STRIP)
    if _ARABIC.match(t):
        return t
    if _ROMAN.match(t) and len(t) <= 7:
        return t.lower()
    return None


def head_lines(lines: list[dict]) -> list[dict]:
    """書眉區那幾行。界線拿**行距**算，不拿頁高比例算——頁高比例對只有幾行的頁
    （扉頁、部名頁）會把書眉區壓成零。"""
    if not lines:
        return []
    tops = sorted(ln["top"] for ln in lines)
    gaps = [b - a for a, b in zip(tops, tops[1:])]
    if not gaps:
        return list(lines)
    band = tops[0] + 0.6 * median(gaps)
    return [ln for ln in lines if ln["top"] <= band]


def strip_head(lines: list[dict]) -> list[dict]:
    """🚨 書眉要從正文裡拿掉。撈完頁碼就以為事情結束了，會讓「MYSTERIUM
    TREMENDUM 20」黏在該頁第一段的最前面——每一頁都黏一次，中英對照兩邊
    段落數還是一樣多，頁面完全正常，只是每段開頭多一截書眉。"""
    if len(lines) <= 2:
        return lines
    head = {id(ln) for ln in head_lines(lines)}
    body = [ln for ln in lines if id(ln) not in head]
    return body or lines


def folio_of(lines: list[dict]) -> str | None:
    """從書眉區撈印刷頁碼；撈不到回 None（**絕不用流水號頂替**）。

    書眉區的界線不拿頁高比例算，而拿**行距**算：最上緣那一行，加上不到一個行距的
    容許量。頁高比例對整頁滿版的頁面沒問題，對只有幾行的頁（扉頁、部名頁）會把
    書眉區壓成零。

    頁碼要嘛自成一行，要嘛黏在書眉字串的頭或尾。黏在字串裡的只收阿拉伯數字——
    「Chapter III」的 III 是章號不是頁碼，羅馬數字只在整行就是頁碼時才認。
    """
    head = head_lines(lines)
    if not head:
        return None
    for ln in head:                      # 整行就是頁碼（阿拉伯或羅馬）
        f = _as_folio(ln["text"])
        if f:
            return f
    for ln in head:                      # 黏在書眉字串頭尾（只收阿拉伯）
        toks = ln["text"].split()
        if len(toks) < 2:
            continue
        for tok in (toks[0], toks[-1]):
            f = _as_folio(tok)
            if f and f.isdigit():
                return f
    return None


def folio_int(folio: str | None) -> int | None:
    """'21'→21；'xii'→None。羅馬頁碼進不了整數欄，寧可留 None——序言的 xii
    與正文的 12 是不同的兩頁，混在一起比沒有頁碼更糟。"""
    return int(folio) if folio and folio.isdigit() else None


def fill_folios(raw: list[str | None]) -> list[str | None]:
    """書眉沒印頁碼的頁（章首頁、插圖頁）由鄰頁遞推。

    先順推再逆推：一節的第一頁多半就是章首頁，只能由下一頁減一。
    羅馬頁碼不做算術（xii 減一不是 xi 這麼簡單，而且序言與正文各自從 1 起算）。
    """
    out = list(raw)
    for i in range(1, len(out)):
        if out[i] is None and (n := folio_int(out[i - 1])) is not None:
            out[i] = str(n + 1)
    for i in range(len(out) - 2, -1, -1):
        if out[i] is None and (n := folio_int(out[i + 1])) is not None and n > 1:
            out[i] = str(n - 1)
    return out


# ── 註腳 ─────────────────────────────────────────────────────────────────────

def split_notes(lines: list[dict], gap_factor: float = 1.20,
                height_factor: float = 1.02) -> tuple[list[dict], list[dict]]:
    """(正文行, 註腳行)。抓不到註腳就回 (全部, [])。

    只認**頁末連續**的那一串，且三個條件同時成立：
      1. 起頭那一行前面的行距 ≥ 一般行距 × gap_factor（註腳橫線佔掉的空間；
         實測奧托那本只多出三成，門檻設一點三五會整頁漏掉）
      2. 該串的字高不大於正文中位數 × height_factor（註腳是小字）
      3. 起頭那一行以註腳記號開頭
    """
    if len(lines) < 4:
        return lines, []
    gaps = [lines[i]["top"] - lines[i - 1]["top"] for i in range(1, len(lines))]
    if not gaps:
        return lines, []
    gap_med = median(gaps)
    h_med = median([ln["h"] for ln in lines if ln["h"] > 0] or [1])
    # 由後往前找最靠後、且行距夠大的斷點；只在頁面下半部找
    page_bottom = max(ln["bottom"] for ln in lines) or 1
    for i in range(len(lines) - 1, 0, -1):
        if lines[i]["top"] < page_bottom * 0.55:
            break
        if gaps[i - 1] < gap_med * gap_factor:
            continue
        tail = lines[i:]
        if not _NOTE_MARK.match(tail[0]["text"]):
            continue
        if median([ln["h"] for ln in tail if ln["h"] > 0] or [h_med]) > h_med * height_factor:
            continue
        return lines[:i], tail
    return lines, []


# ── 重排 ─────────────────────────────────────────────────────────────────────

_WS = re.compile(r"\s+")
_HYPHEN_EOL = re.compile(r"([A-Za-zÄÖÜäöüß])[-‐‑–]$")


def normalize(text: str) -> str:
    """OCR 逐字輸出的空白很亂（1924 那刷字距被切成兩個空白），先壓平。"""
    t = _WS.sub(" ", text).strip()
    t = t.replace(" ,", ",").replace(" .", ".").replace(" ;", ";").replace(" ?", "?")
    t = t.replace(" ’", "’").replace("‘ ", "‘").replace(" !", "!")
    return t


def is_indented(lines: list[dict], i: int, window: int = 1, thresh: int = 45,
                max_indent: int = 220) -> bool:
    """第 i 行是不是段落首行——跟**鄰近幾行**的左緣比，不是跟全頁比。

    掃描頁常整頁傾斜，左緣自上而下可以漂一百多個單位；拿全頁最小 x0 當基準，
    後半頁會每一行都被判成新段落。窗口預設只看緊鄰的上下各一行——傾斜每行只漂
    一兩個單位，縮排卻有八九十，窗口愈小分得愈開。縮排另有上界，見內文。
    """
    lo = max(0, i - window)
    hi = min(len(lines), i + window + 1)
    others = [lines[j]["x0"] for j in range(lo, hi) if j != i]
    if not others:
        return False
    delta = lines[i]["x0"] - min(others)
    # 🚨 縮排是有上界的。OCR 常把同一條印刷行拆成兩筆 LINE，後半截的 x0 動輒
    # 右移五百到一千九——那不是段落縮排，是同一行的下半截。真正的首行縮排在
    # 600dpi 下大約是一個 em，八九十個單位。沒有上界的話，每一個 OCR 碎片都會
    # 變成一個新段落，段落數一多，中英兩欄就對不起來了。
    return thresh < delta <= max_indent


def _same_printed_line(lines: list[dict], i: int, med_gap: float) -> bool:
    """第 i 筆跟上一筆其實是同一條印刷行——OCR 把一行拆成兩筆時，兩筆的 top
    幾乎相同。這種碎片絕不可以當成新段落。"""
    if i == 0 or med_gap <= 0:
        return False
    return (lines[i]["top"] - lines[i - 1]["top"]) < med_gap * 0.5


def reflow(lines: list[dict], indent_thresh: int = 45) -> list[str]:
    """行 → 段。斷詞接回、首行縮排切段。"""
    tops = [ln["top"] for ln in lines]
    gaps = [b - a for a, b in zip(tops, tops[1:]) if b - a > 0]
    med_gap = median(gaps) if gaps else 0
    paras: list[list[str]] = []
    for i, ln in enumerate(lines):
        text = ln["text"]
        # 🚨 上一行以連字號收尾＝這一行是同一個字的下半截，不管縮排多少都不能切段。
        # 掃描歪斜會讓續行的 x0 偶爾超過門檻，切下去就會出現「…expres-」自成一段。
        continues = bool(paras) and (
            _HYPHEN_EOL.search(paras[-1][-1].rstrip())
            or _same_printed_line(lines, i, med_gap))
        start_new = (not paras) or (not continues and is_indented(lines, i, thresh=indent_thresh))
        if start_new:
            paras.append([text])
            continue
        prev = paras[-1][-1]
        m = _HYPHEN_EOL.search(prev.rstrip())
        if m:
            paras[-1][-1] = prev.rstrip()[: -1]  # 去掉行末連字號
            paras[-1][-1] += text.lstrip().split(" ", 1)[0]
            rest = text.lstrip().split(" ", 1)
            if len(rest) > 1:
                paras[-1].append(rest[1])
        else:
            paras[-1].append(text)
    return [normalize(" ".join(p)) for p in paras if normalize(" ".join(p))]


_ALNUM = re.compile(r"[A-Za-z0-9ÄÖÜäöüßÀ-ÿ]")


def is_junk(text: str, min_ratio: float = 0.55, min_len: int = 4) -> bool:
    """整行都是 OCR 噪音就丟。掃描本頁末常有裝飾線、書帖記號、書口髒污被認成
    「$r b I £ £」這種東西；留著會被當成一整段送進翻譯引擎，引擎回的是
    「我注意到您提供的內容似乎不完整」——那句話會原樣寫進譯文欄
    （[[feedback_haiku_meta_reply_pollution]]）。"""
    t = text.strip()
    if len(t) < min_len:
        return True
    letters = len(_ALNUM.findall(t))
    if letters / len(t) < min_ratio:
        return True
    # 幾乎全是單字母的碎塊（"$r b I £ £"）
    toks = t.split()
    return len(toks) >= 3 and sum(1 for w in toks if len(w) <= 1) / len(toks) > 0.6


def repair_folios(raw: list[str | None]) -> list[str | None]:
    """把讀錯的頁碼打掉，交給 fill_folios 遞推。

    🚨 OCR 偶爾把書眉的髒字認成數字（實測 258 頁裡有 20 處跳號，最誇張的一次
    把某頁讀成「1」）。錯的頁碼比沒有頁碼糟——它會讓引用者照著寫進論文。
    判準：一個阿拉伯頁碼要留下來，必須與**前後兩個**已知頁碼的遞增關係都對得上；
    對不上的一律清成 None。
    """
    out = list(raw)
    idx = [i for i, f in enumerate(raw) if f and f.isdigit()]
    for pos, i in enumerate(idx):
        n = int(raw[i])
        # 比對一律讀 raw：邊清邊比會讓前一個被清掉的鄰居變成 None，後面整串跟著崩。
        near = idx[max(0, pos - 2):pos] + idx[pos + 1:pos + 3]
        if not any(int(raw[j]) - n == j - i for j in near):
            out[i] = None
    return out


def page_units(lines: list[dict], folio: str | None) -> list[dict]:
    """一個掃描頁 → [{kind: 'body'|'note', text, page}]。註腳排在正文之後。"""
    body, notes = split_notes(strip_head(lines))
    out = [{"kind": "body", "text": t, "page": folio}
           for t in reflow(body) if not is_junk(t)]
    out += [{"kind": "note", "text": t, "page": folio}
            for t in reflow(notes, indent_thresh=10**6) if not is_junk(t)]
    return out
