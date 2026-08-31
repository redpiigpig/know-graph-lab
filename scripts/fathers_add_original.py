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
#   roman     — 原典行標是 `I. [1] …`（行首羅馬章號＋章內方括號節號），中譯只有
#               「第N章」標題 → 逐章對齊。特土良全集那一系。
# 四種都不猜：對不上就留空。
#
# 一冊裡收了好幾部各自獨立的著作時（特土良那冊 23 部），用 `parts` 逐部登記：
# 每部有自己的 chapter_path 前綴與原典網址，章號各自從一起算，不可混在一起。
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
    "tertullian-anf3": {
        "label": "特土良（ANF 第三卷）",
        "ebook_id": "364dac2e-410f-4906-be63-8bb86b4865ee",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        # 站上那一冊逐部切得很乾淨，每部都對得到 The Latin Library 的一篇。
        "parts": [(zh, f"https://www.thelatinlibrary.com/tertullian/tertullian.{slug}.shtml")
                  for zh, slug in (
                      ("特土良護教辭", "apol"),
                      ("特土良論偶像崇拜", "idololatria"),
                      ("特土良論觀劇", "spect"),
                      ("特土良論花冠", "corona"),
                      ("特土良致斯卡普拉", "scapulam"),
                      ("特土良致萬民", "nationes1"),
                      ("特土良致萬民", "nationes2"),
                      ("特土良駁猶太人", "iudaeos"),
                      ("特土良論靈魂的見證", "testimonia"),
                      ("特土良論靈魂", "anima"),
                      ("特土良駁異端的時效", "praescrip"),
                      ("特土良駁馬吉安", "marcionem1"),
                      ("特土良駁馬吉安", "marcionem2"),
                      ("特土良駁馬吉安", "marcionem3"),
                      ("特土良駁馬吉安", "marcionem4"),
                      ("特土良駁馬吉安", "marcionem5"),
                      ("特土良駁黑摩根", "herm"),
                      ("特土良駁瓦倫廷派", "valentinianos"),
                      ("特土良論基督的肉身", "carne"),
                      ("特土良論肉身復活", "resurrectione"),
                      ("特土良駁普拉克西亞斯", "praxean"),
                      ("特土良蝎傷解毒劑", "scorpiace"),
                      ("特土良駁諸異端附錄", "haereses"),
                      ("特土良論悔改", "paen"),
                      ("特土良論洗禮", "baptismo"),
                      ("特土良論禱告", "oratione"),
                      ("特土良致殉道者", "martyres"),
                      ("特土良論忍耐", "patientia"),
                  )],
    },
    "anf4-latin": {
        "label": "ANF 第四卷的拉丁篇（特土良後期著作＋密努修＋科摩狄安）",
        "ebook_id": "904661d3-16fc-4f37-bb04-f7c4aa7671e9",
        "lang": "la",
        "mode": "roman",
        "source": "The Latin Library（公有領域）",
        # 🚨 同一冊的俄利根八卷《駁塞爾蘇斯》與《論原理》是希臘文，要走 PG 掃描本
        #    的 OCR（見 fathers_pg_ocr.py），這裡只收拉丁的部分。
        # 🚨 兩部拉丁原文有、卻對不起來，先不收：
        #    ·《論逼迫中逃避》—— 站上那一整部塞在單一段落裡（465 個段落），
        #      一個「第N章」標題都沒有，我方沒有錨點可用。要收得先重新分章。
        #    ·科摩狄安《教誨集》—— 拉丁本（commodianus2）的每首詩只有詩題沒有
        #      編號，而中譯用 ANF 的章號。兩邊沒有共同的鍵，只能靠第幾首的次序
        #      硬對，那是另一種對齊機制。
        "parts": [
                      ("特土良《論婦女裝飾》", "https://www.thelatinlibrary.com/tertullian/tertullian.cultu1.shtml"),
                      ("特土良《論婦女裝飾》", "https://www.thelatinlibrary.com/tertullian/tertullian.cultu2.shtml"),
                      ("特土良《致妻書》", "https://www.thelatinlibrary.com/tertullian/tertullian.uxor1.shtml"),
                      ("特土良《致妻書》", "https://www.thelatinlibrary.com/tertullian/tertullian.uxor2.shtml"),
                      ("特土良《論貞女蒙頭》", "https://www.thelatinlibrary.com/tertullian/tertullian.virginibus.shtml"),
                      ("特土良《勸貞潔書》", "https://www.thelatinlibrary.com/tertullian/tertullian.castitatis.shtml"),
                      ("特土良《論獨婚》", "https://www.thelatinlibrary.com/tertullian/tertullian.monog.shtml"),
                      ("特土良《論貞操》", "https://www.thelatinlibrary.com/tertullian/tertullian.pudicitia.shtml"),
                      ("特土良《論禁食》", "https://www.thelatinlibrary.com/tertullian/tertullian.ieiunio.shtml"),
                      ("特土良《論披袍》", "https://www.thelatinlibrary.com/tertullian/tertullian.pallio.shtml"),
                      ("密努修《屋大維對話錄》", "https://www.thelatinlibrary.com/minucius.html"),
        ],
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
    """抓原典。回傳 (逐章, 逐節, 逐卷逐章)。

    第三項只有多卷的 roman 模式用得到：原典每卷的章號都從一起算，而中譯有兩種
    習慣——《駁馬吉安》整部連續編號 1–145，《論婦女裝飾》卻每卷從第一章重來。
    機器分不出是哪一種，所以兩種鍵都備好，對齊時各試一次、取命中高的那個。
    """
    if spec["mode"] == "greek":
        paragraphs = load_greek_ledger(Path(spec["ledger"]))
        return {}, paragraphs, {}
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (know-graph-lab fathers-original)"
    chapters: dict[tuple[int | None, int], str] = {}
    by_book: dict[tuple[int | None, int], str] = {}
    sections: dict[tuple[int | None, int, int | None], str] = {}
    unit = "章" if spec["mode"] == "chapter" else "節"
    for i, url in enumerate(spec["urls"], 1):
        r = s.get(url, timeout=45)
        r.raise_for_status()
        text = FO.strip_html(r.text)
        if spec["mode"] == "paragraph":
            got = FO.parse_numbered_text(text, default_book=i)
            sections.update(got)
        elif spec["mode"] == "roman":
            got = FO.parse_chapter_markers(text)
            # 多卷的著作（《駁馬吉安》五卷、《致萬民》兩卷）原典每卷的章號都從
            # 一重新起算，但站上的中譯是整部連續編號（駁馬吉安 29+29+24+43+20
            # ＝145，正好是中譯的 1–145）。所以第二卷起要接著前面累計的章數。
            base = max((k[1] for k in chapters), default=0)
            by_book.update({(i, k[1]): v for k, v in got.items()})
            got = {(None, k[1] + base): v for k, v in got.items()}
            chapters.update(got)
        else:
            got = FO.parse_bracketed_chapters(text, i)
            chapters.update(got)
        print(f"  抓 {url.rsplit('/', 1)[-1]:16} → {len(got)} {unit}")
    if spec["mode"] == "paragraph":
        chapters = FO.by_chapter(sections)
    return chapters, FO.by_paragraph(sections), by_book


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def align_part(chunks, spans, chapters, by_book):
    """對整部做逐章對齊，兩種編號法各試一次，取命中高的那個。

    多卷著作的中譯有兩種編號習慣，同一冊裡都有：《駁馬吉安》五卷整部連續編號
    1–145（→ 用累計後的 chapters），《論婦女裝飾》兩卷每卷從第一章重來（→ 用
    逐卷的 by_book，卷次靠章號回頭偵測）。機器分不出是哪一種，所以兩種都跑，
    看誰命中多。猜錯的那一種通常是 0 命中，差距非常明顯。
    """
    seq = []
    for c in chunks:
        if c["chunk_index"] not in spans:
            continue
        body = FO.split_body(c.get("content") or "")
        for i, n in FO.chapter_headings(body):
            seq.append((c["chunk_index"], i, n))
    if not seq:
        return {}, 0, 0

    flat: dict[int, list] = {}
    n_flat = 0
    for ci, i, n in seq:
        text = chapters.get((None, n)) or chapters.get((1, n))
        if text:
            flat.setdefault(ci, []).append((i, text))
            n_flat += 1

    per: dict[int, list] = {}
    n_per = 0
    for (ci, i, n), b in zip(seq, FO.book_of([n for _, _, n in seq])):
        text = by_book.get((b, n))
        if text:
            per.setdefault(ci, []).append((i, text))
            n_per += 1

    hits, n_hit = (per, n_per) if n_per > n_flat else (flat, n_flat)
    return hits, n_hit, len(seq)


def parts_of(spec: dict) -> list[tuple[str, dict]]:
    """把 spec 正規化成 [(chapter_path 前綴, 該部的 spec)]。單一著作就是一部。

    同一個前綴登記多個網址＝那一部原典分成好幾卷（《駁馬吉安》五卷）。這裡要
    把它們併成同一部再交出去——拆成好幾部的話，每一卷的章號都會從一重新起算，
    而站上的中譯是整部連續編號，第二卷起就全部對不上。
    """
    if "parts" not in spec:
        return [(spec["prefix"], spec)]
    grouped: dict[str, list[str]] = {}
    for prefix, url in spec["parts"]:
        grouped.setdefault(prefix, []).append(url)
    return [(prefix, {**spec, "prefix": prefix, "urls": urls})
            for prefix, urls in grouped.items()]


def spans_for(chunks: list[dict], part: dict) -> dict[int, FO.Span]:
    out: dict[int, FO.Span] = {}
    for c in chunks:
        cp = c.get("chapter_path") or ""
        if not cp.startswith(part["prefix"]):
            continue
        # 「卷二」整卷一段時要餵該卷章數才解得出範圍
        book_hint = None
        m = FO.CHAPTER_PATH.search(cp)
        if m and m.group(2) is None:
            book_hint = (part.get("chapters") or {}).get(FO.zh_numeral(m.group(1)))
        s = FO.parse_chapter_path(cp, chapters_in_book=book_hint)
        if s and part["mode"] == "greek":
            # 這一部的 chapter_path 是「論司祭職 第3章」，第 N 章其實是第 N-2 卷
            s = FO.Span(s.first + part["book_from_chapter"], s.first, s.last)
            if s.book < 1:
                continue
        if s:
            out[c["chunk_index"]] = s
    return out


def coverage_for(chunks: list[dict], spans: dict[int, FO.Span], part: dict,
                 chapters: dict, paragraphs: dict) -> list:
    """依模式挑對的比對層級。

    🚨 章模式不可以拿 chapter_path 的範圍標籤當「站上有哪些章」——標籤會湊整
       （該卷只到第 35 章，標籤照樣寫「第31-40章」），拿它比對會冒出一堆不存在的
       「多出章」，把真正的缺章淹掉。要數內文裡真的出現的章標題。
    """
    if part["mode"] == "greek":
        found = []
        for c in chunks:
            s = spans.get(c["chunk_index"])
            if not s:
                continue
            for p in FO.split_body(c.get("content") or ""):
                m = FO.LEADING_NO.match(p)
                if m:
                    found.append(FO.Span(s.book, int(m.group(1)), int(m.group(1))))
        return FO.coverage(found, {k: "x" for k in paragraphs})
    if part["mode"] in ("chapter", "roman"):
        found = []
        for c in chunks:
            s = spans.get(c["chunk_index"])
            if not s:
                continue
            for p in FO.split_body(c.get("content") or ""):
                m = FO.ZH_CHAPTER_HEAD.match(p)
                n = FO.zh_numeral(m.group(1)) if m else None
                if n is not None:
                    found.append(FO.Span(s.book, n, n))
        return FO.coverage(found, chapters)
    return FO.coverage(list(spans.values()), chapters)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, choices=sorted(WORKS))
    ap.add_argument("--chunks-dir", default=None)
    ap.add_argument("--apply", action="store_true", help="寫回 JSONL（預設只驗不寫）")
    ap.add_argument("--only", help="只跑某一部（chapter_path 前綴），試跑用")
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

    parts = parts_of(spec)
    if a.only:
        parts = [x for x in parts if x[0] == a.only]
        if not parts:
            print(f"沒有前綴為「{a.only}」的部")
            return 1
    print(f"《{spec['label']}》 原文 {spec['lang']} ← {spec['source']}"
          f"（{'逐章' if spec['mode'] in ('chapter', 'roman') else '逐節'}對齊）"
          + (f"，共 {len(parts)} 部" if len(parts) > 1 else ""))

    chunks = load_chunks(path)
    cols: dict[int, list[str]] = {}
    hit_total = num_total = 0
    skipped: list[str] = []
    for prefix, part in parts:
        chapters, paragraphs, by_book = fetch_original(part)
        spans = spans_for(chunks, part)
        if not spans:
            print(f"  ⚠ 「{prefix}」站上找不到對應段落，跳過")
            continue
        bad = [c for c in coverage_for(chunks, spans, part, chapters, paragraphs)
               if not c.ok]
        note = ""
        for c in bad:
            bits = []
            if c.missing:
                bits.append(f"站上中譯沒有第 {c.missing} 章")
            if c.extra:
                # 這一側是原典電子本的缺口，不是我們的問題——civ18 那頁就從
                # [XXXI] 直接跳到 [XLVII]，中間 15 章根本沒收。分開講才不會
                # 誤判責任歸屬。
                bits.append(f"原典電子本沒有第 {c.extra} 章")
            note += "\n      ⚠ 卷 " + str(c.book) + "：" + "；".join(bits)

        hit = num = 0
        if part["mode"] in ("paragraph", "greek"):
            for c in chunks:
                sp = spans.get(c["chunk_index"])
                if not sp:
                    continue
                body = FO.split_body(c.get("content") or "")
                col, h, n = FO.align_by_paragraph_number(body, sp.book, paragraphs)
                hit += h
                num += n
                if h:
                    cols[c["chunk_index"]] = col
                else:
                    skipped.append(f"{c['chapter_path']}（{n} 個錨點全對不上）")
        else:
            placed, hit, num = align_part(chunks, spans, chapters, by_book)
            for c in chunks:
                if c["chunk_index"] not in spans:
                    continue
                got = placed.get(c["chunk_index"])
                size = len(FO.split_body(c.get("content") or ""))
                if got:
                    cols[c["chunk_index"]] = FO.fill_column(size, got)
                else:
                    skipped.append(f"{c['chapter_path']}（錨點全對不上）")
        hit_total += hit
        num_total += num
        pct = f"{hit / num:.0%}" if num else "—"
        print(f"  {prefix:22} 段 {len(spans):3}  命中 {hit:4}/{num:<4} {pct:>4}{note}")

    updated: list[dict] = []
    for c in chunks:
        col = cols.get(c["chunk_index"])
        if not col:
            updated.append(c)
            continue
        sources, order = FO.build_sources(
            c.get("sources"), c.get("source_text"), c.get("source_lang"),
            FO.render_column(col), spec["lang"])
        updated.append({**c, "sources": sources, "source_order": order,
                        # 舊的兩欄 reader 讀 source_text/source_lang，主欄仍是英譯
                        "source_lang": order[0], "source_text": sources[order[0]]})

    pct = f"{hit_total / num_total:.0%}" if num_total else "—"
    print(f"\n補上原文欄 {len(cols)} 段；錨點命中 {hit_total} / {num_total}（{pct}）")
    if skipped:
        print(f"錨點全對不上而跳過的 {len(skipped)} 段：")
        for x in skipped[:12]:
            print(f"  · {x}")
        if len(skipped) > 12:
            print(f"  …另外 {len(skipped) - 12} 段")

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
