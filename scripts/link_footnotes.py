#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把「章末／節末已有註釋條列，但正文沒連上」的書轉成 reader 認得的格式（2026-09-28，乾跑）。

背景：scripts/survey_footnotes.py 盤點全館後發現，電子圖書館（ebooks.collection is
null）裡「OCR／MinerU 頁尾分隔線＋裸數字」那類已經有 scripts/consolidate_page_chunks.py
在吃（另一支批次程式正在改同一批檔案，本工具刻意跳過那類、不碰）。本工具處理的是
**不同的**兩種殘局：

  1. 章／節末已經有 `(N)` 或 `[N]` 條列註釋，但落在 reader 的「切換模式」外——
     reader（pages/ebook/[id].vue renderMarkdown）只認「15 個以上破折號的分隔線」
     會切換進/出註釋模式，標題（`## 註釋`）本身**不會**切換進去，只會把模式切回
     正文。所以「## 註釋\n\n(N) …」這種常見寫法其實是**看起來成功的失敗**：條列
     好好地在那，reader 卻把它們當一般段落印出來，完全點不回正文、也沒有 ↩。
  2. 條列本身用 `[N]` 而不是 `(N)`——reader 的 fnMatch 正規式只認 `(\d+)`，`[N]`
     格式同樣是死的。
  3. 不論以上哪種，正文裡對應的註號可能還是裸數字、`[N]`、上標 ¹²³、或「註N／注N」，
     沒換成可點的 `[^N]`。

只做以下事：在同一個 chunk 內（不跨 chunk，前後有多段切換模式的複雜情況一律跳過，
保守優先），找出「已有的註釋條列」→ 統一成 `(N) 文字`、在條列前補一行分隔線（如果
原本就有分隔線且註釋已在模式內，維持原樣不動)、然後把正文裡「確實對得上這條註」的
標記換成 `[^N]`。**只做 --dry-run**：印出每本「條目數／正文連上數」，不寫檔、不推
R2、不動 DB。

用法：
  python -X utf8 scripts/link_footnotes.py --ids <id> [<id> ...]
  python -X utf8 scripts/link_footnotes.py --sample 50 [--seed N]
  python -X utf8 scripts/link_footnotes.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import consolidate_page_chunks as cp  # noqa: E402  重用其 split_page／link_markers

CH = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

_CJK = r"[\u4e00-\u9fff]"
_PUNCT = r"[，。、；：！？」』）]"
RULE_RE = re.compile(r"^[—－\-]{15,}\s*$")
HEADING_RE = re.compile(r"^#{1,4}\s+(.+)$")
NOTES_WORD = re.compile(r"^(?:註釋|注釋|附註|註解|注解|Notes?)\s*$", re.I)
FOOT_RULE = "—" * 15

# 條列本身可能長這樣：(12) 文字 / [12] 文字 / 12．文字 / 12、文字 / 12) 文字 / 註12：文字
ENTRY_RE = re.compile(
    r"^(?:\((\d{1,4})\)|\[(\d{1,4})\]|(?:註|注)(\d{1,4})[：:、]|(\d{1,4})[).、．.])\s*(.*)$",
    re.S,
)

SUP_MAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
SUP_RUN = re.compile(f"[⁰¹²³⁴⁵⁶⁷⁸⁹]{{1,3}}")
BRACKET_INLINE = re.compile(r"\[(\d{1,4})\](?!\()")
ZHU_INLINE = re.compile(r"(?:註|注)(\d{1,4})(?![\d年月日%％頁])")
_LEFT_OK = re.compile("(?:" + _CJK + "|" + _PUNCT + "|[A-Za-z])$")


def _entry_num(m: re.Match) -> int:
    for g in m.groups()[:4]:
        if g is not None:
            return int(g)
    raise AssertionError


