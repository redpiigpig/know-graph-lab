#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從獵書清單抽一份隨機樣本，交 zlib_fetch.mjs --dry-run 探勘。

為什麼要有這支：獵表那 1,190 筆是 2026-07-23 從各全集作家的**著作目錄**反推出來
的（「這位作家寫過而我們還沒收」），從來沒跟 z-library 對過。清單上的數字因此是
「想要幾本」不是「找得到幾本」，而這兩者差很多——帳本裡 bib-* 那批試了 148 筆
只下到 35 本，68% 回「沒有對得上的版本」。

探勘只搜不下載，不花下載額度，只花時間。命中的記成 dry（不算已處理，正式跑
還會抓）；沒命中的記成 not-found／no-usable-hit（算已處理，從此退出佇列）——
這正是我們要的：把不存在的清掉，佇列才會密。

  python scripts/zlib_probe_sample.py --source collected-works-hunt --n 40
  node scripts/zlib_fetch.mjs --list c:/tmp/zlib_probe.jsonl --dry-run \
       --account 2 --limit 999 --max-tries 40
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WANTED = ROOT / "output" / "zlib_wanted_all.jsonl"
OUT = Path("c:/tmp/zlib_probe.jsonl")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="只抽這個 source 的")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    rows = [json.loads(l) for l in WANTED.read_text(encoding="utf-8").splitlines() if l.strip()]
    pool = [r for r in rows if r.get("source") == a.source]
    if not pool:
        raise SystemExit(f"清單裡沒有 source={a.source}")

    # 🚨 不能拿佇列前 N 筆當樣本。佇列頭被 FOCUS_AUTHORS 佔著，抽出來會是同一位
    # 作家的同一本書的不同譯名，量到的是那本書的死活，不是這份清單的體質。
    rnd = random.Random(a.seed)
    sample = rnd.sample(pool, min(a.n, len(pool)))

    out = Path(a.out)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in sample) + "\n",
                   encoding="utf-8")
    authors = {r.get("who", "?") for r in sample}
    print(f"{a.source}：母體 {len(pool)} 筆，抽出 {len(sample)} 筆（{len(authors)} 位作家）→ {out}")


if __name__ == "__main__":
    main()
