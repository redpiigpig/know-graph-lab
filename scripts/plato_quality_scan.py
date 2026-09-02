#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""哲學全集（plato_build 產出）的譯文健檢：抓「看起來像成功的失敗」。

2026-09-02 上傳亞氏三部時發現：《政治學》《歐德謨倫理學》有幾十個 chunk 的譯文
後半變成模型的逐字對照自語——
    "政", "體", "——", "之", "外", "，" … same. "對" same. "哪些" same.
——chunk 照樣寫檔、照樣上傳、reader 照樣顯示，只有字數異常大這一個外顯徵兆。
（[[feedback_reader_silent_failures]]：讀本／全集最危險的一類錯就是印得出來但內容錯。）

三個判準，任一中即列為受損：
  1. token 自語：連續的「引號包單字＋逗號」串，或反覆出現的 ` same.` / ` punctuation.`
  2. 體積異常：content 長度 > 該書中位數的 6 倍（正常一節 1–2 千字）
  3. 譯文裡混入大量英文句子（非引文級別）

  python scripts/plato_quality_scan.py                 # 掃 c:/tmp 全部 plato_*.jsonl
  python scripts/plato_quality_scan.py --work politics # 只看一部
  python scripts/plato_quality_scan.py --json          # 給後續清快取用
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

JSONL_DIR = Path("c:/tmp")
CACHE_DIR = Path("c:/tmp/plato_cache")

_TOKEN_BABBLE = re.compile(r'("[^"]{1,6}",\s*){4,}')       # "政", "體", "——", "之",
_SAME_TALK = re.compile(r'\b(same|punctuation|identical)\b\.?', re.I)
_LATIN_RUN = re.compile(r"[A-Za-z][A-Za-z ,.'’-]{60,}")


def flags_for(content: str) -> list[str]:
    """單一 chunk 的受損標記（純函式）。"""
    out = []
    if _TOKEN_BABBLE.search(content):
        out.append("token-babble")
    if len(_SAME_TALK.findall(content)) >= 3:
        out.append("same-talk")
    latin = sum(len(m.group(0)) for m in _LATIN_RUN.finditer(content))
    if latin > max(200, len(content) * 0.15):
        out.append("latin-bleed")
    return out


def scan_file(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    lengths = [len(r.get("content", "")) for r in rows] or [0]
    median = statistics.median(lengths) or 1
    bad = []
    for r in rows:
        content = r.get("content", "")
        fl = flags_for(content)
        if len(content) > median * 6:
            fl.append("oversize")
        if fl:
            bad.append({"chunk_index": r.get("chunk_index"),
                        "chapter_path": r.get("chapter_path"),
                        "anchors": r.get("anchors"),
                        "chars": len(content), "flags": fl})
    return {"work": path.stem.replace("plato_", ""), "chunks": len(rows),
            "median_chars": int(median), "bad": bad}


def purge_cache(slug: str, *, apply: bool) -> list[str]:
    """刪掉受損節的逐節翻譯快取，下一次 plato_build 就會重譯這幾節。

    直接對 `plato_cache/<slug>_zh/*.txt` 判斷，比回推 chunk→anchors 準：一個 chunk
    可能含兩節，壞的常常只有其中一節。
    """
    cdir = CACHE_DIR / f"{slug}_zh"
    if not cdir.is_dir():
        return []
    texts = {p: p.read_text(encoding="utf-8") for p in sorted(cdir.glob("*.txt"))}
    if not texts:
        return []
    median = statistics.median([len(t) for t in texts.values()]) or 1
    doomed = [p for p, t in texts.items() if flags_for(t) or len(t) > median * 6]
    for p in doomed:
        if apply:
            p.unlink()
    return [p.name for p in doomed]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", help="只掃一部（slug）")
    ap.add_argument("--json", action="store_true", help="輸出 JSON（給清快取用）")
    ap.add_argument("--purge", action="store_true", help="刪受損節的快取（下次 build 重譯）")
    ap.add_argument("--dry-run", action="store_true", help="配 --purge：只列不刪")
    a = ap.parse_args()

    if a.purge:
        slugs = [a.work] if a.work else sorted(
            p.stem.replace("plato_", "") for p in JSONL_DIR.glob("plato_*.jsonl"))
        total = 0
        for slug in slugs:
            names = purge_cache(slug, apply=not a.dry_run)
            total += len(names)
            if names:
                verb = "會刪" if a.dry_run else "已刪"
                print(f"{slug:24} {verb} {len(names)} 節：{', '.join(names[:8])}"
                      + ("…" if len(names) > 8 else ""))
        print(f"\n合計 {total} 節（重跑 plato_build 會重譯）")
        return

    paths = sorted(JSONL_DIR.glob(f"plato_{a.work}.jsonl" if a.work else "plato_*.jsonl"))
    reports = [scan_file(p) for p in paths]
    if a.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
        return
    total = 0
    for rep in reports:
        n = len(rep["bad"])
        total += n
        mark = "✗" if n else "✓"
        print(f"{mark} {rep['work']:24} chunks={rep['chunks']:4} 中位={rep['median_chars']:5} 受損={n}")
        for b in rep["bad"][:3]:
            print(f"      idx={b['chunk_index']} {b['chars']:6,}字 {','.join(b['flags'])}  {b['chapter_path']}")
        if n > 3:
            print(f"      …另外 {n - 3} 個")
    print(f"\n合計受損 chunk：{total}")


if __name__ == "__main__":
    main()
