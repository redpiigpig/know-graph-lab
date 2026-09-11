#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從 DOAJ（開放取用期刊指南）收宗教與神學類期刊的篇目。

**為什麼先做這個**：玄奘訂的那些庫（ProQuest、Project MUSE、De Gruyter…）全都綁
校內 IP，而排程下載那條線最要命的問題是「唯一有用的時機是人在學校，那時筆電用電池，
工作排程器預設不啟動」——兩邊永遠錯開（[[research-data-airiti]] 記過這個坑）。
**DOAJ 完全開放、不綁 IP、有公開 API**，是唯一能無條件自動化的一項。

收錄範圍按 LCC 分類：

    Religions. Mythology. Rationalism ／ Religion (General) ／ Christianity ／
    The Bible ／ Doctrinal Theology ／ Practical Theology ／ Christian Denominations ／
    Judaism ／ Islam. Bahai Faith. Theosophy, etc. ／ Buddhism

⚠️ **API 不吃萬用字元**：`bibjson.subject.code:BR*` 一律回 400
（“Query contains disallowed Lucene features”）。要用加引號的完整分類詞或完整碼。

存放：
  期刊清單  `data/research-data/doaj-journals.json`（進版控，兩百多筆，小）
  篇目      Drive `知識圖工作室/_corpus/doaj/<issn>.jsonl`（大，不進 git）
  網站索引  `public/content/research-data/contemporary-theology/doaj.json`（進版控）

用法：
  python scripts/doaj_harvest.py --journals            # 建／更新期刊清單
  python scripts/doaj_harvest.py --articles --limit 5  # 先抓五刊試
  python scripts/doaj_harvest.py --articles            # 全抓（可重跑，會續傳）
  python scripts/doaj_harvest.py --index               # 產網站索引
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
JOURNALS = ROOT / "data" / "research-data" / "doaj-journals.json"
CORPUS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/doaj")
INDEX = ROOT / "public" / "content" / "research-data" / "contemporary-theology" / "doaj.json"

API = "https://doaj.org/api/v4/search"
UA = {"User-Agent": "kglab-research/1.0 (academic bibliography compilation)"}
DELAY = 1.2          # DOAJ 公開 API，別打太快
PAGE = 100           # API 上限

# LCC 分類詞 → 中文區名。這十個是 DOAJ 實際用得到的宗教類 LCC 詞。
SUBJECTS = {
    "Religions. Mythology. Rationalism": "宗教學總論／神話",
    "Religion (General)": "宗教（總類）",
    "Christianity": "基督教",
    "The Bible": "聖經研究",
    "Doctrinal Theology": "教義神學",
    "Practical Theology": "實踐神學",
    "Christian Denominations": "基督教各宗派",
    "Judaism": "猶太教",
    "Islam. Bahai Faith. Theosophy, etc.": "伊斯蘭／巴哈伊",
    "Buddhism": "佛教",
}


def get(path: str, query: str, page: int = 1, size: int = PAGE) -> dict:
    url = f"{API}/{path}/{urllib.parse.quote(query, safe='')}?page={page}&pageSize={size}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt < 3:
                time.sleep(3)
                continue
            raise
    return {}


def issn_of(bib: dict) -> str | None:
    for k in ("pissn", "eissn"):
        if bib.get(k):
            return bib[k]
    for x in bib.get("identifier") or []:
        if x.get("type") in ("pissn", "eissn") and x.get("id"):
            return x["id"]
    return None


def harvest_journals() -> list[dict]:
    found: dict[str, dict] = {}
    for term, zh in SUBJECTS.items():
        q = f'bibjson.subject.term:"{term}"'
        page, total = 1, None
        while True:
            d = get("journals", q, page)
            total = d.get("total", 0)
            rows = d.get("results") or []
            for r in rows:
                b = r.get("bibjson") or {}
                issn = issn_of(b)
                if not issn:
                    continue
                rec = found.setdefault(issn, {
                    "issn": issn,
                    "title": b.get("title"),
                    "alt_title": b.get("alternative_title"),
                    "publisher": (b.get("publisher") or {}).get("name"),
                    "country": (b.get("publisher") or {}).get("country"),
                    "language": b.get("language") or [],
                    "start_year": b.get("oa_start"),
                    "homepage": next((x.get("url") for x in (b.get("ref") or {}).items()
                                      if False), None) or (b.get("ref") or {}).get("journal"),
                    "license": [x.get("type") for x in (b.get("license") or [])],
                    "lcc": sorted({s.get("term") for s in (b.get("subject") or [])
                                   if s.get("scheme") == "LCC" and s.get("term")}),
                    "areas": [],
                })
                if zh not in rec["areas"]:
                    rec["areas"].append(zh)
            if not rows or page * PAGE >= (total or 0):
                break
            page += 1
            time.sleep(DELAY)
        print(f"  {zh:14s} {total:>4} 種（累計不重複 {len(found)}）")
        time.sleep(DELAY)
    return sorted(found.values(), key=lambda x: (x["title"] or "").lower())


CAP = 1000     # DOAJ 的硬上限，見 fetch_range 的說明


def rows_of(d: dict) -> list[dict]:
    out = []
    for r in d.get("results") or []:
        b = r.get("bibjson") or {}
        out.append({
            "title": b.get("title"),
            "authors": [a.get("name") for a in (b.get("author") or []) if a.get("name")],
            "year": b.get("year"), "month": b.get("month"),
            "doi": next((x.get("id") for x in (b.get("identifier") or [])
                         if x.get("type") == "doi"), None),
            "url": next((x.get("url") for x in (b.get("link") or [])
                         if x.get("type") == "fulltext"), None),
            "abstract": (b.get("abstract") or "")[:1200],
            "keywords": b.get("keywords") or [],
        })
    return out


