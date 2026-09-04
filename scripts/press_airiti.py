# -*- coding: utf-8 -*-
"""華藝線上圖書館（Airiti Library）的宗教類期刊：刊物普查 → 篇目索引 → 全文下載。

《校園》《新使者》這類教會刊物不在自家網站做典藏，卻整份收在華藝裡，而且帶著
自家網站沒有的三個欄位：**卷期、頁碼、正式作者署名**。做註腳需要的就是這三個。

本檔三個階段：

  --discover   學科分類「人文學＞宗教學」（代碼 A00-A03）底下的所有期刊，
               外加一份指名探測清單（有些刊被歸到別的學科，靠刊名補抓）。
               → public/content/research-data/press/airiti-journals.json
  --toc SLUG   逐卷期抓篇目（篇名／作者／卷期／出版年月／起訖頁／有無電子全文）
               → public/content/research-data/press/airiti/<slug>.json
  --summarize  把各刊的篇目統計併成一份小索引，給 /research-data/press 卡片用
               → public/content/research-data/press/airiti-index.json
  --download SLUG  把有電子全文的篇目逐篇下載成 PDF
               → G:/我的雲端硬碟/資料/知識圖工作室/研究資料/華藝期刊全文/<刊名>/

站台結構（2026-09 實測，全部 server-render，不需要瀏覽器）：

  卷期清單  GET /Publication/Information?publicationID=<pid>&type=期刊&tabName=2
            → <option value="<issueID>">68卷2期 (2026/04)</option>
  單期篇目  同一網址加 &issueYear=<年>&issueID=<issueID>&page=<N>&publisherID=<pubid>
            → div.searchResultGroup[key=<docID>]，每頁 10 筆，頁尾 .ustyle_pageList 有下一頁
  下載      兩段：POST /Article/TextDownloadWindowNew（帶該筆的 AjaxRequestVerificationToken）
            拿到新 token 與 lan_下載編號，再 POST /Article/TextDownloadNew
            {docID, token:'', key:<下載編號>} → PDF bytes

🚨 **下載額度是綁機構 IP 的**。本機目前被華藝認成玄奘大學（頁面右上角寫著
   「您好！玄奘大學 IP:…」），reCAPTCHA 因此被跳過（lan_是否跳過reCAPTCHA檢查=true）。
   這代表跑得快就是拿全校的訂閱在衝——華藝對異常流量的處置是**停整個機構的權限**，
   不是停你一個帳號。所以預設 6 秒一篇、單次上限 300 篇，不要往下調。

🚨 IP 認證是**會掉的**（換網段、離開校內網路）。掉了以後下載端點不會報錯，
   會安靜地回一個 JSON 錯誤訊息而不是 PDF，HTTP 一樣 200。所以每一筆都驗
   `%PDF` 開頭，不是只看狀態碼；驗到掉線就整批停，別把失敗寫滿帳本。

  python -X utf8 scripts/press_airiti.py --discover
  python -X utf8 scripts/press_airiti.py --toc campus
  python -X utf8 scripts/press_airiti.py --toc all
  python -X utf8 scripts/press_airiti.py --download campus [--limit 300]
"""
import argparse
import json
import re
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.airitilibrary.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "public/content/research-data/press"
TOC_DIR = OUT / "airiti"
DRIVE = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/研究資料/華藝期刊全文")

# 學科分類：人文學（A00）＞宗教學（A03）。第二層的鍵長這樣 "A00-A03.00.00"，查詢吃萬用字元。
SUBJECT_RELIGION = "A00-A03*"
# 期刊類（CEPS 台灣／CEPS 中國大陸／CJTD），對應 全域_OpPubType 的 0 / 1 / 2
PUB_TYPES = [0, 1, 2]
# 出版品查詢欄位代碼（全域_OpPubSearchFiled）
F_PUB_NAME, F_SUBJECT2, F_PUBLICATION_ID = 1, 6, 16

