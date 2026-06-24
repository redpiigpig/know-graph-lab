"""一次性遷移：救援 accs_commentary 中 father_name 空的續行/掉名片段。

用 accs_commentary.plan_blank_father_fixes（純函式、已測）規劃：
  (1) 續行併入：前列 comment 句中斷裂 → 併 body、繼承 father（DELETE 來源列）。
  (2) 作品回填：殘留 blank 若 work_title 全書唯一對應某 father → 補 father。
走 PostgREST（PATCH/DELETE by id，無 SQL 轉義風險）。

  python scripts/accs_resolve_blank_fathers.py --book gen            # dry-run
  python scripts/accs_resolve_blank_fathers.py --book gen --apply    # 實際寫入
"""
import argparse
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from accs_commentary import plan_blank_father_fixes  # noqa: E402

ENV_FILE = ROOT.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().lstrip("﻿"); v = v.strip().strip("'\"")
        if k and k not in os.environ:
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
HJSON = {**H, "Content-Type": "application/json", "Prefer": "return=minimal"}


def fetch_rows(book: str) -> list[dict]:
    rows, step, off = [], 1000, 0
    while True:
        url = (f"{SUPABASE_URL}/rest/v1/accs_commentary?book_code=eq.{book}"
               "&select=id,chapter,pericope_order,entry_order,section_kind,"
               "father_name,work_title,body_zh"
               "&order=chapter.asc,pericope_order.asc,entry_order.asc"
               f"&limit={step}&offset={off}")
        r = requests.get(url, headers=H, timeout=60); r.raise_for_status()
        batch = r.json()
        rows.extend(batch)
        if len(batch) < step:
            break
        off += step
    return rows


def patch_row(row_id: int, payload: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/accs_commentary?id=eq.{row_id}"
    r = requests.patch(url, headers=HJSON, json=payload, timeout=30)
    if r.status_code not in (200, 204):
        raise RuntimeError(f"PATCH {row_id} {r.status_code}: {r.text[:200]}")


def delete_row(row_id: int) -> None:
    url = f"{SUPABASE_URL}/rest/v1/accs_commentary?id=eq.{row_id}"
    r = requests.delete(url, headers=H, timeout=30)
    if r.status_code not in (200, 204):
        raise RuntimeError(f"DELETE {row_id} {r.status_code}: {r.text[:200]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default="gen")
    ap.add_argument("--apply", action="store_true", help="實際寫入（預設 dry-run）")
    args = ap.parse_args()

    rows = fetch_rows(args.book)
    blanks_before = sum(
        1 for r in rows
        if r["section_kind"] == "comment" and not (r.get("father_name") or "").strip()
    )
    total_body_before = sum(len(r.get("body_zh") or "") for r in rows)

    plan = plan_blank_father_fixes(rows)
    merges, father_sets = plan["merges"], plan["father_sets"]

    merged_source_ids = {s["id"] for m in merges for s in m["sources"]}
    set_ids = {fs["row"]["id"] for fs in father_sets}
    # body 守恆檢查：併入後文字總長不變
    total_body_after = (
        sum(len(m["new_body"]) for m in merges)
        + sum(len(r.get("body_zh") or "") for r in rows
              if r["id"] not in merged_source_ids
              and r["id"] not in {m["target"]["id"] for m in merges})
    )
    blanks_resolved = len(merged_source_ids) + len(set_ids)

    print(f"== blank-father 救援計畫（book={args.book}）==")
    print(f"  原始 blank-father comment：{blanks_before}")
    print(f"  續行併入 merges：{len(merges)}（刪除來源列 {len(merged_source_ids)}）")
    print(f"  作品回填 father_sets：{len(father_sets)}")
    print(f"  本計畫可解決：{blanks_resolved} / {blanks_before}")
    print(f"  殘留（無訊號）：{blanks_before - blanks_resolved}")
    print(f"  body 字數守恆：before={total_body_before} after={total_body_after} "
          f"{'OK' if total_body_before == total_body_after else '⚠️ 不符！'}")

    if total_body_before != total_body_after:
        print("  ⚠️ 守恆失敗，中止。", file=sys.stderr); sys.exit(1)

    print("\n  merges 範例：")
    for m in merges[:5]:
        t = m["target"]
        print(f"   ch{t['chapter']} p{t['pericope_order']} e{t['entry_order']} "
              f"[{t.get('father_name') or '∅'}] +{len(m['sources'])} 片段 → "
              f"…{m['new_body'][-26:]}")
    print("  father_sets 範例：")
    for fs in father_sets[:8]:
        r = fs["row"]
        print(f"   ch{r['chapter']} p{r['pericope_order']} e{r['entry_order']} "
              f"work={r.get('work_title')} → {fs['father']}")

    if not args.apply:
        print("\n  [dry-run] 加 --apply 才寫入。")
        return

    print("\n  套用中…")
    n = 0
    for m in merges:
        payload = {"body_zh": m["new_body"]}
        if m["new_work"]:
            payload["work_title"] = m["new_work"]
        patch_row(m["target"]["id"], payload)
        for s in m["sources"]:
            delete_row(s["id"])
        n += 1
    for fs in father_sets:
        patch_row(fs["row"]["id"], {"father_name": fs["father"]})
        n += 1
    print(f"  完成：{len(merges)} merges + {len(father_sets)} 回填，共 {n} 筆操作。")


if __name__ == "__main__":
    main()
