# -*- coding: utf-8 -*-
"""《國度復興報》收錄 pipeline —— 走 Wayback，不走活站。

財團法人國度復興傳播基金會（楊寧亞牧師）2002 年創刊，靈恩／復興系統，
在護家與同志運動議題上發聲最積極，是論文第六章議題結盟那一章的對照組
（長老教會、福音派論壇報、復興系統三方對同一議題的分歧）。

🚨 **活站兩個網域都取不到內容**（2026-08 實測，含真瀏覽器）：
   - krtnews.tw（舊站，版權 2016）：單篇頁只吐標題與日期，正文一個字都沒有；
     各分類的「列表頁」全部回同一批 35 篇（交集 35/35），也沒有分頁
   - www.krtnews.com.tw（現行站）：單篇 item 頁一律 HTTP 404 空白，
     連 Playwright 開也一樣；列表的 ?start=N 分頁是死的（每頁都回同一批 23 篇）
   所以**不要再試著爬活站**，那是死路，兩邊都驗過了。

改走 Internet Archive：那些快照是網站還活著時抓的，帶完整正文。
CDX 查到 krtnews.tw 11,170 筆、krtnews.com.tw 4,102 筆文章頁快照（2012–2026）。

🚨 取 Wayback 一律加 `id_` 後綴（`/web/<ts>id_/<url>`），拿的才是原始頁面，
   不然會混進 Wayback 自己注入的工具列與改寫過的連結。
🚨 Wayback 是非營利站，逐筆之間一定要留延遲，不要平行灌。

R2：evangelical-fulltext/krt/<年>.jsonl（按年打包，不逐篇一個小檔）
index：public/content/research-data/evangelical/krt-index.json
       public/content/research-data/evangelical/krt-articles.json

  python -X utf8 scripts/press_krt.py --harvest          # 從 CDX 建快照清單
  python -X utf8 scripts/press_krt.py --process [--limit N]
  python -X utf8 scripts/press_krt.py --publish
"""
import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

DOMAINS = ["krtnews.tw", "krtnews.com.tw"]
CDX = ("https://web.archive.org/cdx/search/cdx?url={dom}*&output=json"
       "&fl=original,timestamp&collapse=urlkey&limit=60000")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/krt_wayback.json")
R2_PREFIX = "evangelical-fulltext/krt"
OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/evangelical"

ART_RE = re.compile(r"/(?:article|item)/(\d+)")
TITLE_TAIL = re.compile(r"\s*[-|｜]\s*國度復興報.*$")
DELAY = 4.0          # Wayback 是非營利站，而且會擋；放慢到四秒

# 🚨 **這批快照沒有可用的發布日期**，三種欄位都驗過（2026-08）：
#    - 站頭「2012年 08月14日 星期二 天氣：」＝今日天氣小工具，等於**快照當天**
#    - div.itemToolbar 的「2012-01-15, 週日 00:00」在**每一篇都一模一樣**，是站台固定值
#    - krtnews.tw 的 .date 三個值分別是快照日、與兩個在不同文章間重複的值
#    所以本 pipeline **完全不產生 date 欄位**，只存 capturedAt（快照日）並在頁面標明
#    那是「發布日的上限」。絕不拿快照日冒充發布日——那會讓年表看起來成立而其實是假的。


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=90)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            r.encoding = "utf-8"     # 站方沒宣告 charset，requests 會猜成 latin-1 而整頁亂碼
            return r.text
        except Exception as e:       # noqa: BLE001
            last = e
            time.sleep(2 ** i * 2)
    print(f"  ! {url[:80]}：{last}", flush=True)
    return None


def category_of(url: str) -> str:
    """分類就寫在路徑上（/chinese-church/local/article/N.html），不必解析頁面。"""
    m = re.search(r"krtnews(?:\.com)?\.tw(?::\d+)?/(.+?)/(?:article|item)/", url)
    return m.group(1) if m else ""


