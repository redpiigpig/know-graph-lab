"""星雲大師全集 → reader 書（books.masterhsingyun.org /ArticleDetail/artcle{N} → 單語 JSONL → R2 + DB）。

collected-works 第三套漢傳佛教全集（單語）。官網的 /bcN/bookM 是空殼、不暴露目錄，但
**每篇文章在 `/ArticleDetail/artcle{N}` 有 server-render 全文**（免登入），且自帶麵包屑：
  回首頁 › 第N類【類名】 › 冊(ebook) › [子冊…] › p篇  ← 完整 大類/冊/篇 階層
正文在 `div.txtContent`，`<p>` 內以 `<br><br>` 分段、`<b>` 為小標。

資料模型（靠麵包屑反推，無需另一份目錄）：
  parent_volume = 大類（第N類【類名】）  ·  ebook = 冊（麵包屑第 2 項，~366 部）
  chapter_path  = 冊 · [子冊…] · p篇      ·  chunk = 一篇文章（artcle{N}）
ID 範圍約 100–24000（~87% 有效、其餘 302）。

版權：星雲大師 2023 圓寂、非公有領域；本站 auth-gate 私人研究圖書館收錄（同印順/聖嚴）。
⚠️ ~2 萬篇 → crawl 必須**禮貌節流 + 指數退避 + resumable 快取**，避免被封（user 叮囑）。
方法論見 .claude/skills/ebook-collected-works/hsingyun_collected_works.md。

純函式（parse_article / classify_breadcrumb / clean_book_title …）零 network/DB，由
scripts/tests/test_hsingyun_build.py 鎖定。upload 重用 translate_ebook_to_zh / standardize_ebook。

  python scripts/hsingyun_build.py --crawl --start 1 --end 25500   # 禮貌抓全文到快取（resumable）
  python scripts/hsingyun_build.py --inspect                       # 從快取印 大類/冊/篇 統計
  python scripts/hsingyun_build.py --build --upload                # 快取 → ~366 冊 → R2 + DB
"""
from __future__ import annotations

import argparse
import html as _html
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

BASE = "https://books.masterhsingyun.org"
ART_URL = BASE + "/ArticleDetail/artcle{n}"
CACHE_DIR = Path(os.environ.get("HSINGYUN_CACHE") or r"c:/tmp/hsingyun_cache")
REG_PATH = SCRIPT_DIR.parent / ".claude/skills/ebook-collected-works/hsingyun_registry.json"
EBID_PREFIX = "c0000000-0000-4000-8000-"
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
_CLASS_RE = re.compile(r"第[一二三四五六七八九十]+類")


# ── 純解析 ───────────────────────────────────────────────────────────────────
def _strip_tags(s: str) -> str:
    return _html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def parse_article(html_text: str) -> dict | None:
    """artcle{N} HTML → {breadcrumb:[...(不含回首頁)], paras:[...], heading:str|None}。
    若無 breadcrumb（302/重導）或為索引頁（大師全集）→ None。"""
    m = re.search(r'<ul class="breadcrumb">(.*?)</ul>', html_text, re.S)
    if not m:
        return None
    items = [_strip_tags(x).rstrip("/").strip()
             for x in re.findall(r"<li[^>]*>(.*?)</li>", m.group(1), re.S)]
    items = [i for i in items if i and i != "回首頁"]
    if not items or not any(_CLASS_RE.match(i) for i in items[:1]):
        return None  # 索引頁 / 非文章

    body = re.search(r'class="txtContent[^"]*">(.*?)</div>', html_text, re.S)
    paras: list[str] = []
    heading = None
    if body:
        # <b>…</b> 內的小標單獨抓；整段以 <br> 切
        inner = body.group(1)
        bm = re.search(r"<b>(.*?)</b>", inner, re.S)
        if bm:
            heading = re.sub(r"\s+", " ", _strip_tags(bm.group(1))).strip()
        for chunk in re.split(r"(?:<br\s*/?>\s*){1,}", inner):
            txt = _strip_tags(chunk)
            txt = re.sub(r"[ \t]*\n[ \t\n]*", "", txt)
            if txt:
                paras.append(txt)
    if not paras:
        return None
    return {"breadcrumb": items, "paras": paras, "heading": heading}


