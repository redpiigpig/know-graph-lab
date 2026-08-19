#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Curation aid for the Dazangjing source catalog.

Reads the classifier ledger (classified-records.jsonl), keeps the latest row per
record, and for every keep_primary_work candidate:
  - normalizes title_orig + title_zh,
  - flags candidates that already exist in the Dazangjing corpus (data/dazangjing/*.ts),
  - groups intra-candidate duplicates (same work, many editions/translations).

This NEVER inserts anything. It produces a human worklist so the curator can
decide what to add. Dedup is intentionally fuzzy and over-reports matches; the
human confirms.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dazangjing"
LEDGER = DATA / "source-catalog" / "classified-records.jsonl"
TS_FILES = [DATA / "index.ts", DATA / "ancient.ts", DATA / "medieval.ts",
            DATA / "early-modern.ts", DATA / "modern.ts"]

# TS string fields may contain escaped quotes (l\'Église); match them safely.
ZH_RE = re.compile(r"title_zh:\s*'((?:[^'\\]|\\.)*)'")
ORIG_RE = re.compile(r"title_orig:\s*'((?:[^'\\]|\\.)*)'")

# Edition/translation/series noise stripped before comparing original titles.
NOISE = re.compile(
    r"\b(translated|translation|edited|edition|introduction|introd|notes?|"
    r"vol|volume|tome|band|books?|liber|libri|with|together|essays?|select|"
    r"works|opera|opere|fragments?|critical|study|english|latin|greek|syriac|"
    r"version|texte|text|par|by|and|the|de|la|le|du|des|von|une?)\b",
    re.I,
)

# Cross-language / collected-edition records that cannot be matched reliably by
# title normalization alone. Each value names the existing corpus work.
KNOWN_CORPUS_EQUIVALENTS = {
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb34812913t|contra gentes ; de incarnatione / athanasius ; ed. and transl. by robert w. thomson,...|athanase (0295?-0373 ; saint). auteur du texte; athanase (0295?-0373 ; saint). auteur du texte|1971":
        "Against the Heathen (Contra Gentes) / De Incarnatione",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb30649716q|the homilies of s. john chrysostom,... on the statues or to the people of antioch / s. john chrysostom ; translated with notes... [by e. budge.]|jean chrysostome (0347?-0407 ; saint). auteur du texte|1842":
        "Homilies on the Statues (to the People of Antioch)",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb41411477f|johannis chrysostomi de davide et saule homiliae tres / quas edidit francesca prometea barone|jean chrysostome (0347?-0407 ; saint). auteur du texte|2008":
        "De Davide et Saule homiliae tres",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb306495839|the homilies of s. john chrysostom,... on the gospel of st. matthew / s. john chrysostom ; translated with notes... [by sir g. prevost]|jean chrysostome (0347?-0407 ; saint). auteur du texte|1843-1851":
        "Homilies on the Gospel of Matthew",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb33031558b|homélies, xxxviii-xxxix, xl, i, xlv, xli. textes introduits par dom thomas becquet, o.s.b., choisis, présentés et traduits par edmond devolver / grégoire de nazianze|grégoire de nazianze (0330?-0390? ; saint). auteur du texte|1962":
        "Select Orations (Gregory of Nazianzus)",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb32914665m|homélies sur l'hexaéméron...[ @ ] introduction et traduction de stanislas giet,... 2e édition revue et augmentée / basile de césarée|basile de césarée (0329?-0379 ; saint). auteur du texte|1968":
        "The Hexaemeron (Basil of Caesarea)",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb30001151s|gregorii barhebraei chronicon ecclesiasticum, quod... ediderunt, latinitate donarunt... joannes baptista abbeloos,... et thomas josephus lamy|barhebraeus, gregorius abū al-faraǧ (1226-1286). auteur du texte|1872-1877":
        "Chronicon Ecclesiasticum (Bar Hebraeus)",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb453860223|the hymns on faith / st. ephrem the syrian ; translated by jeffrey t. wickes,...|éphrem (0306?-0373 ; saint). auteur du texte|2015":
        "Madrāšê de Fide (Ephrem)",
    "bnf|http://catalogue.bnf.fr/ark:/12148/cb472462865|hymns on paradise / st. ephrem ; introduction and translation by sebastian brock|éphrem (0306?-0373 ; saint). auteur du texte; éphrem (0306?-0373 ; saint). auteur du texte|1990":
        "Hymni de Paradiso (Ephrem)",
}

# Stable work-level matches across translated titles, modern editions, and
# transliteration systems. These patterns are deliberately work-specific.
KNOWN_CORPUS_PATTERNS = [
    (re.compile(r"aphrahat.{0,30}demonstr|demonstrations? (?:i|ii)?\b.*aphra", re.I),
     "Demonstrations of Aphrahat"),
    (re.compile(r"(?:isaac|依撒格|以撒).{0,35}(?:nineveh|尼尼微|ascetic|苦修|苦行|mystic|神秘|homil)", re.I),
     "Ascetical Homilies of Isaac of Nineveh"),
    (re.compile(r"babai.{0,25}(?:book|liber).{0,12}(?:union|unione)|大巴貝.{0,20}(?:聯合|合一)", re.I),
     "Liber de Unione (Babai the Great)"),
    (re.compile(r"(?:coptic|ethiopian).{0,30}synaxarium|book of the saints of the ethiopian|科普特.{0,15}(?:聖人曆|殉道曆)|衣索匹亞.{0,15}(?:聖人曆|聖品歷|聖徒之書)", re.I),
     "Coptic / Ethiopian Synaxarium"),
    (re.compile(r"history of the patriarchs of the egyptian church|埃及教會宗主教史", re.I),
     "History of the Patriarchs of Alexandria"),
    (re.compile(r"\begeria\b|\bethérie\b|itinerarium egeriae|埃格麗雅|埃蓋莉婭", re.I),
     "Itinerarium Egeriae"),
    (re.compile(r"(?:book|version).{0,15}enoch|以諾書", re.I),
     "1 Enoch"),
    (re.compile(r"eutychii.{0,25}annal|厄提基烏斯年史", re.I),
     "Naẓm al-Jawhar (Annals of Eutychius)"),
    (re.compile(r"\beznik\b|ełc ałandoc|aġandoc|wider die sekten|駁異端（亞美尼亞|論天主（駁異端", re.I),
     "Ełc Ałandocʻ (Against the Sects)"),
    (re.compile(r"feth.?a nagast|費塔.{0,6}納加斯特", re.I),
     "Fetḥa Nagaśt"),
    (re.compile(r"(?:life|ḥayāt).{0,30}(?:shenoute|shinūdah)|聖安巴謝努達傳", re.I),
     "Life of Shenoute"),
    (re.compile(r"history of the councils|histoire des conciles|大公會議史", re.I),
     "Tārīkh al-Majāmiʿ"),
    (re.compile(r"(?:life|histoire|vita).{0,25}macrina|瑪克蓮娜傳", re.I),
     "Life of Macrina"),
    (re.compile(r"jacob of serugh.{0,35}(?:thomas|hexaemeron)|賽魯吉的雅各.{0,20}(?:多馬|六日創世)", re.I),
     "Homilies of Jacob of Serugh"),
    (re.compile(r"(?:lamp of the intellect|kitab misbah al-aql|理性之燈)", re.I),
     "Kitāb Miṣbāḥ al-ʿAql"),
    (re.compile(r"life of (?:saint )?mary of egypt|埃及聖瑪利亞傳", re.I),
     "Life of Mary of Egypt"),
    (re.compile(r"(?:ethiopian|éthiopien).{0,25}miracles? of mary|衣索匹亞聖母瑪利亞奇蹟", re.I),
     "Täʾammǝra Maryam"),
    (re.compile(r"(?:perpetua|perpetuae|百圖亞|佩爾培圖)", re.I),
     "Passion of Perpetua and Felicity"),
    (re.compile(r"matean oghbergut|哀嘆之書", re.I),
     "Book of Lamentations (Gregory of Narek)"),
    (re.compile(r"\bnarsai\b.{0,40}(?:homil|carmina)|納爾賽.{0,20}(?:講道|詩歌)|那西講道", re.I),
     "Mēmrē of Narsai"),
    (re.compile(r"(?:movses|moses).{0,25}(?:khoren|xoren).{0,25}(?:history|patmut)|patm(?:ut|ow)t.{0,12}hayoc|亞美尼亞人的歷史", re.I),
     "Patmutʻiwn Hayotsʻ"),
    (re.compile(r"(?:pachom|paḫōm).{0,30}(?:rule|kanōn|規章)", re.I),
     "Rule of Pachomius"),
    (re.compile(r"(?:life|vita).{0,25}melania|聖梅拉尼亞", re.I),
     "Life of Melania the Younger"),
    (re.compile(r"persian martyr acts|波斯殉道錄", re.I),
     "Acts of the Persian Martyrs"),
    (re.compile(r"(?:general epistle|tught.? e.?ndhanrakan).{0,30}(?:nerses|nersesi)|納爾謝斯.{0,12}牧函", re.I),
     "Tʻughtʻ Endhanrakan"),
    (re.compile(r"(?:preces.{0,20}ners|bank. cap.aw|havatov khostovanim|雅魚禱文)", re.I),
     "Hawatov Khostovanim"),
    (re.compile(r"(?:lament for edessa|oghb edeseay|哀嘆以德薩)", re.I),
     "Oghb Edesioy"),
    (re.compile(r"(?:life|vark).{0,20}mashtot|馬什托茨生平", re.I),
     "Life of Mashtots"),
    (re.compile(r"(?:vardan|vardanay).{0,25}(?:war|paterazm)|瓦爾丹與亞美尼亞戰爭", re.I),
     "History of Vardan and the Armenian War"),
    (re.compile(r"(?:durr.{0,15}tam|kostbaren perle|澄明信仰之珍珠|精粹之珠)", re.I),
     "Ad-Durr ath-Thamīn"),
    (re.compile(r"(?:abu|abū).{0,8}(?:qurrah|qurra).{0,35}(?:icon|著作)|阿布.{0,4}(?:庫拉|古拉).{0,20}(?:聖像|著作)", re.I),
     "Works of Theodore Abū Qurrah"),
    (re.compile(r"(?:veneration of the holy icons|difesa delle icone|聖像崇敬論|聖像辯護論)", re.I),
     "Treatise on the Veneration of the Holy Icons (Abū Qurrah)"),
    (re.compile(r"disputation between a christian and a saracen|基督徒與撒拉森人辯論", re.I),
     "Disputatio Christiani et Saraceni"),
    (re.compile(r"(?:nagaśt|nebābunā|nebabenā).{0,30}(?:tergwām|tiregwām)", re.I),
     "Fetḥa Nagaśt"),
    (re.compile(r"homélies.{0,20}(?:isaac|isaac le syrien)", re.I),
     "Ascetical Homilies of Isaac of Nineveh"),
    (re.compile(r"homily on the apostle thomas and the resurrection", re.I),
     "Mēmrā on Thomas and the Resurrection"),
    (re.compile(r"preces s\. niersis clajensis", re.I),
     "Hawatov Khostovanim"),
    (re.compile(r"synaxarium.{0,35}copt", re.I),
     "Coptic Synaxarium"),
]


def known_corpus_pattern_hit(rows: list[dict]) -> str:
    haystack = "\n".join(
        f"{r.get('classification', {}).get('title_orig', '')} "
        f"{r.get('classification', {}).get('title_zh', '')} "
        f"{r.get('classification', {}).get('author', '')}"
        for r in rows
    )
    for pattern, corpus_title in KNOWN_CORPUS_PATTERNS:
        if pattern.search(haystack):
            return corpus_title
    return ""


def unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def norm(s: str) -> str:
    """Aggressive normalization for fuzzy matching of original-language titles."""
    if not s:
        return ""
    s = unescape(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # strip diacritics
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)  # drop punctuation (keeps latin-script core)
    s = NOISE.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_zh(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"[《》「」〈〉，。、：；！？\s（）()]", "", unescape(s))


def corpus_index() -> tuple[set[str], set[str], dict[str, str]]:
    """Return (normalized title_orig set, normalized title_zh set, zh->raw map)."""
    orig: set[str] = set()
    zh: set[str] = set()
    zh_raw: dict[str, str] = {}
    for f in TS_FILES:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for m in ORIG_RE.findall(text):
            n = norm(m)
            if n:
                orig.add(n)
        for m in ZH_RE.findall(text):
            n = norm_zh(m)
            if n:
                zh.add(n)
                zh_raw[n] = unescape(m)
    return orig, zh, zh_raw


def load_keep(ledger: Path) -> list[dict]:
    """Latest row per record_key, decision=keep_primary_work."""
    latest: dict[str, dict] = {}
    for line in ledger.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        k = r.get("record_key")
        if k:
            latest[k] = r
    keep = []
    for r in latest.values():
        c = r.get("classification", {})
        if c.get("decision") == "keep_primary_work":
            keep.append(r)
    return keep


def prefix_hit(cand: str, corpus: set[str]) -> str:
    """Fuzzy corpus match: exact, or one is a prefix of the other (>=6 chars)."""
    if not cand:
        return ""
    if cand in corpus:
        return cand
    for c in corpus:
        if len(cand) >= 6 and len(c) >= 6 and (cand.startswith(c) or c.startswith(cand)):
            return c
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--out", default=str(DATA / "source-catalog" / "curation-worklist.json"))
    args = ap.parse_args()

    keep = load_keep(Path(args.ledger))
    c_orig, c_zh, _ = corpus_index()

    groups: dict[str, list[dict]] = defaultdict(list)
    for r in keep:
        c = r["classification"]
        key = norm(c.get("title_orig", "")) or norm_zh(c.get("title_zh", "")) or r["record_key"]
        groups[key].append(r)

    in_corpus = []
    new_groups = []
    for key, rows in sorted(groups.items()):
        c0 = rows[0]["classification"]
        no = norm(c0.get("title_orig", ""))
        nz = norm_zh(c0.get("title_zh", ""))
        known_hit = next(
            (KNOWN_CORPUS_EQUIVALENTS[r["record_key"]]
             for r in rows if r["record_key"] in KNOWN_CORPUS_EQUIVALENTS),
            "",
        )
        hit = (known_hit or known_corpus_pattern_hit(rows) or
               prefix_hit(no, c_orig) or (nz if nz in c_zh else ""))
        entry = {"key": key, "n_editions": len(rows), "rows": rows, "corpus_hit": hit}
        (in_corpus if hit else new_groups).append(entry)

    print(f"keep_primary candidates: {len(keep)}  ->  unique works: {len(groups)}")
    print(f"  already in corpus (skip): {len(in_corpus)}")
    print(f"  NEW unique works to curate: {len(new_groups)}")
    print()
    print("=== NEW unique works (candidate for insertion, human-curate) ===")
    for e in new_groups:
        c = e["rows"][0]["classification"]
        eras = sorted({row["classification"].get("eraKey") for row in e["rows"]})
        colls = sorted({row["classification"].get("collectionKey") for row in e["rows"]})
        canons = sorted({row["classification"].get("canon") for row in e["rows"]})
        print(f"[{','.join(eras)} | {','.join(colls)} | {','.join(canons)}] "
              f"{c.get('title_zh')}  <-  {str(c.get('title_orig'))[:55]}  "
              f"(x{e['n_editions']}, {(c.get('author') or '')[:24]})")
    print()
    print("=== already-in-corpus (skipped) ===")
    for e in in_corpus:
        c = e["rows"][0]["classification"]
        print(f"  {c.get('title_zh')}  <-  {str(c.get('title_orig'))[:45]}  ~= corpus[{e['corpus_hit'][:30]}]")

    out = Path(args.out)
    out.write_text(json.dumps(
        {"new_works": [{"era_keys": sorted({r["classification"].get("eraKey") for r in e["rows"]}),
                        "collection_keys": sorted({r["classification"].get("collectionKey") for r in e["rows"]}),
                        "canons": sorted({r["classification"].get("canon") for r in e["rows"]}),
                        "n_editions": e["n_editions"],
                        "title_zh": e["rows"][0]["classification"].get("title_zh"),
                        "title_orig": e["rows"][0]["classification"].get("title_orig"),
                        "author": e["rows"][0]["classification"].get("author"),
                        "reason_zh": e["rows"][0]["classification"].get("reason_zh"),
                        "sources": [r.get("source_record", {}).get("source") for r in e["rows"]]}
                       for e in new_groups],
         "in_corpus_count": len(in_corpus)},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nworklist -> {out}")


if __name__ == "__main__":
    main()
