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
8. 即使原文只是片段、半句、書目、網址或註號，也照樣逐字翻譯（書目與網址原樣保留），**絕不可**要求補充原文、評論原文品質或說明自己要翻譯。
9. 只輸出這一段的譯文，不要前言、說明或原文。

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


def _page_lines(page, clip=None) -> list[dict]:
    """一頁 → 視覺行（span 以基線分群；上標註號併進它所疊的那一行，保留成行內數字）。

    不用 block：dict 的 block 會把上標註號拆成獨立小 block，還會掉行
    （西野 2020 第一頁「作を残している」整行不見、「台湾のラモット²」被拆散）。"""
    spans = []
    for b in page.get_text("dict", clip=clip)["blocks"]:
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


def horizontal_page_items(page, heads: set[str], printed: int | None = None,
                          clip=None) -> tuple[list[dict], int]:
    """一頁 → [{text, start, note}] 照閱讀順序；另回傳被當書眉頁碼濾掉的字數。
    clip：只讀頁面的這一塊（呼叫端先切好欄時用；欄距窄的中文雙欄，同基線的左右兩行會被併成一行）。"""
    W, H = page.rect.width, page.rect.height
    lines = _page_lines(page, clip)
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


# ── 直排（縱書）文字層切段 ─────────────────────────────────────────────────────
# 印佛研等直排 PDF 的文字層常是「一字一行」：每個字各自一個 dir=(0,1) 的 line。
# 作法：字按中心 x 分成直行 → 直行內按 y 排、遇大空隙切開（上下兩段式的段間空白）→
# 各段依 y 區間合併成「段」（上段、下段）→ 段內按 (-x1, y0) 由右而左。
# 🚨 不可整頁按 (-x1, y0) 排：上下兩段式會把下段每一行插進上段對應那一行後面。

def vertical_ratio(page) -> float:
    vert = hor = 0
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            c = sum(len(s["text"].strip()) for s in l["spans"])
            if abs(l["dir"][1]) > 0.9:
                vert += c
            else:
                hor += c
    return vert / max(vert + hor, 1)


