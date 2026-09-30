#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回原 PDF 重抽段落（2026-10-01）：有 538 本 PDF 的正文每頁被接成一大段、換行全丟了
（段長中位數 13,000 字），資料裡已分不出段落，restructure_chapters 只能跳過。

這裡用 PyMuPDF 讀每一行的位置重建段落，只換掉每塊的 content，其餘欄位（chapter_path、
page_number、page_numbers、printed_pages）原樣保留：
  - 新段落：行首比左邊界縮排 ≥ 6pt，或與上一行的間距 > 行距中位數 ×2.5（掃描書行距不均，×1.6 會切斷句子），
            或上一行比版面短 15% 以上且以句末標點收尾；
  - 行尾「-」接下一行小寫開頭 → 接回斷字；
  - 書眉：同一行字（去掉數字）在全書 ≥ 5 頁的頁首或頁尾出現 → 拿掉；純頁碼行拿掉；
  - 每頁開頭放 {{p:印刷頁}}（沒有印刷頁就不放，不留 PDF 頁假頁碼），跨頁續段不斷段。
守恆：新舊兩版的字（\\w）數差距 > 3% 就不寫（這批書的舊內容也是同一個文字層抽的，應該幾乎一樣）。

  python -X utf8 scripts/reflow_pdf_paragraphs.py --ids 檔 [--apply]
寫回留 .jsonl.bak_reflow，推 R2＋更新 DB；之後再跑 restructure_chapters 才會一章一頁。
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
END = re.compile(r"[.?!:;\"'”’)\]。！？」』）：；]$")


def page_lines(page) -> list[tuple[float, float, float, float, str]]:
    """[(x0, y0, x1, y1, 文字)]，照閱讀順序。"""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b["lines"]:
            t = "".join(s["text"] for s in ln["spans"]).strip()
            if t:
                x0, y0, x1, y1 = ln["bbox"]
                out.append((x0, y0, x1, y1, t))
    return out


def running_keys(doc, pages: list[int]) -> set[str]:
    """全書 ≥5 頁的頁首／頁尾出現同一行字（去數字）→ 書眉。"""
    cnt: collections.Counter = collections.Counter()
    for p in pages:
        ls = page_lines(doc[p - 1])
        for t in {ls[0][4], ls[-1][4]} if ls else ():
            k = re.sub(r"[\d\s.·—\-|]+", "", t).lower()
            if k and len(k) < 60:
                cnt[k] += 1
    return {k for k, n in cnt.items() if n >= 5}


def page_paragraphs(page, running: set[str]) -> tuple[list[str], bool]:
    """回傳 (段落們, 第一段是否是新段落開頭)。"""
    ls = page_lines(page)
    # 去頁首頁尾：書眉或純頁碼
    while ls and (re.fullmatch(r"[\divxlcIVXLC.\s\-—]{1,8}", ls[0][4])
                  or re.sub(r"[\d\s.·—\-|]+", "", ls[0][4]).lower() in running):
        ls = ls[1:]
    while ls and (re.fullmatch(r"[\divxlcIVXLC.\s\-—]{1,8}", ls[-1][4])
                  or re.sub(r"[\d\s.·—\-|]+", "", ls[-1][4]).lower() in running):
        ls = ls[:-1]
    if not ls:
        return [], False
    left = statistics.median(x[0] for x in ls)
    right = max(x[2] for x in ls)
    width = max(1.0, right - left)
    gaps = [b[1] - a[3] for a, b in zip(ls, ls[1:]) if b[1] > a[3]]
    gap_med = statistics.median(gaps) if gaps else 0
    paras: list[str] = []
    cur: list[str] = []
    first_new = ls[0][0] - left >= 6
    for i, (x0, y0, x1, y1, t) in enumerate(ls):
        if i:
            px0, py0, px1, py1, pt = ls[i - 1]
            new = (x0 - left >= 6 and px0 - left < 6) \
                or (gap_med and y0 - py1 > gap_med * 2.5 + 4) \
                or ((right - px1) > 0.15 * width and END.search(pt))
            if new and cur:
                paras.append(" ".join(cur))
                cur = []
        if cur and cur[-1].endswith("-") and t[:1].islower():
            cur[-1] = cur[-1][:-1] + t
        elif cur and re.search(r"[\u4e00-\u9fff]$", cur[-1]) and re.match(r"[\u4e00-\u9fff]", t):
            cur[-1] += t                    # 中文行接行不加空格
        else:
            cur.append(t)
    if cur:
        paras.append(" ".join(cur))
    paras = [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]
    # 修補切過頭：上一段沒有句末標點、這段小寫開頭 → 同一句被切開，接回
    fixed: list[str] = []
    for p in paras:
        if fixed and not END.search(fixed[-1]) and p[:1].islower():
            fixed[-1] += " " + p
        else:
            fixed.append(p)
    return fixed, first_new


def words(s: str) -> int:
    return len(re.findall(r"\w", re.sub(r"\{\{[ps]:[^}]*\}\}|\[\^\d+\]", "", s)))


