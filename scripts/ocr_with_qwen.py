#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Qwen2.5-VL OCR fallback for when Gemini's daily quota is exhausted.

Same DB / JSONL / R2 contract as ocr_with_gemini.py — picks up the SAME queue
(`ebooks` rows where parse_error LIKE '%no extractable text%'), writes pages
to local _chunks JSONL, mirrors to R2, and stamps `parsed_at`. The daily bat
only invokes this script when ocr_with_gemini.py exits with code 2 (quota hit).

Pipeline per book:
  1. fitz (PyMuPDF) renders each page at DPI=150 → JPEG bytes
  2. POST to Ollama /api/generate with the image + a Chinese-aware OCR prompt
  3. Aggregate non-empty pages, write JSONL, push to R2, update DB

Trade-offs vs Gemini:
  + No daily quota (free, unlimited)
  - 10-30s per page on RTX 4050 mobile (vs Gemini's batched whole-book call)
  - Slightly weaker on long-tail traditional Chinese characters
  → Therefore default --limit 5 in the bat: don't try to clear 391-book backlog
    locally; Qwen just keeps progress visible while waiting for Gemini quota.

Usage:
  ollama pull qwen2.5vl:3b      (one-time)
  python scripts/ocr_with_qwen.py status
  python scripts/ocr_with_qwen.py run [--limit N] [--dpi 150] [--model qwen2.5vl:3b]
"""
import argparse
import base64
import io
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing PyMuPDF. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from ocr_with_gemini import (
    fetch_ocr_targets,
    update_book_done,
    update_book_error,
    insert_chunk_previews,
    write_jsonl,
    push_to_r2,
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS = "http://localhost:11434/api/tags"
DEFAULT_MODEL = "qwen2.5vl:3b"
DEFAULT_DPI = 150
DEFAULT_LIMIT = 5  # don't try to clear backlog locally; just show progress

PAGE_PROMPT = """請將這頁書頁中的所有文字（中文與英文）按閱讀順序完整辨識輸出。

規則：
- 只輸出純文字內容，不要評論或說明
- 段落之間用換行分隔
- 雙欄排版時：先輸出左欄全部，再輸出右欄
- 傳統垂直排版時：從右上角開始，由右至左、由上至下
- 跳過頁碼、頁眉頁腳、純裝飾元素
- 看不清的字用 ▢ 取代"""


def ensure_ollama_ready(model: str) -> None:
    try:
        r = requests.get(OLLAMA_TAGS, timeout=5)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Ollama not reachable at http://localhost:11434 — {e}", file=sys.stderr)
        print("   Start it with: `ollama serve` (or just launch the Ollama app).", file=sys.stderr)
        sys.exit(1)
    names = {m.get("name", "") for m in r.json().get("models", [])}
    if not any(model == n or n.startswith(model + ":") or model.startswith(n.split(":")[0]) for n in names):
        # be lenient — qwen2.5vl:3b vs qwen2.5vl etc.
        if model not in names:
            print(f"❌ Model {model!r} not pulled. Run: ollama pull {model}", file=sys.stderr)
            sys.exit(1)


def render_page_jpeg(doc, page_idx: int, dpi: int) -> bytes:
    pix = doc[page_idx].get_pixmap(dpi=dpi)
    return pix.tobytes("jpeg")


def ocr_one_page(model: str, img_bytes: bytes, num_predict: int = 4096) -> str:
    body = {
        "model": model,
        "prompt": PAGE_PROMPT,
        "images": [base64.b64encode(img_bytes).decode()],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": num_predict},
    }
    r = requests.post(OLLAMA_URL, json=body, timeout=600)
    r.raise_for_status()
    return (r.json().get("response") or "").strip()


def process_one_qwen(book: dict, src_path: Path, model: str, dpi: int) -> dict:
    t_start = time.time()
    doc = fitz.open(src_path)
    n_pages = len(doc)
    pages = []
    page_failures = 0
    try:
        for i in range(n_pages):
            try:
                img = render_page_jpeg(doc, i, dpi)
                text = ocr_one_page(model, img)
                if text:
                    pages.append({"page": i + 1, "text": text})
                    print(".", end="", flush=True)
                else:
                    print("·", end="", flush=True)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                page_failures += 1
                print("x", end="", flush=True)
                if page_failures > max(5, n_pages // 4):
                    return {"status": "fail", "error": f"too many page failures ({page_failures}/{n_pages}): {str(e)[:120]}"}
    finally:
        doc.close()

    if not pages:
        return {"status": "fail", "error": "Qwen returned 0 usable pages"}

    total_chars = sum(len(p["text"]) for p in pages)
    jsonl_path = write_jsonl(book["id"], pages)
    insert_chunk_previews(book["id"], pages)

    r2_ok = True
    r2_err = ""
    try:
        push_to_r2(book["id"], jsonl_path)
    except Exception as e:
        r2_ok = False
        r2_err = str(e)[:200]

    if r2_ok:
        update_book_done(
            book["id"],
            total_chars=total_chars,
            chunk_count=len(pages),
            total_pages=max(p["page"] for p in pages),
        )
    else:
        update_book_error(book["id"], f"Qwen-OCR ok but R2 push failed: {r2_err}")

    elapsed = time.time() - t_start
    per_page = elapsed / max(n_pages, 1)
    tag = "✓" if r2_ok else "⚠ R2 fail"
    print(f"\n  {tag} {len(pages)}/{n_pages} pages, {total_chars // 1000}K chars, {elapsed:.0f}s ({per_page:.1f}s/page)")
    return {"status": "ok"} if r2_ok else {"status": "fail", "error": f"R2: {r2_err}"}


def cmd_status():
    targets = fetch_ocr_targets()
    print(f"OCR candidates (parse_error contains 'no extractable text'): {len(targets)}")
    print(f"Qwen would process smallest-first; default --limit {DEFAULT_LIMIT} per run.")


def cmd_run(limit: int, model: str, dpi: int):
    ensure_ollama_ready(model)
    targets = fetch_ocr_targets()
    print(f"OCR candidates: {len(targets)}")
    if limit:
        targets = targets[:limit]
    if not targets:
        print("Nothing to do.")
        return

    ok = 0
    failed = []
    for i, b in enumerate(targets, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [{i:3d}/{len(targets)}] ⚠ source missing: {src}", file=sys.stderr)
            update_book_error(b["id"], f"file not found: {src}")
            failed.append((b["title"], "source missing"))
            continue

        title_short = (b["title"] or src.stem)[:40]
        sz_mb = src.stat().st_size / 1024 / 1024
        print(f"  [{i:3d}/{len(targets)}] Qwen-OCR  {title_short}  ({sz_mb:.1f} MB)")

        try:
            result = process_one_qwen(b, src, model, dpi)
        except KeyboardInterrupt:
            print("\n⚠ interrupted")
            break
        except Exception as e:
            print(f"\n  ❌ {str(e)[:200]}")
            failed.append((b["title"], str(e)[:200]))
            continue

        if result["status"] == "ok":
            ok += 1
        else:
            failed.append((b["title"], result["error"]))
            update_book_error(b["id"], f"Qwen-OCR: {result['error']}")

    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("First failures:")
        for n, e in failed[:10]:
            print(f"  - {n[:50]}  {e[:120]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["status", "run"])
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()
    if args.cmd == "status":
        cmd_status()
    else:
        cmd_run(args.limit, args.model, args.dpi)


if __name__ == "__main__":
    main()
