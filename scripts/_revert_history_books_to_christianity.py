"""把上一輪錯放到 神學 的「教會史／基督教史／傳記」類書，移回 世界宗教/基督教。

User 規則：
- 基督教史／教會史／傳記 → 世界宗教/基督教
- 神學只收：系統神學、教父原典（Schaff 等英譯）、神學論述、教義研究
"""
import os
import sys
import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import requests

sys.stdout.reconfigure(encoding="utf-8")

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
DRIVE_ROOT = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館")

APPLY = "--apply" in sys.argv

# Move these from 神學 → 世界宗教/基督教
TITLES_TO_REVERT = [
    "Historia ecclesiastica",
    "Historia Ecclesiastica - Critical Edition 2008",
    "The Sacred Writings of Socrates Scholasticus",
    "新版宗教史叢書_基督教史",
    "The Battle for Bonhoeffer",
    "Dietrich Bonhoeffer A Biography - Theologian, Christian, Man for His Times",
]


def main():
    moved, fail = 0, 0
    for title in TITLES_TO_REVERT:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ebooks?title=eq.{title}&select=id,title,file_path,category,subcategory",
            headers=H,
        )
        rows = r.json()
        if not rows:
            print(f"  ⚠ not found: {title}")
            fail += 1
            continue
        for row in rows:
            old_path = Path(row["file_path"])
            new_path = DRIVE_ROOT / "世界宗教" / old_path.name
            if row["category"] == "世界宗教":
                print(f"  - already in 世界宗教: {title[:50]}")
                continue
            # 子類：教會史 OR 基督教傳記
            if "Bonhoeffer" in title:
                new_sub = "基督教"  # 神學家傳記也歸 基督教 sub
            elif "Historia" in title or "Socrates Scholasticus" in title:
                new_sub = "基督教"
            elif "基督教史" in title:
                new_sub = "基督教"
            else:
                new_sub = "基督教"
            print(f"  ↻ {title[:60]} → 世界宗教/{new_sub}")
            if APPLY:
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
                    json={"category": "世界宗教", "subcategory": new_sub, "file_path": str(new_path)},
                )
                if patch.status_code in (200, 204):
                    moved += 1
                else:
                    print(f"    DB patch failed: {patch.status_code}")
                    fail += 1
            else:
                moved += 1
    print(f"\n=== Done: moved={moved}, fail={fail} (DRY_RUN={not APPLY}) ===")


if __name__ == "__main__":
    main()
