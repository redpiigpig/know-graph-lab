# -*- coding: utf-8 -*-
"""把四門課簡報資料裡「會投影出去的字」全部攤平出來。

用途有二：
  1. 文字潤飾（course_slides_polish.py）要拿到一份完整、去重、有出處的清單；
  2. 潤飾完要驗證「只有該改的字變了」，得能再攤一次做前後比對。

🚨 只收會出現在投影片上的字：標題、副標、條目、表格、圖說、分節頁。
   圖片 key（'durkheim'）與版面參數不是給人看的，不收。

用法：
  python scripts/course_slides_strings.py            # 印出統計
  python scripts/course_slides_strings.py --dump out.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# 每一種投影片，哪幾個位置是「字」。索引以 item[1:] 為準（item[0] 是類型）。
# None＝該位置整個遞迴收（清單／表格），'skip'＝不收（圖片 key）。
SHAPES = {
    'cover':      ['dict'],
    'section':    ['text', 'text', 'list'],
    'big':        ['text', 'text'],
    'bullets':    ['text', 'list', 'text'],
    'imgbullets': ['text', 'list', 'skip', 'text', 'text'],
    'two':        ['text', 'pair', 'pair', 'text'],
    'table':      ['text', 'list', 'list', 'text', 'text', 'skip'],
    'photo':      ['text', 'skip', 'text', 'text'],
    'gallery':    ['text', 'gallery', 'text'],
}
# kwargs 裡會出現在畫面上的鍵
KW_TEXT = ('sub', 'cap', 'note')


def _walk_list(node, out):
    if isinstance(node, str):
        if node.strip():
            out.append(node)
    elif isinstance(node, (list, tuple)):
        for x in node:
            _walk_list(x, out)


def deck_strings(deck):
    """回傳這一份 deck 會投影出去的所有字（依出現順序，可能重複）。"""
    out = []
    for key in ('kicker', 'title', 'subtitle'):
        if key in deck:
            out.append(deck[key])
    _walk_list(deck.get('footer', ''), out)
    for item in deck['slides']:
        out.extend(slide_strings(item))
    return out


def slide_strings(item):
    out = []
    kind, args = item[0], list(item[1:])
    if args and isinstance(args[-1], dict) and kind != 'cover':
        kw = args.pop()
        for k in KW_TEXT:
            if kw.get(k):
                out.append(kw[k])
    spec = SHAPES.get(kind, [])
    for i, a in enumerate(args):
        how = spec[i] if i < len(spec) else 'list'
        if how == 'skip':
            continue
        if how == 'dict' and isinstance(a, dict):
            for k in ('kicker', 'title', 'subtitle'):
                if a.get(k):
                    out.append(a[k])
            _walk_list(a.get('meta', []), out)
            continue
        if how == 'gallery':
            # [(圖 key, 說明), ...]——只收說明
            for it in a:
                if isinstance(it, (list, tuple)) and len(it) > 1:
                    _walk_list(it[1], out)
            continue
        if how == 'pair':
            # (欄標題, [條目...])
            _walk_list(a, out)
            continue
        _walk_list(a, out)
    return out


def load_all():
    """{課程代號: {次數: deck}}。"""
    from course_slides_data import DECKS as D1
    from course_slides_data2 import DECKS2
    from course_slides_data3 import DECKS3
    from course_slides_data4 import DECKS4
    from course_slides_data_ch import DECKS_CH
    from course_slides_data_sl import DECKS_SL
    return {'wr': {**D1, **DECKS2, **DECKS3, **DECKS4},
            'ch': DECKS_CH, 'sl': DECKS_SL}


def collect():
    """回傳 {字串: [出處, ...]}，出處是 '課程/次數'。"""
    seen = {}
    for course, decks in load_all().items():
        for no, deck in sorted(decks.items()):
            for s in deck_strings(deck):
                seen.setdefault(s, []).append(f'{course}/{no}')
    # 開場互動那兩頁的題目也是投影出去的字
    try:
        from course_slides_openers import OPENERS
    except ImportError:
        return seen
    for course, byno in OPENERS.items():
        for no, d in sorted(byno.items()):
            for q in list(d.get('ask', [])) + list(d.get('answer', [])):
                seen.setdefault(q, []).append(f'{course}/開場{no}')
    return seen


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    seen = collect()
    total = sum(len(v) for v in seen.values())
    chars = sum(len(s) for s in seen)
    print(f'不重複字串 {len(seen)} 條（出現 {total} 次），合計 {chars} 字')
    if '--dump' in sys.argv:
        out = Path(sys.argv[sys.argv.index('--dump') + 1])
        out.write_text(json.dumps(
            [{'text': k, 'where': v} for k, v in seen.items()],
            ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'→ {out}')
