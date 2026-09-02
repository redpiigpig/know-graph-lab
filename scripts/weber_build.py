#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""馬克斯‧韋伯全集（宗教社會學）→ /collected-works：REFERENCE 轉錄既有繁中譯本。

user 2026-07-23 拍板走 REFERENCE（[[feedback_collected_works_reference_first]]）：韋伯
1920 卒、德文原著全數公有領域，但中文世界已有成熟譯本，重譯不划算 → 把 Drive 全集夾
裡的既有中譯直接轉錄成 reader 可讀的 chunks，零 LLM、不寫 source_text（reader 單欄）。
同一著作有多譯本時取「繁體優先、繁體中取最新出版年」
（[[feedback_collected_works_latest_traditional_edition]]）——所以兩篇志業演講用李中文
（暖暖書屋）而非《學術與政治》選集本。

來源 G:\\...\\全集\\宗教社會學\\韋伯\\ 有九本，分三類：
  * EPUB（乾淨電子書）── 本檔處理，spine 逐節切 chunk。
  * 文字層 PDF（韋伯方法論文集、學術與政治選集）── 待接。
  * 掃描 PDF（宗教社會學、新教倫理、社會科學方法論…五本簡體）── 要先 OCR，另議。

解析與切段沿用 kawai_build 的純函式（同樣是「既有中譯 EPUB → chunks」的形狀）。

  python scripts/weber_build.py --inspect
  python scripts/weber_build.py --book vocation-science --upload
  python scripts/weber_build.py --all --upload
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from kawai_build import extract_part_text, split_paras  # noqa: E402

SRC_DIR = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集\宗教社會學\韋伯")
PARENT_VOLUME = "馬克斯‧韋伯全集"
EBID = "18640000-0000-4000-8000-0000000000{:02d}"  # 1864 = 生年；末兩位 = BOOKS 的 n

BOOKS = [
    {"slug": "vocation-science", "n": 1, "title": "以學術為志業",
     "original": "Wissenschaft als Beruf", "year": 1919, "pub_year": 2018,
     "translator": "李中文", "publisher": "暖暖書屋",
     "file": "以學術為志業 = Wissenschaft als Beruf (馬克斯 · 韋伯 (Max Weber) 著  李中文 譯) "
             "(z-library.sk, 1lib.sk, z-lib.sk).epub"},
    {"slug": "vocation-politics", "n": 2, "title": "以政治為志業",
     "original": "Politik als Beruf", "year": 1919, "pub_year": 2020,
     "translator": "李中文", "publisher": "暖暖書屋",
     "file": "以政治為志業 = Politik als Beruf (馬克斯 · 韋伯 (Max Weber) 著  李中文 譯) "
             "(z-library.sk, 1lib.sk, z-lib.sk).epub"},
]
BY_SLUG = {b["slug"]: b for b in BOOKS}

# 封面、導航、書末書訊不是內文；照片頁沒有文字，抽出來是空的自然會被略過。
_SKIP = re.compile(r"(cover|nav|Review)\.xhtml$", re.I)

# ncx 沒收進目錄的幾個檔，總比「第 N 節」有交代。
_FILE_LABEL = {"Photograph": "書前圖像與書介", "Note1": "註釋",
               "Glossay": "譯名對照表", "Glossary": "譯名對照表"}


# ── 純解析函式（零 network/DB）────────────────────────────────────────

def spine_hrefs(opf_xml: str) -> list[str]:
    """content.opf → 依 spine 順序的內文 href（相對 OPF 所在目錄）。"""
    root = ET.fromstring(opf_xml)
    ns = {"o": "http://www.idpf.org/2007/opf"}
    manifest = {i.get("id"): i.get("href") for i in root.findall(".//o:manifest/o:item", ns)}
    out = []
    for ref in root.findall(".//o:spine/o:itemref", ns):
        href = manifest.get(ref.get("idref"))
        if href and not _SKIP.search(href):
            out.append(href)
    return out


def ncx_entries(ncx_xml: str) -> list[tuple[str, str | None, str]]:
    """toc.ncx → 依序 [(檔名, anchor|None, 標題)]。

    這兩本的正文整篇裝在一個 01.xhtml 裡，十來個小節全靠 `#sigil_toc_id_N` 錨點
    區分。只看檔名就會把三萬字的演講變成一個 chunk，所以錨點必須留著。
    """
    root = ET.fromstring(ncx_xml)
    ns = {"n": "http://www.daisy.org/z3986/2005/ncx/"}
    out: list[tuple[str, str | None, str]] = []
    for pt in root.findall(".//n:navPoint", ns):
        text = pt.find("./n:navLabel/n:text", ns)
        content = pt.find("./n:content", ns)
        if text is None or content is None:
            continue
        src = content.get("src") or ""
        name, _, anchor = src.split("/")[-1].partition("#")
        if name:
            out.append((name, anchor or None, (text.text or "").strip()))
    return out


def split_by_anchors(html: str, anchors: list[str]) -> list[tuple[str | None, str]]:
    """xhtml → [(anchor|None, 片段)]，依錨點在文件中出現的先後切開。

    錨點前的內容（篇題、編者說明）歸在 anchor=None 的第一片；找不到任何錨點就整檔一片。
    """
    hits = []
    for a in anchors:
        m = re.search(rf"""<[^>]*\bid=["']{re.escape(a)}["']""", html)
        if m:
            hits.append((m.start(), a))
    hits.sort()
    if not hits:
        return [(None, html)]
    out: list[tuple[str | None, str]] = []
    if hits[0][0] > 0:
        out.append((None, html[:hits[0][0]]))
    for i, (pos, a) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(html)
        out.append((a, html[pos:end]))
    return out


