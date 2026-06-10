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
    args = ap.parse_args()

    tp = make_haiku_engine()

    if args.probe:
        sample = ("Religion, in the highest sense of the word, is that which "
                  "enables man to apprehend the Infinite under different names "
                  "and varying disguises.")
        print("EN:", sample)
        print("ZH:", tp(sample))
        return

    for w in ma.WORKS:
        if w["slug"] in SKIP_SLUGS:
            print(f"  ⏭ skip {w['slug']} (left to running process)", flush=True)
            continue
        if ma.is_done(w):
            print(f"  ✓ {w['slug']} done — skip", flush=True)
            continue
        if not ma.sec_path(w["slug"], 0).exists():
            print(f"  ⤓ ingest {w['slug']}", flush=True)
            ma.ingest_work(w)
        print(f"▶ Haiku-translate {w['slug']} — {w['title']}", flush=True)
        try:
            ma.translate_work(w, tp)
            ma.assemble_and_upload(w)
            print(f"  ✓ {w['slug']} complete", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {w['slug']} failed: {type(e).__name__}: {e}", flush=True)
    print("haiku pass complete", flush=True)


if __name__ == "__main__":
    main()
