#!/usr/bin/env python3
"""Fetch the patristic and liturgical half of the reader's Latin corpus.

The repository already holds fifteen centuries of papal and conciliar Latin --
seven hundred and fifty-five documents, nearly all of them with a Chinese
counterpart -- but that corpus is entirely documentary.  It contains no hymn, no
rule, no confession, no pilgrim's diary; and the lower volume's first half is
supposed to be exactly those.  So the literary side is fetched separately from
The Latin Library, whose texts are public-domain works in freely offered
transcriptions.

Author index pages and text pages look alike, so each fetched page is judged by
what it actually contains: a page whose Latin word count is small but whose
links into its own directory are many is an index, and its children are queued.
That avoids maintaining a hand-written list of every chapter file, which for
Augustine alone would be thirteen.

Every page records its URL and a checksum, because a reader that cannot say
which transcription it printed cannot be audited against it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "source-cache" / "original-readers" / "latin-full" / "latin-church"
BASE = "https://www.thelatinlibrary.com/"

# Grouped the way the volume is taught, not the way the site is arranged.
TARGETS = {
    "liturgy": ["hymni.html", "creeds.html", "diesirae.html", "professio.html"],
    "fathers": [
        "tertullian.html", "novatian.html", "lactantius.html", "arnobius.html",
        "ambrose.html", "jerome.html", "august.html", "leothegreat.html",
        "vicentius.html", "prosperus.html", "sulpiciusseverus.html",
        "perp.html", "egeria.html", "commodianus.html", "prud.html",
        "sedulius.html", "paulinus.poemata.html", "eucherius.html",
    ],
    "medieval": [
        "benedict.html", "greg.html", "isidore.html", "bede.html", "alcuin.html",
        "anselm.html", "abelard.html", "bernardclairvaux.shtml", "bernardcluny.html",
        "hugo.html", "aquinas.html", "bonaventura.itinerarium.html", "kempis.html",
        "vorag.html", "cassiodorus.html", "liberpontificalis.html",
    ],
    "documents": ["papal.html", "decretum.html", "innocent.html", "gregory7.html", "gregory.html"],
}

STRIP = re.compile(r"<(script|style|head)[^>]*>.*?</\1>", re.S | re.I)
TAGS = re.compile(r"<[^>]+>")
NAV = re.compile(r"^(The Latin Library|The Classics Page|The Christian Latin|Christian Latin)", re.I)

INDEX_MIN_LINKS = 5
INDEX_MAX_WORDS = 250


def clean(html: str) -> str:
    text = STRIP.sub(" ", html)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = TAGS.sub(" ", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&aelig;", "æ").replace("&oelig;", "œ")
                .replace("&eacute;", "é").replace("&egrave;", "è")
                .replace("&quot;", '"').replace("&#39;", "'"))
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln and not NAV.match(ln))


def children(html: str, url: str) -> list[str]:
    here = urllib.parse.urlparse(url)
    folder = here.path.rsplit("/", 1)[0]
    # Most authors keep their works in a folder of their own, but the folder is
    # not reliably named after the index page: august.html lists its
    # Confessions under augustine/, not august/.  So any relative link one
    # level down counts as a child, whatever that level is called.
    depth = here.path.count("/")
    out = []
    for href in re.findall(r'href="([^"]+)"', html, flags=re.I):
        if href.startswith(("http", "mailto:", "#", "/")):
            continue
        target = urllib.parse.urljoin(url, href)
        path = urllib.parse.urlparse(target).path
        if not path.endswith((".html", ".shtml")):
            continue
        parent = path.rsplit("/", 1)[0]
        if parent != folder and path.count("/") != depth + 1:
            continue
        if path == here.path:
            continue
        out.append(target)
    return sorted(dict.fromkeys(out))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pace", type=float, default=0.8)
    ap.add_argument("--max-pages", type=int, default=1200)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    session = requests.Session()
    session.headers["User-Agent"] = "know-graph-lab reader corpus builder"

    queue = [(group, BASE + page, 0) for group, pages in TARGETS.items() for page in pages]
    seen: set[str] = set()
    fetched = 0

    while queue and fetched < args.max_pages:
        group, url, depth = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        key = urllib.parse.urlparse(url).path.lstrip("/").replace("/", "__")
        if key in manifest:
            continue
        try:
            resp = session.get(url, timeout=60)
            resp.encoding = resp.apparent_encoding or "latin-1"
            if resp.status_code != 200:
                print(f"skip {url} → {resp.status_code}", flush=True)
                continue
        except Exception as exc:  # noqa: BLE001
            print(f"fail {url}: {exc}", flush=True)
            continue
        fetched += 1
        time.sleep(args.pace)

        text = clean(resp.text)
        count = len(L.words(text))
        kids = children(resp.text, url)
        if depth == 0 and count < INDEX_MAX_WORDS and len(kids) >= INDEX_MIN_LINKS:
            queue.extend((group, kid, 1) for kid in kids)
            print(f"index {url} → {len(kids)} 子頁", flush=True)
            continue
        if count < 30:
            continue
        path = OUT / group / f"{key}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        manifest[key] = {
            "group": group,
            "url": url,
            "words": count,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        }
        print(f"{group}/{key}: {count:,} 詞", flush=True)

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(m["words"] for m in manifest.values())
    print(f"完成：{len(manifest)} 篇，{total:,} 詞")


if __name__ == "__main__":
    main()
