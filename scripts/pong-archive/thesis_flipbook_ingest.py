#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest 龐牧師學位論文 PDF → R2 + structured JSONL → pong_writings row.

Pipeline per PDF (idempotent):
  1. Upload original PDF to R2 at pong-writings/{slug}.pdf
  2. Run Gemini structured OCR → blocks per page (heading/paragraph/quote/footnote)
     + chapter outline. Falls back to plain text if structured prompt fails.
  3. Gzip JSONL, upload to R2 at pong-writings-pages/{slug}.jsonl.gz
  4. Upsert pong_writings row (category='thesis')

Why a dedicated pipeline (not reusing ocr_with_gemini.py): that script targets
the `ebooks` table with plain {page, text}. Thesis flipbook needs richer per-page
structure (heading levels, quotes, footnotes) for HTML restyling, and a different
table (pong_writings) + different R2 prefix.

Usage:
  python scripts/pong-archive/thesis_flipbook_ingest.py status
  python scripts/pong-archive/thesis_flipbook_ingest.py run                    # both PDFs
  python scripts/pong-archive/thesis_flipbook_ingest.py run --only bd          # just BD
  python scripts/pong-archive/thesis_flipbook_ingest.py run --only mth         # just MTh
  python scripts/pong-archive/thesis_flipbook_ingest.py run --skip-ocr         # only upload PDF + create row
  python scripts/pong-archive/thesis_flipbook_ingest.py run --skip-pdf-upload  # only re-OCR
