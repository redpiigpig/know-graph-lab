#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""華藝：按**作者**把某位學者的全部篇目列出來、（校內 IP 時）逐篇下載全文。

press_airiti.py 是按「刊」走的（先抓整刊篇目再下載），要某一個人的著作得先把他發表過的
每一份刊都抓篇目，太慢。這支直接打華藝的檢索：

  POST /Article/Query?queryString=<encodeURIComponent(JSON)>   （表單欄位 queryString 同值）

🚨 JSON 的「查詢歷史類型代碼」必須是 "ADLang"——寫 "DSF" 會回一頁看起來正常的
   「查無資料」（85,461 bytes，含 noResult.png），HTTP 200，不報錯。2026-09-26 卡了半小時。
   欄位代碼是數字：作者=2、篇名=1、所有欄位含全文=49（完整表在 _Layout_js 的 全域_OpDocSearchFiled）。
結果頁每筆 `div.searchResultGroup[key=docID]`，出處在 `span.source` 的三個 key：
   key0=publicationID、key1=出版日期 YYYYMMDD、key2=issueID。publisherID 不在結果裡，
   要另外從 /Publication/Information?publicationID=<pid> 取（一刊一次，有快取）。
下載沿用 press_airiti.fetch_pdf（兩段式、驗 %PDF、6 秒一篇、機構 IP 掉了就整批停）。

  python -X utf8 scripts/airiti_author_fetch.py 鍾雲鶯 楊弘任            # 只列清單
  python -X utf8 scripts/airiti_author_fetch.py 鍾雲鶯 楊弘任 --download # 列＋下載
  python -X utf8 scripts/airiti_author_fetch.py 鍾雲鶯 --types 期刊 會議  # 只要這些類型

輸出：public/content/research-data/press/airiti-authors/<作者>.json（篇目，進版控）
      Drive 研究資料/華藝期刊全文/_作者專輯/<作者>/<年>_<刊>_<篇名>.pdf（＋ _ledger.json）
已在各刊資料夾下過的（journal ledger 標 ok）不重下，只在清單上註明位置。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")
import press_airiti as pa  # noqa: E402

BASE = "https://www.airitilibrary.com"
OUT = ROOT / "public" / "content" / "research-data" / "press" / "airiti-authors"
DRIVE = pa.DRIVE / "_作者專輯"
PUBCACHE = Path(r"C:/tmp/airiti_publisher_ids.json")

SRC_RE = re.compile(r'class="source 點擊資訊" key0="([^"]*)" key1="([^"]*)" key2="([^"]*)".*?'
                    r'sourceTitleName">([^<]*)<.*?sourcePub">([^<]*)<.*?sourcedate">\(([^)]*)\)<'
                    r'(?:.*?sourcePageRange">Pp\.&nbsp;([^<]*)<)?', re.S)
GROUP_RE = re.compile(r'<div class="searchResultGroup" key="([^"]+)">(.*?)(?=<div class="searchResultGroup"|id="Result_分頁")', re.S)


def query_page(s, author: str, page: int, page_size: int = 50) -> str:
    obj = {"查詢歷史類型代碼": "ADLang",
           "DSF": {"SearchFileds": [{"IsAdvQuery": False, "FieldName": 2, "FieldQuery": True,
                                     "FieldLogic": 0, "SearchKeyWord": author}],
                   "SortFiled": 6, "SearchPubTypes": [], "PageSize": page_size, "Page": page,
                   "IsFuzzySearch": False, "IsReturnFacet": False},
           "BSF": {"SearchFiledList": []}}
    qs = urllib.parse.quote(json.dumps(obj, ensure_ascii=False))
    r = pa.post_with_retry(s, f"{BASE}/Article/Query?queryString={qs}", data={"queryString": qs},
                           headers={"Referer": BASE + "/"}, timeout=90)
    return r.text


def parse_results(html: str, author: str) -> list[dict]:
    out = []
    for doc_id, body in GROUP_RE.findall(html):
        m = SRC_RE.search(body)
        title = re.search(r"_文章書目_點擊篇名\('[^']*'[^>]*>\s*(.*?)\s*</a>", body, re.S)
        authors = re.findall(r'class="點擊作者"[^>]*>([^<]*)<', body)
        ptype = re.search(r'<li class="preTag [^"]*">.*?<span>([^<]*)</span>', body, re.S)
        # 作者欄的比對要嚴格：華藝的作者檢索會把「鍾雲鶯」也配到英文名相近的人
        if not any(author in a for a in authors):
            continue
        out.append({"docId": doc_id, "title": re.sub(r"\s+", " ", title.group(1)) if title else "",
                    "authors": authors, "type": ptype.group(1).strip() if ptype else "",
                    "pid": m.group(1) if m else None, "dateCode": m.group(2) if m else None,
                    "issueID": m.group(3) if m else None, "journal": m.group(4).strip("《》") if m else "",
                    "volIssue": m.group(5).strip() if m else "", "date": m.group(6).strip() if m else "",
                    "pages": (m.group(7) or "").strip() if m else "",
                    "fulltext": "TextDownloadWindowNew" in body or "全文下載" in body or 'class="download' in body})
    return out


def search_author(s, author: str) -> list[dict]:
    res, page = [], 1
    while True:
        html = query_page(s, author, page)
        got = parse_results(html, author)
        n_groups = len(GROUP_RE.findall(html))
        print(f"  第 {page} 頁：{n_groups} 筆結果，{len(got)} 筆作者對得上")
        res += got
        if n_groups < 50 or page >= 20:
            break
        page += 1
        time.sleep(2)
    # 去重（同一篇有時期刊版與會議版都在）
    seen, uniq = set(), []
    for a in res:
        if a["docId"] in seen:
            continue
        seen.add(a["docId"]); uniq.append(a)
    return uniq


