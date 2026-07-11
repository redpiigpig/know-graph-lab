# -*- coding: utf-8 -*-
"""口述訪談三冊頁數同步：量頁碼 → 更新目錄 → 回填專書腳註。

流程（需本機 Microsoft Word，走 COM 自動化，自開獨立實例不動別人視窗）：
  1. 重建三冊訪談 docx（依日期排序版）
  2. Word 開啟各冊：更新目次欄位（烙上真實頁碼）、記錄每篇起頁與總頁數、
     並為專書引文片段找出精確頁碼
  3. 依頁碼改寫《當代的大愛道革命_全書初稿.md》的訪談腳註：
     補訪問地點（從逐字稿 metadata）＋「收入《口述訪談集》第N冊，頁X–Y」
     （引文另標確切頁碼）
  4. 重建專書 md/docx（pandoc 頁尾註），再用 Word 更新專書目次
頁數紀錄存 scripts/state/dadaodao_pages.json。
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from dadaodao_interviews_docx import VOLUMES, build_volume, SRC_DIR, OUT_DIR  # noqa: E402

MD = ROOT / '當代的大愛道革命_全書初稿.md'
STATE = SCRIPTS / 'state/dadaodao_pages.json'
CN = ['一', '二', '三']

WD_PAGE = 3      # wdActiveEndPageNumber
WD_STAT_PAGES = 2


def person_of(fname: str) -> str:
    """'08.20 釋長慈法師口述訪談紀錄' → '釋長慈法師'"""
    s = re.sub(r'^[\d.]+\s*', '', fname)
    return s.split('口述訪談紀錄')[0]


def quote_snippets():
    """md 中「引文區塊緊接 [^id]」→ id: 引文片段（供 Word Find 找精確頁）。"""
    text = MD.read_text(encoding='utf-8')
    out = {}
    for m in re.finditer(r'((?:^>.*\n)+)', text, re.M):
        block = m.group(1)
        idm = re.search(r'\[\^([^\]]+)\]\s*$', block.strip())
        if not idm:
            continue
        first = re.sub(r'^>\s?', '', block.strip().split('\n')[0])
        first = re.sub(r'\*\*|\[\^[^\]]+\]', '', first)
        seg = re.split(r'…|——|\[', first)[0].strip()
        if len(seg) >= 8:
            out[idm.group(1)] = seg[:24]
    return out


def measure_with_word():
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    pages = {}   # fname -> {vol, vol_label, start, end}
    totals = {}
    snippets = quote_snippets()
    fn_person = footnote_persons()
    quote_pages = {}
    try:
        for vi, (vtitle, out_name, files) in enumerate(VOLUMES):
            path = OUT_DIR / out_name
            doc = word.Documents.Open(str(path))
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents.Item(i).Update()
            starts = []
            for p in doc.Paragraphs:
                if p.OutlineLevel == 1:
                    title = p.Range.Text.strip()
                    if title:
                        starts.append((title, p.Range.Information(WD_PAGE)))
            total = doc.ComputeStatistics(WD_STAT_PAGES)
            totals[out_name] = total
            # 依順序對應 files（每篇一個 Heading 1）
            for idx, fname in enumerate(files):
                start = starts[idx][1] if idx < len(starts) else None
                end = (starts[idx + 1][1] - 1) if idx + 1 < len(starts) else total
                pages[fname] = {'vol': vi + 1, 'vol_label': CN[vi], 'start': start, 'end': end}
            # 引文精確頁：此冊涵蓋的受訪者
            persons_here = {person_of(f): f for f in files}
            for fid, snip in snippets.items():
                person = fn_person.get(fid)
                if not person or person not in persons_here:
                    continue
                rng = doc.Content
                f = rng.Find
                f.ClearFormatting()
                f.Forward = True
                if f.Execute(FindText=snip):
                    quote_pages[fid] = rng.Information(WD_PAGE)
            doc.Save()
            doc.Close()
            print(f'{vtitle}：{total} 頁，目次已更新')
    finally:
        word.Quit()
    return pages, totals, quote_pages


def footnote_persons():
    """md 腳註 id → 受訪者名（僅口述訪談紀錄類腳註）。"""
    out = {}
    for m in re.finditer(r'(?m)^\[\^([^\]]+)\]:\s*(.+)$', MD.read_text(encoding='utf-8')):
        t = m.group(2)
        pm = re.match(r'^([^，。]*?)口述訪談紀錄，張辰瑋訪問', t)
        if pm:
            out[m.group(1)] = pm.group(1)
    return out


def interview_place(fname: str) -> str:
    txt = (SRC_DIR / f'{fname}.txt').read_text(encoding='utf-8')
    m = re.search(r'(?:訪問|訪談|採訪)地點[：:]\s*(.+)', txt)
    return m.group(1).strip() if m else ''


def update_md_footnotes(pages, quote_pages):
    text = MD.read_text(encoding='utf-8')
    person_file = {person_of(f): f for _, _, fs in VOLUMES for f in fs}
    n = 0

    def fix(m):
        nonlocal n
        fid, body = m.group(1), m.group(2)
        pm = re.match(r'^([^，。]*?)口述訪談紀錄，張辰瑋訪問，([^，。【]+)', body)
        if not pm:
            return m.group(0)
        person = pm.group(1)
        fname = person_file.get(person)
        if not fname or fname not in pages:
            return m.group(0)
        info = pages[fname]
        place = interview_place(fname)
        # 清掉舊的地點待核／附錄頁碼待核／先前回填的收入資訊（冪等）
        body2 = re.sub(r'【地點待核】。?', '', body)
        body2 = re.sub(r'。?全文見本書附錄【頁碼待核】。?', '', body2)
        body2 = re.sub(r'。?收入《(?:當代的大愛道革命‧口述訪談集|人間佛教與印順學派訪談集)》[^。]*', '', body2).rstrip('。， ')
        # 若原本沒有任何地點（逐字稿地點的 4 字視窗皆不在句中）才補
        overlap = place and any(place[i:i + 4] in body2 for i in range(max(1, len(place) - 3)))
        if place and not overlap:
            body2 += f'，{place}'
        cite = f'。收入《人間佛教與印順學派訪談集》第{info["vol_label"]}冊，頁{info["start"]}–{info["end"]}'
        if fid in quote_pages:
            cite += f'，引文見頁{quote_pages[fid]}'
        n += 1
        return f'[^{fid}]: {body2}{cite}。'

    text = re.sub(r'(?m)^\[\^([^\]]+)\]:\s*(.+)$', fix, text)
    MD.write_text(text, encoding='utf-8')
    print(f'腳註回填：{n} 條')


def update_book_toc():
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        path = ROOT / 'public/content/works/mahaprajapati-revolution-book.docx'
        doc = word.Documents.Open(str(path))
        for i in range(1, doc.TablesOfContents.Count + 1):
            doc.TablesOfContents.Item(i).Update()
        total = doc.ComputeStatistics(WD_STAT_PAGES)
        doc.Save()
        doc.Close()
        print(f'專書目次已更新，共 {total} 頁')
    finally:
        word.Quit()


def main():
    print('① 重建三冊訪談 docx（日期排序）')
    for vtitle, out_name, files in VOLUMES:
        build_volume(vtitle, out_name, files)
    print('② Word 量頁數＋更新目次')
    pages, totals, quote_pages = measure_with_word()
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({'pages': pages, 'totals': totals, 'quote_pages': quote_pages},
                                ensure_ascii=False, indent=1), encoding='utf-8')
    print('③ 回填專書腳註頁碼')
    update_md_footnotes(pages, quote_pages)
    print('④ 重建專書 md/docx')
    import dadaodao_book_export
    dadaodao_book_export.build()
    print('⑤ 更新專書目次')
    update_book_toc()


if __name__ == '__main__':
    main()
