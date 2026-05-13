#!/usr/bin/env python3
"""
sermon_redo.py — re-transcribe + re-clean a sermon end-to-end.

The cleanup step itself is done by Claude in the conversation (this script
only handles the deterministic parts: queue parsing, audio download, Whisper
transcription, DB upserts, and txt-file status updates).

Subcommands:

  status <txt_file>
    Print pending / done / skipped counts for a year list.

  prepare <txt_file> [--date YYYY-MM-DD]
    Find the next entry whose status is 「⏳ 未完成」 (or the entry matching
    --date), ensure pong_sermons + pong_media rows exist, download audio
    and Whisper-transcribe to tmp_sermon/<date>_raw.txt. Prints a JSON
    object {date, title, url, sermon_id, media_id, raw_file, clean_file}
    on stdout for the caller to consume.

  commit <txt_file> --date YYYY-MM-DD --clean-file PATH
    UPDATE pong_media.transcript + pong_sermons.content from the cleaned
    file, then flip the txt entry's marker from 「⏳ 未完成」 to 「✅ 完成」.
    Sermon/media IDs are looked up from the DB by date — caller does not
    need to pass them.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# Pull helpers from the existing pipeline (download_audio, transcribe, etc.)
sys.path.insert(0, str(Path(__file__).parent))
from pong_sermon_pipeline import (
    extract_youtube_id,
    download_audio,
    transcribe,
    fetch_youtube_metadata,
)

TMP_DIR = ROOT / "tmp_sermon"
DONE_MARKER = "# ✅ 完成"
PENDING_MARKER = "# ⏳ 未完成"
SKIP_MARKER = "# ⛔ 別人"


# ─── Supabase REST helpers ──────────────────────────────────────────────────

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


def find_sermon_by_date(date_str: str) -> dict | None:
    r = requests.get(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={"select": "id,title,sermon_date,media_id,content", "sermon_date": f"eq.{date_str}"},
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def find_media_by_youtube_id(yid: str) -> dict | None:
    r = requests.get(
        f"{_sb_url()}/pong_media",
        headers=_sb_headers(),
        params={"select": "id,youtube_id,title,duration_sec", "youtube_id": f"eq.{yid}"},
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def insert_sermon(date_str: str, title: str) -> int:
    # Import locally to avoid restructuring the module tree — the classifier
    # lives next to its sibling helpers in sermon_other_redo.
    from sermon_other_redo import classify_sermon_type
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
            "location": "衛理公會城中教會",
            "sermon_type": classify_sermon_type(title, None),
            "is_published": False,
        },
    )
    if r.status_code in (200, 201):
        return r.json()[0]["id"]
    return sermon_id  # already exists


def insert_media(*, youtube_id: str, title: str, duration: int,
                 description: str, thumbnail: str, broadcast_date: str) -> int:
    r = requests.post(
        f"{_sb_url()}/pong_media",
        headers=_sb_headers(),
        json={
            "title": title,
            "media_type": "sermon_audio",
            "platform": "youtube",
            "youtube_id": youtube_id,
            "duration_sec": duration,
            "transcript": "",
            "description": description,
            "thumbnail_url": thumbnail,
            "broadcast_date": broadcast_date,
            "is_published": True,
        },
    )
    r.raise_for_status()
    return r.json()[0]["id"]


def link_sermon_media(sermon_id: int, media_id: int) -> None:
    requests.patch(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={"id": f"eq.{sermon_id}"},
        json={"media_id": media_id, "has_recording": True},
    ).raise_for_status()


def update_transcript_and_content(media_id: int, sermon_id: int, text: str) -> None:
    requests.patch(
        f"{_sb_url()}/pong_media",
        headers=_sb_headers(),
        params={"id": f"eq.{media_id}"},
        json={"transcript": text},
    ).raise_for_status()
    requests.patch(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={"id": f"eq.{sermon_id}"},
        json={"content": text},
    ).raise_for_status()


# ─── Queue txt parsing ──────────────────────────────────────────────────────

@dataclass
class Entry:
    idx: int          # index in `entries` (not the file line number)
    line_no: int      # 1-based line number of the marker line in the file
    marker: str       # the full marker line (e.g. "# ⏳ 未完成")
    date: str         # YYYY-MM-DD
    title: str
    url: str

    @property
    def status(self) -> str:
        if "完成" in self.marker and "未完成" not in self.marker:
            return "done"
        if "別人" in self.marker:
            return "skip"
        if "無錄影" in self.marker or "📅" in self.marker:
            return "no_recording"
        return "pending"


def parse_queue(path: Path) -> list[Entry]:
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: list[Entry] = []
    i = 0
    idx = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            marker_line_no = i + 1
            marker = line.rstrip()
            # Next non-blank line is "YYYY-MM-DD …"
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines):
                break
            m = re.match(r"^(\d{4}-\d{2}-\d{2})\s+(.*)", lines[j].strip())
            if not m:
                i = j + 1
                continue
            date = m.group(1)
            title = m.group(2).strip()
            # Following non-blank line is the URL
            k = j + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            url = lines[k].strip() if k < len(lines) else ""
            entries.append(Entry(idx=idx, line_no=marker_line_no,
                                 marker=marker, date=date, title=title, url=url))
            idx += 1
            i = k + 1
        else:
            i += 1
    return entries


def rewrite_marker(path: Path, line_no: int, new_marker: str) -> None:
    """Replace the marker on a specific 1-based line."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines[line_no - 1] = new_marker + "\n"
    path.write_text("".join(lines), encoding="utf-8")


