"""Backfill scripture_ref for 龐 sermons by mapping sermon_date to the
(lectionary_year, season, week_num) slot and looking up Sunday readings
in pong_lectionary_weeks/days.

Calendar logic mirrors composables/useChurchCalendar.js:
  cycle = ((church_year - 2022) % 3 + 3) % 3 → 0:A, 1:B, 2:C
  church_year = year of the calendar year containing 將臨期第一主日 of the
  ecclesiastical year (so date 2024-02-11 → church_year 2023).

Output format: '經課一：X；啟應文：Y；經課二：Z；福音書：W' per existing convention.

Usage:
    python backfill_scripture_ref.py dryrun
    python backfill_scripture_ref.py apply
"""
from __future__ import annotations

import os
import sys
import argparse
from datetime import date, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from standardize_sermon import patch_sermon

URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TOKEN = os.environ["SUPABASE_ACCESS_TOKEN"]
REF = URL.split("//", 1)[1].split(".", 1)[0]


def _query(sql: str):
    r = requests.post(
        f"https://api.supabase.com/v1/projects/{REF}/database/query",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"query": sql},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


# ─── Church calendar (port of useChurchCalendar.js) ──────────────────────
def easter_date(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) // 451
    month = (h + L - 7 * m + 114) // 31
    day = ((h + L - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def prev_sunday(d: date) -> date:
    """Sunday on or before d (Sunday=6 in Python's weekday())."""
    # Python: Mon=0, ..., Sun=6 → we want Sun=0 alignment
    # JS getDay(): Sun=0, Mon=1, ..., Sat=6
    # Convert: js_getDay = (d.weekday() + 1) % 7
    js_dow = (d.weekday() + 1) % 7
    return d - timedelta(days=js_dow)


def next_sunday(d: date) -> date:
    js_dow = (d.weekday() + 1) % 7
    return d + timedelta(days=(7 - js_dow) % 7)


def get_current_church_year(d: date) -> int:
    """The year whose Advent 1 begins this ecclesiastical year."""
    christmas = date(d.year, 12, 25)
    advent1 = prev_sunday(christmas - timedelta(days=1)) - timedelta(days=21)
    return d.year if d >= advent1 else d.year - 1


def get_lectionary_year_en(church_year: int) -> str:
    return ["A", "B", "C"][((church_year - 2022) % 3 + 3) % 3]


def get_church_year_sundays(church_year: int) -> list[dict]:
    """Returns ordered list of {sunday, season, week_num, label} for the year."""
    christmas = date(church_year, 12, 25)
    advent1 = prev_sunday(christmas - timedelta(days=1)) - timedelta(days=21)
    christmas2 = date(church_year + 1, 12, 25)
    next_advent1 = prev_sunday(christmas2 - timedelta(days=1)) - timedelta(days=21)

    easter = easter_date(church_year + 1)
    ash_wed = easter - timedelta(days=46)
    lent1 = next_sunday(ash_wed + timedelta(days=1))
    pentecost = easter + timedelta(days=49)
    trinity = pentecost + timedelta(days=7)

    slots: list[dict] = []

    # Advent 1-4
    for w in range(1, 5):
        slots.append({"season": "advent", "week_num": w,
                      "sunday": advent1 + timedelta(days=(w - 1) * 7)})

    # Christmas weeks 1, 2 (latter optional)
    epiphany_day = date(church_year + 1, 1, 6)
    cs1 = next_sunday(christmas + timedelta(days=1))
    cs2 = cs1 + timedelta(days=7)
    slots.append({"season": "christmas", "week_num": 1, "sunday": cs1})
    slots.append({"season": "christmas", "week_num": 2,
                  "sunday": cs2 if cs2 < epiphany_day else None})

    # Epiphany 1-9 (some optional based on Lent start)
    epiphany1 = next_sunday(epiphany_day + timedelta(days=1))
    for w in range(1, 10):
        sun = epiphany1 + timedelta(days=(w - 1) * 7)
        slots.append({"season": "epiphany", "week_num": w,
                      "sunday": sun if sun < lent1 else None})

    # Lent 1-6
    for w in range(1, 7):
        slots.append({"season": "lent", "week_num": w,
                      "sunday": lent1 + timedelta(days=(w - 1) * 7)})

    # Easter 1-7
    for w in range(1, 8):
        slots.append({"season": "easter", "week_num": w,
                      "sunday": easter + timedelta(days=(w - 1) * 7)})

    # Pentecost (Proper) 1-29
    proper_start = [
        (4, 24), (4, 29), (5, 5),  (5, 12), (5, 19), (5, 26),
        (6, 2),  (6, 9),  (6, 16), (6, 23), (6, 30), (7, 7),
        (7, 14), (7, 21), (7, 28), (8, 4),  (8, 11), (8, 18),
        (8, 25), (9, 1),  (9, 8),  (9, 15), (9, 22), (9, 29),
        (10, 6), (10, 13), (10, 20), (10, 27), (11, 20),
    ]
    yr2 = church_year + 1
    for p in range(1, 30):
        mo, dy = proper_start[p - 1]
        sun = next_sunday(date(yr2, mo, dy))
        avail = trinity <= sun < next_advent1
        slots.append({"season": "pentecost", "week_num": p,
                      "sunday": sun if avail else None})

    return slots


def find_slot(d: date) -> tuple[str, str, int] | None:
    """Returns (lectionary_year, season, week_num) for sermon_date d, or None."""
    church_year = get_current_church_year(d)
    cycle = get_lectionary_year_en(church_year)
    slots = [s for s in get_church_year_sundays(church_year) if s["sunday"]]
    slots.sort(key=lambda s: s["sunday"])

    # Find slot whose sunday ≤ d < next slot's sunday
    for i, s in enumerate(slots):
        end = slots[i + 1]["sunday"] if i + 1 < len(slots) else (s["sunday"] + timedelta(days=7))
        if s["sunday"] <= d < end:
            return cycle, s["season"], s["week_num"]
    return None


# ─── Lectionary lookup ───────────────────────────────────────────────────
_READINGS_CACHE: dict[tuple[str, str, int], list[dict] | None] = {}


def fetch_sunday_readings(cycle: str, season: str, week_num: int) -> list[dict] | None:
    key = (cycle, season, week_num)
    if key in _READINGS_CACHE:
        return _READINGS_CACHE[key]
    rows = _query(
        f"""
        SELECT d.readings
        FROM pong_lectionary_weeks w
        JOIN pong_lectionary_days d ON d.week_id = w.id
        WHERE w.lectionary_year = '{cycle}'
          AND w.season = '{season}'
          AND w.week_num = {week_num}
          AND d.day_of_week = 0
        LIMIT 1
        """
    )
    val = rows[0]["readings"] if rows else None
    _READINGS_CACHE[key] = val
    return val


# Slot labels matching pong's existing format ("經課一/啟應文/經課二/福音書").
# Ordering convention: [OT first, Psalm, NT epistle, Gospel].
SLOT_LABELS = ["經課一", "啟應文", "經課二", "福音書"]


def format_scripture_ref(readings: list[dict]) -> str:
    parts = []
    for slot, r in zip(SLOT_LABELS, readings):
        book = r.get("book", "")
        passage = r.get("passage", "")
        if book and passage:
            parts.append(f"{slot}：{book} {passage}")
    return "；".join(parts)


# ─── Driver ──────────────────────────────────────────────────────────────
def fetch_targets():
    return _query(
        "SELECT id, sermon_date "
        "FROM pong_sermons "
        "WHERE preacher LIKE '%龐%' "
        "  AND (scripture_ref IS NULL OR scripture_ref = '') "
        "ORDER BY sermon_date"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["dryrun", "apply"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--show-misses", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    rows = fetch_targets()
    if args.limit:
        rows = rows[: args.limit]

    n_match = n_no_slot = n_no_readings = 0
    for row in rows:
        d = date.fromisoformat(row["sermon_date"])
        slot = find_slot(d)
        if not slot:
            n_no_slot += 1
            if args.show_misses:
                print(f"× {row['id']} {d}  no slot found")
            continue
        cycle, season, week_num = slot
        readings = fetch_sunday_readings(cycle, season, week_num)
        if not readings:
            n_no_readings += 1
            if args.show_misses:
                print(f"× {row['id']} {d}  ({cycle}/{season}/wk{week_num}) → no readings in DB")
            continue
        ref = format_scripture_ref(readings)
        if not ref:
            n_no_readings += 1
            continue
        n_match += 1
        print(f"+ {row['id']} {d}  ({cycle}/{season}/wk{week_num}) → {ref}")
        if args.mode == "apply":
            patch_sermon(row["id"], {"scripture_ref": ref})

    print()
    print(f"# total {len(rows)}  matched {n_match}  no_slot {n_no_slot}  no_readings {n_no_readings}")


if __name__ == "__main__":
    main()
