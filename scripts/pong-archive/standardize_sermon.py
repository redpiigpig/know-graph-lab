"""Standardize 龐君華 sermon content + metadata to the canonical format
expected by `pages/pong-archive/sermons/[year].vue` renderer.

Functions are pure and idempotent — running twice yields the same output.

Usage:
  from standardize_sermon import (
      derive_preacher_title, derive_preacher_full,
      derive_liturgical_season, strip_markdown,
      ensure_speaker_label, regroup_short_paragraphs,
      derive_occasion, standardize_content,
  )
"""
from __future__ import annotations

import os
import re
import sys
import json
import argparse
from datetime import date as _date

import requests
from dotenv import load_dotenv

load_dotenv()


# ─── Preacher title era map ───────────────────────────────────────────────
TITLE_TRANSITION = _date(2019, 5, 1)


def derive_preacher_title(d: _date) -> str:
    """牧師 (pre-2019-05) → 會督 (2019-05+, permanent including post-retirement)."""
    return "牧師" if d < TITLE_TRANSITION else "會督"


def derive_preacher_full(d: _date) -> str:
    return f"龐君華{derive_preacher_title(d)}"


# ─── Liturgical season (date-based, approximate) ──────────────────────────
def derive_liturgical_season(d: _date) -> str | None:
    """Returns the liturgical season tag used by the frontend for color coding.

    Approximate — Lent/Easter/Pentecost are date-dependent and we leave None
    so callers can keep an existing value rather than overwriting with a guess.
    """
    m, day = d.month, d.day
    if (m, day) >= (12, 25) or m == 1 and day <= 5:
        return "christmas"
    if m == 12:
        return "advent"
    if m == 1 and day >= 6:
        return "epiphany"
    if m == 2:
        return "epiphany"
    return None  # leave existing


# ─── Markdown stripping ───────────────────────────────────────────────────
_MD_HEAD = re.compile(r"^#{1,6}\s+(.+?)\s*$")
_MD_HR = re.compile(r"^---+\s*$")
_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def strip_markdown(content: str) -> str:
    """Convert markdown headings → 【X】, drop horizontal rules, strip emphasis/links."""
    out = []
    for line in content.split("\n"):
        if _MD_HR.match(line):
            continue
        m = _MD_HEAD.match(line)
        if m:
            out.append(f"【{m.group(1).strip()}】")
            continue
        line = _MD_BOLD.sub(r"\1", line)
        line = _MD_ITALIC.sub(r"\1", line)
        line = _MD_LINK.sub(r"\1", line)
        out.append(line)
    return "\n".join(out)


# ─── Speaker label ────────────────────────────────────────────────────────
_SPEAKER_RE = re.compile(r"^.{1,8}：")


def ensure_speaker_label(content: str, sermon_date: str | _date) -> str:
    if isinstance(sermon_date, str):
        d = _date.fromisoformat(sermon_date)
    else:
        d = sermon_date
    label = derive_preacher_full(d) + "："
    stripped = content.lstrip("\n").lstrip()
    first_line = stripped.split("\n", 1)[0].rstrip()
    if _SPEAKER_RE.match(first_line):
        return content
    return f"{label}\n\n{stripped}"


# ─── Paragraph regrouping ─────────────────────────────────────────────────
_SHIFT = re.compile(r"^(所以|今天|另一方面|但是|於是|我們看到|那麼|因此|然後|最後|首先|其次|第二|第三|因為|然而)")
_SPECIAL = re.compile(r"^[【（(].")  # section heading or stage direction


