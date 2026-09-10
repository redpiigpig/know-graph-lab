#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓洛桑運動（Lausanne Movement）的文獻語料。

第6章第六節「運動那一條線」要處理福音派這一支，而福音派在二十世紀的組織核心是
洛桑運動——它與世界教會協會（WCC）構成近現代基督宗教的兩條主線。

⚠️ 這一批不在 archive.org：那裡關於洛桑的東西極少且多為借閱制。正確的來源是洛桑
運動自己的網站，它把全部文件免費公開：

  * 四份基礎文件：洛桑信約（1974）、馬尼拉宣言（1989）、開普敦承諾（2010）、
    首爾宣言（2024）
  * 洛桑專題論文（Lausanne Occasional Papers, LOP）第 6 至 80 號

存放：`G:/我的雲端硬碟/資料/知識圖工作室/_corpus/lausanne/`
索引：同目錄的 `index.json`

用法：
  python scripts/genealogy_lausanne_fetch.py --list   # 只列出找到哪些
  python scripts/genealogy_lausanne_fetch.py          # 抓（可重跑，跳過已有的）
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/lausanne")
UA = {"User-Agent": "Mozilla/5.0 (kglab-ingest)"}
BASE = "https://lausanne.org"
INDEX_PAGES = [f"{BASE}/occasional-papers", f"{BASE}/occasional-papers/page/2"]

# 四份基礎文件的固定路徑
FOUNDATIONAL = [
    ("lausanne-covenant", "/statement/lausanne-covenant", "洛桑信約（1974）"),
    ("manila-manifesto", "/statement/manila-manifesto", "馬尼拉宣言（1989）"),
    ("cape-town-commitment", "/statement/ctcommitment", "開普敦承諾（2010）"),
    ("seoul-statement", "/statement/the-seoul-statement", "首爾宣言（2024）"),  # 路徑有 the-
]

TAG = re.compile(r"<[^>]+>")
SCRIPT = re.compile(r"<(script|style|nav|header|footer)\b[^>]*>.*?</\1>", re.S | re.I)


def get(url: str, timeout: int = 60) -> str:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=timeout
    ).read().decode("utf-8", "replace")


def to_text(page: str) -> str:
    """粗略去標籤。語料是拿來檢索的，不求版面。"""
    page = SCRIPT.sub(" ", page)
    page = re.sub(r"<br\s*/?>|</p>|</h[1-6]>|</li>", "\n", page, flags=re.I)
    txt = html.unescape(TAG.sub(" ", page))
    txt = re.sub(r"[ \t\u00a0]+", " ", txt)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def discover() -> list[tuple[str, str, str]]:
    """(slug, 路徑, 題名)；含基礎文件與所有 LOP。"""
    found: dict[str, tuple[str, str, str]] = {}
    for slug, path, title in FOUNDATIONAL:
        found[slug] = (slug, path, title)
    seen_pages = 0
    for idx in INDEX_PAGES:
        try:
            page = get(idx)
            seen_pages += 1
        except Exception as e:
            print(f"  目次頁取不到 {idx}：{type(e).__name__}", file=sys.stderr)
            continue
        # 站上連結是絕對網址，而且有 /zh-hant/ /ko/ 等語言前綴的重複連結，只取英文版
        for m in re.finditer(
                r'href="https://lausanne\.org/occasional-paper/([a-z0-9\-]+)"[^>]*>(.*?)</a>',
                page, re.S):
            slug, raw = m.group(1), to_text(m.group(2))[:120]
            found.setdefault(slug, (slug, f"/occasional-paper/{slug}", raw or slug))
    if not seen_pages:
        print("  ⚠️ 兩個目次頁都取不到，只會抓四份基礎文件", file=sys.stderr)
    return list(found.values())


def strip_boilerplate(out_dir: Path, index: dict) -> None:
    """剝掉網站的導覽列與頁尾。

    lausanne.org 每一頁開頭都有同一段導覽（裡面就寫著「洛桑信約、馬尼拉宣言、
    開普敦承諾與首爾宣言」），頁尾也一樣。不剝的話，查任何一份核心文件的名字都會
    命中全部一百多篇——**看起來檢索正常，其實全是假命中**。

    作法是逐行統計：出現在六成以上檔案裡的短行判為樣板。這比猜開頭結尾的標記穩，
    網站改版也不會失效。
    """
    from collections import Counter
    files = sorted(out_dir.glob("*.txt"))
    if len(files) < 5:
        return
    texts = {f: f.read_text(encoding="utf-8", errors="replace") for f in files}
    freq: Counter = Counter()
    for t in texts.values():
        for ln in {l.strip() for l in t.splitlines() if l.strip()}:
            freq[ln] += 1
    n = len(files)
    boiler = {ln for ln, c in freq.items() if c >= n * 0.6 and len(ln) < 200}
    if not boiler:
        return
    for f, t in texts.items():
        kept = [l for l in t.splitlines() if l.strip() and l.strip() not in boiler]
        nl = chr(10)
        cleaned = re.sub(nl + "{3,}", nl * 2, nl.join(kept)).strip() + nl
        if cleaned != t:
            f.write_text(cleaned, encoding="utf-8")
    for v in index.values():
        fp = out_dir / v["file"]
        if fp.exists():
            v["chars"] = len(fp.read_text(encoding="utf-8", errors="replace"))
    print(f"  剝除樣板 {len(boiler)} 種重複行")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    items = discover()
    print(f"洛桑運動文獻：找到 {len(items)} 篇"
          f"（含 {len(FOUNDATIONAL)} 份基礎文件）")
    if args.limit:
        items = items[: args.limit]
    if args.list:
        for slug, path, title in items:
            print(f"  {slug[:40]:40s} {title[:56]}")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    idx_path = OUT / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}

    got = skipped = failed = 0
    for i, (slug, path, title) in enumerate(items, 1):
        target = OUT / f"{slug}.txt"
        if target.exists() and target.stat().st_size > 1500:
            skipped += 1
            continue
        try:
            txt = to_text(get(BASE + path))
        except Exception as e:
            print(f"[{i}/{len(items)}] {slug} 失敗 {type(e).__name__}")
            failed += 1
            continue
        if len(txt) < 1500:
            print(f"[{i}/{len(items)}] {slug} 內容過短（{len(txt)} 字），可能是導頁")
            failed += 1
            continue
        target.write_text(txt, encoding="utf-8")
        index[slug] = {"title": title, "path": path, "file": target.name, "chars": len(txt)}
        got += 1
        print(f"[{i}/{len(items)}] {slug[:38]:38s} {len(txt)/1000:5.0f}k 字")
        time.sleep(1.0)

    strip_boilerplate(OUT, index)
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(v["chars"] for v in index.values())
    print(f"\n抓取 {got}／略過 {skipped}／失敗 {failed}")
    print(f"語料現況：{len(index)} 篇、{total:,} 字 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
