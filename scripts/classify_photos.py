#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""辰瑋相片保守分類器。

本工具採 fail-closed 規則。只有 EXIF 同時提供可信的實體拍攝裝置
``Make`` + ``Model``，以及可解析的 ``DateTimeOriginal`` 或
``DateTimeDigitized``，檔案才有資格進入年月資料夾。其餘檔案一律規劃到
下載；只有檔名或 EXIF 明確寫出 Screenshot/截圖時才規劃到截圖。

HEIC、IMG_ 前綴、檔名中的日期、像素尺寸、mtime、目前所在資料夾和目前
檔名都不是「實拍照片」的證據。

預設只產生 plan manifest：

    python scripts/classify_photos.py
    python scripts/classify_photos.py plan --manifest <manifest.json>

執行搬移必須明確提供經審閱的 manifest、checkpoint 和 manifest 顯示的
SHA-256；工具不建立分類目標資料夾、不覆寫，也不處理可能被拆散的同 stem
影像/影片組：

    python scripts/classify_photos.py execute \
        --manifest <manifest.json> \
        --checkpoint <checkpoint.json> \
        --confirm-plan-sha256 <sha256>
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from PIL import ExifTags, Image


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


PHOTOS_ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/照片/辰瑋相片")
REPORT_PATH = Path(__file__).parent / "photo_classification_report.json"
MOVE_LOG_PATH = Path(__file__).parent / "photo_move_log.jsonl"

MANIFEST_SCHEMA = "chenwei-photo-classification-manifest/v2"
CHECKPOINT_SCHEMA = "chenwei-photo-classification-checkpoint/v1"
POLICY_VERSION = "physical-device-exif-fail-closed/v1"

IMG_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif",
    ".avif", ".bmp", ".mp4", ".mov", ".m4v", ".webm", ".mkv",
}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
STILL_IMAGE_EXTS = IMG_EXTS - VIDEO_EXTS

# These are physical-device manufacturers, not a generic "non-empty Make"
# allow rule.  Every accepted maker also requires a non-placeholder Model.
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

# Editing/camera apps sometimes write themselves into Make or Model.  They do
# not prove a physical capture device, even when a date tag is present.
APP_METADATA_MARKERS = (
    "snowcorp", "snow corporation", "foodie", "b612", "beautyplus",
    "meitu", "picsart", "vsco", "snapseed", "line camera", "instagram",
    "facebook", "adobe photoshop", "photoshop camera", "canva",
)
MODEL_PLACEHOLDERS = {
    "", "unknown", "none", "n/a", "na", "null", "camera", "digital camera",
    "smartphone", "phone", "mobile", "ios", "android",
}

EXPLICIT_SCREENSHOT_PREFIXES = (
    "screenshot", "screen_shot", "screen shot", "screen-shot",
)


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


def _normalise_metadata_text(value: Any) -> str:
    return re.sub(r"\s+", " ", _decode_text(value).casefold()).strip()


def read_exif(img_path: Path) -> tuple[dict[str, Any], int, int, str | None]:
    """Return named EXIF plus dimensions/format.

    Dimensions and format are exposed for reporting compatibility only.  The
    classifier deliberately never uses them as evidence of a camera photo or
    screenshot.
    """

    try:
        with Image.open(img_path) as img:
            width, height = img.size
            image_format = img.format
            raw = img._getexif() if hasattr(img, "_getexif") else None
            named = {
                ExifTags.TAGS.get(key, key): value
                for key, value in (raw or {}).items()
            }
            return named, width, height, image_format
    except Exception:
        return {}, 0, 0, None


def parse_exif_datetime(value: Any) -> dt.datetime | None:
    """Parse an EXIF capture date, returning None for invalid values."""

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
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def extract_trusted_capture_time(
    exif: dict[str, Any],
) -> tuple[dt.datetime | None, str | None]:
    """Use only original/digitized EXIF tags; never filename/mtime/DateTime."""

    for tag in ("DateTimeOriginal", "DateTimeDigitized"):
        parsed = parse_exif_datetime(exif.get(tag))
        if parsed is not None:
            return parsed, tag
    return None, None


