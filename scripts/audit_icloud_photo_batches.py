#!/usr/bin/env python3
"""Read-only audit for overlapping iCloud Photos ZIP batches.

The script hashes every staged file, extracts embedded/filename capture dates,
and hashes only size-matched files from the existing Chenwei library index.
It never copies, moves, renames, or deletes media.  Its only write is the JSON
report requested with --output.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import ExifTags, Image


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif", ".avif", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
PHONE_MAKES = {
    "apple", "samsung", "huawei", "htc", "asus", "google", "xiaomi",
    "oneplus", "oppo", "vivo", "realme", "lge", "lg", "motorola",
}
CAMERA_MAKES = {
    "canon", "nikon", "sony", "fujifilm", "olympus", "panasonic",
    "ricoh", "leica", "pentax", "sigma", "hasselblad", "casio",
    "kodak", "gopro",
}
TZ_TAIPEI = dt.timezone(dt.timedelta(hours=8))
DATE_SOURCE_RANK = {
    "exif_datetime_original": 0,
    "quicktime_apple_creationdate": 1,
    "quicktime_creation_time": 2,
    "exif_datetime_digitized": 3,
    "exif_datetime": 4,
    "live_photo_pair": 5,
    "filename_ymd_hms": 6,
    "filename_ymd": 7,
    "filename_epoch_ms": 8,
    "filename_epoch_s": 9,
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def decode_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        for encoding in ("utf-8", "utf-16", "ascii", "latin-1"):
            try:
                return value.decode(encoding, errors="ignore").strip("\x00 \t\r\n")
            except Exception:
                pass
        return ""
    return str(value).strip("\x00 \t\r\n")


def parse_embedded_datetime(value: Any) -> str | None:
    text = decode_value(value)
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    for fmt in (
        "%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S",
        "%Y:%m:%d", "%Y-%m-%d",
    ):
        try:
            parsed = dt.datetime.strptime(text[:19], fmt)
            return parsed.isoformat(timespec="seconds")
        except ValueError:
            pass
    try:
        parsed = dt.datetime.fromisoformat(normalized)
        return parsed.isoformat(timespec="seconds")
    except ValueError:
        return None


def parse_filename_datetime(name: str) -> tuple[str | None, str | None]:
    stem = Path(name).stem
    epoch_ms = re.search(r"(?<!\d)(1[0-9]{12})(?!\d)", stem)
    if epoch_ms:
        try:
            parsed = dt.datetime.fromtimestamp(int(epoch_ms.group(1)) / 1000, tz=dt.timezone.utc).astimezone(TZ_TAIPEI)
            if 2000 <= parsed.year <= 2035:
                return parsed.isoformat(timespec="seconds"), "filename_epoch_ms"
        except (OverflowError, OSError, ValueError):
            pass

    epoch_s = re.search(r"(?<!\d)(1[0-9]{9})(?!\d)", stem)
    if epoch_s:
        try:
            parsed = dt.datetime.fromtimestamp(int(epoch_s.group(1)), tz=dt.timezone.utc).astimezone(TZ_TAIPEI)
            if 2000 <= parsed.year <= 2035:
                return parsed.isoformat(timespec="seconds"), "filename_epoch_s"
        except (OverflowError, OSError, ValueError):
            pass

    match = re.search(
        r"(?<!\d)(20\d{2})[-_. ]?(0[1-9]|1[0-2])[-_. ]?(0[1-9]|[12]\d|3[01])"
        r"(?:[-_ T]?([01]\d|2[0-3])[-_.:]?([0-5]\d)[-_.:]?([0-5]\d))?(?!\d)",
        stem,
    )
    if match:
        try:
            parts = [int(match.group(i) or 0) for i in range(1, 7)]
            parsed = dt.datetime(*parts)
            source = "filename_ymd_hms" if match.group(4) else "filename_ymd"
            return parsed.isoformat(timespec="seconds"), source
        except ValueError:
            pass
    return None, None


def image_metadata(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "detected_type": "image",
        "format": None,
        "width": None,
        "height": None,
        "make": None,
        "model": None,
        "software": None,
        "user_comment": None,
        "embedded_date_candidates": [],
        "metadata_error": None,
        "pillow_error": None,
        "container_brand": None,
        "extension_content_mismatch": False,
    }
    try:
        with Image.open(path) as image:
            result["format"] = image.format
            result["width"], result["height"] = image.size
            # _getexif() flattens the Exif sub-IFD.  getexif().items() alone
            # omits DateTimeOriginal/DateTimeDigitized on ordinary JPEG files.
            raw = image._getexif() if hasattr(image, "_getexif") else image.getexif()
            named = {ExifTags.TAGS.get(key, str(key)): value for key, value in (raw or {}).items()}
            result["make"] = decode_value(named.get("Make")) or None
            result["model"] = decode_value(named.get("Model")) or None
            result["software"] = decode_value(named.get("Software")) or None
            result["user_comment"] = decode_value(named.get("UserComment")) or None
            for tag, source in (
                ("DateTimeOriginal", "exif_datetime_original"),
                ("DateTimeDigitized", "exif_datetime_digitized"),
                ("DateTime", "exif_datetime"),
            ):
                parsed = parse_embedded_datetime(named.get(tag))
                if parsed:
                    result["embedded_date_candidates"].append({"value": parsed, "source": source, "raw": decode_value(named.get(tag))})
    except Exception as exc:
        # iCloud occasionally gives HEIC still images a .JPG filename. Pillow
        # cannot open those on this host, but ffprobe identifies the HEIC
        # container reliably. Treat that as a format mismatch, not corruption.
        pillow_error = f"{type(exc).__name__}: {exc}"
        fallback = video_metadata(path)
        brand = (fallback.get("container_brand") or "").casefold()
        if not fallback.get("metadata_error") and brand in {"heic", "heix", "hevc", "mif1", "avif"}:
            result.update(fallback)
            result["detected_type"] = "image"
            result["format"] = "HEIC" if brand in {"heic", "heix", "hevc", "mif1"} else "AVIF"
            result["metadata_error"] = None
            result["pillow_error"] = pillow_error
            result["extension_content_mismatch"] = True
        else:
            result["metadata_error"] = pillow_error
            result["pillow_error"] = pillow_error
    return result


def video_metadata(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "detected_type": "video",
        "format": None,
        "width": None,
        "height": None,
        "make": None,
        "model": None,
        "software": None,
        "user_comment": None,
        "embedded_date_candidates": [],
        "metadata_error": None,
        "pillow_error": None,
        "container_brand": None,
        "extension_content_mismatch": False,
    }
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        if proc.returncode != 0:
            result["metadata_error"] = f"ffprobe exit {proc.returncode}: {proc.stderr.strip()[:500]}"
            return result
        payload = json.loads(proc.stdout or "{}")
        fmt = payload.get("format") or {}
        result["format"] = fmt.get("format_name")
        format_tags = {str(k).lower(): v for k, v in (fmt.get("tags") or {}).items()}
        result["container_brand"] = decode_value(format_tags.get("major_brand")) or None
        streams = payload.get("streams") or []
        video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
        if video_stream:
            result["width"] = video_stream.get("width")
            result["height"] = video_stream.get("height")
        all_tags = dict(format_tags)
        for stream in streams:
            for key, value in (stream.get("tags") or {}).items():
                all_tags.setdefault(str(key).lower(), value)
        result["make"] = decode_value(all_tags.get("com.apple.quicktime.make") or all_tags.get("make")) or None
        result["model"] = decode_value(all_tags.get("com.apple.quicktime.model") or all_tags.get("model")) or None
        result["software"] = decode_value(all_tags.get("com.apple.quicktime.software") or all_tags.get("encoder")) or None

        apple_date = all_tags.get("com.apple.quicktime.creationdate")
        parsed = parse_embedded_datetime(apple_date)
        if parsed:
            result["embedded_date_candidates"].append({"value": parsed, "source": "quicktime_apple_creationdate", "raw": decode_value(apple_date)})
        creation_values: list[Any] = []
        if "creation_time" in format_tags:
            creation_values.append(format_tags["creation_time"])
        creation_values.extend(
            (stream.get("tags") or {}).get("creation_time")
            for stream in streams
            if (stream.get("tags") or {}).get("creation_time")
        )
        for value in creation_values:
            parsed = parse_embedded_datetime(value)
            if parsed and not any(item["value"] == parsed for item in result["embedded_date_candidates"]):
                result["embedded_date_candidates"].append({"value": parsed, "source": "quicktime_creation_time", "raw": decode_value(value)})
    except Exception as exc:
        result["metadata_error"] = f"{type(exc).__name__}: {exc}"
    return result


def best_date(metadata: dict[str, Any], name: str) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    candidates = list(metadata.get("embedded_date_candidates") or [])
    filename_value, filename_source = parse_filename_datetime(name)
    if filename_value:
        candidates.append({"value": filename_value, "source": filename_source, "raw": name})
    candidates.sort(key=lambda item: DATE_SOURCE_RANK.get(item["source"], 999))
    if not candidates:
        return None, None, []
    return candidates[0]["value"], candidates[0]["source"], candidates


def library_relpath(year: str, bucket: str, name: str) -> str:
    segments = PurePosixPath(bucket).parts
    first = segments[0] if segments else ""
    if re.fullmatch(r"0[1-9]|1[0-2]", first):
        parts = [f"{year}相片", f"{year}.{first}", *segments[1:], name]
    elif first == "screenshots":
        parts = [f"{year}相片", f"{year}截圖", *segments[1:], name]
    elif first == "downloads":
        parts = [f"{year}相片", f"{year}下載", *segments[1:], name]
    else:
        parts = [f"{year}相片", *segments, name]
    return PurePosixPath(*parts).as_posix()


def enumerate_library(index_path: Path, root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    index = json.loads(index_path.read_text(encoding="utf-8"))
    chenwei = index["libraries"]["chenwei"]
    entries: list[dict[str, Any]] = []
    for year, year_data in chenwei["years"].items():
        for bucket, files in (year_data.get("buckets") or {}).items():
            for item in files:
                relpath = library_relpath(year, bucket, item["name"])
                entries.append({
                    "year": year,
                    "bucket": bucket,
                    "name": item["name"],
                    "relpath": relpath,
                    "path": str(root / Path(*PurePosixPath(relpath).parts)),
                    "size": int(item["size"]),
                    "mtime_ms": item.get("mtime"),
                })
    return index, entries


def filename_quality(name: str) -> tuple[int, str]:
    stem = Path(name).stem
    if re.fullmatch(r"[0-9A-Fa-f]{32,64}", stem) or re.fullmatch(r"[0-9A-Fa-f-]{36}", stem):
        return 3, name.casefold()
    if ".mp4video" in name.casefold():
        return 2, name.casefold()
    if re.match(r"(?i)^(IMG|DSC|PXL|MVIMG|VID|Screenshot|FB_IMG)[_-]", stem):
        return 0, name.casefold()
    return 1, name.casefold()


def classify_record(record: dict[str, Any]) -> dict[str, Any]:
    ext = record["ext"]
    name = record["name"]
    lower = name.casefold()
    meta = record["metadata"]
    make = (meta.get("make") or "").casefold()
    model = (meta.get("model") or "").casefold()
    user_comment = (meta.get("user_comment") or "").casefold()
    width = meta.get("width") or 0
    height = meta.get("height") or 0
    ratio = max(width, height) / min(width, height) if width and height else None
    reliable_date = record.get("captured_at") is not None

    category = "review"
    confidence = "low"
    reason = "insufficient metadata to distinguish a downloaded photograph from a graphic"
    visual_review = True

    if "screenshot" in lower or "screen_shot" in lower or "screen shot" in lower or "screenshot" in user_comment:
        category, confidence, reason, visual_review = "screenshot", "high", "filename or EXIF explicitly says Screenshot", False
    elif record.get("live_photo_pair"):
        category, confidence, reason, visual_review = "photo", "high", "paired still/video Live Photo basename", False
    elif make in PHONE_MAKES or make in CAMERA_MAKES or make == "sony":
        category, confidence, reason, visual_review = "photo", "high", f"embedded camera make={make}", False
    elif meta.get("embedded_date_candidates") and ext in IMAGE_EXTS | VIDEO_EXTS:
        category, confidence, reason, visual_review = "photo", "high", "embedded EXIF/QuickTime capture date", False
    elif ext in VIDEO_EXTS:
        category = "photo"
        confidence = "medium" if reliable_date else "low"
        reason = "video media; no evidence it is a downloaded graphic"
        visual_review = not reliable_date
    elif ext == ".png":
        if ratio is not None and 1.55 <= ratio <= 2.5 and min(width, height) <= 1500:
            category, confidence = "screenshot", "medium"
            reason = f"PNG with phone-screen aspect ratio {ratio:.2f} at {width}x{height}"
        else:
            category, confidence = "review", "low"
            reason = f"PNG without explicit screenshot/camera metadata at {width}x{height}"
        visual_review = True
    elif ext in {".jpg", ".jpeg"} and re.match(r"(?i)^_?DSC[_-]?\d+", Path(name).stem):
        category, confidence, reason, visual_review = "photo", "medium", "camera-style DSC filename", False
    elif ext in {".jpg", ".jpeg"} and re.match(r"(?i)^IMG[_-]?\d+", Path(name).stem):
        category, confidence, reason, visual_review = "photo", "medium", "phone/camera-style IMG filename", False
    elif ext in {".jpg", ".jpeg"}:
        category, confidence = "photo", "low"
        reason = "JPEG treated as a photograph candidate; visual review needed because camera metadata is absent"
        visual_review = True

    date_value = record.get("captured_at")
    target_relpath = None
    target_exists = None
    date_year = date_month = None
    if date_value:
        date_year, date_month = date_value[:4], date_value[5:7]
        if category == "photo":
            target_relpath = f"{date_year}相片/{date_year}.{date_month}"
        elif category == "screenshot":
            target_relpath = f"{date_year}相片/{date_year}截圖"
        elif category == "download":
            target_relpath = f"{date_year}相片/{date_year}下載"

    return {
        "recommended_category": category,
        "classification_confidence": confidence,
        "classification_reason": reason,
        "visual_review_required": visual_review,
        "reliable_date_available": reliable_date,
        "date_year": date_year,
        "date_month": date_month,
        "target_folder_candidate": target_relpath,
        "target_folder_exists": target_exists,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", action="append", nargs=2, metavar=("ID", "PATH"), required=True)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--library-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-archive", action="append", nargs=3, metavar=("ID", "PATH", "SHA256"), default=[])
    args = parser.parse_args()

    batch_roots = {batch_id: Path(path) for batch_id, path in args.batch}
    archive_info = {
        batch_id: {"path": path, "sha256": sha}
        for batch_id, path, sha in args.batch_archive
    }
    records: list[dict[str, Any]] = []
    batch_summary: dict[str, dict[str, Any]] = {}
    print("Hashing staged iCloud files...", flush=True)
    for batch_id, root in batch_roots.items():
        paths = sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.as_posix().casefold())
        extension_counts = Counter()
        total_bytes = 0
        for index, path in enumerate(paths, 1):
            stat = path.stat()
            digest = sha256_file(path)
            ext = path.suffix.casefold()
            extension_counts[ext or "<none>"] += 1
            total_bytes += stat.st_size
            records.append({
                "batch_id": batch_id,
                "path": str(path),
                "relpath": path.relative_to(root).as_posix(),
                "name": path.name,
                "ext": ext,
                "size": stat.st_size,
                "sha256": digest,
                "packaging_mtime": dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc).astimezone().isoformat(timespec="seconds"),
                "packaging_mtime_used_as_capture_date": False,
            })
            if index % 200 == 0:
                print(f"  {batch_id}: {index}/{len(paths)}", flush=True)
        batch_summary[batch_id] = {
            "root": str(root),
            "files": len(paths),
            "bytes": total_bytes,
            "extensions": dict(sorted(extension_counts.items())),
            "archive": archive_info.get(batch_id),
        }

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["sha256"]].append(record)

    print(f"Extracting metadata for {len(groups)} unique byte streams...", flush=True)
    metadata_cache: dict[str, dict[str, Any]] = {}
    for index, (digest, members) in enumerate(groups.items(), 1):
        sample_path = Path(members[0]["path"])
        ext = members[0]["ext"]
        if ext in IMAGE_EXTS:
            metadata_cache[digest] = image_metadata(sample_path)
        elif ext in VIDEO_EXTS:
            metadata_cache[digest] = video_metadata(sample_path)
        else:
            metadata_cache[digest] = {
                "detected_type": "other", "format": None, "width": None, "height": None,
                "make": None, "model": None, "software": None, "user_comment": None,
                "embedded_date_candidates": [], "metadata_error": "unsupported extension",
                "pillow_error": None, "container_brand": None,
                "extension_content_mismatch": False,
            }
        if index % 250 == 0:
            print(f"  metadata: {index}/{len(groups)}", flush=True)

    for record in records:
        record["metadata"] = copy.deepcopy(metadata_cache[record["sha256"]])
        captured_at, captured_source, candidates = best_date(record["metadata"], record["name"])
        record["captured_at"] = captured_at
        record["capture_date_source"] = captured_source
        record["date_candidates"] = candidates
        record["live_photo_pair"] = False

    pair_map: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        pair_map[(record["batch_id"], Path(record["name"]).stem.casefold())].append(record)
    for members in pair_map.values():
        has_image = any(item["ext"] in IMAGE_EXTS for item in members)
        has_video = any(item["ext"] in VIDEO_EXTS for item in members)
        if not (has_image and has_video):
            continue
        dated = sorted(
            (item for item in members if item.get("captured_at")),
            key=lambda item: DATE_SOURCE_RANK.get(item.get("capture_date_source"), 999),
        )
        for item in members:
            item["live_photo_pair"] = True
            if not item.get("captured_at") and dated:
                item["captured_at"] = dated[0]["captured_at"]
                item["capture_date_source"] = "live_photo_pair"
                item["date_candidates"].append({
                    "value": dated[0]["captured_at"],
                    "source": "live_photo_pair",
                    "raw": dated[0]["name"],
                })

    for record in records:
        record["classification"] = classify_record(record)
        target = record["classification"].get("target_folder_candidate")
        if target:
            target_path = args.library_root / Path(*PurePosixPath(target).parts)
            record["classification"]["target_folder_exists"] = target_path.is_dir()

    staging_sizes = set(record["size"] for record in records)
    photo_index, library_entries = enumerate_library(args.index, args.library_root)
    library_candidates = [entry for entry in library_entries if entry["size"] in staging_sizes]
    print(f"Hashing {len(library_candidates)} size-matched library candidates (not the whole library)...", flush=True)
    library_errors: list[dict[str, Any]] = []
    library_by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, entry in enumerate(library_candidates, 1):
        path = Path(entry["path"])
        try:
            if not path.is_file():
                raise FileNotFoundError(path)
            digest = sha256_file(path)
            clean = {key: value for key, value in entry.items() if key != "path"}
            clean["sha256"] = digest
            library_by_hash[digest].append(clean)
        except Exception as exc:
            library_errors.append({"relpath": entry["relpath"], "error": f"{type(exc).__name__}: {exc}"})
        if index % 100 == 0:
            print(f"  library candidates: {index}/{len(library_candidates)}", flush=True)

    batch_ids = list(batch_roots)
    content_groups: list[dict[str, Any]] = []
    keep_candidates: list[dict[str, Any]] = []
    skip_candidates: list[dict[str, Any]] = []
    for digest, members in sorted(groups.items(), key=lambda item: (min(member["batch_id"] for member in item[1]), min(member["relpath"].casefold() for member in item[1]))):
        present_batches = sorted({member["batch_id"] for member in members})
        canonical = sorted(
            members,
            key=lambda item: (batch_ids.index(item["batch_id"]), *filename_quality(item["name"]), item["relpath"].casefold()),
        )[0]
        existing = library_by_hash.get(digest, [])
        if existing:
            disposition = "skip_existing_library_exact_match"
            for member in members:
                member["disposition"] = disposition
                member["duplicate_of"] = existing[0]["relpath"]
                skip_candidates.append({
                    "batch_id": member["batch_id"], "relpath": member["relpath"], "sha256": digest,
                    "reason": disposition, "duplicate_of": existing[0]["relpath"],
                })
        else:
            disposition = "keep_one_new_content"
            for member in members:
                if member is canonical:
                    member["disposition"] = disposition
                    member["duplicate_of"] = None
                else:
                    member["disposition"] = "skip_staged_exact_duplicate"
                    member["duplicate_of"] = f"{canonical['batch_id']}:{canonical['relpath']}"
                    skip_candidates.append({
                        "batch_id": member["batch_id"], "relpath": member["relpath"], "sha256": digest,
                        "reason": "skip_staged_exact_duplicate", "duplicate_of": member["duplicate_of"],
                    })
            keep_candidates.append({
                "batch_id": canonical["batch_id"],
                "relpath": canonical["relpath"],
                "path": canonical["path"],
                "name": canonical["name"],
                "ext": canonical["ext"],
                "size": canonical["size"],
                "sha256": digest,
                "source_batches": present_batches,
                "staged_exact_duplicate_records": len(members) - 1,
                "captured_at": canonical["captured_at"],
                "capture_date_source": canonical["capture_date_source"],
                "classification": canonical["classification"],
            })

        content_groups.append({
            "sha256": digest,
            "size": members[0]["size"],
            "source_batches": present_batches,
            "source_members": [
                {
                    "batch_id": member["batch_id"],
                    "relpath": member["relpath"],
                    "name": member["name"],
                    "disposition": member["disposition"],
                    "duplicate_of": member["duplicate_of"],
                }
                for member in members
            ],
            "cross_batch_exact_duplicate": len(present_batches) > 1,
            "within_batch_exact_duplicate": any(sum(1 for member in members if member["batch_id"] == batch_id) > 1 for batch_id in batch_ids),
            "canonical_source": {"batch_id": canonical["batch_id"], "relpath": canonical["relpath"]},
            "library_exact_matches": existing,
            "disposition": disposition,
        })

    within_summary: dict[str, Any] = {}
    for batch_id in batch_ids:
        duplicate_groups = [
            members for members in groups.values()
            if sum(1 for member in members if member["batch_id"] == batch_id) > 1
        ]
        within_summary[batch_id] = {
            "duplicate_content_groups": len(duplicate_groups),
            "redundant_file_records": sum(
                sum(1 for member in members if member["batch_id"] == batch_id) - 1
                for members in duplicate_groups
            ),
        }

    cross_groups = [members for members in groups.values() if len({member["batch_id"] for member in members}) > 1]
    library_matched_groups = [digest for digest in groups if library_by_hash.get(digest)]
    unique_hashes_by_batch = {
        batch_id: {record["sha256"] for record in records if record["batch_id"] == batch_id}
        for batch_id in batch_ids
    }
    capture_source_counts = Counter(record.get("capture_date_source") or "missing" for record in records)
    unique_capture_source_counts = Counter()
    for members in groups.values():
        best = sorted(
            members,
            key=lambda item: DATE_SOURCE_RANK.get(item.get("capture_date_source"), 999),
        )[0]
        unique_capture_source_counts[best.get("capture_date_source") or "missing"] += 1
    classification_counts = Counter(candidate["classification"]["recommended_category"] for candidate in keep_candidates)

    report = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "mode": "read_only_audit",
        "rules": {
            "packaging_mtime_is_not_capture_date": True,
            "capture_date_priority": list(DATE_SOURCE_RANK),
            "exact_duplicate_definition": "same SHA-256 bytes",
            "cross_batch_keep_preference": "batch argument order; batch1 is treated as earlier download",
            "within_batch_download_order": "unknown; canonical choice uses stable filename quality then lexical order",
            "downloaded_photographs": "recommend photo folders when photo evidence exists; ambiguous graphics require visual review",
            "new_drive_folders_allowed": False,
            "media_mutations_performed": False,
        },
        "batches": batch_summary,
        "library_snapshot": {
            "root": str(args.library_root),
            "index": str(args.index),
            "index_generated_at": photo_index.get("generatedAt"),
            "index_reported_total_files": photo_index["libraries"]["chenwei"].get("totalFiles"),
            "index_entries_enumerated": len(library_entries),
            "size_matched_candidates_hashed": len(library_candidates),
            "hash_errors": library_errors,
        },
        "summary": {
            "source_file_records": len(records),
            "source_bytes": sum(record["size"] for record in records),
            "unique_content_sha256": len(groups),
            "unique_contents_by_batch": {
                batch_id: len(hashes) for batch_id, hashes in unique_hashes_by_batch.items()
            },
            "exclusive_unique_contents_by_batch": {
                batch_id: len(hashes - set().union(*(other for other_id, other in unique_hashes_by_batch.items() if other_id != batch_id)))
                for batch_id, hashes in unique_hashes_by_batch.items()
            },
            "within_batch_exact_duplicates": within_summary,
            "cross_batch_overlap_unique_contents": len(cross_groups),
            "cross_batch_overlap_file_records": sum(len(members) for members in cross_groups),
            "cross_batch_overlap_records_by_batch": {
                batch_id: sum(1 for members in cross_groups for member in members if member["batch_id"] == batch_id)
                for batch_id in batch_ids
            },
            "existing_library_exact_match_unique_contents": len(library_matched_groups),
            "existing_library_exact_match_source_records": sum(len(groups[digest]) for digest in library_matched_groups),
            "new_unique_contents_to_keep": len(keep_candidates),
            "source_records_to_skip": len(skip_candidates),
            "capture_date_source_counts_all_records": dict(sorted(capture_source_counts.items())),
            "capture_date_source_counts_unique_content": dict(sorted(unique_capture_source_counts.items())),
            "unique_content_without_reliable_date": unique_capture_source_counts.get("missing", 0),
            "keep_candidate_classification_counts": dict(sorted(classification_counts.items())),
            "keep_candidates_requiring_visual_review": sum(
                1 for item in keep_candidates if item["classification"]["visual_review_required"]
            ),
            "keep_candidates_without_reliable_date": sum(
                1 for item in keep_candidates if not item["classification"]["reliable_date_available"]
            ),
            "keep_candidates_target_folder_missing": sum(
                1 for item in keep_candidates
                if item["classification"]["target_folder_candidate"]
                and item["classification"]["target_folder_exists"] is False
            ),
            "metadata_errors_all_records": sum(1 for record in records if record["metadata"].get("metadata_error")),
            "extension_content_mismatch_source_records": sum(
                1 for record in records if record["metadata"].get("extension_content_mismatch")
            ),
            "extension_content_mismatch_unique_contents": sum(
                1 for digest in groups if metadata_cache[digest].get("extension_content_mismatch")
            ),
        },
        "keep_candidates": keep_candidates,
        "skip_candidates": skip_candidates,
        "content_groups": content_groups,
        "source_records": records,
        "warnings": [
            "ZIP/extraction mtimes are recorded for provenance only and were never used as capture dates.",
            "SHA-256 proves byte-identical duplicates only; visually identical recompressions/crops are outside this report.",
            "Ambiguous PNG/JPEG files without decisive metadata are flagged for visual review rather than forced into Downloads.",
            "HEIC containers mislabeled with .JPG extensions are explicitly flagged; import must correct or convert them.",
            "No media file or Drive folder was created, copied, moved, renamed, or deleted by this audit.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = args.output.with_suffix(args.output.suffix + ".tmp")
    temp_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp_output, args.output)
    print(f"Report written: {args.output}", flush=True)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
