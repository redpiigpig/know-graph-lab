"""
Seed historical_rulers for /translation-glossary (「歷代帝王」tab) — HAND-CURATED.

跟 seed_glossary_places.py 並列、同政策：純人工策展（無 LLM），定名「確定」。
帝王譯名規則（補 /translation-glossary 翻譯原則）：
  - 聖經出現過的帝王 → name_recommended 用通行學界譯，和合本/思高譯放 name_variants
    （極通行的和合本譯如「尼布甲尼撒/西拿基立/希西家」本身即標準，直接用）。
  - polity 欄對齊 place_names 的王朝-民族帝國名（阿契美尼德-波斯帝國／塞琉古-希臘帝國…），
    使「國名與城市」與「歷代帝王」兩 tab 一致。
  - name_root 沿用既有名根（密特／塞琉／亞歷山／托勒密／君士坦丁／大流士／安條克…）。
  - 鄂圖曼(王朝/帝國) vs 奧斯曼(開國者 Osman 人名) 為既成中譯分流，不強制同根（notes 標明）。

Usage:
  python scripts/seed_glossary_rulers.py --dry
  python scripts/seed_glossary_rulers.py
"""
from __future__ import annotations
import os, sys, io, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import requests
from dotenv import load_dotenv
load_dotenv(".env")

URL = os.environ["SUPABASE_URL"]
SVC = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SVC, "Authorization": f"Bearer {SVC}"}
H_UPSERT = {**H, "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"}

ROWS: list[dict] = []
_order = 0


def R(en, rec, *, o="", lang="", rom="", var="", reason="", root="",
      polity="", title="", region="", rs=None, re=None, notes=""):
    global _order
    _order += 10
    ROWS.append({
        "name_english": en, "name_original": o or None,
        "name_original_lang": lang or None, "name_romanized": rom or None,
        "name_recommended": rec, "name_variants": var or None,
        "recommendation_reason": reason or None, "name_root": root or None,
        "polity": polity or None, "title": title or None, "region": region or None,
        "reign_start": rs, "reign_end": re, "notes": notes or None,
        "sort_order": _order,
    })


# ════════════════════════════════════════════════════════════════════════════
# 亞述帝國  (sort 1000–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1000
P_ASSYRIA = "亞述帝國"
R("Tiglath-Pileser III", "提革拉毘列色三世", var="提格拉特帕拉沙爾三世（史學）；普勒(Pul)",
  rom="Tukultī-apil-Ešarra", root="提革拉", polity=P_ASSYRIA, title="國王",
  region="美索不達米亞", rs=-745, re=-727,
  reason="和合本王下15:29作「提革拉毘列色」，王下15:19稱「普勒」；史學作提格拉特帕拉沙爾")
R("Shalmaneser V", "撒縵以色五世", var="沙爾馬那塞爾五世（史學）",
  rom="Šulmānu-ašarēd", polity=P_ASSYRIA, title="國王", region="美索不達米亞",
  rs=-727, re=-722, reason="和合本王下17:3作「撒縵以色」")
R("Sargon II", "撒珥根二世", var="薩爾貢二世（史學）", rom="Šarru-kīn",
  polity=P_ASSYRIA, title="國王", region="美索不達米亞", rs=-722, re=-705,
  reason="賽20:1作「撒珥根」；史學作薩爾貢")
R("Sennacherib", "西拿基立", var="辛那赫里布（史學）", rom="Sîn-aḫḫē-erība",
  polity=P_ASSYRIA, title="國王", region="美索不達米亞", rs=-705, re=-681,
  reason="和合本王下18:13通行作「西拿基立」，即標準")
R("Esarhaddon", "以撒哈頓", var="阿薩爾哈東（史學）", rom="Aššur-aḫa-iddina",
  polity=P_ASSYRIA, title="國王", region="美索不達米亞", rs=-681, re=-669,
  reason="和合本王下19:37作「以撒哈頓」")
