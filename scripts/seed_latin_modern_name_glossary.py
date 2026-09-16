#!/usr/bin/env python3
"""把拉丁下冊〈近現代教廷拉丁〉專名表缺中文的那幾十個名字補進譯名詞庫。

重整之後那張表剩 84 條，其中 31 條的中文登錄本來就有；這一支補其餘的。補的是
**詞庫**而不是附錄檔，因為譯名的權威在詞庫，附錄只是取用的一方——直接寫進附錄
等於在讀本裡養一份沒人知道的第二套譯名。

定名的根據寫在每一筆的 `recommendation_reason` 裡。有六個是靠**語料上下文**定的，
不是靠字面猜：

* ``Tullius`` 在這批語料裡二十七次全是西塞羅（``Tullius [Cic., nat.d.]``、
  ``Tullius Romani disertissimus generis``），所以它不是另一個人，是西塞羅的
  族名——掛成 Cicero 那一筆的 ``name_variants``，不另立新名。
* ``Lucina`` 二十六次全部出自 ``S. Laurentii in Lucina``，那是羅馬的聖老楞佐堂銜，
  **不是生育女神**。照女神填就會把一個地名寫成神名。
* ``Sabinus`` 兼有「薩賓王」與「米蘭執事撒比努」兩義，取音譯以免綁死其中一個。
* ``Afer``／``Italus``／``Graecus`` 這些是族稱形容詞，``Biblia``（聖經）、
  ``Deipara``（天主之母）是普通名詞與稱號——**都不入詞庫**，它們該做的是離開
  專名表，已在 `build_latin_appendices.py` 的停用表處理。
* 五個聖經人名（Eva、Emmanuel、Ezechiel、Saulus、Cornelius）也不入詞庫：這本
  讀本的聖經譯名權威是思高譯本，與上冊那張表同一條路，寫在 builder 裡。

    python -X utf8 scripts/seed_latin_modern_name_glossary.py          # 只報告
    python -X utf8 scripts/seed_latin_modern_name_glossary.py --write
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

# table -> rows.  `name_original` is the Latin as the reader meets it.
SEED: dict[str, list[dict]] = {
    "place_names": [
        {"name_original": "Italia", "name_english": "Italy", "name_recommended": "義大利",
         "place_type": "國名", "name_root": "義大利"},
        {"name_original": "Europa", "name_english": "Europe", "name_recommended": "歐洲",
         "place_type": "地區", "name_variants": "歐羅巴"},
        {"name_original": "Germania", "name_english": "Germania", "name_recommended": "日耳曼尼亞",
         "place_type": "行省", "name_root": "日耳曼"},
        {"name_original": "Africa", "name_english": "Africa", "name_recommended": "阿非利加",
         "place_type": "行省",
         "recommendation_reason": "教會拉丁裡指羅馬的阿非利加行省（北非），不是今日的非洲洲名"},
        {"name_original": "Sicilia", "name_english": "Sicily", "name_recommended": "西西里",
         "place_type": "地區", "name_root": "西西里"},
        {"name_original": "Anglia", "name_english": "England", "name_recommended": "英格蘭",
         "place_type": "國名"},
        {"name_original": "Hibernia", "name_english": "Ireland", "name_recommended": "愛爾蘭",
         "place_type": "國名"},
        {"name_original": "Bononia", "name_english": "Bologna", "name_recommended": "波隆那",
         "place_type": "城市"},
        {"name_original": "Constantinopolis", "name_english": "Constantinople",
         "name_recommended": "君士坦丁堡", "place_type": "城市", "name_root": "君士坦丁"},
        {"name_original": "Hierosolyma", "name_english": "Jerusalem", "name_recommended": "耶路撒冷",
         "place_type": "城市"},
        {"name_original": "Aethiopia", "name_english": "Ethiopia", "name_recommended": "衣索比亞",
         "place_type": "國名", "name_variants": "厄提約丕雅（思高）"},
        {"name_original": "Tiberis", "name_english": "Tiber", "name_recommended": "台伯河",
         "place_type": "地區"},
        {"name_original": "Lucina", "name_english": "Lucina", "name_recommended": "盧奇納",
         "place_type": "地區",
         "recommendation_reason": "語料 26 次全部出自 S. Laurentii in Lucina，"
                                  "是羅馬的堂銜地名，不是生育女神 Lucina"},
    ],
    "historical_rulers": [
        {"name_original": "Caesar", "name_english": "Caesar", "name_recommended": "凱撒",
         "title": "獨裁官", "name_root": "凱撒"},
        {"name_original": "Pompeius", "name_english": "Pompey", "name_recommended": "龐培",
         "title": "執政官"},
        {"name_original": "Antonius", "name_english": "Mark Antony", "name_recommended": "安東尼",
         "title": "三頭之一"},
        {"name_original": "Justinianus", "name_english": "Justinian", "name_recommended": "查士丁尼",
         "title": "皇帝", "name_root": "查士丁"},
        {"name_original": "Romulus", "name_english": "Romulus", "name_recommended": "羅慕路斯",
         "title": "傳說中的羅馬建城者"},
        {"name_original": "Sabinus", "name_english": "Sabinus", "name_recommended": "薩比努斯",
         "title": "人名",
         "recommendation_reason": "語料裡兼指薩賓王與米蘭執事，取音譯不綁死其中一個"},
        {"name_original": "Valerius", "name_english": "Valerius", "name_recommended": "瓦萊里烏斯",
         "title": "氏族名"},
        {"name_original": "Carolus", "name_english": "Charles", "name_recommended": "查理",
         "title": "君王名", "name_variants": "嘉祿（教會用）"},
    ],
    "philosophers": [
        {"name_original": "Cato", "name_english": "Cato", "name_recommended": "加圖",
         "era": "羅馬共和"},
        {"name_original": "Flaccus", "name_english": "Flaccus", "name_recommended": "弗拉庫斯",
         "era": "羅馬",
         "recommendation_reason": "語料同時出現維里烏斯·弗拉庫斯與瓦萊里烏斯·弗拉庫斯，"
                                  "取音譯不綁死其中一位"},
        {"name_original": "Vergilius", "name_english": "Virgil", "name_recommended": "維吉爾",
         "era": "羅馬"},
    ],
    # 🚨 Marcion、Sabellius、Hermogenes、Saturninus、Theophilus 詞庫本來就有，
    # 而且推薦名與我原本想填的不一樣（黑摩根 vs 赫爾摩革乃、薩圖爾努斯 vs
    # 薩圖尼努斯）。詞庫的 name_recommended 是絕對權威，所以那五筆不補，
    # 照詞庫的用。缺的只有這三個。
    "theologians": [
        # 🚨 詞庫裡三位 Theophilus（安提阿、凱撒利亞、亞歷山大）獨缺這一位，而這批
        # 語料裡二十五次**全部**是他：episcopus Alexandrinus、Theophilo Alexandrino、
        # 〈致帕瑪基烏斯書〉裡宣告奧利振為異端的那一位。缺了他，附錄就從剩下兩位裡
        # 挑一個填上，印出來是「凱撒利亞的提阿非羅」——名字看起來很正常，指的是另
        # 一個人。中文從兄弟列的體例走（安提阿的提阿非羅／凱撒利亞的提阿非羅）。
        {"name_original": "Theophilus", "name_english": "Theophilus of Alexandria",
         "name_latin_std": "Theophilus Alexandrinus", "name_recommended": "亞歷山大的提阿非羅",
         "name_catholic_sgs": "亞歷山大‧德敖斐羅", "role": "亞歷山大宗主教",
         "recommendation_reason": "語料 25 次全部標明 episcopus Alexandrinus，"
                                  "與詞庫既有的安提阿、凱撒利亞兩位同名者不是同一人"},
        {"name_original": "Valentinus", "name_english": "Valentinus", "name_catholic_sgs": "瓦倫廷",
         "name_recommended": "瓦倫廷", "role": "異端／諾斯底"},
        {"name_original": "Rufinus", "name_english": "Rufinus of Aquileia",
         "name_catholic_sgs": "魯菲努斯", "name_recommended": "魯菲努斯", "role": "教父／譯者",
         "recommendation_reason": "語料指阿奎萊亞的魯菲努斯（與耶柔米論戰者）"},
        {"name_original": "Cyrillus", "name_english": "Cyril", "name_catholic_sgs": "濟利祿",
         "name_recommended": "濟利祿", "role": "教父"},
    ],
    "deities": [
        {"name_original": "Vulcanus", "name_english": "Vulcan", "name_recommended": "伏爾甘",
         "religion": "羅馬"},
        {"name_original": "Ceres", "name_english": "Ceres", "name_recommended": "刻瑞斯",
         "religion": "羅馬"},
        {"name_original": "Hercules", "name_english": "Hercules", "name_recommended": "赫丘力士",
         "religion": "羅馬"},
    ],
}

# Not new names — a spelling of one already in the register.
VARIANTS: list[tuple[str, str, str, str]] = [
    ("philosophers", "Cicero", "Tullius",
     "語料 27 次全是西塞羅（Tullius [Cic., nat.d.]），是他的族名而非另一個人"),
]


def client() -> tuple[str, dict]:
    load_dotenv(ROOT / ".env")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        raise SystemExit("需要 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY")
    return url, {"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json", "Prefer": "return=representation"}


def existing(url: str, headers: dict, table: str) -> tuple[dict[str, dict], dict[str, dict]]:
    """（依 name_english 索引，依 name_original 索引）。

    🚨 分成兩份索引，是因為 **name_original 不是身分**。原文欄寫的是拉丁拼法，
    而羅馬人名同名的極多：詞庫本來就有兩位 Saturninus、三位 Theophilus。先前
    把兩欄混成一份索引，結果「亞歷山大的提阿非羅」被判成已存在（撞的是凱撒利亞
    那一位的 name_original），整筆靜默略過——附錄照樣印出一個提阿非羅，指的是
    另一個人。身分看 name_english，那一欄才帶著限定語。
    """
    by_english: dict[str, dict] = {}
    by_original: dict[str, dict] = {}
    response = requests.get(
        f"{url}/rest/v1/{table}",
        params={"select": "id,name_original,name_english,name_variants", "limit": "5000"},
        headers=headers, timeout=90,
    )
    response.raise_for_status()
    for row in response.json():
        english = (row.get("name_english") or "").strip().lower()
        original = (row.get("name_original") or "").strip().lower()
        if english:
            by_english.setdefault(english, row)
        if original:
            by_original.setdefault(original, row)
    return by_english, by_original


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    url, headers = client()

    added = skipped = 0
    for table, rows in SEED.items():
        by_english, by_original = existing(url, headers, table)
        fresh, alias = [], []
        for row in rows:
            latin = row["name_original"].lower()
            english = (row.get("name_english") or "").lower()
            if english in by_english:
                # 同一個實體，只是原文欄寫的是別的拼法（Ἰταλία／Italy）。再插一列
                # 會撞 name_english 的唯一鍵，也會讓同一個地方有兩筆。拉丁拼法掛成
                # 那一列的變體就好。
                alias.append((by_english[english], row["name_original"]))
            elif latin in by_original and not (by_original[latin].get("name_english") or "").strip():
                # 舊列連英文名都沒有，無從判斷是不是同一人，當成同一列不重複插。
                print(f"  已在 {table}：{row['name_original']}")
                skipped += 1
            else:
                fresh.append(row)
        for row, latin in alias:
            current = (row.get("name_variants") or "").strip()
            if latin.lower() == (row.get("name_original") or "").strip().lower():
                print(f"  已在 {table}：{latin}")
                skipped += 1
                continue
            if latin.lower() in current.lower():
                print(f"  已有變體 {table}：{latin}")
                continue
            merged = f"{current}／{latin}".strip("／")
            print(f"{table}：{row.get('name_english')} 補拉丁拼法 {latin}")
            if args.write:
                response = requests.patch(
                    f"{url}/rest/v1/{table}", params={"id": f"eq.{row['id']}"},
                    headers=headers, json={"name_variants": merged}, timeout=90)
                if not response.ok:
                    print(f"    ✘ {response.status_code} {response.text[:160]}")
        if not fresh:
            continue
        print(f"{table}：新增 {len(fresh)} 筆　{'、'.join(r['name_original'] for r in fresh)}")
        if args.write:
            # PostgREST 的批次插入要求每一列的鍵完全相同（PGRST102
            # "All object keys must match"）——少寫一個可選欄位，整批就退回。
            # 補齊成同一組鍵，缺的給 None。
            columns = sorted({key for row in fresh for key in row})
            payload = [{key: row.get(key) for key in columns} for row in fresh]
            response = requests.post(f"{url}/rest/v1/{table}", headers=headers, json=payload, timeout=90)
            if not response.ok:
                print(f"    ✘ {response.status_code} {response.text[:200]}")
                continue
            added += len(fresh)

    for table, target, variant, reason in VARIANTS:
        by_english, by_original = existing(url, headers, table)
        row = by_english.get(target.lower()) or by_original.get(target.lower())
        if not row:
            print(f"  ！{table} 找不到 {target}，{variant} 沒有掛上去")
            continue
        current = (row.get("name_variants") or "").strip()
        if variant.lower() in current.lower():
            print(f"  已有變體 {target} ← {variant}")
            continue
        merged = f"{current}／{variant}".strip("／")
        print(f"{table}：{target} 補變體 {variant}（{reason}）")
        if args.write:
            response = requests.patch(
                f"{url}/rest/v1/{table}", params={"id": f"eq.{row['id']}"},
                headers=headers, json={"name_variants": merged}, timeout=90,
            )
            if not response.ok:
                print(f"    ✘ {response.status_code} {response.text[:200]}")

    print(f"\n新增 {added} 筆，略過 {skipped} 筆（已存在）")
    if not args.write:
        print("（未寫入；加 --write）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
