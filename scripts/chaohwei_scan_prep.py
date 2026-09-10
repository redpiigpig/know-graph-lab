#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《心靈的交會：山間對話》掃描檔前處理 —— 2-up 拆頁、轉正、合併。

來源是四個 PDF（封面／ch1-2／ch3-4／後半），每一個 PDF page 其實是**一張橫躺的
掃描紙，上下疊著兩個書頁**：整體順時針轉 90° 才是正的，轉正後「下半＝前一頁、
上半＝後一頁」（實測頁碼 b 在下、c 在上）。

本腳本只做確定性的影像／版面處理，不碰 LLM：

  split   四檔 → 一份「每頁一個書頁、方向正確」的工作 PDF
  build   依頁碼對照表（OCR 產出）挑頁去重 → 最終合併 PDF

用法：
  python -X utf8 scripts/chaohwei_scan_prep.py split --out c:/tmp/chaohwei/work.pdf
  python -X utf8 scripts/chaohwei_scan_prep.py build --work c:/tmp/chaohwei/work.pdf \
      --keep c:/tmp/chaohwei/keep.json --out c:/tmp/chaohwei/心靈的交會_合併.pdf
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz

SRC_DIR = Path("C:/Users/user/Downloads/drive-download-20260910T035806Z-1-001")

# 掃描檔的先後順序：封面 → 第一至二章 → 第三至四章 → 後半
SOURCES = [
    ("cover", "心靈的交會 封面.pdf"),
    ("ch1-2", "心靈的交會ch1-2.pdf"),
    ("ch3-4", "心靈的交會ch3-4.pdf"),
    ("後半", "心靈的交會 後半.pdf"),
]

ROTATE = 270  # show_pdf_page 的 rotate 與 fitz.Matrix 反向；實測 270 才轉正


def find_split_y(page: fitz.Page, *, band: float = 0.18) -> float:
    """找 2-up 掃描頁上下兩書頁之間的分隔線 y 座標。

    兩頁之間是掃描機留下的深色帶。取頁面中央 ±band 的範圍，逐列算平均灰度，
    最暗的一列即分隔線；整區都不夠暗（例如某頁其實只有一個書頁）就退回正中間。
    純幾何、無 LLM。
    """
    rect = page.rect
    lo = rect.height * (0.5 - band)
    hi = rect.height * (0.5 + band)
    clip = fitz.Rect(0, lo, rect.width, hi)
    pix = page.get_pixmap(matrix=fitz.Matrix(0.25, 0.25), clip=clip, colorspace=fitz.csGRAY)
    if pix.height == 0:
        return rect.height / 2
    rows = []
    data = pix.samples
    for y in range(pix.height):
        base = y * pix.stride
        rows.append(sum(data[base:base + pix.width]) / max(1, pix.width))
    darkest = min(range(len(rows)), key=lambda i: rows[i])
    if rows[darkest] > 200:  # 沒有明顯深色帶
        return rect.height / 2
    return lo + (darkest + 0.5) * (hi - lo) / pix.height


def split_page(src: fitz.Document, pno: int, out: fitz.Document, *, two_up: bool) -> int:
    """把來源第 pno 頁拆進 out。回傳寫出的書頁數。"""
    page = src[pno]
    rect = page.rect
    if not two_up:
        halves = [fitz.Rect(0, 0, rect.width, rect.height)]
    else:
        y = find_split_y(page)
        # 轉正後「下半在前」，所以先寫下半再寫上半
        halves = [fitz.Rect(0, y, rect.width, rect.height), fitz.Rect(0, 0, rect.width, y)]
    for clip in halves:
        # 轉 90° 後長寬互換
        w, h = clip.height, clip.width
        np = out.new_page(width=w, height=h)
        np.show_pdf_page(np.rect, src, pno, clip=clip, rotate=ROTATE)
    return len(halves)


def cmd_split(args: argparse.Namespace) -> None:
    out = fitz.open()
    index: list[dict] = []
    for tag, fname in SOURCES:
        src = fitz.open(SRC_DIR / fname)
        two_up = tag != "cover"
        for pno in range(len(src)):
            before = len(out)
            n = split_page(src, pno, out, two_up=two_up)
            for k in range(n):
                index.append({
                    "work_page": before + k + 1,      # 工作 PDF 的 1-based 頁
                    "source": tag,
                    "src_page": pno + 1,               # 來源 PDF 的 1-based 頁
                    "half": ("single" if not two_up else ("lower" if k == 0 else "upper")),
                })
        src.close()
        print(f"  {tag}: → 累計 {len(out)} 個書頁", flush=True)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, deflate=True)
    out.close()
    idx = dest.with_suffix(".index.json")
    idx.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ {dest} — {len(index)} 個書頁；對照表 {idx}")


def cmd_build(args: argparse.Namespace) -> None:
    keep = json.loads(Path(args.keep).read_text(encoding="utf-8"))
    work = fitz.open(args.work)
    out = fitz.open()
    for wp in keep:
        out.insert_pdf(work, from_page=wp - 1, to_page=wp - 1)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, deflate=True, garbage=3)
    out.close()
    work.close()
    print(f"✅ {dest} — {len(keep)} 頁")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("split", help="四個來源 PDF → 每頁一個書頁的工作 PDF")
    sp.add_argument("--out", required=True)
    sp.set_defaults(func=cmd_split)

    bp = sub.add_parser("build", help="依 keep 清單挑頁 → 最終合併 PDF")
    bp.add_argument("--work", required=True)
    bp.add_argument("--keep", required=True, help="JSON 陣列：要保留的工作 PDF 頁號（1-based，已排序）")
    bp.add_argument("--out", required=True)
    bp.set_defaults(func=cmd_build)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
