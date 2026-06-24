#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build a first-pass source-driven catalog for /dazangjing.

The output is intentionally a candidate list, not curated canon data. It records
which library/archive a title came from so later passes can deduplicate, verify,
date, and classify each work into era x collection x zheng/wai.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "dazangjing" / "source-catalog"

SEED_QUERIES = [
    "Augustine De civitate Dei",
    "Athanasius De incarnatione",
    "Eusebius Historia ecclesiastica",
    "John Chrysostom homiliae",
    "Gregory Nazianzen orationes",
    "Basil Caesarea Hexaemeron",
    "Corpus iuris canonici",
    "Thomas Aquinas Summa theologiae",
    "Bonaventure Itinerarium mentis in Deum",
    "Meister Eckhart sermons",
    "Martin Luther De servo arbitrio",
    "Calvin Institutio religionis christianae",
    "Book of Common Prayer",
    "Philokalia",
    "Symeon Metaphrastes Menologion",
    "Michael the Syrian Chronicle",
    "Bar Hebraeus Chronicon Ecclesiasticum",
    "Codex Vaticanus",
    "Septuagint",
    "Nag Hammadi Library",
    "Coptic Synaxarium",
    "Shenoute Canons",
    "Agathangelos History of the Armenians",
    "Gregory of Narek Book of Lamentations",
    "Kebra Nagast",
    "Gadla Takla Haymanot",
    "Ephrem Syriac hymns",
    "Jacob of Serugh homilies",
    "Book of the Himyarites",
    "Martyrdom of Shushanik",
    "Life of Nino",
]

# Eastern-tradition + diversity-first queries (user 2026-06-24: 越東方／越多元越優先；
# 西方希臘/拉丁教父於既有 corpus 已飽和，增量在科普特/敘利亞/亞美尼亞/喬治亞/衣索匹亞/
# 阿拉伯基督教/波斯景教，以及女性與非西方作者）。
EASTERN_QUERIES = [
    # Coptic
    "Shenoute of Atripe canons", "Besa life of Shenoute", "Pachomius koinonia rules",
    "Coptic Synaxarium", "Paphnutius histories monks Upper Egypt", "Severus ibn al-Muqaffa History Patriarchs",
    # Ethiopic / Ge'ez
    "Fetha Nagast", "Ethiopian Synaxarium", "Gadla Lalibela", "Giyorgis of Sagla Book of Mystery",
    "Zara Yaqob Mahafa Berhan", "Taamra Maryam miracles of Mary", "Gädlä Täklä Haymanot",
    # Syriac
    "Jacob of Serugh memre", "Narsai homilies", "Isaac of Nineveh ascetical homilies",
    "Aphrahat Demonstrations", "John of Ephesus Lives Eastern Saints", "Babai the Great",
    "Acts of the Persian Martyrs", "History of Mar Aba", "Book of the Bee Solomon of Basra",
    # Armenian
    "Movses Khorenatsi History of Armenians", "Eznik of Kolb Against the Sects",
    "Yeghishe Vardan Armenian War", "Koriun Life of Mashtots", "Nerses Shnorhali",
    "Gregory of Narek Book of Lamentations",
    # Georgian
    "Giorgi Mtatsmindeli", "Ioane Zosime", "Martyrdom of Abo of Tiflis", "Georgian Chronicles Kartlis Tskhovreba",
    # Arabic Christian
    "Theodore Abu Qurrah", "Eutychius of Alexandria Annals", "Sawirus ibn al-Muqaffa",
    # Women / non-Western voices
    "Egeria Itinerarium pilgrimage", "Life of Macrina Gregory of Nyssa", "Life of Melania the Younger",
    "Life of Mary of Egypt", "Sayings Desert Mothers ammas", "Perpetua Felicitas passion",
    "Heliand Old Saxon gospel", "Ethiopic Book of Enoch", "Nubian Christian texts Old Dongola",
]

