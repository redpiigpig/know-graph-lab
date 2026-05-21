"""
Backfill Vatican II 16 docs' Chinese version from vatican.va PDF.

1. Download `vat-ii_{slug}_zh-t.pdf` to /tmp/vat2_pdf/
2. pdftotext -enc UTF-8 -layout -> raw .txt
3. Light clean (collapse 3+ blank lines, strip leading/trailing blank, strip page numbers)
4. Write data/creeds/ecumenical-councils/vatican-ii/{code-lc}-zh.txt
5. Rewrite the corresponding ts file: replace the zh-Hant-Catholic version block.

Run from project root:
  python scripts/backfill_vatican_ii_chinese.py
"""
import os
import re
import subprocess
import sys
import time

import requests

DOCS = [
    ("SC", "sacrosanctum-concilium", 1),
    ("IM", "inter-mirifica", 2),
    ("LG", "lumen-gentium", 3),
    ("OE", "orientalium-ecclesiarum", 4),
    ("UR", "unitatis-redintegratio", 5),
    ("CD", "christus-dominus", 6),
    ("PC", "perfectae-caritatis", 7),
    ("OT", "optatam-totius", 8),
    ("GE", "gravissimum-educationis", 9),
    ("NA", "nostra-aetate", 10),
    ("DV", "dei-verbum", 11),
    ("AA", "apostolicam-actuositatem", 12),
    ("DH", "dignitatis-humanae", 13),
    ("AG", "ad-gentes", 14),
    ("PO", "presbyterorum-ordinis", 15),
    ("GS", "gaudium-et-spes", 16),
]

URL = "https://www.vatican.va/chinese/concilio/vat-ii_{slug}_zh-t.pdf"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "vat2_pdf")
TXT_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "vatican-ii")
TS_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils")
os.makedirs(PDF_DIR, exist_ok=True)


def download(slug: str) -> str:
    path = os.path.join(PDF_DIR, f"{slug}.pdf")
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return path
    url = URL.format(slug=slug)
    print(f"  downloading {url} ...", flush=True)
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0"})
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def pdf_to_text(pdf_path: str) -> str:
    """Use pdftotext -layout to preserve paragraph structure."""
    txt_path = pdf_path.replace(".pdf", ".txt")
    subprocess.run(
        ["pdftotext", "-enc", "UTF-8", "-layout", pdf_path, txt_path],
        check=True,
    )
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


def clean(text: str) -> str:
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip page number lines (pure digits) and form-feed
    lines = []
    for line in text.split("\n"):
        # PDF page break char
        line = line.replace("\f", "")
        # Strip trailing spaces (pdftotext -layout pads heavily)
        stripped = line.rstrip()
        # Skip lines that are only a number 1-200 (page numbers)
        if re.match(r"^\s*\d{1,3}\s*$", stripped):
            continue
        lines.append(stripped)
    text = "\n".join(lines)
    # Collapse 3+ blank lines -> 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_txt(code: str, content: str) -> str:
    path = os.path.join(TXT_DIR, f"{code.lower()}-chinese.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


CHINESE_VERSION_PATTERN = re.compile(
    r"\{\s*\n\s*lang:\s*'zh-Hant-Catholic',.*?\n\s*placeholder:\s*true,\s*\n\s*\},\s*\n",
    re.DOTALL,
)


def update_ts_file(code: str, doc_order: int) -> bool:
    """Rewrite the zh-Hant-Catholic block in the corresponding ts file.

    Replace placeholder with raw-text import.
    """
    code_lc = code.lower()
    ts_path = os.path.join(TS_DIR, f"vatican-ii-{doc_order:02d}-{code_lc}.ts")
    with open(ts_path, "r", encoding="utf-8") as f:
        src = f.read()

    # Add the zh import line (after the en import)
    if f"from './vatican-ii/{code_lc}-chinese.txt?raw'" not in src:
        # find existing imports
        new_import = (
            f"// @ts-expect-error — Vite raw-text import\n"
            f"import zhText from './vatican-ii/{code_lc}-chinese.txt?raw'\n"
        )
        # Insert after the last "import ... from './vatican-ii/..." line
        marker = re.search(r"(import enText from '\./vatican-ii/[^']+\?raw'\n)", src)
        if not marker:
            print(f"  [{code}] cannot find enText import — manual fix needed")
            return False
        src = src[:marker.end()] + new_import + src[marker.end():]

    # Replace the zh-Hant-Catholic placeholder block
    new_block = (
        "{\n"
        "      lang: 'zh-Hant-Catholic',\n"
        "      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',\n"
        "      text: zhText as string,\n"
        f"      source: 'https://www.vatican.va/chinese/concilio/vat-ii_{slug_of(code)}_zh-t.pdf',\n"
        "      translator: '台灣地區主教團 / 香港教區禮儀委員會',\n"
        "    },\n"
    )

    new_src, n = CHINESE_VERSION_PATTERN.subn(new_block, src, count=1)
    if n != 1:
        print(f"  [{code}] cannot find placeholder block (matched {n} times)")
        return False

    with open(ts_path, "w", encoding="utf-8") as f:
        f.write(new_src)
    return True


def slug_of(code: str) -> str:
    for c, s, _ in DOCS:
        if c == code:
            return s
    return ""


def main():
    fail = []
    for code, slug, doc_order in DOCS:
        print(f"[{code}] {slug}", flush=True)
        try:
            pdf_path = download(slug)
            raw = pdf_to_text(pdf_path)
            cleaned = clean(raw)
            if len(cleaned) < 500:
                print(f"  [{code}] extracted text too short ({len(cleaned)} chars) — skipping ts update")
                fail.append((code, "text_too_short"))
                continue
            txt_path = write_txt(code, cleaned)
            print(f"  -> {txt_path} ({len(cleaned)} chars)", flush=True)
            ok = update_ts_file(code, doc_order)
            if not ok:
                fail.append((code, "ts_rewrite_failed"))
        except Exception as e:
            print(f"  [{code}] EXCEPTION: {e}", flush=True)
            fail.append((code, str(e)))
        time.sleep(0.8)

    if fail:
        print("\n=== Failures ===")
        for code, reason in fail:
            print(f"  {code}: {reason}")
        sys.exit(1)
    else:
        print("\n=== All 16 docs backfilled successfully ===")


if __name__ == "__main__":
    main()
