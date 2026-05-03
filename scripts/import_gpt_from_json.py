import json
import sys
import re
import requests
from datetime import datetime
from pathlib import Path

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

# HTML tag pattern: count <...> tags
TAG_PATTERN = r'<[^>]*>'

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

def has_too_many_tags(text):
    """Check if text has 3 or more <...> tags"""
    if not text:
        return False
    tags = re.findall(TAG_PATTERN, text)
    return len(tags) >= 3

def is_code_related(text):
    """Check if text is about programming"""
    if not text or len(text.strip()) < 12:
        return True

    # Check for thought keywords first
    for kw in THOUGHT_KEYWORDS:
        if kw in text:
            return False

    # Check for code patterns
    code_patterns = [
        r'\.vue\b', r'\.js\b', r'\.ts\b', r'\.py\b', r'\.css\b', r'\.html\b',
        r'npm run', r'git commit', r'git push', r'git add', r'git rebase',
        r'nodemon', r'vite\b', r'\bERROR:', r'SQLSTATE',
        r'import \{', r'const \{', r'<script', r'<template', r'<!DOCTYPE',
        r'function\s+\w+\s*\(', r'def\s+\w+\s*\(', r'class\s+\w+',
        r'SELECT\s+', r'UPDATE\s+', r'INSERT\s+', r'DELETE\s+FROM',
        r'\[plugin:vite', r'net::ERR_',
    ]

    for pat in code_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True

    return False

def parse_conversations():
    """Parse all JSON conversation files"""
    entries = []
    files_dir = Path('stores')

    for i in range(5):
        filepath = files_dir / f'conversations-{i:03d}.json'
        if not filepath.exists():
            print(f'❌ 檔案不存在: {filepath}')
            continue

        print(f'📄 讀取: {filepath}')
        with open(filepath, 'r', encoding='utf-8') as f:
            conversations = json.load(f)

        for conv in conversations:
            conv_id = conv.get('id', '')
            create_time = conv.get('create_time')
            mapping = conv.get('mapping', {})

            if not create_time:
                continue

            # Extract user-assistant pairs from mapping
            messages_by_id = {}
            for node_id, node in mapping.items():
                message = node.get('message')
                if message:
                    messages_by_id[node_id] = message

            # Build conversation tree by traversing children
            user_prompt = None
            assistant_response = None
            msg_time = None

            for node_id, message in messages_by_id.items():
                role = message.get('author', {}).get('role')
                content_parts = message.get('content', {}).get('parts', [])
                msg_text = ''.join(str(p) for p in content_parts if p)

                if role == 'user' and msg_text:
                    user_prompt = msg_text
                    msg_time = message.get('create_time') or create_time
                elif role == 'assistant' and msg_text and user_prompt:
                    assistant_response = msg_text
                    msg_time = message.get('create_time') or create_time

                    # Check filtering
                    if has_too_many_tags(user_prompt) or has_too_many_tags(assistant_response):
                        print(f'  🗑️ 刪除: 有3+個<>標籤')
                        user_prompt = None
                        assistant_response = None
                        continue

                    if is_code_related(user_prompt):
                        print(f'  🗑️ 刪除: 對話是寫程式')
                        user_prompt = None
                        assistant_response = None
                        continue

                    # Convert timestamp to datetime
                    dt = datetime.utcfromtimestamp(msg_time)
                    date_str = dt.strftime('%Y-%m-%d')
                    ts_str = dt.isoformat() + 'Z'

                    entries.append({
                        'dialogue_date': date_str,
                        'dialogue_time': ts_str,
                        'prompt': user_prompt[:4000],
                        'response': assistant_response[:8000] if assistant_response else None,
                    })

                    user_prompt = None
                    assistant_response = None

    return entries

def clear_old_data():
    """Clear old ChatGPT data from database"""
    print('\n🗑️ 清空舊的ChatGPT對話...')
    # Delete all from ai_dialogues_chatgpt with WHERE clause
    resp = requests.delete(
        f'{SUPABASE_URL}/rest/v1/ai_dialogues_chatgpt?id=gte.0',
        headers=HEADERS,
    )
    if resp.status_code not in (200, 204):
        print(f'  ⚠️ 警告: {resp.status_code} {resp.text[:100]}')
    else:
        print(f'  ✅ 已清空')

def batch_insert(rows, batch_size=200):
    """Insert rows in batches"""
    total = 0
    for start in range(0, len(rows), batch_size):
        chunk = rows[start:start+batch_size]
        resp = requests.post(
            f'{SUPABASE_URL}/rest/v1/ai_dialogues_chatgpt',
            headers=HEADERS,
            json=chunk,
        )
        if resp.status_code not in (200, 201):
            print(f'  ❌ ERROR {resp.status_code}: {resp.text[:200]}')
        else:
            total += len(chunk)
            print(f'  ✅ 已上傳 {start+len(chunk)} / {len(rows)}')
    return total

print('=' * 60)
print('ChatGPT 對話重新匯入')
print('=' * 60)

print('\n📖 解析JSON檔案...')
entries = parse_conversations()
print(f'\n總共: {len(entries)} 條對話')

if entries:
    # Sort by date/time
    entries.sort(key=lambda e: (e['dialogue_date'], e['dialogue_time']))
    print(f'日期範圍: {entries[0]["dialogue_date"]} ~ {entries[-1]["dialogue_date"]}')

    clear_old_data()

    print('\n📤 上傳到資料庫...')
    inserted = batch_insert(entries)
    print(f'\n✨ 完成: {inserted} 條對話已匯入')
else:
    print('\n❌ 沒有對話可以匯入')
