#!/usr/bin/env python3
"""凍結下冊所需的希臘教會文獻來源。

下冊第 26–50 課讀的是「希臘教會文獻與禮儀文本」。定義類的信經與教令倉庫裡已有
（``data/creeds/**`` 與 ``creeds-greek.json``），缺的是**教規彙編**與**禮儀文本**
兩批：前者取自希臘文維基文庫的《神聖教規》系列，後者取自 glt.goarch.org。

每一份都連同修訂版本號、時間戳與 sha256 一起存下來，之後的建置一律讀本地凍結
檔，不再上網；來源換了、字改了，雜湊就對不上，而不是悄悄換一份文本。

維基文庫的條文本身是古代教會文獻（早已逾著作權期間），錄入與編排採 CC BY-SA 4.0，
與本讀本已用的 First1KGreek 同一授權型態，僅供私人授權使用。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
CHURCH_DIR = CACHE / "sources" / "church-documents"
LITURGY_DIR = CACHE / "sources" / "liturgy"
MANIFEST = CHURCH_DIR / "manifest.json"

# Wikimedia throttles requests whose agent string says nothing about who is
# asking, and a burst of fourteen anonymous ones is refused outright.
USER_AGENT = "know-graph-lab-original-reader/1.0 (private-use Koine Greek reader; non-commercial)"
WIKISOURCE_API = "https://el.wikisource.org/w/api.php"
WIKISOURCE_LICENSE = (
    "條文為古代教會文獻，已逾著作權期間；希臘文維基文庫的錄入與編排採 CC BY-SA 4.0，"
    "本讀本私人授權使用並標明出處。"
)
GOARCH_LICENSE = (
    "Greek Liturgical Texts, ed. Seraphim Dedes（美國希臘正教總主教區）；"
    "禮儀文本本身為教會公用文本，本讀本私人授權使用並標明出處。"
)

# stem -> 維基文庫條目名。教規彙編按傳統次序：使徒教規、大公會議教規、地方會議教規。
WIKISOURCE_PAGES: dict[str, str] = {
    "canons-apostolic": "Αποστολικοί Κανόνες",
    "canons-nicaea-i": "Κανόνες Α΄ Οικουμενικής Συνόδου",
    "canons-constantinople-i": "Κανόνες Β΄ Οικουμενικής Συνόδου",
    "canons-chalcedon": "Κανόνες Δ΄ Οικουμενικής Συνόδου",
    "canons-trullo": "Κανόνες Πενθέκτης Οικουμενικής Συνόδου",
    "canons-ancyra": "Κανόνες της εν Αγκύρα Συνόδου",
    "canons-neocaesarea": "Κανόνες της εν Νεοκαισαρεία Συνόδου",
    "canons-gangra": "Κανόνες της εν Γάγγρα Συνόδου",
    "canons-antioch": "Κανόνες της εν Αντιοχεία Συνόδου",
    "canons-laodicea": "Κανόνες της εν Λαοδικεία Συνόδου",
    "canons-sardica": "Κανόνες της εν Σαρδική Συνόδου",
    "canons-carthage": "Κανόνες της εν Καρθαγένη Συνόδου",
    "hymn-akathistos": "Ακάθιστος ύμνος",
    "hymn-great-doxology": "Η Μεγάλη Δοξολογία",
    "hymn-kassiani": "Τροπάριο της Κασσιανής",
    "orthros-christmas": "Όρθρος των Χριστουγέννων",
}

# stem -> glt.goarch.org 的頁面。Sun_Liturgy 已由禮儀附錄凍結，不重複下載。
GOARCH_PAGES: dict[str, str] = {
    "goarch-orthros.html": "https://glt.goarch.org/texts/Oro/Orthros.html",
    "goarch-paraklesis.html": "https://glt.goarch.org/texts/Oro/Paraklesis.html",
}


def _context() -> ssl.SSLContext:
    return ssl.create_default_context()


def fetch(url: str, attempts: int = 5) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=60, context=_context()) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503) or attempt == attempts:
                raise
            wait = 5 * attempt
            print(f"    {error.code}，等 {wait} 秒再試（第 {attempt} 次）", flush=True)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def fetch_wikisource(title: str) -> dict:
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content|ids|timestamp",
            "rvslots": "main",
            "titles": title,
            "format": "json",
            "formatversion": "2",
        }
    )
    payload = json.loads(fetch(f"{WIKISOURCE_API}?{query}").decode("utf-8"))
    pages = payload["query"]["pages"]
    if not pages or pages[0].get("missing"):
        raise LookupError(f"維基文庫查無此條目：{title}")
    revision = pages[0]["revisions"][0]
    return {
        "title": pages[0]["title"],
        "revisionId": revision["revid"],
        "timestamp": revision["timestamp"],
        "content": revision["slots"]["main"]["content"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="凍結希臘教會文獻來源")
    parser.add_argument("--write", action="store_true", help="寫出凍結檔與 manifest")
    parser.add_argument("--refresh", action="store_true", help="已存在也重新下載")
    args = parser.parse_args()

    CHURCH_DIR.mkdir(parents=True, exist_ok=True)
    LITURGY_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    for stem, title in WIKISOURCE_PAGES.items():
        path = CHURCH_DIR / f"{stem}.wiki"
        if path.exists() and not args.refresh:
            body = path.read_text(encoding="utf-8")
            record = {"stem": stem, "state": "cached"}
        else:
            page = fetch_wikisource(title)
            body = page["content"]
            record = {
                "stem": stem,
                "state": "fetched",
                "revisionId": page["revisionId"],
                "timestamp": page["timestamp"],
            }
            if args.write:
                path.write_text(body, encoding="utf-8")
            time.sleep(1.5)
        record.update(
            {
                "title": title,
                "sourceUrl": "https://el.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": len(body.encode("utf-8")),
                "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "license": WIKISOURCE_LICENSE,
            }
        )
        records.append(record)
        print(f"  {stem}: {record['state']}, {record['bytes']} bytes")

    for stem, url in GOARCH_PAGES.items():
        path = LITURGY_DIR / stem
        if path.exists() and not args.refresh:
            body = path.read_bytes()
            state = "cached"
        else:
            body = fetch(url)
            state = "fetched"
            if args.write:
                path.write_bytes(body)
            time.sleep(1.5)
        records.append(
            {
                "stem": stem,
                "state": state,
                "title": stem,
                "sourceUrl": url,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "license": GOARCH_LICENSE,
            }
        )
        print(f"  {stem}: {state}, {len(body)} bytes")

    manifest = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "note": "下冊第 26–50 課所需的教規彙編與禮儀文本凍結來源。",
        "count": len(records),
        "sources": records,
    }
    if args.write:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {MANIFEST}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
