#!/usr/bin/env python
"""異譯對讀（巴利系自動版）機械抽查：純讀檔，不呼叫模型。

用法：python -X utf8 scripts/tripitaka_compare_audit.py [--family pi] [--out output/tripitaka_pali_auto_audit.json]

對 index.json 裡 family==pi 且 auto==true 的每一組，算：
  n_units / n_versions
  empty_frac      空格比例（各本各節）
  cum_dev         各本累積字數曲線與各漢譯中位曲線的最大偏離（KS 式，0~1；對齊錯位時偏大）
  pali_cum_dev    巴利本（拉丁字母）累積曲線 vs 漢譯中位曲線
  cross_frac      相鄰節錯位疑似：漢譯兩本間，第 n 節與對方第 n±1 節的字二元組相似度高於同節的比例
  doc_sim         漢譯本之間整體字二元組 Jaccard（偏低＝可能配錯經；注意阿含本來就會差很多）
  midsent_frac    節尾不是句末標點的比例（漢譯）
  len_ratio       各本總字數最大/最小（漢譯之間）
  overlap_min/mean 各本兩兩之間「同節都有字」的比例（低＝各本內容落在不同節）
  dumped_versions 整本塞進一兩節的版本（最大單格 >60% 全文，其餘本攤開）
  tiny_units      只有 1–2 節
  score           綜合可疑分數
"""
import argparse, json, re, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CMP = ROOT / 'public' / 'content' / 'tripitaka' / 'compare'
END = set('。！？；」』”）.!?;:）：')
CJK = re.compile(r'[㐀-鿿]')


def clen(s, lang):
    if lang == 'lzh':
        return len(CJK.findall(s))
    return len(re.findall(r'\w', s))


def bigrams(s):
    t = CJK.findall(s)
    return {a + b for a, b in zip(t, t[1:])}


