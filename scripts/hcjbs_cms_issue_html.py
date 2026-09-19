# -*- coding: utf-8 -*-
"""產生臺灣佛教研究中心站每期頁面的 HTML（**照模擬站版面**），以及首頁的封面牆。

版面＝模擬站 `pages/Hsuan_Chuang_Studies/issue/[n].vue`：左邊封面、右邊
篇名／作者／頁數／全文 四欄表格，全文是橘色 PDF 鈕，**全白底、無列底色**、
**不放「玄奘大學原始頁」連結**（那是模擬站才需要的外連）。

🚨 PDF 連結一律用**檔案庫實際檔名**：CMS 上傳時會把檔名裡的英文字母全轉小寫
   （`Loka…` → `loka…`），照本機檔名寫會 404。清單用
   `node scripts/hcu_cms_upload_files.mjs --list > filelist.txt` 產生。

用法：
    python -X utf8 scripts/hcjbs_cms_issue_html.py 44 45            # 各期頁
    python -X utf8 scripts/hcjbs_cms_issue_html.py --wall           # 首頁封面牆
"""
import argparse
import json
import re
from pathlib import Path

from hcjbs_cms_style import (FILES, cover_img, cover_url, esc, pdf_button, section_nav,
                             two_col, wrap)

PUB_DATE = {44: '2025.9', 45: '2026.3'}      # 學報自印的出版年月（上半年 3 月／下半年 9 月）
ZH = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


