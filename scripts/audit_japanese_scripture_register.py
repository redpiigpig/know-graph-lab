#!/usr/bin/env python3
"""Check every chapter of the Japanese reader's scripture cache for its register.

🚨 Why this exists.  `bible_以賽亞書_001.txt` sat in the cache labelled
「文語訳（明治元訳舊約／大正改訳新約），公有領域」 and was not the 文語訳 at all:
its text is a modern translation (「アモツの子イザヤが……治世のことである」),
while chapter 2 of the same book is genuine 文語 (「すゑの日にヱホバの家の山は
……堅立ち」).  The ja.wikisource page 「イザヤ書 (文語訳)」 itself carries the
modern text for chapter 1 — re-fetching returns the same thing, and no
alternative page for that chapter exists (probed 2026-09-11:
`明治元訳旧約聖書/イザヤ書`, `イザヤ書-第一章 (文語訳)` and two more spellings
are all missing).  So the chapter is dropped, not repaired.

That is a rights problem and not only a style one: 口語訳 (1954/55) and
新共同訳 (1987) are still in copyright, and a mislabelled chapter puts
copyrighted text into a corpus documented as public domain.

**One chapter got in, so there may be a second.**  Reading them by hand is
exactly the failure mode this series keeps hitting, so the判準 is a pure
function (`classify_register` in `build_japanese_lemma_corpus.py`), it runs
over the whole cache, and it is pinned by tests in both directions.

    python -X utf8 scripts/audit_japanese_scripture_register.py
    python -X utf8 scripts/audit_japanese_scripture_register.py --write  # 標 manifest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_japanese_lemma_corpus import classify_register  # noqa: E402

CACHE = ROOT / "output/source-cache/original-readers/japanese-full/scripture"
MANIFEST = CACHE / "manifest.json"

# 只有這兩群宣稱自己是文語。佛典那一群的訓読各有譯者，本來就 rightsChecked: false，
# 混著現代語訳是那一批自己的問題，報出來但不當成違規。
BUNGO_GROUPS = ("bible", "creed")
EXCLUSION_NOTE = (
    "維基文庫「イザヤ書 (文語訳)」頁的這一章實為現代語譯本（口語訳／新共同訳系），"
    "非明治元訳；該譯本仍在著作權內。重抓同源仍為現代語，亦無其他候選頁名。"
    "已排除出語料，不得當成公有領域文語訳使用。"
)


def audit() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_file = {Path(meta["file"]).name: (key, meta) for key, meta in manifest.items()}
    rows: list[dict[str, Any]] = []
    for path in sorted(CACHE.glob("*.txt")):
        key, meta = by_file.get(path.name, ("", {}))
        verdict = classify_register(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "file": path.name,
                "key": key,
                "group": meta.get("group", ""),
                "title": meta.get("titleZh") or path.stem,
                "claimsBungo": meta.get("group") in BUNGO_GROUPS,
                "inManifest": bool(key),
                **verdict,
            }
        )
    return rows, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="把違規的章標進 manifest")
    args = parser.parse_args()

    rows, manifest = audit()
    offenders = [row for row in rows if row["claimsBungo"] and row["register"] != "文語"]
    others = [row for row in rows if not row["claimsBungo"] and row["register"] != "文語"]
    orphans = [row for row in rows if not row["inManifest"]]

    print(f"掃過 {len(rows)} 份，宣稱文語的 {sum(1 for r in rows if r['claimsBungo'])} 份")
    print(f"🚨 宣稱文語卻判不是文語：{len(offenders)} 份")
    for row in offenders:
        print(
            f"  - {row['file']}（{row['title']}）判為{row['register']}："
            f"文語特徵 {row['bungoHits']}、現代語特徵 {row['modernHits']}、{row['chars']} 字"
        )
    print(f"非文語群（佛典訓読等）判為非文語：{len(others)} 份，這一批本來就 rightsChecked: false")
    for row in others:
        print(f"  · {row['file']} 判為{row['register']}（{row['bungoHits']}／{row['modernHits']}）")
    if orphans:
        print(f"⚠ 有 {len(orphans)} 份檔案不在 manifest 裡，來源與權利狀態無從查起：")
        for row in orphans:
            print(f"  · {row['file']} 判為{row['register']}")

    if args.write:
        changed = 0
        for row in offenders:
            meta = manifest[row["key"]]
            meta["excluded"] = True
            meta["excludedReason"] = EXCLUSION_NOTE
            meta["registerAudit"] = {
                "register": row["register"],
                "bungoHits": row["bungoHits"],
                "modernHits": row["modernHits"],
                "checked": "2026-09-11",
            }
            meta["rightsChecked"] = False
            meta["rightsNote"] = "來源標示為文語訳，實為現代語譯本，著作權未清；已排除"
            changed += 1
        if changed:
            MANIFEST.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            print(f"manifest 標了 {changed} 條並寫回")
    elif offenders:
        print("（未寫入；加 --write 會把這幾章標成 excluded 並撤掉公有領域註記）")
    return 1 if offenders and not args.write else 0


if __name__ == "__main__":
    raise SystemExit(main())
