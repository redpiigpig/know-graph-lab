"""
Merge subsection chunks back into their parent chapter chunk.

GENERAL VERSION (vs the one-shot c:/tmp/merge_calvin_subsections.py):
  Works on any book where the EPUB emitted one spine-doc per subsection,
  resulting in chunks whose first heading is DEEPER than the previous
  chunk's first heading (e.g. prev=h2 chapter, cur=h3 subsection).

Detection rule (general):
  For each chunk i > 0:
    cur_first_heading_level > prev_first_heading_level
    AND prev was a real chapter (not front-matter like 封面/目錄)
    → merge cur into prev (drop the cur chunk; renumber)

This catches both:
  - Calvin (NPNF1, NPNF2, ANF, IVP ACCS …): prev=h2 chapter, cur=h3 subsection
  - Lakoff 肉身哲學, 中國儒學史 etc.: prev=h3 chapter, cur=h4 subsection

The merged chunk's content keeps the subsection's heading inline (### / ####)
so the reader still shows section breaks via h3/h4 styling, and `loadToc()`
emits anchor ids for them via the existing `sec-{chunk}-{seq}` mechanism.

Usage:
  python scripts/merge_subsection_chunks.py <ebook_id> --dry-run
  python scripts/merge_subsection_chunks.py <ebook_id>
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

FRONTMATTER_TITLES = {
    "封面", "出版資訊", "出版說明", "目錄", "目　錄", "目　　錄",
    "版權頁", "版權資訊", "扉頁",
}
# Volume dividers — same regex as server/utils/ebook-chunks.ts. Chunks
# whose chapter_path is just `第N卷/編/冊/集/篇/部/部分` are group headers,
# not real chapters. They must NOT absorb subsequent chapter chunks during
# subsection merge.
VOLUME_DIVIDER_RE = re.compile(r"^第[一二三四五六七八九十百千]+(?:卷|編|冊|集|篇|部|部分)$")
HEAD_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)


def load_env() -> None:
    envf = Path(__file__).parent.parent / ".env"
    for line in envf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        os.environ.setdefault(k.strip(), v)


def first_head_level(content: str) -> int | None:
    m = HEAD_RE.search(content or "")
    return len(m.group(1)) if m else None


def is_frontmatter(chapter_path: str) -> bool:
    return (chapter_path or "").strip() in FRONTMATTER_TITLES


def is_volume_divider(chapter_path: str) -> bool:
    collapsed = (chapter_path or "").replace(" ", "").replace("　", "").strip()
    return bool(VOLUME_DIVIDER_RE.match(collapsed))


def run(ebook_id: str, dry_run: bool) -> None:
    load_env()
    jsonl_dir = Path(os.environ.get("EBOOK_CHUNKS_DIR", "G:/我的雲端硬碟/資料/知識圖工作室/_chunks"))
    jsonl_path = jsonl_dir / f"{ebook_id}.jsonl"
    if not jsonl_path.exists():
        print(f"JSONL not found: {jsonl_path}")
        sys.exit(1)

    lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    chunks = [json.loads(l) for l in lines]
    print(f"Before merge: {len(chunks)} chunks")

    merged: list[dict] = [chunks[0]]
    merge_log: list[tuple[int, str]] = []
    for i in range(1, len(chunks)):
        c = chunks[i]
        cur_lvl = first_head_level(c["content"])
        prev = merged[-1]
        prev_lvl = first_head_level(prev["content"])
        # Merge if current chunk's first heading is DEEPER than previous
        # AND previous chunk is not a front-matter (don't fold subsections
        # under 封面/出版資訊).
        if (
            cur_lvl is not None
            and prev_lvl is not None
            and cur_lvl > prev_lvl
            and not is_frontmatter(prev.get("chapter_path", ""))
            and not is_volume_divider(prev.get("chapter_path", ""))
        ):
            prev["content"] = prev["content"].rstrip() + "\n\n" + c["content"].lstrip()
            merge_log.append((i, c.get("chapter_path", "")))
            continue
        merged.append(c)

    print(f"After merge:  {len(merged)} chunks (collapsed {len(merge_log)} subsection chunks)")
    if merge_log:
        print("Sample merged subsection titles:")
        for idx, title in merge_log[:10]:
            print(f"  was #{idx}: {title[:60]}")
        if len(merge_log) > 10:
            print(f"  ... +{len(merge_log)-10} more")

    if dry_run:
        print("\n(dry run — JSONL + DB not modified)")
        return

    # Renumber chunk_index
    for i, c in enumerate(merged):
        c["chunk_index"] = i

    tmp_path = jsonl_path.with_suffix(".jsonl.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        for c in merged:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    bak = jsonl_path.with_suffix(".jsonl.bak_pre_merge")
    if bak.exists():
        bak.unlink()
    jsonl_path.rename(bak)
    tmp_path.rename(jsonl_path)
    print(f"JSONL written. Backup: {bak}")

    h = {
        "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
        "Content-Type": "application/json",
    }
    base = os.environ["SUPABASE_URL"] + "/rest/v1"
    r = requests.delete(f"{base}/ebook_chunks?ebook_id=eq.{ebook_id}", headers=h, timeout=60)
    print(f"DELETE ebook_chunks: {r.status_code}")

    batch_size = 50
    inserted = 0
    for i in range(0, len(merged), batch_size):
        batch = merged[i : i + batch_size]
        rows = [
            {
                "ebook_id": ebook_id,
                "chunk_index": c["chunk_index"],
                "chunk_type": c.get("chunk_type", "chapter"),
                "page_number": c.get("page_number"),
                "chapter_path": c.get("chapter_path"),
                "content": (c["content"] or "")[:200],
                "char_count": len(c.get("content") or ""),
            }
            for c in batch
        ]
        r = requests.post(
            f"{base}/ebook_chunks",
            headers={**h, "Prefer": "return=minimal"},
            json=rows,
            timeout=30,
        )
        if r.status_code not in (200, 201, 204):
            print(f"INSERT batch {i} failed: {r.status_code} {r.text[:200]}")
            sys.exit(1)
        inserted += len(batch)
    print(f"Inserted {inserted} chunk previews")

    r = requests.patch(
        f"{base}/ebooks?id=eq.{ebook_id}",
        headers={**h, "Prefer": "return=minimal"},
        json={"chunk_count": len(merged), "total_pages": len(merged)},
        timeout=15,
    )
    print(f"UPDATE ebooks count: {r.status_code}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    run(args.ebook_id, args.dry_run)


if __name__ == "__main__":
    main()