def harvest():
    rows = {}
    if HARVEST.exists():
        rows = {r["key"]: r for r in json.loads(HARVEST.read_text(encoding="utf-8"))}
    before = len(rows)
    for dom in DOMAINS:
        data = json.loads(get(CDX.format(dom=dom)) or "[]")
        body = data[1:] if data and data[0][0] == "original" else data
        n = 0
        for orig, ts in body:
            m = ART_RE.search(orig)
            if not m:
                continue
            # 同一篇可能有多個時間點的快照；CDX 已 collapse 過 urlkey，
            # 這裡再以「網域＋文章編號」為鍵，保留最早的那一次（最接近原貌）
            key = f"{dom}:{m.group(1)}"
            if key not in rows or ts < rows[key]["ts"]:
                rows[key] = {"key": key, "dom": dom, "id": m.group(1),
                             "url": orig, "ts": ts, "cat": category_of(orig)}
            n += 1
        print(f"  {dom}：CDX 文章頁 {n} 筆", flush=True)
    HARVEST.parent.mkdir(parents=True, exist_ok=True)
    HARVEST.write_text(json.dumps(sorted(rows.values(), key=lambda r: r["key"]),
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n去重後 {len(rows)} 篇（新增 {len(rows) - before}）→ {HARVEST}")


def parse_article(html: str):
    """→ (標題, 內文)。抓不到內文就回 None，交給呼叫端計為失敗。

    刻意不回日期：見檔頭，這批快照沒有可信的發布日期。
    """
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    title = ""
    if soup.title:
        title = TITLE_TAIL.sub("", clean(soup.title.get_text())).strip()
    # 正文＝夠長的 <p> 串起來。這站的側欄全是短連結列，長段落只會是內文。
    paras = [clean(p.get_text(" ")) for p in soup.find_all("p")]
    body = chr(10).join(p for p in paras if len(p) >= 40)
    return (title, body) if len(body) >= 120 else (title, None)


def process(limit=0):
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    done = skip = fail = 0
    for r in rows:
        if r.get("chars"):
            skip += 1
            continue
        html = get(f"https://web.archive.org/web/{r['ts']}id_/{r['url']}")
        if not html:
            fail += 1
            continue
        title, body = parse_article(html)
        if not body:
            r["chars"] = 0          # 記下來，下一輪不必再抓
            fail += 1
            continue
        ts = r["ts"]
        r.update(title=title, capturedAt=f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
                 chars=len(body), text=body)
        done += 1
        if done % 100 == 0:
            print(f"  …已處理 {done}（失敗 {fail}）", flush=True)
            HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        if limit and done >= limit:
            break
        time.sleep(DELAY)
    HARVEST.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n新增 {done}、已有略過 {skip}、失敗 {fail}", flush=True)


def publish():
    """打包上 R2 並產 index。

    分桶用的是**快照年**不是發布年——這批沒有可信的發布日期（見檔頭）。
    欄位一律叫 capturedAt／capturedYear，不留任何叫 date/year 的東西，
    免得日後有人拿去當發布日排年表。
    """
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = [r for r in rows if r.get("text")]
    # 兩個網域收了同一篇的情況：同題同字數視為重複，留快照較早的那一份
    best = {}
    for r in have:
        k = (r.get("title", ""), r["chars"])
        if k not in best or r["ts"] < best[k]["ts"]:
            best[k] = r
    uniq = sorted(best.values(), key=lambda r: (r["ts"], r["key"]))

    by_year, arts = defaultdict(list), []
    for r in uniq:
        by_year[r["capturedAt"][:4]].append(r)
        arts.append({"id": r["key"], "cat": r["cat"], "capturedAt": r["capturedAt"],
                     "title": r.get("title", ""), "chars": r["chars"]})
    index = []
    for y in sorted(by_year):
        items = by_year[y]
        body = chr(10).join(json.dumps(
            {"id": x["key"], "cat": x["cat"], "capturedAt": x["capturedAt"],
             "title": x.get("title", ""), "text": x["text"],
             "wayback": f"https://web.archive.org/web/{x['ts']}/{x['url']}"},
            ensure_ascii=False) for x in items)
        df.r2_put_text(f"{R2_PREFIX}/{y}.jsonl", body)
        index.append({"capturedYear": y, "count": len(items),
                      "chars": sum(x["chars"] for x in items)})
        print(f"  快照 {y}：{len(items)} 篇 / {sum(x['chars'] for x in items):,} 字", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "krt-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "krt-articles.json").write_text(json.dumps(arts, ensure_ascii=False, indent=1), encoding="utf-8")
    print("")
    print(f"{len(uniq)} 篇（去重前 {len(have)}）/ {sum(x['chars'] for x in index):,} 字 → {OUT}")


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
