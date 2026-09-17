#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
元文琪譯《阿維斯塔》—— 從掃描頁**幾何地**找回 MinerU 丟掉的節號。

    python scripts/avesta_yuan_lines.py --probe 46
    python scripts/avesta_yuan_lines.py --scan 36 376 --out output/yuan_markers.json

═══════════ 為什麼需要這支 ═══════════

🚨 **MinerU 會把「一」「二」「三」「十」整個丟掉。**
   這四個字是純橫豎筆畫，版面分析把置中獨立成行的它們判成**分隔線**而非文字。
   實測全書正文（掃描 595 頁）獨立成行的中文數字出現次數：

       一 1 次　二 3 次　三 15 次　┃　四 29　五 30　六 29　七 22　八 26　九 28

   「四」以後都在 25–30 之間，「一二三」幾乎全滅，「十」也從 28 掉到 9。
   而這本書的節號就是這樣印的（置中、獨立一行），所以**每一章的前三節與第十節
   都失去了節號**——頁面上看起來只是幾段沒有編號的文字，完全看不出少了東西。

   這件事會直接毀掉逐節對照：節號對不上就只能按段落順序硬湊，
   而硬湊出來的版面完全正常，只是每一節的中譯都配錯一格。

═══════════ 作法：不讀字，只找位置 ═══════════

不需要辨識那四個字。只要知道**哪幾行是節號行**，就能依序編號，
再拿 MinerU 沒丟掉的「四、五、六…」當**校驗碼**——
若第 4 個節號行對應的文字不是「四」，就表示偵測錯了，該頁整頁退回。

節號行的幾何特徵（實測 2011 年商務版，三項同時成立才算）：
  一、**窄**：橫向墨跡寬度不到正文寬度的 20%
  二、**置中**：墨跡中心與版心中線的偏移小於版心寬度的 8%
  三、**孤立**：上下都是空白（本身就是一整行）

配對方式：**逐行對位**。MinerU 保留了原書的斷行（同一段的兩行是分開的兩筆），
所以幾何偵測到的「非節號行」數量必須與 MinerU 給的行數相等；
不相等就表示有行被吃掉或多切，該頁退回，不猜。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PDF = (r"G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館/世界宗教/波斯宗教/祆教/"
       r"杜斯特哈赫選編；元文琪譯，阿維斯塔——瑣羅亞斯德教聖書（2011）.pdf")
JSONL = r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks/6d731f04-664d-4459-826e-0dba1dbefc4b.jsonl"

# ── 幾何門檻（實測 2011 年商務版）──
RENDER_SCALE = 2.0
INK_THRESHOLD = 160      # 灰階低於此值算墨
MIN_ROW_INK = 3          # 一行至少要有幾個墨點才算有字
MARKER_MAX_WIDTH = 0.20  # 節號行的墨寬上限（佔版心寬度）
MARKER_MAX_OFFSET = 0.08 # 節號行中心偏離版心中線的上限
HEADER_TOP = 0.10        # 頁首（書名頁碼）佔全頁高度的比例，切掉
FOOTER_BOTTOM = 0.92     # 頁尾與註腳分隔線以下，切掉


# ────────────────────────── 純函式 ──────────────────────────

def row_bands(ink_per_row: list[int], min_ink: int = MIN_ROW_INK) -> list[tuple[int, int]]:
    """把「每一列的墨點數」切成一段一段的文字行，回 [(起列, 訖列), …]。

    >>> row_bands([0, 0, 5, 6, 0, 0, 7, 0], min_ink=3)
    [(2, 3), (6, 6)]
    >>> row_bands([0, 0, 0])
    []
    """
    bands: list[tuple[int, int]] = []
    start = None
    for i, n in enumerate(ink_per_row):
        if n >= min_ink and start is None:
            start = i
        elif n < min_ink and start is not None:
            bands.append((start, i - 1))
            start = None
    if start is not None:
        bands.append((start, len(ink_per_row) - 1))
    return bands


