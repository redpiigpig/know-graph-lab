"""
Seed translation_glossary tables (theologians + theological_terms)
via Gemini batch fill.

Strategy:
  1. Master list 我手寫 minimal entries (name_english + 已知 hints)
  2. Gemini 對每筆 entry 補完：原文、生卒年、國籍、學派、身份、7 個傳統中譯、建議譯名、理由
  3. UPSERT 進 DB（name_english unique key 給 theologians；term_english unique 給 terms）

Usage:
  python scripts/seed_translation_glossary.py --target people --limit 10        # smoke test
  python scripts/seed_translation_glossary.py --target people                   # 全部
  python scripts/seed_translation_glossary.py --target terms
  python scripts/seed_translation_glossary.py --target both                     # 都跑
  python scripts/seed_translation_glossary.py --target people --resume          # skip 已 enriched 的（has zh_recommended）
"""
from __future__ import annotations
import os, sys, io, json, time, argparse, itertools
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests
from dotenv import load_dotenv
load_dotenv(".env")

URL = os.environ["SUPABASE_URL"]
SVC = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": SVC, "Authorization": f"Bearer {SVC}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=representation"}
H_UPSERT = {**H_JSON, "Prefer": "resolution=merge-duplicates,return=representation"}

GEMINI_KEYS = [k for k in [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("GEMINI_API_KEY_2"),
    os.environ.get("GEMINI_API_KEY_3"),
    os.environ.get("GEMINI_API_KEY_4"),
] if k]
_key_idx = 0
ENGINE = "gemini"  # default; CLI sets

# ============================================================================
# Master lists — 我預先列出，Gemini 補完詳細欄位
# ============================================================================

