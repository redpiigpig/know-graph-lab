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
import re
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


def pages_from_middle(middle: dict) -> dict[int, dict]:
    """`middle.json` → {0-based 頁索引: {text, footnotes, printed_page}}。

    正文走 `preproc_blocks`（合併前），不走 `para_blocks`／`content_list` ——
    理由見模組開頭那段，這是本檔存在的主要原因。

    🚨 **註腳與印刷頁碼不在 `preproc_blocks` 裡**，MinerU 把它們跟書眉一起
    歸到 `discarded_blocks`。只讀正文等於把兩樣硬規定要的東西靜默丟光：
    專案規矩是註釋一律要收（不然無法核對作者引了什麼），頁碼要帶得回原書
    （引用寫得出第幾頁）。2026-09-18《民主妙法》第一版就是這樣——334 頁
    零缺頁、字數正常、閘全過，而全書 300 多條譯註原註一條都不在。

    分類不必自己猜：那些 block 自帶 `type`（`header`／`page_number`／
    `page_footnote`），照標籤撿就好。認不得的型別一律當家具丟掉。
    """
    out: dict[int, dict] = {}
    for page in middle.get("pdf_info") or []:
        idx = int(page.get("page_idx", len(out)))
        blocks = page.get("preproc_blocks")
        if blocks is None:                      # 舊版格式的保險
            blocks = page.get("para_blocks") or []
        notes: list[str] = []
        printed: int | None = None
        for b in page.get("discarded_blocks") or []:
            kind = b.get("type")
            text = _block_text(b).strip()
            if not text:
                continue
            if kind == "page_footnote":
                notes.append(" ".join(text.split()))
            elif kind == "page_number" and printed is None:
                digits = re.sub(r"\D", "", text)
                if digits:
                    printed = int(digits)
        out[idx] = {
            "text": "\n".join(_block_text(b) for b in blocks).strip(),
            "footnotes": notes,
            "printed_page": printed,
        }
    return out


def find_middle_json(out_dir: Path) -> Path:
    hits = sorted(out_dir.rglob("*_middle.json"))
    if not hits:
        raise FileNotFoundError(f"MinerU 沒有產出 middle.json：{out_dir}")
    return hits[0]


# ── 跑 MinerU ─────────────────────────────────────────────────────────────

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
# 每次都會印、對查錯零幫助的開場白。留著會把訊息額度吃光。
_BANNER = ("Start MinerU FastAPI Service", "API documentation:", "Started local mineru-api",
           "Uvicorn running on", "Started server process", "Waiting for application startup",
           "Application startup complete", "Request concurrency limited")


def last_lines(*streams: str | None, n: int = 4, width: int = 220) -> str:
    """把 MinerU 的輸出濃縮成「最後幾行有意義的話」。

    進度條用 \\r 更新，所以要一起當換行切；banner 與空行丟掉；ANSI 色碼去掉。
    取尾巴而不是取頭，因為呼叫端會截短，而死因永遠在最後一行。
    """
    lines: list[str] = []
    for s in streams:
        for raw in _ANSI.sub("", s or "").replace("\r", "\n").split("\n"):
            ln = raw.strip()
            if ln and not any(b in ln for b in _BANNER):
                lines.append(ln[:width])
    return " ⏎ ".join(lines[-n:]) if lines else "（MinerU 沒留下任何訊息）"