def regroup_short_paragraphs(content: str, target_min: int = 200, target_max: int = 600) -> str:
    """Merge consecutive short prose paragraphs until ~target_min..target_max chars.

    Preserves boundaries at:
      • speaker labels (xx：)
      • section headings 【…】
      • stage directions （…）
    Splits when next paragraph starts with a topical-shift marker.
    Idempotent: long paragraphs pass through unchanged.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    if len(paras) <= 1:
        return content

    out = []
    buf: list[str] = []

    def is_special(p: str) -> bool:
        return bool(_SPECIAL.match(p) or _SPEAKER_RE.match(p))

    def flush():
        if buf:
            out.append("".join(buf))
            buf.clear()

    for p in paras:
        if is_special(p):
            flush()
            out.append(p)
            continue
        if not buf:
            buf.append(p)
            continue
        joined_len = sum(len(x) for x in buf)
        if (_SHIFT.match(p) and joined_len >= target_min) or joined_len + len(p) > target_max:
            flush()
            buf.append(p)
        else:
            buf.append(p)
    flush()
    return "\n\n".join(out)


# ─── Occasion derivation from sermon body ────────────────────────────────
# Numerals in occasion ordinals (e.g., 第二十一個主日)
_NUM = r"[一二三四五六七八九十百零兩０-９0-9]+"

# Each pattern captures the full occasion phrase. They are ordered from most
# specific (named main feasts) to general (generic season + ordinal main 主日).
_OCC_PATTERNS = [
    # Named main feasts / fixed-point occasions
    re.compile(r"((?:基督)?復活主日)"),
    re.compile(r"((?:基督)?受難(?:日|節))"),
    re.compile(r"(復活前夕)"),
    re.compile(r"(棕枝主日|棕樹主日)"),
    re.compile(r"((?:聖)?三一(?:的)?主日|聖三一(?:的)?主日)"),
    re.compile(r"(善牧主日)"),
    re.compile(r"(基督登山變(?:像|相)主日)"),
    re.compile(r"((?:基督|宇宙)?(?:君王|王權)主日|基督是王主日)"),
    re.compile(r"(聖灰(?:禮拜三|日))"),
    re.compile(r"(諸聖(?:日|節|主日))"),
    re.compile(r"(聖週(?:[一二三四五六日]))"),
    re.compile(r"(聖誕(?:節|主日|前夕))"),
    re.compile(r"(主受洗(?:日|主日)|耶穌受洗主日)"),
    re.compile(r"(基督升天(?:的)?主日|升天(?:主日|日|節))"),
    re.compile(r"(聖靈降臨(?:的)?主日)"),
    re.compile(r"(立約(?:主日|崇拜|禮拜))"),
    re.compile(r"(顯現(?:日|節))(?![後之])"),
    re.compile(r"(感恩(?:節|主日))"),
    re.compile(r"(聖靈降臨(?:節|日))(?![之後期])"),
    # Season + ordinal patterns (allow 期/節/日 stem and optional 之後/的)
    re.compile(rf"(顯現(?:期|節|日)(?:期)?(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(大齋[期祭](?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(復活(?:期|節)(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(聖靈降臨(?:節|期)(?:期)?(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(將臨期(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(降臨期(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(常年期(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(聖誕(?:節|主日)(?:之?後)?(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    # Allow 中的 / 中 / 中第 between season and ordinal (e.g. 復活期中的第四個主日)
    re.compile(rf"(復活(?:期|節)中(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(顯現(?:期|節|日)中(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(聖靈降臨(?:節|期)中(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    re.compile(rf"(大齋[期祭]中(?:的)?(?:第|的第)?{_NUM}個?主日)"),
    # Last/最後 variants
    re.compile(r"(顯現(?:期|節|日)(?:期)?(?:之?後)?(?:的)?最後(?:一)?個?主日)"),
    re.compile(r"(聖靈降臨(?:節|期)(?:期)?(?:之?後)?(?:的)?最後(?:一)?個?主日)"),
    re.compile(r"(大齋[期祭](?:的)?最後(?:一)?個?主日)"),
    re.compile(r"(復活(?:期|節)(?:的)?最後(?:一)?個?主日)"),
    re.compile(r"(將臨期(?:的)?最後(?:一)?個?主日)"),
]

# Variants → canonical (e.g. "複活" / 大齋祭 typos)
_OCC_CANON = [
    (re.compile(r"大齋祭"), "大齋期"),
    (re.compile(r"基督登山變相"), "基督登山變像"),
    (re.compile(r"棕樹主日"), "棕枝主日"),
]


_TODAY_CUES = re.compile(r"今天")


def derive_occasion(content: str) -> str | None:
    """Best-effort extraction of the liturgical occasion from the opening prose.

    Strategy: find each `今天` in the first 1500 chars. Within 80 chars after
    each cue, try every pattern; pick the FIRST match. Falls back to bare
    earliest match (no cue) only if no cued match is found, since standalone
    matches risk false positives ("復活節快到了" in a non-復活期 sermon).
    """
    if not content:
        return None
    head = content[:1500]

    def _try_match(window: str) -> str | None:
        # Collect all matches; pick (earliest start, then longest length)
        hits: list[tuple[int, int, str]] = []
        for pat in _OCC_PATTERNS:
            for m in pat.finditer(window):
                hits.append((m.start(), -len(m.group(1)), m.group(1)))
        if not hits:
            return None
        hits.sort()
        return hits[0][2]

    # Pass 1: anchored to 今天 — short window so we don't drag in unrelated mentions
    for cue in _TODAY_CUES.finditer(head):
        window = head[cue.start(): cue.start() + 60]
        cand = _try_match(window)
        if cand:
            for pat, repl in _OCC_CANON:
                cand = pat.sub(repl, cand)
            return cand.strip()

    # Pass 2: fallback — search whole head, but be conservative
    cand = _try_match(head)
    if cand:
        for pat, repl in _OCC_CANON:
            cand = pat.sub(repl, cand)
        return cand.strip()
    return None


# ─── Combined content standardization ─────────────────────────────────────
def standardize_content(content: str | None, sermon_date: str | _date,
                        do_regroup: bool = True) -> str | None:
    if not content:
        return content
    out = strip_markdown(content)
    out = ensure_speaker_label(out, sermon_date)
    if do_regroup:
        avg = _avg_para_len(out)
        if avg < 150:
            out = regroup_short_paragraphs(out)
    out = re.sub(r"\n{3,}", "\n\n", out).rstrip() + "\n"
    return out


def _avg_para_len(content: str) -> float:
    paras = [p for p in re.split(r"\n\s*\n", content) if p.strip()]
    if not paras:
        return 0.0
    return sum(len(p) for p in paras) / len(paras)


# ─── Supabase helpers ─────────────────────────────────────────────────────
def _env() -> tuple[str, str]:
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return url, key


def fetch_sermon(sermon_id: int) -> dict | None:
    url, key = _env()
    r = requests.get(
        f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}&select=*",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=30,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def fetch_sermons_by_ids(ids: list[int]) -> list[dict]:
    url, key = _env()
    in_clause = ",".join(str(i) for i in ids)
    r = requests.get(
        f"{url}/rest/v1/pong_sermons?id=in.({in_clause})&select=*&order=sermon_date",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def patch_sermon(sermon_id: int, patch: dict) -> None:
    url, key = _env()
    r = requests.patch(
        f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        json=patch,
        timeout=30,
    )
    r.raise_for_status()


def patch_media_transcript(media_id: int, transcript: str) -> None:
    url, key = _env()
    r = requests.patch(
        f"{url}/rest/v1/pong_media?id=eq.{media_id}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        json={"transcript": transcript},
        timeout=30,
    )
    r.raise_for_status()


# ─── CLI dry-run / apply ──────────────────────────────────────────────────
def _diff_summary(old: str | None, new: str | None) -> str:
    if old is None or new is None:
        return f"None→{'set' if new else 'None'}"
    if old == new:
        return "no change"
    return f"len {len(old)}→{len(new)}, head {(new or '')[:30]!r}"


def cmd_dryrun(args):
    ids = [int(x) for x in args.ids.split(",")] if args.ids else None
    if args.preset == "missing_label":
        ids = _ids_missing_speaker_label()
    if not ids:
        print("no ids supplied", file=sys.stderr)
        sys.exit(1)
    rows = fetch_sermons_by_ids(ids)
    print(f"# dry-run: {len(rows)} rows")
    for row in rows:
        date_iso = row["sermon_date"]
        old_content = row.get("content") or ""
        new_content = standardize_content(old_content, date_iso,
                                          do_regroup=args.regroup)
        new_preacher = derive_preacher_full(_date.fromisoformat(date_iso))
        ok = "·"
        if not old_content.strip():
            print(f"{ok} {row['id']} {date_iso}  EMPTY content — skip")
            continue
        print(f"{ok} {row['id']} {date_iso}  {_diff_summary(old_content, new_content)}")
        if args.show_head:
            print(f"   OLD head: {old_content[:80]!r}")
            print(f"   NEW head: {(new_content or '')[:80]!r}")
        if row.get("preacher") != new_preacher:
            print(f"   preacher: {row.get('preacher')!r} → {new_preacher!r}")


def cmd_apply(args):
    ids = [int(x) for x in args.ids.split(",")] if args.ids else None
    if args.preset == "missing_label":
        ids = _ids_missing_speaker_label()
    if not ids:
        print("no ids supplied", file=sys.stderr)
        sys.exit(1)
    rows = fetch_sermons_by_ids(ids)
    n_changed = 0
    for row in rows:
        date_iso = row["sermon_date"]
        old_content = row.get("content") or ""
        if not old_content.strip():
            print(f"skip {row['id']} (empty)")
            continue
        new_content = standardize_content(old_content, date_iso,
                                          do_regroup=args.regroup)
        new_preacher = derive_preacher_full(_date.fromisoformat(date_iso))
        patch = {}
        if new_content and new_content != old_content:
            patch["content"] = new_content
        if row.get("preacher") != new_preacher:
            patch["preacher"] = new_preacher
        if not patch:
            print(f"= {row['id']} {date_iso}  no change")
            continue
        patch_sermon(row["id"], patch)
        if "content" in patch and row.get("media_id"):
            patch_media_transcript(row["media_id"], new_content)
        n_changed += 1
        print(f"✓ {row['id']} {date_iso}  patched: {list(patch.keys())}")
    print(f"# done: {n_changed}/{len(rows)} rows updated")


def _ids_missing_speaker_label() -> list[int]:
    """Use the management API to fetch the list of pong sermons with no speaker label."""
    token = os.environ["SUPABASE_ACCESS_TOKEN"]
    ref = os.environ.get("SUPABASE_PROJECT_REF") or _ref_from_url(os.environ["SUPABASE_URL"])
    sql = (
        "SELECT id FROM pong_sermons "
        "WHERE preacher LIKE '%龐%' AND content IS NOT NULL "
        "AND length(content) > 0 AND content !~ '^.{1,8}：' "
        "ORDER BY sermon_date"
    )
    r = requests.post(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"query": sql},
        timeout=30,
    )
    r.raise_for_status()
    return [row["id"] for row in r.json()]


def _ref_from_url(url: str) -> str:
    return url.split("//", 1)[1].split(".", 1)[0]


def main():
    ap = argparse.ArgumentParser(description="Standardize 龐 sermon format")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_dry = sub.add_parser("dryrun", help="show diffs without writing")
    p_dry.add_argument("--ids", help="comma-separated sermon ids")
    p_dry.add_argument("--preset", choices=["missing_label"], help="canned id list")
    p_dry.add_argument("--regroup", action="store_true", help="also try paragraph regrouping")
    p_dry.add_argument("--show-head", action="store_true")
    p_dry.set_defaults(func=cmd_dryrun)

    p_app = sub.add_parser("apply", help="write changes to DB")
    p_app.add_argument("--ids", help="comma-separated sermon ids")
    p_app.add_argument("--preset", choices=["missing_label"], help="canned id list")
    p_app.add_argument("--regroup", action="store_true")
    p_app.set_defaults(func=cmd_apply)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
