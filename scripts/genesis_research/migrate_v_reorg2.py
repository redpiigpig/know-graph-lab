# -*- coding: utf-8 -*-
"""migrate_v_reorg2.py — 2026-07-03 重排第二波（使用者追加定案）：
意欲純化＋四象限回 V1《各種生死觀》、愛＋主體回 V2《美學觀》（原第一波曾移入 V3）。
dimension 不變只換 book_id；撞 (project_slug,book_id,ref_key) 唯一鍵＝同文獻已在目標卷→刪除搬移方（照第一波前例）。

用法：dry-run 預設；--apply 寫 DB。ledger c:/tmp/genesis_research/migrate_v_reorg2.jsonl。
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
LEDGER = Path('c:/tmp/genesis_research/migrate_v_reorg2.jsonl')
LEDGER.parent.mkdir(parents=True, exist_ok=True)

RULES = [
    ('V3', ['慾望與願然的現象學差異', '「少欲知足」可說、「少願知足」不可說',
            '幸福清空效應：慾望壓力場崩潰後的輕盈', '激情上癮與願然空轉',
            '意欲的成熟：讓願然穿過慾望整合情境而清晰'], 'V1'),
    ('V3', ['意欲的兩軸：從論述到象限的推導', '熵的宇宙方向性：秩序意欲與激情意欲的物理根基',
            '健康的願然：兩極之間的動態調控', '兩種失衡：過度秩序的僵化與過度激情的耗散'], 'V1'),
    ('V3', ['愛是「你值得我交託自身」的意欲', "L 與 L'：實然之愛與應然之愛的二維張力",
            '信、望、愛作為願然的三種時間性朝向', '愛作為願然的最高位置'], 'V2'),
    ('V3', ['抽象理念的僭越與主體的失落', '主體完滿（hi 趨近 1）作為價值論的終極向度',
            '超越完滿——菩薩執誓不入涅槃與更高價值可能性的辨析', '主體的神性完滿與文明的方向'], 'V2'),
]


def fetch(v):
    r = requests.get(f'{URL}/rest/v1/lit_review_entries', headers={**H, 'Range': '0-9999'},
                     params={'select': 'id,ref_key,dimension', 'project_slug': 'eq.genesis-philosophy',
                             'book_id': f'eq.{v}', 'order': 'display_order'}, timeout=120)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    dim2new = {}
    for _, secs, new_v in RULES:
        for s in secs:
            dim2new[s] = new_v

    v3 = fetch('V3')
    moves = [(e, dim2new[e['dimension']]) for e in v3 if e['dimension'] in dim2new]
    from collections import Counter
    print('V3 total:', len(v3), ' moves:', len(moves), Counter(nv for _, nv in moves))

    if not args.apply:
        print('(dry-run)')
        return

    done = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding='utf-8').splitlines():
            if line.strip():
                done.add(json.loads(line)['id'])

    hh = dict(H)
    hh['Content-Type'] = 'application/json'
    hh['Prefer'] = 'return=minimal'
    ok = dup = fail = skip = 0
    with LEDGER.open('a', encoding='utf-8') as lg:
        for e, new_v in moves:
            if e['id'] in done:
                skip += 1
                continue
            r = requests.patch(f'{URL}/rest/v1/lit_review_entries?id=eq.{e["id"]}', headers=hh,
                               data=json.dumps({'book_id': new_v}).encode(), timeout=60)
            if r.status_code in (200, 204):
                ok += 1
                lg.write(json.dumps({'id': e['id'], 'old_book': 'V3', 'new_book': new_v,
                                     'dim': e['dimension']}, ensure_ascii=False) + '\n')
            elif r.status_code == 409 and '23505' in r.text:
                rd = requests.delete(f'{URL}/rest/v1/lit_review_entries?id=eq.{e["id"]}', headers=hh, timeout=60)
                dup += 1
                lg.write(json.dumps({'id': e['id'], 'old_book': 'V3', 'new_book': None,
                                     'dim': e['dimension'],
                                     'action': f'deleted-dup(目標{new_v}已有同ref_key, del={rd.status_code})',
                                     'ref_key': e['ref_key']}, ensure_ascii=False) + '\n')
                print(f'  DUP→刪 id={e["id"]} {e["ref_key"]}')
            else:
                fail += 1
                print(f'  FAIL id={e["id"]} {r.status_code} {r.text[:150]}')
    print(f'apply：ok={ok} dup刪={dup} fail={fail} skip={skip}')


if __name__ == '__main__':
    main()
