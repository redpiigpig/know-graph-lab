#!/usr/bin/env python3
"""Repair 教父著作「標題吞內文」排版缺陷 — a heading line (## / ### / ####)
that merged a short section TITLE with the following body paragraph into one
line, so the reader renders a 900-char paragraph as a giant centered heading.

Root cause: the chunk-level translation occasionally dropped the blank line
between `## Heading` and its body, gluing them. The English source_text keeps
them as separate blocks, so we use EN as ground truth for the split point and
ask the LLM (Gemini → NVIDIA per engine policy) to cut the ZH line at the
correct title/body boundary WITHOUT changing any wording.

Modes:
  --sample N   dry-run on N spread-out cases, print 原始 vs 建議 (no writes)
  --dry-run    dry-run on ALL flagged cases → writes proposals JSON only
  --apply      rewrite JSONL (Drive) + push R2 + update DB preview

Targets come from the audit raw JSON (T2 findings whose heading >60 chars and
contains sentence punctuation). Safe-guards: rejects any split where title or
body is empty, or where title+body != original (char-for-char, ignoring the
inserted blank line).
"""
from __future__ import annotations

import argparse
import os
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import translate_ebook_to_zh as te  # GEMINI_KEYS, gemini_translate infra, nvidia_chat
import standardize_ebook as se       # push_to_r2 + URL/H_GET/H_JSON
import requests

# Audit artifacts (fathers_audit_raw.json) — override with FATHERS_AUDIT_DIR.
SCRATCH = Path(os.environ.get("FATHERS_AUDIT_DIR") or Path(__file__).parent.parent / "_audit")
# 2026-07-20 Drive 改版：電子書 已移入「知識圖工作室」。一律吃 EBOOK_CHUNKS_DIR。
# 找不到就直接爆掉 —— 舊版靜默 skip 會假裝「全部修好了」，極危險。
CH = Path(os.environ.get("EBOOK_CHUNKS_DIR")
          or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
if not CH.exists():
    raise SystemExit(f"[FATAL] chunks dir not found: {CH} — "
                     "set EBOOK_CHUNKS_DIR to the current Drive location.")

HEAD_RE = re.compile(r"^(#{1,4})\s+(.+)$")


def norm(s: str) -> str:
    return re.sub(r"\[\^\d+\]|\{\{p:\d+\}\}|\*+|\s", "", s or "")


def is_swallow(htext: str) -> bool:
    return len(norm(htext)) > 60 and bool(re.search(r"[。！？]", htext))


def fathers_ebook_ids() -> list[str]:
    """The refined 教父 volumes, read straight from the /fathers listing page so
    the worklist never drifts from what the site marks as 已精修."""
    import re as _re
    vue = Path(__file__).parent.parent / "pages" / "fathers" / "index.vue"
    ids = _re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                      vue.read_text(encoding="utf-8"))
    return list(dict.fromkeys(ids))


def load_targets() -> dict[str, list[int]]:
    """Whole-book scan for chunks containing >=1 swallowed heading.

    NOTE: an earlier version derived targets from the audit JSON's T2 findings,
    but scan_translated_book only reports the FIRST heading per chunk, so that
    undercounted badly (228 vs the real ~5,776). Always scan the JSONL itself.
    """
    targets: dict[str, list[int]] = {}
    for eid in fathers_ebook_ids():
        fn = CH / f"{eid}.jsonl"
        if not fn.exists():
            continue
        idxs = []
        for line in fn.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            c = json.loads(line)
            if find_swallow_line(c.get("content") or ""):
                idxs.append(c.get("chunk_index"))
        if idxs:
            targets[eid] = idxs
    return targets


def first_blocks(md: str, n: int = 6) -> list[str]:
    return [b.strip() for b in md.split("\n\n") if b.strip()][:n]


def en_reference(source_text: str, zh_head_norm: str) -> tuple[str, str]:
    """Return (en_heading, en_body_opening) from the EN source's leading blocks.
    We take the first EN heading-shaped block and the first following body block."""
    blocks = [b.strip() for b in (source_text or "").split("\n\n") if b.strip()]
    en_head, en_body = "", ""
    for i, b in enumerate(blocks):
        m = HEAD_RE.match(b.split("\n")[0].strip())
        if m:
            en_head = m.group(2).strip()
            # first non-heading block after it
            for nb in blocks[i + 1:]:
                if not HEAD_RE.match(nb.split("\n")[0].strip()):
                    en_body = nb.strip()
                    break
            break
    return en_head[:200], en_body[:200]


SPLIT_PROMPT = """以下這行中文把一個「小節標題」和緊接的「內文段落」誤黏成同一行，中間漏了分段。\
請只在正確的標題／內文分界處切開，**逐字保留原文，不得改字、翻譯、增刪或調整任何標點**。

判斷分界時參考英文原文結構（英文的標題與內文本來就是分開的）：
- 英文標題：{en_head}
- 英文內文起始：{en_body}

待切開的中文（已去除開頭的 Markdown「#」記號，你回傳時也不要加回「#」）：
{zh}

只輸出 JSON，格式：{{"title": "小節標題", "body": "內文段落全文"}}
title 應該短（對應英文標題）；body 是其餘全部內文。不要輸出任何其他文字。"""


