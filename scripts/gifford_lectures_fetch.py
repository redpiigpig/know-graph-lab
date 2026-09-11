#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓吉福德講座（Gifford Lectures）歷屆講者與講題，供 /research-data/contemporary-theology 用。

吉福德講座是自然神學領域最重要的系列講座，一八八八年起在蘇格蘭四所大學
（亞伯丁、愛丁堡、格拉斯哥、聖安德魯斯）輪流舉辦，多數講稿後來成書。
**把歷屆名單當成一份書目來讀，等於得到一條橫跨一百四十年的當代神學與宗教哲學主軸**
——詹姆斯《宗教經驗之種種》、巴特《教義學綱要》、田立克、尼布爾、泰勒《世俗時代》
都出自這裡。

⚠️ **官網 giffordlectures.org 有 Cloudflare，curl 一律 403。**改抓維基百科英文版
〈Gifford Lectures〉條目的 wikitext：那裡四所大學各一張 wikitable，欄位是
年份／講者／講題／ISBN，結構比官網乾淨，而且維基的 API 不擋。

輸出 `public/content/research-data/contemporary-theology/gifford.json`（進版控，
頁面直接讀它）。這是策展資料不是大檔，不放 Drive。

用法：
  python scripts/gifford_lectures_fetch.py          # 抓並寫檔
  python scripts/gifford_lectures_fetch.py --list   # 只印出來看
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "content" / "research-data" / "contemporary-theology" / "gifford.json"
API = ("https://en.wikipedia.org/w/api.php?action=parse&page=Gifford_Lectures"
       "&prop=wikitext&format=json&formatversion=2")
UA = {"User-Agent": "kglab-research/1.0 (academic bibliography compilation)"}

UNIVERSITIES = ["Aberdeen", "Edinburgh", "Glasgow", "St Andrews"]
ZH = {"Aberdeen": "亞伯丁", "Edinburgh": "愛丁堡",
      "Glasgow": "格拉斯哥", "St Andrews": "聖安德魯斯"}

REF = re.compile(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", re.S | re.I)
TPL = re.compile(r"\{\{[^{}]*\}\}")
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
EXTLINK = re.compile(r"\[(https?://\S+?) ([^\]]+)\]")
BARE_URL = re.compile(r"\[(https?://\S+?)\]")
HTMLTAG = re.compile(r"<[^>]+>")


# 屬性值可能加引號也可能不加（rowspan="2"| 與 rowspan=2| 兩種寫法混用）
_ATTR = r'[a-zA-Z-]+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s|]+)'
CELL_ATTR = re.compile(r"^\s*" + _ATTR + r"(?:\s+" + _ATTR + r")*\s*\|(?!\|)")
BR = re.compile(r"<br\s*/?>", re.I)


def clean(cell: str) -> str:
    """把一格 wikitext 變成純文字。順序要緊：先拆模板與 ref，再拆連結。"""
    s = REF.sub("", cell)
    for _ in range(3):                       # 模板會巢狀
        s = TPL.sub("", s)
    # ⚠️ 欄位屬性要先剝：`rowspan="2"|2022` 不剝就會把 rowspan 當成年份的一部分，
    # 而它長得很像資料，掃過去完全看不出錯。
    s = CELL_ATTR.sub("", s)
    # ⚠️ 同一格可能有兩位講者，靠 <br> 或換行分隔；不先換成分隔號，
    # 去標籤之後會黏成「Manthia DiawaraTerri Geis」這種不存在的人名。
    s = BR.sub(" ／ ", s)
    s = EXTLINK.sub(lambda m: m.group(2), s)  # [url 顯示字] → 顯示字
    s = BARE_URL.sub("", s)
    s = WIKILINK.sub(lambda m: m.group(2) or m.group(1), s)
    s = s.replace("'''", "").replace("''", "")
    s = HTMLTAG.sub("", s)
    s = s.replace("&nbsp;", " ").replace("&ndash;", "–").replace("&amp;", "&")
    s = re.sub(r"\n+", " ／ ", s)
    s = re.sub(r"(\s*／\s*)+", " ／ ", s)
    return re.sub(r"[ \t]+", " ", s).strip(" \t|／ ")


def link_of(cell: str) -> str | None:
    """取這一格裡第一個外部連結（多半是 archive.org 全文或官網講者頁）。"""
    m = EXTLINK.search(REF.sub("", cell))
    return m.group(1) if m else None


def parse_section(wikitext: str, uni: str) -> list[dict]:
    """抓某一所大學那一節的表格。"""
    m = re.search(r"==+ *" + re.escape(uni) + r" *==+", wikitext)
    if not m:
        print(f"  ⚠️ 找不到 {uni} 這一節", file=sys.stderr)
        return []
    rest = wikitext[m.end():]
    end = re.search(r"\n==+ *[^=]+ *==+", rest)
    block = rest[: end.start()] if end else rest
    tbl = re.search(r"\{\|.*?\n\|\}", block, re.S)
    if not tbl:
        print(f"  ⚠️ {uni} 那一節裡沒有表格", file=sys.stderr)
        return []

    rows = []
    for raw in tbl.group(0).split("\n|-")[1:]:
        # 一列的各格：以行首 | 分隔；跳過 ! 開頭的表頭
        cells = [c for c in re.split(r"\n\|", raw) if not c.lstrip().startswith("!")]
        cells = [c for c in cells if c.strip()]
        if len(cells) < 2:
            continue
        year, speaker = clean(cells[0]), clean(cells[1])
        lecture = clean(cells[2]) if len(cells) > 2 else ""
        isbn = clean(cells[3]) if len(cells) > 3 else ""
        if not year or not speaker:
            continue
        if not re.search(r"\d{4}", year):     # 表頭殘骸
            continue
        rows.append({
            "university": uni, "university_zh": ZH[uni],
            "year": year, "speaker": speaker, "lecture": lecture,
            "isbn": isbn or None,
            "url": link_of(cells[2]) if len(cells) > 2 else None,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    req = urllib.request.Request(API, headers=UA)
    data = json.loads(urllib.request.urlopen(req, timeout=90).read())
    wikitext = data["parse"]["wikitext"]

    rows: list[dict] = []
    for uni in UNIVERSITIES:
        got = parse_section(wikitext, uni)
        print(f"  {ZH[uni]:6s} {len(got):>3} 場")
        rows.extend(got)

    def first_year(r: dict) -> int:
        m = re.search(r"\d{4}", r["year"])
        return int(m.group(0)) if m else 9999

    rows.sort(key=lambda r: (first_year(r), r["university"]))
    with_book = sum(1 for r in rows if r["lecture"])
    print(f"\n合計 {len(rows)} 場、{len({r['speaker'] for r in rows})} 位講者，"
          f"其中 {with_book} 場記有講題")

    if args.list:
        for r in rows[:40]:
            print(f"  {r['year']:12s} {r['university_zh']:6s} {r['speaker'][:26]:28s} {r['lecture'][:44]}")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "Wikipedia, “Gifford Lectures”（官網 giffordlectures.org 有 Cloudflare，抓不到）",
        "count": len(rows),
        "speakers": len({r["speaker"] for r in rows}),
        "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
