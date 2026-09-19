# -*- coding: utf-8 -*-
"""把 hcjbs_issue_harvest.py 取下的篇目，產生「臺灣佛教研究中心」站每期頁面的 HTML。

版面完全照該站既有各期（以第四十三期為範本）：三欄表格（篇名／作者／頁數）、
專輯以 ❖ 整列分隔、單數篇淺藍底 #DBE5F1、**中文標楷體／英文與數字 Times New Roman**、
末尾一列「出版日期」。

🚨 PDF 連結一律用**檔案庫實際檔名**：CMS 上傳時會把檔名裡的英文字母全轉小寫
   （`Loka…` → `loka…`），照本機檔名寫會 404。檔名清單用
   `node scripts/hcu_cms_upload_files.mjs --list` 取得，存成 filelist.txt 餵進來。

用法：
    python -X utf8 scripts/hcjbs_cms_issue_html.py 44 45 \
        --filelist c:/tmp/hcu-cms/filelist.txt --out c:/tmp/hcu-cms/out
"""
import argparse
import html
import json
import re
from pathlib import Path

RID = '436650DB9FC648D783CDF0FEAACE0321'
PREFIX = f'/upload/userfiles/{RID}/files/'
KAI = 'font-family: 標楷體; color: black'
TNR = "font-family: 'Times New Roman',serif; color: black"

# 每期的出版日期（學報自印的那個，非上網日期）：上半年 3 月、下半年 9 月。
PUB_DATE = {44: '2025.9', 45: '2026.3'}

TD_TITLE = ('width: 404.0pt; border-left: 1.0pt dotted lightgrey; border-right: medium none; '
            'border-top: medium none; border-bottom: medium none; padding-left: .75pt; '
            'padding-right: .75pt; padding-top: .75pt; padding-bottom: 0cm')
TD_AUTHOR = ('width: 3.0cm; border-left: medium none; border-right: medium none; '
             'border-top: medium none; border-bottom: 1.0pt dotted lightgrey; padding-left: .75pt; '
             'padding-right: .75pt; padding-top: .75pt; padding-bottom: 0cm')
TD_PAGE = ('width: 77.95pt; border-left: medium none; border-right: 1.0pt dotted lightgrey; '
           'border-top: medium none; border-bottom: 1.0pt dotted lightgrey; padding-left: .75pt; '
           'padding-right: .75pt; padding-top: .75pt; padding-bottom: 0cm')
TD_HEAD = ('border: none; border-bottom: solid #548DD4 1.5pt; padding: .75pt .75pt 0cm .75pt')
TD_SECTION = ('width: 20.0cm; border-left: medium none; border-right: medium none; '
              'border-top: medium none; border-bottom: 1.0pt dotted lightgrey; '
              'padding-left: .75pt; padding-right: .75pt; padding-top: .75pt; padding-bottom: 0cm')


def esc(s):
    return html.escape(s, quote=False)


def find_pdf(names, issue, seq, title_zh):
    """在檔案庫檔名清單裡找這一篇的 PDF（比對 `<期>-<序號>` 前綴）。"""
    want = f'{issue}-{seq}'
    cands = [n for n in names if n.startswith(want) and not re.match(rf'^{issue}-{seq}\d', n)]
    if len(cands) == 1:
        return cands[0]
    if not cands:
        return None
    # 多個候選時取與篇名最相近的那個
    key = re.sub(r'\W', '', title_zh)[:12]
    for n in cands:
        if key and key[:6] in re.sub(r'\W', '', n):
            return n
    return sorted(cands, key=len)[0]


def row_head():
    return f'''	<tr>
		<td nowrap="nowrap" style="{TD_HEAD}">
			<p align="center" class="MsoNormal" style="text-align: center">
				<span style="{KAI}">篇名</span></p>
		</td>
		<td nowrap="nowrap" style="{TD_HEAD}">
			<p align="center" class="MsoNormal" style="text-align: center">
				<span style="{KAI}">作者</span></p>
		</td>
		<td nowrap="nowrap" style="{TD_HEAD}">
			<p align="center" class="MsoNormal" style="text-align: center">
				<span style="{KAI}">頁數</span></p>
		</td>
	</tr>'''


def row_section(label):
    return f'''	<tr>
		<td colspan="3" nowrap="nowrap" style="{TD_SECTION}">
			<p class="MsoNormal" style="text-align: justify; text-justify: inter-ideograph">
				<b><span style="font-size: 16.0pt; font-family: 'MS Mincho',serif; color: black">❖</span><span style="font-size: 16.0pt; {KAI}">{esc(label)}</span></b></p>
		</td>
	</tr>'''


