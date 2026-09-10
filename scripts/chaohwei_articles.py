#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從站上既有的研究資料裡，把**昭慧法師的單篇文章**撈出來 → 全集 hub 的著作目錄。

昭慧法師的全集不只專書：期刊論文（玄奘佛學研究、法印學報）、雜誌文章（弘誓雙月刊）、
以及她投到別家刊物的專文（《新使者》、《台灣教會公報》）。這些**多半已經在站上**，
只是散在 `/research-data` 各 collection 裡，全集那邊看不到。本腳本做的是「盤點與連結」，
不重抓、不重存。

  python -X utf8 scripts/chaohwei_articles.py            # 盤點，印報告
  python -X utf8 scripts/chaohwei_articles.py --out c:/tmp/chaohwei_articles.json

來源與現況（各自的限制寫在 SOURCES 裡）：
  玄奘佛學研究 / 法印學報 …… 索引有篇目層（title+author），直接比對作者
  新使者               …… 索引有篇目層，作者欄含頭銜
  台灣教會公報          …… R2 上每年一個 jsonl.gz，要下載後全文搜
  弘誓雙月刊            …… 🚨 只有整期 PDF、**沒有篇目層**，本腳本撈不到，
                           要另外從目次頁抽（見 SKILL）
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CONTENT = ROOT / "public/content/research-data"

# 昭慧法師的各種署名寫法。**不要只查「釋昭慧」**——刊物署名不一致，
# 有「昭慧法師」「釋昭慧」「昭慧」，英文則是 Shih Chao-Hwei / Chao-Hwei Shih。
NAME_RE = re.compile(r"昭慧|Chao[- ]?Hwei", re.I)

# 署名樣式：報刊的投書把作者寫成「◎釋昭慧」「文／昭慧法師」
# 「（作者為玄奘大學宗教與文化學系教授釋昭慧）」。
# 🚨 分辨「她寫的」與「只是寫到她」全靠這個——教會公報 42 篇命中裡，
# 絕大多數是報導中提到她，不是她的投書。只看有沒有出現名字會全部收錯。
BYLINE_RE = re.compile(
    r"[◎◇☉]\s*(?:釋)?昭慧"
    r"|(?:文|作者|撰文|口述)\s*[／/:：]\s*(?:釋)?昭慧"
    r"|作者[為是][^。\n]{0,30}昭慧"
    r"|昭慧法師\s*[／/]\s*(?:文|撰)"
)

# (顯示名, 索引檔, collection 路由)
INDEX_SOURCES = [
    ("玄奘佛學研究", "yinshun-hongshi/xuanzang-index.json", "yinshun-hongshi"),
    ("法印學報", "yinshun-hongshi/faryin-index.json", "yinshun-hongshi"),
    ("妙心", "yinshun-hongshi/miaoxin-index.json", "yinshun-hongshi"),
    ("福嚴會訊", "yinshun-hongshi/fuyan-index.json", "yinshun-hongshi"),
    ("新使者", "pct/new-messenger-index.json", "pct"),
]


def scan_index(path: Path, journal: str) -> list[dict]:
    """吃一個「期 → articles[]」形狀的索引，回傳作者命中的篇目。純解析。"""
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    out = []
    for issue in data:
        for a in issue.get("articles") or []:
            author = str(a.get("author") or "")
            if not NAME_RE.search(author):
                continue
            out.append({
                "journal": journal,
                "issue": issue.get("issue"),
                "date": issue.get("date") or "",
                "title": (a.get("title") or "").strip(),
                "author": author.strip(),
                "has_fulltext": bool(a.get("hasFulltext") or a.get("textKey") or a.get("pdfKey")),
                "key": a.get("textKey") or a.get("pdfKey") or "",
                "note": a.get("note") or "",
            })
    return out


def scan_tcnn(limit_years: int | None = None) -> list[dict]:
    """台灣教會公報：R2 上每年一個 jsonl.gz，逐年下載後比對標題與內文署名。

    公報是新聞網站，昭慧法師多半以**投書／專文**出現，作者不一定進 metadata，
    所以標題與內文都要看；只在內文命中的另外標記，交人工判斷是不是她本人所寫。
    """
    try:
        import download_files as df  # noqa: F401  （R2 helper，與 pct_tcnn 同一支）
    except Exception:
        df = None
    idx_path = CONTENT / "pct/tcnn-index.json"
    if not idx_path.exists():
        return []
    years = json.loads(idx_path.read_text(encoding="utf-8"))
    if limit_years:
        years = years[:limit_years]

    import boto3
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    s3 = boto3.client("s3", region_name="auto", endpoint_url=env["R2_ENDPOINT"],
                      aws_access_key_id=env["R2_ACCESS_KEY"],
                      aws_secret_access_key=env["R2_SECRET_KEY"])
    out = []
    for y in years:
        key = y.get("textKey")
        if not key:
            continue
        try:
            body = s3.get_object(Bucket=env["R2_BUCKET"], Key=key)["Body"].read()
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ {key}: {e}", flush=True)
            continue
        raw = gzip.GzipFile(fileobj=io.BytesIO(body)).read().decode("utf-8", "replace")
        n = 0
        for line in raw.splitlines():
            if not line.strip():
                continue
            try:
                art = json.loads(line)
            except json.JSONDecodeError:
                continue
            title = art.get("title") or ""
            text = art.get("text") or ""
            in_title = bool(NAME_RE.search(title))
            m = NAME_RE.search(text)
            if not (in_title or m):
                continue
            n += 1
            # 是「她寫的」還是「寫到她」？公報的投書署名寫成「◎釋昭慧」，
            # 報導則是在內文裡提到她。只看有沒有出現名字分不出來，要看上下文。
            byline = bool(BYLINE_RE.search(text))
            ctx = ""
            if m:
                s = max(0, m.start() - 30)
                ctx = text[s:m.end() + 30].replace("\n", " ")
            out.append({
                "journal": "台灣教會公報",
                "issue": y.get("year"),
                "date": art.get("date") or "",
                "title": title.strip(),
                "author": "釋昭慧" if byline else "",
                "has_fulltext": True,
                "key": art.get("link") or "",
                "note": ("署名投書" if byline else
                         "標題命中" if in_title else "報導中提及（非本人所寫）"),
                "context": ctx,
            })
        print(f"  {y.get('year')}: {n} 篇命中", flush=True)
    return out


