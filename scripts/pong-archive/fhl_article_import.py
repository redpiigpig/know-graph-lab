#!/usr/bin/env python3
"""
fhl_article_import.py — 從 wf.fhl.net/article/old.html 匯入龐君華牧師文章到 pong_writings。

category='web', publication='衛蘭專文'
Usage:
  python scripts/pong-archive/fhl_article_import.py
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

BASE_URL = "https://wf.fhl.net/article/"
INDEX_FILE = ROOT / "tmp_fhl" / "articles_index.json"
LOG_FILE = ROOT / "tmp_fhl" / "article_import_log.txt"
THROTTLE_SEC = 3
PUBLICATION = "衛蘭專文"


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


def max_sort_order() -> int:
    r = requests.get(
        f"{_sb_url()}/pong_writings",
        headers=_sb_headers(),
        params={"select": "sort_order", "order": "sort_order.desc", "limit": 1},
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0]["sort_order"] if rows else 0


def article_exists_by_url(source_url: str) -> bool:
    r = requests.get(
        f"{_sb_url()}/pong_writings",
        headers=_sb_headers(),
        params={"select": "id", "source_url": f"eq.{source_url}"},
    )
    r.raise_for_status()
    return bool(r.json())


def insert_article(*, title: str, published_date: str | None, content: str,
                   source_url: str, sort_order: int) -> int:
    payload = {
        "title": title,
        "category": "web",
        "publication": PUBLICATION,
        "content": content,
        "source_url": source_url,
        "tags": ["衛蘭專文", "網路文章"],
        "is_published": True,
        "sort_order": sort_order,
    }
    if published_date:
        payload["published_date"] = published_date
    r = requests.post(
        f"{_sb_url()}/pong_writings",
        headers=_sb_headers(),
        json=payload,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()[0]["id"]


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

def parse_article_page(data: bytes) -> tuple[str | None, str | None, str | None]:
    """Returns (author, date_str, body_text). Any may be None."""
    text = data.decode("big5", errors="replace")

    # 作者
    m = re.search(r'作者[：:]?\s*<a[^>]*>\s*([^<]+)\s*</a>', text, re.S)
    author = m.group(1).strip() if m else None

    # 日期：在 <TITLE>YYYY.MM.DD...</TITLE> 或 header td
    date_str = None
    title_m = re.search(r'<TITLE>\s*(\d{4}\.\d{2}\.\d{2})', text, re.I)
    if not title_m:
        title_m = re.search(r'<td[^>]*bgcolor=["\']?#CCCCCC["\']?[^>]*>\s*(\d{4}\.\d{2}\.\d{2})', text, re.I)
    if title_m:
        date_str = title_m.group(1).replace(".", "-")  # YYYY-MM-DD

    # 正文：在 Arial size=2 > <br><br> ... <br><font face="Arial" size="2"></font>
    body_m = re.search(
        r'<font face="Arial" size="2"><br>\s*<br>\s*(.*?)<br>\s*<font face="Arial" size="2"></font>',
        text, re.S | re.I
    )
    if not body_m:
        return author, date_str, None

    body_html = body_m.group(1)
    # <p> → 段落
    body_html = re.sub(r'<p[^>]*>', '\n\n', body_html)
    body_html = re.sub(r'<br\s*/?>', '\n', body_html)
    # 移除 HTML tags
    body_html = re.sub(r'<[^>]+>', '', body_html)
    body_html = (body_html
                 .replace('&nbsp;', '')
                 .replace('&amp;', '&')
                 .replace('&lt;', '<')
                 .replace('&gt;', '>')
                 .replace('&quot;', '"'))
    lines = [ln.lstrip('　 \t') for ln in body_html.split('\n')]
    body = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()

    return author, date_str, body if len(body) > 100 else None


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
    log(f"=== fhl_article_import start — {len(entries)} entries ===")

    next_sort = max_sort_order() + 1
    log(f"next sort_order: {next_sort}")

    stats = {"imported": 0, "skip_exists": 0, "skip_author": 0, "failed": 0}

    for entry in entries:
        href  = entry["href"]
        title = entry["title"].lstrip("&nbsp;").strip()
        source_url = BASE_URL + href

        # 已入庫 → skip
        try:
            if article_exists_by_url(source_url):
                log(f"[skip-exists] {href}  {title}")
                stats["skip_exists"] += 1
                continue
        except Exception as e:
            log(f"[db-check-fail] {href}: {e}")
            stats["failed"] += 1
            continue

        time.sleep(THROTTLE_SEC)
        log(f"[fetch] {href}  {title[:50]}")
        data = fetch_page(href)
        if data is None:
            stats["failed"] += 1
            continue

        author, date_str, body = parse_article_page(data)
        log(f"  author={author!r}  date={date_str!r}  body_len={len(body) if body else 0}")

        if author is None or "龐君華" not in author:
            stats["skip_author"] += 1
            continue

        if not body:
            log(f"  [skip-no-body]")
            stats["failed"] += 1
            continue

        try:
            wid = insert_article(
                title=title,
                published_date=date_str,
                content=body,
                source_url=source_url,
                sort_order=next_sort,
            )
            log(f"  [inserted] pong_writings id={wid} sort={next_sort}")
            next_sort += 1
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
