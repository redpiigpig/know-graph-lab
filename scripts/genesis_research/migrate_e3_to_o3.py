# -*- coding: utf-8 -*-
"""
migrate_e3_to_o3.py
把舊 E3《主體的誕生》的研究資料（逐節對話地圖＋refdb）整卷重歸到本體論 O3。
背景：使用者定案「主體的生成／誕生屬本體論卷三 O3，不屬認識論」——見
[[project_genesis_epistemology_trilogy]]。E3 清空後供新書《認識你自己》使用。

做法：
  - E3∩O3 ref_key 重複者：刪 E3 副本（O3 已有，避免違反 unique 鍵）。
  - E3-only：book_id→O3、dimension 用 Gemini 引擎重歸到 O3 canonical 小節、
    display_order 給新 offset(400+) 排在 O3 原生條目之後（保留來源可辨）。
  - 全程寫 ledger（含被刪列的完整 row、被搬列的 old 值）→ 可還原。不佔 Claude 額度。

用法：
  python -X utf8 migrate_e3_to_o3.py            # dry-run（印計畫，不寫 DB）
  python -X utf8 migrate_e3_to_o3.py --apply    # 實際執行
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import requests

ROOT = Path('c:/Users/user/Desktop/know-graph-lab')
sys.path.insert(0, str(ROOT / 'scripts' / 'genesis_research'))
import reclassify_refdb as R  # 帶入 env + Gemini/NVIDIA/Haiku 引擎 + vol_sections/classify_batch

URL = R.URL
H = R.H
LEDGER = Path('c:/tmp/genesis_research/migrate_e3_to_o3.jsonl')
OFFSET = 400  # 搬入 O3 的 display_order 起點（排在 O3 原生 refdb<200 / dialogue 200+ 之後）


def get(v):
    r = requests.get(f'{URL}/rest/v1/lit_review_entries', headers={**H, 'Range': '0-9999'},
                     params={'select': '*', 'project_slug': 'eq.genesis-philosophy',
                             'book_id': f'eq.{v}', 'order': 'display_order'}, timeout=120)
    r.raise_for_status()
    return r.json()


def patch(eid, fields):
    h = dict(H)
    h['Content-Type'] = 'application/json'
    h['Prefer'] = 'return=minimal'
    r = requests.patch(f'{URL}/rest/v1/lit_review_entries?id=eq.{eid}', headers=h,
                       data=json.dumps(fields, ensure_ascii=False).encode('utf-8'), timeout=60)
    return r.status_code in (200, 204)


def delete(eid):
    h = dict(H)
    h['Prefer'] = 'return=minimal'
    r = requests.delete(f'{URL}/rest/v1/lit_review_entries?id=eq.{eid}', headers=h, timeout=60)
    return r.status_code in (200, 204)


def main():
    apply = '--apply' in sys.argv
    dry = not apply
    e3 = get('E3')
    o3 = get('O3')
    o3k = {r['ref_key'] for r in o3}
    secs = R.vol_sections('O3')
    dups = [r for r in e3 if r['ref_key'] in o3k]
    moves = [r for r in e3 if r['ref_key'] not in o3k]
    print(f'E3 {len(e3)} | O3 {len(o3)} | dup-in-O3 {len(dups)}(delete) | move {len(moves)} | O3 小節 {len(secs)}',
          flush=True)

    lf = None if dry else LEDGER.open('a', encoding='utf-8')
    n_move = n_del = 0
    try:
        for i in range(0, len(moves), 12):
            batch = moves[i:i + 12]
            verdicts = R.classify_batch(secs, batch) or []
            vmap = {x.get('i'): x.get('sec') for x in verdicts if isinstance(x, dict)}
            for j, e in enumerate(batch):
                si = vmap.get(j)
                new_dim = secs[si][1] if isinstance(si, int) and 0 <= si < len(secs) else e.get('dimension')
                fields = {'book_id': 'O3', 'dimension': new_dim, 'display_order': OFFSET + i + j}
                if dry:
                    print(f'  MOVE {e["ref_key"][:38]:38} [{e.get("dimension")}] -> [{new_dim}]', flush=True)
                    ok = True
                else:
                    ok = patch(e['id'], fields)
                if ok:
                    n_move += 1
                    if lf:
                        lf.write(json.dumps({'act': 'move', 'id': e['id'], 'ref_key': e['ref_key'],
                                             'old': {'book_id': 'E3', 'dimension': e.get('dimension'),
                                                     'display_order': e.get('display_order')},
                                             'new': fields}, ensure_ascii=False) + '\n')
                else:
                    print(f'  ⚠ MOVE 失敗 {e["ref_key"][:38]}', flush=True)
            if lf:
                lf.flush()
            print(f'  搬移進度 {min(i + 12, len(moves))}/{len(moves)}', flush=True)

        for e in dups:
            if dry:
                print(f'  DEL-DUP {e["ref_key"][:38]}', flush=True)
                ok = True
            else:
                ok = delete(e['id'])
            if ok:
                n_del += 1
                if lf:
                    lf.write(json.dumps({'act': 'delete', 'row': e}, ensure_ascii=False) + '\n')
            else:
                print(f'  ⚠ DELETE 失敗 {e["ref_key"][:38]}', flush=True)
    finally:
        if lf:
            lf.close()
    print(f'\n完成：搬移 {n_move}、刪重複 {n_del}（dry={dry}）', flush=True)
    if dry:
        print('→ 檢查無誤後加 --apply 實際執行', flush=True)


if __name__ == '__main__':
    main()
