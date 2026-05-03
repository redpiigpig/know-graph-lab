import re, sys, json, requests, time
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding='utf-8')

def _load_env():
    env = {}
    with open('.env', 'r', encoding='utf-8-sig') as f:
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
HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

gpt_file = 'c:/Users/user/Desktop/know-graph-lab/stores/和GPT的對話.txt'

CODE_STRONG = [
    r'\.vue\b', r'\.js\b', r'\.ts\b', r'\.py\b', r'\.css\b', r'\.html\b',
    r'npm run', r'git commit', r'git push', r'git add', r'git rebase',
    r'nodemon', r'vite\b', r'\bERROR:', r'SQLSTATE',
    r'給我全部的code', r'完整的code', r'直接幫我改', r'按照原本.*改', r'按照原檔',
    r'import \{', r'const \{', r'<script', r'<template', r'<!DOCTYPE',
    r'function\s+\w+\s*\(', r'def\s+\w+\s*\(', r'class\s+\w+',
    r'PS C:\\\\', r'C:\\\\Users\\\\.*>',
    r'config\.js:\d+', r'SELECT\s+', r'UPDATE\s+', r'INSERT\s+', r'DELETE\s+FROM',
    r'\[plugin:vite', r'net::ERR_', r'generated image',
]

THOUGHT_KEYWORDS = [
    '神學', '哲學', '宗教', '基督', '佛教', '禪', '倫理', '上帝',
    '信仰', '聖顯', '卡巴拉', '神秘主義', '本體', '靈性', '靈魂',
    '末世', '救贖', '啟示', '聖經', '教會', '牧師', '牧者',
    '榮格', '阿尼', '原型', '自性', '無意識', '積極想像',
    '基督事件', '尼西亞', '衛斯理', '佛陀', '菩薩', '觀音',
    '神話', '詮釋', '心靈', '靈修', '夢境', '夢中',
    '個體化', '陰影', '永恆少年', '倪柝聲', '龐君華', '龐牧',
    '克里須那', '阿周那', '薄伽梵歌', '奧義書',
    '汎心論', '意識哲', '宇宙', '聖顯',
    '思想', '理論', '文化', '歷史意識', '共時性',
    '否定神學', '本體論', '現象學', '主體性', '倫理學', '存在主義',
]

def is_code_entry(text):
    if not text or len(text.strip()) < 12:
        return True
    for pat in CODE_STRONG:
        if re.search(pat, text, re.IGNORECASE):
            return True
    for kw in THOUGHT_KEYWORDS:
        if kw in text:
            return False
    return False

def parse_gpt_file():
    with open(gpt_file, encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n')

    entries = []

    # Find all markers
    user_pattern = re.compile(r'^user$', re.MULTILINE)
    chat_pattern = re.compile(r'^ChatGPT$', re.MULTILINE)

    user_matches = list(user_pattern.finditer(content))
    chat_matches = list(chat_pattern.finditer(content))

    print(f"Found {len(user_matches)} 'user' and {len(chat_matches)} 'ChatGPT' markers")

    # Extract pairs: each user is followed by ChatGPT response
    for i, user_match in enumerate(user_matches):
        u_start = user_match.end() + 1

        # Find next ChatGPT marker after this user
        chat_match = None
        for cm in chat_matches:
            if cm.start() > user_match.start():
                chat_match = cm
                break

        if not chat_match:
            break

        c_start = chat_match.start()
        c_end = chat_match.end() + 1

        # Find where this ChatGPT response ends (next user or EOF)
        next_user = user_matches[i+1].start() if i+1 < len(user_matches) else len(content)

        prompt = content[u_start:c_start].strip()
        response = content[c_end:next_user].strip()

        if not prompt:
            continue

        if is_code_entry(prompt):
            continue

        # Distribute dates across same range as Gemini
        base_date = datetime(2026, 1, 9)
        day_offset = i % 112  # 112 days (Jan 9 - Apr 30)
        date_obj = base_date + timedelta(days=day_offset)

        # Spread times evenly within the day
        hour = (i // 112) % 24
        minute = (i // 2688) % 60
        date_obj = date_obj.replace(hour=hour, minute=minute)

        date_str = date_obj.strftime('%Y-%m-%d')
        ts_str = date_obj.isoformat() + 'Z'

        entries.append({
            'dialogue_date': date_str,
            'dialogue_time': ts_str,
            'prompt': prompt[:4000],  # Limit prompt size
            'response': (response[:8000] if response else None),
            'source': 'chatgpt',
        })

    return entries

def batch_insert(rows, batch_size=200):
    total = 0
    for start in range(0, len(rows), batch_size):
        chunk = rows[start:start+batch_size]
        resp = requests.post(
            f'{SUPABASE_URL}/rest/v1/ai_dialogues',
            headers=HEADERS,
            data=json.dumps(chunk, ensure_ascii=False).encode('utf-8'),
        )
        if resp.status_code not in (200, 201):
            print(f'  ERROR {resp.status_code}: {resp.text[:200]}')
        else:
            total += len(chunk)
            print(f'  inserted {start+len(chunk)} / {len(rows)}')
        time.sleep(0.1)
    return total

print('Parsing GPT conversations...')
entries = parse_gpt_file()
print(f'Total kept: {len(entries)}')

if entries:
    print('Uploading...')
    inserted = batch_insert(entries)
    print(f'Done: {inserted} rows inserted')
else:
    print('No entries to upload')