"""
import gzip
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime, date

# stdout UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests
import boto3
import fitz  # PyMuPDF
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parents[2]


def load_env():
    env = {}
    with (ROOT / ".env").open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
SB_URL = ENV["SUPABASE_URL"].rstrip("/")
SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
SB_H = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

R2_BUCKET = ENV["R2_BUCKET"]
PDF_PREFIX = "pong-writings/"
PAGES_PREFIX = "pong-writings-pages/"

# Two-thesis target manifest
THESES = {
    "bd": {
        "slug": "pong-bd-thesis-1992",
        "pdf": "pong-archive/stores/龐牧師學位論文/92 BD - Pong Kwan Wah - Thesis Full.pdf",
        "title": "聖經神學的進路：以《雅各書》為例",  # placeholder; will be overwritten by 真正 title from PDF cover
        "title_en": "Bachelor of Divinity Thesis",
        "published_date": "1992-06-01",
        "date_approximate": True,
        "publication": "中華信義神學院",  # placeholder; user will edit if needed
        "tags": ["學位論文", "BD", "信義神學院"],
        "sort_order_hint": "thesis-bd",
    },
    "mth": {
        "slug": "pong-mth-thesis",
        "pdf": "pong-archive/stores/龐牧師學位論文/MTh.pdf",
        "title": "MTh 論文",  # placeholder
        "title_en": "Master of Theology Thesis",
        "published_date": None,
        "date_approximate": True,
        "publication": None,
        "tags": ["學位論文", "MTh"],
        "sort_order_hint": "thesis-mth",
    },
}


# ── R2 helpers ────────────────────────────────────────────────
_r2 = None
def r2():
    global _r2
    if _r2 is None:
        _r2 = boto3.client(
            "s3",
            region_name="auto",
            endpoint_url=ENV["R2_ENDPOINT"],
            aws_access_key_id=ENV["R2_ACCESS_KEY"],
            aws_secret_access_key=ENV["R2_SECRET_KEY"],
        )
    return _r2


def r2_head(key):
    try:
        return r2().head_object(Bucket=R2_BUCKET, Key=key)
    except Exception:
        return None


def r2_put(key, body, content_type, content_encoding=None):
    kwargs = dict(Bucket=R2_BUCKET, Key=key, Body=body, ContentType=content_type)
    if content_encoding:
        kwargs["ContentEncoding"] = content_encoding
    r2().put_object(**kwargs)


# ── DB helpers ────────────────────────────────────────────────
def db_find_by_slug(slug):
    """Find existing pong_writings row by source_url marker we stash there."""
    r = requests.get(
        f"{SB_URL}/rest/v1/pong_writings",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        params={"select": "*", "source_url": f"eq.thesis-slug:{slug}"},
        timeout=30,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def db_next_sort_order():
    r = requests.get(
        f"{SB_URL}/rest/v1/pong_writings",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        params={"select": "sort_order", "order": "sort_order.desc", "limit": "1"},
        timeout=30,
    )
    r.raise_for_status()
    rows = r.json()
    return (rows[0]["sort_order"] or 0) + 1 if rows else 1


def db_upsert(slug, meta, pdf_r2_key, pages_r2_key, outline, total_pages):
    existing = db_find_by_slug(slug)
    payload = {
        "title": meta["title"],
        "title_en": meta.get("title_en"),
        "category": "thesis",
        "publication": meta.get("publication"),
        "published_date": meta.get("published_date"),
        "date_approximate": meta.get("date_approximate", True),
        "source_url": f"thesis-slug:{slug}",  # used as unique key
        "tags": meta.get("tags", []),
        "is_published": True,
        "pdf_r2_key": pdf_r2_key,
        "pages_r2_key": pages_r2_key,
        "outline": outline or [],
        "total_pages": total_pages,
    }
    if existing:
        r = requests.patch(
            f"{SB_URL}/rest/v1/pong_writings?id=eq.{existing['id']}",
            headers=SB_H,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        print(f"  → updated pong_writings id={existing['id']}")
        return existing["id"]
    else:
        payload["sort_order"] = db_next_sort_order()
        r = requests.post(
            f"{SB_URL}/rest/v1/pong_writings",
            headers=SB_H,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        new_id = r.json()[0]["id"]
        print(f"  → inserted pong_writings id={new_id}")
        return new_id


# ── PDF upload ────────────────────────────────────────────────
def upload_pdf(slug, pdf_path):
    key = f"{PDF_PREFIX}{slug}.pdf"
    size = pdf_path.stat().st_size
    head = r2_head(key)
    if head and head.get("ContentLength") == size:
        print(f"  ✓ PDF already on R2 ({size/1024/1024:.1f} MB) — skipping upload")
        return key
    print(f"  ↑ uploading PDF {pdf_path.name} ({size/1024/1024:.1f} MB)…", end="", flush=True)
    t0 = time.time()
    with pdf_path.open("rb") as f:
        r2_put(key, f.read(), "application/pdf")
    print(f" done ({time.time()-t0:.1f}s)")
    return key


# ── Gemini structured OCR ────────────────────────────────────
PAGES_SCHEMA = {
    "type": "object",
    "properties": {
        "outline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer"},  # 1=chapter, 2=section, 3=subsection
                    "text":  {"type": "string"},
                    "page":  {"type": "integer"},  # 1-based PDF page where heading appears
                },
                "required": ["level", "text", "page"],
            },
        },
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer"},
                    "blocks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type":   {"type": "string"},
                                # type: chapter_title | section_title | subsection_title |
                                #       paragraph | quote | list_item | footnote | page_number
                                "level":  {"type": "integer"},  # 1-4, for headings
                                "marker": {"type": "string"},   # footnote marker e.g. "1", "*"
                                "text":   {"type": "string"},
                            },
                            "required": ["type", "text"],
                        },
                    },
                },
                "required": ["page", "blocks"],
            },
        },
    },
    "required": ["outline", "pages"],
}


PROMPT = """\
這份 PDF 是一本繁體中文神學論文（學位論文，掃描檔）。請完整 OCR 並結構化每一頁。

對每一頁，將內容拆解為 blocks 陣列。每個 block 是以下其中一種：