# 歸在別的學科、但對本論文一樣要緊的刊，用刊名補探。
# 查不到就會在 discover 的輸出裡留一筆 hits=0，不是靜靜消失。
NAME_PROBES = [
    "使者", "宇宙光", "台灣教會公報", "人生", "香光", "慈濟", "普門學報",
    "圓光佛學學報", "正觀", "福嚴", "海潮音", "菩提樹", "獅子吼",
    "中華佛學", "法光", "基督教論壇", "靈糧", "校園", "神學", "佛學", "宗教",
]

# 要做篇目索引的刊：slug → (publicationID, 刊名)
JOURNALS = {
    # ── 基督教
    "campus":             ("a0000007",     "校園"),
    "new-messenger":      ("a0000496",     "新使者"),
    "wilderness":         ("P20250214002", "曠野"),
    "theology-church":    ("P20190115001", "神學與教會"),
    "taiwan-theology":    ("P20151015001", "台灣神學論刊"),
    "ces-journal":        ("19986505",     "華神期刊"),
    "sino-christian":     ("19902670",     "漢語基督教學術論評"),
    "logos-pneuma":       ("P20170411002", "道風：基督教文化評論"),
    "jiandao":            ("P20220215001", "建道學刊"),
    "collectanea":        ("P20230411002", "神學論集"),
    "dao-magazine":       ("a0000008",     "道雜誌"),
    "baptist-annual":     ("P20161102001", "浸神學刊"),
    # ── 佛教
    "chbs-journal":       ("P20160922003", "中華佛學學報"),
    "chbs-journal-old":   ("P20160922002", "中華佛學學報（舊刊名）"),
    "chbs-studies":       ("P20160922001", "中華佛學研究"),
    "ddbj":               ("P20190125001", "法鼓佛學學報"),
    "ntu-buddhist":       ("10271112",     "臺大佛學研究"),
    "ntu-buddhist-old":   ("P20191030002", "佛學研究中心學報"),
    "fgu-journal":        ("P20181205001", "佛光學報"),
    "hcu-buddhist":       ("18133649",     "玄奘佛學研究"),
    "dharma-seals":       ("22241299",     "法印學報"),
    "hongshi":            ("P20121213001", "弘誓雙月刊"),
    "huayen":             ("P20160706001", "華嚴學報"),
    "humanistic-buddhism": ("P20180307006", "人間佛教研究"),
    # ── 宗教學綜合
    "religious-philosophy": ("10277730",   "宗教哲學"),
    "fujen-religious":    ("16820568",     "輔仁宗教研究"),
    "new-century":        ("16843738",     "新世紀宗教研究"),
    "taiwan-religion":    ("a0000594",     "臺灣宗教研究"),
    "chinese-religions":  ("P20170630002", "華人宗教研究"),
}

DELAY_META = 1.5     # 篇目：只是讀頁面，正常瀏覽速率
DELAY_DL = 6.0       # 全文：見檔頭，這個數字不要調小
DL_CAP = 300         # 單次執行的下載上限


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "zh-TW,zh;q=0.9"})
    return s


def _text(el):
    return el.get_text(" ", strip=True) if el else ""


# ---------------------------------------------------------------- 刊物普查

def pub_query(s, fields, page_size=100):
    obj = {"查詢歷史類型代碼": "PubSearch",
           "PSF": {"SortFiled": 1, "PageSize": page_size,
                   "SearchFileds": fields,
                   "SearchPubTypes": [{"FieldName": t, "FieldQuery": True, "FieldLogic": 1}
                                      for t in PUB_TYPES]}}
    qs = urllib.parse.quote(json.dumps(obj, ensure_ascii=False))
    r = s.post(f"{BASE}/Publication/Query?queryString={qs}",
               data={"queryString": qs}, timeout=90)
    r.raise_for_status()
    return r.text


