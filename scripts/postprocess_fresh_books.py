#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新書後處理（2026-10-01 使用者：「以後新書的 OCR 也要按這個規則——分頁、章節勘定、分段、註腳」）。

每日 run_ocr_daily.bat 在「標準化」之後跑這支：最近 N 天新解析、還沒重建過（沒有 .bak_restructure）的書，
依序走 2026-09-28～10-01 全館整理用的同一套工具，每一步獨立子行程、限時 15 分鐘，一步出錯就停在那本、記下來換下一本：
  PDF：backfill_printed_pages（印刷頁碼）→ assign_chapters_from_bookmarks（書籤章節）
       → chapters_via_llm_toc（書籤不可用才做；讀目錄頁，走 Gemini→NVIDIA）→ consolidate_page_chunks（逐頁併一節一塊）
       → reflow_pdf_paragraphs（只對整頁接成一段的）
  全部：restructure_chapters（一章一頁、每頁約五千字、段號、卷首引言、EPUB 插圖）→ relink_missing_footnotes（只用規則）
各工具自己的安全閘照舊有效：章節不可靠的書會被 restructure 擋下（記在 log），不會硬切。

  python -X utf8 scripts/postprocess_fresh_books.py [--days 3] [--limit 40] [--ids id ...]
log：scripts/logs/postprocess_YYYY-MM-DD.log；處理過的記 scripts/state/postprocess_done.txt（不重做）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
DONE = ROOT / "scripts" / "state" / "postprocess_done.txt"
LOG = ROOT / "scripts" / "logs" / f"postprocess_{dt.date.today()}.log"
TIMEOUT = 900


def log(msg: str) -> None:
    line = dt.datetime.now().strftime("%H:%M ") + msg
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def step(name: str, args: list[str]) -> bool:
    try:
        r = subprocess.run([sys.executable, "-X", "utf8", *args], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        log(f"    {name}：逾時 {TIMEOUT // 60} 分鐘")
        return False
    tail = (r.stdout or "").strip().splitlines()[-1:] or (r.stderr or "").strip().splitlines()[-1:]
    log(f"    {name} rc={r.returncode} {tail[0][:140] if tail else ''}")
    return r.returncode == 0


def load(bid: str) -> list[dict]:
    p = CH / f"{bid}.jsonl"
    return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()] if p.exists() else []


def n_chapters(cs: list[dict]) -> int:
    return len({(c.get("chapter_path") or "").split(" / ")[0] for c in cs if (c.get("chapter_path") or "").strip()})


def unsplit(cs: list[dict]) -> bool:
    lens = [len(p) for c in cs for p in (c.get("content") or "").split("\n\n") if p.strip()]
    return bool(lens) and statistics.median(lens) > 2500


def fresh_ids(days: int) -> list[dict]:
    import requests
    import translate_ebook_to_zh as te
    H = {"apikey": te.KEY, "Authorization": "Bearer " + te.KEY}
    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).isoformat()
    out, off = [], 0
    while True:                      # 🚨 PostgREST 不帶 limit 會靜默截在 1000
        b = requests.get(te.URL + "/rest/v1/ebooks", headers=H, timeout=120, params={
            "select": "id,title,file_type,collection,parsed_at", "parsed_at": f"gte.{since}",
            "order": "parsed_at", "limit": "1000", "offset": str(off)}).json()
        out += b
        if len(b) < 1000:
            return out
        off += 1000


def process(m: dict) -> None:
    bid = m["id"]
    cs = load(bid)
    if not cs:
        log(f"  {bid[:8]} 沒有全文檔，略過")
        return
    if any(c.get("source_text") or c.get("sources") for c in cs):
        log(f"  {bid[:8]} 有對照欄，略過（走 rebuild_reference_bilingual／number_multilingual）")
        return
    log(f"▶ {bid[:8]} {(m.get('title') or '')[:30]}（{m.get('file_type')}，{len(cs)} 塊，{n_chapters(cs)} 章）")
    ids_file = ROOT / "output" / "restructure" / "_postprocess_one.txt"
    ids_file.parent.mkdir(parents=True, exist_ok=True)
    ids_file.write_text(bid + "\n", encoding="utf-8")
    if m.get("file_type") == "pdf":
        ok = step("印刷頁碼", ["scripts/backfill_printed_pages.py", "--apply", "--ids", bid])
        ok = ok and step("書籤章節", ["scripts/assign_chapters_from_bookmarks.py", "--apply", "--ids", bid])
        if ok and n_chapters(load(bid)) < 2:
            ok = step("讀目錄頁補章節", ["scripts/chapters_via_llm_toc.py", "--apply", "--ids", bid])
        ok = ok and step("合併逐頁塊", ["scripts/consolidate_page_chunks.py", "--apply", "--ids", bid])
        if ok and unsplit(load(bid)):
            ok = step("重抽段落", ["scripts/reflow_pdf_paragraphs.py", "--apply", "--ids", str(ids_file)])
        if not ok:
            log("    前段失敗，這本先停在這裡")
            return
    args = ["scripts/restructure_chapters.py", "--apply", "--new-only", "--ids", str(ids_file)]
    if m.get("collection") == "collected-works":
        args.insert(2, "--collected")
    step("一章一頁＋分頁＋段號", args)
    step("補註腳（規則）", ["scripts/relink_missing_footnotes.py", "--apply", "--ids", bid])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--ids", nargs="*")
    a = ap.parse_args()
    if not CH.exists():
        log("G: 不在（Drive 卡住？見 CLAUDE.md），今天不跑")
        return 0
    LOG.parent.mkdir(parents=True, exist_ok=True)
    DONE.parent.mkdir(parents=True, exist_ok=True)
    done = set(DONE.read_text(encoding="utf-8").split()) if DONE.exists() else set()
    books = [{"id": i} for i in a.ids] if a.ids else fresh_ids(a.days)
    if a.ids:
        import audit_toc_accuracy as at
        meta = at.load_meta()
        books = [dict(meta.get(b["id"], {}), id=b["id"]) for b in books]
    todo = [m for m in books if m["id"] not in done
            and not (CH / f"{m['id']}.jsonl.bak_restructure").exists()][:a.limit]
    log(f"新書後處理：近 {a.days} 天解析 {len(books)} 本，待處理 {len(todo)} 本")
    for m in todo:
        try:
            process(m)
        except Exception as e:  # noqa: BLE001
            log(f"  {m['id'][:8]} 錯誤 {type(e).__name__}: {str(e)[:120]}")
        with DONE.open("a", encoding="utf-8") as f:
            f.write(m["id"] + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
