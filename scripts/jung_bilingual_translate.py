"""Generic resumable English→繁中 bilingual translator for public-domain Jung
early works (no clean parallel German → 英+繁中 two-column). Handles a Gutenberg
HTML source or an archive.org djvu.txt source. Engine = NVIDIA-first chain from
translate_ebook_to_zh; checkpoint per chunk, per-chunk error tolerance, resumable,
uploads every N chunks. Books register in WORKS; run --work <slug> or --all.

Sibling of jung_collected_papers_translate.py (which is #48225-specific); this one
is reusable for any single English PD work → Jung hub bilingual ebook.
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

DATA_ROOT = Path(".claude/skills/ebook-collected-works/jung_data")

WORKS = {
    "theory-psychoanalysis": {
        "ebid": "22222225-2222-4222-8222-222222222225",
        "title": "精神分析理論（1913 Fordham 講稿·英繁中對照）",
        "src_title": "The Theory of Psychoanalysis (1915)",
        "src": r"C:/tmp/jung_theory_psa.html", "fmt": "html",
        "file_path": "Project Gutenberg/66041", "year": 1915,
    },
    "dementia-praecox": {
        "ebid": "22222226-2222-4222-8222-222222222226",
        "title": "早發性癡呆心理學（1909英譯·英繁中對照）",
        "src_title": "The Psychology of Dementia Praecox (Peterson & Brill, 1909)",
        "src": r"C:/tmp/jung_dementia.txt", "fmt": "txt",
        "file_path": "Internet Archive/psychologyofdeme00junguoft", "year": 1909,
    },
    "word-association": {
        "ebid": "22222227-2222-4222-8222-222222222227",
        "title": "字詞聯想研究（1918英譯·英繁中對照）",
        "src_title": "Studies in Word-Association (Eder, 1918)",
        "src": r"C:/tmp/jung_wordassoc.txt", "fmt": "txt",
        "file_path": "Internet Archive/studiesinwordass00jung", "year": 1918,
    },
}


def load_env() -> None:
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def parse_html(path: str) -> list[dict]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(Path(path).read_text(encoding="utf-8", errors="replace"), "html.parser")
    for sel in soup.select("#pg-header, #pg-footer, .pagenum, .pageno"):
        sel.decompose()
    out, heading = [], "Front Matter"
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
        txt = re.sub(r"\s+", " ", el.get_text(" ")).strip()
        if not txt or txt.lower().startswith(("the project gutenberg", "produced by", "transcriber")):
            continue
        if el.name in ("h1", "h2", "h3", "h4"):
            heading = txt[:120]
        else:
            out.append({"heading": heading, "text": txt})
    return out


def parse_txt(path: str) -> list[dict]:
    """Clean archive djvu OCR → paragraphs, tag running ALL-CAPS heading."""
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    raw = raw.replace("\r\n", "\n").replace("¬\n", "").replace("\xad", "")
    raw = re.sub(r"([A-Za-z])-\n\s*([a-z])", r"\1\2", raw)  # de-hyphenate
    lines, heading = [], "Front Matter"
    for ln in raw.split("\n"):
        s = re.sub(r"[ \t]+", " ", ln).strip()
        if not s or re.fullmatch(r"[\d ivxlcdm.,\-]+", s.lower()):
            lines.append("")
            continue
        lines.append(s)
    # coalesce into paragraphs on blank lines
    paras, cur = [], []
    for s in lines:
        if s:
            cur.append(s)
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    out = []
    for p in paras:
        if p.upper() == p and re.search(r"[A-Z]", p) and len(p) <= 70:
            heading = p[:120]
            continue
        out.append({"heading": heading, "text": p})
    return out


def chunk_units(paras: list[dict], max_chars: int) -> list[dict]:
    units, cur, n, head = [], [], 0, None
    for p in paras:
        if head is None:
            head = p["heading"]
        if cur and n + len(p["text"]) + 2 > max_chars:
            units.append({"heading": head, "en": "\n\n".join(cur)})
            cur, n, head = [], 0, p["heading"]
        cur.append(p["text"])
        n += len(p["text"]) + 2
    if cur:
        units.append({"heading": head, "en": "\n\n".join(cur)})
    return units


def assemble(cfg: dict, data: Path, units: list[dict], *, upload: bool) -> None:
    out = [{"chunk_index": 0, "chunk_type": "chapter", "page_number": None,
            "chapter_path": "封面", "format": "markdown", "content": f"## {cfg['title']}"}]
    ci = 1
    for i, u in enumerate(units):
        part = data / "parts" / f"{i:04d}.json"
        if not part.exists():
            continue
        obj = json.loads(part.read_text(encoding="utf-8"))
        c = build_multilang_chunk(chunk_index=ci, chapter_path=f"{cfg['title']} · {i + 1:04d}",
                                  volume=cfg["title"], parent_volume="榮格早期著作",
                                  title_en=u["heading"], content_zh=obj["zh"],
                                  sources={"en": obj["en"]}, source_order=["en"])
        validate_multilang_chunk(c)
        out.append(c)
        ci += 1
    base = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
    base.mkdir(parents=True, exist_ok=True)
    write_jsonl(out, base / f"{cfg['ebid']}.jsonl")
    print(f"  assembled {len(out)} chunks", flush=True)
    if not upload:
        return
    import requests

    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    hj = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates"}
    hg = {"apikey": key, "Authorization": f"Bearer {key}"}
    now = dt.datetime.utcnow().isoformat() + "Z"
    row = {"id": cfg["ebid"], "title": cfg["title"], "author": "C. G. 榮格", "author_en": "C. G. Jung",
           "original_title": cfg["src_title"], "file_type": "epub", "file_path": cfg["file_path"],
           "category": "世界宗教", "subcategory": "深層心理學", "display_mode": "standard",
           "translator": "Codex（NVIDIA 英譯本重譯繁中）", "publication_year": cfg["year"],
           "chunk_count": len(out), "total_pages": len(out),
           "total_chars": sum(len(c["content"]) for c in out), "parsed_at": now, "standardized_at": now}
    try:
        requests.post(f"{url}/rest/v1/ebooks", headers=hj, json=row, timeout=30).raise_for_status()
        requests.delete(f"{url}/rest/v1/ebook_chunks?ebook_id=eq.{cfg['ebid']}", headers=hg, timeout=60).raise_for_status()
        prev = [{"ebook_id": cfg["ebid"], "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
                 "page_number": c.get("page_number"), "chapter_path": c["chapter_path"],
                 "content": c["content"][:200], "char_count": len(c["content"])} for c in out]
        for i in range(0, len(prev), 20):
            requests.post(f"{url}/rest/v1/ebook_chunks", headers=hj, json=prev[i:i + 20], timeout=60).raise_for_status()
        print(f"  upserted previews={len(prev)}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARN upload: {exc}", flush=True)


PRE = re.compile(r"^(以下是?|以下為|這是?|下面是?|這裡是|好的|當然|茲將)[^\n]{0,80}(翻譯|繁體中文|中文版|譯文|版本|如下|結果|Markdown|對照)[^\n]{0,120}[:：。]?\s*$")
RULE = re.compile(r"^[-*_]{3,}$")


def clean_preamble(zh: str) -> str:
    paras = zh.split("\n\n")
    while paras and (PRE.match(paras[0].strip()) or RULE.match(paras[0].strip()) or not paras[0].strip()):
        paras.pop(0)
    return "\n\n".join(paras)


def run_work(slug: str, cfg: dict, args) -> None:
    import translate_ebook_to_zh as te

    engine = {"nvidia": te.nvidia_with_gemini_fallback, "auto": te.gemini_with_nvidia_fallback,
              "haiku": te.haiku_translate}[args.engine]
    data = DATA_ROOT / slug
    (data / "parts").mkdir(parents=True, exist_ok=True)
    paras = parse_html(cfg["src"]) if cfg["fmt"] == "html" else parse_txt(cfg["src"])
    units = chunk_units(paras, args.max_chars)
    if args.limit:
        units = units[:args.limit]
    print(f"[{slug}] paras={len(paras)} units={len(units)}", flush=True)
    if args.inspect:
        return
    done = sum((data / "parts" / f"{i:04d}.json").exists() for i in range(len(units)))
    for i, u in enumerate(units):
        part = data / "parts" / f"{i:04d}.json"
        if part.exists():
            continue
        try:
            zh = "\n\n".join(te._to_traditional(engine(s)) for s in te.split_oversized(u["en"]))
            zh = clean_preamble(zh)
        except Exception as exc:  # noqa: BLE001
            print(f"  SKIP {i:04d}: {type(exc).__name__} {str(exc)[:100]}", flush=True)
            time.sleep(8)
            continue
        part.write_text(json.dumps({"i": i, "en": u["en"], "zh": zh,
                                    "at": dt.datetime.now().isoformat(timespec="seconds")},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
        done += 1
        (data / "status.json").write_text(json.dumps(
            {"ebook_id": cfg["ebid"], "title": cfg["title"], "done": done, "total": len(units),
             "current": f"{i:04d}", "updated_at": dt.datetime.now().isoformat(timespec="seconds")},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {done}/{len(units)} {slug} {i:04d}", flush=True)
        if done % args.upload_every == 0:
            assemble(cfg, data, units, upload=not args.no_upload)
        time.sleep(0.4)
    assemble(cfg, data, units, upload=not args.no_upload)
    print(f"[{slug}] complete", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", choices=list(WORKS))
    ap.add_argument("--all", action="store_true", help="run all works sequentially")
    ap.add_argument("--order", help="comma slugs order for --all")
    ap.add_argument("--engine", default="nvidia", choices=["nvidia", "auto", "haiku"])
    ap.add_argument("--max-chars", type=int, default=4200)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--upload-every", type=int, default=8)
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()
    load_env()
    if args.all:
        slugs = args.order.split(",") if args.order else list(WORKS)
    elif args.work:
        slugs = [args.work]
    else:
        ap.error("need --work or --all")
    for slug in slugs:
        run_work(slug, WORKS[slug], args)


if __name__ == "__main__":
    main()
