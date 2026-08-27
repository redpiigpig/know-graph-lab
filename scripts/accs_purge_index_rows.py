"""刪掉混進 accs_commentary 的書末索引列（詞條＋頁碼被 OCR 成教父引文）。

規矩照 [[project_accs_scripture]]：
  分頁完整撈（PostgREST 預設只回 1000 列且不報錯）→ 備份 → 核對筆數 → 才刪。
預設 dry-run，要加 --apply 才真的動手。
"""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

TABLE = 'accs_commentary'
BACKUP_DIR = Path('c:/tmp/accs_rows_backup')

# 只用可靠訊號。刻意不用「body 太短」——實測會誤殺真的跨頁續行殘句
# （例 pro 13:1 body='食，惡人無以果腹。'）。
STROKE = re.compile(r'^[一二三四五六七八九十百]+劃$')
PAGEREF = re.compile(r'[,，]\s*(x{0,3}[ivx]+|\d{1,3})(\s*[-–,，]\s*\d{1,3})*$')


def is_index_row(x: dict) -> bool:
    if (x.get('father_name') or '').strip():
        return False                      # 有教父名就是真引文
    body = (x.get('body_zh') or '').strip()
    head = (x.get('heading') or '').strip()
    if STROKE.match(head):
        return True                       # 「十八劃」筆劃索引標題
    if re.fullmatch(r'[\d,，\s\-–]+', body):
        return True                       # body 只有頁碼
    if PAGEREF.search(body) and len(body) < 45:
        return True                       # 「敵基督和獸, 163, 205, 279」
    return False


def fetch_all() -> list[dict]:
    cols = ('id,book_code,chapter,verse_start,verse_end,pericope_order,entry_order,'
            'section_kind,heading,father_name,work_title,body_zh,source_vol')
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/{TABLE}?select={cols}&order=id&offset={off}&limit=1000',
                         headers=te.H_GET, timeout=120)
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

    rows = fetch_all()
    print(f'撈到 {len(rows)} 列（分頁完整撈）')

    doomed = [x for x in rows if x['section_kind'] == 'comment' and is_index_row(x)]
    print(f'判定為索引污染 {len(doomed)} 列')
    print('  分布:', Counter(x['book_code'] for x in doomed).most_common(10))

    if not doomed:
        print('沒有要刪的，結束')
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'accs_index_rows_{stamp}.jsonl'
    with backup.open('w', encoding='utf-8') as fh:
        for x in doomed:
            fh.write(json.dumps(x, ensure_ascii=False) + '\n')
    written = sum(1 for _ in backup.open(encoding='utf-8'))
    print(f'備份 → {backup}  寫入 {written} 列')
    if written != len(doomed):
        print(f'✗ 備份筆數不符（{written} != {len(doomed)}）→ 中止，不刪任何東西')
        return 1
    print('✓ 備份筆數相符')

    if not args.apply:
        print('\n(dry-run；要真的刪請加 --apply)')
        for x in doomed[:5]:
            print(f"    {x['book_code']} {x['chapter']}:{x['verse_start']} "
                  f"heading={x['heading']!r} body={x['body_zh'][:36]!r}")
        return 0

    ids = [x['id'] for x in doomed]
    deleted = 0
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        lst = ','.join(str(v) for v in chunk)
        r = requests.delete(f'{te.URL}/rest/v1/{TABLE}?id=in.({lst})',
                            headers={**te.H_JSON, 'Prefer': 'return=representation'}, timeout=120)
        r.raise_for_status()
        deleted += len(r.json())
    print(f'已刪 {deleted} 列')

    after = fetch_all()
    left = [x for x in after if x['section_kind'] == 'comment' and is_index_row(x)]
    print(f'刪後複查：總列數 {len(after)}（原 {len(rows)}，差 {len(rows) - len(after)}）；殘留索引列 {len(left)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
