#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 84000 的書目後設資料併進德格版甘珠爾（DK）的目錄。

`tripitaka_derge.py` 從 TEI 正文抽出了藏文題名（1,075／1,124），但沒有梵文題名、
沒有英譯題名、也沒有譯者。這一支補那三樣，來源是 84000 的 Linked Open Data。

## 來源與授權

  https://github.com/84000/data-rdf   1,254 個 RDF，涵蓋 Toh 2–4458
  （甘珠爾＋丹珠爾；1–1108 裡只有 Toh 1、44、841 沒有獨立檔，那三部有子編號檔）
  **授權 CC0**，RDF 自己寫在 LegalData 裡。

⚠️ 用 GitHub 的 tarball 一次抓完（3 MB），不要逐檔抓 1,254 次——對方是公益專案。

## RDF 怎麼讀

四個 `skos:prefLabel` **都沒有 `xml:lang`**，只能靠它們掛在哪個 `rdf:Description`
底下分辨。實測 Toh 113：

  WAITOH113   (Work)     Saddharma­puṇḍarīka              ← 梵文題名
                         The White Lotus of the Good Dharma
  WATTOH113   (Work)     དམ་པའི་ཆོས་པད་མ་དཀར་པོ།            ← 藏文題名
  WAETOH113   (Work)     The White Lotus of the Good Dharma ← 英譯題名
                         Peter Alan Roberts                ← 譯者
  WEKDTOH113  (Instance) དམ་པའི་ཆོས་པད་མ་དཀར་པོ།

🚨 **梵文題名裡有軟連字符**（U+00AD，`Saddharma\u00adpuṇḍarīka` 那個看不見的字元）。
不清掉的話，站上搜「Saddharmapuṇḍarīka」會查不到，而字串看起來完全正常。

## 🚨 `title_zh` 這一支**不填**

84000 沒有漢譯對照，一個 Taishō 編號都沒有。而中文站真正要的 `title_zh` 是
**該經既有的漢譯正式書名**，不是藏文題名的翻譯：Toh 113 的藏文題名直譯是
「正法白蓮華」，漢譯正式書名卻是《妙法蓮華經》。把前者填進 title_zh，
讀者會以為那是真的漢譯書名——**頁面完全正常，內容是編的**。
漢譯書名要另外走東北目錄（宇井伯壽等，1934）的漢譯對照欄，只填對照表說有的。

## 順便得到一道驗證閘

84000 也給藏文題名，所以可以拿它**反驗**本站從 TEI 正文抽出來的那 1,075 個題名。
兩邊獨立取得，對得上才表示抽對了。不一致的逐筆列出，不要靜默覆蓋。

## 用法

  python scripts/tripitaka_derge_titles.py --fetch    # 抓 tarball 到 Drive 快取
  python scripts/tripitaka_derge_titles.py --merge    # 併進 DK.catalog.json 與各 toc.json
  python scripts/tripitaka_derge_titles.py --audit    # 只比對不寫檔
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tarfile
import unicodedata
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DK = Path("G:/我的雲端硬碟/資料/知識圖工作室/_tripitaka_tibetan")
CATALOG = DK / "DK.catalog.json"
CACHE = DK / "src" / "84000-data-rdf.tar.gz"
TARBALL = "https://codeload.github.com/84000/data-rdf/tar.gz/refs/heads/master"

DESC = re.compile(r'<rdf:Description rdf:about="([^"]+)">(.*?)</rdf:Description>', re.S)
LABEL = re.compile(r"<skos:prefLabel[^>]*>([^<]+)</skos:prefLabel>")


def clean(s: str) -> str:
    """清掉軟連字符與零寬字元——它們看不見，但會讓搜尋整個查不到。"""
    s = s.replace("\u00ad", "").replace("\u200b", "").replace("\ufeff", "")
    return unicodedata.normalize("NFC", s).strip()


# 🚨 84000 在「這部經沒有梵文題名」時，WAITOH 那一格塞的是英譯或佔位符
#    （`[no Sanskrit title]`）。照收的話 238 筆（21%）的梵文題名會是英文，
#    而頁面顯示「梵文題名：The Sūtra of Vasiṣṭha」看起來完全正常。
#    梵文轉寫不會出現英文虛詞，用這個判。
ENGLISH_STOPWORDS = re.compile(
    r"\b(the|of|on|to|in|and|with|for|from|by|a|an|that|which|who|"
    r"his|her|its|called|named|entitled)\b", re.I)


