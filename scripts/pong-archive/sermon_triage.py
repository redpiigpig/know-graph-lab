#!/usr/bin/env python3
"""
sermon_triage.py — overnight autopilot for 2020+ queue files.

For each ⏳ entry: download audio, Whisper-transcribe ONLY the first chunk
(20 min), apply heuristics to identify the preacher.
- If 邱牧師 / other guest detected → mark ⛔ 別人 + delete orphan DB rows.
- If 龐牧師 candidate → keep ⏳ 未完成 (so manual cleaning can proceed later).
- The triage transcript is saved as <date>_triage.txt for review.

Heuristic signals:
  邱牧師 strong signals (→ ⛔):
    - "在香港" / "我從香港" / "住山" / "半山"  (autobiographical)
    - "跟龐會督" / "跟龐惠都" / "跟盛惠都"  (refers to 龐 in 3rd person)

  龐牧師 strong signals (→ keep ⏳):
    - "丘牧師" / "邱牧師" addressed in 1st few lines (greeting)
    - "我過去在總會服侍"

  Other guest signals (→ ⛔):
    - "感謝[X名字]的證道" with X != 龐
    - "第一次來到城中教會" / "謝謝邀請"

Default: KEEP as ⏳ (so manual review picks up uncertain cases).

Usage:
  python sermon_triage.py YEAR_TXT_FILE [...] [--full]

  --full: also do FULL transcription (for cleaning) when 龐 candidate found.
          Without it, triage only saves first chunk.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from pong_sermon_pipeline import (
    download_audio,
    extract_youtube_id,
    fetch_youtube_metadata,
    transcribe,
)
from sermon_redo import (
    parse_queue,
    rewrite_marker,
    find_sermon_by_date,
    TMP_DIR,
)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS_RW = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


# Heuristic patterns
QIU_SELF_REF = re.compile(
    r"在香港|我從香港|我从香港|住山|半山|跟龐會督|跟庞会督|跟龐惠都|跟盛惠都|跟龎會督"
)
PONG_THIRD_PERSON_GREETING = re.compile(
    r"(丘|邱)牧師.{0,8}(各位|弟兄|大家)|(丘|邱)牧師.{0,3}今天.{0,3}(在|不在|主理|證道|講道|佈道|步道)"
)
PONG_SELF_REF = re.compile(
    r"我過去在總會|我以前在總會|我担任会督|我擔任會督|當會督的時候|做會督"
)
GUEST_THANK = re.compile(
    r"感謝.{1,10}(牧師|傳道|會督|長老).{0,5}(證道|講道|信息|分享)"
)
GUEST_INTRO = re.compile(
    r"第一次來到.{0,4}(城中|本堂)|很高興.{0,8}邀請.{0,8}講"
)


def classify(triage_text):
    """Apply heuristics. Returns ('skip'|'pong'|'unsure', reason_str)."""
    t = triage_text

    # 1. Strong 邱 signals
    m = QIU_SELF_REF.search(t)
    if m:
        return "skip", f"邱牧師自述/3人稱龐: 「{m.group(0)}」"

    # 2. 龐 in greeting (preacher addresses 邱牧師 from pulpit)
    m = PONG_THIRD_PERSON_GREETING.search(t)
    if m:
        return "pong", f"問候/提到邱牧師: 「{m.group(0)}」"

    # 3. 龐 self-reference (former 會督 service)
    m = PONG_SELF_REF.search(t)
    if m:
        return "pong", f"龐牧師自述: 「{m.group(0)}」"

    # 4. Other guest preacher
    m = GUEST_INTRO.search(t)
    if m:
        return "skip", f"其他客座: 「{m.group(0)}」"

    m = GUEST_THANK.search(t)
    if m and "龐" not in m.group(0):
        return "skip", f"其他客座: 「{m.group(0)}」"

    return "unsure", "無明顯訊號"


def delete_orphan_rows(sermon_id, media_id):
    """Delete pong_sermons + pong_media rows."""
    if sermon_id:
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/pong_sermons?id=eq.{sermon_id}",
            headers=HEADERS_RW,
            timeout=30,
        )
        print(f"  [del] pong_sermons {sermon_id}: {r.status_code}")
    if media_id:
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/pong_media?id=eq.{media_id}",
            headers=HEADERS_RW,
            timeout=30,
        )
        print(f"  [del] pong_media {media_id}: {r.status_code}")


def upsert_sermon_and_media(date_iso, title, url, meta):
    """Mirror sermon_redo logic to ensure rows exist for triage."""
    youtube_id = extract_youtube_id(url)

    # pong_media: lookup by youtube_id
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/pong_media?youtube_id=eq.{youtube_id}&select=id",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        timeout=30,
    )
    rows = r.json()
    if rows:
        media_id = rows[0]["id"]
    else:
        body = {
            "youtube_id": youtube_id,
            "title": meta.get("title", title),
            "duration_sec": meta.get("duration", 0),
            "broadcast_date": date_iso,
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/pong_media",
            headers={**HEADERS_RW, "Prefer": "return=representation"},
            json=body,
            timeout=30,
        )
        r.raise_for_status()
        media_id = r.json()[0]["id"]

    # pong_sermons: id = YYYYMMDD
    sermon_id = int(date_iso.replace("-", ""))
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/pong_sermons?id=eq.{sermon_id}&select=id,media_id",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        timeout=30,
    )
    rows = r.json()
    if not rows:
        # Compute church_year (Advent-start)
        from datetime import date as _d
        d = _d.fromisoformat(date_iso)
        church_year = d.year if d.month < 12 else d.year + 1
        body = {
            "id": sermon_id,
            "sermon_date": date_iso,
            "church_year": church_year,
            "title": title,
            "media_id": media_id,
            "preacher": "龐君華牧師",
            "location": "城中教會",
            "has_recording": True,
            "is_published": False,
        }
        requests.post(
            f"{SUPABASE_URL}/rest/v1/pong_sermons",
            headers=HEADERS_RW,
            json=body,
            timeout=30,
        )

    return sermon_id, media_id


def process_entry(entry, txt_path, do_full=False):
    """Triage one entry. Returns 'pong' / 'skip' / 'unsure'."""
    print(f"\n=== {entry.date} {entry.title} ===")
    print(f"    {entry.url}")

    youtube_id = extract_youtube_id(entry.url)
    triage_file = TMP_DIR / f"{entry.date}_triage.txt"

    # Skip if triage already exists (resume support)
    if triage_file.exists() and triage_file.stat().st_size > 200:
        print(f"  [skip] triage already exists: {triage_file}")
        triage_text = triage_file.read_text(encoding="utf-8")
    else:
        # Get metadata + create DB rows
        try:
            meta = fetch_youtube_metadata(entry.url)
        except Exception as e:
            print(f"  [error] metadata fetch failed: {e}")
            return "error"

        sermon_id, media_id = upsert_sermon_and_media(
            entry.date, entry.title, entry.url, meta
        )
        print(f"  [db] sermon={sermon_id} media={media_id}")

        # Download + Whisper FIRST chunk only
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = Path(tmpdir) / f"{youtube_id}.mp3"
            try:
                download_audio(entry.url, audio_path)
            except Exception as e:
                print(f"  [error] download failed: {e}")
                return "error"
            triage_text = transcribe(audio_path, lang="zh", max_chunks=1)
        triage_file.write_text(triage_text, encoding="utf-8")
        print(f"  [triage] {len(triage_text)} chars")

    # Classify
    decision, reason = classify(triage_text)
    print(f"  [classify] {decision}: {reason}")

    if decision == "skip":
        # Delete orphan rows + mark ⛔ 別人
        sermon_id_int = int(entry.date.replace("-", ""))
        # Look up media_id
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/pong_sermons?id=eq.{sermon_id_int}&select=media_id",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=30,
        )
        rows = r.json()
        media_id = rows[0]["media_id"] if rows else None
        delete_orphan_rows(sermon_id_int, media_id)
        rewrite_marker(txt_path, entry.line_no, "# ⛔ 別人")
        print(f"  [mark] ⛔ 別人")
    elif decision == "pong":
        print(f"  [keep] ⏳ 未完成 (龐候選)")
    else:
        print(f"  [keep] ⏳ 未完成 (待手動判斷)")

    return decision


def main():
    p = argparse.ArgumentParser()
    p.add_argument("txt_files", nargs="+", help="year txt file(s)")
    args = p.parse_args()

    summary = {"pong": [], "skip": [], "unsure": [], "error": []}

    for txt_file in args.txt_files:
        txt_path = Path(txt_file)
        print(f"\n##### {txt_path.name} #####")
        entries = parse_queue(txt_path)
        pending = [e for e in entries if e.status == "pending"]
        print(f"pending: {len(pending)}")

        for entry in pending:
            try:
                result = process_entry(entry, txt_path)
            except KeyboardInterrupt:
                print("\n[abort] interrupted by user")
                return
            except Exception as e:
                print(f"  [error] {e}")
                result = "error"
            summary[result].append(f"{entry.date} {entry.title}")

    print("\n\n##### SUMMARY #####")
    for k, items in summary.items():
        print(f"\n{k.upper()}: {len(items)}")
        for it in items[:50]:
            print(f"  {it}")
        if len(items) > 50:
            print(f"  ... and {len(items) - 50} more")


if __name__ == "__main__":
    main()
