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

PROMPT = """以下是《古代基督信仰聖經註釋叢書》（Ancient Christian Commentary on Scripture，校園書房繁體中文版）**連續的一至數頁**掃描影像，內容是某卷聖經某段經文的教父註釋。請依影像順序處理，把所有頁的條目**合併成單一 JSON 陣列**輸出（跨頁未完的同一則正文要接成完整一段）。

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


def ocr_batch_claude(pngs: list[bytes], model: str = "haiku") -> list[dict]:
    """OCR N 頁 → 合併結構化 entries，經 claude CLI（Max OAuth，無 API key）。
    model: 'haiku'（快、品質普通）或 'sonnet'（慢、掃描中文精度高）。多圖一次呼叫。"""
    content = []
    for png in pngs:
        b64 = base64.standard_b64encode(png).decode()
        content.append({"type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": b64}})
    content.append({"type": "text", "text": PROMPT})
    msg = {"type": "user", "message": {"role": "user", "content": content}}
    cmd = [
        CLAUDE_BIN, "-p", "--model", model, "--verbose",
        "--disable-slash-commands", "--allowedTools", "",
        "--input-format", "stream-json", "--output-format", "stream-json",
    ]
    cwd = r"c:\tmp" if sys.platform == "win32" else "/tmp"
    # Popen + communicate(timeout)；逾時時用 taskkill /T 連孫（claude.cmd→node）一起殺，
    # 否則 subprocess.run 的 timeout 只殺直系子、孫占住 pipe → communicate 卡死整輪 wedge。
    # ⚠️ 絕對別加 CREATE_NEW_PROCESS_GROUP：該 flag 會讓 claude.cmd→node 的 console/stdin
    #    行為改變、即使 Max 額度「allowed」也卡到 300s 逾時（2026-06-15 整夜空跑的真因）。
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding="utf-8", cwd=cwd)
    try:
        out, err = proc.communicate(input=json.dumps(msg) + "\n", timeout=300)
    except subprocess.TimeoutExpired:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           capture_output=True)
        else:
            proc.kill()
        try:
            proc.communicate(timeout=10)
        except Exception:
            pass
        raise RuntimeError(f"{model} OCR 逾時（額度疑乾），依規範退出")
    if proc.returncode != 0:
        blob = (err or "") + (out or "")
        if "rate_limit" in blob:
            raise RuntimeError(f"{model} rate limited，依規範退出")
        # 🚨 任何非零退出都是「本頁失敗」，一律 raise（→ 留在 checkpoint 外、下輪重試）。
        # 絕不可 return []：rate-limit/錯誤訊息格式不一定含 'rate_limit'，吞成空頁會讓整章
        # 漏掉又假 .done（2026-07-03 申命記 26-32 章 26 頁被誤記空頁的根因）。
        raise RuntimeError(f"{model} exit {proc.returncode}: {(err or out or '')[:160]}")
    final = None
    for line in (out or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "result" and evt.get("subtype") == "success":
            final = evt.get("result", "")
    if final is None:
        # 沒拿到 success result event＝回應被截斷/出錯，不是「空頁」→ raise 重試，別記空。
        raise RuntimeError(f"{model} 無 success result event（回應截斷/出錯），依規範退出")
    return _coerce_json_array(final) if final else []


_CLIENTS: dict = {}        # api_key → genai.Client（快取，避免 client-closed bug）
_DEAD_KEYS: set = set()    # **只放 credit/額度永久乾**的 key（如 prepayment depleted）
_KEY_IDX = [0]             # round-robin 指標，讓負載平均分散到各 key（避單 key 撞 RPM）


def _client(key: str):
    if key not in _CLIENTS:
        _CLIENTS[key] = genai.Client(api_key=key)
    return _CLIENTS[key]


def _gemini_generate(contents: list) -> list[dict]:
    """送 contents（影像 Part… + PROMPT）給 Gemini，回傳解析後 entries。
    key round-robin；RPM/暫時性 429 退避重試（**不**標死）；只有 credit 永久乾的
    key 才永久剔除；全部永久乾才退出。"""
    n = len(API_KEYS)
    attempts = 0
    max_attempts = n * 4
    while attempts < max_attempts:
        live = [k for k in API_KEYS if k not in _DEAD_KEYS]
        if not live:
            raise RuntimeError("全部 Gemini key credit 永久乾，依規範退出")
        key = live[_KEY_IDX[0] % len(live)]
        _KEY_IDX[0] += 1
        try:
            resp = _client(key).models.generate_content(
                model=MODEL, contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            txt = (resp.text or "").strip()
            return json.loads(txt) if txt else []
        except Exception as e:
            msg = str(e).lower()
            if isinstance(e, json.JSONDecodeError):
                print(f"    [JSON parse fail, skip] {str(e)[:80]}", file=sys.stderr)
                return []
            if "depleted" in msg or "prepayment" in msg or "billing" in msg:
                _DEAD_KEYS.add(key); continue          # 餘額用罄 → 永久剔除
            if "429" in msg or "resource_exhausted" in msg or "quota" in msg or "rate" in msg \
               or "503" in msg or "unavailable" in msg:
                attempts += 1
                time.sleep(min(5 * attempts, 30))      # RPM/暫時性 → 退避換下一把
                continue
            raise
    raise RuntimeError("連續 429 達上限（可能當日額度耗盡），依規範退出")


def ocr_page(png: bytes) -> list[dict]:
    """單頁結構化 OCR（Gemini）。"""
    return _gemini_generate([types.Part.from_bytes(data=png, mime_type="image/png"), PROMPT])


def ocr_batch_gemini(pngs: list[bytes]) -> list[dict]:
    """多頁一次呼叫（省額度）：N 張影像 + PROMPT → 合併 entries。
    每條 entry 自帶 ref，故跨頁順序交給 build_rows_auto 依 ref 還原。"""
    parts = [types.Part.from_bytes(data=p, mime_type="image/png") for p in pngs]
    return _gemini_generate(parts + [PROMPT])


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
    ap.add_argument("--engine", choices=["gemini", "haiku", "sonnet"], default="gemini",
                    help="OCR 引擎：gemini（每日額度限制）/ haiku（Max，快但掃描中文易錯）/ "
                         "sonnet（Max，慢但掃描中文精度高）")
    ap.add_argument("--replace", action="store_true",
                    help="入庫前先刪該書既有 accs_commentary 列（含示範 placeholder）")
    ap.add_argument("--resume", action="store_true",
                    help="沿用 c:/tmp 的 per-page checkpoint，跳過已 OCR 的頁")
    ap.add_argument("--sleep", type=float, default=1.5)
    ap.add_argument("--batch", type=int, default=4,
                    help="Gemini 每次呼叫處理幾頁（省額度；haiku 強制 1）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    batch_size = max(1, args.batch)

    # Per-page checkpoint on disk → long runs survive a crash; --resume skips done pages.
    # 記錄相容兩種形狀：{"page":p,...}（舊單頁）與 {"pages":[...],...}（批次）。
    ckpt = Path(r"c:/tmp" if sys.platform == "win32" else "/tmp") / f"accs_{args.book}_{Path(args.pdf).stem}.raw.jsonl"

    def _rec_pages(rec: dict) -> list[int]:
        return rec.get("pages") or ([rec["page"]] if "page" in rec else [])

    done_pages: set[int] = set()
    if args.resume and ckpt.exists():
        for ln in ckpt.read_text(encoding="utf-8").splitlines():
            try:
                done_pages.update(_rec_pages(json.loads(ln)))
            except Exception:
                pass
        print(f"  [resume] {len(done_pages)} pages already in {ckpt.name}", flush=True)

    pdf = fitz.open(args.pdf)
    pages = [p for p in parse_pages(args.pages) if (p - 1) < pdf.page_count]
    todo = [p for p in pages if p not in done_pages]
    print(f"== ACCS OCR [{args.engine}] x{batch_size}p ==  {args.book} "
          f"ch{args.chapter if args.chapter else 'AUTO'}  {len(todo)}/{len(pages)} pages to do",
          flush=True)

    ckpt_fh = ckpt.open("a", encoding="utf-8")
    consec_exit = 0   # 連續「依規範退出」（逾時/rate-limit）計數；真乾才會連幾次
    for bi in range(0, len(todo), batch_size):
        chunk = todo[bi:bi + batch_size]
        print(f"  [{bi + 1}-{bi + len(chunk)}/{len(todo)}] pages {chunk[0]}-{chunk[-1]} ... ",
              end="", flush=True)
        try:
            pngs = [render_page(pdf, p - 1) for p in chunk]
            if args.engine == "gemini":
                entries = ocr_batch_gemini(pngs)
            else:
                entries = ocr_batch_claude(pngs, model=args.engine)
            print(f"{len(entries)} entries", flush=True)
            consec_exit = 0   # 成功一頁就歸零
            if not args.dry_run:   # dry-run 不污染 checkpoint
                ckpt_fh.write(json.dumps({"pages": chunk, "entries": entries}, ensure_ascii=False) + "\n")
                ckpt_fh.flush()
        except Exception as e:
            print(f"FAIL {e}", flush=True)
            if "依規範退出" in str(e):
                # 單頁逾時多半是 CLI 偶發卡頓（batch 1 時更明顯）：跳過該頁、續跑，
                # 該頁留在 checkpoint 之外、下輪自動重試。只有**連續 3 次**才視為真的額度乾→退。
                consec_exit += 1
                if consec_exit >= 3:
                    print("  [bail] 連續 3 次逾時/rate-limit → 視為額度乾，依規範退出", flush=True)
                    break
        time.sleep(args.sleep)
    ckpt_fh.close()
    pdf.close()

    # Rebuild full raw list from checkpoint in document (page) order, so
    # build_rows_auto sees entries in source order → correct per-chapter pericope_order.
    recs: list[tuple[int, list[dict]]] = []
    for ln in ckpt.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(ln)
            pgs = _rec_pages(rec)
            if pgs:
                recs.append((min(pgs), rec.get("entries", [])))
        except Exception:
            pass
    recs.sort(key=lambda t: t[0])
    raw: list[dict] = []
    for _, entries in recs:
        raw.extend(entries)

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

    if not rows:
        print("  [skip] 本次無任何 rows（額度乾/全空）→ 不刪不寫，保留既有資料", flush=True)
        return
    if args.replace:
        delete_book_rows(args.book)   # 只在確實有 rows 時才整批換，避免空結果清空
    upsert_rows(rows)
    print(f"upserted {len(rows)} rows into accs_commentary", flush=True)

    # 完成標記：本書目標頁全數已在 checkpoint → 寫 .done，讓每日排程不再重跑/覆蓋
    covered: set[int] = set()
    for ln in ckpt.read_text(encoding="utf-8").splitlines():
        try:
            covered.update(_rec_pages(json.loads(ln)))
        except Exception:
            pass
    if set(pages) and set(pages).issubset(covered):
        done_marker = ckpt.with_suffix(".done")
        done_marker.write_text(f"{len(covered)} pages\n", encoding="utf-8")
        print(f"  [done] all {len(set(pages))} target pages OCR'd → {done_marker.name}", flush=True)


if __name__ == "__main__":
    main()
