#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TRC 下載檔 → 去重 → 命名 → Drive（電子圖書館正本）。

跟 `ingest_new_books.py` 的差別：那支吃「z-lib 頂層的扁平檔名」，靠 Gemini 猜
分類；TRC 這邊每個檔都有完整的站內路徑（`分類/作者/作品/版本/檔名`），書名與
作者直接從路徑回推**不必問 LLM**，而且同一部書常有多個掃描本要先去重。

  python scripts/trc_ingest.py --src z-lib/trc-creeds --map c:/tmp/trc_creeds_map.json \\
         --category 神學 --sub 信條與教理問答 --dry-run
  python scripts/trc_ingest.py ... --run

去重靠內容特徵（PDF 頁數＋首尾頁文字指紋），不靠檔名——TRC 常有
`亞歷山大-赫治-威斯敏斯特信條.pdf` 與 `亞歷山大赫治-威斯敏斯特信條.pdf`
這種同書異名。同一群組保留體積最大者（掃描品質通常最好）。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import to_traditional

DRIVE_ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館")
BAD_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
LATIN_NAME = re.compile(
    r"[A-Z][a-zA-Z.'\-]+(?:\s+(?:of\s+|de\s+|van\s+|von\s+)?[A-Z][a-zA-Z.'\-]+)+")
NOT_PERSON = re.compile(
    r"Confession|Catechism|Standard|Unity|Canon|Declaration|Formula|Creed|Consensus"
    r"|Directory|Government|Collection|Works|Library|Series|Church|Synod|Congregation"
    r"|信條|信綱|信經|準則|問答|要理|教理|合集|文集|全集|叢書|選集|系列", re.IGNORECASE)
# 純編號／代碼型檔名（RT505、123、M1862…）不足以當書名，要往路徑上層找
CODE_NAME = re.compile(r"^(?:[A-Z]{0,3}[\d\-_. ]{2,}|新增.*文檔|新文字文件)$", re.IGNORECASE)


def sig(p: Path) -> tuple:
    """內容特徵：PDF 用頁數＋文字指紋；其餘用體積。"""
    if p.suffix.lower() != ".pdf":
        return (p.suffix.lower(), p.stat().st_size)
    try:
        import fitz
        d = fitz.open(p)
        pages = d.page_count          # 先取，close() 之後就讀不到了
        txt = "".join(d[i].get_text()[:400] for i in
                      list(range(min(3, pages))) + [pages // 2])
        d.close()
        h = hashlib.sha1(txt.encode("utf-8", "ignore")).hexdigest()[:12] if txt.strip() else "noText"
        return ("pdf", pages, h)
    except Exception:
        return ("pdf", p.stat().st_size)


def name_from(trc_path: str, fallback: str) -> tuple[str, str]:
    """TRC 路徑 → (作者, 書名)，全部繁體。"""
    parts = [to_traditional(x) for x in trc_path.strip("/").split("/") if x]
    stem = to_traditional(Path(fallback).stem)
    author = ""
    for seg in reversed(parts[:-1]):
        if LATIN_NAME.search(seg) and not NOT_PERSON.search(seg) \
                and not re.match(r"^\s*\d{3,4}", seg):
            author = re.split(r"[：:]", seg)[0].strip()
            break
    # 檔名是代碼就往上取有意義的資料夾當書名
    title = stem
    if CODE_NAME.match(stem):
        for seg in reversed(parts[:-1]):
            if not re.match(r"^\s*\d{3,4}\s*$", seg) and len(seg) > 3:
                title = seg
                break
    title = clean_title(title, author)
    return author, title


NOISE = re.compile(r"\s*\(\d+\)|\s*\d{3,6}kb|\s*[-_]\s*副本|\s+內頁|\s*[（(]全文[）)]", re.IGNORECASE)


def clean_title(title: str, author: str) -> str:
    """去掉檔名雜訊，並剝掉與作者重複的前綴。

    TRC 的資料夾常是「作者 書名」，檔名又重複一次書名，直接串起來會變成
    「Abraham Hellenbroek 聖言小學的開端，聖言小學的開端 [荷]亞伯拉罕…」。
    """
    t = NOISE.sub("", title).strip(" -—_")
    if author:
        # 標題開頭若就是作者名（或其拉丁部分），剝掉
        for cand in (author, *author.split()):
            if len(cand) > 3 and t.lower().startswith(cand.lower()):
                t = t[len(cand):].strip(" -—_，,：:")
    return t or title


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--map", required=True, help="檔名→TRC 路徑 對照 JSON")
    ap.add_argument("--category", required=True, help="Drive 十大分類，如 神學")
    ap.add_argument("--sub", default="", help="分類下的子資料夾（套書／專題）")
    ap.add_argument("--min-mb", type=float, default=2.0, help="小於此體積視為單篇文本，不進圖書館")
    ap.add_argument("--run", action="store_true", help="實際搬檔（預設 dry-run）")
    a = ap.parse_args()

    src = Path(a.src)
    m = json.loads(Path(a.map).read_text(encoding="utf-8"))
    dest = DRIVE_ROOT / a.category / a.sub if a.sub else DRIVE_ROOT / a.category

    files = [p for p in src.iterdir()
             if p.is_file() and p.stat().st_size >= a.min_mb * 1024 * 1024]
    groups: dict[tuple, list[Path]] = collections.defaultdict(list)
    for p in files:
        groups[sig(p)].append(p)

    plan, dropped = [], []
    for g in groups.values():
        g.sort(key=lambda p: -p.stat().st_size)
        keep = g[0]
        dropped += g[1:]
        author, title = name_from(m.get(keep.name, ""), keep.name)
        fn = f"{author}，{title}{keep.suffix.lower()}" if author else f"{title}{keep.suffix.lower()}"
        fn = BAD_FS.sub("_", fn).strip()
        plan.append([keep, fn])

    # 檔名清理（剝掉 2944kb、(1) 這類尾綴）會讓「內容不同但名字撞在一起」的
    # 掃描本共用同一個目的檔名，其中一本就會被靜默略過。撞名一律補頁數消歧。
    byname: dict[str, list] = collections.defaultdict(list)
    for row in plan:
        byname[row[1]].append(row)
    for fn, rows in byname.items():
        if len(rows) < 2:
            continue
        for row in rows:
            s = sig(row[0])
            mark = f"{s[1]}頁" if s[0] == "pdf" and len(s) > 2 and isinstance(s[1], int) \
                else f"{row[0].stat().st_size // 1024 // 1024}MB"
            stem, ext = fn.rsplit(".", 1)
            row[1] = f"{stem}（{mark}）.{ext}"

    plan = [(s, dest / fn) for s, fn in plan]

    print(f"來源 {len(files)} 檔（≥{a.min_mb}MB）→ 去重後 {len(plan)} 部，捨棄重複 {len(dropped)} 檔")
    print(f"目的地 {dest}\n")
    for s, d in sorted(plan, key=lambda x: x[1].name):
        print(f"  {s.stat().st_size / 1024 / 1024:>7.1f}MB  {d.name[:88]}")
    if dropped:
        print(f"\n重複捨棄：")
        for p in dropped:
            print(f"  {p.name[:80]}")

    if not a.run:
        print("\n(dry-run，未搬檔。加 --run 實際執行)")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    moved = 0
    for s, d in plan:
        if d.exists():
            print(f"  ✓ 已存在：{d.name}")
            continue
        shutil.move(str(s), str(d))
        moved += 1
    print(f"\n已搬 {moved} 部到 {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
