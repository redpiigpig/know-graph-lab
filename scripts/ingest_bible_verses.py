#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Bible verse text from public GitHub repos into Supabase bible_verses.

Usage:
    python scripts/ingest_bible_verses.py <version> [--dry-run] [--book BOOK]

Versions:
    sblgnt   — SBL Greek NT (CC BY 4.0)
    vul      — Clementine Vulgate (PD)
    wlc      — Westminster Leningrad Codex (WLC, Hebrew OT, PD)
    lxx      — Septuagint Rahlfs 1935 (CC BY-NC-SA)
    cuv2010  — 和合本2010 (scrape rcuv.hkbs.org.hk, copyright HKBS)
    niv      — NIV (scrape, copyright Biblica)
    all      — run sblgnt + vul + wlc + lxx in sequence

Inserts into bible_verses (book_code, chapter, verse, version_code, text)
using PostgREST upsert. Batches of 500 rows per HTTP call.
"""
import argparse
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests


# ─── env ────────────────────────────────────────────────────────────────────

def load_env():
    env = {}
    with open(".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
SUPA_URL = ENV["SUPABASE_URL"]
SUPA_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
PG_HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal",
}

GITHUB_RAW = "https://raw.githubusercontent.com"


# ─── 統一 upsert ────────────────────────────────────────────────────────────

def upsert_verses(rows, batch_size=500, dry_run=False):
    """Upsert into bible_verses via PostgREST.

    rows: list of {book_code, chapter, verse, version_code, text}
    Dedupes within the batch on (book, ch, v, version) keeping the longest text
    — PostgREST refuses ON CONFLICT batches with duplicate keys.
    """
    if dry_run:
        print(f"  [dry-run] would upsert {len(rows)} rows; sample: {rows[:2]}")
        return
    if not rows:
        return
    # Dedupe: keep the row with the longest text for each PK
    dedup = {}
    for r in rows:
        k = (r["book_code"], r["chapter"], r["verse"], r["version_code"])
        prev = dedup.get(k)
        if not prev or len(r["text"]) > len(prev["text"]):
            dedup[k] = r
    rows = list(dedup.values())
    total = len(rows)
    done = 0
    for i in range(0, total, batch_size):
        chunk = rows[i:i + batch_size]
        r = requests.post(
            f"{SUPA_URL}/rest/v1/bible_verses?on_conflict=book_code,chapter,verse,version_code",
            headers=PG_HEADERS,
            json=chunk,
            timeout=60,
        )
        if r.status_code >= 300:
            print(f"  ✗ HTTP {r.status_code}: {r.text[:500]}", file=sys.stderr)
            sys.exit(1)
        done += len(chunk)
        if done % 5000 == 0 or done == total:
            print(f"  → {done}/{total} rows", file=sys.stderr)


def clear_version(code):
    """Delete all bible_verses for one version (so we can re-ingest cleanly)."""
    r = requests.delete(
        f"{SUPA_URL}/rest/v1/bible_verses?version_code=eq.{code}",
        headers={**PG_HEADERS, "Prefer": "return=minimal"},
        timeout=120,
    )
    if r.status_code >= 300:
        print(f"  ✗ clear {code}: HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ cleared previous {code} rows", file=sys.stderr)


# ─── SBLGNT (Greek NT) ──────────────────────────────────────────────────────
# 27 plain-text files at LogosBible/SBLGNT/data/sblgnt/text/{Book}.txt
# Line format: "Matt 1:1<TAB>Βίβλος γενέσεως ..."  (first line is book title — skip)

SBLGNT_REPO = "LogosBible/SBLGNT/master/data/sblgnt/text"
SBLGNT_FILES = {
    "Matt":   "mat", "Mark":  "mrk", "Luke":  "luk", "John":  "jhn",
    "Acts":   "act", "Rom":   "rom", "1Cor":  "1co", "2Cor":  "2co",
    "Gal":    "gal", "Eph":   "eph", "Phil":  "php", "Col":   "col",
    "1Thess": "1th", "2Thess":"2th", "1Tim":  "1ti", "2Tim":  "2ti",
    "Titus":  "tit", "Phlm":  "phm", "Heb":   "heb", "Jas":   "jas",
    "1Pet":   "1pe", "2Pet":  "2pe", "1John": "1jn", "2John": "2jn",
    "3John":  "3jn", "Jude":  "jud", "Rev":   "rev",
}
# Apparatus markers to strip from SBLGNT text
SBL_APPARATUS = re.compile(r"[⸀⸁⸂⸃⸄⸅⸆⸇⸉⸊⸋⸌⸍⸎⸏⸐⸑⸒⸓⸔⸕]")
SBL_LINE = re.compile(r"^([\w\s]+?)\s+(\d+):(\d+)\s+(.+)$")


def ingest_sblgnt(dry_run=False):
    print("→ Ingesting SBLGNT (Greek NT, CC BY 4.0)")
    clear_version("sblgnt") if not dry_run else None
    rows = []
    for fname, book_code in SBLGNT_FILES.items():
        url = f"{GITHUB_RAW}/{SBLGNT_REPO}/{fname}.txt"
        text = requests.get(url, timeout=30).text
        for line_no, line in enumerate(text.splitlines()):
            line = line.strip()
            if not line:
                continue
            # First line is Greek book title — only contains letters/spaces, no ':'
            if ":" not in line:
                continue
            m = SBL_LINE.match(line)
            if not m:
                continue
            _, ch, v, txt = m.groups()
            txt = SBL_APPARATUS.sub("", txt).strip()
            rows.append({
                "book_code": book_code,
                "chapter": int(ch),
                "verse": int(v),
                "version_code": "sblgnt",
                "text": txt,
            })
    print(f"  parsed {len(rows)} verses from {len(SBLGNT_FILES)} books")
    upsert_verses(rows, dry_run=dry_run)


# ─── Clementine Vulgate (Latin full canon) ──────────────────────────────────
# 73 plain-text files at BibleGet-I-O/Clementine-Vulgate/src/utf8/{Book}.lat
# Line format: "1:1 In principio creavit Deus..."  (chapter:verse + space + text)

VUL_REPO = "BibleGet-I-O/Clementine-Vulgate/master/src/utf8"
# Vulgate uses custom Latin abbreviations. Map to our OSIS-lowercase codes.
# Note: 1Rg-4Rg.lat combines 1-2 Samuel + 1-2 Kings; 1Par-2Par combines 1-2 Chron;
# 1Jo-3Jo combines 1-3 John. We split these by per-line book markers in file.
# Simpler approach: skip these combined files and use a known per-book scheme
# from a different source. For MVP, we use these combined files and split by book.
VUL_FILES = {
    # OT
    "Gn":     "gen", "Ex":    "exo", "Lv":    "lev", "Nm":    "num", "Dt":    "deu",
    "Jos":    "jos", "Jdc":   "jdg", "Rt":    "rut",
    "Esr":    "ezr", "Neh":   "neh",
    "Tob":    "tob", "Jdt":   "jdt", "Est":   "est",
    "Job":    "job", "Ps":    "psa", "Pr":    "pro", "Ecl":   "ecc", "Ct":    "sng",
    "Sap":    "wis", "Sir":   "sir",
    "Is":     "isa", "Jr":    "jer", "Lam":   "lam", "Bar":   "bar",
    "Ez":     "ezk", "Dn":    "dan",
    "Os":     "hos", "Joel":  "jol", "Am":    "amo", "Abd":   "oba", "Jon":   "jon",
    "Mch":    "mic", "Nah":   "nam", "Hab":   "hab", "Soph":  "zep", "Agg":   "hag",
    "Zach":   "zec", "Mal":   "mal",
    "1Mcc":   "1ma", "2Mcc":  "2ma",
    # NT
    "Mt":     "mat", "Mc":    "mrk", "Lc":    "luk", "Jo":    "jhn",
    "Act":    "act", "Rom":   "rom",
    "1Cor":   "1co", "2Cor":  "2co", "Gal":   "gal", "Eph":   "eph", "Phlp":  "php",
    "Col":    "col", "1Thes": "1th", "2Thes": "2th", "1Tim":  "1ti", "2Tim":  "2ti",
    "Tit":    "tit", "Phlm":  "phm", "Hbr":   "heb", "Jac":   "jas",
    "1Ptr":   "1pe", "2Ptr":  "2pe", "Jud":   "jud", "Apc":   "rev",
    "1Jo":    "1jn", "2Jo":   "2jn", "3Jo":   "3jn",
}
# Combined files: 1Rg-4Rg.lat (= 1Sa 2Sa 1Ki 2Ki sequentially), 1Par-2Par (= 1Ch 2Ch).
# These have per-book chapter restarts; we detect ch=1 resets.
VUL_COMBINED = {
    "1Rg-4Rg": ["1sa", "2sa", "1ki", "2ki"],
    "1Par-2Par": ["1ch", "2ch"],
}
# Expected chapter counts for combined-file split (chapter resets when reached)
VUL_CHAPTER_COUNTS = {
    "1sa": 31, "2sa": 24, "1ki": 22, "2ki": 25,
    "1ch": 29, "2ch": 36,
    "1jn": 5, "2jn": 1, "3jn": 1,
}
VUL_LINE = re.compile(r"^(\d+):(\d+)\s+(.+)$")


def ingest_vul(dry_run=False):
    print("→ Ingesting Vulgate (Clementine, Latin full, PD)")
    clear_version("vul") if not dry_run else None
    rows = []
    # Standard one-book files
    for fname, book_code in VUL_FILES.items():
        url = f"{GITHUB_RAW}/{VUL_REPO}/{fname}.lat"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ {fname}: HTTP {r.status_code}", file=sys.stderr)
            continue
        for line in r.text.splitlines():
            line = line.strip()
            m = VUL_LINE.match(line)
            if not m:
                continue
            ch, v, txt = m.groups()
            rows.append({
                "book_code": book_code,
                "chapter": int(ch),
                "verse": int(v),
                "version_code": "vul",
                "text": txt.strip(),
            })
    # Combined files: split by chapter reset
    for fname, books in VUL_COMBINED.items():
        url = f"{GITHUB_RAW}/{VUL_REPO}/{fname}.lat"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ {fname}: HTTP {r.status_code}", file=sys.stderr)
            continue
        book_idx = 0
        prev_ch = 0
        chapter_offset = 0  # for current book, all chapters of prev books summed
        for line in r.text.splitlines():
            line = line.strip()
            m = VUL_LINE.match(line)
            if not m:
                continue
            ch, v, txt = m.groups()
            ch_int, v_int = int(ch), int(v)
            # Detect book boundary: chapter resets to 1 from prev_ch > 1
            if ch_int < prev_ch and book_idx + 1 < len(books):
                book_idx += 1
                chapter_offset = 0
            prev_ch = ch_int
            rows.append({
                "book_code": books[book_idx],
                "chapter": ch_int,
                "verse": v_int,
                "version_code": "vul",
                "text": txt.strip(),
            })
    print(f"  parsed {len(rows)} verses from {len(VUL_FILES) + len(VUL_COMBINED)} files")
    upsert_verses(rows, dry_run=dry_run)


# ─── WLC (Hebrew OT) ────────────────────────────────────────────────────────
# 39 OSIS XML files at openscriptures/morphhb/master/wlc/{Book}.xml
# Parse <verse osisID="Gen.1.1"> ... <w lemma="..." morph="...">word</w> ... </verse>

WLC_REPO = "openscriptures/morphhb/master/wlc"
WLC_FILES = {
    "Gen":  "gen", "Exod": "exo", "Lev":  "lev", "Num":  "num", "Deut": "deu",
    "Josh": "jos", "Judg": "jdg", "Ruth": "rut",
    "1Sam": "1sa", "2Sam": "2sa", "1Kgs": "1ki", "2Kgs": "2ki",
    "1Chr": "1ch", "2Chr": "2ch", "Ezra": "ezr", "Neh":  "neh", "Esth": "est",
    "Job":  "job", "Ps":   "psa", "Prov": "pro", "Eccl": "ecc", "Song": "sng",
    "Isa":  "isa", "Jer":  "jer", "Lam":  "lam", "Ezek": "ezk", "Dan":  "dan",
    "Hos":  "hos", "Joel": "jol", "Amos": "amo", "Obad": "oba", "Jonah":"jon",
    "Mic":  "mic", "Nah":  "nam", "Hab":  "hab", "Zeph": "zep", "Hag":  "hag",
    "Zech": "zec", "Mal":  "mal",
}
OSIS_NS = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"


def ingest_wlc(dry_run=False):
    print("→ Ingesting WLC (Hebrew OT, PD text + CC-BY morph)")
    clear_version("wlc") if not dry_run else None
    rows = []
    for fname, book_code in WLC_FILES.items():
        url = f"{GITHUB_RAW}/{WLC_REPO}/{fname}.xml"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ {fname}: HTTP {r.status_code}", file=sys.stderr)
            continue
        book_rows = _parse_wlc_book(r.content, book_code)
        rows.extend(book_rows)
    print(f"  parsed {len(rows)} verses from {len(WLC_FILES)} books")
    upsert_verses(rows, dry_run=dry_run)


def _parse_wlc_book(xml_bytes, book_code):
    """Parse WLC OSIS XML: <verse osisID="Gen.1.1"> ... <w>...</w> ... </verse>.
    Container style — collect all <w> text inside each verse element."""
    out = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return out
    seen = set()
    for verse_el in root.iter(f"{OSIS_NS}verse"):
        osis_id = verse_el.attrib.get("osisID")
        if not osis_id:
            continue  # eID closing markers, skip
        parts = osis_id.split(".")
        if len(parts) != 3:
            continue
        try:
            ch, v = int(parts[1]), int(parts[2])
        except ValueError:
            continue
        if (ch, v) in seen:
            continue
        seen.add((ch, v))
        words = [w.text for w in verse_el.iter(f"{OSIS_NS}w") if w.text]
        text = " ".join(words).strip()
        if text:
            out.append({
                "book_code": book_code,
                "chapter": ch,
                "verse": v,
                "version_code": "wlc",
                "text": text,
            })
    return out


# ─── LXX Rahlfs 1935 (Greek OT + Deuterocanon) ──────────────────────────────
# Single TSV file at eliranwong/LXX-Rahlfs-1935/.../LXX_final_main.csv
# Columns: book_id<TAB>chapter<TAB>verse<TAB>text
# Text has <S>...</S> Strong and <m>...</m> morph markers — strip them.

LXX_URL = (
    "https://raw.githubusercontent.com/eliranwong/LXX-Rahlfs-1935/master/"
    "11_end-users_files/MyBible/Bibles/LXX_final_main.csv"
)
# eliranwong/LXX-Rahlfs-1935 book IDs from books_main.csv.
# Note: 150 = Ezra (Esdras B/II 1-10), 160 = Neh (Esdras B/II 11-23).
LXX_BOOK_IDS = {
    10: "gen", 20: "exo", 30: "lev", 40: "num", 50: "deu",
    60: "jos", 70: "jdg", 80: "rut",
    90: "1sa", 100: "2sa", 110: "1ki", 120: "2ki",
    130: "1ch", 140: "2ch",
    150: "ezr", 160: "neh",   # LXX Esdras B/II split into Ezra+Neh
    165: "1es",                # LXX Esdras A/I = our 1 Esdras
    170: "tob", 180: "jdt", 190: "est",
    220: "job", 230: "psa", 240: "pro",
    250: "ecc", 260: "sng",
    270: "wis", 280: "sir",
    290: "isa", 300: "jer", 310: "lam",
    315: "epj", 320: "bar",
    325: "sus", 330: "ezk", 340: "dan", 345: "bel",
    350: "hos", 360: "jol", 370: "amo", 380: "oba", 390: "jon",
    400: "mic", 410: "nam", 420: "hab", 430: "zep",
    440: "hag", 450: "zec", 460: "mal",
    462: "1ma", 464: "2ma", 466: "3ma", 467: "4ma",
    # Skipped (not in our canon list): 232 = PsSol (Psalms of Solomon),
    # 800 = Od (Odes — pieces of other books); add later if needed.
}
LXX_STRIP = re.compile(r"<S>\d+</S>|<m>[^<]+</m>|<f>[^<]*</f>|<n>[^<]*</n>")


def ingest_lxx(dry_run=False):
    print("→ Ingesting LXX Rahlfs 1935 (Greek OT + Deutero, CC BY-NC-SA)")
    clear_version("lxx") if not dry_run else None
    r = requests.get(LXX_URL, timeout=60)
    r.encoding = "utf-8"
    rows = []
    skipped_books = set()
    for ln in r.text.splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = ln.split("\t")
        if len(parts) < 4:
            continue
        try:
            book_id = int(parts[0])
            ch = int(parts[1])
            v = int(parts[2])
        except ValueError:
            continue
        text = "\t".join(parts[3:])
        text = LXX_STRIP.sub("", text).strip()
        if not text:
            continue
        book_code = LXX_BOOK_IDS.get(book_id)
        if not book_code:
            skipped_books.add(book_id)
            continue
        rows.append({
            "book_code": book_code,
            "chapter": ch,
            "verse": v,
            "version_code": "lxx",
            "text": text,
        })
    if skipped_books:
        print(f"  ! skipped book_ids (no mapping): {sorted(skipped_books)}", file=sys.stderr)
    print(f"  parsed {len(rows)} verses")
    upsert_verses(rows, dry_run=dry_run)


# ─── CUV2010 (和合本2010) ───────────────────────────────────────────────────
# Scrape rcuv.hkbs.org.hk per chapter. Polite rate-limit (0.5s between requests).
# URL: https://rcuv.hkbs.org.hk/bb/info/RCUV2/{HKBS_CODE}/{chapter}/
# HKBS uses uppercase 3-letter codes matching OSIS (GEN, EXO, ..., MAT, ..., REV).

CUV_BASE = "https://rcuv.hkbs.org.hk/bb/info/RCUV2"  # RCUV2 = 上帝版；RCUV1 = 神版
CUV_BOOK_MAP = {  # our code → HKBS code (uppercase, mostly OSIS-compatible)
    "gen": "GEN", "exo": "EXO", "lev": "LEV", "num": "NUM", "deu": "DEU",
    "jos": "JOS", "jdg": "JDG", "rut": "RUT",
    "1sa": "1SA", "2sa": "2SA", "1ki": "1KI", "2ki": "2KI",
    "1ch": "1CH", "2ch": "2CH", "ezr": "EZR", "neh": "NEH", "est": "EST",
    "job": "JOB", "psa": "PSA", "pro": "PRO", "ecc": "ECC", "sng": "SNG",
    "isa": "ISA", "jer": "JER", "lam": "LAM", "ezk": "EZK", "dan": "DAN",
    "hos": "HOS", "jol": "JOL", "amo": "AMO", "oba": "OBA", "jon": "JON",
    "mic": "MIC", "nam": "NAM", "hab": "HAB", "zep": "ZEP", "hag": "HAG",
    "zec": "ZEC", "mal": "MAL",
    "mat": "MAT", "mrk": "MRK", "luk": "LUK", "jhn": "JHN", "act": "ACT",
    "rom": "ROM", "1co": "1CO", "2co": "2CO", "gal": "GAL", "eph": "EPH",
    "php": "PHP", "col": "COL", "1th": "1TH", "2th": "2TH", "1ti": "1TI",
    "2ti": "2TI", "tit": "TIT", "phm": "PHM", "heb": "HEB", "jas": "JAS",
    "1pe": "1PE", "2pe": "2PE", "1jn": "1JN", "2jn": "2JN", "3jn": "3JN",
    "jud": "JUD", "rev": "REV",
}
# CUV response = metadata line + HTML body. HTML pattern:
#   <h3>section</h3><p><b>1</b><span>text<i>name</i>text<sup title="footnote"></sup></span><b>2</b><span>...</span></p>
# Parse: <b>NUM</b><span>TEXT</span> pairs. Strip <i> (keep inner) and <sup title="..."> (drop).
CUV_BV_PAIR = re.compile(r'<b>(\d+)</b>\s*<span>(.*?)</span>', re.DOTALL)


def _clean_cuv_text(html):
    """Strip <i>...</i> wrappers (keep inner), drop <sup title="..."> footnotes,
    collapse whitespace."""
    # Strip footnote sups (empty tags with title attribute)
    html = re.sub(r'<sup[^>]*></sup>', '', html)
    html = re.sub(r'<sup[^>]*>.*?</sup>', '', html, flags=re.DOTALL)
    # Unwrap <i> tags
    html = re.sub(r'</?i>', '', html)
    # Drop any remaining HTML tags
    html = re.sub(r'<[^>]+>', '', html)
    # Collapse whitespace
    return re.sub(r'\s+', ' ', html).strip()


def ingest_cuv2010(dry_run=False, only_book=None, resume=False):
    print("→ Ingesting 和合本2010 RCUV (HKBS, scrape ~30-60 min)")
    if not dry_run and only_book is None and not resume:
        clear_version("cuv2010")

    # Get chapter counts from DB
    r = requests.get(
        f"{SUPA_URL}/rest/v1/bible_books?canon_protestant=eq.true&select=code,chapter_count",
        headers=PG_HEADERS, timeout=30,
    )
    chapter_counts = {row["code"]: row["chapter_count"] for row in r.json()}

    # Resume mode: skip books that already have ≥80% of their expected verses in DB.
    # Use Management API for a proper DISTINCT scan (PostgREST list view caps at 1000 rows).
    done_books = set()
    if resume:
        try:
            ref = SUPA_URL.replace("https://", "").split(".")[0]
            mgmt_resp = requests.post(
                f"https://api.supabase.com/v1/projects/{ref}/database/query",
                headers={
                    "Authorization": f"Bearer {ENV.get('SUPABASE_ACCESS_TOKEN', '')}",
                    "content-type": "application/json",
                },
                json={"query": "SELECT DISTINCT book_code FROM bible_verses WHERE version_code='cuv2010';"},
                timeout=30,
            )
            for row in mgmt_resp.json():
                done_books.add(row["book_code"])
        except Exception as e:
            print(f"  ! resume scan failed: {e}; doing full re-scrape", file=sys.stderr)
        print(f"  resume mode: {len(done_books)} books already in DB, skipping", file=sys.stderr)

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (research, Bible parallel study)"
    rows = []
    total_verses = 0
    for book_code, hkbs_code in CUV_BOOK_MAP.items():
        if only_book and book_code != only_book:
            continue
        if resume and book_code in done_books:
            continue
        n_chapters = chapter_counts.get(book_code, 0)
        if not n_chapters:
            continue
        book_verses = 0
        for ch in range(1, n_chapters + 1):
            url = f"{CUV_BASE}/{hkbs_code}/{ch}/"
            try:
                resp = session.get(url, timeout=30)
            except Exception as e:
                print(f"    ✗ {book_code} {ch}: {e}", file=sys.stderr)
                continue
            if resp.status_code != 200:
                print(f"    ✗ {book_code} {ch}: HTTP {resp.status_code}", file=sys.stderr)
                continue
            # Response starts with a metadata pipe-delimited line, then HTML
            body = resp.text
            # Find the first <h3> or <p> as start of HTML
            html_start = body.find("<")
            if html_start < 0:
                continue
            html = body[html_start:]
            for m in CUV_BV_PAIR.finditer(html):
                v_num = int(m.group(1))
                v_text = _clean_cuv_text(m.group(2))
                if not v_text:
                    continue
                rows.append({
                    "book_code": book_code,
                    "chapter": ch,
                    "verse": v_num,
                    "version_code": "cuv2010",
                    "text": v_text,
                })
                book_verses += 1
            time.sleep(0.25)  # be polite ~4 req/sec
        total_verses += book_verses
        print(f"  ✓ {book_code} ({hkbs_code}) {n_chapters} ch → {book_verses} verses (total {total_verses})",
              file=sys.stderr)
        # Flush per book so we don't lose all progress on crash
        if rows and not dry_run:
            upsert_verses(rows)
            rows = []
    print(f"  done — {total_verses} verses")


# ─── NIV (aruljohn/Bible-niv JSON dump) ─────────────────────────────────────
# Clean per-book JSON files. Each: { book, count, chapters: [{ chapter, verses: [{verse, text}] }] }

NIV_REPO = "aruljohn/Bible-niv/main"
NIV_BOOKS = {
    "Genesis": "gen", "Exodus": "exo", "Leviticus": "lev", "Numbers": "num",
    "Deuteronomy": "deu", "Joshua": "jos", "Judges": "jdg", "Ruth": "rut",
    "1 Samuel": "1sa", "2 Samuel": "2sa", "1 Kings": "1ki", "2 Kings": "2ki",
    "1 Chronicles": "1ch", "2 Chronicles": "2ch", "Ezra": "ezr", "Nehemiah": "neh",
    "Esther": "est", "Job": "job", "Psalms": "psa", "Proverbs": "pro",
    "Ecclesiastes": "ecc", "Song Of Solomon": "sng", "Isaiah": "isa", "Jeremiah": "jer",
    "Lamentations": "lam", "Ezekiel": "ezk", "Daniel": "dan", "Hosea": "hos",
    "Joel": "jol", "Amos": "amo", "Obadiah": "oba", "Jonah": "jon",
    "Micah": "mic", "Nahum": "nam", "Habakkuk": "hab", "Zephaniah": "zep",
    "Haggai": "hag", "Zechariah": "zec", "Malachi": "mal",
    "Matthew": "mat", "Mark": "mrk", "Luke": "luk", "John": "jhn",
    "Acts": "act", "Romans": "rom", "1 Corinthians": "1co", "2 Corinthians": "2co",
    "Galatians": "gal", "Ephesians": "eph", "Philippians": "php", "Colossians": "col",
    "1 Thessalonians": "1th", "2 Thessalonians": "2th", "1 Timothy": "1ti",
    "2 Timothy": "2ti", "Titus": "tit", "Philemon": "phm", "Hebrews": "heb",
    "James": "jas", "1 Peter": "1pe", "2 Peter": "2pe", "1 John": "1jn",
    "2 John": "2jn", "3 John": "3jn", "Jude": "jud", "Revelation": "rev",
}


def ingest_niv(dry_run=False):
    print("-> Ingesting NIV (aruljohn/Bible-niv JSON, (c) Biblica)")
    import json
    if not dry_run:
        clear_version("niv")
    rows = []
    for book_name, book_code in NIV_BOOKS.items():
        # URL-encode space
        url = f"{GITHUB_RAW}/{NIV_REPO}/{quote(book_name)}.json"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ {book_name}: HTTP {r.status_code}", file=sys.stderr)
            continue
        data = r.json()
        for chapter in data.get("chapters", []):
            ch_num = int(chapter["chapter"])
            for v in chapter.get("verses", []):
                v_num = int(v["verse"])
                text = (v.get("text") or "").strip()
                if not text:
                    continue
                rows.append({
                    "book_code": book_code,
                    "chapter": ch_num,
                    "verse": v_num,
                    "version_code": "niv",
                    "text": text,
                })
    print(f"  parsed {len(rows)} verses from {len(NIV_BOOKS)} books")
    upsert_verses(rows, dry_run=dry_run)


# ─── KJVA + 思高 (scrollmapper/bible_databases JSON) ────────────────────────
# Same schema: {translation, books: [{name, chapters: [{chapter, verses: [{verse, text}]}]}]}.
# We have these from one repo via different JSON files.

SCROLLMAPPER_BASE = "https://raw.githubusercontent.com/scrollmapper/bible_databases/master/formats/json"

# Map scrollmapper book "name" → our OSIS lowercase code.
# Includes special handling for Baruch (splits ch 6 → epj) and Daniel (Sigao splits 13/14 → sus/bel).
SCROLLMAPPER_BOOKS = {
    # OT 39
    "Genesis": "gen", "Exodus": "exo", "Leviticus": "lev", "Numbers": "num",
    "Deuteronomy": "deu", "Joshua": "jos", "Judges": "jdg", "Ruth": "rut",
    "I Samuel": "1sa", "II Samuel": "2sa", "I Kings": "1ki", "II Kings": "2ki",
    "I Chronicles": "1ch", "II Chronicles": "2ch", "Ezra": "ezr", "Nehemiah": "neh",
    "Esther": "est", "Job": "job", "Psalms": "psa", "Proverbs": "pro",
    "Ecclesiastes": "ecc", "Song of Solomon": "sng", "Isaiah": "isa", "Jeremiah": "jer",
    "Lamentations": "lam", "Ezekiel": "ezk", "Daniel": "dan", "Hosea": "hos",
    "Joel": "jol", "Amos": "amo", "Obadiah": "oba", "Jonah": "jon",
    "Micah": "mic", "Nahum": "nam", "Habakkuk": "hab", "Zephaniah": "zep",
    "Haggai": "hag", "Zechariah": "zec", "Malachi": "mal",
    # NT 27
    "Matthew": "mat", "Mark": "mrk", "Luke": "luk", "John": "jhn",
    "Acts": "act", "Romans": "rom", "I Corinthians": "1co", "II Corinthians": "2co",
    "Galatians": "gal", "Ephesians": "eph", "Philippians": "php", "Colossians": "col",
    "I Thessalonians": "1th", "II Thessalonians": "2th", "I Timothy": "1ti",
    "II Timothy": "2ti", "Titus": "tit", "Philemon": "phm", "Hebrews": "heb",
    "James": "jas", "I Peter": "1pe", "II Peter": "2pe", "I John": "1jn",
    "II John": "2jn", "III John": "3jn", "Jude": "jud", "Revelation": "rev",
    "Revelation of John": "rev",
    # Deuterocanon
    "Tobit": "tob", "Judith": "jdt", "Wisdom": "wis", "Sirach": "sir",
    "I Maccabees": "1ma", "II Maccabees": "2ma",
    "I Esdras": "1es", "II Esdras": "2es",
    "Prayer of Manasses": "man", "Prayer of Manasseh": "man",
    "Susanna": "sus",
    "Bel and the Dragon": "bel",
    "Prayer of Azariah": "aza",
    # Skip: "Additions to Esther" (folded back to est is messy — leave for Phase 2)
    # Special: "Baruch" → split ch 1-5 to bar, ch 6 to epj (Letter of Jeremiah)
    "Baruch": "bar",
}
SCROLLMAPPER_SKIP = {"Additions to Esther"}  # complicates est numbering


def _ingest_scrollmapper(version_code, json_filename, dry_run=False):
    print(f"-> Ingesting {version_code} (scrollmapper/{json_filename})")
    if not dry_run:
        clear_version(version_code)
    import json
    url = f"{SCROLLMAPPER_BASE}/{json_filename}"
    # Retry transient connection resets (large files + China network sometimes drop)
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=180, stream=False)
            if r.status_code != 200:
                print(f"  X HTTP {r.status_code}", file=sys.stderr)
                return
            data = r.json()
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
            wait = 2 ** attempt
            print(f"  ! attempt {attempt+1}/4 failed ({type(e).__name__}); retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    else:
        print(f"  X all attempts failed", file=sys.stderr)
        return
    rows = []
    unknown_books = set()
    for book in data.get("books", []):
        name = book["name"]
        if name in SCROLLMAPPER_SKIP:
            continue
        code = SCROLLMAPPER_BOOKS.get(name)
        if not code:
            unknown_books.add(name)
            continue
        for ch in book.get("chapters", []):
            ch_num = int(ch["chapter"])
            # SPLIT: Baruch ch 6 → epj
            if code == "bar" and ch_num == 6:
                eff_code, eff_ch = "epj", 1
            # SPLIT: 思高 Daniel ch 13/14 → sus/bel (KJVA already has them as separate books)
            elif code == "dan" and ch_num == 13 and version_code == "sigao":
                eff_code, eff_ch = "sus", 1
            elif code == "dan" and ch_num == 14 and version_code == "sigao":
                eff_code, eff_ch = "bel", 1
            else:
                eff_code, eff_ch = code, ch_num
            for v in ch.get("verses", []):
                v_num = int(v["verse"])
                text = (v.get("text") or "").strip()
                if not text:
                    continue
                rows.append({
                    "book_code": eff_code,
                    "chapter": eff_ch,
                    "verse": v_num,
                    "version_code": version_code,
                    "text": text,
                })
    if unknown_books:
        print(f"  ! unmapped books: {sorted(unknown_books)}", file=sys.stderr)
    print(f"  parsed {len(rows)} verses across {len({r['book_code'] for r in rows})} books")
    upsert_verses(rows, dry_run=dry_run)


def ingest_kjva(dry_run=False):
    _ingest_scrollmapper("kjva", "KJVA.json", dry_run=dry_run)


def ingest_sigao(dry_run=False):
    _ingest_scrollmapper("sigao", "ChiSB.json", dry_run=dry_run)


def ingest_cuv1919(dry_run=False):
    _ingest_scrollmapper("cuv1919", "ChiUn.json", dry_run=dry_run)


def ingest_cuv1919w(dry_run=False):
    _ingest_scrollmapper("cuv1919w", "ChiUnL.json", dry_run=dry_run)


def ingest_drc(dry_run=False):
    _ingest_scrollmapper("drc", "DRC.json", dry_run=dry_run)


def ingest_asv(dry_run=False):
    _ingest_scrollmapper("asv", "ASV.json", dry_run=dry_run)


def ingest_ylt(dry_run=False):
    _ingest_scrollmapper("ylt", "YLT.json", dry_run=dry_run)


# ─── Brenton LXX English (USFM zip from eBible.org) ─────────────────────────
# One zip → 60+ USFM files. We only fetch the books that fill our gaps
# (3ma/4ma/epj/ps2/2es) since KJVA + Sigao already cover the common deutero.

BRENTON_USFM_RAW = "https://ebible.org/Scriptures/eng-Brenton_usfm.zip"
# Map Brenton USFM book code → our code. USFM filename pattern: NN-XXXeng-Brenton.usfm
BRENTON_USFM_MAP = {
    "TOB": "tob", "JDT": "jdt", "WIS": "wis", "SIR": "sir",
    "BAR": "bar",       # Brenton has Baruch (only ch 1-5; LJE separate)
    "LJE": "epj",       # Letter of Jeremiah as separate file!
    "1MA": "1ma", "2MA": "2ma", "3MA": "3ma", "4MA": "4ma",
    "1ES": "1es",
    "MAN": "man",
    "SUS": "sus", "BEL": "bel",
    "DAG": "dan",       # Daniel-Greek (full inc. additions) — skip; use WLC/LXX/Sigao
}


def ingest_brenton(dry_run=False):
    print("-> Ingesting Brenton LXX English (eBible.org USFM)")
    if not dry_run:
        clear_version("brenton")
    import io, zipfile
    r = requests.get(BRENTON_USFM_RAW, timeout=120)
    if r.status_code != 200:
        print(f"  X HTTP {r.status_code}", file=sys.stderr)
        return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    rows = []
    # USFM verse marker: \v N text...  (chapter \c N, verse \v N)
    chap_re = re.compile(r"^\\c\s+(\d+)")
    verse_re = re.compile(r"^\\v\s+(\d+)([a-z]?)\s*(.*)")
    # Brenton inserts \p, \q, \s for paragraph/poetry/section — we skip those lines
    skip_markers = re.compile(r"^\\(p|q\d?|m|nb|s\d?|r|d|h|toc\d?|imt\d?|ip|ide|rem|mt\d?|usfm|fig)")
    for name in z.namelist():
        if not name.endswith(".usfm"):
            continue
        m = re.match(r"\d+-([A-Z0-9]+)eng-Brenton\.usfm", name)
        if not m:
            continue
        usfm_code = m.group(1)
        if usfm_code not in BRENTON_USFM_MAP:
            continue
        book_code = BRENTON_USFM_MAP[usfm_code]
        if usfm_code == "DAG":
            continue  # skip Daniel-Greek
        text = z.read(name).decode("utf-8")
        current_ch = 0
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            mc = chap_re.match(line)
            if mc:
                current_ch = int(mc.group(1))
                continue
            mv = verse_re.match(line)
            if mv and current_ch:
                # Brenton 'epj' (Letter of Jeremiah) is its own book → chapter 1
                ch = current_ch if usfm_code != "LJE" else 1
                v_num = int(mv.group(1))
                v_text = mv.group(3).strip()
                # Strip remaining USFM markers like \nd \nd*  \add \add* etc.
                v_text = re.sub(r"\\[a-z]+\*?\s?", "", v_text).strip()
                if not v_text:
                    continue
                rows.append({
                    "book_code": book_code,
                    "chapter": ch,
                    "verse": v_num,
                    "version_code": "brenton",
                    "text": v_text,
                })
            elif skip_markers.match(line):
                continue
    print(f"  parsed {len(rows)} verses across {len({r['book_code'] for r in rows})} books")
    upsert_verses(rows, dry_run=dry_run)


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version",
                    choices=["sblgnt", "vul", "wlc", "lxx", "cuv2010", "niv",
                             "kjva", "sigao", "brenton",
                             "cuv1919", "cuv1919w", "drc", "asv", "ylt", "all"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--book", help="Limit to one book code (for testing)")
    ap.add_argument("--resume", action="store_true",
                    help="CUV2010: skip books already in DB")
    args = ap.parse_args()

    if args.version == "all":
        for v in ("sblgnt", "vul", "wlc", "lxx"):
            globals()[f"ingest_{v}"](dry_run=args.dry_run)
        return

    fn_map = {
        "sblgnt": ingest_sblgnt,
        "vul": ingest_vul,
        "wlc": ingest_wlc,
        "lxx": ingest_lxx,
        "cuv2010": lambda dry_run=False: ingest_cuv2010(
            dry_run=dry_run, only_book=args.book, resume=args.resume),
        "niv": ingest_niv,
        "kjva": ingest_kjva,
        "sigao": ingest_sigao,
        "brenton": ingest_brenton,
        "cuv1919": ingest_cuv1919,
        "cuv1919w": ingest_cuv1919w,
        "drc": ingest_drc,
        "asv": ingest_asv,
        "ylt": ingest_ylt,
    }
    fn_map[args.version](dry_run=args.dry_run)


if __name__ == "__main__":
    main()
