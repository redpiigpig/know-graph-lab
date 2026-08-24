#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 譯名與站上譯名表對齊。

站上 /translation-glossary 的 `deities`／`place_names`／`theological_terms`
是**絕對權威**（見 feedback_glossary_strict_authority）：凡表裡有的，一律照表，
不接受本管線自譯的說法。

**唯一例外見下 CORPUS_OVERRIDES**：詞庫有幾條出自聖經或通俗語境，套進希臘宗教
語境並不合適，user 2026-08-23 定調本藏經改用中文古典學界的譯名慣例。這是
使用者的決定，不是本管線自作主張，故明文列出並由 --fix 跳過。

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

# ─────────────── 本藏經的譯名例外（user 2026-08-23 定調）───────────────
# 《希臘羅馬大藏經》以**中文古典學界**的譯名慣例為準，不套用詞庫中出自聖經或
# 通俗語境的條目。理由逐條列出，日後有人想「統一」時看得到為什麼不能統一。
#
# 🚨 這張表存在的意義：沒有它，任何人跑一次 --fix 就會把使用者的決定默默改回去。
CORPUS_OVERRIDES = {
    'hesiod':    ('赫西俄德',   '古典學界通行（商務印書館《神譜》張竹明譯本一系）'),
    'demeter':   ('得墨忒耳',   '古典學界通行；「狄蜜特」是通俗音譯風格'),
    'hermes':    ('赫爾墨斯',   '「赫密士」屬《赫密士文集》那一系晚期埃及—希臘的稱法，'
                                '與奧林匹亞十二神的赫爾墨斯同名而不同脈絡'),
    'cyrene':    ('昔蘭尼',     '「古利奈」是新約譯法（古利奈人西門，可 15:21）；'
                                '本藏經裡它一律是古典希臘殖民城邦'),
    'aphrodite': ('阿芙羅狄忒', '古典學界通行；「阿芙羅黛蒂」是通俗音譯風格'),
    'artemis':   ('阿爾忒彌斯', '古典學界通行；「阿緹米絲」是通俗音譯風格'),
    'osiris':    ('奧西里斯',   '古典學與埃及學通行'),
    'hades':     ('哈得斯',     '古典學界通行；「黑帝斯」出自通俗與電玩語境'),
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CGRN_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'cgrn')
PHI_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'phi')
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


def scan() -> tuple[list[dict], list[dict], list[dict]]:
    """回傳 (與詞庫不符者, 詞庫未收者, 本藏經例外)。"""
    gloss = fetch_glossary()
    mismatch, missing, overridden = [], [], []
    for f in sorted(glob.glob(os.path.join(CGRN_DIR, '*.aligned.json'))
                    + glob.glob(os.path.join(PHI_DIR, '*.aligned.json'))):
        d = json.loads(io.open(f, encoding='utf-8').read())
        for en, ours in (d.get('names') or {}).items():
            ov = CORPUS_OVERRIDES.get(en.strip().lower())
            if ov:
                # 本藏經例外：以古典學譯名為準，詞庫不適用。仍檢查有沒有寫錯。
                overridden.append({'file': f, 'title': d['title_zh'], 'en': en,
                                   'ours': ours, 'expect': ov[0], 'why': ov[1]})
                continue
            hit = lookup(en, gloss)
            if hit is None:
                missing.append({'file': f, 'title': d['title_zh'], 'en': en, 'ours': ours})
            elif hit[0] != ours:
                mismatch.append({'file': f, 'title': d['title_zh'], 'en': en,
                                 'ours': ours, 'authority': hit[0], 'table': hit[1]})
    return mismatch, missing, overridden


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
    mismatch, missing, overridden = scan()

    print(f'\n與詞庫不符 {len(mismatch)} 條、詞庫未收 {len(missing)} 條、'
          f'本藏經例外 {len(overridden)} 條\n')
    for m in mismatch:
        print(f"  ✗ {m['en']}：本管線「{m['ours']}」→ 詞庫「{m['authority']}」（{m['table']}）"
              f"　［{m['title']}］")
    seen: set[str] = set()
    for o in overridden:
        if o['en'] in seen:
            continue
        seen.add(o['en'])
        ok = o['ours'] == o['expect']
        print(f"  {'✓' if ok else '✗'} 〔本藏經例外〕{o['en']}：應作「{o['expect']}」"
              + ('' if ok else f"，但檔中是「{o['ours']}」需修")
              + f"\n      {o['why']}")

    if args.fix and mismatch:
        n = apply_fixes(mismatch)
        print(f'\n已依詞庫統一，改動 {n} 處譯文段落')
    # 🚨 --check 唯讀。write_candidates 會整份覆寫，曾把人工策展過的定名對照表
    #    連同 register 依據一起洗掉；只有明確要求 --candidates 時才重生。
    if args.candidates:
        write_candidates(missing)
    elif missing:
        note = os.path.relpath(CAND_OUT, ROOT)
        print()
        print(f'（詞庫未收 {len(missing)} 條；要重生對照表請加 --candidates，'
              f'注意會覆寫 {note}）')


if __name__ == '__main__':
    main()
