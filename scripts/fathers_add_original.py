#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替站上的教父卷補上第三欄「原文」（拉丁／希臘），成為 中文 / 英文 / 原文 三欄對照。

  python scripts/fathers_add_original.py --work augustine-confessions          # 只驗，不寫
  python scripts/fathers_add_original.py --work augustine-confessions --apply  # 寫回 JSONL

站上教父卷本來就是兩欄：content 是繁中精修，source_text 是 Schaff 英譯。本腳本
補的是第三欄原典，對齊靠古典分章（liber.caput），不做語意對齊。

流程：
  ① 抓原典 → 按 卷.章 切段（scripts/fathers_original.py 的純函式）
  ② **覆蓋率閘**：站上章節 vs 原典章節，缺章或多章一律先報出來
  ③ 逐段組裝 sources[原文語言]；範圍內任何一章缺就整段留白
  ④ --apply 才寫回 {id}.jsonl，並鏡射 source_text/source_lang 給舊的兩欄 reader

🚨 覆蓋率閘不是形式。首跑《懺悔錄》就靠它抓到站上卷一只到第 18 章、第 19–20 章
   中英文都不存在。沒有閘的話那兩章拉丁文會被併進第 18 章那一段，三欄看起來齊、
   內容從那裡開始錯位，而畫面上完全看不出來。

🚨 只讀寫 {id}.jsonl。同目錄下的 .en.bak.jsonl 與 .bak_pre_merge 是翻譯前的英文
   原檔，段數對不上（Augustine Confessions 正式檔 68 段、英文備份 481 段）。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fathers_original", ROOT / "scripts" / "fathers_original.py")
FO = importlib.util.module_from_spec(_spec)
sys.modules["fathers_original"] = FO
_spec.loader.exec_module(FO)


# ── 取源登錄 ────────────────────────────────────────────────────────────────
# 每一部著作登記：站上是哪一本 ebook、原文語言、原典從哪裡抓、每卷幾章。
# `chapters` 是原典的權威章數，用來判站上有沒有缺章——不可以拿站上的章數回填。
# `mode` 決定原典怎麼切、又怎麼放進中譯的段落格：
#   paragraph — 原典帶 `卷.章.節` 行標，中譯段落也帶同一組節號 → 逐節對齊（最細）
#   chapter   — 原典只有 `[I]` 這種章號，中譯只有「第N章」標題 → 逐章對齊（較粗）
#   greek     — 原典是 Migne PG 掃描本的自家 OCR 帳本（scripts/fathers_pg_ocr.py），
#               ΛΟΓΟΣ 分卷、α΄ β΄ γ΄ 分節，節號與中英譯的 1. 2. 是同一套編次 → 逐節
# 三種都不猜：對不上就留空。
WORKS: dict[str, dict] = {
    "augustine-confessions": {
        "label": "奧古斯丁《懺悔錄》",
        "ebook_id": "9edb7c37-4231-412b-83bd-78f3f793cc0a",
        "prefix": "懺悔錄",
        "lang": "la",
        "mode": "paragraph",
        "urls": [f"https://www.thelatinlibrary.com/augustine/conf{b}.shtml"
                 for b in range(1, 14)],
        "chapters": {1: 20, 2: 10, 3: 12, 4: 16, 5: 14, 6: 16, 7: 21,
                     8: 12, 9: 13, 10: 43, 11: 31, 12: 32, 13: 38},
        "source": "The Latin Library（Corpus Christianorum 系 Verheijen 校本，公有領域）",
    },
    "augustine-city-of-god": {
        "label": "奧古斯丁《上帝之城》",
        "ebook_id": "1eb50be9-34ac-4ce3-874d-1280975851fc",
        "prefix": "上帝之城",
        "lang": "la",
        "mode": "chapter",
        "urls": [f"https://www.thelatinlibrary.com/augustine/civ{b}.shtml"
                 for b in range(1, 23)],
        "source": "The Latin Library（Dombart–Kalb 校本，公有領域）",
    },
    "chrysostom-de-sacerdotio": {
        "label": "金口若望《論司祭職》",
        "ebook_id": "76df31fe-e732-4aa6-88c2-d650a09fb688",
        "prefix": "論司祭職",
        "lang": "grc",
        "mode": "greek",
        "ledger": "output/source-cache/pg-greek-ocr/pg48-de-sacerdotio.jsonl",
        # 站上這一部切成「論司祭職 第3章」…「第8章」，其實是六卷正文；前兩段是
        # 書名頁與導論。第N章 → 卷 N-2。
        "book_from_chapter": -2,
        "source": "Migne PG 48.623–692 掃描本，Gemini Vision 逐欄 OCR",
    },
}