def trusted_device_kind(make_value: Any, model_value: Any) -> str | None:
    """Return phone/camera only for an explicit physical Make + Model pair."""

    make = _normalise_metadata_text(make_value)
    model = _normalise_metadata_text(model_value)
    if not make or not model or model in MODEL_PLACEHOLDERS:
        return None

    combined = f"{make} {model}"
    if any(marker in combined for marker in APP_METADATA_MARKERS):
        return None

    if make == "apple" or make.startswith("apple "):
        # Apple + a generic software/platform Model is not enough.
        if re.search(r"\b(?:iphone|ipad)\b", model):
            return "phone"
        return None

    if make == "sony" or make.startswith("sony "):
        if any(hint in model for hint in SONY_PHONE_MODEL_HINTS):
            return "phone"
        return "camera"

    if any(make == prefix or make.startswith(prefix + " ")
           for prefix in PHONE_MAKE_PREFIXES):
        return "phone"
    if any(make == prefix or make.startswith(prefix + " ")
           for prefix in CAMERA_MAKE_PREFIXES):
        return "camera"
    return None


def _has_app_authored_metadata(exif: dict[str, Any]) -> bool:
    """Reject app identities only when Make/Model themselves impersonate hardware.

    Export/edit ``Software`` such as Instagram or Foodie does not erase otherwise
    valid physical Make+Model plus original capture-time evidence.
    """

    fields = ("Make", "Model")
    combined = " ".join(_normalise_metadata_text(exif.get(field)) for field in fields)
    return any(marker in combined for marker in APP_METADATA_MARKERS)


def _explicit_screenshot_reason(name: str, exif: dict[str, Any]) -> str | None:
    lower_name = name.casefold()
    if lower_name.startswith(EXPLICIT_SCREENSHOT_PREFIXES):
        return "filename explicitly starts with Screenshot"
    if "截圖" in name or "螢幕截圖" in name:
        return "filename explicitly contains 截圖"

    user_comment = _normalise_metadata_text(exif.get("UserComment"))
    if ("screenshot" in user_comment or "screen shot" in user_comment
            or "截圖" in user_comment):
        return "EXIF UserComment explicitly says Screenshot"
    return None


def classify_from_exif(file_path: Path, exif: dict[str, Any]) -> dict[str, Any]:
    """Pure evidence classifier used by :func:`classify` and regression tests."""

    make = _decode_text(exif.get("Make"))
    model = _decode_text(exif.get("Model"))
    captured, captured_source = extract_trusted_capture_time(exif)
    captured_iso = captured.isoformat() if captured else None

    screenshot_reason = _explicit_screenshot_reason(file_path.name, exif)
    if screenshot_reason:
        return {
            "kind": "screenshot",
            "captured": captured_iso,
            "captured_source": captured_source,
            "confidence": "high",
            "reason": screenshot_reason,
            "make": make or None,
            "model": model or None,
            "photo_qualified": False,
        }

    device_kind = trusted_device_kind(make, model)
    if _has_app_authored_metadata(exif):
        device_kind = None
    if device_kind and captured:
        return {
            "kind": device_kind,
            "captured": captured_iso,
            "captured_source": captured_source,
            "confidence": "high",
            "reason": (
                f"trusted physical device Make={make}, Model={model}; "
                f"capture time from EXIF {captured_source}"
            ),
            "make": make,
            "model": model,
            "photo_qualified": True,
        }

    if device_kind:
        reason = (
            "trusted physical Make+Model but no parseable "
            "DateTimeOriginal/DateTimeDigitized; fail-closed to download"
        )
    elif make or model:
        reason = (
            "Make+Model is incomplete, app-authored, placeholder, or not on the "
            "physical-device allowlist; fail-closed to download"
        )
    else:
        reason = (
            "no trusted physical Make+Model; extension, filename, dimensions and "
            "mtime are intentionally ignored; fail-closed to download"
        )
    return {
        "kind": "download",
        "captured": captured_iso,
        "captured_source": captured_source,
        "confidence": "conservative",
        "reason": reason,
        "make": make or None,
        "model": model or None,
        "photo_qualified": False,
    }


