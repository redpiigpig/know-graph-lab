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
    """
    if dry_run:
        print(f"  [dry-run] would upsert {len(rows)} rows; sample: {rows[:2]}")
        return
    if not rows:
        return
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
# eliranwong uses MySword-style book ids: 10=Gen, 20=Exo, ..., 670=Sir, 700=Tobit, etc.
# Reference: https://github.com/eliranwong/LXX-Rahlfs-1935/blob/master/.../books_main.csv
LXX_BOOK_IDS = {
    10: "gen", 20: "exo", 30: "lev", 40: "num", 50: "deu",
    60: "jos", 70: "jdg", 80: "rut",
    90: "1sa", 100: "2sa", 110: "1ki", 120: "2ki",
    130: "1ch", 140: "2ch",
    150: "1es",  # 1 Esdras (LXX Esdras A)
    160: "ezr",  # 2 Esdras (LXX Esdras B = Ezra-Neh; we split below)
    190: "est", 200: "jdt", 210: "tob",
    220: "1ma", 230: "2ma", 240: "3ma", 250: "4ma",
    220.5: "1ma",  # safety
    260: "psa", 265: "ps2",  # Psalm 151
    270: "pro", 280: "ecc", 290: "sng",
    300: "job", 305: "wis", 310: "sir",
    315: "ps2",  # Odes/Pss of Solomon possibly — exclude
    320: "hos", 330: "amo", 340: "mic", 350: "jol", 360: "oba",
    370: "jon", 380: "nam", 390: "hab", 400: "zep", 410: "hag",
    420: "zec", 430: "mal",
    440: "isa", 450: "jer", 460: "bar", 470: "lam", 480: "epj",
    490: "ezk", 500: "sus", 510: "dan", 520: "bel",
    # Variants (LXX2 columns) skipped — main file uses these.
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
CUV_VERSE_RE = re.compile(r'<span[^>]*class="[^"]*verse[^"]*"[^>]*>.*?(\d+)\s*(.*?)</span>',
                          re.DOTALL)


def ingest_cuv2010(dry_run=False, only_book=None):
    print("→ Ingesting 和合本2010 RCUV (HKBS, scrape; slow ~1 hr)")
    if not dry_run:
        clear_version("cuv2010") if only_book is None else None
    from bs4 import BeautifulSoup  # type: ignore

    # Get chapter counts from bible_books
    r = requests.get(
        f"{SUPA_URL}/rest/v1/bible_books?canon_protestant=eq.true&select=code,chapter_count",
        headers=PG_HEADERS, timeout=30,
    )
    chapter_counts = {row["code"]: row["chapter_count"] for row in r.json()}
    rows = []
    for book_code, hkbs_code in CUV_BOOK_MAP.items():
        if only_book and book_code != only_book:
            continue
        n_chapters = chapter_counts.get(book_code, 0)
        if not n_chapters:
            continue
        print(f"  {book_code} ({hkbs_code}) {n_chapters} chapters", file=sys.stderr)
        for ch in range(1, n_chapters + 1):
            url = f"{CUV_BASE}/{hkbs_code}/{ch}/"
            try:
                resp = requests.get(url, timeout=30,
                                    headers={"User-Agent": "Mozilla/5.0 (research)"})
            except Exception as e:
                print(f"    ✗ {book_code} {ch}: {e}", file=sys.stderr)
                continue
            if resp.status_code != 200:
                print(f"    ✗ {book_code} {ch}: HTTP {resp.status_code}", file=sys.stderr)
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            # The structure on rcuv.hkbs.org.hk: <div class="bibleVerse"> contains
            # verses, each as <p> or <span> with verse number + text.
            # Find all verse-bearing elements; structure can vary.
            verse_container = soup.select_one(
                ".bibleVerse, .scripture, #scripture, .bible-text, .chapter-content")
            if not verse_container:
                # Fallback: whole body
                verse_container = soup.body or soup
            # Each verse: typically <sup>1</sup> verse text <sup>2</sup> verse text ...
            # We split on superscript number markers.
            html = str(verse_container)
            # Strip script/style
            for tag in verse_container.find_all(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            # Get text with verse-number markers preserved
            text_with_marks = ""
            for el in verse_container.descendants:
                if hasattr(el, "name") and el.name == "sup":
                    text_with_marks += f"\n[V{el.get_text(strip=True)}] "
                elif hasattr(el, "name") and el.name is None:
                    text_with_marks += str(el)
            # Split on \n[Vn]
            for m in re.finditer(r"\[V(\d+)\]\s*(.+?)(?=\[V\d+\]|$)",
                                  text_with_marks, re.DOTALL):
                v_num = int(m.group(1))
                v_text = m.group(2).strip()
                v_text = re.sub(r"\s+", " ", v_text)
                if not v_text:
                    continue
                rows.append({
                    "book_code": book_code,
                    "chapter": ch,
                    "verse": v_num,
                    "version_code": "cuv2010",
                    "text": v_text,
                })
            time.sleep(0.4)  # be polite
        # Flush per book to avoid losing data on crash
        if rows and not dry_run:
            upsert_verses(rows)
            rows = []
    print(f"  done")


# ─── NIV (NIV84 dump) ───────────────────────────────────────────────────────
# Use Rosuav/NIV84 GitHub dump as starting point — messy HTML per book.
# For MVP we'll use a cleaner unofficial JSON if found; else skip until later.

def ingest_niv(dry_run=False):
    print("→ NIV ingest not yet implemented (need to scout cleaner source).")
    print("  Run with --version niv-skip to suppress this message.")
    return


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version",
                    choices=["sblgnt", "vul", "wlc", "lxx", "cuv2010", "niv", "all"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--book", help="Limit to one book code (for testing)")
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
        "cuv2010": lambda dry_run=False: ingest_cuv2010(dry_run=dry_run, only_book=args.book),
        "niv": ingest_niv,
    }
    fn_map[args.version](dry_run=args.dry_run)


if __name__ == "__main__":
    main()