def jac(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cum(vals):
    tot = sum(vals)
    if tot == 0:
        return None
    out, c = [], 0
    for v in vals:
        c += v
        out.append(c / tot)
    return out


def audit(slug):
    j = json.loads((CMP / f'{slug}.json').read_text(encoding='utf8'))
    units = [u['id'] for u in j['units']]
    vers = j['versions']
    cells = j['cells']
    n = len(units)
    txt = {v['id']: [(cells.get(u, {}).get(v['id']) or '').strip() for u in units] for v in vers}
    lang = {v['id']: v.get('lang') for v in vers}
    # 原典側＝巴利／梵／藏等非漢文本，加上漢譯南傳（nan-，是巴利的漢譯、與巴利逐句同步）；漢譯側＝其餘漢文本
    side_p = lambda v: lang[v['id']] != 'lzh' or v['id'].startswith('nan-')
    zh = [v['id'] for v in vers if not side_p(v)]
    pi = [v['id'] for v in vers if side_p(v)]
    r = {'slug': slug, 'title': j.get('title'), 'n_units': n, 'n_versions': len(vers),
         'n_zh': len(zh), 'n_other': len(pi)}
    r['has_nan'] = any(v['id'].startswith('nan-') for v in vers)
    cells_total = n * len(vers)
    empty = sum(1 for v in txt for t in txt[v] if not t)
    r['empty_frac'] = round(empty / cells_total, 3) if cells_total else 1
    per_empty = {v: sum(1 for t in txt[v] if not t) / n for v in txt} if n else {}
    r['max_version_empty'] = round(max(per_empty.values()), 3) if per_empty else 1
    lens = {v: [clen(t, lang[v]) for t in txt[v]] for v in txt}
    tot = {v: sum(lens[v]) for v in lens}
    zt = [tot[v] for v in zh if tot[v] > 0]
    r['len_ratio'] = round(max(zt) / min(zt), 2) if len(zt) >= 2 else None
    r['tiny_units'] = n <= 2
    # 累積曲線偏離
    curves = {v: cum(lens[v]) for v in lens}
    zc = [curves[v] for v in zh if curves[v]]
    if len(zc) >= 1 and n >= 3:
        med = [statistics.median(c[i] for c in zc) for i in range(n)]
        devs = {v: max(abs(curves[v][i] - med[i]) for i in range(n)) for v in zh if curves[v]}
        r['cum_dev'] = round(max(devs.values()), 3)
        pdv = [max(abs(curves[v][i] - med[i]) for i in range(n)) for v in pi if curves[v]]
        r['pali_cum_dev'] = round(max(pdv), 3) if pdv else None
        r['worst_version'] = max(devs, key=devs.get)
    else:
        r['cum_dev'] = r['pali_cum_dev'] = None
    # 相鄰錯位
    bg = {v: [bigrams(t) for t in txt[v]] for v in zh}
    cross = tot_pairs = 0
    cross_units = set()
    for i, a in enumerate(zh):
        for b in zh[i + 1:]:
            for k in range(n):
                if not bg[a][k] or not bg[b][k]:
                    continue
                same = jac(bg[a][k], bg[b][k])
                alt = max([jac(bg[a][k], bg[b][k + d]) for d in (-1, 1) if 0 <= k + d < n] or [0])
                alt2 = max([jac(bg[a][k + d], bg[b][k]) for d in (-1, 1) if 0 <= k + d < n] or [0])
                tot_pairs += 1
                if max(alt, alt2) > same + 0.03:
                    cross += 1
                    cross_units.add(units[k])
    r['cross_frac'] = round(cross / tot_pairs, 3) if tot_pairs else None
    r['cross_units'] = sorted(cross_units)[:12]
    # 整體相似
    docs = {v: bigrams(''.join(txt[v])) for v in zh}
    sims = [jac(docs[a], docs[b]) for i, a in enumerate(zh) for b in zh[i + 1:]]
    r['doc_sim'] = round(statistics.mean(sims), 3) if sims else None
    r['min_doc_sim'] = round(min(sims), 3) if sims else None
    # 句中切
    mid = tot_n = 0
    for v in zh:
        for t in txt[v]:
            if t:
                tot_n += 1
                if t[-1] not in END:
                    mid += 1
    r['midsent_frac'] = round(mid / tot_n, 3) if tot_n else None
    # 單本某節遠短／遠長（相對累積份額）
    odd = 0
    for v in zh:
        for k in range(n):
            others = [lens[o][k] / tot[o] for o in zh if o != v and tot[o]]
            if not others or not tot[v]:
                continue
            m = statistics.median(others)
            me = lens[v][k] / tot[v]
            if m > 0.05 and (me < m / 4 or me > m * 4):
                odd += 1
    r['odd_cells'] = odd
    # 非空重疊：各本之間「同一節兩本都有字」的比例（低＝各本內容落在不同節，沒對起來）
    ov = []
    allv = list(txt)
    for i, a in enumerate(allv):
        for b in allv[i + 1:]:
            either = sum(1 for k in range(n) if txt[a][k] or txt[b][k])
            both = sum(1 for k in range(n) if txt[a][k] and txt[b][k])
            ov.append(both / either if either else 0)
    zov = []
    for i, a in enumerate(zh):
        for b in zh[i + 1:]:
            either = sum(1 for k in range(n) if txt[a][k] or txt[b][k])
            both = sum(1 for k in range(n) if txt[a][k] and txt[b][k])
            zov.append(both / either if either else 0)
    r['zh_overlap_min'] = round(min(zov), 3) if zov else None
    r['overlap_min'] = round(min(ov), 3) if ov else None
    r['overlap_mean'] = round(statistics.mean(ov), 3) if ov else None
    # 巴利／原典本有字的節，有多少節至少一本漢譯也有字（0＝兩邊內容落在完全不同的節）
    pk = [k for k in range(n) if any(txt[v][k] for v in pi)]
    r['pali_cover'] = round(sum(1 for k in pk if any(txt[v][k] for v in zh)) / len(pk), 3) if pk else None
    zk = [k for k in range(n) if any(txt[v][k] for v in zh)]
    r['zh_cover'] = round(sum(1 for k in zk if any(txt[v][k] for v in pi)) / len(zk), 3) if zk else None
    # 傾倒：某本最大單格佔該本全文 >60%，其餘本卻是攤開的（＝整本塞進一兩節，其餘節留空）
    maxsh = {v: (max(lens[v]) / tot[v]) if tot[v] else 0 for v in lens}
    dumped = []
    if n >= 6:
        for v in lens:
            others = [maxsh[o] for o in lens if o != v and tot[o]]
            if tot[v] >= 600 and maxsh[v] > 0.6 and others and statistics.median(others) < 0.45:
                dumped.append(v)
    r['dumped_versions'] = dumped
    r['dump_frac'] = round(len(dumped) / len(vers), 3) if vers else 0
    r['max_cell_chars'] = max((max(l) for l in lens.values() if l), default=0)
    # 稀疏：某本只在不到 25% 的節有字，而另一本幾乎每節都有（n>=8）；常見於傾倒或只配到開頭
    nef = {v: sum(1 for t in txt[v] if t) / n for v in txt} if n else {}
    sparse = []
    if n >= 8:
        for v in nef:
            if nef[v] < 0.25 and max(nef[o] for o in nef if o != v) >= 0.8:
                sparse.append(v)
    r['sparse_versions'] = sparse
    # 可疑分數
    s = 0.0
    s += 2 if r['tiny_units'] else 0
    s += 3 * r['empty_frac']
    s += 4 * (r['cum_dev'] or 0)
    s += 2 * (r['pali_cum_dev'] or 0)
    s += 3 * (r['cross_frac'] or 0)
    s += 2 * max(0, 0.12 - (r['min_doc_sim'] if r['min_doc_sim'] is not None else 0.12)) / 0.12
    s += 1.5 * (r['midsent_frac'] or 0)
    s += 0.3 * min(odd, 6)
    s += 5 * r['dump_frac']
    s += 1.5 * len(r['sparse_versions']) / max(1, len(vers))
    s += 3 * (1 - (r['pali_cover'] if r['pali_cover'] is not None else 1))
    s += 3 * (1 - (r['overlap_mean'] if r['overlap_mean'] is not None else 1))
    r['score'] = round(s, 3)
    return r


# 人工抽查評等（2026-10-02，逐組讀各本節首節尾）：A 可用／B 小錯／C 大錯
MANUAL = {
    'C': 'sn2.30 an7.63 mn135 sn2.20 sn1.36 sn36.21 iti14 mn130 dn31 dn2 mn32 mn5 mn35 an6.58-mn2 mn13 dn26 mn46 dn18 sn42.8 mn104 mn41-mn42 dn22-mn10 iti24-sn15.10 sn42.5 sn1.32 mn33',
    'B': 'mn140 an8.9 mn61 dn28 mn18 an7.22 an8.42-an8.43 mn63 sn4.10 mn24 sn11.1 sn40.10 an3.70 sn24.8',
    'A': 'sn2.22 sn1.39 sn11.23 sn1.62 an7.67 an9.20 sn1.47 sn11.19 sn15.7 an7.69 dn25 an3.127 sn15.11 sn22.96 sn22.59 an4.7 an10.21 sn1.6 sn42.1 sn1.22 sn1.31 sn1.51 sn1.55 sn42.7 sn1.59 sn4.7 sn16.3 an7.61',
}


def flag(r):
    """機械旗標：C?＝建議撤下或改人工；B?＝需人工看；A?＝可放行。依 55+13 組人工評等校準。"""
    om = r['overlap_mean']
    if om is not None and om < 0.5 or (r['pali_cover'] is not None and r['pali_cover'] < 0.5):
        return 'C?'
    if (om is not None and om < 0.75) or r['dumped_versions'] or r['sparse_versions'] or (r['zh_overlap_min'] is not None and r['zh_overlap_min'] < 0.5):
        return 'B?'
    return 'A?'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--family', default='pi')
    ap.add_argument('--out', default=str(ROOT / 'output' / 'tripitaka_pali_auto_audit.json'))
    a = ap.parse_args()
    idx = json.loads((CMP / 'index.json').read_text(encoding='utf8'))
    sel = [x for x in idx if x['family'] == a.family and x.get('auto')]
    rows = []
    for x in sel:
        rows.append(audit(x['slug']))
        rows[-1]['labels'] = x['labels']
        rows[-1]['flag'] = flag(rows[-1])
        for gk, gv in MANUAL.items():
            if x['slug'][3:] in gv.split():
                rows[-1]['manual'] = gk
    rows.sort(key=lambda r: -r['score'])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({'count': len(rows), 'rows': rows}, ensure_ascii=False, indent=1), encoding='utf8')
    import collections
    print(f'{len(rows)} groups -> {a.out}')
    print('flags', dict(collections.Counter(r['flag'] for r in rows)))
    print('flag x manual', sorted(collections.Counter((r['flag'], r.get('manual', '-')) for r in rows).items()))
    for r in rows[:15]:
        print(r['score'], r['slug'], r['n_units'], r['n_versions'], r['cum_dev'], r['cross_frac'], r['min_doc_sim'])


if __name__ == '__main__':
    main()
