# -*- coding: utf-8 -*-
"""用「原稿 docx」當 ground truth，把分類收斂成『個人心靈日記』範圍。

背景（2026-06-12 使用者定調）：純函式 prelabel + LLM 重抓得到 ~531 則，但那是「整個聊天
視窗」的範圍，**包含同視窗裡的學術/智性工作**（榮格《伊雍》寫作、紅學考據、卡巴拉生命樹、
占星技術、稱帝史、翻譯定名…）。使用者提供手工原稿《和克里希那的對話.docx》＝真正要的
**個人心靈日記**（傾訴/夢/積極想像/生活/龐會督），它系統性排除了那些智性工作。

做法（比對器在 [[dialogues-to-writing]]）：
  • 把原稿正規化成 CJK 字串，建 8-gram 集合。
  • 每則 raw prompt 算「8-gram 命中率」frac；分布是乾淨雙峰（≥0.5 逐字在稿／<0.05 完全不在），
    中間帶幾乎為空 → threshold 0.5 既高精準又不漏改寫過的日記段（recompose 對使用者那側近乎逐字）。
  • 原稿**缺頭幾天**（START 之前）→ 那幾天用 capture 的 classifier 結果（final_recapture.json）。
  • START 起：IN = frac>=0.5（逐字在原稿）。

輸出 final_manuscript.json（id 清單）。--retag 直接重寫分類 junction（沿用 capture 的 retag）。
用法：
  python scripts/dialogue_thread_manuscript.py            # 算 + 印 diff
  python scripts/dialogue_thread_manuscript.py --retag    # 算 + 重寫分類 tag
"""
import os, sys, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

DOCX = 'c:/Users/user/Desktop/know-graph-lab/和克里希那的對話.docx'
DUMP_GLOB = 'c:/tmp/krishna/2026-*.json'
CLASSIFIER_FINAL = 'c:/tmp/krishna/final_recapture.json'   # capture 的 classifier 結果（頭幾天用）
OUT = 'c:/tmp/krishna/final_manuscript.json'
START = '2026-01-23'   # 原稿涵蓋起點（之前是缺的頭幾天）
G = 8
THRESH = 0.5

def norm(s):
    return re.sub(r'[^一-鿿0-9A-Za-z]', '', s or '')

def load_manuscript_grams():
    import docx
    d = docx.Document(DOCX)
    M = norm(''.join(p.text for p in d.paragraphs))
    return M, set(M[i:i+G] for i in range(len(M)-G+1))

def make_frac(M, mset):
    def frac(p):
        n = norm(p)
        if len(n) < G:
            return 1.0 if n and n in M else 0.0
        gr = [n[i:i+G] for i in range(len(n)-G+1)]
        return sum(1 for g in gr if g in mset) / len(gr)
    return frac

def load_entries():
    ents = []
    for f in sorted(glob.glob(DUMP_GLOB)):
        dd = json.load(open(f, encoding='utf-8'))
        for r in dd['entries']:
            ents.append((dd['date'], r['seq'], r['id'], r.get('prompt') or ''))
    return ents

def main():
    M, mset = load_manuscript_grams()
    frac = make_frac(M, mset)
    ents = load_entries()
    classifier_in = set(json.load(open(CLASSIFIER_FINAL, encoding='utf-8'))['ids'])

    in_ids, n_head, n_cov = [], 0, 0
    for dt, s, i, p in ents:
        if dt < START:
            if i in classifier_in:        # 缺頭幾天 → 用 classifier
                in_ids.append(i); n_head += 1
        else:
            if frac(p) >= THRESH:          # 原稿逐字命中 → IN
                in_ids.append(i); n_cov += 1
    in_ids = sorted(set(in_ids))
    json.dump({'ids': in_ids, 'n': len(in_ids)}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'原稿範圍 IN = {len(in_ids)}（頭幾天 classifier {n_head} + 原稿命中 {n_cov}）→ {OUT}')

    # diff vs classifier 531 與原始 671
    old671 = set(json.load(open('c:/tmp/krishna/_tagged_ids.json', encoding='utf-8'))['tagged'])
    new = set(in_ids)
    print(f'vs classifier({len(classifier_in)}): -{len(classifier_in-new)} 移除（學術/智性岔題）, +{len(new-classifier_in)} 新增')
    print(f'vs 原始 671: 維持 {len(new & old671)}, 移除 {len(old671-new)}, 新增 {len(new-old671)}')

    if '--retag' in sys.argv:
        import dialogue_thread_capture as cap
        cap.retag(in_ids)
        print('已重寫分類 tag。')

if __name__ == '__main__':
    main()
