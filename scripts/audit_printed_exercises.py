#!/usr/bin/env python3
"""Read the printed books back and check every exercise landed on its own lesson.

The failure this exists to catch is the one this series keeps producing: a page
that looks perfectly typeset and carries the wrong lesson's content.  Rendering
without error proves nothing about pairing, and neither does the builder's own
binding — the builder can bind correctly and still print the block somewhere
else.  So this reads the PDFs, not the DOCX and not the JSON:

* every lesson in the book prints exactly ten items;
* the ten items on the page are the ten the exercise set holds for the lesson
  the page itself says it is;
* no item line carries Chinese — the translation is the answer, and printing it
  beside the question is the one thing the owner ruled out;
* across the whole set, every item is printed exactly once.

Run it after ``render_and_check_reader_pdfs.py``, which checks the physical page
(size, fonts, blanks) and knows nothing about what is on it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "output" / "print-masters"
CACHE = ROOT / "output" / "source-cache" / "original-readers"

CJK = re.compile(r"[㐀-䶿一-鿿]")
LESSON_TAG = re.compile(r"第\s*(\d{1,2})\s*課")
HEADING = re.compile(r"本課翻譯練習（\s*(\d+)\s*題）")
# 🚨 題號行有兩種長相：引用題是「01　馬太福音 26:15」，自撰題自 2026-09-18 起
# 只印「01」（正式課本不在題旁寫「自撰」）。要求題號後面一定有空白的話，自撰題
# 全部匹配不到——四本一共 1,223 題會被報成不見了。
ITEM_NUMBER = re.compile(r"^(\d{2})(?:\s|$)")

# stem -> (exercise set, the lessons the book prints, offset to the set's own
# numbering).  Japanese needs the offset: the exercise set counts 1–100 straight
# through while each printed volume starts again at 1, and converting between
# the two is exactly the join this whole script exists to check.
BOOKS: dict[str, list[tuple[str, str, range, int]]] = {
    "grc": [
        # 🚨 這幾個範圍必須跟 build_greek_full_reader.PARTS 一模一樣。切點一改而
        # 這裡沒跟著改，稽核會說「課次順序印錯」——錯的是稽核自己。
        ("greek-original-reader-vol1", "greek-full/exercise-set-v1.json", range(1, 51), 0),
        ("greek-original-reader-vol2", "greek-full/exercise-set-v2.json", range(1, 51), 0),
    ],
    "lat": [
        ("latin-original-reader-vol1", "latin-full/exercise-set-v1.json", range(1, 51), 0),
        ("latin-original-reader-vol2", "latin-full/exercise-set-v2.json", range(1, 51), 0),
    ],
    "ja": [
        ("japanese-original-reader-vol1", "japanese-full/exercise-set.json", range(1, 51), 0),
        ("japanese-original-reader-vol2", "japanese-full/exercise-set.json", range(1, 51), 50),
    ],
    "heb": [
        ("hebrew-original-reader-50-lessons", "hebrew-full/exercise-set.json", range(1, 51), 0),
    ],
}


def normalise(text: str) -> str:
    """Compare on letters alone.

    A PDF extractor returns what the renderer laid down, which is not always
    what the source string held: decomposed accents, hyphenation at a line
    break, a space where the line wrapped.  None of those are pairing errors,
    and comparing raw strings would report fifty of them.
    """
    text = unicodedata.normalize("NFD", text)
    return "".join(
        ch for ch in text.lower()
        if ch.isalpha() and not unicodedata.combining(ch)
    )


def bag(text: str) -> Counter:
    return Counter(normalise(text))


def similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    shared = sum((a & b).values())
    return shared / max(sum(a.values()), sum(b.values()))


def best_match(printed: Counter, candidates: list[tuple[str, Counter]]) -> str:
    return max(candidates, key=lambda row: similarity(printed, row[1]))[0]


MM = 25.4 / 72.0
PAGE_HEIGHT_MM = 257.0
# 眉標印在版心上緣以上、頁碼在下緣以下；兩者都不是內文。
HEADER_BAND_MM = 16.0
FOOTER_BAND_MM = 16.0


def _banded(page, *, inside: bool) -> list[str]:
    """以 block 為單位取行：inside 取版心內，否則取頁眉頁腳帶。

    🚨 用 block 不用「把所有行按 y 排序」。逐詞對譯一頁上有好幾欄，同一個 y 有
    原文也有中文義；按 y 排會把兩欄交錯成一串，題目與句子就對不起來了（第一版
    這樣改，四本報出三千多項假的不合）。PyMuPDF 的 block 次序就是閱讀次序。

    🚨 也不能用 ``page.get_text().splitlines()`` 一把抓。頁尾自 2026-09-18 起只印
    頁碼，而自撰題的題號行也只有兩位數字——字串分不出「第 73 頁」與「第 73 題」。
    """
    bottom = PAGE_HEIGHT_MM - FOOTER_BAND_MM
    rows: list[str] = []
    for block in page.get_text("blocks"):
        top_mm = block[1] * MM
        in_body = HEADER_BAND_MM <= top_mm <= bottom
        if in_body != inside:
            continue
        for line in (block[4] or "").splitlines():
            rows.append(line.strip())
    return rows


def running_head(page) -> list[str]:
    return _banded(page, inside=False)


def body_lines(page) -> list[str]:
    return _banded(page, inside=True)


def printed_blocks(pdf: Path) -> list[dict]:
    """Every exercise section the book prints, with the lesson its page claims.

    The lesson comes from the running head, which every page of a lesson
    carries, rather than from the order the blocks appear in: a block that
    started on the wrong lesson's page is exactly the failure being looked for,
    and counting blocks would not see it.  A block that runs over onto the next
    page keeps collecting, because the next page's head still names the lesson.
    """
    document = fitz.open(pdf)
    blocks: list[dict] = []
    current: dict | None = None
    for number, page in enumerate(document, start=1):
        lines = body_lines(page)
        tag = next((LESSON_TAG.search(line) for line in running_head(page)
                    if LESSON_TAG.search(line)), None)
        lesson = int(tag.group(1)) if tag else None
        if current is not None and lesson != current["lesson"]:
            current = None
        for index, line in enumerate(lines):
            found = HEADING.search(line)
            if found:
                current = {"lesson": lesson, "page": number, "items": [],
                           "claimed": int(found.group(1))}
                blocks.append(current)
                continue
            if current is None or len(current["items"]) >= current["claimed"]:
                continue
            match = ITEM_NUMBER.match(line)
            if not match:
                continue
            # The item number and its reference share a line; the sentence is
            # the run of non-empty lines under it, which is more than one
            # whenever it wrapped.
            text: list[str] = []
            for row in lines[index + 1:]:
                if not row:
                    break
                text.append(row)
            current["items"].append({"no": int(match.group(1)), "text": " ".join(text),
                                     "head": line, "page": number})
    return blocks


def printed_matches(got: dict, want: dict) -> bool:
    """印出來的那幾行，是不是這一題的句子。

    🚨 不能只比「相等」。題號與出處共用一行，而出處會折行——日文第四冊第 43 課
    第 2 題的出處是〈奥羽北部の石器時代文化における古代シナ文化の影響について〉，
    在 141mm 的版心裡折成兩行，於是「題號行下面那幾行」的第一行其實是出處的尾巴
    「いて〉」，比對就報成「印的不是本課的題目」——而書上完全正確。

    所以：相等當然算，句子落在收集到的那段文字**結尾**也算（前面多出來的是出處
    的續行）。不放寬成「包含」——那會讓一題印成另一題的一部分也算過。
    """
    printed, expected = normalise(got["text"]), normalise(want["text"])
    return printed == expected or (bool(expected) and printed.endswith(expected))


def audit(language: str) -> list[str]:
    """Check what the books print against what the exercise sets hold.

    Two routes, because right-to-left cannot be read back the same way.  For
    Greek and Latin the printed line is the source line, so the comparison is
    the string itself.  PyMuPDF hands back a Hebrew line in visual runs and
    sometimes twice over — ``יוֹנֵק`` comes out ``ויֹוֹוֵנק`` — so neither the order
    nor the letter counts survive extraction, and comparing them reports every
    Hebrew item as mispaired: 377 false alarms and no true one.  What does
    survive is which sentence it is.  So each printed Hebrew item is matched
    against every item in the book and has to come out closest to the one the
    page is supposed to be carrying, which is exactly the failure being looked
    for — a page holding another lesson's content.
    """
    problems: list[str] = []
    seen: dict[str, str] = {}
    exact = language != "heb"
    # Japanese is written in kanji, so "does the item line carry Chinese
    # characters" is not a test that can be run on it.  What replaces it is the
    # pairing check itself: the printed line has to equal the source sentence
    # exactly, which no line with a translation appended can do.
    check_cjk = language != "ja"
    for stem, relative, lessons, offset in BOOKS[language]:
        pdf = PDF_DIR / f"{stem}.pdf"
        if not pdf.is_file():
            problems.append(f"{stem}：找不到 PDF，先跑 render_and_check_reader_pdfs.py")
            continue
        payload = json.loads((CACHE / relative).read_text(encoding="utf-8"))
        expected = {row["lesson"] - offset: row for row in payload["lessons"]}
        catalogue = [
            (f"{row['lesson'] - offset}:{item['no']}", bag(item["text"]))
            for row in payload["lessons"] if row["lesson"] - offset in lessons
            for item in row["items"]
        ]
        blocks = printed_blocks(pdf)
        if len(blocks) != len(lessons):
            problems.append(
                f"{stem}：印出 {len(blocks)} 組練習題，本冊應有 {len(lessons)} 課")
        printed_lessons = [block["lesson"] for block in blocks]
        if printed_lessons != list(lessons):
            problems.append(f"{stem}：課次順序印成 {printed_lessons}，應為 {list(lessons)}")
        for block in blocks:
            row = expected.get(block["lesson"])
            if row is None:
                problems.append(f"{stem} 第 {block['lesson']} 課：練習題檔裡沒有這一課")
                continue
            if len(block["items"]) != len(row["items"]):
                problems.append(
                    f"{stem} 第 {block['lesson']} 課（p.{block['page']}）："
                    f"印出 {len(block['items'])} 題，應有 {len(row['items'])} 題")
            for index, (got, want) in enumerate(zip(block["items"], row["items"]), start=1):
                if exact:
                    paired = printed_matches(got, want)
                else:
                    paired = best_match(bag(got["text"]), catalogue) == \
                        f"{block['lesson']}:{want['no']}"
                if not paired:
                    problems.append(
                        f"{stem} 第 {block['lesson']} 課第 {index} 題（p.{block['page']}）"
                        f"印的不是本課的題目：\n        印出 {got['text']}"
                        f"\n        應為 {want['text']}")
            for item in block["items"]:
                if check_cjk and CJK.search(item["text"]):
                    problems.append(
                        f"{stem} 第 {block['lesson']} 課第 {item['no']} 題（p.{item['page']}）"
                        f"題目旁印出漢字：{item['text']}")
                key = normalise(item["text"]) if exact else \
                    best_match(bag(item["text"]), catalogue)
                where = f"{stem} 第 {block['lesson']} 課第 {item['no']} 題"
                if key and key in seen:
                    problems.append(f"{where} 與 {seen[key]} 印出同一句")
                seen[key] = where
        print(f"  {stem}：{len(blocks)} 課、"
              f"{sum(len(block['items']) for block in blocks)} 題")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", choices=sorted(BOOKS))
    args = parser.parse_args()
    problems = audit(args.language)
    for line in problems:
        print(f"      ✘ {line}")
    if problems:
        print(f"{len(problems)} 項不合")
        return 1
    tail = "題旁零漢字" if args.language != "ja" else "題旁零中譯（逐句與原稿相同）"
    print(f"每一課十題，題目都落在自己的課上，{tail}　✔")
    return 0


if __name__ == "__main__":
    sys.exit(main())
