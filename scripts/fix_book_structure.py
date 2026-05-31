"""Library-wide structure repair — two jobs in one resumable, quota-aware tool.

  JOB A  (recover) : NO_TOC page-chunked PDFs whose OCR text is present ->
                     mechanically strip page-numbers + constant furniture
                     header, then ask Gemini flash-lite to infer the chapter
                     hierarchy and ADD chapter_path (additive only — never
                     overwrites existing structure; page_number is sacred).
                     Books whose OCR is too thin are SKIPPED to a needs_reocr
                     list (anti-hallucination gate). Huge books are windowed.

  JOB B  (audit)   : every book that already HAS a TOC (all EPUB + PDFs with
                     chapter_path) is scanned with pure rules for suspect
                     entries (leaked .html/.xml filenames, blockquote/verse
                     lines as headings, bare ordinals). REPORT ONLY — writes
                     no changes. Costs zero LLM quota.

Safety / autonomy:
  - Resumable: a ledger (c:/tmp/structure_fix_ledger.json) records every book's
    outcome; re-running skips done books, so quota pauses never lose progress.
  - Quota: 4 Gemini keys rotated; sustained 429 -> exponential backoff sleep and
    retry (rides through daily-quota windows) instead of crashing.
  - DB writes preserve all columns (rebuilt from JSONL); a guard refuses the
    delete+reinsert path if a book unexpectedly carries source_text, so bilingual
    data can never be clobbered.

Usage:
    python scripts/fix_book_structure.py all              # B then A, full library
    python scripts/fix_book_structure.py audit            # Job B only (no quota)
    python scripts/fix_book_structure.py recover [--limit N] [--dry-run]
    python scripts/fix_book_structure.py recover --ids <id1,id2>   # specific books
"""
from __future__ import annotations
import argparse, json, os, re, statistics, sys, time
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}
CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR") or se.CHUNKS_DIR)

LEDGER = Path("c:/tmp/structure_fix_ledger.json")
NEEDS_REOCR = Path("c:/tmp/needs_reocr.txt")
AUDIT_FLAGS = Path("c:/tmp/toc_audit_flags.txt")
AUDIT_JSON = Path("c:/tmp/structure_audit.json")  # produced by structure_audit.py

GEMINI_KEYS = [os.environ[k] for k in ("GEMINI_API_KEY_1", "GEMINI_API_KEY_2",
                                       "GEMINI_API_KEY_3", "GEMINI_API_KEY_4") if k in os.environ]
MODEL = "gemini-2.5-flash-lite"
MIN_CHARS_PER_PAGE = 25          # density gate: below this avg -> needs re-OCR
WINDOW_PAGES = 280               # huge books are split into windows of this many pages

# ── page furniture helpers ──────────────────────────────────────────────────
ROMAN = re.compile(r"^[ivxlcdmIVXLCDM]{1,6}$")
ARABIC = re.compile(r"^\d{1,4}$")
FN_RE = re.compile(r"\.(x?html?|xml|ncx|opf)\b", re.I)
BQ_RE = re.compile(r"^\s*>")
BARE_RE = re.compile(r"^[一二三四五六七八九十百0-9]{1,3}$")


def strip_leading_pagenum(text: str) -> str:
    lines = text.split("\n")
    while lines and (ARABIC.match(lines[0].strip()) or ROMAN.match(lines[0].strip())):
        lines = lines[1:]
    return "\n".join(lines)


def strip_trailing_pagenum(text: str) -> str:
    lines = text.split("\n")
    while lines and (ARABIC.match(lines[-1].strip()) or ROMAN.match(lines[-1].strip())):
        lines = lines[:-1]
    return "\n".join(lines)


