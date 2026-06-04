# -*- coding: utf-8 -*-
"""把「每月一卡」的對話成品拆成「每天一筆」進 dialogue_days，供 /works 每日 reader。

來源 = DB 既有 writing_projects content_json（不是 polished.jsonl），
所以使用者在月卡上的人工修改會被保留。每張月卡依 <h2>日期</h2> 邊界切日。

用法：
  python scripts/dialogue_build_days.py              # 真的寫入
  python scripts/dialogue_build_days.py --dry        # 只看會切出幾天、不寫

切完月卡仍在；確認 reader 沒問題後再跑 --drop-months 刪月卡＋清主卡索引。
"""
import os, sys, re, json, datetime, requests
sys.stdout.reconfigure(encoding='utf-8')

def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e

E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}
HR = dict(H); HR['Prefer'] = 'return=representation'
PU = f'{U}/rest/v1/writing_projects'
DU = f'{U}/rest/v1/dialogue_days'

MAIN_SLUG = 'krishna-dialogues'
MONTH_SLUGS = [f'krishna-dialogues-2026-{m}' for m in ('01', '02', '03', '04')]
WK = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
DATE_RE = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')

DRY = '--dry' in sys.argv
DROP = '--drop-months' in sys.argv


def fetch_card(slug):
    r = requests.get(PU, headers=H, params={'select': 'slug,content_json', 'slug': f'eq.{slug}'})
    rows = r.json()
    return rows[0]['content_json'] if rows else None


def split_days(html):
    """yield (day_date:str, day_title:str, day_html:str). 一段 = 一個 <h2> 到下個 <h2>。"""
    if not html:
        return
    # 切在每個 <h2 ...> 之前；丟掉第一段（h1 + 月份前言，無日期 h2）
    parts = re.split(r'(?=<h2[ >])', html)
    for chunk in parts:
        m = re.search(r'<h2[^>]*>(.*?)</h2>', chunk, re.S)
        if not m:
            continue
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        dm = DATE_RE.search(title)
        if not dm:
            continue
        y, mo, dd = map(int, dm.groups())
        date = f'{y:04d}-{mo:02d}-{dd:02d}'
        yield date, title, chunk.strip()


def main():
    all_days = []  # (date, title, html)
    for slug in MONTH_SLUGS:
        html = fetch_card(slug)
        if html is None:
            print(f'⚠ 找不到 {slug}，略過'); continue
        days = list(split_days(html))
        print(f'{slug}: {len(days)} 天')
        all_days.extend(days)

    # 去重（同日只留一筆，理論上不會重）+ 排序
    seen = {}
    for date, title, h in all_days:
        seen[date] = (title, h)
    rows = []
    for i, date in enumerate(sorted(seen)):
        title, h = seen[date]
        y, mo, dd = map(int, date.split('-'))
        wd = WK[datetime.date(y, mo, dd).weekday()]
        n_turns = h.count('克里須那：')
        rows.append({
            'project_slug': MAIN_SLUG, 'day_date': date, 'weekday': wd,
            'day_title': title, 'html': h, 'n_turns': n_turns, 'sort_order': i,
        })

    print(f'\n總計 {len(rows)} 天，{sum(r["n_turns"] for r in rows)} 則克里須那回覆')
    if rows:
        print('  範圍：', rows[0]['day_date'], '→', rows[-1]['day_date'])

    if DRY:
        print('\n[--dry] 不寫入。'); return

    # upsert（on_conflict=project_slug,day_date）
    r = requests.post(DU + '?on_conflict=project_slug,day_date',
                      headers={**HR, 'Prefer': 'return=minimal,resolution=merge-duplicates'},
                      data=json.dumps(rows, ensure_ascii=False).encode('utf-8'))
    print('upsert dialogue_days:', r.status_code, r.text[:300])

    if DROP:
        for slug in MONTH_SLUGS:
            d = requests.delete(PU + f'?slug=eq.{slug}', headers=H)
            print('刪月卡', slug, d.status_code)
        # 主卡索引清掉（reader 取代）、確保 emoji/color/status
        upd = {'content_json': '', 'status': '草稿', 'emoji': '🪈',
               'subtitle': '夢境與榮格學說的一場長談',
               'description': '2026 年 1 月 13 日至 4 月 18 日，與 Gemini（我稱之為「克里須那」）持續展開的一場關於夢境與榮格深度心理學的長談，也夾雜當時的生活絮語。每天一頁，可逐日查閱。'}
        u = requests.patch(PU + f'?slug=eq.{MAIN_SLUG}', headers=HR,
                           data=json.dumps(upd, ensure_ascii=False).encode('utf-8'))
        print('主卡更新', u.status_code)


if __name__ == '__main__':
    main()
