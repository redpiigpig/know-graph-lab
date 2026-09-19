"""Unpaywall —— 把既有的 45 萬筆 Crossref DOI 換成可下載的開放取用全文。

`crossref_harvest.py` 收了 **821 刊・452,459 篇**宗教學／神學論文的
metadata，每一筆都有 DOI，但**一篇全文都沒有**。Unpaywall 就是做
「DOI → 合法 OA 全文位置」這件事的，免費、免帳號（只要帶 email）。

實測（2026-09-16，母體隨機抽 120 篇）：**OA 26%、有直接 PDF 連結 21%**，
Unpaywall 查不到的 0 筆。外推全庫 → 約 **11.7 萬篇 OA、9.4 萬篇可直接下載**。
命中的多半是各國的神學院學報與大學 OJS 期刊（印尼、波蘭、南非、
烏克蘭、智利、斯里蘭卡…），正好是本專案缺的「非英美視角」那一塊。

🚨 **抽樣要按「篇」不能按「刊」。** 第一次估的時候是「每一刊抽一篇」，
   得到 67%——把只有幾十篇的小型 OA 學報和有上萬篇的老牌封閉期刊
   等權重看待，高估了兩倍半。而且那個數字看起來完全合理，是實際跑
   起來只有 1% 才發現的（檔案是按 ISSN 排序，開頭那幾刊剛好是
   JAAR 這種老牌封閉期刊）。**要估母體比例，就要從母體抽。**

兩階段，而且**刻意分開**：

    --resolve   只查位置，不下載。每筆一個 HTTP 請求、幾 KB。
                45 萬筆跑完就知道「到底有多少拿得到」，這是分母。
    --fetch     真的下載 PDF。9.4 萬篇 × 約 1 MB ≈ 94 GB、
                以 2 秒一篇要 52 小時，**不該無差別全下**，
                所以吃 --journal／--year／--limit 篩選。

  python scripts/unpaywall_resolve.py --resolve            # 全跑（可續跑）
  python scripts/unpaywall_resolve.py --resolve --limit 2000
  python scripts/unpaywall_resolve.py --status
  python scripts/unpaywall_resolve.py --fetch --journal "HTS" --limit 200

🚨 **要帶 email，而且要守它的用量。** Unpaywall 是非營利的，官方請求
   每天不超過 100k 次。45 萬筆要分五天跑完——`--resolve` 本來就可續跑，
   排程每天跑一趟即可，不要一次灌爆別人的服務。

🚨 **`is_oa` 為真不等於拿得到 PDF。** 有的只有 landing page（`url`）
   沒有 `url_for_pdf`；有的 `host_type` 是 publisher 的 bronze
   ——看得到讀得到但沒有授權聲明。本檔把 `pdf_url`／`landing_url`／
   `license`／`host_type`／`version` 全記下來，**不要只存一個 url
   就當成「有全文」**，那會讓後面下載時才發現一半是 HTML 目次頁。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CORPUS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/crossref")
OUT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/unpaywall")
RESOLVED = OUT / "resolved.jsonl"
PDF_DIR = OUT / "pdf"
FETCH_FAILED = OUT / "fetch-failed.jsonl"   # 抓不到的 DOI，下一輪別再排隊

EMAIL = "redpiigpig@gmail.com"
API = "https://api.unpaywall.org/v2/"
UA = f"know-graph-lab/1.0 (academic research; {EMAIL})"

# 官方請求每日不超過 100k 次。實測請求本身約 0.63 秒，所以整個週期要
# 湊到 0.86 秒才會落在 ~99k/日。先前設 0.12 實測跑出 1.33 筆/秒＝11.5 萬/日，
# **超過人家的請求**，改成 0.23。
RESOLVE_SLEEP = 0.23
FETCH_SLEEP = 2.0        # 下載對各家 OJS 站客氣點
MAX_PDF_MB = 60


def get(url: str, timeout: int = 30, tries: int = 3) -> bytes | None:
    """回 bytes；404 回 None（Unpaywall 對它不認得的 DOI 就回 404）。"""
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 422):
                return None
            if k == tries - 1:
                raise
        except Exception:                          # noqa: BLE001
            if k == tries - 1:
                raise
        time.sleep(2 ** k)
    return None


def _one_journal(f: Path):
    issn = f.stem
    with f.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("doi"):
                r["issn"] = issn
                yield r


def crossref_rows():
    """逐刊讀 Crossref 收成，但**輪流**不是一刊跑完再下一刊。

    821 個檔、45 萬列，不要一次全載進記憶體。

    🚨 為什麼要輪流：檔案是按 ISSN 排序的，開頭幾刊剛好是 JAAR 這種
       老牌封閉期刊，一路跑下去前一萬筆的 OA 命中率只有 1%——整整幾小時
       查下來一篇都下載不了，而且會讓人以為「Unpaywall 對這個領域沒用」。
       輪流查的話每一刊都會早早被碰到，OA 豐富的那些小型學報立刻現形，
       `--fetch` 也才有東西可下。全部查完的總量一樣，只是次序不同。
    """
    gens = [_one_journal(f) for f in sorted(CORPUS.glob("*.jsonl"))]
    while gens:
        alive = []
        for g in gens:
            try:
                yield next(g)
                alive.append(g)
            except StopIteration:
                pass
        gens = alive


def done_dois() -> set[str]:
    if not RESOLVED.exists():
        return set()
    out = set()
    for line in RESOLVED.open(encoding="utf-8"):
        if line.strip():
            try:
                out.add(json.loads(line)["doi"])
            except (ValueError, KeyError):
                pass
    return out


def cmd_resolve(args) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    seen = done_dois()
    print(f"已查過 {len(seen):,} 筆")
    n = oa = pdf = miss = 0
    t0 = time.time()
    with RESOLVED.open("a", encoding="utf-8") as fh:
        for r in crossref_rows():
            doi = r["doi"]
            if doi in seen:
                continue
            if args.limit and n >= args.limit:
                break
            url = API + urllib.parse.quote(doi) + f"?email={EMAIL}"
            try:
                body = get(url)
            except Exception as e:                 # noqa: BLE001
                print(f"   ✗ {doi}：{type(e).__name__}")
                break                              # 連不上就停，下次續跑
            n += 1
            if body is None:
                miss += 1
                rec = {"doi": doi, "issn": r["issn"], "found": False}
            else:
                j = json.loads(body.decode("utf-8", "replace"))
                loc = j.get("best_oa_location") or {}
                is_oa = bool(j.get("is_oa"))
                oa += is_oa
                pdf += bool(loc.get("url_for_pdf"))
                # 🚨 五個欄位全留。只存一個 url 的話，下載時才會發現
                #    一半是 landing page 而不是 PDF，而那時已經沒有
                #    license／host_type 可以判斷了。
                rec = {
                    "doi": doi, "issn": r["issn"], "found": True,
                    "is_oa": is_oa,
                    "pdf_url": loc.get("url_for_pdf"),
                    "landing_url": loc.get("url"),
                    "host_type": loc.get("host_type"),
                    "license": loc.get("license"),
                    "version": loc.get("version"),
                    "journal": j.get("journal_name") or r.get("journal"),
                    "year": j.get("year") or r.get("year"),
                    "title": (j.get("title") or r.get("title") or "")[:300],
                }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if n % 200 == 0:
                fh.flush()
                rate = n / max(1e-9, time.time() - t0)
                print(f"   …{n:,} 筆　OA {oa:,}（{oa / n * 100:.0f}%）"
                      f"　有 PDF {pdf:,}　查無 {miss}　{rate:.1f} 筆/秒", flush=True)
            time.sleep(RESOLVE_SLEEP)
    print(f"\n✓ 本輪查 {n:,} 筆：OA {oa:,}、其中有直接 PDF {pdf:,}、Unpaywall 查無 {miss}")


def load_resolved() -> list[dict]:
    if not RESOLVED.exists():
        sys.exit(f"還沒查過，先跑 --resolve：{RESOLVED}")
    out = []
    for line in RESOLVED.open(encoding="utf-8"):
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def cmd_status(args) -> None:
    rows = load_resolved()
    total = sum(1 for _ in CORPUS.glob("*.jsonl"))
    oa = [r for r in rows if r.get("is_oa")]
    withpdf = [r for r in oa if r.get("pdf_url")]
    have = {p.stem for p in PDF_DIR.glob("*.pdf")} if PDF_DIR.exists() else set()
    print(f"Crossref 收成　{452459:>9,} 筆（{total} 刊）")
    print(f"已查 Unpaywall {len(rows):>9,}　（{len(rows) / 452459 * 100:.1f}%）")
    print(f"其中 OA　　　　{len(oa):>9,}　（{len(oa) / max(1, len(rows)) * 100:.0f}%）")
    print(f"有直接 PDF 連結{len(withpdf):>9,}　（{len(withpdf) / max(1, len(rows)) * 100:.0f}%）")
    print(f"已下載　　　　　{len(have):>9,}")
    lic = Counter(str(r.get("license") or "（無授權聲明）") for r in oa)
    print("\n授權（🚨 NC／ND 對營利用途等於不能用，且看不出來）：")
    for k, v in lic.most_common(8):
        print(f"   {k:<24}{v:>8,}")
    host = Counter(str(r.get("host_type") or "?") for r in oa)
    print("\n來源類型：", dict(host.most_common()))
    jour = Counter(str(r.get("journal") or "?")[:40] for r in withpdf)
    print(f"\n有 PDF 的刊物 {len(jour):,} 種，最大宗：")
    for k, v in jour.most_common(10):
        print(f"   {k:<42}{v:>6,}")


def cmd_fetch(args) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    rows = [r for r in load_resolved() if r.get("pdf_url")]
    if args.journal:
        rows = [r for r in rows if args.journal.lower() in str(r.get("journal", "")).lower()]
    if args.year:
        rows = [r for r in rows if str(r.get("year")) == str(args.year)]
    have = {p.stem for p in PDF_DIR.glob("*.pdf")}
    # 🚨 待辦是按「有沒有 .pdf」算的，所以抓不到的那四成（403／landing page／SSL）
    #    會永遠留在待辦裡，而且因為 --limit 取的是前 N 筆，它們會堆在最前面，
    #    跑幾輪之後整輪都在重試同一批死目標，新的永遠輪不到。記一份失敗帳本跳過。
    #    要重試就刪掉 fetch-failed.jsonl（403 有可能是暫時的）。
    failed = set()
    if FETCH_FAILED.exists():
        for line in FETCH_FAILED.open(encoding="utf-8"):
            if line.strip():
                try:
                    failed.add(json.loads(line)["doi"])
                except (ValueError, KeyError):
                    pass
    todo = [r for r in rows
            if slugify(r["doi"]) not in have and r["doi"] not in failed]
    if args.limit:
        todo = todo[: args.limit]
    print(f"符合條件 {len(rows):,} 筆，已下 {len(rows) - len([r for r in rows if slugify(r['doi']) not in have]):,}，本輪 {len(todo):,}")
    # 🚨 別把 403／HTML landing page／SSL 失敗混成同一個 bad 計數。
    #    2026-09-19 抽樣 25 筆：PDF 成功 13、403 六、HTML 五、SSL 一——四種原因
    #    四種對策（403 是對方擋腳本、HTML 是 landing page 擋下來是對的、SSL 是人家
    #    憑證壞了），混成一句「非 PDF 或失敗」就完全看不出該不該處理。
    ok = big = 0
    why = Counter()
    fl = FETCH_FAILED.open('a', encoding='utf-8')
    for i, r in enumerate(todo, 1):
        try:
            b = get(r["pdf_url"], timeout=90)
        except urllib.error.HTTPError as e:
            why[f"HTTP {e.code}"] += 1
            fl.write(json.dumps({'doi': r['doi'], 'why': f"HTTP {e.code}"},
                                ensure_ascii=False) + '\n')
            time.sleep(FETCH_SLEEP)
            continue
        except Exception as e:                     # noqa: BLE001
            why[type(e).__name__] += 1
            fl.write(json.dumps({'doi': r['doi'], 'why': type(e).__name__},
                                ensure_ascii=False) + '\n')
            time.sleep(FETCH_SLEEP)
            continue
        if not b:
            why['空回應'] += 1
            fl.write(json.dumps({'doi': r['doi'], 'why': '空回應'},
                                ensure_ascii=False) + '\n')
        elif len(b) > MAX_PDF_MB * 1024 * 1024:
            big += 1
        elif not b[:5].startswith(b"%PDF"):
            # 🚨 OA 連結常常回 HTML 的 landing page 而不是 PDF，
            #    而檔案大小看起來完全正常。存進去就會變成一堆
            #    「打得開但沒有內文」的假 PDF。
            why['HTML landing page（非 PDF）'] += 1
            fl.write(json.dumps({'doi': r['doi'], 'why': 'HTML landing page'},
                                ensure_ascii=False) + '\n')
        else:
            (PDF_DIR / f"{slugify(r['doi'])}.pdf").write_bytes(b)
            ok += 1
        if i % 25 == 0:
            print(f"   …{i}/{len(todo)}　成功 {ok}／沒拿到 {sum(why.values())}／過大 {big}", flush=True)
        time.sleep(FETCH_SLEEP)
    fl.close()
    print(f"✓ 下載 {ok:,}（超過 {MAX_PDF_MB}MB 跳過 {big}）→ {PDF_DIR}")
    if why:
        print("  沒拿到的原因：" + "、".join(f"{k} {v}" for k, v in why.most_common()))


def slugify(doi: str) -> str:
    return doi.replace("/", "_").replace(":", "_")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--journal")
    ap.add_argument("--year")
    a = ap.parse_args()
    if a.resolve:
        cmd_resolve(a)
    elif a.fetch:
        cmd_fetch(a)
    elif a.status:
        cmd_status(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
