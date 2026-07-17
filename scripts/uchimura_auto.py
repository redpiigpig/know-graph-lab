#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumable ja→繁中 translate queue for Uchimura Kanzō (內村鑑三) Aozora works.

Modeled on scripts/panikkar_auto.py (checkpoint per section, per-work queue,
per-paragraph engine chain Gemini→NVIDIA→Haiku). Source = Aozora Bunko XHTML
cached in c:/tmp/uchimura_cache/ (public domain, fetched throttled 2026-07-16);
parser + registry live in scripts/uchimura_build.py (test-first). One reader
chunk = ≤10 paragraph rows, content=繁中 / sources.ja=原文, equal ¶ counts.

  python scripts/uchimura_auto.py --list
  python scripts/uchimura_auto.py --probe denmark-story --maxparas 3
  python scripts/uchimura_auto.py --work denmark-story --upload
  python scripts/uchimura_auto.py --run-queue          # all 6 works, resumable

Long-running runs are launched DETACHED via PowerShell Start-Process (Bash
background jobs die with the session), logging to scripts/logs/uchimura_translate.log.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import uchimura_build as ub  # noqa: E402  (loads .env, reconfigures stdout)
import panikkar_build as pb  # noqa: E402  (build_section_chunk / build_multilang_chunk)
from multilang_chunks import write_jsonl  # noqa: E402

DATA_ROOT = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / "uchimura_data"
MAX_PARAS_PER_CHUNK = 10


def _sec_path(slug: str, idx: int) -> Path:
    d = DATA_ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    return d / f"sec{idx}.json"


# ── translate (checkpoint per section, resumable) ────────────────────────────
def translate_work(slug: str, translate_para, *, save_every: int = 5,
                   maxparas: int | None = None) -> int:
    secs = ub.load_work_sections(slug)
    w = ub.REGISTRY[slug]
    print(f"  {slug}: {len(secs)} sections ({w['title']})", flush=True)
    translated = 0
    for i, s in enumerate(secs):
        cp = _sec_path(slug, i)
        cache = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
        src = list(s["paras"])
        zh = (list(cache.get("zh") or []) + [None] * len(src))[:len(src)]
        title_zh = cache.get("title_zh") or None
        if title_zh is None:
            if s["heading"] in ("(front)", ""):
                title_zh = w["title"] if i == 0 else s["heading"]
            else:
                title_zh = translate_para(s["heading"]) or s["heading"]
        todo = [j for j in range(len(src)) if not zh[j]]
        if maxparas is not None:
            todo = todo[:maxparas]

        def save() -> None:
            cp.write_text(json.dumps({
                "heading": s["heading"], "title_zh": title_zh,
                "src": src, "zh": zh,
            }, ensure_ascii=False, indent=1), encoding="utf-8")

        for done, j in enumerate(todo, 1):
            out = translate_para(src[j])
            if out:
                zh[j] = out
                translated += 1
            if done % save_every == 0 or done == len(todo):
                save()
        if not todo:
            save()
        filled = sum(1 for z in zh if z)
        print(f"    sec{i} 「{(title_zh or '')[:18]}」 {filled}/{len(src)}", flush=True)
    return translated


def is_done(slug: str) -> bool:
    secs = ub.load_work_sections(slug)
    for i, s in enumerate(secs):
        cp = _sec_path(slug, i)
        if not cp.exists():
            return False
        zh = (json.loads(cp.read_text(encoding="utf-8")).get("zh") or [])
        n = len(s["paras"])
        if n and sum(1 for z in zh if z) < max(1, int(n * 0.95)):
            return False
    return True


# ── build + upload ────────────────────────────────────────────────────────────
def _chunked(zh: list, src: list, maxp: int = MAX_PARAS_PER_CHUNK):
    for k in range(0, len(zh), maxp):
        yield zh[k:k + maxp], src[k:k + maxp]


def build_chunks(slug: str) -> list[dict]:
    w = ub.REGISTRY[slug]
    volume = f"{w['title']}（內村鑑三）"
    chunks = [pb.build_multilang_chunk(
        chunk_index=0, chapter_path="封面", content_zh="## 封面", sources={},
        source_order=[], volume=volume, parent_volume=w["parent_volume"],
        chunk_type="cover", page_number=1)]
    secs = ub.load_work_sections(slug)
    ci = 1
    for i, s in enumerate(secs):
        cp = _sec_path(slug, i)
        if not cp.exists():
            continue
        c = json.loads(cp.read_text(encoding="utf-8"))
        src = c.get("src") or []
        zh = (list(c.get("zh") or []) + [None] * len(src))[:len(src)]
        zh = [(z or sv) for z, sv in zip(zh, src)]  # unfilled → show 原文
        if not any(zh):
            continue
        base_title = (c.get("title_zh") or s["heading"] or w["title"]).strip()
        src_head = s["heading"] if s["heading"] not in ("(front)", "") else w["original_title"]
        groups = list(_chunked(zh, src))
        for part, (zg, sg) in enumerate(groups, 1):
            title = base_title if len(groups) == 1 else f"{base_title}（{part}）"
            head = src_head if len(groups) == 1 else f"{src_head}（{part}）"
            chunks.append(pb.build_section_chunk(
                chunk_index=ci, title_zh=title, zh_paras=zg,
                source_paras={"ja": sg}, source_heads={"ja": head},
                source_order=["ja"], volume=volume,
                parent_volume=w["parent_volume"], page_number=ci + 1))
            ci += 1
    return chunks


