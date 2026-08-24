#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRC 檔案清單 → 作品層級彙整 → 大藏經分類器輸入 records。

TRC（thereformedcatholic.org）的樹是 `分類/作者/作品/[版本]/檔案`，同一部作品
常有多個檔（原版 ORIGINAL、各家譯本、不同格式）。直接把「檔」當「書」會把一部
作品灌成好幾筆，所以這支先把檔收斂成**作品**，再吐分類器要的 record。

  python scripts/trc_records.py --report            # 作品層級統計
  python scripts/trc_records.py --out c:/tmp/trc_records.json
  python scripts/trc_records.py --report --category 初代教會

所有中文欄位（title_zh / author / note）出去前都過 opencc s2tw + TRAD_FIXES
（[[feedback_traditional_chinese_only]]）——TRC 幾乎整批簡體。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import to_traditional  # opencc s2tw + TRAD_FIXES

CATALOG = Path("c:/tmp/trc_catalog.json")
SITE = "https://thereformedcatholic.org/download"

# 目錄名若整個命中，代表它是「同一部作品的某個版本」而不是獨立作品，
# 歸群時要往上退一層。
VERSION_RX = re.compile(
    r"^(原版|原著|原文)?\s*(ORIGINAL|Original)?\s*$"
    r"|原版|ORIGINAL"
    r"|[譯译][本版]|[譯译]$"
    r"|繁體|繁体|簡體|简体|中文版|英文版|中英"
    r"|掃描|扫描|[電电]子版|重排|排版|校[訂订]"
    r"|^(PDF|EPUB|MOBI|TXT|DOC[X]?)$",
    re.IGNORECASE,
)

# 作者資料夾長這樣：「鍾馬田 David Martyn Lloyd-Jones」「馬太米德 Matthew Mead」
# ——中文名後面接兩個以上大寫開頭的拉丁字。
LATIN_NAME_RX = re.compile(r"[A-Z][a-zA-Z.'\-]+(?:\s+(?:of\s+|de\s+|van\s+|von\s+)?[A-Z][a-zA-Z.'\-]+)+")

EBOOK_EXTS = {"pdf", "epub", "mobi", "azw3", "azw", "doc", "docx", "txt", "chm"}


def load(path: Path = CATALOG) -> list[dict]:
    if not path.exists():
        sys.exit(f"找不到 {path}——先跑 python scripts/trc_catalog.py")
    return json.loads(path.read_text(encoding="utf-8"))


# 文獻群／合集的招牌字：命中就不是人名，是一份文件或一套叢書。
NOT_PERSON_RX = re.compile(
    r"Confession|Catechism|Standard|Unity|Canon|Declaration|Formula|Creed|Consensus"
    r"|Directory|Government|Collection|Works|Library|Series|Church|Synod|Congregation"
    r"|Testament|Bible|Scripture|Institute|Theology|Doctrine|Commentary"
    r"|信條|信綱|信經|準則|問答|要理|教理|合集|文集|全集|叢書|選集|系列",
    re.IGNORECASE,
)


def is_author_dir(name: str) -> bool:
    """level-2 目錄是不是作者名。

    只有「看起來像人名」才算：有拉丁人名、不以年份開頭（`1619 三項聯合信綱…`）、
    且不含文獻群招牌字（`Three Forms of Unity` / `Westminster Standards` 這類
    會誤中純拉丁名規則）。
    """
    if re.match(r"^\s*\d{3,4}", name):
        return False
    if NOT_PERSON_RX.search(name):
        return False
    return bool(LATIN_NAME_RX.search(name))


def work_key(parts: list[str]) -> list[str]:
    """把檔案路徑（不含檔名）收斂到「作品」那一層：剝掉尾端的版本目錄。"""
    out = list(parts)
    while len(out) > 2 and VERSION_RX.search(out[-1]):
        out.pop()
    return out


def group(files: list[dict]) -> dict[tuple, dict]:
    """檔 → 作品。回傳 {work_key_tuple: work_dict}。"""
    works: dict[tuple, dict] = {}
    for f in files:
        parts = [p for p in f["path"].strip("/").split("/") if p]
        if len(parts) < 2:
            continue  # 根目錄散檔（README 等）
        dirs = work_key(parts[:-1])
        key = tuple(dirs)
        w = works.setdefault(key, {
            "category": dirs[0],
            "author_dir": dirs[1] if len(dirs) >= 3 and is_author_dir(dirs[1]) else "",
            "work_dir": dirs[-1],
            "path": "/" + "/".join(dirs),
            "depth": len(dirs),
            "files": [],
            "size": 0,
        })
        w["files"].append(f)
        w["size"] += f.get("size") or 0
    return works


