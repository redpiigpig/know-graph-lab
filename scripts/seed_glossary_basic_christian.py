#!/usr/bin/env python3
"""Add the basic Christian vocabulary the theological-terms glossary never had.

`/translation-glossary` was built out of the patristic translation work, so it
holds homoousios, perichoresis and Theotokos but not 「聖經」「福音」「使徒」.
That gap only became visible when the Japanese reader's appendix tried to join
against it: fourteen ordinary words in the corpus, two of them covered.

Six of these carry a real divergence between the two Chinese traditions and are
the reason the column exists — 使徒／宗徒, 宣教士／傳教士, 聖徒／聖人, 燔祭／
全燔祭, 牧師／牧者, 傳道／傳教. The other six read the same in both and are
recorded as such, because 「兩邊一樣」 is also an answer the appendix needs: a
blank cell would otherwise be read as 「還沒查」.

    python -X utf8 scripts/seed_glossary_basic_christian.py          # 看要寫什麼
    python -X utf8 scripts/seed_glossary_basic_christian.py --write
"""

from __future__ import annotations

import argparse
import os

import requests
from dotenv import load_dotenv

TABLE = "theological_terms"

# term_english 是這張表的比對鍵，所以照最通行的英文單詞寫，不加括號說明。
ROWS = [
    {
        "term_english": "Bible",
        "term_original": "τὰ βιβλία",
        "term_original_lang": "grc",
        "zh_recommended": "聖經",
        "zh_protestant": "聖經",
        "zh_catholic_sgs": "聖經",
        "category": "聖經與正典",
        "notes": "兩傳統同形。思高本書名亦作《聖經》。",
    },
    {
        "term_english": "gospel",
        "term_original": "εὐαγγέλιον",
        "term_original_lang": "grc",
        "zh_recommended": "福音",
        "zh_protestant": "福音",
        "zh_catholic_sgs": "福音",
        "category": "聖經與正典",
        "notes": "兩傳統同形。",
    },
    {
        "term_english": "Christ",
        "term_original": "Χριστός",
        "term_original_lang": "grc",
        "zh_recommended": "基督",
        "zh_protestant": "基督",
        "zh_catholic_sgs": "基督",
        "category": "基督論",
        "notes": "兩傳統同形。",
    },
    {
        "term_english": "cross",
        "term_original": "σταυρός",
        "term_original_lang": "grc",
        "zh_recommended": "十字架",
        "zh_protestant": "十字架",
        "zh_catholic_sgs": "十字架",
        "category": "救恩論",
        "notes": "兩傳統同形。",
    },
    {
        "term_english": "synagogue",
        "term_original": "συναγωγή",
        "term_original_lang": "grc",
        "zh_recommended": "會堂",
        "zh_protestant": "會堂",
        "zh_catholic_sgs": "會堂",
        "category": "教會學",
        "notes": "兩傳統同形。指猶太人的會堂，與 ἐκκλησία（教會）分開。",
    },
    {
        "term_english": "tabernacle",
        "term_original": "מִשְׁכָּן / σκηνή",
        "term_original_lang": "hbo",
        "zh_recommended": "會幕",
        "zh_protestant": "會幕",
        "zh_catholic_sgs": "會幕",
        "category": "聖事",
        "notes": "兩傳統主要譯法同形；思高本在 מִשְׁכָּן 一詞另用「帳棚」，"
                 "אֹהֶל מוֹעֵד 則作「會幕」。",
    },
    {
        "term_english": "apostle",
        "term_original": "ἀπόστολος",
        "term_original_lang": "grc",
        "zh_recommended": "使徒",
        "zh_protestant": "使徒",
        "zh_catholic_sgs": "宗徒",
        "category": "教會學",
        "notes": "兩傳統分歧：思高本一律作「宗徒」，《使徒行傳》亦作《宗徒大事錄》。",
    },
    {
        "term_english": "missionary",
        "term_original": "missionarius",
        "term_original_lang": "lat",
        "zh_recommended": "宣教士",
        "zh_protestant": "宣教士",
        "zh_catholic_sgs": "傳教士",
        "category": "教會學",
        "notes": "本站定名為「宣教士」，不用「傳教士」或日文的「宣教師」；"
                 "天主教傳統作「傳教士」。",
    },
    {
        "term_english": "saint",
        "term_original": "ἅγιος",
        "term_original_lang": "grc",
        "zh_recommended": "聖徒",
        "zh_protestant": "聖徒",
        "zh_catholic_sgs": "聖人",
        "category": "教會學",
        "notes": "兩傳統分歧：新教指全體信徒，天主教「聖人」指冊封者，"
                 "指全體信徒時思高本作「聖徒」。",
    },
    {
        "term_english": "burnt offering",
        "term_original": "עֹלָה / ὁλοκαύτωμα",
        "term_original_lang": "hbo",
        "zh_recommended": "燔祭",
        "zh_protestant": "燔祭",
        "zh_catholic_sgs": "全燔祭",
        "category": "聖事",
        "notes": "兩傳統分歧：思高本作「全燔祭」。",
    },
    {
        "term_english": "pastor",
        "term_original": "ποιμήν",
        "term_original_lang": "grc",
        "zh_recommended": "牧師",
        "zh_protestant": "牧師",
        "zh_catholic_sgs": "牧者",
        "category": "教會學",
        "notes": "兩傳統分歧：弗四 11 和合本作「牧師」，思高本作「牧者」；"
                 "天主教的聖職稱謂另作司鐸、神父。",
    },
    {
        "term_english": "evangelization",
        "term_original": "εὐαγγελισμός",
        "term_original_lang": "grc",
        "zh_recommended": "傳道",
        "zh_protestant": "傳道",
        "zh_catholic_sgs": "傳教",
        "category": "教會學",
        "notes": "兩傳統分歧：新教作「傳道／佈道」，天主教作「傳教／福傳」。",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    load_dotenv(".env")
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}",
               "Content-Type": "application/json", "Prefer": "return=representation"}

    existing = requests.get(
        f"{url}/rest/v1/{TABLE}?select=term_english&limit=2000", headers=headers, timeout=60).json()
    have = {(row.get("term_english") or "").strip().lower() for row in existing}
    todo = [row for row in ROWS if row["term_english"].lower() not in have]

    for row in ROWS:
        mark = "＋" if row in todo else "＝已有"
        variant = ("　新教 " + row["zh_protestant"] + "／天主教 " + row["zh_catholic_sgs"]
                   if row["zh_protestant"] != row["zh_catholic_sgs"] else "　兩傳統同形")
        print(f"  {mark} {row['term_english']:<16}{row['zh_recommended']}{variant}")

    if not args.write:
        print(f"（未寫入；加 --write。要新增 {len(todo)} 筆）")
        return 0
    if not todo:
        print("詞庫已經都有了，沒有要新增的。")
        return 0
    reply = requests.post(f"{url}/rest/v1/{TABLE}", headers=headers, json=todo, timeout=60)
    reply.raise_for_status()
    print(f"已新增 {len(reply.json())} 筆到 {TABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
