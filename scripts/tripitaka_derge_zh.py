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
# 對帳閘門檻：我們的書名有幾成的字要出現在東北大那格的書名裡。
COVER_MIN = 0.5

# 已查證的上游錯誤：東北大自己把經號標錯的，逐筆排除並寫明證據。
# 只放「確定錯」的，不放「看起來怪」的——後者由對帳閘報出來供人判讀。
UPSTREAM_WRONG = {
    # Toh 119 ＝ 聖大般涅槃經（藏 འཕགས་པ་ཡོངས་སུ་མྱ་ངན་ལས་འདས་པ་ཆེན་པོའི་མདོ），
    # 東北大那格書名也寫「大般涅槃経（巻第一…巻第四十，後分二巻）」，
    # SAT 卻掛 0874 ＝《金剛頂一切如來真實攝大乘現證大教王經》，一部密續。
    # 多半是 0374 打成 0874。正確經號無從由本資料推定，留空不臆造。
    ("119", "T0874"),
}

TOHOKU_NO = re.compile(r"TOHOKU-(\d+)([A-Za-z]?)")
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
_JP2T = None


def jp2t(s: str) -> str:
    """日本新字體 → 繁體。只給對帳閘用，不當書名。

    東北大那一欄是日本新字體（経／厳／説／薬），要跟我們的繁體書名比對，
    得先拉到同一套字形上，否則《大方廣佛華嚴經》對《大方廣佛華厳経》
    會被算成三個字不一樣。
    """
    global _JP2T
    if _JP2T is None:
        import opencc
        _JP2T = opencc.OpenCC("jp2t")
    return _JP2T.convert(s)


def parse(page: str) -> tuple[str | None, list[tuple[list[str], str]]]:
    """回 (該頁自報的 Toh 編號, [SAT 經號, …])。

    🚨 一格裡可以有不只一個 SAT 連結，而且**多個漢文書名是直接黏在一起的**，
       中間沒有任何分隔符。Toh 44 那一格就是
       「大方廣佛華厳経［八十華厳］（巻第一…巻第八十）普賢菩薩行願讃」
       後面接兩個連結 (SAT 0278), (SAT 0297)——兩部經兩個書名黏成一串。
       用 `.search()` 只取第一個連結的話，Toh 44 會少掉 T0297、Toh 176 會
       從三部縮成一部，而目錄照樣有值、看起來完全正常。所以要 `finditer`。
       書名一律不取（見檔頭），黏不黏得開都不影響。

    🚨 後綴本的大小寫兩邊不一樣：我們的目錄寫 `359a`，東北大寫 `359A`。
       不統一的話那一部永遠對不到。
    """
    m = TOHOKU_NO.search(page)
    if not m:
        return None, []
    toh = str(int(m.group(1))) + (m.group(2) or "").lower()
    out: list[tuple[list[str], str]] = []
    for cell in SAT_CELL.findall(page):
        sats = [u.group(1) for u in SAT_ULN.finditer(cell)]
        if not sats:
            continue
        # 書名文字（把「SAT No. N」那幾個連結剝掉）。只餵對帳閘，不當書名。
        out.append((sats, jp2t(clean(re.sub(r"<a\b.*?</a>", "", cell, flags=re.S)))))
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


RANGE_TAIL = re.compile(r"\(第\d+卷-第\d+卷\)\s*$")


