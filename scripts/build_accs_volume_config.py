#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掃描下載處的校園版 ACCS 掃描 PDF → 產生 OCR 設定檔 accs_volume_config.json。

單書卷：直接可跑（book_code + 整卷頁範圍；書前後版權/序/目錄/索引頁 OCR 會回空自動跳過）。
多書卷：標 needs_boundaries（純圖像掃描無書籤，須一趟 vision 找各書卷起始頁後補 ranges）。
不 OCR、不入庫；只產生設定。NT 優先排序。
"""
import glob
import json
import os
import re

import fitz

DL = r"C:\Users\user\Downloads"
OUT = os.path.join(os.path.dirname(__file__), "accs_volume_config.json")

# 檔名編號 → 有序書卷代碼（對齊 bible_books.code）。單元素=單書卷。
VOL_BOOKS = {
    "11-17": ["1ki", "2ki", "1ch", "2ch", "ezr", "neh", "est"],
    "18":    ["job"],
    "19a":   ["psa"],   # 诗1-50
    "19b":   ["psa"],   # 诗51-150
    "20-22": ["pro", "ecc", "sng"],
    "23a":   ["isa"],   # 赛1-39
    "23b":   ["isa"],   # 赛40-66
    # 24-25 耶利米書/哀歌：未購得，缺
    "26-27": ["ezk", "dan"],
    "28-39": ["hos", "jol", "amo", "oba", "jon", "mic",
              "nam", "hab", "zep", "hag", "zec", "mal"],
    "40a":   ["mat"],   # 太1-13
    "40b":   ["mat"],   # 太14-28
    "41":    ["mrk"],
    "42":    ["luk"],
    "43a":   ["jhn"],   # 约1-10
    "43b":   ["jhn"],   # 约11-21
    "44":    ["act"],
    "45":    ["rom"],
    "46-47": ["1co", "2co"],
    "48-50": ["gal", "eph", "php"],
    "51-57": ["col", "1th", "2th", "1ti", "2ti", "tit", "phm"],
    "58":    ["heb"],
    "59-65": ["jas", "1pe", "2pe", "1jn", "2jn", "3jn", "jud"],
    "66":    ["rev"],
}
# NT 優先：mat…rev 先，OT 後
NT_ORDER = ["40a", "40b", "41", "42", "43a", "43b", "44", "45",
            "46-47", "48-50", "51-57", "58", "59-65", "66"]


def vol_key(name: str) -> str:
    """由檔名判定 VOL_BOOKS 的 key（處理同號分冊 a/b）。"""
    m = re.search(r"丛书\s*([\d]+(?:-[\d]+)?)", name)
    base = m.group(1) if m else "?"
    if base == "19":
        return "19a" if "1-50" in name else "19b"
    if base == "23":
        return "23a" if ("1-39" in name or "1—39" in name) else "23b"
    if base == "40":
        return "40a" if ("1-13" in name) else "40b"
    if base == "43":
        return "43a" if ("1-10" in name) else "43b"
    return base


def main():
    files = sorted(glob.glob(os.path.join(DL, "古代基督信仰圣经注释丛书*.pdf")))
    cfg = []
    for f in files:
        name = os.path.basename(f)
        key = vol_key(name)
        books = VOL_BOOKS.get(key)
        if not books:
            print(f"  ⚠ 未對應書卷: {name}")
            continue
        d = fitz.open(f)
        pages = d.page_count
        d.close()
        cfg.append({
            "pdf": f,
            "vol_key": key,
            "books": books,
            "page_count": pages,
            "single_book": len(books) == 1,
            "testament": "NT" if key in NT_ORDER else "OT",
            # 單書卷：整卷一個 range，前後雜頁靠 prompt 回空自動跳過
            # 多書卷：待 vision 定界後填 [{book, pages}]
            "ranges": ([{"book": books[0], "pages": f"1-{pages}"}]
                       if len(books) == 1 else None),
            "status": "ready" if len(books) == 1 else "needs_boundaries",
        })
    # 排序：NT 單書卷 → NT 多書卷 → OT 單書卷 → OT 多書卷
    def sort_key(c):
        t = 0 if c["testament"] == "NT" else 2
        s = 0 if c["single_book"] else 1
        idx = NT_ORDER.index(c["vol_key"]) if c["vol_key"] in NT_ORDER else 99
        return (t + s, idx, c["vol_key"])
    cfg.sort(key=sort_key)
    json.dump(cfg, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ready = [c for c in cfg if c["status"] == "ready"]
    need = [c for c in cfg if c["status"] == "needs_boundaries"]
    tot = sum(c["page_count"] for c in cfg)
    print(f"\n設定檔 → {OUT}")
    print(f"共 {len(cfg)} 卷 / {tot} 頁")
    print(f"\n可直接跑（單書卷）{len(ready)} 卷：")
    for c in ready:
        print(f"  [{c['testament']}] {c['books'][0]:<4} {c['page_count']:>4}p  {os.path.basename(c['pdf'])[:36]}")
    print(f"\n待 vision 定界（多書卷）{len(need)} 卷：")
    for c in need:
        print(f"  [{c['testament']}] {'+'.join(c['books'])}  {c['page_count']}p  {os.path.basename(c['pdf'])[:32]}")


if __name__ == "__main__":
    main()
