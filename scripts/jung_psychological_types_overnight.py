"""Overnight local-Ollama translator for Jung, Psychological Types (1923).

Input is the Internet Archive djvu text for the 1923 Baynes English translation.
The script is deliberately checkpoint-heavy:

* source is cleaned and split into stable chunks
* each translated chunk is written as its own JSON file
* reruns skip completed chunks
* every N chunks it assembles a partial bilingual reader JSONL and upserts it

This is for the public-domain early English edition, not the later Hull CW6 text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import requests

sys.path.insert(0, "scripts")
from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl

try:
    from opencc import OpenCC
except Exception:  # noqa: BLE001
    OpenCC = None

EBID = "22222223-2222-4222-8222-222222222223"
TITLE = "心理類型（1923英譯早期版）"
SOURCE_TITLE = "Psychological Types: or, The Psychology of Individuation (1923)"
AUTHOR = "C. G. 榮格"
SOURCE_URL = "https://archive.org/download/psychological_types/psychological_types_djvu.txt"
SRC = Path(r"C:/tmp/jung_psychological_types_1923_en.txt")
DATA = Path(".claude/skills/ebook-collected-works/jung_data/psychological-types-1923")
PARTS = DATA / "parts"
STATUS = DATA / "status.json"
MODEL = "qwen2.5:7b"
_OPENCC = OpenCC("s2t") if OpenCC else None


PROMPT = """你是榮格《Psychological Types》（1923 英譯早期版）的繁體中文譯者。
請把下列英文譯成流暢、學術、可閱讀的繁體中文。

硬性規則：
1. 只輸出繁體中文譯文，不要前言、不要解釋。
2. 保留段落分段；必要時可保留人名、拉丁文、希臘文、德文術語原形。
3. 術語一致：
   - psychological type = 心理類型
   - extraversion = 外傾；introversion = 內傾
   - extraverted = 外傾的；introverted = 內傾的
   - thinking = 思維；feeling = 情感；sensation = 感覺；intuition = 直覺
   - unconscious = 無意識；consciousness = 意識
   - libido = 力比多；complex = 情結；affect = 情感作用
   - collective unconscious = 集體無意識；individuation = 個體化
   - ego = 自我；self = 自性（若明顯只是普通 oneself 才譯為自己）
4. OCR 偶有斷詞或頁眉，請依上下文順讀，不要把明顯頁眉當正文發揮。

