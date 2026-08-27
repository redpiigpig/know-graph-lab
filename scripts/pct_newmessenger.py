# -*- coding: utf-8 -*-
"""長老教會「焚而不燬」信仰資源網（gospel.pct.org.tw）的雜誌收錄 pipeline。

進「台灣基督長老教會研究資料」collection。站上逐篇全文開放，版面是舊式 ASP.NET
表格，但內文固定包在 <td id="Zoom">，題名／欄目／作者各有 class，解析穩定。

同一套版面掛著數本刊物，用 strTID 區分——1 新使者、4 女宣雜誌、6 事工說明書。
各刊的 harvest／R2 前綴／index 檔名都由 --mag 決定。

期別用 strISID 直接遞增（1…最新期），比走分頁完整；每期目次頁列出該期各篇的
strMAGID，再逐篇取回。

R2：pct-fulltext/new-messenger/<期>-<MAGID>.txt
index：public/content/research-data/pct/new-messenger-index.json（期／篇名／作者）

  python -X utf8 scripts/pct_newmessenger.py --harvest [--mag lusoan] [--max-issue 210]
  python -X utf8 scripts/pct_newmessenger.py --process [--mag lusoan] [--limit N]
  python -X utf8 scripts/pct_newmessenger.py --publish [--mag lusoan]
"""
import argparse
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

BASE = "https://gospel.pct.org.tw/AssociatorMagazine.aspx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
MAGAZINES = {
    "new-messenger": {"tid": 1, "name": "新使者"},
    "lusoan": {"tid": 4, "name": "女宣雜誌"},
    "ministry": {"tid": 6, "name": "事工說明書"},
}
CONTENT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct"

# 由 --mag 設定，模組載入時先給預設值
MAG = "new-messenger"
TID = 1
HARVEST = Path(r"C:/tmp/pct_new-messenger.json")
R2_TXT = "pct-fulltext/new-messenger"
INDEX_OUT = CONTENT / "new-messenger-index.json"


def use(mag: str):
    """切換目標刊物：一次設定 strTID 與各路徑。"""
    global MAG, TID, HARVEST, R2_TXT, INDEX_OUT
    if mag not in MAGAZINES:
        raise SystemExit(f"--mag 只能是 {'/'.join(MAGAZINES)}")
    MAG = mag
    TID = MAGAZINES[mag]["tid"]
    HARVEST = Path(rf"C:/tmp/pct_{mag}.json")
    R2_TXT = f"pct-fulltext/{mag}"
    INDEX_OUT = CONTENT / f"{mag}-index.json"


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def get(url: str) -> str:
    last = None
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=60, verify=False)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def issue_url(isid: int) -> str:
    return f"{BASE}?strTID={TID}&strISID={isid}&strPageNo=1"


def article_url(isid: int, magid: str) -> str:
    return f"{BASE}?strTID={TID}&strISID={isid}&strMAGID={magid}"


def parse_issue(html: str, isid: int):
    """該期目次 → (期名, [(MAGID, 篇名)])。只取本期的連結，不含側欄推薦。"""
    soup = BeautifulSoup(html, "html.parser")
    title = ""
    for a in soup.find_all("a", href=True):
        if f"strISID={isid}&" not in a["href"] or "strMAGID" in a["href"]:
            continue
        t = clean(a.get_text())
        if re.match(r"^第\s*%d\s*期" % isid, t):
            title = t
            break
    arts, seen = [], set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"strISID=(\d+)[^\"']*strMAGID=(M\d+)", a["href"])
        if not m or int(m.group(1)) != isid:
            continue
        magid = m.group(2)
        name = clean(a.get_text())
        if not name or magid in seen:
            continue
        seen.add(magid)
        arts.append({"magid": magid, "title": name})
    return title, arts


def parse_article(html: str):
    """→ (欄目, 題名, 作者, 內文)。內文固定在 <td id="Zoom">。"""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    def first(css):
        el = soup.select_one(css)
        return clean(el.get_text(" ")) if el else ""

    body_el = soup.find(id="Zoom")
    body = ""
    if body_el:
        lines = [clean(x) for x in body_el.get_text("\n").split("\n")]
        body = "\n".join(l for l in lines if l)
    # text10_gray 這個 class 導覽列也在用，第一個抓到的多半是空的導覽格；
    # 欄目是題名那格所在表格裡的那一個，所以從題名往上找。
    title_el = soup.select_one("td.text15_blue_bold")
    column = ""
    if title_el:
        table = title_el.find_parent("table")
        if table:
            for td in table.select("td.text10_gray"):
                t = clean(td.get_text(" "))
                if t:
                    column = t
                    break
    return column, clean(title_el.get_text(" ")) if title_el else "", first("td.title1"), body


