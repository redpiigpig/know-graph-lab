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

Superseded artifacts are deleted outright (owner, 2026-09-25: the old PDFs go; the
source layer in git is the archive), so a
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
# 擁有者 2026-09-25：「資料夾中單字卡和讀本要分開」。印刷母版底下分三夾，撲克牌
# 不再混進「讀本」那一夾。
DRIVE_MASTER_READERS = DRIVE_MASTERS / "讀本"
DRIVE_MASTER_CARDS = DRIVE_MASTERS / "單字卡"
DRIVE_MASTER_PLAYING = DRIVE_MASTERS / "撲克牌"
WORK_PLAYING = ROOT / "output/playing-cards"

# A reader PDF belongs in the reader folders, a deck PDF in the card folders.
def is_deck(name: str) -> bool:
    return "flashcards" in name


def is_playing(name: str) -> bool:
    return "playing-cards" in name


# Artifacts from an earlier shape of the release. The Greek 50-lesson book was
# replaced by the two-volume pair, the samples belong to the template phase, and
# rebuild-v2/v3 are superseded Hebrew renders.
SUPERSEDED_NAMES = {
    # 2026-09-08：書背改成每一冊一張，寬度由該冊頁數算出（build_reader_spines.py）。
    # 這兩個是舊的單張、寬度寫死 16 mm 的希伯來書背。
    "hebrew-original-reader-spine-b5-height.pdf",
    "hebrew-original-reader-spine-b5-height.svg",
    # 2026-09-25：希伯來單冊 505 頁超過上限，切成 vol1／vol2，單冊那個 stem 作廢。
    "hebrew-original-reader-50-lessons.docx",
    "hebrew-original-reader-50-lessons.pdf",
    "hebrew-original-reader-50-lessons-spine.pdf",
    "greek-original-reader-50-lessons.docx",
    "greek-original-reader-50-lessons.pdf",
    "greek-original-reader-sample.docx",
    "hebrew-original-reader-sample.docx",
    "latin-original-reader-sample.docx",
    "original-reader-vocabulary-inspect.ndjson",
    "original-reader-vocabulary-master.xlsx.inspect.ndjson",
    # 2026-09-17：教父半部改成節錄後，希臘從六冊收成四冊（build_greek_full_reader.PARTS）。
    # 🚨 第五、六冊在本機刪掉就沒了，Drive 上卻還躺著——使用者翻到的是一本已經
    # 不存在的冊次，而且它自己看起來完全正常。
    "greek-original-reader-vol5.docx",
    "greek-original-reader-vol5.pdf",
    "greek-original-reader-vol5-spine.pdf",
    "greek-original-reader-vol6.docx",
    "greek-original-reader-vol6.pdf",
    "greek-original-reader-vol6-spine.pdf",
    # 2026-09-18：一課壓到八頁、讀文按版面預算節錄之後各半都進得去一本，擁有者
    # 裁示並冊——希臘、拉丁、日文各從四／三／四冊收成兩冊。
    # 🚨 本機刪掉就沒了，Drive 上卻還躺著；使用者翻到的是一本已經不存在的冊次，
    # 而它自己看起來完全正常。
    # 2026-09-25：希臘 vol3 又活回來了（下冊 611 頁切成 vol2／vol3），不在作廢名單。
    "greek-original-reader-vol4.docx",
    "greek-original-reader-vol4.pdf",
    "greek-original-reader-vol4-spine.pdf",
    # 2026-09-25：拉丁 vol3／vol4 活回來了（上下冊各切兩本），不在作廢名單。
    "japanese-original-reader-vol3.docx",
    "japanese-original-reader-vol3.pdf",
    "japanese-original-reader-vol3-spine.pdf",
    "japanese-original-reader-vol4.docx",
    "japanese-original-reader-vol4.pdf",
    "japanese-original-reader-vol4-spine.pdf",
}
# 2026-09-16 書背改走課程讀本那一套版式，舊的裸書背 SVG 全部作廢。
SUPERSEDED_SUFFIXES = ("-spine.svg",)
SUPERSEDED_DIRS = {"rebuild-v2", "rebuild-v3", "_superseded"}


def digest(path: Path) -> str:
    """檔案的 sha256；讀不到就回空字串。

    Drive 那一側的檔可能只是雲端佔位而沒有落地，讀它會丟 `OSError: [Errno 22]`。
    整支腳本因此中途死掉，而前面已經同步好的檔沒有任何紀錄——看起來就像同步失敗。
    讀不到的目標當成「跟母版不一樣」，重新複製一份就是了。
    """
    sha = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                sha.update(block)
    except OSError as error:
        print(f"  讀不到（當成過期）：{path}　{error.strerror or error}")
        return ""
    return sha.hexdigest()


def targets_for(name: str) -> list[Path]:
    if is_deck(name):
        return [WORK_CARDS / name, DRIVE_CARDS / name, DRIVE_MASTER_CARDS / name]
    if is_playing(name):
        return [WORK_PLAYING / name, DRIVE_MASTER_PLAYING / name]
    return [WORK_READERS / name, DRIVE_READERS / name, DRIVE_MASTER_READERS / name]


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
    """把作廢的版次搬進各處的 _superseded。

    🚨 **印刷母版那一夾也要掃。** 這支腳本原本只掃 output/original-readers 與
    Drive 的「讀本」，而 Drive 的「印刷母版」——送印時真正會被打開的那一夾——
    從來沒有被清過：2026-09-17 作廢的希臘第五、六冊在那裡躺到 2026-09-18 才
    被發現，旁邊還多了並冊後作廢的另外五冊。一本已經不存在的冊次躺在送印夾裡，
    而它自己看起來完全正常，這正是這支腳本存在的理由。
    """
    moved = 0
    # 🚨 output/print-masters 也要掃：sync 是拿它當權威往三處複製的，作廢的冊次留在
    # 那裡就會被當成現行的書推上 Drive。
    folders = (MASTERS, WORK_READERS, DRIVE_READERS, DRIVE_MASTERS, DRIVE_MASTER_READERS,
               DRIVE_MASTER_CARDS, WORK_CARDS, DRIVE_CARDS)
    for folder in folders:
        if not folder.exists():
            continue
        for name in sorted(SUPERSEDED_NAMES):
            source = folder / name
            if not source.exists():
                continue
            moved += 1
            print(f"  作廢（刪除）：{source}")
            if write:
                source.unlink()
        for source in sorted(folder.glob("*")):
            if source.is_file() and source.name.endswith(SUPERSEDED_SUFFIXES):
                moved += 1
                print(f"  作廢（刪除）：{source}")
                if write:
                    source.unlink()
        for name in sorted(SUPERSEDED_DIRS):
            source = folder / name
            if not source.is_dir():
                continue
            moved += 1
            print(f"  作廢（刪除）：{source}/")
            if write:
                shutil.rmtree(source)
    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="實際覆寫與搬移")
    args = parser.parse_args()

    print("一、以 output/print-masters 為準，對齊各處副本")
    copied, missing = sync(args.write)
    print(f"  過期 {copied} 份、缺 {missing} 份")

    print("二、刪除作廢的舊版次")
    moved = retire(args.write)
    print(f"  {moved} 項")

    if not args.write:
        print("（未寫入；加 --write）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
