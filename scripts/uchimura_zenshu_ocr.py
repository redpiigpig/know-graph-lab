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


def db_state(vol: int) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?select=id,title,chunk_count,parsed_at,parse_error"
                     f"&id=eq.{ebook_id(vol)}", headers=H, timeout=30)
    rows = r.json() if r.ok else []
    return rows[0] if rows else {}


def cmd_status() -> int:
    done = ledger_done()
    pend = 0
    for v in VOLS:
        s = db_state(v)
        if not s:
            print(f"  卷{v:02d} 尚未登記（PDF 還沒下載完或沒跑 register）")
            continue
        chunks = s.get("chunk_count")
        mark = "✓ 已轉錄" if (chunks or 0) > 0 else ("… 待轉錄" if v not in done else "✓ ledger")
        pend += 0 if (chunks or 0) > 0 else 1
        print(f"  卷{v:02d} {mark:8} chunks={str(chunks):>5}  {s.get('title','')[:34]}")
    print(f"待轉錄 {pend} 卷")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-minutes", type=int, default=240)
    ap.add_argument("--status", action="store_true")
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
        if (s.get("chunk_count") or 0) > 0:
            note(vol, True, 0, 0, "DB 已有 chunks，視為完成")
            continue
        print(f"▶ 卷{vol:02d} 開始：{s.get('title','')[:40]}", flush=True)
        t0 = time.time()
        p = subprocess.run([PY, str(REPO / "scripts" / "mineru_ocr.py"), "run",
                            "--book", ebook_id(vol)], cwd=REPO)
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