R("Ashurbanipal", "亞述巴尼帕", var="亞斯那巴（拉4:10）；阿淑爾巴尼拔", root="亞述",
  rom="Aššur-bāni-apli", polity=P_ASSYRIA, title="國王", region="美索不達米亞",
  rs=-669, re=-631, reason="史學通行「亞述巴尼帕」；拉4:10和合作「亞斯那巴」")

# ════════════════════════════════════════════════════════════════════════════
# 新巴比倫帝國  (sort 1200–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1200
P_BABYLON = "新巴比倫帝國"
R("Nabopolassar", "那波帕拉薩爾", var="納波波拉薩", rom="Nabû-apla-uṣur",
  polity=P_BABYLON, title="國王", region="美索不達米亞", rs=-626, re=-605,
  reason="新巴比倫（迦勒底）王朝奠基者")
R("Nebuchadnezzar II", "尼布甲尼撒二世", var="尼布甲尼撒爾（思高拿步高）", root="尼布甲尼撒",
  rom="Nabû-kudurri-uṣur", polity=P_BABYLON, title="國王", region="美索不達米亞",
  rs=-605, re=-562, reason="和合本但/耶通行「尼布甲尼撒」即標準；思高作「拿步高」")
R("Amel-Marduk", "以未米羅達", var="阿邁爾-馬爾杜克（史學）", rom="Amēl-Marduk",
  polity=P_BABYLON, title="國王", region="美索不達米亞", rs=-562, re=-560,
  reason="和合本王下25:27作「以未米羅達」(Evil-Merodach)")
R("Belshazzar", "伯沙撒", var="貝爾沙薩（史學）", rom="Bēl-šar-uṣur",
  polity=P_BABYLON, title="攝政／太子", region="美索不達米亞",
  reason="但5「伯沙撒」；那波尼度之子、實際攝政")
R("Nabonidus", "那波尼度斯", var="拿波尼度", rom="Nabû-naʾid",
  polity=P_BABYLON, title="國王", region="美索不達米亞", rs=-556, re=-539,
  reason="新巴比倫末代王")

# ════════════════════════════════════════════════════════════════════════════
# 瑪代  (sort 1350–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1350
R("Cyaxares", "基亞克薩雷斯", var="夏克薩列", lang="peo", polity="瑪代",
  title="國王", region="伊朗高原", rs=-625, re=-585)
R("Astyages", "阿斯提阿格斯", var="阿斯提亞格", lang="grc", o="Ἀστυάγης",
  polity="瑪代", title="國王", region="伊朗高原", rs=-585, re=-550,
  reason="末代瑪代王，外孫居魯士滅之")
R("Darius the Mede", "大利烏（瑪代人大流士）", var="瑪代人大流士", root="大流士",
  polity="瑪代", title="國王", region="伊朗高原",
  reason="但5:31「瑪代人大利烏」；身分史學有爭議，名根「大流士」")

# ════════════════════════════════════════════════════════════════════════════
# 阿契美尼德-波斯帝國  (sort 1500–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1500
P_PERSIA = "阿契美尼德-波斯帝國"
R("Cyrus II the Great", "居魯士二世", var="古列（和合本）；塞魯士；居魯士大帝", root="居魯士",
  o="Κῦρος", lang="grc", polity=P_PERSIA, title="沙阿（萬王之王）", region="波斯",
  rs=-559, re=-530, reason="史學/宗教學通行「居魯士」；和合本代下36/拉1作「古列」")
R("Cambyses II", "岡比西斯二世", var="坎拜西斯", o="Καμβύσης", lang="grc",
  polity=P_PERSIA, title="沙阿", region="波斯", rs=-530, re=-522,
  reason="居魯士之子，征服埃及")
R("Darius I the Great", "大流士一世", var="大利烏（和合但6）；大流士大帝", root="大流士",
  o="Δαρεῖος", lang="grc", polity=P_PERSIA, title="沙阿", region="波斯",
  rs=-522, re=-486, reason="拉4-6准建聖殿者；名根「大流士」")
