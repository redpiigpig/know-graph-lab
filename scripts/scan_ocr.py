#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工作 PDF → 逐頁 OCR（Gemini Vision）。設定見 scripts/scan_books.py。

吃 scan_prep.py split 出來的工作 PDF（每頁一個書頁、方向已轉正），逐頁存一個
JSON 到 --cache：{"work_page":N,"format":"v2","printed":"59","header":"…","text":"…"}。
可 --resume（已存在的頁跳過），被配額打斷可以續跑，每一批各自落地。

輸出格式刻意做成**結構化的行**（`【頁 N】`／`【眉 …】`／正文／`[^4]: 註文`），
而不是「一坨文字之後再想辦法拆」：先前那個版本要在字串裡認頁眉，把整頁 454 字
的正文當成頁眉刪光過（[[feedback_reader_silent_failures]]）。

  python -X utf8 scripts/scan_ocr.py --book chaohwei-minds --batch 6 --resume
  python -X utf8 scripts/scan_ocr.py --book chaohwei-vijnapti --pages 149-152
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import scan_books  # noqa: E402
from ocr_pdf_to_text import ocr_pdf  # noqa: E402  （沿用既有 Gemini key 輪替與退避）

_BASE = """\
這是《{title}》（繁體中文{layout}）的掃描頁。每一個 PDF page 就是書上的一個頁面。

請逐頁完整轉錄，輸出 JSON：{{"pages":[{{"page":1,"text":"..."}}]}}
"page" 是這個檔案裡的 1-based 頁次。"text" 必須**嚴格照下面的行格式**：

第 1 行：`【頁 N】`——該頁的印刷頁碼。
  * 阿拉伯數字頁碼就寫數字（例：`【頁 59】`）；中文數字頁碼（一三〇）換算成 `130`；
  * 前言／序言區若印的是英文字母或羅馬數字，原樣寫（例：`【頁 b】`、`【頁 iv】`）；
  * 頁面上**看不到**印刷頁碼（扉頁、版權頁、章名頁、空白頁）一律寫 `【頁 ?】`，
    **絕對不要用前後頁推算或自己編號**。

第 2 行：`【眉 …】`——頁眉那一行的原文（頁碼旁邊的書名或章名）。
  沒有頁眉就寫 `【眉 —】`。頁眉**只能出現在這一行**，不可混進正文。

第 3 行起：正文。
  * **一個自然段寫成一行**——不要按書上的印刷換行斷句，也不要把整頁擠成一行。
  * 段落之間不要空行。
{extra}  * 中文標點一律**全形**（，。：；？！「」（）——），不要輸出半形逗號。
  * 括號裡裝中文就用全形（），裝西文或數字才用半形()：`（一）`、`（大正二九‧一五九上）`，但 `(Bentham)`、`(2021)`。

最後：腳註。**腳註一定要收**（研究者要靠它核對出處，漏掉等於毀了這一頁）。
  * 正文裡的**上標註號**寫成 `[^4]`，貼在它所標記的字詞後面；
  * 頁面下方的**註文**每註一行，格式 `[^4]: 註文全文`（書名、卷冊、頁碼、網址原樣照抄）；
  * 註號要用**書上印的那個數字**，不要自己從 1 重編；真的看不清就寫 `[^?]`；
  * 若本頁最上面那條註文是**從上一頁接續下來的**（開頭沒有註號、直接承接前文），
    寫成 `[^續]: …`，不要硬安一個號碼給它；
  * 該頁沒有腳註就完全不要寫 `[^…]`。

其他：參考書目與表格照樣轉錄（表格用純文字逐列寫出，一列一行）。
整頁空白或只有裝飾，就寫 `【頁 ?】`＋`【眉 —】`＋`（無正文）` 三行。
不要翻譯、不要摘要、不要加任何說明或評論，只輸出原文。

🚨 一次給你多頁時，**每一頁只能轉錄它自己的內容**。看不清或沒把握就寫
`（無正文）`，絕對不要把前一頁（或後一頁）的文字再抄一次充數——那種錯誤
在成品上看起來完全正常，是這條線最難查出來的一種。
"""

_VERTICAL = ("  * 原書是**直排**（由右至左、由上而下）。請照閱讀順序轉錄成一般橫排文字，"
             "不要保留直排造成的斷行。\n")
