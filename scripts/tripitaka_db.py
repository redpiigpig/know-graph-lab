"""佛教大藏經 /tripitaka —— 目錄 rows 進 Supabase、逐段全文上 R2。

分工（遵守「新大內容表一律 file-backed」）：
  Supabase  只存目錄（2,554 列、約 1.5 MB）＋各部的對照語言旗標
  Drive     `_tripitaka/{id}.jsonl`（逐段正文）為 canonical
  R2        `tripitaka/{id}.jsonl.gz`（線上後備，單檔多在 100 KB 內）

9,700 萬字的正文絕不進 DB —— 2026-07 那次超量鎖站就是這樣來的。

  python scripts/tripitaka_db.py --schema          # 建表（冪等）
  python scripts/tripitaka_db.py --push            # catalog.json → tripitaka_works
  python scripts/tripitaka_db.py --sync-drive      # 本機 out/ → Drive _tripitaka/
  python scripts/tripitaka_db.py --push-r2 [--only T0262]
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_cbeta as tc  # noqa: E402

REF = "vloqgautkahgmqcwgfuo"
MGMT = f"https://api.supabase.com/v1/projects/{REF}/database/query"
CATALOG = Path(os.environ.get("TRIPITAKA_CATALOG", "C:/tmp/cbeta/catalog.json"))
LOCAL_OUT = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
R2_PREFIX = "tripitaka/"


def _env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        raise RuntimeError(f"缺 {key}")
    return v


def sql(query: str) -> list:
    req = urllib.request.Request(
        MGMT, data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {_env('SUPABASE_ACCESS_TOKEN')}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode()
    return json.loads(body) if body.strip() else []


SCHEMA = """
create table if not exists tripitaka_works (
  id              text primary key,
  canon           text not null,
  vol             int  not null,
  work_no         int  not null,
  work_suffix     text default '',
  title_zh        text not null,
  series          text,
  byline          text,
  dynasty         text,
  translator      text,
  author          text,
  lost_translator boolean default false,
  extent          text,
  juan_count      int,
  division_key    text not null,
  japanese        boolean default false,
  xml_path        text,
  seg_count       int default 0,
  char_count      int default 0,
  toc_count       int default 0,
  -- equiv_count：大正藏原註標出的巴利對應條數
  -- term_count / term_langs：CBETA <cb:tt> 漢梵巴詞條（全藏 29,930 組、142 部）
  equiv_count     int default 0,
  term_count      int default 0,
  term_langs      text[] default '{}',
  parallel_langs  text[] default '{}',
  pali_ref        text,
  sanskrit_ref    text,
  tibetan_toh     text,
  parallel_count  int default 0,
  display_order   int
);
create index if not exists tripitaka_works_div_idx
  on tripitaka_works (division_key, display_order);
create index if not exists tripitaka_works_canon_idx
  on tripitaka_works (canon, work_no);
create index if not exists tripitaka_works_title_idx
  on tripitaka_works using gin (to_tsvector('simple', title_zh));

-- 逐段的跨語對照。段本身在檔案裡，這裡只記「哪一段對到什麼」。
-- src: taisho-equiv（大正藏原註）/ suttacentral / gretil / 84000 / manual
create table if not exists tripitaka_parallels (
  id       bigserial primary key,
  work_id  text not null references tripitaka_works(id) on delete cascade,
  seg      text,
  lang     text not null,
  ref      text not null,
  src      text not null,
  note     text
);
create index if not exists tripitaka_parallels_work_idx on tripitaka_parallels (work_id);
create unique index if not exists tripitaka_parallels_uniq
  on tripitaka_parallels (work_id, coalesce(seg,''), lang, ref, src);

