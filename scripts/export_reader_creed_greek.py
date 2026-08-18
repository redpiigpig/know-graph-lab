#!/usr/bin/env python3
"""Export the conciliar Greek this repository was missing.

`data/creeds/**` already carries Greek for Nicaea 325 and for the canons of
several councils, but three texts the Greek reader needs were absent:

* the Niceno-Constantinopolitan Creed of 381 in its **conciliar plural** form
  (Πιστεύομεν …) -- the repository only had Chinese for this creed, and the
  Greek circulating online is almost always the liturgical singular (Πιστεύω …)
  used at the Divine Liturgy, which is a different text;
* the Chalcedonian *Definition of Faith* (451) -- the scraped council file holds
  the thirty **canons**, not the Ὅρος;
* the *Definition* of Constantinople III (681) against the Monothelites -- never
  scraped at all, and absent from Documenta Catholica Omnia.

All three come from Philip Schaff, *Creeds of Christendom*, vol. II (1877), on
CCEL, where the Greek is real text rather than page images and the edition is
long out of copyright.  CCEL serves the Greek decomposed, so each segment is
stored both raw and NFC-normalised; the reader displays NFC and keeps the raw
form as the immutable source layer.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "source-cache" / "original-readers" / "greek-full" / "creeds-greek.json"

EDITION = "Philip Schaff, Creeds of Christendom, vol. II: The Greek and Latin Creeds (New York, 1877)"
LICENSE_NOTE = "1877 年出版，已逾著作權期間；數位版由 CCEL 提供，正文為可選取文字而非掃描影像。"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
CELL_RE = re.compile(r"<td\b[^>]*>(?P<cell>.*?)</td>", re.S | re.I)

DOCUMENTS: list[dict] = [
    {
        "id": "creed-constantinople-381",
        "slug": "constantinople-381",
        "titleZh": "尼西亞—君士坦丁堡信經（381，大公會議原文）",
        "titleGrc": "Σύμβολον Νικαίας–Κωνσταντινουπόλεως",
        "year": 381,
        "completeness": "complete",
        "path": "creeds2.iv.i.ii.i.html",
        "note": (
            "大公會議原文用複數 Πιστεύομεν；拜占庭禮儀誦念的是單數 Πιστεύω 形，"
            "兩者是不同文本，本讀本兩形分開收，不混用。"
        ),
    },
    {
        "id": "creed-chalcedon-451",
        "slug": "chalcedon-451",
        "titleZh": "迦克墩信仰定義（451）",
        "titleGrc": "Ὅρος τῆς ἐν Χαλκηδόνι Δ´ Οἰκουμενικῆς Συνόδου",
        "year": 451,
        "completeness": "complete",
        "path": "creeds2.iv.i.iii.html",
        "note": "repo 既有的 early-04-greek.txt 是三十條教規，不是這份信仰定義。",
    },
    {
        "id": "creed-constantinople-681",
        "slug": "constantinople-681",
        "titleZh": "君士坦丁堡第三次大公會議信仰定義（681，駁一志論）",
        "titleGrc": "Ὅρος τῆς ΣΤ´ Οἰκουμενικῆς Συνόδου",
        "year": 681,
        "completeness": "complete",
        "path": "creeds2.iv.i.v.html",
        "note": (
            "第六次大公會議未頒教規，故 Documenta Catholica Omnia 沒有對應希臘文檔；"
            "本文接在迦克墩定義「παραδέδωκε σύμβολον」之後續讀。"
        ),
    },
]

BASE = "https://www.ccel.org/ccel/schaff/"


def fetch(path: str) -> str:
    request = urllib.request.Request(
        BASE + path, headers={"User-Agent": "private-authorized-original-reader/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


NOTE_RE = re.compile(
    r"<sup\b[^>]*class=\"Note\".*?</sup>|<span\b[^>]*class=\"mnote\".*?</span>",
    re.S | re.I,
)


def cell_text(cell: str) -> str:
    # Schaff's footnote markers and margin notes sit inside the Greek cell and
    # are English editorial apparatus.  Dropping them first keeps the creed text
    # clean and stops the Greek-ratio test from rejecting a heavily annotated
    # cell.
    text = re.sub(r"<[^>]+>", " ", NOTE_RE.sub(" ", cell))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


GREEK_SPAN_RE = re.compile(r"<span\b[^>]*class=\"Greek\"[^>]*>(?P<text>[^<]*)</span>", re.I)


def extract_greek(body: str) -> list[dict]:
    """Take the Greek column of Schaff's parallel Greek/English tables.

    Two filters do the work.  Restricting to ``<td>`` keeps out the English
    commentary that surrounds each creed and quotes single Greek words in the
    same span class.  Inside a cell, reading only the Greek spans keeps out
    Schaff's footnote markers and critical notes, which sit *between* the Greek
    spans and would otherwise leak English into the creed text.
    """
    segments = []
    for cell in CELL_RE.finditer(body):
        pieces = [
            html.unescape(match.group("text")).strip()
            for match in GREEK_SPAN_RE.finditer(NOTE_RE.sub(" ", cell.group("cell")))
        ]
        text = re.sub(r"\s+", " ", " ".join(piece for piece in pieces if piece)).strip()
        if len(text) < 40 or len(GREEK_RE.findall(text)) < len(text) * 0.5:
            continue
        segments.append(
            {
                "ordinal": len(segments) + 1,
                "sourceText": text,
                "displayText": unicodedata.normalize("NFC", text),
                "reviewStatus": review_status(text),
            }
        )
    if not segments:
        raise LookupError("這一頁沒有抓到希臘文欄位")
    return segments


# Schaff sets variant readings and a Greek term index in the same cells as the
# creed, so a segment is only auto-accepted when it reads as running text.
# An apparatus abbreviation is a short Greek token whose full stop is followed by
# a *lower-case* Greek word (κυρ. καὶ ζωοπ.); a genuine sentence end is followed
# by a capital or by nothing, so τέλος. and Ἀμὴν. must not trip this.
ABBREVIATION_RE = re.compile(
    r"(?<![Ͱ-Ͽἀ-῿])[Ͱ-Ͽἀ-῿]{2,5}\.\s+"
    r"[α-ωἀ-ἇὰ-ῄῐ-ῗῠ-ῧῲ-ῴ]"
)


def review_status(text: str) -> str:
    if ABBREVIATION_RE.search(text):
        return "needs_review_apparatus_abbreviations"
    if not text.rstrip().endswith((".", "·", ";")):
        return "needs_review_no_terminal_stop"
    return "auto_accepted"


def main() -> None:
    parser = argparse.ArgumentParser(description="補抓讀本缺少的大公會議希臘文")
    parser.add_argument("--write", action="store_true", help="寫出 creeds-greek.json")
    args = parser.parse_args()

    documents = []
    total = 0
    for spec in DOCUMENTS:
        segments = extract_greek(fetch(spec["path"]))
        words = sum(len(segment["displayText"].split()) for segment in segments)
        total += words
        documents.append(
            {
                **{key: value for key, value in spec.items() if key != "path"},
                "edition": EDITION,
                "sourceUrl": BASE + spec["path"],
                "licenseNote": LICENSE_NOTE,
                "segmentCount": len(segments),
                "wordCount": words,
                "segments": segments,
            }
        )
        flagged = [s for s in segments if s["reviewStatus"] != "auto_accepted"]
        print(f"  {spec['slug']:<22s} {len(segments):>2d} 段  {words:>4d} 詞  {spec['titleZh']}")
        for segment in flagged:
            print(f"      待複核 第 {segment['ordinal']} 段（{segment['reviewStatus']}）："
                  f"{segment['displayText'][:48]}…")
        time.sleep(1.0)

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "edition": EDITION,
        "licenseNote": LICENSE_NOTE,
        "textLayers": {
            "sourceText": "CCEL 原樣（希臘文為分解字元）",
            "displayText": "NFC 正規化後的顯示層",
        },
        "counts": {"documents": len(documents), "words": total},
        "documents": documents,
    }

    print(f"  合計 {len(documents)} 篇、{total} 詞")
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