# 教父／神學家：name_english + minimal hints
# century / school / role 是給 Gemini 的 anchor；如不確定可留 None
THEOLOGIANS_MASTER = [
    # 使徒教父 (1c-2c 初)
    ("Clement of Rome",          "1c",    "羅馬",       "使徒教父"),
    ("Ignatius of Antioch",      "1-2c",  "安提阿",     "使徒教父"),
    ("Polycarp of Smyrna",       "2c",    "士每拿",     "使徒教父"),
    ("Papias of Hierapolis",     "2c",    "希拉波利",   "使徒教父"),
    ("Hermas",                   "2c",    "羅馬",       "使徒教父"),
    ("Mathetes",                 "2c",    None,         "使徒教父"),
    # 護教士 (2c)
    ("Justin Martyr",            "2c",    "撒瑪利亞",   "護教士"),
    ("Tatian the Assyrian",      "2c",    "敘利亞",     "護教士"),
    ("Athenagoras of Athens",    "2c",    "雅典",       "護教士"),
    ("Theophilus of Antioch",    "2c",    "安提阿",     "護教士"),
    ("Melito of Sardis",         "2c",    "撒狄",       "護教士"),
    ("Aristides of Athens",      "2c",    "雅典",       "護教士"),
    ("Hermias",                  "2-3c",  None,         "護教士"),
    # 反諾斯底
    ("Irenaeus of Lyon",         "2c",    "士每拿/里昂", "教父"),
    # 亞歷山大學派
    ("Clement of Alexandria",    "2-3c",  "亞歷山大",   "教父"),
    ("Origen",                   "3c",    "亞歷山大",   "教父"),
    ("Dionysius of Alexandria",  "3c",    "亞歷山大",   "教父"),
    ("Pantaenus",                "2c",    "亞歷山大",   "教父"),
    ("Pierius of Alexandria",    "3c",    "亞歷山大",   "教父"),
    ("Theognostus of Alexandria","3c",    "亞歷山大",   "教父"),
    # 西方拉丁早期
    ("Tertullian",               "2-3c",  "迦太基",     "教父"),
    ("Cyprian of Carthage",      "3c",    "迦太基",     "教父"),
    ("Minucius Felix",           "2-3c",  "羅馬",       "護教士"),
    ("Novatian",                 "3c",    "羅馬",       "教父"),
    ("Commodian",                "3c",    "北非",       "教父"),
    ("Arnobius of Sicca",        "3-4c",  "北非",       "護教士"),
    ("Lactantius",               "3-4c",  "北非",       "護教士"),
    # 3c 各派
    ("Hippolytus of Rome",       "2-3c",  "羅馬",       "教父"),
    ("Gregory Thaumaturgus",     "3c",    "新該撒利亞", "教父"),
    ("Julius Africanus",         "2-3c",  "耶路撒冷",   "教父"),
    ("Methodius of Olympus",     "3-4c",  "奧林波斯",   "教父"),
    ("Anatolius of Laodicea",    "3c",    "亞歷山大",   "教父"),
    ("Venantius",                "3-4c",  None,         "教父"),
    ("Asterius the Sophist",     "3-4c",  "卡帕多家",   "教父"),
    # Apostolic Constitutions / Twelve Patriarchs 等
    # 4c 大主教時代
    ("Eusebius of Caesarea",     "3-4c",  "該撒利亞",   "教父；教會史家"),
    ("Athanasius of Alexandria", "4c",    "亞歷山大",   "教父；教會博士"),
    ("Cyril of Jerusalem",       "4c",    "耶路撒冷",   "教父；教會博士"),
    ("Hilary of Poitiers",       "4c",    "普瓦捷",     "教父；教會博士"),
    ("Basil the Great",          "4c",    "加帕多家",   "教父；教會博士"),
    ("Gregory of Nazianzus",     "4c",    "加帕多家",   "教父；教會博士"),
    ("Gregory of Nyssa",         "4c",    "加帕多家",   "教父；教會博士"),
    ("Macrina the Younger",      "4c",    "加帕多家",   "教父；女隱修導師"),
    ("Ambrose of Milan",         "4c",    "米蘭",       "教父；教會博士"),
    ("Ephrem the Syrian",        "4c",    "敘利亞",     "教父；教會博士"),
    ("Aphrahat the Persian Sage","4c",    "波斯",       "敘利亞教父"),
    ("Didymus the Blind",        "4c",    "亞歷山大",   "教父"),
    ("Epiphanius of Salamis",    "4c",    "撒拉米斯",   "教父"),
    ("Pacian of Barcelona",      "4c",    "巴塞隆納",   "教父"),
    ("Asterius of Amasea",       "4-5c",  "本都",       "教父"),
    ("Apollinaris of Laodicea",  "4c",    "老底嘉",     "異端；基督論"),
    # 4-5c 東方
    ("John Chrysostom",          "4-5c",  "安提阿/君士坦丁堡", "教父；教會博士"),
    ("Theodore of Mopsuestia",   "4-5c",  "安提阿",     "教父；安提阿學派"),
    ("Diodore of Tarsus",        "4c",    "安提阿",     "教父"),
    ("Theodoret of Cyrus",       "5c",    "敘利亞",     "教父"),
    ("Nestorius",                "5c",    "君士坦丁堡", "異端；基督論"),
    ("Cyril of Alexandria",      "5c",    "亞歷山大",   "教父；教會博士"),
    ("Eutyches",                 "5c",    "君士坦丁堡", "異端；基督一性"),
    # 4-5c 西方
    ("Jerome",                   "4-5c",  "羅馬/伯利恆", "教父；教會博士"),
    ("Augustine of Hippo",       "4-5c",  "希波",       "教父；教會博士"),
    ("John Cassian",             "4-5c",  "馬賽",       "教父；隱修"),
    ("Vincent of Lerins",        "5c",    "勒蘭斯",     "教父"),
    ("Pelagius",                 "4-5c",  "不列顛",     "異端；恩典論"),
    ("Sulpitius Severus",        "4-5c",  "高盧",       "教父；史家"),
    ("Salvian of Marseille",     "5c",    "馬賽",       "教父"),
    ("Caesarius of Arles",       "5-6c",  "亞耳",       "教父"),
    ("Boethius",                 "5-6c",  "羅馬",       "教父；哲學家"),
    ("Prosper of Aquitaine",     "5c",    "阿基坦",     "教父"),
    ("Fulgentius of Ruspe",      "5-6c",  "北非",       "教父"),
    # 5-6c 東方
    ("Severus of Antioch",       "5-6c",  "敘利亞",     "教父；一性論"),
    ("Philoxenus of Mabbug",     "5-6c",  "敘利亞",     "教父；一性論"),
    ("Romanos the Melodist",     "5-6c",  "敘利亞",     "教父；聖頌詩人"),
    ("Pseudo-Dionysius the Areopagite", "5-6c", None,  "神秘神學家"),
    # 6c-8c
    ("Leo the Great",            "5c",    "羅馬",       "教宗；教會博士"),
    ("Gregory the Great",        "6-7c",  "羅馬",       "教宗；教會博士"),
    ("Isidore of Seville",       "6-7c",  "西班牙",     "教父；教會博士"),
    ("Bede the Venerable",       "7-8c",  "不列顛",     "教父；教會博士"),
    ("Maximus the Confessor",    "6-7c",  "君士坦丁堡", "教父；神秘神學"),
    ("John of Damascus",         "7-8c",  "大馬士革",   "教父；教會博士"),
    ("Andrew of Crete",          "7-8c",  "克里特",     "教父；聖頌詩人"),
    ("Germanus of Constantinople", "7-8c", "君士坦丁堡", "教父"),
    ("Theodore the Studite",     "8-9c",  "君士坦丁堡", "教父；隱修改革"),
    ("Cassiodorus",              "5-6c",  "義大利",     "教父"),
    # 9c-13c 中世紀
    ("Photius of Constantinople","9c",    "君士坦丁堡", "東方教父；牧首"),
    ("Symeon the New Theologian","10-11c","君士坦丁堡", "神秘神學家"),
    ("Gregory Palamas",          "13-14c","希臘",       "神秘神學家；本質-能力"),
    ("Anselm of Canterbury",     "11-12c","坎特伯雷",   "經院神學家；教會博士"),
    ("Peter Lombard",            "12c",   "巴黎",       "經院神學家"),
    ("Bernard of Clairvaux",     "12c",   "克萊蕾沃",   "教會博士；神秘"),
    ("Hugh of Saint Victor",     "12c",   "巴黎",       "神秘神學家"),
    ("Richard of Saint Victor",  "12c",   "巴黎",       "神秘神學家"),
    ("Hildegard of Bingen",      "12c",   "賓根",       "神秘神學家；教會博士"),
    ("Bonaventure",              "13c",   "義大利",     "經院神學家；教會博士"),
    ("Albertus Magnus",          "13c",   "德國",       "經院神學家；教會博士"),
    ("Thomas Aquinas",           "13c",   "義大利",     "經院神學家；教會博士"),
    ("Duns Scotus",              "13-14c","蘇格蘭",     "經院神學家"),
    ("William of Ockham",        "14c",   "英格蘭",     "經院神學家"),
    ("Meister Eckhart",          "13-14c","德國",       "神秘神學家"),
    ("Johannes Tauler",          "14c",   "德國",       "神秘神學家"),
    ("Catherine of Siena",       "14c",   "義大利",     "神秘神學家；教會博士"),
    ("Julian of Norwich",        "14-15c","英格蘭",     "神秘神學家"),
    ("Thomas à Kempis",          "14-15c","荷蘭",       "靈修；《效法基督》"),
    # 中世紀補完
    ("John Scotus Eriugena",     "9c",    "愛爾蘭",     "經院神學家；新柏拉圖主義"),
    ("Alcuin of York",           "8-9c",  "英格蘭",     "卡羅林文藝復興"),
    ("Rabanus Maurus",           "9c",    "德國",       "教父教師"),
    ("Anselm of Laon",           "11-12c","法國",       "經院前期"),
    ("Peter Abelard",            "11-12c","法國",       "經院神學家；倫理"),
    ("Berengar of Tours",        "11c",   "法國",       "聖事爭議"),
    ("Hugh of Saint-Cher",       "13c",   "法國",       "聖經註釋家"),
    ("Robert Grosseteste",       "13c",   "英格蘭",     "經院；自然神學"),
    ("Roger Bacon",              "13c",   "英格蘭",     "經院；實驗主義"),
    ("Henry of Ghent",           "13c",   "比利時",     "經院神學家"),
    ("Giles of Rome",            "13-14c","義大利",     "奧斯定會神學家"),
    ("John Climacus",            "6-7c",  "西奈山",     "東方神秘；《聖梯》"),
    ("Nicholas Cabasilas",       "14c",   "希臘",       "東正教神學家"),
    ("Gregory of Sinai",         "13-14c","希臘",       "靜修神學家"),
    ("Mechthild of Magdeburg",   "13c",   "德國",       "女性神秘神學家"),
    ("Henry Suso",               "14c",   "德國",       "神秘神學家"),
    ("Catherine of Genoa",       "15-16c","義大利",     "神秘神學家"),
    ("Nicholas of Cusa",         "15c",   "德國",       "後經院；學識的無知"),
    ("Gabriel Biel",             "15c",   "德國",       "後經院；唯名論"),
    ("John Wycliffe",            "14c",   "英格蘭",     "宗改先驅"),
    ("Jan Hus",                  "14-15c","波希米亞",   "宗改先驅；殉道"),
    ("Marsilius of Padua",       "14c",   "義大利",     "政治神學"),
    ("Lorenzo Valla",            "15c",   "義大利",     "人文主義者"),
    # 近代 16-18c 補完
    ("Martin Bucer",             "16c",   "斯特拉斯堡", "改教家"),
    ("Andreas Karlstadt",        "16c",   "德國",       "改教家；激進派"),
    ("Johannes Oecolampadius",   "16c",   "瑞士",       "改教家"),
    ("Peter Martyr Vermigli",    "16c",   "義大利／英", "改教家"),
    ("Johann Gerhard",           "16-17c","德國",       "路德正統神學家"),
    ("Francis Turretin",         "17c",   "日內瓦",     "改革宗正統"),
    ("William Perkins",          "16-17c","英格蘭",     "清教徒神學家"),
    ("Roger Williams",           "17c",   "新英格蘭",   "浸信會；政教分離"),
    ("George Fox",               "17c",   "英格蘭",     "公誼會（貴格會）創辦人"),
    ("Cornelius Jansen",         "17c",   "比利時",     "詹森主義"),
    ("Madame Guyon",             "17c",   "法國",       "Quietism 神秘"),
    ("François Fénelon",         "17-18c","法國",       "神秘神學家；主教"),
    ("Francisco Suárez",         "16-17c","西班牙",     "巴洛克經院"),
    ("Luis de Molina",           "16c",   "西班牙",     "耶穌會；中知識"),
    ("Petavius (Denis Pétau)",   "17c",   "法國",       "耶穌會；教父學"),
    ("William Law",              "18c",   "英格蘭",     "靈修神學家"),
    ("Joseph Butler",            "18c",   "英格蘭",     "聖公會護教學家"),
    ("Philip Jakob Spener",      "17c",   "德國",       "敬虔主義之父"),
    ("August Hermann Francke",   "17-18c","德國",       "敬虔主義"),
    ("Nikolaus von Zinzendorf",  "17-18c","德國",       "莫拉維弟兄會"),
    # 現代 19c 補完
    ("Charles Hodge",            "19c",   "美國",       "普林斯頓改革宗"),
    ("B. B. Warfield",           "19-20c","美國",       "普林斯頓改革宗"),
    ("Charles Finney",           "19c",   "美國",       "復興主義"),
    ("Horace Bushnell",          "19c",   "美國",       "自由派"),
    ("F. D. Maurice",            "19c",   "英格蘭",     "聖公會；基督教社會主義"),
    ("John Keble",               "19c",   "英格蘭",     "牛津運動"),
    ("Edward Pusey",             "19c",   "英格蘭",     "牛津運動"),
    ("B. F. Westcott",           "19c",   "英格蘭",     "新約學者"),
    ("F. C. Baur",               "19c",   "德國",       "圖賓根學派"),
    ("Albrecht Ritschl",         "19c",   "德國",       "自由派神學"),
    ("Vladimir Soloviev",        "19c",   "俄國",       "東正教哲學家"),
    ("Alexei Khomyakov",         "19c",   "俄國",       "斯拉夫派；東正教"),
    ("Sergius Bulgakov",         "19-20c","俄國",       "東正教神學家；索菲亞論"),
    # 現代 20c 補完
    ("Emil Brunner",             "20c",   "瑞士",       "辯證神學"),
    ("H. Richard Niebuhr",       "20c",   "美國",       "倫理神學"),
    ("Lesslie Newbigin",         "20c",   "英／印",     "宣教神學"),
    ("Carl F. H. Henry",         "20c",   "美國",       "福音派"),
    ("John Stott",               "20-21c","英格蘭",     "福音派"),
    ("Francis Schaeffer",        "20c",   "美國",       "福音派護教學"),
    ("Thomas F. Torrance",       "20c",   "蘇格蘭",     "辯證神學"),
    ("T. F. Torrance",           "20c",   "蘇格蘭",     "辯證神學（同 Thomas F.）"),
    ("Sallie McFague",           "20-21c","美國",       "女性神學；隱喻神學"),
    ("Rosemary Radford Ruether", "20-21c","美國",       "女性神學"),
    ("Elizabeth Johnson",        "20-21c","美國",       "天主教女性神學"),
    ("James Cone",               "20-21c","美國",       "黑人神學"),
    ("Jon Sobrino",              "20-21c","薩爾瓦多",   "解放神學"),
    ("Leonardo Boff",            "20-21c","巴西",       "解放神學"),
    ("C. S. Song",               "20-21c","台灣",       "故事神學；華人（宋泉盛）"),
    ("Kosuke Koyama",            "20-21c","日本",       "脈絡神學"),
    ("Jacques Maritain",         "20c",   "法國",       "天主教哲學家"),
    ("Edward Schillebeeckx",     "20c",   "比利時",     "天主教神學家"),
    ("Walter Kasper",            "20-21c","德國",       "天主教神學家；樞機"),
    ("Avery Dulles",             "20-21c","美國",       "天主教神學家；樞機"),
    ("Justin Popović",           "20c",   "塞爾維亞",   "東正教神學家"),
    ("Dumitru Stăniloae",        "20c",   "羅馬尼亞",   "東正教神學家"),
    ("Christos Yannaras",        "20-21c","希臘",       "東正教哲學家"),
    ("John Behr",                "20-21c","英格蘭",     "東正教教父學"),
    ("D. A. Carson",             "20-21c","加拿大",     "福音派新約學者"),
    ("Alister McGrath",          "20-21c","英格蘭",     "聖公會神學家"),
    ("Kevin Vanhoozer",          "20-21c","美國",       "後現代福音派"),
    ("George Lindbeck",          "20c",   "美國",       "後自由神學"),
    ("John Milbank",             "20-21c","英格蘭",     "Radical Orthodoxy"),
    ("Stanley Grenz",            "20c",   "加拿大",     "後保守福音派"),
    ("Donald Bloesch",           "20c",   "美國",       "福音派改革宗"),
    ("Thomas Oden",              "20-21c","美國",       "教父再覺醒"),
    ("Tim Keller",               "20-21c","美國",       "福音派；改革宗"),
    ("John Piper",               "20-21c","美國",       "改革宗復興"),
    ("Wayne Grudem",             "20-21c","美國",       "改革宗神學家"),
    # 華人補完（純英文音譯 — Watchman Nee / Carver T. Yu 已在前面，不重複）
    ("Jia Yuming",               "20c",   "中國",       "華人神學家（賈玉銘）"),
    ("Ho Shih-Ming",             "20c",   "香港",       "華人神學家（何世明）；中華神學"),
    ("Stephen Tong",             "20-21c","印尼／華人", "歸正復興（唐崇榮）"),
    ("Khiok-Khng Yeo",           "20-21c","美華",       "華人新約學者（楊克勤）"),
    ("Daniel Hung",              "20-21c","台灣",       "華人神學家（洪同勉）"),
    ("Lin Hongxin",              "20-21c","台灣",       "華人神學家（林鴻信）；歸正"),
    ("Andrew Pang",              "20-21c","香港",       "華人神學家（彭順強）"),
    ("Yang Mu-Ku",               "20c",   "香港",       "華人神學家（楊牧谷）"),
    ("Lim Chi-Pin",              "20-21c","台灣",       "華人神學家（林治平）；歷史"),
    ("Chow Lien-Hwa",            "20-21c","台灣",       "華人神學家（周聯華）"),
    # 16c 宗教改革
    ("Erasmus of Rotterdam",     "15-16c","荷蘭",       "人文主義者"),
    ("Martin Luther",            "16c",   "德國",       "宗教改革家"),
    ("Philip Melanchthon",       "16c",   "德國",       "路德派改教家"),
    ("Huldrych Zwingli",         "16c",   "瑞士",       "宗教改革家"),
    ("John Calvin",              "16c",   "日內瓦",     "宗教改革家"),
    ("Heinrich Bullinger",       "16c",   "瑞士",       "改教家"),
    ("Theodore Beza",            "16c",   "日內瓦",     "改教家"),
    ("Menno Simons",             "16c",   "荷蘭",       "重洗派"),
    ("Thomas Cranmer",           "16c",   "英格蘭",     "聖公會改教家"),
    ("Richard Hooker",           "16c",   "英格蘭",     "聖公會神學家"),
    ("Ignatius of Loyola",       "16c",   "西班牙",     "耶穌會創辦人"),
    ("Teresa of Ávila",          "16c",   "西班牙",     "神秘神學家；教會博士"),
    ("John of the Cross",        "16c",   "西班牙",     "神秘神學家；教會博士"),
    ("Robert Bellarmine",        "16-17c","義大利",     "教會博士；反宗改"),
    ("Francis de Sales",         "16-17c","法國/薩伏依","教會博士"),
    # 17c-18c
    ("Jakob Böhme",              "16-17c","德國",       "神秘神學家"),
    ("John Owen",                "17c",   "英格蘭",     "清教徒神學家"),
    ("Jonathan Edwards",         "18c",   "新英格蘭",   "大覺醒"),
    ("John Wesley",              "18c",   "英格蘭",     "衛理會"),
    ("Charles Wesley",           "18c",   "英格蘭",     "衛理會聖詩"),
    ("Friedrich Schleiermacher", "18-19c","德國",       "近代神學之父"),
    # 19c
    ("John Henry Newman",        "19c",   "英格蘭",     "牛津運動；樞機"),
    ("Søren Kierkegaard",        "19c",   "丹麥",       "存在主義神學"),
    ("Charles Spurgeon",         "19c",   "英格蘭",     "浸信會"),
    ("Adolf von Harnack",        "19-20c","德國",       "自由派神學"),
    # 20c
    ("Karl Barth",               "20c",   "瑞士",       "辯證神學"),
    ("Dietrich Bonhoeffer",      "20c",   "德國",       "認信教會；殉道"),
    ("Rudolf Bultmann",          "20c",   "德國",       "存在主義詮釋"),
    ("Paul Tillich",             "20c",   "德國/美國",  "存在主義神學"),
    ("Reinhold Niebuhr",         "20c",   "美國",       "新正統"),
    ("Karl Rahner",              "20c",   "德國",       "天主教神學家"),
    ("Hans Urs von Balthasar",   "20c",   "瑞士",       "天主教神學家"),
    ("Henri de Lubac",           "20c",   "法國",       "天主教神學家；新神學"),
    ("Yves Congar",              "20c",   "法國",       "天主教神學家"),
    ("Jean Daniélou",            "20c",   "法國",       "天主教神學家；教父學"),
    ("Joseph Ratzinger",         "20-21c","德國",       "教宗本篤十六；神學家"),
    ("Jürgen Moltmann",          "20-21c","德國",       "盼望神學"),
    ("Wolfhart Pannenberg",      "20-21c","德國",       "系統神學"),
    ("Hans Küng",                "20-21c","瑞士",       "天主教神學家"),
    ("Gustavo Gutiérrez",        "20-21c","秘魯",       "解放神學"),
    ("Stanley Hauerwas",         "20-21c","美國",       "倫理神學"),
    ("N. T. Wright",             "20-21c","英格蘭",     "新約學者"),
    ("Cornelius Van Til",        "20c",   "美國",       "改革宗護教學"),
    ("J. I. Packer",             "20-21c","英格蘭",     "福音派"),
    ("Vladimir Lossky",          "20c",   "俄/法",      "東正教神學家"),
    ("Georges Florovsky",        "20c",   "俄/美",      "東正教神學家"),
    ("Alexander Schmemann",      "20c",   "俄/美",      "東正教神學家"),
    ("John Zizioulas",           "20-21c","希臘",       "東正教神學家"),
    ("Kallistos Ware",           "20-21c","英格蘭",     "東正教神學家"),
    # 中國／華人神學家
    ("Watchman Nee",             "20c",   "中國",       "華人神學家"),
    ("Wang Mingdao",             "20c",   "中國",       "華人神學家"),
    ("T. C. Chao",               "20c",   "中國",       "華人神學家"),
    ("K. H. Ting",               "20c",   "中國",       "華人神學家；三自"),
    ("Carver T. Yu",             "20-21c","香港",       "華人神學家"),
]