# ─── Subcommands ────────────────────────────────────────────────────────────

def cmd_status(txt_file: Path) -> None:
    entries = parse_queue(txt_file)
    counts = {"done": 0, "pending": 0, "skip": 0, "no_recording": 0}
    for e in entries:
        counts[e.status] = counts.get(e.status, 0) + 1
    print(f"queue: {txt_file}")
    print(f"  total       : {len(entries)}")
    print(f"  done        : {counts['done']}")
    print(f"  pending     : {counts['pending']}")
    print(f"  skip        : {counts['skip']}")
    print(f"  no_recording: {counts['no_recording']}")
    pending = [e for e in entries if e.status == "pending"]
    if pending:
        print("\n  next pending:")
        for e in pending[:5]:
            print(f"    {e.date}  {e.title}")


def cmd_prepare(txt_file: Path, target_date: str | None, target_youtube_id: str | None = None) -> None:
    entries = parse_queue(txt_file)
    if target_youtube_id:
        # Disambiguate by youtube_id (used for Part 1 / Part 2 same-date entries)
        candidates = [e for e in entries if extract_youtube_id(e.url) == target_youtube_id]
        if not candidates:
            print(f"[error] youtube_id {target_youtube_id} not found in {txt_file}", file=sys.stderr)
            sys.exit(2)
        entry = candidates[0]
        if entry.status == "skip":
            print(f"[error] {entry.date}/{target_youtube_id} is marked 別人 — refusing to process", file=sys.stderr)
            sys.exit(2)
    elif target_date:
        # Prefer pending entries when there are duplicates on the same date
        candidates = [e for e in entries if e.date == target_date and e.status == "pending"]
        if not candidates:
            candidates = [e for e in entries if e.date == target_date]
        if not candidates:
            print(f"[error] date {target_date} not found in {txt_file}", file=sys.stderr)
            sys.exit(2)
        entry = candidates[0]
        if entry.status == "skip":
            print(f"[error] {target_date} is marked 別人 — refusing to process", file=sys.stderr)
            sys.exit(2)
    else:
        candidates = [e for e in entries if e.status == "pending"]
        if not candidates:
            print("[done] no pending entries", file=sys.stderr)
            sys.exit(3)
        entry = candidates[0]

    print(f"[entry] {entry.date}  {entry.title}", file=sys.stderr)
    print(f"[url]   {entry.url}", file=sys.stderr)

    youtube_id = extract_youtube_id(entry.url)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    # Disambiguate by youtube_id when multiple entries share a date.
    same_date_count = sum(1 for e in entries if e.date == entry.date)
    suffix = f"_{youtube_id}" if same_date_count > 1 else ""
    raw_file = TMP_DIR / f"{entry.date}{suffix}_raw.txt"
    clean_file = TMP_DIR / f"{entry.date}{suffix}_clean.txt"

    # 1) Ensure pong_sermons row exists
    sermon = find_sermon_by_date(entry.date)
    if sermon:
        sermon_id = sermon["id"]
        print(f"[sermon] existing id={sermon_id}", file=sys.stderr)
    else:
        sermon_id = insert_sermon(entry.date, entry.title)
        sermon = {"id": sermon_id, "media_id": None}
        print(f"[sermon] created id={sermon_id}", file=sys.stderr)

    # 2) Ensure pong_media row exists (lookup by youtube_id, fall back to creating)
    media = find_media_by_youtube_id(youtube_id)
    duration_sec = 0
    meta = None
    if media:
        media_id = media["id"]
        duration_sec = media.get("duration_sec") or 0
        print(f"[media] existing id={media_id}", file=sys.stderr)
    else:
        meta = fetch_youtube_metadata(entry.url)
        duration_sec = meta["duration"]
        media_id = insert_media(
            youtube_id=youtube_id,
            title=entry.title,
            duration=duration_sec,
            description=meta["description"],
            thumbnail=meta["thumbnail"],
            broadcast_date=entry.date,
        )
        print(f"[media] created id={media_id}", file=sys.stderr)

    # 3) Make sure they're linked
    if not sermon.get("media_id"):
        link_sermon_media(sermon_id, media_id)

    # 4) Download + transcribe (skip if raw file already on disk)
    if raw_file.exists() and raw_file.stat().st_size > 200:
        print(f"[skip] raw file already exists: {raw_file}", file=sys.stderr)
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = Path(tmpdir) / f"{youtube_id}.mp3"
            download_audio(entry.url, audio_path)
            transcript = transcribe(audio_path, lang="zh")
        raw_file.write_text(transcript, encoding="utf-8")
        print(f"[whisper] wrote {len(transcript)} chars to {raw_file}", file=sys.stderr)

    print(json.dumps({
        "date": entry.date,
        "title": entry.title,
        "url": entry.url,
        "sermon_id": sermon_id,
        "media_id": media_id,
        "raw_file": str(raw_file),
        "clean_file": str(clean_file),
    }, ensure_ascii=False))


