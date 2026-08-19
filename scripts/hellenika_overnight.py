#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 整夜策展驅動器。

輪流跑三件事，跑到待辦清空或時限到：
  A. intro 補寫（scripts/hellenika_intro.py --all）
  B. 銘文取源（scripts/hellenika_cgrn.py，若存在）
  C. 驗證＋commit＋push

Gemini 額度用罄時 intro 會自動落到 NVIDIA；兩邊都乾就靜待下一輪
（Gemini key 冷卻 1 小時後自行恢復），不中止整夜。

只管自己啟動的子程序，絕不去動別人的（見 feedback_no_kill_other_tasks）。

用法：
    python scripts/hellenika_overnight.py --hours 10
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = 'c:/tmp/hellenika/overnight.log'
CORPUS = 'c:/tmp/hellenika/corpus.json'
INTROS = os.path.join(ROOT, 'data', 'hellenika', 'intros.json')


def log(msg: str) -> None:
    line = f'[{time.strftime("%m-%d %H:%M:%S")}] {msg}'
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with io.open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def run(cmd: list[str], timeout: float = 5400) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except subprocess.TimeoutExpired:
        return 124, f'timeout after {timeout}s'


def count_pending() -> tuple[int, int]:
    if not os.path.exists(CORPUS):
        return -1, -1
    corpus = json.loads(io.open(CORPUS, encoding='utf-8').read())
    intros = json.loads(io.open(INTROS, encoding='utf-8').read()) if os.path.exists(INTROS) else {}
    total = len(corpus['works'])
    done = sum(1 for w in corpus['works'] if w['work'].get('intro') or w['id'] in intros)
    return done, total


def git_dirty() -> bool:
    _, out = run(['git', 'status', '--porcelain', 'data/hellenika'], timeout=120)
    return bool(out.strip())


def commit(done: int, total: int) -> None:
    if not git_dirty():
        return
    run(['git', 'add', 'data/hellenika'], timeout=120)
    msg = (f'chore(hellenika): 條目簡介補寫 {done}/{total}\n\n'
           '由 scripts/hellenika_overnight.py 整夜批次產生，'
           '規範見 .claude/skills/hellenika-curate/SKILL.md §1（四要件與六禁忌）。\n\n'
           'Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>')
    rc, out = run(['git', '-c', 'core.hooksPath=.githooks', 'commit', '-q', '-m', msg], timeout=1800)
    if rc != 0:
        log(f'  commit 失敗：{out[-400:]}')
        return
    rc, out = run(['git', 'push', '-q', 'origin', 'master'], timeout=900)
    log('  ✓ commit+push' if rc == 0 else f'  push 失敗：{out[-300:]}')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=float, default=10.0)
    args = ap.parse_args()

    deadline = time.time() + args.hours * 3600
    log(f'=== 整夜策展開始，時限 {args.hours} 小時 ===')
    rounds = 0
    stalled = 0

    while time.time() < deadline:
        rounds += 1
        before, total = count_pending()

        rc, out = run([sys.executable, 'scripts/hellenika_dump.py'], timeout=300)
        if rc != 0:
            log(f'第 {rounds} 輪 dump 失敗：{out[-300:]}')
            time.sleep(120)
            continue

        done, total = count_pending()
        if done >= total:
            log(f'✅ intro 全數完成 {done}/{total}')
            commit(done, total)
            break

        log(f'--- 第 {rounds} 輪：intro {done}/{total}，待補 {total - done} ---')
        rc, out = run([sys.executable, 'scripts/hellenika_intro.py', '--all'],
                      timeout=min(5400, max(600, deadline - time.time())))
        tail = '\n'.join(l for l in out.splitlines() if l.strip())[-1200:]
        log(tail if tail else '(無輸出)')

        after, total = count_pending()
        gained = after - done
        log(f'--- 第 {rounds} 輪產出 {gained} 筆，累計 {after}/{total} ---')

        if gained > 0:
            commit(after, total)
            stalled = 0
        else:
            stalled += 1
            wait = min(1800, 300 * stalled)     # 兩邊引擎都乾，等 key 冷卻恢復
            log(f'  本輪無產出（連續 {stalled} 次），等 {wait}s 讓額度恢復')
            if time.time() + wait >= deadline:
                break
            time.sleep(wait)

    done, total = count_pending()
    log(f'=== 整夜策展結束：intro {done}/{total}，共 {rounds} 輪 ===')


if __name__ == '__main__':
    main()
