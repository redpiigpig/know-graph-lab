# -*- coding: utf-8 -*-
"""《基督教論壇報》收錄 pipeline（台灣福音派）。

進 /research-data 第五個 collection「台灣福音派研究資料」。論壇報 1965 年創刊，
是福音派系統最主要的教派報紙——與長老教會系統的《台灣教會公報》同文類、同年代，
所以放進語料層之後，同一議題（同志、廢死、性別平權、政教關係）在兩報的逐年曲線
可以直接並排，看出基督教內部的分裂而不只是「宗教界的結盟」。

站方是自寫 PHP：
  列表 news/3-2-2.php?main_cat=M&cat=C&page=N   一頁 18 篇，翻到底會回預設頁
  單篇 news/3-3.php?cat=C&article=ID
文章 ID 不能遞增窮舉（無效 ID 一律回同一張預設頁），只能從列表逐頁取。
日期與作者只在列表頁上，單篇頁沒有，所以列表階段就要一併記下來。

同一網址形式混著兩種頁面：單篇文章，以及只有導言＋子篇連結的「專題」頁；
專題頁若當成一篇收進去會污染語料，靠子連結數判別。

R2：evangelical-fulltext/ct/<ID>.txt
index：public/content/research-data/evangelical/ct-index.json（各年篇數）

  python -X utf8 scripts/ct_forum.py --harvest [--max-pages 300]
  python -X utf8 scripts/ct_forum.py --process [--limit N]
  python -X utf8 scripts/ct_forum.py --publish
"""
import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

BASE = "https://ct.org.tw/html/news/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/ct_forum.json")
R2_TXT = "evangelical-fulltext/ct"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/evangelical/ct-index.json"
PER_PAGE = 18
DATE_RE = re.compile(r"(20\d{2}|19\d{2})-(\d{1,2})-(\d{1,2})")


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def get(url, params=None):
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=45)
            if 400 <= r.status_code < 500:
                return None
            r.raise_for_status()
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def categories(html: str):
    """→ [(main_cat, cat, 名稱)]，從任一列表頁的分類導覽取得。"""
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for a in soup.find_all("a", href=True):
        m = re.search(r"3-2-2\.php\?main_cat=(\d+)&cat=(\d+)", a["href"])
        name = clean(a.get_text())
        if m and name:
            out[(int(m.group(1)), int(m.group(2)))] = name
    return [(mc, c, n) for (mc, c), n in sorted(out.items())]


def parse_listing(html: str, cat: int):
    """→ [{id, date, author, title}]；日期與作者只在列表頁上。"""
    soup = BeautifulSoup(html, "html.parser")
    rows, seen = [], set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"3-3\.php\?cat=(\d+)&article=(\d{5,})", a["href"])
        if not m:
            continue
        aid = int(m.group(2))
        title = clean(a.get_text())
        if not title or aid in seen:
            continue
        seen.add(aid)
        par = a.find_parent(["li", "div", "tr", "td"])
        blob = clean(par.get_text(" ")) if par else ""
        md = DATE_RE.search(blob)
        date = f"{md.group(1)}-{int(md.group(2)):02d}-{int(md.group(3)):02d}" if md else ""
        rows.append({"id": aid, "cat": int(m.group(1)), "date": date, "title": title})
    return rows


def harvest(max_pages=300):
    first = get(BASE + "3-2-2.php", {"main_cat": 1, "cat": 10, "page": 1})
    cats = categories(first)
    print(f"分類 {len(cats)} 個", flush=True)

    arts = {}
    if HARVEST.exists():
        arts = {r["id"]: r for r in json.loads(HARVEST.read_text(encoding="utf-8"))}
    for mc, c, name in cats:
        seen_before = len(arts)
        page1_ids = None
        for page in range(1, max_pages + 1):
            html = get(BASE + "3-2-2.php", {"main_cat": mc, "cat": c, "page": page})
            if not html:
                break
            rows = parse_listing(html, c)
            ids = {r["id"] for r in rows}
            for r in rows:
                arts.setdefault(r["id"], r)
            # 終止條件只看「這一頁還是不是真的列表頁」，不能看「有沒有新文章」——
            # 續跑時前幾頁本來就都收過了，用新舊判斷會一開頁就誤判到底。
            if page == 1:
                page1_ids = ids
            elif ids == page1_ids or len(rows) < PER_PAGE // 2:
                break      # 翻過頭時站方回的是預設頁，內容與第一頁相同
            time.sleep(0.35)
        print(f"  {name}（cat={c}）：+{len(arts) - seen_before}，累計 {len(arts)}", flush=True)
        HARVEST.write_text(json.dumps(sorted(arts.values(), key=lambda r: -r["id"]),
                                      ensure_ascii=False, indent=1), encoding="utf-8")

    rows = sorted(arts.values(), key=lambda r: -r["id"])
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    years = Counter(r["date"][:4] for r in rows if r["date"])
    print(f"\n共 {len(rows)} 篇；有日期 {sum(years.values())}，年代 "
          f"{min(years) if years else '-'}–{max(years) if years else '-'}")


