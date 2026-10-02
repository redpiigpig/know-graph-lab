# 月燈三昧經（三昧王經 Samādhirāja）異譯對讀：一品一組，品號＝梵本品號。
# 本檔由 tripitaka_compare.py 以其全域 exec（SETS、_bo、_z 等可直接用）。
#
# 本子：梵本 GRETIL sa_samAdhirAjasUtra（Vaidya 1961，40 品，頌號 SRS_品.頌）；
#       藏譯 Toh 127＋84000 英譯（TMX 9,329 句，40 章）；
#       那連提耶舍 T0639（557 年，十卷，CBETA 不分品——各品起訖用 start／end 以內容定界，範圍錨點）；
#       先公 T0640（＝梵本第 26–28 品「十事」一段的別行本）、T0641（宋藏本，六種不可思議，對梵本第 23 品）。
# 🚨 藏譯章次與梵本不同：梵本第 22 品＝藏譯第 22＋23 章；梵本第 23–38 品＝藏譯第 24–39 章；梵本第 39、40 品＝藏譯第 40 章。
#    下表已換算成「梵本第 k 品的 TMX 起句」（藏譯章題句多與上一章章尾題同在一句，歸本品開頭）。

_SR_TMX = [0, 108, 221, 371, 456, 608, 699, 835, 927, 1210, 1729, 1963, 2059, 2185, 2497, 2555, 2672, 3337, 3500, 3615,
           3664, 3786, 3964, 4163, 4393, 4444, 4493, 4522, 4893, 5299, 5343, 5468, 6408, 6587, 6819, 7661, 7945, 8318, 8752,
           None, 9329]
_SR_HEAD = {1: "sarvadharmasvabhāvasamatāvipañcita-Samādhirājasūtram", 2: "2 Śālendrarājapūrvayogaparivarto",
            3: "3 Bhūtaguṇavarṇaprakāśanaparivartaḥ", 4: "4 Buddhānusmṛtiparivartaḥ", 5: "5 Ghoṣadattaparivartaḥ",
            6: "6 Samādhiparivartaḥ", 7: "7 Trikṣāntyavatāraparivartaḥ", 8: "8 Abhāvasamudgataparivartaḥ",
            9: "9 Gambhīradharmakṣāntiparivartaḥ", 10: "10 Purapraveśaparivartaḥ", 11: "11 Sūtradhāraṇaparivartaḥ",
            12: "12 Samādhyanuśikṣaṇāparivartaḥ", 13: "13 Samādhinirdeśaparivartaḥ", 14: "14 Smitasaṃdarśanaparivartaḥ",
            15: "15 Smitavyākaraṇaparivartaḥ", 16: "16 Pūrvayogaparivartaḥ", 17: "17 Bahubuddhanirhārasamādhimukhaparivartaḥ",
            18: "18 Samādhyanuparindanaparivartaḥ", 19: "19 Acintyabuddhadharmanirdeśaparivartaḥ",
            20: "20 Indraketudhvajarājaparivartaḥ", 21: "21 Pūrvayogaparivartaḥ", 22: "22 Tathāgatakāyanirdeśaparivartaḥ",
            23: "23 Tathāgatācintyanirdeśaparivartaḥ", 24: "24 Pratisaṃvidavatāraparivartaḥ", 25: "25 Anumodanāparivartaḥ",
            26: "26 Dānānuśaṃsāparivartaḥ", 27: "27 Śīlanirdeśaparivartaḥ", 28: "28 Daśānuśaṃsāparivartaḥ",
            29: "29 Tejaguṇarājaparivartaḥ", 30: "30 Anuśaṃsāparivartaḥ", 31: "31 Sarvadharmasvabhāvanirdeśaparivartaḥ",
            32: "32 Sūtradhāraṇānuśaṃsāparivartaḥ", 33: "33 Kṣemadattaparivartaḥ", 34: "34 Jñānāvatīparivartaḥ",
            35: "35 Supuṣpacandraparivartaḥ", 36: "36 Śīlaskandhanirdeśaparivartaḥ", 37: "37 Yaśaḥprabhaparivartaḥ",
            38: "38 Kāyavāṅmanaḥsaṃvaraparivartaḥ", 39: "39 Padatriśatanirdeśaparivartaḥ", 40: "40 Parīndanāparivartaḥ"}
