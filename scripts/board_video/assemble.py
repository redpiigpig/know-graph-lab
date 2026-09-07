# -*- coding: utf-8 -*-
"""把「黑板段」與「預告片段」混剪成一支影片。

黑板段由 render.mjs 逐格畫出來，預告片段直接從官方預告剪；兩邊時間軸共用 cues.json，
所以某一條 cue 指定成 B-roll 時，它佔的秒數不變，整支片長度也不變。

哪幾條 cue 要切預告片，寫在 素材/預告片/broll.json：
    {"63": {"shot": 394}, "65": {"shot": 388, "speed": 0.8}}
key 是 cue 編號，shot 是接觸表上的截圖編號（用它來定位是哪支預告的第幾秒）。

用法：
    python assemble.py --from 457 --to 488 --out 試片_混剪.mp4
    python assemble.py --all --out 人魚島解說_混剪.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
HERE = Path(__file__).parent
SEG = PROJ / "out" / "_segments"
TRAILERS = PROJ / "素材" / "預告片"
MASCOT = PROJ / "素材" / "多馬豬" / "多馬豬_圓形.png"

FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30"]


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=cwd)
    if r.returncode:
        print("失敗：", " ".join(str(c) for c in cmd)[:300])
        print((r.stderr or "")[-800:])
        sys.exit(1)


def ass_time(s: float) -> str:
    h, s = divmod(max(0.0, s), 3600)
    m, s = divmod(s, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_ass(cues, t0, path: Path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Def,Microsoft JhengHei,52,&H00FFFFFF,&H00202020,&H80000000,0,0,1,4,2,2,340,140,54,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [head]
    for c in cues:
        s, e = c["t"] - t0, c["t"] + c["dur"] - t0
        text = c["text"].replace("\n", " ")
        lines.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Def,,0,0,0,,{text}")
    path.write_text("\n".join(lines), encoding="utf-8")


def board_segment(theme, t0, t1, out: Path):
    run(["node", str(HERE / "render.mjs"), "--theme", theme, "--from", f"{t0}",
         "--to", f"{t1}", "--nosub", "--cover", "0", "--out", str(Path("_segments") / out.name)])


def clip_segment(shot, dur, out: Path, speed=1.0):
    src = TRAILERS / f"{shot['video']}.mp4"
    start = max(0.0, shot["t"] - 0.35)
    vf = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
          f"setpts={1/speed:.4f}*PTS,fps=30")
    cmd = FF + ["-ss", f"{start}", "-t", f"{dur * speed:.2f}", "-i", str(src)]
    if MASCOT.exists():
        cmd += ["-i", str(MASCOT), "-filter_complex",
                f"[0:v]{vf}[v];[1:v]scale=240:-1[m];[v][m]overlay=46:H-150-h[o]",
                "-map", "[o]"]
    else:
        cmd += ["-vf", vf]
    cmd += ["-an"] + ENC + [str(out)]
    run(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="t0", type=float, default=0)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--theme", default="paper")
    ap.add_argument("--out", default="混剪.mp4")
    ap.add_argument("--nosub", action="store_true")
    args = ap.parse_args()

    data = json.loads((PROJ / "cues.json").read_text(encoding="utf-8"))
    broll = {}
    bf = TRAILERS / "broll.json"
    if bf.exists():
        broll = {int(k): v for k, v in json.loads(bf.read_text(encoding="utf-8")).items()}
    shots = {s["n"]: s for s in json.loads((TRAILERS / "截圖索引.json").read_text(encoding="utf-8"))}

    t1 = data["total"] if args.all else (args.t1 or data["total"])
    cues = [c for c in data["cues"] if c["t"] + c["dur"] > args.t0 and c["t"] < t1]
    if not cues:
        print("這個範圍沒有 cue")
        return
    t0 = cues[0]["t"]
    SEG.mkdir(parents=True, exist_ok=True)

    # 切成「連續黑板段」與「單條預告片段」
    runs, cur = [], []
    for c in cues:
        if c["i"] in broll:
            if cur:
                runs.append(("board", cur)); cur = []
            runs.append(("clip", [c]))
        else:
            cur.append(c)
    if cur:
        runs.append(("board", cur))

    parts = []
    for k, (kind, group) in enumerate(runs):
        out = SEG / f"seg_{k:03d}.mp4"
        a, b = group[0]["t"], group[-1]["t"] + group[-1]["dur"]
        if kind == "board":
            print(f"  黑板段 {a:.1f}–{b:.1f}s（{len(group)} 條）")
            board_segment(args.theme, a, b, out)
        else:
            spec = broll[group[0]["i"]]
            shot = shots.get(spec["shot"])
            if not shot:
                print(f"  找不到截圖 {spec['shot']}，這段改用黑板")
                board_segment(args.theme, a, b, out)
            else:
                print(f"  預告片段 {a:.1f}–{b:.1f}s ← [{spec['shot']}] {shot['video']} {shot['t']}s")
                clip_segment(shot, b - a, out, spec.get("speed", 1.0))
        parts.append(out)

    lst = SEG / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    merged = SEG / "merged.mp4"
    run(FF + ["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(merged)])

    final = PROJ / "out" / args.out
    if args.nosub:
        merged.replace(final)
    else:
        ass = SEG / "subs.ass"
        write_ass(cues, t0, ass)
        # subtitles 濾鏡的檔名不能帶磁碟代號（冒號會被當參數分隔），切到字幕檔目錄用相對檔名
        run(FF + ["-i", "merged.mp4", "-vf", "subtitles=subs.ass", "-an"]
            + ENC + [str(final)], cwd=str(SEG))
    print(f"\n完成：{final}")


if __name__ == "__main__":
    main()
