"""
Seed official_titles for /translation-glossary (「官制與行政區」tab) — HAND-CURATED.

跟 seed_glossary_rulers.py / seed_glossary_places.py 並列、同政策：純人工策展（無 LLM）。
資料來自使用者與 AI 共同推演的「漢譯世界史」官職/行政區對照（使用者逐項討論定調）。

定名規則（見 .claude/skills/translation-glossary/offices_register_blueprint.md）：
  - 共時性：按「社會發展階段＋政治氣質」對到某朝代 register，不按日曆年代。
  - 「總督/行省/副王」是明清 register 的詞，只用在奧斯曼/蒙兀兒/俄/近世殖民帝國。
  - 帝國晚期逐層對到魏晉三級：大區行臺(行臺尚書令)→州(刺史)→郡(太守)。
  - **每個帝國撐開成完整權力金字塔**：中央（至少到部長級）→〔超一級〕→一級→二級〔→三級〕。
  - 舊的扁平譯（總督;行省）降到 name_variants 供對照。
  - register 值必須是 ADMIN_REGISTERS 之一；check_register_matches_polity 自檢政權↔register。
  - 中國詞不足可借日/韓/越漢字官職（統監/留守/道…），notes 標明。

【提】= AI 提案、細項待使用者逐項拍板；未標者為較有把握之對照。

Usage:
  python scripts/seed_glossary_offices.py --dry      # 預覽 + 自檢，不寫 DB
  python scripts/seed_glossary_offices.py --replace  # 先清空整表再全量重灌（restructure 後用這個）
  python scripts/seed_glossary_offices.py            # upsert（增量）
"""
from __future__ import annotations
import os, sys, io, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glossary_naming as gn  # noqa: E402

ROWS: list[dict] = []
_order = 0


def R(en, rec, *, o="", lang="", rom="", var="", reason="", root="",
      etype="官職", polity="", register="", level="", tier="", notes=""):
    """en=name_english, rec=name_recommended, var=既有扁平譯(；分隔)。"""
    global _order
    _order += 10
    ROWS.append({
        "name_english": en, "name_original": o or None,
        "name_original_lang": lang or None, "name_romanized": rom or None,
        "name_recommended": rec, "name_variants": var or None,
        "recommendation_reason": reason or None, "name_root": root or None,
        "entity_type": etype or None, "polity": polity or None,
        "register": register or None, "admin_level": level or None,
        "rank_tier": tier or None, "notes": notes or None,
        "sort_order": _order,
    })


# ════════════════════════════════════════════════════════════════════════════
# 商周制 — 青銅神權（阿卡德 / 古埃及 / 蘇美）
# ════════════════════════════════════════════════════════════════════════════
_order = 1000
# 阿卡德帝國
R("Akkadian Vizier", "冢宰", o="sukkallu", lang="akk", polity="阿卡德帝國", register="商周制",
  level="中央", tier="中央", var="宰相", reason="王之首輔")
R("City-state", "方國", etype="行政區", polity="阿卡德帝國", register="商周制",
  level="一級", tier="地方", var="城邦", reason="承認蘇美舊城邦，如商承周邊方國")
R("Ensi", "侯", rom="Ensí", polity="阿卡德帝國", register="商周制",
  level="一級", tier="地方", reason="保留舊城邦統治權的地方領主")
R("Akkadian Town", "邑", etype="行政區", polity="阿卡德帝國", register="商周制",
  level="二級", tier="地方", reason="城邑")
R("Rabianum (Akkad)", "邑宰", o="rabiānum", lang="akk", polity="阿卡德帝國", register="商周制",
  level="二級", tier="地方", var="市長", reason="城邑之長")
# 古埃及
R("Egyptian Vizier", "冢宰", o="tjaty", lang="egy", polity="古埃及", register="商周制",
  level="中央", tier="中央", var="宰相", reason="法老之下最高行政首長")
R("Overseer of the Treasury (Egypt)", "司帑", lang="egy", polity="古埃及", register="商周制",
  level="中央", tier="中央", var="度支；財政大臣", reason="掌國庫財賦")
R("High Priest of Amun", "大祝", lang="egy", polity="古埃及", register="商周制",
  level="中央", tier="中央", var="大祭司", reason="阿蒙神大祭司，權傾朝野")
R("Two Lands", "兩畿", etype="行政區", polity="古埃及", register="商周制",
  level="超一級", tier="地方", var="上下埃及", reason="上下埃及各設一相治理")
R("Nome", "州", o="Sepat", lang="egy", etype="行政區", polity="古埃及", register="商周制",
  level="一級", tier="地方", var="省", reason="沿尼羅河、歷史悠久穩定的行政區（使用者定調）")
R("Nomarch", "州伯", polity="古埃及", register="商周制", level="一級", tier="地方",
  var="州長；省長", root="伯", reason="世襲地方豪族，「伯」體現封建貴族色彩（使用者定調）")
R("Egyptian Town", "邑", etype="行政區", polity="古埃及", register="商周制",
  level="二級", tier="地方", var="城", reason="城邑")
R("Haty-a (Mayor)", "邑宰", o="ḥꜣtj-ꜥ", lang="egy", polity="古埃及", register="商周制",
  level="二級", tier="地方", var="市長", reason="城邑之長")
# 蘇美（烏爾第三王朝）
R("Sumerian Grand Vizier", "冢宰", o="sukkal-mah", lang="sux", polity="蘇美", register="商周制",
  level="中央", tier="中央", var="大維齊爾", reason="烏爾第三王朝之首輔")
R("Sumerian Province", "州", etype="行政區", polity="蘇美", register="商周制",
  level="一級", tier="地方", var="邦", reason="烏爾第三王朝的省")
R("Ensi (Sumer)", "牧", rom="ensi", polity="蘇美", register="商周制",
  level="一級", tier="地方", var="侯", reason="民政省長")
R("Shagina", "司馬", rom="šagina", polity="蘇美", register="商周制",
  level="一級", tier="軍事", var="將軍", reason="軍事省長")
R("Sumerian Town", "邑", etype="行政區", polity="蘇美", register="商周制",
  level="二級", tier="地方", reason="城邑")

# ════════════════════════════════════════════════════════════════════════════
# 春秋制 — 霸業立法／商業神權（古巴比倫 / 新巴比倫）
# ════════════════════════════════════════════════════════════════════════════
_order = 2000
# 古巴比倫（漢摩拉比）
R("Old Babylonian Vizier", "令尹", polity="古巴比倫", register="春秋制",
  level="中央", tier="中央", var="宰相", reason="中央宰輔（楚職）")
R("Chief Judge (Hammurabi's Code)", "司寇", polity="古巴比倫", register="春秋制",
  level="中央", tier="中央", var="廷尉", reason="掌刑獄，漢摩拉比法典傳統")
R("Old Babylonian Province", "畿", etype="行政區", polity="古巴比倫", register="春秋制",
  level="一級", tier="地方", reason="王畿/大省；漢摩拉比≈齊桓")
R("Old Babylonian City", "邑", etype="行政區", polity="古巴比倫", register="春秋制",
  level="二級", tier="地方", reason="城邑")
R("Mayor (Old Babylon)", "邑宰", o="rabiānum", lang="akk", polity="古巴比倫", register="春秋制",
  level="二級", tier="地方", var="市長", reason="城邑之長")
# 新巴比倫帝國（兩層省制）
R("Neo-Babylonian Vizier", "令尹", polity="新巴比倫帝國", register="春秋制",
  level="中央", tier="中央", var="宰相", reason="中央宰輔（楚職）")
