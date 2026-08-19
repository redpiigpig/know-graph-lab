#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safely plan and execute canonical photo-library renames.

Names have the form ``{S|D|}YYYY-MM-DD(N).ext``.  The prefix is a structural
bucket label only:

* files under ``YYYY截圖`` use ``S``;
* files under ``YYYY下載`` use ``D``;
* month/event photos have no prefix.

An unprefixed month/event file may be named from a capture date only when a
physical-device Make + Model and a parseable EXIF DateTimeOriginal or
DateTimeDigitized are present.  Filename dates and mtime never prove capture.
For S/D buckets, dates are explicitly non-capture labels: preserve a legal,
year-matching S/D date first; then use a year-matching embedded/filename date;
otherwise use the bucket year's January 1 anchor.

The default command is plan-only.  Execution and rollback require an explicit
reviewed manifest, checkpoint, and confirmed plan SHA-256.  Renames use a
whole-batch collision preflight and two phases (source -> temp -> target), with
checkpoint resume and best-effort whole-batch rollback.  Targets are never
overwritten.  Same-stem image/video candidates are one logical unit and share
one canonical basename.

Examples::

    python scripts/rename_photos.py
    python scripts/rename_photos.py plan --library chenwei --manifest plan.json
    python scripts/rename_photos.py execute --manifest plan.json \
        --checkpoint run.checkpoint.json --confirm-plan-sha256 <sha256>
    python scripts/rename_photos.py rollback --manifest plan.json \
        --checkpoint run.checkpoint.json --confirm-plan-sha256 <sha256>
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from PIL import ExifTags, Image


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


try:
    from pillow_heif import register_heif_opener  # type: ignore

    register_heif_opener()
    HEIF_OK = True
except Exception:
    HEIF_OK = False


PHOTOS_PARENT = Path("G:/我的雲端硬碟/資料/知識圖工作室/照片")
LIBRARIES = {
    "chenwei": "辰瑋相片",
    "training": "訓練相片",
    "hongshi": "弘誓相片",
}
DEFAULT_LIB = "chenwei"

PHOTOS_ROOT = PHOTOS_PARENT / LIBRARIES[DEFAULT_LIB]
REPORT_PATH = Path(__file__).parent / f"photo_rename_report_{DEFAULT_LIB}.json"
LOG_PATH = Path(__file__).parent / "photo_rename_log.jsonl"

MANIFEST_SCHEMA = "photo-rename-manifest/v2"
CHECKPOINT_SCHEMA = "photo-rename-checkpoint/v1"
POLICY_VERSION = "trusted-capture-or-structural-date/v1"

IMG_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif",
    ".avif", ".bmp", ".mp4", ".mov", ".m4v", ".webm", ".mkv",
}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
STILL_EXTS = IMG_EXTS - VIDEO_EXTS

TMP_PREFIX = "__rename_tmp_"
MIN_YEAR, MAX_YEAR = 1900, 2100
FINGERPRINT_EDGE_BYTES = 64 * 1024

PHONE_MAKE_PREFIXES = (
    "samsung", "huawei", "htc", "asus", "google", "xiaomi", "oneplus",
    "oppo", "vivo", "realme", "lge", "lg electronics", "motorola",
    "honor", "nothing", "zte", "nokia",
)
CAMERA_MAKE_PREFIXES = (
    "canon", "nikon", "fujifilm", "fuji photo film", "olympus",
    "om digital solutions", "panasonic", "ricoh", "leica", "pentax",
    "sigma", "hasselblad", "casio", "kodak", "gopro", "dji",
    "phase one",
)
SONY_PHONE_MODEL_HINTS = ("xperia", "j9110", "j8110", "h9436", "h8")
APP_METADATA_MARKERS = (
    "snowcorp", "snow corporation", "foodie", "b612", "beautyplus",
    "meitu", "picsart", "vsco", "snapseed", "line camera", "instagram",
    "facebook", "adobe photoshop", "photoshop camera", "canva",
)
MODEL_PLACEHOLDERS = {
    "", "unknown", "none", "n/a", "na", "null", "camera", "digital camera",
    "smartphone", "phone", "mobile", "ios", "android",
}

_SCREENSHOT_RE = re.compile(r"^(?P<year>\d{4})截圖$")
_DOWNLOAD_RE = re.compile(r"^(?P<year>\d{4})下載$")
_MONTH_RE = re.compile(r"^(?P<year>\d{4})\.(?P<month>0[1-9]|1[0-2])$")
_YEAR_RE = re.compile(r"^(?P<year>\d{4})相片$")
_CANONICAL_RE = re.compile(
    r"^(?P<prefix>[SD]?)(?P<date>\d{4}-\d{2}-\d{2})\((?P<n>[1-9]\d*)\)"
    r"(?P<ext>\.[^.]+)$",
    re.IGNORECASE,
)
_FN_DATE_RE = re.compile(
    r"(?P<year>19\d{2}|20\d{2}|2100)[-_.\s]?"
    r"(?P<month>0[1-9]|1[0-2])[-_.\s]?"
    r"(?P<day>0[1-9]|[12]\d|3[01])"
    r"(?:[-_T\s]?(?P<hour>[01]\d|2[0-3])"
    r"[-_:.\s]?(?P<minute>[0-5]\d)"
    r"(?:[-_:.\s]?(?P<second>[0-5]\d))?)?"
)


def set_library(slug: str) -> None:
    global PHOTOS_ROOT, REPORT_PATH
    if slug not in LIBRARIES:
        raise ValueError(f"unknown library: {slug}; choose from {sorted(LIBRARIES)}")
    PHOTOS_ROOT = PHOTOS_PARENT / LIBRARIES[slug]
    REPORT_PATH = Path(__file__).parent / f"photo_rename_report_{slug}.json"


def normalize_ext(ext: str) -> str:
    lowered = ext.casefold()
    return ".jpg" if lowered == ".jpeg" else lowered


def _decode_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        for encoding in ("utf-8", "utf-16", "ascii"):
            try:
                return value.decode(encoding, errors="ignore").strip("\x00 ")
            except Exception:
                continue
        return ""
    return str(value).strip().strip("\x00")


def _normalise_text(value: Any) -> str:
    return re.sub(r"\s+", " ", _decode_text(value).casefold()).strip()