def is_marker_band(x0: int, x1: int, body_x0: int, body_x1: int) -> bool:
    """這一行是不是節號行？窄 ＋ 置中，兩項都要成立。

    >>> is_marker_band(480, 520, 200, 800)   # 窄且置中
    True
    >>> is_marker_band(200, 800, 200, 800)   # 整行寬度，正文
    False
    >>> is_marker_band(200, 260, 200, 800)   # 窄但靠左（如註腳序號）
    False
    """
    body_w = body_x1 - body_x0
    if body_w <= 0:
        return False
    if (x1 - x0) > MARKER_MAX_WIDTH * body_w:
        return False
    centre = (x0 + x1) / 2
    body_centre = (body_x0 + body_x1) / 2
    return abs(centre - body_centre) <= MARKER_MAX_OFFSET * body_w


def merge_marker_bands(bands: list[dict], max_gap: int) -> list[dict]:
    """把同一個字被拆開的筆畫併回一個節號。

    🚨 這是本支最重要的一個發現：偵測出來的不是「一個節號行」，而是**每一橫各自一行**
       ——「一」一條、「二」兩條、「三」三條。所以合併之後的筆畫數**直接就是數字**，
       根本不必辨識字形。這也正好解釋了 MinerU 為什麼會丟掉它們：
       在版面分析眼中，它們就是一到三條孤零零的水平線。

    回傳的每一項多出 'strokes'（併了幾條）與 'height'（整字的高度）。

    >>> b = [{'y0': 10, 'y1': 12, 'x0': 500, 'x1': 540, 'marker': True},
    ...      {'y0': 20, 'y1': 22, 'x0': 500, 'x1': 540, 'marker': True},
    ...      {'y0': 90, 'y1': 92, 'x0': 500, 'x1': 540, 'marker': True}]
    >>> [(m['strokes'], m['y0']) for m in merge_marker_bands(b, max_gap=30)]
    [(2, 10), (1, 90)]
    """
    out: list[dict] = []
    for b in bands:
        if out and (b["y0"] - out[-1]["y1"]) <= max_gap:
            prev = out[-1]
            prev["y1"] = b["y1"]
            prev["x0"] = min(prev["x0"], b["x0"])
            prev["x1"] = max(prev["x1"], b["x1"])
            prev["strokes"] += 1
        else:
            out.append({**b, "strokes": 1})
    for m in out:
        m["height"] = m["y1"] - m["y0"]
    return out


def marker_value(m: dict, thin: int) -> int | None:
    """由筆畫數與字高判斷節號的值。判不出來回 None——**不猜**。

    一／二／三 是 1–3 條孤立的橫劃；「十」是一橫加一豎，併起來只有一條
    但**字高明顯大於一條橫劃**。四以上筆畫太雜，交給 MinerU 讀到的文字，
    本函式不處理（回 None）。

    >>> marker_value({'strokes': 1, 'height': 2}, thin=8)
    1
    >>> marker_value({'strokes': 3, 'height': 21}, thin=8)
    3
    >>> marker_value({'strokes': 1, 'height': 24}, thin=8)   # 十
    10
    >>> marker_value({'strokes': 5, 'height': 30}, thin=8) is None
    True
    """
    if m["strokes"] == 1 and m["height"] > thin:
        return 10
    if 1 <= m["strokes"] <= 3:
        return m["strokes"]
    return None


CN_DIGITS = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九"}


def cn_number(n: int) -> str:
    """阿拉伯數字 → 這本書用的中文數字寫法。

    >>> [cn_number(n) for n in (1, 3, 10, 11, 20, 24, 30, 105)]
    ['一', '三', '十', '十一', '二十', '二十四', '三十', '一百零五']
    """
    if n < 10:
        return CN_DIGITS[n]
    if n < 20:
        return "十" + (CN_DIGITS[n - 10] if n > 10 else "")
    if n < 100:
        t, o = divmod(n, 10)
        return CN_DIGITS[t] + "十" + (CN_DIGITS[o] if o else "")
    h, rest = divmod(n, 100)
    if rest == 0:
        return CN_DIGITS[h] + "百"
    if rest < 10:
        return CN_DIGITS[h] + "百零" + CN_DIGITS[rest]
    return CN_DIGITS[h] + "百" + cn_number(rest)


