# -*- coding: utf-8 -*-
"""驗每一段的長度有沒有對上它該佔的 cue 秒數。

音樂與音效是照 cues.json 的時間鋪的，影片卻是一段一段接出來的；只要有一段渲短了，
後面每一句的音效就整批往前偏，而且愈後面偏愈多——畫面本身完全正常，看不出來。
所以出片後一定要跑這支。

用法：
    python check_sync.py --from 67.83                    # 驗 _segments 裡的每一段
    python check_sync.py --from 67.83 --video out/本體_第一幕起_v2.mp4
"""
import argparse
import json
import subprocess
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
SEG = PROJ / "out" / "_segments"


def dur_of(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--video", help="接好的整段影片，比對總長")
    ap.add_argument("--tol", type=float, default=0.5, help="容許誤差（秒）")
    args = ap.parse_args()

    data = json.loads((PROJ / "cues.json").read_text(encoding="utf-8"))
    t1 = args.t1 or data["total"]
    cues = [c for c in data["cues"] if c["t"] + c["dur"] > args.t0 and c["t"] < t1]
    broll = {}
    bf = PROJ / "素材" / "預告片" / "broll.json"
    if bf.exists():
        broll = {int(k) for k in json.loads(bf.read_text(encoding="utf-8"))}

    # 照 assemble.py 同一套規則重算分段，才知道第 k 段該多長
    runs, cur = [], []
    for c in cues:
        if c["i"] in broll:
            if cur:
                runs.append(cur); cur = []
            runs.append([c])
        else:
            cur.append(c)
    if cur:
        runs.append(cur)

    want = sum(g[-1]["t"] + g[-1]["dur"] - g[0]["t"] for g in runs)
    got, bad, drift = 0.0, [], 0.0
    for k, g in enumerate(runs):
        p = SEG / f"seg_{k:03d}.mp4"
        if not p.exists():
            bad.append((k, "缺檔", 0, 0))
            continue
        exp = g[-1]["t"] + g[-1]["dur"] - g[0]["t"]
        act = dur_of(p)
        got += act
        drift += act - exp
        if abs(act - exp) > args.tol:
            bad.append((k, f"cue {g[0]['i']}–{g[-1]['i']}", exp, act))

    print(f"分段 {len(runs)} 段：cue 上應為 {want:.1f}s，實得 {got:.1f}s，累積漂移 {got - want:+.1f}s")
    if bad:
        print(f"對不上的 {len(bad)} 段（誤差 > {args.tol}s）：")
        for k, tag, exp, act in bad[:20]:
            print(f"  seg_{k:03d}  {tag}  應 {exp:.2f}s  實 {act:.2f}s  {act - exp:+.2f}s")
    else:
        print("每一段都對得上")

    if args.video:
        v = Path(args.video)
        if not v.is_absolute():
            v = PROJ / "out" / args.video
        print(f"整段影片 {dur_of(v):.1f}s（cue 上應為 {want:.1f}s）")


if __name__ == "__main__":
    main()
