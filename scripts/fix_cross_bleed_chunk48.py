"""One-off fix for ANF Vol 1 chunk 48 (帕皮亞殘篇) cross-bleed.

The CCEL EPUB packaged the「Introductory Note to the Writings of Justin
Martyr」content INSIDE the Papias Fragments HTML file. The translator
treated it as part of Papias; the T2 sweep then over-corrected the h3
heading (which should have been「殉道者猶斯定著作導讀」) to「帕皮亞殘篇」.

This script splits chunk 48 at the bleed boundary:
  - Keep in chunk 48: everything up to and INCLUDING (1764) footnote
  - Move to chunk 49 head: 「殉道者猶斯定著作導讀」 heading + biographical
    body + (1765-1767) footnotes
  - Renumber footnote dict keys; merge page_numbers

Splits both `content` (Chinese) and `source_text` (English) at matching
boundaries.
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

EBOOK_ID = "c98d358d-7066-4691-a896-b7232707b0db"
CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Boundary markers — these uniquely identify the start of the bleed
# content in each language. Lifted from the actual chunk dump.
ZH_BLEED_MARKER = "### 帕皮亞殘篇\n[ 公元 110"
EN_BLEED_MARKER = "### Introductory Note to the Writings of"
# The corrected ZH heading once we relocate the section.
ZH_CORRECTED_HEADING = "### 殉道者猶斯定著作導讀"


def main():
    jsonl = CHUNKS_DIR / f"{EBOOK_ID}.jsonl"
    chunks = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l]
    c48, c49 = chunks[48], chunks[49]
    assert c48["chapter_path"] == "帕皮亞殘篇", c48["chapter_path"]
    assert "猶斯定第一護教辭" in c49["chapter_path"], c49["chapter_path"]

    # ── Locate split point in ZH content ──
    zh_full = c48["content"]
    zh_idx = zh_full.find(ZH_BLEED_MARKER)
    assert zh_idx > 0, "ZH bleed marker not found — already fixed?"
    # Trim trailing whitespace AND any trailing separator before the bleed,
    # since that separator was "closing" the (1764) footnote section.
    zh_left = zh_full[:zh_idx].rstrip()
    # If the last block is the toggle separator, drop it — chunk 48 no longer
    # needs an open-and-close pair after this point.
    zh_left = re.sub(r"\n*[—－\-]{15,}\s*$", "", zh_left).rstrip()
    # The bleed section: rewrite the heading line
    zh_right = zh_full[zh_idx:]
    zh_right = zh_right.replace("### 帕皮亞殘篇\n", ZH_CORRECTED_HEADING + "\n", 1)

    # ── Locate split point in EN source_text ──
    en_full = c48.get("source_text", "") or ""
    en_idx = en_full.find(EN_BLEED_MARKER)
    if en_idx < 0:
        # Variant: heading on one line
        en_idx = en_full.find("Justin Martyr\n\n[ a.d. 110")
    assert en_idx > 0, "EN bleed marker not found"
    en_left = en_full[:en_idx].rstrip()
    en_left = re.sub(r"\n*[—－\-]{15,}\s*$", "", en_left).rstrip()
    en_right = en_full[en_idx:]

    # ── Footnotes that belong to the bled section ──
    # Numerically: (1765), (1766), (1767) are Justin intro footnotes.
    # Move from c48.footnotes → c49.footnotes (prepend; keep c49 existing).
    BLEED_FN_NUMS = {1765, 1766, 1767}
    c48_fn = dict(c48.get("footnotes") or {})
    c49_fn = dict(c49.get("footnotes") or {})
    moved_fn = {}
    for k in list(c48_fn.keys()):
        if int(k) if str(k).isdigit() else -1 in BLEED_FN_NUMS:
            moved_fn[k] = c48_fn.pop(k)
    # Combine with c49's existing footnotes; new numbers don't collide
    # (c49 starts at 1768+).
    c49_fn_new = {**moved_fn, **c49_fn}

    # ── Page numbers ──
    # Find {{p:N}} markers in the moved section and shift them from c48 to c49.
    moved_pages = sorted({int(m.group(1))
                          for m in re.finditer(r"\{\{p:(\d+)\}\}", zh_right)})
    c48_pages = sorted(set(c48.get("page_numbers") or []) - set(moved_pages))
    c49_pages = sorted(set(c49.get("page_numbers") or []) | set(moved_pages))

    # ── Apply ──
    c48["content"] = zh_left
    c48["source_text"] = en_left
    c48["footnotes"] = c48_fn if c48_fn else None
    c48["page_numbers"] = c48_pages
    if c48_pages:
        c48["page_number"] = c48_pages[0]

    # Prepend the bleed section to c49 with a separator paragraph between
    c49["content"] = zh_right.rstrip() + "\n\n" + c49["content"].lstrip()
    c49["source_text"] = en_right.rstrip() + "\n\n" + (c49.get("source_text") or "").lstrip()
    c49["footnotes"] = c49_fn_new if c49_fn_new else None
    c49["page_numbers"] = c49_pages
    if c49_pages:
        c49["page_number"] = c49_pages[0]

    print(f"chunk 48: {len(zh_full)} → {len(zh_left)} chars ({len(zh_full)-len(zh_left)} moved)")
    print(f"chunk 49: prepended {len(zh_right)} chars")
    print(f"  fn moved: {sorted(moved_fn.keys())}")
    print(f"  pages moved: {moved_pages}")

    # ── Write ──
    with open(jsonl, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"✓ wrote {jsonl.name} ({jsonl.stat().st_size // 1024} KB)")

    # Push R2 + refresh just the 2 affected previews
    se.push_to_r2(EBOOK_ID, jsonl)
    print("✓ pushed R2")
    for c in (c48, c49):
        body = {
            "ebook_id": EBOOK_ID,
            "chunk_index": c["chunk_index"],
            "chunk_type": c.get("chunk_type", "chapter"),
            "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": (c.get("content") or "")[:200],
            "char_count": len(c.get("content") or ""),
        }
        # Upsert via PATCH-then-POST fallback
        r = requests.delete(
            f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{EBOOK_ID}&chunk_index=eq.{c['chunk_index']}",
            headers=H_GET, timeout=30)
        requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=body, timeout=30)
    print("✓ refreshed previews for chunks 48 & 49")


if __name__ == "__main__":
    main()
