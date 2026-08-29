# -*- coding: utf-8 -*-
"""國家圖書館「臺灣記憶」→「臺灣基督長老教會文獻」的**書目與目次**索引。

🚨 只收書目與目次，**不下載數位影像**：站上 444 件全部標記 DO_authorized=0、
頁面明寫「不開放授權」。書目資訊與目次屬公開檢索內容，可用來在到館前開好
調閱清單；數位影像另需向國圖申請授權，取得後再議。

用途：長老教會歷史檔案館（與南神黃彰輝紀念圖書館共構）庫房採閉架、須 2 個
工作天前申請、每人每次限 10 件——到館前必須先有清單。這份索引就是為此。

列表 API（從前台攔到的）：
  /ajax/list_articles2?collection=C_Presbyterian&page=N&page_limit=100
單件頁：/article?u=<uniID>&lang=chn（目次由 JS 產生，需瀏覽器取）

index：public/content/research-data/pct/tm-presbyterian-index.json

  python -X utf8 scripts/tm_presbyterian.py --list          # 只抓書目（快）
  python -X utf8 scripts/tm_presbyterian.py --toc [--limit N]  # 補目次（需 playwright）
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

BASE = "https://tm.ncl.edu.tw"
LIST_API = BASE + "/ajax/list_articles2"
COLLECTION = "C_Presbyterian"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"}
OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct/tm-presbyterian-index.json"


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("　", " ")).strip()


def item_url(uni_id: str) -> str:
    return f"{BASE}/article?u={uni_id}&lang=chn"


def fetch_list():
    rows, page = [], 1
    while True:
        r = requests.get(LIST_API, params={
            "lang": "chn", "collection": COLLECTION,
            "special_search": "overview_index", "page": page, "page_limit": 100,
        }, headers=UA, timeout=60)
        r.raise_for_status()
        p = r.json()["payload"]
        recs = p["records"]
        for x in recs:
            rows.append({
                "uniID": x["uniID"],
                "title": clean(x["mainTitle"]),
                "accessionNo": x.get("accessionNo") or "",
                "type": clean(x.get("collectionTypeChn") or ""),
                "topic": clean(x.get("topic") or ""),
                "keyword": clean(x.get("keyword") or ""),
                "year": x.get("year") or "",
                "authorized": bool(x.get("DO_authorized")),
                "url": item_url(x["uniID"]),
            })
        total = p["total_found"]
        print(f"  page {page}: +{len(recs)}，累計 {len(rows)}/{total}", flush=True)
        if len(rows) >= total or not recs:
            break
        page += 1
        time.sleep(0.3)
    return rows


def save(rows):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    withtoc = sum(1 for r in rows if r.get("toc"))
    print(f"{len(rows)} 件（{withtoc} 件有目次）→ {OUT}")


def cmd_list():
    rows = fetch_list()
    if OUT.exists():        # 保留既有目次，不要被書目重抓洗掉
        old = {r["uniID"]: r for r in json.loads(OUT.read_text(encoding="utf-8"))}
        for r in rows:
            if old.get(r["uniID"], {}).get("toc"):
                r["toc"] = old[r["uniID"]]["toc"]
    save(rows)
    n = sum(1 for r in rows if r["authorized"])
    print(f"其中開放授權 {n} 件——目前為 0，故本流程一律不取數位影像。")


# ── 目次 ────────────────────────────────────────────────────────────────
# 單件頁的目次由 JS 產生，requests 拿不到，要用瀏覽器。
# 版面上沒有「目次」標題也沒有專屬容器，目次就夾在
#   「<影像頁次>/<總頁數>」（例：1/338）  ←→  「數位物件瀏覽」
# 這兩個標記之間，只能用標記切。切不到就當這件沒有目次（不少單件本來就沒有）。
TOC_JS = r"""
import { chromium } from 'playwright'
const items = JSON.parse(process.argv[2])
const b = await chromium.launch()
const p = await b.newPage()
const out = []
for (const it of items) {
  try {
    await p.goto(it.url, { waitUntil: 'domcontentloaded', timeout: 90000 })
    await p.waitForTimeout(4500)
    out.push({ uniID: it.uniID, text: await p.locator('body').innerText() })
  } catch (e) {
    out.push({ uniID: it.uniID, text: '', error: String(e).slice(0, 100) })
  }
}
console.log(JSON.stringify(out))
await b.close()
"""
NODE_SCRIPT = Path(__file__).resolve().parent / ".tm_toc.mjs"
IMG_COUNT_RE = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s*$")


def slice_toc(text: str):
    """回傳 (目次列表, 影像總頁數)。抓不到就 ([], 0)。"""
    lines = [l.strip() for l in (text or "").split("\n")]
    start = total = None
    for i, l in enumerate(lines):
        m = IMG_COUNT_RE.match(l)
        if m:
            start, total = i + 1, int(m.group(2))
            break
    if start is None:
        return [], 0
    toc = []
    for l in lines[start:]:
        if "數位物件瀏覽" in l or l == "中文題名":
            break
        if l and l != "載入更多":
            toc.append(l)
    return toc, total


def cmd_toc(limit: int, batch: int = 40):
    rows = json.loads(OUT.read_text(encoding="utf-8"))
    todo = [r for r in rows if not r.get("toc") and not r.get("tocChecked")]
    if limit:
        todo = todo[:limit]
    print(f"待補目次 {len(todo)} 件（全庫 {len(rows)} 件）", flush=True)
    by_id = {r["uniID"]: r for r in rows}
    repo = Path(__file__).resolve().parents[1]
    NODE_SCRIPT.write_text(TOC_JS, encoding="utf-8")
    for i in range(0, len(todo), batch):
        chunk = [{"uniID": r["uniID"], "url": r["url"]} for r in todo[i:i + batch]]
        r = subprocess.run(["node", str(NODE_SCRIPT), json.dumps(chunk, ensure_ascii=False)],
                           cwd=repo, capture_output=True, text=True, encoding="utf-8", timeout=3600)
        if not r.stdout.strip():
            sys.stderr.write(r.stderr or "")
            print("  這批沒有回傳，跳過", flush=True)
            continue
        got = 0
        for res in json.loads(r.stdout):
            row = by_id.get(res["uniID"])
            if row is None:
                continue
            toc, total = slice_toc(res.get("text", ""))
            row["tocChecked"] = True          # 記下「查過了」，沒有目次的不必重查
            if toc:
                row["toc"] = toc
                got += 1
            if total:
                row["imageCount"] = total
        save(rows)
        print(f"  {i + len(chunk)}/{len(todo)}：本批 {got} 件有目次", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--toc", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.list:
        cmd_list()
    elif args.toc:
        cmd_toc(args.limit)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
