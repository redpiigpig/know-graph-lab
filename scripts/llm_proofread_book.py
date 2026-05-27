"""Per-chunk LLM proofreader using Haiku 4.5.

Catches what static rules can't — things like:
  - Body content that visibly belongs to a different work (post-h3 cross-bleed)
  - Term inconsistencies (the LLM noticed the book uses both 哥林多 and 科林斯)
  - Translation drift from source (paragraph N's ZH doesn't say what its EN does)
  - Heading mis-labeling (an h3 reads「帕皮亞殘篇」but body is about Justin Martyr)
  - Footnote attribution oddities

The static T9 NCX-driven scanner catches structural cross-bleed; this LLM
pass catches the「smells weird」cases that need semantic understanding.

Each chunk costs ~$0.001 with Haiku-4.5 (chunk avg 3K tokens input + 500
out → ~$0.001 input + $0.002 output ≈ $0.003). A 112-chunk book runs
about $0.30.

Usage:
    python scripts/llm_proofread_book.py <ebook_id>
    python scripts/llm_proofread_book.py <ebook_id> --limit 5     # test a few
    python scripts/llm_proofread_book.py <ebook_id> --start 50    # resume
    python scripts/llm_proofread_book.py <ebook_id> --workers 4   # parallel
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
# Reuse the credential / client plumbing already battle-tested by the
# translator — same OAuth / API-key handling, same auto-refresh.
from translate_ebook_to_zh import (  # noqa: E402
    HAIKU_MODEL, _refresh_anthropic_client_if_creds_changed,
)
import translate_ebook_to_zh as tezh  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

PROOFREAD_PROMPT = """你是電子書翻譯校對員。下面是一本繁體中文電子書的某一頁，這頁屬於：

書名：{title}
本頁卷別：{volume}
本頁章節：{chapter_path}

請檢查這頁是否有以下問題（只報告真實存在的問題，不要編造）：

1. **內容歸屬錯誤**：頁面中出現的內文明顯不屬於上述卷別（例如：本頁應該是「帕皮亞殘篇」但出現了猶斯定生平介紹）。指出哪段內文不屬於這裡，應該屬於什麼。
2. **小標題不對**：標題（### / ####）跟它下面的內文主題不符。例如標題說「帕皮亞殘篇」但下面是 Justin Martyr 內容。
3. **名詞前後不一致**：同一個人物／地名／作品在這頁內用了兩種譯法（如「哥林多」和「科林斯」、「丟格那妥」和「狄奧格尼」）。列出衝突的譯法。
4. **明顯翻譯離原文太遠**：跟英文原文對照看，某段中譯的意思跟英文不一樣（不是用字差異，而是意思不同）。
5. **註釋編號異常**：(N) 編號錯亂、缺號、或順序不對。
6. **其他語義或結構異常**：你覺得讀起來怪怪的任何地方。

**回應格式（嚴格 JSON，不要 markdown 也不要任何說明）**：

{{
  "issues": [
    {{"type": "ATTRIBUTION|HEADING|TERM|TRANSLATION|FOOTNOTE|OTHER",
      "severity": "WARN|INFO",
      "snippet": "出問題的字串前 30 字",
      "description": "20 字內描述問題"}}
  ]
}}

如果這頁完全乾淨，回 `{{"issues": []}}`。

---

【中譯內文】

{zh_content}