# 神學名詞：name_english + category + minimal hints
TERMS_MASTER = [
    # 三一論
    ("hypostasis",                  "三一論", "尼西亞前"),
    ("ousia / substance",           "三一論", "尼西亞前"),
    ("homoousios",                  "三一論", "尼西亞後"),
    ("homoiousios",                 "三一論", "尼西亞後"),
    ("perichoresis",                "三一論", "尼西亞後"),
    ("Trinity",                     "三一論", "尼西亞後"),
    ("monarchy of the Father",      "三一論", "尼西亞前"),
    ("Filioque",                    "三一論", "中世紀"),
    ("essence-energies distinction","三一論", "中世紀東方"),
    ("subordinationism",            "三一論", "尼西亞前"),
    ("modalism / Sabellianism",     "三一論", "尼西亞前"),
    ("Arianism",                    "三一論", "尼西亞前後"),
    ("eternal generation",          "三一論", "尼西亞後"),
    ("processio (procession)",      "三一論", "中世紀"),
    # 基督論
    ("incarnation",                 "基督論", "尼西亞後"),
    ("hypostatic union",            "基督論", "迦克墩"),
    ("two natures",                 "基督論", "迦克墩"),
    ("communicatio idiomatum",      "基督論", "迦克墩"),
    ("kenosis",                     "基督論", "新約"),
    ("Theotokos",                   "基督論", "5c"),
    ("Christotokos",                "基督論", "5c"),
    ("Anhypostasia / Enhypostasia", "基督論", "後迦克墩"),
    ("Monophysitism",               "基督論", "5-6c"),
    ("Nestorianism",                "基督論", "5c"),
    ("Monothelitism",               "基督論", "7c"),
    ("Adoptionism",                 "基督論", "2-3c"),
    ("Docetism",                    "基督論", "1-2c"),
    ("Logos",                       "基督論", "2c"),
    ("Logos spermatikos",           "基督論", "2c"),
    # 救恩論
    ("soteriology",                 "救恩論", "通用"),
    ("recapitulation (anakephalaiosis)", "救恩論", "2c"),
    ("ransom theory",               "救恩論", "2-3c"),
    ("Christus Victor",             "救恩論", "通用"),
    ("substitutionary atonement",   "救恩論", "中世紀-宗改"),
    ("satisfaction theory",         "救恩論", "中世紀"),
    ("penal substitution",          "救恩論", "宗改"),
    ("moral influence theory",      "救恩論", "中世紀"),
    ("theosis / deification",       "救恩論", "教父"),
    ("justification",               "救恩論", "宗改"),
    ("sanctification",              "救恩論", "通用"),
    ("imputation",                  "救恩論", "宗改"),
    ("sola fide",                   "救恩論", "宗改"),
    ("sola gratia",                 "救恩論", "宗改"),
    ("synergism vs monergism",      "救恩論", "宗改"),
    ("prevenient grace",            "救恩論", "宗改"),
    ("irresistible grace",          "救恩論", "宗改"),
    ("predestination / election",   "救恩論", "通用"),
    ("Pelagianism / semi-Pelagianism", "救恩論", "5c"),
    ("original sin",                "救恩論", "教父"),
    ("total depravity",             "救恩論", "宗改"),
    # 教會學
    ("ecclesia",                    "教會學", "新約"),
    ("apostolic succession",        "教會學", "2c"),
    ("regula fidei",                "教會學", "2c"),
    ("magisterium",                 "教會學", "中世紀-梵二"),
    ("primacy of Peter",            "教會學", "教父-中世紀"),
    ("papal infallibility",         "教會學", "梵一"),
    ("synodality / conciliarity",   "教會學", "教父-現代"),
    ("autocephaly",                 "教會學", "東正教"),
    ("denomination",                "教會學", "近代"),
    ("ecumenism",                   "教會學", "20c"),
    ("nota ecclesiae (marks of the church)", "教會學", "宗改"),
    ("priesthood of all believers", "教會學", "宗改"),
    ("sensus fidei / fidelium",     "教會學", "梵二"),
    # 聖事
    ("sacrament",                   "聖事", "通用"),
    ("baptism",                     "聖事", "新約"),
    ("eucharist",                   "聖事", "新約"),
    ("transubstantiation",          "聖事", "中世紀"),
    ("consubstantiation",           "聖事", "宗改"),
    ("real presence",               "聖事", "通用"),
    ("symbolic memorial view",      "聖事", "宗改"),
    ("anamnesis",                   "聖事", "教父"),
    ("epiclesis",                   "聖事", "教父"),
    ("confirmation / chrismation",  "聖事", "教父"),
    ("penance / reconciliation",    "聖事", "中世紀"),
    ("anointing of the sick",       "聖事", "中世紀"),
    ("matrimony",                   "聖事", "中世紀"),
    ("holy orders",                 "聖事", "通用"),
    ("ex opere operato",            "聖事", "中世紀"),
    # 末世論
    ("eschatology",                 "末世論", "通用"),
    ("parousia",                    "末世論", "新約"),
    ("apocatastasis",               "末世論", "教父"),
    ("millennium / chiliasm",       "末世論", "新約-教父"),
    ("amillennialism",              "末世論", "近代"),
    ("postmillennialism",           "末世論", "近代"),
    ("premillennialism",            "末世論", "近代"),
    ("dispensationalism",           "末世論", "近代"),
    ("purgatory",                   "末世論", "中世紀"),
    ("particular judgment",         "末世論", "中世紀"),
    ("general resurrection",        "末世論", "新約"),
    ("beatific vision",             "末世論", "中世紀"),
    ("hell / hades / sheol / gehenna", "末世論", "新約-教父"),
    # 解經
    ("typology",                    "解經", "教父"),
    ("allegorical interpretation",  "解經", "教父"),
    ("literal sense",               "解經", "通用"),
    ("anagogical sense",            "解經", "中世紀"),
    ("tropological sense",          "解經", "中世紀"),
    ("quadriga (four senses)",      "解經", "中世紀"),
    ("Antiochene exegesis",         "解經", "4-5c"),
    ("Alexandrian exegesis",        "解經", "2-3c"),
    ("scopus",                      "解經", "宗改"),
    ("sola scriptura",              "解經", "宗改"),
    ("inerrancy",                   "解經", "近代"),
    ("inspiration",                 "解經", "通用"),
    ("canon (of scripture)",        "解經", "教父"),
    # 制度／教會法
    ("bishop / episcopos",          "制度", "新約"),
    ("presbyter / elder",           "制度", "新約"),
    ("deacon",                      "制度", "新約"),
    ("monasticism",                 "制度", "教父"),
    ("cenobitic / eremitic",        "制度", "教父"),
    ("see / cathedra",              "制度", "教父"),
    ("metropolitan / patriarch",    "制度", "教父"),
    ("ecumenical council",          "制度", "教父"),
    ("synod",                       "制度", "教父"),
    ("vicar / vicarius Christi",    "制度", "中世紀"),
    # 神學人類學
    ("imago Dei",                   "神學人類學", "教父"),
    ("nous",                        "神學人類學", "教父"),
    ("logos endiathetos vs prophorikos", "神學人類學", "2-3c"),
    ("body-soul-spirit (trichotomy)", "神學人類學", "教父"),
    ("body-soul (dichotomy)",       "神學人類學", "宗改"),
    ("freedom of will",             "神學人類學", "教父-宗改"),
    ("concupiscence",               "神學人類學", "中世紀"),
    # 倫理 / 靈修
    ("agape",                       "倫理靈修", "新約"),
    ("phronesis",                   "倫理靈修", "教父"),
    ("apatheia",                    "倫理靈修", "教父"),
    ("hesychasm",                   "倫理靈修", "中世紀東方"),
    ("kenosis (spiritual)",         "倫理靈修", "教父"),
    ("via negativa / apophatic",    "倫理靈修", "教父-中世紀"),
    ("via positiva / cataphatic",   "倫理靈修", "中世紀"),
    ("contemplation / theoria",     "倫理靈修", "教父"),
    ("praxis",                      "倫理靈修", "教父"),
    ("ascesis",                     "倫理靈修", "教父"),
    ("lectio divina",               "倫理靈修", "中世紀"),
    ("examen",                      "倫理靈修", "16c"),
    ("dark night of the soul",      "倫理靈修", "16c"),
    # 信仰準則 / 公會議
    ("Apostles' Creed",             "信經", "教父"),
    ("Nicene-Constantinopolitan Creed", "信經", "4c"),
    ("Athanasian Creed",            "信經", "4-5c"),
    ("Chalcedonian Definition",     "信經", "5c"),
    ("Tome of Leo",                 "信經", "5c"),
    ("anathema",                    "信經", "教父"),
    # 神聖名與位格
    ("YHWH / Tetragrammaton",       "神論", "舊約"),
    ("Pneuma",                      "神論", "新約"),
    ("aseity",                      "神論", "中世紀"),
    ("impassibility",               "神論", "教父"),
    ("immutability",                "神論", "教父"),
    ("omnipotence",                 "神論", "教父"),
    ("omniscience",                 "神論", "教父"),
    ("simplicity",                  "神論", "中世紀"),
    ("divine attributes",           "神論", "通用"),
    # 異端與運動
    ("Gnosticism",                  "異端", "2-3c"),
    ("Marcionism",                  "異端", "2c"),
    ("Montanism",                   "異端", "2-3c"),
    ("Donatism",                    "異端", "4c"),
    ("Manichaeism",                 "異端", "3-5c"),
    ("Iconoclasm",                  "異端爭議", "8-9c"),
    ("Catharism",                   "異端", "中世紀"),
    ("Quietism",                    "異端", "17c"),
    ("Jansenism",                   "天主教爭議", "17c"),
    ("modernism (theological)",     "現代爭議", "19-20c"),
]

