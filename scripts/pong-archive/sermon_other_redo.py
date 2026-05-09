#!/usr/bin/env python3
"""
sermon_other_redo.py — re-transcribe + commit 龐君華 sermons preached at
churches **other than** 城中教會 (台北衛理堂、雅各堂、信義會、聖公會 …).

Mirrors `sermon_redo.py` but reads metadata (location/preacher/occasion/
scripture_ref/scripture_readings) from an embedded MANIFEST keyed by
youtube_id, since the source txt file is freeform and each entry has its
own location and richer metadata than the per-year city-church queues.

Subcommands:

  status <txt_file>
    Show pending / done / skipped counts.

  prepare <txt_file> [--date YYYY-MM-DD] [--youtube-id ID]
    Pick next pending entry (or the one matching --date / --youtube-id),
    ensure pong_sermons + pong_media rows exist with full metadata, then
    download YouTube audio and Whisper-transcribe to
    tmp_sermon/<date>_raw.txt. Emits JSON on stdout.

  commit <txt_file> --date YYYY-MM-DD --clean-file PATH
    UPDATE pong_media.transcript + pong_sermons.content from the clean
    file, mark the txt entry's marker as 「✅ 完成」.
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

sys.path.insert(0, str(Path(__file__).parent))
from pong_sermon_pipeline import (  # noqa: E402
    extract_youtube_id,
    download_audio,
    transcribe,
    fetch_youtube_metadata,
)

TMP_DIR = ROOT / "tmp_sermon"
DONE_MARKER = "# ✅ 完成"
PENDING_MARKER = "# ⏳ 未完成"


# ─── Manifest ──────────────────────────────────────────────────────────────
# All metadata for each entry, keyed by 11-char YouTube id.
# preferred_id: when set, force this id for new pong_sermons rows (used for
# 100000000-series rows that already exist with that id from a prior pass).
MANIFEST: dict[str, dict] = {
    "uTYicIP3aeQ": {
        "date": "2024-03-17",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "讓心靈活過來",
        "occasion": "預苦期第五主日",
        "scripture_ref": "約翰福音 12:20-33",
        "scripture_readings": "經課一：耶利米書 31:31-34；啟應文：詩篇 51:1-12；經課二：希伯來書 5:5-10；福音書：約翰福音 12:20-33",
        "worship_team": "司會：牟維丹 敬拜：林雅惠、榮恩敬拜團",
        "is_full_service": True,
    },
    "8Pli_WqdYJU": {
        "date": "2021-09-05",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "起因由信",
        "occasion": "主日崇拜",
        "scripture_ref": "雅各書 2:1-10",
        "scripture_readings": "經課一：箴言 22:1-2, 8-9, 22-23；啟應文：詩篇 125；經課二：雅各書 2:1-10；福音書：馬可福音 7:24-37",
        "worship_team": "司會：彭德全 敬拜：李玟瑤",
        "is_full_service": True,
        "preferred_id": 100000000,
    },
    "WP6iW2xS8nU": {
        "date": "2025-11-30",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "雙重的來臨",
        "occasion": "將臨期第一主日",
        "scripture_ref": "馬太福音 24:36-44",
        "scripture_readings": "經課一：以賽亞書 2:1-5；啟應文：詩篇 122:1-9；經課二：羅馬書 13:11-14；福音書：馬太福音 24:36-44",
        "worship_team": "司會：牟維丹 敬拜：歐陽光、榮恩敬拜團",
        "is_full_service": True,
    },
    "gCOIcYRV-us": {
        "date": "2021-10-03",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "苦罪懸迷",
        "occasion": "成人主日",
        "scripture_ref": "馬可福音 10:2-16",
        "scripture_readings": "經課一：約伯記 1:1, 2:1-10；啟應文：詩篇 26；經課二：希伯來書 1:1-4, 2:5-12；福音書：馬可福音 10:2-16",
        "worship_team": "司會：彭德全 敬拜：傅靜紅",
        "is_full_service": True,
        "preferred_id": 100000001,
    },
    "sVSduRPjKjo": {
        "date": "2024-05-26",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "神聖的連結",
        "occasion": "三一主日（成人主日）",
        "scripture_ref": "約翰福音 3:1-17",
        "scripture_readings": "經課一：以賽亞書 6:1-8；啟應文：詩篇 29；經課二：羅馬書 8:12-17；福音書：約翰福音 3:1-17",
        "worship_team": "司會：劉淑華 敬拜：林雅惠、榮恩敬拜團",
        "is_full_service": True,
    },
    "ExZdgNF14U0": {
        "date": "2023-10-29",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "愛的雙重誡命",
        "occasion": "聖靈降臨後第二十二主日",
        "scripture_ref": "馬太福音 22:34-46",
        "scripture_readings": "經課一：申命記 34:1-12；啟應文：詩篇 90:1-6, 13-17；經課二：帖撒羅尼迦前書 2:1-8；福音書：馬太福音 22:34-46",
        "worship_team": "司會：劉淑華 敬拜：李玟瑤、榮恩敬拜團",
        "is_full_service": True,
    },
    "CjIhO1WUhjo": {
        "date": "2025-03-02",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "攀登榮耀之巔：與神聖相遇",
        "occasion": "登山變相主日",
        "scripture_ref": "路加福音 9:28-36",
        "scripture_readings": "經課一：出埃及記 34:29-35；啟應文：詩篇 99:1-9；經課二：哥林多後書 3:12-4:2；福音書：路加福音 9:28-36",
        "worship_team": "司會：劉淑華 敬拜：李玟瑤、榮恩敬拜團",
        "is_full_service": True,
    },
    "tp7n-_LMHl4": {
        "date": "2021-11-07",
        "location": "台北衛理堂",
        "preacher": "龐君華會督",
        "title": "信心與價值的重估",
        "occasion": "聖徒主日",
        "scripture_ref": "馬可福音 12:38-44",
        "scripture_readings": "經課一：路得記 3:1-5, 4:13-17；啟應文：詩篇 127；經課二：希伯來書 9:24-28；福音書：馬可福音 12:38-44",
        "worship_team": "司會：彭德全 敬拜：吳佳玲",
        "is_full_service": True,
        "preferred_id": 100000002,
    },
    "sumZrvLsTdA": {
        "date": "2020-09-20",
        "location": "衛理公會雅各堂",
        "preacher": "龐君華會督",
        "title": "聖靈與真理充滿的殿",
        "occasion": None,
        "scripture_ref": "彼得前書 2:4-5",
        "scripture_readings": None,
        "worship_team": None,
        "is_full_service": False,
    },
    "sxBHiRUJNcQ": {
        "date": "2021-03-27",
        "location": "衛理公會雅各堂",
        "preacher": "龐君華會督",
        "title": "門徒與管家",
        "occasion": "北二教區靈修會",
        "scripture_ref": "馬可福音 11:1-11",
        "scripture_readings": "經課一：以賽亞書 50:4-9a；啟應文：詩篇 31:9-16；經課二：腓立比書 2:5-11；福音書：馬可福音 11:1-11",
        "worship_team": None,
        "is_full_service": False,
    },
    "AN-0xMz7NOk": {
        "date": "2025-01-18",
        "location": "台灣信義會救恩堂",
        "preacher": "龐君華會督",
        "title": "不要疑惑，總要信",
        "occasion": "基督徒合一祈禱週",
        "scripture_ref": "約翰福音 2:1-11",
        "scripture_readings": "經課一：以賽亞書 62:1-5；啟應文：詩篇 36:5-10；經課二：哥林多前書 12:1-11；福音書：約翰福音 2:1-11",
        "worship_team": None,
        "is_full_service": True,
    },
    "3ac370LejWM": {
        "date": "2025-08-31",
        "location": "台灣聖公會聖提摩太堂",
        "preacher": "龐君華會督",
        "title": "心靈的水池",
        "occasion": "聖靈降臨後第十二主日 聖餐禮拜",
        "scripture_ref": "路加福音 14:1, 7-14",
        "scripture_readings": "經課一：耶利米書 2:4-13；啟應文：詩篇 18:1, 10-16；經課二：希伯來書 13:1-8, 15-16；福音書：路加福音 14:1, 7-14",
        "worship_team": None,
        "worship_songs": "新聖詩 250 首〈著謳咾主上帝〉、新聖詩 370 首〈咱奉獻聲音及才能〉、新聖詩 222 首〈上帝做阮代代幫助〉",
        "is_full_service": True,
    },
}


# ─── Manifest field normalizers ────────────────────────────────────────────
# pong_sermons.scripture_readings is a JSONB array of
#   {display_label, book, reference}; worship_songs is a JSONB array of
# strings. Manifest values are kept as plain strings for editor friendliness;
# convert them at write time.

_LABEL_RE = re.compile(r"^(經課[一二三四]?|啟應文|福音書|信息經文|詩篇經課)\s*[：:]\s*(.+)$")
_BOOK_REF_RE = re.compile(r"^(\S+?)\s+(\d.*)$")


def _normalize_readings(value):
    if not value or isinstance(value, list):
        return value
    out = []
    for seg in re.split(r"[；;]", str(value)):
        seg = seg.strip()
        if not seg:
            continue
        m = _LABEL_RE.match(seg)
        if not m:
            out.append({"display_label": "", "book": "", "reference": seg})
            continue
        label, body = m.group(1), m.group(2).strip()
        m2 = _BOOK_REF_RE.match(body)
        if m2:
            out.append({"display_label": label, "book": m2.group(1), "reference": m2.group(2).strip()})
        else:
            out.append({"display_label": label, "book": body, "reference": ""})
    return out


def _normalize_songs(value):
    if not value or isinstance(value, list):
        return value
    return [s.strip() for s in re.split(r"[、,]", str(value)) if s.strip()]


# ─── Supabase REST helpers ─────────────────────────────────────────────────

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
        params={
            "select": "id,title,sermon_date,media_id,content,location,preacher",
            "sermon_date": f"eq.{date_str}",
        },
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


def insert_sermon(meta: dict, youtube_url: str | None = None) -> int:
    """Insert pong_sermons row using MANIFEST metadata. Returns sermon id."""
    date_str = meta["date"]
    year, month = int(date_str[:4]), int(date_str[5:7])
    church_year = year if month == 12 else year - 1
    sermon_id = meta.get("preferred_id") or int(date_str.replace("-", ""))
    payload = {
        "id": sermon_id,
        "sermon_date": date_str,
        "title": meta["title"],
        "church_year": church_year,
        "preacher": meta["preacher"],
        "location": meta["location"],
        "occasion": meta.get("occasion"),
        "scripture_ref": meta.get("scripture_ref"),
        "scripture_readings": _normalize_readings(meta.get("scripture_readings")),
        "worship_team": meta.get("worship_team"),
        "worship_songs": _normalize_songs(meta.get("worship_songs")),
        "youtube_url": youtube_url,
        "is_published": True,
        "has_recording": True,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    r = requests.post(f"{_sb_url()}/pong_sermons", headers=_sb_headers(), json=payload)
    if r.status_code in (200, 201):
        return r.json()[0]["id"]
    # Already exists — update metadata best-effort, then return existing id
    return sermon_id


def patch_sermon_metadata(sermon_id: int, meta: dict, youtube_url: str | None = None) -> None:
    """Backfill missing metadata on an existing row (e.g. preacher=None on the
    100000000-series 台北衛理堂 entries). Doesn't touch fields that are already
    set."""
    sermon = requests.get(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={"select": "id,preacher,location,title,occasion,scripture_ref,scripture_readings,worship_team,worship_songs,youtube_url,is_published",
                "id": f"eq.{sermon_id}"},
    ).json()[0]
    patch = {}
    for k in ("preacher", "location", "title", "occasion", "scripture_ref",
              "worship_team"):
        if not sermon.get(k) and meta.get(k):
            patch[k] = meta[k]
    if not sermon.get("scripture_readings") and meta.get("scripture_readings"):
        patch["scripture_readings"] = _normalize_readings(meta["scripture_readings"])
    if not sermon.get("worship_songs") and meta.get("worship_songs"):
        patch["worship_songs"] = _normalize_songs(meta["worship_songs"])
    if youtube_url and not sermon.get("youtube_url"):
        patch["youtube_url"] = youtube_url
    if not sermon.get("is_published"):
        patch["is_published"] = True
    if patch:
        requests.patch(
            f"{_sb_url()}/pong_sermons",
            headers=_sb_headers(),
            params={"id": f"eq.{sermon_id}"},
            json=patch,
        ).raise_for_status()


def insert_media(*, youtube_id: str, meta: dict, duration: int,
                 description: str, thumbnail: str) -> int:
    r = requests.post(
        f"{_sb_url()}/pong_media",
        headers=_sb_headers(),
        json={
            "title": meta["title"],
            "media_type": "sermon_audio",
            "platform": "youtube",
            "youtube_id": youtube_id,
            "duration_sec": duration,
            "transcript": "",
            "description": description,
            "thumbnail_url": thumbnail,
            "broadcast_date": meta["date"],
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


# ─── Queue txt parsing ─────────────────────────────────────────────────────
# 別的教會講道.txt is freeform per-entry but each entry's first line is a
# header/title and the next non-blank URL-bearing line is the YouTube link.
# We add header markers (# ⏳ 未完成 / # ✅ 完成) above each entry block to
# track status the same way as the year-files do.

@dataclass
class Entry:
    line_no: int       # 1-based line number of the marker line
    marker: str        # the full marker line
    url: str           # YouTube URL
    youtube_id: str

    @property
    def status(self) -> str:
        if "完成" in self.marker and "未完成" not in self.marker:
            return "done"
        if "別人" in self.marker:
            return "skip"
        return "pending"


def parse_queue(path: Path) -> list[Entry]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    entries: list[Entry] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("#"):
            marker = line
            marker_line_no = i + 1
            # Find the next URL line within this entry block (until next # or EOF)
            url = ""
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("#"):
                m = re.search(r"https?://\S+", lines[j])
                if m:
                    url = m.group(0).rstrip(",.;)")
                    break
                j += 1
            if url:
                yid = extract_youtube_id(url)
                entries.append(Entry(line_no=marker_line_no, marker=marker, url=url, youtube_id=yid))
            i = j if j > i else i + 1
        else:
            i += 1
    return entries


def rewrite_marker(path: Path, line_no: int, new_marker: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines[line_no - 1] = new_marker + "\n"
    path.write_text("".join(lines), encoding="utf-8")


# ─── Subcommands ───────────────────────────────────────────────────────────

def cmd_status(txt_file: Path) -> None:
    entries = parse_queue(txt_file)
    counts = {"done": 0, "pending": 0, "skip": 0}
    for e in entries:
        counts[e.status] = counts.get(e.status, 0) + 1
    print(f"queue: {txt_file}")
    print(f"  total   : {len(entries)}")
    print(f"  done    : {counts['done']}")
    print(f"  pending : {counts['pending']}")
    print(f"  skip    : {counts['skip']}")
    pending = [e for e in entries if e.status == "pending"]
    if pending:
        print("\n  next pending:")
        for e in pending[:5]:
            meta = MANIFEST.get(e.youtube_id, {})
            print(f"    {meta.get('date','?')}  {meta.get('title','?')}  ({meta.get('location','?')})")


def cmd_prepare(txt_file: Path, target_date: str | None, target_youtube_id: str | None) -> None:
    entries = parse_queue(txt_file)

    if target_youtube_id:
        candidates = [e for e in entries if e.youtube_id == target_youtube_id]
    elif target_date:
        candidates = [e for e in entries
                      if MANIFEST.get(e.youtube_id, {}).get("date") == target_date]
    else:
        candidates = [e for e in entries if e.status == "pending"]
    if not candidates:
        if not target_date and not target_youtube_id:
            print("[done] no pending entries", file=sys.stderr)
            sys.exit(3)
        print(f"[error] no entry matches selector", file=sys.stderr)
        sys.exit(2)
    entry = candidates[0]
    if entry.status == "skip":
        print(f"[error] entry is marked 別人 — refusing", file=sys.stderr)
        sys.exit(2)

    meta = MANIFEST.get(entry.youtube_id)
    if not meta:
        print(f"[error] no manifest entry for youtube_id={entry.youtube_id}", file=sys.stderr)
        sys.exit(2)

    print(f"[entry] {meta['date']}  {meta['title']}  ({meta['location']})", file=sys.stderr)
    print(f"[url]   {entry.url}", file=sys.stderr)

    youtube_id = entry.youtube_id
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    raw_file = TMP_DIR / f"{meta['date']}_raw.txt"
    clean_file = TMP_DIR / f"{meta['date']}_clean.txt"

    # 1) Ensure pong_sermons row
    canonical_youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
    sermon = find_sermon_by_date(meta["date"])
    if sermon:
        sermon_id = sermon["id"]
        print(f"[sermon] existing id={sermon_id}", file=sys.stderr)
        patch_sermon_metadata(sermon_id, meta, youtube_url=canonical_youtube_url)
    else:
        sermon_id = insert_sermon(meta, youtube_url=canonical_youtube_url)
        sermon = {"id": sermon_id, "media_id": None}
        print(f"[sermon] created id={sermon_id}", file=sys.stderr)

    # 2) Ensure pong_media row
    media = find_media_by_youtube_id(youtube_id)
    if media:
        media_id = media["id"]
        print(f"[media] existing id={media_id}", file=sys.stderr)
    else:
        ymeta = fetch_youtube_metadata(entry.url)
        media_id = insert_media(
            youtube_id=youtube_id,
            meta=meta,
            duration=ymeta["duration"],
            description=ymeta["description"],
            thumbnail=ymeta["thumbnail"],
        )
        print(f"[media] created id={media_id}", file=sys.stderr)

    # 3) Link
    if not sermon.get("media_id"):
        link_sermon_media(sermon_id, media_id)

    # 4) Download + transcribe
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
        "date": meta["date"],
        "title": meta["title"],
        "location": meta["location"],
        "url": entry.url,
        "sermon_id": sermon_id,
        "media_id": media_id,
        "is_full_service": meta.get("is_full_service", False),
        "raw_file": str(raw_file),
        "clean_file": str(clean_file),
    }, ensure_ascii=False))


def cmd_commit(txt_file: Path, date: str, clean_file: Path) -> None:
    entries = parse_queue(txt_file)
    matches = [e for e in entries
               if MANIFEST.get(e.youtube_id, {}).get("date") == date]
    if not matches:
        print(f"[error] date {date} not found in {txt_file}", file=sys.stderr)
        sys.exit(2)
    entry = matches[0]

    meta = MANIFEST[entry.youtube_id]
    sermon = find_sermon_by_date(date)
    if not sermon:
        print(f"[error] no pong_sermons row for {date}; run prepare first", file=sys.stderr)
        sys.exit(2)
    media = find_media_by_youtube_id(entry.youtube_id)
    if not media:
        print(f"[error] no pong_media row for youtube_id={entry.youtube_id}; run prepare first", file=sys.stderr)
        sys.exit(2)

    text = clean_file.read_text(encoding="utf-8").strip() + "\n"
    if len(text) < 200:
        print(f"[error] clean file is suspiciously short ({len(text)} chars)", file=sys.stderr)
        sys.exit(2)

    update_transcript_and_content(media["id"], sermon["id"], text)
    link_sermon_media(sermon["id"], media["id"])
    print(f"[db] updated pong_media id={media['id']} + pong_sermons id={sermon['id']}", file=sys.stderr)

    rewrite_marker(txt_file, entry.line_no, DONE_MARKER)
    print(f"[txt] marked {date} as 「✅ 完成」 in {txt_file}", file=sys.stderr)


# ─── Entry point ───────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("txt_file", type=Path)

    s = sub.add_parser("prepare")
    s.add_argument("txt_file", type=Path)
    s.add_argument("--date", help="Specific YYYY-MM-DD")
    s.add_argument("--youtube-id", help="11-char YouTube id")

    s = sub.add_parser("commit")
    s.add_argument("txt_file", type=Path)
    s.add_argument("--date", required=True)
    s.add_argument("--clean-file", required=True, type=Path)

    args = p.parse_args()
    if args.cmd == "status":
        cmd_status(args.txt_file)
    elif args.cmd == "prepare":
        cmd_prepare(args.txt_file, args.date, args.youtube_id)
    elif args.cmd == "commit":
        cmd_commit(args.txt_file, args.date, args.clean_file)


if __name__ == "__main__":
    main()
