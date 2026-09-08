#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把《無境界者》已刊的〈基督宗教宗派譜系學初探〉三篇轉成 /works 書稿卷（idempotent）。

來源是 Drive 上的雜誌原稿 docx（唯讀），輸出 public/content/works/christian-genealogy/
底下的 G1 / G2 / G5。未刊的 G0（導論）、G3（卷三）、G4（卷四）是人工底稿，
不由本腳本產生，也不會被覆寫。

docx → 書稿的對應：
  粗體 14pt          → <h2>  一章
  粗體（繼承字級）    → <h3>  一節
  10pt              → 圖說（連續數行併成一段）
  w:tbl             → <table>
  footnoteReference → <sup class="footnote-ref">，每章末尾一個 .footnotes 區塊

雜誌排版遺留的圖框錨點（"-381019494500"、"center30099000"、"right0…"）會被剝掉，
但只剝行首那一串數字，正文一個字都不動。

用法：python scripts/christian_genealogy_build.py [--check]
"""
from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public" / "content" / "works" / "christian-genealogy"
DRIVE = Path("G:/我的雲端硬碟/資料/無境界者/雜誌")

# 卷 → (docx, 卷次題頭, 書名頁副標, 出處)
SOURCES = [
    {
        "id": "G1",
        "docx": DRIVE / "05-第五期" / "5-9尼西亞基督教的形成.docx",
        "kicker": "基督宗教譜系學‧卷一",
        "title": "正統的劃界",
        "sub": "尼西亞基督教的形成",
        "cite": "原刊：張辰瑋，〈尼西亞基督教的形成──基督宗教宗派譜系學初探（一）〉，"
        "《無境界者》第5期（2025.10），頁55-72。書稿版依原文轉錄，尚未改寫。",
    },
    {
        "id": "G2",
        "docx": DRIVE / "07-第七期" / "7-16基督宗教的七個大公傳統.docx",
        "kicker": "基督宗教譜系學‧卷二",
        "title": "教系的成形",
        "sub": "基督宗教的七個大公傳統",
        "cite": "原刊：張辰瑋，〈基督宗教的七個大公傳統──基督宗教宗派譜系學初探（二）〉，"
        "《無境界者》第7期（2026.02），頁212-229。書稿版依原文轉錄，尚未改寫。",
    },
    {
        "id": "G5",
        "docx": DRIVE / "08-第八期" / "8-16主教制的歷史演變與教會的大公性.docx",
        "kicker": "基督宗教譜系學‧附卷",
        "title": "主教制與教會的大公性",
        "sub": "聖秩、使徒統緒與普世運動",
        "cite": "原刊：張辰瑋，〈主教制的歷史演變與教會的大公性──基督宗教宗派譜系學初探（番外篇）〉，"
        "《無境界者》第8期（2026）。書稿版依原文轉錄，尚未改寫。",
    },
]

ANCHOR = re.compile(r"^(?:center|right|left|top|bottom|inline)?-?\d{2,}")
DROP_EXACT = {"。", "【專題文章】"}


def _runs(p):
    """(text, footnote_ids, bold, size_pt) for one w:p."""
    text, fns, bolds, size = [], [], [], None
    for r in p.iter(f"{W}r"):
        rpr = r.find(f"{W}rPr")
        chunk = "".join(t.text or "" for t in r.iter(f"{W}t"))
        for ref in r.iter(f"{W}footnoteReference"):
            fid = ref.get(f"{W}id")
            if fid:
                fns.append((len("".join(text)) + len(chunk), fid))
        if chunk.strip():
            b = rpr is not None and rpr.find(f"{W}b") is not None
            bolds.append(b)
            if size is None and rpr is not None:
                sz = rpr.find(f"{W}sz")
                if sz is not None and sz.get(f"{W}val"):
                    size = int(sz.get(f"{W}val")) / 2
        text.append(chunk)
    return "".join(text), fns, (bool(bolds) and all(bolds)), size


def _footnotes(zf: zipfile.ZipFile) -> dict[str, str]:
    """footnote id → 已轉義的 HTML（保留斜體）。"""
    out = {}
    if "word/footnotes.xml" not in zf.namelist():
        return out
    root = ET.fromstring(zf.read("word/footnotes.xml"))
    for fn in root.iter(f"{W}footnote"):
        fid = fn.get(f"{W}id")
        # separator / continuationSeparator 才是分隔符；真正的註腳從 id=1 起，
        # 不能靠 id 判斷（第一條註腳就是 id=1）。
        if fid is None or fn.get(f"{W}type"):
            continue
        parts = []
        for p in fn.iter(f"{W}p"):
            for r in p.iter(f"{W}r"):
                rpr = r.find(f"{W}rPr")
                s = html.escape("".join(t.text or "" for t in r.iter(f"{W}t")))
                if s and rpr is not None and rpr.find(f"{W}i") is not None:
                    s = f"<em>{s}</em>"
                parts.append(s)
        body = "".join(parts).strip()
        # 註腳首字是自動編號留下的空白／製表
        body = re.sub(r"^[\s\u00a0]+", "", body)
        if body:
            out[fid] = body
    return out


def _table_html(tbl) -> str:
    rows = []
    for tr in tbl.findall(f"{W}tr"):
        cells = []
        for tc in tr.findall(f"{W}tc"):
            txt = " ".join(
                "".join(t.text or "" for t in p.iter(f"{W}t")).strip()
                for p in tc.iter(f"{W}p")
            ).strip()
            cells.append(html.escape(txt))
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    head = "".join(f"<th>{c}</th>" for c in rows[0])
    body = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:]
    )
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + body
        + "</tbody></table></div>"
    )


def parse(path: Path):
    """docx → (header_lines, blocks)；blocks 是 (kind, payload) 串。"""
    with zipfile.ZipFile(path) as zf:
        doc = ET.fromstring(zf.read("word/document.xml"))
        notes = _footnotes(zf)
    body = doc.find(f"{W}body")
    blocks, header = [], []
    seen_first_h2 = False
    for el in body:
        if el.tag == f"{W}tbl":
            t = _table_html(el)
            if t:
                blocks.append(("table", t))
            continue
        if el.tag != f"{W}p":
            continue
        raw, fns, bold, size = _runs(el)
        text = ANCHOR.sub("", raw).strip()
        if not text or text in DROP_EXACT:
            continue
        if not seen_first_h2:
            # 書名頁那幾行：標題(24)／副標(16)／作者／學歷／關鍵字
            if not (bold and size == 14.0):
                header.append(text)
                continue
        if bold and size == 14.0:
            seen_first_h2 = True
            blocks.append(("h2", (text, fns)))
        elif bold and size is None:
            blocks.append(("h3", (text, fns)))
        elif size is not None and size <= 10.5:
            blocks.append(("cap", text))
        else:
            blocks.append(("p", (text, fns, raw)))
    return header, blocks, notes


def render(src: dict) -> str:
    header, blocks, notes = parse(src["docx"])
    vid = src["id"].lower()
    keywords = next((h for h in header if h.startswith("🌿")), "")

    out = [
        '<header class="book-head">',
        f'<p class="book-kicker">{html.escape(src["kicker"])}</p>',
        f'<h1 class="book-title">{html.escape(src["title"])}</h1>',
        f'<p class="book-sub">{html.escape(src["sub"])}</p>',
    ]
    if keywords:
        out.append(f'<p class="book-thesis">{html.escape(keywords.lstrip("🌿"))}</p>')
    out.append(f'<p class="book-meta">張辰瑋　　{html.escape(src["cite"])}</p>')
    out.append("</header>\n")

    n = 0          # 章序
    fnum = 0       # 全卷連續註號
    chap: list[str] = []
    chap_notes: list[tuple[int, str]] = []

    def flush():
        if not chap:
            return
        if chap_notes:
            chap.append('<div class="footnotes">')
            for num, body in chap_notes:
                chap.append(
                    f'<div class="fn-item" id="fn-{vid}-{num}">'
                    f'<span class="fn-num">{num}</span>'
                    f'<div class="fn-body">{body}'
                    f'<a href="#fnref-{vid}-{num}" class="footnote-backref">↩</a>'
                    f"</div></div>"
                )
            chap.append("</div>")
        chap.append("</section>\n")
        out.append("\n".join(chap))
        chap.clear()
        chap_notes.clear()

    def marker(fns) -> str:
        """標題上的註號：註文歸入該標題所屬的章。"""
        nonlocal fnum
        out_m = []
        for _pos, fid in fns:
            if fid not in notes:
                continue
            fnum += 1
            chap_notes.append((fnum, notes[fid]))
            out_m.append(
                f'<sup class="footnote-ref">'
                f'<a href="#fn-{vid}-{fnum}" id="fnref-{vid}-{fnum}">{fnum}</a></sup>'
            )
        return "".join(out_m)

    for kind, payload in blocks:
        if kind == "h2":
            flush()
            n += 1
            payload, h_fns = payload
            chap.append(
                f'<section class="chapter"><h2>第{n}節　{html.escape(payload)}'
                f'{marker(h_fns)}</h2>\n'
            )
        elif not chap:
            continue  # 章前的孤兒段落（雜誌排版殘留）
        elif kind == "h3":
            head, h_fns = payload
            chap.append(f"<h3>{html.escape(head)}{marker(h_fns)}</h3>")
        elif kind == "cap":
            chap.append(f'<p class="fig-cap">{html.escape(payload)}</p>')
        elif kind == "table":
            chap.append(payload)
        else:
            text, fns, raw = payload
            # 註號按 raw 的位置插回 text：兩者只差行首錨點，用尾端對齊
            shift = len(raw) - len(raw.lstrip()) - (len(raw) - len(text))
            marks = []
            for pos, fid in fns:
                if fid not in notes:
                    continue
                fnum += 1
                chap_notes.append((fnum, notes[fid]))
                marks.append((max(0, pos - shift), fnum))
            esc = html.escape(text)
            if marks:
                # 由後往前插，位置以未轉義字串計，故先切片再轉義
                pieces, last = [], len(text)
                for pos, num in reversed(marks):
                    pos = min(pos, len(text))
                    pieces.append(html.escape(text[pos:last]))
                    pieces.append(
                        f'<sup class="footnote-ref">'
                        f'<a href="#fn-{vid}-{num}" id="fnref-{vid}-{num}">{num}</a></sup>'
                    )
                    last = pos
                pieces.append(html.escape(text[:last]))
                esc = "".join(reversed(pieces))
            chap.append(f"<p>{esc}</p>")
    flush()
    return "\n".join(out)


def main() -> int:
    check = "--check" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bad = 0
    for src in SOURCES:
        if not src["docx"].exists():
            print(f"MISSING {src['docx']}")
            bad += 1
            continue
        html_out = render(src)
        n_ch = html_out.count('<section class="chapter">')
        n_fn = html_out.count('class="fn-item"')
        n_ref = html_out.count('class="footnote-ref"')
        status = "OK " if n_ch and n_fn == n_ref else "FAIL"
        if n_fn != n_ref:
            bad += 1
        print(f"{status} {src['id']}  {n_ch} 節 / 註號 {n_ref} 對 註文 {n_fn} / {len(html_out):,} 字元")
        if not check:
            (OUT_DIR / f"{src['id']}.html").write_text(html_out, encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
