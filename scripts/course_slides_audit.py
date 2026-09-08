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

# 預設稽核「最終版」那幾夾——PDF 出在那裡（知識圖工作室只留 pptx）。
# 也可以在命令列直接給資料夾路徑。
FINAL = Path(r'G:\我的雲端硬碟\玄奘\博一上\教學')
DEFAULT_DIRS = [FINAL / '115-1 世界宗教文化導論' / '簡報',
                FINAL / '115-1世界宗教文化導論（假日）',
                FINAL / '115-1 基督宗教概論' / '簡報',
                FINAL / '115-1 宗教系國文' / '簡報']


def lines(page):
    """回傳 (方框, 文字, 字級, 所屬文字框序號)。

    🚨 同一個文字框裡上下相鄰的兩行，光是行高互相探進去就會被判成壓字
    （字級不同時特別明顯）。真正的壓字是**兩個文字框**疊在一起，
    所以帶著 block 序號，只比對不同框。
    """
    out = []
    for bi, blk in enumerate(page.get_text('dict')['blocks']):
        for ln in blk.get('lines', []):
            txt = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not txt:
                continue
            size = max(sp['size'] for sp in ln['spans'])
            out.append((fitz.Rect(ln['bbox']), txt, size, bi))
    return out


def overlap(a, b):
    """兩行是不是真的疊在一起。

    🚨 只看「交疊面積佔較小者幾成」會大量誤判：短行（像「▍ 神聖」）跟上下
    相鄰的大字行，光是行高互相探進去就足以超過三成。2026-09-09 就是這樣
    報了 16 處壓字，實測內文底部其實都還在框內兩公分以上。
    所以**面積與垂直方向都要疊到**才算。
    """
    r = a & b
    if r.is_empty:
        return 0.0
    small = min(a.get_area(), b.get_area()) or 1
    vh = min(a.height, b.height) or 1
    return min(r.get_area() / small, r.height / vh)


def images(page):
    """回傳頁面上每張圖的方框。跑版的圖多半是超出版面或壓在字上。"""
    out = []
    for info in page.get_image_info():
        r = fitz.Rect(info['bbox'])
        if r.get_area() > 4:
            out.append(r)
    return out


def audit(pdf, min_size):
    doc = fitz.open(pdf)
    bad = []
    for i, page in enumerate(doc):
        ls = lines(page)
        h, w = page.rect.height, page.rect.width
        for r in images(page):
            if r.y1 > h + 1 or r.x1 > w + 1 or r.x0 < -1 or r.y0 < -1:
                bad.append((i + 1, '圖超出版面', f'{r.width:.0f}×{r.height:.0f}'))
            for r2, t2, _s2, _b in ls:
                # 只抓真的壓在圖上的字；圖說本來就會貼著圖，所以門檻抓高一點
                if overlap(r2, r) > 0.5:
                    bad.append((i + 1, '圖壓字', t2[:26]))
        # 頁尾那一行：小字、靠頁底。內文壓到它就是跑版。
        foot = min((r.y0 for r, t, s, _b in ls if s < 15 and r.y0 > h * 0.87), default=h)
        for j, (r, t, s, bi) in enumerate(ls):
            if s < min_size:
                bad.append((i + 1, f'字太小 {s:.1f}pt', t[:34]))
            if r.y1 > h - 6 or r.x1 > w - 4 or r.x0 < 4:
                bad.append((i + 1, '溢出版面', t[:34]))
            elif s >= 15 and r.y1 > foot + 2:
                bad.append((i + 1, '壓到頁尾', t[:34]))
            for r2, t2, _s2, bj in ls[j + 1:]:
                if bj != bi and overlap(r, r2) > 0.3:
                    bad.append((i + 1, '壓字', f'{t[:20]} ／ {t2[:20]}'))
    doc.close()
    return bad


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    min_size = float(args[args.index('--min-size') + 1]) if '--min-size' in args else 11.0
    dirs = [Path(a) for a in args if not a.startswith('--') and Path(a).is_dir()]
    total = 0
    for d in (dirs or DEFAULT_DIRS):
        if not d.exists():
            continue
        print(f'── {d.name}')
        for pdf in sorted(d.glob('*.pdf')):
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
