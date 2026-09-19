# -*- coding: utf-8 -*-
"""臺灣佛教研究中心站《玄奘佛學研究》各頁的共用版面元件——**照模擬站的 UI 做**。

模擬站＝`redpiigpig.com/Hsuan_Chuang_Studies`（`pages/Hsuan_Chuang_Studies/`）。
除了校網母頁的 header／nav 由 CMS 提供，底下的內容一律長成模擬站那樣：

- **一律白底**：不用任何 background（曾照舊期的 Word 表格抄了 `#DBE5F1` 淺藍列底，被退）
- 標題：22px 粗體 ＋ 96px 黑色粗線 ＋ 虛線延伸
- 表格：只有框線（表頭 2px #333、每列 1px #eee），沒有填色
- PDF 用橘色按鈕 `#c8860a`
- 字體堆疊把 Latin 放最前、標楷體放後面，讓**英文與數字走 Times New Roman**、中文走標楷體
  （逐字元回退，不必逐段切 span）

🚨 CMS 的 CKEditor 會重寫 HTML：版面一律用 `<table>` ＋ inline style，不要靠 flex／grid／class。
"""

import html

RID = '436650DB9FC648D783CDF0FEAACE0321'
FILES = f'/upload/userfiles/{RID}/files/'
IMAGES = f'/upload/userfiles/{RID}/Images/'
FONT = "'Times New Roman',Times,DFKai-SB,標楷體,KaiTi,serif"
ORANGE = '#c8860a'


def esc(s):
    return html.escape(str(s), quote=False)


def wrap(inner):
    """整頁外框：白底＋字體堆疊。"""
    return (f'<div style="font-family: {FONT}; color: #333; background: #ffffff;">\n'
            f'{inner}\n</div>')


def title_bar(text, width=96):
    """22px 粗體標題 ＋ 黑粗線 ＋ 虛線（模擬站每頁的區塊標）。"""
    return (f'<p style="font-size: 22px; font-weight: bold; color: #111111; margin: 0 0 8px;">'
            f'{esc(text)}</p>\n'
            f'<table width="100%" cellpadding="0" cellspacing="0" '
            f'style="border-collapse: collapse; margin: 0 0 24px;">\n\t<tr>\n'
            f'\t\t<td width="{width}" style="height: 4px; background: #111111; padding: 0; '
            f'font-size: 0; line-height: 0;"></td>\n'
            f'\t\t<td style="height: 4px; border-bottom: 1px dashed #bbbbbb; padding: 0; '
            f'font-size: 0; line-height: 0;"></td>\n\t</tr>\n</table>')


def para(text, size=17, indent=0, bold=False, color='#333333', align=None):
    st = (f'font-size: {size}px; line-height: 1.85; color: {color}; '
          f'margin: 0 0 14px;')
    if indent:
        st += f' padding-left: {indent * 1.6}em;'
    if bold:
        st += ' font-weight: bold;'
    al = f' align="{align}"' if align else ''
    return f'<p{al} style="{st}">{text if "<" in str(text) else esc(text)}</p>'


def sub_head(text, size=18):
    return (f'<p style="font-size: {size}px; font-weight: bold; color: #111111; '
            f'margin: 26px 0 10px;">{esc(text)}</p>')


def rule_table(headers, rows, widths=None, center_cols=(), size=15):
    """白底表格：表頭只有下框線，每列 1px #eee 分隔。"""
    n = len(headers) if headers else (len(rows[0]) if rows else 0)
    ws = widths or [None] * n
    out = ['<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; margin: 0 0 22px;">']
    if headers:
        out.append('\t<tr>')
        for i, h in enumerate(headers):
            w = f' width="{ws[i]}"' if ws[i] else ''
            al = ' align="center"' if i in center_cols else ''
            out.append(f'\t\t<td{w}{al} style="border-bottom: 2px solid #333333; padding: 0 8px 8px; '
                       f'font-size: 13px; font-weight: bold; color: #666666;">{esc(h)}</td>')
        out.append('\t</tr>')
    for row in rows:
        out.append('\t<tr>')
        for i, cell in enumerate(row):
            al = ' align="center"' if i in center_cols else ''
            out.append(f'\t\t<td{al} style="border-bottom: 1px solid #eeeeee; padding: 10px 8px; '
                       f'font-size: {size}px; line-height: 1.7; color: #333333;">{esc(cell)}</td>')
        out.append('\t</tr>')
    out.append('</table>')
    return '\n'.join(out)


def pdf_button(href, label='PDF ↓'):
    return (f'<a href="{href}" target="_blank" style="display: inline-block; padding: 4px 12px; '
            f'font-size: 13px; color: #ffffff; background: {ORANGE}; text-decoration: none; '
            f'border-radius: 3px; white-space: nowrap;">{esc(label)}</a>')


def cover_img(issue, width=220):
    return (f'<img src="{IMAGES}cover-{issue:02d}.jpg" alt="第{issue}期封面" width="{width}" '
            f'style="width: {width}px; border: 1px solid #e2e2e2; display: block;" />')


def two_col(left, right, left_width=256):
    """左封面／右內容（模擬站各期頁的版面）。"""
    return ('<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">\n'
            f'\t<tr>\n\t\t<td width="{left_width}" valign="top" style="padding: 0 36px 0 0;">\n'
            f'{left}\n\t\t</td>\n\t\t<td valign="top">\n{right}\n\t\t</td>\n\t</tr>\n</table>')


def cover_url(issue):
    return f'{IMAGES}cover-{issue:02d}.jpg'


# 學報這一區的六個頁面（模擬站的 nav）。value 是公開網址。
BASE = ('https://www.hcu.edu.tw/buddhism/buddhism/zh-tw/'
        '43C51435624E43D583779C031ACF4E2F/B975569CC2F04819892552ADE1A9090E')
SECTIONS = [
    ('研究學報', f'{BASE}/'),
    ('編輯委員', f'{BASE}/28DBE4BB84354651ADB043FED6A1FAAE/'),
    ('投稿指引', f'{BASE}/963E07CC70054A9191713195B7E233A5/'),
    ('審查流程', f'{BASE}/25E6418CEC0E4A69AF569743EA6FDF43/'),
    ('學術倫理', f'{BASE}/3D19104FF4CE46AC8F619F4F110BB884/'),
    ('AI 使用規範', f'{BASE}/430E878E0E0E409B96DBB8361E9FE95E/'),
]


def section_nav(current=None):
    """區內導覽：模擬站上方那一排（研究學報｜編輯委員｜投稿指引｜審查流程｜學術倫理｜AI 使用規範）。

    校網母頁的 nav 只到「資料庫」，這五個章則頁在選單第三層，首頁上看不到，
    所以每頁自己帶一排。current 那一項不加連結、用金色標出來。
    """
    cells = []
    for name, url in SECTIONS:
        if name == current:
            cells.append(f'\t\t<td align="center" style="padding: 8px 10px; border-right: 1px solid #dddddd; '
                         f'font-size: 15px; color: {ORANGE}; font-weight: bold;">{esc(name)}</td>')
        else:
            cells.append(f'\t\t<td align="center" style="padding: 8px 10px; border-right: 1px solid #dddddd; '
                         f'font-size: 15px;"><a href="{url}" style="color: #444444; text-decoration: none;">'
                         f'{esc(name)}</a></td>')
    return ('<table cellpadding="0" cellspacing="0" style="border-collapse: collapse; '
            'margin: 0 0 26px; border-bottom: 1px solid #dddddd;">\n\t<tr>\n'
            + '\n'.join(cells) + '\n\t</tr>\n</table>')
