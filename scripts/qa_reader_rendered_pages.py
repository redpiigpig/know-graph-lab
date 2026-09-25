#!/usr/bin/env python3
"""把七冊每一頁都轉成圖，逐頁檢查——文字層看不見的那一半。

前面三道關卡查的都是「文字層說了什麼」：
``render_and_check_reader_pdfs`` 查頁面尺寸與內嵌字型，``audit_reader_pages``
查課次、字級與版心，``audit_printed_exercises`` 查題目配對。它們共用一個盲點：
**抽得出文字不等於印得出來**。裁掉半個字、整頁重覆、某一頁悄悄變成空白、油墨
壓到裁切線——文字層一個字都不會少。

所以這一支把每一頁 rasterise 之後逐頁量：

* 頁數與頁序連續；
* 每一頁的尺寸一致；
* 沒有空白頁（墨水比例低於萬分之 3.5）；
* 沒有兩頁完全相同（整頁重覆是分頁規則改動後最常見的副作用）；
* 沒有墨水壓進最外圈 0.4%（裁切線內側）；封面允許滿版。

判準與 ``qa_hebrew_rendered_pages.py`` 共用同一組函式，那一支原本只服務希伯來。

    python -X utf8 scripts/qa_reader_rendered_pages.py
    python -X utf8 scripts/qa_reader_rendered_pages.py --only latin-original-reader-vol1
    python -X utf8 scripts/qa_reader_rendered_pages.py --dpi 150 --keep
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_hebrew_rendered_pages import analyze  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "output" / "print-masters"
REPORT_DIR = ROOT / "output" / "qa" / "original-readers"

BOOKS = (
    ["hebrew-original-reader-50-lessons"]  # 2026-09-25 稍後回到單冊
    + [f"greek-original-reader-vol{n}" for n in (1, 2)]
    + [f"latin-original-reader-vol{n}" for n in (1, 2)]
    + [f"japanese-original-reader-vol{n}" for n in (1, 2)]
)

# 110 dpi 就夠：這幾項量的是墨水比例、整頁雜湊與邊緣，不是字形。再高只是慢，
# 而七冊兩千五百頁在 150 dpi 要吃掉近一 GB 的暫存。
DEFAULT_DPI = 110


def rasterise(pdf: Path, out_dir: Path, dpi: int) -> int:
    document = fitz.open(pdf)
    out_dir.mkdir(parents=True, exist_ok=True)
    for number, page in enumerate(document, start=1):
        page.get_pixmap(dpi=dpi).save(out_dir / f"page-{number:04d}.png")
    count = document.page_count
    document.close()
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    parser.add_argument("--keep", action="store_true", help="留下 PNG 供人工翻看")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    worst = 0
    for stem in BOOKS:
        if args.only and stem not in args.only:
            continue
        pdf = PDF_DIR / f"{stem}.pdf"
        if not pdf.is_file():
            print(f"✘ {stem}：找不到 PDF")
            worst = 1
            continue
        work = Path(tempfile.mkdtemp(prefix=f"raster-{stem}-"))
        try:
            pages = rasterise(pdf, work, args.dpi)
            result = analyze(work, pages)
            mark = "✔" if result["passed"] else "✘"
            print(f"{mark} {stem}：{result['actualPages']} 頁逐頁檢查")
            for name, ok in result["checks"].items():
                if not ok:
                    print(f"    ✘ {name}")
            if result["blankPages"]:
                print(f"    空白頁：{result['blankPages'][:12]}")
            if result["duplicateGroups"]:
                print(f"    整頁重覆：{result['duplicateGroups'][:6]}")
            if result["edgeIntrusions"]:
                rows = [row["page"] for row in result["edgeIntrusions"]]
                print(f"    墨水壓到最外圈：{rows[:12]}")
            report = REPORT_DIR / f"{stem}-rendered-pages.json"
            # records 是每一頁一筆，留著會讓報告變成幾 MB；只留判斷需要的部分。
            summary = {k: v for k, v in result.items() if k != "records"}
            report.write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                              encoding="utf-8")
            worst |= 0 if result["passed"] else 1
            if args.keep:
                kept = REPORT_DIR / f"{stem}-pages"
                shutil.rmtree(kept, ignore_errors=True)
                shutil.move(str(work), str(kept))
                print(f"    PNG 留在 {kept}")
        finally:
            if not args.keep:
                shutil.rmtree(work, ignore_errors=True)
    return worst


if __name__ == "__main__":
    sys.exit(main())
