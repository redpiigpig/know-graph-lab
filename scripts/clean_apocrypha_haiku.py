"""
Send apocrypha_sections (cct_zh) through Claude Haiku 4.5 to fix character-level
OCR errors that regex-cleanup can't reach:

  • 默示 → 服示 / 歐示 / 做示 / 敢示 / 毆示 / 敵示 (the most pervasive variant)
  • 「」 → -···- / 「···」 → o J / 0 J  (quote marks <-> Latin letters)
  • garbled words (使國位 → 便西拉, etc.) — model fixes via Chinese-language context
  • leftover simplified glyphs from the original PDF embed

Strategy:
  • Batch ~12 sections per Haiku call (≈ 2.5K chars), bounded by --batch-size.
  • Each batch packed with `###S{idx}###` separators so we can parse the response.
  • Strict system prompt instructs model to return ONLY cleaned text, preserve
    verse numbers, no commentary.
  • Idempotent: tracks `text_haiku_cleaned` flag on each row; resumable.
  • On any parse mismatch, the batch is rolled back and individually retried
    one-at-a-time so a single bad row can't kill the run.

Usage:
  python -X utf8 scripts/clean_apocrypha_haiku.py status
  python -X utf8 scripts/clean_apocrypha_haiku.py run [--limit N] [--batch-size 12]
  python -X utf8 scripts/clean_apocrypha_haiku.py run --doc gthom        # only one doc
  python -X utf8 scripts/clean_apocrypha_haiku.py reset                  # wipe progress flag
"""
from __future__ import annotations
import os, sys, json, time, argparse, subprocess, re
import requests
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ['SUPABASE_URL']
PROJECT_REF = SUPABASE_URL.split('//')[1].split('.')[0]
ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def _resolve_claude_bin() -> str:
    """Windows ships `claude.cmd`; subprocess won't auto-resolve. Look it up."""
    if sys.platform == 'win32':
        for cand in [
            os.path.expandvars(r'%APPDATA%\npm\claude.cmd'),
            os.path.expandvars(r'%APPDATA%\npm\claude.ps1'),
        ]:
            if os.path.exists(cand):
                return cand
    return 'claude'


CLAUDE_BIN = _resolve_claude_bin()
MODEL = 'haiku'        # alias → claude-haiku-4-5

SYSTEM_PROMPT = """繁體中文 OCR 校正＋潤稿引擎。

輸入若干段繁體中文（1990 年代基督教典外文獻 PDF text-extract），以 ###S{n}### 標記分隔。回傳 JSON 物件 `{"cleaned":[...]}`，cleaned 陣列依輸入順序放修正後的每段文字（不含 ###S{n}### 標記本身）。

任務目標：把 OCR 雜訊高的中文典外文獻文本，整理成讀者易讀的繁體中文版面，但**結構必須保留**。

修正範圍：
1. **同字異 OCR 統一**：服示 / 歐示 / 做示 / 敢示 / 毆示 / 敵示 / 數示 / 教示 等 OCR 變體統一回原意（如「啟示文學」「啟示錄」）。「使國位 / 使西拉 / 便古拉 / 便商拉 / 便茜拉 / 便茵拉 / 便哥拉」統一回「便西拉」。「以諸」「以諸一書」「以諸二書」「以諸三書」是 OCR 誤讀，正確為「以諾」「以諾一書」「以諾二書」「以諾三書」。其他類似形似字一併修正。
2. **標點修復**：句末孤立 o / 0 → 。；句末 o J → 。」；句首孤立 - → 「；半角拆出的 > < → 《》。
3. **簡體 → 繁體**：殘留簡體一律繁體（台港標準）。
4. **拋棄 OCR 雜訊**：純亂碼字、單獨一行的 OCR 殘字、無意義符號可移除。
5. **verse 編號**：保留阿拉伯數字 verse 編號（1、2、7、8、12 1 等），可把編號與其後的內文合併成一行（如「1 王要公義」）。

**結構保留（嚴格）**：
- 卷次（卷一、卷二、卷三 等）**必須保留各自獨立**，不可合併多卷為一句。
- 書名（《以諾一書》《以諾二書》《以諾三書》《禧年書》等）**必須個別保留**，每一本書要能識別。
- 列表型內容（每一行原本是一個書目／條目）必須維持換行，不可串成連續散文。
- 副題、章節標題、段落標題必須保留為獨立行。

嚴禁：
- 不要把多個卷次／書目合併為一句（例：禁止「卷一《以諾一書》、卷二《以諾二書》、卷三《以諾三書》」這種串句）。
- 不要加說明、前言、結語、emoji、markdown 標題。
- 不要刪除實質內容（人名、地名、敘事、教義論述）。
- 不要任意改譯神學名詞（教父名、聖經人名、神學術語）。

few-shot：
輸入 ###S0### 華人信徒對歐示文學有理解
回傳 {"cleaned":["華人信徒對啟示文學有理解"]}

輸入 ###S0### 卷一\\n(以諸一書〉\\n(1 Enoch)\\n卷二\\n(以諸二書〉\\n(2 Enoch)
回傳 {"cleaned":["卷一\\n《以諾一書》\\n(1 Enoch)\\n卷二\\n《以諾二書》\\n(2 Enoch)"]}"""


