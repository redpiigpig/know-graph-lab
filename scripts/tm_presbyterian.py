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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        cmd_list()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
