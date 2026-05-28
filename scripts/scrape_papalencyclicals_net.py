"""
Scrape a single document from papalencyclicals.net into a paragraph-aligned
.txt file compatible with data/encyclicals/textLoader.ts.

URL pattern: https://www.papalencyclicals.net/{popekey}/{docslug}.htm

Output convention (matches data/creeds/paragraphParser.ts):
  - Single intro paragraphs (pre-numbering): emitted as '## Introduction' chapter then plain paras
  - Numbered paragraphs: emitted verbatim as 'N. ...'
  - Footnotes (after final <hr/>): emitted as '[^N]: ...'

Usage:
  python scripts/scrape_papalencyclicals_net.py \\
      --url https://www.papalencyclicals.net/pius09/p9quanta.htm \\
      --out tmp/quanta-english.txt

  # batch:
  python scripts/scrape_papalencyclicals_net.py --url URL --out FILE [--meta meta.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Tag, NavigableString  # type: ignore
except ImportError:
    print("ERROR: BeautifulSoup4 required. pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


USER_AGENT = "Mozilla/5.0 (compatible; know-graph-lab papal scraper)"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    return raw.decode("utf-8", errors="replace")


_SMART_QUOTES = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
    "′": "'", "″": '"',
}


def normalize_text(s: str) -> str:
    for k, v in _SMART_QUOTES.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def collapse_inline(el: Tag) -> str:
    """Render an element's text, preserving inline footnote anchors as [^N]."""
    parts: list[str] = []
    for child in el.descendants:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            if child.name == "sup":
                # often wraps footnote anchors
                continue  # text inside <sup> will be handled by descendant walk
            if child.name == "a":
                href = child.get("href", "")
                m = re.match(r"#_?ftn(\d+)", href) or re.match(r"#fn(\d+)", href)
                if m:
                    # Replace anchor text with [^N]
                    # We're walking descendants; mark the anchor's own text to skip
                    pass
    # Simpler: process top-level children
    out: list[str] = []
    for node in el.children:
        if isinstance(node, NavigableString):
            out.append(str(node))
        elif isinstance(node, Tag):
            if node.name == "sup":
                txt = node.get_text("", strip=True)
                m = re.match(r"^(\d+)$", txt)
                if m:
                    out.append(f"[^{m.group(1)}]")
                else:
                    # also handle <sup><a>N</a></sup>
                    a = node.find("a")
                    if a:
                        m2 = re.match(r"^(\d+)$", a.get_text(strip=True))
                        if m2:
                            out.append(f"[^{m2.group(1)}]")
                            continue
                    out.append(txt)
            elif node.name == "a":
                href = node.get("href", "")
                m = re.match(r"#_?ftn(\d+)", href) or re.match(r"#fn(\d+)", href)
                txt = node.get_text("", strip=True)
                if m:
                    out.append(f"[^{m.group(1)}]")
                else:
                    out.append(txt)
            elif node.name == "br":
                out.append(" ")
            elif node.name in ("b", "strong", "i", "em", "span", "u", "small"):
                out.append(collapse_inline(node))
            else:
                out.append(node.get_text(" ", strip=False))
    return normalize_text("".join(out))


PARA_NUM_RE = re.compile(r"^(\d{1,3})\.\s+(.*)$", re.S)


def split_para_number(text: str) -> tuple[str | None, str]:
    m = PARA_NUM_RE.match(text)
    if m:
        return m.group(1), m.group(2).strip()
    return None, text.strip()