def detect_header(pages: list[dict]) -> tuple[str | None, float, bool]:
    """Longest leading prefix shared by >=30% of pages (after page-number
    removal). Returns (header, coverage, is_constant_furniture)."""
    leads = []
    for c in pages:
        body = strip_leading_pagenum((c.get("content") or "").lstrip()).lstrip()
        if len(body) >= 6:
            leads.append(body[:40])
    if not leads:
        return None, 0.0, False
    n = len(pages)
    best, best_cov = None, 0.0
    for L in range(4, 31):
        p, freq = Counter(l[:L] for l in leads).most_common(1)[0]
        if freq / n >= 0.30:
            best, best_cov = p, freq / n
        else:
            break
    if not best:
        return None, 0.0, False
    followed_nl = sum(1 for l in leads if l.startswith(best) and l[len(best):len(best)+1] == "\n")
    is_constant = followed_nl < 0.5 * best_cov * n
    return best.strip(), round(best_cov, 3), is_constant


# ── Gemini with key rotation + backoff ──────────────────────────────────────
_key_idx = 0


def gemini_json(prompt: str, max_tokens: int = 8192) -> list | None:
    """Call flash-lite expecting a JSON array. Rotates keys; backs off on 429.
    Returns parsed list, or None on hard failure."""
    global _key_idx
    from google import genai
    from google.genai import types
    cfg = types.GenerateContentConfig(response_mime_type="application/json",
                                      temperature=0.0, max_output_tokens=max_tokens)
    backoff = 30
    consecutive_429 = 0
    for _ in range(len(GEMINI_KEYS) * 6):
        try:
            client = genai.Client(api_key=GEMINI_KEYS[_key_idx])
            r = client.models.generate_content(model=MODEL, contents=prompt, config=cfg)
            return _parse_json_array(r.text)
        except Exception as e:
            es = str(e)
            _key_idx = (_key_idx + 1) % len(GEMINI_KEYS)
            if "429" in es or "RESOURCE_EXHAUSTED" in es:
                consecutive_429 += 1
                if consecutive_429 >= len(GEMINI_KEYS):
                    print(f"    all keys 429 — sleeping {backoff}s", flush=True)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 900)
                    consecutive_429 = 0
                continue
            print(f"    gemini error: {es[:80]}", flush=True)
            return None
    return None


def _parse_json_array(text: str) -> list | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except Exception:
        # JSON repair: truncate to the last complete object in the array
        cut = text.rfind("}")
        if cut > 0:
            try:
                return json.loads(text[:cut + 1] + "]")
            except Exception:
                pass
    return None


PROMPT = """你拿到一本中文/外文書的「逐頁首行摘要」。這本書在掃描或 OCR 後失去了目錄結構。
請判讀章/節邊界並輸出目錄。規則：
- 只在你有把握「該頁是某章/節的開頭」時才列出。寧缺勿濫。
- title 必須是**繁體中文**（原文簡體請轉繁；原文英文等保留原文）。
- 標題要**簡短**（最多約 25 字），只取章節名本身：**不要**含內文句子、目錄的點點點「……」、頁碼「（101）」、頁眉碎片，也**不要**輸出像「(Family tree diagram)」這種說明性文字。
- level：1=部/篇/序/附錄/參考文獻，2=章，3=節。同層級用法要一致。
- 若整本幾乎沒有可辨識的章節開頭，回傳空陣列 []（不要杜撰）。

逐頁摘要（格式 `p<頁碼>│<首行>`）：
{skeleton}

只輸出 JSON 陣列，每筆 {{"page": <int>, "level": <1|2|3>, "title": "<標題>"}}。"""


_LEADER_RE = re.compile(r"[.．。…⋯·]{3,}.*$")          # dotted TOC leaders + trailing junk
_TRAIL_PGNUM_RE = re.compile(r"\s*[（(]\s*\d{1,4}\s*[)）]\s*$")
_EN_META_RE = re.compile(r"[（(]\s*[A-Za-z][^）)]{4,}[)）]")  # "(Family tree diagram ...)"
_SENT_CUT = re.compile(r"^(.{8,30}?[。！？])")


