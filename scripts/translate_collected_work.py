"""Driver: turn two source editions of one work into a trilingual reader book.

Ties the collected-works pieces together:

    load_plaintext_sections(de) ┐
                                ├─ align_editions ─ assemble_multilang_chunks ─ write_jsonl ─ (R2 + DB)
    load_plaintext_sections(en) ┘                       ▲ translate_fn (LLM)

The translation engine (Gemini/Haiku/Sonnet) + R2/DB upload are reused from
translate_ebook_to_zh, but lazy-imported so the pure parts (section loading,
alignment, JSONL assembly) stay testable with a stub translate_fn — no network,
LLM, or heavy deps.

Pilot: public-domain 1912《Wandlungen》(de) + Hinkle 1916《Psychology of the
Unconscious》(en). See .claude/skills/collected-works-multilang/.
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from align_editions import align_editions, parse_chapter_number
from multilang_chunks import assemble_multilang_chunks, validate_multilang_chunk, write_jsonl

# German source, English as a do-not-translate disambiguation reference, output
# 繁體中文. Glossary terms live in jung_glossary.md; high-frequency ones are
# pinned here so the engine doesn't drift across sections.
JUNG_PROMPT_TMPL = """你是榮格全集的專業譯者。把下列**德文原典**翻譯成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）。
2. 從德文原典翻譯；附上的英文僅供消歧義參考，**不要翻譯英文**。
3. 保留 Markdown 結構（## / ### / **粗體** / *斜體* / > 引文 / - 清單）與腳註標記 [^N]。
4. 術語對齊（德文為準）：Archetypus→原型、kollektives Unbewusstes→集體無意識、
   das Unbewusste→無意識（非「潛意識」）、Individuation→個體化、das Selbst→自性
   （禁「本我」）、Anima→阿尼瑪、Animus→阿尼姆斯、Schatten→陰影、Libido→力比多、
   Numinosum→努秘、Wandlung→轉化。人名：Freud→佛洛伊德（禁「弗洛伊德」）。
5. 章節標題簡潔（「Kapitel 1」→「第一章」）。

只輸出翻譯後的繁體中文，不要前言或說明。

