#!/usr/bin/env python3
"""Match the doctoral proposal bibliography against the synced Drive library."""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import requests


EBOOK_EXTENSIONS = {".pdf", ".epub", ".mobi", ".azw", ".azw3", ".doc", ".docx"}


def normalize(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"\([^)]*(?:z-lib|zlibrary|1lib|edition|出版社|press)[^)]*\)", "", value)
    return "".join(ch for ch in value if ch.isalnum() or "\u3400" <= ch <= "\u9fff")


def score(title: str, stem: str) -> float:
    left, right = normalize(title), normalize(stem)
    if not left or not right:
        return 0.0
    if left in right:
        ratio = min(len(left), len(right)) / max(len(left), len(right))
        return 0.92 + 0.08 * ratio
    if right in left and len(right) / len(left) >= 0.75:
        return 0.82 + 0.10 * (len(right) / len(left))
    return SequenceMatcher(None, left, right).ratio()


def candidate_paths(title: str, file_records: list[tuple[Path, str]]) -> list[Path]:
    needle = normalize(title)
    if not needle:
        return []
    exact = [path for path, stem in file_records if needle in stem]
    if exact:
        return exact
    if re.search(r"[\u3400-\u9fff]", needle):
        anchors = {needle[: min(5, len(needle))], needle[-min(5, len(needle)) :]}
        return [path for path, stem in file_records if any(anchor in stem for anchor in anchors)]
    words = [word.lower() for word in re.findall(r"[A-Za-z]{4,}", title)]
    return [
        path for path, stem in file_records
        if sum(normalize(word) in stem for word in words) >= min(2, len(words))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/doctoral_thesis_references.json"))
    parser.add_argument("--drive-root", type=Path, default=Path(r"G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館"))
    parser.add_argument("--output", type=Path, default=Path("data/doctoral_thesis_reference_audit.json"))
    parser.add_argument("--threshold", type=float, default=0.76)
    parser.add_argument("--with-db", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    files = []
    for root, _dirs, names in os.walk(args.drive_root):
        files.extend(
            Path(root) / name for name in names
            if Path(name).suffix.lower() in EBOOK_EXTENSIONS
        )
    file_records = [(path, normalize(path.stem)) for path in files]
    db_rows = []
    if args.with_db:
        env = {}
        for line in Path(".env").read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
        key = env["SUPABASE_SERVICE_ROLE_KEY"]
        response = requests.get(
            f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "select": "id,title,author,file_path,parsed_at,chunk_count,parse_error,standardized_at",
                "limit": "5000",
            },
            timeout=60,
        )
        response.raise_for_status()
        db_rows = response.json()

    rows = []
    for ref in manifest["references"]:
        lookup_title = ref.get("title") or ref["citation"]
        candidates = candidate_paths(lookup_title, file_records)
        ranked = sorted(
            ((score(lookup_title, path.stem), path) for path in candidates),
            key=lambda item: item[0],
            reverse=True,
        )[:5]
        matches = [
            {"score": round(value, 4), "path": str(path)}
            for value, path in ranked if value >= args.threshold
        ]
        db_ranked = sorted(
            ((score(lookup_title, item.get("title") or ""), item) for item in db_rows),
            key=lambda item: item[0], reverse=True,
        )[:5]
        db_matches = [
            {"score": round(value, 4), **item}
            for value, item in db_ranked if value >= args.threshold
        ]
        rows.append({
            "index": ref["index"],
            "title": ref["title"],
            "citation": ref["citation"],
            "status": "drive_match" if matches else "missing",
            "matches": matches,
            "db_matches": db_matches,
            "best_candidates": [
                {"score": round(value, 4), "path": str(path)} for value, path in ranked[:3]
            ],
        })

    output = {
        "source": manifest["source"],
        "drive_root": str(args.drive_root),
        "file_count_scanned": len(files),
        "threshold": args.threshold,
        "matched_count": sum(row["status"] == "drive_match" for row in rows),
        "missing_count": sum(row["status"] == "missing" for row in rows),
        "db_matched_count": sum(bool(row["db_matches"]) for row in rows),
        "references": rows,
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("file_count_scanned", "matched_count", "missing_count")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
