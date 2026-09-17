# -*- coding: utf-8 -*-
"""把 ACCS 兩卷 PDF 的**原書印刷頁碼**補回 JSONL 的 `page_number`。

由來：2026-09-18 稽核（`audit_page_numbers_by_shelf.py`）量出全庫只有兩本 PDF 的
`page_number` 全是 None——ACCS 卷十五《次經》與卷十二《耶利米書‧耶利米哀歌》。
PDF 一律要帶得回原書頁碼（[[feedback_pdf_page_number]]），這兩卷漏了。

作法：
  1. 每頁取**最上面那一條 line**（頁眉），裡面有印刷頁碼。位置會變——有時整行
     就是數字，有時跟在書卷書眉後面（`Tobit 3:7-17 10`）——所以按 y 座標取頂行
     再抽數字，不靠固定欄位。
  2. 由此量出「PDF 頁碼 − 印刷頁碼」的偏移。前言用羅馬數字，正文才進入阿拉伯
     數字，所以偏移只在正文區成立。
  3. 每個 chunk 拿它的 `source_text`（英文原文）去比對逐頁文字，落在哪一頁就
     記那一頁的**印刷頁碼**。

🚨 不可以拿 PDF 頁序當頁碼。這兩卷的 PDF 比原書多出前言，卷十五實測偏移 51 頁
   ——直接用 PDF 頁序會讓每一條引用都錯 51 頁，而且看起來完全正常。
🚨 比對不到的 chunk 一律留 None，不要用內插硬塞。假頁碼比沒有更糟。

    python -X utf8 scripts/accs_backfill_page_numbers.py            # 只分析
    python -X utf8 scripts/accs_backfill_page_numbers.py --apply    # 寫回 Drive+R2+DB
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import fitz
import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHUNKS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
BOOKS = {
    "37ff8191-8bc8-4eeb-bd84-d85fa3dd893b": "卷十五：次經",
    "3f678406-3969-49c1-a971-d76a6fd62f0e": "卷十二：耶利米書‧耶利米哀歌",
}
MIN_PROBE = 24        # 拿來比對的字串長度；太短會配到別頁


def foot_number(page) -> int | None:
    """取頁面**最下面**那一條 line 的整數（印刷頁碼）。

    🚨 頁碼在頁尾置中，不在頁眉。頁眉是書卷書眉（`Tobit 3:7-17`），而且它左右
       頁換邊。第一版抓頂行，603 頁只測到 21 頁有數字（4%），偏移就看起來
       「不穩定」——其實是抓錯地方。
    """
    lines = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            txt = "".join(s["text"] for s in ln["spans"]).strip()
            if txt:
                lines.append((ln["bbox"][1], txt))
    if not lines:
        return None
    bottom = max(y for y, _ in lines)
    foot = " ".join(t for y, t in sorted(lines) if bottom - y < 3)
    m = re.fullmatch(r"\D*?(\d{1,4})\D*", foot)
    return int(m.group(1)) if m else None


def page_offset(doc) -> tuple[int | None, Counter]:
    """回傳（最常見的 PDF−印刷 偏移, 分佈）。"""
    off = Counter()
    for i in range(doc.page_count):
        n = foot_number(doc[i])
        if n is not None:
            off[i + 1 - n] += 1
    return (off.most_common(1)[0][0] if off else None), off


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def squash(s: str) -> str:
    """只留小寫英數，其餘全丟。

    🚨 逐字比對在這裡一定失敗。JSONL 的 source_text 是 OCR 正規化過的：原書的
       小型大寫被拆成 `O VERVIEW`／`A THANASIUS`／`W ISDOM OF S OLOMON`，還混著
       不斷行空格與 markdown `##`。第一版用原字串比對，381 段對到 0 段。
    """
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def build_index(doc) -> list[str]:
    return [squash(doc[i].get_text()) for i in range(doc.page_count)]


def locate(probe: str, pages: list[str], hint: int = 0) -> int | None:
    """probe 落在哪一個 PDF 頁（0-based）。從 hint 往後找，找不到再全掃。"""
    if len(probe) < 8:
        return None
    for i in range(hint, len(pages)):
        if probe in pages[i]:
            return i
    for i in range(0, hint):
        if probe in pages[i]:
            return i
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}",
         "Content-Type": "application/json", "Prefer": "return=representation"}

    for bid, label in BOOKS.items():
        row = requests.get(f"{url}/rest/v1/ebooks?select=id,title,file_path&id=eq.{bid}",
                           headers=h, timeout=60).json()[0]
        pdf = Path(row["file_path"])
        jl = CHUNKS / f"{bid}.jsonl"
        print(f"\n=== {label}")
        print(f"  PDF  {pdf.name}  在={pdf.exists()}")
        print(f"  JSONL 在={jl.exists()}")
        if not (pdf.exists() and jl.exists()):
            print("  ⛔ 缺檔，跳過")
            continue

        doc = fitz.open(pdf)
        offset, dist = page_offset(doc)
        top = dist.most_common(3)
        share = dist[offset] / sum(dist.values()) if dist else 0
        print(f"  PDF {doc.page_count} 頁　偏移 {offset}（佔 {share:.0%}）　前三 {top}")
        if offset is None or share < 0.5:
            print("  ⛔ 偏移不穩定，不敢寫，跳過")
            continue

        pages = build_index(doc)
        rows = [json.loads(l) for l in jl.read_text(encoding="utf-8").splitlines() if l.strip()]
        hit = miss = 0
        hint = 0
        for r in rows:
            # 跳過 markdown 標題那幾行，從正文開始取——標題在 PDF 裡的排版
            # 跟內文不連續，壓平之後不一定接得起來。
            body = "\n".join(ln for ln in (r.get("source_text") or "").split("\n")
                             if ln.strip() and not ln.lstrip().startswith(("#", "*")))
            probe = squash(body or r.get("source_text") or "")
            idx = locate(probe[:80], pages, hint)
            if idx is None:
                idx = locate(probe[:40], pages, hint)
            if idx is None:
                idx = locate(probe[:24], pages, hint)
            if idx is None:
                r["page_number"] = None
                miss += 1
                continue
            hint = idx
            printed = idx + 1 - offset
            r["page_number"] = printed if printed >= 1 else None
            hit += 1 if r["page_number"] else 0
            miss += 0 if r["page_number"] else 1

        got = [r["page_number"] for r in rows if r.get("page_number")]
        print(f"  {len(rows)} 段：對到 {hit}、沒對到 {miss}（分母 {len(rows)}）")
        if got:
            print(f"  印刷頁碼範圍 {min(got)} – {max(got)}　遞增={got == sorted(got)}")
        if not args.apply:
            print("  （dry-run，未寫）")
            continue
        if hit / max(len(rows), 1) < 0.6:
            print("  ⛔ 命中率不到六成，不寫。寧可沒有頁碼也不要錯的")
            continue

        shutil.copy2(jl, jl.with_suffix(".jsonl.bak"))
        with jl.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        import ocr_with_gemini as og
        og.push_to_r2(bid, jl)
        requests.patch(f"{url}/rest/v1/ebooks?id=eq.{bid}", headers=h, timeout=60,
                       data=json.dumps({"total_pages": max(got) if got else None}))
        print(f"  ✓ Drive、R2、DB 都已更新（備份 {jl.with_suffix('.jsonl.bak').name}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
