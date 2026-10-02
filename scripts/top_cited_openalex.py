"""依 OpenAlex 引用數抓某領域「被引用最多的 N 篇期刊論文」，並把開放取用的 PDF 直接下載。

與 top_papers_build.py（研究史策展清單）互補：那邊是人選的「改變了怎麼問問題」，
這邊是引用數排行，只收期刊論文。使用者 2026-10-02：「我要你下載的是引用前五百的論文，不只是書目。」

  python -X utf8 scripts/top_cited_openalex.py historiography            # 抓清單
  python -X utf8 scripts/top_cited_openalex.py historiography --fetch "G:/…/期刊論文"   # 下載 OA PDF

設定檔 data/research-data/<field>/top-cited.config.json：
  {"total": 500, "pools": [{"name": "環境史", "concept": "C197099058", "quota": 100}, …]}
  pool 也可以用 "search" 取代 "concept"（另加 "within": 概念 ID 限縮）；"sources": [期刊 ID…] 限定期刊，
  可與 concept（"C1|C2" 表示或）並用。
🚨 只靠 concept 會被 OpenAlex 的自動標籤帶偏（「深度歷史」抓到天文學、「環境史」抓到動物園生物學，
   而 Chakrabarty、Cronon 的經典反而漏掉）——先鎖領域期刊，綜合期刊再加 concept 限縮。

🚨 OpenAlex 的 type=article 混著大量書評（JSTOR 給書評也發 DOI，引用數是那本書的），
   所以要濾：頁數 ≥ 5，或頁數不明但有摘要；標題以 "Review"、"Book Review" 開頭的直接丟。
產物：
  public/content/research-data/<field>/top-cited.json      清單（進版控）
  output/top-papers/<field>-top-cited-doi.json             給 doi_browser_fetch.mjs 的 DOI 清單（校內用）
"""
import json, re, sys, time, pathlib, argparse
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://api.openalex.org/works'
MAILTO = 'know-graph-lab@users.noreply.github.com'
SELECT = 'id,doi,title,publication_year,cited_by_count,authorships,primary_location,biblio,open_access,abstract_inverted_index,type,best_oa_location,locations'


def pages(w):
    b = w.get('biblio') or {}
    try:
        return int(b.get('last_page')) - int(b.get('first_page')) + 1
    except (TypeError, ValueError):
        return None


def looks_like_article(w):
    t = (w.get('title') or '').strip()
    if not t or re.match(r'(book )?reviews?\b|review of\b', t, re.I):
        return False
    src = ((w.get('primary_location') or {}).get('source') or {})
    if src.get('type') not in (None, 'journal'):
        return False
    n = pages(w)
    if n is not None:
        return n >= 5
    return bool(w.get('abstract_inverted_index'))


def fetch_pool(pool, want):
    flt = ['type:article']
    if pool.get('concept'):
        flt.append('concepts.id:' + pool['concept'])
    if pool.get('sources'):
        flt.append('primary_location.source.id:' + '|'.join(pool['sources']))
    if pool.get('within'):
        flt.append('concepts.id:' + pool['within'])
    params = {'filter': ','.join(flt), 'sort': 'cited_by_count:desc', 'per-page': 200,
              'select': SELECT, 'mailto': MAILTO, 'cursor': '*'}
    if pool.get('search'):
        params['search'] = pool['search']
    got, scanned = [], 0
    while len(got) < want and scanned < want * 6:
        r = requests.get(API, params=params, timeout=60)
        r.raise_for_status()
        j = r.json()
        res = j.get('results') or []
        if not res:
            break
        for w in res:
            scanned += 1
            if looks_like_article(w):
                got.append(w)
        params['cursor'] = j['meta'].get('next_cursor')
        if not params['cursor']:
            break
        time.sleep(0.2)
    print(f"  {pool['name']}: 掃 {scanned} 筆，留 {len(got)} 篇")
    return got


