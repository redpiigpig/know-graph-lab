# -*- coding: utf-8 -*-
"""查無教會系既有中譯本的可得性：有沒有電子版、有沒有館藏、還是只能買紙本。

為什麼要有這一支：REFERENCE-first 說「有中譯本就不自譯」
（[[feedback_collected_works_reference_first]]），但那條規則要能執行，得先知道
**那本書拿不拿得到**。廖本恩碩論書目給了 41 筆既有中譯，全是台灣基督教小出版社
（永望文化、人光、台灣教會公報社、中國信徒佈道會）1963–2018 的書——
**z-lib 對這種書幾乎全無命中**（帳本裡這批 0 筆紀錄），所以得換地方查。

查三處，各有各的脾氣：

  Google Books   有 API、不擋、但台灣小出版社收錄極不完整；查到也多半只有書目
  國圖 SMRT      臺灣書目整合查詢，台灣的書最齊，但回的是 HTML
  HyRead／雲端書庫  台灣電子書平台，有的話就是真的能讀

🚨 **查不到不等於沒有**。這批書多半只在教會書房與圖書館流通，網路書目本來就薄；
   NBINet 改版成 Primo 之後對 CJK 查詢更是整個失效（[[feedback_reader_silent_failures]]
   同一類：0 筆不是結論）。所以輸出分「找到」與「查無」，查無那一欄只是「線上查不到」，
   不可寫成「不存在」。

  python -X utf8 scripts/mukyokai_zh_availability.py
  python -X utf8 scripts/mukyokai_zh_availability.py --out c:/tmp/mukyokai_zh_avail.json
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
WANTED = ROOT / "data" / "zlib-wanted" / "mukyokai-chinese-translations.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PAUSE = 1.2          # 對公開 API 客氣一點


def get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def google_books(title: str, author: str) -> dict:
    """Google Books API。回傳最像的一筆，或空 dict。"""
    q = f'intitle:"{title}"'
    if author:
        q += f' inauthor:"{author}"'
    url = ("https://www.googleapis.com/books/v1/volumes?"
           + urllib.parse.urlencode({"q": q, "maxResults": 5, "country": "TW"}))
    try:
        data = json.loads(get(url))
    except urllib.error.HTTPError as e:
        # 🚨 429＝匿名日配額用盡。回 {"error":…} 給呼叫端當「查到了」是我自己踩過的坑：
        #    dict 有內容就是 truthy，於是整批錯誤被報成「有書目」。錯誤一律另立 _fail。
        return {"_fail": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"_fail": type(e).__name__}
    for it in data.get("items", []):
        vi = it.get("volumeInfo", {})
        if title.replace("：", ":")[:6] in (vi.get("title", "") or "").replace("：", ":"):
            acc = it.get("accessInfo", {})
            return {
                "title": vi.get("title"),
                "publisher": vi.get("publisher"),
                "year": (vi.get("publishedDate") or "")[:4],
                "viewability": acc.get("viewability"),      # NO_PAGES / PARTIAL / ALL_PAGES
                "epub": (acc.get("epub") or {}).get("isAvailable"),
                "pdf": (acc.get("pdf") or {}).get("isAvailable"),
                "link": vi.get("infoLink"),
            }
    return {}


def ncl_smrt(title: str) -> dict:
    """國家圖書館「臺灣書目整合查詢系統」。只看有沒有命中，不解析細目。"""
    url = ("https://metadata.ncl.edu.tw/blstkmc/blstkm?" +
           urllib.parse.urlencode({"@0": title, "!!": "1"}))
    try:
        html = get(url, timeout=40)
    except urllib.error.HTTPError as e:
        return {"_fail": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"_fail": type(e).__name__}
    hit = title[:6] in html
    return {"hit": hit, "url": url, "bytes": len(html)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--who", help="只查某位作者（例：矢内原忠雄）")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--skip-ncl", action="store_true", help="只跑 Google Books")
    args = ap.parse_args()

    rows = [json.loads(l) for l in WANTED.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.who:
        rows = [r for r in rows if r.get("who") == args.who]
    if args.limit:
        rows = rows[:args.limit]

    out = []
    for i, r in enumerate(rows, 1):
        title, who = r.get("expect") or r.get("query", ""), r.get("who", "")
        gb = google_books(title, who)
        time.sleep(PAUSE)
        ncl = {} if args.skip_ncl else ncl_smrt(title)
        if not args.skip_ncl:
            time.sleep(PAUSE)
        view = gb.get("viewability", "")
        mark = ("⚠ 查不動" if gb.get("_fail") else
                "📖 可讀" if view == "ALL_PAGES" else
                "👀 部分" if view == "PARTIAL" else
                "📇 有書目" if gb else "—")
        out.append({**r, "google_books": gb, "ncl": ncl})
        nstat = ("查不動" if ncl.get("_fail") else "命中" if ncl.get("hit") else "查無")
        print(f"{i:3}/{len(rows)} {who[:8]:10}《{title[:24]:26}》 {mark:8} "
              f"GB={gb.get('publisher','') or ('—' if gb.get('_fail') else '查無'):14} 國圖={nstat}")

    fails = sum(1 for o in out if o["google_books"].get("_fail"))
    found = sum(1 for o in out if o["google_books"] and not o["google_books"].get("_fail"))
    read = sum(1 for o in out if o["google_books"].get("viewability") in ("ALL_PAGES", "PARTIAL"))
    ncl_hit = sum(1 for o in out if o["ncl"].get("hit"))
    if fails:
        print(f"🚨 {fails} 筆**查不動**（多半是 Google Books 匿名日配額 429）"
              f"——那不是「查無」，今天的結果對這幾筆無效。")
    print(f"\n共 {len(out)} 筆：Google Books 有書目 {found}、可線上看（全部或部分）{read}、"
          f"國圖書目命中 {ncl_hit}")
    print("🚨 查無只代表線上查不到，不代表書不存在——這批多半只在教會書房與圖書館流通。")
    if args.out:
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print("已寫", args.out)


if __name__ == "__main__":
    main()
