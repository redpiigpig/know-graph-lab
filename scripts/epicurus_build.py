# -*- coding: utf-8 -*-
"""伊比鳩魯傳世核心文本 -> 希臘／英／繁中三欄全集。

來源（均為公有領域校本／譯本）：

* 三封書信、主要教義：Perseus canonical-greekLit，Usener 希臘校本與
  R. D. Hicks 英譯的《名哲言行錄》卷十。
* 梵蒂岡格言集：OpenGreekAndLatin First1KGreek 的 von der Muehll 1922
  希臘校本；英譯採 Cyril Bailey 1926《Epicurus: The Extant Remains》
  Internet Archive 掃描本。Bailey 未重印與《主要教義》重複的格言，
  依固定對應條號回填 Hicks 的公有領域英譯。

用法：
  python scripts/epicurus_build.py --list
  python scripts/epicurus_build.py herodotus --inspect
  python scripts/epicurus_build.py herodotus --engine nvidia --limit 2
  python scripts/epicurus_build.py --all --engine auto --resume --upload

每一《名哲言行錄》節／每一格言都獨立快取於
``c:/tmp/epicurus_cache/<work>_zh/<anchor>.txt``；重跑即續傳，同一 work
不可同時開兩個 process。
"""
from __future__ import annotations

import argparse
import copy
import io
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import quote

from lxml import etree

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
sys.path.insert(0, str(Path(__file__).resolve().parent))
import multilang_chunks as mc  # noqa: E402


CACHE = Path("c:/tmp/epicurus_cache")
SOURCE_CACHE = CACHE / "sources"
PERSEUS_GRC = (
    "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/"
    "data/tlg0004/tlg001/tlg0004.tlg001.perseus-grc2.xml"
)
PERSEUS_ENG = (
    "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/"
    "data/tlg0004/tlg001/tlg0004.tlg001.perseus-eng2.xml"
)
VATICAN_GRC = (
    "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/"
    "data/tlg0537/tlg014/tlg0537.tlg014.1st1K-grc1.xml"
)
BAILEY_IA_ID = "EpicurusTheExtantRemainsBaileyOxford1926OptimizedForGreekOnLeft"
BAILEY_EPUB = "Epicurus-the-Extant-Remains-Bailey-Oxford-1926 Optimized for Greek on Left.epub"

_NS = {"t": "http://www.tei-c.org/ns/1.0"}
_PARENT = "伊比鳩魯傳世著作"

WORKS = {
    "herodotus": {
        "ebook_id": "71000000-0000-4000-8000-000000000001",
        "title_zh": "致希羅多德書（論自然綱要）",
        "title_orig": "Ἐπιστολὴ πρὸς Ἡρόδοτον",
        "range": (35, 83),
        "kind": "letter",
    },
    "pythocles": {
        "ebook_id": "71000000-0000-4000-8000-000000000002",
        "title_zh": "致皮托克勒書（論天象）",
        "title_orig": "Ἐπιστολὴ πρὸς Πυθοκλέα",
        "range": (84, 116),
        "kind": "letter",
    },
    "menoeceus": {
        "ebook_id": "71000000-0000-4000-8000-000000000003",
        "title_zh": "致梅諾寇書（論倫理與幸福）",
        "title_orig": "Ἐπιστολὴ πρὸς Μενοικέα",
        "range": (121, 135),
        "kind": "letter",
    },
    "principal-doctrines": {
        "ebook_id": "71000000-0000-4000-8000-000000000004",
        "title_zh": "主要教義",
        "title_orig": "Κύριαι Δόξαι",
        "kind": "doctrines",
    },
    "vatican-sayings": {
        "ebook_id": "71000000-0000-4000-8000-000000000005",
        "title_zh": "梵蒂岡格言集",
        "title_orig": "Γνωμολόγιον Βατικανὸν Ἐπικούρειον",
        "kind": "vatican",
    },
}


