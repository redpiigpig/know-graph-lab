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

import time

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_book_structure import (  # noqa: E402
    TINY, HEADING_MIN, BENIGN_PARSE_ERRORS, OCR_MARKERS, PATH_MARKERS, load_env,
)
import structure_audit  # noqa: E402  (S2-S6 mess_score)
# 判準與 ocr_with_gemini 寫入端同一份，見 ocr_repetition 的模組說明。
from ocr_repetition import (  # noqa: E402
    detect_repeated_pages, looks_looping, repetition_rate, repetition_verdict,
)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BLANK = 100          # char_count 低於此 = 空白 chunk（re-ocr-worklist 同義）
# 覆蓋率低於此即視為截斷。留 8% 餘裕給尾頁空白、封底未收錄等正常落差。
COVERAGE_OK = 0.92
GIANT = 80_000
OCR_FAILED_MARKERS = ("OCR:", "Haiku-OCR:")   # 永久失敗也算 REOCR 候選

TIER_REOCR = "REOCR"
TIER_RESTANDARDIZE = "RESTANDARDIZE"
TIER_FIX_TOC = "FIX_TOC"
TIER_GOOD = "GOOD"
TIER_FAIR = "FAIR"

TIERS_OUT = Path("c:/tmp/quality_tiers.json")
# 全文正本。DB 只存 100 字 preview，而「整塊重吐上一塊」的重複多半落在頁的尾段，
# preview 看不到 —— 要判那一種只能讀這裡。
CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")


def drive_repetition_check(book_id: str) -> tuple[bool, str]:
    """拿 Drive 全文再確認一次。回傳 (是否通過, 說明)；讀不到檔案一律當通過。

    為什麼非讀 Drive 不可：preview 版的 repetition_rate 系統性低估。實測
    《性與宗教》Drive 全文判 70% 的頁是前一頁的複述，preview 卻低到連 flag
    都不掛、拿 96 分照樣上架。同一批還有《中國中古時代的禮儀、宗教與制度》
    （52%，剛好 80 分過關）與 ACCS 林前後（24%，83 分）。

    讀不到檔案不扣分：那是「不知道」，不是「不好」——絕不因為拿不到證據而定罪。
    """
    p = CHUNKS_DIR / f"{book_id}.jsonl"
    if not p.exists():
        return True, ""
    rows = []
    try:
        with p.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rows.append({"page": r.get("page_number"),
                                 "text": r.get("content") or ""})
    except OSError:
        return True, ""
    return repetition_verdict(rows)


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
    # chunk 的最大 page_number ÷ 來源 PDF 實際頁數。None = 拿不到來源頁數
    # （EPUB、檔案讀不到）→ 不計分，絕不因為「不知道」而扣分。
    page_coverage: float | None = None
    # 退化迴圈／整塊重吐的 chunk 佔比。結構訊號一個都抓不到這種書。
    repeat_rate: float = 0.0


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

    # 🚨 內容是胡謅的，結構卻完美。前面每一條罰則量的都是結構，而退化迴圈那種書
    # chunk 數對、目錄齊、覆蓋率足 —— 實測《東方化革命》拿 98 分、
    # 《海德格爾式的現代神學》94 分，全都通過 80 分閘門上線可讀。
    # 罰則要夠重：10% 的 chunk 壞掉就足以把一本滿分書壓到閘門（80）以下。
    # 係數取 220 不取 200：200 會讓 10% 剛好落在 80，而閘門是 `>= 80`，於是
    # 「十頁裡有一頁是胡謅的」正好放行 —— 邊界要落在擋下那一側。
    # 5% 只記 flag 不擋：留給人看，但還不到整本下架的程度。
    if s.repeat_rate > 0:
        score -= min(60, round(s.repeat_rate * 220))
        if s.repeat_rate >= 0.05:
            flags.append("REPETITION_LOOP")

    # 覆蓋率：blank_rate 抓「內容爛」，這條抓「內容好但不完整」。
    # 舊 OCR 路徑把整本一次送 Gemini，撞輸出上限後只存下前面幾十頁，
    # 那幾十頁品質極好 → blank_rate≈0、分數接近滿分，書卻缺了九成。
    truncated = s.page_coverage is not None and s.page_coverage < COVERAGE_OK
    if truncated:
        score -= min(50, round((COVERAGE_OK - s.page_coverage) * 60))
        flags.append("TRUNCATED")

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
    if (s.blank_rate > 0.5 or truncated) and not s.path_broken:
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
                       bool(meta.get("standardized_at")),
                       page_coverage(meta, chunks, blank_rate),
                       repetition_rate(chunks))


