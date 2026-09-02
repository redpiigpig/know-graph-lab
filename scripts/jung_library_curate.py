#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把圖書館裡的榮格中譯本歸位：該進全集的標進全集，沒轉錄成功的清掉。

2026-09-02：CW 十六卷上架後清點，圖書館還有九本 `collection` 是 NULL 的榮格書
（[[feedback_collected_works_not_in_library]]：全集作家的原著中譯本該歸全集）。
原檔都還在 Drive，差別在轉錄成不成功：

  * 六本 EPUB 早就轉錄好（14–84 chunks）→ 只要補 collection。
  * 《榮格自傳》EPUB 解析當掉（manifest 列了 OEBPS/Images/copyright.jpg 但檔案不在，
    ebooklib 直接 KeyError）→ 0 chunk，要改走 zipfile 路線重轉。
  * 兩本 PDF 各只有 1 chunk 865 字＝沒轉錄：塔維斯托克講演的內容 CW18 已經涵蓋，
    另一本連書名都還沒確認（93MB 掃描）→ 刪 row，Drive 原檔留著，哪天要 OCR 再建。

  python scripts/jung_library_curate.py --dry-run
  python scripts/jung_library_curate.py --apply
"""
from __future__ import annotations

import argparse
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]

# 標進全集（都已有實質內容）
PROMOTE = {
    "de58044e-d56c-478e-8e01-b11f40d3a157": "紅書（繁體）",
    "2feb39cd-22cb-4413-ad24-39dbd194779d": "榮格論心理類型（莊仲黎譯）",
    "82128c89-5313-409b-a3e2-f4de58eacff2": "伊雍：自性現象學研究（簡體全譯）",
    "f10da364-b449-4002-8661-e8e52be3617c": "未發現的自我",
    "cf2197ab-7bc3-40ce-a243-a748f4d6e85b": "英雄與母親",
    "708321c8-00be-4a9f-b84d-eced12ec4d81": "東方的智慧",
}

# 刪 row（Drive 原檔不動）
DROP = {
    "08e5c61a-558f-4487-b7bd-c8ce2c3aaa1f": "分析心理學的理論與實踐：塔維斯托克講演"
                                            "（1 chunk；內容已在 CW18）",
    "9f2137fd-47bd-4967-acd8-96cb1f8fe307": "榮格著作（徐说譯，書名待 OCR 確認；1 chunk）",
}

# 待重轉（parser 卡在缺圖）——本腳本不處理，見 jung_collected_works.md
PENDING = {"b920a143-b6c8-4aef-9dfb-87d956808058": "榮格自傳：回憶‧夢‧省思"}


def _env() -> tuple[str, str]:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"')
    return env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]


def _req(method: str, path: str, body: dict | None = None) -> tuple[int, str]:
    url, key = _env()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{url}/rest/v1/{path}", data=data, method=method,
                                 headers={"apikey": key, "Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:  # noqa: PERF203
        return e.code, e.read().decode()[:200]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真的寫入（預設只列）")
    a = ap.parse_args()

    for eid, title in PROMOTE.items():
        print(f"[標入全集] {title}")
        if a.apply:
            code, body = _req("PATCH", f"ebooks?id=eq.{eid}", {"collection": "collected-works"})
            print(f"           HTTP {code} {body if code >= 300 else ''}")
    for eid, why in DROP.items():
        print(f"[刪 row]   {why}")
        if a.apply:
            for path in (f"ebook_chunks?ebook_id=eq.{eid}", f"ebooks?id=eq.{eid}"):
                code, body = _req("DELETE", path)
                print(f"           HTTP {code} {body if code >= 300 else ''}")
    for title in PENDING.values():
        print(f"[待重轉]   {title}（EPUB 缺圖，ebooklib 解析當掉）")
    if not a.apply:
        print("\n（--dry-run 模式；加 --apply 才會寫入）")


if __name__ == "__main__":
    main()
