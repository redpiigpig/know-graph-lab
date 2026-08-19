# -*- coding: utf-8 -*-
"""Diels A/B-aware pilot pipeline for the 14 early Greek philosophy hubs.

Only Heraclitus and Parmenides are enabled for translation in this pilot.
The critical invariant is that a Diels entry's witness context is never treated
as the philosopher's words.  A reader unit is emitted only when the quoted
text has an explicit TEI boundary or a narrowly curated extraction rule.

Examples:
  python scripts/presocratics_build.py heraclitus --b 1 --engine auto
  python scripts/presocratics_build.py parmenides --b 3 --engine auto
  python scripts/presocratics_build.py --list
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
sys.path.insert(0, str(Path(__file__).resolve().parent))

import multilang_chunks as mc  # noqa: E402
from presocratics_registry import HUBS, citation_id, record_policy  # noqa: E402


CACHE = Path("c:/tmp/presocratics_cache")
NS = "http://www.tei-c.org/ns/1.0"
Q = lambda tag: f"{{{NS}}}{tag}"
PARENT_VOLUME = "古希臘哲學全集"
WIKISOURCE_API = "https://en.wikisource.org/w/api.php"

# Heraclitus' Diels TEI does not encode quotation boundaries consistently.
# Start with one defensible pilot rule.  Every additional ID must be reviewed
# against the cited ancient witness before being added here.
HERACLITUS_SAFE_WHOLE_TAIL = {"1"}


PROMPT_TMPL = """你是古希臘哲學原典的繁體中文譯者。請直接翻譯下列已經校定的 B 類引文殘篇。

硬性規則：
1. 只翻譯 [希臘文引文]；[公有領域英譯參考] 只供校讀，不可反向覆蓋希臘文。
2. 這是古代文獻所保存的引文，不稱為作者手稿，也不要加入「作者寫道」等來源未有的話。
3. 赫拉克利特：λόγος 譯「邏各斯」，必要時可依句法譯「言說／理則」；不要一律譯成「理性」。
4. 巴門尼德：τὸ ὄν 譯「存有者／存有」；εἶναι 譯「是／存有」；δόξα 譯「意見」。
5. 忠實保存否定、對比、重複與詩行論證；不加標題、註解、Markdown 或引號。

