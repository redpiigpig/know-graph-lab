#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掃描本轉錄的**書籍設定表**（純資料，零 I/O）。

每一本紙本掃描檔要轉錄成全集的一卷，都在這裡加一筆。設定驅動的理由是：
掃描本之間長得很不一樣，而差異幾乎都落在同樣幾個欄位上——

* 《心靈的交會》橫排、2-up 的**下半頁在前**（頁碼 b 在下、c 在上）；
* 《唯識》直排、2-up 的**上半頁在前**（頁碼 130 在上、131 在下）。

半頁順序寫死過一次就會靜靜地把整本書的頁序弄反，而每一頁單獨看都正常
（[[feedback_reader_silent_failures]]），所以一律由本表指定、不靠猜。

欄位：
  src_dir      來源 PDF 所在目錄
  sources      [(tag, 檔名, 是否 2-up)]，**依書的順序**排
  rotate       show_pdf_page 的 rotate 值（實測值；與 fitz.Matrix 反向）
  half_order   'lower-first'（轉正後下半頁在前）或 'upper-first'
  vertical     原書是否直排（只影響 OCR prompt 的說明，轉錄一律出橫排純文字）
  speakers     對談錄的發言人；非對談錄留空 tuple
  ignore_marks 是否要 OCR 忽略鉛筆畫線與手寫筆記
"""
from __future__ import annotations

BOOKS: dict[str, dict] = {
    # 彼得‧辛格與釋昭慧的對談錄（法界出版 2021，作者授權製作電子版）
    "chaohwei-minds": {
        "title": "心靈的交會：山間對話",
        "src_dir": r"C:\Users\user\Downloads\drive-download-20260910T035806Z-1-001",
        "sources": [
            ("cover", "心靈的交會 封面.pdf", False),
            ("ch1-2", "心靈的交會ch1-2.pdf", True),
            ("ch3-4", "心靈的交會ch3-4.pdf", True),
            ("後半", "心靈的交會 後半.pdf", True),
        ],
        "rotate": 270,
        "half_order": "lower-first",
        "vertical": False,
        "speakers": ("辛格", "昭慧"),
        "ignore_marks": False,
        "work_pdf": "c:/tmp/chaohwei/work.pdf",
        "ocr_cache": ["c:/tmp/chaohwei/ocr2", "c:/tmp/chaohwei/ocr"],
    },
    # 昭慧法師的唯識學專著（掃描本上有前手的鉛筆畫線與眉批，一律不收）
    "chaohwei-vijnapti": {
        "title": "初期唯識思想——瑜伽行派形成之脈絡",  # 書名取自書末法界出版社書目 1010
        "src_dir": r"C:\Users\user\Downloads",
        "sources": [("full", "唯識.pdf", True)],
        "rotate": 270,
        "half_order": "upper-first",
        "vertical": True,
        "speakers": (),
        "ignore_marks": True,
        "work_pdf": "c:/tmp/chaohwei_vijnapti/work.pdf",
        "ocr_cache": ["c:/tmp/chaohwei_vijnapti/ocr"],
    },
    # 昭慧法師寫的印順導師傳記（東大圖書 1997 修訂初版，現代佛學叢書）。
    # 掃描是**左右並排**的跨頁（不是上下疊），所以不走 scan_prep split：
    # 第 1 張（版權頁＋法相）整張躺著、rotate=270 轉正不拆，其餘張用
    # split_two_up_pdf.find_split_x 從書溝切開、左頁在前。2026-09-30 先轉前半
    # （卷首至頁 119），後半待掃；新掃描檔依序加進 sources 後重出 work_pdf。
    "chaohwei-seeder": {
        "title": "人間佛教的播種者",
        "src_dir": r"G:\我的雲端硬碟\資料\知識圖工作室\全集\佛學\昭慧法師\人間佛教的播種者_掃描原檔",
        "sources": [
            ("前半", "01_卷首至頁117.pdf", True),
            ("118-119", "02_頁118-119.pdf", True),
        ],
        "rotate": 0,
        "half_order": "left-first",
        "vertical": False,
        "speakers": (),
        "ignore_marks": False,
        "skip_figures": True,  # 使用者定調（2026-10-01）：照片與圖說不收
        # 本書註號是黑底圓圈數字、每章連續編號；不講的話模型一律吐 `[^●]`，
        # 號碼全丟、同頁兩條註分不開。頁底註文的圈號印得很小常被讀成 ❶，
        # 以正文註號為準（build 對齊）。
        "note_hint": ("本書的註號是黑底圓圈數字 ❶❷❸（每一章連續編號，所以一頁上可能是 ❼❽），"
                      "頁底註文前面也印著同樣的圓圈數字。請換成阿拉伯數字："
                      "正文 ❶ 寫 `[^1]`、❷ 寫 `[^2]`，頁底對應的註文寫 `[^1]: …`、`[^2]: …`，"
                      "**不要寫成 `[^●]`**。"),
        "work_pdf": "c:/tmp/chaohwei_seeder/work.pdf",
        "ocr_cache": ["c:/tmp/chaohwei_seeder/ocr"],
    },
}


def get(slug: str) -> dict:
    if slug not in BOOKS:
        raise SystemExit(f"未知的書：{slug}（可用：{', '.join(BOOKS)}）")
    return BOOKS[slug]
