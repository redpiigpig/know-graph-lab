#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
乾淨語料重算 —— 把「本站自己機翻的書」剔掉之後再數通行度。

    python -X utf8 scripts/glossary_corpus_clean.py --terms output/_ctx_terms.txt

═══════════ 為什麼需要這支 ═══════════

🚨 2026-09-17 實測發現：圖書館裡混著**本站自己把英文書整本機翻的產物**。
「格列高里」全庫 1,355 次，其中 1,286 次出自四本 NPNF——那四本書名是英文，
內容卻是 98% 中文，連 CCEL 都被譯成「基督教經典伊西爾圖書館」。

拿它當「既有中譯」的證據，就是**自我循環論證**：
我們自己譯的詞，回頭被當成學界通行的證據，再拿來裁定自己該用什麼詞。
閘一寫得很清楚——**自創的譯名不在候選之列**，機翻的也一樣。

判準：**書名是英文（拉丁字母為主）但內文是中文**＝本站機翻，剔除。
真正的中譯本書名會是中文（《當代神學辭典》《古代基督信仰聖經註釋叢書》）。
"""
from __future__ import annotations

import argparse
import io
import json
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

CHUNKS = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
U = os.environ["SUPABASE_URL"]
K = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": K, "Authorization": f"Bearer {K}"}

CJK = re.compile(r"[\u4e00-\u9fff]")
LAT = re.compile(r"[A-Za-z]")
HINT = re.compile(r"基督教|神學|教父|宗教|教會|哲學|歷史|世界宗教")


def is_machine_translated(title: str, text: str) -> bool:
    """書名英文、內文中文 → 本站機翻。"""
    t_cjk = len(CJK.findall(title))
    t_lat = len(LAT.findall(title))
    if t_lat < 8 or t_cjk > t_lat * 0.3:
        return False                      # 書名有中文 → 是真的中譯本
    body_cjk = len(CJK.findall(text[:200_000]))
    body_lat = len(LAT.findall(text[:200_000]))
    return body_cjk > body_lat            # 英文書名 + 中文內容 = 機翻


def books() -> list[dict]:
    out, step = [], 1000
    while True:
        r = requests.get(
            f"{U}/rest/v1/ebooks?select=id,title,category&order=id"
            f"&limit={step}&offset={len(out)}", headers=H, timeout=120)
        r.raise_for_status()
        page = r.json()
        out += page
        if len(page) < step:
            return out


def main() -> int:
    ap = argparse.ArgumentParser(description="剔除本站機翻後重算通行度")
    ap.add_argument("--terms", required=True)
    ap.add_argument("--out", default="output/name_corpus_clean.md")
    a = ap.parse_args()

    words = sorted({w.strip() for w in io.open(a.terms, encoding="utf-8")
                    if w.strip() and not w.startswith("#")}, key=len, reverse=True)
    pat = re.compile("|".join(map(re.escape, words)))

    rows = [b for b in books() if HINT.search(b.get("category") or "")]
    keep_n = defaultdict(int); keep_b = defaultdict(int)
    mt_n = defaultdict(int);   mt_b = defaultdict(int)
    n_keep = n_mt = 0
    mt_titles: list[str] = []

    for i, b in enumerate(rows, 1):
        p = CHUNKS / f"{b['id']}.jsonl"
        if not p.exists():
            continue
        t = "\n".join((json.loads(l).get("content") or "")
                      for l in io.open(p, encoding="utf-8", errors="replace") if l.strip())
        if not t:
            continue
        mt = is_machine_translated(b["title"], t)
        if mt:
            n_mt += 1
            if len(mt_titles) < 60:
                mt_titles.append(b["title"][:60])
        else:
            n_keep += 1
        cnt, bk = (mt_n, mt_b) if mt else (keep_n, keep_b)
        seen = set()
        for m in pat.finditer(t):
            cnt[m.group(0)] += 1
            seen.add(m.group(0))
        for w in seen:
            bk[w] += 1
        if i % 400 == 0:
            print(f"  … {i}/{len(rows)}（真中譯 {n_keep} / 機翻 {n_mt}）", flush=True)

    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# 乾淨語料通行度（真中譯本 {n_keep} 本；已剔除本站機翻 {n_mt} 本）", "",
         "🚨 剔除的是**書名英文、內文中文**的書——本站自己把英文原典整本機翻的產物。",
         "拿它當「既有中譯」的證據是自我循環論證（閘一：自創／自譯不在候選之列）。", "",
         "| 寫法 | 真中譯本次數 | 真中譯本書數 | （機翻書次數） |", "|---|---:|---:|---:|"]
    for w in sorted(words, key=lambda x: -keep_b[x]):
        if keep_n[w] or mt_n[w]:
            L.append(f"| {w} | {keep_n[w]} | {keep_b[w]} | {mt_n[w]} |")
    L += ["", "## 被剔除的機翻書（前 60）", ""]
    L += [f"- {t}" for t in mt_titles]
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\n寫出 → {out}")
    print(f"真中譯本 {n_keep} 本 / 機翻 {n_mt} 本")
    for w in sorted(words, key=lambda x: -keep_b[x])[:18]:
        print(f"  {w:<18} 真={keep_n[w]:>6} ({keep_b[w]:>3}本)   機翻={mt_n[w]:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
