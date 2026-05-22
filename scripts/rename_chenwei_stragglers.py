#!/usr/bin/env python3
"""
針對 chenwei audit 2026-05-21 發現的 3 個未 rename 子資料夾，繞過 1.5+ 小時整 chenwei plan walk。

跑 plan/execute 對應：
  plan    → 顯示三資料夾預計 rename mapping，寫 report
  execute → 依 report 兩階段 rename（reuse rename_photos.cmd_execute 的 phase1+phase2 邏輯）
"""
import json
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import rename_photos as RP

ROOT = RP.PHOTOS_PARENT / RP.LIBRARIES["chenwei"]
TARGETS = [
    ROOT / "2019相片" / "法國照片" / "劭瑋手機相片",
    ROOT / "2019相片" / "法國照片" / "相機相片",
    ROOT / "2016相片" / "03.19石門區心靈之旅" / "新增資料夾",
]

REPORT_PATH = Path(__file__).parent / "photo_rename_report_chenwei_stragglers.json"


def cmd_plan():
    print(f"HEIC EXIF support: {'YES' if RP.HEIF_OK else 'NO'}")
    all_plan = []
    for folder in TARGETS:
        print(f"\n=== {folder} ===")
        if not folder.exists():
            print("  !! 不存在")
            continue
        prefix = RP.folder_prefix(folder.name)
        plan = RP.collect_folder_plan(folder, prefix)
        for item in plan:
            item["folder"] = str(folder).replace("\\", "/")
            item["folder_name"] = folder.name
            item["prefix"] = prefix
        will = [x for x in plan if not x["skip"]]
        sources = {}
        for x in plan:
            sources[x["dt_source"]] = sources.get(x["dt_source"], 0) + 1
        print(f"  total: {len(plan)}, will_rename: {len(will)}, dt_source: {sources}")
        if will:
            print("  examples:")
            for x in will[:3] + (will[-1:] if len(will) > 3 else []):
                print(f"    {Path(x['src']).name}  →  {x['target_name']}  ({x['dt_source']})")
        all_plan.extend(plan)

    summary = {
        "total": len(all_plan),
        "will_rename": sum(1 for x in all_plan if not x["skip"]),
    }
    REPORT_PATH.write_text(
        json.dumps({"plan": all_plan, "summary": summary}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nReport: {REPORT_PATH}")
    print(f"Summary: {summary}")


def cmd_execute():
    if not REPORT_PATH.exists():
        print(f"先跑 plan：{REPORT_PATH} 不存在")
        sys.exit(1)
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    plan = [x for x in data["plan"] if not x["skip"]]
    if not plan:
        print("沒有需要 rename 的檔案")
        return
    print(f"執行 {len(plan)} 個 rename…")

    by_folder: dict[str, list[dict]] = {}
    for item in plan:
        by_folder.setdefault(item["folder"], []).append(item)

    RP.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    renamed = skipped = errors = 0
    with RP.LOG_PATH.open("a", encoding="utf-8") as log:
        for folder_str, items in by_folder.items():
            folder = Path(folder_str)
            tmp_map = []
            for i, item in enumerate(items):
                src = Path(item["src"])
                if not src.exists():
                    skipped += 1
                    continue
                tmp = folder / f"{RP.TMP_PREFIX}{i:05d}{RP.normalize_ext(src.suffix)}"
                try:
                    src.rename(tmp)
                    tmp_map.append((tmp, item["target_name"], src.name))
                except Exception as e:
                    print(f"ERR phase1 {src}: {e}")
                    errors += 1
            for tmp, target_name, orig_name in tmp_map:
                tgt = folder / target_name
                if tgt.exists():
                    stem, suf = tgt.stem, tgt.suffix
                    j = 2
                    while True:
                        cand = folder / f"{stem}_dup{j}{suf}"
                        if not cand.exists():
                            tgt = cand
                            break
                        j += 1
                try:
                    tmp.rename(tgt)
                    log.write(json.dumps({
                        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "folder": folder_str,
                        "from": orig_name,
                        "to": tgt.name,
                    }, ensure_ascii=False) + "\n")
                    renamed += 1
                except Exception as e:
                    print(f"ERR phase2 {tmp}: {e}")
                    errors += 1
    print(f"\nRename 完成：renamed={renamed} skipped={skipped} errors={errors}")


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        cmd_plan()
    elif cmd == "execute":
        cmd_execute()
    else:
        print(f"unknown cmd: {cmd}")
        sys.exit(1)