def _vertical_cols(page) -> tuple[list[dict], list[dict], float]:
    """一頁 → (直行段 [{x0,x1,y0,y1,size,text}], 剩下的橫排 span, 正文字級)。"""
    W = page.rect.width
    vg, hs = [], []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            v = abs(l["dir"][1]) > 0.9
            for s in l["spans"]:
                t = s["text"].strip()
                if not t:
                    continue
                x0, y0, x1, y1 = s["bbox"]
                g = {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "size": s["size"], "text": t,
                     "xc": (x0 + x1) / 2, "v": v}
                (vg if v else hs).append(g)
    if not vg:
        return [], hs, 10.0
    sizes = sorted(g["size"] for g in vg for _ in range(len(g["text"])))
    body = sizes[len(sizes) // 2]
    # 1) 依中心 x 分群
    vg.sort(key=lambda g: -g["xc"])
    groups: list[list[dict]] = []
    for g in vg:
        if groups and abs(groups[-1][-1]["xc"] - g["xc"]) < min(g["size"], body) * 0.4:
            groups[-1].append(g)
        else:
            groups.append([g])
    # 2) 群內按 y 排、大空隙切開
    segs = []
    for grp in groups:
        grp.sort(key=lambda g: g["y0"])
        cur = [grp[0]]
        for g in grp[1:]:
            if g["y0"] - cur[-1]["y1"] > max(g["size"], body) * 1.2:
                segs.append(cur)
                cur = [g]
            else:
                cur.append(g)
        segs.append(cur)
    # 2b) 上下兩段式的段間空白（gutter）：頁面中段直字幾乎沒覆蓋的一條橫帶。
    #     段間距有時只比字距大一點（魏 2023 首頁 12pt vs 字級 9.2），單靠空隙切不乾淨，要用覆蓋率找。
    H = page.rect.height
    occ = [0] * (int(H) + 2)
    for g in vg:
        if g["size"] < body * 0.7 or g["size"] > body * 1.3:
            continue
        for y in range(max(int(g["y0"]), 0), min(int(g["y1"]) + 1, len(occ))):
            occ[y] += 1
    M = max(occ) or 1
    best, run = None, None
    for y in range(int(H * 0.25), int(H * 0.75)):
        if occ[y] <= M * 0.08:
            run = (run[0], y) if run else (y, y)
            if run[1] - run[0] + 1 >= body * 0.5 and (best is None or run[1] - run[0] > best[1] - best[0]):
                best = run
        else:
            run = None
    if best is not None:
        gut = (best[0] + best[1]) / 2
        cut = []
        for sg in segs:
            if max(g["size"] for g in sg) > body * 1.3:
                cut.append(sg)
                continue
            up = [g for g in sg if (g["y0"] + g["y1"]) / 2 < gut]
            dn = [g for g in sg if (g["y0"] + g["y1"]) / 2 >= gut]
            cut += [x for x in (up, dn) if x]
        segs = cut
    cols = []
    for sg in segs:
        sz = sorted(g["size"] for g in sg for _ in range(len(g["text"])))
        cols.append({"x0": min(g["x0"] for g in sg), "x1": max(g["x1"] for g in sg),
                     "y0": min(g["y0"] for g in sg), "y1": max(g["y1"] for g in sg),
                     "size": sz[len(sz) // 2], "glyphs": sg})
    # 3) 小字直行：純假名＝振り仮名丟掉；其餘（註號「（ ）」）併進右／左鄰最近且 y 重疊的正文直行
    main = [c for c in cols if c["size"] >= body * 0.7]
    small = [c for c in cols if c["size"] < body * 0.7]
    ruby = 0
    for c in small:
        t = "".join(g["text"] for g in c["glyphs"])
        if _KANA_RE.fullmatch(t):
            ruby += len(t)
            continue
        # 註號小字（「（ ）」）裡的縱中橫數字先併進來，整個當一個記號插進正文
        own = [h for h in hs if c["x0"] - 1 <= (h["x0"] + h["x1"]) / 2 <= c["x1"] + 1
               and c["y0"] - 1 <= (h["y0"] + h["y1"]) / 2 <= c["y1"] + 1]
        if own:
            hs = [h for h in hs if h not in own]
            c["glyphs"] = sorted(c["glyphs"] + own, key=lambda g: (g["y0"] + g["y1"]) / 2)
        c["text"] = "".join(g["text"] for g in c["glyphs"])
        if re.fullmatch(r"[（(]\s*[）)]", c["text"]) and own:
            c["text"] = "(" + "".join(h["text"] for h in own) + ")"
        token = {"x0": c["x0"], "x1": c["x1"], "y0": c["y1"] - 0.5, "y1": c["y1"] + 0.5,
                 "size": c["size"], "text": c["text"], "xc": c["xc"] if "xc" in c else (c["x0"] + c["x1"]) / 2}
        best, bd = None, body * 1.3
        for m in main:
            if min(c["y1"], m["y1"]) - max(c["y0"], m["y0"]) < -1:
                continue
            d = max(m["x0"] - c["x1"], c["x0"] - m["x1"], 0)
            if d < bd:
                best, bd = m, d
        if best is not None:
            best["glyphs"].append(token)
        else:
            main.append(c)
    ruby_chars[0] += ruby
    # 4) 橫排短 span（縱中橫的數字、註號）：落在某直行的 x 範圍內就插進去
    rest = []
    for h in hs:
        in_margin = h["y0"] > H * 0.9 or h["y1"] < H * 0.1
        if h["x1"] - h["x0"] < body * 1.8 and not in_margin and not re.fullmatch(r"[―—‒–\-\s ]+", h["text"]):
            hit = next((m for m in main if m["x0"] - body * 0.4 <= h["xc"] <= m["x1"] + body * 0.4
                        and m["y0"] - body * 0.5 <= (h["y0"] + h["y1"]) / 2 <= m["y1"] + body * 0.5), None)
            if hit is not None:
                hit["glyphs"].append(h)
                continue
        rest.append(h)
    for m in main:
        m["glyphs"].sort(key=lambda g: (g["y0"] + g["y1"]) / 2)
        m["y0"] = min(g["y0"] for g in m["glyphs"])
        m["y1"] = max(g["y1"] for g in m["glyphs"])
        m["text"] = ""
        for g in m["glyphs"]:
            m["text"] = _join(m["text"], g["text"])
        m["xc"] = (m["x0"] + m["x1"]) / 2
    return main, rest, body


def _vhead_key(t: str) -> str:
    return _DIGITS_RE.sub("#", _norm_ws(t))


def vertical_running_heads(doc, skip: int) -> set[str]:
    """直排頁：頁緣（左右 12%）重複出現的直行＝柱（書眉）。"""
    from collections import Counter
    cnt: Counter = Counter()
    for pi, page in enumerate(doc):
        if pi < skip or vertical_ratio(page) < 0.5:
            continue
        W = page.rect.width
        seen = set()
        for c in _vertical_cols(page)[0]:
            if (c["xc"] < W * 0.12 or c["xc"] > W * 0.88) and len(c["text"]) < 80:
                k = _vhead_key(c["text"])
                if k not in seen:
                    seen.add(k)
                    cnt[k] += 1
    return {k for k, v in cnt.items() if v >= 2 and len(k.replace("#", "")) >= 2}


def vertical_page_items(page, heads: set[str], printed: int | None = None) -> tuple[list[dict], int]:
    """直排頁 → [{text, start, note}]（與 horizontal_page_items 同形）；另回傳濾掉的書眉頁碼字數。"""
    W, H = page.rect.width, page.rect.height
    cols, rest, body = _vertical_cols(page)
    dropped = 0
    keep = []
    for c in cols:
        t = _norm_ws(c["text"])
        edge = c["xc"] < W * 0.1 or c["xc"] > W * 0.9
        if (edge and c["size"] < body * 0.95 and len(t) < 80) or _vhead_key(t) in heads \
                or (edge and _PAGE_NUM_RE.match(t)):
            dropped += len(t)
            continue
        keep.append(c)
    # 橫排剩餘：頁碼／書眉丟掉；其他（直排頁裡夾的橫排西文、表格）照 y 附在頁尾
    tail = []
    for h in sorted(rest, key=lambda h: (round(h["y0"] / max(h["size"], 1)), h["x0"])):
        t = _norm_ws(h["text"])
        if (h["y1"] < H * 0.12 or h["y0"] > H * 0.9) and (len(t) < 60 or _PAGE_NUM_RE.match(t)):
            dropped += len(t)
            continue
        if re.fullmatch(r"[\d\s･・.,()（）\-‒–―― ]+", h["text"]):
            dropped += len(t)
            continue
        tail.append(h)
    if not keep:
        return [], dropped
    # 段（上下兩段式）。同一頁可能右半是通欄（要旨）、左半才分上下段（康 2019 首頁），
    # 首頁標題又常橫跨兩段、底下段的右端沒有上段對應（魏 2023）。作法：
    # 先用「非通欄直行」的 y 覆蓋率找段間空白 gutter → 每一直行歸上段／下段／通欄 →
    # 由右而左把連續的非通欄直行併成一「區」，區內先上段（-x1）再下段（-x1）。
    Hh = page.rect.height
    y_lo, y_hi = min(c["y0"] for c in keep), max(c["y1"] for c in keep)
    span_all = max(y_hi - y_lo, 1)

    def big(c) -> bool:
        return c["size"] > body * 1.3
    occ = [0] * (int(Hh) + 2)
    for c in keep:
        if big(c) or c["y1"] - c["y0"] > span_all * 0.75:
            continue
        for yy in range(max(int(c["y0"]), 0), min(int(c["y1"]) + 1, len(occ))):
            occ[yy] += 1
    M = max(occ) or 1
    gbest, run = None, None
    for yy in range(int(Hh * 0.25), int(Hh * 0.75)):
        if occ[yy] <= M * 0.2:
            run = (run[0], yy) if run else (yy, yy)
            if run[1] - run[0] + 1 >= body * 0.8 and (gbest is None or run[1] - run[0] > gbest[1] - gbest[0]):
                gbest = run
        else:
            run = None
    gut = (gbest[0] + gbest[1]) / 2 if gbest and M >= 3 else None
    if gut is not None and (sum(1 for c in keep if c["y1"] <= gut + 1) < 2
                            or sum(1 for c in keep if c["y0"] >= gut - 1) < 2):
        gut = None

    def tier(c) -> int:              # 0 上段、1 下段、-1 通欄（或無分段）
        if gut is None:
            return -1
        if c["y1"] <= gut + 1:
            return 0
        if c["y0"] >= gut - 1:
            return 1
        return -1
    byx = sorted(keep, key=lambda c: (-c["x1"], c["y0"]))
    zones: list[list[dict]] = []
    for c in byx:
        full = tier(c) < 0
        if zones and not full and tier(zones[-1][-1]) >= 0:
            zones[-1].append(c)
        else:
            zones.append([c])
    seq: list[tuple[dict, float, float, tuple]] = []      # (直行, 段頂, 段底, 段鍵)
    for zi, cs in enumerate(zones):
        for t in (-1, 0, 1):
            part = [c for c in cs if tier(c) == t]
            if not part:
                continue
            top = min(c["y0"] for c in part) if t != 1 else gut
            bot = max(c["y1"] for c in part) if t != 0 else gut
            if t == 0:
                top = min(c["y0"] for c in keep if tier(c) == 0)
            if t == 1:
                bot = max(c["y1"] for c in keep if tier(c) == 1)
                top = min(c["y0"] for c in keep if tier(c) == 1)
            seq += [(c, top, bot, (zi, t)) for c in part]
    items = []
    prev = prev_top = prev_bot = prev_key = None
    for i, (c, top, bot, key) in enumerate(seq):
        sz = c["size"]
        rel = c["y0"] - top
        nxt = seq[i + 1][0] if i + 1 < len(seq) and seq[i + 1][3] == key else None
        same = prev is not None and prev_key == key
        prel = (prev["y0"] - prev_top) if same else None
        note = sz < body * 0.92
        indent = (nxt is not None and (nxt["y0"] - top) < rel - sz * 0.6
                  and (prel is None or rel > prel + sz * 0.5)) or (prel is not None and rel > prel + sz * 1.5)
        heading = bool(_HEADING_RE.match(c["text"]))
        prev_short = prev is not None and prev["y1"] < prev_bot - prev["size"] * 1.5 and (
            prev["text"].endswith(SENT_END + ("：", ":")) or bool(_HEADING_RE.match(prev["text"])))
        size_jump = prev is not None and abs(sz - prev["size"]) > 0.6
        prev_note = prev is not None and prev["size"] < body * 0.92
        start = indent or heading or (prev is not None and (prev_short or size_jump or note != prev_note))
        if note and _NOTE_START_RE.match(c["text"]):
            start = True
        items.append({"text": c["text"], "start": start, "note": note})
        prev, prev_top, prev_bot, prev_key = c, top, bot, key
    for h in tail:
        items.append({"text": h["text"], "start": True, "note": h["size"] < body * 0.92})
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
    vheads = vertical_running_heads(doc, skip)
    ruby_chars[0] = 0
    stream, dropped, raw = [], 0, 0
    for pi, page in enumerate(doc):
        if pi < skip:
            continue
        printed = (ps + (pi - skip) * step) if ps else None
        if vertical_ratio(page) >= 0.5:
            items, d = vertical_page_items(page, vheads | heads, printed)
        else:
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


_last_ocr_err = [""]
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
            _last_ocr_err[0] = str(ex)
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


MINERU_PY = ROOT / "_mineru_venv" / "Scripts" / "python.exe"
QUOTA_SIGNS = ("exhausted", "429", "quota", "RESOURCE_EXHAUSTED", "rate limit")
# 兩支背景工作（本檔 --auto 與 yinshun_debate_fulltext.py）共用：Gemini OCR 連兩次配額錯就寫下停到何時，
# 之後幾輪排程直接跳過 Gemini，不必每輪再把各把 key 試一遍
GEMINI_BLOCK = ROOT / "output" / "yinshun-fulltext" / "gemini_blocked_until.txt"


def gemini_blocked() -> bool:
    try:
        return time.time() < float(GEMINI_BLOCK.read_text(encoding="utf-8").strip())
    except Exception:  # noqa: BLE001
        return False


def block_gemini(hours: float = 4) -> None:
    GEMINI_BLOCK.parent.mkdir(parents=True, exist_ok=True)
    GEMINI_BLOCK.write_text(str(time.time() + hours * 3600), encoding="utf-8")


def run_mineru_ocr(e: dict, pdf: Path) -> bool:
    """橫排掃描（J-STAGE 影像＋粗糙 OCR 層）走本機 MinerU（CPU，不搶夜班的 GPU 鎖），
    組成與 Gemini 路徑同格式的 `<id>.ocr.txt`：每 PDF 頁一個【頁 N】，一段一行。
    N 用書目核過的 pageStart／pageStep（一 PDF 頁一印刷頁）；沒有就寫【頁 ?】。
    🚨 MinerU 原樣輸出，不過 OpenCC（日文不可簡繁轉換）。"""
    import subprocess
    import tempfile
    lang = "en" if e.get("lang", "").startswith("英") else ("ch" if e.get("lang", "").startswith("中") else "japan")
    with tempfile.TemporaryDirectory(prefix="yj_mineru_") as td:
        out = Path(td) / "o.jsonl"
        r = subprocess.run([str(MINERU_PY), "-X", "utf8", str(ROOT / "scripts" / "mineru_ocr.py"), "run",
                            "--pdf", str(pdf), "--out", str(out), "--lang", lang, "--device", "cpu"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not out.exists():
            tail = (r.stdout or "")[-300:] + (r.stderr or "")[-300:]
            print(f"    ✗ MinerU 失敗 exit {r.returncode}：{tail}", flush=True)
            return False
        chunks = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines() if x.strip()]
    ps, st = e.get("pageStart"), e.get("pageStep", 1)
    body = []
    for c in sorted(chunks, key=lambda c: c["page_number"]):
        k = c["page_number"] - 1
        n = str(ps + k * st) if ps else "?"
        text = c.get("content") or ""
        main, _, notes = text.partition("—" * 15)
        paras = []
        for blk in re.split(r"\n\s*\n", main):
            t = ""
            for ln in blk.splitlines():
                t = _join(t, ln.strip()) if t else ln.strip()
            if t:
                paras.append(t)
        paras += [ln.strip() for ln in notes.splitlines() if ln.strip()]
        body.append(f"【頁 {n}】\n" + ("\n".join(paras) if paras else "（空白）"))
    ocr_txt_path(e["id"]).write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"    → {ocr_txt_path(e['id']).name}（MinerU {len(chunks)} 頁）", flush=True)
    return True


def load_catalog() -> list[dict]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


# ── 翻譯（Gemini → NVIDIA → Haiku，逐段寫回） ─────────────────────────────────
_PROTECT_RE = re.compile(r"《[^》]{1,80}》|〈[^〉]{1,80}〉|『[^』]{1,80}』|岩波|余輩")
_META_RE = re.compile(r"我注意到您|您提供的|您尚未提供|您貼上的|請提供(完整|具體|您要)|請將(原文|該段)|無法(提供|進行)?(忠實|準確)?(完整)?的?翻譯|尊敬的用戶|我已準備好|我準備好(進行)?翻譯|這段文字(殘缺|內容破碎|中沒有)|看來您提供|抱歉，(您|我需要)|我很遺憾，但這段|（注：(由於您|您提供|此段文本)")
_KANA_ANY = re.compile(r"[぀-ヿ]")
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

    # YJ_ENGINE=haiku：直打 Haiku（Max 訂閱，獨立額度池），免費池乾掉或要趕工時用
    engine = te.haiku_first if os.environ.get("YJ_ENGINE") == "haiku" else te.gemini_with_nvidia_fallback

    def fn(src: str) -> str:
        out = engine(src)
        out = re.sub(r"<think>.*?</think>", "", out, flags=re.S)
        out = _PREAMBLE_RE.sub("", out).strip()
        if "<think>" in out or "</think>" in out:
            raise RuntimeError("推理外洩（think 標籤未閉合）")
        bad = te.unusable_reason(out, src)
        if bad:
            raise RuntimeError(f"譯文不可用：{bad}")
        # 🚨 Haiku 遇到片段／書目／亂碼會回「抱歉，您尚未提供…」「我注意到您提供的…」，
        #    甚至自己編一段日文「論文」塞進來（2026-09-23 實測 23 篇中十幾篇中招）。這些一律退回。
        if _META_RE.search(out):
            raise RuntimeError("譯文不可用：後設回覆（拒譯／要求補充原文）")
        kana = len(_KANA_ANY.findall(out))
        if kana > 12 and kana / max(len(out), 1) > 0.08 and kana > len(_KANA_ANY.findall(src)) * 0.3:
            raise RuntimeError("譯文不可用：譯文欄殘留大量假名（未譯或捏造日文）")
        return out
    return fn


def work_path(eid: str) -> Path:
    return WORK_DIR / f"{eid.split('/')[-1]}.json"


def translate_entry(e: dict, fn, pace: float) -> tuple[int, int]:
    wp = work_path(e["id"])
    data = json.loads(wp.read_text(encoding="utf-8"))
    paras = data["paras"]
    if e.get("transcribeOnly"):
        print(f"  {e['id']}: 只轉錄（{e.get('lang', '')}），{len(paras)} 段", flush=True)
        return len(paras), len(paras)
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
            if e.get("transcribeOnly"):
                translated = paras
        row = {k: e.get(k, "") for k in ("id", "group", "author", "year", "title", "titleZh", "venue",
                                         "volume", "issue", "pages", "kind", "url", "abstract", "lang")}
        row["abstract"] = row["abstract"] if row["abstract"] != "未讀。" else ""
        row.update(paras=paras, translated=translated)
        if e.get("zhSame"):
            row["zhSame"] = True          # 原件本即中文（《內明》中譯審查報告）：兩欄同文
        if e.get("transcribeOnly"):
            row["transcribeOnly"] = True  # 中文／英文原件：只轉錄、單欄
        rows.append(row)
    INDEX_OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"索引 {len(rows)} 筆 → {INDEX_OUT.relative_to(ROOT)}")


def status_rows(cat: list[dict]) -> list[tuple]:
    rows = []
    for e in cat:
        if not e.get("pdf") or not e.get("translate"):
            continue
        wp = work_path(e["id"])
        need_ocr = e.get("ocr") and not ocr_txt_path(e["id"]).exists()
        if wp.exists():
            ps = json.loads(wp.read_text(encoding="utf-8"))["paras"]
            n, done = len(ps), (len(ps) if e.get("transcribeOnly") else sum(1 for p in ps if p["zh"]))
        else:
            n = done = 0
        st = ("待OCR(" + e.get("ocrEngine", "gemini") + ")") if need_ocr else (
            "未切段" if not wp.exists() else ("完成" if done == n and n else "翻譯中"))
        kind = "只轉錄" if e.get("transcribeOnly") else "逐段中譯"
        rows.append((e["id"], kind, st, done, n))
    return rows


def auto(cat: list[dict], only: set | None, pace: float) -> None:
    """背景續跑：逐篇 OCR → 切段 → 翻譯 → 上傳 R2 → 重寫索引。一次一篇、一個程序。
    Gemini OCR 連續兩次配額錯就這一輪不再叫 Gemini（其餘篇目照做 MinerU／翻譯），留待下輪。
    翻譯連續兩篇都停在失敗（引擎全倒）就整場停。"""
    s3, bucket = r2_client()
    fn = None
    gem_streak, gem_blocked, tr_fail = 0, gemini_blocked(), 0
    for e in cat:
        if only and e["id"] not in only:
            continue
        if not e.get("pdf") or not e.get("translate"):
            continue
        pdf = DRIVE_DIR / e["pdf"]
        if not pdf.exists():
            print(f"✗ 找不到 PDF：{pdf}", flush=True)
            continue
        wp = work_path(e["id"])
        if e.get("ocr") and not ocr_txt_path(e["id"]).exists():
            if e.get("ocrEngine") == "mineru":
                print(f"● MinerU OCR {e['id']}", flush=True)
                if not run_mineru_ocr(e, pdf):
                    continue
            else:
                if gem_blocked:
                    print(f"… {e['id']} 待 Gemini OCR（本輪配額已停）", flush=True)
                    continue
                print(f"● Gemini OCR {e['id']}", flush=True)
                _last_ocr_err[0] = ""
                if not run_ocr(e, pdf):
                    if any(k.lower() in _last_ocr_err[0].lower() for k in QUOTA_SIGNS):
                        gem_streak += 1
                        if gem_streak >= 2:
                            gem_blocked = True
                            block_gemini()
                            print("⛔ Gemini OCR 連續兩次配額錯：本輪不再叫 Gemini，其餘篇目留佇列", flush=True)
                    continue
                gem_streak = 0
        if not wp.exists():
            print(f"● 切段 {e['id']}", flush=True)
            try:
                paras = extract_paras(e, pdf, report=True)
            except Exception as ex:  # noqa: BLE001
                print(f"    ✗ 切段失敗：{ex}", flush=True)
                continue
            wp.write_text(json.dumps({"id": e["id"], "paras": paras}, ensure_ascii=False, indent=1), encoding="utf-8")
        if not e.get("transcribeOnly") and not e.get("zhSame"):
            ps = json.loads(wp.read_text(encoding="utf-8"))["paras"]
            if any(not p["zh"] for p in ps):
                fn = fn or get_translator()
                done, total = translate_entry(e, fn, pace)
                print(f"  → {done}/{total}", flush=True)
                if done < total:
                    tr_fail += 1
                    if tr_fail >= 2:
                        upload(e, s3, bucket)
                        write_index(cat)
                        print("⛔ 連續兩篇翻譯停在失敗，整場停（重跑接續）", flush=True)
                        return
                else:
                    tr_fail = 0
        elif e.get("zhSame"):
            translate_entry(e, None, 0)
        upload(e, s3, bucket)
        print(f"  ↑ R2 {R2_PREFIX}{e['id']}.json", flush=True)
        write_index(cat)
    write_index(cat)
    left = [r for r in status_rows(cat) if r[2] != "完成"]
    print(f"本輪結束：{len(left)} 篇未完成", flush=True)
    if not left:
        print("ALL_DONE", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="背景續跑：OCR→切段→翻譯→上傳→索引，全自動")
    ap.add_argument("--status", action="store_true", help="印每篇進度表")
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
    if a.status:
        rows = status_rows(cat)
        for r in rows:
            print(f"{r[0]:18} {r[1]:5} {r[2]:14} {r[3]}/{r[4]}")
        from collections import Counter
        print(f"共 {len(rows)} 篇：" + "、".join(f"{k} {v}" for k, v in Counter(r[2] for r in rows).items()))
        return
    if a.auto:
        try:
            from keep_awake import keep_awake
            keep_awake()
        except Exception:  # noqa: BLE001
            pass
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        auto(cat, only, a.pace)
        return
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