REPOSITORIES: list[dict[str, Any]] = [
    {
        "key": "loc",
        "name": "Library of Congress",
        "country": "US",
        "mode": "loc_json",
        "endpoint": "https://www.loc.gov/books/",
        "status": "api",
    },
    {
        "key": "dnb",
        "name": "Deutsche Nationalbibliothek",
        "country": "DE",
        "mode": "dnb_sru",
        "endpoint": "https://services.dnb.de/sru/dnb",
        "status": "sru",
    },
    {
        "key": "bnf",
        "name": "Bibliotheque nationale de France",
        "country": "FR",
        "mode": "bnf_sru",
        "endpoint": "https://catalogue.bnf.fr/api/SRU",
        "status": "sru",
    },
    {
        "key": "openlibrary",
        "name": "Open Library",
        "country": "global",
        "mode": "openlibrary_json",
        "endpoint": "https://openlibrary.org/search.json",
        "status": "api",
    },
    {
        "key": "archive_org",
        "name": "Internet Archive",
        "country": "global",
        "mode": "archive_json",
        "endpoint": "https://archive.org/advancedsearch.php",
        "status": "api",
    },
    {
        "key": "bl",
        "name": "British Library",
        "country": "UK",
        "mode": "manual",
        "endpoint": "https://search.bl.uk/",
        "status": "manual_queue",
        "note": "No stable public JSON/SRU endpoint confirmed in this pass.",
    },
    {
        "key": "rsl",
        "name": "Russian State Library",
        "country": "RU",
        "mode": "manual",
        "endpoint": "https://www.rsl.ru/",
        "status": "manual_queue",
    },
    {
        "key": "nlr",
        "name": "National Library of Russia",
        "country": "RU",
        "mode": "manual",
        "endpoint": "https://nlr.ru/",
        "status": "manual_queue",
    },
    {
        "key": "vatican_library",
        "name": "Biblioteca Apostolica Vaticana",
        "country": "VA",
        "mode": "manual",
        "endpoint": "https://opac.vatlib.it/",
        "status": "manual_queue",
    },
    {
        "key": "vatican_archive",
        "name": "Archivio Apostolico Vaticano",
        "country": "VA",
        "mode": "manual",
        "endpoint": "https://www.archivioapostolicovaticano.va/",
        "status": "manual_queue",
    },
    {
        "key": "constantinople",
        "name": "Ecumenical Patriarchate of Constantinople",
        "country": "TR",
        "mode": "manual",
        "endpoint": "https://ec-patr.org/",
        "status": "manual_queue",
    },
    {
        "key": "alexandria_patriarchate",
        "name": "Greek Orthodox Patriarchate of Alexandria and All Africa",
        "country": "EG",
        "mode": "manual",
        "endpoint": "https://www.patriarchateofalexandria.com/",
        "status": "manual_queue",
    },
    {
        "key": "hmml",
        "name": "Hill Museum & Manuscript Library Reading Room",
        "country": "US/global",
        "mode": "manual",
        "endpoint": "https://www.vhmml.org/readingRoom/",
        "status": "manual_queue",
        "traditions": ["armenian", "coptic", "ethiopic", "syriac"],
        "note": "Eastern Christian manuscripts from partner repositories; API not confirmed in this pass.",
    },
    {
        "key": "betamasaheft",
        "name": "Beta masaheft: Manuscripts of Ethiopia and Eritrea",
        "country": "DE/ET/ER",
        "mode": "manual",
        "endpoint": "https://betamasaheft.eu/",
        "status": "manual_queue",
        "traditions": ["ethiopic", "geez", "ethiopian", "eritrean"],
    },
    {
        "key": "syriaca",
        "name": "Syriaca.org",
        "country": "US/global",
        "mode": "manual",
        "endpoint": "https://syriaca.org/",
        "status": "manual_queue",
        "traditions": ["syriac"],
        "note": "Use for authors, saints, BHSE, CBSS, and authority records; not a holding library.",
    },
    {
        "key": "matenadaran",
        "name": "Mesrop Mashtots Institute of Ancient Manuscripts (Matenadaran)",
        "country": "AM",
        "mode": "manual",
        "endpoint": "https://matenadaran.am/",
        "status": "manual_queue",
        "traditions": ["armenian"],
    },
    {
        "key": "georgian_manuscripts",
        "name": "Korneli Kekelidze Georgian National Centre of Manuscripts",
        "country": "GE",
        "mode": "manual",
        "endpoint": "https://manuscript.ge/",
        "status": "manual_queue",
        "traditions": ["georgian", "armenian", "greek", "oriental"],
    },
    {
        "key": "coptic_encyclopedia",
        "name": "Claremont Coptic Encyclopedia",
        "country": "US/EG",
        "mode": "manual",
        "endpoint": "https://ccdl.claremont.edu/digital/collection/cce",
        "status": "manual_queue",
        "traditions": ["coptic"],
        "note": "Reference layer for Coptic authors, works, and institutions; not a holding catalog.",
    },
    {
        "key": "bho",
        "name": "Bibliotheca Hagiographica Orientalis",
        "country": "BE/global",
        "mode": "manual",
        "endpoint": "http://syri.ac/bho",
        "status": "manual_queue",
        "traditions": ["arabic", "coptic", "syriac", "armenian", "ethiopic"],
        "note": "Hagiographic work authority list for Oriental Christian traditions.",
    },
    {
        "key": "ldab",
        "name": "Leuven Database of Ancient Books",
        "country": "BE/global",
        "mode": "manual",
        "endpoint": "https://www.trismegistos.org/ldab/",
        "status": "manual_queue",
        "traditions": ["coptic", "syriac", "greek", "latin"],
        "note": "Ancient literary manuscripts, especially useful for pre/ancient period witnesses.",
    },
]