def cmd_commit(txt_file: Path, date: str, clean_file: Path, target_youtube_id: str | None = None) -> None:
    entries = parse_queue(txt_file)
    if target_youtube_id:
        matches = [e for e in entries if extract_youtube_id(e.url) == target_youtube_id]
    else:
        # Prefer the first pending entry for this date; fall back to any match.
        pending_matches = [e for e in entries if e.date == date and e.status == "pending"]
        matches = pending_matches or [e for e in entries if e.date == date]
    if not matches:
        print(f"[error] date {date} not found in {txt_file}", file=sys.stderr)
        sys.exit(2)
    entry = matches[0]
    if entry.status == "skip":
        print(f"[error] {date} is marked 別人 — refusing to commit", file=sys.stderr)
        sys.exit(2)

    sermon = find_sermon_by_date(date)
    if not sermon:
        print(f"[error] no pong_sermons row for {date}; run prepare first", file=sys.stderr)
        sys.exit(2)

    # Look up media by THIS entry's youtube_id rather than sermon.media_id —
    # for dates with multiple recordings, each entry's transcript should land
    # on its own pong_media row.
    youtube_id = extract_youtube_id(entry.url)
    media = find_media_by_youtube_id(youtube_id)
    if not media:
        print(f"[error] no pong_media row for youtube_id={youtube_id}; run prepare first", file=sys.stderr)
        sys.exit(2)
    media_id = media["id"]

    text = clean_file.read_text(encoding="utf-8").strip() + "\n"
    if len(text) < 200:
        print(f"[error] clean file is suspiciously short ({len(text)} chars); aborting", file=sys.stderr)
        sys.exit(2)

    update_transcript_and_content(media_id, sermon["id"], text)
    # Re-link sermon to this entry's media (for dates with one entry this is a no-op;
    # for multi-entry dates the most recently committed becomes the primary).
    link_sermon_media(sermon["id"], media_id)
    print(f"[db] updated pong_media id={media_id} + pong_sermons id={sermon['id']}", file=sys.stderr)

    rewrite_marker(txt_file, entry.line_no, DONE_MARKER)
    print(f"[txt] marked {date} as 「✅ 完成」 in {txt_file}", file=sys.stderr)


# ─── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("txt_file", type=Path)

    s = sub.add_parser("prepare")
    s.add_argument("txt_file", type=Path)
    s.add_argument("--date", help="Specific YYYY-MM-DD (default: next pending)")
    s.add_argument("--youtube-id", help="Pick a specific entry by 11-char YouTube ID (used for Part 1/Part 2 disambiguation)")

    s = sub.add_parser("commit")
    s.add_argument("txt_file", type=Path)
    s.add_argument("--date", required=True)
    s.add_argument("--clean-file", required=True, type=Path)
    s.add_argument("--youtube-id", help="Disambiguate which entry to commit on a multi-entry date")

    args = p.parse_args()
    if args.cmd == "status":
        cmd_status(args.txt_file)
    elif args.cmd == "prepare":
        cmd_prepare(args.txt_file, args.date, args.youtube_id)
    elif args.cmd == "commit":
        cmd_commit(args.txt_file, args.date, args.clean_file, args.youtube_id)


if __name__ == "__main__":
    main()
