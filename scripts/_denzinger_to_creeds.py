"""
Phase 4 of the Denzinger pipeline — pull DH-indexed Chinese chunks into the
/creeds council Chinese files (data/creeds/.../{slug}-chinese.txt).

Spec: .claude/skills/ebook-pipeline/book-structure-bilingual-parallel.md §7

Reads `_chunks/{id}.bilingual.jsonl` (output of segment_denzinger.py
--write-jsonl), filters by COUNCIL_DH_RANGES, concatenates the Chinese
content per council slug, writes to data/creeds/.../{slug}-chinese.txt.

⚠ DH ranges below are SPEC DRAFTS — verify against the actual Denzinger
book chapter divisions before --write.

Usage:
  python scripts/_denzinger_to_creeds.py             # dry-run, print plan
  python scripts/_denzinger_to_creeds.py --write     # write new files only
  python scripts/_denzinger_to_creeds.py --write --force  # overwrite existing
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import CHUNKS_DIR  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
BILINGUAL_JSONL = CHUNKS_DIR / f"{BOOK_ID}.bilingual.jsonl"

# Spec § 7 ranges — refined 2026-05-29 against entries.json council headers.
# Each council's DH range extends from its first DH (council header) to one
# below the next council/Part marker, matching how Denzinger physically groups
# session decrees + immediate post-council pope letters under the council.
# (slug, dh_range_start, dh_range_end, council_display_name)
COUNCIL_DH_RANGES: list[tuple[str, int, int, str]] = [
    # 早期大公會議 (3-7)
    ("ecumenical-councils/early/early-03",         250, 299,  "以弗所大公會議 (431)"),
    ("ecumenical-councils/early/early-04",         300, 420,  "迦克墩大公會議 (451)"),
    ("ecumenical-councils/early/early-05",         421, 549,  "第二次君士坦丁堡大公會議 (553)"),
    ("ecumenical-councils/early/early-06",         550, 599,  "第三次君士坦丁堡大公會議 (680-681)"),
    ("ecumenical-councils/early/early-07",         600, 649,  "第二次尼西亞大公會議 (787)"),
    # 中世紀大公會議 (8-18)
    ("ecumenical-councils/medieval/medieval-08",   650, 709,  "第四次君士坦丁堡大公會議 (869-870)"),
    # Verified against parsed 詳細目錄 2026-05-28 + 2026-05-29 extension:
    # Lateran I  TOC: 「710-712  法典(1123 年 3 月 27 日)」
    # Lateran II TOC: 「715-718  法典：貿賣聖職及扶重利」 + 721-741 (Eugenius III 前)
    # Lateran III TOC: 「751 第三場會議(3 月 19 或 22 日)」… 758
    ("ecumenical-councils/medieval/medieval-09",   710, 714,  "第一次拉特朗大公會議 (1123)"),
    ("ecumenical-councils/medieval/medieval-10",   715, 750,  "第二次拉特朗大公會議 (1139)"),
    ("ecumenical-councils/medieval/medieval-11",   751, 799,  "第三次拉特朗大公會議 (1179)"),
    ("ecumenical-councils/medieval/medieval-12",   800, 829,  "第四次拉特朗大公會議 (1215)"),
    ("ecumenical-councils/medieval/medieval-13",   830, 849,  "第一次里昂大公會議 (1245)"),
    ("ecumenical-councils/medieval/medieval-14",   850, 890,  "第二次里昂大公會議 (1274)"),
    ("ecumenical-councils/medieval/medieval-15",   891, 1150, "維也納大公會議 (1311-1312)"),
    ("ecumenical-councils/medieval/medieval-16",   1151, 1299, "康士坦茨大公會議 (1414-1418)"),
    ("ecumenical-councils/medieval/medieval-17",   1300, 1439, "巴塞爾／費拉拉／佛羅倫斯／羅馬大公會議 (1431-1445)"),
    # Lateran V (1512-1517): parse_toc 未能單獨抓 council header（被緊鄰 Pope
    # Leo X vol 覆寫），但詳細目錄 line 1570 顯示 Lateran V 從 DH 1440 開始。
    # 終點接 Trent (1500) 之前。
    ("ecumenical-councils/medieval/medieval-18",   1440, 1499, "第五次拉特朗大公會議 (1512-1517)"),
    # 特利騰大公會議 (19) — 25 sessions
    ("ecumenical-councils/trent/trent-03",  1500, 1500, "Trent Session 3 — 信經"),
    ("ecumenical-councils/trent/trent-04",  1501, 1508, "Trent Session 4 — 正典聖經與傳承"),
    ("ecumenical-councils/trent/trent-05",  1510, 1516, "Trent Session 5 — 原罪"),
    ("ecumenical-councils/trent/trent-06",  1520, 1583, "Trent Session 6 — 成義令"),
    ("ecumenical-councils/trent/trent-07",  1600, 1630, "Trent Session 7 — 聖事總論／聖洗／堅振"),
    ("ecumenical-councils/trent/trent-13",  1635, 1661, "Trent Session 13 — 聖體聖事"),
    ("ecumenical-councils/trent/trent-14",  1667, 1719, "Trent Session 14 — 修和聖事／傅油聖事"),
    ("ecumenical-councils/trent/trent-21",  1725, 1734, "Trent Session 21 — 兩種形體領聖體"),
    ("ecumenical-councils/trent/trent-22",  1738, 1760, "Trent Session 22 — 彌撒聖祭"),
    ("ecumenical-councils/trent/trent-23",  1763, 1778, "Trent Session 23 — 聖秩聖事"),
    ("ecumenical-councils/trent/trent-24",  1797, 1816, "Trent Session 24 — 婚姻聖事"),
    ("ecumenical-councils/trent/trent-25",  1820, 1835, "Trent Session 25 — 煉獄／聖人敬禮／聖像"),
    # 梵蒂岡第一屆 (20)
    ("ecumenical-councils/vatican-i/df",   3000, 3045, "梵一 Dei Filius — 論天主公教信仰"),
    ("ecumenical-councils/vatican-i/pa",   3050, 3075, "梵一 Pastor Aeternus — 論教宗"),
    # 梵蒂岡第二屆 (21) — 16 文獻 / Hünermann 標準編號（4001-4345）
    ("ecumenical-councils/vatican-ii/sc",  4001, 4099, "梵二 Sacrosanctum Concilium — 禮儀憲章"),
    ("ecumenical-councils/vatican-ii/lg",  4100, 4179, "梵二 Lumen Gentium — 教會憲章"),
    ("ecumenical-councils/vatican-ii/dv",  4180, 4194, "梵二 Dei Verbum — 天主啟示憲章"),
    ("ecumenical-councils/vatican-ii/ad-gentes", 4195, 4199, "梵二 Nostra Aetate — 教會對非基督宗教態度宣言"),
    ("ecumenical-councils/vatican-ii/gs",  4201, 4345, "梵二 Gaudium et Spes — 牧職憲章"),
]

# Appendix 5 of Denzinger 43rd edition — Protestant creeds (DH 5500-5702).
# These don't belong under /ecumenical-councils/, hence a parallel
# /protestant-creeds/ subtree. Verified against parse_toc entries.json
# (附錄五 基督新教歷代一些重要信仰表白).
# (slug, dh_range_start, dh_range_end, display_name)
PROTESTANT_DH_RANGES: list[tuple[str, int, int, str]] = [
    ("protestant-confessions/luther-small-catechism",     5500, 5502, "路德《小本基督徒要學》（小本教理）"),
    ("protestant-confessions/augsburg-confession",        5503, 5523, "奧斯堡信條（1530）"),
    ("protestant-confessions/anglican-articles",          5524, 5562, "安立甘宗信條（三十九條）"),
    ("protestant-confessions/english-congregational",     5563, 5574, "英國公理會信條"),
    ("protestant-confessions/reformed-belgic",            5575, 5590, "改革宗信仰綱要 / 比利時信條"),
    ("protestant-confessions/lima-bem",                   5591, 5701, "利馬文件（BEM）— 受洗‧聖餐‧職事"),
    ("protestant-confessions/taiwan-presbyterian-creed",  5702, 5702, "台灣基督長老教會信條"),
]

# Marker indicating an existing file is a placeholder (safe to overwrite without --force)
PLACEHOLDER_MARKERS = ("中文版尚未取得", "Chinese version not yet obtained", "尚未取得")


def is_placeholder(path: Path) -> bool:
    """File is a placeholder when it contains an explicit marker text."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return True
    return any(m in text for m in PLACEHOLDER_MARKERS)


