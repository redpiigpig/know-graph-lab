# -*- coding: utf-8 -*-
"""稽核 chunk 的 `page_number` 是不是**原書頁碼**——全庫、不取樣。

與 `audit_page_numbers.py` 的分工：那支只看 JSONL，分不出 serial-epub 與
serial-pdf（那一刀要 `ebooks.file_type`，不分會把一千多本頁碼正確的 PDF 也
打成假頁碼）。這支拿 DB 的書目 metadata ＋ Drive 的 chunks，兩邊合起來判。

2026-09-16：chunk 那一半從 `ebook_chunks` 改讀 `_chunks/*.jsonl`（表退場了，見
database/drop-ebook-chunks-2026-09-16.sql）。原本寫這支的理由是「Drive 沒掛時
會安靜地掃到 0 個檔」——那個坑改由 chunks_jsonl.require_dir() 直接拋例外擋住，
不再是默默回 0。

判準與 `audit_page_numbers.py` 一致（[[feedback_transcribe_page_numbers]]）：

  serial  九成五以上的 chunk 滿足 page_number == chunk_index + 1  → 見下方分刀
  real    有跳號或重複（同一頁多個 chunk）                        → 真頁碼
  none    全部 NULL                                              → 沒有頁碼
  sparse  部分有值                                                → 混合，要個別看

🚨 兩層防誤判，少一層結論就會差二十倍：

   1. 單看一個 chunk 的 `page_number == chunk_index + 1` 不能判定造假——一定要
      **整本一起看比例**。
   2. **serial 不等於假**。一頁一 chunk 的 PDF 本來就長這樣。真正的造假是
      **EPUB 而 serial**。2026-09-10 全庫實測：serial 1,146 本／237,586 chunk，
      分刀之後真正該修的只有 **51 本／6,486 chunk**（全集 50 ＋ 圖書館 1），
      其餘 1,095 本都是 PDF 的真頁碼。

  node/py 都行，這支走 Management API（psycopg2 直連是 IPv6-only 跑不通的，
  見 [[reference_supabase_management_api]]）。

  python -X utf8 scripts/audit_page_numbers_db.py
  python -X utf8 scripts/audit_page_numbers_db.py --out c:/tmp/page_audit_db.json
  python -X utf8 scripts/audit_page_numbers_db.py --collection collected-works
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import chunks_jsonl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SERIAL_RATIO = 0.95      # 與 audit_page_numbers.classify 同一把尺


def load_env(root: Path) -> dict:
    env = {}
    for line in (root / ".env").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k] = v.strip().strip('"').strip("'")
    return env


def run_sql(env: dict, sql: str):
    import requests
    ref = env["SUPABASE_URL"].replace("https://", "").split(".")[0]
    r = requests.post(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        headers={"content-type": "application/json",
                 "Authorization": f"Bearer {env['SUPABASE_ACCESS_TOKEN']}"},
        json={"query": sql}, timeout=180)
    r.raise_for_status()
    return r.json()


def classify(total: int, with_page: int, serial: int, file_type: str = "") -> str:
    """一本書的計數（＋檔案格式）→ serial-epub / serial-pdf / real / none / sparse。

    🚨 **serial 不等於假**。一頁一 chunk 的 PDF 本來就長這樣，那個頁碼是真的。
    真正的造假是 **EPUB 而 serial**：EPUB 沒有版面也就沒有頁碼，逐一遞增只可能是
    `chunk_index+1` 冒充的。2026-09-10 全庫實測 serial 1,146 本，其中 EPUB 只有
    51 本（全集 50＋圖書館 1），其餘 1,091 本都是 PDF——若不分這一刀，會把
    一千多本頁碼正確的書判成待修。"""
    if total == 0:
        return "empty"
    if with_page == 0:
        return "none"
    if with_page < total:
        return "sparse"
    if serial < max(3, int(with_page * SERIAL_RATIO)):
        return "real"
    return "serial-epub" if (file_type or "").lower() != "pdf" else "serial-pdf"


SQL = """
SELECT e.id::text            AS ebook_id,
       coalesce(e.collection, '(圖書館)') AS collection,
       coalesce(e.file_type, '?')        AS file_type,
       e.title,
       e.author
FROM ebooks e
{where}
ORDER BY e.title;
"""


def tally_book(chunks: list[dict]) -> tuple[int, int, int]:
    """一本書的 chunks → (total, with_page, serial)。判準同 classify()。"""
    total = with_page = serial = 0
    for c in chunks:
        total += 1
        pn, ci = c.get("page_number"), c.get("chunk_index")
        if isinstance(pn, int):
            with_page += 1
            if isinstance(ci, int) and pn == ci + 1:
                serial += 1
    return total, with_page, serial


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--collection", help="只看某個 collection（例 collected-works）")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    env = load_env(root)
    where = ""
    if args.collection:
        where = f"WHERE e.collection = '{args.collection}'"
    rows = run_sql(env, SQL.format(where=where))
    if not isinstance(rows, list):
        print("查詢失敗:", rows)
        raise SystemExit(1)
    print(f"DB 書目 {len(rows):,} 本，開始讀 Drive 的 chunks …")

    # 🚨 印分母：沒有 JSONL 的書會被排除，不說清楚就會以為「全庫只有這些」。
    buckets = chunks_jsonl.scan([r["ebook_id"] for r in rows])

    out = []
    tally = {}
    for r in rows:
        chunks = buckets.get(r["ebook_id"])
        if chunks is None:
            continue          # 這本還沒轉錄，不是頁碼問題
        total, with_page, serial = tally_book(chunks)
        kind = classify(total, with_page, serial, r.get("file_type", ""))
        tally[kind] = tally.get(kind, 0) + 1
        out.append({**r, "total": total, "with_page": with_page,
                    "serial": serial, "kind": kind})

    print(f"有 chunks 的共 {len(out):,} 本書（DB 書目 {len(rows):,} 本）")
    for k in ("serial-epub", "serial-pdf", "real", "none", "sparse", "empty"):
        if tally.get(k):
            print(f"  {k:7s} {tally[k]:5d}")

    bad = [r for r in out if r["kind"] == "serial-epub"]
    if bad:
        print(f"\n**假頁碼**（EPUB 卻逐一遞增＝chunk_index+1 冒充），共 {len(bad)} 本："
              f"\n（EPUB 沒有版面就沒有頁碼，這些一律該改成 NULL 並重推）")
        for r in bad[:30]:
            print(f"  {r['collection']:16} {str(r.get('author'))[:12]:14} "
                  f"{str(r['title'])[:32]:34} chunks={r['total']:>5}")
        if len(bad) > 30:
            print(f"  …另 {len(bad) - 30} 本")
        print(f"\n受影響的 chunk 共 {sum(int(r['total']) for r in bad):,} 個")

    maybe = [r for r in out if r["kind"] == "serial-pdf"]
    if maybe:
        print(f"\nPDF 且逐一遞增 {len(maybe)} 本——多半是一頁一 chunk，頁碼是真的；"
              f"要確認就抽幾本比對原書。")

    if args.out:
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
        print("\n已寫", args.out)


if __name__ == "__main__":
    main()
