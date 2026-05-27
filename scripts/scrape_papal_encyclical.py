"""
Scrape a single papal encyclical from vatican.va into the
data/encyclicals/{NNc-pope-slug}/{slug}-{lang}.txt format expected by
data/encyclicals/textLoader.ts.

Output convention (sympatico with data/creeds/paragraphParser.ts):
  - <p><b>...</b></p>         -> '## {text}' (chapter heading)
  - <p>N. ...</p>             -> 'N. ...'    (numbered paragraph)
  - inline <a href="#_ftnN">M</a> -> '[^M]'
  - footnote definition section -> trailing '[^M]: ...'

Usage:
  python scripts/scrape_papal_encyclical.py \\
      --pope francesco \\
      --pope-slug francis \\
      --century 21 \\
      --doc-slug laudato-si-2015 \\
      --url-key papa-francesco_20150524_enciclica-laudato-si \\
      --doctype encyclicals

Languages handled: la / en / zh_tw.

vatican.va URL pattern (modern Francis era):
  https://www.vatican.va/content/{pope}/{lang}/{doctype}/documents/{url-key}.html

For older encyclicals (Pius IX / Leo XIII era) the URL pattern uses:
  hf_{pope}_{YYYYMMDD}_{slug}
i.e. --url-key 'hf_l-xiii_18910515_rerum-novarum'
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser

try:
    from bs4 import BeautifulSoup, Tag, NavigableString  # type: ignore
except ImportError:
    print("ERROR: BeautifulSoup4 required. Run: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

URL_TMPL = (
    "https://www.vatican.va/content/{pope}/{lang}/{doctype}/documents/"
    "{key}.html"
)

# Doctypes where the URL does NOT use a `documents/` subfolder (eg the
# older Pius IX path /pius-ix/it/documents/{key}.html — only ONE
# `documents/` segment, not `{doctype}/documents/`).
DOCTYPE_NO_SUBFOLDER = {"documents"}


def make_url(pope: str, lang: str, doctype: str, key: str) -> str:
    if doctype in DOCTYPE_NO_SUBFOLDER:
        return f"https://www.vatican.va/content/{pope}/{lang}/{doctype}/{key}.html"
    return URL_TMPL.format(pope=pope, lang=lang, doctype=doctype, key=key)

LANG_FILES = [
    ("la", "latin"),
    ("it", "italian"),
    ("en", "english"),
    ("zh_tw", "chinese"),
]


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    # vatican.va serves utf-8 mostly; some old pages iso-8859-1. Try utf-8 first.
    for enc in ("utf-8", "iso-8859-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def is_section_heading(p: Tag) -> bool:
    """A <p> wholly bold-italic (or italic-bold) -> section heading.

    vatican.va encyclicals use a mix of patterns; we detect the common one:
      <p><b><i>HEADING</i></b></p>  or  <p><i><b>HEADING</b></i></p>
      <p><b>HEADING</b></p>          (used for chapter-level)
    """
    children = [c for c in p.children if not (isinstance(c, NavigableString) and not c.strip())]
    if len(children) != 1:
        return False
    inner = children[0]
    if not isinstance(inner, Tag):
        return False
    if inner.name not in ("i", "b", "strong", "em"):
        return False
    text = inner.get_text(" ", strip=True)
    # Heuristic: heading is short-ish and doesn't start with a number+period
    if len(text) > 200:
        return False
    if re.match(r"^\d+\.\s", text):
        return False
    sub = [c for c in inner.children if not (isinstance(c, NavigableString) and not c.strip())]
    # Single nested tag of opposite type (b > i or i > b): heading
    if len(sub) == 1 and isinstance(sub[0], Tag) and sub[0].name in ("i", "b", "strong", "em"):
        return True
    # Single bare-bold heading (no nested italics)
    if inner.name in ("b", "strong") and not any(isinstance(c, Tag) for c in sub):
        return True
    return False


def is_flat_section_heading(p: Tag) -> bool:
    """Fallback for HTML that uses plain <p> (no bold/italic wrap) for headings.

    Used by e.g. Fratelli Tutti, Dilexit Nos. A <p> is a flat heading if:
      - has no <a href="#_ftn..."> references (body paragraphs always do)
      - text doesn't start with `N.` (not a numbered paragraph)
      - text length 4 to 250 chars
      - text contains no sentence-internal punctuation (`,;:`)
      - text has no `. ` mid-sentence period

    The vatican.va template uses `style="text-align: center;"` for chapter-level
    headings sometimes; we accept both styles.
    """
    # Skip if has any footnote anchor
    if p.find("a", href=re.compile(r"^#_(?:ftn|edn)\d+")):
        return False
    # Skip if has inline bold/italic — handled by is_section_heading
    if any(isinstance(c, Tag) and c.name in ("b", "i", "strong", "em") for c in p.children):
        return False
    text = p.get_text(" ", strip=True)
    if not text or len(text) < 4 or len(text) > 250:
        return False
    if re.match(r"^\d+\.\s", text):
        return False
    if re.match(r"^\[\^", text):
        return False
    # Reject if contains sentence-internal punctuation (Latin)
    if re.search(r"[,;](\s|$)", text):
        return False
    if re.search(r":\s", text):
        return False
    # Reject if contains mid-sentence period (period followed by space + word)
    if re.search(r"\.\s+\S", text):
        return False
    # Reject CJK punctuation (Chinese commas / semicolons / colons / periods)
    if re.search(r"[，；：。、！？]", text):
        return False
    # Accept
    return True


def transform_footnote_refs(p: Tag) -> str:
    """Convert inline <a href="#_ftnN" name="_ftnrefN">M</a> -> [^M]."""
    for a in p.find_all("a", href=re.compile(r"^#_(?:ftn|edn)\d+")):
        marker_num = a.get_text(" ", strip=True)
        # marker_num may be wrapped like "[33]" — strip brackets
        marker_num = re.sub(r"[\[\]]", "", marker_num).strip()
        if marker_num.isdigit():
            a.replace_with(f"[^{marker_num}]")
        else:
            a.replace_with("")
    for a in p.find_all("a"):
        a.replace_with(a.get_text(" ", strip=True))
    text = p.get_text(" ", strip=True)
    text = re.sub(r"\[\s*\[\^(\d+)\]\s*\]", r"[^\1]", text)
    # vatican.va wraps paragraph numbers in <a name="N">N</a> — get_text(" ")
    # leaves a space before the period: "2 . Body" → fold to "2. Body".
    text = re.sub(r"^(\d{1,3})\s+\.\s*", r"\1. ", text)
    # Some HTML omits the space after the paragraph-number period:
    #   "131.Later, his spiritual..." → "131. Later, his spiritual..."
    # Only insert when the next char is a letter/CJK (avoid "1.5 million").
    text = re.sub(r"^(\d{1,3})\.([A-Za-z一-鿿])", r"\1. \2", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def is_footnote_section_start(p: Tag) -> bool:
    a = p.find("a", attrs={"name": re.compile(r"^_(?:ftn|edn)\d+$")})
    return a is not None


def parse_footnote_def(p: Tag) -> tuple[str, str] | None:
    a = p.find("a", attrs={"name": re.compile(r"^_(?:ftn|edn)\d+$")})
    if not a:
        return None
    m = re.match(r"_(?:ftn|edn)(\d+)", a.get("name", ""))
    if not m:
        return None
    num = m.group(1)
    for inner_a in p.find_all("a"):
        inner_a.replace_with(inner_a.get_text(" ", strip=True))
    text = p.get_text(" ", strip=True)
    text = re.sub(rf"^\[?\s*{num}\s*\]?\s*", "", text).strip()
    return num, text


PARA_NUM_RE = re.compile(r"^(\d{1,3})\.\s+")


def extract(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup.find_all(["nav", "footer", "header", "script", "style"]):
        t.decompose()

    out_lines: list[str] = []
    footnotes: list[tuple[str, str]] = []
    seen_footnote_start = False

    for p in soup.find_all("p"):
        if not seen_footnote_start and is_footnote_section_start(p):
            seen_footnote_start = True

        if seen_footnote_start:
            res = parse_footnote_def(p)
            if res:
                num, body = res
                if len(body) >= 2:
                    footnotes.append((num, body))
            continue

        txt = p.get_text(" ", strip=True)
        if not txt or len(txt) < 4:
            continue
        if re.match(r"^\[\s*[A-Z]{2}(\s*-\s*[A-Z]{2})+\s*\]$", txt):
            continue
        # Skip language switcher style: comma/dot separated language codes
        if re.match(r"^[A-Z]{2}(\s*[,\-]\s*[A-Z]{2}){3,}$", txt):
            continue

        if is_section_heading(p):
            out_lines.append(f"## {txt}")
            out_lines.append("")
            continue

        if is_flat_section_heading(p):
            out_lines.append(f"## {txt}")
            out_lines.append("")
            continue

        body = transform_footnote_refs(p)
        if body:
            out_lines.append(body)
            out_lines.append("")

    if footnotes:
        out_lines.append("---")
        out_lines.append("")
        out_lines.append("## Footnotes")
        out_lines.append("")
        for num, body in footnotes:
            out_lines.append(f"[^{num}]: {body}")
            out_lines.append("")  # blank line so parseDoc treats each as its own block

    return "\n".join(out_lines).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pope", required=True, help="vatican.va URL pope slug, e.g. 'francesco' / 'benedict-xvi' / 'leo-xiii'")
    ap.add_argument("--pope-slug", required=True, help="our internal pope slug, e.g. 'francis'")
    ap.add_argument("--century", type=int, required=True)
    ap.add_argument("--doc-slug", required=True, help="our internal doc slug, e.g. 'laudato-si-2015'")
    ap.add_argument("--url-key", required=True, help="vatican.va URL filename without .html, e.g. 'papa-francesco_20150524_enciclica-laudato-si'")
    ap.add_argument("--doctype", default="encyclicals", choices=["encyclicals", "apost_constitutions", "apost_exhortations", "apost_letters", "documents", "bulls"])
    ap.add_argument("--langs", default="la,en,zh_tw", help="comma-separated subset of la/en/zh_tw")
    args = ap.parse_args()

    century_label = f"{args.century:02d}c"
    out_dir = os.path.join(ROOT, "data", "encyclicals", f"{century_label}-{args.pope_slug}")
    os.makedirs(out_dir, exist_ok=True)

    wanted_langs = {l.strip() for l in args.langs.split(",") if l.strip()}
    failures = []
    for lang_url, lang_file in LANG_FILES:
        if lang_url not in wanted_langs:
            continue
        url = make_url(args.pope, lang_url, args.doctype, args.url_key)
        target = os.path.join(out_dir, f"{args.doc_slug}-{lang_file}.txt")
        print(f"[{args.doc_slug}-{lang_file}] {url}", flush=True)
        try:
            html = fetch_html(url)
            content = extract(html)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  -> {target} ({len(content)} bytes)", flush=True)
        except Exception as e:
            print(f"  FAILED: {e}", flush=True)
            failures.append((args.doc_slug, lang_file, str(e)))
        time.sleep(0.8)

    if failures:
        print("\n=== Failures ===")
        for f in failures:
            print(f)
        return 1
    print(f"\n=== Done: {len([l for l in LANG_FILES if l[0] in wanted_langs])} files ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
