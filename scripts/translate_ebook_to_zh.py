"""Translate an English ebook into traditional Chinese via Gemini Flash.

Currently scoped to the ACCS Apocrypha volume — the first English source the
library acquired (2026-05-21). Pipeline:
  1. Read EPUB (cleaner than OCR txt) → ordered list of (heading, body) chunks
  2. Per chunk, call Gemini Flash with a translation prompt that enforces
     traditional-Chinese theological terminology (教父、次經、巴錄、瑪加伯…)
  3. Write Chinese markdown chunks to local _chunks/ JSONL
  4. PATCH ebooks row: parsed_at, standardized_at, chunk_count, total_chars

Usage:
  python scripts/translate_ebook_to_zh.py <ebook_id> --inspect      # dump source chunks
  python scripts/translate_ebook_to_zh.py <ebook_id> --limit 3      # smoke test 3 chunks
  python scripts/translate_ebook_to_zh.py <ebook_id>                # full run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import ebooklib
from ebooklib import epub

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent))

import standardize_ebook as se  # for URL/headers + push_to_r2 + update_db helpers
import standardize_pdf_lite as pl  # for collapse_cjk_spacing

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=representation"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# ── Gemini ────────────────────────────────────────────────────────────────

def _find_gemini_keys() -> list[str]:
    primary = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    raw = []
    for name in primary:
        v = os.environ.get(name)
        if v: raw.append(v); break
    for n in range(1, 11):
        for base in primary:
            v = os.environ.get(f"{base}_{n}")
            if v: raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_gemini_keys()
_key_idx = 0


PROMPT_TMPL = """你是基督教神學翻譯專家。把下列英文段落翻譯成「繁體中文」。

關鍵要求：
1. **嚴守繁體中文**：所有用字必須繁體。
2. **教父/教會傳統術語對齊以下標準譯法**：
   - Patristic / Church Fathers → 教父
   - Apocrypha / Deuterocanonical → 次經 / 第二正典
   - Wisdom of Solomon → 智慧篇
   - Sirach / Ecclesiasticus → 德訓篇 / 便西拉智訓
   - Tobit → 多俾亞傳 / 多比傳
   - Baruch → 巴錄
   - Judith → 友弟德傳 / 猶滴傳
   - 1-2 Maccabees → 瑪加伯上下 / 馬加比上下
   - Augustine → 奧古斯丁
   - Athanasius → 亞他那修 / 阿塔納修
   - Origen → 奧利金
   - John Chrysostom → 屈梭多模 / 金口若望
   - Cyril of Alexandria → 亞歷山大的西里爾
   - Bede → 比德
3. **保留原文 Markdown 結構**：## / ### / **粗體** / *斜體* / > 引文 / - 列表全部對應翻譯。
4. **聖經引用格式**：把英文 (1 Mac 4:18) 翻成繁體（瑪加伯上 4:18）。
5. **章節標題簡潔**：別把 "Chapter 1" 翻成囉嗦句子，直譯「第一章」即可。

只輸出翻譯後的繁體中文 markdown，不要加說明、不要 wrap 在程式碼塊裡。

--- 原文 ---

