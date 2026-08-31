#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修 accs_commentary 裡「正文漏進 work_title 欄」的 210 列。

第四類「不會報錯只會靜靜地錯」的資料錯誤（前三類見 accs_purge_index_rows.py、
accs_merge_split_quotes.py、accs_recover_inline_fathers.py）。OCR 把一整段正文
放進了出處欄，網站上那一則的出處就顯示成幾百字的經文。

🚨 判定訊號用**句末標點**（。！？）而不是長度。
   `書信集：致在幼發拉底河、奧斯利那地區、敘利亞和腓利基者` 是 26 字的真書名，
   拿長度當門檻會把它誤殺——跟 accs_purge_index_rows 不可加「body 太短」同一個道理。

🚨 不可「字串裡有《》就抽出來當書名」。
   `亞哈隨魯──《七十士譯本》稱作亞達薛西` 的《七十士譯本》是正文提到的譯本，
   不是這一則的出處。ACCS 的體例是**引文以《作品》收尾**，所以只認結尾的《》。

修法按可修復性分級，**只動逐列查證過安全的**：

  A1  結尾有《書名》，且前面那段正文已經在 body_zh 裡 → 清成書名。 安全
  C   整段與 body_zh 重複                            → 清空。     安全
  E   body_zh 整格只是一個《書名》、work_title 裝著整段正文
      → **兩欄對調**。兩個值都保留只是換位，不丟任何資料，最安全的一種。
  ── 以下一律不碰，等人工判讀 ──
  A2  結尾有《書名》，但前段不在 body_zh → 清掉會掉這段字
  B   《》出現在句中而非結尾           → 抽出來會配錯出處
  D   其餘：沒有書名、內容也不在 body_zh

🚨 D 那一批**不是**批次邊界切開的引文續行。第一版憑印象這樣寫進交接文件，
   實測後推翻了：拿「開頭像續行 ＋ 前一列 body 未收尾 ＋ 同章」三個條件去比對，
   命中 0 列。真正的病根是欄位錯位（E 那類就是它的可解子集）。
   別再照「續行」的方向去修這批。

預設 dry-run，要 --apply 才寫入；寫入前一律先把原值備份成 jsonl。
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

SENTENCE = re.compile(r'[。！？]')
END_TITLE = re.compile(r'《([^》]{2,30})》\s*[0-9.\-–,，:：\s]*$')
ANY_TITLE = re.compile(r'《([^》]{2,30})》')
# body_zh 整格就只是一個《書名》→ 這一列的兩欄是對調的
PURE_TITLE = re.compile(r'^\s*《([^》]{2,40})》\s*([0-9.\-–,，:：\s]*)$')

# 前段要比對多少字才算「已經在 body 裡」。取尾端 25 字：夠長到不會誤中，
# 又短到不會因為一兩個 OCR 錯字就整段對不上。
PROBE = 25


def fetch_rows() -> list:
    """🚨 PostgREST 預設只回 1000 列且不報錯 —— 一定要分頁，否則備份會缺列。"""
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/{TABLE}'
                         f'?select=id,book_code,chapter,father_name,work_title,body_zh'
                         f'&order=id&offset={off}&limit=1000', headers=te.H_GET, timeout=120)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    return rows


