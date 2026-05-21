"""
Re-extract Vatican II HTML (Latin + English) preserving structure:

  - <p><i><b>...</b></i></p>  -> '## {text}' (section heading)
  - <p>N. ...</p>             -> 'N. ...' (paragraph; keeps inline footnote refs)
  - <a href="#_ftnN" name="_ftnrefN">M</a>  -> '[^M]' (anchor-style footnote ref)
  - footnote definitions section -> trailing '[^M]: ...' lines

Output: data/creeds/ecumenical-councils/vatican-ii/{code}-{lang}.txt (overwrite)

Run from project root:
  python scripts/rebuild_vatican_ii_html.py
"""
import os
import re
import sys
import time
from bs4 import BeautifulSoup, Tag
import requests

DOCS = [
    ("SC", "const", "19631204", "sacrosanctum-concilium"),
    ("IM", "decree", "19631204", "inter-mirifica"),
    ("LG", "const", "19641121", "lumen-gentium"),
    ("OE", "decree", "19641121", "orientalium-ecclesiarum"),
    ("UR", "decree", "19641121", "unitatis-redintegratio"),
    ("CD", "decree", "19651028", "christus-dominus"),
    ("PC", "decree", "19651028", "perfectae-caritatis"),
    ("OT", "decree", "19651028", "optatam-totius"),
    ("GE", "decl", "19651028", "gravissimum-educationis"),
    ("NA", "decl", "19651028", "nostra-aetate"),
    ("DV", "const", "19651118", "dei-verbum"),
    ("AA", "decree", "19651118", "apostolicam-actuositatem"),
    ("DH", "decl", "19651207", "dignitatis-humanae"),
    ("AG", "decree", "19651207", "ad-gentes"),
    ("PO", "decree", "19651207", "presbyterorum-ordinis"),
    ("GS", "const", "19651207", "gaudium-et-spes"),
]

URL_TMPL = "https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_{type}_{date}_{slug}_{lang}.html"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "vatican-ii")


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0"})
    r.raise_for_status()
    # vatican.va serves iso-8859-1; requests auto-detects via meta but force just in case
    r.encoding = r.apparent_encoding or "iso-8859-1"
    return r.text


def is_section_heading(p: Tag) -> bool:
    """A <p> wholly inside <i><b>...</b></i> or <b><i>...</i></b> is a section heading."""
    children = [c for c in p.children if not (isinstance(c, str) and not c.strip())]
    if len(children) != 1:
        return False
    inner = children[0]
    if not isinstance(inner, Tag):
        return False
    if inner.name not in ("i", "b"):
        return False
    sub = [c for c in inner.children if not (isinstance(c, str) and not c.strip())]
    if len(sub) != 1:
        return False
    inner2 = sub[0]
    if isinstance(inner2, Tag) and inner2.name in ("i", "b") and inner2.name != inner.name:
        return True
    return False


def transform_footnote_refs(p: Tag) -> str:
    """
    Convert inline `<a href="#_ftnN" name="_ftnrefN">M</a>` -> `[^M]`.
    Then return text representation with markers in place.
    """
    # Clone — work on a fresh tree
    for a in p.find_all("a", href=re.compile(r"^#_ftn\d+")):
        marker_num = a.get_text(" ", strip=True)
        a.replace_with(f"[^{marker_num}]")
    # remove any other navigational <a> within
    for a in p.find_all("a"):
        a.replace_with(a.get_text(" ", strip=True))
    text = p.get_text(" ", strip=True)
    # Collapse [33] (sometimes wrapped in brackets) -> [^33]
    text = re.sub(r"\[\s*\[\^(\d+)\]\s*\]", r"[^\1]", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def is_footnote_section_start(p: Tag) -> bool:
    """
    Footnote definitions: a <p> containing one of:
      <a name="_ftn1">...</a>
    """
    a = p.find("a", attrs={"name": re.compile(r"^_ftn\d+$")})
    return a is not None


def parse_footnote_def(p: Tag) -> tuple[str, str] | None:
    """Parse a footnote-definition <p> -> (num, body)."""
    a = p.find("a", attrs={"name": re.compile(r"^_ftn\d+$")})
    if not a:
        return None
    m = re.match(r"_ftn(\d+)", a.get("name", ""))
    if not m:
        return None
    num = m.group(1)
    # Convert internal refs to plain text
    for inner_a in p.find_all("a"):
        inner_a.replace_with(inner_a.get_text(" ", strip=True))
    text = p.get_text(" ", strip=True)
    # Strip leading marker like "[33]" or "33"
    text = re.sub(rf"^\[?\s*{num}\s*\]?\s*", "", text).strip()
    return num, text


def extract(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup.find_all(["nav", "footer", "header", "script", "style"]):
        t.decompose()

    out_lines: list[str] = []
    footnotes: list[tuple[str, str]] = []
    seen_footnote_start = False

    for p in soup.find_all("p"):
        # Once we hit a footnote def, all subsequent <p> are footnote defs or noise
        if not seen_footnote_start and is_footnote_section_start(p):
            seen_footnote_start = True

        if seen_footnote_start:
            res = parse_footnote_def(p)
            if res:
                num, body = res
                if len(body) >= 2:
                    footnotes.append((num, body))
            continue

        # Skip language switcher line
        txt = p.get_text(" ", strip=True)
        if not txt or len(txt) < 4:
            continue
        if re.match(r"^\[\s*[A-Z]{2}(\s*-\s*[A-Z]{2})+\s*\]$", txt):
            continue

        if is_section_heading(p):
            out_lines.append(f"## {txt}")
            out_lines.append("")
            continue

        # Standard paragraph (may contain footnote refs)
        body = transform_footnote_refs(p)
        if body:
            out_lines.append(body)
            out_lines.append("")

    # Append footnote definitions
    if footnotes:
        out_lines.append("---")
        out_lines.append("")
        out_lines.append("## Footnotes")
        out_lines.append("")
        for num, body in footnotes:
            out_lines.append(f"[^{num}]: {body}")

    return "\n".join(out_lines).strip() + "\n"


def main():
    failures = []
    for code, doctype, date, slug in DOCS:
        for lang_url, lang_file in [("lt", "latin"), ("en", "english")]:
            url = URL_TMPL.format(type=doctype, date=date, slug=slug, lang=lang_url)
            target = os.path.join(TXT_DIR, f"{code.lower()}-{lang_file}.txt")
            print(f"[{code}-{lang_file}] {url}", flush=True)
            try:
                html = fetch_html(url)
                content = extract(html)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  -> {target} ({len(content)} bytes)", flush=True)
            except Exception as e:
                print(f"  FAILED: {e}", flush=True)
                failures.append((code, lang_file, str(e)))
            time.sleep(0.8)

    if failures:
        print("\n=== Failures ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print("\n=== All 32 (16 docs × 2 langs) re-extracted ===")


if __name__ == "__main__":
    main()