def clean_title(t: str) -> str:
    """Zero-cost post-clean of an LLM/OCR title: drop dotted leaders, trailing
    page numbers, English meta-notes; cap body-overflow at a sentence boundary
    or hard length."""
    t = (t or "").strip()
    t = _EN_META_RE.sub("", t)
    t = _LEADER_RE.sub("", t)
    t = _TRAIL_PGNUM_RE.sub("", t)
    t = t.strip(" 　-—－.·")
    if len(t) > 32:                       # body overflow — try to cut at a sentence end
        m = _SENT_CUT.match(t)
        t = (m.group(1) if m else t[:30]).rstrip("，、 ")
    return t.strip()


_L1_RE = re.compile(r"第[一二三四五六七八九十百0-9]+[部篇卷]")
_L1_WORD = re.compile(r"^(序|序言|序論|前言|導言|導論|緒論|結論|結語|餘論|附錄|參考文獻|參考書目|後記|跋|引言|致謝|謝辭|索引|凡例|目錄|出版說明|譯者|FOREWORD|PREFACE|INTRODUCTION|CONTENTS|BIBLIOGRAPHY|APPENDIX|INDEX|NOTES)", re.I)
_L2_RE = re.compile(r"(第[一二三四五六七八九十百0-9]+章)|^\s*(chapter|CHAPTER)\b", re.I)
_L3_RE = re.compile(r"(第[一二三四五六七八九十百0-9]+[節节])|^[一二三四五六七八九十]+\s*[、.]|^\d+\s*[、.]")


def level_from_title(title: str, fallback: int) -> int:
    """Infer hierarchy level from the title's own wording — far more reliable
    than the LLM's level field, which wobbles."""
    t = title.strip()
    if _L1_RE.search(t) or _L1_WORD.match(t):
        return 1
    if _L2_RE.search(t):
        return 2
    if _L3_RE.search(t):
        return 3
    return fallback


def build_skeleton(pages: list[dict], header: str | None) -> str:
    lines = []
    for c in pages:
        body = strip_trailing_pagenum(strip_leading_pagenum((c.get("content") or "").lstrip())).lstrip()
        if header and body.startswith(header):
            body = body[len(header):].lstrip("\n， 　")
        first = re.sub(r"\s+", " ", body[:70]).strip()
        pg = c.get("page_number") or c.get("chunk_index")
        lines.append(f"p{pg}│{first}")
    return "\n".join(lines)


def infer_toc(pages: list[dict], header: str | None) -> list:
    """One book -> merged TOC list. Windows huge books to dodge truncation."""
    if len(pages) <= WINDOW_PAGES:
        toc = gemini_json(PROMPT.format(skeleton=build_skeleton(pages, header)))
        return toc or []
    merged = []
    for i in range(0, len(pages), WINDOW_PAGES):
        win = pages[i:i + WINDOW_PAGES]
        toc = gemini_json(PROMPT.format(skeleton=build_skeleton(win, header)))
        if toc:
            merged.extend(toc)
    return merged


# ── persistence ─────────────────────────────────────────────────────────────
def load_ledger() -> dict:
    if LEDGER.exists():
        try:
            return json.loads(LEDGER.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_ledger(led: dict):
    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")


def fetch_book(eid: str) -> dict | None:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{eid}&select=*", headers=H_GET, timeout=30)
    return (r.json() or [None])[0]


def write_book(eid: str, chunks: list[dict]):
    """Persist JSONL -> R2 -> DB previews. DB refresh rebuilds full rows from
    JSONL (preserves source_text/lang/etc). Guard: never run on a book whose
    chunks carry source_text via the lossy path — but since we rebuild from the
    JSONL which HAS those fields, it is preserved."""
    jsonl_path = CHUNKS_DIR / f"{eid}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    try:
        se.push_to_r2(eid, jsonl_path)
    except Exception as e:
        print(f"    R2 push warn: {str(e)[:60]}", flush=True)
    # rebuild DB previews
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}", headers=H_GET, timeout=30)
    rows = []
    for c in chunks:
        row = {
            "ebook_id": eid, "chunk_index": c["chunk_index"],
            "chunk_type": c.get("chunk_type", "page"), "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": (c.get("content") or "")[:200], "char_count": len(c.get("content") or ""),
        }
        for opt in ("source_text", "source_lang", "section_type", "dh_number", "page_numbers"):
            if c.get(opt) is not None:
                row[opt] = c[opt]
        rows.append(row)
    for i in range(0, len(rows), 25):
        batch = rows[i:i + 25]
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=batch, timeout=40)
        if rr.status_code not in (200, 201):
            for row in batch:
                requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=row, timeout=30)


