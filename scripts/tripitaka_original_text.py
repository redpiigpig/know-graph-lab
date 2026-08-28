"""佛教大藏經 /tripitaka —— 把原典**全文**掛到漢文段落上。

tripitaka_parallels.py 產出的是「指標」（雜阿含第 1267 經 ↔ SN 1.1），
本檔負責把指標換成真正讀得到的原文。

  巴利  SuttaCentral bilara 逐段本（root/pli/ms，7,288 部）—— 已切段、有段 id
  梵文  SuttaCentral 幾乎沒有（root/san 只 2 檔），須另從 GRETIL 取，見 --gretil
  藏文  德格版須另從 84000／Adarsha 取，尚未接（缺口，見 SKILL.md）

對齊的誠實界線：巴利那一側是「一整部經」，漢文那一側是「該經的起始段」。
所以呈現成**該經開頭的一塊可展開原文**，不是逐句並排 —— 逐句並排會讓讀者
以為第 n 段漢文正對第 n 段巴利，那是假的。漢巴兩本的段落數本來就不一樣。

  python scripts/tripitaka_original_text.py --pali            # 掛巴利原文
  python scripts/tripitaka_original_text.py --pali --only T0099
"""
from __future__ import annotations

import argparse
import json
import re
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_parallels as tpp  # noqa: E402

SC_DIR = Path(os.environ.get("SC_DATA", "C:/tmp/cbeta/sc-data/sc_bilara_data"))
SEG_DIR = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
ROWS = Path(os.environ.get("TRIPITAKA_PARALLEL_ROWS", "C:/tmp/cbeta/parallels_rows.jsonl"))


def _index_bilara(root: Path, suffix: str) -> tuple[dict[str, Path], list]:
    """SC 的檔名是 `{uid}_{role}-{lang}-{edition}.json`，建 uid → 路徑索引。

    法句經那類是**區間檔名**（dhp1-20、dhp100-115），單經 uid（dhp21）在
    索引裡查不到 —— 一開始就是這樣漏掉 1,640 筆。故另建區間索引。
    """
    idx: dict[str, Path] = {}
    ranges: list[tuple[str, int, int, Path]] = []
    for p in root.rglob(f"*{suffix}"):
        uid = p.name.split("_")[0]
        idx.setdefault(uid, p)
        m = re.match(r"^([a-z][a-z-]*?)(\d+)-(\d+)$", uid)
        if m:
            ranges.append((m.group(1), int(m.group(2)), int(m.group(3)), p))
    return idx, ranges


def find_text(uid: str, idx: dict[str, Path], ranges: list) -> Path | None:
    """uid → 檔案。先直接查，查不到再看它落在哪個區間檔裡。"""
    uid = uid.rstrip("-")
    if uid in idx:
        return idx[uid]
    m = re.match(r"^([a-z][a-z-]*?)(\d+)$", uid)
    if not m:
        return None
    prefix, n = m.group(1), int(m.group(2))
    for rp, lo, hi, path in ranges:
        if rp == prefix and lo <= n <= hi:
            return path
    return None


def load_text(path: Path) -> list[list[str]]:
    """→ [[段id, 文字], …]，保留 SC 的段 id（sn22.120:1.1）供引用。"""
    d = json.loads(path.read_text(encoding="utf-8"))
    return [[k, v.strip()] for k, v in d.items() if v and v.strip()]


def build_pali(only: str | None) -> None:
    pli_idx, pli_ranges = _index_bilara(SC_DIR / "root" / "pli", "-pli-ms.json")
    print(f"巴利逐段本 {len(pli_idx):,} 部（含 {len(pli_ranges)} 個區間檔）")
    if not pli_idx:
        sys.exit(f"找不到 SuttaCentral 巴利資料（{SC_DIR}）。先 sparse-clone sc-data。")

    rows = [json.loads(l) for l in ROWS.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_work: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    stats = Counter()
    missing = Counter()

    for r in rows:
        if r["lang"] != "pi" or not r.get("seg"):
            continue
        if only and r["work_id"] != only:
            continue
        uid = (r.get("uid") or "").split("#")[0]
        path = find_text(uid, pli_idx, pli_ranges)
        if not path:
            missing[uid.rstrip("0123456789.") or uid] += 1
            stats["no_text"] += 1
            continue
        lines = load_text(path)
        if not lines:
            stats["empty"] += 1
            continue
        by_work[r["work_id"]][r["seg"]].append({
            "lang": "pi",
            "uid": uid,
            "ref": r["ref"],
            "src": r["src"],
            "partial": r.get("note") == "部分平行",
            "lines": lines,
        })
        stats["attached"] += 1
        stats["lines"] += len(lines)

    for wid, segs in sorted(by_work.items()):
        out = SEG_DIR / f"{wid}.orig.json"
        # 同一段可能對到多部巴利經（一經多平行），依 uid 去重後保序
        cleaned = {}
        for seg, items in segs.items():
            seen = set()
            keep = []
            for it in items:
                if it["uid"] in seen:
                    continue
                seen.add(it["uid"])
                keep.append(it)
            cleaned[seg] = keep
        out.write_text(json.dumps(cleaned, ensure_ascii=False), encoding="utf-8")
        n = sum(len(v) for v in cleaned.values())
        print(f"  {wid}: {len(cleaned)} 段掛上 {n} 部巴利原文 → {out.name}")

    print(f"\n掛上 {stats['attached']:,} 筆／{stats['lines']:,} 行巴利原文，"
          f"涵蓋 {len(by_work)} 部漢文經")
    if stats["no_text"]:
        print(f"  {stats['no_text']:,} 筆有對應編號但 SuttaCentral 無逐段本"
              f"（多為律藏與註釋書）:", dict(missing.most_common(8)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pali", action="store_true")
    ap.add_argument("--only", type=str)
    a = ap.parse_args()
    if a.pali:
        build_pali(a.only)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
