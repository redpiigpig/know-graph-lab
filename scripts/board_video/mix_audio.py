# -*- coding: utf-8 -*-
"""替解說影片鋪背景音樂與音效。

黑板段與預告片段出片時一律是無聲的（`assemble.py` 每段都帶 `-an`，兩邊串流規格才對得
起來），所以旁白以外的聲音全部在這一關補：**音樂**依「幕」換曲、**音效**依 cues.json
裡本來就有的事件（換幕／鏡頭移動／寫字／條目揭露）落點。細流表那兩欄（音效、背景音樂）
講的就是這件事，這支腳本是把它實作出來。

音樂配置在 `素材/音樂/配置.json`（第一次跑會自動產生，一幕一列）。要換曲、調音量、
讓某一幕安靜，改那份檔案再跑一次即可，不必重渲影片。

用法：
    python mix_audio.py --beds-only                    # 只出音樂床／音效床，先聽
    python mix_audio.py --video out/人魚島解說_全片.mp4 --offset 12.04 \
                        --out 人魚島解說_全片_配樂.mp4
    python mix_audio.py --video ... --music-db -18     # 音樂大聲一點

`--offset` 是「cue 時間 → 影片時間」的位移：全片＝片頭（79.87s，已把序幕講完）接上
本體（從第一幕 t=67.83 起），所以 offset = 79.87 - 67.83 = 12.04。只混本體就給 0。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
MUSIC = PROJ / "素材" / "音樂"
SFX = PROJ / "素材" / "音效" / "合成"
CONF = MUSIC / "配置.json"
LIB = Path(r"G:\我的雲端硬碟\創作\影片創作\_素材庫\配樂庫")   # 共用配樂庫（CC BY 4.0 純器樂）
WORK = PROJ / "out" / "_audio"

FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]

# 幕的分組 → 音樂類別（細流表 bgm_by_group 那張表的落實）
GROUP_CAT = {
    "序幕": "01_開場輕快",
    "劇情": "02_敘事鋪底",
    "人魚島": "04_黑暗懸疑",
    "倫理": "05_思辨鋼琴",
    "假設": "05_思辨鋼琴",
    "自然": "04_黑暗懸疑",
    "神話": "06_神話史詩",
    "結語": "07_溫暖收束",
}
XFADE = 1.5      # 幕與幕之間交疊幾秒
MUSIC_DB = -6.0   # 音樂床相對原音的基準（旁白進來時再被 sidechain 壓下去）
MUSIC_LUFS = -26  # 各曲響度先拉齊：CC 音樂彼此差到十幾 dB，不拉齊會忽大忽小

# 音效與音量（dB）：用途對照見 素材/音效/合成/說明.txt
SFX_DB = {
    "擦黑板": -11, "粉筆_寫字": -17, "粉筆_寫字短": -19, "whoosh_短": -15,
    "whoosh_長": -13, "叮_提示": -17, "叮_低": -19, "重擊": -8,
    "爬升_揭露前": -12, "翻頁": -16, "彈出": -17, "心跳": -16,
}
# 「揭露真相」型的幕：幕首下重擊，前 2 秒鋪爬升（說明.txt 指名第五幕與第九幕）
ACCENT_CHAPTERS = ("第五幕", "第九幕")


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", **kw)
    if r.returncode:
        print("失敗：", " ".join(str(c) for c in cmd)[:300])
        print((r.stderr or "")[-900:])
        sys.exit(1)
    return r


def dur_of(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)])
    return float(r.stdout.strip())


def film_t(t, offset, stretch=1.0, t0=0.0):
    """cue 時間 → 影片時間。"""
    return (t - t0) * stretch + t0 + offset


def chapters(cues):
    """把 cue 切成「幕」：(幕名, 分組, 起, 迄)。"""
    out = []
    for c in cues:
        if c.get("chapter") or not out:
            if out:
                out[-1][3] = c["t"]
            out.append([c.get("chapter") or "序幕", c["group"], c["t"], None])
    out[-1][3] = cues[-1]["t"] + cues[-1]["dur"]
    return [tuple(x) for x in out]


def build_conf(chs):
    """一幕一列的音樂配置；同一類別內輪流換曲，免得整段都在重複同一首。"""
    used = {}
    rows = []
    for name, group, a, b in chs:
        cat = GROUP_CAT.get(group, "02_敘事鋪底")
        files = sorted(p.name for p in (MUSIC / cat).glob("*.mp3"))
        if not files:
            rows.append(dict(幕=name, 分組=group, 類別=cat, 曲目="", 音量dB=0))
            continue
        k = used.get(cat, 0)
        used[cat] = k + 1
        rows.append(dict(幕=name, 分組=group, 類別=cat,
                         曲目=files[k % len(files)], 音量dB=0))
    return rows


def music_bed(chs, conf, offset, total, out: Path, stretch=1.0, t0=0.0):
    """一幕一段，各自淡入淡出、交疊 XFADE 秒後疊在一起。"""
    segs = []
    for (name, _g, a, b), row in zip(chs, conf):
        if not row.get("曲目"):
            continue
        src = (LIB if row.get("來源") == "配樂庫" else MUSIC) / row["類別"] / row["曲目"]
        if not src.exists():
            print(f"  找不到 {src.name}，這一幕沒有音樂")
            continue
        fa, fb = film_t(a, offset, stretch, t0), film_t(b, offset, stretch, t0)
        start = max(0.0, fa - XFADE)              # 第一幕往前補到影片開頭
        length = fb - start + XFADE
        seg = WORK / f"m{len(segs):02d}.wav"
        run(FF + ["-stream_loop", "-1", "-i", str(src), "-t", f"{length:.3f}",
                  "-af", (f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
                          f"afade=t=in:st=0:d={XFADE},"
                          f"afade=t=out:st={max(0.0, length - XFADE):.3f}:d={XFADE},"
                          f"loudnorm=I={MUSIC_LUFS}:TP=-2:LRA=11,"
                          f"volume={row.get('音量dB', 0)}dB"),
                  str(seg)])
        segs.append((seg, start))
        print(f"  {name}  {row['類別']}／{row['曲目'][:34]}  {length:.0f}s")

    graph = []
    for k, (_seg, start) in enumerate(segs):
        ms = int(round(max(0.0, start) * 1000))
        graph.append(f"[{k}:a]adelay={ms}|{ms}[d{k}]")
    graph.append("".join(f"[d{k}]" for k in range(len(segs)))
                 + f"amix=inputs={len(segs)}:normalize=0:dropout_transition=0,"
                 + f"atrim=0:{total:.3f},apad=whole_dur={total:.3f},"
                 + "alimiter=limit=0.89[out]")
    return _render_graph([s for s, _ in segs], graph, out)


def sfx_events(cues, offset, sfx_from, stretch=1.0, t0=0.0):
    """cues.json 裡已經有的事件 → 音效落點。規則照 素材/音效/合成/說明.txt。"""
    ev = []
    prev = None
    for c in cues:
        if c["t"] < sfx_from:            # 序幕那段是實拍原音，不鋪黑板音效
            prev = c
            continue
        t = film_t(c["t"], offset, stretch, t0)
        if c.get("chapter"):
            ev.append((t - 0.15, "擦黑板"))
            ev.append((t + 0.45, "粉筆_寫字"))
            if c["chapter"].startswith(ACCENT_CHAPTERS):
                ev.append((t - 2.0, "爬升_揭露前"))
                ev.append((t + 0.1, "重擊"))
        elif c.get("travel"):
            ev.append((t - 0.1, "whoosh_長" if prev and prev["group"] != c["group"]
                       else "whoosh_短"))
        if c.get("first_visit"):
            ev.append((t + 0.55, "粉筆_寫字"))
            if c["group"] == "神話":
                ev.append((t + 0.15, "翻頁"))
        elif prev and prev["node"] == c["node"] and c["reveal"] > prev["reveal"]:
            ev.append((t + 0.35, "粉筆_寫字短"))   # 又寫上一條
            if c["reveal"] >= 3:
                ev.append((t + 0.9, "叮_低"))
        prev = c
    return sorted(ev)


def sfx_bed(events, total, out: Path):
    names = sorted({n for _t, n in events})
    files = [SFX / f"{n}.wav" for n in names]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        print("  找不到音效：", "／".join(missing))
        sys.exit(1)
    idx = {n: i for i, n in enumerate(names)}
    per = {n: [t for t, m in events if m == n] for n in names}

    graph, labels = [], []
    for n in names:
        k = len(per[n])
        outs = "".join(f"[{n}_{j}]" for j in range(k))
        graph.append(f"[{idx[n]}:a]aformat=sample_fmts=fltp:sample_rates=48000:"
                     f"channel_layouts=stereo,volume={SFX_DB.get(n, -16)}dB,asplit={k}{outs}")
        for j, t in enumerate(per[n]):
            ms = int(round(max(0.0, t) * 1000))
            graph.append(f"[{n}_{j}]adelay={ms}|{ms}[e_{idx[n]}_{j}]")
            labels.append(f"[e_{idx[n]}_{j}]")
    graph.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:"
                 f"dropout_transition=0,atrim=0:{total:.3f},apad=whole_dur={total:.3f},"
                 f"alimiter=limit=0.89[out]")
    return _render_graph(files, graph, out)


def _render_graph(inputs, graph, out: Path):
    """濾鏡圖用 -filter_complex_script 餵：事件多的時候命令列長度會爆掉。"""
    script = WORK / (out.stem + ".filter")
    script.write_text(";\n".join(graph), encoding="utf-8")
    cmd = list(FF)
    for p in inputs:
        cmd += ["-i", str(p)]
    cmd += ["-filter_complex_script", str(script), "-map", "[out]", str(out)]
    run(cmd)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", help="要配樂的影片（相對 out/ 或絕對路徑）")
    ap.add_argument("--out", default="人魚島解說_全片_配樂.mp4")
    ap.add_argument("--offset", type=float, default=0.0, help="cue 時間 → 影片時間的位移")
    ap.add_argument("--stretch", type=float, default=1.0,
                    help="影片實長／cue 應有長度；逐段接片的影格進位會累積一兩秒")
    ap.add_argument("--sfx-from", type=float, default=None,
                    help="從第幾秒（cue 時間）起才鋪音效，預設＝第一幕")
    ap.add_argument("--music-db", type=float, default=MUSIC_DB)
    ap.add_argument("--sfx-db", type=float, default=0.0, help="音效整體增減")
    ap.add_argument("--no-soften", action="store_true",
                    help="不要對音樂做人聲頻段挖除與高頻收斂")
    ap.add_argument("--beds-only", action="store_true", help="只出音樂床與音效床")
    ap.add_argument("--reset-conf", action="store_true", help="重產音樂配置")
    args = ap.parse_args()

    WORK.mkdir(parents=True, exist_ok=True)
    data = json.loads((PROJ / "cues.json").read_text(encoding="utf-8"))
    cues = data["cues"]
    chs = chapters(cues)

    if args.reset_conf or not CONF.exists():
        CONF.write_text(json.dumps(build_conf(chs), ensure_ascii=False, indent=2),
                        encoding="utf-8")
        print(f"已產生音樂配置：{CONF}（要換曲改這份）")
    conf = json.loads(CONF.read_text(encoding="utf-8"))
    if len(conf) != len(chs):
        print(f"配置有 {len(conf)} 列、影片有 {len(chs)} 幕，對不起來；"
              f"用 --reset-conf 重產（會蓋掉手改的部分）")
        sys.exit(1)

    video = None
    if args.video:
        video = Path(args.video)
        if not video.is_absolute():
            video = PROJ / "out" / args.video
        if not video.exists():
            print(f"找不到 {video}")
            sys.exit(1)
    total = dur_of(video) if video else data["total"] + args.offset

    sfx_from = args.sfx_from
    if sfx_from is None:
        sfx_from = next((c["t"] for c in cues[1:] if c.get("chapter")), 0.0)

    print("音樂床：")
    mbed = music_bed(chs, conf, args.offset, total, WORK / "音樂床.wav",
                     args.stretch, sfx_from)
    events = sfx_events(cues, args.offset, sfx_from, args.stretch, sfx_from)
    print(f"音效床：{len(events)} 個落點"
          f"（{'／'.join(sorted({n for _t, n in events}))}）")
    sbed = sfx_bed(events, total, WORK / "音效床.wav")

    if args.beds_only or not video:
        print(f"\n完成：{mbed}\n      {sbed}")
        return

    final = PROJ / "out" / args.out
    graph = [
        # 人聲頻段（2 kHz）挖 3.5 dB、8 kHz 以上收掉：讓音樂變柔而不只是變小
        (f"[1:a]volume={args.music_db}dB,equalizer=f=2000:t=q:w=1.1:g=-3.5,"
         f"treble=g=-4:f=8000[m0]" if not args.no_soften
         else f"[1:a]volume={args.music_db}dB[m0]"),
        "[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asplit=2[a0][sc]",
        # 旁白一進來音樂就自動讓路；本體目前無旁白，這一關等於不作用，錄完也不用改參數
        "[m0][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[m]",
        f"[2:a]volume={args.sfx_db}dB[s]",
        "[a0][m][s]amix=inputs=3:normalize=0:dropout_transition=0,"
        "alimiter=limit=0.95[aout]",
    ]
    script = WORK / "mux.filter"
    script.write_text(";\n".join(graph), encoding="utf-8")
    run(FF + ["-i", str(video), "-i", str(mbed), "-i", str(sbed),
              "-filter_complex_script", str(script),
              "-map", "0:v", "-c:v", "copy", "-map", "[aout]",
              "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
              "-movflags", "+faststart", str(final)])
    print(f"\n完成：{final}")


if __name__ == "__main__":
    main()
