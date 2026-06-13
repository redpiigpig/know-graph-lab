"""Ingest ACCS (古代基督信仰聖經註釋叢書) patristic commentary for a Bible book
into the accs_commentary table, by structured-OCR of the 校園 Chinese-version
scanned PDF.

Pipeline (per page range):
  1. PyMuPDF render each page → PNG (≤2000px, see [[feedback_screenshot_2000px]]).
  2. Gemini 2.5 Flash structured output → JSON array of raw entries
     {ref, kind, heading, father, father_en, work, body} following the ACCS
     catena layout (經文段落 → 總論 overview → 教父引文 comments w/ attribution).
  3. accs_commentary.build_rows() orders them into DB rows (pericope/entry order,
     father-name normalisation).
  4. Idempotent upsert into accs_commentary (on the UNIQUE key).

Engine policy: Gemini-first (vision), 2-strike 429 退出（[[feedback_ocr_two_strike_quota]]）.

Usage:
  python scripts/ingest_accs_genesis.py --pdf c:/tmp/accs_gen_1-11.pdf \
      --book gen --chapter 1 --pages 30-44 \
      --source-vol "ACCS OT I（創 1–11）" [--dry-run]

`--pages` 是 PDF 實體頁碼範圍（人工先翻 PDF 找該章對應頁）。一次跑一章，OCR 後
spot-check 再跑下一章。
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().lstrip("﻿"); v = v.strip().strip("'\"")
        if k and k not in os.environ:
            os.environ[k] = v

sys.path.insert(0, str(ROOT / "scripts"))
from accs_commentary import build_rows, build_rows_auto  # noqa: E402
from ocr_with_gemini import _find_gemini_keys  # noqa: E402

try:
    import json_repair as _json_repair
    HAS_JSON_REPAIR = True
except ImportError:
    HAS_JSON_REPAIR = False

try:
    import fitz
except ImportError:
    print("pip install pymupdf", file=sys.stderr); sys.exit(1)
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("pip install google-genai", file=sys.stderr); sys.exit(1)
import requests

API_KEYS = _find_gemini_keys()
if not API_KEYS:
    print("ERR: 無 GEMINI_API_KEY", file=sys.stderr); sys.exit(1)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
MODEL = "gemini-2.5-flash"

PROMPT = """這是《古代基督信仰聖經註釋叢書》（Ancient Christian Commentary on Scripture，校園書房繁體中文版）一頁掃描影像，內容是某卷聖經某段經文的教父註釋。

本叢書體例（catena）每個經文段落的版式：
①**經文引用標題**（如「1:1-2」「1:14-19」，常為粗體置中／置左）
②可選的**總論**（編者導語，整段斜體或縮排，概述該段教父觀點，無作者署名）
③若干則**教父引文**；每則的版式為：**粗體主題小標**（如「聖靈所造」「洗禮的象徵」）→ 正文 → 段末以破折號標註**教父名 + 作品名**（如「— 巴西流《創世六日講道集》」，有時帶上標頁碼）。

請把這頁逐則抽成結構化 JSON 陣列，每元素一則：
- `ref`：該則所屬經文段落引用，章節格式 "1:1-2" / "1:14"。沿用本頁或前文最近出現的段落標題；同段落多則共用同一 ref。
- `kind`："overview"（總論）或 "comment"（具名教父引文）。
- `heading`：該則正上方的**粗體主題小標**，逐字照抄繁中（總論若有標題也填；真的沒有才空字串）。**務必盡力辨識小標，不要遺漏。**
- `father`：教父名（繁中；overview 留空）。
- `father_en`：教父英文名（頁面有或你確定才填，否則空字串）。
- `work`：作品名（繁中，去書名號；無則空字串）。
- `body`：該則正文（繁中）。

