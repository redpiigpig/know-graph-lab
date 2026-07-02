"""Writer-side multi-language chunk builder for collected-works books
(德 GW + 英 CW + 繁中, …).

This is the Python mirror of the reader/JS contract in
`lib/multilang-sources.ts`. The translate pipeline uses it to emit JSONL the
reader understands: every chunk carries `sources` (lang-code → text) +
`source_order`, and ALSO mirrors the PRIMARY source (source_order[0]) into the
legacy `source_text` / `source_lang` fields so the two-column reader and all
existing bilingual books keep working unchanged.

Pure functions only — no network, DB, LLM, or filesystem (except the tiny
`write_jsonl` convenience). The actual alignment + translation engine plugs a
`translate_fn` into `assemble_multilang_chunks`.

See .claude/skills/ebook-collected-works/SKILL.md.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable


def normalize_sources(
    sources: dict | None,
    source_order: list | None,
    source_text: str | None = None,
    source_lang: str | None = None,
) -> tuple[dict, list]:
    """Canonicalize multilang fields → (sources, source_order).

    Mirror of TS `normalizeSources`:
      - explicit `sources` wins; `source_order` is filtered to existing keys and
        any missing source key is appended (stable) so no column is dropped.
      - else fall back to the legacy single source (source_text + source_lang);
        note source_text="" is a real (blank-but-present) source, only None is
        monolingual.
      - else empty (monolingual).
    """
    if sources:
        present = dict(sources)
        order: list = []
        for lang in (source_order or []):
            if lang in present and lang not in order:
                order.append(lang)
        for key in present:
            if key not in order:
                order.append(key)
        return present, order
    if source_text is not None and source_lang:
        return {source_lang: source_text}, [source_lang]
    return {}, []


def mirror_primary_source(chunk: dict) -> dict:
    """Return a copy of `chunk` with `sources`/`source_order` normalized and the
    legacy `source_text`/`source_lang` mirrored to the primary source. Monolingual
    chunks keep null source fields. Does not mutate the input. Mirror of TS
    `mirrorPrimarySource`.
    """
    sources, order = normalize_sources(
        chunk.get("sources"),
        chunk.get("source_order"),
        chunk.get("source_text"),
        chunk.get("source_lang"),
    )
    out = dict(chunk)
    if not order:
        out["source_lang"] = chunk.get("source_lang")
        out["source_text"] = chunk.get("source_text")
        return out
    primary = order[0]
    out["sources"] = sources
    out["source_order"] = order
    out["source_lang"] = primary
    out["source_text"] = sources[primary]
    return out


# JSONL field order kept close to the existing translate_ebook_to_zh writer so
# diffs between bilingual and multilingual books stay readable.
def build_multilang_chunk(
    *,
    chunk_index: int,
    chapter_path: str,
    content_zh: str,
    sources: dict,
    source_order: list | None = None,
    volume: str | None = None,
    parent_volume: str | None = None,
    chunk_type: str = "chapter",
    page_number: int | None = None,
    title_en: str | None = None,
    anchors: list | None = None,
) -> dict:
    """Assemble one reader-ready multilang chunk (already mirrored).

    `content_zh` is the 繁中 translation (the `content` / main column). `sources`
    is {lang: text} for every non-zh column; `source_order` defaults to the
    sources' insertion order. Optional `volume` / `parent_volume` drive the
    sidebar tree; `title_en` is the source heading used by --resume dedupe.
    `anchors` is an optional per-段 citation list (e.g. Stephanus/Bekker
    ["17a","17b",…]) aligned 1:1 with the content/sources `\\n\\n` 段 — the
    collected-works reader shows it as the left citation column.
    """
    chunk: dict = {
        "chunk_index": chunk_index,
        "chunk_type": chunk_type,
        "page_number": page_number,
        "chapter_path": chapter_path,
        "format": "markdown",
        "content": content_zh,
        "sources": dict(sources),
        "source_order": list(source_order) if source_order else list(sources.keys()),
    }
    if volume is not None:
        chunk["volume"] = volume
    if parent_volume is not None:
        chunk["parent_volume"] = parent_volume
    if title_en is not None:
        chunk["title_en"] = title_en
    if anchors:
        chunk["anchors"] = list(anchors)
    return mirror_primary_source(chunk)


def validate_multilang_chunk(chunk: dict) -> None:
    """Raise ValueError if a chunk violates the reader contract. Cheap guard to
    run before writing JSONL so a malformed chunk fails loud, not silently in
    the reader."""
    if not chunk.get("content"):
        raise ValueError(f"chunk {chunk.get('chunk_index')}: empty content (繁中主欄)")
    order = chunk.get("source_order") or []
    sources = chunk.get("sources") or {}
    if not order:
        return  # monolingual chunk — nothing more to check
    for lang in order:
        if lang not in sources:
            raise ValueError(f"chunk {chunk.get('chunk_index')}: source_order '{lang}' not in sources")
    if set(sources.keys()) != set(order):
        raise ValueError(f"chunk {chunk.get('chunk_index')}: sources keys {set(sources)} != source_order {set(order)}")
    primary = order[0]
    if chunk.get("source_lang") != primary or chunk.get("source_text") != sources[primary]:
        raise ValueError(f"chunk {chunk.get('chunk_index')}: source_text/source_lang not mirrored to primary '{primary}'")


def assemble_multilang_chunks(
    aligned_units: Iterable[dict],
    translate_fn: Callable[[dict], str],
    source_order: list,
    *,
    volume: str | None = None,
    parent_volume_fn: Callable[[dict], str | None] | None = None,
) -> list[dict]:
    """Turn aligned cross-edition units into reader-ready multilang chunks.

    `aligned_units`: each is {chapter_path, sources:{lang:text}, [volume],
    [title_en], [parent_volume]} — produced by the (separate) alignment step.
    `translate_fn(unit) -> zh markdown` is the engine boundary (LLM in prod, a
    stub in tests). Chunks are indexed 0..N-1 and validated.
    """
    out: list[dict] = []
    for i, unit in enumerate(aligned_units):
        zh = translate_fn(unit)
        chunk = build_multilang_chunk(
            chunk_index=i,
            chapter_path=unit["chapter_path"],
            content_zh=zh,
            sources=unit["sources"],
            source_order=source_order,
            volume=unit.get("volume", volume),
            parent_volume=(parent_volume_fn(unit) if parent_volume_fn else unit.get("parent_volume")),
            title_en=unit.get("title_en"),
            anchors=unit.get("anchors"),
        )
        validate_multilang_chunk(chunk)
        out.append(chunk)
    return out


def write_jsonl(chunks: list[dict], path: str | Path) -> None:
    """Write chunks one-per-line (UTF-8, no ASCII escaping) — same on-disk format
    as translate_ebook_to_zh."""
    p = Path(path)
    with open(p, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
