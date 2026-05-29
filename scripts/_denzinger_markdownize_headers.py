"""
Convert in-content section headers to Markdown headings.

After consolidation a DH entry chunk's `content` field often contains
prose interleaved with section headers that should be visually distinct:

    我信天主父，全能的父…       ← DH 6 中譯

    分成部分的信經              ← group label
    I. 分成「聖三」三部分的信經    ← Roman section
    撤開後期教會的進展問題不談…    ← Roman intro
    A. 西方教會的信經格式        ← letter sub-section
    宗徒信經                   ← group within letter
    所謂「宗徒信經」彼稱許多世紀…  ← group intro
    10  羅馬司祭希波巴托斯…       ← next DH heading

We promote these one-liner header lines into Markdown `##` / `###`
headings so reader renderMarkdown gives them h2/h3 styling, visually
separating them from the surrounding prose.

Patterns promoted:
    - 「第一部分：信經」「第二部分：教會訓導文獻」 → `#`
    - 「Ⅰ. xxx」「I. xxx」                    → `##`
    - 「A. xxx」「B. xxx」                    → `###`
    - Known group labels from entries.json (簡單的信經 / 宗徒信經 / 洗禮
      信經問答短式 / 地方性的信經 / 東方教伊拿集中的信經 / 分成部分的信經
      / 等) → `##`

Run AFTER `_denzinger_strip_internal_pages.py`.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import CHUNKS_DIR, URL, H, push_to_r2  # noqa: E402
import requests  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
MAIN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.jsonl"
PRE_MD_BACKUP = CHUNKS_DIR / f"{BOOK_ID}.jsonl.premarkdown.bak"
TOC_DIR = Path(__file__).parent / "_denzinger_toc"


PART_RE = re.compile(r"^第[一二三四五]部分[：:]\s*(.+)$")
# Allow both ascii Roman (I. II. III.) and unicode Roman (Ⅰ. Ⅱ.).
ROMAN_RE = re.compile(
    r"^(I{1,3}|IV|V|VI{0,3}|IX|X|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ])\.\s+(.+)$"
)
LETTER_RE = re.compile(r"^([A-Z])\.\s+(.+)$")


def load_group_labels() -> set[str]:
    """Collect known group labels from entries.json: any entry whose
    `volume` is a short bare label like 「宗徒信經」 or 「簡單的信經」 —
    NOT a full pope/council header — gets registered."""
    p = TOC_DIR / "entries.json"
    if not p.exists():
        return set()
    entries = json.loads(p.read_text(encoding="utf-8"))
    out: set[str] = set()
    for e in entries:
        v = (e.get("volume") or "").strip()
        # Skip pope/council/year tags
        if not v or len(v) > 18 or "：" in v or "(" in v or "年" in v:
            continue
        if "大公會議" in v or "地區會議" in v:
            continue
        if v.startswith("Ⅰ") or v.startswith("I.") or re.match(r"^[A-Z]\.", v):
            continue
        if v.startswith("第") and "部分" in v:
            continue
        out.add(v)
    # Add a couple of labels we observed in OCR'd prose that don't appear
    # as entries.json volumes but ARE used as inline section markers.
    out.update({
        "分成部分的信經",
        "宗徒信經",
        "洗禮信經問答短式",
        "地方性的信經",
        "東方教會的信經格式",
        "西方教會的信經格式",
        "簡單的信經",
        "東方教伊拿集中的信經",
    })
    return out


def markdownize(text: str, group_labels: set[str]) -> tuple[str, int]:
    """Walk lines, promoting matched header lines to Markdown headings.
    A line is a candidate only if it's standalone (the surrounding lines
    are blank or NOT continuation prose). We treat ANY single short line
    matching a known pattern as a header — false positives are rare in
    Denzinger content."""
    if not text:
        return text, 0
    lines = text.split("\n")
    promoted = 0
    out: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            out.append(ln)
            continue
        m = PART_RE.match(stripped)
        if m:
            out.append(f"# {stripped}")
            promoted += 1
            continue
        m = ROMAN_RE.match(stripped)
        if m and len(stripped) <= 40:
            out.append(f"## {stripped}")
            promoted += 1
            continue
        m = LETTER_RE.match(stripped)
        if m and len(stripped) <= 30:
            out.append(f"### {stripped}")
            promoted += 1
            continue
        if stripped in group_labels:
            out.append(f"## {stripped}")
            promoted += 1
            continue
        out.append(ln)
    return "\n".join(out), promoted


def load_chunks() -> list[dict]:
    out: list[dict] = []
    with MAIN_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def push_db(chunks: list[dict]) -> None:
    print("Patching DB rows…")
    import time
    t0 = time.time()
    n = 0
    for c in chunks:
        idx = c["chunk_index"]
        payload = {"content": c.get("content") or ""}
        r = requests.patch(
            f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{BOOK_ID}&chunk_index=eq.{idx}",
            headers=H,
            json=payload,
            timeout=60,
        )
        if r.status_code in (200, 204):
            n += 1
        else:
            print(f"  ⚠ row {idx} → {r.status_code}: {r.text[:120]}")
        if n and n % 100 == 0:
            print(f"  patched {n}/{len(chunks)} ({time.time()-t0:.0f}s)")
    print(f"✓ patched {n}/{len(chunks)} DB rows in {time.time()-t0:.0f}s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-db", action="store_true")
    ap.add_argument("--no-r2", action="store_true")
    args = ap.parse_args()

    group_labels = load_group_labels()
    print(f"Loaded {len(group_labels)} group labels")

    chunks = load_chunks()
    total_promoted = 0
    for c in chunks:
        new_zh, p = markdownize(c.get("content") or "", group_labels)
        if p:
            c["content"] = new_zh
            total_promoted += p
    print(f"Promoted {total_promoted} lines to Markdown headings")

    if args.dry_run:
        print("\n─ Sample chunk 7 (DH 6) content head ─")
        for c in chunks:
            if c["chunk_index"] == 7:
                print((c.get("content") or "")[:1500])
                break
        return 0

    if not PRE_MD_BACKUP.exists():
        shutil.copyfile(MAIN_JSONL, PRE_MD_BACKUP)
        print(f"✓ Backed up → {PRE_MD_BACKUP.name}")

    with MAIN_JSONL.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"✓ Wrote main JSONL ({len(chunks)} chunks)")

    if not args.no_r2:
        push_to_r2(BOOK_ID, MAIN_JSONL)
        print("✓ R2 push ok")

    if not args.no_db:
        push_db(chunks)

    return 0


if __name__ == "__main__":
    sys.exit(main())
