# -*- coding: utf-8 -*-
"""愛比克泰德全集 → 希臘／英／繁中三欄（collected-works pipeline ①）。

可靠來源與版權：
- 希臘原文：Heinrich Schenkl 編《Epicteti dissertationes》Teubner 1916；
  Perseus canonical-greekLit TEI（資料標示 CC BY-SA 4.0）。
- 《談話錄》《手冊》英譯：George Long 1887；Perseus TEI（公有領域）。
- 《殘篇》英譯：P. E. Matheson 1916（公有領域）；使用可直接抓取的
  Stoic Breviary 校訂轉錄，原掃描存 Internet Archive item MN40058ucmf_2。

對齊粒度：談話錄以卷.篇、手冊以章、殘篇以 Schenkl 編號。每篇在 reader
中是一列，避免把獨立版本的段落硬切成假對齊。翻譯過長篇章時內部分片，但
最終仍合成單一篇章；完成篇與分片皆有快取，中斷可續。

用法：
  python scripts/epictetus_build.py handbook --limit 1 --engine auto
  python scripts/epictetus_build.py --all --engine auto --upload
  python scripts/epictetus_build.py --list
"""
from __future__ import annotations

import argparse
import math
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


CACHE = Path("c:/tmp/epictetus_cache")
RAW = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0557"
FRAGMENTS_EN_URL = "https://stoicbreviary.blogspot.com/p/text-epictetus-fragments.html"
NS = "http://www.tei-c.org/ns/1.0"
Q = lambda tag: f"{{{NS}}}{tag}"
PARENT_VOLUME = "愛比克泰德全集"


WORKS = {
    "handbook": {
        "ebook_id": "72000000-0000-4000-8000-000000000001",
        "title_zh": "手冊",
        "title_orig": "Ἐγχειρίδιον",
        "grc": "tlg002/tlg0557.tlg002.perseus-grc2.xml",
        "eng": "tlg002/tlg0557.tlg002.perseus-eng3.xml",
        "source_note": "Schenkl 1916 希臘文；George Long 1887 英譯",
    },
    "discourses": {
        "ebook_id": "72000000-0000-4000-8000-000000000002",
        "title_zh": "談話錄",
        "title_orig": "Διατριβαί",
        "grc": "tlg001/tlg0557.tlg001.perseus-grc2.xml",
        "eng": "tlg001/tlg0557.tlg001.perseus-eng3.xml",
        "source_note": "Schenkl 1916 希臘文；George Long 1887 英譯",
    },
    "fragments": {
        "ebook_id": "72000000-0000-4000-8000-000000000003",
        "title_zh": "殘篇",
        "title_orig": "Fragmenta",
        "grc": "tlg003/tlg0557.tlg003.perseus-grc2.xml",
        "eng": None,
        "source_note": "Schenkl 1916 希臘文；P. E. Matheson 1916 英譯",
    },
}


PROMPT_TMPL = """你是古希臘斯多噶哲學的專業譯者。把下列**愛比克泰德希臘原典**翻成**繁體中文**。

規則：
1. 嚴守繁體中文，忠實、清楚、可讀；保留課堂問答語氣，不增註、不摘要、不改寫。
2. 以希臘原文為準；所附公有領域英譯只供消歧義，絕不可反客為主。
3. 定名鎖定：Ἐπίκτητος→愛比克泰德、Ἀρριανός→阿里安、Σωκράτης→蘇格拉底、
   Ζήνων→芝諾、Χρύσιππος→克呂西波、Μουσώνιος Ῥοῦφος→穆索尼烏斯‧魯弗斯。
4. 術語鎖定：τὰ ἐφ’ ἡμῖν→操之在我、τὰ οὐκ ἐφ’ ἡμῖν→不操之在我、
   προαίρεσις→抉擇意志、φαντασία→表象（依文脈可作印象）、συγκατάθεσις→同意、
   ὁρμή→衝動、ὄρεξις→欲求、ἔκκλισις→規避、ἀρετή→德性、λόγος→理性／邏各斯、
   φύσις→自然、ἀπάθεια→不動情（無擾）、ἀταραξία→心靈的寧靜、προκοπή→精進。
5. **只輸出一段連續繁體中文譯文**；不要標題、編號、前言、說明或 Markdown。

{source}"""


