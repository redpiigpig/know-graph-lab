# -*- coding: utf-8 -*-
"""註腳：把 MinerU 撿回來的註腳文字，變成 reader **真的顯示得出來**的東西。

🚨 為什麼需要這一支（2026-09-19 查出來的）
──────────────────────────────────────────────────────────────────────
`ingest_infancy_gospels.py` 收下來的 26 條註腳，在 DB 裡確實存在，但站上**一條都
看不到**。`pages/apocrypha/[slug].vue` 的邏輯是：

    在節的**正文**裡找上標字元（⁴）→ 拿那個數字去 `footnote_defs[「4」]` 查定義

而那支存的是「整頁一個 list」、還複製給該頁每一節（32 節各背一份同樣的 26 條），
正文裡的標記又是普通數字不是上標——56 節裡只有 1 節含上標。三件事各自都不會報錯，
合起來就是「DB 有、頁面空」。這正是最難發現的那一類：**稽核說收到了，而且是真的
收到了，只是沒有人看得見。**

所以本檔做三件事：
  ① 把註腳文字拆成 {標記: 定義}，標記被 OCR 吃掉的用前後鄰居補（只在夾得住時補）
  ② 把正文裡對應的普通數字轉成上標，讓 reader 連得起來
  ③ 逐節分派：哪一節的正文裡有這個標記，定義才掛給那一節

②是有風險的一步（正文裡的數字不只有註腳標記），所以閘開得很緊，見 link_page。
"""
from __future__ import annotations

import re

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
TO_SUP = str.maketrans("0123456789", SUP)
LEAD_NUM = re.compile(r"^(\d{1,3})\s*")


def page_footnotes(notes: list[str]) -> tuple[dict[int, str], list[str]]:
    """一頁的註腳文字 → ({標記: 定義}, 補不出標記的那幾條)。

    實測 2,085 條裡 83.2% 開頭就帶標記。缺標記的那些用**前後鄰居夾**：
    [82, ?, 84] 中間那條就是 83。夾不住（開頭就缺、或連著缺兩條以上對不起來）
    就不猜，原文照樣留著但不給標記——寧可少掛一條，也不要掛錯號。
    """
    parsed: list[tuple[int | None, str]] = []
    for n in notes:
        m = LEAD_NUM.match(n)
        if m:
            parsed.append((int(m.group(1)), n[m.end():].strip()))
        else:
            parsed.append((None, n.strip()))
    # 用左右鄰居補中間的洞
    for i, (num, text) in enumerate(parsed):
        if num is not None:
            continue
        prev = next((parsed[j][0] for j in range(i - 1, -1, -1) if parsed[j][0] is not None), None)
        nxt = next((parsed[j][0] for j in range(i + 1, len(parsed)) if parsed[j][0] is not None), None)
        if prev is not None and nxt is not None and nxt - prev == 2:
            parsed[i] = (prev + 1, text)
        elif prev is not None and nxt is None:
            parsed[i] = (prev + 1, text)
    out: dict[int, str] = {}
    unresolved: list[str] = []
    for num, text in parsed:
        if num is None or num in out:
            unresolved.append(text)
        else:
            out[num] = text
    return out, unresolved


def keyed(notes: list[str]) -> dict[str, str]:
    """一頁的註腳 → {鍵: 定義}，**一條都不丟**。

    🚨 補不出標記的那些（實測 718 條裡有 49 條，MinerU 沒把那個小上標認出來）
    也要收。原本只回傳認得出標記的，那 49 條就這麼消失了——註釋內容本身是完整的，
    丟掉的只是「它對應正文哪個位置」。
    鍵用 `*1`、`*2`，一眼看得出「書上有這條註，但標記沒辨識出來」，
    也不會跟真的標記撞號。
    """
    defs, un = page_footnotes(notes)
    out = {str(k): v for k, v in sorted(defs.items())}
    for i, text in enumerate(un, 1):
        out[f"*{i}"] = text
    return out


def link_page(texts: list[str], markers: list[int]) -> tuple[list[str], list[int]]:
    """把一頁各節的正文裡的註腳標記轉成上標。→ (改過的正文, 沒連上的標記)。

    🚨 正文裡的數字不是只有註腳標記（年份、經文出處、章節號都長一樣），所以這一刀
    夾了四個條件：
      ① 標記**照順序**出現 —— 從上一個標記之後的位置才開始找下一個，
         這條最有力，等於要求整頁的標記單調遞增（實測 96.1% 的頁本來就是）
      ② 前後不能再接數字（避免把 12 的 1 切走、或在 1997 裡找到 9）
      ③ 不在段落開頭（段落開頭的數字是節號，已經被切節那一步剝掉了；
         剩在開頭的多半是沒被認出來的節號，不該當註腳）
      ④ 連不上的標記一律回報，不硬塞

    連不上的標記仍然會**保留定義**（footnote_defs 照樣寫進去），只是正文裡沒有
    對應的上標可點——那是資料在、連結不在，而不是資料掉了。
    """
    joined_positions: list[tuple[int, int]] = []   # (節索引, 節內偏移)
    flat = []
    for i, t in enumerate(texts):
        for off in range(len(t)):
            joined_positions.append((i, off))
        flat.append(t)
    whole = "".join(flat)

    edits: dict[int, list[tuple[int, int]]] = {}
    missed: list[int] = []
    cursor = 0
    for mk in markers:
        s = str(mk)
        found = None
        for m in re.finditer(re.escape(s), whole):
            if m.start() < cursor:
                continue
            before = whole[m.start() - 1] if m.start() else ""
            after = whole[m.end()] if m.end() < len(whole) else ""
            if before.isdigit() or after.isdigit():
                continue
            sec_i, off = joined_positions[m.start()]
            if off == 0:                      # 段落／節開頭 → 多半是節號
                continue
            found = (m, sec_i, off)
            break
        if not found:
            missed.append(mk)
            continue
        m, sec_i, off = found
        edits.setdefault(sec_i, []).append((off, len(s)))
        cursor = m.end()

    out = list(texts)
    for i, spans in edits.items():
        t = out[i]
        for off, n in sorted(spans, reverse=True):
            t = t[:off] + t[off:off + n].translate(TO_SUP) + t[off + n:]
        out[i] = t
    return out, missed
