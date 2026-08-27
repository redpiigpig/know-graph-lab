#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ziliaozhan 書目 × 基督教大藏經 既有書目 → 交集與缺口。

  python scripts/zlz_match.py                 # 交集（藏經有、站上也有）→ 值得收
  python scripts/zlz_match.py --gap           # 站上有、藏經沒有 → 餵分類器看缺什麼
  python scripts/zlz_match.py --gap --out c:/tmp/zlz_gap_records.json

比對難點：兩邊的漢語書名體例不同（天主教用「天主之城」、藏經可能作「上帝之城」），
還有簡繁、書名號、冊次、譯者附註。所以先正規化再比，並保留別名表處理
天主教／新教的定名差異——這類差異靠字串比對永遠對不上。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import to_traditional

DAZANG = Path("c:/tmp/dazang_works.json")
ZLZ = Path("c:/tmp/zlz_catalog.json")

# 天主教↔新教的定名差異，字串比對永遠對不上，只能列表。
# 左為天主教慣用、右為藏經可能採用的形式（雙向都試）。
ALIASES = [
    ("天主之城", "上帝之城"), ("天主經", "主禱文"), ("默示錄", "啟示錄"),
    ("聖詠集", "詩篇"), ("宗徒大事錄", "使徒行傳"), ("依撒意亞", "以賽亞"),
    ("耶肋米亞", "耶利米"), ("厄則克耳", "以西結"), ("達尼爾", "但以理"),
    ("創世紀", "創世記"), ("出谷紀", "出埃及記"), ("肋未紀", "利未記"),
    ("戶籍紀", "民數記"), ("申命紀", "申命記"), ("若望", "約翰"),
    ("瑪竇", "馬太"), ("馬爾谷", "馬可"), ("路加", "路加"),
    ("斐理伯", "腓立比"), ("格林多", "哥林多"), ("羅馬人書", "羅馬書"),
    ("師主篇", "效法基督"), ("神操", "靈性操練"),
    ("奧思定", "奧古斯丁"), ("多瑪斯", "托馬斯"), ("多默", "多馬"),
    ("盎博羅削", "安波羅修"), ("安布羅斯", "安波羅修"),
    ("大額我略", "大貴格利"), ("國瑞", "貴格利"), ("金口若望", "屈梭多模"),
    ("神學大全", "神學大全"), ("懺悔錄", "懺悔錄"),
]

# 「研究某書」不是「某書」。包含式比對會把論文題目咬成原典——
# 《天路歷程》互文翻譯研究 ⊃ 天路歷程、比較分析《馬太福音》…的主位結構 ⊃ 馬太福音。
STUDY_RX = re.compile(
    r"研究|探析|探究|析論|評述|考論|述考|淺析|芻議|試論|管窺"
    r"|之研究|的研究|—論|——論|：從|從.{1,12}角度|從.{1,12}看|以.{1,12}為例"
    r"|比較分析|互文|視域|讀者回應|接受史|翻譯策略|語料庫|主位結構"
    r"|碩士論文|博士論文|學位論文")

NOISE = re.compile(
    r"[《》〈〉（）()\[\]【】｛｝{}「」『』…—\-–—_、，,。.：:；;！!？?\s]"
    r"|全\d+[冊册卷]|共\d+[冊册卷]|上[下中]?[冊册卷]|第?[一二三四五六七八九十\d]+[冊册卷輯辑]"
    r"|中文版|中譯本|修訂版|校對版|新版|節錄|選集|合集|全集|注釋|註釋|導讀"
    r"|拉丁文|中英雙語|繁體|简体|簡體")


def norm(s: str) -> str:
    """正規化：轉繁 → 去書名號/冊次/版本註記 → 去空白。"""
    return NOISE.sub("", to_traditional(s or "")).lower()