USER_AGENT = "Mozilla/5.0 (know-graph-lab research; redpiigpig@gmail.com)"


def fetch_text(url: str, timeout: int = 30, retries: int = 3) -> str:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # transient TLS reset / timeout — back off and retry
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise last  # type: ignore[misc]


def text_or_none(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(text_or_none(v) for v in value if text_or_none(v))
    if isinstance(value, dict):
        return text_or_none(value.get("title") or value.get("name") or value.get("label"))
    return str(value)


def simplify_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def loc_records(repo: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"fo": "json", "c": str(limit), "q": query})
    url = f"{repo['endpoint']}?{params}"
    data = json.loads(fetch_text(url))
    out = []
    for item in data.get("results", [])[:limit]:
        out.append(
            {
                "source": repo["key"],
                "query": query,
                "title": simplify_space(text_or_none(item.get("title"))),
                "author": simplify_space(text_or_none(item.get("contributor") or item.get("creator"))),
                "date": simplify_space(text_or_none(item.get("date"))),
                "language": simplify_space(text_or_none(item.get("language"))),
                "subjects": item.get("subject", [])[:8] if isinstance(item.get("subject"), list) else [],
                "url": item.get("url") or item.get("id"),
                "raw_id": item.get("id"),
                "classification_status": "unclassified",
            }
        )
    return out


def openlibrary_records(repo: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "q": query, "limit": str(limit),
        "fields": "title,author_name,first_publish_year,language,key,edition_count",
    })
    url = f"{repo['endpoint']}?{params}"
    data = json.loads(fetch_text(url))
    out = []
    for item in data.get("docs", [])[:limit]:
        out.append({
            "source": repo["key"],
            "query": query,
            "title": simplify_space(text_or_none(item.get("title"))),
            "author": simplify_space("; ".join(item.get("author_name", [])[:3])),
            "date": simplify_space(text_or_none(item.get("first_publish_year"))),
            "language": simplify_space("; ".join(item.get("language", [])[:3])),
            "subjects": [],
            "url": f"https://openlibrary.org{item.get('key')}" if item.get("key") else repo["endpoint"],
            "raw_id": item.get("key", ""),
            "classification_status": "unclassified",
        })
    return out


