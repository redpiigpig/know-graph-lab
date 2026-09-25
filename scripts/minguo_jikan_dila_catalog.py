# -*- coding: utf-8 -*-
"""法鼓 DILA「民國佛教期刊文獻集成」資料庫 → 全集篇目 TSV ＋ 太虛相關優先清單。

跟 `haichaoyin_dila_toc.py`（只抓《海潮音》一刊）的差別：這支抓**整個資料庫**
（正編 MFQ 96,109 筆＋補編 MFQB 43,410 筆，2026-09-25 查得），因為 OCR 全集之後要
按篇目把每一冊切成單篇，每一刊都要有篇目；太虛優先清單也不能只看《海潮音》。

DILA 的 search.php 參數（從表單讀出來的）：
    edition=MFQ|MFQB|both       正編／補編／全部
    spValue=關鍵字               查文章名／期刊名／作者名，🚨 要一併送三個 checkbox
                                 myLessAreaTitle=on&myLessAreaJournalName=on&myLessAreaAuthor=on，
                                 不送就回一頁空表單（不是 0 筆，是根本沒查）
    paperAuthor=太虛             作者精確查
    journalName=海潮音           刊名
    start=N                      每頁 30 筆
每筆有「叢刊資訊：MFQ,vol.171,p.315~317」（集成冊與頁）與「原書資訊：<刊名>,v.9,no.10,p.1~3,日期」。

快取每一頁 HTML 到 output/minguo_jikan/dila_pages/<query-slug>/<start>.html，可中斷續跑；
重跑只補缺頁。逐頁間隔 1 秒，不要打爆 DILA。

用法：
    python -X utf8 scripts/minguo_jikan_dila_catalog.py crawl            # 整庫（約 4,650 頁、90 分鐘）
    python -X utf8 scripts/minguo_jikan_dila_catalog.py crawl --edition MFQB
    python -X utf8 scripts/minguo_jikan_dila_catalog.py quick            # 只抓太虛關鍵字／作者查詢（幾分鐘），先出優先清單
    python -X utf8 scripts/minguo_jikan_dila_catalog.py build            # 由快取產出 _篇目_全集.tsv 與 _篇目_太虛相關_全集.tsv
    python -X utf8 scripts/minguo_jikan_dila_catalog.py build --dry-run  # 只印統計，不寫 Drive

產出（Drive 集成夾 `研究資料\\民國與台灣佛教史\\民國佛教期刊文獻集成\\`）：
    _篇目_全集.tsv               整庫篇目（crawl 完才完整；quick 之後只有查詢命中的那些）
    _篇目_太虛相關_全集.tsv       叢刊、冊、集成頁、篇名、作者、原刊、原刊卷期、原刊頁、命中關鍵字
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_mod
import json
import re
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "minguo_jikan" / "dila_pages"
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成")
OUT_FULL = DRIVE / "_篇目_全集.tsv"
OUT_TAIXU = DRIVE / "_篇目_太虛相關_全集.tsv"
BASE = "http://buddhistinformatics.dila.edu.tw/minguofojiaoqikan/search.php"
UA = "know-graph-lab research (redpiigpig@gmail.com)"
PER_PAGE = 30
GAP = 1.0

# 太虛優先清單的關鍵字：篇名或作者含任一個就算命中。
TAIXU_KEYWORDS = ["太虛", "世界佛學苑", "世苑", "漢藏教理院", "武昌佛學院", "閩南佛學院",
                  "柏林教理院", "巴利三藏院", "錫蘭留學", "法舫", "法尊"]
# quick 模式要跑的查詢（作者精確查一個，關鍵字全欄位查各一個）
QUICK_QUERIES = [{"paperAuthor": "太虛", "edition": "both"}] + [
    {"spValue": k, "edition": "both",
     "myLessAreaTitle": "on", "myLessAreaJournalName": "on", "myLessAreaAuthor": "on"}
    for k in TAIXU_KEYWORDS]

EDITION_NAME = {"MFQ": "正編", "MFQB": "補編"}
COLS = ["叢刊", "冊", "集成頁", "篇名", "作者", "原刊", "原刊卷", "原刊期", "原刊頁", "日期",
        "類別", "dila_id", "原書資訊原文"]


# ── 純函式：解析 ────────────────────────────────────────────────────────────

def _text(x: str) -> str:
    return re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", x))).replace("\ufeff", "").strip()


def total_hits(page_html: str) -> int | None:
    """有結果時是 `<span>2526筆</span>`；0 筆時是「回傳結果 : 0筆，你可以嘗試別的關鍵字」。"""
    m = re.search(r"<span>(\d+)筆</span>", page_html) or re.search(r"回傳結果</a>\s*[:：]\s*<span>(\d+)筆", page_html)
    return int(m.group(1)) if m else None


def parse_page(page_html: str) -> list[dict]:
    """一頁 HTML → 篇目 rows（欄位見 COLS）。"""
    out: list[dict] = []
    for blk in re.split(r'<div class="resultItem">', page_html)[1:]:
        blk = blk.split('<hr class="tailHr"')[0]
        idm = re.search(r'<a href="#top" title="(\d+)"', blk)
        title = re.search(r'<div class="paperTitle">(.*?)</div>', blk, re.S)
        infos = [(_text(x), x) for x in re.findall(r'<div class="showItemInfo">(.*?)</div>', blk, re.S)]
        d = {c: "" for c in COLS}
        d["dila_id"] = idm.group(1) if idm else ""
        tt = _text(title.group(1)) if title else ""
        m = re.match(r"\d+\s+(.*)", tt)
        d["篇名"] = (m.group(1) if m else tt).strip("『』").strip()
        for inf, raw in infos:
            if inf.startswith("叢刊資訊"):
                m = re.search(r"(MFQB|MFQ)\s*,\s*vol\.\s*(\d+)\s*,\s*p\.\s*([\w~\-?]+)", inf)
                if m:
                    d["叢刊"] = EDITION_NAME[m.group(1)]
                    d["冊"] = m.group(2)
                    d["集成頁"] = m.group(3)
            elif inf.startswith("原書資訊"):
                body = inf.split("：", 1)[1].strip()
                jm = re.search(r'journalName=([^"&]+)', raw)
                d["原刊"] = urllib.parse.unquote(jm.group(1)).replace("\ufeff", "").strip() if jm else body.split(",")[0]
                v = re.search(r"\bv\.\s*([\w\-]+)", body)
                n = re.search(r"\bno\.\s*([\w\-/~]+)", body)
                p = re.search(r"\bp\.\s*([\w~\-]+)", body)
                d["原刊卷"] = v.group(1) if v else ""
                d["原刊期"] = n.group(1) if n else ""
                d["原刊頁"] = p.group(1) if p else ""
                parts = [x.strip() for x in body.split(",")]
                last = parts[-1] if parts else ""
                d["日期"] = last if re.match(r"\d{4}", last) else ""
                d["原書資訊原文"] = body.replace("未登錄日期", "").rstrip(", ")
            elif inf.startswith("文章類別"):
                d["類別"] = inf.split("：", 1)[1].strip()
            elif inf.startswith("作者"):
                a = inf.split("：", 1)[1].strip()
                d["作者"] = "" if "無記作者" in a else "；".join(a.split())
        out.append(d)
    return out


def page_range(s: str) -> tuple[int, int] | None:
    """'315~317' → (315, 317)；'315' → (315, 315)；解析不出來回 None。"""
    m = re.match(r"(\d+)(?:\s*~\s*(\d+))?", s or "")
    if not m:
        return None
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    if b < a or b - a > 600:          # DILA 偶有「5730574」這種黏字
        return None
    return a, b


def taixu_hits(row: dict, keywords=TAIXU_KEYWORDS) -> list[str]:
    """這一筆命中哪些關鍵字（篇名或作者）。作者＝太虛另記「作者太虛」。"""
    hay = f"{row.get('篇名', '')}\n{row.get('作者', '')}"
    hits = [k for k in keywords if k in hay]
    if "太虛" in (row.get("作者") or ""):
        hits.append("作者太虛")
    return hits


def row_key(row: dict) -> tuple:
    return (row.get("dila_id") or "", row.get("叢刊"), row.get("冊"), row.get("集成頁"), row.get("篇名"))


# ── 抓取（快取） ─────────────────────────────────────────────────────────────

def query_slug(q: dict) -> str:
    key = "&".join(f"{k}={v}" for k, v in sorted(q.items()) if k != "start")
    h = hashlib.md5(key.encode("utf-8")).hexdigest()[:8]
    label = re.sub(r"[^\w\u4e00-\u9fff]+", "_", (q.get("paperAuthor") or q.get("spValue") or q.get("journalName") or "all"))
    return f"{q.get('edition', 'both')}_{label}_{h}"


def fetch_page(session, q: dict, start: int) -> str:
    d = CACHE / query_slug(q)
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{start:06d}.html"
    if f.exists() and f.stat().st_size > 2000:
        return f.read_text(encoding="utf-8")
    for i in range(5):
        try:
            r = session.get(BASE, params={**q, "start": start}, timeout=60)
            r.raise_for_status()
            t = r.content.decode("utf-8", "replace")
            if "resultItem" not in t and total_hits(t) is None:
                raise RuntimeError("頁面不含結果（參數錯或站上出錯）")
            f.write_text(t, encoding="utf-8")
            time.sleep(GAP)
            return t
        except Exception as e:
            print(f"  start={start} 失敗：{e}", flush=True)
            time.sleep(10 * (i + 1))
    raise RuntimeError(f"{query_slug(q)} start={start} 抓不到")


def crawl_query(session, q: dict, label: str) -> int:
    first = fetch_page(session, q, 0)
    total = total_hits(first) or 0
    npages = (total + PER_PAGE - 1) // PER_PAGE
    have = sum(1 for s in range(0, total, PER_PAGE)
               if (CACHE / query_slug(q) / f"{s:06d}.html").exists())
    print(f"[{label}] {total} 筆，{npages} 頁（快取已有 {have}）", flush=True)
    t0 = time.time()
    for i, start in enumerate(range(0, total, PER_PAGE)):
        fetch_page(session, q, start)
        if i and i % 200 == 0:
            print(f"  [{label}] {i}/{npages} 頁，{(time.time() - t0) / 60:.0f} 分", flush=True)
    return total


def load_cached_rows() -> tuple[list[dict], dict]:
    """把快取裡所有查詢的所有頁都解析出來、去重。回傳 (rows, 每個查詢的頁數)。"""
    seen: dict[tuple, dict] = {}
    stats: dict[str, int] = {}
    for qd in sorted(CACHE.glob("*")):
        if not qd.is_dir():
            continue
        n = 0
        for f in sorted(qd.glob("*.html")):
            for r in parse_page(f.read_text(encoding="utf-8")):
                seen.setdefault(row_key(r), r)
            n += 1
        stats[qd.name] = n
    return list(seen.values()), stats


# ── 產出 ─────────────────────────────────────────────────────────────────────

def write_tsv(rows: list[dict], cols: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".part")
    with open(tmp, "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def sort_key(r: dict):
    pr = page_range(r.get("集成頁", "")) or (10 ** 6, 10 ** 6)
    return (r.get("叢刊") or "", int(r["冊"]) if (r.get("冊") or "").isdigit() else 10 ** 6, pr[0], pr[1])


def build_taixu(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        hits = taixu_hits(r)
        if hits:
            out.append({**r, "命中關鍵字": "、".join(hits)})
    out.sort(key=sort_key)
    return out


def volume_stats(rows: list[dict]) -> list[tuple[str, int, int, int]]:
    """(叢刊, 冊, 篇數, 涉及頁數) 依冊排序。"""
    by: dict[tuple, list] = defaultdict(list)
    for r in rows:
        if (r.get("冊") or "").isdigit():
            by[(r["叢刊"], int(r["冊"]))].append(r)
    out = []
    for (ed, vol), rs in sorted(by.items()):
        pages: set[int] = set()
        for r in rs:
            pr = page_range(r.get("集成頁", ""))
            if pr:
                pages.update(range(pr[0], pr[1] + 1))
        out.append((ed, vol, len(rs), len(pages)))
    return out


def cmd_crawl(a) -> int:
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = UA
    eds = ["MFQ", "MFQB"] if a.edition == "all" else [a.edition]
    for ed in eds:
        crawl_query(s, {"edition": ed}, ed)
    return 0


def cmd_quick(a) -> int:
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = UA
    for q in QUICK_QUERIES:
        crawl_query(s, q, q.get("paperAuthor") and f"作者={q['paperAuthor']}" or f"關鍵字={q['spValue']}")
    return cmd_build(a)


def cmd_build(a) -> int:
    rows, stats = load_cached_rows()
    full_done = all(k in stats for k in ("MFQ_all_", "MFQB_all_")) or any(
        k.startswith("MFQ_all") for k in stats) and any(k.startswith("MFQB_all") for k in stats)
    print(f"快取查詢 {len(stats)} 個、合計 {sum(stats.values())} 頁 → 去重後 {len(rows)} 筆"
          f"{'' if full_done else '（🚨 整庫尚未抓完，這是查詢命中的子集）'}")
    tx = build_taixu(rows)
    vs = volume_stats(tx)
    print(f"太虛相關：{len(tx)} 筆，涉及 {len(vs)} 冊，"
          f"約 {sum(p for *_, p in vs)} 個集成頁")
    kw = Counter(k for r in tx for k in r["命中關鍵字"].split("、"))
    print("  命中關鍵字：" + "、".join(f"{k} {n}" for k, n in kw.most_common()))
    print("  冊次（叢刊 冊：篇數/頁數）：" + "；".join(f"{e}{v}：{n}/{p}" for e, v, n, p in vs))
    if a.dry_run:
        return 0
    if not DRIVE.exists():
        print(f"⛔ Drive 集成夾不在：{DRIVE}（G: 卡住？）")
        return 3
    rows.sort(key=sort_key)
    write_tsv(rows, COLS, OUT_FULL)
    write_tsv(tx, COLS + ["命中關鍵字"], OUT_TAIXU)
    print(f"寫出 {OUT_FULL.name}（{len(rows)}）與 {OUT_TAIXU.name}（{len(tx)}）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crawl")
    c.add_argument("--edition", choices=["MFQ", "MFQB", "all"], default="all")
    c.set_defaults(func=cmd_crawl)
    q = sub.add_parser("quick")
    q.add_argument("--dry-run", action="store_true")
    q.set_defaults(func=cmd_quick)
    b = sub.add_parser("build")
    b.add_argument("--dry-run", action="store_true")
    b.set_defaults(func=cmd_build)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