R("Across-the-River (Ebir-nari)", "河外大省", o="Ebir-nāri", lang="akk", etype="行政區",
  polity="新巴比倫帝國", register="春秋制", level="超一級", tier="地方", var="河外行省",
  reason="統整個黎凡特之超級大省，由大尹總管")
R("Bel Pihati (Babylonian)", "大尹", o="bēl pīhāti", lang="akk", polity="新巴比倫帝國",
  register="春秋制", level="一級", tier="地方", var="省長；總督", root="尹",
  reason="大省總管；王莽改太守曰大尹、宋亦有大尹，帶南方尹味且高於縣公")
R("Neo-Babylonian Metropolitan Province", "畿", etype="行政區", polity="新巴比倫帝國",
  register="春秋制", level="一級", tier="地方", reason="巴比倫王畿")
R("Shakin Temi", "縣公", o="šākin ṭēmi", lang="akk", polity="新巴比倫帝國", register="春秋制",
  level="二級", tier="地方", var="令尹；牧",
  reason="城邑之長（巴比倫城等），隸大尹之下；楚縣特稱「公」（葉公/白公），別於中央令尹")
R("Neo-Babylonian City", "邑", etype="行政區", polity="新巴比倫帝國", register="春秋制",
  level="二級", tier="地方", reason="城邑")

# ════════════════════════════════════════════════════════════════════════════
# 戰國秦制 — 軍國郡縣（新亞述 / 波斯 / 塞琉古 / 托勒密）
# ════════════════════════════════════════════════════════════════════════════
_order = 2500
# 新亞述帝國
R("Assyrian Chancellor", "丞相", o="sukkallu", lang="akk", polity="新亞述帝國", register="戰國秦制",
  level="中央", tier="中央", var="宰相", reason="中央首輔")
R("Turtanu", "太尉", o="turtānu", lang="akk", polity="新亞述帝國", register="戰國秦制",
  level="中央", tier="軍事", var="大將軍；元帥", reason="全國軍事統帥")
R("Rab-shakeh", "大行人", o="rab šāqê", lang="akk", polity="新亞述帝國", register="戰國秦制",
  level="中央", tier="中央", var="拉伯沙基", notes="聖經王下18章圍耶路撒冷之使者",
  reason="首席酒政、兼掌外交出使")
R("Assyrian Province", "鎮", etype="行政區", polity="新亞述帝國", register="戰國秦制",
  level="一級", tier="軍事", var="行省", root="鎮", reason="軍事佔領據點、肅殺氣（使用者定調）")
R("Shaknu", "鎮監", o="šaknu", lang="akk", rom="Bel Pihati", polity="新亞述帝國",
  register="戰國秦制", level="一級", tier="軍事", var="總督；省長", root="鎮",
  reason="佔領軍司令，使用者定「鎮監」")
R("Assyrian District", "縣", etype="行政區", polity="新亞述帝國", register="戰國秦制",
  level="二級", tier="地方", reason="鎮下之縣")
R("Assyrian District Governor", "縣尉", polity="新亞述帝國", register="戰國秦制",
  level="二級", tier="軍事", var="縣令", reason="縣之武職長官，配亞述軍事風格")
# 阿契美尼德-波斯帝國
R("Hazarapatish", "丞相", o="hazarapatiš", lang="peo", polity="阿契美尼德-波斯帝國",
  register="戰國秦制", level="中央", tier="中央", var="千夫長；大維齊爾", reason="萬王之王之首輔（千夫長）")
R("Ganzabara", "治粟內史", o="ganzabara", lang="peo", polity="阿契美尼德-波斯帝國",
  register="戰國秦制", level="中央", tier="財政", var="司帑", reason="掌帝國財賦")
R("Satrapy", "州", etype="行政區", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="一級", tier="地方", var="行省；大州", root="州", reason="一省即一舊王國（使用者定調用「州」）")
R("Satrap", "州伯", o="xšaçapāvan", lang="peo", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="一級", tier="地方", var="總督；省長；方伯", root="伯",
  reason="半獨立土皇帝，對「萬王之王」稱伯（使用者定調州伯）")
R("King's Eye", "監御史", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="監察", tier="中央", var="行人；國王之眼", reason="巡視監視省長")
R("Persian Hyparchy", "郡", etype="行政區", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="二級", tier="地方", reason="州下之次級區")
R("Hyparch", "郡守", o="ὕπαρχος", lang="grc", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="二級", tier="地方", reason="次級區長官")
# 塞琉古-希臘帝國
R("Seleucid Chief Minister", "丞相", o="ho epi tōn pragmatōn", lang="grc",
  polity="塞琉古-希臘帝國", register="戰國秦制", level="中央", tier="中央", reason="總攬國政之首輔")
R("Seleucid Finance Minister", "大司農", o="ho epi tōn prosodōn", lang="grc",
  polity="塞琉古-希臘帝國", register="戰國秦制", level="中央", tier="財政", var="司帑", reason="掌歲入")
R("Upper Satrapies", "上諸州", etype="行政區", polity="塞琉古-希臘帝國", register="戰國秦制",
  level="超一級", tier="地方", reason="東方諸州（伊朗高原以東）之總合")
R("Strategos of the Upper Satrapies", "上將軍", o="στρατηγός", lang="grc",
  polity="塞琉古-希臘帝國", register="戰國秦制", level="超一級", tier="軍事", var="東方大將軍",
  reason="統轄東方諸州之最高軍政長官")
R("Strategia", "郡", etype="行政區", polity="塞琉古-希臘帝國", register="戰國秦制",
  level="一級", tier="軍事", var="行省", root="郡", reason="希臘化外來軍事殖民區（使用者定調用「郡」）")
R("Strategos", "郡尉", o="στρατηγός", lang="grc", polity="塞琉古-希臘帝國", register="戰國秦制",
  level="一級", tier="軍事", var="將軍；總督", root="郡", reason="將軍即行政首長，對郡置「尉」（使用者定調）")
R("Seleucid Eparchy", "縣", etype="行政區", polity="塞琉古-希臘帝國", register="戰國秦制",
  level="二級", tier="地方", var="小行省", reason="郡下之次級區")
R("Eparch (Seleucid)", "縣尉", o="ἔπαρχος", lang="grc", polity="塞琉古-希臘帝國", register="戰國秦制",
  level="二級", tier="軍事", reason="次級區長官")
# 托勒密-埃及
R("Dioiketes", "大司農", o="διοικητής", lang="grc", polity="托勒密-埃及", register="戰國秦制",
  level="中央", tier="財政", var="丞相", reason="總掌全國財政經濟之首相級大臣")
R("Ptolemaic Nome", "郡", etype="行政區", polity="托勒密-埃及", register="戰國秦制",
  level="一級", tier="地方", var="州", reason="托勒密沿用埃及舊 nome")
R("Strategos (Ptolemaic)", "郡尉", o="στρατηγός", lang="grc", polity="托勒密-埃及", register="戰國秦制",
  level="一級", tier="軍事", var="將軍", reason="nome 之軍政長官")
R("Nomarch (Ptolemaic)", "郡守", polity="托勒密-埃及", register="戰國秦制",
  level="一級", tier="地方", reason="nome 之民政長官")
R("Oikonomos", "少府", o="οἰκονόμος", lang="grc", polity="托勒密-埃及", register="戰國秦制",
  level="一級", tier="財政", reason="nome 之財政官")
R("Toparchy (Ptolemaic)", "鄉", etype="行政區", polity="托勒密-埃及", register="戰國秦制",
  level="二級", tier="地方", reason="nome 下之次級區")
