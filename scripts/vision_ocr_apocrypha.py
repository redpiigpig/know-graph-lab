"""
Page-batched Gemini Vision OCR for the 10 黃根春《基督教典外文獻》PDFs.

Why a dedicated script instead of `ocr_with_gemini.py`:
  Existing script uploads the whole PDF and asks Gemini to OCR every page in
  one call. Gemini Flash output caps around 32K tokens (~14K Chinese chars),
  so a 350-page book truncates to ~30 pages (94% loss). This script renders
  pages to images and batches them in groups of ~15 per Vision call, with
  per-batch checkpointing so a mid-book crash doesn't lose work.

Pipeline per book:
  1. Open PDF with PyMuPDF, render each page → JPEG bytes at 150 DPI.
  2. Batch BATCH_PAGES per Gemini Vision call.
  3. Parse structured JSON output → list of {page, text}.
  4. Append cleaned batch to checkpoint JSONL on disk.
  5. After all batches done: copy checkpoint → final JSONL, insert
     ebook_chunks rows (preview), update ebooks.parsed_at/total_pages.

Key rotation: 4 GEMINI_API_KEYs cycle on 429. Two consecutive batches with
all-keys-out pauses the run (per memory rule).

Usage:
  python -X utf8 scripts/vision_ocr_apocrypha.py status
  python -X utf8 scripts/vision_ocr_apocrypha.py run [--book ID] [--batch-pages 15]
                                                     [--dpi 150] [--limit 1]
"""
from __future__ import annotations
import os, sys, json, time, argparse, base64, io
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()
SUPABASE_URL = os.environ['SUPABASE_URL']
PROJECT_REF = SUPABASE_URL.split('//')[1].split('.')[0]
ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Missing: pip install google-genai", file=sys.stderr); sys.exit(1)

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing: pip install PyMuPDF", file=sys.stderr); sys.exit(1)

try:
    import json_repair as _json_repair
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

import subprocess

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/電子書/_chunks")
MODEL = "gemini-2.5-flash"

# Haiku CLI fallback (used when all Gemini keys quota-blocked).
# Uses Max-session OAuth via claude.cmd; no ANTHROPIC_API_KEY required.
def _resolve_claude_bin() -> str:
    if sys.platform == 'win32':
        for cand in [os.path.expandvars(r'%APPDATA%\npm\claude.cmd')]:
            if os.path.exists(cand): return cand
    return 'claude'
CLAUDE_BIN = _resolve_claude_bin()
# 5 Chinese-heavy pages × ~1000 chars × 2 tokens/char ≈ 10K output tokens —
# comfortably under Gemini Flash's 32K cap. Larger batches (10+) routinely
# truncate the JSON response, returning 0 parseable pages.
DEFAULT_BATCH_PAGES = 5
DEFAULT_DPI = 150
PREVIEW_LEN = 200

BOOKS: list[dict] = [
    {'id': 'b1fbff1b-cbf1-45b6-a9cd-cf0e9f943c57', 'title': '基督教典外文獻-舊約篇-第1冊'},
    {'id': 'd5e5df29-2428-4dca-9f79-5ca21587d073', 'title': '基督教典外文獻-舊約篇-第2冊'},
    {'id': 'af50523d-b206-447d-8060-78d4e366ced4', 'title': '基督教典外文獻-舊約篇-第3冊'},
    {'id': 'a96b524b-464e-419e-8d78-b302d28302d3', 'title': '基督教典外文獻-舊約篇-第4冊'},
    {'id': '05f4b0a5-f5ba-4a33-8187-34f9c9abbff3', 'title': '基督教典外文獻-舊約篇-第5冊'},
    {'id': '6aaa0ffe-e8ad-41d2-943e-49d7fd6125d2', 'title': '基督教典外文獻-舊約篇-第6冊'},
    {'id': '425f2664-e967-4fc0-b053-d79bc1ac106d', 'title': '基督教典外文獻-新約篇-第1冊'},
    {'id': '0a1b2977-3d3c-4a47-96cd-0bee1bad17f1', 'title': '基督教典外文獻-新約篇-第2冊'},
    {'id': '12156219-cf9c-4610-a84c-5d5358c22817', 'title': '基督教典外文獻-新約篇-第3冊'},
    {'id': '677c5e16-5b19-4f9b-9499-ee44d5c3eb01', 'title': '基督教典外文獻-新約篇-第4冊'},
]
BOOK_DIR = Path("G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/基督教典外文獻 (10 冊)")
for b in BOOKS:
    b['path'] = BOOK_DIR / f"{b['title']}.pdf"


