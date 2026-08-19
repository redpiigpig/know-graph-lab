#!/usr/bin/env python3
"""Build a read-only, repeatable import plan for the audited iCloud batches.

This script never copies, converts, moves, renames, deletes, or overwrites
media, and it never creates a Drive folder.  It reads the exact-duplicate
audit, the visual-classification report, the existing Chenwei folder tree,
and an optional perceptual-duplicate SHA exclusion list.  Its only writes are
the local JSON planning report and local JSON planned-operation manifest.

Important policies encoded here:

* ZIP/extraction/packaging mtimes are never capture dates.
* A reliable captured_at is normalized to Asia/Taipei for routing/naming.
* Undated real photographic media goes only to the existing 2026未分類.
* Undated screenshots/download graphics go to existing 2026截圖/2026下載;
  their D/S filename date is the planned import date, never a capture date.
* Only already-existing Drive target parents may receive planned operations.
* Live Photo still+MOV pairs stay together and share one YYYY-MM-DD(n) stem.
* HEIC containers mislabeled as .JPG are marked for JPEG conversion; the
  conversion itself is deliberately outside this planning script.
* Perceptual exclusions are an explicit input and never silently inferred.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = REPO_ROOT / "scripts/logs/icloud_batch1_batch2_exact_dedup_audit_20260804.json"
DEFAULT_VISUAL = REPO_ROOT / "scripts/logs/icloud_visual_classification_20260804.json"
DEFAULT_UNDATED_PHOTO_VISUAL = REPO_ROOT / "scripts/logs/icloud_undated_photo_visual_overrides_20260804.json"
DEFAULT_EXCLUDE = REPO_ROOT / "scripts/logs/icloud_exclude_perceptual_sha_pending.txt"
DEFAULT_REPORT = REPO_ROOT / "scripts/logs/icloud_import_plan_20260804.json"
DEFAULT_MANIFEST = REPO_ROOT / "scripts/logs/icloud_import_planned_manifest_20260804.json"

TZ_TAIPEI = dt.timezone(dt.timedelta(hours=8))
VALID_CATEGORIES = {"photo", "screenshot", "download"}
VIDEO_EXTS = {".mov", ".mp4", ".m4v", ".webm", ".mkv"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATED_STEM_RE = re.compile(r"^(?:S|D)?\d{4}-\d{2}-\d{2}\(\d+\)$", re.IGNORECASE)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def load_exclude_sha(path: Path) -> set[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Perceptual exclusion input does not exist: {path}")
    text = path.read_text(encoding="utf-8-sig")
    stripped = text.lstrip()
    values: Iterable[Any]
    if stripped.startswith("[") or stripped.startswith("{"):
        payload = json.loads(text)
        if isinstance(payload, dict):
            values = payload.get("exclude_perceptual_sha", [])
        elif isinstance(payload, list):
            values = payload
        else:
            raise ValueError("Perceptual exclusion JSON must be an array or object")
    else:
        values = (
            line.split("#", 1)[0].strip()
            for line in text.splitlines()
        )
    result: set[str] = set()
    for raw in values:
        value = str(raw).strip().casefold()
        if not value:
            continue
        if not SHA256_RE.fullmatch(value):
            raise ValueError(f"Invalid SHA-256 in {path}: {raw!r}")
        result.add(value)
    return result


def parse_capture(value: str | None) -> dict[str, Any]:
    if not value:
        return {
            "reliable": False,
            "raw": None,
            "normalized_local_datetime": None,
            "local_date": None,
            "local_year": None,
            "local_month": None,
            "timezone_policy": "missing; no date inferred",
        }
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid captured_at {value!r}") from exc
    if parsed.tzinfo is None:
        local = parsed.replace(tzinfo=TZ_TAIPEI)
        policy = "naive EXIF/filename time interpreted as Asia/Taipei local time"
    else:
        local = parsed.astimezone(TZ_TAIPEI)
        policy = "timezone-aware captured_at converted to Asia/Taipei"
    return {
        "reliable": True,
        "raw": value,
        "normalized_local_datetime": local.isoformat(timespec="seconds"),
        "local_date": local.date().isoformat(),
        "local_year": f"{local.year:04d}",
        "local_month": f"{local.month:02d}",
        "timezone_policy": policy,
    }


def destination_mtime_policy(capture: dict[str, Any], capture_source: str | None) -> dict[str, Any]:
    if capture["reliable"]:
        return {
            "mode": "set_from_reliable_captured_at",
            "planned_value": capture["normalized_local_datetime"],
            "is_capture_time": True,
            "capture_source": capture_source,
            "note": "A future importer may set destination mtime to this capture time.",
            "forbidden_inputs": ["ZIP packaging mtime", "archive entry mtime", "extraction mtime"],
        }
    return {
        "mode": "set_at_execution_from_import_download_time",
        "planned_value": None,
        "is_capture_time": False,
        "capture_source": None,
        "note": "No reliable capture date exists. A future importer may record only its actual import/download time, explicitly as non-capture time.",
        "forbidden_inputs": ["ZIP packaging mtime", "archive entry mtime", "extraction mtime"],
    }


def target_relative_parent(category: str, capture: dict[str, Any]) -> tuple[str | None, str]:
    if category == "photo":
        if capture["reliable"]:
            year, month = capture["local_year"], capture["local_month"]
            return f"{year}相片/{year}.{month}", "reliable capture year/month"
        return "2026相片/2026未分類", "undated real photographic media policy"
    if not capture["reliable"]:
        suffix = "截圖" if category == "screenshot" else "下載"
        return f"2026相片/2026{suffix}", f"undated {category}; route by import/download year, never as capture year"
    year = capture["local_year"]
    suffix = "截圖" if category == "screenshot" else "下載"
    return f"{year}相片/{year}{suffix}", "reliable capture year and visual category"


def windows_target(root: Path, relative: str) -> Path:
    return root / Path(*PurePosixPath(relative).parts)


def source_role(record: dict[str, Any]) -> str:
    metadata = record.get("metadata") or {}
    if metadata.get("detected_type") == "video" or record.get("ext", "").casefold() in VIDEO_EXTS:
        return "video"
    return "still"


def build_live_photo_groups(
    audit: dict[str, Any],
    keep_by_sha: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    raw_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in audit["source_records"]:
        if record.get("live_photo_pair"):
            key = (record["batch_id"], Path(record["name"]).stem.casefold())
            raw_groups[key].append(record)

    collapsed: dict[tuple[str, ...], dict[str, Any]] = {}
    for (batch_id, stem), members in sorted(raw_groups.items()):
        shas = tuple(sorted({member["sha256"] for member in members}))
        if shas not in collapsed:
            collapsed[shas] = {
                "signature": shas,
                "source_basenames": set(),
                "source_groups": [],
                "records": [],
            }
        group = collapsed[shas]
        group["source_basenames"].add(stem)
        group["source_groups"].append({"batch_id": batch_id, "basename": stem})
        group["records"].extend(members)

    groups: list[dict[str, Any]] = []
    by_sha: dict[str, dict[str, Any]] = {}
    for signature, raw in sorted(collapsed.items()):
        keep_shas = [sha for sha in signature if sha in keep_by_sha]
        roles: dict[str, str] = {}
        for sha in signature:
            role_records = [record for record in raw["records"] if record["sha256"] == sha]
            roles[sha] = "video" if any(source_role(record) == "video" for record in role_records) else "still"
        pair_hash = hashlib.sha256("|".join(signature).encode("ascii")).hexdigest()[:12]
        group = {
            "pair_id": f"LP-{pair_hash}",
            "signature": list(signature),
            "keep_shas": keep_shas,
            "roles": roles,
            "source_basenames": sorted(raw["source_basenames"]),
            "source_groups": sorted(raw["source_groups"], key=lambda item: (item["batch_id"], item["basename"])),
        }
        groups.append(group)
        for sha in keep_shas:
            if sha in by_sha and by_sha[sha]["pair_id"] != group["pair_id"]:
                raise ValueError(f"SHA belongs to multiple Live Photo groups: {sha}")
            by_sha[sha] = group
    return groups, by_sha


def classification_overrides(
    visual: dict[str, Any],
    undated_photo_visual: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    overrides: dict[str, dict[str, Any]] = {}
    for item in visual.get("items", []):
        overrides[item["sha256"]] = {
            "category": item["classification"],
            "method": "full_visual_review",
            "review_id": item["review_id"],
            "confidence": item["confidence"],
            "reason": item["reason"],
        }
    validation = visual.get("explicit_screenshot_validation") or {}
    for item in validation.get("records", []):
        sha = item["sha256"]
        if sha in overrides:
            continue
        overrides[sha] = {
            "category": item["observed_classification"],
            "method": "explicit_screenshot_visual_validation",
            "review_id": item["sample_id"],
            "confidence": item["confidence"],
            "reason": item["reason"],
        }
    for item in undated_photo_visual.get("overrides", []):
        overrides[item["sha256"]] = {
            "category": item["classification"],
            "method": "completed_undated_full_visual_review",
            "review_id": item["review_id"],
            "confidence": item["confidence"],
            "reason": item["reason"],
        }
    return overrides


def capture_date_overrides(undated_photo_visual: dict[str, Any]) -> dict[str, dict[str, Any]]:
    overrides: dict[str, dict[str, Any]] = {}
    for item in undated_photo_visual.get("date_recovery_candidates", []):
        if not item.get("reliable"):
            continue
        sha = item["sha256"].casefold()
        if sha in overrides:
            raise ValueError(f"Duplicate capture-date override SHA: {sha}")
        if item.get("zip_packaging_mtime_used"):
            raise ValueError(f"ZIP/archive mtime is forbidden as capture evidence: {item['source_name']}")
        overrides[sha] = item
    return overrides


def classification_for(candidate: dict[str, Any], overrides: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = candidate["classification"]
    override = overrides.get(candidate["sha256"])
    if override:
        final = override["category"]
        provenance = {
            "method": override["method"],
            "report_item_id": override["review_id"],
            "confidence": override["confidence"],
            "reason": override["reason"],
        }
    else:
        final = source["recommended_category"]
        provenance = {
            "method": "audit_metadata_heuristic",
            "report_item_id": None,
            "confidence": source["classification_confidence"],
            "reason": source["classification_reason"],
        }
    if final not in VALID_CATEGORIES:
        raise ValueError(f"Unresolved classification {final!r}: {candidate['name']}")
    return {
        "source_category": source["recommended_category"],
        "final_category": final,
        "changed": final != source["recommended_category"],
        "provenance": provenance,
    }


def collision_state(folder: Path) -> dict[str, set[str]]:
    names: set[str] = set()
    stems: set[str] = set()
    for child in folder.iterdir():
        if child.is_file():
            names.add(child.name.casefold())
            stems.add(child.stem.casefold())
    return {"names": names, "stems": stems}


def allocate_dated_stem(state: dict[str, set[str]], prefix: str, local_date: str) -> str:
    index = 1
    while True:
        stem = f"{prefix}{local_date}({index})"
        if stem.casefold() not in state["stems"]:
            state["stems"].add(stem.casefold())
            return stem
        index += 1


def allocate_undated_stem(state: dict[str, set[str]], desired: str, group_sha: str) -> str:
    desired = desired.strip() or "icloud_undated"
    if desired.casefold() not in state["stems"]:
        state["stems"].add(desired.casefold())
        return desired
    for length in (12, 16, 24, 64):
        stem = f"{desired}__icloud_{group_sha[:length]}"
        if stem.casefold() not in state["stems"]:
            state["stems"].add(stem.casefold())
            return stem
    raise RuntimeError(f"Could not allocate undated stem: {desired}")


def planned_extension(record: dict[str, Any]) -> str:
    if record["conversion"]["required"]:
        return ".jpg"
    extension = Path(record["source"]["name"]).suffix.casefold()
    if not extension:
        raise ValueError(f"Source has no extension: {record['source']['name']}")
    return extension


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--visual", type=Path, default=DEFAULT_VISUAL)
    parser.add_argument("--undated-photo-visual", type=Path, default=DEFAULT_UNDATED_PHOTO_VISUAL)
    parser.add_argument("--library-root", type=Path)
    parser.add_argument("--exclude-perceptual-sha", type=Path, default=DEFAULT_EXCLUDE)
    parser.add_argument("--perceptual-review-status", choices=("pending", "complete"), default="pending")
    parser.add_argument(
        "--planned-import-date",
        default=dt.datetime.now(TZ_TAIPEI).date().isoformat(),
        help="YYYY-MM-DD used only for undated screenshot/download D/S names; it is never a capture date",
    )
    parser.add_argument("--output-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output-manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    try:
        planned_import_date = dt.date.fromisoformat(args.planned_import_date).isoformat()
    except ValueError as exc:
        raise ValueError(f"Invalid --planned-import-date: {args.planned_import_date!r}") from exc

    audit = read_json(args.audit)
    visual = read_json(args.visual)
    undated_photo_visual = read_json(args.undated_photo_visual)
    library_root = args.library_root or Path(audit["library_snapshot"]["root"])
    exclude_sha = load_exclude_sha(args.exclude_perceptual_sha)
    if not library_root.is_dir():
        raise FileNotFoundError(f"Chenwei library root does not exist: {library_root}")

    keep_candidates = audit["keep_candidates"]
    keep_by_sha = {item["sha256"]: item for item in keep_candidates}
    if len(keep_by_sha) != len(keep_candidates):
        raise ValueError("keep_candidates contains duplicate SHA-256 values")
    unknown_excludes = sorted(exclude_sha - set(keep_by_sha))
    if unknown_excludes:
        raise ValueError(f"Exclusion list contains SHA not present in keep_candidates: {unknown_excludes[:5]}")

    batch_order = {batch_id: index for index, batch_id in enumerate(audit["batches"], 1)}
    content_group_by_sha = {group["sha256"]: group for group in audit["content_groups"]}
    overrides = classification_overrides(visual, undated_photo_visual)
    date_overrides = capture_date_overrides(undated_photo_visual)
    unknown_override_shas = sorted((set(overrides) | set(date_overrides)) - set(keep_by_sha))
    if unknown_override_shas:
        raise ValueError(f"Visual/date override contains SHA not present in keep_candidates: {unknown_override_shas[:5]}")
    live_groups, live_by_sha = build_live_photo_groups(audit, keep_by_sha)
    mismatch_sha = {
        record["sha256"]
        for record in audit["source_records"]
        if (record.get("metadata") or {}).get("extension_content_mismatch")
    }

    records: list[dict[str, Any]] = []
    by_sha: dict[str, dict[str, Any]] = {}
    for candidate in keep_candidates:
        sha = candidate["sha256"]
        capture_value = candidate.get("captured_at")
        capture_source = candidate.get("capture_date_source")
        date_override = date_overrides.get(sha)
        date_override_applied = bool(date_override and not capture_value)
        if date_override_applied:
            capture_value = date_override["captured_at"]
            capture_source = date_override["source"]
        capture = parse_capture(capture_value)
        classification = classification_for(candidate, overrides)
        relative_parent, route_reason = target_relative_parent(classification["final_category"], capture)
        target_parent = windows_target(library_root, relative_parent) if relative_parent else None
        source_group = content_group_by_sha.get(sha) or {}
        ordered_source_batches = sorted(candidate.get("source_batches", []), key=lambda item: batch_order[item])
        source_members = []
        for member in source_group.get("source_members", []):
            source_members.append({
                **member,
                "batch_order": batch_order.get(member["batch_id"]),
            })
        pair = live_by_sha.get(sha)
        role = pair["roles"].get(sha) if pair else None
        conversion_required = sha in mismatch_sha
        record = {
            "source": {
                "batch_id": candidate["batch_id"],
                "batch_order": batch_order[candidate["batch_id"]],
                "source_batches": ordered_source_batches,
                "source_batch_orders": [batch_order[item] for item in ordered_source_batches],
                "relpath": candidate["relpath"],
                "path": candidate["path"],
                "name": candidate["name"],
                "extension": candidate["ext"],
                "size": candidate["size"],
                "sha256": sha,
                "staged_exact_duplicate_records": candidate["staged_exact_duplicate_records"],
                "content_group_source_members": source_members,
                "download_order_note": "Lower batch_order is the earlier downloaded batch; within-batch order is unknown.",
            },
            "capture": {
                **capture,
                "source": capture_source,
                "date_override_applied": date_override_applied,
                "date_override_report_item_id": date_override["review_id"] if date_override_applied else None,
                "date_override_source_text": date_override["source_text"] if date_override_applied else None,
                "date_override_precedence_note": date_override.get("precedence_note") if date_override_applied else None,
                "zip_packaging_mtime_used": False,
            },
            "classification": classification,
            "live_photo": {
                "is_member": bool(pair),
                "pair_id": pair["pair_id"] if pair else None,
                "role": role,
                "source_basenames": pair["source_basenames"] if pair else [],
            },
            "conversion": {
                "required": conversion_required,
                "reason": "HEIC container mislabeled with .JPG extension" if conversion_required else None,
                "planned_output_format": "JPEG" if conversion_required else None,
                "planned_output_extension": ".jpg" if conversion_required else None,
                "performed": False,
            },
            "routing": {
                "target_relative_parent": relative_parent,
                "target_parent": str(target_parent) if target_parent else None,
                "target_parent_exists": bool(target_parent and target_parent.is_dir()),
                "reason": route_reason,
            },
            "destination_mtime_policy": destination_mtime_policy(capture, capture_source),
            "disposition": None,
            "hold_reason": None,
            "planned_destination": None,
        }
        if not Path(candidate["path"]).is_file():
            raise FileNotFoundError(f"Canonical staged source is missing: {candidate['path']}")
        records.append(record)
        by_sha[sha] = record

    # Normalize each Live Photo pair as a unit. A timezone-aware MOV timestamp
    # and a local still timestamp should resolve to the same Taipei date.
    live_pair_validation: list[dict[str, Any]] = []
    for pair in live_groups:
        members = [by_sha[sha] for sha in pair["keep_shas"] if sha in by_sha]
        pair_status = {
            "pair_id": pair["pair_id"],
            "keep_member_count": len(members),
            "member_shas": [member["source"]["sha256"] for member in members],
            "roles": [member["live_photo"]["role"] for member in members],
            "source_basenames": pair["source_basenames"],
            "local_dates_before_pair_normalization": sorted({
                member["capture"]["local_date"] for member in members if member["capture"]["local_date"]
            }),
        }
        live_pair_validation.append(pair_status)
        if len(members) != 2 or {member["live_photo"]["role"] for member in members} != {"still", "video"}:
            for member in members:
                member["disposition"] = "hold"
                member["hold_reason"] = "live_photo_pair_incomplete_in_keep_candidates"
            continue
        categories = {member["classification"]["final_category"] for member in members}
        dates = {member["capture"]["local_date"] for member in members if member["capture"]["local_date"]}
        if categories != {"photo"}:
            for member in members:
                member["disposition"] = "hold"
                member["hold_reason"] = "live_photo_pair_classification_conflict"
            continue
        if len(dates) > 1:
            for member in members:
                member["disposition"] = "hold"
                member["hold_reason"] = "live_photo_pair_local_date_conflict"
            continue
        if dates:
            pair_date = next(iter(dates))
            year, month = pair_date[:4], pair_date[5:7]
            relative_parent = f"{year}相片/{year}.{month}"
        else:
            pair_date = None
            relative_parent = "2026相片/2026未分類"
        target_parent = windows_target(library_root, relative_parent)
        for member in members:
            member["live_photo"]["shared_local_date"] = pair_date
            member["routing"] = {
                "target_relative_parent": relative_parent,
                "target_parent": str(target_parent),
                "target_parent_exists": target_parent.is_dir(),
                "reason": "Live Photo pair-level routing",
            }
        if exclude_sha.intersection(pair["keep_shas"]):
            for member in members:
                member["disposition"] = "hold"
                member["hold_reason"] = "perceptual_exclusion_touches_live_photo_pair; pair-level decision required"

    # Decide plan/hold/exclude without assigning names yet.
    for record in records:
        if record["disposition"]:
            continue
        sha = record["source"]["sha256"]
        if sha in exclude_sha:
            record["disposition"] = "excluded_perceptual_duplicate"
            continue
        if not record["routing"]["target_relative_parent"]:
            record["disposition"] = "hold"
            record["hold_reason"] = record["routing"]["reason"]
            continue
        if not record["routing"]["target_parent_exists"]:
            record["disposition"] = "hold"
            if record["source"]["name"].casefold() == "img_2610.jpg" and record["routing"]["target_relative_parent"] == "2012相片/2012.06":
                record["hold_reason"] = "explicit_hold_IMG_2610.JPG; existing 2012.06 target is absent"
            else:
                record["hold_reason"] = "required_target_parent_does_not_exist"
            continue
        record["disposition"] = "plan"

    # Treat a planned Live Photo pair as one naming unit; all other planned
    # files are singleton naming units.
    naming_units: list[dict[str, Any]] = []
    consumed: set[str] = set()
    for pair in live_groups:
        members = [by_sha[sha] for sha in pair["keep_shas"] if sha in by_sha]
        planned = [member for member in members if member["disposition"] == "plan"]
        if planned:
            if len(planned) != 2:
                raise ValueError(f"Live Photo pair would be split: {pair['pair_id']}")
            naming_units.append({"kind": "live_photo", "pair": pair, "members": planned})
            consumed.update(member["source"]["sha256"] for member in planned)
    for record in records:
        if record["disposition"] == "plan" and record["source"]["sha256"] not in consumed:
            naming_units.append({"kind": "singleton", "pair": None, "members": [record]})

    def unit_sort_key(unit: dict[str, Any]) -> tuple[Any, ...]:
        members = unit["members"]
        first = min(members, key=lambda item: (item["source"]["batch_order"], item["source"]["name"].casefold()))
        pair_date = first["live_photo"].get("shared_local_date") if unit["kind"] == "live_photo" else None
        local_datetime = min(
            (member["capture"]["normalized_local_datetime"] for member in members if member["capture"]["normalized_local_datetime"]),
            default="9999-12-31T23:59:59+08:00",
        )
        return (
            first["routing"]["target_relative_parent"].casefold(),
            pair_date or first["capture"]["local_date"] or "9999-12-31",
            local_datetime,
            min(member["source"]["batch_order"] for member in members),
            first["source"]["name"].casefold(),
            first["source"]["sha256"],
        )

    folder_states: dict[str, dict[str, set[str]]] = {}
    operations: list[dict[str, Any]] = []
    for unit in sorted(naming_units, key=unit_sort_key):
        members = unit["members"]
        first = min(members, key=lambda item: (item["source"]["batch_order"], item["source"]["name"].casefold()))
        relative_parent = first["routing"]["target_relative_parent"]
        target_parent = windows_target(library_root, relative_parent)
        if relative_parent not in folder_states:
            folder_states[relative_parent] = collision_state(target_parent)
        state = folder_states[relative_parent]
        category = first["classification"]["final_category"]
        if unit["kind"] == "live_photo":
            local_date = first["live_photo"].get("shared_local_date")
        else:
            local_date = first["capture"]["local_date"]
        if local_date:
            date_basis = "capture_date"
            date_is_capture_time = True
        elif category in {"screenshot", "download"}:
            local_date = planned_import_date
            date_basis = "import_date"
            date_is_capture_time = False
        else:
            date_basis = "no_date_original_basename"
            date_is_capture_time = False
        if local_date:
            prefix = "" if category == "photo" else "S" if category == "screenshot" else "D"
            shared_stem = allocate_dated_stem(state, prefix, local_date)
        else:
            desired = unit["pair"]["source_basenames"][0] if unit["pair"] else Path(first["source"]["name"]).stem
            group_sha = hashlib.sha256("|".join(sorted(member["source"]["sha256"] for member in members)).encode("ascii")).hexdigest()
            shared_stem = allocate_undated_stem(state, desired, group_sha)

        output_extensions = [planned_extension(member) for member in members]
        if len(output_extensions) != len(set(output_extensions)):
            raise ValueError(f"Naming unit has colliding output extensions: {shared_stem}")
        for member, extension in sorted(zip(members, output_extensions), key=lambda pair: pair[1]):
            target_name = shared_stem + extension
            if target_name.casefold() in state["names"]:
                raise ValueError(f"Target filename collision after allocation: {target_parent / target_name}")
            state["names"].add(target_name.casefold())
            target_path = target_parent / target_name
            if target_path.exists():
                raise FileExistsError(f"Planned target already exists: {target_path}")
            member["live_photo"]["shared_destination_stem"] = shared_stem if unit["kind"] == "live_photo" else None
            member["planned_destination"] = {
                "relative_parent": relative_parent,
                "parent": str(target_parent),
                "name": target_name,
                "path": str(target_path),
                "shared_stem": shared_stem,
                "extension": extension,
                "date_basis": date_basis,
                "date_value": local_date,
                "date_is_capture_time": date_is_capture_time,
                "collision_policy": "logical stem reserved against all existing and earlier planned files in the target folder",
            }
            operation = {
                "operation_id": None,
                "operation": "convert_heic_container_to_jpeg_then_copy" if member["conversion"]["required"] else "copy",
                "source": member["source"],
                "capture": member["capture"],
                "classification": member["classification"],
                "live_photo": member["live_photo"],
                "conversion": member["conversion"],
                "destination": member["planned_destination"],
                "destination_mtime_policy": member["destination_mtime_policy"],
                "media_mutation_performed": False,
            }
            operations.append(operation)

    operations.sort(key=lambda item: (
        item["destination"]["relative_parent"].casefold(),
        item["destination"]["name"].casefold(),
        item["source"]["sha256"],
    ))
    for index, operation in enumerate(operations, 1):
        operation["operation_id"] = f"ICLOUD-{index:04d}"

    disposition_counts = Counter(record["disposition"] for record in records)
    category_counts = Counter(record["classification"]["final_category"] for record in records)
    planned_category_counts = Counter(operation["classification"]["final_category"] for operation in operations)
    hold_reason_counts = Counter(record["hold_reason"] for record in records if record["hold_reason"])
    provenance_counts = Counter(record["classification"]["provenance"]["method"] for record in records)
    plan_target_parents = sorted({operation["destination"]["parent"] for operation in operations})
    corrections = [
        record for record in records
        if record["classification"]["source_category"] == "screenshot"
        and record["classification"]["final_category"] == "photo"
    ]
    required_jpeg_correction_names = {"IMG_3054.JPEG", "IMG_3114.JPEG", "IMG_3118.JPEG"}
    required_jpeg_corrections = [
        record for record in corrections
        if record["source"]["name"] in required_jpeg_correction_names
    ]
    mismatch_records = [record for record in records if record["conversion"]["required"]]
    img_2610 = [record for record in records if record["source"]["name"].casefold() == "img_2610.jpg"]
    filename_date_recoveries = [
        record for record in records
        if record["capture"]["date_override_applied"]
        and record["capture"]["source"] == "filename_ymdhms_prefix"
    ]
    planned_pair_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for operation in operations:
        pair_id = operation["live_photo"]["pair_id"]
        if pair_id:
            planned_pair_groups[pair_id].append(operation)

    validation_errors: list[str] = []
    expected_keep = audit["summary"]["new_unique_contents_to_keep"]
    if len(records) != expected_keep:
        validation_errors.append(f"record count {len(records)} != audit keep count {expected_keep}")
    if sum(disposition_counts.values()) != len(records):
        validation_errors.append("disposition counts do not cover every candidate")
    if len(operations) != disposition_counts.get("plan", 0):
        validation_errors.append("operation count does not equal plan disposition count")
    if any(not Path(parent).is_dir() for parent in plan_target_parents):
        validation_errors.append("one or more planned target parents do not exist")
    if any(Path(operation["destination"]["path"]).exists() for operation in operations):
        validation_errors.append("one or more planned target paths already exist")
    if len({operation["destination"]["path"].casefold() for operation in operations}) != len(operations):
        validation_errors.append("planned target paths are not unique case-insensitively")
    if len(required_jpeg_corrections) != 3 or {record["source"]["name"] for record in required_jpeg_corrections} != required_jpeg_correction_names:
        validation_errors.append("the three required screenshot-JPEG-to-photo corrections are not exact")
    expected_mismatch = audit["summary"]["extension_content_mismatch_unique_contents"]
    if len(mismatch_records) != expected_mismatch or expected_mismatch != 7:
        validation_errors.append(f"mislabeled HEIC/JPG count is {len(mismatch_records)}, expected 7")
    if len(img_2610) != 1 or img_2610[0]["disposition"] != "hold" or "2012.06" not in (img_2610[0]["hold_reason"] or ""):
        validation_errors.append("IMG_2610.JPG is not explicitly held for missing 2012.06")
    if len(filename_date_recoveries) != 1:
        validation_errors.append(f"filename date recovery count is {len(filename_date_recoveries)}, expected 1")
    else:
        recovered = filename_date_recoveries[0]
        if recovered["source"]["name"] != "2017062721542034328.jpeg":
            validation_errors.append("filename date recovery was not applied to 2017062721542034328.jpeg")
        if recovered["capture"]["normalized_local_datetime"] != "2017-06-27T21:54:20+08:00":
            validation_errors.append("filename date recovery timestamp is not 2017-06-27T21:54:20+08:00")
        if recovered["routing"]["target_relative_parent"] != "2017相片/2017.06":
            validation_errors.append("filename date recovery was not routed to 2017相片/2017.06")
    for pair_id, pair_operations in planned_pair_groups.items():
        if len(pair_operations) != 2:
            validation_errors.append(f"planned Live Photo pair is split: {pair_id}")
            continue
        stems = {operation["destination"]["shared_stem"] for operation in pair_operations}
        extensions = {operation["destination"]["extension"] for operation in pair_operations}
        if len(stems) != 1 or extensions != {".jpg", ".mov"}:
            validation_errors.append(f"Live Photo pair does not share one .jpg/.mov stem: {pair_id}")
    mismatch_pair_ids = {record["live_photo"]["pair_id"] for record in mismatch_records}
    if None in mismatch_pair_ids or len(mismatch_pair_ids) != 7:
        validation_errors.append("each mislabeled HEIC/JPG still must belong to a distinct Live Photo pair")

    validation = {
        "ok": not validation_errors,
        "errors": validation_errors,
        "candidate_count_matches_audit": len(records) == expected_keep,
        "all_candidates_have_one_disposition": sum(disposition_counts.values()) == len(records),
        "all_planned_target_parents_exist": all(Path(parent).is_dir() for parent in plan_target_parents),
        "all_planned_target_paths_absent": all(not Path(operation["destination"]["path"]).exists() for operation in operations),
        "planned_target_paths_unique_case_insensitively": len({operation["destination"]["path"].casefold() for operation in operations}) == len(operations),
        "zip_packaging_mtime_used": False,
        "visual_screenshot_jpeg_photo_corrections": [
            {"name": record["source"]["name"], "sha256": record["source"]["sha256"], "target": record["routing"]["target_relative_parent"]}
            for record in required_jpeg_corrections
        ],
        "mislabeled_heic_jpg_count": len(mismatch_records),
        "live_photo_pair_source_groups": len(live_groups),
        "live_photo_pair_planned_groups": len(planned_pair_groups),
        "live_photo_pair_details": live_pair_validation,
        "IMG_2610_JPG": {
            "count": len(img_2610),
            "disposition": img_2610[0]["disposition"] if img_2610 else None,
            "hold_reason": img_2610[0]["hold_reason"] if img_2610 else None,
        },
        "filename_date_recovery": {
            "count": len(filename_date_recoveries),
            "source_name": filename_date_recoveries[0]["source"]["name"] if filename_date_recoveries else None,
            "capture_source": filename_date_recoveries[0]["capture"]["source"] if filename_date_recoveries else None,
            "normalized_local_datetime": filename_date_recoveries[0]["capture"]["normalized_local_datetime"] if filename_date_recoveries else None,
            "target_relative_parent": filename_date_recoveries[0]["routing"]["target_relative_parent"] if filename_date_recoveries else None,
            "zip_packaging_mtime_used": False,
        },
    }
    if validation_errors:
        raise RuntimeError("Plan validation failed:\n- " + "\n- ".join(validation_errors))

    known_holds = [
        record for record in records
        if record["disposition"] == "hold"
        and record["hold_reason"] == "explicit_hold_IMG_2610.JPG; existing 2012.06 target is absent"
    ]
    unresolved_holds = [
        record for record in records
        if record["disposition"] == "hold" and record not in known_holds
    ]
    notices = []
    if known_holds:
        notices.append(
            "Known hold: IMG_2610.JPG remains unplanned because the existing 2012相片/2012.06 folder is absent; no folder will be created."
        )
    undated_visual_complete = (
        undated_photo_visual.get("review_status") == "complete"
        and (undated_photo_visual.get("validation") or {}).get("ok") is True
        and (undated_photo_visual.get("summary") or {}).get("total") == 403
        and len(undated_photo_visual.get("overrides", [])) == 403
        and (undated_photo_visual.get("summary") or {}).get("unknown") == 0
    )
    blockers = []
    if not undated_visual_complete:
        blockers.append("undated-photo full visual review is incomplete, invalid, or contains unknown decisions")
    if args.perceptual_review_status != "complete":
        blockers.append("cross-library perceptual duplicate report is pending")
    if unresolved_holds:
        blockers.append(f"{len(unresolved_holds)} unresolved candidate(s) remain on hold")
    if blockers:
        plan_status = "draft_pending_resolution"
    elif known_holds:
        plan_status = "ready_for_execution_with_known_hold"
    else:
        plan_status = "ready_for_manual_approval"

    input_metadata = {
        "audit": {"path": str(args.audit.resolve()), "sha256": sha256_file(args.audit), "generated_at": audit.get("generated_at")},
        "visual": {"path": str(args.visual.resolve()), "sha256": sha256_file(args.visual), "generated_at": visual.get("generated_at")},
        "undated_photo_visual": {
            "path": str(args.undated_photo_visual.resolve()),
            "sha256": sha256_file(args.undated_photo_visual),
            "generated_at": undated_photo_visual.get("generated_at"),
            "review_status": undated_photo_visual.get("review_status"),
            "validation_ok": (undated_photo_visual.get("validation") or {}).get("ok"),
            "override_count": len(undated_photo_visual.get("overrides", [])),
            "unknown_count": (undated_photo_visual.get("summary") or {}).get("unknown"),
            "date_recovery_candidate_count": len(undated_photo_visual.get("date_recovery_candidates", [])),
        },
        "exclude_perceptual_sha": {
            "path": str(args.exclude_perceptual_sha.resolve()),
            "sha_count": len(exclude_sha),
            "review_status": args.perceptual_review_status,
        },
        "planned_import_date": {
            "value": planned_import_date,
            "used_only_for_undated_screenshot_download_names": True,
            "is_capture_time": False,
            "rerun_required_if_actual_import_date_differs": True,
        },
    }
    summary = {
        "keep_candidates": len(records),
        "final_classification": dict(sorted(category_counts.items())),
        "classification_provenance": dict(sorted(provenance_counts.items())),
        "disposition": dict(sorted(disposition_counts.items())),
        "planned_operations": len(operations),
        "planned_classification": dict(sorted(planned_category_counts.items())),
        "hold_reasons": dict(sorted(hold_reason_counts.items(), key=lambda item: str(item[0]))),
        "known_holds": len(known_holds),
        "unresolved_holds": len(unresolved_holds),
        "perceptual_excluded_sha": len(exclude_sha),
        "filename_date_recoveries_applied": len(filename_date_recoveries),
        "mislabeled_heic_jpg_to_convert": len(mismatch_records),
        "live_photo_pairs": len(live_groups),
        "live_photo_files_planned": sum(len(items) for items in planned_pair_groups.values()),
        "existing_target_parents_used": len(plan_target_parents),
    }
    manifest = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "status": plan_status,
        "mode": "read_only_plan; no import executed",
        "media_mutations_performed": False,
        "drive_folder_mutations_performed": False,
        "inputs": input_metadata,
        "library_root": str(library_root),
        "rules": {
            "new_drive_folders_allowed": False,
            "zip_packaging_mtime_may_be_capture_time": False,
            "live_photo_pair_members_share_stem": True,
            "mislabeled_heic_jpg_requires_real_jpeg_conversion": True,
            "perceptual_finalization_required": True,
            "undated_photo_full_visual_review_required": True,
            "filename_ymdhms_prefix_may_supply_capture_time_when_no_embedded_time_exists": True,
            "undated_screenshot_download_name_date_basis": "import_date; is_capture_time=false",
        },
        "blockers": blockers,
        "notices": notices,
        "summary": summary,
        "validation": validation,
        "operations": operations,
    }
    report = {
        "schema_version": 1,
        "generated_at": manifest["generated_at"],
        "status": plan_status,
        "mode": "read_only_planning_only",
        "import_executed": False,
        "media_mutations_performed": False,
        "drive_folder_mutations_performed": False,
        "inputs": input_metadata,
        "outputs": {
            "report": str(args.output_report.resolve()),
            "planned_manifest": str(args.output_manifest.resolve()),
        },
        "library_root": str(library_root),
        "blockers": blockers,
        "notices": notices,
        "summary": summary,
        "validation": validation,
        "target_parents_used": plan_target_parents,
        "hold_candidates": [record for record in records if record["disposition"] == "hold"],
        "known_hold_candidates": known_holds,
        "unresolved_hold_candidates": unresolved_holds,
        "excluded_candidates": [record for record in records if record["disposition"] == "excluded_perceptual_duplicate"],
        "conversion_candidates": mismatch_records,
        "classification_corrections": corrections,
        "candidate_decisions": records,
    }
    write_json_atomic(args.output_manifest, manifest)
    write_json_atomic(args.output_report, report)
    print(json.dumps({
        "report": str(args.output_report.resolve()),
        "manifest": str(args.output_manifest.resolve()),
        "status": plan_status,
        "blockers": blockers,
        "summary": summary,
        "validation_ok": validation["ok"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
