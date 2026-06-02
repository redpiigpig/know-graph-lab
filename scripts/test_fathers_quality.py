"""Regression test — every REFINED 教父 volume must meet the same fixed quality bar.

跑這支可隨時確認「每一卷品質都固定」：上架後若有人重譯/重整/手改造成品質倒退，
這支會抓出來。對 /fathers REFINED_IDS 裡、且有 TERM_FIXES_BY_BOOK 條目的教父卷
（ANF + NPNF 已精修卷）逐卷檢查 5 道門檻：

  G1  validate_book_structure → 0 FAIL          結構完整（chunk_index 連續 / chapter_path 非空…）
  G2  scan T9 cross-bleed = 0                    無 CCEL packaging 跨作品 bleed
  G3  scan T1 title-bleed = 0                    無「標題吞內文」
  G4  term convergence                           TERM_FIXES_BY_BOOK 每個「變體」在內文出現 0 次
  G5  no dual-state                              無 >10 連續英文內文 chunk；整書中文 chunk 比例 ≥ 0.7

Usage:
  python scripts/test_fathers_quality.py            # 測全部已精修卷
  python scripts/test_fathers_quality.py <id> ...   # 只測指定卷
Exit 0 全過；1 任一卷任一門檻 FAIL。
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_book_structure as vb
import scan_translated_book as sc
from sweep_book_quality import TERM_FIXES_BY_BOOK

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:\我的雲端硬碟\資料\電子書\_chunks")
VUE = ROOT / "pages" / "fathers" / "index.vue"

# zh 偵測
_ZH = re.compile(r"[一-鿿]")
def zh_ratio(s: str) -> float:
    s = s or ""
    return len(_ZH.findall(s)) / max(len(s), 1)


def refined_ids() -> list[str]:
    """Parse the REFINED_IDS set literal from pages/fathers/index.vue."""
    txt = VUE.read_text(encoding="utf-8")
    m = re.search(r"REFINED_IDS\s*=\s*new Set\(\[(.*?)\]\)", txt, re.S)
    block = m.group(1) if m else ""
    return re.findall(r"'([0-9a-f]{8}-[0-9a-f-]{27,})'", block)


def check_volume(eid: str) -> tuple[list[str], list[str]]:
    """Return (failures, notes) for one volume."""
    fails: list[str] = []
    notes: list[str] = []
    path = CHUNKS_DIR / f"{eid}.jsonl"
    if not path.exists():
        return [f"JSONL not found: {path}"], notes
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    # G1 structural
    n_fail = sum(1 for i in vb.validate(eid) if i.severity == "FAIL")
    if n_fail:
        fails.append(f"G1 validate {n_fail} FAIL")

    # G2/G3 scan T9 / T1
    sissues = sc.scan(eid)
    t9 = sum(1 for i in sissues if i.rule == "T9")
    t1 = sum(1 for i in sissues if i.rule == "T1")
    if t9:
        fails.append(f"G2 T9 cross-bleed={t9}")
    if t1:
        fails.append(f"G3 T1 title-bleed={t1}")

    # G4 term convergence — every forbidden variant must be absent from content
    fixes = TERM_FIXES_BY_BOOK.get(eid, {})
    blob = "\n".join(r.get("content", "") or "" for r in rows)
    bad = []
    for wrong, right in fixes.items():
        # skip degenerate rules where the variant is a substring of its own target
        if wrong in right:
            continue
        c = blob.count(wrong)
        if c:
            bad.append(f"{wrong}→{right}×{c}")
    if bad:
        fails.append(f"G4 unconverged: {', '.join(bad[:8])}" + (" …" if len(bad) > 8 else ""))

    # G5 dual-state — overall zh ratio + longest English body run
    body = [r for r in rows if (r.get("volume") or "") != "索引"
            and (r.get("content") or "").strip()]
    zh_chunks = sum(1 for r in body if zh_ratio(r.get("content", "")) > 0.15)
    ratio = zh_chunks / max(len(body), 1)
    run = maxrun = 0
    for r in body:
        if zh_ratio(r.get("content", "")) < 0.05:
            run += 1; maxrun = max(maxrun, run)
        else:
            run = 0
    if ratio < 0.70:
        fails.append(f"G5 zh-ratio={ratio:.2f} (<0.70, dual-state?)")
    if maxrun > 10:
        fails.append(f"G5 English-run={maxrun} body chunks (dual-state?)")

    notes.append(f"{len(rows)} chunks · zh {ratio:.2f} · T9={t9} T1={t1} · terms {len(fixes)}")
    return fails, notes


def main():
    ids = sys.argv[1:] or [i for i in refined_ids() if i in TERM_FIXES_BY_BOOK]
    if not ids:
        print("no refined fathers volumes to test"); return 0
    print(f"Testing {len(ids)} refined 教父 volumes\n" + "=" * 64)
    n_pass = n_fail = 0
    for eid in ids:
        fails, notes = check_volume(eid)
        tag = "✓ PASS" if not fails else "✗ FAIL"
        print(f"{tag}  {eid}  ({notes[0] if notes else ''})")
        for f in fails:
            print(f"        ↳ {f}")
        n_pass += not fails
        n_fail += bool(fails)
    print("=" * 64)
    print(f"  {n_pass} PASS · {n_fail} FAIL  /  {len(ids)} volumes")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
