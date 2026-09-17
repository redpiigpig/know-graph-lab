# -*- coding: utf-8 -*-
"""版面預檢：不出 PDF，直接用渲染器自己的估算式檢查每一頁裝不裝得下。

`course_slides_audit.py` 是**量 PDF**（權威，但要先跑 office_to_pdf，一份三十秒）。
這一支是**量估算**：跑完三十七份只要幾秒，適合改完版面參數先掃一遍，
確定沒有明顯的溢出再去出 PDF。兩者不互相取代——

  🚨 估算通過不代表 PDF 一定乾淨（PowerPoint 的實際斷行與估算不會完全一樣），
     所以**最後一定還是要跑 course_slides_audit.py**。
  🚨 但估算抓得到 audit 抓不到的東西：audit 只看得到「已經出成 PDF 的那一版」，
     改完參數還沒重出時它報的是舊版的結果。

用法：
  python scripts/course_slides_fitcheck.py            # 四門全掃
  python scripts/course_slides_fitcheck.py christianity
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import course_slides_pptx as R        # noqa: E402
import course_slides_weekly as W      # noqa: E402
import course_schedule as CS          # noqa: E402


def _items(slide):
    """回傳 (條目表, 文字欄寬 cm, 可用高 cm, 字級表, 間距表, grow) 或 None。"""
    kind = slide[0]
    kw = slide[-1] if isinstance(slide[-1], dict) else {}
    sub = kw.get('sub') if kw else None
    if kind in ('bullets', 'two', 'table') and isinstance(slide[-1], str):
        sub = slide[-1]
    if kind == 'bullets':
        top = R.title_block(slide[1], sub)[2]
        return (list(slide[2]), R.BOX_W, R.BODY_BOTTOM - top,
                R.BULLET_SZ, R.BULLET_SP, R.GROW, 1.3, (0, 0.9, 1.6))
    if kind == 'imgbullets':
        top = R.title_block(slide[1], sub)[2]
        h = R.BODY_BOTTOM - top
        # 文字欄寬是由窄到寬試出來的，估算與渲染必須走同一支 img_layout
        return (list(slide[2]), R.img_layout(list(slide[2]), h), h,
                R.IMG_SZ, R.IMG_SP, R.GROW, 1.3, (0, 0.9, 1.6))
    if kind == 'quote':
        lines, k3 = list(slide[2]), kw
        h = (R.BODY_BOTTOM - R.title_block(slide[1], k3.get('sub'))[2]
             - (R.SRC_H if k3.get('source') else 0))
        return (R._quote_items(lines, k3.get('alt')), R.BOX_W - 2 * R.PANEL_PAD, h,
                R.QUOTE_SZ, R.QUOTE_SP, 1.0, R.QUOTE_LINE, (0, 0.6, 0.6))
    return None


def check(key):
    c = CS.COURSES[key]
    src, folder = W.SOURCE[key]
    R.FOLDER = folder
    R.IMGDIR = R.DRIVE / folder / '簡報' / '圖片'
    R.MANIFEST = R.load_manifest()
    R.CHAPTERS = R.CHAPTER_DIRS[src]
    pool = W.chapter_slides(src)
    bad = 0
    for i, (label, _date, title, chs) in enumerate(CS.units(c), 1):
        slides = W._walk([s for ch in chs for s in pool.get(ch, [])], set(chs))
        if not slides:
            continue
        cap = W.CAP[key]
        for split_at, floor in W.LADDER:
            R.SPLIT_AT, R.FIT_FLOOR = split_at, floor
            prepared = R.prepare(slides, src)
            if sum(1 for s in prepared if s[0] != 'quote') <= cap:
                break
        for s in prepared:
            got = _items(s)
            if not got:
                continue
            items, w, h, sizes, sp, grow, line, ind = got
            k = R.fit(items, w, h * R.FIT_MARGIN, sizes, sp,
                      line=line, indent_cm=ind, grow=grow)
            # 重算這個字級下真正的高度——fit 內部的 height_at 是區域函式，
            # 這裡用同一條算式再算一次，當作獨立的第二意見。
            LINE = 1.60 / 1.3 * line
            tot = 0.0
            for it in items:
                lvl, txt = (it if isinstance(it, tuple) else (0, it))
                if not txt:
                    tot += sizes[0] * 0.5 * k
                    continue
                sz = sizes[lvl] * k
                avail = (w - ind[min(lvl, 2) if lvl != 3 else 0]) * R.CM_PT
                rows = -(-(len(txt) + 2) // max(8, int(avail / sz)))
                tot += rows * sz * LINE + sp[lvl] * k
            if tot > h * R.CM_PT:
                bad += 1
                over = tot - h * R.CM_PT
                print(f'  ✘ {c["code"]} {label}　{s[0]}「{str(s[1])[:30]}」'
                      f'　超出 {over:.0f}pt（k={k:.2f}）')
    return bad


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    keys = [a for a in sys.argv[1:] if a in W.SOURCE] or list(W.SOURCE)
    total = 0
    for k in keys:
        print(f'── {CS.COURSES[k]["name"]}（{CS.COURSES[k]["code"]}）')
        total += check(k)
    print(f'\n估算上裝不下的頁：{total}')
