#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""某一個領域「最有影響力的 N 篇研究」清單 → /research-data/top-papers/<field> 的資料。

通用版：換一個領域只要多一個資料夾，不用改這支。使用者 2026-09-26 定調這是常規
用法（「抓 500 篇最有影響力研究以後會是我的常規用法……其他領域也可能如此」），
首例是聖經研究（舊約／新約／次經與典外／批判史四組）。

輸入（都在 data/research-data/<field>/）：
  top-papers.config.json   領域標題、說明、分組（slug／name／icon／desc）、相關連結
  top*.jsonl               一行一筆：group／theme／author／author_zh／year／title／title_zh／
                           venue／type(article|chapter|monograph)／lang／note
                           檔名隨意，一組一檔比較好維護（top500-ot.jsonl…）

做三件事：
  1. Crossref 逐筆核對（query.bibliographic）：候選原樣快取在 output/top-papers/<field>-crossref.json
     （不進版控，刪了重跑就回來），挑選規則在 pick()——題名相似度 ≥ 0.82、年份差 ≤ 2、
     題名不是書評、專著只認 book 類型。🚨 第一版沒有後兩條，328 個「命中」裡混了一堆書評的 DOI
     （題名一模一樣、後面接 "By 作者"），看起來全對。專書與十九世紀以前的作品多半核不到，這是正常的。
  2. 比對電子圖書館有沒有（沿用 contemporary_theology_index 的 in_library，題名關鍵詞＋作者
     兩道閘，見那邊的說明——兩種相反的壞法都會看起來很正常）。
  3. 寫 public/content/research-data/<field>/top-papers.json（進版控），頁面
     pages/research-data/top-papers/[field].vue 直接讀。

用法：
  python -X utf8 scripts/top_papers_build.py biblical-studies
  python -X utf8 scripts/top_papers_build.py biblical-studies --no-crossref   # 只重組不打 API
  python -X utf8 scripts/top_papers_build.py biblical-studies --no-library    # 不連 DB

🚨 稽核一定要印分母：每組筆數、Crossref 命中數、館內命中數都印出來，
「0 筆」先懷疑迴圈沒跑到（feedback_silent_zero_is_a_bug）。
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from contemporary_theology_index import in_library, library_titles, load_env  # noqa: E402

CROSSREF = "https://api.crossref.org/works"
UA = "kglab-top-papers/1.0 (mailto:redpiigpig@gmail.com)"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9一-鿿 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    # 副標常被 Crossref 切掉，主標對上就算：拿較短的那一段去比
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    if short in long_ and len(short) >= 20:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


BOOK_TYPES = {"book", "monograph", "edited-book", "reference-book", "book-set", "book-series"}
# 🚨 這一行別用 Bash heredoc 改：heredoc 會把 \b 吃成退格字元（2026-09-26 踩過）。
REVIEW_RE = re.compile(r"\bbook review\b|\breviews?\b|\breviewed\b|\. by [A-Z]|\bby [A-Z][a-z]+ [A-Z][a-z]+\.?$", re.I)


def crossref_candidates(item: dict, session: requests.Session) -> list[dict]:
    """把 Crossref 回的候選原樣存下來（不在這裡挑），挑選規則改了不必重打 API。"""
    q = f'{item["title"]} {item.get("author", "")}'
    for attempt in range(4):
        try:
            r = session.get(CROSSREF, params={"query.bibliographic": q, "rows": 6,
                                              "select": "DOI,title,author,issued,container-title,volume,page,type"},
                            headers={"User-Agent": UA}, timeout=30)
        except requests.RequestException:
            time.sleep(3 * (attempt + 1))
            continue
        if r.status_code == 200:
            break
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(5 * (attempt + 1))
            continue
        return []
    else:
        return []
    out = []
    for w in r.json().get("message", {}).get("items", []):
        parts = (w.get("issued") or {}).get("date-parts") or [[None]]
        y = parts[0][0] if parts and parts[0] else None
        out.append({"doi": w.get("DOI"), "cr_title": " ".join(w.get("title") or []), "cr_year": y,
                    "container": " ".join(w.get("container-title") or []) or None,
                    "volume": w.get("volume"), "pages": w.get("page"), "cr_type": w.get("type"),
                    "cr_authors": [a.get("family", "") for a in (w.get("author") or [])]})
    return out


