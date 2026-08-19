"""Full-resolution raster checks and contact sheets for the Hebrew reader."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PAGE_RE = re.compile(r"page-(\d+)\.png$")


def dark_count(image: Image.Image, threshold: int = 238) -> int:
    histogram = image.convert("L").histogram()
    return sum(histogram[:threshold])


def analyze(directory: Path, expected_pages: int) -> dict:
    pages = []
    for path in directory.glob("page-*.png"):
        match = PAGE_RE.match(path.name)
        if match:
            pages.append((int(match.group(1)), path))
    pages.sort()

    ordinals = [number for number, _ in pages]
    expected = list(range(1, expected_pages + 1))
    records = []
    dimensions = set()
    hashes: dict[str, list[int]] = defaultdict(list)
    blank_pages = []
    edge_intrusions = []

    for number, path in pages:
        with Image.open(path) as source:
            image = source.convert("RGB")
        width, height = image.size
        dimensions.add((width, height))
        pixels = width * height
        ink = dark_count(image)
        ink_ratio = ink / pixels
        edge = max(4, round(min(width, height) * 0.004))
        edge_dark = sum(
            dark_count(crop)
            for crop in (
                image.crop((0, 0, width, edge)),
                image.crop((0, height - edge, width, height)),
                image.crop((0, edge, edge, height - edge)),
                image.crop((width - edge, edge, width, height - edge)),
            )
        )
        edge_pixels = 2 * width * edge + 2 * max(0, height - 2 * edge) * edge
        edge_ratio = edge_dark / max(1, edge_pixels)
        digest = hashlib.sha256(image.tobytes()).hexdigest()
        hashes[digest].append(number)

        if ink_ratio < 0.00035:
            blank_pages.append(number)
        # No normal page furniture reaches the outer 0.4% of the B5 sheet.
        # Page 1's editorial cover is allowed a deliberate edge treatment.
        if number != 1 and edge_ratio > 0.004:
            edge_intrusions.append({"page": number, "ratio": round(edge_ratio, 6)})

        records.append(
            {
                "page": number,
                "width": width,
                "height": height,
                "bytes": path.stat().st_size,
                "inkRatio": round(ink_ratio, 6),
                "edgeInkRatio": round(edge_ratio, 6),
            }
        )

    duplicate_groups = [numbers for numbers in hashes.values() if len(numbers) > 1]
    checks = {
        "pageCount": len(pages) == expected_pages,
        "continuousOrdinals": ordinals == expected,
        "uniformDimensions": len(dimensions) == 1,
        "noBlankPages": not blank_pages,
        "noOuterEdgeIntrusions": not edge_intrusions,
        "noExactDuplicatePages": not duplicate_groups,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "expectedPages": expected_pages,
        "actualPages": len(pages),
        "dimensions": [list(value) for value in sorted(dimensions)],
        "blankPages": blank_pages,
        "edgeIntrusions": edge_intrusions,
        "duplicateGroups": duplicate_groups,
        "records": records,
    }


def contact_sheets(directory: Path, output: Path, per_sheet: int = 20) -> int:
    pages = []
    for path in directory.glob("page-*.png"):
        match = PAGE_RE.match(path.name)
        if match:
            pages.append((int(match.group(1)), path))
    pages.sort()
    output.mkdir(parents=True, exist_ok=True)

    cols, rows = 5, 4
    thumb_w, thumb_h, label_h, gutter = 210, 297, 22, 12
    sheet_w = cols * (thumb_w + gutter) + gutter
    sheet_h = rows * (thumb_h + label_h + gutter) + gutter
    font = ImageFont.load_default()

    count = 0
    for start in range(0, len(pages), per_sheet):
        group = pages[start : start + per_sheet]
        sheet = Image.new("RGB", (sheet_w, sheet_h), "#d7d1c8")
        draw = ImageDraw.Draw(sheet)
        for index, (number, path) in enumerate(group):
            row, col = divmod(index, cols)
            x = gutter + col * (thumb_w + gutter)
            y = gutter + row * (thumb_h + label_h + gutter)
            with Image.open(path) as source:
                thumb = source.convert("RGB")
                thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            px = x + (thumb_w - thumb.width) // 2
            py = y + (thumb_h - thumb.height) // 2
            sheet.paste(thumb, (px, py))
            draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline="#70685f", width=1)
            draw.text((x + 3, y + thumb_h + 4), f"Page {number}", fill="#201c18", font=font)
        first, last = group[0][0], group[-1][0]
        sheet.save(output / f"pages-{first:03d}-{last:03d}.png", optimize=True)
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--expected-pages", type=int, default=365)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--contact-sheets", type=Path)
    args = parser.parse_args()

    report = analyze(args.directory, args.expected_pages)
    if args.contact_sheets:
        report["contactSheetCount"] = contact_sheets(args.directory, args.contact_sheets)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("passed", "checks", "actualPages", "dimensions", "blankPages", "edgeIntrusions", "duplicateGroups")}, ensure_ascii=False))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