# ============================================================================
# Gemini structured call
# ============================================================================

PERSON_PROMPT = """你是基督教神學歷史與翻譯專家。針對以下教父／神學家，請回傳結構化 JSON。

人物清單（每行一個英文常用名 + 已知 hint）：
{entries}

對每位回傳以下欄位（純 JSON array，不要 wrap markdown）：
- name_english: 原英文常用名
- name_original: 原文（希臘 / 拉丁 / 敘利亞 / 希伯來），含字母原文，不要羅馬化
- name_original_lang: grc / lat / syc / cop / arm / heb
- name_latin_std: 拉丁化標準名（e.g. Iustinus Martyr, Augustinus Hipponensis）
- nationality: 出身地／民族（繁體中文）
- born_year: 出生年（int，BC 用負數，不確定填 null）
- died_year: 卒年（int，不確定填 null）
- century: 活躍世紀 e.g. "2c" / "4-5c"
- school: 學派／傳統（繁體中文，e.g. 亞歷山大學派 / 安提阿學派 / 加帕多家三傑 / 拉丁西方 / 經院 / 路德派 / 改革宗 / 東正教 / ...）
- role: 身份（繁體中文，e.g. 使徒教父 / 護教士 / 教父 / 經院神學家 / 改教家 / 教會博士）
- name_protestant: 新教傳統中譯（華聯／證主／校園／改革宗常見譯名；多變體用「；」分隔）
- name_catholic_sgs: 思高傳統中譯（教廷／思高聖經學會）
- name_orthodox: 東正教中譯（東亞主教教區）
- name_hk: 香港中譯（基督教文藝／道風書社）
- name_tw: 台灣中譯（光啟／輔大）
- name_china_academic: 中國學界中譯
- name_recommended: 「建議採用」的單一譯名（繁體中文）
- recommendation_reason: 建議理由（繁體中文 2-3 句；應綜合：原文音譯接近度／傳統權威／學界通用度／使用者偏好）

關鍵規則：
- 如某傳統沒有獨立中譯（罕見人物或大家公用同譯），該欄可以填同樣譯名；但如果各傳統有實際不同的譯名，**務必如實列出差異**，不要全部填一樣
- Justin Martyr 一律建議「殉道者猶斯定」（使用者明確指示）
- Augustine of Hippo 一律建議「希波的奧古斯丁」
- 所有中文一律繁體（用「‧」中間點，不用「·」）
- 拉丁名要正確（不要寫成英文化）

各傳統慣用譯名差異的典型範例（請參照這種「真實差異」的填法）：

| 人物 | 新教 | 思高 | 東正教 | 中國學界 |
|---|---|---|---|---|
| Clement of Rome | 羅馬的革利免 | 羅馬‧克萊孟一世 | 羅馬的革利免 | 克勒孟一世 / 革利免 |
| Ignatius of Antioch | 安提阿的伊格那丟 | 安提約基雅‧依納爵 | 神聖致命者伊格納提 | 安條克的伊格那提烏斯 |
| Polycarp | 士每拿的坡旅甲 | 斯米爾納‧玻里加 | 司米爾納的聖波利卡爾普 | 波利卡普 |
| Justin Martyr | 殉道者游斯丁 | 殉道者猶斯定 | 殉道者尤斯丁 | 殉教者猶斯定 |
| Irenaeus of Lyon | 里昂的愛任紐 | 里昂‧依肋內 | 里昂的聖愛任紐 | 里昂的伊里奈烏 |
| Origen | 奧利金 | 奧利振 | 奧利根 | 奧利金 / 奧立振 |
| Tertullian | 特土良 | 戴爾都良 | 特土良 | 德爾圖良 |
| Cyprian | 居普良 | 西彼廉 | 迦太基的居普良 | 西普里安 |
| Athanasius | 亞他那修 | 阿塔納修 | 亞歷山大的聖阿塔納修 | 阿塔那修 |
| Augustine | 奧古斯丁 | 奧斯定 | 希波的聖奧古斯丁 | 奧古斯丁 |
| John Chrysostom | 屈梭多模 | 金口若望 | 聖金口約安 | 約翰‧克里索斯通 |
| Basil the Great | 大巴西流 | 大巴西略 | 大聖瓦西里 | 巴西爾大帝 |
| Gregory of Nazianzus | 拿先素斯的貴格利 | 額我略‧納齊安 | 神學家額我略 | 納齊安的格列高利 |
| Jerome | 耶柔米 | 熱羅尼莫 | 至福人耶柔米 | 哲羅姆 / 耶柔米 |
| Ambrose | 安波羅修 | 盎博羅削 | 米蘭的聖盎博羅削 | 安布羅斯 |
| Leo the Great | 大利奧 | 大良一世 | 教宗聖良 | 利奧一世 |
| Gregory the Great | 大格雷戈里 | 大額我略 | 教宗聖格列高利 | 格列高利一世 |
| Thomas Aquinas | 多瑪斯阿奎那 | 聖多瑪斯‧阿奎那 | （非東方傳統） | 托馬斯‧阿奎那 |

務必依照此種精度填寫，不可全欄填同樣譯名。新教 vs 思高 vs 東正教 vs 中國學界各自有自己的譯名傳統。

回傳純 JSON array，順序對應輸入清單。
"""

