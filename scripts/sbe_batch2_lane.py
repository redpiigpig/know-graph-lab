#!/usr/bin/env python3
"""東方聖書第二批的 fleet-keeper lane：跑自己那一片，完工才印 ASCII 標記。

為什麼要這層包裝，而不是讓 keeper 直接跑 sbe_translate：

1. **`sbe done` 不等於翻完。** `mueller_auto.is_done()` 把失敗 MAX_FAIL 次的段落
   算成「已耗盡」＝完成，引擎壞一段時間就會整本被判死。拿它當 keeper 的完工標記
   會讓 lane 在沒翻完的情況下自我退場。這裡改用 `sbe_progress.scan()` 的實數：
   六卷合計 left==0 且 dead==0 才算數。
2. **空 pass 不是免費的。** lane 做完後若還被每 30 分鐘重拉，一趟空 pass 仍會走到
   `ingest_work()` 結尾那個無條件的 `assemble_and_upload()`，等於定期白傳整卷。
   所以一定要有可信的退場標記（見 [[feedback_disable_finished_schedules]]）。

完工時由搶到鎖的那一片補跑逐卷彙整（lane 帶 --no-upload，尾巴不會自己上去）。
稽核與驗收**不在這裡跑**——那兩步要人看輸出才算數，埋在背景日誌裡等於沒跑。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

MARKER = "SBE_BATCH2_COMPLETE"
SLUGS = ["sbe-25-laws-of-manu", "sbe-08-bhagavadgita", "sbe-09-quran-2",
         "sbe-15-upanishads-2", "sbe-21-lotus-sutra", "sbe-39-taoism-1"]


def strict_remaining() -> tuple[int, int]:
    """回傳 (left, dead)——sbe_progress 的實數，不是 is_done() 的判斷。"""
    import sbe_progress as sp
    left = dead = 0
    for slug in SLUGS:
        total, done, blank, d, _secs = sp.scan(slug)
        left += total - done - blank - d
        dead += d
    return left, dead


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", required=True, help="i/n")
    args = ap.parse_args()

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    # 收尾期間的暫時鬆綁（預設 6 秒是帳號風險的取捨，不要改預設值）。
    env.setdefault("KGL_NVIDIA_MIN_INTERVAL", "2")

    cmd = [sys.executable, "-X", "utf8", str(HERE / "sbe_translate.py"),
           "--loop", "--backend", "nvidia", "--no-upload",
           "--reupload-every", "60",
           "--only", ",".join(SLUGS), "--shard", args.shard]
    subprocess.run(cmd, cwd=str(HERE.parent), env=env)

    left, dead = strict_remaining()
    print(f"[lane {args.shard}] strict left={left} dead={dead}", flush=True)
    if left or dead:
        return 0  # 還沒完：keeper 的 30 分鐘節奏就是重試機制

    # 真完工。搶到鎖的那一片補跑逐卷彙整（原子建檔，不會兩片同時跑）。
    lock = HERE / "state" / "sbe_batch2_assembled.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(lock, "x", encoding="ascii") as fh:
            fh.write(args.shard)
        print(f"[lane {args.shard}] 取得彙整鎖，跑 sbe_assemble_upload", flush=True)
        subprocess.run([sys.executable, "-X", "utf8",
                        str(HERE / "sbe_assemble_upload.py")],
                       cwd=str(HERE.parent), env=env)
    except FileExistsError:
        print(f"[lane {args.shard}] 彙整已由別片處理", flush=True)

    print(MARKER, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
