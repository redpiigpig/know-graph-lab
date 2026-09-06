#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""祆教譯名入 /translation-glossary —— HAND-CURATED，不走 LLM。

《祆教經典》(/avesta) 四藏用到的專名，逐條定名後入庫。分四張表：

    theological_terms (entity_type='work')  經典與文獻名
    deities           (religion='祆教（瑣羅亞斯德）')  神祇／概念／人物
    place_names                              地名

🚨 **既有條目一律不動。** 詞庫裡已有的五筆（查拉圖斯特拉／阿胡拉‧馬茲達／
   安格拉‧曼紐／密特拉／祆教）與全部波斯君主、薩珊-波斯帝國、書珊…都是既定權威，
   本批只補沒有的。見 [[feedback_glossary_strict_authority]]。

🚨 2026-09-06 二次修訂（使用者指示「去查中文的經典祆教著作或相關論文再確定」）：
   經典篇名一律改從**中文學界既成譯名**，不再由本站按音理自擬。依據：
     · 元文琪譯《阿維斯塔——瑣羅亞斯德教聖書》（商務印書館 2010，中文世界唯一
       成規模的《阿維斯陀》譯本）的卷次篇名
     · 中文維基百科正體版條目名（〈亞斯納〉〈亞扎塔〉〈阿沙‧瓦希什塔〉）
     · 龔方震、晏可佳《祆教史》（上海社科院 1998）
   據此推翻本站初擬的五個篇名：迦薩→伽薩、耶斯那→亞斯納、耶什特→亞什特、
   維斯佩拉德→維斯帕拉德、祓魔法典→萬迪達德。理由見各條 reason。

定名依 /translation-glossary 的五條原則：
  1. 按原文不按英文 —— 阿維斯陀語／中古波斯語為準，英文轉寫退為 name_english。
  2. 沿用良好古譯／既有意譯 —— 「祓魔法典」「穆護」屬此。
  3. 音意結合 —— 有好意譯就不硬音譯（宗教判例、宜與不宜、百門）。
  4. 名根一致 —— 阿維斯陀／小阿維斯陀 同 root；斯彭塔‧曼紐／斯彭塔‧阿爾邁提 同 root。
  5. 已廢古譯不用 —— 大夏、大秦一類一律不收，連變體都不放。

🚨 印歐同源詞的陷阱：daēva 與梵語 deva（提婆）同源**而義相反**（祆教的迭瓦是惡魔），
   haoma 與 soma（蘇摩）同源，aša 與吠陀 ṛta 同源，Yima 與 Yama（閻摩）同源。
   同源**不等於**可以借用佛教既有譯名——借了會把兩個宗教的價值判斷混在一起。
   故一律另行音譯，並在 reason 註明同源關係。

用法：
    python scripts/seed_glossary_zoroastrian.py --dry   # 預覽（預設）
    python scripts/seed_glossary_zoroastrian.py --run   # 實際寫入
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RELIGION = "祆教（瑣羅亞斯德）"
SOURCE = "祆教經典 /avesta（2026-09-06 定名）"

WORKS: list[dict] = []
DEITIES: list[dict] = []
PLACES: list[dict] = []
_ord = {"w": 9000, "d": 9000, "p": 9000}


def W(en, rec, *, o="", lang="ae", translit="", cn="", reason="", root="", era="", note=""):
    """經典／文獻名 → theological_terms(entity_type='work')。
    cn＝大陸學界既有譯名（多為元文琪《阿維斯塔》商務本），入 zh_china_academic。"""
    _ord["w"] += 10
    WORKS.append({
        "term_original": o or None, "term_original_lang": lang or None,
        "term_latin_translit": translit or None, "term_english": en,
        "zh_recommended": rec, "zh_china_academic": cn or None,
        "recommendation_reason": reason or None, "name_root": root or None,
        "entity_type": "work", "era": era or None, "notes": note or None,
        "first_source": SOURCE, "sort_order": _ord["w"],
    })


def D(en, rec, *, o="", lang="ae", var="", reason="", root="", etype="deity", domain="", note=""):
    """神祇／概念／人物 → deities。"""
    _ord["d"] += 10
    DEITIES.append({
        "name_english": en, "name_original": o or None, "name_original_lang": lang or None,
        "name_recommended": rec, "name_variants": var or None,
        "recommendation_reason": reason or None, "name_root": root or None,
        "religion": RELIGION, "entity_type": etype, "domain_of": domain or None,
        "notes": note or None, "sort_order": _ord["d"],
    })


def P(en, rec, *, o="", lang="", var="", reason="", root="", ptype="城市", modern=""):
    """地名 → place_names。"""
    _ord["p"] += 10
    PLACES.append({
        "name_english": en, "name_original": o or None, "name_original_lang": lang or None,
        "name_recommended": rec, "name_variants": var or None,
        "recommendation_reason": reason or None, "name_root": root or None,
        "place_type": ptype, "modern_name": modern or None, "sort_order": _ord["p"],
    })


# ════════════════ A. 經典與文獻名 ════════════════

# ── 阿維斯陀（正藏）──
W("Avesta", "阿維斯陀", o="Avestā", translit="Avestā", cn="阿維斯塔",
  root="阿維斯陀", era="約前 1500 – 公元 4 世紀",
  reason="本站《東方聖書》第 4、23、31 卷卷名與中文維基通行作「阿維斯陀」，"
         "沿用以求一致；商務印書館元文琪譯本作《阿維斯塔》，列為大陸學界譯名。")
W("Yasna", "亞斯納", o="Yasna", translit="Yasna",
  reason="yasna 意為「敬拜、獻祭」。🚨 2026-09-06 由初擬的「耶斯那」改。"
         "元文琪譯本第二卷作《亞斯納》，中文維基百科正體版的條目名亦為〈亞斯納〉——"
         "兩個獨立來源一致。「耶斯那」雖亦見於中文維基的另一版本，非主流。")