def row_article(a, pdf_name, shade):
    bg = '; background: #DBE5F1' if shade else ''
    zh, en = esc(a['title_zh']), esc(a['title_en'])
    if pdf_name:
        href = PREFIX + pdf_name
        zh_cell = (f'<a href="{href}" target="_blank"><span style="{KAI}">{zh}</span></a>')
        en_cell = (f'<a href="{href}" target="_blank"><span lang="EN-US" style="{TNR}">{en}</span></a>'
                   if en else '')
    else:
        # 🚨 沒有 PDF 的篇目照樣要列出來（有目無文），但不掛連結——
        #    掛一個連不到的連結比沒有連結更糟。
        zh_cell = f'<span style="{KAI}">{zh}</span>'
        en_cell = f'<span lang="EN-US" style="{TNR}">{en}</span>' if en else ''
    en_block = f'''
			<p class="MsoNormal">
				{en_cell}</p>''' if en_cell else ''
    return f'''	<tr>
		<td style="{TD_TITLE}{bg}">
			<p class="MsoNormal">
				{zh_cell}</p>{en_block}
		</td>
		<td nowrap="nowrap" style="{TD_AUTHOR}{bg}">
			<p align="center" class="MsoNormal" style="text-align: center">
				<span style="{KAI}">{esc(a['author'])}</span></p>
		</td>
		<td nowrap="nowrap" style="{TD_PAGE}{bg}">
			<p align="center" class="MsoNormal" style="text-align: center">
				<span lang="EN-US" style="{TNR}">{esc(a['page'])}</span></p>
		</td>
	</tr>'''


def row_pubdate(text):
    return f'''	<tr>
		<td colspan="3" nowrap="nowrap" style="{TD_SECTION}">
			<p class="MsoNormal">
				<span style="{KAI}">出版日期：</span><span lang="EN-US" style="{TNR}">{esc(text)}</span></p>
		</td>
	</tr>'''


def build(issue, data, names):
    rows = [row_head()]
    seq = 0
    shade = True
    for it in data['items']:
        if it['kind'] == 'section':
            rows.append(row_section(it['label']))
            continue
        seq += 1
        pdf = find_pdf(names, issue, seq, it['title_zh'])
        rows.append(row_article(it, pdf, shade))
        shade = not shade
    if issue in PUB_DATE:
        rows.append(row_pubdate(PUB_DATE[issue]))
    body = '\n'.join(rows)
    return (f'<table border="0" cellpadding="0" cellspacing="0" class="MsoNormalTable" '
            f'style="width: 20.0cm; border-collapse: collapse" width="756">\n'
            f'<tbody>\n{body}\n</tbody>\n</table>\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('issues', nargs='*', type=int, default=[44, 45])
    ap.add_argument('--harvest', default='c:/tmp/hcu-cms/issues-harvest.json')
    ap.add_argument('--filelist', default='c:/tmp/hcu-cms/filelist.txt')
    ap.add_argument('--out', default='c:/tmp/hcu-cms/out')
    args = ap.parse_args()

    harvest = json.loads(Path(args.harvest).read_text(encoding='utf-8'))
    names = [l.strip() for l in Path(args.filelist).read_text(encoding='utf-8').splitlines() if l.strip()]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    for n in args.issues:
        data = harvest.get(str(n)) or harvest.get(n)
        if not data:
            print(f'❌ harvest 裡沒有第 {n} 期')
            continue
        arts = [x for x in data['items'] if x['kind'] == 'article']
        htmltext = build(n, data, names)
        linked = htmltext.count('<a href=')  # 每篇有中英兩個連結
        fp = out / f'issue-{n}.html'
        fp.write_text(htmltext, encoding='utf-8')
        # 🚨 印分母：有幾篇、其中幾篇掛得上 PDF、哪幾篇沒有
        missing = []
        seq = 0
        for it in data['items']:
            if it['kind'] != 'article':
                continue
            seq += 1
            if not find_pdf(names, n, seq, it['title_zh']):
                missing.append(f"{n}-{seq} {it['title_zh'][:28]}")
        print(f'第{n}期 → {fp}  篇數={len(arts)}  有PDF={len(arts)-len(missing)}  無PDF={len(missing)}')
        for m in missing:
            print(f'   ⚠ 無 PDF：{m}')


if __name__ == '__main__':
    main()
