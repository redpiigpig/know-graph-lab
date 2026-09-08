#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《基督宗教譜系學》的查料工具：在一組指定的參考書全文裡做跨書檢索。

全文正本在 Drive 的 `知識圖工作室/_chunks/{ebook_id}.jsonl`（DB 的 ebook_chunks 只有
preview，查不到東西）。本腳本只讀那批 JSONL，不動 DB、不上網。

用法：
  python scripts/genealogy_research.py 尼西亞 亞流            # 全部書源，AND 條件
  python scripts/genealogy_research.py --set reformation 重洗派
  python scripts/genealogy_research.py --book gonzalez 宗主教 --width 500
  python scripts/genealogy_research.py --list                 # 列出書源與書組

輸出到 stdout，每筆一段：書名、頁碼、章節路徑、命中前後文。頁碼直接抄自原書
（[[feedback_pdf_page_number]]：page_number 是原書頁碼，不是重編的序號），可以直接
寫進註腳。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CHUNKS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")

# 書源：短名 → (ebook_id, 註腳用的書目)
SOURCES: dict[str, tuple[str, str]] = {
    # 通史
    "gonzalez": ("342203a6-198d-44f1-9816-16f95bdbc722",
                 "岡薩雷斯（Justo L. González）著，趙城藝譯，《基督教史》（上海：上海三聯書店，2016）"),
    "cambridge": ("af612eee-f1c6-425a-8d73-0cdbfcf9b053",
                  "《劍橋基督教史》（九卷本，中譯）"),
    "wangmeixiu": ("c811ff89-9a15-4fa1-af57-3235d6c2b36f",
                   "王美秀等，《基督教史》"),
    "youbin": ("497667ba-f783-4ce3-bcf4-021b45c8970e", "遊斌，《基督教史綱》"),
    # 畢爾麥爾三冊
    "bihlmeyer-ancient": ("f81a9514-7e55-48c6-a41c-9d4ed4ce5455",
                          "畢爾麥爾（Karl Bihlmeyer）等，《古代教會史》（北京：宗教文化出版社）"),
    "bihlmeyer-medieval": ("3f72d1a6-245b-44cc-9527-6e9b0d49cd7d",
                           "畢爾麥爾等，《中世紀教會史》（北京：宗教文化出版社，2010）"),
    "bihlmeyer-modern": ("1ea6134a-9fe8-4a74-a85d-44f0ec22414f",
                         "畢爾麥爾等，《近代教會史：從宗教改革到現代時期（1517-1950年）》"
                         "（北京：宗教文化出版社，2011）"),
    # 原典與信條
    "eusebius": ("e35a97b1-368b-46c6-9c38-1159501fbf12", "優西比烏，《教會史》"),
    "bede": ("31f39f65-d446-4128-8080-025a4cec9b6a", "比德，《英吉利教會史》"),
    "councils": ("919a1f54-4bb6-4b59-b3d9-311aed018022",
                 "Philip Schaff ed., NPNF2 Vol. 14: The Seven Ecumenical Councils"),
    "creeds1": ("783b1fcf-9095-4959-82da-862df3ef1d15",
                "Philip Schaff, Creeds of Christendom, Vol. 1: The History of Creeds"),
    "creeds2": ("960a55e9-0767-4e46-a9f5-30b04b31a33b",
                "Philip Schaff, Creeds of Christendom, Vol. 2: The Greek and Latin Creeds"),
    "creeds3": ("c1c8ca9f-4eb2-404c-84cf-db3a9f9768f8",
                "Philip Schaff, Creeds of Christendom, Vol. 3: The Evangelical Protestant Creeds"),
    "creeds-zh": ("bc240569-b9ce-44ec-b6f0-94b2a0fb60bd", "《歷代信經信條》（2023）"),
    # 新教
    "mcgrath": ("4170547c-e0a5-494e-a336-b2048911bb12",
                "麥格夫（Alister McGrath），《宗教改革運動思潮》"),
    "lindsay": ("bc1481a5-e280-4964-81dd-44795e522095",
                "林賽（Thomas M. Lindsay），《宗教改革史（上冊）》"),
    "protestant-encyc": ("c0fb6a16-31ff-447b-af90-b4e2c26d1c33", "《新教百科全書》"),
    "pentecostal": ("df754d5b-723d-4fe7-a34e-97a5c50745f5",
                    "劉義，《全球靈恩運動與基督教》"),
    # 東方
    "moffett1": ("a0602e5a-d023-4c9c-a8df-9fd9d2263dc9",
                 "莫菲特（Samuel H. Moffett），《亞洲基督教史》第一卷"),
    "moffett2": ("943689fd-5089-4ac2-9007-b0c6ba1b9038", "莫菲特，《亞洲基督教史》第二卷"),
    "china1550": ("4fe57c5d-4de7-4f32-bf84-fc937cfb8511", "阿克穆爾，《1550年前的中國基督教史》"),
    "orthodox-catechism": ("f97b77e5-7367-473d-8beb-2178acf0b549", "《東正教教理問答》"),
    "russia-orthodox": ("8497e1b0-b9f0-405f-9da1-db3fa45df039", "《俄羅斯東正教與文化》"),
    # 天主教近現代
    "vat2-docs": ("ff006b9d-8399-462d-b7ec-a52e16086db3",
                  "《天主教梵蒂岡第二屆大公會議文獻》（信德社版）"),
    "vat2-history": ("995b4697-81d9-4f3e-969d-4df9c54103be", "《梵蒂岡第二屆大公會議簡史》"),
    "vat2-journey": ("7f86b459-9885-482f-a0b7-465a64dfd0a4", "《梵二開啟的旅程》"),
}