# ── JOB A — recover ──────────────────────────────────────────────────────────
def recover_book(eid: str, dry_run: bool = False) -> dict:
    jsonl_path = CHUNKS_DIR / f"{eid}.jsonl"
    if not jsonl_path.exists():
        return {"status": "skip", "note": "no jsonl"}
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    pages = [c for c in chunks if c.get("chunk_type") == "page"] or chunks
    if any(c.get("source_text") for c in chunks):
        return {"status": "skip", "note": "has source_text (bilingual) — not a recover target"}

    # density gate (anti-hallucination)
    total_chars = sum(len(c.get("content") or "") for c in pages)
    if total_chars / max(1, len(pages)) < MIN_CHARS_PER_PAGE:
        NEEDS_REOCR.open("a", encoding="utf-8").write(f"{eid}\n")
        return {"status": "needs_reocr", "note": f"thin OCR {total_chars}/{len(pages)} pp"}

    header, cov, is_const = detect_header(pages)
    strip_hdr = header if (is_const and cov >= 0.6 and len(header or "") >= 4) else None

    # Layer-1 strip (page numbers always; furniture header when confident)
    n_stripped = 0
    for c in pages:
        orig = c.get("content") or ""
        body = strip_trailing_pagenum(strip_leading_pagenum(orig.lstrip()))
        if strip_hdr:
            b2 = body.lstrip()
            if b2.startswith(strip_hdr):
                body = b2[len(strip_hdr):].lstrip("\n， 　")
        if body != orig:
            c["content"] = body
            n_stripped += 1

    # Job A — LLM TOC
    toc = infer_toc(pages, strip_hdr)
    if not toc:
        # still persist the strip if it happened
        if n_stripped and not dry_run:
            write_book(eid, chunks)
        return {"status": "no_toc_returned", "stripped": n_stripped,
                "note": "empty TOC (book may be structureless)"}

    by_page = {t["page"]: t for t in toc if isinstance(t, dict) and "page" in t}
    cur, n_assigned = [], 0
    for c in pages:
        pg = c.get("page_number") or c.get("chunk_index")
        if pg in by_page:
            t = by_page[pg]
            title = clean_title(t.get("title") or "")
            if title:
                lvl = level_from_title(title, t.get("level", 2))
                cur = [x for x in cur if x[0] < lvl] + [(lvl, title)]
        cp = " > ".join(x[1] for x in cur) if cur else None
        # ADDITIVE ONLY: never overwrite an existing chapter_path
        if cp and not (c.get("chapter_path") or "").strip():
            c["chapter_path"] = cp
            n_assigned += 1

    if not dry_run:
        write_book(eid, chunks)
    return {"status": "ok", "toc_entries": len(toc), "assigned": n_assigned,
            "stripped": n_stripped, "coverage": f"{n_assigned}/{len(pages)}",
            "header": strip_hdr}


