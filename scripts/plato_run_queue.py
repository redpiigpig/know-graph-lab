#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""哲學全集佇列：依序把 26 部柏拉圖/亞里斯多德作品逐一 plato_build（--resume）。
已完成的（全快取）會快速 assemble+upload；未跑過的自動抓 Perseus 源翻譯。
某部因額度乾退出即停整批（交由 fleet_keeper 重探後續傳）。
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 依 plato_build --list 的正典順序
WORKS = [
    "apology", "euthyphro", "crito", "phaedo", "cratylus", "theaetetus",
    "sophist", "statesman", "parmenides-d", "philebus", "symposium", "phaedrus",
    "protagoras-d", "gorgias-d", "meno", "republic", "timaeus", "critias",
    "laws", "letters",
    "nicomachean-ethics", "eudemian-ethics", "metaphysics", "politics",
    "poetics", "rhetoric",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="auto")
    args = ap.parse_args()
    for slug in WORKS:
        print(f"\n=== plato_build {slug} ===", flush=True)
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "plato_build.py"),
               slug, "--engine", args.engine, "--upload"]
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            print(f"  [bail] {slug} 退出碼 {rc}（多半額度乾或無來源）→ 停整批續傳", flush=True)
            return 1
    print("\n哲學全集佇列全數完成", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
