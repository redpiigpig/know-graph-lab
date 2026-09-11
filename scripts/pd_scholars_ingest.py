#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把公有領域的宗教學者原著建成全集 ebook row，交 parse_worker 解析。

緣起（2026-09-11）：使用者要優先做宗教學者，點名伊利亞德／韋伯／涂爾幹／奧托。
盤點發現**奧托全空（0 本）、涂爾幹只有 1 本**，但兩人都早已進入公有領域——
奧托 1937 卒、涂爾幹 1917 卒，原文與早期英譯都能合法直接抓，根本不必等 z-lib。

來源都選 **EPUB**：archive.org 與 Gutenberg 本來就提供，直接走現成的電子書管線，
不必為了一份 djvu.txt 另寫一支 builder。

ebook_id 照全集慣例給每位作者一個命名空間（[[ebook-collected-works]] §B5）：
奧托 `07701869-…`（otto＋生年）、涂爾幹沿用既有的 `80000000-…`。

  python scripts/pd_scholars_ingest.py            # 預演
  python scripts/pd_scholars_ingest.py --apply    # 建 row（再跑 parse_worker）
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集")

BOOKS = [
    {
        "id": "07701869-0000-4000-8000-000000000001",
        "title": "論「聖」",
        "subtitle": "論神聖觀念中的非理性因素及其與理性的關係（德文原著）",
        "author": "魯道夫‧奧托", "author_en": "Rudolf Otto",
        "original_title": "Das Heilige: Über das Irrationale in der Idee des Göttlichen "
                          "und sein Verhältnis zum Rationalen",
        "original_publish_year": 1917,
        "publication_year": 1926,          # 手上這一份是 Klotz, Gotha 第 14 版
        "publisher": "Leopold Klotz Verlag",
        "publisher_location": "Gotha",
        # 🚨 這裡**必須**是 .txt 不是 .epub。archive.org 同一筆的 EPUB 只有掃描頁
        # 影像沒有文字層，parse_worker 會回「no extractable text」。文字在 djvu.txt，
        # 已用 archive_djvu_clean.py 清好放在同一夾。
        # （2026-09-11 這裡一度寫成 .epub，upsert 把修好的 file_path 又蓋回去。）
        "path": STUDIO / "宗教學" / "奧托" / "Rudolf Otto，Das Heilige (14. Aufl. 1926).txt",
    },
    {
        "id": "07701869-0000-4000-8000-000000000002",
        "title": "自然主義與宗教",
        "subtitle": "英譯本（Thomson／Thomson 譯，1907）",
        "author": "魯道夫‧奧托", "author_en": "Rudolf Otto",
        "original_title": "Naturalism and Religion",
        "original_publish_year": 1904,
        "publication_year": 1907,
        "publisher": "Williams & Norgate",
        "publisher_location": "London",
        "path": STUDIO / "宗教學" / "奧托" / "Rudolf Otto，Naturalism and Religion (1907).epub",
    },
    {
        "id": "80000000-0000-4000-8000-000000000020",
        "title": "自殺論",
        "subtitle": "社會學研究（法文原著）",
        "author": "涂爾幹", "author_en": "Émile Durkheim",
        "original_title": "Le Suicide: Étude de sociologie",
        "original_publish_year": 1897,
        "publication_year": 1897,
        "publisher": "Félix Alcan",
        "publisher_location": "Paris",
        "path": STUDIO / "宗教社會學" / "涂爾幹" / "Émile Durkheim，Le Suicide (1897).epub",
    },
    {
        "id": "07701869-0000-4000-8000-000000000003",
        "title": "東西方的神祕主義",
        "subtitle": "商羯羅與艾克哈特之比較（德文原著）",
        "author": "魯道夫‧奧托", "author_en": "Rudolf Otto",
        "original_title": "West-Östliche Mystik: Vergleich und Unterscheidung zur Wesensdeutung",
        "original_publish_year": 1926,
        "publication_year": 1926,
        "publisher": "Leopold Klotz Verlag",
        "publisher_location": "Gotha",
        "path": STUDIO / "宗教學" / "奧托" / "Rudolf Otto，West-Östliche Mystik (1926).txt",
    },
    {
        "id": "07701869-0000-4000-8000-000000000004",
        "title": "印度的恩典宗教與基督教",
        "subtitle": "英譯本（Foster／Symons 譯，1930）",
        "author": "魯道夫‧奧托", "author_en": "Rudolf Otto",
        "original_title": "Die Gnadenreligion Indiens und das Christentum",
        "original_publish_year": 1930,
        "publication_year": 1930,
        "publisher": "Student Christian Movement Press",
        "publisher_location": "London",
        "path": STUDIO / "宗教學" / "奧托" / "Rudolf Otto，India's Religion of Grace and Christianity (1930).txt",
    },
    {
        "id": "80000000-0000-4000-8000-000000000022",
        "title": "社會分工論",
        "subtitle": "法文原著（1893 初版）",
        "author": "涂爾幹", "author_en": "Émile Durkheim",
        "original_title": "De la division du travail social: étude sur l'organisation "
                          "des sociétés supérieures",
        "original_publish_year": 1893,
        "publication_year": 1893,
        "publisher": "Félix Alcan",
        "publisher_location": "Paris",
        "path": STUDIO / "宗教社會學" / "涂爾幹" / "Émile Durkheim，De la division du travail social (1893).txt",
    },
    {
        "id": "80000000-0000-4000-8000-000000000023",
        "title": "社會學方法的規則",
        "subtitle": "法文原著",
        "author": "涂爾幹", "author_en": "Émile Durkheim",
        "original_title": "Les règles de la méthode sociologique",
        "original_publish_year": 1895,
        "publication_year": 1919,          # 手上這一份是 Alcan 第 7 版
        "publisher": "Félix Alcan",
        "publisher_location": "Paris",
        "path": STUDIO / "宗教社會學" / "涂爾幹" / "Émile Durkheim，Les règles de la méthode sociologique (1919).txt",
    },
    {
        "id": "80000000-0000-4000-8000-000000000021",
        "title": "教育與社會學",
        "subtitle": "法文原著",
        "author": "涂爾幹", "author_en": "Émile Durkheim",
        "original_title": "Éducation et sociologie",
        "original_publish_year": 1922,
        "publication_year": 1922,
        "publisher": "Félix Alcan",
        "publisher_location": "Paris",
        "path": STUDIO / "宗教社會學" / "涂爾幹" / "Émile Durkheim，Éducation et sociologie (1922).epub",
    },

    # ── 泰勒（宗教人類學開山，1832–1917，全 PD）──────────────────────
    {
        "id": "e7541832-0000-4000-8000-000000000001",
        "title": "原始文化（卷一）",
        "subtitle": "神話、哲學、宗教、語言、藝術與風俗的發展研究",
        "author": "愛德華‧伯內特‧泰勒", "author_en": "Edward Burnett Tylor",
        "original_title": "Primitive Culture: Researches into the Development of Mythology, "
                          "Philosophy, Religion, Language, Art and Custom, Vol. 1",
        "original_publish_year": 1871, "publication_year": 1871,
        "publisher": "John Murray", "publisher_location": "London",
        "path": STUDIO / "宗教學" / "泰勒" / "Edward B. Tylor，Primitive Culture Vol.1 (1871).txt",
    },
    {
        "id": "e7541832-0000-4000-8000-000000000002",
        "title": "原始文化（卷二）",
        "subtitle": "第四修訂版；萬物有靈論的完整論證在這一卷",
        "author": "愛德華‧伯內特‧泰勒", "author_en": "Edward Burnett Tylor",
        "original_title": "Primitive Culture, Vol. 2 (4th ed., revised)",
        "original_publish_year": 1871, "publication_year": 1903,
        "publisher": "John Murray", "publisher_location": "London",
        "path": STUDIO / "宗教學" / "泰勒" / "Edward B. Tylor，Primitive Culture Vol.2 (4th ed.).txt",
    },
    {
        "id": "e7541832-0000-4000-8000-000000000003",
        "title": "人類學",
        "subtitle": "人及其文明之研究導論",
        "author": "愛德華‧伯內特‧泰勒", "author_en": "Edward Burnett Tylor",
        "original_title": "Anthropology: An Introduction to the Study of Man and Civilization",
        "original_publish_year": 1881, "publication_year": 1881,
        "publisher": "Macmillan", "publisher_location": "London",
        "path": STUDIO / "宗教學" / "泰勒" / "Edward B. Tylor，Anthropology (1881).txt",
    },

    # ── 范德列烏（宗教現象學集大成，1890–1950，原文 2021 起 PD）────────
    {
        "id": "1ee71890-0000-4000-8000-000000000001",
        "title": "宗教現象學",
        "subtitle": "德文原著（1956 第二版）",
        "author": "傑拉杜斯‧范德列烏", "author_en": "Gerardus van der Leeuw",
        "original_title": "Phänomenologie der Religion",
        "original_publish_year": 1933, "publication_year": 1956,
        "publisher": "J.C.B. Mohr (Paul Siebeck)", "publisher_location": "Tübingen",
        "path": STUDIO / "宗教學" / "范德列烏" / "Gerardus van der Leeuw，Phänomenologie der Religion (1956).txt",
    },
    {
        "id": "1ee71890-0000-4000-8000-000000000002",
        "title": "宗教的本質與顯現",
        "subtitle": "英譯本（Turner 譯）",
        "author": "傑拉杜斯‧范德列烏", "author_en": "Gerardus van der Leeuw",
        "original_title": "Religion in Essence and Manifestation",
        "original_publish_year": 1933, "publication_year": 1938,
        "publisher": "Allen & Unwin", "publisher_location": "London",
        "path": STUDIO / "宗教學" / "范德列烏" / "Gerardus van der Leeuw，Religion in Essence and Manifestation.txt",
    },

    # ── 瓦赫（宗教學方法論＋芝加哥學派，1898–1955）────────────────────
    {
        "id": "0ac41898-0000-4000-8000-000000000001",
        "title": "宗教學",
        "subtitle": "學科基礎之探討（德文原著）",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Religionswissenschaft: Prolegomena zu ihrer "
                          "wissenschaftstheoretischen Grundlegung",
        "original_publish_year": 1924, "publication_year": 1924,
        "publisher": "J.C. Hinrichs", "publisher_location": "Leipzig",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Religionswissenschaft (1924).txt",
    },
    {
        "id": "0ac41898-0000-4000-8000-000000000002",
        "title": "理解（卷一）",
        "subtitle": "十九世紀詮釋學理論史‧施萊爾馬赫的奠基",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Das Verstehen: Grundzüge einer Geschichte der "
                          "hermeneutischen Theorie im 19. Jahrhundert, Bd. 1",
        "original_publish_year": 1926, "publication_year": 1926,
        "publisher": "J.C.B. Mohr", "publisher_location": "Tübingen",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Das Verstehen I (1926).txt",
    },
    {
        "id": "0ac41898-0000-4000-8000-000000000003",
        "title": "理解（卷二）",
        "subtitle": "神學詮釋學的開展",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Das Verstehen, Bd. 2: Die theologische Hermeneutik von "
                          "Schleiermacher bis Hofmann",
        "original_publish_year": 1929, "publication_year": 1929,
        "publisher": "J.C.B. Mohr", "publisher_location": "Tübingen",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Das Verstehen II (1929).txt",
    },
    {
        "id": "0ac41898-0000-4000-8000-000000000004",
        "title": "理解（卷三）",
        "subtitle": "歷史學與語文學詮釋學",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Das Verstehen, Bd. 3: Das Verstehen in der Historik von "
                          "Ranke bis zum Positivismus",
        "original_publish_year": 1933, "publication_year": 1933,
        "publisher": "J.C.B. Mohr", "publisher_location": "Tübingen",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Das Verstehen III (1933).txt",
    },
    {
        "id": "0ac41898-0000-4000-8000-000000000005",
        "title": "特倫德倫堡與狄爾泰",
        "subtitle": "短論",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Trendelenburg und Dilthey",
        "original_publish_year": 1926, "publication_year": 1926,
        "publisher": "J.C.B. Mohr", "publisher_location": "Tübingen",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Trendelenburg und Dilthey (1926).txt",
    },
    {
        "id": "0ac41898-0000-4000-8000-000000000006",
        "title": "宗教社會學",
        "subtitle": "英文原著",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Sociology of Religion",
        "original_publish_year": 1944, "publication_year": 1944,
        "publisher": "University of Chicago Press", "publisher_location": "Chicago",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Sociology of Religion (1944).txt",
    },
    {
        "id": "0ac41898-0000-4000-8000-000000000007",
        "title": "宗教經驗的類型",
        "subtitle": "基督教與非基督教（英文原著）",
        "author": "約阿希姆‧瓦赫", "author_en": "Joachim Wach",
        "original_title": "Types of Religious Experience: Christian and Non-Christian",
        "original_publish_year": 1951, "publication_year": 1951,
        "publisher": "University of Chicago Press", "publisher_location": "Chicago",
        "path": STUDIO / "宗教學" / "瓦赫" / "Joachim Wach，Types of Religious Experience (1951).txt",
    },
]


