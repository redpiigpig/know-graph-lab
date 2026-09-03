"""講義章節註釋一致性檢查：marker 編號須 1..N 依序、與 fn-item 一一對應。
用法：python scripts/lecture_footnote_check.py [glob ...]（省略＝四本全查）"""
import re, sys, glob, io

DEFAULT = [
    'public/content/works/christianity-intro/chapters/ch*.html',
    'public/content/works/world-religions-intro/chapters/ch*.html',
    'public/content/works/world-religions-intro/chapters-wr2/ch*.html',
    'public/content/works/sinographic-literature/chapters/ch*.html',
]

def check(path):
    s = io.open(path, encoding='utf8').read()
    marks = [int(n) for n in re.findall(r'id="fnref-ch\d+-(\d+)"', s)]
    notes = [int(n) for n in re.findall(r'id="fn-ch\d+-(\d+)"', s)]
    bad = []
    if marks != list(range(1, len(marks) + 1)):
        bad.append(f'markers not 1..N in order: {marks}')
    if sorted(notes) != sorted(marks):
        bad.append(f'notes {notes} != markers {marks}')
    refs = re.search(r'<h3>參考資料</h3>(.*?)</ul>', s, re.S)
    n_ref = len(re.findall(r'<li>', refs.group(1))) if refs else 0
    return len(marks), n_ref, bad

if __name__ == '__main__':
    pats = sys.argv[1:] or DEFAULT
    fail = 0
    for pat in pats:
        for f in sorted(glob.glob(pat)):
            n, r, bad = check(f)
            flag = '  ✗ ' + '; '.join(bad) if bad else ''
            if bad: fail += 1
            print(f'{f}  notes={n:3d} refs={r:3d}{flag}')
    sys.exit(1 if fail else 0)