def run_mineru(pdf: Path, out_dir: Path, lang: str = "ch",
               start: int | None = None, end: int | None = None,
               device: str | None = None) -> dict[int, str]:
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
    # MinerU 的 get_device() 先看這個環境變數，才輪到 torch.cuda.is_available()，
    # 而 ~/mineru.json 沒有 device 這個鍵，所以這一行是可靠的強制指定。
    if device:
        env["MINERU_DEVICE_MODE"] = device

    t0 = time.time()
    proc = subprocess.run(argv, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        elapsed = time.time() - t0
        # 🚨 呼叫端只留訊息的前 140–200 字，而 MinerU 開頭固定是
        #    「Start MinerU FastAPI Service / Started local mineru-api / API documentation」
        #    三行 banner —— 直接塞 stdout 的話，存進 parse_error 的永遠是那段廢話，
        #    真正的錯在最後面。2026-09-18 十本書就是這樣查不出死因。所以取**尾巴**。
        raise RuntimeError(
            f"MinerU 失敗 (exit {proc.returncode}, {elapsed:.0f}s)：{last_lines(proc.stderr, proc.stdout)}")

    middle = json.loads(find_middle_json(out_dir).read_text(encoding="utf-8"))
    pages = pages_from_middle(middle)
    print(f"  MinerU 讀完 {len(pages)} 頁，耗時 {time.time() - t0:.0f}s", flush=True)
    return pages


# ── 輸出成本專案的 JSONL ──────────────────────────────────────────────────

FOOTNOTE_RULE = "—" * 15          # reader 認這條線當「註釋」區的起點


def drop_isolated_printed_pages(pages: dict[int, dict]) -> int:
    """把孤立的假印刷頁碼清掉，回傳清掉幾個。

    🚨 撿回來的頁碼偶爾是別的東西。《民主妙法》的書名頁（沒印頁碼）就被填了 8，
    夾在一串「PDF 頁 − 7」之間，單看那一頁完全正常。假頁碼比沒有頁碼更糟，
    因為它會讓人照著寫進論文（[[feedback_transcribe_page_numbers]]）。

    判準是**跟鄰居的位移對不對得上**，不是「跟全書主流位移對不對得上」——
    前言另編、正文重新從 1 起算的書，換算位移本來就會變一次，那種換檔是一整段
    連號的，不該被當成錯。只有前後都不同意的那一個才丟。
    """
    numbered = [(idx, page) for idx, page in sorted(pages.items()) if page["printed_page"]]
    offsets = [idx - page["printed_page"] for idx, page in numbered]
    dropped = 0
    for i, (idx, page) in enumerate(numbered):
        neighbours = offsets[max(0, i - 1):i] + offsets[i + 1:i + 2]
        if neighbours and offsets[i] not in neighbours:
            page["printed_page"] = None
            dropped += 1
    return dropped


def to_chunks(pages: dict[int, dict], page_offset: int = 0) -> list[dict]:
    """`pages_from_middle` 的輸出 → 本專案的 chunk 形狀。

    `page_number` 用 1-based 實體頁（`page_offset` 給「只 OCR 後半本」那種場合補回），
    `printed_page` 另存原書印的那個頁碼 —— 兩者是不同的東西，前者是檔案裡的第幾張，
    後者才是引用時寫的頁。位移不是常數（前言用羅馬數字、插頁不編號），所以逐頁記，
    不要拿一個 offset 去推算。

    註腳接在正文後面、以一條長橫線分隔，不要跟正文混在一起。
    空白頁保留，不要悄悄丟掉——頁碼覆蓋率的稽核靠它。
    """
    bogus = drop_isolated_printed_pages(pages)
    if bogus:
        print(f"  （清掉 {bogus} 個跟前後都對不上的印刷頁碼，寧可留空）", flush=True)
    chunks = []
    for i, idx in enumerate(sorted(pages)):
        page = pages[idx]
        body = page["text"]
        if page["footnotes"]:
            body = (body + "\n\n" + FOOTNOTE_RULE + "\n" + "\n".join(page["footnotes"])).strip()
        chunks.append({
            "chunk_index": i,
            "chunk_type": "page",
            "page_number": idx + 1 + page_offset,
            "printed_page": page["printed_page"],
            "chapter_path": None,
            "format": "text",
            "content": body,
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


def acquire_lock(wait_minutes: int = 0) -> bool:
    """拿到 GPU 就回 True。持有者已經死掉的話接收這把鎖。

    `wait_minutes > 0` 會等對方讓出來再上 —— 整夜跑的場合該等，不該因為
    現在剛好有人在用就整晚什麼都不做。每日排程那種短班則維持不等（直接跳過）。
    """
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + wait_minutes * 60
    announced = False
    while True:
        old = None
        if LOCK.exists():
            try:
                old = int(LOCK.read_text(encoding="utf-8").strip().split()[0])
            except Exception:
                old = None
        if not (old and old != os.getpid() and _pid_alive(old)):
            if old:
                print(f"  （接收前一個已結束的 lock：PID {old}）")
            LOCK.write_text(f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}",
                            encoding="utf-8")
            return True
        if time.time() >= deadline:
            print(f"⛔ 另一個 MinerU 正在跑（PID {old}）"
                  f"{'，等了 %d 分鐘仍沒讓出來' % wait_minutes if wait_minutes else '，這次跳過'}"
                  f" —— GPU 只有 6GB，不能兩個一起擠")
            return False
        if not announced:
            print(f"  ⏳ GPU 被 PID {old} 佔著，最多等 {wait_minutes} 分鐘…", flush=True)
            announced = True
        time.sleep(60)


def release_lock() -> None:
    try:
        if LOCK.exists() and LOCK.read_text(encoding="utf-8").strip().split()[0] == str(os.getpid()):
            LOCK.unlink()
    except Exception:
        pass


ENV_SIGNS = ("getaddrinfo", "URLError", "ConnectionError", "Connection refused",
             "Temporary failure", "timed out", "Max retries", "SSLError",
             "Remote end closed", "Connection aborted",
             # 🚨 這台是繁中 Windows，socket 錯誤回的是**中文**訊息，
             #    上面整排英文關鍵字對它視而不見。2026-09-18 內村卷 09／11 就是這樣
             #    被判成「這一卷的問題」：`[WinError 10054] 遠端主機已強制關閉一個現存的連線。`
             #    所以改認 WinError 代碼 —— 那串不會被在地化。
             "WinError 10054",   # 連線被對方強制關閉
             "WinError 10053",   # 連線被本機軟體中止
             "WinError 10060",   # 連線逾時
             "WinError 10061",   # 拒絕連線
             "WinError 11001",   # 主機名稱解析失敗
             "WinError 10051",   # 網路無法連線
             )


# MinerU 光是起 FastAPI ＋ 載模型就要 10–15 秒，載完才輪到這本書。
# 死在這之前，它根本沒翻開書，怎麼樣都不會是「這本書的問題」。
STARTUP_SECONDS = 60
_ELAPSED = re.compile(r"exit -?\d+, (\d+)s")


def looks_like_env_failure(msg: str) -> bool:
    """這個錯是「環境壞了」還是「這本書不行」。

    分錯的代價不對稱：把環境錯當成書的失敗，會在幾秒內燒掉整個佇列
    （2026-09-16 實測 30 本）；反過來只是多停一次、下次再跑。所以寧可誤判成環境錯。

    🚨 2026-09-18 又燒掉 10 本：關鍵字表只認得網路錯，而那天是待機醒來後 GPU 不穩，
       MinerU 在載模型時就沒了、一個字都沒留，於是十本書被判「書壞了」踢出佇列
       （事後單獨重跑同一本 exit 0）。所以加第二條判準：**死得太快就是環境問題**。
    """
    low = (msg or "").lower()
    if any(s.lower() in low for s in ENV_SIGNS):
        return True
    m = _ELAPSED.search(msg or "")
    return m is not None and int(m.group(1)) < STARTUP_SECONDS


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
        # 🚨 校園 WiFi 會隨機斷。一次閃斷不該讓這一本白白算失敗 ——
        #    2026-09-18 內村卷 09／11 就是死在這一行（各只花 12s／32s，MinerU 根本沒起跑）。
        #    先重試，重試完還是不行才交給分類器判。
        rows, err = None, None
        for i in range(5):
            try:
                rows = json.loads(urllib.request.urlopen(req, timeout=30).read())
                break
            except Exception as e:
                err = e
                if i < 4:
                    print(f"  ⚠ 查 DB 失敗（{type(e).__name__}），{2 ** i}s 後重試"
                          f"（{i + 1}/4）", flush=True)
                    time.sleep(2 ** i)
        if rows is None:
            # 查不到書名 ≠ 這本書壞了。DNS／連線問題要讓呼叫端整場停下來。
            print(f"⛔ 查 DB 失敗：{str(err)[:160]}")
            return 3 if looks_like_env_failure(str(err)) else 1
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
            pages = run_mineru(pdf, Path(td), lang=args.lang, start=args.start, end=args.end,
                               device=getattr(args, "device", None))
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
    if book_id is None:
        return 0                                  # --pdf 一次性轉檔，本來就沒有要入庫

    # 🚨 寫完檔不等於入庫。這裡本來就 return 0 了，於是 `run --book` 跑完
    #    exit 0、JSONL 也在，但 R2 沒有、`parsed_at` 還是 null、`parse_error`
    #    還掛著 'no extractable text' —— 站上看不到，而且這本還留在佇列裡等
    #    明天的排程再 OCR 一次。2026-09-18《民主妙法》與內村數卷都是這樣。
    #    發布一律走 queue 用的同一組函式，不要在這裡另寫一套。
    sys.path.insert(0, str(REPO / "scripts"))
    import ocr_with_gemini as og
    pub = [{"page": c["page_number"], "printed_page": c.get("printed_page"),
            "text": c["content"]} for c in chunks]
    try:
        path = og.write_jsonl(book_id, pub)       # 內含簡→繁，形狀與 queue 一致
        og.push_to_r2(book_id, path)
        non_empty = [c for c in pub if c["text"].strip()]
        og.update_book_done(book_id,
                            total_chars=sum(len(c["text"]) for c in non_empty),
                            chunk_count=len(non_empty),
                            total_pages=max(c["page"] for c in non_empty))
    except Exception as e:
        msg = str(e)
        print(f"  ✗ 發布失敗（JSONL 已寫出，重跑即可）：{msg[:200]}")
        return 3 if looks_like_env_failure(msg) else 1
    print("  ✓ 已入庫（R2 已推送，parsed_at 已寫）")
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
    # 🚨 2026-09-23：純圖片 epub 也會掛 'no extractable text' 進同一個佇列，MinerU 對它回
    #    「No supported documents」、13 秒就死 → 被判環境錯整場停，而且它照大小排在第 0 位，
    #    每一輪都卡在它。MinerU 只吃 PDF，其餘留給 ocr_with_gemini。
    non_pdf = [t for t in targets if not (t.get("file_path") or "").lower().endswith(".pdf")]
    if non_pdf:
        print(f"  略過非 PDF {len(non_pdf)} 本（MinerU 不吃，留給 Gemini）："
              + "、".join(t["title"][:24] for t in non_pdf[:3]))
        targets = [t for t in targets if t not in non_pdf]
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
    streak: list[str] = []   # 連續失敗的書；成功一本就清掉
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
                print(f"  ⛔ 環境問題，整場停：{msg[:200]}")
                return 3
            print(f"  ✗ 這本失敗：{msg[:200]}")
            og.update_book_error(bid, f"MinerU: {msg[:200]}")
            fail += 1
            streak.append(bid)
            # 🚨 認不出來的環境錯照樣會燒佇列 —— 關鍵字表漏過 2026-09-16 那次斷網
            #    以外的每一種死法。所以不管看不看得懂訊息，連錯這麼多本就是環境有事：
            #    好書不會排隊壞。把這一串放回佇列再整場停，等人來看。
            if len(streak) >= args.max_streak:
                print(f"\n⛔ 連續 {len(streak)} 本失敗 —— 這不是書的問題，整場停。")
                for sid in streak:
                    og.update_book_error(sid, "no extractable text")
                print(f"   已把這 {len(streak)} 本放回佇列：{', '.join(s[:8] for s in streak)}")
                return 3
            continue

        streak.clear()   # MinerU 跑得動 → 前面那些失敗確實是各自的書的問題
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
        pub = [{"page": c["page_number"], "printed_page": c.get("printed_page"),
                "text": og._trad(c["content"])} for c in chunks]
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
    r.add_argument("--device", choices=["cpu", "cuda"],
                   help="強制指定運算裝置。--device cpu 不碰 GPU，因此**不排 GPU 鎖**，"
                        "可以在別人的夜班佇列跑著的時候插隊做幾頁的小活")
    r.add_argument("--wait-gpu-minutes", type=int, default=0,
                   help="GPU 被別的 MinerU 佔著時最多等幾分鐘（預設 0＝不等，直接回 4）。"
                        "單本插班在夜間佇列後面時要給，不然只會立刻回 4")
    r.set_defaults(func=cmd_run)

    q = sub.add_parser("queue", help="吃 OCR 佇列（每日排程用）")
    q.add_argument("--limit", type=int, default=5, help="本輪最多做幾本")
    q.add_argument("--max-minutes", type=int, default=0,
                   help="時間上限，到了就把其餘留給下一班（0＝不限）")
    q.add_argument("--lang", default="ch")
    q.add_argument("--wait-gpu-minutes", type=int, default=0,
                   help="GPU 被別的 MinerU 佔著時最多等幾分鐘（預設 0＝不等，直接回 4）。"
                        "整夜跑該給大一點，別因為現在剛好有人在用就整晚什麼都不做")
    q.add_argument("--exclude", nargs="*", default=[], help="要跳過的 ebook id")
    q.add_argument("--max-streak", type=int, default=3,
                   help="連續幾本失敗就判定環境有問題、把那幾本放回佇列並整場停（預設 3）")
    q.add_argument("--max-db-mb", type=int, default=1100,
                   help="DB 超過這個大小就停（預設 1100 MB）。"
                        "2026-07-08 曾在 1,313 MB 被鎖站，這道閘是為了別讓沒人看著的夜班撞上去")
    q.set_defaults(func=cmd_queue)

    args = ap.parse_args()
    # check 不碰 GPU，不用排隊
    if args.cmd == "check":
        return args.func(args)

    # 🚨 這台是 S0 Modern Standby 筆電：一進待機，掛在主控台的行程會同時收到
    #    STATUS_CONTROL_C_EXIT（0xC000013A）—— 2026-09-08 稽核 30 小時的排程事件
    #    抓到 40 次這種死法。而 `powercfg /requests` 顯示沒有任何行程在阻止睡眠，
    #    管線跑再久 Windows 都認為機器閒著。一本幾百頁的書要跑十幾分鐘，
    #    整夜作業更是幾十小時，沒有這一格闔上蓋子就全沒了。
    try:
        from keep_awake import keep_awake
        keep_awake()
    except Exception:
        pass
    # 鎖是為了那張 6GB 的卡：兩個一起擠會 OOM。跑 CPU 的不佔顯存，不必排隊，
    # 也不該把鎖從別人手上接過來。
    if getattr(args, "device", None) == "cpu":
        print("  （--device cpu：不佔 GPU，略過 GPU 鎖）", flush=True)
    elif not acquire_lock(getattr(args, "wait_gpu_minutes", 0)):
        return 4
    try:
        return args.func(args)
    finally:
        release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
