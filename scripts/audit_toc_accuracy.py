#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""唯讀稽核（2026-09-27）：電子圖書館每本書的「目錄章節抓得準不準、切塊合不合理、頁碼是不是原書的」。

audit_book_structure.py 只數「有沒有章節」；這支驗「對不對」。逐本讀 Drive `_chunks/*.jsonl`。

目錄章節
  NO_TOC            長書（≥30 塊）章名少於 2 種
  BODY_AS_TITLE     章名其實是正文：>50 字、句號結尾、或含 2 個以上逗號（章名黏正文）
  RUNNING_HEADER    同一章名在全書不連續出現 ≥3 段（書眉被當章名，或切錯）
  SEQ_BROKEN        「第N章／Chapter N」編號跳號或倒退
  PRINTED_TOC_MISS  書前「目錄／目次／Contents」頁列出的條目，在章名裡找得到的 <50%
  JUNK_TITLE        章名是頁碼、純數字、亂碼（無漢字無字母）
切塊
  GRANULARITY       page（一頁一塊）／chapter（一章一塊）／section（一節多塊）／mixed
  TINY_CHUNKS       >30% 的塊少於 150 字（碎裂）
  GIANT_CHUNK       有塊超過 80,000 字（沒切開）
頁碼
  PAGE_NONE         無頁碼（epub 正常；pdf 就是遺失）
  PAGE_SERIAL       page_number == chunk_index+1 佔 ≥90%（流水號冒充頁碼，epub 才算假）
  PAGE_BACKWARD     頁碼倒退 ≥3 次
OCR
  THIN_TEXT         pdf 每頁平均 <80 字（帶薄文字層、實際要 OCR）