PROMPT_TMPL = """你是古希臘哲學經典的專業譯者。把下列**古希臘文原典**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；學術散文語氣，忠實、清楚、流暢，不加註、不改寫。
2. 從希臘原文翻譯；附上的英譯只供消歧義參考，**不要翻譯英文**。
3. 人名依翻譯定名：Ἐπίκουρος→伊比鳩魯、Ἡρόδοτος→希羅多德、
   Πυθοκλῆς→皮托克勒、Μενοικεύς→梅諾寇、Μητρόδωρος→梅特羅多洛。
4. 術語鎖定（希臘為準）：ἡδονή→快樂、ἀταραξία→心靈的寧靜、
   ἀπονία→身體無痛、φρόνησις→實踐智慧、ἀρετή→德性、ψυχή→靈魂、
   αἴσθησις→感覺、πρόληψις→預概念、ἄτομον/κενόν→原子/虛空、
   φύσις→自然（本性）、ἀνάγκη→必然、τύχη→機運、αὐτάρκεια→自足、
   φιλία→友誼、δικαιοσύνη→正義、ἐπιθυμία→欲望、τέλος→目的（終點）。
5. **只輸出一段連續的繁體中文譯文**，不要分段、不要條號、不要前言或說明。

{source}"""


_DOCTRINES_BY_DL_SECTION = {
    139: (1, 2, 3),
    140: (4, 5),
    141: (6, 7, 8),
    142: (9, 10, 11),
    143: (12, 13, 14),
    144: (15, 16, 17, 18),
    145: (19, 20),
    146: (21, 22, 23),
    147: (24,),
    148: (25, 26, 27, 28),
    149: (29, 30),
    150: (31, 32, 33),
    151: (34, 35, 36),
    152: (37,),
    153: (38,),
    154: (39, 40),
}

# Bailey 1926 不重印的 Vatican sayings；數值是對應的 Principal Doctrine。
_VATICAN_PD_DUPLICATES = {
    1: 1,
    2: 2,
    3: 4,
    5: 5,
    6: 35,
    8: 15,
    12: 17,
    13: 27,
    20: 29,
    22: 19,
    49: 12,
    50: 8,
    72: 13,
}

_BAILEY_PAGE_ITEMS = {
    106: (4, 7, 9, 10, 11, 14),
    108: (15, 16, 17, 18, 19, 21, 23, 24, 25, 26, 27),
    110: (28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39),
    112: (40, 41, 42, 43, 44, 45, 46, 47, 48),
    114: (51, 52, 53, 54, 55, 56, 58, 59, 60, 61),
    116: (62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 73, 74),
    118: tuple(range(75, 82)),
}
_BAILEY_FIRST_MARKER = {106: "IV.", 108: "XV.", 110: "XXVIII.", 112: "XL.", 114: "LI.", 116: "LXII.", 118: "LXXV."}
_ROMAN_OCR_RE = re.compile(
    r"(?<![A-Za-zΑ-Ωα-ω])\[?[IVXLCDMAEKS]{1,12}(?:-[IVXLCDMAEKS]{1,12})?[\.,](?=\s)"
)


def _download(url: str, dest: Path, *, timeout: int = 180) -> Path:
    import requests

    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    last = None
    for attempt in range(3):
        try:
            with requests.get(url, timeout=(20, timeout), stream=True) as r:
                r.raise_for_status()
                with dest.open("wb") as f:
                    for chunk in r.iter_content(65536):
                        if chunk:
                            f.write(chunk)
            if dest.stat().st_size <= 1000:
                raise RuntimeError(f"download too small: {dest}")
            return dest
        except Exception as exc:  # pragma: no cover - network retry
            last = exc
            if dest.exists():
                dest.unlink()
            time.sleep(2**attempt)
    raise RuntimeError(f"download failed: {url}: {last}")


def _download_bailey_epub(dest: Path) -> Path:
    """Use IA metadata to avoid a slow random redirect host."""
    import requests

    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    meta = requests.get(f"https://archive.org/metadata/{BAILEY_IA_ID}", timeout=60)
    meta.raise_for_status()
    data = meta.json()
    host = data.get("d1") or data.get("d2") or "archive.org"
    directory = data.get("dir") or f"/download/{BAILEY_IA_ID}"
    return _download(f"https://{host}{directory}/{quote(BAILEY_EPUB)}", dest)


def fetch_sources(*, need_vatican: bool = False) -> dict[str, Path]:
    paths = {
        "dl_grc": _download(PERSEUS_GRC, SOURCE_CACHE / "diogenes-laertius-book10-grc.xml"),
        "dl_en": _download(PERSEUS_ENG, SOURCE_CACHE / "diogenes-laertius-book10-hicks-en.xml"),
    }
    if need_vatican:
        paths["vat_grc"] = _download(VATICAN_GRC, SOURCE_CACHE / "vatican-sayings-von-der-muehll-grc.xml")
        paths["bailey_epub"] = _download_bailey_epub(SOURCE_CACHE / "bailey-1926-extant-remains.epub")
    return paths


