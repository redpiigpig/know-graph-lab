"""把原文讀本校對抓到的譯名回饋寫進翻譯定名（/translation-glossary）。

使用者 2026-09-25：「翻譯的回饋也要跟著更新 /translation-glossary」。來源是 2026-09-23 七冊
逐頁校對的譯名類發現（`output/qa/original-readers/content-review-2026-09-23/findings.json`，
cat B／D／E 裡的專名不一）與 09-25 練習題覆核。這裡只收「譯名層」：人名、地名、族名、
次經書名、按譯本 register 分歧的字（阿們／亞孟）。一般詞義錯（ἐν 配與格之類）不是
定名問題，改在讀本詞表。

規矩（見 translation-glossary skill）：hand-curated、不走 LLM；★推薦形只用既有權威譯本
（和合本修訂版／思高）或使用者已裁示的名（巴別／巴比倫 2026-09-18）；兩個譯本分歧而
使用者沒裁過的，★暫依讀本印的那個，reason 寫明另一形，留給使用者定奪。
existing 的名只補空白欄，不覆蓋既有 ★。

用法：python -X utf8 scripts/seed_glossary_readers_2026_09_25.py [--dry-run]
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}
FIRST_SOURCE = "原文讀本校對 2026-09-23／09-25"
SRC = "讀本校對 2026-09-23"

# 人名（theologians，person_era=biblical）
# (name_english, original, lang, ★recommended, protestant(和修), catholic(思高), variants, reason)
PERSONS = [
    ("Jethro", "Ἰοθόρ／יִתְרוֹ", "grc", "葉忒羅", "葉忒羅", "耶特洛", "葉特羅",
     "和合本／和修作葉忒羅；希臘讀本第 28 課對譯與整句曾一作葉忒羅一作葉特羅"),
    ("Naomi", "Νωεμείν／נָעֳמִי", "grc", "拿娥米", "拿娥米", "納敖米", "拿俄米",
     "和修 2010 改作拿娥米（和合本拿俄米）；希臘讀本第 39 課兩形並見"),
    ("Kilion", "Χελαιών／כִּלְיוֹן", "grc", "基連", "基連", "基肋雍", "基利翁",
     "和合本／和修基連；希臘讀本第 39 課對譯作基利翁"),
    ("Amnon", "Ἀμνών／אַמְנוֹן", "grc", "暗嫩", "暗嫩", "阿默農", "",
     "大衛之子（撒下 13）；希臘第一冊附錄誤作地名「哀嫩」"),
    ("Cleopas", "Κλεοπᾶς", "grc", "革流巴", "革流巴", "克羅帕", "",
     "路 24:18；與約 19:25 的 Clopas（革羅帕／革羅罷）不是同一人，希臘讀本第 19 課曾混"),
    ("Quirinius", "Κυρήνιος", "grc", "居里扭", "居里扭", "季黎諾", "居里尼",
     "路 2:2；希臘讀本第 8 課對譯作居里尼、整句作居里扭"),
    ("Jason (Thessalonica)", "Ἰάσων", "grc", "耶孫", "耶孫", "雅松", "雅孫",
     "徒 17:5；希臘讀本第 23 課對譯雅孫、整句耶孫"),
    ("Tobit", "Τωβίθ", "grc", "托彼特", "多比", "托彼特", "多比特",
     "希臘讀本次經各課課題用思高名，暫依之；和修次經作多比。待使用者定奪"),
    ("Tobias", "Τωβίας", "grc", "多俾亞", "多比雅", "多俾亞", "",
     "托彼特之子；讀本曾把父、祖父、子三人都標「多俾亞」。暫依思高，待使用者定奪"),
    ("Tobiel", "Τωβιήλ", "grc", "托彼耳", "多比業", "托彼耳", "",
     "托彼特之父；暫依思高，待使用者定奪"),
    ("Judith", "Ἰουδίθ", "grc", "友弟德", "猶滴", "友弟德", "朱蒂絲；朱迪特",
     "希臘讀本第 37–38 課課題用思高名，對譯曾出現朱蒂絲／猶滴／朱迪特三形。暫依思高，待使用者定奪"),
    ("Holofernes", "Ὀλοφέρνης", "grc", "敖羅斐乃", "荷羅弗尼", "敖羅斐乃", "何羅弗尼；荷羅孚尼；荷羅斐尼；荷羅否南",
     "同一章曾出現四種寫法。暫依思高（課題所用），待使用者定奪"),
]

# 地名／族名／作品名／術語（theological_terms）
# (term_english, original, lang, entity_type, ★recommended, protestant, catholic, reason, notes)
TERMS = [
    ("Amen", "אָמֵן／ἀμήν／amen", "he", "term", "阿們", "阿們", "亞孟",
     "和修／和合本作阿們；思高作亞孟。讀本依所用譯本：希伯來／希臘（和修）阿們，拉丁（思高）亞孟",
     "同一本書內只准一形；09-23 校對抓到阿們／亞孟混用"),
    ("Babel", "בָּבֶל", "he", "place", "巴別", "巴別", "巴貝耳",
     "使用者 2026-09-18 定名：只有創世記十一章的巴別塔作「巴別」，其餘一律「巴比倫」",
     "Babylon 另有一條（巴比倫）"),
    ("Persians", "Πέρσαι／Περσῶν", "grc", "term", "波斯人", "波斯人", "波斯人",
     "希臘第一冊附錄把 Περσῶν 音譯成「彼息氏」；應意譯波斯", ""),
    ("Ammon (people)", "Ἀμμών／עַמּוֹן", "he", "place", "亞捫", "亞捫", "阿孟",
     "族名；「亞們」是猶大王 Amon（אָמוֹן）的譯名，兩者不可混", ""),
    ("Beth-shemesh", "Βαιθσάμυς／בֵּית שֶׁמֶשׁ", "he", "place", "伯示麥", "伯示麥", "貝特舍默士",
     "希臘第一冊附錄漏「伯」作「示麥」", ""),
    ("Amphipolis", "Ἀμφίπολις", "grc", "place", "暗妃坡里", "暗妃坡里", "安非頗里",
     "徒 17:1；希臘讀本第 23 課對譯誤作腓立比（另一城）", ""),
    ("Cappadocia", "Καππαδοκία", "grc", "place", "加帕多家", "加帕多家", "卡帕多細雅",
     "和合本／和修加帕多家；讀本對譯曾作卡帕多家", ""),
    ("Asia (Roman province)", "Ἀσία", "grc", "place", "亞細亞", "亞細亞", "亞細亞",
     "和合本／和修亞細亞；讀本對譯曾作亞西亞", ""),
    ("Satan", "שָׂטָן／Σατανᾶς", "he", "term", "撒但", "撒但", "撒殫",
     "和合本／和修撒但（不是撒旦）；讀本對譯曾作撒旦", ""),
    ("Ephrathites", "Ἐφραθαῖοι／אֶפְרָתִי", "he", "term", "以法他人", "以法他人", "厄弗辣大人",
     "得 1:2；希臘讀本第 39 課誤作「伯利恆人」", ""),
    ("Elam", "Αἰλάμ／עֵילָם", "he", "place", "以攔", "以攔", "厄藍",
     "希臘第一冊第 43 課生詞表以小寫無重音的 αιλαμ 混入", ""),
    ("Book of Tobit", "Τωβίθ", "grc", "work", "多俾亞傳", "多比傳", "多俾亞傳",
     "希臘讀本課題用思高書名、練習出處卻用和修次經書名（多比傳），全冊要一套。暫依思高，待使用者定奪", ""),
    ("Book of Judith", "Ἰουδίθ", "grc", "work", "友弟德傳", "猶滴傳", "友弟德傳",
     "同上；暫依思高，待使用者定奪", ""),
    ("Sirach (Ecclesiasticus)", "Σοφία Σειράχ", "grc", "work", "德訓篇", "便西拉智訓", "德訓篇",
     "同上；暫依思高，待使用者定奪", ""),
    ("Wisdom of Solomon", "Σοφία Σαλωμῶνος", "grc", "work", "智慧篇", "所羅門智訓", "智慧篇",
     "同上；暫依思高，待使用者定奪", ""),
    ("1 Maccabees", "Μακκαβαίων Αʹ", "grc", "work", "瑪加伯上", "馬加比一書", "瑪加伯上",
     "同上；暫依思高，待使用者定奪", ""),
    ("2 Maccabees", "Μακκαβαίων Βʹ", "grc", "work", "瑪加伯下", "馬加比二書", "瑪加伯下",
     "同上；暫依思高，待使用者定奪", ""),
    ("4 Maccabees", "Μακκαβαίων Δʹ", "grc", "work", "瑪加伯四書", "馬加比四書", "瑪加伯四書",
     "思高不收此書，名從瑪加伯系列；和修次經作馬加比四書。待使用者定奪", ""),
]


def fetch_existing() -> tuple[dict[str, dict], dict[str, dict]]:
    r1 = requests.get(f"{URL}/rest/v1/theologians?select=id,name_english,name_recommended,name_protestant,name_catholic_sgs,name_variants&limit=5000", headers=H_GET, timeout=60)
    r2 = requests.get(f"{URL}/rest/v1/theological_terms?select=id,term_english,zh_recommended,zh_protestant,zh_catholic_sgs&limit=5000", headers=H_GET, timeout=60)
    r1.raise_for_status(); r2.raise_for_status()
    return ({(x["name_english"] or "").lower(): x for x in r1.json()},
            {(x["term_english"] or "").lower(): x for x in r2.json()})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    persons, terms = fetch_existing()
    inserts_p, patches_p, inserts_t, patches_t = [], [], [], []
    for en, orig, lang, rec, prot, cath, variants, reason in PERSONS:
        row = {"name_english": en, "name_original": orig, "name_original_lang": lang,
               "name_latin_std": en, "name_recommended": rec, "name_protestant": prot,
               "name_catholic_sgs": cath, "name_variants": variants, "person_era": "biblical",
               "recommendation_reason": reason, "first_source": FIRST_SOURCE, "notes": SRC}
        old = persons.get(en.lower())
        if old is None:
            inserts_p.append(row)
        else:  # 只補空白欄，不覆蓋既有 ★
            patch = {k: v for k, v in row.items() if k in ("name_protestant", "name_catholic_sgs", "name_variants", "recommendation_reason") and not old.get(k) and v}
            if patch:
                patches_p.append((old["id"], en, patch))
    for en, orig, lang, etype, rec, prot, cath, reason, notes in TERMS:
        row = {"term_english": en, "term_original": orig, "term_original_lang": lang,
               "entity_type": etype, "zh_recommended": rec, "zh_protestant": prot,
               "zh_catholic_sgs": cath, "recommendation_reason": reason,
               "notes": (notes + "　" if notes else "") + SRC, "first_source": FIRST_SOURCE}
        old = terms.get(en.lower())
        if old is None:
            inserts_t.append(row)
        else:
            patch = {k: v for k, v in row.items() if k in ("zh_protestant", "zh_catholic_sgs", "recommendation_reason") and not old.get(k) and v}
            if patch:
                patches_t.append((old["id"], en, patch))
    print(f"theologians：新增 {len(inserts_p)}，補欄 {len(patches_p)}；theological_terms：新增 {len(inserts_t)}，補欄 {len(patches_t)}")
    for r in inserts_p: print("  +人", r["name_english"], "★", r["name_recommended"])
    for _, en, patch in patches_p: print("  ~人", en, patch)
    for r in inserts_t: print("  +詞", r["term_english"], "★", r["zh_recommended"])
    for _, en, patch in patches_t: print("  ~詞", en, patch)
    if args.dry_run:
        print("（dry-run，未寫入）"); return
    if inserts_p:
        requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON, json=inserts_p, timeout=60).raise_for_status()
    for rid, _, patch in patches_p:
        requests.patch(f"{URL}/rest/v1/theologians?id=eq.{rid}", headers=H_JSON, json=patch, timeout=60).raise_for_status()
    if inserts_t:
        requests.post(f"{URL}/rest/v1/theological_terms", headers=H_JSON, json=inserts_t, timeout=60).raise_for_status()
    for rid, _, patch in patches_t:
        requests.patch(f"{URL}/rest/v1/theological_terms?id=eq.{rid}", headers=H_JSON, json=patch, timeout=60).raise_for_status()
    print("已寫入")


if __name__ == "__main__":
    main()
