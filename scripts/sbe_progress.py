#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""東方聖卷（SBE）逐卷進度：已譯／死段／真正待譯。

為什麼需要這支
--------------
`sbe_translate.py --loop` 印出的「sbe done」不等於翻完。`mueller_auto.is_done()`
把「連續失敗 MAX_FAIL(=3) 次」的段落算成**已耗盡**、計入完成——原意是不讓一兩個
死段卡住整本，但引擎整段時間壞掉時（Haiku 的 OAuth 401、Gemini 免費層日額度用完），
它會把整本判死：2026-09-17 實測易經 2,620 段、耆那教 2,399 段全是死段，那兩卷的
譯文覆蓋率其實只有 15% 與 4%，而佇列回報「done」。

所以判「翻完了沒」要看資料，不要看 log（[[feedback_silent_zero_is_a_bug]] 同理）。
死段通常不是壞資料，是當時的引擎壞掉；引擎換好之後把 fail 歸零重跑就會過。

    python -X utf8 scripts/sbe_progress.py            # 逐卷一覽
    python -X utf8 scripts/sbe_progress.py --reset    # 把「無譯文卻已耗盡」的 fail 歸零
    python -X utf8 scripts/sbe_progress.py --reset --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mueller_auto as ma  # noqa: E402
from sbe_translate import WORKS  # noqa: E402


# 稽核判定「來源沒有可譯內容」而留白的記號（audit_llm_meta_replies.BLANK_MARK）。
# 那不是待辦——硬翻只會得到錯譯——所以要跟「還沒翻」分開算。
BLANK_MARK = "blank-unusable-source"


def scan(slug: str) -> tuple[int, int, int, int, list[Path]]:
    """(段數, 已譯, 留白, 死段, sec 檔清單)。死段＝沒有譯文且 fail >= MAX_FAIL。"""
    wd = ma.work_dir(slug)
    secs = sorted(wd.glob("sec*.json")) if wd.exists() else []
    total = done = blank = dead = 0
    for p in secs:
        s = json.loads(p.read_text(encoding="utf-8"))
        en = s.get("en") or []
        zh = s.get("zh") or []
        fail = s.get("fail") or []
        engines = s.get("engines") or []
        for j in range(len(en)):
            total += 1
            z = (zh[j] if j < len(zh) else None) or ""
            f = fail[j] if j < len(fail) else 0
            if z.strip():
                done += 1
            elif j < len(engines) and engines[j] == BLANK_MARK:
                blank += 1
            elif f >= ma.MAX_FAIL:
                dead += 1
    return total, done, blank, dead, secs


def reset_dead(slug: str, secs: list[Path], apply: bool) -> int:
    """把「沒有譯文卻被記到 MAX_FAIL」的 fail 歸零。已譯的段落一律不動。"""
    cleared = 0
    for p in secs:
        s = json.loads(p.read_text(encoding="utf-8"))
        en = s.get("en") or []
        zh = s.get("zh") or []
        fail = s.get("fail") or []
        if not fail:
            continue
        changed = False
        for j in range(len(en)):
            z = (zh[j] if j < len(zh) else None) or ""
            if not z.strip() and (fail[j] if j < len(fail) else 0):
                fail[j] = 0
                cleared += 1
                changed = True
        if changed and apply:
            s["fail"] = fail
            p.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    return cleared


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true",
                    help="把「無譯文卻已耗盡」的 fail 歸零，讓它們重新排進佇列")
    ap.add_argument("--apply", action="store_true", help="真的寫回（預設只試跑）")
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    all_total = all_done = all_blank = all_dead = all_reset = 0
    for w in WORKS:
        total, done, blank, dead, secs = scan(w["slug"])
        left = total - done - blank - dead
        # 分母扣掉留白：那些段落已經處理過了，只是處理的結論是「不譯」。
        pct = (done / (total - blank) * 100) if total - blank else 0.0
        line = (f"  {w['slug']:24s} {done:6d}/{total - blank:<6d}（{pct:5.1f}%）"
                f" 待譯 {left:5d}")
        if blank:
            line += f"　留白 {blank}"
        if dead:
            line += f"　🚨 死段 {dead}"
        print(line)
        if a.reset:
            n = reset_dead(w["slug"], secs, a.apply)
            all_reset += n
            if n:
                print(f"    ↳ 清掉失敗計數 {n} 段")
        all_total += total
        all_done += done
        all_blank += blank
        all_dead += dead

    denom = all_total - all_blank
    pct = (all_done / denom * 100) if denom else 0.0
    print(f"合計 {all_done:,}/{denom:,}（{pct:.1f}%）"
          f"　留白 {all_blank:,}　死段 {all_dead:,}"
          f"　待譯 {denom - all_done - all_dead:,}")
    if a.reset:
        print(f"共清掉 {all_reset:,} 段的失敗計數"
              + ("（已寫回）" if a.apply else "（試跑；加 --apply 才寫）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
