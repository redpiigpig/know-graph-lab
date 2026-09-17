# -*- coding: utf-8 -*-
"""從《繪本通俗三國志》（葛飾戴斗繪，江戶刊本）抽出插圖。

國會圖書館掃描本共 198 卷放在維基共享資源，全部公有領域，但都是整卷 PDF
（合計 9.5 GB）。不必下載整卷——MediaWiki 會把 PDF 的單頁算成縮圖，
用 iiurlparam=pageN-WIDTHpx 就能一頁一頁取。

每卷約 61 頁，多數是密排文字的對開頁，插圖嵌在其中。流程是
**接觸表人工挑頁**：

    --sheet 1            # 掃全卷出一張接觸表，人眼挑出有插圖的頁
    --volume 1 --pages 13 16 18 25   # 取那幾頁的高解析整頁

🚨 不要再嘗試自動判讀插圖頁。試過三種判準都分不開：
   區塊墨量變異數、每欄墨量變異係數、欄距自相關峰值。
   實測文字頁中位 0.27–0.69、插圖頁 0.00–0.38，區間完全重疊——
   因為直排文字欄間本來就有大量留白，而版畫的排線又有自己的週期。
   61 頁的卷子會被判成 60 頁都有圖。人眼看接觸表三秒就分得出來。

整頁取用不裁切：書頁帶著旁邊的文字更像原書，放進簡報也好看，
而且省掉「裁到一半」這種看起來成功的失敗。
"""
import argparse
import io
import json
import os
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "know-graph-lab tutoring slides/1.0 (redpiigpig@gmail.com)"}
OUT = r"G:\我的雲端硬碟\資料\知識圖工作室\教學\家教_三國演義\_圖庫\ehon"
# 🚨 判斷一定要在夠高的解析度做：260px 的對開頁每半只有 130px 寬，
#    日文直行糊成一片，變異係數分不出文字與圖畫（實測 61 頁全被判成圖）。
PAGE_PX = 1500
BLOCK = 16               # 區塊墨量用的格子邊長（低解析圖上）
MIN_RATIO = 1.45         # 一半的變異數要比另一半大這麼多才算是圖


def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as fh:
        return json.load(fh)


def volume_titles():
    r = api({"action": "query", "format": "json", "list": "categorymembers",
             "cmtype": "file", "cmtitle": "Category:絵本通俗三国志", "cmlimit": "500"})
    pdfs = [m["title"] for m in r["query"]["categorymembers"]
            if m["title"].lower().endswith(".pdf")]
    return sorted(pdfs)


def page_thumb(title, n, px):
    r = api({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
             "iiprop": "url", "iiurlwidth": str(px), "iiurlparam": "page%d-%dpx" % (n, px)})
    ii = list(r["query"]["pages"].values())[0].get("imageinfo")
    return ii[0].get("thumburl") if ii else None


def page_count(title):
    r = api({"action": "query", "format": "json", "titles": title,
             "prop": "imageinfo", "iiprop": "size"})
    return list(r["query"]["pages"].values())[0]["imageinfo"][0].get("pagecount", 0)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as fh:
        return fh.read()


