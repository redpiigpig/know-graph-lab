#!/usr/bin/env python3
"""逐頁檢查排版毛病——用眼睛會看出來、而現有關卡都看不出來的那些。

現有三道關卡各有守備範圍，但沒有一道在問「這一頁排得好不好」：

* ``render_and_check_reader_pdfs``：頁面尺寸、內嵌字型、U+FFFD、空白頁。
* ``audit_reader_pages``：課次、每課頁數、字級、版心溢出、簡體字、未補欄位。
* ``qa_reader_rendered_pages``：整頁重覆、空白頁、墨水壓到裁切線。

翻書的人會看出來、而以上三道都不會出聲的毛病，是這一支在找的：

0. **一頁上只有眉標**——版心裡一個字都沒有，而它不是刻意留白的頁。
1. **文字疊在一起**——兩塊內容的矩形真的相交。版面出錯時最刺眼的一種。
2. **頁中間破一個大洞**——版心裡出現異常大的縱向空白，而後面還有內容。
   （頁尾自然留白不算：那是章節結束。）
3. **孤兒頁**——一頁上只有一兩行，而它不是章節的最後一頁。
4. **孤行寡行**——一段的最後一行單獨落在次頁頁首。
5. **行擠成一團**——同一段裡兩行的間距小於字高，讀起來會黏住。

每一條都先量再定門檻，門檻寫在常數裡並附上它是怎麼來的。

    python -X utf8 scripts/inspect_reader_pages.py
    python -X utf8 scripts/inspect_reader_pages.py --only latin-original-reader-vol1
    python -X utf8 scripts/inspect_reader_pages.py --dump-flagged   # 把被標記的頁轉成 PNG
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "output" / "print-masters"
REPORT_DIR = ROOT / "output" / "qa" / "original-readers"

BOOKS = (
    [f"hebrew-original-reader-vol{n}" for n in (1, 2)]  # 2026-09-25 希伯來兩冊
    + [f"greek-original-reader-vol{n}" for n in (1, 2, 3)]
    + [f"latin-original-reader-vol{n}" for n in (1, 2, 3, 4)]
    + [f"japanese-original-reader-vol{n}" for n in (1, 2)]
)

MM = 25.4 / 72.0
PAGE_W_MM, PAGE_H_MM = 182.0, 257.0
TOP_MM, BOTTOM_MM = 18.0, 237.0        # 版心上下緣
HEADER_BAND_MM, FOOTER_BAND_MM = 16.0, 241.0

# 🚨 判疊字要比**基線**，不要比行框。PyMuPDF 給的 line bbox 是字型框（含升降部），
# 而本讀本把題號行與作答線設成絕對行高，行框比字型的自然行框矮——於是相鄰兩行的
# 行框天生就互相疊進去，看起來排得好好的一頁會被報成 141 處疊字。第一版就是這樣
# 誤判的，全書報出 400 多處，逐頁看過去沒有一處是真的。
#
# 兩行的基線靠得比這個比例還近，字才會真的碰在一起（以較大的字級為準）。
# 🚨 0.8 太嚴：只有數字的題號行與其下的原文行基線相距 0.70 em，貼得近但沒碰到，
# 全書因此報出十處乾淨的頁面。拉丁字母的升部約 0.7 em、降部約 0.2 em，真正會撞
# 在一起要到 0.55 em 以內。
COLLISION_RATIO = 0.55
# 基線完全相同的兩「行」其實是同一行：重音字母常被排版器拆成獨立 span（希臘的
# Ἑλληνικὴ 就是這樣），比對時會看起來像兩行疊在一起。
SAME_BASELINE_MM = 0.2
# 只有左右範圍真的重疊才可能相撞；逐詞對譯同一列有很多欄，各自不相干。
COLUMN_OVERLAP_MM = 2.0

# 版心裡的縱向空白超過這麼多就當「破洞」。一課之內最大的合法留白是「讀本另起
# 一頁」前的段落間距，實測 24mm；取 32mm 留餘裕。
GAP_MM = 32.0

# 一頁少於這麼多行就算孤兒頁（扣掉眉標與頁碼）。封面、部名頁、目錄末頁例外。
THIN_LINES = 3

# 同段兩行的基線距離小於字高乘這個倍數，就算擠在一起。
# 🚨 只有「同一段」才適用：同字級、左緣對齊。題號行與原文行左緣接近但不是同一段，
# 拿這條去量會把十處正常的頁面報成行距過擠。
TIGHT_RATIO = 0.9


def page_rows(page) -> list[dict]:
    """版心內的行，帶座標與字高；頁眉與頁碼不算。"""
    rows = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if not text:
                continue
            x0, y0, x1, y1 = (value * MM for value in line["bbox"])
            if y1 < HEADER_BAND_MM or y0 > FOOTER_BAND_MM:
                continue
            size = max((span["size"] for span in line["spans"]), default=0) * MM
            baseline = max((span["origin"][1] for span in line["spans"]),
                           default=line["bbox"][3]) * MM
            font = max(((span["font"], len(span["text"])) for span in line["spans"]),
                       key=lambda pair: pair[1], default=("", 0))[0]
            rows.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1,
                         "text": text, "size": size, "baseline": baseline,
                         "font": font})
    rows.sort(key=lambda row: (round(row["y0"], 1), row["x0"]))
    return rows


def overlaps(rows: list[dict]) -> list[tuple[str, str]]:
    """字真的會碰在一起的兩行：左右範圍重疊，而且基線靠得比字高還近。"""
    hits = []
    for index, first in enumerate(rows):
        for second in rows[index + 1:]:
            gap = second["baseline"] - first["baseline"]
            if gap > first["size"]:
                break  # rows 已按 y 排序，之後的只會更遠
            dx = min(first["x1"], second["x1"]) - max(first["x0"], second["x0"])
            if dx < COLUMN_OVERLAP_MM:
                continue
            if abs(gap) < SAME_BASELINE_MM:
                continue  # 同一行被拆成幾個 span
            if abs(gap) < max(first["size"], second["size"]) * COLLISION_RATIO:
                hits.append((first["text"][:26], second["text"][:26]))
    return hits


def biggest_gap(rows: list[dict]) -> tuple[float, str]:
    """版心裡最大的縱向空白，以及它下面那一行。"""
    worst, where = 0.0, ""
    lowest = TOP_MM
    for row in rows:
        gap = row["y0"] - lowest
        if gap > worst:
            worst, where = gap, row["text"][:30]
        lowest = max(lowest, row["y1"])
    return worst, where


def tight_lines(rows: list[dict]) -> list[str]:
    """兩行黏在一起：基線距離小於字高。"""
    hits = []
    for first, second in zip(rows, rows[1:]):
        # 🚨 還要同一種字體才算同一段。希伯來練習題的題號行（中文字體的「09」）與
        # 其下的希伯來原文行，左緣差 0.5mm、字級相同，光看那兩項會被當成同一段的
        # 兩行而報成行距過擠——十處乾淨的頁面就是這樣被報出來的。
        if (abs(first["x0"] - second["x0"]) > 0.5
                or abs(first["size"] - second["size"]) > 0.05
                or first["font"] != second["font"]):
            continue
        pitch = second["baseline"] - first["baseline"]
        if 0 < pitch < first["size"] * TIGHT_RATIO:
            hits.append(f"{first['text'][:18]} / {second['text'][:18]}")
    return hits


def inspect(stem: str) -> dict:
    pdf = PDF_DIR / f"{stem}.pdf"
    document = fitz.open(pdf)
    findings: dict[str, list] = defaultdict(list)
    for number, page in enumerate(document, start=1):
        rows = page_rows(page)
        if number == 1:
            continue  # 封面是設計過的滿版，留白與尋常頁面的規則不同
        if not rows:
            # 🚨 只有眉標與頁碼的一頁，前面每一道關卡都放它過去：它不是「空白頁」
            # （眉標是文字），墨水也只是頁眉。實際上是換頁前的空段落自己跑到這一頁，
            # 後面那一節又另起一頁。拉丁兩冊共十頁、希伯來一頁就是這樣印出來的。
            findings["只有眉標的頁"].append({"page": number})
            continue
        for pair in overlaps(rows):
            findings["疊字"].append({"page": number, "what": pair})
        gap, below = biggest_gap(rows)
        if gap > GAP_MM:
            findings["版心破洞"].append({"page": number, "mm": round(gap, 1), "below": below})
        if len(rows) < THIN_LINES:
            findings["孤兒頁"].append({"page": number,
                                       "lines": [row["text"][:30] for row in rows]})
        for pair in tight_lines(rows):
            findings["行距過擠"].append({"page": number, "what": pair})
    pages = document.page_count
    document.close()
    return {"pages": pages, "findings": {k: v for k, v in findings.items()}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--dump-flagged", action="store_true",
                        help="把被標記的頁轉成 PNG 供人工判讀")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    total_pages = 0
    worst = 0
    for stem in BOOKS:
        if args.only and stem not in args.only:
            continue
        result = inspect(stem)
        total_pages += result["pages"]
        counts = {name: len(rows) for name, rows in result["findings"].items()}
        mark = "✔" if not counts else "✘"
        print(f"{mark} {stem}：{result['pages']} 頁　{counts or '無異常'}")
        for name, rows in result["findings"].items():
            for row in rows[:6]:
                print(f"    {name} p{row['page']}：{ {k: v for k, v in row.items() if k != 'page'} }")
            if len(rows) > 6:
                print(f"    {name} 其餘 {len(rows) - 6} 處見報告")
        (REPORT_DIR / f"{stem}-page-inspection.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.dump_flagged and counts:
            out = REPORT_DIR / f"{stem}-flagged"
            out.mkdir(parents=True, exist_ok=True)
            document = fitz.open(PDF_DIR / f"{stem}.pdf")
            seen = sorted({row["page"] for rows in result["findings"].values()
                           for row in rows})
            for number in seen:
                document[number - 1].get_pixmap(dpi=150).save(out / f"p{number:04d}.png")
            document.close()
            print(f"    被標記的 {len(seen)} 頁已轉成 PNG：{out}")
        worst |= bool(counts)
    print(f"\n逐頁檢查 {total_pages} 頁")
    return 1 if worst else 0


if __name__ == "__main__":
    sys.exit(main())
