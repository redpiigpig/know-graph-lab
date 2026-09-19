# -*- coding: utf-8 -*-
"""稽核「臺灣佛教研究中心」站《玄奘佛學研究》底下我們上稿的那幾頁——抓公開頁回來逐項點名。

🚨 「送出成功」不等於「頁面對」：CKEditor 會改寫 HTML、CMS 會轉檔名大小寫、
   發布狀態沒按到也還是 200。所以一律回頭抓公開頁，印出分母與每一條檢查。

用法：python -X utf8 scripts/hcjbs_cms_verify.py
"""
import re
import sys
import html as htmllib

import requests

BASE = ('https://www.hcu.edu.tw/buddhism/buddhism/zh-tw/'
        '43C51435624E43D583779C031ACF4E2F/B975569CC2F04819892552ADE1A9090E')
UA = {'User-Agent': 'Mozilla/5.0'}

# 各期頁＝「玄奘佛學研究」節點底下的內容；五個章則頁＝該節點底下的**子節點**（nav 上各一項）
PAGES = {
    '第四十四期玄奘佛學研究': 'DE09FA1EDAB748D7A8FAE8E8CA57EE7B',
    '第四十五期玄奘佛學研究': '34BD6FE105FA42A583802ACC00D32151',
    '投稿指引': '963E07CC70054A9191713195B7E233A5',
    '編輯委員': '28DBE4BB84354651ADB043FED6A1FAAE',
    '審查流程': '25E6418CEC0E4A69AF569743EA6FDF43',
    '學術倫理': '3D19104FF4CE46AC8F619F4F110BB884',
    '生成式人工智慧（AI）使用規範': '430E878E0E0E409B96DBB8361E9FE95E',
}
# 章則頁是節點，頁尾要掛 Word；各期頁不掛
WANT_DOCX = {
    '投稿指引': '投稿指引',
    '編輯委員': '編輯團隊資訊',
    '審查流程': '期刊審查流程',
    '學術倫理': '學術倫理聲明',
    '生成式人工智慧（AI）使用規範': '學報AI使用規範',
}

# 每頁要出現的字串（正面），與不該出現的（負面）
MUST = {
    '第四十四期玄奘佛學研究': ['「佛教應用倫理的對話」專輯', '玄奘論壇', '黃漢忠', '梁秀睿',
                    'Reexamine the Patient Right to Autonomy Act', '出版日期'],
    '第四十五期玄奘佛學研究': ['「臺灣佛教」專輯', '侯坤宏', '劉勁松', '妙通寺的發展及其在當代臺灣佛教史的地位',
                    '出版日期'],
    '投稿指引': ['徵稿啟事', '第56期', '當代東南亞上座部佛教', 'hcu10@hcu.edu.tw', '堅意法師',
             '學術性論文撰寫格式要點', '稿件編排', '台灣期刊論文索引系統'],
    '編輯委員': ['總編輯', '釋昭慧', '王三慶', '何日生', '李玉珍', '李瑞全', '林保堯', '林朝成',
             '邱敏捷', '侯坤宏', '張瓈文', '黃運喜', '葉海煙', '蕭麗華', '嚴瑋泓', 'Marcus Günzel',
             '編輯團隊簡介', '庭野和平獎'],
    '審查流程': ['審稿流程', '內審', '外審', '第三位審查', '修訂回應表', '複審'],
    '學術倫理': ['編輯者義務', '審查者義務', '投稿者（作者）義務', '調查參與', '資料使用與保留',
             '來源告知', '資料來源之告知', 'COPE'],
    '生成式人工智慧（AI）使用規範': ['透明揭露原則', '人類須負最終全責原則', '機密與個資安全限制',
                        '作者使用相關工具', 'Prompt'],
}
MUST_NOT = {
    '生成式人工智慧（AI）使用規範': ['學生使用相關工具'],   # 老師指示改「作者」
}


