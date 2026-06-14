"""Add confirmed /gnostic proper nouns, person names and work titles to the
translation glossary (2026-06-14), so future re-translations stay term-consistent
and aligned with the /apocrypha + glossary authority used in curate_gnostic_naming.py.

  deities            — Gnostic/Manichaean/Mandaean/Hermetic figures + sects
  theologians        — Valentinus / Bardaisan / Epiphanes / Addai (missing persons)
  theological_terms  — key work titles (entity_type='work')

Idempotent: upsert on the natural key. Run anytime."""
import os, json, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))
URL = os.environ["SUPABASE_URL"]
SK = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def upsert(table, rows, conflict):
    h = {"apikey": SK, "Authorization": f"Bearer {SK}", "Content-Type": "application/json",
         "Prefer": "resolution=merge-duplicates,return=minimal"}
    r = requests.post(f"{URL}/rest/v1/{table}?on_conflict={conflict}", headers=h,
                      data=json.dumps(rows), timeout=60)
    print(f"  {table}: {r.status_code} ({len(rows)} rows) {r.text[:160]}")
    r.raise_for_status()


# ── deities: figures + sects (★recommended aligns with curate_gnostic_naming) ──
# (en, orig, lang, rom, ★rec, variants, religion, entity_type, domain, root, reason)
DEITIES = [
    ("Mani", "ⲙⲁⲛⲓ", "cop", "Mani", "摩尼", "瑪尼；摩尼教教主",
     "摩尼教", "教主", "摩尼教創教者", "摩尼", "波斯先知，摩尼教創立者（216–274）；統一作摩尼，勿作馬尼"),
    ("Hermes Trismegistus", "Ἑρμῆς ὁ Τρισμέγιστος", "grc", "Hermes ho Trismegistos", "三重至偉的赫密士",
     "赫密士·特里斯墨吉斯托斯；三倍偉大的赫密士；三重偉大的赫密士", "赫密士", "教主", "赫密士文集託名作者", "赫密士",
     "赫密士文集（Corpus Hermeticum）託名之祖；Trismegistus 意「三重至偉」"),
    ("Asclepius", "Ἀσκληπιός", "grc", "Asklepios", "阿斯克勒庇俄斯",
     "阿斯克勒皮俄斯；醫神", "赫密士", "deity", "赫密士的門徒；醫神", "阿斯克勒庇俄斯",
     "赫密士文集中赫密士的對話對象；希臘醫神"),
    ("Poimandres", "Ποιμάνδρης", "grc", "Poimandres", "牧人者",
     "普伊曼德雷斯；人之牧者；波伊曼德爾", "赫密士", "concept", "至高心智（Nous）的顯現", "牧人者",
     "赫密士文集首篇所載的神聖啟示者，意「人之牧者」"),
    ("Uthra", "ʿuthra", "mid", "uthra", "烏特拉",
     "烏斯拉；光明神靈", "曼達教", "deity", "曼達教的光明界神靈", "烏特拉",
     "曼達教中由光明界差遣的神靈／使者（複數 uthri）"),
    # ── sects ──
    ("Naassene", "Νaασσηνοί", "grc", "Naassenoi", "拿俄賽尼派",
     "那細尼派；蛇派（Naas＝蛇）", "諾斯底", "教派", "諾斯底教派", "",
     "源自希伯來文 naḥash（蛇）；崇蛇的早期諾斯底支派，與俄斐特派相關"),
    ("Marcionite", "", "", "Marcionite", "馬吉安派",
     "馬吉安主義", "諾斯底", "教派", "馬吉安創立的二元論教派", "馬吉安",
     "馬吉安（Marcion）創立；嚴格區分舊約造物主與新約慈父神"),
    ("Manichaeism", "", "", "Manichaeism", "摩尼教",
     "明教；摩尼教派", "摩尼教", "教派", "摩尼創立的二元論宗教", "摩尼",
     "摩尼創立的光明／黑暗二元論世界性宗教；漢語史籍作明教"),
    ("Mandaeism", "", "", "Mandaeism", "曼達教",
     "曼底安教；拿撒勒派", "曼達教", "教派", "施洗約翰傳統的諾斯底宗教", "曼達",
     "兩河流域現存的諾斯底宗教，尊施洗約翰；mandā＝知識（靈知）"),
    ("Catharism", "", "", "Catharism", "卡特里派",
     "純潔派；阿爾比派（Albigenses）", "諾斯底", "教派", "中世紀二元論教派", "卡特里",
     "中世紀法國南部二元論教派；Cathar＝純潔者，亦稱阿爾比派"),
    ("Carpocratian", "", "", "Carpocratian", "卡波克拉特派",
     "迦波克拉底派", "諾斯底", "教派", "迦波克拉特創立的諾斯底派", "卡波克拉特",
     "亞歷山卓的迦波克拉特（Carpocrates）所創；以埃皮法內斯（Epiphanes）為代表"),
]

