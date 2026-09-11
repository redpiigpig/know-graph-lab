# -*- coding: utf-8 -*-
"""《基督信徒的慰藉》裡內村引用的西文詩：中文欄改成「原文　／　中譯」並列。

為什麼要有這一支：內村在書中直接引英文與德文詩（布萊恩特、彌爾頓、胡德、席勒、
洪堡墓誌），`needs_translation` 判它們「不是日文」而整批跳過，於是中文欄留白，
reader 退回顯示原文。使用者 2026-09-10 定調 **原文＋中譯並列**（他的通則是
外文引文必附中譯），而且詩詞可用韻文體。

同一段引詩裡有幾行本來就譯過、有幾行沒有，這裡一併整成同一個格式，
不然一首詩會半英半中。

🚨 逐行對譯而非逐句：英詩跨行斷句（Milton 那五行是一個句子），所以中譯也照原樣
   斷行，讀者要合起來讀。這是詩的通例，不是譯錯。
🚨 只改這幾個明確的 index，而且動手前先比對原文字串——段落編號不是穩定鍵
   （[[feedback_reader_silent_failures]]）。

  python -X utf8 scripts/fix_consolations_verse.py --dry
  python -X utf8 scripts/fix_consolations_verse.py --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = Path(__file__).resolve().parent.parent / \
    ".claude/skills/ebook-collected-works/uchimura_data/consolations"

SEP = "　／　"

# (sec, index, 原文開頭比對, 中譯)
VERSE: list[tuple[str, int, str, str]] = [
    # 布萊恩特（第一章「所愛者逝去之時」）
    ("sec5", 7, "“Life mocks the idle hate", "生命嘲笑那徒然的憎恨——"),
    ("sec5", 8, "Of his arch-enemy Death", "其宿敵死亡的憎恨；不但如此，它逕自坐上"),
    ("sec5", 9, "Upon the tyrant's throne", "那暴君的寶座，即墳墓，"),
    ("sec5", 10, "And of the triumphs of his ghostly foe", "並將那幽冥仇敵的種種凱旋"),
    ("sec5", 11, "Makes his own nourishment.", "化作自己的養分。」——布萊恩特"),
    # 席勒《威廉‧泰爾》（內村下一段自己附了日譯「勇者は独り立つ時最も強し」）
    ("sec5", 37, "Der starke ist", "強者獨處之時最強。"),
    # 洪堡墓誌（第二章「被國人所棄之時」）
    ("sec6", 19, "In Deutschland geboren", "生於德意志，"),
    ("sec6", 20, "Ein B", "世界的公民。"),
    ("sec6", 21, "独逸国に生れたる世界の市民", "生於德意志國的世界公民"),
    # 第三章「被基督教會所棄」
    ("sec7", 17, "With one voice, O world", "世界啊，縱使你異口同聲否認，"),
    ("sec7", 18, "Stand thou on that side", "你就站到那一邊去罷——我站在這一邊！"),
    # 彌爾頓《復樂園》（第四章「事業失敗之時」）
    ("sec8", 1, "“When I was yet a child", "當我尚是孩童，一切孩童的遊戲"),
    ("sec8", 2, "To me was pleasing", "於我皆無樂趣；我一心"),
    ("sec8", 3, "Serious to learn and know", "認真學習與求知，進而去做"),
    ("sec8", 4, "What might be public good", "於公眾有益之事；我自認"),
    ("sec8", 5, "Born to that end.", "生而為此。」——彌爾頓《復樂園》"),
    # 湯瑪斯‧胡德〈嘆息橋〉（第五章「貧困逼迫之時」）
    ("sec9", 11, "“In she plunged boldly", "她毅然投身而下，"),
    ("sec9", 12, "No matter how coldly", "不管那湍急的河水"),
    ("sec9", 13, "The rough river ran", "流得何等冰冷——"),
    ("sec9", 14, "Picture it", "想像一下——想想看吧"),
    ("sec9", 15, "Dissolute Man !", "放縱之人！」——湯瑪斯‧胡德"),
]


# 青空文庫把德文的變音符號當成外字，輸出成「※」（m※chtigsten、B※rger）。
# 既然中文欄要並列原文，就把它補回可讀的樣子。只收查得到出處的這幾個，不猜。
GAIJI_FIX = {
    "m※chtigsten": "mächtigsten",
    "B※rger": "Bürger",
}


# ── 引擎翻一半的段落（partial）：人工補完 ────────────────────────────────────
#
# `fix_echo_and_meta` 認得出這幾段「譯文裡夾著假名、但後半不足以獨立成篇」，
# 但**不會自動切**——切了就是截斷。這裡逐段補完整。
# 格式與 VERSE 不同：這些是純中文，不並列原文（原文本來就是日文，reader 有原文欄）。
PARTIAL: list[tuple[str, int, str, str]] = [
    ("sec4", 3, "大正十二年（一九二三年）二月七日東京市外柏木",
     "大正十二年（一九二三年）二月七日　於東京市外柏木"),
    ("sec5", 16, "何様か何処かで相見んと",
     "不知何時、不知何處，我們終要再相見〕"),
    ("sec10", 31, "よろこび受けんふたつとも",
     "願這兩樣都歡喜領受，"),
    # 羅馬書八章 38–39 節。內村的日文作「我主イエスキリストに頼れる神の愛」，
    # 中譯依和合本語體，並照他的語序把「這愛是在…裡的」擺回句末。
    ("sec10", 66, "そは或いは死、或いは生",
     "我深信，無論是死、是生、是天使、是掌權的、是有能的、是現在的事、"
     "是將來的事、是高處的、是深處的，或是別的受造之物，"
     "都不能叫我們與神的愛隔絕；這愛是在我們的主耶穌‧基督裡的。"),
]


def bilingual(src: str, zh: str) -> str:
    """原文　／　中譯。純函式，測試鎖在 tests/test_consolations_verse.py。"""
    s = (src or "").strip()
    for bad, good in GAIJI_FIX.items():
        s = s.replace(bad, good)
    return f"{s}{SEP}{(zh or '').strip()}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    by_sec: dict[str, list] = {}
    for sec, idx, head, zh in VERSE:
        by_sec.setdefault(sec, []).append((idx, head, zh, True))
    for sec, idx, head, zh in PARTIAL:
        by_sec.setdefault(sec, []).append((idx, head, zh, False))

    total = skipped = 0
    for sec, items in by_sec.items():
        p = DATA / f"{sec}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        touched = False
        for idx, head, zh, pair in items:
            if idx >= len(d["src"]) or not d["src"][idx].startswith(head):
                print(f"  ⚠ {sec}[{idx}] 原文對不上（{d['src'][idx][:40] if idx < len(d['src']) else '越界'}）"
                      f"——跳過，段落編號不是穩定鍵")
                skipped += 1
                continue
            new = bilingual(d["src"][idx], zh) if pair else zh
            print(f"  {sec}[{idx}] {new[:88]}")
            if args.apply:
                d["zh"][idx] = new
                touched = True
            total += 1
        if touched:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{'已改' if args.apply else '將改'} {total} 段"
          + (f"，跳過 {skipped} 段" if skipped else ""))
    if not args.apply:
        print("加 --apply 才會真的寫入")


if __name__ == "__main__":
    main()
