# -*- coding: utf-8 -*-
"""稽核「臺灣佛教研究中心」站《玄奘佛學研究》全部頁面——抓公開頁回來逐項點名。

🚨 「送出成功」不等於「頁面對」：CKEditor 會改寫 HTML、CMS 會轉檔名大小寫、
   生效時間沒到也照樣存得起來。所以一律回頭抓公開頁，並印出分母。
🚨 也要驗**樣式有沒有套上**：五個章則頁曾經內容全對、關鍵字全中，但外框 div
   （'Times New Roman'／標楷體 字體堆疊）漏了沒套上——只驗關鍵字驗不出這種錯。

用法：
    python -X utf8 scripts/hcjbs_cms_verify.py             # 全部（45 期＋封面牆＋5 章則）
    python -X utf8 scripts/hcjbs_cms_verify.py --quick     # 封面牆＋5 章則＋抽 5 期
"""
import html as htmllib
import json
import re
import sys

import requests

BASE = ('https://www.hcu.edu.tw/buddhism/buddhism/zh-tw/'
        '43C51435624E43D583779C031ACF4E2F/B975569CC2F04819892552ADE1A9090E')
UA = {'User-Agent': 'Mozilla/5.0'}
FONT_MARK = "Times New Roman',Times,DFKai-SB"
NAV_NAMES = ['研究學報', '編輯委員', '投稿指引', '審查流程', '學術倫理', 'AI 使用規範']

RULE_PAGES = {
    '投稿指引': ('963E07CC70054A9191713195B7E233A5', '投稿指引',
             ['本學報主要刊載', '第56期', '當代東南亞上座部佛教', 'hcu10@hcu.edu.tw', '稿件編排']),
    '編輯委員': ('28DBE4BB84354651ADB043FED6A1FAAE', '編輯團隊資訊',
             ['總編輯', '釋昭慧', 'Marcus Günzel', '編輯團隊簡介', '庭野和平獎']),
    '審查流程': ('25E6418CEC0E4A69AF569743EA6FDF43', '期刊審查流程',
             ['審稿流程', '內審', '外審', '第三位審查', '修訂回應表']),
    '學術倫理': ('3D19104FF4CE46AC8F619F4F110BB884', '學術倫理聲明',
             ['編輯者義務', '審查者義務', '調查參與', '資料來源之告知', 'COPE']),
    'AI 使用規範': ('430E878E0E0E409B96DBB8361E9FE95E', '學報AI使用規範',
                ['透明揭露原則', '人類須負最終全責原則', '作者使用相關工具']),
}


