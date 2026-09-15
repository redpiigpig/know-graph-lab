"""德格版甘珠爾 —— 漢譯對照（東北大學《西藏大藏經總目錄》數位版）。

`title_zh` 一直留空是有原因的：甘珠爾是藏譯，不是漢譯，**沒有「漢文書名」這種東西**。
能填的只有「漢譯對照本」——同一部印度原典另外譯成漢文的那一部經。這個對照關係
不能猜，只能抄目錄。這一輪把來源定下來：

  東北大學 touda.tohoku.ac.jp 的西藏大藏經資料庫，是 1934 年宇井伯壽等編
  《西藏大藏經總目錄》（＝東北目錄、Toh 編號的出處）的官方數位化。每一筆詳目
  的「内容構成」表列出該部的漢譯對照本，並附 **SAT No.＝大正藏經號**。

試過而不能用的三條路（別再試一次）：
  * 84000 data-rdf ── 1,254 個 rdf 檔，**零個漢字**，只有藏／梵／英。
  * rKTs ── 藏文本位，頁面裡沒有 Taishō／南條編號。
  * SuttaCentral parallels ── 德格↔大正藏只有 14 組，落在我們目錄內 13 組。
  * Lancaster《高麗大藏經解題目錄》的東北索引 ── 全藏只標了 391 個 Toh，
    甘珠爾段 313 個（27.8%），是他隨手註的交叉參照，不是系統性對照表。

🚨 **不要抄東北大那一欄的漢文書名。** 它是日本新字體，而且有錯字：
     根本説一切有部…（説≠說）、薬事（薬≠藥）、
     「根本**設**一切有部毘奈耶皮革事」（設≠說）、
     「根本説一切有部毘奈**那**羯恥那衣事」（那≠耶）。
   照抄的話頁面會顯示一個長得很像漢文書名、其實是日文且有錯字的字串，
   而且完全看不出來。正確做法是**只取 SAT 經號**，書名回我們自己的
   CBETA 目錄（catalog.json）拿——那是繁體、是我們站上真的有全文的那一部。

🚨 canon id 不能用 Toh 編號算。id ＝ "1501001" + 7 位流水號，但流水號因為
   後綴本（360a 之類）會跟 Toh 編號錯開：Toh 360→…000361、843→…000844、
   1108→…001109。所以每一頁都要讀出 `TOHOKU-NNNN` 自報的編號來認人，
   不是靠 id 反推。

  python scripts/tripitaka_derge_zh.py --fetch    # 爬詳目（可續跑）
  python scripts/tripitaka_derge_zh.py --build    # 併回 DK.catalog.json
  python scripts/tripitaka_derge_zh.py --audit    # 涵蓋率與異常
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DK = Path("G:/我的雲端硬碟/資料/知識圖工作室/_tripitaka_tibetan")
CATALOG = DK / "DK.catalog.json"
# 🚨 快取放本機不放 Drive。同樣的 1,140 個 46KB 檔，寫 G: 時實測只跑 8 頁／分
#    （請求本身 0.3–1 秒，其餘全耗在 DriveFS 的逐檔同步），寫本機是 40 頁／分。
#    照 repo-hygiene 的判準這本來就是快取：刪掉重跑會一模一樣長回來。
CACHE_DIR = Path(os.environ.get("TOUDA_CACHE", "C:/tmp/touda"))
CBETA_CATALOG = Path(os.environ.get("CBETA_CATALOG", "C:/tmp/cbeta/catalog.json"))

BASE = "https://touda.tohoku.ac.jp/collection/en/database/tibet"
HDRS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    # 少了 Referer／Accept 這個站一律回 403，不是擋爬蟲，是 Drupal 的預設。
    "Referer": BASE + "/collection/derge/canon",
}
DELAY = 1.2
ID_PREFIX = "1501001"
# 甘珠爾是 Toh 1–1108，加上後綴本流水號會往後漂，多掃一點當緩衝。
ID_MAX = 1140

TOHOKU_NO = re.compile(r"TOHOKU-(\d+)([a-z]?)", re.I)
# 「内容構成」表：漢譯對照那一格 ＝ 書名字串 ＋ SAT 連結。
SAT_CELL = re.compile(
    r"<td[^>]*case-sat-link[^>]*>(.*?)</td>", re.S)
SAT_ULN = re.compile(r"satdb2015\.php\?uln=([0-9A-Za-z]+)")


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("\u00ad", "").replace("\u200b", "").replace("\ufeff", "")
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s)).strip()


def die(msg: str) -> None:
    print(f"✗ {msg}")
    raise SystemExit(1)


def works() -> list[dict]:
    if not CATALOG.exists():
        die(f"找不到 {CATALOG}（先跑 tripitaka_derge.py --catalog）")
    return json.loads(CATALOG.read_text(encoding="utf-8"))["works"]


# ─────────────────────────────────────────────────────────────
# 抓
# ─────────────────────────────────────────────────────────────
def get(url: str, tries: int = 4) -> str | None:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if k == tries - 1:
                raise
        except OSError:
            if k == tries - 1:
                raise
        time.sleep(2 * (k + 1))
    return None


def write_atomic(p: Path, text: str) -> None:
    """🚨 直接寫，程序被砍在一半就留下半個檔，續跑會當它已經抓過。"""
    tmp = p.with_suffix(p.suffix + ".part")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)


def fetch() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    got = skip = miss = 0
    for n in range(1, ID_MAX + 1):
        cid = f"{ID_PREFIX}{n:07d}"
        dst = CACHE_DIR / f"{cid}.html"
        if dst.exists():
            skip += 1
            continue
        s = get(f"{BASE}/canon/{cid}")
        if s is None:
            miss += 1
        else:
            write_atomic(dst, s)
            got += 1
        if (got + skip + miss) % 50 == 0:
            print(f"  …{n}/{ID_MAX}　新抓 {got}／已有 {skip}／404 {miss}")
        time.sleep(DELAY)
    print(f"完成：新抓 {got}、已有 {skip}、404 {miss}　→ {CACHE_DIR}")


# ─────────────────────────────────────────────────────────────
# 解析
# ─────────────────────────────────────────────────────────────
def parse(page: str) -> tuple[str | None, list[tuple[str, str]]]:
    """回 (該頁自報的 Toh 編號, [(SAT 經號, 東北大那欄的漢文書名), …])。"""
    m = TOHOKU_NO.search(page)
    if not m:
        return None, []
    toh = str(int(m.group(1))) + (m.group(2) or "")
    out: list[tuple[str, str]] = []
    for cell in SAT_CELL.findall(page):
        uln = SAT_ULN.search(cell)
        if not uln:
            continue
        # 書名是連結前面那段文字；連結本身是「SAT No. 1444」要丟掉。
        title = clean(re.sub(r"<a\b.*?</a>", "", cell, flags=re.S)).strip("（()） ")
        out.append((uln.group(1), title))
    return toh, out


def cbeta_index() -> dict[str, str]:
    """大正藏經號 → 繁體書名。"""
    if not CBETA_CATALOG.exists():
        die(f"找不到 {CBETA_CATALOG}（先跑 tripitaka_cbeta.py --catalog）")
    d = json.loads(CBETA_CATALOG.read_text(encoding="utf-8"))
    idx: dict[str, str] = {}
    for w in d:
        if w.get("canon") != "T":
            continue
        idx[w["id"]] = w["title_zh"]
    return idx


def lookup(idx: dict[str, str], sat: str) -> tuple[str, str] | None:
    """SAT 經號 → (我們的作品 id, 繁體書名)。

    🚨 大正藏 220《大般若經》在 CBETA 被拆成 T0220a…T0220p 十六會，
       查 `T0220` 會落空。落空就退回找同號的第一個分會，取它的書名，
       不要因為查不到就把東北大那個日文字串填進去。
    """
    num = sat.zfill(4) if sat.isdigit() else sat
    wid = f"T{num}"
    if wid in idx:
        return wid, idx[wid]
    alts = sorted(k for k in idx if re.fullmatch(re.escape(wid) + r"[a-z]", k))
    if alts:
        return alts[0], idx[alts[0]]
    return None


# ─────────────────────────────────────────────────────────────
# 併回目錄
# ─────────────────────────────────────────────────────────────
def collect() -> tuple[dict[str, list[tuple[str, str]]], dict]:
    pages = sorted(CACHE_DIR.glob(f"{ID_PREFIX}*.html"))
    if not pages:
        die("快取是空的，先跑 --fetch")
    by_toh: dict[str, list[tuple[str, str]]] = {}
    dup = 0
    for p in pages:
        toh, sats = parse(p.read_text(encoding="utf-8"))
        if toh is None:
            continue
        if toh in by_toh:
            dup += 1
            continue
        by_toh[toh] = sats
    return by_toh, {"pages": len(pages), "dup": dup}


def build(write: bool) -> None:
    ws = works()
    by_toh, meta = collect()
    idx = cbeta_index()

    stat = Counter()
    unmatched: Counter = Counter()
    for w in ws:
        sats = by_toh.get(w["toh"])
        if sats is None:
            stat["目錄查無此 Toh"] += 1
            continue
        if not sats:
            stat["無漢譯對照"] += 1
            w["zh_parallels"] = []
            w["title_zh"] = ""
            w["title_zh_source"] = ""
            continue
        rows = []
        for sat, their in sats:
            hit = lookup(idx, sat)
            if hit is None:
                unmatched[sat] += 1
                continue
            wid, title = hit
            if not any(r["id"] == wid for r in rows):
                rows.append({"id": wid, "t": sat, "title": title,
                             "title_tohoku": their})
        if not rows:
            stat["有 SAT 但我們沒有那部經"] += 1
            w["zh_parallels"] = []
            w["title_zh"] = ""
            w["title_zh_source"] = ""
            continue
        rows.sort(key=lambda r: r["id"])
        w["zh_parallels"] = rows
        w["title_zh"] = rows[0]["title"]
        w["title_zh_source"] = "tohoku-sat"
        stat["單一對照" if len(rows) == 1 else "多部對照"] += 1

    print(f"快取 {meta['pages']:,} 頁，重覆 Toh {meta['dup']}；目錄 {len(ws):,} 部")
    for k, v in stat.most_common():
        print(f"  {k:<22}{v:>6,}")
    filled = sum(1 for w in ws if w.get("title_zh"))
    print(f"\n填得出漢譯對照：{filled:,}／{len(ws):,}（{filled/len(ws)*100:.1f}%）")
    if unmatched:
        print(f"\n⚠️ {len(unmatched)} 個 SAT 經號在我們的大正藏目錄裡查不到"
              f"（多半是卷 56–84，CBETA 未收）：")
        print("   " + "、".join(f"T{k}×{v}" for k, v in unmatched.most_common(20)))

    if not write:
        print("\n（--audit 模式，沒有寫回）")
        return
    doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    doc["works"] = ws
    doc["zh_source"] = "tohoku-touda"
    tmp = CATALOG.with_suffix(".json.part")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(CATALOG)
    print(f"\n已寫回 {CATALOG}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--audit", action="store_true")
    a = ap.parse_args()
    if a.fetch:
        fetch()
    if a.audit:
        build(write=False)
    if a.build:
        build(write=True)
    if not (a.fetch or a.build or a.audit):
        ap.print_help()


if __name__ == "__main__":
    main()