def publisher_id(s, pid: str, cache: dict) -> str | None:
    if pid in cache:
        return cache[pid]
    r = s.get(f"{BASE}/Publication/Information", params={"publicationID": pid, "type": "期刊", "tabName": "2"},
              timeout=60)
    # 出版單位代碼不一定是數字（鵝湖月刊社是 U20110425001），頁面的 JS 變數才是正本
    m = re.search(r"全域_出版單位代碼\s*=\s*'([^']+)'", r.text) or re.search(r"publisherID=(\w+)", r.text)
    cache[pid] = m.group(1) if m else None
    PUBCACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    time.sleep(1.5)
    return cache[pid]


def journal_ledgers() -> dict[str, Path]:
    """各刊資料夾的 _ledger.json 裡標 ok 的 docId → 所在資料夾，避免重下。"""
    done = {}
    if not pa.DRIVE.exists():
        return done
    for led in pa.DRIVE.glob("*/_ledger.json"):
        try:
            for k, v in json.loads(led.read_text(encoding="utf-8")).items():
                if v == "ok":
                    done[k] = led.parent
        except (OSError, json.JSONDecodeError):
            pass
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("authors", nargs="+")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--types", nargs="*", default=None, help="只下這些類型（期刊／會議／學位）")
    ap.add_argument("--limit", type=int, default=300)
    args = ap.parse_args()

    s = pa.session()
    inst = pa.institution(s)
    print(f"機構身分：{inst or '（無）'}")
    if args.download and not inst:
        print("不是校內 IP，只列清單不下載"); args.download = False
    cache = json.loads(PUBCACHE.read_text(encoding="utf-8")) if PUBCACHE.exists() else {}
    done_elsewhere = journal_ledgers()
    OUT.mkdir(parents=True, exist_ok=True)
    spent = 0

    for author in args.authors:
        print(f"\n══ {author}")
        arts = search_author(s, author)
        n_ft = sum(a["fulltext"] for a in arts)
        print(f"  共 {len(arts)} 篇（有電子全文 {n_ft}）；類型：{ {t: sum(a['type']==t for a in arts) for t in {a['type'] for a in arts}} }")
        for a in arts:
            a["downloaded"] = None
            if a["docId"] in done_elsewhere:
                a["downloaded"] = str(done_elsewhere[a["docId"]].relative_to(pa.DRIVE))
        (OUT / f"{author}.json").write_text(json.dumps(
            {"author": author, "fetched": time.strftime("%Y-%m-%d"), "count": len(arts), "articles": arts},
            ensure_ascii=False, indent=1), encoding="utf-8")
        for a in sorted(arts, key=lambda x: x["date"]):
            flag = "✓已有" if a["downloaded"] else ("全文" if a["fulltext"] else "無全文")
            print(f"   {a['date'][:7]:8} {flag:4} [{a['type']}] 《{a['journal']}》{a['volIssue']} {a['title'][:44]}")

        if not args.download:
            continue
        root = DRIVE / pa.safe_name(author)
        root.mkdir(parents=True, exist_ok=True)
        ledger_p = root / "_ledger.json"
        ledger = json.loads(ledger_p.read_text(encoding="utf-8")) if ledger_p.exists() else {}
        todo = [a for a in arts if a["fulltext"] and not a["downloaded"] and ledger.get(a["docId"]) != "ok"
                and a["pid"] and (args.types is None or any(t in a["type"] for t in args.types))]
        print(f"  待下載 {len(todo)} 篇")
        ok = fail = 0
        for a in todo[:args.limit]:
            pub = publisher_id(s, a["pid"], cache)
            if not pub:
                ledger[a["docId"]] = "fail: 取不到 publisherID"; fail += 1; continue
            year = (a["dateCode"] or "")[:4]
            dest = root / f"{pa.safe_name(year + '_' + a['journal'] + '_' + a['title'], 120)}.pdf"
            if dest.exists() and dest.stat().st_size > 1024:
                ledger[a["docId"]] = "ok"; a["downloaded"] = str(dest.relative_to(pa.DRIVE)); continue
            time.sleep(pa.DELAY_DL)
            blob, info = pa.fetch_pdf(s, a["pid"], pub, year, a["issueID"], a["docId"])
            if blob is None:
                ledger[a["docId"]] = f"fail: {info}"; fail += 1
                print(f"  ✗ {a['title'][:36]} — {info[:70]}", flush=True)
                if "IP 認證" in info:
                    print("  ⚠ 中止：華藝已經不認這台機器的機構身分了"); break
                continue
            err = pa.write_with_retry(dest, blob)
            if err:
                ledger[a["docId"]] = f"fail: 寫檔失敗 {err}"; fail += 1; continue
            ledger[a["docId"]] = "ok"; a["downloaded"] = str(dest.relative_to(pa.DRIVE)); ok += 1; spent += 1
            pa.add_spent(1)
            print(f"  ✓ {a['date'][:7]} 《{a['journal']}》{a['title'][:40]} ({len(blob)//1024} KB)", flush=True)
            ledger_p.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
        ledger_p.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"{author}.json").write_text(json.dumps(
            {"author": author, "fetched": time.strftime("%Y-%m-%d"), "count": len(arts), "articles": arts},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {author}：本次 {ok} 成功／{fail} 失敗 → {root}")
    print(f"\n今日累計 {pa.spent_today()} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