# ── JOB B — audit (rules only, report) ───────────────────────────────────────
def audit_book(eid: str, title: str) -> dict | None:
    r = requests.get(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}"
                     f"&select=chapter_path&limit=800", headers=H_GET, timeout=40)
    paths = [c.get("chapter_path") or "" for c in r.json()]
    nn = [p for p in paths if p]
    if not nn:
        return None  # no TOC -> a recover target, not an audit target
    fn = [p for p in nn if FN_RE.search(p)]
    bq = [p for p in nn if BQ_RE.match(p)]
    bare = [p for p in nn if BARE_RE.match(p.strip())]
    if not (fn or bq or len(bare) >= 3):
        return None
    return {"id": eid, "title": title, "n": len(paths),
            "filename_leaks": len(fn), "blockquote_titles": len(bq), "bare_ordinals": len(bare),
            "samples": (fn[:2] + bq[:2] + bare[:2])[:4]}


# ── worklists ────────────────────────────────────────────────────────────────
def fetch_all_books(sel: str, filt: str = "") -> list[dict]:
    out, off = [], 0
    q = f"{URL}/rest/v1/ebooks?select={sel}" + (f"&{filt}" if filt else "")
    while True:
        r = requests.get(q, headers={**H_GET, "Range": f"{off}-{off+999}"}, timeout=60)
        rows = r.json()
        out += rows
        if len(rows) < 1000:
            break
        off += 1000
    return out


def recover_worklist() -> list[str]:
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    return [a["id"] for a in audit
            if a["file_type"] == "pdf" and a["signals"]["no_toc_pct"] >= 0.6]


def run_audit():
    print("JOB B — auditing all has-TOC books (rules only)…", flush=True)
    books = [b for b in fetch_all_books("id,title,chunk_count") if (b.get("chunk_count") or 0) > 0]
    flagged = []
    for i, b in enumerate(books):
        try:
            res = audit_book(b["id"], b.get("title") or "")
        except Exception:
            res = None
        if res:
            flagged.append(res)
        if (i + 1) % 200 == 0:
            print(f"  audited {i+1}/{len(books)}, flagged {len(flagged)}", flush=True)
    flagged.sort(key=lambda x: x["filename_leaks"] + x["blockquote_titles"], reverse=True)
    L = [f"TOC AUDIT — {len(flagged)} books with suspect entries (of {len(books)})\n"]
    for f in flagged:
        L.append(f"[fn={f['filename_leaks']} bq={f['blockquote_titles']} bare={f['bare_ordinals']}] "
                 f"{f['title'][:46]}")
        L.append(f"    {f['id']} | e.g. {f['samples']}")
    AUDIT_FLAGS.write_text("\n".join(L), encoding="utf-8")
    print(f"✓ JOB B done: {len(flagged)} flagged -> {AUDIT_FLAGS}", flush=True)


def run_recover(limit: int = 0, dry_run: bool = False, ids: list[str] | None = None):
    led = load_ledger()
    work = ids or recover_worklist()
    work = [w for w in work if w not in led]
    if limit:
        work = work[:limit]
    print(f"JOB A — recover: {len(work)} books to process "
          f"({len(led)} already in ledger){' [DRY-RUN]' if dry_run else ''}", flush=True)
    for i, eid in enumerate(work):
        b = fetch_book(eid)
        title = (b.get("title") if b else "") or eid
        try:
            res = recover_book(eid, dry_run=dry_run)
        except Exception as e:
            res = {"status": "error", "note": str(e)[:120]}
        print(f"  [{i+1}/{len(work)}] {res['status']:14} {title[:38]} "
              f"{res.get('coverage','')} {res.get('note','')}", flush=True)
        if not dry_run:
            led[eid] = {"title": title, **res}
            save_ledger(led)
    print("✓ JOB A pass complete", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["all", "audit", "recover"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ids", default="")
    args = ap.parse_args()
    ids = [x for x in args.ids.split(",") if x] or None
    if args.mode in ("all", "audit"):
        run_audit()
    if args.mode in ("all", "recover"):
        run_recover(limit=args.limit, dry_run=args.dry_run, ids=ids)


if __name__ == "__main__":
    main()
