#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""書籤補不了的「一頁一塊」PDF：改讀書前印刷目錄補 chapter_path（乾跑，2026-09-28）。

背景：scripts/assign_chapters_from_bookmarks.py 用 PDF 內建書籤幫約 2,496 本
「一頁一塊」書補章節；書籤不能用的那批（output/toc_audit/bookmark_chapters.tsv
第二欄 no-usable-bookmarks／toc-read-failed／low-coverage）改用書前印的目錄頁。

做法沿用 scripts/toc_from_toc_pages.py 已驗證過的核心（頁碼解析、印刷頁→PDF 頁
的錨點推算、「那一頁真的有這個標題」驗證閘），本檔只加兩件事：

  1. 自動在前 ~8%（至少 15 頁）找目錄／目次／CONTENTS 頁（原腳本要人工指定
     `--toc-pages`，這裡批次跑要自動抓）。
  2. 沒有 printed_page 錨點的書（本抽樣裡過半數是這樣），退回直接在正文裡找
     標題出現在哪一頁（toc_from_toc_pages 原本只對「目次行沒頁碼」的殘料這樣做，
     這裡放寬成：anchor 推算失敗或整本沒有錨點時都試這條路）。

🚨 本檔只做 `--dry-run` 統計，不寫 JSONL、不推 R2、不改 DB —— 另一支背景程式
   （assign_chapters_from_bookmarks.py）正在動同一批檔案，兩邊不能搶著寫。

用法：
    python -X utf8 scripts/chapters_from_printed_toc.py --ids <id> [<id> ...] --dry-run
    python -X utf8 scripts/chapters_from_printed_toc.py --from-report output/toc_audit/bookmark_chapters.tsv \
        --sample 40 --seed 1 --dry-run --report output/toc_audit/printed_toc_dryrun.tsv
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consolidate_page_chunks as cp  # noqa: E402
import toc_from_toc_pages as tp  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

STATUSES_ELIGIBLE = ("no-usable-bookmarks", "toc-read-failed", "low-coverage")

_HEADER_RE = re.compile(
    r"(目\s*錄|目\s*次|contents?|table\s+of\s+contents)",
    re.IGNORECASE,
)


# ── 目錄頁偵測（純函式） ──────────────────────────────────────────
def is_toc_header_page(content: str) -> bool:
    """開頭幾行是否出現「目錄／目次／CONTENTS」之類的標題字樣。"""
    head = "\n".join((content or "").splitlines()[:6])
    return bool(_HEADER_RE.search(head))


def toc_entry_ratio(content: str) -> float:
    """這一頁的非空行裡，有多少比例被 parse_toc_lines 解成「標題+頁碼」條目。

    用來判斷目錄的續頁（沒有「目錄」抬頭字樣，但整頁都是條目）。
    """
    lines = [l for l in (content or "").splitlines() if l.strip()]
    if not lines:
        return 0.0
    entries, _ = tp.parse_toc_lines(lines)
    return len(entries) / len(lines)


def find_toc_page_range(pages: list[dict], min_scan: int = 15, front_ratio: float = 0.08,
                         max_continuation: int = 10) -> list[int] | None:
    """在書前 ~front_ratio（至少 min_scan 頁）找目錄／目次頁，回傳實體頁序清單。

    找到抬頭頁後往後延伸：只要下一頁「看起來還是條目」就併入（跨頁目錄），
    遇到不像的頁就停；`pages` 需已含 page_number 且是 chunk_type=='page'。
    """
    ordered = sorted((c for c in pages if isinstance(c.get("page_number"), int)),
                      key=lambda c: c["page_number"])
    if not ordered:
        return None
    scan_n = max(min_scan, round(len(ordered) * front_ratio))
    front = ordered[:scan_n]
    start_pos = None
    for i, c in enumerate(front):
        if is_toc_header_page(c.get("content") or ""):
            start_pos = i
            break
    if start_pos is None:
        return None
    result = [front[start_pos]["page_number"]]
    for j in range(start_pos + 1, min(start_pos + 1 + max_continuation, len(ordered))):
        c = ordered[j]
        if toc_entry_ratio(c.get("content") or "") >= 0.3:
            result.append(c["page_number"])
        else:
            break
    return result


# ── 逐條目定位（沿用 toc_from_toc_pages 的推算＋驗證閘） ──────────────
def resolve_entries(entries: list[dict], anchors: list[tuple[int, int]],
                     by_page: dict[int, dict], toc_pages: set[int]) -> tuple[list[dict], list[dict]]:
    """回傳 (resolved, dropped)。resolved 條目多一個 'how' 欄位（anchor／content-search）。"""
    max_printed = max((p for _, p in anchors), default=0)
    resolved, dropped = [], []
    for e in entries:
        hit, how = None, None
        if anchors:
            for cand in tp.digit_candidates(e["printed_page"], max_printed):
                guess = tp.resolve_page(cand, anchors)
                v = tp.verify(guess, e["title"], by_page) if guess else None
                if v is not None:
                    hit, how = v, "anchor"
                    break
        if hit is None:
            page = tp.find_by_title(e["title"], by_page, skip=toc_pages)
            if page is not None:
                hit, how = page, "content-search"
        if hit is None:
            dropped.append(e)
        else:
            resolved.append({**e, "pdf_page": hit, "how": how})
    return resolved, dropped


