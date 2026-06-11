#!/usr/bin/env python3
"""One-off parallel translation pass for the Müller auto-queue, using Claude
Haiku instead of the NVIDIA chain.

Why this exists: the scheduled `mueller_auto.py --run-queue` (PID held the lock)
was running OLD code that livelocked on `origin-growth` (is_done never fired
because ~1 unfillable OCR/marginalia segment per section kept it under 100%),
starving the other 12 books. We must not stop that process (not started this
session). So this driver runs the FIXED translate_work/is_done (fail-skip) over
the starved books on a SEPARATE engine (Haiku → no NVIDIA contention with the
stuck run or /coach), skipping `origin-growth` to avoid writing the same
section caches concurrently.

Usage:
  python scripts/mueller_haiku_pass.py --probe        # 1-paragraph engine smoke
  python scripts/mueller_haiku_pass.py                # translate all starved books
"""
import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mueller_build as mb            # loads .env on import, defines MUELLER_PROMPT_TMPL
import translate_ebook_to_zh as te
import mueller_auto as ma

SKIP_SLUGS = {"origin-growth-religion"}  # left to the running (old-code) process


def _clean(out: str) -> str:
    out = re.sub(r"(?m)^\s*#{1,6}\s.*$", "", out)
    return re.sub(r"\s*\n\s*", " ", out).strip()


def make_haiku_engine():
    te.PROMPT_TMPL = mb.MUELLER_PROMPT_TMPL  # Müller comparative-religion glossary prompt

    def translate_para(en: str, de: str = "") -> str:
        src = en.strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)
        out = ""
        for _ in range(4):  # retry-on-empty: don't cache a heading-only/blank reply
            out = _clean(" ".join(te.haiku_translate(p) for p in pieces))
            if out:
                return out
        return out

    return translate_para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="translate one paragraph and exit")
    ap.add_argument("--engine", choices=["haiku", "nvidia"], default="haiku",
                    help="haiku = Claude Haiku (this driver); nvidia = mueller_build NVIDIA chain")
    ap.add_argument("--only", default="", help="comma-separated slugs to restrict to "
                    "(disjoint sets let two engines run in parallel without collision)")
    ap.add_argument("--loop", action="store_true", help="self-restart until every "
                    "--only book is_done (survives engine deaths / token expiry)")
    args = ap.parse_args()

    tp = make_haiku_engine() if args.engine == "haiku" else mb.make_engine()
    tag = args.engine.capitalize()
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    if args.probe:
        sample = ("Religion, in the highest sense of the word, is that which "
                  "enables man to apprehend the Infinite under different names "
                  "and varying disguises.")
        print("EN:", sample)
        print("ZH:", tp(sample))
        return

    def in_scope(w):
        return w["slug"] not in SKIP_SLUGS and (not only or w["slug"] in only)

    def all_done():
        return all(ma.is_done(w) for w in ma.WORKS if in_scope(w))

    def one_pass():
        for w in ma.WORKS:
            if not in_scope(w):
                continue
            if ma.is_done(w):
                print(f"  ✓ {w['slug']} done — skip", flush=True)
                continue
            if not ma.sec_path(w["slug"], 0).exists():
                print(f"  ⤓ ingest {w['slug']}", flush=True)
                ma.ingest_work(w)
            print(f"▶ {tag}-translate {w['slug']} — {w['title']}", flush=True)
            try:
                ma.translate_work(w, tp)
                ma.assemble_and_upload(w)
                print(f"  ✓ {w['slug']} complete", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  ✗ {w['slug']} failed: {type(e).__name__}: {e}", flush=True)

    if not args.loop:
        one_pass()
        print(f"{tag} pass complete", flush=True)
        return

    # --loop: keep retrying whole set until done; an engine death / token expiry
    # that escapes the per-book guard just restarts the pass instead of stalling.
    attempt = 0
    while not all_done():
        attempt += 1
        print(f"=== {tag} loop attempt {attempt} ===", flush=True)
        try:
            one_pass()
        except BaseException as e:  # noqa: BLE001  — even SystemExit shouldn't stall the loop
            print(f"  ‼ {tag} pass crashed: {type(e).__name__}: {e} — retry in 60s", flush=True)
        if all_done():
            break
        time.sleep(60)
    print(f"{tag} loop complete — all books done", flush=True)


if __name__ == "__main__":
    main()
