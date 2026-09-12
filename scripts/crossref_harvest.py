#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從 Crossref 收神學與宗教學期刊的篇目——補「非英語神學期刊」這個缺口。

**為什麼是這一支而不是 IxTheo**（2026-09-12 實測，別再走一次）：

原訂補這個缺口的是 Index Theologicus（IxTheo，圖賓根 UB 的神學索引，四百萬筆，
免費開放不綁機構 IP）。實測結論是**抓不到，而且不是技術問題**：

  * `ixtheo.de` **整站**擋在一道 proof-of-work 瀏覽器驗證後面——17-bit SHA-256
    挑戰、openresty 前端、回應帶 `X-Robots-Tag: noindex`。`robots.txt` 本身、
    OAI-PMH 的 `/OAI/Server?verb=Identify`、VuFind 的 `/api/v1/search`、
    `/Search/Results` 全部一視同仁回那張「Verifying your browser…」。
    換 UA 沒用。這是站方**刻意設來擋自動抓取**的閘門，不是設定失誤，所以不繞。
  * 往底層追也不通。IxTheo 自 2013 年起把單篇著錄直接建在 K10plus（原 SWB）的
    PICA CBS，再匯出到自己的 Solr。K10plus 的公開 SRU（`sru.k10plus.de/opac-de-627`）
    確實沒有閘門，但**只有書刊層沒有單篇層**：拿《Zeitschrift für Theologie und
    Kirche》的 ISSN 0044-3549 去查只回 3 筆，全是刊物本身的著錄。帶單篇的
    `sru.k10plus.de/k10plus` 回 `info:srw/diagnostic/1/236 Access to specified
    database denied`。也查不到公開的資料 dump。

要 IxTheo 的資料只剩一條路：寫信給圖賓根 UB 的 FID Theologie 要。在那之前，
Crossref 填同一個缺口——德語神學的主要出版社（Mohr Siebeck、Vandenhoeck &
Ruprecht、De Gruyter、Brill、Peeters、Aschendorff）都繳 DOI，而且**題名／作者／
卷／期／起訖頁／年份一次到齊**，正是做註腳要的那三個欄位（華藝之外唯一有的）。

## 實測到的端點與限制

  端點      `https://api.crossref.org/journals?query=<詞>`（找刊，查的是刊名與出版社）
            `https://api.crossref.org/journals/<issn>/works?cursor=*&rows=1000`（抓篇目）
  授權      Crossref 的中繼資料採 CC0，可自由再散布。
  速率      公開池不保證；帶聯絡信箱走 polite pool 比較穩。本腳本讀環境變數
            `CROSSREF_MAILTO`，**沒設就走匿名池**（不把私人信箱寫死在版控裡）。

🚨 三個坑：

1. **不要用 offset 分頁。** `rows`+`offset` 在 offset 超過 10000 之後直接失敗，
   而一份大刊（例如 Brill 那幾種）輕易破萬。`cursor=*` 沒有這個上限——
   這一點跟 DOAJ 正好相反（DOAJ 是 1000 筆硬上限、只能靠年份二分切小，
   見 doaj_harvest.py 的 fetch_range）。翻頁時**每一次都要把原查詢參數一起送**，
   只送 cursor 會回到第一頁；照這樣抓會得到一個「筆數是 rows 的整數倍」的檔案，
   數字整齊、不報錯、看起來完全正常。所以寫檔後一定要跟 total-results 對帳。
2. **`select` 不吃 `language`。** `?select=...,language` 回 400
   `select-not-available`，但**不帶 select 時完整紀錄裡有 language 欄**。
   非英語比重是這一批存在的理由，所以寧可傳整包也不要 select 掉語言。
3. **`type` 要過濾。** 一刊的 works 裡混著 journal-issue、book-review、
   editorial、component。只留 `journal-article`（並把被濾掉的數量記在對帳裡，
   否則 total-results 永遠對不上而看不出是正常的還是漏抓）。

## 存放

  期刊清單  `data/research-data/crossref-journals.json`（進版控）
  篇目      Drive `知識圖工作室/_corpus/crossref/<issn>.jsonl`（大，不進 git）
  網站索引  `public/content/research-data/contemporary-theology/crossref.json`（進版控）

## 用法

  python scripts/crossref_harvest.py --journals           # 建／更新刊物清單
  python scripts/crossref_harvest.py --articles --limit 5 # 先抓五刊試
  python scripts/crossref_harvest.py --articles           # 全抓（可中斷續跑）
  python scripts/crossref_harvest.py --index              # 產網站索引
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
JOURNALS = ROOT / "data" / "research-data" / "crossref-journals.json"
DOAJ_JOURNALS = ROOT / "data" / "research-data" / "doaj-journals.json"
CORPUS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/crossref")
INDEX = ROOT / "public" / "content" / "research-data" / "contemporary-theology" / "crossref.json"

API = "https://api.crossref.org"
DELAY = 1.0
ROWS = 1000

