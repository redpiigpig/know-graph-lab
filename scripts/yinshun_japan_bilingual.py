"""日本學者論印順：PDF 全文 → 逐段日譯中 → 原文／中譯兩欄 JSON → R2 ＋ 索引。

    python -X utf8 scripts/yinshun_japan_bilingual.py --dry-run          # 只切段、看段數與前幾段
    python -X utf8 scripts/yinshun_japan_bilingual.py                    # 切段＋翻譯（可中斷，重跑接續）
    python -X utf8 scripts/yinshun_japan_bilingual.py --only <id> --upload

書目來源：scripts/data/yinshun_japan_catalog.json（每筆 id/group/author/year/title/…/pdf）。
PDF 正本在 Drive `研究資料\\印順學派與弘誓\\日本學者論印順\\`，逐段對照的工作檔存同夾 `_對照\\<id>.json`
（Drive 是正本、每翻完一段就寫回，斷線重跑從缺口接）。`--upload` 把對照檔送 R2
`yinshun-hongshi-fulltext/japan/<id>.json`，並重寫站上索引 japan-index.json。

🚨 日文不可過 OpenCC（余輩→餘輩、岩波→巖波）：原文欄一律原樣保存；譯文欄只收模型輸出。
🚨 頁碼只取 PDF 內印刷頁碼對應（--page-start），抓不到就留 null，不用段序頂替。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "scripts" / "data" / "yinshun_japan_catalog.json"
DRIVE_DIR = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\日本學者論印順")
WORK_DIR = DRIVE_DIR / "_對照"
INDEX_OUT = ROOT / "public" / "content" / "research-data" / "yinshun-hongshi" / "japan-index.json"
R2_PREFIX = "yinshun-hongshi-fulltext/"

PROMPT = """你是日本佛教學論文的專業譯者，把以下日文學術文字翻成台灣學術界通行的**繁體中文白話**。

要求：
1. 忠實、完整、逐句翻譯，不摘要、不省略、不加評論；文語體也譯成白話（引用的漢詩偈頌除外）。
2. 日文書名、論文名、期刊名**照原漢字保留**（例：《印度哲学研究》《大乗と小乗》），不改成簡體或新造中譯；書名用《》、篇名用〈〉。
3. 人名：日本人名照原漢字；中國人名用通行寫法（印順、太虛、呂澂）。
4. 佛教術語用漢傳通行譯語（如來藏、阿毘達磨、說一切有部）；梵巴語轉寫原樣保留。
5. 引自漢文佛典的原文（漢文、訓讀體）直接還原為漢文原句，不要再白話化。
6. 註號、頁碼、年份照原樣保留。
7. 片假名外來語、西方人名與梵語人名一律譯成中文通行譯名，不可留片假名（例：エンゲイジド・ブッディズム→入世佛教、シャーンティデーヴァ→寂天、ラモット→拉莫特），首次出現可括注原文拼法。
8. 只輸出這一段的譯文，不要前言、說明或原文。

