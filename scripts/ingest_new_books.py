#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily z-lib ingest.

Watches the skill-local "z-lib" drop folder, and for each ebook file:
  1. Parses filename -> (author, title) using parse_drive_inventory.parse_filename
     (handles z-library pattern, "by Author", 全形 comma split, etc.)
  2. Asks Gemini to classify into one of the 9 main categories
     (with a fallback rule for English Christian-studies books -> 宗教學).
  3. Inserts an `ebooks` row with category set + future Drive path as file_path.
  4. Moves the local file from z-lib/ to
     G:/我的雲端硬碟/資料/電子書/{category}/{author}，{title}.{ext}
     Since G: is the Drive sync mount, the move IS the upload (sync client
     uploads in background) AND the local-delete in one filesystem rename.

After ingest, the new ebook row has parsed_at = NULL, so the next
parse_worker.py / ocr_with_gemini.py run picks it up automatically.

Usage:
  python scripts/ingest_new_books.py status
  python scripts/ingest_new_books.py run [--limit N] [--dry-run]
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import parse_filename, to_traditional, TITLE_AUTHOR_OVERRIDES


NEW_BOOK_DIR = Path(__file__).resolve().parent.parent / "z-lib"
DRIVE_ROOT = Path("G:/我的雲端硬碟/資料/電子書")
EBOOK_EXTS = {".pdf", ".epub", ".mobi", ".azw3", ".azw"}
INVALID_FNAME_CHARS = {
    "<": "＜", ">": "＞", ":": "：", '"': "＂", "|": "｜",
    "?": "？", "*": "＊", "\\": "＼", "/": "／",
}

CATEGORIES = [
    "哲學", "世界宗教", "宗教學", "人類生物學", "心理學",
    "文學", "自然科學", "歷史學", "社會政治學",
]


def load_env():
    env = {}
    with open(Path(__file__).parent.parent / ".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
SB_HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
}


def _find_gemini_keys() -> list[str]:
    """Return all usable Gemini API keys (in order). Supports bare-name slots
    (GEMINI_API_KEY / Gemini_API_Key / GOOGLE_API_KEY), numbered slots
    (Gemini_API_Key_1 .. _10), and comma-separated multi-key strings — the
    same .env layout `ocr_with_gemini.py` uses. Free-tier daily quota is
    per-key, so rotating lets ingest survive a single-key 429 lockout."""
    primary = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    raw_values: list[str] = []
    for name in primary:
        v = os.environ.get(name) or ENV.get(name)
        if v:
            raw_values.append(v); break
    for n in range(1, 11):
        for base in primary:
            v = os.environ.get(f"{base}_{n}") or ENV.get(f"{base}_{n}")
            if v:
                raw_values.append(v); break
    keys: list[str] = []
    seen: set[str] = set()
    for raw in raw_values:
        for piece in raw.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_gemini_keys()
GEMINI_KEY = GEMINI_KEYS[0] if GEMINI_KEYS else None  # back-compat
_gemini_key_idx = 0  # index into GEMINI_KEYS — advances only when current key hits 429


def sanitize_filename(name: str) -> str:
    for bad, good in INVALID_FNAME_CHARS.items():
        name = name.replace(bad, good)
    return name.strip()


_ZLIB_SUFFIX_RE = re.compile(r"\s*\([^()]*(?:z-lib|z-library|1lib)[^()]*\)\s*", re.I)


def _strip_zlib_suffix(name: str) -> str:
    """parse_drive_inventory.parse_filename only recognises '(z-lib.org)' / '(z-library)'.
    The newer mirror writes '(z-library.sk, 1lib.sk, z-lib.sk)' — internal commas
    confuse the comma-split fallback and produce nonsense author/title. Strip any
    paren containing a z-lib host before delegating to the shared parser."""
    stem = Path(name).stem
    ext = Path(name).suffix
    cleaned = _ZLIB_SUFFIX_RE.sub(" ", stem).strip()
    return f"{cleaned}{ext}"


