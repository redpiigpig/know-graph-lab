#!/usr/bin/env python3
"""The lower volume's fifty readings, from the fathers to the modern curia.

Twenty-five patristic and medieval readings, then twenty-five from Trent
onwards.  Where the upper volume can print a whole chapter every time because
biblical chapters are short, this volume cannot: Lumen Gentium runs to
twenty-two thousand words and Gaudium et Spes to twenty-seven.  So each reading
declares what it is.  A creed, a hymn, a bull, a conciliar canon is printed
entire and marked ``complete``; a constitution or an encyclical is printed from
a stated paragraph range and marked ``excerpt``.  The two are never mixed
silently, and no reading is described as complete because nobody checked.

Chinese comes from whatever already sits beside the Latin in this repository.
Seven hundred and fifty-three of the church documents here were gathered for the
parallel readers and already have it, which is why the modern half draws on
those rather than fetching the same texts again from vatican.va: a reading whose
translation has to be promised later is a reading that ships without one.

The order inside each half is computed, not chosen.  The measure is the same one
the upper volume uses -- how much of the passage the reader has already been
taught, against how long its sentences run -- so that Ambrose's hymns arrive
before Aquinas's metaphysics without anyone having to assert that they are
easier.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
CHURCH = CACHE / "latin-church"
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
OUTPUT = CACHE / "church-plan.json"

# kind: repo = a -latin.txt in data/, file = a fetched Latin Library text
# extent: complete | excerpt
PATRISTIC = [
    ("使徒信經", "Symbolum Apostolorum", "file", "liturgy/creeds.html.txt", "complete", "2 世紀起", "", ("^Symbolum Apostolorum$", "^Quicumque")),
    ("亞他納修信經", "Symbolum Quicumque", "file", "liturgy/creeds.html.txt", "complete", "5–6 世紀", "三位一體與基督二性的命題鏈", ("^Quicumque", "^Symbolum Nicaenum Pristinum$")),
    ("聖安博晨禱聖詩", "Hymni Ambrosiani", "file", "fathers/ambrose__hymns.html.txt", "complete", "4 世紀", "含 Aeterne rerum conditor"),
    ("將臨期詠：懇求厄瑪奴耳", "Veni, veni, Emmanuel", "file", "liturgy/hymni.html.txt", "complete", "12 世紀", "", ("^Veni, veni, Emmanuel", "^Puer nobis nascitur")),
    ("聖誕詠", "Adeste, fideles", "file", "liturgy/hymni.html.txt", "complete", "18 世紀", "", ("^Adeste, fideles", "^Gloria, laus et honor")),
    ("聖枝主日詠", "Gloria, laus et honor", "file", "liturgy/hymni.html.txt", "complete", "9 世紀", "德奧道夫作", ("^Gloria, laus et honor", "^Stabat mater dolorosa")),
    ("聖母痛苦詠", "Stabat mater dolorosa", "file", "liturgy/hymni.html.txt", "complete", "13 世紀", "", ("^Stabat mater dolorosa", "^Chorus novae Ierusalem")),
    ("末日經", "Dies irae", "file", "liturgy/diesirae.html.txt", "complete", "13 世紀", "追思彌撒繼抒詠"),
    ("復活詠", "Chorus novae Ierusalem", "file", "liturgy/hymni.html.txt", "complete", "11 世紀", "傅爾伯作", ("^Chorus novae Ierusalem", "^O quanta, qualia")),
    ("天鄉之歌", "O quanta, qualia", "file", "liturgy/hymni.html.txt", "complete", "12 世紀", "阿伯拉作", ("^O quanta, qualia", "^Dies irae")),
    ("聖體聖詩集", "Hymni de Corpore Christi", "file", "medieval/aquinas__corpuschristi.shtml.txt", "complete", "1264", "含 Pange lingua、Lauda Sion、Verbum supernum、Adoro te"),
    ("斐理伯與佩爾佩圖亞殉道錄", "Passio Perpetuae et Felicitatis", "file", "fathers/perp.html.txt", "excerpt", "203", "取殉道日敘事段"),
    ("厄革里雅朝聖記", "Itinerarium Egeriae", "file", "fathers/egeria2.html.txt", "excerpt", "4 世紀末", "耶路撒冷聖週禮儀實錄"),
    ("戴都良論祈禱", "De oratione", "file", "fathers/tertullian__tertullian.oratione.shtml.txt", "excerpt", "3 世紀初", "主禱文逐句詮釋"),
    ("聖傑羅尼莫書信", "Epistulae", "file", "fathers/jerome__epistulae.html.txt", "excerpt", "4 世紀末", "武加大譯者自述譯經原則"),
    ("聖奧思定懺悔錄 卷一", "Confessiones I", "file", "fathers/augustine__conf1.shtml.txt", "excerpt", "397–400", "取卷一開篇"),
    ("聖奧思定懺悔錄 卷八", "Confessiones VIII", "file", "fathers/augustine__conf8.shtml.txt", "excerpt", "397–400", "花園歸化敘事"),
    ("聖良一世四旬期講道", "Sermones de Quadragesima", "file", "fathers/leothegreat__quadragesima1.html.txt", "excerpt", "5 世紀中", ""),
    ("肋令的味增爵：備忘錄", "Commonitorium", "file", "fathers/vicentius.html.txt", "excerpt", "434", "「普世、始終、眾人所信」準則"),
    ("聖本篤會規", "Regula Benedicti", "file", "medieval/benedict.html.txt", "excerpt", "6 世紀", "取序言與第一章"),
    ("大額我略", "Gregorius Magnus", "file", "medieval/greg.html.txt", "excerpt", "6 世紀末", ""),
    ("聖安瑟莫：證道書", "Proslogion", "file", "medieval/anselmproslogion.html.txt", "excerpt", "1078", "取第二至四章"),
    ("聖文德：心靈邁向天主的旅程", "Itinerarium mentis in Deum", "file", "medieval/bonaventura.itinerarium.html.txt", "excerpt", "1259", ""),
    ("額我略七世：教宗敕語", "Dictatus papae", "repo", "dictatus-papae-1075", "complete", "1075", "二十七條，全文極短"),
    ("波尼法爵八世：唯一至聖", "Unam Sanctam", "repo", "unam-sanctam-1302", "complete", "1302", "中世紀教權論的頂點"),
]

MODERN = [
    ("特倫多大公會議：聖經與聖傳", "Concilium Tridentinum, sessio IV", "repo", "trent-04", "complete", "1546", "正典目錄與武加大譯本的地位"),
    ("特倫多大公會議：成義論", "Concilium Tridentinum, sessio VI", "repo", "trent-06", "excerpt", "1547", "取序言與前十章"),
    ("特倫多大公會議：聖事總論", "Concilium Tridentinum, sessio VII", "repo", "trent-07", "excerpt", "1547", "取聖事總論法條"),
    ("特倫多大公會議：至聖聖體", "Concilium Tridentinum, sessio XIII", "repo", "trent-13", "excerpt", "1551", "體變論"),
    ("特倫多大公會議：彌撒聖祭", "Concilium Tridentinum, sessio XXII", "repo", "trent-22", "excerpt", "1562", "彌撒作為祭獻"),
    ("特倫多大公會議：聖像與敬禮", "Concilium Tridentinum, sessio XXV", "repo", "trent-25", "excerpt", "1563", ""),
    ("梵一：天主子", "Dei Filius", "repo", "df", "excerpt", "1870", "信仰與理性"),
    ("梵一：永恆牧者", "Pastor Aeternus", "repo", "pa", "excerpt", "1870", "教宗首席權與不能錯"),
    ("良十三：永恆之父", "Aeterni Patris", "repo", "aeterni-patris-1879", "excerpt", "1879", "復興多瑪斯哲學"),
    ("良十三：新事", "Rerum Novarum", "repo", "rerum-novarum-1891", "excerpt", "1891", "天主教社會訓導的起點"),
    ("良十三：至上智慧的天主", "Providentissimus Deus", "repo", "providentissimus-deus-1893", "excerpt", "1893", "聖經研究"),
    ("庇護十一：四十年", "Quadragesimo Anno", "repo", "quadragesimo-anno-1931", "excerpt", "1931", "輔助原則"),
    ("庇護十二：奧體", "Mystici Corporis Christi", "repo", "mystici-corporis-1943", "excerpt", "1943", "教會作為基督奧體"),
    ("若望二十三：和平於世", "Pacem in Terris", "repo", "pacem-in-terris-1963", "excerpt", "1963", "首份致全人類的通諭"),
    ("梵二：禮儀憲章", "Sacrosanctum Concilium", "repo", "sc", "excerpt", "1963", "禮儀改革的憲章"),
    ("梵二：教會憲章", "Lumen Gentium", "repo", "lg", "excerpt", "1964", "取第一、二章"),
    ("梵二：大公主義法令", "Unitatis Redintegratio", "repo", "ur", "excerpt", "1964", ""),
    ("梵二：教會對非基督宗教態度宣言", "Nostra Aetate", "repo", "na", "complete", "1965", "全文僅約兩千詞"),
    ("梵二：天主的啟示教義憲章", "Dei Verbum", "repo", "dv", "excerpt", "1965", "聖經與聖傳"),
    ("梵二：信仰自由宣言", "Dignitatis Humanae", "repo", "dh", "excerpt", "1965", ""),
    ("梵二：論教會在現代世界牧職憲章", "Gaudium et Spes", "repo", "gs", "excerpt", "1965", "取序言與第一部第一章"),
    ("保祿六：人類生命", "Humanae Vitae", "repo", "humanae-vitae-1968", "excerpt", "1968", ""),
    ("若望保祿二：信仰與理性", "Fides et Ratio", "repo", "fides-et-ratio-1998", "excerpt", "1998", ""),
    ("本篤十六：天主是愛", "Deus Caritas Est", "repo", "deus-caritas-est-2005", "excerpt", "2005", ""),
    ("方濟各：願祢受讚頌", "Laudato Si'", "repo", "laudato-si-2015", "excerpt", "2015", "現行教廷拉丁文的當代樣貌"),
]

# Every reading is a complete chapter or a complete piece.  Where a work is too
# long to print entire, what is printed is a whole number of its own divisions --
# chapters, numbered sections, canons -- never a slice measured in words.
PER_HALF = 25
assert len(PATRISTIC) == PER_HALF, len(PATRISTIC)
assert len(MODERN) == PER_HALF, len(MODERN)


SECTION_NUMBER = re.compile(r"^\s*(\d{1,3})[.、]", re.M)
PLACEHOLDER = ("待補", "⏳")
EXCERPT_MARKS = ("教義選集", "Denzinger", "中譯條目")


def chinese_kind(latin_path: Path) -> tuple[str, int]:
    """What kind of Chinese sits beside this Latin, if any.

    A -chinese.txt file existing is not the same as a parallel translation
    existing, and treating the two as equal was wrong in three different ways at
    once.  Some of these files are a placeholder that says 中譯待補.  Fifteen are
    selections from the Denzinger anthology -- the Sacrosanctum Concilium file
    holds one entry out of a constitution of a hundred and thirty paragraphs and
    says so in its own header.  Only nine are translations of the document, and
    only five of those number their sections so that the two sides can be
    matched.

    Pairing the other twenty-two by paragraph index would print Latin beside
    Chinese from a different part of the text, and it would look perfectly fine
    on the page.
    """
    chinese = latin_path.with_name(latin_path.name.replace("-latin.txt", "-chinese.txt"))
    if not chinese.exists():
        return "none", 0
    raw = chinese.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"^#.*$", "", raw, flags=re.M).strip()
    if len(body) < 200 or any(mark in raw for mark in PLACEHOLDER):
        return "placeholder", 0
    if any(mark in raw for mark in EXCERPT_MARKS):
        return "denzinger-excerpts", 0
    numbers = len(set(SECTION_NUMBER.findall(body)))
    return ("full-translation-numbered" if numbers >= 5 else
            "full-translation-unnumbered"), numbers


def load_text(kind: str, ref: str, repo_index: dict) -> tuple[str, str, bool]:
    """Return (text, source path, whether a Chinese parallel already exists)."""
    if kind == "repo":
        doc = repo_index.get(ref)
        if not doc:
            raise SystemExit(f"repo 找不到 {ref}")
        return doc["text"], doc["path"], doc["hasChinese"]
    path = CHURCH / ref
    if not path.exists():
        raise SystemExit(f"語料缺檔 {ref}")
    return (path.read_text(encoding="utf-8", errors="replace"),
            str(path.relative_to(ROOT)).replace("\\", "/"), False)


def section(text: str, anchors: tuple[str, str]) -> str:
    """Cut one hymn or creed out of the anthology that holds it.

    Six hymns and two creeds live inside two files, and pointing eight readings
    at the whole file makes eight readings that print the same sixteen hundred
    words.  The anchors are matched on the *last* occurrence of the opening
    line, because these files repeat every title in a table of contents at the
    top and matching the first occurrence cuts the contents list instead of the
    hymn.
    """
    lines = text.splitlines()
    start_re, end_re = re.compile(anchors[0]), re.compile(anchors[1])
    starts = [i for i, line in enumerate(lines) if start_re.search(line.strip())]
    if not starts:
        raise SystemExit(f"找不到起點 {anchors[0]}")

    def span(begin: int) -> tuple[int, int]:
        for index in range(begin + 1, len(lines)):
            if end_re.search(lines[index].strip()):
                return begin, index
        return begin, len(lines)

    # Of the places the title appears, take the one that yields the longest
    # section.  The contents list at the top of these files repeats every title
    # in order, so a title there is immediately followed by the next title and
    # its "section" is one line long; the real one is hundreds.  Choosing by
    # length needs no knowledge of how long the contents list happens to be.
    begin, end = max((span(i) for i in starts), key=lambda pair: pair[1] - pair[0])
    return chr(10).join(lines[begin:end]).strip()


DIVISION_RULES = [
    ("章", r"^(?:CAPUT|Caput|CAP\.|Cap\.)\s+[IVXLC\d]+"),
    # The Latin Library numbers several works in brackets -- the Passio
    # Perpetuae runs [1] to [21] -- and those are the edition's own
    # divisions, so they outrank a bare "4." that may just be a list item.
    ("節", r"^\[\d{1,3}\]"),
    ("節", r"^[IVXLC]{1,6}\.\s"),
    ("號", r"^\d{1,3}\.\s"),
    # A chapter heading is not always punctuated.  The Proslogion writes
    # "1 Excitatio mentis ad contemplandum Deum" -- a number, a space, a
    # capitalised title -- and without this rule the whole work counts as one
    # division and six thousand words go into a lesson that budgeted fourteen
    # hundred.  Last in priority, so a work that punctuates its numbers is
    # still cut on those.
    ("章", r"^\d{1,3}\s+[A-Z][a-z]"),
]

UNIT_BUDGET = 1400
WHOLE_WORK_LIMIT = 6000


CENTURY = re.compile(r"(\d{1,2})\s*[–—/／]?\s*(\d{1,2})?\s*世紀")
YEAR = re.compile(r"\b(\d{3,4})\b")


def year_of(dated: str) -> int:
    """Sort key for a date written the way a bibliography writes it.

    The lower volume is ordered by when a text was written, not by how hard it
    is.  The owner's point on 2026-08-26 is that a reading need not match the
    vocabulary already taught, and once that constraint is gone a difficulty
    sort has nothing to recommend it -- while chronology is the whole argument
    of the volume: fifteen centuries of church Latin, in order.
    """
    year = YEAR.search(dated)
    if year:
        return int(year.group(1))
    century = CENTURY.search(dated)
    if century:
        first = int(century.group(1))
        last = int(century.group(2) or first)
        return (first + last - 1) * 50
    return 9999


def divisions(text: str) -> tuple[str, list[str]]:
    """Split a work at its own strongest structural marker.

    Priority matters.  A conciliar constitution numbers its paragraphs *and*
    divides into chapters, and cutting it at paragraph 1 when it has chapters
    would print a fragment of a chapter rather than a chapter.
    """
    lines = text.splitlines()
    for label, pattern in DIVISION_RULES:
        marker = re.compile(pattern)
        starts = [i for i, line in enumerate(lines) if marker.match(line.strip())]
        if len(starts) < 2:
            continue
        blocks = []
        for index, begin in enumerate(starts):
            end = starts[index + 1] if index + 1 < len(starts) else len(lines)
            block = chr(10).join(lines[begin:end]).strip()
            if block:
                blocks.append(block)
        if len(blocks) >= 2:
            return label, blocks
    return "", []


def complete_unit(text: str, budget: int = UNIT_BUDGET) -> tuple[str, int, str]:
    """Print whole divisions, never part of one.

    The owner's rule on 2026-08-26: a lesson reads a complete chapter or a
    complete piece.  A word-count excerpt breaks that -- it stops wherever nine
    hundred words happen to land, mid-argument -- so the cut is made at the
    work's own boundaries and the budget only decides how many of them fit.
    A single division larger than the budget is still printed whole, because a
    half chapter is not a chapter.
    """
    label, blocks = divisions(text)
    if not blocks:
        total = len(L.words(text))
        if total <= WHOLE_WORK_LIMIT:
            return text.strip(), total, "全文"
        # No divisions and too long to print entire.  Complete paragraphs are
        # the largest honest unit available; say so rather than implying a
        # chapter was chosen.
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        kept, count = [], 0
        for paragraph in paragraphs:
            words = len(L.words(paragraph))
            if kept and count + words > budget:
                break
            kept.append(paragraph)
            count += words
        return ((chr(10) * 2).join(kept), count,
                f"原文無分章標記；取前 {len(kept)} 個完整段落，非全文")

    kept, count = [], 0
    for block in blocks:
        words = len(L.words(block))
        if kept and count + words > budget:
            break
        kept.append(block)
        count += words
    span = f"第 1–{len(kept)} {label}" if len(kept) > 1 else f"第 1 {label}"
    note = f"{span}（完整，共 {len(blocks)} {label}）"
    return (chr(10) * 2).join(kept), count, note


def measure(text: str, lm: Lemmatiser, taught: set[str]) -> dict:
    sentences = [s for s in re.split(r"[.;:?!]", text) if s.strip()]
    tokens = [w for w in L.words(text) if lm.is_word(w)]
    known = names = 0
    for word in tokens:
        lemma = lm.lemma(word)
        if lemma and lemma in lm.names:
            names += 1
        elif lemma and L.fold(lemma) in taught:
            known += 1
    total = max(len(tokens), 1)
    coverage = (known + names) / total
    mean_sentence = statistics.mean(len(L.words(s)) for s in sentences) if sentences else 0.0
    return {
        "words": len(tokens),
        "coverage": round(coverage, 4),
        "meanSentenceWords": round(mean_sentence, 1),
        "difficulty": round((1 - coverage) * 100 + mean_sentence / 4, 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lm = Lemmatiser()
    taught: set[str] = set()
    if VOCABULARY.exists():
        data = json.loads(VOCABULARY.read_text(encoding="utf-8"))
        taught = {L.fold(e["headword"]) for e in data["entries"]}
    if not taught:
        print("[!] 尚無詞表，難度只反映句長")

    repo_index = {doc["slug"]: doc for doc in L.church_documents()}

    def build(rows, era):
        out = []
        for spec in rows:
            title, latin_title, kind, ref, extent, dated, note = spec[:7]
            anchors = spec[7] if len(spec) > 7 else None
            text, path, _ = load_text(kind, ref, repo_index)
            zh_kind, zh_sections = (chinese_kind(ROOT / path) if kind == "repo"
                                    else ("none", 0))
            if anchors:
                text = section(text, anchors)
            printed, printed_words, rule = (
                complete_unit(text) if extent == "excerpt"
                else (text, len(L.words(text)), "全文"))
            out.append({
                "title": title, "latinTitle": latin_title, "era": era,
                "sourceKind": kind, "sourceRef": ref, "sourcePath": path,
                "section": list(anchors) if anchors else None,
                "extent": extent, "date": dated, "year": year_of(dated), "note": note,
                "printedWords": printed_words,
                "excerptRule": rule,
                "chineseSource": zh_kind,
                "chineseSections": zh_sections,
                # Only a numbered full translation can be set beside the Latin
                # automatically.  Everything else goes to the self-translation
                # queue, with what exists recorded so a human can align it later.
                "chineseParallel": ("repo-aligned-by-number"
                                    if zh_kind == "full-translation-numbered"
                                    else "pending"),
                **measure(printed, lm, taught),
            })
        out.sort(key=lambda r: (r["year"], r["title"]))
        return out

    plan = build(PATRISTIC, "教父與中世紀") + build(MODERN, "特倫多以降")
    for index, row in enumerate(plan, start=1):
        row["lesson"] = index

    complete = sum(1 for r in plan if r["extent"] == "complete")
    with_zh = sum(1 for r in plan if r["chineseParallel"] != "pending")
    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "volume": "下冊",
        "counts": {"readings": len(plan), "complete": complete,
                   "excerpt": len(plan) - complete, "chineseReady": with_zh},
        "terminalSection": {
            "title": "常年期主日彌撒經文",
            "latinTitle": "Ordo Missae, tempus per annum",
            "status": "latin_frozen_chinese_self_translated",
            "note": "拉丁文取自 Collins《A Primer of Ecclesiastical Latin》讀本部分所印之"
                    "現行彌撒常規；本私人版之製作已獲口頭同意。中文為自譯研讀本，"
                    "非教會核准之禮儀譯本——中文彌撒另有《感恩祭典》，本書不取代之。"
                    "此節獨立於五十篇讀本之外。",
        },
        "readings": plan,
    }
    print(f"下冊 {len(plan)} 篇（按年代排序）：完整全文 {complete}、"
          f"取完整章節 {len(plan) - complete}；可直接對照的既有中譯 {with_zh}")
    kinds = Counter(r["chineseSource"] for r in plan)
    print("　既有中文檔分類：", dict(kinds))
    for row in plan:
        mark = "全" if row["extent"] == "complete" else "章"
        zh = "中" if row["chineseParallel"] != "pending" else "－"
        print(f"{row['lesson']:>3} {mark}{zh} {row['date']:>8s} {row['title']:<24s} "
              f"{row['words']:>5}詞  {row['excerptRule']}")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