def scrape(url: str) -> dict:
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    t = soup.find("title")
    if t:
        title = re.sub(r"\s*-\s*Papal Encyclicals\s*$", "", t.get_text(strip=True))
    title = title or "Untitled"

    # date
    date = ""
    meta = soup.find("meta", attrs={"property": "article:published_time"})
    if meta:
        v = meta.get("content", "")
        m = re.match(r"(\d{4}-\d{2}-\d{2})", v)
        if m:
            date = m.group(1)

    # author / pope
    pope = ""
    meta = soup.find("meta", attrs={"name": "twitter:data1"})
    if meta:
        pope = meta.get("content", "").strip()
    # section is e.g. "Ven. Pope Pius IX (June 16, 1846 - February 7, 1878)"
    pope_section = ""
    meta = soup.find("meta", attrs={"property": "article:section"})
    if meta:
        pope_section = meta.get("content", "").strip()

    # body
    body = soup.find("div", class_="entry-content")
    if not body:
        raise RuntimeError("no entry-content div found")

    lines: list[str] = []
    footnotes: dict[str, str] = {}
    after_hr = False
    seen_h_heading = False
    intro_paras: list[str] = []
    body_paras: list[tuple[str | None, str]] = []  # (num, text)

    for node in body.children:
        if isinstance(node, NavigableString):
            continue
        if not isinstance(node, Tag):
            continue

        if node.name == "hr":
            after_hr = True
            continue

        if not after_hr:
            if node.name in ("h1", "h2", "h3", "h4"):
                text = node.get_text(" ", strip=True)
                if text:
                    body_paras.append((None, f"__HEADING__::{normalize_text(text)}"))
                    seen_h_heading = True
                continue
            if node.name == "p":
                text = collapse_inline(node)
                if not text:
                    continue
                # Treat as heading only when the <p> is solely wrapped in <strong>/<b>
                # (i.e. there is a non-empty <strong> child and no bare text siblings).
                non_empty_children = [c for c in node.children
                                      if not (isinstance(c, NavigableString) and not str(c).strip())]
                has_strong_wrap = (
                    len(non_empty_children) >= 1
                    and all(isinstance(c, Tag) and c.name in ("strong", "b")
                            for c in non_empty_children)
                    and len(text) < 200
                    and not PARA_NUM_RE.match(text)
                )
                if has_strong_wrap:
                    body_paras.append((None, f"__HEADING__::{text}"))
                    continue
                num, txt = split_para_number(text)
                body_paras.append((num, txt))
                continue
            if node.name == "blockquote":
                text = collapse_inline(node)
                if text:
                    body_paras.append((None, text))
                continue
            if node.name == "ul" or node.name == "ol":
                # list items in body: render as one paragraph per item, no number
                for li in node.find_all("li", recursive=False):
                    text = collapse_inline(li)
                    if text:
                        body_paras.append((None, "- " + text))
                continue
        else:
            # Footnotes section: <p>1. ...</p> and/or <ul><li>2. ...</li></ul>
            if node.name == "p":
                text = collapse_inline(node)
                if not text:
                    continue
                m = re.match(r"^(\d+)\.\s*(.*)$", text)
                if m:
                    footnotes[m.group(1)] = m.group(2).strip()
                continue
            if node.name in ("ul", "ol"):
                for li in node.find_all("li", recursive=False):
                    text = collapse_inline(li)
                    if not text:
                        continue
                    m = re.match(r"^(\d+)\.\s*(.*)$", text)
                    if m:
                        footnotes[m.group(1)] = m.group(2).strip()
                continue

    # Convert inline numeric footnote markers (plain digits appended to words)
    # into [^N] markers, but ONLY for digits that match a footnote number.
    # papalencyclicals.net pages often render "interests.1" or "religion."2"" as plain text.
    def add_inline_fn(text: str) -> str:
        if not footnotes:
            return text
        # Match digit(s) right after a word-char, before a space/quote/punct/end.
        # Limit to numbers that appear in the footnotes table.
        valid = set(footnotes.keys())
        def repl(m: re.Match) -> str:
            pre, n = m.group(1), m.group(2)
            if n in valid:
                return f"{pre}[^{n}]"
            return m.group(0)
        # Apply once per run; iterate from longest digit-string first to avoid biting "12" as "1"+"2"
        return re.sub(r"([a-zA-Z\"'\)\.,;:])(\d{1,2})(?=[\s\"'\)\.,;:]|$)", repl, text)

    # Emit
    out_lines: list[str] = []
    out_lines.append(f"## {title.upper()}")
    out_lines.append("")
    pope_clean = re.sub(r"^Pope\s+(BI\.|Bl\.|St\.)?\s*", "", pope, flags=re.I).strip()
    if pope_clean:
        out_lines.append(f"DOCUMENT OF POPE {pope_clean.upper()}")
        out_lines.append("")
    if date:
        out_lines.append(f"Promulgated {date}")
        out_lines.append("")

    for num, txt in body_paras:
        if txt.startswith("__HEADING__::"):
            head = txt[len("__HEADING__::"):]
            out_lines.append(f"## {head}")
            out_lines.append("")
            continue
        txt = add_inline_fn(txt)
        if num is not None:
            out_lines.append(f"{num}. {txt}")
        else:
            out_lines.append(txt)
        out_lines.append("")

    if footnotes:
        out_lines.append("")
        for k in sorted(footnotes.keys(), key=lambda x: int(x)):
            out_lines.append(f"[^{k}]: {footnotes[k]}")

    return {
        "title": title,
        "date": date,
        "pope": pope,
        "pope_section": pope_section,
        "text": "\n".join(out_lines).rstrip() + "\n",
        "num_paras": sum(1 for n, _ in body_paras if n is not None),
        "num_headings": sum(1 for _, t in body_paras if t.startswith("__HEADING__::")),
        "num_footnotes": len(footnotes),
        "url": url,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, help="output .txt path")
    ap.add_argument("--meta", default=None, help="optional .json metadata path")
    args = ap.parse_args()

    info = scrape(args.url)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(info["text"], encoding="utf-8")

    if args.meta:
        meta_out = {k: v for k, v in info.items() if k != "text"}
        meta_out["bytes"] = len(info["text"].encode("utf-8"))
        Path(args.meta).write_text(
            json.dumps(meta_out, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"  Wrote {out_path}  ({len(info['text'].encode('utf-8'))} bytes)")
    print(f"    title={info['title']!r}  date={info['date']}  pope={info['pope']!r}")
    print(f"    paras={info['num_paras']}  headings={info['num_headings']}  fns={info['num_footnotes']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
