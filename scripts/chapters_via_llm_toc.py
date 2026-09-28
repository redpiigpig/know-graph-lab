#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""書籤不能用的一頁一塊 PDF：請模型讀書前幾頁、抽出印刷目錄，補章節再合併成一節一塊（2026-09-28）。

背景：assign_chapters_from_bookmarks.py 跑完，1,253 本書籤不能用（多為逐頁書籤）。agent 寫的
chapters_from_printed_toc.py 用規則解析目錄頁，抽樣成功率只有 15–18%（找不到目錄頁 32%、
英文跨行式目錄解不出 30%）。這支把「找目錄頁＋解析條目」交給模型（Gemini 先，額度用盡改 NVIDIA，
都不耗 Claude），後半段沿用 chapters_from_printed_toc 的定位與防呆：
  - 印刷頁碼→實體頁：先用 printed_page 錨點推算並驗證，沒有才在內文搜章名
  - 🚨 內文搜尋定位只收 ≥5 字的章名（《馬太亨利》「使徒行傳」這類泛用短名全配到引用處）
  - 單調性、至少 3 條、落點不重複 ≥50%、覆蓋 ≥50% 頁
留 .jsonl.bak_chapters；報告 output/toc_audit/llm_toc_chapters.tsv。
  python -X utf8 scripts/chapters_via_llm_toc.py [--ids ...] [--limit N] [--apply]
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consolidate_page_chunks as cp  # noqa: E402
import chapters_from_printed_toc as cpt  # noqa: E402
import toc_from_toc_pages as tp  # noqa: E402
import translate_ebook_to_zh as te  # noqa: E402
import standardize_ebook as se  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
MIN_SEARCH_TITLE = 5

PROMPT = """下面是一本書最前面幾頁的文字，每頁開頭標了〔PDF頁 N〕。
請找出其中的「目錄／目次／Contents」，把目錄條目逐條列出成 JSON 陣列：
[{"title": "章名（照目錄原文，不要翻譯、不要改寫）", "level": 1 或 2（篇／部＝1、章＝1、節＝2）, "printed_page": 目錄上印的頁碼（整數）}]
規則：只收目錄上**有頁碼**的條目；照目錄順序；羅馬數字頁碼（前言 i、ii）的條目略過；不要自己編造。
找不到目錄就回 []。只輸出 JSON，不要任何說明。

{text}"""


def front_text(pages: list[dict], max_chars: int = 30_000) -> str:
    n = max(15, int(len(pages) * 0.08))
    parts, used = [], 0
    for c in pages[:n]:
        body = (c.get("content") or "")[:2500]
        piece = f"〔PDF頁 {c['page_number']}〕\n{body}\n"
        if used + len(piece) > max_chars:
            break
        parts.append(piece)
        used += len(piece)
    return "".join(parts)


def parse_entries(raw: str) -> list[dict]:
    """模型輸出 → [{title, printed_page, level}]；抓第一個 JSON 陣列，欄位不合就丟。純函式。"""
    m = re.search(r"\[.*\]", raw or "", re.S)
    if not m:
        return []
    try:
        arr = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    out = []
    for e in arr if isinstance(arr, list) else []:
        if not isinstance(e, dict):
            continue
        t = str(e.get("title") or "").strip()
        try:
            pg = int(e.get("printed_page"))
        except (TypeError, ValueError):
            continue
        lv = e.get("level") if e.get("level") in (1, 2) else 1
        if t and 0 < pg < 5000:
            out.append({"title": t, "printed_page": pg, "level": lv})
    return out


_gem_dead_until = 0.0


def ask_model(prompt: str) -> tuple[str, str]:
    """Gemini 輪一圈金鑰；全部 429 就記下冷卻 30 分鐘、改 NVIDIA。回傳 (文字, 引擎)。"""
    global _gem_dead_until
    if time.time() > _gem_dead_until and te.GEMINI_KEYS:
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}}
        base = f"https://generativelanguage.googleapis.com/v1beta/models/{te.GEMINI_MODEL}:generateContent"
        for key in te.GEMINI_KEYS:
            try:
                r = requests.post(f"{base}?key={key}", json=body, timeout=90)
            except requests.RequestException:
                continue
            if r.status_code == 200:
                try:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"], "gemini"
                except (KeyError, IndexError):
                    continue
        _gem_dead_until = time.time() + 1800
    try:
        return te.nvidia_chat(prompt, max_tokens=6000, temperature=0.1, thinking=False), "nvidia"
    except Exception as e:  # noqa: BLE001
        return "", f"engine-failed {type(e).__name__}"


