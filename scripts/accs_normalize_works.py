#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""照對照表統一 accs_commentary 的作品名（work_title）。

同一部書在 ACCS 語料裡有多種寫法：書名號有無（《講道集》／講道集）、節號黏在
書名後（講道集 231.2）、異譯（註釋／注釋／詮釋）加上 OCR 錯字（請道集、書集集、
馬大福音註釋）。讀者會以為是不同的書，依作品篩選也全是破的。

體例＝`scripts/accs_work_titles.json`：正典寫法不帶書名號（書信集、講道集），
節號以半形空格接在書名之後。中文語料的變體對照收在該檔的 `_zh_canonical`。

分兩層，兩層都不猜：

  1. **機械規則**（本檔寫死，無須對照表）：剝掉外層書名號《》〈〉、全形轉半形、
     節號標點正規化。這一層是純排版差異，可逆、不改變任何字義。
  2. **對照表**（`_zh_canonical`，人工策展）：異譯與 OCR 錯字 → 正典書名。
     查不到的一律不碰，等人工補進對照表再重跑（本腳本可重複執行）。

🚨 絕不用字串相似度自動歸併。`馬可福音註釋` 與 `馬太福音註釋` 只差一個字，
   卻是兩卷不同的福音書；`詩篇註釋`／`詩篇詳解`／`詩篇短講集` 是三部不同的書。
   候選由 `--propose` 產生給人審，核可後才寫進 `_zh_canonical`。

🚨 書名絕不交給 LLM 翻譯（見 accs_ingest_epub.resolve_work 的註解）：短標題沒有
   上下文，模型會把它當成待續寫的開頭，實測會吐回一整段經文。查不到就保留原樣。

預設 dry-run，要 --apply 才寫入；寫入前一律先備份對照。
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

TABLE = 'accs_commentary'
MAP_PATH = Path(__file__).resolve().parent / 'accs_work_titles.json'
BACKUP_DIR = Path('c:/tmp/accs_rows_backup')

# 正文漏進書名欄的訊號：真書名不會有句末標點。這一類不是改名能解決的，
# 要另案修（見接手清單），本腳本一律跳過不碰。
SENTENCE = re.compile(r'[。！？]')

# 尾端節號：11.3 / 4.12 / 132.4-5 / 18.15-19, 22 / 2.3.15 及後
TAIL_SECT = re.compile(r'(?P<sect>[0-9][0-9.：:，,\-–\s]*(?:及後|以下)?)$')

# 🚨 只正規化「節號」裡的全形字元，書名本體一個字都不動。
# 中文書名的全形冒號是正確體例（保羅書信註釋：以弗所書），不是待統一的變體；
# 第一版把整串下去轉，1,218 列裡有 1,100 列是在把正確的「：」改成半形「:」。
FULLWIDTH_SECT = str.maketrans('０１２３４５６７８９．－　', '0123456789.- ')


def split_title(raw: str) -> tuple[str, str]:
    """拆成 (基底書名, 節號)。書名只做空白正規化，節號另外做全形轉半形。"""
    s = re.sub(r'[\s　]+', ' ', raw).strip()
    m = TAIL_SECT.search(s)
    sect = ''
    if m:
        # 只有在節號前面還有書名時才拆，否則整串就是內容，別拆壞。
        # 🚨 前一個字若是數字／英文／點，代表這個數字是節號的一部分而不是新節號的
        # 開頭（「講道集 28a.1」的 .1 不可切出來變成「28a. 1」）。
        head = s[:m.start()].strip()
        prev = s[m.start() - 1] if m.start() else ''
        if head and not (prev.isascii() and (prev.isalnum() or prev == '.')):
            sect = m.group('sect').translate(FULLWIDTH_SECT).strip().rstrip(',，')
            sect = re.sub(r'\s+', ' ', sect)
            s = head
    # 剝掉成對的外層書名號，可能有多層
    for _ in range(3):
        t = s.strip()
        if len(t) > 2 and ((t[0] == '《' and t[-1] == '》') or (t[0] == '〈' and t[-1] == '〉')):
            s = t[1:-1]
        else:
            break
    return s.strip(), sect


def canonical(raw: str, table: dict) -> tuple[str, str]:
    """回傳 (正規化後的完整書名, 判定依據)。"""
    base, sect = split_title(raw)
    if not base:
        return raw, 'blank'
    mapped = table.get(base)
    rebuilt = (mapped or base) + (' ' + sect if sect else '')
    if mapped:
        how = 'map'
    elif rebuilt != raw:
        how = 'rule'
    else:
        how = 'same'
    return rebuilt, how