def reflow_book(chunks: list[dict], pdf_path: str) -> tuple[list[dict] | None, str]:
    import fitz
    doc = fitz.open(pdf_path)
    all_pages = sorted({p for c in chunks for p in (c.get("page_numbers") or [c.get("page_number")]) if p})
    if not all_pages or max(all_pages) > len(doc):
        return None, "頁碼對不上 PDF"
    running = running_keys(doc, all_pages)
    out = []
    for c in chunks:
        pages = c.get("page_numbers") or ([c["page_number"]] if c.get("page_number") else [])
        printed = c.get("printed_pages") or [None] * len(pages)
        old = c.get("content") or ""
        if not pages or "\n\n" in old.strip() and statistics.median(len(p) for p in old.split("\n\n")) < 2500:
            out.append(dict(c))          # 這塊本來就有分段，不動
            continue
        paras: list[str] = []
        for p, pp in zip(pages, printed):
            ps, first_new = page_paragraphs(doc[p - 1], running)
            if not ps:
                continue
            mark = f"{{{{p:{pp}}}}}" if pp else ""
            if paras and not first_new and not END.search(paras[-1]):
                paras[-1] += (" " if not re.search(r"[\u4e00-\u9fff]$", paras[-1]) else "") + mark + ps[0]
                ps = ps[1:]
            elif ps:
                ps[0] = mark + ps[0]
            paras += ps
        # 舊內容的註釋區（分隔線之後）照搬
        m = re.search(r"\n[—\-]{15,}\n[\s\S]*$", old)
        new = "\n\n".join(paras) + (m.group(0) if m else "")
        out.append(dict(c, content=new))
    a, b = sum(words(c.get("content") or "") for c in chunks), sum(words(c["content"]) for c in out)
    if a and abs(a - b) / a > 0.03:
        return None, f"字數守恆失敗 {a:,}→{b:,}"
    return out, f"OK {a:,}→{b:,}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    import multiprocessing as mp
    import audit_toc_accuracy as at
    meta = at.load_meta()
    done = set(DONE.read_text(encoding="utf-8").split()) if DONE.exists() else set()
    for bid in Path(a.ids).read_text(encoding="utf-8").split():
        if a.apply and bid in done:
            continue                               # 已重抽且推完（斷掉重跑時接續用）
        # 每本在子行程跑、逾時就砍：10-01 凌晨兩次整條停擺，都是 PyMuPDF 零碎讀 Drive 上的 PDF 時等下載等不回來
        p = mp.Process(target=handle, args=(bid, meta.get(bid, {}), a.apply))
        p.start()
        p.join(BOOK_TIMEOUT)
        if p.is_alive():
            p.terminate()
            p.join()
            print("TIMEOUT", bid, f"超過 {BOOK_TIMEOUT // 60} 分鐘，砍掉跳下一本", flush=True)
    return 0


BOOK_TIMEOUT = 900
DONE = Path(__file__).resolve().parents[1] / "output" / "restructure" / "reflow_done.txt"


def handle(bid: str, m: dict, apply: bool) -> None:
    import os
    import socket
    import tempfile
    socket.setdefaulttimeout(120)      # 10-01 凌晨：沒設逾時的 DB／R2 呼叫也可能掛住
    import standardize_ebook as se
    src = CH / f"{bid}.jsonl"
    bak = src.with_name(src.name + ".bak_reflow")
    tmp_pdf = None
    try:
        if m.get("file_type") != "pdf" or not Path(m.get("file_path") or "").exists():
            print("SKIP", bid, "不是 PDF 或原檔不在", flush=True)
            return
        base = bak if bak.exists() else src
        cs = [json.loads(l) for l in base.open(encoding="utf-8") if l.strip()]
        cs.sort(key=lambda c: c.get("chunk_index") or 0)
        # 先把 PDF 整份複製到本機再讀：一次循序下載，比 PyMuPDF 在 Drive 上零碎讀穩
        fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        shutil.copyfile(m["file_path"], tmp_pdf)
        out, why = reflow_book(cs, tmp_pdf)
        print(("OK" if out else "SKIP"), bid, why, flush=True)
        if out and apply:
            if not bak.exists():
                shutil.copy2(src, bak)
            tmp = src.with_name(src.name + ".tmp")      # 寫完整份再換上，被砍也不會留半個檔
            with tmp.open("w", encoding="utf-8") as f:
                for c in out:
                    f.write(json.dumps(c, ensure_ascii=False) + "\n")
            os.replace(tmp, src)
            se.push_to_r2(bid, src)
            se.update_db(bid, out)
            with DONE.open("a", encoding="utf-8") as f:
                f.write(bid + "\n")
    except Exception as e:  # noqa: BLE001
        print("ERR", bid, f"{type(e).__name__}: {str(e)[:120]}", flush=True)
    finally:
        if tmp_pdf and os.path.exists(tmp_pdf):
            os.remove(tmp_pdf)


if __name__ == "__main__":
    sys.exit(main())
