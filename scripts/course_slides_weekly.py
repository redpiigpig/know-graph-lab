# -*- coding: utf-8 -*-
"""課堂簡報 —— **按週次**出，不按章節。

既有的 `course_slides_data*.py` 是「八次上課×兩章」的組法；週三兩門其實是
每週一個單元共十六週，假日班則是每次一個單元。本檔把既有內容依章拆開，
再照 `course_schedule.py` 的週次表重新編組，交 `course_slides_pptx.py` 渲染。

🚨 **投影片上不出現章號。** 講義章節是使用者自己的備課編號、不發給學生
（2026-09-07 定調），所以這裡會改寫分節頁的標記、封面副標與課末書目頁的說明。

🚨 **每學期第一次上課固定插一頁自我介紹**（封面與開場互動之後）。

用法：
  python scripts/course_slides_weekly.py                    # 四門全出
  python scripts/course_slides_weekly.py wr-day             # 只出某一門
  python scripts/course_slides_weekly.py wr-day 1 2         # 只出某門的第 1、2 週
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import course_schedule as CS          # noqa: E402
import course_slides_pptx as R        # noqa: E402

# 一份簡報的「內容頁」張數上限（使用者 2026-09-07 定）。
# 封面、開場互動兩頁、自我介紹、演講行程頁、參考書目、圖片出處都不算在內——
# 那些不是要講的內容。平日班一節 100 分鐘、假日班一次四小時，所以差一倍。
CAP = {'wr-day': 30, 'christianity': 30, 'chinese': 50, 'wr-weekend': 50}

# 壓張數的階梯：(SPLIT_AT, FIT_FLOOR)。往下走＝密的頁改「縮字」不「拆頁」。
LADDER = [(0.78, 0.72), (0.74, 0.68), (0.70, 0.64),
          (0.66, 0.60), (0.62, 0.56), (0.58, 0.52)]

# 四門課各一套配色（見 course_slides_pptx.PALETTES）——同一個版型、不同色系，
# 抽錯簡報一眼看得出來。使用者 2026-09-08：「不用每堂課都一樣」。
PALETTE = {'wr-day': 'blue', 'christianity': 'green',
           'chinese': 'rust', 'wr-weekend': 'indigo'}

# course_schedule 的鍵 →（簡報內容來源代號, Drive 資料夾）
SOURCE = {
    'wr-day': ('wr', '115-1_世界宗教文化導論'),
    'wr-weekend': ('wr', '115-1_世界宗教文化導論'),
    'christianity': ('ch', '115-1_基督宗教概論'),
    'chinese': ('sl', '115-1_宗教系國文講義'),
}

ZH = '一二三四五六七八九十'


def _chapter_no(label):
    """從分節頁的標記抓章號：'第一章'→1、'第十二章‧第三段'→12；抓不到回 None。"""
    m = re.match(r'第([一二三四五六七八九十]+)章', label or '')
    if not m:
        return None
    s = m.group(1)
    if s.startswith('十'):
        return 10 + (ZH.index(s[1]) + 1 if len(s) > 1 else 0)
    if '十' in s:
        return (ZH.index(s[0]) + 1) * 10 + (ZH.index(s[2]) + 1 if len(s) > 2 else 0)
    return ZH.index(s) + 1


def _strip_chapter(label):
    """分節頁標記去掉章號：'第一章‧第三段'→'第三段'、'第一章'→''。"""
    return re.sub(r'^第[一二三四五六七八九十]+章[‧·]?', '', label or '').strip()


def load_decks(src):
    if src == 'ch':
        from course_slides_data_ch import DECKS_CH as D
    elif src == 'sl':
        from course_slides_data_sl import DECKS_SL as D
    else:
        from course_slides_data import DECKS as D1
        from course_slides_data2 import DECKS2
        from course_slides_data3 import DECKS3
        from course_slides_data4 import DECKS4
        D = {**D1, **DECKS2, **DECKS3, **DECKS4}
    return D


def chapter_slides(src):
    """把既有各次的內容拆成 {章號: [slide, ...]}（不含封面）。

    每次上課涵蓋第 2n−1、2n 章；分節頁的章號是切點，切點之前的鋪陳歸該次的頭一章。
    """
    out = {}
    for no, deck in load_decks(src).items():
        cur = no * 2 - 1
        for item in deck['slides']:
            if item[0] == 'cover':
                continue
            if item[0] == 'section':
                ch = _chapter_no(item[1])
                if ch:
                    cur = ch
                item = ('section', _strip_chapter(item[1])) + tuple(item[2:])
            # 舊資料第 1 次夾了一頁「這門課怎麼上」，內容是假日班的次數與章號分部，
            # 掛到日間部就是錯的；課程說明改由 intro_slide() 依各課資料重生。
            if item[0] == 'bullets' and '這門課怎麼上' in str(item[1]):
                continue
            out.setdefault(cur, []).append(_clean_subs(item))
    return out


CH_REF = re.compile(r'第[一二三四五六七八九十]+(、[一二三四五六七八九十]+)*章[‧·]?')


def _clean_subs(item):
    """把副標裡的章號拿掉——'第五、六章' 這種字串會直接投影給學生看到。

    副標可能是結尾的 kwargs dict，也可能是位置參數的字串；兩種都要清，
    否則整條副標只剩交叉引用被改寫成的「其他單元」，比留著還糟。
    """
    if item and isinstance(item[-1], dict) and 'sub' in item[-1]:
        kw = dict(item[-1])
        sub = CH_REF.sub('', kw['sub'] or '').strip('　 ‧·、')
        if sub:
            kw['sub'] = sub
        else:
            kw.pop('sub')
        return tuple(item[:-1]) + ((kw,) if kw else ())
    if (item[0] in ('bullets', 'imgbullets', 'two', 'table')
            and isinstance(item[-1], str) and CH_REF.search(item[-1])):
        sub = CH_REF.sub('', item[-1]).strip('　 ‧·、')
        return tuple(item[:-1]) + ((sub,) if sub else ())
    return item


# 沒帶數字的章別稱呼也是章號洩漏的一種，只是抓不到 CH_REF。
BARE_CH = [('每一章', '每一個單元'), ('每章', '每個單元'), ('本章', '本單元'),
           ('這一章', '這個單元'), ('該章', '該單元'), ('下一章', '下一個單元'),
           ('上一章', '上一個單元'), ('各章', '各單元'), ('前幾章', '前幾個單元'),
           ('後幾章', '後幾個單元'), ('兩章', '兩個單元'), ('三章', '三個單元')]


def intro_slide(c):
    """第一次上課的課程說明頁——依各門課自己的資料生成，不出現章號。"""
    sessions = CS.units(c)
    exams = [(lb, dt, ti) for lb, dt, ti, _e, _c in c['rows'] if '考' in ti]
    self_study = [(lb, dt) for lb, dt, ti, _e, _c in c['rows']
                  if ti.startswith(CS.SELF_STUDY)]
    b = [
        f"上課時間：{c['time']}，{c['room']}",
        (1, f'正課共 {len(sessions)} 次；另有自主學習與文本閱讀 '
            f'{len(self_study)} 次，不到校'),
        '成績評量',
    ]
    b += [(1, f'{item}　{pct}') for item, pct in c['assessment']]
    if exams:
        b.append('考試')
        b += [(1, f'{lb}（{dt}）　{ti}') for lb, dt, ti in exams]
    if self_study:
        b.append('自主學習與文本閱讀')
        b += [(1, f'{lb}（{dt}）不到校，自行研讀指定內容並與教師個別討論自評')
              for lb, dt in self_study]
    return ('bullets', '這門課怎麼上', b, {'sub': '課程說明與評量方式'})


def cover_for(c, label, date, title):
    return {
        'kicker': f"玄奘大學　{c['klass']}　{c['code']}",
        'title': c['name'],
        'subtitle': f'{label}　{title}',
        'meta': [f"{date}　{c['time'].split('　', 1)[-1]}", c['room'],
                 f'授課教師：{CS.TEACHER}'],
    }


ZH_NUM = {c: i + 1 for i, c in enumerate(ZH)}


def _zh_int(s):
    if s.startswith('十'):
        return 10 + (ZH_NUM[s[1]] if len(s) > 1 else 0)
    if '十' in s:
        return ZH_NUM[s[0]] * 10 + (ZH_NUM[s[2]] if len(s) > 2 else 0)
    return ZH_NUM[s]


def _derefer(text, chs):
    """把正文裡的交叉引用『第十四章』換成中性說法。

    直接刪掉會把句子砍斷（「見第十四章」→「見」），所以依前後關係換詞。
    """
    def sub(m):
        nums = [_zh_int(x) for x in re.findall(r'[一二三四五六七八九十]+', m.group(0))]
        if all(n in chs for n in nums):
            return '本單元'
        if all(n > max(chs) for n in nums):
            return '後面的單元'
        if all(n < min(chs) for n in nums):
            return '前面的單元'
        return '其他單元'
    text = CH_REF.sub(sub, text)
    for a, b in BARE_CH:
        text = text.replace(a, b)
    return text


def _walk(node, chs):
    if isinstance(node, str):
        return _derefer(node, chs)
    if isinstance(node, tuple):
        return tuple(_walk(x, chs) for x in node)
    if isinstance(node, list):
        return [_walk(x, chs) for x in node]
    if isinstance(node, dict):
        return {k: _walk(v, chs) for k, v in node.items()}
    return node


def guest_slide(c, label):
    """演講／校外參訪那幾週，封面後先放一頁行程說明。

    這幾週由講者或現場主導，後面的講授內容保留著當備用（講者提早結束就接得上），
    不是拿掉不用。
    """
    extra = next((e for lb, _d, _t, e, _c in c['rows'] if lb == label), [])
    lines = [x for x in extra if x.startswith('【')]
    if not lines:
        return None
    rest = [x for x in extra if not x.startswith('【')]
    head, _, body = lines[0].partition('】')
    # 用 section 而不是 big：fold_bigs 會把 big 併進下一頁，這一頁必須自己站著。
    return ('section', head.strip('【'), body.strip() or head.strip('【'), rest)


def build_course(key, only=None):
    c = CS.COURSES[key]
    src, folder = SOURCE[key]
    R.FOLDER = folder
    R.IMGDIR = R.DRIVE / folder / '簡報' / '圖片'
    R.MANIFEST = R.load_manifest()
    R.CHAPTERS = R.CHAPTER_DIRS[src]
    R.use_palette(PALETTE[key])
    pool = chapter_slides(src)

    made = []
    for i, (label, date, title, chs) in enumerate(CS.units(c), 1):
        if only and i not in only:
            continue
        slides = _walk([s for ch in chs for s in pool.get(ch, [])], set(chs))
        if not slides:
            print(f'⚠ {c["code"]} {label} {title}：沒有可用的內容（章 {chs}），略過')
            continue
        deck = {
            'filename': f'{c["code"]}_{label.replace(" ", "")}_{title[:14]}.pptx',
            'footer': f'{c["name"]}　{label}　{title}',
            'slides': ([('cover', cover_for(c, label, date, title))]
                       + ([intro_slide(c)] if i == 1 else [])
                       + [g for g in [guest_slide(c, label)] if g] + slides),
        }
        # 內容頁超過上限就一階一階調降，讓密的頁改用縮字而不是再拆一頁。
        cap = CAP[key]
        for split_at, floor in LADDER:
            R.SPLIT_AT, R.FIT_FLOOR = split_at, floor
            n = len(R.prepare(slides, src))
            if n <= cap:
                break
        if n > cap:
            print(f'　（{label} 壓到 {n} 張仍超過 {cap}，內容本身就偏多）')

        # 🚨 開場互動題庫是按「八次上課×兩章」編的，索引不是週次。
        # 週次化之後要用本單元頭一章回推：第 n 次＝第 2n−1、2n 章。
        opener_no = (min(chs) + 1) // 2
        out, cnt = R.build(deck, no=opener_no, course=src, refs=chs,
                           profile=(i == 1))
        made.append((out, cnt))
        print(f'✔ {out}　（{cnt} 張）')
    return made


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    keys = [a for a in args if a in SOURCE] or list(SOURCE)
    only = {int(a) for a in args if a.isdigit()} or None
    for k in keys:
        build_course(k, only)
