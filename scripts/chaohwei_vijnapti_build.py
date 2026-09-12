#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《初期唯識思想——瑜伽行派形成之脈絡》OCR 快取 → 昭慧法師全集（/collected-works）。

釋昭慧著，法界出版社 2001（民國九十年），為印順導師祝壽的「人間佛教‧薪火相傳」
學術研討會而出版。原稿是作者民國八十一年起在華雨寺講的「唯識學概論」講座紀錄，
由印悅法師整理、悟殷法師校訂增補出處。**作者授權製作電子版**（使用者已取得）。

pipeline ②（單一語言）：本即繁體中文，零翻譯零跨語對齊。與《心靈的交會》的差別
在版式 —— 這本是**直排論著**、頁碼印中文數字、腳註多且常跨頁，沒有發言人。
純函式共用 `chaohwei_build`（全形標點、腳註、接行、章別、頁碼帳都在那邊）。

📄 頁碼：每一段掛原書印刷頁碼當 `anchors[i]`。🚨 本書前面三段（出版前言／自序／
目次）各自從 1 編起，與正文的 1–280 撞號，所以卷首的錨點一律加前綴（`自序3`），
不然頁碼帳會把它們當成正文同號頁的「重複」而丟掉真正的頁。

  python -X utf8 scripts/chaohwei_vijnapti_build.py --audit
  python -X utf8 scripts/chaohwei_vijnapti_build.py --inspect
  python -X utf8 scripts/chaohwei_vijnapti_build.py --upload
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import chaohwei_build as cb  # noqa: E402

EBOOK_ID = "c4a01957-0000-4000-8000-000000000002"
TITLE = "初期唯識思想——瑜伽行派形成之脈絡"
AUTHOR = "釋昭慧"
PUBLISHER_YEAR = 2001
CACHE = "c:/tmp/chaohwei_vijnapti/ocr"
WORK = "c:/tmp/chaohwei_vijnapti/work.pdf"

BODY_START_WP = 18  # 掃描頁 18 ＝ 正文印刷頁 1（前面是前言／自序／目次）

# 卷首三段各自從 1 編頁 —— 用掃描頁區間分段，並替頁碼加前綴。區間是逐頁看過
# OCR 的 header 與內容定出來的，不是猜的：wp1 是出版前言的**最後一頁**（頁 8），
# wp2–7 是自序頁 1–6，wp8–16 是目次頁 1–9。
# 使用者定調（2026-09-12）：**出版前言不收**。掃描本也只有它的最後一頁（頁 8），
# 收進來是半截。wp1 整頁排除，不是只從章名表拿掉 —— 只拿掉章名的話那一頁會掉進
# 隔壁章，而且它的頁碼「8」沒了前綴就會跟正文第 8 頁撞號。
SKIP_WP: set[int] = {1}

FRONT_MATTER: list[dict] = [
    {"title": "自序", "wp": (2, 7), "prefix": "自序"},
    {"title": "目次", "wp": (8, 16), "prefix": "目次"},
]

# 章名與起始頁 —— 照書上的「目次」頁抄，再逐章拿正文頁眉與該頁的章標題驗過。
# 🚨 目次那一頁的 OCR 把參考資料的訖頁「一一八」讀成「一二八」，與肆的起頁
# 一一九 相衝；以正文為準（參考資料的頁眉到頁 117，肆的標題出現在頁 119）。
CHAPTERS: list[dict] = [
    {"title": "自序", "start": "自序1", "end": "自序6"},
    {"title": "目次", "start": "目次1", "end": "目次9"},
    {"title": "壹　緒論", "start": "1", "end": "12"},
    {"title": "貳　研究方法論", "start": "13", "end": "78"},
    {"title": "參　參考資料", "start": "79", "end": "118"},
    {"title": "肆　根本佛法與唯識學——「心爲主導性」的思考脈絡", "start": "119", "end": "162"},
    {"title": "伍　簡述唯識思想史", "start": "163", "end": "176"},
    {"title": "陸　無常、無我之問題探索", "start": "177", "end": "198"},
    {"title": "柒　部派思想與唯識學", "start": "199", "end": "248"},
    {"title": "捌　性空大乘與唯識學", "start": "249", "end": "272"},
    {"title": "結論", "start": "273", "end": "274"},
    {"title": "參考書目", "start": "275", "end": "280"},
]


# ── 純函式（零 I/O，scripts/tests/test_chaohwei_vijnapti_build.py 鎖定）────────