def variants(s: str) -> set[str]:
    """加上天主教↔新教定名互換後的所有寫法。"""
    base = norm(s)
    out = {base}
    for a, b in ALIASES:
        na, nb = norm(a), norm(b)
        if na and na in base:
            out.add(base.replace(na, nb))
        if nb and nb in base:
            out.add(base.replace(nb, na))
    return {x for x in out if len(x) >= 2}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", action="store_true", help="輸出站上有但藏經沒有的")
    ap.add_argument("--out", help="寫出分類器 records JSON")
    ap.add_argument("--min-len", type=int, default=3, help="標題正規化後短於此不比對")
    a = ap.parse_args()

    dz = json.loads(DAZANG.read_text(encoding="utf-8"))
    zl = json.loads(ZLZ.read_text(encoding="utf-8"))

    # 藏經側：標題所有寫法 → 作品
    index: dict[str, dict] = {}
    for w in dz:
        for t in (w["title_zh"], w.get("title_orig") or ""):
            for v in variants(t):
                if len(v) >= a.min_len:
                    index.setdefault(v, w)

    # 站上的書名幾乎都帶附註——「论三位一体-奥古斯丁」「神学大全中文版（圣多玛斯
    # 阿奎那巨著）」——正規化後仍多出作者與版本說明。所以不能要求完全相等，
    # 改判「藏經書名是否出現在站上書名裡」。
    # 短書名（如「神操」「路加」）用包含式會亂咬，故設 SAFE_LEN 門檻：
    # 未達長度者仍走完全相等。
    SAFE_LEN = 4
    long_keys = sorted((k for k in index if len(k) >= SAFE_LEN), key=len, reverse=True)

    hit, miss = [], []
    for z in zl:
        vs = [v for v in variants(z["title"]) if len(v) >= a.min_len]
        m = next((index[v] for v in vs if v in index), None)          # ① 完全相等
        how = "exact"
        if not m:                                                     # ② 包含（長書名才用）
            for zv in vs:
                k = next((k for k in long_keys if k in zv), None)
                if k:
                    m, how = index[k], "contains"
                    break
        # 包含式命中但標題長得像論文 → 那是研究不是原典，不收
        if m and how == "contains" and STUDY_RX.search(z["title"]):
            m = None
        if m:
            hit.append({**z, "dazang": m, "match": how, "key": k if how == "contains" else ""})
        else:
            miss.append(z)

    # 包含式的副作用：藏經裡若有「基督教史」「基督教神學」這種通用書名，站上
    # 任何「基督教史略」「基督教神學美學研究」都會被咬中。判準是「同一個藏經
    # 書名咬中太多筆」——那就不是書名而是題材詞，該筆改列待審不自動收。
    import collections as _c
    keyhits = _c.Counter(h["key"] for h in hit if h["key"])
    GENERIC_AT = 3
    generic = {k for k, n in keyhits.items() if n >= GENERIC_AT}
    vague = [h for h in hit if h["key"] in generic]
    hit = [h for h in hit if h["key"] not in generic]
    if vague:
        print(f"  ⚠ 因藏經書名過於通用而改列待審：{len(vague)} 筆"
              f"（通用詞 {len(generic)} 個：{'、'.join(sorted(generic)[:6])}）\n")

    print(f"站上書目 {len(zl)} 筆 × 藏經 {len(dz)} 部\n")
    print(f"  ✓ 交集（藏經已有、站上也有）：{len(hit)} 筆  ← 值得收")
    print(f"  · 站上有、藏經沒有：{len(miss)} 筆\n")

    rows = miss if a.gap else hit
    import collections
    print(f"{'分類':<10}{'筆數':>7}")
    for k, n in collections.Counter(r["category_zh"] for r in rows).most_common():
        print(f"  {k:<8}{n:>7}")

    if not a.gap:
        print("\n=== 交集明細 ===")
        for h in sorted(hit, key=lambda x: x["category_zh"]):
            d = h["dazang"]
            mk = "=" if h.get("match") == "exact" else "⊃"
            print(f"  [{h['category_zh']:<4}] {h['title'][:38]:<40}"
                  f"{mk} {d['era']:<13}{d['title_zh'][:22]}")

    if a.out:
        recs = [{
            "source": "ziliaozhan", "query": r["category_zh"], "title": r["title"],
            "author": "", "date": r["date"], "language": "chinese",
            "subjects": [r["category_zh"]], "url": r["url"], "raw_id": r["id"],
            "classification_status": "unclassified",
        } for r in rows]
        Path(a.out).write_text(json.dumps({"records": recs}, ensure_ascii=False, indent=1),
                               encoding="utf-8")
        print(f"\n已寫 {a.out}（{len(recs)} 筆）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
