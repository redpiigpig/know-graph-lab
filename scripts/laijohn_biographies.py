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
# 這是一位長老義務維護的個人史料庫，站方沒有 robots.txt，也就是說禮貌完全靠自律。
# 用可辨識的 UA 而不是假扮 Chrome：對方若覺得流量礙事，至少找得到人。
UA = {"User-Agent": "KnowGraphLab-research/1.0 (+redpiigpig@gmail.com)"}
HARVEST = Path(r"C:/tmp/laijohn_pc.json")
R2_TXT = "pct-fulltext/laijohn"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct/laijohn-index.json"
DELAY = 2.0           # 義務維護的個人站；每秒兩次太快了，2 秒才是合宜的速率
MIN_CHARS = 150


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def decode(raw: bytes) -> str:
    """本站**同時有 Big5 與 UTF-8 兩種頁面**，必須逐頁嗅探。

    🚨 原本這裡寫死 `decode("big5", "replace")`，結果是 UTF-8 那批頁面
       整頁變亂碼——而 `errors="replace"` 讓它不會拋例外，抓取、寫檔、
       產索引全都「成功」。實際上 2026-09-06 回頭清點，已收的本土信徒
       4,221 篇裡有 1,930 篇（45.7%）題名是亂碼。
       這就是 [[feedback_reader_silent_failures]] 那一類：畫面完全正常、內容全錯。

    不要只看 meta charset：`/archives/pj/pj-contents.htm` 根本沒有 meta，
    卻是帶 BOM 的 UTF-8。

    🚨 **也不要用「比較替換字元數量」來猜**。第一版改成那樣，重抓完仍有 246 篇
       是亂碼：Big5 幾乎接受任何位元組對，所以 UTF-8 的內容被 Big5 解時**不會**
       產生替換字元，比大小就會一路倒向 Big5。
       正解是 **UTF-8 自我驗證**：strict 解得開就一定是 UTF-8，解不開才是 Big5。
    """
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    try:
        return raw.decode("utf-8")            # strict：過了就確定是 UTF-8
    except UnicodeDecodeError:
        return raw.decode("big5", "replace")


def get(url: str):
    """回傳解好碼的 HTML；4xx 視同沒有這一頁回 None。"""
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=45)
            if 400 <= r.status_code < 500:
                return None
            r.raise_for_status()
            return decode(r.content)
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


MOJIBAKE = ("�", "�", "嚗", "蝢", "瘣", "�")


def looks_mojibake(s):
    """題名裡出現替換字元、或 Big5 誤解 UTF-8 時特有的那幾個字，就當它壞了。

    這幾個字（嚗蝢瘣）不是罕見字，是 UTF-8 位元組被 Big5 解出來的典型產物；
    正常的台灣人名地名幾乎不會用到。
    """
    t = s or ""
    return any(m in t for m in MOJIBAKE)


def process(limit=0, redo=False, repair=False):
    """redo=True 時忽略 R2 既有、整批重抓。

    🚨 2026-09-06 需要這個旗標的理由：`get()` 原本寫死 decode("big5")，而站上
       同時有 UTF-8 的頁面，於是已收的 4,221 篇裡 1,930 篇（45.7%）題名是亂碼。
       編碼修好了，但**舊資料不會自己好**——R2 上那批仍是當初解錯碼存進去的。
       沒有這個旗標的話，「已經抓過就跳過」會讓修正永遠套不到既有資料上。
    """
    rows = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = set() if redo else df.r2_existing_keys(R2_TXT)
    # 🚨 `rows` 是**整本帳本**，結尾會原樣寫回檔案。所以要縮小處理範圍時，
    #    只能另外開一個 `targets`，**絕對不可以把 `rows` 換成過濾後的子集**——
    #    第一版那樣寫，補抓 146 篇之後帳本就從 4,234 筆被覆寫成 146 筆，
    #    其餘 4,088 筆的題名與字數全沒了，而過程一句錯誤訊息都沒有。
    targets = rows
    if repair:
        # 只補抓題名壞掉的那些。整批重跑要 2.3 小時、四千多次請求打在一個
        # 義務維護的個人站上，為了兩百多篇不值得。
        targets = [r for r in rows if looks_mojibake(r.get("title"))]
        have = set()
        print(f"補抓模式：題名疑似亂碼的 {len(targets)} 篇", flush=True)
    done = skip = fail = 0
    for r in targets:
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
    ap.add_argument("--redo", action="store_true",
                    help="忽略 R2 既有、整批重抓（編碼修正後要用）")
    ap.add_argument("--repair", action="store_true",
                    help="只補抓題名仍是亂碼的那些")
    args = ap.parse_args()
    if args.harvest:
        harvest()
    if args.process:
        process(args.limit, args.redo, args.repair)
    if args.publish:
        publish()
    if not (args.harvest or args.process or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
