# -*- coding: utf-8 -*-
"""
reclassify_offcanon.py
把某卷所有「dimension 不在該卷 canonical 小節清單」的條目，重新分類到 canonical 小節。
用於 M1/M2/E1/E2——這幾卷的參考資料在較早 session 建立，dimension 是章級或舊版章節
標籤，與現行 clean_inv 不一致（reclassify_refdb.py 只處理 display_order<200，漏掉
dialogue/遷入條目，本腳本補上：對齊條件改成「off-canonical」不看 display_order）。

走 Gemini→NVIDIA→Haiku（不佔 Claude 額度）；ledger 可還原。

用法：
  python -X utf8 reclassify_offcanon.py            # M1 M2 E1 E2
  python -X utf8 reclassify_offcanon.py --vol E1
  python -X utf8 reclassify_offcanon.py --dry-run
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import requests

ROOT = Path('c:/Users/user/Desktop/know-graph-lab')
sys.path.insert(0, str(ROOT / 'scripts' / 'genesis_research'))
import reclassify_refdb as R  # vol_sections / classify_batch / patch / env

URL = R.URL
H = R.H
INV = R.INV
LEDGER = Path('c:/tmp/genesis_research/reclassify_offcanon.jsonl')
DEFAULT = ['M1', 'M2', 'E1', 'E2']


def canon_set(v):
    return {s for _, s in R.vol_sections(v)}


def fetch_off(v):
    r = requests.get(f'{URL}/rest/v1/lit_review_entries', headers={**H, 'Range': '0-9999'},
                     params={'select': 'id,ref_key,title,abstract_zh,dimension,display_order',
                             'project_slug': 'eq.genesis-philosophy', 'book_id': f'eq.{v}',
                             'order': 'display_order'}, timeout=120)
    r.raise_for_status()
    cs = canon_set(v)
    return [e for e in r.json() if (e.get('dimension') or '') not in cs]


def process(v, batch_size, dry, done):
    secs = R.vol_sections(v)
    rows = [e for e in fetch_off(v) if e['id'] not in done]
    print(f'\n=== {v} === off-canonical 待處理 {len(rows)}／canonical 小節 {len(secs)} ===', flush=True)
    lf = None if dry else LEDGER.open('a', encoding='utf-8')
    n = 0
    try:
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            verdicts = R.classify_batch(secs, batch)
            if verdicts is None:
                print(f'  batch {i // batch_size} 三引擎全失敗，跳過', flush=True)
                continue
            vmap = {x.get('i'): x.get('sec') for x in verdicts if isinstance(x, dict)}
            for j, e in enumerate(batch):
                si = vmap.get(j)
                if not isinstance(si, int) or not (0 <= si < len(secs)):
                    print(f'  ⚠ {e["ref_key"][:38]} 無效 sec={si}，保留原 dim', flush=True)
                    continue
                new_dim = secs[si][1]
                if dry:
                    print(f'    {e.get("dimension")}  →  {new_dim}', flush=True)
                    ok = True
                else:
                    ok = new_dim == e.get('dimension') or R.patch(e['id'], new_dim)
                if ok:
                    n += 1
                    if lf:
                        lf.write(json.dumps({'id': e['id'], 'vol': v, 'old': e.get('dimension'),
                                             'new': new_dim}, ensure_ascii=False) + '\n')
            if lf:
                lf.flush()
            print(f'  進度 {min(i + batch_size, len(rows))}/{len(rows)}（累計改 {n}）', flush=True)
    finally:
        if lf:
            lf.close()
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vol', nargs='*', default=None)
    ap.add_argument('--batch', type=int, default=12)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    done = set()
    if LEDGER.exists():
        for ln in LEDGER.read_text(encoding='utf-8').splitlines():
            try:
                done.add(json.loads(ln)['id'])
            except Exception:
                pass
    print(f'ledger 已處理 {len(done)} 筆', flush=True)
    total = 0
    for v in (args.vol or DEFAULT):
        total += process(v, args.batch, args.dry_run, done)
    print(f'\n完成：重分類 {total} 筆（dry-run={args.dry_run}）', flush=True)


if __name__ == '__main__':
    main()
