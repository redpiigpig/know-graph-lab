"""CyberLeninka（КиберЛенинка）—— 俄文開放取用學術期刊的宗教／神學／哲學／歷史層。

俄文那一塊唯一路徑完全走通的來源：免帳號、有 JSON API、全文在網頁上。
俄國的宗教學與東正教神學研究幾乎都在這裡（各神學院學報、《宗教學問題》、
《東正教聖提洪大學學報》…），而且中文世界近乎空白。

    --search   逐題查詢 → toc.jsonl（題名／摘要／作者／年／刊名／分類）
    --fetch    逐篇抓文章頁抽全文 → text/
    --status   對帳，一律印分母

🚨 **搜尋是 POST JSON，不是 GET。** 直接 GET `/api/search` 回 405，
   很容易被當成「端點不存在」。

🚨 **`found` 永遠是 1000，那不是命中數。** 不管查什麼——連「патристика」
   這種窄題也回 1000。拿它當總數，程式會「收滿 1,000 筆」然後宣稱收齊了。

🚨 **這個 API 永遠不會說「沒有了」。** `from` 開到 3000 它照樣吐 100 筆
   不重複的連結。實測「патристика」翻到 1,400 筆都還在吐，但**相關度早就崩了**：

       from=0    標題/摘要含「патрист」 65／100
       from=200                        69／100
       from=400                        11／100   ← 開始脫離
       from=900                         0／100
       from=1300                        3／100   （還在吐）

   所以**停止條件是相關度不是抓完**。連續 STOP_PAGES 頁的命中率低於
   MIN_HIT_RATE 就收工。不這樣做，帳面上會是「收了 1,400 篇патристика
   論文」，實際上後一千篇跟主題無關——而且從數字上完全看不出來。

  python scripts/cyberleninka_harvest.py --search
  python scripts/cyberleninka_harvest.py --search --only патристика
  python scripts/cyberleninka_harvest.py --fetch --limit 200
  python scripts/cyberleninka_harvest.py --status
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

API = "https://cyberleninka.ru/api/search"
SITE = "https://cyberleninka.ru"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/cyberleninka")
TOC = ROOT / "toc.jsonl"
TEXT_DIR = ROOT / "text"
LEDGER = Path(__file__).resolve().parent / "state" / "cyberleninka_ledger.jsonl"
QUERIES = Path(__file__).resolve().parent.parent / "data" / "cyberleninka-queries.txt"

PAGE = 100            # API 單次上限實測可到 100
SEARCH_SLEEP = 0.8
FETCH_SLEEP = 1.5     # 抓全文更客氣：這是別人免費開放的東西
MIN_CHARS = 1000      # 低於此視為沒抽到全文
# 相關度停止條件（見檔頭）
MIN_HIT_RATE = 0.15   # 該頁標題／摘要含查詢詞的比例
STOP_PAGES = 3        # 連續幾頁低於門檻就收工
MAX_FROM = 3000       # 再怎樣也不往下翻了

BODY = re.compile(r'itemprop="articleBody"[^>]*>(.*)', re.S)
PARA = re.compile(r"<p[^>]*>(.*?)</p>", re.S)
TAG = re.compile(r"<[^>]+>")


def strip_tags(s: str) -> str:
    return TAG.sub("", s)


def clean(s: str) -> str:
    s = strip_tags(s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    s = s.replace("\ufeff", "").replace("\u00ad", "").replace("\u200b", "")
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"[ \t]+", " ", s).strip()


def post(payload: dict, tries: int = 4) -> dict:
    data = json.dumps(payload).encode()
    for k in range(tries):
        try:
            req = urllib.request.Request(API, data=data, headers={
                "User-Agent": UA, "Content-Type": "application/json", "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception:                          # noqa: BLE001
            if k == tries - 1:
                raise
            time.sleep(2 ** k)
    return {}


def get(url: str, tries: int = 3) -> str | None:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                return None
            if k == tries - 1:
                raise
        except Exception:                          # noqa: BLE001
            if k == tries - 1:
                raise
        time.sleep(2 ** k)
    return None


def slug(link: str) -> str:
    """`/article/n/paradoksy-v-patristike` → `paradoksy-v-patristike`。"""
    return link.rstrip("/").rsplit("/", 1)[-1]


def stem(word: str) -> str:
    """查詢詞取前六個字母當詞幹——俄文格變化多，整詞比對會漏掉一半。

    「патристика」的詞幹「патрис」同時吃得到 патристики／патристике／
    патристику。取太短會亂命中，六個字母是實測堪用的長度。
    """
    w = re.sub(r"[^\w]", "", word.lower())
    return w[:6] if len(w) > 6 else w


def relevant(art: dict, stems: list[str]) -> bool:
    hay = (strip_tags(art.get("name") or "") + " "
           + strip_tags(art.get("annotation") or "")).lower()
    return any(s in hay for s in stems)


def load_queries(only: str | None) -> list[str]:
    if only:
        return [only]
    if not QUERIES.exists():
        sys.exit(f"沒有查詢清單：{QUERIES}")
    out = []
    for line in QUERIES.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def load_toc() -> dict[str, dict]:
    if not TOC.exists():
        return {}
    out = {}
    for line in TOC.open(encoding="utf-8"):
        if line.strip():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            out[r["slug"]] = r
    return out


def cmd_search(args) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    have = load_toc()
    print(f"篇目已有 {len(have):,} 筆")
    queries = load_queries(args.only)
    added = 0
    with TOC.open("a", encoding="utf-8") as fh:
        for qi, q in enumerate(queries, 1):
            stems = [stem(w) for w in q.split() if len(w) > 3] or [stem(q)]
            cold = 0
            got = kept = 0
            for frm in range(0, MAX_FROM, PAGE):
                try:
                    d = post({"mode": "articles", "q": q, "size": PAGE, "from": frm})
                except Exception as e:             # noqa: BLE001
                    print(f"   ✗ {q} from={frm}：{type(e).__name__}")
                    break
                arts = d.get("articles") or []
                if not arts:
                    break
                got += len(arts)
                hits = sum(1 for a in arts if relevant(a, stems))
                for a in arts:
                    if not relevant(a, stems):
                        continue          # 只收真的相關的，不是回什麼收什麼
                    s = slug(a.get("link") or "")
                    if not s or s in have:
                        continue
                    rec = {
                        "slug": s,
                        "link": a.get("link"),
                        "title": clean(a.get("name") or ""),
                        "annotation": clean(a.get("annotation") or ""),
                        "authors": a.get("authors") or [],
                        "year": a.get("year"),
                        "journal": a.get("journal"),
                        "journal_link": a.get("journal_link"),
                        "catalogs": a.get("catalogs") or [],
                        "query": q,
                    }
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    have[s] = rec
                    kept += 1
                    added += 1
                fh.flush()
                rate = hits / len(arts)
                cold = cold + 1 if rate < MIN_HIT_RATE else 0
                if cold >= STOP_PAGES:
                    break
                time.sleep(SEARCH_SLEEP)
            print(f"  [{qi}/{len(queries)}] {q[:34]:<36}翻了 {got:>5} 筆，"
                  f"收 {kept:>4}（相關度跌破後停）", flush=True)
    print(f"\n✓ 新增 {added:,} 筆，篇目共 {len(have):,} → {TOC}")


def cmd_fetch(args) -> None:
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    toc = load_toc()
    if not toc:
        sys.exit("篇目是空的，先跑 --search")
    have = {p.stem for p in TEXT_DIR.glob("*.txt")}
    todo = [r for r in toc.values() if r["slug"] not in have]
    if args.limit:
        todo = todo[: args.limit]
    print(f"篇目 {len(toc):,}，已抽 {len(have):,}，本輪 {len(todo):,}")
    ok = thin = miss = 0
    with LEDGER.open("a", encoding="utf-8") as lg:
        for i, r in enumerate(todo, 1):
            h = get(SITE + r["link"])
            if h is None:
                miss += 1
                lg.write(json.dumps({"slug": r["slug"], "status": "not-found"},
                                    ensure_ascii=False) + "\n")
                time.sleep(FETCH_SLEEP)
                continue
            m = BODY.search(h)
            # 🚨 不要用 `</div></div>` 收尾——正文容器裡巢著一個廣告 div，
            #    那樣會在廣告那裡就收掉，抽出 0 字而且不會報錯。
            #    正文整個是 <p>，直接把容器之後的 <p> 全撈出來最穩。
            paras = [clean(x) for x in PARA.findall(m.group(1))] if m else []
            text = "\n\n".join(p for p in paras if p)
            if len(text) < MIN_CHARS:
                thin += 1
                lg.write(json.dumps({"slug": r["slug"], "status": "thin",
                                     "chars": len(text)}, ensure_ascii=False) + "\n")
            else:
                (TEXT_DIR / f"{r['slug']}.txt").write_text(text, encoding="utf-8")
                ok += 1
                lg.write(json.dumps({"slug": r["slug"], "status": "ok",
                                     "chars": len(text)}, ensure_ascii=False) + "\n")
            lg.flush()
            if i % 50 == 0:
                print(f"   …{i}/{len(todo)}　成功 {ok}／薄 {thin}／缺 {miss}", flush=True)
            time.sleep(FETCH_SLEEP)
    print(f"✓ 抽出 {ok:,} 篇（正文太薄 {thin}、頁面不在 {miss}）→ {TEXT_DIR}")


def cmd_status(args) -> None:
    toc = load_toc()
    if not toc:
        print(f"篇目還沒有：{TOC}")
        return
    txts = {p.stem for p in TEXT_DIR.glob("*.txt")} if TEXT_DIR.exists() else set()
    chars = sum(p.stat().st_size for p in TEXT_DIR.glob("*.txt")) if TEXT_DIR.exists() else 0
    print(f"篇目　　{len(toc):>7,}")
    print(f"已抽全文{len(txts):>7,}　{len(txts) / len(toc) * 100:.1f}%　"
          f"約 {chars / 1048576:.0f} MB")

    from collections import Counter
    years = Counter(str(r.get("year") or "?") for r in toc.values())
    jour = Counter(str(r.get("journal") or "?") for r in toc.values())
    q = Counter(r.get("query") or "?" for r in toc.values())
    print(f"\n刊物 {len(jour):,} 種，最大宗：")
    for n, c in jour.most_common(8):
        print(f"   {n[:44]:<46}{c:>5}")
    print(f"\n查詢詞 {len(q)} 個，產出最多：")
    for n, c in q.most_common(8):
        print(f"   {n[:30]:<32}{c:>5}")
    ys = [int(y) for y in years if y.isdigit()]
    if ys:
        print(f"\n年代 {min(ys)}–{max(ys)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--only", help="只跑這一個查詢詞")
    ap.add_argument("--limit", type=int, help="--fetch 本輪上限")
    a = ap.parse_args()
    if a.search:
        cmd_search(a)
    elif a.fetch:
        cmd_fetch(a)
    elif a.status:
        cmd_status(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