# 各刊在站上的落點（點篇名連過去看原件）
JOURNAL_ROUTE = {
    "弘誓雙月刊": "/research-data/yinshun-hongshi",
    "玄奘佛學研究": "/research-data/yinshun-hongshi",
    "法印學報": "/research-data/yinshun-hongshi",
    "妙心": "/research-data/yinshun-hongshi",
    "福嚴會訊": "/research-data/yinshun-hongshi",
    "新使者": "/research-data/pct",
    "台灣教會公報": "/research-data/pct",
}
# 刊物在 hub 上的呈現順序：她自家的刊物在前，投到別家的在後
JOURNAL_ORDER = ["弘誓雙月刊", "玄奘佛學研究", "法印學報", "妙心", "福嚴會訊",
                 "新使者", "台灣教會公報"]


def scan_hongshi_magazine(toc_path: Path) -> list[dict]:
    """《弘誓雙月刊》篇目（`hongshi_toc.py --all` 產出的 magazine-toc.json）。

    這一刊是她的主場（自己創辦的），但站上原本只有整期 PDF、沒有篇目層，
    所以在別處怎麼查都查不到。
    """
    if not toc_path.exists():
        return []
    sys.path.insert(0, str(ROOT / "scripts"))
    from hongshi_toc import matches_author
    out = []
    for issue in json.loads(toc_path.read_text(encoding="utf-8")):
        for e in issue.get("articles") or []:
            if not matches_author(e.get("author", ""), "昭慧"):
                continue
            out.append({
                "journal": "弘誓雙月刊",
                "issue": issue.get("issue"),
                "date": "",
                "title": e.get("title", ""),
                "author": e.get("author", ""),
                "has_fulltext": True,
                "key": f"p{e.get('page')}",
                "note": "",
            })
    return out


def group_for_publish(hits: list[dict]) -> list[dict]:
    """命中篇目 → hub 要的分組結構。只收「她寫的」，報導中提及的不算著作。純函式。"""
    keep = [h for h in hits if h.get("note") != "報導中提及（非本人所寫）"]
    by: dict[str, list[dict]] = {}
    for h in keep:
        by.setdefault(h["journal"], []).append(h)
    groups = []
    for j in JOURNAL_ORDER + [k for k in by if k not in JOURNAL_ORDER]:
        items = by.get(j)
        if not items:
            continue
        items.sort(key=lambda x: (-(int(x["issue"]) if str(x.get("issue", "")).isdigit() else 0),
                                  x.get("title", "")))
        groups.append({"journal": j, "route": JOURNAL_ROUTE.get(j, ""), "items": items})
    return groups


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", help="把命中的篇目寫成 JSON")
    ap.add_argument("--publish", action="store_true",
                    help="寫出 hub 用的 public/content/collected-works/chao-hwei-articles.json")
    ap.add_argument("--skip-tcnn", action="store_true", help="跳過教會公報（要下載 17 個年份檔）")
    ap.add_argument("--limit-years", type=int)
    a = ap.parse_args()

    hits: list[dict] = []
    mag = scan_hongshi_magazine(CONTENT / "yinshun-hongshi/magazine-toc.json")
    print(f"{'弘誓雙月刊':<12} {len(mag):>4} 篇"
          + ("" if mag else "　⚠ 還沒有 magazine-toc.json，先跑 hongshi_toc.py --all"))
    hits += mag
    for journal, rel, _coll in INDEX_SOURCES:
        got = scan_index(CONTENT / rel, journal)
        print(f"{journal:<12} {len(got):>4} 篇")
        hits += got
    if not a.skip_tcnn:
        print("台灣教會公報（逐年下載 R2）…")
        hits += scan_tcnn(a.limit_years)

    print(f"\n合計 {len(hits)} 篇；有全文 {sum(1 for h in hits if h['has_fulltext'])} 篇")
    for h in hits:
        flag = "✓" if h["has_fulltext"] else "✗"
        print(f"  {flag} {h['journal']} {h['issue']}　{h['title'][:40]}　{h['note']}")
    if a.out:
        Path(a.out).write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✅ {a.out}")
    if a.publish:
        groups = group_for_publish(hits)
        dest = ROOT / "public/content/collected-works/chao-hwei-articles.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        payload = {"slug": "chao-hwei", "name": "昭慧法師",
                   "total": sum(len(g["items"]) for g in groups), "groups": groups}
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"✅ {dest}（{payload['total']} 篇，{len(groups)} 種刊物）")


if __name__ == "__main__":
    main()
