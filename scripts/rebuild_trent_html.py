"""
Scrape Council of Trent (1545-63) session decrees to markdown txt files.

Source: papalencyclicals.net (Waterworth 1848 English translation, public domain)
  - Per-session pages: /councils/trent/{ordinal-word}-session.htm
  - URL pattern is inconsistent (firstsession.htm / fourth-session.htm)

Output: data/creeds/ecumenical-councils/trent/trent-NN-{lang}.txt
  - NN: zero-padded session number 01-25
  - {lang}: english | latin | chinese
  - Naming matches the textKey convention in trent-NN.ts metadata files
  - latin + chinese: placeholders (Latin source TBD; Chinese needs 紙本《大公會議文獻彙編》)

Run from project root:
  python -X utf8 scripts/rebuild_trent_html.py
"""
import os
import re
import time
from bs4 import BeautifulSoup, NavigableString, Tag
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "trent")

BASE = "https://www.papalencyclicals.net/councils/trent"

# Sessions with confirmed individual decree pages
# (based on papalencyclicals.net index inspection 2026-05-22)
# Some sessions are procedural / suspension and have no separate decree page.
# Format: (session_num, url_slug_without_extension)
SESSIONS = [
    (1,  "firstsession"),
    (2,  "second-session"),
    (3,  "third-session"),
    (4,  "fourth-session"),
    (5,  "fifth-session"),
    (6,  "sixth-session"),
    (7,  "seventh-session"),
    (8,  "eighth-session"),
    (9,  "ninth-session"),
    (10, "tenth-session"),
    (11, "eleventh-session"),
    (12, "twelfth-session"),
    (13, "thirteenth-session"),
    (14, "fourteenth-session"),
    (15, "fifteenth-session"),
    (16, "sixteenth-session"),
    (17, "seventeenth-session"),
    (18, "eighteenth-session"),
    (19, "nineteenth-session"),
    (20, "twentieth-session"),
    (21, "twenty-first-session"),
    (22, "twenty-second-session"),
    (23, "twenty-third-session"),
    (24, "twenty-fourth-session"),
    (25, "twenty-fifth-session"),
]


