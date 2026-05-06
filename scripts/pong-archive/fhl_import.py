#!/usr/bin/env python3
"""
fhl_import.py — 從 wf.fhl.net/sermon/old.html 匯入龐君華牧師講章到 pong_sermons。

Usage:
  python scripts/pong-archive/fhl_import.py

設計原則：
- 每次 HTTP request 前 sleep THROTTLE_SEC 秒
- 單次嘗試，失敗記 log 繼續，絕不 retry
- DB 已存在同日期的 row → skip（不覆蓋）
- 只匯入 pong_sermons（無 YouTube 音檔，不建 pong_media row）
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
import urllib.request
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

BASE_URL = "https://wf.fhl.net/sermon/"
INDEX_FILE = ROOT / "tmp_fhl" / "index.json"
LOG_FILE = ROOT / "tmp_fhl" / "import_log.txt"
THROTTLE_SEC = 3


# ─── Supabase ────────────────────────────────────────────────────────────────

def _sb_url() -> str:
    return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"


def _sb_headers() -> dict:
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def sermon_exists(date_str: str) -> bool:
    r = requests.get(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={"select": "id", "sermon_date": f"eq.{date_str}"},
    )
    r.raise_for_status()
    return bool(r.json())


def insert_sermon(date_str: str, title: str, content: str) -> int:
    year, month = int(date_str[:4]), int(date_str[5:7])
    church_year = year if month == 12 else year - 1
    sermon_id = int(date_str.replace("-", ""))
    r = requests.post(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        json={
            "id": sermon_id,
            "sermon_date": date_str,
            "title": title,
            "church_year": church_year,
            "preacher": "龐君華牧師",
            "location": "城中牧區",
            "content": content,
            "has_recording": False,
            "is_published": False,
        },
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return sermon_id


# ─── HTTP fetch ──────────────────────────────────────────────────────────────

def fetch_page(href: str) -> bytes | None:
    url = BASE_URL + href
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read()
    except Exception as e:
        log(f"  [FETCH-FAIL] {url}: {e}")
        return None


# ─── HTML parsing ────────────────────────────────────────────────────────────

def _extract_font_block(text: str, font_face: str) -> str | None:
    """Extract content of <font face="FONT_FACE"> block with proper nesting."""
    # Use <font[^>]*face= so attribute order doesn't matter (e.g. size=+1 face="標楷體")
    pat = re.compile(r'<font\b[^>]*face="[^"]*' + re.escape(font_face) + r'[^"]*"[^>]*>', re.I)
    m = pat.search(text)
    if not m:
        return None
    pos = m.end()
    depth = 1
    result_end = pos
    while pos < len(text) and depth > 0:
        next_open = re.search(r'<font\b', text[pos:], re.I)
        next_close = re.search(r'</font>', text[pos:], re.I)
        if next_close is None:
            break
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos += next_open.end()
        else:
            depth -= 1
            result_end = pos + next_close.start()
            pos += next_close.end()
    return text[m.end():result_end]


def parse_page(data: bytes) -> tuple[str | None, str | None]:
    """Returns (author_display_name, cleaned_body_text). Either may be None."""
    text = data.decode("big5", errors="replace")

    # 作者:<a href="mailto:...">顯示名稱</a>
    m = re.search(r'作者[：:]?\s*<a[^>]*>\s*([^<]+)\s*</a>', text, re.S)
    author = m.group(1).strip() if m else None

    # 嘗試抽取 新細明體 字體區塊（含正文），正確處理嵌套 font tag
    body_html = _extract_font_block(text, "新細明體")
    if not body_html:
        # 部分龐牧師頁面用 標楷體
        body_html = _extract_font_block(text, "標楷體")
    if not body_html:
        return author, None

    # 移除頂部 <center>...<br/> (標題 + 經文)
    body_html = re.sub(r'<center>.*?</center>\s*<br\s*/?>', '', body_html, flags=re.S)
    # 移除底部 【日期 + 地點】 標記
    body_html = re.sub(r'【[^】]+】', '', body_html)
    # <p> → 段落分隔
    body_html = re.sub(r'<p[^>]*>', '\n\n', body_html)
    body_html = re.sub(r'<br\s*/?>', '\n', body_html)
    # 清除剩餘 HTML tags
    body_html = re.sub(r'<[^>]+>', '', body_html)
    # HTML entities
    body_html = (body_html
                 .replace('&nbsp;', '')
                 .replace('&amp;', '&')
                 .replace('&lt;', '<')
                 .replace('&gt;', '>')
                 .replace('&quot;', '"'))
    # 移除每行開頭的全形空格
    lines = [ln.lstrip('　 \t') for ln in body_html.split('\n')]
    body = '\n'.join(lines).strip()
    # 壓縮三個以上連續空行為兩個
    body = re.sub(r'\n{3,}', '\n\n', body)

    return author, body if len(body) > 200 else None


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    with open(INDEX_FILE, encoding="utf-8") as f:
        entries = json.load(f)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log(f"=== fhl_import start — {len(entries)} entries ===")

    stats = {"imported": 0, "skip_exists": 0, "skip_author": 0, "failed": 0}

    for i, entry in enumerate(entries):
        href  = entry["href"]
        title = entry["title"]
        date_str = entry["date"].replace(".", "-")  # "YYYY.MM.DD" → "YYYY-MM-DD"

        # DB 已有同日期 → skip
        try:
            if sermon_exists(date_str):
                log(f"[skip-exists] {date_str}  {title}")
                stats["skip_exists"] += 1
                continue
        except Exception as e:
            log(f"[db-check-fail] {date_str}: {e}")
            stats["failed"] += 1
            continue

        # 每次 fetch 前 sleep（第一篇也等，距離上次 index fetch 已夠久）
        time.sleep(THROTTLE_SEC)

        log(f"[fetch] {href}  {date_str}  {title}")
        data = fetch_page(href)
        if data is None:
            stats["failed"] += 1
            continue

        author, body = parse_page(data)
        log(f"  author={author!r}  body_len={len(body) if body else 0}")

        if author is None or "龐" not in author:
            stats["skip_author"] += 1
            continue

        if not body:
            log(f"  [skip-no-body]")
            stats["failed"] += 1
            continue

        content = f"龐君華牧師：\n\n{body}\n"

        try:
            sid = insert_sermon(date_str, title, content)
            log(f"  [inserted] pong_sermons id={sid}")
            stats["imported"] += 1
        except Exception as e:
            log(f"  [db-insert-fail] {e}")
            stats["failed"] += 1

    log(
        f"\n=== DONE  imported={stats['imported']}  "
        f"skip_exists={stats['skip_exists']}  "
        f"skip_author={stats['skip_author']}  "
        f"failed={stats['failed']} ==="
    )


if __name__ == "__main__":
    main()
