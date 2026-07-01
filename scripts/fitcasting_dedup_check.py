# -*- coding: utf-8 -*-
"""fitcasting 去重 dry-run：比對子夾(new/新增資料夾)既有影片 vs root 597 支的時長(±2s)。
名字對不上(子夾=2025-11-22(N).mp4、root=FitCasting_-_…)，只靠 ffprobe 時長找疑似重複。
只列清單、不刪。"""
import os, subprocess, json
G = r"G:\我的雲端硬碟\資料\儲存資料夾\訓練相片\fitcasting"
VID = {".mp4",".mov",".m4v",".webm",".mkv",".avi",".wmv",".mts",".m2ts",".3gp",".mpg",".mpeg"}

def ffprobe_dur(p):
    try:
        o=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",p],
                         capture_output=True,text=True,encoding="utf-8",errors="replace")
        return float(json.loads(o.stdout or "{}").get("format",{}).get("duration") or 0)
    except Exception:
        return 0.0

root_clips, sub_clips = [], []
for a,_,fs in os.walk(G):
    rel = os.path.relpath(a, G)
    for f in fs:
        if os.path.splitext(f)[1].lower() in VID:
            p=os.path.join(a,f)
            (root_clips if rel=="." else sub_clips).append(p)

print(f"root 影片={len(root_clips)}  子夾影片={len(sub_clips)}", flush=True)
print("probing root durations…", flush=True)
root=[(p,ffprobe_dur(p)) for p in root_clips]
print("probing 子夾 durations…", flush=True)

dups=[]
for sp in sub_clips:
    sd=ffprobe_dur(sp)
    matches=[(rp,rd) for rp,rd in root if sd>0 and abs(rd-sd)<=2.0]
    tag = "★疑似重複" if matches else "唯一(非重複)"
    print(f"\n[{tag}] 子夾 {os.path.relpath(sp,G)}  {sd:.0f}s", flush=True)
    for rp,rd in matches:
        print(f"        ↔ root {os.path.basename(rp)}  {rd:.0f}s", flush=True)
    if matches: dups.append((sp,[m[0] for m in matches]))

print(f"\n=== 摘要 ===  子夾 {len(sub_clips)} 支，其中 {len(dups)} 支在 root 有時長重複(★)", flush=True)