def extract_notes_block(content: str) -> dict:
    """回傳 {kind, body, entries, multi_region} 之一：
    kind='rule'          — 已有分隔線切換（reader 已認得），只可能還缺正文連結／括號格式
    kind='heading_no_rule' — 有「註釋」類標題但全篇沒有分隔線，條列是死的
    kind=None            — 這個 chunk 沒有可辨識的條列註釋區塊，略過
    body 是條列之前（含標題，若有）的原文；entries 是 [(num, text)]。
    multi_region=True 代表分隔線出現不只一次（CCEL 那種每章一組），保守跳過不處理。
    """
    blocks = re.split(r"\n{2,}", content or "")
    rule_idx = [i for i, b in enumerate(blocks) if RULE_RE.match(b.strip())]
    if len(rule_idx) > 1:
        return {"kind": None, "body": content, "entries": [], "multi_region": True}
    if len(rule_idx) == 1:
        i = rule_idx[0]
        body = "\n\n".join(blocks[:i]).rstrip()
        entries = []
        for b in blocks[i + 1:]:
            b = b.strip()
            if not b:
                continue
            m = ENTRY_RE.match(b)
            if m:
                entries.append([_entry_num(m), m.group(5).strip()])
            elif entries:
                entries[-1][1] += " " + b
        return {"kind": "rule" if entries else None, "body": body,
                "entries": [(n, t) for n, t in entries], "multi_region": False}

    # 沒有分隔線：找「註釋類標題」，其後若接著條列格式的段落才算數（避免隨便一個
    # 叫「附註」的標題後面接的其實是一般散文）。
    for i, b in enumerate(blocks):
        h = HEADING_RE.match(b.strip())
        if not h or not NOTES_WORD.match(h.group(1).strip()):
            continue
        rest = blocks[i + 1:]
        if not rest or not ENTRY_RE.match(rest[0].strip()):
            continue
        entries = []
        for b2 in rest:
            b2 = b2.strip()
            if not b2:
                continue
            m = ENTRY_RE.match(b2)
            if m:
                entries.append([_entry_num(m), m.group(5).strip()])
            elif entries:
                entries[-1][1] += " " + b2
        body = "\n\n".join(blocks[: i + 1]).rstrip()
        return {"kind": "heading_no_rule", "body": body,
                "entries": [(n, t) for n, t in entries], "multi_region": False}
    return {"kind": None, "body": content, "entries": [], "multi_region": False}


def link_explicit_markers(body: str, numbers: list[int]) -> tuple[str, list[int]]:
    """先處理「本來就長得像註標」的三種明確寫法：`[N]`、上標 ¹²³、「註N／注N」。
    比裸數字可靠得多——標記本身已經自我宣告是引用，不必再靠前後文猜。只在左界是
    中文字／標點／英文字母時才算數（避免抓到句首、公式裡的數字）。"""
    found: list[int] = []
    remaining = set(numbers)
    pos = 0
    body_work = body
    # 上標與一般數字一對一（同樣長度），直接轉譯比對，不影響其他 match 的 offset。
    for n in sorted(remaining):
        best = None
        best_repl = None
        for rx, wrap in ((SUP_RUN, lambda s: s.translate(SUP_MAP)),
                         (BRACKET_INLINE, lambda s: s[1:-1]),
                         (ZHU_INLINE, lambda s: re.sub(r"^(?:註|注)", "", s))):
            for m in rx.finditer(body_work, pos):
                if wrap(m.group(0)) != str(n):
                    continue
                if not (m.start() > 0 and _LEFT_OK.search(body_work[:m.start()])):
                    continue
                if best is None or m.start() < best.start():
                    best, best_repl = m, f"[^{n}]"
                break  # 這個規則只取第一個候選，讓其他規則也有機會比 start()
        if best:
            body_work = body_work[:best.start()] + best_repl + body_work[best.end():]
            pos = best.start() + len(best_repl)
            found.append(n)
    return body_work, found


# 裸數字啟發式（cp.link_markers）借用自 consolidate_page_chunks，那邊只排除緊接
# 著度數符號／年／月／日／%／頁的數字；人工核對時抓到「公元[^1]世紀」「[^18]世紀
# 劍橋柏拉圖倫理學派」「[^19]世紀與[^20]世紀之交」這種世紀／年代誤判（喀爾文以外
# 的另一本書，正文其實是「1世紀」「18世紀」，不是註號）。在這裡多加一層針對
# link_footnotes 自己場景的守門：借來的裸數字結果，緊接著這些量詞就整條打回原狀。
_BARE_NUMBER_FALSE_FRIEND = re.compile(r"^(?:世紀|年代|年|月|日|世|頁|節|章|卷|冊|行|款|條|項|"
                                        r"號|号|時|分|秒|度|個|个|位|名|次|回|版|刷)")


def _revert_false_friends(body: str, candidates: set[int]) -> tuple[str, set[int]]:
    """掃 body 裡屬於 candidates 的 `[^N]`，緊接量詞（世紀／年代…）就打回裸數字。"""
    reverted: set[int] = set()

    def repl(m: re.Match) -> str:
        n = int(m.group(1))
        if n in candidates and _BARE_NUMBER_FALSE_FRIEND.match(body[m.end():]):
            reverted.add(n)
            return str(n)
        return m.group(0)

    new_body = re.sub(r"\[\^(\d{1,4})\]", repl, body)
    return new_body, reverted


