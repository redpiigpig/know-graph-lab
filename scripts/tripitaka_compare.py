"""異譯對讀：同一部經的多個漢譯本＋梵／巴／藏原典，按義段並排（像聖經多譯本對照）。

佛典沒有跨語言的「節」，所以對齊單位是本組自訂的**義段**（序分、照見五蘊、色空不異…），
每一組在 SETS 裡明列。每個本子只給「第幾義段從哪幾個字起」的切點，腳本照切：

  🚨 切出來的每一刀都是原文——不增字、不漏字、不改字。閘：
     1. 每個切點都要在上一刀之後找得到（找不到＝原文與記憶不符，整組拒絕）
     2. 各本切完重新接起來，必須與原文一字不差
     3. 義段在各本內必須照順序、不重複（同源異流但不會倒序）
  某本沒有的義段就留空（例如短本心經沒有序分），頁面顯示「—」，不硬湊。

輸出 public/content/tripitaka/compare/<slug>.json ＋ index.json（頁面 /tripitaka/compare/<slug>）。

  python -X utf8 scripts/tripitaka_compare.py            # 全部重建
  python -X utf8 scripts/tripitaka_compare.py heart-sutra
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIP = Path("G:/我的雲端硬碟/資料/知識圖工作室/_tripitaka")
OUT = ROOT / "public/content/tripitaka/compare"

# ── 各組定義 ────────────────────────────────────────────────────────────────
# version.src:
#   {"work": "T0250", "start": "觀世音菩薩"}        漢文：該部正文，從 start 那幾個字起
#   {"orig": "T0251", "lang": "sa"}                   原典：掛在該部的 orig.json 那一份
# version.cuts: [(義段, 起頭幾個字)] 或原典逐行 [(義段, 行號)]
SETS: dict[str, dict] = {}

SETS["heart-sutra"] = {
    "title": "般若波羅蜜多心經",
    "family": "sa",
    "extra_works": ["DKtoh0021"],
    "intro": (
        "梵本有廣、略兩本：略本只有正宗分（羅什、玄奘所據），廣本多了序分與流通分"
        "（法月以下五家與藏譯所據）。某本沒有的義段留空，不是漏收。"
    ),
    "units": [
        ("u00", "題名・歸敬"),
        ("u01", "如是我聞"),
        ("u02", "說法處與聽眾"),
        ("u03", "世尊入定"),
        ("u03b", "觀自在請說・佛許（法月本獨有）"),
        ("u04", "觀自在照見五蘊皆空"),
        ("u05", "舍利子請問"),
        ("u06", "觀自在答：當觀五蘊自性空"),
        ("u07", "色空不異・色即是空"),
        ("u08", "受想行識亦復如是"),
        ("u09", "諸法空相：不生不滅"),
        ("u10", "空中無五蘊・十二處"),
        ("u11", "無十八界"),
        ("u12", "無十二緣起"),
        ("u13", "無四諦・無智無得"),
        ("u14", "菩薩依般若・究竟涅槃"),
        ("u15", "三世諸佛依般若得菩提"),
        ("u16", "般若是大神咒"),
        ("u17", "故說咒"),
        ("u18", "咒語"),
        ("u19", "菩薩應如是學"),
        ("u20", "世尊出定讚歎"),
        ("u21", "大眾歡喜奉行"),
        ("u22", "尾題・譯記"),
    ],
    "versions": [
        {"id": "sa", "lang": "sa", "label": "梵本（略本）", "who": "GRETIL 校訂本",
         "src": {"orig": "T0251", "lang": "sa"},
         "cuts": [("u00", "Prajñāpāramitā-hṛdaya-sūtra"), ("u04", "Ārya Āvalokiteśvaro"),
                  ("u07", "Iha Śāriputra rūpaṃ"), ("u08", "Evam eva vedanā"),
                  ("u09", "Iha Śāriputra sarva-dharmāḥ"), ("u10", "Tasmāc Chāriputra śūnyatāyāṃ"),
                  ("u11", "na cakṣur-dhātur"), ("u12", "n'āvidyā n'āvidyā"),
                  ("u13", "na duḥkha-samudaya"), ("u14", "Tasmāc Chāriputra aprāptitvād"),
                  ("u15", "Tradhva-vyavasthitāḥ"), ("u16", "Tasmāj jñātavyaṃ"),
                  ("u17", "Prajñāpāramitāyām ukto"), ("u18", "Oṃ gate"), ("u22", "Ity ārya")]},
        {"id": "bo", "lang": "bo", "label": "藏譯（廣本）", "who": "無垢友、寶軍譯・Toh 21",
         "src": {"orig": "T0251", "lang": "bo"},
         "lines": [("u00", 0), ("u01", 2), ("u02", 3), ("u03", 4), ("u04", 5), ("u05", 6),
                   ("u06", 8), ("u07", 11), ("u08", 14), ("u09", 15), ("u10", 17), ("u11", 18),
                   ("u12", 19), ("u13", 20), ("u14", 21), ("u15", 23), ("u16", 24), ("u17", 26),
                   ("u18", 27), ("u19", 28), ("u20", 29), ("u21", 33), ("u22", 34)]},
        {"id": "T0250", "lang": "lzh", "label": "羅什本", "who": "鳩摩羅什譯・402–413 年",
         "src": {"work": "T0250", "start": "觀世音菩薩行深"},
         "cuts": [("u04", "觀世音菩薩行深"), ("u07", "「舍利弗！色空故"),
                  ("u08", "受、想、行、識亦如是"), ("u09", "「舍利弗！是諸法空相"),
                  ("u10", "是故空中無色"), ("u11", "無眼界"), ("u12", "無無明"),
                  ("u13", "無苦、集"), ("u14", "「以無所得故"), ("u15", "三世諸佛"),
                  ("u16", "「故知般若"), ("u17", "故說般若波羅蜜呪"), ("u18", "「竭帝")]},
        {"id": "T0251", "lang": "lzh", "label": "玄奘本", "who": "玄奘譯・649 年",
         "src": {"work": "T0251", "start": "觀自在菩薩行深"},
         "cuts": [("u04", "觀自在菩薩行深"), ("u07", "「舍利子！色不異空"),
                  ("u08", "受、想、行、識，亦復如是"), ("u09", "「舍利子！是諸法空相"),
                  ("u10", "是故，空中無色"), ("u11", "無眼界"), ("u12", "無無明"),
                  ("u13", "無苦、集"), ("u14", "「以無所得故"), ("u15", "三世諸佛"),
                  ("u16", "「故知般若"), ("u17", "故說般若波羅蜜多咒"), ("u18", "「揭帝")]},
        {"id": "T0252", "lang": "lzh", "label": "法月本", "who": "法月譯・738 年",
         "src": {"work": "T0252", "start": "如是我聞"},
         "cuts": [("u01", "如是我聞"), ("u02", "一時佛在王舍大城"),
                  ("u03b", "爾時觀自在菩薩摩訶薩在彼敷坐"), ("u04", "於是觀自在菩薩摩訶薩蒙佛聽許"),
                  ("u05", "彼了知五蘊自性皆空"), ("u06", "於斯告舍利弗"), ("u07", "色性是空"),
                  ("u08", "受、想、行、識亦復如是"), ("u09", "舍利子！是諸法空相"),
                  ("u10", "是故空中無色"), ("u11", "無眼界"), ("u12", "無無明"),
                  ("u13", "無苦、集"), ("u14", "以無所得故"), ("u15", "三世諸佛"),
                  ("u16", "故知般若"), ("u17", "故說般若波羅蜜多呪"), ("u18", "「揭諦"),
                  ("u21", "佛說是經已")]},
        {"id": "T0253", "lang": "lzh", "label": "般若利言本", "who": "般若、利言等譯・790 年",
         "src": {"work": "T0253", "start": "如是我聞"},
         "cuts": [("u01", "如是我聞"), ("u02", "一時佛在王舍城"), ("u03", "時佛世尊即入三昧"),
                  ("u04", "爾時眾中有菩薩摩訶薩"), ("u05", "即時舍利弗承佛威力"),
                  ("u06", "爾時觀自在菩薩摩訶薩告"), ("u07", "舍利子！色不異空"),
                  ("u08", "受、想、行、識亦復如是"), ("u09", "舍利子！是諸法空相"),
                  ("u10", "是故空中無色"), ("u11", "無眼界"), ("u12", "無無明"),
                  ("u13", "無苦、集"), ("u14", "以無所得故"), ("u15", "三世諸佛"),
                  ("u16", "故知般若"), ("u17", "故說般若波羅蜜多呪"), ("u18", "「櫱諦"),
                  ("u19", "「如是，舍利弗"), ("u20", "即時，世尊從廣大"),
                  ("u21", "爾時世尊說是語已")]},
        {"id": "T0254", "lang": "lzh", "label": "智慧輪本", "who": "智慧輪譯・約 850 年",
         "src": {"work": "T0254", "start": "如是我聞"},
         "cuts": [("u01", "如是我聞"), ("u02", "一時薄誐梵"), ("u03", "爾時，世尊入三摩地"),
                  ("u04", "時眾中有一菩薩摩訶薩"), ("u05", "即時具壽舍利子"),
                  ("u06", "爾時，觀世音自在菩薩摩訶薩告"), ("u07", "舍利子！色空，空性見色"),
                  ("u08", "受、想、行、識亦復如是"), ("u09", "舍利子！是諸法性相空"),
                  ("u10", "是故空中無色"), ("u11", "無眼界"), ("u12", "無無明"),
                  ("u13", "無苦、集"), ("u14", "以無所得故"), ("u15", "三世諸佛"),
                  ("u16", "故知般若"), ("u17", "故說般若波羅蜜多真言"), ("u18", "「唵"),
                  ("u19", "「如是，舍利子"), ("u20", "爾時，世尊從三摩地"),
                  ("u21", "爾時世尊如是說已")]},
        {"id": "T0255", "lang": "lzh", "label": "法成本", "who": "法成譯（敦煌）・約 856 年",
         "src": {"work": "T0255", "start": "如是我聞"},
         "cuts": [("u01", "如是我聞"), ("u02", "一時薄伽梵"), ("u03", "爾時，世尊等入"),
                  ("u04", "復於爾時"), ("u05", "時，具壽舍利子"), ("u06", "觀自在菩薩摩訶薩答"),
                  ("u07", "色即是空，空即是色。色不異空"), ("u08", "如是受、想、行、識"),
                  ("u09", "是故舍利子！一切法空性無相"), ("u10", "舍利子！是故爾時空性之中"),
                  ("u11", "無眼界"), ("u12", "無無明"), ("u13", "無苦、集"),
                  ("u14", "是故舍利子！以無所得故"), ("u15", "三世一切諸佛"),
                  ("u16", "舍利子！是故當知"), ("u17", "故知般若波羅蜜多是祕密咒"),
                  ("u18", "「峩帝"), ("u19", "「舍利子！菩薩摩訶薩應如是修學"),
                  ("u20", "爾時，世尊從彼定起"), ("u21", "時薄伽梵說是語已")]},
        {"id": "T0257", "lang": "lzh", "label": "施護本", "who": "施護譯・約 1000 年",
         "src": {"work": "T0257", "start": "如是我聞"},
         "cuts": [("u01", "如是我聞"), ("u02", "一時，世尊在王舍城"), ("u03", "爾時，世尊即入"),
                  ("u04", "時，觀自在菩薩摩訶薩在佛會中"), ("u05", "爾時，尊者舍利子"),
                  ("u06", "時，觀自在菩薩摩訶薩告"), ("u07", "所謂即色是空"),
                  ("u08", "受、想、行、識，亦復如是"), ("u09", "「舍利子！此一切法"),
                  ("u10", "舍利子！是故，空中無色"), ("u11", "無眼界無眼識界"),
                  ("u12", "無無明無無明盡"), ("u13", "無苦、集"), ("u14", "「舍利子！由是無得故"),
                  ("u15", "所有三世諸佛"), ("u16", "「是故，應知"),
                  ("u17", "我今宣說般若波羅蜜多大明曰"), ("u18", "「怛"),
                  ("u19", "「舍利子！諸菩薩摩訶薩，若能誦"), ("u20", "爾時，世尊從三摩地"),
                  ("u21", "佛說此經已")]},
    ],
}


SETS["dhammacakka"] = {
    "title": "轉法輪經",
    "family": "pi",
    "intro": (
        "佛陀初轉法輪。巴利 SN 56.11 與漢譯南傳是「一諦講完三轉再講下一諦」，"
        "雜阿含 379 與義淨本是「四諦先示轉一輪、再勸轉一輪、再證轉一輪」，"
        "所以「三轉十二行」只立一個義段，段內各依原本次第。"
        "巴利與漢譯南傳的「歡喜奉行」在憍陳如得法眼之前，安世高本先說四諦內容才定義各諦——"
        "這幾處是原典本身的次第，照原樣保留。"
    ),
    "units": [
        ("p00", "經題"),
        ("p01", "如是我聞"),
        ("p02", "說法處：鹿野苑"),
        ("p02b", "自然法輪飛來（安世高本獨有）"),
        ("p03", "告五比丘"),
        ("p04", "出家者不應親近二邊"),
        ("p05", "中道・八正道"),
        ("p06", "四聖諦的內容"),
        ("p07", "三轉十二行：示轉・勸轉・證轉"),
        ("p10", "未淨則不自稱成覺"),
        ("p11", "已淨故自證菩提"),
        ("p12", "解脫智見：不受後有"),
        ("p13", "憍陳如得法眼淨"),
        ("p14", "阿若憍陳如得名"),
        ("p15", "諸天展轉傳唱"),
        ("p16", "大千震動・光明普照"),
        ("p17", "經名由來・總結"),
        ("p18", "歡喜奉行"),
    ],
    "versions": [
        {"id": "pi", "lang": "pi", "label": "巴利 SN 56.11", "who": "Mahāsaṅgīti 本・SuttaCentral",
         "src": {"orig": "T0099", "lang": "pi", "ref": "SN 56.11"}, "reorder": True,
         "cuts": [("p00", "Saṁyutta Nikāya 56.11"), ("p02", "Ekaṁ samayaṁ"), ("p03", "Tatra kho bhagavā"),
                  ("p04", "“Dveme"), ("p05", "Ete kho, bhikkhave, ubho ante"),
                  ("p06", "Idaṁ kho pana, bhikkhave, dukkhaṁ"), ("p07", "‘Idaṁ dukkhaṁ ariyasaccan’ti"),
                  ("p10", "Yāvakīvañca"), ("p11", "Yato ca kho me"), ("p12", "Ñāṇañca pana"),
                  ("p18", "Idamavoca"), ("p13", "Imasmiñca"), ("p15", "Pavattite ca pana"),
                  ("p16", "Itiha tena"), ("p14", "Atha kho bhagavā imaṁ udānaṁ")]},
        {"id": "zh-nan", "lang": "lzh", "label": "漢譯南傳", "who": "元亨寺版・N18（譯自巴利）",
         "src": {"orig": "T0099", "lang": "zh-nan", "ref": "SN 56.11", "drop_numerals": True},
         "reorder": True,
         "cuts": [("p00", "〔一一〕"), ("p01", "如是我聞"), ("p02", "一時，世尊住"),
                  ("p03", "於此處，世尊言五比丘"), ("p04", "「諸比丘！出家者"),
                  ("p05", "諸比丘！如來捨此二邊"), ("p06", "諸比丘！苦聖諦者，即是此，謂"),
                  ("p07", "諸比丘！苦聖諦者，即是此，於先前"), ("p10", "諸比丘！我於四聖諦以如是"),
                  ("p11", "諸比丘！然而我於此四聖諦"), ("p12", "又，我智生與見"),
                  ("p18", "世尊如是說示已"), ("p13", "又說示此教時"), ("p15", "世尊轉如是法輪時"),
                  ("p16", "如是於其剎那"), ("p14", "時，世尊稱讚而曰")]},
        {"id": "SA379", "lang": "lzh", "label": "雜阿含 379", "who": "求那跋陀羅譯・435–443 年",
         "src": {"work": "T0099", "node": "（三七九）", "start": "如是我聞"},
         "cuts": [("p01", "如是我聞"), ("p02", "一時，佛住波羅㮈"), ("p03", "爾時，世尊告五比丘"),
                  ("p07", "「此苦聖諦，本所未曾聞法"), ("p10", "「諸比丘！我於此四聖諦三轉十二行不生"),
                  ("p11", "我已於四聖諦三轉十二行生"), ("p13", "爾時，世尊說是法時"),
                  ("p14", "爾時，世尊告尊者憍陳如"), ("p15", "尊者阿若拘隣知法已"),
                  ("p17", "世尊於波羅㮈國仙人住處鹿野苑中轉法輪"), ("p18", "佛說此經已")]},
        {"id": "T0109", "lang": "lzh", "label": "安世高本", "who": "安世高譯《轉法輪經》・約 150 年",
         "src": {"work": "T0109", "start": "聞如是"}, "reorder": True,
         "cuts": [("p01", "聞如是"), ("p02", "一時，佛在波羅㮈國鹿野樹下坐"), ("p02b", "於是有自然法輪"),
                  ("p03", "於是，佛告諸比丘"), ("p04", "世間有二事墮邊行"), ("p05", "若此比丘不念貪欲"),
                  ("p06", "若諸比丘本末聞道"), ("p07", "「又是，比丘！苦為真諦"),
                  ("p10", "是為四諦三轉合十二事"), ("p11", "一切世間諸天人民"), ("p12", "是生後不復有"),
                  ("p13", "佛說是時"), ("p15", "眾祐法輪聲三轉"), ("p16", "爾時，佛界三千"),
                  ("p17", "是為佛眾祐"), ("p18", "佛說是已")]},
        {"id": "T0110", "lang": "lzh", "label": "義淨本", "who": "義淨譯《三轉法輪經》・710 年",
         "src": {"work": "T0110", "start": "如是我聞"},
         "cuts": [("p01", "如是我聞"), ("p02", "一時，薄伽梵"), ("p03", "爾時，世尊告五苾芻"),
                  ("p07", "「汝等苾芻！此苦聖諦，於所聞法"), ("p10", "「汝等苾芻！若我於此四聖諦"),
                  ("p11", "「汝等苾芻！由我於此"), ("p13", "爾時世尊說是法時"), ("p14", "佛告憍陳如"),
                  ("p15", "是時地居藥叉"), ("p17", "因名此經為三轉法輪"), ("p18", "時五苾芻")]},
    ],
}


SETS["samdhinirmocana-1"] = {
    "title": "解深密經・序品與離言無二",
    "family": "bo",
    "extra_works": ["DKtoh0106"],
    "intro": (
        "梵本已佚，藏譯（德格版 Toh 106）是現存最完整的原典層。此組取序分與第一品"
        "（如理請問菩薩問「一切法無二」）——玄奘本併入〈勝義諦相品〉開頭，流支本為〈善問菩薩問品〉，"
        "真諦《解節經》為〈不可言無二品〉。真諦把有為、無為譯作「所作、非所作」，"
        "說法處也在耆闍崛山，不在寶莊嚴宮殿。藏、英兩欄取自 84000 翻譯記憶，逐句對齊。"
    ),
    "units": [
        ("s00", "經題・歸敬"),
        ("s01", "如是我聞"),
        ("s02", "說法處"),
        ("s03", "佛的功德"),
        ("s04", "聲聞眾"),
        ("s05", "菩薩眾"),
        ("s06", "如理請問發問：一切法無二"),
        ("s07", "答：有為、無為皆非有為非無為"),
        ("s08", "再問其故"),
        ("s09", "「有為」是假施設的言說"),
        ("s10", "「無為」亦是假施設的言說"),
        ("s11", "三問：聖者如何為離言者立名"),
        ("s12", "幻師喻：愚者執以為實"),
        ("s13", "幻師喻：智者知其是幻"),
        ("s14", "合法：凡夫執有為無為"),
        ("s15", "合法：聖者如實了知"),
        ("s16", "結：聖者為他假立名想"),
        ("s17", "偈頌"),
        ("s18", "品尾題"),
    ],
    "versions": [
        {"id": "bo", "lang": "bo", "label": "藏譯", "who": "德格版 Toh 106・84000 翻譯記憶",
         "src": {"tmx": "toh106", "side": "bo", "from": 0, "to": 66},
         "lines": [("s00", 0), ("s01", 2), ("s02", 3), ("s03", 9), ("s04", 14), ("s05", 18),
                   ("s06", 19), ("s07", 22), ("s08", 25), ("s09", 27), ("s10", 34), ("s11", 41),
                   ("s12", 42), ("s13", 47), ("s14", 51), ("s15", 54), ("s16", 59), ("s17", 60),
                   ("s18", 65)]},
        {"id": "en", "lang": "en", "label": "84000 英譯", "who": "譯自藏譯・與藏文逐句對齊",
         "src": {"tmx": "toh106", "side": "en", "from": 0, "to": 66},
         "lines": [("s00", 0), ("s01", 2), ("s02", 3), ("s03", 9), ("s04", 14), ("s05", 18),
                   ("s06", 19), ("s07", 22), ("s08", 25), ("s09", 27), ("s10", 34), ("s11", 41),
                   ("s12", 42), ("s13", 47), ("s14", 51), ("s15", 54), ("s16", 59), ("s17", 60),
                   ("s18", 65)]},
        {"id": "T0675", "lang": "lzh", "label": "流支本", "who": "菩提流支譯《深密解脫經》・514 年",
         "src": {"work": "T0675", "nodes": ["序品第一", "聖者善問菩薩問品第二"], "start": "歸命釋迦牟尼佛"},
         "cuts": [("s00", "歸命釋迦牟尼佛"), ("s01", "如是我聞"), ("s02", "一時婆伽婆住法界殿"),
                  ("s03", "諸佛如來善覺所覺"), ("s04", "與諸無量聲聞眾俱"), ("s05", "時諸無量大菩薩眾"),
                  ("s06", "爾時，婆伽婆百千萬"), ("s07", "爾時，深密解脫菩薩告善問菩薩言"),
                  ("s08", "善問菩薩言：「佛子！云何有為法"),
                  ("s09", "深密解脫菩薩言：「善男子！言有為法者"),
                  ("s10", "善男子！言無為者，惟是如來名字說法"),
                  ("s11", "善問菩薩言：「佛子！云何彼事"), ("s12", "深密解脫菩薩言：「善男子！譬如幻師"),
                  ("s13", "「善男子！復有智慧非愚癡者"), ("s14", "「善男子！凡夫眾生未得"),
                  ("s15", "「善男子！復有眾生非是愚癡"), ("s16", "「善男子！如是彼事"),
                  ("s17", "爾時，深密解脫菩薩而說偈言")]},
        {"id": "T0677", "lang": "lzh", "label": "真諦本", "who": "真諦譯《解節經》・約 560 年",
         "src": {"work": "T0677", "node": "不可言無二品第一", "start": "如是我聞"},
         "cuts": [("s01", "如是我聞"), ("s02", "一時佛婆伽婆，住王舍城耆闍崛山"),
                  ("s04", "與大比丘眾九萬九千人俱"), ("s05", "復有菩薩摩訶薩無量百千"),
                  ("s06", "爾時如理正聞菩薩，問能解"), ("s07", "能解甚深義節菩薩言：「善男子！是一切法"),
                  ("s08", "如理正聞菩薩問言"), ("s09", "能解甚深義節菩薩言：「善男子！所作者"),
                  ("s10", "「善男子！非所作者，此是大師正教言句"), ("s12", "「善男子！如巧幻師"),
                  ("s13", "若有諸人——非嬰兒、凡夫及愚癡邪智"), ("s14", "「善男子！如此嬰兒、凡夫"),
                  ("s15", "「若有諸人——非嬰兒、凡夫——已見真實"), ("s16", "「善男子！如是聖人由聖知見"),
                  ("s17", "爾時能解甚深義節菩薩，即說偈言")]},
        {"id": "T0676", "lang": "lzh", "label": "玄奘本", "who": "玄奘譯《解深密經》・647 年",
         "src": {"work": "T0676", "nodes": ["序品第一", "解深密經勝義諦相品第二"],
                 "start": "如是我聞", "end": "爾時，法涌菩薩"},
         "cuts": [("s01", "如是我聞"), ("s02", "一時，薄伽梵住最勝光曜"), ("s03", "是薄伽梵最清淨覺"),
                  ("s04", "與無量大聲聞眾俱"), ("s05", "復有無量菩薩摩訶薩"),
                  ("s06", "爾時，如理請問菩薩摩訶薩，即於佛前"),
                  ("s07", "解甚深義密意菩薩告如理請問菩薩曰"), ("s08", "如理請問菩薩復問"),
                  ("s09", "解甚深義密意菩薩謂如理請問菩薩曰：「善男子！言有為者"),
                  ("s10", "「善男子！言無為者，亦是本師"), ("s11", "爾時，如理請問菩薩摩訶薩復問"),
                  ("s12", "解甚深義密意菩薩謂如理請問菩薩曰：「善男子！如善幻師"),
                  ("s13", "「若有眾生非愚、非鈍"), ("s14", "「如是，若有眾生是愚夫類"),
                  ("s15", "「若有眾生非愚夫類"), ("s16", "「如是，善男子！彼諸聖者"),
                  ("s17", "爾時，解甚深義密意菩薩，欲重宣")]},
    ],
}


# ── 讀原文 ──────────────────────────────────────────────────────────────────
def read_jsonl(work: str) -> list[dict]:
    return [json.loads(l) for l in (TRIP / f"{work}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def zh_text(src: dict) -> str:
    """該部正文（略去 byline、序），從 start 那幾個字起接到最後。
    給 node（目錄標題，如「（三七九）」）就只取那一經——阿含一部上千經。"""
    segs = read_jsonl(src["work"])
    heads = src.get("nodes") or ([src["node"]] if "node" in src else [])
    if heads:
        toc = json.loads((TRIP / f"{src['work']}.toc.json").read_text(encoding="utf-8"))
        nodes = toc if isinstance(toc, list) else toc["toc"]
        ids = []
        for h in heads:
            hit = [n for n in nodes if n["head"] == h]
            if len(hit) != 1:
                raise SystemExit(f"  ✗ {src['work']}: 目錄標題「{h}」命中 {len(hit)} 個")
            ids.append(hit[0]["i"])
        segs = [s for s in segs if s["d"] in ids and s["kind"] != "head"]
    body = "".join(s["sources"]["lzh"] for s in segs if s["kind"] != "byline")
    i = body.find(src["start"])
    if i < 0:
        raise SystemExit(f"  ✗ {src['work']}: 找不到起點「{src['start']}」")
    body = body[i:]
    if "end" in src:  # 只取到某句之前（一品裡只對讀前半）
        j = body.find(src["end"])
        if j < 0:
            raise SystemExit(f"  ✗ {src['work']}: 找不到截止點「{src['end']}」")
        body = body[:j]
    return body


def tmx_lines(src: dict) -> list[str]:
    """84000 翻譯記憶的第 from..to 個對齊單元（藏或英那一側）。
    藏英同一個單元號，所以兩欄用同一組行號切，保證逐句對得上。"""
    sys.path.insert(0, str(ROOT / "scripts"))
    from tripitaka_tibetan import fetch  # 快取在 C:/tmp/cbeta/tibetan，沒有會自己抓
    raw = fetch(src["tmx"]).read_text(encoding="utf-8", errors="replace")
    side = re.compile(rf'xml:lang="{src["side"]}"[^>]*>\s*<seg>(.*?)</seg>', re.S)
    out = []
    for tu in re.findall(r"<tu[ >].*?</tu>", raw, re.S):
        m = side.search(tu)
        out.append(re.sub(r"<[^>]+>|\s+", " ", m.group(1)).replace("­", "").strip() if m else "")
    return out[src["from"]:src["to"]]


def orig_lines(src: dict) -> list[str]:
    if "tmx" in src:
        return tmx_lines(src)
    o = json.loads((TRIP / f"{src['orig']}.orig.json").read_text(encoding="utf-8"))
    # ref 用前綴比：同一部阿含掛了上千份原典，要指明是哪一經（如 "SN 56.11"）
    want = src.get("ref")
    for lst in o.values():
        for x in lst:
            if x["lang"] == src["lang"] and (not want or re.match(re.escape(want) + r"(?![\d.\-])", x["ref"])):
                lines = [ln[1] for ln in x["lines"]]
                if src.get("drop_numerals"):
                    # 元亨寺版的段號自成一行（「一」「一〇」），不是經文
                    lines = [l for l in lines if not re.fullmatch(r"[一二三四五六七八九〇十]+", l.strip())]
                return lines
    raise SystemExit(f"  ✗ {src['orig']}: orig.json 沒有 {src['lang']} {want or ''}")


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


# ── 切段＋三道閘 ────────────────────────────────────────────────────────────
def cut_version(v: dict, unit_order: list[str]) -> dict[str, str]:
    if "lines" in v:
        lines = orig_lines(v["src"])
        marks = v["lines"]
        if marks[0][1] != 0:
            raise SystemExit(f"  ✗ {v['id']}: 第一刀必須從第 0 行起")
        pieces = []
        for k, (u, start) in enumerate(marks):
            end = marks[k + 1][1] if k + 1 < len(marks) else len(lines)
            if end <= start:
                raise SystemExit(f"  ✗ {v['id']}: {u} 的行號沒有遞增")
            pieces.append((u, " ".join(lines[start:end])))
        whole = " ".join(lines)
    else:
        whole = zh_text(v["src"]) if "work" in v["src"] else "\n".join(orig_lines(v["src"]))
        pos = []
        at = 0
        for u, snip in v["cuts"]:
            i = whole.find(snip, at)
            if i < 0:
                raise SystemExit(f"  ✗ {v['id']}: {u} 的切點「{snip}」在上一刀之後找不到")
            pos.append((u, i))
            at = i + 1
        if pos[0][1] != 0:
            raise SystemExit(f"  ✗ {v['id']}: 第一刀「{v['cuts'][0][1]}」不在正文開頭（前面還有 {pos[0][1]} 字沒歸段）")
        pieces = [(u, whole[i:(pos[k + 1][1] if k + 1 < len(pos) else len(whole))])
                  for k, (u, i) in enumerate(pos)]

    # 閘 2：接回去一字不差
    if norm("".join(p for _, p in pieces)) != norm(whole):
        raise SystemExit(f"  ✗ {v['id']}: 切完接回去與原文不符")
    # 閘 3：義段不重複；除非該本明列 reorder（同源異流、段落確實換了位置），否則要照順序
    idx = [unit_order.index(u) if u in unit_order else -1 for u, _ in pieces]
    if -1 in idx:
        raise SystemExit(f"  ✗ {v['id']}: 有未定義的義段 {[u for u, _ in pieces if u not in unit_order]}")
    if len(set(idx)) != len(idx):
        raise SystemExit(f"  ✗ {v['id']}: 義段重複 {[u for u, _ in pieces]}")
    if idx != sorted(idx) and not v.get("reorder"):
        raise SystemExit(f"  ✗ {v['id']}: 義段倒序 {[u for u, _ in pieces]}（確屬原典換位就加 reorder 並說明）")
    return {u: re.sub(r"\s*\n\s*", " ", p).strip() for u, p in pieces}


def build(slug: str) -> dict:
    cfg = SETS[slug]
    order = [u for u, _ in cfg["units"]]
    cells: dict[str, dict[str, str]] = {u: {} for u in order}
    for v in cfg["versions"]:
        got = cut_version(v, order)
        for u, t in got.items():
            cells[u][v["id"]] = t
        print(f"  ✓ {v['id']:6s} {v['label']:10s} {len(got):2d} 義段  {sum(len(t) for t in got.values()):,} 字")
    empty = [u for u in order if not cells[u]]
    if empty:
        raise SystemExit(f"  ✗ 義段沒有任何本子：{empty}")
    # 閱讀器靠這份清單判斷要不要顯示「異譯對讀」；甘珠爾那部（TMX 沒有經號）由 extra_works 補
    works = sorted({w for v in cfg["versions"] if (w := v["src"].get("work") or v["src"].get("orig"))}
                   | set(cfg.get("extra_works", [])))
    return {
        "slug": slug, "title": cfg["title"], "family": cfg["family"], "intro": cfg["intro"],
        "units": [{"id": u, "label": l} for u, l in cfg["units"]],
        "versions": [{k: v[k] for k in ("id", "lang", "label", "who") if k in v}
                     | ({"reorder": v["reorder"]} if v.get("reorder") else {}) for v in cfg["versions"]],
        "works": works,
        "cells": cells,
    }


def main() -> None:
    slugs = sys.argv[1:] or list(SETS)
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in slugs:
        print(f"[{slug}]")
        data = build(slug)
        (OUT / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    # 索引一律按 SETS 全部重寫，閱讀器用它判斷某部經有沒有異譯對讀
    index = []
    for slug in SETS:
        f = OUT / f"{slug}.json"
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            index.append({"slug": slug, "title": d["title"], "family": d["family"],
                          "works": d["works"], "versions": len(d["versions"])})
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"索引 {len(index)} 組 → {OUT / 'index.json'}")


if __name__ == "__main__":
    main()