def prefix_front_matter(records: list[dict],
                        sections: list[dict] = None,
                        body_start: int = BODY_START_WP) -> list[dict]:
    """替卷首各段的印刷頁碼加上段名前綴（`3` → `自序3`）。回傳新的 record list。

    本書的出版前言、自序、目次各自從 1 編頁，正文又從 1 編起，同一個「頁 3」
    在書上出現四次。不分命名空間的話：頁碼帳會判成重複而丟掉三頁真頁，
    而讀者看到的引用號也分不出是哪一個第 3 頁。
    """
    sections = FRONT_MATTER if sections is None else sections
    out: list[dict] = []
    for r in records:
        wp = r["work_page"]
        if wp >= body_start:
            out.append(r)
            continue
        sec = next((s for s in sections if s["wp"][0] <= wp <= s["wp"][1]), None)
        printed = (r.get("printed") or "").strip()
        out.append({**r, "printed": f"{sec['prefix']}{printed}" if sec and printed else printed})
    return out


def drop_leading_chapter_title(units: list[tuple], chapters: list[dict]) -> list[tuple]:
    """章開頭那幾段若拼起來就是章名，刪掉 —— `split_chapters` 已經寫了 `## 章名`。

    本書每章第一頁的頁首就印著章標題（「貳　研究方法論」），而章首頁沒有頁眉，
    `drop_repeated_header` 那一關比對的是 header 欄，接不到這一種。

    比對要**逐段累加**：長標題在書上是折成兩行印的（「肆根本佛法與唯識學」＋
    「——「心為主導性」的思考脈絡」），只比第一段的話會漏掉後半，
    於是章名的下半截就孤零零地留在正文最前面。
    """
    heads: dict[int, str] = {}
    for _, _, idx in units:
        if 0 <= idx < len(chapters):
            heads.setdefault(idx, cb._title_key(chapters[idx]["title"]))
    out: list[tuple] = []
    acc: dict[int, str] = {}
    done: set[int] = set()
    for anchor, para, idx in units:
        key = heads.get(idx)
        if key and idx not in done:
            nxt = acc.get(idx, "") + cb._title_key(para)
            if nxt and key.startswith(nxt):
                acc[idx] = nxt
                if nxt == key:
                    done.add(idx)
                continue  # 這一段還在標題範圍內 → 丟掉
            done.add(idx)  # 接不下去了，從這一段起都是正文
        out.append((anchor, para, idx))
    return out


# 節標題的三層編號樣式。㈠㈡ 是 OCR 對「（一）（二）」的另一種讀法，兩種都要認。
_HEAD_PATS: list[tuple[int, "re.Pattern"]] = [
    (1, re.compile(r"^[一二三四五六七八九十]{1,3}、\s*")),
    (2, re.compile(r"^(?:[（(][一二三四五六七八九十]{1,3}[）)]|[㈠-㈩㉑-㉟])\s*")),
    (3, re.compile(r"^\d{1,2}[.、]\s*")),
]
_TOC_ENTRY_RE = re.compile(r"／[〇一二三四五六七八九十百]+(?:——[〇一二三四五六七八九十百]+)?")


def toc_keys(toc_text: str) -> dict[str, tuple[int, str]]:
    """目次頁的文字 → {節標題正規化鍵: (層級, 目次上印的編號)}。

    目次每一條長成「一、傳統研究法／一三」，`／` 後面是中文數字頁碼。書上目次是
    這本書自己列的權威節標題表，拿它當白名單比任何 regex 都可靠
    —— 與 `CHAPTERS` 照抄目次是同一個道理。層級也直接取自目次的編號樣式。
    """
    keys: dict[str, tuple[int, str]] = {}
    for raw in (toc_text or "").replace("\n", "／\n").split("\n"):
        for piece in _TOC_ENTRY_RE.split(raw):
            piece = piece.strip()
            for lv, rx in _HEAD_PATS:
                m = rx.match(piece)
                if m:
                    k = cb._title_key(piece[m.end():])
                    if k:
                        keys.setdefault(k, (lv, m.group(0).strip()))
                    break
    return keys


