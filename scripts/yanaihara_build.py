#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""矢內原忠雄（1893–1961）青空文庫四篇 → /collected-works 神學區。

內村鑑三的弟子、無教會主義第二代領袖；卒 1961 → 日本與台灣皆已公有領域
（[[project_uchimura_yanaihara]]）。青空文庫這四篇是新字新假名的乾淨電子文本，
零 OCR，是這位作家最省力的起手線；《帝国主義下の台湾》要走 NDL IIIF＋OCR，另辦。

本檔只提供「作家層」的東西——registry、來源檔、metadata——解析與翻譯 driver 全部
沿用內村那一套（uchimura_build 的青空 XHTML 解析、uchimura_auto 的續傳翻譯佇列）：

  python scripts/uchimura_auto.py --author yanaihara --list
  python scripts/uchimura_auto.py --author yanaihara --work final-lecture --upload
  python scripts/uchimura_auto.py --author yanaihara --run-queue

來源檔 2026-09-02 節流抓下，存 c:/tmp/yanaihara_cache/。
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import uchimura_build as ub  # noqa: E402  (載 .env、青空 XHTML 解析、stdout 轉碼)

CACHE_DIR = Path("c:/tmp/yanaihara_cache")
# ja→繁中的引擎鏈與內村共用（同一種文本、同一條 Gemini→NVIDIA→Haiku）。
make_engine = ub.make_engine
DATA_DIRNAME = "yanaihara_data"
AUTHOR_ZH = "矢內原忠雄"
AUTHOR_EN = "Yanaihara Tadao"
CATEGORY = "神學"

# deterministic 命名空間 e0000000-…（a=印順 b=聖嚴 c=星雲 d=內村 → e=矢內原）
REGISTRY: dict[str, dict] = {
    "final-lecture": {
        "ebook_id": "e0000000-0000-4000-8000-000000000001",
        "title": "帝大聖經研究會終講之辭",
        "original_title": "帝大聖書研究会終講の辞",
        "subtitle": "一九三七年因〈國家的理想〉去職前的最後一講（日文原文＋繁中對照）",
        "year": 1937,
        "parent_volume": "時論與信仰",
        "files": ["52208_46235.html"],
    },
    "reading-and-writing": {
        "ebook_id": "e0000000-0000-4000-8000-000000000002",
        "title": "讀書與著書",
        "original_title": "読書と著書",
        "subtitle": "論讀書之道與著述之責（日文原文＋繁中對照）",
        "year": 1938,
        "parent_volume": "時論與信仰",
        "files": ["55956_50928.html"],
    },
    "christianity-intro": {
        "ebook_id": "e0000000-0000-4000-8000-000000000003",
        "title": "基督教入門",
        "original_title": "キリスト教入門",
        "subtitle": "《嘉信》一九五一年連載，一九五二年角川書店成書（日文原文＋繁中對照）",
        "year": 1952,
        "parent_volume": "信仰與人物",
        "files": ["60192_74816.html"],
    },
    "jesus-life": {
        "ebook_id": "e0000000-0000-4000-8000-000000000004",
        "title": "耶穌傳：據馬可福音",
        "original_title": "イエス伝　マルコ伝による",
        "subtitle": "《聖書講義》第一卷（一九四八；初出一九四〇嘉信文庫講話）（日文原文＋繁中對照）",
        "year": 1948,
        "parent_volume": "聖書講義",
        "files": ["60358_76776.html"],
    },
}

# 先短後長：兩篇短文當日就能見效，《耶穌傳》一百八十餘節排最後。
QUEUE = ["final-lecture", "reading-and-writing", "christianity-intro", "jesus-life"]


def load_work_sections(slug: str, cache_dir: Path = CACHE_DIR) -> list[dict]:
    """與 uchimura_build.load_work_sections 同介面，換一個快取目錄與 registry。"""
    out: list[dict] = []
    for name in REGISTRY[slug]["files"]:
        raw = (cache_dir / name).read_bytes()
        doc = ub.parse_aozora(ub.decode_aozora(raw))
        for sec in doc["sections"]:
            paras = ub.split_long_paras(sec["paras"])
            if paras:
                out.append({"heading": sec["heading"], "paras": paras})
    return out


def main():
    total = 0
    for slug in QUEUE:
        secs = load_work_sections(slug)
        paras = sum(len(s["paras"]) for s in secs)
        chars = sum(len(p) for s in secs for p in s["paras"])
        total += chars
        w = REGISTRY[slug]
        print(f"{slug:22} {w['title']:14} sections={len(secs):4} paras={paras:5} {chars:8,} 字")
    print(f"\n合計 {total:,} 日文字")


if __name__ == "__main__":
    main()
