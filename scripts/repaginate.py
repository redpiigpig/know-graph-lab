#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""已重建（一章一頁）的書再分頁成每頁約五千字（2026-10-01 使用者定：全館每頁約五千字）。

直接處理現行 JSONL（不從 .bak_restructure 重來），所以 relink_missing_footnotes 補過的註腳連結會保留。
只切單語頁（有 source_text／sources 的對照頁不動——兩欄要同步切，另行處理）；切法同
restructure_chapters.paginate：節優先、段落次之，段號不變，註釋跟著引用頁走。
守恆：去掉標記後的字數改前改後必須相等。寫檔先 .tmp 再換上，推 R2＋更新 DB，完成記 repaginate_done.txt。

  python -X utf8 scripts/repaginate.py [--apply] [--ids 檔]      # 不給 --ids＝所有有 .bak_restructure 的書
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_reference_bilingual as rb  # noqa: E402
import restructure_chapters as rc  # noqa: E402

CH = rb.CHUNKS
DONE = Path(__file__).resolve().parents[1] / "output" / "restructure" / "repaginate_done.txt"


def repaginate(chunks: list[dict]) -> tuple[list[dict], int]:
    known = rb.printed_map(chunks)
    out, split = [], 0
    for c in chunks:
        t = c.get("content") or ""
        if len(t) <= rc.PAGE_MAX or c.get("source_text") or c.get("sources"):
            out.append(c)
            continue
        pages = rc.paginate(t, c.get("chapter_path") or "", c, known)
        split += len(pages) > 1
        out += pages
    for i, c in enumerate(out):
        c["chunk_index"] = i
    return out, split


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids")
    a = ap.parse_args()
    import socket
    socket.setdefaulttimeout(120)
    import standardize_ebook as se
    if a.ids:
        ids = Path(a.ids).read_text(encoding="utf-8").split()
    else:
        ids = sorted(p.name.split(".")[0] for p in CH.glob("*.jsonl.bak_restructure"))
    done = set(DONE.read_text(encoding="utf-8").split()) if DONE.exists() else set()
    for bid in ids:
        if bid in done:
            continue
        src = CH / f"{bid}.jsonl"
        try:
            cs = [json.loads(l) for l in src.open(encoding="utf-8") if l.strip()]
            cs.sort(key=lambda c: c.get("chunk_index") or 0)
            out, split = repaginate(cs)
            if not split:
                print("SAME", bid, flush=True)
            elif rc.mass(cs) != rc.mass(out):
                print("SKIP", bid, f"守恆失敗 {rc.mass(cs)}→{rc.mass(out)}", flush=True)
                continue
            else:
                print("OK", bid, f"{len(cs)}→{len(out)} 頁", flush=True)
                if a.apply:
                    tmp = src.with_name(src.name + ".tmp")
                    with tmp.open("w", encoding="utf-8") as f:
                        for c in out:
                            f.write(json.dumps(c, ensure_ascii=False) + "\n")
                    os.replace(tmp, src)
                    se.push_to_r2(bid, src)
                    se.update_db(bid, out)
            if a.apply:
                with DONE.open("a", encoding="utf-8") as f:
                    f.write(bid + "\n")
        except Exception as e:  # noqa: BLE001
            print("ERR", bid, f"{type(e).__name__}: {str(e)[:120]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