W("Gāthās", "伽薩", o="Gāθā", translit="Gāθā", root="伽薩",
  era="約前 1500–1000",
  reason="🚨 2026-09-06 由本站初擬的「迦薩」改為「伽薩」。初擬理由是音理"
         "（迦在台灣國語只讀 jiā，伽兼讀 qié 有歧義），但元文琪譯《阿維斯塔》"
         "（商務 2010）第一卷即作《伽薩》，是中文世界唯一成規模的譯本，"
         "屬「沿用既有良好譯名」（原則 2）所指者，音理推衍不應凌駕於其上。"
         "🚨 仍不可借用佛教的「偈」「伽陀」——梵語 gāthā 雖與本詞同源，但那是文類名，"
         "借用會把查拉圖斯特拉的十七首詩降成一種泛稱文體。",
  note="查拉圖斯特拉本人所作的十七首詩，古阿維斯陀語，全教最古的一層。"
       "＝耶斯那第 28–34、43–46、47–50、51、53 章。")
W("Yasna Haptaŋhāiti", "七章禱", translit="Yasna Haptaŋhāiti", cn="七章亞斯納",
  reason="hapta「七」；意譯「七章禱」較音譯可讀。散文體，古阿維斯陀語，與迦薩同層。")
W("Visperad", "維斯帕拉德", o="Vīspe ratavō", translit="Visperad",
  reason="vīspe ratavō「向一切主宰者」。全為音譯，因其內容無可意譯的主題。"
         "🚨 2026-09-06 由初擬的「維斯佩拉德」改，依元文琪譯本第五卷《維斯帕拉德》。")
W("Vendidad / Videvdad", "萬迪達德", o="Vīdaēva-dāta", translit="Vīdēvdād",
  era="約前 400 – 公元 300",
  reason="原文 vī-daēva-dāta ＝「驅除迭瓦之法」。🚨 2026-09-06 由本站初擬的意譯"
         "「祓魔法典」改為音譯。元文琪譯本第四卷作《萬迪達德》，中文維基作《萬迪達德》"
         "／《溫迪達德》——中文學界一律音譯，未見用意譯作正式書名者。"
         "意譯「祓魔法典」「驅魔書」「降魔書」退為變體；"
         "本站《東方聖書》第 4 卷卷名亦同步改。",
  note="二十一納斯克中唯一完整傳世者，22 章。")
W("Yasht", "亞什特", o="Yašt", translit="Yašt",
  reason="yašt「敬拜、讚頌」。獻給各亞扎塔的讚歌 21 首。"
         "🚨 2026-09-06 由初擬的「耶什特」改，依元文琪譯本第三卷《亞什特》。")
W("Khordeh Avesta", "小阿維斯陀", translit="Xorde Avestā", cn="胡爾達‧阿維斯塔",
  root="阿維斯陀",
  reason="khordeh「小的」。元文琪譯本第六卷作《胡爾達‧阿維斯塔》（純音譯），"
         "但「小阿維斯陀」意義透明、且與《阿維斯陀》構成名根一致的一組，"
         "中文他處亦通行，故本站取之，音譯列為變體。此為本區少數不從元文琪本者，"
         "理由是原則 3（音意結合）與原則 4（名根一致）。在家信眾日課本。")
W("Sīrōzah", "三十日誦", translit="Sīrōzah", cn="西魯澤",
  reason="sī「三十」＋rōz「日」。元文琪譯本作《大西魯澤篇》（音譯），"
         "但「三十日誦」意義透明且不與他篇混淆，故取意譯，音譯列為變體。")
W("Niyāyišn", "讚頌", translit="Niyāyišn", cn="尼亞耶什",
  reason="小阿維斯陀的五篇「讚頌」（日月水火密特拉），意譯。")
W("Gāh", "時禱", translit="Gāh",
  reason="一晝夜五時段各有專禱，意譯「時禱」與基督宗教日課的「時辰禱」對位可讀。")
W("Āfrīnagān", "阿法林甘", translit="Āfrīnagān", cn="阿法林甘",
  reason="配合供品行禮的祝福禱文。🚨 由初擬的意譯「祝禱」改為音譯，依元文琪譯本"
         "《阿法林甘篇》——「祝禱」過泛，與讚頌（Niyāyišn）難以分辨。")
W("Nirangistan", "儀軌書", translit="Nīrangistān", cn="尼朗吉斯坦",
  reason="nīrang「儀軌、咒式」＋-stān「集」。意譯。薩珊祭司實務僅存的直接材料。")
W("Herbedestan", "修學書", translit="Hērbedestān", cn="赫爾貝德斯坦",
  reason="🚨 本站初擬「師徒書」已廢。hērbed 是授業祭司，全篇論的是「誰該去求學、去多久、"
         "家業與學業如何權衡」，是修學義務而非師徒關係，故改「修學書」。",
  note="含女性受教的規定。原屬胡斯帕拉姆納斯克。")
W("Hadhokht Nask", "哈多赫特納斯克", translit="Hāδōxt Nask",
  reason="音譯。祆教來世觀最重要的原典段落（義人死後三日的靈魂經歷）。")
W("Aogemadaeca", "我等奉行", translit="Aogəmadaēčā", cn="奧格瑪達埃查",
  reason="篇名取自首句 aogəmadaēčā「我等奉行」，依原文取意譯。喪禮誦本。")
W("Frahang ī Ōīm", "詞義彙編", translit="Frahang ī Ōīm",
  reason="阿維斯陀語—中古波斯語對譯詞表，意譯。保存大量今已無出處的阿維斯陀語詞。")
W("Nasks", "納斯克", translit="Nask", cn="納斯克",
  reason="薩珊正典的分卷單位，音譯已通行。全 21 部，今存 1 部半。")

# ── 伽薩五篇與亞什特諸篇（篇名依元文琪譯本；此前本站只有意譯，未定音譯專名）──
W("Ahunavaiti Gatha", "阿胡納瓦德‧伽薩", translit="Ahunauuaitī Gāθā", root="伽薩",
  reason="迦薩第一組（耶斯那 28–34 章），篇名依元文琪譯本。意譯「阿胡納瓦提迦薩」為本站舊擬，已廢。")
