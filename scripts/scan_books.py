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
}


def get(slug: str) -> dict:
    if slug not in BOOKS:
        raise SystemExit(f"未知的書：{slug}（可用：{', '.join(BOOKS)}）")
    return BOOKS[slug]