R("Xerxes I", "薛西斯一世", var="亞哈隨魯（和合本以斯帖記）；澤克西斯", root="薛西",
  o="Ξέρξης", lang="grc", polity=P_PERSIA, title="沙阿", region="波斯",
  rs=-486, re=-465, reason="以斯帖記「亞哈隨魯」即此王；史學作薛西斯；名根「薛西」與亞達薛西共享")
R("Artaxerxes I", "亞達薛西一世", var="阿爾塔薛西斯（史學）", root="薛西",
  o="Ἀρταξέρξης", lang="grc", polity=P_PERSIA, title="沙阿", region="波斯",
  rs=-465, re=-424, reason="拉7/尼2差尼希米回耶路撒冷者；和合作「亞達薛西」")
R("Darius III", "大流士三世", var="大流士‧科多曼努斯", root="大流士",
  o="Δαρεῖος", lang="grc", polity=P_PERSIA, title="沙阿", region="波斯",
  rs=-336, re=-330, reason="末代波斯王，敗於亞歷山大")

# ════════════════════════════════════════════════════════════════════════════
# 古埃及法老 + 托勒密  (sort 1750–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1750
R("Thutmose III", "圖特摩斯三世", var="杜得模斯三世", polity="古埃及（新王國）",
  title="法老", region="埃及", rs=-1479, re=-1425, root="圖特摩斯")
R("Ramesses II", "拉美西斯二世", var="蘭塞（出1:11城名）；拉美西斯大帝", root="拉美西斯",
  polity="古埃及（新王國）", title="法老", region="埃及", rs=-1279, re=-1213,
  reason="常被指為出埃及記法老（學界有爭議）")
R("Shoshenq I", "示撒", var="舍順克一世（史學）", polity="古埃及（第22王朝）",
  title="法老", region="埃及", rs=-943, re=-922,
  reason="王上14:25掠耶路撒冷的「示撒」；史學作舍順克一世")
R("Necho II", "尼哥二世", var="尼科二世（史學）", polity="古埃及（第26王朝）",
  title="法老", region="埃及", rs=-610, re=-595,
  reason="王下23:29殺約西亞的「法老尼哥」")
R("Apries", "合弗拉", var="阿普里斯（史學）；法老合弗拉", polity="古埃及（第26王朝）",
  title="法老", region="埃及", rs=-589, re=-570, reason="耶44:30「法老合弗拉」")
R("Ptolemy I Soter", "托勒密一世", var="托勒密‧索特爾（救主）", root="托勒密",
  o="Πτολεμαῖος", lang="grc", polity="托勒密-希臘王國", title="法老／國王",
  region="埃及", rs=-305, re=-282, reason="托勒密王朝奠基者；名根「托勒密」")
R("Cleopatra VII", "克麗奧佩脫拉七世", var="克莉奧帕特拉（陸）；埃及艷后", root="克麗奧",
  o="Κλεοπάτρα", lang="grc", polity="托勒密-希臘王國", title="女王", region="埃及",
  rs=-51, re=-30, reason="托勒密末代統治者")

# ════════════════════════════════════════════════════════════════════════════
# 塞琉古-希臘帝國  (sort 2000–)
# ════════════════════════════════════════════════════════════════════════════
_order = 2000
P_SEL = "塞琉古-希臘帝國"
R("Seleucus I Nicator", "塞琉古一世", var="西流古", root="塞琉", o="Σέλευκος",
  lang="grc", rom="Seleukos", polity=P_SEL, title="國王", region="敘利亞／美索不達米亞",
  rs=-305, re=-281, reason="塞琉古帝國奠基者，名根「塞琉」")
R("Antiochus III the Great", "安條克三世", var="安提阿哥三世（思高）；大帝", root="安條克",
  o="Ἀντίοχος", lang="grc", polity=P_SEL, title="國王", region="敘利亞",
  rs=-222, re=-187, reason="名根「安條克」（與城市安提阿中譯分流）")
