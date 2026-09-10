#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《弘誓雙月刊》整期 PDF → **篇目層**（頁碼／篇名／作者），零 LLM。

站上這份刊物原本只有「整期 PDF」一層（`magazine-index.json` 每期只有 parts），
所以「昭慧法師在弘誓雙月刊寫過哪些文章」這種問題根本查不了。幸好這批 PDF
**帶乾淨的文字層**，而且每期都有一頁排版一致的目次：

    6  　有關慈濟內湖園區爭議之商榷　／釋昭慧
    13　他們早就應該走下「神壇」
         ——點評余鐘柳律師　　／釋昭慧

於是只要解析那一頁就好，不必 OCR、不必碰配額。長篇名會折行（續行以「——」起頭），
作者可能多位（頓號分隔）或跨宗教對談（「古倫神父‧昭慧法師」）。

  python -X utf8 scripts/hongshi_toc.py --inspect 121      # 看單期解析結果
  python -X utf8 scripts/hongshi_toc.py --all --out public/content/research-data/yinshun-hongshi/magazine-toc.json
  python -X utf8 scripts/hongshi_toc.py --all --author 昭慧 # 只印某人的篇目
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from pathlib import Path

MAG_DIR = r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\弘誓雙月刊"

# ── 純函式（零 I/O，scripts/tests/test_hongshi_toc.py 鎖定）────────────────

# 目次行：開頭是頁碼，中間篇名，最後 ／作者。三者用全形或半形空白隔開。
_ENTRY_RE = re.compile(r"^\s*(\d{1,3})\s*[　\s]+(.*)$")
_AUTHOR_SPLIT = "／"
# 分類小標（■本期專題、薪火相傳…）沒有頁碼也沒有作者，不是篇目
_SECTION_RE = re.compile(r"^\s*[■□◆●]?\s*[\u4e00-\u9fff：:、，,\s]{2,20}\s*$")


def _clean(s: str) -> str:
    """收斂空白。**破折號要留著**——續行的「——點評余鐘柳律師」是副標記號，
    strip 掉會讓篇名變成「他們早就應該走下「神壇」點評余鐘柳律師」。"""
    return re.sub(r"[　\s]+", " ", (s or "").strip()).strip(" ‧·")


def parse_toc(text: str) -> list[dict]:
    """一頁目次文字 → [{"page":6,"title":"…","author":"釋昭慧"}]。

    四種行各自處理：
      有頁碼＋有／ → 完整一筆
      有頁碼＋無／ → 開一筆，篇名待續（下一行的「——副標」接上來）
      無頁碼＋有／ → 接續前一筆：補完篇名並取得作者
      無頁碼＋無／ → 前一筆待續就接篇名，否則視為分類小標丟掉
    """
    out: list[dict] = []
    pending: dict | None = None

    def flush():
        nonlocal pending
        if pending and pending.get("author"):
            out.append(pending)
        pending = None

    for raw in (text or "").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        m = _ENTRY_RE.match(line)
        rest = m.group(2) if m else line
        has_author = _AUTHOR_SPLIT in rest
        if m:
            flush()
            if has_author:
                title, _, author = rest.rpartition(_AUTHOR_SPLIT)
                out.append({"page": int(m.group(1)), "title": _clean(title),
                            "author": _clean(author)})
            else:
                pending = {"page": int(m.group(1)), "title": _clean(rest), "author": ""}
            continue
        if has_author and pending is not None:
            title, _, author = rest.rpartition(_AUTHOR_SPLIT)
            extra = _clean(title)
            if extra:
                pending["title"] = f"{pending['title']}{extra}"
            pending["author"] = _clean(author)
            flush()
            continue
        if pending is not None and not _SECTION_RE.match(line):
            pending["title"] = f"{pending['title']}{_clean(rest)}"
    flush()
    return [e for e in out if e["title"] and e["author"]]


def split_authors(author: str) -> list[str]:
    """作者欄 → 個別作者。頓號分隔（合著）、‧分隔（對談）都要拆開。

    拆開是為了讓「這個人寫過哪些」查得到——不拆的話，
    「古倫神父‧昭慧法師」用「釋昭慧」是比不到的。
    """
    parts = re.split(r"[、,，&＆]|\s+and\s+", author or "")
    out: list[str] = []
    for p in parts:
        for q in re.split(r"[‧·・]", p):
            q = q.strip()
            # 「著，張展源譯」這種要保留原樣，別再切
            if q:
                out.append(q)
    return out or ([author.strip()] if author.strip() else [])


