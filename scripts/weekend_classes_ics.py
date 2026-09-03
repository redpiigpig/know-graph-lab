# -*- coding: utf-8 -*-
"""週末授課日期 → .ics，供 Google 日曆匯入。

沒有寫入 Google 日曆的工具，因此改產生標準 iCalendar 檔：
Google 日曆 → 設定 → 匯入與匯出 → 匯入，選這個檔即可。
匯入時要選「115-1 玄奘教課」那個日曆，顏色才會是深綠——
Google 的顏色綁在日曆上，不吃檔案裡的事件顏色。

日期依學期週次（第一週 9/7–9/13）推得，與使用者給的雙週日全部吻合。
每筆事件的說明欄寫該次要講的章節，上課前打開日曆就知道進度。

用法：python scripts/weekend_classes_ics.py
輸出：G:\\我的雲端硬碟\\玄奘\\博一\\115-1 玄奘教課.ics
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(r'G:\我的雲端硬碟\玄奘\博一') / '115-1 玄奘教課.ics'

SAT = ['2026-09-12', '2026-09-26', '2026-10-10', '2026-10-24', '2026-11-07',
       '2026-11-21', '2026-12-05', '2026-12-19', '2027-01-02']
SUN = ['2026-09-20', '2026-10-04', '2026-10-18', '2026-11-01', '2026-11-15',
       '2026-11-29', '2026-12-13', '2026-12-27', '2027-01-10']

COURSES = [
    dict(name='國文（PPA066）', room='妙然 206', dates=SAT,
         chapters='public/content/works/sinographic-literature/chapters',
         tail='自由學習：個別與老師討論自評'),
    dict(name='世界宗教文化導論（PPA001）', room='妙然 401', dates=SUN,
         chapters='public/content/works/world-religions-intro/chapters-wr2',
         tail='自由學習：個別與老師討論自評'),
]

START, END = '131000', '170000'


def chapter_title(chapters, n):
    f = ROOT / chapters / f'ch{n:02d}.html'
    h = re.search(r'<h2>(.*?)</h2>', f.read_text(encoding='utf-8')).group(1)
    return re.sub(r'<[^>]+>', '', h).strip()


def fold(line):
    """iCalendar 一行最多 75 個八位元組，超過要折行（續行以一個空白開頭）。"""
    b = line.encode('utf-8')
    if len(b) <= 73:
        return line
    out, cur = [], b''
    for ch in line:
        e = ch.encode('utf-8')
        if len(cur) + len(e) > 73:
            out.append(cur.decode('utf-8'))
            cur = b' '
        cur += e
    out.append(cur.decode('utf-8'))
    return '\r\n'.join(out)


def esc(s):
    return s.replace('\\', '\\\\').replace(';', r'\;').replace(',', r'\,')


def build():
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0',
         'PRODID:-//know-graph-lab//115-1 weekend classes//ZH-TW',
         'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:115-1 玄奘教課',
         'X-WR-TIMEZONE:Asia/Taipei',
         # Google 匯入不吃事件層顏色，顏色綁在日曆上；這兩行是給 Apple 行事曆看的
         'COLOR:#0B8043', 'X-APPLE-CALENDAR-COLOR:#0B8043',   # 羅勒葉／深綠
         'BEGIN:VTIMEZONE', 'TZID:Asia/Taipei',
         'BEGIN:STANDARD', 'DTSTART:19800101T000000',
         'TZOFFSETFROM:+0800', 'TZOFFSETTO:+0800', 'TZNAME:CST',
         'END:STANDARD', 'END:VTIMEZONE']

    n = 0
    for c in COURSES:
        for i, d in enumerate(c['dates']):
            day = d.replace('-', '')
            if i == 8:
                topic = c['tail']
            else:
                a, b = 2 * i + 1, 2 * i + 2
                topic = (f'{chapter_title(c["chapters"], a)}／'
                         f'{chapter_title(c["chapters"], b)}')
            n += 1
            L += [
                'BEGIN:VEVENT',
                f'UID:hcu-115-1-{day}-{n}@know-graph-lab',
                'DTSTAMP:20260903T000000Z',
                f'DTSTART;TZID=Asia/Taipei:{day}T{START}',
                f'DTEND;TZID=Asia/Taipei:{day}T{END}',
                fold(f'SUMMARY:{esc(c["name"])}　第 {i + 1} 次'),
                fold(f'LOCATION:{esc("玄奘大學 " + c["room"])}'),
                fold(f'DESCRIPTION:{esc(topic)}'),
                'BEGIN:VALARM', 'TRIGGER:-PT60M', 'ACTION:DISPLAY',
                'DESCRIPTION:一小時後上課', 'END:VALARM',
                'END:VEVENT',
            ]
    L.append('END:VCALENDAR')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\r\n'.join(L) + '\r\n', encoding='utf-8')
    return OUT, n


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p, n = build()
    print(f'✔ {p}　（{n} 筆事件）')
