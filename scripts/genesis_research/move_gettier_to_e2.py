# -*- coding: utf-8 -*-
"""
move_gettier_to_e2.py
使用者定案：舊 E3 的「蓋提爾／誠實生成論／強弱認識論／知行合一」通用認識論群組
不屬主體本體論(O3)、也不屬新 E3《認識你自己》各學科知識論，應歸卷二 E2《認識的形式地基》。
先前 migrate_e3_to_o3.py 把整卷 155 筆遷進 O3；本腳本把其中這 39 筆再撥到 E2，
並**還原其原始 E3 dimension**（原本就是良好的認識論小節標籤，比 O3 canonical 更貼切）。

- 資料源＝migrate ledger `c:/tmp/genesis_research/migrate_e3_to_o3.jsonl` 的 move 條目。
- 標記詞判定 E2-bound；其餘 92 筆(感質/中文房間/自指/圖靈/怪圈/複製人)留 O3。
- book_id→E2、dimension→原 E3 dim、display_order→500+。ledger 可還原。不佔 Claude 額度。

用法：
  python -X utf8 move_gettier_to_e2.py            # dry
  python -X utf8 move_gettier_to_e2.py --apply
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import requests

ROOT = Path('c:/Users/user/Desktop/know-graph-lab')
sys.path.insert(0, str(ROOT / 'scripts' / 'genesis_research'))
import reclassify_refdb as R  # env only

URL = R.URL
H = R.H
MIG = Path('c:/tmp/genesis_research/migrate_e3_to_o3.jsonl')
LEDGER = Path('c:/tmp/genesis_research/move_gettier_to_e2.jsonl')
MARK = ['蓋提爾', 'JTB', '誠實', '強認識論', '弱認識論', '強弱', '知行合一', '知識論接壤', '認識即承擔']


def patch(eid, fields):
    h = dict(H)
    h['Content-Type'] = 'application/json'
    h['Prefer'] = 'return=minimal'
    r = requests.patch(f'{URL}/rest/v1/lit_review_entries?id=eq.{eid}', headers=h,
                       data=json.dumps(fields, ensure_ascii=False).encode('utf-8'), timeout=60)
    return r.status_code in (200, 204)


def main():
    apply = '--apply' in sys.argv
    dry = not apply
    rows = []
    for l in MIG.read_text(encoding='utf-8').splitlines():
        if not l.strip():
            continue
        d = json.loads(l)
        if d['act'] == 'move' and any(m in d['old']['dimension'] for m in MARK):
            rows.append(d)
    print(f'E2-bound（蓋提爾/誠實/強弱/知行合一）：{len(rows)} 筆', flush=True)
    lf = None if dry else LEDGER.open('a', encoding='utf-8')
    n = 0
    try:
        for i, d in enumerate(rows):
            fields = {'book_id': 'E2', 'dimension': d['old']['dimension'], 'display_order': 500 + i}
            if dry:
                print(f'  {d["ref_key"][:42]:42} → E2 [{d["old"]["dimension"]}]', flush=True)
                ok = True
            else:
                ok = patch(d['id'], fields)
            if ok:
                n += 1
                if lf:
                    lf.write(json.dumps({'id': d['id'], 'ref_key': d['ref_key'],
                                         'from_book': 'O3', 'to': fields}, ensure_ascii=False) + '\n')
            else:
                print(f'  ⚠ 失敗 {d["ref_key"][:42]}', flush=True)
    finally:
        if lf:
            lf.close()
    print(f'\n完成：撥 {n} 筆到 E2（dry={dry}）', flush=True)


if __name__ == '__main__':
    main()
