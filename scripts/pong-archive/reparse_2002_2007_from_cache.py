#!/usr/bin/env python3
"""
reparse_2002_2007_from_cache.py
================================
Round 2: re-parse all 38 龐 2002-2007 sermons from cached fhl HTML
(`tmp_fhl/html_cache/sermonNNN.html`) using a structure-aware parser.

Splits the cached HTML into:
  1. <center>…</center>  — metadata block (occasion / 講題 / 經課 / 整理 / 講道)
  2. body                  — the sermon prose, with named section headers wrapped 【】
  3. footer                — fhl page nav (stripped: 前期索引/Copyright/回首頁/etc.)

Writes:
  - pong_sermons.title          = 講題 (no 節期 prefix)
  - pong_sermons.occasion       = 節期 phrase  (e.g. 「棕樹主日」)
  - pong_sermons.scripture_ref  = 經課 list, separators normalized to ；
  - pong_sermons.content        = "龐君華牧師：\n\n{body}\n"
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
INDEX_FILE = ROOT / "tmp_fhl" / "index.json"
HTML_CACHE_DIR = ROOT / "tmp_fhl" / "html_cache"
LOG_FILE = ROOT / "tmp_fhl" / "reparse_2002_2007_log.txt"


# ─── Supabase ────────────────────────────────────────────────────────────────


def _sb_url() -> str:
    return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"


def _sb_headers(write: bool = False) -> dict:
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    if write:
        h["Content-Type"] = "application/json"
        h["Prefer"] = "return=representation"
    return h


def fetch_rows() -> list[dict]:
    r = requests.get(
        f"{_sb_url()}/pong_sermons",
        headers=_sb_headers(),
        params={
            "select": "id,sermon_date,title,preacher,occasion,scripture_ref,content,media_id",
            "preacher": "eq.龐君華牧師",
            "sermon_date": "gte.2002-01-01",
            "and": "(sermon_date.lte.2007-12-31)",
            "order": "sermon_date.asc",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def patch_sermon(sermon_id: int, payload: dict) -> None:
    r = requests.patch(
        f"{_sb_url()}/pong_sermons?id=eq.{sermon_id}",
        headers=_sb_headers(write=True),
        json=payload,
        timeout=30,
    )
    if r.status_code not in (200, 204):
        raise RuntimeError(f"PATCH sermon {sermon_id} HTTP {r.status_code}: {r.text[:300]}")


# ─── HTML helpers ────────────────────────────────────────────────────────────


def html_to_text(html: str) -> str:
    """Convert paragraph HTML to plain text, preserving paragraph breaks."""
    s = html
    s = re.sub(r"<p[^>]*>", "\n\n", s, flags=re.I)
    s = re.sub(r"</p>", "", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = (s
         .replace("&nbsp;", "")
         .replace("&amp;", "&")
         .replace("&lt;", "<")
         .replace("&gt;", ">")
         .replace("&quot;", '"'))
    # Trim leading 全形空格 from each line
    s = "\n".join(ln.lstrip("　 \t") for ln in s.split("\n"))
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def slice_metadata_and_body(html_text: str) -> tuple[str, str]:
    """
    Cut the page into (metadata_html, body_html) at </center>.

    Falls back to the whole body region if no <center> block is found.
    """
    # Find the inner-most <center> block (some pages nest)
    # Strategy: find first <center> after author info, take up until first </center>.
    m_open = re.search(r"<center\b[^>]*>", html_text, re.I)
    if not m_open:
        return "", html_text
    m_close = re.search(r"</center>", html_text[m_open.end():], re.I)
    if not m_close:
        return "", html_text
    metadata_html = html_text[m_open.end(): m_open.end() + m_close.start()]
    body_html = html_text[m_open.end() + m_close.end():]
    return metadata_html, body_html


def strip_footer(body_text: str) -> str:
    """Drop fhl navigation/footer lines from end of body."""
    # Cut at first occurrence of any footer marker
    markers = [
        "前期索引",
        "上一則",
        "下一則",
        "寄給朋友",
        "【回應文章】",
        "Copyright",
        "All Rights Shared",
        "回首頁",
        "wf.fhl.net",
    ]
    cut = len(body_text)
    for mk in markers:
        idx = body_text.find(mk)
        if 0 <= idx < cut:
            cut = idx
    body_text = body_text[:cut]
    # Also drop date stamps in 【...】 form (e.g. 【2002-3-24 城中牧區】)
    body_text = re.sub(r"【[^】]*】", "", body_text)
    return body_text.rstrip()


# ─── Metadata extraction ─────────────────────────────────────────────────────

OCCASION_PATTERNS = [
    r"棕樹主日",
    r"棕枝主日",
    r"復活節後第[一二三四五六七八九十廿]+(?:個)?主日",
    r"復活節期第[一二三四五六七八九十廿]+(?:個)?主日",
    r"復活期第[一二三四五六七八九十廿]+(?:個)?主日",
    r"復活節第[一二三四五六七八九十廿]+(?:個)?主日",
    r"復活第[一二三四五六七八九十廿]+主日",
    r"復活主日",
    r"聖誕節後第[一二三四五六七八九十廿]+(?:個)?主日(?:\s*\(?聖家主日\)?)?",
    r"聖誕主日",
    r"聖家主日",
    r"將臨[節期]期?第[一二三四五六七八九十廿]+(?:個)?主日",
    r"將臨節期第[一二三四五六七八九十廿]+(?:個)?主日",
    r"將臨期第[一二三四五六七八九十廿]+(?:個)?主日",
    r"大齋期第[一二三四五六七八九十廿]+(?:個)?主日",
    r"四旬節\(?大齋期\)?第[一二三四五六七八九十廿]+主日",
    r"顯現節期最後主日",
    r"顯現節後第[一二三四五六七八九十廿]+(?:個)?主日",
    r"顯現節第[一二三四五六七八九十廿]+主日",
    r"顯現節",
    r"基督變相主日",
    r"基督普世君王主日",
    r"基督君王主日",
    r"基督為王主日",
    r"基督升天主日",
    r"聖三一主日",
    r"聖靈降臨節後第[一二三四五六七八九十廿]+(?:個)?主日",
    r"聖靈降臨節第[一二三四五六七八九十廿]+(?:個)?主日",
    r"聖靈降臨節?後第[一二三四五六七八九十廿]+(?:個)?主日",
    r"聖靈降臨節後第十[一二三四五六七八九]主日",
    r"聖靈降臨節後第二十[一二三四五六七八九]?主日",
    r"聖靈降臨節",
    r"立約主日",
]
OCC_RE = re.compile("|".join(f"(?:{p})" for p in OCCASION_PATTERNS))

TITLE_RE = re.compile(r"(?:講題|證道主題|主題)\s*[：:]\s*(.+?)(?=\s*(?:經課|證道|整理|講道|講員|前言|引言|$))")
SCRIP_RE = re.compile(r"經課\s*[：:]\s*(.+?)(?=\s*(?:整理|講道|講員|證道|前言|引言|$))")


BIBLE_BOOKS_ALT = (
    r"以賽亞書|耶利米書|耶利米哀歌|以西結書|但以理書|何西阿書|約珥書|阿摩司書|"
    r"俄巴底亞書|約拿書|彌迦書|那鴻書|哈巴谷書|西番雅書|哈該書|撒迦利亞書|瑪拉基書|"
    r"創世記|出埃及記|利未記|民數記|申命記|約書亞記|士師記|路得記|"
    r"撒母耳記[上下]|列王紀[上下]|歷代志[上下]|以斯拉記|尼希米記|以斯帖記|"
    r"約伯記|詩篇|箴言|傳道書|雅歌|"
    r"馬太福音|馬可福音|路加福音|約翰福音|使徒行傳|"
    r"羅馬書|哥林多前書|哥林多後書|加拉太書|以弗所書|腓立比書|歌羅西書|"
    r"帖撒羅尼迦前書|帖撒羅尼迦後書|提摩太前書|提摩太後書|提多書|腓利門書|"
    r"希伯來書|雅各書|彼得前書|彼得後書|約翰一書|約翰二書|約翰三書|猶大書|啟示錄"
)
BIBLE_BOOKS_RE = re.compile(rf"^({BIBLE_BOOKS_ALT})\s*[\d:：~∼\-,，、]")
BIBLE_BOOK_PREFIX_RE = re.compile(rf"({BIBLE_BOOKS_ALT})")


def normalize_scripture(s: str) -> str:
    s = s.strip()
    # Replace , 、 with ；
    s = re.sub(r"[、，]\s*", "；", s)
    # Insert ； before a bible-book name that is directly preceded by a digit/end-marker
    # e.g. "以弗所書4：1~16約翰福音 6：24~35" → "以弗所書4：1~16；約翰福音 6：24~35"
    s = re.sub(rf"(?<=[\d下上])({BIBLE_BOOKS_ALT})", r"；\1", s)
    s = re.sub(r"；\s*；+", "；", s)
    s = s.rstrip("；").strip()
    return s


def extract_metadata(meta_text: str) -> dict:
    md = {}
    occ_m = OCC_RE.search(meta_text)
    if occ_m:
        md["occasion"] = occ_m.group(0).strip()
    title_m = TITLE_RE.search(meta_text)
    if title_m:
        md["title"] = title_m.group(1).strip().rstrip("：:")
    scrip_m = SCRIP_RE.search(meta_text)
    if scrip_m:
        md["scripture_ref"] = normalize_scripture(scrip_m.group(1))
    return md


def cleanup_title(title: str, occasion: str | None) -> tuple[str, str | None]:
    """Strip 節期 prefix, 講章/崇拜 noise, leading separators from a title.

    Returns (cleaned_title, derived_occasion). derived_occasion is set if the
    leading 節期 prefix was extracted from the title and `occasion` was None.
    """
    if not title:
        return title, occasion
    t = title.strip()
    derived_occ = None
    # If existing occasion known, strip it as prefix
    if occasion:
        pat = rf"^[\s　]*{re.escape(occasion)}[\s　]*[-－—]*[\s　]*"
        t2 = re.sub(pat, "", t)
        if t2 != t:
            t = t2
    # Strip generic 節期 prefix and capture as occasion
    occ_pat = re.compile(r"^[\s　]*(" + "|".join(OCCASION_PATTERNS) + r")[\s　]*[-－—]*[\s　]*")
    m = occ_pat.match(t)
    if m:
        derived_occ = m.group(1)
        t = t[m.end():]
    # Strip 崇拜/講章/證道主題/etc. document-type tokens
    t = re.sub(r"^[\s　]*(崇拜講章|證道講章|證道主題|證道主旨|證道|講章|崇拜|主題)[\s：:　]*", "", t)
    # Strip ALL leading separators (multiple dashes / colons / whitespace)
    t = re.sub(r"^[\s　\-－—:：]+", "", t)
    return t.strip(), (derived_occ if not occasion else occasion)


# ─── Body header wrapping ────────────────────────────────────────────────────

# Strict structural headers — unambiguous sermon section markers (safe to split
# mid-line / wrap as 【…】). Words like 應用/反省/回應 are common Chinese verbs
# and must never trigger auto-splitting.
STRICT_HEADERS = ["前言", "引言", "緒言", "起頭", "開場", "起首",
                  "結語", "結論", "結束", "結尾"]
# Wrap-as-header when the line is JUST that word (allows broader list)
ALL_HEADERS = STRICT_HEADERS + ["應用", "反省", "回應", "主題", "結論",
                                "默想", "禱告"]
HDR_PREFIX_RE = re.compile(r"^(" + "|".join(STRICT_HEADERS) + r")(?=[^\s])")
NAMED_HEADERS = STRICT_HEADERS  # back-compat alias


def wrap_named_headers(body: str) -> str:
    """Wrap section headers in 【…】. Two cases:
    - Paragraph that IS just a header word (broader ALL_HEADERS list).
    - Paragraph starting with STRICT_HEADERS prefix glued to body — split.
    Verb-y words like 應用/反省/回應 are NOT split mid-paragraph (false positives).
    """
    out_paras = []
    for p in re.split(r"\n\s*\n", body):
        s = p.strip()
        if not s:
            continue
        # Standalone header line
        if s in ALL_HEADERS:
            out_paras.append(f"【{s}】")
            continue
        # Strict-header glued at start of paragraph
        m = HDR_PREFIX_RE.match(s)
        if m:
            hdr = m.group(1)
            rest = s[m.end():].lstrip()
            out_paras.append(f"【{hdr}】")
            if rest:
                out_paras.append(rest)
            continue
        out_paras.append(s)
    return "\n\n".join(out_paras)


# ─── Core parser ─────────────────────────────────────────────────────────────


META_MARKERS = ("經課", "整理", "講題", "證道主題", "講道", "講員", "證道", "主題", "作者")
NOISE_LINE_RE = re.compile(r"^(作者|整理|講道|講員|證道|司會|司琴|讀經|啟應)\s*[：:]")
# Capture group stops at first sentence punctuation or end of line; max 50 chars
SCRIP_LINE_RE = re.compile(r"^經課\s*[：:]\s*([^\r\n。！？]{1,200})$")
TITLE_LINE_RE = re.compile(r"^(?:講題|證道主題|主題)\s*[：:]\s*([^\r\n。！？]{1,50})$")
DATE_LINE_RE = re.compile(r"^\d{4}[.\-/年]\s*\d{1,2}[.\-/月]\s*\d{1,2}[日]?\s*$")
LOCATION_LINE_RE = re.compile(r"^(城中(牧區|教會)|衛理公會|衛理城中|信義會)[\s　]*$")
BARE_NOISE_LINES = {"證道", "講章", "崇拜", "崇拜講章", "證道講章", "講章內容", "證道主題"}


def split_glued_markers(text: str) -> str:
    """Insert newlines before metadata markers and STRICT section headers
    when they're glued to the previous text without a break.

    Only STRICT_HEADERS (前言/結語/etc) are split — never verb-headers.
    Mid-line splitting only triggers immediately after a sentence terminator
    (。！？) to reduce false positives.
    """
    # Metadata markers (insert \n before)
    for mk in META_MARKERS:
        text = re.sub(rf"(?<=[^\s\n]){re.escape(mk)}(?=\s*[：:])", f"\n{mk}", text)
    # Strict headers: at line start glued to body → split
    for hdr in STRICT_HEADERS:
        text = re.sub(rf"(^|\n){hdr}(?=[^\s\n])", rf"\1{hdr}\n\n", text)
    # Strict headers: after sentence terminator → split
    for hdr in STRICT_HEADERS:
        text = re.sub(rf"(?<=[。！？]){hdr}(?=[^\s\n])", f"\n\n{hdr}\n\n", text)
    return text


def parse_html(html_bytes: bytes) -> tuple[dict, str]:
    """Return (metadata_dict, body_text).

    Strategy: strip all HTML, work on flat text. Cut at footer markers.
    Insert linebreaks before glued metadata/header markers. Classify each
    line as occasion/title/scripture/noise/section-header/body.
    """
    text = html_bytes.decode("big5", errors="replace")

    # Drop noise tags
    text = re.sub(r"<head\b.*?</head>", "", text, flags=re.S | re.I)
    text = re.sub(r"<script\b.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", "", text, flags=re.S | re.I)
    # Discard everything from <body> start? Just keep <body> content
    bm = re.search(r"<body\b[^>]*>", text, flags=re.I)
    if bm:
        text = text[bm.end():]

    # Convert to plain text
    plain = html_to_text(text)

    # Cut at footer markers
    cut = len(plain)
    for mk in ("前期索引", "Copyright", "回首頁", "All Rights Shared",
               "【回應文章】", "上一則", "下一則", "寄給朋友"):
        idx = plain.find(mk)
        if 0 <= idx < cut:
            cut = idx
    plain = plain[:cut].strip()

    # Strip date markers like 【2002-3-24 城中牧區】
    plain = re.sub(r"【[^】]*】", "", plain)

    # Pre-split glued markers
    plain = split_glued_markers(plain)
    plain = re.sub(r"\n{3,}", "\n\n", plain).strip()

    md: dict[str, str] = {}
    title_candidates: list[str] = []
    explicit_title: str | None = None
    body_lines: list[str] = []

    for raw_ln in plain.split("\n"):
        ln = raw_ln.strip()
        if not ln:
            if body_lines and body_lines[-1] != "":
                body_lines.append("")
            continue

        # Always-drop noise
        if (NOISE_LINE_RE.match(ln)
                or DATE_LINE_RE.match(ln)
                or LOCATION_LINE_RE.match(ln)
                or ln in BARE_NOISE_LINES
                or re.match(r"^.{1,8}：\s*$", ln)):
            continue

        # Always-extract: 講題: / 經課:
        tm = TITLE_LINE_RE.match(ln)
        if tm:
            explicit_title = tm.group(1).strip()
            continue
        sm = SCRIP_LINE_RE.match(ln)
        if sm:
            ref = normalize_scripture(sm.group(1))
            md["scripture_ref"] = (md["scripture_ref"] + "；" + ref) if md.get("scripture_ref") else ref
            continue

        # While body hasn't started: try to parse as metadata
        if not body_lines:
            # Bare scripture-reference line
            if BIBLE_BOOKS_RE.match(ln) and len(ln) <= 60:
                ref = normalize_scripture(ln.rstrip("；；").rstrip("；").strip())
                if ref:
                    md["scripture_ref"] = (md["scripture_ref"] + "；" + ref) if md.get("scripture_ref") else ref
                continue

            # Occasion line — exact / near-exact match
            occ_m = OCC_RE.match(ln)
            if occ_m:
                occ = occ_m.group(0).strip()
                rest = ln[len(occ):].strip()
                if not rest or rest in BARE_NOISE_LINES or len(rest) <= 8:
                    if "occasion" not in md:
                        md["occasion"] = occ
                    # If occasion already set and this is a duplicate/echo, drop it
                    continue

            # Named section header alone → body starts
            if ln in NAMED_HEADERS:
                body_lines.append(ln)
                continue

            # Title candidate
            if (2 <= len(ln) <= 32
                    and not re.search(r"[。！？]", ln)
                    and not OCC_RE.fullmatch(ln)):
                title_candidates.append(ln)
                continue

        body_lines.append(ln)

    # Derive occasion from any title candidate that starts with an occasion phrase
    if "occasion" not in md and title_candidates:
        occ_pat = re.compile(r"^[\s　]*(" + "|".join(OCCASION_PATTERNS) + r")\b")
        for c in title_candidates:
            m = occ_pat.match(c) or OCC_RE.match(c)
            if m:
                md["occasion"] = m.group(0).strip(" 　-－—:：")
                break

    # Pick title: explicit 講題 wins; else shortest non-scripture / non-occasion candidate
    if explicit_title:
        md["title"] = explicit_title
    elif title_candidates:
        good = [c for c in title_candidates
                if not BIBLE_BOOKS_RE.match(c) and not OCC_RE.fullmatch(c)]
        if good:
            md["title"] = min(good, key=lambda s: (len(s), s))

    # Strip prefix / noise tokens from title; backfill occasion from prefix
    if md.get("title"):
        clean, occ = cleanup_title(md["title"], md.get("occasion"))
        md["title"] = clean
        if occ and not md.get("occasion"):
            md["occasion"] = occ

    body = "\n".join(body_lines)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    body = wrap_named_headers(body)
    return md, body


# ─── Main ────────────────────────────────────────────────────────────────────


def log(msg: str) -> None:
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    log("=== reparse 2002-2007 from HTML cache — start ===")

    idx = json.load(open(INDEX_FILE, encoding="utf-8"))
    fhl_by_date: dict[str, list[dict]] = {}
    for e in idx:
        fhl_by_date.setdefault(e["date"].replace(".", "-"), []).append(e)

    # Manual override: 2006-08-13 has TWO entries; correct is sermon143
    duplicate_overrides = {"2006-08-13": "sermon143.html"}

    rows = fetch_rows()
    log(f"DB rows: {len(rows)}")

    stats = {"updated": 0, "no_match": 0, "parse_fail": 0, "patch_fail": 0}

    for i, row in enumerate(rows, 1):
        sid = row["id"]
        d = row["sermon_date"]

        if d in duplicate_overrides:
            href = duplicate_overrides[d]
        else:
            entries = fhl_by_date.get(d, [])
            if not entries:
                log(f"[no-match] {d} id={sid}")
                stats["no_match"] += 1
                continue
            # On duplicates, take first (earlier sermonNNN.html → typically the right one)
            href = entries[0]["href"]

        cache = HTML_CACHE_DIR / href.replace("/", "_")
        if not cache.exists():
            log(f"[no-cache] {d} id={sid} {href}")
            stats["no_match"] += 1
            continue

        data = cache.read_bytes()
        md, body = parse_html(data)
        if not body or len(body) < 500:
            log(f"[parse-fail] {d} id={sid} body_len={len(body)}")
            stats["parse_fail"] += 1
            continue

        new_content = f"龐君華牧師：\n\n{body}\n"

        old_title = row.get("title") or ""
        old_occasion = row.get("occasion")
        old_scripture = row.get("scripture_ref")

        # Title preference: extracted 講題 > cleaned existing
        if md.get("title"):
            new_title = md["title"]
        else:
            cleaned, _ = cleanup_title(old_title, md.get("occasion") or old_occasion)
            new_title = cleaned

        # Preserve curated occasion (clean, ≤30 chars, matches a known pattern)
        # over fhl-derived if existing is already clean.
        if old_occasion and OCC_RE.fullmatch(old_occasion) and len(old_occasion) <= 30:
            new_occasion = old_occasion
        else:
            new_occasion = md.get("occasion") or old_occasion

        # Preserve curated scripture in 經課一/啟應文/福音書 lectionary form
        if old_scripture and any(k in old_scripture for k in ("經課一", "啟應文", "福音書")):
            new_scripture = old_scripture
        else:
            new_scripture = md.get("scripture_ref") or old_scripture

        patch = {"content": new_content}
        if new_title and new_title != old_title:
            patch["title"] = new_title
        if new_occasion and new_occasion != old_occasion:
            patch["occasion"] = new_occasion
        if new_scripture and new_scripture != old_scripture:
            patch["scripture_ref"] = new_scripture

        log(f"[{i}/{len(rows)}] {d} id={sid} {href}")
        log(f"  title:    {old_title!r} → {new_title!r}")
        log(f"  occasion: {old_occasion!r} → {new_occasion!r}")
        log(f"  scrip:    {old_scripture!r} → {new_scripture!r}")
        log(f"  content_len: {len(row.get('content') or '')} → {len(new_content)}")

        try:
            patch_sermon(sid, patch)
            stats["updated"] += 1
        except Exception as e:
            log(f"  [PATCH-FAIL] {e}")
            stats["patch_fail"] += 1

    log(f"\n=== DONE  updated={stats['updated']}  no_match={stats['no_match']}  parse_fail={stats['parse_fail']}  patch_fail={stats['patch_fail']} ===")


if __name__ == "__main__":
    main()