def enforce_monotonic(resolved: list[dict], tolerance: int = 3) -> tuple[list[dict], list[dict]]:
    """目次原本由上到下印刷頁遞增；定位結果理當同序遞增（允許小抖動）。

    往回跳超過 tolerance 頁的視為誤配（例如標題撞到別處同名字串），丟棄。
    """
    kept, dropped = [], []
    last = -(10 ** 9)
    for e in resolved:
        if e["pdf_page"] < last - tolerance:
            dropped.append(e)
        else:
            kept.append(e)
            last = max(last, e["pdf_page"])
    return kept, dropped


# ── 單本處理 ──────────────────────────────────────────────────
def process_book(bid: str, chunks: list[dict]) -> dict:
    pages = [c for c in chunks if c.get("chunk_type") == "page" and isinstance(c.get("page_number"), int)]
    total_pages = len(pages)
    out = {"id": bid, "total_pages": total_pages, "toc_pages": [], "entries_parsed": 0,
           "entries_resolved": 0, "entries_dropped": 0, "unique_anchors": 0, "covered_pages": 0,
           "coverage_pct": 0.0, "orig_chunks": len(chunks), "merged_chunks": None,
           "status": ""}
    if total_pages < 10:
        out["status"] = "too-short"
        return out

    by_page = {c["page_number"]: c for c in pages}
    toc_page_nums = find_toc_page_range(pages)
    if not toc_page_nums:
        out["status"] = "no-toc-page-found"
        return out
    out["toc_pages"] = toc_page_nums

    lines: list[str] = []
    for p in toc_page_nums:
        lines += (by_page[p].get("content") or "").splitlines()
    entries, _orphans = tp.parse_toc_lines(lines)
    out["entries_parsed"] = len(entries)
    if len(entries) < 3:
        out["status"] = "too-few-entries"
        return out

    anchors = [(c["page_number"], c["printed_page"]) for c in pages if c.get("printed_page")]
    resolved, dropped = resolve_entries(entries, anchors, by_page, set(toc_page_nums))
    resolved = sorted(resolved, key=lambda e: e["pdf_page"])
    resolved, extra_dropped = enforce_monotonic(resolved)
    out["entries_resolved"] = len(resolved)
    out["entries_dropped"] = len(dropped) + len(extra_dropped)
    if not resolved:
        out["status"] = "no-entries-resolved"
        return out
    # 🚨 少數幾條解到、但覆蓋率算出來很高，八成是同一個標題重複命中同一頁（例如
    # 《以西結書註釋》287 條全解到 8 條、全部落在 pdf_page=1 封面）——不是真的定位
    # 到章節，是誤配。至少要有 3 條、且落點大半不重複，才信這批結果。
    out["unique_anchors"] = len({e["pdf_page"] for e in resolved})
    if len(resolved) < 3:
        out["status"] = f"too-few-resolved {len(resolved)}"
        return out
    if out["unique_anchors"] / len(resolved) < 0.5:
        out["status"] = f"duplicate-anchors {out['unique_anchors']}/{len(resolved)}"
        return out

    work = [dict(c) for c in chunks]
    tp.assign(work, resolved, toc_page_nums)
    work_pages = [c for c in work if c.get("chunk_type") == "page"]
    covered = sum(1 for c in work_pages
                  if c.get("chapter_path") and c["chapter_path"] != "目次"
                  and c["page_number"] not in toc_page_nums)
    out["covered_pages"] = covered
    out["coverage_pct"] = round(covered / total_pages, 4) if total_pages else 0.0
    if out["coverage_pct"] < 0.5:
        out["status"] = f"low-coverage {covered}/{total_pages}"
        return out

    merged = cp.consolidate(work)
    out["merged_chunks"] = len(merged)
    out["status"] = "ok"
    return out


# ── 批次跑 ──────────────────────────────────────────────────
def load_candidate_ids(report_path: Path) -> list[str]:
    ids = []
    for line in report_path.open(encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 2:
            continue
        bid, status = parts
        if status.startswith(STATUSES_ELIGIBLE):
            ids.append(bid)
    return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", default=None)
    ap.add_argument("--from-report", default=None)
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", default=str(ROOT / "output/toc_audit/printed_toc_dryrun.tsv"))
    args = ap.parse_args()

    if not args.dry_run:
        print("🚨 本腳本只支援 --dry-run（不寫 JSONL／R2／DB），請加 --dry-run", file=sys.stderr)
        return 2

    if args.ids:
        ids = args.ids
    elif args.from_report:
        ids = load_candidate_ids(Path(args.from_report))
        if args.sample:
            random.Random(args.seed).shuffle(ids)
            ids = ids[: args.sample]
    else:
        print("需要 --ids 或 --from-report", file=sys.stderr)
        return 2

    rows = []
    stat: dict[str, int] = {}
    for bid in ids:
        p = CH / f"{bid}.jsonl"
        try:
            chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception as e:  # noqa: BLE001
            rows.append({"id": bid, "status": f"read-error {type(e).__name__}"})
            stat["read-error"] = stat.get("read-error", 0) + 1
            continue
        res = process_book(bid, chunks)
        rows.append(res)
        key = res["status"].split(" ")[0]
        stat[key] = stat.get(key, 0) + 1

    out_path = Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("id\ttotal_pages\ttoc_pages\tentries_parsed\tentries_resolved\tentries_dropped\t"
                "covered_pages\tcoverage_pct\torig_chunks\tmerged_chunks\tstatus\n")
        for r in rows:
            f.write("\t".join(str(r.get(k, "")) for k in (
                "id", "total_pages", "toc_pages", "entries_parsed", "entries_resolved",
                "entries_dropped", "covered_pages", "coverage_pct", "orig_chunks",
                "merged_chunks", "status")) + "\n")

    print(f"共 {len(ids)} 本；{stat}")
    print(f"報告：{out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