_DIALOGUE = ("  * 這是對談錄，發言以「{a}：」「{b}：」起頭，每一次發言自成一段。\n")
_MARKS = ("  * 頁面上有前手用鉛筆或原子筆畫的線、方框、底線、圈點與手寫眉批，"
          "**一律忽略**，只轉錄印刷文字。\n")


def build_prompt(book: dict) -> str:
    """依書籍設定組出 OCR prompt。純函式。"""
    extra = ""
    if book.get("vertical"):
        extra += _VERTICAL
    sp = book.get("speakers") or ()
    if len(sp) >= 2:
        extra += _DIALOGUE.format(a=sp[0], b=sp[1])
    if book.get("ignore_marks"):
        extra += _MARKS
    return _BASE.format(title=book["title"],
                        layout="直排" if book.get("vertical") else "橫排",
                        extra=extra)


_PAGENO_RE = re.compile(r"^\s*【頁\s*([^】]*)】\s*")
_HEADER_RE = re.compile(r"^\s*【眉\s*([^】]*)】\s*")


def split_printed(text: str) -> tuple[str, str, str]:
    """OCR 文字 → (printed, header, body)，拆掉開頭的 `【頁 N】`／`【眉 …】`。

    找不到標記時該欄回 ""（＝不知道），body 原樣回傳；絕不臆測頁碼。純函式。
    """
    s = text or ""
    printed = ""
    m = _PAGENO_RE.match(s)
    if m:
        printed = m.group(1).strip()
        if printed in {"?", "？", "—", "-"}:
            printed = ""
        s = s[m.end():]
    header = ""
    m = _HEADER_RE.match(s)
    if m:
        header = m.group(1).strip()
        if header in {"—", "-", "?", "？"}:
            header = ""
        s = s[m.end():]
    return printed, header, s.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--book", required=True, help=", ".join(scan_books.BOOKS))
    ap.add_argument("--work", help="預設用設定裡的 work_pdf")
    ap.add_argument("--cache", help="預設用設定裡 ocr_cache 的第一個")
    ap.add_argument("--model", default="gemini-flash-latest",
                    help="首選模型；ocr_pdf 會自動 fallback 到其他模型（新 key 對 2.5-flash 一律 404）")
    ap.add_argument("--batch", type=int, default=6)
    ap.add_argument("--pages", help="1-based 範圍，例 2-9")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    book = scan_books.get(args.book)
    work = Path(args.work or book["work_pdf"])
    cache = Path(args.cache or book["ocr_cache"][0])
    cache.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(book)

    import fitz
    doc = fitz.open(work)
    total = len(doc)
    doc.close()

    if args.pages:
        lo, _, hi = args.pages.partition("-")
        lo, hi = int(lo), int(hi or lo)
    else:
        lo, hi = 1, total

    todo = [p for p in range(lo, hi + 1)
            if not (args.resume and (cache / f"{p:03d}.json").exists())]
    if not todo:
        print("✅ 全部已在快取中")
        return
    print(f"《{book['title']}》待 OCR {len(todo)} 頁（{lo}-{hi} 共 {hi - lo + 1} 頁）", flush=True)

    # 每一批各自落地：整段跑完才寫檔的話，中途被配額打斷就前功盡棄
    runs: list[tuple[int, int]] = []
    for p in todo:
        if runs and p == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], p)
        else:
            runs.append((p, p))
    batches: list[tuple[int, int]] = []
    for rs, re_ in runs:
        batches += [(s, min(s + args.batch - 1, re_)) for s in range(rs, re_ + 1, args.batch)]

    done = 0
    for bi, (rs, re_) in enumerate(batches, 1):
        pages = ocr_pdf(work, model=args.model, pages=(rs, re_), batch=0, prompt=prompt)
        for p in pages:
            wp = int(p.get("page", 0))
            if not (rs <= wp <= re_):
                continue
            printed, header, body = split_printed(p.get("text") or "")
            (cache / f"{wp:03d}.json").write_text(
                json.dumps({"work_page": wp, "format": "v2", "printed": printed,
                            "header": header, "text": body},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            done += 1
        print(f"  ✔ 批 {bi}/{len(batches)} 頁 {rs}-{re_}（累計 {done}）", flush=True)
    print(f"✅ 寫出 {done} 頁 → {cache}")


if __name__ == "__main__":
    main()
