# -*- coding: utf-8 -*-
"""把圖庫排成接觸表，用來一眼檢查有沒有抓錯圖／浮水印／內容不符。

授權過了不代表圖是對的：jadeseal 就曾被標成「玉璽圖示」，其實是整幅
「孫堅背約奪玉璽」版畫。規模大了一定要能整批看。

用法：
    python -X utf8 scripts/sanguo_contact_sheet.py            # 全部
    python -X utf8 scripts/sanguo_contact_sheet.py --keys rtk2,rtk3
"""
import argparse, io, json, os
from PIL import Image, ImageDraw, ImageFont

LIB = r"G:\我的雲端硬碟\資料\知識圖工作室\教學\家教_三國演義\_圖庫"
CELL, COLS, PAD, LABEL = 180, 10, 6, 22
FONTS = [r"C:\Windows\Fonts\msjh.ttc", r"C:\Windows\Fonts\mingliu.ttc", r"C:\Windows\Fonts\simsun.ttc"]


def font(size):
    for f in FONTS:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", help="只看這幾個 key，逗號分隔")
    ap.add_argument("--out", default=os.path.join(os.environ.get("TEMP", "."), "sanguo_sheet"))
    a = ap.parse_args()

    lib = json.load(io.open(os.path.join(LIB, "credits.json"), encoding="utf-8"))
    keys = a.keys.split(",") if a.keys else sorted(lib)
    keys = [k for k in keys if k in lib]
    fnt, fnt2 = font(13), font(11)

    pages, per = [], COLS * 5
    for start in range(0, len(keys), per):
        chunk = keys[start:start + per]
        rows = (len(chunk) + COLS - 1) // COLS
        W = COLS * (CELL + PAD) + PAD
        H = rows * (CELL + LABEL + PAD) + PAD
        sheet = Image.new("RGB", (W, H), "#F4F1EA")
        d = ImageDraw.Draw(sheet)
        for i, k in enumerate(chunk):
            r, c = divmod(i, COLS)
            x = PAD + c * (CELL + PAD)
            y = PAD + r * (CELL + LABEL + PAD)
            try:
                im = Image.open(os.path.join(LIB, "images", lib[k]["file"])).convert("RGB")
                im.thumbnail((CELL, CELL), Image.LANCZOS)
                sheet.paste(im, (x + (CELL - im.width) // 2, y + (CELL - im.height) // 2))
            except Exception as e:
                d.text((x + 4, y + 4), "讀不到\n%s" % e, fill="#C4331C", font=fnt2)
            d.rectangle([x, y, x + CELL, y + CELL], outline="#C9BFA8")
            d.text((x + 2, y + CELL + 2), k, fill="#191410", font=fnt)
            d.text((x + 2, y + CELL + 12), lib[k]["desc"][:13], fill="#574E44", font=fnt2)
        p = "%s_%d.png" % (a.out, len(pages) + 1)
        sheet.save(p)
        pages.append(p)
        print("  %s  (%d 張, %dx%d)" % (p, len(chunk), W, H))
    print("共 %d 頁" % len(pages))


if __name__ == "__main__":
    main()
