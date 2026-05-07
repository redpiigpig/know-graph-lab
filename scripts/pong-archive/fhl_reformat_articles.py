#!/usr/bin/env python3
"""
fhl_reformat_articles.py — 重新格式化 pong_writings 中的衛蘭專文（category='web'）。

變更：
- 在文章開頭加上「作者：龐君華」
- 每段首行加全形縮排「　　」
- 文章末尾加「原文網址：{source_url}」

Usage:
  python scripts/pong-archive/fhl_reformat_articles.py [--dry-run]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DRY_RUN = "--dry-run" in sys.argv


# ─── Supabase ────────────────────────────────────────────────────────────────

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


def fetch_web_articles() -> list[dict]:
    r = requests.get(
        f"{_sb_url()}/pong_writings",
        headers=_sb_headers(),
        params={
            "select": "id,title,content,source_url",
            "category": "eq.web",
            "publication": "eq.衛蘭專文",
            "order": "sort_order.asc",
        },
    )
    r.raise_for_status()
    return r.json()


def patch_content(article_id: int, new_content: str) -> None:
    r = requests.patch(
        f"{_sb_url()}/pong_writings",
        headers={**_sb_headers(), "Prefer": "return=minimal"},
        params={"id": f"eq.{article_id}"},
        json={"content": new_content},
    )
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")


# ─── Formatting ──────────────────────────────────────────────────────────────

def _is_heading(line: str) -> bool:
    t = line.strip()
    if not t:
        return False
    return (
        len(t) <= 20
        and not re.search(r"[，。！？、；：]$", t)
        and re.search(r"[一-鿿]", t)
    )


def already_formatted(content: str) -> bool:
    """Check if the content was already reformatted (has author header)."""
    return content.lstrip().startswith("作者：龐君華")


def reformat(content: str, source_url: str) -> str:
    """
    Reformat article content:
    1. Prepend 作者：龐君華
    2. Indent first line of each paragraph block with
    3. Append 原文網址：{source_url}

    Quote blocks (lines starting with '> ') are left untouched — they
    must be marked manually in the content before running this script.
    """
    blocks = re.split(r"\n\n+", content.strip())
    out: list[str] = ["作者：龐君華"]

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        first = lines[0].strip()

        # Single-line heading → keep as-is
        if len(lines) == 1 and _is_heading(first):
            out.append(block)
            continue

        # Quote block (starts with "> ") → keep as-is
        if first.startswith("> "):
            out.append(block)
            continue

        # Regular paragraph → indent first line
        lines[0] = "　　" + lines[0].lstrip("　 \t")
        out.append("\n".join(lines))

    out.append(f"原文網址：{source_url}")
    return "\n\n".join(out)


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    articles = fetch_web_articles()
    print(f"Found {len(articles)} 衛蘭專文 articles{'  [DRY-RUN]' if DRY_RUN else ''}")

    ok = skip = fail = 0

    for art in articles:
        art_id = art["id"]
        title = art["title"][:40]
        content = art["content"] or ""
        source_url = art["source_url"] or ""

        if already_formatted(content):
            print(f"[skip-already] id={art_id}  {title}")
            skip += 1
            continue

        new_content = reformat(content, source_url)

        if DRY_RUN:
            print(f"[dry-run] id={art_id}  {title}")
            # Show first 3 lines of new content for verification
            for line in new_content.split("\n")[:5]:
                print(f"  {line!r}")
            ok += 1
            continue

        try:
            patch_content(art_id, new_content)
            print(f"[ok] id={art_id}  {title}")
            ok += 1
        except Exception as e:
            print(f"[fail] id={art_id}  {title}: {e}")
            fail += 1

    print(f"\nDone  ok={ok}  skip={skip}  fail={fail}")


if __name__ == "__main__":
    main()
