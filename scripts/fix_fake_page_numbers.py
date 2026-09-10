# -*- coding: utf-8 -*-
"""把 `ebook_chunks` 裡的假頁碼清成 NULL。

配 `audit_page_numbers_db.py` 使用：那一支找出「EPUB 卻逐一遞增」的書
（＝`page_number` 是 `chunk_index+1` 冒充的），這一支把那些值清掉。

為什麼是清成 NULL 而不是留著：假頁碼**比沒有頁碼更糟**，因為它會讓人照著寫進
論文（[[feedback_transcribe_page_numbers]]）。EPUB 沒有版面也就沒有頁碼，
這些書的正確狀態就是 NULL。

🚨 不要對 `serial-pdf` 動手。一頁一 chunk 的 PDF 本來就滿足 `chunk_index+1`，
   那是真頁碼；清掉會毀掉一千多本書的引註能力。本支只吃 `serial-epub`。

🚨 只改 DB。Drive 上的 `_chunks/*.jsonl` 仍是舊值——但建構器已經修好
   （沒有真頁碼就寫 None），所以下次重建出來的就是 NULL，兩邊會自然收斂。

  python -X utf8 scripts/fix_fake_page_numbers.py                  # 只看
  python -X utf8 scripts/fix_fake_page_numbers.py --apply
  python -X utf8 scripts/fix_fake_page_numbers.py --apply --skip <ebook_id>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import audit_page_numbers_db as audit  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip", action="append", default=[],
                    help="要跳過的 ebook_id（例：即將補上真頁碼的書）")
    args = ap.parse_args()

    env = audit.load_env(SCRIPT_DIR.parent)
    rows = audit.run_sql(env, audit.SQL.format(where=""))
    bad = [r for r in rows
           if audit.classify(int(r["total"]), int(r["with_page"]),
                             int(r["serial"] or 0), r.get("file_type", "")) == "serial-epub"
           and r["ebook_id"] not in args.skip]

    print(f"假頁碼的書 {len(bad)} 本，chunk 共 {sum(int(r['total']) for r in bad):,} 個")
    for r in bad:
        print(f"  {str(r.get('author'))[:12]:14} {str(r['title'])[:34]:36} "
              f"chunks={r['total']:>5}")
    if args.skip:
        print(f"（跳過 {len(args.skip)} 本：{', '.join(args.skip)}）")

    if not args.apply:
        print("\n加 --apply 才會真的清掉")
        return

    ids = ", ".join(f"'{r['ebook_id']}'" for r in bad)
    if not ids:
        print("沒有要清的")
        return
    audit.run_sql(env, f"UPDATE ebook_chunks SET page_number = NULL "
                       f"WHERE ebook_id IN ({ids}) AND page_number IS NOT NULL;")
    left = audit.run_sql(env, f"SELECT count(page_number) AS still "
                              f"FROM ebook_chunks WHERE ebook_id IN ({ids});")
    print(f"\n已清。殘留有值的 chunk：{left[0]['still']}")


if __name__ == "__main__":
    main()
