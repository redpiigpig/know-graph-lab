#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""章內段落分配的錨點校正版本 —— 改善 align_reference.py 純比例分配的錯位問題。

背景（2026-09-28）：`merge_original_column.distribute()` 只按累計字數比例把
一個章節區塊的英文段落切給對應的中譯 chunk 群，兩邊字數比例只要在哪一段
「偏胖偏瘦」（長引文、大段對話、OCR 斷字…）就會整段位移，越到章節後段
偏移量越大。詹姆斯《宗教經驗種種》15 段對不上、伯格《神聖的帷幕》4 段
對不上都是這個原因。

改法：先在中譯段落與英文段落之間找幾個「錨點」（中譯段落裡括注的外文專名
／年份／經文章節，沿用 `align_reference.content_anchors`／`anchor_hit_rate`
既有邏輯去英文段落裡找對應位置），錨點在兩邊都必須單調遞增（否則就是誤配，
丟棄不用）。有了錨點就把整個 block 切成「錨點之間」的小區間，每個小區間
各自重新跑一次比例分配——區間越小，比例分配的誤差就越小，等於用真的對應
關係校正比例分配的漂移，類似 DTW／分段線性對齊但不需要引入外部函式庫。

沒有錨點時完全退化成原本的純比例分配（結果應與 `moc.distribute` 一致），
不會比舊法更差。

用法（供 align_reference.py 替換用）：

    import align_reference as ar
    import align_reference_anchors as ara
    result = ar.align_book(en, zh, distribute_fn=ara.distribute_with_anchors)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import align_reference as ar  # noqa: E402
import merge_original_column as moc  # noqa: E402


def find_anchor_breakpoints(members: list[dict], paras: list[str], *,
                            weights: list[int] | None = None,
                            slack_frac: float = 0.15, min_slack: int = 3,
                            min_hit: int = 2, min_hit_ratio: float = 0.6,
                            min_margin: int = 1,
                            min_paras_per_member: float = 0.4) -> list[tuple[int, int]]:
    """在中譯 chunk 群（members）與英文段落群（paras）之間找單調遞增的錨點。

    對每個中譯 chunk 抽錨點（外文專名／年份／經文章節），只在「純比例分配
    原本會把它放在哪裡」（`expected_pj`，累計字數比例算出的期望位置）附近
    一個小視窗裡找命中最多的段落——**不對全書搜尋**。真實書跑起來才發現，
    不限制搜尋範圍會讓偶爾出現的巧合命中（重複出現的年份、常見詞）把某個
    chunk 的錨點誤配到全書任何角落，一步跳到後面幾十段，害中間一大段被
    整個吃掉、後面幾十個 chunk 全配不到內容（比純比例分配的覆蓋率崩更慘，
    2026-09-28 拿詹姆斯試跑就是这样：覆蓋率從 94% 掉到 37%）。加了視窗與
    `min_hit`（至少兩個獨立錨點同時命中，不接受單一巧合詞）之後，錨點只
    做「原位置附近的小幅校正」，不會遠距離亂跳。

    只保留「chunk 序＋段落序都嚴格遞增」的錨點（貪婪掃描、不是嚴格 LIS，
    但夠用：偶爾漏掉一兩個不影響——少切一刀只是退回比例分配，不會切錯）。

    另外兩道防呆閘（2026-09-28 拿真書試跑才補上，光靠視窗還不夠）：
    - **命中比例**（`min_hit_ratio`）＋**領先差距**（`min_margin`）：候選段落要
      有夠高比例的錨點都命中、且明顯比次佳候選段落更好，避免常見詞（年份、
      高頻人名）湊巧在好幾段都命中一兩個，選到似是而非的位置。
    - **段落密度下限**（`min_paras_per_member`）：接受一個錨點前，先檢查它
      切出來的這個小區間平均每個中譯 chunk 能分到的段落數不能太低——太低
      代表這個錨點把一大段中譯 chunk 硬塞進沒幾段原文裡，之後只有一兩個
      chunk 拿得到內容、其餘全部落空（比純比例分配的覆蓋率崩更慘）。
      這正是拿詹姆斯《宗教經驗種種》試跑時實際踩到的坑：不設此閘覆蓋率從
      94% 掉到 37%，加了視窗但沒有這道密度檢查仍掉到 87%。

    回傳：[(member_index, para_index), ...]，member_index／para_index
    嚴格遞增（member_index 用 chunk 在 members 裡的序號，可能跳號）。
    """
    if not members or not paras:
        return []
    if weights is None:
        weights = [len(m.get("content") or "") or 1 for m in members]
    total_w = sum(weights) or 1
    total_p = len(paras)
    slack = max(min_slack, int(total_p * slack_frac))

    breakpoints: list[tuple[int, int]] = []
    last_pj = -1
    last_mi = -1
    acc_w = 0
    for mi, m in enumerate(members):
        acc_w += weights[mi] if mi < len(weights) else 0
        expected_pj = int(total_p * acc_w / total_w)
        content = m.get("content") or ""
        anchors = ar.content_anchors(content)
        n_anchors = sum(len(v) for v in anchors.values())
        if n_anchors == 0:
            continue
        lo = max(last_pj + 1, expected_pj - slack)
        hi = min(total_p - 1, expected_pj + slack)
        best_pj, best_hit, second_hit = -1, 0, 0
        for pj in range(lo, hi + 1):
            hit, total = ar.anchor_hit_rate(anchors, paras[pj])
            if total == 0:
                continue
            if hit > best_hit:
                best_pj, second_hit, best_hit = pj, best_hit, hit
            elif hit > second_hit:
                second_hit = hit
        if best_pj <= last_pj or best_hit < min_hit:
            continue
        if best_hit / n_anchors < min_hit_ratio:
            continue
        if best_hit - second_hit < min_margin:
            continue
        # 密度檢查：這個候選錨點切出的區間，平均每個 member 至少要分到
        # `min_paras_per_member` 段原文，否則寧可不切（留給比例分配兜底）。
        seg_members = mi - last_mi
        seg_paras = best_pj - last_pj
        if seg_members > 0 and seg_paras / seg_members < min_paras_per_member:
            continue
        breakpoints.append((mi, best_pj))
        last_pj, last_mi = best_pj, mi
    return breakpoints


