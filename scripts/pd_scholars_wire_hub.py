#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 data/pd-scholars/*.jsonl 裡已上架的各卷接進 stores/collectedWorks.ts 的 hub。

做兩件事，順序不能反：
  1. **先比對既有條目**——書目上已經有這一部書就接上去（填 ebookId、改 status），
     不要另立一筆。
  2. 比不到才新增。

🚨 為什麼第 1 步不能省：泰勒《原始文化》與弗雷澤《金枝》在 hub 上都已經有一筆
**帶內容的中譯**（683／650 段），只是 source_text 是空的。不先比對就直接新增，
站上會出現兩個《原始文化》、兩個《金枝》，而讀者分不出哪個是哪個。
這兩本現在的正解是「把英文原文併進既有那一筆的來源欄」，不是並列——所以本腳本
把它們列進 SKIP，不接也不新增，留待合併。

🚨 ebookId 的 key **不加引號**（`ebookId: '...'`）——apply-ebooks-quality-collection.mjs
是照那個樣式 grep 的，加了引號那一卷會漏標 collection。

  python scripts/pd_scholars_wire_hub.py            # 預演
  python scripts/pd_scholars_wire_hub.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "stores" / "collectedWorks.ts"
DATA = ROOT / "data" / "pd-scholars"

# 作者繁中名 → hub slug
SLUG = {
    "詹姆斯‧喬治‧弗雷澤": "james-frazer",
    "珍‧艾倫‧哈里森": "jane-ellen-harrison",
    "威廉‧羅伯遜‧史密斯": "william-robertson-smith",
    "齊美爾": "georg-simmel",
    "納坦‧瑟德布盧姆": "nathan-soderblom",
    "恩斯特‧特洛爾奇": "ernst-troeltsch",
}

# 站上已有一筆帶內容的中譯、只缺來源欄的——**不接不新增**，留待把原文併進去。
SKIP = {
    "金枝（一卷節本）": "站上已有《金枝（英繁對照）》650 段（有中譯無原文）；"
                  "正解是把這份英文併進那一筆的來源欄，不是並列兩本。",
}


def norm(s: str) -> str:
    return re.sub(r"[\s《》（）()：:‧·、,，.。\-—]", "", (s or "")).lower()


def author_span(text: str, slug: str):
    i = text.find(f'"slug": "{slug}"')
    if i < 0:
        i = text.find(f"slug: '{slug}'")
    if i < 0:
        return None
    nxt = [x for x in (text.find('"slug":', i + 20), text.find("slug: '", i + 20)) if x > 0]
    return i, (min(nxt) if nxt else len(text))


def entries(text: str, a: int, b: int):
    """該作者 works[] 的每一個條目 (起, 迄, title, titleOriginal)。"""
    out = []
    for m in re.finditer(r'"title":\s*"((?:[^"\\]|\\.)*)"', text[a:b]):
        p = a + m.start()
        start = text.rfind("{", 0, p)
        depth, i = 0, start
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        blk = text[start:i + 1]
        to = re.search(r'"titleOriginal":\s*"((?:[^"\\]|\\.)*)"', blk)
        out.append((start, i + 1, m.group(1), to.group(1) if to else ""))
    return out


def render(d: dict, indent: int = 16) -> str:
    sp = " " * indent
    lines = ["{"]
    for k, v in d.items():
        key = k if k == "ebookId" else f'"{k}"'
        if isinstance(v, list):
            inner = ",\n".join(f'{sp}      "{x}"' for x in v)
            lines.append(f'{sp}      {key}: [\n{inner}\n{sp}      ],')
        elif isinstance(v, int):
            lines.append(f"{sp}      {key}: {v},")
        elif k == "ebookId":
            lines.append(f"{sp}      {key}: '{v}',")
        else:
            lines.append(f'{sp}      {key}: "{v}",')
    return "\n".join(lines).rstrip(",") + f"\n{sp}}}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    books = []
    for f in sorted(DATA.glob("*.jsonl")):
        books += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

    src = STORE.read_text(encoding="utf-8")
    linked = added = skipped = 0

    for b in books:
        if b["title"] in SKIP:
            print(f"  ⏭ 跳過 {b['title']}　{SKIP[b['title']]}")
            skipped += 1
            continue
        slug = SLUG.get(b["author"])
        if not slug:
            print(f"  ✗ 不認得作者 {b['author']}")
            continue
        sp = author_span(src, slug)
        if not sp:
            print(f"  ✗ 找不到 hub {slug}")
            continue
        if b["id"] in src:
            continue                                   # 已接過

        hit = None
        for start, end, title, to in entries(src, *sp):
            blk = src[start:end]
            if "ebookId" in blk:
                continue                               # 已有內容的條目不動
            if norm(title) == norm(b["title"]) or (to and norm(to) == norm(b["original_title"])):
                hit = (start, end, blk)
                break

        note = (b.get("subtitle") or "").strip()
        if hit:
            start, end, blk = hit
            new = re.sub(r'"status":\s*"[^"]*"', '"status": "in-progress"', blk, count=1)
            new = new.replace('"status": "in-progress"',
                              f'"status": "in-progress",\n                      ebookId: \'{b["id"]}\'', 1)
            src = src[:start] + new + src[end:]
            linked += 1
            print(f"  ✓ 接 {b['author'][:8]:10s} {b['title'][:30]}")
        else:
            es = entries(src, *sp)
            if not es:
                print(f"  ✗ {slug} 沒有 works 條目可插入")
                continue
            tail = es[-1][1]
            entry = {
                "title": b["title"],
                "titleOriginal": b["original_title"],
                "year": str(b["publication_year"]),
                "yearSort": b["publication_year"],
                "category": "原著",
                "languages": [],
                "status": "in-progress",
                "ebookId": b["id"],
            }
            if note:
                entry["note"] = note
            entry.pop("languages")
            src = src[:tail] + ",\n                " + render(entry) + src[tail:]
            added += 1
            print(f"  ＋ 新增 {b['author'][:8]:10s} {b['title'][:30]}")

    print(f"\n接上 {linked}　新增 {added}　跳過 {skipped}")
    if a.apply:
        STORE.write_text(src, encoding="utf-8")
        print("已寫回 store")
    else:
        print("（預演，加 --apply 才寫回）")


if __name__ == "__main__":
    main()
