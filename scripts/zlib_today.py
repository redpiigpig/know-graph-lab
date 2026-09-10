#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""印出今天（本地時間）從 z-library 下載成功幾本。

zlib_daily.ps1 拿這個數字決定「還要不要換下一個帳號繼續抓」——目標是每天四十本，
四個帳號各十本，但每個帳號當天可能已經被別輪用掉一部分額度，所以不能只數帳號數。

  python scripts/zlib_today.py          # 只印數字，給排程讀
  python scripts/zlib_today.py --break  # 連同各狀態一起印，給人看
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "scripts" / "state" / "zlib_ledger.jsonl"


def today_counts() -> Counter:
    """帳本的 at 是 UTC ISO 字串，本地是 UTC+8——早上八點前跑的那幾輪，UTC 日期
    還停在昨天。直接切前十個字元會把清晨那幾本算到前一天去，所以要真的換算。"""
    today = datetime.now().astimezone().date()
    out: Counter = Counter()
    if not LEDGER.exists():
        return out
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        at = r.get("at")
        if not at:
            continue
        try:
            ts = datetime.fromisoformat(at.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts.astimezone().date() == today:
            out[r.get("status", "?")] += 1
    return out


if __name__ == "__main__":
    c = today_counts()
    if "--break" in sys.argv:
        print(f"今天下載 {c['downloaded']} 本")
        for k, v in c.most_common():
            print(f"  {k:18} {v}")
    else:
        print(c["downloaded"])
