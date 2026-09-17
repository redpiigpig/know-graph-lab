# -*- coding: utf-8 -*-
"""圖書館與全集各有多少本「引用不出原書頁碼」。

延伸 `audit_page_numbers.py`：那一支只看 JSONL 本身，分不出兩件事——

🚨 **serial 不等於假頁碼。** epub 沒有實體頁，`page_number = index + 1` 是憑空捏的；
   PDF 走一頁一 chunk，`page_number` 就是實體頁，同樣長成 1,2,3… 卻是真的。
   不分這兩者，帳會從 51 本暴增成 1,146 本（[[feedback_transcribe_page_numbers]]）。
🚨 **要分書架。** 圖書館（collection 為空）與全集（collected-works）兩條線的
   頁碼來源不同，混在一起看不出是哪一條線在漏。

判定（每本歸一格）：
  有真頁碼   real／sparse／(serial 且 pdf)
  假頁碼     serial 且 epub 等無實體頁的來源  ← 比沒有更糟，會讓人照著引
  沒有頁碼   none（全部 None）
  沒有全文   DB 說 parsed 了，Drive 卻找不到 JSONL

    python -X utf8 scripts/audit_page_numbers_by_shelf.py
    python -X utf8 scripts/audit_page_numbers_by_shelf.py --out c:/tmp/page_shelf.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_page_numbers import CHUNKS, scan_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 有實體頁的來源：serial 在這些格式上是真頁碼
PAGED_TYPES = {"pdf"}


def fetch_books():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    out, off = [], 0
    while True:
        r = requests.get(
            f"{url}/rest/v1/ebooks?select=id,title,author,file_type,collection,"
            f"category,parsed_at,total_chars&order=id&limit=1000&offset={off}",
            headers=h, timeout=60)
        r.raise_for_status()
        page = r.json()
        out += page
        if len(page) < 1000:
            break
        off += 1000
    return out


def verdict(kind: str, file_type: str | None) -> str:
    if kind == "none":
        return "沒有頁碼"
    if kind == "serial":
        return "有真頁碼" if (file_type or "").lower() in PAGED_TYPES else "假頁碼"
    if kind in ("real", "sparse"):
        return "有真頁碼"
    return "沒有全文"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()

    books = fetch_books()
    parsed = [b for b in books if b.get("parsed_at")]
    print(f"全庫 {len(books):,} 本，其中已解析 {len(parsed):,} 本（分母）\n")

    tally = defaultdict(Counter)
    detail = {}
    missing_jsonl = defaultdict(list)
    for i, b in enumerate(parsed, 1):
        shelf = "全集" if b.get("collection") == "collected-works" else "圖書館"
        p = CHUNKS / f"{b['id']}.jsonl"
        if not p.exists():
            v, kind = "沒有全文", "missing"
            missing_jsonl[shelf].append(b)
        else:
            try:
                kind, _ = scan_file(p)
            except Exception as e:
                kind = f"error:{type(e).__name__}"
            v = verdict(kind, b.get("file_type"))
        tally[shelf][v] += 1
        detail[b["id"]] = {"shelf": shelf, "kind": kind, "verdict": v,
                           "file_type": b.get("file_type"), "title": b.get("title")}
        if i % 500 == 0:
            print(f"  掃描中 {i}/{len(parsed)}", flush=True)

    print()
    order = ["有真頁碼", "假頁碼", "沒有頁碼", "沒有全文"]
    width = max(len(k) for k in order) + 2
    for shelf in ("圖書館", "全集"):
        t = tally[shelf]
        total = sum(t.values())
        print(f"=== {shelf}（已解析 {total:,} 本）===")
        for k in order:
            n = t.get(k, 0)
            pct = n / total * 100 if total else 0
            print(f"  {k:<{width}} {n:>5,}  {pct:5.1f}%")
        other = {k: v for k, v in t.items() if k not in order}
        if other:
            print(f"  其他 {other}")
        bad = sum(t.get(k, 0) for k in ("假頁碼", "沒有頁碼", "沒有全文"))
        print(f"  → 引用不出原書頁碼：{bad:,} 本（{bad / total * 100 if total else 0:.1f}%）\n")

    if args.out:
        Path(args.out).write_text(json.dumps(detail, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
        print("明細已寫", args.out)


if __name__ == "__main__":
    main()
