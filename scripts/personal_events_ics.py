# -*- coding: utf-8 -*-
"""家教與外務行程 → .ics，供 Google 日曆匯入。

與 weekend_classes_ics.py 分成兩個檔：授課那份是整學期固定的，這份是零星約定，
之後有變動只要重匯這一份，不會把課程事件洗掉一次。

沒說時間的就開成整日事件（家教六次、佛學研討會），不自己編一個時段填進去——
日曆上寫錯時間比沒寫更麻煩。DESCRIPTION 會標出與課表相撞的那幾筆。

用法：python scripts/personal_events_ics.py
輸出：G:\\我的雲端硬碟\\玄奘\\博一\\115-1 個人行程.ics
"""
import sys
from datetime import date, timedelta
from pathlib import Path

from weekend_classes_ics import esc, fold

OUT = Path(r'G:\我的雲端硬碟\玄奘\博一') / '115-1 個人行程.ics'

TUTOR = '天母國三家教'
_REVIEW = 'Judy 老師排的每週進度複習。時間未定，請自行拖到正確時段。'

# span＝(起, 迄) 時分秒，None 就是整日；days＝整日事件橫跨幾天
EVENTS = [
    dict(date='2026-09-06', name=TUTOR, place='天母', note=_REVIEW),
    dict(date='2026-09-13', name=TUTOR, place='天母', note=_REVIEW),
    dict(date='2026-09-19', name=TUTOR, place='天母', note=_REVIEW),
    dict(date='2026-10-03', name=f'{TUTOR}（待 Judy 確認）', place='天母',
         note=_REVIEW + ' 原訂 10/4，因 10/4 是雙週日、下午要上 PPA001，改約 10/3。'),
    dict(date='2026-10-09', name=TUTOR, place='天母',
         note=_REVIEW + ' 注意：週五晚間原本就有國中家教 19:00–20:30。'),
    dict(date='2026-10-11', name=TUTOR, place='天母', note=_REVIEW),
    dict(date='2026-09-05', name='弘誓學院地藏法會', place='佛教弘誓學院',
         note='開學前一天（學期第一週是 9/7–9/13），不撞課。時間待確認。',
         span=('090000', '120000')),
    dict(date='2026-10-05', name='濟南教會演講', place='濟南基督長老教會',
         note='⚠ 與週一國中家教 19:00–20:30 相撞，需擇一或改期。',
         span=('183000', '203000')),
    dict(date='2026-10-16', days=2, name='與 Soe San 出遊', place='',
         note='⚠ 10/16（五）晚間原本有國中家教 19:00–20:30。'
              '10/17 是雙週六，國文不上課。'),
    dict(date='2026-10-18', name='大專研究佛學研討會（協助）', place='',
         note='⚠ 衝堂：10/18 是雙週日，下午 13:10–17:00 有 PPA001 世界宗教文化導論。'
              '前兩天剛出遊回來。'),
]


def build():
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0',
         'PRODID:-//know-graph-lab//115-1 personal events//ZH-TW',
         'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:115-1 家教與外務',
         'X-WR-TIMEZONE:Asia/Taipei',
         'BEGIN:VTIMEZONE', 'TZID:Asia/Taipei',
         'BEGIN:STANDARD', 'DTSTART:19800101T000000',
         'TZOFFSETFROM:+0800', 'TZOFFSETTO:+0800', 'TZNAME:CST',
         'END:STANDARD', 'END:VTIMEZONE']

    for n, e in enumerate(EVENTS, start=1):
        start = date.fromisoformat(e['date'])
        day = start.strftime('%Y%m%d')
        span = e.get('span')
        L += ['BEGIN:VEVENT',
              f'UID:hcu-115-1-personal-{day}-{n}@know-graph-lab',
              'DTSTAMP:20260903T000000Z']
        if span:
            L += [f'DTSTART;TZID=Asia/Taipei:{day}T{span[0]}',
                  f'DTEND;TZID=Asia/Taipei:{day}T{span[1]}']
        else:
            # 整日事件的 DTEND 是結束日的隔天（iCalendar 的迄日不含當天）
            end = start + timedelta(days=e.get('days', 1))
            L += [f'DTSTART;VALUE=DATE:{day}',
                  f'DTEND;VALUE=DATE:{end.strftime("%Y%m%d")}']
        L.append(fold(f'SUMMARY:{esc(e["name"])}'))
        if e.get('place'):
            L.append(fold(f'LOCATION:{esc(e["place"])}'))
        L.append(fold(f'DESCRIPTION:{esc(e["note"])}'))
        if span:   # 整日事件不設提醒——會在前一天晚上就響，沒有意義
            L += ['BEGIN:VALARM', 'TRIGGER:-PT120M', 'ACTION:DISPLAY',
                  'DESCRIPTION:兩小時後有行程', 'END:VALARM']
        L.append('END:VEVENT')
    L.append('END:VCALENDAR')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\r\n'.join(L) + '\r\n', encoding='utf-8')
    return OUT, len(EVENTS)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p, n = build()
    print(f'✔ {p}　（{n} 筆事件）')
