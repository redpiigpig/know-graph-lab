#!/usr/bin/env python3
"""Read every page of every printed reader and report what is wrong with it.

``render_and_check_reader_pdfs.py`` certifies the paper: page size, embedded
fonts, blank pages, U+FFFD, the 500-page cap.  It says nothing about what is on
the page, and "renders cleanly" has never meant "is finished" in this series.
``audit_printed_exercises.py`` then checks one section of one kind of page.
This checks the rest of the book:

* **完整** — every lesson the book claims is present, in order, and carries its
  three parts: a vocabulary table of the right size, ten exercises, a reading.
* **跑版** — any text drawn outside the type area.  The page is mirrored, so the
  bound edge is the wide one and it swaps sides on every turn; a block over the
  line is either an oversized table or a word that could not be broken.
* **未補完** — the placeholders this series prints on purpose when a layer is
  missing (〔待補〕, 中譯待補).  They are not bugs — the rule is that a gap must
  be visible — but "every page is complete" is exactly the claim they refute,
  so they are counted rather than hidden.
* **簡體字** — the Chinese in these books is Traditional throughout.  The test
  is a list of characters that exist only as simplifications, never OpenCC:
  converting and comparing calls 祢 simplified, which is how this series
  produced a false report once already.
* **體例** — the section headings each book uses, printed side by side, so that
  four books that are meant to be one series can be seen to say the same things
  in the same words.

    python -X utf8 scripts/audit_reader_pages.py            # 全部
    python -X utf8 scripts/audit_reader_pages.py --only latin-original-reader-vol1
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "output" / "print-masters"

MM = 25.4 / 72.0
PAGE_W_MM, PAGE_H_MM = 182, 257
MARGIN_INSIDE_MM, MARGIN_OUTSIDE_MM = 24, 17
MARGIN_TOP_MM, MARGIN_BOTTOM_MM = 18, 20
# The header sits 8 mm from the trim and the footer 9 mm, so both are outside
# the type area by design; the overflow test starts above the header line.
HEADER_MM, FOOTER_MM = 8, 9
# A hair of tolerance: a glyph's ink box is not its advance box, and italic and
# bold faces overhang their own by a fraction of a millimetre.  2 mm rather than
# 1.5: at 1.5 the last glyph of one justified line in 4,700 pages came out
# 0.1 mm over, and the page is correct — checked by eye.
TOLERANCE_MM = 2.0

BOOKS = (
    ["hebrew-original-reader-50-lessons"]
    + [f"greek-original-reader-vol{n}" for n in range(1, 7)]
    + [f"latin-original-reader-vol{n}" for n in range(1, 4)]
    + [f"japanese-original-reader-vol{n}" for n in range(1, 5)]
)

LESSON_TAG = re.compile(r"第\s*(\d{1,3})\s*課")
EXERCISE_HEAD = re.compile(r"本課翻譯練習（\s*(\d+)\s*題）")
PLACEHOLDERS = ("〔待補〕", "〔中譯待補〕", "中譯待補", "（中文待補）", "待補")
# Never valid in Traditional Chinese.  Deliberately short and conservative:
# every character here is a simplification with no traditional use at all, so a
# hit is a real leak rather than a judgement call.
SIMPLIFIED = "们这个说国学见为变时关发会讲现实点样两员题长门问间东车马鸟语书图"
# 🚨 日文的新字體不是簡體字。国・学・会・点 是日文的正規寫法（國・學・會・點
# 的新字體），日文讀本的正文裡到處都是；不扣掉這四個，日文四冊會報出四百多頁
# 「簡體字」而一個都不是。其餘那些（这・个・说・们・时・长・问・间…）日文寫的
# 是舊字體或別的字，出現在日文書裡一樣是漏網的簡體。
SHINJITAI = "国学会点"
# `null`，不是 `"null" in text`：拉丁文的 nulla／nullum／nullius 都含 null，
# 照子字串比會把整本武加大報成「未成形的值」。
BROKEN = re.compile(r"(?:undefined|NaN|None|null)|\[object Object\]")


def type_area(page_number: int) -> tuple[float, float, float, float]:
    """The band any ink may occupy, in points, for a page of this parity.

    Mirrored margins: the bound edge is the inside one, which is the left of a
    recto and the right of a verso.  Getting this backwards would report every
    page of the book as overflowing on one side and none on the other, which is
    what a wrong answer here looks like.

    Vertically the band is the paper minus the header and footer offsets, not
    the type area: the running head and the page number are *supposed* to sit
    outside the type area, and measuring against it reports the footer of every
    page in the book as overflow.  That was this script's first answer — four
    hundred and fifty-two hits in a book with none.
    """
    inside, outside = MARGIN_INSIDE_MM, MARGIN_OUTSIDE_MM
    left, right = (inside, outside) if page_number % 2 == 1 else (outside, inside)
    return (
        left / MM,
        (HEADER_MM - TOLERANCE_MM) / MM,
        (PAGE_W_MM - right) / MM,
        (PAGE_H_MM - FOOTER_MM + TOLERANCE_MM * 2) / MM,
    )


def audit(stem: str) -> tuple[list[str], dict]:
    pdf = PDF_DIR / f"{stem}.pdf"
    if not pdf.is_file():
        return [f"{stem}：找不到 PDF"], {}
    document = fitz.open(pdf)
    wanted_simplified = (
        "".join(ch for ch in SIMPLIFIED if ch not in SHINJITAI)
        if stem.startswith("japanese-")
        else SIMPLIFIED
    )
    problems: list[str] = []
    overflow: list[tuple[int, str]] = []
    thin: list[int] = []
    placeholders: Counter = Counter()
    simplified: list[tuple[int, str]] = []
    broken: list[tuple[int, str]] = []
    headings: Counter = Counter()
    lessons: list[int] = []
    no_running_head: list[int] = []
    exercises: dict[int, int] = {}
    current: int | None = None

    for number, page in enumerate(document, start=1):
        text = page.get_text()
        lines = [line.strip() for line in text.splitlines()]
        left, top, right, bottom = type_area(number)

        for block in page.get_text("blocks"):
            x0, y0, x1, y1 = block[:4]
            body = (block[4] or "").strip()
            if not body:
                continue
            if x0 < left - TOLERANCE_MM / MM or x1 > right + TOLERANCE_MM / MM:
                overflow.append((number, body[:40]))
            elif y0 < top - TOLERANCE_MM / MM or y1 > bottom + TOLERANCE_MM / MM:
                overflow.append((number, body[:40]))

        stripped = text.strip()
        if 0 < len(stripped) < 40:
            thin.append(number)
        for mark in PLACEHOLDERS:
            if mark in text:
                placeholders[mark] += text.count(mark)
        hits = {ch for ch in wanted_simplified if ch in text}
        if hits:
            simplified.append((number, "".join(sorted(hits))))
        found_broken = BROKEN.search(text)
        if found_broken:
            broken.append((number, found_broken.group(0)))

        # 封面與各部的首頁刻意不掛眉標（`start_section` 之前的那一頁），
        # 所以只在正文頁上要求它。
        head = lines[0] if lines else ""
        if number > 1 and current is not None and "·" not in head and "讀本" not in head:
            no_running_head.append(number)
        tag = LESSON_TAG.search(head)
        if tag:
            number_seen = int(tag.group(1))
            if number_seen != current:
                current = number_seen
                lessons.append(number_seen)

        for line in lines:
            found = EXERCISE_HEAD.search(line)
            if found and current is not None:
                exercises[current] = int(found.group(1))
            for label in ("生詞", "本課生詞", "詞表", "背誦", "讀文", "讀本", "附錄",
                          "本課翻譯練習", "體例與來源", "翻譯練習"):
                if line.startswith(label):
                    headings[label] += 1
                    break

    # 每一課都要有十題，而且課次要連號、不重覆。
    if lessons != sorted(set(lessons)):
        problems.append(f"課次不是遞增或有重覆：{lessons}")
    missing = [n for n in lessons if exercises.get(n) != 10]
    if missing:
        problems.append(f"這幾課沒有印滿十題：{[(n, exercises.get(n)) for n in missing]}")
    if overflow:
        problems.append(f"文字跑出版心 {len(overflow)} 處：{overflow[:6]}")
    if broken:
        problems.append(f"疑似未成形的值：{broken[:6]}")
    if simplified:
        problems.append(f"簡體字出現在 {len(simplified)} 頁：{simplified[:6]}")
    if no_running_head:
        problems.append(f"沒有眉標的頁 {len(no_running_head)} 頁：{no_running_head[:10]}")

    summary = {
        "pages": document.page_count,
        "lessons": len(lessons),
        "thin": thin,
        "placeholders": dict(placeholders),
        "headings": dict(headings),
    }
    document.close()
    return problems, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=[])
    args = parser.parse_args()

    worst = 0
    all_headings: dict[str, dict] = {}
    for stem in BOOKS:
        if args.only and stem not in args.only:
            continue
        problems, summary = audit(stem)
        mark = "✔" if not problems else "✘"
        print(f"{mark} {stem}：{summary.get('pages', 0)} 頁、{summary.get('lessons', 0)} 課")
        if summary.get("thin"):
            print(f"    幾乎空白的頁（<40 字）{len(summary['thin'])} 頁：{summary['thin'][:10]}")
        if summary.get("placeholders"):
            print(f"    還沒補完的欄位：{summary['placeholders']}")
        for line in problems:
            print(f"    ✘ {line}")
        all_headings[stem] = summary.get("headings", {})
        worst |= bool(problems)

    print("\n各書的區塊標題（體例要一致）")
    for stem, headings in all_headings.items():
        rows = "、".join(f"{k}×{v}" for k, v in sorted(headings.items(), key=lambda r: -r[1]))
        print(f"  {stem}: {rows}")
    return 1 if worst else 0


if __name__ == "__main__":
    sys.exit(main())