W("Ushtavaiti Gatha", "奧什塔瓦德‧伽薩", translit="Uštauuaitī Gāθā", root="伽薩",
  reason="伽薩第二組（耶斯那 43–46 章），含著名的「二十問」。篇名依元文琪譯本。")
W("Spentamainyu Gatha", "塞潘特馬德‧伽薩", translit="Spəṇtā.mainyū Gāθā", root="伽薩",
  reason="伽薩第三組（耶斯那 47–50 章）。篇名依元文琪譯本。")
W("Vohukhshathra Gatha", "沃胡赫什塔爾‧伽薩", translit="Vohu.xšaθrā Gāθā", root="伽薩",
  reason="伽薩第四組（耶斯那 51 章）。篇名依元文琪譯本。")
W("Vahishtoishti Gatha", "瓦希什圖伊什特‧伽薩", translit="Vahištōišti Gāθā", root="伽薩",
  reason="伽薩第五組（耶斯那 53 章），先知幼女的婚禮致辭。篇名依元文琪譯本。")

W("Aban Yasht", "阿邦‧亞什特", translit="Ābān Yašt", root="亞什特",
  reason="亞什特第 5 首，獻給水神阿娜希塔。🚨 篇名用**新波斯語**形（Ābān＝水），"
         "非阿維斯陀語形——元文琪譯本如此，帕西社群今日亦如此稱呼。")
W("Tir Yasht", "蒂爾‧亞什特", translit="Tīr Yašt", root="亞什特",
  reason="亞什特第 8 首，獻給天狼星神提什特里亞（新波斯語 Tīr）。篇名依元文琪譯本。")
W("Mehr Yasht", "梅赫爾‧亞什特", translit="Mihr Yašt", root="亞什特",
  reason="亞什特第 10 首，獻給密特拉（新波斯語 Mihr／Mehr），全書最長。篇名依元文琪譯本。")
W("Farvardin Yasht", "法爾瓦爾丁‧亞什特", translit="Frawardīn Yašt", root="亞什特",
  reason="亞什特第 13 首，獻給弗拉瓦希，逐一唱出數百位先賢之名。篇名依元文琪譯本。")
W("Bahram Yasht", "巴赫拉姆‧亞什特", translit="Bahrām Yašt", root="亞什特",
  reason="亞什特第 14 首，獻給勝利神韋雷特拉格納（新波斯語 Bahrām）。篇名依元文琪譯本。")
W("Zamyad Yasht", "扎姆亞德‧亞什特", translit="Zamyād Yašt", root="亞什特",
  reason="亞什特第 19 首，敘王者神光的轉移與逃逸。篇名依元文琪譯本。")

# ── 巴列維文獻（續典）──
W("Dēnkard", "丹卡爾德", translit="Dēnkard", lang="pal", cn="德恩卡爾特", era="9–10 世紀",
  reason="dēn「宗教」＋kard「作為」。音譯已通行；意譯「宗教行述」列為變體，"
         "因本書實為百科而非行傳，意譯易生誤解。",
  note="原 9 卷存 3–9。第 8、9 卷逐部撮述二十一納斯克，是失傳正典的唯一目錄。")
W("Bundahišn", "本達希什", translit="Bundahišn", lang="pal", cn="班達希申",
  reason="bun「太初」＋dahišn「造作」。🚨 不取意譯「創世書」——與《創世記》碰撞，"
         "讀者會誤以為是同一文類的對應物。")
W("Wizīdagīhā ī Zādspram", "扎德斯普拉姆選集", translit="Wizīdagīhā ī Zādspram", lang="pal",
  reason="wizīdagīhā「選集」意譯＋作者名音譯，音意結合。")
W("Dādestān ī Dēnīg", "宗教判例", translit="Dādestān ī Dēnīg", lang="pal", cn="達德斯坦‧丹尼克",
  reason="dādestān「判決」＋dēnīg「宗教的」。意譯達意：九十二則祭司對信眾疑問的書面判答，"
         "與教會法規的「決疑」同類。")
W("Nāmagīhā ī Manuščihr", "曼努什奇赫爾書信", translit="Nāmagīhā ī Manuščihr", lang="pal",
  era="公元 881 年", reason="nāmag「書信」意譯＋人名音譯。有明確年份的祆教文獻極少，這是其一。")
W("Šāyest nē Šāyest", "宜與不宜", translit="Šāyest nē Šāyest", lang="pal", cn="沙耶斯特‧內‧沙耶斯特",
  reason="直譯「可以與不可以」；取「宜與不宜」以合漢語律書的語感（如《禮記》宜否之辨）。")
W("Škand-gumānīg Wizār", "破疑釋惑", translit="Škand-gumānīg Wizār", lang="pal", cn="解疑論",
  reason="škand「破除」＋gumānīg「疑惑的」＋wizār「解說」。四字意譯保留原文的雙重結構。",
  note="逐章反駁伊斯蘭、猶太教、基督宗教與摩尼教；前現代少數由非亞伯拉罕傳統寫出的系統性一神教批判。")
W("Dādestān ī Mēnōg ī Xrad", "智慧之靈", translit="Mēnōg ī Xrad", lang="pal", cn="智慧精神",
  reason="🚨 本站初擬「智慧精神」已廢。mēnōg 是祆教的專門術語，指與「質態」(gētīg) 相對的"
         "「靈態」，是一個位格化的靈而非抽象品質；譯「精神」會讀成一種心態。改「智慧之靈」。",
  note="智者向智慧之靈發問六十三則的對話體。")
W("Ardā Wīrāz Nāmag", "阿爾達‧維拉茲書", translit="Ardā Wīrāz Nāmag", lang="pal", cn="阿爾達‧維拉夫書",
  root="維拉茲",
  reason="nāmag「書」意譯＋人名音譯。🚨 取 Wīrāz 的中古波斯語讀音作「維拉茲」，"
         "不取英譯常見的 Viraf「維拉夫」——後者出自古吉拉特語轉寫，非原文（原則 1）。",
  note="魂遊天堂與地獄的一〇一章；與但丁《神曲》結構相似度極高。")
