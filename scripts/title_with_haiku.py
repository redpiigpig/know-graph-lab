"""
Batch-generate titles for ai_dialogues entries where title IS NULL,
using Claude Haiku 4.5. Idempotent — safe to re-run; only touches rows
without titles.

Default target is Gemini (since Gemini exports lack titles entirely).
Can also backfill the ~8500 ChatGPT rows that came from the older
text-format import and never got titled.

PREREQ:
  - Add ANTHROPIC_API_KEY=sk-ant-... to .env (or export it)
  - pip show anthropic  # should be installed (>= 0.40)

USAGE:
  python scripts/title_with_haiku.py                    # all NULL Gemini rows
  python scripts/title_with_haiku.py --limit 5          # smoke test 5 rows
  python scripts/title_with_haiku.py --source chatgpt   # back-fill leftover ChatGPT
  python scripts/title_with_haiku.py --concurrency 12   # tune throughput

COST ESTIMATE (Haiku 4.5: $1/MTok input, $5/MTok output):
  ~2600 Gemini rows × ~1000 input tok + ~15 output tok ≈ $2.7 total
  ~8500 ChatGPT rows ≈ $9 total
"""

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

import requests
import anthropic

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent


def _load_env():
    env = dict(os.environ)
    env_path = ROOT / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip())
    return env


ENV = _load_env()
SUPABASE_URL = ENV["SUPABASE_URL"]
SERVICE_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
ACCESS_TOKEN = ENV["SUPABASE_ACCESS_TOKEN"]
PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0]
# Try to get ANTHROPIC_KEY from env, fall back to None (uses default auth)
ANTHROPIC_KEY = ENV.get("ANTHROPIC_API_KEY")

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 64

SYSTEM = (
    "你是對話標題生成器。讀完使用者問題與 AI 回答後，產生 6~12 個繁體中文字、"
    "可作為對話標題的短語。\n\n"
    "嚴格規則：\n"
    "1. 只輸出標題本身，不要加引號、句號、換行、解釋、Markdown 標記。\n"
    "2. 不要使用「關於…」「討論…」「解析…」這類空泛開頭。直接點出主題。\n"
    "3. 範例好標題：「卡巴拉與否定神學」、「弘誓青年會運作困境」、"
    "「Vue 元件樣式調整」、「主體性倫理學綜述」。\n"
    "4. 程式碼/技術問題用具體技術詞，例：「TypeScript 型別錯誤排查」。\n"
    "5. 若內容過短或無法判斷主題，輸出：（無主題）"
)


def sql_lit(s):
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


def run_sql(sql, retries=3):
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    for attempt in range(retries):
        try:
            resp = requests.post(
                url,
                json={"query": sql},
                headers={
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
                timeout=60,
            )
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise SystemExit(f"SQL connection failed: {e}")
            time.sleep(2 ** attempt)
            continue
        if resp.status_code in (200, 201):
            try:
                return resp.json()
            except Exception:
                return []
        if attempt < retries - 1:
            print(f"  SQL retry ({resp.status_code}: {resp.text[:120]})")
            time.sleep(2 ** attempt)
            continue
        raise SystemExit(f"SQL failed {resp.status_code}: {resp.text[:300]}")


def fetch_pending(table, limit):
    lim = f"LIMIT {int(limit)}" if limit else ""
    sql = f"""
SELECT id::text AS id,
       LEFT(prompt, 1500) AS prompt,
       LEFT(COALESCE(response,''), 800) AS response
FROM {table}
WHERE title IS NULL
ORDER BY dialogue_time DESC NULLS LAST
{lim};
"""
    return run_sql(sql)


def update_titles_batch(table, rows):
    """rows: list of (id_uuid_str, title_str)"""
    if not rows:
        return
    values = ",\n      ".join(
        f"({sql_lit(rid)}::uuid, {sql_lit(title)})" for rid, title in rows
    )
    sql = f"""
UPDATE {table} AS d
SET title = v.t
FROM (VALUES
      {values}
) AS v(id, t)
WHERE d.id = v.id;
"""
    run_sql(sql)


def sanitize_title(raw):
    if not raw:
        return None
    t = raw.strip()
    # strip wrapping punctuation Claude sometimes adds
    for pair in ['""', "''", "「」", "『』", "《》", "[]", "()", "（）"]:
        if len(t) >= 2 and t[0] == pair[0] and t[-1] == pair[1]:
            t = t[1:-1].strip()
    t = t.strip(" \"'`。．.\n\r\t")
    # multiline → first non-empty line only
    for line in t.splitlines():
        line = line.strip()
        if line:
            t = line
            break
    if len(t) > 30:
        t = t[:30]
    return t or None


async def title_one(client, sem, row, retry_log):
    prompt_text = row.get("prompt") or ""
    response_text = row.get("response") or ""
    user_msg = (
        f"使用者問題：\n{prompt_text}\n\n"
        f"---\n\nAI 回答（節錄）：\n{response_text}\n\n"
        f"---\n\n請輸出 6~12 字繁體中文標題："
    )
    async with sem:
        for attempt in range(3):
            try:
                resp = await client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM,
                    messages=[{"role": "user", "content": user_msg}],
                )
                raw = "".join(
                    b.text for b in resp.content if getattr(b, "type", None) == "text"
                )
                title = sanitize_title(raw)
                return row["id"], title, resp.usage
            except anthropic.RateLimitError:
                wait = 5 * (attempt + 1)
                retry_log.append(f"  429 on {row['id'][:8]}, sleep {wait}s")
                await asyncio.sleep(wait)
            except anthropic.APIError as e:
                if attempt == 2:
                    retry_log.append(f"  GIVE UP {row['id'][:8]}: {e}")
                    return row["id"], None, None
                await asyncio.sleep(2 ** attempt)
        return row["id"], None, None