USE_GEMINI = True  # flipped off by --no-gemini when Gemini quota is exhausted


def llm_split(zh_line: str, en_head: str, en_body: str) -> dict | None:
    prompt = SPLIT_PROMPT.format(en_head=en_head or "(無)", en_body=en_body or "(無)", zh=zh_line)
    out = None
    if USE_GEMINI:
        try:
            out = te.gemini_chat(prompt) if hasattr(te, "gemini_chat") else _gemini_generic(prompt)
        except Exception as e:  # noqa: BLE001
            print(f"    gemini fail: {e}; → nvidia", file=sys.stderr)
    if not out:
        try:
            out = te.nvidia_chat(prompt, max_tokens=3000)
        except Exception as e:  # noqa: BLE001
            print(f"    nvidia fail: {e}", file=sys.stderr)
            return None
    # strip code fences
    out = re.sub(r"^```(?:json)?|```$", "", out.strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(obj, dict) or not obj.get("title") or not obj.get("body"):
        return None
    return {"title": str(obj["title"]).strip(), "body": str(obj["body"]).strip()}


def _gemini_generic(prompt: str) -> str:
    """Generic Gemini call (translate_ebook_to_zh only exposes a fixed-prompt
    translator, so replicate the minimal request here with the same keys)."""
    import time
    import requests
    keys = te.GEMINI_KEYS
    if not keys:
        raise RuntimeError("no Gemini key")
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "text/plain"}}
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{te.GEMINI_MODEL}:generateContent"
    for ki in range(len(keys)):
        key = keys[(te._key_idx + ki) % len(keys)]
        for attempt, wait in enumerate((0, 3, 10), start=1):
            if wait:
                time.sleep(wait)
            try:
                r = requests.post(f"{base}?key={key}", json=body, timeout=90)
            except requests.exceptions.RequestException:
                continue
            if r.status_code == 200:
                try:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError):
                    continue
            if r.status_code in (429, 502, 503, 504):
                continue
            raise RuntimeError(f"Gemini HTTP {r.status_code}")
    raise RuntimeError("all Gemini keys failed")


def validate(orig_line_text: str, title: str, body: str) -> bool:
    """title+body must equal the original heading text char-for-char (ignoring
    whitespace) so we never silently lose/alter content."""
    return norm(title) + norm(body) == norm(orig_line_text)


def find_swallow_line(content: str, skip: set[str] | None = None) -> tuple[int, str, str] | None:
    """Return (line_index, marker, heading_text) of the first swallowed heading.
    `skip` holds heading texts we already failed to split, so the caller's loop
    advances past them instead of spinning on the same line."""
    lines = content.split("\n")
    for i, ln in enumerate(lines):
        m = HEAD_RE.match(ln.strip())
        if m and is_swallow(m.group(2)) and not (skip and m.group(2) in skip):
            return i, m.group(1), m.group(2)
    return None


def process_chunk(chunk: dict, retries: int = 2, max_fixes: int = 30) -> dict | None:
    """Fix EVERY swallowed heading in the chunk — consolidated chunks (e.g.
    「第1-10章」) carry many sub-chapter headings and more than one can be
    swallowed, so a single-shot fix would leave the rest behind."""
    content = chunk.get("content", "")
    if not find_swallow_line(content):
        return None
    src = chunk.get("source_text") or (chunk.get("sources") or {}).get("en", "") or ""
    titles: list[str] = []
    failures: list[str] = []
    skip: set[str] = set()
    for _ in range(max_fixes):
        found = find_swallow_line(content, skip)
        if not found:
            break
        line_idx, marker, htext = found
        en_head, en_body = en_reference(src, norm(htext))
        split = None
        for _r in range(retries):
            cand = llm_split(htext, en_head, en_body)
            if cand and validate(htext, cand["title"], cand["body"]):
                split = cand
                break
        if not split:
            # Can't split this one - leave it untouched and skip past it so
            # the loop advances instead of spinning on the same heading.
            failures.append(htext[:60])
            lines = content.split("\n")
            skip.add(htext)
            content = "\n".join(lines)
            continue
        lines = content.split("\n")
        lines[line_idx] = f"{marker} {split['title']}\n\n{split['body']}"
        content = "\n".join(lines)
        titles.append(split["title"])
    if not titles:
        return {"ok": False, "reason": "no-valid-split", "orig": failures[:1] and failures[0] or ""}
    return {"ok": True, "titles": titles, "failed": failures, "new_content": content}


