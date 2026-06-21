#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""組裝創生哲學叢書某一冊的 book HTML（idempotent，可重跑）。

讀 c:/tmp/genesis_<series>/draft/<BOOK>/ 下的 _preface.html / NN.html / _coda.html，
抽出 body 片段、每章包成 <section class="chapter">，前綴沿用既有部署檔的
<header class="book-head">…</header>，序放章前、跋放章後，輸出到
public/content/works/genesis/<BOOK>.html。

精修後重新部署、或日後回填對話編號引用（改 draft 後）只要再跑一次本腳本即可。

用法：
  python scripts/assemble_genesis_book.py ethics A 10 B 10 C 8
  （series 後接 BOOK nChapters 的成對參數）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public" / "content" / "works" / "genesis"


def strip_to_body(s: str) -> str:
    """若是完整 HTML doc 取 <body> 內容，否則原樣。"""
    if "<body>" in s:
        s = s.split("<body>", 1)[1].split("</body>", 1)[0]
    return s


def chapter_fragment(s: str) -> str:
    s = strip_to_body(s)
    i = s.find("<h2")
    j = s.rfind("</section>")
    if i != -1 and j != -1 and j > i:
        return s[i : j + len("</section>")].strip()
    if i != -1:
        return s[i:].strip()
    return s.strip()


def section_fragment(s: str) -> str:
    s = strip_to_body(s)
    i = s.find("<section")
    j = s.rfind("</section>")
    if i != -1 and j != -1 and j > i:
        return s[i : j + len("</section>")].strip()
    return s.strip()


def existing_header(book: str) -> str:
    f = OUT_DIR / f"{book}.html"
    if not f.exists():
        raise SystemExit(f"找不到既有部署檔 {f}（需沿用其 <header>）")
    m = re.search(r'<header class="book-head">.*?</header>', f.read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit(f"{f} 內找不到 <header class=\"book-head\">")
    return m.group(0)


def assemble(series: str, book: str, n_chapters: int) -> None:
    draft = Path("c:/tmp") / f"genesis_{series}" / "draft" / book
    parts = [existing_header(book)]

    pre = draft / "_preface.html"
    if pre.exists():
        parts.append(section_fragment(pre.read_text(encoding="utf-8")))

    for ch in range(1, n_chapters + 1):
        f = draft / f"{ch:02d}.html"
        if not f.exists():
            raise SystemExit(f"缺章 {f}")
        parts.append(f'<section class="chapter">{chapter_fragment(f.read_text(encoding="utf-8"))}</section>')

    coda = draft / "_coda.html"
    if coda.exists():
        parts.append(section_fragment(coda.read_text(encoding="utf-8")))

    out = OUT_DIR / f"{book}.html"
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"  寫出 {out}  ({n_chapters} 章, {out.stat().st_size:,} bytes)")


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 3:
        raise SystemExit(__doc__)
    series = args[0]
    rest = args[1:]
    if len(rest) % 2 != 0:
        raise SystemExit("BOOK 與 nChapters 必須成對")
    print(f"series={series}")
    for i in range(0, len(rest), 2):
        book, n = rest[i], int(rest[i + 1])
        print(f"組裝 {book}（{n} 章）…")
        assemble(series, book, n)
    print("完成。")


if __name__ == "__main__":
    main()
