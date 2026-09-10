#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《心靈的交會：山間對話》工作 PDF → 逐頁 OCR（Gemini Vision）。

吃 chaohwei_scan_prep.py split 出來的工作 PDF（每頁一個書頁、方向已轉正），
逐頁存一個 JSON 到 --cache，內容 {"work_page":N,"printed":"59","text":"..."}。
可 --resume（已存在的頁跳過），因此被 quota 打斷可以續跑。

印刷頁碼是本書上架的硬需求（研究者要引用得出「第幾頁」），所以 prompt 要求
模型把頁碼單獨回報，**不從流水號推算**；看不到就回 "?"，寧可留空。

  python -X utf8 scripts/chaohwei_ocr.py --work c:/tmp/chaohwei/work.pdf \
      --cache c:/tmp/chaohwei/ocr --batch 6 [--pages 2-9] [--resume]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from ocr_pdf_to_text import ocr_pdf  # noqa: E402  （沿用既有 Gemini key 輪替與退避）

PROMPT = """\
這是《心靈的交會：山間對話》（彼得‧辛格與釋昭慧的對談錄，法界出版，繁體中文橫排）的掃描頁。
每一個 PDF page 就是書上的一個頁面。

請逐頁完整轉錄，輸出 JSON：{"pages":[{"page":1,"text":"..."}]}
"page" 是這個檔案裡的 1-based 頁次。"text" 必須**嚴格照下面的行格式**：

第 1 行：`【頁 N】`——該頁的印刷頁碼。
  * 阿拉伯數字頁碼就寫數字（例：`【頁 59】`）；
  * 前言／序言區若印的是英文字母或羅馬數字，原樣寫（例：`【頁 b】`、`【頁 iv】`）；
  * 頁面上**看不到**印刷頁碼（扉頁、版權頁、章名頁、空白頁）一律寫 `【頁 ?】`，
    **絕對不要用前後頁推算或自己編號**。

第 2 行：`【眉 …】`——頁眉那一行的原文（頁碼旁邊的書名或章名，
  例：`【眉 心靈交會‧山間對話】`、`【眉 對話三：婦女與平等】`）。
  該頁沒有頁眉就寫 `【眉 —】`。頁眉**只能出現在這一行**，不可混進正文。

第 3 行起：正文。
  * **一個自然段寫成一行**——不要按書上的印刷換行斷句，也不要把整頁擠成一行。
  * 段落之間不要空行。
  * 對談錄的發言以「辛格：」「昭慧：」起頭，每一次發言自成一段。
  * 中文標點一律**全形**（，。：；？！「」（）——），不要輸出半形逗號。

最後：腳註。**腳註一定要收**（研究者要靠它核對出處，漏掉等於毀了這一頁）。
  * 正文裡的**上標註號**寫成 `[^4]`，貼在它所標記的字詞後面；
  * 頁面下方的**註文**每註一行，格式 `[^4]: 註文全文`（書名、篇名、日期、網址原樣照抄）；
  * 註號要用**書上印的那個數字**（原書是第 4 註就寫 `[^4]`），不要自己從 1 重編；
    真的看不清就寫 `[^?]`；
  * 註號常被誤認成標點或引號，看到正文中孤立的小數字就當註號處理；
  * 該頁沒有腳註就完全不要寫 `[^…]`。

其他：參考書目與出版社書目表格照樣轉錄（表格用純文字逐列寫出，一列一行）。
整頁空白或只有裝飾，就寫 `【頁 ?】`＋`【眉 —】`＋`（無正文）` 三行。
不要翻譯、不要摘要、不要加任何說明或評論，只輸出原文。
"""

_PAGENO_RE = re.compile(r"^\s*【頁\s*([^】]*)】\s*")
_HEADER_RE = re.compile(r"^\s*【眉\s*([^】]*)】\s*")


def split_printed(text: str) -> tuple[str, str, str]:
    """把 OCR 文字開頭的 `【頁 N】`／`【眉 …】` 拆出來 → (printed, header, body)。

    模型讓頁眉自己佔一行，正文就不必再靠猜的把頁眉從第一段裡挖出來——
    先前的版本要在字串裡認頁眉，曾把整頁正文當成頁眉刪光。
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
    ap.add_argument("--work", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--model", default="gemini-flash-latest",
                    help="首選模型；ocr_pdf 會自動 fallback 到其他模型（新 key 對 2.5-flash 一律 404）")
    ap.add_argument("--batch", type=int, default=6)
    ap.add_argument("--pages", help="1-based 範圍，例 2-9")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)

    import fitz
    doc = fitz.open(args.work)
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
    print(f"待 OCR {len(todo)} 頁（{lo}-{hi} 共 {hi - lo + 1} 頁）", flush=True)

    # 連續區段各自送批，避免 resume 時把已完成的頁再算進切片
    runs: list[tuple[int, int]] = []
    for p in todo:
        if runs and p == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], p)
        else:
            runs.append((p, p))

    # 每一批各自落地：整段跑完才寫檔的話，中途被 quota 打斷就前功盡棄
    batches: list[tuple[int, int]] = []
    for rs, re_ in runs:
        batches += [(s, min(s + args.batch - 1, re_)) for s in range(rs, re_ + 1, args.batch)]

    done = 0
    for bi, (rs, re_) in enumerate(batches, 1):
        pages = ocr_pdf(Path(args.work), model=args.model, pages=(rs, re_),
                        batch=0, prompt=PROMPT)
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
