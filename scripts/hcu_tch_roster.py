# -*- coding: utf-8 -*-
"""從玄奘「教職員服務系統」抓當學期各門課的最新修課名單（課堂管理名冊）。

`course_enrollment.py` 查的是公開開課查詢，只拿得到「已選人數」這個數字；
要**逐個學生**的學號姓名系級就只能登入 tch.hcu.edu.tw 的教職員服務系統。

🚨 整站 Big5，POST 的表單值也要 big5 編碼。
🚨 登入帳號是**學校 mail 帳號**（或原教師代號），不一定等於 I-Learn 帳號；
   帳密放 .env 的 HCU_TCH_USER / HCU_TCH_PASS，沒設就退回 HCU_ILEARN_USER / HCU_ILEARN_PASS。
   密碼錯或帳號不對時系統回 alert('無法取得教職員基本資料！')。

用法：
    python scripts/hcu_tch_roster.py --explore     # 印出登入後的選單連結
    python scripts/hcu_tch_roster.py               # 抓名單寫 JSON
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://tch.hcu.edu.tw'
UA = {'User-Agent': 'Mozilla/5.0'}


def env(name, *fallbacks):
    for k in (name, *fallbacks):
        v = os.environ.get(k)
        if v:
            return v
    for line in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k, v = line.split('=', 1)
            if k.strip() in (name, *fallbacks) and v.strip():
                return v.strip()
    return None


def dec(resp):
    return resp.content.decode('big5', 'replace')


def alert_of(text):
    m = re.search(r"alert\('([^']*)'\)", text)
    return m.group(1) if m else None


def _post_login(user, pw, years, term):
    # 🚨 玄奘的 DNS 會整段解不出來而主機還活著，先把 IP 釘上去（見 course_roster）。
    import course_roster
    course_roster.pin_hcu_dns()
    s = requests.Session()
    s.headers.update(UA)
    s.get(f'{BASE}/tch/prof/default.asp', timeout=40, verify=False)
    body = urllib.parse.urlencode(
        {'acdyyy': years, 'acdtype': term, 'loginname': user, 'loginpassword': pw},
        encoding='big5')
    r = s.post(f'{BASE}/EMPMain.asp', data=body, timeout=40, verify=False,
               headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return s, dec(r)


def login(user, pw, years='115', term='FIRST'):
    """登入。登入頁自己寫著「請使用 mail 帳號登入」，所以帳號含 @ 時退一步用
    local part 再試一次（有些校內 ASP 只吃 @ 前面那段）。"""
    tries = [user]
    if '@' in user:
        tries.append(user.split('@')[0])
    last = None
    for u in tries:
        s, t = _post_login(u, pw, years, term)
        last = alert_of(t)
        if not last:
            return s, t
    raise SystemExit(f'登入失敗：{last}\n'
                     '👉 教職員服務系統要的是**學校 mail 帳號或教師代號**，'
                     '跟 I-Learn（學生）帳號不是同一組。請在 .env 補 '
                     'HCU_TCH_USER / HCU_TCH_PASS。')


def links(text):
    out = []
    for m in re.finditer(r'''<a[^>]+href=["']?([^"'\s>]+)["']?[^>]*>(.*?)</a>''', text, re.S | re.I):
        u = html.unescape(m.group(1))
        label = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(2))).strip()
        out.append((label, u))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--explore', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    user = env('HCU_TCH_USER', 'HCU_ILEARN_USER')
    pw = env('HCU_TCH_PASS', 'HCU_ILEARN_PASS')
    if not user or not pw:
        raise SystemExit('缺少 HCU_TCH_USER / HCU_TCH_PASS（或 HCU_ILEARN_*）')

    s, home = login(user, pw)
    print('登入成功')
    if a.explore:
        for label, u in links(home):
            print(f'{label} | {u}')
        (ROOT / 'output' / 'hcu-tch-home.html').write_text(home, encoding='utf-8')
        print('\n已存 output/hcu-tch-home.html')


if __name__ == '__main__':
    main()
