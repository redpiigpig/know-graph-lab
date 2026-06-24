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


def fetch_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "know-graph-lab catalog harvester"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


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


def harvest(limit: int, sleep_seconds: float) -> dict[str, Any]:
    manifest = {
        "description": "First-pass source catalog for Christian Dazangjing. Candidate records need curation before insertion.",
        "repositories": REPOSITORIES,
        "queries": SEED_QUERIES,
    }
    rows = []
    errors = []
    for repo in REPOSITORIES:
        if repo["mode"] == "manual":
            continue
        for query in SEED_QUERIES:
            try:
                if repo["mode"] == "loc_json":
                    rows.extend(loc_records(repo, query, limit))
                else:
                    rows.extend(sru_records(repo, query, limit))
            except Exception as exc:
                errors.append({"source": repo["key"], "query": query, "error": str(exc)})
            time.sleep(sleep_seconds)
    return {"manifest": manifest, "records": rows, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--sleep", type=float, default=0.25)
    parser.add_argument("--out", default=str(OUT_DIR / "seed-records.json"))
    args = parser.parse_args()

    data = harvest(args.limit, args.sleep)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"records={len(data['records'])} errors={len(data['errors'])} -> {out}")


if __name__ == "__main__":
    main()
