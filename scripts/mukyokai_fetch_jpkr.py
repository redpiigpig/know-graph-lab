# -*- coding: utf-8 -*-
"""把日韓文無教會研究裡**開放全文**那批抓下來。

書目在 `data/mukyokai/jp-kr-bibliography.jsonl`（197 筆，2026-09-11 盤點）。
這一支只碰 `access == "open"` 的（74 筆）——其餘是 abstract／paywall／print，
沒有全文可抓，硬抓只會拿到登入頁或書目頁。

落地：Drive `研究資料\無教會主義\_jp-kr\`（Drive 是 canonical storage，
[[feedback_drive_canonical_storage]]）。**不上 R2**——PDF 整本是大檔，
R2 只放小衍生物（[[feedback_r2_small_derivatives_only]]）。

🚨 三個一定要驗的東西，少一個就會收進一堆「看起來成功」的垃圾：

  1. **Content-Type 必須是 PDF**。機構典藏被擋時回的是 200 的 HTML 登入頁，
     存下來副檔名還是 .pdf，檔案總管看不出來。
  2. **檔頭必須是 %PDF**。有些站回 200 + 空白 body。
  3. **大小不可過小**。一頁的錯誤頁也可能是合法 PDF。

  python -X utf8 scripts/mukyokai_fetch_jpkr.py --dry     # 只列要抓什麼
  python -X utf8 scripts/mukyokai_fetch_jpkr.py --run
  python -X utf8 scripts/mukyokai_fetch_jpkr.py --run --lang ko
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "data" / "mukyokai" / "jp-kr-bibliography.jsonl"
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\無教會主義\_jp-kr")
LEDGER = ROOT / "scripts" / "state" / "mukyokai_jpkr_ledger.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
PAUSE = 3.0          # 對方多是大學機構典藏，慢一點
MIN_BYTES = 20_000   # 比這小的多半是錯誤頁


def slug(r: dict) -> str:
    """檔名：語言_年_作者_題名前段_雜湊。雜湊防同名覆蓋。"""
    raw = f"{r.get('author','')}|{r.get('title','')}|{r.get('year','')}"
    h = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", f"{r.get('author','')}_{r.get('title','')}")[:60]
    return f"{r.get('lang','xx')}_{r.get('year','') or '____'}_{safe}_{h}"


def load_done() -> set[str]:
    if not LEDGER.exists():
        return set()
    out = set()
    for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("status") == "ok":
            out.add(d["slug"])
    return out


def note(rec: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + chr(10))


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), (r.headers.get("Content-Type") or "").lower()


def verify(body: bytes, ctype: str) -> str:
    """回空字串＝通過；否則回不通過的理由。"""
    if "pdf" not in ctype and not body.startswith(b"%PDF"):
        head = body[:200].decode("utf-8", "replace").replace(chr(10), " ")
        return f"不是 PDF（Content-Type={ctype[:40]}；開頭「{head[:60]}」）"
    if not body.startswith(b"%PDF"):
        return "Content-Type 說是 PDF，但檔頭不是 %PDF"
    if len(body) < MIN_BYTES:
        return f"只有 {len(body):,} bytes，太小，多半是錯誤頁"
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--lang", choices=["ja", "ko"])
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    rows = [json.loads(l) for l in BIB.read_text(encoding="utf-8").splitlines() if l.strip()]
    todo = [r for r in rows if r.get("access") == "open"]
    if args.lang:
        todo = [r for r in todo if r.get("lang") == args.lang]
    done = load_done()
    todo = [r for r in todo if slug(r) not in done]
    if args.limit:
        todo = todo[:args.limit]

    print(f"書目 {len(rows)} 筆；open {sum(1 for r in rows if r.get('access')=='open')} 筆；"
          f"本輪要抓 {len(todo)} 筆（已抓過 {len(done)}）")
    if not args.run:
        for r in todo[:20]:
            print(f"  {r.get('lang')} {r.get('year',''):>5} {str(r.get('author'))[:10]:12} "
                  f"{str(r.get('title'))[:38]:40} {(r.get('fulltext_url') or r.get('url'))[:60]}")
        print("\n加 --run 才會真的下載")
        return

    DRIVE.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for i, r in enumerate(todo, 1):
        url = r.get("fulltext_url") or r.get("url") or ""
        name = slug(r)
        label = f"{i:3}/{len(todo)} {r.get('lang')} {str(r.get('title'))[:30]:32}"
        if not url:
            print(f"{label} ✗ 沒有網址")
            note({"slug": name, "status": "no-url", **{k: r.get(k) for k in ("lang", "title", "author", "year")}})
            fail += 1
            continue
        try:
            body, ctype = fetch(url)
        except urllib.error.HTTPError as e:
            print(f"{label} ✗ HTTP {e.code}")
            note({"slug": name, "status": "http", "code": e.code, "url": url})
            fail += 1
            time.sleep(PAUSE)
            continue
        except Exception as e:  # noqa: BLE001
            print(f"{label} ✗ {type(e).__name__}")
            note({"slug": name, "status": "error", "error": type(e).__name__, "url": url})
            fail += 1
            time.sleep(PAUSE)
            continue
        why = verify(body, ctype)
        if why:
            print(f"{label} ✗ {why}")
            note({"slug": name, "status": "not-pdf", "why": why, "url": url, "bytes": len(body)})
            fail += 1
            time.sleep(PAUSE)
            continue
        out = DRIVE / f"{name}.pdf"
        out.write_bytes(body)
        print(f"{label} ✓ {len(body)/1024:,.0f} KB")
        note({"slug": name, "status": "ok", "url": url, "bytes": len(body),
              "file": str(out), **{k: r.get(k) for k in ("lang", "title", "author", "year", "venue")}})
        ok += 1
        time.sleep(PAUSE)

    print(f"\n成功 {ok}、失敗 {fail}。落地 {DRIVE}")
    print("🚨 失敗的多半是機構典藏擋機器人（HTTP 406／回登入頁），不是檔案不存在——"
          "帳本記著 url，可個別用瀏覽器補。")


if __name__ == "__main__":
    main()
