#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《人間佛教的播種者》OCR 快取 → 昭慧法師全集（/collected-works）。

釋昭慧著，東大圖書（現代佛學叢書），民國八十四年七月初版、八十六年二月修訂初版。
印順導師的通俗傳記，十八章。掃描檔是**左右並排**的跨頁，工作 PDF 的做法見
scripts/scan_books.py 的 `chaohwei-seeder` 那一筆。

2026-09-30 先轉前半：卷首＋正文頁 1–119（第十四章開頭），後半待掃。後半掃來後：
新檔加進 scan_books 的 sources、重出 work_pdf、`scan_ocr.py --resume` 補跑，
再把下面 `CHAPTERS` 補到第十八章＋主要參考資料＋後記。

與《初期唯識思想》的差別（純函式共用 chaohwei_build／chaohwei_vijnapti_build）：
  * 橫排；卷首是叢書總序（只掃到最後一頁，不收）、自序 1–6、目次 1–3，
    各自從 1 編頁 → 加前綴，不然會跟正文 1–6 撞號；
  * 註號是黑底圓圈數字、**每章連續編號**。頁底註文的號碼印得很小，OCR 常讀成
    ❶，所以以正文註號為準對齊（`align_note_numbers`）；
  * 節標題是不編號的短標（「普陀山進香」），目次上以「／」分隔 → 白名單比對。

  python -X utf8 scripts/chaohwei_seeder_build.py --audit
  python -X utf8 scripts/chaohwei_seeder_build.py --inspect
  python -X utf8 scripts/chaohwei_seeder_build.py --upload
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
import chaohwei_vijnapti_build as vb  # noqa: E402

EBOOK_ID = "c4a01957-0000-4000-8000-000000000003"
TITLE = "人間佛教的播種者"
AUTHOR = "釋昭慧"
PUBLISHER_YEAR = 1995
# 前面的優先。第一個是人工對照影像校過的頁（自序是粗黑體，OCR 錯字多、又照印刷
# 換行斷句），重跑腳本長不回來，所以放 repo 裡進版控。
CACHE = [str(SCRIPT_DIR.parent / ".claude/skills/ebook-scan-transcribe/chaohwei_seeder_fix"),
         "c:/tmp/chaohwei_seeder/ocr",
         # 88–133 頁：Gemini 額度用完後改本機 MinerU（scripts/chaohwei_seeder_mineru.py 轉格式）
         "c:/tmp/chaohwei_seeder/ocr_mineru"]
WORK = "c:/tmp/chaohwei_seeder/work.pdf"

# 掃描頁 1＝版權頁＋印順法師法相、2＝叢書總序的最後一頁（前面沒掃到，半截不收）
SKIP_WP: set[int] = {1, 2}
CAPTIONS = {"太虛大師道影", "法尊法師晚年德相", "《佛法概論》未修訂前之附圖"}
BODY_START_WP = 13  # 掃描頁 12 是目次後的空白頁，13＝正文頁 1
FRONT_MATTER: list[dict] = [
    {"title": "自序", "wp": (3, 8), "prefix": "自序"},
    {"title": "目次", "wp": (9, 11), "prefix": "目次"},
]

# 照目次頁抄（目次 1–3），起始頁再拿正文章首頁核過
CHAPTERS: list[dict] = [
    {"title": "自序", "start": "自序1", "end": "自序6"},
    {"title": "目次", "start": "目次1", "end": "目次3"},
    {"title": "一‧那個孤寂的身影", "start": "1", "end": "6"},
    {"title": "二‧悠遊尋覓的歲月", "start": "7", "end": "12"},
    {"title": "三‧向佛法中探消息", "start": "13", "end": "16"},
    {"title": "四‧邁向出家之旅", "start": "17", "end": "22"},
    {"title": "五‧求法、教學的生涯", "start": "23", "end": "32"},
    {"title": "六‧普陀山閱藏", "start": "33", "end": "42"},
    {"title": "七‧從普陀到武昌", "start": "43", "end": "46"},
    {"title": "八‧抗戰歲月", "start": "47", "end": "60"},
    {"title": "九‧顛沛流離", "start": "61", "end": "76"},
    {"title": "十‧思想凝定的十四年", "start": "77", "end": "96"},
    {"title": "十一‧多事之秋", "start": "97", "end": "102"},
    {"title": "十二‧山雨欲來風滿樓", "start": "103", "end": "108"},
    {"title": "十三‧《佛法概論》事件", "start": "109", "end": "118"},
    {"title": "十四‧繁忙的弘法生活", "start": "119", "end": "144"},
    # 待掃：十五 145／十六 155／十七 179／十八 201／主要參考資料 205／後記 207
]