alter table tripitaka_works    enable row level security;
alter table tripitaka_parallels enable row level security;
drop policy if exists tripitaka_works_read on tripitaka_works;
create policy tripitaka_works_read on tripitaka_works for select to authenticated using (true);
drop policy if exists tripitaka_parallels_read on tripitaka_parallels;
create policy tripitaka_parallels_read on tripitaka_parallels for select to authenticated using (true);
"""


def series_of(row: dict) -> str:
    """南傳一部書常被切成數冊（『長部經典(第1卷-第14卷)』×3 冊），
    目錄要按書歸群而不是按冊平鋪。大正藏的 T0220a/b/c 同理。"""
    t = row["title_zh"]
    base = re.sub(r"[（(]第.*?[)）]\s*$", "", t).strip()
    return base or t


def cmd_schema():
    sql(SCHEMA)
    print("✓ tripitaka_works / tripitaka_parallels 已就緒")


COLS = ["id", "canon", "vol", "work_no", "work_suffix", "title_zh", "series", "byline",
        "dynasty", "translator", "author", "lost_translator", "extent", "juan_count",
        "division_key", "japanese", "xml_path", "seg_count", "char_count",
        "toc_count", "equiv_count", "term_count", "term_langs", "display_order"]


def postgrest(path: str, rows: list[dict] | None = None, method: str = "POST"):
    """走 PostgREST（service role key）。DDL 才需要 Management API，
    寫資料不用 —— 2026-08 那把 personal access token 過期時就是靠這條路繞過去的。"""
    url = _env("SUPABASE_URL").rstrip("/") + "/rest/v1/" + path
    key = _env("SUPABASE_SERVICE_ROLE_KEY")
    data = json.dumps(rows, ensure_ascii=False).encode() if rows is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode()
    return json.loads(body) if body.strip() else []


def cmd_push():
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows.sort(key=lambda r: (r["canon"] != "T", r["vol"], r["work_no"], r.get("work_suffix", "")))
    payload = []
    for n, r in enumerate(rows, start=1):
        rec = {c: r.get(c) for c in COLS}
        rec["series"] = series_of(r)
        rec["display_order"] = n
        rec["work_suffix"] = r.get("work_suffix") or ""
        rec["term_langs"] = r.get("term_langs") or []
        payload.append(rec)

    for i in range(0, len(payload), 400):
        postgrest("tripitaka_works?on_conflict=id", payload[i:i + 400])
        print(f"  … {min(i + 400, len(payload))}/{len(payload)}", flush=True)
    print(f"✓ tripitaka_works 已寫入 {len(payload)} 列")


def cmd_sync_drive():
    dst = tc.OUT_DIR
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(LOCAL_OUT.glob("*"))
    print(f"{len(files)} 檔 → {dst}")
    for i, f in enumerate(files, 1):
        t = dst / f.name
        if t.exists() and t.stat().st_size == f.stat().st_size:
            continue
        shutil.copy2(f, t)
        if i % 200 == 0:
            print(f"  … {i}/{len(files)}", flush=True)
    print("✓ Drive 同步完成")


def _r2():
    import boto3  # noqa: F401
    from botocore.config import Config
    import boto3 as b3
    return b3.client("s3", endpoint_url=_env("R2_ENDPOINT"),
                     aws_access_key_id=_env("R2_ACCESS_KEY"),
                     aws_secret_access_key=_env("R2_SECRET_KEY"),
                     region_name="auto", config=Config(signature_version="s3v4"))


def cmd_push_r2(only: str | None):
    s3, bucket = _r2(), _env("R2_BUCKET")
    src = LOCAL_OUT if LOCAL_OUT.exists() else tc.OUT_DIR
    files = sorted(src.glob(f"{only}.*" if only else "*"))
    big = []
    for i, f in enumerate(files, 1):
        raw = f.read_bytes()
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as g:
            g.write(raw)
        data = buf.getvalue()
        # R2 政策：單檔 >10 MB 一律不上（見 docs/r2-policy.md）
        if len(data) > 10 * 1024 * 1024:
            big.append((f.name, len(data)))
            continue
        s3.put_object(Bucket=bucket, Key=f"{R2_PREFIX}{f.name}.gz", Body=data,
                      ContentType="application/json", ContentEncoding="gzip")
        if i % 200 == 0:
            print(f"  … {i}/{len(files)}", flush=True)
    print(f"✓ R2 {len(files) - len(big)} 檔")
    for name, n in big:
        print(f"  ⚠ 超過 10 MB 未上傳（Drive 仍有正本）: {name} {n/1048576:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", action="store_true")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--sync-drive", action="store_true")
    ap.add_argument("--push-r2", action="store_true")
    ap.add_argument("--only", type=str)
    a = ap.parse_args()
    if a.schema:
        cmd_schema()
    if a.push:
        cmd_push()
    if a.sync_drive:
        cmd_sync_drive()
    if a.push_r2:
        cmd_push_r2(a.only)
    if not any([a.schema, a.push, a.sync_drive, a.push_r2]):
        ap.print_help()


if __name__ == "__main__":
    main()