def pick(item: dict, cands: list[dict]) -> dict | None:
    """候選裡挑真正的那一筆。🚨 Crossref 對專書最常回的是**書評**（題名一模一樣、後面接 "By 作者"，
    型別是 journal-article、刊名是 JBL／CBQ），所以題名相似還不夠，還要：
    (1) 題名不含書評字樣  (2) 專著只認 book 類型  (3) 年份差 ≤ 2（書評通常晚一兩年，剛好被年份閘和型別閘雙重擋）。"""
    for c in cands:
        t = c["cr_title"]
        if not t or REVIEW_RE.search(t):
            continue
        sim = title_sim(item["title"], t)
        if sim < 0.82:
            continue
        y = c.get("cr_year")
        if y is not None and abs(int(y) - int(item["year"])) > 2:
            continue
        if item.get("type") == "monograph" and c.get("cr_type") not in BOOK_TYPES:
            continue
        if item.get("type") == "article" and c.get("cr_type") in BOOK_TYPES:
            continue
        return {**c, "sim": round(sim, 3)}
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("field")
    ap.add_argument("--no-crossref", action="store_true")
    ap.add_argument("--no-library", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="忽略 Crossref 快取全部重查")
    args = ap.parse_args()

    src = ROOT / "data" / "research-data" / args.field
    cfg = json.loads((src / "top-papers.config.json").read_text(encoding="utf-8"))
    files = sorted(src.glob("top*.jsonl"))
    items: list[dict] = []
    for f in files:
        rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"  {f.name}: {len(rows)} 筆")
        items += rows
    groups = {g["slug"]: g for g in cfg["groups"]}
    bad = [it for it in items if it.get("group") not in groups]
    if bad:
        print(f"  ! {len(bad)} 筆的 group 不在 config 裡：{sorted({b['group'] for b in bad})}")
        return 1
    print(f"合計 {len(items)} 筆，{len(groups)} 組")

    # ── 1. Crossref ──
    cache_dir = ROOT / "output" / "top-papers"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_f = cache_dir / f"{args.field}-crossref.json"
    cache = {} if args.refresh or not cache_f.exists() else json.loads(cache_f.read_text(encoding="utf-8"))
    # 舊格式（存的是挑好的一筆或 None）一律作廢，改存候選清單
    cache = {k: v for k, v in cache.items() if isinstance(v, list)}
    if not args.no_crossref:
        s = requests.Session()
        todo = [it for it in items if f'{it["title"]}|{it["year"]}' not in cache]
        print(f"Crossref：快取 {len(cache)}，待查 {len(todo)}")
        for i, it in enumerate(todo, 1):
            k = f'{it["title"]}|{it["year"]}'
            cache[k] = crossref_candidates(it, s)
            if i % 25 == 0:
                print(f"  …{i}/{len(todo)}")
                cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
            time.sleep(0.6)
        cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    hit = 0
    for it in items:
        m = pick(it, cache.get(f'{it["title"]}|{it["year"]}') or [])
        it["crossref"] = m
        hit += bool(m)
    print(f"Crossref 命中 {hit}/{len(items)}（分母＝全部；專書與古籍核不到是正常的）")

    # ── 2. 館藏 ──
    if not args.no_library:
        env = load_env()
        lib = library_titles(env)
        print(f"電子圖書館 {len(lib)} 筆題名")
        for it in items:
            it["in_library"] = in_library(it, lib)
    else:
        for it in items:
            it.setdefault("in_library", False)
    print(f"館內已有 {sum(it['in_library'] for it in items)}/{len(items)}")

    # ── 3. 組裝 ──
    out_groups = []
    for g in cfg["groups"]:
        gi = [it for it in items if it["group"] == g["slug"]]
        themes: dict[str, list] = {}
        for it in gi:  # 主題照檔案裡首次出現的順序（那就是研究史順序），組內照年份
            themes.setdefault(it.get("theme") or "其他", []).append(it)
        th = [{"name": n, "count": len(v), "items": sorted(v, key=lambda x: x["year"])} for n, v in themes.items()]
        out_groups.append({**g, "count": len(gi), "in_library": sum(x["in_library"] for x in gi),
                           "verified": sum(bool(x["crossref"]) for x in gi), "themes": th})
        print(f"  {g['name']}: {len(gi)} 筆／{len(th)} 主題／館內 {out_groups[-1]['in_library']}／核對 {out_groups[-1]['verified']}")

    langs: dict[str, int] = {}
    types: dict[str, int] = {}
    for it in items:
        langs[it.get("lang", "?")] = langs.get(it.get("lang", "?"), 0) + 1
        types[it.get("type", "?")] = types.get(it.get("type", "?"), 0) + 1
    out = {"field": cfg["field"], "title": cfg["title"], "icon": cfg.get("icon", "📚"), "color": cfg.get("color", "slate"),
           "desc": cfg["desc"], "method": cfg.get("method", ""), "related": cfg.get("related", []),
           "total": len(items), "verified": hit, "in_library": sum(it["in_library"] for it in items),
           "langs": dict(sorted(langs.items(), key=lambda kv: -kv[1])), "types": types,
           "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "groups": out_groups}
    dst = ROOT / "public" / "content" / "research-data" / args.field / "top-papers.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {dst.relative_to(ROOT)}  {len(items)} 筆")
    return 0


if __name__ == "__main__":
    sys.exit(main())