def verify_against_survivors(
    detected: list[int],
    survivors: dict[int, str],
) -> list[str]:
    """拿 MinerU 沒丟掉的節號當校驗碼，回傳不符之處的說明（空 list ＝ 全對）。

    detected 是偵測到的節號行在該頁的序號（第幾個節號行 → 推定的節號值），
    survivors 是 MinerU 實際讀到的 {推定節號: 文字}。

    >>> verify_against_survivors([4, 5, 6], {4: '四', 5: '五', 6: '六'})
    []
    >>> verify_against_survivors([4, 5], {4: '五'})
    ['第 4 個節號推定為「四」，但 MinerU 讀到的是「五」']
    """
    bad: list[str] = []
    for n in detected:
        got = survivors.get(n)
        if got is not None and got != cn_number(n):
            bad.append(f"第 {n} 個節號推定為「{cn_number(n)}」，但 MinerU 讀到的是「{got}」")
    return bad


# ────────────────────────── 影像 ──────────────────────────

def classify_rule(h: int, w: int, fill: float, page_w: int) -> str | None:
    """這一條細線是頁首線、腳註線，還是都不是？（實測 2011 年商務版的數值）

    三種細線在同一頁上寬度差了一個數量級，分得很開：
        頁首線   h=3  w=747 (77% 頁寬)  fill=0.58
        腳註線   h=3  w=249 (26% 頁寬)  fill=0.47
        節號橫劃 h=3  w= 28 ( 3% 頁寬)  fill=0.71   ← 這個不是線，是「一」的一橫

    >>> classify_rule(3, 747, 0.58, 975)
    'header'
    >>> classify_rule(3, 249, 0.47, 975)
    'footnote'
    >>> classify_rule(3, 28, 0.71, 975) is None
    True
    >>> classify_rule(26, 692, 0.35, 975) is None      # 正文行，不是線
    True
    """
    if h > 4:
        return None
    r = w / page_w
    # 🚨 fill 的門檻不能省。掃描髒點也是又細又長（實測 p47 有一條 h=1、寬 16%、
    #    fill=0.02 的淡痕）；當成腳註線去切，那一頁後半段整個被丟掉，
    #    而剩下的部分讀起來完全正常。
    if r > 0.55 and fill > 0.25:
        return "header"
    if 0.12 < r < 0.50 and fill > 0.30:
        return "footnote"
    return None