W("Zand ī Wahman Yasn", "瓦赫曼耶什特", translit="Zand ī Wahman Yasn", lang="pal", cn="巴赫曼耶什特",
  root="瓦赫曼",
  reason="🚨 本站初擬「巴赫曼耶什特」改。Bahman 是新波斯語形，本書是中古波斯語，"
         "原文作 Wahman，故取「瓦赫曼」（原則 1）。西方舊題 Bahman Yasht 出自韋斯特 SBE，列為變體。",
  note="金銀鐵鉛之樹的異象；祆教啟示文學的代表。")
W("Ayādgār ī Jāmāspīg", "賈馬斯普紀念書", translit="Ayādgār ī Jāmāspīg", lang="pal",
  root="紀念書", reason="ayādgār「紀念、遺記」意譯＋人名音譯；與《扎雷爾紀念書》同構。")
W("Pahlavi Rivāyat", "巴列維利瓦亞特", translit="Pahlavi Rivāyat", lang="pal",
  root="利瓦亞特", reason="附於《宗教判例》之後流傳的雜纂。")
W("Čīdag Andarz ī Pōryōtkēšān", "古聖精選訓誡", translit="Čīdag Andarz ī Pōryōtkēšān", lang="pal",
  reason="čīdag「精選」＋andarz「訓誡」＋pōryōtkēšān「先賢、古聖」，逐詞意譯。",
  note="祆教的要理問答：十五歲當知者為何？答曰知我是誰、屬誰、從何而來、往何處去。")
W("Kārnāmag ī Ardaxšīr ī Pābagān", "阿爾達希爾功業記", translit="Kārnāmag ī Ardaxšīr", lang="pal",
  reason="kārnāmag「功業記」意譯＋君主名依詞庫既有「阿爾達希爾一世」。")
W("Ayādgār ī Zarērān", "扎雷爾紀念書", translit="Ayādgār ī Zarērān", lang="pal",
  root="紀念書", reason="現存最古的伊朗語敘事詩之一，原為安息時期口傳吟唱。")
W("Wizārišn ī Čatrang", "棋弈書", translit="Wizārišn ī Čatrang", lang="pal",
  reason="čatrang 即西洋棋（源自梵語 caturaṅga）。世界棋史最早的文獻之一。")

# ── 後期文獻（外典）──
W("Sad Dar", "百門", translit="Sad Dar", lang="fa", cn="薩達爾", era="約 15 世紀",
  reason="sad「百」＋dar「門、章」。意譯；「門」在漢語佛道文獻本即章目之稱（法門、十門）。")
W("Zarātušt-nāma", "查拉圖斯特拉傳", translit="Zarātušt-nāma", lang="fa", root="查拉圖斯特拉",
  era="約 1278 年",
  reason="nāma「書、傳」；人名依詞庫既有「查拉圖斯特拉」，名根一致。仿《列王紀》體例的先知生平長詩。")
W("Persian Rivāyats", "波斯利瓦亞特", translit="Rivāyat", lang="fa", root="利瓦亞特",
  era="1478–1773 年",
  reason="rivāyat 原為伊斯蘭教法的「傳述、答問」，祆教沿用其形式；音譯保留這層借用關係，"
         "意譯「教法答問」列為變體。",
  note="印度帕西社群與伊朗祭司往返近三百年、二十餘通的教法問答。")
W("Qissa-i Sanjān", "桑賈恩紀事", translit="Qissa-i Sanjān", lang="fa", era="1600 年",
  reason="qissa「紀事、故事」；地名音譯。帕西族群認同的奠基文本，"
         "但成書晚於所敘事件六百年，史實性須另行評估。")
W("Dabestān-e Mazāheb", "諸教志", translit="Dabestān-e Mazāheb", lang="fa", era="17 世紀中",
  reason="dabestān「學堂、彙編」＋mazāheb「諸教派」。意譯「諸教志」合漢語志書體例。")


# ════════════════ B. 宗教名詞與概念 ════════════════

_ord["d"] = 9200
D("Mazdayasna", "馬茲達崇拜", o="mazdayasna", var="瑪茲達教；拜火教（俗稱，不確）",
  etype="概念", root="馬茲達",
  reason="信徒的自稱（「敬拜馬茲達者」），與外稱「祆教」並行。"
         "🚨「拜火教」是漢語俗稱，祆教敬火為潔淨的象徵而非崇拜對象，正式行文不用。")
D("Zurvanism", "祖爾萬派", var="佐爾萬主義", etype="教派", root="祖爾萬",
  reason="薩珊時期以「時間」(Zurwān) 為第一本原、視善惡二靈為其雙生子的一派；"
         "後被正統斥為異端。名根與神格「祖爾萬」一致。")
D("Avestan language", "阿維斯陀語", etype="概念", root="阿維斯陀",
  reason="與《阿維斯陀》名根一致。分古、新兩層，古阿維斯陀語即迦薩與七章禱所用。")
D("Pahlavi", "巴列維", var="帕拉維；中古波斯語", etype="概念",
  reason="音譯已通行（另有巴列維王朝同名）。嚴格說 Pahlavi 指書寫系統，"
         "所記語言為中古波斯語，行文時兩者可互換但不可混稱「巴列維語族」。")
D("Pazand", "帕贊德", etype="概念",
  reason="以阿維斯陀字母轉寫中古波斯語的書寫法，避開巴列維文字的表意符歧義。")
D("Zand", "贊德", var="經註", etype="概念",
  reason="阿維斯陀經文的中古波斯語譯註。🚨「Avesta and Zand」被歐洲早期誤讀為書名"
         "「曾德‧阿維斯陀」(Zend-Avesta)，該形式為訛稱，本站不用於書名。")
D("Amesha Spenta", "不朽聖者", o="Aməša Spənta", var="阿姆沙‧斯彭塔；聖不朽者；六大天使",
  etype="概念", domain="阿胡拉‧馬茲達的六位屬性神格",
  reason="aməša「不朽的」＋spənta「豐饒的、聖的」。意譯較音譯可讀；"
         "🚨 不用「天使長」一類基督宗教對位詞——它們是馬茲達的位格化屬性，不是受造的使者。")
