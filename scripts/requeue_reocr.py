#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REOCR tier 重轉錄 orchestrator（薄，重 OCR 不可破壞既有良好資料）。

輸入：quality_sweep.py 產出的 c:/tmp/quality_tiers.json 之 REOCR tier。
流程（每本，ledger 冪等續跑）：
  pending → 備份 {id}.jsonl → {id}.jsonl.bak
          → ocr_with_gemini.py run --book {id} --staging（寫 {id}.jsonl.new，不動 DB/R2）
  ocr_staged → staged gate（頁碼覆蓋不退、空白率改善、字數實質成長、結構基本規則）
  validated  → swap：.new → .jsonl，插 DB previews、推 R2、更新 parsed_at
  swapped    → 重 standardize（standardize_pdf_lite --book）
  restandardized → quality_sweep --ids 重評分 → done
gate 不過 → {id}.jsonl.new 改名 .rejected 留查，原檔原封不動。

Usage:
  python scripts/requeue_reocr.py run [--limit 5] [--tier REOCR]
  python scripts/requeue_reocr.py status
  python scripts/requeue_reocr.py retry-rejected   # 清 rejected 狀態重排
Ledger: scripts/logs/reocr_ledger.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_book_structure import load_env  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS = Path(__file__).resolve().parent
PY = sys.executable
ENV = load_env()
CHUNKS_DIR = Path(ENV.get("EBOOK_CHUNKS_DIR") or "G:/我的雲端硬碟/資料/電子書/_chunks")
TIERS_FILE = Path("c:/tmp/quality_tiers.json")
LEDGER = SCRIPTS / "logs" / "reocr_ledger.json"

BLANK = 100  # chars; 與 quality_sweep 同義


# ── ledger ───────────────────────────────────────────────────────────────

