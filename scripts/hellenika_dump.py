#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 把 data/hellenika/*.ts 傾印成 JSON 供批次策展讀取。

TS 檔只用 `import type`，本體是純物件字面量，因此剝掉型別註記後即為合法 JS。
不引入任何相依（不用 jiti/tsx），只借 node 跑一支臨時 .mjs。

用法：
    python scripts/hellenika_dump.py                 # → c:/tmp/hellenika/corpus.json
    python scripts/hellenika_dump.py --out X.json
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'hellenika')
DEFAULT_OUT = 'c:/tmp/hellenika/corpus.json'


def _strip_types(src: str) -> str:
    """剝掉 type-only import 與型別註記，留下合法 JS。"""
    src = re.sub(r"(?m)^import type .*?\n", '', src)
    src = re.sub(r"export const (\w+): HellenCanon =", r"export const \1 =", src)
    return src


def dump() -> dict:
    tmpdir = tempfile.mkdtemp(prefix='hellenika_dump_')
    try:
        for name in ('greek', 'roman'):
            src = io.open(os.path.join(DATA, f'{name}.ts'), encoding='utf-8').read()
            io.open(os.path.join(tmpdir, f'{name}.mjs'), 'w', encoding='utf-8').write(_strip_types(src))

        runner = os.path.join(tmpdir, 'run.mjs')
        io.open(runner, 'w', encoding='utf-8').write(
            "import { GREEK_CANON } from './greek.mjs'\n"
            "import { ROMAN_CANON } from './roman.mjs'\n"
            "process.stdout.write(JSON.stringify([GREEK_CANON, ROMAN_CANON]))\n"
        )
        proc = subprocess.run(['node', runner], capture_output=True, text=True, encoding='utf-8')
        if proc.returncode != 0:
            raise SystemExit(f'node failed:\n{proc.stderr}')
        canons = json.loads(proc.stdout)
    finally:
        for f in os.listdir(tmpdir):
            os.unlink(os.path.join(tmpdir, f))
        os.rmdir(tmpdir)

    works = []
    for canon in canons:
        for volume in canon['volumes']:
            for division in volume['divisions']:
                for i, w in enumerate(division['works']):
                    works.append({
                        'id': f"{canon['key']}:{volume['key']}:{division['key']}:{i}",
                        'canon_key': canon['key'],
                        'canon_name': canon['name'],
                        'volume_key': volume['key'],
                        'volume_sigil': volume['sigil'],
                        'volume_name': volume['name'],
                        'volume_summary': volume['summary'],
                        'volume_parallel': volume.get('parallel'),
                        'division_key': division['key'],
                        'division_label': division['label'],
                        'division_desc': division.get('desc'),
                        'work': w,
                    })

    return {
        'canons': [
            {'key': c['key'], 'name': c['name'],
             'volumes': [{'key': v['key'], 'sigil': v['sigil'], 'name': v['name'],
                          'summary': v['summary'], 'parallel': v.get('parallel'),
                          'clock': v.get('clock'), 'span': v.get('span')}
                         for v in c['volumes']]}
            for c in canons
        ],
        'works': works,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()

    payload = dump()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    io.open(args.out, 'w', encoding='utf-8').write(json.dumps(payload, ensure_ascii=False, indent=1))

    works = payload['works']
    have = sum(1 for w in works if w['work'].get('intro'))
    print(f"{len(works)} 種；已有 intro {have}，待補 {len(works) - have}")
    print(f"→ {args.out}")


if __name__ == '__main__':
    main()
