#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依 v2 領域邊界，重標「創生哲學」已標對話的五域 facet 分類（item③-3）。

背景：classify_genesis_philosophy.py 首輪用舊 facet 定義掛標；創生哲學叢書 v2 精修
後邊界更精確（量子→本體論、數學→認識論、空無/默然/神聖/終極→存有論、願然/美→價值論、
誠實/善→倫理學、創生公式/生成三要素→本體論）。本腳本只重判**已屬創生哲學**對話的 facet，
**替換**其五個子分類標籤（保留父標「創生哲學」），不重跑 belongs 候選池。

引擎與 v2 facet 準則沿用 classify_genesis_philosophy（已更新為 v2）。
**預設 dry-run**（只印 old→new facet 差異統計），`--execute` 才真寫（先刪舊 facet 子標、再插新）。
resumable：ledger `c:/tmp/genesis_retag_{source}.jsonl`。

用法：
  python scripts/retag_genesis_facets.py --source chatgpt --dry-run   # 掃描+抽樣差異
  python scripts/retag_genesis_facets.py --source all --execute       # 真重標
"""
import argparse
import json
import sys
from collections import Counter

import requests

import classify_genesis_philosophy as C

sys.stdout.reconfigure(encoding="utf-8")


def fetch_parent_tagged_ids(parent_id: str) -> set[str]:
    """所有掛了父標『創生哲學』的 dialogue_id（跨來源；分頁）。"""
    ids: set[str] = set()
    off = 0
    while True:
        r = requests.get(
            f"{C.SUPABASE_URL}/rest/v1/ai_dialogue_entry_categories",
            headers={**C.SB_HDR, "Range-Unit": "items", "Range": f"{off}-{off+999}"},
            params={"select": "dialogue_id", "category_id": f"eq.{parent_id}"},
            timeout=60,
        )
        rows = r.json()
        if not isinstance(rows, list) or not rows:
            break
        ids.update(x["dialogue_id"] for x in rows)
        off += len(rows)
        if len(rows) < 1000:
            break
    return ids


def fetch_current_facets(dialogue_ids: list[str], facet_id_to_name: dict[str, str]) -> dict[str, set[str]]:
    """回傳 {dialogue_id: {facet 名稱…}}（只取五子分類）。"""
    out: dict[str, set[str]] = {d: set() for d in dialogue_ids}
    fids = list(facet_id_to_name)
    inlist = ",".join(dialogue_ids)
    cin = ",".join(fids)
    r = requests.get(
        f"{C.SUPABASE_URL}/rest/v1/ai_dialogue_entry_categories",
        headers=C.SB_HDR,
        params={"select": "dialogue_id,category_id",
                "dialogue_id": f"in.({inlist})", "category_id": f"in.({cin})"},
        timeout=60,
    )
    for row in r.json():
        out.setdefault(row["dialogue_id"], set()).add(facet_id_to_name[row["category_id"]])
    return out


def delete_facet_tags(dialogue_ids: list[str], facet_ids: list[str]) -> None:
    """刪掉這批 dialogue 的所有五子分類標（保留父標）。"""
    if not dialogue_ids:
        return
    inlist = ",".join(dialogue_ids)
    cin = ",".join(facet_ids)
    h = {**C.SB_HDR, "Prefer": "return=minimal"}
    r = requests.delete(
        f"{C.SUPABASE_URL}/rest/v1/ai_dialogue_entry_categories",
        headers=h,
        params={"dialogue_id": f"in.({inlist})", "category_id": f"in.({cin})"},
        timeout=120,
    )
    if r.status_code not in (200, 204):
        print(f"  ⚠ delete HTTP {r.status_code}: {r.text[:200]}", flush=True)


def process(source: str, cat: dict[str, str], batch_size: int, limit: int | None,
            execute: bool) -> dict:
    table = f"ai_dialogues_{source}"
    facet_ids = [cat[f] for f in C.FACETS]
    id2name = {cat[f]: f for f in C.FACETS}
    parent_tagged = fetch_parent_tagged_ids(cat[C.PARENT_NAME])
    print(f"\n=== {source} ===  父標對話總數(跨源) {len(parent_tagged)}", flush=True)

    ledger = C.LEDGER_DIR / f"genesis_retag_{source}.jsonl"
    done: set[str] = set()
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass

    todo = sorted(i for i in parent_tagged if i not in done)
    if limit:
        todo = todo[:limit]
    print(f"  ledger 已處理 {len(done)}・待重判(此源存在者於抓取時過濾) {len(todo)}", flush=True)

    st = {"judged": 0, "changed": 0, "now_false": 0}
    facet_dist: Counter = Counter()
    lf = ledger.open("a", encoding="utf-8") if execute else None
    try:
        for i in range(0, len(todo), batch_size):
            ids = todo[i:i + batch_size]
            rows = C.fetch_dialogues(table, ids)  # 不在此源的 id 自動略過
            if not rows:
                continue
            try:
                verdicts = C.llm_classify(rows)
            except Exception as e:
                print(f"  batch {i // batch_size} 跳過：{e}", flush=True)
                continue
            vmap = {v.get("i"): v for v in verdicts if isinstance(v, dict)}
            cur = fetch_current_facets([d["id"] for d in rows], id2name)
            batch_ids, new_rows = [], []
            for idx, d in enumerate(rows):
                v = vmap.get(idx, {})
                belongs = bool(v.get("belongs"))
                new = [f for f in (v.get("facets") or []) if f in C.FACETS][:2]
                old = cur.get(d["id"], set())
                st["judged"] += 1
                if not belongs:
                    st["now_false"] += 1
                if set(new) != old:
                    st["changed"] += 1
                for f in new:
                    facet_dist[f] += 1
                batch_ids.append(d["id"])
                for f in new:
                    new_rows.append({"dialogue_id": d["id"], "category_id": cat[f]})
                if lf:
                    lf.write(json.dumps({"id": d["id"], "belongs": belongs,
                                         "old": sorted(old), "new": new},
                                        ensure_ascii=False) + "\n")
                elif set(new) != old:  # dry-run 抽樣印差異
                    if st["changed"] <= 25:
                        print(f"    {d['id'][:8]} {sorted(old)} → {new}"
                              f"{' (belongs=false)' if not belongs else ''}", flush=True)
            if execute:
                delete_facet_tags(batch_ids, facet_ids)   # 先刪舊五子標
                C.insert_tags(new_rows)                    # 再插新（父標不動）
                lf.flush()
            print(f"  進度 {min(i + batch_size, len(todo))}/{len(todo)}"
                  f"・累計變更 {st['changed']}", flush=True)
    finally:
        if lf:
            lf.close()
    print(f"  {source} facet 新分布：{dict(facet_dist)}", flush=True)
    return st


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["chatgpt", "gemini", "all"], default="chatgpt")
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--execute", action="store_true", help="真寫（預設 dry-run）")
    args = ap.parse_args()

    cat = C.get_category_ids()
    print("分類 id：", {k: v[:8] for k, v in cat.items()},
          f"  mode={'EXECUTE' if args.execute else 'DRY-RUN'}", flush=True)
    sources = ["chatgpt", "gemini"] if args.source == "all" else [args.source]
    tot = {"judged": 0, "changed": 0, "now_false": 0}
    for s in sources:
        st = process(s, cat, args.batch, args.limit, args.execute)
        for k in tot:
            tot[k] += st[k]
    print(f"\n完成：重判 {tot['judged']}・facet 有變更 {tot['changed']}"
          f"・now belongs=false {tot['now_false']}（execute={args.execute}）", flush=True)


if __name__ == "__main__":
    main()