def heading_level(para: str, keys: dict[str, tuple[int, str]], max_len: int = 24) -> int | None:
    """這一段是不是節標題？是就回傳層級 1/2/3，不是就 None。

    🚨 光看編號樣式會大量誤判：書裡的散文列舉也長成「一、細心相續：特別與唯識學
    中阿陀那識執受根身……有關。」，自序末尾的日期「九十、三、十九」也一樣。
    所以兩道閘都要過：

    1. **目次白名單**——標題文字出現在書上的目次頁，就直接認（長度不限，
       目次裡本來就有長標題）。
    2. 目次沒有的（目次 OCR 有漏字，例如正文的「現代佛教教學研究法」目次讀成
       「現代佛教學研究法」）退而求其次：夠短、而且**整段沒有句號**。
       散文列舉幾乎一定有句號，真標題幾乎一定沒有。
    """
    s = (para or "").strip()
    if not s or s.startswith("#"):
        return None
    for lv, rx in _HEAD_PATS:
        m = rx.match(s)
        if not m:
            continue
        body = s[m.end():].strip()
        if not body:
            return None
        # 編號後面又接一個編號 → 那是數字串不是標題（自序文末的日期
        # 「九十、三、十九 于尊梅樓」剛好短、又沒有句號，兩道閘都會放過）
        if lv == 1 and _HEAD_PATS[0][1].match(body):
            return None
        if cb._title_key(body) in keys:
            return lv
        if len(s) <= max_len and "。" not in s:
            return lv
        return None
    # 編號認不出來，但整段（或去掉開頭一個字之後）正好是目次上的一條標題。
    # 🚨 圈號 ㈡㈢㈣ 常被 OCR 讀成「口」「曰」「四」——這些是真的漢字，不能靠
    # 字形認。改成反過來問「拿掉那個字之後是不是目次上的標題」，由白名單把關，
    # 才不會把正文裡以「口」「四」開頭的句子誤判成標題。
    for cand in (s, s[1:].strip()):
        hit = keys.get(cb._title_key(cand))
        if hit and len(s) <= max_len:
            return hit[0]
    return None


def canonical_heading(para: str, keys: dict[str, tuple[int, str]]) -> str:
    """編號被 OCR 讀壞的標題 → 換回目次上印的那個編號。

    圈號 ㈡㈢㈣ 常被讀成「口」「曰」「四」「白」「田」，直接呈現就是一行錯字。
    只在**這一段已經被認定是標題、而且編號認不出來**時才動，換上去的編號來自
    書上的目次，不是我編的。認得出編號的（`一、`、`（一）`）原樣不動。
    """
    s = (para or "").strip()
    if any(rx.match(s) for _lv, rx in _HEAD_PATS):
        return s
    if cb._title_key(s) in keys:
        return s                      # 整段就是標題本文，本來就沒有編號可修
    stripped = s[1:].strip()          # 開頭那一個字是被讀壞的編號
    hit = keys.get(cb._title_key(stripped))
    if not hit:
        return s
    # 接法照書上的習慣：`（一）` 直接接、`一、` 也直接接，圈號才空一格
    sep = "" if hit[1][-1] in "）)、." else " "
    return f"{hit[1]}{sep}{stripped}"


def mark_headings(chunks: list[dict], toc: str) -> list[dict]:
    """把正文裡的節標題加上 `###`／`####`／`#####`（章是 `##`，所以往下錯開一層）。

    卷首（自序、目次）跳過：目次整頁都是標題樣式，加了會變成一頁全是標題列。
    """
    keys = toc_keys(toc)
    out = []
    for c in chunks:
        if c["chunk_type"] != "chapter" or c["chapter_path"].endswith(("自序", "目次")):
            out.append(c)
            continue
        paras = []
        for p in c["content"].split("\n\n"):
            lv = heading_level(p, keys)
            paras.append(f"{'#' * (lv + 2)} {canonical_heading(p, keys)}" if lv else p)
        out.append({**c, "content": "\n\n".join(paras)})
    return out


def build_chunks(chapters: list[dict]) -> list[dict]:
    """章 list → ebook_chunks（cover + 每章一 chunk）。

    `page_number` 只在該章第一段讀得到**純數字**印刷頁碼時才填，所以卷首那三段
    （`自序3` 這種）一律 None —— 不拿流水號或去掉前綴的數字充數。
    """
    cover = (f"# {TITLE}\n\n{AUTHOR}　著\n\n法界出版社，{PUBLISHER_YEAR}"
             f"（民國九十年）\n\n為印順導師九六嵩壽「人間佛教‧薪火相傳」學術研討會而出版。")
    chunks = [{
        "chunk_index": 0, "chunk_type": "cover", "page_number": 0,
        "chapter_path": TITLE, "volume": TITLE, "parent_volume": None,
        "format": "markdown", "content": cover,
    }]
    for i, ch in enumerate(chapters, 1):
        first = next((a for a in ch["anchors"] if a.isdigit()), None)
        chunks.append({
            "chunk_index": i, "chunk_type": "chapter",
            "page_number": int(first) if first else None,
            "chapter_path": f"{TITLE} · {ch['title']}",
            "volume": TITLE, "parent_volume": None, "format": "markdown",
            "content": "\n\n".join(ch["paras"]),
            "anchors": [""] + list(ch["anchors"]) if ch["paras"][0].startswith("## ")
                       else list(ch["anchors"]),
        })
    return chunks


# ── I/O ────────────────────────────────────────────────────────────────────

