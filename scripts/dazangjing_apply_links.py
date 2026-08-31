#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把審過的逐卷連結寫回 data/dazangjing/{era}.ts。

  python scripts/dazangjing_apply_links.py --links data/dazangjing/source-catalog/LINKS_fathers.jsonl
  python scripts/dazangjing_apply_links.py --links ... --apply

輸入是 scripts/dazangjing_link_fathers.py 產出的 .jsonl。只改 `link:` 一個欄位，
其他一律不動。

🚨 逐行比對，且一次只改一行。資料檔裡一部作品就是一行，所以「這一行同時有這個
   title_zh 又有 link: '/fathers'」是可驗證的定位條件。找到 0 行或 2 行以上一律
   跳過並報出來——寧可少改一條，也不要改到同名的另一部書。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dazangjing"
FILES = {
    "pre": DATA / "index.ts",
    "ancient": DATA / "ancient.ts",
    "medieval": DATA / "medieval.ts",
    "early-modern": DATA / "early-modern.ts",
    "modern": DATA / "modern.ts",
}
PORTAL_LINK = "link: '/fathers'"


def esc(title: str) -> str:
    """資料檔用單引號字串，標題裡的單引號是跳脫過的。"""
    return title.replace("\\", "\\\\").replace("'", "\\'")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--links", required=True)
    ap.add_argument("--apply", action="store_true", help="寫檔（預設只報告）")
    a = ap.parse_args()

    rows = [json.loads(l) for l in
            Path(a.links).read_text(encoding="utf-8").splitlines() if l.strip()]
    by_era: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_era[r["era"]].append(r)
    print(f"待寫回 {len(rows)} 條，涉及 {len(by_era)} 個時代")

    total_ok = 0
    skipped: list[tuple[str, str]] = []
    for era, items in by_era.items():
        path = FILES.get(era)
        if not path or not path.exists():
            skipped += [(r["title_zh"], f"找不到 {era} 的資料檔") for r in items]
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        changed = 0
        for r in items:
            needle = f"title_zh: '{esc(r['title_zh'])}'"
            hits = [i for i, ln in enumerate(lines)
                    if needle in ln and PORTAL_LINK in ln]
            if len(hits) != 1:
                skipped.append((r["title_zh"],
                                f"{era} 檔內符合的行有 {len(hits)} 行，不是剛好 1 行"))
                continue
            i = hits[0]
            lines[i] = lines[i].replace(PORTAL_LINK, f"link: '{r['link']}'", 1)
            changed += 1
        total_ok += changed
        print(f"  {era}: {changed} / {len(items)} 條")
        if a.apply and changed:
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n可寫回 {total_ok} 條；跳過 {len(skipped)} 條")
    for t, why in skipped[:25]:
        print(f"  · {t} —— {why}")
    if len(skipped) > 25:
        print(f"  …另外 {len(skipped) - 25} 條")
    if not a.apply:
        print("\n（只報告不寫檔。確認無誤後加 --apply）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