def parse_book_meta(filename: str) -> dict:
    """Filename -> {author, title, ext}. Returns {} if parsing produced no usable title."""
    info = parse_filename(_strip_zlib_suffix(filename))
    title = (info.get("short") or info.get("full") or "").strip()
    author = (info.get("author") or "").strip()
    # Convert simplified -> traditional for Chinese; English passes through unchanged
    if title:
        title = to_traditional(title)
    if author:
        author = to_traditional(author)
    # Manual overrides for known patterns where author can't be parsed
    if not author:
        for pattern, ovr in TITLE_AUTHOR_OVERRIDES:
            if pattern in filename:
                author = ovr
                break
    # Strip leaked extension
    title = re.sub(r"\.(pdf|epub|mobi|azw3|azw)\b", "", title, flags=re.I).strip()
    author = re.sub(r"\.(pdf|epub|mobi|azw3|azw)\b", "", author, flags=re.I).strip()
    # Dedupe author "X [X]"
    author = re.sub(r"^(.+?)\s*\[\1\]$", r"\1", author).strip()
    if not title:
        return {}
    ext = Path(filename).suffix.lower().lstrip(".")
    return {"author": author or None, "title": title, "ext": ext}


def fallback_category(title: str, author: str) -> str | None:
    """Cheap keyword pre-classifier for common cases — saves Gemini calls."""
    text = f"{title} {author}".lower()
    christian_kw = [
        "christ", "christian", "christology", "church", "bonhoeffer", "syriac",
        "nestorius", "cyril", "monophysite", "chalcedon", "ephrem", "babai",
        "homilies", "patristic", "apostolic", "gospel", "biblical", "theology",
    ]
    if any(k in text for k in christian_kw):
        return "宗教學"
    if "zoroastr" in text or "avesta" in text or "islam" in text or "buddhis" in text:
        return "世界宗教"
    return None


CATEGORIZE_PROMPT = """你是書籍分類助手。請將下列書籍歸入恰好一個分類：

九大分類（擇一）：
- 哲學 — 哲學家、哲學流派、形上學、倫理學、邏輯學
- 世界宗教 — 特定宗教的經典、教義、史實（基督教、伊斯蘭、佛教、印度教、瑣羅亞斯德教、巴哈伊…）
- 宗教學 — 神學、聖經研究、教會史、宗教社會學、宗教比較學等學術研究
- 人類生物學 — 人類學、生物人類學、演化、考古、體質
- 心理學 — 心理學、精神分析、認知科學
- 文學 — 小說、詩歌、散文、文學評論
- 自然科學 — 物理、化學、生物、地球科學、數學
- 歷史學 — 通史、斷代史、地區史、人物傳記（非宗教人物）
- 社會政治學 — 政治、經濟、社會學、法律、國際關係

辨別技巧：
- 「教會史」「基督論」「神學家」屬 宗教學（學術研究）
- 「巴哈伊經典」「可蘭經」「阿維斯塔」屬 世界宗教（宗教文獻本身）
- 不確定時，傾向 宗教學 而非 世界宗教

書名: {title}
作者: {author}

只回傳一行 JSON，無其他文字：
{{"category":"<從上面九個擇一>","subcategory":"<細分名稱或 null>","confidence":0.0-1.0}}
"""