{source}"""

_MD_HEADING_RE = re.compile(r"^#{1,6}\s+\S")


def split_sections(text: str) -> list[dict]:
    """Split a plain-text / markdown edition into [{heading, text}] sections.

    A line starts a new section when it is a markdown heading (`## …`) OR a short
    line (≤80 chars) that parses as a chapter/section anchor (Chapter III /
    Kapitel 3 / 第三章 / § 4). Text before the first heading becomes a
    '(front)' section so nothing is dropped.
    """
    heads: list[str | None] = []
    bodies: list[list[str]] = []
    cur_body: list[str] | None = None

    for raw in text.splitlines():
        s = raw.strip()
        is_heading = bool(_MD_HEADING_RE.match(s)) or (0 < len(s) <= 80 and parse_chapter_number(s) is not None)
        if is_heading:
            cur_body = []
            heads.append(s)
            bodies.append(cur_body)
        else:
            if cur_body is None:
                # leading body before any heading → front-matter bucket
                cur_body = []
                heads.append(None)
                bodies.append(cur_body)
            cur_body.append(raw)

    sections = []
    for h, body_lines in zip(heads, bodies):
        body = "\n".join(body_lines).strip()
        heading = h if h is not None else "(front)"
        if heading != "(front)" or body:
            sections.append({"heading": heading, "text": body})
    return sections


def load_plaintext_sections(path: str | Path) -> list[dict]:
    return split_sections(Path(path).read_text(encoding="utf-8"))


def default_chunks_path(ebook_id: str) -> Path:
    base = os.environ.get("EBOOK_CHUNKS_DIR")
    if not base:
        raise RuntimeError("EBOOK_CHUNKS_DIR not set; pass out_path explicitly")
    return Path(base) / f"{ebook_id}.jsonl"


def make_translate_fn(engine: str = "gemini"):
    """Build a real LLM translate_fn(unit) → 繁中, reusing the
    translate_ebook_to_zh engine. Lazy import keeps the heavy deps + env reads
    out of the pure/test path."""
    import translate_ebook_to_zh as te

    te.PROMPT_TMPL = JUNG_PROMPT_TMPL  # engines wrap source with module PROMPT_TMPL
    engine_fn = {
        "gemini": te.gemini_with_haiku_fallback,
        "haiku": te.haiku_translate,
        "sonnet": te.sonnet_translate,
    }[engine]

    def translate_fn(unit: dict) -> str:
        de = (unit["sources"].get("de") or "").strip()
        en = (unit["sources"].get("en") or "").strip()
        primary = de or en  # de-only/en-only sections: translate whichever exists
        ref = en if (de and en) else ""
        pieces = te.split_oversized(primary)
        out = []
        for piece in pieces:
            src = piece
            if ref and len(pieces) == 1:
                src = f"{piece}\n\n[英文參考 — 不要翻譯，僅供消歧義]\n{ref}"
            out.append(engine_fn(src))
        return "\n\n".join(out)

    return translate_fn


def _upload(ebook_id: str, chunks: list[dict], out_path: Path) -> None:
    """Push JSONL to R2 + patch ebooks row + refresh previews (reuses te globals)."""
    import datetime
    import requests
    import translate_ebook_to_zh as te

    try:
        te.se.push_to_r2(ebook_id, out_path)
        print("  ✓ pushed R2")
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 push failed: {e}")

    total_chars = sum(len(c["content"]) for c in chunks)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    patch = {"chunk_count": len(chunks), "total_chars": total_chars,
             "total_pages": len(chunks), "parsed_at": now, "standardized_at": now}
    requests.patch(f"{te.URL}/rest/v1/ebooks?id=eq.{ebook_id}", headers=te.H_JSON, json=patch, timeout=30).raise_for_status()
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}", headers=te.H_GET, timeout=30)
    rows = [{"ebook_id": ebook_id, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[i:i + 25], timeout=60)
    print(f"  ✓ ebooks row + previews updated  chunk_count={len(chunks)}")


def run(de_path, en_path, ebook_id, translate_fn, *, source_order=("de", "en"),
        limit=None, volume=None, out_path=None, upload=False) -> list[dict]:
    """Full pipeline. `translate_fn` is injected so tests pass a stub and the
    real CLI passes make_translate_fn(engine)."""
    de_secs = load_plaintext_sections(de_path)
    en_secs = load_plaintext_sections(en_path)
    units = align_editions(de_secs, en_secs)
    if limit:
        units = units[:limit]
    chunks = assemble_multilang_chunks(units, translate_fn, list(source_order), volume=volume)
    for c in chunks:
        validate_multilang_chunk(c)
    out = Path(out_path) if out_path else default_chunks_path(ebook_id)
    write_jsonl(chunks, out)
    print(f"Wrote {out}  ({len(chunks)} chunks)")
    if upload:
        _upload(ebook_id, chunks, out)
    return chunks


def main():
    ap = argparse.ArgumentParser(description="Translate a 2-edition work into a trilingual reader book")
    ap.add_argument("--de", required=True, help="German source plain-text/markdown path")
    ap.add_argument("--en", required=True, help="English source plain-text/markdown path")
    ap.add_argument("--ebook", required=True, help="ebook_id (DB row must exist)")
    ap.add_argument("--engine", default="gemini", choices=["gemini", "haiku", "sonnet"])
    ap.add_argument("--limit", type=int, default=None, help="only first N aligned units (smoke test)")
    ap.add_argument("--volume", default=None)
    ap.add_argument("--out", default=None, help="JSONL out path (default: EBOOK_CHUNKS_DIR/<id>.jsonl)")
    ap.add_argument("--upload", action="store_true", help="push R2 + patch DB")
    args = ap.parse_args()
    run(args.de, args.en, args.ebook, make_translate_fn(args.engine),
        limit=args.limit, volume=args.volume, out_path=args.out, upload=args.upload)


if __name__ == "__main__":
    main()