D("yazata", "亞扎塔", o="yazata", var="雅扎塔；應祀者", etype="概念",
  domain="值得敬拜的神格總稱",
  reason="字面「值得敬拜者」。音譯為主，意譯「應祀者」列為變體。")
D("daēva", "迭瓦", o="daēva", var="代弗", etype="概念", domain="惡魔",
  reason="🚨 **絕不可譯「提婆」。** 梵語 deva 與本詞同源，佛教漢譯作提婆／天，"
         "但祆教把 daēva 貶為惡魔——這正是印度－伊朗宗教分道的關鍵。"
         "借用佛教譯名會把兩個宗教相反的價值判斷混成一個詞。")
D("druj", "德魯格", o="druj", var="虛妄；謊言", etype="概念", domain="虛妄／謊言",
  reason="與「阿沙」(真理) 相對的宇宙原理。音譯為主，意譯「虛妄」列為變體。"
         "貝希斯敦銘文的 drauga 即此詞的古波斯語形。")
D("asha", "阿沙", o="aša", var="阿夏；真理；正法", etype="概念", domain="真理／宇宙秩序",
  reason="與吠陀 ṛta 同源，指真理兼宇宙秩序兼禮儀正確——漢語無單詞可對，故音譯，"
         "意譯列為變體。🚨 不宜逕譯「法」或「道」，那會誤導成印度或中國的對應概念。")
D("fravashi", "弗拉瓦希", o="fravaši", var="前靈；祖靈", etype="概念", domain="先在之靈／守護靈",
  reason="人與神皆有的先在之靈，兼具祖先崇拜與守護靈兩重性格；漢語無對應詞，音譯。")
D("haoma", "豪麻", o="haoma", var="好瑪", etype="概念", domain="聖植物／榨汁禮",
  reason="與梵語 soma（漢譯蘇摩）同源。🚨 不借用「蘇摩」——兩教的儀式地位與植物指涉都不同，"
         "共用一名會掩蓋差異。豪麻在耶斯那中另有位格化的神格，見 Haoma 條。")
D("khvarenah", "赫瓦雷納", o="xᵛarənah", var="王者神光；法爾（Farr）", etype="概念",
  domain="王權神光",
  reason="附麗於正統君王與英雄的神聖光輝，可轉移、可逃逸。意譯「王者神光」達意但過長，"
         "作變體；新波斯語形 Farr 亦列變體。")
D("Frashokereti", "弗拉紹‧克雷提", o="Frašō.kərəti", var="萬物復原；終末更新", etype="概念",
  domain="末世的萬物更新",
  reason="字面「使之奇妙」。祆教末世論的核心：烈火熔盡群山、死者復活、惡被消滅、世界復歸完好。"
         "意譯「萬物復原」列為變體。")
D("Saoshyant", "薩奧希揚特", o="Saošyant", var="救世主；救主", etype="概念", domain="末世救主",
  reason="字面「使之有益者」。🚨 意譯「救世主」列為變體而不作主譯——"
         "免得讀者逕以基督論的救主概念套入。")
D("Chinvat Bridge", "裁判之橋", o="Činvatō Pərətu", var="欽瓦特橋；分別橋", etype="概念",
  domain="亡魂受審之橋",
  reason="činvant「分別者、裁判者」＋pərətu「橋」。義人過之則寬如大道，惡人過之則窄如刀刃。"
         "取意譯以見其功能。")
D("dakhma", "寂靜之塔", o="dakhma", var="達克瑪；天葬塔", etype="概念", domain="曝屍塔",
  reason="依原則 2 沿用既有良好意譯。🚨「寂靜之塔」(Tower of Silence) 其實是十九世紀"
         "英國人的造語、非原文，但漢語世界已通行且傳神；原文音譯「達克瑪」列為變體。")
D("Ātaš Bahrām", "阿塔什‧巴赫拉姆", var="勝利之火；巴赫拉姆火", etype="概念", domain="最高等級聖火",
  root="巴赫拉姆", reason="三級聖火之最高者，須由十六種來源的火合成、歷一年淨禮方成。")
D("gahanbar", "伽罕巴爾", o="gāhānbār", var="迦罕巴爾；六節期", etype="概念", domain="六大季節祭",
  reason="一年六次的季節祭，各紀念一項創造。意譯「六節期」列為變體。")
D("kusti", "庫斯提", var="聖帶", etype="概念", domain="祭司與信眾繫的聖帶",
  reason="七十二縷編成，對應耶斯那七十二章；每日解繫數次並誦禱。")
D("sudreh", "蘇德拉", var="聖衫", etype="概念", domain="貼身穿的聖白衫",
  reason="與庫斯提同為入教（納夭特）後終身穿戴之物。")
D("barashnum", "巴爾什農", o="barašnūm", var="九夜大淨禮", etype="概念", domain="最高等級的淨禮",
  reason="祓魔法典第 9 章所載的九夜潔淨儀式。意譯「九夜大淨禮」列為變體。")
D("nasu", "納蘇", o="nasu", var="屍魔", etype="概念", domain="屍體污染之魔",
  reason="以蠅形撲向屍體的污染之魔；祆教潔淨法的整套規定皆為對治此物。")
D("mowbed", "穆護", var="莫貝德；祭司長；магупат", etype="概念", domain="祭司長",
  reason="🚨 依原則 2 恢復唐代漢籍古譯。唐代長安祆祠的祭司即稱「穆護」"
         "（《通典》《唐會要》），是漢語現成且仍為隋唐宗教史學界使用的譯名，"
         "不屬「已廢古譯」之列，故取為主譯。")
D("magi / magus", "麻葛", o="maguš", lang="peo", var="瑪吉；博士（太 2 和合本）；術士",
  etype="概念", domain="米底亞的祭司部族",
  reason="米底亞的世襲祭司階層，希羅多德所記的六部族之一。"
         "🚨 和合本《馬太》二章的「博士」即此字，但那是聖經語境的譯法，"
         "作為宗教史術語應與之區分，故主譯取「麻葛」。")
