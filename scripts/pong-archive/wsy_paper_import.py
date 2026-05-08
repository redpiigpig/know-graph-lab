#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import 龐君華 articles from 衛神院訊 (Methodist Graduate School of Theology Newsletter)
into pong_writings.

Reads tmp_methodist/wsy_articles/{NNN}.json files and inserts each into
pong_writings as category='periodical', publication='衛神院訊'.

Usage:
  python scripts/pong-archive/wsy_paper_import.py [--dry-run]
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

ARTICLES_DIR = ROOT / "tmp_methodist" / "wsy_articles"

CATEGORY = "periodical"
PUBLICATION = "衛神院訊"
SOURCE_URL = "https://www.mgst.org.tw/"


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


def article_exists(title: str) -> bool:
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
                   date_approximate: bool, issue_label: str,
                   author_role: str, sort_order: int,
                   dry_run: bool = False) -> int | None:
    payload = {
        "title": title,
        "category": CATEGORY,
        "publication": PUBLICATION,
        "published_date": published_date,
        "date_approximate": date_approximate,
        "content": body,
        "source_url": SOURCE_URL,
        "tags": ["衛神院訊", issue_label, author_role],
        "is_published": True,
        "sort_order": sort_order,
    }
    if dry_run:
        print(f"  [DRY-RUN] would insert: {title}  pub_date={published_date}"
              f"{' (approximate)' if date_approximate else ''}")
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

    stats = {"inserted": 0, "skip_exists": 0, "failed": 0}

    for path in files:
        d = json.loads(path.read_text(encoding="utf-8"))
        title = d["title"].strip()
        body = d["body"].strip()
        pub_date = d["published_date"]
        approx = d.get("date_approximate", False)
        issue_label = d["issue_label"]
        author_role = d.get("author_role", "")

        if not title or not body:
            print(f"[skip-empty] {path.name}")
            stats["failed"] += 1
            continue

        try:
            if article_exists(title):
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
                date_approximate=approx,
                issue_label=issue_label,
                author_role=author_role,
                sort_order=next_sort,
                dry_run=dry_run,
            )
            print(f"[ok] {path.name} -> id={wid} sort={next_sort} title='{title}' "
                  f"date={pub_date}{'~' if approx else ''}")
            next_sort += 1
            stats["inserted"] += 1
        except Exception as e:
            print(f"[fail] {path.name}: {e}")
            stats["failed"] += 1

    print(f"\n=== DONE  inserted={stats['inserted']}  "
          f"skip_exists={stats['skip_exists']}  failed={stats['failed']} ===")


if __name__ == "__main__":
    main()
