# -*- coding: utf-8 -*-
"""把講義章末小考的選項順序打散（紙本與 Kahoot 共用同一個順序）。

為什麼要做：原本各章的正確選項落在一個固定循環的位置上（第一章
BABADDDDAB、第二章 CCCBABADDD…），而且三門課十六章的序列完全相同。
答案本身沒錯，但位置有規律，學生不必讀題也能猜。

為什麼用內容雜湊而不用亂數：這支腳本必須是**冪等**的——重跑要得到同樣的
順序，否則每跑一次紙本就和已經建好的 Kahoot 對不起來。順序由
md5(章節+題號+選項文字) 決定，只跟內容有關，與目前的排列無關，因此
重跑、甚至先跑再跑都收斂到同一個結果。

用法：
  python scripts/course_quiz_shuffle.py            # 全部三門課
  python scripts/course_quiz_shuffle.py --check    # 只檢查不改（列出目前序列）
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUIZ_DIRS = [
    ROOT / 'public/content/works/christianity-intro/quizzes',
    ROOT / 'public/content/works/sinographic-literature/quizzes',
    ROOT / 'public/content/works/world-religions-intro/quizzes',
]
LETTERS = 'ABCD'


def order_key(seed, text):
    return hashlib.md5(f'{seed}||{text}'.encode('utf-8')).hexdigest()


def process(path, write=True):
    s = path.read_text(encoding='utf-8')
    stem = path.stem                      # 例：ch1-ch01
    blocks = list(re.finditer(r'<ul class="q-options">(.*?)</ul>', s, re.S))
    m = re.search(r'(<div class="quiz-answers">.*?<ol>)(.*?)(</ol>)', s, re.S)
    if not blocks or not m:
        return None
    keys = re.findall(r'<strong>\(([A-D])\)</strong>', m.group(2))
    if len(keys) != len(blocks):
        raise ValueError(f'{path.name}：題數 {len(blocks)} 與答案數 {len(keys)} 不符')

    new_keys, pieces, last = [], [], 0
    for i, (blk, key) in enumerate(zip(blocks, keys), 1):
        opts = [re.sub(r'^\([A-D]\)\s*', '', o).strip()
                for o in re.findall(r'<li>(.*?)</li>', blk.group(1), re.S)]
        correct_text = opts[LETTERS.index(key)]
        ordered = sorted(opts, key=lambda t: order_key(f'{stem}-{i}', t))
        new_keys.append(LETTERS[ordered.index(correct_text)])
        html = '\n' + '\n'.join(
            f'<li>({LETTERS[j]}) {t}</li>' for j, t in enumerate(ordered)) + '\n'
        pieces.append(s[last:blk.start(1)])
        pieces.append(html)
        last = blk.end(1)
    pieces.append(s[last:])
    s2 = ''.join(pieces)

    # 解析區的開頭字母跟著換（本檔已確認解析不會另外引用其他選項代號）
    it = iter(new_keys)
    m2 = re.search(r'(<div class="quiz-answers">.*?<ol>)(.*?)(</ol>)', s2, re.S)
    body = re.sub(r'<strong>\([A-D]\)</strong>',
                  lambda _: f'<strong>({next(it)})</strong>', m2.group(2))
    s2 = s2[:m2.start(2)] + body + s2[m2.end(2):]

    if write and s2 != s:
        path.write_text(s2, encoding='utf-8')
    return ''.join(keys), ''.join(new_keys)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    check = '--check' in sys.argv
    changed = 0
    for d in QUIZ_DIRS:
        for f in sorted(d.glob('*-ch*.html')):
            r = process(f, write=not check)
            if not r:
                continue
            old, new = r
            if old != new:
                changed += 1
            print(f'{f.parent.parent.name[:14]:14s} {f.name:16s} {old} → {new}')
    print(f'\n{"（--check：未寫入）" if check else "已更新"} {changed} 份')