# 找刊用的查詢詞。刻意多語並行——這一批存在的理由就是 DOAJ 與華藝都照不到的
# 德語／法語／義語神學期刊。英語詞留著是為了把同一刊的英語題名也撈進來。
QUERIES = [
    # 德語
    "Theologie", "Theologische", "Religionswissenschaft", "Kirchengeschichte",
    "Kirche", "Bibel", "Dogmatik", "Ökumene", "Liturgie", "Exegese",
    "Judaistik", "Religionspädagogik", "Religionsphilosophie",
    # 法語
    "théologie", "théologique", "religieuses", "ecclésiastique", "biblique",
    # 義語／西語／葡語
    "teologia", "teologica", "teología", "religiosa", "eclesiástica", "bíblica",
    # 荷語／北歐
    "theologisch", "kerk", "teologisk", "teologi",
    # 英語
    "Theology", "Theological", "Religion", "Religious Studies", "Biblical",
    "Church History", "Ecclesiastical", "Patristic", "Scripture", "Hermeneutics",
]

# 刊名要命中這個才收。query 查的是刊名＋出版社，光靠 query 會把
# 「某某出版社出的物理期刊」也帶進來。
KEEP = re.compile(
    r"theolog|religio|kirch|kerk|église|eglise|chiesa|iglesia|igreja|church|"
    r"bibl|bíbl|scriptur|exeget|exeges|patrist|liturg|ökumen|oekumen|ecumen|"
    r"dogmat|homilet|missio|judaist|jewish|islam|buddhis|hindu|spiritual|"
    r"teolog|christ|kristen|catholic|katholi|protestant|evangel|"
    r"canon law|kanonist|seelsorg|pastoral|religieus|religieuse",
    re.I,
)

# 明顯不是本題的，命中就丟。KEEP 太寬會撈到這些。
DROP = re.compile(r"christ church|evangelical medicine|religion and health care law", re.I)


def ua() -> dict:
    """polite pool 要靠 UA 裡的 mailto。信箱只從環境變數讀，不寫死在版控裡。"""
    mail = os.environ.get("CROSSREF_MAILTO", "").strip()
    s = "kglab-research/1.0 (academic bibliography compilation)"
    if mail:
        s += f" (mailto:{mail})"
    return {"User-Agent": s}


