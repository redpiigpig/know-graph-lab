"""
Seed the place_names table for /translation-glossary (「國名與城市」tab).

UNLIKE seed_translation_glossary.py, this is a HAND-CURATED master list — NO LLM.
譯名「確定」工作的本質是人工權威策展（聖經傳統優先、名根一致、台陸變體如實列），
不是 LLM 自填（使用者多次糾正過 LLM 亂猜）。所以這裡每筆都手工定。

定名原則（見 /translation-glossary 翻譯原則頁 + glossary_naming.py）：
  1. 按原文不按英文（希臘／拉丁／原民族語為準）
  2. 沿用良好古譯／既有意譯（聖經和合本/思高地名、通行史學譯名）
  3. 音意結合（亞歷山卓 > 亞歷山大城；馬爾堡 > 馬布爾）
  4. 名根一致 name_root（塞琉 → 塞琉古/塞琉西亞；凱撒/該撒；安提阿）
  其中聖經出現過的地名 → 以聖經傳統中譯為 name_recommended，史學/學界譯放 name_variants。
  現代國名 → 台灣（中華民國外交部）慣用為 name_recommended，大陸/港譯放 name_variants。

Usage:
  python scripts/seed_glossary_places.py            # upsert 全部（idempotent, on_conflict=name_english）
  python scripts/seed_glossary_places.py --dry      # 只印不寫
"""
from __future__ import annotations
import os, sys, io, json, argparse
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


def P(en, rec, *, o="", lang="", rom="", var="", reason="", root="",
      ptype="", modern="", mc="", region="", period="", notes=""):
    """Append one place_names row. en=name_english(key), rec=name_recommended(★)."""
    global _order
    _order += 10
    ROWS.append({
        "name_english": en,
        "name_original": o or None,
        "name_original_lang": lang or None,
        "name_romanized": rom or None,
        "name_recommended": rec,
        "name_variants": var or None,
        "recommendation_reason": reason or None,
        "name_root": root or None,
        "place_type": ptype or None,
        "modern_name": modern or None,
        "modern_country": mc or None,
        "region": region or None,
        "period": period or None,
        "notes": notes or None,
        "sort_order": _order,
    })


# ════════════════════════════════════════════════════════════════════════════
# BLOCK 1 — 古代近東帝國／政權  (sort 10–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1000
P("Sumer", "蘇美", o="𒆠𒂗𒂠", lang="sux", rom="Šumer", var="蘇美爾",
  ptype="政權", region="美索不達米亞", period="古代近東", root="蘇美",
  reason="兩河文明最早城邦群；台慣用「蘇美」，陸作「蘇美爾」")
P("Akkad", "阿卡德", o="𒀀𒂵𒉈𒆠", lang="akk", rom="Akkadu", var="亞甲",
  ptype="政權", region="美索不達米亞", period="古代近東", root="阿卡德",
  reason="薩爾貢帝國；聖經創十10作「亞甲」(Accad)，史學作「阿卡德」")
P("Assyria", "亞述", o="𒀸𒋩", lang="akk", rom="Aššur", var="",
  ptype="國名", region="美索不達米亞", period="古代近東", root="亞述",
  reason="聖經傳統定名（王下/賽/拿），史學亦同")
P("Babylonia", "巴比倫尼亞", o="𒆍𒀭𒊏𒆠", lang="akk", rom="Bābilim",
  var="巴比倫（王國）", ptype="國名", region="美索不達米亞", period="古代近東",
  root="巴比倫", reason="國名作巴比倫尼亞以別於城市巴比倫；聖經統稱巴比倫")
P("Chaldea", "迦勒底", o="", lang="", var="加爾底亞",
  ptype="地區", region="美索不達米亞", period="古代近東", root="迦勒底",
  reason="聖經傳統（創十一31「迦勒底的吾珥」），新巴比倫王朝核心")
P("Elam", "以攔", o="", lang="elx", var="埃蘭",
  ptype="國名", region="伊朗高原", period="古代近東", root="以攔",
  reason="聖經創十22作「以攔」；史學多作「埃蘭」")
P("Media", "瑪代", o="", lang="peo", var="米底亞；米底",
  ptype="國名", region="伊朗高原", period="古代近東", root="瑪代",
  reason="聖經但以理書「瑪代波斯」傳統；史學作米底亞")
P("Urartu", "烏拉爾圖", o="", lang="", var="亞拉臘（聖經）；烏拉圖",
  ptype="國名", region="高加索／安納托利亞", period="古代近東", root="烏拉",
  reason="聖經之「亞拉臘」(Ararat)即此；史學作烏拉爾圖")
P("Hittites", "西台", o="", lang="hit", var="赫梯；赫人（聖經「赫人」）",
  ptype="國名", region="安納托利亞", period="古代近東", root="西台",
  reason="台慣用「西台」，陸作「赫梯」；聖經人群作「赫人」")
P("Mitanni", "米坦尼", o="", lang="", var="米丹尼",
  ptype="國名", region="美索不達米亞北", period="古代近東", root="米坦尼")
P("Phoenicia", "腓尼基", o="Φοινίκη", lang="grc", rom="Phoinikē", var="",
  ptype="地區", region="黎凡特", period="古代近東", root="腓尼基",
  reason="聖經與史學一致")
P("Aram", "亞蘭", o="", lang="arc", var="阿拉姆",
  ptype="地區", region="黎凡特", period="古代近東", root="亞蘭",
  reason="聖經傳統（亞蘭＝大馬士革一帶）；語言作亞蘭語")
P("Israel (kingdom)", "以色列（北國）", o="יִשְׂרָאֵל", lang="heb",
  rom="Yisra'el", ptype="國名", region="黎凡特", period="古代近東",
  root="以色列", reason="聖經傳統定名")
P("Judah", "猶大（南國）", o="יְהוּדָה", lang="heb", rom="Yehudah",
  var="猶太（後期）", ptype="國名", region="黎凡特", period="古代近東",
  root="猶大", reason="聖經傳統；後期希臘化稱猶太(Judaea)")
P("Moab", "摩押", o="מוֹאָב", lang="heb", ptype="國名", region="黎凡特",
  period="古代近東", root="摩押", reason="聖經傳統")
P("Edom", "以東", o="אֱדוֹם", lang="heb", ptype="國名", region="黎凡特",
  period="古代近東", root="以東", reason="聖經傳統")
P("Ammon", "亞捫", o="עַמּוֹן", lang="heb", ptype="國名", region="黎凡特",
  period="古代近東", root="亞捫", reason="聖經傳統")
P("Nabataea", "納巴泰", o="", lang="", var="奈伯特；拿巴提",
  ptype="國名", region="阿拉伯／黎凡特", period="古典", root="納巴泰",
  reason="佩特拉為都的商業王國")