# ── theologians: persons missing from glossary ──
# (en[unique], orig, lang, latin, ★rec, century, role, school, nationality, born, died, reason, notes)
THEOLOGIANS = [
    ("Valentinus (gnostic teacher)", "Οὐαλεντῖνος", "grc", "Valentinus", "瓦倫廷",
     "2c", "諾斯底教師／異端", "瓦倫廷派", "埃及（亞歷山卓）", 100, 160,
     "與其教派 瓦倫廷派（Valentinian）一致採短稱；勿作瓦倫蒂努斯／瓦倫汀",
     "最具系統的諾斯底學派創立者；曾於羅馬幾乎當選主教"),
    ("Bardaisan of Edessa", "ܒܪ ܕܝܨܢ", "syc", "Bardaisanes", "巴爾戴桑",
     "2-3c", "教師／詩人", "埃德薩", "埃德薩", 154, 222,
     "敘利亞文 Bar Dayṣān；亦作巴戴桑／巴爾德薩內斯",
     "埃德薩的基督徒哲人、占星家、聖詩作者，後被視為異端"),
    ("Epiphanes (Carpocratian)", "Ἐπιφάνης", "grc", "Epiphanes", "埃皮法內斯",
     "2c", "諾斯底教師", "卡波克拉特派", "亞歷山卓／薩摩斯", 130, 160,
     "按原文音譯，與撒拉米的厄皮法尼（Epiphanius）區別",
     "迦波克拉特之子，著《論正義》（On Righteousness）；早夭受奉如神"),
    ("Addai (Addaeus the Apostle)", "ܐܕܝ", "syc", "Addaeus", "阿達伊",
     "1-2c", "使徒（七十門徒之一）", "埃德薩", "埃德薩", None, None,
     "敘利亞文 Addai；亦作阿戴／阿達烏斯",
     "《阿達伊教導》（Doctrine of Addai）載其赴埃德薩傳教，與亞伯加王傳說相關"),
]

# ── theological_terms: key work titles (entity_type='work') ──
# (en[unique], orig, lang, translit, ★rec, category, era, definition, notes)
WORKS = [
    ("Corpus Hermeticum", "Corpus Hermeticum", "lat", "Corpus Hermeticum", "赫密士文集",
     "作品名", "2-3c", "託名三重至偉的赫密士的希臘文宗教哲學論集（17 篇）", "亦譯《赫米斯文集》"),
    ("Ginza Rba", "ginzā rbā", "mid", "Ginza Rabba", "大寶庫",
     "作品名", "古代晚期", "曼達教最重要的經典，意「大寶藏」", "亦譯《偉大的寶庫》《金贊》"),
    ("Kephalaia", "ⲕⲉⲫⲁⲗⲁⲓⲁ", "cop", "Kephalaia", "凱法萊亞",
     "作品名", "3-4c", "摩尼教教義問答體文集，意「章節／要義」", "科普特文摩尼教法典"),
    ("Excerpta ex Theodoto", "Ἐκλογαὶ ἐκ τῶν Θεοδότου", "grc", "Excerpta ex Theodoto", "狄奧多托語錄",
     "作品名", "2c", "革利免輯錄瓦倫廷派狄奧多托的語錄", "亦稱《摘自狄奧多托》"),
    ("Pistis Sophia", "ⲡⲓⲥⲧⲓⲥ ⲥⲟⲫⲓⲁ", "cop", "Pistis Sophia", "皮斯特斯·索菲亞",
     "作品名", "3-4c", "科普特文諾斯底經典，意「信仰‧智慧」", "與 /apocrypha 一致；勿作皮斯蒂斯"),
]


def main():
    drows = []
    for i, (en, o, l, rom, rec, var, rel, et, dom, root, reason) in enumerate(DEITIES):
        drows.append({"name_english": en, "name_original": o or None, "name_original_lang": l or None,
                      "name_romanized": rom, "name_recommended": rec, "name_variants": var or None,
                      "religion": rel, "entity_type": et, "domain_of": dom or None,
                      "name_root": root or None, "recommendation_reason": reason, "sort_order": 200 + i})
    upsert("deities", drows, "name_english")

    trows = []
    for i, (en, o, l, lat, rec, cent, role, school, nat, born, died, reason, notes) in enumerate(THEOLOGIANS):
        trows.append({"name_english": en, "name_original": o or None, "name_original_lang": l or None,
                      "name_latin_std": lat, "name_recommended": rec, "century": cent, "role": role,
                      "school": school, "nationality": nat, "born_year": born, "died_year": died,
                      "recommendation_reason": reason, "notes": notes, "sort_order": 900 + i})
    upsert("theologians", trows, "name_english")

    wrows = []
    for i, (en, o, l, tr, rec, cat, era, defn, notes) in enumerate(WORKS):
        wrows.append({"term_english": en, "term_original": o or None, "term_original_lang": l or None,
                      "term_latin_translit": tr, "zh_recommended": rec, "category": cat, "entity_type": "work",
                      "era": era, "definition_zh": defn, "notes": notes, "sort_order": 700 + i})
    upsert("theological_terms", wrows, "term_english")
    print("done.")


if __name__ == "__main__":
    main()