{source}"""

SENT_END = tuple("。」』）)．.！？!?")
_PAGE_NUM_RE = re.compile(r"^[\s\-－—‐‒–−・.()（）LＬ]*\d{1,4}[\s\-－—‐‒–−・.()（）]*$")
_DIGITS_RE = re.compile(r"[\d０-９一二三四五六七八九〇十百]+")


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _join(a: str, b: str) -> str:
    """接兩段文字：日文直接黏；兩邊都是拉丁字母才補空白；英文斷字的連字號去掉。"""
    if not a:
        return b
    if a.endswith("-") and re.match(r"[a-z]", b[:1]):
        return a[:-1] + b
    if re.match(r"[A-Za-z0-9,.;:)]", a[-1]) and re.match(r"[A-Za-z0-9(]", b[:1]):
        return a + " " + b
    return a + b


# ── 橫排文字層切段 ────────────────────────────────────────────────────────────
_SUPER_RE = re.compile(r"[（(]?[\d０-９]{1,3}[）)]?[,，、\-–]?[\d０-９]{0,3}[）)]?|[＊*※†]+[\d０-９]*")
_KANA_RE = re.compile(r"[぀-ヿー・]{1,16}")
ruby_chars = [0]          # 本次抽取丟掉的振り仮名字數（字數對帳用）


def _page_lines(page) -> list[dict]:
    """一頁 → 視覺行（span 以基線分群；上標註號併進它所疊的那一行，保留成行內數字）。

    不用 block：dict 的 block 會把上標註號拆成獨立小 block，還會掉行
    （西野 2020 第一頁「作を残している」整行不見、「台湾のラモット²」被拆散）。"""
    spans = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            if abs(l["dir"][1]) > 0.9:          # 直排行不在這裡處理
                continue
            for s in l["spans"]:
                if s["text"].strip():
                    spans.append({"x0": s["bbox"][0], "y0": s["bbox"][1], "x1": s["bbox"][2],
                                  "y1": s["bbox"][3], "size": s["size"], "text": s["text"]})
    if not spans:
        return []
    sizes = sorted(s["size"] for s in spans for _ in range(len(s["text"])))
    body = sizes[len(sizes) // 2]
    # 先把一般大小的 span 分行，再把小字 span（上標）掛到垂直重疊最多的行上
    big = sorted([s for s in spans if s["size"] >= body * 0.8], key=lambda s: (s["y0"] + s["y1"]) / 2)
    small = [s for s in spans if s["size"] < body * 0.8]
    lines: list[dict] = []
    for s in big:
        cy = (s["y0"] + s["y1"]) / 2
        for ln in lines:
            if abs(cy - ln["cy"]) < min(s["size"], ln["size"]) * 0.45 and not (
                    s["x0"] > ln["x1"] + body * 6 or s["x1"] < ln["x0"] - body * 6):
                ln["spans"].append(s)
                ln["x0"], ln["x1"] = min(ln["x0"], s["x0"]), max(ln["x1"], s["x1"])
                ln["y0"], ln["y1"] = min(ln["y0"], s["y0"]), max(ln["y1"], s["y1"])
                break
        else:
            lines.append({"cy": cy, "size": s["size"], "spans": [s], "x0": s["x0"], "x1": s["x1"],
                          "y0": s["y0"], "y1": s["y1"]})
    big_lines = list(lines)
    for s in small:
        best, ov = None, -body * 0.6
        for ln in big_lines:
            o = min(s["y1"], ln["y1"]) - max(s["y0"], ln["y0"])
            near = s["x0"] <= ln["x1"] + body * 1.5 and s["x1"] >= ln["x0"] - body * 1.5
            if o > ov and near:
                best, ov = ln, o
        t = s["text"].strip()
        # 上標註號（1、(1)、（12）、＊、12）：疊在或緊貼某一行上 → 併進該行，保留成行內數字
        if best is not None and _SUPER_RE.fullmatch(t):
            best["spans"].append(s)
            best["x0"], best["x1"] = min(best["x0"], s["x0"]), max(best["x1"], s["x1"])
        # 振り仮名（ruby）：純假名小字、緊貼在正文行上方 → 丟掉（它是讀音，不是正文）
        #（ルビ跟上一行的間距可能跟下一行一樣近，所以不能用上面那個 best，要專找「正下方」的行）
        elif _KANA_RE.fullmatch(t) and any(
                0 <= ln["y0"] - s["y1"] + 1 < body * 0.6 and ln["x0"] - 1 <= s["x0"] and s["x1"] <= ln["x1"] + 1
                for ln in big_lines):
            ruby_chars[0] += len(t)
        else:
            lines.append({"cy": (s["y0"] + s["y1"]) / 2, "size": s["size"], "spans": [s],
                          "x0": s["x0"], "x1": s["x1"], "y0": s["y0"], "y1": s["y1"]})
    # 小字註文行彼此也要合成一行（同一基線的幾個小 span）
    merged: list[dict] = []
    for ln in sorted(lines, key=lambda l: l["cy"]):
        for m in merged:
            if m["size"] < body * 0.8 and ln["size"] < body * 0.8 and abs(m["cy"] - ln["cy"]) < ln["size"] * 0.45 \
                    and not (ln["x0"] > m["x1"] + body * 6 or ln["x1"] < m["x0"] - body * 6):
                m["spans"] += ln["spans"]
                m["x0"], m["x1"] = min(m["x0"], ln["x0"]), max(m["x1"], ln["x1"])
                break
        else:
            merged.append(ln)
    lines = merged
    for ln in lines:
        ln["spans"].sort(key=lambda s: s["x0"])
        t = ""
        for s in ln["spans"]:
            t = _join(t, s["text"].strip()) if t else s["text"].strip()
        ln["text"] = t
        ln["size"] = max((s["size"] for s in ln["spans"] if s["size"] >= body * 0.8), default=ln["size"])
        ln["body"] = body
    return lines


def _running_heads(doc, skip: int) -> set[str]:
    """跨頁重複出現在頁面上下緣的短行（書眉、刊名＋頁碼）→ 去數字後的正規化字串。"""
    from collections import Counter
    cnt: Counter = Counter()
    for pi, page in enumerate(doc):
        if pi < skip:
            continue
        H = page.rect.height
        seen = set()
        for ln in _page_lines(page):
            if (ln["y1"] < H * 0.12 or ln["y0"] > H * 0.9) and len(ln["text"]) < 80:
                k = _DIGITS_RE.sub("#", _norm_ws(ln["text"]))
                if k not in seen:
                    seen.add(k)
                    cnt[k] += 1
    return {k for k, v in cnt.items() if v >= 2 and len(k.replace("#", "")) >= 2}


def _is_headfoot(ln: dict, H: float, heads: set[str], printed: int | None = None) -> bool:
    if not (ln["y1"] < H * 0.12 or ln["y0"] > H * 0.9):
        return False
    t = _norm_ws(ln["text"])
    if _PAGE_NUM_RE.match(t) or re.fullmatch(r"[‒–\-−\s\d]+", t):
        return True
    if len(t) < 40 and re.search(r"[-‒–−]\d{1,4}[-‒–−]", t):      # 「- 180 -圓光佛學學報第十五期」
        return True
    # 首頁刊頭「佛教文化学会紀要 第29号 令和２年10月129」：只出現一次，但以本頁頁碼收尾
    if printed and len(t) < 60 and re.search(rf"(?<!\d){printed}[)）]?$", t):
        return True
    return _DIGITS_RE.sub("#", t) in heads


def _two_col(lines: list[dict], W: float) -> bool:
    """雙欄：只落在左半的行、只落在右半的行，各自佔全頁正文字數 30% 以上。
    （舊判準「左右各有 2 個 block」太鬆：上標註號的小 block 就讓單欄頁被當雙欄。）"""
    mid = W / 2
    tot = sum(len(l["text"]) for l in lines) or 1
    left = sum(len(l["text"]) for l in lines if l["x1"] < mid + 3)
    right = sum(len(l["text"]) for l in lines if l["x0"] > mid - 3)
    return left / tot >= 0.3 and right / tot >= 0.3


_HEADING_RE = re.compile(r"^[（(]?[一二三四五六七八九十0-9０-９]+[）)．.、]|^第[一二三四五六七八九十0-9]+[章節]|^[①-⑳]"
                         r"|^(はじめに|おわりに|むすび|結論|結語|序論|緒論|まとめ)$")
_NOTE_START_RE = re.compile(r"^[（(]?\s*[\d０-９]+\s*[）)．.]|^[\d０-９]{1,3}\s|^[＊*※]|^(注|註)\s*[（(]?[\d０-９]")


def horizontal_page_items(page, heads: set[str], printed: int | None = None) -> tuple[list[dict], int]:
    """一頁 → [{text, start, note}] 照閱讀順序；另回傳被當書眉頁碼濾掉的字數。"""
    W, H = page.rect.width, page.rect.height
    lines = _page_lines(page)
    dropped = sum(len(_norm_ws(l["text"])) for l in lines if _is_headfoot(l, H, heads, printed))
    lines = [l for l in lines if not _is_headfoot(l, H, heads, printed)]
    if not lines:
        return [], dropped
    if _two_col(lines, W):
        mid = W / 2
        full = [l for l in lines if l["x0"] < mid - 3 and l["x1"] > mid + 3]
        left = [l for l in lines if l["x1"] <= mid + 3]
        right = [l for l in lines if l["x0"] >= mid - 3 and l not in full]
        # 🚨 不可按 (y,x) 排——會把右欄插進左欄
        cols = [sorted(full, key=lambda l: l["cy"]), sorted(left, key=lambda l: l["cy"]),
                sorted(right, key=lambda l: l["cy"])]
    else:
        cols = [sorted(lines, key=lambda l: l["cy"])]
    items = []
    for col in cols:
        if not col:
            continue
        body = col[0]["body"]

        def local(i: int) -> tuple[float, float]:
            """同一段落塊的左右緣：前後三行裡 x0 相近（±1.2 字）且同為正文／註文的行。
            用整欄邊界會把兩側內縮的引文塊逐行切斷。"""
            me = col[i]
            kind = me["size"] < body * 0.92
            nb = [l for l in col[max(0, i - 3):i + 4]
                  if (l["size"] < body * 0.92) == kind and abs(l["x0"] - me["x0"]) < me["size"] * 1.2]
            return min(l["x0"] for l in nb), max(l["x1"] for l in nb)
        prev = None
        for i, l in enumerate(col):
            sz = l["size"]
            note = sz < body * 0.92
            # 段首：比下一行內縮（首行縮排），或比上一行內縮一字半以上（進入引文塊）
            nxt = col[i + 1] if i + 1 < len(col) else None
            #（引文塊最後一行也比下一行的首行縮排更靠右，所以還要求本行比上一行靠右）
            indent = (nxt is not None and nxt["x0"] < l["x0"] - sz * 0.6
                      and (prev is None or l["x0"] > prev["x0"] + sz * 0.5)) or (
                prev is not None and l["x0"] > prev["x0"] + sz * 1.5)
            heading = bool(_HEADING_RE.match(l["text"]))
            # 上一行提早收尾 → 段落結束；但只認句末標點、標題與字級變化——
            # 圖片旁繞排的窄行也「提早收尾」，那不是分段（志賀 2016 曾因此一句拆成五段）
            prev_short = prev is not None and prev["x1"] < local(i - 1)[1] - prev["size"] * 1.5 and (
                prev["text"].endswith(SENT_END + ("：", ":")) or bool(_HEADING_RE.match(prev["text"])))
            size_jump = prev is not None and abs(sz - prev["size"]) > 0.6
            prev_note = prev is not None and prev["size"] < body * 0.92
            # 頁首／欄首第一行：沒縮排也不是標題 → 承接上一頁（上一欄）的段落
            start = indent or heading or (prev is not None and (prev_short or size_jump or note != prev_note))
            if note and _NOTE_START_RE.match(l["text"]):
                start = True
            items.append({"text": l["text"], "start": start, "note": note})
            prev = l
    return items, dropped


# ── OCR 文字（Gemini Vision）→ 項目 ─────────────────────────────────────────────
_OCR_PAGE_RE = re.compile(r"^\s*【頁\s*([^】]*)】\s*$")


def ocr_items(txt: str) -> list[tuple[str | None, list[dict]]]:
    """`<id>.ocr.txt`（每個印刷頁以【頁 N】開頭、一段一行、承接上頁半句的行首帶 ↪）→ [(頁碼, 項目)]。"""
    pages: list[tuple[str | None, list[dict]]] = []
    txt = re.sub(r"(【頁\s*[^】]*】)", "\n\\1\n", txt.replace("¶", "\n"))
    # 模型被叫過別抄書眉，仍常照抄：全篇重複出現的短行（去數字後相同）與純頁碼行一律濾掉
    from collections import Counter
    norm = lambda x: _DIGITS_RE.sub("#", _norm_ws(x.lstrip("↪")))
    rep = Counter(norm(x) for x in txt.splitlines() if x.strip() and len(_norm_ws(x)) <= 40
                  and not _OCR_PAGE_RE.match(x))
    heads = {k for k, v in rep.items() if v >= 2 and len(k.replace("#", "")) >= 4}
    lines_in = []
    for x in txt.splitlines():
        t = _norm_ws(x.lstrip("↪"))
        if not _OCR_PAGE_RE.match(x) and t and (
                re.fullmatch(r"[-‒–—−―]*[\d一二三四五六七八九〇十百]{1,5}[-‒–—−―]*", t) or norm(x) in heads):
            continue
        lines_in.append(x)
    for raw in lines_in:
        m = _OCR_PAGE_RE.match(raw)
        if m:
            v = m.group(1).strip()
            pages.append((v if re.fullmatch(r"\d{1,4}", v) else None, []))
            continue
        s = raw.strip()
        if not s or s in ("（空白）", "(空白)"):
            continue
        if not pages:
            pages.append((None, []))
        cont = s.startswith("↪")
        s = s.lstrip("↪").strip()
        # 模型仍常照印刷行斷行：上一行沒以句號類收尾、本行也不像標題或註 → 視為同段接續
        prev = pages[-1][1][-1]["text"] if pages[-1][1] else None
        if prev is not None and not cont and not prev.endswith(SENT_END + ("：", ":")) \
                and not _HEADING_RE.match(s) and not _HEADING_RE.match(prev) and not _NOTE_START_RE.match(s) \
                and len(prev) >= 12:
            cont = True
        pages[-1][1].append({"text": s, "start": not cont, "cont": cont, "note": False})
    return pages


def build_paras(stream: list[tuple[int | None, list[dict]]], max_len: int = 900) -> list[dict]:
    """（頁碼, 項目）串 → 段落。

    - 文字層：`start` 是本行是否段首；新頁第一行不是段首、上一段沒以句號收 → 接上去（跨頁接續）。
    - OCR：一行一段；行首 ↪（cont）→ 接上一頁的正文段。
    - 頁腳註文（note）不打斷正文：先暫存，等正文那一段結束才放出來。"""
    paras: list[dict] = []
    pending: list[dict] = []
    cur: dict | None = None
    for printed, items in stream:
        for it in items:
            t = it["text"].strip()
            if not t:
                continue
            if it.get("note"):
                if pending and not it["start"]:
                    pending[-1]["orig"] = _join(pending[-1]["orig"], t)
                else:
                    pending.append({"page": printed, "orig": t, "zh": ""})
                continue
            if cur is not None and (it.get("cont") or (not it["start"] and not it.get("ocr"))):
                cur["orig"] = _join(cur["orig"], t)
                continue
            if cur is not None:
                paras.append(cur)
            paras.extend(pending)
            pending = []
            cur = {"page": printed, "orig": t, "zh": ""}
    if cur is not None:
        paras.append(cur)
    paras.extend(pending)
    # 過長的段在句號處切開，免得一段譯文被截斷
    out: list[dict] = []
    for p in paras:
        s = p["orig"]
        while len(s) > max_len:
            cut = s.rfind("。", 0, max_len)
            if cut < max_len // 3:
                break
            out.append({"page": p["page"], "orig": s[:cut + 1], "zh": ""})
            s = s[cut + 1:]
        out.append({"page": p["page"], "orig": s, "zh": ""})
    return [p for p in out if len(p["orig"].strip()) >= 2]


def _trim(e: dict, paras: list[dict]) -> list[dict]:
    """同一頁混著別篇文章（雜誌掃描常見）：書目 `startMarker`／`endMarker` 指定本篇起訖段落的字串。
    起點那段保留、終點那段保留，之外的全丟。模型被叫過「只轉錄本篇」仍會照抄，所以要這一道。"""
    sm, em = e.get("startMarker"), e.get("endMarker")
    if sm:
        i = next((k for k, p in enumerate(paras) if sm in p["orig"]), None)
        if i is None:
            raise ValueError(f"{e['id']} 找不到 startMarker「{sm}」")
        paras = paras[i:]
    if em:
        j = next((k for k, p in enumerate(paras) if em in p["orig"]), None)
        if j is None:
            raise ValueError(f"{e['id']} 找不到 endMarker「{em}」")
        paras = paras[:j + 1]
    return paras


def extract_paras(e: dict, pdf_path: Path, report: bool = False) -> list[dict]:
    """依書目決定來源：`ocr: true` 讀 `_對照/<id>.ocr.txt`，否則讀 PDF 文字層（橫排）。"""
    return _trim(e, _extract_paras(e, pdf_path, report))


def _extract_paras(e: dict, pdf_path: Path, report: bool = False) -> list[dict]:
    if e.get("ocr"):
        op = ocr_txt_path(e["id"])
        if not op.exists():
            raise FileNotFoundError(f"缺 OCR 檔 {op.name}，先跑 --ocr")
        pages = ocr_items(op.read_text(encoding="utf-8"))
        for _, items in pages:
            for it in items:
                it["ocr"] = True
        # 同一頁印了兩套頁碼（印佛研：J-STAGE 通號「—938—」＋分冊「(175)」），模型挑哪個不一定。
        # 書目的 pageStart/pageStep 是照印在頁上的通號核過的：一個 PDF 頁一個印刷頁、且至少兩頁
        # OCR 讀到的號碼正好落在這個序列上 → 整篇改用這個序列（它就是頁上印的那一套）。
        ps0, st0 = e.get("pageStart"), e.get("pageStep", 1)
        if ps0:
            import fitz
            n_pdf = len(fitz.open(pdf_path))
            if len(pages) == n_pdf:
                seq = [ps0 + k * st0 for k in range(n_pdf)]
                hit = sum(1 for k, (pg, _) in enumerate(pages) if pg and int(pg) == seq[k])
                if hit >= 2 and hit < n_pdf:
                    print(f"    頁碼：OCR 讀到 {hit}/{n_pdf} 頁與書目序列相符，其餘改用書目序列 {seq[0]}…{seq[-1]}")
                if hit >= 2:
                    pages = [(str(seq[k]), items) for k, (_, items) in enumerate(pages)]
        paras = build_paras([(int(p) if p else None, items) for p, items in pages])
        if report:
            src = sum(len(_norm_ws(it["text"])) for _, items in pages for it in items)
            got = sum(len(_norm_ws(p["orig"])) for p in paras)
            nums = [int(p) for p, _ in pages if p]
            print(f"    字數：OCR {src} → 切段 {got}（差 {abs(src - got) / max(src, 1):.1%}）；"
                  f"印刷頁 {len(nums)}/{len(pages)} 頁讀到頁碼 {nums[:1]}…{nums[-1:]}")
        return paras
    import fitz
    doc = fitz.open(pdf_path)
    skip = e.get("skipPages", 0)
    ps, step = e.get("pageStart"), e.get("pageStep", 1)
    heads = _running_heads(doc, skip)
    ruby_chars[0] = 0
    stream, dropped, raw = [], 0, 0
    for pi, page in enumerate(doc):
        if pi < skip:
            continue
        printed = (ps + (pi - skip) * step) if ps else None
        items, d = horizontal_page_items(page, heads, printed)
        dropped += d
        raw += len(_norm_ws(page.get_text("text")))
        dropped += ruby_chars[0]
        ruby_chars[0] = 0
        stream.append((printed, items))
    paras = build_paras(stream)
    if report:
        got = sum(len(_norm_ws(p["orig"])) for p in paras)
        diff = abs(raw - dropped - got) / max(raw - dropped, 1)
        flag = "  🚩 >2% 要查" if diff > 0.02 else ""
        print(f"    字數：get_text {raw}－書眉頁碼 {dropped}＝{raw - dropped} → 切段 {got}（差 {diff:.1%}）{flag}")
    return paras


# ── Gemini Vision OCR ────────────────────────────────────────────────────────
OCR_PROMPT = """這是{lang}學術文獻〈{title}〉（{venue}）的 PDF，共 {k} 個 PDF 頁。請逐頁完整轉錄原文，
輸出 JSON：{{"pages":[{{"page":1,"text":"..."}}]}}，"page" 是這份檔案裡的 1-based 頁次。

