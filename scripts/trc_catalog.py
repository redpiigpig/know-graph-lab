#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thereformedcatholic.org（AList 檔案站）目錄普查 → 本地清單。

使用者已取得該站授權作私人收藏。**站方資源有限，一律逐項、間隔請求，不並發**。

  python scripts/trc_catalog.py            # 走訪全樹，寫 c:/tmp/trc_catalog.json
  python scripts/trc_catalog.py --report   # 只讀既有 json 出分類統計

站點是 AList：POST {BASE}/api/fs/list  {path, password, page, per_page, refresh}
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import requests

BASE = "https://thereformedcatholic.org/download"
OUT = Path("c:/tmp/trc_catalog.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DELAY = 2.0          # 每次列目錄之間的間隔（秒）——別把人家站打爆
TIMEOUT = 90


def list_dir(path: str) -> list[dict]:
    r = requests.post(
        f"{BASE}/api/fs/list",
        headers={"Content-Type": "application/json", "User-Agent": UA},
        json={"path": path, "password": "", "page": 1, "per_page": 1000, "refresh": False},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    d = r.json()
    if d.get("code") != 200:
        raise RuntimeError(f"{path}: {d.get('code')} {d.get('message')}")
    return (d.get("data") or {}).get("content") or []


def walk(path: str = "/", depth: int = 0, acc: list | None = None) -> list[dict]:
    """深度優先走訪；每次請求之間 sleep(DELAY)。"""
    if acc is None:
        acc = []
    try:
        items = list_dir(path)
    except Exception as e:  # noqa: BLE001 — 單一目錄失敗不該中斷整棵樹
        print(f"  ⚠ {path}: {e}", flush=True)
        return acc
    for it in items:
        full = f"{path.rstrip('/')}/{it['name']}"
        if it.get("is_dir"):
            print(f"{'  ' * depth}📁 {full}", flush=True)
            time.sleep(DELAY)
            walk(full, depth + 1, acc)
        else:
            acc.append({
                "path": full,
                "name": it["name"],
                "size": it.get("size", 0),
                "modified": it.get("modified"),
                "category": full.strip("/").split("/")[0],
                "ext": Path(it["name"]).suffix.lower().lstrip("."),
            })
    return acc


def report(files: list[dict]) -> None:
    total = sum(f["size"] for f in files)
    print(f"\n檔案 {len(files)} 個，合計 {total / 1024 / 1024 / 1024:.2f} GB\n")
    print(f"{'分類':<34}{'檔數':>6}{'GB':>9}")
    by_cat: Counter = Counter()
    size_cat: Counter = Counter()
    for f in files:
        by_cat[f["category"]] += 1
        size_cat[f["category"]] += f["size"]
    for cat, n in by_cat.most_common():
        print(f"  {cat[:32]:<32}{n:>6}{size_cat[cat] / 1024 ** 3:>9.2f}")
    print(f"\n{'副檔名':<12}{'檔數':>6}{'GB':>9}")
    ext = Counter(f["ext"] for f in files)
    ext_size: Counter = Counter()
    for f in files:
        ext_size[f["ext"]] += f["size"]
    for e, n in ext.most_common(12):
        print(f"  {(e or '(無)'):<10}{n:>6}{ext_size[e] / 1024 ** 3:>9.2f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="只讀既有清單出報表")
    a = ap.parse_args()
    if a.report:
        files = json.loads(OUT.read_text(encoding="utf-8"))
    else:
        files = walk("/")
        OUT.write_text(json.dumps(files, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n已寫 {OUT}")
    report(files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
