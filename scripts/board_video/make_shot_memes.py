# -*- coding: utf-8 -*-
"""用預告片畫面自製梗圖（memes.tw 那種：粗白字＋黑描邊，上或下）。

memes.tw 擋機器人抓取，模板本身也多半來自別人的影劇畫面；這支改用我們自己
抓下來的官方預告片分鏡當模板，跟影片其他部分同一套「評論引用」基礎，也不用等網站。

用法：
    python make_shot_memes.py                       # 產預設那批
    python make_shot_memes.py --shot 394 --top "無差別報復" --bottom "強者的正義觀"
編號就是接觸表左下角的 [NNN]。
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
IDX = PROJ / "素材" / "預告片" / "截圖索引.json"
SHOTS = PROJ / "素材" / "預告片" / "截圖"
OUT = PROJ / "素材" / "梗圖"
FONT = r"C:\Windows\Fonts\msjhbd.ttc"

# (檔名, 接觸表編號, 上方字, 下方字) —— 對著腳本裡的哏挑的
BATCH = [
    ("一百倍報酬", 224, "高達一百倍的報酬", "拉麵甜點吃到飽"),
    ("真正原因", 385, "", "招待大家上島的真正原因是？"),
    ("居民失蹤", 388, "島上的居民陸續遭到綁架", "但沒有人要說出兇手"),
    ("去討伐吧", 392, "去討伐那傢伙吧", "（沒說對手有多強）"),
    ("力量不對等", 394, "一尾巴打碎岩石", "這叫力量的不對等"),
    ("替死鬼", 398, "反正你們都來了", "就幫我們解決吧"),
    ("營火晚會", 260, "全島歡呼慶功", "只有吉伊知道真相"),
    ("沉默", 296, "", "他把秘密留在了心底"),
]


def draw_meme(src: Path, top: str, bottom: str, dest: Path, width=1280):
    im = Image.open(src).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)))
    d = ImageDraw.Draw(im)
    size = round(width * 0.062)
    font = ImageFont.truetype(FONT, size)

    def put(text, y, anchor):
        if not text:
            return
        # 太長就自己折行，memes.tw 也是這樣處理
        lines, cur = [], ""
        for ch in text:
            if d.textlength(cur + ch, font=font) > width * 0.92:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
        block = "\n".join(lines)
        d.multiline_text((width / 2, y), block, font=font, fill="white",
                         stroke_width=max(3, size // 12), stroke_fill="black",
                         anchor=anchor, align="center", spacing=10)

    put(top, round(im.height * 0.035), "ma")
    put(bottom, im.height - round(im.height * 0.035), "md")
    im.save(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", type=int, help="接觸表編號")
    ap.add_argument("--top", default="")
    ap.add_argument("--bottom", default="")
    ap.add_argument("--name", default="自訂")
    args = ap.parse_args()

    idx = {s["n"]: s for s in json.loads(IDX.read_text(encoding="utf-8"))}
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = [(args.name, args.shot, args.top, args.bottom)] if args.shot else BATCH
    for name, n, top, bottom in jobs:
        s = idx.get(n)
        if not s:
            print(f"  找不到編號 {n}")
            continue
        dest = OUT / f"梗圖_{name}.jpg"
        draw_meme(SHOTS / s["file"], top, bottom, dest)
        print(f"  {dest.name}  ←  [{n:03d}] {s['video']} {s['t']}s")


if __name__ == "__main__":
    main()
