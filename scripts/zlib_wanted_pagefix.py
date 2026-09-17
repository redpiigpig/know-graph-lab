# -*- coding: utf-8 -*-
"""把「館藏已有、但引用不出原書頁碼」的書排成 z-lib 獵表，去找 PDF 版。

由來：2026-09-18 稽核（`audit_page_numbers_by_shelf.py`）量出圖書館 1,414 本、
全集 156 本的 `page_number` 是 null。原因幾乎都是來源格式沒有實體頁——
epub 940／docx 499／txt 129。政策上留 null 是對的，但**論文引用寫不出第幾頁**。
補救辦法是去 z-lib 找同一本書的 PDF 版，抓回來重跑，PDF 一頁一 chunk 就有真頁碼。

🚨 這批**不能混進 `zlib_wanted_all.jsonl`**。`zlib_retire_owned.py` 會比對 ebooks
   把「館藏已經有的」註銷掉，而這批正是館藏已經有的——一進去就被整批註銷，
   而且帳本上看起來「已處理」，沒有人會發現。所以另存一份，並在註銷腳本裡
   放行 `source == "pagefix"`。

    python -X utf8 scripts/zlib_wanted_pagefix.py            # 只看統計
    python -X utf8 scripts/zlib_wanted_pagefix.py --write    # 寫獵表
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_page_numbers import CHUNKS, scan_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path("output/zlib_wanted_pagefix.jsonl")
# 這些格式沒有實體頁，是可以靠換 PDF 版補救的對象
UPGRADABLE = {"epub", "docx", "doc", "txt", "mobi", "azw3", "chm"}
MIN_TITLE = 4          # 書名太短查不準，寧可不排


def fetch_books():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    out, off = [], 0
    while True:
        r = requests.get(
            f"{url}/rest/v1/ebooks?select=id,title,author,file_type,collection,"
            f"category,parsed_at&order=id&limit=1000&offset={off}", headers=h, timeout=60)
        r.raise_for_status()
        page = r.json()
        out += page
        if len(page) < 1000:
            break
        off += 1000
    return out


def simplified(s: str) -> str:
    try:
        import opencc
        return opencc.OpenCC("tw2sp").convert(s)
    except Exception:
        return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    books = fetch_books()
    parsed = [b for b in books if b.get("parsed_at")]
    print(f"全庫 {len(books):,} 本，已解析 {len(parsed):,} 本（分母）")

    cand, skipped = [], Counter()
    for b in parsed:
        ft = (b.get("file_type") or "").lower()
        if ft not in UPGRADABLE:
            skipped["格式本來就有頁碼或無法升級"] += 1
            continue
        p = CHUNKS / f"{b['id']}.jsonl"
        if not p.exists():
            skipped["Drive 沒有 JSONL"] += 1
            continue
        try:
            kind, _ = scan_file(p)
        except Exception:
            skipped["讀不了"] += 1
            continue
        if kind != "none":
            skipped["已經有頁碼"] += 1
            continue
        title = (b.get("title") or "").strip()
        if len(title) < MIN_TITLE:
            skipped["書名太短"] += 1
            continue
        cand.append(b)

    print(f"\n可去 z-lib 找 PDF 版的：{len(cand):,} 本")
    for k, v in skipped.most_common():
        print(f"  （略過）{k}: {v:,}")
    print("\n格式分佈:", dict(Counter((b.get('file_type') or '?') for b in cand).most_common()))
    print("書架分佈:", dict(Counter(
        ('全集' if b.get('collection') == 'collected-works' else '圖書館') for b in cand)))

    rows = []
    for b in cand:
        title = (b.get("title") or "").strip()
        who = (b.get("author") or "").strip()
        key = "pagefix-" + hashlib.sha1(f"{title}|{who}".encode()).hexdigest()[:10]
        rows.append({
            "key": key,
            "query": f"{title} {who}".strip(),
            "expect": title,
            "who": who,
            "source": "pagefix",          # 🚨 zlib_retire_owned 要放行這個 source
            "zh": f"{who}《{title}》" if who else f"《{title}》",
            "expect_s": simplified(title),
            "who_s": simplified(who),
            "existing_id": b["id"],       # 抓到之後是「換檔」不是「新增一本」
            "existing_type": b.get("file_type"),
        })

    if not args.write:
        print(f"\n（未寫檔）加 --write 會寫 {len(rows):,} 筆到 {OUT}")
        for r in rows[:5]:
            print("   ", r["zh"][:60])
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n已寫 {len(rows):,} 筆到 {OUT}")


if __name__ == "__main__":
    main()