def _clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _element_text(node: ET.Element, *, exclude=("head", "note", "pb")) -> str:
    """Flatten TEI text while excluding editorial notes and page furniture."""
    excluded = {Q(x) for x in exclude}
    parts: list[str] = []

    def walk(cur: ET.Element) -> None:
        if cur.tag in excluded:
            return
        if cur.text:
            parts.append(cur.text)
        for child in cur:
            walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(node)
    return _clean_space(" ".join(parts))


def _head_text(node: ET.Element) -> str:
    head = node.find(f"./{Q('head')}")
    return _clean_space(" ".join(head.itertext())) if head is not None else ""


def parse_tei(xml: str, work: str) -> list[dict]:
    """Parse ordered source units without assuming English paragraph parity."""
    root = ET.fromstring(xml)
    body = root.find(f".//{Q('body')}")
    if body is None:
        return []
    container = next(
        (child for child in body.findall(f"./{Q('div')}")
         if child.get("type") in {"edition", "translation"}),
        body,
    )
    out: list[dict] = []
    if work == "discourses":
        for book in container.findall(f"./{Q('div')}[@subtype='book']"):
            book_n = book.get("n", "")
            for chapter in book.findall(f"./{Q('div')}[@subtype='chapter']"):
                chapter_n = chapter.get("n", "")
                text = _element_text(chapter)
                if text:
                    out.append({"key": f"{book_n}.{chapter_n}", "book": book_n,
                                "chapter": chapter_n, "head": _head_text(chapter), "text": text})
    elif work == "handbook":
        for chapter in container.findall(f"./{Q('div')}[@subtype='chapter']"):
            chapter_n = chapter.get("n", "")
            text = _element_text(chapter)
            if text:
                out.append({"key": chapter_n, "chapter": chapter_n,
                            "head": _head_text(chapter), "text": text})
    elif work == "fragments":
        for frag in container.findall(f"./{Q('div')}[@subtype='fragment']"):
            frag_n = frag.get("n", "")
            text = _element_text(frag)
            if text:
                out.append({"key": frag_n, "chapter": frag_n,
                            "head": _head_text(frag), "text": text})
    else:
        raise ValueError(f"unknown work: {work}")
    return out


def parse_matheson_fragments(html: str) -> dict[str, str]:
    """Extract Matheson's numbered fragments from the accessible 1916 transcript."""
    from bs4 import BeautifulSoup, NavigableString, Tag

    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("div.post-body.entry-content")
    if body is None:
        raise ValueError("Matheson fragments page: article body not found")
    out: dict[str, str] = {}
    current: str | None = None
    parts: list[str] = []

    def flush() -> None:
        nonlocal parts
        if current and parts:
            text = _clean_space(" ".join(parts))
            if text:
                out[current] = text
        parts = []

    for child in body.children:
        if isinstance(child, Tag) and child.name == "h3":
            label = _clean_space(child.get_text(" ", strip=True))
            if re.fullmatch(r"\d+[a-z]?", label, flags=re.I):
                flush()
                current = label.lower()
                continue
        if current:
            if isinstance(child, NavigableString):
                text = str(child)
            elif isinstance(child, Tag):
                text = child.get_text(" ", strip=True)
            else:
                text = ""
            if text.strip():
                parts.append(text)
    flush()
    return out


def _zh_num(value: str) -> str:
    if not value.isdigit():
        return value
    n = int(value)
    digits = "零一二三四五六七八九"
    if n < 10:
        return digits[n]
    if n < 20:
        return "十" + (digits[n % 10] if n % 10 else "")
    if n < 100:
        return digits[n // 10] + "十" + (digits[n % 10] if n % 10 else "")
    return value


def build_units(work: str, grc_xml: str, eng_source: str) -> list[dict]:
    grc = parse_tei(grc_xml, work)
    if work == "fragments":
        eng_map = parse_matheson_fragments(eng_source)
    else:
        eng_map = {x["key"]: x for x in parse_tei(eng_source, work)}
    units: list[dict] = []
    for seq, g in enumerate(grc, start=1):
        e = eng_map.get(g["key"])
        if not e:
            continue  # fragment 28a has no Matheson counterpart; English-only 9/10a likewise omitted
        e_text = e if isinstance(e, str) else e["text"]
        e_head = "" if isinstance(e, str) else e.get("head", "")
        if work == "discourses":
            if g["book"] == "0":
                chapter_path = "談話錄 · 阿里安致盧基烏斯‧格利烏斯書"
                volume = "談話錄‧序"
                anchor = "Disc. pref."
            else:
                chapter_path = f"談話錄 · 第{_zh_num(g['book'])}卷 · 第{_zh_num(g['chapter'])}篇"
                volume = f"談話錄‧第{_zh_num(g['book'])}卷"
                anchor = f"Disc. {g['book']}.{g['chapter']}"
        elif work == "handbook":
            chapter_path = f"手冊 · 第{_zh_num(g['chapter'])}章"
            volume = "手冊"
            anchor = f"Ench. {g['chapter']}"
        else:
            chapter_path = f"殘篇 · 第{g['chapter']}則"
            volume = "殘篇"
            anchor = f"Frag. {g['chapter']}"
        units.append({
            "chapter_path": chapter_path,
            "page_number": seq,
            "volume": volume,
            "parent_volume": PARENT_VOLUME,
            "title_en": f"{anchor} {e_head}".strip(),
            "sources": {"grc": g["text"], "en": e_text},
            "anchors": [anchor],
            "_cache_id": anchor.replace(" ", "_").replace(".", "-").lower(),
        })
    return units


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?;··;])\s+", _clean_space(text))
    return [p for p in parts if p]


