# -*- coding: utf-8 -*-
"""課程指定讀物切片：整本 PDF → 各週資料夾裡的單篇 PDF。

課程大綱按**印刷頁碼**指定讀物（「Blackwell Companion 91-122」），整本電子檔前面
還有封面、版權頁、目錄，兩者一定對不上。硬套一個位移會切錯章，而切錯章不會報錯
——檔案大小正常、頁數正常、打開也真的是一篇論文，只是不是指定的那一篇
（[[feedback_reader_silent_failures]]）。所以這支做兩件事：

  1. 逐頁讀頁眉／頁腳上真正印著的數字，取眾數當位移（不是猜、不是手填）；
  2. 每片都驗首頁含不含篇名關鍵字，驗不過就不寫檔，列進待辦。

    python -X utf8 scripts/course_slice_readings.py            # 切
    python -X utf8 scripts/course_slice_readings.py --offsets  # 只報位移
    python -X utf8 scripts/course_slice_readings.py --audit    # 只列各片首頁，肉眼複核

整本原書留在 z-lib/ 讓 16:00 的 ingest_new_books.py 收進電子圖書館；這支只讀不搬。
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import Counter

import fitz

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DROP = os.path.join(ROOT, "z-lib")
DEST = r"G:\我的雲端硬碟\玄奘\博一上\上課\宗教研究基本問題與研究方法"

# 書代號 → (在 z-lib/ 的檔名 glob, 書名簡稱，寫進切片檔名裡)
BOOKS = {
    "guide": ("Guide to the study of religion*", "Guide"),
    "routledge": ("The Routledge companion*", "Routledge Companion"),
    "understanding": ("Understanding religion*", "Understanding Religion"),
    "theory": ("Theory and Method in Religious Studies*", "Theory and Method"),
    "blackwell": ("The Blackwell Companion*", "Blackwell Companion"),
    "insider": ("The InsiderOutsider Problem*", "Insider-Outsider"),
}

# (週次資料夾, 序號, 作者, 篇名, 書, 起頁, 訖頁, 首頁驗證關鍵字)
# 序號＝大綱裡的排列順序，不是週次；W02-04 那種跨週的區塊照大綱原樣不拆。
READINGS = [
    ("W02-04 歷史背景與學科定位", 2, "Sharpe", "The Study of Religion in Historical Perspective", "routledge", 21, 45, "Historical Perspective"),
    ("W02-04 歷史背景與學科定位", 3, "Sharpe", "Theology and Religious Studies", "understanding", 1, 17, "Theology"),
    ("W02-04 歷史背景與學科定位", 4, "Whaling", "Introduction", "theory", 1, 39, "Introduction"),
    ("W02-04 歷史背景與學科定位", 5, "King", "Orientalism and the Study of Religion", "routledge", 275, 290, "Orientalism"),

    ("W05 研究對象的定義", 1, "Braun", "Religion", "guide", 3, 18, "Religion"),
    ("W05 研究對象的定義", 2, "Sharpe", "The Question of Definition", "understanding", 33, 48, "Definition"),
    ("W05 研究對象的定義", 3, "Arnal", "Definition", "guide", 21, 34, "Definition"),

    ("W06-08 理解、解釋、詮釋的問題", 1, "Sharpe", "Commitment and Understanding", "understanding", 18, 32, "Commitment"),
    ("W06-08 理解、解釋、詮釋的問題", 2, "Green", "Hermeneutics", "routledge", 392, 406, "Hermeneutics"),
    ("W06-08 理解、解釋、詮釋的問題", 3, "Penner", "Interpretation", "guide", 57, 66, "Interpretation"),
    ("W06-08 理解、解釋、詮釋的問題", 4, "Segal", "Theories of Religion", "routledge", 49, 60, "Theories of Religion"),

    ("W10 現代主義、後現代主義", 1, "Wiebe", "Modernism", "guide", 351, 364, "Modernism"),
    ("W10 現代主義、後現代主義", 2, "Wolfart", "Postmodernism", "guide", 380, 395, "Postmodernism"),
    ("W10 現代主義、後現代主義", 3, "Campbell", "Modernity and Postmodernity", "blackwell", 309, 320, "Postmodernity"),

    # 大綱寫 41-176，括號註明實際只讀 41-56 與 84-164 兩段，所以切兩檔
    ("W11 歷史與比較（一）", 1, "King", "Historical and Phenomenological Approaches (41-56)", "theory", 41, 56, "Phenomenological"),
    ("W11 歷史與比較（一）", 2, "King", "Historical and Phenomenological Approaches (84-164)", "theory", 84, 164, ""),

    ("W12 歷史與比較（二）", 1, "Smith", "Classification", "guide", 35, 44, "Classification"),
    ("W12 歷史與比較（二）", 2, "Martin", "Comparison", "guide", 45, 56, "Comparison"),

    ("W13 歷史與比較（三）", 1, "Allen", "Phenomenology of Religion", "routledge", 182, 207, "Phenomenology"),
    ("W13 歷史與比較（三）", 2, "Ryba", "Phenomenology of Religion", "blackwell", 91, 122, "Phenomenology"),
    ("W13 歷史與比較（三）", 3, "Roscoe", "The Comparative Method", "blackwell", 25, 46, "Comparative Method"),
    ("W13 歷史與比較（三）", 4, "Paden", "Comparative Religion", "routledge", 208, 225, "Comparative Religion"),

    ("W14 社會與文化（一）", 1, "Gifford", "Religious Authority - Scripture, Tradition, Charisma", "routledge", 379, 391, "Religious Authority"),
    ("W14 社會與文化（一）", 2, "Jensen", "Structure", "guide", 314, 333, "Structure"),

    ("W15 社會與文化（二）", 1, "Segal", "Myth and Ritual", "routledge", 355, 378, "Myth and Ritual"),

    ("W16 社會與文化（三）", 1, "Segal", "Myth", "blackwell", 337, 356, "Myth"),
    ("W16 社會與文化（三）", 2, "McCutcheon", "Myth", "guide", 190, 208, "Myth"),

    ("W17 社會與文化（四）", 1, "Grimes", "Ritual", "guide", 259, 270, "Ritual"),
    ("W17 社會與文化（四）", 2, "Bell", "Ritual", "blackwell", 397, 411, "Ritual"),
]

_PAGENO = re.compile(r"(\d{1,4})")


def find_offset(doc: fitz.Document) -> int:
    """PDF 頁序(1-based) − 印刷頁碼。逐頁投票取眾數。

    只掃中段：前面是羅馬數字的前言、後面是索引，兩頭都會污染投票。
    """
    votes: Counter[int] = Counter()
    lo, hi = int(doc.page_count * 0.15), int(doc.page_count * 0.85)
    for i in range(lo, hi):
        lines = [ln.strip() for ln in doc[i].get_text().splitlines() if ln.strip()]
        for cand in lines[:2] + lines[-2:]:
            m = _PAGENO.fullmatch(cand)
            if m:
                votes[i + 1 - int(m.group(1))] += 1
    if not votes:
        raise RuntimeError("讀不到任何頁碼——這本可能沒有文字層，要先 OCR")
    (best, n), rest = votes.most_common(1)[0], votes.most_common(3)[1:]
    runner = rest[0][1] if rest else 0
    # 眾數要壓倒性領先才可信。差距不大代表頁眉抓到的是別的數字（年份、註號），
    # 這時候寧可停下來，也不要切出一堆錯章。
    if n < 20 or n < runner * 5:
        raise RuntimeError(f"位移投票不夠乾淨：{votes.most_common(3)}")
    return best


def safe(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "-", s).strip().rstrip(".")


def open_books() -> dict[str, tuple[fitz.Document, int, str]]:
    out = {}
    for key, (pat, short) in BOOKS.items():
        files = glob.glob(os.path.join(DROP, pat))
        if not files:
            print(f"[缺書] {key}（{pat}）")
            continue
        doc = fitz.open(files[0])
        out[key] = (doc, find_offset(doc), short)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offsets", action="store_true", help="只報各書的頁碼位移")
    ap.add_argument("--audit", action="store_true", help="只列已切好的各片首頁，肉眼複核")
    a = ap.parse_args()

    if a.audit:
        for folder in sorted(os.listdir(DEST)):
            d = os.path.join(DEST, folder)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if not f.lower().endswith(".pdf"):
                    continue
                with fitz.open(os.path.join(d, f)) as doc:
                    head = [ln.strip() for ln in doc[0].get_text().splitlines() if ln.strip()]
                print(f"{f[:62]:64s} | 首頁: {' / '.join(head[:4])[:80]}")
        return

    books = open_books()
    if a.offsets:
        for key, (doc, off, _) in books.items():
            print(f"{key:14s} {doc.page_count:5d} 頁  位移 {off:+d}")
        return

    ok, bad = 0, []
    for folder, seq, author, title, book, p1, p2, kw in READINGS:
        if book not in books:
            bad.append((folder, title, f"缺書 {book}"))
            continue
        doc, off, short = books[book]
        lo, hi = p1 + off - 1, p2 + off - 1          # 0-based
        if lo < 0 or hi >= doc.page_count:
            bad.append((folder, title, f"頁碼超出範圍 {lo}-{hi}/{doc.page_count}"))
            continue
        head = doc[lo].get_text() + (doc[lo + 1].get_text() if lo + 1 < doc.page_count else "")
        if kw and kw.lower() not in head.lower():
            bad.append((folder, title, f"首頁驗不到「{kw}」"))
            continue
        week = folder.split()[0]
        dst = os.path.join(DEST, folder,
                           f"{week}_{seq}_{safe(author)}_{safe(title)} ({short} {p1}-{p2}).pdf")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        out = fitz.open()
        out.insert_pdf(doc, from_page=lo, to_page=hi)
        out.save(dst)
        out.close()
        ok += 1
        print(f"✓ {os.path.basename(dst)}  ({hi - lo + 1}p)")

    for folder, title, why in bad:
        print(f"✗ {folder} / {title} —— {why}")
    print(f"\n切出 {ok} 篇，未切 {len(bad)} 篇")


if __name__ == "__main__":
    main()