def split_zh_en(name: str) -> tuple[str, str]:
    """「靈性低潮 Spiritual Depression」→ ('靈性低潮', 'Spiritual Depression')。"""
    m = LATIN_NAME_RX.search(name)
    if not m:
        # 單一個大寫拉丁字也算（如 "Institutes"）
        m2 = re.search(r"[A-Za-z][A-Za-z.'\-]{2,}(?:\s+[A-Za-z.'\-]+)*\s*$", name)
        if m2 and re.search(r"[\u4e00-\u9fff]", name[:m2.start()]):
            return name[:m2.start()].strip(" -—:："), m2.group(0).strip()
        return name.strip(), ""
    return name[:m.start()].strip(" -—:："), m.group(0).strip()


def to_record(w: dict) -> dict:
    """作品 → 大藏經分類器 record（比照既有 ledger 的 source_record 形狀）。"""
    title_raw, title_en = split_zh_en(w["work_dir"])
    author_zh, author_en = split_zh_en(w["author_dir"]) if w["author_dir"] else ("", "")
    author = " ".join(x for x in (to_traditional(author_zh), author_en) if x).strip()
    exts = sorted({f["ext"] for f in w["files"] if f["ext"]})
    return {
        "source": "trc",
        "query": to_traditional(w["path"]),
        "title": title_en or to_traditional(title_raw),
        "title_zh_raw": to_traditional(title_raw),
        "author": author,
        "date": "",
        "language": "chinese",
        "subjects": [to_traditional(w["category"])],
        "url": SITE + w["path"],
        "raw_id": w["path"],
        "note": to_traditional(
            f"TRC 藏本，{len(w['files'])} 檔（{'/'.join(exts) or '無副檔名'}），"
            f"{w['size'] / 1024 / 1024:.1f} MB"
        ),
        "classification_status": "unclassified",
    }


def report(works: dict[tuple, dict], files: list[dict]) -> None:
    total_size = sum(w["size"] for w in works.values())
    print(f"檔案 {len(files)} 個 → 收斂為作品 {len(works)} 部，合計 "
          f"{total_size / 1024 ** 3:.1f} GB\n")

    by_cat_w: Counter = Counter()
    by_cat_f: Counter = Counter()
    by_cat_s: Counter = Counter()
    authors: dict[str, set] = defaultdict(set)
    for w in works.values():
        c = to_traditional(w["category"])
        by_cat_w[c] += 1
        by_cat_f[c] += len(w["files"])
        by_cat_s[c] += w["size"]
        if w["author_dir"]:
            authors[c].add(w["author_dir"])

    print(f"{'分類':<30}{'作品':>6}{'檔':>7}{'作者':>6}{'GB':>9}")
    for c, n in by_cat_w.most_common():
        print(f"  {c[:28]:<28}{n:>6}{by_cat_f[c]:>7}{len(authors[c]):>6}{by_cat_s[c] / 1024 ** 3:>9.2f}")

    multi = [w for w in works.values() if len(w["files"]) > 1]
    print(f"\n多檔（多版本／多格式）作品：{len(multi)} 部")
    big = sorted(works.values(), key=lambda w: -w["size"])[:15]
    print(f"\n最大 15 部作品：")
    for w in big:
        print(f"  {w['size'] / 1024 ** 3:>7.2f} GB  {to_traditional(w['path'])[:90]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", help="寫出分類器 records JSON")
    ap.add_argument("--category", help="只取某個分類（前綴比對，簡繁皆可）")
    ap.add_argument("--max-mb", type=float, help="只取單部總體積 <= N MB 的作品")
    a = ap.parse_args()

    files = load()
    works = group(files)

    if a.category:
        want = to_traditional(a.category)
        works = {k: w for k, w in works.items()
                 if to_traditional(w["category"]).startswith(want)}
    if a.max_mb:
        works = {k: w for k, w in works.items() if w["size"] <= a.max_mb * 1024 * 1024}

    if a.report or not a.out:
        report(works, files)
    if a.out:
        recs = [to_record(w) for w in sorted(works.values(), key=lambda w: w["path"])]
        Path(a.out).write_text(json.dumps({"records": recs}, ensure_ascii=False, indent=1),
                               encoding="utf-8")
        print(f"\n已寫 {a.out}（{len(recs)} 筆）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
