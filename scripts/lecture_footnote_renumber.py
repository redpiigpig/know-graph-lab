"""把講義章節的註號重編為正文出現順序，並依同一順序重排註釋區塊。

在既有註釋之間插入新註之後用它收尾——手工改號很容易漏掉 backref，
而漏掉的結果是註號跳不回正文，讀者按了沒反應（這種錯不會報錯，只會變成
「看起來正常的壞頁面」）。

用法：python scripts/lecture_footnote_renumber.py <檔案...>
"""
import re, sys, io


def renumber(path):
    s = io.open(path, encoding='utf-8').read()
    ch = re.search(r'id="fnref-(ch\d+)-\d+"', s).group(1)
    order = [int(n) for n in re.findall(rf'id="fnref-{ch}-(\d+)"', s)]
    if order == list(range(1, len(order) + 1)):
        return 0
    mapping = {old: i + 1 for i, old in enumerate(order)}

    for old, new in mapping.items():
        a = (f'<sup class="footnote-ref"><a href="#fn-{ch}-{old}" '
             f'id="fnref-{ch}-{old}">{old}</a></sup>')
        s = s.replace(a, f'<<M{new}>>')
    for new in mapping.values():
        s = s.replace(f'<<M{new}>>',
                      f'<sup class="footnote-ref"><a href="#fn-{ch}-{new}" '
                      f'id="fnref-{ch}-{new}">{new}</a></sup>')

    bodies = {}
    for blk in re.findall(rf'<div class="fn-item" id="fn-{ch}-\d+">.*?</div></div>',
                          s, re.S):
        old = int(re.search(rf'id="fn-{ch}-(\d+)"', blk).group(1))
        bodies[old] = re.search(r'<div class="fn-body">(.*)<a href="#fnref',
                                blk, re.S).group(1)
    items = '\n'.join(
        f'<div class="fn-item" id="fn-{ch}-{new}"><span class="fn-num">{new}</span>'
        f'<div class="fn-body">{bodies[old]}'
        f'<a href="#fnref-{ch}-{new}" class="footnote-backref">↩</a></div></div>'
        for old, new in sorted(mapping.items(), key=lambda kv: kv[1]))
    start = s.index('<div class="footnotes">') + len('<div class="footnotes">')
    end = s.index('</div>\n\n<h3>參考資料</h3>')
    s = s[:start] + '\n' + items + '\n' + s[end:]
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(mapping)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for f in sys.argv[1:]:
        n = renumber(f)
        print(f'{f}  {"重編 %d 條" % n if n else "順序本已正確"}')