P("Saba (Sheba)", "示巴", o="", lang="", var="薩巴",
  ptype="國名", region="阿拉伯", period="古代近東", root="示巴",
  reason="聖經「示巴女王」傳統")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 2 — 古典波斯／希臘羅馬政權  (sort 1300–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1300
P("Achaemenid Empire", "阿契美尼德-波斯帝國", o="", lang="peo",
  var="波斯第一帝國；阿黑門尼德", ptype="帝國", region="伊朗高原",
  period="古典", root="阿契美尼德",
  reason="王朝-民族命名：阿契美尼德王朝＋波斯。居魯士創建")
P("Parthia", "安息帝國", o="", lang="xpr",
  var="帕提亞帝國；阿薩息斯王朝", ptype="帝國", region="伊朗高原",
  period="古典", root="安息",
  reason="中文古譯優先：《史記》「安息」源自王朝開創者 Aršak（阿薩息斯），較英文 Parthia 更貼近其自稱")
P("Sasanian Empire", "薩珊-波斯帝國", o="", lang="pal",
  var="薩珊波斯；薩桑；波斯第二帝國", ptype="帝國", region="伊朗高原",
  period="古典晚期", root="薩珊", reason="王朝-民族命名：薩珊王朝＋波斯")
P("Seleucid Empire", "塞琉古-希臘帝國", o="", lang="grc",
  var="塞琉古帝國；西流基王朝（聖經系）", ptype="帝國", region="敘利亞／兩河",
  period="希臘化", root="塞琉",
  reason="王朝-民族命名：塞琉古王朝＋希臘（希臘化馬其頓-希臘王朝）；名根「塞琉」一致")
P("Ptolemaic Kingdom", "托勒密-希臘王國", o="", lang="grc",
  var="托勒密王朝；托勒密埃及；多利買（聖經系）", ptype="王國", region="埃及",
  period="希臘化", root="托勒密",
  reason="王朝-民族命名：托勒密王朝＋希臘（希臘化馬其頓-希臘王朝，統治埃及）")
P("Macedon", "馬其頓", o="Μακεδονία", lang="grc", rom="Makedonia",
  ptype="國名", region="希臘北", period="古典", root="馬其頓",
  reason="聖經與史學一致")
P("Athens (polis)", "雅典", o="Ἀθῆναι", lang="grc", rom="Athēnai",
  ptype="城邦", modern="Athens", mc="希臘", region="希臘", period="古典",
  root="雅典", reason="聖經徒十七亦作雅典")
P("Sparta", "斯巴達", o="Σπάρτη", lang="grc", rom="Spartē", var="拉刻代蒙",
  ptype="城邦", region="希臘", period="古典", root="斯巴達")
P("Roman Republic", "羅馬共和", o="", lang="lat", ptype="政權",
  region="義大利", period="古典", root="羅馬")
P("Roman Empire", "羅馬帝國", o="Imperium Romanum", lang="lat",
  ptype="帝國", region="地中海", period="古典", root="羅馬",
  reason="聖經與史學一致")
P("Byzantine Empire", "拜占庭帝國", o="", lang="grc",
  var="東羅馬帝國", ptype="帝國", region="地中海東", period="中世紀",
  root="拜占庭", reason="以君士坦丁堡為都的東羅馬")
P("Carthage (state)", "迦太基", o="", lang="phn", var="",
  ptype="政權", region="北非", period="古典", root="迦太基",
  reason="布匿戰爭對手；同名城市見城市區")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 3 — 中世紀／近代帝國  (sort 1600–)
# ════════════════════════════════════════════════════════════════════════════
_order = 1600
P("Holy Roman Empire", "神聖羅馬帝國", o="Sacrum Romanum Imperium",
  lang="lat", ptype="帝國", region="中歐", period="中世紀", root="羅馬")
P("Frankish Kingdom", "法蘭克王國", o="", lang="lat", var="法蘭克",
  ptype="國名", region="西歐", period="中世紀", root="法蘭克")
P("Umayyad Caliphate", "伍麥亞-阿拉伯帝國", o="", lang="ar",
  var="伍麥亞王朝；奧米亞；倭馬亞（陸）", ptype="哈里發國", region="中東",
  period="中世紀", root="伍麥亞", reason="王朝-民族命名：伍麥亞王朝＋阿拉伯")
P("Abbasid Caliphate", "阿拔斯-阿拉伯帝國", o="", lang="ar",
  var="阿拔斯王朝；阿巴斯", ptype="哈里發國", region="中東", period="中世紀",
  root="阿拔斯", reason="王朝-民族命名：阿拔斯王朝＋阿拉伯")
P("Fatimid Caliphate", "法蒂瑪-阿拉伯帝國", o="", lang="ar",
  var="法蒂瑪王朝；法提瑪", ptype="哈里發國", region="北非／埃及",
  period="中世紀", root="法蒂瑪", reason="王朝-民族命名：法蒂瑪王朝＋阿拉伯（伊斯瑪儀派）")
P("Ottoman Empire", "鄂圖曼-土耳其帝國", o="", lang="ota",
  var="鄂圖曼帝國；奧斯曼帝國（陸）", ptype="帝國", region="中東／巴爾幹",
  period="近代", root="鄂圖曼", reason="王朝-民族命名：鄂圖曼王朝＋土耳其；陸作「奧斯曼」")
P("Safavid Empire", "薩法維-波斯帝國", o="", lang="fa",
  var="薩法維波斯；薩非；沙法維", ptype="帝國", region="伊朗高原",
  period="近代", root="薩法維", reason="王朝-民族命名：薩法維王朝＋波斯")
P("Mughal Empire", "蒙兀兒-印度帝國", o="", lang="fa",
  var="蒙兀兒帝國；莫臥兒（陸）", ptype="帝國", region="南亞", period="近代",
  root="蒙兀兒", reason="王朝-民族命名：蒙兀兒王朝＋印度；陸作「莫臥兒」")
P("Carolingian Empire", "卡洛林-法蘭克帝國", o="", lang="lat",
  var="查理曼帝國；加洛林帝國", ptype="帝國", region="西歐", period="中世紀",
  root="卡洛林",
  reason="王朝-民族命名：卡洛林王朝＋法蘭克。非單一人物（查理‧馬特→丕平→查理曼→虔誠者路易），故不用「查理曼帝國」")
P("Mongol Empire", "蒙古帝國", o="", lang="mn", ptype="帝國",
  region="歐亞草原", period="中世紀", root="蒙古",
  reason="民族即國名，無另立王朝名（孛兒只斤為氏族），故單稱蒙古帝國")
P("Kievan Rus'", "基輔羅斯", o="", lang="orv", ptype="政權",
  region="東歐", period="中世紀", root="羅斯")
# ── 單一人物建立的帝國 → 例外：直接用人名，不加王朝-民族 ──────────────────
P("Empire of Alexander the Great", "亞歷山大帝國", o="", lang="grc",
  var="馬其頓帝國（廣義）", ptype="帝國", region="希臘—近東", period="希臘化",
  root="亞歷山",
  reason="單一人物例外：亞歷山大一人所建，逝後即分裂為繼業者諸國，故用人名；名根「亞歷山」一致（亞歷山卓）")
P("Timurid Empire", "帖木兒帝國", o="", lang="fa", var="帖木兒王朝（廣義）",
  ptype="帝國", region="中亞／波斯", period="中世紀晚期", root="帖木兒",
  reason="單一人物例外：以征服者帖木兒為名")
P("First French Empire", "拿破崙帝國", o="Premier Empire", lang="fr",
  var="法蘭西第一帝國", ptype="帝國", region="西歐", period="近代", root="拿破崙",
  reason="單一人物例外：拿破崙一世所建，史稱法蘭西第一帝國，慣以人名指稱")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 4 — 古代地區／行省／地理區  (sort 2000–)
# ════════════════════════════════════════════════════════════════════════════
_order = 2000
P("Mesopotamia", "美索不達米亞", o="Μεσοποταμία", lang="grc",
  rom="Mesopotamia", var="兩河流域", ptype="地區", region="近東",
  period="通用", root="美索不達米亞", reason="希臘文「兩河之間」；意譯「兩河流域」並用")
P("Levant", "黎凡特", o="", lang="", var="累范特", ptype="地區",
  region="地中海東", period="通用", root="黎凡特")
P("Canaan", "迦南", o="כְּנַעַן", lang="heb", rom="Kena'an",
  ptype="地區", region="黎凡特", period="古代近東", root="迦南",
  reason="聖經傳統")
P("Palestine", "巴勒斯坦", o="Παλαιστίνη", lang="grc", var="巴力斯坦",
  ptype="地區", region="黎凡特", period="通用", root="巴勒斯坦")
P("Judaea", "猶太", o="Ἰουδαία", lang="grc", rom="Ioudaia",
  ptype="行省", modern="", mc="以色列／巴勒斯坦", region="黎凡特",
  period="古典", root="猶太", reason="羅馬行省，聖經作「猶太地」；與王國「猶大」(Judah) 中譯傳統分流")
P("Galilee", "加利利", o="Γαλιλαία", lang="grc", rom="Galilaia",
  ptype="地區", region="黎凡特", period="古典", root="加利利",
  reason="聖經傳統")
P("Samaria (region)", "撒馬利亞", o="Σαμάρεια", lang="grc",
  var="撒瑪利亞（和合本）", ptype="地區", region="黎凡特", period="古典",
  root="撒馬利亞", reason="和合本作「撒瑪利亞」")
P("Asia Minor", "小亞細亞", o="", lang="", var="安納托利亞",
  ptype="地區", region="安納托利亞", period="通用", root="亞細亞",
  reason="今安納托利亞半島")
P("Anatolia", "安納托利亞", o="Ἀνατολή", lang="grc", var="安那托利亞",
  ptype="地區", region="安納托利亞", period="通用", root="安納托利亞")
P("Cappadocia", "加帕多家", o="Καππαδοκία", lang="grc", rom="Kappadokia",
  var="卡帕多奇亞；卡帕多細亞", ptype="地區／行省", region="安納托利亞",
  period="古典", root="加帕多家", reason="聖經彼前一1作「加帕多家」；加帕多家三傑")
P("Phrygia", "弗呂家", o="Φρυγία", lang="grc", var="弗里吉亞",
  ptype="地區", region="安納托利亞", period="古典", root="弗呂家",
  reason="聖經徒二10作「弗呂家」")
P("Galatia", "加拉太", o="Γαλατία", lang="grc", ptype="行省",
  region="安納托利亞", period="古典", root="加拉太", reason="聖經書卷名")
P("Bithynia", "庇推尼", o="Βιθυνία", lang="grc", var="比提尼亞",
  ptype="行省", region="安納托利亞", period="古典", root="庇推尼",
  reason="聖經徒十六7作「庇推尼」")
P("Pontus", "本都", o="Πόντος", lang="grc", var="龐圖斯",
  ptype="地區／王國", region="安納托利亞", period="古典", root="本都",
  reason="聖經彼前一1作「本都」")
P("Cilicia", "基利家", o="Κιλικία", lang="grc", var="奇里乞亞",
  ptype="行省", region="安納托利亞", period="古典", root="基利家",
  reason="聖經（保羅家鄉大數所在）作「基利家」")
P("Lydia (region)", "呂底亞", o="Λυδία", lang="grc", var="利底亞",
  ptype="地區／王國", region="安納托利亞", period="古典", root="呂底亞")
P("Ionia", "愛奧尼亞", o="Ἰωνία", lang="grc", var="伊奧尼亞",
  ptype="地區", region="安納托利亞", period="古典", root="愛奧尼亞")
P("Thrace", "色雷斯", o="Θρᾴκη", lang="grc", var="特拉基亞",
  ptype="地區", region="巴爾幹", period="古典", root="色雷斯")
P("Macedonia (province)", "馬其頓", o="Μακεδονία", lang="grc",
  ptype="行省", region="希臘北", period="古典", root="馬其頓")
P("Achaia", "亞該亞", o="Ἀχαΐα", lang="grc", var="阿哈伊亞",
  ptype="行省", region="希臘", period="古典", root="亞該亞",
  reason="聖經羅馬行省名作「亞該亞」")
P("Illyricum", "以利哩古", o="Ἰλλυρικόν", lang="grc", var="伊利里庫姆",
  ptype="行省", region="巴爾幹", period="古典", root="以利哩古",
  reason="聖經羅十五19作「以利哩古」")
P("Dalmatia", "撻馬太", o="Δαλματία", lang="grc", var="達爾馬提亞",
  ptype="地區", region="巴爾幹", period="古典", root="撻馬太",
  reason="聖經提後四10作「撻馬太」")
P("Gaul", "高盧", o="Gallia", lang="lat", ptype="地區",
  region="西歐", period="古典", root="高盧")
P("Hispania", "希斯帕尼亞", o="Hispania", lang="lat", var="西班尼亞",
  ptype="地區", region="伊比利", period="古典", root="希斯帕尼亞",
  reason="羅馬之伊比利半島")
P("Britannia", "不列顛尼亞", o="Britannia", lang="lat", var="布列塔尼亞",
  ptype="行省", region="不列顛", period="古典", root="不列顛")
P("Numidia", "努米底亞", o="", lang="lat", var="奴米底亞",
  ptype="地區", region="北非", period="古典", root="努米底亞")
P("Arabia", "阿拉伯", o="Ἀραβία", lang="grc", ptype="地區",
  region="阿拉伯", period="通用", root="阿拉伯")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 5 — 兩河／波斯重要城市  (sort 3000–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3000
P("Babylon", "巴比倫", o="𒆍𒀭𒊏𒆠", lang="akk", rom="Bābilim",
  ptype="城市", modern="Hillah 附近", mc="伊拉克", region="美索不達米亞",
  period="古代近東", root="巴比倫", reason="聖經傳統")
P("Nineveh", "尼尼微", o="", lang="akk", var="尼尼微",
  ptype="城市", modern="Mosul", mc="伊拉克", region="美索不達米亞",
  period="古代近東", root="尼尼微", reason="聖經（約拿書）傳統")
P("Ur", "吾珥", o="", lang="sux", var="烏爾",
  ptype="城市", modern="Tell el-Muqayyar", mc="伊拉克", region="美索不達米亞",
  period="古代近東", root="吾珥", reason="聖經「迦勒底的吾珥」(創十一31)")
P("Uruk", "烏魯克", o="𒌷𒀕", lang="sux", var="以力（聖經創十10）",
  ptype="城市", mc="伊拉克", region="美索不達米亞", period="古代近東",
  root="烏魯克")
P("Nippur", "尼普爾", o="", lang="sux", ptype="城市", mc="伊拉克",
  region="美索不達米亞", period="古代近東", root="尼普爾")
P("Susa", "書珊", o="", lang="elx", var="蘇薩",
  ptype="城市", modern="Shush", mc="伊朗", region="伊朗高原",
  period="古代近東", root="書珊", reason="聖經（以斯帖記/但以理）作「書珊」")
P("Persepolis", "波斯波利斯", o="Περσέπολις", lang="grc",
  var="帕賽波利斯", ptype="城市", mc="伊朗", region="伊朗高原",
  period="古典", root="波斯", reason="阿契美尼德禮儀首都")
P("Ecbatana", "亞馬他", o="Ἀγβάτανα", lang="grc", var="埃克巴坦那",
  ptype="城市", modern="Hamadan", mc="伊朗", region="伊朗高原",
  period="古典", root="亞馬他", reason="聖經拉六2作「亞馬他」；史學作埃克巴坦那")
P("Ctesiphon", "泰西封", o="Κτησιφῶν", lang="grc", rom="Ktesiphon",
  ptype="城市", modern="Salman Pak", mc="伊拉克", region="美索不達米亞",
  period="古典", reason="帕提亞／薩珊首都；與塞琉西亞並稱塞琉西亞-泰西封")
P("Seleucia", "塞琉西亞", o="Σελεύκεια", lang="grc", rom="Seleukeia",
  var="西流基", ptype="城市", modern="Ctesiphon 附近", mc="伊拉克",
  region="美索不達米亞", period="古典", root="塞琉",
  reason="塞琉古系城名，名根「塞琉」須一致")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 6 — 黎凡特／聖經重要城市  (sort 3300–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3300
P("Jerusalem", "耶路撒冷", o="יְרוּשָׁלַ͏ִם", lang="heb", rom="Yerushalayim",
  var="耶路撒冷；Aelia Capitolina(羅馬)", ptype="城市", mc="以色列／巴勒斯坦",
  region="黎凡特", period="通用", root="耶路撒冷", reason="聖經傳統")
P("Damascus", "大馬士革", o="דַּמֶּשֶׂק", lang="heb", var="大馬色（部分譯本）",
  ptype="城市", mc="敘利亞", region="黎凡特", period="通用", root="大馬士革",
  reason="聖經傳統")
P("Antioch", "安提阿", o="Ἀντιόχεια", lang="grc", rom="Antiocheia",
  var="安條克（史學）", ptype="城市", modern="Antakya", mc="土耳其",
  region="黎凡特", period="古典", root="安提阿",
  reason="聖經（門徒初稱基督徒之地，徒十一26）作「安提阿」；史學作「安條克」")
P("Tyre", "推羅", o="צֹר", lang="heb", var="泰爾；提爾",
  ptype="城市", mc="黎巴嫩", region="黎凡特", period="古代近東", root="推羅",
  reason="聖經傳統（腓尼基港市）")
P("Sidon", "西頓", o="צִידוֹן", lang="heb", var="賽達",
  ptype="城市", mc="黎巴嫩", region="黎凡特", period="古代近東", root="西頓",
  reason="聖經傳統")
P("Caesarea Maritima", "凱撒利亞", o="Καισάρεια", lang="grc",
  var="該撒利亞（和合本）", ptype="城市", mc="以色列", region="黎凡特",
  period="古典", root="凱撒", reason="聖經作「該撒利亞」；羅馬猶太行省治所")
P("Caesarea Philippi", "凱撒利亞腓立比", o="Καισάρεια Φιλίππου",
  lang="grc", var="該撒利亞腓立比（和合本）", ptype="城市", mc="以色列",
  region="黎凡特", period="古典", root="凱撒", reason="聖經太十六13")
P("Bethlehem", "伯利恆", o="בֵּית לֶחֶם", lang="heb", rom="Beit Leḥem",
  ptype="城市", mc="巴勒斯坦", region="黎凡特", period="通用", root="伯利恆",
  reason="聖經傳統")
P("Nazareth", "拿撒勒", o="Ναζαρέθ", lang="grc", ptype="城市",
  mc="以色列", region="黎凡特", period="古典", root="拿撒勒",
  reason="聖經傳統")
P("Capernaum", "迦百農", o="Καφαρναούμ", lang="grc", ptype="城市",
  mc="以色列", region="黎凡特", period="古典", root="迦百農",
  reason="聖經傳統")
P("Jericho", "耶利哥", o="יְרִיחוֹ", lang="heb", ptype="城市",
  mc="巴勒斯坦", region="黎凡特", period="古代近東", root="耶利哥",
  reason="聖經傳統")
P("Joppa", "約帕", o="יָפוֹ", lang="heb", var="雅法(Jaffa)",
  ptype="城市", modern="Jaffa", mc="以色列", region="黎凡特",
  period="通用", root="約帕", reason="聖經作「約帕」；今特拉維夫-雅法")
P("Petra", "佩特拉", o="Πέτρα", lang="grc", var="彼特拉",
  ptype="城市", mc="約旦", region="黎凡特", period="古典", root="佩特拉",
  reason="納巴泰首都")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 7 — 埃及／北非重要城市  (sort 3600–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3600
P("Alexandria", "亞歷山卓", o="Ἀλεξάνδρεια", lang="grc", rom="Alexandreia",
  var="亞歷山大城；亞歷山大里亞", ptype="城市", modern="Alexandria",
  mc="埃及", region="埃及", period="古典", root="亞歷山",
  reason="音意結合：保留亞歷山根＋卓字較「大城」典雅達意")
P("Memphis", "孟斐斯", o="Μέμφις", lang="grc", var="挪弗（聖經）",
  ptype="城市", mc="埃及", region="埃及", period="古代近東", root="孟斐斯",
  reason="聖經作「挪弗」(耶四十六14)；史學作孟斐斯")
P("Thebes (Egypt)", "底比斯", o="Θῆβαι", lang="grc", var="挪亞們（聖經）",
  ptype="城市", modern="Luxor", mc="埃及", region="埃及", period="古代近東",
  root="底比斯", reason="聖經作「挪亞們」(鴻三8)；今路克索")
P("Carthage", "迦太基", o="Carthago", lang="lat", ptype="城市",
  modern="Tunis 近郊", mc="突尼西亞", region="北非", period="古典",
  root="迦太基", reason="教父居普良、特土良、奧古斯丁活動地")
P("Hippo Regius", "希波", o="Hippo Regius", lang="lat", var="希波雷吉烏斯",
  ptype="城市", modern="Annaba", mc="阿爾及利亞", region="北非",
  period="古典", root="希波", reason="奧古斯丁主教座；定名「希波的奧古斯丁」")
P("Cyrene", "古利奈", o="Κυρήνη", lang="grc", var="昔蘭尼",
  ptype="城市", mc="利比亞", region="北非", period="古典", root="古利奈",
  reason="聖經作「古利奈人西門」(可十五21)；史學作昔蘭尼")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 8 — 希臘／小亞細亞／愛琴海城市  (sort 3900–)
# ════════════════════════════════════════════════════════════════════════════
_order = 3900
P("Corinth", "哥林多", o="Κόρινθος", lang="grc", var="科林斯",
  ptype="城市", mc="希臘", region="希臘", period="古典", root="哥林多",
  reason="聖經書卷名作「哥林多」；史學作科林斯")
P("Ephesus", "以弗所", o="Ἔφεσος", lang="grc", var="艾菲索斯",
  ptype="城市", mc="土耳其", region="安納托利亞", period="古典", root="以弗所",
  reason="聖經書卷名")
P("Thessalonica", "帖撒羅尼迦", o="Θεσσαλονίκη", lang="grc",
  var="塞薩洛尼基", ptype="城市", modern="Thessaloniki", mc="希臘",
  region="希臘", period="古典", root="帖撒羅尼迦", reason="聖經書卷名")
P("Philippi", "腓立比", o="Φίλιπποι", lang="grc", var="菲利皮",
  ptype="城市", mc="希臘", region="希臘", period="古典", root="腓立比",
  reason="聖經書卷名")
P("Smyrna", "士每拿", o="Σμύρνα", lang="grc", var="士麥那",
  ptype="城市", modern="İzmir", mc="土耳其", region="安納托利亞",
  period="古典", root="士每拿", reason="啟示錄七教會之一；坡旅甲主教座")
P("Pergamon", "別迦摩", o="Πέργαμον", lang="grc", var="帕加馬；佩加蒙",
  ptype="城市", mc="土耳其", region="安納托利亞", period="古典", root="別迦摩",
  reason="聖經（啟二12）作「別迦摩」")
P("Sardis", "撒狄", o="Σάρδεις", lang="grc", var="薩第斯",
  ptype="城市", mc="土耳其", region="安納托利亞", period="古典", root="撒狄",
  reason="啟示錄七教會之一")
P("Laodicea", "老底嘉", o="Λαοδίκεια", lang="grc", var="拉俄狄刻亞",
  ptype="城市", mc="土耳其", region="安納托利亞", period="古典", root="老底嘉",
  reason="啟示錄七教會之一")
P("Tarsus", "大數", o="Ταρσός", lang="grc", var="塔爾蘇斯",
  ptype="城市", mc="土耳其", region="安納托利亞", period="古典", root="大數",
  reason="保羅家鄉，聖經作「大數」")
P("Miletus", "米利都", o="Μίλητος", lang="grc", var="米利特斯",
  ptype="城市", mc="土耳其", region="安納托利亞", period="古典", root="米利都",
  reason="聖經徒二十15")
P("Nicaea", "尼西亞", o="Νίκαια", lang="grc", var="尼凱亞",
  ptype="城市", modern="İznik", mc="土耳其", region="安納托利亞",
  period="古典", root="尼西亞", reason="第一、七次大公會議地；信經名")
P("Chalcedon", "迦克墩", o="Χαλκηδών", lang="grc", var="卡爾西頓",
  ptype="城市", modern="Kadıköy", mc="土耳其", region="安納托利亞",
  period="古典", root="迦克墩", reason="451 年大公會議地；定名「迦克墩信經」")
P("Constantinople", "君士坦丁堡", o="Κωνσταντινούπολις", lang="grc",
  var="伊斯坦堡(今名)；拜占庭(舊名)", ptype="城市", modern="Istanbul",
  mc="土耳其", region="安納托利亞", period="古典—中世紀", root="君士坦丁",
  reason="新羅馬，東方牧首座")
P("Athens", "雅典", o="Ἀθῆναι", lang="grc", rom="Athēnai",
  ptype="城市", mc="希臘", region="希臘", period="通用", root="雅典")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 9 — 義大利／西方教會史城市  (sort 4200–)
# ════════════════════════════════════════════════════════════════════════════
_order = 4200
P("Rome", "羅馬", o="Roma", lang="lat", ptype="城市", mc="義大利",
  region="義大利", period="通用", root="羅馬", reason="聖經與史學一致")
P("Milan", "米蘭", o="Mediolanum", lang="lat", var="梅迪奧拉努姆(古名)",
  ptype="城市", mc="義大利", region="義大利", period="通用", root="米蘭",
  reason="安波羅修主教座；米蘭敕令")
P("Ravenna", "拉溫納", o="Ravenna", lang="lat", var="拉文納",
  ptype="城市", mc="義大利", region="義大利", period="古典晚期", root="拉溫納",
  reason="西羅馬末期首都")
P("Aquileia", "阿奎萊亞", o="Aquileia", lang="lat", var="阿奎利亞",
  ptype="城市", mc="義大利", region="義大利", period="古典", root="阿奎萊亞")
P("Hippo", "希波", o="Hippo", lang="lat", ptype="城市",
  mc="阿爾及利亞", region="北非", period="古典", root="希波",
  notes="同 Hippo Regius，見北非區")
P("Lyon", "里昂", o="Lugdunum", lang="lat", var="盧格杜努姆(古名)",
  ptype="城市", mc="法國", region="高盧", period="通用", root="里昂",
  reason="愛任紐主教座")
P("Carthage (city)", "迦太基", o="Carthago", lang="lat", ptype="城市",
  mc="突尼西亞", region="北非", period="古典", root="迦太基",
  notes="見北非城市區同名條")
P("Trier", "特里爾", o="Augusta Treverorum", lang="lat", var="奧古斯塔‧特列維羅倫(古名)",
  ptype="城市", mc="德國", region="高盧", period="古典", root="特里爾")
P("Marburg", "馬爾堡", o="Marburg", lang="de", var="馬布爾",
  ptype="城市", modern="Marburg", mc="德國", region="中歐", period="近代",
  root="馬爾", reason="-burg 作「堡」意譯，優於純音譯「布爾」；馬爾堡會談")
P("Wittenberg", "威登堡", o="Wittenberg", lang="de", var="維滕貝格",
  ptype="城市", mc="德國", region="中歐", period="近代", root="威登堡",
  reason="路德張貼九十五條地")
P("Geneva", "日內瓦", o="Genève", lang="fr", var="日內瓦",
  ptype="城市", mc="瑞士", region="中歐", period="近代", root="日內瓦",
  reason="加爾文改教中心")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 10 — 現代國家：東亞・東南亞・南亞  (sort 5000–)
#   name_recommended = 台灣慣用（繁體）；name_variants = 大陸/港譯（若不同）
# ════════════════════════════════════════════════════════════════════════════
_order = 5000
P("Japan", "日本", ptype="國名", region="東亞", period="現代", root="日本")
P("South Korea", "韓國", var="南韓；大韓民國", ptype="國名", region="東亞",
  period="現代", root="韓")
P("North Korea", "北韓", var="朝鮮（陸）", ptype="國名", region="東亞",
  period="現代", root="韓", reason="台作北韓，陸作朝鮮")
P("Mongolia", "蒙古", ptype="國名", region="東亞", period="現代", root="蒙古")
P("China", "中國", var="中華人民共和國", ptype="國名", region="東亞",
  period="現代", root="中")
P("Vietnam", "越南", ptype="國名", region="東南亞", period="現代", root="越南")
P("Thailand", "泰國", ptype="國名", region="東南亞", period="現代", root="泰")
P("Laos", "寮國", var="老撾（陸）", ptype="國名", region="東南亞",
  period="現代", root="寮", reason="台作寮國，陸作老撾")
P("Cambodia", "柬埔寨", ptype="國名", region="東南亞", period="現代", root="柬")
P("Myanmar", "緬甸", var="Burma 舊稱", ptype="國名", region="東南亞",
  period="現代", root="緬甸")
P("Malaysia", "馬來西亞", ptype="國名", region="東南亞", period="現代", root="馬來")
P("Singapore", "新加坡", var="星加坡", ptype="國名", region="東南亞",
  period="現代", root="新加坡")
P("Indonesia", "印尼", var="印度尼西亞", ptype="國名", region="東南亞",
  period="現代", root="印尼")
P("Philippines", "菲律賓", ptype="國名", region="東南亞", period="現代", root="菲")
P("Brunei", "汶萊", var="文萊（陸）", ptype="國名", region="東南亞",
  period="現代", root="汶萊")
P("East Timor", "東帝汶", ptype="國名", region="東南亞", period="現代", root="帝汶")
P("India", "印度", ptype="國名", region="南亞", period="現代", root="印度")
P("Pakistan", "巴基斯坦", ptype="國名", region="南亞", period="現代", root="巴基斯坦")
P("Bangladesh", "孟加拉", var="孟加拉國", ptype="國名", region="南亞",
  period="現代", root="孟加拉")
P("Sri Lanka", "斯里蘭卡", var="錫蘭(舊稱)", ptype="國名", region="南亞",
  period="現代", root="斯里蘭卡")
P("Nepal", "尼泊爾", ptype="國名", region="南亞", period="現代", root="尼泊爾")
P("Bhutan", "不丹", ptype="國名", region="南亞", period="現代", root="不丹")
P("Maldives", "馬爾地夫", var="馬爾代夫（陸）", ptype="國名", region="南亞",
  period="現代", root="馬爾", reason="台作馬爾地夫，陸作馬爾代夫")
P("Afghanistan", "阿富汗", ptype="國名", region="中亞／南亞", period="現代", root="阿富汗")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 11 — 現代國家：中亞・中東  (sort 5400–)
# ════════════════════════════════════════════════════════════════════════════
_order = 5400
P("Kazakhstan", "哈薩克", var="哈薩克斯坦（陸）", ptype="國名", region="中亞",
  period="現代", root="哈薩克", reason="台略去「斯坦」，陸保留")
P("Uzbekistan", "烏茲別克", var="烏茲別克斯坦（陸）", ptype="國名", region="中亞",
  period="現代", root="烏茲別克")
P("Turkmenistan", "土庫曼", var="土庫曼斯坦（陸）", ptype="國名", region="中亞",
  period="現代", root="土庫曼")
P("Kyrgyzstan", "吉爾吉斯", var="吉爾吉斯斯坦（陸）", ptype="國名", region="中亞",
  period="現代", root="吉爾吉斯")
P("Tajikistan", "塔吉克", var="塔吉克斯坦（陸）", ptype="國名", region="中亞",
  period="現代", root="塔吉克")
P("Turkey", "土耳其", ptype="國名", region="中東／安納托利亞", period="現代", root="土耳其")
P("Iran", "伊朗", var="波斯(舊稱)", ptype="國名", region="中東", period="現代", root="伊朗")
P("Iraq", "伊拉克", ptype="國名", region="中東", period="現代", root="伊拉克")
P("Syria", "敘利亞", ptype="國名", region="中東", period="現代", root="敘利亞")
P("Lebanon", "黎巴嫩", ptype="國名", region="中東", period="現代", root="黎巴嫩")
P("Israel", "以色列", ptype="國名", region="中東", period="現代", root="以色列")
P("Jordan", "約旦", ptype="國名", region="中東", period="現代", root="約旦")
P("Saudi Arabia", "沙烏地阿拉伯", var="沙特阿拉伯（陸）", ptype="國名",
  region="中東", period="現代", root="沙烏地", reason="台作沙烏地，陸作沙特")
P("Yemen", "葉門", var="也門（陸）", ptype="國名", region="中東", period="現代",
  root="葉門", reason="台作葉門，陸作也門")
P("Oman", "阿曼", ptype="國名", region="中東", period="現代", root="阿曼")
P("United Arab Emirates", "阿拉伯聯合大公國", var="阿拉伯聯合酋長國（陸）；阿聯",
  ptype="國名", region="中東", period="現代", root="阿拉伯聯合")
P("Qatar", "卡達", var="卡塔爾（陸）", ptype="國名", region="中東", period="現代",
  root="卡達")
P("Bahrain", "巴林", ptype="國名", region="中東", period="現代", root="巴林")
P("Kuwait", "科威特", ptype="國名", region="中東", period="現代", root="科威特")
P("Azerbaijan", "亞塞拜然", var="阿塞拜疆（陸）", ptype="國名", region="高加索",
  period="現代", root="亞塞拜然")
P("Armenia", "亞美尼亞", ptype="國名", region="高加索", period="現代", root="亞美尼亞")
P("Georgia", "喬治亞", var="格魯吉亞（陸）", ptype="國名", region="高加索",
  period="現代", root="喬治亞", reason="台作喬治亞，陸作格魯吉亞")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 12 — 現代國家：歐洲  (sort 5800–)
# ════════════════════════════════════════════════════════════════════════════
_order = 5800
P("United Kingdom", "英國", var="聯合王國", ptype="國名", region="西歐",
  period="現代", root="英")
P("Ireland", "愛爾蘭", ptype="國名", region="西歐", period="現代", root="愛爾蘭")
P("France", "法國", ptype="國名", region="西歐", period="現代", root="法")
P("Germany", "德國", var="德意志", ptype="國名", region="中歐", period="現代", root="德")
P("Netherlands", "荷蘭", var="尼德蘭", ptype="國名", region="西歐", period="現代", root="荷")
P("Belgium", "比利時", ptype="國名", region="西歐", period="現代", root="比")
P("Luxembourg", "盧森堡", ptype="國名", region="西歐", period="現代", root="盧森堡")
P("Switzerland", "瑞士", ptype="國名", region="中歐", period="現代", root="瑞士")
P("Austria", "奧地利", ptype="國名", region="中歐", period="現代", root="奧")
P("Spain", "西班牙", ptype="國名", region="西歐", period="現代", root="西班牙")
P("Portugal", "葡萄牙", ptype="國名", region="西歐", period="現代", root="葡")
P("Italy", "義大利", var="意大利（陸／港）", ptype="國名", region="南歐",
  period="現代", root="義", reason="台作義大利，陸港作意大利")
P("Greece", "希臘", ptype="國名", region="南歐", period="現代", root="希臘")
P("Denmark", "丹麥", ptype="國名", region="北歐", period="現代", root="丹麥")
P("Norway", "挪威", ptype="國名", region="北歐", period="現代", root="挪威")
P("Sweden", "瑞典", ptype="國名", region="北歐", period="現代", root="瑞典")
P("Finland", "芬蘭", ptype="國名", region="北歐", period="現代", root="芬蘭")
P("Iceland", "冰島", ptype="國名", region="北歐", period="現代", root="冰島")
P("Poland", "波蘭", ptype="國名", region="中歐", period="現代", root="波蘭")
P("Czechia", "捷克", var="捷克共和國", ptype="國名", region="中歐", period="現代", root="捷克")
P("Slovakia", "斯洛伐克", ptype="國名", region="中歐", period="現代", root="斯洛伐克")
P("Hungary", "匈牙利", ptype="國名", region="中歐", period="現代", root="匈")
P("Romania", "羅馬尼亞", ptype="國名", region="東歐", period="現代", root="羅馬尼亞")
P("Bulgaria", "保加利亞", ptype="國名", region="東歐", period="現代", root="保加利亞")
P("Croatia", "克羅埃西亞", var="克羅地亞（陸）", ptype="國名", region="巴爾幹",
  period="現代", root="克羅", reason="台作克羅埃西亞，陸作克羅地亞")
P("Slovenia", "斯洛維尼亞", var="斯洛文尼亞（陸）", ptype="國名", region="巴爾幹",
  period="現代", root="斯洛維尼亞")
P("Serbia", "塞爾維亞", ptype="國名", region="巴爾幹", period="現代", root="塞爾維亞")
P("Bosnia and Herzegovina", "波士尼亞與赫塞哥維納", var="波斯尼亞和黑塞哥維那（陸）",
  ptype="國名", region="巴爾幹", period="現代", root="波士尼亞")
P("Montenegro", "蒙特內哥羅", var="黑山（陸，意譯）", ptype="國名", region="巴爾幹",
  period="現代", root="蒙特內哥羅", reason="台音譯，陸意譯「黑山」")
P("North Macedonia", "北馬其頓", ptype="國名", region="巴爾幹", period="現代", root="馬其頓")
P("Albania", "阿爾巴尼亞", ptype="國名", region="巴爾幹", period="現代", root="阿爾巴尼亞")
P("Kosovo", "科索沃", ptype="國名", region="巴爾幹", period="現代", root="科索沃")
P("Ukraine", "烏克蘭", ptype="國名", region="東歐", period="現代", root="烏克蘭")
P("Belarus", "白俄羅斯", ptype="國名", region="東歐", period="現代", root="白俄")
P("Moldova", "摩爾多瓦", ptype="國名", region="東歐", period="現代", root="摩爾多瓦")
P("Lithuania", "立陶宛", ptype="國名", region="波羅的海", period="現代", root="立陶宛")
P("Latvia", "拉脫維亞", ptype="國名", region="波羅的海", period="現代", root="拉脫維亞")
P("Estonia", "愛沙尼亞", ptype="國名", region="波羅的海", period="現代", root="愛沙尼亞")
P("Russia", "俄羅斯", var="俄國", ptype="國名", region="歐亞", period="現代", root="俄")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 13 — 現代國家：非洲  (sort 6300–)
# ════════════════════════════════════════════════════════════════════════════
_order = 6300
P("Egypt", "埃及", ptype="國名", region="北非", period="現代", root="埃及")
P("Libya", "利比亞", ptype="國名", region="北非", period="現代", root="利比亞")
P("Tunisia", "突尼西亞", var="突尼斯（陸；與首都同名）", ptype="國名",
  region="北非", period="現代", root="突尼", reason="台國名作突尼西亞別於首都突尼斯")
P("Algeria", "阿爾及利亞", ptype="國名", region="北非", period="現代", root="阿爾及利亞")
P("Morocco", "摩洛哥", ptype="國名", region="北非", period="現代", root="摩洛哥")
P("Sudan", "蘇丹", ptype="國名", region="東非", period="現代", root="蘇丹")
P("South Sudan", "南蘇丹", ptype="國名", region="東非", period="現代", root="蘇丹")
P("Ethiopia", "衣索比亞", var="埃塞俄比亞（陸）", ptype="國名", region="東非",
  period="現代", root="衣索", reason="台作衣索比亞，陸作埃塞俄比亞")
P("Eritrea", "厄利垂亞", var="厄立特里亞（陸）", ptype="國名", region="東非",
  period="現代", root="厄利")
P("Somalia", "索馬利亞", var="索馬里（陸）", ptype="國名", region="東非",
  period="現代", root="索馬")
P("Djibouti", "吉布地", var="吉布提（陸）", ptype="國名", region="東非",
  period="現代", root="吉布")
P("Kenya", "肯亞", var="肯尼亞（陸）", ptype="國名", region="東非", period="現代",
  root="肯", reason="台作肯亞，陸作肯尼亞")
P("Tanzania", "坦尚尼亞", var="坦桑尼亞（陸）", ptype="國名", region="東非",
  period="現代", root="坦")
P("Uganda", "烏干達", ptype="國名", region="東非", period="現代", root="烏干達")
P("Rwanda", "盧安達", var="盧旺達（陸）", ptype="國名", region="東非",
  period="現代", root="盧安")
P("Burundi", "蒲隆地", var="布隆迪（陸）", ptype="國名", region="東非",
  period="現代", root="蒲隆")
P("Nigeria", "奈及利亞", var="尼日利亞（陸）", ptype="國名", region="西非",
  period="現代", root="奈", reason="台作奈及利亞，陸作尼日利亞")
P("Ghana", "迦納", var="加納（陸）", ptype="國名", region="西非", period="現代",
  root="迦納")
P("Ivory Coast", "象牙海岸", var="科特迪瓦（陸，音譯）", ptype="國名", region="西非",
  period="現代", root="象牙", reason="台意譯象牙海岸，陸音譯科特迪瓦")
P("Senegal", "塞內加爾", ptype="國名", region="西非", period="現代", root="塞內")
P("Mali", "馬利", var="馬里（陸）", ptype="國名", region="西非", period="現代", root="馬利")
P("Niger", "尼日", var="尼日爾（陸）", ptype="國名", region="西非", period="現代", root="尼日")
P("Burkina Faso", "布吉納法索", var="布基納法索（陸）", ptype="國名", region="西非",
  period="現代", root="布")
P("Cameroon", "喀麥隆", ptype="國名", region="中非", period="現代", root="喀麥隆")
P("Chad", "查德", var="乍得（陸）", ptype="國名", region="中非", period="現代", root="查")
P("Democratic Republic of the Congo", "剛果民主共和國", var="民主剛果；剛果（金）",
  ptype="國名", region="中非", period="現代", root="剛果")
P("Republic of the Congo", "剛果共和國", var="剛果（布）", ptype="國名", region="中非",
  period="現代", root="剛果")
P("Angola", "安哥拉", ptype="國名", region="中南非", period="現代", root="安哥拉")
P("Zambia", "尚比亞", var="贊比亞（陸）", ptype="國名", region="南非", period="現代", root="尚")
P("Zimbabwe", "辛巴威", var="津巴布韋（陸）", ptype="國名", region="南非",
  period="現代", root="辛", reason="台作辛巴威，陸作津巴布韋")
P("Mozambique", "莫三比克", var="莫桑比克（陸）", ptype="國名", region="南非",
  period="現代", root="莫")
P("South Africa", "南非", var="南非共和國", ptype="國名", region="南非",
  period="現代", root="南非")
P("Namibia", "納米比亞", ptype="國名", region="南非", period="現代", root="納米")
P("Botswana", "波札那", var="博茨瓦納（陸）", ptype="國名", region="南非",
  period="現代", root="波札")
P("Madagascar", "馬達加斯加", ptype="國名", region="南非", period="現代", root="馬達")

# ════════════════════════════════════════════════════════════════════════════
# BLOCK 14 — 現代國家：美洲・大洋洲  (sort 6800–)
# ════════════════════════════════════════════════════════════════════════════
_order = 6800
P("United States", "美國", var="美利堅合眾國", ptype="國名", region="北美",
  period="現代", root="美")
P("Canada", "加拿大", ptype="國名", region="北美", period="現代", root="加")
P("Mexico", "墨西哥", ptype="國名", region="北美", period="現代", root="墨")
P("Guatemala", "瓜地馬拉", var="危地馬拉（陸）", ptype="國名", region="中美",
  period="現代", root="瓜")
P("Honduras", "宏都拉斯", var="洪都拉斯（陸）", ptype="國名", region="中美",
  period="現代", root="宏")
P("Costa Rica", "哥斯大黎加", var="哥斯達黎加（陸）", ptype="國名", region="中美",
  period="現代", root="哥斯")
P("Panama", "巴拿馬", ptype="國名", region="中美", period="現代", root="巴拿馬")
P("Cuba", "古巴", ptype="國名", region="加勒比", period="現代", root="古巴")
P("Brazil", "巴西", ptype="國名", region="南美", period="現代", root="巴西")
P("Argentina", "阿根廷", ptype="國名", region="南美", period="現代", root="阿根廷")
P("Chile", "智利", ptype="國名", region="南美", period="現代", root="智利")
P("Peru", "秘魯", ptype="國名", region="南美", period="現代", root="秘魯")
P("Colombia", "哥倫比亞", ptype="國名", region="南美", period="現代", root="哥倫")
P("Venezuela", "委內瑞拉", ptype="國名", region="南美", period="現代", root="委內")
P("Ecuador", "厄瓜多", var="厄瓜多爾（陸）", ptype="國名", region="南美",
  period="現代", root="厄瓜")
P("Bolivia", "玻利維亞", ptype="國名", region="南美", period="現代", root="玻利")
P("Paraguay", "巴拉圭", ptype="國名", region="南美", period="現代", root="巴拉圭")
P("Uruguay", "烏拉圭", ptype="國名", region="南美", period="現代", root="烏拉圭")
P("Australia", "澳洲", var="澳大利亞（陸）", ptype="國名", region="大洋洲",
  period="現代", root="澳", reason="台作澳洲，陸作澳大利亞")
P("New Zealand", "紐西蘭", var="新西蘭（陸）", ptype="國名", region="大洋洲",
  period="現代", root="紐", reason="台作紐西蘭，陸作新西蘭")
P("Papua New Guinea", "巴布亞紐幾內亞", var="巴布亞新幾內亞（陸）", ptype="國名",
  region="大洋洲", period="現代", root="幾內亞")
P("Fiji", "斐濟", ptype="國名", region="大洋洲", period="現代", root="斐濟")


# ════════════════════════════════════════════════════════════════════════════
# Main — root-consistency self-check + upsert
# ════════════════════════════════════════════════════════════════════════════
def check_roots():
    """每筆 name_root 必須是 name_recommended 的子字串（glossary_naming 規則）。"""
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
            f"{URL}/rest/v1/place_names?on_conflict=name_english",
            headers=H_UPSERT, json=batch, timeout=90,
        )
        if r.status_code >= 300:
            print(f"  UPSERT ERROR {r.status_code}: {r.text[:500]}")
            return False
        print(f"  ✓ upserted {len(batch)} (rows {i+1}–{i+len(batch)})")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只印不寫")
    args = ap.parse_args()

    # dedup check on name_english (upsert key)
    seen = {}
    for r in ROWS:
        seen.setdefault(r["name_english"], 0)
        seen[r["name_english"]] += 1
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups:
        print(f"⚠️  重複 name_english（會互相覆蓋）：{dups}")

    bad = check_roots()
    if bad:
        print(f"⚠️  名根不一致 {len(bad)} 筆：")
        for en, rec, root in bad:
            print(f"    {en}: 「{rec}」未含 root「{root}」")
    else:
        print("✓ 名根一致性檢查通過")

    print(f"\n共 {len(ROWS)} 筆 place_names")
    if args.dry:
        for r in ROWS:
            print(f"  [{r['sort_order']:>4}] {r['name_english']:<32} → {r['name_recommended']}"
                  + (f"  ({r['name_variants']})" if r.get("name_variants") else ""))
        sys.exit(0)

    if upsert(ROWS):
        print("\nDone.")
