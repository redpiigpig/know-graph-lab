#!/usr/bin/env python3
"""Write a deterministic SHA-256 manifest for final reader artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> dict:
    sha256 = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha256.update(block)
    return {
        "path": str(path.resolve()).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256.hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    resolved_files = [path.resolve() for path in args.files]
    if len(set(resolved_files)) != len(resolved_files):
        raise SystemExit("duplicate release artifact path")
    if output in resolved_files:
        raise SystemExit("hash manifest output cannot also be an input")
    missing = [str(path) for path in args.files if not path.is_file()]
    if missing:
        raise SystemExit(f"missing release artifacts: {', '.join(missing)}")
    payload = {
        "schemaVersion": "1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "artifacts": [digest(path) for path in resolved_files],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)
    print(output)


if __name__ == "__main__":
    main()
