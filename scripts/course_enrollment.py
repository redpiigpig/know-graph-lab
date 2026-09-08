# -*- coding: utf-8 -*-
"""查玄奘公開開課查詢的四門課已選人數，並與 course_schedule.ENROLLED 對帳。

修課須知要印幾份＝已選人數＋2，份數寫在檔名裡。加退選期間人數天天在動，
所以印之前先跑這支，數字對不上就改 ENROLLED 再重出修課須知。

🚨 整站 Big5，查詢字串也要用 big5 編碼，否則查不到任何課。

用法：python scripts/course_enrollment.py
"""
import html
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import course_schedule as CS  # noqa: E402

BASE = 'https://tch.hcu.edu.tw/pub'
OPCLASS = ('BE1A', 'BE2A', 'PA1A')      # 大學部 1A／2A、二專 1A
WANT = set(CS.ENROLLED)


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=40).read().decode('big5', 'replace')


def _cells(tr):
    return [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c)).replace('\xa0', ' ').strip()
            for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S | re.I)]


def fetch():
    """回傳 {課號: 已選人數}。"""
    home = _get(f'{BASE}/GetOpClass.asp?Years=115&Term=1')
    seen, out = set(), {}
    for dept, team, op in re.findall(
            r"LoadCur\('115','1','([^']*)','([^']*)','([^']*)'", home):
        if '宗教' not in dept or op not in OPCLASS or op in seen:
            continue
        seen.add(op)
        qs = urllib.parse.urlencode(
            {'Years': '115', 'Term': '1', 'TeamNo': team,
             'DeptName': dept, 'OpClass': op}, encoding='big5')
        for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', _get(f'{BASE}/CurDataList.asp?{qs}'),
                             re.S | re.I):
            c = _cells(tr)
            if len(c) > 7 and c[1] in WANT:
                # 第 8 欄是「上限/配課/已選人數」，要的是最後那個
                # 🚨 欄位分隔是字面的 &nbsp; 實體，不是空白，直接 int() 會炸
                out[c[1]] = int(re.sub(r'\D', '', c[7].split('/')[-1]))
    return out


ROSTERS = {
    'BBE275': ('115-1_世界宗教文化導論', '世界宗教文化導論-點名表.docx'),
    'PPA001': ('115-1_世界宗教文化導論', '二年制世界宗教文化導論-點名表.docx'),
    'BBE150': ('115-1_基督宗教概論', '基督宗教概論-點名表.docx'),
    'PPA066': ('115-1_宗教系國文講義', '國文-點名表.docx'),
}
DRIVE = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')

# 點名表姓名欄後面掛的學籍註記。表尾自己寫著：
# 休:休學 退:退學 刪:刪除 保:保留學籍 W:期中退選。這些人不會來，份數要扣掉。
MARK = re.compile(r'[（(](休|退|刪|保|W)[學籍]?[）)]')


def roster():
    """回傳 {課號: (名單人數, 註記人數)}；檔案不在就跳過。"""
    from docx import Document
    out = {}
    for code, (folder, name) in ROSTERS.items():
        f = DRIVE / folder / name
        if not f.exists():
            continue
        rows = [[c.text.strip() for c in r.cells]
                for t in Document(str(f)).tables for r in t.rows]
        body = [r for r in rows if re.match(r'^\d+$', r[0] or '')]
        out[code] = (len(body), sum(1 for r in body if MARK.search(r[2])))
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sel, ros = fetch(), roster()
    diff = False
    for code, was in CS.ENROLLED.items():
        n, marked = ros.get(code, (0, 0))
        # 名單是快照、系統是即時；取兩者較大者，再扣掉學籍註記的人
        live = max(n - marked, (sel.get(code) or 0) - marked)
        flag = '✔' if live == was else '⚠'
        if live != was:
            diff = True
        print(f'{flag} {code}　實到 {live} 人（名單 {n}、註記 {marked}、'
              f'系統已選 {sel.get(code)}）　記錄 {was}　→ 印 {live + 2} 份')
    if diff:
        print('\n人數有變：改 course_schedule.ENROLLED，再跑 course_notice_docx.py 重出。')
