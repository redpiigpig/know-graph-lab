# -*- coding: utf-8 -*-
"""替每一本課程讀本做書背標籤 PDF。

    python -X utf8 scripts/build_reader_spine.py            # 掃三門課的成品，逐本出
    python -X utf8 scripts/build_reader_spine.py --paper 100  # 換紙磅數（預設 80g）

書背上只有「115-1　課名」（使用者 2026-09-10 定案），分冊的再加冊別。
**低於 100 頁的不出書背**（使用者 2026-09-11）：那種書背只有幾公釐，裁不準也貼不上。

寬度是**算出來的**：雙面印，張數 = ceil(頁數 / 2)，80g 影印紙一張約 0.104 mm，
再加 2 mm 給封面與膠層。輸出是一張 **B5**（跟讀本同尺寸），中間放實際尺寸的書背條，四周有細框可以裁；
框外印著算出來的尺寸與頁數，拿去給影印店直接講。書背條高 247 mm，比書矮 10 mm——
排滿 257 mm 的話印表機的邊界會把它裁掉。

🚨 紙磅數不同厚度就不同：60g 約 0.08、80g 約 0.104、100g 約 0.13 mm。裝訂前
先量一下書背實際厚度再決定要不要重出——算出來的只是估計值。
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import sys
from pathlib import Path

import fitz

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"G:\我的雲端硬碟\玄奘\博一上\上課")
# 讀本與書背的其他擺放位置，跟 build_course_reader.SHARED_OUTS 對齊。
SHARED_OUTS = (
    Path(r"G:\我的雲端硬碟") / "115-1 課程讀本",                          # 送印那一疊
    Path(r"G:\我的雲端硬碟\資料\知識圖工作室\教學") / "115-1_修課讀本",     # 工作室歸檔
)
CJK = r"C:\Windows\Fonts\mingliu.ttc"
LATIN = r"C:\Windows\Fonts\times.ttf"
MM = 72 / 25.4                      # 1 mm 幾點
# 紙張跟讀本同尺寸：JIS B5（182 × 257 mm）。使用者 2026-09-10：「讀本都是 B5，
# 書背也要是 B5」——同一疊紙進印表機，不必換紙匣也不會被縮放。
PAGE = (182 * MM, 257 * MM)
# 書背條比書略矮 10 mm：B5 的高就是 257 mm，排滿版印表機邊界會裁掉。
B5_H = 247 * MM
SEMESTER = "115-1"

# 檔名 → (課名, 冊別, 放在哪個課程資料夾)
BOOKS = [
    ("宗教研究方法讀本_上冊.pdf", "宗教研究基本問題與研究方法", "上冊", "宗教研究基本問題與研究方法"),
    ("宗教研究方法讀本_下冊.pdf", "宗教研究基本問題與研究方法", "下冊", "宗教研究基本問題與研究方法"),
    ("宗教學理論讀本.pdf", "宗教學理論與方法（一）", "", "宗教學理論與方法(一)"),
    ("初階日文讀本.pdf", "初階宗教學日文文獻選讀", "", "初階宗教學日文文獻選讀"),
]
THICKNESS = {60: 0.08, 70: 0.09, 80: 0.104, 100: 0.13, 120: 0.15}


def spine_width_mm(pages: int, gsm: int) -> float:
    sheets = math.ceil(pages / 2)
    return sheets * THICKNESS.get(gsm, 0.104) + 2.0


def make_spine(src: Path, course: str, volume: str, gsm: int) -> tuple[Path, float, int]:
    doc = fitz.open(src)
    pages = doc.page_count
    doc.close()
    w_mm = spine_width_mm(pages, gsm)
    w = w_mm * MM

    out = fitz.open()
    page = out.new_page(width=PAGE[0], height=PAGE[1])
    page.insert_font(fontname="CJK", fontfile=CJK)
    page.insert_font(fontname="TNR", fontfile=LATIN)

    x0 = (PAGE[0] - w) / 2
    y0 = (PAGE[1] - B5_H) / 2
    rect = fitz.Rect(x0, y0, x0 + w, y0 + B5_H)
    page.draw_rect(rect, color=(0.6,) * 3, width=0.4)

    # 🚨 轉 **270** 度不是 90：書立在架上、書背朝外時，中文書名要由**上往下**讀。
    #    轉 90 度會變成由下往上，整排書擺在一起只有這本是倒的。
    label = f"{SEMESTER}　{course}" + (f"　{volume}" if volume else "")
    size = min(16.0, max(7.0, w * 0.5))          # 字級跟著書背寬度走
    while size > 6 and fitz.Font(fontfile=CJK).text_length(label, size) > B5_H - 20 * MM:
        size -= 0.5
    page.insert_textbox(rect, label, fontname="CJK", fontsize=size,
                        align=fitz.TEXT_ALIGN_CENTER, rotate=270)

    note = f"{src.stem}　{pages} 頁　書背寬 {w_mm:.1f} mm（{gsm}g 紙，雙面）"
    page.insert_text((28, PAGE[1] - 16), note, fontname="CJK", fontsize=9, color=(0.45,) * 3)

    dst = src.with_name(src.stem + "_書背.pdf")
    # 一張紙印幾個字卻 27 MB——`insert_font` 會把整包細明體嵌進去。子集化之後
    # 只留用到的那幾個字，剩不到 100 KB。
    try:
        out.subset_fonts(verbose=False)
    except Exception:
        pass
    out.save(dst, garbage=4, deflate=True)
    out.close()
    return dst, w_mm, pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", type=int, default=80, help="紙磅數（60/70/80/100/120）")
    ap.add_argument("--min-pages", type=int, default=100,
                    help="低於這個頁數就不出書背（太薄貼不上，使用者 2026-09-11 定案）")
    a = ap.parse_args()
    made = 0
    for name, course, volume, folder in BOOKS:
        src = BASE / folder / name
        if not src.exists():
            continue
        doc = fitz.open(src)
        pages = doc.page_count
        doc.close()
        if pages < a.min_pages:
            # 薄的那幾本書背只有幾公釐，印出來裁不準也貼不上，直接不做
            print(f"－ {src.stem}　{pages} 頁（<{a.min_pages}）太薄，不出書背"
                  f"　估寬 {spine_width_mm(pages, a.paper):.1f} mm")
            stale = src.with_name(src.stem + "_書背.pdf")
            if stale.exists():
                stale.unlink()
                print(f"  已刪掉舊的 {stale.name}")
            continue
        dst, w_mm, pages = make_spine(src, course, volume, a.paper)
        print(f"✓ {dst.name}　{pages} 頁　書背寬 {w_mm:.1f} mm")
        # 🚨 其他位置也要有。讀本與書背各有好幾份（跟課的、送印的、工作室歸檔的），
        #    只更新一邊就會拿著舊書背去貼新的書（2026-09-12 讀本本身就這樣過一次）。
        for d in SHARED_OUTS:
            d.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, d / dst.name)
            shutil.copy2(src, d / src.name)
        made += 1
    if not made:
        sys.exit("一本都沒找到——先跑 build_course_reader.py")


if __name__ == "__main__":
    main()
