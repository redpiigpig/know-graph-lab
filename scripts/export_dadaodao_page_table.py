"""Export the verified A5 page map as a human-readable Markdown table."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "scripts/state/dadaodao_pages_a5.json"
OUTPUT = ROOT / "訪談稿_A5頁碼表.md"


def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8-sig"))
    lines = [
        "# 《當代的大愛道革命》訪談稿 A5 頁碼表",
        "",
        "版型：A5（14.8 × 21.0 公分）。封面不編頁碼，目錄使用小寫羅馬數字；三冊訪談正文採連續阿拉伯數字頁碼：第一冊自 1 起、第二冊自 189 起、第三冊自 414 起。下列頁碼是正文顯示頁碼，不是 Word 檔案的物理頁序。",
        "",
        "> 本表為目前定稿版面的引註基準。若再改字級、行距、段距、頁邊或訪談正文，須重新量頁後才可沿用。",
        "",
    ]
    volume_names = {1: "第一冊", 2: "第二冊", 3: "第三冊"}
    docs = {int(name[-6]): totals for name, totals in state["totals"].items()}
    pages = sorted(state["pages"].values(), key=lambda row: (row["vol"], row["start"]))
    for volume in (1, 2, 3):
        totals = docs[volume]
        lines.extend(
            [
                f"## {volume_names[volume]}",
                "",
                f"物理頁數 {totals['physical']} 頁；訪談正文 {totals['body_start']}–{totals['body_last']} 頁。",
                "",
                "| 正文頁碼 | 訪談篇名 |",
                "|---:|---|",
            ]
        )
        for row in pages:
            if row["vol"] == volume:
                lines.append(f"| {row['start']}–{row['end']} | {row['title']} |")
        lines.append("")
    lines.extend(
        [
            "## 第二版引註原則",
            "",
            "- 首次引用寫全稱，例如：「《口述訪談集》第一冊，頁 12」。",
            "- 同一段連續引用可簡寫為：「第一冊，頁 12」。",
            "- 篇章頁碼範圍只能用來定位材料；逐字引文仍須另核定它實際落在其中哪一頁。",
            "- 作者在場的觀察、記憶與感受，應標明為研究者第一人稱敘事，不用訪談內容替作者的心理判斷背書。",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
