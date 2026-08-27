#!/usr/bin/env python3
"""Make every copy of a reader or flashcard artifact the same copy.

The readers exist in four places — the local working copy, the local print
masters, and the Drive 讀本／單字卡／印刷母版 folders — and on 2026-08-27 they
had drifted: the print masters were current while the working copy and the Drive
讀本 folder still held the previous render, three of them with a different page
count (希臘上冊 480 對 521, 希伯來 395 對 401, 拉丁上冊 332 對 313). Nothing was
wrong with those files except that they were out of date, which is the failure
mode this whole series keeps guarding against: an artifact that renders cleanly
and is simply not the current book.

``output/print-masters/`` is the authority. Everything else is made to match it.

Superseded artifacts are moved into ``_superseded/`` rather than deleted, so a
mistake here costs a move rather than a rebuild.

    python -X utf8 scripts/sync_reader_artifacts.py            # report only
    python -X utf8 scripts/sync_reader_artifacts.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "output/print-masters"
WORK_READERS = ROOT / "output/original-readers"
WORK_CARDS = ROOT / "output/flashcards"

DRIVE = Path("G:/我的雲端硬碟/資料/知識圖工作室/語言/原文讀本")
DRIVE_READERS = DRIVE / "讀本"
DRIVE_CARDS = DRIVE / "單字卡"
DRIVE_MASTERS = DRIVE / "印刷母版"

# A reader PDF belongs in the reader folders, a deck PDF in the card folders.
def is_deck(name: str) -> bool:
    return "flashcards" in name


# Artifacts from an earlier shape of the release. The Greek 50-lesson book was
# replaced by the two-volume pair, the samples belong to the template phase, and
# rebuild-v2/v3 are superseded Hebrew renders.
SUPERSEDED_NAMES = {
    "greek-original-reader-50-lessons.docx",
    "greek-original-reader-50-lessons.pdf",
    "greek-original-reader-sample.docx",
    "hebrew-original-reader-sample.docx",
    "latin-original-reader-sample.docx",
    "original-reader-vocabulary-inspect.ndjson",
    "original-reader-vocabulary-master.xlsx.inspect.ndjson",
}
SUPERSEDED_DIRS = {"rebuild-v2", "rebuild-v3"}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            sha.update(block)
    return sha.hexdigest()


def targets_for(name: str) -> list[Path]:
    if is_deck(name):
        return [WORK_CARDS / name, DRIVE_CARDS / name, DRIVE_MASTERS / name]
    return [WORK_READERS / name, DRIVE_READERS / name, DRIVE_MASTERS / name]


def sync(write: bool) -> tuple[int, int]:
    copied = missing = 0
    for master in sorted(MASTERS.glob("*.pdf")):
        want = digest(master)
        for target in targets_for(master.name):
            if not target.parent.exists():
                print(f"  略過（資料夾不在）：{target}")
                continue
            if target.exists() and digest(target) == want:
                continue
            state = "過期" if target.exists() else "缺"
            if state == "缺":
                missing += 1
            else:
                copied += 1
            print(f"  {state}：{target}")
            if write:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(master, target)
    return copied, missing


def retire(write: bool) -> int:
    moved = 0
    for folder in (WORK_READERS, DRIVE_READERS):
        if not folder.exists():
            continue
        attic = folder / "_superseded"
        for name in sorted(SUPERSEDED_NAMES):
            source = folder / name
            if not source.exists():
                continue
            moved += 1
            print(f"  作廢：{source}")
            if write:
                attic.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(attic / name))
        for name in sorted(SUPERSEDED_DIRS):
            source = folder / name
            if not source.is_dir():
                continue
            moved += 1
            print(f"  作廢：{source}/")
            if write:
                attic.mkdir(parents=True, exist_ok=True)
                destination = attic / name
                if destination.exists():
                    shutil.rmtree(destination)
                shutil.move(str(source), str(destination))
    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="實際覆寫與搬移")
    args = parser.parse_args()

    print("一、以 output/print-masters 為準，對齊各處副本")
    copied, missing = sync(args.write)
    print(f"  過期 {copied} 份、缺 {missing} 份")

    print("二、把舊版次搬進 _superseded")
    moved = retire(args.write)
    print(f"  {moved} 項")

    if not args.write:
        print("（未寫入；加 --write）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
