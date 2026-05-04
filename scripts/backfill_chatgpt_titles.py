"""
Backfill title / conversation_id / project_id on ai_dialogues_chatgpt
from stores/conversations-*.json. Idempotent: only touches rows where
title IS NULL.

Match key: (dialogue_date, LEFT(prompt, 200)).
Mimics the (user, assistant) walk in import_gpt_from_json.py exactly so
prompt prefixes match what was inserted.
"""
import json
import sys
import requests
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent

def _load_env():
    env = {}
    with open(ROOT / '.env', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

_ENV = _load_env()
SUPABASE_URL = _ENV['SUPABASE_URL']
SERVICE_KEY  = _ENV['SUPABASE_SERVICE_ROLE_KEY']
ACCESS_TOKEN = _ENV['SUPABASE_ACCESS_TOKEN']
PROJECT_REF  = SUPABASE_URL.replace('https://', '').split('.')[0]

REST_HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
}

KEY_LEN = 200  # chars from prompt used as composite-key suffix

def run_sql(sql: str):
    url = f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query'
    resp = requests.post(url, json={'query': sql}, headers={
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    })
    if resp.status_code not in (200, 201):
        raise SystemExit(f'SQL failed {resp.status_code}: {resp.text}')
    try:
        return resp.json()
    except Exception:
        return []


def parse_json_meta():
    """Yield (date_str, prompt_prefix, title, conv_id, project_id) for every
    user→assistant pair in conversations-*.json, mirroring import_gpt_from_json.py."""
    files_dir = ROOT / 'stores'
    for i in range(5):
        fp = files_dir / f'conversations-{i:03d}.json'
        if not fp.exists():
            print(f'  (skip missing {fp.name})')
            continue
        print(f'  reading {fp.name}')
        with open(fp, 'r', encoding='utf-8') as f:
            convs = json.load(f)

        for conv in convs:
            create_time = conv.get('create_time')
            if not create_time:
                continue
            mapping = conv.get('mapping', {})
            title = conv.get('title') or '(無標題)'
            cid = conv.get('conversation_id') or conv.get('id')
            pid = conv.get('conversation_template_id')

            messages_by_id = {}
            for nid, node in mapping.items():
                m = node.get('message')
                if m:
                    messages_by_id[nid] = m

            user_prompt = None
            for nid, m in messages_by_id.items():
                role = m.get('author', {}).get('role')
                parts = m.get('content', {}).get('parts', [])
                text = ''.join(str(p) for p in parts if p)
                if role == 'user' and text:
                    user_prompt = text
                elif role == 'assistant' and text and user_prompt:
                    msg_time = m.get('create_time') or create_time
                    dt = datetime.utcfromtimestamp(msg_time)
                    date_str = dt.strftime('%Y-%m-%d')
                    yield (date_str, user_prompt[:KEY_LEN], title, cid, pid)
                    user_prompt = None


def sql_lit(s):
    if s is None:
        return 'NULL'
    return "'" + s.replace("'", "''") + "'"


def main():
    print('=' * 60)
    print('Backfill ChatGPT titles')
    print('=' * 60)

    print('\n1. Parsing JSON files...')
    meta_map = {}
    dup_skipped = 0
    for date_str, prefix, title, cid, pid in parse_json_meta():
        key = f'{date_str}|{prefix}'
        if key in meta_map and meta_map[key][0] != title:
            dup_skipped += 1
        meta_map[key] = (title, cid, pid)
    print(f'  parsed {len(meta_map)} unique (date, prompt[:{KEY_LEN}]) keys '
          f'({dup_skipped} duplicate keys with conflicting titles, last wins)')

    print('\n2. Fetching DB rows where title IS NULL...')
    rows = run_sql(
        f"SELECT id::text, dialogue_date::text AS d, "
        f"LEFT(prompt, {KEY_LEN}) AS h "
        f"FROM ai_dialogues_chatgpt WHERE title IS NULL"
    )
    print(f'  fetched {len(rows)} candidate rows')

    print('\n3. Matching...')
    matched = []
    for r in rows:
        key = f"{r['d']}|{r['h']}"
        m = meta_map.get(key)
        if m:
            matched.append((r['id'], *m))
    print(f'  matched {len(matched)} / {len(rows)}')

    if not matched:
        print('  nothing to update')
        return

    print('\n4. Batch UPDATE via VALUES join...')
    BATCH = 300
    total = 0
    for start in range(0, len(matched), BATCH):
        chunk = matched[start:start + BATCH]
        values = ',\n      '.join(
            f"({sql_lit(rid)}::uuid, {sql_lit(t)}, {sql_lit(c)}, {sql_lit(p)})"
            for (rid, t, c, p) in chunk
        )
        sql = f"""
UPDATE ai_dialogues_chatgpt AS d
SET title = v.t,
    conversation_id = v.c,
    project_id = v.p
FROM (VALUES
      {values}
) AS v(id, t, c, p)
WHERE d.id = v.id;
"""
        run_sql(sql)
        total += len(chunk)
        print(f'  updated {total} / {len(matched)}')

    print('\n5. Verifying...')
    summary = run_sql(
        "SELECT COUNT(*) FILTER (WHERE title IS NOT NULL) AS with_title, "
        "COUNT(*) AS total FROM ai_dialogues_chatgpt"
    )
    print(f'  {summary}')

    proj_summary = run_sql(
        "SELECT project_id, COUNT(*) FROM ai_dialogues_chatgpt "
        "WHERE project_id IS NOT NULL GROUP BY project_id ORDER BY 2 DESC"
    )
    print('\n  rows per project:')
    for r in proj_summary:
        print(f"    {r['count']:>5}  {r['project_id']}")


if __name__ == '__main__':
    main()
