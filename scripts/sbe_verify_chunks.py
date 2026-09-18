#!/usr/bin/env python3
"""收尾第三步：驗成品不驗流程 —— 直接讀 Drive 的 _chunks/<eid>.jsonl。

檢查兩件事：
 1. 每個 chunk 都有 sources（逐節對照才成立）
 2. 中文/原文長度比落在「該卷自己的中位數」附近
    🚨 分母取 source_order[0]（實際被翻的那一欄），不是最長的那一欄。
"""
import json, os, statistics, sys
from pathlib import Path
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sbe_translate as st  # noqa: E402

CHUNKS = Path(os.environ["EBOOK_CHUNKS_DIR"])
SLUGS = sys.argv[1:] or ["sbe-25-laws-of-manu", "sbe-08-bhagavadgita", "sbe-09-quran-2",
                         "sbe-15-upanishads-2", "sbe-21-lotus-sutra", "sbe-39-taoism-1"]
by_slug = {w["slug"]: w for w in st.WORKS}

def zh_len(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")

bad_total = 0
for slug in SLUGS:
    w = by_slug.get(slug)
    if not w:
        print(f"✗ {slug}: 不在 sbe_translate.WORKS"); bad_total += 1; continue
    f = CHUNKS / f"{w['eid']}.jsonl"
    if not f.exists():
        print(f"✗ {slug}: 找不到 {f.name}"); bad_total += 1; continue
    rows = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    body = [r for r in rows if r.get("chunk_type") != "cover"]

    no_sources = [r["chunk_index"] for r in body if not r.get("sources")]

    ratios = []
    for r in body:
        srcs, order = r.get("sources") or {}, r.get("source_order") or []
        key = order[0] if order else next(iter(srcs), None)
        src = (srcs.get(key) or "") if key else ""
        z = zh_len(r.get("content") or "")
        if len(src) >= 200:                      # 短段比值噪音大，不計
            ratios.append((r["chunk_index"], z / len(src)))
    if not ratios:
        print(f"? {slug}: 沒有夠長的段可比長度"); continue
    med = statistics.median(v for _, v in ratios)
    lo, hi = med * 0.45, med * 2.2               # 該卷自己的中位數為準
    outliers = [(i, v) for i, v in ratios if not (lo <= v <= hi)]

    flag = "✓" if not no_sources and not outliers else "✗"
    if flag == "✗":
        bad_total += 1
    print(f"{flag} {slug:24s} chunks={len(body):4d}  中位比={med:.3f}  "
          f"缺sources={len(no_sources)}  長度離群={len(outliers)}")
    for i, v in outliers[:5]:
        print(f"      chunk {i} 比值 {v:.3f}（區間 {lo:.3f}–{hi:.3f}）")
    if no_sources[:5]:
        print(f"      缺 sources 的 chunk_index：{no_sources[:5]}")

print("\n全綠" if bad_total == 0 else f"\n{bad_total} 卷有問題")
