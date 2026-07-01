"""Clean OCR noise from Müller source columns (en/de) without touching the
Chinese translation. Two pure layers + a driver.

  clean_source(text, lang) — per-paragraph: strip OCR junk symbols, control/
      zero-width chars, archive/Google/Microsoft scan boilerplate, and join
      lowercase line-wrap hyphens. German („ …) quotes are preserved when
      lang == 'de' (they are real), stripped as OCR junk in English.

  is_junk_para(text) — TRUE for whole-paragraph junk: TOC dot-leaders, bare
      page/roman-numeral lines, ALL-CAPS running-head fragments. Conservative
      (high precision) — it must NOT flag real prose.

The driver drops junk paragraphs from en (+de) + zh + fail together so the
parallel lists stay aligned, and rewrites surviving en/de through clean_source.
zh text is never edited (only dropped when its en pair is junk).

Usage:
  python scripts/mueller_source_clean.py --dry-run     # report, change nothing
  python scripts/mueller_source_clean.py --apply       # rewrite sec*.json
  python scripts/mueller_source_clean.py --apply --rebuild   # + rebuild/upload
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from pathlib import Path

# OCR misreads that are effectively never real glyphs in a Latin-script
# scholarly text (footnote bullets, decorative marks, stray currency signs).
# „ (U+201E) is handled per-language: real in German, OCR junk in English.
_JUNK_SYMBOLS = "•■♦►▼▲◄●○◊¶§™€"
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f​-‏﻿­]")
# Scan boilerplate, incl. OCR-mangled variants ("tine Internet Arciiive",
# "IVIicrosoft"): the "Digitized by … Corporation/Foundation" span, and any bare
# archive.org URL token (prefix http/littp/www/./none; archive→arciiive/arcliive).
_SCAN_BOILERPLATE = re.compile(
    r"\s*Digitized by\b.{0,110}?(?:Corporation|Foundation|University\b[^.]*)", re.I)
_ARCHIVE_URL = re.compile(r"\s*\S*ar[hcli]+ive\.org/\S+", re.I)
_HYPHEN_WRAP = re.compile(r"([a-z])-\s+([a-z])")
_MULTISPACE = re.compile(r"[ \t]{2,}")


def clean_source(text: str, lang: str = "en") -> str:
    if not text:
        return text
    s = _CONTROL.sub("", text)
    s = _SCAN_BOILERPLATE.sub(" ", s)
    s = _ARCHIVE_URL.sub(" ", s)
    junk = _JUNK_SYMBOLS if lang == "de" else _JUNK_SYMBOLS + "„"
    for ch in junk:
        s = s.replace(ch, "")
    s = _HYPHEN_WRAP.sub(r"\1\2", s)
    s = _MULTISPACE.sub(" ", s)
    return s.strip()


# A table-of-contents / index entry ends a dotted leader in a PAGE NUMBER:
# "Totemism . . . . . .198". Real 19th-c prose uses ". . ." as an ellipsis but
# almost never follows it immediately with a bare page number, so requiring the
# trailing digits keeps real sentences (incl. Gifford's will, quoted verse) safe.
_TOC_LEADER = re.compile(r"\.\s*\.\s*\.[\s.]*\d")
_BARE_NUM = re.compile(r"^[IVXLCDMivxlcdm0-9][IVXLCDMivxlcdm0-9\s.,()\-–—]*$")
_RUNHEAD = re.compile(r"^[^a-z]*\b(CONTENTS|PREFACE|INDEX|APPENDIX|ERRATA)\b[^a-z]*$")


def is_junk_para(text: str) -> bool:
    """Whole-paragraph OCR junk. Conservative: real prose must survive."""
    s = (text or "").strip()
    if not s:
        return False
    if len(_TOC_LEADER.findall(s)) >= 2:      # ≥2 dotted-leader→page-number entries
        return True
    if len(s) < 30 and _BARE_NUM.match(s):    # bare page / roman-numeral line
        return True
    if len(s) < 60 and _RUNHEAD.match(s):     # ALL-CAPS running head, no prose
        return True
    return False


# ── driver ──────────────────────────────────────────────────────────────────

def _mueller_works(root: Path) -> list[str]:
    return sorted(d for d in os.listdir(root)
                  if (root / d).is_dir() and not d.startswith("sbe-"))


def clean_section(cache: dict) -> tuple[dict, int, int, list[str]]:
    """Return (new_cache, cleaned_count, dropped_count, drop_examples)."""
    en = list(cache.get("en") or [])
    de = list(cache.get("de") or [])
    zh = list(cache.get("zh") or [])
    fail = list(cache.get("fail") or [])
    has_de = bool(de)
    n = len(en)
    en = (en + [""] * n)[:n]
    zh = (zh + [None] * n)[:n]
    fail = (fail + [0] * n)[:n]
    if has_de:
        de = (de + [""] * n)[:n]

    new_en, new_de, new_zh, new_fail = [], [], [], []
    cleaned = dropped = 0
    examples: list[str] = []
    for i in range(n):
        original = en[i] or ""
        ce = clean_source(original, "en")
        # drop whole-junk or content that scan-boilerplate reduced to nothing
        if is_junk_para(ce) or (original.strip() and not ce.strip()):
            dropped += 1
            if len(examples) < 3:
                examples.append(original[:90])
            continue
        if ce != original:
            cleaned += 1
        new_en.append(ce)
        new_zh.append(zh[i])
        new_fail.append(fail[i])
        if has_de:
            new_de.append(clean_source(de[i] or "", "de"))

    out = dict(cache)
    out["en"] = new_en
    out["zh"] = new_zh
    out["fail"] = new_fail
    if has_de:
        out["de"] = new_de
    return out, cleaned, dropped, examples


def run(root: Path, apply: bool) -> dict[str, dict]:
    report: dict[str, dict] = {}
    for w in _mueller_works(root):
        wc = wd = 0
        drop_ex: list[str] = []
        for f in sorted(glob.glob(str(root / w / "sec*.json"))):
            cache = json.loads(Path(f).read_text(encoding="utf-8"))
            new_cache, cleaned, dropped, examples = clean_section(cache)
            wc += cleaned
            wd += dropped
            if examples and len(drop_ex) < 4:
                drop_ex.extend(examples[: 4 - len(drop_ex)])
            if apply and (cleaned or dropped):
                Path(f).write_text(
                    json.dumps(new_cache, ensure_ascii=False, indent=1),
                    encoding="utf-8")
        if wc or wd:
            report[w] = {"cleaned": wc, "dropped": wd, "drop_examples": drop_ex}
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="rewrite sec*.json")
    ap.add_argument("--dry-run", action="store_true", help="report only (default)")
    ap.add_argument("--rebuild", action="store_true",
                    help="with --apply: rebuild + upload changed works")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1] / \
        ".claude" / "skills" / "ebook-collected-works" / "mueller_data"
    apply = args.apply and not args.dry_run
    report = run(root, apply=apply)
    tot_c = sum(r["cleaned"] for r in report.values())
    tot_d = sum(r["dropped"] for r in report.values())
    print(f"{'APPLIED' if apply else 'DRY-RUN'}: {len(report)} works｜"
          f"cleaned={tot_c} paras｜dropped={tot_d} junk paras\n")
    for w, r in sorted(report.items(), key=lambda kv: -kv[1]["dropped"] - kv[1]["cleaned"]):
        print(f"  {w:28} cleaned={r['cleaned']:4} dropped={r['dropped']:3}")
        for ex in r["drop_examples"][:2]:
            print(f"        drop⟩ {ex!r}")

    if apply and args.rebuild:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        import mueller_build as mb  # noqa
        # rebuild hook left to the caller / follow-up; printing changed works
        print("\nchanged works to rebuild:", ", ".join(report))


if __name__ == "__main__":
    main()
