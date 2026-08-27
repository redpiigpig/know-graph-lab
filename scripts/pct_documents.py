# -*- coding: utf-8 -*-
"""台灣基督長老教會總會「重要文獻」收錄 pipeline。

三大聲明（1971〈對國是的聲明與建議〉、1975〈我們的呼籲〉、1977〈人權宣言〉）、
1985〈台灣基督長老教會信仰告白〉，以及歷年總會的牧函、宣言與聲明——這批是
博論第四章第一節「從自立到實況：公共性的體制條件」的直接文本。

站上是 ab_doc.aspx?DocID=N，N 不連續且無效值會回 ASP.NET 錯誤頁（約 672 字的
固定樣板），所以用「長度＋錯誤字串」兩道判斷濾掉，不能只看 HTTP 200。

R2：pct-fulltext/pct-documents/<DocID>.txt
index：public/content/research-data/pct/documents-index.json

  python -X utf8 scripts/pct_documents.py --scan [--from 1 --to 200]
  python -X utf8 scripts/pct_documents.py --publish
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

URL = "https://www.pct.org.tw/ab_doc.aspx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/pct_documents.json")
R2_TXT = "pct-fulltext/pct-documents"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct/documents-index.json"

ERROR_MARK = "應用程式中發生伺服器錯誤"
MIN_CHARS = 300


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def get(url, params=None):
    """無效 DocID 站方回 500（不是 404 也不是錯誤樣板），視同「沒有這一件」回 None，
    不重試——否則掃 200 個號碼光是空轉退避就要好幾分鐘。"""
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=45, verify=False)
            if r.status_code in (404, 500):
                return None
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def parse_doc(html: str):
    """→ (標題, 年份, 內文)；不是有效文獻頁就回 (None, '', '')。"""
    if not html or ERROR_MARK in html:
        return None, "", ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    lines = [clean(x) for x in soup.get_text("\n").split("\n")]
    # 版面殘留的 CSS 片段（width: 182px 之類）不是內文
    lines = [l for l in lines if len(l) > 8 and not re.match(r"^[a-z-]+\s*:", l)]
    if not lines:
        return None, "", ""
    body = "\n".join(lines)
    if len(body) < MIN_CHARS:
        return None, "", ""

    # 第一行是 <title>「文獻名 - 關於我們 - 台灣基督長老教會」，第二行多為文獻名
    title = ""
    for l in lines[:4]:
        cand = l.split(" - ")[0].strip()
        if cand and "台灣基督長老教會" != cand and len(cand) < 60:
            title = cand
            break
    m = re.search(r"(19\d{2}|20\d{2})", title) or re.search(r"(19\d{2}|20\d{2})", body[:400])
    return title or lines[0][:50], (m.group(1) if m else ""), body


def scan(lo, hi):
    rows = {}
    if HARVEST.exists():
        rows = {r["docId"]: r for r in json.loads(HARVEST.read_text(encoding="utf-8"))}
    found = 0
    for n in range(lo, hi + 1):
        try:
            title, year, body = parse_doc(get(URL, {"DocID": n}))
        except Exception as e:  # noqa: BLE001
            print(f"  ! DocID={n}: {e}", flush=True)
            continue
        if not title:
            continue
        rows[n] = {"docId": n, "title": title, "year": year, "chars": len(body),
                   "source": f"{URL}?DocID={n}"}
        df.r2_put_text(f"{R2_TXT}/{n}.txt", body)
        found += 1
        print(f"  ✓ {n:>4}  {year or '—':<5} {title[:44]} （{len(body):,} 字）", flush=True)
        time.sleep(0.4)
    out = sorted(rows.values(), key=lambda r: r["docId"])
    HARVEST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n本輪新增／更新 {found}，累計 {len(out)} 件 → {HARVEST}")


def publish():
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    out = [{**r, "textKey": f"{R2_TXT}/{r['docId']}.txt"}
           for r in rows if f"{R2_TXT}/{r['docId']}.txt" in have]
    out.sort(key=lambda r: (r["year"] or "0000", r["docId"]), reverse=True)
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} 件 → {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--from", dest="lo", type=int, default=1)
    ap.add_argument("--to", dest="hi", type=int, default=200)
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    if args.scan:
        scan(args.lo, args.hi)
    if args.publish:
        publish()
    if not (args.scan or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