def distribute_with_anchors(paras: list[str], weights: list[int],
                             members: list[dict]) -> list[str]:
    """錨點校正版 `distribute`：先用 `find_anchor_breakpoints` 把
    (members, paras) 切成幾個小區間，區間內各自按 `moc.distribute` 做原本的
    比例分配。沒有錨點（或只有 0/1 個 member/para）時完全等於原本的純比例分配。

    🚨 保底：切區間會讓極少數 member 分到的小區間段落不夠、比例分配後留空
    ——但純比例分配版本在同樣位置通常有內容（只是位置可能不準）。「留白」
    在這支程式原本的設計哲學裡是安全選項（見檔頭 docstring：對不上寧可
    留空，不可以硬配錯），但這裡的留空不是「找不到錨點」，只是切區間的
    副作用，所以改用純比例分配的原內容補回，不讓覆蓋率比舊法還低。
    """
    n = len(weights)
    if not paras or not weights:
        return ["" for _ in weights]

    fallback = moc.distribute(paras, weights)
    breakpoints = find_anchor_breakpoints(members, paras, weights=weights)
    if not breakpoints:
        return fallback

    out: list[str] = [""] * n
    prev_mi, prev_pj = 0, 0
    bounds = breakpoints + [(n, len(paras))]
    for mi, pj in bounds:
        if mi <= prev_mi:
            continue  # 保護：理論上 breakpoints 已嚴格遞增，這裡只是防呆
        seg_weights = weights[prev_mi:mi]
        seg_paras = paras[prev_pj:pj] if pj > prev_pj else []
        seg_out = moc.distribute(seg_paras, seg_weights) if seg_paras else ["" for _ in seg_weights]
        for k, val in enumerate(seg_out):
            out[prev_mi + k] = val
        prev_mi, prev_pj = mi, pj

    # 錨點掃描停在最後一個中譯 chunk 之前就不會再往後切，這裡確認掃到底了；
    # 若最後一段區間沒把 members 收完（理論上不會發生，bounds 最後一項固定是
    # (n, len(paras))），保底再補一次比例分配，不留空段。
    if prev_mi < n:
        seg_weights = weights[prev_mi:n]
        seg_paras = paras[prev_pj:] if prev_pj < len(paras) else []
        seg_out = moc.distribute(seg_paras, seg_weights) if seg_paras else ["" for _ in seg_weights]
        for k, val in enumerate(seg_out):
            out[prev_mi + k] = val

    for i in range(n):
        if not out[i].strip() and fallback[i].strip():
            out[i] = fallback[i]
    return out
