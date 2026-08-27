#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從天主教在線（ziliaozhan.win）逐檔下載。使用者已取得授權作私人收藏。

🚨 比照 TRC 的規矩：一次一個檔、檔與檔之間留間隔，絕不並發。

  python scripts/zlz_fetch.py --list c:/tmp/zlz_todo.json [--limit 5] [--dry-run]

下載是三段式（帝國 CMS 的 DownSys）：
  ① 條目頁 /download/pdf/{cat}/{date}/{id}.html  → 抓 classid 與 id
  ② /e/DownSys/DownSoft/?classid=&id=&pathid=0   → 中介頁，內含 pass token
  ③ /e/DownSys/doaction.php?...&pass=...         → 302 轉 dl.ziliaozhan.win 拿檔
pass 是每次現算的，不能預先批次取，所以每檔都得走完整條鏈。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import to_traditional
from trc_fetch import keep_awake, with_retry     # 共用防待機與重試

BASE = "https://ziliaozhan.win"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
DROP = Path(__file__).resolve().parent.parent / "z-lib" / "zlz"
LEDGER = Path("c:/tmp/zlz_downloaded.json")
DELAY = 8.0
TIMEOUT = 300
CHUNK = 1 << 20
BAD_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

DOWNSOFT_RX = re.compile(r"/e/DownSys/DownSoft/\?classid=(\d+)&id=(\d+)&pathid=(\d+)")
DOACTION_RX = re.compile(r"(doaction\.php\?enews=DownSoft[^\"'\s]+)")


def ses() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    s.verify = False
    return s


def resolve(s: requests.Session, item_url: str) -> tuple[str, str]:
    """條目頁 → (最終下載網址, 伺服器給的檔名)。"""
    r = with_retry(lambda: s.get(item_url, timeout=60), "條目頁")
    r.encoding = r.apparent_encoding or "utf-8"
    m = DOWNSOFT_RX.search(r.text)
    if not m:
        raise RuntimeError("條目頁找不到下載連結")
    classid, rid, pathid = m.groups()
    inter = f"{BASE}/e/DownSys/DownSoft/?classid={classid}&id={rid}&pathid={pathid}"
    r2 = with_retry(lambda: s.get(inter, headers={"Referer": item_url}, timeout=60), "中介頁")
    r2.encoding = r2.apparent_encoding or "utf-8"
    m2 = DOACTION_RX.search(r2.text)
    if not m2:
        raise RuntimeError("中介頁找不到 doaction 連結")
    final = f"{BASE}/e/DownSys/{m2.group(1)}"
    # 先不下載內容，只跟到 302 取真實檔名
    h = s.get(final, headers={"Referer": inter}, timeout=60, stream=True, allow_redirects=True)
    name = ""
    for hop in (*h.history, h):
        loc = hop.headers.get("location") or hop.url
        if loc and re.search(r"\.(pdf|chm|zip|rar|epub|doc[x]?)$", unquote(loc), re.I):
            name = unquote(loc).split("/")[-1]
    h.close()
    return final, name


def fetch_one(s: requests.Session, item: dict, dest: Path, led: dict, dry: bool) -> bool:
    url = item["url"]
    if url in led:
        print(f"  ✓ 帳本已記錄，跳過：{led[url]['name'][:56]}")
        return True
    final, srvname = resolve(s, url)
    title = to_traditional(item.get("title") or Path(srvname).stem)
    ext = (Path(srvname).suffix or ".pdf").lower()
    out = dest / BAD_FS.sub("_", f"{title}{ext}")[:190]
    if out.exists() and out.stat().st_size > 4096:
        print(f"  ✓ 已存在，跳過：{out.name}")
        led[url] = {"name": out.name, "size": out.stat().st_size}
        return True
    print(f"  ↓ {out.name}")
    if dry:
        return True

    def _pull() -> int:
        n = 0
        tmp = out.with_suffix(out.suffix + ".part")
        with s.get(final, timeout=TIMEOUT, stream=True) as r:
            r.raise_for_status()
            ct = (r.headers.get("content-type") or "").lower()
            if "text/html" in ct:
                raise RuntimeError(f"拿到 HTML 不是檔案（{ct}）")
            with tmp.open("wb") as fh:
                for blk in r.iter_content(CHUNK):
                    fh.write(blk)
                    n += len(blk)
        tmp.replace(out)
        return n

    got = with_retry(_pull, out.name[:40])
    led[url] = {"name": out.name, "size": got}
    print(f"    完成 {got / 1024 / 1024:.1f} MB")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--dest", default=str(DROP))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=DELAY)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    import urllib3
    urllib3.disable_warnings()
    dest = Path(a.dest)
    dest.mkdir(parents=True, exist_ok=True)
    items = json.loads(Path(a.list).read_text(encoding="utf-8"))
    led = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    items = [i for i in items if i["url"] not in led]
    if a.limit:
        items = items[:a.limit]
    print(f"帳本已有 {len(led)} 筆，本輪待抓 {len(items)} 檔\n")

    s = ses()
    keep_awake(True)
    ok = fail = 0
    try:
        for i, it in enumerate(items, 1):
            print(f"[{i}/{len(items)}] {it.get('title','')[:56]}")
            try:
                fetch_one(s, it, dest, led, a.dry_run)
                ok += 1
                if i % 5 == 0 and not a.dry_run:
                    LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")
            except Exception as e:  # noqa: BLE001 — 單檔失敗不中斷整批
                print(f"  ⚠ 失敗：{e}")
                fail += 1
            if i < len(items) and not a.dry_run:
                time.sleep(a.delay)
    finally:
        if not a.dry_run:
            LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")
        keep_awake(False)
    print(f"\n成功 {ok}，失敗 {fail}（帳本 {len(led)} 筆）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
