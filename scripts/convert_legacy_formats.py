# -*- coding: utf-8 -*-
"""把 parse_worker 讀不懂的舊格式轉成它讀得懂的，再交回佇列。

怎麼發現的（2026-09-16）：全館 5,336 本裡有 731 本沒轉錄，其中 **315 本
既不在 OCR 佇列、也沒有 parse_error** —— `parse_worker` 的佇列查詢寫死
`file_type=in.(pdf,epub,docx,txt)`，於是這些格式連被嘗試的機會都沒有，
自然也不會留下錯誤訊息。不在任何清單上，稽核看不到，就這樣躺了幾個月。
檔案全部好好在 Drive 上，一本都沒掉。

    .doc  189 本   →  .docx   LibreOffice（soffice --convert-to）
    .mobi  63 本   →  .epub   calibre（ebook-convert）
    .azw3   6 本   →  .epub   calibre
    .rtf    1 本   →  .docx   LibreOffice
    .chm   56 本   →  目前無解（需要 7-Zip 或 chmlib，兩個都沒裝）

作法：轉出來的檔放在**原檔旁邊、同檔名不同副檔名**，原檔保留不動
（Drive 是正本，見 CLAUDE.md）。成功才改 `ebooks.file_path` 與 `file_type`，
接著 `parse_worker` 下一輪就會自然撈到它（`parsed_at` 仍是 null）。

用法：
    python scripts/convert_legacy_formats.py status
    python scripts/convert_legacy_formats.py run --limit 20
    python scripts/convert_legacy_formats.py run --types doc,rtf
    python scripts/convert_legacy_formats.py run --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
EBOOK_CONVERT = Path(r"C:\Program Files\Calibre2\ebook-convert.exe")

# 來源副檔名 → (目標副檔名, 用哪個工具)
PLAN = {
    "doc": ("docx", "soffice"),
    "rtf": ("docx", "soffice"),
    "mobi": ("epub", "calibre"),
    "azw3": ("epub", "calibre"),
    # chm 沒有可用工具，刻意不列 —— 列了只會產生一堆失敗紀錄
}
MIN_BYTES = 2_000          # 轉出來小於這個就是失敗，別拿去騙後面的流程


def env():
    from dotenv import load_dotenv
    load_dotenv(REPO / ".env")
    return os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def rest(path: str, method: str = "GET", body=None):
    url, key = env()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{url}/rest/v1/{path}", data=data, method=method,
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "application/json", "Prefer": "return=representation"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    return json.loads(raw) if raw else []


def pending(types: list[str] | None = None) -> list[dict]:
    """還沒轉錄、而且是我們會轉的格式。

    同時收兩種狀態：`parse_error` 是 null（還沒被碰過，佇列修好之前的舊狀態），
    以及 `unsupported file_type:`（佇列修好之後 parse_worker 會這樣標）。
    """
    want = types or list(PLAN)
    q = ",".join(want)
    rows = rest(f"ebooks?parsed_at=is.null&file_type=in.({q})"
                f"&select=id,title,file_type,file_path,parse_error&order=file_type,id&limit=2000")
    out = []
    for r in rows:
        pe = r.get("parse_error")
        if pe and "unsupported file_type" not in pe:
            continue                     # 有別的錯（檔案不在之類），先別碰
        out.append(r)
    return out


def convert(src: Path, dst_ext: str, tool: str) -> Path | None:
    """轉一個檔。回傳產出的路徑，失敗回 None。

    轉到暫存目錄再搬過去：LibreOffice 與 calibre 都會在輸出目錄留下中間檔，
    直接寫進 Drive 會把那些垃圾一起同步上雲。
    """
    with tempfile.TemporaryDirectory(prefix="convert_") as td:
        tmp = Path(td)
        if tool == "soffice":
            if not SOFFICE.exists():
                print("    ⛔ 找不到 LibreOffice")
                return None
            argv = [str(SOFFICE), "--headless", "--norestore",
                    "--convert-to", dst_ext, "--outdir", str(tmp), str(src)]
        else:
            if not EBOOK_CONVERT.exists():
                print("    ⛔ 找不到 calibre ebook-convert")
                return None
            argv = [str(EBOOK_CONVERT), str(src), str(tmp / (src.stem + "." + dst_ext))]

        try:
            p = subprocess.run(argv, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=600)
        except subprocess.TimeoutExpired:
            print("    ✗ 轉檔逾時（10 分鐘）")
            return None
        made = list(tmp.glob(f"*.{dst_ext}"))
        if not made:
            tail = ((p.stdout or "") + (p.stderr or ""))[-200:].replace("\n", " ")
            print(f"    ✗ 沒有產出（exit {p.returncode}）{tail}")
            return None
        out = made[0]
        if out.stat().st_size < MIN_BYTES:
            print(f"    ✗ 產出只有 {out.stat().st_size} bytes，當作失敗")
            return None
        final = src.with_suffix("." + dst_ext)
        final.write_bytes(out.read_bytes())     # 原檔保留，轉出的放旁邊
        return final


def cmd_status(args) -> int:
    rows = pending()
    from collections import Counter
    c = Counter(r["file_type"] for r in rows)
    print(f"可轉換的待處理：{len(rows)} 本")
    for ft, n in sorted(c.items()):
        dst, tool = PLAN[ft]
        print(f"  .{ft:<5} {n:>4} 本  → .{dst}（{tool}）")
    # 順帶報一下轉不了的
    blocked = rest("ebooks?parsed_at=is.null&file_type=eq.chm&select=id&limit=2000")
    if blocked:
        print(f"\n  .chm   {len(blocked):>4} 本  → 目前無解（需要 7-Zip 或 chmlib，都沒裝）")
    print(f"\n工具：LibreOffice {'✓' if SOFFICE.exists() else '✗'}　"
          f"calibre {'✓' if EBOOK_CONVERT.exists() else '✗'}")
    return 0


def cmd_run(args) -> int:
    types = [t.strip() for t in args.types.split(",")] if args.types else None
    if types:
        bad = [t for t in types if t not in PLAN]
        if bad:
            print(f"⛔ 不會轉這些格式：{bad}（會的有 {list(PLAN)}）")
            return 1
    rows = pending(types)
    print(f"待轉 {len(rows)} 本，本輪做 {min(args.limit, len(rows))} 本")

    ok = fail = 0
    for r in rows[: args.limit]:
        src = Path(r.get("file_path") or "")
        ft = r["file_type"]
        dst_ext, tool = PLAN[ft]
        print(f"\n▶ [{ft}] {(r.get('title') or '')[:44]}")

        if not src.exists():
            drive = Path(str(src.drive) + os.sep) if src.drive else None
            if drive is not None and not drive.exists():
                print(f"  ⛔ {src.drive} 掛不上 —— Drive 卡住，整場停")
                return 3
            print("  ✗ 檔案不在")
            rest(f"ebooks?id=eq.{r['id']}", "PATCH", {"parse_error": f"file not found: {src}"})
            fail += 1
            continue

        if args.dry_run:
            print(f"  （dry-run）會轉成 {src.with_suffix('.' + dst_ext).name}")
            continue

        t0 = time.time()
        out = convert(src, dst_ext, tool)
        if not out:
            rest(f"ebooks?id=eq.{r['id']}", "PATCH",
                 {"parse_error": f"convert failed: {ft}->{dst_ext}"})
            fail += 1
            continue

        # 轉好了才改指向；parse_error 清掉讓 parse_worker 下一輪撈得到
        rest(f"ebooks?id=eq.{r['id']}", "PATCH",
             {"file_path": str(out), "file_type": dst_ext, "parse_error": None})
        ok += 1
        print(f"  ✓ {out.name}（{out.stat().st_size / 1024:.0f} KB，{time.time() - t0:.0f}s）")

    print(f"\n完成 {ok} 本、失敗 {fail} 本")
    if ok:
        print("→ 下一輪 parse_worker 會自動撈到它們（parsed_at 仍是 null）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status", help="還有幾本待轉")
    s.set_defaults(func=cmd_status)
    r = sub.add_parser("run", help="轉檔")
    r.add_argument("--limit", type=int, default=20)
    r.add_argument("--types", help="只轉某些格式，逗號分隔，例如 doc,rtf")
    r.add_argument("--dry-run", action="store_true")
    r.set_defaults(func=cmd_run)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
