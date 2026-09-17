# -*- coding: utf-8 -*-
"""把既有簡報 HTML 裡的某一張圖換成圖庫裡的另一張。

第一～四回是早期手寫的 HTML（不是 rNN.py 產的），沒辦法重新組版，
但它們彼此重複用圖（第二回 5 張有 3 張借自第一回）。本工具直接在
HTML 上動刀：換掉 IMG 的 base64、CREDIT 的說明與授權、以及內容裡
所有引用該 key 的地方。

用法：
    python -X utf8 scripts/sanguo_swap_image.py 檔案.html 舊key=新key [舊key=新key ...]
"""
import argparse
import base64
import io
import json
import os
import re
import sys

LIB = r"G:\我的雲端硬碟\資料\知識圖工作室\教學\家教_三國演義\_圖庫"
MIME = {"jpg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}
MAX_BYTES = 200 * 1024
MAX_EDGE = 1400


def load(key, credits):
    if key not in credits:
        sys.exit("圖庫裡沒有 %s" % key)
    v = credits[key]
    rel = v["file"]
    path = os.path.join(LIB, rel) if "/" in rel else os.path.join(LIB, "images", rel)
    raw = io.open(path, "rb").read()
    ext = path.rsplit(".", 1)[-1].lower()
    if len(raw) > MAX_BYTES:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        if max(im.size) > MAX_EDGE:
            r = MAX_EDGE / float(max(im.size))
            im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=84, optimize=True)
        raw, ext = buf.getvalue(), "jpg"
    uri = "data:%s;base64,%s" % (MIME[ext], base64.b64encode(raw).decode("ascii"))
    return uri, v["desc"], v["license"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("swaps", nargs="+", metavar="OLD=NEW")
    a = ap.parse_args()

    credits = json.load(io.open(os.path.join(LIB, "credits.json"), encoding="utf-8"))
    t = io.open(a.html, encoding="utf-8").read()

    for sw in a.swaps:
        old, new = sw.split("=")
        uri, desc, lic = load(new, credits)

        # 1) IMG 裡那一條的 base64
        pat = re.compile(r'(\b%s:")data:image/[a-z+]+;base64,[A-Za-z0-9+/=]+(")' % re.escape(old))
        t, n1 = pat.subn(lambda m: m.group(1) + uri + m.group(2), t, count=1)
        # 2) CREDIT 裡那一條
        pat2 = re.compile(r'(\b%s\s*:\s*\[)"[^"]*"\s*,\s*"[^"]*"(\])' % re.escape(old))
        t, n2 = pat2.subn(lambda m: '%s"%s","%s"%s' % (m.group(1), desc, lic, m.group(2)), t, count=1)
        # 3) IMG 與 CREDIT 的物件 key 本身（沒有引號，長這樣：slips:"data..." ）
        #    🚨 只改引用不改 key，會讓 IMG["新key"] 變 undefined，整份簡報當掉。
        t, n3 = re.subn(r'(^|[{,\s])%s(\s*:)' % re.escape(old),
                        lambda m: m.group(1) + new + m.group(2), t)
        # 4) 內容裡所有引用（ph/pc/mp 與 data-k）
        t, n4 = re.subn(r'("%s")' % re.escape(old), '"%s"' % new, t)

        if not (n1 and n2 and n3 >= 2):
            sys.exit("✗ %s 沒換成功（IMG %d / CREDIT %d / key %d）" % (old, n1, n2, n3))
        print("  %s → %s   %s" % (old, new, desc))

    io.open(a.html, "w", encoding="utf-8").write(t)
    print("寫回 %s（%.1f MB）" % (a.html, os.path.getsize(a.html) / 1048576.0))


if __name__ == "__main__":
    main()
