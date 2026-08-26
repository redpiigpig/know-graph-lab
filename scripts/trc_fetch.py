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


RETRIES = 4           # 暫時性網路錯誤重試次數
BACKOFF = 15.0        # 首次重試前等待秒數，逐次加倍


def keep_awake(on: bool = True) -> None:
    """下載期間告訴 Windows「系統忙碌中」，擋掉閒置待機。

    只用 ES_SYSTEM_REQUIRED、不用 ES_DISPLAY_REQUIRED——螢幕照常關。
    **蓋上蓋子仍照常睡**（lid action 永遠優先於這個旗標），正是要的行為：
    機器閒著別自己睡，但闔上就該睡。
    """
    if sys.platform != "win32":
        return
    import ctypes
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(
        (ES_CONTINUOUS | ES_SYSTEM_REQUIRED) if on else ES_CONTINUOUS)


def with_retry(fn, what: str):
    """暫時性網路錯誤重試。

    從待機恢復的頭幾秒網路還沒起來，`getaddrinfo failed` 與
    `RemoteDisconnected` 都會冒出來——這類該重試，不該計為失敗。
    """
    delay = BACKOFF
    for i in range(RETRIES):
        try:
            return fn()
        except (requests.ConnectionError, requests.Timeout) as e:
            if i == RETRIES - 1:
                raise
            print(f"    ⟳ {what}：{type(e).__name__}，{delay:.0f} 秒後重試")
            time.sleep(delay)
            delay *= 2


def raw_url(path: str) -> tuple[str, int]:
    r = with_retry(lambda: requests.post(
        f"{BASE}/api/fs/get",
        headers={"Content-Type": "application/json", "User-Agent": UA},
        json={"path": path, "password": ""}, timeout=60,
    ), "取得連結")
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


LEDGER = Path("c:/tmp/trc_downloaded.json")


def load_ledger() -> dict:
    """已下載帳本：TRC 路徑 → {name, size}。

    只看目的資料夾判斷「已下載」是不夠的——檔案一旦入庫搬進 Drive 就從
    dest 消失，整批會被重抓，白白耗掉站方頻寬。帳本以站內路徑為鍵，
    檔案搬到哪都不影響判定。
    """
    if LEDGER.exists():
        try:
            return json.loads(LEDGER.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 帳本壞掉不該擋下載，重建即可
            return {}
    return {}


def save_ledger(led: dict) -> None:
    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")


def fetch_one(path: str, dest_dir: Path, author: str = "", dry: bool = False,
              led: dict | None = None) -> Path | None:
    if led is not None and path in led:
        print(f"  ✓ 帳本已記錄，跳過：{led[path]['name'][:56]}")
        return None
    url, size = raw_url(path)
    out = dest_dir / safe_name(path, author)
    if out.exists() and out.stat().st_size == size and size:
        print(f"  ✓ 已存在，跳過：{out.name}")
        if led is not None:
            led[path] = {"name": out.name, "size": size}
        return out
    print(f"  ↓ {out.name}  ({size / 1024 / 1024:.1f} MB)")
    if dry:
        return None
    tmp = out.with_suffix(out.suffix + ".part")

    def _pull() -> int:
        n = 0
        with requests.get(url, headers={"User-Agent": UA}, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()
            with tmp.open("wb") as fh:
                for blk in r.iter_content(CHUNK):
                    fh.write(blk)
                    n += len(blk)
        return n

    got = with_retry(_pull, out.name[:40])
    if size and got != size:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"體積不符：拿到 {got} 應為 {size}")
    tmp.replace(out)
    if led is not None:
        led[path] = {"name": out.name, "size": got}
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

    keep_awake(True)
    led = load_ledger()
    todo = [it for it in todo if it["path"] not in led]
    print(f"帳本已有 {len(led)} 筆，本輪待抓 {len(todo)} 檔\n")

    ok = fail = 0
    try:
        for i, it in enumerate(todo, 1):
            print(f"[{i}/{len(todo)}] {it['path']}")
            try:
                fetch_one(it["path"], dest, it.get("author", ""), a.dry_run, led)
                ok += 1
                if i % 10 == 0:
                    save_ledger(led)      # 中途被砍也不會整批重抓
            except Exception as e:  # noqa: BLE001 — 單檔失敗不中斷整批
                print(f"  ⚠ 失敗：{e}")
                fail += 1
            if i < len(todo) and not a.dry_run:
                time.sleep(a.delay)   # 一次一個檔、留間隔——不要拿掉
    finally:
        # 被外力終止時（先前整夜那輪就這樣沒了）帳本一樣要落盤
        if not a.dry_run:
            save_ledger(led)
        keep_awake(False)
    print(f"\n成功 {ok}，失敗 {fail}（帳本共 {len(led)} 筆）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