R("Toparches", "嗇夫", o="τοπάρχης", lang="grc", polity="托勒密-埃及", register="戰國秦制",
  level="二級", tier="地方", reason="鄉之長，借秦漢鄉官「嗇夫」")

# ════════════════════════════════════════════════════════════════════════════
# 漢制 — 郡國並行（羅馬共和 / 羅馬帝國早期）
# ════════════════════════════════════════════════════════════════════════════
_order = 3000
# 羅馬共和國
R("Consul", "執政官", o="consul", lang="la", polity="羅馬共和國", register="漢制",
  level="中央", tier="中央", reason="共和國最高行政長官（二人）")
R("Praetor", "廷尉", o="praetor", lang="la", polity="羅馬共和國", register="漢制",
  level="中央", tier="司法", var="法務官", reason="掌司法審判")
R("Quaestor", "治粟內史", o="quaestor", lang="la", polity="羅馬共和國", register="漢制",
  level="中央", tier="財政", var="財務官", reason="掌國庫")
R("Censor", "司直", o="censor", lang="la", polity="羅馬共和國", register="漢制",
  level="中央", tier="監察", var="司民；監察官", reason="掌戶口、風紀、元老院名籍")
R("Tribune of the Plebs", "保民官", o="tribunus plebis", lang="la", polity="羅馬共和國",
  register="漢制", level="中央", tier="中央", reason="護民、有否決權")
R("Senate", "元老院", o="senatus", lang="la", etype="機構", polity="羅馬共和國", register="漢制",
  level="中央", tier="中央", reason="貴族議政機構")
R("Senatorial Province", "行省", etype="行政區", polity="羅馬共和國", register="漢制",
  level="一級", tier="地方", root="行省", reason="元老院管轄之已羅馬化富庶區")
R("Proconsul", "牧", o="pro consule", lang="la", polity="羅馬共和國", register="漢制",
  level="一級", tier="地方", var="總督", reason="前執政官外放，地位崇高如漢州牧（使用者定調）")
R("Roman Civitas", "縣", o="civitas", lang="la", etype="行政區", polity="羅馬共和國", register="漢制",
  level="二級", tier="地方", var="自治市", reason="行省下之自治城邦")
R("Duumvir", "邑宰", o="duumvir", lang="la", polity="羅馬共和國", register="漢制",
  level="二級", tier="地方", var="二市長", reason="自治市之首長（二人）")
# 羅馬帝國（早期＝漢制）
R("Praetorian Prefect (Principate)", "太尉", o="praefectus praetorio", lang="la",
  polity="羅馬帝國", register="漢制", level="中央", tier="軍事", var="禁衛軍長官",
  reason="元首制下之禁衛統帥（晚期演為大區行臺，見魏晉制）")
R("Ab Epistulis", "尚書", o="ab epistulis", lang="la", polity="羅馬帝國", register="漢制",
  level="中央", tier="中央", var="秘書", reason="掌皇帝文書之秘書長")
R("Imperial Province", "行省", etype="行政區", polity="羅馬帝國", register="漢制",
  level="一級", tier="軍事", root="行省", reason="邊境駐軍團之皇帝直轄區")
R("Legatus Augusti", "都護", lang="la", polity="羅馬帝國", register="漢制",
  level="一級", tier="軍事", var="總督；皇帝欽差", root="都護",
  reason="皇帝欽差、統率軍團，如漢西域都護（使用者定調）")
R("Praefectus Aegypti", "大尹", lang="la", polity="羅馬帝國", register="漢制",
  level="特區", tier="中央", var="總督；埃及長官",
  reason="埃及為皇帝私產，長官如皇家大管家，用「尹」不用「總督」（使用者定調）")
R("Judaea Prefecture", "郡", o="Iudaea", lang="la", etype="行政區", polity="羅馬帝國",
  register="漢制", level="二級", tier="地方", var="猶太行省",
  reason="隸敘利亞大行省之附屬小區，非獨立行省（使用者定調降為「郡」）")
R("Praefectus Iudaeae", "都尉", lang="la", polity="羅馬帝國", register="漢制",
  level="二級", tier="軍事", var="總督；巡撫", notes="本丟彼拉多 Pontius Pilate 之職",
  reason="騎士階級、受都護節制、管邊陲小郡，位低於都護（使用者定調都尉）")
R("Conventus", "郡", o="conventus iuridicus", lang="la", etype="行政區", polity="羅馬帝國",
  register="漢制", level="二級", tier="地方", var="司法巡迴區", reason="行省下之司法巡迴區，轄數自治市")
R("Imperial Civitas", "縣", o="civitas", lang="la", etype="行政區", polity="羅馬帝國",
  register="漢制", level="三級", tier="地方", var="自治市", reason="會郡下之自治城邦")
R("Client Kingdom", "屬國", etype="行政區", polity="羅馬帝國", register="漢制",
  level="羈縻", tier="地方", reason="名義獨立之緩衝國，Rex→國王；羅馬亦郡國並行如漢")
R("Toparchy", "縣", o="τοπαρχία", lang="grc", etype="行政區", polity="希律猶太王國",
  register="漢制", level="三級", tier="地方", var="邑", reason="希律王國內二級單位，王國—縣二級制")
R("Ethnarch", "民族大君", o="ἐθνάρχης", lang="grc", polity="希律猶太王國", register="漢制",
  level="羈縻", tier="地方", reason="希律死後裂土，如推恩令分封")
R("Tetrarch", "分封王", o="τετράρχης", lang="grc", polity="希律猶太王國", register="漢制",
  level="羈縻", tier="地方", var="侯", reason="四分領地之王，如安提帕領加利利")

# ════════════════════════════════════════════════════════════════════════════
# 魏晉制 — 帝國晚期三級科層（羅馬帝國晚期，戴克里先後）
# ════════════════════════════════════════════════════════════════════════════
_order = 4000
R("Magister Officiorum", "尚書令", lang="la", polity="羅馬帝國", register="魏晉制",
  level="中央", tier="中央", var="百官之長", reason="總領禁衛文書、驛傳、朝儀之中樞首長")
R("Comes Sacrarum Largitionum", "度支尚書", lang="la", polity="羅馬帝國", register="魏晉制",
  level="中央", tier="財政", var="財政大臣", reason="掌帝國財賦")
R("Quaestor Sacri Palatii", "廷尉", lang="la", polity="羅馬帝國", register="魏晉制",
  level="中央", tier="司法", var="御前法務大臣", reason="掌立法草詔")
R("Tetrarchy", "四帝共治", o="tetrarchia", lang="la", etype="機構", polity="羅馬帝國",
  register="魏晉制", level="中央", tier="中央", var="四主分治",
  reason="戴克里先所創：二正帝(Augusti)＋二副帝(Caesares)分治帝國四方")
R("Augustus (Tetrarchy)", "正帝", o="Augustus", lang="la", polity="羅馬帝國", register="魏晉制",
  level="超一級", tier="中央", var="奧古斯都；大皇帝", reason="共治正帝，各統帝國之半（東/西）")
R("Caesar (Tetrarchy)", "副帝", o="Caesar", lang="la", polity="羅馬帝國", register="魏晉制",
  level="超一級", tier="中央", var="凱撒；儲帝", reason="共治副帝兼儲君，各統一區，受正帝節制")
