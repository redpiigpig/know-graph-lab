"""
Scrape original-language (Greek + Latin) text of ecumenical councils from
documentacatholicaomnia.eu (DCO).

Coverage:
  Early Eastern (3-7, 431-787):
    - Greek originals where DCO has GR.pdf (Chalcedon 451, Nicaea II 787)
    - Latin (Rusticus Diaconi etc. medieval translations) where DCO has LT.doc (all 5)
  Medieval West (8-18, 869-1517):
    - Latin originals — 3 as LT.pdf (Lateran IV, Basel-Florence, Lateran V),
      8 as LT.doc (Const IV, Lat I-III, Lyon I-II, Vienne, Constance)
  Trent (19, 1545-63):
    - Single big LT.pdf containing all 25 sessions — split locally by SESSIO marker

Tools:
  - pdftotext -enc UTF-8 -layout  (for PDFs, preserves Greek polytonic & layout)
  - antiword                       (for .doc files — clean Latin extraction)

Output:
  data/creeds/ecumenical-councils/early/early-NN-{greek|latin}.txt
  data/creeds/ecumenical-councils/medieval/medieval-NN-latin.txt
  data/creeds/ecumenical-councils/trent/trent-NN-latin.txt

Idempotent: re-runs overwrite outputs. Use --council 3 to scrape one only.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EARLY_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "early")
MED_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "medieval")
TRENT_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "trent")

DCO_BASE = "https://www.documentacatholicaomnia.eu/03d/"

# Source registry: (council_num, lang, output_file_basename, remote_filename)
#   lang ∈ {"greek", "latin"}; remote_filename is the DCO 03d/ path filename
SOURCES: list[tuple[int, str, str, str, str]] = [
    # Early Eastern (3-7) — Greek where available + Latin from DCO
    # (council, lang, out_dir_token, out_basename, dco_filename)
    (3, "latin", "early", "early-03-latin",
     "0431-0431,_Concilium_Ephesenum,_Documenta_Omnia,_LT.doc"),
    (4, "greek", "early", "early-04-greek",
     "0451-0451,_Concilium_Chalcedonense,_Documenta_Omnia,_GR.pdf"),
    (4, "latin", "early", "early-04-latin",
     "0451-0451,_Concilium_Chalcedonense,_Documenta_Omnia,_LT.doc"),
    (5, "latin", "early", "early-05-latin",
     "0553-0553,_Concilium_Constantinopolitanum_II,_Documenta,_LT.doc"),
    (6, "latin", "early", "early-06-latin",
     "0680-0680,_Concilium_Constantinopolitanum_III,_Documenta,_LT.doc"),
    (7, "greek", "early", "early-07-greek",
     "0787-0787,_Concilium_Nicaenum_II,_Documenta,_GR.pdf"),
    (7, "latin", "early", "early-07-latin",
     "0787-0787,_Concilium_Nicaenum_II,_Documenta,_LT.doc"),

    # Medieval (8-18) — Latin only; 3 are PDFs, 8 are DOCs
    (8, "latin", "medieval", "medieval-08-latin",
     "0869-0870,_Concilium_Constantinopolitanum_IV,_Documenta,_LT.doc"),
    (9, "latin", "medieval", "medieval-09-latin",
     "1123-1123,_Concilium_Lateranum_I,_Documenta,_LT.doc"),
    (10, "latin", "medieval", "medieval-10-latin",
     "1139-1139,_Concilium_Lateranum_II,_Documenta,_LT.doc"),
    (11, "latin", "medieval", "medieval-11-latin",
     "1179-1179,_Concilium_Lateranum_III,_Documenta,_LT.doc"),
    (12, "latin", "medieval", "medieval-12-latin",
     "1215-1215,_Concilium_Lateranense_IIII,_Documenta,_LT.pdf"),
    (13, "latin", "medieval", "medieval-13-latin",
     "1245-1245,_Concilium_Lugdunense_I,_Documenta,_LT.doc"),
    (14, "latin", "medieval", "medieval-14-latin",
     "1274-1274,_Concilium_Lugdunense_II,_Documenta,_LT.doc"),
    (15, "latin", "medieval", "medieval-15-latin",
     "1311-1312,_Concilium_Viennense,_Documenta,_LT.doc"),
    (16, "latin", "medieval", "medieval-16-latin",
     "1414-1414,_Concilium_Constantiense,_Documenta,_LT.doc"),
    (17, "latin", "medieval", "medieval-17-latin",
     "1431-1431,_Concilium_Basileense,_Documenta_Omnia,_LT.pdf"),
    (18, "latin", "medieval", "medieval-18-latin",
     "1512-1512,_Concilium_Lateranum_V,_Documenta_Omnia,_LT.pdf"),

    # Trent — single big PDF, split locally
    (19, "latin", "trent", "_trent_full_latin",
     "1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf"),
]

OUT_DIRS = {"early": EARLY_DIR, "medieval": MED_DIR, "trent": TRENT_DIR}


def http_get(url: str, dest: str) -> int:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0 (creeds-originals)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        return os.path.getsize(dest)
    except urllib.error.HTTPError as e:
        return -e.code
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"  ! download error: {e}")
        return -1


def extract_pdf(pdf_path: str) -> str:
    """Run pdftotext -enc UTF-8 -layout (preserves Greek polytonic)."""
    out_path = pdf_path + ".txt"
    cp = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", "-layout", pdf_path, out_path],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        print(f"  ! pdftotext failed: {cp.stderr.strip()}")
        return ""
    with open(out_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_doc(doc_path: str) -> str:
    """Run antiword to extract text from .doc — clean plain Latin output."""
    cp = subprocess.run(
        ["antiword", "-w", "0", doc_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if cp.returncode != 0:
        print(f"  ! antiword failed: {cp.stderr.strip()}")
        return ""
    return cp.stdout


def clean_dco_intro(text: str, language: str) -> str:
    """Strip the DCO Italian intro + footer noise present in every PDF.

    DCO PDFs from internetsv.info start with an Italian-language introduction,
    then a "Fontes:" line, then a copyright disclaimer, then finally the actual
    Latin/Greek text. We strip everything up to the actual title repetition.
    """
    if not text:
        return text

    # Common boundary markers — actual text starts after one of these
    # (1) Repeated title (e.g. "CONCILIUM TRIDENTINUM\n  Canones et Decreta")
    # (2) SESSIO I marker
    # (3) Κανὼν A' (Greek canon 1)
    # (4) "Concilia oecumenica et generalia"
    cutoff_patterns = [
        # Skip past the noise; find a real start marker
        r"\n[ \t]*SESSIO\s+I\b",
        r"\n[ \t]*CANON\s+I\b",
        r"\nΚανὼν\s+[ΑA]\b",
        r"\nΚανὼν\s+α[΄'']?\b",
        # Title doubled (intro then again as start of actual text)
        r"CONCILIUM\s+\w+\b[^\n]*\n\s+\w+",
    ]
    for pat in cutoff_patterns:
        m = re.search(pat, text)
        if m and m.start() > 200:  # Only strip if a real intro precedes
            # back off to start of paragraph
            start = m.start()
            # find preceding empty line
            preceding_break = text.rfind("\n\n", 0, start)
            if preceding_break > 200:
                text = text[preceding_break:].lstrip()
                break

    # Strip footer "www.internetsv.info" page markers throughout
    text = re.sub(r"\n[ \t]*www\.internetsv\.info[ \t]*\n", "\n", text)
    # Strip page numbers (lonely small ints on their own line)
    text = re.sub(r"\n[ \t]{20,}\d{1,3}[ \t]*\n", "\n", text)

    return text.strip() + "\n"


def split_trent_sessions(full_text: str) -> dict[int, str]:
    """Split the Trent omnibus Latin PDF text into 25 session bodies.

    Marker is `SESSIO {ROMAN}` at start of line. Roman = I..XXV.
    """
    roman_to_int = {}
    romans = []
    for n in range(1, 26):
        # Map standard roman numerals
        roman_to_int[_to_roman(n)] = n
        romans.append(_to_roman(n))

    # Find all session markers
    # Match SESSIO XXV first to avoid SESSIO V matching SESSIO XV/XXV
    sorted_romans = sorted(romans, key=len, reverse=True)
    pattern = r"^[ \t]*SESSIO\s+(" + "|".join(sorted_romans) + r")\s*$"
    matches = list(re.finditer(pattern, full_text, re.MULTILINE))

    sections: dict[int, str] = {}
    for i, m in enumerate(matches):
        n = roman_to_int[m.group(1)]
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = full_text[start:end].strip()
        # If we already saw this session (e.g. duplicate marker), append
        if n in sections:
            sections[n] += "\n\n" + body
        else:
            sections[n] = body
    return sections


def _to_roman(n: int) -> str:
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def write_text(path: str, content: str, header: str | None = None) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = ""
    if header:
        payload += header + "\n\n"
    payload += content.strip() + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(payload)


def process_one(council: int, lang: str, out_dir_token: str, out_basename: str,
                dco_fname: str, *, tmp_root: str, dry: bool = False) -> bool:
    print(f"[{council:02d} {lang:5s}] {dco_fname}")
    if dry:
        return True

    url = DCO_BASE + dco_fname
    suffix = ".pdf" if dco_fname.lower().endswith(".pdf") else ".doc"
    raw_path = os.path.join(tmp_root, f"council_{council:02d}_{lang}{suffix}")
    size = http_get(url, raw_path)
    if size <= 0:
        print(f"  ! HTTP {size} — skip")
        return False
    print(f"  ✓ downloaded {size} bytes")

    if suffix == ".pdf":
        text = extract_pdf(raw_path)
    else:
        text = extract_doc(raw_path)

    if not text or len(text.strip()) < 100:
        print(f"  ! extracted text too short ({len(text)} chars)")
        return False

    # Strip DCO Italian intro noise for PDF sources
    if suffix == ".pdf":
        text = clean_dco_intro(text, lang)

    out_dir = OUT_DIRS[out_dir_token]

    # Special case: Trent — split into 25 session files
    if out_basename == "_trent_full_latin":
        sections = split_trent_sessions(text)
        print(f"  ✓ split into {len(sections)} sessions")
        for n in range(1, 26):
            body = sections.get(n)
            session_path = os.path.join(out_dir, f"trent-{n:02d}-latin.txt")
            if not body:
                header = f"# Session {n} 拉丁版本未在 DCO Alberigo 全集中標出獨立 SESSIO 標頭"
                write_text(session_path, "（待人工切分；參 trent-_full-latin.txt）", header=header)
            else:
                header = (f"# Trent Session {n} — Latin\n"
                          f"# Source: Documenta Catholica Omnia (DCO) / Alberigo, Conciliorum "
                          f"Oecumenicorum Decreta, 1973")
                write_text(session_path, body, header=header)
        # Also write the full text for reference
        full_path = os.path.join(out_dir, "_trent-full-latin.txt")
        write_text(full_path, text, header="# Trent — Full Latin Omnibus (DCO/Alberigo 1973)")
        return True

    # Normal case: single file output
    out_path = os.path.join(out_dir, f"{out_basename}.txt")
    council_name_hint = dco_fname.split(",")[1].strip().replace("_", " ")
    header = (
        f"# {council_name_hint} — {'希臘原文' if lang == 'greek' else '拉丁文本'}\n"
        f"# Source: Documenta Catholica Omnia\n"
        f"# Remote: {dco_fname}"
    )
    write_text(out_path, text, header=header)
    print(f"  ✓ wrote {out_path}")
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--council", type=int, default=None,
                   help="Only scrape a single council number (3-19)")
    p.add_argument("--lang", choices=["greek", "latin"], default=None,
                   help="Only scrape one language")
    p.add_argument("--dry", action="store_true", help="Print plan only, no IO")
    args = p.parse_args()

    targets = SOURCES
    if args.council:
        targets = [t for t in targets if t[0] == args.council]
    if args.lang:
        targets = [t for t in targets if t[1] == args.lang]

    if not targets:
        print("No targets matched.")
        return 1

    tmp_root = tempfile.mkdtemp(prefix="dco_originals_")
    print(f"Working dir: {tmp_root}\nTotal targets: {len(targets)}\n")

    ok = 0
    fail = 0
    for (council, lang, out_dir_token, out_basename, dco_fname) in targets:
        try:
            if process_one(council, lang, out_dir_token, out_basename, dco_fname,
                           tmp_root=tmp_root, dry=args.dry):
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  !! exception: {e}")
            fail += 1
        time.sleep(0.3)  # polite

    print(f"\n=== Done: {ok} ok, {fail} fail (tmp: {tmp_root}) ===")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
