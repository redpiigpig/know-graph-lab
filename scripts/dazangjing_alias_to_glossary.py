#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把大藏經審定表判出的「同書異名」補進翻譯詞庫 theological_terms。

  python scripts/dazangjing_alias_to_glossary.py --dry-run
  python scripts/dazangjing_alias_to_glossary.py --run

為什麼要進詞庫：`zlz_match.py` 與提案清理的撞名比對都讀
`theological_terms.zh_protestant / zh_catholic_sgs`，往詞庫補一組譯名，
下一輪比對就自動抓得到，不必改程式（[[ebook-trc-archive]] 的既定做法）。

🚨 `zh_protestant` / `zh_catholic_sgs` 在這裡兼作「別名槽」。多數條目並沒有
真正的新教／天主教之分，只是同一部書的不同漢譯；擺放依傳統歸屬，擺不出來的
就把兩個譯名各放一格。真正要當權威的是 `zh_recommended`——一律填**藏內既有
定名**，那才是 [[feedback_glossary_strict_authority]] 說的唯一權威。

🚨 別名不可用泛稱。「護教篇」在教父文獻裡至少撞到儒斯定與特土良兩部，
所以兩筆各自靠 `term_original`（Apologia vs Apologeticum）分辨；
「詩篇註解」「三聯論」這類太泛的候選在審定階段就已剔掉。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SOURCE = "大藏經 TRC／天主教在線審定 2026-08-30"