def refresh_previews(ebook_id: str, chunks: list[dict]) -> None:
    requests.delete(f"{se.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                    headers=se.H_GET, timeout=30)
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type", "chapter"),
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        "content": (c.get("content") or "")[:200],
        "char_count": len(c.get("content") or ""),
    } for c in chunks]
    for i in range(0, len(rows), 25):
        batch = rows[i:i + 25]
        rr = requests.post(f"{se.URL}/rest/v1/ebook_chunks", headers=se.H_JSON, json=batch, timeout=60)
        if rr.status_code not in (200, 201):
            for row in batch:
                requests.post(f"{se.URL}/rest/v1/ebook_chunks", headers=se.H_JSON, json=row, timeout=30)


def apply_book(eid: str, idxs: list[int]) -> dict:
    fn = CH / f"{eid}.jsonl"
    chunks = [json.loads(l) for l in fn.read_text(encoding="utf-8").splitlines() if l]
    by_idx = {c.get("chunk_index"): c for c in chunks}
    fixed, skipped = [], []
    for idx in idxs:
        c = by_idx.get(idx)
        if not c:
            skipped.append({"idx": idx, "reason": "chunk-missing"}); continue
        res = process_chunk(c)
        if res and res.get("ok"):
            c["content"] = res["new_content"]
            fixed.append({"idx": idx, "titles": res["titles"], "failed": res.get("failed", [])})
            n = len(res["titles"])
            print(f"    ✓ c{idx}: {n} 處 — {res['titles'][0][:36]}"
                  + (f" …+{n-1}" if n > 1 else ""), file=sys.stderr)
        else:
            skipped.append({"idx": idx, "reason": (res or {}).get("reason", "?"),
                            "orig": (res or {}).get("orig", "")[:80]})
            print(f"    ⚠ c{idx} skipped: {(res or {}).get('reason')}", file=sys.stderr)
    if fixed:
        with open(fn, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        try:
            se.push_to_r2(eid, fn); print("    ✓ R2", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"    ⚠ R2: {e}", file=sys.stderr)
        try:
            refresh_previews(eid, chunks); print("    ✓ DB previews", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"    ⚠ DB: {e}", file=sys.stderr)
    return {"eid": eid, "fixed": fixed, "skipped": skipped}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0, help="dry-run on N spread cases")
    ap.add_argument("--dry-run", action="store_true", help="dry-run ALL → proposals json")
    ap.add_argument("--apply", action="store_true", help="write JSONL + R2 + DB")
    ap.add_argument("--no-gemini", action="store_true", help="skip Gemini, use NVIDIA directly")
    ap.add_argument("--limit", type=int, default=0, help="only process the first N books still needing work")
    args = ap.parse_args()

    global USE_GEMINI
    if args.no_gemini:
        USE_GEMINI = False

    targets = load_targets()
    flat = [(eid, idx) for eid, idxs in targets.items() for idx in idxs]
    print(f"total swallow targets: {len(flat)} across {len(targets)} books", file=sys.stderr)

    if args.sample:
        # spread across books: one per book until N
        picked, seen = [], set()
        for eid, idx in flat:
            if eid not in seen:
                picked.append((eid, idx)); seen.add(eid)
            if len(picked) >= args.sample:
                break
        proposals = []
        for eid, idx in picked:
            fn = CH / f"{eid}.jsonl"
            chunks = {c.get("chunk_index"): c for c in
                      (json.loads(l) for l in fn.read_text(encoding="utf-8").splitlines() if l)}
            c = chunks.get(idx)
            if not c:
                continue
            print(f"\n… {eid[:8]} chunk {idx}", file=sys.stderr)
            res = process_chunk(c)
            proposals.append({"eid": eid, "idx": idx, "res": res})
        (SCRATCH / "heading_split_sample.json").write_text(
            json.dumps(proposals, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nwrote sample → {SCRATCH / 'heading_split_sample.json'}", file=sys.stderr)
        return

    if args.apply:
        report = []
        tot_fixed = tot_skip = 0
        # Skip books whose targets no longer contain any swallow (already
        # repaired in an earlier run) so --limit spends its budget on real work.
        pending = []
        for eid, idxs in targets.items():
            fn = CH / f"{eid}.jsonl"
            if not fn.exists():
                continue
            by = {c.get("chunk_index"): c for c in
                  (json.loads(l) for l in fn.read_text(encoding="utf-8").splitlines() if l)}
            if any(by.get(i) and find_swallow_line(by[i].get("content", "")) for i in idxs):
                pending.append((eid, idxs))
        print(f"books still needing work: {len(pending)}", file=sys.stderr)
        if args.limit:
            pending = pending[:args.limit]
        for bi, (eid, idxs) in enumerate(pending, 1):
            print(f"\n[{bi}/{len(targets)}] {eid}  ({len(idxs)} targets)", file=sys.stderr)
            r = apply_book(eid, idxs)
            report.append(r)
            tot_fixed += len(r["fixed"]); tot_skip += len(r["skipped"])
        (SCRATCH / "heading_split_apply_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n=== DONE: fixed {tot_fixed}, skipped {tot_skip} across {len(targets)} books ===",
              file=sys.stderr)
        return

    print("nothing to do — pass --sample N / --apply", file=sys.stderr)


if __name__ == "__main__":
    main()