def load_chunks() -> list[dict]:
    if not BILINGUAL_JSONL.exists():
        print(f"ERROR: bilingual JSONL not found: {BILINGUAL_JSONL}", file=sys.stderr)
        print("Run segment_denzinger.py --write-jsonl first.", file=sys.stderr)
        sys.exit(1)
    out: list[dict] = []
    with BILINGUAL_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def chunks_for_range(chunks: list[dict], lo: int, hi: int) -> list[dict]:
    return [c for c in chunks
            if c.get("section_type") == "entry"
            and isinstance(c.get("dh_number"), int)
            and lo <= c["dh_number"] <= hi
            and (c.get("content") or "").strip()]


def build_content(council_name: str, lo: int, hi: int, chunks: list[dict]) -> str:
    """Format chunks as a single Chinese text file. Each DH N labeled."""
    head = (
        f"# {council_name}\n"
        f"# DH {lo}–{hi}\n"
        f"# 來源：光啟文化 2013《公教會之信仰與倫理教義選集》(Denzinger 中譯)\n"
        f"# 共 {len(chunks)} 條中譯條目\n"
        f"\n"
    )
    parts = []
    for c in chunks:
        dh = c["dh_number"]
        zh = (c.get("content") or "").strip()
        parts.append(f"【DH {dh}】\n{zh}\n")
    return head + "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="actually write files (default = dry-run)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite even non-placeholder files (will backup .bak)")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    creeds_root = repo_root / "data" / "creeds"

    chunks = load_chunks()
    entry_chunks = [c for c in chunks if c.get("section_type") == "entry"
                                       and isinstance(c.get("dh_number"), int)]
    print(f"Loaded {len(chunks)} bilingual chunks ({len(entry_chunks)} DH entries)")

    written = skipped_exists = skipped_empty = backed_up = 0
    for slug, lo, hi, name in COUNCIL_DH_RANGES + PROTESTANT_DH_RANGES:
        out_path = creeds_root / f"{slug}-chinese.txt"
        filt = chunks_for_range(chunks, lo, hi)

        if not filt:
            skipped_empty += 1
            print(f"  {slug:<40s} DH {lo}-{hi}: ⊘ no chunks in range — skip")
            continue

        if out_path.exists() and not args.force and not is_placeholder(out_path):
            skipped_exists += 1
            print(f"  {slug:<40s} DH {lo}-{hi}: {len(filt):3} chunks → {out_path.name} ⚠ exists (skip; use --force)")
            continue

        content = build_content(name, lo, hi, filt)
        char_count = sum(len((c.get("content") or "")) for c in filt)
        action = "would write" if not args.write else "wrote"

        if args.write:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if out_path.exists() and not is_placeholder(out_path):
                bak = out_path.with_suffix(out_path.suffix + ".bak")
                shutil.copyfile(out_path, bak)
                backed_up += 1
            out_path.write_text(content, encoding="utf-8")
            written += 1

        print(f"  {slug:<40s} DH {lo}-{hi}: {len(filt):3} chunks, {char_count:>6,} chars  → {action} {out_path.relative_to(repo_root)}")

    print(f"\nSummary: written={written}, skipped_exists={skipped_exists}, skipped_empty={skipped_empty}, backed_up={backed_up}")
    if not args.write:
        print("\n[DRY RUN] re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