R("Praetorian Prefecture", "大區行臺", lang="la", etype="行政區", polity="羅馬帝國",
  register="魏晉制", level="超一級", tier="地方", var="大區", root="行臺",
  reason="戴克里先後最高行政區（四大區：高盧/義大利/伊利里亞/東方，約當四帝管區），如魏晉行臺（使用者定調）")
R("Praetorian Prefect (Dominate)", "行臺尚書令", lang="la", polity="羅馬帝國",
  register="魏晉制", level="超一級", tier="中央", var="大區長官", root="行臺",
  reason="皇帝首席副手、總攬軍政財，如行臺尚書令（使用者定調）")
R("Diocese", "州", o="dioecesis", lang="la", etype="行政區", polity="羅馬帝國",
  register="魏晉制", level="一級", tier="地方", var="管區", root="州", reason="大區下之中間層，如魏晉之州")
R("Vicarius", "刺史", lang="la", polity="羅馬帝國", register="魏晉制",
  level="一級", tier="地方", var="管區長官", reason="監察其下數郡，如魏晉刺史（使用者定調）")
R("Late Province", "郡", o="provincia", lang="la", etype="行政區", polity="羅馬帝國",
  register="魏晉制", level="二級", tier="地方", var="行省", root="郡",
  reason="戴克里先切碎後之小行省，實質如郡，故改譯「郡」（使用者定調）")
R("Rector", "太守", lang="la", polity="羅馬帝國", register="魏晉制",
  level="二級", tier="地方", var="行省總督；Praeses", reason="基層行省長官，如漢晉太守（使用者定調）")

# ════════════════════════════════════════════════════════════════════════════
# 唐制 — 軍區藩鎮／宗教帝國（東羅馬軍區 / 阿拉伯-阿拔斯）
# ════════════════════════════════════════════════════════════════════════════
_order = 5000
# 拜占庭帝國（軍區制時期＝唐制）
R("Domestic of the Schools", "大將軍", o="δομέστικος τῶν σχολῶν", lang="grc",
  polity="拜占庭帝國", register="唐制", level="中央", tier="軍事", reason="中央野戰軍最高統帥")
R("Logothete tou Dromou", "侍中", o="λογοθέτης τοῦ δρόμου", lang="grc", polity="拜占庭帝國",
  register="唐制", level="中央", tier="中央", var="傳驛大臣", reason="掌外交、驛傳、情報之樞要")
R("Exarchate", "總督區", o="ἐξαρχᾶτον", lang="grc", etype="行政區", polity="拜占庭帝國",
  register="唐制", level="超一級", tier="軍事", var="大都督府",
  reason="6-8世紀拉文納/迦太基總督區，軍民合一之大區")
R("Exarch", "大都督", o="ἔξαρχος", lang="grc", polity="拜占庭帝國", register="唐制",
  level="超一級", tier="軍事", var="總督", reason="總督區全權長官，如持節大都督（拉文納總督）")
R("Katepanate", "大都護府", o="κατεπανίκιον", lang="grc", etype="行政區", polity="拜占庭帝國",
  register="唐制", level="超一級", tier="軍事", var="都督府",
  reason="10-11世紀合數軍區之邊防大區（如義大利大都護府）")
R("Katepano", "大都護", o="κατεπάνω", lang="grc", polity="拜占庭帝國", register="唐制",
  level="超一級", tier="軍事", var="都督", reason="統轄數軍道之邊防統帥")
R("Theme", "軍道", o="θέμα", lang="grc", etype="行政區", polity="拜占庭帝國", register="唐制",
  level="一級", tier="軍事", var="軍區", root="道", reason="軍區制，士兵屯田世襲，如中晚唐藩鎮之道")
R("Byzantine Strategos", "節度使", o="στρατηγός", lang="grc", polity="拜占庭帝國", register="唐制",
  level="一級", tier="軍事", var="軍區將軍", reason="軍政一把抓，與唐節度使同時演化功能全同（使用者定調）")
R("Tourma", "州", o="τοῦρμα", lang="grc", etype="行政區", polity="拜占庭帝國", register="唐制",
  level="二級", tier="軍事", reason="軍道下之次級區")
R("Tourmarches", "都督", o="τουρμάρχης", lang="grc", polity="拜占庭帝國", register="唐制",
  level="二級", tier="軍事", reason="次級軍區長官")
# 阿拔斯-阿拉伯帝國
R("Vizier", "宰相", o="وزير", lang="ar", polity="阿拔斯-阿拉伯帝國", register="唐制",
  level="中央", tier="中央", reason="波斯化文官體系之首")
R("Diwan al-Kharaj", "戶部尚書", o="ديوان الخراج", lang="ar", polity="阿拔斯-阿拉伯帝國",
  register="唐制", level="中央", tier="財政", var="度支", reason="掌田賦稅收之財政部")
R("Qadi al-Qudat", "大理寺卿", o="قاضي القضاة", lang="ar", polity="阿拔斯-阿拉伯帝國",
  register="唐制", level="中央", tier="司法", var="大法官", reason="全國最高司法官")
R("Wilayah", "道", o="ولاية", lang="ar", etype="行政區", polity="阿拔斯-阿拉伯帝國", register="唐制",
  level="一級", tier="地方", var="行省；轄區", root="道", reason="遼闊行省，如唐之道（使用者定調）")
R("Amir", "經略使", o="أمير", lang="ar", rom="Wali", polity="阿拔斯-阿拉伯帝國", register="唐制",
  level="一級", tier="軍事", var="埃米爾；總督；提督", reason="軍政合一、邊疆經營，如唐宋經略安撫使（使用者定調）")
R("Kura", "州", o="كورة", lang="ar", etype="行政區", polity="阿拔斯-阿拉伯帝國", register="唐制",
  level="二級", tier="地方", reason="道下之州縣級區")
R("Amil", "刺史", o="عامل", lang="ar", polity="阿拔斯-阿拉伯帝國", register="唐制",
  level="二級", tier="地方", var="稅吏", reason="州級行政、徵稅官")
# 薩珊-波斯帝國（唐制：四方都督＋祆教國教＋門閥世卿；拜占庭之鏡像對手）
_order = 5200
R("Sasanian Grand Vizier", "丞相", o="wuzurg framadar", lang="pal", polity="薩珊-波斯帝國",
  register="唐制", level="中央", tier="中央", var="大相；波斯宰相", reason="帝國首輔")
R("Eran-spahbed", "大將軍", o="ērān-spāhbed", lang="pal", polity="薩珊-波斯帝國",
  register="唐制", level="中央", tier="軍事", var="太尉；全軍統帥", reason="改革前之全國軍事統帥")
R("Mowbedan Mowbed", "國師", o="mowbedān mowbed", lang="pal", polity="薩珊-波斯帝國",
  register="唐制", level="中央", tier="中央", var="大祭司；祆教教長", reason="祆教國教之最高祭司，權傾朝野")
R("Wastaryoshan-salar", "大司農", o="wāstaryōšān-sālār", lang="pal", polity="薩珊-波斯帝國",
  register="唐制", level="中央", tier="財政", reason="掌農賦稅收")
R("Wuzurgan", "世卿", o="wuzurgān", lang="pal", etype="機構", polity="薩珊-波斯帝國",
  register="唐制", level="中央", tier="中央", var="門閥；七大家族", reason="世襲大貴族（七大家族），如魏晉門閥")
R("Kust (Quarter)", "方", o="kust", lang="pal", etype="行政區", polity="薩珊-波斯帝國",
  register="唐制", level="超一級", tier="軍事", var="四方；大區", reason="庫斯老一世改革分帝國為東西南北四方")
