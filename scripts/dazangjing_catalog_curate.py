#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Curation aid for the Dazangjing source catalog.

Reads the classifier ledger (classified-records.jsonl), keeps the latest row per
record, and for every keep_primary_work candidate:
  - normalizes title_orig + title_zh,
  - flags candidates that already exist in the Dazangjing corpus (data/dazangjing/*.ts),
  - groups intra-candidate duplicates (same work, many editions/translations).

This NEVER inserts anything. It produces a human worklist so the curator can
decide what to add. Dedup is intentionally fuzzy and over-reports matches; the
human confirms.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dazangjing"
LEDGER = DATA / "source-catalog" / "classified-records.jsonl"
TS_FILES = [DATA / "index.ts", DATA / "ancient.ts", DATA / "medieval.ts",
            DATA / "early-modern.ts", DATA / "modern.ts"]

# TS string fields may contain escaped quotes (l\'Église); match them safely.
ZH_RE = re.compile(r"title_zh:\s*'((?:[^'\\]|\\.)*)'")
ORIG_RE = re.compile(r"title_orig:\s*'((?:[^'\\]|\\.)*)'")

# Edition/translation/series noise stripped before comparing original titles.
NOISE = re.compile(
    r"\b(translated|translation|edited|edition|introduction|introd|notes?|"
    r"vol|volume|tome|band|books?|liber|libri|with|together|essays?|select|"
    r"works|opera|opere|fragments?|critical|study|english|latin|greek|syriac|"
    r"version|texte|text|par|by|and|the|de|la|le|du|des|von|une?)\b",
    re.I,
)


def unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def norm(s: str) -> str:
    """Aggressive normalization for fuzzy matching of original-language titles."""
    if not s:
        return ""
    s = unescape(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # strip diacritics
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)  # drop punctuation (keeps latin-script core)
    s = NOISE.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_zh(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"[《》「」〈〉，。、：；！？\s（）()]", "", unescape(s))


def corpus_index() -> tuple[set[str], set[str], dict[str, str]]:
    """Return (normalized title_orig set, normalized title_zh set, zh->raw map)."""
    orig: set[str] = set()
    zh: set[str] = set()
    zh_raw: dict[str, str] = {}
    for f in TS_FILES:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for m in ORIG_RE.findall(text):
            n = norm(m)
            if n:
                orig.add(n)
        for m in ZH_RE.findall(text):
            n = norm_zh(m)
            if n:
                zh.add(n)
                zh_raw[n] = unescape(m)
    return orig, zh, zh_raw


def load_keep(ledger: Path) -> list[dict]:
    """Latest row per record_key, decision=keep_primary_work."""
    latest: dict[str, dict] = {}
    for line in ledger.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        k = r.get("record_key")
        if k:
            latest[k] = r
    keep = []
    for r in latest.values():
        c = r.get("classification", {})
        if c.get("decision") == "keep_primary_work":
            keep.append(r)
    return keep


def prefix_hit(cand: str, corpus: set[str]) -> str:
    """Fuzzy corpus match: exact, or one is a prefix of the other (>=6 chars)."""
    if not cand:
        return ""
    if cand in corpus:
        return cand
    for c in corpus:
        if len(cand) >= 6 and len(c) >= 6 and (cand.startswith(c) or c.startswith(cand)):
            return c
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--out", default=str(DATA / "source-catalog" / "curation-worklist.json"))
    args = ap.parse_args()

    keep = load_keep(Path(args.ledger))
    c_orig, c_zh, _ = corpus_index()

    groups: dict[str, list[dict]] = defaultdict(list)
    for r in keep:
        c = r["classification"]
        key = norm(c.get("title_orig", "")) or norm_zh(c.get("title_zh", "")) or r["record_key"]
        groups[key].append(r)

    in_corpus = []
    new_groups = []
    for key, rows in sorted(groups.items()):
        c0 = rows[0]["classification"]
        no = norm(c0.get("title_orig", ""))
        nz = norm_zh(c0.get("title_zh", ""))
        hit = prefix_hit(no, c_orig) or (nz if nz in c_zh else "")
        entry = {"key": key, "n_editions": len(rows), "rows": rows, "corpus_hit": hit}
        (in_corpus if hit else new_groups).append(entry)

    print(f"keep_primary candidates: {len(keep)}  ->  unique works: {len(groups)}")
    print(f"  already in corpus (skip): {len(in_corpus)}")
    print(f"  NEW unique works to curate: {len(new_groups)}")
    print()
    print("=== NEW unique works (candidate for insertion, human-curate) ===")
    for e in new_groups:
        c = e["rows"][0]["classification"]
        eras = sorted({row["classification"].get("eraKey") for row in e["rows"]})
        colls = sorted({row["classification"].get("collectionKey") for row in e["rows"]})
        canons = sorted({row["classification"].get("canon") for row in e["rows"]})
        print(f"[{','.join(eras)} | {','.join(colls)} | {','.join(canons)}] "
              f"{c.get('title_zh')}  <-  {str(c.get('title_orig'))[:55]}  "
              f"(x{e['n_editions']}, {c.get('author','')[:24]})")
    print()
    print("=== already-in-corpus (skipped) ===")
    for e in in_corpus:
        c = e["rows"][0]["classification"]
        print(f"  {c.get('title_zh')}  <-  {str(c.get('title_orig'))[:45]}  ~= corpus[{e['corpus_hit'][:30]}]")

    out = Path(args.out)
    out.write_text(json.dumps(
        {"new_works": [{"era_keys": sorted({r["classification"].get("eraKey") for r in e["rows"]}),
                        "collection_keys": sorted({r["classification"].get("collectionKey") for r in e["rows"]}),
                        "canons": sorted({r["classification"].get("canon") for r in e["rows"]}),
                        "n_editions": e["n_editions"],
                        "title_zh": e["rows"][0]["classification"].get("title_zh"),
                        "title_orig": e["rows"][0]["classification"].get("title_orig"),
                        "author": e["rows"][0]["classification"].get("author"),
                        "reason_zh": e["rows"][0]["classification"].get("reason_zh"),
                        "sources": [r.get("source_record", {}).get("source") for r in e["rows"]]}
                       for e in new_groups],
         "in_corpus_count": len(in_corpus)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nworklist -> {out}")


if __name__ == "__main__":
    main()
