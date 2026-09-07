# -*- coding: utf-8 -*-
"""卡片改成「寬度隨內容」之後，原本的座標會顯得太空。這支把整張板依實際卡片尺寸收緊。

作法：量到每張卡的真實寬高（由 _measure 產生的 sizes.json，或直接給預設值），
然後對所有座標找「不會互相重疊的最小縮放倍率」，重寫 spec 的 x/y 與 BOARD。
相對位置關係不變，只是整體靠攏。

用法：
    node measure_cards.mjs > sizes.json     # 先量（在瀏覽器裡量才準）
    python compact_layout.py --sizes sizes.json [--gap-x 220] [--gap-y 170] [--apply]
不加 --apply 只印出結果不改檔。
"""
import argparse
import json
import re
from pathlib import Path

SPEC = Path(__file__).parent / "spec_chiikawa.py"


def load_spec_nodes():
    src = SPEC.read_text(encoding="utf-8")
    nodes = []
    for m in re.finditer(r'dict\(id="(N\d+)".*?x=(\d+), y=(\d+), w=(\d+), h=(\d+),\s*\n\s*title="([^"]+)"',
                         src, re.S):
        nodes.append(dict(id=m.group(1), x=int(m.group(2)), y=int(m.group(3)),
                          w=int(m.group(4)), h=int(m.group(5)), title=m.group(6)))
    return src, nodes


def overlaps(a, b, gx, gy):
    return not (a["x2"] + gx <= b["x1"] or b["x2"] + gx <= a["x1"]
                or a["y2"] + gy <= b["y1"] or b["y2"] + gy <= a["y1"])


def try_scale(nodes, sizes, k, gx, gy):
    boxes = []
    for n in nodes:
        w, h = sizes.get(n["title"], (n["w"], n["h"]))
        boxes.append(dict(id=n["id"], x1=n["x"] * k, y1=n["y"] * k,
                          x2=n["x"] * k + w, y2=n["y"] * k + h))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if overlaps(boxes[i], boxes[j], gx, gy):
                return None
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="sizes.json")
    ap.add_argument("--gap-x", type=float, default=220)
    ap.add_argument("--gap-y", type=float, default=170)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    sizes = {k: tuple(v) for k, v in json.loads(Path(args.sizes).read_text(encoding="utf-8")).items()}
    src, nodes = load_spec_nodes()
    print(f"讀到 {len(nodes)} 個節點，量到 {len(sizes)} 張卡片尺寸")

    lo, hi, best = 0.30, 1.0, None
    for _ in range(24):                       # 二分找不重疊的最小倍率
        mid = (lo + hi) / 2
        boxes = try_scale(nodes, sizes, mid, args.gap_x, args.gap_y)
        if boxes:
            best, hi = (mid, boxes), mid
        else:
            lo = mid
    if not best:
        print("找不到可行倍率，請把 gap 調小")
        return
    k, boxes = best
    pad = 260
    minx = min(b["x1"] for b in boxes) - pad
    miny = min(b["y1"] for b in boxes) - pad
    bw = round(max(b["x2"] for b in boxes) - minx + pad)
    bh = round(max(b["y2"] for b in boxes) - miny + pad)
    print(f"倍率 {k:.3f}　板面 15200x9400 → {bw}x{bh}")

    newpos = {}
    for n in nodes:
        newpos[n["id"]] = (round(n["x"] * k - minx), round(n["y"] * k - miny))

    if not args.apply:
        for n in nodes[:6]:
            print(f"  {n['id']} {n['title'][:12]:14s} ({n['x']},{n['y']}) → {newpos[n['id']]}")
        print("  …（加 --apply 才會寫回 spec）")
        return

    out = src
    for nid, (x, y) in newpos.items():
        out = re.sub(rf'(dict\(id="{nid}".*?x=)\d+(, y=)\d+', rf'\g<1>{x}\g<2>{y}', out, flags=re.S)
    out = re.sub(r'BOARD = \{"w": \d+, "h": \d+\}', f'BOARD = {{"w": {bw}, "h": {bh}}}', out)
    SPEC.write_text(out, encoding="utf-8")
    print("已寫回 spec_chiikawa.py")


if __name__ == "__main__":
    main()