D("Parsi", "帕西", var="巴斯；波斯人（字面）", etype="概念", domain="遷居印度的祆教社群",
  reason="八至十世紀自伊朗渡海入印度古吉拉特的祆教徒後裔；今日祆教人口的主體。")
D("menog", "靈態", o="mēnōg", lang="pal", var="梅諾格；靈界", etype="概念", domain="無形的存在狀態",
  reason="與「質態」(gētīg) 構成祆教宇宙論的基本對偶：先有靈態的創造，後有質態的實現。"
         "🚨 不譯「精神／物質」——那是笛卡兒式的二分，祆教的質態是善的、是靈態的完成而非墮落。")
D("getig", "質態", o="gētīg", lang="pal", var="蓋提格；物質界", etype="概念", domain="有形的存在狀態",
  reason="見「靈態」條。質態為善，是祆教與摩尼教、諾斯底主義最根本的分歧點。")
D("Ahuna Vairya", "阿胡納‧瓦伊里亞", o="Ahuna Vairiia", var="亞塔‧阿胡‧瓦伊里約", etype="概念",
  domain="全教第一禱詞",
  reason="僅一節，經文稱其在創世之前即已存在。以首二詞 yaθā ahū vairyō 亦稱之。")
D("Ashem Vohu", "阿舍姆‧沃胡", o="Ašəm Vohū", etype="概念", domain="讚頌真理的三行禱",
  reason="祆教徒一生誦唸次數最多的一句；首詞即 aša（阿沙，真理）的受格。")
D("andarz", "安達爾茲", var="訓誡文", etype="概念", domain="波斯特有的訓誡文類",
  reason="長者對子弟的格言式教導，與希伯來箴言、佛教法句同類而更世俗務實。")

# ════════════════ C. 神祇與神格 ════════════════

_ord["d"] = 9500
D("Spenta Mainyu", "斯彭塔‧曼紐", o="Spəṇta Mainyu", var="豐饒之靈；聖靈（不宜）",
  root="斯彭塔", domain="馬茲達的創造之靈",
  reason="spəṇta「豐饒的、聖的」＋mainyu「靈」，與安格拉‧曼紐相對。"
         "🚨 變體「聖靈」列出僅為對照，正式行文不用——會與基督宗教的三一論位格混淆。")
D("Vohu Manah", "沃胡‧馬納", o="Vohu Manah", var="善念；瓦赫曼（Wahman）；巴赫曼（Bahman）",
  etype="deity", domain="不朽聖者之一：善念",
  reason="六不朽聖者之首。中古波斯語形 Wahman 即《瓦赫曼耶什特》書名所本（該形只出現在變體欄，故不設 name_root）。")
D("Asha Vahishta", "阿沙‧瓦希什塔", o="Aša Vahišta", var="至上真理；阿爾德瓦希什特（Ardwahisht）",
  root="阿沙", etype="deity", domain="不朽聖者之一：最勝之義；掌火",
  reason="名根與概念詞「阿沙」一致。")
D("Khshathra Vairya", "赫沙特拉‧瓦伊里亞", o="Xšaθra Vairya", var="善治；沙赫雷瓦爾（Šahrewar）",
  etype="deity", domain="不朽聖者之一：可欲的王權；掌金屬",
  reason="xšaθra「王權」與古波斯語銘文的 xšāyaθiya（王）同源。")
D("Spenta Armaiti", "斯彭塔‧阿爾邁提", o="Spəṇtā Ārmaiti", var="虔敬；斯潘達爾馬德（Spandarmad）",
  root="斯彭塔", etype="deity", domain="不朽聖者之一：虔敬；掌大地",
  reason="名根與「斯彭塔‧曼紐」一致。六者中唯一明確為女性神格。")
D("Haurvatat", "豪爾瓦塔特", o="Haurvatāt", var="圓滿；霍爾達德（Hordad）", etype="deity",
  domain="不朽聖者之一：完整；掌水", reason="與「阿梅雷塔特」常成對出現。")
D("Ameretat", "阿梅雷塔特", o="Amərətāt", var="不朽；阿穆爾達德（Amurdad）", etype="deity",
  domain="不朽聖者之一：不朽；掌植物",
  reason="a-「非」＋mərəta「死」，與希臘語 ambrotos（不死）同源。")
D("Anahita", "阿娜希塔", o="Arəduuī Sūrā Anāhitā", var="阿爾德維‧蘇拉‧阿娜希塔；阿納希塔",
  root="阿娜希塔", etype="deity", domain="水／豐饒／戰勝",
  reason="全稱意為「潤澤的、強大的、無玷的」。耶什特第 5 首的受祀者；"
         "阿爾塔薛西斯二世起入王室銘文，是阿契美尼德晚期宗教變化的關鍵證據。")
D("Tishtrya", "提什特里亞", o="Tištrya", var="提斯特里亞；提爾（Tīr）；天狼星神", etype="deity",
  domain="天狼星／降雨",
  reason="化白馬與旱魔阿波沙化的黑馬相鬥，勝則降雨——印歐鬥龍神話的伊朗形態。")
D("Verethragna", "韋雷特拉格納", o="Vərəθraγna", var="巴赫拉姆（Bahrām）；韋雷斯拉格那",
  etype="deity", domain="勝利／戰爭",
  reason="字面「擊破障礙者」，與吠陀 Vṛtrahan（因陀羅的稱號）同源。以十種化身現形。"
         "中古波斯語形 Bahrām 即「阿塔什‧巴赫拉姆」所本（該形只出現在變體欄，故不設 name_root）。")
D("Sraosha", "斯勞沙", o="Sraoša", var="索魯什（Sorush）；斯羅沙", etype="deity",
  domain="聽從／守護亡魂",
  reason="字面「聽從、聆聽」。人死後三夜守護其魂者；亦為祭儀誦唸本身的神格化。")