# 🚨 《論三位一體》拉丁原文有（thelatinlibrary.com/augustine/trin1–15），但站上那一冊
#    （NPNF1 Vol 3, d7f66759-3fa9-4633-abde-87003cdbcc06）把它和《創世記字義解》等
#    併成一個「奧古斯丁教義論集」，共用同一組卷號，從 chapter_path 分不出哪一卷屬
#    哪一部。硬接會把《創世記字義解》的中譯配上《論三位一體》的拉丁文——三欄看起來
#    齊，內容卻是兩部不同的書。要收這一部，得先把那一冊重新分篇。


def load_greek_ledger(path: Path) -> dict[tuple[int | None, int], str]:
    """讀 fathers_pg_ocr.py 的帳本，按頁與欄的閱讀順序接稿，再切成 {(卷,節): 文字}。"""
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    order = {"c0h0": 0, "c0h1": 1, "c1h0": 2, "c1h1": 3}
    rows.sort(key=lambda r: (r["page"], order.get(r["crop"], 9)))
    text = FO.join_crops([r["text"] for r in rows])
    pages = len({r["page"] for r in rows})
    print(f"  OCR 帳本 {len(rows)} 塊 / {pages} 頁 → {len(text)} 字")
    return FO.parse_greek_sections(text)


def fetch_original(spec: dict) -> tuple[dict, dict]:
    """抓原典。回傳 (逐章 {(卷,章): 文字}, 逐節 {(卷,節): 文字})。

    chapter 模式沒有節，第二項是空的。
    """
    if spec["mode"] == "greek":
        paragraphs = load_greek_ledger(Path(spec["ledger"]))
        return {}, paragraphs
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (know-graph-lab fathers-original)"
    chapters: dict[tuple[int | None, int], str] = {}
    sections: dict[tuple[int | None, int, int | None], str] = {}
    unit = "章" if spec["mode"] == "chapter" else "節"
    for i, url in enumerate(spec["urls"], 1):
        r = s.get(url, timeout=45)
        r.raise_for_status()
        text = FO.strip_html(r.text)
        if spec["mode"] == "paragraph":
            got = FO.parse_numbered_text(text, default_book=i)
            sections.update(got)
        else:
            got = FO.parse_bracketed_chapters(text, i)
            chapters.update(got)
        print(f"  抓 {url.rsplit('/', 1)[-1]:16} → {len(got)} {unit}")
    if spec["mode"] == "paragraph":
        chapters = FO.by_chapter(sections)
    return chapters, FO.by_paragraph(sections)


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, choices=sorted(WORKS))
    ap.add_argument("--chunks-dir", default=None)
    ap.add_argument("--apply", action="store_true", help="寫回 JSONL（預設只驗不寫）")
    a = ap.parse_args()

    spec = WORKS[a.work]
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))
    raw = a.chunks_dir or os.environ.get("EBOOK_CHUNKS_DIR") or ""
    # 🚨 別偷懶寫 Path(raw).is_dir()——Path("") 等於「.」，在 Windows 上是存在的，
    # 環境變數沒讀到時會安靜地把工作目錄當成 chunks 目錄，然後報「找不到檔案」。
    if not raw:
        print("EBOOK_CHUNKS_DIR 沒設（.env 讀不到？）")
        return 1
    chunks_dir = Path(raw)
    if not chunks_dir.is_dir():
        print(f"找不到 chunks 目錄 {chunks_dir}（Drive 沒掛？）")
        return 1
    path = chunks_dir / f"{spec['ebook_id']}.jsonl"
    if not path.exists():
        print(f"找不到 {path}")
        return 1

    print(f"《{spec['label']}》 原文 {spec['lang']} ← {spec['source']}"
          f"（{'逐章' if spec['mode'] == 'chapter' else '逐節'}對齊）")
    chapters, paragraphs = fetch_original(spec)
    print(f"原典共 {len(chapters)} 章"
          + (f" / {len(paragraphs)} 節" if paragraphs else "") + "\n")

    chunks = load_chunks(path)
    spans: dict[int, FO.Span] = {}
    for c in chunks:
        cp = c.get("chapter_path") or ""
        if not cp.startswith(spec["prefix"]):
            continue
        # 「卷二」整卷一段時要餵該卷章數才解得出範圍
        book_hint = None
        m = FO.CHAPTER_PATH.search(cp)
        if m and m.group(2) is None:
            book_hint = (spec.get("chapters") or {}).get(FO.zh_numeral(m.group(1)))
        s = FO.parse_chapter_path(cp, chapters_in_book=book_hint)
        if s and spec["mode"] == "greek":
            # 這一部的 chapter_path 是「論司祭職 第3章」，第 N 章其實是第 N-2 卷
            s = FO.Span(s.first + spec["book_from_chapter"], s.first, s.last)
            if s.book < 1:
                continue
        if s:
            spans[c["chunk_index"]] = s

    print(f"站上可對齊段落 {len(spans)} / 全書 {len(chunks)} 段")

    if spec["mode"] == "greek":
        # 沒有章這一層，覆蓋率就看節：原典有而站上中譯沒有的節，一樣要報出來。
        by_book: dict[int | None, set[int]] = {}
        for (b, n) in paragraphs:
            by_book.setdefault(b, set()).add(n)
        found = []
        for c in chunks:
            s = spans.get(c["chunk_index"])
            if not s:
                continue
            for p in FO.split_body(c.get("content") or ""):
                m = FO.LEADING_NO.match(p)
                if m:
                    found.append(FO.Span(s.book, int(m.group(1)), int(m.group(1))))
        covs = FO.coverage(found, {k: "x" for k in paragraphs})
    elif spec["mode"] == "chapter":
        # 章模式的覆蓋率要看「內文裡真的出現的章標題」，不要看 chapter_path 的範圍
        # 標籤——標籤會湊整（該卷只到第 35 章，標籤照樣寫「第31-40章」），拿它比對
        # 會冒出一堆不存在的「多出章」，把真正的缺章淹掉。
        found: list[FO.Span] = []
        for c in chunks:
            s = spans.get(c["chunk_index"])
            if not s:
                continue
            for p in FO.split_body(c.get("content") or ""):
                m = FO.ZH_CHAPTER_HEAD.match(p)
                n = FO.zh_numeral(m.group(1)) if m else None
                if n is not None:
                    found.append(FO.Span(s.book, n, n))
        covs = FO.coverage(found, chapters)
    else:
        covs = FO.coverage(list(spans.values()), chapters)
    bad = [c for c in covs if not c.ok]
    print(f"\n覆蓋率閘：{len(covs) - len(bad)} / {len(covs)} 卷齊全")
    for c in bad:
        parts = []
        if c.missing:
            parts.append(f"站上中譯沒有第 {c.missing} 章")
        if c.extra:
            # 這一側是原典電子本的缺口，不是我們的問題——civ18 那頁就從 [XXXI]
            # 直接跳到 [XLVII]，中間 15 章根本沒收。分開講才不會誤判責任歸屬。
            parts.append(f"原典電子本沒有第 {c.extra} 章")
        print(f"  ⚠ 卷 {c.book}：" + "；".join(parts))

    done = 0
    hit_total = num_total = 0
    updated: list[dict] = []
    for c in chunks:
        s = spans.get(c["chunk_index"])
        if not s:
            updated.append(c)
            continue
        body = FO.split_body(c.get("content") or "")
        if spec["mode"] in ("paragraph", "greek"):
            col, hit, numbered = FO.align_by_paragraph_number(body, s.book, paragraphs)
        else:
            col, hit, numbered = FO.align_by_chapter_heading(body, s.book, chapters)
        hit_total += hit
        num_total += numbered
        if not hit:
            # 一個錨點都對不上 → 這一段的編號體系跟原典不一致，別硬塞
            print(f"  ⚠ 「{c['chapter_path']}」{numbered} 個錨點全對不上，跳過")
            updated.append(c)
            continue
        if hit < numbered:
            print(f"  · 「{c['chapter_path']}」{hit}/{numbered} 個錨點配到原文，其餘留白")
        sources, order = FO.build_sources(
            c.get("sources"), c.get("source_text"), c.get("source_lang"),
            FO.render_column(col), spec["lang"])
        updated.append({**c, "sources": sources, "source_order": order,
                        # 舊的兩欄 reader 讀 source_text/source_lang，主欄仍是英譯
                        "source_lang": order[0], "source_text": sources[order[0]]})
        done += 1

    pct = f"{hit_total / num_total:.0%}" if num_total else "—"
    print(f"\n補上原文欄 {done} 段；逐節命中 {hit_total} / {num_total}（{pct}）")

    if not a.apply:
        print("\n（只驗不寫。確認無誤後加 --apply）")
        return 0

    backup = path.with_suffix(".jsonl.bak_pre_original")
    if not backup.exists():
        shutil.copy2(path, backup)
        print(f"備份 → {backup.name}")
    path.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in updated) + "\n",
        encoding="utf-8")
    print(f"寫回 {path.name}（{len(updated)} 段）")
    print("🚨 線上還要把 JSONL 推到 R2 才會生效（見 server/utils/ebook-chunks.ts）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
