#!/usr/bin/env python3
"""Build a form-to-lemma index for the corpora that ship without morphology.

Only the New Testament source carries lemmas: MorphGNT gives one for every
token.  Swete's Septuagint, the Apostolic Fathers, First1KGreek and the
liturgical texts are plain text, so counting "how often does λόγος occur" in
them is impossible without first deciding that λόγου and λόγῳ are the same word.

Morpheus, the morphological analyser behind Perseus, publishes exactly that
mapping: every attested Ancient Greek form with its lemma, part of speech and a
short English sense.  This script streams that 220 MB dump once and writes a
compact index keyed the way the rest of this reader keys Greek — accents,
breathings and iota subscripts folded away — so a form found in any corpus can
be resolved to a headword.

A folded form often has more than one analysis.  All of them are kept, ordered
so the caller can see the ambiguity rather than be handed a silent guess, and
the frequency builder resolves it by preferring a lemma the New Testament also
uses before falling back to the first analysis.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
MORPHEUS_ZIP = CACHE / "sources" / "morpheus" / "MorpheusUnicode.xml.zip"
MORPHEUS_URL = (
    "https://raw.githubusercontent.com/gcelano/LemmatizedAncientGreekXML/"
    "master/Morpheus/MorpheusUnicode.xml.zip"
)
OUTPUT = CACHE / "lemma-index.json"

# The compact <t> record, which repeats the verbose <token> block above it.
RECORD_RE = re.compile(
    r"<t>\s*<i>.*?</i>\s*<f>(?P<form>[^<]*)</f>\s*<b>[^<]*</b>\s*"
    r"<l>(?P<lemma>[^<]*)</l>\s*<e>[^<]*</e>\s*<p>(?P<pos>[^<]*)</p>",
    re.S,
)


def stream_records(chunk_size: int = 1 << 22):
    """Yield (form, lemma, pos) without holding the whole dump in memory."""
    if not MORPHEUS_ZIP.exists():
        raise FileNotFoundError(
            f"缺少 Morpheus 檔：{MORPHEUS_ZIP}\n下載自 {MORPHEUS_URL}"
        )
    with zipfile.ZipFile(MORPHEUS_ZIP) as archive:
        name = archive.namelist()[0]
        with archive.open(name) as handle:
            tail = ""
            while True:
                block = handle.read(chunk_size)
                if not block:
                    break
                text = tail + block.decode("utf-8", "replace")
                last = 0
                for match in RECORD_RE.finditer(text):
                    last = match.end()
                    yield match.group("form"), match.group("lemma"), match.group("pos")
                # Keep the unconsumed tail so a record split across two reads is
                # not lost; it is short, so the overlap costs nothing.
                tail = text[last:] if last else text[-4096:]


def build() -> dict:
    index: dict[str, list[str]] = {}
    lemma_pos: dict[str, str] = {}
    seen = 0
    for form, lemma, pos in stream_records():
        seen += 1
        lemma = unicodedata.normalize("NFC", lemma).strip()
        if not lemma:
            continue
        key = fold(form)
        if not key:
            continue
        bucket = index.setdefault(key, [])
        if lemma not in bucket:
            bucket.append(lemma)
        lemma_pos.setdefault(lemma, (pos or "")[:1])
    return {
        "schemaVersion": "1.0.0",
        "source": "Morpheus (Perseus) via gcelano/LemmatizedAncientGreekXML",
        "sourceUrl": MORPHEUS_URL,
        "note": (
            "鍵是去重音、去氣號、去下標 iota 的字形，與讀本其他比對一致；"
            "一個字形可能對到多個詞位，全部保留，讓歧義看得見。"
        ),
        "recordsRead": seen,
        "formCount": len(index),
        "lemmaCount": len(lemma_pos),
        "forms": index,
        "lemmaPos": lemma_pos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="建立希臘文字形→詞位對照表")
    parser.add_argument("--write", action="store_true", help="寫出 lemma-index.json")
    args = parser.parse_args()

    payload = build()
    print(
        f"  讀入 {payload['recordsRead']} 筆分析；"
        f"字形 {payload['formCount']}、詞位 {payload['lemmaCount']}"
    )
    ambiguous = sum(1 for values in payload["forms"].values() if len(values) > 1)
    print(f"  一形多位者 {ambiguous}（{ambiguous * 100 // max(payload['formCount'], 1)}%）")

    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print(f"已寫出 {OUTPUT}（{OUTPUT.stat().st_size / 1_048_576:.1f} MB）")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