D("Rashnu", "拉什努", o="Rašnu", etype="deity", domain="公義／審判",
  reason="亡魂過裁判之橋時執秤者。與密特拉、斯勞沙合為審判三神。")
D("Ashi", "阿希", o="Aṣ̌i", var="阿爾德（Ard）；福運", etype="deity", domain="福運／賞報",
  reason="耶什特第 17 首的受祀女神；與「阿沙」音近而詞源不同，勿混。")
D("Vayu", "瓦尤", o="Vaiiu", var="瓦伊；風神", etype="deity", domain="風／生死之間",
  reason="與吠陀 Vāyu 同源。兼具生死兩面，是祆教二元體系裡罕見的曖昧神格。")
D("Atar", "阿塔爾", o="Ātar", var="阿塔什（Ātaš）；火", etype="deity", domain="火",
  reason="火的神格化，阿胡拉‧馬茲達之子。祆教敬火為潔淨與真理的可見象徵。")
D("Haoma (deity)", "豪麻神", o="Haoma", root="豪麻", etype="deity", domain="聖植物之神格",
  reason="耶斯那第 9–11 章中現身向查拉圖斯特拉自陳來歷；與作為植物／飲品的「豪麻」同名，"
         "行文須以「豪麻神」區別。")
D("Zurwan", "祖爾萬", o="Zurwān", lang="pal", var="佐爾萬；時神", root="祖爾萬", etype="deity",
  domain="無限時間",
  reason="祖爾萬派奉為第一本原、善惡二靈之父。正統祆教不承認其至高地位。")
D("Aeshma", "埃什瑪", o="Aēšma", var="忿怒魔", etype="deity", domain="忿怒／暴力之魔",
  reason="🚨 《多俾亞傳》的阿斯摩太（Asmodeus）一般認為源自 Aēšma-daēva，"
         "是祆教影響第二聖殿猶太教的少數具體詞證之一。")
D("Azhi Dahaka", "阿日‧達哈卡", o="Aži Dahāka", var="扎哈克（Zahhāk）；三頭龍", etype="deity",
  domain="三頭巨龍／暴君",
  reason="aži「蛇、龍」與梵語 ahi、希臘語 ekhis 同源。後在《列王紀》中人格化為暴君扎哈克。")
D("Yima", "伊瑪", o="Yima", var="賈姆希德（Jamshīd）；亞瑪", etype="傳說人物", domain="首王／黃金時代",
  reason="🚨 與吠陀 Yama（漢譯閻摩、閻羅）同源，但職能全異：吠陀的閻摩是首位死者與冥界之主，"
         "祆教的伊瑪是首王與黃金時代之君。**不可借用「閻摩」譯名。**",
  note="祓魔法典第 2 章載其奉命造地下方城以避大寒，攜各類生靈之種入內。")
D("Thraetaona", "斯萊塔奧納", o="Θraētaona", var="費里頓（Farīdūn）", etype="傳說人物",
  domain="屠龍英雄", reason="制伏阿日‧達哈卡者；與吠陀 Trita Āptya 同源。")
D("Keresaspa", "克爾薩斯帕", o="Kərəsāspa", var="加爾沙斯普（Garshāsp）", etype="傳說人物",
  domain="英雄／末世助手", reason="末世時將醒來擊殺脫縛的阿日‧達哈卡。")

# ════════════════ D. 歷史人物（祭司與作者）════════════════

_ord["d"] = 9700
D("Vishtaspa", "維什塔斯帕", o="Vīštāspa", var="古世塔斯普（Goštāsp）；維斯塔斯普",
  etype="傳說人物", domain="首位皈依的護法王",
  reason="🚨 與阿契美尼德的大流士之父 Hystaspes（希斯塔斯佩斯）同名而非同人，行文須辨明。")
D("Kartir", "卡爾提爾", o="Kirdīr", lang="pal", var="卡爾迪爾；基爾德", etype="祭司",
  domain="薩珊三世紀祭司長",
  reason="四處銘文自述其設立火廟、整肅祭司，並列舉遭其打擊的宗教——"
         "祆教史上唯一一份由當事祭司親自刻下的宗教鎮壓紀錄。")
D("Adurbad i Mahraspandan", "阿杜爾巴德‧馬赫拉斯潘丹", lang="pal", var="阿都爾巴德",
  etype="祭司", domain="四世紀祭司長",
  reason="傳受熔銅神判而不傷；今傳阿維斯陀的編定與《小阿維斯陀》的成書皆歸其名下。")
D("Zadspram", "扎德斯普拉姆", lang="pal", etype="祭司", domain="九世紀祭司、《選集》作者")
D("Manushchihr", "曼努什奇赫爾", lang="pal", etype="祭司", domain="九世紀祭司長、《宗教判例》作者",
  reason="其三封書信斥其弟扎德斯普拉姆擅改大淨禮，是有明確年份（881）的祆教文獻。")
D("Mardanfarrokh", "馬爾丹法魯赫", lang="pal", etype="祭司", domain="《破疑釋惑》作者",
  reason="自陳曾遍訪各教、讀其經書而後歸信祆教，故其書採比較宗教的論證體例。")
D("Adur-Farnbag", "阿杜爾法恩巴格", lang="pal", etype="祭司", domain="九世紀祭司長、《丹卡爾德》初編者")
D("Arda Wiraz", "阿爾達‧維拉茲", lang="pal", var="阿爾達‧維拉夫", root="維拉茲", etype="祭司",
  domain="魂遊天地獄的義人",
  reason="名根與《阿爾達‧維拉茲書》一致；取中古波斯語讀音，不取英譯常見的 Viraf。")
D("Jamasp", "賈馬斯普", o="Jāmāspa", var="賈馬斯帕", etype="傳說人物", domain="維什塔斯帕王的智臣",
  reason="《賈馬斯普紀念書》託其名答王問未來之事。")
D("Tansar", "坦薩爾", lang="pal", var="托薩爾（Tōsar）", etype="祭司", domain="薩珊初期祭司長",
  reason="傳為阿爾達希爾一世的宗教顧問，《坦薩爾書信》託其名。")

# ════════════════ E. 地名 ════════════════

