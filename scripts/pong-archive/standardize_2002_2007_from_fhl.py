#!/usr/bin/env python3
"""
standardize_2002_2007_from_fhl.py
=================================
Cross-reference 2002-2007 pong_sermons rows (preacher=龐君華牧師) against
authoritative fhl.net source and replace DB.content if fhl.net version is
materially better (longer / cleaner).

Source : tmp_fhl/index.json (built earlier) + sermonNNN.html on wf.fhl.net
Target : pong_sermons.content  (and pong_media.transcript if media_id set)

Strategy:
- For each DB row in [2002-01-01, 2007-12-31]:
    * find fhl entry by sermon_date
    * fetch fhl page (urllib + big5), parse via fhl_import.parse_page
    * decide replace?
        - replace if   fhl_len  >  db_len * 1.5      (fhl much longer)
                or     db_len   <  1500              (current is a stub)
                or     '☉' in db OR DB content has chunk markers / OCR garbage
    * keep speaker label `龐君華牧師：` + blank line on top
    * PATCH pong_sermons.content
    * PATCH pong_media.transcript if media_id

Throttle 3s between fhl requests.
Progress reported every 10 rows.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from datetime import date as _date
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# Reuse parse_page from fhl_import
sys.path.insert(0, str(ROOT / "scripts" / "pong-archive"))
from fhl_import import parse_page  # type: ignore

BASE_URL = "https://wf.fhl.net/sermon/"
INDEX_FILE = ROOT / "tmp_fhl" / "index.json"
LOG_FILE = ROOT / "tmp_fhl" / "standardize_2002_2007_log.txt"
THROTTLE_SEC = 3
HTML_CACHE_DIR = ROOT / "tmp_fhl" / "html_cache"
HTML_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ─── Supabase ────────────────────────────────────────────────────────────────


def _sb_url() -> str:
    return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"


def _sb_headers(write: bool = False) -> dict:
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    if write:
        h["Content-Type"] = "application/json"
        h["Prefer"] = "return=representation"
    return h


def fetch_db_rows() -> list[dict]:
    r = requests.get(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={
            "select": "id,sermon_date,title,preacher,media_id,content",
            "preacher": "eq.龐君華牧師",
            "sermon_date": "gte.2002-01-01",
            "and": "(sermon_date.lte.2007-12-31)",
            "order": "sermon_date.asc",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def patch_sermon(sermon_id: int, content: str) -> None:
    r = requests.patch(
        f"{_sb_url()}/pong_sermons?id=eq.{sermon_id}",
        headers=_sb_headers(write=True),
        json={"content": content},
        timeout=30,
    )
    if r.status_code not in (200, 204):
        raise RuntimeError(f"PATCH sermon {sermon_id} HTTP {r.status_code}: {r.text[:300]}")


def patch_media_transcript(media_id: str, transcript: str) -> None:
    r = requests.patch(
        f"{_sb_url()}/pong_media?id=eq.{media_id}",
        headers=_sb_headers(write=True),
        json={"transcript": transcript},
        timeout=30,
    )
    if r.status_code not in (200, 204):
        raise RuntimeError(f"PATCH media {media_id} HTTP {r.status_code}: {r.text[:300]}")


# ─── HTTP fetch (with disk cache) ────────────────────────────────────────────


def fetch_html(href: str) -> bytes | None:
    cache = HTML_CACHE_DIR / href.replace("/", "_")
    if cache.exists() and cache.stat().st_size > 1000:
        return cache.read_bytes()
    url = BASE_URL + href
    try:
        time.sleep(THROTTLE_SEC)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        cache.write_bytes(data)
        return data
    except Exception as e:
        log(f"  [FETCH-FAIL] {url}: {e}")
        return None


# ─── Decision logic ──────────────────────────────────────────────────────────


def should_replace(db_content: str, fhl_body: str) -> tuple[bool, str]:
    """fhl.net is authoritative — replace whenever fhl_body is reasonable."""
    db_len = len(db_content or "")
    fhl_len = len(fhl_body or "")
    if fhl_len < 500:
        return False, f"fhl too short ({fhl_len}) — likely parse failure"
    return True, f"fhl authoritative (db={db_len} → fhl={fhl_len})"


def build_content(fhl_body: str, db_content: str) -> str:
    # Always start with canonical speaker label + blank line
    body = fhl_body.strip()
    # Drop leading speaker label if already in body (avoid duplication)
    if body.startswith("龐君華"):
        # already labelled
        return body if body.endswith("\n") else body + "\n"
    return f"龐君華牧師：\n\n{body}\n"


# ─── Logging ─────────────────────────────────────────────────────────────────


def log(msg: str) -> None:
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────


def main() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log(f"=== standardize 2002-2007 龐 from fhl.net — start ===")

    idx = json.load(open(INDEX_FILE, encoding="utf-8"))
    fhl_by_date: dict[str, dict] = {e["date"].replace(".", "-"): e for e in idx}

    db_rows = fetch_db_rows()
    log(f"DB rows: {len(db_rows)}   fhl entries: {len(fhl_by_date)}")

    stats = {"updated": 0, "kept": 0, "no_match": 0, "fetch_fail": 0, "parse_fail": 0, "patch_fail": 0}
    media_synced = 0

    for i, row in enumerate(db_rows, 1):
        sid = row["id"]
        d = row["sermon_date"]
        title = row.get("title") or ""
        db_content = row.get("content") or ""
        media_id = row.get("media_id")

        entry = fhl_by_date.get(d)
        if not entry:
            log(f"[no-match] {d}  id={sid}  '{title[:30]}'")
            stats["no_match"] += 1
            continue

        href = entry["href"]
        log(f"[{i}/{len(db_rows)}] {d}  id={sid}  href={href}  '{title[:30]}'")

        data = fetch_html(href)
        if data is None:
            stats["fetch_fail"] += 1
            continue

        author, body = parse_page(data)
        if not body:
            log(f"  [parse-fail] author={author!r}")
            stats["parse_fail"] += 1
            continue

        if author and "龐" not in author:
            log(f"  [skip-author-mismatch] author={author!r}")
            stats["kept"] += 1
            continue

        ok, reason = should_replace(db_content, body)
        log(f"  decision: {'REPLACE' if ok else 'KEEP'} — {reason}")
        if not ok:
            stats["kept"] += 1
            continue

        new_content = build_content(body, db_content)
        try:
            patch_sermon(sid, new_content)
            stats["updated"] += 1
            log(f"  [patched] sermons.content len={len(new_content)}")
            if media_id:
                try:
                    patch_media_transcript(media_id, new_content)
                    media_synced += 1
                    log(f"  [patched] media.transcript {media_id}")
                except Exception as e:
                    log(f"  [media-patch-fail] {e}")
        except Exception as e:
            log(f"  [patch-fail] {e}")
            stats["patch_fail"] += 1

        # Progress every 10
        if i % 10 == 0:
            log(f"--- progress: {i}/{len(db_rows)}   updated={stats['updated']}  kept={stats['kept']}  fail={stats['fetch_fail']+stats['parse_fail']+stats['patch_fail']} ---")

    log(
        f"\n=== DONE  updated={stats['updated']}  kept={stats['kept']}  "
        f"no_match={stats['no_match']}  fetch_fail={stats['fetch_fail']}  "
        f"parse_fail={stats['parse_fail']}  patch_fail={stats['patch_fail']}  "
        f"media_synced={media_synced} ==="
    )


if __name__ == "__main__":
    main()