TERM_PROMPT = """你是基督教神學翻譯專家。針對以下神學名詞，請回傳結構化 JSON。

名詞清單（每行一個英文名 + 分類）：
{entries}

對每條回傳以下欄位（純 JSON array，不要 wrap markdown）：
- term_english: 英文原名
- term_original: 原文（希臘 / 拉丁 / 希伯來 / 敘利亞，含字母原文）
- term_original_lang: grc / lat / heb / syc / 多語則 multi
- term_latin_translit: 羅馬化／拉丁化（e.g. homoousios, perichōrēsis）
- category: 分類（沿用輸入提供的 category）
- era: 時期（e.g. 尼西亞前 / 尼西亞後 / 迦克墩 / 中世紀 / 宗改）
- zh_protestant: 新教傳統中譯
- zh_catholic_sgs: 思高傳統中譯
- zh_orthodox: 東正教中譯
- zh_hk: 香港中譯
- zh_tw: 台灣中譯
- zh_china_academic: 中國學界中譯
- zh_recommended: 建議採用的單一譯名
- recommendation_reason: 建議理由（繁體中文 2-3 句）
- definition_zh: 簡短中文釋義（2-3 句，繁體）

規則：
- 各傳統若無獨立譯法（多數通用詞會共用譯）就讓三-五欄相同；真的沒中譯才填 null
- homoousios → 建議「同質／同性同體」（思高用「同性同體」；新教用「同質」）
- Theotokos → 建議「天主之母／神之母」（思高=天主之母；新教=神之母／生神者）
- 中文一律繁體
- recommendation_reason 要點出在哪幾個傳統間有實質差異

回傳純 JSON array，順序對應輸入清單。
"""

