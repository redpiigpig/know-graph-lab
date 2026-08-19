#!/usr/bin/env python3
"""Lease a cloud translation lane for interactive Claude assistance."""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "scripts" / "state"
CLAIMS_PATH = STATE_DIR / "translation_lane_claims.json"
LANES = (
    "gemini-1", "gemini-2", "gemini-3",
    "nvidia-1", "nvidia-2", "nvidia-3", "nvidia-4",
    "gemini-4-reviewer",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_claims() -> dict[str, dict]:
    try:
        claims = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        claims = {}
    now = time.time()
    return {
        lane: claim for lane, claim in claims.items()
        if float(claim.get("expires_at_epoch") or 0) > now
    }


def save_claims(claims: dict[str, dict]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CLAIMS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(claims, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, CLAIMS_PATH)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["acquire", "release", "status"])
    ap.add_argument("--lane", choices=LANES)
    ap.add_argument("--owner", default="claude")
    ap.add_argument("--minutes", type=int, default=120)
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    claims = load_claims()
    if args.action == "status":
        save_claims(claims)
        print(json.dumps(claims, ensure_ascii=False, indent=2))
        return
    if not args.lane:
        ap.error("--lane is required for acquire/release")
    if args.action == "release":
        claims.pop(args.lane, None)
        save_claims(claims)
        print(f"released={args.lane}")
        return
    expires = time.time() + max(5, args.minutes) * 60
    claims[args.lane] = {
        "owner": args.owner,
        "note": args.note,
        "created_at": now_iso(),
        "expires_at": datetime.fromtimestamp(
            expires, timezone.utc).astimezone().isoformat(timespec="seconds"),
        "expires_at_epoch": expires,
    }
    save_claims(claims)
    print(json.dumps({args.lane: claims[args.lane]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