英文原文：
"""


def load_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def ensure_source() -> None:
    if SRC.exists() and SRC.stat().st_size > 1_000_000:
        return
    SRC.parent.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(SOURCE_URL, timeout=90).read()
    SRC.write_bytes(data)


def _find_core(text: str) -> str:
    start_candidates = [
        text.find("TRANSLATORS  PREFACE", 10_000),
        text.find("TRANSLATOR'S PREFACE", 10_000),
        text.find("FOREWORD", 10_000),
    ]
    start = min([x for x in start_candidates if x > 0], default=0)
    idx = text.rfind("\nINDEX")
    end = idx if idx > start else len(text)
    return text[start:end]


def clean_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("¬\n", "").replace("¬", "")
    text = re.sub(r"([A-Za-z])-\n\s*([a-z])", r"\1\2", text)
    text = _find_core(text)
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            lines.append("")
            continue
        if re.fullmatch(r"\d{1,4}", line):
            continue
        if re.fullmatch(r"[ivxlcdmIVXLCDM]{1,8}", line):
            continue
        # Drop repeated page headers, but keep real structural headings.
        is_caps = line.upper() == line and re.search(r"[A-Z]", line)
        keep_caps = line.startswith(("CHAPTER", "FOREWORD", "INTRODUCTION", "TRANSLATORS", "DEFINITIONS"))
        if is_caps and not keep_caps and len(line) <= 70:
            continue
        lines.append(line)

    paras: list[str] = []
    cur: list[str] = []
    for line in lines:
        if not line:
            if cur:
                paras.append(" ".join(cur).strip())
                cur = []
            continue
        cur.append(line)
    if cur:
        paras.append(" ".join(cur).strip())

    cleaned = "\n\n".join(p for p in paras if p)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    return cleaned


def split_chunks(text: str, max_chars: int) -> list[dict]:
    paras = text.split("\n\n")
    chunks: list[dict] = []
    cur: list[str] = []
    cur_len = 0
    heading = "Front Matter"
    for para in paras:
        if re.match(r"^(CHAPTER [IVXLCDM]+|FOREWORD|INTRODUCTION|TRANSLATORS)", para):
            heading = para[:120]
        if cur and cur_len + len(para) + 2 > max_chars:
            chunks.append({"idx": len(chunks) + 1, "heading": heading, "en": "\n\n".join(cur)})
            cur = []
            cur_len = 0
        cur.append(para)
        cur_len += len(para) + 2
    if cur:
        chunks.append({"idx": len(chunks) + 1, "heading": heading, "en": "\n\n".join(cur)})
    return chunks


def call_ollama(en: str, *, retries: int = 3) -> str:
    payload = json.dumps({
        "model": MODEL,
        "prompt": PROMPT + en,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 8192,
            "num_predict": 3600,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=420) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            zh = (data.get("response") or "").strip()
            if len(zh) < 20:
                raise RuntimeError(f"too-short translation: {zh!r}")
            return to_traditional(zh)
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            last = exc
            time.sleep(15 * attempt)
    raise RuntimeError(f"ollama failed after retries: {last}")


def to_traditional(text: str) -> str:
    if _OPENCC:
        return _OPENCC.convert(text)
    return text


def save_status(total: int, done: int, current: int | None = None, error: str | None = None) -> None:
    STATUS.write_text(json.dumps({
        "ebook_id": EBID,
        "title": TITLE,
        "model": MODEL,
        "total": total,
        "done": done,
        "current": current,
        "error": error,
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def assemble_and_upload(chunks: list[dict], *, upload: bool) -> None:
    load_env()
    out_chunks = [{
        "chunk_index": 0,
        "chunk_type": "chapter",
        "page_number": None,
        "chapter_path": "封面",
        "format": "markdown",
        "content": f"## {TITLE}",
    }]

    for chunk in chunks:
        part = PARTS / f"{chunk['idx']:04d}.json"
        if not part.exists():
            break
        obj = json.loads(part.read_text(encoding="utf-8"))
        c = build_multilang_chunk(
            chunk_index=chunk["idx"],
            chapter_path=f"{TITLE} · {chunk['idx']:04d}",
            volume=TITLE,
            parent_volume="榮格早期著作",
            title_en=chunk["heading"],
            content_zh=obj["zh"],
            sources={"en": obj["en"]},
            source_order=["en"],
        )
        validate_multilang_chunk(c)
        out_chunks.append(c)

    base = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
    base.mkdir(parents=True, exist_ok=True)
    out = base / f"{EBID}.jsonl"
    write_jsonl(out_chunks, out)
    print(f"assembled {len(out_chunks)} chunks -> {out}", flush=True)

    if not upload:
        return
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h_json = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
              "Prefer": "resolution=merge-duplicates"}
    h_get = {"apikey": key, "Authorization": f"Bearer {key}"}
    now = dt.datetime.utcnow().isoformat() + "Z"
    row = {
        "id": EBID,
        "title": TITLE,
        "author": AUTHOR,
        "author_en": "C. G. Jung",
        "original_title": SOURCE_TITLE,
        "file_type": "epub",
        "file_path": "Internet Archive/psychological_types",
        "category": "世界宗教",
        "subcategory": "深層心理學",
        "display_mode": "standard",
        "translator": "Codex + 本地 Ollama（英譯本重譯繁中）",
        "publication_year": 1923,
        "chunk_count": len(out_chunks),
        "total_pages": len(out_chunks),
        "total_chars": sum(len(c["content"]) for c in out_chunks),
        "parsed_at": now,
        "standardized_at": now,
    }
    try:
        requests.post(f"{url}/rest/v1/ebooks", headers=h_json, json=row, timeout=30).raise_for_status()
        requests.delete(f"{url}/rest/v1/ebook_chunks?ebook_id=eq.{EBID}", headers=h_get, timeout=60).raise_for_status()
        previews = [{"ebook_id": EBID, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
                     "page_number": c.get("page_number"), "chapter_path": c["chapter_path"],
                     "content": c["content"][:200], "char_count": len(c["content"])} for c in out_chunks]
        for i in range(0, len(previews), 10):
            r = requests.post(f"{url}/rest/v1/ebook_chunks", headers=h_json, json=previews[i:i + 10], timeout=60)
            if not r.ok:
                print(f"  WARN preview upsert failed {r.status_code}: {r.text[:500]}", flush=True)
                return
        print(f"upserted ebook {EBID} previews={len(previews)}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARN upload failed but continuing: {exc}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-chars", type=int, default=5500)
    ap.add_argument("--upload-every", type=int, default=10)
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    PARTS.mkdir(parents=True, exist_ok=True)
    ensure_source()
    text = clean_text(SRC.read_text(encoding="utf-8", errors="replace"))
    chunks = split_chunks(text, args.max_chars)
    if args.limit:
        chunks = chunks[:args.limit]
    (DATA / "source_chunks.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
        encoding="utf-8",
    )
    done = sum((PARTS / f"{c['idx']:04d}.json").exists() for c in chunks)
    save_status(len(chunks), done)
    print(f"chunks total={len(chunks)} done={done}", flush=True)

    for chunk in chunks:
        part = PARTS / f"{chunk['idx']:04d}.json"
        if part.exists():
            continue
        save_status(len(chunks), done, current=chunk["idx"])
        print(f"translating {chunk['idx']:04d}/{len(chunks)} {chunk['heading'][:70]!r}", flush=True)
        try:
            zh = call_ollama(chunk["en"])
            part.write_text(json.dumps({
                "idx": chunk["idx"],
                "heading": chunk["heading"],
                "en": chunk["en"],
                "zh": zh,
                "model": MODEL,
                "translated_at": dt.datetime.now().isoformat(timespec="seconds"),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            done += 1
            save_status(len(chunks), done)
            if done == 1 or done % args.upload_every == 0:
                assemble_and_upload(chunks, upload=not args.no_upload)
            time.sleep(args.sleep)
        except Exception as exc:  # noqa: BLE001
            save_status(len(chunks), done, current=chunk["idx"], error=str(exc))
            raise

    assemble_and_upload(chunks, upload=not args.no_upload)
    save_status(len(chunks), done)
    print("complete", flush=True)


if __name__ == "__main__":
    main()
