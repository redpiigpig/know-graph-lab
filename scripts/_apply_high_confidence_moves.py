"""High-confidence 跨類移動。每本明確說明 reason，不靠 regex 一鍋抓。

執行：python scripts/_apply_high_confidence_moves.py --apply
"""
import os
import sys
import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import requests

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
DRIVE_ROOT = Path(r"G:\我的雲端硬碟\資料\電子書")

# (title 完整 match, target_cat, target_sub, reason)
MOVES = [
    # ── 世界宗教 → 神學 — 系統神學/教父原典 ──
    ("教父", "神學", "教父原典", "教父原典文本，標題即「教父」"),
    ("基督教神學", "神學", "系統神學", "系統神學專書"),
    ("基督教神學導論", "神學", "系統神學", "系統神學導論"),
    ("使徒教父著作", "神學", "教父原典", "使徒教父原典英譯"),
    # ── 世界宗教 → 哲學 — 哲學分析 of 神學／宗教概念 ──
    ("論埃及神學與哲學", "哲學", "古代哲學", "古埃及哲學專書"),
    ("砍去自然神論頭顱的大刀──康德《純粹理性批判》導讀", "哲學", "近代哲學", "康德純粹理性批判導讀"),
    ("印度哲學祛魅", "哲學", "東方哲學", "印度哲學學術研究"),
    ("古印度六派哲學經典", "哲學", "東方哲學", "印度哲學原典"),
    ("儒家的心性學與道德形上學", "哲學", "中國思想史", "儒家哲學形上學"),
    ("海德格爾與神學", "哲學", "近代哲學", "海德格爾哲學"),
    ("康德、費希特和青年黑格爾論倫理神學", "哲學", "近代哲學", "康德/費希特/黑格爾哲學"),
    ("康德的理性神學", "哲學", "近代哲學", "康德哲學"),
    ("柏拉圖的神學", "哲學", "古希臘哲學", "柏拉圖哲學"),
    ("基督教的柏拉圖主義", "哲學", "古希臘哲學", "柏拉圖主義哲學分析"),
    # ── 自然科學 → 哲學 — 純科學哲學 ──
    ("科學哲學的歷史導論", "哲學", "近代哲學", "科學哲學經典導論"),
    # ── 世界宗教 → 社會政治學 — Weber 社會學經典 ──
    ("猶太人與現代資本主義", "社會政治學", "政治經濟社會學", "Sombart 經典社會學"),
    ("新教倫理與資本主義精神（新版）", "社會政治學", "政治經濟社會學", "Weber 經典社會學"),
    # ── 世界宗教 → 宗教學 — 跨宗教學術研究 ──
    ("古希臘的神話與宗教", "宗教學", "神話學", "古希臘神話學術研究"),
]


def main():
    moved, fail, not_found = 0, 0, 0
    for title, target_cat, target_sub, reason in MOVES:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ebooks?title=eq.{title}&select=id,title,file_path,category,subcategory",
            headers=H,
        )
        rows = r.json()
        if not rows:
            print(f"  ⚠ NOT FOUND: {title}  [{reason}]")
            not_found += 1
            continue
        for row in rows:
            old_path = Path(row["file_path"])
            new_path = DRIVE_ROOT / target_cat / old_path.name
            if row["category"] == target_cat and row["subcategory"] == target_sub:
                print(f"  - already in place: {title[:50]}")
                continue
            print(f"  ↻ {title[:55]:57s}  {row['category']}/{row.get('subcategory')} → {target_cat}/{target_sub}  [{reason}]")
            if not APPLY:
                continue
            if old_path.exists() and old_path != new_path:
                try:
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old_path), str(new_path))
                except Exception as e:
                    print(f"    move failed: {e}")
                    fail += 1
                    continue
            patch = requests.patch(
                f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{row['id']}",
                headers={**H, "Content-Type": "application/json"},
                json={"category": target_cat, "subcategory": target_sub, "file_path": str(new_path)},
            )
            if patch.status_code in (200, 204):
                moved += 1
            else:
                print(f"    DB patch failed: {patch.status_code}")
                fail += 1

    print(f"\n=== Done: moved={moved}, fail={fail}, not_found={not_found} (DRY_RUN={not APPLY}) ===")


if __name__ == "__main__":
    main()