def split_for_translation(text: str, max_chars: int = 12000) -> list[str]:
    """Split at sentence-like punctuation; normalized content is conserved."""
    if len(text) <= max_chars:
        return [_clean_space(text)]
    out: list[str] = []
    cur: list[str] = []
    size = 0
    for sentence in _split_sentences(text):
        if cur and size + 1 + len(sentence) > max_chars:
            out.append(" ".join(cur))
            cur, size = [], 0
        if len(sentence) > max_chars:
            words = sentence.split()
            for word in words:
                if cur and size + 1 + len(word) > max_chars:
                    out.append(" ".join(cur))
                    cur, size = [], 0
                cur.append(word)
                size += len(word) + (1 if size else 0)
        else:
            cur.append(sentence)
            size += len(sentence) + (1 if size else 0)
    if cur:
        out.append(" ".join(cur))
    return out


def _split_reference(text: str, n: int) -> list[str]:
    """Make n monotonic, roughly balanced English reference windows."""
    if n <= 1:
        return [_clean_space(text)]
    sentences = _split_sentences(text)
    if len(sentences) < n:
        words = _clean_space(text).split()
        width = max(1, math.ceil(len(words) / n))
        parts = [" ".join(words[i:i + width]) for i in range(0, len(words), width)]
    else:
        target = max(1, math.ceil(sum(len(s) + 1 for s in sentences) / n))
        parts, cur, size = [], [], 0
        for sentence in sentences:
            if cur and size + 1 + len(sentence) > target and len(parts) < n - 1:
                parts.append(" ".join(cur)); cur, size = [], 0
            cur.append(sentence); size += len(sentence) + (1 if size else 0)
        if cur:
            parts.append(" ".join(cur))
    while len(parts) < n:
        parts.append("")
    if len(parts) > n:
        parts[n - 1:] = [" ".join(parts[n - 1:])]
    return parts


def make_translate_fn(engine: str, work: str):
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
    cdir = CACHE / f"{work}_zh"
    pdir = cdir / ".parts"
    pdir.mkdir(parents=True, exist_ok=True)

    def translate(unit: dict) -> str:
        final = cdir / f"{unit['_cache_id']}.txt"
        cached = final.read_text(encoding="utf-8").strip() if final.exists() else ""
        if cached:
            return _clean_space(cached)
        greek_parts = split_for_translation(unit["sources"]["grc"])
        english_parts = _split_reference(unit["sources"]["en"], len(greek_parts))
        translated: list[str] = []
        fresh = 0
        for i, (grc, eng) in enumerate(zip(greek_parts, english_parts), start=1):
            piece_cache = pdir / f"{unit['_cache_id']}.{i:02d}.txt"
            zh = piece_cache.read_text(encoding="utf-8").strip() if piece_cache.exists() else ""
            if not zh:
                source = grc + (f"\n\n[公有領域英譯參考（勿翻）]\n{eng}" if eng else "")
                zh = _clean_space(engine_fn(source))
                tmp = piece_cache.with_suffix(piece_cache.suffix + ".tmp")
                tmp.write_text(zh, encoding="utf-8")
                tmp.replace(piece_cache)
                fresh += 1
            translated.append(_clean_space(zh))
        result = _clean_space(" ".join(translated))
        tmp = final.with_suffix(final.suffix + ".tmp")
        tmp.write_text(result, encoding="utf-8")
        tmp.replace(final)
        if fresh:
            print(f"  ↳ {unit['chapter_path']} (+{fresh} part{'s' if fresh != 1 else ''})", flush=True)
        return result

    return translate


