# -*- coding: utf-8 -*-
"""簡報版面稽核：抓「字壓到字」「字太小」「文字掉出版面」。

把渲染好的 PDF 逐頁拆成文字行，檢查三件事：
  1. 重疊——兩行的方框交疊面積超過較小者的三成（在投影片上就是壓字）
  2. 過小——字級低於門檻（預設 11pt，投影用）
  3. 溢出——文字超出版面或壓到頁尾那一行

用法：python scripts/course_slides_audit.py [--min-size 11]
"""
import sys
from pathlib import Path

import fitz

DRIVE = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')
FOLDERS = ['115-1_世界宗教文化導論', '115-1_基督宗教概論', '宗教系國文講義']


def lines(page):
    out = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            txt = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not txt:
                continue
            size = max(sp['size'] for sp in ln['spans'])
            out.append((fitz.Rect(ln['bbox']), txt, size))
    return out


def overlap(a, b):
    r = a & b
    if r.is_empty:
        return 0.0
    small = min(a.get_area(), b.get_area()) or 1
    return r.get_area() / small


def audit(pdf, min_size):
    doc = fitz.open(pdf)
    bad = []
    for i, page in enumerate(doc):
        ls = lines(page)
        h, w = page.rect.height, page.rect.width
        for j, (r, t, s) in enumerate(ls):
            if s < min_size:
                bad.append((i + 1, f'字太小 {s:.1f}pt', t[:34]))
            if r.y1 > h - 6 or r.x1 > w - 4 or r.x0 < 4:
                bad.append((i + 1, '溢出版面', t[:34]))
            for r2, t2, _ in ls[j + 1:]:
                if overlap(r, r2) > 0.3:
                    bad.append((i + 1, '壓字', f'{t[:20]} ／ {t2[:20]}'))
    doc.close()
    return bad


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    min_size = float(args[args.index('--min-size') + 1]) if '--min-size' in args else 11.0
    total = 0
    for folder in FOLDERS:
        d = DRIVE / folder / '簡報'
        if not d.exists():
            continue
        print(f'── {folder}')
        for pdf in sorted(d.glob('第*.pdf')):
            bad = audit(pdf, min_size)
            total += len(bad)
            if bad:
                print(f'  ✘ {pdf.stem}　{len(bad)} 處')
                for pg, kind, txt in bad[:6]:
                    print(f'      p{pg:<3} {kind}　{txt}')
                if len(bad) > 6:
                    print(f'      ⋯⋯另有 {len(bad) - 6} 處')
            else:
                print(f'  ✔ {pdf.stem}')
    print(f'\n合計問題 {total} 處')
