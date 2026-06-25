# -*- coding: utf-8 -*-
"""把本機 C:\\Users\\張辰瑋的資料\\辰瑋相片 缺漏的檔補到 G: 辰瑋相片。
比對基準＝photo_index.json 的 chenwei size 多重集合（jpg 只更名不改 bytes，size 對不上＝G 真的沒有）。
- 一般 img/vid：size 不在 G → 依「相同相對路徑」copy 到 G（2021-2024 已在 {Y}.MM 月夾、2014-2020 事件夾原樣保留）
- .cr2 RAW：全部 copy（G 完全沒有）
- HEIC：轉成暫存 JPG(q92，同 convert_heic_to_jpg)→ 拿 JPG size 跟 G 比對；已在 G 跳過，否則把 JPG 直接落到 G 相對路徑(.jpg)
之後再跑 classify → rename → index → R2。ledger 可續跑。
用 C:\\Users\\user\\AppData\\Local\\Python\\bin\\python.exe
"""
import os, json, shutil, time
from collections import Counter
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()

C = r"C:\Users\張辰瑋的資料\辰瑋相片"
GROOT = r"G:\我的雲端硬碟\資料\儲存資料夾\辰瑋相片"
INDEX = r"C:\Users\user\Desktop\know-graph-lab\scripts\photo_index.json"
LED = r"C:\tmp\chenwei_fill_ledger.json"
LOGP = r"C:\tmp\chenwei_fill.log"
WORK = r"c:\tmp\cw_heic_work"
IMG = {'.jpg','.jpeg','.png','.gif','.webp','.bmp','.tif','.tiff'}
HEIC = {'.heic','.heif'}
VID = {'.mp4','.mov','.m4v','.avi','.mkv','.wmv','.mts','.m2ts','.3gp','.webm','.mpg','.mpeg'}
RAW = {'.cr2','.cr3','.nef','.arw','.dng','.raf','.orf','.rw2'}
QUALITY = 92
os.makedirs(WORK, exist_ok=True)
logf = open(LOGP, "a", encoding="utf-8")
def L(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True); logf.write(line+"\n"); logf.flush()
def load_led():
    try: return json.load(open(LED, encoding="utf-8"))
    except: return {}
def save_led(d):
    json.dump(d, open(LED+".tmp","w",encoding="utf-8"), ensure_ascii=False); os.replace(LED+".tmp", LED)

def gsizes():
    idx = json.load(open(INDEX, encoding="utf-8"))
    cw = idx["libraries"]["chenwei"]
    c = Counter()
    for y, yd in cw.get("years", {}).items():
        for b, arr in yd.get("buckets", {}).items():
            for f in arr:
                e = f.get("ext","").lower()
                if e in IMG or e in VID: c[f.get("size",0)] += 1
    return c

def gdst(relpath):
    return os.path.join(GROOT, relpath)
def safe(dst):
    b,e = os.path.splitext(dst); n=2; t=dst
    while os.path.exists(t): t=f"{b}__c{n}{e}"; n+=1
    return t

def main():
    L("=== chenwei fill START ===")
    gmul = gsizes()
    L(f"G chenwei size-multiset distinct={len(gmul)}")
    led = load_led()
    copied=raw=heic_new=heic_skip=skip=fail=0; bytes_c=0
    for root,_,files in os.walk(C):
        for fn in files:
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, C)
            e = os.path.splitext(fn)[1].lower()
            if led.get(src,{}).get("status") in ("done","skip_exist"):
                continue
            try:
                if e in IMG or e in VID:
                    s = os.path.getsize(src)
                    if gmul.get(s,0) > 0:
                        gmul[s]-=1; led[src]={"status":"skip_exist"}; skip+=1; continue
                    dst = safe(gdst(rel)); os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst); copied+=1; bytes_c+=s; led[src]={"status":"done","mode":"copy"}
                elif e in RAW:
                    dst = safe(gdst(rel)); os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst); raw+=1; bytes_c+=os.path.getsize(dst); led[src]={"status":"done","mode":"raw"}
                elif e in HEIC:
                    # 轉暫存 jpg → size 比對
                    tmp = os.path.join(WORK, "t.jpg")
                    im = Image.open(src); ex = im.info.get("exif"); rgb = im.convert("RGB")
                    if ex: rgb.save(tmp,"JPEG",quality=QUALITY,exif=ex)
                    else: rgb.save(tmp,"JPEG",quality=QUALITY)
                    im.close()
                    ts = os.path.getsize(tmp)
                    if gmul.get(ts,0) > 0:
                        gmul[ts]-=1; led[src]={"status":"skip_exist","mode":"heic_dup"}; heic_skip+=1
                        os.remove(tmp); continue
                    dst = safe(gdst(os.path.splitext(rel)[0] + ".jpg")); os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.move(tmp, dst); heic_new+=1; bytes_c+=ts; led[src]={"status":"done","mode":"heic_jpg"}
                else:
                    continue
                save_led(led)
            except Exception as ex:
                L(f"FAIL {rel}: {ex}"); led[src]={"status":"fail"}; save_led(led); fail+=1
        if (copied+raw+heic_new) and (copied+raw+heic_new) % 200 == 0:
            L(f"...progress copied={copied} raw={raw} heic_new={heic_new} heic_skip={heic_skip} skip={skip} {bytes_c/1073741824:.1f}GB")
    L(f"=== DONE === copied_imgvid={copied} cr2={raw} heic_new_jpg={heic_new} heic_skip={heic_skip} skip_exist={skip} fail={fail} total={bytes_c/1073741824:.1f}GB")
    logf.close()

if __name__ == "__main__":
    main()
