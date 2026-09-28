#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""對 pairs_134.tsv 裡配到 zh_id 的每一組，跑 `is_foreign_original` /
`verify_same_book` 兩道不寫入的檢查，並用純比例分配（舊法）與錨點校正
（`align_reference_anchors.distribute_with_anchors`，新法）各跑一次乾跑
`align_book`，記錄章節覆蓋率／段落覆蓋率供比較。

🚨 只讀，不寫：不碰任何書的 JSONL、不推 R2、不改 DB。

用法：
    python scripts/reference_pairs_verify.py \
        --pairs output/reference_pairs/pairs_134.tsv \
        --out output/reference_pairs/verify_results.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import align_reference as ar  # noqa: E402
import align_reference_anchors as ara  # noqa: E402


def verify_pair(orig_id: str, zh_id: str) -> dict:
    out: dict = {"orig_id": orig_id, "zh_id": zh_id}
    try:
        en = ar.load_jsonl(orig_id)
        zh = ar.load_jsonl(zh_id)
    except FileNotFoundError as e:
        out["error"] = f"jsonl 找不到：{e}"
        return out
    except Exception as e:  # noqa: BLE001
        out["error"] = f"讀取失敗：{type(e).__name__}: {e}"
        return out

    out["en_chunks"] = len(en)
    out["zh_chunks"] = len(zh)

    foreign, prof = ar.is_foreign_original(en)
    zh_prof = ar.is_foreign_original(zh)[1]
    zh_is_chinese = zh_prof["why"] == "chinese"
    out["orig_is_foreign"] = foreign
    out["orig_script_why"] = prof["why"]
    out["orig_han_share"] = prof.get("han_share")
    out["zh_is_chinese"] = zh_is_chinese
    out["zh_script_why"] = zh_prof["why"]

    if not (foreign and zh_is_chinese):
        out["gate"] = "fail_language"
        return out

    try:
        old = ar.align_book(en, zh)
        new = ar.align_book(en, zh, distribute_fn=ara.distribute_with_anchors)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"align_book 失敗：{type(e).__name__}: {e}"
        out["traceback"] = traceback.format_exc()[-2000:]
        return out

    old_r, new_r = old["report"], new["report"]
    out["old"] = {"chapter_coverage": old_r["chapter_coverage"],
                  "paragraph_coverage": old_r["zh_paragraph_coverage"],
                  "chapter_anchor_hit": old_r["chapter_anchor_hit"],
                  "chapter_anchor_total": old_r["chapter_anchor_total"]}
    out["new"] = {"chapter_coverage": new_r["chapter_coverage"],
                  "paragraph_coverage": new_r["zh_paragraph_coverage"]}

    same_old = ar.verify_same_book(old["zh_chunks"])
    same_new = ar.verify_same_book(new["zh_chunks"])
    out["verify_same_book_old"] = same_old
    out["verify_same_book_new"] = same_new

    n_anchor_used = sum(
        1 for c in new["zh_chunks"] if (c.get("source_text") or "").strip())
    out["gate"] = "pass" if same_old["verdict"] == "same" else (
        "undetermined" if same_old["verdict"] == "undetermined" else "fail_different_book")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", default=str(ROOT / "output/reference_pairs/pairs_134.tsv"))
    ap.add_argument("--out", default=str(ROOT / "output/reference_pairs/verify_results.json"))
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 組（0＝全部），debug 用")
    args = ap.parse_args()

    rows = []
    with open(args.pairs, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)

    to_check = [r for r in rows if r.get("zh_id")]
    if args.limit:
        to_check = to_check[:args.limit]
    print(f"共 {len(rows)} 組，其中 {len(to_check)} 組有 zh_id 待驗證")

    results = []
    for i, r in enumerate(to_check, 1):
        print(f"[{i}/{len(to_check)}] {r['orig_id']} <-> {r['zh_id']}  ({r.get('zh_title','')[:30]})")
        res = verify_pair(r["orig_id"], r["zh_id"])
        res["orig_title"] = r.get("orig_title", "")
        res["zh_title_hint"] = r.get("zh_title", "")
        res["source"] = r.get("source", "")
        results.append(res)
        if "error" in res:
            print(f"    ERROR: {res['error']}")
        elif res.get("gate") == "fail_language":
            print(f"    語言不符：orig={res['orig_script_why']} zh={res['zh_script_why']}")
        else:
            print(f"    gate={res.get('gate')}  old_cov={res.get('old',{}).get('paragraph_coverage')}"
                  f"  new_cov={res.get('new',{}).get('paragraph_coverage')}"
                  f"  same_old={res.get('verify_same_book_old',{}).get('verdict')}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n寫入 {args.out}")

    from collections import Counter
    cnt = Counter(r.get("gate", "error" if "error" in r else "?") for r in results)
    print("gate 分布：", dict(cnt))


if __name__ == "__main__":
    main()