def zh_num(n):
    if n <= 10:
        return ZH[n]
    if n < 20:
        return '十' + (ZH[n % 10] if n % 10 else '')
    return ZH[n // 10] + '十' + (ZH[n % 10] if n % 10 else '')


def find_pdf(names, issue, seq, title_zh):
    want = f'{issue}-{seq}'
    cands = [n for n in names if n.startswith(want) and not re.match(rf'^{issue}-{seq}\d', n)]
    if len(cands) == 1:
        return cands[0]
    if not cands:
        return None
    key = re.sub(r'\W', '', title_zh)[:12]
    for n in cands:
        if key and key[:6] in re.sub(r'\W', '', n):
            return n
    return sorted(cands, key=len)[0]


CELL = 'border-bottom: 1px solid #eeeeee; padding: 14px 8px;'


def article_table(data, issue, names):
    rows = ['<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">',
            '\t<tr>',
            '\t\t<td style="border-bottom: 2px solid #333333; padding: 0 8px 8px; font-size: 13px; '
            'font-weight: bold; color: #666666;">篇名</td>',
            '\t\t<td width="110" style="border-bottom: 2px solid #333333; padding: 0 8px 8px; '
            'font-size: 13px; font-weight: bold; color: #666666;">作者</td>',
            '\t\t<td width="56" align="center" style="border-bottom: 2px solid #333333; padding: 0 8px 8px; '
            'font-size: 13px; font-weight: bold; color: #666666;">頁數</td>',
            '\t\t<td width="92" align="center" style="border-bottom: 2px solid #333333; padding: 0 8px 8px; '
            'font-size: 13px; font-weight: bold; color: #666666;">全文</td>',
            '\t</tr>']
    seq = 0
    for it in data['items']:
        if it['kind'] == 'section':
            rows += ['\t<tr>',
                     f'\t\t<td colspan="4" style="{CELL} padding-top: 20px; padding-bottom: 8px;">'
                     f'<span style="font-size: 16px; font-weight: bold; color: #111111;">❖ '
                     f'{esc(it["label"])}</span></td>',
                     '\t</tr>']
            continue
        seq += 1
        pdf = find_pdf(names, issue, seq, it['title_zh'])
        # 🚨 沒有 PDF 的篇目照樣列出來（有目無文），但不掛連結——
        #    掛一個連不到的連結比沒有連結更糟。
        full = pdf_button(FILES + pdf) if pdf else '<span style="font-size: 13px; color: #cccccc;">—</span>'
        en = (f'<br /><span style="font-size: 13px; color: #888888; line-height: 1.5;">'
              f'{esc(it["title_en"])}</span>') if it['title_en'] else ''
        rows += ['\t<tr>',
                 f'\t\t<td style="{CELL} font-size: 16px; color: #222222; line-height: 1.55;">'
                 f'{esc(it["title_zh"])}{en}</td>',
                 f'\t\t<td style="{CELL} font-size: 14px; color: #555555;">{esc(it["author"])}</td>',
                 f'\t\t<td align="center" style="{CELL} font-size: 14px; color: #777777;">{esc(it["page"])}</td>',
                 f'\t\t<td align="center" style="{CELL}">{full}</td>',
                 '\t</tr>']
    rows.append('</table>')
    if issue in PUB_DATE:
        rows.append(f'<p style="margin: 18px 0 0; font-size: 14px; color: #777777;">出版日期：'
                    f'{PUB_DATE[issue]}</p>')
    return '\n'.join(rows)


def issue_page(issue, data, names):
    # 🚨 這裡不要再印「第N期玄奘佛學研究學報」：CMS 的內容樣板已經把篇名與日期
    #    印在內容區上方了，我們再印一次就是同一個標題連著出現兩遍。
    return wrap(section_nav('研究學報') + '\n'
                + two_col(cover_img(issue), article_table(data, issue, names)))


def cover_wall(issue_links, per_row=5):
    """首頁封面牆：每列五張封面，圖下是「第N期」，點進該期頁面。"""
    cells = []
    for issue, url in issue_links:
        cells.append(
            f'\t\t<td width="{100 // per_row}%" align="center" valign="top" style="padding: 0 12px 30px;">\n'
            f'\t\t\t<a href="{url}" style="text-decoration: none; color: #333333;">'
            f'<img src="{cover_url(issue)}" alt="第{issue}期封面" width="100%" '
            f'style="width: 100%; border: 1px solid #e2e2e2; display: block;" /></a>\n'
            f'\t\t\t<div style="margin-top: 10px; font-size: 15px;">'
            f'<a href="{url}" style="text-decoration: none; color: #333333;">第{zh_num(issue)}期</a></div>\n'
            f'\t\t</td>')
    rows = []
    for i in range(0, len(cells), per_row):
        chunk = cells[i:i + per_row]
        while len(chunk) < per_row:
            chunk.append(f'\t\t<td width="{100 // per_row}%"></td>')
        rows.append('\t<tr>\n' + '\n'.join(chunk) + '\n\t</tr>')
    table = ('<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">\n'
             + '\n'.join(rows) + '\n</table>')
    # 🚨 這裡不要再加「玄奘佛學研究」標題：CMS 的清單樣板自己會印一次節點名稱，
    #    我們再印一次，畫面上同一個標題就連續出現兩遍。
    return wrap(section_nav('研究學報') + '\n' + table)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('issues', nargs='*', type=int)
    ap.add_argument('--harvest', default='c:/tmp/hcu-cms/issues-harvest.json')
    ap.add_argument('--filelist', default='c:/tmp/hcu-cms/filelist.txt')
    ap.add_argument('--links', default='c:/tmp/hcu-cms/issue-links.json',
                    help='{期號: 該期公開頁 URL}，封面牆要用')
    ap.add_argument('--wall', action='store_true')
    ap.add_argument('--out', default='c:/tmp/hcu-cms/out')
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.wall:
        links = json.loads(Path(args.links).read_text(encoding='utf-8'))
        pairs = sorted(((int(k), v) for k, v in links.items()), reverse=True)
        fp = out / 'cover-wall.html'
        fp.write_text(cover_wall(pairs), encoding='utf-8')
        print(f'封面牆 → {fp}  {len(pairs)} 期')
        return

    harvest = json.loads(Path(args.harvest).read_text(encoding='utf-8'))
    names = [l.strip() for l in Path(args.filelist).read_text(encoding='utf-8').splitlines() if l.strip()]
    for n in args.issues or [44, 45]:
        data = harvest.get(str(n)) or harvest.get(n)
        if not data:
            print(f'❌ harvest 裡沒有第 {n} 期')
            continue
        arts = [x for x in data['items'] if x['kind'] == 'article']
        fp = out / f'issue-{n}.html'
        fp.write_text(issue_page(n, data, names), encoding='utf-8')
        missing, seq = [], 0
        for it in data['items']:
            if it['kind'] != 'article':
                continue
            seq += 1
            if not find_pdf(names, n, seq, it['title_zh']):
                missing.append(f"{n}-{seq} {it['title_zh'][:26]}")
        print(f'第{n}期 → {fp}  篇數={len(arts)}  有PDF={len(arts) - len(missing)}  無PDF={len(missing)}')
        for m in missing:
            print(f'   ⚠ 無 PDF：{m}')


if __name__ == '__main__':
    main()
