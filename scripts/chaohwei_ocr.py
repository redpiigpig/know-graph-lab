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
- "page" 是這個檔案裡的 1-based 頁次。
- "text" 的**第一行**固定是該頁的印刷頁碼，格式 `【頁 N】`：
  * 阿拉伯數字頁碼就寫數字（例：`【頁 59】`）；
  * 前言／序言區若印的是英文字母或羅馬數字，就原樣寫（例：`【頁 b】`、`【頁 iv】`）；
  * 頁面上**看不到**印刷頁碼（扉頁、版權頁、章名頁、空白頁）一律寫 `【頁 ?】`，
    **絕對不要用前後頁推算或自己編號**。
  頁碼通常印在頁面最上方頁眉那一行的最外側（左頁在左、右頁在右），
  頁眉另有書名或章名（例：「心靈交會‧山間對話」「對話三：婦女與平等」）。
- 第二行起是該頁正文，逐字轉錄，保留段落換行。
- **頁眉單獨成一行**（頁碼＋書名，或頁碼＋章名），不要和正文黏在同一行。
- **腳註一定要收**（研究者要靠它核對出處，漏掉等於毀了這一頁）：
  * 正文裡的**上標註號**寫成 `[^4]`，貼在它所標記的字詞後面；
  * 頁面下方的**註文**放在該頁最後，每註一行，格式 `[^4]: 註文全文`（含書名、篇名、日期、網址，原樣照抄）；
  * 註號常被誤認成標點或引號，看到正文中孤立的小數字就當註號處理；
  * 該頁沒有腳註就完全不要寫 `[^…]`。
- 這是對談錄：發言人以「辛格：」「昭慧：」起頭，請保留這個格式，發言各自成段。
- 中文句子裡的標點一律用**全形**（，。：；？！「」（）——），照原書排版，不要輸出半形逗號。
- 註腳、註釋、參考書目、出版社書目表格一律照樣轉錄（表格用純文字逐列寫出）。
- 整頁空白或只有裝飾就寫 `【頁 ?】`＋下一行 `（無正文）`。
- 不要翻譯、不要摘要、不要加任何說明或評論，只輸出原文。
"""

_PAGENO_RE = re.compile(r"^\s*【頁\s*([^】]*)】\s*")


def split_printed(text: str) -> tuple[str, str]:
    """把 OCR 文字開頭的 `【頁 N】` 拆出來 → (printed, body)。

    找不到標記時 printed 回 ""（＝不知道頁碼），body 原樣回傳 —— 絕不臆測頁碼。
    純函式。
    """
    m = _PAGENO_RE.match(text or "")
    if not m:
        return "", (text or "").strip()
    printed = m.group(1).strip()
    if printed in {"?", "？", ""}:
        printed = ""
    return printed, text[m.end():].strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--model", default="gemini-2.5-flash")
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
            printed, body = split_printed(p.get("text") or "")
            (cache / f"{wp:03d}.json").write_text(
                json.dumps({"work_page": wp, "printed": printed, "text": body},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            done += 1
        print(f"  ✔ 批 {bi}/{len(batches)} 頁 {rs}-{re_}（累計 {done}）", flush=True)
    print(f"✅ 寫出 {done} 頁 → {cache}")


if __name__ == "__main__":
    main()
