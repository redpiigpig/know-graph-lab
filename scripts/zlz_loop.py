#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""天主教在線：可續跑的序列下載＋分批 ingest（背景用，無並發）。

  python -X utf8 scripts/zlz_loop.py [--chunk 40]

每輪：挑 chunk 個帳本沒有的條目 → zlz_fetch（8 秒間隔）→ zlz_ingest --run。
失敗的條目本次執行不再重試（記在 c:/tmp/zlz_failed.json）；連續 3 輪零成功即停。
續跑＝再執行同一指令（靠帳本）。進度看 c:/tmp/zlz_loop.log 與帳本筆數。
"""
import argparse, json, subprocess, sys
from pathlib import Path

H = Path(__file__).parent
CAT = Path("c:/tmp/zlz_catalog.json"); LED = Path("c:/tmp/zlz_downloaded.json")
FAIL = Path("c:/tmp/zlz_failed.json"); TODO = Path("c:/tmp/zlz_chunk.json")


def led():
    return json.loads(LED.read_text(encoding="utf-8")) if LED.exists() else {}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--chunk", type=int, default=40)
    a = ap.parse_args()
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    failed = set(json.loads(FAIL.read_text(encoding="utf-8"))) if FAIL.exists() else set()
    dead = 0
    while True:
        done = led()
        todo = [i for i in cat if i["url"] not in done and i["url"] not in failed][:a.chunk]
        print(f"帳本 {len(done)}／{len(cat)}，失敗 {len(failed)}，本輪 {len(todo)}", flush=True)
        if not todo:
            break
        TODO.write_text(json.dumps(todo, ensure_ascii=False), encoding="utf-8")
        subprocess.run([sys.executable, "-X", "utf8", str(H / "zlz_fetch.py"), "--list", str(TODO)])
        after = led()
        got = sum(1 for i in todo if i["url"] in after)
        failed |= {i["url"] for i in todo if i["url"] not in after}
        FAIL.write_text(json.dumps(sorted(failed)), encoding="utf-8")
        subprocess.run([sys.executable, "-X", "utf8", str(H / "zlz_ingest.py"), "--run"])
        dead = dead + 1 if got == 0 else 0
        if dead >= 3:
            print("連續 3 輪零成功，停。", flush=True)
            return 1
    print("全部處理完畢", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