# 書組：按卷次把常用的書源綁起來
SETS: dict[str, list[str]] = {
    "all": list(SOURCES),
    "early": ["eusebius", "gonzalez", "cambridge", "bihlmeyer-ancient", "moffett1", "creeds1"],
    "nicaea": ["councils", "creeds1", "creeds2", "bihlmeyer-ancient", "gonzalez", "cambridge"],
    "traditions": ["moffett1", "moffett2", "china1550", "orthodox-catechism",
                   "bihlmeyer-medieval", "cambridge", "creeds2", "bede"],
    "reformation": ["mcgrath", "lindsay", "bihlmeyer-modern", "creeds3", "protestant-encyc",
                    "gonzalez", "cambridge"],
    "modern": ["vat2-docs", "vat2-history", "vat2-journey", "pentecostal",
               "protestant-encyc", "russia-orthodox", "bihlmeyer-modern"],
}


def load(short: str):
    eid, cite = SOURCES[short]
    p = CHUNKS / f"{eid}.jsonl"
    if not p.exists():
        print(f"（缺全文：{short} {cite}）", file=sys.stderr)
        return
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("terms", nargs="*", help="全部要出現才算命中（AND）")
    ap.add_argument("--set", default="all", help=f"書組：{'/'.join(SETS)}")
    ap.add_argument("--book", action="append", help="只查這些書源（可重複），蓋過 --set")
    ap.add_argument("--width", type=int, default=320, help="命中前後各取幾個字")
    ap.add_argument("--max", type=int, default=40, help="最多印幾筆")
    ap.add_argument("--list", action="store_true", help="列出書源與書組")
    args = ap.parse_args()

    if args.list:
        print("書源：")
        for k, (eid, cite) in SOURCES.items():
            ok = "○" if (CHUNKS / f"{eid}.jsonl").exists() else "✕"
            print(f"  {ok} {k:22s} {cite}")
        print("\n書組：")
        for k, v in SETS.items():
            print(f"  {k:14s} {', '.join(v)}")
        return 0

    if not args.terms:
        ap.error("要給關鍵詞")

    books = args.book or SETS.get(args.set) or ap.error(f"沒有這個書組：{args.set}")
    pats = [re.compile(t) for t in args.terms]
    hits = 0
    for short in books:
        cite = SOURCES[short][1]
        for c in load(short):
            text = c.get("content") or ""
            if not all(p.search(text) for p in pats):
                continue
            m = pats[0].search(text)
            a = max(0, m.start() - args.width)
            b = min(len(text), m.end() + args.width)
            snippet = re.sub(r"\s+", " ", text[a:b]).strip()
            hits += 1
            print(f"\n── [{short}] {cite}")
            print(f"   頁 {c.get('page_number')}　{c.get('chapter_path') or ''}")
            print(f"   …{snippet}…")
            if hits >= args.max:
                print(f"\n（已達上限 {args.max} 筆，用 --max 放寬）")
                return 0
    print(f"\n共 {hits} 筆命中（書組 {args.set}，{len(books)} 本）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