def gemini_classify(title: str, author: str) -> dict:
    """Returns {category, subcategory, confidence}. Raises on hard error.

    Rotates through GEMINI_KEYS on 429 — free-tier RPD is per-key, so if
    key #1 is exhausted from earlier OCR runs, switching to #2/#3/#4 buys
    a fresh quota window without waiting for daily reset.
    """
    global _gemini_key_idx
    if not GEMINI_KEYS:
        raise RuntimeError("Gemini API key not found in env")
    prompt = CATEGORIZE_PROMPT.format(title=title, author=author or "(unknown)")
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }
    base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    # Per-key budget: 4 attempts with short backoff (transient spike). On
    # persistent 429 advance to next key and reset attempts.
    last_err: str | None = None
    while _gemini_key_idx < len(GEMINI_KEYS):
        key = GEMINI_KEYS[_gemini_key_idx]
        url = f"{base_url}?key={key}"
        rotated = False
        for attempt, wait in enumerate((0, 5, 15, 30), start=1):
            if wait:
                time.sleep(wait)
            r = requests.post(url, json=body, timeout=30)
            if r.status_code == 200:
                break
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code in (429, 503) and attempt < 4:
                print(f"    Gemini {r.status_code} on key #{_gemini_key_idx} — "
                      f"retry {attempt} after {wait + (5 if attempt == 1 else 15)}s",
                      file=sys.stderr)
                continue
            if r.status_code == 429:
                # Persistent 429 on this key — try the next one.
                if _gemini_key_idx + 1 < len(GEMINI_KEYS):
                    _gemini_key_idx += 1
                    print(f"    ⟳ Gemini 429 on key #{_gemini_key_idx - 1}; "
                          f"switching to key #{_gemini_key_idx} of {len(GEMINI_KEYS)}",
                          file=sys.stderr)
                    rotated = True
                    break  # re-enter outer while with new key
                raise RuntimeError(f"Gemini {last_err} (all {len(GEMINI_KEYS)} keys exhausted)")
            raise RuntimeError(f"Gemini {last_err}")
        if rotated:
            continue
        break
    data = r.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Be lenient with markdown fences
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.M).strip()
    parsed = json.loads(text)
    cat = parsed.get("category", "").strip()
    if cat not in CATEGORIES:
        # Map some common LLM mistakes
        if cat in {"基督教", "神學", "聖經研究", "教會史"}:
            cat = "宗教學"
        elif cat in {"伊斯蘭教", "佛教", "印度教", "瑣羅亞斯德教"}:
            cat = "世界宗教"
        else:
            raise ValueError(f"Gemini returned non-category: {cat!r}")
    return {
        "category": cat,
        "subcategory": (parsed.get("subcategory") or None),
        "confidence": float(parsed.get("confidence", 0.5)),
    }


def classify(title: str, author: str) -> dict:
    fb = fallback_category(title, author)
    if fb:
        return {"category": fb, "subcategory": None, "confidence": 0.9, "source": "fallback"}
    g = gemini_classify(title, author)
    g["source"] = "gemini"
    return g


def build_target_path(meta: dict, category: str) -> Path:
    """Build the destination path under DRIVE_ROOT/{category}/."""
    title = meta["title"].strip()
    author = (meta.get("author") or "").strip()
    ext = meta["ext"]
    if author:
        new_name = f"{author}，{title}.{ext}"
    else:
        new_name = f"{title}.{ext}"
    new_name = sanitize_filename(new_name)
    if len(new_name) > 200:
        # Truncate title; keep author
        keep = 200 - len(author) - len(ext) - 4
        title = title[:max(20, keep)]
        new_name = sanitize_filename(f"{author}，{title}.{ext}" if author else f"{title}.{ext}")
    return DRIVE_ROOT / category / new_name


