# 比丘戒本（波羅提木叉）異譯對讀人工版：巴利、梵本三部、漢譯六部，一篇聚一組。
# 本檔由 tripitaka_compare.py 以其全域 exec（SETS 等可直接用）。
#
# 骨架＝巴利 Pātimokkha（上座部）的條目次第與編號；他部同義之條依條文內容歸同節，
# 原本次第不同者設 reorder（各部條目次第本就不同，這是戒本對讀的常態，不是錯排）；
# 他部獨有之條單列一節，排在該部原次第的鄰近處。
# 一段裡併說數條的（根有戒經眾學法「不太高、不太下、不象鼻…著裙」）整段歸第一條，其餘各節該本空著。
# 切點字串由人工對照表（每本每條「第幾段起」）產生，不經模型自動對齊。
#
# 巴利本取 SuttaCentral bilara 的 Mahāsaṅgīti 本（pli-tv-bu-pm），快取在 C:/tmp/cbeta/sc-data。
# 主檔 orig_lines() 只認 tmx／gretil／refs／orig 四種來源；這裡把 gretil_paras 包一層，
# 名稱以 "sc:" 起頭的改讀 bilara 根本文（一段一行），其餘照舊交給原函式。

import json as _pm_json
from pathlib import Path as _PmPath

try:
    import tripitaka_compare_curated as _pm_tcc
    if not getattr(_pm_tcc, "_pm_sc_patched", False):
        _pm_gretil_orig = _pm_tcc.gretil_paras

        def _pm_gretil_paras(name):
            if name.startswith("sc:"):
                p = _PmPath("C:/tmp/cbeta/sc-data/sc_bilara_data/root/pli/ms/vinaya") / f"{name[3:]}_root-pli-ms.json"
                d = _pm_json.loads(p.read_text(encoding="utf-8"))
                return [v.strip() for v in d.values() if v.strip()]
            return _pm_gretil_orig(name)

        _pm_tcc.gretil_paras = _pm_gretil_paras
        _pm_tcc._pm_sc_patched = True
except ImportError:
    pass


# 欄序依部派：上座、法藏、化地、說一切有、大眾（說出世）、飲光、根本說一切有。
_PM_VERS = [
    ("pi", "pi", "巴利・上座部", "Theravāda Bhikkhupātimokkha・Mahāsaṅgīti 本（SuttaCentral）", {"gretil": "sc:pli-tv-bu-pm"}),
    ("T1429", "lzh", "四分戒本", "法藏部・後秦 佛陀耶舍譯《四分律比丘戒本》（唐 懷素集）", {"work": "T1429"}),
    ("T1422a", "lzh", "五分戒本", "化地部・劉宋 佛陀什等譯《彌沙塞五分戒本》", {"work": "T1422a"}),
    ("sa-sarv", "sa", "梵・說一切有部", "Sarvāstivāda Prātimokṣasūtra・von Simson 1986／2000（GRETIL）", {"gretil": "sa_prAtimokSasUtra-of-the-sarvAstivAdins"}),
    ("T1436", "lzh", "十誦戒本", "說一切有部・姚秦 鳩摩羅什譯《十誦比丘波羅提木叉戒本》", {"work": "T1436"}),
    ("sa-mahl", "sa", "梵・大眾說出世部", "Mahāsāṃghika-Lokottaravāda Prātimokṣasūtra・Tatia 1976（GRETIL）", {"gretil": "sa_prAtimokSasUtra-of-the-lokottaravAdimahAsaGghika"}),
    ("T1426", "lzh", "僧祇戒本", "大眾部・東晉 佛陀跋陀羅譯《摩訶僧祇律大比丘戒本》", {"work": "T1426"}),
    ("T1460", "lzh", "解脫戒經", "飲光部・元魏 般若流支譯", {"work": "T1460"}),
    ("sa-mula", "sa", "梵・根本說一切有部", "Mūlasarvāstivāda Prātimokṣasūtra・Banerjee 1954（GRETIL）", {"gretil": "sa_prAtimokSasUtra-of-the-mUlasarvAstivAdins"}),
    ("T1454", "lzh", "根有戒經", "根本說一切有部・唐 義淨譯《根本說一切有部戒經》", {"work": "T1454"}),
]