{source}
"""


def gemini_translate(source: str, model: str = "gemini-2.5-flash") -> str:
    global _key_idx
    if not GEMINI_KEYS:
        raise RuntimeError("no Gemini API key")
    body = {
        "contents": [{"parts": [{"text": PROMPT_TMPL.format(source=source)}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "text/plain"},
    }
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    while _key_idx < len(GEMINI_KEYS):
        key = GEMINI_KEYS[_key_idx]
        for attempt, wait in enumerate((0, 5, 20, 60), start=1):
            if wait:
                time.sleep(wait)
            r = requests.post(f"{base}?key={key}", json=body, timeout=180)
            if r.status_code == 200:
                data = r.json()
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    raise RuntimeError(f"unexpected Gemini response: {json.dumps(data)[:300]}")
                return text.strip()
            if r.status_code in (429, 502, 503, 504):
                print(f"  Gemini {r.status_code} key#{_key_idx} attempt {attempt}", file=sys.stderr)
                if attempt >= 3:
                    if _key_idx + 1 < len(GEMINI_KEYS):
                        _key_idx += 1
                        print(f"  → rotating to key #{_key_idx}", file=sys.stderr)
                    else:
                        raise RuntimeError(f"all {len(GEMINI_KEYS)} keys exhausted")
                    break
                continue
            raise RuntimeError(f"Gemini HTTP {r.status_code}: {r.text[:300]}")
    raise RuntimeError("all keys exhausted")


# ── EPUB → ordered chunks ─────────────────────────────────────────────────

def epub_to_chunks(epub_path: Path) -> list[dict]:
    book = epub.read_epub(str(epub_path))
    chunks: list[dict] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        # Build markdown
        md_parts = []
        for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "li"]):
            text = el.get_text(separator=" ", strip=True)
            if not text:
                continue
            tag = el.name
            if tag == "h1":   md_parts.append(f"## {text}")
            elif tag == "h2": md_parts.append(f"### {text}")
            elif tag in ("h3", "h4"): md_parts.append(f"#### {text}")
            elif tag == "blockquote": md_parts.append(f"> {text}")
            elif tag == "li": md_parts.append(f"- {text}")
            else:             md_parts.append(text)
        content = "\n\n".join(md_parts).strip()
        if not content:
            continue
        # Derive title from first heading
        m = re.search(r"^(#{2,4})\s+(.+)", content, re.M)
        title = m.group(2).strip() if m else item.get_name()
        chunks.append({
            "src_file": item.get_name(),
            "title_en": title,
            "content_en": content,
        })
    return chunks


# ── Pipeline ──────────────────────────────────────────────────────────────

def find_epub_for_book(book: dict) -> Path:
    pdf = Path(book["file_path"])
    # Sister .epub in same dir
    epub_p = pdf.with_suffix(".epub")
    if epub_p.exists():
        return epub_p
    # Otherwise search sibling
    for f in pdf.parent.iterdir():
        if f.suffix.lower() == ".epub":
            return f
    raise FileNotFoundError(f"no epub for {pdf}")


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*", headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        raise SystemExit(f"no ebooks row for {ebook_id}")
    return rows[0]


def translate_book(ebook_id: str, limit: int | None, inspect: bool, dry_run: bool) -> None:
    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}")
    epub_path = find_epub_for_book(book)
    print(f"EPUB: {epub_path}")

    src_chunks = epub_to_chunks(epub_path)
    print(f"Source chunks: {len(src_chunks)}")
    total_en_chars = sum(len(c["content_en"]) for c in src_chunks)
    print(f"Source total: {total_en_chars:,} chars")

    if inspect:
        for i, c in enumerate(src_chunks[:8]):
            print(f"\n[{i}] {c['title_en'][:60]}  ({len(c['content_en'])} chars)")
            print(c["content_en"][:400])
        print(f"... and {max(0, len(src_chunks)-8)} more")
        return

    target = src_chunks[:limit] if limit else src_chunks

    out_chunks: list[dict] = []
    t_total = time.time()
    for i, c in enumerate(target):
        en = c["content_en"]
        if not en.strip() or len(en) < 30:
            # Skip empties + tiny front-matter slivers
            continue
        elapsed_total = time.time() - t_total
        rate = (i + 1) / elapsed_total if elapsed_total else 0
        eta = (len(target) - i - 1) / rate if rate else 0
        print(f"\n[{i+1}/{len(target)}] {c['title_en'][:50]}  ({len(en)} en chars)  ETA {int(eta)}s")
        if dry_run:
            print("  (dry-run, skipped Gemini call)")
            continue
        t0 = time.time()
        try:
            zh = gemini_translate(en)
        except Exception as e:
            print(f"  ⚠ translation failed: {e}", file=sys.stderr)
            continue
        zh = se.to_traditional(zh)         # safety s2tw pass — Gemini sometimes returns simplified
        zh = pl.collapse_cjk_spacing(zh)
        elapsed = time.time() - t0
        out_chunks.append({
            "chunk_index": len(out_chunks),
            "chunk_type": "chapter",
            "page_number": None,
            "chapter_path": (re.search(r"^(#{2,4})\s+(.+)", zh, re.M).group(2).strip()
                             if re.search(r"^(#{2,4})\s+", zh, re.M) else c["title_en"]),
            "format": "markdown",
            "source_lang": "en",
            "content": zh,
        })
        print(f"  ✓ {len(zh)} zh chars  in {elapsed:.1f}s")

    if dry_run or not out_chunks:
        return

    # Persist
    out_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for c in out_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\nWrote {out_path}  ({out_path.stat().st_size//1024} KB)")

    # R2 + DB previews
    try:
        se.push_to_r2(ebook_id, out_path)
        print("  ✓ pushed R2")
    except Exception as e:
        print(f"  ⚠ R2 push failed: {e}", file=sys.stderr)

    # Update DB
    total_chars = sum(len(c["content"]) for c in out_chunks)
    now = datetime.utcnow().isoformat() + "Z"
    patch = {
        "chunk_count": len(out_chunks),
        "total_chars": total_chars,
        "total_pages": len(out_chunks),
        "parsed_at": now,
        "standardized_at": now,
    }
    r = requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}", headers=H_JSON, json=patch, timeout=30)
    r.raise_for_status()
    print(f"  ✓ ebooks row updated  chunk_count={len(out_chunks)}  total_chars={total_chars:,}")

    # Refresh ebook_chunks previews
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}", headers=H_GET, timeout=30)
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c["chunk_type"],
        "page_number": c["page_number"],
        "chapter_path": c["chapter_path"],
        "content": c["content"][:200],
        "char_count": len(c["content"]),
    } for c in out_chunks]
    BATCH = 25
    for i in range(0, len(rows), BATCH):
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=rows[i:i+BATCH], timeout=60)
        if not rr.ok:
            print(f"  ⚠ chunk preview insert: {rr.status_code}: {rr.text[:200]}", file=sys.stderr)
    print("  ✓ ebook_chunks previews refreshed")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id")
    p.add_argument("--inspect", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    translate_book(args.ebook_id, args.limit, args.inspect, args.dry_run)


if __name__ == "__main__":
    main()
