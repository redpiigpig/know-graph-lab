#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 ACCS 語料的教父寫法寫進 theologians.name_variants。

對照表在 accs_father_variants.json（以 name_english 定位人物，身分人工確認過）。
寫進去之後跑 accs_normalize_fathers.py，那些寫法就會一併歸到 name_recommended。

之所以先進詞庫再正規化、而不是直接改資料表：詞庫是權威來源
（[[feedback_glossary_strict_authority]]），這樣別的語料日後遇到同樣的寫法
也能共用；而且改定名只要改詞庫再重跑，不必回頭動資料。

預設 dry-run，要 --apply 才寫入。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

MAP_PATH = Path(__file__).resolve().parent / 'accs_father_variants.json'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    mapping = {k: v for k, v in json.loads(MAP_PATH.read_text(encoding='utf-8')).items()
               if not k.startswith('_')}

    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/theologians'
                         f'?select=id,name_english,name_recommended,name_variants'
                         f'&offset={off}&limit=1000', headers=te.H_GET, timeout=60)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    by_en = {(x['name_english'] or '').strip(): x for x in rows}

    missing = [k for k in mapping if k not in by_en]
    if missing:
        print('✗ 詞庫找不到這些 name_english，請先確認拼法或新增人物：')
        for k in missing:
            print(f'   {k}')
        return 1

    todo = []
    for en, variants in mapping.items():
        row = by_en[en]
        have = {v.strip() for v in (row['name_variants'] or '').split('；') if v.strip()}
        add = [v for v in variants if v not in have and v != row['name_recommended']]
        if add:
            todo.append((row, sorted(have | set(add))))

    print(f'要更新 {len(todo)} 位人物的變體欄：')
    for row, merged in todo:
        print(f"   {row['name_recommended']:<16s} ← {'、'.join(merged)}")
    if not todo:
        return 0
    if not args.apply:
        print('\n(dry-run；要寫入請加 --apply)')
        return 0

    for row, merged in todo:
        r = requests.patch(f"{te.URL}/rest/v1/theologians?id=eq.{row['id']}",
                           headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                           json={'name_variants': '；'.join(merged)}, timeout=60)
        r.raise_for_status()
    print(f'\n已更新 {len(todo)} 位')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