def classify_breadcrumb(items: list[str]) -> dict:
    """麵包屑（不含回首頁）→ {parent_volume(大類), book_key(冊), chapter_parts[], title}。"""
    parent = items[0]
    book = items[1] if len(items) > 1 else items[0]
    chapter_parts = items[1:] if len(items) > 1 else [items[0]]
    title = items[-1]
    return {"parent_volume": parent, "book_key": book,
            "chapter_parts": chapter_parts, "title": title}


def clean_book_title(book_key: str) -> str:
    """'004-005金剛經講話(共2冊)' → '金剛經講話'；'025佛法滿人間' → '佛法滿人間'。"""
    s = re.sub(r"^[\d\-]+", "", book_key)            # 去前導冊號
    s = re.sub(r"[（(]共[^）)]*[冊册][）)]\s*$", "", s)  # 去 (共N冊)
    return s.strip() or book_key


def book_sort_key(book_key: str):
    m = re.match(r"(\d+)", book_key)
    return (int(m.group(1)) if m else 9999, book_key)


# ── crawl（禮貌 + resumable）─────────────────────────────────────────────────
def _cache_file(n: int) -> Path:
    return CACHE_DIR / f"{n}.json"


def fetch_one(session, n: int, *, tries: int = 5):
    """抓一篇 → 寫快取 {n, parsed} 或 {n, empty:true}。回傳 'ok'/'empty'/'err'。"""
    f = _cache_file(n)
    if f.exists():
        return "cached"
    last = None
    for k in range(tries):
        try:
            r = session.get(ART_URL.format(n=n), timeout=30, headers=_UA,
                            verify=False, allow_redirects=False)
            if r.status_code in (301, 302, 303, 404):
                f.write_text(json.dumps({"n": n, "empty": True}), encoding="utf-8")
                return "empty"
            r.raise_for_status()
            r.encoding = "utf-8"
            parsed = parse_article(r.text)
            if parsed is None:
                f.write_text(json.dumps({"n": n, "empty": True}), encoding="utf-8")
                return "empty"
            f.write_text(json.dumps({"n": n, "parsed": parsed}, ensure_ascii=False), encoding="utf-8")
            return "ok"
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(20.0, 0.8 * (2 ** k)))  # 指數退避，封頂 20s
    print(f"    ✗ artcle{n}: {last}", flush=True)
    return "err"


def crawl(start: int, end: int, *, workers: int = 5):
    import requests
    from concurrent.futures import ThreadPoolExecutor
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    todo = [n for n in range(start, end + 1) if not _cache_file(n).exists()]
    print(f"crawl {start}-{end}: {len(todo)} 待抓（已快取 {end - start + 1 - len(todo)}）", flush=True)
    stats = {"ok": 0, "empty": 0, "err": 0, "cached": 0}
    done = 0

    def work(n):
        time.sleep(0.05)  # 每請求小延遲，禮貌節流
        return fetch_one(session, n)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(work, todo):
            stats[res] = stats.get(res, 0) + 1
            done += 1
            if done % 500 == 0:
                print(f"  {done}/{len(todo)}  ok={stats['ok']} empty={stats['empty']} err={stats['err']}", flush=True)
    print(f"crawl done: {stats}", flush=True)


# ── build（快取 → 冊 → R2/DB）────────────────────────────────────────────────
def load_cache() -> list[dict]:
    arts = []
    for f in CACHE_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if d.get("parsed"):
            arts.append({"n": d["n"], **d["parsed"]})
    arts.sort(key=lambda a: a["n"])
    return arts


def group_books(arts: list[dict]) -> dict:
    """文章 list → {book_key: {parent_volume, title, arts:[...]}}（保 ID 序）。"""
    books: dict[str, dict] = {}
    for a in arts:
        c = classify_breadcrumb(a["breadcrumb"])
        b = books.setdefault(c["book_key"], {
            "book_key": c["book_key"], "parent_volume": c["parent_volume"],
            "title": clean_book_title(c["book_key"]), "arts": []})
        b["arts"].append({**a, "_class": c})
    return books


def build_registry() -> dict:
    books = group_books(load_cache())
    reg = {}
    for i, bk in enumerate(sorted(books, key=book_sort_key)):
        b = books[bk]
        reg[bk] = {"title": b["title"], "parent_volume": b["parent_volume"],
                   "ebook_id": EBID_PREFIX + f"{i + 1:012d}", "n_articles": len(b["arts"])}
    REG_PATH.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"registry: {len(reg)} 冊 / {sum(b['n_articles'] for b in reg.values())} 篇", flush=True)
    return reg


