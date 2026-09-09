#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「Drive 上有檔、但 ebooks 裡沒有這本」的孤兒檔補建 DB 列。

第三種看不見的書：先前只盤點過「有列但沒全文」，漏掉了「連列都沒有」的。這類書
在館藏查詢裡完全隱形——不是查不到全文，是查不到書。2026-09-09 首次盤點時發現
34 個（另有 169 個在 `_待入庫`，那是刻意的暫存區，不動）。

其中 28 個是第 4-5 世紀教會史家的原典中譯（蘇格拉底、索佐門、狄奧多勒、賽維魯），
以每卷一個 docx 放在以「作者，書名，年代」命名的資料夾裡——資料夾式的多卷書，
既有的 ingest 只掃單檔，所以整批漏掉。

分類與作者從路徑推：`電子圖書館/{category}/{sub…}/{作者，書名，年}/{卷}.docx`。
套書一卷一列（[[feedback_set_books_split]]）。

用法：
  python scripts/ingest_orphan_drive_files.py --audit    # 只盤點，寫 output/drive_not_in_db.json
  python scripts/ingest_orphan_drive_files.py --dry-run  # 印出要建的列
  python scripts/ingest_orphan_drive_files.py            # 真的建列
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DRIVE = Path("G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館")
EXT = {".pdf", ".epub", ".docx", ".doc", ".txt", ".mobi", ".azw3", ".chm", ".rtf"}
SKIP_DIRS = {"_待入庫"}
CN = "一二三四五六七八九十十一十二十三十四十五"


def with_retry(fn, *, tries: int = 6, what: str = "request"):
    """Supabase 在 parse_worker 同時跑的時候會直接重置連線（WinError 10054）。
    這支腳本本來就常跟共用管線並行，退避重試比要求對方讓路實際。"""
    import time
    for i in range(1, tries + 1):
        try:
            return fn()
        except requests.exceptions.RequestException as e:
            if i == tries:
                raise
            print(f"   {what} 第 {i} 次失敗（{type(e).__name__}），{3 * i} 秒後重試",
                  file=sys.stderr)
            time.sleep(3 * i)


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def known_filenames(env) -> set[str]:
    """DB 裡已登記的檔名（keyset 分頁；PostgREST 沒帶 limit 會靜默截在 1000 筆）。"""
    H = {"apikey": env["SUPABASE_SERVICE_ROLE_KEY"],
         "Authorization": f'Bearer {env["SUPABASE_SERVICE_ROLE_KEY"]}'}
    out, last = set(), ""
    while True:
        params = {"select": "id,file_path", "order": "id", "limit": "1000"}
        if last:
            params["id"] = f"gt.{last}"
        r = with_retry(lambda: requests.get(
            f'{env["SUPABASE_URL"]}/rest/v1/ebooks', headers=H, params=params, timeout=60),
            what="撈 file_path")
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        for b in page:
            fp = (b.get("file_path") or "").replace("/", "\\").lower()
            if fp:
                out.add(fp.rsplit("\\", 1)[-1])
        if len(page) < 1000:
            break
        last = page[-1]["id"]
    return out


def describe(p: Path) -> dict:
    """從路徑推 category / subcategory / author / title。"""
    rel = p.relative_to(DRIVE)
    parts = list(rel.parts)
    category = parts[0]
    # 最後一段是檔名；倒數第二段若含全形逗號，是「作者，書名，年」的多卷資料夾
    folder = parts[-2] if len(parts) >= 2 else ""
    sub = "/".join(parts[1:-1]) if len(parts) > 2 else ""
    author = title = None
    if "，" in folder:
        bits = [b.strip() for b in folder.split("，")]
        author = bits[0]
        title = bits[1] if len(bits) > 1 else folder
        sub = "/".join(parts[1:-2]) if len(parts) > 3 else (parts[1] if len(parts) > 2 else "")
        m = re.search(r"(\d+)\s*$", p.stem)          # Church History3 → 卷三
        if m:
            n = int(m.group(1))
            title = f"{title} 卷{CN[n - 1] if 1 <= n <= len(CN) else n}"
    else:
        stem = p.stem
        if "，" in stem:
            bits = [b.strip() for b in stem.split("，")]
            author, title = bits[0], bits[1] if len(bits) > 1 else stem
        else:
            title = stem
    return {"title": title, "author": author, "category": category,
            "subcategory": sub or None, "file_type": p.suffix.lstrip(".").lower(),
            "file_path": str(p).replace("/", "\\")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = load_env()
    known = known_filenames(env)
    print(f"DB 已登記檔名 {len(known):,}")

    orphans = [p for p in DRIVE.rglob("*")
               if p.is_file() and p.suffix.lower() in EXT
               and p.name.lower() not in known
               and not any(d in p.parts for d in SKIP_DIRS)]
    print(f"Drive 有檔但 DB 沒有（排除 _待入庫）：{len(orphans)}")

    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output" / "drive_not_in_db.json").write_text(
        json.dumps([str(p) for p in orphans], ensure_ascii=False, indent=1), encoding="utf-8")
    if args.audit:
        return 0

    rows = [describe(p) for p in orphans]
    for r in rows:
        print(f'  [{r["file_type"]:4s}] {r["category"]}/{r["subcategory"] or "-"} '
              f'│ {r["author"] or "（無作者）"} │ {r["title"]}')
    if args.dry_run:
        return 0

    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    r = with_retry(lambda: requests.post(
        f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Prefer": "return=representation,resolution=ignore-duplicates",
                 "Content-Type": "application/json"},
        json=rows, timeout=120), what="建列")
    if r.status_code in (200, 201):
        print(f"\n建了 {len(r.json())} 列。接著跑 parse_worker 解析全文"
              f"（.doc/.mobi 仍不支援，會標為 skip）。")
        return 0
    print(f"\nINSERT HTTP {r.status_code}: {r.text[:300]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
