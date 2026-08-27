#!/usr/bin/env python3
"""Fetch the Japanese reader's corpus: pre-war religious studies, from 青空文庫.

The contract's second volume reads 戰前宗教學與無教會主義, and Japanese
copyright runs seventy years from the author's death — non-retroactively, so
everyone who died in 1967 or earlier was already public domain when the term
was extended in 2018 and stayed there. Every author below qualifies:

    内村鑑三 1930  姉崎正治 1949  折口信夫 1953  和辻哲郎 1960
    津田左右吉 1961  矢内原忠雄 1961  柳田國男 1962  鈴木大拙 1966
    新渡戸稲造 1933  清沢満之 1903  西田幾多郎 1945

青空文庫 holds 433 of their works. This downloads the plain-text file for each
and strips the format's furniture: the ruby readings in 《…》, the ruby anchor
｜, the editorial notes in ［＃…］, and the header and licence blocks the file
wraps every work in. What is left is the running text, in the author's own
orthography — 舊字舊假名 where they wrote that way, which for this volume is
the point rather than a problem.

The corpus feeds two things: the fifty readings of 第二冊, and the frequency
rule that extends the vocabulary past where the textbook ends.

    python -X utf8 scripts/fetch_japanese_corpus.py            # 看清單
    python -X utf8 scripts/fetch_japanese_corpus.py --write
"""

from __future__ import annotations

import argparse
import io
import json
import re
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full/aozora"
INDEX = CACHE / "index.json"
TEXTS = CACHE / "texts"
MANIFEST = CACHE / "manifest.json"

HEADERS = {"User-Agent": "know-graph-lab private reader build (contact: redpiigpig)"}

RUBY = re.compile(r"《[^》]*》")
ANCHOR = re.compile(r"｜")
NOTE = re.compile(r"［＃[^］]*］")
RULE = re.compile(r"^-{10,}$", re.M)


def clean(text: str) -> str:
    """The running text, with 青空文庫's markup and wrappers removed."""

    # The files are Shift_JIS with CRLF, so a rule line ends in a carriage
    # return and a pattern anchored with $ then matches nothing at all — the
    # header rides into the text and the first page of every reading becomes
    # 【テキスト中に現れる記号について】. Normalise the line endings first.
    text = text.replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))

    # 青空文庫 wraps an explanatory block between two rules of dashes, and it
    # sits *after* the title and author rather than at the very top — so taking
    # the third slice of a split leaves the title behind and keeps the block.
    # Cut out what lies between the first pair of rules, wherever they are.
    rules = [m.span() for m in RULE.finditer(text)]
    if len(rules) >= 2:
        text = text[: rules[0][0]] + text[rules[1][1] :]
    body = text.split("底本：")[0]
    body = NOTE.sub("", RUBY.sub("", body))
    body = ANCHOR.sub("", body)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def fetch(url: str) -> str | None:
    request = urllib.request.Request(url, headers=HEADERS)
    raw = urllib.request.urlopen(request, timeout=120).read()
    if url.endswith(".zip"):
        archive = zipfile.ZipFile(io.BytesIO(raw))
        members = [n for n in archive.namelist() if n.lower().endswith(".txt")]
        if not members:
            return None
        raw = archive.read(members[0])
    # 青空文庫's text files are Shift_JIS; a few later ones are UTF-8.
    for encoding in ("shift_jis", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("shift_jis", "replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = json.loads(INDEX.read_text(encoding="utf-8"))
    wanted = [r for r in rows if (r.get("テキストファイルURL") or "").strip()]
    print(f"書目 {len(rows)} 筆，其中有純文字檔的 {len(wanted)}")
    by_author: dict[str, int] = {}
    for row in wanted:
        by_author[f'{row.get("姓", "")}{row.get("名", "")}'] = by_author.get(
            f'{row.get("姓", "")}{row.get("名", "")}', 0
        ) + 1
    for author, count in sorted(by_author.items(), key=lambda kv: -kv[1]):
        print(f"  {author}：{count} 篇")

    if not args.write:
        print("（未下載；加 --write）")
        return 0

    TEXTS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    todo = [r for r in wanted if r["作品ID"] not in manifest]
    if args.limit:
        todo = todo[: args.limit]
    print(f"待下載 {len(todo)}")

    for index, row in enumerate(todo, start=1):
        path = TEXTS / f'{row["作品ID"]}.txt'
        try:
            raw = fetch(row["テキストファイルURL"])
            if raw is None:
                raise ValueError("壓縮檔裡沒有 txt")
            body = clean(raw)
        except Exception as error:  # noqa: BLE001 - re-runnable
            print(f"  ✗ {row['作品名']}：{error}")
            continue
        path.write_text(body, encoding="utf-8")
        manifest[row["作品ID"]] = {
            "title": row["作品名"],
            "author": f'{row.get("姓", "")}{row.get("名", "")}',
            "died": row.get("没年月日", ""),
            "firstPublished": row.get("初出", ""),
            "orthography": row.get("文字遣い種別", ""),
            "copyrightFlag": row.get("作品著作権フラグ", ""),
            "sourceUrl": row["テキストファイルURL"],
            "chars": len(body),
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        }
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        if index % 20 == 0:
            print(f"  … {index}/{len(todo)}", flush=True)
        time.sleep(0.6)

    total = sum(item["chars"] for item in manifest.values())
    print(f"完成 {len(manifest)} 篇，合計 {total:,} 字")
    flagged = [v["title"] for v in manifest.values() if v["copyrightFlag"] not in ("なし", "")]
    if flagged:
        print(f"  ⚠ 著作權旗標非「なし」的 {len(flagged)} 篇，收之前要逐篇確認：{flagged[:5]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
