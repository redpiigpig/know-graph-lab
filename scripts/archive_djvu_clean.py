#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 archive.org 的 `_djvu.txt` 清成可入庫的純文字。

什麼時候需要：archive.org 同一筆有時給 EPUB 也給 djvu.txt，但**那個 EPUB 可能只是
掃描頁影像沒有文字層**——奧托《論「聖」》就是，parse_worker 直接回
「no extractable text」。這種時候文字在 djvu.txt 裡，而且品質往往不差
（那一份是 Antiqua 不是 Fraktur，德文常見詞命中率正常）。

djvu.txt 的三種機械性雜訊，都與內容無關：
  1. 行尾軟連字號 `¬`（有時是 `-`）把一個字拆成兩行
  2. 字與字之間被塞成兩個以上的空格
  3. 頁碼行、書眉行、archive.org 自己的掃描聲明

🚨 只做機械性清理，不改字。OCR 真正認錯的字（Fraktur 的 ſ→f 那類）留著，
別在這一層自作聰明——看得見的錯遠好過被掩蓋的錯。

  python scripts/archive_djvu_clean.py <in.txt> <out.txt>
  python scripts/archive_djvu_clean.py <in.txt> <out.txt> --drop-headers "DAS HEILIGE"
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Google／archive.org 掃描件開頭那一大段聲明，到第一個空行為止
BOILERPLATE = re.compile(
    r"^.*?(?:This is a digital copy of a book|about this book|Über dieses Buch)"
    r".*?(?:\n\s*\n)", re.S | re.I)


def dehyphenate(text: str) -> str:
    """行尾的 `¬` 或 `-` 接下一行行首 → 接回同一個字。"""
    return re.sub(r"[¬\-]\s*\n\s*", "", text)


def collapse_spaces(text: str) -> str:
    """djvu 逐字定位造成的多重空格收成一個；不動換行。"""
    return re.sub(r"[ \t]{2,}", " ", text)


def is_noise_line(line: str, headers: list[str]) -> bool:
    s = line.strip()
    if not s:
        return False
    if re.fullmatch(r"[\dIVXLCivxlc]{1,6}\*?", s):        # 純頁碼（含羅馬數字、9* 這種）
        return True
    if any(h and h.lower() in s.lower() and len(s) < len(h) + 12 for h in headers):
        return True                                       # 書眉：只比書名長一點點
    return False


def clean(text: str, headers: list[str] | None = None) -> str:
    headers = headers or []
    text = BOILERPLATE.sub("", text, count=1)
    text = dehyphenate(text)
    kept = [ln for ln in text.splitlines() if not is_noise_line(ln, headers)]
    text = "\n".join(kept)
    text = collapse_spaces(text)
    # 三個以上換行收成段落分隔
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--drop-headers", nargs="*", default=[],
                    help="要當書眉刪掉的字串（書名、章名）")
    a = ap.parse_args()

    raw = Path(a.src).read_text(encoding="utf-8", errors="replace")
    out = clean(raw, a.drop_headers)
    Path(a.dst).write_text(out, encoding="utf-8")
    print(f"{len(raw):,} → {len(out):,} 字元　({len(raw.splitlines()):,} → {len(out.splitlines()):,} 行)")
    print(f"→ {a.dst}")


if __name__ == "__main__":
    main()
