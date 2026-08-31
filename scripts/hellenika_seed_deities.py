#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 把《俄耳甫斯讚歌》的 62 條神名寫進 /translation-glossary 的 deities 表。

一次性的入庫腳本（user 2026-08-30 授權定名：「62 條神名，你自己翻譯」）。
在此之前，這批依 feedback_glossary_ancient_name_priority 只列在
data/hellenika/glossary-candidates-orphic.md 標【提】，不自行入庫。

## 定名原則（逐條的理由寫在 recommendation_reason 欄）

1. **按希臘原文讀音，不按英文拼寫。** Taylor 1792 把神名全換成拉丁對應
   （Bacchus、Ceres、Proserpine…），本表一律回到希臘原名。
2. **名根一致（name_root）。** 同一個希臘詞頭在中文必須是同一個字：
   Ὑγεία 許革亞／Ὕπνος 許普諾斯（Ὑ→許）、Πρωτεύς 普羅透斯／Πρωτόγονος
   普羅托格諾斯／Προθυραία 普羅提萊亞（Πρω-, Προ-→普羅）。
3. **抽象神格音譯為主、意譯附註。** Δίκη、Νόμος、Τύχη 這類既是抽象名詞又是
   受祭的神，純意譯會失去神格，故正文用音譯、篇名並列意譯。
4. **稱號意義明確者，篇名並列意譯**（Λικνίτης 簸箕中的、Περικιόνιος 繞柱者、
   Τριετηρικός 三年一祭的），但主譯仍取音譯，因為它們在文中是被呼求的專名。

🚨 表裡**已有**的六條（宙斯、赫拉、波塞頓、雅典娜、阿波羅、阿瑞斯）不動；
本藏經另有定名的四條（赫爾墨斯／阿爾忒彌斯／得墨忒耳／阿芙羅狄忒）走
hellenika_glossary.py 的 CORPUS_OVERRIDES，也不在此表。

用法：
    python scripts/hellenika_seed_deities.py --check    # 只比對，不寫
    python scripts/hellenika_seed_deities.py --apply
