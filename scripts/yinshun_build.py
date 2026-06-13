"""印順導師全集 → reader 書（CBETA Y 系列 TEI P5 XML → 單語 JSONL → R2 + DB）。

collected-works 第一個「單一語言」案例：全集本即繁體中文 → 零翻譯、零跨語對齊。
pipeline = 解析 CBETA TEI（cb:div 巢狀章節樹 + 直屬 <p> 正文）→ 不含 sources 的
單欄 chunk（reader 向後相容退化單欄）→ R2 + ebooks/ebook_chunks。

來源：cbeta-org/xml-p5  Y/Y{NN}/Y{NN}n{NNNN}.xml（44 XML=42 部，非商業可再散布）。
方法論與卷目見 .claude/skills/ebook-collected-works/yinshun_collected_works.md。

純函式（parse_tei_chunks / extract_text / div_head 等）零 network/DB，由
scripts/tests/test_yinshun_build.py 鎖定。upload 重用 translate_ebook_to_zh / standardize_ebook。

  python scripts/yinshun_build.py --inspect --xml c:/tmp/Y08.xml   # 章節樹 + chunk 計數
  python scripts/yinshun_build.py --book Y08 --upload               # 一卷 → R2 + DB
  python scripts/yinshun_build.py --all --upload                   # 全 44 卷
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

TEI = "http://www.tei-c.org/ns/1.0"
CB = "http://www.cbeta.org/ns/1.0"
RAW = "https://raw.githubusercontent.com/cbeta-org/xml-p5/master/Y/{vol}/{stem}.xml"


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _clean(s: str) -> str:
    """殺掉 lb 換行（CBETA 用 \\n 折行，中文接行不插空格）與 XML 縮排，
    但保留真正的英文詞間空格與全形空格（U+3000，章節標題分隔用）。"""
    s = re.sub(r"[ \t]*\n[ \t\n]*", "", s)  # 折行：中文安全接合，不插空格
    s = re.sub(r"[ \t]+", " ", s).strip()   # 收斂剩餘真實空格
    return s


def extract_text(el: ET.Element) -> str:
    """遞迴取元素純文字：剝除 <note>（夾注/校注）整棵子樹、丟棄 <lb> 邊碼，
    其餘文字連續串接（印順正文是連續段落，邊碼只是換行不入文）。"""
    tag = _local(el.tag)
    if tag == "note":
        return ""
    if tag == "lb":  # 邊碼/換行：本身無文字，只回其 tail（由 parent 處理）
        return ""
    parts = [el.text or ""]
    for child in el:
        parts.append(extract_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def div_head(div: ET.Element) -> str:
    """取一個 div 的第一個非空 <head> 文字（CBETA 有時並列一個空 head）。"""
    for child in div:
        if _local(child.tag) == "head":
            txt = _clean(extract_text(child))
            if txt:
                return txt
    return ""


def _norm_para(p: ET.Element) -> str:
    return _clean(extract_text(p))


def parse_tei_chunks(xml_text: str, *, volume: str, parent_volume: str,
                     book_prefix: str = "") -> tuple[str, list[dict]]:
    """CBETA TEI XML → (書名, [chunk...])。

    走訪 body 的 div 巢狀：每個含「直屬 <p>」的 div 出一個 chunk，
    chapter_path = 祖先 div head 堆疊（含書名前綴）；巢狀 div 一律遞迴。
    chunk 無 sources → reader 單欄繁中。"""
    root = ET.fromstring(xml_text)
    m_titles = root.findall(f".//{{{TEI}}}titleStmt/{{{TEI}}}title")
    book = ""
    for t in m_titles:
        if t.get("level") == "m" and (t.get(f"{{http://www.w3.org/XML/1998/namespace}}lang") or "").startswith("zh"):
            book = (t.text or "").strip()
            break
    if not book:
        for t in m_titles:
            if t.get("level") == "m":
                book = (t.text or "").strip()
                break

    body = root.find(f".//{{{TEI}}}body")
    chunks: list[dict] = []
    counter = {"i": 0}
    root_label = book_prefix or book

    def walk(el: ET.Element, path: list[str]):
        direct_paras = [
            _norm_para(c) for c in el
            if _local(c.tag) == "p" and _norm_para(c)
        ]
        if direct_paras:
            counter["i"] += 1
            cp = " · ".join([root_label] + path) if path else root_label
            chunks.append({
                "chunk_index": counter["i"],
                "chunk_type": "chapter",
                "page_number": counter["i"],
                "chapter_path": cp,
                "volume": volume,
                "parent_volume": parent_volume,
                "format": "markdown",
                "content": "\n\n".join(direct_paras),
            })
        for c in el:
            if _local(c.tag) == "div":
                h = div_head(c)
                walk(c, path + [h] if h else path)

    if body is not None:
        walk(body, [])
    return book, chunks


# ── Registry：44 卷（vol code → stem / 書名 / volume / parent_volume）──────────
# 書名以 XML <title level="m"> 為準，--build-registry 自動回填；此處先放分組骨架。
PARENT_OF = {  # Y 卷號 → parent_volume 分組
    **{f"Y{n:02d}": "妙雲集" for n in range(1, 25)},
    **{f"Y{n:02d}": "華雨集" for n in range(25, 30)},
    **{f"Y{n:02d}": "專書" for n in range(30, 45)},
}
EBID_NS = "a0000000-0000-4000-8000-0000000000{:02d}"  # 44 卷 deterministic UUID


def registry_path() -> Path:
    return SCRIPT_DIR.parent / ".claude/skills/ebook-collected-works/yinshun_registry.json"


def load_registry() -> dict:
    p = registry_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def stem_for(vol: str, reg: dict) -> str:
    return reg[vol]["stem"]


def fetch_xml(vol: str, stem: str) -> str:
    import requests
    url = RAW.format(vol=vol, stem=stem)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.text


def build_book(vol: str, reg: dict, *, upload: bool) -> list[dict]:
    meta = reg[vol]
    xml_text = fetch_xml(vol, meta["stem"])
    book, chunks = parse_tei_chunks(
        xml_text, volume=meta["title"], parent_volume=meta["parent_volume"],
        book_prefix=meta["title"])
    cover = {"chunk_index": 0, "chunk_type": "chapter", "page_number": 0,
             "chapter_path": meta["title"], "volume": meta["title"],
             "parent_volume": meta["parent_volume"], "format": "markdown",
             "content": f"# {meta['title']}\n\n印順法師佛學著作集 · {meta['parent_volume']}"}
    allc = [cover] + chunks
    print(f"  {vol} {book}: {len(chunks)} 節 chunk | {sum(len(c['content']) for c in allc)} 字", flush=True)
    if upload:
        _upload(meta, allc)
    return allc


def _upload(meta: dict, chunks: list[dict]):
    import datetime
    import requests
    import translate_ebook_to_zh as te
    ebid = meta["ebook_id"]
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
    now = datetime.datetime.utcnow().isoformat() + "Z"
    row = {"id": ebid, "title": meta["title"], "author": "印順法師", "author_en": "Yin Shun",
           "original_title": meta["title"], "file_type": "epub",
           "file_path": f"印順法師佛學著作集/{meta['parent_volume']}/{meta['title']}",
           "category": "世界宗教", "subcategory": "佛教", "display_mode": "standard",
           "translator": None, "publication_year": meta.get("year"),
           "chunk_count": len(chunks), "total_pages": len(chunks), "total_chars": total,
           "parsed_at": now, "standardized_at": now}
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebid}", headers=te.H_GET, timeout=30)
    rows = [{"ebook_id": ebid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[i:i + 25], timeout=60)
    print(f"    ✓ DB ebooks+previews  chunk_count={len(chunks)}  {ebid}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", type=str, help="本機 XML 檔（--inspect 用）")
    ap.add_argument("--book", type=str, help="卷號 Y08")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--inspect", action="store_true", help="印章節樹 + chunk 計數，不入庫")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    if a.inspect and a.xml:
        xml_text = Path(a.xml).read_text(encoding="utf-8")
        book, chunks = parse_tei_chunks(xml_text, volume="?", parent_volume="?")
        print(f"書名：{book}　chunk 數：{len(chunks)}")
        for c in chunks[:25]:
            print(f"  [{c['chunk_index']:>3}] {c['chapter_path']}  ({len(c['content'])}字)")
        print("\n首 chunk 內文：\n" + chunks[0]["content"][:300])
        return

    reg = load_registry()
    if not reg:
        raise SystemExit("registry 未建：先跑 build_registry（見 yinshun_collected_works.md）")
    vols = sorted(reg) if a.all else [a.book]
    for v in vols:
        build_book(v, reg, upload=a.upload)


if __name__ == "__main__":
    main()