def _pm(title, intro, units, cuts):
    """cuts：{本: (end 或 None, reorder, [(義段, 從哪幾個字起), …])}；第一刀即 start。
    漢譯一律 anchor_nodes=[]（戒本不分品，一部跨十組，閱讀器改掛段落 uid 起訖）。"""
    vs = []
    for vid, lang, label, who, base in _PM_VERS:
        if vid not in cuts:
            continue
        end, reorder, cc = cuts[vid]
        src = dict(base) | {"start": cc[0][1]}
        if end:
            src["end"] = end
        if "work" in base:
            src["anchor_nodes"] = []
        v = {"id": vid, "lang": lang, "label": label, "who": who, "src": src, "cuts": cc}
        if reorder:
            v["reorder"] = True
        vs.append(v)
    return {"title": title, "family": "pi", "intro": intro, "units": units, "versions": vs}


SETS['pratimoksa-c01'] = _pm(
    '比丘戒本（一）序：說戒緣起',
    '波羅提木叉（別解脫）是半月布薩時誦出的比丘學處條文，各部律各有一本，條數二百二十七（巴利）至二百六十三（說一切有部梵本）不等。本對讀收十本：巴利《比丘波羅提木叉》（上座部）、梵本三部（說一切有部、大眾說出世部、根本說一切有部），漢譯六部：《四分戒本》（法藏部）、《五分戒本》（化地部）、《十誦戒本》（說一切有部）、《僧祇戒本》（大眾部）、《解脫戒經》（飲光部）、義淨《根本說一切有部戒經》。一篇聚一組，節的次第與編號一律照巴利本，他部次第不同者標「段序依原本」。未收：大眾部梵本另一校本（Pachow & Mishra 1956，與 Tatia 本同屬大眾說出世部，取 Tatia 本）、GRETIL 的梵本殘片集（sa_prAtimokSasUtrafragments）；大正藏 T1422b《五分戒本》（「丹本」）經文字比對與《十誦戒本》相合（九十波夜提、眾學一百零七、闡陀偈句、殺眾草木等皆十誦系文句），不是化地部本，不收，五分取 T1422a《彌沙塞五分戒本》（九十一波逸提、眾學一百，與《五分律》相合）；《四分僧戒本》T1430 與 T1429 同出佛陀耶舍，取懷素集本。本組是說戒前的序分。各本詳略差異很大：讚戒偈有「稽首禮諸佛」（四分）、「是解脫戒經」（解脫戒經）、「別解脫經難得聞」（根有，梵本根有第 1–13 頌同文）、大眾說出世部梵本的 upodghāta 五頌與 vastu 諸頌；「合十指爪掌」偈見於五分、十誦、僧祇、根有（「合十指恭敬」，梵本根有第 14–19 頌），說一切有部梵本此處是讚別解脫的六首 āryā 頌（Einl. III），位置與作用相同，歸同一節。「冬時一月過少一夜…老死至近，佛法欲滅」（時節與勸精進）巴利、四分無；說一切有部梵本把集僧、說欲（前行問答）放在時節之前，大眾說出世部梵本把白羯磨放在「老死至近」與十利之前，皆依原本次第。《解脫戒經》在篇首就誦出七佛略說戒偈（他本在戒本之末），單列一節；《僧祇戒本》卷首的「六念法」、《四分戒本》懷素集序與《解脫戒經》僧昉〈譯經緣起〉皆單列。巴利本卷首是後世加入的「前行（pubbakaraṇa）、前務（pubbakicca）、適時（pattakalla）」偈與請說戒文，歸前行一節。',
    [
        ('s0', '卷首後序：懷素〈四分比丘戒本序〉・僧昉〈譯經緣起〉'),
        ('s0b', '六念法（僧祇戒本卷首）'),
        ('s1', '讚戒偈（說戒緣起）'),
        ('s2', '時節：老死至近，佛法欲滅，當勤精進'),
        ('s3', '說戒前行：集僧、未受具者出、說欲清淨、比丘尼請教誡'),
        ('s3b', '七佛略說戒偈（解脫戒經置於篇首）'),
        ('s4', '說戒偈：合十指爪掌，我今欲說戒'),
        ('s5', '白羯磨：今十五日布薩說戒'),
        ('s6', '說戒序：有罪發露，無罪默然，故妄語障道'),
        ('s7', '已說戒序・三問清淨'),
    ],
    {
        'pi': ('Pārājikuddeso\nTatrime', False, [
            ('s3', 'Dvemātikāpāḷi\nTheravāda'),
            ('s5', 'Nidānuddeso\nSuṇātu'),
            ('s6', 'Kiṁ saṅghassa pubbakiccaṁ?'),
            ('s7', 'Uddiṭṭhaṁ kho āyasmanto'),
        ]),
        'T1429': ('「諸大德！是四', False, [
            ('s0', '四分比丘戒本'),
            ('s1', '稽首禮諸佛，'),
            ('s3', '「僧集？」（'),
            ('s5', '「大德僧聽！'),
            ('s6', '「諸大德！我'),
            ('s7', '「諸大德！我'),
        ]),
        'T1422a': ('「諸大德！是', False, [
            ('s2', '「大德僧聽！'),
            ('s3', '未受具戒者已'),
            ('s4', '合十指爪掌，'),
            ('s5', '「大德僧聽！'),
            ('s6', '「諸大德！今'),
            ('s7', '「諸大德已說'),
        ]),
        'sa-sarv': ('I. pārājikā dharmāḥ', True, [
            ('s3', 'EINLEITUNG (nidānam)'),
            ('s2', 'nirgatam āyuṣmanto'),
            ('s4', 'III\nPrMoSū_Einl.III.1:'),
            ('s5', 'IV\nśṛṇotu bhadantaḥ'),
            ('s6', 'poṣathaṃ vayam'),
            ('s7', 'V\nuddiṣṭaṃ mayāyuṣmantaḥ'),
        ]),
        'T1436': ('「諸大德！是四', False, [
            ('s2', '「大德僧聽！'),
            ('s3', '「未受具戒者'),
            ('s4', '「合十指爪掌'),
            ('s5', '「大德僧聽！'),
            ('s6', '「諸大德！今'),
            ('s7', '「諸大德！已'),
        ]),
        'sa-mahl': ('[I. catvāraḥ pārājikā', True, [
            ('s1', 'Prātimokṣasūtram*'),
            ('s3', 'PrMoSū(Mā-L)Einl.'),
            ('s5', 'śṛṇotu me bhante saṃgho Ō adya saṃghasya pāñcadaśiko'),
            ('s2', 'abhimukhaṃ krāmati'),
            ('s6', 'prātimokṣam āyuṣmanto'),
            ('s7', '// [iti] nidānaṃ'),
        ]),
        'T1426': ('「諸大德！是四', False, [
            ('s0b', '六念法「一者'),
            ('s2', '摩訶僧祇律波'),
            ('s3', '「未受具戒者'),
            ('s4', '「合十指爪掌'),
            ('s5', '「大德僧聽！'),
            ('s6', '「諸大德！今'),
            ('s7', '「諸大德！已'),
        ]),
        'T1460': ('「諸大德！此', False, [
            ('s0', '解脫戒經譯經'),
            ('s1', '是解脫戒經，'),
            ('s2', '「諸大德！時'),
            ('s3', '眾僧和合坐。'),
            ('s3b', '「毘婆尸如來'),
            ('s5', '「大德僧聽！'),
            ('s6', '「諸大德！今'),
            ('s7', '諸大德！我已'),
        ]),
        'sa-mula': ('catvāraḥ pārājikā', False, [
            ('s1', 'namaḥ sarvajñāya'),
            ('s2', 'nirgatam āyuṣmanto'),
            ('s3', 'kiṃ bhagavataḥ'),
            ('s4', 'praṇamya śākyasiṃhāya'),
            ('s5', 'śṛṇotu bhadantaḥ'),
            ('s6', 'poṣadhaṃ vayam'),
            ('s7', 'uddiṣṭaṃ khalu'),
        ]),
        'T1454': ('「諸大德！此', False, [
            ('s1', '別解脫經難得'),
            ('s2', '「諸大德！春'),
            ('s3', '大德僧伽！先'),
            ('s4', '合十指恭敬，'),
            ('s5', '「大德僧伽聽'),
            ('s6', '「諸大德！我'),
            ('s7', '諸大德！我已'),
        ]),
    })


