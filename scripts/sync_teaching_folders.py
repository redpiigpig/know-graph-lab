"""把教學材料的兩個 Drive 位置對齊：課堂用的 `玄奘\博一上\教學` 與網站鏡射用的
`資料\知識圖工作室\教學`。同一份檔兩邊都要有，內容不同時以**修改時間較新**的那份為準。

    python scripts/sync_teaching_folders.py            # 只比對，不動檔
    python scripts/sync_teaching_folders.py --apply    # 實際複製
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

CLASS_ROOT = Path(r"G:\我的雲端硬碟\玄奘\博一上\教學")
MIRROR_ROOT = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\教學")

# 兩邊的資料夾名不一樣（課堂夾用空格、鏡射夾用底線）
COURSES = [
    ("115-1 世界宗教文化導論", "115-1_世界宗教文化導論"),
    ("115-1 基督宗教概論", "115-1_基督宗教概論"),
    ("115-1 宗教系國文", "115-1_宗教系國文講義"),
]

SKIP = {"desktop.ini", "Thumbs.db", ".DS_Store"}


def files(root: Path) -> dict[Path, Path]:
    if not root.exists():
        return {}
    return {
        p.relative_to(root): p
        for p in root.rglob("*")
        if p.is_file() and p.name not in SKIP
    }


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def copy(src: Path, dst: Path, apply: bool) -> None:
    if apply:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="實際複製（預設只比對）")
    args = ap.parse_args()

    total = {"missing": 0, "newer": 0, "same": 0}
    for class_dir, mirror_dir in COURSES:
        a_root, b_root = CLASS_ROOT / class_dir, MIRROR_ROOT / mirror_dir
        a, b = files(a_root), files(b_root)
        print(f"\n=== {class_dir}  （課堂 {len(a)} 檔／鏡射 {len(b)} 檔）")

        for rel in sorted(a.keys() | b.keys()):
            if rel not in b:
                print(f"  課堂→鏡射  缺檔  {rel}")
                copy(a[rel], b_root / rel, args.apply)
                total["missing"] += 1
            elif rel not in a:
                print(f"  鏡射→課堂  缺檔  {rel}")
                copy(b[rel], a_root / rel, args.apply)
                total["missing"] += 1
            else:
                pa, pb = a[rel], b[rel]
                if pa.stat().st_size == pb.stat().st_size and digest(pa) == digest(pb):
                    total["same"] += 1
                    continue
                newer, older, arrow = (
                    (pa, pb, "課堂→鏡射") if pa.stat().st_mtime > pb.stat().st_mtime
                    else (pb, pa, "鏡射→課堂")
                )
                print(f"  {arrow}  較新  {rel}  ({newer.stat().st_mtime - older.stat().st_mtime:+.0f} 秒)")
                copy(newer, older, args.apply)
                total["newer"] += 1

    verb = "已複製" if args.apply else "待複製"
    print(f"\n{verb}：缺檔 {total['missing']}、版本較舊 {total['newer']}；相同 {total['same']}")


if __name__ == "__main__":
    main()