- chapter_title  (level=1)  — 章標題，例如「第一章 緒論」
- section_title  (level=2)  — 節標題，例如「第一節 研究背景」或「一、研究動機」
- subsection_title (level=3) — 小節標題，例如「(一) 研究方法」
- subsection_title (level=4) — 更細的小節，例如「1. 略談」
- paragraph                 — 一般段落（正文）
- quote                     — 引用文字（聖經、別人著作的引文，通常縮排或字體不同）
- list_item                 — 列表項目（1. / (一) / a. 開頭的單行）
- footnote                  — 該頁底的腳註（含腳註編號 marker）
- page_number               — 頁碼（保留純頁碼數字字串，例如 "12"）

格式守則：
- 每個 block 都必須有 type 與 text。標題類額外帶 level，腳註額外帶 marker（如 "1", "2", "*"）。
- text 內保留原始換行用 \\n。
- 段落要合併同段的多行成一個 paragraph block。
- 引文是塊狀引用（block quote），跨多行就放在同一個 quote block。
- 跳過頁眉/頁腳的重複裝飾（如書名），只把真正頁碼保留為 page_number。
- 如果一頁是空白或純扉頁，仍回傳該頁但 blocks 設為空陣列。

同時在 outline 陣列中列出整本論文的章節目錄（chapter_title / section_title），每筆含 level、text、首次出現的 page。

只回傳 JSON 物件，符合下列形狀：
{
  "outline": [{"level": 1, "text": "...", "page": 1}, ...],
  "pages":   [{"page": 1, "blocks": [{"type": "...", "text": "...", ...}, ...]}, ...]
}

