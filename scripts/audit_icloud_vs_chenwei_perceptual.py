#!/usr/bin/env python3
"""Read-only cross-audit of fresh iCloud originals against Chenwei media.

Cached/R2 thumbnails are used only to generate candidates. Every candidate is
re-read from both current originals before classification. Media are never
copied, moved, renamed, or deleted; only the requested report/contact sheets
and a resumable temporary video-signature cache are written.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import copy
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np
from PIL import ExifTags, Image, ImageDraw, ImageFont, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pillow_heif = None


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".avif", ".bmp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
FP_VERSION = "phash16-dhash9-color8-v1"
THUMB_WIDTH = 480
PHASH_N = 16
PHASH_LOW = 8
COS_TABLE = np.cos(
    ((2 * np.arange(PHASH_N)[None, :] + 1) * np.arange(PHASH_LOW)[:, None] * np.pi)
    / (2 * PHASH_N)
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def json_sha(path: Path) -> str:
    return sha256_file(path)


def cache_key(year: str, bucket: str, name: str) -> str:
    return hashlib.sha256(f"chenwei|{year}|{bucket}|{name}".encode()).hexdigest()[:32]


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


def source_for_bucket(bucket: str) -> str:
    if bucket == "screenshots":
        return "screenshot"
    if bucket == "downloads":
        return "download"
    if re.match(r"^(0[1-9]|1[0-2])(?:/|$)", bucket):
        return "photo"
    return "event"


def flatten_library(index: dict[str, Any], root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    images, videos = [], []
    for year, year_data in index["libraries"]["chenwei"]["years"].items():
        for bucket, files in year_data.get("buckets", {}).items():
            for item in files:
                relpath = library_relpath(year, bucket, item["name"])
                row = {
                    "year": year,
                    "bucket": bucket,
                    "source": source_for_bucket(bucket),
                    "name": item["name"],
                    "ext": str(item.get("ext") or Path(item["name"]).suffix).casefold(),
                    "kind": item.get("kind"),
                    "size": int(item.get("size") or 0),
                    "mtime_ms": item.get("mtime"),
                    "relpath": relpath,
                    "path": str(root / Path(*PurePosixPath(relpath).parts)),
                    "cache_key": cache_key(year, bucket, item["name"]),
                }
                (videos if row["kind"] == "video" else images).append(row)
    return images, videos


def load_checkpoint(path: Path) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("v") != FP_VERSION:
                continue
            parts = str(row.get("key", "")).split("|")
            if len(parts) >= 4:
                found[parts[1]] = {"fingerprint": row["fingerprint"], "checkpoint_key": row["key"]}
    return found


def bits_to_int(bits: np.ndarray) -> int:
    value = 0
    for bit in bits.astype(np.uint8).reshape(-1).tolist():
        value = (value << 1) | int(bit)
    return value


def fingerprint_pil(image: Image.Image, *, webp_roundtrip: bool = True) -> tuple[dict[str, Any], np.ndarray, Image.Image]:
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    if width > THUMB_WIDTH:
        new_height = max(1, round(height * THUMB_WIDTH / width))
        thumb = image.resize((THUMB_WIDTH, new_height), Image.Resampling.LANCZOS)
    else:
        thumb = image.copy()
    if webp_roundtrip:
        buffer = io.BytesIO()
        thumb.save(buffer, format="WEBP", quality=80)
        buffer.seek(0)
        thumb = Image.open(buffer).convert("RGB")
        thumb.load()

    gray16 = np.asarray(thumb.convert("L").resize((PHASH_N, PHASH_N), Image.Resampling.LANCZOS), dtype=np.float64)
    coeffs = COS_TABLE @ gray16 @ COS_TABLE.T
    low = coeffs[:PHASH_LOW, :PHASH_LOW].reshape(-1)
    threshold = float(np.median(low[1:]))
    phash = bits_to_int(low > threshold)

    gray_d = np.asarray(thumb.convert("L").resize((9, 8), Image.Resampling.LANCZOS), dtype=np.int16)
    dhash = bits_to_int(gray_d[:, :-1] > gray_d[:, 1:])
    color = np.asarray(thumb.resize((8, 8), Image.Resampling.LANCZOS), dtype=np.float64).reshape(-1, 3).mean(axis=0)
    gray64 = np.asarray(thumb.convert("L").resize((64, 64), Image.Resampling.LANCZOS), dtype=np.uint8)
    rgb64 = np.asarray(thumb.resize((64, 64), Image.Resampling.LANCZOS), dtype=np.uint8)
    fp = {
        "p_hash": int(phash),
        "p_hash_hex": f"{phash:016x}",
        "d_hash": int(dhash),
        "d_hash_hex": f"{dhash:016x}",
        "width": int(thumb.width),
        "height": int(thumb.height),
        "source_width": int(width),
        "source_height": int(height),
        "aspect_ratio": thumb.width / max(1, thumb.height),
        "brightness": round(float(gray16.mean()), 2),
        "average_rgb": [round(float(value), 2) for value in color],
    }
    return fp, gray64, thumb


def embedded_image_date(image: Image.Image) -> tuple[str | None, str | None]:
    try:
        raw = image._getexif() if hasattr(image, "_getexif") else image.getexif()
        named = {ExifTags.TAGS.get(key, str(key)): value for key, value in (raw or {}).items()}
    except Exception:
        return None, None
    for tag, source in (("DateTimeOriginal", "exif_datetime_original"), ("DateTimeDigitized", "exif_datetime_digitized"), ("DateTime", "exif_datetime")):
        value = named.get(tag)
        if isinstance(value, bytes):
            value = value.decode("ascii", errors="ignore")
        if not value:
            continue
        text = str(value).strip("\x00 ")
        for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return dt.datetime.strptime(text[:19], fmt).isoformat(timespec="seconds"), source
            except ValueError:
                pass
    return None, None


def read_image_fresh(path: Path, *, hash_bytes: bool = False) -> dict[str, Any]:
    stat = path.stat()
    digest = sha256_file(path) if hash_bytes else None
    with Image.open(path) as image:
        image.load()
        capture_date, capture_source = embedded_image_date(image)
        fp, gray64, thumb = fingerprint_pil(image)
    return {
        "path": str(path),
        "actual_size": stat.st_size,
        "actual_mtime": stat.st_mtime,
        "sha256": digest,
        "fingerprint": fp,
        "gray64": gray64,
        "thumb": thumb,
        "embedded_date": capture_date,
        "embedded_date_source": capture_source,
        "read_at": now_iso(),
    }


def checkpoint_fp(row: dict[str, Any]) -> dict[str, Any]:
    source = row["fingerprint"]
    return {
        "p_hash": int(source["pHash"], 16),
        "p_hash_hex": source["pHash"],
        "d_hash": int(source["dHash"], 16),
        "d_hash_hex": source["dHash"],
        "width": int(source["width"]),
        "height": int(source["height"]),
        "source_width": None,
        "source_height": None,
        "aspect_ratio": float(source["aspectRatio"]),
        "brightness": float(source["brightness"]),
        "average_rgb": [float(x) for x in source["averageRgb"]],
        "thumb_sha256": source.get("thumbSha256"),
        "normalized_sha256": source.get("normalizedSha256"),
    }


def fp_metrics(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    p = (int(a["p_hash"]) ^ int(b["p_hash"])).bit_count()
    d = (int(a["d_hash"]) ^ int(b["d_hash"])).bit_count()
    aspect = abs(float(a["aspect_ratio"]) - float(b["aspect_ratio"])) / max(float(a["aspect_ratio"]), float(b["aspect_ratio"]), 1e-9)
    brightness = abs(float(a["brightness"]) - float(b["brightness"]))
    color = math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a["average_rgb"], b["average_rgb"])))
    return {
        "p_hash_distance": p,
        "d_hash_distance": d,
        "total_hash_distance": p + d,
        "aspect_delta": round(aspect, 6),
        "brightness_delta": round(brightness, 3),
        "color_distance": round(color, 3),
        "score": round(p * 2 + d + aspect * 100 + brightness / 10 + color / 20, 3),
    }


def normalized_correlation(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.astype(np.float64).reshape(-1)
    bb = b.astype(np.float64).reshape(-1)
    aa -= aa.mean(); bb -= bb.mean()
    denom = math.sqrt(float(np.dot(aa, aa) * np.dot(bb, bb)))
    return float(np.dot(aa, bb) / denom) if denom > 1e-9 else (1.0 if np.allclose(a, b) else 0.0)


def edge_array(gray: np.ndarray) -> np.ndarray:
    data = gray.astype(np.float64)
    gx = np.diff(data, axis=1, append=data[:, -1:])
    gy = np.diff(data, axis=0, append=data[-1:, :])
    return np.hypot(gx, gy)


def crop_gray(gray: np.ndarray, scale: float) -> np.ndarray:
    if scale >= 0.999:
        crop = gray
    else:
        height, width = gray.shape
        out_h, out_w = max(4, round(height * scale)), max(4, round(width * scale))
        y, x = (height - out_h) // 2, (width - out_w) // 2
        crop = gray[y:y + out_h, x:x + out_w]
    return np.asarray(Image.fromarray(crop).resize((64, 64), Image.Resampling.LANCZOS), dtype=np.uint8)


def visual_metrics(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    full_ncc = normalized_correlation(a["gray64"], b["gray64"])
    edge_ncc = normalized_correlation(edge_array(a["gray64"]), edge_array(b["gray64"]))
    best = (full_ncc, 1.0, 1.0)
    for left_scale, right_scale in ((0.9, 1.0), (0.8, 1.0), (1.0, 0.9), (1.0, 0.8), (0.9, 0.9)):
        value = normalized_correlation(crop_gray(a["gray64"], left_scale), crop_gray(b["gray64"], right_scale))
        if value > best[0]:
            best = (value, left_scale, right_scale)
    mae = float(np.abs(a["gray64"].astype(np.float64) - b["gray64"].astype(np.float64)).mean())
    return {
        "full_frame_ncc": round(full_ncc, 6),
        "edge_ncc": round(edge_ncc, 6),
        "best_center_crop_ncc": round(best[0], 6),
        "best_center_crop_scales": [best[1], best[2]],
        "grayscale_mae": round(mae, 3),
    }


def candidate_tier(metrics: dict[str, Any], *, broad: bool = True) -> str | None:
    strict = (
        metrics["p_hash_distance"] <= 4 and metrics["d_hash_distance"] <= 5
        and metrics["total_hash_distance"] <= 8 and metrics["aspect_delta"] <= 0.02
        and metrics["brightness_delta"] <= 20 and metrics["color_distance"] <= 28
    )
    if strict:
        return "strict"
    if broad and (
        metrics["p_hash_distance"] <= 8 and metrics["d_hash_distance"] <= 10
        and metrics["total_hash_distance"] <= 14 and metrics["aspect_delta"] <= 0.04
        and metrics["brightness_delta"] <= 32 and metrics["color_distance"] <= 48
    ):
        return "broad"
    return None


def classify_verified_pair(metrics: dict[str, Any], visual: dict[str, Any], library: dict[str, Any]) -> tuple[str, str]:
    strict = candidate_tier(metrics) == "strict"
    safe = strict and (
        (visual["full_frame_ncc"] >= 0.985 and visual["edge_ncc"] >= 0.94)
        or (visual["full_frame_ncc"] >= 0.97 and visual["edge_ncc"] >= 0.90 and metrics["p_hash_distance"] <= 2)
        or (visual["best_center_crop_ncc"] >= 0.99 and metrics["p_hash_distance"] <= 3)
    )
    if safe:
        if library["source"] == "download" or library["name"].casefold().startswith("d20"):
            return "safe_skip", "later_downloaded_copy"
        return "safe_skip", "same_base_reencoded_scaled_light_edit"
    likely = (
        candidate_tier(metrics) is not None
        and (visual["full_frame_ncc"] >= 0.82 or visual["best_center_crop_ncc"] >= 0.90)
    )
    if likely:
        return "manual_review", "possible_same_base_or_light_edit"
    if metrics["p_hash_distance"] <= 8 and visual["full_frame_ncc"] >= 0.35:
        return "keep_distinct", "distinct_burst_pose_or_frame"
    return "keep_distinct", "different_image"


def parse_library_filename_date(item: dict[str, Any]) -> tuple[str | None, str | None]:
    if item["source"] == "download":
        return None, None
    match = re.search(r"(?<!\d)(20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(?!\d)", item["name"])
    if not match:
        return None, None
    try:
        value = dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
        return f"{value}T00:00:00", "existing_normalized_photo_filename"
    except ValueError:
        return None, None


def probe_video(path: Path) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
        if proc.returncode:
            return {"ok": False, "error": f"ffprobe_exit_{proc.returncode}"}
        data = json.loads(proc.stdout or "{}")
        fmt = data.get("format") or {}
        stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        tags = {str(k).casefold(): v for k, v in (fmt.get("tags") or {}).items()}
        stream_tags = {str(k).casefold(): v for k, v in (stream.get("tags") or {}).items()}
        creation = tags.get("com.apple.quicktime.creationdate") or tags.get("creation_time") or stream_tags.get("creation_time")
        capture = None
        if creation:
            try:
                capture = dt.datetime.fromisoformat(str(creation).replace("Z", "+00:00")).isoformat(timespec="seconds")
            except ValueError:
                pass
        return {
            "ok": True,
            "duration": float(fmt.get("duration") or stream.get("duration") or 0),
            "width": int(stream.get("width") or 0),
            "height": int(stream.get("height") or 0),
            "capture_date": capture,
            "capture_date_source": "quicktime_creation_time" if capture else None,
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}:{exc}"[:300]}


def extract_video_frame(path: Path, when: float) -> tuple[dict[str, Any], np.ndarray, Image.Image]:
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, when):.3f}", "-i", str(path), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True, timeout=90,
    )
    if proc.returncode or not proc.stdout:
        raise RuntimeError(f"ffmpeg_frame_exit_{proc.returncode}")
    with Image.open(io.BytesIO(proc.stdout)) as image:
        image.load()
        return fingerprint_pil(image)


def video_signature(path: Path) -> dict[str, Any]:
    probe = probe_video(path)
    if not probe.get("ok"):
        return {"ok": False, "probe": probe}
    duration = probe["duration"]
    try:
        fp, _gray, _ = extract_video_frame(path, max(0.0, duration * 0.10))
        return {"ok": True, "probe": probe, "fingerprint": fp}
    except Exception as exc:
        return {"ok": False, "probe": probe, "error": f"{type(exc).__name__}:{exc}"[:300]}


def video_pair_verify(new_path: Path, lib_path: Path, new_probe: dict[str, Any], lib_probe: dict[str, Any]) -> dict[str, Any]:
    duration = max(new_probe.get("duration") or 0, lib_probe.get("duration") or 0)
    positions = (0.10, 0.50, 0.90) if duration > 2 else (0.0, 0.5, 0.9)
    frames = []
    for position in positions:
        try:
            a_fp, a_gray, _ = extract_video_frame(new_path, (new_probe.get("duration") or 0) * position)
            b_fp, b_gray, _ = extract_video_frame(lib_path, (lib_probe.get("duration") or 0) * position)
            metrics = fp_metrics(a_fp, b_fp)
            visual = {
                "full_frame_ncc": round(normalized_correlation(a_gray, b_gray), 6),
                "edge_ncc": round(normalized_correlation(edge_array(a_gray), edge_array(b_gray)), 6),
            }
            frames.append({"position": position, "metrics": metrics, "visual": visual})
        except Exception as exc:
            frames.append({"position": position, "error": f"{type(exc).__name__}:{exc}"[:300]})
    valid = [frame for frame in frames if "metrics" in frame]
    strict_matches = sum(1 for frame in valid if candidate_tier(frame["metrics"], broad=False) and frame["visual"]["full_frame_ncc"] >= 0.96)
    duration_delta = abs((new_probe.get("duration") or 0) - (lib_probe.get("duration") or 0))
    tolerance = max(0.35, duration * 0.01)
    if len(valid) >= 2 and strict_matches >= 2 and duration_delta <= tolerance:
        classification, reason = "safe_skip", "same_video_reencoded_or_downloaded_copy"
    elif valid and any(frame["visual"]["full_frame_ncc"] >= 0.85 for frame in valid):
        classification, reason = "manual_review", "possible_same_video_or_overlapping_frames"
    else:
        classification, reason = "keep_distinct", "different_video_or_video_frames"
    return {
        "duration_delta": round(duration_delta, 6),
        "duration_tolerance": round(tolerance, 6),
        "frames": frames,
        "classification": classification,
        "reason": reason,
    }


def fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    canvas = Image.new("RGB", (width, height), "white")
    copy_img = image.convert("RGB").copy()
    copy_img.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas.paste(copy_img, ((width - copy_img.width) // 2, (height - copy_img.height) // 2))
    return canvas


def font(size: int) -> ImageFont.ImageFont:
    for candidate in (Path("C:/Windows/Fonts/msjh.ttc"), Path("C:/Windows/Fonts/arial.ttf")):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def render_contact_sheets(pairs: list[dict[str, Any]], output_dir: Path, rows_per_sheet: int = 4) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    title_font, label_font = font(20), font(15)
    row_h, image_w, image_h = 330, 430, 250
    for page, start in enumerate(range(0, len(pairs), rows_per_sheet), 1):
        subset = pairs[start:start + rows_per_sheet]
        sheet = Image.new("RGB", (image_w * 2 + 40, row_h * len(subset) + 50), "#f4f1eb")
        draw = ImageDraw.Draw(sheet)
        draw.text((16, 12), f"Fresh-original candidate pairs — page {page}", fill="black", font=title_font)
        for row_index, pair in enumerate(subset):
            y = 48 + row_index * row_h
            try:
                with Image.open(pair["icloud_path"]) as image:
                    image.load(); left = fit_image(ImageOps.exif_transpose(image), image_w, image_h)
            except Exception:
                left = Image.new("RGB", (image_w, image_h), "#ddd")
            try:
                with Image.open(pair["library_path"]) as image:
                    image.load(); right = fit_image(ImageOps.exif_transpose(image), image_w, image_h)
            except Exception:
                right = Image.new("RGB", (image_w, image_h), "#ddd")
            sheet.paste(left, (10, y)); sheet.paste(right, (image_w + 30, y))
            draw.rectangle((10, y, image_w + 10, y + image_h), outline="#555", width=1)
            draw.rectangle((image_w + 30, y, image_w * 2 + 30, y + image_h), outline="#555", width=1)
            metrics = pair.get("original_metrics") or {}
            visual = pair.get("visual_metrics") or {}
            text = (
                f"{pair['id']}  {pair['classification']} / {pair['reason']}\n"
                f"iCloud: {Path(pair['icloud_path']).name}    Library: {pair['library_relpath']}\n"
                f"p={metrics.get('p_hash_distance')} d={metrics.get('d_hash_distance')} "
                f"NCC={visual.get('full_frame_ncc')} edge={visual.get('edge_ncc')} crop={visual.get('best_center_crop_ncc')}"
            )
            draw.multiline_text((14, y + image_h + 5), text, fill="#111", font=label_font, spacing=2)
        out = output_dir / f"candidates_{page:03d}.png"
        sheet.save(out, format="PNG", optimize=True)
        paths.append(str(out))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exact-report", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--library-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sheets-dir", type=Path, required=True)
    parser.add_argument("--video-cache", type=Path, default=Path("C:/tmp/chenwei_video_signatures_20260804.json"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    started = dt.datetime.now(dt.timezone.utc)
    exact = json.loads(args.exact_report.read_text(encoding="utf-8"))
    index = json.loads(args.index.read_text(encoding="utf-8"))
    library_images, library_videos = flatten_library(index, args.library_root)
    checkpoint = load_checkpoint(args.checkpoint)
    input_items = exact["keep_candidates"]
    input_images = [copy.deepcopy(item) for item in input_items if item["ext"] in IMAGE_EXTS]
    input_videos = [copy.deepcopy(item) for item in input_items if item["ext"] in VIDEO_EXTS]
    print(f"Inputs: {len(input_images)} images, {len(input_videos)} videos", flush=True)

    # Current index -> cached/R2 fingerprint mapping. HEIC/GIF or missing cache
    # entries are fingerprinted directly from current originals as a small,
    # explicitly recorded candidate-generation exception.
    lib_fp_rows, lib_fp_missing = [], []
    for item in library_images:
        saved = checkpoint.get(item["cache_key"])
        if saved:
            row = copy.deepcopy(item); row["fingerprint"] = checkpoint_fp(saved); row["fingerprint_source"] = "cached_r2_480_candidate_only"
            lib_fp_rows.append(row)
        else:
            lib_fp_missing.append(item)
    print(f"Library thumbnail fingerprints: {len(lib_fp_rows)}; missing/unsupported: {len(lib_fp_missing)}", flush=True)

    def fresh_missing(item: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        path = Path(item["path"])
        try:
            current = read_image_fresh(path)
            row = copy.deepcopy(item); row["fingerprint"] = current["fingerprint"]; row["fingerprint_source"] = "fresh_original_candidate_stage"
            return row, None
        except Exception as exc:
            return None, {"relpath": item["relpath"], "error": f"{type(exc).__name__}:{exc}"[:300]}

    with futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as pool:
        missing_results = list(pool.map(fresh_missing, lib_fp_missing))
    library_candidate_errors = [error for _, error in missing_results if error]
    lib_fp_rows.extend(row for row, _ in missing_results if row)

    print("Fingerprinting fresh iCloud image originals...", flush=True)
    def fresh_input(item: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        try:
            current = read_image_fresh(Path(item["path"]))
            row = copy.deepcopy(item); row["fresh"] = current
            return row, None
        except Exception as exc:
            return None, {"sha256": item["sha256"], "path": item["path"], "error": f"{type(exc).__name__}:{exc}"[:300]}

    fresh_inputs, fresh_input_errors = [], []
    with futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for index_no, (row, error) in enumerate(pool.map(fresh_input, input_images), 1):
            if row: fresh_inputs.append(row)
            if error: fresh_input_errors.append(error)
            if index_no % 200 == 0: print(f"  iCloud images {index_no}/{len(input_images)}", flush=True)

    # Vectorized full-library candidate search.
    lib_p = np.asarray([row["fingerprint"]["p_hash"] for row in lib_fp_rows], dtype=np.uint64)
    lib_d = np.asarray([row["fingerprint"]["d_hash"] for row in lib_fp_rows], dtype=np.uint64)
    lib_aspect = np.asarray([row["fingerprint"]["aspect_ratio"] for row in lib_fp_rows], dtype=np.float64)
    lib_brightness = np.asarray([row["fingerprint"]["brightness"] for row in lib_fp_rows], dtype=np.float64)
    lib_color = np.asarray([row["fingerprint"]["average_rgb"] for row in lib_fp_rows], dtype=np.float64)
    thumbnail_candidates: list[dict[str, Any]] = []
    for pos, item in enumerate(fresh_inputs, 1):
        fp = item["fresh"]["fingerprint"]
        pd = np.bitwise_count(np.bitwise_xor(lib_p, np.uint64(fp["p_hash"]))).astype(np.int16)
        dd = np.bitwise_count(np.bitwise_xor(lib_d, np.uint64(fp["d_hash"]))).astype(np.int16)
        aspect = np.abs(lib_aspect - fp["aspect_ratio"]) / np.maximum(np.maximum(lib_aspect, fp["aspect_ratio"]), 1e-9)
        bright = np.abs(lib_brightness - fp["brightness"])
        color = np.linalg.norm(lib_color - np.asarray(fp["average_rgb"]), axis=1)
        total = pd + dd
        mask = (pd <= 8) & (dd <= 10) & (total <= 14) & (aspect <= 0.04) & (bright <= 32) & (color <= 48)
        indices = np.flatnonzero(mask)
        if indices.size:
            scores = pd[indices] * 2 + dd[indices] + aspect[indices] * 100 + bright[indices] / 10 + color[indices] / 20
            indices = indices[np.argsort(scores)[:10]]
            for lib_index in indices.tolist():
                metrics = {
                    "p_hash_distance": int(pd[lib_index]), "d_hash_distance": int(dd[lib_index]),
                    "total_hash_distance": int(total[lib_index]), "aspect_delta": round(float(aspect[lib_index]), 6),
                    "brightness_delta": round(float(bright[lib_index]), 3), "color_distance": round(float(color[lib_index]), 3),
                    "score": round(float(pd[lib_index] * 2 + dd[lib_index] + aspect[lib_index] * 100 + bright[lib_index] / 10 + color[lib_index] / 20), 3),
                }
                thumbnail_candidates.append({
                    "icloud": item,
                    "library": lib_fp_rows[lib_index],
                    "thumbnail_metrics": metrics,
                    "thumbnail_tier": candidate_tier(metrics),
                })
        if pos % 200 == 0: print(f"  cross-search {pos}/{len(fresh_inputs)} candidates={len(thumbnail_candidates)}", flush=True)
    print(f"Thumbnail candidate pairs: {len(thumbnail_candidates)}", flush=True)

    # Fresh-current-original verification. Library rows just removed after the
    # snapshot are current-missing and deliberately excluded.
    library_original_cache: dict[str, dict[str, Any]] = {}
    library_original_errors: dict[str, str] = {}
    unique_lib_rows = {candidate["library"]["relpath"]: candidate["library"] for candidate in thumbnail_candidates}
    def read_library(row: dict[str, Any]) -> tuple[str, dict[str, Any] | None, str | None]:
        try:
            return row["relpath"], read_image_fresh(Path(row["path"]), hash_bytes=True), None
        except Exception as exc:
            return row["relpath"], None, f"{type(exc).__name__}:{exc}"[:300]
    with futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as pool:
        for done, (relpath, current, error) in enumerate(pool.map(read_library, unique_lib_rows.values()), 1):
            if current: library_original_cache[relpath] = current
            else: library_original_errors[relpath] = error or "unknown"
            if done % 50 == 0: print(f"  fresh library originals {done}/{len(unique_lib_rows)}", flush=True)

    verified_pairs: list[dict[str, Any]] = []
    stale_thumbnail_count = 0
    for number, candidate in enumerate(thumbnail_candidates, 1):
        icloud, library = candidate["icloud"], candidate["library"]
        current = library_original_cache.get(library["relpath"])
        if not current:
            verified_pairs.append({
                "id": f"img-{number:05d}", "media_type": "image", "icloud_sha256": icloud["sha256"],
                "icloud_path": icloud["path"], "library_relpath": library["relpath"], "library_path": library["path"],
                "classification": "excluded_current_missing", "reason": library_original_errors.get(library["relpath"], "current_missing"),
                "thumbnail_metrics": candidate["thumbnail_metrics"],
            })
            continue
        original_metrics = fp_metrics(icloud["fresh"]["fingerprint"], current["fingerprint"])
        visual = visual_metrics(icloud["fresh"], current)
        stale_metrics = fp_metrics(library["fingerprint"], current["fingerprint"])
        stale = candidate_tier(stale_metrics, broad=False) is None
        stale_thumbnail_count += int(stale)
        classification, reason = classify_verified_pair(original_metrics, visual, library)
        library_date = current.get("embedded_date")
        library_date_source = current.get("embedded_date_source")
        if not library_date:
            library_date, library_date_source = parse_library_filename_date(library)
        recovered = None
        if not icloud.get("captured_at") and classification == "safe_skip" and library_date:
            recovered = {"value": library_date, "source": library_date_source, "from_library_relpath": library["relpath"]}
        verified_pairs.append({
            "id": f"img-{number:05d}", "media_type": "image", "icloud_sha256": icloud["sha256"],
            "icloud_path": icloud["path"], "icloud_relpath": icloud["relpath"], "icloud_name": icloud["name"],
            "icloud_existing_date": icloud.get("captured_at"), "library_relpath": library["relpath"], "library_path": library["path"],
            "library_source": library["source"], "library_index_size": library["size"], "library_current_size": current["actual_size"],
            "library_current_sha256": current["sha256"], "library_index_size_matches": current["actual_size"] == library["size"],
            "thumbnail_metrics": candidate["thumbnail_metrics"], "thumbnail_tier": candidate["thumbnail_tier"],
            "library_cached_thumbnail_stale": stale, "cached_vs_current_metrics": stale_metrics,
            "original_metrics": original_metrics, "visual_metrics": visual,
            "classification": classification, "reason": reason, "recovered_date": recovered,
            "current_originals_verified_at": now_iso(),
        })

    # Video signature stage and fresh three-frame verification.
    print(f"Video stage: {len(input_videos)} new vs {len(library_videos)} indexed", flush=True)
    video_cache: dict[str, Any] = {}
    if args.video_cache.exists():
        try: video_cache = json.loads(args.video_cache.read_text(encoding="utf-8"))
        except Exception: video_cache = {}

    current_library_videos, missing_library_videos = [], []
    for item in library_videos:
        path = Path(item["path"])
        try:
            stat = path.stat()
        except Exception as exc:
            missing_library_videos.append({"relpath": item["relpath"], "error": f"{type(exc).__name__}:{exc}"})
            continue
        key = f"{item['relpath']}|{stat.st_size}|{stat.st_mtime_ns}"
        cached = video_cache.get(key)
        if cached and cached.get("ok"):
            row = copy.deepcopy(item); row["signature"] = cached; current_library_videos.append(row)
        else:
            row = copy.deepcopy(item); row["cache_key_runtime"] = key; current_library_videos.append(row)

    def sig_library_video(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if row.get("signature"):
            return row, {}
        sig = video_signature(Path(row["path"]))
        row["signature"] = sig
        return row, {row["cache_key_runtime"]: sig}
    cache_updates: dict[str, Any] = {}
    with futures.ThreadPoolExecutor(max_workers=max(1, min(args.workers, 3))) as pool:
        processed_library_videos = []
        for done, (row, update) in enumerate(pool.map(sig_library_video, current_library_videos), 1):
            processed_library_videos.append(row); cache_updates.update(update)
            if done % 50 == 0: print(f"  library video signatures {done}/{len(current_library_videos)}", flush=True)
    current_library_videos = processed_library_videos
    if cache_updates:
        video_cache.update(cache_updates)
        args.video_cache.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.video_cache.with_suffix(".tmp")
        tmp.write_text(json.dumps(video_cache, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, args.video_cache)

    fresh_new_videos, new_video_errors = [], []
    for item in input_videos:
        sig = video_signature(Path(item["path"]))
        if sig.get("ok"):
            row = copy.deepcopy(item); row["signature"] = sig; fresh_new_videos.append(row)
        else:
            new_video_errors.append({"sha256": item["sha256"], "path": item["path"], "error": sig})

    video_thumbnail_candidates = []
    valid_lib_videos = [row for row in current_library_videos if row.get("signature", {}).get("ok")]
    for new in fresh_new_videos:
        new_sig = new["signature"]
        candidates = []
        for library in valid_lib_videos:
            lib_sig = library["signature"]
            duration = max(new_sig["probe"]["duration"], lib_sig["probe"]["duration"])
            duration_delta = abs(new_sig["probe"]["duration"] - lib_sig["probe"]["duration"])
            if duration_delta > max(0.5, duration * 0.015):
                continue
            metrics = fp_metrics(new_sig["fingerprint"], lib_sig["fingerprint"])
            tier = candidate_tier(metrics)
            if not tier:
                continue
            candidates.append((metrics["score"] + duration_delta, library, metrics, tier))
        for _, library, metrics, tier in sorted(candidates, key=lambda row: row[0])[:5]:
            video_thumbnail_candidates.append({"new": new, "library": library, "metrics": metrics, "tier": tier})
    print(f"Video thumbnail candidate pairs: {len(video_thumbnail_candidates)}", flush=True)

    video_verified = []
    for number, candidate in enumerate(video_thumbnail_candidates, 1):
        new, library = candidate["new"], candidate["library"]
        lib_path = Path(library["path"])
        if not lib_path.is_file():
            video_verified.append({
                "id": f"vid-{number:05d}", "media_type": "video", "icloud_sha256": new["sha256"],
                "icloud_path": new["path"], "library_relpath": library["relpath"], "library_path": library["path"],
                "classification": "excluded_current_missing", "reason": "current_missing",
            })
            continue
        verification = video_pair_verify(Path(new["path"]), lib_path, new["signature"]["probe"], library["signature"]["probe"])
        recovered = None
        library_date = library["signature"]["probe"].get("capture_date")
        library_date_source = library["signature"]["probe"].get("capture_date_source")
        if not library_date:
            library_date, library_date_source = parse_library_filename_date(library)
        if not new.get("captured_at") and verification["classification"] == "safe_skip" and library_date:
            recovered = {"value": library_date, "source": library_date_source, "from_library_relpath": library["relpath"]}
        video_verified.append({
            "id": f"vid-{number:05d}", "media_type": "video", "icloud_sha256": new["sha256"],
            "icloud_path": new["path"], "icloud_relpath": new["relpath"], "library_relpath": library["relpath"],
            "library_path": library["path"], "thumbnail_metrics": candidate["metrics"], "thumbnail_tier": candidate["tier"],
            **verification, "recovered_date": recovered, "current_originals_verified_at": now_iso(),
        })

    all_pairs = verified_pairs + video_verified
    # One disposition per iCloud content. Safe wins; otherwise manual wins.
    by_sha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in all_pairs:
        by_sha[pair["icloud_sha256"]].append(pair)
    dispositions = []
    for item in input_items:
        pairs = by_sha.get(item["sha256"], [])
        safe = [pair for pair in pairs if pair["classification"] == "safe_skip"]
        manual = [pair for pair in pairs if pair["classification"] == "manual_review"]
        excluded = [pair for pair in pairs if pair["classification"] == "excluded_current_missing"]
        if safe:
            choice = sorted(safe, key=lambda pair: (pair.get("original_metrics") or pair.get("thumbnail_metrics") or {}).get("score", 999))[0]
            disposition = "safe_skip"
        elif manual:
            choice = sorted(manual, key=lambda pair: (pair.get("original_metrics") or pair.get("thumbnail_metrics") or {}).get("score", 999))[0]
            disposition = "manual_review"
        else:
            choice = None
            disposition = "keep_no_confirmed_duplicate"
        dispositions.append({
            "sha256": item["sha256"], "batch_id": item["batch_id"], "relpath": item["relpath"], "path": item["path"],
            "media_type": "video" if item["ext"] in VIDEO_EXTS else "image", "disposition": disposition,
            "best_pair_id": choice.get("id") if choice else None,
            "best_library_match": choice.get("library_relpath") if choice else None,
            "reason": choice.get("reason") if choice else "no fresh-original perceptual duplicate confirmed",
            "recovered_date": choice.get("recovered_date") if choice else None,
            "excluded_current_missing_candidates": len(excluded),
        })

    # Fresh-original contact sheets for all safe/manual image pairs plus the
    # strongest 40 distinct image candidates as an explicit burst/pose sample.
    image_review_pairs = [pair for pair in verified_pairs if pair["classification"] in {"safe_skip", "manual_review"}]
    distinct_sample = sorted(
        (pair for pair in verified_pairs if pair["classification"] == "keep_distinct"),
        key=lambda pair: (pair.get("original_metrics") or {}).get("score", 999),
    )[:40]
    contact_sheet_pairs = image_review_pairs + distinct_sample
    contact_sheet_paths = render_contact_sheets(contact_sheet_pairs, args.sheets_dir) if contact_sheet_pairs else []

    counts = Counter(item["disposition"] for item in dispositions)
    pair_counts = Counter(pair["classification"] for pair in all_pairs)
    recovered = [item for item in dispositions if item.get("recovered_date")]
    elapsed = (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
    report = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "mode": "read_only_perceptual_audit",
        "inputs": {
            "exact_audit_report": str(args.exact_report), "exact_audit_sha256": json_sha(args.exact_report),
            "photo_index": str(args.index), "photo_index_sha256": json_sha(args.index),
            "photo_index_generated_at": index.get("generatedAt"), "photo_index_reported_total": index["libraries"]["chenwei"].get("totalFiles"),
            "library_root": str(args.library_root), "thumbnail_checkpoint": str(args.checkpoint),
            "new_keep_contents": len(input_items), "new_keep_images": len(input_images), "new_keep_videos": len(input_videos),
        },
        "rules": {
            "cached_r2_thumbnails_candidate_only": True,
            "every_reported_candidate_reread_from_current_originals": True,
            "current_missing_excluded": True,
            "zip_mtime_used_for_dates": False,
            "safe_skip_categories": ["same_base_reencoded_scaled_light_edit", "later_downloaded_copy", "same_video_reencoded_or_downloaded_copy"],
            "burst_pose_or_different_video_frames_are_kept": True,
            "media_mutations_performed": False,
        },
        "summary": {
            "new_keep_contents_audited": len(input_items),
            "library_index_images": len(library_images), "library_index_videos": len(library_videos),
            "library_cached_thumbnail_fingerprints": len(checkpoint),
            "library_images_candidate_ready": len(lib_fp_rows), "library_image_candidate_stage_errors": len(library_candidate_errors),
            "fresh_icloud_image_errors": len(fresh_input_errors),
            "thumbnail_image_candidate_pairs": len(thumbnail_candidates), "fresh_image_pairs_verified": len(verified_pairs),
            "video_thumbnail_candidate_pairs": len(video_thumbnail_candidates), "fresh_video_pairs_verified": len(video_verified),
            "fresh_icloud_video_errors": len(new_video_errors),
            "pair_classification_counts": dict(sorted(pair_counts.items())),
            "safe_skip_contents": counts.get("safe_skip", 0),
            "manual_review_contents": counts.get("manual_review", 0),
            "keep_no_confirmed_duplicate_contents": counts.get("keep_no_confirmed_duplicate", 0),
            "reliably_recovered_missing_dates": len(recovered),
            "current_missing_candidate_pairs_excluded": pair_counts.get("excluded_current_missing", 0),
            "materially_stale_thumbnail_candidate_pairs": stale_thumbnail_count,
            "contact_sheets": len(contact_sheet_paths),
            "elapsed_seconds": round(elapsed, 2),
        },
        "dispositions": dispositions,
        "candidate_pairs": all_pairs,
        "date_recoveries": recovered,
        "contact_sheets": contact_sheet_paths,
        "errors": {
            "fresh_icloud_images": fresh_input_errors,
            "library_image_candidate_stage": library_candidate_errors,
            "library_current_original_candidates": [{"relpath": key, "error": value} for key, value in sorted(library_original_errors.items())],
            "new_videos": new_video_errors,
            "library_videos_current_missing": missing_library_videos,
        },
        "limitations": [
            "Perceptual hashing is a high-recall candidate filter, not duplicate proof.",
            "Safe-skip requires strict fresh-original hashes plus high normalized/edge correlation; broader matches remain manual.",
            "The photo index and cached thumbnails predate any concurrent library cleanup; current-missing originals are excluded.",
            "Contact sheets are rendered from fresh current originals, not R2 thumbnails.",
            "Only high-confidence safe matches can supply a missing date, using embedded metadata or a normalized existing photo filename; ZIP mtime is never used.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = args.output.with_suffix(args.output.suffix + ".tmp")
    temp_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp_output, args.output)
    print(f"Report: {args.output}", flush=True)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