def block_variance(im):
    """區塊墨量的變異數：文字均勻→小，圖畫有大黑大白→大。"""
    g = im.convert("L")
    w, h = g.size
    cols, rows = max(1, w // BLOCK), max(1, h // BLOCK)
    small = g.resize((cols, rows), Image.BOX)
    px = list(small.getdata())
    n = len(px)
    mean = sum(px) / n
    return sum((p - mean) ** 2 for p in px) / n


BAND = 26          # 一條水平帶的高度（1100px 頁面上）
TEXT_CV = 0.55     # 每欄墨量的變異係數：低於此視為文字帶
MIN_RUN = 0.55     # 圖畫帶要連續佔到半頁高度的幾成才收
INK_LO, INK_HI = 0.04, 0.72   # 太白＝空白頁，太黑＝封面或污損


def _cols_ink(im):
    """每一欄的墨量（0..1）。"""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    out = []
    step = max(1, h // 60)          # 取樣，不必每一列都算
    for x in range(w):
        s = 0
        n = 0
        for y in range(0, h, step):
            s += 255 - px[x, y]
            n += 1
        out.append(s / (255.0 * n))
    return out


def _is_text_band(im):
    """文字帶：每一欄的墨量都差不多（字級一致、行列整齊）→ 變異係數低。
    圖畫帶：墨集中在某些欄 → 變異係數高。"""
    c = _cols_ink(im)
    if not c:
        return True
    mean = sum(c) / len(c)
    if mean < 0.02:                  # 整條空白，當成文字帶（不要）
        return True
    var = sum((v - mean) ** 2 for v in c) / len(c)
    return (var ** .5) / mean < TEXT_CV


def find_plate(im):
    """在一整頁（兩面對開）裡找出插圖區塊，回傳 (l,t,r,b) 相對比例；找不到回 None。"""
    w, h = im.size
    im = im.crop((int(w * .03), int(h * .04), int(w * .97), int(h * .96)))
    W, H = im.size
    best = None
    for half, (x0, x1) in (("L", (0, W // 2)), ("R", (W // 2, W))):
        sub = im.crop((x0, 0, x1, H))
        g = sub.convert("L")
        ink = 1 - (sum(g.resize((40, 40), Image.BOX).getdata()) / (255.0 * 1600))
        if not (INK_LO < ink < INK_HI):
            continue                  # 空白頁或整片黑的封面
        flags = []
        for y in range(0, H - BAND, BAND):
            flags.append(_is_text_band(sub.crop((0, y, x1 - x0, y + BAND))))
        # 最長的一段連續「非文字」帶
        run = bestrun = 0
        end = bestend = 0
        for i, is_text in enumerate(flags):
            if is_text:
                run = 0
            else:
                run += 1
                end = i
                if run > bestrun:
                    bestrun, bestend = run, end
        if not bestrun:
            continue
        cover = bestrun * BAND / float(H)
        if cover < MIN_RUN:
            continue
        top = (bestend + 1 - bestrun) * BAND
        bot = (bestend + 1) * BAND
        cand = (cover, (x0 / float(W), top / float(H), x1 / float(W), bot / float(H)))
        if not best or cand[0] > best[0]:
            best = cand
    return best[1] if best else None


def sheet(title, vol_no, out_dir):
    """掃全卷出一張接觸表，供人眼挑頁。"""
    from PIL import ImageDraw, ImageFont
    n = page_count(title)
    tag = "v%03d" % vol_no
    tmp = os.path.join(os.environ.get("TEMP", "."), "ehon_scan", tag)
    os.makedirs(tmp, exist_ok=True)

    def grab(p):
        fp = os.path.join(tmp, "p%03d.jpg" % p)
        if os.path.exists(fp):
            return fp
        try:
            u = page_thumb(title, p, 260)
            if not u:
                return None
            io.open(fp, "wb").write(get(u))
            return fp
        except Exception:
            return None

    with ThreadPoolExecutor(6) as ex:
        files = [f for f in ex.map(grab, range(1, n + 1)) if f]
    CELL, COLS = 175, 11
    rows = (len(files) + COLS - 1) // COLS
    sh = Image.new("RGB", (COLS * (CELL + 5) + 5, rows * (CELL + 14 + 5) + 5), "#FFF")
    dr = ImageDraw.Draw(sh)
    try:
        fnt = ImageFont.truetype(r"C:\Windows\Fonts\msjh.ttc", 11)
    except Exception:
        fnt = ImageFont.load_default()
    for i, fp in enumerate(files):
        r, c = divmod(i, COLS)
        x, y = 5 + c * (CELL + 5), 5 + r * (CELL + 14 + 5)
        im = Image.open(fp).convert("RGB")
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        sh.paste(im, (x + (CELL - im.width) // 2, y + (CELL - im.height) // 2))
        dr.rectangle([x, y, x + CELL, y + CELL], outline="#CCC")
        dr.text((x + 2, y + CELL + 2), os.path.basename(fp)[1:-4], fill="#000", font=fnt)
    dest = os.path.join(out_dir, "sheet_%s.png" % tag)
    sh.save(dest)
    print("  卷 %d 共 %d 頁 → %s" % (vol_no, n, dest))
    return dest


def pull_pages(title, vol_no, pages):
    """取指定頁的高解析整頁。"""
    os.makedirs(OUT, exist_ok=True)
    tag = "v%03d" % vol_no

    def one(p):
        dest = os.path.join(OUT, "%s_p%03d.jpg" % (tag, p))
        if os.path.exists(dest):
            return dest
        try:
            u = page_thumb(title, p, PAGE_PX)
            if not u:
                return None
            im = Image.open(io.BytesIO(get(u)))
            w, h = im.size
            im = im.crop((int(w * .03), int(h * .04), int(w * .97), int(h * .96)))
            im.convert("RGB").save(dest, "JPEG", quality=88, optimize=True)
            return dest
        except Exception:
            return None

    with ThreadPoolExecutor(5) as ex:
        got = [g for g in ex.map(one, pages) if g]
    print("  卷 %d 取出 %d / %d 頁" % (vol_no, len(got), len(pages)))
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="列出所有卷")
    ap.add_argument("--sheet", nargs="+", type=int, metavar="VOL",
                    help="出接觸表供人眼挑頁")
    ap.add_argument("--volume", type=int, help="要取頁的卷序")
    ap.add_argument("--pages", nargs="+", type=int, help="要取的頁碼")
    ap.add_argument("--out", default=os.environ.get("TEMP", "."), help="接觸表放哪")
    a = ap.parse_args()
    titles = volume_titles()
    if a.list:
        for i, t2 in enumerate(titles, 1):
            print("%3d  %s" % (i, t2[5:]))
    elif a.sheet:
        for v in a.sheet:
            sheet(titles[v - 1], v, a.out)
    elif a.volume and a.pages:
        pull_pages(titles[a.volume - 1], a.volume, a.pages)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