def classify(file_path: Path) -> dict[str, Any]:
    exif, _width, _height, _format = read_exif(file_path)
    return classify_from_exif(file_path, exif)


def _parse_year_folder(year_folder: str) -> str:
    match = re.fullmatch(r"(\d{4})相片", year_folder)
    if not match:
        raise ValueError(f"invalid year folder: {year_folder}")
    return match.group(1)


def plan_target(
    file_path: Path,
    year_folder: str,
    info: dict[str, Any],
    *,
    photos_root: Path = PHOTOS_ROOT,
) -> tuple[Path, str]:
    """Return a target directory without treating current location as evidence."""

    del file_path  # Filename/current folder must not influence classification.
    folder_year = _parse_year_folder(year_folder)
    kind = info["kind"]

    if kind in ("phone", "camera") and info.get("photo_qualified"):
        captured = parse_exif_datetime(info.get("captured"))
        if captured is None:
            # A malformed external info record must also fail closed.
            return photos_root / f"{folder_year}相片" / f"{folder_year}下載", "download"
        target_year = f"{captured.year:04d}"
        target_month = f"{captured.month:02d}"
        return (
            photos_root / f"{target_year}相片" / f"{target_year}.{target_month}",
            "photo",
        )

    # For non-photos, the containing year is only the requested destination
    # namespace.  It is not evidence about capture type or capture date.
    base = photos_root / f"{folder_year}相片"
    if kind == "screenshot":
        return base / f"{folder_year}截圖", "screenshot"
    return base / f"{folder_year}下載", "download"


def _slash(path: Path) -> str:
    return str(path.resolve(strict=False)).replace("\\", "/")


def _same_path(left: Path, right: Path) -> bool:
    return _slash(left).casefold() == _slash(right).casefold()


def _add_block(item: dict[str, Any], reason: str) -> None:
    reasons = item.setdefault("block_reasons", [])
    if reason not in reasons:
        reasons.append(reason)
    item["action_before_block"] = item.get("action_before_block", item["action"])
    item["action"] = "blocked"


def _build_plan_item(
    source: Path,
    year_dir: Path,
    source_label: str,
    *,
    photos_root: Path,
    current_month_dir: Path | None = None,
) -> dict[str, Any]:
    info = classify(source)
    target_dir, bucket = plan_target(
        source, year_dir.name, info, photos_root=photos_root,
    )
    # Once (and only once) the EXIF evidence independently qualifies a photo,
    # preserve an existing event subtree when its enclosing YYYY.MM agrees with
    # the trusted capture month.  This is placement preservation, never evidence
    # for classification.  Cross-month photos still target the trusted YYYY.MM.
    if (
        current_month_dir is not None
        and bucket == "photo"
        and info.get("photo_qualified")
        and _same_path(target_dir, current_month_dir)
    ):
        target_dir = source.parent
    target = target_dir / source.name
    action = "keep" if _same_path(source.parent, target_dir) else "move"
    stat = source.stat()
    item: dict[str, Any] = {
        "src": _slash(source),
        "tgt": _slash(target),
        "tgt_dir": _slash(target_dir),
        "action": action,
        "bucket": bucket,
        "kind": info["kind"],
        "captured": info.get("captured"),
        "captured_source": info.get("captured_source"),
        "confidence": info["confidence"],
        "reason": info["reason"],
        "make": info.get("make"),
        "model": info.get("model"),
        "photo_qualified": bool(info.get("photo_qualified")),
        "year_folder": year_dir.name,
        "source": source_label,
        "cross_year": bool(
            info.get("photo_qualified")
            and info.get("captured")
            and info["captured"][:4] != _parse_year_folder(year_dir.name)
        ),
        # Integrity fields are never classification evidence.
        "source_size": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
        "block_reasons": [],
    }
    if action == "move" and not target_dir.is_dir():
        _add_block(item, "target_directory_missing")
    elif action == "move" and target.exists():
        _add_block(item, "target_already_exists")
    return item