def article_text(html: str):
    """→ (內文, 是否為專題頁)。專題頁只有導言＋一串子篇連結，不能當一篇文章收。

    每一篇文章頁的側欄本來就固定掛著 8–9 條「相關文章」，所以不能單看子連結數——
    那會把 2,000 多字的正常報導也判成專題頁（實測誤殺 8,960 篇）。專題頁的特徵是
    子連結明顯多於側欄常數，且正文極短。
    """
    soup = BeautifulSoup(html, "html.parser")
    sub_links = len({m.group(0) for a in soup.find_all("a", href=True)
                     for m in [re.search(r"article=\d{5,}", a["href"])] if m})
    for tag in soup(["script", "style"]):
        tag.decompose()
    lines = [clean(x) for x in soup.get_text("\n").split("\n")]
    lines = [l for l in lines if len(l) > 15 and not l.startswith('" class=')]
    body = "\n".join(lines)
    return body, sub_links >= 14 and len(body) < 1200


def process(limit=0):
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    done = skip = topic = fail = 0
    for r in rows:
        key = f"{R2_TXT}/{r['id']}.txt"
        if key in have:
            skip += 1
            continue
        try:
            html = get(BASE + "3-3.php", {"cat": r["cat"], "article": r["id"]})
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"  ! {r['id']}: {e}", flush=True)
            continue
        if not html:
            skip += 1
            continue
        body, is_topic = article_text(html)
        if is_topic:
            topic += 1
            continue
        if len(body) < 300:
            skip += 1
            continue
        r["chars"] = len(body)
        df.r2_put_text(key, body)
        done += 1
        if done % 200 == 0:
            print(f"  …已處理 {done} 篇", flush=True)
            HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        if limit and done >= limit:
            break
        time.sleep(0.3)
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n新增 {done}、專題頁略過 {topic}、其他略過 {skip}、失敗 {fail}", flush=True)


def backfill_chars():
    """補回 chars 欄。

    --process 中途被中斷時，最後那批已經上傳 R2、卻還沒寫回 harvest 的篇目會缺
    chars；而重跑 --process 只會因為「R2 已有」把它們跳過，chars 永遠補不回來，
    /research-data 上的字數就一路少算。這裡直接從 R2 讀回長度。
    """
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    todo = [r for r in rows
            if f"{R2_TXT}/{r['id']}.txt" in have and not r.get("chars")]
    print(f"缺 chars 的篇目：{len(todo)}", flush=True)
    for i, r in enumerate(todo, 1):
        obj = df.s3.get_object(Bucket=df.R2_BUCKET, Key=f"{R2_TXT}/{r['id']}.txt")
        r["chars"] = len(obj["Body"].read().decode("utf-8"))
        if i % 100 == 0:
            print(f"  …已補 {i}/{len(todo)}", flush=True)
            HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"補回 {len(todo)} 篇的字數", flush=True)


def publish():
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    by_year = {}
    for r in rows:
        if f"{R2_TXT}/{r['id']}.txt" not in have:
            continue
        by_year.setdefault(r["date"][:4] or "未標年", []).append(r)
    out = [{"year": y, "count": len(v), "chars": sum(x.get("chars", 0) for x in v)}
           for y, v in sorted(by_year.items(), reverse=True)]
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    # 篇目清單（不含全文）另存一份給頁面用；只留有全文的，避免點開全是空的
    arts = [{"id": r["id"], "cat": r["cat"], "date": r["date"], "title": r["title"]}
            for r in rows if f"{R2_TXT}/{r['id']}.txt" in have]
    arts.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
    (INDEX_OUT.parent / "ct-articles.json").write_text(
        json.dumps(arts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} 年 / {sum(x['count'] for x in out)} 篇 → {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--backfill-chars", action="store_true",
                    help="--process 被中斷後補回缺漏的字數")
    ap.add_argument("--max-pages", type=int, default=300)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.harvest:
        harvest(args.max_pages)
    if args.process:
        process(args.limit)
    if args.backfill_chars:
        backfill_chars()
    if args.publish:
        publish()
    if not (args.harvest or args.process or args.publish or args.backfill_chars):
        ap.print_help()


if __name__ == "__main__":
    main()