def page_through(q: str, total: int) -> list[dict]:
    out, page = [], 1
    while True:
        d = get("articles", q, page)
        got = rows_of(d)
        out += got
        if not got or page * PAGE >= min(total, CAP):
            return out
        page += 1
        time.sleep(DELAY)


def fetch_range(issn: str, lo: int, hi: int, warn: list) -> list[dict]:
    """抓某一刊某個年份區間的篇目，超過上限就把區間對半切。

    🚨 **DOAJ API 一個查詢最多只給 1000 筆**，第 11 頁（pageSize=100）直接回 400：
    “You cannot access results beyond 1000 records via this API.”
    照著分頁抓到出錯就停，會寫出一個剛好 1000 筆的檔案——數字整齊、程式不報錯、
    看起來完全正常，而 Acta Theologica 其實有 1355 篇，默默少了 355 篇。

    繞法是用 `bibjson.year:[lo TO hi]` 把查詢切小，切到每一段都在上限之內。
    二分比逐年掃省很多次請求（一刊多半三、五次就切完）。
    """
    q = f'issn:{issn} AND bibjson.year:[{lo} TO {hi}]'
    total = get("articles", q, 1, 1).get("total", 0)
    time.sleep(DELAY)
    if total == 0:
        return []
    if total <= CAP:
        return page_through(q, total)
    if lo >= hi:
        warn.append(f"{issn} {lo} 年單年就有 {total} 篇，超過 API 上限，只取得 {CAP} 篇")
        return page_through(q, CAP)
    mid = (lo + hi) // 2
    return fetch_range(issn, lo, mid, warn) + fetch_range(issn, mid + 1, hi, warn)


def harvest_articles(journals: list[dict], limit: int | None, force: bool) -> None:
    CORPUS.mkdir(parents=True, exist_ok=True)
    todo = journals[:limit] if limit else journals
    done = skipped = 0
    short = []
    for i, j in enumerate(todo, 1):
        out = CORPUS / f"{j['issn'].replace('/', '-')}.jsonl"
        # ⚠️ 續傳只看檔案在不在。這一批三百多刊，中途一定會被休眠或關機打斷
        # （[[feedback_laptop_sleeps_design_for_resume]]），不能設計成必須一次跑完。
        if out.exists() and out.stat().st_size > 2 and not force:
            skipped += 1
            continue
        warn: list[str] = []
        try:
            expect = get("articles", f'issn:{j["issn"]}', 1, 1).get("total", 0)
            time.sleep(DELAY)
            rows = fetch_range(j["issn"], 1800, 2030, warn)
        except Exception as e:
            print(f"[{i}/{len(todo)}] {j['issn']} 失敗 {type(e).__name__}")
            continue
        seen, uniq = set(), []
        for r in rows:
            k = (r["title"], r.get("doi"))
            if k in seen:
                continue
            seen.add(k); uniq.append(r)
        nl = chr(10)
        out.write_text(nl.join(json.dumps(r, ensure_ascii=False) for r in uniq) + nl,
                       encoding="utf-8")
        done += 1
        flag = ""
        if expect and len(uniq) < expect:
            # 沒繫年份的篇目落在區間外，這是正常的；差太多才是問題
            flag = f"  ⚠️ 館方總數 {expect}，實得 {len(uniq)}"
            short.append(f"{j['issn']} {j['title']}：{expect} → {len(uniq)}")
        print(f"[{i}/{len(todo)}] {(j['title'] or '')[:40]:42s} {len(uniq):>5} 篇{flag}")
        for w in warn:
            print(f"        ⚠️ {w}")
        time.sleep(DELAY)
    print(chr(10) + f"抓 {done} 刊／略過 {skipped} 刊（已抓過，用 --force 重抓）")
    if short:
        print(f"⚠️ 有 {len(short)} 刊實得少於館方總數（多半是篇目沒繫年份）：")
        for x in short[:10]:
            print(f"    {x}")


def build_index(journals: list[dict]) -> None:
    if not CORPUS.exists():
        print("⚠️ Drive 的 _corpus/doaj 不在（G: 沒掛載？），索引只會有期刊沒有篇數")
    rows, articles = [], 0
    for j in journals:
        f = CORPUS / f"{j['issn'].replace('/', '-')}.jsonl"
        n = sum(1 for _ in f.open(encoding="utf-8")) if f.exists() else 0
        articles += n
        rows.append({**j, "articles": n})
    rows.sort(key=lambda x: -x["articles"])
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({
        "source": "DOAJ API v4（開放取用，不需機構身分）",
        "subjects": SUBJECTS,
        "journals": len(rows), "articles": articles,
        "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"期刊 {len(rows)} 種、篇目 {articles:,} 篇 → {INDEX}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--journals", action="store_true")
    ap.add_argument("--articles", action="store_true")
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.journals:
        rows = harvest_journals()
        JOURNALS.parent.mkdir(parents=True, exist_ok=True)
        JOURNALS.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n{len(rows)} 種期刊 → {JOURNALS}")

    if args.articles or args.index:
        if not JOURNALS.exists():
            print("先跑 --journals")
            return 1
        js = json.loads(JOURNALS.read_text(encoding="utf-8"))
        if args.articles:
            harvest_articles(js, args.limit, args.force)
        if args.index:
            build_index(js)

    if not any([args.journals, args.articles, args.index]):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