def get(url: str) -> dict:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=ua())
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(6 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt < 3:
                time.sleep(4)
                continue
            raise
    return {}


# ---------------------------------------------------------------- 刊物清單

def doaj_issns() -> set[str]:
    if not DOAJ_JOURNALS.exists():
        return set()
    out = set()
    for j in json.loads(DOAJ_JOURNALS.read_text(encoding="utf-8")):
        if j.get("issn"):
            out.add(j["issn"].upper())
    return out


def harvest_journals() -> list[dict]:
    known = doaj_issns()
    found: dict[str, dict] = {}
    for q in QUERIES:
        url = f"{API}/journals?query={urllib.parse.quote(q)}&rows=1000"
        try:
            m = get(url).get("message") or {}
        except Exception as e:
            print(f"  {q:24s} 失敗 {type(e).__name__}")
            time.sleep(DELAY)
            continue
        hits = 0
        for it in m.get("items") or []:
            title = (it.get("title") or "").strip()
            if not title or not KEEP.search(title) or DROP.search(title):
                continue
            issns = [x.upper() for x in (it.get("ISSN") or []) if x]
            if not issns:
                continue
            key = issns[0]
            rec = found.setdefault(key, {
                "issn": key,
                "issns": issns,
                "title": title,
                "publisher": it.get("publisher"),
                "subjects": sorted({s.get("name") for s in (it.get("subjects") or [])
                                    if s.get("name")}),
                "total_dois": (it.get("counts") or {}).get("total-dois"),
                "in_doaj": any(x in known for x in issns),
                "queries": [],
            })
            if q not in rec["queries"]:
                rec["queries"].append(q)
            hits += 1
        print(f"  {q:24s} 命中 {hits:>4}（累計不重複 {len(found)}）")
        time.sleep(DELAY)
    return sorted(found.values(), key=lambda x: -(x["total_dois"] or 0))


# ---------------------------------------------------------------- 篇目

def rows_of(items: list[dict]) -> tuple[list[dict], int]:
    """留 journal-article，其餘（journal-issue／book-review／editorial…）計數丟掉。"""
    out, dropped = [], 0
    for it in items:
        if it.get("type") != "journal-article":
            dropped += 1
            continue
        title = (it.get("title") or [""])[0]
        if not title.strip():
            dropped += 1
            continue
        d = (it.get("issued") or {}).get("date-parts") or [[None]]
        out.append({
            "title": title.strip(),
            "authors": [" ".join(x for x in (a.get("given"), a.get("family")) if x).strip()
                        or a.get("name") or ""
                        for a in (it.get("author") or [])],
            "year": d[0][0] if d and d[0] else None,
            "volume": it.get("volume"), "issue": it.get("issue"), "pages": it.get("page"),
            "doi": it.get("DOI"),
            "lang": it.get("language"),
            "journal": (it.get("container-title") or [None])[0],
            "url": it.get("URL"),
        })
    return out, dropped


def fetch_journal(issn: str) -> tuple[list[dict], int, int]:
    """cursor 翻完一整刊。回 (篇目, Crossref 自報總數, 非 journal-article 的筆數)。

    🚨 每一次翻頁都要把 rows 一起送回去，只送 cursor 會退回第一頁——
    那樣抓出來的檔案筆數會是 rows 的整數倍，好看且不報錯。
    """
    cursor, out, total, dropped = "*", [], 0, 0
    seen: set[str] = set()
    while True:
        url = (f"{API}/journals/{urllib.parse.quote(issn)}/works"
               f"?rows={ROWS}&cursor={urllib.parse.quote(cursor, safe='')}")
        m = get(url).get("message") or {}
        total = m.get("total-results") or total
        items = m.get("items") or []
        got, dr = rows_of(items)
        dropped += dr
        for r in got:
            k = r.get("doi") or f"{r['title']}|{r.get('year')}"
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        nxt = m.get("next-cursor")
        if not items or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(DELAY)
    return out, total, dropped


def harvest_articles(journals: list[dict], limit: int | None, force: bool) -> None:
    if not CORPUS.parent.parent.exists():
        print("⚠️ G: 沒掛載，先修 Drive 再跑（別寫進一個不存在的路徑）")
        return
    CORPUS.mkdir(parents=True, exist_ok=True)
    todo = journals[:limit] if limit else journals
    done = skipped = 0
    mismatch: list[str] = []
    for i, j in enumerate(todo, 1):
        out = CORPUS / f"{j['issn'].replace('/', '-')}.jsonl"
        # 續傳只看檔案在不在——這台筆電通勤會休眠，不能設計成必須一次跑完。
        if out.exists() and out.stat().st_size > 2 and not force:
            skipped += 1
            continue
        try:
            rows, total, dropped = fetch_journal(j["issn"])
        except Exception as e:
            print(f"[{i}/{len(todo)}] {j['issn']} 失敗 {type(e).__name__}")
            time.sleep(DELAY)
            continue
        nl = chr(10)
        out.write_text(nl.join(json.dumps(r, ensure_ascii=False) for r in rows) + nl,
                       encoding="utf-8")
        done += 1
        # 對帳：實得＋被濾掉的，應該等於 Crossref 自報總數。差太多就是漏抓。
        gap = total - (len(rows) + dropped)
        flag = ""
        if gap > max(5, total * 0.02):
            flag = f"  ⚠️ 自報 {total}、實得 {len(rows)}＋濾掉 {dropped}，差 {gap}"
            mismatch.append(f"{j['issn']} {j['title']}：{flag.strip()}")
        print(f"[{i}/{len(todo)}] {(j['title'] or '')[:38]:40s} "
              f"{len(rows):>6} 篇（濾 {dropped}）{flag}")
        time.sleep(DELAY)
    print(chr(10) + f"抓 {done} 刊／略過 {skipped} 刊（已抓過，用 --force 重抓）")
    if mismatch:
        print(f"⚠️ 有 {len(mismatch)} 刊對不上帳，要逐刊看：")
        for x in mismatch[:15]:
            print("    " + x)


# ---------------------------------------------------------------- 索引

def build_index(journals: list[dict]) -> None:
    if not CORPUS.exists():
        print("⚠️ Drive 的 _corpus/crossref 不在（G: 沒掛載？），索引只會有刊沒有篇數")
    rows, articles = [], 0
    langs: dict[str, int] = {}
    for j in journals:
        f = CORPUS / f"{j['issn'].replace('/', '-')}.jsonl"
        n = 0
        if f.exists():
            for line in f.open(encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                n += 1
                try:
                    lg = (json.loads(line).get("lang") or "未標").split("-")[0]
                except json.JSONDecodeError:
                    lg = "未標"
                langs[lg] = langs.get(lg, 0) + 1
        articles += n
        rows.append({k: j[k] for k in ("issn", "title", "publisher", "in_doaj")}
                    | {"articles": n})
    rows.sort(key=lambda x: -x["articles"])
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({
        "source": "Crossref REST API（中繼資料 CC0，不需機構身分）",
        "why": "IxTheo 整站擋在 proof-of-work 驗證後面、K10plus 公開 SRU 沒有單篇層，"
               "非英語神學期刊這個缺口改由 Crossref 補。詳見腳本檔頭。",
        "journals": len(rows), "articles": articles,
        "languages": dict(sorted(langs.items(), key=lambda x: -x[1])),
        "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    top = "／".join(f"{k} {v:,}" for k, v in
                    sorted(langs.items(), key=lambda x: -x[1])[:8])
    print(f"期刊 {len(rows)} 種、篇目 {articles:,} 篇 → {INDEX}")
    print(f"語言分布：{top}")


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
        n_new = sum(1 for r in rows if not r["in_doaj"])
        print(f"\n{len(rows)} 種期刊 → {JOURNALS}（其中 {n_new} 種不在 DOAJ 那 313 種裡）")

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
