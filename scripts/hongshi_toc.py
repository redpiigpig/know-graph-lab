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

# 分隔符有兩種：80–156 期用「／」，**157 期起改版用「│」**。
# 只認一種的話，改版後那 44 期會全部解析成 0 篇，而且完全沒有錯誤訊息。
_SEPS = "／│"
_SEP_RE = re.compile("[" + _SEPS + "]")

# 頁碼必須是**獨立的數字**（後面接空白或行尾）。少了這道界限，封面說明裡的
# 「2023年8月13日，第二十一屆…」會被當成第 202 頁的篇目。
_ENTRY_RE = re.compile(r"^\s*(\d{1,3})(?=[\s　]|$)[\s　]*(.*)$")

# 目次的起點；在它之前的是刊頭（版權頁那一堆「發行人│…」）
_TOC_MARK_RE = re.compile(r"目\s*次|Contents")

# 刊頭欄位長得跟篇目一模一樣（`發行人│釋見岸`），不擋掉會整批變成假篇目
_MASTHEAD_RE = re.compile(
    r"^\s*(民國.{0,12}出刊|.{0,6}創刊|封面說明|封底說明|導師|發行人|總編輯|副總編輯"
    r"|美術排版|編校|編政|發行|地址|電話|傳真|電子信箱|弘誓學團網址|劃撥帳號|戶名"
    r"|ISSN|vol\.)\s*[" + _SEPS + "]"
)
# 封面說明底下是一段散文，要整段跳過，直到下一個真的篇目
_COVER_NOTE_RE = re.compile(r"^\s*(封面說明|封底說明)\s*[" + _SEPS + "]")

# 分類小標一律帶標記（【本期專題】、■…）。
# 🚨 別用「純中文 2-20 字」當判準：新版的篇名本身就長那樣，會被整條吃掉。
_SECTION_RE = re.compile(r"^\s*[■□◆●【]")


def _clean(s: str) -> str:
    """收斂空白。**破折號要留著**——續行的「——點評余鐘柳律師」是副標記號，
    strip 掉會讓篇名變成「他們早就應該走下「神壇」點評余鐘柳律師」。"""
    return re.sub(r"[　\s]+", " ", (s or "").strip()).strip(" ‧·")


def _split_author(rest: str) -> tuple[str, str]:
    """把一行拆成 (篇名部分, 作者)。以**最後一個**分隔符為界。"""
    idx = max(rest.rfind(c) for c in _SEPS)
    return rest[:idx], rest[idx + 1:]


def parse_toc(text: str) -> list[dict]:
    """一頁目次文字 → [{"page":6,"title":"…","author":"釋昭慧"}]。

    新舊兩種版面共用一套規則（差別只在分隔符是「／」還是「│」）：
      有頁碼＋有分隔符 → 完整一筆
      有頁碼＋無分隔符 → 開一筆，篇名待續（下一行的「——副標」接上來）
      無頁碼＋有分隔符 → 接續前一筆；沒有前一筆就是「編輯室報告│釋耀行」那種無頁碼篇目
      無頁碼＋無分隔符 → 前一筆待續就接篇名，否則視為分類小標丟掉

    🚨 **兩欄式版面直接回空**：157 期那種「頁碼獨立成一欄、篇名在另一欄」的排版，
    PyMuPDF 會先吐一整串裸頁碼再吐篇名。硬解會生出一堆空篇名的假篇目，
    再把後面所有文字全灌進最後一筆——寧可回空讓稽核看見，也不要吐垃圾。
    """
    body = text or ""
    m = _TOC_MARK_RE.search(body)
    if m:
        body = body[m.end():]  # 目次之前是刊頭，不是篇目

    out: list[dict] = []
    pending: dict | None = None
    empty_starts = 0   # 「開了一筆卻沒篇名」的次數＝兩欄式版面的徵兆
    skipping = False   # 封面說明的散文區

    def flush():
        nonlocal pending
        if pending and pending.get("author") and pending.get("title"):
            out.append(pending)
        pending = None

    for raw in body.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if _COVER_NOTE_RE.match(line):
            flush()
            skipping = True
            continue
        m = _ENTRY_RE.match(line)
        if skipping:
            # 封面說明散文結束於下一個篇目、分類小標，或編輯室報告
            if m or line.lstrip().startswith("【") or "編輯室報告" in line:
                skipping = False
            else:
                continue
        if _MASTHEAD_RE.match(line):
            flush()
            continue
        rest = m.group(2) if m else line
        has_author = bool(_SEP_RE.search(rest))
        if m:
            if pending is not None and not pending["title"]:
                empty_starts += 1
                if empty_starts >= 3:
                    return []  # 兩欄式版面，交給稽核處理
            flush()
            if has_author:
                title, author = _split_author(rest)
                out.append({"page": int(m.group(1)), "title": _clean(title),
                            "author": _clean(author)})
            else:
                pending = {"page": int(m.group(1)), "title": _clean(rest), "author": ""}
            continue
        if has_author:
            title, author = _split_author(rest)
            if pending is not None:
                extra = _clean(title)
                if extra:
                    pending["title"] = pending["title"] + extra
                pending["author"] = _clean(author)
                flush()
            elif _clean(title) and _clean(author):
                # 無頁碼的篇目（改版後的「編輯室報告│釋耀行」就長這樣）
                out.append({"page": None, "title": _clean(title), "author": _clean(author)})
            continue
        if pending is not None and not _SECTION_RE.match(line):
            pending["title"] = pending["title"] + _clean(rest)
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
    """在前 14 頁裡找目次頁。回傳 (0-based 頁次, 文字)。

    計分＝分隔符個數，帶「目次／Contents」字樣的再加重。兩種版面的分隔符不同
    （舊「／」新「│」），只數一種的話改版後那批會挑到錯的頁或挑不到。
    """
    best = (-1, 0, "")
    for i in range(min(14, len(doc))):
        t = doc[i].get_text() or ""
        n = len(_SEP_RE.findall(t)) + (100 if _TOC_MARK_RE.search(t) else 0)
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


def _pg(page) -> str:
    """頁碼欄；改版後有「編輯室報告」這種無頁碼篇目，直接格式化 None 會炸。"""
    return f"p{page:<4}" if page is not None else "  -  "


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
            print(f"  {iss:>3} 期 {_pg(e['page'])} {e['title'][:46]}　／{e['author']}")
    elif a.inspect:
        for i in issues:
            print(f"\n第 {i['issue']} 期（目次在 p{i['toc_page']}）")
            for e in i["articles"]:
                print(f"  {_pg(e['page'])} {e['title'][:50]}　／{e['author']}")

    if a.out:
        Path(a.out).write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✅ {a.out}")


if __name__ == "__main__":
    main()