def env() -> dict:
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip("\"'")
    return out


E = env()
URL = E["SUPABASE_URL"]
KEY = E.get("SUPABASE_SERVICE_ROLE_KEY") or E.get("SUPABASE_SERVICE_KEY")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def api(path: str, method: str = "GET", body=None, prefer: str | None = None):
    headers = dict(H)
    if prefer:
        headers["Prefer"] = prefer
    req = urllib.request.Request(
        URL + "/rest/v1/" + urllib.parse.quote(path, safe="?&=.,*()-"),
        method=method, headers=headers,
        data=json.dumps(body).encode() if body is not None else None,
    )
    raw = urllib.request.urlopen(req).read().decode("utf-8")
    return json.loads(raw) if raw.strip() else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    print("實際建立" if a.apply else "預演（加 --apply 才會寫 DB）", "\n")
    ok = []
    for b in BOOKS:
        p: Path = b["path"]
        if not p.exists():
            print(f"  ✗ 檔案不在：{p}")
            continue
        exists = api(f"ebooks?select=id&id=eq.{b['id']}")
        state = "已存在→更新" if exists else "新建"
        print(f"  {state:8s} {b['author']}《{b['title']}》  {p.stat().st_size/1e6:.1f} MB")
        if not a.apply:
            continue
        row = {
            "id": b["id"], "title": b["title"], "subtitle": b["subtitle"],
            "author": b["author"], "author_en": b["author_en"],
            "original_title": b["original_title"],
            "original_publish_year": b["original_publish_year"],
            "publication_year": b["publication_year"],
            "publisher": b["publisher"], "publisher_location": b["publisher_location"],
            "file_type": p.suffix.lstrip(".").lower(), "file_path": str(p),
            # 🚨 一定要帶 collection，否則這本會混進電子圖書館
            # （[[feedback_collected_works_not_in_library]]）
            "collection": "collected-works",
            "display_mode": "standard",
        }
        api("ebooks", "POST", [row], prefer="resolution=merge-duplicates")
        ok.append(b["id"])

    if a.apply and ok:
        print(f"\n建好 {len(ok)} 本。接著解析：")
        print("  python scripts/parse_worker.py run " + " ".join(f"--book {i}" for i in ok))


if __name__ == "__main__":
    main()
