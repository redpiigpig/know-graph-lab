# -*- coding: utf-8 -*-
"""清掉 dialogue_days html 裡「講者標籤後又重複一次講者名」的殘留
（來源組裝時 body 開頭混進「阿周那：」等，造成 <strong>阿周那：</strong>阿周那： …）。
冪等，可重跑。用法：python scripts/dialogue_dedup_speaker.py [--dry]"""
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
H = {'apikey': K, 'Authorization': 'Bearer ' + K}
DU = f'{U}/rest/v1/dialogue_days'; SLUG = 'krishna-dialogues'
DRY = '--dry' in sys.argv
# <strong class="speaker">阿周那：</strong> 之後若又冒出同一個講者名（再加一個「：」，
# 或旁白式「阿周那問／說／道／回答」），去掉那段重複。group2=不含冒號的名字。
DUP = re.compile(r'(<strong class="speaker">([^<：]+?)：</strong>)\s*\2(?:：|問|說|道|回答|回應)?[\s，、]*')

def main():
    days = json.load(urllib.request.urlopen(urllib.request.Request(
        f'{DU}?select=day_date,html&project_slug=eq.{SLUG}&order=day_date', headers=H)))
    changed = 0
    for d in days:
        new, n = DUP.subn(r'\1', d['html'])
        if n:
            changed += 1
            print(f'{d["day_date"]}: 去重 {n} 處')
            if not DRY:
                rq = urllib.request.Request(f'{DU}?project_slug=eq.{SLUG}&day_date=eq.{d["day_date"]}',
                    data=json.dumps({'html': new}, ensure_ascii=False).encode('utf-8'), method='PATCH',
                    headers={**H, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
                urllib.request.urlopen(rq)
    print(f'\n{"[--dry] " if DRY else ""}{changed} 天有去重')

if __name__ == '__main__':
    main()