# 那連提耶舍本各品起頭（＝上一品的 end）。CBETA 此經不分品，以梵藏內容逐品比定。
_SR_ZH0 = {1: "如是我聞", 2: "爾時，世尊而說偈言：「我念往劫", 3: "「童子！以是義故，若有菩薩摩訶薩欲於如來真實功德",
           4: "爾時，月光童子白佛言：「世尊！所言三昧", 5: "爾時，世尊告月光童子言：「過去久遠無量無邊",
           6: "「童子！是故，菩薩摩訶薩愛樂是定者", 7: "「童子！是故，菩薩摩訶薩應善巧知入三法忍",
           8: "爾時，佛告月光童子言：「於過去廣大久遠無量無數", 9: "「童子！菩薩摩訶薩當安住深忍法中",
           10: "「童子！以是義故，欲得成就堅固行", 11: "爾時，世尊與諸比丘前後圍遶往詣月光童子住處"}


def _sr(k, title, intro, units, sa_cuts, en, zh_cuts, extra=()):
    """sa_cuts 首刀＝品題（第一品＝經題）；en＝[(義段, TMX 絕對句號)]；zh_cuts＝那連提耶舍本切點（首刀＝本品起頭）。"""
    a, b = _SR_TMX[k - 1], _SR_TMX[k]
    if zh_cuts and zh_cuts[0][1] != _SR_ZH0.get(k):
        raise SystemExit(f"  ✗ samadhiraja-c{k:02d}: 漢譯首刀與 _SR_ZH0 不一致")
    vs = [{"id": "sa", "lang": "sa", "label": "梵本", "who": "Vaidya 校訂本（1961）・GRETIL",
           "src": {"gretil": "sa_samAdhirAjasUtra", "start": sa_cuts[0][1]} | ({"end": _SR_HEAD[k + 1]} if k < 40 else {}),
           "cuts": sa_cuts}]
    if en:
        vs += _bo("toh127", a, b, [(u, n - a) for u, n in en], "德格版 Toh 127・84000 翻譯記憶")
    if zh_cuts:
        vs.append({"id": "T0639", "lang": "lzh", "label": "那連提耶舍本", "who": "那連提耶舍譯《月燈三昧經》・557 年",
                   "src": {"work": "T0639", "start": zh_cuts[0][1], "end": _SR_ZH0[k + 1] if k < 40 else "存疑",
                           "anchor_nodes": []}, "cuts": zh_cuts})
    vs += list(extra)
    SETS[f"samadhiraja-c{k:02d}"] = {"title": f"月燈三昧經・第{k}品 {title}", "family": "sa", "extra_works": ["DKtoh0127"],
                                     "intro": intro, "units": units, "versions": vs}


_sr(1, "序品（Nidāna）",
    "梵本〈Nidānaparivarta〉＝藏譯第一章＝那連提耶舍本卷一開頭。月光童子（Candraprabha）以偈請問，佛答「一法」（於眾生平等心）；"
    "梵本以三百餘句列舉「一切法體性平等無戲論三昧」之相，那連提耶舍本改作二十組「十法」，末段「名為因、名為相應…」對梵本 hetuyuktinaya 以下諸句。"
    "藏英此段數百句只成三句（TMX 92–94），說法利益的開頭也在第 94 句內。",
    [("c01-1", "序：說處・與會大眾"), ("c01-2", "月光童子請問・佛許"), ("c01-3", "月光童子問偈"),
     ("c01-4", "一法：於一切眾生平等心・偈"), ("c01-5", "三昧之相（諸句）"), ("c01-6", "說法利益・大地六種震動・光明照幽冥")],
    [("c01-1", _SR_HEAD[1]), ("c01-2", "tena khalu punaḥ samayena tasminneva parṣatsaṃnipāte candraprabho"),
     ("c01-3", "atha khalu candraprabhaḥ kumārabhūtastuṣṭa"),
     ("c01-4", "atha khalu bhagavāṃścandraprabhaṃ kumārabhūtametadavocat - ekadharmeṇa"),
     ("c01-5", "tatra kumāra sarvasattveṣu samacitto"), ("c01-6", "asmin khalu punaḥ sarvadharmaparyāye samādhinirdeśe")],
    [("c01-1", 0), ("c01-2", 25), ("c01-3", 34), ("c01-4", 69), ("c01-5", 91), ("c01-6", 95)],
    [("c01-1", "如是我聞"), ("c01-2", "時此眾中有菩薩名月光童子"), ("c01-3", "爾時，童子以偈問曰"),
     ("c01-4", "爾時，佛告月光童子：「菩薩摩訶薩若與一法"), ("c01-5", "「童子！菩薩摩訶薩於一切眾生起平等心"),
     ("c01-6", "說是法門時，會中有八十那由他")])

