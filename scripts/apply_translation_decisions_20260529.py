"""Apply 2026-05-29 translation decisions across glossary + chunks.

User-final 譯名決策清單：

Latin tradition (Roman Catholic 西方傳統)：
  Clemens (Roman Clement)   羅馬的革利免 → 羅馬的克勉
  Gregorius (Pope Gregory I) 大額我略 → 額我略 (dedupe duplicate)

Greek tradition (希臘東方教父)：
  Κλήμης (Alex. Clement)    亞歷山卓的革利免 (KEEP)
  Γρηγόριος (Naz.)         拿先斯的格列高理 → 拿先斯的格列高里 (「理」→「里」)
  其他 Gregory 一致改「里」: 尼撒/帕拉馬/西奈
  奇蹟行者格列高利 (Thaumaturgus) → 奇蹟行者格列高里 (一致)
  Κύριλλος (Cyril Alex.)   亞歷山卓的西里爾 → 亞歷山卓的區利羅
  Cyril of Jerusalem       西瑞爾 → 耶路撒冷的區利羅
  Βασίλειος (Basil)        大巴西略 → 凱撒利亞的巴西流
  巴西略 (any context)     → 巴西流

Armenian tradition：
  Գրիգոր (Gregory Illum.)  ADD 啟蒙者格里高爾

Syriac tradition：
  Aphrem (Ephrem)          敘利亞的厄弗冷 (KEEP, 已對)
  Aphrahaṭ                 波斯智者亞弗拉哈特 → 波斯賢士阿弗拉哈特
  亞弗拉哈特               → 阿弗拉哈特
  Ishaq (Isaac Nineveh)    ADD 尼尼微的伊沙克
  Tatian                   他提安 (KEEP, dedupe duplicate)

Replacement scope per user's "全卷都改" + "連 content 內文也改"：
  - Vol 1 + Vol 9 含 Roman Clement → 革利免 → 克勉 (作品名 + parent + volume + content)
  - Vol 2 亞歷山卓的革利免 → 不動 (保留 革利免)
  - 其他名稱替換 (巴西略/西里爾/格列高理/亞弗拉哈特) 全卷 search-replace
  - Vol 8 後續處理 (翻譯尚未完成)

Run order:
  1. Update DB theologians (name_recommended)
  2. Add Isaac of Nineveh + Gregory the Illuminator
  3. Dedupe duplicates (大額我略, 他提安)
  4. Walk chunks (Vol 1-9) → update parent_volume, volume, chapter_path, content
  5. Push R2 + refresh previews
  6. Update scripts (backfill_parent_volume.PARENT_RULES, consolidate_by_ncx
     PARENT_CN_FALLBACK + LETTER_CN_LABELS) — done manually after

Usage:
    python scripts/apply_translation_decisions_20260529.py            # apply
    python scripts/apply_translation_decisions_20260529.py --dry-run  # report
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

# Vol-id constants
VOL1 = "c98d358d-7066-4691-a896-b7232707b0db"
VOL2 = "4e3d16fc-ef4f-420f-a3ec-56e2e92d659f"
VOL3 = "364dac2e-410f-4906-be63-8bb86b4865ee"
VOL4 = "904661d3-16fc-4f37-bb04-f7c4aa7671e9"
VOL5 = "0e08c662-540b-4186-b250-9bca0cfe1002"
VOL6 = "dffaae40-e088-41c1-ab7f-9b96f9249661"
VOL7 = "75d8aae0-7431-4be9-baee-c57d26599653"
VOL9 = "72cb2f94-da86-4e16-bbbd-4cf3391031df"

# Vol 1 + Vol 9 contain Roman Clement (1st/2nd Clement, Epistles of Clement)
ROMAN_CLEMENT_VOLS = {VOL1, VOL9}

# ── DB updates: (current name_recommended, new name_recommended) ──
DB_NAME_UPDATES = [
    ("羅馬的革利免",                  "羅馬的克勉"),
    ("大額我略",                      "額我略"),
    ("拿先斯的格列高理",              "拿先斯的格列高里"),
    ("尼撒的格列高理",                "尼撒的格列高里"),
    ("帕拉馬的格列高理",              "帕拉馬的格列高里"),
    ("西奈的格列高理",                "西奈的格列高里"),
    ("奇蹟行者格列高利",              "奇蹟行者格列高里"),
    ("亞歷山卓的西里爾",              "亞歷山卓的區利羅"),
    ("西瑞爾",                        "耶路撒冷的區利羅"),
    ("大巴西略",                      "凱撒利亞的巴西流"),
    ("波斯智者亞弗拉哈特",            "波斯賢士阿弗拉哈特"),
]

# New entries to add (en, original, zh)
NEW_ENTRIES = [
    ("Gregory the Illuminator (apostle of Armenia)", "Գրիգոր Lusavorich",
     "啟蒙者格里高爾"),
    ("Isaac of Nineveh (Isaac the Syrian)", "ܐܝܣܚܩ Ishaq",
     "尼尼微的伊沙克"),
]

# Chunk-level replacements (applied to volume / chapter_path / content)
# Order matters: longer / more-specific first
COMMON_REPLACEMENTS = [
    # Gregory family — 「理」→「里」(consistent across all)
    ("拿先斯的格列高理", "拿先斯的格列高里"),
    ("尼撒的格列高理",   "尼撒的格列高里"),
    ("帕拉馬的格列高理", "帕拉馬的格列高里"),
    ("西奈的格列高理",   "西奈的格列高里"),
    ("奇蹟行者格列高利", "奇蹟行者格列高里"),
    # Pope Gregory — drop 大
    ("大額我略", "額我略"),
    # Cyril
    ("亞歷山卓的西里爾", "亞歷山卓的區利羅"),
    # Basil — 大巴西略 / 巴西略 → 凱撒利亞的巴西流 / 巴西流
    ("大巴西略", "凱撒利亞的巴西流"),
    ("巴西略",   "巴西流"),
    # Aphrahat
    ("波斯智者亞弗拉哈特", "波斯賢士阿弗拉哈特"),
    ("亞弗拉哈特",         "阿弗拉哈特"),
]

# Roman Clement only — 革利免 → 克勉. Applied to Vol 1 + Vol 9 only.
ROMAN_CLEMENT_REPLACEMENTS = [
    ("羅馬的革利免",         "羅馬的克勉"),
    ("革利免致哥林多人前書", "克勉致哥林多人前書"),
    ("革利免致哥林多人後書", "克勉致哥林多人後書"),
    ("革利免書信集",         "克勉書信集"),
    ("革利免後書",           "克勉後書"),
    ("革利免前書",           "克勉前書"),
    # NB: 「革利免」 standalone — handled in code with context guards
]


def apply_replacements(text: str, replacements: list[tuple[str, str]]) -> str:
    """Apply ordered list of (old, new) string replacements."""
    if not text:
        return text
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def process_chunk_field(s: str, ebook_id: str) -> str:
    """Apply COMMON_REPLACEMENTS + ROMAN_CLEMENT_REPLACEMENTS (if applicable)
    to a string field (volume / chapter_path / content)."""
    if not s:
        return s
    s = apply_replacements(s, COMMON_REPLACEMENTS)
    if ebook_id in ROMAN_CLEMENT_VOLS:
        s = apply_replacements(s, ROMAN_CLEMENT_REPLACEMENTS)
        # Standalone 革利免 → 克勉 only in Roman Clement vols
        # (Vol 1 全是使徒教父含 1st/2nd Clement；Vol 9 含 The Epistles of
        # Clement section — 兩本都不含亞歷山卓的革利免)
        s = re.sub(r"革利免", "克勉", s)
    return s


# ── DB ────────────────────────────────────────────────────────────────

def update_db_names(dry_run: bool):
    updated = 0
    for old, new in DB_NAME_UPDATES:
        r = requests.get(f"{URL}/rest/v1/theologians?select=id,name_english,name_recommended"
                         f"&name_recommended=eq.{old}", headers=H_GET, timeout=30)
        r.raise_for_status()
        rows = r.json()
        if not rows:
            print(f"  - {old}: no match")
            continue
        for row in rows:
            print(f"  ✏ {old:25s} → {new:25s} (id={row['id'][:8]}.. en={row['name_english']})")
            if not dry_run:
                r2 = requests.patch(f"{URL}/rest/v1/theologians?id=eq.{row['id']}",
                                    headers=H_JSON,
                                    json={"name_recommended": new}, timeout=30)
                if r2.status_code in (200, 204):
                    updated += 1
                else:
                    print(f"    !! PATCH {r2.status_code}: {r2.text[:200]}", file=sys.stderr)
    print(f"\nDB updated: {updated} rows")


def add_new_entries(dry_run: bool):
    for en, original, zh in NEW_ENTRIES:
        r = requests.get(f"{URL}/rest/v1/theologians?select=id"
                         f"&name_english=eq.{en}", headers=H_GET, timeout=30)
        if r.json():
            print(f"  • already exists: {en}")
            continue
        print(f"  + ADD: {zh:20s}  ({en})")
        if not dry_run:
            r2 = requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON,
                               json=[{
                                   "name_english": en,
                                   "name_original": original,
                                   "name_latin_std": en,
                                   "name_recommended": zh,
                                   "first_source": "ANF Vol 8/9 + 2026-05-29 decision",
                               }], timeout=30)
            if r2.status_code not in (200, 201):
                print(f"    !! POST {r2.status_code}: {r2.text[:200]}", file=sys.stderr)


def dedupe_db(dry_run: bool):
    """Delete extra rows for known duplicate name_recommended."""
    dupes = ["額我略", "他提安"]  # post-rename names
    for name in dupes:
        r = requests.get(f"{URL}/rest/v1/theologians?select=id,name_english,name_recommended"
                         f"&name_recommended=eq.{name}", headers=H_GET, timeout=30)
        rows = r.json()
        if len(rows) <= 1:
            continue
        print(f"  ↯ dedupe {name}: {len(rows)} rows")
        # Keep the first; delete rest
        for row in rows[1:]:
            print(f"    - delete id={row['id'][:8]} en={row['name_english']}")
            if not dry_run:
                requests.delete(f"{URL}/rest/v1/theologians?id=eq.{row['id']}",
                                headers=H_GET, timeout=30)


# ── Chunks ────────────────────────────────────────────────────────────

ALL_VOLS = [
    ("Vol 1", VOL1), ("Vol 2", VOL2), ("Vol 3", VOL3), ("Vol 4", VOL4),
    ("Vol 5", VOL5), ("Vol 6", VOL6), ("Vol 7", VOL7), ("Vol 9", VOL9),
]


def process_book(label: str, ebook_id: str, dry_run: bool):
    src = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not src.exists():
        print(f"  {label}: jsonl not found, skipping")
        return
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    field_changes = defaultdict(int)
    for r in rows:
        for field in ("volume", "parent_volume", "chapter_path", "content", "source_text", "title_en"):
            v = r.get(field)
            if not v:
                continue
            new = process_chunk_field(v, ebook_id)
            if new != v:
                r[field] = new
                field_changes[field] += 1

    total = sum(field_changes.values())
    print(f"\n{label} ({ebook_id})")
    print(f"  field changes: {dict(field_changes)}; total: {total}")

    if dry_run or total == 0:
        return

    with open(src, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  wrote {src.name} ({src.stat().st_size // 1024} KB)")

    se.push_to_r2(ebook_id, src)
    print("  pushed R2")

    # Refresh DB previews (chapter_path / content preview may have changed)
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                    headers=H_GET, timeout=60)
    insert_rows = [{
        "ebook_id": ebook_id,
        "chunk_index": r["chunk_index"],
        "chunk_type": r.get("chunk_type", "chapter"),
        "page_number": r.get("page_number"),
        "chapter_path": r.get("chapter_path"),
        "content": (r.get("content") or "")[:200],
        "char_count": len(r.get("content") or ""),
    } for r in rows]
    BATCH = 25
    for i in range(0, len(insert_rows), BATCH):
        batch = insert_rows[i:i + BATCH]
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON,
                           json=batch, timeout=60)
        if rr.status_code not in (200, 201):
            print(f"    batch {i}: {rr.status_code} {rr.text[:200]}", file=sys.stderr)
    print(f"  refreshed previews ({len(insert_rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db-only", action="store_true", help="only update DB, skip chunks")
    ap.add_argument("--chunks-only", action="store_true", help="only update chunks")
    args = ap.parse_args()

    if not args.chunks_only:
        print("=== DB: rename name_recommended ===")
        update_db_names(args.dry_run)
        print("\n=== DB: add new entries (Gregory Illuminator, Isaac of Nineveh) ===")
        add_new_entries(args.dry_run)
        print("\n=== DB: dedupe duplicate name_recommended ===")
        dedupe_db(args.dry_run)

    if not args.db_only:
        print("\n=== Chunks: rewrite parent_volume / volume / chapter_path / content ===")
        for label, ebid in ALL_VOLS:
            process_book(label, ebid, args.dry_run)


if __name__ == "__main__":
    main()