R("Spahbed (Quarter)", "都督", o="spāhbed", lang="pal", polity="薩珊-波斯帝國",
  register="唐制", level="超一級", tier="軍事", var="四方都督；大將軍", reason="一方之最高軍政統帥，如唐四鎮都督")
R("Shahr (Province)", "州", o="šahr", lang="pal", etype="行政區", polity="薩珊-波斯帝國",
  register="唐制", level="一級", tier="地方", var="省；ostan", reason="一級行政區")
R("Shahrab", "州牧", o="šahrab", lang="pal", polity="薩珊-波斯帝國", register="唐制",
  level="一級", tier="地方", var="刺史；省長；ostandar", reason="州之長官")
R("Marzban (Sasanian)", "節度使", o="marzbān", lang="pal", polity="薩珊-波斯帝國", register="唐制",
  level="一級", tier="軍事", var="邊境總督；招討使", reason="邊疆軍政重鎮之馬爾茲班，如唐節度使")
R("Sasanian District", "縣", o="tasug", lang="pal", etype="行政區", polity="薩珊-波斯帝國",
  register="唐制", level="二級", tier="地方", var="rostag", reason="州下之縣")
R("Sasanian District Head", "縣令", polity="薩珊-波斯帝國", register="唐制",
  level="二級", tier="地方", reason="縣之長官")
R("Dihqan", "里正", o="dihqān", lang="pal", polity="薩珊-波斯帝國", register="唐制",
  level="二級", tier="地方", var="鄉豪；地方鄉紳", reason="鄉里世襲小地主，帝國基層支柱，如里正/鄉豪")

# ════════════════════════════════════════════════════════════════════════════
# 宋制 — 中央文官（東羅馬晚期）
# ════════════════════════════════════════════════════════════════════════════
_order = 5500
R("Mesazon", "參知政事", o="μεσάζων", lang="grc", polity="拜占庭帝國", register="宋制",
  level="中央", tier="中央", var="首相", reason="晚期實際首相（帝與百官間之中介）")
R("Logothete", "三司使", o="λογοθέτης", lang="grc", polity="拜占庭帝國", register="宋制",
  level="中央", tier="財政", var="度支使；大臣", reason="掌財政之中央大臣，如宋三司使")
R("Kephale", "知州", o="κεφαλή", lang="grc", polity="拜占庭帝國", register="宋制",
  level="一級", tier="地方", var="總督；城市長官", reason="晚期中央派任之府/城長官，如宋「知某州事」")
R("Byzantine Kastron", "城", o="κάστρον", lang="grc", etype="行政區", polity="拜占庭帝國",
  register="宋制", level="二級", tier="地方", var="縣", reason="設防城邑，晚期基層行政單位")
R("Kastrophylax", "知縣", o="καστροφύλαξ", lang="grc", polity="拜占庭帝國", register="宋制",
  level="二級", tier="地方", var="城守", reason="城邑之守，如宋知縣")

# ════════════════════════════════════════════════════════════════════════════
# 遼金元制 — 游牧/征服帝國（安息 / 塞爾柱 / 蒙古）
# ════════════════════════════════════════════════════════════════════════════
_order = 6000
# 安息-帕提亞帝國
R("Wuzurg Framadar", "大相", o="wuzurg framadar", lang="pal", polity="安息-帕提亞帝國",
  register="遼金元制", level="中央", tier="中央", var="丞相", reason="帝國首輔")
R("Northern Court (Parthia)", "北面官", polity="安息-帕提亞帝國", register="遼金元制",
  level="中央", tier="中央", reason="治游牧伊朗部族之官（遼南北面雙軌）", etype="機構")
R("Southern Court (Parthia)", "南面官", polity="安息-帕提亞帝國", register="遼金元制",
  level="中央", tier="中央", reason="治定居希臘城市之官（遼南北面雙軌）", etype="機構")
R("Parthian Vassal Kingdom", "屬國", etype="行政區", polity="安息-帕提亞帝國", register="遼金元制",
  level="超一級", tier="地方", reason="半獨立封屬國（如亞美尼亞、埃蘭）")
R("Parthian Satrapy", "省", etype="行政區", polity="安息-帕提亞帝國", register="遼金元制",
  level="一級", tier="地方", var="行省", reason="沿襲之省級區")
R("Marzban", "招討使", o="marzbān", lang="pal", polity="安息-帕提亞帝國", register="遼金元制",
  level="一級", tier="軍事", var="邊境總督；馬爾茲班", reason="邊疆軍事鎮守者，如遼宋招討使")
R("Parthian City", "城", etype="行政區", polity="安息-帕提亞帝國", register="遼金元制",
  level="二級", tier="地方", reason="城邑")
R("Dizpat", "城主", o="dizpat", lang="pal", polity="安息-帕提亞帝國", register="遼金元制",
  level="二級", tier="地方", reason="城邑之長")
# 塞爾柱-突厥帝國
R("Seljuk Vizier", "宰相", o="وزير", lang="fa", polity="塞爾柱-突厥帝國", register="遼金元制",
  level="中央", tier="中央", notes="尼查姆‧穆勒克（Nizam al-Mulk）為代表", reason="波斯官僚體系之首輔")
R("Iqta", "食邑", o="إقطاع", lang="ar", etype="行政區", polity="塞爾柱-突厥帝國", register="遼金元制",
  level="一級", tier="軍事", var="采邑；封地", reason="以軍事義務換取之土地采邑")
R("Seljuk Emir", "節度使", o="أمير", lang="ar", polity="塞爾柱-突厥帝國", register="遼金元制",
  level="一級", tier="軍事", var="埃米爾", reason="掌一省軍政之突厥將領")
R("Atabeg", "太傅", o="اتابك", lang="fa", polity="塞爾柱-突厥帝國", register="遼金元制",
  level="一級", tier="地方", var="監國；輔王", reason="幼主之師傅兼領地監國者")
R("Seljuk District", "州", etype="行政區", polity="塞爾柱-突厥帝國", register="遼金元制",
  level="二級", tier="地方", reason="省下之州縣級區")
# 蒙古帝國（元）
R("Central Secretariat", "丞相", o="ᠳᠤᠮᠳᠠᠳᠤ ᠶᠠᠮᠤᠨ", lang="mn", rom="Zhongshu", polity="蒙古帝國",
  register="遼金元制", level="中央", tier="中央", var="中書省", reason="元中書省，總理政務之首輔")
R("Bureau of Military Affairs", "樞密院", etype="機構", polity="蒙古帝國", register="遼金元制",
  level="中央", tier="軍事", reason="掌全國軍務")
R("Jarghuchi", "斷事官", o="ᠵᠠᠷᠭᠤᠴᠢ", lang="mn", rom="jarghuchi", polity="蒙古帝國",
  register="遼金元制", level="中央", tier="司法", var="札魯忽赤", reason="蒙古最高司法官")
R("Great Khan", "大汗", o="ᠶᠡᠺᠡ ᠬᠠᠭᠠᠨ", lang="mn", rom="Yeke Khagan", polity="蒙古帝國",
  register="遼金元制", level="中央", tier="中央", var="可汗", reason="草原共主")