def _prepend_cover(work: str, chunks: list[dict]) -> list[dict]:
    d = WORKS[work]
    cover = mc.build_multilang_chunk(
        chunk_index=0, chapter_path="封面", content_zh="## 封面", sources={}, source_order=[],
        volume=d["title_zh"], parent_volume=PARENT_VOLUME, chunk_type="cover", page_number=1,
    )
    mc.validate_multilang_chunk(cover)
    for i, chunk in enumerate(chunks, start=1):
        chunk["chunk_index"] = i
    return [cover] + chunks


def _download(url: str, path: Path, *, minimum=1000) -> str:
    import requests

    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size < minimum:
        response = requests.get(url, headers={"User-Agent": "KnowGraphLab/1.0"}, timeout=90)
        response.raise_for_status()
        path.write_bytes(response.content)
    return path.read_text(encoding="utf-8")


def fetch_sources(work: str) -> tuple[str, str]:
    d = WORKS[work]
    raw_dir = CACHE / "raw"
    grc_path = raw_dir / Path(d["grc"]).name
    grc = _download(f"{RAW}/{d['grc']}", grc_path, minimum=5000)
    if work == "fragments":
        eng = _download(FRAGMENTS_EN_URL, raw_dir / "matheson_fragments_1916.html", minimum=10000)
    else:
        eng_path = raw_dir / Path(d["eng"]).name
        eng = _download(f"{RAW}/{d['eng']}", eng_path, minimum=5000)
    return grc, eng


def ensure_ebook_row(work: str) -> None:
    import requests
    import translate_ebook_to_zh as te

    d = WORKS[work]
    response = requests.get(f"{te.URL}/rest/v1/ebooks?id=eq.{d['ebook_id']}&select=id",
                            headers=te.H_GET, timeout=30)
    if response.ok and response.json():
        return
    row = {
        "id": d["ebook_id"],
        "title": f"{d['title_zh']}（希英繁三欄）",
        "author": "愛比克泰德",
        "author_en": "Epictetus",
        "file_type": "epub",
        "file_path": f"PERSEUS/epictetus-{work}-trilingual",
        "category": "世界宗教",
        "subcategory": "古希臘哲學",
        "original_title": d["title_orig"],
        "translator": "AI 輔助（希臘原典直譯）",
        "display_mode": "standard",
        "collection": "collected-works",
    }
    requests.post(f"{te.URL}/rest/v1/ebooks", headers=te.H_JSON, json=row, timeout=30).raise_for_status()
    print(f"  ✓ inserted ebooks row {d['ebook_id']}", flush=True)


def run(work: str, *, engine="auto", limit=None, upload=False) -> list[dict]:
    grc, eng = fetch_sources(work)
    units = build_units(work, grc, eng)
    print(f"[{work}] 愛比克泰德《{WORKS[work]['title_zh']}》 → {len(units)} 篇/章；"
          f"{WORKS[work]['source_note']}", flush=True)
    if limit:
        units = units[:limit]
    translate = make_translate_fn(engine, work)
    chunks = mc.assemble_multilang_chunks(units, translate, ["grc", "en"],
                                          volume=WORKS[work]["title_zh"])
    for chunk, unit in zip(chunks, units):
        chunk["page_number"] = unit["page_number"]
    chunks = _prepend_cover(work, chunks)
    out = Path(f"c:/tmp/epictetus_{work}.jsonl")
    mc.write_jsonl(chunks, out)
    print(f"  ✓ {out.name}: {len(chunks)} chunks / "
          f"{sum(len(c['content']) for c in chunks):,} 繁中字", flush=True)
    if upload:
        ensure_ebook_row(work)
        from translate_collected_work import _upload

        _upload(WORKS[work]["ebook_id"], chunks, out)
    return chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("work", nargs="?", choices=list(WORKS))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--engine", choices=["auto", "gemini", "nvidia", "haiku", "sonnet"], default="auto")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list or (not args.work and not args.all):
        for slug, data in WORKS.items():
            print(f"  {slug:12} 愛比克泰德《{data['title_zh']}》 {data['ebook_id']}")
    elif args.all:
        for slug in ("handbook", "discourses", "fragments"):
            run(slug, engine=args.engine, limit=args.limit, upload=args.upload)
    else:
        run(args.work, engine=args.engine, limit=args.limit, upload=args.upload)
