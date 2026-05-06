#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fill missing publisher / publish_year on `books` rows via online lookup.

Sources (in order, Chinese-titled books prefer Google Books, others Open Library):
  1. Open Library Search   https://openlibrary.org/search.json
  2. Google Books v1       https://www.googleapis.com/books/v1/volumes

Idempotent + safe:
- Only updates fields that are currently NULL.
- Skips rows where `metadata_locked = true` (manual-edit protection).
- Sets `metadata_source` to the provider name when at least one field was filled.

Usage:
  python scripts/enrich_book_metadata.py status
  python scripts/enrich_book_metadata.py run [--limit N] [--dry-run] [--book <uuid>]
  python scripts/enrich_book_metadata.py probe --book <uuid>      # dump raw API responses
"""
import argparse
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Missing dependency. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


# ── env loading ────────────────────────────────────────────────
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
GOOGLE_BOOKS_KEY = ENV.get("GOOGLE_BOOKS_API_KEY") or os.environ.get("GOOGLE_BOOKS_API_KEY")

REST_HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type": "application/json",
}
HTTP_HEADERS = {
    "User-Agent": "know-graph-lab-enrich/1.0 (personal; redpiigpig@gmail.com)",
    "Accept": "application/json",
}


# ── helpers ────────────────────────────────────────────────────
def is_cjk(s: str) -> bool:
    if not s:
        return False
    cjk = sum(1 for c in s if "　" <= c <= "鿿")
    return cjk / max(len(s), 1) > 0.3


_PUNCT_RE = re.compile(r"[\s\W_]+", re.UNICODE)


def _norm(s: str) -> str:
    return _PUNCT_RE.sub("", (s or "").lower())


def title_match(a: str, b: str) -> bool:
    """Return True if `a` and `b` likely refer to the same title."""
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    if na == nb or na in nb or nb in na:
        return True
    # CJK char overlap
    common = sum(1 for ch in na if ch in nb)
    return common >= max(4, int(len(na) * 0.6))


def _author_tokens(name: str):
    if not name:
        return []
    out = []
    for tok in re.split(r"[\s,，、・·\-]+", name):
        tok = tok.strip()
        if tok:
            out.append(tok.lower())
    return out


def author_match(query_author: str, candidate_authors) -> bool:
    if not query_author:
        return True  # caller decided to skip author check
    if not candidate_authors:
        return False
    if isinstance(candidate_authors, str):
        candidate_authors = [candidate_authors]
    q_tokens = _author_tokens(query_author)
    for ca in candidate_authors:
        if not ca:
            continue
        ca_tokens = _author_tokens(ca)
        ca_norm = _norm(ca)
        q_norm = _norm(query_author)
        if q_norm and (q_norm in ca_norm or ca_norm in q_norm):
            return True
        for tok in q_tokens:
            if len(tok) >= 2 and any(tok in c for c in ca_tokens):
                return True
        for tok in ca_tokens:
            if len(tok) >= 2 and any(tok in q for q in q_tokens):
                return True
    return False


def _year(s: str) -> Optional[int]:
    if not s:
        return None
    m = re.search(r"(1[0-9]{3}|20[0-9]{2})", str(s))
    return int(m.group(1)) if m else None


# ── lookup providers ───────────────────────────────────────────
_SUBTITLE_SPLITTERS = re.compile(r"[：:—\-‧·]")


def _title_variants(title: str):
    """Yield title strings worth searching, most-specific first."""
    seen = set()
    candidates = [title]
    # Strip 《》「」（）
    stripped = re.sub(r"[《》「」『』（）()【】]", "", title)
    if stripped != title:
        candidates.append(stripped)
    # Drop subtitle after ：/:/—/-
    parts = _SUBTITLE_SPLITTERS.split(stripped)
    if len(parts) > 1 and parts[0].strip():
        candidates.append(parts[0].strip())
    for c in candidates:
        c = c.strip()
        if c and c not in seen:
            seen.add(c)
            yield c


def _gb_query(url: str, debug=False, label=""):
    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=20)
    except Exception as e:
        print(f"    google_books net error: {e}", file=sys.stderr)
        return []
    if debug:
        print(f"    [google_books {r.status_code} {label}] {url[:140]}")
    if r.status_code != 200:
        return []
    return r.json().get("items") or []


def _gb_match(items, title, author, debug=False):
    for it in items[:5]:
        info = it.get("volumeInfo", {}) or {}
        d_title = info.get("title", "") + (": " + info.get("subtitle", "") if info.get("subtitle") else "")
        d_authors = info.get("authors") or []
        if debug:
            print(f"      candidate: {d_title!r} by {d_authors} | publisher={info.get('publisher')} date={info.get('publishedDate')}")
        if not title_match(title, d_title) and not title_match(title, info.get("title", "")):
            continue
        if author and not author_match(author, d_authors):
            continue
        publisher = info.get("publisher")
        year = _year(info.get("publishedDate"))
        if publisher or year:
            return {"publisher": publisher, "publish_year": year, "source": "google_books"}
    return None


def lookup_google_books(title: str, author: Optional[str], debug=False):
    """Try precise → title-variant → free-text queries until one matches."""
    key_suffix = f"&key={urllib.parse.quote_plus(GOOGLE_BOOKS_KEY)}" if GOOGLE_BOOKS_KEY else ""
    for variant in _title_variants(title):
        # Pass 1: intitle + inauthor (when we have author)
        if author:
            q = f'intitle:"{variant}"+inauthor:"{author}"'
            url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote_plus(q, safe='+:\"')}&maxResults=5{key_suffix}"
            items = _gb_query(url, debug, label=f"intitle+inauthor [{variant[:20]}]")
            hit = _gb_match(items, title, author, debug)
            if hit:
                return hit
        # Pass 2: intitle only
        q = f'intitle:"{variant}"'
        url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote_plus(q, safe='+:\"')}&maxResults=5{key_suffix}"
        items = _gb_query(url, debug, label=f"intitle [{variant[:20]}]")
        hit = _gb_match(items, title, author, debug)
        if hit:
            return hit
    # Pass 3: free-text title + author
    if author:
        q = f"{title} {author}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote_plus(q)}&maxResults=5{key_suffix}"
        items = _gb_query(url, debug, label="freetext+author")
        hit = _gb_match(items, title, author, debug)
        if hit:
            return hit
    return None


def _ol_query(params, debug=False, label=""):
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode(params)
    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=20)
    except Exception as e:
        print(f"    open_library net error: {e}", file=sys.stderr)
        return []
    if debug:
        print(f"    [open_library {r.status_code} {label}] {url[:140]}")
    if r.status_code != 200:
        return []
    return r.json().get("docs") or []


def _ol_match(docs, title, author, debug=False):
    for d in docs[:5]:
        d_title = d.get("title", "")
        d_authors = d.get("author_name") or []
        if debug:
            print(f"      candidate: {d_title!r} by {d_authors}")
        if not title_match(title, d_title):
            continue
        if author and not author_match(author, d_authors):
            continue
        publisher = (d.get("publisher") or [None])[0]
        publish_dates = d.get("publish_date") or []
        year = d.get("first_publish_year") or (_year(publish_dates[0]) if publish_dates else None)
        if publisher or year:
            return {"publisher": publisher, "publish_year": year, "source": "open_library"}
    return None


def lookup_open_library(title: str, author: Optional[str], debug=False):
    for variant in _title_variants(title):
        if author:
            docs = _ol_query({"title": variant, "author": author, "limit": "5"}, debug, f"title+author [{variant[:20]}]")
            hit = _ol_match(docs, title, author, debug)
            if hit:
                return hit
        docs = _ol_query({"title": variant, "limit": "5"}, debug, f"title [{variant[:20]}]")
        hit = _ol_match(docs, title, author, debug)
        if hit:
            return hit
    return None


def enrich_one(book, debug=False):
    """Look up missing fields; return dict of fields to PATCH (only nulls + metadata_source)."""
    title = book.get("title") or ""
    author = book.get("author") or None
    if not title:
        return {}
    cjk = is_cjk(title)
    providers = (lookup_google_books, lookup_open_library) if cjk else (lookup_open_library, lookup_google_books)
    for src in providers:
        result = src(title, author, debug=debug)
        if not result:
            continue
        update = {}
        if book.get("publisher") is None and result.get("publisher"):
            update["publisher"] = result["publisher"]
        if book.get("publish_year") is None and result.get("publish_year"):
            update["publish_year"] = result["publish_year"]
        if update:
            update["metadata_source"] = result["source"]
            return update
    return {}


# ── DB ops ─────────────────────────────────────────────────────
def fetch_books_needing_enrichment(book_id=None):
    if book_id:
        url = f"{SUPA_URL}/rest/v1/books?id=eq.{book_id}&select=id,title,author,publisher,publish_year,metadata_locked"
    else:
        # nulls + not locked
        url = (
            f"{SUPA_URL}/rest/v1/books"
            f"?select=id,title,author,publisher,publish_year,metadata_locked"
            f"&or=(publisher.is.null,publish_year.is.null)"
            f"&metadata_locked=is.false"
            f"&order=title"
        )
    r = requests.get(url, headers=REST_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def patch_book(book_id, fields):
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        return
    url = f"{SUPA_URL}/rest/v1/books?id=eq.{book_id}"
    r = requests.patch(
        url,
        headers={**REST_HEADERS, "Prefer": "return=minimal"},
        json=fields,
        timeout=20,
    )
    r.raise_for_status()


# ── commands ───────────────────────────────────────────────────
def cmd_status(_args):
    rows = fetch_books_needing_enrichment()
    locked = requests.get(
        f"{SUPA_URL}/rest/v1/books?select=id&metadata_locked=is.true",
        headers=REST_HEADERS,
        timeout=15,
    ).json()
    total = requests.get(
        f"{SUPA_URL}/rest/v1/books?select=id",
        headers={**REST_HEADERS, "Prefer": "count=exact", "Range-Unit": "items", "Range": "0-0"},
        timeout=15,
    )
    total_count = total.headers.get("Content-Range", "0/0").split("/")[-1]
    pub_null = sum(1 for r in rows if r["publisher"] is None)
    yr_null = sum(1 for r in rows if r["publish_year"] is None)
    print(f"books total:                {total_count}")
    print(f"need enrichment:            {len(rows)}  (publisher null: {pub_null}, publish_year null: {yr_null})")
    print(f"metadata_locked:            {len(locked)}")
    if GOOGLE_BOOKS_KEY:
        print("google_books key:           present (higher quota)")
    else:
        print("google_books key:           missing (using anonymous quota)")


def cmd_run(args):
    if args.book:
        rows = fetch_books_needing_enrichment(args.book)
    else:
        rows = fetch_books_needing_enrichment()
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("nothing to do")
        return
    print(f"{'DRY-RUN ' if args.dry_run else ''}enriching {len(rows)} books\n")
    filled_pub = filled_yr = no_hit = 0
    for i, b in enumerate(rows, 1):
        title = b["title"]
        author = b.get("author") or "?"
        print(f"[{i}/{len(rows)}] {title[:50]}  ({author[:24]})")
        if b["metadata_locked"]:
            print("  → skipped (metadata_locked)")
            continue
        update = enrich_one(b, debug=args.debug)
        if update:
            print(f"  → {update}")
            if "publisher" in update:
                filled_pub += 1
            if "publish_year" in update:
                filled_yr += 1
            if not args.dry_run:
                try:
                    patch_book(b["id"], update)
                except Exception as e:
                    print(f"  ! PATCH failed: {e}", file=sys.stderr)
        else:
            print("  → no hit")
            no_hit += 1
        time.sleep(args.sleep)
    print(f"\nfilled publisher: {filled_pub}, filled publish_year: {filled_yr}, no hit: {no_hit}")


def cmd_probe(args):
    if not args.book:
        print("probe needs --book <uuid>", file=sys.stderr)
        sys.exit(2)
    rows = fetch_books_needing_enrichment(args.book)
    if not rows:
        print("book not found", file=sys.stderr)
        sys.exit(2)
    b = rows[0]
    print(f"Probing: {b['title']}  ({b.get('author','?')})\n")
    enrich_one(b, debug=True)


# ── entry ──────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    rp = sub.add_parser("run")
    rp.add_argument("--limit", type=int)
    rp.add_argument("--dry-run", action="store_true")
    rp.add_argument("--book", type=str, help="enrich a single book by id")
    rp.add_argument("--debug", action="store_true")
    rp.add_argument("--sleep", type=float, default=0.6)
    pp = sub.add_parser("probe")
    pp.add_argument("--book", type=str, required=True)
    args = p.parse_args()
    {"status": cmd_status, "run": cmd_run, "probe": cmd_probe}[args.cmd](args)


if __name__ == "__main__":
    main()
