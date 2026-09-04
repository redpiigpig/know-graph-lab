#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把各處的「想要的書」彙整成一份 zlib_fetch 吃得下的清單。

三個來源：
  1. data/zlib-wanted/*.jsonl —— 人工策展的主題書單（聖經研究、基督教史、神學方法
     論、宗教學、宗教史、佛教與性別、佛教史、佛學、佛典考據與批判研究，以及小黑書
     那一系列的英文原著）。這些直接就是目標格式。
  2. .claude/skills/ebook-collected-works/z-library_獵表_全集中譯.txt —— 全集作家
     尚未收錄的著作（1,100 餘筆），找的是**中譯本**。
  3. 同資料夾的 基督宗教研究_中譯獵表.txt —— 同格式。

輸出 output/zlib_wanted_all.jsonl（中繼，不進版控），交
`node scripts/zlib_fetch.mjs --list` 逐日消化。

  python scripts/zlib_wanted.py                # 產生合併清單
  python scripts/zlib_wanted.py --stats        # 只看統計
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import author_blacklist

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "zlib-wanted"
SKILL = ROOT / ".claude" / "skills" / "ebook-collected-works"
HUNT_FILES = [
    (SKILL / "z-library_獵表_全集中譯.txt", "collected-works-hunt"),
    (SKILL / "基督宗教研究_中譯獵表.txt", "christianity-studies-hunt"),
]
OUT = ROOT / "output" / "zlib_wanted_all.jsonl"

# 一天只抓得到十本，六千多筆照雜湊亂序排等於永遠輪不到正在寫的那幾本。
# 排序依據是「為什麼現在需要這本書」——有時程壓力的排前面：
#   10 學位論文（送件有期限）
#   20 下學期要開的講義（開課前要備齊）
#   30 正在改寫成期刊論文的稿子
#   40 書籍寫作（長期，沒有硬期限）
#   60 主題策展書單（想讀，但不擋任何進度）
# 數字留空隙，之後插新計畫不必重排。
PRIORITY = {
    "biblio-hcu-phd": 10,
    "biblio-christianity-intro": 20,
    "biblio-world-religions-intro": 20,
    "biblio-sinographic-literature": 20,
    "biblio-yinshun-shengyan": 30,
    "biblio-bajingfa": 30,
    "biblio-pong-pastoral-spirituality": 30,
    "biblio-genesis-philosophy": 40,
    "biblio-mahaprajapati-revolution": 40,
    "biblio-theological-studies-manifesto": 40,
    "biblio-bachelor-evangelical": 50,
}
DEFAULT_PRIORITY = 60


def prioritize(items: list[dict]) -> list[dict]:
    """依 PRIORITY 分層，層內在各來源之間輪流取，同一本書中譯排在原文前面。

    層內輪流是刻意的：genesis-philosophy 一家就佔了三分之一，照來源整批排會讓
    它獨吞好幾個月的額度，其餘計畫全部餓死。
    中譯排前面是因為使用者讀中文最快；原文那一格晚幾天到不影響。
    """
    from collections import defaultdict, deque

    buckets: dict[int, dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
    for it in items:
        src = it.get("source", "")
        # 同一本書的兩格：-zh 先、-orig 後
        buckets[PRIORITY.get(src, DEFAULT_PRIORITY)][src].append(it)
    for tier in buckets.values():
        for src, q in tier.items():
            ordered = sorted(q, key=lambda x: (0 if x["key"].endswith("-zh") else 1, x["key"]))
            tier[src] = deque(ordered)

    out: list[dict] = []
    for lvl in sorted(buckets):
        srcs = list(buckets[lvl])
        while any(buckets[lvl][s] for s in srcs):
            for s in srcs:
                if buckets[lvl][s]:
                    out.append(buckets[lvl][s].popleft())
    return out

_AUTHOR_RE = re.compile(r"^\s*▍\s*(.+?)\s*(?:\((.+?)\))?\s*(?:約?\s*[前\d].*)?$")
_WANT_RE = re.compile(r"^\s*\[需獵\]\s*《(.+?)》(?:\s*（(.+?)）)?")
# 基督宗教研究那份是另一種排版：一行一本，[領域] 作者｜《書名》 譯者 / 出版社
_CHR_RE = re.compile(r"^\[(?P<field>[^\]]+)\]\s*(?P<author>[^｜|]+)[｜|]\s*《(?P<title>[^》]+)》")


def _stable_key(*parts: str) -> str:
    """内建 hash() 每次執行的結果都不一樣（PYTHONHASHSEED 隨機），拿來當帳本的鍵
    等於每天重抓同一批書。要用穩定雜湊。"""
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]


def parse_hunt(text: str, source: str) -> list[dict]:
    """獵表 txt → 目標格式。作家行以 ▍ 起頭，其下的 [需獵] 行是要找的書。"""
    out: list[dict] = []
    author_zh, author_en = "", ""
    for line in text.splitlines():
        if line.lstrip().startswith("▍"):
            m = _AUTHOR_RE.match(line)
            if m:
                author_zh = (m.group(1) or "").strip()
                author_en = (m.group(2) or "").strip()
            continue
        m = _WANT_RE.match(line)
        if not m or not author_zh:
            continue
        title_zh = m.group(1).strip()
        title_orig = (m.group(2) or "").strip()
        key = "hunt-" + _stable_key(author_zh, title_zh)
        out.append({
            "key": key,
            # 找的是中譯本，所以用中文書名＋作者名去搜
            "query": f"{title_zh} {author_zh}".strip(),
            "expect": title_zh,
            "who": author_zh,
            "source": source,
            "zh": f"{author_zh}《{title_zh}》",
            **({"orig": title_orig} if title_orig else {}),
        })
    return out


def parse_christianity(text: str, source: str) -> list[dict]:
    """基督宗教研究獵表 → 目標格式。這份的重點是「有沒有中譯本」，所以照樣搜中文。"""
    out: list[dict] = []
    for line in text.splitlines():
        m = _CHR_RE.match(line)
        if not m:
            continue
        author = re.sub(r"（.*?）", "", m.group("author")).strip()
        title = m.group("title").strip()
        out.append({
            "key": "chr-" + _stable_key(author, title),
            "query": f"{title} {author}".strip(),
            "expect": title,
            "who": author,
            "source": source,
            "zh": f"{author}《{title}》",
            "field": m.group("field"),
        })
    return out


def load_curated() -> list[dict]:
    out = []
    for f in sorted(CURATED.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    items = load_curated()
    for path, source in HUNT_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        items += parse_hunt(text, source) + parse_christianity(text, source)

    seen, merged, banned = set(), [], []
    for it in items:
        if it["key"] in seen:
            continue
        seen.add(it["key"])
        # 使用者判定不值得讀的作者，連搜都不要搜（data/author-blacklist.json）
        hit = author_blacklist.match(it.get("who", ""), it.get("zh", ""), it.get("query", ""))
        if hit:
            banned.append((hit["name"], it.get("zh") or it.get("query", "")))
            continue
        merged.append(it)

    by_source: dict[str, int] = {}
    for it in merged:
        by_source[it["source"]] = by_source.get(it["source"], 0) + 1
    for s, n in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {s:28} {n:5}")
    print(f"  {'合計':28} {len(merged):5}")
    if banned:
        print(f"\n  黑名單濾掉 {len(banned)} 筆：")
        for who, what in banned[:10]:
            print(f"    [{who}] {what}")
        if len(banned) > 10:
            print(f"    …另 {len(banned) - 10} 筆")

    if a.stats:
        return
    merged = prioritize(merged)
    print("\n排序後前 12 筆（先做的）：")
    for it in merged[:12]:
        print(f"  [{it.get('source', '')[:28]:28}] {it.get('zh') or it.get('query', '')[:46]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for it in merged:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