R("Antiochus IV Epiphanes", "安條克四世（伊比法尼）", var="安提阿哥四世（思高瑪加伯傳）", root="安條克",
  o="Ἀντίοχος", lang="grc", polity=P_SEL, title="國王", region="敘利亞",
  rs=-175, re=-164, reason="但11/瑪加伯傳之褻瀆聖殿者；思高作「安提阿哥」")

# ════════════════════════════════════════════════════════════════════════════
# 馬其頓／亞歷山大帝國  (sort 2200–)
# ════════════════════════════════════════════════════════════════════════════
_order = 2200
R("Philip II of Macedon", "腓力二世", var="菲利普二世（陸）", o="Φίλιππος",
  lang="grc", polity="馬其頓王國", title="國王", region="希臘北", rs=-359, re=-336,
  root="腓力", reason="亞歷山大之父")
R("Alexander the Great", "亞歷山大大帝", var="亞歷山大三世", root="亞歷山",
  o="Ἀλέξανδρος", lang="grc", rom="Alexandros", polity="亞歷山大帝國",
  title="國王／皇帝", region="希臘／波斯", rs=-336, re=-323,
  reason="名根「亞歷山」與亞歷山卓城一致；其帝國採單一人物例外命名")

# ════════════════════════════════════════════════════════════════════════════
# 羅馬皇帝  (sort 2400–)
# ════════════════════════════════════════════════════════════════════════════
_order = 2400
P_ROME = "羅馬帝國"
R("Augustus", "奧古斯都", var="屋大維；該撒亞古士督（和合本路2:1）", o="Augustus",
  lang="lat", polity=P_ROME, title="皇帝", region="羅馬", rs=-27, re=14,
  reason="路2:1報名上冊之「該撒亞古士督」；史學通行「奧古斯都」")
R("Tiberius", "提庇留", var="提比略（陸）", o="Tiberius", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=14, re=37,
  reason="路3:1；耶穌受難時在位")
R("Caligula", "卡利古拉", var="該猶斯", o="Caligula", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=37, re=41)
R("Claudius", "革老丟", var="克勞狄烏斯（史學）", o="Claudius", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=41, re=54,
  reason="徒11:28/18:2「革老丟」；史學作克勞狄烏斯")
R("Nero", "尼祿", var="尼羅；尼祿王", o="Nero", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=54, re=68,
  reason="逼迫教會，傳統下彼得保羅殉道於其時")