_sr(2, "娑羅王本事品（Śālendrarāja）",
    "梵本〈Śālendrarājapūrvayoga〉全品是偈（SRS 2.1–30）：佛自述往昔為王（梵 Bhīṣmottara／漢毘沙謨達）於娑羅樹王佛所出家求此三昧，"
    "憶恒沙同名釋迦諸佛，說得此三昧不難之行與持一偈功德。藏譯章首另有一段長行（佛說往昔供養諸佛），梵本與那連提耶舍本皆無。"
    "那連提耶舍本 29 頌，梵本 2.26（諸佛攝受、天龍隨從）併入 2.25。",
    [("c02-0", "藏譯長行：往昔供養諸佛・娑羅王佛所出家"), ("c02-1", "偈：娑羅王佛時為王出家求此三昧（2.1–11）"),
     ("c02-2", "偈：恒沙同名釋迦諸佛（2.12–15）"), ("c02-3", "偈：得是三昧則不難（2.16–21）"),
     ("c02-4", "偈：持一偈功德・囑後世受持（2.22–30）")],
    [("c02-1", _SR_HEAD[2]), ("c02-2", "smarāmi buddhāna sahasrakoṭiyo"), ("c02-3", "pratipattiya eṣa samādhi labhyate"),
     ("c02-4", "buddhena ye cakṣuṣa dṛṣṭa")],
    [("c02-0", 108), ("c02-1", 123), ("c02-2", 157), ("c02-3", 173), ("c02-4", 190)],
    [("c02-1", _SR_ZH0[2]), ("c02-2", "念昔百億諸如來"), ("c02-3", "發修勝行得此定"), ("c02-4", "佛眼所見諸眾生")])

_sr(3, "顯如來實德品（Bhūtaguṇavarṇaprakāśana）",
    "梵本〈Bhūtaguṇavarṇaprakāśana〉＝藏譯第三章。長行列如來實德名號，偈頌自述往昔捨施求此三昧、持四句偈之福；"
    "後段預言末世比丘「說戒而得活」（栴檀香喻）、貧人得藏喻；月光童子與五百人誓願護持。梵本偈頌前的勸持長行（3.17 後）藏譯無。"
    "那連提耶舍本「說…而得活」多出「知見」一項。",
    [("c03-1", "長行：如來實德名號"), ("c03-2", "偈：往昔捨施求此三昧（3.1–10）"), ("c03-3", "偈：持一四句偈福過布施（3.11–17）"),
     ("c03-4", "勸受持・偈：七億三千萬佛說此經・名入大悲（3.18–20）"), ("c03-5", "偈：末世比丘說戒而得活・栴檀香喻（3.21–30）"),
     ("c03-6", "偈：貧人得藏喻・三世諸佛學此三昧（3.31–35）"), ("c03-7", "月光童子誓願護持・五百人同持（3.36–39）")],
    [("c03-1", _SR_HEAD[3]), ("c03-2", "atha bhagavāṃstasyāṃ velāyāmimā gāthā abhāṣata"),
     ("c03-3", "bahuśruta śrutadhāri ye bhavanti"), ("c03-4", "tasmāttarhi kumāra bodhisattven mahāsattvena udgrahītavyo"),
     ("c03-5", "bheṣyanti paścime kāle"), ("c03-6", "yatha puruṣu daridru"), ("c03-7", "candraprabhaḥ kumāru hṛṣṭacittaḥ")],
    [("c03-1", 221), ("c03-2", 258), ("c03-3", 289), ("c03-4", 306), ("c03-5", 313), ("c03-6", 342), ("c03-7", 357)],
    [("c03-1", _SR_ZH0[3]), ("c03-2", "爾時，世尊而說偈言：「於無量數千劫中"), ("c03-3", "若有多聞能受持"),
     ("c03-4", "「童子！以是義故，菩薩摩訶薩於是三昧應當至心受持"), ("c03-5", "若能於彼末世時"), ("c03-6", "譬如貧賤為他欺"),
     ("c03-7", "月光童子心歡喜")])

