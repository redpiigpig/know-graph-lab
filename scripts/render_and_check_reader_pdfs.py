#!/usr/bin/env python3
"""把讀本與單字卡的 DOCX 轉成 PDF，並檢查印得出來。

檢查的四件事，都是實際踩過的坑：

* **頁面尺寸**：讀本每一頁必須是 JIS B5 182×257 mm，單字卡是 A4 橫式 297×210 mm。
  版式一改就可能有某一節掉回 Letter，而螢幕上看不出來。
* **字型內嵌**：只要有一個字沒內嵌，送印就會被換成別的字。CJK 混在拉丁字型的 run
  裡最容易發生（NotoSansJP-Thin 那次）。
* **替代字元**：`\\ufffd` 代表字型裡沒有那個字。
* **空白頁**：換頁規則改動後最常見的副作用；一本書多出幾十張白紙才發現就太晚了。

LibreOffice 同時只允許一個 profile，所以每一份都給它自己的 `UserInstallation`，
不然第二份會靜默失敗或吃到前一份的設定。
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.com")

B5 = (182.0, 257.0)
A4_LANDSCAPE = (297.0, 210.0)

TARGETS: dict[str, tuple[Path, tuple[float, float]]] = {}
for stem in ("greek-original-reader-vol1", "greek-original-reader-vol2",
             "latin-original-reader-vol1", "latin-original-reader-vol2",
             "hebrew-original-reader-50-lessons"):
    TARGETS[stem] = (ROOT / "output/original-readers" / f"{stem}.docx", B5)
for stem in ("hebrew-flashcards-1000", "greek-flashcards-volume-1",
             "greek-flashcards-volume-2", "latin-flashcards-volume-1",
             "latin-flashcards-volume-2", "hebrew-flashcards-appendix",
             "greek-flashcards-appendix", "latin-flashcards-appendix",
             "english-flashcards-1000"):
    TARGETS[stem] = (ROOT / "output/flashcards" / f"{stem}.docx", A4_LANDSCAPE)
for stem in ("buddhist-playing-cards", "christian-playing-cards"):
    TARGETS[stem] = (ROOT / "output/playing-cards" / f"{stem}.docx", A4_LANDSCAPE)

MM = 25.4 / 72.0  # PDF 點 -> 毫米


def render(docx: Path, out_dir: Path) -> Path:
    profile = Path(tempfile.mkdtemp(prefix="lo-profile-"))
    try:
        subprocess.run(
            [str(SOFFICE), f"-env:UserInstallation={profile.resolve().as_uri()}",
             "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx)],
            check=True, capture_output=True, timeout=3600,
        )
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = out_dir / (docx.stem + ".pdf")
    if not pdf.is_file():
        raise SystemExit(f"{docx.name}：LibreOffice 沒有產出 PDF")
    return pdf


def check(pdf: Path, expected_mm: tuple[float, float]) -> list[str]:
    problems: list[str] = []
    document = fitz.open(pdf)
    sizes = set()
    blank: list[int] = []
    replacement: list[int] = []
    for number, page in enumerate(document, start=1):
        sizes.add((round(page.rect.width * MM), round(page.rect.height * MM)))
        text = page.get_text().strip()
        if not text and not page.get_images() and not page.get_drawings():
            blank.append(number)
        # 只抓 U+FFFD。空心方框 □ 在希伯來讀本裡是「完成本課」那份自我檢核清單
        # 的打勾框，是刻意印上去的字，不是缺字。
        if "\ufffd" in text:
            replacement.append(number)

    want = (round(expected_mm[0]), round(expected_mm[1]))
    wrong = sorted(size for size in sizes if size != want)
    if wrong:
        problems.append(f"頁面尺寸不是 {want[0]}×{want[1]} mm：{wrong}")
    if blank:
        problems.append(f"空白頁 {len(blank)} 頁：{blank[:12]}")
    if replacement:
        problems.append(f"替代字元出現在第 {replacement[:12]} 頁")

    # get_page_fonts 回 (xref, ext, type, basefont, name, encoding)；
    # ext 是 "n/a"（或 xref 為 0）就表示字型沒有內嵌在檔案裡。
    unembedded: set[str] = set()
    for number in range(document.page_count):
        for xref, ext, _type, basefont, *_ in document.get_page_fonts(number, full=True):
            if ext == "n/a" or xref == 0:
                unembedded.add(basefont)
    if unembedded:
        problems.append(f"未內嵌字型：{sorted(unembedded)}")

    print(f"  {pdf.name}：{document.page_count} 頁，"
          f"{'／'.join(f'{w}×{h}' for w, h in sorted(sizes))} mm"
          + ("　✔" if not problems else ""))
    document.close()
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="轉 PDF 並檢查")
    parser.add_argument("--only", nargs="*", default=[], help="只跑這幾個 stem")
    parser.add_argument("--out", default=str(ROOT / "output/print-masters"))
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    failed = False
    for stem, (docx, expected) in TARGETS.items():
        if args.only and stem not in args.only:
            continue
        if not docx.is_file():
            print(f"  {stem}：找不到 {docx}")
            failed = True
            continue
        problems = check(render(docx, out_dir), expected)
        for line in problems:
            print(f"      ✘ {line}")
        failed = failed or bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
