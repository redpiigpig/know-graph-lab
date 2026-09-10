# -*- coding: utf-8 -*-
"""從既有的讀本 PDF 重切成新的一本——雲端硬碟掛掉時的救援路徑。

`build_course_reader.py` 是從 Drive 上各週資料夾的來源 PDF 重新排版；來源不在
（雲端硬碟沒掛載、或原書已經還掉）時就走這一支：拿已經排好的那本，照書籤把
每一篇整段搬過來，換新的封面、新的分部、新的目錄與頁碼。

    python -X utf8 scripts/split_course_reader.py --reader sat --src 舊合本.pdf --out D:\\某夾
    python -X utf8 scripts/split_course_reader.py --reader japanese --src 舊日文讀本.pdf --out ... --by-order

排版一個字都不會動（整頁搬），所以正文與原本那本逐頁相同；換掉的只有封面、
分部頁、目錄與頁碼。

## 兩個要小心的地方

  1. **舊頁碼要真的刪掉**。整頁搬過來時舊書的頁碼還印在頁腳，新的蓋上去就變成
     一頁兩個號碼；畫白色蓋住也不夠，文字層還在（選取、搜尋、轉檔都會冒回來），
     所以用 redaction 把頁腳那一條刪乾淨再重新編號。
  2. **篇名要對得起來**。結構表裡的鍵是檔名式的（`Segal_Myth (Blackwell`），
     書籤裡是顯示名（`Segal, Myth`），兩者不一樣。先精確比對、再前綴比對，
     兩篇都對不上就直接報錯——**寧可停下來，也不要默默搬錯篇**
     （[[feedback_reader_silent_failures]]）。日文那本的鍵是檔名，跟書籤完全
     對不起來，但順序與結構表一模一樣，所以走 `--by-order`。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_course_reader import (  # noqa: E402
    COVER, PH, PW, READERS, Book, cover_and_toc, stamp_numbers,
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def pieces_of(doc: fitz.Document) -> list[tuple[str, int, int]]:
    """書籤第二層＝一篇。回傳 [(篇名, 起頁, 迄頁)]，頁碼是 1-based 含頭含尾。"""
    toc = doc.get_toc()
    out = []
    for i, (lvl, title, page) in enumerate(toc):
        if lvl != 2:
            continue
        nxt = next((p for l, _, p in toc[i + 1:] if l in (1, 2)), doc.page_count + 1)
        out.append((title.strip(), page, nxt - 1))
    return out


def match(key: str, pieces: list[tuple[str, int, int]]) -> tuple[str, int, int]:
    """結構表的鍵 → 書籤裡的那一篇。對不上就 sys.exit，不要猜。"""
    # 🚨 先拿含括號的全名比，再退回去掉括號的短名。反過來的話，King 那兩篇
    #    （41-56）與（84-164）會在短名這一步變成同一個名字而撞在一起。
    full = key.replace("_", ", ").strip()
    for want in (full, full.split(" (")[0].strip()):
        exact = [p for p in pieces if p[0] == want]
        if len(exact) == 1:
            return exact[0]
        pref = [p for p in pieces if p[0].startswith(want)]
        if len(pref) == 1:
            return pref[0]
    sys.exit(f"對不上：「{key}」→「{full}」，候選 {[p[0] for p in pieces if p[0].startswith(full[:12])] or '無'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", choices=list(READERS), required=True)
    ap.add_argument("--src", required=True, help="已經排好的那本 PDF")
    ap.add_argument("--out", required=True, help="成品放哪個資料夾")
    ap.add_argument("--by-order", action="store_true",
                    help="不比對篇名，照書籤順序一篇一篇對（日文那本用）")
    a = ap.parse_args()

    parts, _, lang, stem = READERS[a.reader]
    src = fitz.open(a.src)
    pieces = pieces_of(src)
    print(f"來源 {os.path.basename(a.src)}　{src.page_count} 頁，{len(pieces)} 篇")

    body = fitz.open()
    marks: list[list] = []
    entries: list[tuple[str, str, int]] = []
    seq = 0
    for name, blurb, items in parts:
        part = Book(lang=lang)
        part.part_title(name, blurb)
        marks.append([1, name, body.page_count + 1])
        body.insert_pdf(part.doc)
        part.doc.close()
        for key, weeks in items:
            title, lo, hi = pieces[seq] if a.by_order else match(key, pieces)
            seq += 1
            marks.append([2, title, body.page_count + 1])
            entries.append((weeks, title, body.page_count + 1))   # 這一篇的第一頁
            body.insert_pdf(src, from_page=lo - 1, to_page=hi - 1)
            print(f"  ✓ {weeks:10s} {title[:52]}　{hi - lo + 1} 頁")

    front = cover_and_toc(lang, COVER[a.reader], entries)

    book = fitz.open()
    book.insert_pdf(front.doc)
    book.insert_pdf(body)
    # 舊頁碼要**真的移掉**再重編。畫一條白色蓋掉是不夠的：看起來乾淨，但文字層
    # 還在，選取或搜尋都會冒出舊號碼，PDF 轉檔也會把它撈回來。所以用 redaction
    # 把頁腳那一條的文字刪掉（正文下緣在 PH-54，這條帶子不會吃到內文）。
    for i in range(front.doc.page_count, book.page_count):
        book[i].add_redact_annot(fitz.Rect(0, PH - 46, PW, PH - 18))
        book[i].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    stamp_numbers(book, front.doc.page_count, front.cjk_path)
    book.set_toc([[lvl, t, p + front.doc.page_count] for lvl, t, p in marks])

    os.makedirs(a.out, exist_ok=True)
    dst = os.path.join(a.out, f"{stem}.pdf")
    book.save(dst, deflate=True)
    print(f"\n✓ {dst}　{book.page_count} 頁（封面目錄 {front.doc.page_count} 頁）")
    src.close()


if __name__ == "__main__":
    main()
