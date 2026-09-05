# -*- coding: utf-8 -*-
"""從預告片抓分鏡截圖：偵測鏡頭切換 → 取切換後穩定的那一格 → 存原解析度 jpg。

同時輸出接觸表（contact sheet），每張 5x4 格、寬 1900px，用來人工挑圖。
"""
import argparse
import json
from pathlib import Path

import cv2

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
SRC = PROJ / "素材" / "預告片"      # 由 --src 覆寫
OUT = SRC / "截圖"
SHEETS = SRC / "接觸表"

STRIDE = 3          # 每 3 格比一次，夠敏感也夠快
CORR_CUT = 0.72     # 直方圖相關係數低於此視為換鏡頭
SETTLE = 0.35       # 切換後等 0.35 秒再取，避開轉場糊掉的那幾格
MIN_GAP = 0.7       # 兩張截圖至少間隔
MAX_PER_VIDEO = 60


def hist(frame):
    small = cv2.resize(frame, (160, 90))
    h = cv2.calcHist([cv2.cvtColor(small, cv2.COLOR_BGR2HSV)], [0, 1], None, [32, 32], [0, 180, 0, 256])
    return cv2.normalize(h, h).flatten()


def usable(frame) -> bool:
    m = frame.mean()
    return 18 < m < 246


def shots_from(path: Path) -> list[dict]:
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    prev, last_t, out = None, -99.0, []
    idx = 0
    pending = None  # (取樣時間)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = idx / fps
        if pending is not None and t >= pending:
            if usable(frame) and t - last_t >= MIN_GAP:
                name = f"{path.stem}_{int(t*1000):06d}.jpg"
                # cv2.imwrite 遇到中文路徑會靜默失敗，改用 imencode 自己寫
                ok_enc, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                if not ok_enc:
                    idx += 1
                    continue
                (OUT / name).write_bytes(buf.tobytes())
                out.append(dict(file=name, video=path.stem, t=round(t, 2)))
                last_t = t
            pending = None
        if idx % STRIDE == 0:
            h = hist(frame)
            if prev is not None:
                corr = cv2.compareHist(prev, h, cv2.HISTCMP_CORREL)
                if corr < CORR_CUT and pending is None and len(out) < MAX_PER_VIDEO:
                    pending = t + SETTLE
            prev = h
        idx += 1
    cap.release()
    print(f"  {path.name}: {total} 格 / {fps:.1f}fps → {len(out)} 張")
    return out


def contact_sheets(shots: list[dict], cols=5, rows=4, cell_w=380):
    from PIL import Image, ImageDraw
    SHEETS.mkdir(parents=True, exist_ok=True)
    cell_h = int(cell_w * 9 / 16)
    per = cols * rows
    made = []
    for page in range((len(shots) + per - 1) // per):
        chunk = shots[page * per:(page + 1) * per]
        sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + 24)), "#111111")
        draw = ImageDraw.Draw(sheet)
        for k, s in enumerate(chunk):
            im = Image.open(OUT / s["file"]).convert("RGB").resize((cell_w, cell_h))
            cx, cy = (k % cols) * cell_w, (k // cols) * (cell_h + 24)
            sheet.paste(im, (cx, cy))
            draw.text((cx + 6, cy + cell_h + 5), f"[{s['n']:03d}] {s['video']} {s['t']:.1f}s", fill="#eeeeee")
        p = SHEETS / f"接觸表_{page + 1:02d}.jpg"
        sheet.save(p, quality=88)
        made.append(p.name)
    return made


def main():
    global SRC, OUT, SHEETS
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(SRC), help="放 mp4 的資料夾")
    args = ap.parse_args()
    SRC = Path(args.src)
    OUT, SHEETS = SRC / "截圖", SRC / "接觸表"
    OUT.mkdir(parents=True, exist_ok=True)
    all_shots = []
    for mp4 in sorted(SRC.glob("*.mp4")):
        all_shots += shots_from(mp4)
    for n, s in enumerate(all_shots, 1):
        s["n"] = n
    (SRC / "截圖索引.json").write_text(json.dumps(all_shots, ensure_ascii=False, indent=1), encoding="utf-8")
    sheets = contact_sheets(all_shots)
    print(f"總計 {len(all_shots)} 張截圖，接觸表 {len(sheets)} 頁")


if __name__ == "__main__":
    main()
