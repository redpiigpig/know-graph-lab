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


def _split_notes(text: str) -> tuple[list[str], list[str]]:
    import re
    m = re.search(r"\n\n" + re.escape(rb.FOOT_RULE) + r"\n\n", text)
    body, notes = (text[:m.start()], text[m.end():]) if m else (text, "")
    items: list[str] = []
    for n in rb.paras(notes):
        if rc.FN_ITEM.match(n) or not items:
            items.append(n if rc.FN_ITEM.match(n) else f"(0) {n}")
        else:
            items[-1] += "\n\n" + n          # 沒配上註號的原註是接在前一條下的續段，跟著走、不可丟
    return body.split("\n\n"), items


def paginate_bilingual(c: dict) -> list[dict]:
    """中英對照頁（rebuild_reference_bilingual 產的，兩欄正文列數相等）：同一列一起切，每頁中文約五千字。
    中文註依 [^N] 所在頁分配，英文註（已配成相同註號）跟著同一頁。列數不等就不切。"""
    import re
    zb, zn = _split_notes(c.get("content") or "")
    eb, en = _split_notes(c.get("source_text") or "")
    if len(zb) != len(eb) or len(c.get("content") or "") <= rc.PAGE_MAX:
        return [c]
    pages: list[list[int]] = [[]]
    size = 0
    for i, z in enumerate(zb):
        sec = z.startswith("### ")
        if pages[-1] and ((sec and size >= 1500) or (not sec and size + len(z) > rc.PAGE_TARGET and size >= 800)):
            pages.append([])
            size = 0
        pages[-1].append(i)
        size += len(z)
    owner = {}
    for pi, rows in enumerate(pages):
        for i in rows:
            for n in re.findall(r"\[\^(\d+)\]", zb[i]):
                owner.setdefault(int(n), pi)
    num = lambda s: int(rc.FN_ITEM.match(s).group(1))  # noqa: E731
    out = []
    top = (c.get("chapter_path") or "").split(" / ")[0]
    path = c.get("chapter_path") or ""
    for pi, rows in enumerate(pages):
        zt = "\n\n".join(zb[i] for i in rows)
        et = "\n\n".join(eb[i] for i in rows)
        zns = [n for n in zn if owner.get(num(n), len(pages) - 1) == pi]
        ens = [n for n in en if owner.get(num(n), len(pages) - 1) == pi]
        zns = [n[4:] if n.startswith("(0) ") else n for n in zns]     # 拿掉臨時標記
        ens = [n[4:] if n.startswith("(0) ") else n for n in ens]
        if zns:
            zt += f"\n\n{rb.FOOT_RULE}\n\n" + "\n\n".join(zns)
        if ens:
            et += f"\n\n{rb.FOOT_RULE}\n\n" + "\n\n".join(ens)
        sec = re.match(r"### (.+)", zb[rows[0]])
        if pi and sec:
            path = f"{top} / {sec.group(1).strip()}"
        mk = re.search(r"\{\{p:(\d+)\}\}", zt)
        d = dict(c, content=zt, source_text=et, chapter_path=c.get("chapter_path") if pi == 0 else path)
        if pi and mk:
            d["printed_page"] = int(mk.group(1))
        out.append(d)
    return out


def repaginate(chunks: list[dict]) -> tuple[list[dict], int]:
    known = rb.printed_map(chunks)
    out, split = [], 0
    for c in chunks:
        t = c.get("content") or ""
        if len(t) <= rc.PAGE_MAX or c.get("sources"):
            out.append(c)
            continue
        if c.get("source_text"):
            pages = paginate_bilingual(c)
            split += len(pages) > 1
            out += pages
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