不要翻譯、不要摘要、不要加任何 markdown 包裝或註解。原文是繁體中文時請以繁體中文輸出（若 OCR 看到簡體，請靜默轉繁體）。
"""


def gemini_client():
    keys = []
    for name in ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY"):
        v = ENV.get(name) or os.environ.get(name)
        if v:
            for k in v.split(","):
                k = k.strip()
                if k and k not in keys:
                    keys.append(k)
    for n in range(1, 11):
        for base in ("GEMINI_API_KEY", "Gemini_API_Key"):
            v = ENV.get(f"{base}_{n}") or os.environ.get(f"{base}_{n}")
            if v:
                for k in v.split(","):
                    k = k.strip()
                    if k and k not in keys:
                        keys.append(k)
    if not keys:
        raise RuntimeError("No Gemini API key found in .env")
    return genai.Client(api_key=keys[0]), keys


def run_ocr(pdf_path, model="gemini-2.5-flash"):
    client, keys = gemini_client()
    print(f"  ◇ Gemini OCR ({model}, {len(keys)} key(s))…")
    t0 = time.time()

    with tempfile.NamedTemporaryFile(
        prefix="thesis_", suffix=".pdf", delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)
    try:
        tmp_path.write_bytes(pdf_path.read_bytes())
        uploaded = client.files.upload(
            file=tmp_path,
            config=types.UploadFileConfig(
                display_name=tmp_path.name,
                mime_type="application/pdf",
            ),
        )
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass

    try:
        resp = client.models.generate_content(
            model=model,
            contents=[uploaded, PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PAGES_SCHEMA,
            ),
        )
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass

    elapsed = time.time() - t0
    raw = resp.text or ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try json_repair if installed; otherwise re-raise
        try:
            import json_repair
            data = json_repair.loads(raw)
        except Exception:
            print(f"  ❌ JSON parse failed (raw {len(raw)} chars)")
            raise

    pages = data.get("pages", [])
    outline = data.get("outline", [])

    # Sanity stats (no full text dumped to log)
    block_count = sum(len(p.get("blocks", [])) for p in pages)
    type_hist = {}
    for p in pages:
        for b in p.get("blocks", []):
            t = b.get("type", "?")
            type_hist[t] = type_hist.get(t, 0) + 1

    print(f"  ✓ OCR done in {elapsed:.0f}s — {len(pages)} pages, "
          f"{block_count} blocks, {len(outline)} outline entries")
    print(f"    blocks by type: " + ", ".join(f"{k}={v}" for k, v in sorted(type_hist.items())))
    return outline, pages


def write_jsonl(pages):
    """One line per page. {page, blocks}."""
    lines = []
    for p in pages:
        lines.append(json.dumps({
            "page":   p["page"],
            "blocks": p.get("blocks", []),
        }, ensure_ascii=False))
    return ("\n".join(lines) + "\n").encode("utf-8")


def upload_jsonl(slug, pages):
    raw = write_jsonl(pages)
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
        gz.write(raw)
    gz_bytes = buf.getvalue()
    key = f"{PAGES_PREFIX}{slug}.jsonl.gz"
    print(f"  ↑ uploading JSONL ({len(raw)/1024:.1f} KB → {len(gz_bytes)/1024:.1f} KB gz)…",
          end="", flush=True)
    r2_put(key, gz_bytes, "application/x-ndjson", content_encoding="gzip")
    print(" done")
    return key


# ── Commands ──────────────────────────────────────────────────
def cmd_status():
    for which, meta in THESES.items():
        pdf = ROOT / meta["pdf"]
        exists = pdf.exists()
        size_mb = pdf.stat().st_size / 1024 / 1024 if exists else 0
        slug = meta["slug"]
        doc = fitz.open(pdf) if exists else None
        pages = len(doc) if doc else "?"
        if doc:
            doc.close()
        pdf_key = f"{PDF_PREFIX}{slug}.pdf"
        pages_key = f"{PAGES_PREFIX}{slug}.jsonl.gz"
        on_r2_pdf = bool(r2_head(pdf_key))
        on_r2_pages = bool(r2_head(pages_key))
        db_row = db_find_by_slug(slug)
        print(f"\n[{which.upper()}] {meta['pdf']}")
        print(f"  local: {'✓' if exists else '✗'} ({size_mb:.1f} MB, {pages} pages)")
        print(f"  R2 PDF:        {'✓' if on_r2_pdf else '✗'} ({pdf_key})")
        print(f"  R2 pages:      {'✓' if on_r2_pages else '✗'} ({pages_key})")
        print(f"  pong_writings: {'✓ id=' + str(db_row['id']) if db_row else '✗'}")


def cmd_run(only=None, skip_ocr=False, skip_pdf_upload=False):
    targets = [k for k in THESES if (only is None or k == only)]
    if not targets:
        print(f"❌ unknown --only value: {only}")
        sys.exit(1)

    for which in targets:
        meta = THESES[which]
        print(f"\n========== {which.upper()}: {meta['pdf']} ==========")
        pdf_path = ROOT / meta["pdf"]
        if not pdf_path.exists():
            print(f"  ❌ source missing: {pdf_path}")
            continue

        slug = meta["slug"]
        existing_row = db_find_by_slug(slug)

        # 1. PDF → R2
        if skip_pdf_upload:
            pdf_key = f"{PDF_PREFIX}{slug}.pdf"
            print(f"  ⊘ skip-pdf-upload, using existing key {pdf_key}")
        else:
            pdf_key = upload_pdf(slug, pdf_path)

        # 2. OCR
        if skip_ocr:
            pages_key = (existing_row or {}).get("pages_r2_key") or f"{PAGES_PREFIX}{slug}.jsonl.gz"
            outline   = (existing_row or {}).get("outline") or []
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            print(f"  ⊘ skip-ocr, leaving pages_r2_key={pages_key}, outline={len(outline)} entries")
        else:
            outline, pages = run_ocr(pdf_path)
            pages_key = upload_jsonl(slug, pages)
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()

        # 3. DB row
        db_upsert(slug, meta, pdf_key, pages_key, outline, total_pages)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "status":
        cmd_status()
    elif cmd == "run":
        only = None
        if "--only" in args:
            only = args[args.index("--only") + 1].lower()
        skip_ocr = "--skip-ocr" in args
        skip_pdf_upload = "--skip-pdf-upload" in args
        cmd_run(only=only, skip_ocr=skip_ocr, skip_pdf_upload=skip_pdf_upload)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
