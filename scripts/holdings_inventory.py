"""資料總盤點：Drive／R2／站上電子圖書館／repo 索引，實際「已經有什麼」。

每個做研究或資料收集的 session，動手下載前先讀 docs/holdings.md，
或用 --find 查某本書、某份刊物是否已經在手上。收完資料要重跑一次。

  python -X utf8 scripts/holdings_inventory.py            # 重建 docs/holdings.md
  python -X utf8 scripts/holdings_inventory.py --find 海潮音 太虛
  python -X utf8 scripts/holdings_inventory.py --skip-r2  # R2 計數較慢時略過

輸出：
  docs/holdings.md                 人讀的總表（進 git）
  output/holdings/files.tsv        Drive 全部檔案清單（--find 用；不進 git）
  output/holdings/summary.json     機讀摘要

🚨 規模數字只代表「檔案存在」，不代表內容可用——頁碼真假、有無文字層、
   「有全文」是否只是連結，都要看各主題資料夾裡的「既有資料盤點.md」。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVE = Path(r"G:/我的雲端硬碟/資料/知識圖工作室")
OUT_DIR = ROOT / "output" / "holdings"
MD = ROOT / "docs" / "holdings.md"
FILES_TSV = OUT_DIR / "files.tsv"
SUMMARY = OUT_DIR / "summary.json"

# 往下展開幾層：研究資料、全集這類「主題夾」要看到子題；電子圖書館看到類別即可
DEPTH = {"研究資料": 3, "全集": 2, "電子圖書館": 2}
DEFAULT_DEPTH = 1
SKIP_DIRS = {"_chunks"}  # 巨量 JSONL，只算總數不展開

env = {}
envf = ROOT / ".env"
if envf.exists():
    for line in envf.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*(.*)", line)
        if m:
            env[m.group(1)] = m.group(2).strip().strip('"').strip("'")


def _get(*keys):
    for k in keys:
        if env.get(k):
            return env[k]
    return None


def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


# ---------------------------------------------------------------- Drive
def walk_drive():
    """回傳 (files 清單, 各資料夾彙總 dict)。"""
    if not DRIVE.exists():
        sys.exit("🚨 找不到 G: 的知識圖工作室——先 Test-Path 'G:\\我的雲端硬碟'，"
                 "G: 不見是 DriveFS 卡住（見 CLAUDE.md），不是沒有資料。")
    files = []
    agg = defaultdict(lambda: {"n": 0, "size": 0, "ext": Counter(), "mtime": 0.0})
    for dirpath, dirnames, filenames in os.walk(DRIVE):
        rel = Path(dirpath).relative_to(DRIVE)
        parts = rel.parts
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            if fn in ("desktop.ini",) or fn.startswith("~$"):
                continue
            p = Path(dirpath) / fn
            try:
                st = p.stat()
            except OSError:
                continue
            files.append((str(rel / fn), st.st_size, st.st_mtime))
            top = parts[0] if parts else "(根目錄)"
            depth = DEPTH.get(top, DEFAULT_DEPTH)
            for k in range(1, min(len(parts), depth) + 1):
                key = "/".join(parts[:k])
                a = agg[key]
                a["n"] += 1
                a["size"] += st.st_size
                a["ext"][p.suffix.lower() or "(無)"] += 1
                a["mtime"] = max(a["mtime"], st.st_mtime)
            if not parts:
                a = agg["(根目錄)"]
                a["n"] += 1
                a["size"] += st.st_size
    return files, agg


def topic_inventories():
    """各主題資料夾自己寫的盤點 md（既有資料盤點.md、*盤點*.md）。"""
    out = []
    for p in DRIVE.rglob("*盤點*.md"):
        if "_chunks" in p.parts:
            continue
        out.append((str(p.relative_to(DRIVE)), dt.datetime.fromtimestamp(p.stat().st_mtime)))
    return sorted(out)


# ---------------------------------------------------------------- R2
def r2_counts():
    try:
        import boto3
    except ImportError:
        return None, "boto3 未安裝"
    ep = _get("R2_ENDPOINT", "NUXT_R2_ENDPOINT")
    ak = _get("R2_ACCESS_KEY", "R2_ACCESS_KEY_ID", "NUXT_R2_ACCESS_KEY")
    sk = _get("R2_SECRET_KEY", "R2_SECRET_ACCESS_KEY", "NUXT_R2_SECRET_KEY")
    bucket = _get("R2_BUCKET", "NUXT_R2_BUCKET")
    if not all((ep, ak, sk, bucket)):
        return None, ".env 缺 R2 設定"
    s3 = boto3.client("s3", endpoint_url=ep, aws_access_key_id=ak,
                      aws_secret_access_key=sk, region_name="auto")
    tops = [p["Prefix"] for p in s3.list_objects_v2(Bucket=bucket, Delimiter="/").get("CommonPrefixes", [])]
    # research-private 底下再展開一層
    sub = [p["Prefix"] for p in s3.list_objects_v2(Bucket=bucket, Prefix="research-private/", Delimiter="/").get("CommonPrefixes", [])]
    prefixes = [t for t in tops if t != "research-private/"] + sub
    res = {}
    pag = s3.get_paginator("list_objects_v2")
    for pre in prefixes:
        n = size = 0
        t0 = time.time()
        for page in pag.paginate(Bucket=bucket, Prefix=pre):
            for o in page.get("Contents", []):
                n += 1
                size += o["Size"]
            if time.time() - t0 > 120:  # 單一前綴最多數兩分鐘，超過標「≥」
                res[pre] = (n, size, True)
                break
        else:
            res[pre] = (n, size, False)
    return res, None


# ---------------------------------------------------------------- 站上電子圖書館（Supabase ebooks）
def ebooks_counts():
    import urllib.request
    url = _get("SUPABASE_URL", "VITE_SUPABASE_URL")
    key = _get("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_KEY")
    if not (url and key):
        return None, ".env 缺 Supabase 設定"
    rows = []
    step = 1000  # 🚨 PostgREST 沒帶 range 會靜默截在 1000 筆（memory: postgrest_silent_1000_cap）
    start = 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/ebooks?select=title,category,subcategory,collection&order=id",
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Range-Unit": "items", "Range": f"{start}-{start + step - 1}"})
        try:
            batch = json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:  # noqa: BLE001
            return None, f"查詢失敗：{e}"
        rows += batch
        if len(batch) < step:
            break
        start += step
    return rows, None


# ---------------------------------------------------------------- repo 索引
def repo_indexes():
    base = ROOT / "public" / "content" / "research-data"
    out = []
    for p in sorted(base.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, list):
            n = len(d)
        elif isinstance(d, dict):
            lists = [v for v in d.values() if isinstance(v, list)]
            n = max((len(v) for v in lists), default=len(d))
        else:
            n = 0
        out.append((str(p.relative_to(ROOT)).replace("\\", "/"), n))
    return out


# ---------------------------------------------------------------- 產出
def build(skip_r2=False):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("掃 Drive …", flush=True)
    files, agg = walk_drive()
    with FILES_TSV.open("w", encoding="utf-8") as f:
        for path, size, mtime in files:
            f.write(f"{path}\t{size}\t{dt.datetime.fromtimestamp(mtime):%Y-%m-%d}\n")
    inv = topic_inventories()
    r2, r2err = (None, "略過") if skip_r2 else r2_counts()
    print("查站上電子圖書館 …", flush=True)
    eb, eberr = ebooks_counts()
    idx = repo_indexes()

    now = dt.datetime.now()
    L = []
    L.append("# 資料總盤點（自動產生）\n")
    L.append(f"產生時間：{now:%Y-%m-%d %H:%M}　指令：`python -X utf8 scripts/holdings_inventory.py`\n")
    L.append("> **做研究或收資料之前先讀這份**；查特定書刊用 `--find 關鍵字`。"
             "規模只代表檔案存在，內容能不能用（頁碼真假、有無文字層、「有全文」是否只是連結）"
             "要看下面各主題的盤點 md。外部來源與管線見 [data-sources.md](data-sources.md)。"
             "流程規則見 `.claude/skills/research-data-holdings/SKILL.md`。\n")

    L.append("\n## 一、各主題的盤點 md（先讀這些）\n")
    if inv:
        for rel, mt in inv:
            L.append(f"- `{rel}`（{mt:%Y-%m-%d}）")
    else:
        L.append("- （尚無）")

    L.append(f"\n## 二、Drive：`{DRIVE}`\n")
    L.append(f"全部 {len(files):,} 個檔案。\n")
    L.append("| 資料夾 | 檔數 | 容量 | 主要格式 | 最近更新 |")
    L.append("|---|---:|---:|---|---|")
    for key in sorted(agg, key=lambda k: (k.split("/")[0], k)):
        a = agg[key]
        indent = "　" * (key.count("/"))
        name = key.split("/")[-1]
        ext = "、".join(f"{e}×{c}" for e, c in a["ext"].most_common(3))
        mt = dt.datetime.fromtimestamp(a["mtime"]).strftime("%Y-%m-%d") if a["mtime"] else ""
        L.append(f"| {indent}{name} | {a['n']:,} | {human(a['size'])} | {ext} | {mt} |")

    L.append("\n## 三、站上電子圖書館（Supabase `ebooks`）\n")
    if eb is None:
        L.append(f"（未取得：{eberr}）")
    else:
        L.append(f"共 {len(eb):,} 本。\n")
        coll = Counter((r.get("collection") or "（一般）") for r in eb)
        L.append("依 collection：" + "、".join(f"{k} {v:,}" for k, v in coll.most_common()) + "\n")
        cat = Counter((r.get("category") or "（未分類）") for r in eb)
        L.append("| 類別 | 本數 |")
        L.append("|---|---:|")
        for k, v in cat.most_common():
            L.append(f"| {k} | {v:,} |")

    L.append("\n## 四、R2\n")
    if r2 is None:
        L.append(f"（未取得：{r2err}）")
    else:
        L.append("| 前綴 | 物件數 | 容量 |")
        L.append("|---|---:|---:|")
        for pre, (n, size, cut) in sorted(r2.items()):
            L.append(f"| `{pre}` | {'≥' if cut else ''}{n:,} | {human(size)} |")

    L.append("\n## 五、repo 研究資料索引（`public/content/research-data/`）\n")
    L.append("多半是**篇目**（書目 metadata），不是全文；全文在 R2 或 Drive。\n")
    L.append("| 檔案 | 筆數 |")
    L.append("|---|---:|")
    for rel, n in idx:
        L.append(f"| `{rel}` | {n:,} |")

    MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    SUMMARY.write_text(json.dumps({
        "generated": now.isoformat(timespec="seconds"),
        "drive_files": len(files),
        "folders": {k: {"n": v["n"], "size": v["size"]} for k, v in agg.items()},
        "ebooks": len(eb) if eb is not None else None,
        "r2": {k: v[0] for k, v in (r2 or {}).items()},
        "topic_inventories": [r for r, _ in inv],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    if eb is not None:
        (OUT_DIR / "ebooks_titles.tsv").write_text(
            "\n".join(f"{r.get('title','')}\t{r.get('category','')}\t{r.get('subcategory','')}\t{r.get('collection','')}" for r in eb),
            encoding="utf-8")
    print(f"✓ {MD.relative_to(ROOT)}　Drive {len(files):,} 檔　ebooks {len(eb) if eb else '—'}　R2 {len(r2 or {})} 前綴")


def find(terms):
    if not FILES_TSV.exists():
        sys.exit("先跑一次不帶 --find 的完整盤點，產生 output/holdings/files.tsv")
    age = (time.time() - FILES_TSV.stat().st_mtime) / 86400
    print(f"（Drive 檔案清單是 {age:.1f} 天前產生的；太舊就先重跑盤點）\n")
    lines = FILES_TSV.read_text(encoding="utf-8").splitlines()
    eb = (OUT_DIR / "ebooks_titles.tsv")
    eb_lines = eb.read_text(encoding="utf-8").splitlines() if eb.exists() else []
    idx_root = ROOT / "public" / "content" / "research-data"
    for t in terms:
        print(f"══ {t}")
        hits = [l for l in lines if t in l.split("\t")[0]]
        print(f"  Drive 檔名：{len(hits)} 筆")
        for h in hits[:25]:
            path, size, day = h.split("\t")
            print(f"    {path}　{human(int(size))}　{day}")
        if len(hits) > 25:
            print(f"    …（另 {len(hits) - 25} 筆）")
        ehits = [l for l in eb_lines if t in l.split("\t")[0]]
        print(f"  站上電子圖書館書名：{len(ehits)} 筆")
        for h in ehits[:15]:
            print("    " + h.replace("\t", "　"))
        ihits = []
        for p in idx_root.rglob("*.json"):
            try:
                c = p.read_text(encoding="utf-8").count(t)
            except Exception:  # noqa: BLE001
                continue
            if c:
                ihits.append((c, str(p.relative_to(ROOT)).replace("\\", "/")))
        print(f"  repo 索引（篇目）：{len(ihits)} 個檔")
        for c, p in sorted(ihits, reverse=True)[:10]:
            print(f"    {p}　出現 {c} 次")
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--find", nargs="+")
    ap.add_argument("--skip-r2", action="store_true")
    a = ap.parse_args()
    if a.find:
        find(a.find)
    else:
        build(skip_r2=a.skip_r2)
