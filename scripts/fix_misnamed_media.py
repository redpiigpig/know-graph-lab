# -*- coding: utf-8 -*-
"""掃 chenwei 相簿裡副檔名是 .jpg/.jpeg/.png 但實際是『影片容器(ISO-BMFF ftyp)』或 HEIC 的誤命名檔。
- ftyp 品牌 qt/mp4/isom/M4V/avc1… → 影片 → 改副檔名成 .MOV（保留原名）
- ftyp 品牌 heic/heix/mif1/hevc… → HEIC 影像 → 只報告（交給 convert_heic_to_jpg）
- FFD8FF → 正常 JPEG（略過）；其他 → 未知/壞檔（只報告）
每個 rename 寫進 rollback log。用法：python fix_misnamed_media.py [apply]
"""
import os, sys, json, time
ROOT = r"G:\我的雲端硬碟\資料\儲存資料夾\辰瑋相片"
LOG = r"C:\tmp\misnamed_media_rename_log.jsonl"
APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
IMG_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_BRANDS = {b"qt  ", b"mp4 ", b"isom", b"mp42", b"M4V ", b"avc1", b"iso2", b"3gp"}
HEIC_BRANDS = {b"heic", b"heix", b"hevc", b"mif1", b"msf1", b"heim", b"hevx"}

def sniff(p):
    try:
        with open(p, "rb") as f:
            b = f.read(12)
    except Exception as e:
        return ("read_err", str(e))
    if len(b) < 12:
        return ("tiny", "")
    if b[0:3] == b"\xff\xd8\xff":
        return ("jpeg_ok", "")
    if b[0:8] == b"\x89PNG\r\n\x1a\n":
        return ("png_ok", "")
    if b[4:8] == b"ftyp":
        brand = b[8:12]
        if brand in VIDEO_BRANDS or brand[:3] == b"3gp":
            return ("video", brand.decode("latin1").strip())
        if brand in HEIC_BRANDS:
            return ("heic", brand.decode("latin1").strip())
        return ("ftyp_other", brand.decode("latin1").strip())
    return ("unknown", b[:4].hex())

def safe_rename_target(p):
    base = os.path.splitext(p)[0] + ".MOV"
    t, n = base, 2
    while os.path.exists(t):
        t = os.path.splitext(p)[0] + f"__v{n}.MOV"; n += 1
    return t

vids = heics = corrupt = 0
renamed = []
for a, _, fs in os.walk(ROOT):
    for f in fs:
        ext = os.path.splitext(f)[1].lower()
        if ext not in IMG_EXT:
            continue
        p = os.path.join(a, f)
        kind, info = sniff(p)
        if kind == "video":
            vids += 1
            rel = os.path.relpath(p, ROOT)
            if APPLY:
                dst = safe_rename_target(p)
                try:
                    os.rename(p, dst)
                    rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "from": p, "to": dst, "brand": info}
                    with open(LOG, "a", encoding="utf-8") as lf:
                        lf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    renamed.append(rel)
                    print(f"RENAME  {rel}  (ftyp {info}) -> .MOV", flush=True)
                except Exception as e:
                    print(f"FAIL    {rel}: {e}", flush=True)
            else:
                print(f"[dry] video .{ext[1:]}  {rel}  (ftyp {info})", flush=True)
        elif kind == "heic":
            heics += 1
            print(f"[heic]  {os.path.relpath(p, ROOT)}  (ftyp {info}) -> 交給 convert_heic_to_jpg", flush=True)
        elif kind in ("unknown", "tiny", "read_err", "ftyp_other"):
            corrupt += 1
            print(f"[{kind}] {os.path.relpath(p, ROOT)}  {info}", flush=True)

print(f"\n=== {'APPLIED' if APPLY else 'DRY-RUN'} === 影片誤命名={vids} HEIC誤命名={heics} 未知/壞={corrupt}", flush=True)
if APPLY:
    print(f"已改 {len(renamed)} 個 .jpg→.MOV，rollback log: {LOG}", flush=True)
