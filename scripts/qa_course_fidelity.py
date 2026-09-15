# -*- coding: utf-8 -*-
"""課程讀本的**逐段忠實度**稽核：成品裡的每一段，都要在來源切片裡原樣找得到。

    python -X utf8 scripts/qa_course_fidelity.py
    python -X utf8 scripts/qa_course_fidelity.py --reader sat --show 20

跟 `qa_course_reader.py` 的分工：那一支查「有沒有十八類已知的壞法」，靠的是我
想得到的症狀；這一支不靠症狀，而是**拿成品回頭對來源**，所以它抓得到我沒想到
的那一類——字被吃掉、段落漏印、順序被打亂、內容憑空多出來。

（使用者 2026-09-15 問「每一段都檢查過了嗎」。誠實的答案是沒有：稽核只證明
「這十八類不在裡面」，不等於「每一段都對」。這一支補的就是這個缺口。）

做法：兩邊都壓成**只留字母數字的長字串**（大小寫、空白、標點、換行、連字號
全部不算），然後逐段拿成品的簽名去來源裡找。

  · 找不到 → 這一段的文字跟來源對不起來（抽取時吃掉字元、或拼接錯）
  · 找得到但位置往回跳 → 順序被打亂（雙欄讀序那一類）

🚨 只能報「成品 ⊄ 來源」，**不能反過來要求來源的每一段都在成品裡**：書目、註釋、
   編者導言、頁眉、課綱指定範圍以外的頁，本來就是刻意不收的。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_course_reader as B  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SIG = 48          # 每段取多長的簽名去比對
MIN_LEN = 60      # 太短的段（小標、署名）不比，正常會對不上
JUMP = 6000       # 往回跳超過這麼多字元才算亂序（約兩頁），小幅是刻意重排


def squash(t: str) -> str:
    """只留字母與數字，全部轉小寫。連字號、空白、標點、換行一律不算。"""
    return re.sub(r"[^0-9a-z぀-ヿ一-鿿]", "", t.lower())


def source_text(path: str) -> str:
    """來源切片的全文，壓平成只留字母數字。

    🚨 要先套上我們**刻意**做的那些修正，不然自己的修正會被報成「對不上」：
    `OCR_FIXES` 把掃描壞掉的字改對（`Among alli` → `Among all`），成品是對的、
    來源才是錯的，不扣掉就每次報一筆假警報（2026-09-15 第一次跑就中）。
    """
    import fitz
    with fitz.open(path) as doc:
        raw = "\n".join(page.get_text() for page in doc)
    for bad, good in B.OCR_FIXES.items():
        raw = raw.replace(bad, good)
    # 梵文轉寫的間隔附標也要先合起來（來源 `epoche¯`／成品 `epochē`）
    raw = B.SPACING_WORD.sub(B._compose, raw)
    return squash(raw)


def check_reader(reader: str, show: int) -> int:
    parts, courses, lang, stem = B.READERS[reader]
    files = B.index_pdfs(courses)
    bad = 0
    print("=" * 74)
    print(f"{stem}")
    for _name, _blurb, items in parts:
        for key, _weeks in items:
            path = B.locate(files, key)
            if not path or not path.lower().endswith(".pdf"):
                continue
            author, title, _tag = B.title_of_pdf(path)
            src = source_text(path)

            paras, _notes = B.extract_pdf(path)
            paras, _ = B.repair_spacing(paras)
            paras, _ = B.drop_bad_headings(paras)
            paras, _ = B.cut_editor_intro(paras)
            paras, _ = B.drop_repeated_title(paras, title, author)
            paras, _ = B.join_page_cites(paras)
            paras, _ = B.split_paragraphs_at(paras)
            kept, _ = B.cut_bibliography(paras)

            missing, jumped, last = [], [], -1
            checked = 0
            for kind, t in kept:
                if kind != "p":
                    continue
                s = squash(t)
                if len(s) < MIN_LEN:
                    continue
                checked += 1
                # 🚨 在整段的**三個位置**各取一段簽名去找，任何一段對得上就算數。
                #    我們會把頁眉從句子中間挖掉（來源：「…non-commitment is a
                #    Commitment and Understanding 25 positive advantage…」），
                #    只在段首取一次的話，挖掉的位置剛好落在簽名裡就誤報
                #    （2026-09-15 Sharpe 那篇就差這幾個字元）。
                # 🚨 同一句話在一篇裡可能出現兩次（King 那篇的 Schmid 那句就重複
                #    了）。永遠取第一次的話，對應到第二次的段落就被報成「倒退」。
                #    取**上一個位置之後最近的那一次**，沒有才退回第一次。
                def locate(pr: str) -> int:
                    i = src.find(pr, max(0, last))
                    return i if i >= 0 else src.find(pr)

                probes = [s[:SIG], s[len(s) // 2:len(s) // 2 + SIG], s[-SIG:]]
                at = next((i for i in (locate(pr) for pr in probes if len(pr) >= SIG)
                           if i >= 0), -1)
                if at < 0:
                    missing.append(t[:70])
                elif at < last - JUMP:
                    # 🚨 只報**大幅**倒退。雙欄書的區塊順序在來源裡本來就是錯的，
                    #    我們刻意重排成正確讀序，比對時每一次重排都會顯示成倒退
                    #    （2026-09-15 三筆假警報都是這樣來的）。真的亂序會跳很遠。
                    jumped.append(t[:70])
                else:
                    last = at

            flag = ""
            if missing:
                flag += f"　★對不上 {len(missing)}"
            if jumped:
                flag += f"　★順序倒退 {len(jumped)}"
            bad += len(missing) + len(jumped)
            print(f"  {key[:40]:42s} 查 {checked:4d} 段{flag or '　全部對得上'}")
            for m in missing[:show]:
                print(f"       對不上｜{m}")
            for j in jumped[:show]:
                print(f"       倒退　｜{j}")
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", help="只查一本（mon1／mon2／sat）")
    ap.add_argument("--show", type=int, default=3, help="每篇最多列幾筆")
    a = ap.parse_args()
    # 日文讀本的來源是我們自己產的 HTML，不走 PDF 抽取，沒有這個問題
    readers = [a.reader] if a.reader else ["mon1", "mon2", "sat"]
    total = sum(check_reader(r, a.show) for r in readers)
    print("\n總結：", "每一段都在來源裡找得到" if total == 0 else f"{total} 段要看")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
