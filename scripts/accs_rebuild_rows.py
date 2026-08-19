#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用保留的原始 OCR（c:/tmp/accs_*.raw.jsonl）重建 accs_commentary 的列。

存在的理由：OCR 很貴（Gemini 免費層每 key 每模型每天 20 次），但 raw jsonl 是 canonical
且完整保留，所以**parser 修好後不需要重跑任何一頁 OCR**，直接重建即可。

2026-08-19 首用：`parse_full_ref` 原本只認冒號式章節分隔（'1:1-4'），但 ACCS 各卷體例不一，
全庫 33% 的 ref 是句點式（'1.1-4'；馬太 1-13 佔 79%、希伯來書 68%）。句點式被當成「單獨一節」
→ build_rows_auto 沿用上一章 → 整章註釋錯位（希伯來書 2/7/8/13 章整章被吸進第 1 章）。

  python scripts/accs_rebuild_rows.py            # 乾跑，只比對數字
  python scripts/accs_rebuild_rows.py --apply    # 實際重建（先備份到 c:/tmp/accs_rows_backup/）
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import ingest_accs_genesis as ing          # noqa: E402  (載 .env、SUPABASE_*、upsert_rows)
from accs_commentary import build_rows_auto  # noqa: E402

RAW_DIR = Path("c:/tmp")
BACKUP_DIR = Path("c:/tmp/accs_rows_backup")


def raw_files() -> list[Path]:
    return sorted(RAW_DIR.glob("accs_*.raw.jsonl"))


def book_of(path: Path) -> str:
    return path.name.split("_", 2)[1]


def load_entries(path: Path) -> list[dict]:
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.extend(json.loads(line).get("entries", []))
        except json.JSONDecodeError:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="實際重建（預設只乾跑）")
    ap.add_argument("--only", help="只處理此 book_code")
    a = ap.parse_args()

    # 同一書卷可能拆成多個 PDF（創 1-11 / 創 12-50…），要合併後一次建列
    by_book: dict[str, list[dict]] = {}
    for f in raw_files():
        b = book_of(f)
        if a.only and b != a.only:
            continue
        by_book.setdefault(b, []).extend(load_entries(f))

    print(f"{'書卷':<6}{'現有':>7}{'重建後':>8}{'差':>7}   章數變化")
    total_before = total_after = 0
    for book, entries in sorted(by_book.items()):
        cur = ing.fetch_rows(book) if hasattr(ing, "fetch_rows") else None
        rows = build_rows_auto(book, entries, f"ACCS（{book}）")
        before = count_db(book)
        chs_after = sorted({r["chapter"] for r in rows})
        chs_before = db_chapters(book)
        total_before += before
        total_after += len(rows)
        delta = len(rows) - before
        note = f"{len(chs_before)} → {len(chs_after)} 章"
        if set(chs_after) - set(chs_before):
            note += f"（新增 ch{sorted(set(chs_after)-set(chs_before))}）"
        print(f"{book:<6}{before:>7}{len(rows):>8}{delta:>+7}   {note}")

        if a.apply:
            if not rows:
                print(f"   [skip] {book} 重建結果為空，不動原資料")
                continue
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup(book)
            # 先確認備份真的落檔且筆數對得上，才敢刪——刪掉之後 upsert 失敗會留下空書卷
            saved = json.loads((BACKUP_DIR / f"{book}.json").read_text(encoding="utf-8"))
            if len(saved) != before:
                print(f"   [abort] {book} 備份 {len(saved)} 筆 != 現有 {before} 筆，跳過不動")
                continue
            delete_book(book)
            ing.upsert_rows(rows)
            after = count_db(book)
            status = "OK" if after == len(rows) else f"⚠ 寫入 {after} != 預期 {len(rows)}"
            print(f"   -> 重建完成 {after} 筆  {status}")
    print(f"\n合計 {total_before} → {total_after}（{total_after-total_before:+d}）")
    if not a.apply:
        print("（乾跑，未寫入。加 --apply 才實際重建）")
    return 0


# ── DB helpers（走 ingest 既有的 SUPABASE 常數）────────────────────────────
import requests  # noqa: E402

H = {"apikey": ing.SUPABASE_KEY, "Authorization": f"Bearer {ing.SUPABASE_KEY}"}
BASE = f"{ing.SUPABASE_URL}/rest/v1/accs_commentary"


def count_db(book: str) -> int:
    r = requests.get(BASE, headers={**H, "Prefer": "count=exact", "Range": "0-0"},
                     params={"book_code": f"eq.{book}", "select": "id"}, timeout=60)
    cr = r.headers.get("content-range", "*/0")
    return int(cr.split("/")[-1]) if cr.split("/")[-1].isdigit() else 0


PAGE = 1000   # PostgREST 預設一次最多 1000 列——沒分頁會靜靜地只拿到前 1000 筆


def fetch_all(book: str, select: str) -> list[dict]:
    """分頁抓完整個書卷。沒有這層，備份會缺列、章數統計會少算。"""
    out: list[dict] = []
    offset = 0
    while True:
        r = requests.get(BASE, headers={**H, "Range-Unit": "items",
                                        "Range": f"{offset}-{offset + PAGE - 1}"},
                         params={"book_code": f"eq.{book}", "select": select,
                                 "order": "id"}, timeout=120)
        if r.status_code not in (200, 206):
            raise RuntimeError(f"fetch {book} failed: {r.status_code} {r.text[:120]}")
        batch = r.json()
        out.extend(batch)
        if len(batch) < PAGE:
            return out
        offset += PAGE


def db_chapters(book: str) -> list[int]:
    return sorted({row["chapter"] for row in fetch_all(book, "chapter")})


def backup(book: str) -> None:
    (BACKUP_DIR / f"{book}.json").write_text(
        json.dumps(fetch_all(book, "*"), ensure_ascii=False), encoding="utf-8")


def delete_book(book: str) -> None:
    requests.delete(BASE, headers=H, params={"book_code": f"eq.{book}"}, timeout=120)


if __name__ == "__main__":
    raise SystemExit(main())
