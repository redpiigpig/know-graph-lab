#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「教父名寫在正文裡」的無署名引文補回 father_name。

背景：跨批次邊界的引文常被切成兩半，後半沒有署名。多數情況名字在前一頁、
救不回來（見 [[project_accs_scripture]]）。但有一小批的名字其實**字面上就在
正文開頭**，只是 OCR 沒把它抽到 father 欄：

    「安波羅修註釋者：保羅說他寧願死……」
    「食物必成為虛無亞歷山大的革利免：我們必須控制肚腹……」
                     ^^^^^^^^^^^^ 名字   ^^^^ 冒號後才是正文
    （前面那截「食物必成為虛無」是被併進來的小標）

這種有憑有據——名字在文本裡，不是從鄰居推論的。只補這一種；其餘一律不動，
因為在教父註釋裡安錯名字比留空白嚴重得多。

比對用的名字表取自語料自身既有的 father_name（不另建清單，避免與
[[feedback_glossary_strict_authority]] 的定名衝突），長名優先避免部分匹配。

預設 dry-run，要 --apply 才寫入。可重複執行（只挑 father_name 仍為空的列），
所以日後若從 raw JSONL 重建，再跑一次即可。
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
MAX_NAME_OFFSET = 60      # 名字要出現在正文開頭附近，才可能是署名而非內文提及
COLONS = ('：', ':')


def fetch_all() -> list[dict]:
    cols = ('id,book_code,chapter,verse_start,section_kind,heading,'
            'father_name,work_title,body_zh')
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


# 語料自帶的 father_name 本身含錯字（「失明者獲地模」）、作品名（「保羅書信註釋」）
# 與碎片（「油」「保羅說」「多模」）。直接拿來比對會把這些垃圾寫成署名，比留空白更糟。
# 因此只採信「反覆出現過的、像人名的」值。
MIN_NAME_USES = 5          # 在語料裡至少當過 5 次署名，濾掉一次性的錯字與碎片
MIN_NAME_LEN = 3           # 兩字以下多半是被切斷的殘名
WORKISH = ('註釋', '作品', '斷片', '講道集', '書信集', '選集', '集萃', '《', '》')
NOT_A_NAME = ('保羅說', '使徒', '經文', '先知')


def known_names(rows: list[dict]) -> list[str]:
    from collections import Counter
    uses = Counter((x['father_name'] or '').strip() for x in rows)
    uses.pop('', None)
    good = [n for n, c in uses.items()
            if c >= MIN_NAME_USES and len(n) >= MIN_NAME_LEN
            and not any(w in n for w in WORKISH)
            and not any(w in n for w in NOT_A_NAME)]
    return sorted(good, key=len, reverse=True)   # 長名優先：「敘利亞人以法蓮」勝過「以法蓮」


# 名字前面必須是開頭，或是明確的分隔符——否則可能正把一個更長的名字攔腰切斷
# （「亞歷山大的革利免」被切成「革利免」、「大巴西流」被切成「巴西流」）。
BOUNDARY = set('◆◊·、。！？；：」』）(）【】 　')
MIN_BODY_AFTER = 20        # 冒號後太短就不是引文


def find_inline(body: str, names: list[str]):
    """回傳 (教父名, 名字前的殘餘小標, 冒號後的正文) 或 None。"""
    for name in names:
        for colon in COLONS:
            i = body.find(name + colon)
            if not (0 <= i <= MAX_NAME_OFFSET):
                continue
            if i > 0 and body[i - 1] not in BOUNDARY:
                continue          # 名字被更長的名字包住，跳過
            rest = body[i + len(name) + len(colon):].strip()
            if len(rest) < MIN_BODY_AFTER:
                continue
            return name, body[:i].strip(), rest
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    rows = fetch_all()
    names = known_names(rows)
    print(f'撈到 {len(rows)} 列；語料自帶教父名 {len(names)} 種')

    fixes = []
    for x in rows:
        if x['section_kind'] != 'comment' or (x['father_name'] or '').strip():
            continue
        got = find_inline((x['body_zh'] or '').strip(), names)
        if not got:
            continue
        name, lead, rest = got
        if not rest:
            continue                       # 冒號後沒東西就不是引文，跳過
        patch = {'father_name': name, 'body_zh': rest}
        if lead and not (x['heading'] or '').strip():
            patch['heading'] = lead        # 被併進正文的小標，還給 heading
        fixes.append((x, patch))

    print(f'可補 {len(fixes)} 列\n')
    for x, p in fixes:
        print(f"  {x['book_code']:4s} {x['chapter']:>3}:{x['verse_start']:<3} → {p['father_name']}"
              f"{'   [小標 ' + p['heading'] + ']' if 'heading' in p else ''}")
        print(f"      原: {x['body_zh'][:58]}")
        print(f"      新: {p['body_zh'][:58]}")
    if not fixes:
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'accs_inline_father_before_{stamp}.jsonl'
    with backup.open('w', encoding='utf-8') as fh:
        for x, _ in fixes:
            fh.write(json.dumps(x, ensure_ascii=False) + '\n')
    written = sum(1 for _ in backup.open(encoding='utf-8'))
    print(f'\n備份原始列 → {backup}（{written} 列）')
    if written != len(fixes):
        print('✗ 備份筆數不符 → 中止')
        return 1

    if not args.apply:
        print('(dry-run；要寫入請加 --apply)')
        return 0

    done = 0
    for x, p in fixes:
        r = requests.patch(f"{te.URL}/rest/v1/{TABLE}?id=eq.{x['id']}",
                           headers=te.H_JSON, json=p, timeout=60)
        r.raise_for_status()
        done += 1
    print(f'已更新 {done} 列')

    after = fetch_all()
    still = sum(1 for x in after
                if x['section_kind'] == 'comment' and not (x['father_name'] or '').strip())
    print(f'複查：comment 無署名 {still} 列')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
