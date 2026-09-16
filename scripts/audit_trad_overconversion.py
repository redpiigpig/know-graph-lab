# -*- coding: utf-8 -*-
"""稽核／修復「簡轉繁轉過頭」的專業術語 —— 目前主目標是佛學的「熏習」被寫成「燻習」。

怎麼發現的（2026-09-16）：拿 `scripts/ocr_bench.py` 比對 OCR 引擎時，發現
gemini 在《佛教的概念與方法》12 頁裡把「熏習」(vāsanā) **62 次全部**輸出成「燻習」。
燻是燻肉的燻，熏習是唯識學的核心詞。Gemini 是在模型內部自己做簡繁轉換的，
而 `parse_drive_inventory.TRAD_FIXES` 沒有這一條，所以錯字一路寫進館藏、沒有任何閘攔得住。
（opencc `s2tw` 本身是對的：「熏习」→「熏習」。問題只出在模型自己轉的那一條路。）

🚨 **不可以無差別把「燻」換成「熏」** —— 燻肉、煙燻、燻雞都是對的字。
只換下面 PAIRS 裡「後面那個字使它必定是佛學／中醫術語」的組合。

用法：
    python scripts/audit_trad_overconversion.py audit              # 全庫稽核（可續跑）
    python scripts/audit_trad_overconversion.py audit --limit 200  # 先抽樣看看
    python scripts/audit_trad_overconversion.py fix --dry-run      # 預覽會改什麼
    python scripts/audit_trad_overconversion.py fix                # 真的改（先備份 .bak）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CHUNKS_DIR = Path(os.environ.get(
    "EBOOK_CHUNKS_DIR", r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks"))
STATE = Path("c:/tmp/trad_overconversion_audit.json")

# (錯, 對)。只收「第二個字讓它不可能是食物」的搭配。
PAIRS = [
    ("燻習", "熏習"),      # vāsanā，唯識學核心詞
    ("燻染", "熏染"),
    ("燻修", "熏修"),
    ("所燻", "所熏"),
    ("受燻", "受熏"),
    ("能燻", "能熏"),
    ("燻成", "熏成"),
    ("燻發", "熏發"),
    ("燻種", "熏種"),
    ("聞燻", "聞熏"),
]
# 只要出現這些就**不要**動整個檔（避免誤傷飲食／製程類的書）
SAFE_WORDS = ("燻肉", "煙燻", "燻雞", "燻鮭", "燻製", "燻烤")


def scan_text(text: str) -> dict[str, int]:
    return {bad: text.count(bad) for bad, _ in PAIRS if bad in text}


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"scanned": {}, "hits": {}}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def iter_files(limit: int | None):
    files = sorted(CHUNKS_DIR.glob("*.jsonl"))
    return files[:limit] if limit else files


def cmd_audit(args) -> int:
    st = load_state() if args.resume else {"scanned": {}, "hits": {}}
    files = iter_files(args.limit)
    total = len(files)
    if not total:
        print(f"⛔ {CHUNKS_DIR} 下一個 .jsonl 都沒有 —— G: 沒掛？先確認再說，別當成「沒問題」")
        return 1
    print(f"要掃 {total} 個 JSONL（已掃過 {len(st['scanned'])} 個）")

    t0 = time.time()
    done = 0
    for i, f in enumerate(files, 1):
        if args.resume and f.name in st["scanned"]:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            st["scanned"][f.name] = f"ERR {e.__class__.__name__}"
            continue
        counts = scan_text(text)
        st["scanned"][f.name] = sum(counts.values())
        if counts:
            st["hits"][f.stem] = {
                "counts": counts,
                "total": sum(counts.values()),
                "has_food_word": any(w in text for w in SAFE_WORDS),
            }
        done += 1
        if i % 200 == 0:
            el = time.time() - t0
            print(f"  …{i}/{total}　命中 {len(st['hits'])} 本　"
                  f"已耗時 {el / 60:.1f} 分", flush=True)
            save_state(st)

    save_state(st)
    hits = st["hits"]
    grand = sum(h["total"] for h in hits.values())
    print()
    print(f"=== 稽核完成：掃 {len(st['scanned'])} 個檔，{len(hits)} 本中鏢，共 {grand} 處 ===")
    for bid, h in sorted(hits.items(), key=lambda kv: -kv[1]["total"])[:20]:
        food = "　⚠含飲食用詞，修前先看" if h["has_food_word"] else ""
        detail = "、".join(f"{k}×{v}" for k, v in h["counts"].items())
        print(f"  {bid}  {h['total']:>4} 處　{detail}{food}")
    print(f"\n明細 → {STATE}")
    return 0


def cmd_fix(args) -> int:
    st = load_state()
    hits = st.get("hits") or {}
    if not hits:
        print("⛔ 還沒有稽核結果（或稽核命中 0 本）。先跑 audit，"
              "而且要確認它真的掃完 —— 「0 筆」多半是迴圈沒跑到。")
        return 1

    changed_files = 0
    changed_spots = 0
    for bid, h in sorted(hits.items(), key=lambda kv: -kv[1]["total"]):
        if h.get("has_food_word") and not args.include_food:
            print(f"  跳過 {bid}（含飲食用詞，要改請加 --include-food）")
            continue
        p = CHUNKS_DIR / f"{bid}.jsonl"
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8").splitlines()
        out, n = [], 0
        for line in lines:
            if not line.strip():
                out.append(line)
                continue
            d = json.loads(line)
            c = d.get("content") or ""
            before = c
            for bad, good in PAIRS:
                c = c.replace(bad, good)
            if c != before:
                n += before.count("燻") - c.count("燻")
                d["content"] = c
            out.append(json.dumps(d, ensure_ascii=False))
        if not n:
            continue
        changed_files += 1
        changed_spots += n
        print(f"  {bid}  修 {n} 處")
        if not args.dry_run:
            bak = p.with_suffix(".jsonl.trad.bak")
            if not bak.exists():
                bak.write_bytes(p.read_bytes())
            tmp = p.with_suffix(".jsonl.tmp")
            tmp.write_text("\n".join(out) + "\n", encoding="utf-8")
            tmp.replace(p)

    verb = "會修" if args.dry_run else "已修"
    print(f"\n{verb} {changed_files} 本、共 {changed_spots} 處"
          f"{'（--dry-run，沒有實際寫入）' if args.dry_run else '；原檔備份為 .jsonl.trad.bak'}")
    if not args.dry_run and changed_files:
        print("🚨 JSONL 改了之後，DB 的 100 字 preview 要一起重建："
              "python scripts/repopulate_chunk_previews.py run --book <id> --force")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="掃全庫找過度轉換")
    a.add_argument("--limit", type=int, help="只掃前 N 個檔（抽樣）")
    a.add_argument("--resume", action="store_true", default=True)
    a.add_argument("--no-resume", dest="resume", action="store_false")
    a.set_defaults(func=cmd_audit)

    f = sub.add_parser("fix", help="按稽核結果改回正確用字")
    f.add_argument("--dry-run", action="store_true")
    f.add_argument("--include-food", action="store_true",
                   help="連含飲食用詞的書也改（預設跳過，怕誤傷燻肉）")
    f.set_defaults(func=cmd_fix)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
