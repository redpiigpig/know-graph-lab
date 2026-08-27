# -*- coding: utf-8 -*-
"""《妙心雜誌》收錄 pipeline（台南妙心寺 mst.org.tw，靜態 Big5 HTML，純 requests）。

進「印順學派與弘誓研究資料」collection 的「妙心雜誌」子站。創刊於民國85年（1996），
雙月刊。站上每篇一個 HTML，另有兩種索引：26 個專欄頁（跨期）與各期目次頁 indexN.htm。
兩邊都爬、以 URL 去重，才不會漏掉只出現在其中一邊的篇目。

沒有 PDF、沒有掃描檔，所以不需要 OCR——全文直接由 HTML 取出。

R2：yinshun-hongshi-fulltext/妙心雜誌/<slug>.txt（全文；原始 HTML 體積小，一併留 Drive）
Drive canonical：G:\\…\\印順學派與弘誓\\妙心雜誌\\
index：public/content/research-data/yinshun-hongshi/miaoxin-index.json

  python -X utf8 scripts/mst_magazine.py --harvest            # 專欄頁+各期目次 → 篇目清單
  python -X utf8 scripts/mst_magazine.py --process [--limit N]  # 抓 HTML+抽全文+上傳(冪等)
  python -X utf8 scripts/mst_magazine.py --publish            # 建 index.json
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402  reuse .env / s3 client

ROOT = "http://www.mst.org.tw/"
INDEX_URL = ROOT + "MiauCim-bak/magazine.htm"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/mst_magazine.json")
STAGE = Path(r"C:/tmp/mst_dl"); STAGE.mkdir(parents=True, exist_ok=True)
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\妙心雜誌")
R2_TXT = "yinshun-hongshi-fulltext/妙心雜誌"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/yinshun-hongshi/miaoxin-index.json"

# 站上檔案一律 Big5；少數頁面混入 UTF-8 或壞字，decode 一律 replace 不中斷。
ENCODINGS = ("big5hkscs", "big5", "utf-8")


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def decode(raw: bytes) -> str:
    for enc in ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("big5", "replace")


def get(url: str) -> bytes:
    last = None
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=45)
            r.raise_for_status()
            return r.content
        except Exception as e:  # noqa: BLE001  站在自架主機上，偶有斷線
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


# ── 純函式：從 URL 猜期數與篇名（檔名形如 214-法句經講記（九十三）.htm）────────
ISSUE_RE = re.compile(r"/(\d{1,3})[-\uff0d]([^/]+)\.html?$", re.I)
# \u5c08\u6b04\u9801\u7684\u9023\u7d50\u6587\u5b57\u662f\u671f\u5225\u6a19\u7c64\uff1a\u300c214\u671f115.7.1\u300d\u300c\u7b2c214\u671f115.07.01\u300d\u3002
LABEL_RE = re.compile(r"^\u7b2c?\s*(\d{1,3})\s*\u671f")


def parse_article_url(url: str):
    """回傳 (issue:int|None, title:str)。檔名不合慣例時 issue 為 None、標題取檔名。"""
    path = unquote(url)
    m = ISSUE_RE.search(path)
    if m:
        return int(m.group(1)), clean(m.group(2))
    name = path.rsplit("/", 1)[-1]
    return None, clean(re.sub(r"\.html?$", "", name, flags=re.I))


def slug_for(url: str) -> str:
    """R2/Drive 檔名：期數-標題-雜湊，避免同名不同期互蓋。"""
    issue, title = parse_article_url(url)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    safe = re.sub(r'[\\/:*?"<>|]', "_", title)[:60]
    return f"{issue or 0:03d}-{safe}-{digest}"


def is_article(url: str) -> bool:
    low = unquote(url).lower()
    if not low.endswith((".htm", ".html")):
        return False
    name = low.rsplit("/", 1)[-1]
    if name.startswith("index") or name.endswith("目次.htm"):
        return False
    return "/magazine/" in low


# ── harvest ───────────────────────────────────────────────────────────────
def links_of(html: str, base: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        out.append((urljoin(base, href), clean(a.get_text())))
    return out


def harvest():
    root_html = decode(get(INDEX_URL))
    pages, seen = [], set()
    for url, label in links_of(root_html, INDEX_URL):
        if url.lower().endswith((".htm", ".html")) and url not in seen:
            seen.add(url)
            pages.append((url, label))
    print(f"索引頁 {len(pages)} 個（26 專欄 + 各期目次）")

    articles = {}
    for i, (page, label) in enumerate(pages, 1):
        try:
            html = decode(get(page))
        except Exception as e:  # noqa: BLE001  單頁失敗不該中斷整批
            print(f"  ! {label or page}: {e}")
            continue
        for url, text in links_of(html, page):
            url = url.split("#")[0]
            if not is_article(url) or url in articles:
                continue
            issue, title = parse_article_url(url)
            # 專欄頁的連結文字是期別標籤（「210期114.11.1」）而非篇名——那種情況
            # 標題要回頭取檔名，期數則由標籤補上（舊檔名沒有 NNN- 前綴）。
            m = LABEL_RE.match(text)
            if m:
                issue = issue or int(m.group(1))
            elif text:
                title = clean(text)
            articles[url] = {
                "url": url,
                "issue": issue,
                "title": title,
                "column": label if "index" not in page.rsplit("/", 1)[-1] else "",
            }
        if i % 20 == 0:
            print(f"  …{i}/{len(pages)} 頁，累計 {len(articles)} 篇")
        time.sleep(0.25)

    rows = sorted(articles.values(), key=lambda r: (-(r["issue"] or 0), r["title"]))
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    issues = sorted({r["issue"] for r in rows if r["issue"]})
    print(f"共 {len(rows)} 篇，期數 {min(issues)}–{max(issues)}（{len(issues)} 期） → {HARVEST}")


# ── process ───────────────────────────────────────────────────────────────
def article_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    lines = [clean(x) for x in soup.get_text("\n").split("\n")]
    return "\n".join(l for l in lines if l)


def process(limit=None):
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    DRIVE.mkdir(parents=True, exist_ok=True)
    done = skipped = failed = 0
    for row in rows:
        slug = slug_for(row["url"])
        key = f"{R2_TXT}/{slug}.txt"
        if key in have:
            skipped += 1
            continue
        if limit is not None and done >= limit:
            break
        try:
            raw = get(row["url"])
        except Exception as e:  # noqa: BLE001
            print(f"  ! {row['title']}: {e}")
            failed += 1
            continue
        html = decode(raw)
        text = article_text(html)
        if len(text) < 120:  # 目次殘頁／空殼，不入庫
            skipped += 1
            continue
        (DRIVE / f"{slug}.htm").write_bytes(raw)
        df.r2_put_text(key, text)
        row["chars"] = len(text)
        done += 1
        if done % 25 == 0:
            print(f"  …已處理 {done} 篇")
        time.sleep(0.25)
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"新增 {done}、既有/略過 {skipped}、失敗 {failed}")


# ── publish ───────────────────────────────────────────────────────────────
def publish():
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    by_issue = {}
    for row in rows:
        slug = slug_for(row["url"])
        if f"{R2_TXT}/{slug}.txt" not in have:
            continue
        issue = row["issue"] or 0
        by_issue.setdefault(issue, []).append({
            "title": row["title"],
            "column": row.get("column") or "",
            "textKey": f"{R2_TXT}/{slug}.txt",
            "source": row["url"],
        })
    out = [{"issue": str(i), "articles": sorted(a, key=lambda x: x["title"])}
           for i, a in sorted(by_issue.items(), reverse=True)]
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} 期 / {sum(len(x['articles']) for x in out)} 篇 → {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--limit", type=int)
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
