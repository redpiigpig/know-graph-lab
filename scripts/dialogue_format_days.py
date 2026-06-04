# -*- coding: utf-8 -*-
"""把 dialogue_days 的 html 整理得更像對話錄：
  1. 日期標題 <h2> → <h3>，主題 <h3> → <h4>（階層：日期 > 主題）。
  2. 過長的單一 <p>（多半是阿周那直接貼上的長文，來源無換行）依句末標點
     重新分段成數個 <p>，每段約 110 字；保留開頭的 <strong>講者：</strong>。
克里希那的回覆原本已經是多個短 <p>，不會被動到（門檻只切長段）。

用法：
  python scripts/dialogue_format_days.py --dry   # 只看會變幾段、不寫
  python scripts/dialogue_format_days.py         # 寫回 DB
"""
import os, sys, re, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e

E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
DU = f'{U}/rest/v1/dialogue_days'
DRY = '--dry' in sys.argv
SLUG = 'krishna-dialogues'
LONG = 180        # 超過這長度的 <p> 才重新分段
TARGET = 110      # 每段目標字數

P_RE = re.compile(r'<p>(.*?)</p>', re.S)
# 講者標籤＝段落開頭、以「：」結尾的 <strong>（名字不寫死，須/希、阿周那皆通）
SPEAKER_RE = re.compile(r'^<strong[^>]*>([^<]*：)</strong>(.*)$', re.S)
MD_BOLD_RE = re.compile(r'\*\*([^*<>\n]+?)\*\*')


def reparagraph(inner):
    """inner = 一個 <p> 的內容。回傳整理後的 <p>…</p>（一段或多段）。
    - 段首講者標籤 <strong>X：</strong> 加 class="speaker"（reader 縮排用）。
    - 殘留 markdown **粗體** → <strong>。
    - 過長（多為直接貼上的長文）依句末標點重新分段。"""
    inner = MD_BOLD_RE.sub(r'<strong>\1</strong>', inner.strip())
    m = SPEAKER_RE.match(inner)
    if m:
        prefix = f'<strong class="speaker">{m.group(1)}</strong>'
        body = m.group(2).strip()
    else:
        prefix, body = '', inner
    # 已有 <br>（原文本就有換行）或不夠長 → 只套用上面的 prefix/粗體，不再切段
    if '<br>' in body or len(re.sub('<[^>]+>', '', body)) < LONG:
        return f'<p>{prefix}{body}</p>'
    # 依句末標點切句（保留標點），再合併成約 TARGET 字的段落
    sents = [s.strip() for s in re.split(r'(?<=[。！？])\s+', body) if s.strip()]
    paras, cur = [], ''
    for s in sents:
        nb = s.startswith('‧') or s.startswith('＃') or s.startswith('#')
        if cur and (nb or len(cur) >= TARGET):
            paras.append(cur); cur = s
        else:
            cur = f'{cur} {s}'.strip() if cur else s
    if cur:
        paras.append(cur)
    if not paras:
        return f'<p>{prefix}{body}</p>'
    return ''.join([f'<p>{prefix}{paras[0]}</p>'] + [f'<p>{p}</p>' for p in paras[1:]])


def format_html(html):
    # 標題降階：日期 h2→h3、主題 h3→h4（階層：日期 > 主題）
    html = html.replace('<h2>', '<h3>').replace('</h2>', '</h3>')
    html = html.replace('<h3>主題：', '<h4>主題：')
    html = re.sub(r'(<h4>主題：.*?)</h3>', r'\1</h4>', html, flags=re.S)
    html = P_RE.sub(lambda mm: reparagraph(mm.group(1)), html)
    return html


def main():
    req = urllib.request.Request(
        f'{DU}?select=day_date,html&project_slug=eq.{SLUG}&order=day_date',
        headers={'apikey': K, 'Authorization': 'Bearer ' + K})
    rows = json.load(urllib.request.urlopen(req))
    print('days:', len(rows))
    changed = 0
    for r in rows:
        old = r['html'] or ''
        new = format_html(old)
        if new == old:
            continue
        changed += 1
        d = r['day_date']
        pold, pnew = old.count('<p>'), new.count('<p>')
        print(f'{d}: <p> {pold} → {pnew}')
        if not DRY:
            body = json.dumps({'html': new}, ensure_ascii=False).encode('utf-8')
            rq = urllib.request.Request(
                f'{DU}?project_slug=eq.{SLUG}&day_date=eq.{d}', data=body, method='PATCH',
                headers={'apikey': K, 'Authorization': 'Bearer ' + K,
                         'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
            urllib.request.urlopen(rq)
    print(f'\n{"[--dry] " if DRY else ""}changed {changed}/{len(rows)} days')


if __name__ == '__main__':
    main()
