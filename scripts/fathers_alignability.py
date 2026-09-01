#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教父卷「可不可以補第三欄」的預檢 —— 挑下一冊之前先跑這支。

  python scripts/fathers_alignability.py                 # 全 39 冊總覽
  python scripts/fathers_alignability.py --volume 4e3d   # 某一冊逐部細看

補第三欄靠的是**中譯裡的錨點**：節號（「17. …」）或章標題（「第二章——…」）。
原典再齊全，中譯這邊沒有錨點就放不上去——而腳本只會回報「命中 0」，看起來像
取源壞掉。

實際踩過兩種不同的死路，兩種這支都測得出來：
  · 未分篇 —— 一冊把好幾部各自獨立的著作壓成一個前綴（安波羅修「論著選」340 章、
    奧古斯丁教義論集 244 章）。分不出哪一章屬哪一部。→ 看「部數」與「最大章」。
  · 中譯失去章結構 —— 逐部切得很乾淨，但每部內文的「第N章」標題不見了
    （ANF 第二卷的革利免《雜文集》八卷只剩 16 個標題，該有 154 個）。
    → 看「錨點覆蓋率」。

🚨 別憑節號密度挑冊。我曾照節號密度 89% 挑安波羅修，結果整冊是未分篇的。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fathers_original", ROOT / "scripts" / "fathers_original.py")
FO = importlib.util.module_from_spec(_spec)
sys.modules["fathers_original"] = FO
_spec.loader.exec_module(FO)

RANGE = re.compile(r"第(\d+)(?:[-–](\d+))?章")


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def fetch_books() -> list[dict]:
    import requests
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.get(
        f"{url}/rest/v1/ebooks",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        params={"select": "id,title,parsed_at,chunk_count",
                "or": "(subcategory.ilike.%Schaff%,subcategory.ilike.%ACCS%)",
                "limit": "500"},
        timeout=60)
    r.raise_for_status()
    return [b for b in r.json() if b.get("parsed_at") and (b.get("chunk_count") or 0) > 0]


def survey(path: Path) -> dict[str, dict]:
    """逐部統計：段數、chapter_path 宣告的最大章、中譯裡數得到的錨點。"""
    works: dict[str, dict] = defaultdict(
        lambda: {"chunks": 0, "declared": 0, "headings": 0, "numbered": 0})
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        cp = c.get("chapter_path") or ""
        name = FO.work_name(cp)
        if name in ("封面", "書名頁", "前言", "導論", "索引", "版權頁", "目錄", ""):
            continue
        w = works[name]
        w["chunks"] += 1
        m = RANGE.search(cp)
        if m:
            w["declared"] = max(w["declared"], int(m.group(2) or m.group(1)))
        body = FO.split_body(c.get("content") or "")
        w["headings"] += len(FO.chapter_headings(body))
        w["numbered"] += sum(1 for p in body if FO.LEADING_NO.match(p))
    return works


def verdict(w: dict) -> str:
    anchors = max(w["headings"], w["numbered"])
    if w["declared"] >= 100 and w["chunks"] >= 10 and anchors < w["declared"] * 0.3:
        return "未分篇？"
    if not anchors:
        return "無錨點"
    if w["declared"] and anchors < w["declared"] * 0.5:
        return "錨點稀疏"
    return "可對齊"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks-dir", default=None)
    ap.add_argument("--volume", help="只看這一冊（ebook id 前綴）")
    a = ap.parse_args()

    load_env()
    raw = a.chunks_dir or os.environ.get("EBOOK_CHUNKS_DIR") or ""
    if not raw:
        print("EBOOK_CHUNKS_DIR 沒設")
        return 1
    chunks_dir = Path(raw)

    books = fetch_books()
    if a.volume:
        books = [b for b in books if b["id"].startswith(a.volume)]

    rows = []
    for b in books:
        path = chunks_dir / f"{b['id']}.jsonl"
        if not path.exists():
            continue
        works = survey(path)
        if not works:
            continue
        if a.volume:
            print(f"《{b['title']}》")
            print(f"  {'作品':30}{'段':>4}{'宣告章':>7}{'章標題':>7}{'節號':>6}  判定")
            for name, w in sorted(works.items(), key=lambda x: -x[1]["declared"]):
                print(f"  {name:30}{w['chunks']:>4}{w['declared']:>7}"
                      f"{w['headings']:>7}{w['numbered']:>6}  {verdict(w)}")
            continue
        ok = sum(1 for w in works.values() if verdict(w) == "可對齊")
        anchors = sum(max(w["headings"], w["numbered"]) for w in works.values())
        rows.append((ok, len(works), anchors, b["id"][:8], b["title"][:46]))

    if a.volume:
        return 0
    rows.sort(key=lambda r: (-r[0], -r[2]))
    print(f"{'可對齊部':>6}{'總部數':>7}{'錨點數':>7}  冊")
    for ok, total, anchors, vid, title in rows:
        print(f"{ok:>6}{total:>7}{anchors:>7}  {vid} {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
