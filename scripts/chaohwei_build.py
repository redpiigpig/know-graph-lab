#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《心靈的交會：山間對話》OCR 快取 → 昭慧法師全集（/collected-works）。

彼得‧辛格（Peter Singer）與釋昭慧 2016 年在南投霧社高峰禪林菩提院的對談錄，
法界出版社 2021。**作者授權製作電子版**（使用者已取得）。

pipeline ②（單一語言）＋ genre `dialogue`：本即繁體中文，零翻譯零跨語對齊；
段首寫成 `〔辛格〕`／`〔昭慧〕`，reader 會渲染成對話輪。

📄 頁碼：每一段都掛原書印刷頁碼當 `anchors[i]`（reader 左欄的引用號），
chunk 另存該章起始頁 `page_number`。頁碼一律來自 OCR 讀到的**印刷頁碼**，
讀不到就留空 —— 絕不拿流水號充數（[[feedback_transcribe_page_numbers]]）。

  python -X utf8 scripts/chaohwei_build.py --cache c:/tmp/chaohwei/ocr --audit
  python -X utf8 scripts/chaohwei_build.py --cache c:/tmp/chaohwei/ocr --inspect
  python -X utf8 scripts/chaohwei_build.py --cache c:/tmp/chaohwei/ocr --upload
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

EBOOK_ID = "c4a01957-0000-4000-8000-000000000001"  # c4a≈chao-hwei，1957＝昭慧法師生年
TITLE = "心靈的交會：山間對話"
ORIGINAL_TITLE = "Meeting of Minds: Dialogue in the mountain"
AUTHOR = "釋昭慧、彼得‧辛格"
PUBLISHER_YEAR = 2021

SPEAKERS = ("辛格", "昭慧")

# 章名表 —— 章名與起訖頁全部照書上的「目次 CONTENTS」頁抄，不是我自己歸納的。
# 分派段落靠**印刷頁碼區間**而不是比對標題文字：兩篇序的標題是自訂散文句
#（〈在這交會時互放的光芒〉），任何 regex 或字串比對都會連正文一起誤判。
CHAPTERS: list[dict] = [
    {"title": "彼得‧辛格　自序", "start": "a", "end": "d"},
    {"title": "在這交會時互放的光芒（釋昭慧　自序）", "start": "i", "end": "iii"},
    {"title": "對話一：倫理學的基礎理論", "start": "1", "end": "22"},
    {"title": "對話二：佛法的核心概念：業與涅槃", "start": "23", "end": "58"},
    {"title": "對話三：婦女與平等", "start": "59", "end": "78"},
    {"title": "對話四：情欲", "start": "79", "end": "98"},
    {"title": "對話五：扼殺胚胎", "start": "99", "end": "150"},
    {"title": "對話六：動物福利", "start": "151", "end": "176"},
    {"title": "對話七：安樂死與自殺", "start": "177", "end": "198"},
    {"title": "對話八：死刑與戰爭中的殺戮", "start": "199", "end": "216"},
    {"title": "對談尾聲的總結與回顧", "start": "217", "end": "222"},
]

# ── 純函式（零 I/O，scripts/tests/test_chaohwei_build.py 鎖定）──────────────

_CJK = r"\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef"
_HALF2FULL = {",": "，", ";": "；", ":": "：", "?": "？", "!": "！"}
_PUNCT_RE = re.compile(rf"(?<=[{_CJK}])\s*([,;:?!])")


def to_fullwidth_punct(text: str) -> str:
    """把**緊接在中文字後面**的半形標點換成全形。

    Gemini 轉錄中文書時常把原書的全形「，」吐成半形「,」。只在前一個字元是
    CJK 時才換，所以書裡的英文引文（`Singer, Peter`）與數字（`1,000`）不受影響。
    """
    if not text:
        return text
    return _PUNCT_RE.sub(lambda m: _HALF2FULL[m.group(1)], text)


_DASH_RE = re.compile(r"—{3,}")
_BLANK_MARK_RE = re.compile(r"^\s*（無正文）\s*$")