R("Vespasian", "維斯帕先", var="韋斯巴薌", o="Vespasianus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=69, re=79, root="維斯帕")
R("Titus", "提圖斯", var="提多（與聖經提多同名，本指皇帝）", o="Titus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=79, re=81,
  reason="70年毀耶路撒冷聖殿；勿與保羅書信收信人提多混淆")
R("Domitian", "圖密善", var="多米田（思高）", o="Domitianus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=81, re=96,
  reason="傳統下啟示錄寫作期之逼迫皇帝")
R("Trajan", "圖拉真", var="特拉揚", o="Traianus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=98, re=117,
  reason="與小普林尼通信論基督徒；伊格那丟殉道於其時")
R("Hadrian", "哈德良", var="阿德里安", o="Hadrianus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=117, re=138,
  reason="平巴柯巴起義，建Aelia Capitolina")
R("Marcus Aurelius", "馬可‧奧勒留", var="奧理略；瑪爾庫斯‧奧雷里烏斯", o="Marcus Aurelius",
  lang="lat", polity=P_ROME, title="皇帝", region="羅馬", rs=161, re=180,
  reason="斯多噶哲人皇帝；護教士游斯丁殉道於其時")
R("Septimius Severus", "塞普提米烏斯‧塞維魯", var="塞維魯", o="Septimius Severus",
  lang="lat", polity=P_ROME, title="皇帝", region="羅馬", rs=193, re=211, root="塞維魯")
R("Decius", "德修", var="德西烏斯（史學）", o="Decius", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=249, re=251,
  reason="首次帝國全面逼迫教會（249-251）")
R("Valerian", "瓦勒良", var="瓦萊里安", o="Valerianus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=253, re=260,
  reason="逼迫教會，居普良殉道於其時；後為薩珊沙普爾一世所擒")
R("Diocletian", "戴克里先", var="迪奧克里先", o="Diocletianus", lang="lat",
  polity=P_ROME, title="皇帝", region="羅馬", rs=284, re=305,
  reason="四帝共治；大逼迫（303）發動者")
R("Constantine I the Great", "君士坦丁一世", var="君士坦丁大帝", root="君士坦丁",
  o="Constantinus", lang="lat", polity=P_ROME, title="皇帝", region="羅馬／拜占庭",
  rs=306, re=337, reason="米蘭敕令、召開尼西亞會議；名根「君士坦丁」與城一致")
R("Julian the Apostate", "背教者尤利安", var="朱利安；猶利安；叛教者尤利安", root="尤利安",
  o="Iulianus", lang="lat", polity=P_ROME, title="皇帝", region="羅馬", rs=361, re=363,
  reason="末位異教皇帝，欲復興多神教")
R("Theodosius I", "狄奧多西一世", var="狄奧多西大帝；提阿多修", root="狄奧多西",
  o="Theodosius", lang="lat", polity=P_ROME, title="皇帝", region="羅馬", rs=379, re=395,
  reason="定基督教為國教（380）；帝國末次統一後永久東西分治")

# ════════════════════════════════════════════════════════════════════════════
# 拜占庭（東羅馬）皇帝  (sort 2800–)
# ════════════════════════════════════════════════════════════════════════════
_order = 2800
P_BYZ = "拜占庭帝國"
R("Justinian I", "查士丁尼一世", var="優士丁尼（思高/東正教）；游斯丁尼", root="查士丁尼",
  o="Ἰουστινιανός", lang="grc", polity=P_BYZ, title="皇帝", region="拜占庭",
  rs=527, re=565, reason="《查士丁尼法典》、聖索菲亞大教堂")
R("Heraclius", "希拉克略", var="伊拉克略", o="Ἡράκλειος", lang="grc",
  polity=P_BYZ, title="皇帝", region="拜占庭", rs=610, re=641,
  reason="對薩珊得勝、旋失地於阿拉伯")
R("Leo III the Isaurian", "利奧三世", var="伊掃利亞王朝利奧三世；良三世", root="利奧",
  o="Λέων", lang="grc", polity=P_BYZ, title="皇帝", region="拜占庭", rs=717, re=741,
  reason="發動毀像運動(726)")
R("Basil II", "巴西爾二世", var="瓦西里二世（保加利亞屠夫）", root="巴西爾",
  o="Βασίλειος", lang="grc", polity=P_BYZ, title="皇帝", region="拜占庭",
  rs=976, re=1025)
R("Constantine XI Palaiologos", "君士坦丁十一世", var="君士坦丁‧帕里奧洛戈斯", root="君士坦丁",
  o="Κωνσταντῖνος", lang="grc", polity=P_BYZ, title="皇帝", region="拜占庭",
  rs=1449, re=1453, reason="末代拜占庭皇帝，1453君士坦丁堡陷落殉國")

# ════════════════════════════════════════════════════════════════════════════
# 薩珊-波斯帝國  (sort 3000–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3000
P_SAS = "薩珊-波斯帝國"
R("Ardashir I", "阿爾達希爾一世", var="阿爾達栩", lang="pal", polity=P_SAS,
  title="沙阿（萬王之王）", region="波斯", rs=224, re=242, reason="薩珊王朝奠基者")
R("Shapur I", "沙普爾一世", var="夏普爾一世", lang="pal", polity=P_SAS,
  title="沙阿", region="波斯", rs=240, re=270, root="沙普爾",
  reason="擒羅馬皇帝瓦勒良；摩尼活躍於其朝")
R("Khosrow I", "霍斯勞一世", var="庫斯老一世（不朽的靈魂）", lang="pal", polity=P_SAS,
  title="沙阿", region="波斯", rs=531, re=579, root="霍斯勞", reason="薩珊極盛之君")

# ════════════════════════════════════════════════════════════════════════════
# 哈里發（正統/伍麥亞/阿拔斯）  (sort 3300–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3300
P_RASH = "正統哈里發國"
R("Abu Bakr", "阿布‧伯克爾", var="艾布‧伯克爾", lang="ar", polity=P_RASH,
  title="哈里發", region="阿拉伯", rs=632, re=634, reason="首任正統哈里發")
R("Umar ibn al-Khattab", "歐麥爾", var="奧馬爾；歐瑪爾", lang="ar", polity=P_RASH,
  title="哈里發", region="阿拉伯", rs=634, re=644, reason="第二任，大征服時期")
R("Uthman ibn Affan", "奧斯曼（哈里發）", var="奧特曼‧伊本‧阿凡", lang="ar", polity=P_RASH,
  title="哈里發", region="阿拉伯", rs=644, re=656,
  notes="與鄂圖曼開國者 Osman 中譯同作「奧斯曼」但非同人，須區別")
R("Ali ibn Abi Talib", "阿里", var="阿里‧伊本‧阿比‧塔利卜", lang="ar", polity=P_RASH,
  title="哈里發", region="阿拉伯", rs=656, re=661,
  notes="第四任；什葉派尊為首位伊瑪目")
R("Muawiya I", "穆阿維葉一世", var="穆阿維亞", lang="ar", polity="伍麥亞-阿拉伯帝國",
  title="哈里發", region="敘利亞", rs=661, re=680, reason="伍麥亞王朝奠基者")
R("Harun al-Rashid", "哈倫‧拉希德", var="哈倫‧賴世德", lang="ar",
  polity="阿拔斯-阿拉伯帝國", title="哈里發", region="美索不達米亞", rs=786, re=809,
  reason="阿拔斯極盛、《一千零一夜》背景之君")
R("Al-Ma'mun", "馬蒙", var="麥蒙", lang="ar", polity="阿拔斯-阿拉伯帝國",
  title="哈里發", region="美索不達米亞", rs=813, re=833, reason="智慧宮、翻譯運動贊助者")

# ════════════════════════════════════════════════════════════════════════════
# 鄂圖曼-土耳其帝國蘇丹  (sort 3600–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3600
P_OTT = "鄂圖曼-土耳其帝國"
R("Osman I", "奧斯曼一世", var="鄂圖曼一世（與王朝同源）", lang="ota", polity=P_OTT,
  title="蘇丹", region="安納托利亞", rs=1299, re=1326,
  notes="王朝/帝國中譯作「鄂圖曼」，開國者人名慣作「奧斯曼」，為既成分流")
R("Mehmed II the Conqueror", "穆罕默德二世", var="默罕默德二世；征服者", lang="ota",
  polity=P_OTT, title="蘇丹", region="安納托利亞", rs=1451, re=1481,
  reason="1453攻陷君士坦丁堡")
R("Selim I", "塞利姆一世", var="冷酷者塞利姆", lang="ota", polity=P_OTT,
  title="蘇丹", region="安納托利亞", rs=1512, re=1520, root="塞利姆")
R("Suleiman the Magnificent", "蘇萊曼一世", var="蘇里曼；立法者；大帝", lang="ota",
  polity=P_OTT, title="蘇丹", region="安納托利亞", rs=1520, re=1566,
  reason="鄂圖曼極盛之君")

# ════════════════════════════════════════════════════════════════════════════
# 法蘭克／神聖羅馬帝國  (sort 3900–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3900
R("Charlemagne", "查理曼", var="查理大帝；卡爾大帝", root="查理曼", o="Carolus Magnus",
  lang="lat", polity="卡洛林-法蘭克帝國", title="皇帝", region="西歐", rs=768, re=814,
  reason="800年加冕為皇帝；名與「卡洛林-法蘭克帝國」呼應")
R("Otto I the Great", "奧托一世", var="鄂圖一世；奧托大帝", o="Otto", lang="lat",
  polity="神聖羅馬帝國", title="皇帝", region="中歐", rs=962, re=973,
  reason="962加冕，神聖羅馬帝國肇建", root="奧托")
R("Frederick I Barbarossa", "腓特烈一世", var="紅鬍子腓特烈；巴巴羅薩", root="腓特烈",
  lang="de", polity="神聖羅馬帝國", title="皇帝", region="中歐", rs=1155, re=1190)
R("Charles V (HRE)", "查理五世", var="卡爾五世（神羅）；卡洛斯一世（西班牙）",
  lang="de", polity="神聖羅馬帝國／哈布斯堡", title="皇帝", region="中歐／西班牙",
  rs=1519, re=1556, reason="路德宗改時的神羅皇帝（沃木斯議會）")

# ════════════════════════════════════════════════════════════════════════════
# 近代歐洲君主  (sort 4200–)
# ════════════════════════════════════════════════════════════════════════════
_order = 4200
R("Louis IX of France", "路易九世", var="聖路易", o="Louis", lang="fr",
  polity="法蘭西王國", title="國王", region="西歐", rs=1226, re=1270, root="路易")
R("Henry VIII", "亨利八世", var="亨利八世", lang="en", polity="英格蘭王國",
  title="國王", region="不列顛", rs=1509, re=1547, root="亨利",
  reason="英格蘭宗教改革、脫離羅馬")
R("Elizabeth I", "伊莉莎白一世", var="伊麗莎白一世（陸）", lang="en",
  polity="英格蘭王國", title="女王", region="不列顛", rs=1558, re=1603,
  reason="確立英國國教會；台作伊莉莎白，陸作伊麗莎白")
R("Louis XIV", "路易十四", var="太陽王", o="Louis", lang="fr", polity="法蘭西王國",
  title="國王", region="西歐", rs=1643, re=1715, root="路易",
  reason="撤銷南特敕令(1685)，逼迫胡格諾派")
R("Napoleon I", "拿破崙一世", var="拿破崙‧波拿巴", root="拿破崙", o="Napoléon",
  lang="fr", polity="拿破崙帝國", title="皇帝", region="西歐", rs=1804, re=1814,
  reason="法蘭西第一帝國；採單一人物例外命名")

# ════════════════════════════════════════════════════════════════════════════
# 薩法維／蒙兀兒／蒙古／帖木兒  (sort 4500–)
# ════════════════════════════════════════════════════════════════════════════
_order = 4500
R("Ismail I", "伊斯瑪儀一世", var="伊斯邁爾一世", lang="fa", polity="薩法維-波斯帝國",
  title="沙阿", region="波斯", rs=1501, re=1524, reason="薩法維王朝奠基者、定什葉派為國教")
R("Abbas I the Great", "阿巴斯一世", var="阿拔斯大帝（薩法維）", lang="fa",
  polity="薩法維-波斯帝國", title="沙阿", region="波斯", rs=1588, re=1629,
  notes="勿與阿拔斯王朝混淆")
R("Babur", "巴布爾", var="巴卑爾", lang="fa", polity="蒙兀兒-印度帝國",
  title="皇帝", region="南亞", rs=1526, re=1530, reason="蒙兀兒帝國奠基者")
R("Akbar the Great", "阿克巴", var="阿克巴大帝", lang="fa", polity="蒙兀兒-印度帝國",
  title="皇帝", region="南亞", rs=1556, re=1605, root="阿克巴")
R("Aurangzeb", "奧朗則布", var="奧朗則普", lang="fa", polity="蒙兀兒-印度帝國",
  title="皇帝", region="南亞", rs=1658, re=1707)
R("Genghis Khan", "成吉思汗", var="鐵木真", lang="mn", polity="蒙古帝國",
  title="大汗", region="歐亞草原", rs=1206, re=1227, reason="蒙古帝國奠基者")
R("Kublai Khan", "忽必烈", var="忽必烈汗；元世祖", lang="mn", polity="蒙古帝國／元",
  title="大汗／皇帝", region="東亞", rs=1260, re=1294)
R("Timur", "帖木兒", var="跛子帖木兒；塔默蘭(Tamerlane)", root="帖木兒", lang="fa",
  polity="帖木兒帝國", title="埃米爾", region="中亞", rs=1370, re=1405,
  reason="帖木兒帝國奠基者；採單一人物例外命名")

# ════════════════════════════════════════════════════════════════════════════
# 以色列／猶大 + 希律  (sort 4800–)
# ════════════════════════════════════════════════════════════════════════════
_order = 4800
R("Saul", "掃羅", var="撒烏耳（思高）", o="שָׁאוּל", lang="heb", polity="以色列聯合王國",
  title="王", region="黎凡特", reason="以色列首王；勿與使徒保羅原名掃羅混淆")
R("David", "大衛", var="達味（思高）", o="דָּוִד", lang="heb", polity="以色列聯合王國",
  title="王", region="黎凡特", root="大衛", reason="聖經傳統")
R("Solomon", "所羅門", var="撒羅滿（思高）", o="שְׁלֹמֹה", lang="heb",
  polity="以色列聯合王國", title="王", region="黎凡特", reason="聖經傳統")
R("Jeroboam I", "耶羅波安一世", var="雅洛貝罕（思高）", o="יָרָבְעָם", lang="heb",
  polity="以色列（北國）", title="王", region="黎凡特", reason="北國首王")
R("Ahab", "亞哈", var="阿哈布（思高）", o="אַחְאָב", lang="heb",
  polity="以色列（北國）", title="王", region="黎凡特", reason="以利亞時期之王")
R("Hezekiah", "希西家", var="希則克雅（思高）", o="חִזְקִיָּהוּ", lang="heb",
  polity="猶大（南國）", title="王", region="黎凡特", reason="抗西拿基立、宗教改革")
R("Josiah", "約西亞", var="約史雅（思高）", o="יֹאשִׁיָּהוּ", lang="heb",
  polity="猶大（南國）", title="王", region="黎凡特", reason="申命記改革")
R("Herod the Great", "希律大帝", var="黑落德（思高）；大希律", root="希律",
  o="Ἡρῴδης", lang="grc", polity="希律王朝（羅馬附庸）", title="王", region="黎凡特",
  rs=-37, re=-4, reason="太2屠嬰之王；擴建第二聖殿")


# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════
def check_roots():
    bad = []
    for r in ROWS:
        root = (r.get("name_root") or "").strip()
        rec = r.get("name_recommended") or ""
        if root and root not in rec:
            bad.append((r["name_english"], rec, root))
    return bad


def upsert(rows):
    for i in range(0, len(rows), 100):
        batch = rows[i:i+100]
        r = requests.post(
            f"{URL}/rest/v1/historical_rulers?on_conflict=name_english",
            headers=H_UPSERT, json=batch, timeout=90,
        )
        if r.status_code >= 300:
            print(f"  UPSERT ERROR {r.status_code}: {r.text[:500]}")
            return False
        print(f"  ✓ upserted {len(batch)} (rows {i+1}–{i+len(batch)})")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    seen = {}
    for r in ROWS:
        seen[r["name_english"]] = seen.get(r["name_english"], 0) + 1
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups:
        print(f"⚠️  重複 name_english：{dups}")

    bad = check_roots()
    if bad:
        print(f"⚠️  名根不一致 {len(bad)} 筆：")
        for en, rec, root in bad:
            print(f"    {en}: 「{rec}」未含 root「{root}」")
    else:
        print("✓ 名根一致性檢查通過")

    print(f"\n共 {len(ROWS)} 筆 historical_rulers")
    if args.dry:
        for r in ROWS:
            print(f"  [{r['sort_order']:>4}] {r['name_english']:<30} → {r['name_recommended']:<16}"
                  + f" @{r.get('polity') or ''}")
        sys.exit(0)

    if upsert(ROWS):
        print("\nDone.")
