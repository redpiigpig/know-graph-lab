# Ingest 廖憶榕（釋德晟）《學問僧的生命書寫──印順法師與聖嚴法師自傳之研究》
# (中正大學 2017 博論, clean text layer) as single-language zh fulltext under the
# existing yinshun-shengyan stub entry 176 (ref_key zhd13132b3-2017).
# One section per PDF page → research-review reader shows it single-column.
import sys, json, re, requests, fitz

PDF = '學問僧的生命書寫.pdf'
REF = 'zhd13132b3-2017'
SLUG = 'yinshun-shengyan'
APPLY = '--apply' in sys.argv

env = {}
for line in open('.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')
U = env['SUPABASE_URL']; K = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}


def norm(t):
    # join hard-wrapped lines into flowing prose; collapse runs of blank lines
    t = t.replace('\r\n', '\n')
    # drop a bare running-header / lone page-number line
    lines = [ln.rstrip() for ln in t.split('\n')]
    lines = [ln for ln in lines if ln.strip()]
    return '\n'.join(lines).strip()


doc = fitz.open(PDF)
rows = []
for i in range(doc.page_count):
    t = norm(doc[i].get_text())
    if len(t) < 8:            # blank / image-only page
        continue
    rows.append({'oi': i + 1, 'text': t, 'n': len(t)})

print(f'{doc.page_count} pages → {len(rows)} non-empty sections, '
      f'{sum(r["n"] for r in rows):,} chars')
print('first section preview:')
print(' ', rows[0]['text'][:120].replace('\n', ' / '))

if not APPLY:
    print('\n(dry-run; pass --apply to ingest)')
    sys.exit()

eid = requests.get(f'{U}/rest/v1/lit_review_entries',
                   params={'project_slug': 'eq.' + SLUG, 'ref_key': 'eq.' + REF, 'select': 'id'},
                   headers=H).json()[0]['id']
payload = [{'entry_id': eid, 'version_code': 'zh', 'order_index': r['oi'],
            'text': r['text'], 'char_count': r['n']} for r in rows]
# upsert in batches (avoid oversized request)
for b in range(0, len(payload), 100):
    chunk = payload[b:b + 100]
    resp = requests.post(
        f'{U}/rest/v1/lit_review_sections?on_conflict=entry_id,version_code,order_index',
        headers={**H, 'Prefer': 'resolution=merge-duplicates,return=minimal'},
        data=json.dumps(chunk), timeout=120)
    resp.raise_for_status()
    print(f'  upserted {b + len(chunk)}/{len(payload)}')
requests.patch(f'{U}/rest/v1/lit_review_entries?id=eq.{eid}',
               headers={**H, 'Prefer': 'return=minimal'},
               data=json.dumps({'fulltext_status': 'translated'}), timeout=30)
print(f'✓ entry {eid} ({REF}) ← {len(payload)} zh sections; status→translated')
