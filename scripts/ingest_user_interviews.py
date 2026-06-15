# Ingest the user's own oral-history interview transcripts (筆者訪問) as
# single-language zh fulltext under their research-review entries on
# yinshun-shengyan, so 研究回顧 shows them readable (single column).
#   136 林建德教授訪談記  ← 08.27 林建德教授口述訪談紀錄.txt
#   137 釋清德法師訪談記  ← 09.13 釋清德法師口述訪談紀錄.txt
import sys, re, json, requests
from pathlib import Path

PAIRS = [
    (136, 'public/content/interviews/08.27 林建德教授口述訪談紀錄.txt'),
    (137, 'public/content/interviews/09.13 釋清德法師口述訪談紀錄.txt'),
]
SLUG = 'yinshun-shengyan'
APPLY = '--apply' in sys.argv

env = {}
for line in open('.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')
U = env['SUPABASE_URL']; K = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}

FN = re.compile(r'\[(\d+)\]\(#footnote\d+\)')      # [194](#footnote194) → [194]


def paragraphs(text):
    text = text.replace('\r\n', '\n')
    out = []
    for blk in re.split(r'\n\s*\n', text):
        p = FN.sub(r'[\1]', blk).strip()
        if p:
            out.append(p)
    return out


for eid, path in PAIRS:
    paras = paragraphs(Path(path).read_text(encoding='utf-8'))
    print(f'entry {eid} ← {Path(path).name}: {len(paras)} paragraphs, '
          f'{sum(len(p) for p in paras):,} chars; head: {paras[0][:30]}')
    if not APPLY:
        continue
    payload = [{'entry_id': eid, 'version_code': 'zh', 'order_index': i,
                'text': p, 'char_count': len(p)} for i, p in enumerate(paras)]
    resp = requests.post(
        f'{U}/rest/v1/lit_review_sections?on_conflict=entry_id,version_code,order_index',
        headers={**H, 'Prefer': 'resolution=merge-duplicates,return=minimal'},
        data=json.dumps(payload), timeout=120)
    resp.raise_for_status()
    requests.patch(f'{U}/rest/v1/lit_review_entries?id=eq.{eid}',
                   headers={**H, 'Prefer': 'return=minimal'},
                   data=json.dumps({'fulltext_status': 'translated'}), timeout=30)
    print(f'  ✓ {len(payload)} zh sections under entry {eid}; status→translated')

print('\n(dry-run; pass --apply)' if not APPLY else '\nDone.')
