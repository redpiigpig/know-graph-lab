#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""「一頁一塊但沒有章節」的 PDF：讀 PDF 內建書籤補回 chapter_path，再合併成一節一塊（2026-09-27）。

使用者：「我不相信有書沒有章節」——抽樣 15 本有 11 本 PDF 自帶書籤，只是當初入館沒讀進來。
  1. 子程序讀 fitz get_toc（60 秒逾時；壞 PDF 會讓 fitz 卡死，見 backfill_printed_pages.read_labels）
  2. 沿用 standardize_pdf.normalize_toc（拒收逐頁書籤、濾封面／版權等樣板）；可行時往下多取一層（盡量到「節」）
  3. 書籤名稱清理：NUL、「.pdf」尾巴、尾端頁碼；簡體轉繁（日文書整本判定後不轉）
  4. 依 page_number 替每頁標 chapter_path（「父 / 本」），覆蓋 ≥50% 頁才採用
  5. 交 consolidate_page_chunks.consolidate 合併（同一支程式裡做，不跟其他改寫 JSONL 的程式搶）
留 .jsonl.bak_chapters；報告 output/toc_audit/bookmark_chapters.tsv。
  python -X utf8 scripts/assign_chapters_from_bookmarks.py [--ids ...] [--apply]
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consolidate_page_chunks as cp  # noqa: E402
import standardize_pdf as sp  # noqa: E402
import standardize_ebook as se  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")


def read_toc(fp: str, timeout: int = 60) -> list | None:
    code = "import fitz,json,sys;d=fitz.open(sys.argv[1]);print(json.dumps([d.page_count,d.get_toc()]))"
    try:
        r = subprocess.run([sys.executable, "-c", code, fp], capture_output=True, text=True,
                           encoding="utf-8", timeout=timeout)
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def clean_title(t: str) -> str:
    t = (t or "").replace("\x00", "").strip()
    t = re.sub(r"\.pdf$", "", t, flags=re.I)
    t = re.sub(r"[\s.·…]+\d{1,4}$", "", t).strip()        # 「CONTENTS. 3」「I. Very Man. 7」
    return t


def entries_from_toc(toc: list, total_pages: int) -> list[dict] | None:
    """normalize_toc 取最淺可用層；若再深一層仍不是逐頁書籤（每條平均 ≥2 頁），就用深一層（盡量到節）。"""
    toc = [[lv, clean_title(t), pg] for lv, t, pg in toc if clean_title(t)]
    base = sp.normalize_toc(toc, total_pages)
    if not base:
        return None
    cap = max(e["level"] for e in base)

    def at(c: int) -> list[dict]:
        # 🚨 同一頁的父子書籤兩個都留（《東方化革命》「正文」與「第一章」同頁，去重留父就丟了第一章）；
        #    穩定排序讓父在前，assign 取最後一個 start≤頁 的＝最深那層，build_chapter_path 補回祖先
        out = []
        for lv, t, pg in toc:
            if lv > c or sp._is_boilerplate_title(t):
                continue
            pg = max(1, min(int(pg or 1), total_pages or 10 ** 9))
            out.append({"level": int(lv), "title": t, "start_page": pg})
        out.sort(key=lambda e: (e["start_page"], e["level"]))
        return out

    same, deeper = at(cap), at(cap + 1)
    pages_d = len({e["start_page"] for e in deeper})
    if pages_d > len({e["start_page"] for e in same}) and total_pages / max(pages_d, 1) >= 2:
        return deeper
    return same


def assign(chunks: list[dict], entries: list[dict], japanese: bool) -> int:
    """依 page_number 標 chapter_path；回傳標到幾頁。"""
    paths = [sp.build_chapter_path(entries, k) for k in range(len(entries))]
    if not japanese:
        paths = [se.to_traditional(p) for p in paths]
    n = 0
    for c in chunks:
        if c.get("chunk_type") != "page" or not isinstance(c.get("page_number"), int):
            continue
        k = -1
        for j, e in enumerate(entries):
            if e["start_page"] <= c["page_number"]:
                k = j
            else:
                break
        if k >= 0:
            c["chapter_path"] = paths[k]
            n += 1
    return n


def main() -> int:
    import requests
    import translate_ebook_to_zh as te
    apply = "--apply" in sys.argv
    ids = [a for a in sys.argv[sys.argv.index("--ids") + 1:] if not a.startswith("--")] if "--ids" in sys.argv else None
    H = {"apikey": te.KEY, "Authorization": "Bearer " + te.KEY}
    paths, off = {}, 0
    while True:
        b = requests.get(te.URL + "/rest/v1/ebooks", headers=H, timeout=120, params={
            "select": "id,file_path", "file_type": "eq.pdf", "order": "id", "limit": "1000", "offset": str(off)}).json()
        paths.update({x["id"]: x["file_path"] for x in b if x.get("file_path")})
        if len(b) < 1000:
            break
        off += 1000
    files = [CH / f"{i}.jsonl" for i in ids] if ids else sorted(CH.glob("*.jsonl"))
    rep = open(ROOT / "output/toc_audit/bookmark_chapters.tsv", "w", encoding="utf-8")
    stat: dict[str, int] = {}
    for n, p in enumerate(files):
        try:
            chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception:  # noqa: BLE001
            continue
        if cp.eligible(chunks) != "no-chapters":
            continue
        fp = paths.get(p.stem)
        res = ""
        if not fp or not Path(fp).exists():
            res = "no-pdf"
        else:
            got = read_toc(fp)
            if got is None:
                res = "toc-read-failed"
            else:
                total, toc = got
                ent = entries_from_toc(toc, total) if toc else None
                if not ent:
                    res = "no-usable-bookmarks"
                else:
                    jp = se.book_is_japanese(c.get("content") or "" for c in chunks)
                    k = assign(chunks, ent, jp)
                    pages = sum(1 for c in chunks if c.get("chunk_type") == "page")
                    if k < 0.5 * pages:
                        res = f"low-coverage {k}/{pages}"
                    else:
                        new = cp.consolidate(chunks)
                        res = f"merged {len(chunks)}->{len(new)} ({len(ent)} 書籤)"
                        if apply:
                            bak = p.with_suffix(".jsonl.bak_chapters")
                            if not bak.exists():
                                shutil.copy2(p, bak)
                            out = se.write_jsonl(p.stem, new)
                            try:
                                se.push_to_r2(p.stem, out)
                                se.update_db(p.stem, new)
                            except Exception as e:  # noqa: BLE001
                                res += f" sync-failed {type(e).__name__}"
        key = res.split(" ")[0]
        stat[key] = stat.get(key, 0) + 1
        rep.write(f"{p.stem}\t{res}\n")
        rep.flush()
        if n % 200 == 0:
            print(n, stat, flush=True)
    print("SUMMARY", stat, flush=True)
    print("BOOKMARK_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
