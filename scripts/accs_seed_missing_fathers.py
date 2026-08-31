#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""補上 ACCS 語料裡有、翻譯詞庫卻沒收的 5 位教父，並合併詞庫自身的重複人物。

這 5 位是逐一查證過「詞庫真的沒收」才新增的——盤點 21 個高頻署名時，其餘 16 位
都已在詞庫、只是譯名不同，直接新增會一次造出 16 組重複人物（厄弗冷那個坑）。
身分認定靠 `accs_commentary.father_name_en`，不是靠字形猜：
`小亞那比烏` 的英文名欄寫著 Arnobius the Younger，「小」＝ the Younger。

🚨 **老小兩位亞那比烏是不同的人**：詞庫既有的「阿爾諾比烏斯」是 Arnobius of Sicca
   （西加的老亞那比烏，護教士，四世紀初），本檔新增的是 Arnobius the Younger
   （五世紀，寫詩篇註釋）。名字近似但差了一百多年，絕不可合併。

name_recommended 一律沿用 ACCS 語料既有的譯法：那是這批語料通行的寫法，
改掉會讓上百列跟著變動卻毫無好處，也違反「已核可的古譯不再改」的原則。

合併重複人物：兩組都是「一筆有生卒與變體、一筆整列空白」，保留有資料那筆、
刪掉空白那筆，英文異拼寫進 notes。詞庫沒有任何外鍵指向 theologians.id
（全 repo 查無 theologian_id），所以刪除是安全的。

預設 dry-run，要 --apply 才寫入。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

TABLE = 'theologians'

NEW_FATHERS = [
    {
        'name_recommended': '普魯頓丟',
        'name_english': 'Prudentius',
        'name_original': 'Aurelius Prudentius Clemens',
        'name_original_lang': 'lat',
        'name_latin_std': 'Aurelius Prudentius Clemens',
        'nationality': '西班牙（羅馬帝國塔拉哥行省）',
        'born_year': 348, 'died_year': 413, 'century': '4c',
        'person_era': 'early',
        'school': '拉丁西方',
        'role': '基督教拉丁詩人',
        'recommendation_reason': 'ACCS 校園繁中版既有譯法，本語料 59 列通行此寫法。',
        'notes': '代表作《時日詩集》(Cathemerinon)、《聖化詩頌》。',
    },
    {
        'name_recommended': '狄奧菲拉克圖斯',
        'name_english': 'Theophylact of Ohrid',
        'name_original': 'Θεοφύλακτος Ἀχρίδος',
        'name_original_lang': 'grc',
        'nationality': '拜占庭（歐赫里德）',
        'born_year': 1055, 'died_year': 1107, 'century': '11c',
        'person_era': 'medieval',
        'school': '拜占庭希臘',
        'role': '總主教；註釋家',
        'recommendation_reason': 'ACCS 校園繁中版既有譯法，本語料 46 列通行此寫法。',
        'notes': '大公書信與福音書註釋，ACCS 大量引用。',
    },
    {
        'name_recommended': '阿拉託',
        'name_english': 'Arator',
        'name_original': 'Arator',
        'name_original_lang': 'lat',
        'name_latin_std': 'Arator',
        'nationality': '利古里亞（義大利）',
        'born_year': 490, 'died_year': 550, 'century': '6c',
        'person_era': 'early',
        'school': '拉丁西方',
        'role': '副祭；基督教拉丁詩人',
        'recommendation_reason': 'ACCS 校園繁中版既有譯法，本語料 43 列通行此寫法。',
        'notes': '《論使徒行傳》(De Actibus Apostolorum)，ACCS 使徒行傳卷的主要引用來源之一。',
    },
    {
        'name_recommended': '耶路撒冷的赫西糾',
        'name_english': 'Hesychius of Jerusalem',
        'name_original': 'Ἡσύχιος Ἱεροσολυμίτης',
        'name_original_lang': 'grc',
        'nationality': '巴勒斯坦（耶路撒冷）',
        'born_year': None, 'died_year': 451, 'century': '5c',
        'person_era': 'early',
        'school': '希臘東方；耶路撒冷',
        'role': '司鐸；註釋家',
        'recommendation_reason': 'ACCS 校園繁中版既有譯法，本語料 40 列通行此寫法。',
        'notes': '《約伯記講道集》《詩篇註釋斷片》。',
    },
    {
        'name_recommended': '小亞那比烏',
        'name_english': 'Arnobius the Younger',
        'name_original': 'Arnobius Iunior',
        'name_original_lang': 'lat',
        'name_latin_std': 'Arnobius Iunior',
        'nationality': '北非／羅馬',
        'born_year': None, 'died_year': 455, 'century': '5c',
        'person_era': 'early',
        'school': '拉丁西方',
        'role': '隱修士；註釋家',
        'recommendation_reason': 'ACCS 校園繁中版既有譯法（「小」即 the Younger），本語料 24 列。',
        'notes': '🚨 與詞庫既有的「阿爾諾比烏斯」(Arnobius of Sicca，西加的老亞那比烏，'
                 '四世紀初護教士) 是**不同的兩個人**，相差逾一世紀，不可合併。'
                 '著《詩篇註釋》(Commentarii in Psalmos)。',
    },
]