def _block_duplicate_targets(plan: list[dict[str, Any]]) -> None:
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in plan:
        if item["action"] == "move":
            by_target[item["tgt"].casefold()].append(item)
    for items in by_target.values():
        if len(items) > 1:
            for item in items:
                _add_block(item, "multiple_sources_have_same_target")


def _block_same_stem_image_video_pairs(plan: list[dict[str, Any]]) -> None:
    """Detect Live-Photo-like candidates and block the whole logical unit."""

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in plan:
        source = Path(item["src"])
        groups[(_slash(source.parent).casefold(), source.stem.casefold())].append(item)

    for items in groups.values():
        suffixes = {Path(item["src"]).suffix.casefold() for item in items}
        if not (suffixes & STILL_IMAGE_EXTS and suffixes & VIDEO_EXTS):
            continue
        logical_paths = sorted(item["src"] for item in items)
        logical_unit = hashlib.sha256(
            "\n".join(logical_paths).encode("utf-8")
        ).hexdigest()[:16]
        for item in items:
            item["same_stem_image_video_candidate"] = True
            item["logical_unit"] = logical_unit
            _add_block(item, "same_stem_image_video_candidate_requires_atomic_review")


def collect_plan(*, photos_root: Path = PHOTOS_ROOT) -> list[dict[str, Any]]:
    """Scan loose files and every YYYY.MM folder using fail-closed policy."""

    if not photos_root.is_dir():
        raise FileNotFoundError(f"photo root does not exist: {photos_root}")

    plan: list[dict[str, Any]] = []
    for year_dir in sorted(photos_root.iterdir(), key=lambda p: p.name.casefold()):
        if not year_dir.is_dir() or not re.fullmatch(r"\d{4}相片", year_dir.name):
            continue
        year_num = _parse_year_folder(year_dir.name)
        month_re = re.compile(rf"^{year_num}\.(0[1-9]|1[0-2])$")

        # Loose files are all classified.  No name/location can grandfather a
        # file into a month.
        for source in sorted(year_dir.iterdir(), key=lambda p: p.name.casefold()):
            if source.is_file() and source.suffix.casefold() in IMG_EXTS:
                plan.append(_build_plan_item(
                    source, year_dir, "loose", photos_root=photos_root,
                ))

        # Every file already in a month is re-qualified.  A file that does not
        # pass the physical-device + original/digitized-date gate is explicitly
        # planned to download (or screenshot only with explicit screenshot proof).
        for month_dir in sorted(year_dir.iterdir(), key=lambda p: p.name.casefold()):
            if not month_dir.is_dir() or not month_re.fullmatch(month_dir.name):
                continue
            for source in sorted(
                month_dir.rglob("*"), key=lambda p: p.as_posix().casefold(),
            ):
                if source.is_file() and source.suffix.casefold() in IMG_EXTS:
                    relative_parent = source.parent.relative_to(year_dir)
                    plan.append(_build_plan_item(
                        source,
                        year_dir,
                        f"month/{relative_parent.as_posix()}",
                        photos_root=photos_root,
                        current_month_dir=month_dir,
                    ))

    _block_duplicate_targets(plan)
    _block_same_stem_image_video_pairs(plan)
    return plan


