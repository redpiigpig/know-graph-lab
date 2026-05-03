#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walk the local Google Drive ebook folder, parse filenames, and produce:
- data/local_inventory.json: full snapshot of {path, original_name, parsed_author, parsed_title, category, subcategory, new_name, target_path}

Usage:
  python scripts/local_drive_pipeline.py scan       # build inventory from local FS
  python scripts/local_drive_pipeline.py rename     # apply renames (uses inventory)
  python scripts/local_drive_pipeline.py dryrun     # preview renames
"""
import json
import os
import re
import sys
from pathlib import Path

DRIVE_ROOT = Path('G:/我的雲端硬碟/資料/電子書')
INVENTORY_FILE = 'data/local_inventory.json'

EBOOK_EXTS = {'.pdf', '.epub', '.mobi', '.azw3', '.azw'}

# Reuse parsing logic from parse_drive_inventory.py
sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import (
    parse_filename, to_traditional, TITLE_AUTHOR_OVERRIDES, MAIN_CATEGORIES
)


# Windows-disallowed characters in filenames
INVALID_CHARS = r'<>:"|?*\\/'


def sanitize_filename(name):
    """Replace invalid chars with safe alternatives."""
    # Replace half-width invalid chars with full-width versions
    replacements = {
        '<': '＜', '>': '＞', ':': '：', '"': '"', '|': '｜',
        '?': '？', '*': '＊', '\\': '＼', '/': '／',
    }
    for bad, good in replacements.items():
        name = name.replace(bad, good)
    return name.strip()


def determine_category(rel_parts):
    """Determine category/subcategory from path parts (relative to DRIVE_ROOT)."""
    if not rel_parts:
        return None, None
    category = rel_parts[0]  # e.g., 哲學
    subcategory = rel_parts[1] if len(rel_parts) > 1 else None
    return category, subcategory


def apply_overrides(record):
    orig = record['original_name']
    if record['subcategory'] == '摩門教' and not record['author']:
        record['author'] = '約瑟‧斯密'
    if not record['author']:
        for pattern, author in TITLE_AUTHOR_OVERRIDES:
            if pattern in orig:
                record['author'] = author
                break
    return record


def scan():
    """Walk the local Drive folder and build inventory."""
    inventory = []
    for root, _, files in os.walk(DRIVE_ROOT):
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext not in EBOOK_EXTS:
                continue
            full_path = Path(root) / fname
            rel_path = full_path.relative_to(DRIVE_ROOT)
            rel_parts = list(rel_path.parts[:-1])  # parent dirs

            category, subcategory = determine_category(rel_parts)
            info = parse_filename(fname)

            author = to_traditional(info['author']) if info['author'] else None
            book_title = to_traditional(info['short']) if info['short'] else None

            record = {
                'original_path': str(full_path),
                'original_name': fname,
                'parent_dir': str(full_path.parent),
                'extension': ext.lstrip('.'),
                'category': category,
                'subcategory': subcategory,
                'author': author,
                'book_title': book_title,
            }
            record = apply_overrides(record)

            # Determine if this is a series collision (use full title)
            # Skip for now — handle in second pass
            record['use_full_title'] = False

            inventory.append(record)

    # Detect collisions: same parent_dir + same short title -> use full title
    from collections import defaultdict
    groups = defaultdict(list)
    for i, r in enumerate(inventory):
        key = (r['parent_dir'], r['book_title'])
        groups[key].append(i)
    for key, indices in groups.items():
        if len(indices) > 1:
            for i in indices:
                inventory[i]['use_full_title'] = True

    # Re-parse with full title for collision groups
    for r in inventory:
        if r['use_full_title']:
            info = parse_filename(r['original_name'])
            full = to_traditional(info['full']) if info['full'] else r['book_title']
            r['book_title'] = full

    # Compute new_name and target_path
    for r in inventory:
        title = (r['book_title'] or 'Untitled').strip()
        author = (r['author'] or '').strip()

        # Clean up: strip trailing .pdf etc. from title/author (they may have leaked in)
        title = re.sub(r'\.(pdf|epub|mobi|azw3|azw)\b', '', title, flags=re.IGNORECASE).strip()
        author = re.sub(r'\.(pdf|epub|mobi|azw3|azw)\b', '', author, flags=re.IGNORECASE).strip()
        # Clean up: dedupe author if it appears twice with []
        author = re.sub(r'^(.+?)\s*\[\1\]$', r'\1', author).strip()

        # Validation: if title is empty, useless
        unsafe = False
        reasons = []
        if not title or title == 'Untitled':
            unsafe = True
            reasons.append('no_title')
        if author and (len(author) > 50 or '_' == author):
            unsafe = True
            reasons.append('bad_author')
        # Build new name
        if author:
            new_name = f"{author}，{title}.{r['extension']}"
        else:
            new_name = f"{title}.{r['extension']}"
        new_name = sanitize_filename(new_name)
        # Final check: too long for Windows (260 char limit roughly)
        if len(new_name) > 200:
            unsafe = True
            reasons.append('too_long')

        r['new_name'] = new_name if not unsafe else r['original_name']
        r['unsafe_reasons'] = reasons
        r['target_path'] = str(Path(r['parent_dir']) / r['new_name'])

    os.makedirs('data', exist_ok=True)
    with open(INVENTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)
    print(f"Scanned {len(inventory)} ebooks", file=sys.stderr)

    # Stats
    no_author = sum(1 for r in inventory if not r['author'])
    no_cat = sum(1 for r in inventory if not r['category'])
    print(f"No author: {no_author}", file=sys.stderr)
    print(f"No category: {no_cat}", file=sys.stderr)
    rename_count = sum(1 for r in inventory if r['original_name'] != r['new_name'])
    print(f"Will rename: {rename_count}", file=sys.stderr)


def dryrun():
    with open(INVENTORY_FILE, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    n = 0
    for r in inventory:
        if r['original_name'] != r['new_name']:
            n += 1
            if n <= 30:
                print(f"  {r['original_name']}")
                print(f"    -> {r['new_name']}")
    print(f"\nTotal would rename: {n}", file=sys.stderr)


def rename():
    with open(INVENTORY_FILE, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    renamed = 0
    skipped = 0
    failed = 0
    log = []
    for r in inventory:
        if r['original_name'] == r['new_name']:
            continue
        src = Path(r['original_path'])
        dst = Path(r['target_path'])
        if not src.exists():
            log.append(f"MISSING: {src}")
            failed += 1
            continue
        if dst.exists() and src != dst:
            log.append(f"TARGET EXISTS: {dst}  (source: {src.name})")
            skipped += 1
            continue
        try:
            src.rename(dst)
            renamed += 1
            if renamed % 100 == 0:
                print(f"  renamed {renamed}...", file=sys.stderr)
        except Exception as e:
            log.append(f"FAILED: {src} -> {dst}: {e}")
            failed += 1

    with open('data/rename_log.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log))

    print(f"\nRenamed: {renamed}", file=sys.stderr)
    print(f"Skipped (target exists): {skipped}", file=sys.stderr)
    print(f"Failed: {failed}", file=sys.stderr)
    print("Log: data/rename_log.txt", file=sys.stderr)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if cmd == 'scan':
        scan()
    elif cmd == 'dryrun':
        dryrun()
    elif cmd == 'rename':
        rename()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