# (要保留的 id, 要刪除的 id, 刪除那筆的英文異拼)
MERGES = [
    ('79c491e0-d19e-4adc-8989-ae7f0b5f2847',
     'edc00508-a25a-403f-8af0-dd992331e2bf', 'Pelagius (British monk)'),
    ('04583594-c3e9-4088-a2f8-02d80da2723b',
     '2e07fd5f-0bd6-4b20-8069-ceb2fbdeee0a', 'Theodoret of Cyrrhus'),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    r = requests.get(f'{te.URL}/rest/v1/{TABLE}?select=id,name_recommended,name_english,notes',
                     headers=te.H_GET, timeout=60)
    r.raise_for_status()
    existing = {(x.get('name_english') or '').strip(): x for x in r.json()}
    by_id = {x['id']: x for x in r.json()}

    print('=== 要新增的教父 ===')
    todo = []
    for f in NEW_FATHERS:
        if f['name_english'] in existing:
            print(f'   = {f["name_recommended"]} 已存在，跳過')
            continue
        todo.append(f)
        print(f'   + {f["name_recommended"]}  [{f["name_english"]}]  {f["century"]}  {f["role"]}')

    print('\n=== 要合併的重複人物 ===')
    merges = []
    for keep_id, drop_id, alt_en in MERGES:
        keep = by_id.get(keep_id)
        drop = by_id.get(drop_id)
        if not keep or not drop:
            print(f'   ! {keep_id[:8]}/{drop_id[:8]} 有一邊已不存在，跳過')
            continue
        if keep['name_recommended'] != drop['name_recommended']:
            print(f'   ! 推薦名不一致（{keep["name_recommended"]} vs '
                  f'{drop["name_recommended"]}），拒絕合併')
            continue
        merges.append((keep, drop, alt_en))
        print(f'   保留 {keep["name_recommended"]} [{keep.get("name_english")}]')
        print(f'   刪除 {drop["name_recommended"]} [{drop.get("name_english")}]  '
              f'→ 異拼寫進 notes')

    if not args.apply:
        print('\n(dry-run；要寫入請加 --apply)')
        return 0

    for f in todo:
        r = requests.post(f'{te.URL}/rest/v1/{TABLE}',
                          headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                          json=f, timeout=60)
        r.raise_for_status()
    print(f'\n已新增 {len(todo)} 位')

    for keep, drop, alt_en in merges:
        note = (keep.get('notes') or '').strip()
        add = f'英文亦作 {alt_en}。'
        if add not in note:
            note = (note + ' ' + add).strip()
            r = requests.patch(f'{te.URL}/rest/v1/{TABLE}?id=eq.{keep["id"]}',
                               headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                               json={'notes': note}, timeout=60)
            r.raise_for_status()
        r = requests.delete(f'{te.URL}/rest/v1/{TABLE}?id=eq.{drop["id"]}',
                            headers={**te.H_JSON, 'Prefer': 'return=minimal'}, timeout=60)
        r.raise_for_status()
    print(f'已合併 {len(merges)} 組重複人物')

    r = requests.get(f'{te.URL}/rest/v1/{TABLE}?select=id', headers={**te.H_GET,
                     'Prefer': 'count=exact', 'Range': '0-0'}, timeout=60)
    print(f'複查：詞庫現有 {r.headers.get("content-range", "?").split("/")[-1]} 位')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