{source}"""


def _clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _flatten(node: ET.Element, *, exclude: set[str] | None = None) -> str:
    exclude = exclude or set()
    parts: list[str] = []

    def walk(cur: ET.Element) -> None:
        local = cur.tag.rsplit("}", 1)[-1]
        if local in exclude:
            return
        if cur.text:
            parts.append(cur.text)
        for child in cur:
            child_local = child.tag.rsplit("}", 1)[-1]
            if child_local not in exclude:
                walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(node)
    return _clean_space(" ".join(parts))


def _first_paragraph_tail(fragment: ET.Element) -> str:
    paragraph = fragment.find("./" + Q("p"))
    if paragraph is None:
        return ""
    return _flatten(paragraph, exclude={"label", "bibl", "note", "pb"})


def _bywater_label(fragment: ET.Element) -> tuple[str | None, str | None]:
    label = fragment.find(".//" + Q("label"))
    if label is None:
        return None, None
    raw = _clean_space("".join(label.itertext())).strip("[] ")
    match = re.fullmatch(r"(\d+)\s+Bywater", raw, flags=re.I)
    return (match.group(1) if match else None), raw


def parse_diels_b_tei(xml_text: str, slug: str) -> dict[str, dict]:
    """Parse Diels B records while preserving witness context separately.

    ``quotation_text`` is empty when no trustworthy boundary is available;
    callers must skip such records rather than translate ``witness_context``.
    """
    if slug not in HUBS or HUBS[slug]["dk_chapter"] is None:
        raise ValueError(f"no Diels registry for {slug}")
    root = ET.fromstring(xml_text)
    records: dict[str, dict] = {}
    for fragment in root.findall(f".//{Q('div')}[@subtype='fragment']"):
        number = fragment.get("n")
        if not number:
            continue
        policy = record_policy("B")
        bibl = [_flatten(node) for node in fragment.findall(f".//{Q('bibl')}")]
        witness_context = _flatten(fragment, exclude={"label", "pb"})
        quote_nodes = fragment.findall(f".//{Q('quote')}")
        quotation = _clean_space("\n\n".join(_flatten(node) for node in quote_nodes))
        boundary = "tei-quote" if quotation else "unreviewed-witness-context"
        if slug == "heraclitus" and number in HERACLITUS_SAFE_WHOLE_TAIL:
            quotation = _first_paragraph_tail(fragment)
            boundary = "curated-whole-tail"
        bywater_id, legacy_label = _bywater_label(fragment)
        records[number] = {
            **policy,
            "slug": slug,
            "kind": "B",
            "number": number,
            "citation": citation_id(slug, "B", number),
            "witness_bibliography": bibl,
            "witness_context": witness_context,
            "quotation_text": quotation,
            "is_direct_quotation": bool(quotation),
            "quotation_boundary": boundary,
            "bywater_id": bywater_id,
            "legacy_label": legacy_label,
        }
    return records


def parse_testimonium_record(slug: str, number: str, witness_text: str, source: str) -> dict:
    """Construct a future A record with safeguards locked in."""
    if not witness_text.strip() or not source.strip():
        raise ValueError("an A testimonium requires witness text and its source")
    return {
        **record_policy("A"),
        "slug": slug,
        "kind": "A",
        "number": number,
        "citation": citation_id(slug, "A", number),
        "witness_bibliography": [source],
        "witness_context": _clean_space(witness_text),
        "quotation_text": "",
        "quotation_boundary": "not-applicable",
    }


def _burnet_html(payload: str) -> str:
    stripped = payload.lstrip("\ufeff \t\r\n")
    if stripped.startswith("{"):
        return json.loads(stripped)["parse"]["text"]
    return payload


def _paragraph_text(tag) -> str:
    for node in tag.select("sup.reference, span.reference, span.pagenum, .ws-noexport"):
        node.decompose()
    text = _clean_space(tag.get_text(" ", strip=True)).replace("\u200b", "")
    return re.sub(r"\s+R\.?\s*P\.?\s*\d+[a-z]?(?:\s*[a-z])?\.?\s*$", "", text).strip()


def parse_burnet_fragments(payload: str, slug: str) -> dict[tuple[str, ...], str]:
    """Parse only Burnet's bounded fragment section, not his commentary."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_burnet_html(payload), "html.parser")
    paragraphs = soup.find_all("p")
    out: dict[tuple[str, ...], str] = {}
    if slug == "heraclitus":
        active = False
        for paragraph in paragraphs:
            text = _paragraph_text(copy.copy(paragraph))
            lower = text.lower()
            if lower.startswith("the fragments."):
                active = True
                continue
            if active and "doxographical tradition" in lower:
                break
            if not active:
                continue
            match = re.match(r"^\s*\((\d+)\)\s*(.+)$", text)
            if match:
                out[(match.group(1),)] = match.group(2).strip()
        return out
    if slug != "parmenides":
        raise ValueError(f"Burnet parser not enabled for {slug}")

    active = False
    current: tuple[str, ...] | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if current and buffer:
            out[current] = _clean_space(" ".join(buffer))
        buffer = []

    for paragraph in paragraphs:
        text = _paragraph_text(copy.copy(paragraph))
        lower = text.lower()
        if "the fragments of parmenides" in lower and "arrangement of diels" in lower:
            active = True
            continue
        if not active:
            continue
        if re.match(r"^86\.\s", text):
            break
        marker = re.fullmatch(r"\(\s*([\d\s,]+)\s*\)", text)
        if marker:
            flush()
            current = tuple(re.findall(r"\d+", marker.group(1)))
            continue
        if current and text and text not in {"The Way of Truth", "The Way of Belief"}:
            buffer.append(text)
    flush()
    return out


def build_units(slug: str, greek_xml: str, burnet_payload: str) -> list[dict]:
    if slug not in {"heraclitus", "parmenides"}:
        raise ValueError(f"pilot build not enabled for {slug}")
    greek = parse_diels_b_tei(greek_xml, slug)
    english = parse_burnet_fragments(burnet_payload, slug)
    hub = HUBS[slug]
    units: list[dict] = []
    if slug == "heraclitus":
        for number, record in greek.items():
            bywater = record.get("bywater_id")
            if not record["quotation_text"] or not bywater:
                continue
            en = english.get((bywater,))
            if not en:
                continue
            units.append(_unit(hub, [record], en, f"Bywater {bywater}"))
    else:
        for numbers, en in english.items():
            records = [greek.get(number) for number in numbers]
            if any(not record or not record["quotation_text"] for record in records):
                continue
            units.append(_unit(hub, records, en, "Diels " + ", ".join(numbers)))
    return units


def _unit(hub: dict, records: list[dict], english: str, english_id: str) -> dict:
    first, last = records[0]["number"], records[-1]["number"]
    display = records[0]["citation"] if len(records) == 1 else f"DK {hub['dk_chapter']} B{first}–B{last}"
    greek = "\n\n".join(record["quotation_text"] for record in records)
    cache_id = "B" + "_".join(record["number"] for record in records)
    return {
        "chapter_path": f"{hub['name_zh']} · B類引文殘篇 · {display}",
        "title_en": display,
        "sources": {"grc": greek, "en": english},
        "anchors": [display],
        "_cache_id": cache_id,
        "kind": "B",
        "record_type": "quoted_fragment",
        "citation": display,
        "crosswalk": {"english_system": english_id, "diels": [r["citation"] for r in records]},
        "quotation_boundaries": [r["quotation_boundary"] for r in records],
    }


