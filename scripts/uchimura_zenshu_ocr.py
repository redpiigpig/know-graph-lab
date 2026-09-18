# -*- coding: utf-8 -*-
"""《内村鑑三全集》20 卷專屬 OCR 跑法（本機 MinerU）。

為什麼不直接丟共用佇列：共用佇列排了一百多本，而且照檔案大小小的先做，
這 20 卷每卷 800–1400 頁會一路被插隊。這支照卷序自己走完。

設計前提（都是踩過的）：
  * 可續跑——每卷跑完就寫進 ledger，筆電睡著／排程被砍掉，下一班從沒做完的那卷接。
  * 離開碼 3（環境壞了：斷網、Supabase 不通、MinerU 自己掛）→ **整場停**，
    不可以繼續往下把每一卷都標成壞掉。
  * 離開碼 4（另一個 MinerU 佔著 GPU）→ 這班什麼都不做，安靜退出等下一班。
  * `--max-minutes` 到了就收工，不會硬跑到天亮。

    python scripts/uchimura_zenshu_ocr.py --max-minutes 240
    python scripts/uchimura_zenshu_ocr.py --status
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# 主控台是 cp950，印到 ▶／✓ 就會 UnicodeEncodeError 整支掛掉（排程會變成每晚靜默失敗）。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = Path(__file__).resolve().parent.parent
load_dotenv(REPO / ".env")
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

PY = r"C:\Users\user\AppData\Local\Python\bin\python.exe"   # 裸 python 會中 _whisper_venv
LEDGER = REPO / "scripts" / "state" / "uchimura_zenshu_ocr.jsonl"
VOLS = range(1, 21)


def ebook_id(vol: int) -> str:
    return f"d0000001-0000-4000-8000-{vol:012d}"


# 半截的 JSONL 也會「存在」。856 頁的卷只寫出個位數行，就是寫到一半死了。
MIN_LINES = 50


def jsonl_path(vol: int) -> Path:
    return Path(os.environ["EBOOK_CHUNKS_DIR"]) / f"{ebook_id(vol)}.jsonl"


def transcribed(vol: int) -> int:
    """這一卷轉錄好了沒 —— 回傳行數，0 代表沒有。

    🚨 判準是 Drive 上那份 JSONL，**不是 `ebooks.chunk_count`**。
    `mineru_ocr.py run --book` 只寫 JSONL、不碰 DB（全集不混進圖書館），
    而 `seisho_kenkyu_index.py --source mineru` 讀的也正是這份 —— 它就是成品。
    拿 chunk_count 當判準的話，20 卷全轉完了也永遠顯示「待轉錄 20 卷」，
    排程那支 `uchimura_zenshu_done.py` 也永遠不會把自己關掉（會無限空轉）。

    🚨 不能只看檔案在不在：空檔、寫到一半的檔都會存在，所以數行數。
    G: 沒掛的時候一律回 0＝還沒完，往「不要誤判成完成」那邊倒。
    """
    try:
        p = jsonl_path(vol)
        if not p.exists():
            return 0
        with p.open(encoding="utf-8") as fh:
            n = sum(1 for ln in fh if ln.strip())
        return n if n >= MIN_LINES else 0
    except OSError:
        return 0


def ledger_done() -> set[int]:
    if not LEDGER.exists():
        return set()
    out = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("ok"):
            out.add(int(r["vol"]))
    return out


def note(vol: int, ok: bool, code: int, secs: float, msg: str = "") -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"vol": vol, "ok": ok, "exit": code, "secs": round(secs),
                             "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "msg": msg},
                            ensure_ascii=False) + "\n")


def db_get(url: str, tries: int = 6, timeout: int = 30):
    """🚨 一次 DNS 閃斷不該弄死整班四小時的轉錄。

    2026-09-18 實測：卷 01 轉完（856 頁、9 分）之後，查卷 02 的那一個 requests.get
    撞到 `getaddrinfo failed`（校園 WiFi），整支腳本 traceback 收工——20 卷只做了 1 卷。
    每晚排程照跑的話，等於 20 個晚上才轉得完。退避重試共約 63 秒，撐得過一般閃斷；
    真的斷很久才會拋出去，那時候停下來是對的。
    """
    for i in range(tries):
        try:
            return requests.get(url, headers=H, timeout=timeout)
        except requests.RequestException as e:
            if i == tries - 1:
                raise
            wait = 2 ** i
            print(f"  ⚠ 連 Supabase 失敗（{type(e).__name__}），{wait}s 後重試"
                  f"（{i + 1}/{tries - 1}）", flush=True)
            time.sleep(wait)


def db_state(vol: int) -> dict:
    r = db_get(f"{URL}/rest/v1/ebooks?select=id,title,chunk_count,parsed_at,parse_error"
               f"&id=eq.{ebook_id(vol)}")
    rows = r.json() if r.ok else []
    return rows[0] if rows else {}


def cmd_status() -> int:
    done = ledger_done()
    pend = 0
    for v in VOLS:
        s = db_state(v)
        if not s:
            print(f"  卷{v:02d} 尚未登記（PDF 還沒下載完或沒跑 register）")
            pend += 1
            continue
        lines = transcribed(v)
        if lines:
            mark = "✓ 已轉錄"
        elif v in done:
            # ledger 說做過，成品卻不在 —— 這種不一致要看見，不要靜靜當成完成。
            mark = "⚠ 帳不符"
        else:
            mark = "… 待轉錄"
        pend += 0 if lines else 1
        print(f"  卷{v:02d} {mark:8} {lines:>5} 段  {s.get('title', '')[:34]}")
    print(f"待轉錄 {pend} 卷（判準＝Drive 上的 JSONL 段數，不是 ebooks.chunk_count）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-minutes", type=int, default=240)
    ap.add_argument("--status", action="store_true")
    # 🚨 這顆 GPU 是跟通用佇列、別的 session 的單本插班共用的。沒有這個旗標，
    #    只要開跑那一刻剛好有人在用就回 exit 4、整班收工 —— 夜班排程等於整晚空轉，
    #    而且 log 只有一行「這班不做了」，看起來像跑過了。預設等，不要直接放棄。
    ap.add_argument("--wait-gpu-minutes", type=int, default=90,
                    help="GPU 被別的 MinerU 佔著時最多等幾分鐘（預設 90；0＝不等）")
    args = ap.parse_args()
    if args.status:
        return cmd_status()

    deadline = time.time() + args.max_minutes * 60
    done = ledger_done()
    worked = 0
    for vol in VOLS:
        if time.time() > deadline:
            print("⏸ 時間到，收工（下一班接著跑）", flush=True)
            break
        if vol in done:
            continue
        s = db_state(vol)
        if not s:
            print(f"  卷{vol:02d} 還沒登記，跳過", flush=True)
            continue
        # 成品在就別重轉（ledger 掉了也不用重做一次十分鐘）。判準同 transcribed()：
        # 看 Drive 上的 JSONL，不是 ebooks.chunk_count —— 這條線從不寫 DB，
        # 拿 chunk_count 判的話這一關永遠不會成立。
        if (n := transcribed(vol)):
            note(vol, True, 0, 0, f"成品已在（{n} 段），視為完成")
            continue
        print(f"▶ 卷{vol:02d} 開始：{s.get('title','')[:40]}", flush=True)
        t0 = time.time()
        p = subprocess.run([PY, str(REPO / "scripts" / "mineru_ocr.py"), "run",
                            "--book", ebook_id(vol),
                            "--wait-gpu-minutes", str(args.wait_gpu_minutes)], cwd=REPO)
        secs = time.time() - t0
        code = p.returncode
        if code == 0:
            note(vol, True, 0, secs)
            worked += 1
            print(f"  ✓ 卷{vol:02d} 完成，{secs/60:.1f} 分", flush=True)
        elif code == 4:
            print("  ⏸ GPU 被另一個 MinerU 佔著，這班不做了", flush=True)
            return 0
        elif code == 3:
            note(vol, False, 3, secs, "環境問題，整場停")
            print("  ⛔ 環境問題（網路／Supabase／MinerU），整場停——不把後面的卷標成壞掉", flush=True)
            return 3
        else:
            note(vol, False, code, secs, "這一卷的問題")
            print(f"  ✗ 卷{vol:02d} 離開碼 {code}，跳過這卷繼續", flush=True)
    print(f"這一班轉錄了 {worked} 卷", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