async def main_async(table, limit, concurrency, flush):
    print(f"🔍 fetching pending rows from {table} (limit={limit or 'all'})...")
    rows = fetch_pending(table, limit)
    print(f"   {len(rows)} rows to title\n")
    if not rows:
        return

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_KEY)
    sem = asyncio.Semaphore(concurrency)
    retry_log = []

    completed = 0
    buffer = []
    samples = []  # first 5 (id, title) for visual sanity check
    total_in = 0
    total_out = 0
    failed = 0

    started = time.monotonic()

    tasks = [
        asyncio.create_task(title_one(client, sem, row, retry_log)) for row in rows
    ]

    for fut in asyncio.as_completed(tasks):
        rid, title, usage = await fut
        completed += 1
        if usage:
            total_in += usage.input_tokens
            total_out += usage.output_tokens
        if title:
            buffer.append((rid, title))
            if len(samples) < 5:
                samples.append((rid[:8], title))
        else:
            failed += 1

        if len(buffer) >= flush:
            update_titles_batch(table, buffer)
            elapsed = time.monotonic() - started
            rate = completed / max(elapsed, 1e-6)
            eta = (len(rows) - completed) / max(rate, 1e-6)
            print(
                f"   ✅ {completed}/{len(rows)}  saved {len(buffer)}  "
                f"({rate:.1f}/s, ETA {eta:.0f}s)"
            )
            buffer.clear()

    if buffer:
        update_titles_batch(table, buffer)
        print(f"   ✅ {completed}/{len(rows)}  saved {len(buffer)} (final flush)")

    elapsed = time.monotonic() - started
    cost_in = total_in / 1_000_000 * 1.00
    cost_out = total_out / 1_000_000 * 5.00
    print(f"\n📊 done in {elapsed:.0f}s")
    print(f"   tokens: in={total_in:,}  out={total_out:,}")
    print(f"   cost:   ${cost_in:.4f} + ${cost_out:.4f} = ${cost_in + cost_out:.4f}")
    print(f"   failed: {failed}")
    if retry_log:
        print(f"\n⚠️  {len(retry_log)} retries/errors:")
        for line in retry_log[:20]:
            print(line)
        if len(retry_log) > 20:
            print(f"   ... and {len(retry_log) - 20} more")

    if samples:
        print("\n🔍 sample titles (first 5):")
        for rid, t in samples:
            print(f"   [{rid}]  {t}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--source",
        default="gemini",
        choices=["gemini", "chatgpt"],
        help="which table to process (default: gemini)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="cap rows processed (use 5 or 10 for a smoke test first)",
    )
    ap.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="parallel API calls (default 8; raise to 16+ if rate limit allows)",
    )
    ap.add_argument(
        "--flush",
        type=int,
        default=20,
        help="write partial progress every N completions (default 20)",
    )
    args = ap.parse_args()

    table = f"ai_dialogues_{args.source}"
    asyncio.run(main_async(table, args.limit, args.concurrency, args.flush))


if __name__ == "__main__":
    main()
