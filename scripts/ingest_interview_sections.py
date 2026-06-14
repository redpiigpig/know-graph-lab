#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 OCR 出來的「訪談錄」逐頁文字 → lit_review_sections（通用版）。

給法鼓山系訪談錄共用（惠敏《六十感恩紀》ref=zhc36750ae-2014、
李志夫《浮塵掠影》ref=zhfd96f758-2013…）。

- 來源：<out>/*.txt（每檔一頁，開頭「【頁 N】」）。
- 目標：lit_review_entries(project=mahaprajapati-revolution, ref_key=<ref>) 下的
  單語(zh)全文；reader 對「每段只有一個 version code」以中文單欄呈現。
- order_index = 印刷頁碼（照片倒序拍，依頁碼排序才正確）；無頁碼者排最後。
- 冪等：on_conflict (entry_id, version_code, order_index)。

  python -X utf8 scripts/ingest_interview_sections.py --ref zhc36750ae-2014 \
      --out scripts/data/huimin_liushi_ganen [--dry-run]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

PAGE_RE = re.compile(r"【頁\s*([0-9]+)】")

load_dotenv()
U = os.environ["SUPABASE_URL"]
K = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": K, "Authorization": f"Bearer {K}", "Content-Type": "application/json"}


def entry_id(slug: str, ref: str) -> int:
    r = requests.get(f"{U}/rest/v1/lit_review_entries?project_slug=eq.{slug}&ref_key=eq.{ref}&select=id",
                     headers=H, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no entry for {slug}/{ref}")
    return rows[0]["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--slug", default="mahaprajapati-revolution")
    ap.add_argument("--only-range", default="", help="只收這段印刷頁碼 lo,hi（含）")
    ap.add_argument("--exclude-range", default="", help="排除這段印刷頁碼 lo,hi（含）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    only = tuple(int(x) for x in args.only_range.split(",")) if args.only_range else None
    excl = tuple(int(x) for x in args.exclude_range.split(",")) if args.exclude_range else None

    files = sorted(Path(args.out).glob("*.txt"))
    rows, fallback, seen, skipped, filtered = [], 9000, set(), 0, 0
    for f in files:
        text = f.read_text(encoding="utf-8").strip()
        first = text.splitlines()[0] if text else ""
        if not text or "（無正文）" in first:
            skipped += 1
            continue
        m = PAGE_RE.search(text)
        if m:
            oi = int(m.group(1))
            # page-range filters apply only to pages with a real printed number
            if only and not (only[0] <= oi <= only[1]):
                filtered += 1
                continue
            if excl and excl[0] <= oi <= excl[1]:
                filtered += 1
                continue
            while oi in seen:
                oi += 1000
        else:
            if only:           # unnumbered pages excluded when a positive range is requested
                filtered += 1
                continue
            oi = fallback
            fallback += 1
        seen.add(oi)
        rows.append({"oi": oi, "text": text})

    rows.sort(key=lambda r: r["oi"])
    print(f"{len(files)} files → {len(rows)} sections ({skipped} empty/photo, {filtered} out-of-range)")
    print("  page nums:", ", ".join(str(r["oi"]) for r in rows[:12]), "..." if len(rows) > 12 else "")
    if args.dry_run:
        return

    eid = entry_id(args.slug, args.ref)
    payload = [{"entry_id": eid, "version_code": "zh", "order_index": r["oi"],
                "text": r["text"], "char_count": len(r["text"])} for r in rows]
    resp = requests.post(
        f"{U}/rest/v1/lit_review_sections?on_conflict=entry_id,version_code,order_index",
        headers={**H, "Prefer": "resolution=merge-duplicates,return=minimal"},
        data=json.dumps(payload), timeout=120)
    if resp.status_code not in (200, 201, 204):
        sys.exit(f"upsert error {resp.status_code}: {resp.text[:300]}")
    requests.patch(f"{U}/rest/v1/lit_review_entries?id=eq.{eid}",
                   headers={**H, "Prefer": "return=minimal"},
                   data=json.dumps({"fulltext_status": "translated"}), timeout=30)
    print(f"✓ upserted {len(payload)} zh sections under entry {eid} (ref {args.ref}); status→translated")


if __name__ == "__main__":
    main()
