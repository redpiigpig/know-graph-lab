#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""榮格全集佇列：依宗教學優先序把 19 卷 CW 逐一 jung_cw_translate（--vol，resume）。
已完成的（全快取）快速跳過；未跑過的翻整卷。某卷因額度乾退出即停整批
（交由 fleet_keeper 重探後續傳）。引擎預設 nvidia（把 Gemini 留給 ACCS OCR）。
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 宗教學優先序：9ii/11/12 已完成放前面（resume 秒過）→ 9i/14/13 宗教密度高 → 其餘
# 跳過 3/4/6：已有 standalone 完整譯本（dementia-praecox=CW3 / theory-psychoanalysis=CW4
# / psychological-types-1923=CW6），不重譯省 token（user 拍板 2026-07-22）。
VOLS = ["9ii", "11", "12", "9i", "14", "13", "5", "8", "10", "7",
        "1", "2", "15", "16", "17", "18"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="nvidia", choices=["nvidia", "auto", "haiku"])
    args = ap.parse_args()
    for vol in VOLS:
        print(f"\n=== jung_cw_translate --vol {vol} ===", flush=True)
        rc = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "jung_cw_translate.py"),
             "--vol", vol, "--engine", args.engine]).returncode
        if rc != 0:
            print(f"  [bail] CW{vol} 退出碼 {rc}（多半額度乾）→ 停整批續傳", flush=True)
            return 1
    print("\n榮格全 19 卷 CW 佇列完成", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
