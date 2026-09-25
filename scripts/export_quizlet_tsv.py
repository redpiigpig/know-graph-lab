"""把印刷單字卡的資料層輸出成 Quizlet 網頁版「匯入」貼上框吃得下的文字檔。

Quizlet 沒有開放 API（2020 年關掉了），只能在網頁版「建立學習集 → 匯入」把文字
貼進去：一行一張卡，正面與背面用 Tab 隔開。這支腳本從 build_flashcards.DECKS 讀同
一份資料，所以匯進 Quizlet 的卡跟印出來的卡一模一樣。

希伯來原本說不出（使用者 Quizlet 上已有一套），同日改口「希伯來的也要建立」，所以全部都出；
匯入哪一副由使用者自己決定，這支只出檔。

用法：python -X utf8 scripts/export_quizlet_tsv.py [--deck grc1 ...]
產物：output/flashcards/quizlet/<deck>.txt，並複製到 Drive 單字卡\Quizlet匯入\。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_flashcards import DECKS, load_cards  # noqa: E402

OUT = ROOT / "output" / "flashcards" / "quizlet"
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\語言\原文讀本\單字卡\Quizlet匯入")
SKIP: set[str] = set()


def skipped(key: str) -> bool:
    return key in SKIP


def back_text(card: dict) -> str:
    parts = []
    if card.get("reading"):
        parts.append(card["reading"])
    parts.append(card["glossZh"])
    if card.get("pos"):
        parts.append(f"（{card['pos']}）")
    parts.append(card.get("footer") or f"第 {card['lesson']} 課")
    return "　".join(parts).replace("\t", " ").replace("\n", " ")


def export(key: str) -> Path:
    deck = DECKS[key]
    cards = load_cards(deck)
    lines = [f"{card['headword'].replace(chr(9), ' ')}\t{back_text(card)}" for card in cards]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{Path(deck['output']).stem}.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {deck['title']}：{len(lines)} 張 → {path.name}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--deck", nargs="*", default=[k for k in DECKS if not skipped(k)])
    args = parser.parse_args()
    paths = [export(key) for key in args.deck if not skipped(key)]
    if DRIVE.parent.exists():
        DRIVE.mkdir(parents=True, exist_ok=True)
        for path in paths:
            shutil.copy2(path, DRIVE / path.name)
        print(f"已複製到 {DRIVE}")


if __name__ == "__main__":
    main()