def load_ledger() -> dict:
    try:
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_ledger(led: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")


def set_state(led: dict, bid: str, state: str, **extra) -> None:
    e = led.setdefault(bid, {})
    e["state"] = state
    e["updated_at"] = datetime.now(timezone.utc).isoformat()
    e.update(extra)
    save_ledger(led)


# ── staged gate（純函式）─────────────────────────────────────────────────

def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def jsonl_stats(chunks: list[dict]) -> dict:
    n = len(chunks)
    texts = [(c.get("content") or "") for c in chunks]
    pages = [c.get("page_number") for c in chunks if c.get("page_number") is not None]
    return {
        "n": n,
        "total_chars": sum(len(t) for t in texts),
        "blank_rate": (sum(1 for t in texts if len(t) < BLANK) / n) if n else 1.0,
        "max_page": max(pages) if pages else 0,
    }


def staged_gate(old_chunks: list[dict], new_chunks: list[dict]) -> tuple[bool, list[str]]:
    """重 OCR 成品必須全面優於舊檔才准 swap。"""
    problems: list[str] = []
    if not new_chunks:
        return False, ["new JSONL is empty"]
    idx = [c.get("chunk_index") for c in new_chunks]
    if idx != list(range(len(new_chunks))):
        problems.append("chunk_index not contiguous 0..N-1")
    if any(c.get("chunk_type") not in ("page", "chapter", "section") for c in new_chunks):
        problems.append("invalid chunk_type")
    pages = [c.get("page_number") for c in new_chunks if c.get("page_number") is not None]
    if pages and pages != sorted(pages):
        problems.append("page_number not monotonically increasing")

    old, new = jsonl_stats(old_chunks), jsonl_stats(new_chunks)
    if new["max_page"] < old["max_page"]:
        problems.append(f"page coverage lost: {new['max_page']} < {old['max_page']}")
    if new["blank_rate"] >= old["blank_rate"] and old["blank_rate"] > 0.05:
        problems.append(f"blank_rate not improved: {new['blank_rate']:.2f} >= {old['blank_rate']:.2f}")
    if new["total_chars"] <= old["total_chars"] * 1.1 and old["blank_rate"] > 0.5:
        problems.append(f"chars no real gain: {new['total_chars']} vs {old['total_chars']}")
    return not problems, problems


# ── steps ────────────────────────────────────────────────────────────────

def run_cmd(argv: list[str]) -> int:
    print(f"  $ {' '.join(str(a) for a in argv[1:])}", flush=True)
    return subprocess.run(argv, cwd=str(SCRIPTS.parent)).returncode


def step_ocr(bid: str) -> str:
    """回傳 'staged' | 'quota' | 'env' | 'fail'。"""
    rc = run_cmd([PY, str(SCRIPTS / "ocr_with_gemini.py"), "run",
                  "--book", bid, "--staging"])
    if (CHUNKS_DIR / f"{bid}.jsonl.new").exists():
        return "staged"
    if rc == 2:
        return "quota"
    # 子行程炸掉（traceback、環境錯誤）≠ 這本書 OCR 失敗：不燒佇列，整場停
    if rc != 0:
        return "env"
    return "fail"


def swap_and_publish(bid: str) -> bool:
    """gate 過後：.new 轉正 → DB previews → R2 → parsed_at。"""
    new_p = CHUNKS_DIR / f"{bid}.jsonl.new"
    live_p = CHUNKS_DIR / f"{bid}.jsonl"
    new_p.replace(live_p)
    import ocr_with_gemini as og
    chunks = [{"page": c.get("page_number") or i + 1, "text": c.get("content") or ""}
              for i, c in enumerate(read_jsonl(live_p))]
    non_empty = [c for c in chunks if c["text"].strip()]
    og.insert_chunk_previews(bid, non_empty)
    og.push_to_r2(bid, live_p)
    og.update_book_done(bid, total_chars=sum(len(c["text"]) for c in non_empty),
                        chunk_count=len(non_empty),
                        total_pages=max(c["page"] for c in non_empty))
    return True


def process_book(led: dict, bid: str, title: str) -> str:
    """推進一本書的狀態機；回傳最終狀態。"""
    st = led.get(bid, {}).get("state", "pending")
    live = CHUNKS_DIR / f"{bid}.jsonl"
    bak = CHUNKS_DIR / f"{bid}.jsonl.bak"
    new = CHUNKS_DIR / f"{bid}.jsonl.new"

    if st in ("done", "rejected"):
        return st

    if st == "pending":
        if live.exists() and not bak.exists():
            bak.write_bytes(live.read_bytes())
        r = step_ocr(bid)
        if r == "quota":
            print("  ⛔ quota — 停在 pending，明日排程續跑", flush=True)
            return "pending"
        if r == "env":
            print("  ⛔ 環境錯誤（REST/相依炸掉）— 停在 pending，整場中止", flush=True)
            return "pending"
        if r == "fail":
            set_state(led, bid, "ocr_failed", title=title)
            return "ocr_failed"
        set_state(led, bid, "ocr_staged", title=title)
        st = "ocr_staged"

    if st == "ocr_staged":
        old_chunks = read_jsonl(bak) if bak.exists() else (read_jsonl(live) if live.exists() else [])
        ok, problems = staged_gate(old_chunks, read_jsonl(new))
        if not ok:
            new.replace(CHUNKS_DIR / f"{bid}.jsonl.rejected")
            set_state(led, bid, "rejected", title=title, problems=problems)
            print(f"  ✗ gate 不過：{problems}", flush=True)
            return "rejected"
        set_state(led, bid, "validated", title=title)
        st = "validated"

    if st == "validated":
        swap_and_publish(bid)
        set_state(led, bid, "swapped", title=title)
        st = "swapped"

    if st == "swapped":
        run_cmd([PY, str(SCRIPTS / "standardize_pdf_lite.py"), bid])
        set_state(led, bid, "restandardized", title=title)
        st = "restandardized"

    if st == "restandardized":
        run_cmd([PY, str(SCRIPTS / "quality_sweep.py"), "--ids", bid])
        run_cmd([PY, str(SCRIPTS / "validate_book_structure.py"), bid])  # 報告用，不擋
        set_state(led, bid, "done", title=title)
        return "done"

    return st


# ── CLI ──────────────────────────────────────────────────────────────────

def cmd_run(limit: int, tier: str) -> None:
    # 前置檢查：REST 被 quota 鎖（402）時 OCR 子行程必炸，會把整批書誤標
    # ocr_failed。環境不可用就整場跳過、ledger 原封不動，明晚再試。
    from quality_sweep import rest_available
    from audit_book_structure import load_env as _le
    if not rest_available(_le()):
        print("⛔ Supabase REST 不可用（quota 鎖定？）— 本輪跳過，佇列不動")
        return
    tiers = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
    books = [b for b in tiers["tiers"].get(tier, [])
             if "PATH_BROKEN" not in b.get("flags", [])]
    led = load_ledger()
    todo = [b for b in books if led.get(b["id"], {}).get("state", "pending")
            not in ("done", "rejected", "ocr_failed")]
    print(f"{tier} tier：{len(books)} 本，其中 {len(todo)} 本待處理；本輪 limit={limit}")
    done = 0
    for b in todo:
        if done >= limit:
            break
        print(f"\n▶ {b['id']}  {(b.get('title') or '')[:40]}", flush=True)
        final = process_book(led, b["id"], b.get("title") or "")
        if final == "pending":   # quota — 全場停
            break
        done += 1
    print("\nledger →", LEDGER)


def cmd_status() -> None:
    led = load_ledger()
    from collections import Counter
    print(Counter(e.get("state") for e in led.values()) or "(ledger empty)")


def cmd_retry_rejected() -> None:
    led = load_ledger()
    n = 0
    for bid, e in led.items():
        if e.get("state") in ("rejected", "ocr_failed"):
            e["state"] = "pending"
            n += 1
    save_ledger(led)
    print(f"reset {n} books to pending")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "run":
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 5
        tier = args[args.index("--tier") + 1] if "--tier" in args else "REOCR"
        cmd_run(limit, tier)
    elif cmd == "status":
        cmd_status()
    elif cmd == "retry-rejected":
        cmd_retry_rejected()
    else:
        sys.exit(__doc__)
