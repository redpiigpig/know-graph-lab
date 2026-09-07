# -*- coding: utf-8 -*-
"""把片頭與本體接成一支完整影片。

片頭是實拍原音（已經把序幕講完了），本體從第一幕開始、目前還沒有旁白，
所以本體要先補一條無聲音軌，兩段的串流規格才對得起來、能直接 concat 不用重壓。

用法：
    python join_parts.py 片頭_v1.mp4 本體_第一幕起.mp4 --out 人魚島解說_全片.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
OUTDIR = PROJ / "out"
WORK = OUTDIR / "_join"
FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=cwd)
    if r.returncode:
        print("失敗：", " ".join(str(c) for c in cmd)[:280])
        print((r.stderr or "")[-700:])
        sys.exit(1)


def probe(path: Path) -> dict:
    # 一定要指定 utf-8：ffprobe 的 JSON 會把中文檔名放進去，text=True 預設拿
    # cp950 解，讀取執行緒直接炸掉、stdout 變成 None，而 returncode 還是 0。
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                        "-of", "json", str(path)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return json.loads(r.stdout)


def describe(path: Path):
    info = probe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    return dict(dur=float(info["format"]["duration"]),
                size=f"{v['width']}x{v['height']}" if v else "?",
                fps=v.get("r_frame_rate") if v else "?",
                audio=bool(a))


def ensure_audio(path: Path, out: Path) -> Path:
    """沒有音軌就補一條靜音，有的話原樣拿來用。"""
    if describe(path)["audio"]:
        return path
    print(f"  {path.name} 沒有音軌，補靜音")
    run(FF + ["-i", str(path), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
              "-shortest", "-map", "0:v", "-map", "1:a", "-c:v", "copy"] + AENC + [str(out)])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+", help="要接起來的檔名（相對 out/ 或絕對路徑）")
    ap.add_argument("--out", default="人魚島解說_全片.mp4")
    args = ap.parse_args()

    WORK.mkdir(parents=True, exist_ok=True)
    prepared, total = [], 0.0
    for i, name in enumerate(args.parts):
        p = Path(name)
        if not p.is_absolute():
            p = OUTDIR / name
        if not p.exists():
            print(f"找不到 {p}")
            sys.exit(1)
        d = describe(p)
        print(f"  {p.name}  {d['dur']:.1f}s  {d['size']}  {'有聲' if d['audio'] else '無聲'}")
        total += d["dur"]
        prepared.append(ensure_audio(p, WORK / f"part_{i:02d}.mp4"))

    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in prepared), encoding="utf-8")
    final = OUTDIR / args.out
    run(FF + ["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(final)])
    got = describe(final)
    print(f"\n完成：{final}")
    print(f"  {got['dur']:.1f} 秒（{int(got['dur'] // 60)} 分 {int(got['dur'] % 60)} 秒）"
          f"／預期 {total:.1f} 秒")


if __name__ == "__main__":
    main()