# ── 純函式 ────────────────────────────────────────────────────────────────

_REF_RE = re.compile(r"\[\^(\d+)\](?!:)")
_NOTE_RE = re.compile(r"^\[\^(\d+)\]:\s*")
_CHAPTER_LINE_RE = re.compile(r"^[一二三四五六七八九十]{1,3}\s*[·‧・.．]")


def align_note_numbers(text: str) -> str:
    """頁底註文的號碼改成跟正文註號一致（依出現順序一一對應）。

    本書註號每章連續編，頁底註文前的圈號印得極小，OCR 常一律讀成 ❶：正文是
    `[^2]`、註文卻是 `[^1]:`，reader 就配不起來。正文的圈號大、讀得準，所以
    以它為準。只在**數量相同而號碼不同**時才動；數量對不上（有註跨頁、或漏讀）
    就原樣留著，交給人看。
    """
    lines = (text or "").split("\n")
    refs = [m.group(1) for ln in lines if not _NOTE_RE.match(ln) for m in _REF_RE.finditer(ln)]
    note_idx = [i for i, ln in enumerate(lines) if _NOTE_RE.match(ln)]
    if not note_idx or len(refs) != len(note_idx):
        return text
    if [_NOTE_RE.match(lines[i]).group(1) for i in note_idx] == refs:
        return text
    for i, n in zip(note_idx, refs):
        lines[i] = _NOTE_RE.sub(f"[^{n}]: ", lines[i], count=1)
    return "\n".join(lines)


def _sec_key(s: str) -> str:
    # 目次與正文對同一個字常用不同字形（人生佛敎／人生佛教）
    return cb._title_key(s).replace("敎", "教")