R("Khanate", "汗國", o="ᠬᠠᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="超一級", tier="地方", reason="大汗分封諸子之汗國（伊兒/金帳/察合台）")
R("Branch Secretariat", "行省", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="超一級", tier="地方", var="行中書省", reason="元創「行中書省」，中央派出之大區（「行省」本源）")
R("Pingzhang Zhengshi", "平章政事", polity="蒙古帝國", register="遼金元制",
  level="超一級", tier="地方", reason="行省之最高長官")
R("Darughachi", "達魯花赤", o="ᠳᠠᠷᠤᠭᠠᠴᠢ", lang="mn", polity="蒙古帝國", register="遼金元制",
  level="一級", tier="地方", var="監臨官；鎮守官", reason="蒙古派駐地方之最高監臨官，元代本即漢譯「達魯花赤」")
R("Lu (Circuit)", "路", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="二級", tier="地方", reason="元行省下之路")
R("Route Commander", "總管", polity="蒙古帝國", register="遼金元制",
  level="二級", tier="地方", var="路總管", reason="路之民政長官（與達魯花赤並置）")
R("Tumen", "萬戶", o="ᠲᠦᠮᠡᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="一級", tier="軍事", var="土綿", reason="十進位軍事編制（一萬戶/兵）")
R("Minghan", "千戶", o="ᠮᠢᠩᠭᠠᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="二級", tier="軍事", reason="千戶編制，如元千戶／金猛安")
R("Jaghun", "百戶", o="ᠵᠠᠭᠤᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="三級", tier="軍事", reason="百戶編制，如元百戶／金謀克")

# ════════════════════════════════════════════════════════════════════════════
# 明清制 — 近世火藥帝國＋殖民（奧斯曼 / 蒙兀兒 / 俄 / 西 / 英 / 法）
# ════════════════════════════════════════════════════════════════════════════
_order = 7000
# 鄂圖曼-土耳其帝國
R("Grand Vizier", "首相", o="صدر اعظم", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="中央", tier="中央", var="大維齊爾；內閣首輔", reason="蘇丹之下最高執政")
R("Defterdar", "戶部尚書", o="دفتردار", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="中央", tier="財政", reason="掌帝國財政")
R("Kadiasker", "大理寺卿", o="قاضی عسکر", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="中央", tier="司法", var="軍法官", reason="最高司法官（分魯米利亞/安納托利亞）")
R("Sheikh ul-Islam", "大宗伯", o="شیخ الاسلام", lang="ota", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="中央", tier="中央", var="掌教", reason="伊斯蘭教法最高權威")
R("Eyalet", "總督區", o="ایالت", lang="ota", etype="行政區", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="一級", tier="地方", var="行省", reason="奧斯曼一級軍事封建區（使用者定調）")
R("Beylerbey", "總督", o="بیلربیی", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="一級", tier="地方", var="眾貝伊之貝伊", reason="一級長官，明清 register 內「總督」恰當")
R("Sanjak", "旗", o="سنجاق", lang="ota", etype="行政區", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="二級", tier="軍事", var="縣", reason="Sanjak 原意旗幟，與清八旗同軍事邏輯（使用者定調）")
R("Sanjak-bey", "旗主", o="سنجاق بیی", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="二級", tier="軍事", var="佐領；旗長", reason="軍事動員基本單位之長，如清旗主/佐領")
R("Kaza", "縣", o="قضا", lang="ota", etype="行政區", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="三級", tier="地方", reason="旗下之司法/行政縣")
R("Kadi", "知縣", o="قاضی", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="三級", tier="司法", var="法官", reason="縣之法官兼行政首長")
R("Timar", "采邑", o="تیمار", lang="ota", etype="行政區", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="三級", tier="軍事", var="食邑", reason="騎兵封地，以軍役換取收租權")
R("Sipahi", "府兵", o="سپاهی", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="三級", tier="軍事", var="騎兵", reason="領 timar 出征之封建騎士，如府兵")
R("Janissary", "禁軍", o="یڭیچری", lang="ota", polity="鄂圖曼-土耳其帝國", register="明清制",
  level="中央", tier="軍事", var="新軍", reason="蘇丹常備步兵，devshirme 徵召，如禁軍")
# 蒙兀兒帝國
R("Mughal Wazir", "首相", o="وزیر", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="中央", tier="中央", var="大維齊爾", reason="帝國宰輔（diwan 之首）")
R("Diwan-i-Kul", "戶部尚書", o="دیوان کل", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="中央", tier="財政", reason="全國財政大臣")
R("Mir Bakhshi", "兵部尚書", o="میر بخشی", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="中央", tier="軍事", reason="掌軍餉、軍階（mansab）")
R("Sadr-us-Sudur", "大宗伯", o="صدرالصدور", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="中央", tier="中央", var="掌教", reason="宗教與慈善事務最高官")
R("Mansabdar", "品秩軍官", o="منصبدار", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="中央", tier="軍事", var="曼薩布達爾", reason="以數字軍階(mansab)定品秩之官僚軍事貴族，如清品秩")
R("Subah", "省", lang="fa", etype="行政區", polity="蒙兀兒帝國", register="明清制",
  level="一級", tier="地方", reason="官僚化一級行政區")
R("Subahdar", "提督", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="一級", tier="軍事", var="總督", reason="掌一省軍政，用「提督」以別於奧斯曼總督")
R("Provincial Diwan (Mughal)", "布政使", o="دیوان", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="一級", tier="財政", reason="省之財政長官，與提督並置")
R("Sarkar", "府", o="سرکار", lang="fa", etype="行政區", polity="蒙兀兒帝國", register="明清制",
  level="二級", tier="地方", reason="省下之府")
R("Faujdar", "知府", o="فوجدار", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="二級", tier="軍事", reason="府之軍政長官")
R("Pargana", "縣", o="پرگنه", lang="fa", etype="行政區", polity="蒙兀兒帝國", register="明清制",
  level="三級", tier="地方", reason="府下之縣")
R("Amalguzar", "知縣", o="عمل گذار", lang="fa", polity="蒙兀兒帝國", register="明清制",
  level="三級", tier="地方", var="徵稅官", reason="縣之徵稅、行政首長")
# 俄羅斯帝國
R("Governing Senate", "參政院", o="Правительствующий сенат", lang="ru", etype="機構",
  polity="俄羅斯帝國", register="明清制", level="中央", tier="中央", var="樞密院", reason="彼得大帝所立最高行政/司法院")
R("Collegia", "六部", o="коллегии", lang="ru", etype="機構", polity="俄羅斯帝國", register="明清制",
  level="中央", tier="中央", var="各部", reason="分掌財政/外交/軍事之各部")
R("Procurator-General", "都察院", o="генерал-прокурор", lang="ru", polity="俄羅斯帝國",
  register="明清制", level="中央", tier="監察", var="總檢察長", reason="「沙皇之眼」監察百官")
R("Governorate-General", "總督區", o="генерал-губернаторство", lang="ru", etype="行政區",
  polity="俄羅斯帝國", register="明清制", level="超一級", tier="地方", reason="轄數省之大區")
R("Governor-General (Russia)", "總督", o="генерал-губернатор", lang="ru", polity="俄羅斯帝國",
  register="明清制", level="超一級", tier="地方", reason="總督區長官，如兩廣總督")
R("Guberniya", "省", o="губерния", lang="ru", etype="行政區", polity="俄羅斯帝國", register="明清制",
  level="一級", tier="地方", reason="一級行政區")
R("Gubernator", "巡撫", o="губернатор", lang="ru", polity="俄羅斯帝國", register="明清制",
  level="一級", tier="地方", var="省長；總督", reason="沙俄省長，權重如清末巡撫（使用者定調）")
R("Uyezd", "縣", o="уезд", lang="ru", etype="行政區", polity="俄羅斯帝國", register="明清制",
  level="二級", tier="地方", var="州", reason="省下之縣")
R("Ispravnik", "知縣", o="исправник", lang="ru", polity="俄羅斯帝國", register="明清制",
  level="二級", tier="地方", reason="縣之警政/行政長官")
# 西班牙帝國
R("Council of the Indies", "理藩院", o="Consejo de Indias", lang="es", etype="機構",
  polity="西班牙帝國", register="明清制", level="中央", tier="中央", reason="掌美洲/菲律賓殖民之最高會議")
R("Casa de Contratacion", "市舶司", o="Casa de Contratación", lang="es", etype="機構",
  polity="西班牙帝國", register="明清制", level="中央", tier="財政", var="貿易署", reason="掌殖民貿易與稅收")
R("Viceroyalty", "副王區", o="Virreinato", lang="es", etype="行政區", polity="西班牙帝國",
  register="明清制", level="超一級", tier="地方", reason="最高殖民區，國王替身之轄地（使用者定調）")
R("Viceroy", "副王", o="Virrey", lang="es", polity="西班牙帝國", register="明清制",
  level="超一級", tier="地方", var="總督", reason="Viceroy 原意國王替身，如親王就藩（使用者定調）")
R("Audiencia", "王國", o="Audiencia", lang="es", etype="行政區", polity="西班牙帝國", register="明清制",
  level="一級", tier="地方", var="聽審院", reason="設聽審院之王國級行政區（如墨西哥/新加利西亞）")
R("Captaincy General", "都督府", o="Capitanía General", lang="es", etype="行政區",
  polity="西班牙帝國", register="明清制", level="一級", tier="軍事", reason="戰略要地軍管區（古巴/菲律賓）")
R("Captain General", "提督", o="Capitán General", lang="es", polity="西班牙帝國", register="明清制",
  level="一級", tier="軍事", var="都督；總督", reason="鎮守戰略要地之軍事統帥（使用者定調）")
R("Corregimiento", "道", o="Corregimiento", lang="es", etype="行政區", polity="西班牙帝國",
  register="明清制", level="二級", tier="地方", reason="王國下之次級行政區")
R("Corregidor", "道臺", o="Corregidor", lang="es", polity="西班牙帝國", register="明清制",
  level="二級", tier="地方", reason="地方行政官")
# 大英帝國
R("Colonial Secretary", "殖民部尚書", polity="大英帝國", register="明清制",
  level="中央", tier="中央", var="殖民地大臣", reason="倫敦掌殖民地之閣員")
R("Board of Trade", "市舶司", etype="機構", polity="大英帝國", register="明清制",
  level="中央", tier="財政", var="貿易委員會", reason="掌殖民貿易")
R("Governor-General (Britain)", "大總督", polity="大英帝國", register="明清制",
  level="超一級", tier="地方", var="總督；副王", reason="統轄聯邦/大陸領地、下有數省長，如兩廣總督（使用者定調）")
R("Colonial Governor", "總督", polity="大英帝國", register="明清制",
  level="一級", tier="地方", notes="如香港總督、新加坡總督", reason="直轄倫敦、獨當一面之最高長官（使用者定調）")
R("Lieutenant Governor", "巡撫", polity="大英帝國", register="明清制",
  level="二級", tier="地方", var="省督", reason="上有大總督管轄，如加拿大各省督（使用者定調）")
R("District (India)", "縣", etype="行政區", polity="大英帝國", register="明清制",
  level="三級", tier="地方", reason="印度基層行政區")
R("District Collector", "知縣", polity="大英帝國", register="明清制",
  level="三級", tier="地方", var="徵稅官", reason="縣之徵稅兼行政首長")
# 法蘭西殖民帝國
R("Ministre des Colonies", "殖民部尚書", lang="fr", polity="法蘭西殖民帝國", register="明清制",
  level="中央", tier="中央", var="殖民地大臣", reason="巴黎掌殖民地之閣員")
R("Gouverneur général", "大總督", lang="fr", polity="法蘭西殖民帝國", register="明清制",
  level="超一級", tier="地方", reason="殖民聯邦最高長官，如法屬印度支那大總督（使用者定調）")
R("Résident supérieur", "統監", lang="fr", polity="法蘭西殖民帝國", register="明清制",
  level="保護國", tier="地方", var="高級駐紮官；駐紮大臣",
  reason="保護國高級駐紮官（名義顧問實太上皇），借日治朝鮮「統監」（使用者定調；中國詞不足借日）")
R("Gouverneur (colonial)", "巡撫", lang="fr", polity="法蘭西殖民帝國", register="明清制",
  level="一級", tier="地方", reason="直轄地省長，位在大總督之下")
R("Cercle", "縣", lang="fr", etype="行政區", polity="法蘭西殖民帝國", register="明清制",
  level="二級", tier="地方", reason="殖民地基層行政區")
R("Commandant de cercle", "知縣", lang="fr", polity="法蘭西殖民帝國", register="明清制",
  level="二級", tier="地方", reason="cercle 之行政首長")

# ════════════════════════════════════════════════════════════════════════════
# 周封建五等爵 — 中世紀西歐封建
# ════════════════════════════════════════════════════════════════════════════
_order = 8000
R("Chancellor", "相", o="cancellarius", lang="la", polity="中世紀西歐封建", register="周封建五等爵",
  level="中央", tier="中央", var="掌璽；尚書令", reason="國王之首輔、掌印")
R("Curia Regis", "政事堂", o="curia regis", lang="la", etype="機構", polity="中世紀西歐封建",
  register="周封建五等爵", level="中央", tier="中央", var="御前會議", reason="國王與封臣之議政會議")
R("Kingdom", "王國", etype="行政區", polity="中世紀西歐封建", register="周封建五等爵",
  level="超一級", tier="封爵", reason="封建最高政治體")
R("King", "國王", o="rex", lang="la", polity="中世紀西歐封建", register="周封建五等爵",
  level="超一級", tier="封爵", reason="封建君主")
R("Duchy", "公國", etype="行政區", polity="中世紀西歐封建", register="周封建五等爵",
  level="一級", tier="封爵", reason="公爵領地")
R("Duke", "公", o="dux", lang="la", polity="中世紀西歐封建", register="周封建五等爵",
  level="一級", tier="封爵", reason="五等爵之首，傳統譯已正確")
R("Marquisate", "侯國", etype="行政區", polity="中世紀西歐封建", register="周封建五等爵",
  level="一級", tier="封爵", var="邊境侯領", reason="邊侯領地")
R("Marquis", "侯", polity="中世紀西歐封建", register="周封建五等爵",
  level="一級", tier="封爵", var="侯爵；邊侯", reason="邊境封侯")
R("County", "伯國", etype="行政區", polity="中世紀西歐封建", register="周封建五等爵",
  level="二級", tier="封爵", reason="伯爵領地")
R("Count", "伯", o="comes", lang="la", polity="中世紀西歐封建", register="周封建五等爵",
  level="二級", tier="封爵", var="伯爵", root="伯", reason="伯爵")
R("Viscounty", "子國", etype="行政區", polity="中世紀西歐封建", register="周封建五等爵",
  level="三級", tier="封爵", reason="子爵領地")
R("Viscount", "子", polity="中世紀西歐封建", register="周封建五等爵",
  level="三級", tier="封爵", var="子爵", reason="子爵")
R("Barony", "男爵領", etype="行政區", polity="中世紀西歐封建", register="周封建五等爵",
  level="三級", tier="封爵", reason="男爵領地")
R("Baron", "男", polity="中世紀西歐封建", register="周封建五等爵",
  level="三級", tier="封爵", var="男爵", reason="男爵")
# 神聖羅馬帝國（周封建五等爵：諸侯共主，如周天子＋諸侯）
_order = 8200
R("Holy Roman Emperor", "皇帝", o="Kaiser", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="中央", tier="中央", var="共主；德意志皇帝", reason="選出之共主，如周天子御諸侯")
R("Prince-elector", "選帝侯", o="Kurfürst", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="中央", tier="封爵", var="選侯", reason="有權選立皇帝之七大諸侯（中國無真正對應，沿用「選帝侯」）")
R("Arch-Chancellor", "大相", o="Erzkanzler", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="中央", tier="中央", var="尚書令；掌璽", reason="美因茨大主教兼任之帝國首相")
R("Imperial Diet", "帝國議會", o="Reichstag", lang="de", etype="機構", polity="神聖羅馬帝國",
  register="周封建五等爵", level="中央", tier="中央", var="諸侯大會", reason="皇帝與諸侯共議之會，如周之會同盟會")
R("Imperial Chamber Court", "帝國樞密法院", o="Reichskammergericht", lang="de", etype="機構",
  polity="神聖羅馬帝國", register="周封建五等爵", level="中央", tier="司法", reason="帝國最高法院")
R("Imperial Circle", "帝國圈", o="Reichskreis", lang="de", etype="行政區", polity="神聖羅馬帝國",
  register="周封建五等爵", level="超一級", tier="地方", var="聯防藩部；帝國大區", reason="數邦國聯合之防務/賦稅大區（共十圈）")
R("Kreisobrist", "圈帥", o="Kreisobrist", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="超一級", tier="軍事", var="藩部都督", reason="帝國圈之軍事統帥")
R("Kingdom (in HRE)", "王國", etype="行政區", polity="神聖羅馬帝國", register="周封建五等爵",
  level="一級", tier="封爵", var="邦國", reason="帝國內之王國（如波希米亞）")
R("Archduchy", "大公國", o="Erzherzogtum", lang="de", etype="行政區", polity="神聖羅馬帝國",
  register="周封建五等爵", level="一級", tier="封爵", reason="奧地利哈布斯堡之領地")
R("Archduke", "大公", o="Erzherzog", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="一級", tier="封爵", reason="大公國之君")
R("Prince-Bishopric", "采邑主教區", o="Hochstift", lang="de", etype="行政區", polity="神聖羅馬帝國",
  register="周封建五等爵", level="一級", tier="封爵", var="主教邦", reason="政教合一之教會諸侯領")
R("Prince-Bishop", "采邑主教", o="Fürstbischof", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="一級", tier="封爵", reason="兼領世俗封地之主教諸侯")
R("Landgrave", "方伯", o="Landgraf", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="二級", tier="封爵", var="伯", root="伯", reason="直屬皇帝之邦伯，如周方伯")
R("Margrave", "邊侯", o="Markgraf", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="二級", tier="封爵", var="邊境伯；藩侯", reason="邊區封侯，如周之邊侯")
R("Free Imperial City", "帝國自由市", o="Reichsstadt", lang="de", etype="行政區", polity="神聖羅馬帝國",
  register="周封建五等爵", level="三級", tier="地方", var="自由邑", reason="直屬皇帝、自治之城市")
R("Imperial Knight", "帝國騎士", o="Reichsritter", lang="de", polity="神聖羅馬帝國", register="周封建五等爵",
  level="三級", tier="封爵", var="帝國之士", reason="直屬皇帝之低階封臣")

# ════════════════════════════════════════════════════════════════════════════
# 商周制（稱謂/部落）— 以色列士師時期
# ════════════════════════════════════════════════════════════════════════════
_order = 8500
R("Shophet", "士師", o="שֹׁפֵט", lang="he", polity="以色列士師時期", register="商周制",
  level="中央", tier="軍事", reason="帶兵先知兼法官之神權部落領袖（使用者定調，仿聖經和合本）")
R("Tribe", "支派", etype="行政區", polity="以色列士師時期", register="商周制",
  level="一級", tier="地方", var="部族", reason="十二支派各據一地，無中央王權")
R("Tribal Elder", "族長", o="זָקֵן", lang="he", polity="以色列士師時期", register="商周制",
  level="一級", tier="地方", var="長老", reason="支派之長老")
R("Clan", "氏族", o="מִשְׁפָּחָה", lang="he", etype="行政區", polity="以色列士師時期",
  register="商周制", level="二級", tier="地方", reason="支派下之宗族")
R("Clan Head", "宗長", polity="以色列士師時期", register="商周制",
  level="二級", tier="地方", var="家長", reason="氏族之長")


# ── 自檢 ────────────────────────────────────────────────────────────────────
def selfcheck() -> bool:
    ok = True
    seen: dict[tuple, int] = {}
    for r in ROWS:
        k = (r["name_english"], r.get("polity"))
        seen[k] = seen.get(k, 0) + 1
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups:
        print(f"⚠️  重複 (name_english, polity)：{dups}"); ok = False
    badv = gn.check_register_valid(ROWS)
    if badv:
        print(f"⚠️  register 非法 {len(badv)} 筆：{[(r['name_english'], r['register']) for r in badv]}")
        ok = False
    badm = gn.check_register_matches_polity(ROWS)
    if badm:
        print(f"⚠️  register↔polity 不符 {len(badm)} 筆：")
        for r in badm:
            print(f"    {r['name_english']} @{r['polity']}: register「{r['register']}」"
                  f" 不在允許集合「{r['_expected_register']}」")
        ok = False
    if ok:
        print("✓ 自檢通過（unique / register 合法 / register↔polity 相符）")
    return ok


def _client():
    import requests  # noqa
    from dotenv import load_dotenv
    load_dotenv(".env")
    url = os.environ["SUPABASE_URL"]; svc = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return url, {"apikey": svc, "Authorization": f"Bearer {svc}"}


def truncate() -> None:
    import requests
    url, h = _client()
    # delete all rows (id is uuid; use a always-true filter)
    r = requests.delete(f"{url}/rest/v1/official_titles?id=not.is.null",
                        headers={**h, "Prefer": "return=minimal"}, timeout=60)
    print(f"  truncate: {r.status_code}")


def upsert(rows: list[dict]) -> bool:
    import requests
    url, h = _client()
    hh = {**h, "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates,return=minimal"}
    B = 50
    for i in range(0, len(rows), B):
        batch = rows[i:i + B]
        r = requests.post(f"{url}/rest/v1/official_titles?on_conflict=name_english,polity",
                          headers=hh, json=batch, timeout=90)
        if r.status_code >= 300:
            print(f"  UPSERT ERROR {r.status_code}: {r.text[:500]}"); return False
        print(f"  ✓ upserted {len(batch)} (rows {i+1}–{i+len(batch)})")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="預覽 + 自檢，不寫 DB")
    ap.add_argument("--replace", action="store_true", help="先清空整表再全量重灌")
    args = ap.parse_args()

    ok = selfcheck()
    print(f"\n共 {len(ROWS)} 筆 official_titles")
    if args.dry or not ok:
        cur = None
        for r in ROWS:
            if r["register"] != cur:
                cur = r["register"]; print(f"── {cur} ──")
            print(f"  {r.get('polity') or '':<18} {r['name_english']:<30}"
                  f" → {r['name_recommended']:<10} ({r.get('admin_level') or ''})")
        if not ok:
            print("\n✗ 自檢未過，未寫 DB。修正後再跑。")
        sys.exit(0 if ok else 1)

    if args.replace:
        truncate()
    if upsert(ROWS):
        print("\nDone.")
