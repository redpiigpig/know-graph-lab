#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import 龐君華會督 articles from 中華衛訊 (Methodist Paper) into pong_writings.

Reads tmp_methodist/articles/{NN}.json files (produced by methodist_paper_extract.py)
and inserts each into pong_writings as category='periodical', publication='中華衛訊'.

Usage:
  python scripts/pong-archive/methodist_paper_import.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

ARTICLES_DIR = ROOT / "tmp_methodist" / "articles"
SOURCE_BASE_URL = "https://methodist.org.tw/methodistpaper/"

CATEGORY = "periodical"
PUBLICATION = "中華衛訊"

# Issue PDF URLs (for source_url)
ISSUE_PDF = {
    105: "https://methodist.org.tw/wp-content/uploads/2024/01/105.pdf",
    106: "https://methodist.org.tw/wp-content/uploads/2024/01/106.pdf",
    107: "https://methodist.org.tw/wp-content/uploads/2024/01/107.pdf",
    108: "https://methodist.org.tw/wp-content/uploads/2024/01/108.pdf",
    109: "https://methodist.org.tw/wp-content/uploads/2024/01/109.pdf",
    110: "https://methodist.org.tw/wp-content/uploads/2024/01/110.pdf",
    111: "https://methodist.org.tw/wp-content/uploads/2024/01/111.pdf",
    112: "https://methodist.org.tw/wp-content/uploads/2024/01/112.pdf",
}


def sb_url() -> str:
    return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"


def sb_headers() -> dict:
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def max_sort_order() -> int:
    r = requests.get(
        f"{sb_url()}/pong_writings",
        headers=sb_headers(),
        params={"select": "sort_order", "order": "sort_order.desc", "limit": 1},
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0]["sort_order"] if rows else 0


def article_exists(source_url: str, title: str) -> bool:
    r = requests.get(
        f"{sb_url()}/pong_writings",
        headers=sb_headers(),
        params={
            "select": "id",
            "publication": f"eq.{PUBLICATION}",
            "title": f"eq.{title}",
        },
    )
    r.raise_for_status()
    return bool(r.json())


def insert_article(*, title: str, body: str, published_date: str,
                   issue_label: str, source_url: str, sort_order: int,
                   dry_run: bool = False) -> int | None:
    payload = {
        "title": title,
        "category": CATEGORY,
        "publication": PUBLICATION,
        "published_date": published_date,
        "content": body,
        "source_url": source_url,
        "tags": ["中華衛訊", "會督的話", issue_label],
        "is_published": True,
        "sort_order": sort_order,
    }
    if dry_run:
        print(f"  [DRY-RUN] would insert: {title}  pub_date={published_date}")
        return None
    r = requests.post(
        f"{sb_url()}/pong_writings",
        headers=sb_headers(),
        json=payload,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()[0]["id"]


def main():
    dry_run = "--dry-run" in sys.argv
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")

    files = sorted(ARTICLES_DIR.glob("*.json"))
    if not files:
        print("No article JSONs found.")
        return

    next_sort = max_sort_order() + 1
    print(f"next_sort starts at: {next_sort}")

    stats = {"inserted": 0, "skip_no_pong": 0, "skip_exists": 0, "failed": 0}

    for path in files:
        d = json.loads(path.read_text(encoding="utf-8"))
        if not d.get("has_pong_article"):
            print(f"[skip-no-pong] {path.name}")
            stats["skip_no_pong"] += 1
            continue

        title = d.get("title", "").strip()
        body = d.get("body", "").strip()
        pub_date = d["_published_date"]
        issue_num = d["_issue"]
        issue_label = d["_issue_label"]
        source_url = ISSUE_PDF.get(issue_num, SOURCE_BASE_URL)

        if not title or not body:
            print(f"[skip-empty] {path.name}: title or body missing")
            stats["failed"] += 1
            continue

        try:
            if article_exists(source_url, title):
                print(f"[skip-exists] {path.name}: '{title}' already in DB")
                stats["skip_exists"] += 1
                continue
        except Exception as e:
            print(f"[db-check-fail] {path.name}: {e}")
            stats["failed"] += 1
            continue

        try:
            wid = insert_article(
                title=title,
                body=body,
                published_date=pub_date,
                issue_label=issue_label,
                source_url=source_url,
                sort_order=next_sort,
                dry_run=dry_run,
            )
            print(f"[ok] {path.name} -> id={wid} sort={next_sort} title='{title}' "
                  f"date={pub_date}")
            next_sort += 1
            stats["inserted"] += 1
        except Exception as e:
            print(f"[fail] {path.name}: {e}")
            stats["failed"] += 1

    print(f"\n=== DONE  inserted={stats['inserted']}  "
          f"skip_no_pong={stats['skip_no_pong']}  "
          f"skip_exists={stats['skip_exists']}  "
          f"failed={stats['failed']} ===")


if __name__ == "__main__":
    main()