def normalize_page_text(text: str) -> str:
    """一頁 OCR 文字的整理：全形標點、破折號收斂成兩個全形破折號、去除空白行雜訊。"""
    if not text:
        return ""
    if _BLANK_MARK_RE.match(text.strip()):
        return ""
    out = to_fullwidth_punct(text)
    out = _DASH_RE.sub("——", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return out.strip()


_HEADER_PATTERNS = (
    re.compile(r"心靈(的)?交會"),                       # 書名頁眉（偶數頁）
    re.compile(r"山間對話"),
    re.compile(r"^(彼得\s*[·‧・.]?\s*辛格|釋?\s*昭慧(法師)?)\s*自?序$"),
    re.compile(r"^對話[一二三四五六七八九十]+\s*[：:]"),  # 章名頁眉（奇數頁）
    re.compile(r"^[0-9ivxlcIVXLC]{1,5}$"),               # 只有頁碼
    re.compile(r"^.{1,2}$"),                             # 掃描邊緣撿到的孤立殘字
)


_MAX_HEADER_LEN = 40  # 頁眉就是短短一行；超過這個長度的一定是正文

# 頁眉黏在正文同一行時（OCR 常這樣），只削掉行首那一小截，別把整行當頁眉
_HEADER_PREFIX_RE = re.compile(
    rf"^\s*(?:對話[一二三四五六七八九十]+\s*[：:][^：:]{{0,20}}?|心靈(?:的)?交會[^：:]{{0,14}}?)"
    rf"(?=(?:{'|'.join(SPEAKERS)})\s*[：:])"
)


def strip_page_header(text: str, printed: str) -> str:
    """刪掉頁首那一到兩行的**頁眉**（書名／章名／頁碼），只在該頁有印刷頁碼時作用。

    「只在有印刷頁碼時」是關鍵：章名頁（「對話二　Dialogue 2　佛法的核心概念」）
    本身沒有印刷頁碼，所以不會被誤刪——那是真正的章標題，不是頁眉。

    🚨 第二個關鍵是長度上限。OCR 有時把頁眉和正文吐成同一行
    （「對話六：動物福利辛格：在探討終結生命的…」），早期版本沒有長度限制，
    整頁 454 字就這樣被當成頁眉刪光——audit 看的是原始文字，還是報「沒有缺頁」。
    現在超長的行改成只削行首那一截頁眉。
    """
    if not text or not (printed or "").strip():
        return text or ""
    lines = text.split("\n")
    cut = 0
    for ln in lines[:2]:
        s = ln.strip()
        if not s:
            break
        if _HEADER_PREFIX_RE.match(s):
            break  # 頁眉後面就接著發言 → 這一行有正文，交給下面只削前綴
        if len(s) <= _MAX_HEADER_LEN and any(p.search(s) for p in _HEADER_PATTERNS):
            cut += 1
            continue
        break
    rest = "\n".join(lines[cut:]).strip()
    return _HEADER_PREFIX_RE.sub("", rest, count=1).strip()


_NOTE_RE = re.compile(r"^\s*\[\^([^\]]{1,8})\]\s*[:：]\s*")


_CONT_RE = re.compile(r"^\s*\[\^續\]\s*[:：]\s*")


def is_note(para: str) -> bool:
    """這一段是不是註文（`[^4]: …`）？"""
    return bool(_NOTE_RE.match(para or ""))


def is_note_continuation(para: str) -> bool:
    """這一段是不是**上一頁那條註**延續下來的（`[^續]: …`）？

    長註被版面切到下一頁底下是常事（唯識那本尤其多）。OCR 讀到沒有註號、
    直接承接前文的註文時會標成 `[^續]`，build 再把它接回原註——不接的話，
    註釋會斷成兩半而且後半沒有號碼，等於引不回去。
    """
    return bool(_CONT_RE.match(para or ""))


def split_body_and_notes(text: str) -> tuple[str, list[str]]:
    """一頁文字 → (正文, 註文段落 list)。

    腳註必須在接行之前先抽出來：`normalize_cjk_linebreaks` 只看「上一行有沒有
    句末標點」，會把頁末的註文黏到正文最後一段的尾巴，註釋就這樣消失在段落裡。
    註文本身可能折行，續行接回同一註（中文接行不插空格）。
    """
    body: list[str] = []
    notes: list[str] = []
    for raw in (text or "").split("\n"):
        ln = raw.strip()
        if _NOTE_RE.match(ln):
            notes.append(ln)
        elif notes:
            if ln:  # 註文的續行
                sep = " " if notes[-1][-1].isascii() and ln[0].isascii() else ""
                notes[-1] += sep + ln
        else:
            body.append(raw)
    return "\n".join(body).strip(), notes


_SPEAKER_RE = re.compile(rf"^\s*(?:〔\s*)?({'|'.join(SPEAKERS)})(?:\s*〕)?\s*[：:]\s*")


def mark_speaker(para: str) -> str:
    """「辛格：內文」→「〔辛格〕內文」。已經是 `〔辛格〕` 的原樣回傳；不是發言就不動。"""
    m = _SPEAKER_RE.match(para or "")
    if not m:
        return para
    return f"〔{m.group(1)}〕" + para[m.end():].lstrip()


_SENT_END = "。！？」』）》…—"


def stitch_pages(pages: list[dict]) -> list[tuple[str, str, int]]:
    """逐頁段落 → 全書段落串流 [(anchor, para, chapter_idx)]，跨頁續段合併。

    `pages` 是 [{"printed": "59", "chapter": 3, "paras": [...]}, ...]，依書序排好。
    某頁最後一段若沒有以句末標點結束，而下一頁第一段也不是新發言／新標題，
    就把兩段接起來（中文接行不插空格），anchor 與章別都取**該段起始的那一頁**——
    這樣引用時指到的是段落開始的頁，符合學術慣例。
    """
    out: list[tuple[str, str, int]] = []
    for pg in pages:
        printed = pg.get("printed") or ""
        ch = pg.get("chapter", -1)
        for i, para in enumerate(pg.get("paras") or []):
            para = para.strip()
            if not para:
                continue
            if is_note_continuation(para):
                # 接回上一頁那條註（anchor 留在註**開始**的那一頁）；
                # 找不到可接的註就退化成獨立一段，不憑空造一個註號
                if out and is_note(out[-1][1]):
                    anchor, prev, prev_ch = out[-1]
                    tail = _CONT_RE.sub("", para)
                    sep = " " if prev[-1].isascii() and tail[:1].isascii() else ""
                    out[-1] = (anchor, prev + sep + tail, prev_ch)
                    continue
                para = _CONT_RE.sub("", para)
            if (i == 0 and out
                    and ch == out[-1][2]          # 跨章不接：章末殘句不該吃掉下一章的開頭
                    and not is_note(out[-1][1])   # 前一段是註文時，下一頁正文不可接上去
                    and not is_note(para)
                    and not _SPEAKER_RE.match(para)
                    and not para.startswith("#")
                    and out[-1][1]
                    and out[-1][1][-1] not in _SENT_END):
                anchor, prev, prev_ch = out[-1]
                sep = " " if prev[-1].isascii() and para[0].isascii() else ""
                out[-1] = (anchor, prev + sep + para, prev_ch)
            else:
                out.append((printed, para, ch))
    return out


def normalize_printed(printed: str) -> str:
    """印刷頁碼正規化：純字母的頁碼一律小寫（OCR 常把前言的 `c` 讀成 `C`）。

    數字頁碼原樣保留。這一步只影響引用號的呈現與比對，不做任何進位或推算。
    """
    s = (printed or "").strip()
    return s.lower() if s.isalpha() else s


def page_sort_key(printed: str) -> tuple:
    """印刷頁碼 → 可排序鍵。用來偵測序列裡的洞，不用來重排頁（順序以掃描序為準）。

    分三段命名空間：前言字母（a,b,c…）＜ 羅馬數字（i,ii…）＜ 阿拉伯數字。
    無法解讀就回 (9, 0)。
    """
    s = (printed or "").strip()
    if not s:
        return (9, 0)
    if s.isdigit():
        return (2, int(s))
    low = s.lower()
    if re.fullmatch(r"[ivxlcdm]+", low):
        vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
        total, prev = 0, 0
        for ch in reversed(low):
            v = vals[ch]
            total += -v if v < prev else v
            prev = max(prev, v)
        return (1, total)
    if len(low) == 1 and low.isalpha():
        return (0, ord(low) - ord("a") + 1)
    return (9, 0)


def audit_pages(records: list[dict]) -> dict:
    """掃描頁清單 → 重複／缺頁報告。

    `records` = [{"work_page":N,"printed":"59","text":"..."}]，依掃描順序。
    重複：同一個非空 printed 出現在多個 work_page → 保留正文最長的那一份。
    缺頁：阿拉伯數字頁碼區間裡沒出現過的號碼。
    回傳 {"keep":[work_page…], "duplicates":[...], "missing":[...], "blank":[...]}。
    """
    by_printed: dict[str, list[dict]] = {}
    blank: list[int] = []
    apparatus: list[int] = []
    for r in records:
        p = normalize_printed(r.get("printed") or "")
        body = (r.get("text") or "").strip()
        if not body or body == "（無正文）":
            blank.append(r["work_page"])
            continue
        if is_apparatus_page(body, p):
            # 章名頁的「頁碼」是模型把「Dialogue 4」讀成的，不是印刷頁碼；
            # 拿去比對會生出假的重複，所以整頁不參與頁碼帳
            apparatus.append(r["work_page"])
            continue
        if p:
            by_printed.setdefault(p, []).append(r)

    drop: set[int] = set()
    duplicates = []
    for p, rs in by_printed.items():
        if len(rs) < 2:
            continue
        # 同一頁被掃兩次時，**先比影像品質再比字數**：實測重掃的那一份常被掃描機
        # 的黑邊吃掉半行，OCR 反而因為多吐了亂碼而「比較長」——單看字數會選到爛的。
        best = max(rs, key=lambda r: (r.get("quality", 0), len((r.get("text") or "").strip())))
        losers = [r["work_page"] for r in rs if r["work_page"] != best["work_page"]]
        drop.update(losers)
        duplicates.append({"printed": p, "keep": best["work_page"], "drop": sorted(losers)})

    nums = sorted(int(p) for p in by_printed if p.isdigit())
    missing: list[int] = []
    blank_gaps: list[int] = []
    if nums:
        have = set(nums)
        first_wp = {p: min(r["work_page"] for r in rs) for p, rs in by_printed.items()}
        blankset = set(blank) | set(apparatus)
        for n in range(nums[0], nums[-1] + 1):
            if n in have:
                continue
            # 這個號碼沒出現，是「章末空白頁」還是「真的沒掃到」？
            # 看掃描序：前一頁與後一頁之間如果夾著一張空白的掃描頁，就是空白頁。
            lo = first_wp.get(str(n - 1))
            hi = first_wp.get(str(n + 1))
            if lo and hi and any(w in blankset for w in range(lo + 1, hi)):
                blank_gaps.append(n)
            else:
                missing.append(n)

    keep = [r["work_page"] for r in records if r["work_page"] not in drop]
    return {
        "keep": keep,
        "duplicates": sorted(duplicates, key=lambda d: page_sort_key(d["printed"])),
        "missing": missing,
        "blank_gaps": blank_gaps,
        "blank": blank,
        "apparatus": apparatus,
        "printed_range": (nums[0], nums[-1]) if nums else None,
    }


_TITLE_NOISE_RE = re.compile(r"[\s　·‧・:：,，.。、!！?？「」『』（）()]+")


def _title_key(s: str) -> str:
    """章名比對用的正規化鍵：去掉空白與各式標點，只留字。"""
    return _TITLE_NOISE_RE.sub("", (s or "").strip())


def match_title(para: str, titles: list[str]) -> str | None:
    """段落是不是章名？是就回傳**表上的**章名，否則 None。

    刻意用「明確章名表」而不是 regex 猜：本書的序標題是自訂散文句
    （〈在這交會時互放的光芒〉），任何 regex 都會連正文一起誤判。
    比對允許 OCR 的標點與空白差異，也允許章名後面黏到一小段殘字。
    """
    key = _title_key(para)
    if not key:
        return None
    for t in titles:
        tk = _title_key(t)
        if not tk:
            continue
        if key == tk or (key.startswith(tk) and len(key) <= len(tk) + 4):
            return t
    return None


def is_apparatus_page(text: str, printed: str) -> bool:
    """這一頁是不是「裝置頁」——書名頁／目次頁／章名頁？是就整頁不收。

    三者共同點是**沒有印刷頁碼**、而且內容是中英對照的標題文字。章名（對話一…）
    改由章名表提供，目次的資訊已經寫進 CHAPTERS，書名頁的資訊在 cover chunk，
    收進正文只會變成夾在段落之間的雜訊。有印刷頁碼的頁一律不算裝置頁。
    """
    t = (text or "").strip()
    if not t:
        return False
    # 章名頁：中英章名並列、字數極少。這一條**不看 printed**——模型常把章名頁
    # 的「Dialogue.4」讀成頁碼 4 或 75，害它被當成正文頁的重複。
    if (len(t) < 80 and re.search(r"Dialogue[\s.]*\d", t)
            and re.search(r"對話[一二三四五六七八九十]", t)):
        return True
    if (printed or "").strip():
        return False
    if "目次" in t or "CONTENTS" in t:
        return True
    if "Meeting of Minds" in t:
        return True
    return False


def tag_chapters(pages: list[dict], chapters: list[dict]) -> list[dict]:
    """替每一頁標上它屬於第幾章（`chapter` 欄；-1＝卷首、len＝卷末）。

    做法是拿章的**起始頁碼原字串**去掃描序上找那一頁，找到就從那裡換章。
    刻意不解讀頁碼的語意：前言用的 `c`、`d` 同時也是羅馬數字 100 與 500，
    任何「把頁碼轉成數字再比大小」的寫法都會在這裡靜靜地判錯章
    （實測 `c`／`d` 兩頁會被算成第 100、500 頁而掉出序的區間）。
    比對忽略大小寫（OCR 會把 `c` 讀成 `C`），且切點必須沿掃描序遞增。
    """
    starts: dict[int, int] = {}
    last_wp = -1
    for i, ch in enumerate(chapters):
        key = (ch["start"] or "").strip().lower()
        # 起始頁被 OCR 讀錯（或那一頁剛好沒印頁碼）時，往後找兩頁當切點；
        # 少了這道保險，一個讀錯的頁碼會讓整章靜靜地併進前一章
        keys = [key]
        if key.isdigit():
            keys += [str(int(key) + k) for k in (1, 2)]
        hit = None
        for k in keys:
            for pg in pages:
                if pg["work_page"] <= last_wp:
                    continue
                if (pg.get("printed") or "").strip().lower() == k:
                    hit = pg["work_page"]
                    break
            if hit:
                break
        if hit:
            starts[hit] = i
            last_wp = hit
    cur = -1
    end_wp = None
    if chapters:
        last_key = (chapters[-1]["end"] or "").strip().lower()
        for pg in pages:
            if (pg.get("printed") or "").strip().lower() == last_key:
                end_wp = pg["work_page"]
    for pg in pages:
        if pg["work_page"] in starts:
            cur = starts[pg["work_page"]]
        elif end_wp is not None and pg["work_page"] > end_wp:
            cur = len(chapters)  # 目次最後一章之後 → 卷末（出版社書目等）
        pg["chapter"] = cur
    return pages


def split_chapters(units: list[tuple], chapters: list[dict]) -> list[dict]:
    """段落串流 [(anchor, para, chapter_idx)] → 章 list。

    章名寫成 markdown `## `，reader 會渲染成跨欄小標（該列不掛頁碼）。
    """
    buckets: dict[int, dict] = {}
    order: list[int] = []
    for anchor, para, idx in units:
        if idx not in buckets:
            title = ("卷首" if idx < 0 else
                     "卷末" if idx >= len(chapters) else chapters[idx]["title"])
            paras = [] if idx < 0 or idx >= len(chapters) else [f"## {title}"]
            buckets[idx] = {"title": title, "anchors": [], "paras": paras}
            order.append(idx)
        b = buckets[idx]
        b["anchors"].append(anchor)
        b["paras"].append(mark_speaker(para))
    return [buckets[i] for i in order if buckets[i]["anchors"]]


def build_chunks(chapters: list[dict]) -> list[dict]:
    """章 list → ebook_chunks（cover + 每章一 chunk）。

    `page_number` 只在該章第一段讀得到印刷數字頁碼時才填，其餘留 None
    （封面 chunk 例外，固定 0）—— 不用 chunk_index 充數。
    """
    cover = (f"# {TITLE}\n\n{ORIGINAL_TITLE}\n\n"
             f"彼得‧辛格（Peter Singer）、釋昭慧　對談\n\n法界出版社，{PUBLISHER_YEAR}")
    chunks = [{
        "chunk_index": 0, "chunk_type": "cover", "page_number": 0,
        "chapter_path": TITLE, "volume": TITLE, "parent_volume": None,
        "format": "markdown", "content": cover,
    }]
    for i, ch in enumerate(chapters, 1):
        first = next((a for a in ch["anchors"] if a.isdigit()), None)
        chunks.append({
            "chunk_index": i, "chunk_type": "chapter",
            "page_number": int(first) if first else None,
            "chapter_path": f"{TITLE} · {ch['title']}",
            "volume": TITLE, "parent_volume": None, "format": "markdown",
            "content": "\n\n".join(ch["paras"]),
            "anchors": [""] + list(ch["anchors"]) if ch["paras"][0].startswith("## ")
                       else list(ch["anchors"]),
        })
    return chunks


# ── I/O ────────────────────────────────────────────────────────────────────

def page_quality(work_pdf: Path, page_no: int) -> int:
    """工作 PDF 第 page_no 頁的「乾淨度」0–20（20 最乾淨）。

    掃描機在重掃那一份上留下的黑邊會吃掉半行字，所以用「很暗的像素佔比」當品質
    指標：黑邊越多分數越低。分成 20 檔而不是用浮點，是為了讓細微差異不干擾
    「同分時比字數」那一層。
    """
    import fitz
    doc = fitz.open(work_pdf)
    try:
        pix = doc[page_no - 1].get_pixmap(matrix=fitz.Matrix(0.18, 0.18), colorspace=fitz.csGRAY)
        data = pix.samples
        dark = sum(1 for v in data if v < 60)
        ratio = dark / max(1, len(data))
    finally:
        doc.close()
    return int(round((1 - ratio) * 20))


def load_cache(caches: Path | list[Path], work_pdf: Path | None = None) -> list[dict]:
    """讀 OCR 快取。給多個目錄時**前面的優先**，後面的只用來補前面沒有的頁。

    這是為了讓「改了 prompt 重跑」可以中途被配額打斷也還能出書：新快取跑到哪
    算哪，其餘的頁沿用舊快取（[[feedback_laptop_sleeps_design_for_resume]]）。
    """
    if isinstance(caches, Path):
        caches = [caches]
    by_page: dict[int, dict] = {}
    for cache in caches:
        for f in sorted(Path(cache).glob("*.json")):
            rec = json.loads(f.read_text(encoding="utf-8"))
            by_page.setdefault(rec["work_page"], rec)
    recs = sorted(by_page.values(), key=lambda r: r["work_page"])
    if work_pdf and Path(work_pdf).exists():
        for r in recs:
            r["quality"] = page_quality(Path(work_pdf), r["work_page"])
    return recs


def pages_for_stitch(records: list[dict], keep: list[int]) -> list[dict]:
    from clean_ocr_text import normalize_cjk_linebreaks
    keepset = set(keep)
    out: list[dict] = []
    dropped: list[tuple] = []
    for r in records:
        if r["work_page"] not in keepset:
            continue
        printed = normalize_printed(r.get("printed") or "")
        raw = r.get("text") or ""
        if is_apparatus_page(raw, printed):
            continue
        v2 = r.get("format") == "v2"
        # v2 的頁眉在 OCR 階段就單獨存進 header 欄，正文不必再猜著削
        cleaned = normalize_page_text(raw if v2 else strip_page_header(raw, printed))
        # 註文要在接行之前抽走，否則會被黏進正文最後一段
        body, notes = split_body_and_notes(cleaned)
        if not body and not notes:
            # 🚨 有正文的頁被清理清成空白＝整頁靜靜消失，比缺頁更難發現
            if len(raw.strip()) > 40:
                dropped.append((r["work_page"], printed, len(raw.strip())))
            continue
        if v2:
            paras = [ln.strip() for ln in body.split("\n") if ln.strip()]
        else:
            paras = [p.strip() for p in normalize_cjk_linebreaks(body).split("\n\n") if p.strip()]
        paras += notes
        out.append({"work_page": r["work_page"], "printed": printed, "paras": paras})
    for wp, pr, n in dropped:
        print(f"  \u26a0 掃描頁 {wp}（印刷頁 {pr or '?'}）原有 {n} 字，卻被頁眉清理清成空白", flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", nargs="+", default=["c:/tmp/chaohwei/ocr2", "c:/tmp/chaohwei/ocr"],
                    help="OCR 快取目錄，可給多個；前面的優先，後面的補缺頁")
    ap.add_argument("--work", default="c:/tmp/chaohwei/work.pdf",
                    help="工作 PDF；用來替重複頁評影像品質")
    ap.add_argument("--audit", action="store_true", help="只印重複／缺頁報告")
    ap.add_argument("--keep-out", help="把 keep 清單寫成 JSON（給 chaohwei_scan_prep.py build）")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    records = load_cache([Path(c) for c in a.cache], Path(a.work))
    if not records:
        raise SystemExit(f"快取是空的：{a.cache}")
    print(f"OCR 快取：{' → '.join(a.cache)}（{len(records)} 頁）")
    rep = audit_pages(records)

    if a.audit or a.keep_out:
        rng = rep["printed_range"]
        print(f"掃描頁 {len(records)}　→　保留 {len(rep['keep'])} 頁")
        print(f"印刷頁碼範圍：{rng[0]}–{rng[1]}" if rng else "印刷頁碼範圍：（無數字頁碼）")
        print(f"空白頁 {len(rep['blank'])}：{rep['blank']}")
        print(f"裝置頁（封面／書名頁／目次／章名頁）{len(rep['apparatus'])}：{rep['apparatus']}")
        print(f"重複 {len(rep['duplicates'])} 組：")
        for d in rep["duplicates"]:
            print(f"  頁 {d['printed']}：保留掃描頁 {d['keep']}，去掉 {d['drop']}")
        print(f"章末空白頁（不是缺頁）{len(rep['blank_gaps'])}：{rep['blank_gaps']}")
        print(f"🚨 真缺頁 {len(rep['missing'])}：{rep['missing']}")
        if a.keep_out:
            Path(a.keep_out).write_text(json.dumps(rep["keep"]), encoding="utf-8")
            print(f"✅ keep 清單 → {a.keep_out}")
        if a.audit:
            return

    pages = tag_chapters(pages_for_stitch(records, rep["keep"]), CHAPTERS)
    units = stitch_pages(pages)
    chapters = split_chapters(units, CHAPTERS)
    chunks = build_chunks(chapters)

    if a.inspect or not a.upload:
        total = sum(len(c["content"]) for c in chunks)
        print(f"{len(chunks)} chunks　{total:,} 字")
        for c in chunks:
            head = c["content"].split("\n", 1)[0][:40]
            print(f"  [{c['chunk_index']:>2}] p={c['page_number']}　{c['chapter_path'][:40]:<42} {head}")
    if a.upload:
        _upload(chunks)


def _upload(chunks: list[dict]) -> None:
    import datetime
    import requests
    import translate_ebook_to_zh as te

    # Drive（canonical）沒掛載時退到本機，仍然推 R2 讓站上讀得到；
    # 少寫這一層會變成「上傳成功但 Drive 沒有正本」([[feedback_build_not_equal_deployed]])
    chunks_dir = te.CHUNKS_DIR
    if not chunks_dir.exists():
        chunks_dir = Path("c:/tmp/chaohwei/_chunks")
        chunks_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ⚠ Drive 未掛載，JSONL 暫存 {chunks_dir}（掛回後要複製到 {te.CHUNKS_DIR}）", flush=True)
    out = chunks_dir / f"{EBOOK_ID}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    try:
        te.se.push_to_r2(EBOOK_ID, out)
        print("  ✓ R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 失敗: {e}", flush=True)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # total_pages 要用全書最後一個印刷頁，不是最後一章的**起始**頁（那會少掉整章）
    pages = [int(a) for c in chunks for a in (c.get("anchors") or []) if str(a).isdigit()]
    pages += [c["page_number"] for c in chunks if c["page_number"]]
    row = {
        "id": EBOOK_ID, "title": TITLE, "author": AUTHOR, "author_en": "Shih Chao-Hwei; Peter Singer",
        "original_title": ORIGINAL_TITLE, "file_type": "pdf",
        "file_path": f"全集/佛學/昭慧法師/{TITLE}",
        "category": "佛學", "subcategory": "佛教倫理學", "display_mode": "standard",
        "collection": "collected-works", "translator": "袁筱晴",
        "publication_year": PUBLISHER_YEAR,
        "chunk_count": len(chunks), "total_pages": max(pages) if pages else None,
        "total_chars": sum(len(c["content"]) for c in chunks),
        "parsed_at": now, "standardized_at": now,
    }
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{EBOOK_ID}", headers=te.H_GET, timeout=30)
    rows = [{
        "ebook_id": EBOOK_ID, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
        "page_number": c["page_number"], "chapter_path": c["chapter_path"],
        "content": c["content"][:200], "char_count": len(c["content"]),
    } for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[i:i + 25], timeout=60)
    print(f"  ✓ DB ebooks+previews  chunk_count={len(chunks)}  {EBOOK_ID}", flush=True)


if __name__ == "__main__":
    main()
