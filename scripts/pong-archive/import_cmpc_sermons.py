#!/usr/bin/env python3
"""
從 CMPC 城中教會網站抓取 13 篇龐君華講章，匯入 pong_sermons。
這些是 pong_sermons 中缺少的篇目（其餘 29 篇已存在）。
"""
import os, re, sys, time
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DRY_RUN = "--dry-run" in sys.argv
BASE_URL = "https://cmpc.health999.net/cmpc_main/sermon/"

# 13 篇缺漏講章：(編號, 日期, 講題)
# 注意：
#   010 - 原 2004-03-14 的內容已被覆蓋，網站實際日期是 2007-02-25（大齋期第一主日）
#   028 - 內容正確(2004-10-24)，但頁面 title block 殘留前一篇的標題，需強制覆蓋
MISSING = [
    ("001", "2004-01-01", "新的期待─立約與紀律"),
    ("002", "2004-01-11", "顯現與恩典"),
    ("006", "2004-02-28", "神聖的呼召"),
    ("009", "2004-03-07", "我在那裡？"),
    ("010", "2007-02-25", "大齋期的意義與生活"),  # 原 2004 內容已消失，實際為 2007-02-25
    ("011", "2004-03-21", "大齋節期"),
    ("021", "2004-06-06", "榮歸三一主"),
    ("022", "2004-06-13", "常以為虧欠"),
    ("027", "2004-10-17", "聖道、信心與祈禱"),
    ("028", "2004-10-24", "謙卑面對上主"),        # 頁面 title 錯，強制用此標題
    ("076", "2006-10-01", "眾人之僕"),
    ("077", "2006-10-15", "失落與賞賜"),
    ("078", "2006-09-17", "靜默之言"),
]

# 強制標題覆蓋（頁面 title block 有誤的篇目）
TITLE_OVERRIDE = {
    "028": "謙卑面對上主",
}

# 教會年計算：將臨節第一主日前 → 上一年
# 2003 將臨節第一主日: 2003-11-30
# 2004 將臨節第一主日: 2004-11-28
# 2005 將臨節第一主日: 2005-11-27
ADVENT_STARTS = {
    2003: "2003-11-30",
    2004: "2004-11-28",
    2005: "2005-11-27",
    2006: "2006-12-03",
}

def church_year(date_str: str) -> int:
    y = int(date_str[:4])
    advent = ADVENT_STARTS.get(y, f"{y}-11-27")
    return y if date_str >= advent else y - 1


def _sb_url():
    return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"


def _sb_headers():
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def fetch_sermon(num: str) -> bytes:
    url = BASE_URL + f"word_{num}.htm"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content


def parse_sermon(raw: bytes) -> dict:
    text = raw.decode("cp950", errors="replace")

    # 講題
    m = re.search(r'講題：(.+?)</font>', text, re.S)
    title_raw = m.group(1).strip() if m else ""
    title_raw = re.sub(r'<[^>]+>', '', title_raw).strip()

    # 經文
    m = re.search(r'經文[:：](.+?)</b>', text, re.S)
    scripture = ""
    if m:
        scripture = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        scripture = re.sub(r'\s+', ' ', scripture)

    # 主要內容 <td>：有三個 width=751 的 td，第二個（index=1）才是正文
    blocks = re.findall(r'<td width="751">(.*?)</td>', text, re.S)
    if not blocks:
        blocks = re.findall(r'<td\s+width=751>(.*?)</td>', text, re.S)
    # 取最長的 block（通常就是正文）
    body = max(blocks, key=len) if blocks else text

    # 移除 HTML 標籤，保留 <br> 換行
    body = re.sub(r'<br\s*/?>', '\n', body, flags=re.I)
    body = re.sub(r'</p>', '\n', body, flags=re.I)
    body = re.sub(r'<[^>]+>', ' ', body)

    # HTML entities
    body = body.replace('&nbsp;', ' ')
    body = body.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    body = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), body)

    # 清理空白
    lines = []
    for ln in body.split('\n'):
        ln = ln.strip()
        if ln:
            lines.append(ln)

    # 合併列印時折行的段落（欄位換行）
    merged: list[str] = []
    buf = ""
    SENT_END = re.compile(r'[。！？」』…]$')
    for ln in lines:
        if not buf:
            buf = ln
        elif SENT_END.search(buf):
            merged.append(buf)
            buf = ln
        else:
            # 跨列繼續
            if re.search(r'[A-Za-z]$', buf) and re.search(r'^[A-Za-z]', ln):
                buf += ' ' + ln
            else:
                buf += ln
    if buf:
        merged.append(buf)

    content = '\n\n'.join(p for p in merged if p)

    return {
        "title_short": title_raw,
        "scripture": scripture,
        "content": content,
    }


def insert_sermon(sermon_id: int, title: str, date: str, scripture: str, content: str):
    cy = church_year(date)
    row = {
        "id": sermon_id,
        "title": title,
        "sermon_date": date,
        "church_year": cy,
        "liturgical_season": "pentecost",
        "location": "城中牧區",
        "scripture_ref": scripture or None,
        "content": content,
    }
    r = requests.post(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        json=row,
    )
    return r.status_code, r.text[:200] if r.status_code not in (200, 201, 204) else ""


def main():
    ok = fail = 0
    for num, date, expected_title in MISSING:
        sermon_id = int(date.replace("-", ""))
        print(f"\n[{num}] {date}  {expected_title}")

        try:
            raw = fetch_sermon(num)
            parsed = parse_sermon(raw)
        except Exception as e:
            print(f"  FETCH ERROR: {e}")
            fail += 1
            continue

        title = TITLE_OVERRIDE.get(num) or parsed["title_short"] or expected_title

        if DRY_RUN:
            print(f"  title: {title}")
            print(f"  scripture: {parsed['scripture']}")
            print(f"  church_year: {church_year(date)}")
            lines = parsed["content"].split("\n")
            print(f"  content lines: {len(lines)}")
            print(f"  first 200 chars: {parsed['content'][:200]}")
            ok += 1
            continue

        status, err = insert_sermon(
            sermon_id, title, date, parsed["scripture"], parsed["content"]
        )
        if status in (200, 201, 204):
            print(f"  HTTP {status}  OK")
            ok += 1
        else:
            print(f"  HTTP {status}  {err}")
            fail += 1

        time.sleep(0.3)

    print(f"\nDone  ok={ok}  fail={fail}")


if __name__ == "__main__":
    main()