def matches_author(author: str, needle: str) -> bool:
    """作者欄有沒有這個人？比對各種署名（釋昭慧／昭慧法師／昭慧）。"""
    return any(needle in a for a in split_authors(author))


# ── I/O ────────────────────────────────────────────────────────────────────

def find_toc_page(doc) -> tuple[int, str]:
    """在前 14 頁裡找目次頁＝「／」最多的那一頁。回傳 (0-based 頁次, 文字)。"""
    best = (-1, 0, "")
    for i in range(min(14, len(doc))):
        t = doc[i].get_text() or ""
        n = t.count(_AUTHOR_SPLIT)
        if n > best[1]:
            best = (i, n, t)
    return best[0], best[2]


def parse_issue(pdf_path: str) -> dict:
    import fitz
    doc = fitz.open(pdf_path)
    try:
        pno, text = find_toc_page(doc)
        entries = parse_toc(text) if pno >= 0 else []
        # 目次跨頁時下一頁還有一截，接著解析
        if pno >= 0 and pno + 1 < len(doc):
            more = parse_toc(doc[pno + 1].get_text() or "")
            if more and entries and more[0]["page"] >= entries[-1]["page"]:
                entries += more
    finally:
        doc.close()
    m = re.search(r"(\d{2,3})", os.path.basename(pdf_path))
    return {"issue": int(m.group(1)) if m else None,
            "file": os.path.basename(pdf_path),
            "toc_page": pno + 1 if pno >= 0 else None,
            "articles": entries}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=MAG_DIR)
    ap.add_argument("--inspect", help="只看某一期（期號）")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--author", help="只列這位作者的篇目")
    ap.add_argument("--out")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.dir, "*.pdf")))
    if a.inspect:
        files = [f for f in files if a.inspect in os.path.basename(f)]
    if not files:
        raise SystemExit(f"找不到 PDF：{a.dir}")

    # 逐期落地：Drive 上這批 117 期約 4.7 GB，幾乎全部時間在等 I/O
    # （實測 10 分鐘只跑掉 1.6 秒 CPU）。全部跑完才寫檔的話，中斷就前功盡棄，
    # 而且過程中完全看不出還活著沒有。
    cache = Path(a.out).with_suffix(".partial.json") if a.out else None
    done: dict[str, dict] = {}
    if cache and cache.exists():
        done = {i["file"]: i for i in json.loads(cache.read_text(encoding="utf-8"))}
        print(f"（續跑：快取已有 {len(done)} 期）", flush=True)

    issues = []
    for n, f in enumerate(files, 1):
        name = os.path.basename(f)
        if name in done:
            issues.append(done[name])
            continue
        try:
            rec = parse_issue(f)
            issues.append(rec)
            print(f"  [{n}/{len(files)}] {name}　{len(rec['articles'])} 篇", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ {name}: {e}", flush=True)
            continue
        if cache:
            cache.write_text(json.dumps(issues, ensure_ascii=False), encoding="utf-8")

    total = sum(len(i["articles"]) for i in issues)
    empty = [i["issue"] for i in issues if not i["articles"]]
    print(f"{len(issues)} 期　篇目 {total}　解析不到目次 {len(empty)} 期：{empty}")

    if a.author:
        hits = [(i["issue"], e) for i in issues for e in i["articles"]
                if matches_author(e["author"], a.author)]
        print(f"\n『{a.author}』{len(hits)} 篇：")
        for iss, e in hits:
            print(f"  {iss:>3} 期 p{e['page']:<4} {e['title'][:46]}　／{e['author']}")
    elif a.inspect:
        for i in issues:
            print(f"\n第 {i['issue']} 期（目次在 p{i['toc_page']}）")
            for e in i["articles"]:
                print(f"  p{e['page']:<4} {e['title'][:50]}　／{e['author']}")

    if a.out:
        Path(a.out).write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✅ {a.out}")


if __name__ == "__main__":
    main()