def _article_chunk(a: dict, idx: int, book_title: str, parent_volume: str) -> dict:
    c = a["_class"]
    chapter_path = " · ".join([book_title] + c["chapter_parts"][1:]) if len(c["chapter_parts"]) > 1 else f"{book_title} · {c['title']}"
    page = None
    pm = re.search(r"p0*(\d+)", c["title"])
    if pm:
        page = int(pm.group(1))
    return {"chunk_index": idx, "chunk_type": "chapter", "page_number": page,
            "chapter_path": chapter_path, "volume": book_title,
            "parent_volume": parent_volume, "format": "markdown",
            "content": "\n\n".join(a["paras"])}


def build_book(bk: str, books: dict, reg: dict, *, upload: bool) -> list[dict]:
    b = books[bk]
    meta = reg[bk]
    title = meta["title"]
    cover = {"chunk_index": 0, "chunk_type": "chapter", "page_number": 0,
             "chapter_path": title, "volume": title, "parent_volume": meta["parent_volume"],
             "format": "markdown", "content": f"# {title}\n\n星雲大師全集 · {meta['parent_volume']}"}
    chunks = [cover]
    for i, a in enumerate(b["arts"], start=1):
        chunks.append(_article_chunk(a, i, title, meta["parent_volume"]))
    print(f"  {bk[:24]} {title}: {len(chunks)-1} 篇 | {sum(len(c['content']) for c in chunks)} 字", flush=True)
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
    except Exception as e:  # noqa: BLE001
        print(f"    ⚠ R2 失敗: {e}", flush=True)
    total = sum(len(c["content"]) for c in chunks)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {"id": ebid, "title": meta["title"], "author": "星雲大師", "author_en": "Hsing Yun",
           "original_title": meta["title"], "file_type": "epub",
           "file_path": f"星雲大師全集/{meta['parent_volume']}/{meta['title']}",
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
    print(f"    ✓ {ebid} chunk_count={len(chunks)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crawl", action="store_true")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=25500)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--resume", action="store_true", help="跳過 DB 已有 chunk 的冊")
    ap.add_argument("--book", type=str, default=None)
    a = ap.parse_args()

    if a.crawl:
        crawl(a.start, a.end, workers=a.workers)
        return

    if a.inspect:
        books = group_books(load_cache())
        from collections import Counter
        cls = Counter(b["parent_volume"] for b in books.values())
        print(f"冊數 {len(books)}　篇數 {sum(len(b['arts']) for b in books.values())}")
        for k, v in sorted(cls.items()):
            print(f"  {k}: {v} 冊")
        for bk in sorted(books, key=book_sort_key)[:8]:
            print(f"  · {clean_book_title(bk)}  ({len(books[bk]['arts'])} 篇)")
        return

    if a.build:
        books = group_books(load_cache())
        reg = build_registry()
        targets = [a.book] if a.book else sorted(books, key=book_sort_key)
        if a.resume:
            done = _books_with_chunks({reg[bk]["ebook_id"]: bk for bk in targets if bk in reg})
            targets = [bk for bk in targets if bk not in done]
            print(f"resume: 跳過 {len(done)} 已完成，剩 {len(targets)} 冊", flush=True)
        failed = []
        for bk in targets:
            try:
                build_book(bk, books, reg, upload=a.upload)
            except Exception as e:  # noqa: BLE001  一冊失敗不中斷全批
                print(f"  ✗ {bk[:24]} 失敗：{e}", flush=True)
                failed.append(bk)
        for bk in list(failed):  # 失敗者重試一輪
            try:
                print(f"  ↻ 重試 {bk[:24]}", flush=True)
                build_book(bk, books, reg, upload=a.upload)
                failed.remove(bk)
            except Exception as e:  # noqa: BLE001
                print(f"  ✗✗ {bk[:24]} 仍失敗：{e}", flush=True)
        if failed:
            print(f"最終失敗 {len(failed)} 冊：{[b[:16] for b in failed]}", flush=True)
        return
    ap.print_help()


def _books_with_chunks(ebid_to_book: dict) -> set:
    """查 DB：哪些冊已有 chunk_count>0（resume 用）。"""
    import requests
    import translate_ebook_to_zh as te
    done = set()
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