def link_footnotes_chunk(content: str) -> dict:
    """單一 chunk 的完整流程。回傳 dict：changed、new_content、entries、linked、kind。"""
    if cp.split_page(content or "")[1]:
        return {"kind": "page-rule-other-tool", "entries": 0, "linked": 0,
                "changed": False, "new_content": content}
    info = extract_notes_block(content or "")
    if info["kind"] is None or not info["entries"]:
        return {"kind": info["kind"] or "no-notes", "entries": 0, "linked": 0,
                "changed": False, "new_content": content,
                "multi_region": info.get("multi_region", False)}
    numbers = [n for n, _ in info["entries"]]
    # 有些書已經跑過一輪（body 裡已經是 [^N]），不用再猜、也不能猜（regex 認不得
    # `[^N]` 這個寫法），先算進「已連上」再處理剩下的。
    already = {int(m) for m in re.findall(r"\[\^(\d{1,4})\]", info["body"])} & set(numbers)
    body, found = link_explicit_markers(info["body"], [n for n in numbers if n not in already])
    remaining = [n for n in numbers if n not in already and n not in found]
    if remaining:
        body, found2 = cp.link_markers(body, remaining)
        body, reverted = _revert_false_friends(body, set(found2))
        found = sorted(set(found) | (set(found2) - reverted))
    found = sorted(set(found) | already)
    notes_text = "\n\n".join(f"({n}) {t}" for n, t in info["entries"])
    new_content = body.rstrip() + f"\n\n{FOOT_RULE}\n\n{notes_text}"
    changed = new_content != (content or "").strip()
    return {"kind": info["kind"], "entries": len(numbers), "linked": len(found),
            "changed": changed, "new_content": new_content}


def eligible_book(chunks: list[dict]) -> str:
    """回傳空字串＝可處理；否則回略過原因（雙語書一律跳過，交給 ebook-translate 那條線）。"""
    if any(("source_text" in c or "sources" in c) for c in chunks):
        return "bilingual-skip"
    # 2026-09-28：已合併成一節一塊的書（有 page_numbers）註釋由 consolidate_page_chunks 處理；
    # 這支再跑一次曾把 {{p:34}} 頁碼標記與「5,000萬」連成註號，83 本全數還原。
    if any(c.get("page_numbers") for c in chunks):
        return "consolidated-skip"
    return ""


def dry_run_book(ebook_id: str, apply: bool = False) -> dict | None:
    p = CH / f"{ebook_id}.jsonl"
    if not p.exists():
        return None
    try:
        chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
    except Exception:  # noqa: BLE001
        return None
    why = eligible_book(chunks)
    if why:
        return {"skip": why}
    total_entries = 0
    total_linked = 0
    kinds = {}
    changed_any = False
    for c in chunks:
        fmt = c.get("format")
        if fmt and fmt not in ("markdown", "text", "md"):
            continue
        r = link_footnotes_chunk(c.get("content") or "")
        if r["entries"]:
            total_entries += r["entries"]
            total_linked += r["linked"]
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
            if apply and r.get("changed"):
                c["content"] = r["new_content"]
                changed_any = True
    if apply and changed_any:
        # 2026-09-28 正式寫入：留 .jsonl.bak_footnotes（已有就不覆蓋），寫回＋推 R2＋更新 DB
        import shutil
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import standardize_ebook as se  # noqa: E402
        bak = p.with_suffix(".jsonl.bak_footnotes")
        if not bak.exists():
            shutil.copy2(p, bak)
        out = se.write_jsonl(ebook_id, chunks)
        se.push_to_r2(ebook_id, out)
        se.update_db(ebook_id, chunks)
    return {"entries": total_entries, "linked": total_linked, "kinds": kinds, "written": bool(apply and changed_any)}


def fetch_library_ids(limit: int | None = None) -> list[dict]:
    import requests
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows: list[dict] = []
    offset = 0
    while True:
        r = requests.get(
            f"{url}/rest/v1/ebooks?select=id,title&collection=is.null&order=id"
            f"&limit=1000&offset={offset}", headers=headers, timeout=60)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        offset += 1000
        if len(batch) < 1000:
            break
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", default=[])
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true", help="正式寫入（留 .jsonl.bak_footnotes）")
    args = ap.parse_args()

    if args.ids:
        library = [{"id": i, "title": i} for i in args.ids]
    else:
        library = fetch_library_ids()
        print(f"電子圖書館共 {len(library)} 本", flush=True)
        if args.sample:
            random.seed(args.seed)
            library = random.sample(library, min(args.sample, len(library)))
        elif not args.all:
            print("請加 --ids / --sample N / --all 其中之一", flush=True)
            return 1

    n_books_with_entries = 0
    total_entries = 0
    total_linked = 0
    for row in library:
        res = dry_run_book(row["id"], apply=args.apply)
        if res is None or res.get("skip") or not res.get("entries"):
            continue
        n_books_with_entries += 1
        total_entries += res["entries"]
        total_linked += res["linked"]
        rate = res["linked"] / res["entries"] * 100
        print(f"{row['id']}  {row.get('title', '')[:30]:30s}  註釋 {res['entries']:4d} 條，"
              f"正文連上 {res['linked']:4d} 個（{rate:.0f}%）  {res['kinds']}", flush=True)

    print("\nSUMMARY", flush=True)
    print(f"  有偵測到條列註釋的書：{n_books_with_entries} 本", flush=True)
    print(f"  條目總數：{total_entries}；正文連上：{total_linked}"
          + (f"（{total_linked/total_entries*100:.1f}%）" if total_entries else ""), flush=True)
    print("LINK_FOOTNOTES_DRYRUN_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