_sr(4, "念佛品（Buddhānusmṛti）",
    "梵本〈Buddhānusmṛti〉＝藏譯第四章（章名〈三昧〉）。月光童子問「何謂三昧」，佛以一連串句子答（那連提耶舍本列四十句）；"
    "偈頌（SRS 4.1–25）說念佛相好而入無相、知法身、臨終不失念佛。藏譯章首多月光童子再請問許的數句。",
    [("c04-1", "月光童子問三昧・佛答三昧之相"), ("c04-2", "偈：開甘露門・離惡友・持戒頭陀則得此定（4.1–8）"),
     ("c04-3", "偈：念佛相好・入無相・住法身（4.9–15）"), ("c04-4", "偈：念佛常見諸佛・臨終不失・勸修（4.16–25）")],
    [("c04-1", _SR_HEAD[4]), ("c04-2", "atha khalu bhagavāṃstasyāṃ velāyāmimā gāthā abhāṣata"),
     ("c04-3", "ākārato yaḥ smarate tathāgatān"), ("c04-4", "ārocayāmi prativedayāmi")],
    [("c04-1", 371), ("c04-2", 378), ("c04-3", 404), ("c04-4", 424)],
    [("c04-1", _SR_ZH0[4]), ("c04-2", "爾時，世尊而說偈言：「我已開於甘露門"), ("c04-3", "念佛相好及德行"), ("c04-4", "我今為汝善說之")])

_sr(5, "聲德佛品（Ghoṣadatta）",
    "梵本〈Ghoṣadatta〉＝藏譯第五章。過去聲德佛（Ghoṣadatta）時二王分治閻浮提，大力王（Mahābala）與婆羅門居士以財食供養；"
    "佛念眾生唯求世樂，說出家偈；大力王與八萬人出家持此三昧，後成智勇佛（Jñānaśūra）與堅勇諸佛。"
    "藏譯章首多一段長行（勸捨親友眷屬、以此三昧速成菩提），梵本與那連提耶舍本皆無。",
    [("c05-0", "藏譯長行：勸捨眷屬・依此三昧速成菩提"), ("c05-1", "聲德佛出世・二王・大力王財食供養"),
     ("c05-2", "聲德佛念眾生唯求世福・說出家偈（5.1–11）"), ("c05-3", "大力王與八萬人出家持此三昧・後皆成佛"),
     ("c05-4", "偈：重頌本事（5.12–28）")],
    [("c05-1", _SR_HEAD[5]), ("c05-2", "iti hi kumāra tasya bhagavato ghoṣadattasya etadabhūt"),
     ("c05-3", "aśrauṣīt khalu punaḥ kumāra rājā mahābalo"),
     ("c05-4", "atha khalu bhagavāṃścandraprabhasya kumārabhūtasya tasyāṃ velāyāmetadeva pūrvayoga")],
    [("c05-0", 456), ("c05-1", 462), ("c05-2", 477), ("c05-3", 522), ("c05-4", 548)],
    [("c05-1", _SR_ZH0[5]), ("c05-2", "「童子！時聲德如來作如是念"), ("c05-3", "「童子！時大力王聞聲德如來"),
     ("c05-4", "爾時，世尊欲重宣此義而說偈言：「我念過去久遠世")])

