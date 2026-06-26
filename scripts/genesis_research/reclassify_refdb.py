# -*- coding: utf-8 -*-
"""
reclassify_refdb.py  —  交接第三節 (C)
把 M3/O*/V*/B* 既有 ref-DB 條目（display_order<200，章級 dimension）
逐筆細化到 canonical h3 小節（clean_inv.json）。

做法：每卷把「全卷 canonical 小節清單（編號＋所屬章）」+ 該卷既有條目
（title / 目前章 dimension / abstract_zh）丟給 Gemini→NVIDIA→Haiku，
回傳每筆最貼切的小節編號 → REST PATCH dimension = 該小節字串。

- 不佔 Claude session 額度（走 Python LLM 引擎鏈）。
- ledger 記 c:/tmp/genesis_research/reclassify_refdb.jsonl，可續跑、冪等。
- 這些卷主題單一，不做跨卷搬移（dimension 已隱含該 book 的章）。

用法：
  python -X utf8 reclassify_refdb.py            # 全 10 卷
  python -X utf8 reclassify_refdb.py --vol M3 O1
  python -X utf8 reclassify_refdb.py --dry-run  # 不寫 DB
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import requests

ROOT = Path('c:/Users/user/Desktop/know-graph-lab')
sys.path.insert(0, str(ROOT / 'scripts'))
import classify_genesis_philosophy as C  # 共用 env + Gemini/NVIDIA/Haiku 引擎

URL = C.SUPABASE_URL
H = C.SB_HDR
INV = json.load(open('c:/tmp/genesis_research/clean_inv.json', encoding='utf-8'))
VOLS = ['M3', 'O1', 'O2', 'O3', 'V1', 'V2', 'V3', 'B1', 'B2', 'B3']
LEDGER = Path('c:/tmp/genesis_research/reclassify_refdb.jsonl')

SYSTEM = (
    "你是『創生哲學』的學術文獻分類助理。每卷有一份 canonical 小節清單（每個小節標註所屬章）。"
    "給你若干筆文獻（標題／目前所屬章／繁中摘要），請為每一筆挑出『唯一最貼切』的小節編號。"
    "判準：先用『目前所屬章』縮小到該章的小節，再依標題與摘要的主題挑該章內最相符的小節；"
    "若摘要明顯更貼近另一章的小節，可跨章選。務必只回清單內既有編號，不得自創。"
)


def vol_sections(v):
    """回傳 [(chap_title, section_str), ...]，順序即編號。"""
    out = []
    for ch in INV[v]:
        for s in ch.get('sections', []):
            out.append((ch['title'], s))
    return out


def fetch_orig(v):
    r = requests.get(f'{URL}/rest/v1/lit_review_entries', headers={**H, 'Range': '0-9999'},
                     params={'select': 'id,ref_key,title,abstract_zh,dimension,display_order',
                             'project_slug': 'eq.genesis-philosophy', 'book_id': f'eq.{v}',
                             'order': 'display_order'}, timeout=120)
    r.raise_for_status()
    return [e for e in r.json() if (e.get('display_order') or 0) < 200]


def patch(eid, dim):
    h = dict(H)
    h['Content-Type'] = 'application/json'
    h['Prefer'] = 'return=minimal'
    r = requests.patch(f'{URL}/rest/v1/lit_review_entries?id=eq.{eid}', headers=h,
                       data=json.dumps({'dimension': dim}, ensure_ascii=False).encode('utf-8'),
                       timeout=60)
    return r.status_code in (200, 204)


def classify_batch(secs, batch):
    seclist = '\n'.join(f'{i}. [{chap}] {sec}' for i, (chap, sec) in enumerate(secs))
    items = '\n\n'.join(
        f'[{j}] 標題：{(e.get("title") or "")[:180]}\n'
        f'    目前所屬章：{e.get("dimension")}\n'
        f'    摘要：{(e.get("abstract_zh") or "")[:320]}'
        for j, e in enumerate(batch))
    prompt = (f"可選小節（編號. [所屬章] 小節）：\n{seclist}\n\n"
              f"文獻：\n{items}\n\n"
              f"為每則挑唯一最貼切的小節編號。嚴格只輸出 JSON 陣列，"
              f'元素格式 {{"i": <文獻編號>, "sec": <小節編號>}}，不要任何說明文字。')
    for name, fn in (('Gemini', C.gemini_chat), ('NVIDIA', C.nvidia_chat), ('Haiku', C.haiku_chat)):
        try:
            return C._parse_json(fn(SYSTEM, prompt))
        except Exception as e:
            print(f'  · {name} 失敗：{type(e).__name__} {str(e)[:110]}', flush=True)
    return None


def process_vol(v, batch_size, dry, done):
    secs = vol_sections(v)
    rows = [e for e in fetch_orig(v) if e['id'] not in done]
    print(f'\n=== {v} === orig 待處理 {len(rows)}／小節 {len(secs)} 個', flush=True)
    lf = None if dry else LEDGER.open('a', encoding='utf-8')
    n_ok = 0
    try:
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            verdicts = classify_batch(secs, batch)
            if verdicts is None:
                print(f'  batch {i // batch_size} 三引擎全失敗，跳過', flush=True)
                continue
            vmap = {x.get('i'): x.get('sec') for x in verdicts if isinstance(x, dict)}
            for j, e in enumerate(batch):
                si = vmap.get(j)
                if not isinstance(si, int) or not (0 <= si < len(secs)):
                    print(f'  ⚠ {e["ref_key"][:40]} 無效 sec={si}，保留原 dim', flush=True)
                    continue
                new_dim = secs[si][1]
                if new_dim == e.get('dimension'):
                    ok = True
                else:
                    ok = True if dry else patch(e['id'], new_dim)
                if ok:
                    n_ok += 1
                    if dry and new_dim != e.get('dimension'):
                        print(f'    {e.get("dimension")}  →  {new_dim}', flush=True)
                    if lf:
                        lf.write(json.dumps({'id': e['id'], 'vol': v, 'old': e.get('dimension'),
                                             'new': new_dim}, ensure_ascii=False) + '\n')
                else:
                    print(f'  ⚠ PATCH 失敗 {e["ref_key"][:40]}', flush=True)
            if lf:
                lf.flush()
            print(f'  進度 {min(i + batch_size, len(rows))}/{len(rows)}（累計改 {n_ok}）', flush=True)
    finally:
        if lf:
            lf.close()
    return n_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vol', nargs='*', default=None)
    ap.add_argument('--batch', type=int, default=12)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    done = set()
    if LEDGER.exists():
        for ln in LEDGER.read_text(encoding='utf-8').splitlines():
            try:
                done.add(json.loads(ln)['id'])
            except Exception:
                pass
    print(f'ledger 已處理 {len(done)} 筆', flush=True)

    vols = args.vol or VOLS
    total = 0
    for v in vols:
        total += process_vol(v, args.batch, args.dry_run, done)
    print(f'\n完成：細化 {total} 筆（dry-run={args.dry_run}）', flush=True)


if __name__ == '__main__':
    main()
