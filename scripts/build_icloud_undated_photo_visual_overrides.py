#!/usr/bin/env python3
"""Build the completed SHA-level visual/date override report for undated iCloud photos.

This script only reads the review inventory and writes a JSON review artifact.  It
does not move, rename, import, or delete any media.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = REPO_ROOT / "scripts/logs/icloud_undated_photo_visual_review_inventory_20260804.json"
DEFAULT_PRIOR_VISUAL = REPO_ROOT / "scripts/logs/icloud_visual_classification_20260804.json"
DEFAULT_OUTPUT = REPO_ROOT / "scripts/logs/icloud_undated_photo_visual_overrides_20260804.json"
TZ_TAIPEI = dt.timezone(dt.timedelta(hours=8))


DOWNLOAD_REASONS = {
    "UP049": "Greeting-card illustration rather than a camera photograph.",
    "UP102": "Artwork/painting reproduction rather than a real-world camera capture.",
    "UP116": "Anime illustration rather than photographic content.",
    "UP117": "Anime illustration rather than photographic content.",
    "UP120": "CG/illustrated explicit image rather than photographic content.",
    "UP121": "CG/illustrated explicit image rather than photographic content.",
    "UP122": "CG/illustrated explicit image rather than photographic content.",
    "UP123": "CG/illustrated explicit image rather than photographic content.",
    "UP124": "CG/illustrated explicit image rather than photographic content.",
    "UP125": "CG/illustrated explicit image rather than photographic content.",
    "UP126": "CG/illustrated explicit image rather than photographic content.",
    "UP143": "Magazine/poster graphic layout rather than a camera photograph.",
    "UP193": "Monthly calendar graphic rather than a camera photograph.",
    "UP226": "Small Honor Guard logo graphic rather than photographic content.",
    "UP293": "Synthetic/AI cadet poster rather than a real camera capture.",
    "UP298": "Movie poster rather than a camera photograph.",
    "UP326": "YouTube-style thumbnail graphic rather than a camera photograph.",
    "UP345": "SpongeBob cartoon still with subtitle; non-photographic content.",
    "UP347": "Text/educational meme graphic rather than a camera photograph.",
    "UP362": "Taiwan map graphic rather than photographic content.",
    "UP370": "Synthetic/AI military-themed render rather than a real camera capture.",
    "UP374": "Illustrated mathematics meme rather than photographic content.",
    "UP382": "Ordination event poster graphic rather than a camera photograph.",
    "UP387": "Manga/anime illustration rather than photographic content.",
    "UP396": "Typeset code quotation graphic rather than a camera photograph.",
    "UP397": "SpongeBob cartoon/meme frame rather than photographic content.",
}


SCREENSHOT_REASONS = {
    "UP072": "Visible social-media post interface.",
    "UP182": "Visible Copy/Share context-menu interface over the collage.",
    "UP207": "Visible Instagram story/camera interface.",
    "UP214": "Visible Instagram Reels interface.",
    "UP318": "Visible IDE/Git Graph interface.",
    "UP332": "Article/web-page text interface capture.",
    "UP359": "Visible phone Notes/app interface.",
    "UP373": "Visible iPhone camera application controls and mode interface.",
    "UP395": "Visible X social-media post interface and controls.",
    "UP399": "Visible Android connection/settings interface.",
    "UP400": "Visible Android SIM manager/settings interface.",
    "UP401": "Visible Android SIM settings interface.",
}


DATE_RECOVERY = {
    "UP363": {
        "captured_at": "2017-06-27T21:54:20+08:00",
        "source": "filename_ymdhms_prefix",
        "source_text": "20170627215420",
        "pattern": "first 14 filename digits parsed as YYYYMMDDhhmmss",
        "timezone_policy": "filename timestamp interpreted as Asia/Taipei local time",
        "target_relative_parent": "2017相片/2017.06",
        "reliable": True,
        "zip_packaging_mtime_used": False,
        "precedence_note": "Use only when no more authoritative embedded capture timestamp is available.",
    }
}


REJECTED_ON_IMAGE_DATES = [
    {
        "review_id": "UP193",
        "observation": "Calendar graphic contains calendar date information.",
        "decision": "not_a_capture_date",
        "reason": "The date belongs to the graphic's content and does not establish when the file was captured or downloaded.",
    },
    {
        "review_id": "UP382",
        "observation": "Event poster visibly states 23 May 2026.",
        "decision": "not_a_capture_date",
        "reason": "This is the advertised event date, not a camera timestamp or file capture date.",
    },
    {
        "review_id": "UP395",
        "observation": "X post interface visibly states 2026/4/5.",
        "decision": "not_a_capture_date",
        "reason": "This is the post timestamp and does not establish when the screenshot file itself was captured.",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def evidence_for(record: dict[str, Any]) -> dict[str, Any]:
    if record["prior_visual_review"]:
        return {
            **record["prior_visual_review"].get("evidence", {}),
            "reused_from_prior_visual_report": True,
        }
    return {
        "contact_sheet_path": record["contact_sheet"],
        "manual_visual_review": True,
    }


def classify(record: dict[str, Any]) -> tuple[str, str, str]:
    review_id = record["review_id"]
    prior = record["prior_visual_review"]
    if prior:
        return prior["classification"], prior["confidence"], prior["reason"]
    if review_id in DOWNLOAD_REASONS:
        return "download", "high", DOWNLOAD_REASONS[review_id]
    if review_id in SCREENSHOT_REASONS:
        return "screenshot", "high", SCREENSHOT_REASONS[review_id]
    return (
        "photo",
        "high",
        "Real-world photographic content; editing, cropping, watermarking, or internet origin does not change it into UI or a non-photographic graphic.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--prior-visual", type=Path, default=DEFAULT_PRIOR_VISUAL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    inventory = read_json(args.inventory)
    prior_visual = read_json(args.prior_visual)
    records = inventory["records"]
    by_review_id = {record["review_id"]: record for record in records}
    if len(by_review_id) != len(records):
        raise ValueError("Inventory contains duplicate review IDs")

    expected_exception_ids = set(DOWNLOAD_REASONS) | set(SCREENSHOT_REASONS) | set(DATE_RECOVERY)
    missing_exception_ids = sorted(expected_exception_ids - set(by_review_id))
    if missing_exception_ids:
        raise ValueError(f"Review decisions reference missing inventory IDs: {missing_exception_ids}")

    overrides: list[dict[str, Any]] = []
    for record in records:
        classification, confidence, reason = classify(record)
        overrides.append(
            {
                "review_id": record["review_id"],
                "sha256": record["sha256"],
                "batch_id": record["batch_id"],
                "batch_order": record["batch_order"],
                "source_path": record["source_path"],
                "source_name": record["source_name"],
                "source_ext": record["source_ext"],
                "prior_classification": "photo",
                "classification": classification,
                "confidence": confidence,
                "reason": reason,
                "evidence": evidence_for(record),
                "reused_prior_visual": bool(record["prior_visual_review"]),
            }
        )

    date_recovery_candidates = []
    for review_id, recovery in DATE_RECOVERY.items():
        record = by_review_id[review_id]
        date_recovery_candidates.append(
            {
                "review_id": review_id,
                "sha256": record["sha256"],
                "source_name": record["source_name"],
                **recovery,
            }
        )

    classifications = Counter(item["classification"] for item in overrides)
    confidences = Counter(item["confidence"] for item in overrides)
    reused_count = sum(item["reused_prior_visual"] for item in overrides)
    new_count = len(overrides) - reused_count
    inventory_shas = {record["sha256"] for record in records}
    output_shas = {item["sha256"] for item in overrides}
    contact_sheet_paths = {
        Path(record["contact_sheet"])
        for record in records
        if record["needs_new_review"]
    }
    validation_errors = []
    checks = {
        "inventory_record_count_is_403": len(records) == 403,
        "override_record_count_is_403": len(overrides) == 403,
        "unique_review_id_count_is_403": len({item["review_id"] for item in overrides}) == 403,
        "unique_sha256_count_is_403": len(output_shas) == 403,
        "exact_sha_set_matches_inventory": output_shas == inventory_shas,
        "reused_prior_visual_count_is_20": reused_count == 20,
        "new_visual_review_count_is_383": new_count == 383,
        "unknown_count_is_zero": classifications.get("unknown", 0) == 0,
        "all_classifications_valid": set(classifications) <= {"photo", "screenshot", "download"},
        "all_24_contact_sheets_exist": len(contact_sheet_paths) == 24 and all(path.is_file() for path in contact_sheet_paths),
        "all_source_files_exist": all(Path(item["source_path"]).is_file() for item in overrides),
        "filename_date_recovery_count_is_one": len(date_recovery_candidates) == 1,
        "filename_date_recovery_avoids_zip_mtime": all(
            not item["zip_packaging_mtime_used"] for item in date_recovery_candidates
        ),
    }
    for name, ok in checks.items():
        if not ok:
            validation_errors.append(name)
    if validation_errors:
        raise RuntimeError("Visual override validation failed: " + ", ".join(validation_errors))

    output = {
        "schema_version": "1.0",
        "generated_at": dt.datetime.now(TZ_TAIPEI).isoformat(timespec="seconds"),
        "review_status": "complete",
        "mode": "manual_visual_review_and_date_override_report",
        "mutation_performed": False,
        "source_inventory": str(args.inventory.resolve()),
        "prior_visual_report": str(args.prior_visual.resolve()),
        "prior_visual_report_generated_at": prior_visual.get("generated_at"),
        "contact_sheet_directory": inventory["contact_sheet_root"],
        "classification_policy": {
            "photo": "Real people, scenery, objects, or other camera-captured photographic/video content, including downloaded photographs.",
            "screenshot": "Visible application, website, social-media, device-settings, or other user interface capture.",
            "download": "Poster, illustration, generated image, map, logo, meme, or other non-photographic internet graphic.",
        },
        "date_policy": {
            "require_complete_calendar_date": True,
            "event_or_post_content_date_is_capture_date": False,
            "zip_packaging_mtime_may_be_capture_time": False,
            "more_authoritative_embedded_capture_time_takes_precedence": True,
        },
        "summary": {
            "total": len(overrides),
            "reused_prior_visual": reused_count,
            "new_visual_review": new_count,
            "classification": dict(sorted(classifications.items())),
            "confidence": dict(sorted(confidences.items())),
            "unknown": classifications.get("unknown", 0),
            "date_recovery_candidates": len(date_recovery_candidates),
            "eligible_on_image_date_overrides": 0,
            "rejected_on_image_content_dates": len(REJECTED_ON_IMAGE_DATES),
        },
        "date_recovery_candidates": date_recovery_candidates,
        "on_image_date_review": {
            "status": "complete",
            "eligible_capture_timestamp_overrides": [],
            "rejected_content_dates": REJECTED_ON_IMAGE_DATES,
            "note": "No image showed a complete, clearly readable camera date watermark that could safely override capture time.",
        },
        "overrides": overrides,
        "validation": {
            "ok": True,
            "errors": [],
            **checks,
        },
    }
    write_json_atomic(args.output, output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "summary": output["summary"],
                "validation": output["validation"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
