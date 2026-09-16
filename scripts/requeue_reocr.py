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
  python scripts/requeue_reocr.py run [--limit 5] [--tier REOCR] [--engine gemini|mineru]
  python scripts/requeue_reocr.py run --from-ledger --engine mineru --limit 40
  python scripts/requeue_reocr.py status
  python scripts/requeue_reocr.py retry-rejected   # 清 rejected 狀態重排

--engine mineru 走本機 GPU（scripts/mineru_ocr.py），不吃配額、不會 429/503，
適合把 Gemini 失敗掉的那批補回來；開跑前會先自檢環境，壞掉就整場跳過而不是
把每一本都誤標成 ocr_failed。預設仍是 gemini，排程行為不變。

🚨 --from-ledger 改從 ledger 取「曾經失敗的書」，不看 quality_tiers.json。
那份 tier 檔是某一次 sweep 的快照，重新分類之後就對不上：2026-09-16 實測
ledger 有 38 本 ocr_failed／rejected，而當時 REOCR tier 只剩 1 本，照 tier 跑
會處理 0 本卻一路綠燈跑完。要重跑失敗的那批一律用 --from-ledger。
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
CHUNKS_DIR = Path(ENV.get("EBOOK_CHUNKS_DIR") or "G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
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


def step_ocr(bid: str, engine: str = "gemini") -> str:
    """回傳 'staged' | 'quota' | 'env' | 'fail'。

    engine='mineru' 走本機 GPU（`mineru_ocr.py`），不吃配額所以沒有 'quota' 這一路；
    它的 exit 2 是「重複幻覺判準擋下來」＝這一本的問題，不該停整場。
    """
    if engine == "mineru":
        rc = run_cmd([PY, str(SCRIPTS / "mineru_ocr.py"), "run",
                      "--book", bid, "--staging"])
        if (CHUNKS_DIR / f"{bid}.jsonl.new").exists():
            return "staged"
        return "fail"          # 含 rc==2（幻覺擋下）與 rc==1（這本讀不了）

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


def process_book(led: dict, bid: str, title: str, engine: str = "gemini") -> str:
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
        r = step_ocr(bid, engine)
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

def cmd_run(limit: int, tier: str, engine: str = "gemini",
            from_ledger: bool = False) -> None:
    # 前置檢查：REST 被 quota 鎖（402）時 OCR 子行程必炸，會把整批書誤標
    # ocr_failed。環境不可用就整場跳過、ledger 原封不動，明晚再試。
    from quality_sweep import rest_available
    from audit_book_structure import load_env as _le
    if not rest_available(_le()):
        print("⛔ Supabase REST 不可用（quota 鎖定？）— 本輪跳過，佇列不動")
        return
    if engine == "mineru":
        # 本機引擎的「環境壞掉」會讓每一本都失敗，先驗一次再開跑，
        # 免得整批書被誤標成 ocr_failed（Gemini 那路是靠 exit code 分辨）。
        if subprocess.run([PY, str(SCRIPTS / "mineru_ocr.py"), "check"]).returncode != 0:
            print("⛔ MinerU 環境自檢不過 — 本輪跳過，佇列不動")
            return
    led = load_ledger()
    if from_ledger:
        # 🚨 別拿 quality_tiers.json 當「誰失敗了」的來源 —— 它是某一次 sweep 的快照，
        # 之後重新分類過就對不上了。2026-09-16 實測：帳本裡 38 本 ocr_failed／rejected，
        # 而當時的 REOCR tier 只剩 1 本，照 tier 跑會處理 0 本卻回報成功。
        # 帳本才是「哪些書失敗過」的權威來源。
        books = [{"id": bid, "title": e.get("title") or ""}
                 for bid, e in led.items()
                 if e.get("state") in ("ocr_failed", "rejected", "pending")]
        # process_book 對 done/rejected 會直接回傳不做事，所以這裡明白地把狀態退回
        # pending 讓狀態機重跑。原本的失敗理由留在 ledger 的其他欄位裡。
        reset = 0
        for b in books:
            if led.get(b["id"], {}).get("state") in ("ocr_failed", "rejected"):
                led[b["id"]]["state"] = "pending"
                reset += 1
        if reset:
            save_ledger(led)
        print(f"從 ledger 取待重跑清單：{len(books)} 本（重設 {reset} 本為 pending）")
        todo = books
    else:
        tiers = json.loads(TIERS_FILE.read_text(encoding="utf-8"))
        books = [b for b in tiers["tiers"].get(tier, [])
                 if "PATH_BROKEN" not in b.get("flags", [])]
        todo = [b for b in books if led.get(b["id"], {}).get("state", "pending")
                not in ("done", "rejected", "ocr_failed")]
        if books and not todo:
            print(f"⚠ {tier} tier {len(books)} 本全都處理過了 —— 要重跑失敗的那批"
                  f"請加 --from-ledger（tier 快照不含它們）")
    src = "ledger" if from_ledger else f"{tier} tier"
    print(f"{src}：{len(books)} 本，其中 {len(todo)} 本待處理；"
          f"本輪 limit={limit}　引擎={engine}")
    if not todo:
        print("⛔ 待處理 0 本 —— 先確認清單來源對不對，不要當成「跑完了」")
        return
    done = 0
    for b in todo:
        if done >= limit:
            break
        print(f"\n▶ {b['id']}  {(b.get('title') or '')[:40]}", flush=True)
        final = process_book(led, b["id"], b.get("title") or "", engine)
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
        engine = args[args.index("--engine") + 1] if "--engine" in args else "gemini"
        if engine not in ("gemini", "mineru"):
            sys.exit(f"--engine 只接受 gemini 或 mineru，收到 {engine}")
        cmd_run(limit, tier, engine, from_ledger="--from-ledger" in args)
    elif cmd == "status":
        cmd_status()
    elif cmd == "retry-rejected":
        cmd_retry_rejected()
    else:
        sys.exit(__doc__)