def lookup(idx: dict[str, str], sat: str, blob: str = "") -> tuple[str, str] | None:
    """SAT 經號 → (我們的作品 id, 繁體書名)。

    🚨 同一個大正藏經號在 CBETA 可能被拆成幾個分卷，查 `T0220` 會落空：
       般若部用小寫（T0220a…T0220p 十六會），密教部用大寫
       （T1005A／B、T0974A…F）。只認小寫的話，密教部那 7 個經號全部落空。
       落空要退回找同號的分卷，但**分卷有兩種，不能一律取第一個**：

       (a) 真的是不同的經，只是共用一個大正藏號——T1005A《大寶廣博樓閣善住
           祕密陀羅尼經》與 T1005B《寶樓閣經梵字真言》、T0974A–F 六種
           佛頂尊勝陀羅尼。這種要拿東北大那格的書名去比，挑對的那一部。
       (b) 只是 CBETA 按檔案卷段切開，書名根本一樣——T0220a–p 全部叫
           「大般若波羅蜜多經(第401卷-第600卷)」之類。這種取第一個的話，
           Toh 8／9／10／12…十二部不同的般若經會全部顯示成
           「大般若波羅蜜多經(第1卷-第200卷)」，而 Toh 10 其實是第三會。
           所以這種要把卷段括號拿掉，回傳不帶卷段的本名。
    """
    num = sat.zfill(4) if sat.isdigit() else sat
    wid = f"T{num}"
    if wid in idx:
        return wid, idx[wid]
    alts = sorted(k for k in idx if re.fullmatch(re.escape(wid) + r"[A-Za-z]", k))
    if not alts:
        return None
    bases = {RANGE_TAIL.sub("", idx[k]) for k in alts}
    if len(bases) == 1:                       # (b) 分卷只是檔案切法
        return wid, bases.pop()
    best = max(alts, key=lambda k: covered(idx[k], blob))   # (a) 不同的經
    return best, idx[best]


# ─────────────────────────────────────────────────────────────
# 併回目錄
# ─────────────────────────────────────────────────────────────
def collect() -> tuple[dict[str, list[tuple[list[str], str]]], dict]:
    pages = sorted(CACHE_DIR.glob(f"{ID_PREFIX}*.html"))
    if not pages:
        die("快取是空的，先跑 --fetch")
    by_toh: dict[str, list[tuple[list[str], str]]] = {}
    dup = 0
    for p in pages:
        toh, cells = parse(p.read_text(encoding="utf-8"))
        if toh is None:
            continue
        if toh in by_toh:
            dup += 1
            continue
        by_toh[toh] = cells
    return by_toh, {"pages": len(pages), "dup": dup}


def covered(title: str, blob: str) -> float:
    """我們這個書名，有幾成的字出現在東北大那一格的書名字串裡。

    🚨 為什麼需要這一關：東北大自己會標錯經號。Toh 119 那一格書名寫
       「大般涅槃経」，SAT 卻掛 0874（＝《金剛頂一切如來真實攝大乘現證
       大教王經》，一部密續），多半是 0374 打成 0874。照收的話，涅槃經
       底下會冒出一部金剛頂經，而頁面上完全看不出異常。
       兩邊書名都是漢字，字形差異用 jp2t 抹平之後就能互相對帳。
    ⚠️ 只能用在「一格只掛一個 SAT」的情況。東北大一格裡列了 N 個 SAT 時
       **只寫一個代表性書名**（「維摩詰所說經 (), (), ()」＝三個連結一個
       書名），逐名比對必然失敗——實測 50% 門檻擋下 37 筆，其中 36 筆是對的，
       只有 Toh 119 是真錯。而且它那一欄本身有系統性錯字（寶→賓：
       「大賓積經」「廣大賓棲閣」；音→昔：「觀世昔菩薩」；礙→凝：「無凝」），
       所以這一關只用來抓「整個對錯人」，不拿來挑字。
    """
    t = re.sub(r"[^一-鿿]", "", title)
    if not t:
        return 0.0
    return sum(1 for ch in t if ch in blob) / len(t)


