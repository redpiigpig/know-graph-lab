# -*- coding: utf-8 -*-
"""把使用者手工編輯的「對話錄 docx」直接灌進 dialogue_days（取代舊的爛 recompose）。

使用者 2026-06-12：之前 LLM recompose 的克里須那回覆太囉嗦/詩化/條列，品質不好。
使用者已親手把 2026.01 整理成乾淨的對話形式（日期標題 → 阿周那：/克里須那： 流暢散文），
這就是要的成品。直接解析 docx → dialogue_days HTML，零 LLM、零失真。

docx 結構：每天 'M月D日（X）' 標題 → '阿周那：' / '克里須那：' 標籤行 → 內文段落（可多段）。
同一天若有多個區段（如 1/15 兩次）合併。輸出 dialogue_days HTML：
  <h3>2026年M月D日（星期X）</h3>
  <p><strong class="speaker">阿周那：</strong>第一段</p><p>續段</p>…
  <p><strong class="speaker">克里須那：</strong>…</p>…

用法：
  python scripts/dialogue_rewrite_from_docx.py 和檔名.docx --dry            # 印統計 + 指定日預覽
  python scripts/dialogue_rewrite_from_docx.py 和檔名.docx --day 2026-01-14 # 預覽單日 HTML
  python scripts/dialogue_rewrite_from_docx.py 和檔名.docx --write          # 寫入 dialogue_days
"""
import os, sys, re, json, html, urllib.request, datetime

sys.stdout.reconfigure(encoding='utf-8')

SLUG = 'krishna-dialogues'
AI = '克里須那'
USER = '阿周那'
WD = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日', 0: '日'}
DH = re.compile(r'^\s*(?:2026年)?(\d{1,2})月(\d{1,2})日\s*[（(]?\s*([一二三四五六日週周])?')
LABEL = re.compile(r'^\s*(阿周那|克里須那|克里希那|克里須納|克里希納)\s*[:：]\s*(.*)$')


def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e


def parse_docx(path):
    import docx
    d = docx.Document(path)
    paras = [p.text for p in d.paragraphs]
    days = {}        # date -> {'wd': str, 'turns': [[speaker, [para,...]]]}
    cur = None
    turn = None      # [speaker, [paras]]

    def flush_turn(day):
        nonlocal turn
        if turn and turn[1]:
            day['turns'].append(turn)
        turn = None

    for p in paras:
        t = p.strip()
        if not t:
            continue
        m = DH.match(t)
        if m:
            if cur:
                flush_turn(days[cur])
            mm, dd = int(m.group(1)), int(m.group(2))
            cur = f'2026-{mm:02d}-{dd:02d}'
            wd = m.group(3) or ''
            days.setdefault(cur, {'wd': wd, 'turns': []})
            if wd:
                days[cur]['wd'] = wd
            turn = None
            continue
        if cur is None:
            continue
        lm = LABEL.match(t)
        if lm:
            flush_turn(days[cur])
            speaker = USER if lm.group(1) == USER else AI
            rest = lm.group(2).strip()
            turn = [speaker, [rest] if rest else []]
        else:
            if turn is None:                 # 內文出現在標籤前（罕見）→ 當阿周那
                turn = [USER, []]
            turn[1].append(t)
    if cur:
        flush_turn(days[cur])
    return days


def weekday_of(date):
    y, m, dd = map(int, date.split('-'))
    iso = datetime.date(y, m, dd).isoweekday()   # 1=Mon..7=Sun
    return WD[iso]


def day_html(date, info):
    y, m, dd = date.split('-')
    wd = info['wd'] or weekday_of(date)
    parts = [f'<h3>{int(y)}年{int(m)}月{int(dd)}日（星期{wd}）</h3>']
    for speaker, paras in info['turns']:
        paras = [html.escape(x) for x in paras if x.strip()]
        if not paras:
            continue
        parts.append(f'<p><strong class="speaker">{speaker}：</strong>{paras[0]}</p>')
        parts.extend(f'<p>{x}</p>' for x in paras[1:])
    return ''.join(parts)


def main():
    args = sys.argv[1:]
    path = next((a for a in args if a.endswith('.docx')), None)
    if not path:
        print('需指定 .docx'); return
    DRY = '--dry' in args
    WRITE = '--write' in args
    day_arg = next((args[i + 1] for i, a in enumerate(args) if a == '--day'), None)

    days = parse_docx(path)
    print(f'解析 {path}：{len(days)} 天 → {sorted(days)}', flush=True)
    for dt in sorted(days):
        nt = len(days[dt]['turns'])
        nu = sum(1 for s, _ in days[dt]['turns'] if s == USER)
        print(f'  {dt}（{days[dt]["wd"]}）turns={nt}（{USER} {nu} / {AI} {nt-nu}）')

    if day_arg:
        print(f'\n=== {day_arg} HTML 預覽 ===')
        print(day_html(day_arg, days[day_arg])[:1600])
        return
    if DRY:
        sample = sorted(days)[1] if len(days) > 1 else sorted(days)[0]
        print(f'\n=== 範例 {sample} 前 1200 字 ===\n' + day_html(sample, days[sample])[:1200])
        return

    if WRITE:
        E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
        DBH = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}
        for dt in sorted(days):
            if not days[dt]['turns']:
                print(f'  skip {dt}（原稿空白，未覆蓋既有內容）', flush=True); continue
            y, m, dd = dt.split('-')
            wd = days[dt]['wd'] or weekday_of(dt)
            body = json.dumps({
                'html': day_html(dt, days[dt]),
                'weekday': f'星期{wd}',
                'day_title': f'{int(y)}年{int(m)}月{int(dd)}日（星期{wd}）',
                'n_turns': len(days[dt]['turns']),
            }, ensure_ascii=False).encode('utf-8')
            url = f'{U}/rest/v1/dialogue_days?project_slug=eq.{SLUG}&day_date=eq.{dt}'
            req = urllib.request.Request(url, data=body, method='PATCH',
                                         headers={**DBH, 'Prefer': 'return=minimal'})
            urllib.request.urlopen(req)
            print(f'  wrote {dt}', flush=True)
        print('完成寫入 dialogue_days。')


if __name__ == '__main__':
    main()
