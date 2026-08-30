#!/usr/bin/env python3
"""Repair the Hebrew proper-name appendix: the Genesis line, one label, no repeats.

Three faults the owner found on 2026-08-29, all of them visible on the printed
card and none of them caught by any gate:

1. **The founding generations are missing.** The table had 119 names and not one
   of 撒拉, 以撒, 利百加, 拉結, 利亞, 以實瑪利, 以掃, 夏甲, 悉帕, 辟拉, 挪亞,
   亞當, 塞特, 以諾, 瑪土撒拉, nor any of the twelve tribal ancestors. The list
   was built from what the fifty printed chapters happen to contain, and those
   chapters are not Genesis-heavy — so the appendix of a Hebrew Bible reader had
   no Abraham's household in it.
2. **A name could appear twice.** 耶路撒冷 sat at two slots of the same lesson.
3. **Two labels on one card.** `properNameTypes` is a list of everything Strong's
   mentions, so 以色列 prints 「人名、民族／國名」 and 但 prints 「人名、地名」.
   That is evidence worth keeping in the data, but a card needs one word.

The fixes, in the order they matter:

* the added names take their **pointed form from Genesis itself** — this reader's
  rule is that a name is spelled as its earliest occurrence spells it, so the
  form comes from the OSHB text rather than a lexicon's citation form, with the
  cantillation stripped because those accents belong to the verse and not to the
  name;
* the printed label becomes the single nine-category `category`, which already
  exists and already decides the question;
* entries are keyed on their pointed form, and lesson slots are renumbered so no
  lesson has two names in one position.

    python -X utf8 scripts/fix_hebrew_proper_names.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ROOT / "data/originalReaders/vocabulary/hebrew-proper-names.json"
# 印出來的附錄卡與網頁附錄表讀的是這一份，不是上面那一份詞表。第一次只改了
# 詞表，卡片一點也沒變——改對了檔案才算修好。
APPENDIX = ROOT / "output/source-cache/original-readers/hebrew-full/appendix-tables.json"
GENESIS = ROOT / "output/source-cache/scripture/morphology/books/Gen.json"
DICTIONARY = ROOT / "output/source-cache/scripture/fhl-strong-dictionary.json"

# 重音記號（טעמים）屬於那一節經文，不屬於這個名字；母音點要留。
CANTILLATION = re.compile(r"[֑-ֽֿ֯׀׃-׆]")

# 要補的人：亞當到約瑟這條線。Strong 編號逐一以信望愛字典的釋義驗過，
# 附點寫法取自創世記本文。分類用九類裡的既有名稱，一人一類。
ADDITIONS = [
    (120, "亞當", "族長與先知", "人類始祖；亞當"),
    (8352, "塞特", "族長與先知", "塞特，亞當第三子"),
    (2585, "以諾", "族長與先知", "以諾，與神同行"),
    (4968, "瑪土撒拉", "族長與先知", "瑪土撒拉，以諾之子"),
    (5146, "挪亞", "族長與先知", "挪亞，方舟的建造者"),
    (85, "亞伯拉罕", "族長與先知", "亞伯拉罕，信心之父"),
    (8283, "撒拉", "族長與先知", "撒拉，亞伯拉罕之妻"),
    (1904, "夏甲", "族長與先知", "夏甲，撒拉的埃及使女"),
    (6989, "基土拉", "族長與先知", "基土拉，亞伯拉罕續娶之妻"),
    (3458, "以實瑪利", "族長與先知", "以實瑪利，亞伯拉罕與夏甲之子"),
    (3327, "以撒", "族長與先知", "以撒，亞伯拉罕與撒拉之子"),
    (7259, "利百加", "族長與先知", "利百加，以撒之妻"),
    (6215, "以掃", "族長與先知", "以掃，以撒長子"),
    (3290, "雅各", "族長與先知", "雅各，以色列"),
    (3812, "利亞", "族長與先知", "利亞，雅各之妻"),
    (7354, "拉結", "族長與先知", "拉結，雅各之妻"),
    (2153, "悉帕", "族長與先知", "悉帕，利亞的使女"),
    (1090, "辟拉", "族長與先知", "辟拉，拉結的使女"),
    (7205, "流便", "族長與先知", "流便，雅各長子；流便支派"),
    (8095, "西緬", "族長與先知", "西緬，雅各次子；西緬支派"),
    (3878, "利未", "族長與先知", "利未，雅各三子；利未支派"),
    (3063, "猶大", "族長與先知", "猶大，雅各四子；猶大支派"),
    (1835, "但", "族長與先知", "但，雅各五子；但支派"),
    (5321, "拿弗他利", "族長與先知", "拿弗他利，雅各六子；拿弗他利支派"),
    (1410, "迦得", "族長與先知", "迦得，雅各七子；迦得支派"),
    (836, "亞設", "族長與先知", "亞設，雅各八子；亞設支派"),
    (3485, "以薩迦", "族長與先知", "以薩迦，雅各九子；以薩迦支派"),
    (2074, "西布倫", "族長與先知", "西布倫，雅各十子；西布倫支派"),
    (3130, "約瑟", "族長與先知", "約瑟，雅各十一子"),
    (1144, "便雅憫", "族長與先知", "便雅憫，雅各幼子；便雅憫支派"),
    (4519, "瑪拿西", "族長與先知", "瑪拿西，約瑟長子；瑪拿西支派"),
    (669, "以法蓮", "族長與先知", "以法蓮，約瑟次子；以法蓮支派"),
]


# 使用者 2026-08-29 定的分類：人名只分「先祖與族長／君王／先知／新約門徒」，
# 其餘歸其他人名；地名與民族國名照舊。這是判斷不是查表，所以逐個寫出來——
# 押沙龍是王子不是王，巴蘭是受雇的占卜者不是先知，約書亞是領袖不是先知。
ANCESTORS = {
    "亞當", "塞特", "以諾", "瑪土撒拉", "挪亞", "亞伯蘭", "亞伯拉罕", "撒拉", "夏甲",
    "基土拉", "以實瑪利", "以撒", "利百加", "以掃", "雅各", "利亞", "拉結", "悉帕",
    "辟拉", "呂便", "流便", "西緬", "利未", "猶大", "但", "拿弗他利", "迦得", "亞設",
    "以薩迦", "西布倫", "約瑟", "便雅憫", "瑪拿西", "以法蓮",
}
KINGS = {
    "掃羅", "大衛", "所羅門", "羅波安", "耶羅波安", "亞哈", "希西家", "約西亞",
    "西底家", "耶戶", "亞撒", "約沙法", "約阿施", "亞撒利雅", "亞比米勒",
    "尼布甲尼撒", "便哈達", "巴勒",
}
PROPHETS = {"摩西", "撒母耳", "以利亞", "以利沙", "耶利米", "拿單"}
DISCIPLES: set[str] = set()   # 希伯來聖經沒有；這一類是給希臘那副用的

# 名字被寫成一句描述的，逐個改回名字。「有福的」是 אָשֵׁר 的字義，不是那個人。
NAME_FIXES = {"有福的": "亞設"}

# 這幾筆被歸成人名，其實是地名或民族。
PLACE_LIKE = {"基列": "地名", "希伯崙": "地名", "亞述": "民族與國名", "以東": "民族與國名",
              "亞蘭": "民族與國名", "米甸": "民族與國名", "法老": "其他人名"}


def person_category(name: str, current: str) -> str:
    if name in ANCESTORS:
        return "先祖與族長"
    if name in KINGS:
        return "君王"
    if name in PROPHETS:
        return "先知"
    if name in DISCIPLES:
        return "新約門徒"
    return PLACE_LIKE.get(name, current if current in ("地名", "民族與國名") else "其他人名")


def strip_accents(text: str) -> str:
    return CANTILLATION.sub("", unicodedata.normalize("NFC", text))


def head_name(gloss: str) -> str:
    """卡面該印的名字：整串裡「；」之前那一段。

    表裡的中文欄常是一整句描述——「以實瑪利；亞伯拉罕長子及五名以色列人的名字」
    ——那是註解不是名字，印在卡上會被字級階梯縮到看不清。名字歸名字、說明歸
    說明，順帶讓「同一個名字出現兩次」抓得出來。
    """

    return re.split(r"[；;]", gloss)[0].strip()


def genesis_forms() -> dict[int, tuple[str, str]]:
    """Each Strong number's first spelling in Genesis, and where it is."""

    data = json.loads(GENESIS.read_text(encoding="utf-8"))["byVerse"]

    def order(ref: str) -> tuple[int, int]:
        _, chapter, verse = ref.rsplit(".", 2)
        return int(chapter), int(verse)

    found: dict[int, tuple[str, str]] = {}
    for ref in sorted(data, key=order):
        for word in data[ref]:
            strong = word.get("strong", "")
            if not strong.startswith("H"):
                continue
            number = int(strong[1:])
            if number in found:
                continue
            # 前綴（介系詞、冠詞、連接詞）不是名字的一部分。
            found[number] = (strip_accents(word["text"].split("/")[-1]), ref)
    return found


