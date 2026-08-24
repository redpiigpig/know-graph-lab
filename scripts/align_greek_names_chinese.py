#!/usr/bin/env python3
"""Read the Chinese names of Septuagint figures out of the Chinese Bible itself.

Strong's indexes the New Testament, so it names Πέτρος and Αἴγυπτος but has
never heard of Ἰωάβ or Γαλαάδ.  ``biblical_people`` holds people and no places.
That leaves about a hundred and sixty names - most of the Septuagint's kings,
tribes, towns and peoples - with no Chinese in any register the site keeps.

They are not really missing, though.  和合本修訂版 renders every one of them; the
rendering just has to be found.  A Greek name occurs in particular verses, and
the Chinese of those same verses contains its Chinese name - a short run of
characters that shows up in nearly every one of them and hardly anywhere else.
Finding it is a matter of counting, not of guessing, and what comes out is the
Chinese Bible's own wording rather than anything invented here.

The alignment is deliberately conservative.  A candidate has to appear in most
of the sampled verses, has to be rare in the surrounding text, and has to win by
a clear margin; when no candidate does, the name is left empty and reported.
Books whose Greek and Hebrew verse numbers do not correspond - the Psalms, which
are renumbered, Jeremiah, which is reordered, Daniel and Esther, which are
different books in Greek - are never sampled, because a misaligned verse would
supply a confident and wrong answer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_source_texts as gs
import export_reader_rcuv2010_greek as rcuv
from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-appendices.json"
CHINESE_CACHE = CACHE / "rcuv-chapters.json"

# Books where a Greek verse number and a Chinese one mean the same verse.
# The Psalms are renumbered, Jeremiah is reordered, Daniel and Esther are other
# books entirely in Greek, and the deuterocanon is not in this translation.
ALIGNED_BOOKS = {
    "Gen": "GEN", "Exod": "EXO", "Lev": "LEV", "Num": "NUM", "Deut": "DEU",
    "Josh": "JOS", "Judg": "JDG", "Ruth": "RUT", "1Sam": "1SA", "2Sam": "2SA",
    "1Kgs": "1KI", "2Kgs": "2KI", "1Chr": "1CH", "2Chr": "2CH",
    "Ezra": "EZR", "Neh": "NEH", "Job": "JOB", "Prov": "PRO", "Eccl": "ECC",
    "Song": "SNG", "Isa": "ISA", "Ezek": "EZK", "Hos": "HOS", "Joel": "JOL",
    "Amos": "AMO", "Obad": "OBA", "Jonah": "JON", "Mic": "MIC", "Nah": "NAM",
    "Hab": "HAB", "Zeph": "ZEP", "Hag": "HAG", "Zech": "ZEC", "Mal": "MAL",
}

SAMPLE_PER_NAME = 10
MIN_COVERAGE = 0.7          # the name must be in most of the sampled verses
MAX_BACKGROUND = 0.12       # and rare in the chapters around them
MIN_LENGTH, MAX_LENGTH = 2, 6

# Characters that begin or end a Chinese name in these translations far too often
# to be part of one; a candidate that starts with 「和」 has swallowed a conjunction.
# 「所」 is deliberately absent: it begins 所羅門, and excluding it truncated
# Solomon to 羅門.
EDGE_NOISE = "和與的了在是有不也就這那他她它們之於以而或即為被把將對從"


def load_targets() -> list[dict]:
    payload = json.loads(APPENDICES.read_text(encoding="utf-8"))
    return [e for e in payload["appendices"][0]["entries"] if not e.get("zh")]


def occurrences(targets: list[dict]) -> dict[str, list[tuple[str, int, int]]]:
    """Where in the Septuagint each still-unnamed name is written.

    Matching is on the surface form the appendix already recorded as this name's
    commonest spelling, which is exact and needs no lemmatiser; a name is looked
    for in every aligned book until it has enough places to go on.
    """
    wanted = {e["headword"]: e for e in targets}
    stems = {}
    for headword in wanted:
        # Greek declines its names and shifts their accents, so compare on the
        # folded stem: Ἀχαάβ is written Ἀχαὰβ mid-sentence, and Τύρος appears as
        # Τύρου and Τύρῳ.  Folding removes the accents; dropping the last letter
        # removes the ending.
        # Only a Greek case ending may be dropped.  Cutting the last letter off
        # everything turned Ἀβράμ into a stem that also matches Ἀβραάμ, and the
        # two men then shared their verses.
        stem = fold(headword)
        stems[headword] = stem[:-1] if len(stem) > 4 and stem[-1] in "σνυ" else stem
    found: dict[str, list] = defaultdict(list)
    for book in ALIGNED_BOOKS:
        try:
            verses = gs._swete_book_cached(book)
        except (KeyError, FileNotFoundError):
            continue
        for verse in verses:
            words = fold(verse.text).split()
            for headword, stem in stems.items():
                if not stem or len(found[headword]) >= SAMPLE_PER_NAME * 3:
                    continue
                # The stem has to begin a word.  Matching it anywhere in the
                # verse found Τύρος inside μαρτύρομαι and aligned Tyre with
                # 「見證」, which is the verb's meaning and not a city.
                if any(word.startswith(stem) for word in words):
                    found[headword].append((book, verse.chapter, verse.verse))
    return found


def choose_chapters(found: dict[str, list]) -> list[tuple[str, int]]:
    """The fewest chapters that still give every name its sample.

    Names cluster - half of Kings' officials appear in the same few chapters -
    so picking chapters greedily by how many names they serve turns several
    hundred fetches into a fraction of that.
    """
    remaining = {name: SAMPLE_PER_NAME for name in found if found[name]}
    by_chapter: dict[tuple[str, int], set] = defaultdict(set)
    for name, places in found.items():
        for book, chapter, _ in places:
            by_chapter[(book, chapter)].add(name)
    chosen: list[tuple[str, int]] = []
    while remaining:
        best = max(
            by_chapter,
            key=lambda key: sum(1 for name in by_chapter[key] if remaining.get(name)),
            default=None,
        )
        if best is None:
            break
        serves = [name for name in by_chapter[best] if remaining.get(name)]
        if not serves:
            break
        chosen.append(best)
        for name in serves:
            remaining[name] -= 1
            if remaining[name] <= 0:
                del remaining[name]
        del by_chapter[best]
    return chosen


def fetch_chinese(chapters: list[tuple[str, int]]) -> dict[str, dict[int, str]]:
    cache = json.loads(CHINESE_CACHE.read_text(encoding="utf-8")) if CHINESE_CACHE.exists() else {}
    todo = [(b, c) for b, c in chapters if f"{b}.{c}" not in cache]
    print(f"  需取中文 {len(chapters)} 章，其中 {len(todo)} 章尚未快取")
    for index, (book, chapter) in enumerate(todo, 1):
        key = f"{book}.{chapter}"
        try:
            rcuv.BOOK_CODES.setdefault(book, ALIGNED_BOOKS[book])
            payload = rcuv.fetch_chapter(book, chapter)
            cache[key] = {str(v["verse"]): v["text"] for v in payload["verses"]}
        except Exception as error:                       # noqa: BLE001 - report, continue
            print(f"    {key} 取用失敗：{type(error).__name__}: {error}")
            cache[key] = {}
        if index % 20 == 0:
            print(f"    已取 {index}/{len(todo)}")
            CHINESE_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.4)
    CHINESE_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return {key: {int(k): v for k, v in value.items()} for key, value in cache.items()}


def candidates(text: str) -> set[str]:
    """Every short run of Chinese characters in a verse, as a possible name."""
    found = set()
    for run in re.findall(r"[一-鿿]+", text):
        for size in range(MIN_LENGTH, MAX_LENGTH + 1):
            for start in range(len(run) - size + 1):
                piece = run[start:start + size]
                if piece[0] in EDGE_NOISE or piece[-1] in EDGE_NOISE:
                    continue
                found.add(piece)
    return found


def align(name: str, places: list, chinese: dict, background: Counter, total: int) -> dict:
    """The Chinese name, if the sampled verses agree on one."""
    verses = []
    for book, chapter, verse in places[:SAMPLE_PER_NAME]:
        text = chinese.get(f"{book}.{chapter}", {}).get(verse, "")
        if text:
            verses.append((f"{book}.{chapter}.{verse}", text))
    if len(verses) < 2:
        return {}

    tally: Counter = Counter()
    for _, text in verses:
        for piece in candidates(text):
            tally[piece] += 1

    scored = []
    for piece, hits in tally.items():
        coverage = hits / len(verses)
        if coverage < MIN_COVERAGE:
            continue
        noise = background[piece] / max(total, 1)
        if noise > MAX_BACKGROUND:
            continue
        # Longer is better when coverage ties: 尼布甲尼撒 beats 尼布甲.
        scored.append((coverage - noise, len(piece), piece))
    if not scored:
        return {}
    scored.sort(reverse=True)
    best = scored[0]
    # Prefer the longer of two candidates when one contains the other and covers
    # nearly as many verses: the gentilic 迦南人 is the word in the text, and
    # 迦南 is only the part of it the shorter window happened to catch.
    longer = [
        item for item in scored
        if best[2] in item[2] and len(item[2]) > len(best[2])
        and item[0] >= best[0] - (0.3 if item[2] == best[2] + "人" else 0.15)
    ]
    if longer:
        best = max(longer, key=lambda item: (len(item[2]), item[0]))
    # Drop candidates that are merely a piece of the winner.
    rivals = [item for item in scored[1:] if item[2] not in best[2] and best[2] not in item[2]]
    # A name that always keeps company with another - Γαλαάδ with 瑪拿西, Ῥοβοάμ
    # with 所羅門 - has a rival in every verse, so the margin is judged against
    # the runner-up only when the two are genuinely close.
    if rivals and best[0] - rivals[0][0] < 0.1:
        return {}
    # 「亞述王」 is a man's title, not the people's name, and the sampled verses
    # happen to be about him.  A trailing role word comes off when the name
    # without it is also well attested.  「人」 stays: it is what makes 亞摩利人
    # the name of a people rather than a place.
    chinese = best[2]
    while len(chinese) > 2 and chinese[-1] in "王國城地":
        shorter = chinese[:-1]
        if tally.get(shorter, 0) < tally[best[2]]:
            break
        chinese = shorter

    return {
        "zh": chinese,
        "coverage": round(best[0], 3),
        "evidence": [ref for ref, _ in verses],
    }


def classify(entries: list[dict]) -> None:
    """Say whether each name belongs to a person, a place or a people.

    信望愛 states it outright for the names Strong's covers, but the ones read out
    of the Chinese Bible arrive with no such label.  Two registers settle most of
    them - a Chinese name that ``biblical_people`` holds is a person's, one that
    ``place_names`` holds is a place's - and Greek morphology settles a third
    group: a gentilic in -αῖος rendered into Chinese ending in 人 names a people.
    Anything still unsettled keeps an empty label rather than a guessed one.
    """
    import os

    import requests
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        print("  （未設定 Supabase 憑證，略過分類）")
        return
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}

    people, offset = set(), 0
    while True:
        rows = requests.get(
            f"{url}/rest/v1/biblical_people",
            params={"select": "name_zh", "limit": "500", "offset": str(offset)},
            headers=headers, timeout=60,
        ).json()
        for row in rows:
            name = re.sub(r"（.*?）", "", row.get("name_zh") or "").strip()
            if name:
                people.add(name)
        if len(rows) < 500:
            break
        offset += 500
    places = {
        (row.get("name_recommended") or "").strip()
        for row in requests.get(
            f"{url}/rest/v1/place_names",
            params={"select": "name_recommended", "limit": "5000"},
            headers=headers, timeout=60,
        ).json()
    }

    counts: Counter = Counter()
    for entry in entries:
        if entry.get("kind"):
            counts[entry["kind"]] += 1
            continue
        chinese = entry.get("zh", "")
        gentilic = entry["lemma"].endswith(("αῖος", "ιος", "ίτης"))
        if chinese and chinese.endswith("人") and gentilic:
            entry["kind"] = "people"
        elif chinese and chinese in people:
            entry["kind"] = "person"
        elif chinese and chinese in places:
            entry["kind"] = "place"
        counts[entry.get("kind") or "未分類"] += 1
    print("  分類：" + "、".join(f"{k} {v}" for k, v in counts.most_common()))


def main() -> None:
    parser = argparse.ArgumentParser(description="用中文聖經對出七十士專名的中文")
    parser.add_argument("--write", action="store_true", help="寫回 greek-appendices.json")
    parser.add_argument("--limit", type=int, default=0, help="只處理前 N 個未定名者")
    args = parser.parse_args()

    payload = json.loads(APPENDICES.read_text(encoding="utf-8"))
    targets = [e for e in payload["appendices"][0]["entries"] if not e.get("zh")]
    if args.limit:
        targets = targets[:args.limit]
    print(f"  待定名 {len(targets)} 個，於七十士中定位…")

    found = occurrences(targets)
    locatable = {k: v for k, v in found.items() if v}
    print(f"  其中 {len(locatable)} 個在可對位的書卷裡找得到")

    chapters = choose_chapters(locatable)
    chinese = fetch_chinese(chapters)

    background: Counter = Counter()
    total = 0
    for verses in chinese.values():
        for text in verses.values():
            total += 1
            for piece in candidates(text):
                background[piece] += 1
    print(f"  背景語料 {total} 節，用以剔除常用字串")

    named = 0
    for entry in targets:
        places = locatable.get(entry["headword"])
        if not places:
            continue
        result = align(entry["headword"], places, chinese, background, total)
        if result:
            entry.update(
                zh=result["zh"], zhSource="和合本修訂版（RCUV2）",
                zhRoute="中文聖經對位", zhEvidence=result["evidence"],
                zhReview="由經節對位取得，建議複核",
            )
            named += 1

    classify(payload["appendices"][0]["entries"])

    print(f"  對出中文 {named} 個；仍未定名 {len(targets) - named}")
    sample = [e for e in targets if e.get("zhRoute") == "中文聖經對位"][:20]
    for entry in sample:
        print(f"    {entry['headword']:<16s} → {entry['zh']:<8s} {entry['zhEvidence'][0]}")
    left = [e["headword"] for e in targets if not e.get("zh")]
    print(f"  未定名者：{'、'.join(left[:25])}")

    if args.write:
        APPENDICES.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                              encoding="utf-8")
        print(f"已寫回 {APPENDICES}")
    else:
        print("（未寫檔；加 --write 才會寫回）")


if __name__ == "__main__":
    main()
