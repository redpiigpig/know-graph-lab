#!/usr/bin/env python3
"""把訓練／弘誓的大影片就地轉成 HEVC (hevc_nvenc cq26)，省容量、畫質肉眼無差。

安全流程（每支）：
  1. ffprobe 取時長/編碼/解析度/音訊
  2. 已是 hevc 且位元率已低 → 跳過（不重壓）
  3. hevc_nvenc 編到「本機暫存」(c:/tmp，不碰 Drive)
  4. 驗證：時長一致(±1s/±1%)、解析度一致、檔案明顯變小(≤85%)
  5. 全過 → copy 到 G: 同夾 .tmp → os.replace 同卷 atomic 覆蓋原檔（檔名不變）
  6. 任一條不過 → 刪暫存、保留原檔
ledger 可續跑；崩潰重啟自動跳過已完成。

用法：
  python scripts/transcode_videos.py --list        # 只列要處理的清單 + 預估
  python scripts/transcode_videos.py               # 實跑（可隨時中斷、重跑續傳）
  python scripts/transcode_videos.py --limit 3     # 只跑前 3 支（測試用）
"""
import json, os, subprocess, sys, time, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "scripts" / "photo_index.json"
LEDGER = REPO / "scripts" / "transcode_ledger.json"
LOG = REPO / "scripts" / "logs" / "transcode_videos.log"
WORK = Path("c:/tmp/transcode_work")
PHOTOS_ROOT = Path(r"G:/我的雲端硬碟/資料/儲存資料夾")
LIB_DIR = {"training": "訓練相片", "hongshi": "弘誓相片"}

VID_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}
HEVC_OK_CONTAINER = {".mp4", ".mov", ".m4v"}  # 這些容器能裝 hevc，保留原副檔名

CQ = "26"
PRESET = "p6"
MIN_BYTES = {"training": 20 * 1024 * 1024, "hongshi": 50 * 1024 * 1024}
REPLACE_RATIO = 0.85          # 壓後須 ≤ 原始 85% 才替換
ALREADY_HEVC_BITRATE = 12e6   # 已是 hevc 且 < 12Mbps 視為已優化，跳過
DUR_TOL = 1.0                 # 時長容忍秒數


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


def ffprobe(path):
    """回 (duration, vcodec, acodec, w, h)。"""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,codec_name,width,height",
         "-of", "json", path],
        capture_output=True, text=True)
    data = json.loads(out.stdout or "{}")
    dur = float(data.get("format", {}).get("duration") or 0)
    vcodec = acodec = None
    w = h = 0
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and vcodec is None:
            vcodec = s.get("codec_name"); w = s.get("width") or 0; h = s.get("height") or 0
        elif s.get("codec_type") == "audio" and acodec is None:
            acodec = s.get("codec_name")
    return dur, vcodec, acodec, w, h


def collect():
    idx = json.load(open(INDEX, encoding="utf-8"))
    jobs = []
    for lib in ("training", "hongshi"):
        node = idx["libraries"].get(lib)
        if not node:
            continue
        minb = MIN_BYTES[lib]
        for sub, fn in node.get("folders", {}).items():
            for f in fn["files"]:
                ext = f["ext"].lower()
                if ext in VID_EXT and f["size"] >= minb:
                    rel = os.path.join(LIB_DIR[lib], sub, f["name"])
                    jobs.append({"lib": lib, "path": str(PHOTOS_ROOT / rel),
                                 "size": f["size"], "name": f["name"], "ext": ext})
    jobs.sort(key=lambda j: -j["size"])
    return jobs