def _drop_preserve_tail(el) -> None:
    parent = el.getparent()
    if parent is None:
        return
    tail = el.tail or ""
    prev = el.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or "") + tail
    else:
        parent.text = (parent.text or "") + tail
    parent.remove(el)


def clean_element(el, *, lang: str) -> str:
    node = copy.deepcopy(el)
    for bad in node.xpath('.//*[local-name()="note" or local-name()="bibl"]'):
        _drop_preserve_tail(bad)
    for bad in node.xpath('.//*[local-name()="pb"]'):
        _drop_preserve_tail(bad)
    text = " ".join("".join(node.itertext()).split())
    if lang == "grc":
        text = re.sub(r"([Α-ωἀ-῾])[-‐]\s+([Α-ωἀ-῾])", r"\1\2", text)
    return text.strip()


def _book10(tree: etree._ElementTree):
    found = tree.xpath('//t:div[@subtype="book" and @n="10"]', namespaces=_NS)
    if len(found) != 1:
        raise ValueError(f"expected exactly one Book X, found {len(found)}")
    return found[0]


def _section(book, n: int):
    found = book.xpath(f'.//t:div[@subtype="section" and @n="{n}"]', namespaces=_NS)
    if len(found) != 1:
        raise ValueError(f"expected one DL 10.{n}, found {len(found)}")
    return found[0]


def parse_letter_sections(grc_xml: bytes | str, en_xml: bytes | str, start: int, end: int) -> list[dict]:
    grc_book = _book10(_parse_xml(grc_xml))
    en_book = _book10(_parse_xml(en_xml))
    out = []
    for n in range(start, end + 1):
        grc = clean_element(_section(grc_book, n), lang="grc")
        en = clean_element(_section(en_book, n), lang="en")
        if n == 121:
            grc = _trim_from(grc, "Ἐπίκουρος Μενοικεῖ χαίρειν")
            en = _trim_from(en, "Epicurus to Menoeceus, greeting")
        if not grc or not en:
            raise ValueError(f"empty aligned text at DL 10.{n}")
        out.append({"id": f"DL10.{n}", "grc": grc, "en": en})
    return out


def _parse_xml(value: bytes | str) -> etree._ElementTree:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return etree.ElementTree(etree.fromstring(value))


def _trim_from(text: str, marker: str) -> str:
    pos = text.find(marker)
    if pos < 0:
        raise ValueError(f"marker not found: {marker}")
    return text[pos:].strip()