def classify(x: dict) -> tuple:
    """回傳 (級別, patch dict or None)。patch 為 None 代表本腳本不處理。"""
    wt = (x.get('work_title') or '').strip()
    body = (x.get('body_zh') or '')
    m = END_TITLE.search(wt)
    if m:
        lead = wt[:m.start()].strip()
        title = m.group(1).strip()
        # 節號跟在《》之後，保留
        sect = wt[m.end(1) + 1:].strip()
        new = (title + (' ' + sect if sect else '')).strip()
        if not lead:
            return 'A0 只有書名', {'work_title': new}
        probe = lead[-PROBE:] if len(lead) >= PROBE else lead
        if probe and probe in body:
            return 'A1 前段已在 body', {'work_title': new}
        return 'A2 前段不在 body（不碰）', None
    if ANY_TITLE.search(wt):
        return 'B 《》在句中（不碰）', None
    probe = wt[:20]
    if probe and probe in body:
        return 'C 與 body 重複', {'work_title': ''}
    # E：兩欄對調。body_zh 整格只是一個《書名》，而 work_title 裝著整段正文。
    # 網站上會顯示成「出處＝幾百字經文、正文＝一個書名」。
    # 對調不丟任何資料（兩個值都保留、只是換位），所以是最安全的一種修法。
    ms = PURE_TITLE.match(body.strip())
    if ms and len(wt) > 25:
        title = ms.group(1).strip()
        sect = (ms.group(2) or '').strip()
        return 'E 兩欄對調', {'work_title': (title + (' ' + sect if sect else '')).strip(),
                               'body_zh': wt}
    return 'D 內容不在 body（不碰）', None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--dump', action='store_true',
                    help='把需要人工判讀的三類寫成檔案供審閱')
    args = ap.parse_args()

    rows = fetch_rows()
    bad = [x for x in rows
           if (x.get('work_title') or '').strip() and SENTENCE.search(x['work_title'])]
    print(f'{TABLE} {len(rows)} 列；正文污染 {len(bad)} 列')

    tiers = Counter()
    todo, manual = [], []
    for x in bad:
        tier, patch = classify(x)
        tiers[tier] += 1
        if patch is None:
            manual.append((tier, x))
        else:
            todo.append((tier, x, patch))

    print('\n=== 分級 ===')
    for k, v in sorted(tiers.items()):
        print(f'   {v:4d}  {k}')

    print(f'\n本腳本要修 {len(todo)} 列；留給人工 {len(manual)} 列')
    print('\n=== 要修的前 15 列 ===')
    for tier, x, patch in todo[:15]:
        old = x['work_title'].strip()
        shown = (old[:38] + '…') if len(old) > 38 else old
        print(f'   [{tier[:2]}] {x["book_code"]} {x["chapter"]}  {shown!r}')
        wt = patch.get('work_title')
        print(f'          出處 → {wt!r}' if wt else '          出處 → (清空)')
        if 'body_zh' in patch:
            print(f'          正文 → {patch["body_zh"][:38]!r}…  (兩欄對調)')

    if args.dump:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        out = BACKUP_DIR / 'worktitle_bleed_manual.json'
        out.write_text(json.dumps(
            [{'tier': t, 'id': x['id'], 'book': x['book_code'], 'chapter': x['chapter'],
              'father': x.get('father_name'), 'work_title': x['work_title'],
              'body_head': (x.get('body_zh') or '')[:200]} for t, x in manual],
            ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'\n待人工判讀 {len(manual)} 列 → {out}')
        return 0

    if not todo:
        print('\n沒有要修的。')
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'accs_worktitle_bleed_{stamp}.jsonl'
    with backup.open('w', encoding='utf-8') as fh:
        for tier, x, patch in todo:
            # 🚨 兩欄對調要把 body_zh 的原值也記下來，否則回復不了
            fh.write(json.dumps({'id': x['id'], 'tier': tier,
                                 'from_work_title': x.get('work_title'),
                                 'from_body_zh': x.get('body_zh'),
                                 'patch': patch}, ensure_ascii=False) + '\n')
    print(f'\n備份原值 → {backup}（{len(todo)} 列）')

    if not args.apply:
        print('(dry-run；要寫入請加 --apply)')
        return 0

    changed = 0
    for tier, x, patch in todo:
        r = requests.patch(f'{te.URL}/rest/v1/{TABLE}?id=eq.{x["id"]}',
                           headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                           json=patch, timeout=60)
        r.raise_for_status()
        changed += 1
    print(f'已修 {changed} 列')

    after = fetch_rows()
    left = sum(1 for x in after
               if (x.get('work_title') or '').strip() and SENTENCE.search(x['work_title']))
    print(f'複查：仍有正文污染 {left} 列（應等於留給人工的 {len(manual)} 列）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