def build(write: bool) -> None:
    ws = works()
    by_toh, meta = collect()
    idx = cbeta_index()

    stat = Counter()
    unmatched: Counter = Counter()
    suspect: list[tuple[str, str, str, float, str]] = []
    nolisting: list[str] = []
    dropped = 0
    for w in ws:
        if not w["toh"]:          # 目錄冊（dkar chag）本身沒有 Toh 號
            stat["目錄冊，無 Toh 號"] += 1
            continue
        got = by_toh.get(w["toh"])
        if got is None:
            stat["東北目錄無此條"] += 1
            nolisting.append(w["toh"])
            continue
        if not got:
            stat["無漢譯對照"] += 1
            w["zh_parallels"] = []
            w["title_zh"] = ""
            w["title_zh_source"] = ""
            continue
        rows = []
        for sats, blob in got:
            for sat in sats:
                hit = lookup(idx, sat, blob)
                if hit is None:
                    unmatched[sat] += 1
                    continue
                wid, title = hit
                if (w["toh"], wid) in UPSTREAM_WRONG:
                    dropped += 1        # 對照本層的計數，別混進部數統計
                    continue
                # 一格一個經號時書名與經號一對一，可以互相對帳。對不上不代表錯
                # ——多半是「藏文對到的是漢譯某部經當中的一品」（Toh 289
                # 「頻鞞娑邏王迎佛經」＝《中阿含經》第 62 經，所以經號給母經、
                # 書名寫品名）。所以只標記不丟棄，由 --audit 列出來供判讀。
                ok = True
                if len(sats) == 1:
                    cov = covered(title, blob)
                    if cov < COVER_MIN:
                        ok = False
                        suspect.append((w["toh"], wid, title, cov, blob))
                if not any(r["id"] == wid for r in rows):
                    row = {"id": wid, "t": sat, "title": title}
                    if not ok:
                        row["checked"] = False
                    # _rank 只在本函式內用來挑主對照本，寫回前會拿掉。
                    row["_rank"] = (covered(title, blob), -len(rows))
                    rows.append(row)
        if not rows:
            stat["有 SAT 但我們沒有那部經"] += 1
            w["zh_parallels"] = []
            w["title_zh"] = ""
            w["title_zh_source"] = ""
            continue
        # 🚨 主對照本不能用「經號最小」挑。Toh 120（大般涅槃經）對到
        #    T0037／T0375／T0376 三部，取最小號會挑到《緣本致經》——一部
        #    毫不相干的小經，而欄位有值、看起來完全正常。
        #    東北大一格裡只寫一個代表性書名，那就是它認的主對照本；拿它去比，
        #    比中的那一部當主，書名仍用我們自己目錄的繁體題名。
        best = max(rows, key=lambda r: r["_rank"])
        rows.sort(key=lambda r: r["id"])
        for r in rows:
            r.pop("_rank", None)
        w["zh_parallels"] = rows
        w["title_zh"] = best["title"]
        w["title_zh_source"] = "tohoku-sat"
        stat["單一對照" if len(rows) == 1 else "多部對照"] += 1

    print(f"快取 {meta['pages']:,} 頁，重覆 Toh {meta['dup']}；目錄 {len(ws):,} 部"
          f"（下表逐部計數，加起來就是部數）")
    for k, v in stat.most_common():
        print(f"  {k:<22}{v:>6,}")
    if dropped:
        print(f"  ——另有 {dropped} 筆對照本被 UPSTREAM_WRONG 排除（對照本層，不計入上表）")
    filled = sum(1 for w in ws if w.get("title_zh"))
    print(f"\n填得出漢譯對照：{filled:,}／{len(ws):,}（{filled/len(ws)*100:.1f}%）")
    if nolisting:
        # 這不是漏抓。Esukhia 那份 TEI 把幾部經再細分出後綴本（539a–f 是
        # Toh 539 底下的六種陀羅尼），東北目錄沒有給它們獨立條目。
        # 拿母條的對照本套上去是臆造，一律留空。
        print(f"\n📎 {len(nolisting)} 部在東北目錄裡沒有獨立條目（都是後綴本，"
              f"留空不套用母條的對照）：{'、'.join(sorted(nolisting))}")
    if unmatched:
        print(f"\n⚠️ {len(unmatched)} 個 SAT 經號在我們的大正藏目錄裡查不到"
              f"（多半是卷 56–84，CBETA 未收）：")
        print("   " + "、".join(f"T{k}×{v}" for k, v in unmatched.most_common(20)))
    if suspect:
        print(f"\n⚠️ 對帳閘標記 {len(suspect)} 筆待判讀：東北大那格的書名跟它自己掛的"
              f"SAT 經號對不上（字重疊 < {COVER_MIN:.0%}）。\n"
              f"   已收進目錄但標 checked:false；多數是「藏文對到漢譯某部經的一品」，"
              f"確定是上游標錯的請補進 UPSTREAM_WRONG：")
        for toh, wid, title, cov, blob in sorted(suspect, key=lambda x: x[3]):
            print(f"   Toh {toh:<6}{wid} 《{title[:26]}》  重疊 {cov:.0%}"
                  f"　東北大寫的是「{blob[:26]}」")

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
