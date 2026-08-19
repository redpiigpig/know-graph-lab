"""Strict RCUV2010 snapshot loading and MT-to-RCUV verse mapping.

The Hebrew reader follows WLC/MT numbering while the approved Traditional-
Chinese translation uses common Protestant numbering.  Keep this crosswalk in
one place so chapter, memory, print, web, and QA builds cannot drift apart.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


RCUV_VERSION_CODE = "cuv2010"
RCUV_VARIANT = "RCUV2（上帝版）"


def load_rcuv_snapshot(path: Path) -> tuple[dict[tuple[str, int, int], dict[str, Any]], dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    translation = payload.get("translation") or {}
    if translation.get("versionCode") != RCUV_VERSION_CODE:
        raise ValueError(f"{path} is not explicitly {RCUV_VERSION_CODE}")
    if translation.get("variant") != RCUV_VARIANT:
        raise ValueError(f"{path} is not the approved {RCUV_VARIANT}")

    index: dict[tuple[str, int, int], dict[str, Any]] = {}
    for book in payload.get("books") or []:
        book_name = str(book.get("name") or "").strip()
        if not book_name:
            raise ValueError("RCUV snapshot contains a book without name")
        for chapter in book.get("chapters") or []:
            chapter_number = int(chapter["chapter"])
            superscriptions = [
                re.sub(r"\s+", " ", str(value)).strip()
                for value in chapter.get("superscriptions") or []
                if str(value).strip()
            ]
            for verse in chapter.get("verses") or []:
                start = int(verse["verse"])
                end = int(verse.get("verseEnd") or start)
                text = re.sub(r"\s+", "", str(verse.get("text") or "")).strip()
                if not text:
                    raise ValueError(f"empty RCUV verse {book_name}.{chapter_number}.{start}")
                record = {
                    "text": text,
                    "verse": start,
                    "verseEnd": end,
                    "superscriptions": superscriptions,
                    "sourceUrl": chapter.get("sourceUrl"),
                    "responseSha256": chapter.get("responseSha256"),
                }
                for verse_number in range(start, end + 1):
                    key = (book_name, chapter_number, verse_number)
                    if key in index:
                        raise ValueError(f"duplicate RCUV verse key: {key}")
                    index[key] = record
    if not index:
        raise ValueError(f"RCUV snapshot has no verses: {path}")
    return index, translation


def _wrap_title(value: str) -> str:
    value = value.strip()
    if not value:
        return "（詩題）"
    return f"（{value}）"


def _psalm_title_translation(titles: list[str], offset: int, mt_verse: int) -> str:
    if not titles:
        return "（詩題）"
    title = "；".join(titles).strip()
    if offset == 1:
        return _wrap_title(title)
    # Psalm 51's official RCUV title combines the two MT title verses in the
    # reverse literary order.  Split only at the official semicolon and retain
    # the exact RCUV wording instead of inventing a new translation.
    if offset == 2 and "；" in title:
        first, second = [part.strip() for part in title.split("；", 1)]
        if mt_verse == 1:
            return _wrap_title(second)
        if mt_verse == 2:
            if not first.endswith(("。", "！", "？")):
                first += "。"
            return _wrap_title(first)
    return _wrap_title(title if mt_verse == offset else "詩題")


def translation_for_mt(
    index: Mapping[tuple[str, int, int], Mapping[str, Any]],
    book_name: str,
    chapter: int,
    verse: int,
    *,
    mt_psalm_counts: Mapping[int, int] | None = None,
) -> str:
    """Return the exact RCUV2010 text corresponding to one WLC/MT reference."""

    return translation_entry_for_mt(
        index,
        book_name,
        chapter,
        verse,
        mt_psalm_counts=mt_psalm_counts,
    )["text"]


def _translation_entry(
    record: Mapping[str, Any],
    book_name: str,
    chapter: int,
    *,
    text: str | None = None,
    superscription_included: bool = False,
) -> dict[str, Any]:
    start = int(record["verse"])
    end = int(record.get("verseEnd") or start)
    verse_range = str(start) if start == end else f"{start}-{end}"
    return {
        "text": str(text if text is not None else record.get("text") or ""),
        "translationVersionCode": RCUV_VERSION_CODE,
        "translationVariant": RCUV_VARIANT,
        "translationBook": book_name,
        "translationChapter": chapter,
        "translationVerse": start,
        "translationVerseEnd": end,
        "translationRef": f"{book_name}.{chapter}.{verse_range}",
        "translationRange": verse_range,
        "combinedVerseRange": start != end,
        "superscriptionIncluded": superscription_included,
        "sourceUrl": record.get("sourceUrl"),
        "responseSha256": record.get("responseSha256"),
    }


def translation_entry_for_mt(
    index: Mapping[tuple[str, int, int], Mapping[str, Any]],
    book_name: str,
    chapter: int,
    verse: int,
    *,
    mt_psalm_counts: Mapping[int, int] | None = None,
) -> dict[str, Any]:
    """Return RCUV text plus an explicit MT-to-RCUV range crosswalk."""

    if book_name == "Psalms":
        records = [
            record
            for (name, current_chapter, _), record in index.items()
            if name == book_name and current_chapter == chapter
        ]
        if not records:
            return {"text": ""}
        rcu_count = max(int(record["verseEnd"]) for record in records)
        mt_count = (mt_psalm_counts or {}).get(chapter)
        if mt_count is None:
            raise ValueError(f"missing MT verse count for Psalm {chapter}")
        offset = mt_count - rcu_count
        if offset not in {0, 1, 2}:
            raise ValueError(
                f"unsupported Psalm versification offset: Psalm {chapter} MT={mt_count} RCUV={rcu_count}"
            )
        if verse <= offset:
            titles = list(records[0].get("superscriptions") or [])
            title_text = _psalm_title_translation(titles, offset, verse)
            return {
                "text": title_text,
                "translationVersionCode": RCUV_VERSION_CODE,
                "translationVariant": RCUV_VARIANT,
                "translationBook": book_name,
                "translationChapter": chapter,
                "translationVerse": None,
                "translationVerseEnd": None,
                "translationRef": f"{book_name}.{chapter}.superscription.{verse}",
                "translationRange": "superscription",
                "combinedVerseRange": False,
                "superscriptionIncluded": True,
                "sourceUrl": records[0].get("sourceUrl"),
                "responseSha256": records[0].get("responseSha256"),
            }
        translated_verse = verse - offset
        record = index.get((book_name, chapter, translated_verse)) or {}
        if not record:
            return {"text": ""}
        text = str(record.get("text") or "")
        titles = list(record.get("superscriptions") or [])
        superscription_included = offset == 0 and verse == 1 and bool(titles)
        if superscription_included:
            text = _wrap_title("；".join(titles)) + text
        return _translation_entry(
            record,
            book_name,
            chapter,
            text=text,
            superscription_included=superscription_included,
        )

    # MT Isaiah 9:1–20 corresponds to RCUV Isaiah 9:2–21.
    if book_name == "Isaiah" and chapter == 9:
        verse += 1

    # MT Hosea 14:1 is RCUV 13:16; MT 14:2–10 is RCUV 14:1–9.
    if book_name == "Hosea" and chapter == 14:
        if verse == 1:
            record = index.get((book_name, 13, 16)) or {}
            return _translation_entry(record, book_name, 13) if record else {"text": ""}
        verse -= 1

    record = index.get((book_name, chapter, verse)) or {}
    return _translation_entry(record, book_name, chapter) if record else {"text": ""}
