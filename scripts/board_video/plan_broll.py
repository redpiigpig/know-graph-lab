# -*- coding: utf-8 -*-
"""替全片排「哪幾條 cue 切預告片畫面」，寫成 broll.json。

原則跟使用者要的一樣：**複述劇情時看電影畫面，講分析時回黑板**。
所以劇情五幕與四個角色節點才排 B-roll，倫理／神話／結語那幾段留給黑板。
同一個節點的候選圖輪流用，且不連續兩條 cue 都切走（黑板要有機會把字寫出來）。

用法：
    python plan_broll.py            # 看排出來長怎樣
    python plan_broll.py --apply    # 寫進 素材/預告片/broll.json
"""
import argparse
import json
import re
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
TRAILERS = PROJ / "素材" / "預告片"

# 這些節點在複述劇情或介紹角色，適合切電影畫面
BROLL_NODES = ["N10", "N11", "N12", "N13", "N14", "N20", "N21", "N22", "N23", "N24"]
MIN_DUR = 2.4          # 太短的 cue 切過去會像閃屏
EVERY = 2              # 每隔幾條 cue 才切一次


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cues = json.loads((PROJ / "cues.json").read_text(encoding="utf-8"))["cues"]
    sug = json.loads((TRAILERS / "建議配圖.json").read_text(encoding="utf-8"))

    # 建議配圖裡是 "[287] qTROMuvibHs_056430.jpg" 這種字串，取出編號
    pool = {}
    for nid, info in sug.items():
        nums = [int(m.group(1)) for s in info.get("shots", [])
                if (m := re.match(r"\[(\d+)\]", s))]
        if nums:
            pool[nid] = nums

    plan, used = {}, {}
    for c in cues:
        nid = c["node"]
        if nid not in BROLL_NODES or nid not in pool or c["dur"] < MIN_DUR:
            continue
        seen = used.get(nid, -1) + 1
        used[nid] = seen
        if seen % EVERY:                     # 隔一條切一次
            continue
        shots = pool[nid]
        plan[str(c["i"])] = {"shot": shots[(seen // EVERY) % len(shots)]}

    total = sum(c["dur"] for c in cues)
    broll_dur = sum(c["dur"] for c in cues if str(c["i"]) in plan)
    print(f"排了 {len(plan)} 條 B-roll／共 {len(cues)} 條 cue")
    print(f"預告片畫面佔 {broll_dur:.0f} 秒，全片 {total:.0f} 秒（{broll_dur / total * 100:.0f}%）")
    by_node = {}
    for c in cues:
        if str(c["i"]) in plan:
            by_node.setdefault(c["node"], []).append(c["i"])
    for nid in BROLL_NODES:
        if nid in by_node:
            print(f"  {nid}: cue {by_node[nid]}")

    if args.apply:
        out = TRAILERS / "broll.json"
        out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n寫出 {out}")
    else:
        print("\n（加 --apply 才會寫檔）")


if __name__ == "__main__":
    main()
