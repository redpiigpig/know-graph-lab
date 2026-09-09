#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從 archive.org 抓公有領域的原典／研究到 Drive 電子圖書館，並建 ebooks 列。

給的是清單（WANTED），一筆一本：archive.org 的 identifier、書名、作者、分類。
腳本挑格式（pdf ＞ epub ＞ djvu.txt）、下載到
`G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館/{category}/{subcategory}/`，
再 INSERT 一列 ebooks 指向 Drive 路徑，交給 `parse_worker.py` 解析出全文。

為什麼要有這支：獵表（z-lib）對近代學術專書的命中率不高，但**譜系學方法論的
幾本關鍵著作與東方諸教會的原典對照本，多數已進入公有領域**，archive.org 直接可取，
不必靠獵表。合法、免費、成功率高。

⚠️ 只放確定公有領域的東西。archive.org 上有大量「借閱制」（controlled digital
lending）的現代書，那些抓不到全檔也不該抓——腳本遇到只有 `_meta.xml` 沒有可下載
內文的項目會跳過並回報。

用法：
  python scripts/archive_org_fetch.py --list          # 只列清單與館內是否已有
  python scripts/archive_org_fetch.py --dry-run       # 查每一筆在 archive.org 有哪些檔
  python scripts/archive_org_fetch.py                 # 真的下載並建列
  python scripts/archive_org_fetch.py --only newman   # 只跑 key 含 newman 的
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DRIVE_ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館")
UA = "Mozilla/5.0 (kglab-ingest)"
META = "https://archive.org/metadata/{ident}"
DL = "https://archive.org/download/{ident}/{name}"

# key / archive.org identifier / 書名 / 作者 / 分類 / 子分類 / 為什麼要
WANTED = [
    # ── 譜系學方法論（本書第1章的骨架，館內一本都沒有）
    dict(key="nietzsche-genealogy", ident="genealogyofmoral00nietuoft",
         title="The Genealogy of Morals（論道德的譜系）", author="Friedrich Nietzsche",
         category="哲學", sub="哲學原典",
         why="譜系學一詞的來源；館內有尼采多種但獨缺這一本"),
    dict(key="newman-development", ident="a599872600newmuoft",
         title="An Essay on the Development of Christian Doctrine（論基督教教義的發展）",
         author="John Henry Newman", category="神學", sub="主題專論",
         why="本書第1章第2節的有機體比喻出處；原刊已引用但書不在館內"),
    dict(key="troeltsch-social-1", ident="in.ernet.dli.2015.189046",
         title="The Social Teaching of the Christian Churches, Vol. I",
         author="Ernst Troeltsch", category="宗教學", sub="宗教社會學",
         why="教會／教派類型論；第1章第3節與第5章的分化動力學"),
    dict(key="troeltsch-social-2", ident="in.ernet.dli.2015.238007",
         title="The Social Teaching of the Christian Churches, Vol. II",
         author="Ernst Troeltsch", category="宗教學", sub="宗教社會學",
         why="同上，第二卷"),
    dict(key="niebuhr-social-sources", ident="socialsourcesofd0000nieb_w7z0",
         title="The Social Sources of Denominationalism（宗派主義的社會來源）",
         author="H. Richard Niebuhr", category="宗教學", sub="宗教社會學",
         why="第5章新教裂變的主要分析工具；1929 年出版，美國已入公有領域。"
             "⚠️ 該掃描本可能仍是借閱制，抓不到就要另找 1929 年版"),
]

# Patrologia Orientalis：東方諸教會原典的對照譯本（敘利亞／科普特／亞美尼亞／
# 衣索比亞／阿拉伯語原文＋法譯或拉丁譯）。archive.org 上多卷公有領域。
# 卷次很多，先抓與第4章直接相關的幾卷，之後可再擴。
for _vol, _ident in [
    (4, "patrologiaorien04grafplgo"),
    (13, "patrologia-orientalis-volume-13"),
    (17, "patrologia-orientalis-volume-17"),
]:
    WANTED.append(dict(
        key=f"po-{_vol}", ident=_ident,
        title=f"Patrologia Orientalis, Tome {_vol}",
        author="R. Graffin & F. Nau (eds.)",
        category="世界宗教", sub="基督教/東方教會原典",
        why="東方諸教會原典對照譯本；第4章科普特、敘利亞、亞美尼亞三支的一手材料"))

PREFER = (".pdf", ".epub", "_djvu.txt")


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def pick_file(files: list[dict]) -> tuple[str, str, int] | None:
    """挑一個可下載的內文檔。回傳 (檔名, 副檔名, 位元組)。"""
    best = None
    for ext in PREFER:
        for f in files:
            name = f.get("name", "")
            if not name.lower().endswith(ext):
                continue
            # archive.org 的縮圖／中繼檔不要
            if "_text.pdf" in name or name.endswith("_meta.txt"):
                continue
            size = int(f.get("size") or 0)
            if size < 50_000:          # 太小的多半是目錄或空殼
                continue
            if best is None or size > best[2]:
                best = (name, ".pdf" if ext == ".pdf" else (".epub" if ext == ".epub" else ".txt"), size)
        if best:
            return best
    return None