def gemini_call(prompt: str, max_retries: int = 3) -> list:
    global _key_idx
    if not GEMINI_KEYS:
        raise RuntimeError("no Gemini API key")
    for attempt in range(max_retries):
        key = GEMINI_KEYS[_key_idx % len(GEMINI_KEYS)]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }
        try:
            r = requests.post(url, json=body, timeout=120)
            if r.status_code == 429 or r.status_code == 503:
                print(f"  Gemini {r.status_code} key#{_key_idx % len(GEMINI_KEYS)} attempt {attempt+1}")
                _key_idx += 1
                time.sleep(3 * (attempt + 1))
                continue
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  parse error attempt {attempt+1}: {e}")
            time.sleep(3)
            continue
        except requests.RequestException as e:
            print(f"  http error attempt {attempt+1}: {e}")
            _key_idx += 1
            time.sleep(5)
            continue
    raise RuntimeError(f"Gemini failed after {max_retries} attempts")


# ---- Haiku fallback (Anthropic OAuth, same client as translate_ebook_to_zh.py) ----
_anthropic_client = None
_anthropic_client_cred_mtime = 0.0
HAIKU_MODEL = "claude-haiku-4-5-20251001"

def _make_anthropic_client():
    import anthropic as _anth
    from pathlib import Path
    common_kwargs = {"default_headers": {"anthropic-beta": "oauth-2025-04-20"}}
    cred = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred.exists():
        creds = json.loads(cred.read_text(encoding="utf-8"))
        token = creds.get("claudeAiOauth", {}).get("accessToken", "")
        if token:
            return _anth.Anthropic(auth_token=token, **common_kwargs)
    raise RuntimeError("No Anthropic credentials")

