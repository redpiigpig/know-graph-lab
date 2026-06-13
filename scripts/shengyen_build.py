"""聖嚴法師《法鼓全集 2020 紀念版》→ reader 書（ddc.shengyen.org 靜態 HTML → 單語 JSONL → R2 + DB）。

collected-works 第二個「單一語言」案例（繼印順之後）：全集本即繁體中文 → 零翻譯、零對齊。
與印順差別只在來源解析器（HTML 而非 CBETA TEI），下游入庫/hub 完全共用。

來源（ddc.shengyen.org）架構：
  include/getData.php?type=all_books → var G_ALL_BOOKS = {"輯-冊": 書名}（111 冊）
  include/getData.php?type=vol_dump  → var G_VOLS = {"輯-冊-篇": 篇名}（4079 篇）
  tree_menu/toc.html                 → 巢狀 <ul><li><a html_file=...> 章節樹（書內 章/節 → 篇）
  html/{輯-冊-篇}.html               → 每篇正文（p.indent 正文／p.hN 標題／span.pb data-page 頁碼／span.lb 空行碼）

一書（ebook）＝ 一個 輯-冊；chunk ＝ 篇（html 檔）；parent_volume ＝ 輯名。
chapter_path ＝ 書名 · [toc 書內章節] · 篇名。page_number 取該篇首個 data-page（保留原書頁碼）。

版權：聖嚴法師 2009 圓寂、非公有領域；本站為私人 auth-gate 研究圖書館收錄（同印順姿態，
見 [[feedback_jung_nonpd_english_first]]）。方法論見 .claude/skills/ebook-collected-works/shengyen_collected_works.md。

純函式（parse_content_html / clean / build_chapter_paths）零 network/DB，由
scripts/tests/test_shengyen_build.py 鎖定。upload 重用 translate_ebook_to_zh / standardize_ebook（同 yinshun_build）。

  python scripts/shengyen_build.py --build-registry          # 抓 all_books/vol_dump/toc → registry
  python scripts/shengyen_build.py --inspect --book 03-05    # 印某書章節樹 + chunk 計數
  python scripts/shengyen_build.py --book 03-05 --upload     # 一書 → R2 + DB
  python scripts/shengyen_build.py --all --upload            # 全 111 冊
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

BASE = "https://ddc.shengyen.org"
HTML_URL = BASE + "/html/{doc}.html"
REG_PATH = SCRIPT_DIR.parent / ".claude/skills/ebook-collected-works/shengyen_registry.json"

# 輯 code → parent_volume 輯名（00 總目錄不上架；11 年譜特例）
JI_NAMES = {
    "01": "第一輯 教義論述類", "02": "第二輯 佛教史類", "03": "第三輯 文集類",
    "04": "第四輯 禪修類", "05": "第五輯 佛教入門類", "06": "第六輯 自傳、遊記類",
    "07": "第七輯 經典釋義類", "08": "第八輯 生活佛法類", "09": "第九輯 理念願景類",
    "11": "別卷",
}
EBID_PREFIX = "b0000000-0000-4000-8000-"


def _clean(s: str) -> str:
    """殺折行/縮排，保留英文詞間空格與全形空格（同 yinshun_build._clean）。"""
    s = re.sub(r"[ \t]*\n[ \t\n]*", "", s)
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s


def parse_content_html(html: str, *, book_title: str, toc_path: list[str],
                       page_fallback: str | None = None) -> dict | None:
    """單篇 html → 一個單語 chunk。lb/pb 是空 <span> 標記，get_text 已乾淨；
    p.hN → markdown 標題、其餘（indent/byline…）→ 段落。page_number 取首個 data-page。"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    page = None
    pb = soup.select_one("span.pb[data-page]")
    if pb:
        page = pb.get("data-page")
    page = page or page_fallback

    blocks: list[str] = []
    for p in soup.find_all("p"):
        cls = (p.get("class") or [""])[0]
        txt = _clean(p.get_text())
        if not txt:
            continue
        m = re.match(r"h([1-6])", cls)
        if m:
            blocks.append("#" * (int(m.group(1)) + 1) + " " + txt)
        else:
            blocks.append(txt)
    if not blocks:
        return None
    leaf = toc_path[-1] if toc_path else book_title
    cp = " · ".join([book_title] + toc_path) if toc_path else book_title
    return {
        "chunk_type": "chapter",
        "page_number": int(page) if page and str(page).isdigit() else None,
        "chapter_path": cp,
        "title": leaf,
        "content": "\n\n".join(blocks),
    }