# JSON schema constrains Haiku's output to a parseable shape.
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "cleaned": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["cleaned"],
    "additionalProperties": False,
}


# ── DB helpers ─────────────────────────────────────────────────────────
def mgmt_query(sql: str):
    """Run arbitrary SQL via Supabase Management API."""
    r = requests.post(
        f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
        headers={'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        json={'query': sql},
        timeout=60,
    )
    r.raise_for_status()
    return r.json() if r.text else []


def fetch_pending(limit: int | None, doc_slug: str | None) -> list[dict]:
    """Pull rows that still need cleaning, ordered by doc / order_index."""
    where = "WHERE version_code='cct_zh' AND text_haiku_cleaned = FALSE"
    if doc_slug:
        where += f" AND doc_slug = '{doc_slug}'"
    sql = f"""
SELECT id, doc_slug, order_index, text
FROM apocrypha_sections
{where}
ORDER BY doc_slug, order_index
{f'LIMIT {limit}' if limit else ''}
"""
    return mgmt_query(sql)


def update_row(row_id: int, new_text: str, original_text: str):
    """Save cleaned text + preserve original snapshot. Uses PostgREST PATCH."""
    url = f"{SUPABASE_URL}/rest/v1/apocrypha_sections?id=eq.{row_id}"
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }
    payload = {
        'text': new_text,
        'char_count': len(new_text),
        'text_haiku_cleaned': True,
        'text_pre_haiku': original_text,
    }
    r = requests.patch(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()


def mark_cleaned(row_id: int):
    """Mark a row as cleaned without text update (for failure-skip cases)."""
    url = f"{SUPABASE_URL}/rest/v1/apocrypha_sections?id=eq.{row_id}"
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }
    r = requests.patch(url, headers=headers, data=json.dumps({'text_haiku_cleaned': True}))
    r.raise_for_status()


# ── Haiku call ─────────────────────────────────────────────────────────
def call_haiku(prompt_text: str, timeout: int = 240) -> list[str] | None:
    """Invoke claude haiku via subprocess. Returns parsed cleaned[] or None on failure.

    Uses --output-format json + --json-schema to force the model into a
    structured response. The conversational `result` field is ignored — we
    read `structured_output.cleaned` which is schema-constrained.
    Runs cwd from c:\\tmp so the project's CLAUDE.md / auto-memory don't bleed
    into Claude Code's default user-message context.
    """
    cmd = [
        CLAUDE_BIN,
        '-p',
        '--model', MODEL,
        '--disable-slash-commands',
        '--output-format', 'json',
        '--json-schema', json.dumps(OUTPUT_SCHEMA),
        '--system-prompt', SYSTEM_PROMPT,
        '--allowedTools', '',
    ]
    cwd = r'c:\tmp' if sys.platform == 'win32' else '/tmp'
    proc = subprocess.run(
        cmd,
        input=prompt_text,
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=timeout,
        shell=False,
        cwd=cwd,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'claude exit {proc.returncode}: {proc.stderr[:400]}')

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        # Sometimes Claude Code emits non-JSON when it errors out
        return None

    structured = payload.get('structured_output') or {}
    cleaned = structured.get('cleaned')
    if not isinstance(cleaned, list):
        return None
    # Each entry must be a string
    if not all(isinstance(c, str) for c in cleaned):
        return None
    return cleaned


def pack_batch(rows: list[dict]) -> str:
    """Combine rows with separator markers."""
    parts = []
    for i, r in enumerate(rows):
        parts.append(f'###S{i}###')
        parts.append(r['text'])
    return '\n'.join(parts)


