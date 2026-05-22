"""
Lookup ebook cover image URL via Google Books + Open Library.

Strategy per book:
  1. Google Books search `intitle:{title}+inauthor:{author}` → pick first volume's
     `imageLinks.thumbnail` (HTTPS, ~128px wide). Replace `&edge=curl` with
     `&zoom=1` to get larger 256-320px version.
  2. If Google miss, try Open Library `https://covers.openlibrary.org/b/title/{title}-L.jpg`.
     (Hit rate poor for Chinese, but free + no key.)
  3. Skip if `cover_url` already set (unless --force).

Writes to ebooks.cover_url + ebooks.cover_source.

Usage:
  python scripts/lookup_book_cover.py --book <id>            # single
  python scripts/lookup_book_cover.py --book <id> --force    # overwrite
  python scripts/lookup_book_cover.py --category 神學 --limit 50
  python scripts/lookup_book_cover.py --status               # how many missing
"""
import argparse
import os
import sys
import time
import urllib.parse
from pathlib import Path

import requests

# Force UTF-8 on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load_env() -> None:
    envf = Path(__file__).parent.parent / ".env"
    for line in envf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        os.environ.setdefault(k.strip(), v)


def supabase_headers() -> dict:
    return {
        "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
        "Content-Type": "application/json",
    }


def google_books_lookup(title: str, author: str | None) -> str | None:
    """Try Google Books. Returns HTTPS thumbnail URL or None."""
    q_parts = [f'intitle:{title}']
    if author:
        # Author field gets noisy with translators; use only the surname/first
        # token if it's "作者，譯者" form.
        clean_author = author.split("，")[0].split(",")[0].strip()
        if clean_author:
            q_parts.append(f"inauthor:{clean_author}")
    q = "+".join(q_parts)
    url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(q)}&maxResults=5&langRestrict=zh"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        items = r.json().get("items", [])
        for item in items:
            info = item.get("volumeInfo", {})
            links = info.get("imageLinks") or {}
            # Prefer larger size if available
            for key in ("medium", "small", "thumbnail", "smallThumbnail"):
                if key in links:
                    img = links[key]
                    # Upgrade to https + larger zoom
                    img = img.replace("http://", "https://")
                    img = img.replace("&edge=curl", "")
                    if "zoom=" in img:
                        import re
                        img = re.sub(r"zoom=\d", "zoom=0", img)
                    return img
    except Exception as e:
        print(f"    google books error: {e}", file=sys.stderr)
    return None


def open_library_lookup(title: str) -> str | None:
    """Try Open Library by title. Returns URL or None."""
    # Use the search.json API to get OLID first, then build cover URL
    try:
        url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(title)}&limit=3"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        docs = r.json().get("docs", [])
        for d in docs:
            cover_id = d.get("cover_i")
            if cover_id:
                return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    except Exception as e:
        print(f"    open library error: {e}", file=sys.stderr)
    return None


def fetch_candidates(args) -> list[dict]:
    """Fetch ebooks needing cover lookup."""
    base = os.environ["SUPABASE_URL"] + "/rest/v1/ebooks"
    params = ["select=id,title,author,category,cover_url"]
    if args.book:
        params.append(f"id=eq.{args.book}")
    else:
        if not args.force:
            params.append("cover_url=is.null")
        if args.category:
            params.append(f"category=eq.{urllib.parse.quote(args.category)}")
        params.append(f"limit={args.limit}")
        params.append("order=created_at.desc")
    url = base + "?" + "&".join(params)
    r = requests.get(url, headers=supabase_headers(), timeout=15)
    r.raise_for_status()
    return r.json()


def update_cover(book_id: str, cover_url: str, source: str) -> None:
    base = os.environ["SUPABASE_URL"] + "/rest/v1/ebooks"
    r = requests.patch(
        f"{base}?id=eq.{book_id}",
        headers={**supabase_headers(), "Prefer": "return=minimal"},
        json={"cover_url": cover_url, "cover_source": source},
        timeout=15,
    )
    r.raise_for_status()


def status(args) -> None:
    base = os.environ["SUPABASE_URL"] + "/rest/v1/ebooks"
    h = {**supabase_headers(), "Prefer": "count=exact", "Range": "0-0"}
    r_total = requests.get(f"{base}?select=id", headers=h, timeout=15)
    r_done = requests.get(f"{base}?select=id&cover_url=not.is.null", headers=h, timeout=15)
    total = int(r_total.headers.get("Content-Range", "0-0/0").split("/")[-1])
    done = int(r_done.headers.get("Content-Range", "0-0/0").split("/")[-1])
    print(f"ebooks with cover_url: {done} / {total}")


def run(args) -> None:
    books = fetch_candidates(args)
    print(f"Found {len(books)} candidate(s)")
    print()
    ok, miss = 0, 0
    for b in books:
        title = b["title"]
        author = b.get("author") or ""
        if b.get("cover_url") and not args.force:
            print(f"  skip (already has cover): {title}")
            continue
        print(f"→ {title} / {author}")
        # 1. Google Books
        cover = google_books_lookup(title, author)
        source = "google_books"
        # 2. Open Library fallback
        if not cover:
            cover = open_library_lookup(title)
            source = "open_library" if cover else None
        if cover:
            print(f"  ✓ {source}: {cover}")
            if not args.dry_run:
                update_cover(b["id"], cover, source)
            ok += 1
        else:
            print(f"  ✗ no cover found")
            miss += 1
        time.sleep(0.5)  # polite rate
    print()
    print(f"Done: {ok} found / {miss} missed / {len(books)} total")


def main() -> None:
    load_env()
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    rp = sub.add_parser("run")
    rp.add_argument("--book", help="single ebook id")
    rp.add_argument("--category")
    rp.add_argument("--limit", type=int, default=100)
    rp.add_argument("--force", action="store_true")
    rp.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.cmd == "status":
        status(args)
    elif args.cmd == "run":
        run(args)


if __name__ == "__main__":
    main()
