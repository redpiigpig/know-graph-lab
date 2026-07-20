# -*- coding: utf-8 -*-
"""從本機 Google Drive for Desktop 的 metadata DB 抽出三相簿每個檔案的 Drive 檔案 ID。
無需 Service Account / Drive API / 共用資料夾 —— ID 從本機 DriveFS 資料庫直接讀。
輸出 scripts/drive_ids.json：{album: {relpath(forward-slash): drive_id}}。
用法：python harvest_drive_ids.py [--verify]
"""
import os, sys, json, glob, shutil, sqlite3, tempfile

REPO = r"C:\Users\user\Desktop\know-graph-lab"
OUT = os.path.join(REPO, "scripts", "drive_ids.json")
ALBUM_ROOTS = {  # album slug -> 相簿資料夾 local-title
    "chenwei": "辰瑋相片",
    "training": "訓練相片",
    "hongshi": "弘誓相片",
}
G_ROOTS = {
    "chenwei": r"G:\我的雲端硬碟\資料\知識圖工作室\照片\辰瑋相片",
    "training": r"G:\我的雲端硬碟\資料\知識圖工作室\照片\訓練相片",
    "hongshi": r"G:\我的雲端硬碟\資料\知識圖工作室\照片\弘誓相片",
}

def find_db():
    base = os.path.expandvars(r"%LOCALAPPDATA%\Google\DriveFS")
    cands = glob.glob(os.path.join(base, "*", "metadata_sqlite_db"))
    if not cands:
        sys.exit("找不到 DriveFS metadata_sqlite_db（Google Drive 桌面版沒裝？）")
    return max(cands, key=os.path.getmtime)

def load_snapshot():
    src = find_db()
    tmp = tempfile.mkdtemp(prefix="drivefs_")
    dst = os.path.join(tmp, "db")
    shutil.copy2(src, dst)
    wal = src + "-wal"
    if os.path.exists(wal):
        shutil.copy2(wal, dst + "-wal")
    con = sqlite3.connect(dst)
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    return con

def main():
    verify = "--verify" in sys.argv
    con = load_snapshot(); c = con.cursor()
    # 載入字典
    title = {}
    for sid, v in c.execute("SELECT item_stable_id, value FROM item_properties WHERE key='local-title'"):
        title[sid] = v
    parent = {}
    for sid, pid in c.execute("SELECT item_stable_id, parent_stable_id FROM stable_parents"):
        parent.setdefault(sid, pid)  # 取第一個父（極少數多父）
    drive_id, is_folder = {}, {}
    for sid, did, isf in c.execute("SELECT stable_id, id, is_folder FROM items WHERE trashed=0"):
        drive_id[sid] = did; is_folder[sid] = isf
    # 三相簿 root stable_id
    roots = {}
    for slug, nm in ALBUM_ROOTS.items():
        r = c.execute("""SELECT i.stable_id FROM items i JOIN item_properties p ON p.item_stable_id=i.stable_id
                         WHERE p.key='local-title' AND p.value=? AND i.is_folder=1 AND i.trashed=0""", (nm,)).fetchone()
        if not r: sys.exit(f"DriveFS 找不到相簿資料夾「{nm}」")
        roots[slug] = r[0]
    root2slug = {v: k for k, v in roots.items()}

    # 每個 item 往上走到相簿 root，建 relpath；資料夾路徑做快取
    relcache = {}
    def relpath_and_album(sid):
        # 回 (album_slug, [segments from album root down to sid]) 或 None
        if sid in root2slug:
            return root2slug[sid], []
        if sid in relcache:
            return relcache[sid]
        pid = parent.get(sid)
        if pid is None:
            relcache[sid] = None; return None
        up = relpath_and_album(pid)
        if up is None:
            relcache[sid] = None; return None
        album, segs = up
        res = (album, segs + [title.get(sid, str(sid))])
        relcache[sid] = res
        return res

    out = {"chenwei": {}, "training": {}, "hongshi": {}}
    files = 0
    for sid, isf in is_folder.items():
        if isf: continue
        r = relpath_and_album(sid)
        if r is None: continue
        album, segs = r
        if not segs: continue
        rel = "/".join(segs)
        out[album][rel] = drive_id[sid]
        files += 1

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"=== 收 {files} 檔 Drive ID ===")
    for a in out: print(f"  {a}: {len(out[a])} 檔")
    print(f"寫到 {OUT}")

    if verify:
        print("\n=== 驗證：隨機抽幾筆比對 G: 實體檔存在 ===")
        import itertools
        for album in out:
            groot = G_ROOTS[album]
            sample = list(itertools.islice(out[album].items(), 0, 500, 120))
            for rel, did in sample[:4]:
                full = os.path.join(groot, rel.replace("/", "\\"))
                ok = os.path.exists(full)
                print(f"  [{'OK' if ok else '缺'}] {album}/{rel[:50]}  id={did[:14]}  {'✓在G:' if ok else '✗G:沒有'}")

if __name__ == "__main__":
    main()
