#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""天主教在線（ziliaozhan.win）PDF 專區的**書目**普查。

只讀目錄頁，抓標題與站內連結——不下載任何 PDF。用途有二：
  1. 跟《基督教大藏經》既有書目比對，找出「藏經有、這裡也有」的交集
  2. 整份書目餵大藏經分類器，看漢語天主教文獻裡還缺哪些原典

  python scripts/zlz_catalog.py            # 走 79 頁 → c:/tmp/zlz_catalog.json
  python scripts/zlz_catalog.py --report   # 讀既有清單出統計

站點分類：文獻 wenxian／神學 shenxue／哲學 zhexue／研究 yanjiu／聖經 shengjing
          歷史 lishi／傳記 zhuanji／靈修 lingxiu／辭典 cidian／其他 qita
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE = "https://ziliaozhan.win"
OUT = Path("c:/tmp/zlz_catalog.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DELAY = 1.5
PAGES = 79

CAT_ZH = {
    "wenxian": "文獻", "shenxue": "神學", "zhexue": "哲學", "yanjiu": "研究",
    "shengjing": "聖經", "lishi": "歷史", "zhuanji": "傳記", "lingxiu": "靈修",
    "cidian": "辭典", "qita": "其他",
}
# 條目連結：/download/pdf/{cat}/{yyyy-mm-dd}/{id}.html，標題在錨點文字裡
ITEM_RX = re.compile(
    r'href="(/download/pdf/([a-z]+)/([\d-]+)/(\d+)\.html)"[^>]*>([^<]{2,200})<')


def fetch(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60, verify=False)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def scrape() -> list[dict]:
    seen: dict[str, dict] = {}
    for i in range(1, PAGES + 1):
        url = f"{BASE}/download/pdf/" if i == 1 else f"{BASE}/download/pdf/index_{i}.html"
        try:
            html = fetch(url)
        except Exception as e:  # noqa: BLE001 — 單頁失敗不中斷整份普查
            print(f"  ⚠ 第 {i} 頁：{e}", flush=True)
            continue
        n0 = len(seen)
        for path, cat, date, rid, title in ITEM_RX.findall(html):
            t = re.sub(r"\s+", " ", title).strip()
            if not t or rid in seen:
                continue
            seen[rid] = {"id": rid, "title": t, "category": cat,
                         "category_zh": CAT_ZH.get(cat, cat), "date": date,
                         "url": BASE + path}
        print(f"  第 {i}/{PAGES} 頁 +{len(seen) - n0}（累計 {len(seen)}）", flush=True)
        time.sleep(DELAY)
    return list(seen.values())


def report(rows: list[dict]) -> None:
    print(f"\n書目 {len(rows)} 筆\n")
    c = Counter(r["category_zh"] for r in rows)
    print(f"{'分類':<10}{'筆數':>7}")
    for k, n in c.most_common():
        print(f"  {k:<8}{n:>7}")
    yr = Counter((r["date"] or "")[:4] for r in rows)
    print("\n上架年份：", ", ".join(f"{y}:{n}" for y, n in sorted(yr.items()) if y))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        rows = json.loads(OUT.read_text(encoding="utf-8"))
    else:
        import urllib3
        urllib3.disable_warnings()
        rows = scrape()
        OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n已寫 {OUT}")
    report(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
