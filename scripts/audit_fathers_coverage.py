#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/fathers 三欄的**填充率**：每一卷有多少段真的三欄都有東西。

  python scripts/audit_fathers_coverage.py           # 全部
  python scripts/audit_fathers_coverage.py --third   # 只看已補第三欄那 19 卷

與 `scripts/audit_fathers_columns.mjs` 分工：那一支查「排出來對不對齊」，這一支查
「有沒有東西」。兩個問題不一樣——一卷可以完全對齊而九成的段根本沒有原典欄。

🚨 **「有第三欄」不等於「三欄填滿」。** `/fathers` 首頁的「附原典」標籤是整卷層級的
布林值，只要那一卷有任何一段補了原典就會亮；實際填充率可能只有個位數百分比。
問「翻譯填滿了嗎」要看本表的「三欄齊」那一欄，不要看標籤。

取源與 reader 一致：先本機 Drive（`EBOOK_CHUNKS_DIR`），讀不到才算缺。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def fathers_books() -> list[dict]:
    """與 pages/fathers/index.vue 同一條查詢：subcategory 含 Schaff 或 ACCS。"""
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    q = urllib.parse.quote("subcategory.ilike.*Schaff*,subcategory.ilike.*ACCS*")
    req = urllib.request.Request(
        f"{url}/rest/v1/ebooks?or=({q})&select=id,title,chunk_count&limit=500",
        headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def third_column_ids() -> set[str]:
    vue = (ROOT / "pages" / "fathers" / "index.vue").read_text(encoding="utf-8")
    m = re.search(r"ORIGINAL_IDS\s*=\s*new Set\(\[(.*?)\]\)", vue, re.S)
    return set(re.findall(r"['\"]([0-9a-f-]{36})['\"]", m.group(1))) if m else set()


def count(chunks: list[dict]) -> dict:
    """一卷的填充統計。原典＝en 以外的任何來源語言。"""
    zh = en = orig = all3 = 0
    langs: set[str] = set()
    for c in chunks:
        src = c.get("sources") or {}
        has_zh = bool((c.get("content") or "").strip())
        has_en = bool((src.get("en") or c.get("source_text") or "").strip())
        others = [k for k in src if k not in ("en", "zh") and (src.get(k) or "").strip()]
        langs.update(others)
        zh += has_zh
        en += has_en
        orig += bool(others)
        all3 += has_zh and has_en and bool(others)
    return {"n": len(chunks), "zh": zh, "en": en, "orig": orig, "all3": all3,
            "langs": "/".join(sorted(langs)) or "—"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--third", action="store_true", help="只看已補第三欄那幾卷")
    a = ap.parse_args()
    load_env()

    chunks_dir = Path(os.environ.get("EBOOK_CHUNKS_DIR", ""))
    have_third = third_column_ids()
    books = fathers_books()
    books.sort(key=lambda b: b.get("title") or "")

    print(f"{'卷':46} {'段':>5} {'繁中':>6} {'英':>6} {'原典':>6} {'三欄齊':>7}  語言")
    tot = {"n": 0, "zh": 0, "en": 0, "orig": 0, "all3": 0}
    missing = []
    for b in books:
        if a.third and b["id"] not in have_third:
            continue
        f = chunks_dir / f"{b['id']}.jsonl"
        if not f.exists():
            missing.append(b)
            continue
        chunks = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        r = count(chunks)
        for k in tot:
            tot[k] += r[k]
        pct = f"{r['all3'] / r['n']:.0%}" if r["n"] else "—"
        mark = "★" if b["id"] in have_third else " "
        print(f"{mark}{(b.get('title') or '')[:45]:45} {r['n']:5} {r['zh']:6} {r['en']:6} "
              f"{r['orig']:6} {r['all3']:5}{pct:>4}  {r['langs']}")

    print(f"\n合計 {tot['n']} 段：繁中 {tot['zh']}（{tot['zh'] / max(1, tot['n']):.0%}）／"
          f"英 {tot['en']}（{tot['en'] / max(1, tot['n']):.0%}）／"
          f"原典 {tot['orig']}（{tot['orig'] / max(1, tot['n']):.0%}）／"
          f"三欄齊 {tot['all3']}（{tot['all3'] / max(1, tot['n']):.0%}）")
    print(f"★＝首頁標了「附原典」的卷，共 {len(have_third)} 卷")
    if missing:
        print(f"🚨 讀不到 JSONL 的卷：{len(missing)}（先確認 G: 有沒有掛載）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
