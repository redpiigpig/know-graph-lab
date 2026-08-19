#!/usr/bin/env python3
"""Validate and atomically append a Codex-vision ACCS checkpoint batch.

If the prior batch ends mid-sentence and the new batch begins with the same
comment entry, merge that continuation before appending the remaining entries.
No database write or upload is performed.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


REQUIRED_ENTRY_KEYS = {"ref", "kind", "heading", "father", "father_en", "work", "body"}
SENTENCE_END = ("。", "！", "？", "」", "』", "）", ".", "!", "?")


def record_pages(record: dict) -> list[int]:
    pages = record.get("pages")
    if isinstance(pages, list):
        return [int(page) for page in pages]
    if "page" in record:
        return [int(record["page"])]
    return []


def validate_batch(batch: dict, covered: set[int]) -> None:
    pages = record_pages(batch)
    if not pages or pages != sorted(set(pages)):
        raise ValueError(f"batch pages must be non-empty, sorted, and unique: {pages}")
    overlap = covered.intersection(pages)
    if overlap:
        raise ValueError(f"batch overlaps checkpoint pages: {sorted(overlap)}")
    if covered and pages[0] != max(covered) + 1:
        raise ValueError(f"batch must continue after page {max(covered)}; got {pages[0]}")
    entries = batch.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("batch entries must be a non-empty list")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {index} is not an object")
        missing = REQUIRED_ENTRY_KEYS.difference(entry)
        if missing:
            raise ValueError(f"entry {index} missing keys: {sorted(missing)}")
        if entry["kind"] not in {"overview", "comment"}:
            raise ValueError(f"entry {index} has invalid kind: {entry['kind']!r}")
        if not re.fullmatch(r"\d+:[0-9a-z,-]+", entry["ref"]):
            raise ValueError(f"entry {index} has invalid ref: {entry['ref']!r}")
        if not str(entry["body"]).strip():
            raise ValueError(f"entry {index} has empty body")


def can_merge(previous: dict, continuation: dict) -> bool:
    previous_body = str(previous.get("body") or "").rstrip()
    return (
        bool(previous_body)
        and not previous_body.endswith(SENTENCE_END)
        and not str(continuation.get("heading") or "").strip()
        and previous.get("kind") == continuation.get("kind") == "comment"
        and previous.get("ref") == continuation.get("ref")
        and previous.get("father") == continuation.get("father")
        and previous.get("work") == continuation.get("work")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    lines = [line for line in args.checkpoint.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]
    covered = {page for record in records for page in record_pages(record)}
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    validate_batch(batch, covered)

    entries = list(batch["entries"])
    merged = False
    if records and records[-1].get("entries") and entries:
        previous = records[-1]["entries"][-1]
        continuation = entries[0]
        if can_merge(previous, continuation):
            previous["body"] = str(previous["body"]).rstrip() + str(continuation["body"]).lstrip()
            entries.pop(0)
            merged = True

    append_record = {"pages": record_pages(batch), "entries": entries}
    if args.check_only:
        print(
            f"valid pages={append_record['pages']} entries={len(entries)} "
            f"merged_continuation={merged} covered_after={len(covered.union(append_record['pages']))}"
        )
        return 0
    records.append(append_record)

    backup = args.checkpoint.with_name(
        f"{args.checkpoint.name}.pre-codex-p{append_record['pages'][0]}-{append_record['pages'][-1]}.bak"
    )
    if backup.exists():
        raise FileExistsError(f"refusing to overwrite existing backup: {backup}")
    shutil.copy2(args.checkpoint, backup)

    temporary = args.checkpoint.with_suffix(args.checkpoint.suffix + ".codex.tmp")
    text = "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n"
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(args.checkpoint)

    check_records = [json.loads(line) for line in args.checkpoint.read_text(encoding="utf-8").splitlines()]
    check_covered = {page for record in check_records for page in record_pages(record)}
    expected = covered.union(append_record["pages"])
    if check_covered != expected:
        raise RuntimeError("checkpoint readback coverage mismatch")

    print(
        f"appended pages={append_record['pages']} entries={len(entries)} "
        f"merged_continuation={merged} covered={len(check_covered)} backup={backup}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
