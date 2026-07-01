"""
Seed official_titles for /translation-glossary (「官制與行政區」tab) — HAND-CURATED.

跟 seed_glossary_rulers.py / seed_glossary_places.py 並列、同政策：純人工策展（無 LLM）。
資料來自使用者與 AI 共同推演的「漢譯世界史」官職/行政區對照（使用者逐項討論定調）。

定名規則（見 .claude/skills/translation-glossary/offices_register_blueprint.md）：
  - 共時性：按「社會發展階段＋政治氣質」對到某朝代 register，不按日曆年代。
  - 「總督/行省/副王」是明清 register 的詞，只用在奧斯曼/蒙兀兒/俄/近世殖民帝國。
  - 帝國晚期逐層對到魏晉三級：大區行臺(行臺尚書令)→州(刺史)→郡(太守)。
  - 舊的扁平譯（總督;行省）降到 name_variants 供對照。
  - register 值必須是 ADMIN_REGISTERS 之一；check_register_matches_polity 自檢政權↔register。
  - 中國詞不足可借日/韓/越漢字官職（統監/留守/道…），notes 標明。

【提】= AI 提案、使用者尚未逐項拍板；【核】= 使用者已定調。seed 前請確認 §7 待定項。

Usage:
  python scripts/seed_glossary_offices.py --dry     # 預覽 + 自檢，不寫 DB（預設建議先跑這個）
  python scripts/seed_glossary_offices.py           # upsert 進 Supabase
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
# 4.1 青銅神權（商周制）
# ════════════════════════════════════════════════════════════════════════════
_order = 1000
R("City-state", "方國", etype="行政區", polity="阿卡德帝國", register="商周制",
  level="一級", tier="地方", var="城邦", reason="阿卡德承認蘇美城邦統治權，如商承周邊方國")
R("Ensi", "侯", rom="Ensí", etype="官職", polity="阿卡德帝國", register="商周制",
  level="一級", tier="地方", reason="保留舊城邦統治權的地方領主")
R("Nome", "州", o="Sepat", lang="egy", etype="行政區", polity="古埃及", register="商周制",
  level="一級", tier="地方", var="省", reason="沿尼羅河分佈、歷史悠久穩定的行政區（使用者定調）")
R("Nomarch", "州伯", etype="官職", polity="古埃及", register="商周制",
  level="一級", tier="地方", var="州長；省長", root="伯",
  reason="世襲地方豪族，用「伯」體現封建貴族色彩（使用者定調）")

# ════════════════════════════════════════════════════════════════════════════
# 4.2 軍國擴張（春秋制 / 戰國秦制）
# ════════════════════════════════════════════════════════════════════════════
_order = 2000
R("Babylonian Province", "畿", etype="行政區", polity="古巴比倫", register="春秋制",
  level="一級", tier="地方", reason="巴比倫城富庶精華區；漢摩拉比≈齊桓霸業立法（使用者定調）")
R("Bel Pihati (Babylonian)", "大尹", o="bēl pīhāti", lang="akk", etype="官職",
  polity="新巴比倫帝國", register="春秋制", level="一級", tier="地方", var="省長；總督", root="尹",
  reason="統轄大省/富庶城邦群之一級總管（如「河外 Ebir-nāri」黎凡特大省）；王莽改太守曰大尹、宋亦有大尹，帶南方尹味且高於縣公")
R("Shakin Temi", "縣公", o="šākin ṭēmi", lang="akk", etype="官職", polity="新巴比倫帝國",
  register="春秋制", level="二級", tier="地方", var="令尹；牧",
  reason="城邑之長（巴比倫城等），隸大尹之下；使用者定調用楚職，楚縣之長特稱「公」（葉公/白公），別於中央宰輔令尹")
R("Assyrian Province", "鎮", etype="行政區", polity="新亞述帝國", register="戰國秦制",
  level="一級", tier="軍事", var="行省", root="鎮",
  reason="軍事佔領據點、肅殺氣（使用者定調用「鎮」）")
R("Shaknu", "鎮監", o="šaknu", lang="akk", rom="Bel Pihati", etype="官職",
  polity="新亞述帝國", register="戰國秦制", level="一級", tier="軍事", var="總督；省長", root="鎮",
  reason="佔領軍司令，使用者定「鎮監」（AI 原提鎮守/監軍）")
R("Satrapy", "州", etype="行政區", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="一級", tier="地方", var="行省；大州", root="州",
  reason="一省即一舊王國，規模極大（使用者定調用「州」）")
R("Satrap", "州伯", o="xšaçapāvan", lang="peo", etype="官職",
  polity="阿契美尼德-波斯帝國", register="戰國秦制", level="一級", tier="地方",
  var="總督；省長；方伯", root="伯",
  reason="半獨立土皇帝，對「萬王之王」稱伯（使用者定調州伯；方伯亦可）")
R("King's Eye", "監御史", etype="官職", polity="阿契美尼德-波斯帝國", register="戰國秦制",
  level="監察", tier="中央", var="行人；國王之眼",
  reason="【提】巡視監視省長者，如周之行人／秦之監御史")
R("Strategia", "郡", etype="行政區", polity="塞琉古-希臘帝國", register="戰國秦制",
  level="一級", tier="軍事", var="行省", root="郡",
  reason="希臘化外來軍事殖民區（使用者定調用「郡」）")
R("Strategos", "郡尉", o="στρατηγός", lang="grc", etype="官職",
  polity="塞琉古-希臘帝國", register="戰國秦制", level="一級", tier="軍事", var="將軍；總督", root="郡",
  reason="將軍即行政首長，對「郡」置「尉」，秦式肅殺（使用者定調；亦可作「守」）")

# ════════════════════════════════════════════════════════════════════════════
# 4.3 古典帝國（漢制）— 郡國並行
# ════════════════════════════════════════════════════════════════════════════
_order = 3000
R("Senatorial Province", "行省", etype="行政區", polity="羅馬共和國", register="漢制",
  level="一級", tier="地方", root="行省", reason="已羅馬化富庶區，元老院管轄")
R("Proconsul", "牧", o="pro consule", lang="la", etype="官職", polity="羅馬共和國",
  register="漢制", level="一級", tier="地方", var="總督；地方總督",
  reason="前執政官外放，地位崇高如漢之州牧（使用者定調）")
R("Imperial Province", "行省", etype="行政區", polity="羅馬帝國", register="漢制",
  level="一級", tier="軍事", root="行省", reason="邊境駐軍團之皇帝直轄區")
R("Legatus Augusti", "都護", lang="la", etype="官職", polity="羅馬帝國",
  register="漢制", level="一級", tier="軍事", var="總督；皇帝欽差", root="都護",
  reason="皇帝欽差、統率軍團，如漢之西域都護（使用者定調）")
R("Praefectus Aegypti", "大尹", lang="la", etype="官職", polity="羅馬帝國",
  register="漢制", level="特區", tier="中央", var="總督；埃及長官",
  reason="埃及為皇帝私產，長官如皇家大管家，用「尹」不用「總督」（使用者定調）")
R("Judaea Prefecture", "郡", o="Iudaea", lang="la", etype="行政區", polity="羅馬帝國",
  register="漢制", level="二級", tier="地方", var="猶太行省",
  reason="隸敘利亞大行省之附屬小區，非獨立行省（使用者定調降為「郡」）")
R("Praefectus Iudaeae", "都尉", lang="la", etype="官職", polity="羅馬帝國",
  register="漢制", level="二級", tier="軍事", var="總督；巡撫",
  notes="本丟彼拉多 Pontius Pilate 之職",
  reason="騎士階級、受都護節制、管邊陲小郡，位低於都護（使用者定調都尉）")
R("Client Kingdom", "屬國", etype="行政區", polity="羅馬帝國", register="漢制",
  level="羈縻", tier="地方", reason="名義獨立之緩衝國，Rex→國王；羅馬亦郡國並行如漢")
R("Toparchy", "縣", o="τοπαρχία", lang="grc", etype="行政區", polity="希律猶太王國",
  register="漢制", level="三級", tier="地方", var="邑",
  reason="【提】希律王國內二級單位，收稅徵兵，王國—縣二級制")
R("Ethnarch", "民族大君", o="ἐθνάρχης", lang="grc", etype="官職", polity="希律猶太王國",
  register="漢制", level="羈縻", tier="地方",
  reason="【提】希律死後裂土，如推恩令分封；Tetrarch 分封王另立")
R("Tetrarch", "分封王", o="τετράρχης", lang="grc", etype="官職", polity="希律猶太王國",
  register="漢制", level="羈縻", tier="地方", var="侯",
  reason="【提】四分領地之王，如安提帕領加利利")

# ════════════════════════════════════════════════════════════════════════════
# 4.4 帝國晚期三級制（魏晉制）— 大區行臺→州→郡
# ════════════════════════════════════════════════════════════════════════════
_order = 4000
R("Praetorian Prefecture", "大區行臺", lang="la", etype="行政區", polity="羅馬帝國",
  register="魏晉制", level="一級", tier="地方", var="大區", root="行臺",
  reason="戴克里先後最高行政區，如魏晉行臺（中央派出分部）（使用者定調）")
R("Praetorian Prefect", "行臺尚書令", lang="la", etype="官職", polity="羅馬帝國",
  register="魏晉制", level="一級", tier="中央", var="大區長官；禁衛軍長官", root="行臺",
  reason="皇帝首席副手、總攬軍政財，如行臺尚書令（使用者定調）")
R("Diocese", "州", o="dioecesis", lang="la", etype="行政區", polity="羅馬帝國",
  register="魏晉制", level="二級", tier="地方", var="管區", root="州",
  reason="大區下、行省上之中間層，如魏晉之州（使用者定調）")
R("Vicarius", "刺史", lang="la", etype="官職", polity="羅馬帝國",
  register="魏晉制", level="二級", tier="地方", var="管區長官",
  reason="監察其下數郡，如魏晉刺史（使用者定調）")
R("Late Province", "郡", o="provincia", lang="la", etype="行政區", polity="羅馬帝國",
  register="魏晉制", level="三級", tier="地方", var="行省", root="郡",
  reason="戴克里先切碎後之小行省，實質如郡，故改譯「郡」（使用者定調）")
R("Rector", "太守", lang="la", etype="官職", polity="羅馬帝國",
  register="魏晉制", level="三級", tier="地方", var="行省總督；Praeses",
  reason="基層行省長官，如漢晉太守（使用者定調）")

# ════════════════════════════════════════════════════════════════════════════
# 4.5 中世紀軍區/宗教帝國（唐制）
# ════════════════════════════════════════════════════════════════════════════
_order = 5000
R("Theme", "軍道", o="θέμα", lang="grc", etype="行政區", polity="拜占庭帝國",
  register="唐制", level="一級", tier="軍事", var="軍區", root="道",
  reason="軍區制，士兵屯田世襲，如中晚唐藩鎮之道（使用者定調）")
R("Byzantine Strategos", "節度使", o="στρατηγός", lang="grc", etype="官職",
  polity="拜占庭帝國", register="唐制", level="一級", tier="軍事", var="軍區將軍",
  reason="軍政一把抓，與唐節度使同時（7-8c）為邊防演化，功能全同（使用者定調）")
R("Wilayah", "道", o="ولاية", lang="ar", etype="行政區", polity="阿拔斯-阿拉伯帝國",
  register="唐制", level="一級", tier="地方", var="行省；轄區", root="道",
  reason="遼闊行省，如唐之道（使用者定調）")
R("Amir", "經略使", o="أمير", lang="ar", rom="Wali", etype="官職",
  polity="阿拔斯-阿拉伯帝國", register="唐制", level="一級", tier="軍事",
  var="埃米爾；總督；提督",
  reason="軍政合一、邊疆經營，如唐宋經略安撫使；初期征服可作都護（使用者定調）")
R("Vizier", "宰相", o="وزير", lang="ar", etype="官職", polity="阿拔斯-阿拉伯帝國",
  register="唐制", level="中央", tier="中央", reason="波斯化文官體系之首")
# 東羅馬晚期中央文官層（宋制）— 拜占庭跨唐(軍區)/宋(文官) 兩制
R("Kephale", "知州", o="κεφαλή", lang="grc", etype="官職", polity="拜占庭帝國",
  register="宋制", level="一級", tier="地方", var="總督；城市長官",
  reason="晚期（帕列奧列格）中央派任之府/城長官，如宋「知某州事」")
R("Logothete", "三司使", o="λογοθέτης", lang="grc", etype="官職", polity="拜占庭帝國",
  register="宋制", level="中央", tier="中央", var="度支使；大臣",
  reason="掌財政之中央大臣（logothetes tou genikou），如宋三司使")

# ════════════════════════════════════════════════════════════════════════════
# 4.5b 游牧/征服帝國（遼金元制）— 南北面雙軌、十進位軍事編制、達魯花赤
# ════════════════════════════════════════════════════════════════════════════
_order = 5500
R("Vassal Kingdom", "屬國", etype="行政區", polity="安息-帕提亞帝國", register="遼金元制",
  level="羈縻", tier="地方", reason="安息治希臘城市(南面)＋伊朗部族(北面)雙軌，多封屬國")
R("Marzban", "招討使", o="marzbān", lang="pal", etype="官職", polity="安息-帕提亞帝國",
  register="遼金元制", level="一級", tier="軍事", var="邊境總督；馬爾茲班",
  reason="邊疆軍事鎮守者，如遼宋招討使")
R("Iqta", "食邑", o="إقطاع", lang="ar", etype="行政區", polity="塞爾柱-突厥帝國",
  register="遼金元制", level="一級", tier="軍事", var="采邑；封地",
  reason="以軍事義務換取之土地采邑，如遼金元/封建食邑")
R("Khanate", "汗國", o="ᠬᠠᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="帝國", tier="地方", reason="大汗分封諸子之汗國（伊兒/金帳/察合台）")
R("Great Khan", "大汗", o="ᠶᠡᠺᠡ ᠬᠠᠭᠠᠨ", lang="mn", rom="Yeke Khagan", etype="官職",
  polity="蒙古帝國", register="遼金元制", level="中央", tier="中央", var="可汗",
  reason="草原共主，如遼金元之可汗/大汗")
R("Darughachi", "達魯花赤", o="ᠳᠠᠷᠤᠭᠠᠴᠢ", lang="mn", etype="官職", polity="蒙古帝國",
  register="遼金元制", level="一級", tier="地方", var="監臨官；鎮守官",
  reason="蒙古派駐地方之最高監臨官，元代本即漢譯「達魯花赤」")
R("Tumen", "萬戶", o="ᠲᠦᠮᠡᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="一級", tier="軍事", var="土綿",
  reason="十進位軍事編制（一萬戶/兵），如元萬戶")
R("Minghan", "千戶", o="ᠮᠢᠩᠭᠠᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="二級", tier="軍事", reason="千戶編制，如元千戶／金猛安")
R("Jaghun", "百戶", o="ᠵᠠᠭᠤᠨ", lang="mn", etype="行政區", polity="蒙古帝國", register="遼金元制",
  level="三級", tier="軍事", reason="百戶編制，如元百戶／金謀克")
# 中世紀西歐封建五等爵（周封建五等爵；傳統譯已 register-正確）
R("Duke", "公", lang="la", etype="封爵", polity="中世紀西歐封建", register="周封建五等爵",
  tier="封爵", reason="五等爵之首，傳統譯已正確")
R("Marquis", "侯", etype="封爵", polity="中世紀西歐封建", register="周封建五等爵",
  tier="封爵", var="侯爵；邊侯", reason="邊境封侯")
R("Count", "伯", lang="la", rom="Comes", etype="封爵", polity="中世紀西歐封建",
  register="周封建五等爵", tier="封爵", var="伯爵", root="伯")
R("Viscount", "子", etype="封爵", polity="中世紀西歐封建", register="周封建五等爵",
  tier="封爵", var="子爵")
R("Baron", "男", etype="封爵", polity="中世紀西歐封建", register="周封建五等爵",
  tier="封爵", var="男爵")

# ════════════════════════════════════════════════════════════════════════════
# 4.6 近世火藥帝國＋殖民（明清制）— 「總督/行省/副王」在此才恰當
# ════════════════════════════════════════════════════════════════════════════
_order = 6000
R("Eyalet", "總督區", o="ایالت", lang="ota", etype="行政區", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="一級", tier="地方", var="行省",
  reason="奧斯曼一級軍事封建區（使用者定調）")
R("Beylerbey", "總督", o="بیلربیی", lang="ota", etype="官職", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="一級", tier="地方", var="眾貝伊之貝伊",
  reason="一級長官，明清 register 內「總督」恰當（使用者定調）")
R("Sanjak", "旗", o="سنجاق", lang="ota", etype="行政區", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="二級", tier="軍事", var="縣",
  reason="Sanjak 原意旗幟，與清八旗同軍事邏輯（使用者定調）")
R("Sanjak-bey", "旗主", o="سنجاق بیی", lang="ota", etype="官職", polity="鄂圖曼-土耳其帝國",
  register="明清制", level="二級", tier="軍事", var="佐領；旗長",
  reason="軍事動員基本單位之長，如清旗主/佐領（使用者定調）")
R("Subah", "省", lang="fa", etype="行政區", polity="蒙兀兒帝國", register="明清制",
  level="一級", tier="地方", reason="【提】官僚化一級行政區")
R("Subahdar", "提督", lang="fa", etype="官職", polity="蒙兀兒帝國", register="明清制",
  level="一級", tier="軍事", var="總督",
  reason="【提】掌一省軍政，用「提督」以別於奧斯曼總督")
R("Viceroyalty", "副王區", o="Virreinato", lang="es", etype="行政區",
  polity="西班牙帝國", register="明清制", level="一級", tier="地方",
  reason="西班牙最高殖民區，國王替身之轄地（使用者定調）")
R("Viceroy", "副王", o="Virrey", lang="es", etype="官職", polity="西班牙帝國",
  register="明清制", level="一級", tier="地方", var="總督",
  reason="Viceroy 原意國王替身，如親王就藩（使用者定調）")
R("Captaincy General", "都督府", o="Capitanía General", lang="es", etype="行政區",
  polity="西班牙帝國", register="明清制", level="二級", tier="軍事",
  reason="戰略要地軍管區（如古巴/菲律賓）（使用者定調）")
R("Captain General", "提督", o="Capitán General", lang="es", etype="官職",
  polity="西班牙帝國", register="明清制", level="二級", tier="軍事", var="都督;總督",
  reason="鎮守戰略要地之軍事統帥（使用者定調）")
R("Corregidor", "道臺", lang="es", etype="官職", polity="西班牙帝國", register="明清制",
  level="三級", tier="地方", reason="【提】地方行政官")
R("Governor-General", "大總督", etype="官職", polity="大英帝國", register="明清制",
  level="帝國", tier="地方", var="總督；副王",
  reason="統轄聯邦/大陸領地、下有數省長，如兩廣總督（使用者定調）")
R("Colonial Governor", "總督", etype="官職", polity="大英帝國", register="明清制",
  level="一級", tier="地方", notes="如香港總督、新加坡總督",
  reason="直轄倫敦、獨當一面之最高長官（使用者定調）")
R("Lieutenant Governor", "巡撫", etype="官職", polity="大英帝國", register="明清制",
  level="二級", tier="地方", var="省督", reason="上有大總督管轄，如加拿大各省督（使用者定調）")
R("Résident supérieur", "統監", lang="fr", etype="官職", polity="法蘭西殖民帝國",
  register="明清制", level="保護國", tier="地方", var="高級駐紮官；駐紮大臣",
  reason="保護國高級駐紮官（名義顧問實太上皇），借日治朝鮮「統監」（使用者定調；中國詞不足借日）")
R("Gouverneur général", "大總督", lang="fr", etype="官職", polity="法蘭西殖民帝國",
  register="明清制", level="聯邦", tier="地方",
  reason="殖民聯邦最高長官，如法屬印度支那大總督（使用者定調）")

# 稱謂類（跨 register）
_order = 7000
R("Shophet", "士師", o="שֹׁפֵט", lang="he", etype="官職", polity="以色列士師時期",
  register="商周制", level="羈縻", tier="軍事",
  reason="帶兵先知兼法官之神權部落領袖（使用者定調，仿聖經和合本）")


# ── 自檢 ────────────────────────────────────────────────────────────────────
def selfcheck() -> bool:
    ok = True
    # 1) unique (name_english, polity)
    seen: dict[tuple, int] = {}
    for r in ROWS:
        k = (r["name_english"], r.get("polity"))
        seen[k] = seen.get(k, 0) + 1
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups:
        print(f"⚠️  重複 (name_english, polity)：{dups}"); ok = False
    # 2) register 合法
    badv = gn.check_register_valid(ROWS)
    if badv:
        print(f"⚠️  register 非法 {len(badv)} 筆：{[(r['name_english'], r['register']) for r in badv]}")
        ok = False
    # 3) register ↔ polity 相符
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


def upsert(rows: list[dict]) -> bool:
    import requests
    from dotenv import load_dotenv
    load_dotenv(".env")
    url = os.environ["SUPABASE_URL"]
    svc = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": svc, "Authorization": f"Bearer {svc}",
         "Content-Type": "application/json",
         "Prefer": "resolution=merge-duplicates,return=minimal"}
    B = 50
    for i in range(0, len(rows), B):
        batch = rows[i:i + B]
        r = requests.post(
            f"{url}/rest/v1/official_titles?on_conflict=name_english,polity",
            headers=h, json=batch, timeout=90)
        if r.status_code >= 300:
            print(f"  UPSERT ERROR {r.status_code}: {r.text[:500]}"); return False
        print(f"  ✓ upserted {len(batch)} (rows {i+1}–{i+len(batch)})")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="預覽 + 自檢，不寫 DB")
    args = ap.parse_args()

    ok = selfcheck()
    print(f"\n共 {len(ROWS)} 筆 official_titles")
    if args.dry or not ok:
        for r in ROWS:
            print(f"  [{r['sort_order']:>4}] {r['register'] or '?':<7}"
                  f" {r.get('polity') or '':<16} {r['name_english']:<24}"
                  f" → {r['name_recommended']:<8} ({r.get('admin_level') or ''})")
        if not ok:
            print("\n✗ 自檢未過，未寫 DB。修正後再跑。")
        sys.exit(0 if ok else 1)

    if upsert(ROWS):
        print("\nDone.")