def archive_records(repo: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    # Restrict to texts; exclude obvious non-book media.
    q = f"({query}) AND mediatype:texts"
    params = [("q", q), ("rows", str(limit)), ("output", "json")]
    for f in ("identifier", "title", "creator", "year", "language"):
        params.append(("fl[]", f))
    url = f"{repo['endpoint']}?{urllib.parse.urlencode(params)}"
    data = json.loads(fetch_text(url))
    out = []
    for item in data.get("response", {}).get("docs", [])[:limit]:
        ident = item.get("identifier", "")
        out.append({
            "source": repo["key"],
            "query": query,
            "title": simplify_space(text_or_none(item.get("title"))),
            "author": simplify_space(text_or_none(item.get("creator"))),
            "date": simplify_space(text_or_none(item.get("year"))),
            "language": simplify_space(text_or_none(item.get("language"))),
            "subjects": [],
            "url": f"https://archive.org/details/{ident}" if ident else repo["endpoint"],
            "raw_id": ident,
            "classification_status": "unclassified",
        })
    return out


def xml_texts(root: ET.Element, local_name: str) -> list[str]:
    values = []
    for el in root.iter():
        if el.tag.split("}")[-1] == local_name and el.text:
            values.append(simplify_space(el.text))
    return values


def marc_subfields(record: ET.Element, tag: str, codes: str) -> list[str]:
    """Collect subfield text from MARC datafields with the given tag/codes."""
    out: list[str] = []
    for df in record.iter():
        if df.tag.split("}")[-1] != "datafield" or df.attrib.get("tag") != tag:
            continue
        parts = [
            simplify_space(sf.text)
            for sf in df
            if sf.tag.split("}")[-1] == "subfield"
            and sf.attrib.get("code") in codes
            and sf.text
        ]
        if parts:
            out.append(" ".join(parts))
    return out


def marc_records(repo: dict[str, Any], query: str, limit: int, url: str, root: ET.Element) -> list[dict[str, Any]]:
    records = []
    for record in [e for e in root.iter() if e.tag.split("}")[-1] == "record"]:
        titles = marc_subfields(record, "245", "ab")  # title + remainder
        if not titles:
            continue
        authors = marc_subfields(record, "100", "a") + marc_subfields(record, "700", "a")
        dates = marc_subfields(record, "264", "c") + marc_subfields(record, "260", "c")
        languages = marc_subfields(record, "041", "a")
        ids = marc_subfields(record, "856", "u") + marc_subfields(record, "024", "a")
        records.append(
            {
                "source": repo["key"],
                "query": query,
                "title": titles[0],
                "author": "; ".join(authors[:3]),
                "date": "; ".join(dates[:3]),
                "language": "; ".join(languages[:3]),
                "subjects": (marc_subfields(record, "650", "a") + marc_subfields(record, "689", "a"))[:8],
                "url": next((x for x in ids if x.startswith("http")), url),
                "raw_id": "; ".join(ids[:3]),
                "classification_status": "unclassified",
            }
        )
    return records[:limit]


def sru_records(repo: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    if repo["key"] == "dnb":
        cql = f"WOE={query}"
        params = {
            "version": "1.1",
            "operation": "searchRetrieve",
            "query": cql,
            "recordSchema": "MARC21-xml",
            "maximumRecords": str(limit),
        }
        url = f"{repo['endpoint']}?{urllib.parse.urlencode(params)}"
        root = ET.fromstring(fetch_text(url))
        return marc_records(repo, query, limit, url, root)
    else:
        cql = f'bib.anywhere all "{query}"'
        params = {
            "version": "1.2",
            "operation": "searchRetrieve",
            "query": cql,
            "recordSchema": "dublincore",
            "maximumRecords": str(limit),
        }
    url = f"{repo['endpoint']}?{urllib.parse.urlencode(params)}"
    root = ET.fromstring(fetch_text(url))
    records = []
    for record in [e for e in root.iter() if e.tag.split("}")[-1] == "record"]:
        titles = xml_texts(record, "title")
        creators = xml_texts(record, "creator")
        dates = xml_texts(record, "date")
        languages = xml_texts(record, "language")
        identifiers = xml_texts(record, "identifier")
        if not titles:
            titles = xml_texts(record, "datafield")
        if not titles:
            continue
        records.append(
            {
                "source": repo["key"],
                "query": query,
                "title": titles[0],
                "author": "; ".join(creators[:3]),
                "date": "; ".join(dates[:3]),
                "language": "; ".join(languages[:3]),
                "subjects": xml_texts(record, "subject")[:8],
                "url": next((x for x in identifiers if x.startswith("http")), url),
                "raw_id": "; ".join(identifiers[:3]),
                "classification_status": "unclassified",
            }
        )
    return records[:limit]


MODE_DISPATCH = {
    "loc_json": loc_records,
    "dnb_sru": sru_records,
    "bnf_sru": sru_records,
    "openlibrary_json": openlibrary_records,
    "archive_json": archive_records,
}


def harvest(limit: int, sleep_seconds: float, queries: list[str]) -> dict[str, Any]:
    manifest = {
        "description": "First-pass source catalog for Christian Dazangjing. Candidate records need curation before insertion.",
        "repositories": REPOSITORIES,
        "queries": queries,
    }
    rows = []
    errors = []
    for repo in REPOSITORIES:
        fn = MODE_DISPATCH.get(repo["mode"])
        if fn is None:  # manual queue / no machine endpoint
            continue
        for query in queries:
            try:
                rows.extend(fn(repo, query, limit))
            except Exception as exc:
                errors.append({"source": repo["key"], "query": query, "error": str(exc)})
            time.sleep(sleep_seconds)
    return {"manifest": manifest, "records": rows, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--sleep", type=float, default=0.25)
    parser.add_argument("--queries", choices=["seed", "eastern", "all"], default="seed",
                        help="which query set to harvest (seed=Western patristic; eastern=diversity/Eastern; all=both)")
    parser.add_argument("--out", default=str(OUT_DIR / "seed-records.json"))
    args = parser.parse_args()

    queries = {"seed": SEED_QUERIES, "eastern": EASTERN_QUERIES, "all": SEED_QUERIES + EASTERN_QUERIES}[args.queries]
    data = harvest(args.limit, args.sleep, queries)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"records={len(data['records'])} errors={len(data['errors'])} -> {out}")


if __name__ == "__main__":
    main()