def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(
            url,
            timeout=60,
            headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0 (creeds/trent)"},
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except requests.RequestException as e:
        print(f"  ! fetch error: {e}")
        return None


def _normalize_for_subset(s: str) -> str:
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def parse_trent_session(html: str) -> str:
    """
    papalencyclicals.net Trent session structure:
      - <h1>/<h2>/<h3> headings for decree titles ('DECREE ON...', 'CHAPTER X', 'CANONS')
      - <p> body paragraphs
      - <li> sometimes used for canons / sub-clauses (with bullet redundancy like Vatican I)
      - footer with 'Return to', 'Want to be automatically notified', etc.

    Strategy mirrors rebuild_vatican_i_html.py:
      - keep <p>/<li>/<h*> in document order
      - skip bullet sub-fragments that are substrings of the prior paragraph
      - detect headings: h-tags, ALL-CAPS short text, or text starting with
        'CHAPTER', 'CANON', 'DECREE', 'SESSION', 'ON THE', etc.
      - truncate at footer markers
    """
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body") or soup
    for tag in body.find_all(["script", "style"]):
        tag.decompose()

    blocks: list[tuple[str, str]] = []
    prev_para_norm = ""

    HEADING_START = re.compile(
        r"^(SESSION|CHAPTER|CANON|DECREE|ON\s+THE|THE\s+SACRED|DOCTRINE|FOREWORD|"
        r"INTRODUCTION|PROOEMIUM|PREFACE|"
        r"\d+\s*\.\s+(ON|OF))",
        re.IGNORECASE,
    )

    for el in body.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li"]):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        text = re.sub(r"\s+", " ", text).strip()

        # footer / nav noise
        low = text.lower()
        if low.startswith("return to") or low.startswith("back to"):
            continue
        if "papalencyclicals" in low and len(text) < 80:
            continue
        if low.startswith(("copyright", "all rights", "last updated", "©")):
            continue
        if text in ("Council of Trent", "Trent"):
            continue

        is_heading = (
            el.name in ("h1", "h2", "h3", "h4", "h5")
            or (text.isupper() and len(text) < 120 and len(text) > 4)
            or (HEADING_START.match(text) and len(text) < 200)
        )

        # <strong> / <b> entire-wrap also counts as heading
        if not is_heading and el.name in ("p", "li"):
            strong_tags = el.find_all(["strong", "b"])
            if strong_tags:
                inside = " ".join(s.get_text(" ", strip=True) for s in strong_tags)
                if inside and inside.replace(" ", "") == text.replace(" ", ""):
                    is_heading = True

        # substring dedup
        if not is_heading:
            norm = _normalize_for_subset(text)
            if norm and prev_para_norm and norm in prev_para_norm:
                continue
            prev_para_norm = norm
        else:
            prev_para_norm = ""

        blocks.append(("heading" if is_heading else "para", text))

    # Truncate at footer markers
    cutoff = None
    for i, (kind, text) in enumerate(blocks):
        low = text.lower()
        if "want to be automatically notified" in low or "for more information about this site" in low:
            cutoff = i
            break
    if cutoff is not None:
        blocks = blocks[:cutoff]

    lines: list[str] = []
    for kind, text in blocks:
        if kind == "heading":
            lines.append("")
            lines.append(f"## {text}")
            lines.append("")
        else:
            lines.append(text)
            lines.append("")
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    os.makedirs(TXT_DIR, exist_ok=True)

    summary: list[tuple[int, str, int]] = []  # (session_num, status, byte_size)

    for sn, slug in SESSIONS:
        url = f"{BASE}/{slug}.htm"
        print(f"[session {sn:02d}] {url}")
        html = fetch_html(url)
        if html is None:
            print(f"  ✗ 404 — skipping")
            summary.append((sn, "404", 0))
            continue
        md = parse_trent_session(html)
        out_path = os.path.join(TXT_DIR, f"trent-{sn:02d}-english.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  ✓ wrote {os.path.basename(out_path)} ({len(md):,} chars)")
        summary.append((sn, "ok", len(md)))
        time.sleep(0.3)  # polite delay

        # Latin + Chinese placeholders (only if missing — never overwrite)
        for lang in ("latin", "chinese"):
            p = os.path.join(TXT_DIR, f"trent-{sn:02d}-{lang}.txt")
            if not os.path.exists(p):
                if lang == "latin":
                    note = (
                        f"（Session {sn} 拉丁版尚未取得 — vatican.va 對 Trent (1545-63) 僅\n"
                        f"提供 Italian + 部分 Latin extract。\n"
                        f"可能來源：\n"
                        f"  - documentacatholicaomnia.eu (Latin)\n"
                        f"  - Wikisource la (Latin)\n"
                        f"  - intratext.com LAT0432\n"
                        f"取得後請手動覆蓋本檔。）\n"
                    )
                else:
                    note = (
                        f"（Session {sn} 中文版尚未取得。線上無公開全文中譯本。\n"
                        f"可能來源：\n"
                        f"  - 中華民國天主教主教團《天主教大公會議文獻彙編》中譯本\n"
                        f"  - 思高聖經學會《大公會議信條彙編》\n"
                        f"  - 香港教區出版相關文獻\n"
                        f"取得後請手動覆蓋本檔。）\n"
                    )
                with open(p, "w", encoding="utf-8") as f:
                    f.write(note)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for sn, status, sz in summary:
        mark = "✓" if status == "ok" else "✗"
        print(f"  {mark} Session {sn:02d}: {status:6} {sz:>8,} chars")
    ok_count = sum(1 for _, s, _ in summary if s == "ok")
    print(f"\nTotal: {ok_count}/{len(SESSIONS)} sessions scraped")


if __name__ == "__main__":
    main()
