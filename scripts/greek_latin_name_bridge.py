#!/usr/bin/env python3
"""用字形把希臘文與拉丁文的同一個專名接起來，順便長出思高↔和合本的譯名對照。

命名政策（使用者 2026-08-27）：**拉丁讀本用思高本，希臘與希伯來用和合本。**
所以三本書印出來的中文本來就不一樣，橋接不是要統一譯名，是要讓**分類**互通——
希臘那邊已經判定 Δαυίδ 是君王，拉丁的 David 就不必再判一次；而 Δαυίδ 的「大衛」
與 David 的「達味」對上之後，那一對本身就是一筆有憑據的思高↔和合本對照。

對法是字形，不是中文：中文正是分歧的那一端，拿它當鍵只會全部落空——拉丁上冊 585
條有 355 條有中文，卻只有 132 條分得出類，就是因為登錄收的是和合本而拉丁寫的是思高。

拉丁的聖經專名本來就是希臘文的轉寫，規則相當固定（Χ→ch、Θ→th、Φ→ph、αι→ae、
ου→u、字首粗氣號→h、-ος→-us），照著轉再折疊比對即可。對不上的就是對不上，
不做模糊比對——「差一兩個字母應該就是同一個人」正是印在紙上看不出來的那種錯。
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "data" / "originalReaders" / "vocabulary"
GREEK = V / "greek-appendices.json"
LATIN = V / "latin-appendices.json"
OUTPUT = V / "biblical-name-variants.json"

# 雙字母組合先換，否則 α 會先被單字母規則吃掉。
DIGRAPHS = [
    ("αι", "ae"), ("ει", "i"), ("οι", "oe"), ("υι", "ui"),
    ("αυ", "au"), ("ευ", "eu"), ("ηυ", "eu"), ("ου", "u"),
    ("γγ", "ng"), ("γκ", "nc"), ("γχ", "nch"), ("γξ", "nx"),
]

SINGLES = {
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "e",
    "θ": "th", "ι": "i", "κ": "c", "λ": "l", "μ": "m", "ν": "n", "ξ": "x",
    "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "y",
    "φ": "ph", "χ": "ch", "ψ": "ps", "ω": "o",
}

# 字尾的希臘語尾換成拉丁語尾。長的先試。
ENDINGS = [
    ("ος", "us"), ("ον", "um"), ("ης", "es"), ("ας", "as"), ("ᾶς", "as"),
    ("ευς", "eus"), ("ια", "ia"), ("η", "a"), ("α", "a"),
]


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if not unicodedata.combining(c)
    )


def has_rough_breathing(text: str) -> bool:
    """字首的粗氣號在拉丁裡寫成 H：Ἱερουσαλήμ → Hierusalem／Jerusalem。"""
    for char in unicodedata.normalize("NFD", text)[:3]:
        if char == "̔":
            return True
    return False


def to_latin(greek: str) -> str:
    """把一個希臘專名轉成拉丁拼法（近似，只求足以比對）。"""
    rough = has_rough_breathing(greek)
    text = strip_accents(greek).lower()
    for ending, replacement in ENDINGS:
        if text.endswith(ending):
            text = text[: -len(ending)] + replacement
            break
    for digraph, replacement in DIGRAPHS:
        text = text.replace(digraph, replacement)
    out = "".join(SINGLES.get(char, char) for char in text)
    return ("h" + out) if rough else out


def fold_latin(text: str) -> str:
    """拉丁字形折疊：I/J、U/V 同字母，ae/oe 折成 e，y 折成 i。"""
    text = strip_accents(text or "").lower()
    text = text.replace("æ", "ae").replace("œ", "oe")
    text = re.sub(r"[^a-z]", "", text)
    text = text.replace("ae", "e").replace("oe", "e")
    return text.replace("j", "i").replace("v", "u").replace("y", "i")


def latin_name_tables(payload: dict) -> list[dict]:
    tables = []
    for half in ("upper", "lower"):
        for table in payload[half].values():
            title = table.get("title") or ""
            if "專名" in title or "人名" in title:
                tables.append(table)
    return tables


def build() -> dict:
    greek = json.loads(GREEK.read_text(encoding="utf-8"))["appendices"][0]["entries"]
    latin_payload = json.loads(LATIN.read_text(encoding="utf-8"))

    # 拉丁側索引：折疊字形 -> 條目。同一折疊有多筆時全部留著，之後只在唯一時採用。
    latin_index: dict[str, list[dict]] = {}
    for table in latin_name_tables(latin_payload):
        for entry in table["entries"]:
            latin_index.setdefault(fold_latin(entry["headword"]), []).append(entry)

    pairs = []
    for entry in greek:
        candidate = fold_latin(to_latin(entry.get("headword") or entry["lemma"]))
        if not candidate:
            continue
        matches = latin_index.get(candidate) or []
        if len(matches) != 1:
            # 一對多就放掉：對不上的比對錯的好。
            continue
        latin_entry = matches[0]
        pairs.append({
            "greek": entry.get("headword") or entry["lemma"],
            "latin": latin_entry["headword"],
            "bridgeForm": candidate,
            "zhProtestant": (entry.get("zh") or "").strip(),
            "zhCatholicSgs": (latin_entry.get("zh") or "").strip(),
            "category": entry.get("category", ""),
            "categoryRoute": entry.get("categoryRoute", ""),
        })
    return {
        "schemaVersion": "1.0.0",
        "note": (
            "希臘文與拉丁文專名的字形對照，以及由此得到的和合本↔思高本譯名對照。"
            "拉丁讀本用思高本、希臘與希伯來用和合本，是既定的命名政策；本表不統一譯名，"
            "只記錄同一個名字在兩套系統裡各叫什麼，並讓分類從希臘側傳到拉丁側。"
            "轉寫規則見 scripts/greek_latin_name_bridge.py；一對多的比對一律放棄。"
        ),
        "pairCount": len(pairs),
        "pairs": pairs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="建希臘↔拉丁專名字形橋")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--show", type=int, default=25)
    args = parser.parse_args()

    payload = build()
    pairs = payload["pairs"]
    both = [p for p in pairs if p["zhProtestant"] and p["zhCatholicSgs"]]
    differ = [p for p in both if p["zhProtestant"] != p["zhCatholicSgs"]]
    typed = [p for p in pairs if p["category"] and p["category"] != "待歸類"]
    print(f"  對上 {len(pairs)} 組；兩邊都有中文 {len(both)}，其中譯名不同 {len(differ)}")
    print(f"  可把分類傳給拉丁的 {len(typed)} 組")
    for pair in differ[: args.show]:
        print(f"      {pair['greek']:<14} {pair['zhProtestant']:<8}↔ "
              f"{pair['latin']:<14} {pair['zhCatholicSgs']:<8} {pair['category']}")

    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n已寫出 {OUTPUT}")
    else:
        print("\n（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
