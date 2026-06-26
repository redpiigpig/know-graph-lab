# -*- coding: utf-8 -*-
"""逐卷 combine+dedup dialogue ch*.md → dry-parse → (optional) ingest。
用法：
  python ingest_all.py dry            # 全卷 dry-parse 報告
  python ingest_all.py dry M1 M2      # 指定卷 dry
  python ingest_all.py apply M1 O2 …  # 指定卷 combine+ingest
"""
import os, sys, re, subprocess, json
from pathlib import Path
from collections import OrderedDict, Counter
ROOT = Path('c:/Users/user/Desktop/know-graph-lab')
DATA = ROOT / 'scripts' / 'data'
sys.path.insert(0, str(ROOT / 'scripts'))
import lit_review as lr
THEME_ORDER = ['自然科學', '心理學', '哲學', '宗教與神話']
ALLVOLS = ['M1','M2','M3','E1','E2','E3','O1','O2','O3','V1','V2','V3','B1','B2','B3']
# E1/E3 已先前 ingest 的章（dialogue），重組時仍納入（idempotent），但這些卷的「新章」才是重點
def chap_files(vol):
    fs = sorted(DATA.glob(f'lit_review_genesis_{vol}_dialogue_ch*.md'),
                key=lambda p: int(re.search(r'ch(\d+)', p.name).group(1)))
    return fs

def combine(vol):
    files = chap_files(vol)
    by_theme = {t: OrderedDict() for t in THEME_ORDER}
    seen = set(); dup = 0; stance = Counter()
    for fn in files:
        md = fn.read_text(encoding='utf-8'); cur = None; buf = []
        def flush():
            nonlocal dup
            if not buf: return
            text = '\n'.join(buf).strip()
            if not text.startswith('【'): return
            e = lr.parse_entry_block(text); rk = e.get('ref_key')
            if not rk or rk in seen:
                if rk: dup += 1
                return
            seen.add(rk)
            th = cur if cur in by_theme else '哲學'
            by_theme[th][rk] = text; stance[e.get('stance')] += 1
        for ln in md.splitlines():
            s = ln.strip()
            if s.startswith('#') and any(s.lstrip('# ').startswith(t) for t in THEME_ORDER):
                flush(); buf = []
                cur = next(t for t in THEME_ORDER if s.lstrip('# ').startswith(t)); continue
            if s.startswith('【'): flush(); buf = [ln]
            elif buf: buf.append(ln)
        flush()
    out = [f'# 創生哲學 {vol} 逐節對話地圖（合併去重）\n']
    tot = 0
    for t in THEME_ORDER:
        if not by_theme[t]: continue
        out.append(f'\n## {t}\n')
        for rk, txt in by_theme[t].items(): out.append(txt + '\n'); tot += 1
    dest = DATA / f'lit_review_genesis_{vol}_dialogue_combined.md'
    dest.write_text('\n'.join(out), encoding='utf-8')
    return dest, tot, dup, dict(stance), {t: len(by_theme[t]) for t in THEME_ORDER if by_theme[t]}, len(files)

def dry(vol):
    if not chap_files(vol):
        print(f'{vol}: (no dialogue files yet)'); return None
    dest, tot, dup, stance, themes, nf = combine(vol)
    p = lr.parse_review_report(dest.read_text(encoding='utf-8'))
    e = p['entries']
    dups = [k for k, c in Counter(x['ref_key'] for x in e).items() if c > 1]
    miss = [x['ref_key'] for x in e if not x.get('dimension') or not x.get('stance')]
    print(f'{vol}: {nf} files → {tot} uniq (dropped {dup} dup), DUP={dups[:3]} miss={len(miss)} stance={stance} themes={themes}')
    return tot

def apply(vol):
    if dry(vol) is None: return
    dest = DATA / f'lit_review_genesis_{vol}_dialogue_combined.md'
    cmd = [sys.executable, '-X', 'utf8', str(ROOT/'scripts'/'ingest_lit_review.py'),
           '--seed', '--entries-only', '--book-id', vol, '--project', 'genesis-philosophy',
           '--display-offset', '200', '--report', str(dest)]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8')
    print('   ', r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dry'
    vols = sys.argv[2:] or ALLVOLS
    for v in vols:
        (apply if mode == 'apply' else dry)(v)
