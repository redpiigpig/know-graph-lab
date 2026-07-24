#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
照片庫索引產生器：掃 chenwei / training / hongshi 三個 library，把每個資料夾的
檔案 metadata（name / kind / ext / size / mtime）寫進 scripts/photo_index.json。

Nuxt server 啟動時讀這份 JSON 當作 in-memory index，所以 /photos 頁面不必每次
都遞迴 fs.readdir Drive 鏡像。資料變動後重跑此腳本即可。

掛在 rename_photos.py auto 模式跑完的 tail，平日新增照片要直接 web 看就再
跑一次：
    python scripts/build_photo_index.py

只讀檔，不會動到 Drive 內容。失敗 lib 寫空殼，不阻擋其他 lib。
"""
import json
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PHOTOS_PARENT = Path("G:/我的雲端硬碟/資料/知識圖工作室/照片")

LIBRARIES = {
    "chenwei":  {"folder": "辰瑋相片", "layout": "year-month"},
    "training": {"folder": "訓練相片", "layout": "folders"},
    "hongshi":  {"folder": "弘誓相片", "layout": "folders"},
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif", ".avif", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}

OUTPUT_PATH = Path(__file__).parent / "photo_index.json"

# Drive 檔案 ID（由 harvest_drive_ids.py 從本機 Google Drive for Desktop DB 抽出，無需 SA/API）。
# 給影片用：雲端版靠 driveId 嵌 Drive 播放器（原檔不在 R2）。
DRIVE_IDS_PATH = Path(__file__).parent / "drive_ids.json"
_FULL_ID_MAP = {}


def _load_drive_ids():
    if not DRIVE_IDS_PATH.exists():
        print("  (無 drive_ids.json，跳過 driveId 標註；先跑 harvest_drive_ids.py)")
        return
    data = json.load(open(DRIVE_IDS_PATH, encoding="utf-8"))
    for slug, lib in LIBRARIES.items():
        groot = PHOTOS_PARENT / lib["folder"]
        for rel, did in data.get(slug, {}).items():
            _FULL_ID_MAP[os.path.normcase(str(groot / rel))] = did
    print(f"  載入 {len(_FULL_ID_MAP)} 個 Drive 檔案 ID")


def drive_id_for(full_path):
    return _FULL_ID_MAP.get(os.path.normcase(str(full_path)))


def classify(name: str):
    ext = os.path.splitext(name)[1].lower()
    if ext in IMAGE_EXTS:
        return "image", ext
    if ext in VIDEO_EXTS:
        return "video", ext
    return None


def list_files(dir_path: Path):
    """回傳 [{name,kind,ext,size,mtime}]，依檔名 numeric-aware 排序。"""
    out = []
    try:
        entries = list(os.scandir(dir_path))
    except (OSError, PermissionError) as e:
        print(f"  ! 讀取失敗 {dir_path}: {e}")
        return out
    for e in entries:
        if not e.is_file():
            continue
        if e.name.startswith("."):
            continue
        meta = classify(e.name)
        if not meta:
            continue
        kind, ext = meta
        try:
            st = e.stat()
        except OSError:
            continue
        obj = {
            "name": e.name,
            "kind": kind,
            "ext": ext,
            "size": st.st_size,
            "mtime": st.st_mtime * 1000.0,  # ms, 對齊 fs.stat().mtimeMs
        }
        if kind == "video":
            did = drive_id_for(e.path)
            if did:
                obj["driveId"] = did
        out.append(obj)
    # numeric-aware sort 跟 server 端 localeCompare(undefined,{numeric:true}) 比不完全一樣，
    # 但 rename 後的 YYYY-MM-DD(N).ext 命名空間下純字串排序已等價。
    out.sort(key=lambda x: x["name"])
    return out


def list_subfolders(dir_path: Path):
    """直接子層的資料夾名清單，過濾掉 dotfile。"""
    try:
        return sorted(
            [e.name for e in os.scandir(dir_path)
             if e.is_dir() and not e.name.startswith(".")],
            key=lambda n: n,
        )
    except (OSError, PermissionError) as e:
        print(f"  ! 讀取失敗 {dir_path}: {e}")
        return []


# ===== chenwei: year/month + 截圖 + 下載 + 事件 =====

def build_chenwei(root: Path):
    """
    回傳 {
      totalFiles, topFolders,
      years: {
        "2024": {
          monthCounts: {"01": n, ...},
          screenshots: n, downloads: n,
          events: [{name, count}],
          buckets: { "01": [...], "screenshots": [...], "downloads": [...], "<event>": [...] }
        }
      }
    }
    """
    out = {"totalFiles": 0, "topFolders": 0, "years": {}}
    if not root.exists():
        print(f"  !! 找不到 root: {root}")
        return out

    year_dirs = []
    for e in os.scandir(root):
        if not e.is_dir() or e.name.startswith("."):
            continue
        out["topFolders"] += 1
        # 預期 {YEAR}相片
        if e.name.endswith("相片") and e.name[:-2].isdigit() and len(e.name) == 6:
            year_dirs.append((e.name[:4], Path(e.path)))

    year_dirs.sort(key=lambda t: t[0], reverse=True)

    for year, year_dir in year_dirs:
        print(f"  [chenwei] {year}", flush=True)
        y = {
            "monthCounts": {},
            "monthEvents": {},   # {mm: [{name, count}]} 月份底下的事件子資料夾
            "screenshots": 0,
            "downloads": 0,
            "events": [],
            "buckets": {},
        }
        for sub in os.scandir(year_dir):
            if not sub.is_dir() or sub.name.startswith("."):
                continue
            name = sub.name
            sub_path = Path(sub.path)
            # YYYY.MM 月份（含月內事件子資料夾，遞迴一層）
            if len(name) == 7 and name[:4] == year and name[4] == "." and name[5:].isdigit():
                mm = name[5:]
                files = list_files(sub_path)          # 月份散照（直接子檔）
                y["buckets"][mm] = files
                y["monthCounts"][mm] = len(files)
                out["totalFiles"] += len(files)
                # 月內事件子資料夾：bucket key = "{mm}/{事件名}"
                month_events = []
                for ev in os.scandir(sub_path):
                    if not ev.is_dir() or ev.name.startswith("."):
                        continue
                    ev_files = list_files(Path(ev.path))
                    y["buckets"][f"{mm}/{ev.name}"] = ev_files
                    month_events.append({"name": ev.name, "count": len(ev_files)})
                    out["totalFiles"] += len(ev_files)
                if month_events:
                    month_events.sort(key=lambda e: e["name"])
                    y["monthEvents"][mm] = month_events
                continue
            # 截圖
            if name == f"{year}截圖":
                files = list_files(sub_path)
                y["buckets"]["screenshots"] = files
                y["screenshots"] = len(files)
                out["totalFiles"] += len(files)
                continue
            # 下載
            if name == f"{year}下載":
                files = list_files(sub_path)
                y["buckets"]["downloads"] = files
                y["downloads"] = len(files)
                out["totalFiles"] += len(files)
                continue
            # 事件
            files = list_files(sub_path)
            y["buckets"][name] = files
            y["events"].append({"name": name, "count": len(files)})
            out["totalFiles"] += len(files)
        y["events"].sort(key=lambda e: e["name"])
        out["years"][year] = y
    return out


# ===== training / hongshi: 任意巢狀 folders =====

def build_folder_lib(root: Path):
    """
    回傳 {
      totalFiles, topFolders,
      folders: {
        "<subpath>": {
          folders: [{name, fileCount, subfolderCount}],
          files: [...]
        }
      }
    }
    "" 鍵 = root。subpath 用 forward slash。
    """
    out = {"totalFiles": 0, "topFolders": 0, "folders": {}}
    if not root.exists():
        print(f"  !! 找不到 root: {root}")
        return out

    def walk(dir_path: Path, subpath: str, depth: int):
        entries = []
        try:
            entries = list(os.scandir(dir_path))
        except (OSError, PermissionError) as e:
            print(f"  ! 讀取失敗 {dir_path}: {e}")
            out["folders"][subpath] = {"folders": [], "files": []}
            return

        files = []
        folder_entries = []  # [(name, dir_path)]
        for e in entries:
            if e.name.startswith("."):
                continue
            if e.is_dir():
                folder_entries.append((e.name, Path(e.path)))
            elif e.is_file():
                meta = classify(e.name)
                if not meta:
                    continue
                kind, ext = meta
                try:
                    st = e.stat()
                except OSError:
                    continue
                obj = {
                    "name": e.name,
                    "kind": kind,
                    "ext": ext,
                    "size": st.st_size,
                    "mtime": st.st_mtime * 1000.0,
                }
                if kind == "video":
                    did = drive_id_for(e.path)
                    if did:
                        obj["driveId"] = did
                files.append(obj)

        files.sort(key=lambda x: x["name"])
        folder_entries.sort(key=lambda t: t[0])

        # 算每個 subfolder 的 fileCount / subfolderCount（給 list API 用）
        folders_out = []
        for name, sub_path in folder_entries:
            f_count = 0
            sf_count = 0
            try:
                for f in os.scandir(sub_path):
                    if f.name.startswith("."):
                        continue
                    if f.is_file() and classify(f.name):
                        f_count += 1
                    elif f.is_dir():
                        sf_count += 1
            except (OSError, PermissionError):
                pass
            folders_out.append({
                "name": name,
                "fileCount": f_count,
                "subfolderCount": sf_count,
            })

        out["folders"][subpath] = {"folders": folders_out, "files": files}
        out["totalFiles"] += len(files)
        if depth == 0:
            out["topFolders"] += len(folder_entries)

        for name, sub_path in folder_entries:
            new_sub = name if subpath == "" else f"{subpath}/{name}"
            walk(sub_path, new_sub, depth + 1)

    print(f"  [{root.name}] 開始 walk...", flush=True)
    walk(root, "", 0)
    return out


def main():
    t0 = time.time()
    _load_drive_ids()
    index = {
        "version": 1,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "libraries": {},
    }

    for slug, meta in LIBRARIES.items():
        root = PHOTOS_PARENT / meta["folder"]
        print(f"\n=== {slug} ({root}) ===", flush=True)
        t_start = time.time()
        try:
            if meta["layout"] == "year-month":
                data = build_chenwei(root)
            else:
                data = build_folder_lib(root)
        except Exception as e:
            print(f"  !! {slug} 失敗: {e}")
            data = {"totalFiles": 0, "topFolders": 0}
        elapsed = time.time() - t_start
        print(f"  {slug}: totalFiles={data['totalFiles']}, topFolders={data['topFolders']}, "
              f"耗時 {elapsed:.1f}s", flush=True)
        data["layout"] = meta["layout"]
        index["libraries"][slug] = data

    # 防呆：若三個 library 全 0 檔（多半是 G: 暫時未掛載 / Drive 斷線），
    # 絕不可用這份空殼覆寫既有 index（曾因此導致 chenwei 補檔誤判全缺而過量複製 86GB）。
    grand = sum(d.get("totalFiles", 0) for d in index["libraries"].values())
    if grand == 0:
        print("!! 所有 library 皆 0 檔 — 疑 G: 未掛載/Drive 斷線，拒絕覆寫既有 index，直接離開",
              file=sys.stderr)
        sys.exit(2)

    # Atomic write: 先寫 .tmp 再 rename
    tmp_path = OUTPUT_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    tmp_path.replace(OUTPUT_PATH)

    total_elapsed = time.time() - t0
    size_mb = OUTPUT_PATH.stat().st_size / 1024 / 1024
    print(f"\n=== 寫入 {OUTPUT_PATH} ({size_mb:.2f} MB), 總耗時 {total_elapsed:.1f}s ===")


if __name__ == "__main__":
    main()
