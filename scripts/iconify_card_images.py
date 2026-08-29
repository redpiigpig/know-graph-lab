#!/usr/bin/env python3
"""替「跟不相干的詞共用同一張圖」的卡另外找一張圖，來源是 Iconify 上的開源圖庫。

OpenMoji 只有兩千多個概念，三副卡卻有 3,802 張，結果 681 張圖被重複用掉——
希臘卡有一張握手用在 26 張卡上。同詞根共用（בֵּן／בָּנִים 都用男孩）是好事，
不相干的詞共用才是問題：學的人會把兩個字記成同一件事。

本腳本只動後者。四個圖庫合計一萬七千個概念，補得上 OpenMoji 缺的古代名物
（鐮刀、祭壇、戰車、軛、長矛）與抽象詞：

    game-icons  4,133  CC BY 3.0    黑色剪影，古代器物最齊
    ph          9,072  MIT          線條乾淨，抽象詞多
    mdi         7,447  Apache 2.0   概念最全
    tabler      6,184  MIT          與 ph 互補

比對規則跟 OpenMoji 那支一樣嚴：**只認圖示本名，不認標籤**，而且要跟英文詞義
切出來的詞完全相同才算數。找不到就維持原圖，不硬換。

    python scripts/iconify_card_images.py --lang hbo        # 只看會換掉幾張
    python scripts/iconify_card_images.py --lang hbo --write
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/flashcards"
ICON_DIR = CACHE / "iconify"
API = "https://api.iconify.design"
USER_AGENT = {"User-Agent": "know-graph-lab/1.0 (private study flashcards)"}
# 順序即優先序：古代名物先問 game-icons，抽象詞再交給後面三個。
PREFIXES = ("game-icons", "ph", "mdi", "tabler")

LANGS = {
    "hbo": {
        "vocab": ROOT / "data/originalReaders/vocabulary/hebrew-1000.json",
        "images": CACHE / "hebrew-card-images.json",
        "output": CACHE / "hebrew-card-icons.json",
    },
    "grc": {
        "vocab": ROOT / "data/originalReaders/vocabulary/greek-2000.json",
        "images": CACHE / "greek-card-images.json",
        "output": CACHE / "greek-card-icons.json",
    },
    "lat": {
        "vocab": ROOT / "data/originalReaders/vocabulary/latin-2000.json",
        "images": CACHE / "latin-card-images.json",
        "output": CACHE / "latin-card-icons.json",
    },
}


def latin_key(entry: dict) -> str:
    spec = importlib.util.spec_from_file_location(
        "build_flashcards", ROOT / "scripts/build_flashcards.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    globals()["latin_key"] = module.latin_key      # 只載入一次
    return module.latin_key(entry)


def keywords(gloss_en: str, module) -> list[str]:
    """比 OpenMoji matcher 更寬一點的候選詞，但仍然只用來做「本名完全相符」比對。

    圖庫的命名是單數、連字號（`olive-tree`、`wine-bottle`），而 Strong 的釋義是
    一長串英文；只切前幾段會漏掉真正具體的那個詞。這裡把每段都拆成詞、補上去掉
    複數的形式、也試著把相鄰兩詞連成連字號名。
    """

    out: list[str] = []
    for segment in module.english_candidates(gloss_en):
        words = [w for w in segment.replace(" ", " ").split() if w.isalpha()]
        for size in (len(words), 2, 1):
            for start in range(0, max(1, len(words) - size + 1)):
                piece = words[start : start + size]
                if len(piece) != size or not piece:
                    continue
                out.append("-".join(piece))
        for word in words:
            if word.endswith("ies") and len(word) > 4:
                out.append(word[:-3] + "y")
            elif word.endswith("es") and len(word) > 4:
                out.append(word[:-2])
            elif word.endswith("s") and not word.endswith("ss") and len(word) > 3:
                out.append(word[:-1])
    seen: set[str] = set()
    return [w for w in out if not (w in seen or seen.add(w))]


def matcher():
    """借 OpenMoji matcher 的英文詞義切詞與歧義詞黑名單，規則要一致。"""

    spec = importlib.util.spec_from_file_location(
        "match_flashcard_images", ROOT / "scripts/match_flashcard_images.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers=USER_AGENT)
    return urllib.request.urlopen(request, timeout=60).read()


def icon_names() -> dict[str, str]:
    """一次抓下四個圖庫的完整圖示清單，之後全在本機比對，不逐字打 search API。"""

    names: dict[str, str] = {}
    for prefix in reversed(PREFIXES):          # 反著填，前面的圖庫覆蓋後面的
        cache = ICON_DIR / f"_names-{prefix}.json"
        if not cache.exists():
            ICON_DIR.mkdir(parents=True, exist_ok=True)
            print(f"  下載 {prefix} 圖示清單…")
            cache.write_bytes(fetch(f"{API}/collection?prefix={prefix}"))
            time.sleep(1)
        payload = json.loads(cache.read_text(encoding="utf-8"))
        listed: list[str] = list(payload.get("uncategorized") or [])
        for group in (payload.get("categories") or {}).values():
            listed.extend(group)
        for name in listed:
            names[name] = f"{prefix}:{name}"
    return names


def png_for(icon: str) -> Path:
    """把圖示抓成 618 px 的黑色 PNG；卡片端要上色時再自己染。"""

    path = ICON_DIR / f"{icon.replace(':', '-')}.png"
    if path.exists():
        return path
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    prefix, name = icon.split(":", 1)
    svg = ICON_DIR / f"{icon.replace(':', '-')}.svg"
    if not svg.exists():
        svg.write_bytes(fetch(f"{API}/{prefix}/{name}.svg?height=618"))
        time.sleep(0.2)
    page = fitz.open(svg)[0]
    scale = 618 / max(page.rect.width, page.rect.height)
    page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True).save(path)
    return path


def cards_for(lang: str) -> list[dict]:
    """回傳 [{key, lemma, glossEn}]，key 與配圖表同一把鑰匙。"""

    payload = json.loads(LANGS[lang]["vocab"].read_text(encoding="utf-8"))
    entries = payload["entries"] if isinstance(payload, dict) else payload
    rows = []
    for entry in entries:
        if lang == "hbo":
            key = f"{entry['strong']}|{entry['pointed']}"
            lemma = entry["strong"] or entry["pointed"]
        elif lang == "grc":
            key = entry["lemma"]
            lemma = entry["lemma"]
        else:
            key = latin_key(entry)          # 拉丁配圖表用的是折疊過的詞形，不是 headword
            lemma = entry["headword"]
        rows.append({"key": key, "lemma": lemma, "glossEn": entry.get("glossEn") or ""})
    return rows


def variants(names: dict[str, str], keyword: str) -> list[tuple[str, str]]:
    """同一個概念的其他畫法：名字裡含這個關鍵詞的圖示。

    使用者要的正是這一層——「眼睛的單數與複數也要用不同的眼睛卡通圖」。
    Iconify 那四個庫對一個概念常有十幾種畫法（eye、eye-off、eye-closed、
    eye-slash…），所以本名對不上的時候，就在同一個概念裡換一張畫法。

    只認以連字號分隔的詞，不做子字串比對：`ear` 不可以命中 `search`、
    `research`、`earth`，那種命中看起來像成功而畫的是完全不同的東西。
    """

    hits = []
    for name, icon in names.items():
        parts = re.split(r"[-_]", name)
        if keyword in parts and name != keyword:
            hits.append((name, icon))
    # 名字越短越接近那個概念本身（eye-off 勝過 eye-dropper-empty）。
    hits.sort(key=lambda pair: (len(pair[0]), pair[0]))
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="替共用圖的卡另找一張圖")
    parser.add_argument("--lang", choices=sorted(LANGS), required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="只處理前 N 張，打樣用")
    args = parser.parse_args()

    module = matcher()
    config = LANGS[args.lang]
    images = json.loads(config["images"].read_text(encoding="utf-8"))["images"]
    rows = cards_for(args.lang)

    # 使用者 2026-08-29 定的硬規矩：**同一種語言裡，一張圖只能出現在一張卡上**，
    # 連「眼睛的單數與複數」都要用不同的眼睛圖。所以這裡看的是「幾張卡」而不是
    # 「幾個詞」——同一個詞的兩個字形共用，以前算刻意，現在也要拆開。
    #
    # 每張圖留給最有資格的那張卡：手工指定的優先（那是有人特地為它挑的），
    # 其次詞義最短的（意思最直白的那個詞最配得上那張圖）。其餘的另外找圖。
    cards_per_picture: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        record = images.get(row["key"])
        if record:
            cards_per_picture[record["hexcode"]].append(row)

    def claim(row: dict) -> tuple[int, int, str]:
        record = images.get(row["key"], {})
        override = 0 if record.get("source") == "override" else 1
        return (override, len(row.get("glossZh") or ""), row["key"])

    shared: list[dict] = []
    for hexcode, cards in cards_per_picture.items():
        if len(cards) < 2:
            continue
        cards.sort(key=claim)
        shared.extend(cards[1:])          # 第一張保留原圖，其餘要換
    shared.sort(key=lambda row: -len(cards_per_picture[images[row["key"]]["hexcode"]]))
    if args.limit:
        shared = shared[: args.limit]
    print(f"  與同語言其他卡共用一張圖、必須換掉的：{len(shared)} 張")

    names = icon_names()
    # hexcode → OpenMoji 本名，給上面那層備援查概念用。
    openmoji_name = {entry["hexcode"]: name for name, entry in module.load_openmoji().items()}
    print(f"  四個圖庫合計 {len(names)} 個圖示本名")
    # 人工審圖刷掉的組合：英文對得上、圖卻不對（mdi:iron 是熨斗不是鐵、
    # ph:alien 是外星人不是外邦人、ph:command 是 ⌘ 不是吩咐、tabler:grave 是
    # 墓碑不是「寫」）。跳過之後那張卡會去試下一個候選詞。
    rejects = set()
    reject_file = CACHE / "icon-rejects.json"
    if reject_file.exists():
        rejects = set(json.loads(reject_file.read_text(encoding="utf-8"))["pairs"])
    print(f"  人工排除的組合 {len(rejects)}")

    taken = {record["hexcode"] for record in images.values()}
    assigned: dict[str, dict] = {}
    for row in shared:
        options: list[tuple[str, str]] = []
        for candidate in keywords(row["glossEn"], module):
            if candidate in module.AMBIGUOUS_EN:
                continue
            exact = names.get(candidate)
            if exact:
                options.append((candidate, exact))
            # 本名對不上就找同概念的其他畫法，一個關鍵詞最多試六種。
            options.extend((candidate, icon) for _, icon in variants(names, candidate)[:6])
        if not options:
            # 英文詞義一個字也配不上時，改用「它現在共用的那張圖」的概念去找。
            # 那張圖本來就是為這個意思挑的，換的是畫法不是意思——使用者要的
            # 「同一個眼睛概念、不同的眼睛圖」正是這一層。
            current = images.get(row["key"], {})
            concept = (openmoji_name.get(current.get("hexcode")) or "").lower()
            for word in re.split(r"[\s-]+", concept):
                if len(word) < 3 or word in module.AMBIGUOUS_EN:
                    continue
                exact = names.get(word)
                if exact:
                    options.append((word, exact))
                options.extend((word, icon) for _, icon in variants(names, word)[:6])
        for candidate, icon in options:
            if icon in taken or f"{icon}|{candidate}" in rejects:
                continue
            if args.write:
                try:
                    path = png_for(icon)
                except Exception as error:                  # 網路或轉檔失敗就跳過
                    print(f"    ⚠ {icon} 取不到：{error}")
                    continue
            else:
                path = ICON_DIR / f"{icon.replace(':', '-')}.png"   # 試跑不下載
            taken.add(icon)
            assigned[row["key"]] = {
                "icon": icon,
                "file": path.name,
                "source": icon.split(":", 1)[0],
                "glossEn": candidate,
            }
            break

    by_set = collections.Counter(record["source"] for record in assigned.values())
    print(f"  另配到獨立圖示 {len(assigned)} 張：{dict(by_set)}")

    if args.write:
        config["output"].write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0.0",
                    "sources": {
                        "game-icons": "CC BY 3.0 — game-icons.net",
                        "ph": "MIT — Phosphor Icons",
                        "mdi": "Apache 2.0 — Material Design Icons",
                        "tabler": "MIT — Tabler Icons",
                    },
                    "note": "只補「與不相干的詞共用一張圖」的卡；只認圖示本名精確相符，配不到就維持原圖。",
                    "cards": assigned,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\n已寫出 {config['output']}")
    else:
        print("\n（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
