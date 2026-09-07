# -*- coding: utf-8 -*-
"""片頭：開場白 → 海報 → 序幕正文，全部用使用者實拍的原音。

順序是使用者定的：先問好，海報才出現，然後接序幕正文。
開場白最後一句是「所以我們要講的是——」，海報就接在那一刀上。
正文那一分鐘不會一直盯著同一顆布偶，會在指定的句子切到劇照／預告片／暴雷卡再切回來；
畫面換來換去但聲音不斷，因為音軌是整段最後才 mux 回去的。

用法：
    python make_opening.py            # 出 片頭_v1.mp4
    python make_opening.py --nosub    # 不燒字幕
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
SRC = PROJ / "素材" / "片頭"
WORK = PROJ / "out" / "_opening"
TRAILERS = PROJ / "素材" / "預告片"
SFX = PROJ / "素材" / "音效" / "合成"

GREET = SRC / "問好_979496.mp4"
PROLOGUE = SRC / "序幕_665250.mp4"
POSTER = PROJ / "素材" / "封面" / "影片封面.png"
AVATAR = PROJ / "素材" / "多馬豬" / "多馬豬_圓形.png"

FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30"]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

# 兩支實拍的頭尾都有空白，照 whisper 的逐句時間切掉
GREET_TRIM = (2.20, 20.00)      # 講話 3.22–19.32
PROLOGUE_TRIM = (5.20, 66.60)   # 講話 6.03–65.57
POSTER_SEC = 3.6

# 正文要切走的段落（時間以裁切後的正文為準）。來源：圖片路徑、("shot", 編號)、或 ("card", 名稱)
CUTAWAYS = [
    (2.60, 6.20, ("shot", 287)),                                   # 「就是劇場版吉伊卡哇──人魚島的秘密」
    (22.00, 25.80, PROJ / "素材" / "劇照" / "作者被說毫無人性.jpg"),  # 「被說是毫無人性」
    (38.70, 44.40, PROJ / "素材" / "劇照" / "電影劇照.webp"),        # 「要來解說人魚島的秘密」
    (49.10, 54.30, ("card", "spoiler")),                           # 「以下的劇情我們會瘋狂暴雷」
]

# whisper 聽錯的字（吉利卡挖／多瑪珠／等牙便術…）在這裡改回來，順序對應逐句時間
SUBS_GREET = [
    "いらっしゃいませ！歡迎來到多馬茶房",
    "我是多馬豬",
    "今天的電影辯士系列",
    "我們有請到一位新觀眾",
    "所以我們今天要講的是——",
]
SUBS_PROLOGUE = [
    "沒錯，就是《劇場版 吉伊卡哇──人魚島的秘密》",
    "我原本自己沒有特別在看吉伊卡哇的動畫或漫畫",
    "只是從一些網路討論和短影片得知",
    "這可能是一部比較暗黑向的卡哇伊動畫",
    "尤其是這一次劇場版，作者",
    "Nagano 老師被說是「毫無人性」",
    "所以就讓我特別想去看這部動畫到底有多毀童年",
    "結果走出電影院之後",
    "我陷入了對宇宙的冥想和無盡的哲學沉思中",
    "所以這部片就是要來解說人魚島的秘密",
    "以及它可以從倫理學跟比較神話學的角度來做分析",
    "以下的劇情我們會瘋狂暴雷",
    "所以如果你不想要被劇透的話",
    "可以先看完電影再回來看這部影片",
    "那我們就準備開始囉",
]


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=cwd)
    if r.returncode:
        print("失敗：", " ".join(str(c) for c in cmd)[:280])
        print((r.stderr or "")[-700:])
        sys.exit(1)


def dur_of(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


# ── 兩張自己畫的卡 ───────────────────────────────────────────
def lower_third(out: Path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(r"C:\Windows\Fonts\msjhbd.ttc", 72)
    small = ImageFont.truetype(r"C:\Windows\Fonts\msjh.ttc", 36)
    title, sub = "多馬茶房・電影辯士", "解析《劇場版 吉伊卡哇──人魚島的秘密》"
    x, y = 130, 770
    w = int(max(d.textlength(title, font=big), d.textlength(sub, font=small))) + 70
    d.rectangle([x - 34, y - 26, x + w, y + 148], fill=(24, 32, 28, 210))
    d.rectangle([x - 34, y - 26, x - 20, y + 148], fill=(217, 178, 92, 255))
    d.text((x, y), title, font=big, fill=(255, 246, 216, 255))
    d.text((x + 4, y + 94), sub, font=small, fill=(206, 216, 200, 255))
    im.save(out)


def spoiler_card(out: Path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (1920, 1080), "#1b0f10")
    d = ImageDraw.Draw(im)
    for i in range(0, 1080, 10):                      # 一點掃描線質感
        d.line([(0, i), (1920, i)], fill="#231315")
    big = ImageFont.truetype(r"C:\Windows\Fonts\msjhbd.ttc", 150)
    mid = ImageFont.truetype(r"C:\Windows\Fonts\msjhbd.ttc", 58)
    small = ImageFont.truetype(r"C:\Windows\Fonts\msjh.ttc", 40)
    d.text((960, 380), "以下瘋狂暴雷", font=big, fill="#ff5b5b", anchor="mm",
           stroke_width=6, stroke_fill="#2a0d0d")
    d.text((960, 560), "還沒看電影的，先去看完再回來", font=mid, fill="#ffe9c9", anchor="mm")
    d.text((960, 660), "SPOILER  ALERT", font=small, fill="#8b6a6a", anchor="mm")
    if AVATAR.exists():
        pig = Image.open(AVATAR).convert("RGBA").resize((300, 300))
        im.paste(pig, (810, 720), pig)
    im.save(out)


# ── 片段 ────────────────────────────────────────────────────
def trim(src: Path, t0: float, t1: float, out: Path, video_filter: str, with_audio=True):
    cmd = FF + ["-ss", f"{t0:.2f}", "-to", f"{t1:.2f}", "-i", str(src), "-vf", video_filter]
    cmd += (["-map", "0:v", "-map", "0:a"] + VENC + AENC) if with_audio else (["-an"] + VENC)
    run(cmd + [str(out)])


def greeting_segment(out: Path):
    """開場白：緩推近、暖調、暈影，第 1.5 秒浮出頻道標題卡，收在白閃。"""
    lt = WORK / "lower_third.png"
    lower_third(lt)
    d = GREET_TRIM[1] - GREET_TRIM[0]
    vf = ("[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
          "zoompan=z='min(zoom+0.00035,1.10)':d=1:s=1920x1080:fps=30,"
          "eq=contrast=1.06:saturation=1.12:brightness=0.01,vignette=PI/5,"
          f"fade=t=out:st={d - 0.45:.2f}:d=0.45:color=white[v0];"
          "[1:v]format=rgba,fade=in:st=0:d=0.4:alpha=1,fade=out:st=5.0:d=0.6:alpha=1[lt];"
          "[v0][lt]overlay=0:0:enable='between(t,1.5,6.6)'[v]")
    # 標題卡要 -loop 1 變成連續串流；單張圖餵給 fade 會被凍在 alpha=0，等於整張看不見
    run(FF + ["-ss", f"{GREET_TRIM[0]}", "-to", f"{GREET_TRIM[1]}", "-i", str(GREET),
              "-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", str(lt),
              "-filter_complex", vf, "-map", "[v]", "-map", "0:a"]
        + VENC + AENC + [str(out)])


def poster_segment(out: Path):
    """海報：白閃進場、緩慢推近，配一聲 whoosh 與提示音。"""
    vf = ("[0:v]scale=2400:-1,zoompan=z='min(zoom+0.0006,1.16)':d=1:s=1920x1080:fps=30,"
          f"fade=t=in:st=0:d=0.45:color=white,"
          f"fade=t=out:st={POSTER_SEC - 0.4:.2f}:d=0.4:color=black[v]")
    whoosh, ding = SFX / "whoosh_長.wav", SFX / "叮_提示.wav"
    cmd = FF + ["-loop", "1", "-t", f"{POSTER_SEC}", "-i", str(POSTER)]
    chains, labels = [], []
    for i, (f, vol, delay) in enumerate([(whoosh, 0.7, 0), (ding, 0.45, 550)]):
        if not f.exists():
            continue
        cmd += ["-i", str(f)]
        idx = len(labels) + 1
        pre = f"adelay={delay}|{delay}," if delay else ""
        chains.append(f"[{idx}:a]{pre}volume={vol}[a{idx}]")
        labels.append(f"[a{idx}]")
    if labels:
        mix = ";".join(chains) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:duration=first[a]"
        run(cmd + ["-filter_complex", vf + ";" + mix, "-map", "[v]", "-map", "[a]",
                   "-t", f"{POSTER_SEC}"] + VENC + AENC + [str(out)])
    else:
        run(cmd + ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", vf,
                   "-map", "[v]", "-map", "1:a", "-t", f"{POSTER_SEC}"] + VENC + AENC + [str(out)])


def still_clip(img: Path, dur: float, out: Path):
    vf = (f"scale=2400:-1,zoompan=z='min(zoom+0.0006,1.14)':d=1:s=1920x1080:fps=30,"
          f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(dur - 0.25, 0.1):.2f}:d=0.25")
    run(FF + ["-loop", "1", "-t", f"{dur:.2f}", "-i", str(img), "-vf", vf, "-an"]
        + VENC + [str(out)])


def shot_clip(shot, dur: float, out: Path):
    src = TRAILERS / f"{shot['video']}.mp4"
    vf = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,"
          f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(dur - 0.25, 0.1):.2f}:d=0.25")
    run(FF + ["-ss", f"{max(0, shot['t'] - 0.35):.2f}", "-t", f"{dur:.2f}", "-i", str(src),
              "-vf", vf, "-an"] + VENC + [str(out)])


def real_clip(src: Path, t0: float, t1: float, out: Path):
    vf = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
          "zoompan=z='min(zoom+0.00025,1.08)':d=1:s=1920x1080:fps=30,"
          "eq=contrast=1.05:saturation=1.1,vignette=PI/5")
    trim(src, t0, t1, out, vf, with_audio=False)


def prologue_segment(out: Path, shots):
    body = WORK / "pro_trim.mp4"
    trim(PROLOGUE, PROLOGUE_TRIM[0], PROLOGUE_TRIM[1], body,
         "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080")
    total = dur_of(body)

    parts, cursor, k = [], 0.0, 0
    for a, b, spec in CUTAWAYS + [(total, total, None)]:
        a, b = min(a, total), min(b, total)
        if a > cursor + 0.2:
            p = WORK / f"pro_{k:02d}_real.mp4"
            real_clip(body, cursor, a, p)
            parts.append(p)
            k += 1
        if spec is None:
            break
        p = WORK / f"pro_{k:02d}_cut.mp4"
        if isinstance(spec, tuple) and spec[0] == "shot":
            shot = shots.get(spec[1])
            if shot:
                shot_clip(shot, b - a, p)
            else:
                print(f"  找不到截圖 {spec[1]}，改用實拍")
                real_clip(body, a, b, p)
        elif isinstance(spec, tuple) and spec[0] == "card":
            card = WORK / f"card_{spec[1]}.png"
            spoiler_card(card)
            still_clip(card, b - a, p)
        else:
            still_clip(Path(spec), b - a, p)
        parts.append(p)
        k += 1
        cursor = b

    lst = WORK / "pro_concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    silent = WORK / "pro_video.mp4"
    run(FF + ["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])
    run(FF + ["-i", str(silent), "-i", str(body), "-map", "0:v", "-map", "1:a",
              "-shortest", "-c:v", "copy"] + AENC + [str(out)])


# ── 字幕 ────────────────────────────────────────────────────
def ass_time(s: float) -> str:
    h, s = divmod(max(0.0, s), 3600)
    m, s = divmod(s, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_ass(path: Path, greet_len: float, poster_len: float):
    times = json.loads((SRC / "逐句時間.json").read_text(encoding="utf-8"))
    rows = []
    for line, txt in zip(times.get("問好_979496.mp4", []), SUBS_GREET):
        rows.append((line["t"] - GREET_TRIM[0], line["e"] - GREET_TRIM[0], txt))
    off = greet_len + poster_len - PROLOGUE_TRIM[0]
    for line, txt in zip(times.get("序幕_665250.mp4", []), SUBS_PROLOGUE):
        rows.append((line["t"] + off, line["e"] + off, txt))
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
            "BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding\n"
            "Style: Def,Microsoft JhengHei,54,&H00FFFFFF,&H00202020,&H80000000,-1,0,1,4,2,2,"
            "160,160,58,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, "
            "MarginR, MarginV, Effect, Text\n")
    body = "\n".join(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Def,,0,0,0,,{t}"
                     for a, b, t in rows)
    path.write_text(head + body, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="片頭_v1.mp4")
    ap.add_argument("--nosub", action="store_true")
    args = ap.parse_args()

    WORK.mkdir(parents=True, exist_ok=True)
    shots = {s["n"]: s for s in json.loads((TRAILERS / "截圖索引.json").read_text(encoding="utf-8"))}

    print("開場白…")
    a = WORK / "a_greet.mp4"
    greeting_segment(a)
    print("海報…")
    b = WORK / "b_poster.mp4"
    poster_segment(b)
    print("序幕正文…")
    c = WORK / "c_prologue.mp4"
    prologue_segment(c, shots)

    lst = WORK / "all.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in (a, b, c)), encoding="utf-8")
    merged = WORK / "merged.mp4"
    run(FF + ["-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "copy"] + AENC + [str(merged)])

    final = PROJ / "out" / args.out
    if args.nosub:
        merged.replace(final)
    else:
        write_ass(WORK / "subs.ass", dur_of(a), dur_of(b))
        run(FF + ["-i", "merged.mp4", "-vf", "subtitles=subs.ass", "-c:a", "copy"]
            + VENC + [str(final)], cwd=str(WORK))
    print(f"\n完成：{final}（{dur_of(final):.1f} 秒）")


if __name__ == "__main__":
    main()
