# -*- coding: utf-8 -*-
"""普羅提諾《九章集》六集＋波菲利《普羅提諾生平》希／英／繁中管線。

來源：
* 希臘《九章集》：OpenGreekAndLatin/First1KGreek，Volkmann 1883–84 TEI
  (CC BY-SA 4.0)。
* 英譯《九章集》：CCEL 的 Stephen MacKenna / B. S. Page ThML
  (1917–1930，Public Domain)。
* 《普羅提諾生平》：Greek Wikisource 的 Volkmann 1883 原文，以及 English
  Wikisource 的 MacKenna 1917 英譯。

兩版都先切成「集.篇.節」。四篇的歷史版本分節數不同，會以單調 DP 合併相鄰
節為一個對齊單位；每個單位的 grc/en/zh 都壓成單段，避免 reader zipParallel
段落漂移。每個對齊單位翻完立即寫入 c:/tmp/plotinus_cache/<work>_zh/，可續傳。

用法：
  python scripts/plotinus_build.py --list
  python scripts/plotinus_build.py ennead-1 --engine auto --limit 2
  python scripts/plotinus_build.py ennead-1 --engine auto --upload
  python scripts/plotinus_build.py all --engine auto --upload
"""
from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import multilang_chunks as mc  # noqa: E402


CACHE = Path("c:/tmp/plotinus_cache")
GREEK_URL = (
    "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/"
    "data/tlg2000/tlg001/tlg2000.tlg001.1st1K-grc1.xml"
)
MACKENNA_URL = "https://www.ccel.org/ccel/plotinus/enneads.xml"
WIKISOURCE_API = {
    "grc": "https://el.wikisource.org/w/api.php",
    "en": "https://en.wikisource.org/w/api.php",
}
LIFE_EN_TITLE = "Plotinus (MacKenna)/Volume 1/Porphyry's Life of Plotinus"
LIFE_GRC_SEARCH = "Πλωτίνου βίου"

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
ZH_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六",
          7: "七", 8: "八", 9: "九"}
ENNEAD_TITLES = {
    1: "第一集：倫理與人生",
    2: "第二集：自然與宇宙",
    3: "第三集：宇宙、命運與時間",
    4: "第四集：論靈魂",
    5: "第五集：論智性",
    6: "第六集：存有與太一",
}


def _work(n: int) -> dict:
    return {
        "slug": f"ennead-{n}",
        "ebook_id": f"70000000-0000-4000-8000-{60 + n:012d}",
        "title_zh": ENNEAD_TITLES[n],
        "title_orig": f"Ἐννεὰς {ROMAN[n]} / Ennead {ROMAN[n]}",
        "ennead": n,
        "source_order": ["grc", "en"],
    }


WORKS: "OrderedDict[str, dict]" = OrderedDict((f"ennead-{n}", _work(n)) for n in range(1, 7))
WORKS["life"] = {
    "slug": "life",
    "ebook_id": "70000000-0000-4000-8000-000000000067",
    "title_zh": "波菲利《普羅提諾生平》",
    "title_orig": "Περὶ τοῦ Πλωτίνου βίου / Life of Plotinus",
    "source_order": ["grc", "en"],
}


# 對齊 greek_philosophy_glossary.md；希臘原文是權威，MacKenna 只供消歧義。
GLOSSARY = {
    "τὸ Ἕν": "太一",
    "νοῦς": "努斯",
    "ψυχή": "靈魂",
    "ὑπόστασις": "本體",
    "πρόοδος": "流出",
    "ἐπιστροφή": "回歸",
    "ἕνωσις": "合一",
    "οὐσία": "實體",
    "εἶδος / ἰδέα": "理型",
    "λόγος": "邏各斯",
}

