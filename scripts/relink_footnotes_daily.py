#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""每日排程：用模型補「有註文、正文沒連結」的註號（2026-10-02 起，排程 KGL_Footnote_Relink）。

一輪：全館盤點（約 12 分鐘）→ 挑 A／C／D 型、已重建（有 .bak_restructure）的書 →
優先神學／宗教學／世界宗教，再按缺口大小 → relink_missing_footnotes（規則＋模型 Gemini→NVIDIA）。
停手條件：模型連續兩次失敗（額度）、本輪呼叫數到上限、跑超過時限、G: 不見。已補的每本照樣寫回；
明天再從頭盤點，自然接續。E 型（問題清單，不是註腳）與 F 型（正文完全沒註號，見 PDF 上標那條線）不碰。

  python -X utf8 scripts/relink_footnotes_daily.py [--max-calls 400] [--hours 3] [--no-scan] [--dry]
log：output/relink/daily.log
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relink_missing_footnotes as rl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "output/relink/daily.log"
GAPS = ROOT / "output/toc_audit/footnote_gaps.tsv"
DNT = ROOT / "output/restructure/DO_NOT_TOUCH_ids.txt"
PRI = {"神學", "宗教學", "世界宗教"}


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("%m-%d %H:%M ") + msg + "\n")
    print(msg, flush=True)


def arg(name: str, default: float) -> float:
    return float(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def categories() -> dict[str, str]:
    import requests
    import translate_ebook_to_zh as te
    h = {"apikey": te.KEY, "Authorization": "Bearer " + te.KEY}
    out, off = {}, 0
    while True:   # 🚨 PostgREST 不帶 limit 會靜默截在 1000
        b = requests.get(te.URL + "/rest/v1/ebooks", headers=h, timeout=120, params={
            "select": "id,category", "order": "id", "limit": "1000", "offset": str(off)}).json()
        out.update({x["id"]: x.get("category") or "" for x in b})
        if len(b) < 1000:
            return out
        off += 1000


def main() -> int:
    t0 = time.time()
    hours = arg("--hours", 3)
    rl.ENGINE["max_calls"] = int(arg("--max-calls", 400))
    if not rl.CH.exists():
        log("G: 不在，略過（DriveFS 卡住？見 CLAUDE.md）")
        return 3
    if "--no-scan" not in sys.argv:
        rl.scan()
    rows = [l.split("\t") for l in GAPS.read_text(encoding="utf-8").splitlines()[1:]]
    cat = categories()
    dnt = set(DNT.read_text(encoding="utf-8").split()) if DNT.exists() else set()
    todo = []
    for r in rows:
        if len(r) < 4 or r[3] not in ("A", "C", "D") or int(r[2]) == 0 or r[0] in dnt:
            continue
        if not (rl.CH / f"{r[0]}.jsonl.bak_restructure").exists():
            continue          # 還沒重建的書之後會從原檔重做，現在補了會被洗掉
        todo.append((0 if cat.get(r[0]) in PRI else 1, -int(r[2]), r[0]))
    todo.sort()
    log(f"=== 開始：可補 {len(todo)} 本、{-sum(t[1] for t in todo)} 則；呼叫上限 {rl.ENGINE['max_calls']}")
    tr = tl = books = 0
    why = "清單跑完"
    for _, _, bid in todo:
        if time.time() - t0 > hours * 3600:
            why = f"超過 {hours} 小時"
            break
        if not rl.CH.exists():
            why = "G: 不見了"
            break
        p = rl.CH / f"{bid}.jsonl"
        if time.time() - p.stat().st_mtime < 900:
            log(f"略過 {bid}：15 分鐘內有人寫過（避免跟重建／新書後處理並行）")
            continue
        try:
            r, l, exhausted = rl.relink_book(bid, use_llm=True, apply="--dry" not in sys.argv)
        except Exception as e:  # noqa: BLE001
            log(f"ERR {bid} {type(e).__name__}: {e}")
            continue
        books += 1
        tr += r
        tl += l
        if r or l:
            log(f"{bid} 規則 {r}、模型 {l}")
        if exhausted:
            why = "引擎額度用完／到呼叫上限"
            break
    log(f"=== 結束（{why}）：看過 {books} 本，規則 {tr}、模型 {tl}，模型呼叫 {rl.ENGINE['calls']} 次，"
        f"{(time.time() - t0) / 60:.0f} 分鐘")
    return 0


if __name__ == "__main__":
    sys.exit(main())
