#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bible_verses（209MB，852K 節 × 33 版本）搬出 Supabase：
Drive canonical + R2 線上讀（同 ebook chunks hybrid 架構）。

每卷一檔：{"book_code": "gen", "chapters": {"1": [{"v": 1, "t": {"cuv2010": "…"}}]}}
  - Drive: G:/我的雲端硬碟/資料/聖經/_verses/{book}.json.gz
  - R2:    bible-verses/{book}.json.gz

步驟（各自獨立可重跑）：
  python scripts/offload_bible_verses.py export   # DB → Drive gz（Management API，REST 被鎖也能跑）
  python scripts/offload_bible_verses.py upload   # Drive gz → R2
  python scripts/offload_bible_verses.py verify   # 每卷節數對 DB 覆核
  python scripts/offload_bible_verses.py drop     # 覆核過才手動跑：DROP TABLE bible_verses
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_book_structure import load_env  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DRIVE_DIR = Path("G:/我的雲端硬碟/資料/聖經/_verses")
R2_PREFIX = "bible-verses/"

ENV = load_env()


def mgmt_query(sql: str, timeout: int = 300):
    token = ENV["SUPABASE_ACCESS_TOKEN"]
    ref = ENV["SUPABASE_URL"].replace("https://", "").split(".")[0]
    url = f"https://api.supabase.com/v1/projects/{ref}/database/query"
    r = requests.post(url, json={"query": sql},
                      headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
    if r.status_code not in (200, 201):
        raise SystemExit(f"SQL failed {r.status_code}: {r.text[:300]}")
    return r.json()


def book_codes() -> list[str]:
    return [r["book_code"] for r in
            mgmt_query("select distinct book_code from bible_verses order by 1")]


def export() -> None:
    DRIVE_DIR.mkdir(parents=True, exist_ok=True)
    books = book_codes()
    print(f"{len(books)} books to export")
    for i, code in enumerate(books, 1):
        out = DRIVE_DIR / f"{code}.json.gz"
        if out.exists():
            print(f"  [{i}/{len(books)}] {code} exists, skip")
            continue
        rows = mgmt_query(
            f"select chapter, verse, version_code, text from bible_verses "
            f"where book_code='{code}' order by chapter, verse")
        chapters: dict[str, dict[int, dict]] = defaultdict(dict)
        for r in rows:
            ch, v = str(r["chapter"]), r["verse"]
            entry = chapters[ch].setdefault(v, {"v": v, "t": {}})
            entry["t"][r["version_code"]] = r["text"]
        doc = {"book_code": code,
               "chapters": {ch: [vv[k] for k in sorted(vv)] for ch, vv in
                            ((c, m) for c, m in chapters.items())}}
        with gzip.open(out, "wt", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
        print(f"  [{i}/{len(books)}] {code}: {len(rows)} rows -> {out.name} "
              f"({out.stat().st_size // 1024} KB)", flush=True)


def upload() -> None:
    import boto3
    client = boto3.client(
        "s3", endpoint_url=ENV["R2_ENDPOINT"],
        aws_access_key_id=ENV["R2_ACCESS_KEY"],
        aws_secret_access_key=ENV["R2_SECRET_KEY"])
    bucket = ENV["R2_BUCKET"]
    files = sorted(DRIVE_DIR.glob("*.json.gz"))
    print(f"{len(files)} files to upload")
    for i, p in enumerate(files, 1):
        client.upload_file(str(p), bucket, f"{R2_PREFIX}{p.name}")
        print(f"  [{i}/{len(files)}] {p.name}", flush=True)


def verify() -> bool:
    db = {r["book_code"]: r["n"] for r in mgmt_query(
        "select book_code, count(*) n from bible_verses group by 1")}
    ok = True
    for code, n_db in sorted(db.items()):
        p = DRIVE_DIR / f"{code}.json.gz"
        if not p.exists():
            print(f"  MISSING {code}")
            ok = False
            continue
        with gzip.open(p, "rt", encoding="utf-8") as f:
            doc = json.load(f)
        n_file = sum(len(e["t"]) for vs in doc["chapters"].values() for e in vs)
        mark = "OK " if n_file == n_db else "FAIL"
        if n_file != n_db:
            ok = False
        print(f"  {mark} {code}: db={n_db} file={n_file}")
    print("VERIFY", "PASSED" if ok else "FAILED")
    return ok


def drop() -> None:
    if not verify():
        raise SystemExit("verify failed — not dropping")
    mgmt_query("DROP TABLE bible_verses;")
    print("bible_verses dropped.")
    print(mgmt_query("select pg_size_pretty(pg_database_size(current_database())) db_size"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"export": export, "upload": upload, "verify": verify, "drop": drop}.get(
        cmd, lambda: sys.exit(__doc__))()
