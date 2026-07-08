#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全館轉錄品質評分 sweep（純規則零 LLM）。

整合既有三支稽核器的訊號成單一 quality_score / quality_flags / tier，寫回
ebooks 表並輸出重轉優先清單，取代靜態 re-ocr-worklist.md：

  - audit_book_structure.py 的門檻（TINY/GIANT/HEADING_MIN）與 parse_error 分類
  - structure_audit.py 的 S2-S6 結構髒污 mess_score（扣除 S1 NO_TOC 避免重複計分）
  - re-ocr-worklist 的空白率定義（char_count < 100 = 空白 chunk）

計分（score_book_quality 純函式，見 tests/test_quality_sweep_scoring.py）：
  score = 100 − min(50, blank_rate×100)
              − (20 NO_TOC | 10 PARTIAL_TOC)   ← page 型書豁免
              − (15 OVER_FRAGMENTED)            ← page 型書豁免
              − (15 UNDER_SEGMENTED)
              − min(20, mess_wo_toc // 5)
  NEEDS_OCR → 0；clamp 0..100

Tier：REOCR（待OCR/OCR失敗/空白過半）→ requeue_reocr.py
      FIX_TOC（只缺目錄）→ fix_book_structure.py
      RESTANDARDIZE（已標準化但結構爛）→ standardize 重跑
      GOOD（≥80）/ FAIR（其餘）

Usage:
  python scripts/quality_sweep.py --all                 # 全館
  python scripts/quality_sweep.py --recent 1            # 最近 N 天動過的書
  python scripts/quality_sweep.py --ids id1,id2
  python scripts/quality_sweep.py --all --limit 50 --dry-run
輸出：ebooks.quality_* 三欄位 + c:/tmp/quality_tiers.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_book_structure import (  # noqa: E402
    TINY, HEADING_MIN, BENIGN_PARSE_ERRORS, OCR_MARKERS, PATH_MARKERS, load_env,
)
import structure_audit  # noqa: E402  (S2-S6 mess_score)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BLANK = 100          # char_count 低於此 = 空白 chunk（re-ocr-worklist 同義）
GIANT = 80_000
OCR_FAILED_MARKERS = ("OCR:", "Haiku-OCR:")   # 永久失敗也算 REOCR 候選

TIER_REOCR = "REOCR"
TIER_RESTANDARDIZE = "RESTANDARDIZE"
TIER_FIX_TOC = "FIX_TOC"
TIER_GOOD = "GOOD"
TIER_FAIR = "FAIR"

TIERS_OUT = Path("c:/tmp/quality_tiers.json")


@dataclass
class BookSignals:
    n_chunks: int
    blank_rate: float      # char_count < 100 的比例
    no_toc_rate: float     # chapter_path 空的比例
    tiny_rate: float       # char_count < 150 的比例
    giant_n: int           # char_count > 80K 的 chunk 數
    mess_wo_toc: float     # structure_audit mess_score 扣掉 S1 NO_TOC 成分
    per_page_only: bool    # PDF 純逐頁切（主流書況，結構罰則全豁免）
    needs_ocr: bool        # 待 OCR / OCR 永久失敗
    path_broken: bool      # Drive 檔案開不了
    standardized: bool


def score_book_quality(s: BookSignals) -> tuple[int, list[str], str]:
    """純函式：訊號 → (score 0-100, flags, tier)。"""
    flags: list[str] = []
    if s.path_broken:
        flags.append("PATH_BROKEN")
    if not s.standardized:
        flags.append("NOT_STANDARDIZED")

    if s.needs_ocr:
        flags.insert(0, "NEEDS_OCR")
        return 0, flags, (TIER_REOCR if not s.path_broken else TIER_FAIR)

    score = 100

    blank_penalty = min(50, round(s.blank_rate * 100))
    score -= blank_penalty
    if s.blank_rate > 0.2:
        flags.append("BLANK_BODY")

    if s.per_page_only:
        flags.append("PER_PAGE_ONLY")   # 逐頁書：目錄/碎裂豁免，只記 flag
    else:
        if s.no_toc_rate > 0.9:
            score -= 20
            flags.append("NO_TOC")
        elif s.no_toc_rate >= 0.3:
            score -= 10
            flags.append("PARTIAL_TOC")
        if s.tiny_rate > 0.4:
            score -= 15
            flags.append("OVER_FRAGMENTED")

    if s.giant_n > 0:
        score -= 15
        flags.append("UNDER_SEGMENTED")

    mess_penalty = min(20, int(s.mess_wo_toc) // 5)
    score -= mess_penalty
    if s.mess_wo_toc >= 25:
        flags.append("STRUCTURE_MESS")

    score = max(0, min(100, score))

    # tier（順序即優先序）
    if s.blank_rate > 0.5 and not s.path_broken:
        tier = TIER_REOCR
    elif "NO_TOC" in flags and not any(
        f in flags for f in ("BLANK_BODY", "OVER_FRAGMENTED", "UNDER_SEGMENTED", "STRUCTURE_MESS")
    ):
        tier = TIER_FIX_TOC
    elif score >= 80:
        tier = TIER_GOOD
    elif score >= 60:
        tier = TIER_FAIR
    elif s.standardized:
        tier = TIER_RESTANDARDIZE
    else:
        tier = TIER_FAIR
    return score, flags, tier


# ── DB 存取（REST 優先；402 quota 鎖定時 fallback Management API SQL）────

def mgmt_rows(env: dict, sql: str, timeout: int = 300) -> list[dict]:
    token = env["SUPABASE_ACCESS_TOKEN"]
    ref = env["SUPABASE_URL"].replace("https://", "").split(".")[0]
    url = f"https://api.supabase.com/v1/projects/{ref}/database/query"
    r = requests.post(url, json={"query": sql},
                      headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
    if r.status_code not in (200, 201):
        raise SystemExit(f"mgmt SQL failed {r.status_code}: {r.text[:300]}")
    return r.json()


def rest_available(env: dict) -> bool:
    URL, KEY = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.get(f"{URL}/rest/v1/ebooks?select=id&limit=1",
                     headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"}, timeout=30)
    return r.status_code == 200


# ── harvest ──────────────────────────────────────────────────────────────

def harvest_signals(meta: dict, chunks: list[dict]) -> BookSignals:
    """DB meta + chunk previews → BookSignals。"""
    pe = meta.get("parse_error") or ""
    benign = any(m in pe for m in BENIGN_PARSE_ERRORS)
    needs_ocr = (not benign) and any(m in pe for m in OCR_MARKERS + OCR_FAILED_MARKERS)
    path_broken = any(m in pe for m in PATH_MARKERS)

    n = len(chunks)
    if n == 0:
        return BookSignals(0, 1.0, 1.0, 1.0, 0, 0.0, False, needs_ocr, path_broken,
                           bool(meta.get("standardized_at")))

    ccs = [c.get("char_count") or 0 for c in chunks]
    cps = [(c.get("chapter_path") or "").strip() for c in chunks]
    blank_rate = sum(1 for x in ccs if x < BLANK) / n
    tiny_rate = sum(1 for x in ccs if x < TINY) / n
    giant_n = sum(1 for x in ccs if x > GIANT)
    no_toc_rate = sum(1 for x in cps if not x) / n
    nhead = len({x for x in cps if x})

    tp = meta.get("total_pages") or 0
    per_page_only = (meta.get("file_type") == "pdf" and tp > 20
                     and n >= tp * 0.9 and nhead < HEADING_MIN)

    sa = structure_audit.score_book(meta, chunks) if n >= 3 else {}
    mess = sa.get("mess_score", 0.0)
    s1 = (sa.get("signals") or {}).get("no_toc_pct", 0.0)
    mess_wo_toc = max(0.0, mess - 35 * s1)   # S1 已由 no_toc_rate 罰過，避免重複

    return BookSignals(n, blank_rate, no_toc_rate, tiny_rate, giant_n, mess_wo_toc,
                       per_page_only, needs_ocr, path_broken,
                       bool(meta.get("standardized_at")))


def fetch_books(env: dict, ids: list[str] | None, recent_days: int | None,
                use_rest: bool) -> list[dict]:
    select = ("id,title,file_type,total_pages,chunk_count,standardized_at,"
              "parsed_at,parse_error,category,subcategory,collection")
    if not use_rest:
        where = ""
        if ids:
            where = "where id in (" + ",".join(f"'{i}'::uuid" for i in ids) + ")"
        elif recent_days is not None:
            where = (f"where parsed_at >= now() - interval '{recent_days} days' "
                     f"or standardized_at >= now() - interval '{recent_days} days'")
        return mgmt_rows(env, f"select {select} from ebooks {where} order by id")
    URL, KEY = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    filt = ""
    if ids:
        filt = f"&id=in.({','.join(ids)})"
    elif recent_days is not None:
        since = (datetime.now(timezone.utc) - timedelta(days=recent_days)).isoformat()
        filt = f"&or=(parsed_at.gte.{since},standardized_at.gte.{since})"
    rows, off, step = [], 0, 1000
    while True:
        r = requests.get(f"{URL}/rest/v1/ebooks?select={select}{filt}"
                         f"&order=id&offset={off}&limit={step}", headers=H, timeout=120)
        r.raise_for_status()
        c = r.json()
        rows.extend(c)
        if len(c) < step:
            break
        off += step
    return rows


CHUNK_SELECT = "ebook_id,chunk_type,chapter_path,char_count,content,source_lang"


def fetch_chunks(env: dict, book_ids: set[str], use_rest: bool) -> dict[str, list[dict]]:
    """全館分頁掃 ebook_chunks（含 preview），按書分桶。"""
    buckets: dict[str, list[dict]] = defaultdict(list)
    off, step = 0, 10000
    if not use_rest:
        id_filter = ""
        if len(book_ids) <= 200:
            id_filter = ("where ebook_id in ("
                         + ",".join(f"'{i}'::uuid" for i in sorted(book_ids)) + ") ")
        while True:
            c = mgmt_rows(env, f"select {CHUNK_SELECT} from ebook_chunks {id_filter}"
                               f"order by id offset {off} limit {step}")
            for ch in c:
                if ch["ebook_id"] in book_ids:
                    buckets[ch["ebook_id"]].append(ch)
            if len(c) < step:
                break
            off += step
            print(f"  …{off} chunks scanned (mgmt)", flush=True)
        return buckets
    URL, KEY = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    while True:
        r = requests.get(f"{URL}/rest/v1/ebook_chunks?select={CHUNK_SELECT}"
                         f"&order=id&offset={off}&limit={step}", headers=H, timeout=180)
        r.raise_for_status()
        c = r.json()
        for ch in c:
            if ch["ebook_id"] in book_ids:
                buckets[ch["ebook_id"]].append(ch)
        if len(c) < step:
            break
        off += step
        print(f"  …{off} chunks scanned", flush=True)
    return buckets


def write_back(env: dict, results: list[dict], batch: int = 200) -> None:
    """批次 UPDATE quality_* 三欄位（Management API SQL，psycopg2 直連不通）。"""
    token = env["SUPABASE_ACCESS_TOKEN"]
    ref = env["SUPABASE_URL"].replace("https://", "").split(".")[0]
    url = f"https://api.supabase.com/v1/projects/{ref}/database/query"
    for i in range(0, len(results), batch):
        rows = results[i:i + batch]
        values = ",".join(
            f"('{r['id']}'::uuid, {r['score']}, '{json.dumps(r['flags'])}'::jsonb)"
            for r in rows
        )
        sql = (f"UPDATE ebooks AS e SET quality_score=v.score, quality_flags=v.flags, "
               f"quality_checked_at=now() FROM (VALUES {values}) AS v(id,score,flags) "
               f"WHERE e.id=v.id;")
        resp = requests.post(url, json={"query": sql},
                             headers={"Authorization": f"Bearer {token}",
                                      "Content-Type": "application/json"}, timeout=120)
        if resp.status_code not in (200, 201):
            raise SystemExit(f"write_back failed {resp.status_code}: {resp.text[:300]}")
        print(f"  wrote {min(i + batch, len(results))}/{len(results)}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="全館掃描")
    g.add_argument("--ids", help="逗號分隔 ebook_id")
    g.add_argument("--recent", type=int, metavar="N", help="最近 N 天 parse/standardize 過的書")
    ap.add_argument("--limit", type=int, help="只處理前 N 本（抽查用）")
    ap.add_argument("--dry-run", action="store_true", help="不寫 DB，只出報告")
    args = ap.parse_args()

    env = load_env()
    use_rest = rest_available(env)
    if not use_rest:
        print("REST 不可用（quota 鎖定？）→ 改走 Management API SQL")
    ids = args.ids.split(",") if args.ids else None
    books = fetch_books(env, ids, args.recent, use_rest)

    # 尚未 parse 的書在正常 pipeline 佇列中，不評分
    pending = [b for b in books if not b.get("parsed_at") and not b.get("parse_error")]
    books = [b for b in books if b.get("parsed_at") or b.get("parse_error")]
    if args.limit:
        books = books[:args.limit]
    print(f"books to score: {len(books)}（另 {len(pending)} 本未 parse，跳過）")

    buckets = fetch_chunks(env, {b["id"] for b in books}, use_rest)

    results, tiers = [], defaultdict(list)
    for b in books:
        s = harvest_signals(b, buckets.get(b["id"], []))
        score, flags, tier = score_book_quality(s)
        pe = b.get("parse_error") or ""
        if any(m in pe for m in BENIGN_PARSE_ERRORS):
            flags.append("SET_CHILD")   # 套書子卷：requeue 不重 standardize
        r = {"id": b["id"], "title": b.get("title"), "collection": b.get("collection"),
             "score": score, "flags": flags, "tier": tier,
             "n_chunks": s.n_chunks, "blank_rate": round(s.blank_rate, 3)}
        results.append(r)
        tiers[tier].append(r)

    TIERS_OUT.parent.mkdir(parents=True, exist_ok=True)
    TIERS_OUT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scored": len(results),
        "pending_pipeline": len(pending),
        "counts": {t: len(v) for t, v in sorted(tiers.items())},
        "tiers": {t: sorted(v, key=lambda x: x["score"]) for t, v in tiers.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n=== QUALITY SWEEP SUMMARY ===")
    for t in (TIER_REOCR, TIER_RESTANDARDIZE, TIER_FIX_TOC, TIER_FAIR, TIER_GOOD):
        print(f"  {len(tiers.get(t, [])):5d}  {t}")
    print(f"tiers -> {TIERS_OUT}")

    if args.dry_run:
        print("(dry-run：不寫 DB)")
        return
    write_back(env, results)
    print("done.")


if __name__ == "__main__":
    main()