def build_chapter_paths(toc_html: str) -> dict[str, list[str]]:
    """tree_menu/toc.html 巢狀 ul/li → {html_file: [書內章節…, 篇名]}（不含輯/書層）。"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(toc_html, "html.parser")
    paths: dict[str, list[str]] = {}

    def walk(ul, stack):
        for li in ul.find_all("li", recursive=False):
            a = li.find("a", recursive=False)
            txt = a.get_text(strip=True) if a else ""
            sub = li.find("ul", recursive=False)
            hf = a.get("html_file") if a else None
            if hf:
                paths[hf] = stack + [txt]
            if sub:
                walk(sub, stack + [txt] if (txt and not hf) else stack)

    root = soup.find("ul")
    if root:
        walk(root, [])
    return paths


# ── registry ─────────────────────────────────────────────────────────────────
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def _fetch(url: str, *, tries: int = 7) -> str:
    import requests
    last = None
    for k in range(tries):
        try:
            r = requests.get(url, timeout=60, headers={**_UA, "Connection": "close"}, verify=False)
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(8.0, 0.6 * (2 ** k)))  # 指數退避，封頂 8s（伺服器高載會丟連線）
    raise last


def _parse_jsvar(text: str, var: str) -> dict:
    m = re.search(var + r"\s*=\s*(\{.*\})", text, re.S)
    return json.loads(m.group(1))


def build_registry() -> dict:
    all_books = _parse_jsvar(_fetch(BASE + "/include/getData.php?type=all_books"), "G_ALL_BOOKS")
    vols = _parse_jsvar(_fetch(BASE + "/include/getData.php?type=vol_dump&book=00-00"), "G_VOLS")
    toc_paths = build_chapter_paths(_fetch(BASE + "/tree_menu/toc.html"))

    # 篇 → 所屬書（最長前綴匹配 all_books key）
    book_keys = sorted(all_books, key=len, reverse=True)
    docs_by_book: dict[str, list[str]] = {}
    for doc in vols:
        bk = next((b for b in book_keys if doc.startswith(b + "-") or doc == b), None)
        if bk:
            docs_by_book.setdefault(bk, []).append(doc)

    reg: dict[str, dict] = {}
    for i, bk in enumerate(sorted(all_books), start=1):
        if bk.startswith("00"):  # 總目錄不上架
            continue
        ji = bk[:2]
        docs = sorted(docs_by_book.get(bk, []),
                      key=lambda d: [int(x) if x.isdigit() else x for x in d.split("-")])
        reg[bk] = {
            "title": all_books[bk].strip("《》"),
            "parent_volume": JI_NAMES.get(ji, ji),
            "ebook_id": EBID_PREFIX + f"{i:012d}",
            "docs": docs,
            "vols": {d: vols[d].strip() for d in docs},
            "toc": {d + ".html": toc_paths.get(d + ".html", [vols[d].strip()]) for d in docs},
        }
    REG_PATH.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"registry: {len(reg)} 冊 / {sum(len(b['docs']) for b in reg.values())} 篇 → {REG_PATH.name}")
    return reg


def load_registry() -> dict:
    return json.loads(REG_PATH.read_text(encoding="utf-8")) if REG_PATH.exists() else {}


# ── build one book ───────────────────────────────────────────────────────────
def build_book(bk: str, reg: dict, *, upload: bool) -> list[dict]:
    meta = reg[bk]
    title = meta["title"]
    cover = {"chunk_index": 0, "chunk_type": "chapter", "page_number": 0,
             "chapter_path": title, "volume": title, "parent_volume": meta["parent_volume"],
             "format": "markdown", "content": f"# {title}\n\n法鼓全集 · {meta['parent_volume']}"}
    chunks = [cover]
    idx = 0
    for doc in meta["docs"]:
        html = _fetch(HTML_URL.format(doc=doc))
        toc_path = meta["toc"].get(doc + ".html", [meta["vols"].get(doc, doc)])
        ch = parse_content_html(html, book_title=title, toc_path=toc_path)
        if not ch:
            continue
        idx += 1
        ch.update({"chunk_index": idx, "volume": title,
                   "parent_volume": meta["parent_volume"], "format": "markdown"})
        ch.pop("title", None)
        chunks.append(ch)
        time.sleep(0.05)
    print(f"  {bk} {title}: {len(chunks)-1} 篇 chunk | {sum(len(c['content']) for c in chunks)} 字", flush=True)
    if upload:
        _upload(meta, chunks)
    return chunks


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
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {"id": ebid, "title": meta["title"], "author": "聖嚴法師", "author_en": "Sheng Yen",
           "original_title": meta["title"], "file_type": "epub",
           "file_path": f"法鼓全集/{meta['parent_volume']}/{meta['title']}",
           "category": "世界宗教", "subcategory": "佛教", "display_mode": "standard",
           "translator": None, "publication_year": None,
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
    ap.add_argument("--build-registry", action="store_true")
    ap.add_argument("--book", type=str)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--resume", action="store_true", help="跳過 DB 已有 chunk 的冊")
    a = ap.parse_args()

    if a.build_registry:
        build_registry()
        return

    reg = load_registry()
    if not reg:
        raise SystemExit("registry 未建：先跑 --build-registry")

    if a.inspect and a.book:
        chunks = build_book(a.book, reg, upload=False)
        for c in chunks[:25]:
            print(f"  [{c['chunk_index']:>3}] p{c['page_number']} {c['chapter_path']}  ({len(c['content'])}字)")
        return

    vols = sorted(reg) if a.all else [a.book]
    if a.resume:
        done = _books_with_chunks({reg[v]["ebook_id"]: v for v in vols})
        vols = [v for v in vols if v not in done]
        print(f"resume: 跳過 {len(done)} 已完成，剩 {len(vols)} 冊", flush=True)
    failed = []
    for v in vols:
        try:
            build_book(v, reg, upload=a.upload)
        except Exception as e:  # noqa: BLE001  一本失敗不中斷全批
            print(f"  ✗ {v} 失敗：{e}", flush=True)
            failed.append(v)
    for v in failed:  # 失敗者重試一輪
        try:
            print(f"  ↻ 重試 {v}", flush=True)
            build_book(v, reg, upload=a.upload)
            failed.remove(v)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗✗ {v} 仍失敗：{e}", flush=True)
    if failed:
        print(f"最終失敗 {len(failed)} 冊：{failed}", flush=True)


def _books_with_chunks(ebid_to_book: dict[str, str]) -> set[str]:
    """查 DB：哪些冊的 ebook 已有 chunk_count>0（resume 用）。"""
    import requests
    import translate_ebook_to_zh as te
    done: set[str] = set()
    ids = list(ebid_to_book)
    for i in range(0, len(ids), 50):
        r = requests.get(f"{te.URL}/rest/v1/ebooks", headers=te.H_GET,
                         params={"id": "in.(" + ",".join(ids[i:i + 50]) + ")",
                                 "select": "id,chunk_count"}, timeout=30)
        for row in r.json():
            if row.get("chunk_count"):
                done.add(ebid_to_book[row["id"]])
    return done


if __name__ == "__main__":
    main()
