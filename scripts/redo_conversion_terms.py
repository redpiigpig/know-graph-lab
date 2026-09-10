# -*- coding: utf-8 -*-
"""把 conversion／convert 譯得不一致的地方收斂成「歸信」。

為什麼要有這一支：豪斯評傳裡 `convert`／`conversion` 一族共 107 處，譯文出現了
**五種**寫法——回心 50、皈依 24、歸信 22、改宗 5、信主 4。根因在
`howes_build.HOWES_PROMPT_TMPL` 的概念層規則本身就寫著「conversion→回心」，
而「回心」是**日文**基督教譯 conversion 的詞（かいしん），中文基督教界不用，
讀者會誤讀成「悔改」。豪斯的英文原著從頭到尾沒出現過 kaishin，這個詞完全是
翻譯端加上去的。2026-09-10 使用者定調：一律「歸信／歸信者」，只有明確的
天主教語境保留「皈依」。

**為什麼是就地改寫而不是重譯。** 一開始走的是「清掉譯文→重跑引擎」（`--clear`
仍留著）。跑了 33 段之後比對舊譯文，發現術語是修好了，但別的東西壞了：
Takagi Yasaka 從正確的「高木八尺」變成憑空捏造的「高木雅坂」、「尋求者」變回
沒翻的 `seekers`、「鑑三」變成 `Kanz`（ô 掉了）、一段縮水 17%。舊譯文是校過的，
壞的只有那個詞——所以正解是只換詞，不動句子。

兩道閘，缺一不可：

  英文佐證  該段的英文原文真的出現 convert 一族才動（沿用 [[name_lock]] 的規矩）。
            少了它，繆勒講「皈依三寶」、潘尼卡講印度教的段落會被一起改掉。
  受詞檢查  「皈依非戰論」「皈依再臨思想」的受詞不是宗教而是主張，換成
            「歸信非戰論」不通——這幾種語境原樣留著。

  python scripts/redo_conversion_terms.py --author howes --work howes-prophet --dry
  python scripts/redo_conversion_terms.py --author howes --work howes-prophet --apply
  python scripts/redo_conversion_terms.py --author howes --work howes-prophet --clear
      # --clear 是舊路：清掉譯文交給引擎重譯（會連帶弄壞別的地方，慎用）
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
# 🚨「決志」與「歸主」不收：前者多半在講「下定決心」（「要獨立的決志」），
#    後者在中文教會語感裡跟「歸信」不完全等值，動它得不償失。
VARIANTS = ("回心", "皈依", "改宗", "信主")

# 英文佐證：這一段真的在講 conversion 才動它。
EN_EVIDENCE = re.compile(r"\bconver(?:t|ts|ted|ting|sion|sions)\b", re.I)

# 天主教語境：這幾個字一出現就不改「皈依」（「皈依天主教會」是對的）。
CATHOLIC = re.compile(r"Catholic|Jesuit|papal|Pope|nun|monk|convent|Xavier")

# 受詞明確就是基督教時，不必等英文佐證——這幾個片語沒有別的意思。
# （豪斯書裡有一處英文寫的是 "initial commitment to Christianity" 而非 conversion，
#  譯文卻是「初次皈依基督教」：意思一樣，只是英文用了別的字。）
UNAMBIGUOUS = ("皈依基督教", "回心基督教", "改宗基督教")

# 受詞不是宗教而是主張的「皈依」——「歸信非戰論」不通，原樣留著。
_NOT_A_RELIGION = ("非戰論", "再臨思想", "再臨運動", "和平主義", "社會主義")

# 改寫規則，**順序有意義**：長的片語要排在單字前面，否則會被單字規則先切碎。
REWRITES: list[tuple[str, str]] = [
    ("回心信仰基督教", "歸信基督教"),
    ("回心信仰", "歸信"),
    ("回心父親", "使父親歸信"),
    ("改宗為基督教", "歸信基督教"),
    ("領人信主", "領人歸信"),
    ("信主者", "歸信者"),
    ("信主的人", "歸信的人"),
    ("回心", "歸信"),
    ("改宗", "歸信"),
    ("皈依", "歸信"),
]


def rewrite_zh(zh: str) -> str:
    """一段譯文 → 收斂過的譯文。純函式；呼叫端負責英文佐證那道閘。"""
    out = zh or ""
    for frm, to in REWRITES:
        if frm != "皈依":
            out = out.replace(frm, to)
            continue
        # 「皈依」逐處看受詞：後面接的是主張就不動
        pieces, i = [], 0
        while True:
            j = out.find(frm, i)
            if j < 0:
                pieces.append(out[i:])
                break
            tail = out[j + len(frm): j + len(frm) + 6]
            pieces.append(out[i:j])
            pieces.append(frm if any(w in tail for w in _NOT_A_RELIGION) else to)
            i = j + len(frm)
        out = "".join(pieces)
    return out


def hits(src: list[str], zh: list) -> list[int]:
    """回傳「該改寫」的段落序號。純函式，測試鎖在 tests/test_redo_conversion_terms.py。"""
    out = []
    for i, (en, z) in enumerate(zip(src, zh)):
        if not z or not any(v in z for v in VARIANTS):
            continue
        if not EN_EVIDENCE.search(en or "") and not any(u in z for u in UNAMBIGUOUS):
            continue                      # 沒有英文佐證：那個詞是別的意思，別碰
        if CATHOLIC.search(en or "") and "回心" not in z:
            continue                      # 天主教語境的「皈依」照留
        if rewrite_zh(z) == z:
            continue                      # 改寫後沒變（受詞不是宗教）就不算命中
        out.append(i)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", default="howes")
    ap.add_argument("--work", required=True)
    ap.add_argument("--apply", action="store_true", help="就地改寫（建議）")
    ap.add_argument("--clear", action="store_true", help="清掉譯文交給引擎重譯（舊路）")
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
        if args.apply or args.clear:
            for j in idx:
                zh[j] = None if args.clear else rewrite_zh(zh[j])
            c["zh"] = zh
            cp.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    verb = "已清掉" if args.clear else ("已改寫" if args.apply else "將改寫")
    print(f"\n{verb} {total} 段")
    if not (args.apply or args.clear):
        print("加 --apply 才會真的寫入")


if __name__ == "__main__":
    main()
