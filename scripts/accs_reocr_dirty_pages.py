#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重跑「OCR 當時就把正文吐進 work 欄」的那些頁。

`accs_fix_worktitle_bleed.py` 能救的都救完了，剩下的 93 列救不回來——不是 parser
的錯：逐筆比對原始 OCR，**94 列裡有 87 列在 raw jsonl 裡就已經是壞的**，OCR 當時
就把整段正文放進了 `work` 欄。而且壞法不一致（有時真書名躲在 body 結尾、有時 body
裝的是該段的總論、有時整段文字根本沒落地），沒有任何機械規則能可靠還原。
只能回 PDF 重跑那幾頁。

作法（逐書卷）：
  1. 從 checkpoint 移除那幾頁的行（先備份到 c:/tmp/accs_reocr_backup/）
  2. `ingest_accs_genesis.py --resume --pages a-b`，只有被移除的頁會重跑
  3. 全部跑完後**務必**重跑三支冪等修正腳本（見 --help 說明）

🚨 **絕不可加 `--replace`**：那會 `delete_book_rows(book)` 把整卷刪掉，再用這幾頁
   的結果覆蓋。以賽亞書會從 2,329 列變成剩幾十列。

🚨 **`--source-vol` 一定要沿用該書卷現有的值**。upsert 會把整卷的列一起寫回，
   傳錯就等於把整卷的 source_vol 悄悄改掉（各卷體例不一：有的是「ACCS（以賽亞書）」
   有的是「ACCS（1co）」）。本腳本一律先查 DB 現值再帶入。

🚨 **重跑後我的三支修正會被 raw 覆蓋回去**（實測：1ch 有一列 tier C 修好的又變回
   髒的）。這正是那三支寫成冪等的理由——跑完再跑一次就好：
     python -X utf8 scripts/accs_normalize_fathers.py --apply
     python -X utf8 scripts/accs_normalize_works.py   --apply
     python -X utf8 scripts/accs_fix_worktitle_bleed.py --apply

預設 dry-run，只印計畫不動任何東西。
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

RAW_DIR = Path('c:/tmp')
BACKUP_DIR = Path('c:/tmp/accs_reocr_backup')
PDF_DIR = Path('G:/我的雲端硬碟/資料/知識圖工作室/經典對照與註釋/'
               '基督教 - IVP - 古代基督信仰聖經註釋叢書')
SENTENCE = re.compile(r'[。！？]')


def db_broken_headings() -> dict:
    """目前資料表裡仍污染的列 → {book_code: {heading, ...}}。

    只重跑「還壞著」的那些頁，而不是所有 raw 裡 work 欄髒掉的頁。兩者差很多
    （354 頁 vs 約 140 頁）：raw 髒但 DB 已被 A1/C/E 三類修好的列不必再動，
    重跑反而會把修好的覆蓋回髒的、還多花一倍的 OCR。
    """
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/accs_commentary'
                         f'?select=book_code,heading,work_title&order=id'
                         f'&offset={off}&limit=1000', headers=te.H_GET, timeout=120)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    out = {}
    for x in rows:
        w = (x.get('work_title') or '').strip()
        if w and SENTENCE.search(w):
            out.setdefault(x['book_code'], set()).add((x.get('heading') or '').strip())
    return out


def dirty_pages(all_raw: bool = False) -> dict:
    """回傳 {raw 檔名: [要重跑的頁]}。

    預設只挑「raw 的 work 髒 **且** 該 entry 對應的 DB 列現在仍污染」的頁；
    `--all-raw` 才回全部 raw 髒頁。
    """
    broken = {} if all_raw else db_broken_headings()
    out = {}
    for f in sorted(RAW_DIR.glob('accs_*.raw.jsonl')):
        book = f.name.split('_', 2)[1]
        if not all_raw and book not in broken:
            continue
        pages = set()
        for line in f.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            for e in d.get('entries', []):
                if not SENTENCE.search(e.get('work') or ''):
                    continue
                if all_raw or (e.get('heading') or '').strip() in broken[book]:
                    pages.update(d.get('pages') or ([d['page']] if 'page' in d else []))
                    break
        if pages:
            out[f.name] = sorted(pages)
    return out


