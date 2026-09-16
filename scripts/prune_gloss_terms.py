#!/usr/bin/env python3
"""Cut the everyday grammar labels out of the word-by-word glosses, keep the markers.

Owner's ruling, 2026-09-16: 「都要有重要的文法術語，太簡單的不用，那種罕見的才要」
「冠詞太常見了就不用」「那一些如果是特別的標記就需要」.

So the gloss column keeps a grammatical note when the note is a *marker* — a word
whose whole job is to signal something a Chinese reader has no equivalent for —
and drops it when it is a label anybody reading an original-language reader
already knows:

* **keep** 受詞記號 (Hebrew אֶת), 虛擬語氣標記 (ἄν), 不定詞標記, 條件語氣標記,
  完成式助動詞, 關係代詞, 意志·推量, 被·可能·敬, 尊敬標記 — the rule of thumb is
  that they name a construction, not a slot;
* **drop** 冠詞 and every dress of it (定冠詞／屬格冠詞／中性冠詞…), and the bare
  case and number labels 主格／受格／賓格／與格／屬格／單數／複數, together with the
  basic Japanese particle labels 主題／接續／過去／敬體／方向·對象.

Two things this deliberately does **not** touch:

* A parenthesis holding a Chinese *meaning* rather than a term — の「（的）」,
  も「（也）」, か「（嗎）」. Those are the gloss, not a note about it.
* The word itself. Where the label was appended to a meaning （我（賓格）） the
  meaning stays and the label goes; where the label *was* the whole gloss, the
  gloss goes empty and the word prints with nothing under it, which is what
  「太常見了就不用」 asks for.

    python -X utf8 scripts/prune_gloss_terms.py            # 只報告
    python -X utf8 scripts/prune_gloss_terms.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers"

FILES = (
    "greek-full/interlinear.json",
    "latin-full/interlinear.json",
    "japanese-full/interlinear.json",
    "japanese-full/interlinear-gloss.json",
    "hebrew-full/interlinear.json",
)

# 一律留下：構造的名字，不是格位的名字。
KEEP = (
    "標記", "記號", "助動詞", "關係代詞", "關係代名詞",
    "意志", "推量", "可能", "使役", "謙讓", "願望", "命令", "禁止", "尊敬",
)
# 一律拿掉：冠詞與光桿的格位／數，以及「這個詞不必譯」那一類的空話。
DROP = {
    "冠詞", "定冠詞", "屬格冠詞", "中性冠詞", "賓格冠詞", "受格冠詞", "定冠詞屬格",
    "主格", "受格", "賓格", "與格", "屬格", "呼格", "奪格", "用格",
    "單數", "複數", "複數屬格", "中性複數屬格", "陽性", "陰性", "中性",
    "虛詞", "質詞", "語氣詞", "介系詞", "介", "不譯",
}
# 🚨 日文例外（擁有者 2026-09-16 裁定：「保留日文助詞標記」）。
# 日文的格位標籤跟希臘拉丁的不是同一回事：希臘的「（賓格）」是附在一個本來就有
# 意思的詞後面，拿掉還剩「我」；日文的「（主題）」就是 は 的全部內容，拿掉之後
# 那個詞底下什麼都沒有。而 は 與 が 的分別正是靠這兩個標記分辨的——全套拿掉會
# 讓兩萬一千個助詞在逐詞層變成一模一樣的空白。
DROP_NOT_IN_JAPANESE = {
    "主格", "受格", "賓格", "與格", "屬格",
}
PAREN = re.compile(r"[（(]([^）)]{1,14})[）)]")
ZH_KEYS = {"glossZh"}


def prune(gloss: str, japanese: bool = False) -> str:
    """Remove the droppable notes from one gloss, leaving everything else alone."""
    drop = DROP - DROP_NOT_IN_JAPANESE if japanese else DROP

    def swap(match: re.Match[str]) -> str:
        term = match.group(1).strip()
        if any(mark in term for mark in KEEP):
            return match.group(0)
        return "" if term in drop else match.group(0)

    return PAREN.sub(swap, gloss).strip()


def walk(node, counts: Counter, emptied: Counter, apply: bool, japanese: bool):
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key in ZH_KEYS and isinstance(value, str) and value:
                fixed = prune(value, japanese)
                if fixed != value:
                    counts[value] += 1
                    if not fixed:
                        emptied[value] += 1
                out[key] = fixed if apply else value
            else:
                out[key] = walk(value, counts, emptied, apply, japanese)
        return out
    if isinstance(node, list):
        return [walk(item, counts, emptied, apply, japanese) for item in node]
    return node


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    for relative in FILES:
        path = CACHE / relative
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        counts: Counter = Counter()
        emptied: Counter = Counter()
        japanese = relative.startswith("japanese-")
        repaired = walk(payload, counts, emptied, args.write, japanese)
        changed = sum(counts.values())
        blanked = sum(emptied.values())
        if not changed:
            print(f"✔ {relative}")
            continue
        print(f"· {relative}：{changed} 條要改，其中 {blanked} 條改完是空的")
        for gloss, n in counts.most_common(5):
            print(f"      {gloss} → {prune(gloss, japanese) or '（空）'}　×{n}")
        if args.write:
            path.write_text(json.dumps(repaired, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"      已改寫 {path.relative_to(ROOT)}")
    if not args.write:
        print("（未寫入；加 --write）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