def source_page_count(path: str) -> int | None:
    """來源 PDF 的實際頁數。只讀頁數索引，不解全文。"""
    if not path or not path.lower().endswith(".pdf"):
        return None
    try:
        import fitz
        with fitz.open(path) as d:
            return d.page_count or None
    except Exception:
        return None


def page_coverage(meta: dict, chunks: list[dict], blank_rate: float) -> float | None:
    """chunk 的最大 page_number ÷ 來源 PDF 實際頁數。拿不到就回 None。

    只對「看起來還不錯」的書做這個檢查——盲區就在那裡。已經 blank 過半的書
    本來就會落 REOCR，沒必要為它們去開 Drive 上的 PDF（那是網路掛載，
    1000 本要跑兩小時）。
    """
    if meta.get("file_type") != "pdf" or blank_rate > 0.5:
        return None
    pages = [c.get("page_number") for c in chunks]
    pages = [p for p in pages if isinstance(p, int) and p > 0]
    if not pages:
        return None                       # 章節型切塊沒有頁碼，本判準不適用
    real = source_page_count(meta.get("file_path") or "")
    if not real:
        return None
    return min(1.0, max(pages) / real)


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


# id 是 keyset 分頁的游標，必須選出來（見 fetch_chunks）。
def fetch_chunks(env: dict, book_ids: set[str], use_rest: bool) -> dict[str, list[dict]]:
    """讀每本書的 JSONL，按書分桶。

    2026-09-16 從 `ebook_chunks` 改讀 Drive 上的 JSONL。那張表退場了
    （1,005,032 列、在 500 MB 的免費層佔 503 MB），而它存的只是每段前 100 字；
    JSONL 是正本，而且評分改用**全文**反而更準 —— 重複幻覺本來就藏在段落尾段，
    100 字 preview 判不出來（見 [[feedback_ocr_repetition_hallucination]]）。

    🚨 **讀不到檔案不可以等於「這本是空的」。** harvest_signals 對 n==0 會判
    blank/no_toc/tiny 全 100%、15 分、掛三個 flag。以前 PostgREST 分頁寫錯就這樣
    誤殺過 1,334 本。現在的對應風險是 G: 沒掛：那會讓**每一本**都讀到 0 個 chunk。
    所以先驗目錄，不通就直接拋例外中止整場，絕不繼續評分。
    """
    if not CHUNKS_DIR.exists():
        raise RuntimeError(
            f"讀不到 {CHUNKS_DIR} —— Drive 卡住了（先 Test-Path 'G:\\我的雲端硬碟'，"
            f"不通就重啟 GoogleDriveFS）。中止，不繼續評分：讀不到檔案會讓全館被判成空白。")

    buckets: dict[str, list[dict]] = defaultdict(list)
    missing = 0
    for bid in book_ids:
        p = CHUNKS_DIR / f"{bid}.jsonl"
        if not p.exists():
            missing += 1
            continue
        rows = []
        try:
            with p.open(encoding="utf-8") as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        c = json.loads(line)
                    except Exception:
                        continue
                    content = c.get("content") or ""
                    rows.append({
                        "id": f"{bid}:{i}",
                        "ebook_id": bid,
                        "chunk_type": c.get("chunk_type"),
                        "chapter_path": c.get("chapter_path"),
                        "char_count": len(content),
                        "content": content,
                        "source_lang": c.get("source_lang"),
                    })
        except Exception as e:
            print(f"  ⚠ 讀不了 {bid}.jsonl：{str(e)[:80]}", flush=True)
            missing += 1
            continue
        if rows:
            buckets[bid] = rows

    got = len(buckets)
    print(f"  讀了 {got}/{len(book_ids)} 本的 JSONL（{missing} 本沒有檔案）", flush=True)
    # 全軍覆沒＝環境問題，不是全館真的壞了。
    if book_ids and got == 0:
        raise RuntimeError(
            f"{len(book_ids)} 本一本都讀不到 JSONL —— 這是環境問題不是書的問題，中止。")
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
    ap.add_argument("--no-drive-check", action="store_true",
                    help="跳過 Drive 全文複核（Drive 掛掉或只想快速估分時用）")
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
        # 只有「即將放行上架」的書才去讀 Drive 全文複核 —— 成本因此有界（全館
        # 約一千多本會走到這裡），而風險正好都集中在這一批：擋下來的書本來就
        # 不會被讀者看到，複不複核沒差。
        if score >= 80 and s.n_chunks and not args.no_drive_check:
            ok, why = drive_repetition_check(b["id"])
            if not ok:
                score = min(score, 50)
                if "REPETITION_LOOP" not in flags:
                    flags.append("REPETITION_LOOP")
                tier = TIER_RESTANDARDIZE
                print(f"  ✗ Drive 全文複核不過：{str(b.get('title'))[:34]} — {why}",
                      flush=True)

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