def _refresh_anthropic():
    global _anthropic_client, _anthropic_client_cred_mtime
    from pathlib import Path
    cred = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred.exists():
        m = cred.stat().st_mtime
        if m > _anthropic_client_cred_mtime:
            _anthropic_client = _make_anthropic_client()
            _anthropic_client_cred_mtime = m
    elif _anthropic_client is None:
        _anthropic_client = _make_anthropic_client()

def haiku_call(prompt: str, max_retries: int = 6) -> list:
    """Anthropic Haiku fallback. Returns parsed JSON list.
    Retries: RateLimitError 429, OverloadedError 529, APIConnectionError,
    APITimeoutError, InternalServerError 5xx, JSON parse errors."""
    import anthropic as _anth
    _refresh_anthropic()
    backoffs = [0, 30, 60, 120, 240, 480]
    for attempt, wait in enumerate(backoffs[:max_retries], start=1):
        if wait:
            print(f"  Haiku backoff {wait}s attempt {attempt}", flush=True)
            time.sleep(wait)
        try:
            msg = _anthropic_client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt + "\n\n只回傳 pure JSON array，不要 markdown code block。"}],
            )
            text = "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
            if text.startswith("```"):
                text = text.split("```", 2)[1]
                if text.startswith("json"):
                    text = text[4:].lstrip()
                text = text.rsplit("```", 1)[0].strip()
            return json.loads(text)
        except _anth.RateLimitError:
            print(f"  Haiku 429 rate-limit attempt {attempt}/{max_retries}", flush=True)
        except (_anth.APIStatusError) as e:
            status = getattr(e, "status_code", None)
            if status in (502, 503, 504, 529):
                print(f"  Haiku {status} overloaded attempt {attempt}/{max_retries}", flush=True)
            elif status == 401:
                print(f"  Haiku 401 — re-reading credentials", flush=True)
                global _anthropic_client_cred_mtime
                _anthropic_client_cred_mtime = 0.0
                _refresh_anthropic()
            else:
                print(f"  Haiku {status} {type(e).__name__}: {str(e)[:200]}", flush=True)
        except (_anth.APIConnectionError, _anth.APITimeoutError) as e:
            print(f"  Haiku conn error attempt {attempt}: {type(e).__name__}", flush=True)
        except _anth.AuthenticationError:
            print(f"  Haiku 401 — re-reading credentials", flush=True)
            _anthropic_client_cred_mtime = 0.0
            _refresh_anthropic()
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Haiku parse error attempt {attempt}: {e}", flush=True)
    raise RuntimeError(f"Haiku failed after {max_retries} attempts")


