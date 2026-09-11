# -*- coding: utf-8 -*-
"""把已經存進 checkpoint 的壞譯文找出來清空，交給各作者的 auto 重譯。

2026-09-11。判準直接用翻譯管線那一關的 `unusable_reason()`——同一套判準，
所以「閘門會擋下的」與「要清掉重譯的」永遠不會漂移。

清空（`zh[i] = ""`）而不是就地改寫，是因為這幾類壞輸出**沒有可救的部分**：
推理外洩是模型在自言自語，整段未譯是根本沒翻。只有整段重譯一途。
（對照 [[redo_conversion_terms]]：那邊是換詞，有原譯可用，就不該重譯。）

🚨 `src` 一律不碰。清完跑該作者的 auto，它會把空的 `zh` 補回來。

  python -X utf8 scripts/redo_bad_translations.py                # 只看
  python -X utf8 scripts/redo_bad_translations.py --apply
  python -X utf8 scripts/redo_bad_translations.py --author mueller --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from translate_ebook_to_zh import unusable_reason  # noqa: E402

DATA_ROOT = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="資料夾名去掉 _data，例 mueller")
    ap.add_argument("--work")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=8)
    args = ap.parse_args()

    dirs = sorted(DATA_ROOT.glob("*_data"))
    if args.author:
        dirs = [d for d in dirs if d.name == f"{args.author}_data"]
    reasons: Counter[str] = Counter()
    per_work: Counter[str] = Counter()
    shown = 0
    for data in dirs:
        for slug in sorted(p for p in data.iterdir() if p.is_dir()):
            if args.work and slug.name != args.work:
                continue
            for f in sorted(slug.glob("sec*.json")):
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    continue
                zh = d.get("zh") or []
                touched = False
                for i, z in enumerate(zh):
                    why = unusable_reason(z or "")
                    if not why:
                        continue
                    reasons[why] += 1
                    per_work[f"{data.name.replace('_data','')}/{slug.name}"] += 1
                    if shown < args.show:
                        shown += 1
                        print(f"  [{why}] {slug.name}/{f.stem}[{i}] {len(z)} 字")
                        print(f"     {z[:100]}")
                    if args.apply:
                        zh[i] = ""
                        touched = True
                if touched:
                    d["zh"] = zh
                    f.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                                 encoding="utf-8")

    print("\n分類：", "、".join(f"{k} {v}" for k, v in reasons.most_common()) or "（乾淨）")
    print("分卷：")
    for k, n in per_work.most_common():
        print(f"   {k:46} {n}")
    total = sum(reasons.values())
    print(f"\n{'已清空' if args.apply else '待清空'} {total} 段")
    if args.apply and total:
        print("🚨 清空之後**一定要跑該作者的 auto 補譯**，否則書裡會是空段：")
        for a in sorted({k.split('/')[0] for k in per_work}):
            print(f"   {a}")
    elif not args.apply:
        print("加 --apply 才會真的清空")


if __name__ == "__main__":
    main()
