# -*- coding: utf-8 -*-
"""本機 GPU OCR —— MinerU → 本專案的逐頁 JSONL（頁碼原樣保留）。

定位：跟 `ocr_with_gemini.py` 並列的另一條 OCR 路徑。不吃任何配額、不會 429／503，
所以適合整晚跑與重轉錄大批次；Gemini 那條留給它擅長的場合。

🚨 **只能讀 `middle.json` 的 `preproc_blocks`，不可以用 `content_list.json`。**
MinerU 會把跨頁的段落合併、並整段掛到「段落起始的那一頁」。實測《孔子大歷史》
p157 開頭一段 93 字的古文引文（司馬光論孔氏出妻）被搬到 p156——
`content_list.json` 與 `middle.json` 的 `para_blocks` 都中招，只有 `preproc_blocks`
是合併前的狀態、頁碼正確。這件事在本專案是致命的：`page_number` 要撐得起引用，
區塊漂到隔壁頁＝註腳看起來正常卻指錯地方（見 SKILL.md 頁碼政策）。

實測差別（《孔子大歷史》12 頁，原生數位排版、標準答案零誤差）：
    content_list.json   字元正確率 97.28%   最差一頁 13.17%
    preproc_blocks      字元正確率 99.64%   最差一頁  0.92%

另一個實測到的好處：MinerU 輸出**原文原樣**（簡體就是簡體），簡繁轉換留在管線裡由
`to_traditional()`＋`TRAD_FIXES` 處理，錯了可以修。Gemini 是在模型內部自己轉，
實測它把「熏習」(vāsanā) 62 次全轉成「燻習」，而 TRAD_FIXES 沒有這一條，
於是直接寫進館藏無從攔截。

用法：
    python scripts/mineru_ocr.py run --book <ebook_id>
    python scripts/mineru_ocr.py run --pdf <路徑> --out <輸出.jsonl>
    python scripts/mineru_ocr.py run --book <id> --staging   # 寫 .jsonl.new，不動 DB/R2
    python scripts/mineru_ocr.py queue --limit 5             # 吃 OCR 佇列（每日排程用）
    python scripts/mineru_ocr.py check                       # 環境自檢

🚨 **同時只准跑一個。** 這台是 RTX 4050 Mobile 6GB；bat 裡記著 qwen2.5vl:3b
光是視覺計算圖就要 ~6.7 GiB、掉到 CPU 後約 1 tok/min 完全不能用。MinerU 的
pipeline 後端只吃 ~1.1 GB，單獨跑很寬裕，但兩個一起跑就會把彼此擠爆。
每日排程（10/14/18）和手動批次一定會撞在一起，所以用 lock 檔擋，
擋下來回離開碼 4（＝忙碌，不是失敗，呼叫端不該把書標成壞掉）。

離開碼（呼叫端要靠它分辨「這本書不行」和「環境壞了」）：
    0  成功
    1  這一本的問題（PDF 不存在、DB 沒這筆）—— 可以跳過繼續下一本
    2  重複幻覺判準擋下來 —— 也是這一本的問題
    3  🚨 環境問題（DNS／網路／Supabase 不通、MinerU 自己掛了）——
       **整場要停**，不可以當成書的失敗。2026-09-16 踩過：一次短暫斷網讓
       `getaddrinfo failed`，30 本在幾秒內全被標成 ocr_failed，佇列整個燒掉。
    4  另一個 MinerU 正在跑（GPU 被佔），這次什麼都沒做 —— 不是失敗，晚點再來。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
VENV_PY = REPO / "_mineru_venv" / "Scripts" / "python.exe"
MINERU_EXE = REPO / "_mineru_venv" / "Scripts" / "mineru.exe"
CHUNKS_DIR = Path(os.environ.get(
    "EBOOK_CHUNKS_DIR", r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks"))


# ── MinerU 產物 → 逐頁文字 ────────────────────────────────────────────────

def _block_text(block: dict) -> str:
    """一個 block → 純文字。行間補換行，巢狀 block（表格／圖說）遞迴。"""
    parts: list[str] = []
    for line in block.get("lines") or []:
        for span in line.get("spans") or []:
            t = span.get("content") or span.get("html") or ""
            if t:
                parts.append(t)
        parts.append("\n")
    for sub in block.get("blocks") or []:
        parts.append(_block_text(sub))
    return "".join(parts)


def pages_from_middle(middle: dict) -> dict[int, str]:
    """`middle.json` → {0-based 頁索引: 該頁文字}。

    走 `preproc_blocks`（合併前），不走 `para_blocks`／`content_list` ——
    理由見模組開頭那段，這是本檔存在的主要原因。
    """
    out: dict[int, str] = {}
    for page in middle.get("pdf_info") or []:
        idx = int(page.get("page_idx", len(out)))
        blocks = page.get("preproc_blocks")
        if blocks is None:                      # 舊版格式的保險
            blocks = page.get("para_blocks") or []
        out[idx] = "\n".join(_block_text(b) for b in blocks).strip()
    return out


def find_middle_json(out_dir: Path) -> Path:
    hits = sorted(out_dir.rglob("*_middle.json"))
    if not hits:
        raise FileNotFoundError(f"MinerU 沒有產出 middle.json：{out_dir}")
    return hits[0]


# ── 跑 MinerU ─────────────────────────────────────────────────────────────

def run_mineru(pdf: Path, out_dir: Path, lang: str = "ch",
               start: int | None = None, end: int | None = None) -> dict[int, str]:
    """跑一次 MinerU，回傳 {頁索引: 文字}。頁索引以**送進去的 PDF** 為準。"""
    if not MINERU_EXE.exists():
        raise RuntimeError(f"找不到 MinerU：{MINERU_EXE}（venv 沒建好？跑 check 看看）")
    argv = [str(MINERU_EXE), "-p", str(pdf), "-o", str(out_dir),
            "-b", "pipeline", "-m", "ocr", "-l", lang]
    if start is not None:
        argv += ["-s", str(start)]
    if end is not None:
        argv += ["-e", str(end)]

    env = dict(os.environ)
    # 🚨 ModelScope 實測只有 30–40 kB/s，HuggingFace 4.2 MB/s。
    #    但 ~/mineru.json 的 model-source 會蓋過這個環境變數，改那個檔才算數。
    env.setdefault("MINERU_MODEL_SOURCE", "huggingface")

    t0 = time.time()
    proc = subprocess.run(argv, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        tail = (proc.stdout or "")[-1500:] + (proc.stderr or "")[-1500:]
        raise RuntimeError(f"MinerU 失敗 (exit {proc.returncode})：\n{tail}")

    middle = json.loads(find_middle_json(out_dir).read_text(encoding="utf-8"))
    pages = pages_from_middle(middle)
    print(f"  MinerU 讀完 {len(pages)} 頁，耗時 {time.time() - t0:.0f}s", flush=True)
    return pages


# ── 輸出成本專案的 JSONL ──────────────────────────────────────────────────

def to_chunks(pages: dict[int, str], page_offset: int = 0) -> list[dict]:
    """{頁索引: 文字} → 本專案的 chunk 形狀。

    `page_number` 用 1-based 實體頁（`page_offset` 給「只 OCR 後半本」那種場合補回）。
    空白頁保留，不要悄悄丟掉——頁碼覆蓋率的稽核靠它。
    """
    chunks = []
    for i, idx in enumerate(sorted(pages)):
        chunks.append({
            "chunk_index": i,
            "chunk_type": "page",
            "page_number": idx + 1 + page_offset,
            "chapter_path": None,
            "format": "text",
            "content": pages[idx],
        })
    return chunks


def write_jsonl(chunks: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(path)


# ── 品質閘 ────────────────────────────────────────────────────────────────

def quality_report(chunks: list[dict]) -> dict:
    """出貨前自檢。沿用既有的重複幻覺判準，不要另立一套。"""
    texts = [c["content"] for c in chunks]
    n = len(texts)
    blank = sum(1 for t in texts if len(t.strip()) < 30)
    total_chars = sum(len(t) for t in texts)
    rep_ok, rep_msg = True, ""
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from ocr_repetition import repetition_verdict
        rep_ok, rep_msg = repetition_verdict(
            [{"page": c["page_number"], "text": c["content"]} for c in chunks])
    except Exception as e:                       # 模組不在就別擋住流程，但要說
        rep_msg = f"（重複幻覺判準沒跑成：{e}）"
    return {
        "pages": n,
        "blank_pages": blank,
        "blank_rate": round(blank / n, 3) if n else 1.0,
        "total_chars": total_chars,
        "chars_per_page": round(total_chars / n) if n else 0,
        "repetition_ok": rep_ok,
        "repetition_msg": rep_msg,
    }


# ── 指令 ──────────────────────────────────────────────────────────────────

def cmd_check(args) -> int:
    print("=== MinerU 環境自檢 ===")
    ok = True
    print(f"  venv python : {VENV_PY}  {'✓' if VENV_PY.exists() else '✗ 不存在'}")
    print(f"  mineru.exe  : {MINERU_EXE}  {'✓' if MINERU_EXE.exists() else '✗ 不存在'}")
    ok = VENV_PY.exists() and MINERU_EXE.exists()
    if VENV_PY.exists():
        r = subprocess.run([str(VENV_PY), "-c",
                            "import torch;print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"],
                           capture_output=True, text=True)
        print(f"  torch       : {r.stdout.strip() or r.stderr.strip()[:120]}")
    cfg = Path.home() / "mineru.json"
    if cfg.exists():
        d = json.loads(cfg.read_text(encoding="utf-8"))
        src = d.get("model-source")
        print(f"  model-source: {src}"
              f"{'  ⚠ ModelScope 實測只有 30–40 kB/s，建議改 huggingface' if src == 'modelscope' else ''}")
        print("  （🚨 這個檔會蓋過 MINERU_MODEL_SOURCE 環境變數）")
    print(f"  chunks dir  : {CHUNKS_DIR}  {'✓' if CHUNKS_DIR.exists() else '✗ G: 沒掛？'}")
    return 0 if ok else 1


# ── GPU 單例鎖 ────────────────────────────────────────────────────────────

LOCK = REPO / "scripts" / "state" / "mineru_gpu.lock"


def _pid_alive(pid: int) -> bool:
    try:
        out = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{exit 0}} else {{exit 1}}"],
            capture_output=True, timeout=20)
        return out.returncode == 0
    except Exception:
        return True          # 判不出來就當它還活著，寧可多等一輪


def acquire_lock() -> bool:
    """拿到 GPU 就回 True。持有者已經死掉的話接收這把鎖。"""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            old = int(LOCK.read_text(encoding="utf-8").strip().split()[0])
        except Exception:
            old = None
        if old and old != os.getpid() and _pid_alive(old):
            print(f"⛔ 另一個 MinerU 正在跑（PID {old}），這次跳過 —— GPU 只有 6GB，不能兩個一起擠")
            return False
        print(f"  （接收前一個已結束的 lock：PID {old}）")
    LOCK.write_text(f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}", encoding="utf-8")
    return True


def release_lock() -> None:
    try:
        if LOCK.exists() and LOCK.read_text(encoding="utf-8").strip().split()[0] == str(os.getpid()):
            LOCK.unlink()
    except Exception:
        pass


ENV_SIGNS = ("getaddrinfo", "URLError", "ConnectionError", "Connection refused",
             "Temporary failure", "timed out", "Max retries", "SSLError",
             "Remote end closed", "Connection aborted")


def looks_like_env_failure(msg: str) -> bool:
    """這個錯是「環境壞了」還是「這本書不行」。

    分錯的代價不對稱：把環境錯當成書的失敗，會在幾秒內燒掉整個佇列
    （2026-09-16 實測 30 本）；反過來只是多停一次、下次再跑。所以寧可誤判成環境錯。
    """
    return any(s.lower() in (msg or "").lower() for s in ENV_SIGNS)


def cmd_run(args) -> int:
    if args.pdf:
        pdf = Path(args.pdf)
        out_jsonl = Path(args.out) if args.out else pdf.with_suffix(".jsonl")
        book_id = None
    else:
        from dotenv import load_dotenv
        import urllib.request
        load_dotenv(REPO / ".env")
        url = os.environ["SUPABASE_URL"].rstrip("/")
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        req = urllib.request.Request(
            f"{url}/rest/v1/ebooks?id=eq.{args.book}&select=id,title,file_path,total_pages",
            headers={"apikey": key, "Authorization": f"Bearer {key}"})
        try:
            rows = json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            # 查不到書名 ≠ 這本書壞了。DNS／連線問題要讓呼叫端整場停下來。
            print(f"⛔ 查 DB 失敗：{str(e)[:160]}")
            return 3 if looks_like_env_failure(str(e)) else 1
        if not rows:
            print(f"DB 查不到 {args.book}")
            return 1
        book = rows[0]
        pdf = Path(book["file_path"])
        book_id = book["id"]
        print(f"《{book['title']}》 {book.get('total_pages')} 頁")
        out_jsonl = CHUNKS_DIR / (f"{book_id}.jsonl.new" if args.staging else f"{book_id}.jsonl")

    if not pdf.exists():
        # G: 整個不見了是環境問題（Drive 卡住），單一檔案不見才是這本的問題。
        drive_root = Path(str(pdf.drive) + os.sep) if pdf.drive else None
        if drive_root is not None and not drive_root.exists():
            print(f"⛔ {pdf.drive} 掛不上 —— Drive 卡住了，先重啟 GoogleDriveFS")
            return 3
        print(f"找不到 PDF：{pdf}")
        return 1

    try:
        with tempfile.TemporaryDirectory(prefix="mineru_") as td:
            pages = run_mineru(pdf, Path(td), lang=args.lang, start=args.start, end=args.end)
            chunks = to_chunks(pages, page_offset=(args.start or 0))
    except Exception as e:
        msg = str(e)
        print(f"⛔ MinerU 執行失敗：{msg[:200]}")
        return 3 if looks_like_env_failure(msg) else 1

    rep = quality_report(chunks)
    print(f"  頁數 {rep['pages']}　空白 {rep['blank_pages']}（{rep['blank_rate']:.1%}）"
          f"　每頁 {rep['chars_per_page']} 字")
    if not rep["repetition_ok"]:
        print(f"  🚨 {rep['repetition_msg']}")
        print("  → 不寫出。這本留在佇列等重跑，不要把幻覺文字寫進館藏。")
        return 2
    if rep["repetition_msg"]:
        print(f"  {rep['repetition_msg']}")

    write_jsonl(chunks, out_jsonl)
    print(f"  寫出 → {out_jsonl}")
    if args.staging:
        print("  （staging 模式：沒動 DB／R2。接 requeue_reocr 的 staged gate 決定要不要 swap）")
    return 0


def db_size_mb() -> float | None:
    """資料庫現在多大（MB）。量不到回 None —— 量不到不該擋住流程，但要說出來。

    走 Management API：psycopg2 直連是 IPv6-only，這台跑不通
    （見 [[reference_supabase_management_api]]）。
    """
    import urllib.request
    token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    url = os.environ.get("SUPABASE_URL", "")
    if not token or not url:
        return None
    ref = url.split("//")[-1].split(".")[0]
    try:
        req = urllib.request.Request(
            f"https://api.supabase.com/v1/projects/{ref}/database/query",
            data=json.dumps({"query": "select pg_database_size(current_database()) b"}).encode(),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST")
        rows = json.loads(urllib.request.urlopen(req, timeout=45).read())
        return rows[0]["b"] / 1024 / 1024
    except Exception:
        return None


def cmd_queue(args) -> int:
    """吃既有的 OCR 佇列（`parse_error` 含 'no extractable text' 的書）。

    佇列與發布流程完全沿用 `ocr_with_gemini` 那一套 —— 兩條引擎共用同一個佇列
    定義與同一組寫入函式，才不會出現「兩邊各有一套、久了就對不起來」。
    """
    from dotenv import load_dotenv
    load_dotenv(REPO / ".env")
    sys.path.insert(0, str(REPO / "scripts"))
    import ocr_with_gemini as og

    try:
        targets = og.fetch_ocr_targets()
    except Exception as e:
        print(f"⛔ 取佇列失敗：{str(e)[:160]}")
        return 3 if looks_like_env_failure(str(e)) else 1

    if args.exclude:
        skip = set(args.exclude)
        targets = [t for t in targets if t["id"] not in skip]
    print(f"OCR 佇列 {len(targets)} 本，本輪最多做 {args.limit} 本")
    if not targets:
        return 0

    # 🚨 DB 空間閘。整夜跑一次會塞進十幾萬列 preview；2026-07-08 曾因超量被鎖站
    #    （1,313 MB → 救回 359 MB）。2026-09-16 量到已經回到 872 MB，
    #    370 本估計再加 81 MB。沒有這道閘，一個沒人看著的夜班就可能把站鎖掉。
    db_mb = db_size_mb()
    if args.max_db_mb:
        if db_mb is None:
            print("  ⚠ 量不到 DB 大小（Management API 不通），空間閘跳過")
        else:
            print(f"  DB 目前 {db_mb:,.0f} MB（硬上限 {args.max_db_mb:,} MB）")
            if db_mb >= args.max_db_mb:
                print("⛔ 已達硬上限，不開跑。先清空間或調高 --max-db-mb 再說。")
                return 1

    # 2026-09-16：這裡本來有一組「DB 空間不夠就先不寫 preview、記帳日後補」的閘。
    # `ebook_chunks` 整張退場之後沒有 preview 可寫，也就沒有帳要欠 —— 全文一律進
    # Drive＋R2，reader 與搜尋都讀那一份。見 database/drop-ebook-chunks-2026-09-16.sql。

    deadline = time.time() + args.max_minutes * 60 if args.max_minutes else None
    done = fail = 0
    checked_at = time.time()
    for t in targets[: args.limit]:
        if deadline and time.time() > deadline:
            print(f"  ⏱ 已達 {args.max_minutes} 分鐘上限，其餘留給下一班")
            break
        bid, title = t["id"], (t.get("title") or "")[:40]
        pdf = Path(t.get("file_path") or "")
        print(f"\n▶ {bid}  {title}", flush=True)

        if not pdf.exists():
            drive_root = Path(str(pdf.drive) + os.sep) if pdf.drive else None
            if drive_root is not None and not drive_root.exists():
                print(f"  ⛔ {pdf.drive} 掛不上 —— Drive 卡住，整場停")
                return 3
            print("  跳過：檔案不在")
            og.update_book_error(bid, "file not found (mineru)")
            fail += 1
            continue

        try:
            with tempfile.TemporaryDirectory(prefix="mineru_") as td:
                pages = run_mineru(pdf, Path(td), lang=args.lang)
        except Exception as e:
            msg = str(e)
            if looks_like_env_failure(msg):
                print(f"  ⛔ 環境問題，整場停：{msg[:140]}")
                return 3
            print(f"  ✗ 這本失敗：{msg[:140]}")
            og.update_book_error(bid, f"MinerU: {msg[:200]}")
            fail += 1
            continue

        chunks = to_chunks(pages)
        rep = quality_report(chunks)
        print(f"  {rep['pages']} 頁　空白 {rep['blank_rate']:.1%}　每頁 {rep['chars_per_page']} 字")
        if not rep["repetition_ok"]:
            # 寧可留在佇列等重跑，也不要把幻覺文字寫進館藏。
            print(f"  🚨 {rep['repetition_msg']} → 不入庫，留在佇列")
            fail += 1
            continue
        if rep["chars_per_page"] < 50:
            print("  ✗ 每頁不到 50 字，等於沒讀到 → 留在佇列")
            fail += 1
            continue

        # 交給既有的發布路徑：JSONL(繁體) → R2 → parsed_at
        pub = [{"page": c["page_number"], "text": og._trad(c["content"])} for c in chunks]
        try:
            path = og.write_jsonl(bid, pub)
            og.push_to_r2(bid, path)
            non_empty = [c for c in pub if c["text"].strip()]
            og.update_book_done(bid,
                                total_chars=sum(len(c["text"]) for c in non_empty),
                                chunk_count=len(non_empty),
                                total_pages=max(c["page"] for c in non_empty))
        except Exception as e:
            msg = str(e)
            print(f"  ✗ 發布失敗：{msg[:140]}")
            if looks_like_env_failure(msg):
                return 3
            fail += 1
            continue
        done += 1
        print("  ✓ 已入庫")

        # 每 10 分鐘複查一次空間，別等跑完才發現滿了
        if args.max_db_mb and time.time() - checked_at > 600:
            checked_at = time.time()
            size = db_size_mb()
            if size is not None:
                print(f"  （DB {size:,.0f} / {args.max_db_mb:,} MB）")
                if size >= args.max_db_mb:
                    print("⛔ 跑到一半達到空間上限，停在這裡。已完成的都已入庫，其餘留在佇列。")
                    break

    print(f"\n本輪完成 {done} 本、失敗 {fail} 本")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="環境自檢")
    c.set_defaults(func=cmd_check)

    r = sub.add_parser("run", help="OCR 一本書")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--book", help="ebooks.id")
    g.add_argument("--pdf", help="直接指定 PDF 路徑")
    r.add_argument("--out", help="搭配 --pdf 用的輸出 jsonl")
    r.add_argument("--staging", action="store_true", help="寫 .jsonl.new，不動 DB/R2")
    r.add_argument("--lang", default="ch")
    r.add_argument("--start", type=int, help="起始頁（0-based）")
    r.add_argument("--end", type=int, help="結束頁（0-based，含）")
    r.set_defaults(func=cmd_run)

    q = sub.add_parser("queue", help="吃 OCR 佇列（每日排程用）")
    q.add_argument("--limit", type=int, default=5, help="本輪最多做幾本")
    q.add_argument("--max-minutes", type=int, default=0,
                   help="時間上限，到了就把其餘留給下一班（0＝不限）")
    q.add_argument("--lang", default="ch")
    q.add_argument("--exclude", nargs="*", default=[], help="要跳過的 ebook id")
    q.add_argument("--max-db-mb", type=int, default=1100,
                   help="DB 超過這個大小就停（預設 1100 MB）。"
                        "2026-07-08 曾在 1,313 MB 被鎖站，這道閘是為了別讓沒人看著的夜班撞上去")
    q.set_defaults(func=cmd_queue)

    args = ap.parse_args()
    # check 不碰 GPU，不用排隊
    if args.cmd == "check":
        return args.func(args)
    if not acquire_lock():
        return 4
    try:
        return args.func(args)
    finally:
        release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
