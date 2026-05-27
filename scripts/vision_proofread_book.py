"""Haiku Vision proofreader. Pairs with `screenshot_book.mjs` —

  1. node scripts/screenshot_book.mjs --ebook <id>            # captures PNG/page
  2. python scripts/vision_proofread_book.py --ebook <id>     # Vision pass

Catches RENDER-LEVEL bugs the text scanners can't see:
  - Font / sizing anomalies (body content shown in tiny footnote font)
  - Mislabeled section that visually masquerades as one (h3 saying X but
    paragraph immediately under is clearly Y)
  - Layout glitches (overlap, broken columns)
  - Missing content (white box where text should be)

Per-page cost ≈ $0.005 with Haiku-4.5 vision. A 112-page book runs ~$0.50.

Usage:
  python scripts/vision_proofread_book.py --ebook <id>
  python scripts/vision_proofread_book.py --ebook <id> --pages 47-49
  python scripts/vision_proofread_book.py --ebook <id> --workers 4
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
from translate_ebook_to_zh import (  # noqa: E402
    HAIKU_MODEL, _refresh_anthropic_client_if_creds_changed,
)
import translate_ebook_to_zh as tezh  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

VISION_PROMPT = """你是電子書渲染品質檢查員。下圖是電子書 reader 的一頁截圖。

書名：{title}
本頁卷別：{volume}
本頁標題：{chapter_path}

請以視覺判斷有沒有以下問題（只報告真實存在的）：

1. **內容歸屬錯誤**：標題說的是 A 卷，但底下文字明顯講的是 B 卷的內容。
2. **小標題不符**：標題（粗體大字）跟下面那段內文的主題不一致。
3. **註釋字級異常**：本應該是正文的段落卻用了註釋的小字級，或反之。
4. **排版錯亂**：段落被切錯、欄位錯位、空白方塊、文字重疊、超出邊界。
5. **大量內文跑進註釋區**：分隔線下方應該只有 (N) 開頭的註釋，卻有大段正文。
6. **缺漏**：英文欄有但中文欄空著（或反之），同段文字位置應該對齊但沒有。
7. **頁尾異常**：頁尾有非預期的文字（書名重複、編者註等不該出現）。

**嚴格 JSON 格式**：

{{
  "issues": [
    {{"type": "ATTRIBUTION|HEADING|FONT|LAYOUT|FOOTNOTE_BLEED|MISSING|FOOTER|OTHER",
      "severity": "WARN|INFO",
      "where": "頁面位置（如『中段』『右欄底部』）",
      "description": "20 字內描述"}}
  ]
}}

頁面完全乾淨 → `{{"issues": []}}`。
"""


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    return r.json()[0]


def vision_check_page(page_num: int, img_path: Path, book: dict, chunks: list[dict]) -> dict:
    """Send one screenshot to Haiku Vision; return parsed issues."""
    # Accept either .jpg (current) or .png (legacy) suffix
    if not img_path.exists():
        alt = img_path.with_suffix(".png" if img_path.suffix == ".jpg" else ".jpg")
        if alt.exists():
            img_path = alt
        else:
            return {"page": page_num, "issues": [], "error": "missing screenshot"}
    img_bytes = img_path.read_bytes()
    if len(img_bytes) > 4_500_000:
        return {"page": page_num, "issues": [],
                "error": f"image too large ({len(img_bytes)//1024} KB)"}
    img_b64 = base64.standard_b64encode(img_bytes).decode("ascii")
    media_type = "image/jpeg" if img_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"

    c = chunks[page_num - 1] if 0 < page_num <= len(chunks) else {}
    prompt = VISION_PROMPT.format(
        title=book.get("title", ""),
        volume=c.get("volume") or "（無）",
        chapter_path=c.get("chapter_path", ""),
    )

    _refresh_anthropic_client_if_creds_changed()
    for attempt in range(3):
        try:
            msg = tezh._anthropic_client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {
                            "type": "base64", "media_type": media_type,
                            "data": img_b64}},
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
            text = "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```\s*$", "", text)
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                m = re.search(r"\{[\s\S]*\}", text)
                parsed = json.loads(m.group(0)) if m else {"issues": [], "raw": text}
            return {
                "page": page_num,
                "chapter_path": c.get("chapter_path"),
                "issues": parsed.get("issues", []),
            }
        except Exception as e:
            if attempt == 2:
                return {"page": page_num, "issues": [], "error": str(e)}
            time.sleep(2 ** attempt * 5)
    return {"page": page_num, "issues": []}


def parse_pages_arg(s: str, total: int) -> list[int]:
    out: list[int] = []
    for part in s.split(","):
        m = re.match(r"^(\d+)-(\d+)$", part)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.strip().isdigit():
            out.append(int(part))
    return [p for p in out if 1 <= p <= total]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ebook", required=True)
    ap.add_argument("--pages", default=None, help="e.g. 1-20 or 5,12,15")
    ap.add_argument("--workers", type=int, default=3,
                    help="Parallel Vision API calls.")
    ap.add_argument("--shots-dir", default=None,
                    help="Defaults to c:/tmp/proofread_<ebook_prefix>/")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    book = fetch_book(args.ebook)
    jsonl = CHUNKS_DIR / f"{args.ebook}.jsonl"
    chunks = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l]
    total = len(chunks)
    shots_dir = Path(args.shots_dir or f"c:/tmp/proofread_{args.ebook[:8]}")
    if not shots_dir.exists():
        sys.exit(f"shots dir not found: {shots_dir}\n"
                 f"Run first: node scripts/screenshot_book.mjs --ebook {args.ebook}")

    pages = parse_pages_arg(args.pages, total) if args.pages else list(range(1, total + 1))
    print(f"Book: {book['title']}")
    print(f"Vision proofreading {len(pages)} pages from {shots_dir}")
    print(f"Workers: {args.workers}")

    out_path = Path(args.out) if args.out else ROOT / "scripts" / "logs" / f"vision_proofread_{args.ebook}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {
            ex.submit(vision_check_page, p,
                      shots_dir / f"p{str(p).zfill(3)}.png", book, chunks): p
            for p in pages
        }
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            done += 1
            if res.get("issues") or res.get("error"):
                marker = "⚠" if res.get("issues") else "✗"
                n = len(res.get("issues", []))
                err = f" err={res['error'][:40]}" if res.get("error") else ""
                print(f"  {marker} p{res['page']:3d} "
                      f"({res.get('chapter_path','')[:25]:25s}): {n} issues{err}")
            if done % 10 == 0:
                rate = done / max(time.time() - t0, 0.1)
                eta = (len(pages) - done) / max(rate, 0.01)
                print(f"  ... {done}/{len(pages)} ({rate:.1f}/s, ETA {eta/60:.1f}m)")

    results.sort(key=lambda r: r["page"])
    out_path.write_text(
        json.dumps({"ebook_id": args.ebook, "title": book["title"],
                    "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n✓ wrote: {out_path}")

    total_issues = sum(len(r.get("issues", [])) for r in results)
    pages_with_issues = sum(1 for r in results if r.get("issues"))
    errors = sum(1 for r in results if r.get("error"))
    print(f"\nSummary: {total_issues} visual issues on {pages_with_issues} pages "
          f"({errors} API errors)")
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
