"""河合隼雄心理學經典（讀客熊貓君版‧套裝共 6 冊）→ /collected-works 全集。

collected-works 的 REFERENCE / 單一語言案例：來源是一份「簡體中文既有譯本」EPUB
（乾淨電子書，非掃描），內含 6 冊。做法比照 [[feedback_collected_works_reference_first]]：
既有中譯直接當主欄、零 LLM 翻譯、不寫 source_text（reader 退化單欄）；簡→繁走
standardize_ebook.to_traditional（opencc s2tw + TRAD_FIXES，[[feedback_traditional_chinese_only]]）。

套書拆冊（[[feedback_set_books_split]]）：每冊 = 一個 ebooks row；一節（xhtml part）= 一個 chunk。
collection='collected-works' → 不進圖書館（[[feedback_collected_works_not_in_library]]）；
入庫後另跑 scripts/apply-ebooks-quality-collection.mjs 靠 store ebookId 補標。

來源 EPUB 結構（OEBPS/Text/partNNNN.xhtml，spine 依 part 編號序）：
  每冊 = [書名頁][半書名頁][該冊目錄頁] + 內文 parts。6 冊書名頁見 BOOKS。
  toc.ncx 兩層 navMap（章 → 節）→ 建 part → (章, 節) chapter_path。

純解析零 network/DB 的函式（extract_part_text / build_chapter_map / split_paras）由
scripts/tests/test_kawai_build.py 鎖定。upload 重用 translate_ebook_to_zh / standardize_ebook。

  python scripts/kawai_build.py --inspect            # 印 6 冊 part 範圍 + chunk 計數 + 樣本
  python scripts/kawai_build.py --book fantasy        # 建一冊（不上傳）
  python scripts/kawai_build.py --all --upload        # 6 冊 → s2tw → R2 + DB
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

EPUB_PATH = Path(
    r"G:\我的雲端硬碟\資料\知識圖工作室\全集\心理學\河合隼雄"
    r"\河合隼雄心理学经典（读客熊猫君出品，套装共6册。村上春树推崇的心灵导师河合隼雄！）"
    r" (河合隼雄  吉本芭娜娜  河合俊雄) (z-library.sk, 1lib.sk, z-lib.sk).epub"
)
PARENT_VOLUME = "河合隼雄心理學經典（讀客熊貓君版‧共六冊）"
EBID = "ca7a1928-0000-4000-8000-00000000000{}"  # ca7a≈kawai, 1928=生年；末位 1–6

# 6 冊：slug / 繁中書名 / 日文原名 / 原著初版年 / 內文 part 範圍（含頭尾，依 part 編號）。
# 範圍前的 書名頁/半書名頁/目錄頁 一律略過（非內文）。
BOOKS = [
    {"slug": "fantasy", "n": 1, "title": "讀幻想文學",
     "original": "ファンタジーを読む", "year": 1991, "start": 4, "end": 71},
    {"slug": "naruhodo", "n": 2, "title": "原來如此的對談",
     "original": "なるほどの対話（與吉本芭娜娜對談）", "year": 2002, "start": 75, "end": 108},
    {"slug": "otona", "n": 3, "title": "長大成人的難處",
     "original": "大人になることのむずかしさ", "year": 1983, "start": 112, "end": 136},
    {"slug": "monogatari", "n": 4, "title": "故事與神奇",
     "original": "物語とふしぎ", "year": 2007, "start": 140, "end": 164},
    {"slug": "neko", "n": 5, "title": "貓魂",
     "original": "猫だましい", "year": 2000, "start": 168, "end": 182},
    {"slug": "seishun", "n": 6, "title": "青春就是夢和遊戲",
     "original": "青春の夢と遊び", "year": 2005, "start": 186, "end": 211},
]
BY_SLUG = {b["slug"]: b for b in BOOKS}

_SET_TITLE_RE = re.compile(r"^河合隼雄心理学经典")


# ── 純解析函式（test-locked，零 network/DB）─────────────────────────────

class _TextExtractor(HTMLParser):
    """收集 xhtml 內文；<p>/<div>/<h*>/<br> 視為段落邊界。"""
    _BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "br", "blockquote"}

    def __init__(self):
        super().__init__()
        self._buf: list[str] = []
        self.paras: list[str] = []

    def _flush(self):
        s = "".join(self._buf).strip()
        if s:
            self.paras.append(s)
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag in self._BLOCK:
            self._flush()

    def handle_endtag(self, tag):
        if tag in self._BLOCK:
            self._flush()

    def handle_data(self, data):
        self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


def extract_part_text(html: str) -> list[str]:
    """xhtml → 乾淨段落 list。去掉整段等同套書總標題的頁（書名頁/半書名頁）。"""
    p = _TextExtractor()
    p.feed(html)
    p.close()
    out = []
    for s in p.paras:
        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            continue
        if _SET_TITLE_RE.match(s):  # 書名頁/半書名頁/頁眉殘留
            continue
        out.append(s)
    return out


def build_chapter_map(ncx_xml: str) -> dict[str, tuple[str, str | None]]:
    """toc.ncx → { 'partNNNN.xhtml': (章, 節|None) }。

    兩層 navMap：深度 0 = 章、深度 1 = 節。每個 part 取「第一個指向它的 nav」，
    section 為該 nav 若在深度 1。走訪時維持 current_chapter（最近的深度 0 標籤）。
    """
    xml = re.sub(r'xmlns(:\w+)?="[^"]+"', "", ncx_xml)  # 去 namespace
    root = ET.fromstring(xml)
    navmap = root.find("navMap")
    out: dict[str, tuple[str, str | None]] = {}
    cur_chapter = ""

    def part_of(src: str) -> str:
        return src.split("/")[-1].split("#")[0]

    def walk(el, depth):
        nonlocal cur_chapter
        for np in el.findall("navPoint"):
            lab = (np.find("navLabel/text").text or "").strip()
            src = np.find("content").get("src")
            part = part_of(src)
            if depth == 0:
                cur_chapter = lab
                out.setdefault(part, (lab, None))
            else:
                out.setdefault(part, (cur_chapter, lab))
            walk(np, depth + 1)

    walk(navmap, 0)
    return out


def split_paras(paras: list[str]) -> str:
    """段落 list → markdown（段間空行）。"""
    return "\n\n".join(paras)


# ── EPUB 讀取 + 組冊（有 I/O）──────────────────────────────────────────

def _open_epub() -> zipfile.ZipFile:
    if not EPUB_PATH.exists():
        raise SystemExit(f"找不到來源 EPUB：{EPUB_PATH}")
    return zipfile.ZipFile(EPUB_PATH)


def _content_parts(book: dict) -> list[str]:
    return [f"part{n:04d}.xhtml" for n in range(book["start"], book["end"] + 1)]


def build_book(book: dict, *, to_trad, chapter_map: dict) -> list[dict]:
    """一冊 → chunk list（cover + 每 content part 一 chunk）。to_trad: 簡→繁函式。"""
    z = _open_epub()
    title = book["title"]
    cover_body = f"# {title}\n\n{PARENT_VOLUME}\n\n日文原名：{book['original']}（{book['year']}）"
    chunks = [{
        "chunk_index": 0, "chunk_type": "cover", "page_number": 0,
        "chapter_path": title, "volume": title, "parent_volume": PARENT_VOLUME,
        "format": "markdown", "content": cover_body,
    }]
    idx = 0
    carry_chapter, carry_section = "", None
    for part in _content_parts(book):
        try:
            html = z.read(f"OEBPS/Text/{part}").decode("utf-8")
        except KeyError:
            continue
        paras = extract_part_text(html)
        if not paras:
            continue
        chap, sec = chapter_map.get(part, (carry_chapter, carry_section))
        if part in chapter_map:
            carry_chapter, carry_section = chap, sec
        else:
            chap, sec = carry_chapter, carry_section  # 續接無 nav 的 part
        path_parts = [title, chap] + ([sec] if sec else [])
        chapter_path = " · ".join(p for p in path_parts if p)
        body = to_trad(split_paras(paras))
        idx += 1
        chunks.append({
            "chunk_index": idx, "chunk_type": "chapter", "page_number": idx,
            "chapter_path": to_trad(chapter_path), "volume": title,
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

    total = sum(len(c["content"]) for c in chunks)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {
        "id": ebid, "title": book["title"], "author": "河合隼雄", "author_en": "Hayao Kawai",
        "original_title": book["original"], "file_type": "epub",
        "file_path": f"全集/心理學/河合隼雄/{PARENT_VOLUME}/{book['title']}",
        "category": "心理學", "subcategory": "分析心理學", "display_mode": "standard",
        "collection": "collected-works",
        "translator": None, "publication_year": book["year"],
        "chunk_count": len(chunks), "total_pages": len(chunks), "total_chars": total,
        "parsed_at": now, "standardized_at": now,
    }
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebid}", headers=te.H_GET, timeout=30)
    rows = [{
        "ebook_id": ebid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
        "page_number": c["page_number"], "chapter_path": c["chapter_path"],
        "content": c["content"][:200], "char_count": len(c["content"]),
    } for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[i:i + 25], timeout=60)
    print(f"    ✓ DB ebooks+previews  chunk_count={len(chunks)}  {ebid}", flush=True)


def _load_chapter_map() -> dict:
    z = _open_epub()
    ncx = z.read("OEBPS/toc.ncx").decode("utf-8")
    z.close()
    return build_chapter_map(ncx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", type=str, help="slug: " + ", ".join(BY_SLUG))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    from standardize_ebook import to_traditional
    cmap = _load_chapter_map()

    if a.inspect:
        for b in BOOKS:
            chunks = build_book(b, to_trad=to_traditional, chapter_map=cmap)
            chars = sum(len(c["content"]) for c in chunks)
            print(f"[{b['n']}] {b['title']}（{b['original']}）  "
                  f"parts {b['start']}–{b['end']}  chunks={len(chunks)}  {chars:,}字  {EBID.format(b['n'])}")
            for c in chunks[1:4]:
                print(f"     · {c['chapter_path']}  |  {c['content'][:60].replace(chr(10), ' ')}…")
        return

    targets = BOOKS if a.all else [BY_SLUG[a.book]] if a.book else []
    if not targets:
        ap.error("需 --inspect / --book <slug> / --all")
    for b in targets:
        chunks = build_book(b, to_trad=to_traditional, chapter_map=cmap)
        print(f"[{b['n']}] {b['title']}: {len(chunks)} chunks | "
              f"{sum(len(c['content']) for c in chunks):,} 字", flush=True)
        if a.upload:
            _upload(b, chunks)


if __name__ == "__main__":
    main()