def row(w, pool):
    src = ((w.get('primary_location') or {}).get('source') or {})
    b = w.get('biblio') or {}
    au = [a['author']['display_name'] for a in (w.get('authorships') or []) if a.get('author')]
    oa = w.get('open_access') or {}
    return {
        'pool': pool, 'cited': w.get('cited_by_count', 0), 'year': w.get('publication_year'),
        'author': ', '.join(au[:3]) + (' et al.' if len(au) > 3 else ''),
        'title': w.get('title'), 'journal': src.get('display_name'),
        'volume': b.get('volume'), 'issue': b.get('issue'),
        'pages': f"{b.get('first_page') or ''}–{b.get('last_page') or ''}".strip('–'),
        'doi': (w.get('doi') or '').replace('https://doi.org/', '') or None,
        'openalex': w.get('id'), 'oa_url': oa.get('oa_url') if oa.get('is_oa') else None,
        # oa_url 常是落地頁；各收錄位置的 pdf_url 才是直連，下載時依序試
        'pdf_urls': list(dict.fromkeys(u for u in
            [((w.get('best_oa_location') or {}).get('pdf_url'))] +
            [l.get('pdf_url') for l in (w.get('locations') or [])] if u)),
    }


def build(field):
    cfg = json.loads((ROOT / 'data/research-data' / field / 'top-cited.config.json').read_text(encoding='utf8'))
    seen, rows = set(), []
    for p in cfg['pools']:
        n = 0
        for w in fetch_pool(p, p['quota'] * 2):
            if w['id'] in seen:
                continue
            seen.add(w['id'])
            rows.append(row(w, p['name']))
            n += 1
            if n >= p['quota']:
                break
        print(f"    → 去重後收 {n}／{p['quota']}")
    rows.sort(key=lambda r: -r['cited'])
    rows = rows[:cfg['total']]
    out = ROOT / 'public/content/research-data' / field / 'top-cited.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'field': field, 'n': len(rows), 'items': rows}, ensure_ascii=False, indent=1), encoding='utf8')
    doi = [{'doi': r['doi'], 'year': r['year'] or 0, 'author': r['author'] or '?', 'title': r['title'],
            'type': 'article', 'container': r['journal']} for r in rows if r['doi'] and not r['oa_url']]
    dp = ROOT / 'output/top-papers' / f'{field}-top-cited-doi.json'
    dp.parent.mkdir(parents=True, exist_ok=True)
    dp.write_text(json.dumps(doi, ensure_ascii=False, indent=1), encoding='utf8')
    print(f"共 {len(rows)} 篇；開放取用 {sum(1 for r in rows if r['oa_url'])}；非 OA 有 DOI {len(doi)}；無 DOI {sum(1 for r in rows if not r['doi'])}")
    print(f"清單 {out}\nDOI 清單 {dp}")


def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]+', ' ', s or '').strip()[:90]


def fetch(field, outdir):
    data = json.loads((ROOT / 'public/content/research-data' / field / 'top-cited.json').read_text(encoding='utf8'))
    od = pathlib.Path(outdir)
    od.mkdir(parents=True, exist_ok=True)
    ok = skip = bad = 0
    for r in data['items']:
        urls = (r.get('pdf_urls') or []) + ([r['oa_url']] if r['oa_url'] else [])
        if not urls:
            continue
        sur = (r['author'] or '?').split(',')[0].split()[-1]
        dest = od / f"{r['year']}_{safe(sur)}_{safe(r['title'])}.pdf"
        if dest.exists():
            skip += 1
            continue
        got = False
        for u in urls:
            try:
                resp = requests.get(u, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
                if resp.ok and resp.content[:4] == b'%PDF':
                    dest.write_bytes(resp.content)
                    got = True
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        ok += got
        bad += not got
    print(f"下載 {ok}、已有 {skip}、非 PDF 或失敗 {bad}（失敗的多半是落地頁，留給校內瀏覽器那條）")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('field')
    ap.add_argument('--fetch', metavar='OUTDIR')
    a = ap.parse_args()
    fetch(a.field, a.fetch) if a.fetch else build(a.field)
