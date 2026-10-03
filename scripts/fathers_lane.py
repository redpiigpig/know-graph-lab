#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教父 37 卷「重新對齊＋缺譯補譯」長跑 lane。

  python -X utf8 scripts/fathers_lane.py --status          # 讀狀態檔，印 DONE／PENDING（給 keeper 用，不讀書）
  python -X utf8 scripts/fathers_lane.py --run             # 跑（可續跑；額度用盡自停，exit 3）
  python -X utf8 scripts/fathers_lane.py --run --only <id前8> [--no-fill]

階段 1：每卷 fathers_realign_volume.process_volume(apply=True)（只做一次，狀態檔記 realigned）。
階段 2：缺譯小的先補（fathers_fill_gaps.fill_book），補到沒有缺譯或引擎全掛。

🚨 這支會改寫書 JSONL：處理哪一卷就把那卷 id 寫進 output/restructure/DO_NOT_TOUCH_ids.txt
   （KGL_Footnote_Relink 與 fix_fathers_heading_swallow 會讀），處理完移除；結束時一律清掉自己加的。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

OUT = ROOT / "output" / "fathers_gap"
STATE = OUT / "lane_state.json"
DNT = ROOT / "output" / "restructure" / "DO_NOT_TOUCH_ids.txt"


def ids() -> list[str]:
    return (OUT / "ids37.txt").read_text(encoding="utf-8").split()


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"volumes": {}, "all_done": False}


def save_state(st: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(STATE)


def dnt_add(bid: str) -> None:
    cur = set(DNT.read_text(encoding="utf-8").split()) if DNT.exists() else set()
    cur.add(bid)
    DNT.write_text("\n".join(sorted(cur)) + "\n", encoding="utf-8")


def dnt_remove(bid: str) -> None:
    cur = set(DNT.read_text(encoding="utf-8").split()) if DNT.exists() else set()
    cur.discard(bid)
    DNT.write_text(("\n".join(sorted(cur)) + "\n") if cur else "", encoding="utf-8")


def log(msg: str) -> None:
    print(f"[{time.strftime('%m-%d %H:%M:%S')}] {msg}", flush=True)


def run(only: str | None, do_fill: bool) -> int:
    import fathers_fill_gaps as ff
    import fathers_realign_volume as rv
    st = load_state()
    vols = st.setdefault("volumes", {})
    todo = [b for b in ids() if not only or b.startswith(only)]
    # 階段 1：對齊
    for bid in todo:
        v = vols.setdefault(bid, {})
        if v.get("realigned"):
            continue
        dnt_add(bid)
        try:
            log(f"對齊 {bid[:8]} …")
            s = rv.process_volume(bid, apply=True)
            v["realign"] = {k: s.get(k) for k in ("gap_body_rows", "gap_body_letters", "en_body_letters",
                                                  "gap_fn_rows", "zh_orphan_rows", "zh_orphan_chars",
                                                  "rescued_rows", "n_errs")}
            if s.get("applied"):
                v["realigned"] = True
                v.pop("blocked", None)
                log(f"  ✓ {bid[:8]} 已對齊並寫回；缺譯正文 {s['gap_body_rows']} 列／{s['gap_body_letters']} 字母，註文 {s['gap_fn_rows']} 列")
            else:
                v["blocked"] = s.get("conservation_errors")
                log(f"  ✗ {bid[:8]} 未寫回（守恆閘）：{s.get('conservation_errors')}")
            if s.get("push_error"):
                v["push_error"] = s["push_error"]
        finally:
            dnt_remove(bid)
            save_state(st)
    if not do_fill:
        return 0
    # 階段 2：補譯（缺口小的先）
    order = sorted([b for b in todo if vols.get(b, {}).get("realigned")],
                   key=lambda b: (vols[b].get("realign") or {}).get("gap_body_letters") or 0)
    engines_down = False
    for bid in order:
        v = vols[bid]
        if v.get("fill_done"):
            continue
        dnt_add(bid)
        try:
            log(f"補譯 {bid[:8]} …")
            total, done = ff.fill_book(bid, apply=True)
            v["fill_last"] = {"todo_before": total, "filled": done, "at": time.strftime("%m-%d %H:%M")}
            left = total - done
            if total == 0 or (left == 0):
                v["fill_done"] = True
            elif done == 0:
                engines_down = True
            log(f"  {bid[:8]} 缺譯 {total}，本輪補 {done}，剩 {left}")
        finally:
            dnt_remove(bid)
            save_state(st)
        if engines_down:
            log("引擎沒有產出，本輪結束（keeper 之後再接）")
            return 3
    # 統計
    remaining = [b for b in ids() if not vols.get(b, {}).get("blocked")
                 and (not vols.get(b, {}).get("fill_done") or not vols.get(b, {}).get("realigned"))]
    st["all_done"] = not remaining
    save_state(st)
    return 0 if not remaining else 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--no-fill", action="store_true")
    a = ap.parse_args()
    if a.status:
        print("DONE" if load_state().get("all_done") else "PENDING")
        return 0
    if a.run:
        return run(a.only, not a.no_fill)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