def _download(url: str, path: Path, *, params: dict | None = None, minimum: int = 1000) -> str:
    import requests

    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size < minimum:
        response = requests.get(url, params=params, headers={"User-Agent": "KnowGraphLab/1.0"}, timeout=90)
        response.raise_for_status()
        path.write_bytes(response.content)
    return path.read_text(encoding="utf-8-sig")


def fetch_sources(slug: str) -> tuple[str, str]:
    hub = HUBS[slug]
    if hub["source_status"] != "pilot-ready":
        raise ValueError(f"{slug}: sources are only at {hub['source_status']} stage")
    raw = CACHE / "raw"
    greek = _download(hub["greek_tei"], raw / f"{slug}_diels_1922.xml", minimum=5000)
    burnet = _download(
        WIKISOURCE_API,
        raw / f"{slug}_burnet_1920.json",
        params={
            "action": "parse", "page": hub["burnet_page"], "prop": "text",
            "format": "json", "formatversion": "2",
        },
        minimum=10000,
    )
    return greek, burnet


def make_translate_fn(engine: str, slug: str):
    import translate_ebook_to_zh as te

    te.PROMPT_TMPL = PROMPT_TMPL
    engines = {
        "auto": te.gemini_with_nvidia_fallback,
        "gemini": te.gemini_with_nvidia_fallback,
        "nvidia": te.nvidia_translate,
        "haiku": te.haiku_translate,
        "sonnet": te.sonnet_translate,
    }
    if engine not in engines:
        raise ValueError(f"unsupported engine: {engine}")
    engine_fn = engines[engine]
    cdir = CACHE / slug / "B"
    cdir.mkdir(parents=True, exist_ok=True)

    def translate(unit: dict) -> str:
        path = cdir / f"{unit['_cache_id']}.txt"
        cached = path.read_text(encoding="utf-8").strip() if path.exists() else ""
        if cached:
            return _clean_space(cached)
        source = (
            f"[希臘文引文]\n{unit['sources']['grc']}\n\n"
            f"[公有領域英譯參考]\n{unit['sources']['en']}"
        )
        translated = _clean_space(engine_fn(source))
        tmp = path.with_suffix(".tmp")
        tmp.write_text(translated, encoding="utf-8")
        tmp.replace(path)
        print(f"  ↳ {unit['chapter_path']}", flush=True)
        return translated

    return translate


def _prepend_cover(slug: str, chunks: list[dict]) -> list[dict]:
    hub = HUBS[slug]
    cover = mc.build_multilang_chunk(
        chunk_index=0,
        chapter_path="封面",
        content_zh="## 封面",
        sources={},
        source_order=[],
        volume=f"{hub['name_zh']}殘篇",
        parent_volume=PARENT_VOLUME,
        chunk_type="cover",
        page_number=1,
    )
    mc.validate_multilang_chunk(cover)
    for index, chunk in enumerate(chunks, start=1):
        chunk["chunk_index"] = index
    return [cover, *chunks]


def run(slug: str, *, engine: str = "auto", b_ids: list[str] | None = None, limit: int | None = None) -> list[dict]:
    greek, burnet = fetch_sources(slug)
    units = build_units(slug, greek, burnet)
    if b_ids:
        wanted = set(b_ids)
        units = [unit for unit in units if wanted.intersection(unit["crosswalk"]["diels"])
                 or any(citation.endswith("B" + number) for citation in unit["crosswalk"]["diels"] for number in wanted)]
    if limit is not None:
        units = units[:limit]
    if not units:
        raise ValueError(f"{slug}: no reviewed/aligned B units selected")
    print(f"[{slug}] reviewed B units={len(units)}", flush=True)
    chunks = mc.assemble_multilang_chunks(
        units, make_translate_fn(engine, slug), ["grc", "en"], volume=f"{HUBS[slug]['name_zh']}殘篇"
    )
    for chunk, unit in zip(chunks, units):
        chunk["fragment_kind"] = unit["kind"]
        chunk["fragment_citation"] = unit["citation"]
        chunk["fragment_crosswalk"] = unit["crosswalk"]
        chunk["quotation_boundaries"] = unit["quotation_boundaries"]
    chunks = _prepend_cover(slug, chunks)
    out = Path(f"c:/tmp/presocratics_{slug}.jsonl")
    mc.write_jsonl(chunks, out)
    print(f"  ✓ {out}: {len(chunks)} chunks", flush=True)
    return chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", nargs="?", choices=list(HUBS))
    parser.add_argument("--b", action="append", dest="b_ids", help="Diels B number; repeatable")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--engine", choices=["auto", "gemini", "nvidia", "haiku", "sonnet"], default="auto")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list or not args.slug:
        for hub in HUBS.values():
            dk = f"DK {hub['dk_chapter']}" if hub["dk_chapter"] is not None else "非 DK"
            print(f"{hub['slug']:12} {hub['name_zh']:8} {dk:6} {hub['source_status']}")
    else:
        run(args.slug, engine=args.engine, b_ids=args.b_ids, limit=args.limit)
