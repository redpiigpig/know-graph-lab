"""Build compact contact sheets from page-*.png render output for visual QA."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def page_number(path: Path) -> int:
    return int(path.stem.rsplit("-", 1)[-1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--rows", type=int, default=5)
    args = parser.parse_args()

    pages = sorted(args.render_dir.glob("page-*.png"), key=page_number)
    if not pages:
        raise SystemExit(f"no rendered pages in {args.render_dir}")
    out_dir = args.render_dir / "contact_sheets"
    out_dir.mkdir(exist_ok=True)
    per_sheet = args.cols * args.rows
    thumb_w, thumb_h, label_h, gap = 220, 312, 24, 12
    font = ImageFont.load_default()
    for start in range(0, len(pages), per_sheet):
        batch = pages[start:start + per_sheet]
        sheet = Image.new(
            "RGB",
            (
                gap + args.cols * (thumb_w + gap),
                gap + args.rows * (thumb_h + label_h + gap),
            ),
            "#d9d5cc",
        )
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(batch):
            row, col = divmod(index, args.cols)
            x = gap + col * (thumb_w + gap)
            y = gap + row * (thumb_h + label_h + gap)
            with Image.open(path) as page:
                page = page.convert("RGB")
                page.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                px = x + (thumb_w - page.width) // 2
                py = y + (thumb_h - page.height) // 2
                sheet.paste(page, (px, py))
            label = f"physical page {page_number(path)}"
            draw.text((x + 4, y + thumb_h + 4), label, fill="black", font=font)
        first, last = page_number(batch[0]), page_number(batch[-1])
        sheet.save(out_dir / f"pages-{first:03d}-{last:03d}.jpg", quality=88)
    print(f"{len(pages)} pages -> {len(list(out_dir.glob('*.jpg')))} contact sheets")


if __name__ == "__main__":
    main()
