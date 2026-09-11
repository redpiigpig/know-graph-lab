#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""古典期宗教學者 54 本原著：清理 → 放進 Drive → 產出 registry。

為什麼要獨立一支：這批有 54 本（光弗雷澤《金枝》就四個版本二十一卷），
逐筆手寫進 pd_scholars_ingest.py 的 BOOKS 會讓那支腳本失控，而且檔名與中文題名的
對照關係本身就是資料，該存成資料檔。

所以這支做三件事：
  1. 用 archive_djvu_clean 清理（接回行尾軟連字號、收多重空格、刪頁碼書眉）
  2. 放進 Drive `全集/{學科}/{作家}/`
  3. 產出 `data/pd-scholars/classical.jsonl`，交 pd_scholars_ingest.py 建 row

🚨 中文題名是人工對的，不是從檔名機器轉的——《金枝》三版十二卷每一卷有自己的
部名（巫術之藝／禁忌／垂死之神／…），機器轉不出來，而版次與卷次弄錯比沒收更糟。

  python scripts/classical_scholars_place.py            # 預演
  python scripts/classical_scholars_place.py --apply
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("c:/tmp/pd_sources/classical2")
STUDIO = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集")
OUT = ROOT / "data" / "pd-scholars" / "classical.jsonl"

# 每位作者：(繁中名, 英文名, 學科, ebook_id 命名空間, 生年)
AUTHORS = {
    "frazer": ("詹姆斯‧喬治‧弗雷澤", "James George Frazer", "宗教學", "f4a21854"),
    "harrison": ("珍‧艾倫‧哈里森", "Jane Ellen Harrison", "宗教學", "4a881850"),
    "robertson-smith": ("威廉‧羅伯遜‧史密斯", "William Robertson Smith", "宗教學", "5b1a1846"),
    "simmel": ("齊美爾", "Georg Simmel", "宗教社會學", "51ee1858"),
    "soderblom": ("納坦‧瑟德布盧姆", "Nathan Söderblom", "宗教學", "50de1866"),
    "troeltsch": ("恩斯特‧特洛爾奇", "Ernst Troeltsch", "宗教社會學", "70e11865"),
}