def assemble() -> tuple[list[dict], dict]:
    records = cb.load_cache([Path(CACHE)], Path(WORK))
    if not records:
        raise SystemExit(f"快取是空的：{CACHE}")
    # 先修頁碼再加前綴再記帳 —— 反過來的話 wp114 的 97 還掛著誤讀的 17，
    # 會被當成正文頁 17 的重複而丟掉一整頁
    records = [r for r in records if r["work_page"] not in SKIP_WP]
    records = prefix_front_matter(cb.prepare_records(records))
    titles = [c["title"] for c in CHAPTERS]
    rep = cb.audit_pages(records, titles)
    pages = cb.tag_chapters(cb.pages_for_stitch(records, rep["keep"], titles), CHAPTERS)
    units = drop_leading_chapter_title(cb.stitch_pages(pages), CHAPTERS)
    chapters = cb.split_chapters(units, CHAPTERS)
    chunks = build_chunks(chapters)
    toc = next((c["content"] for c in chunks if c["chapter_path"].endswith("目次")), "")
    return mark_headings(chunks, toc), rep


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="store_true", help="只印重複／缺頁報告")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    if a.audit:
        recs = [r for r in cb.load_cache([Path(CACHE)], Path(WORK)) if r["work_page"] not in SKIP_WP]
        records = prefix_front_matter(cb.prepare_records(recs))
        rep = cb.audit_pages(records, [c["title"] for c in CHAPTERS])
        rng = rep["printed_range"]
        print(f"掃描頁 {len(records)}　→　保留 {len(rep['keep'])} 頁")
        print(f"正文印刷頁碼範圍：{rng[0]}–{rng[1]}" if rng else "（無數字頁碼）")
        print(f"空白頁 {len(rep['blank'])}：{rep['blank']}")
        print(f"裝置頁 {len(rep['apparatus'])}：{rep['apparatus']}")
        print(f"重複 {len(rep['duplicates'])} 組：")
        for d in rep["duplicates"]:
            print(f"  頁 {d['printed']}：保留掃描頁 {d['keep']}，去掉 {d['drop']}")
        print(f"章末空白頁（不是缺頁）{len(rep['blank_gaps'])}：{rep['blank_gaps']}")
        print(f"🚨 真缺頁 {len(rep['missing'])}：{rep['missing']}")
        return

    chunks, _ = assemble()
    if a.inspect or not a.upload:
        total = sum(len(c["content"]) for c in chunks)
        print(f"{len(chunks)} chunks　{total:,} 字")
        for c in chunks:
            head = c["content"].split("\n", 1)[0][:34]
            n = len(c.get("anchors") or [])
            print(f"  [{c['chunk_index']:>2}] p={str(c['page_number']):>4}　{n:>4} 段　"
                  f"{c['chapter_path'].split(' · ')[-1][:28]:<30} {head}")
    if a.upload:
        _upload(chunks)


def _upload(chunks: list[dict]) -> None:
    import datetime
    import requests
    import translate_ebook_to_zh as te

    chunks_dir = te.CHUNKS_DIR
    if not chunks_dir.exists():
        chunks_dir = Path("c:/tmp/chaohwei_vijnapti/_chunks")
        chunks_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ⚠ Drive 未掛載，JSONL 暫存 {chunks_dir}", flush=True)
    out = chunks_dir / f"{EBOOK_ID}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    try:
        te.se.push_to_r2(EBOOK_ID, out)
        print("  ✓ R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 失敗: {e}", flush=True)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    pages = [int(a) for c in chunks for a in (c.get("anchors") or []) if str(a).isdigit()]
    pages += [c["page_number"] for c in chunks if c["page_number"]]
    row = {
        "id": EBOOK_ID, "title": TITLE, "author": AUTHOR, "author_en": "Shih Chao-Hwei",
        "file_type": "pdf", "file_path": f"全集/佛學/昭慧法師/{TITLE}",
        "category": "佛學", "subcategory": "唯識學", "display_mode": "standard",
        "collection": "collected-works", "publication_year": PUBLISHER_YEAR,
        "chunk_count": len(chunks), "total_pages": max(pages) if pages else None,
        "total_chars": sum(len(c["content"]) for c in chunks),
        "parsed_at": now, "standardized_at": now,
    }
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{EBOOK_ID}",
                    headers=te.H_GET, timeout=30)
    rows = [{
        "ebook_id": EBOOK_ID, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
        "page_number": c["page_number"], "chapter_path": c["chapter_path"],
        "content": c["content"][:200], "char_count": len(c["content"]),
    } for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON,
                      json=rows[i:i + 25], timeout=60)
    print(f"  ✓ DB ebooks+previews  chunk_count={len(chunks)}  {EBOOK_ID}", flush=True)


if __name__ == "__main__":
    main()
