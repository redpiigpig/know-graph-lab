#!/usr/bin/env python3
"""Build the ordinary-time Divine Liturgy of St John Chrysostom appendix.

This is the Greek reader's counterpart to the Hebrew reader's fifteen-step
Haggadah: one complete rite, kept separate from the fifty lesson readings, read
straight through in the order it is actually celebrated.

The source page marks who speaks by typography rather than by labels — there is
no legend on it — so the role of each utterance is *inferred* and the evidence
that produced the inference is stored beside it:

* bold          -> the priest's exclamation said aloud (ἐκφώνησις)
* blue  #0000ff -> the deacon's litanies
* green #008000 -> the choir and people
* orange #ff6600-> the communion devotions
* red   #ff0000 -> the priest elsewhere, and inline rubrics such as "(3)"
* unmarked      -> the priest's prayers said quietly (εὐχὴ μυστικῶς)

Nothing here decides that a paragraph "is" a rubric because it looks short.  A
role is a reading of the page's typography, labelled as such, and a reviewer can
overturn any single one without re-deriving the whole file.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
SOURCE = CACHE / "sources" / "liturgy" / "goarch-sun-liturgy.html"
OUTPUT = CACHE / "liturgy-chrysostom.json"

EDITION = "Greek Liturgical Texts, ed. Seraphim Dedes（美洲希臘正教總教區）：主日事奉聖禮"
SOURCE_URL = "https://glt.goarch.org/texts/Oro/Sun_Liturgy.html"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")

PRIEST = "ἱερεύς"
DEACON = "διάκονος"
CHOIR = "χορὸς καὶ λαός"
COMMUNION = "κοινωνία（領聖體禱）"

ROLE_LABELS = {
    PRIEST: "司祭",
    DEACON: "執事",
    CHOIR: "詠經班與會眾",
    COMMUNION: "領聖體禱",
}

# The ordinary of the rite, in celebration order.  Each part is recognised by a
# phrase that opens it; a part with no match keeps the previous part, so a
# missing anchor never silently reorders the liturgy.
SECTIONS: list[tuple[str, str, str]] = [
    ("preparation", "司祭與執事的預備禱", r"^Βασιλεῦ Οὐράνιε"),
    ("kairos", "「時候到了」與祝福", r"^Καιρός τοῦ ποιῆσαι"),
    ("opening-blessing", "開端祝文：願天國受讚頌", r"Εὐλογημένη ἡ Βασιλεία"),
    ("great-litany", "大連禱（和平連禱）", r"^Ἐν εἰρήνῃ τοῦ Κυρίου δεηθῶμεν"),
    ("antiphon-1", "第一對經", r"^Κύριε ὁ Θεὸς ἡμῶν, οὗ τὸ κράτος"),
    ("antiphon-2", "第二對經與獨生子頌", r"^Κύριε, ὁ Θεὸς ἡμῶν, σῶσον τὸν λαόν σου"),
    ("antiphon-3", "第三對經", r"^Ὁ τὰς κοινὰς ταύτας"),
    ("little-entrance", "小進堂", r"Εὐλόγησον Δέσποτα, τὴν ἁγίαν εἴσοδον"),
    ("trisagion", "三聖頌", r"^Ὁ Θεὸς ὁ Ἅγιος, ὁ ἐν ἁγίοις ἀναπαυόμενος"),
    ("epistle", "使徒書信", r"^Προκείμενον τῆς ἡμέρας"),
    ("gospel", "福音", r"Εὐαγγελίου"),
    ("fervent-litany", "懇切連禱", r"^Εἴπωμεν πάντες"),
    ("catechumens", "為望教者的祈禱", r"κατηχούμεν"),
    ("cherubic-hymn", "革魯賓頌與大進堂", r"Οἱ τὰ Χερουβεὶμ"),
    ("litany-of-completion", "求全連禱與平安禮", r"^Πληρώσωμεν τὴν δέησιν"),
    ("creed", "信經", r"^Πιστεύω εἰς ἕνα Θεόν"),
    ("anaphora", "感恩經", r"Ἡ χάρις τοῦ Κυρίου ἡμῶν Ἰησοῦ Χριστοῦ καὶ ἡ ἀγάπη"),
    ("epiclesis", "呼求聖神", r"Κατάπεμψον τὸ Πνεῦμά σου τὸ Ἅγιον"),
    ("commemorations", "紀念諸聖與生者亡者", r"Ἐξαιρέτως τῆς Παναγίας"),
    ("lords-prayer", "主禱文", r"^Πάτερ ἡμῶν"),
    # The page prints these with its own capitalisation and punctuation
    # ("τα Ἅγια τοῖς Ἁγίοις.", "Ὀρθοί, μεταλαβόντες"), so the anchors match the
    # page rather than the textbook spelling.
    ("communion-elevation", "舉揚聖體：聖物給聖者", r"Ἅγια τοῖς Ἁγίοις"),
    ("communion-prayers", "領聖體前的預備禱", r"^Πιστεύω, Κύριε, καὶ ὁμολογῶ"),
    ("communion-distribution", "分送聖體聖血", r"^Μετὰ φόβου Θεοῦ"),
    ("thanksgiving", "領聖體後的謝恩", r"Ὀρθοί[,·]\s*μεταλαβόντες"),
    ("dismissal", "散堂", r"^Ἐν εἰρήνῃ προέλθωμεν"),
]


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", html.unescape(text)).strip())


def paragraphs(body: str) -> list[dict]:
    """Split the page into its paragraphs, keeping each one's typography.

    The page opens font runs across paragraph boundaries and wraps individual
    words in their own elements, so a paragraph is taken as "from one <p> up to
    the next", and the colours and bold runs inside it are collected as evidence
    rather than as structure.
    """
    body = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S | re.I)
    blocks = re.findall(r"<p\b[^>]*>(.*?)(?=<p\b|</body>)", body, re.S | re.I)
    rows = []
    for block in blocks:
        text = strip_tags(block)
        if not text or not GREEK_RE.search(text):
            continue
        colours = set(re.findall(r'color="?(#[0-9a-fA-F]{6})"?', block))
        bold = bool(re.search(r"<b\b", block, re.I))
        rows.append({"text": text, "colours": sorted(c.lower() for c in colours), "bold": bold})
    return rows


def infer_role(row: dict) -> tuple[str, str]:
    colours, bold = set(row["colours"]), row["bold"]
    if "#ff6600" in colours:
        return COMMUNION, "橘色：領聖體前後的個人禱文"
    if bold:
        return PRIEST, "粗體：司祭高聲頌（ἐκφώνησις）"
    if "#0000ff" in colours:
        return DEACON, "藍色：執事連禱"
    if "#008000" in colours:
        return CHOIR, "綠色：詠經班與會眾應答"
    if "#ff0000" in colours:
        return PRIEST, "紅色：司祭"
    return PRIEST, "無標色且非粗體：司祭默禱（εὐχὴ μυστικῶς）"


RUBRIC_ONLY = re.compile(r"^[+()\d\s.·]*$")
REPEAT_RE = re.compile(r"\((\d)\)\s*$")


def classify(text: str) -> str:
    if RUBRIC_ONLY.match(text):
        return "rubric"
    if text.endswith(("δεηθῶμεν.", "δεηθῶμεν")):
        return "litany-petition"
    if REPEAT_RE.search(text):
        return "repeated-response"
    return "text"


def assign_sections(rows: list[dict]) -> list[dict]:
    current = ("prelude", "起始")
    matchers = [(key, label, re.compile(pattern)) for key, label, pattern in SECTIONS]
    for row in rows:
        for key, label, pattern in matchers:
            if pattern.search(row["text"]):
                current = (key, label)
                break
        row["section"], row["sectionLabel"] = current
    return rows


def build() -> dict:
    if not SOURCE.exists():
        raise FileNotFoundError(f"missing frozen liturgy source: {SOURCE}")
    rows = assign_sections(paragraphs(SOURCE.read_text(encoding="utf-8")))

    steps = []
    for index, row in enumerate(rows, start=1):
        role, evidence = infer_role(row)
        repeat = REPEAT_RE.search(row["text"])
        step = {
            "ordinal": index,
            "section": row["section"],
            "sectionLabel": row["sectionLabel"],
            "role": role,
            "roleLabel": ROLE_LABELS[role],
            "roleEvidence": evidence,
            "roleDerivation": "inferred_from_typography",
            "kind": classify(row["text"]),
            "wordCount": len(row["text"].split()),
            "sourceText": row["text"],
            "displayText": row["text"],
        }
        if repeat:
            step["repeatCount"] = int(repeat.group(1))
        steps.append(step)

    sections: list[dict] = []
    for step in steps:
        if not sections or sections[-1]["key"] != step["section"]:
            sections.append(
                {
                    "key": step["section"],
                    "label": step["sectionLabel"],
                    "firstStep": step["ordinal"],
                    "lastStep": step["ordinal"],
                    "stepCount": 0,
                    "wordCount": 0,
                }
            )
        sections[-1]["lastStep"] = step["ordinal"]
        sections[-1]["stepCount"] += 1
        sections[-1]["wordCount"] += step["wordCount"]

    role_counts: dict[str, int] = {}
    for step in steps:
        role_counts[step["roleLabel"]] = role_counts.get(step["roleLabel"], 0) + 1

    missing = [key for key, _, _ in SECTIONS if not any(s["key"] == key for s in sections)]

    return {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "status": "flow-parsed-translation-pending",
        "title": "金口聖若望事奉聖禮（常年期主日全文流程）",
        "titleGrc": "Ἡ Θεία Λειτουργία τοῦ ἐν Ἁγίοις Πατρὸς ἡμῶν Ἰωάννου τοῦ Χρυσοστόμου",
        "language": "New Testament Greek",
        "languageCode": "grc",
        "placement": (
            "獨立附錄，與 50 課的讀文分開；體例對應希伯來文讀本的十五段逾越節儀典。"
        ),
        "edition": EDITION,
        "sourceUrl": SOURCE_URL,
        "roleDerivationNote": (
            "來源頁面沒有角色凡例，角色由排版推定：粗體＝司祭高聲頌、藍＝執事、"
            "綠＝詠經班與會眾、橘＝領聖體禱、無標色＝司祭默禱。每一步都存下推定依據，"
            "可逐條覆核推翻，不需重跑整份。"
        ),
        "printedTextNote": (
            "來源頁面不逐條印出會眾對每一句連禱的應答（Κύριε, ἐλέησον／Παράσχου, Κύριε），"
            "所以「詠經班與會眾」的段數看起來偏少；那是版面慣例，不是禮儀缺漏。"
            "排版時應依連禱句數補上應答，並標明為編者所加。"
        ),
        "crossCheckNote": (
            "同一站的復活節講道有重出衍文，因此本份禮儀正文尚未經第二來源對校；"
            "排版前應逐段與另一版本比對。"
        ),
        "summary": {
            "stepCount": len(steps),
            "wordCount": sum(step["wordCount"] for step in steps),
            "sectionCount": len(sections),
            "roleCounts": role_counts,
            "sectionsNotFound": missing,
        },
        "sections": sections,
        "steps": steps,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="建立金口若望事奉聖禮全文流程")
    parser.add_argument("--write", action="store_true", help="寫出 liturgy-chrysostom.json")
    args = parser.parse_args()

    plan = build()
    for section in plan["sections"]:
        print(
            f"  {section['key']:<22s} {section['label']:<18s}"
            f" 第 {section['firstStep']:>3d}–{section['lastStep']:>3d} 步"
            f"  {section['stepCount']:>3d} 段 {section['wordCount']:>5d} 詞"
        )
    summary = plan["summary"]
    print(
        f"  合計 {summary['stepCount']} 段、{summary['wordCount']} 詞、"
        f"{summary['sectionCount']} 個段落；角色分佈 {summary['roleCounts']}"
    )
    if summary["sectionsNotFound"]:
        print(f"  ⚠ 找不到起點的段落：{summary['sectionsNotFound']}")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