def source_vol_of(book: str) -> str | None:
    """該書卷現有的 source_vol（取眾數）。查不到就回 None，呼叫端跳過。"""
    r = requests.get(f'{te.URL}/rest/v1/accs_commentary'
                     f'?select=source_vol&book_code=eq.{book}&limit=1000',
                     headers=te.H_GET, timeout=60)
    r.raise_for_status()
    c = Counter((x.get('source_vol') or '') for x in r.json())
    return c.most_common(1)[0][0] if c else None


def strip_pages(path: Path, pages: set) -> int:
    """把含這些頁的行從 checkpoint 移除，回傳移除行數。先備份。"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    bak = BACKUP_DIR / path.name
    if not bak.exists():
        shutil.copy2(path, bak)
    keep, removed = [], 0
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            keep.append(line)
            continue
        pg = set(d.get('pages') or ([d['page']] if 'page' in d else []))
        if pg & pages:
            removed += 1
        else:
            keep.append(line)
    path.write_text('\n'.join(keep) + '\n', encoding='utf-8')
    # .done 也要清掉，否則排程會以為這卷已完成
    done = path.with_suffix('.done')
    if done.exists():
        done.unlink()
    return removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--engine', default='sonnet', choices=['gemini', 'sonnet', 'haiku'])
    ap.add_argument('--only', help='只處理此 book_code')
    ap.add_argument('--all-raw', action='store_true',
                    help='重跑所有 raw 髒頁（預設只跑 DB 仍污染的那些）')
    args = ap.parse_args()

    plan = dirty_pages(all_raw=args.all_raw)
    print(f'髒頁分布：{len(plan)} 個 raw 檔 / {sum(len(v) for v in plan.values())} 頁\n')

    jobs = []
    for name, pages in sorted(plan.items(), key=lambda kv: -len(kv[1])):
        book = name.split('_', 2)[1]
        if args.only and book != args.only:
            continue
        pdf_stem = name.split('_', 2)[2].replace('.raw.jsonl', '')
        pdf = PDF_DIR / f'{pdf_stem}.pdf'
        sv = source_vol_of(book)
        ok = pdf.exists() and sv is not None
        print(f'{"✓" if ok else "✗"} {book:5s} {len(pages):3d} 頁  {pdf_stem[:38]:38s} '
              f'source_vol={sv!r}')
        if not pdf.exists():
            print(f'      ✗ PDF 不存在：{pdf}')
        if sv is None:
            print(f'      ✗ DB 查不到 source_vol，跳過')
        if ok:
            jobs.append((book, pdf, pages, sv, RAW_DIR / name))

    print(f'\n可執行 {len(jobs)} 卷 / {sum(len(p) for _, _, p, _, _ in jobs)} 頁')
    if not args.apply:
        print('(dry-run；要執行請加 --apply)')
        return 0

    strikes = 0
    for book, pdf, pages, sv, ckpt in jobs:
        removed = strip_pages(ckpt, set(pages))
        lo, hi = min(pages), max(pages)
        print(f'\n=== {book}  移除 {removed} 行  重跑 {len(pages)} 頁 ({lo}-{hi}) ===',
              flush=True)
        cmd = [sys.executable, '-X', 'utf8', 'scripts/ingest_accs_genesis.py',
               '--pdf', str(pdf), '--book', book, '--pages', f'{lo}-{hi}',
               '--source-vol', sv, '--engine', args.engine, '--batch', '2', '--resume']
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            strikes += 1
            print(f'  [rc={rc}] 第 {strikes} 次失敗', flush=True)
            # 連續兩次才停整批（見 [[feedback_ocr_two_strike_quota]]）
            if strikes >= 2:
                print('  [bail] 連續兩卷失敗，停止', flush=True)
                break
        else:
            strikes = 0

    print('\n🚨 跑完務必重跑三支冪等修正（raw 會把它們覆蓋回去）：')
    print('   python -X utf8 scripts/accs_normalize_fathers.py   --apply')
    print('   python -X utf8 scripts/accs_normalize_works.py     --apply')
    print('   python -X utf8 scripts/accs_fix_worktitle_bleed.py --apply')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