def process(bid: str, chunks: list[dict]) -> tuple[str, list[dict] | None]:
    pages = [c for c in chunks if c.get("chunk_type") == "page" and isinstance(c.get("page_number"), int)]
    if len(pages) < 10:
        return "too-short", None
    raw, eng = ask_model(PROMPT.replace("{text}", front_text(pages)))
    entries = parse_entries(raw)
    if len(entries) < 3:
        return f"too-few-entries {len(entries)} ({eng})", None
    by_page = {c["page_number"]: c for c in pages}
    # 目錄頁＝書前幾頁裡含 ≥3 個條目章名的頁
    front = pages[:max(15, int(len(pages) * 0.08))]
    toc_pages = {c["page_number"] for c in front
                 if sum(1 for e in entries if e["title"][:8] in (c.get("content") or "")) >= 3}
    anchors = [(c["page_number"], c["printed_page"]) for c in pages if c.get("printed_page")]
    resolved, _dropped = cpt.resolve_entries(entries, anchors, by_page, toc_pages)
    resolved = [e for e in resolved
                if not (e.get("how") == "content-search" and len(re.sub(r"\s", "", e["title"])) < MIN_SEARCH_TITLE)]
    resolved = sorted(resolved, key=lambda e: e["pdf_page"])
    resolved, _ = cpt.enforce_monotonic(resolved)
    if len(resolved) < 3:
        return f"too-few-resolved {len(resolved)} ({eng})", None
    uniq = len({e["pdf_page"] for e in resolved})
    if uniq / len(resolved) < 0.5:
        return f"duplicate-anchors {uniq}/{len(resolved)}", None
    work = [dict(c) for c in chunks]
    tp.assign(work, resolved, sorted(toc_pages))
    wp = [c for c in work if c.get("chunk_type") == "page"]
    covered = sum(1 for c in wp if c.get("chapter_path") and c["chapter_path"] != "目次")
    if covered < 0.5 * len(wp):
        return f"low-coverage {covered}/{len(wp)}", None
    if not se.book_is_japanese(c.get("content") or "" for c in chunks):
        for c in work:
            if c.get("chapter_path"):
                c["chapter_path"] = se.to_traditional(c["chapter_path"])
    merged = cp.consolidate(work)
    anch = sum(1 for e in resolved if e.get("how") == "anchor")
    return f"merged {len(chunks)}->{len(merged)} ({len(resolved)} 章，錨點 {anch}，{eng})", merged


def main() -> int:
    apply = "--apply" in sys.argv
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    if "--ids" in sys.argv:
        ids = [a for a in sys.argv[sys.argv.index("--ids") + 1:] if not a.startswith("--")]
    else:
        rep = ROOT / "output/toc_audit/bookmark_chapters.tsv"
        ids = [l.split("\t")[0] for l in rep.read_text(encoding="utf-8").splitlines()
               if l.strip() and not l.split("\t")[1].startswith("merged")]
    if limit:
        ids = ids[:limit]
    out = open(ROOT / "output/toc_audit/llm_toc_chapters.tsv", "a", encoding="utf-8")
    stat: dict[str, int] = {}
    for n, bid in enumerate(ids):
        p = CH / f"{bid}.jsonl"
        try:
            chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception:  # noqa: BLE001
            continue
        if cp.eligible(chunks) != "no-chapters":
            continue
        res, merged = process(bid, chunks)
        if merged is not None and apply:
            bak = p.with_suffix(".jsonl.bak_chapters")
            if not bak.exists():
                shutil.copy2(p, bak)
            o = se.write_jsonl(bid, merged)
            try:
                se.push_to_r2(bid, o)
                se.update_db(bid, merged)
            except Exception as e:  # noqa: BLE001
                res += f" sync-failed {type(e).__name__}"
        k = res.split(" ")[0]
        stat[k] = stat.get(k, 0) + 1
        out.write(f"{bid}\t{res}\n")
        out.flush()
        if n % 25 == 0:
            print(n, len(ids), stat, flush=True)
    print("SUMMARY", stat, flush=True)
    print("LLM_TOC_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
