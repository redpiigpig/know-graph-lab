#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""哲學全集佇列：依序把 26 部柏拉圖/亞里斯多德作品逐一 plato_build（--resume）。
已完成的（全快取）會快速 assemble+upload；未跑過的自動抓 Perseus 源翻譯。

額度政策＝**兩次連續失敗才退**（使用者定調）：單部退出非 0 先跳過換下一部，連續兩部都
失敗才視為 provider 整體乾掉、停整批交給 fleet_keeper 重探。2026-08-17 前是「一部失敗就
停整批」，結果 eudemian-ethics 對不到 page 單位之後，排在它後面的 metaphysics／politics／
poetics／rhetoric 等於永遠排不到（佇列長期停在 23/26）。
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
    ap.add_argument("--no-upload", action="store_true")
    args = ap.parse_args()
    consecutive_fails = 0
    skipped: list[str] = []
    for slug in WORKS:
        print(f"\n=== plato_build {slug} ===", flush=True)
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "plato_build.py"),
               slug, "--engine", args.engine]
        if not args.no_upload:
            cmd.append("--upload")
        rc = subprocess.run(cmd).returncode
        if rc == 0:
            consecutive_fails = 0
            continue
        consecutive_fails += 1
        skipped.append(slug)
        if consecutive_fails >= 2:
            print(f"  [bail] {slug} 退出碼 {rc}；連續 2 部失敗＝provider 整體乾掉 → 停整批"
                  f"續傳（本批已跳過：{', '.join(skipped)}）", flush=True)
            return 1
        print(f"  [skip] {slug} 退出碼 {rc}（額度乾或來源對不齊）→ 換下一部，"
              f"本部 checkpoint 保留待續傳", flush=True)
    if skipped:
        print(f"\n哲學全集佇列跑完，跳過 {len(skipped)} 部待處理：{', '.join(skipped)}", flush=True)
        return 0
    print("\n哲學全集佇列全數完成", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
