"""把玄奘 I-Learn（Moodle）課程裡的「資料夾」模組整批換成新檔（教師帳號）。

Moodle 的 web service 沒有「往資料夾加檔」的函式，所以走網頁表單：
  token.php 拿 token＋privatetoken → tool_mobile_get_autologin_key（🚨 UA 要帶 MoodleMobile，
  否則回 apprequired）→ autologin.php 換成網頁 session → 開 modedit.php 編輯頁
  → 對表單的 draft 區刪舊檔、上傳新檔 → 原樣送回表單。

帳密讀 .env 的 HCU_ILEARN_TEACHER_USER / HCU_ILEARN_TEACHER_PASS。

用法（在程式裡呼叫）：
    s = session()
    replace_folder(s, cmid, [Path(...), ...], names={Path: '上傳後檔名'})
    create_folder(s, course_id, section, '課程簡介', [Path(...)])
    加 dry=True 只印計畫不送出。
"""
import html
import json
import re
import sys
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()
sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_roster import pin_hcu_dns  # noqa: E402
import hcu_ilearn_sync as H  # noqa: E402

B = H.BASE
UPLOAD_REPO = '4'   # 「上傳一個檔案」repository 的 id（2026-10-01 從編輯頁讀出）


COOKIE = Path(__file__).resolve().parent.parent / 'output' / 'hcu-ilearn-cookies.pkl'


def session():
    """🚨 autologin 金鑰 6 分鐘內只能產生一次（autologinkeygenerationlockout），
    所以登入後把 cookie 存在 output/（不進版控），下次先試舊 session 還活不活。"""
    import pickle
    pin_hcu_dns()
    e = H.load_env()
    if COOKIE.exists():
        s = requests.Session()
        s.headers['User-Agent'] = 'Mozilla/5.0'
        s.verify = False
        s.cookies = pickle.load(open(COOKIE, 'rb'))
        if 'sesskey' in s.get(B + '/my/', timeout=60).text:
            return s
    d = requests.post(B + '/login/token.php', timeout=60, verify=False, data={
        'username': e['HCU_ILEARN_TEACHER_USER'], 'password': e['HCU_ILEARN_TEACHER_PASS'],
        'service': 'moodle_mobile_app'}).json()
    if 'token' not in d:
        raise SystemExit('I-Learn 教師帳號登入失敗：' + d.get('errorcode', '?'))
    tok = d['token']
    uid = H.ws(tok, 'core_webservice_get_site_info')['userid']
    k = requests.post(B + '/webservice/rest/server.php', timeout=60, verify=False,
                      headers={'User-Agent': 'Mozilla/5.0 MoodleMobile 4.4.0'},
                      data={'wstoken': tok, 'wsfunction': 'tool_mobile_get_autologin_key',
                            'moodlewsrestformat': 'json', 'privatetoken': d['privatetoken']}).json()
    if 'key' not in k:
        raise SystemExit('autologin 失敗：' + k.get('errorcode', '?'))
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0'
    s.verify = False
    s.get(k['autologinurl'], params={'userid': uid, 'key': k['key'],
                                     'urltogo': B + '/my/'}, timeout=60)
    COOKIE.parent.mkdir(exist_ok=True)
    pickle.dump(s.cookies, open(COOKIE, 'wb'))
    return s


def _form(text):
    """解析 modedit 表單：回傳 [(name, value)]，照瀏覽器送出的規則（checkbox 只送勾選的）。"""
    f = re.search(r'<form[^>]*class="[^"]*mform[^"]*".*?</form>', text, re.S).group(0)
    out = []
    for tag in re.finditer(r'<(input|select|textarea)\b([^>]*)>(.*?)(?=<(?:input|select|textarea)\b|</form>)',
                           f, re.S):
        kind, attrs, rest = tag.groups()
        n = re.search(r'\bname="([^"]*)"', attrs)
        if not n or 'disabled' in attrs:
            continue
        name = html.unescape(n.group(1))
        ty = (re.search(r'\btype="([^"]*)"', attrs) or [None, 'text'])[1]
        val = re.search(r'\bvalue="([^"]*)"', attrs)
        val = html.unescape(val.group(1)) if val else ''
        if kind == 'input':
            if ty in ('submit', 'button', 'image', 'file'):
                continue
            if ty in ('checkbox', 'radio') and 'checked' not in attrs:
                continue
            out.append((name, val))
        elif kind == 'textarea':
            out.append((name, html.unescape(rest.split('</textarea>')[0])))
        else:  # select
            body = rest.split('</select>')[0]
            opts = re.findall(r'<option\b([^>]*)>', body)
            chosen = [o for o in opts if 'selected' in o]
            multi = 'multiple' in attrs
            for o in (chosen if (chosen or multi) else opts[:1]):
                v = re.search(r'value="([^"]*)"', o)
                out.append((name, html.unescape(v.group(1)) if v else ''))
    return out


