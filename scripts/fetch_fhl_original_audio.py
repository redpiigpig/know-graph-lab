#!/usr/bin/env python3
"""Download 信望愛's Hebrew and Greek chapter recordings, with the owner's authorisation.

信望愛 (bible.fhl.net) publishes chapter-by-chapter recordings in twenty-two
versions; two of them are the original languages — `version=7 希伯來文` and
`version=9 希臘文` — and their files sit at a flat, predictable path:

    https://media.fhl.net/hebrew/{bid}/{bid}_{chap:03d}.mp3
    https://media.fhl.net/greek/{bid}/{bid}_{chap:03d}.mp3

The owner stated on 2026-08-28 that they have obtained authorisation for these
recordings. That authorisation is recorded in the manifest alongside every file,
because a downloaded audio file with no rights record is exactly what the
release contract refuses to ship: 「Record ancient work, modern edition, digital
transcription, translation, recording, and font rights rather than collapsing
them into one license claim.」

Where the files go: Drive, never R2 and never git. 影音一律不上 R2（docs/r2-policy.md）,
and 1,189 chapters is on the order of gigabytes.

The download is polite (one file a second), resumable, and verifies each file is
actually audio rather than an HTML error page — a wrong chapter number returns a
page, not a 404, and a directory full of 2 KB "recordings" looks fine until you
press play.

    python -X utf8 scripts/fetch_fhl_original_audio.py --language hebrew --limit 5
    python -X utf8 scripts/fetch_fhl_original_audio.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVE = Path("G:/我的雲端硬碟/資料/知識圖工作室/語言/原文讀本/讀本/audio")
MANIFEST = ROOT / "output/source-cache/original-readers/fhl-audio-manifest.json"

HEADERS = {"User-Agent": "know-graph-lab private reader build (contact: redpiigpig)"}
MIN_BYTES = 20_000  # 一章最短的錄音也有幾十 KB；比這小的多半是錯誤頁

AUTHORISATION = {
    "source": "信望愛信望愛全球資訊網 bible.fhl.net / media.fhl.net",
    "versions": {"hebrew": "version=7 希伯來文", "greek": "version=9 希臘文"},
    "grantedBy": "站方授權（使用者 2026-08-28 告知已取得）",
    "scope": "私人研讀用；轉載或公開散布前須再確認授權範圍",
    "recordedBy": "未知，需向站方確認朗讀者",
}

# 章數是聖經自己的固定事實，不必上網問。bid 依信望愛編號：舊約 1–39，新約 40–66。
CHAPTERS = [
    50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150,
    31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4,
    28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5,
    5, 3, 5, 1, 1, 1, 22,
]

# 站上的原文錄音照希伯來聖經的分章，瑪拉基書因此只有三章——基督教編號才把
# 第三章拆成三、四。照基督教章數去要 39_004 只會拿到 404，那不是漏檔。
HEBREW_CHAPTER_OVERRIDES = {39: 3}


def targets(language: str) -> list[tuple[int, int]]:
    span = range(1, 40) if language == "hebrew" else range(40, 67)
    return [
        (bid, chapter)
        for bid in span
        for chapter in range(
            1,
            (HEBREW_CHAPTER_OVERRIDES.get(bid, CHAPTERS[bid - 1]) if language == "hebrew"
             else CHAPTERS[bid - 1]) + 1,
        )
    ]


def urls_for(language: str, bid: int, chapter: int) -> list[str]:
    """mp3 先，ogg 後。哈該書一、二章的 mp3 站上回 403 而 ogg 是好的。"""

    stem = f"https://media.fhl.net/{language}/{bid}/{bid}_{chapter:03d}"
    return [f"{stem}.mp3", f"{stem}.ogg"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("hebrew", "greek", "both"), default="both")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    languages = ("hebrew", "greek") if args.language == "both" else (args.language,)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {
        "schemaVersion": "1.0.0",
        "authorisation": AUTHORISATION,
        "files": {},
    }
    manifest["authorisation"] = AUTHORISATION
    files = manifest["files"]

    plan = [(language, bid, chapter) for language in languages for bid, chapter in targets(language)]
    todo = [item for item in plan if f"{item[0]}/{item[1]}/{item[2]}" not in files]
    if args.limit:
        todo = todo[: args.limit]
    print(f"章數合計 {len(plan)}（希伯來 {len(targets('hebrew'))}、希臘 {len(targets('greek'))}）")
    print(f"已下載 {len(files)}，本輪待download {len(todo)}")

    if not args.write:
        for language, bid, chapter in todo[:5]:
            print(f"  {urls_for(language, bid, chapter)[0]}")
        print("（未下載；加 --write）")
        return 0

    if not DRIVE.exists():
        print(f"⚠ Drive 路徑不在：{DRIVE}。掛上雲端硬碟再跑，音檔不進 repo 也不上 R2。")
        return 1

    done = failed = 0
    for language, bid, chapter in todo:
        key = f"{language}/{bid}/{chapter}"
        folder = DRIVE / f"fhl-{language}" / f"{bid:02d}"
        folder.mkdir(parents=True, exist_ok=True)
        payload = None
        url = ""
        error: Exception | None = None
        for candidate in urls_for(language, bid, chapter):
            try:
                request = urllib.request.Request(candidate, headers=HEADERS)
                payload = urllib.request.urlopen(request, timeout=120).read()
                url = candidate
                break
            except Exception as problem:  # noqa: BLE001 - re-runnable
                error = problem
        if payload is None:
            failed += 1
            if failed % 20 == 1:
                print(f"  ✗ {key}：{error}")
            continue
        target = folder / f"{bid:02d}_{chapter:03d}{'.ogg' if url.endswith('.ogg') else '.mp3'}"
        # 錯的章號會回一頁 HTML 而不是 404，靠大小與檔頭擋掉。ogg 的檔頭是
        # OggS，先前只認 mp3 的兩種檔頭，於是 ogg 備援抓下來也被判成不是音檔。
        is_audio = (
            payload[:4] in (b"ID3\x03", b"ID3\x04")
            or payload.startswith(b"\xff\xfb")
            or payload[:4] == b"OggS"
        )
        if len(payload) < MIN_BYTES or not is_audio:
            failed += 1
            if failed % 20 == 1:
                print(f"  ✗ {key}：拿到的不是音檔（{len(payload)} bytes）")
            continue
        target.write_bytes(payload)
        files[key] = {
            "language": language,
            "book": bid,
            "chapter": chapter,
            "url": url,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "path": str(target),
        }
        done += 1
        if done % 25 == 0:
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  … 已下載 {done}／{len(todo)}", flush=True)
        time.sleep(args.delay)

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(item["bytes"] for item in files.values())
    print(f"完成 {done}，失敗 {failed}；累計 {len(files)} 章、{total / 1_000_000:.1f} MB")
    print(f"存放：{DRIVE}（Drive 正本；不進 git，不上 R2）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
