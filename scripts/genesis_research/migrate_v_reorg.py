# -*- coding: utf-8 -*-
"""migrate_v_reorg.py — 2026-07-02 價值論三部曲重排的 ref-DB 遷移（確定性，不用 LLM）。

重排定案（見 genesis_dialogue_maps_handoff.md「零之二」）：
  V1《各種生死觀》 V2《美學觀》 V3《世界與生活》；五然四德總說移 B1 導論。

lit_review_entries 遷移規則（dimension 為 canonical 小節標籤，逐章整章搬）：
  舊V1 ch1(導論願然之學) → B1，dimension 統一掛「五然之分：實然、識然、應然、願然、默然」
  舊V1 ch2(願然與慾望)   → V3（dimension 不變，章成為新第五章）
  舊V1 ch3(四象限與熵)   → V3（新第六章）
  舊V1 ch4(共振生成論)   → V2（新第二章）
  舊V1 ch5(相對客觀性)   → V2（新第三章）
  舊V1 ch6(真善美聖)     → B1，dimension 統一掛「真善美聖的階序：無真不成善、無善不成美、無美不成聖」
  舊V2 ch1(意義困難)     → V1（新第二章）
  舊V2 ch2(虛無診斷)     → V1（新第六章）
  舊V2 ch3(愛)           → V3（新第七章）
  舊V2 ch4(空無美學)     → V2（不動）
  舊V2 ch5(主體最高價值) → V3（新第八章）
  舊V2 ch6(第二軸心)     → V3（新第九章，dimension 不變）
  舊V3 ch3(藝術文學)     → V2（新第四章）
  舊V3 ch1/2/4/5         → V3（不動）

用法：
  python -X utf8 scripts/genesis_research/migrate_v_reorg.py           # dry-run
  python -X utf8 scripts/genesis_research/migrate_v_reorg.py --apply
ledger：c:/tmp/genesis_research/migrate_v_reorg.jsonl（可還原）。
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import requests

ROOT = Path('c:/Users/user/Desktop/know-graph-lab')
sys.path.insert(0, str(ROOT / 'scripts'))
import classify_genesis_philosophy as C

URL = C.SUPABASE_URL
H = C.SB_HDR
LEDGER = Path('c:/tmp/genesis_research/migrate_v_reorg.jsonl')
LEDGER.parent.mkdir(parents=True, exist_ok=True)

B1_WURAN = '五然之分：實然、識然、應然、願然、默然'
B1_JIEXU = '真善美聖的階序：無真不成善、無善不成美、無美不成聖'

# (舊卷, 舊章 canonical 小節標籤們) → (新卷, dim 覆寫 or None=保留)
RULES = [
    ('V1', ['四然之分：確立願然的位置', '「意欲」作為核心術語：願然不是願意，也不是慾望',
            '現代哲學的雙重遺漏：願然如何被遮蔽', '價值論的問法：「對我而言值得什麼」',
            '本卷的展開路徑'], 'B1', B1_WURAN),
    ('V1', ['慾望與願然的現象學差異', '「少欲知足」可說、「少願知足」不可說',
            '幸福清空效應：慾望壓力場崩潰後的輕盈', '激情上癮與願然空轉',
            '意欲的成熟：讓願然穿過慾望整合情境而清晰'], 'V3', None),
    ('V1', ['意欲的兩軸：從論述到象限的推導', '熵的宇宙方向性：秩序意欲與激情意欲的物理根基',
            '健康的願然：兩極之間的動態調控', '兩種失衡：過度秩序的僵化與過度激情的耗散'], 'V3', None),
    ('V1', ['兩種失敗的美學：客觀論的危機與純粹主觀論的崩解',
            '美的共振生成論：客體潛能性、主體意向性與願然結構',
            '美的潛能與美的現實：隱匿之美的本體地位', '現象即本質：關係性優先的美學論'], 'V2', None),
    ('V1', ['審美相對客觀性：演化原型的形式沉澱', '美的文化主觀性：世代叛逆與歷史變奏',
            '願然共振：基頻與變奏的統一', '審美判斷的重量：鑑賞力作為願然的高階展現'], 'V2', None),
    ('V1', ['真是第一義：誠實作為價值生成的地基', '善立於真：應然向度的誠實根基',
            '美立於善：願然向度的倫理前提', '聖立於美，默然向開放：四向度的完整階序',
            '整體階序與卷二的預告'], 'B1', B1_JIEXU),
    ('V2', ['意義不是被發現的，而是在遭遇中生成的', '兒童的「無限為什麼」：意義場的未完成張力',
            '價值性回答 vs 知識性回答：兩種不可化約的語言',
            '解消「意義的困難問題」：從錯誤提問到正確框架'], 'V1', None),
    ('V2', ['願然斷裂：虛無的精確定義', '激情無能與愛無能：症狀的現象學',
            '後現代解構、他者臨在的消失與意欲的自戀化', '價值論的療癒任務：重新召喚他者臨在'], 'V1', None),
    ('V2', ['愛是「你值得我交託自身」的意欲', "L 與 L'：實然之愛與應然之愛的二維張力",
            '信、望、愛作為願然的三種時間性朝向', '愛作為願然的最高位置'], 'V3', None),
    # 舊V2 ch4 空無美學：book 不動（V2→V2），略
    ('V2', ['抽象理念的僭越與主體的失落', '主體完滿（hi 趨近 1）作為價值論的終極向度',
            '超越完滿——菩薩執誓不入涅槃與更高價值可能性的辨析', '主體的神性完滿與文明的方向'], 'V3', None),
    ('V2', ['後後現代的大敘事：容納而非解構', '沉思作為願然的素樸自我說明——以及 AI 時代的鑑賞力',
            '第二軸心時代的價值口號——共生互成、誠實共善',
            '在臨界處交棒——願然的邊界與存有論的開端'], 'V3', None),
    ('V3', ['模仿論的終結：藝術不再現世界，而是創造世界',
            '文學作為存在界的孵化器：從作者的意想界到讀者的共構', '虛構的重量：世界創造的倫理'], 'V2', None),
]


def fetch(v):
    r = requests.get(f'{URL}/rest/v1/lit_review_entries', headers={**H, 'Range': '0-9999'},
                     params={'select': 'id,ref_key,title,dimension,display_order',
                             'project_slug': 'eq.genesis-philosophy', 'book_id': f'eq.{v}',
                             'order': 'display_order'}, timeout=120)
    r.raise_for_status()
    return r.json()


def patch(eid, payload):
    h = dict(H)
    h['Content-Type'] = 'application/json'
    h['Prefer'] = 'return=minimal'
    r = requests.patch(f'{URL}/rest/v1/lit_review_entries?id=eq.{eid}', headers=h,
                       data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), timeout=60)
    return r.status_code in (200, 204), r.status_code, r.text[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    # 已處理過的 id（冪等續跑）
    done = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding='utf-8').splitlines():
            if line.strip():
                done.add(json.loads(line)['id'])

    dim2rule = {}
    for old_v, secs, new_v, new_dim in RULES:
        for s in secs:
            dim2rule[(old_v, s)] = (new_v, new_dim)

    entries = {v: fetch(v) for v in ['V1', 'V2', 'V3']}
    moves, keeps, unmatched = [], 0, []
    for v, es in entries.items():
        for e in es:
            key = (v, e['dimension'])
            if key in dim2rule:
                new_v, new_dim = dim2rule[key]
                if new_v == v and new_dim is None:
                    keeps += 1
                else:
                    moves.append((e, new_v, new_dim))
            else:
                # 不在規則裡＝該章原地不動（舊V2 ch4、舊V3 ch1/2/4/5）或 off-canonical
                keeps += 1
                unmatched.append((v, e['dimension']))

    from collections import Counter
    print(f'V1={len(entries["V1"])} V2={len(entries["V2"])} V3={len(entries["V3"])}  '
          f'moves={len(moves)} keeps={keeps}')
    cnt = Counter((e[1], e[2] or '(dim不變)') for e in moves)
    for k, n in sorted(cnt.items()):
        print(f'  → {k[0]}  {n:3d} 筆   dim={k[1][:40]}')
    ucnt = Counter(unmatched)
    print('原地不動 dimension 分布（前 12）:')
    for k, n in ucnt.most_common(12):
        print(f'  {k[0]} {n:3d}  {k[1][:44]}')

    if not args.apply:
        print('\n(dry-run；--apply 才寫 DB)')
        return

    ok = fail = skip = 0
    with LEDGER.open('a', encoding='utf-8') as lg:
        for e, new_v, new_dim in moves:
            if e['id'] in done:
                skip += 1
                continue
            payload = {'book_id': new_v}
            if new_dim:
                payload['dimension'] = new_dim
            good, sc, txt = patch(e['id'], payload)
            if good:
                ok += 1
                lg.write(json.dumps({'id': e['id'], 'old_book': [k for k, es in entries.items() if e in es][0],
                                     'old_dim': e['dimension'], 'new_book': new_v,
                                     'new_dim': new_dim or e['dimension']}, ensure_ascii=False) + '\n')
            else:
                fail += 1
                print(f'  FAIL id={e["id"]} {sc} {txt}')
    print(f'apply 完成：ok={ok} fail={fail} skip(已做)={skip}')


if __name__ == '__main__':
    main()
