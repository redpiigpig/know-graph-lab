#!/usr/bin/env python3
"""東方聖書（Sacred Books of the East）逐卷英→繁中轉錄 driver.

The 50-volume SBE is a separate corpus from Müller's own works (it lives in the
/sacred-books-east portal, store: stores/sacredBooksEast.ts), so it keeps its own
registry instead of polluting mueller_auto.WORKS. It otherwise reuses the whole
Müller pipeline: ingest_work / translate_work / assemble_and_upload / sync_previews
(now author-overridable) and the Haiku engine from mueller_haiku_pass.

Each volume is its own dict with an `author`/`author_en` of the actual translator
(Müller, Legge, Bühler, …), an archive.org `en_id` with a real `_djvu.txt`, and a
coarse split. ebook_id namespace: 555555NN-… where NN = volume number.

Usage:
  python scripts/sbe_translate.py --list
  python scripts/sbe_translate.py --ingest <slug>          # English-first, no LLM
  python scripts/sbe_translate.py --loop --only <slug>     # translate to done (resumable)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mueller_build as mb  # noqa: E402  (loads .env, glossary prompt)
import mueller_auto as ma  # noqa: E402
from mueller_haiku_pass import make_haiku_engine  # noqa: E402

# ── SBE registry — one dict per volume (vol 1 first; add the rest as sourced) ──
WORKS = [
    dict(slug="sbe-01-upanishads-1", eid="55555501-5555-4555-8555-555555555555",
         title="奧義書（上）", title_en="The Upanishads, Part I (Sacred Books of the East, Vol. 1)",
         year=1879, category="世界宗教", subcategory="東方聖書",
         author="弗里德里希‧馬克斯‧穆勒（譯）", author_en="F. Max Müller (trans.)",
         parent="東方聖書", en_id="upanishads01mluoft", de_id=None, split="coarse"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--ingest", default="", help="slug — English-first ingest, no LLM")
    ap.add_argument("--only", default="", help="comma-separated slugs to translate")
    ap.add_argument("--loop", action="store_true", help="self-restart until in scope is_done")
    args = ap.parse_args()

    by_slug = {w["slug"]: w for w in WORKS}

    if args.list:
        for w in WORKS:
            print(f"  [{'✓' if ma.is_done(w) else ' '}] {w['slug']:24s} {w['title']}  ({w['en_id']})")
        return

    if args.ingest:
        ma.ingest_work(by_slug[args.ingest])
        return

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    scope = [w for w in WORKS if not only or w["slug"] in only]
    tp = make_haiku_engine()

    def one_pass():
        for w in scope:
            if ma.is_done(w):
                print(f"  ✓ {w['slug']} done — skip", flush=True)
                continue
            print(f"▶ translate {w['slug']} — {w['title']}", flush=True)
            ma.ingest_work(w)  # idempotent; keeps English readable + cache fresh
            ma.translate_work(w, tp)
            ma.assemble_and_upload(w)

    while True:
        try:
            one_pass()
        except BaseException as e:  # noqa: BLE001  (survive engine deaths / token expiry)
            print(f"  ⚠ pass error: {type(e).__name__}: {e}", flush=True)
        if not args.loop or all(ma.is_done(w) for w in scope):
            break
    print("sbe done", flush=True)


if __name__ == "__main__":
    main()