def fetch_rows() -> list:
    """🚨 PostgREST 預設只回 1000 列且不報錯 —— 一定要分頁，否則備份會缺列。"""
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/{TABLE}?select=id,book_code,work_title,section_kind'
                         f'&order=id&offset={off}&limit=1000', headers=te.H_GET, timeout=120)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    return rows


def propose(rows: list) -> list:
    """保守地列出疑似 OCR 錯字：同長、只差一字、高頻方 ≥ 低頻方 5 倍。

    **只列不改。** 差一字仍可能是兩部不同的書（馬太／馬可、詩篇註釋／詩篇詮釋）。
    """
    counts = Counter()
    for x in rows:
        cur = (x.get('work_title') or '').strip()
        if cur and not SENTENCE.search(cur):
            counts[split_title(cur)[0]] += 1
    by_len = defaultdict(list)
    for b, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if b:
            by_len[len(b)].append((b, n))
    out = []
    for group in by_len.values():
        for i, (a, na) in enumerate(group):
            for b, nb in group[i + 1:]:
                d = [k for k, (x, y) in enumerate(zip(a, b)) if x != y]
                if len(d) == 1 and na >= nb * 5:
                    out.append({'keep': a, 'keep_rows': na, 'suspect': b,
                                'suspect_rows': nb, 'pos': d[0],
                                'keep_char': a[d[0]], 'suspect_char': b[d[0]]})
    return sorted(out, key=lambda r: -r['keep_rows'])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='真的寫入（預設只試跑）')
    ap.add_argument('--propose', action='store_true',
                    help='產生疑似 OCR 錯字候選給人審，不寫入資料表')
    args = ap.parse_args()

    raw_map = json.loads(MAP_PATH.read_text(encoding='utf-8'))
    table = raw_map.get('_zh_canonical', {})
    rows = fetch_rows()
    print(f'對照表 {len(table)} 條；{TABLE} {len(rows)} 列')

    todo = defaultdict(list)
    skipped_body = Counter()
    unresolved = Counter()
    for x in rows:
        cur = (x.get('work_title') or '').strip()
        if not cur:
            continue
        if SENTENCE.search(cur):
            skipped_body[cur] += 1          # 正文污染，另案處理
            continue
        new, how = canonical(cur, table)
        if how == 'same':
            unresolved[cur] += 1
        if new != cur:
            todo[(cur, new)].append(x['id'])

    n_rows = sum(len(v) for v in todo.values())
    print(f'\n要改寫 {len(todo)} 種寫法 / {n_rows} 列')
    for (cur, new), ids in sorted(todo.items(), key=lambda kv: -len(kv[1]))[:30]:
        print(f'   {len(ids):5d}  {cur!r}  →  {new!r}')
    if len(todo) > 30:
        print(f'   …另外 {len(todo) - 30} 種')

    print(f'\n正文漏進書名欄、本腳本跳過不碰: '
          f'{len(skipped_body)} 種 / {sum(skipped_body.values())} 列')
    print(f'已是正規寫法或對照表查不到、維持原樣: '
          f'{len(unresolved)} 種 / {sum(unresolved.values())} 列')

    if args.propose:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        props = propose(rows)
        out = BACKUP_DIR / 'work_title_proposals.json'
        out.write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'\n疑似錯字候選 {len(props)} 組 → {out}（**待人工核可**，未套用）')
        return 0

    if not todo:
        print('\n沒有要改的。')
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'accs_work_rename_{stamp}.jsonl'
    with backup.open('w', encoding='utf-8') as fh:
        for (cur, new), ids in todo.items():
            fh.write(json.dumps({'from': cur, 'to': new, 'ids': ids},
                                ensure_ascii=False) + '\n')
    print(f'\n備份對照 → {backup}（{len(todo)} 組 / {n_rows} 列）')

    if not args.apply:
        print('(dry-run；要寫入請加 --apply)')
        return 0

    changed = 0
    for (cur, new), ids in todo.items():
        for i in range(0, len(ids), 100):
            chunk = ','.join(str(v) for v in ids[i:i + 100])
            r = requests.patch(f'{te.URL}/rest/v1/{TABLE}?id=in.({chunk})',
                               headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                               json={'work_title': new}, timeout=120)
            r.raise_for_status()
            changed += len(ids[i:i + 100])
    print(f'已改寫 {changed} 列')

    after = fetch_rows()
    left = 0
    for x in after:
        cur = (x.get('work_title') or '').strip()
        if cur and not SENTENCE.search(cur) and canonical(cur, table)[0] != cur:
            left += 1
    print(f'複查（冪等性）：再跑一次還會變動 {left} 列')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
