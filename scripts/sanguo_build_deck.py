"""把一回的投影片定義組成可離線放的單檔 HTML 簡報。

投影片定義放 scripts/sanguo_decks/rNN.py，只寫內容；版面、翻頁、
講稿面板、圖片來源面板、Q 版人物 SVG 產生器都在共用樣板
scripts/templates/sanguo_deck.html 裡，十六回一致。

圖片不用自己列：本工具會掃投影片內容裡的 ph()／pc()／mp()／ic()／im()
用到哪些 key，只把那幾張從 Drive 圖庫嵌進去，並自動產生 CREDIT。
少一張、拼錯一個 key，組版當場失敗，不會出一份圖是破的簡報。

用法：
    python -X utf8 scripts/sanguo_build_deck.py r05
    python -X utf8 scripts/sanguo_build_deck.py r05 --out C:/tmp/r05.html
"""
import argparse
import base64
import importlib.util
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "scripts", "templates", "sanguo_deck.html")
DECKS = os.path.join(ROOT, "scripts", "sanguo_decks")
LIB = r"G:\我的雲端硬碟\資料\知識圖工作室\教學\家教_三國演義\_圖庫"

MIME = {"jpg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}

# 投影片內容裡引用素材的寫法
RE_PHOTO = re.compile(r'\b(?:ph|pc|mp)\(\s*"(\w+)"')
RE_EMOJI = re.compile(r'\b(?:ic|im)\(\s*"(\w+)"')


def load_deck(name):
    path = os.path.join(DECKS, name + ".py")
    if not os.path.exists(path):
        sys.exit("找不到投影片定義：%s" % path)
    spec = importlib.util.spec_from_file_location("deck_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for attr in ("TITLE", "MARK", "SUB", "SLIDES"):
        if not hasattr(mod, attr):
            sys.exit("%s 少了 %s" % (path, attr))
    return mod


MAX_EDGE = 1400          # 簡報最大顯示約 800px，放大檢視留一倍
MAX_BYTES = 200 * 1024   # 單張上限；超過就降級重存


def shrink(path):
    """把太大的圖壓到簡報用得上的尺寸。

    圖庫存的是原始檔（要保留），這裡只在組版時降級。線稿版畫轉 JPEG
    會糊掉邊緣，所以先試著縮尺寸、維持 PNG；還是太大才轉 JPEG。
    """
    from PIL import Image

    raw = io.open(path, "rb").read()
    ext = path.rsplit(".", 1)[-1].lower()
    if len(raw) <= MAX_BYTES:
        return raw, ext

    im = Image.open(io.BytesIO(raw))
    if max(im.size) > MAX_EDGE:
        ratio = MAX_EDGE / float(max(im.size))
        im = im.resize((max(1, int(im.width * ratio)), max(1, int(im.height * ratio))),
                       Image.LANCZOS)

    if ext == "png":
        buf = io.BytesIO()
        im.convert("P", palette=Image.ADAPTIVE, colors=64).save(buf, "PNG", optimize=True)
        if buf.tell() <= MAX_BYTES:
            return buf.getvalue(), "png"

    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    return buf.getvalue(), "jpg"


def data_uri(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext not in MIME:
        sys.exit("不支援的圖檔格式：%s" % path)
    raw, ext = shrink(path)
    return "data:%s;base64,%s" % (MIME[ext], base64.b64encode(raw).decode("ascii")), len(raw)


def js_obj(pairs):
    """產生 const X={k:"v",...} 的內容，一行一個 key，方便 diff。"""
    return "{\n" + ",\n".join('%s:"%s"' % (k, v) for k, v in pairs) + "}"


def js_credit(items):
    body = ",\n".join(' %s:["%s","%s"]' % (k, d.replace('"', '\\"'), l.replace('"', '\\"'))
                      for k, d, l in items)
    return "{\n" + body + "\n}"


def build(name, out_path=None):
    deck = load_deck(name)
    tpl = io.open(TEMPLATE, encoding="utf-8").read()
    credits = json.load(io.open(os.path.join(LIB, "credits.json"), encoding="utf-8"))
    emoji = json.load(io.open(os.path.join(LIB, "emoji.json"), encoding="utf-8"))

    # 投影片：html 直接當 JS 模板字串塞進去，和現有四回同一種寫法
    slides_js = "[\n" + ",\n".join(
        "{%shtml:`%s`,\n note:`%s`}" % ("cover:1,\n " if s.get("cover") else "",
                                        s["html"].strip(), s["note"].strip())
        for s in deck.SLIDES) + "\n]"

    blob = slides_js
    photo_keys = sorted(set(RE_PHOTO.findall(blob)))
    emoji_keys = sorted(set(RE_EMOJI.findall(blob)))

    missing = [k for k in photo_keys if k not in credits]
    missing += ["(圖示)" + k for k in emoji_keys if k not in emoji]
    if missing:
        sys.exit("圖庫裡沒有這些 key，先補圖再組版：%s" % "、".join(missing))

    # 🚨 不重複閘：同一張照片不准出現在兩回。
    #    （OpenMoji 圖示不算，那是裝飾性符號，全套只有 36 個，硬要不重複沒有意義。）
    claim_path = os.path.join(LIB, "assignments.json")
    claims = json.load(io.open(claim_path, encoding="utf-8")) if os.path.exists(claim_path) else {}
    clash = [(k, claims[k]) for k in photo_keys if claims.get(k) not in (None, name)]
    if clash:
        sys.exit("這些圖已經被別回用掉了，換一張：\n" +
                 "\n".join("  %-16s 已用於 %s" % (k, d) for k, d in clash))
    for k in list(claims):
        if claims[k] == name and k not in photo_keys:
            del claims[k]          # 這一回改掉了就放開
    for k in photo_keys:
        claims[k] = name
    io.open(claim_path, "w", encoding="utf-8").write(
        json.dumps(claims, ensure_ascii=False, indent=1, sort_keys=True))

    img_pairs, credit_items, total = [], [], 0
    for k in photo_keys:
        v = credits[k]
        # 繪本插圖存在 ehon/ 子夾，credits 的 file 會帶斜線；其餘在 images/
        rel = v["file"]
        src = os.path.join(LIB, rel) if "/" in rel else os.path.join(LIB, "images", rel)
        uri, n = data_uri(src)
        img_pairs.append((k, uri))
        credit_items.append((k, v["desc"], v["license"]))
        total += n
    emo_pairs = []
    for k in emoji_keys:
        uri, n = data_uri(os.path.join(LIB, "emoji", emoji[k]["file"]))
        emo_pairs.append((k, uri))
        total += n

    html = tpl
    for ph, val in (("{{TITLE}}", deck.TITLE), ("{{MARK}}", deck.MARK), ("{{SUB}}", deck.SUB)):
        html = html.replace(ph, val)
    html = html.replace("{{EMO}}", js_obj(emo_pairs))
    html = html.replace("{{IMG}}", js_obj(img_pairs))
    html = html.replace("{{CREDIT}}", js_credit(credit_items))
    html = html.replace("{{SLIDES}}", slides_js)

    left = re.findall(r"\{\{(\w+)\}\}", html)
    if left:
        sys.exit("樣板還有沒填的佔位符：%s" % "、".join(left))

    out_path = out_path or os.path.join(
        os.environ.get("TEMP", "."), "sanguo_%s.html" % name)
    io.open(out_path, "w", encoding="utf-8").write(html)

    print("%s　%s" % (deck.TITLE, deck.SUB))
    print("  投影片 %d 頁" % len(deck.SLIDES))
    print("  照片 %d 張、圖示 %d 個，素材共 %.1f MB" % (
        len(photo_keys), len(emoji_keys), total / 1048576.0))
    print("  成品 %.1f MB → %s" % (os.path.getsize(out_path) / 1048576.0, out_path))
    if len(deck.SLIDES) != 20:
        print("  ⚠ 體例是 20 頁（封面 1 ＋ 內容 18 ＋ 收尾『今天哪些是編的』1）")
    if not deck.SLIDES[0].get("cover"):
        print("  ⚠ 第一頁沒有標 cover")
    if "編的" not in deck.SLIDES[-1]["html"]:
        print("  ⚠ 最後一頁不是『今天哪些是編的』")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck", help="投影片定義名稱，例如 r05")
    ap.add_argument("--out", help="輸出檔路徑")
    a = ap.parse_args()
    build(a.deck, a.out)


if __name__ == "__main__":
    main()