def looks_sanskrit(sa: str, en: str) -> bool:
    """WAITOH 給的這一串到底是不是梵文轉寫。"""
    if not sa:
        return False
    if "no Sanskrit" in sa or sa.startswith("["):
        return False
    if en and sa.strip() == en.strip():
        return False
    return not ENGLISH_STOPWORDS.search(sa)


def die(msg: str) -> None:
    print(f"✗ {msg}")
    raise SystemExit(1)


def fetch() -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    print(f"抓 {TARBALL}")
    req = urllib.request.Request(TARBALL, headers={
        "User-Agent": "kglab-research/1.0 (academic; non-commercial)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    tmp = CACHE.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.replace(CACHE)
    print(f"✓ {len(data)/1024/1024:.1f} MB → {CACHE}")


def parse_all() -> dict[str, dict]:
    """tarball → {toh: {title_sa, title_en, title_bo, translator_en}}"""
    if not CACHE.exists():
        die("還沒抓 tarball，先跑 --fetch")
    out: dict[str, dict] = {}
    with tarfile.open(CACHE, "r:gz") as tf:
        for m in tf.getmembers():
            name = m.name.rsplit("/", 1)[-1]
            mm = re.fullmatch(r"toh([\w.-]+)\.rdf", name)
            if not mm:
                continue
            toh = mm.group(1)
            f = tf.extractfile(m)
            if not f:
                continue
            t = f.read().decode("utf-8", errors="replace")
            rec: dict[str, str] = {}
            for about, body in DESC.findall(t):
                key = about.rsplit("/", 1)[-1]
                labs = [clean(x) for x in LABEL.findall(body)]
                if not labs:
                    continue
                if key.startswith("WAITOH"):
                    rec["_sa_raw"] = labs[0]
                    if len(labs) > 1:
                        rec.setdefault("title_en", labs[1])
                elif key.startswith("WATTOH"):
                    rec["title_bo_84000"] = labs[0]
                elif key.startswith("WAETOH"):
                    rec["title_en"] = labs[0]
                    if len(labs) > 1:
                        rec["translator_en"] = "; ".join(labs[1:])
            # 梵文題名最後才定案——要先知道英譯是什麼才判得出來
            raw = rec.pop("_sa_raw", "")
            if looks_sanskrit(raw, rec.get("title_en", "")):
                rec["title_sa"] = raw
            if rec:
                out[toh] = rec
    return out


# 敬語前綴「聖」（Ārya）。本站從正文抽的題名保留它，84000 的通行略稱多半省略。
ARYA = "\u0f60\u0f55\u0f42\u0f66\u0f54"


def bo_key(s: str) -> str:
    """比對藏文題名用：去掉藏文標點與空白，只留字母。"""
    return re.sub(r"[^\u0f40-\u0fbc]", "", s or "")


def same_title(ours: str, theirs: str) -> bool:
    """兩個藏文題名是不是同一部經。

    🚨 **兩邊用的是不同的題名形式，不是誰對誰錯。**本站抽的是正文自帶的**全名**
    （如「毘奈耶分別」的完整寫法），84000 給的是學界通行的**略稱**；
    本站保留敬語前綴（聖／Ārya），84000 多半省略。
    直接拿字串相等去比，會得到「879 筆不一致」這種嚇人而且沒有意義的數字，
    然後讓人以為切錯了七成八的經。

    判準：去標點、去敬語前綴之後，一邊是另一邊的前綴，或兩邊起首 12 個藏文
    字母相同，就算同一部。剩下真正對不上的才值得逐筆看——那才可能是切錯經。
    """
    a, b = bo_key(ours), bo_key(theirs)
    if not a or not b:
        return False
    if a.startswith(ARYA):
        a = a[len(ARYA):]
    if b.startswith(ARYA):
        b = b[len(ARYA):]
    if a.startswith(b) or b.startswith(a):
        return True
    k = 12
    return len(a) >= k and len(b) >= k and a[:k] == b[:k]


def degenerate(title: str) -> bool:
    """本站抽出來的題名是不是只剩敬語前綴、沒抓到正題名。"""
    k = bo_key(title)
    if k.startswith(ARYA):
        k = k[len(ARYA):]
    return len(k) < 4


def run(merge: bool) -> None:
    if not CATALOG.exists():
        die("找不到 DK.catalog.json，先跑 tripitaka_derge.py")
    meta = parse_all()
    print(f"84000 解析到 {len(meta):,} 筆（含丹珠爾與子編號）")

    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    works = cat["works"]
    hit = sa = en = tr = 0
    agree = differ = onlyone = 0
    mismatches: list[tuple[str, str, str]] = []

    for w in works:
        toh = w.get("toh")
        if not toh:
            continue
        m = meta.get(str(toh))
        if not m:
            continue
        hit += 1
        # 藏文題名：**反驗，不覆蓋**。本站的是從 TEI 正文抽的，那才是正本。
        ours, theirs = w.get("title_bo", ""), m.get("title_bo_84000", "")
        if ours and theirs:
            if same_title(ours, theirs):
                agree += 1
            else:
                differ += 1
                if len(mismatches) < 12:
                    mismatches.append((w["id"], ours[:34], theirs[:34]))
        elif ours or theirs:
            onlyone += 1
        if merge:
            if m.get("title_sa"):
                w["title_sa"] = m["title_sa"]
            if m.get("title_en"):
                w["title_en"] = m["title_en"]
            if m.get("translator_en"):
                w["translator_en"] = m["translator_en"]
            if theirs:
                w["title_bo_short"] = theirs      # 84000 的通行略稱，與全名並存
            # 🚨 本站的題名有一小批是「退化」的——抽到的只有敬語前綴（聖／Ārya）
            #    本身，正題名沒抓到（實測 Toh 548／796／894／1035）。那種情況
            #    84000 的才是對的。判準：去掉敬語前綴後不足 4 個藏文字母。
            if theirs and (not ours or degenerate(ours)):
                w["title_bo"] = theirs
                w["title_source"] = "84000"
        sa += bool(m.get("title_sa"))
        en += bool(m.get("title_en"))
        tr += bool(m.get("translator_en"))

    n = len(works)
    print(f"\n本站 {n:,} 部，84000 對得上 {hit:,}（{hit/n:.1%}）")
    print(f"  可補梵文題名 {sa:,}／英譯題名 {en:,}／譯者 {tr:,}")
    print(f"\n藏文題名反驗（兩邊獨立取得）：")
    print(f"  一致 {agree:,}　不一致 {differ:,}　只有一邊有 {onlyone:,}")
    deg = [w["id"] for w in works if w.get("title_bo") and degenerate(w["title_bo"])]
    if deg:
        print(f"  ⚠️ 本站題名退化（只剩敬語前綴）{len(deg)} 筆：{'、'.join(deg[:8])}"
              f"{'…' if len(deg) > 8 else ''}")
        print("     這幾筆採用 84000 的題名（--merge 時）")
    if mismatches:
        print("  不一致的樣本（本站從 TEI 抽 ／ 84000）：")
        for wid, a, b in mismatches:
            print(f"    {wid}  {a}  ／  {b}")

    if not merge:
        print("\n（--audit 模式，沒有寫檔）")
        return

    tmp = CATALOG.with_suffix(".json.part")
    tmp.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(CATALOG)
    # 同步各部的 toc.json
    synced = 0
    for w in works:
        p = DK / f"{w['id']}.toc.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        tgt = d.get("meta", d)
        for k in ("title_sa", "title_en", "translator_en", "title_bo", "title_bo_short", "title_source"):
            if w.get(k):
                tgt[k] = w[k]
        t2 = p.with_suffix(".json.part")
        t2.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        t2.replace(p)
        synced += 1
    named = sum(1 for w in works if w.get("title_bo"))
    print(f"\n✓ 已寫入 DK.catalog.json 與 {synced:,} 個 toc.json")
    print(f"  現在有藏文題名 {named:,}／{n:,}（{named/n:.1%}）")
    print(f"  ⚠️ title_zh 仍全部留空——84000 沒有漢譯對照，要另走東北目錄")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--audit", action="store_true")
    a = ap.parse_args()
    if not any((a.fetch, a.merge, a.audit)):
        ap.print_help()
        return 0
    if not DK.parent.exists():
        die("G: 沒掛載——先修 Drive，別寫進不存在的路徑")
    if a.fetch:
        fetch()
    if a.audit or a.merge:
        run(merge=a.merge)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
