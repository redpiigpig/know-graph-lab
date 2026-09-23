#!/usr/bin/env python3
"""Scrub scraper leftovers out of the Latin reader's translated-reading caches.

`translate_latin_readings_zh.clean_paragraph` now keeps markdown headers, page
footers (www.internetsv.info / a lone page number), HTML entities and footnote
markers out of anything translated from here on.  This one-off applies the same
rule to what is already cached, and keeps every index-keyed layer in step:

- readings-zh.json          the Latin/Chinese segment pairs (dropped or cleaned)
- interlinear.json          reading:v2-<lesson>:<n> keys renumbered, junk tokens gone
- reading-gap-zh.json       v2:l<lesson>:<n0> keys renumbered
- exercise-set-v2.json,
  exercises-v2.json,
  lemma-corpus-church.json  answerKeyRef / ref strings L<lesson>#<n> renumbered

A `zh` of "1" was the translator's placeholder for a paragraph it never got;
it printed as a whole-sentence line reading 「1」.  It becomes blank.

    python -X utf8 scripts/repair_latin_reading_leftovers.py --dry-run
    python -X utf8 scripts/repair_latin_reading_leftovers.py
    python -X utf8 scripts/build_latin_reader_data.py --write      # 🚨 然後一定要重組主檔
    python -X utf8 scripts/build_latin_interlinear.py --group reading

🚨 `build_latin_interlinear.py` 斷詞的來源是主檔 latin-reader-two-volumes.json，
不是 readings-zh.json。2026-09-23 第一輪只修了 readings-zh 與 interlinear，沒重組
主檔，結果逐詞層重生時把垃圾 token 原封不動長了回來，成書照舊印著 (DCO) 與 &lt;。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import translate_latin_readings_zh as T

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/latin-full"
VOLUME = 2  # the church readings are the lower volume

REF = re.compile(r"\bL(\d+)#(\d+)\b")


def load(name: str):
    return json.loads((CACHE / name).read_text(encoding="utf-8"))


def save(name: str, payload) -> None:
    (CACHE / name).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


def clean_token(word: str) -> str:
    """The same scrub, token-sized: the interlinear split `&lt;oratio&gt;` as one word."""
    if word in {"#", "##", "###"} or word.startswith("www.") or word.startswith("http"):
        return ""
    return T.clean_paragraph(word) if "&" in word or "[^" in word else word


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    plan = load("church-plan.json")
    readings = load("readings-zh.json")
    interlinear = load("interlinear.json")
    gaps = load("reading-gap-zh.json")
    lesson_of = {T.reading_key(row): row["lesson"] for row in plan["readings"]}

    # lesson -> {old 1-based index: new 1-based index}; missing = dropped
    remap: dict[int, dict[int, int]] = {}
    report: list[str] = []
    for key, unit in readings["units"].items():
        lesson = lesson_of.get(key)
        if lesson is None:
            continue
        kept, mapping = [], {}
        for old, segment in enumerate(unit["segments"], start=1):
            latin = [T.clean_paragraph(p) for p in segment["latin"]]
            latin = [p for p in latin if p]
            if not latin:
                report.append(f"L{lesson} 第 {old} 段整段刪除：{' '.join(segment['latin'])[:60]!r}")
                continue
            if latin != segment["latin"]:
                report.append(f"L{lesson} 第 {old} 段清洗：{' '.join(segment['latin'])[:50]!r} → {' '.join(latin)[:50]!r}")
            zh = ["" if z.strip() == "1" else z for z in segment["zh"]]
            if zh != segment["zh"]:
                report.append(f"L{lesson} 第 {old} 段整句占位「1」改留白")
            mapping[old] = len(kept) + 1
            kept.append({**segment, "latin": latin, "zh": zh})
        if mapping != {i: i for i in range(1, len(unit["segments"]) + 1)} or any(
            k["zh"] != s["zh"] or k["latin"] != s["latin"] for k, s in zip(kept, unit["segments"])
        ):
            unit["segments"] = kept
            remap[lesson] = mapping

    # interlinear: rebuild the reading:v2-<lesson>:<n> keys for touched lessons
    units = interlinear["units"]
    for lesson, mapping in remap.items():
        prefix = f"reading:v{VOLUME}-{lesson}:"
        old_keys = {int(k[len(prefix):]): k for k in units if k.startswith(prefix)}
        rebuilt = {}
        for old, key in old_keys.items():
            new = mapping.get(old)
            entry = units.pop(key)
            if new is None:
                continue
            tokens = []
            for token in entry["tokens"]:
                # The tokenizer split entities across word and trailing
                # (`&lt;oratio&gt` + `;`), so scrub the two together.
                whole = clean_token(token["word"] + token.get("trailing", ""))
                if not whole:
                    continue
                match = re.match(r"^(.*?)([.,;:!?»)\]]*)$", whole)
                word, trailing = match.group(1), match.group(2)
                if not word:
                    continue
                tokens.append({**token, "word": word, "trailing": trailing})
            entry["tokens"] = tokens
            entry["ref"] = re.sub(r"第 \d+ 段$", f"第 {new} 段", entry.get("ref", ""))
            rebuilt[f"{prefix}{new}"] = entry
        units.update(rebuilt)
        # words in the cleaned Latin must be the words the tokens print
        for old, new in mapping.items():
            segment = next(u for k, u in readings["units"].items() if lesson_of.get(k) == lesson)["segments"][new - 1]
            want = re.findall(r"[A-Za-zÀ-ſ]+", " ".join(segment["latin"]))
            have = re.findall(r"[A-Za-zÀ-ſ]+", " ".join(t["word"] + t.get("trailing", "") for t in rebuilt.get(f"{prefix}{new}", {"tokens": []})["tokens"]))
            if want != have and f"{prefix}{new}" in rebuilt:
                extra = [w for w in want if w not in have][:5] + ["|"] + [w for w in have if w not in want][:5]
                report.append(f"🚨 L{lesson} 第 {new} 段 tokens 與原文不合（{len(want)} vs {len(have)} 詞）{extra}")

    # Footnote markers ([^[2]], [^1]) survived in the token layer of lessons whose
    # Latin was translated from an already-clean paragraph, so `remap` never
    # visited them. Scrub every reading unit's tokens, not only the renumbered.
    scrubbed = 0
    for key, entry in units.items():
        if not key.startswith("reading:"):
            continue
        before = len(entry["tokens"])
        entry["tokens"] = [t for t in entry["tokens"]
                           if not re.fullmatch(r"\[\^\[?\d+\]?\]", t["word"] + t.get("trailing", ""))]
        scrubbed += before - len(entry["tokens"])
    if scrubbed:
        report.append(f"逐詞層另外刪掉 {scrubbed} 個腳註標記 token")

    # gap fill keys are 0-based
    lines = gaps.get("lines", {})
    for lesson, mapping in remap.items():
        prefix = f"v{VOLUME}:l{lesson}:"
        old_entries = {int(k[len(prefix):]): lines.pop(k) for k in list(lines) if k.startswith(prefix)}
        for old0, entry in old_entries.items():
            new = mapping.get(old0 + 1)
            if new is not None:
                lines[f"{prefix}{new - 1}"] = entry

    # exercise answer keys and corpus refs
    def renumber(text: str) -> str:
        def swap(match):
            lesson, index = int(match.group(1)), int(match.group(2))
            mapping = remap.get(lesson)
            if not mapping:
                return match.group(0)
            new = mapping.get(index)
            if new is None:
                report.append(f"🚨 {match.group(0)} 引用了被刪除的段")
                return match.group(0)
            return f"L{lesson}#{new}"
        return REF.sub(swap, text)

    def dangling(text: str) -> bool:
        match = REF.fullmatch(text)
        if not match:
            return False
        mapping = remap.get(int(match.group(1)))
        return mapping is not None and int(match.group(2)) not in mapping

    touched_files = {}
    for name in ("exercise-set-v2.json", "exercises-v2.json"):
        payload = load(name)
        # A quoted exercise that quotes a junk paragraph (the DCO source line,
        # a "## heading") is junk too: scrub its text, and drop it outright when
        # its answer key points at a paragraph that no longer exists.
        for lesson in payload.get("lessons", []):
            for field in ("items", "anchors"):
                rows = lesson.get(field) or []
                kept_rows = []
                for row in rows:
                    key = row.get("answerKeyRef") or ""
                    if dangling(key):
                        report.append(f"{name}：刪掉引用垃圾段的題目 {row.get('uid') or row.get('no')}（{row.get('text', '')[:40]!r}）")
                        continue
                    if row.get("text"):
                        cleaned = T.clean_paragraph(row["text"])
                        if cleaned and cleaned != row["text"]:
                            report.append(f"{name}：題目文字清洗 {row['text'][:40]!r} → {cleaned[:40]!r}")
                            row["text"] = cleaned
                    kept_rows.append(row)
                if field in lesson:
                    lesson[field] = kept_rows
        raw = (CACHE / name).read_text(encoding="utf-8")
        new_raw = renumber(json.dumps(payload, ensure_ascii=False, indent=1))
        if new_raw != raw:
            touched_files[name] = new_raw
    # The sentence corpus indexed the junk paragraphs as sentences (id L26#1 is
    # the markdown header).  Drop those entries; renumber the rest.
    corpus = load("lemma-corpus-church.json")
    dropped = 0

    def keep(entry: dict) -> bool:
        nonlocal dropped
        match = REF.fullmatch(entry.get("id", ""))
        if match and remap.get(int(match.group(1))) is not None and int(match.group(2)) not in remap[int(match.group(1))]:
            dropped += 1
            return False
        return True

    def walk(node):
        if isinstance(node, list):
            kept = [walk(x) for x in node
                    if not (isinstance(x, dict) and "id" in x and not keep(x))
                    and not (isinstance(x, str) and dangling(x))]  # formIndex lists of unit ids
            return kept
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        return node

    corpus = walk(corpus)
    for unit in corpus.get("units", []):
        match = REF.fullmatch(unit.get("id", ""))
        mapping = remap.get(int(match.group(1))) if match else None
        if mapping:
            unit["block"] = mapping[int(match.group(2))]
            unit["blockCount"] = len(mapping)
        if unit.get("chinese", "").strip() == "1":
            unit["chinese"] = ""
        if "text" in unit:
            unit["text"] = T.clean_paragraph(unit["text"]) or unit["text"]
    corpus_raw = renumber(json.dumps(corpus, ensure_ascii=False, indent=1))
    touched_files["lemma-corpus-church.json"] = corpus_raw
    report.append(f"語料庫刪掉 {dropped} 條垃圾句")

    print("\n".join(report))
    print(f"\n動到 {len(remap)} 課；改 {len(touched_files)} 個引用檔：{sorted(touched_files)}")
    if args.dry_run:
        return 0
    save("readings-zh.json", readings)
    save("interlinear.json", interlinear)
    save("reading-gap-zh.json", gaps)
    for name, raw in touched_files.items():
        (CACHE / name).write_text(raw, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
