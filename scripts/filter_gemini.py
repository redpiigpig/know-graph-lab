import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

base = 'c:/Users/user/Desktop/know-graph-lab/stores/Gemini對話_by_date'
out  = 'c:/Users/user/Desktop/know-graph-lab/stores/Gemini對話_filtered'
os.makedirs(out, exist_ok=True)

CODE_SIGNALS = [
    r'npm run', r'git commit', r'git push', r'git add', r'git rebase',
    r'nodemon', r'vite\b', r'SQLSTATE',
    r'給我全部的code', r'完整的code', r'直接幫我改', r'按照原本.*改', r'按照原檔',
    r'import \{', r'const \{',
    r'function\s+\w+\s*\(',
    r'PS C:\\', r'C:\\Users\\.*>',
    r'config\.js:\d+',
    r'SELECT\s+\w', r'UPDATE\s+\w', r'INSERT\s+INTO', r'DELETE\s+FROM',
    r'\[plugin:vite', r'net::ERR_',
    r'\.vue\b', r'\.ts\b', r'\.css\b',
]

def is_code_entry(prompt_text):
    # 3+ HTML/template tags = clearly code
    tag_count = len(re.findall(r'<[a-zA-Z][^>]{0,80}>', prompt_text))
    if tag_count >= 3:
        return True

    for pattern in CODE_SIGNALS:
        if re.search(pattern, prompt_text, re.IGNORECASE):
            return True

    # Attachment with no real text = image/file dump
    if re.search(r'Attached \d+ file', prompt_text, re.IGNORECASE):
        stripped = re.sub(r'Attached \d+ files?\..*', '', prompt_text, flags=re.IGNORECASE|re.DOTALL)
        stripped = re.sub(r'-\s+\S+\n', '', stripped)
        if len(re.sub(r'\s+', '', stripped)) < 15:
            return True

    if len(re.sub(r'\s+', '', prompt_text)) < 12:
        return True

    return False

total_kept = 0
total_removed = 0

for fname in sorted(os.listdir(base)):
    if not fname.endswith('.txt'):
        continue
    date = fname.replace('.txt', '')
    path = os.path.join(base, fname)

    with open(path, encoding='utf-8') as f:
        content = f.read()

    raw_entries = re.split(r'(--- \[\d+\] ---\n)', content)

    kept = []
    removed = 0

    i = 0
    while i < len(raw_entries):
        seg = raw_entries[i]
        if re.match(r'--- \[\d+\] ---\n', seg):
            body = raw_entries[i+1] if i+1 < len(raw_entries) else ''
            i += 2
            pm = re.search(r'Prompted\s+(.*?)(?=\d{4}年\d{1,2}月\d{1,2}日|\Z)', body, re.DOTALL)
            if pm:
                prompt_text = pm.group(1)
                if is_code_entry(prompt_text):
                    removed += 1
                else:
                    kept.append(seg + body)
            else:
                kept.append(seg + body)
        else:
            i += 1

    total_kept += len(kept)
    total_removed += removed

    out_path = os.path.join(out, fname)
    if kept:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('# {}  （保留 {} 筆 / 移除 {} 筆）\n\n'.format(date, len(kept), removed))
            for j, e in enumerate(kept, 1):
                e_renumbered = re.sub(r'--- \[\d+\] ---', '--- [{}] ---'.format(j), e, count=1)
                f.write(e_renumbered)

    print('{}: 保留 {}, 移除 {}'.format(date, len(kept), removed))

print('\n總計：保留 {} 筆，移除 {} 筆'.format(total_kept, total_removed))
print('輸出至：{}'.format(out))
