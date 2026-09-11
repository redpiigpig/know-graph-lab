# -*- coding: utf-8 -*-
"""哪幾卷「checkpoint 已經改了，但站上還是舊的」。

為什麼要有這一支：重譯只寫進 checkpoint（`*_data/<slug>/secN.json`），
**不會自動推上站**。`uchimura_auto --work X`（不帶 --upload）會把 JSONL 寫回 Drive，
但 DB 與 R2 維持不動——於是站上讀到的還是舊譯文，而且頁面完全正常，看不出來。
2026-09-11 就這樣：《基督信徒的慰藉》全書重譯成白話之後，站上仍停在三天前的文言版。

判準：checkpoint 最後修改時間 > `ebooks.parsed_at` 即為過期。

  python -X utf8 scripts/collected_works_stale.py
  python -X utf8 scripts/collected_works_stale.py --author uchimura
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import audit_page_numbers_db as audit  # noqa: E402
import uchimura_auto as ua  # noqa: E402

DATA_ROOT = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works"


def newest_checkpoint(data_dirname: str, slug: str) -> dt.datetime | None:
    d = DATA_ROOT / data_dirname / slug
    if not d.exists():
        return None
    ts = [f.stat().st_mtime for f in d.glob("sec*.json")]
    return dt.datetime.fromtimestamp(max(ts), dt.timezone.utc) if ts else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="只看某位作者")
    args = ap.parse_args()

    env = audit.load_env(SCRIPT_DIR.parent)
    rows = audit.run_sql(env, "SELECT id::text AS id, title, parsed_at FROM ebooks "
                              "WHERE collection='collected-works';")
    parsed = {r["id"]: r["parsed_at"] for r in rows}

    stale, fresh, gaps = [], 0, []
    for author in sorted(ua.AUTHOR_MODULES):
        if args.author and author != args.author:
            continue
        mod = importlib.import_module(ua.AUTHOR_MODULES[author])
        dirname = getattr(mod, "DATA_DIRNAME", "uchimura_data")
        for slug, w in getattr(mod, "REGISTRY", {}).items():
            cp = newest_checkpoint(dirname, slug)
            if cp is None:
                continue
            raw = parsed.get(w["ebook_id"])
            db = dt.datetime.fromisoformat(raw.replace(" ", "T")) if raw else None
            # 還有沒譯完的段落就先別推——推上去會是中日夾雜
            todo = 0
            for f in (DATA_ROOT / dirname / slug).glob("sec*.json"):
                try:
                    todo += sum(1 for z in (json.loads(f.read_text(encoding="utf-8")).get("zh") or []) if not z)
                except Exception:
                    pass
            if db is None or cp > db:
                (gaps if todo else stale).append((author, slug, w["title"], cp, db, todo))
            else:
                fresh += 1

    if stale:
        print("站上過期、且已譯完（可以直接推）：")
        for author, slug, title, cp, db, _t in stale:
            print(f"  {author:12} {slug:22} {title[:20]:22} "
                  f"checkpoint {cp:%m-%d %H:%M} > 站上 {db:%m-%d %H:%M}" if db else
                  f"  {author:12} {slug:22} {title[:20]:22} 站上沒有 parsed_at")
        print("\n  推法： python -X utf8 scripts/uchimura_auto.py --author <A> --work <S> --build-only --upload")
    if gaps:
        print("\n還有段落沒譯完（先別推，會中日夾雜）：")
        for author, slug, title, _cp, _db, todo in gaps:
            print(f"  {author:12} {slug:22} {title[:20]:22} 待譯 {todo}")
    print(f"\n已同步 {fresh} 卷；過期 {len(stale)} 卷；未譯完 {len(gaps)} 卷")


if __name__ == "__main__":
    main()
