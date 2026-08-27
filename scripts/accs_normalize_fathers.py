#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""照翻譯詞庫（theologians）統一 accs_commentary 的教父署名。

同一位教父在 ACCS 語料裡有多種寫法：不同譯名傳統（屈梭多模／金口約翰／金口若望）
加上 OCR 錯字（屈梭多穆／屈梭多姆／屈梭多摩／屈梭模…）。讀者會以為是不同的人，
依教父篩選也全是破的。

權威來源＝`theologians` 的 `name_recommended`（見 [[feedback_glossary_strict_authority]]）。
比對範圍涵蓋詞庫的各傳統欄位：新教／思高／東正教／港／台／陸學界，任一欄位
（以「；」分隔的變體也算）命中，就改寫成該筆的 name_recommended。

只動詞庫查得到的寫法；查不到的一律不碰——那些要先人工策展、補進詞庫，
再跑一次本腳本（可重複執行）。

預設 dry-run，要 --apply 才寫入。
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

TABLE = 'accs_commentary'
BACKUP_DIR = Path('c:/tmp/accs_rows_backup')
NAME_COLS = ['name_recommended', 'name_protestant', 'name_catholic_sgs',
             'name_orthodox', 'name_hk', 'name_tw', 'name_china_academic']


def load_glossary() -> dict[str, str]:
    """各傳統寫法 → name_recommended。"""
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/theologians?select={",".join(NAME_COLS)}'
                         f'&offset={off}&limit=1000', headers=te.H_GET, timeout=60)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    variants: dict[str, str] = {}
    for x in rows:
        rec = (x.get('name_recommended') or '').strip()
        if not rec:
            continue
        for col in NAME_COLS:
            for v in (x.get(col) or '').split('；'):
                v = v.strip()
                if v:
                    variants.setdefault(v, rec)   # 先到先得；name_recommended 排最前
    return variants


def fetch_rows() -> list[dict]:
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/{TABLE}?select=id,book_code,father_name,section_kind'
                         f'&order=id&offset={off}&limit=1000', headers=te.H_GET, timeout=120)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    variants = load_glossary()
    rows = fetch_rows()
    print(f'詞庫可比對寫法 {len(variants)} 種；accs_commentary {len(rows)} 列')

    todo = defaultdict(list)          # (現值, 推薦名) -> [id, ...]
    unknown = Counter()
    for x in rows:
        if x['section_kind'] != 'comment':
            continue
        cur = (x['father_name'] or '').strip()
        if not cur:
            continue
        rec = variants.get(cur)
        if rec is None:
            unknown[cur] += 1
        elif rec != cur:
            todo[(cur, rec)].append(x['id'])

    n_rows = sum(len(v) for v in todo.values())
    print(f'\n要改寫 {len(todo)} 種寫法 / {n_rows} 列：')
    for (cur, rec), ids in sorted(todo.items(), key=lambda kv: -len(kv[1])):
        print(f'   {len(ids):5d}  {cur}  →  {rec}')
    print(f'\n詞庫查不到、維持原樣: {len(unknown)} 種 / {sum(unknown.values())} 列')
    for k, v in unknown.most_common(10):
        print(f'   {v:5d}  {k}')
    if not todo:
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'accs_father_rename_{stamp}.jsonl'
    with backup.open('w', encoding='utf-8') as fh:
        for (cur, rec), ids in todo.items():
            fh.write(json.dumps({'from': cur, 'to': rec, 'ids': ids}, ensure_ascii=False) + '\n')
    print(f'\n備份對照 → {backup}（{len(todo)} 組 / {n_rows} 列）')

    if not args.apply:
        print('(dry-run；要寫入請加 --apply)')
        return 0

    changed = 0
    for (cur, rec), ids in todo.items():
        for i in range(0, len(ids), 100):
            chunk = ','.join(str(v) for v in ids[i:i + 100])
            r = requests.patch(f'{te.URL}/rest/v1/{TABLE}?id=in.({chunk})',
                               headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                               json={'father_name': rec}, timeout=120)
            r.raise_for_status()
            changed += len(ids[i:i + 100])
    print(f'已改寫 {changed} 列')

    after = fetch_rows()
    left = sum(1 for x in after if x['section_kind'] == 'comment'
               and (x['father_name'] or '').strip() in variants
               and variants[(x['father_name'] or '').strip()] != (x['father_name'] or '').strip())
    print(f'複查：仍與推薦名不一致 {left} 列')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