"text" 的規則：
1. 原樣轉錄：字形照印（舊字體「佛敎」「學」照舊、新字體照新），不可改成簡體、不可改寫、不可翻譯、不可摘要。
2. 每一個**印刷頁**以單獨一行 `【頁 N】` 開頭，N 是該頁上**印出來的頁碼**（漢數字也轉成阿拉伯數字）。
   一個 PDF 頁若是左右兩個印刷頁（跨頁掃描），就分成兩個 `【頁 N】` 區塊，按頁碼順序。
   頁碼常印在頁面底部中央（如「— 19 —」「-737-」）或頁角，也可能是書眉裡的數字；仔細找。
   頁面上看不到頁碼就寫 `【頁 ?】`——**絕對不要用前後頁推算**。
   🚨 只轉錄〈{title}〉這一篇：同一頁上若有別篇文章（前一篇的結尾、下一篇的開頭、同頁的其他書評），一律不轉錄。
3. 閱讀順序：直排（縱書）每行由上而下、行序由右而左；頁面分上下段（段組）時先讀完上段全部行再讀下段。
   橫排雙欄先左欄全部再右欄。
4. 不轉錄：書眉（刊名、篇名、作者名與頁碼那一行）、「Society for …」「NII-Electronic Library Service」
   「The Japanese Association of …」之類浮水印。
