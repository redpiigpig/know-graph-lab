#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
站上內容 vs 詞庫主譯 對帳。

    python -X utf8 scripts/glossary_site_conformance.py

🚨 2026-09-17 的教訓：我一度斷言「詞庫沒有歷史人物表」，據此把「先建表」
   列為第一優先——**那是錯的**。`theologians` 有 522 筆，而且早就有
   name_protestant / name_catholic_sgs / name_orthodox / name_hk / name_tw /
   name_china_academic 六個依傳統分欄的欄位。

   我漏掉它的原因：用關鍵字去濾 OpenAPI 的表名，濾詞裡沒有 "theolog"。
   **自己造的分母一定要驗**（同 feedback_silent_zero_is_a_bug）。

   所以真正的問題不是「缺表」，是**站上的 data/*.ts 沒有照詞庫**
   （詞庫 name_recommended 是絕對權威，見 feedback_glossary_strict_authority）。
   這支就是量那個落差。
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

U = os.environ["SUPABASE_URL"]
K = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": K, "Authorization": f"Bearer {K}"}

VARIANT_FIELDS = ["name_protestant", "name_catholic_sgs", "name_orthodox",
                  "name_hk", "name_tw", "name_china_academic", "name_variants"]


def rows(table: str) -> list[dict]:
    """🚨 PostgREST 沒帶 range 會靜默截在 1000 筆。"""
    out, step = [], 1000
    while True:
        r = requests.get(f"{U}/rest/v1/{table}?select=*&order=id"
                         f"&limit={step}&offset={len(out)}", headers=H, timeout=120)
        r.raise_for_status()
        page = r.json()
        out += page
        if len(page) < step:
            return out


def site_text() -> dict[str, str]:
    out = {}
    for pat in ["data/**/*.ts", "data/**/*.json", "pages/**/*.vue", "pages/**/*.ts"]:
        for f in glob.glob(str(ROOT / pat), recursive=True):
            try:
                out[str(Path(f).relative_to(ROOT)).replace("\\", "/")] = \
                    io.open(f, encoding="utf-8").read()
            except OSError:
                pass
    return out


def main() -> int:
    people = rows("theologians")
    files = site_text()
    blob = "\n".join(files.values())
    print(f"詞庫 theologians {len(people)} 筆；站上 {len(files)} 個檔\n")

    drift: list[tuple[int, str, str, str, list[str]]] = []
    for p in people:
        rec = (p.get("name_recommended") or "").strip()
        if not rec or len(rec) < 2:
            continue
        # 變體欄是分號分隔的多值
        variants = []
        for f in VARIANT_FIELDS:
            v = p.get(f)
            if isinstance(v, list):
                variants += [str(x).strip() for x in v]
            elif v:
                variants += [x.strip() for x in re.split(r"[;；／/]", str(v))]
        variants = [v for v in variants if v and v != rec and len(v) >= 2]

        n_rec = blob.count(rec)
        hits = [(v, blob.count(v)) for v in set(variants)]
        hits = [(v, n) for v, n in hits if n]
        if hits:
            drift.append((sum(n for _, n in hits), p["name_english"], rec,
                          str(n_rec), [f"{v}×{n}" for v, n in sorted(hits, key=lambda x: -x[1])]))

    drift.sort(reverse=True)
    total = sum(d[0] for d in drift)
    print(f"站上用了「非主譯的變體」的人物：{len(drift)} 位，共 {total} 處\n")
    print(f"{'人物':<38} {'詞庫主譯':<16} {'主譯用了':>6}   站上實際用的變體")
    print("─" * 118)
    for n, en, rec, n_rec, vs in drift[:45]:
        print(f"{en[:36]:<38} {rec[:14]:<16} {n_rec:>6}   {'、'.join(vs[:5])}")

    out = ROOT / "output" / "glossary_conformance.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# 站上內容 vs 詞庫主譯（theologians {len(people)} 筆）", "",
         f"站上用了非主譯變體的人物 **{len(drift)}** 位，共 **{total}** 處。", "",
         "詞庫 `name_recommended` 是絕對權威；下表每一列都是站上偏離它的地方。", "",
         "| 人物 | 詞庫主譯 | 主譯在站上用了 | 站上實際用的變體 |", "|---|---|---:|---|"]
    for n, en, rec, n_rec, vs in drift:
        L.append(f"| {en} | {rec} | {n_rec} | {'、'.join(vs)} |")
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\n寫出 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
