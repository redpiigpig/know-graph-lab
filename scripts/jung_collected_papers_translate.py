"""Resumable English→繁中 translator for Jung's *Collected Papers on Analytical
Psychology* (ed. Constance E. Long, 2nd ed. 1917/1920; Project Gutenberg #48225).

English-only public-domain source → bilingual (en + 繁中) ebook in the Jung
collected-works hub. Engine = the unified Gemini→NVIDIA→Haiku chain from
translate_ebook_to_zh. Checkpoint-heavy: each chunk → its own JSON, reruns skip
done chunks, every N chunks it assembles a partial JSONL and upserts previews.

Religion-relevant chapters (a religious-studies reader's priority): I (occult
phenomena), XI (psychological types), XIV (psychology of unconscious processes).
Use --chapters to translate a subset first, or omit for all 15.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "scripts")
from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl

EBID = "22222224-2222-4222-8222-222222222224"
TITLE = "分析心理學論文集（英譯早期版·英繁中對照）"
SRC_TITLE = "Collected Papers on Analytical Psychology (2nd ed., 1917)"
SRC_HTML = Path(r"C:/tmp/jung_collected_papers_en.html")
DATA = Path(".claude/skills/ebook-collected-works/jung_data/collected-papers-1917")
PARTS = DATA / "parts"
STATUS = DATA / "status.json"

#繁中章名（依 Constance Long 2nd ed. 目次）
CHAP_ZH = {
    1: "論所謂神祕現象的心理學與病理學", 2: "聯想實驗法",
    3: "父親對個人命運的意義", 4: "謠言心理學的一則貢獻",
    5: "論數字夢的意義", 6: "布洛伊勒精神分裂性否定論之批判",
    7: "精神分析", 8: "論精神分析", 9: "精神分析的若干關鍵問題",
    10: "論無意識在精神病理學中的重要性", 11: "心理類型研究的一則貢獻",
    12: "夢的心理學", 13: "精神病的內容", 14: "無意識歷程的心理學",
    15: "無意識的概念",
}
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
         "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15}


def load_env() -> None:
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def parse_chapters() -> dict[int, dict]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(SRC_HTML.read_text(encoding="utf-8", errors="replace"), "html.parser")
    for t in soup.select("span.pagenum, .lineright"):
        t.decompose()
    # The 15 essays each appear TWICE: once as <p class="p2">CHAPTER N</p> in the
    # annotated front-matter TOC (with a short synopsis), then as <h2>CHAPTER N</h2>
    # at the real body. Start a chapter ONLY on the body <h2> marker; the TOC p2
    # markers precede all h2 so they fall through with cur=None.
    chapters: dict[int, dict] = {}
    cur: int | None = None
    want_title = False
    for el in soup.find_all(["p", "blockquote", "h2", "h3", "h4"]):
        txt = re.sub(r"\s+", " ", el.get_text(" ")).strip()
        if not txt:
            continue
        m = re.fullmatch(r"CHAPTER\s+([IVXL]+)", txt)
        if m and el.name == "h2":
            cur = ROMAN.get(m.group(1))
            if cur:
                chapters[cur] = {"num": cur, "title_en": "", "paras": []}
                want_title = True
            continue
        if cur is None or (m and el.name == "p"):  # skip TOC p2 markers
            continue
        if want_title:
            chapters[cur]["title_en"] = re.sub(r"\s*\[\d+\]\s*$", "", txt).title()
            want_title = False
            continue
        if re.fullmatch(r"[\d ]+", txt):  # stray page numbers
            continue
        chapters[cur]["paras"].append(txt)
    return chapters


def chunk_paras(paras: list[str], max_chars: int) -> list[str]:
    chunks, cur, n = [], [], 0
    for p in paras:
        if cur and n + len(p) + 2 > max_chars:
            chunks.append("\n\n".join(cur))
            cur, n = [], 0
        cur.append(p)
        n += len(p) + 2
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


def save_status(**kw) -> None:
    STATUS.write_text(json.dumps({"ebook_id": EBID, "title": TITLE,
                                  "updated_at": dt.datetime.now().isoformat(timespec="seconds"), **kw},
                                 ensure_ascii=False, indent=2), encoding="utf-8")


def assemble(units: list[dict], *, upload: bool) -> None:
    import translate_ebook_to_zh as te

    out = [{"chunk_index": 0, "chunk_type": "chapter", "page_number": None,
            "chapter_path": "封面", "format": "markdown", "content": f"## {TITLE}"}]
    ci = 1
    for u in units:
        part = PARTS / f"{u['key']}.json"
        if not part.exists():
            continue
        obj = json.loads(part.read_text(encoding="utf-8"))
        c = build_multilang_chunk(
            chunk_index=ci, chapter_path=u["chapter_path"], volume=u["volume"],
            parent_volume="榮格早期著作", title_en=u["title_en"],
            content_zh=obj["zh"], sources={"en": obj["en"]}, source_order=["en"])
        validate_multilang_chunk(c)
        out.append(c)
        ci += 1
    base = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:/我的雲端硬碟/資料/電子書/_chunks")
    base.mkdir(parents=True, exist_ok=True)
    write_jsonl(out, base / f"{EBID}.jsonl")
    print(f"assembled {len(out)} chunks", flush=True)
    if not upload:
        return
    import requests
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    hj = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates"}
    hg = {"apikey": key, "Authorization": f"Bearer {key}"}
    now = dt.datetime.utcnow().isoformat() + "Z"
    row = {"id": EBID, "title": TITLE, "author": "C. G. 榮格", "author_en": "C. G. Jung",
           "original_title": SRC_TITLE, "file_type": "epub",
           "file_path": "Project Gutenberg/48225", "category": "世界宗教",
           "subcategory": "深層心理學", "display_mode": "standard",
           "translator": "Codex（Gemini→NVIDIA→Haiku 英譯本重譯繁中）", "publication_year": 1917,
           "chunk_count": len(out), "total_pages": len(out),
           "total_chars": sum(len(c["content"]) for c in out),
           "parsed_at": now, "standardized_at": now}
    try:
        requests.post(f"{url}/rest/v1/ebooks", headers=hj, json=row, timeout=30).raise_for_status()
        requests.delete(f"{url}/rest/v1/ebook_chunks?ebook_id=eq.{EBID}", headers=hg, timeout=60).raise_for_status()
        prev = [{"ebook_id": EBID, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
                 "page_number": c.get("page_number"), "chapter_path": c["chapter_path"],
                 "content": c["content"][:200], "char_count": len(c["content"])} for c in out]
        for i in range(0, len(prev), 20):
            requests.post(f"{url}/rest/v1/ebook_chunks", headers=hj, json=prev[i:i + 20], timeout=60).raise_for_status()
        print(f"upserted previews={len(prev)}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN upload: {exc}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", help="e.g. 1,11,14 (default: all)")
    ap.add_argument("--max-chars", type=int, default=4200)
    ap.add_argument("--limit", type=int, help="translate only first N chunks (smoke)")
    ap.add_argument("--upload-every", type=int, default=8)
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--engine", default="nvidia", choices=["auto", "nvidia", "haiku"],
                    help="nvidia-first avoids the dead-Gemini 429 retry storm (default)")
    args = ap.parse_args()
    load_env()
    DATA.mkdir(parents=True, exist_ok=True)
    PARTS.mkdir(parents=True, exist_ok=True)

    chapters = parse_chapters()
    want = [int(x) for x in args.chapters.split(",")] if args.chapters else sorted(chapters)
    units: list[dict] = []
    for cn in want:
        ch = chapters.get(cn)
        if not ch:
            continue
        vol = f"{CHAP_ZH.get(cn, ch['title_en'])}（第{cn}章）"
        for i, en in enumerate(chunk_paras(ch["paras"], args.max_chars)):
            units.append({"key": f"ch{cn:02d}_{i:03d}", "chapter": cn, "en": en,
                          "title_en": ch["title_en"], "volume": vol,
                          "chapter_path": f"{CHAP_ZH.get(cn, ch['title_en'])} · {i + 1:03d}"})
    if args.inspect:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        for cn in want:
            ch = chapters.get(cn)
            if ch:
                print(f"ch{cn}: {ch['title_en'][:60]} | paras={len(ch['paras'])} "
                      f"chunks={len(chunk_paras(ch['paras'], args.max_chars))}")
        print("total units:", len(units))
        return

    import translate_ebook_to_zh as te
    engine_fn = {"auto": te.gemini_with_nvidia_fallback, "nvidia": te.nvidia_with_gemini_fallback,
                 "haiku": te.haiku_translate}[args.engine]
    todo = units[:args.limit] if args.limit else units
    done = sum((PARTS / f"{u['key']}.json").exists() for u in todo)
    print(f"units={len(todo)} done={done} engine={args.engine}", flush=True)
    for k, u in enumerate(todo):
        part = PARTS / f"{u['key']}.json"
        if part.exists():
            continue
        save_status(current=u["key"], done=done, total=len(todo))
        zh_parts = [te._to_traditional(engine_fn(s)) for s in te.split_oversized(u["en"])]
        part.write_text(json.dumps({"key": u["key"], "en": u["en"], "zh": "\n\n".join(zh_parts),
                                    "at": dt.datetime.now().isoformat(timespec="seconds")},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
        done += 1
        print(f"  {done}/{len(todo)} {u['key']}", flush=True)
        if done % args.upload_every == 0:
            assemble(units, upload=not args.no_upload)
        time.sleep(0.5)
    assemble(units, upload=not args.no_upload)
    save_status(done=done, total=len(todo), current=None)
    print("complete", flush=True)


if __name__ == "__main__":
    main()
