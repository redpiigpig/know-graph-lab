#!/usr/bin/env python3
"""一課的讀文能收多長——四本原文讀本共用的版面預算。

擁有者 2026-09-17：「一課最多不能超過 8 頁。」一課印三樣東西：二十個生詞、十題
翻譯練習、一篇讀文。前兩樣長度固定，讀文不固定，所以

    頁數 ≈ 固定開銷 + a × 讀文長度 + b × 單元數

🚨 **單元數那一項不能省。** 讀文排的是逐詞對譯：每個單元（一節經文、一段散文）
自成一塊，末尾那一列多半沒排滿，還要加一行整句中譯。所以一篇「五百詞分五段」
與「五百詞分五十段」厚度差很多。只用詞數回歸，希臘的 R² 是 0.793、日文只有
0.478——一半的課落在線的上方；補上單元數之後是 0.925 與 0.643。實際被這一項
咬到的是〈聖母讚頌詞〉那種課：詞數不多、段數上百，照詞數估是七頁，印出來十二頁。

🚨 量的是**印出來的頁**，不是估的。係數由 ``scripts/fit_reader_reading_limit.py``
從已排好的 PDF 回歸出來（每課的眉標就是那一課的頁，數眉標就是數厚度）。版面一改
——字級、行距、cell 邊距、練習題的節奏——係數就不再是這一組，要重量。

🚨 不要用「讀文長度 ÷ 一課總頁數」當每頁容量：那個分母含生詞頁與練習頁，密度會
低估四成，上限就砍過頭。也不要用「一頁排得下幾個原文詞」回推：段末沒排滿的那一
列、整句中譯的行、單元之間的間距都不在那個數字裡。

係數量測日：2026-09-18，12pt 版面（`MIN_READING_PT`）、四本共十二冊 350 課。
"""

from __future__ import annotations

PAGE_LIMIT = 10  # 擁有者 2026-09-25：行距放寬、作答線加高後，一課放寬到十頁
"""擁有者定的硬上限：一課最多這麼多頁。"""

SAFETY_PAGES = 0.6
"""回歸線給的是平均，實際會散在線兩側；留這麼多頁當緩衝。

不留的話，照線設上限會有一半的課壓在線上方——第一輪就是這樣：四本共 31 課印成
九到十頁。這個數字也是量出來的：留 0.6 頁之後重排，沒有一課超過八頁。
"""

MODEL = {
    # 語言: (固定開銷頁, 每單位長度的頁, 每個單元的頁)
    "grc": (2.54, 0.01205, 0.0639),
    "hbo": (3.81, 0.01169, 0.0841),
    "lat": (3.27, 0.01312, 0.0308),
    "ja": (2.62, 0.00758, 0.1220),
}
"""各語言的版面模型。長度的單位：希臘、希伯來、拉丁是**詞**，日文是**字元**。

希伯來的固定開銷比另外三本高將近一頁，因為只有它在讀文之後還印「細讀、專名與
練習」那一節。那一節是刻意保留的，代價就是讀文的額度少一點。
"""


def predicted_pages(language: str, length: int, units: int) -> float:
    """這麼長、這麼多單元的一課，排出來大約幾頁。"""
    base, per_length, per_unit = MODEL[language]
    return base + per_length * length + per_unit * units


def budget_pages(language: str) -> float:
    return PAGE_LIMIT - SAFETY_PAGES


def fits(language: str, length: int, units: int) -> bool:
    return predicted_pages(language, length, units) <= budget_pages(language)


def clip(units: list, weight, language: str) -> list:
    """從篇首連續取整個單元，取到再加一個就會超出版面預算為止。

    ``units`` 是文本自己的分段（經節、章、自然段），``weight`` 回傳一個單元的
    長度。回傳留下來的前幾個單元。

    🚨 第一個單元自己就超出預算時仍然收下：寧可長一點，也不要交出半節、半段——
    擁有者 2026-09-17：「要是自然段落的選集喔，不要是語意沒講完就中斷。」呼叫端
    要用 ``over_budget()`` 檢查這種情形，並改用更細的分段重裁（見那一支的說明）。
    """
    kept: list = []
    running = 0
    for unit in units:
        size = weight(unit)
        if kept and not fits(language, running + size, len(kept) + 1):
            break
        kept.append(unit)
        running += size
    return kept


def over_budget(kept: list, weight, language: str) -> bool:
    """裁完仍然超出預算嗎？

    只有一種情況會這樣：第一個單元自己就太長。這時候粗分段（章）救不了，要退到
    更細的分段（段、句）重裁一次——希臘下冊有兩篇是這樣：〈黑馬牧人書：第一異象〉
    整篇 995 詞只分成一章，〈特魯洛大公會議教規 1–20〉整篇 860 詞只有一段，
    照章、照段裁都等於沒裁，印出來十六頁與十三頁。
    """
    return not fits(language, sum(weight(unit) for unit in kept), len(kept))
