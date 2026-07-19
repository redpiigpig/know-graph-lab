#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""近代經典 English-first Haiku 翻譯佇列（collected-works 下一批）。

來源＝c:/tmp/cw_sources/<slug>.txt（Project Gutenberg PD 純文字，見 _manifest.json）。
每部：去 Gutenberg 頭尾 → split_sections → 合小/切大成翻譯單位 → 逐節 Haiku EN→繁中
（per-節 resumable cache）→ 多語 chunk（content=繁中, sources={en}）→ R2+DB。

重用：translate_collected_work.split_sections / _upload、translate_ebook_to_zh.haiku_translate、
multilang_chunks.build_multilang_chunk。仿 plato_build.ensure_ebook_row 建列。

用法：
  python scripts/modern_classics_auto.py                # 跑整個佇列（resumable）
  python scripts/modern_classics_auto.py --only marx    # 單一部
  python scripts/modern_classics_auto.py --only marx --limit 2   # smoke test
"""
from __future__ import annotations
import argparse, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_ebook_to_zh as te
import translate_collected_work as tcw
import multilang_chunks as mc
import requests

SRC = Path("c:/tmp/cw_sources")
CACHE = Path("c:/tmp/modern_cache")
_NS = "80000000-0000-4000-8000-0000000000"  # + 2位序號

MODERN_PROMPT = """你是經典學術與哲學著作的專業譯者。把下列**英文**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；忠實、流暢的學術語氣，不加註、不改寫、不省略。
2. **保留原文的分段**：原文段落之間空一行，譯文也照樣分段空行，段數對齊。
3. 人名地名採學界通行譯名；引文照譯。
4. 只輸出繁體中文譯文，不要前言、說明或標題編號。

