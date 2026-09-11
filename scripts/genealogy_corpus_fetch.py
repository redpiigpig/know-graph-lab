#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替《基督宗教譜系學》第6章抓一批**開放取用的一手文獻語料**。

第6章（近現代的重組）的材料缺口是全書最大的：電子圖書館裡關於二十世紀普世運動
**一本都沒有**（用英文詞查過，不是查詢語言的問題），而 Rouse & Neill 那三卷
《普世運動史》在 archive.org 上是借閱制、抓不到。

但真正的一手文獻反而是開放的：**世界教會協會信仰與教制委員會的文件系列
（WCC Faith and Order Papers）有 249 份在 archive.org 上無取用限制**，含《洗禮、
聖餐與職事》（利瑪文件，1982）與《教會：邁向共同的異象》（2013）這兩份核心文件。
這一批合起來就是普世運動神學工作的完整文獻紀錄。

本腳本只抓 `_djvu.txt` 純文字（不抓 PDF）：語料是拿來檢索與引用的，不是拿來閱讀
排版的；純文字小、快、可直接餵給 `genealogy_research.py`。

⚠️ 這批**不進電子圖書館**（不建 ebooks 列、不進 parse 佇列）。它是本書專用的研究
語料，249 筆會把圖書館與解析佇列灌爆，而且多數是會議紀錄與研究報告，不是「書」。

存放：`G:/我的雲端硬碟/資料/知識圖工作室/_corpus/ecumenical/`
索引：同目錄的 `index.json`（identifier、題名、年份、檔名、字數）

用法：
  python scripts/genealogy_corpus_fetch.py --list        # 只列出清單
  python scripts/genealogy_corpus_fetch.py --limit 20    # 先抓 20 筆試
  python scripts/genealogy_corpus_fetch.py               # 全抓（可重跑，會跳過已有的）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CORPUS_ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus")
UA = {"User-Agent": "Mozilla/5.0 (kglab-ingest)"}
SEARCH = ("https://archive.org/advancedsearch.php?q={q}"
          "&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=year&rows=1000&output=json")
META = "https://archive.org/metadata/{ident}"
DL = "https://archive.org/download/{ident}/{name}"

# 語料組：短名 → (archive.org 查詢式, 說明)
COLLECTIONS = {
    # WCC 自己的數位檔案：archive.org 上 wcc* 開頭的文本共約 1,465 筆，含
    # wccfops（信仰與教制）、wcclifework（生活與工作）、wccmissionconf（世界宣教大會）、
    # wccjwgrccwcc（羅馬天主教—WCC 聯合工作小組）、wcccciareports（國際事務委員會）等十餘系列。
    "wcc": ("identifier:wcc* AND mediatype:texts",
            "世界教會協會數位檔案（信仰與教制／生活與工作／宣教大會／天主教聯合工作小組…）"),
    "wccfops": ("identifier:wccfops2.*",
                "只取信仰與教制文件系列（Faith and Order Papers）"),
    # 愛丁堡 1910 及其後續：1910-1920 年代出版，公有領域。
    "edinburgh": ('("World Missionary Conference" OR "Continuation Committee") '
                  'AND mediatype:texts AND date:[1900-01-01 TO 1930-12-31]',
                  "世界宣教大會（愛丁堡 1910 及其延續委員會，公有領域）"),
}


def fetch_json(url: str, timeout: int = 90) -> dict:
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=timeout).read())


def listing(query: str) -> list[dict]:
    """分頁取回全部命中。

    ⚠️ advancedsearch 單次 rows 上限 1000，超過就靜默截斷——wcc* 有 1,465 筆，
    不分頁會少拿四百多筆而且完全看不出來。
    """
    out, page = [], 1
    while True:
        d = fetch_json(SEARCH.format(q=urllib.parse.quote(query)) + f"&page={page}")
        docs = d["response"]["docs"]
        out.extend(docs)
        if len(out) >= d["response"]["numFound"] or not docs:
            break
        page += 1
    return out


def safe_name(ident: str, title: str) -> str:
    t = re.sub(r"[\\/:*?\"<>|]", "_", (title or "").strip())[:90]
    return f"{ident}__{t}.txt" if t else f"{ident}.txt"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="wcc", choices=list(COLLECTIONS))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    query, desc = COLLECTIONS[args.set]
    docs = listing(query)
    print(f"{desc}：{len(docs)} 筆")
    if args.limit:
        docs = docs[: args.limit]
    if args.list:
        for r in docs:
            print(f"  {r['identifier']:18s} {str(r.get('title',''))[:78]}")
        return 0

    OUT = CORPUS_ROOT / ("ecumenical" if args.set.startswith("wcc") else args.set)
    OUT.mkdir(parents=True, exist_ok=True)
    idx_path = OUT / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}

    got = skipped = failed = backfilled = 0
    for i, r in enumerate(docs, 1):
        ident = r["identifier"]
        title = str(r.get("title", ""))
        target = OUT / safe_name(ident, title)
        if target.exists() and target.stat().st_size > 2000:
            # ⚠️ 略過的同時要補索引。index.json 只在跑完時寫一次，中途被砍（休眠、
            # 關機、session 結束）已抓的那些就沒進索引；而略過看的是「檔案在不在」，
            # 所以重跑會直接跳過，那批檔案永遠補不回索引——硬碟有、索引沒有、
            # 網站少算，而每一步看起來都正常。
            if ident not in index:
                index[ident] = {"title": title, "year": r.get("year"),
                                "file": target.name,
                                "chars": len(target.read_text("utf-8", "replace"))}
                backfilled += 1
            skipped += 1
            continue
        try:
            m = fetch_json(META.format(ident=ident), timeout=45)
        except Exception as e:
            print(f"[{i}/{len(docs)}] {ident} 中繼失敗 {type(e).__name__}")
            failed += 1
            continue
        if (m.get("metadata") or {}).get("access-restricted-item") == "true":
            print(f"[{i}/{len(docs)}] {ident} 借閱制，跳過")
            failed += 1
            continue
        txts = [f["name"] for f in (m.get("files") or []) if f.get("name", "").endswith("_djvu.txt")]
        if not txts:
            print(f"[{i}/{len(docs)}] {ident} 沒有純文字檔")
            failed += 1
            continue
        try:
            data = urllib.request.urlopen(urllib.request.Request(
                DL.format(ident=ident, name=urllib.parse.quote(txts[0])), headers=UA), timeout=180).read()
        except Exception as e:
            print(f"[{i}/{len(docs)}] {ident} 下載失敗 {type(e).__name__}")
            failed += 1
            continue
        target.write_bytes(data)
        text = data.decode("utf-8", "replace")
        index[ident] = {"title": title, "year": r.get("year"),
                        "file": target.name, "chars": len(text)}
        got += 1
        print(f"[{i}/{len(docs)}] {ident}  {len(text)/1000:.0f}k 字  {title[:52]}")
        if got % 25 == 0:  # 中途落盤，別把一千多筆的索引押在跑完那一刻
            idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(0.7)

    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(v["chars"] for v in index.values())
    print(f"\n抓取 {got}／略過 {skipped}（其中補進索引 {backfilled}）／失敗 {failed}")
    print(f"語料現況：{len(index)} 份、{total:,} 字 → {OUT}")
    print("接著用 `python scripts/genealogy_research.py --set ecumenical <關鍵詞>` 檢索。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