def summarize(plan: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(plan)
    return {
        "total": len(items),
        "by_bucket": dict(sorted(Counter(i["bucket"] for i in items).items())),
        "by_action": dict(sorted(Counter(i["action"] for i in items).items())),
        "by_source": dict(sorted(Counter(i["source"] for i in items).items())),
        "photo_qualified": sum(bool(i.get("photo_qualified")) for i in items),
        "pair_candidate_files": sum(
            bool(i.get("same_stem_image_video_candidate")) for i in items
        ),
        "blocked_files": sum(i["action"] == "blocked" for i in items),
        "block_reasons": dict(sorted(Counter(
            reason for item in items for reason in item.get("block_reasons", [])
        ).items())),
    }


def compute_plan_sha256(root: str | Path, plan: list[dict[str, Any]]) -> str:
    payload = {
        "schema": MANIFEST_SCHEMA,
        "policy_version": POLICY_VERSION,
        "root": _slash(Path(root)),
        "plan": plan,
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_manifest(
    plan: list[dict[str, Any]], *, photos_root: Path = PHOTOS_ROOT,
) -> dict[str, Any]:
    summary = summarize(plan)
    digest = compute_plan_sha256(photos_root, plan)
    return {
        "schema": MANIFEST_SCHEMA,
        "policy_version": POLICY_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "plan_only",
        "status": "blocked" if summary["blocked_files"] else "ready_for_review",
        "root": _slash(photos_root),
        "plan_sha256": digest,
        "classification_policy": {
            "month_requires": [
                "allowlisted physical-device Make",
                "non-placeholder physical-device Model",
                "parseable EXIF DateTimeOriginal or DateTimeDigitized",
            ],
            "never_photo_evidence_alone": [
                "HEIC/HEIF extension", "IMG_ filename", "filename date",
                "dimensions", "mtime", "current folder", "canonical filename",
            ],
            "fallback": "download",
            "screenshot_requires": "explicit Screenshot/截圖 filename or EXIF UserComment",
            "same_stem_image_video": "block for atomic review",
        },
        "summary": summary,
        "plan": plan,
    }


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    temporary.replace(path)


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("unsupported or missing manifest schema")
    if manifest.get("policy_version") != POLICY_VERSION:
        raise ValueError("manifest policy version does not match this classifier")
    plan = manifest.get("plan")
    if not isinstance(plan, list):
        raise ValueError("manifest plan is not a list")
    expected = compute_plan_sha256(manifest.get("root", ""), plan)
    if manifest.get("plan_sha256") != expected:
        raise ValueError("manifest plan_sha256 mismatch; plan may have been edited")
    if manifest.get("status") != "ready_for_review":
        raise ValueError(f"manifest is not executable: status={manifest.get('status')}")
    if any(item.get("action") == "blocked" for item in plan):
        raise ValueError("manifest contains blocked operations")

    sources = [item.get("src", "").casefold() for item in plan]
    move_targets = [
        item.get("tgt", "").casefold()
        for item in plan if item.get("action") == "move"
    ]
    if len(sources) != len(set(sources)):
        raise ValueError("manifest contains duplicate sources")
    if len(move_targets) != len(set(move_targets)):
        raise ValueError("manifest contains duplicate move targets")
    if any(item.get("action") not in {"keep", "move"} for item in plan):
        raise ValueError("manifest contains an unsupported action")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _live_same_stem_pair(source: Path) -> list[Path]:
    siblings = [
        item for item in source.parent.iterdir()
        if item.is_file()
        and item.stem.casefold() == source.stem.casefold()
        and item.suffix.casefold() in IMG_EXTS
    ]
    suffixes = {item.suffix.casefold() for item in siblings}
    if suffixes & STILL_IMAGE_EXTS and suffixes & VIDEO_EXTS:
        return sorted(siblings, key=lambda p: p.name.casefold())
    return []


def preflight_execution(
    manifest: dict[str, Any],
    *,
    completed: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Validate all writes before the first move; never create target folders."""

    validate_manifest(manifest)
    root = Path(manifest["root"])
    completed = completed or {}
    moves = [item for item in manifest["plan"] if item["action"] == "move"]
    pending: list[dict[str, Any]] = []
    for item in moves:
        source = Path(item["src"])
        target = Path(item["tgt"])
        target_dir = Path(item["tgt_dir"])
        if not _is_within(source, root) or not _is_within(target, root):
            raise ValueError(f"source/target escapes manifest root: {source}")
        source_key = _slash(source)
        if source_key in completed:
            record = completed[source_key]
            if not isinstance(record, dict) or not record.get("target"):
                raise ValueError(f"invalid checkpoint record: {source_key}")
            if not _same_path(Path(record["target"]), target):
                raise ValueError(f"checkpoint target does not match manifest: {source_key}")
            if (
                source.exists()
                or not target.is_file()
                or target.stat().st_size != item.get("source_size")
            ):
                raise ValueError(f"checkpoint state does not match disk: {source_key}")
            continue
        if not source.is_file():
            raise FileNotFoundError(f"source missing: {source}")
        stat = source.stat()
        if stat.st_size != item.get("source_size"):
            raise ValueError(f"source size changed after plan: {source}")
        if stat.st_mtime_ns != item.get("source_mtime_ns"):
            raise ValueError(f"source mtime changed after plan: {source}")
        if not target_dir.is_dir():
            raise FileNotFoundError(f"target directory missing: {target_dir}")
        if target.exists():
            raise FileExistsError(f"target already exists: {target}")
        pair = _live_same_stem_pair(source)
        if pair:
            names = ", ".join(path.name for path in pair)
            raise ValueError(
                f"same-stem image/video candidate requires atomic review: {names}"
            )
        pending.append(item)
    return pending


def _load_or_create_checkpoint(
    checkpoint_path: Path,
    *,
    manifest_path: Path,
    plan_sha256: str,
) -> dict[str, Any]:
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("schema") != CHECKPOINT_SCHEMA:
            raise ValueError("unsupported checkpoint schema")
        if checkpoint.get("plan_sha256") != plan_sha256:
            raise ValueError("checkpoint belongs to a different plan")
        if Path(checkpoint.get("manifest", "")).resolve() != manifest_path.resolve():
            raise ValueError("checkpoint belongs to a different manifest path")
        return checkpoint
    checkpoint = {
        "schema": CHECKPOINT_SCHEMA,
        "manifest": _slash(manifest_path),
        "plan_sha256": plan_sha256,
        "status": "preflight_complete",
        "completed": {},
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    _atomic_write_json(checkpoint_path, checkpoint)
    return checkpoint


def cmd_plan(
    *,
    manifest_path: Path = REPORT_PATH,
    photos_root: Path = PHOTOS_ROOT,
) -> dict[str, Any]:
    print("Scanning with fail-closed policy…")
    plan = collect_plan(photos_root=photos_root)
    manifest = build_manifest(plan, photos_root=photos_root)
    _atomic_write_json(manifest_path, manifest)
    summary = manifest["summary"]
    print(f"Plan records: {summary['total']}")
    print(f"Actions: {summary['by_action']}")
    print(f"Buckets: {summary['by_bucket']}")
    print(f"Manifest status: {manifest['status']}")
    print(f"Plan SHA-256: {manifest['plan_sha256']}")
    print(f"Manifest: {manifest_path}")
    return manifest


def cmd_execute(
    *,
    manifest_path: Path,
    checkpoint_path: Path,
    confirm_plan_sha256: str,
) -> dict[str, int]:
    """Execute an explicitly confirmed manifest.  Never called by plan mode."""

    if _same_path(manifest_path, checkpoint_path):
        raise ValueError("manifest and checkpoint paths must be different")
    if _same_path(manifest_path, MOVE_LOG_PATH) or _same_path(checkpoint_path, MOVE_LOG_PATH):
        raise ValueError("manifest/checkpoint path must not be the move log path")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    if confirm_plan_sha256 != manifest["plan_sha256"]:
        raise ValueError("--confirm-plan-sha256 does not match the manifest")
    checkpoint_exists = checkpoint_path.exists()
    if checkpoint_exists:
        checkpoint = _load_or_create_checkpoint(
            checkpoint_path,
            manifest_path=manifest_path,
            plan_sha256=manifest["plan_sha256"],
        )
        completed: dict[str, Any] = checkpoint.setdefault("completed", {})
        planned_sources = {
            item["src"].casefold() for item in manifest["plan"]
            if item["action"] == "move"
        }
        unexpected_completed = {
            source.casefold() for source in completed
        } - planned_sources
        if unexpected_completed:
            raise ValueError("checkpoint contains sources not present in the manifest")
        resumed_count = len(completed)
        moves = preflight_execution(manifest, completed=completed)
    else:
        moves = preflight_execution(manifest)
        reserved_targets = {
            item["tgt"].casefold() for item in manifest["plan"]
            if item["action"] == "move"
        }
        if _slash(checkpoint_path).casefold() in reserved_targets:
            raise ValueError("checkpoint path conflicts with a planned target")
        if _slash(MOVE_LOG_PATH).casefold() in reserved_targets:
            raise ValueError("move log path conflicts with a planned target")
        checkpoint = _load_or_create_checkpoint(
            checkpoint_path,
            manifest_path=manifest_path,
            plan_sha256=manifest["plan_sha256"],
        )
        completed = checkpoint.setdefault("completed", {})
        resumed_count = 0

    moved = 0
    MOVE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MOVE_LOG_PATH.open("a", encoding="utf-8") as log:
        for item in moves:
            source = Path(item["src"])
            target = Path(item["tgt"])
            source_key = _slash(source)
            try:
                # Recheck collision/pair gates immediately before each write in
                # case the filesystem changed after the all-items preflight.
                if target.exists():
                    raise FileExistsError(f"target appeared after preflight: {target}")
                pair = _live_same_stem_pair(source)
                if pair:
                    names = ", ".join(path.name for path in pair)
                    raise ValueError(
                        "same-stem image/video candidate appeared after preflight: "
                        f"{names}"
                    )
                shutil.move(str(source), str(target))
                if (
                    source.exists()
                    or not target.is_file()
                    or target.stat().st_size != item["source_size"]
                ):
                    raise OSError(f"move readback validation failed: {source} -> {target}")
            except Exception:
                checkpoint["status"] = "error"
                checkpoint["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
                _atomic_write_json(checkpoint_path, checkpoint)
                raise
            completed[source_key] = {
                "target": _slash(target),
                "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            checkpoint["status"] = "executing"
            checkpoint["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            _atomic_write_json(checkpoint_path, checkpoint)
            log.write(json.dumps({
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                "plan_sha256": manifest["plan_sha256"],
                "from": source_key,
                "to": _slash(target),
                "bucket": item["bucket"],
            }, ensure_ascii=False) + "\n")
            log.flush()
            moved += 1

    checkpoint["status"] = "complete"
    checkpoint["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    _atomic_write_json(checkpoint_path, checkpoint)
    result = {"moved": moved, "checkpoint_skipped": resumed_count, "errors": 0}
    print(f"Execution complete: {result}")
    print(f"Checkpoint: {checkpoint_path}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    plan_parser = subparsers.add_parser("plan", help="read-only scan and manifest")
    plan_parser.add_argument("--manifest", type=Path, default=REPORT_PATH)
    plan_parser.add_argument("--root", type=Path, default=PHOTOS_ROOT)

    execute_parser = subparsers.add_parser(
        "execute", help="execute an explicitly reviewed manifest",
    )
    execute_parser.add_argument("--manifest", type=Path, required=True)
    execute_parser.add_argument("--checkpoint", type=Path, required=True)
    execute_parser.add_argument("--confirm-plan-sha256", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "plan"
    try:
        if command == "plan":
            cmd_plan(
                manifest_path=getattr(args, "manifest", REPORT_PATH),
                photos_root=getattr(args, "root", PHOTOS_ROOT),
            )
        else:
            cmd_execute(
                manifest_path=args.manifest,
                checkpoint_path=args.checkpoint,
                confirm_plan_sha256=args.confirm_plan_sha256,
            )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
