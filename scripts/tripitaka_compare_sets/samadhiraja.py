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
           4: "爾時，月光童子白佛言：「世尊！所言三昧"}


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