"""
from __future__ import annotations

import argparse
import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hellenika_glossary import _load_env  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

# (希臘原文, 羅馬轉寫, 英文, ★中譯, 異名, 定名理由, name_root)
ROWS: list[tuple[str, str, str, str, str | None, str, str | None]] = [
    # ── 俄耳甫斯派特有的神格 ──
    ('Πρωτόγονος', 'Protogonos', 'Protogonus', '普羅托格諾斯', '初生者',
     '義為「初生者」，俄耳甫斯神譜的第一神；音譯為主，篇名並列意譯。'
     'Πρω-／Προ- 一律作「普羅」，與普羅透斯、普羅提萊亞同根', '普羅'),
    ('Φάνης', 'Phanes', 'Phanes', '法涅斯', '普羅托格諾斯；厄里卡派俄斯',
     '破宇宙卵而出的光輝初神，與普羅托格諾斯、厄里卡派俄斯為同一神的三個名', None),
    ('Ἠρικεπαῖος', 'Erikepaios', 'Ericapaeus', '厄里卡派俄斯', '法涅斯',
     '法涅斯的別名；語源不明（一說腓尼基語借詞），故純音譯不意譯', None),
    ('Μίση', 'Mise', 'Mise', '彌塞', 'Misa',
     '雌雄同體的酒神—得墨忒耳系神格，小亞細亞祕儀所奉；中文無既成譯法，音譯', None),
    ('Ἵπτα', 'Hipta', 'Hipta', '希帕', 'Ippa',
     '呂底亞來源的育嬰母神，神話中承接初生的酒神；音譯', None),
    ('Μηλινόη', 'Melinoe', 'Melinoe', '梅利諾厄', None,
     '珀耳塞福涅所生的冥界幽靈女神，只見於本讚歌；音譯', None),
    ('Ἀνταία', 'Antaia', 'Antaia', '安泰亞', None,
     '得墨忒耳／瑞亞的稱號，義近「可迎面祈求者」但學界有爭議，故不意譯', None),
    ('Λικνίτης', 'Liknites', 'Liknitos', '利克尼忒斯', '簸箕中的酒神',
     '酒神稱號，義為「臥於簸箕（λίκνον）中的」，指嬰兒酒神；音譯為主', None),
    ('Περικιόνιος', 'Perikionios', 'Perikionios', '佩里基俄尼俄斯', '繞柱者',
     '酒神稱號，義為「繞柱而生的」，指忒拜宮柱上的常春藤；音譯為主', None),
    ('Τριετηρικός', 'Trieterikos', 'Trieterikos', '特里厄忒里科斯', '三年祭之神',
     '酒神稱號，義為「三年一祭的」，指隔年舉行的酒神祕儀；音譯為主', None),
    ('Ἀμφιετής', 'Amphietes', 'Amphietos', '安菲厄忒斯', '周年祭之神',
     '酒神稱號，義為「周年的」，與三年祭相對；音譯為主', None),
    ('Βασσαρεύς', 'Bassareus', 'Bassareus', '巴薩留斯', None,
     '酒神稱號，出自色雷斯女信徒所披的狐皮衣 βασσάρα；音譯', None),
    ('Εὐβουλεύς', 'Eubouleus', 'Eubouleus', '歐布勒俄斯', None,
     '厄琉息斯與俄耳甫斯祕儀的神名，義為「善謀者」；音譯已通行於祕儀研究', None),
    ('Προθυραία', 'Prothyraia', 'Prothyraea', '普羅提萊亞', '門前女神',
     '生產女神稱號，義為「門前的」（產房門前），與埃雷圖伊亞同體；'
     'Προ- 作「普羅」與普羅透斯同根', '普羅'),
    # ── 抽象神格：音譯為主，篇名並列意譯 ──
    ('Φύσις', 'Physis', 'Physis', '費西斯', '自然',
     '既是哲學術語也是受祭神格；純作「自然」會失去神格，故音譯為主', None),
    ('Νόμος', 'Nomos', 'Nomos', '諾摩斯', '律法',
     '同上；本藏經他處作為術語時仍可譯「律法」，作神名時音譯', None),
    ('Δίκη', 'Dike', 'Dike', '狄刻', '正義',
     '正義女神。與狄開俄緒涅分立為兩首讚歌，中譯必須可分', None),
    ('Δικαιοσύνη', 'Dikaiosyne', 'Dikaiosyne', '狄開俄緒涅', '公道',
     '與狄刻同源而分立；意譯取「公道」以與「正義」區別', None),
    ('Τύχη', 'Tyche', 'Tyche', '提喀', '機運',
     '意譯取「機運」而非「命運」——「命運」已配給摩伊賴三女神，不可共用', None),
    ('Δαίμων', 'Daimon', 'Daimon', '代蒙', '守護靈',
     '「精靈」「鬼神」在漢語皆有誤導；音譯保留其道德中性，這正是該詞的關鍵', None),
    ('Ὑγεία', 'Hygeia', 'Hygeia', '許革亞', '健康',
     '健康女神，阿斯克勒庇俄斯之女。Ὑ- 作「許」，與許普諾斯同根', '許'),
    ('Μνημοσύνη', 'Mnemosyne', 'Mnemosyne', '謨涅摩緒涅', '記憶',
     '記憶女神，繆斯之母；古典學界通行音譯', None),
    # ── 自然神格與其餘 ──
    ('Ἑκάτη', 'Hekate', 'Hecate', '赫卡忒', None, '古典學界通行音譯', None),
    ('Νύξ', 'Nyx', 'Nyx', '倪克斯', '夜', '夜之女神；音譯為主，意譯附註', None),
    ('Οὐρανός', 'Ouranos', 'Ouranos', '烏拉諾斯', '天',
     '天神。本藏經自《神譜》起一貫作烏拉諾斯，不作「天王星」那類天文譯名', None),
    ('Αἰθήρ', 'Aither', 'Aither', '埃忒耳', '清氣',
     '上層清氣之神。作神名時音譯，不用物理學的「以太」', None),
    ('Ἥλιος', 'Helios', 'Helios', '赫利俄斯', '日', '日神；古典學界通行', None),
    ('Σελήνη', 'Selene', 'Selene', '塞勒涅', '月', '月神；古典學界通行', None),
    ('Πάν', 'Pan', 'Pan', '潘', None, '牧神；已通行', None),
    ('Ἡρακλῆς', 'Herakles', 'Herakles', '赫拉克勒斯', '海克力斯',
     '按希臘原文讀音；「海克力斯」出自英文 Hercules 的通俗音譯', None),
    ('Κρόνος', 'Kronos', 'Cronus', '克洛諾斯', '克羅諾斯',
     '與詞庫既有條目一致；不可與時間之神 Χρόνος 混同', None),
    ('Ῥέα', 'Rhea', 'Rhea', '瑞亞', None, '泰坦母神；已通行', None),
    ('Πλούτων', 'Plouton', 'Plouton', '普魯托', None,
     '冥王的祭儀名，義近「富有者」。與 Ἅιδης（哈得斯）是同一神的兩個名，'
     '但本讚歌兩名分用，中譯須可分', None),
    ('Θάλασσα', 'Thalassa', 'Thalassa', '塔拉薩', '海',
     '海之女神；音譯為主', None),
    ('Τηθύς', 'Tethys', 'Tethys', '忒堤斯', None,
     '泰坦海洋女神；不可與阿基里斯之母 Θέτις（忒提斯）混同', None),
    ('Νηρεύς', 'Nereus', 'Nereus', '涅柔斯', None, '海中老人；古典學界通行', None),
    ('Νηρηΐδες', 'Nereides', 'Nereids', '涅柔斯眾女', '涅瑞伊得斯',
     '涅柔斯的五十個女兒。作「眾女」而非「們」——「們」是現代白話複數', '涅柔斯'),
    ('Πρωτεύς', 'Proteus', 'Proteus', '普羅透斯', None,
     '善變的海神；Πρω- 作「普羅」，與普羅托格諾斯同根', '普羅'),
    ('Κουρῆτες', 'Kouretes', 'Kouretes', '庫瑞忒斯', '科律班忒斯',
     '克里特武舞祭司團，以擊盾聲掩護嬰兒宙斯；音譯', None),
    ('Κόρυβας', 'Korybas', 'Korybas', '科律巴斯', None,
     '庫柏勒的武舞祭司；與庫瑞忒斯常相混而本讚歌分立', None),
    ('Νίκη', 'Nike', 'Nike', '尼刻', '勝利', '勝利女神；音譯為主', None),
    ('Λητώ', 'Leto', 'Leto', '勒托', None, '阿波羅與阿爾忒彌斯之母；已通行', None),
    ('Τιτᾶνες', 'Titanes', 'Titans', '泰坦諸神', '提坦',
     '作「諸神」而非「們」；本藏經他處或作提坦，以泰坦為主譯', None),
    ('Σεμέλη', 'Semele', 'Semele', '塞墨勒', None, '酒神之母；古典學界通行', None),
    ('Σαβάζιος', 'Sabazios', 'Sabazios', '薩巴齊俄斯', 'Zabazios',
     '弗里吉亞—色雷斯的酒神，帝國期與宙斯、酒神合流；音譯', None),
    ('Ἄδωνις', 'Adonis', 'Adonis', '阿多尼斯', None, '已通行', None),
    ('Ἔρως', 'Eros', 'Eros', '厄洛斯', '愛若斯',
     '愛神。Taylor 作 Cupid（拉丁 Cupido），本表回到希臘原名', None),
    ('Νέμεσις', 'Nemesis', 'Nemesis', '涅墨西斯', None,
     '報應女神；古典學界通行', None),
    ('Ἀσκληπιός', 'Asklepios', 'Asklepios', '阿斯克勒庇俄斯', '埃斯庫拉庇烏斯',
     '醫神。異名出自拉丁 Aesculapius，本表按希臘原文', None),
    ('Ἐρινύες', 'Erinyes', 'Erinyes', '厄里倪厄斯', '復仇女神',
     '復仇三女神。音譯為主、意譯附註；與慈心女神（歐墨尼得斯）是同一批神的'
     '兩個稱呼，本讚歌分立兩首，中譯須可分', None),
    ('Λευκοθέα', 'Leukothea', 'Leucothea', '琉科忒亞', '伊諾',
     '化為海中女神的伊諾；音譯', None),
    ('Παλαίμων', 'Palaimon', 'Palaimon', '帕萊蒙', None,
     '琉科忒亞之子，海中少年神；音譯', None),
    ('Ἠώς', 'Eos', 'Eos', '厄俄斯', '曙光',
     '曙光女神。Taylor 作 Aurora（拉丁），本表按希臘原文', None),
    ('Θέμις', 'Themis', 'Themis', '忒彌斯', None,
     '法度女神；與狄刻分工，忒彌斯是神定之律、狄刻是人間之義', None),
    ('Βορέας', 'Boreas', 'Boreas', '玻瑞阿斯', '北風',
     '北風神；音譯為主', None),
    ('Ζέφυρος', 'Zephyros', 'Zephyros', '澤費羅斯', '西風',
     '西風神；音譯為主', None),
    ('Νότος', 'Notos', 'Notos', '諾托斯', '南風',
     '南風神；音譯為主', None),
    ('Ἑστία', 'Hestia', 'Hestia', '赫斯提亞', None,
     '爐灶女神。Taylor 作 Vesta（羅馬對應），本表按希臘原文', None),
    ('Ὕπνος', 'Hypnos', 'Hypnos', '許普諾斯', '睡眠',
     '睡神。Ὑ- 作「許」，與許革亞同根', '許'),
    ('Ὄνειρος', 'Oneiros', 'Oneiros', '俄涅伊洛斯', '夢',
     '夢神。Ὄ- 作「俄」，與俄刻阿諾斯同根', '俄'),
    ('Θάνατος', 'Thanatos', 'Thanatos', '塔納托斯', '死',
     '死神，本讚歌終篇；音譯為主', None),
    ('Σειληνός', 'Seilenos', 'Silenus', '西勒諾斯', None,
     '酒神的老養育者；已通行', None),
    ('Μουσαῖος', 'Mousaios', 'Musaeus', '穆賽俄斯', None,
     '傳說中俄耳甫斯的弟子，本讚歌序詩的受話者；音譯', None),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    _load_env()
    url = os.environ['SUPABASE_URL']
    key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    h = {'apikey': key, 'Authorization': f'Bearer {key}',
         'Content-Type': 'application/json'}

    have = {r['name_english'].strip().lower(): r
            for r in requests.get(
                f'{url}/rest/v1/deities?select=name_english,name_recommended&limit=2000',
                headers=h, timeout=90).json()}

    todo, clash = [], []
    for grc, rom, en, zh, var, why, root in ROWS:
        cur = have.get(en.strip().lower())
        if cur and cur['name_recommended'] != zh:
            clash.append((en, cur['name_recommended'], zh))
        elif cur:
            continue
        todo.append({
            'name_original': grc, 'name_original_lang': 'grc',
            'name_romanized': rom, 'name_english': en,
            'name_recommended': zh, 'name_variants': var,
            'recommendation_reason': why, 'name_root': root,
            'religion': '希臘', 'entity_type': 'deity',
        })

    print('本表 %d 條｜待新增 %d｜已存在且相符 %d'
          % (len(ROWS), len(todo), len(ROWS) - len(todo) - len(clash)))
    if clash:
        print('🚨 與詞庫既有值不符，**不覆寫**，請人工定奪：')
        for en, old, new in clash:
            print('   %-16s 詞庫「%s」 vs 本表「%s」' % (en, old, new))
    if not a.apply:
        for r in todo:
            print('  + %-16s %s' % (r['name_english'], r['name_recommended']))
        return

    for i in range(0, len(todo), 50):
        r = requests.post(f'{url}/rest/v1/deities', headers=h,
                          json=todo[i:i + 50], timeout=120)
        r.raise_for_status()
    print('已寫入 %d 條' % len(todo))


if __name__ == '__main__':
    main()