_sr(6, "三昧品（Samādhi）",
    "梵本〈Samādhi〉＝藏譯第六章（〈修此三昧〉）＝那連提耶舍本「此三昧最初所行」。長行說三輪清淨供養如來；"
    "偈頌（SRS 6.1–25）說香供養之果、隨順忍與不退之名義、魔化佛身而不退、菩薩但有假名、貪著懈怠者不知菩提。"
    "那連提耶舍本七言偈以半頌錯開排列，切點落在句中。",
    [("c06-1", "長行：最初所行・三輪清淨供養"), ("c06-2", "偈：香供養・順忍名義（6.1–7）"),
     ("c06-3", "偈：魔化佛身不退・無我・菩薩假名（6.8–16）"), ("c06-4", "偈：貪著懈怠不知菩提・能知者・勸持（6.17–25）")],
    [("c06-1", _SR_HEAD[6]), ("c06-2", "atha khalu bhagavāṃstasyāṃ velāyāṃ candraprabhasya kumārabhūtasya etadeva samādhiparikarma"),
     ("c06-3", "evaṃ carantasya ya loki mārāste"), ("c06-4", "na cāpi āhāravimūrchitehi")],
    [("c06-1", 608), ("c06-2", 618), ("c06-3", 643), ("c06-4", 675)],
    [("c06-1", _SR_ZH0[6]), ("c06-2", "爾時，世尊即說偈言：「若人香奉無邊智"), ("c06-3", "若修行時有世魔"), ("c06-4", "若於飲食生貪著")])

_sr(7, "入三忍品（Trikṣāntyavatāra）",
    "梵本〈Trikṣāntyavatāra〉＝藏譯第七章（〈得忍〉）。長行勸善巧知三忍；偈頌（SRS 7.1–38）分說三忍之相、三忍名（隨順音聲忍、思惟忍、修習無生忍）、"
    "得忍授記、地動、刀割不瞋。🚨 三忍的分界各本不同：梵藏第 7、8 頌末才標「初忍」，那連提耶舍本第 1–4 頌即標初忍、第 6–8 頌標第二忍；本組依頌號分節，不依此標籤。",
    [("c07-1", "長行：應善巧知三忍"), ("c07-2", "偈：初、二忍之相（7.1–8）"), ("c07-3", "偈：工巧・止觀・神通・化身・利衰不動（7.9–21）"),
     ("c07-4", "偈：三忍之名・授記・地動（7.22–25）"), ("c07-5", "偈：得三忍者不見生死・刀割不瞋・勸修（7.26–38）")],
    [("c07-1", _SR_HEAD[7]), ("c07-2", "atha khalu bhagavāṃścandraprabhasya kumārabhūtasyemaṃ trikṣānty"),
     ("c07-3", "ye śilpasthānā pṛthu asti loke"), ("c07-4", "ghoṣānugāmī iya kṣāntiruktā"), ("c07-5", "kṣāntyā imāstisra niruttarā yadā")],
    [("c07-1", 699), ("c07-2", 710), ("c07-3", 737), ("c07-4", 779), ("c07-5", 793)],
    [("c07-1", _SR_ZH0[7]), ("c07-2", "爾時，世尊為彼月光童子即以偈句"), ("c07-3", "世間所有諸工巧"), ("c07-4", "一名、隨順音聲忍"),
     ("c07-5", "若於如是三勝忍，其有菩薩")])

_sr(8, "無所有起佛品（Abhāvasamudgata）",
    "梵本〈Abhāvasamudgata〉＝藏譯第八章。過去無所有起佛（Abhāvasamudgata）初生即說「一切諸法悉無所有」，草木皆出此聲；"
    "思惟大悲王子（Mahākaruṇācintin）聞此三昧出家，後成善思義佛。藏譯章首另有一段「諸法無有自性智」長行與四句偈，梵本、那連提耶舍本皆無；"
    "那連提耶舍本無重頌（SRS 8.1–12）。梵本末頌 8.12 在藏譯歸入下一章章首。",
    [("c08-0", "藏譯長行：諸法無有自性智・偈"), ("c08-1", "無所有起佛出世・名號因緣"), ("c08-2", "思惟大悲王子出家・成善思義佛"),
     ("c08-3", "偈：重頌本事（8.1–12）")],
    [("c08-1", _SR_HEAD[8]), ("c08-2", "tena ca kumāra kālena tena samayena tasya bhagavato 'bhāvasamudgatasya"),
     ("c08-3", "atha khalu bhagavāṃstasyāṃ velāyāmimā gāthā abhāṣata")],
    [("c08-0", 835), ("c08-1", 860), ("c08-2", 871), ("c08-3", 886)],
    [("c08-1", _SR_ZH0[8]), ("c08-2", "「童子！爾時無所有起如來所說法時，有一王子")])

