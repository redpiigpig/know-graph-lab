# -*- coding: utf-8 -*-
"""LLM 視覺 OCR 的重複幻覺偵測 —— 全專案共用同一份判準。

三個地方要用到，判準必須是同一份（各走各的門檻，稽核就會跟實際行為對不上）：

  ocr_with_gemini.py        寫入前擋掉，書留在佇列等重跑
  quality_sweep.py          放行上架前用 Drive 全文再確認一次
  audit_ocr_repetition.py   回頭掃 2026-09-07 之前入庫的書

兩種故障，成因同一個（模型讀不動某一頁時不回空白，改用既有內容填滿）：

  **整塊重吐上一塊**（detect_repeated_pages）
    2026-09-06《梁發傳略》：p4 開頭是一段雜訊，之後與 p3 逐字相同。
    🚨 重複在尾巴不在開頭 —— DB 只存 100 字 preview，拿 preview 比對抓不到。
       這一項只能用 Drive 上的全文（_chunks/{id}.jsonl）判。

  **同一句話繞圈**（looks_looping）
    2026-09-07《東方化革命》page 77 連續 11 個 chunk：
      髒卜術的詞源和詞形變化也與兩河流域的術語有相似之處。髒卜術的詞源和詞形變化
      也與兩河流域的術語有相似之處。髒卜術的詞源和詞形變化也與兩河流域的術語有…
    這一項週期短，100 字 preview 裡就看得到好幾輪，DB 那份資料就夠。

為什麼要特別防這一類：這種書**結構無懈可擊** —— chunk 數對、目錄齊、頁面覆蓋率
足。純結構評分給《東方化革命》98 分、《海德格爾式的現代神學》94 分，全部通過
80 分上架閘門。空書讀者一眼看得出來，這種書看不出來。
"""
from __future__ import annotations

import difflib

# 比對只取前 CMP_CAP 字：重吐前一頁時開頭就對得上，不必比完整頁。
# SequenceMatcher.ratio() 是 O(n²)，長書逐頁比整頁文字會慢到不能用。
CMP_CAP = 1500


def detect_repeated_pages(chunks: list, min_len: int = 200,
                          ratio: float = 0.90) -> list:
    """找出「這一頁其實是上一頁的複述」的頁。回傳 [(前一頁, 這一頁, 相似度)]。

    只比相鄰兩頁（實測的重吐都是重吐前一頁），O(n)。
    min_len 是為了不要去吵書眉、頁碼、章節分隔頁這些本來就會重複的短字串。
    先過 difflib 自己的兩道 O(n) 上界，再算真正的比值。
    """
    out = []
    prev_i, prev_t = None, ""
    for c in chunks:
        t = (c.get("text") or c.get("content") or "").strip()
        if len(t) < min_len:
            if t:
                prev_i, prev_t = c.get("page"), t
            continue
        if prev_t and len(prev_t) >= min_len:
            sm = difflib.SequenceMatcher(None, prev_t[:CMP_CAP], t[:CMP_CAP])
            if (sm.real_quick_ratio() >= ratio and sm.quick_ratio() >= ratio
                    and sm.ratio() >= ratio):
                out.append((prev_i, c.get("page"), round(sm.ratio(), 3)))
        prev_i, prev_t = c.get("page"), t
    return out


def repetition_verdict(chunks: list, max_share: float = 0.10) -> tuple:
    """整本判定：重複頁佔比超過 max_share 就不要收這本。回傳 (是否通過, 說明)。

    寧可讓書留在 OCR 佇列裡等重跑，也不要把幻覺文字寫進館藏。
    """
    dups = detect_repeated_pages(chunks)
    n_text = sum(1 for c in chunks
                 if len((c.get("text") or c.get("content") or "").strip()) >= 200)
    if not dups or not n_text:
        return True, ""
    share = len(dups) / n_text
    if share < max_share:
        return True, ""
    pairs = ", ".join(f"p{a}≈p{b}({r})" for a, b, r in dups[:4])
    return False, (f"OCR 重複幻覺：{len(dups)}/{n_text} 頁是前一頁的複述"
                   f"（{share:.0%}）— {pairs}")


def looks_looping(text: str, min_reps: int = 3) -> bool:
    """這段文字是不是「同一小段反覆貼成的」。

    三次以上才算：講兩次可能是詩歌或禮文本來就這樣。
    40 字以下不判：書眉、頁碼那些。
    """
    s = (text or "").strip()
    if len(s) < 40:
        return False
    for p in range(4, len(s) // min_reps + 1):
        reps = len(s) // p
        if reps >= min_reps and s[:p] * reps == s[:p * reps]:
            return True
    return False


def repetition_rate(chunks: list) -> float:
    """壞掉的 chunk 佔比：本身是退化迴圈，或與前一個 chunk 一字不差。

    給只拿得到 100 字 preview 的場合用（quality_sweep 的主計分路徑）。
    要抓「尾段才重複」那一種，得用 detect_repeated_pages 配 Drive 全文。
    """
    if not chunks:
        return 0.0
    bad, prev = 0, None
    for c in chunks:
        t = (c.get("content") or c.get("text") or "").strip()
        if looks_looping(t) or (prev and t and t == prev):
            bad += 1
        prev = t
    return bad / len(chunks)
