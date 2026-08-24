#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從 TRC（thereformedcatholic.org / AList）逐檔下載。

🚨 站方資源有限（使用者明確要求）：**一次一個檔、檔與檔之間留間隔，
   絕不並發、絕不整批抓。** 這支刻意寫成序列式，沒有也不要加平行選項。

  python scripts/trc_fetch.py --path "/初代教會 Early Christianity/.../x.pdf"
  python scripts/trc_fetch.py --list c:/tmp/trc_todo.json --limit 5

下載落點預設 repo 的 z-lib/ 投放夾，接著就走既有 ingest：
  python scripts/ingest_new_books.py run
檔名會過 opencc s2tw（[[feedback_traditional_chinese_only]]）。

AList 的 raw_url 指向 OneDrive 個人版 CDN（my.microsoftpersonalcontent.com），
簽章有時效，所以每檔都是「臨下載前才要 URL」，不預先批次取。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import to_traditional

BASE = "https://thereformedcatholic.org/download"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DROP = Path(__file__).resolve().parent.parent / "z-lib"
DELAY = 8.0        # 檔與檔之間的間隔（秒）
TIMEOUT = 180
CHUNK = 1 << 20

BAD_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def raw_url(path: str) -> tuple[str, int]:
    r = requests.post(
        f"{BASE}/api/fs/get",
        headers={"Content-Type": "application/json", "User-Agent": UA},
        json={"path": path, "password": ""}, timeout=60,
    )
    r.raise_for_status()
    d = r.json()
    if d.get("code") != 200:
        raise RuntimeError(f"{path}: {d.get('code')} {d.get('message')}")
    data = d.get("data") or {}
    return data["raw_url"], data.get("size") or 0


def safe_name(path: str, author: str = "") -> str:
    """TRC 路徑 → 繁體檔名。有作者就湊成 ingest 認得的「作者，書名.ext」。"""
    stem = Path(path).stem
    ext = Path(path).suffix.lower()
    title = to_traditional(stem)
    name = f"{to_traditional(author)}，{title}{ext}" if author else f"{title}{ext}"
    name = BAD_FS.sub("_", name).strip()
    return name[:180] + ext if len(name) > 190 else name


def fetch_one(path: str, dest_dir: Path, author: str = "", dry: bool = False) -> Path | None:
    url, size = raw_url(path)
    out = dest_dir / safe_name(path, author)
    if out.exists() and out.stat().st_size == size and size:
        print(f"  ✓ 已存在，跳過：{out.name}")
        return out
    print(f"  ↓ {out.name}  ({size / 1024 / 1024:.1f} MB)")
    if dry:
        return None
    tmp = out.with_suffix(out.suffix + ".part")
    got = 0
    with requests.get(url, headers={"User-Agent": UA}, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with tmp.open("wb") as fh:
            for blk in r.iter_content(CHUNK):
                fh.write(blk)
                got += len(blk)
    if size and got != size:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"體積不符：拿到 {got} 應為 {size}")
    tmp.replace(out)
    print(f"    完成 {got / 1024 / 1024:.1f} MB → {out}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", help="單一 TRC 檔案路徑")
    ap.add_argument("--author", default="", help="檔名前綴作者")
    ap.add_argument("--list", help="JSON 清單：[{path, author?}, ...]")
    ap.add_argument("--dest", default=str(DROP))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=DELAY)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)

    todo: list[dict] = []
    if a.path:
        todo.append({"path": a.path, "author": a.author})
    if a.list:
        items = json.loads(Path(a.list).read_text(encoding="utf-8"))
        todo += items if isinstance(items, list) else items.get("files", [])
    if not todo:
        ap.error("要 --path 或 --list")
    if a.limit:
        todo = todo[:a.limit]

    ok = fail = 0
    for i, it in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {it['path']}")
        try:
            fetch_one(it["path"], dest, it.get("author", ""), a.dry_run)
            ok += 1
        except Exception as e:  # noqa: BLE001 — 單檔失敗不中斷整批
            print(f"  ⚠ 失敗：{e}")
            fail += 1
        if i < len(todo) and not a.dry_run:
            time.sleep(a.delay)     # 一次一個檔、留間隔——不要拿掉
    print(f"\n成功 {ok}，失敗 {fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