def unwrap_print_lines(text: str) -> str:
    """整頁照印刷換行斷句的 OCR（Gemini 在這本有 11 頁如此）→ 還原成一段一行。

    只對「看起來是印刷行」的頁動手：正文行 ≥ 8 行且行長中位數 ≤ 26 字（本書滿行約
    24 字；正常一段一行的頁中位數在百字以上）。判準：新段首行縮排兩格，所以上一行
    若印滿（≥ 常見行寬 −1）就是同一段，接回去。註文行不動。
    """
    lines = (text or "").split("\n")
    body = [ln for ln in lines if ln.strip() and not ln.startswith("[^")]
    if len(body) < 8:
        return text
    lens = sorted(len(ln) for ln in body)
    if lens[len(lens) // 2] > 26:
        return text
    full = max(set(lens), key=lens.count)
    out: list[str] = []
    last_len = 0            # 上一條**印刷行**的長度（不是已經接好的整段）
    for ln in lines:
        if (out and not out[-1].startswith(("[^", "#")) and not ln.startswith("[^")
                and ln.strip() and last_len >= full - 1):
            out[-1] += ln
        else:
            out.append(ln)
        last_len = len(ln)
    return "\n".join(out)


def section_titles(toc: str) -> set[str]:
    """目次文字 → 節標題鍵集合。目次每章一行章名，底下是「頁碼 節名／節名／…」。

    🚨 節名會在**詞中間**折行（「香港三年／擬建」＋「精舍／望重香江」），上一行
    結尾不一定有「／」。所以除了章名行，其餘各行一律直接接到前一行上。
    """
    groups: list[str] = []
    for ln in (toc or "").replace("/", "／").split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if _CHAPTER_LINE_RE.match(ln) or not groups:
            groups.append("")          # 章名本身不是節名，只當分組界線
            continue
        groups[-1] += re.sub(r"^\d+\s*", "", ln) if not groups[-1] else ln
    keys: set[str] = set()
    for g in groups:
        for piece in g.split("／"):
            k = _sec_key(piece)
            if 2 <= len(k) <= 16:
                keys.add(k)
    return keys


def mark_sections(chunks: list[dict], toc: str) -> list[dict]:
    """正文裡整段正好是目次上的節名 → `### 節名`。卷首不動。"""
    keys = section_titles(toc)
    out = []
    for c in chunks:
        if c["chunk_type"] != "chapter" or c["chapter_path"].endswith(("自序", "目次")):
            out.append(c)
            continue
        paras = [f"### {p}" if (not p.startswith("#") and len(p) <= 20
                                 and _sec_key(p) in keys) else p
                 for p in c["content"].split("\n\n")]
        out.append({**c, "content": "\n\n".join(paras)})
    return out


def build_chunks(chapters: list[dict]) -> list[dict]:
    cover = (f"# {TITLE}\n\n{AUTHOR}　著\n\n東大圖書，{PUBLISHER_YEAR}（民國八十四年）初版、"
             "1997（民國八十六年）修訂初版（現代佛學叢書）\n\n印順導師傳記。")
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

def load_records() -> list[dict]:
    recs = [r for r in cb.load_cache([Path(c) for c in CACHE], Path(WORK))
            if r["work_page"] not in SKIP_WP]
    # 使用者定調照片與圖說不收；prompt 已交代，Gemini 仍吐出來，這裡按原文逐條刪
    recs = [{**r, "text": "\n".join(ln for ln in cb.unescape_linebreaks(r.get("text") or "").split("\n")
                                    if ln.strip() not in CAPTIONS)} for r in recs]
    # 目次頁本來就是一條一行，不能拿去還原段落（它是節標題白名單的來源）
    unwrap = lambda r, t: unwrap_print_lines(t) if r["work_page"] >= BODY_START_WP else t
    recs = [{**r, "text": align_note_numbers(unwrap(r, cb.unescape_linebreaks(r.get("text") or "")))}
            for r in recs]
    # 頁碼先修再加前綴再記帳（順序理由見 chaohwei_vijnapti_build.assemble）
    return vb.prefix_front_matter(cb.prepare_records(recs),
                                  sections=FRONT_MATTER, body_start=BODY_START_WP)


def assemble() -> tuple[list[dict], dict]:
    records = load_records()
    titles = [c["title"] for c in CHAPTERS]
    rep = cb.audit_pages(records, titles)
    pages = cb.tag_chapters(cb.pages_for_stitch(records, rep["keep"], titles), CHAPTERS)
    units = vb.drop_leading_chapter_title(cb.stitch_pages(pages), CHAPTERS)
    chunks = build_chunks(cb.split_chapters(units, CHAPTERS))
    toc = next((c["content"] for c in chunks if c["chapter_path"].endswith("目次")), "")
    return mark_sections(chunks, toc), rep


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="store_true", help="只印重複／缺頁報告")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--dump", help="把 chunks 寫成 JSONL 到這個路徑（本機檢查用）")
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()

    if a.audit:
        records = load_records()
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
    if a.dump:
        with open(a.dump, "w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
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
        chunks_dir = Path("c:/tmp/chaohwei_seeder/_chunks")
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
    row = {
        "id": EBOOK_ID, "title": TITLE, "author": AUTHOR, "author_en": "Shih Chao-Hwei",
        "file_type": "pdf", "file_path": f"全集/佛學/昭慧法師/{TITLE}",
        "category": "佛學", "subcategory": "人物傳記", "display_mode": "standard",
        "collection": "collected-works", "publication_year": PUBLISHER_YEAR,
        "chunk_count": len(chunks), "total_pages": max(pages) if pages else None,
        "total_chars": sum(len(c["content"]) for c in chunks),
        "parsed_at": now, "standardized_at": now,
    }
    H = {**te.H_JSON, "Prefer": "resolution=merge-duplicates"}
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id", headers=H, json=row, timeout=30)
    print(f"  ✓ DB ebooks row  chunk_count={len(chunks)}  {EBOOK_ID}", flush=True)


if __name__ == "__main__":
    main()
