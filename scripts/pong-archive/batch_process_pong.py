#!/usr/bin/env python3
"""
batch_process_pong.py — for each ⏳ entry in the year file:
  1. prepare (Whisper)
  2. auto_clean
  3. commit
  4. patch metadata
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).parent
TMP = ROOT / "tmp_sermon"

sys.path.insert(0, str(SCRIPTS))
from sermon_2024_metadata import METADATA


def run(cmd):
    print(f"  $ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def process_date(year_txt, date):
    print(f"\n=== {date} ===", flush=True)
    raw_file = TMP / f"{date}_raw.txt"
    clean_file = TMP / f"{date}_clean.txt"

    # 1. prepare (skip if raw already exists)
    if not raw_file.exists() or raw_file.stat().st_size < 1000:
        r = run(["python", str(SCRIPTS / "sermon_redo.py"), "prepare",
                 year_txt, "--date", date])
        # Even on cosmetic exit-127, raw should be written
        if not raw_file.exists():
            print(f"  [error] prepare failed, no raw file. stderr:\n{r.stderr[-500:]}", flush=True)
            return False
    else:
        print(f"  raw exists: {raw_file.stat().st_size} bytes", flush=True)

    # 2. auto_clean
    r = run(["python", "-X", "utf8", str(SCRIPTS / "auto_clean.py"), date])
    if r.returncode != 0 or not clean_file.exists():
        print(f"  [error] auto_clean failed: {r.stderr}", flush=True)
        return False
    print(f"  auto_clean ok: {clean_file.stat().st_size} bytes", flush=True)

    # 3. commit
    r = run(["python", str(SCRIPTS / "sermon_redo.py"), "commit",
             year_txt, "--date", date, "--clean-file", str(clean_file)])
    if r.returncode != 0:
        print(f"  [error] commit failed: {r.stderr}", flush=True)
        return False
    print(f"  commit ok", flush=True)

    # 4. patch metadata
    if date in METADATA:
        r = run(["python", "-X", "utf8", str(SCRIPTS / "patch_sermon_metadata.py"), date])
        if r.returncode != 0:
            print(f"  [warn] metadata patch failed: {r.stderr}", flush=True)
        else:
            print(f"  metadata patched", flush=True)
    return True


def main():
    year_txt = sys.argv[1]
    dates = sys.argv[2:] if len(sys.argv) > 2 else None

    if dates is None:
        # Read pending entries from queue
        from sermon_redo import parse_queue
        entries = parse_queue(Path(year_txt))
        dates = [e.date for e in entries if e.status == "pending"]

    print(f"processing {len(dates)} dates: {dates}", flush=True)

    succeeded = []
    failed = []
    for d in dates:
        try:
            ok = process_date(year_txt, d)
            (succeeded if ok else failed).append(d)
        except Exception as e:
            print(f"  [error] {e}", flush=True)
            failed.append(d)

    print(f"\n##### DONE #####", flush=True)
    print(f"succeeded ({len(succeeded)}): {succeeded}", flush=True)
    print(f"failed ({len(failed)}): {failed}", flush=True)


if __name__ == "__main__":
    main()
