#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辰瑋相片自動分類。

掃描每個 YYYY相片/ 根目錄的散檔（不動已分類到子資料夾的檔），用 EXIF 與
檔名啟發式判斷類型，計劃搬移至：
  - 截圖：       {year}相片/{year}截圖/
  - 下載：       {year}相片/{year}下載/
  - 手機/相機拍： {year}相片/{year}.{MM}/    （月份由 EXIF DateTimeOriginal
                                                或檔名時間戳推斷）
  - 無法判斷：    {year}相片/{year}未分類/

EXIF year 若與所在年份資料夾不同，仍歸入「所在年份資料夾的對應月份」，
並在 report 加 cross_year 旗標。

Usage:
    python scripts/classify_photos.py plan      # dry-run, 寫出 report JSON
    python scripts/classify_photos.py execute   # 依 report 實際搬移
"""
import json
import re
import sys
import shutil
import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from PIL import Image, ExifTags

PHOTOS_ROOT = Path("G:/我的雲端硬碟/資料/儲存資料夾/辰瑋相片")
REPORT_PATH = Path(__file__).parent / "photo_classification_report.json"
MOVE_LOG_PATH = Path(__file__).parent / "photo_move_log.jsonl"

IMG_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif", ".avif", ".bmp",
    ".mp4", ".mov", ".m4v", ".webm", ".mkv",
}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}

PHONE_MAKES = {
    "apple", "samsung", "huawei", "htc", "asus", "google", "xiaomi",
    "oneplus", "oppo", "vivo", "realme", "lge", "lg", "motorola",
}
CAMERA_MAKES = {
    "canon", "nikon", "fujifilm", "olympus", "panasonic", "ricoh",
    "leica", "pentax", "sigma", "hasselblad", "casio", "kodak",
    "gopro",
}
# Sony 同時做相機與手機，靠 model 判斷
SONY_PHONE_MODEL_HINTS = ("xperia", "j9110", "j8110", "h9436", "h8")


def read_exif(img_path: Path):
    """Returns (exif_named_dict, width, height, format) or ({}, 0, 0, None)."""
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            fmt = img.format
            raw = img._getexif() if hasattr(img, "_getexif") else None
            named = {ExifTags.TAGS.get(k, k): v for k, v in (raw or {}).items()}
            return named, w, h, fmt
    except Exception:
        return {}, 0, 0, None


def parse_filename_datetime(name: str):
    """從檔名抓 YYYY-MM-DD/YYYYMMDD/YYYY.MM.DD 等格式，回傳 datetime 或 None."""
    # P_20180117_123105, IMG_20240315_xxx, 20180117_123105
    m = re.search(r"(20[0-2]\d)[-_.\s]?(0[1-9]|1[0-2])[-_.\s]?(0[1-9]|[12]\d|3[01])"
                  r"(?:[-_\s]?([01]\d|2[0-3])([0-5]\d)?([0-5]\d)?)?", name)
    if not m:
        return None
    try:
        Y = int(m.group(1)); M = int(m.group(2)); D = int(m.group(3))
        hh = int(m.group(4) or 0); mm = int(m.group(5) or 0); ss = int(m.group(6) or 0)
        return datetime.datetime(Y, M, D, hh, mm, ss)
    except Exception:
        return None


def parse_exif_datetime(s):
    if not s: return None
    if isinstance(s, bytes):
        try: s = s.decode("ascii", errors="ignore")
        except: return None
    s = s.strip().strip("\x00")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d", "%Y-%m-%d"):
        try: return datetime.datetime.strptime(s, fmt)
        except: pass
    return None


def decode_user_comment(uc):
    if uc is None: return ""
    if isinstance(uc, bytes):
        try: return uc.decode("ascii", errors="ignore")
        except: return ""
    return str(uc)


def classify(file_path: Path):
    """Return dict: kind, captured (iso or None), confidence, reason, exif_year."""
    ext = file_path.suffix.lower()
    name = file_path.name
    name_low = name.lower()

    # 檔名直接是 Screenshot 開頭 → Android 截圖
    if (name_low.startswith(("screenshot", "screen_shot", "screen shot"))
            or "截圖" in name or "螢幕截圖" in name):
        return {"kind": "screenshot", "captured": None,
                "confidence": "high", "reason": "filename starts with Screenshot"}

    exif, w, h, fmt = read_exif(file_path)
    make = (exif.get("Make") or "").strip().strip("\x00").lower()
    model = (exif.get("Model") or "").strip().strip("\x00")
    uc = decode_user_comment(exif.get("UserComment"))
    captured = parse_exif_datetime(exif.get("DateTimeOriginal")) \
            or parse_exif_datetime(exif.get("DateTime"))

    if not captured:
        captured = parse_filename_datetime(name)

    captured_iso = captured.isoformat() if captured else None
    exif_year = captured.year if captured else None

    # iOS Screenshot 標記
    if "Screenshot" in uc:
        return {"kind": "screenshot", "captured": captured_iso,
                "confidence": "high", "reason": "EXIF UserComment=Screenshot"}

    is_video = ext in VIDEO_EXTS

    # 有 Make/Model — 拍攝裝置
    if make:
        if make in PHONE_MAKES:
            kind = "phone"
            reason = f"EXIF Make={make}"
        elif make in CAMERA_MAKES:
            kind = "camera"
            reason = f"EXIF Make={make}"
        elif make == "sony":
            if any(h in model.lower() for h in SONY_PHONE_MODEL_HINTS):
                kind, reason = "phone", f"Sony {model} (Xperia)"
            else:
                kind, reason = "camera", f"Sony {model}"
        else:
            # 未知品牌但有 metadata → 視為手機
            kind, reason = "phone", f"unknown make={make}"
        return {"kind": kind, "captured": captured_iso,
                "confidence": "high", "reason": reason}

    # HEIC/HEIF：Apple 專屬格式，幾乎都是 iPhone 拍的
    if ext in (".heic", ".heif"):
        return {"kind": "phone", "captured": captured_iso,
                "confidence": "med", "reason": "HEIC/HEIF native Apple format"}

    # 沒 Make/Model — screenshot 還是 download
    if ext == ".png":
        if w and h:
            long_side, short_side = max(w, h), min(w, h)
            ratio = long_side / short_side if short_side else 0
            # 常見手機長寬比 1.5 (3:2) ~ 2.2 (19.5:9)，typically portrait
            if 1.55 <= ratio <= 2.5 and short_side <= 1500:
                return {"kind": "screenshot", "captured": captured_iso,
                        "confidence": "med", "reason": f"PNG no-make + phone ratio {ratio:.2f} @ {w}x{h}"}
        return {"kind": "download", "captured": captured_iso,
                "confidence": "med", "reason": "PNG no-make non-phone-ratio"}
    if ext in {".webp", ".gif", ".avif"}:
        return {"kind": "download", "captured": captured_iso,
                "confidence": "high", "reason": f"{ext} typically web-format"}

    # 沒 EXIF Make 的 JPG/JPEG / 影片
    is_video = ext in VIDEO_EXTS
    label = "video" if is_video else "JPG"
    if captured:
        # 檔名有時間戳，但 EXIF 被剝光 → 多半是處理過的手機照／影片
        return {"kind": "phone", "captured": captured_iso,
                "confidence": "low", "reason": f"{label} no EXIF make, filename has timestamp"}
    return {"kind": "download", "captured": None,
            "confidence": "low", "reason": f"{label} no EXIF make, no date in name"}


def plan_target(file_path: Path, year_folder: str, info: dict) -> tuple[Path, str]:
    """Return (target_dir, bucket_label). 跨年照片依 EXIF 真實年份搬。"""
    folder_year = year_folder.replace("相片", "")
    kind = info["kind"]
    captured = info["captured"]

    # 嘗試由 captured 取得真實年份，否則 fallback 至所在資料夾年份
    cap_year = captured[:4] if captured else None
    target_year = (cap_year if cap_year and "2014" <= cap_year <= "2026"
                   else folder_year)

    base = PHOTOS_ROOT / f"{target_year}相片"

    if kind == "screenshot":
        return base / f"{target_year}截圖", "screenshot"
    if kind == "download":
        return base / f"{target_year}下載", "download"
    if kind in ("phone", "camera"):
        if captured:
            month = captured[5:7]
            return base / f"{target_year}.{month}", "photo"
        return base / f"{target_year}未分類", "photo-undated"
    return base / f"{target_year}未分類", "unknown"


# 哪些年份要掃 YYYY.MM 月份子資料夾，挑出混進去的截圖／下載
SCAN_MONTH_SUBDIR_YEARS = {str(y) for y in range(2014, 2023)}  # 2014..2022


def collect_plan():
    plan = []
    for year_dir in sorted(PHOTOS_ROOT.iterdir()):
        if not year_dir.is_dir(): continue
        if not year_dir.name.endswith("相片"): continue
        year_num = year_dir.name.replace("相片", "")
        month_re = re.compile(rf"^{year_num}\.(0[1-9]|1[0-2])$")

        # Pass 1: 散檔 (loose) — 全分類搬
        for f in year_dir.iterdir():
            if not (f.is_file() and f.suffix.lower() in IMG_EXTS):
                continue
            info = classify(f)
            tgt_dir, bucket = plan_target(f, year_dir.name, info)
            plan.append({
                "src": str(f).replace("\\", "/"),
                "tgt_dir": str(tgt_dir).replace("\\", "/"),
                "bucket": bucket,
                "kind": info["kind"],
                "captured": info["captured"],
                "confidence": info["confidence"],
                "reason": info["reason"],
                "year_folder": year_dir.name,
                "source": "loose",
                "cross_year": bool(info["captured"]
                                   and info["captured"][:4] != year_num),
            })

        # Pass 2: YYYY.MM 月份子資料夾 — 只抽出截圖／下載；
        # 真正的照片留在原月份；事件子資料夾完全略過
        if year_num not in SCAN_MONTH_SUBDIR_YEARS:
            continue
        for sub in year_dir.iterdir():
            if not sub.is_dir(): continue
            if not month_re.match(sub.name): continue   # 事件資料夾跳過
            for f in sub.iterdir():
                if not (f.is_file() and f.suffix.lower() in IMG_EXTS):
                    continue
                info = classify(f)
                if info["kind"] not in ("screenshot", "download"):
                    continue  # 照片留在原月份
                # 月份內僅搬高信心 screenshot/download，避免把照片誤搬
                if info["confidence"] != "high":
                    continue
                tgt_dir, bucket = plan_target(f, year_dir.name, info)
                plan.append({
                    "src": str(f).replace("\\", "/"),
                    "tgt_dir": str(tgt_dir).replace("\\", "/"),
                    "bucket": bucket,
                    "kind": info["kind"],
                    "captured": info["captured"],
                    "confidence": info["confidence"],
                    "reason": info["reason"],
                    "year_folder": year_dir.name,
                    "source": f"month/{sub.name}",
                    "cross_year": bool(info["captured"]
                                       and info["captured"][:4] != year_num),
                })
    return plan


def summarize(plan):
    by_year = {}
    for item in plan:
        y = item["year_folder"]
        by_year.setdefault(y, {"screenshot": 0, "download": 0, "photo": 0,
                               "photo-undated": 0, "from_month": 0,
                               "cross_year": 0, "low_conf": 0})
        by_year[y][item["bucket"]] += 1
        if item.get("source", "").startswith("month/"): by_year[y]["from_month"] += 1
        if item["cross_year"]: by_year[y]["cross_year"] += 1
        if item["confidence"] == "low": by_year[y]["low_conf"] += 1
    return by_year


def cmd_plan():
    print("Scanning…")
    plan = collect_plan()
    print(f"Total loose files: {len(plan)}")
    summary = summarize(plan)
    REPORT_PATH.write_text(
        json.dumps({"plan": plan, "summary": summary}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\nReport: {REPORT_PATH}")
    print(f"\n{'year':<10}{'screenshot':>11}{'download':>10}{'photo':>8}{'undated':>9}{'from_mo':>9}{'cross_yr':>10}{'low_conf':>10}")
    for y in sorted(summary):
        s = summary[y]
        print(f"{y:<10}{s['screenshot']:>11}{s['download']:>10}{s['photo']:>8}"
              f"{s['photo-undated']:>9}{s['from_month']:>9}{s['cross_year']:>10}{s['low_conf']:>10}")


def cmd_execute():
    if not REPORT_PATH.exists():
        print(f"先跑 plan：{REPORT_PATH} 不存在")
        sys.exit(1)
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    plan = data["plan"]
    print(f"執行 {len(plan)} 個搬移…")
    MOVE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    moved = skipped = errors = 0
    with MOVE_LOG_PATH.open("a", encoding="utf-8") as log:
        for item in plan:
            src = Path(item["src"])
            tgt_dir = Path(item["tgt_dir"])
            if not src.exists():
                skipped += 1; continue
            tgt_dir.mkdir(parents=True, exist_ok=True)
            tgt = tgt_dir / src.name
            if tgt.exists():
                # 同名衝突 → 加 suffix
                stem, suf = tgt.stem, tgt.suffix
                i = 2
                while True:
                    cand = tgt_dir / f"{stem}_dup{i}{suf}"
                    if not cand.exists(): tgt = cand; break
                    i += 1
            try:
                shutil.move(str(src), str(tgt))
                log.write(json.dumps({
                    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                    "from": str(src).replace("\\","/"),
                    "to": str(tgt).replace("\\","/"),
                    "bucket": item["bucket"],
                }, ensure_ascii=False) + "\n")
                moved += 1
                if moved % 200 == 0:
                    print(f"  …moved {moved}")
            except Exception as e:
                print(f"ERR {src}: {e}")
                errors += 1
    print(f"\n搬移完成：moved={moved} skipped={skipped} errors={errors}")
    print(f"Move log: {MOVE_LOG_PATH}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("plan", "execute"):
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "plan": cmd_plan()
    else: cmd_execute()


if __name__ == "__main__":
    main()