def download_resumable(url: str, target: Path, expect: int, tries: int = 6) -> bool:
    """邊收邊寫、斷了用 Range 續傳。

    archive.org 的大檔（50-70 MB）在這條線上常常收到一半就斷（IncompleteRead），
    整檔重來只會再斷一次。改成寫到 .part、記錄已收位元組、用 Range 從斷點續，
    收滿 expect 才改名。這也順帶避免把 70 MB 讀進記憶體。
    """
    part = target.with_suffix(target.suffix + ".part")
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, tries + 1):
        have = part.stat().st_size if part.exists() else 0
        if expect and have >= expect:
            break
        headers = {"User-Agent": UA}
        if have:
            headers["Range"] = f"bytes={have}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=180) as r, open(part, "ab") as fh:
                while True:
                    block = r.read(1 << 20)
                    if not block:
                        break
                    fh.write(block)
            got = part.stat().st_size
            print(f"   ↓ {got/1024/1024:.1f} MB（第 {attempt} 次，{time.time()-t0:.0f}s）")
            if not expect or got >= expect:
                break
        except Exception as e:
            got = part.stat().st_size if part.exists() else 0
            print(f"   … 第 {attempt} 次中斷於 {got/1024/1024:.1f} MB：{type(e).__name__}")
            if attempt == tries:
                print("   ✕ 放棄；.part 留著，下次再跑會從斷點續")
                return False
            time.sleep(5 * attempt)
    if expect and part.stat().st_size < expect:
        print(f"   ✕ 收不齊（{part.stat().st_size}/{expect}）")
        return False
    part.replace(target)
    print(f"   ✓ {target}")
    return True


def already_in_library(env, title_fragment: str) -> str | None:
    import requests
    r = requests.get(
        f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
        headers={"apikey": env["SUPABASE_SERVICE_ROLE_KEY"],
                 "Authorization": f'Bearer {env["SUPABASE_SERVICE_ROLE_KEY"]}'},
        params={"select": "id,title", "title": f"ilike.*{title_fragment}*", "limit": "1"},
        timeout=30,
    )
    rows = r.json() if r.status_code == 200 else []
    return rows[0]["title"] if rows else None


def insert_row(env, item: dict, ext: str, path: Path) -> str | None:
    import requests
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.post(
        f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Prefer": "return=representation,resolution=ignore-duplicates",
                 "Content-Type": "application/json"},
        json=[{"title": item["title"], "author": item["author"],
               "file_type": ext.lstrip("."), "category": item["category"],
               "subcategory": item["sub"], "file_path": str(path).replace("/", "\\")}],
        timeout=30,
    )
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0]["id"] if rows else None
    print(f"    [DB] insert HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="只跑 key 含這個字串的")
    args = ap.parse_args()

    env = load_env()
    items = [w for w in WANTED if not args.only or args.only in w["key"]]

    if args.list:
        for w in items:
            probe = w["title"].split("（")[0][:28]
            hit = already_in_library(env, probe)
            print(f'{"已有" if hit else "缺  "} {w["key"]:24s} {w["title"][:46]}')
            if hit:
                print(f'       館內：{hit[:60]}')
            print(f'       用途：{w["why"]}')
        return 0

    ok = skipped = failed = 0
    for w in items:
        print(f'\n── {w["key"]}  {w["title"][:56]}')
        try:
            meta = fetch_json(META.format(ident=w["ident"]))
        except Exception as e:
            print(f"   中繼取不到：{e}")
            failed += 1
            continue
        files = meta.get("files") or []
        if not files:
            print("   ✕ 沒有可下載的檔（多半是借閱制項目）")
            failed += 1
            continue
        pick = pick_file(files)
        if not pick:
            print(f"   ✕ 沒有合用的內文檔（共 {len(files)} 個檔，可能是借閱制）")
            failed += 1
            continue
        name, ext, size = pick
        print(f'   選檔 {name}  {size/1024/1024:.1f} MB')
        if args.dry_run:
            continue

        target = DRIVE_ROOT / w["category"] / w["sub"] / (
            w["title"].split("（")[0].strip().replace("/", "／")[:80] + ext)
        if target.exists() and target.stat().st_size > 50_000:
            print(f"   SKIP 已存在 {target.stat().st_size//1024} KB")
            skipped += 1
            continue
        url = DL.format(ident=w["ident"], name=urllib.parse.quote(name))
        if not download_resumable(url, target, size):
            failed += 1
            continue
        eid = insert_row(env, w, ext, target)
        print(f'   DB {eid or "（未建列，可能已存在）"}')
        ok += 1
        time.sleep(2)

    print(f"\n下載 {ok}／略過 {skipped}／失敗 {failed}")
    if ok:
        print("接著跑 `python scripts/parse_worker.py run` 或等三小時一次的排程解析全文。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