# ── Driver ─────────────────────────────────────────────────────────────
def process_batch(rows: list[dict]) -> tuple[int, int]:
    """Returns (n_updated, n_failed)."""
    prompt = pack_batch(rows)
    try:
        cleaned = call_haiku(prompt)
    except Exception as e:
        print(f'    Haiku call failed: {e}', flush=True)
        return 0, len(rows)

    # Schema-constrained response must produce a list, and its length must match.
    if cleaned is None or len(cleaned) != len(rows):
        print(f'    Got {len(cleaned) if cleaned else "?"} items, expected {len(rows)} — '
              f'retrying {len(rows)} rows individually', flush=True)
        good = 0
        bad = 0
        for r in rows:
            try:
                p = pack_batch([r])
                cl = call_haiku(p)
                if cl is None or len(cl) != 1 or not cl[0]:
                    mark_cleaned(r['id'])
                    bad += 1
                    continue
                update_row(r['id'], cl[0], r['text'])
                good += 1
            except Exception as e:
                print(f'      row {r["id"]} retry failed: {e}', flush=True)
                bad += 1
        return good, bad

    good = 0
    bad = 0
    for r, new_text in zip(rows, cleaned):
        if not new_text or len(new_text) < max(8, len(r['text']) // 5):
            # Suspicious shrinkage — skip and mark to avoid retry loop
            print(f'    row {r["id"]}: cleaned text suspiciously short '
                  f'({len(r["text"])}→{len(new_text)}), marking clean to skip', flush=True)
            mark_cleaned(r['id'])
            bad += 1
            continue
        try:
            update_row(r['id'], new_text, r['text'])
            good += 1
        except Exception as e:
            print(f'    row {r["id"]} PATCH failed: {e}', flush=True)
            bad += 1
    return good, bad


def cmd_status():
    rows = mgmt_query("""
SELECT
  COUNT(*) FILTER (WHERE text_haiku_cleaned = TRUE)  AS cleaned,
  COUNT(*) FILTER (WHERE text_haiku_cleaned = FALSE) AS pending,
  COUNT(*)                                           AS total
FROM apocrypha_sections WHERE version_code = 'cct_zh'
""")
    if rows:
        print(json.dumps(rows[0], ensure_ascii=False))

    rows2 = mgmt_query("""
SELECT doc_slug,
  COUNT(*) FILTER (WHERE text_haiku_cleaned = TRUE)  AS cleaned,
  COUNT(*) FILTER (WHERE text_haiku_cleaned = FALSE) AS pending
FROM apocrypha_sections WHERE version_code = 'cct_zh'
GROUP BY doc_slug
HAVING COUNT(*) FILTER (WHERE text_haiku_cleaned = FALSE) > 0
ORDER BY pending DESC LIMIT 15
""")
    print('\nTop pending docs:')
    for r in rows2:
        print(f'  {r["doc_slug"]:30s} cleaned={r["cleaned"]:5d} pending={r["pending"]:5d}')


def cmd_reset():
    print('Resetting all text_haiku_cleaned flags…')
    mgmt_query("UPDATE apocrypha_sections SET text_haiku_cleaned = FALSE WHERE version_code = 'cct_zh'")
    print('done.')


def cmd_run(limit: int | None, batch_size: int, doc_slug: str | None):
    print(f'Fetching pending rows (limit={limit}, doc={doc_slug or "ALL"}) …', flush=True)
    rows = fetch_pending(limit=limit, doc_slug=doc_slug)
    print(f'  {len(rows)} rows pending', flush=True)
    if not rows:
        return

    t0 = time.time()
    total_good = 0
    total_bad = 0

    for batch_start in range(0, len(rows), batch_size):
        batch = rows[batch_start:batch_start + batch_size]
        elapsed = time.time() - t0
        done = batch_start
        eta_s = (len(rows) - done) * (elapsed / max(done, 1)) if done > 0 else 0
        print(
            f'\n[batch {batch_start // batch_size + 1}/{(len(rows) + batch_size - 1) // batch_size}] '
            f'rows {batch_start}-{batch_start + len(batch)} '
            f'(done {done}/{len(rows)}, elapsed {elapsed:.0f}s, ETA {eta_s/60:.1f}min)',
            flush=True,
        )
        good, bad = process_batch(batch)
        total_good += good
        total_bad += bad
        print(f'  → updated={good} failed={bad}', flush=True)

    print(f'\n──── Done. total updated={total_good} failed={total_bad} '
          f'elapsed={time.time() - t0:.0f}s ────', flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status')
    sub.add_parser('reset')
    rp = sub.add_parser('run')
    rp.add_argument('--limit', type=int, default=None)
    rp.add_argument('--batch-size', type=int, default=12)
    rp.add_argument('--doc', type=str, default=None)
    args = ap.parse_args()

    if args.cmd == 'status':
        cmd_status()
    elif args.cmd == 'reset':
        cmd_reset()
    elif args.cmd == 'run':
        cmd_run(args.limit, args.batch_size, args.doc)


if __name__ == '__main__':
    main()