def supabase_insert(meta: dict, category: str, subcategory: str | None, target_path: Path) -> str | None:
    """Insert ebooks row, return id, or None on failure (already-exists by file_path is fine)."""
    payload = [{
        "title": meta["title"],
        "author": meta.get("author"),
        "file_type": meta["ext"],
        "category": category,
        "subcategory": subcategory,
        "file_path": str(target_path).replace("/", "\\"),
    }]
    r = requests.post(
        f"{URL}/rest/v1/ebooks",
        headers={**SB_HEADERS, "Prefer": "return=representation,resolution=ignore-duplicates"},
        json=payload,
        timeout=20,
    )
    if r.status_code in (200, 201):
        rows = r.json()
        if rows:
            return rows[0]["id"]
    print(f"    [DB] insert failed HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return None


def cmd_status():
    if not NEW_BOOK_DIR.exists():
        print(f"z-lib dir not found: {NEW_BOOK_DIR}")
        return
    files = [p for p in NEW_BOOK_DIR.iterdir() if p.is_file() and p.suffix.lower() in EBOOK_EXTS]
    junk = [p for p in NEW_BOOK_DIR.iterdir() if p.is_file() and p.suffix.lower() not in EBOOK_EXTS]
    print(f"Drop folder: {NEW_BOOK_DIR}")
    print(f"  ebooks waiting: {len(files)}")
    for p in files[:10]:
        print(f"    - {p.name}  ({p.stat().st_size//1024} KB)")
    if len(files) > 10:
        print(f"    ... +{len(files)-10} more")
    if junk:
        print(f"  non-ebook files (will be ignored): {len(junk)}")
        for p in junk:
            print(f"    - {p.name}")


def cmd_run(limit: int | None, dry_run: bool):
    if not NEW_BOOK_DIR.exists():
        print(f"z-lib dir missing: {NEW_BOOK_DIR}", file=sys.stderr)
        return 0
    files = sorted(p for p in NEW_BOOK_DIR.iterdir() if p.is_file() and p.suffix.lower() in EBOOK_EXTS)
    if limit:
        files = files[:limit]
    if not files:
        print("No new books to ingest.")
        return 0

    ok = 0
    fail = 0
    for p in files:
        print(f"\n[{p.name}]")
        meta = parse_book_meta(p.name)
        if not meta:
            print("  SKIP: could not parse title from filename")
            fail += 1
            continue
        print(f"  parsed: title={meta['title']!r}  author={meta.get('author')!r}  ext={meta['ext']}")

        try:
            cls = classify(meta["title"], meta.get("author") or "")
        except Exception as e:
            print(f"  CLASSIFY FAILED: {e}")
            fail += 1
            continue
        print(f"  category: {cls['category']}  subcat: {cls.get('subcategory')}  ({cls['source']}, conf={cls['confidence']:.2f})")

        target = build_target_path(meta, cls["category"])
        print(f"  target: {target}")

        if dry_run:
            ok += 1
            continue

        # Pre-flight: ensure target dir exists & target file doesn't already exist
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            # Duplicate already on Drive — delete the z-lib/ copy so daily runs
            # don't keep scanning the same dupes. Log sizes for verification.
            try:
                z_size = p.stat().st_size
                t_size = target.stat().st_size
                print(f"  SKIP: target already exists on Drive "
                      f"(z-lib={z_size // 1024} KB, drive={t_size // 1024} KB) — deleting z-lib copy")
                p.unlink()
            except Exception as e:
                print(f"  SKIP: target already exists on Drive (delete failed: {e})")
            fail += 1
            continue

        ebook_id = supabase_insert(meta, cls["category"], cls.get("subcategory"), target)
        if not ebook_id:
            print("  ABORT: DB insert failed (file kept in z-lib/)")
            fail += 1
            continue
        print(f"  db: inserted ebook_id={ebook_id}")

        try:
            shutil.move(str(p), str(target))
        except Exception as e:
            print(f"  MOVE FAILED: {e} — DB row was inserted, file still in z-lib/")
            print(f"  manual fix: move file to {target} (Drive will sync), or delete row {ebook_id}")
            fail += 1
            continue
        print(f"  moved -> Drive ({cls['category']})")
        ok += 1
        time.sleep(0.5)  # gentle pacing for Gemini RPM

    print(f"\nDone: {ok} ingested, {fail} failed/skipped (of {len(files)} processed)")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["status", "run"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "status":
        cmd_status()
    else:
        cmd_run(args.limit, args.dry_run)


if __name__ == "__main__":
    main()