{source}"""

# (slug, ebook_n, title_zh, title_orig, author_zh, author_en, author_slug, genre, category, files)
_TABLE = [
    ("marx",          "01", "共產黨宣言", "Manifest der Kommunistischen Partei", "馬克思", "Karl Marx", "karl-marx", "treatise", "哲學", ["karl-marx.txt"]),
    ("mill",          "02", "論自由", "On Liberty", "彌爾", "John Stuart Mill", "john-stuart-mill", "essay", "哲學", ["john-stuart-mill.txt"]),
    ("descartes",     "03", "第一哲學沉思集", "Meditationes de prima philosophia", "笛卡兒", "René Descartes", "descartes", "treatise", "哲學", ["descartes.txt"]),
    ("hume",          "04", "人類理解研究", "An Enquiry Concerning Human Understanding", "休謨", "David Hume", "hume", "treatise", "哲學", ["hume.txt"]),
    ("spinoza",       "05", "倫理學", "Ethica", "斯賓諾莎", "Baruch Spinoza", "spinoza", "treatise", "哲學", ["spinoza.txt"]),
    ("nietzsche",     "06", "查拉圖斯特拉如是說", "Also sprach Zarathustra", "尼采", "Friedrich Nietzsche", "nietzsche", "narrative", "哲學", ["nietzsche.txt"]),
    ("william-james", "07", "宗教經驗之種種", "The Varieties of Religious Experience", "威廉‧詹姆斯", "William James", "william-james", "lecture", "心理學", ["william-james.txt"]),
    ("durkheim",      "08", "宗教生活的基本形式", "Les formes élémentaires de la vie religieuse", "涂爾幹", "Émile Durkheim", "emile-durkheim", "treatise", "宗教社會學", ["emile-durkheim.txt"]),
    ("frazer",        "09", "金枝", "The Golden Bough", "弗雷澤", "James George Frazer", "james-frazer", "treatise", "宗教學", ["james-frazer.txt"]),
    ("freud",         "10", "夢的解析", "Die Traumdeutung", "佛洛伊德", "Sigmund Freud", "sigmund-freud", "treatise", "心理學", ["sigmund-freud.txt"]),
    ("kant",          "11", "純粹理性批判", "Kritik der reinen Vernunft", "康德", "Immanuel Kant", "kant", "treatise", "哲學", ["kant.txt"]),
    ("tylor",         "12", "原始文化", "Primitive Culture", "泰勒", "Edward Burnett Tylor", "edward-tylor", "treatise", "宗教學", ["edward-tylor-vol1.txt", "edward-tylor-vol2.txt"]),
]
WORKS = {r[0]: {"slug": r[0], "ebook_id": _NS + r[1], "title_zh": r[2], "title_orig": r[3],
                "author_zh": r[4], "author_en": r[5], "author_slug": r[6], "genre": r[7],
                "category": r[8], "files": r[9]} for r in _TABLE}

_GUT_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)
_GUT_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)


def _strip_gutenberg(text: str) -> str:
    m = _GUT_START.search(text)
    if m:
        text = text[m.end():]
    m = _GUT_END.search(text)
    if m:
        text = text[:m.start()]
    # 去 "Produced by ..." 首段殘留
    return text.strip()


def _pack_sections(secs: list[dict], min_chars=700, max_chars=4500) -> list[dict]:
    """合併過小節、切分過大節，成適合逐節翻譯的單位。保留 heading 當 chapter_path。"""
    out: list[dict] = []
    buf_head, buf_body = None, []

    def flush():
        nonlocal buf_head, buf_body
        body = "\n\n".join(p for p in buf_body if p.strip()).strip()
        if body:
            out.append({"heading": buf_head or "", "text": body})
        buf_head, buf_body = None, []

    for s in secs:
        head, body = s["heading"], s["text"].strip()
        if not body and head in ("(front)", ""):
            continue
        # 過大 → 依段落切成 <= max_chars 的塊
        if len(body) > max_chars:
            flush()
            paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
            cur, cur_len = [], 0
            for p in paras:
                if cur_len + len(p) > max_chars and cur:
                    out.append({"heading": head, "text": "\n\n".join(cur)})
                    cur, cur_len = [], 0
                cur.append(p); cur_len += len(p) + 2
            if cur:
                out.append({"heading": head, "text": "\n\n".join(cur)})
            continue
        # 起新節 or 累積
        if buf_head is None:
            buf_head = head if head != "(front)" else ""
        buf_body.append(body)
        if sum(len(x) for x in buf_body) >= min_chars:
            flush()
    flush()
    return out


def ensure_row(d: dict) -> None:
    r = requests.get(f"{te.URL}/rest/v1/ebooks?id=eq.{d['ebook_id']}&select=id", headers=te.H_GET, timeout=30)
    if r.ok and r.json():
        return
    row = {"id": d["ebook_id"], "title": f"{d['title_zh']}（英繁對照）",
           "author": d["author_zh"], "author_en": d["author_en"], "file_type": "epub",
           "original_title": d["title_orig"], "translator": "AI 輔助（英文直譯）",
           "display_mode": "standard", "collection": "collected-works"}
    requests.post(f"{te.URL}/rest/v1/ebooks", headers=te.H_JSON, json=row, timeout=30).raise_for_status()
    print(f"  ✓ inserted ebooks row {d['ebook_id']}")


def _translate_cached(slug: str, i: int, en: str) -> str:
    cdir = CACHE / slug
    cdir.mkdir(parents=True, exist_ok=True)
    fp = cdir / f"{i:04d}.txt"
    if fp.exists():
        return fp.read_text(encoding="utf-8")
    zh = te.haiku_translate(en)
    fp.write_text(zh, encoding="utf-8")
    return zh


def build(slug: str, *, limit=None, upload=True, upload_every=20) -> int:
    d = WORKS[slug]
    te.PROMPT_TMPL = MODERN_PROMPT
    # 讀源（可能多卷）→ 去殼 → 分節 → 打包
    packed: list[dict] = []
    for vi, fn in enumerate(d["files"], 1):
        raw = _strip_gutenberg((SRC / fn).read_text(encoding="utf-8", errors="ignore"))
        secs = tcw.split_sections(raw)
        vol = f"卷{['一','二','三','四','五'][vi-1]}" if len(d["files"]) > 1 else None
        for s in _pack_sections(secs):
            s["_vol"] = vol
            packed.append(s)
    if limit:
        packed = packed[:limit]
    print(f"[{slug}] {d['author_zh']}《{d['title_zh']}》 {len(packed)} 節 → 翻譯中…", flush=True)
    ensure_row(d)

    out = Path(f"c:/tmp/modern_{slug}.jsonl")
    chunks: list[dict] = []
    # cover
    cover = mc.build_multilang_chunk(chunk_index=0, chapter_path="封面", content_zh="## 封面",
                                     sources={}, source_order=[], volume=d["title_zh"],
                                     parent_volume=d["title_zh"], chunk_type="cover", page_number=1)
    mc.validate_multilang_chunk(cover)
    chunks.append(cover)

    for i, s in enumerate(packed):
        en = s["text"]
        zh = _translate_cached(slug, i, en)
        head = s["heading"].strip()
        cp = f"{d['title_zh']}" + (f" · {s['_vol']}" if s.get("_vol") else "") + (f" · {head}" if head else f" · 第 {i+1} 節")
        c = mc.build_multilang_chunk(
            chunk_index=len(chunks), chapter_path=cp, content_zh=zh,
            sources={"en": en}, source_order=["en"],
            volume=(d["title_zh"] + (f"‧{s['_vol']}" if s.get("_vol") else "")),
            parent_volume=d["title_zh"], chunk_type="chapter", page_number=i + 2)
        mc.validate_multilang_chunk(c)
        chunks.append(c)
        if upload and upload_every and (i + 1) % upload_every == 0:
            mc.write_jsonl(chunks, out)
            tcw._upload(d["ebook_id"], chunks, out)
            print(f"  … {i+1}/{len(packed)} 節，已上傳 {len(chunks)} chunks", flush=True)

    mc.write_jsonl(chunks, out)
    print(f"  ✓ {out.name}  {len(chunks)} chunks / {sum(len(c['content']) for c in chunks)} 繁中字")
    if upload:
        tcw._upload(d["ebook_id"], chunks, out)
    return len(chunks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="單一部 slug")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-upload", action="store_true")
    args = ap.parse_args()
    order = [args.only] if args.only else list(WORKS)
    for slug in order:
        if slug not in WORKS:
            print(f"[skip] 未知 slug {slug}"); continue
        for attempt in range(1, 4):
            try:
                build(slug, limit=args.limit, upload=not args.no_upload)
                print(f"[ok  ] {slug}")
                break
            except Exception as e:
                print(f"[err ] {slug} 第 {attempt} 次：{type(e).__name__} {e}", flush=True)
    print("=== 佇列結束 ===")


if __name__ == "__main__":
    main()