# (term_original, term_english, zh_protestant, zh_catholic_sgs, zh_recommended)
ALIASES = [
    ("Enchiridion ad Laurentium", "Enchiridion on Faith, Hope, and Love",
     "論信望愛", "傳道員指南", "信望愛手冊"),
    ("Hexaemeron", "On the Hexaemeron (Basil)", "六日創造講疏", "創世六日", "六日創造講疏"),
    ("Enarrationes in Psalmos", "Expositions on the Book of Psalms",
     "詩篇詮釋", "聖奧思定主教聖詠釋義", "詩篇詮釋"),
    ("De Spiritu Sancto (Basilius)", "On the Holy Spirit (Basil)", "論聖靈", "聖靈論", "論聖靈"),
    ("De Trinitate (Augustinus)", "On the Trinity (Augustine)", "三位一體論", "論三位一體", "三位一體論"),
    ("De Officiis Ministrorum", "On the Duties of the Clergy", "論教牧職分", "論責任", "論教牧職分"),
    ("Apologeticum", "The Apology (Tertullian)", "特土良護教辯", "護教篇", "特土良護教辯"),
    ("Apophthegmata Patrum", "Sayings of the Desert Fathers",
     "沙漠教父言行錄", "沙漠父老語錄", "沙漠父老語錄"),
    ("Liber regulae pastoralis", "Pastoral Care (Gregory the Great)",
     "教牧規則", "牧靈指南", "司牧守則"),
    ("Orationes Theologicae", "The Five Theological Orations",
     "五篇神學講辭", "神學演講錄", "五篇神學講辭"),
    ("Sermones ad Populum", "Sermons to the People (Augustine)",
     "大眾講章集", "聖奧思定主教講道詞", "大眾講章集"),
    ("De consensu evangelistarum", "Harmony of the Gospels",
     "論福音書的和諧", "論四福音和諧", "論福音書的和諧"),
    ("Homiliae de statuis", "Homilies on the Statues", "雕像講道", "雕像講道詞選集", "雕像講道"),
    ("Protrepticus ad Graecos", "Exhortation to the Greeks",
     "勸希臘人歸主辭", "勸勉希臘人", "勸希臘人歸主辭"),
    ("Apologia (Iustinus)", "The Apologies of Justin Martyr", "護教篇", "護教篇", "猶斯定護教詞"),
    ("Summa contra Gentiles", "Summa contra Gentiles",
     "駁異教大全", "駁異大全", "哲學大全（駁異教大全）"),
    # De Imitatione Christi 詞庫已有「效法基督／師主篇」一筆，這裡補第三、四個譯名
    ("De Imitatione Christi (漢譯異名)", "The Imitation of Christ (further Chinese titles)",
     "遵主聖範", "輕世金書", "效法基督"),
    ("Triades pro sanctis hesychastis", "Triads in Defense of the Holy Hesychasts",
     "為神聖靜修者辯護", "維護神聖靜修者三論集", "為神聖靜修者辯護"),
    ("Il Dialogo della Divina Provvidenza", "The Dialogue of Divine Providence",
     "西恩納的加大利納對話錄", "聖女加大利納對話錄", "對話錄（天主上智之書）"),
    ("Historia Francorum", "History of the Franks", "法蘭克人史", "法蘭克人歷史", "法蘭克人歷史"),
    ("Canones Synodi Dordrechtanae", "Canons of Dort", "多特信條", "多特信經", "多特信經"),
    ("Westminster Confession of Faith", "Westminster Confession of Faith",
     "西敏信條", "西敏信綱", "西敏信條"),
    ("Kerkorde van Dordrecht", "Church Order of Dort", "多特教會法規", "多特教會條例", "多特教會條例"),
    # Catechismus Romanus 詞庫已有「特倫多／脫利騰」一筆，這裡把藏內定名補成主譯
    ("Catechismus Romanus (藏內定名)", "Roman Catechism",
     "羅馬要理問答", "脫利騰公議會教理問答", "羅馬要理問答"),
    ("Confessio fidei (Cyrillus Lucaris)", "The Eastern Confession of the Orthodox Faith",
     "東方正教信仰告白", "盧卡里斯東方信仰宣認", "盧卡里斯東方信仰宣認"),
    ("A Directory for the Public Worship of God", "Directory for Public Worship",
     "公眾崇拜指南", "公眾敬拜指南", "公眾崇拜指南"),
    ("Confessio Gallicana", "The Gallican (French) Confession", "高盧信綱", "法國信條", "法國信條"),
    ("Casti Connubii", "Casti Connubii", "貞潔婚姻通諭", "論基督徒婚姻通諭", "論基督徒婚姻通諭"),
    ("Christ sein", "On Being a Christian", "做基督徒", "論基督徒", "論作基督徒"),
    ("Orthodoxy (Chesterton)", "Orthodoxy", "回到正統", "正統", "正統"),
    ("Seeds of Contemplation", "Seeds of Contemplation", "默觀生活探秘", "默觀的種子", "默觀的種子"),
    ("Il giornale dell'anima", "Journal of a Soul", "靈心日記", "靈魂日記", "靈魂日記"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="實際寫入（預設 dry-run）")
    a = ap.parse_args()

    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}",
         "Content-Type": "application/json", "Prefer": "return=representation"}

    existing = requests.get(
        f"{url}/rest/v1/theological_terms?entity_type=eq.work&select=term_original",
        headers=h, timeout=60).json()
    have = {(r.get("term_original") or "").strip() for r in existing}
    print(f"詞庫現有 work 條目 {len(existing)} 筆")

    todo = [x for x in ALIASES if x[0] not in have]
    skip = [x for x in ALIASES if x[0] in have]
    if skip:
        print(f"  已存在，略過 {len(skip)} 筆：" + "、".join(x[0][:28] for x in skip))
    print(f"  待新增 {len(todo)} 筆")
    for orig, en, prot, cath, rec in todo:
        print(f"    {rec}　←　{prot}／{cath}　（{orig}）")

    if not a.run:
        print("\n（dry-run，未寫入。加 --run 實際寫入）")
        return 0

    n = 0
    for orig, en, prot, cath, rec in todo:
        row = {"term_original": orig, "term_english": en, "zh_protestant": prot,
               "zh_catholic_sgs": cath, "zh_recommended": rec,
               "entity_type": "work", "first_source": SOURCE}
        r = requests.post(f"{url}/rest/v1/theological_terms", headers=h, json=[row], timeout=60)
        if r.status_code in (200, 201):
            n += 1
        else:
            print(f"  [DB] {rec} 失敗 HTTP {r.status_code}: {r.text[:160]}", file=sys.stderr)
    print(f"\n已寫入 {n} 筆")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