PROMPT_TMPL = """你是古希臘哲學經典的專業譯者。請把下列普羅提諾／波菲利的古希臘原文直譯成繁體中文。

規則：
1. 嚴守繁體中文；忠實、流暢、保持古代哲學論證語氣，不加註、不改寫。
2. 希臘原文是權威；MacKenna 英譯只供消歧義，絕不可改成翻譯英文。
3. 術語鎖定：τὸ Ἕν→太一；νοῦς→努斯（專門本體語境）／心智（一般心理語境）；
   ψυχή→靈魂；ὑπόστασις→本體；πρόοδος→流出；ἐπιστροφή→回歸；
   ἕνωσις→合一；οὐσία→實體（依文脈可本質）；εἶδος/ἰδέα→理型；λόγος→邏各斯
   （一般文脈可譯言說／理性／論證）。整體學說可稱「流溢」，逐句的 procession 用「流出」。
4. 人名鎖定：Πλωτῖνος→普羅提諾；Πορφύριος→波菲利；Πλάτων→柏拉圖；
   Ἀριστοτέλης→亞里斯多德；Ἀμμώνιος Σακκᾶς→阿蒙尼烏斯‧薩卡斯。
5. 只輸出一段連續繁體中文；不要節號、標題、前言、說明、Markdown 水平線或額外分段。

[古希臘原文]
{grc}

[MacKenna 英譯參考（勿翻）]
{en}"""


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _flat(text: str) -> str:
    text = re.sub(r"[\u200b\ufeff\u2060]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _element_text(el: ET.Element, *, skip=("note", "pb", "del", "gap")) -> str:
    """Read mixed XML without page marks, apparatus deletions, or translator notes."""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        if _local(child.tag) not in skip:
            parts.append(_element_text(child, skip=skip))
        if child.tail:
            parts.append(child.tail)
    return _flat(" ".join(parts))


def _xml_root(xml: str | bytes) -> ET.Element:
    if isinstance(xml, bytes):
        return ET.fromstring(xml)
    return ET.fromstring(xml.encode("utf-8"))


def parse_greek_enneads(xml: str | bytes) -> dict[tuple[int, int], dict]:
    root = _xml_root(xml)
    out: dict[tuple[int, int], dict] = {}
    books = [e for e in root.iter() if _local(e.tag) == "div" and e.get("subtype") == "book"]
    for book in books:
        en = int(book.get("n", "0"))
        for chapter in [e for e in book if e.get("subtype") == "chapter"]:
            tr = int(chapter.get("n", "0"))
            head = next((e for e in chapter if _local(e.tag) == "head"), None)
            sections = []
            for section in [e for e in chapter if e.get("subtype") == "section"]:
                text = _element_text(section)
                if text:
                    sections.append((int(section.get("n", "0")), text))
            out[(en, tr)] = {"title": _element_text(head) if head is not None else "", "sections": sections}
    return out


_SECTION_RE = re.compile(r"^(\d+)\.\s*(.*)$", re.S)


def _group_numbered_paragraphs(paragraphs: Iterable[str], *, fallback_one=False) -> list[tuple[int, str]]:
    groups: list[tuple[int, list[str]]] = []
    expected = 1
    pending: list[str] = []
    for raw in paragraphs:
        text = _flat(raw)
        if not text:
            continue
        m = _SECTION_RE.match(text)
        if m and int(m.group(1)) == expected:
            if groups:
                groups[-1][1].extend(pending)
                pending = []
            groups.append((expected, [m.group(2).strip()]))
            expected += 1
        elif groups:
            pending.append(text)
    if groups:
        groups[-1][1].extend(pending)
    elif fallback_one:
        all_text = [_flat(p) for p in paragraphs if _flat(p)]
        if all_text:
            groups = [(1, all_text)]
    return [(n, _flat(" ".join(parts))) for n, parts in groups]


def parse_mackenna_enneads(xml: str | bytes) -> dict[tuple[int, int], dict]:
    root = _xml_root(xml)
    out: dict[tuple[int, int], dict] = {}
    books = [e for e in root.iter() if _local(e.tag) == "div1" and e.get("type") == "book"]
    for en, book in enumerate(books, start=1):
        chapters = [e for e in book if _local(e.tag) == "div2" and e.get("type") == "chapter"]
        for tr, chapter in enumerate(chapters, start=1):
            raw_title = chapter.get("title", "")
            title = re.sub(r"^[^.]+ Tractate\.\s*", "", raw_title, flags=re.I)
            paragraphs = [_element_text(p) for p in chapter if _local(p.tag) == "p"]
            out[(en, tr)] = {
                "title": title,
                "sections": _group_numbered_paragraphs(paragraphs, fallback_one=True),
            }
    return out


def align_sections(greek: list[tuple[int, str]], english: list[tuple[int, str]]) -> list[dict]:
    """Monotonic adjacent-group alignment; exact-count editions stay 1:1."""
    if not greek or not english:
        raise ValueError("both Greek and English sections are required")
    if len(greek) == len(english):
        pairs = [([g], [e]) for g, e in zip(greek, english)]
    else:
        gn, en = len(greek), len(english)
        gtotal = max(1, sum(len(t) for _, t in greek))
        etotal = max(1, sum(len(t) for _, t in english))
        inf = math.inf
        score = [[inf] * (en + 1) for _ in range(gn + 1)]
        back: list[list[tuple[int, int, int, int] | None]] = [[None] * (en + 1) for _ in range(gn + 1)]
        score[0][0] = 0.0
        for i in range(gn):
            for j in range(en):
                if score[i][j] == inf:
                    continue
                for a in range(1, min(3, gn - i) + 1):
                    for b in range(1, min(3, en - j) + 1):
                        glen = sum(len(t) for _, t in greek[i:i + a]) / gtotal
                        elen = sum(len(t) for _, t in english[j:j + b]) / etotal
                        cost = abs(glen - elen) + 0.012 * (a + b - 2)
                        nxt = score[i][j] + cost
                        if nxt < score[i + a][j + b]:
                            score[i + a][j + b] = nxt
                            back[i + a][j + b] = (i, j, a, b)
        if back[gn][en] is None:
            raise ValueError(f"cannot align {gn} Greek sections to {en} English sections")
        pairs = []
        i, j = gn, en
        while i or j:
            prev = back[i][j]
            if prev is None:
                raise ValueError("broken alignment backtrace")
            pi, pj, a, b = prev
            pairs.append((greek[pi:pi + a], english[pj:pj + b]))
            i, j = pi, pj
        pairs.reverse()

    out = []
    for gs, es in pairs:
        out.append({
            "grc_ids": [n for n, _ in gs],
            "en_ids": [n for n, _ in es],
            "grc": _flat(" ".join(text for _, text in gs)),
            "en": _flat(" ".join(text for _, text in es)),
        })
    return out


def _download(url: str, path: Path, *, min_bytes: int) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size < min_bytes:
        import requests
        response = requests.get(url, headers={"User-Agent": "know-graph-lab/1.0"}, timeout=180)
        response.raise_for_status()
        path.write_bytes(response.content)
    return path.read_text(encoding="utf-8")


def fetch_ennead_sources() -> tuple[str, str]:
    raw = CACHE / "raw"
    greek = _download(GREEK_URL, raw / "plotinus_volkmann_1883.xml", min_bytes=2_000_000)
    english = _download(MACKENNA_URL, raw / "plotinus_mackenna_ccel.xml", min_bytes=1_500_000)
    return greek, english


def _fetch_wikisource_html(lang: str) -> str:
    import requests
    raw = CACHE / "raw"
    path = raw / f"porphyry_life_{lang}.html"
    if path.exists() and path.stat().st_size > 20_000:
        return path.read_text(encoding="utf-8")
    session = requests.Session()
    session.headers["User-Agent"] = "know-graph-lab/1.0 (private research library)"
    api = WIKISOURCE_API[lang]
    if lang == "grc":
        search = session.get(api, params={
            "action": "query", "list": "search", "srsearch": LIFE_GRC_SEARCH,
            "srlimit": 10, "format": "json", "formatversion": 2,
        }, timeout=90)
        search.raise_for_status()
        hits = search.json().get("query", {}).get("search", [])
        title = next((hit["title"] for hit in hits if "Πλωτίνου βίου" in hit["title"]), None)
        if not title:
            raise RuntimeError("Greek Wikisource Life of Plotinus page not found")
    else:
        title = LIFE_EN_TITLE
    response = session.get(api, params={
        "action": "parse", "page": title, "prop": "text",
        "format": "json", "formatversion": 2,
    }, timeout=120)
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(f"Wikisource parse error: {data['error']}")
    html = data.get("parse", {}).get("text", "")
    if len(html) < 20_000:
        raise RuntimeError(f"Wikisource returned incomplete {lang} Life ({len(html)} bytes)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html


def _clean_soup_node(node) -> str:
    for bad in node.select(".pagenum, .ws-noexport, sup.reference, style, link"):
        bad.decompose()
    return _flat(node.get_text(" ", strip=True))


def parse_life_greek(html: str) -> list[tuple[int, str]]:
    soup = BeautifulSoup(html, "html.parser")
    first_marker = soup.find(id="p1")
    content = None
    if first_marker:
        content = next(
            (parent for parent in first_marker.parents if "prp-pages-output" in (parent.get("class") or [])),
            None,
        )
    content = content or soup.select_one(".mw-parser-output") or soup
    # One Wikisource page leaves the chapter-25 marker directly under the
    # transclusion div rather than inside a paragraph.  Tokenising every pN
    # marker before flattening keeps that malformed-but-readable page intact.
    for marker in content.find_all(id=re.compile(r"^p\d+$")):
        n = int(marker.get("id")[1:])
        marker.replace_with(f" §§P{n}§§ ")
    text = _clean_soup_node(content)
    pieces = re.split(r"§§P(\d+)§§", text)
    out: list[tuple[int, str]] = []
    for i in range(1, len(pieces), 2):
        n = int(pieces[i])
        body = re.sub(rf"^\s*(?:{n}\s*)?\.\s*", "", pieces[i + 1]).strip()
        if body:
            out.append((n, body))
    return out


def parse_life_english(html: str) -> list[tuple[int, str]]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(".prp-pages-output") or soup.select_one(".mw-parser-output") or soup
    # Four headings (7, 11, 13, 22) are bare text nodes in the transclusion,
    # not paragraphs.  Exact sequential heading tokens avoid confusing the
    # many numbered tractate lists inside chapters 4--6 and 24--26.
    expected = 1
    for node in list(content.find_all(string=True)):
        if _flat(str(node)) == f"{expected}.":
            node.replace_with(f" §§P{expected}§§ ")
            expected += 1
            if expected == 27:
                break
    text = _clean_soup_node(content)
    pieces = re.split(r"§§P(\d+)§§", text)
    out: list[tuple[int, str]] = []
    for i in range(1, len(pieces), 2):
        body = pieces[i + 1].strip()
        if body:
            out.append((int(pieces[i]), body))
    return out


def fetch_life_sources() -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    return parse_life_greek(_fetch_wikisource_html("grc")), parse_life_english(_fetch_wikisource_html("en"))


def _range_label(ids: list[int]) -> str:
    return str(ids[0]) if len(ids) == 1 else f"{ids[0]}–{ids[-1]}"


def build_ennead_units(slug: str, greek: dict, english: dict) -> list[dict]:
    work = WORKS[slug]
    en = work["ennead"]
    units = []
    for tr in range(1, 10):
        g = greek.get((en, tr))
        e = english.get((en, tr))
        if not g or not e:
            raise RuntimeError(f"missing source tractate {ROMAN[en]}.{tr}")
        for group in align_sections(g["sections"], e["sections"]):
            sec = _range_label(group["grc_ids"])
            anchor = f"{ROMAN[en]}.{tr}.{sec}"
            units.append({
                "anchor": anchor,
                "anchors": [anchor],
                "chapter_path": f"{work['title_zh']} · 第{ZH_NUM[tr]}篇 · 第{sec}節",
                "title_en": f"Ennead {ROMAN[en]}.{tr}.{sec} · {e['title']}",
                "volume": f"{work['title_zh']} · 第{ZH_NUM[tr]}篇",
                "parent_volume": "普羅提諾《九章集》",
                "page_number": len(units) + 1,
                "sources": {"grc": group["grc"], "en": group["en"]},
            })
    return units


def build_life_units(greek: list[tuple[int, str]], english: list[tuple[int, str]]) -> list[dict]:
    units = []
    for group in align_sections(greek, english):
        sec = _range_label(group["grc_ids"])
        anchor = f"Vita.{sec}"
        units.append({
            "anchor": anchor,
            "anchors": [anchor],
            "chapter_path": f"波菲利《普羅提諾生平》 · 第{sec}節",
            "title_en": f"Porphyry, Life of Plotinus {sec}",
            "volume": "波菲利《普羅提諾生平》",
            "parent_volume": "傳記與編纂",
            "page_number": len(units) + 1,
            "sources": {"grc": group["grc"], "en": group["en"]},
        })
    return units


def _safe_cache_name(anchor: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", anchor) + ".txt"


def _clean_translation(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(?:以下(?:是|為).{0,30}(?:翻譯|譯文)[：:]?\s*)", "", text)
    text = re.sub(r"^---+\s*", "", text)
    return _flat(text)


def make_translate_fn(engine: str, slug: str, *, engine_fn=None):
    if engine_fn is None:
        import translate_ebook_to_zh as te
        engines = {
            "auto": te.gemini_with_nvidia_fallback,
            "gemini": te.gemini_with_nvidia_fallback,
            "nvidia": te.nvidia_translate,
            "haiku": te.haiku_translate,
            "sonnet": te.sonnet_translate,
        }
        engine_fn = engines[engine]
    cdir = CACHE / f"{slug}_zh"
    cdir.mkdir(parents=True, exist_ok=True)

    def translate(unit: dict) -> str:
        path = cdir / _safe_cache_name(unit["anchor"])
        if path.exists():
            cached = _clean_translation(path.read_text(encoding="utf-8"))
            if cached:
                return cached
        prompt = PROMPT_TMPL.format(grc=unit["sources"]["grc"], en=unit["sources"]["en"])
        zh = _clean_translation(engine_fn(prompt))
        if not zh:
            raise RuntimeError(f"empty translation for {unit['anchor']}")
        path.write_text(zh, encoding="utf-8")
        print(f"  ↳ {unit['anchor']}", flush=True)
        return zh

    return translate


def _prepend_cover(slug: str, chunks: list[dict]) -> list[dict]:
    work = WORKS[slug]
    cover = mc.build_multilang_chunk(
        chunk_index=0, chapter_path="封面", content_zh="## 封面", sources={}, source_order=[],
        volume=work["title_zh"], parent_volume=("傳記與編纂" if slug == "life" else "普羅提諾《九章集》"),
        chunk_type="cover", page_number=1,
    )
    mc.validate_multilang_chunk(cover)
    for i, chunk in enumerate(chunks, start=1):
        chunk["chunk_index"] = i
    return [cover, *chunks]


def ensure_ebook_row(slug: str) -> None:
    import requests
    import translate_ebook_to_zh as te
    work = WORKS[slug]
    response = requests.get(
        f"{te.URL}/rest/v1/ebooks?id=eq.{work['ebook_id']}&select=id", headers=te.H_GET, timeout=30,
    )
    if response.ok and response.json():
        return
    row = {
        "id": work["ebook_id"], "title": f"{work['title_zh']}（希英繁三欄）",
        "author": "普羅提諾" if slug != "life" else "波菲利", "author_en": "Plotinus" if slug != "life" else "Porphyry",
        "file_type": "epub", "file_path": f"PERSEUS/plotinus-{slug}-trilingual",
        "category": "世界宗教", "subcategory": "古希臘哲學", "original_title": work["title_orig"],
        "translator": "AI 輔助（希臘原文直譯）", "display_mode": "standard",
        "collection": "collected-works",
    }
    requests.post(f"{te.URL}/rest/v1/ebooks", headers=te.H_JSON, json=row, timeout=30).raise_for_status()
    print(f"  ✓ inserted ebooks row {work['ebook_id']}")


def load_units(slug: str) -> list[dict]:
    if slug == "life":
        greek, english = fetch_life_sources()
        if len(greek) != 26 or len(english) != 26:
            raise RuntimeError(f"Life source incomplete: grc={len(greek)} en={len(english)} (expected 26/26)")
        return build_life_units(greek, english)
    greek_xml, english_xml = fetch_ennead_sources()
    greek = parse_greek_enneads(greek_xml)
    english = parse_mackenna_enneads(english_xml)
    if len(greek) != 54 or len(english) != 54:
        raise RuntimeError(f"Enneads source incomplete: grc={len(greek)} en={len(english)} (expected 54/54)")
    return build_ennead_units(slug, greek, english)


def run(slug: str, *, engine="auto", limit=None, upload=False) -> list[dict]:
    units = load_units(slug)
    total = len(units)
    cached = sum((CACHE / f"{slug}_zh" / _safe_cache_name(u["anchor"])).exists() for u in units)
    print(f"[{slug}] {WORKS[slug]['title_zh']} {cached}/{total} cached", flush=True)
    if limit is not None:
        units = units[:limit]
    translate = make_translate_fn(engine, slug)
    chunks = mc.assemble_multilang_chunks(units, translate, ["grc", "en"])
    for chunk, unit in zip(chunks, units):
        chunk["page_number"] = unit["page_number"]
    chunks = _prepend_cover(slug, chunks)
    out = Path(f"c:/tmp/plotinus_{slug}.jsonl")
    mc.write_jsonl(chunks, out)
    print(f"  ✓ {out.name}: {len(chunks)} chunks", flush=True)
    if upload:
        if limit is not None:
            raise RuntimeError("refusing to upload a --limit smoke-test build")
        ensure_ebook_row(slug)
        from translate_collected_work import _upload
        _upload(WORKS[slug]["ebook_id"], chunks, out)
    return chunks


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("work", nargs="?", choices=[*WORKS, "all"])
    parser.add_argument("--engine", default="auto", choices=["auto", "gemini", "nvidia", "haiku", "sonnet"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list or not args.work:
        for slug, work in WORKS.items():
            print(f"  {slug:10} {work['title_zh']} {work['ebook_id']}")
        return
    slugs = list(WORKS) if args.work == "all" else [args.work]
    for slug in slugs:
        run(slug, engine=args.engine, limit=args.limit, upload=args.upload)


if __name__ == "__main__":
    main()
