#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新命名辰瑋相片每個資料夾內的檔案，格式：
    {S|D|}YYYY-MM-DD(N).{ext}

- S 前綴：`{YEAR}截圖/` 內
- D 前綴：`{YEAR}下載/` 內
- 無前綴：`{YEAR}.MM/` 月份夾、`{YEAR}未分類/`、事件夾

日期來源優先順序：EXIF DateTimeOriginal → 檔名 YYYYMMDD → mtime
同一天的多張：依完整時間（EXIF/檔名時/mtime）排序，由早至晚 (1)(2)(3)…

掃描範圍：`{YEAR}相片/<即時子資料夾>/` 一層。年根散檔不動（先跑
classify_photos.py 歸位）。子子夾不掃。

Idempotent：已符合格式且編號正確的檔不會再 rename。

兩階段 rename（避免衝突）：先 src → `__rename_tmp_XXXXX.ext`，再 tmp → 目標名。
若 execute 中途崩潰，會留下 tmp 檔；下一次 execute 啟動時偵測並 abort。

Usage:
    python scripts/rename_photos.py plan [LIB]     # dry-run, 寫出 photo_rename_report_{lib}.json
    python scripts/rename_photos.py execute [LIB]  # 依 report 實際 rename
    python scripts/rename_photos.py auto LIB...    # 對每個 LIB 連跑 plan + execute