def _find_gemini_keys() -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for name in ('GEMINI_API_KEY', 'Gemini_API_Key'):
        v = os.environ.get(name)
        if v:
            for k in v.split(','):
                k = k.strip()
                if k and k not in seen: seen.add(k); out.append(k)
        for n in range(1, 6):
            v = os.environ.get(f"{name}_{n}")
            if v:
                for k in v.split(','):
                    k = k.strip()
                    if k and k not in seen: seen.add(k); out.append(k)
    return out


API_KEYS = _find_gemini_keys()
PROMPT = (
    "Each image is one page from a Chinese book (基督教典外文獻 / 黃根春主編，繁體中文). "
    "For each page, extract ALL visible text exactly as written. "
    "Use traditional Chinese 繁體 throughout. "
    "Preserve paragraph breaks with \\n. "
    "Do not translate, summarize, or add commentary. "
    "Skip purely decorative content but still emit the page with empty text. "
    "Return JSON object: {\"pages\":[{\"page\":<1-based-pdf-index>,\"text\":\"...\"}]}."
)
PAGES_SCHEMA = {
    "type": "object",
    "properties": {
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer"},
                    "text": {"type": "string"},
                },
                "required": ["page", "text"],
            },
        },
    },
    "required": ["pages"],
}


# ── DB helpers ─────────────────────────────────────────────────────────
def mgmt_query(sql: str):
    r = requests.post(
        f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
        headers={'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        json={'query': sql}, timeout=60)
    r.raise_for_status()
    return r.json() if r.text else []


def insert_chunks(book_id: str, pages: list[dict]):
    """Delete + insert ebook_chunks rows (preview only) for this book."""
    H = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
         'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
    requests.delete(f"{SUPABASE_URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
                    headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
                    timeout=60)
    rows = [{
        'ebook_id': book_id,
        'chunk_index': i,
        'chunk_type': 'page',
        'page_number': p['page'],
        'chapter_path': None,
        'content': p['text'][:PREVIEW_LEN],
        'char_count': len(p['text']),
    } for i, p in enumerate(pages)]
    BATCH = 100
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        r = requests.post(f"{SUPABASE_URL}/rest/v1/ebook_chunks",
                          headers=H, json=batch, timeout=120)
        r.raise_for_status()


def write_jsonl(book_id: str, pages: list[dict]) -> Path:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHUNKS_DIR / f"{book_id}.jsonl"
    with out.open('w', encoding='utf-8') as f:
        for i, p in enumerate(pages):
            f.write(json.dumps({
                'chunk_index': i,
                'chunk_type': 'page',
                'page_number': p['page'],
                'chapter_path': None,
                'content': p['text'],
            }, ensure_ascii=False) + '\n')
    return out


def update_book_done(book_id: str, total_chars: int, n_pages: int, total_pdf_pages: int):
    H = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
         'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H,
        json={
            'parsed_at': datetime.utcnow().isoformat() + 'Z',
            'parse_error': None,
            'total_chars': total_chars,
            'chunk_count': n_pages,
            'total_pages': total_pdf_pages,
        }, timeout=30)


# ── Gemini call with key rotation ────────────────────────────────────
class KeyRotator:
    def __init__(self, keys: list[str]):
        self.keys = keys
        self.idx = 0
        self.client = genai.Client(api_key=keys[0])
    def rotate(self) -> bool:
        if self.idx + 1 >= len(self.keys):
            return False
        self.idx += 1
        self.client = genai.Client(api_key=self.keys[self.idx])
        print(f'    ⟳ rotated to key #{self.idx + 1}/{len(self.keys)}', flush=True)
        return True
    def reset(self):
        self.idx = 0
        self.client = genai.Client(api_key=self.keys[0])


def is_quota_error(err: str) -> bool:
    low = err.lower()
    return any(k in low for k in ('429', 'quota', 'resource_exhausted', 'rate limit'))


def is_transient_error(err: str) -> bool:
    low = err.lower()
    return is_quota_error(err) or any(k in low for k in
        ('503', '502', '504', '500', 'deadline_exceeded', 'unavailable',
         'internal', 'timeout', 'connection'))


def gemini_ocr_batch(rotator: KeyRotator, page_images: list[tuple[int, bytes]],
                     max_output_tokens: int = 32000) -> list[dict] | None:
    """Send a batch of page images to Gemini Vision. Returns list of {page, text} or None on hard fail.

    `page_images` is list of (page_number, jpeg_bytes).
    """
    contents = []
    for pn, img_bytes in page_images:
        contents.append(types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'))
    # Tag prompt with page numbers so the model emits them correctly
    page_list = ','.join(str(pn) for pn, _ in page_images)
    prompt = PROMPT + f"\nThe images shown correspond to PDF pages: {page_list} (in that order)."
    contents.append(prompt)

    for retry in range(4):
        try:
            resp = rotator.client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=PAGES_SCHEMA,
                    max_output_tokens=max_output_tokens,
                ),
            )
            try:
                data = json.loads(resp.text)
            except json.JSONDecodeError:
                # Gemini truncated the JSON mid-string. Use json_repair to
                # salvage whatever complete page objects were emitted.
                if HAS_JSON_REPAIR:
                    try:
                        data = _json_repair.loads(resp.text)
                        if not isinstance(data, dict): data = {}
                        n = len(data.get('pages', []))
                        if n:
                            print(f' ⚠json_repair salvaged {n}p', end='', flush=True)
                    except Exception:
                        return None
                else:
                    return None
            pages = data.get('pages', [])
            return pages
        except Exception as e:
            err = str(e)[:300]
            if is_quota_error(err):
                if rotator.rotate():
                    continue
                print(f'    ⛔ all keys quota-blocked', flush=True)
                return None
            if is_transient_error(err) and retry < 3:
                wait = (retry + 1) * 10
                print(f'    ↻ transient err, retry {retry+1}/3 after {wait}s: {err[:120]}', flush=True)
                time.sleep(wait)
                continue
            print(f'    ❌ hard error: {err[:200]}', flush=True)
            return None
    return None


