# -*- coding: utf-8 -*-
"""抓弘誓/玄奘 歷屆學術活動 — 改走 Wayback Machine（hongshi 本站被 Cloudflare 持續限流）。

archive.org 非 Cloudflare，純 requests 即可。用 `<ts>id_` raw 修飾抓原始頁（無 wayback 工具列）。
產 C:/tmp/hongshi_dl/meeting/meet-<n>.json，之後 hongshi_publish_meeting.py 上架。

  python -X utf8 scripts/hongshi_meeting_wayback.py
"""
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DIR = Path(r"C:/tmp/hongshi_dl/meeting"); DIR.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (KGL research-data archive fetch)"}
IDX = "https://www.hongshi.org.tw/meeting-B.php"
NAV = re.compile(r"最新消息|弘誓學團|護持捐款|友善連結")


def wb_raw(url: str) -> str | None:
    """Closest Wayback snapshot of url, fetched raw (no toolbar). None if unarchived."""
    for attempt in range(4):
        try:
            a = requests.get("http://archive.org/wayback/available", params={"url": url}, headers=UA, timeout=40)
            snap = a.json().get("archived_snapshots", {}).get("closest", {})
            if not snap.get("available"):
                return None
            ts = snap["timestamp"]
            raw = f"http://web.archive.org/web/{ts}id_/{url}"
            r = requests.get(raw, headers=UA, timeout=60)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception:  # noqa: BLE001
            time.sleep(5 * (attempt + 1))
    return None


def main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select('[id^="wm-"], script, style, nav, header, footer'):
        el.decompose()
    best, blen = "", 0
    for el in soup.find_all(["div", "article", "section", "td", "main"]):
        tx = el.get_text("\n", strip=True)
        if 40 < len(tx) < 80000 and len(tx) > blen and not NAV.search(tx[:40]):
            blen, best = len(tx), tx
    return re.sub(r"\n{3,}", "\n\n", best).strip()


def main():
    idx_html = wb_raw(IDX)
    if not idx_html:
        raise SystemExit("meeting-B.php not in Wayback")
    soup = BeautifulSoup(idx_html, "html.parser")
    items = {}
    for a in soup.find_all("a", href=True):
        m = re.search(r"meeting-B-page\.php\?n=(\d+)", a["href"])
        if m:
            n = int(m.group(1))
            items.setdefault(n, (a.get_text(strip=True) or "")[:80])
    nums = sorted(items, reverse=True)
    print(f"index: {len(nums)} activities (n {min(nums)}–{max(nums)})", flush=True)
    Path(DIR / "_index.json").write_text(
        json.dumps([{"n": n, "title": items[n]} for n in nums], ensure_ascii=False, indent=2), encoding="utf-8")

    ok = skip = miss = 0
    for n in nums:
        fn = DIR / f"meet-{n}.json"
        if fn.exists():
            skip += 1
            continue
        html = wb_raw(f"https://www.hongshi.org.tw/meeting-B-page.php?n={n}")
        if not html:
            print(f"  ⚠ n={n} not archived", flush=True); miss += 1; time.sleep(1); continue
        text = main_text(html)
        if len(text) < 40:
            print(f"  ∅ n={n} thin ({len(text)}c)", flush=True); miss += 1; time.sleep(1); continue
        fn.write_text(json.dumps({"n": n, "title": items[n], "text": text}, ensure_ascii=False, indent=2), encoding="utf-8")
        ok += 1
        if ok % 10 == 0 or ok < 3:
            print(f"  ✓ n={n} {len(text)}c ({ok})", flush=True)
        time.sleep(1.5)   # polite to archive.org
    print(f"\nDONE ok={ok} skip={skip} missing={miss}", flush=True)


if __name__ == "__main__":
    main()
