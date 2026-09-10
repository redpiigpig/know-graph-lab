#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""紙本掃描檔前處理 —— 2-up 拆頁、轉正、合併去重。設定見 scripts/scan_books.py。

館藏掃描檔常見的形態是：一個 PDF page 其實是**一張橫躺的掃描紙，上下疊著兩個
書頁**。本腳本把它還原成「每頁一個書頁、方向正確」的工作 PDF，交給
scan_ocr.py 逐頁 OCR；OCR 讀出印刷頁碼後，再回頭用 build 挑頁去重出成品。

只做確定性的影像／版面處理，不碰 LLM：

  split   來源四檔 → 一份工作 PDF（＋ work_page 對照表）
  build   依 keep 清單挑頁去重 → 最終合併 PDF

  python -X utf8 scripts/scan_prep.py split --book chaohwei-minds
  python -X utf8 scripts/scan_prep.py build --book chaohwei-minds \
      --keep c:/tmp/chaohwei/keep.json --out "…/合併去重.pdf"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz

import scan_books


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


def half_rects(page: fitz.Page, *, two_up: bool, half_order: str) -> list[tuple[str, fitz.Rect]]:
    """一張掃描頁 → [(半頁名, clip)]，**依書的閱讀順序**排。

    半頁順序由設定給定，不從版面猜：橫排書多半是下半頁在前（頁碼 b 在下、
    c 在上），直排書則相反。猜錯的話整本頁序會兩兩顛倒，而每一頁單獨看都正常。
    """
    rect = page.rect
    if not two_up:
        return [("single", fitz.Rect(0, 0, rect.width, rect.height))]
    y = find_split_y(page)
    lower = ("lower", fitz.Rect(0, y, rect.width, rect.height))
    upper = ("upper", fitz.Rect(0, 0, rect.width, y))
    return [lower, upper] if half_order == "lower-first" else [upper, lower]


def cmd_split(args: argparse.Namespace) -> None:
    book = scan_books.get(args.book)
    src_dir = Path(book["src_dir"])
    rotate = book["rotate"]
    out = fitz.open()
    index: list[dict] = []
    for tag, fname, two_up in book["sources"]:
        src = fitz.open(src_dir / fname)
        for pno in range(len(src)):
            for half, clip in half_rects(src[pno], two_up=two_up, half_order=book["half_order"]):
                w, h = clip.height, clip.width  # 轉 90° 後長寬互換
                np = out.new_page(width=w, height=h)
                np.show_pdf_page(np.rect, src, pno, clip=clip, rotate=rotate)
                index.append({"work_page": len(out), "source": tag,
                              "src_page": pno + 1, "half": half})
        src.close()
        print(f"  {tag}: → 累計 {len(out)} 個書頁", flush=True)
    dest = Path(args.out or book["work_pdf"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, deflate=True)
    out.close()
    idx = dest.with_suffix(".index.json")
    idx.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ {dest} — {len(index)} 個書頁；對照表 {idx}")


def cmd_build(args: argparse.Namespace) -> None:
    book = scan_books.get(args.book)
    keep = json.loads(Path(args.keep).read_text(encoding="utf-8"))
    work = fitz.open(args.work or book["work_pdf"])
    out = fitz.open()
    for wp in keep:
        out.insert_pdf(work, from_page=wp - 1, to_page=wp - 1)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # 🚨 garbage=4（跨物件去重）不可省：拆頁時每個半頁都引用了整張來源掃描圖，
    # insert_pdf 會把同一張圖複製一份給每一頁——253 頁就從 8 MB 漲成 214 MB。
    out.save(dest, deflate=True, garbage=4, clean=True)
    out.close()
    work.close()
    size = dest.stat().st_size / 1048576
    print(f"✅ {dest} — {len(keep)} 頁，{size:.1f} MB")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("split", help="來源 PDF → 每頁一個書頁的工作 PDF")
    sp.add_argument("--book", required=True, help=", ".join(scan_books.BOOKS))
    sp.add_argument("--out", help="預設用設定裡的 work_pdf")
    sp.set_defaults(func=cmd_split)

    bp = sub.add_parser("build", help="依 keep 清單挑頁 → 最終合併 PDF")
    bp.add_argument("--book", required=True)
    bp.add_argument("--work")
    bp.add_argument("--keep", required=True, help="JSON 陣列：要保留的工作 PDF 頁號（1-based）")
    bp.add_argument("--out", required=True)
    bp.set_defaults(func=cmd_build)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