5. **一個自然段寫成一行**，不要照印刷換行斷行；章節標題自成一行。
   🚨 分段符 `¶` 只放在**自然段的結尾**、標題之後、每條註之後、每個 `【頁 N】` 之後——JSON 裡的換行會被吃掉，靠 `¶` 分段。
   **不要**在每個印刷行的行尾放 `¶`：直排一行只有十幾二十字，一段通常跨好幾行，要把它們接成一段。
   若該頁第一行是承接上一頁未完的句子，行首加 `↪`。
6. 正文中的上標註號寫成行內半形括號數字如 `(1)`，緊貼它標記的字詞，不可自成一行。
7. 註釋、參考文獻、附記照樣完整轉錄，每條一行，保留原編號。表格逐列轉成文字一列一行；圖只寫圖說。
8. 空白頁寫 `【頁 ?】` 再一行 `（空白）`。
只輸出 JSON，不要任何說明。"""


OCR_MODEL = os.environ.get("YJ_OCR_MODEL", "gemini-2.5-flash")   # 失敗時 ocr_pdf 會自己輪其他模型與 key


def ocr_txt_path(eid: str) -> Path:
    return WORK_DIR / f"{eid.split('/')[-1]}.ocr.txt"


def run_ocr(e: dict, pdf: Path, batch: int = 2, redo_missing: bool = False) -> bool:
    """逐批 OCR，每批寫回 `_對照/<id>.ocr.json`（可續跑），全部完成才組 `<id>.ocr.txt`。
    redo_missing：只把回報【頁 ?】的 PDF 頁重跑一次（模型偶爾漏看頁腳頁碼；重跑還是 ? 就留 null）。"""
    import fitz
    from ocr_pdf_to_text import ocr_pdf
    side = WORK_DIR / f"{e['id'].split('/')[-1]}.ocr.json"
    got: dict[str, str] = json.loads(side.read_text(encoding="utf-8")) if side.exists() else {}
    if redo_missing:
        miss = [k for k, v in got.items() if not re.search(r"【頁\s*\d+\s*】", v) and "空白" not in v]
        for k in miss:
            del got[k]
        if miss:
            print(f"    重跑缺頁碼的 PDF 頁 {sorted(map(int, miss))}", flush=True)
        batch = 1
    n = len(fitz.open(pdf))
    lang = "中文" if e.get("zhSame") else "日文"
    for s in range(1, n + 1, batch):
        rng = list(range(s, min(s + batch - 1, n) + 1))
        if all(str(i) in got for i in rng):
            continue
        prompt = OCR_PROMPT.format(lang=lang, title=e["title"], venue=e.get("venue", ""), k=len(rng))
        t0 = time.time()
        try:
            pages = ocr_pdf(pdf, model=OCR_MODEL, pages=(rng[0], rng[-1]), prompt=prompt)
        except Exception as ex:  # noqa: BLE001
            print(f"    ✗ OCR pp{rng[0]}-{rng[-1]} 失敗：{str(ex)[-200:]}", flush=True)
            return False
        texts = {int(p["page"]): (p.get("text") or "") for p in pages}
        if set(texts) != set(rng) and len(pages) == len(rng):
            # 模型偶爾把印刷頁碼填進 "page"：回傳頁數對得上就照順序對回 PDF 頁
            texts = {i: (p.get("text") or "") for i, p in zip(rng, pages)}
        for i in rng:
            t = texts.get(i, "")
            if not t.strip():
                print(f"    ✗ PDF 頁 {i} 回空，停下（重跑接續）", flush=True)
                side.write_text(json.dumps(got, ensure_ascii=False, indent=1), encoding="utf-8")
                return False
            got[str(i)] = t
        side.write_text(json.dumps(got, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"    OCR pp{rng[0]}-{rng[-1]} ✓ {sum(len(texts.get(i, '')) for i in rng)} 字 {time.time() - t0:.0f}s", flush=True)
    body = []
    for i in range(1, n + 1):
        t = got[str(i)].strip()
        if not t.startswith("【頁"):
            t = "【頁 ?】\n" + t
        body.append(t)
    ocr_txt_path(e["id"]).write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"    → {ocr_txt_path(e['id']).name}", flush=True)
    return True


def load_catalog() -> list[dict]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


# ── 翻譯（Gemini → NVIDIA → Haiku，逐段寫回） ─────────────────────────────────
_PROTECT_RE = re.compile(r"《[^》]{1,80}》|〈[^〉]{1,80}〉|『[^』]{1,80}』|岩波|余輩")
_PREAMBLE_RE = re.compile(r"^\s*(以下是|以下為|下面是)[^\n]{0,20}(翻譯|譯文)[^\n]*[:：]\s*\n|^\s*(譯文|翻譯)[:：]\s*")


def get_translator():
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = PROMPT
    # 🚨 NVIDIA 那一層輸出會過 OpenCC s2tw；譯文裡照原漢字保留的日文書名（岩波→巖波）會被改壞。
    # 包一層：書名號裡的字與已知日文詞先換成佔位符，轉完再換回來。
    orig_tt = te._to_traditional

    def safe_tt(text: str) -> str:
        keep: list[str] = []

        def stash(m):
            keep.append(m.group(0))
            return f"{len(keep) - 1}"
        out = orig_tt(_PROTECT_RE.sub(stash, text))
        return re.sub(r"(\d+)", lambda m: keep[int(m.group(1))], out)
    te._to_traditional = safe_tt
    if os.environ.get("YJ_SKIP_GEMINI"):
        # Gemini 免費層當天額度用完時，每段仍會把 7 把 key 各試三次（幾分鐘）才退 NVIDIA；直接跳過
        te._gemini_cooldown_until = time.time() + 86400

    def fn(src: str) -> str:
        out = te.gemini_with_nvidia_fallback(src)
        out = re.sub(r"<think>.*?</think>", "", out, flags=re.S)
        out = _PREAMBLE_RE.sub("", out).strip()
        if "<think>" in out or "</think>" in out:
            raise RuntimeError("推理外洩（think 標籤未閉合）")
        bad = te.unusable_reason(out, src)
        if bad:
            raise RuntimeError(f"譯文不可用：{bad}")
        return out
    return fn


def work_path(eid: str) -> Path:
    return WORK_DIR / f"{eid.split('/')[-1]}.json"


def translate_entry(e: dict, fn, pace: float) -> tuple[int, int]:
    wp = work_path(e["id"])
    data = json.loads(wp.read_text(encoding="utf-8"))
    paras = data["paras"]
    todo = [i for i, p in enumerate(paras) if not p["zh"]]
    print(f"  {e['id']}: {len(paras) - len(todo)}/{len(paras)} 已譯，待譯 {len(todo)}", flush=True)
    fails = 0
    for i in todo:
        src = paras[i]["orig"]
        if e.get("zhSame") or not re.search(r"[぀-ヿ一-鿿]", src) \
                or re.fullmatch(r"[\d\s.,\-–()（）]+", src):
            paras[i]["zh"] = src          # 本即中文的原件、純數字、純西文書目：原樣
        else:
            try:
                paras[i]["zh"] = fn(src).strip()
                fails = 0
            except Exception as ex:  # noqa: BLE001
                fails += 1
                print(f"    段 {i} 失敗：{str(ex)[:160]}", flush=True)
                if fails >= 3:
                    print("    連續 3 段失敗，停下來（重跑接續）", flush=True)
                    break
                time.sleep(30)
                continue
        wp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(pace)
    done = sum(1 for p in paras if p["zh"])
    return done, len(paras)


# ── R2 與索引 ─────────────────────────────────────────────────────────────────
def r2_client():
    import boto3
    from dotenv import dotenv_values
    env = {**dotenv_values(ROOT / ".env"), **os.environ}
    s3 = boto3.client("s3", region_name="auto", endpoint_url=env["R2_ENDPOINT"],
                      aws_access_key_id=env["R2_ACCESS_KEY"], aws_secret_access_key=env["R2_SECRET_KEY"])
    return s3, env["R2_BUCKET"]


def upload(e: dict, s3, bucket: str) -> None:
    body = work_path(e["id"]).read_bytes()
    s3.put_object(Bucket=bucket, Key=f"{R2_PREFIX}{e['id']}.json", Body=body,
                  ContentType="application/json; charset=utf-8")


def write_index(cat: list[dict]) -> None:
    rows = []
    for e in cat:
        paras = translated = 0
        wp = work_path(e["id"])
        if e.get("pdf") and wp.exists():
            ps = json.loads(wp.read_text(encoding="utf-8"))["paras"]
            paras, translated = len(ps), sum(1 for p in ps if p["zh"])
        row = {k: e.get(k, "") for k in ("id", "group", "author", "year", "title", "titleZh", "venue",
                                         "volume", "issue", "pages", "kind", "url", "abstract", "lang")}
        row["abstract"] = row["abstract"] if row["abstract"] != "未讀。" else ""
        row.update(paras=paras, translated=translated)
        if e.get("zhSame"):
            row["zhSame"] = True          # 原件本即中文（《內明》中譯審查報告）：兩欄同文
        rows.append(row)
    INDEX_OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"索引 {len(rows)} 筆 → {INDEX_OUT.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只處理這個 id（可逗號分隔）")
    ap.add_argument("--dry-run", action="store_true", help="只切段，印字數對帳與前幾段，不翻譯不寫檔")
    ap.add_argument("--show", type=int, default=6, help="--dry-run 印幾段")
    ap.add_argument("--ocr", action="store_true", help="書目標 ocr:true 的篇目先跑 Gemini Vision OCR（可續跑）")
    ap.add_argument("--reocr-missing", action="store_true", help="配 --ocr：只重跑回報【頁 ?】的頁一次")
    ap.add_argument("--resplit", action="store_true", help="重新切段（會清掉該篇已譯內容）")
    ap.add_argument("--no-translate", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--pace", type=float, default=1.0)
    a = ap.parse_args()

    cat = load_catalog()
    only = set(a.only.split(",")) if a.only else None
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    fn = None if (a.dry_run or a.no_translate or a.ocr) else get_translator()
    s3 = bucket = None
    if a.upload:
        s3, bucket = r2_client()

    for e in cat:
        if only and e["id"] not in only:
            continue
        if not e.get("pdf") or not e.get("translate"):
            continue
        pdf = DRIVE_DIR / e["pdf"]
        if not pdf.exists():
            print(f"✗ 找不到 PDF：{pdf}")
            continue
        if a.ocr:
            if e.get("ocr") and a.reocr_missing:
                print(f"● OCR（補頁碼） {e['id']}", flush=True)
                run_ocr(e, pdf, redo_missing=True)
            elif e.get("ocr") and not ocr_txt_path(e["id"]).exists():
                print(f"● OCR {e['id']}", flush=True)
                run_ocr(e, pdf)
            continue
        if e.get("ocr") and not ocr_txt_path(e["id"]).exists():
            print(f"… {e['id']} 尚未 OCR，跳過（先跑 --ocr）")
            continue
        wp = work_path(e["id"])
        if a.dry_run or a.resplit or not wp.exists():
            print(f"● {e['id']}", flush=True)
            paras = extract_paras(e, pdf, report=True)
            n_hit = sum(p["orig"].count("印順") for p in paras)
            print(f"    {len(paras)} 段，{sum(len(p['orig']) for p in paras)} 字，「印順」{n_hit} 次")
            if a.dry_run:
                for p in paras[:a.show]:
                    print(f"    p.{p['page']} │ {p['orig'][:90]}")
                continue
            wp.write_text(json.dumps({"id": e["id"], "paras": paras}, ensure_ascii=False, indent=1), encoding="utf-8")
        if fn:
            done, total = translate_entry(e, fn, a.pace)
            print(f"  → {done}/{total}", flush=True)
        if s3:
            upload(e, s3, bucket)
            print(f"  ↑ R2 {R2_PREFIX}{e['id']}.json")

    if not (a.dry_run or a.ocr):
        write_index(cat)


if __name__ == "__main__":
    main()