輸出：output/toc_audit/toc_audit.tsv（一書一列）＋ summary.md
用法：python -X utf8 scripts/audit_toc_accuracy.py [--limit N]
"""
from __future__ import annotations

import collections
import json
import re
import statistics
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
OUT = Path(__file__).resolve().parents[1] / "output" / "toc_audit"
HAN = re.compile(r"[\u4e00-\u9fff]")
LAT = re.compile(r"[A-Za-z]")
CJK_NUM = "〇零一二三四五六七八九十百"
SEQ_RE = re.compile(r"(?:第\s*([0-9" + CJK_NUM + r"]+)\s*[章講篇])|(?:\b(?:Chapter|CHAPTER|Lecture|LECTURE)\s+([0-9IVXLCivxlc]+)\b)")
TOC_HEAD = re.compile(r"^\s*#*\s*(目\s*錄|目\s*次|Contents|CONTENTS|Table of Contents)\s*$", re.M)


def cjk_int(s: str) -> int | None:
    if s.isdigit():
        return int(s)
    d = {c: i for i, c in enumerate("〇一二三四五六七八九")}
    d["零"] = 0
    if all(c in d for c in s):
        return int("".join(str(d[c]) for c in s)) if len(s) > 1 and "十" not in s else d.get(s)
    total, cur = 0, 0
    for c in s:
        if c in d:
            cur = d[c]
        elif c == "十":
            total += (cur or 1) * 10
            cur = 0
        elif c == "百":
            total += (cur or 1) * 100
            cur = 0
        else:
            return None
    return total + cur


def roman(s: str) -> int | None:
    v = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
    s = s.lower()
    if not s or any(c not in v for c in s):
        return None
    t = 0
    for i, c in enumerate(s):
        t += -v[c] if i + 1 < len(s) and v[s[i + 1]] > v[c] else v[c]
    return t


def leaf(cp: str) -> str:
    return re.split(r"\s*[/·‧]\s*", cp)[-1].strip() if cp else ""


def body_like(t: str) -> bool:
    t = t.strip()
    return len(t) > 50 or t.endswith(("。", "！", "？", ".")) and len(t) > 25 or t.count("，") >= 2


def audit(chunks: list[dict], meta: dict) -> dict:
    flags = []
    n = len(chunks)
    cps = [(c.get("chapter_path") or "").strip() for c in chunks]
    leaves = [leaf(x) for x in cps]
    distinct = [x for x in dict.fromkeys(x for x in cps if x)]
    ftype = (meta.get("file_type") or "").lower()
    lens = [len(c.get("content") or "") for c in chunks]
    # ── 目錄章節 ──
    if n >= 30 and len(distinct) < 2:
        flags.append("NO_TOC")
    titles = list(dict.fromkeys(x for x in leaves if x))
    body_titles = [t for t in titles if body_like(t)]
    if titles and len(body_titles) / len(titles) > 0.2 and len(body_titles) >= 3:
        flags.append("BODY_AS_TITLE")
    runs = collections.Counter()
    prev = None
    for x in cps:
        if x and x != prev:
            runs[x] += 1
        prev = x
    rh = [t for t, k in runs.items() if k >= 3]
    if rh and sum(runs[t] for t in rh) >= 6:
        flags.append("RUNNING_HEADER")
    nums = []
    for t in titles:
        m = SEQ_RE.search(t)
        if m:
            v = cjk_int(m.group(1)) if m.group(1) else (int(m.group(2)) if m.group(2).isdigit() else roman(m.group(2)))
            if v:
                nums.append(v)
    if len(nums) >= 4:
        bad = sum(1 for a, b in zip(nums, nums[1:]) if b != a + 1 and b != 1)
        if bad >= 2:
            flags.append("SEQ_BROKEN")
    junk = [t for t in titles if not HAN.search(t) and not LAT.search(t)]
    if titles and len(junk) >= 3 and len(junk) / len(titles) > 0.1:
        flags.append("JUNK_TITLE")
    # 書前印刷目錄對照
    toc_hit = ""
    for c in chunks[: max(15, n // 10)]:
        body = c.get("content") or ""
        m = TOC_HEAD.search(body)
        if not m:
            continue
        entries = []
        for line in body[m.end():].splitlines():
            line = re.sub(r"[\.·…\s]+\d+\s*$", "", line).strip(" #*-")
            line = re.sub(r"\s+", "", line)
            if 2 <= len(line) <= 30 and (HAN.search(line) or LAT.search(line)):
                entries.append(line)
        entries = entries[:60]
        if len(entries) >= 5:
            norm = lambda x: re.sub(r"^[0-9IVXLivxl\.\s第章部篇講一二三四五六七八九十、:：]+", "", re.sub(r"\s+", "", x)).lower()
            tset = "|".join(norm(t) for t in titles)
            hit = sum(1 for e in entries if norm(e)[:6] and norm(e)[:6] in tset)
            toc_hit = f"{hit}/{len(entries)}"
            if hit / len(entries) < 0.5:
                flags.append("PRINTED_TOC_MISS")
        break
    # ── 切塊 ──
    types = collections.Counter(c.get("chunk_type") for c in chunks)
    pages = [c.get("page_number") for c in chunks]
    per_title = [k for k in collections.Counter(x for x in cps if x).values()]
    if types.get("page", 0) > 0.6 * n:
        gran = "page"
    elif per_title and statistics.median(per_title) <= 1.2:
        gran = "chapter"
    elif per_title and statistics.median(per_title) > 1.2:
        gran = "section"
    else:
        gran = "none"
    if n >= 20 and sum(1 for L in lens if L < 150) > 0.3 * n:
        flags.append("TINY_CHUNKS")
    if lens and max(lens) > 80_000:
        flags.append("GIANT_CHUNK")
    # ── 頁碼 ──
    have = [(c.get("chunk_index"), p) for c, p in zip(chunks, pages) if isinstance(p, int)]
    if not have:
        page_state = "none"
        if ftype == "pdf" and n >= 10:
            flags.append("PAGE_NONE")
    else:
        serial = sum(1 for ci, p in have if ci is not None and p == ci + 1)
        back = sum(1 for (_, a), (_, b) in zip(have, have[1:]) if b < a)
        page_state = "serial" if serial >= 0.9 * len(have) else "real"
        if page_state == "serial" and ftype == "epub":
            flags.append("PAGE_SERIAL")
        if back >= 3:
            flags.append("PAGE_BACKWARD")
    tp = meta.get("total_pages") or 0
    if ftype == "pdf" and tp >= 20 and sum(lens) / tp < 80:
        flags.append("THIN_TEXT")
    return {"chunks": n, "titles": len(titles), "gran": gran, "median_chars": int(statistics.median(lens)) if lens else 0,
            "page_state": page_state, "toc_hit": toc_hit, "flags": flags,
            "chars_per_page": round(sum(lens) / tp) if tp else ""}


def load_meta() -> dict:
    import translate_ebook_to_zh as te  # 讀 .env
    H = {"apikey": te.KEY, "Authorization": "Bearer " + te.KEY}
    out, off = {}, 0
    while True:
        b = requests.get(te.URL + "/rest/v1/ebooks", headers=H, timeout=120, params={
            "select": "id,title,file_type,total_pages,collection,parse_error", "order": "id",
            "limit": "1000", "offset": str(off)}).json()
        for x in b:
            out[x["id"]] = x
        if len(b) < 1000:
            break
        off += 1000
    return out


def main() -> int:
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    OUT.mkdir(parents=True, exist_ok=True)
    meta = load_meta()
    print("ebooks", len(meta), flush=True)
    files = sorted(p for p in CH.glob("*.jsonl") if p.stem in meta)
    if limit:
        files = files[:limit]
    rows, fc, gc, pc = [], collections.Counter(), collections.Counter(), collections.Counter()
    for i, p in enumerate(files):
        try:
            chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception as e:  # noqa: BLE001
            print("ERR", p.name, type(e).__name__, flush=True)
            continue
        chunks.sort(key=lambda c: c.get("chunk_index") or 0)
        m = meta[p.stem]
        r = audit(chunks, m)
        fc.update(r["flags"])
        gc[r["gran"]] += 1
        pc[(m.get("file_type"), r["page_state"])] += 1
        rows.append([p.stem, (m.get("title") or "")[:40], m.get("file_type"), m.get("collection") or "",
                     r["chunks"], r["titles"], r["gran"], r["median_chars"], r["page_state"], r["toc_hit"],
                     r["chars_per_page"], ",".join(r["flags"])])
        if i % 500 == 0:
            print(f"{i}/{len(files)}", flush=True)
    hdr = ["id", "title", "type", "collection", "chunks", "titles", "gran", "median_chars", "page", "toc_hit",
           "chars_per_page", "flags"]
    (OUT / "toc_audit.tsv").write_text("\n".join("\t".join(map(str, r)) for r in [hdr] + rows) + "\n", encoding="utf-8")
    md = [f"# 目錄章節／切塊／頁碼稽核（分母 {len(rows)} 本）", "", "## 旗標", ""]
    md += [f"- {k}：{v}" for k, v in fc.most_common()]
    md += ["", "## 切塊粒度", ""] + [f"- {k}：{v}" for k, v in gc.most_common()]
    md += ["", "## 頁碼（檔案類型, 狀態）", ""] + [f"- {k}：{v}" for k, v in pc.most_common()]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md), flush=True)
    print("TOC_AUDIT_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