def text_of(h):
    """HTML → 純文字。行內標籤直接去掉（換成空白會把「第56期」變成「第 56 期」而誤報）。"""
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S | re.I)
    t = re.sub(r'</?(p|div|td|tr|table|br|li|ul|ol|h[1-6])\b[^>]*>', '\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'[ \t]+', ' ', htmllib.unescape(t))


def common_checks(tag, h, bad):
    """每頁都要過：字體外框、沒有填色、導覽列六項、研究學報可點。"""
    if FONT_MARK not in h:
        print(f'   ❌ {tag} 字體外框沒套上'); bad.append(tag)
    if 'DBE5F1' in h:
        print(f'   ❌ {tag} 還有淺藍列底 #DBE5F1'); bad.append(tag)
    missing = [n for n in NAV_NAMES if n not in h]
    if missing:
        print(f'   ❌ {tag} 導覽列缺：{missing}'); bad.append(tag)
    if not re.search(r'href="[^"]*B975569CC2F04819892552ADE1A9090E/\?sh="[^>]*>\s*研究學報', h):
        print(f'   ❌ {tag} 導覽列的「研究學報」不是連結'); bad.append(tag)


def check_issue(n, url, bad):
    r = requests.get(url, headers=UA, timeout=60)
    h, txt = r.text, ''
    if r.status_code == 200:
        txt = text_of(r.text)
    # 🚨 連結有兩種寫法：站內相對 `/upload/userfiles/…`（我們新上的 44、45 期）與
    #    絕對 `https://www.hcu.edu.tw/upload/userfiles/37837C6F…`（舊期本來就指向宗教系的
    #    檔案庫）。只認相對路徑會把 11–29、41、42 期誤報成「一個 PDF 都沒有」。
    pdfs = sorted(set(re.findall(r'href="((?:https://www\.hcu\.edu\.tw)?/upload/userfiles/[^"]+\.pdf)"', h,
                                 re.I)))
    cover = re.findall(rf'cover-{n:02d}\.jpg', h)
    print(f'■ 第{n:>2}期  http={r.status_code}  字數 {len(txt):>5}  PDF {len(pdfs):>2}  封面 {len(cover)}')
    if r.status_code != 200:
        print('   ❌ 抓不到'); bad.append(f'第{n}期'); return []
    common_checks(f'第{n}期', h, bad)
    if not cover:
        print(f'   ❌ 第{n}期 沒有封面圖'); bad.append(f'第{n}期')
    if not pdfs:
        print(f'   ⚠ 第{n}期 一個 PDF 連結都沒有'); bad.append(f'第{n}期')
    if '篇名' not in txt or '作者' not in txt:
        print(f'   ❌ 第{n}期 沒有篇目表'); bad.append(f'第{n}期')
    return pdfs


def main():
    quick = '--quick' in sys.argv
    bad = []
    links = json.load(open('c:/tmp/hcu-cms/issue-links.json', encoding='utf-8'))

    r = requests.get(f'{BASE}/?sh=', headers=UA, timeout=60)
    h = r.text
    covers = len(set(re.findall(r'cover-\d\d\.jpg', h)))
    issue_links = len(set(re.findall(r'B975569CC2F04819892552ADE1A9090E/[0-9A-F]{32}', h)))
    print(f'■ 研究學報（封面牆）  http={r.status_code}  封面 {covers}/45  期連結 {issue_links}')
    common_checks('封面牆', h, bad)
    if covers != 45:
        print('   ❌ 封面數不是 45'); bad.append('封面牆')
    if 'photo_list_container{display:none' not in h.replace(' ', ''):
        print('   ❌ 缺少藏掉重複清單／分頁的那段 CSS'); bad.append('封面牆')

    for title, (aid, docx, musts) in RULE_PAGES.items():
        r = requests.get(f'{BASE}/{aid}/', headers=UA, timeout=60)
        h = r.text
        txt = text_of(h) if r.status_code == 200 else ''
        atts = re.findall(r'<a[^>]+href="([^"]*Download\.aspx\?aid=[^"]+)"[^>]*>([^<]*)</a>', h)
        hit = [u for u, nm in atts if docx.replace('.docx', '') in nm]
        miss = [k for k in musts if k not in txt]
        print(f'■ {title}  http={r.status_code}  字數 {len(txt):>5}  附件 {len(atts)}  '
              f'關鍵字 {len(musts) - len(miss)}/{len(musts)}  首行縮排 {h.count("text-indent: 2em")}')
        if r.status_code != 200:
            print('   ❌ 抓不到'); bad.append(title); continue
        common_checks(title, h, bad)
        for k in miss:
            print(f'   ❌ 缺關鍵字：{k}'); bad.append(title)
        if not hit:
            print(f'   ❌ 缺 Word 附件：{docx}'); bad.append(title)
        else:
            rr = requests.get('https://www.hcu.edu.tw' + hit[0], headers=UA, timeout=120, stream=True)
            head = next(rr.iter_content(2), b''); rr.close()
            if not (rr.status_code == 200 and head == b'PK'):
                print(f'   ❌ 附件下載不到 status={rr.status_code}'); bad.append(title)
        if title == 'AI 使用規範' and '學生使用相關工具' in txt:
            print('   ❌ AI 規範還寫著「學生」'); bad.append(title)

    todo = sorted(int(k) for k in links)
    if quick:
        todo = [1, 20, 43, 44, 45]
    first_pdfs = []
    for n in todo:
        got = check_issue(n, links[str(n)], bad)
        if got:
            first_pdfs.append((n, got[0]))

    sample = first_pdfs[::6]
    print(f'\n[PDF 抽驗] {len(first_pdfs)} 期有連結，抽 {len(sample)} 個下載驗檔頭')
    for n, p in sample:
        url = p if p.startswith('http') else 'https://www.hcu.edu.tw' + p
        rr = requests.get(url, headers=UA, timeout=120, stream=True)
        head = next(rr.iter_content(4), b''); rr.close()
        ok = rr.status_code == 200 and head == b'%PDF'
        print(f'   {"✔" if ok else "❌"} 第{n}期 status={rr.status_code} {p.split("/")[-1][:40]}')
        if not ok:
            bad.append(f'第{n}期PDF')

    uniq = sorted(set(bad))
    print(f'\n{"✅ 全部通過" if not uniq else f"❌ {len(uniq)} 項有問題：{uniq}"}')
    return 1 if uniq else 0


if __name__ == '__main__':
    sys.exit(main())
