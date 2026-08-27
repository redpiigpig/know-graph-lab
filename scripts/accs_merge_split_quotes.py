#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把被批次邊界切成兩列的同一則引文併回一則。

OCR 是逐批處理的，prompt 雖然要求「跨頁未完的同一則正文要接成完整一段」，
但那只在同一批內有效；批與批之間沒人負責，於是一則長引文被切成兩列。
讀者看到的就是同一位作者的署名在段落中間冒出來一次、結尾再一次：

    …因此他是這樣開始的：「起初，上帝創造天
    — 金口若望
    地。」他幾乎是向我們眾人大聲呼喊著說…
    — 金口若望 《創世記講道集》

切點常常落在詞中間（「天」／「地」），所以正文直接相接、不加任何分隔。

判定條件（全部要成立才動）：
  1. 同一書卷／章／pericope，entry_order 相鄰
  2. 兩列 father_name 非空且相同
  3. 前半沒有 work_title、後半有   —— ACCS 的出處印在引文結尾
  4. 後半沒有 heading             —— 小標印在引文開頭
  5. 前半正文結尾不是句末標點      —— 話還沒說完

同一位教父在同一段有多則獨立引文是常態（各自有自己的出處），所以條件 3、4
是關鍵：兩則獨立引文會各自帶出處，不會一個有一個沒有。

預設 dry-run，要 --apply 才寫入。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

TABLE = 'accs_commentary'
BACKUP_DIR = Path('c:/tmp/accs_rows_backup')
ENDCH = set('。！？」』）.!?')


def fetch_all() -> list[dict]:
    cols = ('id,book_code,chapter,pericope_order,entry_order,section_kind,'
            'father_name,work_title,heading,body_zh')
    rows, off = [], 0
    while True:
        r = requests.get(
            f'{te.URL}/rest/v1/{TABLE}?select={cols}'
            f'&order=book_code,chapter,pericope_order,entry_order&offset={off}&limit=1000',
            headers=te.H_GET, timeout=120)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    return rows


def find_pairs(rows: list[dict]) -> list[tuple[dict, dict]]:
    out = []
    for a, b in zip(rows, rows[1:]):
        if a['section_kind'] != 'comment' or b['section_kind'] != 'comment':
            continue
        if (a['book_code'], a['chapter'], a['pericope_order']) != \
           (b['book_code'], b['chapter'], b['pericope_order']):
            continue
        if b['entry_order'] != a['entry_order'] + 1:
            continue
        fa = (a['father_name'] or '').strip()
        if not fa or fa != (b['father_name'] or '').strip():
            continue
        if (a['work_title'] or '').strip():
            continue
        if not (b['work_title'] or '').strip():
            continue
        if (b['heading'] or '').strip():
            continue
        tail = (a['body_zh'] or '').rstrip()
        if tail and tail[-1] in ENDCH:
            continue
        out.append((a, b))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--show', type=int, default=8)
    args = ap.parse_args()

    rows = fetch_all()
    pairs = find_pairs(rows)
    print(f'撈到 {len(rows)} 列；判定為「一則引文被切兩列」{len(pairs)} 對')

    from collections import Counter
    print('分布:', Counter(a['book_code'] for a, _ in pairs).most_common(10))
    print()
    for a, b in pairs[:args.show]:
        print(f"  {a['book_code']} {a['chapter']}:p{a['pericope_order']} "
              f"e{a['entry_order']}+e{b['entry_order']}  {a['father_name']} 《{b['work_title']}》")
        print(f"      …{(a['body_zh'] or '')[-26:]}‖{(b['body_zh'] or '')[:26]}…")
    if not pairs:
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'accs_split_quotes_before_{stamp}.jsonl'
    with backup.open('w', encoding='utf-8') as fh:
        for a, b in pairs:
            fh.write(json.dumps({'keep': a, 'merged_away': b}, ensure_ascii=False) + '\n')
    written = sum(1 for _ in backup.open(encoding='utf-8'))
    print(f'\n備份 → {backup}（{written} 對）')
    if written != len(pairs):
        print('✗ 備份筆數不符 → 中止')
        return 1

    if not args.apply:
        print('(dry-run；要合併請加 --apply)')
        return 0

    merged = 0
    for a, b in pairs:
        patch = {
            'body_zh': (a['body_zh'] or '') + (b['body_zh'] or ''),
            'work_title': b['work_title'],
        }
        r = requests.patch(f"{te.URL}/rest/v1/{TABLE}?id=eq.{a['id']}",
                           headers=te.H_JSON, json=patch, timeout=60)
        r.raise_for_status()
        r = requests.delete(f"{te.URL}/rest/v1/{TABLE}?id=eq.{b['id']}",
                            headers=te.H_JSON, timeout=60)
        r.raise_for_status()
        merged += 1
    print(f'已合併 {merged} 對（刪除 {merged} 列）')

    after = fetch_all()
    print(f'複查：總列數 {len(after)}（原 {len(rows)}，差 {len(rows) - len(after)}）；'
          f'殘留可合併 {len(find_pairs(after))} 對')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
