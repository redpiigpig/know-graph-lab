# -*- coding: utf-8 -*-
"""《台灣教會公報》新聞網（TCNN）收錄 pipeline。

進「台灣基督長老教會研究資料」collection。tcnn.org.tw 是 WordPress，REST API 未關，
逐篇連全文一起給，所以不需要解析版面、也不需要 OCR。

站上最早一篇是 2010-12-24；2008–2010 的紙本合刊在 Pubu 付費販售，不在本流程範圍。

抓取以「年」為窗口分頁（date_query 兩端），避開 WordPress 深分頁在數萬筆時的效能與
上限問題；每年一個 JSONL 存 R2，索引只留題名與日期，不把全文塞進 repo。

R2：pct-fulltext/tcnn/<年>.jsonl（每行一篇：id/date/title/link/categories/text）
index：public/content/research-data/pct/tcnn-index.json（各年篇數）
       public/content/research-data/pct/tcnn/<年>.json（該年題名清單）

  python -X utf8 scripts/pct_tcnn.py --fetch [--year 2015] [--limit-years N]
  python -X utf8 scripts/pct_tcnn.py --publish
"""
import argparse
import io
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402  reuse .env / s3 client

API = "https://tcnn.org.tw/wp-json/wp/v2/posts"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
FIRST_YEAR = 2010
R2_PREFIX = "pct-fulltext/tcnn"
CONTENT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct"
PER_PAGE = 100


def html_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    lines = [re.sub(r"\s+", " ", x).strip() for x in soup.get_text("\n").split("\n")]
    return "\n".join(l for l in lines if l)


def get_json(params):
    last = None
    for attempt in range(5):
        try:
            r = requests.get(API, params=params, headers=UA, timeout=60)
            if r.status_code == 400:      # 超出該窗口頁數 → 視為讀完
                return None
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(4 * (attempt + 1))
    raise last


def fetch_year(year: int):
    """該年全部文章（已抽純文字）。"""
    rows, page = [], 1
    while True:
        data = get_json({
            "per_page": PER_PAGE,
            "page": page,
            "orderby": "date",
            "order": "asc",
            "after": f"{year}-01-01T00:00:00",
            "before": f"{year + 1}-01-01T00:00:00",
            "_fields": "id,date,link,title,content,categories",
        })
        if not data:
            break
        for e in data:
            text = html_text(e.get("content", {}).get("rendered", ""))
            rows.append({
                "id": e["id"],
                "date": e["date"][:10],
                "title": html_text(e.get("title", {}).get("rendered", "")),
                "link": e.get("link", ""),
                "categories": e.get("categories", []),
                "text": text,
            })
        if len(data) < PER_PAGE:
            break
        page += 1
        time.sleep(0.3)
    return rows


def fetch(only_year=None, limit_years=None):
    this_year = datetime.now().year
    years = [only_year] if only_year else list(range(FIRST_YEAR, this_year + 1))
    if limit_years:
        years = years[:limit_years]
    have = df.r2_existing_keys(R2_PREFIX)
    for year in years:
        key = f"{R2_PREFIX}/{year}.jsonl"
        if key in have and year != this_year:   # 當年度仍在增修，一律重抓
            print(f"{year}：已有，略過")
            continue
        rows = fetch_year(year)
        if not rows:
            print(f"{year}：0 篇")
            continue
        buf = io.StringIO()
        for r in rows:
            buf.write(json.dumps(r, ensure_ascii=False) + "\n")
        df.r2_put_text(key, buf.getvalue())
        chars = sum(len(r["text"]) for r in rows)
        print(f"{year}：{len(rows)} 篇 / {chars:,} 字 → {key}", flush=True)


def publish():
    have = df.r2_existing_keys(R2_PREFIX)
    (CONTENT / "tcnn").mkdir(parents=True, exist_ok=True)
    summary = []
    for key in sorted(have):
        year = Path(key).stem
        body = df.s3.get_object(Bucket=df.R2_BUCKET, Key=key)["Body"].read().decode("utf-8")
        rows = [json.loads(l) for l in body.splitlines() if l.strip()]
        listing = [{"id": r["id"], "date": r["date"], "title": r["title"], "link": r["link"]} for r in rows]
        (CONTENT / "tcnn" / f"{year}.json").write_text(
            json.dumps(listing, ensure_ascii=False, indent=1), encoding="utf-8")
        summary.append({"year": year, "count": len(rows),
                        "chars": sum(len(r["text"]) for r in rows), "textKey": key})
    summary.sort(key=lambda x: x["year"], reverse=True)
    (CONTENT / "tcnn-index.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(summary)} 年 / {sum(x['count'] for x in summary)} 篇 → {CONTENT/'tcnn-index.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--year", type=int)
    ap.add_argument("--limit-years", type=int)
    args = ap.parse_args()
    if args.fetch:
        fetch(args.year, args.limit_years)
    if args.publish:
        publish()
    if not (args.fetch or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