def _parse_datetime(value: Any) -> dt.datetime | None:
    text = _decode_text(value)
    if not text:
        return None
    for fmt in (
        "%Y:%m:%d %H:%M:%S",
        "%Y:%m:%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y:%m:%d",
        "%Y-%m-%d",
    ):
        try:
            parsed = dt.datetime.strptime(text, fmt)
        except ValueError:
            continue
        if MIN_YEAR <= parsed.year <= MAX_YEAR:
            return parsed
    return None


def _parse_filename_datetime(name: str) -> dt.datetime | None:
    match = _FN_DATE_RE.search(name)
    if not match:
        return None
    try:
        return dt.datetime(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
            int(match.group("hour") or 0),
            int(match.group("minute") or 0),
            int(match.group("second") or 0),
        )
    except ValueError:
        return None


def read_metadata(path: Path) -> dict[str, Any]:
    """Read still-image EXIF.  Failure returns no evidence, never a fallback."""

    if path.suffix.casefold() in VIDEO_EXTS:
        return {}
    try:
        with Image.open(path) as image:
            raw = image._getexif() if hasattr(image, "_getexif") else None
            return {
                ExifTags.TAGS.get(key, key): value
                for key, value in (raw or {}).items()
            }
    except Exception:
        return {}


def trusted_device_kind(make_value: Any, model_value: Any) -> str | None:
    make = _normalise_text(make_value)
    model = _normalise_text(model_value)
    if not make or not model or model in MODEL_PLACEHOLDERS:
        return None
    combined = f"{make} {model}"
    if any(marker in combined for marker in APP_METADATA_MARKERS):
        return None
    if make == "apple" or make.startswith("apple "):
        return "phone" if re.search(r"\b(?:iphone|ipad)\b", model) else None
    if make == "sony" or make.startswith("sony "):
        return (
            "phone"
            if any(hint in model for hint in SONY_PHONE_MODEL_HINTS)
            else "camera"
        )
    if any(make == prefix or make.startswith(prefix + " ")
           for prefix in PHONE_MAKE_PREFIXES):
        return "phone"
    if any(make == prefix or make.startswith(prefix + " ")
           for prefix in CAMERA_MAKE_PREFIXES):
        return "camera"
    return None


def trusted_capture(metadata: dict[str, Any]) -> dict[str, Any] | None:
    """Return trusted capture evidence; never consult filename or filesystem."""

    make = _decode_text(metadata.get("Make"))
    model = _decode_text(metadata.get("Model"))
    # Editing/export Software does not erase otherwise valid physical-device
    # evidence.  App identities are rejected only when Make/Model themselves
    # claim to be Snowcorp/Foodie/etc. (inside trusted_device_kind).
    device_kind = trusted_device_kind(make, model)
    if not device_kind:
        return None
    for tag in ("DateTimeOriginal", "DateTimeDigitized"):
        captured = _parse_datetime(metadata.get(tag))
        if captured:
            return {
                "datetime": captured,
                "date_source": tag,
                "make": make,
                "model": model,
                "device_kind": device_kind,
            }
    return None


def folder_prefix(folder_name: str) -> str:
    """Compatibility helper: exact S/D bucket folder names only."""

    if _SCREENSHOT_RE.fullmatch(folder_name):
        return "S"
    if _DOWNLOAD_RE.fullmatch(folder_name):
        return "D"
    return ""


def folder_context(folder: Path, photos_root: Path) -> dict[str, Any]:
    """Find inherited structural bucket/month context without using it as evidence."""

    chain: list[Path] = []
    current = folder
    root_resolved = photos_root.resolve(strict=False)
    while True:
        chain.append(current)
        if current.resolve(strict=False) == root_resolved or current.parent == current:
            break
        current = current.parent

    # S/D is inherited by nested event folders and has structural priority.
    for candidate in chain:
        match = _SCREENSHOT_RE.fullmatch(candidate.name)
        if match:
            return {
                "kind": "screenshot",
                "prefix": "S",
                "bucket_year": int(match.group("year")),
                "bucket_month": None,
                "context_folder": _slash(candidate),
            }
        match = _DOWNLOAD_RE.fullmatch(candidate.name)
        if match:
            return {
                "kind": "download",
                "prefix": "D",
                "bucket_year": int(match.group("year")),
                "bucket_month": None,
                "context_folder": _slash(candidate),
            }

    for candidate in chain:
        match = _MONTH_RE.fullmatch(candidate.name)
        if match:
            return {
                "kind": "month",
                "prefix": "",
                "bucket_year": int(match.group("year")),
                "bucket_month": int(match.group("month")),
                "context_folder": _slash(candidate),
            }

    for candidate in chain:
        match = _YEAR_RE.fullmatch(candidate.name)
        if match:
            return {
                "kind": "event",
                "prefix": "",
                "bucket_year": int(match.group("year")),
                "bucket_month": None,
                "context_folder": _slash(candidate),
            }
    return {
        "kind": "event",
        "prefix": "",
        "bucket_year": None,
        "bucket_month": None,
        "context_folder": _slash(folder),
    }


def _slash(path: Path) -> str:
    return str(path.resolve(strict=False)).replace("\\", "/")


def _same_path(left: Path, right: Path) -> bool:
    return _slash(left).casefold() == _slash(right).casefold()


def content_fingerprint(path: Path) -> str:
    """Fingerprint file content without depending on mutable path metadata.

    Small files are hashed completely.  Large files include size plus the first
    and last 64 KiB; this is an identity guard for checkpoint reconciliation,
    not a cryptographic archive checksum.
    """

    size = path.stat().st_size
    hasher = hashlib.sha256()
    hasher.update(f"edge64k-v1:{size}:".encode("ascii"))
    with path.open("rb") as stream:
        if size <= FINGERPRINT_EDGE_BYTES * 2:
            hasher.update(stream.read())
            scheme = "full-sha256-v1"
        else:
            hasher.update(stream.read(FINGERPRINT_EDGE_BYTES))
            stream.seek(size - FINGERPRINT_EDGE_BYTES)
            hasher.update(stream.read(FINGERPRINT_EDGE_BYTES))
            scheme = "edge64k-sha256-v1"
    return f"{scheme}:{hasher.hexdigest()}"


def _content_matches(path: Path, operation: dict[str, Any]) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == operation["source_size"]
        and content_fingerprint(path) == operation["content_fingerprint"]
    )


