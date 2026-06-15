# Copy 印順學派 / 法鼓 / 史料 / 知識化(CBETA・全集・大專學佛) bibliography entries
# from mahaprajapati-revolution → yinshun-shengyan (NON-destructive copy; the
# 大愛道 originals stay). Sections (if any) are copied too. Idempotent: skips a
# ref_key that already exists on yinshun-shengyan.
import sys, json, requests

DST = 'yinshun-shengyan'
APPLY = '--apply' in sys.argv

# source mahaprajapati entry ids, in the order they should appear (themes stay,
# display_order assigned sequentially from 600 so they form new groups at the end)
SRC_IDS = [
    # 人間佛教思想與印順學脈絡
    185, 186, 187, 220, 221, 222, 223, 439, 440, 441,
    # 法鼓山與聖嚴法師人間佛教
    237, 459, 460,
    # 史料與當代台灣佛教脈絡
    199, 200, 456, 457,
    # 佛教知識化、高教與電子佛典（CBETA・全集・大專學佛）
    465, 466, 467, 468, 469, 470, 471,
]
COPY_COLS = ['ref_key', 'authors', 'title', 'venue', 'year', 'language',
             'theme', 'dimension', 'stance', 'abstract_zh', 'fulltext_url',
             'fulltext_status']

env = {}
for line in open('.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')
U = env['SUPABASE_URL']; K = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}


def get(path, **p):
    r = requests.get(U + '/rest/v1/' + path, params=p, headers=H); r.raise_for_status(); return r.json()


existing = {e['ref_key'] for e in get('lit_review_entries', select='ref_key', project_slug='eq.' + DST)}
do = 600
created = skipped = secs_copied = 0
for sid in SRC_IDS:
    src = get('lit_review_entries', select='*', id='eq.%d' % sid)[0]
    tag = f'{sid} [{src["theme"][:14]}] {(src["authors"] or "")[:14]} | {src["title"][:34]}'
    if src['ref_key'] in existing:
        print('skip (already on dst):', tag); skipped += 1; continue
    sec = get('lit_review_sections', select='order_index,text,char_count',
              entry_id='eq.%d' % sid, version_code='eq.zh')
    print(f'copy do={do} {tag}  ({len(sec)} 段)')
    if APPLY:
        row = {c: src.get(c) for c in COPY_COLS}
        row['project_slug'] = DST; row['display_order'] = do
        r = requests.post(U + '/rest/v1/lit_review_entries',
                          headers={**H, 'Prefer': 'return=representation'}, json=row)
        r.raise_for_status(); nid = r.json()[0]['id']
        if sec:
            payload = [{'entry_id': nid, 'version_code': 'zh', 'order_index': s['order_index'],
                        'text': s['text'], 'char_count': s['char_count']} for s in sec]
            rr = requests.post(U + '/rest/v1/lit_review_sections?on_conflict=entry_id,version_code,order_index',
                              headers={**H, 'Prefer': 'resolution=merge-duplicates,return=minimal'},
                              data=json.dumps(payload)); rr.raise_for_status()
            secs_copied += len(payload)
        created += 1
    do += 1

print(f'\n{"APPLIED" if APPLY else "DRY-RUN"}: would-create={created if APPLY else (len(SRC_IDS)-skipped)} '
      f'skipped={skipped} sections_copied={secs_copied}')
if not APPLY:
    print('(pass --apply to execute)')
