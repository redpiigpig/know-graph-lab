"""Build the trilingual Jung pilot from per-chapter JSON data files → local JSONL + DB upsert.
Resumable: each chapter lives in .claude/skills/ebook-collected-works/jung_data/chNN.json as
aligned rows [{zh,de,en}, ...]; this assembles cover + all chapters into the reader JSONL.
de = 1912 Wandlungen (PD OCR) · en = Hinkle 1916 (PD Gutenberg) · zh = my own glossary-locked translation."""
import os, json, glob, sys
from pathlib import Path
for line in Path(".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("="); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
sys.path.insert(0, "scripts")
from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl
import requests

EBID = "22222222-2222-4222-8222-222222222222"
DATA = Path(".claude/skills/ebook-collected-works/jung_data")

cover = {"chunk_index": 0, "chunk_type": "chapter", "page_number": None, "chapter_path": "封面",
         "format": "markdown", "content": "## 封面"}
chunks = [cover]

for path in sorted(DATA.glob("ch*.json")):
    ch = json.loads(path.read_text(encoding="utf-8"))
    rows = ch["rows"]
    zh = [r["zh"] for r in rows]
    de = [r["de"] for r in rows]
    en = [r["en"] for r in rows]
    # alignment gate: equal segment counts across all three columns
    if not (len(zh) == len(de) == len(en)):
        raise SystemExit(f"{path.name}: segment count mismatch zh={len(zh)} de={len(de)} en={len(en)}")
    chunk = build_multilang_chunk(
        chunk_index=ch["chunk_index"], chapter_path=ch["chapter_path"],
        volume=ch.get("volume"), parent_volume=ch.get("parent_volume"), title_en=ch.get("title_en"),
        content_zh="\n\n".join(zh),
        sources={"de": "\n\n".join(de), "en": "\n\n".join(en)}, source_order=["de", "en"])
    validate_multilang_chunk(chunk)
    chunks.append(chunk)
    print(f"  {path.name}: {len(rows)} rows | {sum(len(s) for s in zh)} zh chars")

out = Path(os.environ["EBOOK_CHUNKS_DIR"]) / f"{EBID}.jsonl"
write_jsonl(chunks, out)
total = sum(len(c["content"]) for c in chunks)
print("wrote", out, len(chunks), "chunks |", total, "zh chars")

URL = os.environ["SUPABASE_URL"]; KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
     "Prefer": "resolution=merge-duplicates"}
row = {"id": EBID,
       "title": "力比多的轉化與象徵（試譯·德英中三欄）", "author": "C. G. 榮格", "author_en": "C. G. Jung",
       "original_title": "Wandlungen und Symbole der Libido (1912)", "file_type": "epub",
       "file_path": "TEST/jung-trilingual-pilot",
       "category": "世界宗教", "subcategory": "深層心理學", "display_mode": "standard",
       "translator": "Claude（德文直譯）", "publication_year": 1912,
       "chunk_count": len(chunks), "total_pages": len(chunks), "total_chars": total,
       "parsed_at": "2026-06-03T00:00:00Z", "standardized_at": "2026-06-04T00:00:00Z"}
r = requests.post(f"{URL}/rest/v1/ebooks", headers=H, json=row, timeout=30)
print("ebooks upsert", r.status_code, r.text[:200] if not r.ok else "OK", EBID)
