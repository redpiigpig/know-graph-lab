# -*- coding: utf-8 -*-
"""精修用：把 NDL 跨頁切成左右單頁圖，並印出該頁的 OCR 文字。

逐字精修只能靠人（或有視覺的模型）把原圖與 OCR 並排看。這支只做準備工作：
  * 跨頁切成右／左兩張單頁（**右半先讀**，日文直書右起）
  * 長邊縮到 2000px 以內（超過會炸 session，見 [[feedback_screenshot_2000px]]）
  * 印出該影像的 OCR 文字，方便逐句對

    python scripts/ndl_proof_pages.py 1099766 --img 4

見 .claude/skills/ebook-collected-works/ndl_open_scans.md 的「逐字精修」一節。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import ndl_build as nb  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

MAX_SIDE = 2000


def make_halves(pid: str, img: int, out_dir: Path) -> list:
    from PIL import Image
    src = nb.CACHE_DIR / pid / ("%07d.jpg" % img)
    if not src.exists():
        raise SystemExit("找不到影像 %s（先跑 --fetch）" % src)
    im = Image.open(src)
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = []
    if nb.is_spread(*im.size):
        boxes = list(zip(["right", "left"], nb.split_spread_boxes(*im.size)))
    else:
        boxes = [("full", (0, 0) + im.size)]
    for name, box in boxes:
        c = im.crop(box)
        c.thumbnail((MAX_SIDE, MAX_SIDE))
        p = out_dir / ("p%03d_%s.jpg" % (img, name))
        c.save(p, quality=93)
        outs.append((name, p, c.size))
    return outs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pid")
    ap.add_argument("--img", type=int, required=True)
    ap.add_argument("--backend", default="gemini")
    ap.add_argument("--out", default=None, help="輸出目錄（預設放快取旁的 proof/）")
    args = ap.parse_args()

    out_dir = Path(args.out) if args.out else (nb.CACHE_DIR / args.pid / "proof")
    for name, p, size in make_halves(args.pid, args.img, out_dir):
        print("%-6s %s  %dx%d" % (name, p, size[0], size[1]))

    txt = nb.CACHE_DIR / args.pid / ("ocr-" + args.backend) / ("%07d.txt" % args.img)
    print("\n===== OCR（影像 %d）=====" % args.img)
    print(txt.read_text(encoding="utf-8") if txt.exists() else "(無 OCR 檔)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
