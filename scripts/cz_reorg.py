# -*- coding: utf-8 -*-
"""城中週報 實體資料夾整理 — 分流 周報/講章/講道/錄音、清垃圾、解壓舊年 zip。
保留所有原始檔（只刪 Word 暫存/鎖檔/系統垃圾）。每步寫入 manifest，可回溯。
用法： python scripts/cz_reorg.py            (dry-run，只印計畫)
       python scripts/cz_reorg.py --apply    (實際執行)
"""
import sys, os, re, json, shutil, zipfile

ROOT = os.path.abspath(r"G:/我的雲端硬碟/資料/知識圖工作室/研究資料/城中教會週報")
APPLY = "--apply" in sys.argv
manifest = []

def log(action, src, dst=""):
    manifest.append({"action": action, "src": src, "dst": dst})
    print(f"  {action:8} {os.path.relpath(src, ROOT)}" + (f"  ->  {os.path.relpath(dst, ROOT)}" if dst else ""))

def do_move(src, dst):
    if not APPLY:
        log("MOVE", src, dst); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        base, ext = os.path.splitext(dst); i = 2
        while os.path.exists(f"{base}__{i}{ext}"):
            i += 1
        dst = f"{base}__{i}{ext}"
    shutil.move(src, dst)
    log("MOVE", src, dst)

def do_delete(path):
    log("DELETE", path)
    if APPLY:
        try: os.remove(path)
        except IsADirectoryError: shutil.rmtree(path)

def do_mkdir(path):
    if APPLY:
        os.makedirs(path, exist_ok=True)

JUNK = re.compile(r"(^~\$|\.tmp$|^~WRL|^desktop\.ini$|^thumbs\.db$|\.exe$|^WS_FTP\.LOG$)", re.I)

def clean_junk():
    print("\n## 1. 清除暫存/鎖檔/系統垃圾")
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        for f in fn:
            if JUNK.search(f):
                do_delete(os.path.join(dp, f)); n += 1
    print(f"   -> {n} 個垃圾檔")

def extract_zips():
    print("\n## 2. 解壓舊年 zip（2003/2010）到對應年資料夾，原 zip 移到 _原始壓縮檔/")
    zdst_keep = os.path.join(ROOT, "_原始壓縮檔")
    for dp, dn, fn in os.walk(ROOT):
        if "_原始壓縮檔" in dp:
            continue
        for f in fn:
            if f.lower().endswith(".zip"):
                zp = os.path.join(dp, f)
                outdir = os.path.join(dp, "_解壓_" + os.path.splitext(f)[0])
                print(f"   ZIP {os.path.relpath(zp, ROOT)} -> {os.path.relpath(outdir, ROOT)}")
                if APPLY:
                    os.makedirs(outdir, exist_ok=True)
                    try:
                        with zipfile.ZipFile(zp) as z:
                            for info in z.infolist():
                                # legacy big5 names
                                try:
                                    name = info.filename.encode("cp437").decode("big5")
                                except Exception:
                                    name = info.filename
                                if name.endswith("/"):
                                    continue
                                if JUNK.search(os.path.basename(name)) or "Folder Settings" in name:
                                    continue
                                target = os.path.join(outdir, name.replace("\\", "/"))
                                os.makedirs(os.path.dirname(target), exist_ok=True)
                                with z.open(info) as s, open(target, "wb") as o:
                                    o.write(s.read())
                    except Exception as e:
                        print("     ! zip err", e)
                do_move(zp, os.path.join(zdst_keep, f))

def consolidate():
    print("\n## 3. 分流：周報 / 講章 / 講道 / 錄音")
    # 3a 周報年資料夾 -> 周報/<year>
    zhoubao = os.path.join(ROOT, "周報")
    for d in sorted(os.listdir(ROOT)):
        full = os.path.join(ROOT, d)
        if not os.path.isdir(full):
            continue
        m = re.match(r"^(20\d{2})周報$", d)
        if m:
            do_move(full, os.path.join(zhoubao, m.group(1)))
        elif d == "2007週報午堂":
            do_move(full, os.path.join(zhoubao, "2007午堂"))
    # 3a' loose 2026 bulletins
    for f in sorted(os.listdir(ROOT)):
        if re.match(r"^26-\d{2}-\d{2}.*\.docx?$", f):
            do_move(os.path.join(ROOT, f), os.path.join(zhoubao, "2026", f))
    # 3b 講章： 2005講章 / 2006講章 併入 講章/
    jiangzhang = os.path.join(ROOT, "講章")
    for d in ("2005講章", "2006講章"):
        full = os.path.join(ROOT, d)
        if os.path.isdir(full):
            do_move(full, os.path.join(jiangzhang, d.replace("講章", "") + "講章"))
    # 3c 錄音： 主日錄音 + 崇拜錄音 -> 錄音/
    luyin = os.path.join(ROOT, "錄音")
    for d, sub in (("主日錄音", "主日"), ("崇拜錄音", "崇拜")):
        full = os.path.join(ROOT, d)
        if os.path.isdir(full):
            do_move(full, os.path.join(luyin, sub))

def main():
    print(f"=== 城中週報 reorg  ({'APPLY' if APPLY else 'DRY-RUN'}) ===\nROOT={ROOT}")
    clean_junk()
    extract_zips()
    consolidate()
    mpath = r"c:/tmp/cz_bulletins/reorg_manifest.json"
    os.makedirs(os.path.dirname(mpath), exist_ok=True)
    json.dump(manifest, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n=== {len(manifest)} 個動作；manifest -> {mpath} ===")
    if not APPLY:
        print("（dry-run，未實際變更。加 --apply 執行）")

if __name__ == "__main__":
    main()