SETS['pratimoksa-c02'] = _pm(
    '比丘戒本（二）四波羅夷',
    '四波羅夷（他勝、斷頭）各部條數、次第全同：婬、盜、斷人命、妄說過人法。巴利、說一切有部梵本、大眾說出世部梵本、根本說一切有部梵本與六部漢譯並排。《僧祇戒本》每條之後附制戒因緣（「佛在毘舍離城，成佛五年冬分第五半月十二日…」：何處、成道第幾年、何時、為誰而制），大眾說出世部梵本同樣在每條後記「idaṃ bhagavatā veśālīyaṃ śikṣāpadaṃ prajñaptaṃ…」，兩本互證，皆歸入該條；梵本篇末的攝頌（uddāna）與根有戒經篇首的攝頌一樣只列條名，前者歸結說、後者歸總標。篇首總標、篇末結說與三問清淨各立一節；《五分戒本》結說與問清淨在同一段。',
    [
        ('pj0', '總標：四波羅夷法半月半月說'),
        ('pj1', '波羅夷一・婬'),
        ('pj2', '波羅夷二・盜'),
        ('pj3', '波羅夷三・斷人命'),
        ('pj4', '波羅夷四・妄說過人法'),
        ('pjz', '結說・三問清淨'),
    ],
    {
        'pi': ('Saṅghādisesuddeso', False, [
            ('pj0', 'Pārājikuddeso\nTatrime'),
            ('pj1', 'Pārājika 1. Methunadhamma'),
            ('pj2', 'Pārājika 2. Adinnādāna'),
            ('pj3', 'Pārājika 3. Manussaviggaha'),
            ('pj4', 'Pārājika 4. Uttarimanussadhamma'),
            ('pjz', 'Uddiṭṭhā kho āyasmanto'),
        ]),
        'T1429': ('「諸大德！是十', False, [
            ('pj0', '「諸大德！是四'),
            ('pj1', '「若比丘！共'),
            ('pj2', '「若比丘！若'),
            ('pj3', '「若比丘！故'),
            ('pj4', '「若比丘！實'),
            ('pjz', '「諸大德！我'),
        ]),
        'T1422a': ('「諸大德！是十', False, [
            ('pj0', '「諸大德！是'),
            ('pj1', '「若比丘共諸'),
            ('pj2', '「若比丘，若'),
            ('pj3', '「若比丘，若'),
            ('pj4', '「若比丘，不'),
            ('pjz', '「諸大德！已'),
        ]),
        'sa-sarv': ('II. saṃghāvaśeṣā', False, [
            ('pj0', 'I. pārājikā dharmāḥ'),
            ('pj1', 'PrMoSū_Pār.1: yaḥ'),
            ('pj2', 'PrMoSū_Pār.2: yaḥ'),
            ('pj3', 'PrMoSū_Pār.3: yaḥ'),
            ('pj4', 'PrMoSū_Pār.4: yaḥ'),
            ('pjz', 'uddiṣṭā mayāyuṣmantaś'),
        ]),
        'T1436': ('「諸大德！是十', False, [
            ('pj0', '「諸大德！是四'),
            ('pj1', '「若比丘，共'),
            ('pj2', '「若比丘，若'),
            ('pj3', '「若比丘，若'),
            ('pj4', '「若比丘，空'),
            ('pjz', '「諸大德！已'),
        ]),
        'sa-mahl': ('[II. trayodaśa', False, [
            ('pj0', '[I. catvāraḥ pārājikā'),
            ('pj1', 'PrMoSū(Mā-L)Pār.1.'),
            ('pj2', 'PrMoSū(Mā-L)Pār.2.'),
            ('pj3', 'PrMoSū(Mā-L)Pār.3.'),
            ('pj4', 'PrMoSū(Mā-L)Pār.4.'),
            ('pjz', 'uddānaṃ (1) maithunam'),
        ]),
        'T1426': ('「諸大德！是十', False, [
            ('pj0', '「諸大德！是四'),
            ('pj1', '「若比丘，於'),
            ('pj2', '「若比丘，於'),
            ('pj3', '「若比丘，自'),
            ('pj4', '「若比丘，未'),
            ('pjz', '「諸大德！已'),
        ]),
        'T1460': ('「諸大德！此十', False, [
            ('pj0', '「諸大德！此'),
            ('pj1', '「若比丘，共'),
            ('pj2', '「若比丘，若'),
            ('pj3', '「若比丘，若'),
            ('pj4', '「若比丘，不'),
            ('pjz', '「諸大德！我'),
        ]),
        'sa-mula': ('saṃghāvaśeṣā dharmāḥ', False, [
            ('pj0', 'catvāraḥ pārājikā'),
            ('pj1', 'Pār.1 (PrMoSū_Mū-Banerjee)'),
            ('pj2', 'Pār.2 (PrMoSū_Mū-Banerjee)'),
            ('pj3', 'Pār.3 (PrMoSū_Mū-Banerjee)'),
            ('pj4', 'Pār.4 (PrMoSū_Mū-Banerjee)'),
            ('pjz', 'uddiṣṭā mayāyuṣmantaś'),
        ]),
        'T1454': ('「諸大德！此十', False, [
            ('pj0', '「諸大德！此'),
            ('pj1', '「若復苾芻，'),
            ('pj2', '「若復苾芻，'),
            ('pj3', '「若復苾芻，'),
            ('pj4', '「若復苾芻，'),
            ('pjz', '「諸大德我已'),
        ]),
    })


