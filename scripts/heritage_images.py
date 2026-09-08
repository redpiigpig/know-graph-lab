# -*- coding: utf-8 -*-
"""把國家文化記憶庫的開放影像抓成本機素材庫（給影片用）。

來源是文化部／臺史博的開放資料集 API（不需金鑰）：
    https://tcmbdata.culture.tw/opendata/dataSet/culture?subject=<代碼>

**這個端點只釋出可開放授權的那一批**——6,000 筆跨分頁抽樣的結果是
CC BY 48%／PDM 26%／OGDL 16%／CC0 6%／CC BY-SA 3.7%，**一筆 NC 都沒有**。
（網站前台整體約有 49% 只到「非商業性使用」，那些不在這個 API 裡。）
所以這裡抓下來的東西全部可商用，差別只在要不要標示：

    PDM / CC0            免標示（仍建議標）
    CC BY / OGDL         必須標示
    CC BY-SA             必須標示，且**帶相同方式分享**——會傳染到整支影片，
                         所以單獨隔離在 _相同方式分享SA/，預設不要用

用法：
    python heritage_images.py --plan                 # 只抓 metadata，看有多少東西
    python heritage_images.py --run                  # 下載（可重複執行，會續跑）
    python heritage_images.py --run --subject 民俗與宗教
    python heritage_images.py --credits              # 重出授權標示.txt

續跑：ledger.json 記每張圖的狀態，中斷後再跑一次就接著下載（筆電會通勤休眠，
一定要能續跑，見 feedback_laptop_sleeps_design_for_resume）。
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API = "https://tcmbdata.culture.tw/opendata/dataSet/culture"
ROOT = Path(r"G:\我的雲端硬碟\創作\影片創作\_素材庫\國家文化記憶庫")
UA = {"User-Agent": "know-graph-lab/1.0 (personal research asset library)"}

# 抓取順序＝對本專案的有用程度，中斷時先確保前面幾類是完整的
SUBJECTS = [
    ("民俗與宗教", "CULTURE_AND_RELIGION"),
    ("人物與團體", "PEOPLE_AND_GROUP"),
    ("藝術與人文", "ART_AND_HUMANITY"),
    ("族群與語言", "ETHNIC_AND_LANGUAGE"),
    ("社會與政治", "SOCIAL_AND_POLITIC"),
    ("產業與經濟", "INDUSTRY_AND_ECONOMIC"),
]
# 生物、生態與環境那一類的代碼還沒試出來（見 SKILL 的「查不到」）
KIND = {"Culture_Object": "作品文物", "Culture_Event": "活動事件", "Culture_People": "人物",
        "Culture_Place": "空間", "Culture_Media": "影音", "Culture_Organization": "組織",
        "Culture_Invisible": "無形文化資產", "Culture_Route": "踏查路線"}
SA_DIR = "_相同方式分享SA"
BAD = re.compile(r'[\\/:*?"<>|\r\n\t]')


def fetch(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def safe(text, limit=40):
    text = BAD.sub("", (text or "").strip()).replace(" ", "")
    return text[:limit] or "無題"


def collect(subject_zh, code, out: Path):
    """抓完整 metadata（一筆一行 JSONL）。"""
    rows, page, total = [], 0, None
    while True:
        d = fetch(f"{API}?subject={code}&page={page}&size=200")
        total = d.get("total", 0)
        batch = d.get("rows") or []
        if not batch:
            break
        rows.extend(batch)
        print(f"\r  {subject_zh}  {len(rows)}/{total}", end="", flush=True)
        if len(rows) >= total:
            break
        page += 1
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    print(f"\r  {subject_zh}  {len(rows)} 筆 → {out.name}          ")
    return rows


def plan_rows(rows, subject_zh):
    """一張圖一個工作項。"""
    jobs = []
    for r in rows:
        images = r.get("images") or []
        if not images:
            continue
        lic = (r.get("imageLicense") or "未標示").strip()
        kind = KIND.get(r.get("indexCode"), r.get("indexCode") or "其他")
        folder = Path(SA_DIR) / subject_zh / kind if "SA" in lic.upper().split() or lic.upper().endswith("-SA") \
            else Path(subject_zh) / kind
        for n, url in enumerate(images, 1):
            ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff"):
                ext = ".jpg"
            suffix = f"_{n}" if len(images) > 1 else ""
            name = f"{r.get('identifier') or r.get('id')}_{safe(r.get('title'))}{suffix}{ext}"
            jobs.append({
                "url": url, "path": str(folder / name), "license": lic,
                "title": r.get("title"), "dept": r.get("createDept"),
                "subject": subject_zh, "kind": kind,
                "identifier": r.get("identifier"), "tcmbUrl": r.get("tcmbUrl"),
                "originalUrl": r.get("originalUrl"), "keywords": r.get("keywords") or [],
            })
    return jobs


def download(job, ledger):
    dest = ROOT / job["path"]
    if dest.exists() and dest.stat().st_size > 0:
        ledger[job["url"]] = {"path": job["path"], "size": dest.stat().st_size}
        return "skip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(job["url"], headers=UA), timeout=120) as r:
            data = r.read()
        if not data:
            raise ValueError("空檔")
        tmp = dest.with_suffix(dest.suffix + ".part")
        tmp.write_bytes(data)
        tmp.replace(dest)
        ledger[job["url"]] = {"path": job["path"], "size": len(data)}
        return "ok"
    except Exception as e:
        ledger[job["url"]] = {"error": str(e)[:120]}
        return "fail"


def write_credits(jobs, path: Path):
    """可以直接貼進影片說明欄的授權標示。"""
    by_lic = {}
    for j in jobs:
        by_lic.setdefault(j["license"], {}).setdefault(j["dept"] or "未標示單位", set()).add(j["subject"])
    lines = ["國家文化記憶庫影像素材　授權標示",
             "（來源：文化部國家文化記憶庫 https://tcmb.culture.tw ；本檔由 scripts/heritage_images.py 產生）",
             ""]
    note = {
        "PDM": "公眾領域標章：著作權已消滅，任何方式任何目的皆可使用。標示非義務，但仍建議標。",
        "CC0": "作者拋棄所有著作權利。標示非義務，但仍建議標。",
        "CC BY": "姓名標示：**必須**標明建檔單位與來源，可商用、可改作。",
        "OGDL": "政府資料開放授權條款第 1 版：**必須**標明出處，可商用、可改作。",
        "CC BY-SA": "姓名標示─相同方式分享：必須標示，且衍生作品要用相同條款釋出。"
                    "**會傳染到整支影片，預設不要用**（已隔離在 " + SA_DIR + "/）。",
    }
    for lic in sorted(by_lic):
        lines.append(f"── {lic} ──")
        if lic in note:
            lines.append(f"   {note[lic]}")
        for dept, subs in sorted(by_lic[lic].items()):
            lines.append(f"   {dept}（{'、'.join(sorted(subs))}）")
        lines.append("")
    lines += ["", "影片說明欄可用的簡短版：",
              "本片部分影像取自文化部國家文化記憶庫（https://tcmb.culture.tw），"
              "依 CC BY／OGDL／公眾領域條款使用，各影像之建檔單位詳見本檔。"]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="只抓 metadata 並統計")
    ap.add_argument("--run", action="store_true", help="下載影像（可續跑）")
    ap.add_argument("--credits", action="store_true", help="重出授權標示.txt")
    ap.add_argument("--subject", help="只處理某一主題（中文名）")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, help="最多下載幾張（試跑用）")
    args = ap.parse_args()

    ROOT.mkdir(parents=True, exist_ok=True)
    meta_dir = ROOT / "_metadata"
    meta_dir.mkdir(exist_ok=True)
    subjects = [(z, c) for z, c in SUBJECTS if not args.subject or z == args.subject]

    all_jobs = []
    for zh, code in subjects:
        f = meta_dir / f"{zh}.jsonl"
        if f.exists() and not args.plan:
            rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        else:
            rows = collect(zh, code, f)
        all_jobs += plan_rows(rows, zh)

    lic_count, size_hint = {}, 0
    for j in all_jobs:
        lic_count[j["license"]] = lic_count.get(j["license"], 0) + 1
    print(f"\n共 {len(all_jobs):,} 張圖")
    for k, v in sorted(lic_count.items(), key=lambda x: -x[1]):
        print(f"  {k:10} {v:6,}")
    (ROOT / "_metadata" / "jobs.jsonl").write_text(
        "\n".join(json.dumps(j, ensure_ascii=False) for j in all_jobs), encoding="utf-8")

    if args.credits or args.run:
        write_credits(all_jobs, ROOT / "授權標示.txt")
        print(f"授權標示 → {ROOT / '授權標示.txt'}")
    if not args.run:
        return

    # 排程與手動同時跑會重工：上一個行程還活著（鎖在 10 分鐘內動過）就安靜退出
    lock = ROOT / ".lock"
    if lock.exists() and time.time() - lock.stat().st_mtime < 600:
        print("另一個下載行程還在跑（.lock 仍新），這次跳過")
        return
    lock.write_text(str(int(time.time())), encoding="utf-8")

    led_path = ROOT / "ledger.json"
    ledger = json.loads(led_path.read_text(encoding="utf-8")) if led_path.exists() else {}
    todo = [j for j in all_jobs if j["url"] not in ledger or "error" in ledger[j["url"]]]
    if args.limit:
        todo = todo[:args.limit]
    print(f"待下載 {len(todo):,} 張（已完成 {len(all_jobs) - len(todo):,}）\n")

    done = {"ok": 0, "skip": 0, "fail": 0}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, res in enumerate(ex.map(lambda j: download(j, ledger), todo), 1):
            done[res] += 1
            if i % 50 == 0 or i == len(todo):
                el = time.time() - t0
                eta = el / i * (len(todo) - i) / 60
                print(f"\r  {i:,}/{len(todo):,}  成功 {done['ok']:,} 失敗 {done['fail']:,}"
                      f"  {i / max(el, 1):.1f} 張/秒  剩約 {eta:.0f} 分  ", end="", flush=True)
                led_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
                lock.write_text(str(int(time.time())), encoding="utf-8")   # 續命
    led_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    lock.unlink(missing_ok=True)
    ok = sum(1 for v in ledger.values() if "error" not in v)
    gb = sum(v.get("size", 0) for v in ledger.values()) / 1024 ** 3
    print(f"\n\n完成 {ok:,}／{len(all_jobs):,} 張，共 {gb:.1f} GB → {ROOT}")
    if ok < len(all_jobs):
        print("還沒抓完，再跑一次同一個指令就會續跑。")
        sys.exit(1)   # 排程看得懂：還沒完


if __name__ == "__main__":
    main()