def parse_publications(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for g in soup.select("div.periodicalsInfoGroup"):
        brief = [_text(li) for li in g.select("ul.publishBrif li")]
        latest = next((b.replace("最新上線：", "").strip()
                       for b in brief if "最新上線" in b), "")
        issn = next((b.replace("ISSN：", "").strip()
                     for b in brief if b.startswith("ISSN")), "")
        rows.append({
            "pid": g.get("key", ""),
            "name": _text(g.select_one("h3 a")),
            "publisher": brief[0] if brief else "",
            "status": brief[1] if len(brief) > 1 else "",
            "latest": latest,
            "issn": issn,
        })
    return rows


def discover(s):
    print("學科分類 人文學＞宗教學 …")
    rows = parse_publications(pub_query(
        s, [{"FieldName": F_PUBLICATION_ID, "SearchKeyWord": "*",
             "FieldQuery": True, "FieldLogic": 0},
            {"FieldName": F_SUBJECT2, "SearchKeyWord": SUBJECT_RELIGION,
             "FieldQuery": True, "FieldLogic": 0}]))
    print(f"  {len(rows)} 種")
    by_pid = {}
    for r in rows:
        r["found_by"] = "宗教學"
        by_pid[r["pid"]] = r

    probes = []
    for kw in NAME_PROBES:
        time.sleep(DELAY_META)
        hits = parse_publications(pub_query(
            s, [{"FieldName": F_PUB_NAME, "SearchKeyWord": kw,
                 "FieldQuery": True, "FieldLogic": 0}], page_size=100))
        fresh = [h for h in hits if h["pid"] not in by_pid]
        for h in fresh:
            h["found_by"] = f"刊名探測：{kw}"
            by_pid[h["pid"]] = h
        probes.append({"keyword": kw, "hits": len(hits), "new": len(fresh),
                       "names": [h["name"] for h in fresh]})
        print(f"  探測「{kw}」：{len(hits)} 命中 / {len(fresh)} 新增", flush=True)

    data = {
        "note": "華藝線上圖書館收錄的宗教類期刊。found_by 記這一筆是靠學科分類找到的，"
                "還是靠刊名探測補到的——沒被「宗教學」收進來的那些，代表華藝把它歸在別的學科。",
        "subject": SUBJECT_RELIGION,
        "counts": {"宗教學學科": len(rows), "刊名探測補入": len(by_pid) - len(rows),
                   "合計": len(by_pid)},
        "probes": probes,
        "items": sorted(by_pid.values(), key=lambda r: (r["found_by"] != "宗教學", r["name"])),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "airiti-journals.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(by_pid)} 種 → {OUT / 'airiti-journals.json'}")


# ---------------------------------------------------------------- 篇目索引

def info_url(pid, **kw):
    q = {"publicationID": pid, "type": "期刊", "tabName": "2"}
    q.update({k: v for k, v in kw.items() if v not in (None, "")})
    return f"{BASE}/Publication/Information?" + urllib.parse.urlencode(q)


ISSUE_RE = re.compile(r'<option value="([^"]+)" key="[^"]*">([^<]+)</option>')
YEAR_RE = re.compile(r"\((\d{4})\s*/")


def list_issues(s, pid):
    """卷期清單。option 的順序就是站上的順序（新 → 舊），照原序保留。"""
    html = s.get(info_url(pid), timeout=90).text
    out, seen = [], set()
    for iid, label in ISSUE_RE.findall(html):
        m = YEAR_RE.search(label)
        if not iid or iid in seen or not m:
            continue
        seen.add(iid)
        out.append({"issueID": iid, "label": label.strip(), "year": m.group(1)})
    pm = re.search(r"全域_出版單位代碼 = '([^']*)'", html)
    return out, (pm.group(1) if pm else "")


DL_RE = re.compile(
    r"Common_點擊全文下載\('([^']*)','([^']*)','([^']*)', '([^']*)', '([^']*)', '([^']*)'\)")


def parse_issue_page(html):
    """單期篇目的一頁。回傳 (articles, 是否還有下一頁)。"""
    soup = BeautifulSoup(html, "html.parser")
    tokens = {m.group(1) for m in DL_RE.finditer(html)}
    arts = []
    for g in soup.select("div.searchResultGroup"):
        doc = g.get("key", "")
        src = g.select_one("span.source")
        arts.append({
            "docId": doc,
            "title": _text(g.select_one("h3 a")),
            "authors": [_text(a) for a in g.select("span.author a")],
            "volIssue": _text(src.select_one("span.sourcePub")) if src else "",
            "date": _text(src.select_one("span.sourcedate")).strip("() ") if src else "",
            "pages": (_text(src.select_one("span.sourcePageRange"))
                      .replace("Pp.", "").strip() if src else ""),
            "fulltext": doc in tokens,
        })
    return arts, bool(soup.select_one("li.PagedList-skipToNext a"))


def harvest_toc(s, slug):
    pid, name = JOURNALS[slug]
    issues, publisher_id = list_issues(s, pid)
    print(f"{name}（{pid}）：{len(issues)} 期")
    all_arts, per_issue = [], []
    for n, iss in enumerate(issues, 1):
        got, page = [], 1
        while True:
            time.sleep(DELAY_META)
            url = info_url(pid, issueYear=iss["year"], issueID=iss["issueID"],
                           page=(page if page > 1 else None), publisherID=publisher_id)
            arts, has_next = parse_issue_page(s.get(url, timeout=90).text)
            got.extend(arts)
            if not has_next or page > 40:
                break
            page += 1
        for a in got:
            a["issueLabel"] = iss["label"]
            a["issueID"] = iss["issueID"]
        all_arts.extend(got)
        per_issue.append({"issueID": iss["issueID"], "label": iss["label"],
                          "year": iss["year"], "count": len(got)})
        print(f"  [{n}/{len(issues)}] {iss['label']}：{len(got)} 篇", flush=True)

    data = {"slug": slug, "pid": pid, "name": name, "publisherID": publisher_id,
            "source": info_url(pid),
            "counts": {"卷期": len(issues), "篇目": len(all_arts),
                       "有電子全文": sum(1 for a in all_arts if a["fulltext"])},
            "issues": per_issue, "articles": all_arts}
    TOC_DIR.mkdir(parents=True, exist_ok=True)
    (TOC_DIR / f"{slug}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  → {len(all_arts)} 篇（{data['counts']['有電子全文']} 篇有全文）"
          f" → {TOC_DIR / (slug + '.json')}")
    return data


# ---------------------------------------------------------------- 全文下載

def fetch_pdf(s, pid, publisher_id, year, issue_id, doc_id, issue_html=None):
    """兩段式下載。回傳 (bytes, 檔名) 或 (None, 錯誤訊息)。"""
    url = info_url(pid, issueYear=year, issueID=issue_id, publisherID=publisher_id)
    html = issue_html if issue_html is not None else s.get(url, timeout=90).text
    tok = next((m.group(4) for m in DL_RE.finditer(html) if m.group(1) == doc_id), None)
    if not tok:
        return None, "此篇在卷期頁上沒有全文下載鈕"
    obj = {"文章代碼": doc_id, "文章篇名": "", "需扣除點數": "",
           "文獻類型代碼": "P001", "ActionName": "TextDownload", "OrderID": None}
    w = s.post(f"{BASE}/Article/TextDownloadWindowNew",
               data={"jsString": urllib.parse.quote(json.dumps(obj, ensure_ascii=False))},
               headers={"AjaxRequestVerificationToken": tok,
                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Referer": url}, timeout=90).text
    t2 = re.search(r"ajaxRequestVerificationToken_DownloadWindow = '([^']+)'", w)
    key = re.search(r"lan_下載編號 = '([^']*)'", w)
    if not (t2 and key):
        return None, "取不到下載編號（多半是 IP 認證掉了）"
    r = s.post(f"{BASE}/Article/TextDownloadNew",
               data={"docID": doc_id, "token": "", "key": key.group(1)},
               headers={"AjaxRequestVerificationToken": t2.group(1),
                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Referer": url}, timeout=180)
    # 🚨 200 不等於拿到 PDF：權限沒過的時候回的是 JSON 錯誤訊息，一樣 200
    if not r.content.startswith(b"%PDF"):
        return None, (r.text[:200] if len(r.content) < 4000
                      else f"非 PDF，{len(r.content)} bytes")
    m = re.search(r"filename=([^;]+)", r.headers.get("content-disposition", ""))
    return r.content, (urllib.parse.unquote(m.group(1).strip()) if m else "")


SAFE = re.compile(r'[\\/:*?"<>|\r\n\t]+')


def safe_name(x, limit=110):
    return SAFE.sub("_", x).strip().rstrip(".")[:limit] or "untitled"


def download(s, slug, limit):
    pid, name = JOURNALS[slug]
    toc = json.loads((TOC_DIR / f"{slug}.json").read_text(encoding="utf-8"))
    root = DRIVE / safe_name(name)
    root.mkdir(parents=True, exist_ok=True)
    ledger_p = root / "_ledger.json"
    ledger = json.loads(ledger_p.read_text(encoding="utf-8")) if ledger_p.exists() else {}

    todo = [a for a in toc["articles"] if a["fulltext"] and ledger.get(a["docId"]) != "ok"]
    print(f"{name}：{len(todo)} 篇待下載（本次上限 {limit}）")
    done = fail = 0
    cached_issue, cached_html = None, None
    for a in todo[:limit]:
        sub = root / safe_name(a["issueLabel"])
        sub.mkdir(parents=True, exist_ok=True)
        dest = sub / f"{safe_name(a['title'], 90)}.pdf"
        if dest.exists() and dest.stat().st_size > 1024:
            ledger[a["docId"]] = "ok"
            continue
        # 同一期連續下載時，卷期頁重抓一次就夠——token 在整頁裡是逐篇各一份的
        if cached_issue != a["issueID"]:
            time.sleep(DELAY_META)
            cached_html = s.get(info_url(pid, issueYear=(a.get("date") or "")[:4],
                                         issueID=a["issueID"],
                                         publisherID=toc["publisherID"]), timeout=90).text
            cached_issue = a["issueID"]
        if f"'{a['docId']}'" not in cached_html:
            cached_html = None  # 這篇不在第一頁，讓 fetch_pdf 自己重抓
        time.sleep(DELAY_DL)
        blob, info = fetch_pdf(s, pid, toc["publisherID"], (a.get("date") or "")[:4],
                               a["issueID"], a["docId"], cached_html)
        if cached_html is None:
            cached_issue = None
        if blob is None:
            ledger[a["docId"]] = f"fail: {info}"
            fail += 1
            print(f"  ✗ {a['title'][:34]} — {info[:70]}", flush=True)
            if "IP 認證" in info:
                print("  ⚠ 中止：華藝已經不認這台機器的機構身分了")
                break
        else:
            dest.write_bytes(blob)
            ledger[a["docId"]] = "ok"
            done += 1
            print(f"  ✓ [{done}] {a['issueLabel']} {a['title'][:34]} "
                  f"({len(blob) // 1024} KB)", flush=True)
        ledger_p.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    ledger_p.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    left = sum(1 for a in toc["articles"] if a["fulltext"] and ledger.get(a["docId"]) != "ok")
    print(f"{name}：本次 {done} 成功 / {fail} 失敗，尚餘 {left} 篇 → {root}")


def summarize():
    """各刊只留統計，給列表頁用——卷期頁那幾份 JSON 動輒好幾 MB，卡片頁不該整份拉。"""
    rows = []
    for slug, (pid, name) in JOURNALS.items():
        f = TOC_DIR / f"{slug}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        yrs = sorted({i["year"] for i in d["issues"]})
        rows.append({"slug": slug, "pid": pid, "name": name,
                     "issues": d["counts"]["卷期"], "articles": d["counts"]["篇目"],
                     "fulltext": d["counts"]["有電子全文"],
                     "start": yrs[0] if yrs else "", "end": yrs[-1] if yrs else ""})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "airiti-index.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} 刊 / {sum(r['articles'] for r in rows):,} 篇 "
          f"→ {OUT / 'airiti-index.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--toc", help="slug 或 all")
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--download", help="slug 或 all")
    ap.add_argument("--limit", type=int, default=DL_CAP)
    args = ap.parse_args()
    s = session()

    if args.discover:
        discover(s)
    if args.toc:
        for slug in ([args.toc] if args.toc != "all" else list(JOURNALS)):
            harvest_toc(s, slug)
    if args.summarize:
        summarize()
    if args.download:
        for slug in ([args.download] if args.download != "all" else list(JOURNALS)):
            download(s, slug, args.limit)
    if not (args.discover or args.toc or args.summarize or args.download):
        ap.print_help()


if __name__ == "__main__":
    main()
