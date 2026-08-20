#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 譯名與站上譯名表對齊。

站上 /translation-glossary 的 `deities`／`place_names`／`theological_terms`
是**絕對權威**（見 feedback_glossary_strict_authority）：凡表裡有的，一律照表，
不接受本管線自譯的說法。

分工：
  · 表裡**有**的 → `--fix` 自動統一（改逐篇專名表與已譯出的譯文）
  · 表裡**沒有**的 → 只列清單交使用者定奪，**絕不自行寫進詞庫**
    （見 feedback_glossary_ancient_name_priority：「還有哪些例子」＝列清單給使用者定奪）

用法：
    python scripts/hellenika_glossary.py --check        # 只報告
    python scripts/hellenika_glossary.py --fix          # 依詞庫統一
    python scripts/hellenika_glossary.py --candidates   # 出待定名清單（Markdown）
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys

import requests

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CGRN_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'cgrn')
CAND_OUT = os.path.join(ROOT, 'data', 'hellenika', 'glossary-candidates.md')


def _load_env() -> None:
    for line in io.open(os.path.join(ROOT, '.env'), encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))


def fetch_glossary() -> dict[str, tuple[str, str]]:
    """英文名 → (權威中譯, 來源表)。鍵一律小寫供比對。"""
    _load_env()
    url = os.environ['SUPABASE_URL']
    key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    h = {'apikey': key, 'Authorization': f'Bearer {key}'}

    specs = [
        ('deities', 'name_english', 'name_recommended', 'name_variants'),
        ('place_names', 'name_english', 'name_recommended', 'name_variants'),
        ('theological_terms', 'term_english', 'zh_recommended', None),
    ]
    table: dict[str, tuple[str, str]] = {}
    for tbl, en_col, zh_col, var_col in specs:
        cols = ','.join(c for c in (en_col, zh_col, var_col) if c)
        rows: list[dict] = []
        offset = 0
        while True:
            r = requests.get(f'{url}/rest/v1/{tbl}?select={cols}&limit=1000&offset={offset}',
                             headers=h, timeout=90)
            r.raise_for_status()
            batch = r.json()
            rows += batch
            if len(batch) < 1000:
                break
            offset += 1000
        for row in rows:
            en, zh = row.get(en_col), row.get(zh_col)
            if not (en and zh):
                continue
            table.setdefault(en.strip().lower(), (zh.strip(), tbl))
            # 變體也當作可比對的英文寫法
            var = row.get(var_col) if var_col else None
            for v in (var if isinstance(var, list) else []):
                if isinstance(v, str) and re.search(r'[A-Za-z]', v):
                    table.setdefault(v.strip().lower(), (zh.strip(), tbl))
        print(f'  {tbl}: {len(rows)} 筆', flush=True)
    return table


# 神祇稱號常寫成「Zeus Meilichios」「Apollo Delphinios」，詞庫多半只收本名。
# 比對時先試全稱，再退到本名＋稱號分開查。
def lookup(en: str, gloss: dict) -> tuple[str, str] | None:
    k = en.strip().lower()
    if k in gloss:
        return gloss[k]
    k2 = re.sub(r'^(the|a)\s+', '', k)
    if k2 in gloss:
        return gloss[k2]
    return None


def scan() -> tuple[list[dict], list[dict]]:
    """回傳 (與詞庫不符者, 詞庫未收者)。"""
    gloss = fetch_glossary()
    mismatch, missing = [], []
    for f in sorted(glob.glob(os.path.join(CGRN_DIR, '*.aligned.json'))):
        d = json.loads(io.open(f, encoding='utf-8').read())
        for en, ours in (d.get('names') or {}).items():
            hit = lookup(en, gloss)
            if hit is None:
                missing.append({'file': f, 'title': d['title_zh'], 'en': en, 'ours': ours})
            elif hit[0] != ours:
                mismatch.append({'file': f, 'title': d['title_zh'], 'en': en,
                                 'ours': ours, 'authority': hit[0], 'table': hit[1]})
    return mismatch, missing


def apply_fixes(mismatch: list[dict]) -> int:
    """依詞庫改逐篇專名表與已譯出的譯文。長詞先replace，避免部分覆蓋。"""
    by_file: dict[str, list[dict]] = {}
    for m in mismatch:
        by_file.setdefault(m['file'], []).append(m)

    changed = 0
    for f, items in by_file.items():
        d = json.loads(io.open(f, encoding='utf-8').read())
        items.sort(key=lambda m: len(m['ours']), reverse=True)
        for m in items:
            if d['names'].get(m['en']) == m['ours']:
                d['names'][m['en']] = m['authority']
            for seg in d['segments']:
                if seg['zh'] and m['ours'] in seg['zh']:
                    seg['zh'] = seg['zh'].replace(m['ours'], m['authority'])
                    changed += 1
        io.open(f, 'w', encoding='utf-8').write(
            json.dumps(d, ensure_ascii=False, indent=1) + '\n')
    return changed


def write_candidates(missing: list[dict]) -> None:
    by_name: dict[str, dict] = {}
    for m in missing:
        rec = by_name.setdefault(m['en'], {'ours': m['ours'], 'where': set()})
        rec['where'].add(m['title'])

    lines = [
        '# 希臘羅馬大藏經 · 待定名清單',
        '',
        '這些專名在站上譯名表（`/translation-glossary`）**查無此條**，因此本管線的譯法',
        '只是暫用，未經定名。依既定規矩不自行寫進詞庫——請逐條定奪後再入庫。',
        '',
        '多數是希臘祭儀特有的東西：神祇稱號（epithet）、地方月份名、祭司職稱、聖所名。',
        '這一層正是現行詞庫最缺的，補進去之後整個 Κ 祭儀法卷都能受益。',
        '',
        '| 英文原名 | 本管線暫譯 | 出現於 |',
        '|---|---|---|',
    ]
    for en in sorted(by_name):
        rec = by_name[en]
        lines.append(f"| {en} | {rec['ours']} | {'、'.join(sorted(rec['where']))} |")
    lines += ['', f'共 {len(by_name)} 條待定名。']
    io.open(CAND_OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'  待定名清單 {len(by_name)} 條 → {os.path.relpath(CAND_OUT, ROOT)}')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('--candidates', action='store_true')
    args = ap.parse_args()
    if not any((args.check, args.fix, args.candidates)):
        ap.print_help()
        return

    print('拉取站上譯名表…', flush=True)
    mismatch, missing = scan()

    print(f'\n與詞庫不符 {len(mismatch)} 條、詞庫未收 {len(missing)} 條\n')
    for m in mismatch:
        print(f"  ✗ {m['en']}：本管線「{m['ours']}」→ 詞庫「{m['authority']}」（{m['table']}）"
              f"　［{m['title']}］")

    if args.fix and mismatch:
        n = apply_fixes(mismatch)
        print(f'\n已依詞庫統一，改動 {n} 處譯文段落')
    if args.candidates or args.check:
        write_candidates(missing)


if __name__ == '__main__':
    main()
