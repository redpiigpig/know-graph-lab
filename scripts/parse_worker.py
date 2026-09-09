#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse ebooks (PDF/EPUB/DOCX/TXT) into ebook_chunks table. Updates parse_progress.txt
checklist as it goes. Skips books already parsed (parsed_at IS NOT NULL).

Usage:
  python scripts/parse_worker.py init          # build checklist from DB
  python scripts/parse_worker.py run            # process all unparsed
  python scripts/parse_worker.py run --limit 5  # only 5 books (dry-run-ish)
  python scripts/parse_worker.py status         # show progress summary
"""
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime

try:
    import requests
    import fitz  # PyMuPDF
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing: {e}. Run: pip install requests pymupdf ebooklib beautifulsoup4", file=sys.stderr)
    sys.exit(1)

CHECKLIST = 'data/parse_progress.txt'
DRIVE_ROOT = 'G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館'
CHUNKS_DIR = 'G:/我的雲端硬碟/資料/知識圖工作室/_chunks'
PREVIEW_LEN = 100  # 2026-07-08 200→100：DB 超量救援  # only first N chars stored in DB; full text stays in local JSONL

# ── env loading ────────────────────────────────────────────────
def load_env():
    env = {}
    with open('.env', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

ENV = load_env()
URL = ENV['SUPABASE_URL']
KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}


# ── single-instance lock ───────────────────────────────────────
LOCKFILE = 'scripts/state/parse_worker.lock'


def single_instance():
    """Refuse to run if another parse_worker is already going.

    Without this, two workers duplicate every chunk of every book they overlap
    on: cmd_run asks for `parsed_at IS NULL ... order=id`, so both start at the
    *same* first book, and parsed_at is only written after the chunks are
    inserted. Both then report success. The scheduled run fires every 3 hours
    and a manual drain takes longer than that, so the overlap is routine, not
    a corner case.

    The lock is an OS file lock, not a PID file, precisely because the overnight
    task keeps dying by hard termination (0xC000013A) -- a PID file would be
    left behind and would then block every later run. An OS lock is released by
    the kernel when the process dies, however it dies.

    Returns the open handle; keep a reference alive for the whole run.
    """
    os.makedirs(os.path.dirname(LOCKFILE), exist_ok=True)
    fh = open(LOCKFILE, 'w')
    try:
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.close()
        return None
    return fh



# ── HTTP with retry ────────────────────────────────────────────
def _http(method, url, **kw):
    """Supabase 偶爾直接重置連線（WinError 10054），尤其在多個工具同時打同一個
    專案的時候。先前沒有重試，一次重置就讓整輪解析中斷——2026-09-09 那輪就是在
    61/350 掛掉的，前面 57 本的成果還在，但剩下 289 本要等下一次排程才會再跑。
    退避重試之後，單次網路抖動不會再終結整輪。"""
    last = None
    for i in range(1, 6):
        try:
            return getattr(requests, method)(url, **kw)
        except requests.exceptions.RequestException as e:
            last = e
            if i == 5:
                break
            print(f"    HTTP {method} 第 {i} 次失敗（{type(e).__name__}），{3*i}s 後重試",
                  flush=True)
            time.sleep(3 * i)
    raise last


# ── DB helpers ─────────────────────────────────────────────────
def fetch_unparsed_books(limit=None):
    """Return list of {id, title, file_type, file_path} for ebooks where parsed_at IS NULL."""
    params = 'select=id,title,file_type,file_path&parsed_at=is.null'
    if limit:
        params += f'&limit={limit}'
    r = _http('get', f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all_books():
    """Return all ebooks.

    Keyset paging, not OFFSET: `status` is normally run while a parse or an
    ingest is writing, and OFFSET over a table that is growing under you both
    repeats and skips rows -- which is how the counts drifted far enough to
    make `todo` come out negative.
    """
    out = []
    page_size = 1000
    last_id = ''
    while True:
        cursor = f'&id=gt.{last_id}' if last_id else ''
        params = (f'select=id,title,file_type,file_path,parsed_at,chunk_count,parse_error'
                  f'&order=id{cursor}&limit={page_size}')
        r = _http('get', f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out.extend(page)
        if len(page) < page_size:
            break
        last_id = page[-1]['id']
    return out


def _strip_nul(s):
    """Postgres 的 text 型別不收 \\u0000，帶 NUL 的 chunk 會讓整批 insert 回 22P05
    而整本書解析失敗（Schaff《History of the Christian Church》第三、四卷就是這樣
    掛掉的）。某些 PDF 的文字層本來就夾著 NUL，抽取端修不掉，在入庫前剝掉即可。"""
    return s.replace('\x00', '') if isinstance(s, str) else s


def insert_chunks(ebook_id, chunks):
    """Write full content to local JSONL, insert preview rows to DB.
    Returns number inserted."""
    for c in chunks:
        c['content'] = _strip_nul(c['content'])
        if c.get('chapter_path'):
            c['chapter_path'] = _strip_nul(c['chapter_path'])

    # 1. Write full content to local JSONL (source of truth, syncs to Drive)
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    jsonl_path = os.path.join(CHUNKS_DIR, f"{ebook_id}.jsonl")
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for i, c in enumerate(chunks):
            f.write(json.dumps({
                'chunk_index': i,
                'chunk_type': c['type'],
                'page_number': c.get('page'),
                'chapter_path': c.get('chapter_path'),
                'content': c['content'],
            }, ensure_ascii=False) + '\n')

    # 2. Build DB rows with truncated content (preview only)
    rows = []
    for i, c in enumerate(chunks):
        rows.append({
            'ebook_id': ebook_id,
            'chunk_index': i,
            'chunk_type': c['type'],
            'page_number': c.get('page'),
            'chapter_path': c.get('chapter_path'),
            'content': c['content'][:PREVIEW_LEN],  # 200 char preview only
            'char_count': len(c['content']),  # full length for stats
        })

    # 3. Adaptive batch insert (smaller batches retry on timeout)
    BATCH_SIZES = [50, 20, 5, 1]
    i = 0
    while i < len(rows):
        succeeded = False
        for batch_size in BATCH_SIZES:
            batch = rows[i:i+batch_size]
            r = _http('post', f"{URL}/rest/v1/ebook_chunks", headers=H, json=batch, timeout=120)
            if r.status_code in (200, 201):
                i += len(batch)
                succeeded = True
                break
            text = r.text[:300]
            if '57014' in text or 'timeout' in text.lower() or r.status_code >= 500:
                if batch_size > 1:
                    continue
            raise RuntimeError(f"chunk insert failed: HTTP {r.status_code} {text}")
        if not succeeded:
            raise RuntimeError(f"chunk insert failed even at batch_size=1")
    return len(rows)


def mark_parsed(ebook_id, chunk_count, total_chars):
    body = {
        'parsed_at': datetime.utcnow().isoformat() + 'Z',
        'chunk_count': chunk_count,
        'total_chars': total_chars,
        'parse_error': None,
    }
    r = _http('patch', f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}", headers=H, json=body, timeout=30)
    if r.status_code not in (200, 204):
        raise RuntimeError(f"mark_parsed failed: HTTP {r.status_code}")


def mark_error(ebook_id, error_msg):
    r = _http('patch',
        f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}",
        headers=H,
        json={'parse_error': error_msg[:1000]},
        timeout=30
    )
    return r.status_code in (200, 204)


def delete_existing_chunks(ebook_id):
    """Used when re-parsing — clear old chunks first."""
    _http('delete', f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}", headers=H, timeout=30)


# ── parsers ────────────────────────────────────────────────────
def parse_pdf(path):
    """Return list of {type:'page', page:N, content:str}."""
    chunks = []
    doc = fitz.open(path)
    try:
        for i, page in enumerate(doc):
            text = page.get_text()
            if text and text.strip():
                chunks.append({
                    'type': 'page',
                    'page': i + 1,
                    'content': text,
                })
    finally:
        doc.close()
    return chunks


def parse_epub(path):
    """Return list of {type:'chapter', chapter_path, content}."""
    book = epub.read_epub(path)

    # Build TOC map: item href -> chapter title path
    toc_map = {}
    def walk_toc(items, prefix=''):
        for item in items:
            if isinstance(item, tuple):
                section, children = item
                title = section.title if hasattr(section, 'title') else str(section)
                walk_toc(children, prefix + title + ' > ')
            else:
                title = item.title if hasattr(item, 'title') else ''
                href = item.href if hasattr(item, 'href') else ''
                if href:
                    href_clean = href.split('#')[0]
                    toc_map[href_clean] = (prefix + title).rstrip(' > ')
    try:
        walk_toc(book.toc)
    except Exception:
        pass  # TOC parsing best-effort

    chunks = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        href = item.get_name()
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        text = soup.get_text(separator='\n').strip()
        if not text:
            continue
        # Collapse multiple blank lines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        chapter_path = toc_map.get(href) or toc_map.get(href.split('/')[-1]) or item.get_name()
        chunks.append({
            'type': 'chapter',
            'chapter_path': chapter_path[:500],  # cap length
            'content': text,
        })
    return chunks


SUPPORTED = ('pdf', 'epub', 'docx', 'txt')


def parse_docx(path):
    """Return list of {type:'chapter', chapter_path, content}.

    段落標題（Heading N）當章界；沒有標題樣式的檔就整份成一章。表格逐列串成
    tab 分隔的一行接在該章尾，免得表格內容整批消失。"""
    import docx  # python-docx

    d = docx.Document(path)
    chunks, cur_title, buf = [], None, []

    def flush():
        text = '\n'.join(x for x in buf if x.strip())
        if text.strip():
            chunks.append({'type': 'chapter',
                           'chapter_path': cur_title or '',
                           'content': text})
        buf.clear()

    for p in d.paragraphs:
        style = (p.style.name or '') if p.style else ''
        text = p.text.strip()
        if style.startswith('Heading') and text:
            flush()
            cur_title = text
            buf.append(text)
        elif text:
            buf.append(text)
    for t in d.tables:
        for row in t.rows:
            cells = [c.text.strip().replace('\n', ' ') for c in row.cells]
            if any(cells):
                buf.append('\t'.join(cells))
    flush()
    return chunks


def parse_txt(path):
    """Return one chunk per ~3000 字 block. 純文字沒有結構可依，切固定長度。"""
    raw = None
    for enc in ('utf-8', 'utf-8-sig', 'big5', 'gb18030', 'cp950'):
        try:
            raw = Path(path).read_text(encoding=enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if raw is None:
        raw = Path(path).read_bytes().decode('utf-8', 'replace')
    paras = [p for p in raw.split('\n') if p.strip()]
    chunks, buf, size = [], [], 0
    for p in paras:
        buf.append(p)
        size += len(p)
        if size >= 3000:
            chunks.append({'type': 'chapter', 'chapter_path': '',
                           'content': '\n'.join(buf)})
            buf, size = [], 0
    if buf:
        chunks.append({'type': 'chapter', 'chapter_path': '',
                       'content': '\n'.join(buf)})
    return chunks


def parse_book(path, file_type, _retry=True):
    """Dispatch parser by file_type. Returns chunks list or raises.

    Drive 串流的檔第一次被打開時可能還沒 hydrate，會丟 OSError(22) Invalid
    argument；同一個檔第二次開就正常。整本書因此被標成解析失敗太冤，重試一次。
    """
    try:
        return _parse_book(path, file_type)
    except OSError as e:
        if not _retry:
            raise
        print(f"    OSError {e.errno}，Drive 檔可能未就緒，5 秒後重試一次")
        time.sleep(5)
        return _parse_book(path, file_type)


def _parse_book(path, file_type):
    ft = file_type.lower()
    if ft == 'pdf':
        return parse_pdf(path)
    elif ft == 'epub':
        return parse_epub(path)
    elif ft == 'docx':
        return parse_docx(path)
    elif ft == 'txt':
        return parse_txt(path)
    else:
        # .doc（舊二進位）、.mobi、.azw3、.chm 仍未支援，需先轉檔
        raise NotImplementedError(f"format not supported: {ft}")


# ── checklist ──────────────────────────────────────────────────
def write_checklist(books):
    """Build initial checklist from books list."""
    os.makedirs('data', exist_ok=True)
    with open(CHECKLIST, 'w', encoding='utf-8') as f:
        f.write("# Ebook parse progress\n")
        f.write("# [ ] not started   [x] parsed   [!] error   [-] skipped (unsupported format)\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
        for b in books:
            mark = ' '
            note = ''
            if b.get('parsed_at'):
                mark = 'x'
                note = f"  ({b.get('chunk_count', '?')} chunks)"
            elif b.get('parse_error'):
                mark = '!'
                note = f"  ERROR: {(b.get('parse_error') or '')[:80]}"
            elif b['file_type'] not in SUPPORTED:
                mark = '-'
                note = f"  (skip: {b['file_type']})"
            rel_path = (b.get('file_path') or '').replace(DRIVE_ROOT.replace('/', '\\'), '').lstrip('\\')
            f.write(f"[{mark}] {b['id'][:8]} {rel_path}{note}\n")


def update_checklist_line(ebook_id, status, note=''):
    """Replace the line for ebook_id with new status."""
    if not os.path.exists(CHECKLIST):
        return
    with open(CHECKLIST, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if f'] {ebook_id[:8]} ' in line:
            # Strip old status marker and any trailing note
            m = re.match(r'^\[.\] (\S+) (.+?)(  \(\d+ chunks\)|  ERROR:.*|  \(skip:.*\))?\s*$', line)
            if m:
                rel_path = m.group(2)
            else:
                rel_path = line.split(']', 1)[1].strip().split(' ', 1)[1] if ' ' in line.split(']', 1)[1].strip() else ''
            new_line = f"[{status}] {ebook_id[:8]} {rel_path}{note}\n"
            lines[i] = new_line
            break
    with open(CHECKLIST, 'w', encoding='utf-8') as f:
        f.writelines(lines)


# ── commands ───────────────────────────────────────────────────
def cmd_init():
    books = fetch_all_books()
    print(f"Fetched {len(books)} books from DB", file=sys.stderr)
    write_checklist(books)
    print(f"Wrote checklist: {CHECKLIST}", file=sys.stderr)
    # Stats
    parsed = sum(1 for b in books if b.get('parsed_at'))
    errored = sum(1 for b in books if b.get('parse_error'))
    skipped = sum(1 for b in books if b['file_type'] not in SUPPORTED)
    todo = len(books) - parsed - errored - skipped
    print(f"  parsed: {parsed}, error: {errored}, skip: {skipped}, todo: {todo}", file=sys.stderr)


def cmd_status():
    """Progress summary.

    The buckets must be mutually exclusive and `todo` must be *counted*, not
    inferred by subtraction. The old version did `len - parsed - errored -
    skipped` while the three overlapped freely -- a book that errored once and
    parsed on a later attempt keeps both columns, and a mobi book can carry a
    parse_error too -- so every such book was subtracted twice. That is how
    todo reached -152 while still reporting plausible-looking numbers before
    it went negative.

    `todo` uses exactly the predicate cmd_run selects on, so the two can never
    disagree about what is left.
    """
    books = fetch_all_books()
    parsed = errored = skipped = todo = 0
    total_chunks = 0
    for b in books:
        total_chunks += b.get('chunk_count') or 0
        if b['file_type'] not in SUPPORTED:
            skipped += 1
        elif b.get('parsed_at'):
            parsed += 1
        elif b.get('parse_error'):
            errored += 1
        else:
            todo += 1
    print(f"Total books: {len(books)}")
    print(f"  parsed:  {parsed}  ({total_chunks} chunks total)")
    print(f"  error:   {errored}  (retry: clear parse_error to requeue)")
    print(f"  skip:    {skipped}  (mobi/azw3/azw — pure-Python parsing not supported)")
    print(f"  todo:    {todo}")
    assert parsed + errored + skipped + todo == len(books), "buckets must partition the table"


def cmd_run(limit=None):
    """Process all unparsed pdf/epub books."""
    lock = single_instance()
    if lock is None:
        # Not an error: the overnight chain should carry on to OCR rather than
        # abort the whole run just because a manual drain is in progress.
        print("another parse_worker holds the lock; skipping parse this round", file=sys.stderr)
        return

    # Get all unparsed PDFs and EPUBs.
    # 🚨 Always pass an explicit limit. PostgREST caps an unbounded select at its
    # own default (1000) and says nothing about it, so `run` with no --limit was
    # silently a 1000-book batch, not "the whole queue" -- which is how a 5,000
    # book backlog looked like it was being drained in one pass.
    params = 'select=id,title,file_type,file_path&parsed_at=is.null&parse_error=is.null&file_type=in.(pdf,epub,docx,txt)&order=id'
    params += f'&limit={limit or 1000}'
    r = _http('get', f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    books = r.json()
    print(f"To process: {len(books)} books", file=sys.stderr)

    succeeded = 0
    failed = 0
    for n, b in enumerate(books, 1):
        path = b['file_path']
        ebook_id = b['id']
        title = b['title'][:60]
        ft = b['file_type']

        print(f"\n[{n}/{len(books)}] [{ft}] {title}", file=sys.stderr)

        if not path or not os.path.exists(path):
            err = f"file not found: {path}"
            print(f"  ! {err}", file=sys.stderr)
            mark_error(ebook_id, err)
            update_checklist_line(ebook_id, '!', f"  ERROR: file not found")
            failed += 1
            continue

        try:
            t0 = time.time()
            chunks = parse_book(path, ft)
            if not chunks:
                err = "no extractable text"
                print(f"  ! {err}", file=sys.stderr)
                mark_error(ebook_id, err)
                update_checklist_line(ebook_id, '!', f"  ERROR: {err}")
                failed += 1
                continue

            total_chars = sum(len(c['content']) for c in chunks)
            # Wipe any partial chunks from a previous failed attempt
            delete_existing_chunks(ebook_id)
            insert_chunks(ebook_id, chunks)
            mark_parsed(ebook_id, len(chunks), total_chars)
            update_checklist_line(ebook_id, 'x', f"  ({len(chunks)} chunks, {total_chars:,} chars)")
            elapsed = time.time() - t0
            print(f"  ✓ {len(chunks)} chunks, {total_chars:,} chars, {elapsed:.1f}s", file=sys.stderr)
            succeeded += 1
        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)[:200]}"
            print(f"  ! {err_msg}", file=sys.stderr)
            mark_error(ebook_id, err_msg)
            update_checklist_line(ebook_id, '!', f"  ERROR: {err_msg[:80]}")
            failed += 1

    print(f"\n=== Done ===", file=sys.stderr)
    print(f"  succeeded: {succeeded}", file=sys.stderr)
    print(f"  failed:    {failed}", file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    # S0 Modern Standby 會把整批主控台行程一起帶走（0xC000013A）。見 keep_awake.py。
    try:
        from keep_awake import keep_awake
        keep_awake()
    except Exception:
        pass

    cmd = sys.argv[1]
    if cmd == 'init':
        cmd_init()
    elif cmd == 'status':
        cmd_status()
    elif cmd == 'run':
        limit = None
        if '--limit' in sys.argv:
            limit = int(sys.argv[sys.argv.index('--limit') + 1])
        cmd_run(limit)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