# 檔名 stem → (繁中題名, 副題, 原文題名, 初版年, 這一份的年, 出版社, 出版地)
# 🚨 弗雷澤《金枝》四個版本並存，卷次與部名逐一核對過書名頁，不可合併。
WORKS: dict[str, tuple] = {
    # ── 弗雷澤 ────────────────────────────────────────────────
    "frazer_golden-bough_ed1-vol1of2_en_1890": (
        "金枝（初版‧卷一）", "巫術與宗教之研究", "The Golden Bough: A Study in Comparative Religion, Vol. 1",
        1890, 1890, "Macmillan", "London"),
    "frazer_golden-bough_ed1-vol2of2_en_1890": (
        "金枝（初版‧卷二）", "", "The Golden Bough, Vol. 2", 1890, 1890, "Macmillan", "London"),
    "frazer_golden-bough_ed2-vol1of3_en_1900": (
        "金枝（二版‧卷一）", "", "The Golden Bough: A Study in Magic and Religion, 2nd ed., Vol. 1",
        1900, 1900, "Macmillan", "London"),
    "frazer_golden-bough_ed2-vol2of3_en_1900": (
        "金枝（二版‧卷二）", "", "The Golden Bough, 2nd ed., Vol. 2", 1900, 1900, "Macmillan", "London"),
    "frazer_golden-bough_ed2-vol3of3_en_1900": (
        "金枝（二版‧卷三）", "", "The Golden Bough, 2nd ed., Vol. 3", 1900, 1900, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol01-magic-art_en_1911": (
        "金枝（三版‧卷一）巫術之藝與王之演進 上", "", "The Magic Art and the Evolution of Kings, Vol. 1",
        1911, 1911, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol02-magic-art_en_1911": (
        "金枝（三版‧卷二）巫術之藝與王之演進 下", "", "The Magic Art and the Evolution of Kings, Vol. 2",
        1911, 1911, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol03-taboo_en_1911": (
        "金枝（三版‧卷三）禁忌與靈魂之危", "", "Taboo and the Perils of the Soul",
        1911, 1911, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol04-dying-god_en_1911": (
        "金枝（三版‧卷四）垂死之神", "", "The Dying God", 1911, 1911, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol05-adonis-attis-osiris_en_1914": (
        "金枝（三版‧卷五）阿多尼斯‧阿提斯‧奧西里斯 上", "", "Adonis Attis Osiris, Vol. 1",
        1914, 1914, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol06-adonis-attis-osiris_en_1914": (
        "金枝（三版‧卷六）阿多尼斯‧阿提斯‧奧西里斯 下", "", "Adonis Attis Osiris, Vol. 2",
        1914, 1914, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol07-spirits-of-the-corn_en_1912": (
        "金枝（三版‧卷七）穀精與野靈 上", "", "Spirits of the Corn and of the Wild, Vol. 1",
        1912, 1912, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol08-spirits-of-the-corn_en_1912": (
        "金枝（三版‧卷八）穀精與野靈 下", "", "Spirits of the Corn and of the Wild, Vol. 2",
        1912, 1912, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol09-scapegoat_en_1913": (
        "金枝（三版‧卷九）代罪羔羊", "", "The Scapegoat", 1913, 1913, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol10-balder_en_1913": (
        "金枝（三版‧卷十）美麗的巴德爾 上", "", "Balder the Beautiful, Vol. 1",
        1913, 1913, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol11-balder_en_1913": (
        "金枝（三版‧卷十一）美麗的巴德爾 下", "", "Balder the Beautiful, Vol. 2",
        1913, 1913, "Macmillan", "London"),
    "frazer_golden-bough_ed3-vol12-bibliography-index_en_1915": (
        "金枝（三版‧卷十二）書目與總索引", "", "Bibliography and General Index",
        1915, 1915, "Macmillan", "London"),
    "frazer_golden-bough_abridged-1vol_en_1922": (
        "金枝（一卷節本）", "作者自行刪節，流傳最廣的版本", "The Golden Bough: A Study in Magic and Religion, Abridged Edition",
        1922, 1922, "Macmillan", "London"),
    "frazer_folk-lore-old-testament_vol1of3_en_1918": (
        "舊約民俗學（卷一）", "宗教、律法與習俗的比較研究", "Folk-Lore in the Old Testament, Vol. 1",
        1918, 1918, "Macmillan", "London"),
    "frazer_folk-lore-old-testament_vol2of3_en_1918": (
        "舊約民俗學（卷二）", "", "Folk-Lore in the Old Testament, Vol. 2", 1918, 1918, "Macmillan", "London"),
    "frazer_folk-lore-old-testament_vol3of3_en_1918": (
        "舊約民俗學（卷三）", "", "Folk-Lore in the Old Testament, Vol. 3", 1918, 1918, "Macmillan", "London"),
    "frazer_totemism-and-exogamy_vol1of4_en_1910": (
        "圖騰制與外婚制（卷一）", "", "Totemism and Exogamy, Vol. 1", 1910, 1910, "Macmillan", "London"),
    "frazer_totemism-and-exogamy_vol2of4_en_1910": (
        "圖騰制與外婚制（卷二）", "", "Totemism and Exogamy, Vol. 2", 1910, 1910, "Macmillan", "London"),
    "frazer_totemism-and-exogamy_vol3of4_en_1910": (
        "圖騰制與外婚制（卷三）", "", "Totemism and Exogamy, Vol. 3", 1910, 1910, "Macmillan", "London"),
    "frazer_totemism-and-exogamy_vol4of4_en_1910": (
        "圖騰制與外婚制（卷四）", "", "Totemism and Exogamy, Vol. 4", 1910, 1910, "Macmillan", "London"),
    "frazer_psyches-task_en_1909": (
        "普緒喀的任務", "迷信對制度發展的貢獻", "Psyche's Task: A Discourse Concerning the Influence of Superstition on the Growth of Institutions",
        1909, 1909, "Macmillan", "London"),

    # ── 哈里森 ────────────────────────────────────────────────
    "harrison_prolegomena-greek-religion_en_1903": (
        "希臘宗教研究導論", "主張儀式先於神話，扭轉十九世紀以文本為中心的典範",
        "Prolegomena to the Study of Greek Religion", 1903, 1903, "Cambridge University Press", "Cambridge"),
    "harrison_themis_en_1912": (
        "忒彌斯", "希臘宗教社會起源研究", "Themis: A Study of the Social Origins of Greek Religion",
        1912, 1912, "Cambridge University Press", "Cambridge"),
    "harrison_epilegomena-greek-religion_en_1921": (
        "希臘宗教研究後論", "", "Epilegomena to the Study of Greek Religion",
        1921, 1921, "Cambridge University Press", "Cambridge"),
    "harrison_ancient-art-and-ritual_en_1913": (
        "古代藝術與儀式", "", "Ancient Art and Ritual", 1913, 1913, "Williams & Norgate", "London"),
    "harrison_primitive-athens_en_1906": (
        "考古學所見的原始雅典", "", "Primitive Athens as Described by Thucydides",
        1906, 1906, "Cambridge University Press", "Cambridge"),
    "harrison_religion-of-ancient-greece_en_1905": (
        "古希臘宗教", "", "The Religion of Ancient Greece", 1905, 1905, "Archibald Constable", "London"),
    "harrison_myths-of-the-odyssey_en_1882": (
        "奧德賽神話", "藝術與文學中的呈現", "Myths of the Odyssey in Art and Literature",
        1882, 1882, "Rivingtons", "London"),

    # ── 羅伯遜‧史密斯 ──────────────────────────────────────────
    "robertson-smith_religion-of-the-semites_ed1_en_1889": (
        "閃族宗教講座（初版）", "以共餐獻祭為核心，涂爾幹獻祭理論的上游",
        "Lectures on the Religion of the Semites, 1st ed.", 1889, 1889, "Adam & Charles Black", "Edinburgh"),
    "robertson-smith_religion-of-the-semites_ed2_en_1894": (
        "閃族宗教講座（二版）", "", "Lectures on the Religion of the Semites, 2nd ed.",
        1889, 1894, "Adam & Charles Black", "London"),
    "robertson-smith_kinship-and-marriage-early-arabia_ed1_en_1885": (
        "早期阿拉伯的親屬與婚姻（初版）", "", "Kinship and Marriage in Early Arabia",
        1885, 1885, "Cambridge University Press", "Cambridge"),
    "robertson-smith_kinship-and-marriage-early-arabia_newed_en_1903": (
        "早期阿拉伯的親屬與婚姻（新版）", "庫克編訂", "Kinship and Marriage in Early Arabia, new ed.",
        1885, 1903, "Adam & Charles Black", "London"),
    "robertson-smith_old-testament-jewish-church_ed1_en_1882": (
        "猶太教會中的舊約", "十二講", "The Old Testament in the Jewish Church",
        1881, 1882, "Adam & Charles Black", "Edinburgh"),
    "robertson-smith_prophets-of-israel_en_1895": (
        "以色列的先知及其在歷史中的地位", "", "The Prophets of Israel and Their Place in History",
        1882, 1895, "Adam & Charles Black", "London"),
    "robertson-smith_lectures-and-essays_en_1912": (
        "講稿與論文集", "黑僧與克里頓編", "Lectures and Essays of William Robertson Smith",
        1912, 1912, "Adam & Charles Black", "London"),

    # ── 齊美爾 ────────────────────────────────────────────────
    "simmel_die-religion_de_1906": (
        "宗教", "社會學視角下的宗教", "Die Religion", 1906, 1906, "Rütten & Loening", "Frankfurt am Main"),
    "simmel_soziologie_de_1908": (
        "社會學", "社會化形式之研究", "Soziologie: Untersuchungen über die Formen der Vergesellschaftung",
        1908, 1908, "Duncker & Humblot", "Leipzig"),
    "simmel_philosophie-des-geldes_ed1_de_1900": (
        "貨幣哲學（初版）", "", "Philosophie des Geldes", 1900, 1900, "Duncker & Humblot", "Leipzig"),
    "simmel_grundfragen-der-soziologie_de_1917": (
        "社會學的基本問題", "個體與社會", "Grundfragen der Soziologie: Individuum und Gesellschaft",
        1917, 1917, "Göschen", "Berlin"),
    "simmel_lebensanschauung_de_1922": (
        "生命觀", "四章形上學", "Lebensanschauung: Vier metaphysische Kapitel",
        1918, 1922, "Duncker & Humblot", "München"),
    "simmel_kant-und-goethe_de_1906": (
        "康德與歌德", "論現代世界觀的歷史", "Kant und Goethe: Zur Geschichte der modernen Weltanschauung",
        1906, 1906, "Bard Marquardt", "Berlin"),

    # ── 瑟德布盧姆 ────────────────────────────────────────────
    "soderblom_gudstrons-uppkomst_sv_1914": (
        "神信仰的生成", "瑞典文原著；1916 德文本的母本", "Gudstrons uppkomst",
        1914, 1914, "Hugo Gebers", "Stockholm"),
    "soderblom_uppenbarelsetrons-tolkning_sv_1911": (
        "啟示信仰的詮釋", "瑞典文", "Uppenbarelsetrons tolkning", 1911, 1911, "Hugo Gebers", "Stockholm"),
    "soderblom_the-living-god_en_1933": (
        "活的上帝", "吉福德講座；作者身後出版", "The Living God: Basal Forms of Personal Religion",
        1933, 1933, "Oxford University Press", "London"),
    "soderblom_christian-fellowship_en_1923": (
        "基督徒的團契", "普世教會運動的神學基礎", "Christian Fellowship: The United Life and Work of Christendom",
        1923, 1923, "Fleming H. Revell", "New York"),

    # ── 特洛爾奇 ──────────────────────────────────────────────
    "troeltsch_soziallehren_de_1912": (
        "基督教會與團體的社會訓誨", "教會型／教派型／神祕型三分法的出處",
        "Die Soziallehren der christlichen Kirchen und Gruppen", 1912, 1912, "J.C.B. Mohr", "Tübingen"),
    "troeltsch_soziallehren_ed3-photomech_de_1923": (
        "基督教會與團體的社會訓誨（第三版）", "照相製版重印",
        "Die Soziallehren der christlichen Kirchen und Gruppen, 3. Aufl.", 1912, 1923, "J.C.B. Mohr", "Tübingen"),
    "troeltsch_absolutheit-des-christentums_de_1902": (
        "基督教的絕對性與宗教史", "", "Die Absolutheit des Christentums und die Religionsgeschichte",
        1902, 1902, "J.C.B. Mohr", "Tübingen"),
    "troeltsch_historismus-und-seine-probleme_de_1922": (
        "歷史主義及其問題", "", "Der Historismus und seine Probleme", 1922, 1922, "J.C.B. Mohr", "Tübingen"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    cleaner = ROOT / "scripts" / "archive_djvu_clean.py"
    rows, seq = [], {}
    missing = [s for s in WORKS if not (SRC / f"{s}.txt").exists()]
    extra = [p.stem for p in SRC.glob("*.txt") if p.stem not in WORKS]
    if missing:
        print(f"⚠ 對照表有但檔案不在（{len(missing)}）：{missing[:3]}")
    if extra:
        print(f"⚠ 檔案有但對照表沒列（{len(extra)}）：{extra[:3]}")

    for stem, meta in WORKS.items():
        src = SRC / f"{stem}.txt"
        if not src.exists():
            continue
        who = stem.split("_")[0]
        if who not in AUTHORS:
            print(f"  ✗ 不認得的作者代號 {who}")
            continue
        zh_name, en_name, field, ns = AUTHORS[who]
        title, subtitle, orig, y0, y1, pub, loc = meta
        seq[who] = seq.get(who, 0) + 1
        eid = f"{ns}-0000-4000-8000-{seq[who]:012d}"
        dest_dir = STUDIO / field / zh_name
        dest = dest_dir / f"{en_name}，{title}.txt"

        rows.append({
            "id": eid, "title": title, "subtitle": subtitle,
            "author": zh_name, "author_en": en_name,
            "original_title": orig,
            "original_publish_year": y0, "publication_year": y1,
            "publisher": pub, "publisher_location": loc,
            "path": str(dest),
        })
        if a.apply:
            dest_dir.mkdir(parents=True, exist_ok=True)
            cmd = [sys.executable, "-X", "utf8", str(cleaner), str(src), str(dest)]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0:
                print(f"  ✗ 清理失敗 {stem}: {r.stderr.strip()[:80]}")
                continue
        print(f"  {zh_name[:10]:12s} {title[:30]:32s} {eid[:8]}")

    if a.apply:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                       encoding="utf-8")
        print(f"\n清理並放好 {len(rows)} 本 → registry {OUT}")
    else:
        print(f"\n預演：{len(rows)} 本（加 --apply 才會動）")


if __name__ == "__main__":
    main()
