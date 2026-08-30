#!/usr/bin/env python3
"""體檢 `*-card-icons.json` 這本帳本：放行的那一層也不是自動安全的。

帳本分兩區：`cards` 是會真的印上卡片的（build_flashcards.py 只讀這個 key），
`pendingReview` 是靠「同概念換畫法」猜出來、必須人看過的。放行那一層的判準是
「圖示本名與候選詞完全相符」——但**相符在第幾個義項上，判準沒有問**。

Strong's 的釋義把引申義與冷僻義並列，於是 בָּרָא「to create ... to cut down」
在第二義上命中 `tabler:cut`，卡片印一把剪刀教「創造」；מִקְנֶה「cattle」命中
`mdi:water`（釋義裡的 watering）。這種錯跟待審那批一樣是錯圖，只是它已經在
放行區裡了。本腳本把「候選詞不在第一個義項」的挑出來，讓人優先看那些。

中文一律讀 build_flashcards.py 讀的那份（希伯來與希臘各有一份審過的 by-lemma
詞義檔，拉丁在詞表自己身上），不讀詞表的 glossZh——希伯來詞表那一欄一千筆全是
空的，拿它當中文欄會印出一張空表，看起來卻像跑完了。

    python scripts/audit_card_icons.py                 # 三種語言，只列可疑的
    python scripts/audit_card_icons.py --lang hebrew --all
    python scripts/audit_card_icons.py --section pending   # 看待審那一區
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LANGS = {
    "hebrew": {
        "code": "hbo",
        "vocab": ROOT / "data/originalReaders/vocabulary/hebrew-1000.json",
        "glosses": CACHE / "original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json",
    },
    "greek": {
        "code": "grc",
        "vocab": ROOT / "data/originalReaders/vocabulary/greek-2000.json",
        "glosses": CACHE / "original-readers/greek-full/greek-2000-gloss-zh-by-lemma.json",
    },
    "latin": {
        "code": "lat",
        "vocab": ROOT / "data/originalReaders/vocabulary/latin-2000.json",
        "glosses": None,                      # 拉丁的繁中就在詞表裡
    },
}


def chinese_by_card_key(lang: str, icon_mod) -> dict[str, str]:
    """卡片鍵 → 繁中詞義，來源與印卡時完全相同。"""

    config = LANGS[lang]
    payload = json.loads(config["vocab"].read_text(encoding="utf-8"))
    entries = payload["entries"] if isinstance(payload, dict) else payload
    out: dict[str, str] = {}
    if lang == "latin":
        for entry in entries:
            out[icon_mod.latin_key(entry)] = (entry.get("glossZh") or "").strip()
        return out
    reviewed = json.loads(config["glosses"].read_text(encoding="utf-8"))
    if lang == "greek":
        table = {lemma: record["glossZh"] for lemma, record in reviewed["glosses"].items()}
        for entry in entries:
            out[entry["lemma"]] = (table.get(entry["lemma"]) or "").strip()
        return out
    table = {(item["strong"], item["pointed"]): item["glossZh"] for item in reviewed["items"]}
    for entry in entries:
        key = f"{entry['strong']}|{entry['pointed']}"
        out[key] = (table.get((entry["strong"], entry["pointed"])) or "").strip()
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="體檢卡片配圖帳本")
    parser.add_argument("--lang", choices=sorted(LANGS) + ["all"], default="all")
    parser.add_argument("--section", choices=("cards", "pending", "both"), default="cards")
    parser.add_argument("--all", action="store_true", help="連沒有疑點的也列出來")
    args = parser.parse_args()

    matcher = load("match_flashcard_images", ROOT / "scripts/match_flashcard_images.py")
    icon_mod = load("iconify_card_images", ROOT / "scripts/iconify_card_images.py")

    languages = sorted(LANGS) if args.lang == "all" else [args.lang]
    sections = ("cards", "pendingReview") if args.section == "both" else (
        {"cards": "cards", "pending": "pendingReview"}[args.section],)

    grand_total = grand_flagged = 0
    for lang in languages:
        ledger_path = CACHE / f"flashcards/{lang}-card-icons.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        rows = {row["key"]: row for row in icon_mod.cards_for(LANGS[lang]["code"])}
        chinese = chinese_by_card_key(lang, icon_mod)
        # 中文一筆都對不上就是鍵接錯了，不是資料缺——寧可停下也不要印一張空表。
        matched = sum(1 for key in ledger.get("cards", {}) if chinese.get(key))
        if ledger.get("cards") and not matched:
            raise SystemExit(f"{lang}：帳本的鍵一筆也對不上繁中詞義，鍵接錯了")

        for section in sections:
            records = ledger.get(section) or {}
            flagged = []
            for key, record in records.items():
                gloss_en = (rows.get(key) or {}).get("glossEn", "")
                segments = matcher.english_candidates(gloss_en)
                first = segments[0].lower().split() if segments else []
                candidate = record["glossEn"].replace("-", " ").lower().split()
                off_first = not (candidate and all(word in first for word in candidate))
                if off_first or args.all:
                    flagged.append((key, record, chinese.get(key, ""),
                                    segments[0] if segments else "", off_first))
            grand_total += len(records)
            grand_flagged += sum(1 for row in flagged if row[4])
            label = "放行" if section == "cards" else "待審"
            print(f"\n=== {lang} · {label} {len(records)} 張，"
                  f"候選詞不在第一義項的 {sum(1 for row in flagged if row[4])} 張 ===")
            for key, record, zh, first, off_first in flagged:
                mark = "⚠" if off_first else " "
                headword = key.split("|")[-1]
                print(f"{mark} {headword:<18}{zh:<22}{record['icon']:<30}"
                      f"配到「{record['glossEn']}」  第一義項：{first[:44]}")

    print(f"\n合計 {grand_total} 張，其中 {grand_flagged} 張命中的不是第一義項。")


if __name__ == "__main__":
    main()
