#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
祆教中譯產物閘 —— 驗「譯出來的東西是不是中文」，不是驗流程跑完沒。

    python -X utf8 scripts/avesta_zh_gate.py

🚨 這支存在的理由是四次實際事故（見 memory）：
  1. 推理外洩：`<think>` 沒閉合，整段推理被當譯文入庫且上線。
  2. 拒譯污染：Haiku 回「我注意到您提供的…」被當譯文存進去（東方聖卷 2,001 段）。
  3. 簡體漏網：救急層回簡體沒過 opencc。
  4. 英文殘留：中譯欄非空 100% 是假象，其實 12.7% 是英文。
     🚨 誤殺要靠**英文虛詞密度**判，不是字母比例——譯文裡有羅馬轉寫是正常的。
"""
from __future__ import annotations

import glob
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CJK = re.compile(r"[一-鿿]")
# 英文虛詞：譯文裡出現這些才是真的沒譯，單看字母比例會誤殺羅馬轉寫
STOP = re.compile(r"\b(the|and|of|to|in|that|is|was|for|with|which|thou|thee|his|her)\b", re.I)
THINK = re.compile(r"<think|</think|^\s*(?:嗯，|好的，|首先，|讓我|我需要|以下是翻譯|翻譯如下)")
# 逐詞空格：機翻把中文一個詞一個空格斷開（「我 祝福 該 祭祀 和 該 禱告」）
WORDGAP = re.compile(r"(?:[一-鿿]{1,3} ){4,}[一-鿿]")
# 拉丁字母嵌在中文詞中間（「瑪zda亚斯尼」），與整句英文殘留是兩回事
LATIN_IN = re.compile(r"[一-鿿][A-Za-z]{2,}[一-鿿]")
REFUSE = re.compile(r"我注意到您|抱歉|無法翻譯|as an AI|I cannot|對不起")
# 簡體特徵字（繁中不會用）
SIMP = re.compile(r"[们个这为体产么长东丝专业丛严丧临书买乱争亚产亲们价众优会伟传伤伦伪]")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="祆教中譯產物閘")
    ap.add_argument("--reset", action="store_true",
                    help="把驗不過的段落 zh 清空，讓 avesta_translate.py 重譯它們")
    args = ap.parse_args()
    flagged: set[str] = set()
    bad: dict[str, list] = {k: [] for k in
                            ("推理外洩", "拒譯", "簡體", "英文殘留",
                             "整段重複", "逐詞空格", "拉丁嵌字", "過短")}
    tot = zh = 0
    for f in sorted(glob.glob(str(ROOT / "data/avesta/sources/text/*.json"))):
        d = json.load(io.open(f, encoding="utf-8"))
        name = Path(f).stem
        for v in d.get("segments") or []:
            tot += 1
            t = (v.get("zh") or "").strip()
            if not t:
                continue
            zh += 1
            ref = v.get("ref") or f"{name}:{v.get('verse')}"
            before = len(flagged)
            n_cjk = len(CJK.findall(t))
            n_stop = len(STOP.findall(t))
            half = len(t) // 2
            if half > 20 and t[:half].strip() and t[:half].strip() in t[half:]:
                bad["整段重複"].append((ref, t[:70]))
            elif WORDGAP.search(t):
                bad["逐詞空格"].append((ref, WORDGAP.search(t).group(0)[:50]))
            elif LATIN_IN.search(t):
                bad["拉丁嵌字"].append((ref, LATIN_IN.search(t).group(0)))
            elif THINK.search(t):
                bad["推理外洩"].append((ref, t[:70]))
            elif REFUSE.search(t):
                bad["拒譯"].append((ref, t[:70]))
            elif SIMP.search(t):
                bad["簡體"].append((ref, SIMP.search(t).group(0) + " … " + t[:56]))
            elif n_stop >= 4 and n_cjk < n_stop * 3:
                bad["英文殘留"].append((ref, t[:70]))
            elif n_cjk < 4:
                bad["過短"].append((ref, t[:70]))
            if len(flagged) == before and any(
                    ref in [r for r, _ in rows] for rows in bad.values()):
                flagged.add(f"{f}	{ref}")

    print(f"中譯 {zh:,}/{tot:,} 段（{zh/tot*100:.1f}%）\n")
    hit = 0
    for k, rows in bad.items():
        print(f"  {k:<12} {len(rows):>4}")
        hit += len(rows)
        for ref, s in rows[:3]:
            print(f"       {ref}  {s}")
    print(f"\n{'✓ 全過' if hit == 0 else f'🚨 {hit} 段有問題'}")

    if args.reset and hit:
        # 🚨 只清「驗不過的那幾段」，不是整檔重來——好的譯文重譯會換掉一批公式譯法，
        #    而萬迪達德最怕的正是同一公式在不同批次譯得不一樣。
        want = {r for rows in bad.values() for r, _ in rows}
        n = 0
        for path in sorted(glob.glob(str(ROOT / "data/avesta/sources/text/*.json"))):
            d = json.load(io.open(path, encoding="utf-8"))
            touched = False
            for v in d.get("segments") or []:
                if (v.get("ref") or "") in want and (v.get("zh") or "").strip():
                    v["zh"] = ""
                    touched = True
                    n += 1
            if touched:
                io.open(path, "w", encoding="utf-8", newline="").write(
                    json.dumps(d, ensure_ascii=False, indent=2))
        print(f"已清空 {n} 段；重跑 avesta_translate.py 即會補譯")
    return 0 if hit == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