ISSUE_DATE_RE = re.compile(r"發行日期[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})")


def parse_issue_date(html: str) -> str:
    """文章頁上有「發行日期：1997/12/10」——期別的出刊日只在這裡，
    是語料層替新使者排年表唯一的來源（目次頁與 index 都沒有）。

    站方偶有佔位值（第199期填 1900/01/01），落在刊物存續區間外的一律當無效——
    這種值進了年表會在 1900 年憑空長出一根柱子，比沒有日期更糟。
    """
    m = ISSUE_DATE_RE.search(re.sub(r"<[^>]+>", " ", html))
    if not m:
        return ""
    year = int(m.group(1))
    if not 1990 <= year <= datetime.now().year + 1:   # 新使者 1990 創刊
        return ""
    return f"{year}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


def parse_issue_title(html: str, isid: int) -> str:
    """文章頁的麵包屑帶著期名（「第43期 世紀末的文化現象」），目次頁反而沒有。"""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        if f"strISID={isid}" not in a["href"] or "strMAGID" in a["href"]:
            continue
        t = clean(a.get_text())
        if re.match(r"^第\s*%d\s*期" % isid, t):
            return t
    return ""


def harvest(max_issue=None):
    # 先看最新一期期號：期別清單第一頁的最大 strISID 就是
    latest = max(int(x) for x in re.findall(r"strISID=(\d+)", get(f"{BASE}?strTID={TID}&strPageNo=1")))
    top = max_issue or latest
    print(f"最新期：{latest}，抓到第 {top} 期", flush=True)

    issues = []
    for isid in range(1, top + 1):
        try:
            title, arts = parse_issue(get(issue_url(isid)), isid)
        except Exception as e:  # noqa: BLE001  單期失敗不中斷整批
            print(f"  ! 第{isid}期：{e}", flush=True)
            continue
        if not arts:
            continue
        issues.append({"issue": isid, "title": title, "articles": arts})
        if isid % 20 == 0:
            print(f"  …第{isid}期，累計 {sum(len(i['articles']) for i in issues)} 篇", flush=True)
        time.sleep(0.25)

    HARVEST.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(issues)} 期 / {sum(len(i['articles']) for i in issues)} 篇 → {HARVEST}")


def process(limit=0):
    issues = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    done = skip = fail = 0
    for it in issues:
        for art in it["articles"]:
            key = f"{R2_TXT}/{it['issue']:03d}-{art['magid']}.txt"
            if key in have:
                skip += 1
                continue
            try:
                html = get(article_url(it["issue"], art["magid"]))
                if not it.get("title"):
                    it["title"] = parse_issue_title(html, it["issue"])
                if not it.get("date"):
                    it["date"] = parse_issue_date(html)
                col, title, author, body = parse_article(html)
                if len(body) < 200:      # 只有連結沒有正文的條目
                    skip += 1
                    continue
                art["column"] = col
                art["author"] = author
                if title:
                    art["title"] = title
                df.r2_put_text(key, body)
                done += 1
                if done % 50 == 0:
                    print(f"  …已處理 {done} 篇", flush=True)
                time.sleep(0.25)
                if limit and done >= limit:
                    print(f"--limit {limit} 到達", flush=True)
                    HARVEST.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
                    return
            except Exception as e:  # noqa: BLE001
                fail += 1
                print(f"  ✗ 第{it['issue']}期 {art['title'][:26]}: {type(e).__name__}: {str(e)[:80]}", flush=True)
    HARVEST.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n新增 {done}、既有/略過 {skip}、失敗 {fail}", flush=True)


def publish():
    issues = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    out = []
    for it in sorted(issues, key=lambda x: -x["issue"]):
        arts = []
        for a in it["articles"]:
            key = f"{R2_TXT}/{it['issue']:03d}-{a['magid']}.txt"
            if key not in have:
                continue
            arts.append({
                "title": a["title"],
                "author": a.get("author", ""),
                "column": a.get("column", ""),
                "textKey": key,
                "source": article_url(it["issue"], a["magid"]),
            })
        if arts:
            out.append({"issue": str(it["issue"]), "title": it["title"],
                        "date": it.get("date", ""), "articles": arts})
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} 期 / {sum(len(x['articles']) for x in out)} 篇 → {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--mag", default="new-messenger", choices=sorted(MAGAZINES))
    ap.add_argument("--max-issue", type=int)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    use(args.mag)
    if args.harvest:
        harvest(args.max_issue)
    if args.process:
        process(args.limit)
    if args.publish:
        publish()
    if not (args.harvest or args.process or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