def render_page_jpeg(doc, page_idx: int, dpi: int) -> bytes:
    """Render PDF page to JPEG bytes."""
    page = doc[page_idx]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    return pix.tobytes('jpeg', jpg_quality=85)


# ── Haiku CLI fallback (image OCR via Max-session OAuth) ─────────────
HAIKU_PROMPT = (
    "Each image is one page of a Chinese book (基督教典外文獻 / 黃根春主編，繁體中文). "
    "For each page, extract ALL visible text exactly as written. "
    "Use traditional Chinese 繁體 throughout. "
    "Preserve paragraph breaks. "
    "Do NOT translate, summarize, or add commentary. "
    "Output format: emit each page as `===PAGE <N>===` on its own line, "
    "followed by that page's text. Example:\n"
    "===PAGE 21===\n"
    "(page 21 content)\n"
    "===PAGE 22===\n"
    "(page 22 content)\n"
)


def haiku_ocr_batch(page_images: list[tuple[int, bytes]]) -> list[dict] | None:
    """OCR a batch of page images via Haiku CLI. Returns list of {page,text} or None on hard fail."""
    # Build stream-json input: single user message with all images + prompt
    content_blocks = []
    for pn, img_bytes in page_images:
        b64 = base64.standard_b64encode(img_bytes).decode()
        content_blocks.append({
            'type': 'image',
            'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': b64},
        })
    page_list = ','.join(str(pn) for pn, _ in page_images)
    content_blocks.append({
        'type': 'text',
        'text': HAIKU_PROMPT + f"\nThe images correspond to PDF pages: {page_list} (in that order).",
    })
    msg = {
        'type': 'user',
        'message': {'role': 'user', 'content': content_blocks},
    }
    stdin_payload = json.dumps(msg) + '\n'

    cmd = [
        CLAUDE_BIN, '-p',
        '--model', 'haiku',
        '--verbose',                    # required for stream-json output
        '--disable-slash-commands',
        '--allowedTools', '',           # no Read tool, just text reply
        '--input-format', 'stream-json',
        '--output-format', 'stream-json',
    ]
    cwd = r'c:\tmp' if sys.platform == 'win32' else '/tmp'
    try:
        proc = subprocess.run(
            cmd, input=stdin_payload, capture_output=True,
            text=True, encoding='utf-8', timeout=600, cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        print(f'    ❌ Haiku timeout 600s', flush=True)
        return None
    if proc.returncode != 0:
        # Look for rate_limit_event in stdout — if present and we're past
        # the five_hour limit, return None so caller can pause/abort.
        if 'rate_limit' in (proc.stderr or '') + (proc.stdout or ''):
            print(f'    ❌ Haiku rate limited', flush=True)
        else:
            print(f'    ❌ Haiku exit {proc.returncode}: {proc.stderr[:250]}', flush=True)
        return None

    # Parse stream-json: find the final "result" event
    final_text = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line: continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get('type') == 'result' and evt.get('subtype') == 'success':
            final_text = evt.get('result', '')
        if evt.get('type') == 'rate_limit_event':
            info = evt.get('rate_limit_info', {})
            if info.get('utilization', 0) >= 0.98 or info.get('isUsingOverage'):
                print(f'    ⚠ Haiku rate limit {info.get("utilization", 0)*100:.0f}%', flush=True)

    if not final_text:
        print(f'    ❌ Haiku returned no result text', flush=True)
        return None

    # Split by "===PAGE N===" markers
    import re
    parts = re.split(r'===PAGE\s+(\d+)===', final_text)
    # parts: [pre, num1, body1, num2, body2, ...]
    blocks: list[tuple[str, str]] = []
    for i in range(1, len(parts) - 1, 2):
        blocks.append((parts[i], parts[i + 1].strip()))

    # Match by ORDER to expected page numbers (Haiku's reported page may differ)
    out = []
    for k, (pn, _) in enumerate(page_images):
        if k < len(blocks):
            out.append({'page': pn, 'text': blocks[k][1]})
        else:
            out.append({'page': pn, 'text': ''})
    return out


# ── Per-book OCR driver ────────────────────────────────────────────────
def process_book(book: dict, rotator: KeyRotator, batch_pages: int, dpi: int) -> bool:
    """Run page-batched Vision OCR on one book. Returns True on success.

    Resumable via per-book JSONL checkpoint:
      G:/.../_chunks/{book_id}.ckpt.jsonl  — append-only, batches stamped as JSONL
    """
    src = book['path']
    if not src.exists():
        print(f'  ⚠ source missing: {src}', flush=True); return False

    doc = fitz.open(src)
    total = len(doc)
    print(f'  {book["title"]}: {total} pages', flush=True)

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    ckpt_path = CHUNKS_DIR / f"{book['id']}.ckpt.jsonl"

    # Load existing checkpoint to know what's done
    done_pages: set[int] = set()
    all_pages: dict[int, str] = {}
    if ckpt_path.exists():
        with ckpt_path.open('r', encoding='utf-8') as f:
            for line in f:
                try:
                    p = json.loads(line)
                    all_pages[int(p['page'])] = p['text']
                    done_pages.add(int(p['page']))
                except Exception:
                    pass
    if done_pages:
        print(f'    resume: {len(done_pages)} pages already in ckpt', flush=True)

    # Process in batches
    quota_strikes = 0
    ckpt_f = ckpt_path.open('a', encoding='utf-8')
    try:
        for batch_start in range(0, total, batch_pages):
            batch_end = min(batch_start + batch_pages, total)
            page_idxs = list(range(batch_start, batch_end))
            page_nums = [i + 1 for i in page_idxs]

            # Skip if all pages in this batch already done
            todo = [pn for pn in page_nums if pn not in done_pages]
            if not todo:
                continue

            t = time.time()
            print(f'    batch pages {page_nums[0]}-{page_nums[-1]} ({len(page_nums)} pp)…',
                  end='', flush=True)
            # Render only pages we need
            page_imgs = []
            for pi, pn in zip(page_idxs, page_nums):
                if pn in done_pages: continue
                page_imgs.append((pn, render_page_jpeg(doc, pi, dpi)))

            result = gemini_ocr_batch(rotator, page_imgs)
            used_engine = 'gemini'
            if result is None:
                # Gemini all-keys quota → fall back to Haiku per user instruction
                print(f' (Gemini out → Haiku)…', end='', flush=True)
                result = haiku_ocr_batch(page_imgs)
                used_engine = 'haiku'
                if result is None:
                    quota_strikes += 1
                    if quota_strikes >= 2:
                        print(f'\n  ⛔ both engines quota-blocked: pausing (ckpt saved)', flush=True)
                        return False
                    print(f'\n    Haiku also out; waiting 90s', flush=True)
                    time.sleep(90)
                    continue

            quota_strikes = 0
            # Match results to expected page_numbers by ORDER (Gemini sometimes
            # mis-numbers its "page" field; we trust the image order we sent).
            for k, (pn, _) in enumerate(page_imgs):
                if k < len(result):
                    text = (result[k].get('text') or '').strip()
                else:
                    text = ''
                all_pages[pn] = text
                done_pages.add(pn)
                ckpt_f.write(json.dumps({'page': pn, 'text': text, 'engine': used_engine},
                                        ensure_ascii=False) + '\n')
            ckpt_f.flush()
            elapsed = time.time() - t
            sample_chars = sum(len(all_pages[pn]) for pn, _ in page_imgs)
            print(f' ✓ ({used_engine}) {sample_chars} chars in {elapsed:.0f}s', flush=True)
    finally:
        ckpt_f.close()
        doc.close()

    # Build final list sorted by page number
    final_pages = [{'page': pn, 'text': all_pages.get(pn, '')}
                   for pn in sorted(all_pages.keys())]
    non_empty = [p for p in final_pages if p['text']]
    total_chars = sum(len(p['text']) for p in non_empty)

    # Write final JSONL + DB
    write_jsonl(book['id'], final_pages)
    insert_chunks(book['id'], final_pages)
    update_book_done(book['id'], total_chars, n_pages=len(final_pages),
                     total_pdf_pages=total)
    print(f'  ✓ {book["title"]} done: {len(non_empty)}/{total} non-empty, {total_chars//1000}K chars',
          flush=True)
    return True


# ── Commands ───────────────────────────────────────────────────────────
def cmd_status():
    print(f'Configured Gemini keys: {len(API_KEYS)}')
    for b in BOOKS:
        ckpt = CHUNKS_DIR / f"{b['id']}.ckpt.jsonl"
        n = 0
        if ckpt.exists():
            with ckpt.open('r', encoding='utf-8') as f:
                n = sum(1 for _ in f)
        print(f'  {b["title"]:40s} ckpt={n} {"(file ok)" if b["path"].exists() else "MISSING"}')


def cmd_run(book_ids: list[str] | None, batch_pages: int, dpi: int, limit: int | None):
    if not API_KEYS:
        print('❌ No GEMINI_API_KEY set', file=sys.stderr); sys.exit(1)
    targets = BOOKS
    if book_ids:
        targets = [b for b in BOOKS if b['id'] in set(book_ids)]
    if limit:
        targets = targets[:limit]

    rotator = KeyRotator(API_KEYS)
    print(f'Processing {len(targets)} books, batch_pages={batch_pages}, dpi={dpi}', flush=True)
    t0 = time.time()
    ok = 0
    for i, book in enumerate(targets, 1):
        print(f'\n[{i}/{len(targets)}]', flush=True)
        try:
            if process_book(book, rotator, batch_pages, dpi):
                ok += 1
        except Exception as e:
            print(f'  ❌ unhandled: {e}', flush=True)
        rotator.reset()  # fresh key cycle per book
    print(f'\n──── Done. {ok}/{len(targets)} books OCR\'d, elapsed {(time.time()-t0)/60:.1f}min ────', flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status')
    rp = sub.add_parser('run')
    rp.add_argument('--book', action='append', default=[])
    rp.add_argument('--batch-pages', type=int, default=DEFAULT_BATCH_PAGES)
    rp.add_argument('--dpi', type=int, default=DEFAULT_DPI)
    rp.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()

    if args.cmd == 'status':
        cmd_status()
    elif args.cmd == 'run':
        cmd_run(args.book or None, args.batch_pages, args.dpi, args.limit)


if __name__ == '__main__':
    main()
