#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整夜 OCR 看守：等服務可用才跑，沒進度就停，不空轉。

  python scripts/ocr_overnight.py [--rounds 24] [--limit 12] [--idle-stop 2]

2026-08-28 那次教訓：用 shell 迴圈 `... | tail -25` 跑了 22 小時，只推進一本
書的 160 頁。兩個問題都在這支修掉：

  ① tail 會緩衝全部輸出到進程結束 → log 一直是空的，22 小時看不出卡住。
     這裡每輪直接寫檔並 flush。
  ② Gemini 全程 503、全部落到速率受限的 Haiku，卻沒有任何機制察覺。
     這裡開跑前先探活；連續 N 輪零進度就停下來報告，不再空轉。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
LOG = Path("c:/tmp/ocr_overnight.log")

_PROBE = (
    "import sys\n"
    "from google import genai\n"
    "genai.Client(api_key=sys.argv[1]).models.generate_content("
    "model='gemini-flash-latest', contents='ping')\n"
    "print('OK')\n"
)


def say(msg: str) -> None:
    line = f"[{datetime.now():%m-%d %H:%M}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def gemini_keys() -> list[str]:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ROOT / ".env")
    vals = [v for k, v in sorted(os.environ.items())
            if k.upper().startswith("GEMINI") and v]
    return [p.strip() for v in vals for p in v.split(",") if p.strip()]


def gemini_alive(keys: list[str]) -> int:
    """回可用的 key 數。每把 key 開獨立子進程——SDK 的 client 會互相污染，
    同一進程內連測多把會冒出 'client has been closed' 這種假錯誤。"""
    n = 0
    for k in keys:
        try:
            r = subprocess.run([sys.executable, "-c", _PROBE, k],
                               capture_output=True, text=True, timeout=90)
            if r.stdout.strip() == "OK":
                n += 1
        except Exception:
            pass
    return n


def unparsed() -> int:
    import requests
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ROOT / ".env")
    u, k = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.get(f"{u}/rest/v1/ebooks",
                     headers={"apikey": k, "Authorization": f"Bearer {k}",
                              "Prefer": "count=exact", "Range": "0-0"},
                     params={"parsed_at": "is.null", "select": "id"}, timeout=30)
    return int(r.headers.get("content-range", "/0").split("/")[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=24)
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--idle-stop", type=int, default=2,
                    help="連續幾輪零進度就停")
    ap.add_argument("--wait", type=int, default=900, help="服務不通時的等待秒數")
    a = ap.parse_args()

    keys = gemini_keys()
    say(f"開跑：{len(keys)} 把 Gemini key，未解析 {unparsed()} 本")

    idle = 0
    for rd in range(1, a.rounds + 1):
        alive = gemini_alive(keys)
        if alive == 0:
            say(f"第 {rd} 輪：Gemini 全數不可用，等 {a.wait // 60} 分鐘再探"
                f"（不硬推——全落 Haiku 只會拖垮共用帳號的速率）")
            time.sleep(a.wait)
            continue

        before = unparsed()
        say(f"第 {rd} 輪：Gemini 可用 {alive}/{len(keys)}，未解析 {before}")
        env = {**os.environ, "GEMINI_PAGES_PER_CALL": "60",
               "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        with LOG.open("a", encoding="utf-8") as f:
            subprocess.run(
                [sys.executable, "-u", "scripts/ocr_with_gemini.py", "run",
                 "--limit", str(a.limit), "--rpm", "3"],
                cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=7200)

        after = unparsed()
        done = before - after
        say(f"第 {rd} 輪結束：完成 {done} 本，剩 {after}")
        idle = idle + 1 if done <= 0 else 0
        if idle >= a.idle_stop:
            say(f"連續 {idle} 輪零進度 → 停止。不空轉，等外部服務恢復再手動重啟。")
            return 0
        time.sleep(300)

    say("跑完預定輪數。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