# ── 組冊（有 I/O）────────────────────────────────────────────────────

def build_book(book: dict, *, to_trad) -> list[dict]:
    z = zipfile.ZipFile(SRC_DIR / book["file"])
    opf = next(n for n in z.namelist() if n.endswith("content.opf"))
    base = opf.rsplit("/", 1)[0] if "/" in opf else ""
    hrefs = spine_hrefs(z.read(opf).decode("utf-8"))
    ncx = next((n for n in z.namelist() if n.endswith(".ncx")), None)
    entries = ncx_entries(z.read(ncx).decode("utf-8")) if ncx else []
    per_file: dict[str, list[tuple[str | None, str]]] = {}
    for name, anchor, label in entries:
        per_file.setdefault(name, []).append((anchor, label))

    title = book["title"]
    head = (f"# {title}\n\n{PARENT_VOLUME}\n\n"
            f"德文原名：{book['original']}（{book['year']}）\n\n"
            f"中譯：{book['translator']}（{book['publisher']}，{book['pub_year']}）")
    chunks = [{"chunk_index": 0, "chunk_type": "cover", "page_number": 0,
               "chapter_path": title, "volume": title, "parent_volume": PARENT_VOLUME,
               "format": "markdown", "content": head}]
    idx = 0
    for href in hrefs:
        name = href.split("/")[-1]
        try:
            html = z.read(f"{base}/{href}" if base else href).decode("utf-8")
        except KeyError:
            continue
        specs = per_file.get(name, [])
        anchor_labels = {a: lab for a, lab in specs if a}
        file_label = (next((lab for a, lab in specs if not a), None)
                      or _FILE_LABEL.get(name.rsplit(".", 1)[0]))
        for anchor, frag in split_by_anchors(html, list(anchor_labels)):
            body = to_trad(split_paras(extract_part_text(frag)))
            if len(body.strip()) < 40:  # 照片頁、空白頁、錨點前的殘頭
                continue
            idx += 1
            label = anchor_labels.get(anchor) or file_label or f"第 {idx} 節"
            chunks.append({
                "chunk_index": idx, "chunk_type": "chapter", "page_number": idx,
                "chapter_path": to_trad(f"{title} · {label}"), "volume": title,
                "parent_volume": PARENT_VOLUME, "format": "markdown", "content": body,
            })
    z.close()
    return chunks


def _upload(book: dict, chunks: list[dict]):
    import datetime
    import requests
    import translate_ebook_to_zh as te

    ebid = EBID.format(book["n"])
    out = te.CHUNKS_DIR / f"{ebid}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    try:
        te.se.push_to_r2(ebid, out)
        print("    ✓ R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"    ⚠ R2 失敗: {e}", flush=True)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {
        "id": ebid, "title": book["title"], "author": "馬克斯‧韋伯", "author_en": "Max Weber",
        "original_title": book["original"], "file_type": "epub",
        "file_path": f"全集/宗教社會學/韋伯/{book['file']}",
        "category": "宗教社會學", "subcategory": "支配與理性化", "display_mode": "standard",
        "collection": "collected-works", "translator": book["translator"],
        "publisher": book["publisher"], "publication_year": book["pub_year"],
        "original_publish_year": book["year"],
        "chunk_count": len(chunks), "total_pages": len(chunks),
        "total_chars": sum(len(c["content"]) for c in chunks),
        "parsed_at": now, "standardized_at": now,
    }
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    r = requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    if r.status_code >= 300:  # PostgREST 把撞了哪條約束寫在 body 裡
        raise SystemExit(f"    ✗ ebooks {r.status_code} {r.text[:300]}")
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebid}", headers=te.H_GET, timeout=30)
    rows = [{
        "ebook_id": ebid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
        "page_number": c["page_number"], "chapter_path": c["chapter_path"],
        "content": c["content"][:200], "char_count": len(c["content"]),
    } for c in chunks]
    for i in range(0, len(rows), 25):
        rr = requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON,
                           json=rows[i:i + 25], timeout=60)
        if rr.status_code >= 300:
            raise SystemExit(f"    ✗ chunks {rr.status_code} {rr.text[:300]}")
    print(f"    ✓ DB ebooks+previews  chunk_count={len(chunks)}  {ebid}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="slug: " + ", ".join(BY_SLUG))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    from standardize_ebook import to_traditional

    targets = BOOKS if (a.all or a.inspect) else [BY_SLUG[a.book]] if a.book else []
    if not targets:
        ap.error("需 --inspect / --book <slug> / --all")
    for b in targets:
        chunks = build_book(b, to_trad=to_traditional)
        chars = sum(len(c["content"]) for c in chunks)
        print(f"[{b['n']}] {b['title']}（{b['original']}）  chunks={len(chunks)}  {chars:,} 字  "
              f"{EBID.format(b['n'])}", flush=True)
        if a.inspect:
            for c in chunks[1:5]:
                print(f"     · {c['chapter_path']}  |  {c['content'][:60]}…")
        if a.upload:
            _upload(b, chunks)


if __name__ == "__main__":
    main()
