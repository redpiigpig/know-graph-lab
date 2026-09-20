# -*- coding: utf-8 -*-
"""把「臺灣佛教研究中心」站既有各期頁的舊版面（Word 貼上的表格）重排成新版面。

資料不外求：舊稿裡就有中英篇名、作者、頁數與 PDF 連結，
所以先用 `hcu_cms_dump_node_articles.mjs --ids …` 把 45 篇原稿撈到 `c:/tmp/hcu-cms/old/`，
這支只做「解析 → 用新樣板重排」。

🚨 PDF 連結一律**沿用舊稿裡的 href**，不要照檔名規則重算：舊期的檔名五花八門
   （`1-1.pdf`、`43-1應用倫理學的新視野…pdf`），重算一定對不上。

用法：
    python -X utf8 scripts/hcjbs_cms_restyle.py            # 全部 45 期
    python -X utf8 scripts/hcjbs_cms_restyle.py 43 42      # 只做指定幾期
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

from hcjbs_cms_issue_html import PUB_DATE, article_table, zh_num
from hcjbs_cms_style import (cover_img, journal_home_url, linked_title, section_nav,
                             title_bar, two_col, wrap)

OLD = Path('c:/tmp/hcu-cms/old')
OUT = Path('c:/tmp/hcu-cms/out')

ZH = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def issue_no(text):
    # 🚨 兩種寫法都要認：站上是「第四十五期」，而 dump 的 index.json 寫的是「第45期」
    #    （來源是 issue-links.json 的鍵）。只認中文數字就會一期都對不到。
    m = re.search(r'第(\d+)期', text or '')
    if m:
        return int(m.group(1))
    m = re.search(r'第([一二三四五六七八九十]+)期', text or '')
    if not m:
        return None
    s = m.group(1)
    if '十' in s:
        a, _, b = s.partition('十')
        return (ZH.get(a, 1) if a else 1) * 10 + (ZH.get(b, 0) if b else 0)
    return ZH.get(s)


def text_of(frag):
    t = re.sub(r'<[^>]+>', '', frag)
    return re.sub(r'\s+', ' ', htmllib.unescape(t)).strip()


CJK = re.compile(r'[\u3000-\u303f\u3400-\u9fff\uff00-\uffef]')
_L = 'A-Za-z0-9\u00c0-\u024f\u1e00-\u1eff'
LATIN_START = re.compile(f'[{_L}]')


def split_zh_en(s):
    """一格裡中英篇名並排時切開（作法與 hcjbs_issue_harvest 相同）。"""
    for m in LATIN_START.finditer(s):
        rest = s[m.start():]
        if len(rest) < 12:
            break
        if len(CJK.findall(rest)) / len(rest) < 0.08:
            return s[:m.start()].strip(' -—–\u3000'), rest.strip()
    return s.strip(), ''


def parse_old(fp):
    """舊稿 → {'items': [...], 'pub': '2025.3'}"""
    src = fp.read_text(encoding='utf-8')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', src, re.S | re.I)
    items, pub = [], ''
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S | re.I)
        if not cells:
            continue
        texts = [text_of(c) for c in cells]
        joined = ' '.join(texts).strip()
        if not joined:
            continue
        if texts[0] in ('篇名', '篇  名'):        # 表頭
            continue
        if re.match(r'^出版日期', joined):
            m = re.search(r'(\d{4})\s*[.\-／/年]\s*(\d{1,2})', joined)
            if m:
                pub = f'{m.group(1)}.{int(m.group(2))}'
            continue
        # 整列合併（colspan）＝專輯分隔列
        if len(cells) == 1 or (len(texts) > 1 and not ''.join(texts[1:])):
            label = re.sub(r'^[❖◆•\s]+', '', texts[0]).strip()
            if label:
                items.append({'kind': 'section', 'label': label})
            continue
        # 一般篇目：第一格是篇名（可能含中英兩個 <p>，可能有 <a href>）
        cell0 = cells[0]
        href = (re.search(r'href="([^"]+)"', cell0) or [None, ''])[1]
        paras = re.findall(r'<p[^>]*>(.*?)</p>', cell0, re.S | re.I)
        chunks = [text_of(x) for x in paras if text_of(x)] or [text_of(cell0)]
        if len(chunks) >= 2:
            zh, en = chunks[0], ' '.join(chunks[1:])
            # 有時第一段就把中英黏在一起
            if CJK.search(en) and len(CJK.findall(en)) / max(1, len(en)) > 0.3:
                zh, en = ' '.join(chunks), ''
        else:
            zh, en = split_zh_en(chunks[0])
        items.append({
            'kind': 'article',
            'title_zh': zh, 'title_en': en,
            'author': texts[1] if len(texts) > 1 else '',
            'page': texts[2] if len(texts) > 2 else '',
            'pdf_href': href,
        })
    return {'items': items, 'pub': pub}


def render(issue, data):
    # CMS 樣板把篇名（.news_title）與日期（.datetime）印在我們的內容之前，順序改不了，
    # 而且它印的節點名稱（h2 .title）不是連結——三個都藏掉，由我們自己印，
    # 這樣「玄奘佛學研究」可點回封面牆、區內導覽也在「第N期…」上面。
    hide = ('<style type="text/css">.news_detail_container h2,'
            '.news_detail_container .news_title,'
            '.news_detail_container .datetime{display:none !important;}</style>')
    body = (hide + '\n'
            + linked_title('玄奘佛學研究', journal_home_url()) + '\n'
            + section_nav('研究學報') + '\n'
            + title_bar(f'第{zh_num(issue)}期玄奘佛學研究學報', width=140) + '\n'
            + two_col(cover_img(issue), article_table(data, issue, [], pub=data.get('pub'))))
    return wrap(body)


def main():
    want = [int(a) for a in sys.argv[1:] if a.isdigit()]
    index = json.loads((OLD / 'index.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    done = []
    for rec in index:
        n = issue_no(rec.get('title'))
        if n is None or (want and n not in want):
            continue
        fp = OLD / f"{rec['id']}.html"
        if not fp.exists():
            print(f'❌ 第{n}期 沒有原稿檔 {fp.name}')
            continue
        data = parse_old(fp)
        arts = [x for x in data['items'] if x['kind'] == 'article']
        secs = [x for x in data['items'] if x['kind'] == 'section']
        nopdf = [x for x in arts if not x['pdf_href']]
        noen = [x for x in arts if not x['title_en']]
        (OUT / f'issue-{n}.html').write_text(render(n, data), encoding='utf-8')
        print(f'第{n:>2}期 篇數 {len(arts):>2} 專輯標 {len(secs)} 無PDF {len(nopdf)} 無英譯 {len(noen)} '
              f'出版日期 {data["pub"] or PUB_DATE.get(n, "—")}  → issue-{n}.html')
        for x in nopdf:
            print(f'     ⚠ 無 PDF：{x["title_zh"][:30]}')
        done.append((n, rec['id']))
    json.dump([{'issue': n, 'id': i} for n, i in sorted(done)],
              open('c:/tmp/hcu-cms/restyle-targets.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'\n共 {len(done)} 期 → c:/tmp/hcu-cms/restyle-targets.json')


if __name__ == '__main__':
    main()
