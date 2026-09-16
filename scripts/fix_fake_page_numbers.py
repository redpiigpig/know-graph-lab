# -*- coding: utf-8 -*-
"""把假頁碼清成 null —— 直接改 Drive 上的 `_chunks/*.jsonl`，再推 R2。

配 `audit_page_numbers_db.py` 使用：那一支找出「EPUB 卻逐一遞增」的書
（＝`page_number` 是 `chunk_index+1` 冒充的），這一支把那些值清掉。

為什麼是清成 null 而不是留著：假頁碼**比沒有頁碼更糟**，因為它會讓人照著寫進
論文（[[feedback_transcribe_page_numbers]]）。EPUB 沒有版面也就沒有頁碼，
這些書的正確狀態就是 null。

🚨 不要對 `serial-pdf` 動手。一頁一 chunk 的 PDF 本來就滿足 `chunk_index+1`，
   那是真頁碼；清掉會毀掉一千多本書的引註能力。本支只吃 `serial-epub`。

2026-09-16 改寫：以前這支只 UPDATE `ebook_chunks`，Drive 上的 JSONL 原封不動
（舊註解自己也寫著「兩邊會自然收斂」——但 reader 讀的一直是 JSONL，所以那次清
根本沒清到使用者看得到的那一份）。現在表退場了，JSONL 是唯一一份，改這裡才算改到。
見 database/drop-ebook-chunks-2026-09-16.sql。

  python -X utf8 scripts/fix_fake_page_numbers.py                  # 只看
  python -X utf8 scripts/fix_fake_page_numbers.py --apply
  python -X utf8 scripts/fix_fake_page_numbers.py --apply --skip <ebook_id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import audit_page_numbers_db as audit  # noqa: E402
import chunks_jsonl  # noqa: E402


def clear_book(ebook_id: str, chunks: list[dict]) -> int:
    """把整本的 page_number 寫成 null，回傳清掉幾個。JSONL 原地覆寫。"""
    hit = sum(1 for c in chunks if c.get("page_number") is not None)
    if not hit:
        return 0
    for c in chunks:
        c["page_number"] = None
    path = chunks_jsonl.path_for(ebook_id)
    tmp = path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(path)          # 先寫暫存再換，中途斷電不會留半本
    return hit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip", action="append", default=[],
                    help="要跳過的 ebook_id（例：即將補上真頁碼的書）")
    ap.add_argument("--no-r2", action="store_true", help="只改本機 JSONL，不推 R2")
    args = ap.parse_args()

    env = audit.load_env(SCRIPT_DIR.parent)
    rows = audit.run_sql(env, audit.SQL.format(where=""))
    if not isinstance(rows, list):
        print("查詢失敗:", rows)
        raise SystemExit(1)
    print(f"DB 書目 {len(rows):,} 本，開始讀 Drive 的 chunks …")
    buckets = chunks_jsonl.scan([r["ebook_id"] for r in rows])

    bad = []
    for r in rows:
        chunks = buckets.get(r["ebook_id"])
        if chunks is None or r["ebook_id"] in args.skip:
            continue
        total, with_page, serial = audit.tally_book(chunks)
        if audit.classify(total, with_page, serial, r.get("file_type", "")) == "serial-epub":
            bad.append((r, chunks))

    print(f"假頁碼的書 {len(bad)} 本，chunk 共 {sum(len(c) for _, c in bad):,} 個")
    for r, chunks in bad:
        print(f"  {str(r.get('author'))[:12]:14} {str(r['title'])[:34]:36} "
              f"chunks={len(chunks):>5}")
    if args.skip:
        print(f"（跳過 {len(args.skip)} 本：{', '.join(args.skip)}）")

    if not args.apply:
        print("\n加 --apply 才會真的清掉")
        return
    if not bad:
        print("沒有要清的")
        return

    se = None
    if not args.no_r2:
        import standardize_ebook as se  # noqa: PLC0415  只有真要推 R2 時才載

    cleared = books = 0
    for r, chunks in bad:
        eid = r["ebook_id"]
        n = clear_book(eid, chunks)
        if not n:
            continue
        cleared += n
        books += 1
        if se is not None:
            try:
                se.push_to_r2(eid, chunks_jsonl.path_for(eid))
            except Exception as e:  # noqa: BLE001
                print(f"  ⚠ R2 推失敗 {eid}：{str(e)[:80]}", file=sys.stderr)
        print(f"  ✓ {str(r['title'])[:34]:36} 清了 {n} 個")

    print(f"\n已清 {books} 本、{cleared:,} 個 chunk 的 page_number。"
          f"{'（--no-r2：R2 上還是舊的）' if args.no_r2 else ''}")


if __name__ == "__main__":
    main()