def repair_appendix(forms: dict[str, tuple[str, str]], dictionary: dict, write: bool) -> None:
    """同樣三件事，做在附錄表上：補世系、去重複、一節一個標籤。

    附錄表的專名是按「節」分組的，而節名就是那九類——所以「一張卡一個標籤」
    在這裡等於「一個名字只出現在一節裡」。以色列同時是人也是國，放在民族與
    國名那一節，types 欄留著當證據。
    """

    payload = json.loads(APPENDIX.read_text(encoding="utf-8"))
    table = next(t for t in payload["tables"] if "proper" in t["id"])

    seen_names: set[str] = set()
    seen_forms: set[str] = set()
    dropped = []
    for group in table["groups"]:
        kept = []
        for entry in group["entries"]:
            name = NAME_FIXES.get(head_name(entry.get("glossZh", "")), head_name(entry.get("glossZh", "")))
            form = strip_accents(entry.get("pointed", ""))
            if name in seen_names or form in seen_forms:
                dropped.append(name)
                continue
            seen_names.add(name)
            seen_forms.add(form)
            entry["name"] = name
            entry["nameNote"] = (re.split(r"[；;]", entry.get("glossZh", ""), 1) + [""])[1].strip()
            entry["glossZh"] = name
            kept.append(entry)
        group["entries"] = kept

    # 分節即標籤，所以移動一筆就是改它的標籤。
    # 上一輪先建了 id 是英文的節（ancestors／prophets），這張表其餘的節 id 都是
    # 中文類名。id 一半中文一半英文，靠 id 找節的程式就會找不到——順手正規化。
    for group in table["groups"]:
        if group.get("titleZh"):
            group["id"] = group["titleZh"]
    by_title = {g.get("titleZh") or g.get("id"): g for g in table["groups"]}
    ancestors = by_title.setdefault("先祖與族長", {"id": "先祖與族長", "titleZh": "先祖與族長", "entries": []})
    prophets = by_title.setdefault("先知", {"id": "先知", "titleZh": "先知", "entries": []})
    if ancestors not in table["groups"]:
        table["groups"].append(ancestors)
    if prophets not in table["groups"]:
        table["groups"].append(prophets)

    moved = 0
    for group in table["groups"]:
        if group is ancestors or group is prophets:
            continue
        staying = []
        for entry in group["entries"]:
            name = entry["name"]
            if name in ANCESTORS:
                ancestors["entries"].append(entry); moved += 1
            elif name in PROPHETS:
                prophets["entries"].append(entry); moved += 1
            elif (group.get("titleZh") or "") == "族長與先知":
                # 舊節拆成「先祖與族長」與「先知」之後，這一節就不該再存在。
                # 留在裡面的是約書亞（領袖）與約伯（受苦的義人），兩位都不是
                # 族長也不是先知，歸其他人名。
                entry["category"] = "其他人名"
                by_title.setdefault(
                    "其他人名", {"id": "其他人名", "titleZh": "其他人名", "entries": []}
                )["entries"].append(entry)
                moved += 1
            else:
                staying.append(entry)
        group["entries"] = staying

    added = 0
    for number, zh, category, note in ADDITIONS:
        if zh in seen_names:
            continue
        pointed, ref = forms.get(number, ("", ""))
        if not pointed:
            continue
        entry = dictionary.get(f"H{number:05d}", {})
        ancestors["entries"].append(
            {
                "pointed": pointed,
                "glossZh": zh,
                "name": zh,
                "nameNote": note,
                "strong": f"H{number}",
                "types": ["person"],
                "category": "先祖與族長",
                "firstOccurrence": ref,
                "transliteration": "",
                "frequency": None,
                "verification": "附點取自創世記本文（OSHB）",
            }
        )
        seen_names.add(zh)
        added += 1

    # 安息日在曆法表已經有一張卡了，專名表的「節期與聖日」再出一張就是同一個
    # 詞出現兩次——跨表也算重複。節期歸曆法表。
    for group in table["groups"]:
        if (group.get("titleZh") or "") == "節期與聖日":
            group["entries"] = []

    # 舊的「族長與先知」那一節已經拆成兩節，空了就拿掉。
    table["groups"] = [g for g in table["groups"] if g["entries"]]
    total = sum(len(g["entries"]) for g in table["groups"])
    print(f"附錄表：刪重複 {len(dropped)}（{dropped}）、改節 {moved}、補世系 {added}，共 {total} 條")
    for group in table["groups"]:
        print(f'    {group.get("titleZh") or group["id"]}: {len(group["entries"])}')
    if write:
        APPENDIX.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  已寫入 {APPENDIX.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    payload = json.loads(NAMES.read_text(encoding="utf-8"))
    items = payload["items"]
    forms = genesis_forms()
    dictionary = json.loads(DICTIONARY.read_text(encoding="utf-8"))["entries"] if DICTIONARY.exists() else {}

    # ── 一、去重 ──────────────────────────────────────────────────────
    # 兩個關鍵都要看：附點寫法（同一個字的兩種寫法算兩筆）與**印出來的名字**。
    # 耶路撒冷有寫法不同的兩筆（ketiv／qere），字形不同但卡上印出來一模一樣，
    # 只比字形是抓不到的——使用者看到的重複就是這一種。
    seen: dict[str, dict] = {}
    by_name: dict[str, dict] = {}
    duplicates = []
    for item in items:
        item["name"] = head_name(item.get("glossZh") or "")
        form = strip_accents(item.get("pointed") or "")
        if form in seen or item["name"] in by_name:
            duplicates.append(item["name"])
            continue
        seen[form] = item
        by_name[item["name"]] = item
    kept = list(seen.values())

    # ── 二、補上創世記那一條線 ────────────────────────────────────────
    added = []
    for number, zh, category, gloss in ADDITIONS:
        pointed, ref = forms.get(number, ("", ""))
        if not pointed:
            print(f"  ✗ {zh}：創世記裡找不到 H{number:05d}，不補（不自己造字形）")
            continue
        if strip_accents(pointed) in seen or zh in by_name:
            continue
        entry = dictionary.get(f"H{number:05d}", {})
        added.append(
            {
                "pointed": pointed,
                "sourcePointed": pointed,
                "unpointed": re.sub(r"[֑-ׇ]", "", pointed),
                "glossZh": zh,
                "name": zh,
                "glossEn": (entry.get("head") or "").split()[1] if entry.get("head") else "",
                "note": gloss,
                "strong": f"H{number}",
                "strongs": [f"H{number}"],
                "isProperName": True,
                "properNameTypes": ["person"],
                "category": category,
                "categoryRoute": "genesis-line",
                "firstOccurrence": ref,
                "itemKind": "proper_name",
                "sourceType": "genesis_line",
                "verification": "附點取自創世記本文（OSHB），Strong 編號經信望愛字典釋義核對",
            }
        )
    kept.extend(added)

    # ── 三、一張卡一個標籤，並重排課次位置 ────────────────────────────
    by_lesson: dict[int, int] = {}
    for item in kept:
        name = NAME_FIXES.get(item.get("name", ""), item.get("name") or head_name(item.get("glossZh") or ""))
        item["name"] = name
        # 卡面只印名字；「亞伯拉罕長子及五名以色列人的名字」那種說明改放註解欄。
        rest = re.split(r"[；;]", item.get("glossZh") or "", 1)
        item["nameNote"] = rest[1].strip() if len(rest) > 1 else item.get("note", "")
        item["glossZh"] = name
        item["printedLabel"] = person_category(name, item.get("category") or "其他人名")
        item["category"] = item["printedLabel"]
        lesson = item.get("lesson") or 0
        by_lesson[lesson] = by_lesson.get(lesson, 0) + 1
        item["lessonSlot"] = by_lesson[lesson]

    print(f"原有 {len(items)} 筆；重複刪掉 {len(duplicates)}（{duplicates}）")
    print(f"補上創世記世系 {len(added)} 筆；合計 {len(kept)} 筆")
    labels = {item["printedLabel"] for item in kept}
    print("印在卡上的標籤（一張一個）:", sorted(labels))

    repair_appendix(forms, dictionary, False)
    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    payload["items"] = kept
    payload["count"] = len(kept)
    payload["note"] = (
        "希伯來專名表。一筆一個名字（依附點寫法去重），標籤取九類分類，一張卡只印一個；"
        "亞當到約瑟的世系另行補入，附點取自創世記本文。"
    )
    NAMES.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已寫入 {NAMES.relative_to(ROOT)}")
    repair_appendix(forms, dictionary, True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
