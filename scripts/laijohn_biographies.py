# -*- coding: utf-8 -*-
"""賴永祥長老史料庫「本土信徒」傳記收錄 pipeline。

進「台灣基督長老教會研究資料」collection。laijohn.com 是靜態 Big5 HTML、無反爬，
但站方是義務維護的個人史料庫，抓取一律加延遲、單執行緒。

站上把台灣本土信徒的略歷、訪問記、告別禮拜、回憶錄依人歸檔，路徑本身就帶人名
代碼：/archives/pc/<姓>/<姓,名>/<類別>/<檔>.htm，所以不必解析頁面就能歸戶。
博論第四章要用的王憲治、黃彰輝、宋泉盛相關傳記文章都在這一區。

R2：pct-fulltext/laijohn/<代碼>--<檔名>.txt
index：public/content/research-data/pct/laijohn-index.json（依人分組）

  python -X utf8 scripts/laijohn_biographies.py --harvest
  python -X utf8 scripts/laijohn_biographies.py --process [--limit N]
  python -X utf8 scripts/laijohn_biographies.py --publish
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

INDEX_URL = "http://www.laijohn.com/archives/pc-contents.htm"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/laijohn_pc.json")
R2_TXT = "pct-fulltext/laijohn"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct/laijohn-index.json"
DELAY = 0.5           # 義務維護的個人站，放慢一點
MIN_CHARS = 150


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def get(url: str):
    """回傳解好碼的 HTML；4xx 視同沒有這一頁回 None。"""
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=45)
            if 400 <= r.status_code < 500:
                return None
            r.raise_for_status()
            return r.content.decode("big5", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


# 路徑形如 /archives/pc/Ong/Ong,HTi/theology/Chng,Ngt.htm
PERSON_RE = re.compile(r"/archives/pc/[^/]+/([^/]+)/", re.I)


def person_of(url: str) -> str:
    m = PERSON_RE.search(unquote(url))
    return m.group(1) if m else "_"


def slug_for(url: str) -> str:
    tail = unquote(url).rsplit("/archives/pc/", 1)[-1]
    safe = re.sub(r'[\\/:*?"<>|,\s]+', "-", tail).rsplit(".", 1)[0][:70]
    return f"{safe}-{hashlib.sha1(url.encode()).hexdigest()[:6]}"


def harvest():
    html = get(INDEX_URL)
    arts = {}
    for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#"):
            continue
        url = urljoin(INDEX_URL, href).split("#")[0]
        if "/archives/pc/" not in url or not url.lower().endswith((".htm", ".html")):
            continue
        arts.setdefault(url, {"url": url, "person": person_of(url), "label": clean(a.get_text())})
    rows = sorted(arts.values(), key=lambda r: (r["person"], r["url"]))
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    people = len({r["person"] for r in rows})
    print(f"{len(rows)} 篇 / {people} 人 → {HARVEST}")


def page_text(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    title = clean(soup.title.get_text()) if soup.title else ""
    lines = [clean(x) for x in soup.get_text("\n").split("\n")]
    # 站上每頁底部固定掛著整組導覽連結，逐行過濾掉
    drop = {"Home", "English Home", "Japanese Entries", "New Entries 新進文章"}
    lines = [l for l in lines if len(l) > 4 and l not in drop]
    return title, "\n".join(lines)


def process(limit=0):
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    done = skip = fail = 0
    for r in rows:
        key = f"{R2_TXT}/{slug_for(r['url'])}.txt"
        if key in have:
            skip += 1
            continue
        try:
            html = get(r["url"])
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"  ! {r['label'][:24]}: {e}", flush=True)
            continue
        if html is None:
            skip += 1
            continue
        title, text = page_text(html)
        if len(text) < MIN_CHARS:
            skip += 1
            continue
        r["title"] = title or r["label"]
        r["chars"] = len(text)
        df.r2_put_text(key, text)
        done += 1
        if done % 100 == 0:
            print(f"  …已處理 {done} 篇", flush=True)
            HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        if limit and done >= limit:
            break
        time.sleep(DELAY)
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n新增 {done}、既有/略過 {skip}、失敗 {fail}", flush=True)


def publish():
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    by_person = {}
    for r in rows:
        key = f"{R2_TXT}/{slug_for(r['url'])}.txt"
        if key not in have:
            continue
        by_person.setdefault(r["person"], []).append({
            "title": r.get("title") or r["label"],
            "label": r["label"],
            "textKey": key,
            "source": r["url"],
        })
    out = [{"person": p, "articles": sorted(a, key=lambda x: x["title"])}
           for p, a in sorted(by_person.items())]
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} 人 / {sum(len(x['articles']) for x in out)} 篇 → {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.harvest:
        harvest()
    if args.process:
        process(args.limit)
    if args.publish:
        publish()
    if not (args.harvest or args.process or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
