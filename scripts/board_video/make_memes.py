# -*- coding: utf-8 -*-
"""梗圖素材兩條路（都不會有授權問題）：

A. 古典名畫反應圖 —— 吶喊／沉思者／創造亞當之類，全是公有領域，
   對這個頻道的調性也對得上（宗教學＋哲學）。抓自 Wikimedia Commons。
B. 多馬豬梗圖卡 —— 用自家吉祥物加大字，原創，零風險，還能建立辨識度。

網路上流行的那些梗圖（暴怒貓、社會建構的迷因模板…）多半有版權或授權不明，
所以不抓；要用的話請自行判斷合理使用。
"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
OUT = PROJ / "素材" / "梗圖"
UA = {"User-Agent": "know-graph-lab-video/1.0"}

# 名畫 → (Commons 搜尋詞, 什麼情緒／用在哪句)
PAINTINGS = {
    "吶喊": ("Edvard Munch The Scream", "崩潰／「這也太暗黑了吧」"),
    "沉思者": ("Rodin The Thinker sculpture", "思考／「所以誰才是反派？」"),
    "創造亞當": ("Michelangelo Creation of Adam", "人神契約／神力授予"),
    "最後的審判": ("Michelangelo Last Judgment", "天罰／報應"),
    "哭泣的赫拉克利特": ("Heraclitus weeping philosopher painting", "無奈／看破"),
    "巴別塔": ("Bruegel Tower of Babel", "僭越／人類的傲慢"),
    "大洪水": ("Deluge flood painting biblical", "神罰降臨"),
    "伊卡洛斯墜落": ("Fall of Icarus Bruegel", "自作自受／旁觀者的冷漠"),
}

# 多馬豬梗圖卡：(檔名, 大字, 小字)
PIG_CARDS = [
    ("毫無人性", "毫無人性", "—— 觀眾對 Nagano 老師的評價"),
    ("宇宙冥想", "走出戲院後\n我陷入了宇宙冥想", "多馬茶房・電影辯士"),
    ("誰是反派", "所以\n誰才是反派？", "第六幕：沒有絕對反派的倫理困境"),
    ("很弔詭", "這是不是\n很弔詭？", "第十一幕：共業的假設"),
    ("強者的正義", "強者的正義觀", "受害一次，復仇無限上綱"),
    ("替死鬼", "反正你們都來了", "島民的僥倖心態"),
    ("不求無傷的童年", "不求一個\n無傷的童年", "結語"),
]


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def commons_top(query: str):
    url = ("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": "6", "gsrlimit": "4",
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": "1600"}))
    try:
        data = get_json(url)
    except Exception as e:
        print(f"  查詢失敗 {query}: {e}")
        return None
    best = None
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        if not info.get("thumburl"):
            continue
        meta = info.get("extmetadata", {}) or {}
        lic = (meta.get("LicenseShortName", {}).get("value") or "").strip()
        if "fair" in lic.lower() or "non-free" in lic.lower():
            continue
        cand = dict(url=info["thumburl"], page=info.get("descriptionurl", ""), lic=lic or "公有領域",
                    artist=re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value") or "unknown").strip(),
                    idx=page.get("index", 99))
        if best is None or cand["idx"] < best["idx"]:
            best = cand
    return best


def fetch_paintings():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (q, usage) in PAINTINGS.items():
        hit = commons_top(q)
        if not hit:
            print(f"  {name}: 找不到")
            continue
        ext = Path(urllib.parse.urlparse(hit["url"]).path).suffix or ".jpg"
        dest = OUT / f"名畫_{name}{ext}"
        try:
            with urllib.request.urlopen(urllib.request.Request(hit["url"], headers=UA), timeout=90) as r:
                dest.write_bytes(r.read())
            rows.append((dest.name, hit["artist"], hit["lic"], usage, hit["page"]))
            print(f"  {name} ✓")
        except Exception as e:
            print(f"  {name} 下載失敗：{e}")
    return rows


def make_pig_cards():
    from PIL import Image, ImageDraw, ImageFont
    pig_path = PROJ / "素材" / "多馬豬" / "多馬豬.png"
    if not pig_path.exists():
        print("  找不到多馬豬，略過梗圖卡")
        return []
    pig = Image.open(pig_path).convert("RGBA")
    big = ImageFont.truetype(r"C:\Windows\Fonts\msjhbd.ttc", 96)
    small = ImageFont.truetype(r"C:\Windows\Fonts\msjh.ttc", 40)
    rows = []
    for fname, headline, sub in PIG_CARDS:
        im = Image.new("RGB", (1280, 720), "#12211c")
        d = ImageDraw.Draw(im)
        for i in range(0, 720, 9):          # 黑板刮痕
            d.line([(0, i), (1280, i)], fill="#16261f", width=1)
        p = pig.resize((360, 360))
        im.paste(p, (70, 190), p)
        # 量出標題實際佔多高再放小字，不然兩行標題會被小字壓到
        bbox = d.multiline_textbbox((0, 0), headline, font=big, spacing=22)
        blockh = bbox[3] - bbox[1]
        y = (720 - blockh - 70) // 2
        d.multiline_text((500, y), headline, font=big, fill="#fdf6e3", spacing=22)
        d.text((504, y + blockh + 34), sub, font=small, fill="#c9d8c4")
        dest = OUT / f"多馬豬_{fname}.png"
        im.save(dest)
        rows.append((dest.name, "自製", "原創（自家素材）", headline.replace("\n", " "), ""))
        print(f"  梗圖卡 {fname} ✓")
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("── 古典名畫反應圖（公有領域）──")
    rows = fetch_paintings()
    print("── 多馬豬梗圖卡（原創）──")
    rows += make_pig_cards()
    lines = ["檔名\t作者\t授權\t建議用在\t來源"]
    lines += ["\t".join(r) for r in rows]
    (OUT / "梗圖清單.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n共 {len(rows)} 張，清單寫在 {OUT / '梗圖清單.txt'}")


if __name__ == "__main__":
    main()