def _unit_id(folder: Path, files: Iterable[Path]) -> str:
    payload = _slash(folder) + "\n" + "\n".join(
        sorted(path.name.casefold() for path in files)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def _canonical_structural_date(
    path: Path, prefix: str, bucket_year: int,
) -> dt.datetime | None:
    match = _CANONICAL_RE.fullmatch(path.name)
    if not match or match.group("prefix").upper() != prefix:
        return None
    parsed = _parse_datetime(match.group("date"))
    return parsed if parsed and parsed.year == bucket_year else None


def _canonical_indices_for_verified_date(
    files: list[Path], *, prefix: str, verified_date: dt.date,
) -> set[int]:
    """Read canonical sequence numbers for ordering only, never date evidence."""

    indices: set[int] = set()
    for path in files:
        match = _CANONICAL_RE.fullmatch(path.name)
        if not match or match.group("prefix").upper() != prefix:
            continue
        parsed = _parse_datetime(match.group("date"))
        if parsed and parsed.date() == verified_date:
            indices.add(int(match.group("n")))
    return indices


def _unique_candidate_date(
    candidates: list[tuple[dt.datetime, str]],
    *,
    conflict_reason: str,
) -> tuple[dt.datetime | None, str | None, list[str]]:
    if not candidates:
        return None, None, []
    by_date = {candidate.date() for candidate, _source in candidates}
    if len(by_date) != 1:
        return None, None, [conflict_reason]
    chosen = min(candidates, key=lambda item: item[0])
    return chosen[0], chosen[1], []


def _structural_unit_date(
    files: list[Path],
    *,
    prefix: str,
    bucket_year: int,
    metadata_by_path: dict[Path, dict[str, Any]],
) -> dict[str, Any]:
    legal = [
        (parsed, "existing_legal_name")
        for path in files
        if (parsed := _canonical_structural_date(path, prefix, bucket_year))
    ]
    chosen, source, blocks = _unique_candidate_date(
        legal, conflict_reason="conflicting_legal_structural_dates_in_unit",
    )
    if blocks:
        return {"block_reasons": blocks}
    if chosen:
        return {
            "datetime": chosen,
            "date_source": source,
            "date_semantics": "not_capture",
            "not_capture": True,
            "block_reasons": [],
        }

    embedded: list[tuple[dt.datetime, str]] = []
    for path in files:
        metadata = metadata_by_path[path]
        for tag in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
            parsed = _parse_datetime(metadata.get(tag))
            if parsed and parsed.year == bucket_year:
                embedded.append((parsed, f"embedded_{tag}"))
                break
    chosen, source, blocks = _unique_candidate_date(
        embedded, conflict_reason="conflicting_embedded_structural_dates_in_unit",
    )
    if blocks:
        return {"block_reasons": blocks}
    if chosen:
        return {
            "datetime": chosen,
            "date_source": source,
            "date_semantics": "not_capture",
            "not_capture": True,
            "block_reasons": [],
        }

    filename_dates = [
        (parsed, "filename_date")
        for path in files
        if (parsed := _parse_filename_datetime(path.name))
        and parsed.year == bucket_year
    ]
    chosen, source, blocks = _unique_candidate_date(
        filename_dates, conflict_reason="conflicting_filename_structural_dates_in_unit",
    )
    if blocks:
        return {"block_reasons": blocks}
    if chosen:
        return {
            "datetime": chosen,
            "date_source": source,
            "date_semantics": "not_capture",
            "not_capture": True,
            "block_reasons": [],
        }

    return {
        "datetime": dt.datetime(bucket_year, 1, 1),
        "date_source": "bucket_year_01_01_anchor",
        "date_semantics": "not_capture",
        "not_capture": True,
        "block_reasons": [],
    }


def _photo_unit_date(
    files: list[Path],
    *,
    pair_candidate: bool,
    metadata_by_path: dict[Path, dict[str, Any]],
) -> dict[str, Any]:
    stills = [path for path in files if path.suffix.casefold() in STILL_EXTS]
    if not stills:
        return {"block_reasons": ["unprefixed_video_has_no_trusted_still_pair"]}

    evidences: list[dict[str, Any]] = []
    for still in stills:
        evidence = trusted_capture(metadata_by_path[still])
        if not evidence:
            return {
                "block_reasons": [
                    "unprefixed_file_lacks_trusted_physical_make_model_and_original_date"
                ]
            }
        evidences.append(evidence)

    dates = {evidence["datetime"].date() for evidence in evidences}
    if len(dates) != 1:
        return {"block_reasons": ["conflicting_trusted_capture_dates_in_unit"]}
    chosen = min(evidences, key=lambda evidence: evidence["datetime"])
    return {
        "datetime": chosen["datetime"],
        "date_source": (
            f"pair_{chosen['date_source']}" if pair_candidate else chosen["date_source"]
        ),
        "date_semantics": "capture",
        "not_capture": False,
        "capture_verified": True,
        "capture_inherited_by_video": pair_candidate,
        "make": chosen["make"],
        "model": chosen["model"],
        "device_kind": chosen["device_kind"],
        "block_reasons": [],
    }


def _logical_groups(files: list[Path]) -> list[tuple[list[Path], bool]]:
    by_stem: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        by_stem[path.stem.casefold()].append(path)

    groups: list[tuple[list[Path], bool]] = []
    for paths in by_stem.values():
        paths = sorted(paths, key=lambda path: path.name.casefold())
        suffixes = {path.suffix.casefold() for path in paths}
        if suffixes & STILL_EXTS and suffixes & VIDEO_EXTS:
            groups.append((paths, True))
        else:
            groups.extend(([path], False) for path in paths)
    return groups


def _add_block(operation: dict[str, Any], reason: str) -> None:
    reasons = operation.setdefault("block_reasons", [])
    if reason not in reasons:
        reasons.append(reason)
    operation["action_before_block"] = operation.get(
        "action_before_block", operation.get("action"),
    )
    operation["action"] = "blocked"


def collect_folder_plan(
    folder: Path,
    prefix: str | None = None,
    *,
    photos_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Build a safe plan for one folder.

    ``prefix`` is accepted only for legacy callers and is checked against the
    structural context; it is never allowed to invent a photo capture date.
    """

    root = photos_root or PHOTOS_ROOT
    if prefix is not None and photos_root is None:
        raise RuntimeError(
            "legacy collect_folder_plan caller is disabled; use a reviewed v2 manifest"
        )
    context = folder_context(folder, root)
    if prefix is not None and prefix != context["prefix"]:
        raise ValueError("legacy prefix disagrees with the folder's structural context")
    files = sorted(
        (
            path for path in folder.iterdir()
            if path.is_file()
            and path.suffix.casefold() in IMG_EXTS
            and not path.name.startswith(TMP_PREFIX)
        ),
        key=lambda path: path.name.casefold(),
    )
    metadata_by_path = {path: read_metadata(path) for path in files}
    units: list[dict[str, Any]] = []

    for unit_files, pair_candidate in _logical_groups(files):
        unit_id = _unit_id(folder, unit_files)
        if context["prefix"]:
            evidence = _structural_unit_date(
                unit_files,
                prefix=context["prefix"],
                bucket_year=context["bucket_year"],
                metadata_by_path=metadata_by_path,
            )
        else:
            evidence = _photo_unit_date(
                unit_files,
                pair_candidate=pair_candidate,
                metadata_by_path=metadata_by_path,
            )
        if not evidence.get("block_reasons") and evidence.get("datetime"):
            indices = _canonical_indices_for_verified_date(
                unit_files,
                prefix=context["prefix"],
                verified_date=evidence["datetime"].date(),
            )
            if len(indices) > 1:
                evidence["block_reasons"] = [
                    "conflicting_existing_canonical_indices_in_unit"
                ]
            elif indices:
                evidence["existing_index_for_order_only"] = next(iter(indices))
        units.append({
            "unit_id": unit_id,
            "files": unit_files,
            "pair_candidate": pair_candidate,
            "context": context,
            "evidence": evidence,
        })

    units.sort(key=lambda unit: (
        bool(unit["evidence"].get("block_reasons")),
        unit["evidence"].get("datetime", dt.datetime.max),
        unit["evidence"].get("existing_index_for_order_only", 10**12),
        min(path.name.casefold() for path in unit["files"]),
        unit["unit_id"],
    ))
    counters: dict[str, int] = defaultdict(int)
    operations: list[dict[str, Any]] = []

    for unit in units:
        evidence = unit["evidence"]
        block_reasons = list(evidence.get("block_reasons", []))
        canonical_base: str | None = None
        date_key: str | None = None
        if not block_reasons:
            date_key = evidence["datetime"].strftime("%Y-%m-%d")
            counters[date_key] += 1
            canonical_base = f"{context['prefix']}{date_key}({counters[date_key]})"

        for source in unit["files"]:
            target_name = (
                f"{canonical_base}{normalize_ext(source.suffix)}"
                if canonical_base else None
            )
            target = folder / target_name if target_name else None
            stat = source.stat()
            action = "blocked" if block_reasons else (
                "keep"
                if source.name.casefold() == target_name.casefold()
                else "rename"
            )
            operation = {
                "op_id": hashlib.sha256(_slash(source).encode("utf-8")).hexdigest()[:20],
                "unit_id": unit["unit_id"],
                "pair_candidate": unit["pair_candidate"],
                "src": _slash(source),
                "target": _slash(target) if target else None,
                "target_name": target_name,
                "temp": None,
                "folder": _slash(folder),
                "folder_name": folder.name,
                "context": context,
                "prefix": context["prefix"],
                "date": date_key,
                "datetime": (
                    evidence.get("datetime").isoformat()
                    if evidence.get("datetime") else None
                ),
                "date_source": evidence.get("date_source"),
                "date_semantics": evidence.get("date_semantics"),
                "not_capture": evidence.get("not_capture"),
                "capture_verified": bool(evidence.get("capture_verified")),
                "capture_inherited_by_video": bool(
                    evidence.get("capture_inherited_by_video")
                    and source.suffix.casefold() in VIDEO_EXTS
                ),
                "make": evidence.get("make"),
                "model": evidence.get("model"),
                "device_kind": evidence.get("device_kind"),
                "existing_index_for_order_only": evidence.get(
                    "existing_index_for_order_only"
                ),
                "action": action,
                "skip": action != "rename",  # blocked legacy callers must not write
                "dt": (
                    evidence.get("datetime").isoformat()
                    if evidence.get("datetime") else None
                ),
                "dt_source": evidence.get("date_source"),
                # mtime is an integrity fingerprint only, never a date source.
                "source_size": stat.st_size,
                "source_mtime_ns": stat.st_mtime_ns,
                "content_fingerprint": content_fingerprint(source),
                "block_reasons": block_reasons.copy(),
            }
            operations.append(operation)
    return operations


def _safe_walk_media(root: Path) -> tuple[dict[Path, list[Path]], list[str]]:
    by_folder: dict[Path, list[Path]] = defaultdict(list)
    leftovers: list[str] = []

    def walk(folder: Path) -> None:
        try:
            entries = sorted(folder.iterdir(), key=lambda path: path.name.casefold())
        except (OSError, PermissionError):
            return
        for entry in entries:
            if entry.is_file() and entry.name.startswith(TMP_PREFIX):
                leftovers.append(_slash(entry))
            elif entry.is_file() and entry.suffix.casefold() in IMG_EXTS:
                by_folder[folder].append(entry)
        for entry in entries:
            if entry.is_dir() and not entry.name.startswith("."):
                walk(entry)

    walk(root)
    return by_folder, leftovers


def _propagate_unit_blocks(operations: list[dict[str, Any]]) -> None:
    reasons_by_unit: dict[str, set[str]] = defaultdict(set)
    for operation in operations:
        reasons_by_unit[operation["unit_id"]].update(operation.get("block_reasons", []))
    for operation in operations:
        for reason in sorted(reasons_by_unit[operation["unit_id"]]):
            _add_block(operation, reason)


def _apply_batch_collision_checks(operations: list[dict[str, Any]]) -> None:
    # Stable, exact temp paths are part of the reviewed manifest.
    for operation in operations:
        if operation["action"] == "rename":
            source = Path(operation["src"])
            temp = source.parent / (
                f"{TMP_PREFIX}v2_{operation['op_id']}{source.suffix.casefold()}"
            )
            operation["temp"] = _slash(temp)
            if temp.exists():
                _add_block(operation, "temporary_path_already_exists")

    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_temp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_keys = {operation["src"].casefold() for operation in operations}
    for operation in operations:
        if operation.get("target") and operation["action"] != "blocked":
            by_target[operation["target"].casefold()].append(operation)
        if operation.get("temp") and operation["action"] != "blocked":
            by_temp[operation["temp"].casefold()].append(operation)

    for items in by_target.values():
        if len(items) > 1:
            for item in items:
                _add_block(item, "batch_target_collision")
    for items in by_temp.values():
        if len(items) > 1:
            for item in items:
                _add_block(item, "batch_temporary_collision")

    for operation in operations:
        if operation["action"] != "rename":
            continue
        target = Path(operation["target"])
        if target.exists() and operation["target"].casefold() not in source_keys:
            _add_block(operation, "target_exists_outside_rename_batch")
    _propagate_unit_blocks(operations)


def collect_plan(
    *, photos_root: Path = PHOTOS_ROOT,
) -> tuple[list[dict[str, Any]], int, list[str]]:
    if not photos_root.is_dir():
        raise FileNotFoundError(f"photo root does not exist: {photos_root}")
    by_folder, leftovers = _safe_walk_media(photos_root)
    operations: list[dict[str, Any]] = []
    for folder in sorted(by_folder, key=lambda path: path.as_posix().casefold()):
        operations.extend(collect_folder_plan(folder, photos_root=photos_root))
    _apply_batch_collision_checks(operations)
    return operations, len(by_folder), sorted(leftovers)


def summarize(operations: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(operations)
    return {
        "total": len(items),
        "by_action": dict(sorted(Counter(item["action"] for item in items).items())),
        "by_prefix": dict(sorted(Counter(item["prefix"] or "(none)" for item in items).items())),
        "by_date_source": dict(sorted(Counter(
            item.get("date_source") or "blocked" for item in items
        ).items())),
        "capture_verified": sum(bool(item.get("capture_verified")) for item in items),
        "not_capture": sum(bool(item.get("not_capture")) for item in items),
        "pair_files": sum(bool(item.get("pair_candidate")) for item in items),
        "blocked": sum(item["action"] == "blocked" for item in items),
        "block_reasons": dict(sorted(Counter(
            reason for item in items for reason in item.get("block_reasons", [])
        ).items())),
    }


def current_script_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def compute_plan_sha256(
    *,
    root: str | Path,
    library: str,
    operations: list[dict[str, Any]],
    script_sha256: str,
    leftover_tmp_files: list[str],
) -> str:
    payload = {
        "schema": MANIFEST_SCHEMA,
        "policy_version": POLICY_VERSION,
        "root": _slash(Path(root)),
        "library": library,
        "script_sha256": script_sha256,
        "leftover_tmp_files": leftover_tmp_files,
        "operations": operations,
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_manifest(
    operations: list[dict[str, Any]],
    *,
    photos_root: Path,
    library: str = DEFAULT_LIB,
    folders_scanned: int = 0,
    leftover_tmp_files: list[str] | None = None,
) -> dict[str, Any]:
    leftovers = leftover_tmp_files or []
    summary = summarize(operations)
    script_sha256 = current_script_sha256()
    digest = compute_plan_sha256(
        root=photos_root,
        library=library,
        operations=operations,
        script_sha256=script_sha256,
        leftover_tmp_files=leftovers,
    )
    return {
        "schema": MANIFEST_SCHEMA,
        "policy_version": POLICY_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "plan_only",
        "status": (
            "blocked" if summary["blocked"] or leftovers else "ready_for_review"
        ),
        "root": _slash(photos_root),
        "library": library,
        "script_sha256": script_sha256,
        "plan_sha256": digest,
        "folders_scanned": folders_scanned,
        "leftover_tmp_files": leftovers,
        "policy": {
            "unprefixed_date": (
                "trusted physical Make+Model plus EXIF DateTimeOriginal/"
                "DateTimeDigitized only"
            ),
            "filename_and_mtime": "never capture evidence",
            "sd_date_semantics": "structural not_capture",
            "sd_fallback": "bucket year January 1 anchor",
            "same_stem_image_video": "one logical unit and shared basename",
            "writes": "explicit manifest/checkpoint, no overwrite, two-phase",
        },
        "summary": summary,
        "operations": operations,
    }


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def validate_manifest(
    manifest: dict[str, Any], *, require_current_script: bool = True,
) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("unsupported or missing manifest schema")
    if manifest.get("policy_version") != POLICY_VERSION:
        raise ValueError("manifest policy version mismatch")
    operations = manifest.get("operations")
    if not isinstance(operations, list):
        raise ValueError("manifest operations must be a list")
    script_sha256 = manifest.get("script_sha256")
    if not script_sha256:
        raise ValueError("manifest does not record its renamer script hash")
    if require_current_script and script_sha256 != current_script_sha256():
        raise ValueError("manifest was produced by a different renamer script")
    expected = compute_plan_sha256(
        root=manifest.get("root", ""),
        library=manifest.get("library", ""),
        operations=operations,
        script_sha256=script_sha256,
        leftover_tmp_files=manifest.get("leftover_tmp_files", []),
    )
    if manifest.get("plan_sha256") != expected:
        raise ValueError("manifest plan_sha256 mismatch")
    if manifest.get("status") != "ready_for_review":
        raise ValueError(f"manifest is not executable: status={manifest.get('status')}")
    if manifest.get("leftover_tmp_files"):
        raise ValueError("manifest records leftover temporary files")
    if any(item.get("action") == "blocked" for item in operations):
        raise ValueError("manifest contains blocked operations")
    if any(item.get("action") not in {"keep", "rename"} for item in operations):
        raise ValueError("manifest contains unsupported actions")

    sources = [item["src"].casefold() for item in operations]
    targets = [item["target"].casefold() for item in operations]
    op_ids = [item["op_id"] for item in operations]
    temps = [
        item["temp"].casefold() for item in operations if item["action"] == "rename"
    ]
    if len(sources) != len(set(sources)):
        raise ValueError("manifest has duplicate sources")
    if len(op_ids) != len(set(op_ids)):
        raise ValueError("manifest has duplicate operation ids")
    if len(targets) != len(set(targets)):
        raise ValueError("manifest has duplicate targets")
    if len(temps) != len(set(temps)):
        raise ValueError("manifest has duplicate temporary paths")

    by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in operations:
        by_unit[item["unit_id"]].append(item)
        target = Path(item["target"])
        if target.name != item.get("target_name"):
            raise ValueError("target path/name mismatch")
        canonical = _CANONICAL_RE.fullmatch(target.name)
        if not canonical or canonical.group("prefix").upper() != item["prefix"]:
            raise ValueError("target name is not canonical for its structural prefix")
        if canonical.group("date") != item.get("date"):
            raise ValueError("target canonical date does not match reviewed date")
        if not item.get("content_fingerprint"):
            raise ValueError("operation lacks content fingerprint")
        if item["action"] == "rename":
            if not item.get("temp") or not Path(item["temp"]).name.startswith(TMP_PREFIX):
                raise ValueError("rename operation lacks a canonical temporary path")
        elif item.get("temp") is not None:
            raise ValueError("keep operation unexpectedly has a temporary path")
        if item["prefix"]:
            if item.get("date_semantics") != "not_capture" or not item.get("not_capture"):
                raise ValueError("S/D operation is not marked as structural not_capture")
        elif not item.get("capture_verified"):
            raise ValueError("unprefixed operation lacks verified capture evidence")
        elif item.get("date_semantics") != "capture" or item.get("not_capture"):
            raise ValueError("unprefixed operation is not marked as verified capture")
        if item.get("date_source") == "mtime":
            raise ValueError("mtime may not be a naming date source")
    for items in by_unit.values():
        if not any(item.get("pair_candidate") for item in items):
            continue
        bases = {Path(item["target"]).stem.casefold() for item in items}
        if len(bases) != 1:
            raise ValueError("same-stem image/video unit does not share a target basename")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _rename_no_overwrite(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"refusing to overwrite: {target}")
    source.rename(target)


def _checkpoint_template(manifest_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": CHECKPOINT_SCHEMA,
        "manifest": _slash(manifest_path),
        "plan_sha256": manifest["plan_sha256"],
        "status": "preflight_complete",
        "op_states": {
            item["op_id"]: "planned"
            for item in manifest["operations"] if item["action"] == "rename"
        },
        "intent": None,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def _load_checkpoint(
    checkpoint_path: Path,
    *,
    manifest_path: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if checkpoint.get("schema") != CHECKPOINT_SCHEMA:
        raise ValueError("unsupported checkpoint schema")
    if checkpoint.get("plan_sha256") != manifest["plan_sha256"]:
        raise ValueError("checkpoint belongs to a different plan")
    if not _same_path(Path(checkpoint.get("manifest", "")), manifest_path):
        raise ValueError("checkpoint belongs to a different manifest path")
    expected_ids = {
        item["op_id"] for item in manifest["operations"] if item["action"] == "rename"
    }
    states = checkpoint.get("op_states")
    if not isinstance(states, dict) or set(states) != expected_ids:
        raise ValueError("checkpoint operations do not match manifest")
    intent = checkpoint.get("intent")
    if intent is not None and (
        not isinstance(intent, dict) or intent.get("op_id") not in expected_ids
    ):
        raise ValueError("checkpoint contains an invalid write-ahead intent")
    return checkpoint


def _write_checkpoint(path: Path, checkpoint: dict[str, Any]) -> None:
    checkpoint["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    _atomic_write_json(path, checkpoint)


def _write_intent(
    checkpoint_path: Path,
    checkpoint: dict[str, Any],
    *,
    operation: dict[str, Any],
    transition: str,
    source: Path,
    target: Path,
) -> None:
    checkpoint["intent"] = {
        "op_id": operation["op_id"],
        "transition": transition,
        "from": _slash(source),
        "to": _slash(target),
        "written_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    _write_checkpoint(checkpoint_path, checkpoint)


def _reconcile_checkpoint(
    checkpoint: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    phase2_statuses = {"phase2", "complete", "rollback", "rollback_failed"}
    status = checkpoint.get("status")
    states = checkpoint["op_states"]
    for operation in manifest["operations"]:
        if operation["action"] != "rename":
            continue
        op_id = operation["op_id"]
        recorded = states[op_id]
        source_matches = _content_matches(Path(operation["src"]), operation)
        temp_matches = _content_matches(Path(operation["temp"]), operation)
        target_matches = _content_matches(Path(operation["target"]), operation)
        if recorded == "planned":
            if source_matches and not temp_matches:
                continue
            if temp_matches:
                states[op_id] = "staged"
                continue
            if target_matches and status in phase2_statuses:
                states[op_id] = "committed"
                continue
        elif recorded == "staged":
            if temp_matches:
                continue
            if target_matches and status in phase2_statuses:
                states[op_id] = "committed"
                continue
            if source_matches and status in {"rollback", "rollback_failed"}:
                states[op_id] = "planned"
                continue
        elif recorded == "committed":
            # Another source path in a swap may contain identical content; the
            # recorded committed state and matching target remain authoritative.
            if target_matches and not temp_matches:
                continue
            if temp_matches and status in {"rollback", "rollback_failed"}:
                states[op_id] = "staged"
                continue
        raise ValueError(
            f"checkpoint/disk state mismatch for {operation['src']}: "
            f"recorded={recorded}, source_matches={source_matches}, "
            f"temp_matches={temp_matches}, target_matches={target_matches}, "
            f"status={status}"
        )
    checkpoint["intent"] = None


def preflight_execution(
    manifest: dict[str, Any],
    *,
    checkpoint: dict[str, Any] | None = None,
) -> None:
    validate_manifest(manifest)
    root = Path(manifest["root"])
    operations = manifest["operations"]
    rename_ops = [item for item in operations if item["action"] == "rename"]
    source_keys = {item["src"].casefold() for item in rename_ops}
    states = checkpoint["op_states"] if checkpoint else {}

    for operation in operations:
        source = Path(operation["src"])
        target = Path(operation["target"])
        if not _is_within(source, root) or not _is_within(target, root):
            raise ValueError(f"operation escapes manifest root: {source}")
        if source.parent.resolve() != target.parent.resolve():
            raise ValueError("rename target must remain in the source folder")
        if operation["action"] == "keep":
            if not source.is_file():
                raise FileNotFoundError(f"kept source missing: {source}")
            if not _content_matches(source, operation):
                raise ValueError(f"kept source content changed: {source}")
            continue

        temp = Path(operation["temp"])
        if not _is_within(temp, root) or temp.parent.resolve() != source.parent.resolve():
            raise ValueError("temporary path escapes source folder")
        state = states.get(operation["op_id"], "planned")
        if state == "planned":
            if not source.is_file():
                raise FileNotFoundError(f"source missing: {source}")
            stat = source.stat()
            if stat.st_size != operation["source_size"]:
                raise ValueError(f"source size changed after plan: {source}")
            if stat.st_mtime_ns != operation["source_mtime_ns"]:
                raise ValueError(f"source mtime changed after plan: {source}")
            if not _content_matches(source, operation):
                raise ValueError(f"source content changed after plan: {source}")
            if temp.exists():
                raise FileExistsError(f"temporary path exists: {temp}")
            if target.exists() and operation["target"].casefold() not in source_keys:
                raise FileExistsError(f"target would be overwritten: {target}")
        elif state == "staged":
            if not _content_matches(temp, operation):
                raise ValueError(f"staged temporary file invalid: {temp}")
        elif state == "committed":
            if not _content_matches(target, operation):
                raise ValueError(f"committed target invalid: {target}")
        else:
            raise ValueError(f"unsupported checkpoint operation state: {state}")

    # Re-scan live same-stem candidates so a newly appeared companion cannot be
    # silently split from the reviewed logical unit.
    manifest_sources = {item["src"].casefold(): item for item in operations}
    checked: set[tuple[str, str]] = set()
    for operation in operations:
        source = Path(operation["src"])
        key = (_slash(source.parent).casefold(), source.stem.casefold())
        if key in checked:
            continue
        checked.add(key)
        siblings = [
            path for path in source.parent.iterdir()
            if path.is_file()
            and path.stem.casefold() == source.stem.casefold()
            and path.suffix.casefold() in IMG_EXTS
            and not path.name.startswith(TMP_PREFIX)
        ]
        suffixes = {path.suffix.casefold() for path in siblings}
        if not (suffixes & STILL_EXTS and suffixes & VIDEO_EXTS):
            continue
        reviewed = [manifest_sources.get(_slash(path).casefold()) for path in siblings]
        if any(item is None for item in reviewed):
            raise ValueError("unreviewed same-stem image/video companion appeared")
        unit_ids = {item["unit_id"] for item in reviewed if item}
        target_bases = {
            Path(item["target"]).stem.casefold() for item in reviewed if item
        }
        if len(unit_ids) != 1 or len(target_bases) != 1:
            raise ValueError("same-stem image/video unit is not atomic in manifest")


def rollback_checkpoint(
    manifest: dict[str, Any],
    checkpoint: dict[str, Any],
    *,
    checkpoint_path: Path,
) -> dict[str, int]:
    """Return every rename operation to its reviewed source path without overwrite."""

    checkpoint["status"] = "rollback"
    _write_checkpoint(checkpoint_path, checkpoint)
    operations = [
        item for item in manifest["operations"] if item["action"] == "rename"
    ]
    states = checkpoint["op_states"]
    restored = 0

    try:
        # First evacuate committed targets back to their unique temp paths.  This
        # makes cycles/swaps safe before any original source path is restored.
        for operation in reversed(operations):
            if states[operation["op_id"]] != "committed":
                continue
            target = Path(operation["target"])
            temp = Path(operation["temp"])
            if not _content_matches(target, operation) or temp.exists():
                raise ValueError(f"cannot stage committed target for rollback: {target}")
            _write_intent(
                checkpoint_path,
                checkpoint,
                operation=operation,
                transition="rollback_target_to_temp",
                source=target,
                target=temp,
            )
            _rename_no_overwrite(target, temp)
            if not _content_matches(temp, operation):
                raise OSError(f"rollback staging readback failed: {target} -> {temp}")
            states[operation["op_id"]] = "staged"
            checkpoint["intent"] = None
            _write_checkpoint(checkpoint_path, checkpoint)

        for operation in reversed(operations):
            state = states[operation["op_id"]]
            source = Path(operation["src"])
            temp = Path(operation["temp"])
            if state == "planned":
                if not _content_matches(source, operation):
                    raise ValueError(f"planned source missing during rollback: {source}")
                continue
            if state != "staged" or not _content_matches(temp, operation) or source.exists():
                raise ValueError(f"cannot restore staged source: {source}")
            _write_intent(
                checkpoint_path,
                checkpoint,
                operation=operation,
                transition="rollback_temp_to_source",
                source=temp,
                target=source,
            )
            _rename_no_overwrite(temp, source)
            if not _content_matches(source, operation):
                raise OSError(f"rollback restore readback failed: {temp} -> {source}")
            states[operation["op_id"]] = "planned"
            checkpoint["intent"] = None
            restored += 1
            _write_checkpoint(checkpoint_path, checkpoint)
    except Exception:
        checkpoint["status"] = "rollback_failed"
        _write_checkpoint(checkpoint_path, checkpoint)
        raise

    checkpoint["status"] = "rolled_back"
    _write_checkpoint(checkpoint_path, checkpoint)
    return {"restored": restored, "errors": 0}


def execute_manifest(
    manifest: dict[str, Any],
    *,
    manifest_path: Path,
    checkpoint_path: Path,
) -> dict[str, int]:
    if checkpoint_path.exists():
        checkpoint = _load_checkpoint(
            checkpoint_path, manifest_path=manifest_path, manifest=manifest,
        )
        _reconcile_checkpoint(checkpoint, manifest)
        _write_checkpoint(checkpoint_path, checkpoint)
    else:
        preflight_execution(manifest)
        checkpoint = _checkpoint_template(manifest_path, manifest)
        _write_checkpoint(checkpoint_path, checkpoint)

    preflight_execution(manifest, checkpoint=checkpoint)
    operations = [
        item for item in manifest["operations"] if item["action"] == "rename"
    ]
    states = checkpoint["op_states"]
    staged_now = committed_now = 0

    try:
        checkpoint["status"] = "phase1"
        _write_checkpoint(checkpoint_path, checkpoint)
        for operation in operations:
            if states[operation["op_id"]] != "planned":
                continue
            source = Path(operation["src"])
            temp = Path(operation["temp"])
            _write_intent(
                checkpoint_path,
                checkpoint,
                operation=operation,
                transition="source_to_temp",
                source=source,
                target=temp,
            )
            _rename_no_overwrite(source, temp)
            if source.exists() or not _content_matches(temp, operation):
                raise OSError(f"phase1 readback failed: {source} -> {temp}")
            states[operation["op_id"]] = "staged"
            checkpoint["intent"] = None
            staged_now += 1
            _write_checkpoint(checkpoint_path, checkpoint)

        checkpoint["status"] = "phase1_complete"
        _write_checkpoint(checkpoint_path, checkpoint)
        if any(state not in {"staged", "committed"} for state in states.values()):
            raise ValueError("not all operations reached phase1 staging")

        checkpoint["status"] = "phase2"
        _write_checkpoint(checkpoint_path, checkpoint)
        for operation in operations:
            if states[operation["op_id"]] == "committed":
                continue
            temp = Path(operation["temp"])
            target = Path(operation["target"])
            _write_intent(
                checkpoint_path,
                checkpoint,
                operation=operation,
                transition="temp_to_target",
                source=temp,
                target=target,
            )
            _rename_no_overwrite(temp, target)
            if temp.exists() or not _content_matches(target, operation):
                raise OSError(f"phase2 readback failed: {temp} -> {target}")
            states[operation["op_id"]] = "committed"
            checkpoint["intent"] = None
            committed_now += 1
            _write_checkpoint(checkpoint_path, checkpoint)
    except Exception as execution_error:
        try:
            _reconcile_checkpoint(checkpoint, manifest)
            _write_checkpoint(checkpoint_path, checkpoint)
            rollback_checkpoint(
                manifest, checkpoint, checkpoint_path=checkpoint_path,
            )
        except Exception as rollback_error:
            raise RuntimeError(
                f"rename failed ({execution_error}); rollback also failed ({rollback_error})"
            ) from rollback_error
        raise RuntimeError(
            f"rename failed and was rolled back: {execution_error}"
        ) from execution_error

    checkpoint["status"] = "complete"
    _write_checkpoint(checkpoint_path, checkpoint)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(json.dumps({
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
            "event": "rename_batch_complete",
            "plan_sha256": manifest["plan_sha256"],
            "manifest": _slash(manifest_path),
            "renamed": len(operations),
        }, ensure_ascii=False) + "\n")
    return {
        "renamed": len(operations),
        "staged_now": staged_now,
        "committed_now": committed_now,
        "errors": 0,
    }


def cmd_plan(
    *,
    library: str = DEFAULT_LIB,
    photos_root: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    if library not in LIBRARIES:
        raise ValueError(f"unknown library: {library}")
    root = photos_root or (PHOTOS_PARENT / LIBRARIES[library])
    report = manifest_path or (
        Path(__file__).parent / f"photo_rename_report_{library}.json"
    )
    operations, folders_scanned, leftovers = collect_plan(photos_root=root)
    manifest = build_manifest(
        operations,
        photos_root=root,
        library=library,
        folders_scanned=folders_scanned,
        leftover_tmp_files=leftovers,
    )
    _atomic_write_json(report, manifest)
    print(f"HEIC EXIF support: {'YES' if HEIF_OK else 'NO'}")
    print(f"Folders scanned: {folders_scanned}")
    print(f"Summary: {manifest['summary']}")
    print(f"Manifest status: {manifest['status']}")
    print(f"Plan SHA-256: {manifest['plan_sha256']}")
    print(f"Manifest: {report}")
    return manifest


def _load_confirmed_manifest(
    *,
    manifest_path: Path,
    checkpoint_path: Path,
    confirm_plan_sha256: str,
    require_current_script: bool = True,
) -> dict[str, Any]:
    if _same_path(manifest_path, checkpoint_path):
        raise ValueError("manifest and checkpoint paths must differ")
    if _same_path(manifest_path, LOG_PATH) or _same_path(checkpoint_path, LOG_PATH):
        raise ValueError("manifest/checkpoint path must not equal the rename log")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, require_current_script=require_current_script)
    if manifest["plan_sha256"] != confirm_plan_sha256:
        raise ValueError("--confirm-plan-sha256 does not match manifest")
    reserved = {
        value.casefold()
        for operation in manifest["operations"]
        for value in (operation.get("src"), operation.get("target"), operation.get("temp"))
        if value
    }
    for label, path in (
        ("manifest", manifest_path),
        ("checkpoint", checkpoint_path),
        ("log", LOG_PATH),
    ):
        if _slash(path).casefold() in reserved:
            raise ValueError(f"{label} path conflicts with a rename operation")
    return manifest


def cmd_execute(
    *,
    manifest_path: Path,
    checkpoint_path: Path,
    confirm_plan_sha256: str,
) -> dict[str, int]:
    manifest = _load_confirmed_manifest(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=confirm_plan_sha256,
        require_current_script=True,
    )
    result = execute_manifest(
        manifest, manifest_path=manifest_path, checkpoint_path=checkpoint_path,
    )
    print(f"Rename complete: {result}")
    print(f"Checkpoint: {checkpoint_path}")
    return result


def cmd_rollback(
    *,
    manifest_path: Path,
    checkpoint_path: Path,
    confirm_plan_sha256: str,
) -> dict[str, int]:
    manifest = _load_confirmed_manifest(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=confirm_plan_sha256,
        # A script update must block new execution, but must not strand an
        # already-staged batch that needs its reviewed sources restored.
        require_current_script=False,
    )
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"checkpoint does not exist: {checkpoint_path}")
    checkpoint = _load_checkpoint(
        checkpoint_path, manifest_path=manifest_path, manifest=manifest,
    )
    _reconcile_checkpoint(checkpoint, manifest)
    _write_checkpoint(checkpoint_path, checkpoint)
    result = rollback_checkpoint(
        manifest, checkpoint, checkpoint_path=checkpoint_path,
    )
    print(f"Rollback complete: {result}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    plan = subparsers.add_parser("plan", help="read-only plan (default)")
    plan.add_argument("--library", choices=sorted(LIBRARIES), default=DEFAULT_LIB)
    plan.add_argument("--root", type=Path)
    plan.add_argument("--manifest", type=Path)

    for command in ("execute", "rollback"):
        write = subparsers.add_parser(command)
        write.add_argument("--manifest", type=Path, required=True)
        write.add_argument("--checkpoint", type=Path, required=True)
        write.add_argument("--confirm-plan-sha256", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "plan"
    try:
        if command == "plan":
            cmd_plan(
                library=getattr(args, "library", DEFAULT_LIB),
                photos_root=getattr(args, "root", None),
                manifest_path=getattr(args, "manifest", None),
            )
        elif command == "execute":
            cmd_execute(
                manifest_path=args.manifest,
                checkpoint_path=args.checkpoint,
                confirm_plan_sha256=args.confirm_plan_sha256,
            )
        else:
            cmd_rollback(
                manifest_path=args.manifest,
                checkpoint_path=args.checkpoint,
                confirm_plan_sha256=args.confirm_plan_sha256,
            )
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
