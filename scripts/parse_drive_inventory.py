#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse drive_inventory.json into drive_parsed.json.

Pipeline:
1. Strip extension
2. Handle special series prefixes (經典與解釋, 中國傳統-經典與解釋)
3. Handle "Complete/Collected Works of X" pattern (English)
4. Handle z-lib pattern with possible nested parens
5. Split on first 全形 comma -> (author, rest)
6. Remove subtitle (split on ：) BUT only if no other file in the same parent
   would collide with the stripped title
7. Convert simplified -> traditional via opencc s2tw
8. Apply manual author overrides for known series/categories
"""
import json
import re
import os
import sys
from collections import defaultdict

CC = None
try:
    import opencc
    CC = opencc.OpenCC('s2tw')
except ImportError:
    print("Installing opencc...", file=sys.stderr)
    os.system("pip install opencc -q")
    try:
        import opencc
        CC = opencc.OpenCC('s2tw')
    except ImportError:
        print("opencc still unavailable - skipping conversion", file=sys.stderr)

MAIN_CATEGORIES = {
    '1Zeidt80yacXeoArjUNo4uMwZ7hiTcPLs': '哲學',
    '1-AkNSet1Qd6MlJxKbRDgFqPIyxQ-QMmd': '世界宗教',
    '1ZYxohucqf07UdfG2H3ThsH-j6qDvtCwk': '宗教學',
    '1ACDWel0ccmpN_UAo_WfJEcs6D1qoCwni': '人類生物學',
    '1a0RTlewpuU4avZxJguh4GnfYiACFQY_9': '心理學',
    '1hyZCPQxP60_SgkfFHvzBOUPB1-hMKbRa': '文學',
    '1tMcY0jIVe3710sQYQR_T6c63wET4xpU2': '自然科學',
    '1E1O3HLqluz_wthGk6ZqBglqFCFxmaOn0': '歷史學',
    '1Im1akp1q3QNO3dNby_tUWqdUVf4v-sO5': '社會政治學',
}

# Manual author overrides for titles where author cannot be parsed.
# Substring match against original_title — be specific to avoid false matches.
# Order matters — first match wins, so put more specific patterns earlier.
TITLE_AUTHOR_OVERRIDES = [
    # Personal collected works
    ('印順法師佛學著作全集', '釋印順'),
    ('三毛典藏全集', '三毛'),
    ('鹽野七生作品集', '鹽野七生'),
    ('周國平尼采譯著系列', '周國平'),
    # Bahai writings
    ('巴哈伊禱文', '巴哈歐拉'),
    ('巴哈伊教育箴言', '巴哈歐拉'),
    ('巴哈伊齋戒', '巴哈歐拉'),
    ('巴哈歐拉書簡集', '巴哈歐拉'),
    ('阿博都‧巴哈遺囑', '阿博都‧巴哈'),
    ('阿博都‧巴哈文選', '阿博都‧巴哈'),
    ('追求靈性─巴哈伊經典選編', '巴哈歐拉'),
    ('義務祈禱與齋戒之重要性', '巴哈歐拉'),
    # Ancient/anonymous texts
    ('Septuagint- The Old Testament in Greek', '七十士譯本'),
    ('盎格鲁-撒克遜编年史', '匿名'),
    ('死海古卷', '匿名'),
    ('使徒教父著作', '使徒教父'),
    ('阿维斯塔', '瑣羅亞斯德'),
    ('摩訶婆羅多', '黃寶生'),  # 黃寶生 譯本 (most common Chinese version)
    ('博伽梵歌', '黃寶生'),
    ('荷馬史詩', '荷馬'),
    # Major series — chief editor / primary author
    ('西洋哲學史', '柯普斯登'),  # Frederick Copleston, 黎明文化 7-vol series
    ('世界宗教史', '任繼愈'),  # 任繼愈 主編
    ('世界文明大系', '汝信'),  # 汝信 主編
    ('伊斯蘭文明', '馬歇爾·哈濟生'),  # Marshall Hodgson, The Venture of Islam
    ('中亞文明史', '聯合國教科文組織'),  # UNESCO commissioned
    # 經典與解釋 series — chief editor 劉小楓
    ('經典與解釋', '劉小楓'),
    ('尼采與古典傳統', '劉小楓'),  # 經典與解釋 series book (parser strips prefix so add separately)
    ('基督教典外文獻', '王曉朝'),  # series edited by 王曉朝
    ('劍橋插圖羅馬史', '科內爾'),
    ('劍橋插圖中世纪史', '麥基特里克'),
    ('劍橋插圖中世紀史', '麥基特里克'),
    # Author-as-title-subject overrides
    ('奧古斯丁：駁朱利安', '奧古斯丁'),
    ('西塞羅散文選', '西塞羅'),
    ('陀思妥耶夫斯基全集', '陀思妥耶夫斯基'),
    ('甘地自傳', '甘地'),
    ('費爾巴哈哲學著作選集', '費爾巴哈'),
    ('摩訶婆羅多的故事', '黃寶生'),
    ('蒋维乔中国佛教史', '蔣維喬'),
    ('蔣維喬中國佛教史', '蔣維喬'),
    ('王明珂', '王明珂'),  # multiple books matching this string contain author in parens
    ('翦商', '李碩'),
    ('路德和加爾文論世俗權威', '馬丁路德'),
    # Anthology / 編 attributions
    ('商務印書館漢譯歷史套裝', '商務印書館'),
    ('新約聖經背景註釋', '基納'),  # Craig Keener
    ('舊約聖經背景註釋', '華爾頓'),  # John Walton
    # Specific lookup-confirmed
    ('托爾斯泰與陀思妥耶夫斯基', '梅列日科夫斯基'),
    ('古代中國與其強鄰', '狄宇宙'),
    ('中國中古時代的禮儀、宗教與制度', '高明士'),
    ('東方神話傳說', '馬昌儀'),
    ('世界近代史', '朱寰'),
    ('東南亞的歷史與宗教', '賀聖達'),
    ('赫耳墨斯秘籍', '赫耳墨斯·特里斯墨吉斯忒斯'),
    ('次經全書', '張久宣'),  # 譯
    ('德魯伊教簡介', 'Philip Carr-Gomm'),
    # Common 摩門教 — handled by subcategory check
]


# Post-fix table for known opencc s2tw false positives.
# s2tw incorrectly converts simplified 历 to 曆 (calendar) where it should be 歷 (past/history).
# These are substring substitutions applied AFTER s2tw conversion.
TRAD_FIXES = [
    ('曆史', '歷史'),
    ('經曆', '經歷'),
    ('來曆', '來歷'),
    ('學曆', '學歷'),
    ('履曆', '履歷'),
    ('簡曆', '簡歷'),
    ('病曆', '病歷'),
    ('閱曆', '閱歷'),
    ('資曆', '資歷'),
    ('遊曆', '遊歷'),
    ('遍曆', '遍歷'),
    ('曆險', '歷險'),
    ('曆程', '歷程'),
    ('曆代', '歷代'),
    ('曆年', '歷年'),
    ('心路曆程', '心路歷程'),
    ('在曆史', '在歷史'),
    ('的曆史', '的歷史'),
    ('史曆', '史歷'),
    # Surname false-positive
    ('慄田', '栗田'),
    # 託 / 托 — names use 托, not 託
    ('託爾斯泰', '托爾斯泰'),
    ('託洛斯基', '托洛斯基'),
    ('託洛茨基', '托洛茨基'),
    ('託馬斯', '托馬斯'),
    ('託瓦德', '托瓦德'),
    ('託妮', '托妮'),
    ('託尼', '托尼'),
    ('託克維爾', '托克維爾'),
]


def to_traditional(text):
    if not text or not CC:
        return text
    out = CC.convert(text)
    # Apply post-fix substitutions
    for wrong, right in TRAD_FIXES:
        out = out.replace(wrong, right)
    return out


def strip_extension(title):
    # Strip up to 2 chained extensions (e.g., .pdf.epub)
    for _ in range(2):
        title = re.sub(r'\.(pdf|epub|mobi|azw3|azw|PDF|EPUB|MOBI|AZW3|AZW)$', '', title)
    return title


def remove_subtitle(title):
    for sep in ['：', '︰', ':']:
        if sep in title:
            return title.split(sep, 1)[0].strip()
    return title.strip()


def parse_filename(title):
    """
    Returns dict with:
      author, book_title_short (subtitle removed), book_title_full (subtitle kept)
    """
    base = strip_extension(title).strip()
    # Always strip (z-lib.org), (Z-Library) tags upfront — they're never part of title or author
    base = re.sub(r'\s*\((z-lib\.org|z-library)\)\s*', '', base, flags=re.IGNORECASE).strip()
    # Strip dangling "by" or "by author" if author is empty/single underscore
    base = re.sub(r'\s+by\s*(_?)\s*$', '', base, flags=re.IGNORECASE).strip()

    # 1. 經典與解釋 series prefix - 經典與解釋XX：title or 中國傳統-經典與解釋，title
    m = re.match(r'^(中國傳統-)?經典與解釋\d*[，：]\s*(.+?)$', base)
    if m:
        rest = m.group(2).strip()
        return {'author': None, 'short': remove_subtitle(rest), 'full': rest}

    # 2. Complete/Collected Works of [Name] (English)
    m = re.match(r'^(Complete|Collected) Works of (.+?)$', base, re.IGNORECASE)
    if m:
        return {'author': m.group(2).strip(), 'short': base, 'full': base}

    # 3a. "by [Author]" pattern (English z-lib OR Chinese with translator notation)
    base_lower = base.lower()
    has_zlib = '(z-lib' in base_lower or '(z-library' in base_lower
    if has_zlib or re.search(r'\bby\s+\S', base):
        # Strip (z-lib.org) and (Z-Library) suffix parens
        cleaned = re.sub(r'\s*\((z-lib\.org|z-library)\)\s*', '', base, flags=re.IGNORECASE).strip()
        # Strip dangling "by" with no author (e.g., "Title by  ")
        cleaned = re.sub(r'\s+by\s*$', '', cleaned, flags=re.IGNORECASE).strip()
        # Generic: capture everything after " by " until end (stripping trailing parens)
        m = re.search(r'^(.+?)\s+by\s+(.+?)(?:\s*\([^)]*\))*\s*$', cleaned)
        if m:
            title_part = m.group(1).strip()
            author_part = m.group(2).strip()
            # Strip trailing 譯/著 markers
            author_part = re.sub(r'(著|譯|編|主編)$', '', author_part).strip()
            # Sanity: author shouldn't be too long
            if 2 <= len(author_part) <= 80:
                return {'author': author_part, 'short': title_part, 'full': title_part}

    # 3. z-lib pattern with optional nested parens:
    #    "Title (subseries) (Author) (z-lib.org)"
    #    "Title (Author) (z-lib.org)"
    #    "Title (Author)"
    # Volume markers that should NOT be treated as authors (exact match)
    VOLUME_MARKERS = {'上', '中', '下', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                      '上冊', '中冊', '下冊', '上卷', '中卷', '下卷',
                      '續', '全', '完', '注', '註', '釋',
                      '一冊', '二冊', '三冊', '四冊', '五冊', '六冊', '七冊', '八冊'}
    paren_groups = re.findall(r'\(([^()]+)\)', base)
    if paren_groups:
        # Filter out (z-lib.org), (Z-Library), volume markers, etc
        candidates = []
        for g in paren_groups:
            g = g.strip()
            gl = g.lower()
            if 'z-lib' in gl or 'zlib' in gl or 'z-library' in gl:
                continue
            # Volume/edition markers like (套裝7冊), (共5冊), (全2冊)
            if re.match(r'^(共|全|套裝)?\d+(本|冊|卷|本套裝)?$', g):
                continue
            if g in VOLUME_MARKERS:
                continue
            if re.match(r'^[v\d]+$', g):
                continue
            candidates.append(g)
        # Last candidate is likely the author (e.g., "(三毛全集·02) (三毛)" -> 三毛)
        # Triggers if (z-lib.org) was originally present, OR if the title ends with a (Author) paren.
        ends_with_paren_author = candidates and re.search(r'\([^()]+\)\s*$', base) and \
                                 re.search(r'\([^()]+\)\s*$', base).group(0).strip('() ') == candidates[-1]
        had_zlib = bool(re.search(r'\((z-lib\.org|z-library)\)', title, re.IGNORECASE))  # check original title
        if candidates and (had_zlib or ends_with_paren_author):
            author = candidates[-1].strip()
            # Strip parens portion from title
            title_no_parens = re.sub(r'\s*\([^()]+\)', '', base).strip()
            if title_no_parens and '，' not in title_no_parens[:20]:
                return {'author': author, 'short': remove_subtitle(title_no_parens), 'full': title_no_parens}

    # 4. Split on first 全形/半形 comma
    for sep in ['，', ',']:
        if sep in base:
            parts = base.split(sep, 1)
            author = parts[0].strip()
            rest = parts[1].strip()
            if len(author) > 100:
                continue
            return {'author': author, 'short': remove_subtitle(rest), 'full': rest}

    # 5. No author marker
    return {'author': None, 'short': remove_subtitle(base), 'full': base}


def resolve_category(parent_id, folders, depth=0):
    if depth > 10:
        return None, None
    if parent_id in MAIN_CATEGORIES:
        return MAIN_CATEGORIES[parent_id], None
    if parent_id not in folders:
        return None, None
    folder = folders[parent_id]
    parent_parent = folder.get('parentId')
    if parent_parent in MAIN_CATEGORIES:
        return MAIN_CATEGORIES[parent_parent], folder['title']
    if parent_parent and parent_parent in folders:
        return resolve_category(parent_parent, folders, depth + 1)
    return None, None


def apply_overrides(record):
    """Apply manual overrides for known patterns."""
    orig = record['original_title']

    # Mormon books → 約瑟‧斯密
    if record['subcategory'] == '摩門教' and not record['author']:
        record['author'] = '約瑟‧斯密'

    # Title-based overrides
    if not record['author']:
        for pattern, author in TITLE_AUTHOR_OVERRIDES:
            if pattern in orig:
                record['author'] = author
                break

    return record


def main():
    with open('data/drive_inventory.json', 'r', encoding='utf-8') as f:
        inv = json.load(f)

    files = inv['files']
    folders = inv['folders']

    # First pass: parse all and collect groups
    initial = []
    for fid, fdata in files.items():
        info = parse_filename(fdata['title'])
        category, subcategory = resolve_category(fdata.get('parentId'), folders)
        initial.append({
            'file_id': fid,
            'original_title': fdata['title'],
            'parent_id': fdata.get('parentId'),
            'extension': fdata.get('extension', 'pdf').lower(),
            'file_size': fdata.get('fileSize'),
            'parsed_author': info['author'],
            'short_title': info['short'],
            'full_title': info['full'],
            'category': category,
            'subcategory': subcategory,
        })

    # Group by (parent_id, short_title) — if collision, must keep full title
    collision_keys = set()
    groups = defaultdict(list)
    for r in initial:
        key = (r['parent_id'], r['short_title'])
        groups[key].append(r)
    for key, rs in groups.items():
        if len(rs) > 1:
            collision_keys.add(key)

    # Build final records
    parsed = []
    for r in initial:
        # Choose title: full if would collide, else short
        if (r['parent_id'], r['short_title']) in collision_keys:
            book_title = r['full_title']
        else:
            book_title = r['short_title']

        # Convert to traditional
        author_t = to_traditional(r['parsed_author']) if r['parsed_author'] else None
        title_t = to_traditional(book_title) if book_title else None
        category_t = to_traditional(r['category']) if r['category'] else None
        subcategory_t = to_traditional(r['subcategory']) if r['subcategory'] else None

        # Build new filename
        ext = r['extension']
        if author_t:
            new_filename = f"{author_t}，{title_t}.{ext}"
        else:
            new_filename = f"{title_t}.{ext}"

        record = {
            'file_id': r['file_id'],
            'original_title': r['original_title'],
            'parent_id': r['parent_id'],
            'extension': ext,
            'file_size': r['file_size'],
            'author': author_t,
            'book_title': title_t,
            'new_filename': new_filename,
            'category': category_t,
            'subcategory': subcategory_t,
        }
        record = apply_overrides(record)

        # Recompute new_filename if override added an author
        if record['author']:
            record['new_filename'] = f"{record['author']}，{record['book_title']}.{ext}"

        parsed.append(record)

    # Stats
    total = len(parsed)
    no_author = sum(1 for r in parsed if not r['author'])
    no_category = sum(1 for r in parsed if not r['category'])

    print(f"Total: {total}", file=sys.stderr)
    print(f"Without author: {no_author}", file=sys.stderr)
    print(f"Without category: {no_category}", file=sys.stderr)
    print(file=sys.stderr)

    # Save output
    with open('data/drive_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    print("Saved: data/drive_parsed.json", file=sys.stderr)


if __name__ == '__main__':
    main()
