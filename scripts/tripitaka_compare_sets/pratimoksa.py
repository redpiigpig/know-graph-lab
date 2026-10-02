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