def text_of(h):
    """HTML → 純文字。

    🚨 行內標籤不可換成空白：頁面把「第56期」排成
       `<span>第</span><span>56</span><span>期</span>`（數字要走 Times New Roman），
       一律換空白就變成「第 56 期」，稽核於是誤報「缺 第56期」。
       只有區塊標籤（p/div/td/tr/br/li…）換行，其餘標籤直接去掉。
    """
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S | re.I)
    t = re.sub(r'</?(p|div|td|tr|table|br|li|ul|ol|h[1-6])\b[^>]*>', '\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'[ \t]+', ' ', htmllib.unescape(t))


def main():
    bad = 0
    for title, aid in PAGES.items():
        r = requests.get(f'{BASE}/{aid}', headers=UA, timeout=60)
        h = r.text
        txt = text_of(h)
        pdfs = sorted(set(re.findall(r'href="(/upload/userfiles/[^"]+\.pdf)"', h)))
        print(f'\n■ {title}  http={r.status_code}  純文字 {len(txt)} 字  PDF 連結 {len(pdfs)} 個')
        if r.status_code != 200:
            print('   ❌ 抓不到頁面'); bad += 1; continue
        if title not in txt:
            print(f'   ❌ 頁面標題不含「{title}」'); bad += 1
        miss = [k for k in MUST.get(title, []) if k not in txt]
        print(f'   關鍵字 {len(MUST.get(title, [])) - len(miss)}/{len(MUST.get(title, []))} 命中')
        for k in miss:
            print(f'   ❌ 缺：{k}'); bad += 1
        for k in MUST_NOT.get(title, []):
            if k in txt:
                print(f'   ❌ 不該出現卻出現：{k}'); bad += 1
        # PDF 連結逐個試（HEAD 會被擋，用 GET 只讀前幾 byte）
        for p in pdfs:
            rr = requests.get('https://www.hcu.edu.tw' + p, headers=UA, timeout=120, stream=True)
            head = next(rr.iter_content(4), b'')
            ok = rr.status_code == 200 and head == b'%PDF'
            rr.close()
            if not ok:
                print(f'   ❌ PDF 連不到：{p.split("/")[-1][:50]}  status={rr.status_code}')
                bad += 1
        if pdfs:
            print(f'   PDF 全部可下載：{len(pdfs)} 個')
        # 章則頁的 Word 附件
        # 🚨 附件不是 href="….docx"：CMS 用 /buddhism/Download.aspx?aid=… 出檔，
        #    連結文字才是檔名。用 .docx 去比會全部誤報成「缺附件」。
        want = WANT_DOCX.get(title)
        if want:
            atts = re.findall(r'<a[^>]+href="([^"]*Download\.aspx\?aid=[^"]+)"[^>]*>([^<]*)</a>', h)
            names = [a[1].strip() for a in atts]
            print(f'   相關附件 {len(atts)} 個：{names}')
            hit = [u for u, n in atts if want in n]
            if not hit:
                print(f'   ❌ 缺 Word 附件：{want}'); bad += 1
            for u in hit:
                full = u if u.startswith('http') else 'https://www.hcu.edu.tw' + u
                rr = requests.get(full, headers=UA, timeout=120, stream=True)
                head = next(rr.iter_content(2), b'')
                ctype = rr.headers.get('Content-Type', '')
                rr.close()
                ok = rr.status_code == 200 and head == b'PK'
                print(f'   {"✔" if ok else "❌"} 附件可下載 status={rr.status_code} type={ctype[:40]}')
                if not ok:
                    bad += 1
        # 🚨 全白底：不該再有淺藍／灰底
        for bgcolor in ('DBE5F1', '#f5f5f5', '#eeeeee; background'):
            if bgcolor in h and bgcolor != '#eeeeee; background':
                print(f'   ❌ 還有底色 {bgcolor}'); bad += 1

    print(f'\n{"✅ 全部通過" if not bad else f"❌ {bad} 項未過"}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