def _draft_files(s, sesskey, itemid):
    r = s.post(B + '/repository/draftfiles_ajax.php', params={'action': 'list'},
               data={'sesskey': sesskey, 'itemid': itemid, 'filepath': '/'}, timeout=60).json()
    return [x['filename'] for x in r.get('list', [])]


def _edit(s, url, files, names=None, dry=False, extra=None):
    names = names or {}
    t = s.get(url, timeout=60).text
    fields = _form(t)
    fd = dict(fields)
    sesskey, itemid = fd['sesskey'], fd['files']
    ctx = re.search(r'"ctx_id"\s*:\s*"?(\d+)', t) or re.search(r'contextid["\s:=]+"?(\d+)', t)
    ctx = ctx.group(1)
    old = _draft_files(s, sesskey, itemid)
    new = [names.get(p, p.name) for p in files]
    print(f'  舊檔 {len(old)}：', *old, sep='\n    ')
    print(f'  新檔 {len(new)}：', *new, sep='\n    ')
    if dry:
        return
    for fn in old:
        s.post(B + '/repository/draftfiles_ajax.php', params={'action': 'delete'}, timeout=60,
               data={'sesskey': sesskey, 'itemid': itemid, 'filepath': '/', 'filename': fn})
    for p in files:
        fn = names.get(p, p.name)
        with open(p, 'rb') as fh:
            r = s.post(B + '/repository/repository_ajax.php', params={'action': 'upload'}, timeout=600,
                       files={'repo_upload_file': (fn, fh)},
                       data={'sesskey': sesskey, 'repo_id': UPLOAD_REPO, 'itemid': itemid,
                             'savepath': '/', 'title': fn, 'ctx_id': ctx, 'env': 'filemanager',
                             'author': '張辰瑋', 'license': 'allrightsreserved',
                             'overwrite': '1'})
        j = r.json()
        if 'error' in j or 'event' in j and j['event'] == 'fileexists':
            raise SystemExit(f'上傳失敗 {fn}：{j}')
    got = _draft_files(s, sesskey, itemid)
    if sorted(got) != sorted(new):
        raise SystemExit(f'draft 區內容不符，未送出表單：{got}')
    fields = [(k, v) for k, v in fields if k not in (extra or {})] + list((extra or {}).items())
    fields.append(('submitbutton2', '儲存並返回課程'))
    r = s.post(B + '/course/modedit.php', data=fields, timeout=120)
    if 'modedit.php' in r.url:
        err = re.findall(r'class="[^"]*error[^"]*"[^>]*>([^<]{2,120})', r.text)
        raise SystemExit(f'表單送出失敗：{err[:3]}')
    print('  ✔ 已儲存')


def replace_folder(s, cmid, files, names=None, dry=False):
    print(f'資料夾 cmid={cmid}')
    _edit(s, f'{B}/course/modedit.php?update={cmid}', files, names, dry)


def create_folder(s, course, section, name, files, names=None, dry=False):
    print(f'新資料夾「{name}」course={course} section={section}')
    _edit(s, f'{B}/course/modedit.php?add=folder&type=&course={course}&section={section}&return=0&sr=0',
          files, names, dry, extra={'name': name})


def folder_files(token, course):
    """回傳 {cmid: (資料夾名, [檔名])}，上傳後核對用。"""
    out = {}
    for sec in H.ws(token, 'core_course_get_contents', courseid=course):
        for m in sec.get('modules', []):
            if m['modname'] == 'folder':
                out[m['id']] = (m['name'], [c['filename'] for c in m.get('contents') or []])
    return out