def main():
    args = sys.argv[1:]
    list_only = "--list" in args
    limit = None
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])

    jobs = collect()
    ledger = load_ledger()
    todo = [j for j in jobs if ledger.get(j["path"], {}).get("status") not in ("done", "skipped", "missing")]
    tot = sum(j["size"] for j in todo)
    by_lib = {}
    for j in todo:
        by_lib[j["lib"]] = by_lib.get(j["lib"], 0) + 1

    if "--count" in args:        # 純 ASCII 整數，給 retry-loop 判斷是否跑乾
        print(len(todo))
        return

    print(f"待處理 {len(todo)} 支，共 {tot/1e9:.1f} GB（{by_lib}），ledger 已記錄 {len(ledger)} 筆")
    if list_only:
        for j in todo[:40]:
            print(f"  {j['size']/1e6:8.1f} MB | {j['lib']:8} | {j['name']}")
        if len(todo) > 40:
            print(f"  ... 還有 {len(todo)-40} 支")
        return

    if limit:
        todo = todo[:limit]

    WORK.mkdir(parents=True, exist_ok=True)
    log(f"=== START === {len(todo)} 支 / {sum(j['size'] for j in todo)/1e9:.1f} GB")
    saved_total = 0
    for i, j in enumerate(todo, 1):
        src = j["path"]
        tag = f"[{i}/{len(todo)}]"
        if not os.path.exists(src):
            log(f"{tag} MISSING {j['name']}"); ledger[src] = {"status": "missing"}; save_ledger(ledger); continue
        try:
            dur0, vcodec, acodec, w, h = ffprobe(src)
        except Exception as e:
            log(f"{tag} PROBE-FAIL {j['name']}: {e}"); ledger[src] = {"status": "probe_fail"}; save_ledger(ledger); continue

        br = j["size"] * 8 / dur0 if dur0 else 0
        if vcodec == "hevc" and br < ALREADY_HEVC_BITRATE:
            log(f"{tag} SKIP already-hevc {j['name']} ({br/1e6:.1f}Mbps)")
            ledger[src] = {"status": "skipped", "reason": "already_hevc"}; save_ledger(ledger); continue

        ext = j["ext"] if j["ext"] in HEVC_OK_CONTAINER else ".mp4"
        work = WORK / f"work_{i}{ext}"
        if work.exists():
            work.unlink()
        acopy = acodec in ("aac", "mp3", "ac3", "eac3", "opus")
        acodec_args = ["-c:a", "copy"] if acopy else ["-c:a", "aac", "-b:a", "192k"]
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src,
               "-map", "0:v:0", "-map", "0:a?", "-map_metadata", "0",
               "-c:v", "hevc_nvenc", "-preset", PRESET, "-rc", "vbr", "-cq", CQ,
               "-b:v", "0", "-pix_fmt", "yuv420p", "-tag:v", "hvc1",
               *acodec_args, "-movflags", "+faststart", str(work)]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - t0
        if r.returncode != 0 or not work.exists():
            log(f"{tag} ENCODE-FAIL {j['name']}: {r.stderr.strip()[:200]}")
            ledger[src] = {"status": "encode_fail"}; save_ledger(ledger)
            if work.exists():
                work.unlink()
            continue

        try:
            dur1, vc1, ac1, w1, h1 = ffprobe(str(work))
        except Exception as e:
            log(f"{tag} VERIFY-FAIL {j['name']}: {e}"); work.unlink(); ledger[src] = {"status": "verify_fail"}; save_ledger(ledger); continue
        newsize = work.stat().st_size
        ok_dur = abs(dur1 - dur0) <= max(DUR_TOL, dur0 * 0.01)
        # 直式手機影片有旋轉旗標（存儲 WxH、顯示 HxW）；ffmpeg 重編會把旋轉烤進畫面
        # 輸出真‧HxW（視覺正確）。故長寬對調也算通過，只擋真正的解析度改變。
        ok_dim = sorted((w1, h1)) == sorted((w, h))
        ok_small = newsize <= j["size"] * REPLACE_RATIO
        if not (ok_dur and ok_dim):
            log(f"{tag} REJECT {j['name']} dur {dur0:.1f}->{dur1:.1f} dim {w}x{h}->{w1}x{h1}")
            work.unlink(); ledger[src] = {"status": "reject_integrity"}; save_ledger(ledger); continue
        if not ok_small:
            log(f"{tag} KEEP-ORIG {j['name']} 壓後 {newsize/1e6:.0f}MB 不夠小（原 {j['size']/1e6:.0f}MB）")
            work.unlink(); ledger[src] = {"status": "skipped", "reason": "not_smaller"}; save_ledger(ledger); continue

        # 替換：copy 到 G: 同夾 .tmp → 同卷 os.replace atomic 覆蓋
        dst = src if ext == j["ext"] else os.path.splitext(src)[0] + ext
        gtmp = dst + ".__newhevc.tmp"
        try:
            shutil.copyfile(str(work), gtmp)
            os.replace(gtmp, dst)               # 同卷 atomic
            if dst != src and os.path.exists(src):
                os.remove(src)                  # 副檔名變了才需刪舊（本批不會發生）
        except Exception as e:
            log(f"{tag} REPLACE-FAIL {j['name']}: {e}")
            if os.path.exists(gtmp):
                try: os.remove(gtmp)
                except Exception: pass
            work.unlink(); ledger[src] = {"status": "replace_fail"}; save_ledger(ledger); continue
        work.unlink()
        saved = j["size"] - newsize
        saved_total += saved
        log(f"{tag} OK {j['name']} {j['size']/1e6:.0f}->{newsize/1e6:.0f}MB "
            f"(-{saved/1e6:.0f}MB, {newsize/j['size']*100:.0f}%) {dt:.0f}s acopy={acopy} 累省 {saved_total/1e9:.1f}GB")
        ledger[src] = {"status": "done", "orig": j["size"], "new": newsize}
        save_ledger(ledger)
    log(f"=== DONE === 本輪累省 {saved_total/1e9:.1f} GB")


if __name__ == "__main__":
    main()