_sr(9, "甚深法忍品（Gambhīradharmakṣānti）",
    "梵本〈Gambhīradharmakṣānti〉＝藏譯第九章＝那連提耶舍本「安住深忍」。知諸法如幻則不見染瞋癡，得種種名號；"
    "偈頌（梵 66 頌，那連提耶舍本五言 60 頌）：諸法如幻之喻、有無二邊、說四念處四禪而起慢、多聞不持戒、遠離愚人。"
    "藏譯章首多讚此三昧王一段及一頌（＝梵本 8.12）。🚨 第一組喻的次第那連提耶舍本與梵藏不同（陽燄、山谷響、牓教、醉人；"
    "「觀彼先際身」在「眼耳鼻無限」之前），第 1–28 頌整組對讀。",
    [("c09-0", "藏譯：此三昧王出生諸佛・偈"), ("c09-1", "甚深法忍：知諸法如幻・不見染瞋癡"), ("c09-2", "無染無瞋無癡・得種種名"),
     ("c09-3", "偈：諸法如幻諸喻・有無二邊（9.1–28）"), ("c09-4", "偈：說法而起慢・持戒多聞・諸喻（9.29–47）"),
     ("c09-5", "偈：智者遠離愚人・慈悲喜捨（9.48–66）")],
    [("c09-1", _SR_HEAD[9]), ("c09-2", "taṃ dharmamasamanupaśyannanupalabhamāno"),
     ("c09-3", "atha khalu bhagavāstasyāṃ velāyamimā gāthā abhāṣata"), ("c09-4", "smṛterupasthānakathāṃ kathitvā"),
     ("c09-5", "na vijña bālehi karonti vigrahaṃ")],
    [("c09-0", 927), ("c09-1", 936), ("c09-2", 946), ("c09-3", 980), ("c09-4", 1076), ("c09-5", 1146)],
    [("c09-1", _SR_ZH0[9]), ("c09-2", "「是菩薩如實無染"), ("c09-3", "爾時，世尊說偈頌曰"), ("c09-4", "演說四念處"),
     ("c09-5", "智不與愚競")])

_sr(10, "入城品（Purapraveśa）",
    "梵本〈Purapraveśa〉＝藏譯第十章。佛勸以「堅固行」（pratipattisāra）為要，月光童子請佛明日受供，連夜莊嚴王舍城；"
    "佛與大眾入城，足躡門閫，大地震動，偈頌（梵 90 頌，那連提耶舍本 84 頌）讚入城瑞相與諸天龍夜叉來會。"
    "🚨 藏譯此章大為增廣：佛摩頂、月光讚佛、莊嚴道路、迎佛、大眾隨行等都有梵本所無的偈頌（TMX 以羅馬數字 {i}…{xlv} 編號），"
    "只依長行位置併入各節；梵本頌號自 TMX 1415 起。",
    [("c10-1", "堅固行・月光童子請佛受供・佛默然許"), ("c10-2", "還家莊嚴王城・往請世尊"), ("c10-3", "世尊與大眾入城・足躡門閫・地動"),
     ("c10-4", "偈：入城瑞相・眾人供養（10.1–32）"), ("c10-5", "偈：梵釋侍衛・化身說法・眾人發心（10.33–48）"),
     ("c10-6", "偈：諸天龍夜叉仙人來會・結讚（10.49–90）")],
    [("c10-1", _SR_HEAD[10]), ("c10-2", "atha khalu candaprabhaḥ kumārabhūto yena rājagṛhaṃ"),
     ("c10-3", "atha khalu bhagavān utthāyāsanāt kalyameva"), ("c10-4", "tatredamucyate"),
     ("c10-5", "brahma daśabalasya dakṣiṇeno"), ("c10-6", "abṛha atapāśca")],
    [("c10-1", 1210), ("c10-2", 1249), ("c10-3", 1356), ("c10-4", 1414), ("c10-5", 1517), ("c10-6", 1570)],
    [("c10-1", _SR_ZH0[10]), ("c10-2", "爾時，月光童子向王舍城還至家中"), ("c10-3", "爾時，世尊於中前時著衣持鉢"),
     ("c10-4", "說偈頌曰"), ("c10-5", "右有百千梵"), ("c10-6", "無煩熱見諦")])