LIB ∈ {chenwei, training, hongshi}，省略時預設 chenwei。
"""
import json
import re
import sys
import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from PIL import Image, ExifTags

# 嘗試啟用 HEIC EXIF 讀取（可選）
try:
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
    HEIF_OK = True
except Exception:
    HEIF_OK = False

PHOTOS_PARENT = Path("G:/我的雲端硬碟/資料/儲存資料夾")

# Library → 對應子資料夾
LIBRARIES = {
    "chenwei": "辰瑋相片",
    "training": "訓練相片",
    "hongshi": "弘誓相片",
}
DEFAULT_LIB = "chenwei"

# 全域，由 main() 設定
PHOTOS_ROOT = PHOTOS_PARENT / LIBRARIES[DEFAULT_LIB]
REPORT_PATH = Path(__file__).parent / f"photo_rename_report_{DEFAULT_LIB}.json"
LOG_PATH = Path(__file__).parent / "photo_rename_log.jsonl"

def set_library(slug: str):
    global PHOTOS_ROOT, REPORT_PATH
    if slug not in LIBRARIES:
        raise SystemExit(f"未知 library：{slug}（可用：{list(LIBRARIES)}）")
    PHOTOS_ROOT = PHOTOS_PARENT / LIBRARIES[slug]
    REPORT_PATH = Path(__file__).parent / f"photo_rename_report_{slug}.json"

IMG_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif", ".avif", ".bmp",
    ".mp4", ".mov", ".m4v", ".webm", ".mkv",
}

TMP_PREFIX = "__rename_tmp_"

MIN_YEAR, MAX_YEAR = 2000, 2026


# ----- 日期 helpers -----

def _parse_exif_datetime(s):
    if not s:
        return None
    if isinstance(s, bytes):
        try:
            s = s.decode("ascii", errors="ignore")
        except Exception:
            return None
    s = s.strip().strip("\x00")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d", "%Y-%m-%d"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            if MIN_YEAR <= dt.year <= MAX_YEAR:
                return dt
        except Exception:
            pass
    return None


_FN_DATE_RE = re.compile(
    r"(20[0-2]\d)[-_.\s]?(0[1-9]|1[0-2])[-_.\s]?(0[1-9]|[12]\d|3[01])"
    r"(?:[-_\s]?([01]\d|2[0-3])[-_:.\s]?([0-5]\d)[-_:.\s]?([0-5]\d)?)?"
)


def _parse_filename_datetime(name: str):
    m = _FN_DATE_RE.search(name)
    if not m:
        return None
    try:
        Y, M, D = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (MIN_YEAR <= Y <= MAX_YEAR):
            return None
        hh = int(m.group(4) or 0)
        mm = int(m.group(5) or 0)
        ss = int(m.group(6) or 0)
        return datetime.datetime(Y, M, D, hh, mm, ss)
    except Exception:
        return None


def file_datetime(path: Path):
    """Returns (datetime, source) where source ∈ {'exif','filename','mtime'}."""
    # 1. EXIF
    try:
        with Image.open(path) as img:
            raw = img._getexif() if hasattr(img, "_getexif") else None
            named = {ExifTags.TAGS.get(k, k): v for k, v in (raw or {}).items()}
            dt = (_parse_exif_datetime(named.get("DateTimeOriginal"))
                  or _parse_exif_datetime(named.get("DateTime")))
            if dt:
                return dt, "exif"
    except Exception:
        pass

    # 2. filename
    dt = _parse_filename_datetime(path.name)
    if dt:
        return dt, "filename"

    # 3. mtime
    try:
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        return mtime, "mtime"
    except Exception:
        return datetime.datetime(MIN_YEAR, 1, 1), "fallback"


# ----- 命名 helpers -----

def folder_prefix(folder_name: str, year: str) -> str:
    if folder_name == f"{year}截圖":
        return "S"
    if folder_name == f"{year}下載":
        return "D"
    return ""


def normalize_ext(ext: str) -> str:
    ext = ext.lower()
    if ext == ".jpeg":
        return ".jpg"
    return ext


# ----- 計畫 -----

def collect_folder_plan(folder: Path, prefix: str) -> list[dict]:
    """Plan renames for a single folder. Returns list of plan entries."""
    files = []
    for f in folder.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in IMG_EXTS:
            continue
        if f.name.startswith(TMP_PREFIX):
            continue  # 上次 execute 沒跑完的中繼檔，另外處理
        dt, src_kind = file_datetime(f)
        files.append({
            "path": f, "dt": dt, "dt_source": src_kind,
            "ext": normalize_ext(f.suffix),
        })

    # 排序：完整時間 → 原檔名（穩定 tiebreaker）
    files.sort(key=lambda x: (x["dt"], x["path"].name))

    plan = []
    counters: dict[str, int] = {}
    for f in files:
        dkey = f["dt"].strftime("%Y-%m-%d")
        counters[dkey] = counters.get(dkey, 0) + 1
        n = counters[dkey]
        new_name = f"{prefix}{dkey}({n}){f['ext']}"
        plan.append({
            "src": str(f["path"]).replace("\\", "/"),
            "target_name": new_name,
            "skip": f["path"].name == new_name,
            "dt": f["dt"].isoformat(),
            "dt_source": f["dt_source"],
        })
    return plan


def collect_plan():
    all_plan = []
    folders_scanned = 0
    leftover_tmp = []
    for year_dir in sorted(PHOTOS_ROOT.iterdir()):
        if not year_dir.is_dir():
            continue
        if not year_dir.name.endswith("相片"):
            continue
        year = year_dir.name.replace("相片", "")

        for sub in sorted(year_dir.iterdir()):
            if not sub.is_dir():
                continue
            # 偵測上次崩潰的中繼檔
            for f in sub.iterdir():
                if f.is_file() and f.name.startswith(TMP_PREFIX):
                    leftover_tmp.append(str(f).replace("\\", "/"))
            prefix = folder_prefix(sub.name, year)
            folder_plan = collect_folder_plan(sub, prefix)
            for item in folder_plan:
                item["folder"] = str(sub).replace("\\", "/")
                item["folder_name"] = sub.name
                item["year"] = year
                item["prefix"] = prefix
            all_plan.extend(folder_plan)
            folders_scanned += 1

    return all_plan, folders_scanned, leftover_tmp


def summarize(plan):
    will_rename = [x for x in plan if not x["skip"]]
    by_source: dict[str, int] = {}
    by_prefix: dict[str, int] = {}
    for x in plan:
        by_source[x["dt_source"]] = by_source.get(x["dt_source"], 0) + 1
        if not x["skip"]:
            p = x["prefix"] or "(none)"
            by_prefix[p] = by_prefix.get(p, 0) + 1
    return {
        "total": len(plan),
        "will_rename": len(will_rename),
        "already_ok": len(plan) - len(will_rename),
        "by_dt_source": by_source,
        "rename_by_prefix": by_prefix,
    }


# ----- 指令 -----

def cmd_plan():
    print(f"HEIC EXIF support: {'YES' if HEIF_OK else 'NO (pillow-heif not installed)'}")
    print("掃描中…")
    plan, n_folders, leftover_tmp = collect_plan()
    summary = summarize(plan)
    REPORT_PATH.write_text(
        json.dumps({
            "plan": plan,
            "summary": summary,
            "folders_scanned": n_folders,
            "leftover_tmp_files": leftover_tmp,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n資料夾掃描：{n_folders}")
    print(f"檔案總數：{summary['total']}")
    print(f"需要 rename：{summary['will_rename']}")
    print(f"已符合格式：{summary['already_ok']}")
    print(f"日期來源分布：{summary['by_dt_source']}")
    print(f"Rename by prefix：{summary['rename_by_prefix']}")
    if leftover_tmp:
        print(f"\n⚠ 發現 {len(leftover_tmp)} 個上次崩潰的 __rename_tmp_* 中繼檔，"
              f"執行 execute 前請手動處理（前 5 個）:")
        for t in leftover_tmp[:5]:
            print(f"   {t}")
    print(f"\nReport: {REPORT_PATH}")

    samples = [x for x in plan if not x["skip"]][:10]
    if samples:
        print("\n--- Sample renames (first 10) ---")
        for s in samples:
            src_name = Path(s["src"]).name
            print(f"  [{s['dt_source']:8}] {s['folder_name']}/  "
                  f"{src_name}  →  {s['target_name']}")


def cmd_execute():
    if not REPORT_PATH.exists():
        print(f"先跑 plan：{REPORT_PATH} 不存在")
        sys.exit(1)
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    leftover = data.get("leftover_tmp_files", [])
    if leftover:
        print(f"⚠ 偵測到 {len(leftover)} 個 __rename_tmp_* 中繼檔，先處理後再跑 execute")
        for t in leftover[:10]:
            print(f"   {t}")
        sys.exit(2)
    plan = [x for x in data["plan"] if not x["skip"]]
    if not plan:
        print("沒有需要 rename 的檔案")
        return
    print(f"執行 {len(plan)} 個 rename…")

    # 按資料夾分組，每資料夾兩階段：先 src→tmp，再 tmp→target
    by_folder: dict[str, list[dict]] = {}
    for item in plan:
        by_folder.setdefault(item["folder"], []).append(item)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    renamed = skipped = errors = 0

    with LOG_PATH.open("a", encoding="utf-8") as log:
        for folder_str, items in by_folder.items():
            folder = Path(folder_str)
            # Phase 1: src → tmp
            tmp_map = []
            for i, item in enumerate(items):
                src = Path(item["src"])
                if not src.exists():
                    skipped += 1
                    continue
                tmp = folder / f"{TMP_PREFIX}{i:05d}{normalize_ext(src.suffix)}"
                try:
                    src.rename(tmp)
                    tmp_map.append((tmp, item["target_name"], src.name))
                except Exception as e:
                    print(f"ERR phase1 {src}: {e}")
                    errors += 1

            # Phase 2: tmp → target_name
            for tmp, target_name, orig_name in tmp_map:
                tgt = folder / target_name
                if tgt.exists():
                    stem, suf = tgt.stem, tgt.suffix
                    j = 2
                    while True:
                        cand = folder / f"{stem}_dup{j}{suf}"
                        if not cand.exists():
                            tgt = cand
                            break
                        j += 1
                try:
                    tmp.rename(tgt)
                    log.write(json.dumps({
                        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "folder": folder_str,
                        "from": orig_name,
                        "to": tgt.name,
                    }, ensure_ascii=False) + "\n")
                    renamed += 1
                    if renamed % 200 == 0:
                        print(f"  …renamed {renamed}")
                except Exception as e:
                    print(f"ERR phase2 {tmp}: {e}")
                    errors += 1

    print(f"\nRename 完成：renamed={renamed} skipped={skipped} errors={errors}")
    print(f"Log: {LOG_PATH}")


def cmd_auto(libs: list[str]):
    """每個 library：plan → execute（連跑）。Overnight 用。"""
    if not libs:
        libs = list(LIBRARIES)
    print(f"=== AUTO mode: {libs} ===\n")
    for lib in libs:
        if lib not in LIBRARIES:
            print(f"!! 跳過未知 library：{lib}")
            continue
        print(f"\n========== [{lib}] ==========")
        set_library(lib)
        print(f"PHOTOS_ROOT = {PHOTOS_ROOT}")
        print(f"\n--- PLAN ---")
        cmd_plan()
        print(f"\n--- EXECUTE ---")
        cmd_execute()
    print("\n=== AUTO mode done ===")


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] not in ("plan", "execute", "auto"):
        print(__doc__)
        sys.exit(1)
    cmd = argv[0]
    rest = argv[1:]
    if cmd == "auto":
        cmd_auto(rest)
        return
    # plan/execute：optional 第二參數選 library
    if rest:
        set_library(rest[0])
    if cmd == "plan":
        cmd_plan()
    else:
        cmd_execute()


if __name__ == "__main__":
    main()
