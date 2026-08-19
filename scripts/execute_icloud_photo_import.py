#!/usr/bin/env python3
"""Execute a reviewed iCloud photo import manifest safely.

The planner is authoritative.  This executor never creates folders, never
overwrites an existing destination, and never deletes source media.  It stages
and verifies each logical unit before committing it.  A Live Photo still and
video are one logical unit so they cannot be silently split.

Without ``--execute`` the command performs a complete read-only preflight,
including current source SHA-256 verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "scripts/logs/icloud_import_planned_manifest_20260804.json"
DEFAULT_LEDGER = REPO_ROOT / "scripts/logs/icloud_import_execution_20260804.jsonl"
DEFAULT_REPORT = REPO_ROOT / "scripts/logs/icloud_import_execution_report_20260804.json"
READY_STATUSES = {
    "ready_for_execution",
    "ready_for_execution_with_known_hold",
}
COPY_BUFFER = 8 * 1024 * 1024


def configure_console() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(COPY_BUFFER):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def append_ledger(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid ledger JSON at line {number}: {exc}") from exc
        if not isinstance(row, dict):
            raise RuntimeError(f"Invalid non-object ledger row at line {number}")
        rows.append(row)
    return rows


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (OSError, ValueError):
        return False


def directory_snapshot(root: Path) -> set[str]:
    result: set[str] = {"."}
    for current, dirs, _files in os.walk(root):
        current_path = Path(current)
        for name in dirs:
            result.add((current_path / name).relative_to(root).as_posix().casefold())
    return result


def verify_input_artifacts(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def walk(value: Any) -> Iterable[dict[str, Any]]:
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                yield value
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    seen: set[tuple[str, str]] = set()
    for item in walk(manifest.get("inputs", {})):
        raw_path = item["path"]
        expected = item["sha256"].casefold()
        key = (raw_path.casefold(), expected)
        if key in seen:
            continue
        seen.add(key)
        path = Path(raw_path)
        if not path.is_file():
            errors.append(f"manifest input missing: {path}")
            continue
        actual = sha256_file(path)
        if actual.casefold() != expected:
            errors.append(f"manifest input SHA mismatch: {path}")
    return errors


def build_units(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    singles: list[dict[str, Any]] = []
    for operation in operations:
        live = operation.get("live_photo") or {}
        if live.get("is_member"):
            pair_id = live.get("pair_id")
            if not pair_id:
                raise RuntimeError(f"Live Photo operation lacks pair_id: {operation.get('operation_id')}")
            pairs[str(pair_id)].append(operation)
        else:
            singles.append(operation)

    units: list[dict[str, Any]] = [
        {"unit_id": f"single:{op['operation_id']}", "kind": "single", "operations": [op]}
        for op in singles
    ]
    for pair_id, members in pairs.items():
        if len(members) != 2:
            raise RuntimeError(f"Live Photo pair {pair_id} has {len(members)} planned members")
        roles = {str((member.get("live_photo") or {}).get("role")) for member in members}
        extensions = {str((member.get("destination") or {}).get("extension", "")).casefold() for member in members}
        stems = {str((member.get("destination") or {}).get("shared_stem", "")).casefold() for member in members}
        if roles != {"still", "video"} or extensions != {".jpg", ".mov"} or len(stems) != 1:
            raise RuntimeError(f"Live Photo pair validation failed: {pair_id}")
        units.append({"unit_id": f"live:{pair_id}", "kind": "live_photo", "operations": members})

    units.sort(key=lambda unit: min(op["operation_id"] for op in unit["operations"]))
    return units


def validate_manifest(manifest: dict[str, Any], execute: bool) -> tuple[Path, list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[str] = []
    validation = manifest.get("validation") or {}
    if not validation.get("ok"):
        errors.append("manifest validation.ok is not true")
    status = manifest.get("status")
    if execute and status not in READY_STATUSES:
        errors.append(f"manifest status is not executable: {status!r}")
    if manifest.get("media_mutations_performed"):
        errors.append("manifest unexpectedly says media mutations were already performed")
    if manifest.get("drive_folder_mutations_performed"):
        errors.append("manifest unexpectedly says Drive folder mutations were performed")

    root = Path(str(manifest.get("library_root", "")))
    if not root.is_dir():
        errors.append(f"library root missing or not a directory: {root}")

    operations = manifest.get("operations")
    if not isinstance(operations, list) or not operations:
        errors.append("manifest operations must be a non-empty list")
        operations = []
    expected_count = (manifest.get("summary") or {}).get("planned_operations")
    if expected_count != len(operations):
        errors.append(f"planned operation count mismatch: summary={expected_count}, actual={len(operations)}")

    ids: set[str] = set()
    targets: set[str] = set()
    for operation in operations:
        operation_id = str(operation.get("operation_id", ""))
        if not operation_id or operation_id in ids:
            errors.append(f"missing or duplicate operation_id: {operation_id!r}")
        ids.add(operation_id)

        source = Path(str((operation.get("source") or {}).get("path", "")))
        destination = Path(str((operation.get("destination") or {}).get("path", "")))
        parent = Path(str((operation.get("destination") or {}).get("parent", "")))
        if not source.is_file():
            errors.append(f"source missing: {source}")
        if not parent.is_dir():
            errors.append(f"target parent missing (folders may not be created): {parent}")
        if destination.parent.resolve(strict=False) != parent.resolve(strict=False):
            errors.append(f"destination parent mismatch: {destination}")
        if root.is_dir() and (not is_within(parent, root) or not is_within(destination, root)):
            errors.append(f"destination escapes library root: {destination}")
        folded = str(destination.resolve(strict=False)).casefold()
        if folded in targets:
            errors.append(f"duplicate target path: {destination}")
        targets.add(folded)
        if operation.get("operation") not in {"copy", "convert_heic_container_to_jpeg_then_copy"}:
            errors.append(f"unsupported operation type: {operation.get('operation')}")

    if errors:
        raise RuntimeError("Manifest validation failed:\n- " + "\n- ".join(errors))
    units = build_units(operations)
    return root, operations, units


def verify_sources(operations: list[dict[str, Any]], workers: int) -> list[dict[str, Any]]:
    def verify(operation: dict[str, Any]) -> dict[str, Any]:
        source = Path(operation["source"]["path"])
        expected_size = int(operation["source"]["size"])
        expected_sha = str(operation["source"]["sha256"]).casefold()
        stat = source.stat()
        actual_sha = sha256_file(source)
        return {
            "operation_id": operation["operation_id"],
            "path": str(source),
            "expected_size": expected_size,
            "actual_size": stat.st_size,
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            "ok": stat.st_size == expected_size and actual_sha.casefold() == expected_sha,
        }

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(verify, operation): operation for operation in operations}
        for future in as_completed(future_map):
            results.append(future.result())
    results.sort(key=lambda row: row["operation_id"])
    failed = [row for row in results if not row["ok"]]
    if failed:
        examples = "\n- ".join(f"{row['operation_id']}: {row['path']}" for row in failed[:20])
        raise RuntimeError(f"Source preflight failed for {len(failed)} operation(s):\n- {examples}")
    return results


def import_conversion_dependencies() -> tuple[Any, Any]:
    try:
        from PIL import Image
        from pillow_heif import register_heif_opener
    except ImportError as exc:
        raise RuntimeError("Pillow and pillow-heif are required for HEIC-to-JPEG conversion") from exc
    register_heif_opener()
    return Image, register_heif_opener


def copy_bytes(source: Path, staged: Path) -> None:
    with source.open("rb") as incoming, staged.open("xb") as outgoing:
        shutil.copyfileobj(incoming, outgoing, length=COPY_BUFFER)
        outgoing.flush()
        os.fsync(outgoing.fileno())


def convert_heic_to_jpeg(source: Path, staged: Path) -> dict[str, Any]:
    Image, _register = import_conversion_dependencies()
    with Image.open(source) as image:
        image.load()
        source_format = str(image.format)
        source_size = tuple(image.size)
        exif = image.info.get("exif")
        icc = image.info.get("icc_profile")
        xmp = image.info.get("xmp")
        output = image.convert("RGB")
        options: dict[str, Any] = {"format": "JPEG", "quality": 95, "subsampling": 0, "optimize": True}
        if exif:
            options["exif"] = exif
        if icc:
            options["icc_profile"] = icc
        if xmp:
            options["xmp"] = xmp
        with staged.open("xb") as handle:
            output.save(handle, **options)
            handle.flush()
            os.fsync(handle.fileno())

    with Image.open(staged) as check:
        check.load()
        if check.format != "JPEG" or tuple(check.size) != source_size:
            raise RuntimeError(
                f"Converted JPEG validation failed for {source}: "
                f"format={check.format}, size={check.size}, expected={source_size}"
            )
    return {
        "source_decode_format": source_format,
        "source_dimensions": list(source_size),
        "output_decode_format": "JPEG",
        "output_dimensions": list(source_size),
        "exif_preserved": bool(exif),
        "icc_profile_preserved": bool(icc),
        "xmp_preserved": bool(xmp),
    }


def planned_mtime(operation: dict[str, Any], import_timestamp: float) -> tuple[float, dict[str, Any]]:
    policy = operation.get("destination_mtime_policy") or {}
    mode = policy.get("mode")
    if mode == "set_from_reliable_captured_at":
        raw = policy.get("planned_value")
        if not isinstance(raw, str):
            raise RuntimeError(f"Missing planned capture mtime for {operation['operation_id']}")
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            raise RuntimeError(f"Capture mtime lacks timezone for {operation['operation_id']}")
        return parsed.timestamp(), {"mode": mode, "value": raw, "is_capture_time": True}
    if mode == "set_at_execution_from_import_download_time":
        iso = datetime.fromtimestamp(import_timestamp, timezone.utc).astimezone().isoformat(timespec="seconds")
        return import_timestamp, {"mode": mode, "value": iso, "is_capture_time": False}
    raise RuntimeError(f"Unsupported destination mtime policy for {operation['operation_id']}: {mode!r}")


def stage_operation(
    operation: dict[str, Any],
    manifest_sha: str,
    import_timestamp: float,
) -> dict[str, Any]:
    source = Path(operation["source"]["path"])
    destination = Path(operation["destination"]["path"])
    temp_name = f".codex-icloud-{manifest_sha[:12]}-{operation['operation_id']}{destination.suffix}.tmp"
    staged = destination.parent / temp_name
    if staged.exists():
        staged.unlink()
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite destination: {destination}")

    conversion_info: dict[str, Any] | None = None
    try:
        if operation["operation"] == "copy":
            copy_bytes(source, staged)
        else:
            conversion_info = convert_heic_to_jpeg(source, staged)
        output_sha = sha256_file(staged)
        output_size = staged.stat().st_size
        if operation["operation"] == "copy":
            expected_sha = str(operation["source"]["sha256"]).casefold()
            if output_sha.casefold() != expected_sha or output_size != int(operation["source"]["size"]):
                raise RuntimeError(f"Staged copy verification failed: {operation['operation_id']}")
        mtime, mtime_record = planned_mtime(operation, import_timestamp)
        os.utime(staged, (mtime, mtime))
        return {
            "operation": operation,
            "source": source,
            "destination": destination,
            "staged": staged,
            "output_sha256": output_sha,
            "output_size": output_size,
            "conversion": conversion_info,
            "mtime": mtime_record,
        }
    except Exception:
        try:
            if staged.exists():
                staged.unlink()
        except OSError:
            pass
        raise


def commit_unit(
    unit: dict[str, Any],
    manifest_sha: str,
    ledger_path: Path,
    import_timestamp: float,
) -> list[dict[str, Any]]:
    staged_items: list[dict[str, Any]] = []
    try:
        for operation in unit["operations"]:
            staged_items.append(stage_operation(operation, manifest_sha, import_timestamp))

        append_ledger(
            ledger_path,
            {
                "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                "manifest_sha256": manifest_sha,
                "event": "unit_staged",
                "unit_id": unit["unit_id"],
                "kind": unit["kind"],
                "operation_ids": [item["operation"]["operation_id"] for item in staged_items],
                "destinations": [str(item["destination"]) for item in staged_items],
                "output_sha256": [item["output_sha256"] for item in staged_items],
            },
        )

        moved: list[dict[str, Any]] = []
        try:
            for item in staged_items:
                if item["destination"].exists():
                    raise FileExistsError(f"Destination appeared during commit: {item['destination']}")
                os.replace(item["staged"], item["destination"])
                moved.append(item)
        except Exception:
            rollback_errors: list[str] = []
            for item in reversed(moved):
                try:
                    if item["destination"].exists() and not item["staged"].exists():
                        os.replace(item["destination"], item["staged"])
                except Exception as exc:
                    rollback_errors.append(f"{item['destination']}: {exc}")
            if rollback_errors:
                raise RuntimeError("Unit commit failed and rollback was incomplete: " + "; ".join(rollback_errors))
            raise

        try:
            records: list[dict[str, Any]] = []
            for item in staged_items:
                destination = item["destination"]
                actual_sha = sha256_file(destination)
                actual_size = destination.stat().st_size
                if actual_sha.casefold() != item["output_sha256"].casefold() or actual_size != item["output_size"]:
                    raise RuntimeError(f"Post-commit verification failed: {destination}")
                records.append(
                    {
                        "operation_id": item["operation"]["operation_id"],
                        "operation": item["operation"]["operation"],
                        "source_path": str(item["source"]),
                        "source_sha256": item["operation"]["source"]["sha256"],
                        "destination_path": str(destination),
                        "destination_sha256": actual_sha,
                        "destination_size": actual_size,
                        "conversion": item["conversion"],
                        "mtime_policy": item["mtime"],
                        "live_photo": item["operation"].get("live_photo"),
                    }
                )

            # The durable completion row is part of the unit transaction.  If
            # it cannot be flushed, roll the just-committed files back so a
            # retry never encounters untracked destinations.
            append_ledger(
                ledger_path,
                {
                    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "manifest_sha256": manifest_sha,
                    "event": "unit_completed",
                    "unit_id": unit["unit_id"],
                    "kind": unit["kind"],
                    "operations": records,
                },
            )
            return records
        except Exception:
            rollback_errors: list[str] = []
            for item in reversed(moved):
                try:
                    if item["destination"].exists() and not item["staged"].exists():
                        os.replace(item["destination"], item["staged"])
                except Exception as exc:
                    rollback_errors.append(f"{item['destination']}: {exc}")
            if rollback_errors:
                raise RuntimeError(
                    "Post-commit verification/ledger write failed and rollback was incomplete: "
                    + "; ".join(rollback_errors)
                )
            raise
    finally:
        for item in staged_items:
            try:
                if item["staged"].exists():
                    item["staged"].unlink()
            except OSError:
                pass


def completed_from_ledger(rows: list[dict[str, Any]], manifest_sha: str) -> dict[str, dict[str, Any]]:
    completed: dict[str, dict[str, Any]] = {}
    foreign = {row.get("manifest_sha256") for row in rows if row.get("manifest_sha256") != manifest_sha}
    if foreign:
        raise RuntimeError("Ledger contains a different manifest SHA; use a separate ledger path")
    for row in rows:
        if row.get("event") != "unit_completed":
            continue
        for operation in row.get("operations") or []:
            operation_id = operation.get("operation_id")
            if operation_id:
                completed[str(operation_id)] = operation
    return completed


def verify_resume_destinations(
    operations: list[dict[str, Any]],
    completed: dict[str, dict[str, Any]],
) -> None:
    errors: list[str] = []
    for operation in operations:
        operation_id = operation["operation_id"]
        destination = Path(operation["destination"]["path"])
        ledger_record = completed.get(operation_id)
        if ledger_record:
            if not destination.is_file():
                errors.append(f"completed destination is missing: {destination}")
                continue
            actual_sha = sha256_file(destination)
            if actual_sha.casefold() != str(ledger_record.get("destination_sha256", "")).casefold():
                errors.append(f"completed destination SHA changed: {destination}")
        elif destination.exists():
            errors.append(f"untracked destination already exists: {destination}")
    if errors:
        raise RuntimeError("Resume/destination validation failed:\n- " + "\n- ".join(errors[:50]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--verify-workers", type=int, default=4)
    parser.add_argument("--execute", action="store_true", help="perform the planned writes after preflight")
    return parser.parse_args()


def main() -> int:
    configure_console()
    args = parse_args()
    if args.verify_workers < 1 or args.verify_workers > 16:
        raise RuntimeError("--verify-workers must be between 1 and 16")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_sha = canonical_json_sha256(manifest)
    started_at = datetime.now().astimezone()
    import_timestamp = started_at.timestamp()
    root, operations, units = validate_manifest(manifest, args.execute)

    input_errors = verify_input_artifacts(manifest)
    if input_errors:
        raise RuntimeError("Manifest input verification failed:\n- " + "\n- ".join(input_errors))

    ledger_rows = load_ledger(args.ledger)
    completed = completed_from_ledger(ledger_rows, manifest_sha)
    verify_resume_destinations(operations, completed)

    source_results = verify_sources(operations, args.verify_workers)
    directories_before = directory_snapshot(root)

    pending_units = [
        unit
        for unit in units
        if not all(operation["operation_id"] in completed for operation in unit["operations"])
    ]
    partially_completed = [
        unit["unit_id"]
        for unit in units
        if any(operation["operation_id"] in completed for operation in unit["operations"])
        and not all(operation["operation_id"] in completed for operation in unit["operations"])
    ]
    if partially_completed:
        raise RuntimeError("Ledger contains partially completed logical units: " + ", ".join(partially_completed))

    execution_records: list[dict[str, Any]] = []
    if args.execute:
        for index, unit in enumerate(pending_units, start=1):
            records = commit_unit(unit, manifest_sha, args.ledger, import_timestamp)
            execution_records.extend(records)
            if index % 25 == 0 or index == len(pending_units):
                print(f"[{index}/{len(pending_units)}] logical import units committed", flush=True)

    directories_after = directory_snapshot(root)
    if directories_after != directories_before:
        added = sorted(directories_after - directories_before)
        removed = sorted(directories_before - directories_after)
        raise RuntimeError(f"Drive folder set changed unexpectedly; added={added[:20]}, removed={removed[:20]}")

    completed_after = completed_from_ledger(load_ledger(args.ledger), manifest_sha) if args.execute else completed
    all_complete = len(completed_after) == len(operations)
    report = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": "execute" if args.execute else "read_only_preflight",
        "manifest": {
            "path": str(args.manifest.resolve()),
            "canonical_sha256": manifest_sha,
            "status": manifest.get("status"),
        },
        "library_root": str(root.resolve()),
        "summary": {
            "planned_operations": len(operations),
            "logical_units": len(units),
            "live_photo_units": sum(unit["kind"] == "live_photo" for unit in units),
            "source_preflight_verified": len(source_results),
            "previously_completed_operations": len(completed),
            "operations_completed_this_run": len(execution_records),
            "completed_operations_after_run": len(completed_after),
            "all_operations_complete": all_complete,
            "conversion_operations": sum(operation["operation"] != "copy" for operation in operations),
            "classification": dict(Counter(operation["classification"]["final_category"] for operation in operations)),
            "folders_created": 0,
            "folders_deleted": 0,
            "source_files_deleted": 0,
        },
        "validation": {
            "manifest_ok": True,
            "manifest_inputs_sha_verified": True,
            "all_current_source_sha_verified": True,
            "all_target_parents_preexisted": True,
            "folder_set_unchanged": directories_after == directories_before,
            "directory_count_before": len(directories_before),
            "directory_count_after": len(directories_after),
        },
        "ledger": str(args.ledger.resolve()),
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    write_json_atomic(args.report, report)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"Report: {args.report.resolve()}")
    if args.execute and not all_complete:
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted; completed ledger entries are resumable.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