_ord["p"] = 9000
P("Airyanem Vaejah", "艾里亞納‧瓦埃賈", o="Airyanəm Vaējah", lang="ae",
  var="伊朗故土；埃蘭‧維吉（Ērān-wēz）", ptype="地區",
  reason="祆教傳說中的雅利安人故土、十六邦國之首、查拉圖斯特拉的降生地。"
         "位置不可考，學界多推定在阿姆河上游或花剌子模一帶。")
P("Bisotun", "貝希斯敦", o="Bagastāna", lang="peo", var="比索通；貝希斯通",
  ptype="遺址", modern="伊朗克爾曼沙赫省",
  reason="原文 Bagastāna「諸神之地」。大流士一世三語巨碑所在；"
         "十九世紀羅林森據此碑破譯楔形文字，是亞述學的起點。")
P("Naqsh-e Rostam", "納克什伊魯斯塔姆", lang="fa", var="納克什‧魯斯塔姆；魯斯塔姆浮雕",
  ptype="遺址", modern="伊朗法爾斯省",
  reason="阿契美尼德四王崖墓與薩珊浮雕所在；沙普爾一世立方體銘文與卡爾提爾銘文皆在此。")
P("Paikuli", "派庫利", lang="fa", ptype="遺址", modern="伊拉克庫德斯坦",
  reason="納爾塞奪位自辯長文所在的塔基遺址。")
P("Yazd", "亞茲德", lang="fa", ptype="城市", modern="伊朗亞茲德省",
  reason="伊朗祆教社群的中心，聖火與火廟延續至今；印度帕西社群三百年來的請益對象。")
P("Kerman", "克爾曼", lang="fa", var="奇爾曼", ptype="城市", modern="伊朗克爾曼省",
  reason="與亞茲德並列的伊朗祆教兩大聚居地。")
P("Sanjan", "桑賈恩", lang="fa", var="珊賈恩", ptype="城市", modern="印度古吉拉特邦",
  reason="帕西人渡海抵印度的登陸地，《桑賈恩紀事》所敘；伊朗沙聖火最初供奉處。")
P("Navsari", "納夫薩里", ptype="城市", modern="印度古吉拉特邦",
  reason="帕西祭司世系的中心，《納夫薩里祭司世系》所記。")


# ════════════════ 寫入 ════════════════

def check_roots(rows, name_key):
    return [(r[name_key], r.get("name_root")) for r in rows
            if r.get("name_root") and r["name_root"] not in (r.get("name_recommended") or r.get("zh_recommended") or "")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="實際寫入（預設只預覽）")
    a = ap.parse_args()

    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    hj = {**h, "Content-Type": "application/json"}
    h_up = {**hj, "Prefer": "resolution=merge-duplicates,return=minimal"}

    # 自檢
    ok = True
    for label, rows, k in (("works", WORKS, "term_english"),
                           ("deities", DEITIES, "name_english"),
                           ("places", PLACES, "name_english")):
        seen: dict[str, int] = {}
        for r in rows:
            seen[r[k]] = seen.get(r[k], 0) + 1
        dup = {x: n for x, n in seen.items() if n > 1}
        if dup:
            print(f"⚠️  {label} 重複鍵：{dup}")
            ok = False
        bad = check_roots(rows, k)
        if bad:
            print(f"⚠️  {label} 名根不一致：{bad}")
            ok = False
    print("✓ 自檢通過（無重複鍵、名根一致）" if ok else "✗ 自檢有問題")

    print(f"\n經典與文獻名 {len(WORKS)}　神祇／概念／人物 {len(DEITIES)}　地名 {len(PLACES)}"
          f"　＝ 共 {len(WORKS) + len(DEITIES) + len(PLACES)} 筆")

    if not a.run:
        for r in WORKS:
            print(f"  [work ] {r['term_english']:<34} → {r['zh_recommended']}")
        for r in DEITIES:
            print(f"  [{r['entity_type']:<5}] {r['name_english']:<34} → {r['name_recommended']}")
        for r in PLACES:
            print(f"  [place] {r['name_english']:<34} → {r['name_recommended']}")
        print("\n（預覽，未寫入。加 --run 實際寫入）")
        return 0 if ok else 1
    if not ok:
        print("自檢未過，不寫入。")
        return 1

    # deities / place_names 有 name_english unique constraint，可直接 upsert
    for table, rows in (("deities", DEITIES), ("place_names", PLACES)):
        for i in range(0, len(rows), 100):
            b = rows[i:i + 100]
            r = requests.post(f"{url}/rest/v1/{table}?on_conflict=name_english",
                              headers=h_up, json=b, timeout=90)
            if r.status_code >= 300:
                print(f"  [{table}] ERROR {r.status_code}: {r.text[:300]}")
                return 1
            print(f"  ✓ {table} upserted {len(b)}")

    # theological_terms 無 unique constraint：先查再決定 insert 或 patch
    exist = requests.get(
        f"{url}/rest/v1/theological_terms?entity_type=eq.work&select=id,term_english",
        headers=h, timeout=60).json()
    have = {(x.get("term_english") or "").strip(): x["id"] for x in exist}
    ins = [r for r in WORKS if r["term_english"] not in have]
    upd = [r for r in WORKS if r["term_english"] in have]
    if ins:
        r = requests.post(f"{url}/rest/v1/theological_terms", headers=h_up, json=ins, timeout=90)
        if r.status_code >= 300:
            print(f"  [terms] INSERT ERROR {r.status_code}: {r.text[:300]}")
            return 1
        print(f"  ✓ theological_terms inserted {len(ins)}")
    for r0 in upd:
        rid = have[r0["term_english"]]
        rr = requests.patch(f"{url}/rest/v1/theological_terms?id=eq.{rid}",
                            headers=h_up, json=r0, timeout=60)
        if rr.status_code >= 300:
            print(f"  [terms] PATCH {r0['term_english']} 失敗 {rr.status_code}: {rr.text[:200]}")
    if upd:
        print(f"  ✓ theological_terms patched {len(upd)}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