{en_block}
"""


def proofread_chunk(c: dict, book: dict) -> dict:
    """Send one chunk to Haiku and return parsed issues. On API error,
    returns {"error": "..."}; on parse error, returns the raw output for
    debugging."""
    zh = (c.get("content") or "").strip()
    en = (c.get("source_text") or "").strip()
    if not zh:
        return {"chunk_index": c.get("chunk_index"), "issues": []}
    # Truncate aggressively — Haiku context is 200K but we don't need to
    # send the whole chunk for proofreading. Take a representative sample:
    # head 6K + tail 4K covers most cross-bleed patterns (tail is where
    # bled-in next-letter intros tend to sit).
    if len(zh) > 10_000:
        zh = zh[:6000] + "\n\n[...]\n\n" + zh[-4000:]
    if len(en) > 10_000:
        en = en[:6000] + "\n\n[...]\n\n" + en[-4000:]
    en_block = f"【英文原文】\n\n{en}" if en else ""

    prompt = PROOFREAD_PROMPT.format(
        title=book.get("title", ""),
        volume=c.get("volume") or "（無）",
        chapter_path=c.get("chapter_path", ""),
        zh_content=zh,
        en_block=en_block,
    )

    _refresh_anthropic_client_if_creds_changed()
    for attempt in range(3):
        try:
            msg = tezh._anthropic_client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
            # Strip markdown fence if Haiku added one
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```\s*$", "", text)
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                # Try to extract first JSON object via brace matching
                m = re.search(r"\{[\s\S]*\}", text)
                parsed = json.loads(m.group(0)) if m else {"issues": [], "raw": text}
            return {
                "chunk_index": c.get("chunk_index"),
                "chapter_path": c.get("chapter_path"),
                "issues": parsed.get("issues", []),
            }
        except Exception as e:
            if attempt == 2:
                return {"chunk_index": c.get("chunk_index"),
                        "issues": [], "error": str(e)}
            time.sleep(2 ** attempt * 5)  # 5s, 10s
    return {"chunk_index": c.get("chunk_index"), "issues": []}


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4,
                    help="Parallel API calls; Haiku has generous RPM.")
    ap.add_argument("--out", default=None,
                    help="JSON report path; default scripts/logs/proofread_<id>.json")
    args = ap.parse_args()

    book = fetch_book(args.ebook_id)
    jsonl = CHUNKS_DIR / f"{args.ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l]
    if args.limit:
        chunks_to_check = chunks[args.start:args.start + args.limit]
    else:
        chunks_to_check = chunks[args.start:]
    print(f"Book: {book['title']}")
    print(f"Proofreading {len(chunks_to_check)} chunks (offset {args.start})")
    print(f"Workers: {args.workers}")

    out_path = Path(args.out) if args.out else ROOT / "scripts" / "logs" / f"proofread_{args.ebook_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(proofread_chunk, c, book): c for c in chunks_to_check}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            done += 1
            if res.get("issues") or res.get("error"):
                marker = "⚠" if res.get("issues") else "✗"
                n = len(res.get("issues", []))
                err = f" err={res['error'][:40]}" if res.get("error") else ""
                print(f"  {marker} chunk {res['chunk_index']:3d} "
                      f"({res.get('chapter_path','')[:25]:25s}): {n} issues{err}")
            if done % 20 == 0:
                rate = done / max(time.time() - t0, 0.1)
                eta = (len(chunks_to_check) - done) / max(rate, 0.01)
                print(f"  ... progress {done}/{len(chunks_to_check)} "
                      f"({rate:.1f}/s, ETA {eta/60:.1f} min)")

    # Sort by chunk_index for stable output
    results.sort(key=lambda r: r.get("chunk_index", -1))

    # Write JSON report
    out_path.write_text(
        json.dumps({"ebook_id": args.ebook_id, "title": book["title"],
                    "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n✓ wrote report: {out_path}")

    # Print summary
    total_issues = sum(len(r.get("issues", [])) for r in results)
    chunks_with_issues = sum(1 for r in results if r.get("issues"))
    chunks_with_errors = sum(1 for r in results if r.get("error"))
    print(f"\nSummary: {total_issues} issues in {chunks_with_issues} chunks "
          f"({chunks_with_errors} API errors)")
    # Group by type
    type_counts: dict[str, int] = {}
    for r in results:
        for iss in r.get("issues", []):
            t = iss.get("type", "OTHER")
            type_counts[t] = type_counts.get(t, 0) + 1
    if type_counts:
        print("By type:")
        for t, n in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