def _roman_to_int(value: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    s = re.sub(r"[^IVXLCDM]", "", value.upper())
    total = prev = 0
    for ch in reversed(s):
        n = vals[ch]
        total += -n if n < prev else n
        prev = max(prev, n)
    return total


def _split_numbered_english(text: str, expected: tuple[int, ...]) -> dict[int, str]:
    # Select the expected headings in order. Doctrine prose and editorial
    # matter can itself contain ``1.``-style references, so collecting every
    # number-like token would create false duplicate headings.
    selected = []
    cursor = 0
    for n in expected:
        match = re.search(rf"(?<!\d){n}\.\s+", text[cursor:])
        if not match:
            raise ValueError(f"English doctrine heading {n} missing; expected {expected}")
        start = cursor + match.start()
        end = cursor + match.end()
        selected.append((n, start, end))
        cursor = end
    out = {}
    for i, (n, _start, content_start) in enumerate(selected):
        end = selected[i + 1][1] if i + 1 < len(selected) else len(text)
        out[n] = text[content_start:end].strip()
    return out


def parse_principal_doctrines(grc_xml: bytes | str, en_xml: bytes | str) -> list[dict]:
    grc_book = _book10(_parse_xml(grc_xml))
    en_book = _book10(_parse_xml(en_xml))
    grc_items: dict[int, str] = {}
    en_items: dict[int, str] = {}
    for dl_section, expected in _DOCTRINES_BY_DL_SECTION.items():
        grc_section = _section(grc_book, dl_section)
        # In Perseus the <add>[<foreign>I.</foreign>]</add> marker closes
        # before the doctrine text, so the Greek itself is in add.tail.
        grc_text = clean_element(grc_section, lang="grc")
        markers = list(re.finditer(r"\[\s*([IVXLCDM]+)\.\s*\]\s*", grc_text))
        numbered = [(m, _roman_to_int(m.group(1))) for m in markers if _roman_to_int(m.group(1)) in expected]
        if [n for _m, n in numbered] != list(expected):
            raise ValueError(
                f"Greek doctrine numbering mismatch in DL 10.{dl_section}: "
                f"got {[n for _m, n in numbered]}, expected {expected}"
            )
        for i, (marker, n) in enumerate(numbered):
            end = numbered[i + 1][0].start() if i + 1 < len(numbered) else len(grc_text)
            grc_items[n] = grc_text[marker.end():end].strip(" []")
        en_text = clean_element(_section(en_book, dl_section), lang="en")
        en_items.update(_split_numbered_english(en_text, expected))
    if set(grc_items) != set(range(1, 41)) or set(en_items) != set(range(1, 41)):
        raise ValueError(f"principal doctrines incomplete: grc={sorted(grc_items)} en={sorted(en_items)}")
    return [{"id": f"PD.{n}", "grc": grc_items[n], "en": en_items[n]} for n in range(1, 41)]


def parse_vatican_greek(xml: bytes | str) -> dict[int, str]:
    tree = _parse_xml(xml)
    out = {}
    for n in range(1, 82):
        found = tree.xpath(f'//t:div[@subtype="section" and @n="{n}"]', namespaces=_NS)
        if len(found) != 1:
            raise ValueError(f"Vatican Saying {n}: expected one Greek section, found {len(found)}")
        out[n] = clean_element(found[0], lang="grc")
    return out


def _page_text(zf: zipfile.ZipFile, page: int) -> str:
    from bs4 import BeautifulSoup

    raw = zf.read(f"EPUB/page_{page}.html")
    text = BeautifulSoup(raw, "html.parser").get_text(" ")
    return " ".join(text.split())


def _bailey_ocr_cleanup(text: str) -> str:
    fixes = {
        "ttme": "time",
        "himeelf": "himself",
        "o!d": "old",
        "!ived": "lived",
        "hke": "like",
        "T would": "I would",
        "1s": "is",
        "1n": "in",
        "1t": "it",
        "teo": "too",
        "rmpossible": "impossible",
        "proclaim: ing": "proclaiming",
        "highspirited": "high-spirited",
        "securnty": "security",
        " hfe ": " life ",
        " byt ": " but ",
        " Ina ": " In a ",
    }
    for old, new in fixes.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip(" []{}᾿")


def _split_bailey_page(text: str, page: int) -> tuple[str, dict[int, str]]:
    """Return (unmarked continuation prefix, numbered sayings) for one OCR page."""
    first = _BAILEY_FIRST_MARKER[page]
    start = text.find(first)
    if start < 0:
        raise ValueError(f"Bailey page {page}: first marker {first} missing")
    prefix = text[:start]
    if "FRAGMENTS" in prefix:
        prefix = prefix.split("FRAGMENTS", 1)[1]
        prefix = re.sub(r"^\s*(?:\d+|τόρ|\.\s*[a-zA-Z]+)\s*", "", prefix)
    body = text[start:]
    stop_tokens = {
        106: "Kareides]",
        108: "μεθα ",
        112: "XLVUI 1",
        114: "τοῦ φίλον",
        116: "σθαι κτήματα",
    }
    stop = stop_tokens.get(page)
    if stop and stop in body:
        body = body[:body.index(stop)]
    body = body.translate(str.maketrans({"Χ": "X", "Ι": "I"}))
    matches = list(_ROMAN_OCR_RE.finditer(body))
    expected = _BAILEY_PAGE_ITEMS[page]
    if len(matches) != len(expected):
        raise ValueError(f"Bailey page {page}: got {len(matches)} sayings, expected {len(expected)}")
    out = {}
    for i, (n, marker) in enumerate(zip(expected, matches)):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out[n] = _bailey_ocr_cleanup(body[marker.end():end])
    return _bailey_ocr_cleanup(prefix), out


def parse_bailey_vatican_english(epub_path: Path, pd_english: dict[int, str]) -> dict[int, str]:
    out: dict[int, str] = {}
    with zipfile.ZipFile(epub_path) as zf:
        prefixes = {}
        for page in _BAILEY_PAGE_ITEMS:
            prefix, items = _split_bailey_page(_page_text(zf, page), page)
            prefixes[page] = prefix
            out.update(items)
    # Facing-page OCR splits the final sentence of 14, 27, and 39 across pages.
    for target, page, needle in (
        (14, 108, "wasted in procrastination"),
        (27, 110, "fully after completion"),
        (39, 112, "For the former"),
    ):
        prefix = prefixes[page]
        pos = prefix.find(needle)
        if pos < 0:
            raise ValueError(f"Bailey continuation missing on page {page}: {needle}")
        out[target] = _bailey_ocr_cleanup(f"{out[target]} {prefix[pos:]}")
    # Bailey prints 56-57 as one restored sentence; split at the colon.
    both = out.pop(56)
    left, sep, right = both.partition(":")
    if not sep:
        raise ValueError("Bailey VS 56-57 combined sentence has no split colon")
    out[56] = left.strip() + ":"
    out[57] = right.strip()
    for vs, pd in _VATICAN_PD_DUPLICATES.items():
        out[vs] = pd_english[pd]
    if set(out) != set(range(1, 82)):
        raise ValueError(f"Vatican English incomplete: {sorted(out)}")
    return out


def build_source_items(work: str, paths: dict[str, Path]) -> list[dict]:
    d = WORKS[work]
    grc_xml = paths["dl_grc"].read_bytes()
    en_xml = paths["dl_en"].read_bytes()
    if d["kind"] == "letter":
        return parse_letter_sections(grc_xml, en_xml, *d["range"])
    doctrines = parse_principal_doctrines(grc_xml, en_xml)
    if d["kind"] == "doctrines":
        return doctrines
    grc = parse_vatican_greek(paths["vat_grc"].read_bytes())
    pd_en = {int(item["id"].split(".")[1]): item["en"] for item in doctrines}
    en = parse_bailey_vatican_english(paths["bailey_epub"], pd_en)
    return [{"id": f"VS.{n}", "grc": grc[n], "en": en[n]} for n in range(1, 82)]


def build_units(work: str, items: list[dict]) -> list[dict]:
    d = WORKS[work]
    units = []
    for item in items:
        anchor = item["id"]
        label = anchor.replace("DL10.", "DL 10.").replace("PD.", "PD ").replace("VS.", "VS ")
        units.append(
            {
                "chapter_path": f"{d['title_zh']} · {label}",
                "page_number": len(units) + 1,
                "volume": d["title_zh"],
                "parent_volume": _PARENT,
                "title_en": label,
                "sources": {"grc": item["grc"], "en": item["en"]},
                "anchors": [label],
                "_cache_id": anchor,
            }
        )
    return units


def make_translate_fn(engine: str, work: str, *, cache_root: Path = CACHE):
    import translate_ebook_to_zh as te

    te.PROMPT_TMPL = PROMPT_TMPL
    engines = {
        "auto": te.gemini_with_haiku_fallback,
        "gemini": te.gemini_with_haiku_fallback,
        "nvidia": te.nvidia_translate,
        "haiku": te.haiku_translate,
        "sonnet": te.sonnet_translate,
    }
    engine_fn = engines[engine]
    cdir = cache_root / f"{work}_zh"
    cdir.mkdir(parents=True, exist_ok=True)

    def translate_fn(unit: dict) -> str:
        safe = re.sub(r"[^\w.-]", "_", unit["_cache_id"])
        cached_file = cdir / f"{safe}.txt"
        if cached_file.exists():
            cached = cached_file.read_text(encoding="utf-8").strip()
            if cached:
                return re.sub(r"\s+", " ", cached).strip()
        source = f"{unit['sources']['grc']}\n\n[既有英譯參考（勿翻）]\n{unit['sources']['en']}"
        zh = re.sub(r"\s+", " ", engine_fn(source)).strip()
        if not zh:
            raise RuntimeError(f"empty translation: {unit['_cache_id']}")
        cached_file.write_text(zh, encoding="utf-8")
        print(f"  ↳ {unit['chapter_path']}")
        return zh

    return translate_fn


def _prepend_cover(work: str, chunks: list[dict]) -> list[dict]:
    d = WORKS[work]
    cover = mc.build_multilang_chunk(
        chunk_index=0,
        chapter_path="封面",
        content_zh="## 封面",
        sources={},
        source_order=[],
        volume=d["title_zh"],
        parent_volume=_PARENT,
        chunk_type="cover",
        page_number=1,
    )
    for i, chunk in enumerate(chunks, start=1):
        chunk["chunk_index"] = i
    return [cover] + chunks


def ensure_ebook_row(work: str) -> None:
    import requests
    import translate_ebook_to_zh as te

    d = WORKS[work]
    response = requests.get(f"{te.URL}/rest/v1/ebooks?id=eq.{d['ebook_id']}&select=id", headers=te.H_GET, timeout=30)
    if response.ok and response.json():
        return
    row = {
        "id": d["ebook_id"],
        "title": f"{d['title_zh']}（希英繁三欄）",
        "author": "伊比鳩魯",
        "author_en": "Epicurus",
        "file_type": "epub",
        "file_path": f"PERSEUS/epicurus-{work}-trilingual",
        "category": "世界宗教",
        "subcategory": "古希臘哲學",
        "original_title": d["title_orig"],
        "translator": "AI 輔助（希臘原文直譯）",
        "display_mode": "standard",
        "collection": "collected-works",
    }
    requests.post(f"{te.URL}/rest/v1/ebooks", headers=te.H_JSON, json=row, timeout=30).raise_for_status()
    print(f"  ✓ inserted ebooks row {d['ebook_id']}")


def inspect(work: str) -> list[dict]:
    paths = fetch_sources(need_vatican=WORKS[work]["kind"] == "vatican")
    items = build_source_items(work, paths)
    total_grc = sum(len(x["grc"]) for x in items)
    total_en = sum(len(x["en"]) for x in items)
    cached = CACHE / f"{work}_zh"
    completed = sum(1 for p in cached.glob("*.txt") if p.read_text(encoding="utf-8").strip()) if cached.exists() else 0
    print(f"[{work}] {WORKS[work]['title_zh']} items={len(items)} grc={total_grc} en={total_en} cache={completed}/{len(items)}")
    return items


def run(work: str, *, engine: str = "auto", limit: int | None = None, upload: bool = False) -> list[dict]:
    paths = fetch_sources(need_vatican=WORKS[work]["kind"] == "vatican")
    items = build_source_items(work, paths)
    print(f"[{work}] 伊比鳩魯《{WORKS[work]['title_zh']}》 {len(items)} items")
    if limit is not None:
        items = items[:limit]
    units = build_units(work, items)
    translate_fn = make_translate_fn(engine, work)
    chunks = mc.assemble_multilang_chunks(units, translate_fn, ["grc", "en"], volume=WORKS[work]["title_zh"])
    for chunk, unit in zip(chunks, units):
        chunk["page_number"] = unit["page_number"]
        chunk["anchors"] = unit["anchors"]
    chunks = _prepend_cover(work, chunks)
    for chunk in chunks[1:]:
        nz = len(chunk["content"].split("\n\n"))
        ng = len(chunk["sources"]["grc"].split("\n\n"))
        ne = len(chunk["sources"]["en"].split("\n\n"))
        if not (nz == ng == ne == len(chunk.get("anchors", []))):
            raise ValueError(f"alignment failed at chunk {chunk['chunk_index']}: zh={nz} grc={ng} en={ne}")
    out = Path(f"c:/tmp/epicurus_{work}.jsonl")
    mc.write_jsonl(chunks, out)
    print(f"  ✓ {out.name} {len(chunks)} chunks / {sum(len(c['content']) for c in chunks)} 繁中字")
    if upload:
        ensure_ebook_row(work)
        from translate_collected_work import _upload

        _upload(WORKS[work]["ebook_id"], chunks, out)
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("work", nargs="?", choices=list(WORKS))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--engine", choices=("auto", "gemini", "nvidia", "haiku", "sonnet"), default="auto")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true", help="accepted explicitly; cache resume is always on")
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()
    if args.list or (not args.work and not args.all):
        for slug, d in WORKS.items():
            print(f"  {slug:20} {d['title_zh']} {d['ebook_id']}")
        return
    selected = list(WORKS) if args.all else [args.work]
    for work in selected:
        if args.inspect:
            inspect(work)
        else:
            run(work, engine=args.engine, limit=args.limit, upload=args.upload)


if __name__ == "__main__":
    main()
