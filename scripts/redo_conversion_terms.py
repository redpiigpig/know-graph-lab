# -*- coding: utf-8 -*-
"""把 conversion／convert 譯得不一致的段落清掉，供重譯。

為什麼要有這一支：豪斯評傳裡 `convert`／`conversion` 一族共 107 處，譯文出現了
**五種**寫法——回心 50、皈依 24、歸信 22、改宗 5、信主 4。根因在
`howes_build.HOWES_PROMPT_TMPL` 的概念層規則本身就寫著「conversion→回心」，
而「回心」是**日文**基督教譯 conversion 的詞（かいしん），中文基督教界不用，
讀者會誤讀成「悔改」。豪斯的英文原著從頭到尾沒出現過 kaishin，這個詞完全是
翻譯端加上去的。2026-09-10 使用者定調：一律「歸信／歸信者」，只有明確的
天主教語境保留「皈依」。

跟 `uchimura_auto.py --redo-matching` 的差別是**多一道英文佐證閘**（沿用
[[name_lock]] 的規矩）：只有該段的英文原文真的出現 convert 一族才清。少了這道閘，
「皈依」會連同繆勒講佛教皈依三寶、潘尼卡講印度教的段落一起被清掉重譯——那些地方
「皈依」是對的。

  python scripts/redo_conversion_terms.py --author howes --work howes-prophet --dry
  python scripts/redo_conversion_terms.py --author howes --work howes-prophet --apply
  # 清完再跑： python scripts/uchimura_auto.py --author howes --work howes-prophet --backend nvidia
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 要收斂掉的變體。「歸信」是正名，不在此列。
VARIANTS = ("回心", "皈依", "改宗", "信主", "決志", "歸主", "轉信", "歸化")

# 英文佐證：這一段真的在講 conversion 才動它。
EN_EVIDENCE = re.compile(r"\bconver(?:t|ts|ted|ting|sion|sions)\b", re.I)

# 天主教語境：這幾個字一出現就不動（「皈依天主教會」是對的）。
CATHOLIC = re.compile(r"Catholic|Jesuit|Rome|papal|Pope|nun|monk|convent|Xavier")


def hits(src: list[str], zh: list) -> list[int]:
    """回傳「該重譯」的段落序號。純函式，測試鎖在 tests/test_redo_conversion_terms.py。"""
    out = []
    for i, (en, z) in enumerate(zip(src, zh)):
        if not z or not any(v in z for v in VARIANTS):
            continue
        if not EN_EVIDENCE.search(en or ""):
            continue                      # 沒有英文佐證：那個詞是別的意思，別碰
        if CATHOLIC.search(en or "") and "皈依" in z and "回心" not in z:
            continue                      # 天主教語境的「皈依」照留
        out.append(i)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", default="howes")
    ap.add_argument("--work", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    import uchimura_auto as ua
    ua.use_author(args.author)
    data_root = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / \
        getattr(ua.ub, "DATA_DIRNAME", "uchimura_data")

    total = 0
    for i in range(len(ua.ub.load_work_sections(args.work))):
        cp = data_root / args.work / f"sec{i}.json"
        if not cp.exists():
            continue
        c = json.loads(cp.read_text(encoding="utf-8"))
        src, zh = c.get("src") or [], c.get("zh") or []
        idx = hits(src, zh)
        if not idx:
            continue
        total += len(idx)
        print(f"  sec{i}: {len(idx)} 段 —— {idx}")
        if args.apply:
            for j in idx:
                zh[j] = None
            c["zh"] = zh
            cp.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{'已清掉' if args.apply else '將清掉'} {total} 段")
    if not args.apply:
        print("加 --apply 才會真的寫入")


if __name__ == "__main__":
    main()
