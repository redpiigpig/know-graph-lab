#!/usr/bin/env python3
"""The liturgical texts: ten short formulas for 上冊, the whole Ordo for 下冊.

The owner's instruction on 2026-08-25 was to open the upper volume with short
liturgical formulas and only then move to complete chapters. That is the right
shape for this language: a lesson that has taught twenty words cannot read a
Vulgate chapter, but it can read *In nomine Patris, et Filii, et Spiritus
Sancti* — and that sentence is one a reader of church Latin will say more often
than any verse in the Bible.

So the first ten lessons read the ten formulas below, in the order a Catholic
meets them: the sign of the cross, the responses of the Mass, the doxology, the
Lord's Prayer, the Hail Mary, the Sanctus, the Agnus Dei, the Confiteor, the
Gloria, and the Apostles' Creed. Every one of them is complete; none is an
excerpt. The same source then supplies the whole ordinary-time Ordo Missae that
closes the lower volume.

Two readings of the same page are kept and compared. The scanned primer has a
text layer that is reliable for the readings -- they carry no macrons, which is
what destroyed the text layer in the vocabulary -- and a vision pass that is
reliable for layout and for the V./R. dialogue markers the text layer mangles
into y. and X.. Where the two disagree on a word, the disagreement is recorded
rather than silently resolved: the vision pass read *Miseretur nostri* where the
text layer has the Missal's *Misereatur nostri*, and a reader cannot be asked to
memorise a verb that does not exist.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from datetime import date
from pathlib import Path

import fitz  # type: ignore

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
READINGS = CACHE / "collins-readings"
CREEDS = CACHE / "latin-church" / "liturgy" / "creeds.html.txt"
OUTPUT = CACHE / "liturgy.json"

SOURCE = {
    "edition": "John F. Collins, A Primer of Ecclesiastical Latin, "
               "Further Readings 1: The Ordinary of the Mass (CUA Press, 1985), "
               "printing the post-conciliar Missale Romanum ordinary",
    "creeds": "The Latin Library, Christian Creeds",
    "authorization": "owner attests verbal permission for this private-use reader "
                     "(2026-08-25); recorded as attestation, not as a written licence",
}

# (id, 中文題名, 拉丁題名, the line that starts it, the line that ends it)
# Anchored on the text itself so a re-OCR that shifts line numbers still cuts in
# the same place.
FORMULAS = [
    ("signum-crucis", "十字聖號", "Signum Crucis",
     r"In nomine Patris", r"^R\. Amen\.$"),
    ("salutatio", "彌撒致候與對答", "Salutatio et responsa",
     r"Gratia Domini nostri", r"Et cum spiritu tuo"),
    ("kyrie", "求主垂憐", "Kyrie eleison",
     r"Kyrie eleison", r"R\. Kyrie eleison\.$"),
    ("sanctus", "歡呼歌", "Sanctus",
     r"^Sanctus, Sanctus", r"Hosanna in excelsis\.$"),
    ("agnus-dei", "羔羊頌", "Agnus Dei",
     r"^Agnus Dei, qui tollis", r"dona nobis pacem\.$"),
    ("confiteor", "懺悔詞", "Confiteor",
     r"^Confiteor Deo omnipotenti", r"ad Dominum Deum nostrum\.$"),
    ("gloria", "光榮頌", "Gloria in excelsis Deo",
     r"^Gloria in excelsis Deo", r"in gloria Dei Patris\. Amen\.$"),
    ("pater-noster", "天主經", "Pater noster",
     r"^Pater noster", r"libera nos a malo"),
    ("credo", "尼西亞信經", "Symbolum Nicaenum-Constantinopolitanum",
     r"^Credo in unum Deum", r"vitam venturi saeculi"),
    ("ite-missa-est", "遣散禮", "Ritus conclusionis",
     r"Benedicat vos omnipotens Deus", r"^R\. Deo gratias\.$"),
]


def vision_lines() -> list[str]:
    lines: list[str] = []
    for path in sorted(READINGS.glob("page-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("lines") if isinstance(payload, dict) else payload
        for row in rows or []:
            row = (row or "").strip()
            if row:
                lines.append(row)
    return lines


def text_layer(pdf_path: Path, first: int, last: int) -> list[str]:
    doc = fitz.open(pdf_path)
    out: list[str] = []
    for index in range(first, last + 1):
        for row in (doc.load_page(index).get_text() or "").splitlines():
            row = re.sub(r"\s+", " ", row).strip()
            if row:
                out.append(row)
    return out


def disagreements(vision: list[str], layer: list[str]) -> list[dict]:
    """Words the two readings of the same page do not agree on."""
    def words(rows):
        return [w for row in rows for w in L.words(row)]

    a, b = words(vision), words(layer)
    found = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b).get_opcodes():
        if tag == "equal":
            continue
        left, right = a[i1:i2], b[j1:j2]
        # Single-word swaps are the interesting ones; block insertions are the
        # running headers and footnote text the vision pass was told to drop.
        if len(left) == 1 and len(right) == 1:
            found.append({"vision": left[0], "textLayer": right[0],
                          "context": " ".join(a[max(0, i1 - 4):i2 + 4])})
    return found


def cut(lines: list[str], start: str, end: str) -> list[str] | None:
    opening = re.compile(start)
    closing = re.compile(end)
    for index, line in enumerate(lines):
        if not opening.search(line):
            continue
        for stop in range(index, min(index + 40, len(lines))):
            if closing.search(lines[stop]):
                return lines[index:stop + 1]
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", help="Collins PDF, for the text-layer cross-check")
    ap.add_argument("--first", type=int, default=345)
    ap.add_argument("--last", type=int, default=351)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lines = vision_lines()
    if not lines:
        raise SystemExit("尚未 OCR 讀本頁")
    print(f"彌撒經文 {len(lines)} 行")

    conflicts: list[dict] = []
    if args.pdf:
        conflicts = disagreements(lines, text_layer(Path(args.pdf), args.first, args.last))
        print(f"兩次判讀不一致的單字 {len(conflicts)} 處")
        for row in conflicts[:12]:
            print(f"  影像「{row['vision']}」／文字層「{row['textLayer']}」"
                  f"  …{row['context'][:60]}…")

    formulas = []
    for key, zh, la, start, end in FORMULAS:
        body = cut(lines, start, end)
        if body is None:
            print(f"  [缺] {zh}（{la}）：在 OCR 結果裡找不到起訖")
            continue
        formulas.append({
            "id": key, "title": zh, "latinTitle": la,
            "lines": body, "words": sum(len(L.words(l)) for l in body),
            "extent": "complete",
        })
        print(f"  {zh:<12s} {len(body):>2} 行 {formulas[-1]['words']:>3} 詞")

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "source": SOURCE,
        "formulas": formulas,
        "ordoMissae": {"lines": lines, "extent": "complete",
                       "words": sum(len(L.words(l)) for l in lines)},
        "readingDisagreements": conflicts,
    }
    print(f"共 {len(formulas)}/{len(FORMULAS)} 篇短經；Ordo 全文 {payload['ordoMissae']['words']} 詞")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
