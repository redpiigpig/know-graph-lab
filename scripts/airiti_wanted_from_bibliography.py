#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把論文與寫作計畫裡的**期刊論文**書目對到華藝，列出該去下載哪些篇。

跟 zlib_wanted_from_bibliography.py 是同一批書目的兩半：那支收「書」，這支收
「期刊論文」。z-library 是書庫沒有期刊，華藝反而整份收著並帶卷期頁碼——論文
註腳要寫「〈某篇〉，《校園》68 卷 2 期（2026 年 4 月），頁 12–17」，缺一個
都寫不成。

🚨 只產清單，不下載。華藝的下載額度綁的是**機構 IP**（本機被認成玄奘大學），
   跑快了是拿全校訂閱在衝，而華藝對異常流量的處置是停整個機構。真要抓請走
   `press_airiti.py --download <slug>`，它有 DELAY_DL=6.0 與 DL_CAP=300 的節流。

  python scripts/airiti_wanted_from_bibliography.py            # 列出清單
  python scripts/airiti_wanted_from_bibliography.py --json OUT # 另存 JSON
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

import zlib_wanted_from_bibliography as B
from ingest_new_books import URL, SB_HEADERS

AIRITI_JSON = ROOT / "public" / "content" / "research-data" / "press" / "airiti-journals.json"


def load_airiti() -> list[dict]:
    d = json.loads(AIRITI_JSON.read_text(encoding="utf-8"))
    return d.get("items", [])


def wired_slugs() -> dict[str, str]:
    """press_airiti.py 的 JOURNALS：pid → slug。已接的刊可以直接 --toc/--download。"""
    src = (ROOT / "scripts" / "press_airiti.py").read_text(encoding="utf-8")
    body = src.split("JOURNALS = {", 1)[1].split("\n}", 1)[0]
    out = {}
    for m in re.finditer(r'"([a-z0-9-]+)":\s*\("([^"]+)",\s*"([^"]+)"\)', body):
        out[m.group(2)] = m.group(1)
    return out


def norm_journal(s: str) -> str:
    """刊名比對鍵。華藝的 name 常是「English / 中文」合併，取中文那半；
    再去掉標點與《》，並拿掉常見的「（舊刊名）」註記。"""
    s = unicodedata.normalize("NFKC", s or "")
    parts = [p.strip() for p in s.split("/")]
    cjk = [p for p in parts if re.search(r"[一-鿿]", p)]
    s = cjk[-1] if cjk else (parts[0] if parts else "")
    s = re.sub(r"[（(].*?[)）]", "", s)
    return re.sub(r"[\s　《》〈〉「」:：,，.。\-–—]", "", s)


_ARTICLE_CITE = re.compile(
    r"〈(?P<title>[^〉]{2,120})〉[^《]*《(?P<venue>[^》]{2,60})》"
    r"[^,，。]*?(?P<vol>(?:第?\d+[卷期年]\s*)+(?:第?\d+期)?)?", re.S)


def articles_from_lit_review() -> list[dict]:
    rows, off = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/lit_review_entries"
                         f"?select=project_slug,title,authors,year,venue"
                         f"&offset={off}&limit=1000", headers=SB_HEADERS, timeout=90)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    out = []
    for x in rows:
        # looks_like_book 為真的是專書，交給 z-library 那一支
        if B.looks_like_book(x.get("title"), x.get("venue")):
            continue
        venue = (x.get("venue") or "").strip()
        if not venue:
            continue
        out.append({"title": (x.get("title") or "").strip(),
                    "author": B.first_author(x.get("authors")),
                    "venue": venue, "year": str(x.get("year") or ""),
                    "source": x["project_slug"]})
    return out


def articles_from_citations() -> list[dict]:
    """博論徵引與碩／學士論文書目：自由文本，靠〈篇名〉，《刊名》的體例挖。"""
    out = []
    tr = ROOT / "data" / "doctoral_thesis_references.json"
    if tr.exists():
        for x in json.loads(tr.read_text(encoding="utf-8")).get("references", []):
            for m in _ARTICLE_CITE.finditer(x.get("citation") or ""):
                out.append({"title": m.group("title").strip(),
                            "author": B.clean_author(x.get("citation", "")),
                            "venue": m.group("venue").strip(),
                            "year": "", "source": "hcu-phd"})
    db = ROOT / "public" / "content" / "works" / "degree-bibliographies.json"
    if db.exists():
        d = json.loads(db.read_text(encoding="utf-8"))
        for g in d.get("groups", []):
            for it in g.get("items", []):
                for m in _ARTICLE_CITE.finditer(it.get("text") or ""):
                    out.append({"title": m.group("title").strip(),
                                "author": B.clean_author(it.get("text", "")),
                                "venue": m.group("venue").strip(),
                                "year": "", "source": g.get("key") or "degree"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="另存一份 JSON")
    a = ap.parse_args()

    arts = articles_from_lit_review() + articles_from_citations()
    print(f"書目裡的期刊論文 {len(arts)} 筆", flush=True)

    airiti = load_airiti()
    wired = wired_slugs()
    idx = {}
    for j in airiti:
        idx.setdefault(norm_journal(j["name"]), j)

    hit, miss = collections.defaultdict(list), collections.Counter()
    seen = set()
    for x in arts:
        k = (norm_journal(x["venue"]), x["title"])
        if k in seen:
            continue
        seen.add(k)
        j = idx.get(norm_journal(x["venue"]))
        if j:
            hit[j["name"]].append({**x, "pid": j["pid"],
                                   "slug": wired.get(j["pid"]),
                                   "status": j.get("status")})
        else:
            miss[x["venue"]] += 1

    total = sum(len(v) for v in hit.values())
    print(f"\n對上華藝的 {total} 篇，分佈在 {len(hit)} 種刊：\n")
    print(f"{'刊名':34} {'篇數':>4}  {'已接腳本':10} 狀態")
    for name, items in sorted(hit.items(), key=lambda kv: -len(kv[1])):
        slug = items[0]["slug"]
        print(f"  {norm_journal(name)[:30]:32} {len(items):>4}  "
              f"{(slug or '✗ 待加入 JOURNALS'):20} {items[0].get('status') or ''}")

    print(f"\n華藝沒有（或刊名對不上）的 {sum(miss.values())} 篇，前 15 種刊：")
    for k, n in miss.most_common(15):
        print(f"  {n:>3}  {k[:56]}")

    if a.json:
        Path(a.json).write_text(json.dumps(
            {"matched": hit, "unmatched": dict(miss)}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
