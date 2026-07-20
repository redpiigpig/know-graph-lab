# -*- coding: utf-8 -*-
"""把 D:\資料\fitcasting 缺的影片 HEVC 轉碼後補上 G: fitcasting（不先上傳 90GB 原檔）。
- 對 G 既有的 18 支做時長比對，已存在的略過
- <20MB 或已是低位元率 hevc → 直接複製原檔（不值得 GPU）
- 其餘 nvenc 轉碼，驗時長/解析度/變小，不夠小則改複製原檔（仍要補齊）
- ledger 可續跑；temp 一次一支放 c:/tmp/fc_work
"""
import os, json, subprocess, time, shutil
D = r"D:\資料\fitcasting"
G = r"G:\我的雲端硬碟\資料\知識圖工作室\照片\訓練相片\fitcasting"
WORK = r"c:\tmp\fc_work"
LED = r"c:\tmp\fitcasting_ledger.json"
LOGP = r"c:\tmp\fitcasting.log"
VID = {".mp4",".mov",".m4v",".webm",".mkv",".avi",".wmv",".mts",".m2ts",".3gp",".mpg",".mpeg"}
KEEP_CONT = {".mp4",".mov"}
CQ="26"; PRESET="p6"; SMALL_BYTES=20*1024*1024; HEVC_LOWBR=12e6; RATIO=0.85; DURTOL=1.0
os.makedirs(WORK, exist_ok=True); os.makedirs(G, exist_ok=True)
logf=open(LOGP,"a",encoding="utf-8")
def L(m):
    line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True); logf.write(line+"\n"); logf.flush()
def load_led():
    try: return json.load(open(LED,encoding="utf-8"))
    except: return {}
def save_led(d):
    json.dump(d,open(LED+".tmp","w",encoding="utf-8"),ensure_ascii=False); os.replace(LED+".tmp",LED)
def ffprobe(p):
    o=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height","-of","json",p],capture_output=True,text=True,encoding="utf-8",errors="replace")
    d=json.loads(o.stdout or "{}"); dur=float(d.get("format",{}).get("duration") or 0)
    vc=ac=None; w=h=0
    for s in d.get("streams",[]):
        if s.get("codec_type")=="video" and vc is None: vc=s.get("codec_name"); w=s.get("width") or 0; h=s.get("height") or 0
        elif s.get("codec_type")=="audio" and ac is None: ac=s.get("codec_name")
    return dur,vc,ac,w,h
def walk(root):
    r=[]
    for a,_,fs in os.walk(root):
        for f in fs:
            if os.path.splitext(f)[1].lower() in VID: r.append(os.path.join(a,f))
    return r
def safe_dst(name):
    b,e=os.path.splitext(name); t=os.path.join(G,name); n=2
    while os.path.exists(t): t=os.path.join(G,f"{b}__d{n}{e}"); n+=1
    return t

L("=== fitcasting transcode-fill START ===")
gvids=walk(G)
gdurs=[]
for f in gvids:
    try: gdurs.append(ffprobe(f)[0])
    except: pass
L(f"G existing videos={len(gvids)} durations={len(gdurs)}")
dvids=sorted(walk(D))
L(f"D fitcasting videos={len(dvids)}")
led=load_led()
done=skip=copied=enc=fail=0; saved=0
for i,src in enumerate(dvids,1):
    if led.get(src,{}).get("status") in ("done","skipped_exist"): 
        done+=1; continue
    if not os.path.exists(src):
        led[src]={"status":"missing"}; save_led(led); continue
    try: dur,vc,ac,w,h=ffprobe(src)
    except Exception as e:
        L(f"[{i}] PROBE-FAIL {os.path.basename(src)[:40]}: {e}"); led[src]={"status":"probe_fail"}; save_led(led); fail+=1; continue
    # already on G by duration?
    hit=False
    for k,gd in enumerate(gdurs):
        if dur>0 and abs(gd-dur)<=2.0: gdurs.pop(k); hit=True; break
    if hit:
        led[src]={"status":"skipped_exist"}; save_led(led); skip+=1; continue
    size=os.path.getsize(src)
    br=size*8/dur if dur else 0
    name=os.path.basename(src)
    # too small or already efficient hevc -> copy raw
    if size<SMALL_BYTES or (vc=="hevc" and br<HEVC_LOWBR):
        dst=safe_dst(name)
        try:
            shutil.copy2(src,dst); copied+=1; led[src]={"status":"done","mode":"copy_raw"}; save_led(led)
            L(f"[{i}/{len(dvids)}] COPY-RAW {name[:40]} {size/1e6:.0f}MB")
        except Exception as e:
            L(f"[{i}] COPY-FAIL {name[:40]}: {e}"); led[src]={"status":"copy_fail"}; save_led(led); fail+=1
        continue
    # transcode
    ext=os.path.splitext(name)[1].lower(); outext=ext if ext in KEEP_CONT else ".mp4"
    work=os.path.join(WORK,f"w{i}{outext}")
    if os.path.exists(work): os.remove(work)
    aargs=["-c:a","copy"] if ac in("aac","mp3","ac3","eac3","opus") else ["-c:a","aac","-b:a","192k"]
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-i",src,"-map","0:v:0","-map","0:a?","-map_metadata","0",
         "-c:v","hevc_nvenc","-preset",PRESET,"-rc","vbr","-cq",CQ,"-b:v","0","-pix_fmt","yuv420p","-tag:v","hvc1",
         *aargs,"-movflags","+faststart",work]
    t0=time.time(); r=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace"); dt=time.time()-t0
    ok_enc = r.returncode==0 and os.path.exists(work)
    use_raw=False
    if ok_enc:
        try:
            d1,v1,a1,w1,h1=ffprobe(work); ns=os.path.getsize(work)
            ok=abs(d1-dur)<=max(DURTOL,dur*0.01) and sorted((w1,h1))==sorted((w,h)) and ns<=size*RATIO
            if not ok: use_raw=True; L(f"[{i}] reject-or-notsmaller -> copy raw {name[:35]}")
        except: use_raw=True
    else:
        use_raw=True; L(f"[{i}] ENCODE-FAIL -> copy raw {name[:35]}: {(r.stderr or '')[:120]}")
    outname=os.path.splitext(name)[0]+outext if not use_raw else name
    dst=safe_dst(outname)
    try:
        if use_raw:
            shutil.copy2(src,dst); led[src]={"status":"done","mode":"copy_raw_fallback"}
        else:
            shutil.copyfile(work,dst); shutil.copystat(src,dst)
            ns=os.path.getsize(dst); saved+=size-ns; enc+=1
            led[src]={"status":"done","mode":"hevc","orig":size,"new":ns}
            L(f"[{i}/{len(dvids)}] OK {name[:35]} {size/1e6:.0f}->{ns/1e6:.0f}MB {dt:.0f}s 累省{saved/1e9:.1f}GB")
        save_led(led)
    except Exception as e:
        L(f"[{i}] WRITE-FAIL {name[:35]}: {e}"); led[src]={"status":"write_fail"}; save_led(led); fail+=1
    finally:
        if os.path.exists(work):
            try: os.remove(work)
            except: pass
L(f"=== DONE === skip_exist={skip} hevc={enc} copy_raw={copied} fail={fail} 省={saved/1e9:.1f}GB")
logf.close()
