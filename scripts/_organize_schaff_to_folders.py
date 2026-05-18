"""把 Schaff 教父集 38 卷的 .epub 檔從宗教學/ 移到 3 個系列子資料夾，並同步更新 DB file_path。

執行：python scripts/_organize_schaff_to_folders.py [--dry-run]

子資料夾命名：
- 宗教學/Schaff - Ante-Nicene Fathers (10 vols)/
- 宗教學/Schaff - Nicene and Post-Nicene Fathers Series 1 (Augustine and Chrysostom)/
- 宗教學/Schaff - Nicene and Post-Nicene Fathers Series 2 (14 vols)/
"""
import os
import sys
import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import requests

sys.stdout.reconfigure(encoding="utf-8")

DRY_RUN = "--dry-run" in sys.argv

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

DRIVE_ROOT = Path(r"G:\我的雲端硬碟\資料\電子書")
CATEGORY = "宗教學"

SUBFOLDER_ANF = "Schaff - Ante-Nicene Fathers (10 vols)"
SUBFOLDER_NPNF1 = "Schaff - Nicene and Post-Nicene Fathers Series 1 (Augustine and Chrysostom)"
SUBFOLDER_NPNF2 = "Schaff - Nicene and Post-Nicene Fathers Series 2 (14 vols)"


def pick_subfolder(title: str) -> str | None:
    if "NPNF1" in title:
        return SUBFOLDER_NPNF1
    if "NPNF2" in title:
        return SUBFOLDER_NPNF2
    if "ANF" in title:
        return SUBFOLDER_ANF
    return None


def main():
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/ebooks?select=id,title,file_path,subcategory&or=(title.ilike.*NPNF1*,title.ilike.*NPNF2*,title.ilike.*ANF*)",
        headers=H,
    )
    rows = r.json()
    print(f"Found {len(rows)} Schaff ebooks in DB")
    print(f"DRY_RUN = {DRY_RUN}\n")

    # 先確保 3 個子資料夾存在
    for sub in [SUBFOLDER_ANF, SUBFOLDER_NPNF1, SUBFOLDER_NPNF2]:
        target_dir = DRIVE_ROOT / CATEGORY / sub
        if not target_dir.exists():
            print(f"  mkdir: {target_dir}")
            if not DRY_RUN:
                target_dir.mkdir(parents=True, exist_ok=True)

    moved, skipped, fail = 0, 0, 0
    for row in rows:
        title = row["title"]
        old_path = Path(row["file_path"])
        sub = pick_subfolder(title)
        if not sub:
            print(f"  ❌ no subfolder match: {title[:60]}")
            fail += 1
            continue

        new_path = DRIVE_ROOT / CATEGORY / sub / old_path.name

        if old_path == new_path:
            print(f"  - already in place: {title[:60]}")
            skipped += 1
            continue

        if not old_path.exists():
            # 可能已經移過了 — 看 new_path 在不在
            if new_path.exists():
                print(f"  ↻ already moved, just sync DB: {title[:60]}")
                if not DRY_RUN:
                    patch = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{row['id']}",
                        headers={**H, "Content-Type": "application/json"},
                        json={"file_path": str(new_path), "subcategory": sub},
                    )
                    if patch.status_code in (200, 204):
                        moved += 1
                    else:
                        print(f"    DB patch failed: {patch.status_code}")
                        fail += 1
                else:
                    moved += 1
                continue
            print(f"  ❌ source not found: {old_path}")
            fail += 1
            continue

        # Move file + UPDATE DB
        print(f"  → [{sub[:30]}] {old_path.name[:60]}")
        if not DRY_RUN:
            try:
                shutil.move(str(old_path), str(new_path))
            except Exception as e:
                print(f"    move failed: {e}")
                fail += 1
                continue
            patch = requests.patch(
                f"{SUPABASE_URL}/rest/v1/ebooks?id=eq.{row['id']}",
                headers={**H, "Content-Type": "application/json"},
                json={"file_path": str(new_path), "subcategory": sub},
            )
            if patch.status_code in (200, 204):
                moved += 1
            else:
                print(f"    DB patch failed: {patch.status_code}, rolling back move...")
                shutil.move(str(new_path), str(old_path))
                fail += 1
        else:
            moved += 1

    print(f"\n=== Done: moved={moved}, skipped={skipped}, fail={fail} ===")


if __name__ == "__main__":
    main()
