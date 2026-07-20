#!/usr/bin/env python3
"""把三個相簿裡的 HEIC/HEIF 照片就地轉成 JPG（保留 EXIF，含日期與方向）。

動機：sharp 在 Windows 沒 libheif → HEIC 無法產縮圖，網站（本機/雲端）都顯示 📄/破圖。
轉成 JPG 後縮圖、瀏覽、雲端全部正常。

安全流程（每張）：
  1. pillow-heif 開檔 → 取 EXIF
  2. 存成同名 .jpg（quality 92）到 G: 同夾的 .tmp → os.replace atomic 成最終 .jpg
  3. 驗證 jpg 可開、尺寸一致 → 刪原 .heic
  4. 任一步失敗 → 保留原 HEIC
ledger 可續跑。轉完記得 `python scripts/build_photo_index.py`（副檔名變了）。

用法：
  python scripts/convert_heic_to_jpg.py --list
  python scripts/convert_heic_to_jpg.py
"""
import json, os, sys, time
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "scripts" / "photo_index.json"
LEDGER = REPO / "scripts" / "heic_convert_ledger.json"
LOG = REPO / "scripts" / "logs" / "convert_heic.log"
PHOTOS_ROOT = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/照片")
LIB_DIR = {"chenwei": "辰瑋相片", "training": "訓練相片", "hongshi": "弘誓相片"}
QUALITY = 92


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_ledger():
    if LEDGER.exists():
        try:
            return json.load(open(LEDGER, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_ledger(d):
    tmp = str(LEDGER) + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, LEDGER)


def chenwei_bucket_dir(year, bucket):
    base = PHOTOS_ROOT / LIB_DIR["chenwei"] / f"{year}相片"
    if bucket in [f"{m:02d}" for m in range(1, 13)]:
        return base / f"{year}.{bucket}"
    if bucket == "screenshots":
        return base / f"{year}截圖"
    if bucket == "downloads":
        return base / f"{year}下載"
    return base / bucket  # 事件夾


def collect():
    idx = json.load(open(INDEX, encoding="utf-8"))
    libs = idx["libraries"]
    jobs = []
    for lib, node in libs.items():
        if node.get("layout") == "year-month":
            for year, yd in node.get("years", {}).items():
                for bucket, arr in yd.get("buckets", {}).items():
                    d = chenwei_bucket_dir(year, bucket)
                    for f in arr:
                        if f["ext"].lower() in (".heic", ".heif"):
                            jobs.append({"lib": lib, "path": str(d / f["name"]), "name": f["name"]})
        else:
            for sub, fn in node.get("folders", {}).items():
                d = PHOTOS_ROOT / LIB_DIR[lib] / sub
                for f in fn["files"]:
                    if f["ext"].lower() in (".heic", ".heif"):
                        jobs.append({"lib": lib, "path": str(d / f["name"]), "name": f["name"]})
    return jobs


def main():
    args = sys.argv[1:]
    list_only = "--list" in args
    jobs = collect()
    ledger = load_ledger()
    todo = [j for j in jobs if ledger.get(j["path"], {}).get("status") not in ("done", "missing")]
    print(f"待轉 {len(todo)} 張 HEIC（ledger 已記錄 {len(ledger)} 筆）")
    if list_only:
        for j in todo[:50]:
            print(f"  {j['lib']:8} | {j['name']}")
        return

    log(f"=== START HEIC→JPG === {len(todo)} 張")
    done = 0
    for i, j in enumerate(todo, 1):
        src = j["path"]
        tag = f"[{i}/{len(todo)}]"
        if not os.path.exists(src):
            log(f"{tag} MISSING {j['name']}"); ledger[src] = {"status": "missing"}; save_ledger(ledger); continue
        dst = os.path.splitext(src)[0] + ".jpg"
        if os.path.exists(dst):
            log(f"{tag} DST-EXISTS 已有同名 jpg，跳過 {j['name']}")
            ledger[src] = {"status": "missing", "reason": "dst_exists"}; save_ledger(ledger); continue
        gtmp = dst + ".__newjpg.tmp"
        try:
            im = Image.open(src)
            w0, h0 = im.size
            exif = im.info.get("exif")
            rgb = im.convert("RGB")
            if exif:
                rgb.save(gtmp, "JPEG", quality=QUALITY, exif=exif)
            else:
                rgb.save(gtmp, "JPEG", quality=QUALITY)
            # 驗證
            chk = Image.open(gtmp)
            if chk.size != (w0, h0):
                raise ValueError(f"尺寸不符 {(w0,h0)} -> {chk.size}")
            chk.close(); im.close()
            os.replace(gtmp, dst)               # 同卷 atomic
            os.remove(src)                       # 刪原 HEIC
        except Exception as e:
            log(f"{tag} FAIL {j['name']}: {e}")
            if os.path.exists(gtmp):
                try: os.remove(gtmp)
                except Exception: pass
            ledger[src] = {"status": "fail"}; save_ledger(ledger); continue
        ns = os.path.getsize(dst)
        done += 1
        log(f"{tag} OK {j['name']} → .jpg ({ns/1e6:.1f}MB)")
        ledger[src] = {"status": "done", "dst": dst}
        save_ledger(ledger)
    log(f"=== DONE === 轉成功 {done} 張。記得跑 build_photo_index.py")


if __name__ == "__main__":
    main()