def llm_call(prompt: str, engine: str) -> list:
    """Try gemini first, fall back to haiku if all keys exhausted."""
    if engine == "haiku":
        return haiku_call(prompt)
    try:
        return gemini_call(prompt)
    except RuntimeError as e:
        print(f"  Gemini exhausted ({e}) → fallback to Haiku")
        return haiku_call(prompt)


def fetch_existing(table: str, key_field: str, key_values: list[str]) -> dict:
    """Return {key_value: row} for existing rows."""
    if not key_values:
        return {}
    out = {}
    # batch in chunks of 50 to keep URL short
    for i in range(0, len(key_values), 50):
        batch = key_values[i:i+50]
        inlist = ",".join(f'"{v}"' for v in batch)
        r = requests.get(
            f"{URL}/rest/v1/{table}?{key_field}=in.({inlist})&select=*",
            headers=H_GET, timeout=30,
        )
        r.raise_for_status()
        for row in r.json():
            out[row[key_field]] = row
    return out


def upsert(table: str, rows: list[dict], key_field: str):
    # PostgREST upsert needs on_conflict in query string
    r = requests.post(
        f"{URL}/rest/v1/{table}?on_conflict={key_field}",
        headers=H_UPSERT, json=rows, timeout=60,
    )
    if r.status_code >= 300:
        print(f"  UPSERT ERROR {r.status_code}: {r.text[:500]}")
        return
    return r.json()


def fill_theologians(resume: bool, limit: int | None):
    master = THEOLOGIANS_MASTER[:]
    name_keys = [m[0] for m in master]
    existing = fetch_existing("theologians", "name_english", name_keys) if resume else {}
    todo = []
    for i, (name, century, nat, role) in enumerate(master):
        ex = existing.get(name)
        if ex and ex.get("name_recommended"):
            continue
        todo.append((i, name, century, nat, role))
    if limit:
        todo = todo[:limit]
    print(f"Theologians: {len(master)} total, {len(todo)} to fill")

    BATCH = 5
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        entries = "\n".join(
            f"- {name}  (世紀:{century or '?'} / 出身:{nat or '?'} / 身份:{role or '?'})"
            for _, name, century, nat, role in batch
        )
        print(f"\n[batch {i//BATCH+1}/{-(-len(todo)//BATCH)}]  {len(batch)} entries: {', '.join(b[1] for b in batch)}")
        t0 = time.time()
        try:
            results = llm_call(PERSON_PROMPT.format(entries=entries), ENGINE)
        except Exception as e:
            print(f"  ✗ batch failed: {type(e).__name__}: {e}")
            continue
        # add sort_order = master index for ordering
        rows = []
        for idx, (orig_idx, name, *_) in enumerate(batch):
            # match by name_english (Gemini might reorder)
            match = next((r for r in results if r.get("name_english", "").strip().lower() == name.lower()), None)
            if not match:
                print(f"  ✗ no match for {name}")
                continue
            match["sort_order"] = orig_idx
            match["updated_at"] = "now()"
            # null sentinel cleanup
            for k, v in list(match.items()):
                if isinstance(v, str) and v.lower() in ("null", "none", "n/a", "?"):
                    match[k] = None
            rows.append(match)
        if rows:
            upsert("theologians", rows, "name_english")
            print(f"  ✓ {len(rows)} upserted in {time.time()-t0:.1f}s")


def fill_terms(resume: bool, limit: int | None):
    master = TERMS_MASTER[:]
    name_keys = [m[0] for m in master]
    existing = fetch_existing("theological_terms", "term_english", name_keys) if resume else {}
    todo = []
    for i, (term, cat, era) in enumerate(master):
        ex = existing.get(term)
        if ex and ex.get("zh_recommended"):
            continue
        todo.append((i, term, cat, era))
    if limit:
        todo = todo[:limit]
    print(f"Terms: {len(master)} total, {len(todo)} to fill")

    BATCH = 6
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i+BATCH]
        entries = "\n".join(
            f"- {term}  (分類:{cat} / 時期:{era})"
            for _, term, cat, era in batch
        )
        print(f"\n[batch {i//BATCH+1}/{-(-len(todo)//BATCH)}]  {len(batch)}: {', '.join(b[1] for b in batch)}")
        t0 = time.time()
        try:
            results = llm_call(TERM_PROMPT.format(entries=entries), ENGINE)
        except Exception as e:
            print(f"  ✗ batch failed: {type(e).__name__}: {e}")
            continue
        rows = []
        for idx, (orig_idx, term, *_) in enumerate(batch):
            match = next((r for r in results if r.get("term_english", "").strip().lower() == term.lower()), None)
            if not match:
                print(f"  ✗ no match for {term}")
                continue
            match["sort_order"] = orig_idx
            match["updated_at"] = "now()"
            for k, v in list(match.items()):
                if isinstance(v, str) and v.lower() in ("null", "none", "n/a", "?"):
                    match[k] = None
            rows.append(match)
        if rows:
            upsert("theological_terms", rows, "term_english")
            print(f"  ✓ {len(rows)} upserted in {time.time()-t0:.1f}s")


# ============================================================================
# Add unique constraints once (idempotent — IF NOT EXISTS via DO block)
# ============================================================================

def ensure_unique():
    sql = """
    DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'theologians_name_english_key') THEN
            ALTER TABLE theologians ADD CONSTRAINT theologians_name_english_key UNIQUE (name_english);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'theological_terms_term_english_key') THEN
            ALTER TABLE theological_terms ADD CONSTRAINT theological_terms_term_english_key UNIQUE (term_english);
        END IF;
    END $$;
    """
    ref = os.environ['SUPABASE_URL'].split('//')[1].split('.')[0]
    token = os.environ['SUPABASE_ACCESS_TOKEN']
    r = requests.post(
        f'https://api.supabase.com/v1/projects/{ref}/database/query',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'query': sql}, timeout=60,
    )
    print(f"Ensure unique constraints: {r.status_code}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["people", "terms", "both"], default="both")
    ap.add_argument("--resume", action="store_true", help="skip rows with name_recommended/zh_recommended already filled")
    ap.add_argument("--limit", type=int, default=None, help="cap entries (smoke test)")
    ap.add_argument("--engine", choices=["gemini", "haiku"], default="gemini",
                    help="gemini = try gemini first then haiku fallback; haiku = haiku only")
    args = ap.parse_args()

    ENGINE = args.engine

    ensure_unique()

    if args.target in ("people", "both"):
        fill_theologians(args.resume, args.limit)
    if args.target in ("terms", "both"):
        fill_terms(args.resume, args.limit)

    print("\nDone.")