SETS['pratimoksa-c03'] = _pm(
    '比丘戒本（三）十三僧殘',
    '十三僧伽婆尸沙（僧殘、僧伽伐尸沙，saṅghādisesa／saṃghāvaśeṣa）：前九條初犯即成，後四條是三諫不捨才成（「九初犯、四乃至三諫」）。各部條目相同，只有末兩條次第分兩系：巴利、五分、僧祇、大眾說出世部梵本先「惡性拒僧」後「污家擯謗」；四分、十誦、解脫戒經、根有戒經與說一切有部、根本說一切有部梵本先污家、後惡性（段序依原本）。結說一節收「已說十三僧殘…覆藏隨日數行波利婆沙、六夜摩那埵、二十僧中出罪」與三問清淨。大眾說出世部梵本第十三條的條號在原檔漏標（只作「SA.」），攝頌（uddāna）歸結說；根有戒經篇首攝頌歸總標。',
    [
        ('ss0', '總標：十三僧殘法半月半月說'),
        ('ss1', '僧殘一・故出精'),
        ('ss2', '僧殘二・觸女人'),
        ('ss3', '僧殘三・向女人麁惡語'),
        ('ss4', '僧殘四・向女人歎身索供養'),
        ('ss5', '僧殘五・媒嫁'),
        ('ss6', '僧殘六・無主自乞作小房（不將比丘指授、過量）'),
        ('ss7', '僧殘七・有主作大房'),
        ('ss8', '僧殘八・以無根波羅夷謗'),
        ('ss9', '僧殘九・異分事中取片謗'),
        ('ss10', '僧殘十・破和合僧，三諫不捨'),
        ('ss11', '僧殘十一・助破僧伴黨，三諫不捨'),
        ('ss12', '僧殘十二・惡性不受諫，三諫不捨'),
        ('ss13', '僧殘十三・污家行惡行、謗僧有愛恚，三諫不捨'),
        ('ssz', '結說（九初犯、四三諫，覆藏行波利婆沙、摩那埵、出罪）・三問清淨'),
    ],
    {
        'pi': ('Aniyatuddeso\nIme', False, [
            ('ss0', 'Saṅghādisesuddeso'),
            ('ss1', 'Saṅghādisesa 1.'),
            ('ss2', 'Saṅghādisesa 2.'),
            ('ss3', 'Saṅghādisesa 3.'),
            ('ss4', 'Saṅghādisesa 4.'),
            ('ss5', 'Saṅghādisesa 5.'),
            ('ss6', 'Saṅghādisesa 6.'),
            ('ss7', 'Saṅghādisesa 7.'),
            ('ss8', 'Saṅghādisesa 8.'),
            ('ss9', 'Saṅghādisesa 9.'),
            ('ss10', 'Saṅghādisesa 10.'),
            ('ss11', 'Saṅghādisesa 11.'),
            ('ss12', 'Saṅghādisesa 12.'),
            ('ss13', 'Saṅghādisesa 13.'),
            ('ssz', 'Uddiṭṭhā kho āyasmanto'),
        ]),
        'T1429': ('「諸大德！是二', True, [
            ('ss0', '「諸大德！是十'),
            ('ss1', '「若比丘！故'),
            ('ss2', '「若比丘！婬'),
            ('ss3', '「若比丘！婬'),
            ('ss4', '「若比丘！婬'),
            ('ss5', '「若比丘！往'),
            ('ss6', '「若比丘！自'),
            ('ss7', '「若比丘！欲'),
            ('ss8', '「若比丘！瞋'),
            ('ss9', '「若比丘！以'),
            ('ss10', '「若比丘！欲'),
            ('ss11', '「若比丘！有'),
            ('ss13', '「若比丘！依'),
            ('ss12', '「若比丘！惡'),
            ('ssz', '「諸大德！我'),
        ]),
        'T1422a': ('「諸大德！是二', False, [
            ('ss0', '「諸大德！是十'),
            ('ss1', '「若比丘，故'),
            ('ss2', '「若比丘，欲'),
            ('ss3', '「若比丘，欲'),
            ('ss4', '「若比丘，欲'),
            ('ss5', '「若比丘行媒'),
            ('ss6', '「若比丘，自'),
            ('ss7', '「若比丘，有'),
            ('ss8', '「若比丘，自'),
            ('ss9', '「若比丘，自'),
            ('ss10', '「若比丘，為'),
            ('ss11', '「若比丘，助'),
            ('ss12', '「若比丘，惡'),
            ('ss13', '「若比丘，依'),
            ('ssz', '「諸大德！已'),
        ]),
        'sa-sarv': ('III. aniyatau dharmau', True, [
            ('ss0', 'II. saṃghāvaśeṣā'),
            ('ss1', 'PrMoSū_SA.1: saṃcintya'),
            ('ss2', 'PrMoSū_SA.2: yaḥ'),
            ('ss3', 'PrMoSū_SA.3: yaḥ'),
            ('ss4', 'PrMoSū_SA.4: yaḥ'),
            ('ss5', 'PrMoSū_SA.5: yaḥ'),
            ('ss6', 'PrMoSū_SA.6: svayācitāṃ'),
            ('ss7', 'PrMoSū_SA.7: m(a)hallakaṃ'),
            ('ss8', 'PrMoSū_SA.8: yaḥ'),
            ('ss9', 'PrMoSū_SA.9: yaḥ'),
            ('ss10', 'PrMoSū_SA.10: yaḥ'),
            ('ss11', 'PrMoSū_SA.11: tasya'),
            ('ss13', 'PrMoSū_SA.12: bhikṣuḥ'),
            ('ss12', 'PrMoSū_SA.13: bhikṣuḥ'),
            ('ssz', 'uddiṣṭā mayāyuṣmantas'),
        ]),
        'T1436': ('「諸大德！是二', True, [
            ('ss0', '「諸大德！是十'),
            ('ss1', '「若比丘，故'),
            ('ss2', '「若比丘，婬'),
            ('ss3', '「若比丘，婬'),
            ('ss4', '「若比丘，婬'),
            ('ss5', '「若比丘，行'),
            ('ss6', '「若比丘，無'),
            ('ss7', '「若比丘，有'),
            ('ss8', '「若比丘，瞋'),
            ('ss9', '「若比丘，瞋'),
            ('ss10', '「若比丘，為'),
            ('ss11', '「是為破和合'),
            ('ss13', '「若比丘，依'),
            ('ss12', '「有一比丘惡'),
            ('ssz', '「諸大德！已'),
        ]),
        'sa-mahl': ('[III. duve aniyatā', False, [
            ('ss0', '[II. trayodaśa'),
            ('ss1', 'PrMoSū(Mā-L)SA.1.'),
            ('ss2', 'PrMoSū(Mā-L)SA.2.'),
            ('ss3', 'PrMoSū(Mā-L)SA.3.'),
            ('ss4', 'PrMoSū(Mā-L)SA.4.'),
            ('ss5', 'PrMoSū(Mā-L)SA.5.'),
            ('ss6', 'PrMoSū(Mā-L)SA.6.'),
            ('ss7', 'PrMoSū(Mā-L)SA.7.'),
            ('ss8', 'PrMoSū(Mā-L)SA.8.'),
            ('ss9', 'PrMoSū(Mā-L)SA.9.'),
            ('ss10', 'PrMoSū(Mā-L)SA.10.'),
            ('ss11', 'PrMoSū(Mā-L)SA.11.'),
            ('ss12', 'PrMoSū(Mā-L)SA.12.'),
            ('ss13', 'PrMoSū(Mā-L)SA.'),
            ('ssz', '// uddānaṃ //\n(1)'),
        ]),
        'T1426': ('「諸大德！是二', False, [
            ('ss0', '「諸大德！是十'),
            ('ss1', '「若比丘故出'),
            ('ss2', '「若比丘，婬'),
            ('ss3', '「若比丘，婬'),
            ('ss4', '「若比丘，婬'),
            ('ss5', '「若比丘，受'),
            ('ss6', '「若比丘，自'),
            ('ss7', '「若比丘，作'),
            ('ss8', '「若比丘，瞋'),
            ('ss9', '「若比丘，瞋'),
            ('ss10', '「若比丘，為'),
            ('ss11', '「若比丘，同'),
            ('ss12', '「若比丘，自'),
            ('ss13', '「若比丘，依'),
            ('ssz', '「諸大德！以'),
        ]),
        'T1460': ('「諸大德！此二', True, [
            ('ss0', '「諸大德！此十'),
            ('ss1', '「若比丘，憶'),
            ('ss2', '「若比丘，染'),
            ('ss3', '「若比丘，染'),
            ('ss4', '「若比丘，於'),
            ('ss5', '「若比丘，行'),
            ('ss6', '「若比丘，自'),
            ('ss7', '「若比丘欲作'),
            ('ss8', '「若比丘，瞋'),
            ('ss9', '「若比丘，瞋'),
            ('ss10', '「若比丘，欲'),
            ('ss11', '「若比丘，有'),
            ('ss13', '「若諸比丘，'),
            ('ss12', '「若比丘，惡'),
            ('ssz', '「諸大德！我'),
        ]),
        'sa-mula': ('III. dvāv aniyatau', True, [
            ('ss0', 'saṃghāvaśeṣā dharmāḥ'),
            ('ss1', 'SA.1 (PrMoSū_Mū-Banerjee)'),
            ('ss2', 'SA.2 (PrMoSū_Mū-Banerjee)'),
            ('ss3', 'SA.3 (PrMoSū_Mū-Banerjee)'),
            ('ss4', 'SA.4 (PrMoSū_Mū-Banerjee)'),
            ('ss5', 'SA.5 (PrMoSū_Mū-Banerjee)'),
            ('ss6', 'SA.6 (PrMoSū_Mū-Banerjee)'),
            ('ss7', 'SA.7 (PrMoSū_Mū-Banerjee)'),
            ('ss8', 'SA.8 (PrMoSū_Mū-Banerjee)'),
            ('ss9', 'SA.9 (PrMoSū_Mū-Banerjee)'),
            ('ss10', 'SA.10 (PrMoSū_Mū-Banerjee)'),
            ('ss11', 'SA.11 (PrMoSū_Mū-Banerjee)'),
            ('ss13', 'SA.12 (PrMoSū_Mū-Banerjee)'),
            ('ss12', 'SA.13 (PrMoSū_Mū-Banerjee)'),
            ('ssz', 'uddiṣṭā mayāyuṣmantas'),
        ]),
        'T1454': ('「諸大德！此二', True, [
            ('ss0', '「諸大德！此十'),
            ('ss1', '「若復苾芻，'),
            ('ss2', '「若復苾芻，'),
            ('ss3', '「若復苾芻，'),
            ('ss4', '「若復苾芻，'),
            ('ss5', '「若復苾芻，'),
            ('ss6', '「若復苾芻，'),
            ('ss7', '「若復苾芻，'),
            ('ss8', '「若復苾芻，'),
            ('ss9', '「若復苾芻，'),
            ('ss10', '「若復苾芻，'),
            ('ss11', '「若復苾芻，'),
            ('ss13', '「若復眾多苾'),
            ('ss12', '「若復苾芻，'),
            ('ssz', '「諸大德！我'),
        ]),
    })
