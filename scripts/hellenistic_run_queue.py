#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""希臘化與新柏拉圖哲學佇列：普羅提諾九章集六集＋波菲利《生平》＋伊比鳩魯五篇＋
愛比克泰德三種，逐部 build（希／英／繁中三欄）並上傳。

這 15 部在 hub 上早就有卡片，但 `ebooks` 的 chunk_count 全是 0——三支 builder
（plotinus/epicurus/epictetus_build.py）寫好之後只跑過首篇的 smoke test，沒有任何
lane 掛著它們，所以卡片點進去是空的。本檔就是那條缺掉的 lane。

額度政策比照 plato_run_queue：**兩次連續失敗才退**。單部失敗先跳過換下一部，連續
兩部都掛才視為 provider 整體乾掉，停整批交給 fleet_keeper 下一輪重探。

  python scripts/hellenistic_run_queue.py --engine haiku
  python scripts/hellenistic_run_queue.py --engine haiku --no-upload
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (builder, work)：先小後大——短篇當日見效，九章集六集排後面。
QUEUE = [
    ("epicurus_build.py", "menoeceus"),
    ("epicurus_build.py", "principal-doctrines"),
    ("epicurus_build.py", "vatican-sayings"),
    ("epicurus_build.py", "herodotus"),
    ("epicurus_build.py", "pythocles"),
    ("epictetus_build.py", "handbook"),
    ("epictetus_build.py", "fragments"),
    ("epictetus_build.py", "discourses"),
    ("plotinus_build.py", "life"),
    ("plotinus_build.py", "ennead-1"),
    ("plotinus_build.py", "ennead-2"),
    ("plotinus_build.py", "ennead-3"),
    ("plotinus_build.py", "ennead-4"),
    ("plotinus_build.py", "ennead-5"),
    ("plotinus_build.py", "ennead-6"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="haiku",
                    help="haiku（預設；Gemini 留給 ACCS、NVIDIA 常 503）")
    ap.add_argument("--no-upload", action="store_true")
    args = ap.parse_args()

    consecutive_fails = 0
    skipped: list[str] = []
    for script, work in QUEUE:
        print(f"\n=== {script} {work} ===", flush=True)
        cmd = [sys.executable, "-X", "utf8", str(ROOT / script), work,
               "--engine", args.engine]
        if not args.no_upload:
            cmd.append("--upload")
        if subprocess.run(cmd).returncode == 0:
            consecutive_fails = 0
            continue
        skipped.append(work)
        consecutive_fails += 1
        if consecutive_fails >= 2:
            print(f"\n連兩部失敗（{', '.join(skipped[-2:])}）→ 停整批，等 keeper 重探",
                  flush=True)
            return 1
    if skipped:
        print(f"\n佇列跑完，跳過：{', '.join(skipped)}", flush=True)
        return 1
    print("\n希臘化哲學佇列全數完成", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
