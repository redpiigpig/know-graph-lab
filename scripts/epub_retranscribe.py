#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ebooklib 解析不動的 EPUB，改走 zipfile 重轉。

觸發這支的案例：《榮格自傳：回憶‧夢‧省思》的 manifest 列了一張
`OEBPS/Images/copyright.jpg`，但那張圖不在壓縮檔裡——`ebooklib.epub.read_epub()`
在讀 manifest 時直接 KeyError，整本書 0 chunk，`parse_error` 就這麼掛了幾個月。
內文其實完好無損：spine 十七個 xhtml、EPUB3 nav 目錄齊全。

所以這支只做一件事：**不碰 manifest 裡的非內文項目**，用 zipfile 讀 spine 列到的
xhtml，一個檔一個 chunk，章名取自目錄（ncx 或 EPUB3 nav），簡→繁走
standardize_ebook.to_traditional，零 LLM。

  python scripts/epub_retranscribe.py --ebook-id <uuid> --inspect
  python scripts/epub_retranscribe.py --ebook-id <uuid> --upload
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from kawai_build import extract_part_text, split_paras  # noqa: E402
from weber_build import ncx_entries, spine_hrefs  # noqa: E402

ROOT = SCRIPT_DIR.parent

# 頁眉／版權頁殘留：整段就這幾個字的，不是內文。
_NOISE = re.compile(r"^(未知|佚名|版權所有|All rights reserved|封面|目錄)$")


# ── 純解析（零 network/DB）────────────────────────────────────────────────

def nav_entries(nav_html: str) -> list[tuple[str, str]]:
    """EPUB3 nav.xhtml → [(檔名, 標題)]。沒有 ncx 的新版 EPUB 走這條。"""
    out = []
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', nav_html, re.S):
        name = m.group(1).split("/")[-1].split("#")[0]
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if name and title:
            out.append((name, title))
    return out


def clean_paras(paras: list[str]) -> list[str]:
    return [p for p in paras if not _NOISE.match(p.strip())]


def build_chunks(epub_path: Path, *, to_trad, title: str) -> list[dict]:
    z = zipfile.ZipFile(epub_path)
    opf = next(n for n in z.namelist() if n.endswith(".opf"))
    base = opf.rsplit("/", 1)[0] if "/" in opf else ""
    hrefs = spine_hrefs(z.read(opf).decode("utf-8"))

    labels: dict[str, str] = {}
    ncx = next((n for n in z.namelist() if n.endswith(".ncx")), None)
    if ncx:
        for name, _anchor, lab in ncx_entries(z.read(ncx).decode("utf-8")):
            labels.setdefault(name, lab)
    else:
        nav = next((n for n in z.namelist() if n.endswith("nav.xhtml")), None)
        if nav:
            for name, lab in nav_entries(z.read(nav).decode("utf-8")):
                labels.setdefault(name, lab)

    chunks = [{"chunk_index": 0, "chunk_type": "cover", "page_number": 0,
               "chapter_path": title, "volume": title, "format": "markdown",
               "content": f"# {title}"}]
    idx = 0
    for href in hrefs:
        name = href.split("/")[-1]
        if re.search(r"(toc|contents)\.x?html$", name, re.I) or \
                labels.get(name) in ("目錄", "Contents"):
            continue                        # 目錄頁不是內文（reader 自己有目錄）
        try:
            html = z.read(f"{base}/{href}" if base else href).decode("utf-8")
        except KeyError:
            continue                        # manifest 有、壓縮檔沒有 → 跳過，不是致命傷
        body = to_trad(split_paras(clean_paras(extract_part_text(html))))
        if len(body.strip()) < 60:          # 書名頁、目錄頁
            continue
        idx += 1
        label = labels.get(name) or f"第 {idx} 節"
        chunks.append({
            "chunk_index": idx, "chunk_type": "chapter", "page_number": idx,
            "chapter_path": to_trad(f"{title} · {label}"), "volume": title,
            "format": "markdown", "content": body,
        })
    z.close()
    return chunks


# ── DB ────────────────────────────────────────────────────────────────────

def _env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"')
    return env


def fetch_row(ebook_id: str) -> dict:
    env = _env()
    req = urllib.request.Request(
        f"{env['SUPABASE_URL']}/rest/v1/ebooks?id=eq.{ebook_id}"
        "&select=id,title,author,file_path,collection",
        headers={"apikey": env["SUPABASE_SERVICE_ROLE_KEY"],
                 "Authorization": f"Bearer {env['SUPABASE_SERVICE_ROLE_KEY']}"})
    rows = json.loads(urllib.request.urlopen(req, timeout=60).read())
    if not rows:
        raise SystemExit(f"查無此書：{ebook_id}")
    return rows[0]


def upload(row: dict, chunks: list[dict], collection: str | None = None) -> None:
    import datetime
    import requests
    import translate_ebook_to_zh as te

    eid = row["id"]
    out = te.CHUNKS_DIR / f"{eid}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    try:
        te.se.push_to_r2(eid, out)
        print("  ✓ R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 失敗: {e}", flush=True)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    patch = {"chunk_count": len(chunks), "total_pages": len(chunks),
             "total_chars": sum(len(c["content"]) for c in chunks),
             "parsed_at": now, "standardized_at": now,
             "parse_error": None}          # 修好了就把舊的錯誤訊息清掉
    if collection:                        # 沒帶這欄，全集書會落回電子圖書館
        patch["collection"] = collection
    r = requests.patch(f"{te.URL}/rest/v1/ebooks?id=eq.{eid}", headers=te.H_JSON,
                       json=patch, timeout=30)
    if r.status_code >= 300:
        raise SystemExit(f"  ✗ ebooks {r.status_code} {r.text[:300]}")
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}",
                    headers=te.H_GET, timeout=60)
    prev = [{"ebook_id": eid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for i in range(0, len(prev), 25):
        rr = requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON,
                           json=prev[i:i + 25], timeout=60)
        if rr.status_code >= 300:
            raise SystemExit(f"  ✗ chunks {rr.status_code} {rr.text[:300]}")
    print(f"  ✓ DB chunk_count={len(chunks)}  {eid}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ebook-id", required=True)
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--collection", help="一併標 collection（全集書用 collected-works）")
    a = ap.parse_args()

    from standardize_ebook import to_traditional

    row = fetch_row(a.ebook_id)
    path = Path(row["file_path"])
    if not path.exists():
        raise SystemExit(f"原檔不在：{path}")
    chunks = build_chunks(path, to_trad=to_traditional, title=row["title"])
    chars = sum(len(c["content"]) for c in chunks)
    print(f"[{row['title']}] {row['author']}  chunks={len(chunks)}  {chars:,} 字")
    if a.inspect:
        for c in chunks[1:6]:
            print(f"   · {c['chapter_path'][:40]:42} {c['content'][:48]}…")
    if a.upload:
        upload(row, chunks, a.collection)


if __name__ == "__main__":
    main()