**辨識準則（品質最重要）**：
1. **逐字精確辨識**，這是繁體中文掃描印刷品：勿漏字、勿吞字、勿改字、勿自行摘要或改寫；不確定的字寧可依上下文判讀正確字，**絕不臆造**。輸出**一律繁體**（簡體一律轉繁體）。
2. **正確斷句**：保留原標點；接回因換行斷開的句子（去掉行尾連字），但不要把兩句併成一句、也不要硬切一句。
3. **一則引文 = 一個 entry**：不同小標或不同教父署名 → 拆成不同 entry，**絕不合併**；同一則跨欄／跨行的正文要合成完整一段。
4. 只抽**教父註釋與總論**；跳過頁首 running header、頁碼、以及整段**重述聖經經文**的區塊（經文另有來源，不要當 comment）。
5. **整頁是前言／序／導論／目錄／讚譽／空白頁 → 回傳空陣列 []**（這些不是逐節註釋）。
6. 跨頁未完的段落：照本頁所見輸出，body 不要臆測補全。
7. **只回傳 JSON 陣列**，不要 markdown 圍欄、不要任何說明文字。
"""

RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "ref": {"type": "string"},
            "kind": {"type": "string"},
            "heading": {"type": "string"},
            "father": {"type": "string"},
            "father_en": {"type": "string"},
            "work": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["ref", "kind", "body"],
    },
}


def render_page(pdf: "fitz.Document", page_idx: int, max_dim: int = 1800) -> bytes:
    page = pdf.load_page(page_idx)
    rect = page.rect
    zoom = max_dim / max(rect.width, rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return pix.tobytes("png")


# ── Haiku Vision via Max-session OAuth (claude CLI, no API key) ──────────────
def _resolve_claude_bin() -> str:
    if sys.platform == "win32":
        cand = os.path.expandvars(r"%APPDATA%\npm\claude.cmd")
        if os.path.exists(cand):
            return cand
    return "claude"


CLAUDE_BIN = _resolve_claude_bin()


def _coerce_json_array(text: str) -> list[dict]:
    text = text.strip()
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text).strip()
    try:
        out = json.loads(text)
    except json.JSONDecodeError:
        if HAS_JSON_REPAIR:
            try:
                out = _json_repair.loads(text)
            except Exception:
                return []
        else:
            return []
    return out if isinstance(out, list) else []


def ocr_page_haiku(png: bytes) -> list[dict]:
    """OCR one page → structured entries via Haiku Vision (claude CLI, Max OAuth)."""
    b64 = base64.standard_b64encode(png).decode()
    msg = {
        "type": "user",
        "message": {"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
            {"type": "text", "text": PROMPT},
        ]},
    }
    cmd = [
        CLAUDE_BIN, "-p", "--model", "haiku", "--verbose",
        "--disable-slash-commands", "--allowedTools", "",
        "--input-format", "stream-json", "--output-format", "stream-json",
    ]
    cwd = r"c:\tmp" if sys.platform == "win32" else "/tmp"
    try:
        proc = subprocess.run(cmd, input=json.dumps(msg) + "\n", capture_output=True,
                              text=True, encoding="utf-8", timeout=600, cwd=cwd)
    except subprocess.TimeoutExpired:
        print("    [Haiku timeout]", file=sys.stderr); return []
    if proc.returncode != 0:
        blob = (proc.stderr or "") + (proc.stdout or "")
        if "rate_limit" in blob:
            raise RuntimeError("Haiku rate limited，依規範退出")
        print(f"    [Haiku exit {proc.returncode}] {(proc.stderr or '')[:160]}", file=sys.stderr)
        return []
    final = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "result" and evt.get("subtype") == "success":
            final = evt.get("result", "")
    if not final:
        return []
    return _coerce_json_array(final)


_CLIENTS: dict = {}        # api_key → genai.Client（快取，避免 client-closed bug）
_DEAD_KEYS: set = set()    # 本輪已 429/額度乾的 key，後續頁不再重試


def _client(key: str):
    if key not in _CLIENTS:
        _CLIENTS[key] = genai.Client(api_key=key)
    return _CLIENTS[key]


def ocr_page(png: bytes) -> list[dict]:
    last_err = None
    live = [k for k in API_KEYS if k not in _DEAD_KEYS]
    if not live:
        raise RuntimeError("全部 Gemini key 額度已乾，依規範退出")
    for key in live:
        try:
            resp = _client(key).models.generate_content(
                model=MODEL,
                contents=[types.Part.from_bytes(data=png, mime_type="image/png"), PROMPT],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            txt = (resp.text or "").strip()
            if not txt:
                return []
            return json.loads(txt)
        except Exception as e:
            msg = str(e); last_err = e
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower() or "depleted" in msg.lower():
                _DEAD_KEYS.add(key)   # 整輪標死，不再重試此 key
                continue
            if "503" in msg or "UNAVAILABLE" in msg:
                time.sleep(3); continue
            if isinstance(e, json.JSONDecodeError):
                print(f"    [JSON parse fail, skip page] {msg[:80]}", file=sys.stderr)
                return []
            raise
    # 所有 live key 這頁都掛了 → 若全死則退出，否則視為暫時性（重試下一頁）
    if not [k for k in API_KEYS if k not in _DEAD_KEYS]:
        raise RuntimeError("全部 Gemini key 額度已乾，依規範退出")
    return []


def parse_pages(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-", 1); out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def upsert_rows(rows: list[dict]) -> None:
    if not rows:
        return
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    url = (f"{SUPABASE_URL}/rest/v1/accs_commentary"
           "?on_conflict=book_code,chapter,verse_start,verse_end,entry_order")
    r = requests.post(url, headers=h, json=rows, timeout=60)
    if r.status_code not in (200, 201, 204):
        print(f"  upsert {r.status_code}: {r.text[:400]}", file=sys.stderr)
        r.raise_for_status()


def delete_book_rows(book: str, demo_only: bool = False) -> None:
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/accs_commentary?book_code=eq.{book}"
    if demo_only:
        url += "&source_vol=like.（公有領域示範*"
    r = requests.delete(url, headers=h, timeout=30)
    print(f"  delete {'demo ' if demo_only else ''}rows ({book}): {r.status_code}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--book", required=True, help="bible_books.code, e.g. gen")
    ap.add_argument("--chapter", type=int, default=None,
                    help="固定章號；省略=整本 PDF 模式，章號由每則 ref 自動推（build_rows_auto）")
    ap.add_argument("--pages", required=True, help="PDF 實體頁範圍 e.g. 30-44 或 1-316")
    ap.add_argument("--source-vol", required=True)
    ap.add_argument("--engine", choices=["gemini", "haiku"], default="gemini",
                    help="OCR 引擎；Gemini 配額乾時用 haiku（Max OAuth，明確下令才開）")
    ap.add_argument("--replace", action="store_true",
                    help="入庫前先刪該書既有 accs_commentary 列（含示範 placeholder）")
    ap.add_argument("--resume", action="store_true",
                    help="沿用 c:/tmp 的 per-page checkpoint，跳過已 OCR 的頁")
    ap.add_argument("--sleep", type=float, default=1.5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ocr_fn = ocr_page_haiku if args.engine == "haiku" else ocr_page

    # Per-page checkpoint on disk → long runs survive a crash; --resume skips done pages.
    ckpt = Path(r"c:/tmp" if sys.platform == "win32" else "/tmp") / f"accs_{args.book}_{Path(args.pdf).stem}.raw.jsonl"
    done_pages: set[int] = set()
    if args.resume and ckpt.exists():
        for ln in ckpt.read_text(encoding="utf-8").splitlines():
            try:
                done_pages.add(json.loads(ln)["page"])
            except Exception:
                pass
        print(f"  [resume] {len(done_pages)} pages already in {ckpt.name}", flush=True)

    pdf = fitz.open(args.pdf)
    pages = parse_pages(args.pages)
    print(f"== ACCS OCR [{args.engine}] ==  {args.book} "
          f"ch{args.chapter if args.chapter else 'AUTO'}  pages {pages[0]}-{pages[-1]} ({len(pages)})",
          flush=True)

    ckpt_fh = ckpt.open("a", encoding="utf-8")
    for i, p in enumerate(pages, 1):
        idx = p - 1
        if idx >= pdf.page_count:
            print(f"  page {p}: out of range"); continue
        if p in done_pages:
            continue
        print(f"  [{i}/{len(pages)}] page {p} ... ", end="", flush=True)
        try:
            entries = ocr_fn(render_page(pdf, idx))
            print(f"{len(entries)} entries", flush=True)
            ckpt_fh.write(json.dumps({"page": p, "entries": entries}, ensure_ascii=False) + "\n")
            ckpt_fh.flush()
        except Exception as e:
            print(f"FAIL {e}", flush=True)
            if "依規範退出" in str(e):
                break
        time.sleep(args.sleep)
    ckpt_fh.close()
    pdf.close()

    # Rebuild full raw list from checkpoint in page order (so build_rows_auto sees
    # entries in document order → correct per-chapter pericope_order).
    by_page: dict[int, list[dict]] = {}
    for ln in ckpt.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(ln); by_page[rec["page"]] = rec["entries"]
        except Exception:
            pass
    raw: list[dict] = []
    for p in sorted(by_page):
        raw.extend(by_page[p])

    if args.chapter:
        rows = build_rows(args.book, args.chapter, raw, args.source_vol)
    else:
        rows = build_rows_auto(args.book, raw, args.source_vol)
    chapters = sorted(set(r["chapter"] for r in rows))
    print(f"\n→ {len(raw)} raw entries → {len(rows)} rows · chapters {chapters} · "
          f"{len(set((r['chapter'], r['verse_start'], r['verse_end']) for r in rows))} pericopes",
          flush=True)

    if args.dry_run:
        for r in rows[:14]:
            who = r["father_name"] or "（總論）"
            print(f"  {r['chapter']}:{r['verse_start']}-{r['verse_end']} [{r['section_kind']}] "
                  f"{who} «{(r['work_title'] or '')}»  {len(r['body_zh'])}字")
        return

    if args.replace:
        delete_book_rows(args.book)
    upsert_rows(rows)
    print(f"upserted {len(rows)} rows into accs_commentary", flush=True)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
