#!/usr/bin/env python
"""把研究產出的「佛學研究」作家 hub JSON 組裝進 stores/collectedWorks.ts。

用法：
    python scripts/cw_assemble_buddhology.py --check     # 只驗證不寫入
    python scripts/cw_assemble_buddhology.py --apply     # 驗證並插入 store

來源：C:/tmp/cw-buddhology/*.json（每檔一個 CwAuthor 陣列）
去處：stores/collectedWorks.ts 的 authors 陣列末端（插在 `  ])` 之前）

🚨 肖像一律自己再 curl 驗一次，不信研究端的自陳——「驗產物不要只驗流程」。
   驗不過的一律改成空字串，靠 emoji 顯示，絕不留破圖。
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SRC = Path("C:/tmp/cw-buddhology")
STORE = Path(__file__).parent.parent / "stores" / "collectedWorks.ts"
CLOSE = "\n  ])\n"

REQUIRED = [
    "slug", "name", "lifespan", "disciplineGroup", "discipline",
    "fields", "color", "emoji", "contribution", "timeline", "works",
]
WORK_REQUIRED = ["title", "yearSort", "category", "status"]
VALID_STATUS = {"done", "in-progress", "planned", "copyright"}
VALID_GROUPS = {"佛學研究", "佛學"}
VALID_REGIONS = {"漢傳", "日本", "西方"}


def portrait_ok(url):
    """實測圖片載不載得動。空字串視為「刻意不放」，直接通過。"""
    if not url:
        return True, "無肖像（emoji）"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ct = r.headers.get("Content-Type", "")
            if r.status == 200 and ct.startswith("image/"):
                return True, ct
            return False, f"HTTP {r.status} / {ct}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)[:80]


def load_all():
    if not SRC.exists():
        sys.exit(f"來源目錄不存在：{SRC}")
    files = sorted(SRC.glob("*.json"))
    if not files:
        sys.exit(f"{SRC} 裡沒有 JSON")
    authors, seen = [], {}
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except ValueError as exc:
            print(f"🚨 {f.name} 不是合法 JSON：{exc}")
            continue
        if not isinstance(data, list):
            data = [data]
        for a in data:
            slug = a.get("slug", "?")
            if slug in seen:
                print(f"🚨 slug 重複：{slug}（{f.name} 與 {seen[slug]}）")
                continue
            seen[slug] = f.name
            a["_src"] = f.name
            authors.append(a)
        print(f"  {f.name}: {len(data)} 位")
    return authors


def validate(authors, existing_slugs):
    bad = []
    for a in authors:
        slug = a.get("slug", "?")
        for k in REQUIRED:
            if not a.get(k):
                bad.append(f"{slug}: 缺 {k}")
        if a.get("disciplineGroup") not in VALID_GROUPS:
            bad.append(f"{slug}: disciplineGroup 不合法（{a.get('disciplineGroup')}）")
        if a.get("region") and a["region"] not in VALID_REGIONS:
            bad.append(f"{slug}: region 不合法（{a['region']}）")
        if slug in existing_slugs:
            bad.append(f"{slug}: store 裡已經有了")
        for w in a.get("works", []):
            for k in WORK_REQUIRED:
                if w.get(k) in (None, ""):
                    bad.append(f"{slug} / {w.get('title', '?')}: 缺 {k}")
            if w.get("status") not in VALID_STATUS:
                bad.append(f"{slug} / {w.get('title', '?')}: status 不合法")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not (args.check or args.apply):
        ap.print_help()
        return

    print("讀取研究產出：")
    authors = load_all()
    store_text = STORE.read_text(encoding="utf-8")
    existing = set(re.findall(r"slug: '([^']+)'", store_text))
    existing |= set(re.findall(r'"slug": "([^"]+)"', store_text))

    print(f"\n共 {len(authors)} 位；store 現有 {len(existing)} 位")

    bad = validate(authors, existing)
    if bad:
        print(f"\n🚨 {len(bad)} 項不合格：")
        for b in bad[:40]:
            print("   " + b)
        if len(bad) > 40:
            print(f"   …另有 {len(bad) - 40} 項")
        sys.exit(1)

    print("\n肖像實測：")
    fixed = 0
    for a in authors:
        ok, why = portrait_ok(a.get("portraitUrl", ""))
        mark = "✓" if ok else "✗"
        print(f"  {mark} {a['name']}　{why}")
        if not ok:
            a["portraitUrl"] = ""
            a.pop("portraitCredit", None)
            fixed += 1
    if fixed:
        print(f"  → {fixed} 張載不動，已改為空字串（改用 emoji）")

    by_region = {}
    for a in authors:
        by_region.setdefault(a.get("region", "（無）"), []).append(a["name"])
    print("\n分區：")
    for r, names in by_region.items():
        print(f"  {r}（{len(names)}）：{'、'.join(names)}")

    works = sum(len(a["works"]) for a in authors)
    print(f"\n著作目錄合計 {works} 筆")

    if args.check:
        print("\n--check：未寫入。確認無誤後跑 --apply。")
        return

    for a in authors:
        a.pop("_src", None)
    block = ""
    for a in authors:
        body = json.dumps(a, ensure_ascii=False, indent=2)
        body = "\n".join("    " + ln for ln in body.splitlines())
        block += body + ",\n\n"

    idx = store_text.rindex(CLOSE)
    out = store_text[:idx] + "\n\n" + block.rstrip() + "\n" + store_text[idx:]
    STORE.write_text(out, encoding="utf-8")
    print(f"\n已插入 {len(authors)} 位到 {STORE}")


if __name__ == "__main__":
    main()