def page_lines(pdf_path: str, page_no: int) -> list[dict]:
    """回傳該頁**正文區**的行清單：[{'y0','y1','x0','x1','h','fill','marker'}, …]。

    切掉頁首（含頁首線）與腳註（自腳註線起）。兩者都靠實測的細線特徵定位，
    不用固定比例——固定比例在章首頁（正文短、腳註多）會切錯。
    """
    import fitz
    import numpy as np

    doc = fitz.open(pdf_path)
    pix = doc[page_no - 1].get_pixmap(matrix=fitz.Matrix(RENDER_SCALE, RENDER_SCALE),
                                      colorspace=fitz.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = img < INK_THRESHOLD

    rows: list[dict] = []
    for y0, y1 in row_bands(ink.sum(axis=1).tolist()):
        sub = ink[y0:y1 + 1, :]
        cols = sub.sum(axis=0).nonzero()[0]
        if not cols.size:
            continue
        x0, x1 = int(cols[0]), int(cols[-1])
        h = y1 - y0 + 1
        fill = float(sub.sum()) / ((x1 - x0 + 1) * h)
        rows.append({"y0": y0, "y1": y1, "x0": x0, "x1": x1, "h": h, "fill": fill,
                     "rule": classify_rule(h, x1 - x0, fill, pix.width)})

    # 頁首線以上全部丟掉（書名與頁碼）；沒有頁首線就從頭算起。
    head = max((i for i, r in enumerate(rows) if r["rule"] == "header" and i < 4), default=-1)
    rows = rows[head + 1:]
    # 腳註線以下全部丟掉（註文不屬正文，MinerU 也沒收）。
    foot = next((i for i, r in enumerate(rows) if r["rule"] == "footnote"), None)
    if foot is not None:
        rows = rows[:foot]
    if not rows:
        return []

    # 版心左右界只看**真正的文字行**（高度夠），否則會被節號的細橫劃拉偏。
    text = [r for r in rows if r["h"] > 10]
    if not text:
        return []
    body_x0 = min(r["x0"] for r in text)
    body_x1 = max(r["x1"] for r in text)

    for r in rows:
        r["marker"] = (r["h"] <= 6
                       and is_marker_band(r["x0"], r["x1"], body_x0, body_x1))

    # 🚨 掃描雜訊要濾掉，否則行數永遠對不上。真正的漢字行高約 25px（2 倍放大），
    #    連只有一個字的行也是；高度不到 10px 又不是節號橫劃的，就是髒點或碎片
    #    （實測 p47 有 h=1 的墨點與 h=5 的碎片各一）。
    #    這是「幾何行數比 MinerU 多」的主因——219 頁對不上裡，+1／+2／+3 佔了 168 頁。
    return [r for r in rows if r["marker"] or r["h"] >= 10]


def main() -> int:
    ap = argparse.ArgumentParser(description="從掃描頁幾何地找回被丟掉的節號")
    ap.add_argument("--probe", type=int, help="看單頁的偵測結果")
    ap.add_argument("--scan", nargs=2, type=int, metavar=("FROM", "TO"))
    ap.add_argument("--out", default=str(ROOT / "output" / "yuan_markers.json"))
    a = ap.parse_args()

    if a.probe:
        lines = page_lines(PDF, a.probe)
        src = {json.loads(l)["page_number"]: json.loads(l)
               for l in open(JSONL, encoding="utf-8") if l.strip()}
        text_lines = [t for t in src[a.probe]["content"].split("\n") if t.strip()]
        geo_text = [ln for ln in lines if not ln["marker"]]
        print(f"p{a.probe}：幾何行 {len(lines)}（節號 {len(lines) - len(geo_text)}／"
              f"正文 {len(geo_text)}）　MinerU 行 {len(text_lines)}")
        print("  對得上" if len(geo_text) == len(text_lines) else "  🚨 行數對不上，該頁應退回")
        ti = 0
        for ln in lines:
            if ln["marker"]:
                print(f"    [節號行] y={ln['y0']}–{ln['y1']} x={ln['x0']}–{ln['x1']}")
            else:
                print(f"    {text_lines[ti][:44] if ti < len(text_lines) else '(缺)'}")
                ti += 1
        return 0

    if a.scan:
        lo, hi = a.scan
        src = {json.loads(l)["page_number"]: json.loads(l)
               for l in open(JSONL, encoding="utf-8") if l.strip()}
        ok = bad = 0
        result = {}
        for pg in range(lo, hi + 1):
            if pg not in src:
                continue
            lines = page_lines(PDF, pg)
            text_lines = [t for t in src[pg]["content"].split("\n") if t.strip()]
            geo_text = [ln for ln in lines if not ln["marker"]]
            match = len(geo_text) == len(text_lines)
            ok, bad = (ok + 1, bad) if match else (ok, bad + 1)
            result[pg] = {
                "match": match,
                "markers_at": [i for i, ln in enumerate(lines) if ln["marker"]],
                "geo_text": len(geo_text), "mineru_text": len(text_lines),
            }
            if pg % 40 == 0:
                print(f"  …p{pg}  對得上 {ok}／對不上 {bad}")
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"完成：{ok} 頁行數吻合、{bad} 頁不吻合 → {a.out}")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