def ensure_row(slug: str):
    import requests
    import translate_ebook_to_zh as te
    w = ub.REGISTRY[slug]
    row = {"id": w["ebook_id"], "title": w["title"], "subtitle": w["subtitle"],
           "author": "內村鑑三", "author_en": "Uchimura Kanzō",
           "original_title": w["original_title"], "original_publish_year": w["year"],
           "file_type": "epub", "category": "神學"}
    r = requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id",
                      headers={**te.H_JSON, "Prefer": "resolution=merge-duplicates"},
                      json=row, timeout=30)
    print(f"  ebooks row upsert HTTP {r.status_code}", flush=True)


def upload(slug: str, chunks: list[dict], out_path: Path):
    import datetime
    import requests
    import translate_ebook_to_zh as te
    eid = ub.REGISTRY[slug]["ebook_id"]
    try:
        te.se.push_to_r2(eid, out_path)
        print("  ✓ pushed R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 push failed: {e}", flush=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    patch = {"chunk_count": len(chunks), "total_chars": sum(len(c["content"]) for c in chunks),
             "total_pages": len(chunks), "parsed_at": now, "standardized_at": now}
    requests.patch(f"{te.URL}/rest/v1/ebooks?id=eq.{eid}", headers=te.H_JSON, json=patch, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}", headers=te.H_GET, timeout=30)
    rows = [{"ebook_id": eid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for k in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[k:k + 25], timeout=60)
    print(f"  ✓ row + previews  chunk_count={len(chunks)}", flush=True)


def out_jsonl(slug: str) -> Path:
    import translate_ebook_to_zh as te
    return Path(te.CHUNKS_DIR) / f"{ub.REGISTRY[slug]['ebook_id']}.jsonl"


def build_and_upload(slug: str, *, do_upload: bool):
    chunks = build_chunks(slug)
    out = out_jsonl(slug)
    write_jsonl(chunks, out)
    print(f"  wrote {out.name} ({len(chunks)} chunks)", flush=True)
    if do_upload:
        ensure_row(slug)
        upload(slug, chunks, out)


def run_work(slug: str, *, do_upload: bool, maxparas=None, backend: str = "auto"):
    print(f"=== {slug} : {ub.REGISTRY[slug]['title']} ===", flush=True)
    engine = ub.make_engine(backend)
    translate_work(slug, engine, maxparas=maxparas)
    build_and_upload(slug, do_upload=do_upload)


def run_queue(backend: str = "auto"):
    for slug in ub.QUEUE:
        try:
            if is_done(slug):
                print(f"=== {slug}: already done, (re)building ===", flush=True)
                build_and_upload(slug, do_upload=True)
                continue
            run_work(slug, do_upload=True, backend=backend)
        except Exception as e:  # noqa: BLE001 — keep the queue going
            print(f"  ⚠ {slug} failed: {str(e)[:200]}", flush=True)
    print("QUEUE_COMPLETE", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--probe", type=str, help="translate N paras of a work, print zh sample")
    ap.add_argument("--work", type=str)
    ap.add_argument("--maxparas", type=int, default=None)
    ap.add_argument("--backend", choices=["auto", "gemini", "nvidia", "haiku"], default="auto")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--run-queue", action="store_true")
    args = ap.parse_args()

    if args.list:
        for slug in ub.QUEUE:
            w = ub.REGISTRY[slug]
            secs = ub.load_work_sections(slug)
            total = sum(len(s["paras"]) for s in secs)
            done = sum(1 for i in range(len(secs)) if _sec_path(slug, i).exists()
                       for z in [json.loads(_sec_path(slug, i).read_text(encoding="utf-8")).get("zh") or []]
                       for _ in [0] if sum(1 for x in z if x) >= len(secs[i]["paras"]))
            filled = 0
            for i in range(len(secs)):
                cp = _sec_path(slug, i)
                if cp.exists():
                    filled += sum(1 for x in (json.loads(cp.read_text(encoding="utf-8")).get("zh") or []) if x)
            print(f"  {slug:20} {w['title']:10} paras={total:4} translated={filled:4} done={is_done(slug)}")
        return
    if args.probe:
        engine = ub.make_engine(args.backend)
        n = args.maxparas or 2
        translate_work(args.probe, engine, save_every=1, maxparas=n)
        # print the freshly translated zh sample (translation only — no source echo)
        for i in range(2):
            cp = _sec_path(args.probe, i)
            if cp.exists():
                c = json.loads(cp.read_text(encoding="utf-8"))
                for z in (c.get("zh") or []):
                    if z:
                        print("ZH:", z[:300], flush=True)
        return
    if args.work:
        if args.build_only:
            build_and_upload(args.work, do_upload=args.upload)
            return
        run_work(args.work, do_upload=args.upload, maxparas=args.maxparas, backend=args.backend)
        return
    if args.run_queue:
        run_queue(args.backend)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
