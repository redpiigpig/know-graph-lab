#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
譯名通行度實測 —— 在電子圖書館全文裡數各個候選寫法各出現幾次。

    python -X utf8 scripts/glossary_corpus_freq.py --family Gregory
    python -X utf8 scripts/glossary_corpus_freq.py --all --out output/name_corpus.md

naming_rules.md 的 C 項（通行度 +0～3）要有分母才算得出來。這支就是那個分母：
`ebooks` 挑出中文的基督教／神學／教父類書，讀 Drive `_chunks/{id}.jsonl` 全文，
逐一數各寫法的出現次數，並記下是「哪幾本書」在用——
🚨 出處要能指到書，不能只有一個總數（見 feedback_translation_must_cite_source）。
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
sys.path.insert(0, str(ROOT / "scripts"))
load_dotenv(ROOT / ".env")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from glossary_name_survey import FAMILIES  # noqa: E402

CHUNKS = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
SUPABASE_URL = os.environ["SUPABASE_URL"]
H = {"apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
     "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}"}

# 只數這幾類——「腓力」在生物學書裡的出現次數不能拿來裁定教父譯名。
CATEGORY_HINT = re.compile(r"基督教|神學|教父|宗教|教會|哲學|歷史|世界宗教")


def books() -> list[dict]:
    """抓 ebooks 清單。🚨 PostgREST 沒帶 range 會靜默截在 1000 筆。"""
    out, step = [], 1000
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ebooks?select=id,title,category,file_path"
            f"&order=id&limit={step}&offset={len(out)}", headers=H, timeout=120)
        r.raise_for_status()
        page = r.json()
        out += page
        if len(page) < step:
            return out


def fulltext(bid: str) -> str:
    p = CHUNKS / f"{bid}.jsonl"
    if not p.exists():
        return ""
    buf = []
    with io.open(p, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                buf.append(json.loads(line).get("content") or "")
            except json.JSONDecodeError:
                continue
    return "\n".join(buf)


def main() -> int:
    ap = argparse.ArgumentParser(description="譯名通行度實測")
    ap.add_argument("--family", action="append", choices=list(FAMILIES))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--terms", help="自訂詞表檔（一行一詞，# 開頭為註解）。"
                                    "用來數『金口若望』這種帶脈絡的複合詞——"
                                    "🚨 裸詞計數會誤導：「依納爵」大宗是羅耀拉，"
                                    "拿它去裁定安提阿那一位就是拿錯證據。")
    ap.add_argument("--out", default="output/name_corpus.md")
    a = ap.parse_args()
    if a.terms:
        words = [w.strip() for w in io.open(a.terms, encoding="utf-8")
                 if w.strip() and not w.startswith("#")]
        fams = ["脈絡詞"]
        forms = {"脈絡詞": sorted(set(words), key=len, reverse=True)}
    else:
        fams = list(FAMILIES) if a.all else (a.family or [])
        forms = None
    if not fams:
        ap.print_help()
        return 1

    # 🚨 「良」「讓」「揚」是高頻常用字，在全文語料裡數出來的是噪音不是證據。
    # 改數帶脈絡的複合詞——「教宗良」數得到良一世，「良」數到的是特土良與善良。
    EXTRA = {"Leo": ["教宗良", "良一世", "良十三世", "大良", "教宗利奧", "利奧一世"]}
    SKIP = {"良", "讓", "揚"}
    if forms is None:
        forms = {f: sorted(set(FAMILIES[f] + EXTRA.get(f, [])) - SKIP,
                           key=len, reverse=True) for f in fams}
    # 一個 family 一個 pattern，各自長的優先，免得短寫法把長寫法吃掉
    pats = {f: re.compile("|".join(map(re.escape, v))) for f, v in forms.items()}

    rows = [b for b in books() if CATEGORY_HINT.search(b.get("category") or "")]
    counts: dict[str, dict[str, int]] = {f: defaultdict(int) for f in fams}
    bybook: dict[str, dict[str, int]] = {f: defaultdict(int) for f in fams}
    scanned = 0
    for i, b in enumerate(rows, 1):
        t = fulltext(b["id"])
        if not t:
            continue
        scanned += 1
        for f in fams:
            seen = set()
            for m in pats[f].finditer(t):
                counts[f][m.group(0)] += 1
                seen.add(m.group(0))
            for form in seen:
                bybook[f][form] += 1
        if i % 200 == 0:
            print(f"  … {i}/{len(rows)}（有全文 {scanned}）", flush=True)

    out = ROOT / a.out if not Path(a.out).is_absolute() else Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    L = [f"# 譯名通行度實測（母體：{scanned} 本有全文的中文宗教／哲學／史類書）", ""]
    for f in fams:
        L += [f"## {f}", "", "| 寫法 | 總次數 | 幾本書用 |", "|---|---:|---:|"]
        for form, n in sorted(counts[f].items(), key=lambda kv: -kv[1]):
            L.append(f"| {form} | {n} | {bybook[f][form]} |")
        for form in forms[f]:
            if form not in counts[f]:
                L.append(f"| {form} | 0 | 0 |")
        L.append("")
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"寫出 → {out}（母體 {scanned} 本）")
    for f in fams:
        top = sorted(counts[f].items(), key=lambda kv: -kv[1])[:6]
        print(f"  {f:10s} " + "  ".join(f"{k}={v}" for k, v in top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
