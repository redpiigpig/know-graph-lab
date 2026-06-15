# Move 印順/聖嚴 interview & comparison fulltext entries from
# mahaprajapati-revolution → yinshun-shengyan.
#
# Two operations:
#   MERGE: the same work already has a curated stub on yinshun-shengyan.
#          Re-point the fulltext sections to that stub, mark it translated,
#          copy fulltext_url, then delete the now-empty source entry.
#   MOVE:  no stub on yinshun-shengyan → just flip project_slug (keep theme/order).
#
# Run with --apply to execute; default is dry-run.
import sys, requests

env = {}
for line in open('.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')
URL = env['SUPABASE_URL']; KEY = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}
DST = 'yinshun-shengyan'

# source_entry_id -> dest_stub_entry_id (same work, merge fulltext into stub)
MERGE = {238: 133, 320: 147, 370: 182}
# source entries with no stub on dst → move project_slug + retheme into the
# paper's DOC-type reference groups (append at end via high display_order).
MOVE = {
    261: ('佛典與檔案', 500),          # 浮塵掠影：李志夫訪談錄
    269: ('佛典與檔案', 501),          # 臺灣佛教一甲子：吳老擇訪談錄
    356: ('佛典與檔案', 502),          # 杏壇衲履：恆清訪談錄
    294: ('專書著作', 510),            # 印順九秩華誕祝壽文集
    319: ('研討會與專書論文', 520),    # 林建德 如來藏對比（與 154 並列＝兩篇）
    422: ('研討會與專書論文', 521),    # 林建德 空性與佛性
    423: ('研討會與專書論文', 522),    # 王宣歷 聖嚴融合性
}

APPLY = '--apply' in sys.argv


def get(path, **params):
    r = requests.get(URL + '/rest/v1/' + path, params=params, headers=H)
    r.raise_for_status(); return r.json()


def secs_count(eid, vc='zh'):
    r = requests.get(URL + '/rest/v1/lit_review_sections',
                     params={'select': 'id', 'entry_id': 'eq.%d' % eid, 'version_code': 'eq.' + vc},
                     headers={**H, 'Prefer': 'count=exact', 'Range': '0-0'})
    cr = r.headers.get('content-range', '*/0'); return int(cr.split('/')[-1])


def entry(eid):
    rows = get('lit_review_entries', select='*', id='eq.%d' % eid)
    return rows[0] if rows else None


print('=== DRY-RUN ===' if not APPLY else '=== APPLYING ===')
print('\n-- MERGE (sections → existing stub, delete source) --')
for src, dst_id in MERGE.items():
    se, de = entry(src), entry(dst_id)
    print(f'src {src} "{se["title"][:30]}" ({secs_count(src)}段, {se["ref_key"]})')
    print(f'  → stub {dst_id} "{de["title"][:30]}" ({de["ref_key"]}, status={de["fulltext_status"]}, existing段={secs_count(dst_id)})')
    if APPLY:
        # re-point sections
        r = requests.patch(URL + '/rest/v1/lit_review_sections',
                           params={'entry_id': 'eq.%d' % src},
                           headers={**H, 'Prefer': 'return=minimal'},
                           json={'entry_id': dst_id})
        r.raise_for_status()
        # update stub
        r = requests.patch(URL + '/rest/v1/lit_review_entries',
                           params={'id': 'eq.%d' % dst_id},
                           headers={**H, 'Prefer': 'return=minimal'},
                           json={'fulltext_status': 'translated', 'fulltext_url': se.get('fulltext_url')})
        r.raise_for_status()
        # delete source
        r = requests.delete(URL + '/rest/v1/lit_review_entries',
                            params={'id': 'eq.%d' % src}, headers={**H, 'Prefer': 'return=minimal'})
        r.raise_for_status()
        print('  ✓ merged + deleted source')

print('\n-- MOVE (flip project_slug + retheme) --')
for src, (theme, do) in MOVE.items():
    se = entry(src)
    print(f'move {src} "{se["title"][:34]}" ({secs_count(src)}段) {se["theme"]}→{theme} do={do} → {DST}')
    if APPLY:
        r = requests.patch(URL + '/rest/v1/lit_review_entries',
                           params={'id': 'eq.%d' % src},
                           headers={**H, 'Prefer': 'return=minimal'},
                           json={'project_slug': DST, 'theme': theme, 'display_order': do})
        r.raise_for_status()
        print('  ✓ moved')

print('\nDone.' if APPLY else '\n(dry-run only; pass --apply to execute)')
