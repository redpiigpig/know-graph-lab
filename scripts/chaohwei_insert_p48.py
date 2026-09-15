"""把使用者補拍的印刷頁 48 插進《初期唯識思想》的工作檔與 OCR 快取。

原掃描漏翻了這一頁（工作 PDF 第 33 張的上半是頁 47、下半是頁 49）。使用者
2026-09-15 補拍照片，見 Downloads/48頁.jpg（一張裡有 48、49 兩頁）。

🚨 這一頁的文字是**人工逐字讀出來的，不是跑 OCR**。照片有透視、弧度與不勻的
光，chaohwei_ocr.py 那條管線是照平面掃描設計的，對照片不保險（使用者指出）。

work_page 是 int 且 load_cache 按它排序、page_quality 又拿它當 work.pdf 的頁
索引，所以插在中間就必須整體重編：66..300 → 67..301。卷首那幾頁的硬編碼
（SKIP_WP={1}、FRONT_MATTER 的 wp1–16）全都在 66 之前，不受影響。
"""

import json
import shutil
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path("c:/tmp/chaohwei_vijnapti")
WORK = BASE / "work.pdf"
OCR = BASE / "ocr"
PHOTO = Path.home() / "Downloads" / "48頁.jpg"
NEW_WP = 66  # 頁 47 是 wp65，所以頁 48 插在 wp66

# ── 人工轉錄（半形標點，與 OCR 快取同風格；build 的 _HALF2FULL 會轉全形）──
TEXT = """距,吾人必須看透語文這樣的特性,進而超越它,使自己的心情不跟著它轉。這是「名假施設」之教對於修道的提撕。
「受假」,則是強調世間一切皆是因緣生法。一法的生起,固然是由於眾多因緣聚合,一法的滅去,也是眾多因緣離散使然。所有的一切,皆是因緣條件下的存在,沒有一法可不靠其他因緣而單獨生起。既屬因緣和合,也就沒有獨立不變而真實的自體存在。「受假」的施教重點,在於破除修道者牢固的自性見,使其明瞭自身只是蘊處界的聚集,沒有常恆不變的自性存在。
「法假」,則是強調因緣和合的一切,沒有終極的實在可言,其重點在於破除聲聞部派中「假必依實」論者所安立的極微與剎那,這是《大般若經》提出三假的用意。
中觀學中有「唯名」、「唯表」,而唯識學中的vijñapti mātratā,也是「唯表」之意,此外,唯識學「入所知相」的「四尋思」中,也有「名尋思」一法[^18]。雖然中觀與唯識皆有「唯表」與「唯名」之詞彙與意涵,但他們所要強調的重點卻是不同的。
[^18]: 「由何、云何而得悟入?由聞熏習種類如理作意所攝似法似義有見意言;由四尋思,謂由名、義、自性、差別假立尋思;及由四種如實遍智,謂由名、事、自性、差別假立如實遍智,如是皆同不可得故。」(《攝大乘論》卷中,大正三一・一四二下)"""


def make_page_image() -> Path:
    """照片 → 轉正 → 取右半（頁 48）→ 去木桌與手指 → 提對比。"""
    im = Image.open(PHOTO).transpose(Image.ROTATE_90)
    w, h = im.size
    page = im.crop((w // 2, 15, w // 2 + 655, 1055))
    page = ImageOps.autocontrast(page.convert("L"), cutoff=1)
    tw = 1632  # 與其他工作頁同級
    page = page.resize((tw, int(page.height * tw / page.width)), Image.LANCZOS)
    out = BASE / "p48_inserted.png"
    page.convert("RGB").save(out)
    return out


def main() -> None:
    assert WORK.exists() and OCR.exists() and PHOTO.exists(), "來源不齊"
    doc = fitz.open(WORK)
    n_before = len(doc)
    assert n_before == 300, f"work.pdf 應為 300 頁，實得 {n_before}"

    # 1) 造出這一頁的 PDF 頁面，尺寸比照鄰頁高度
    img = make_page_image()
    with Image.open(img) as probe:
        iw, ih = probe.size
    height = doc[64].rect.height  # wp65（頁 47）的高度
    width = height * iw / ih
    tmp = fitz.open()
    pg = tmp.new_page(width=width, height=height)
    pg.insert_image(pg.rect, filename=str(img))

    # 2) 插到第 66 頁（0-based index 65）
    doc.insert_pdf(tmp, from_page=0, to_page=0, start_at=65)
    assert len(doc) == 301, len(doc)
    doc.save(str(BASE / "work.new.pdf"))
    doc.close()
    tmp.close()

    # 3) 快取重編 66..300 → 67..301（由大到小，避免蓋掉）
    moved = 0
    for wp in range(300, NEW_WP - 1, -1):
        src = OCR / f"{wp:03d}.json"
        if not src.exists():
            continue
        rec = json.loads(src.read_text(encoding="utf-8"))
        assert rec["work_page"] == wp, (wp, rec["work_page"])
        rec["work_page"] = wp + 1
        (OCR / f"{wp + 1:03d}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        moved += 1

    # 4) 寫入頁 48
    (OCR / f"{NEW_WP:03d}.json").write_text(json.dumps({
        "work_page": NEW_WP,
        "format": "v2",
        "printed": "48",
        "header": "初期唯識思想",
        "text": TEXT,
        "source": "photo-2026-09-15-manual",  # 人工轉錄，非 OCR
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    shutil.move(str(BASE / "work.new.pdf"), str(WORK))
    print(f"work.pdf {n_before} → 301 頁；快取重編 {moved} 檔；已寫入 wp{NEW_WP}＝印刷頁 48")


if __name__ == "__main__":
    main()
