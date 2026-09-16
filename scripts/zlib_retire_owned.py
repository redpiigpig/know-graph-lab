"""把「館藏已經有了」的書從 z-lib 獵表裡註銷，避免重複下載。

獵表是**願望清單不是庫存清單**——它從書目與作者著作表生成，從來沒跟
`ebooks` 比對過。所以已經用別的路徑收進來的書（TRC 檔案站、手動下載、
套書拆卷）還是會被排進去再抓一次。

作法：比對 `ebooks` 的書名／作者，命中的在 `scripts/state/zlib_ledger.jsonl`
補一列 `status: "already-owned"`。`zlib_fetch.mjs` 的 `doneKeys()` 會把
任何非 dry 的狀態算成已處理，所以寫進去就不會再排。

🚨 這支腳本的風險方向是**單向**的：註銷錯了 → 那本書永遠不會被下載，
   而且清單上看起來「已處理」，完全不會有人發現；漏註銷 → 頂多多抓一次。
   所以判準一律從嚴，寧可漏也不要錯：

   * 書名正規化後要**夠長**（≥ MIN_CHARS）才准比對。`expect` 寫成
     「Religion」那種通用詞會命中上百本。
   * 簡繁要先拉到同一套字形（opencc s2tw），否則《无形的宗教》對不上
     《無形的宗教》——而對不上只是漏註銷，不會出錯。
   * 有 `who` 時作者要對得上，或書名長到 LONG_CHARS 以上才免作者這一關。
   * 預設只印不寫（`--audit`），要真的寫得加 `--apply`。

  python scripts/zlib_retire_owned.py --audit           # 只看會註銷哪些
  python scripts/zlib_retire_owned.py --audit --show 60 # 多印幾筆
  python scripts/zlib_retire_owned.py --apply           # 真的寫進帳本
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
# 🚨 要讀 **合併後**那一份（zlib_wanted.py 的產物，fetcher 實際讀的就是它），
#    不是 data/zlib-wanted/*.jsonl。直接讀原始檔會少 862 筆（合併時還會
#    展開書目來源），而且 mukyokai-zh-found.jsonl 根本不是獵表格式、沒有 key。
WANTED_MERGED = ROOT / "output" / "zlib_wanted_all.jsonl"
WANTED_DIR = ROOT / "data" / "zlib-wanted"
LEDGER = ROOT / "scripts" / "state" / "zlib_ledger.jsonl"

# 書名正規化後至少要這麼多字才准比對
MIN_CHARS = 6
# 長到這個程度就算沒有作者也夠獨特
LONG_CHARS = 14

_CC = None


def norm(s: str) -> str:
    """正規化：簡→繁、去標點與空白、英文轉小寫。"""
    global _CC
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    if re.search(r"[一-鿿]", s):
        if _CC is None:
            import opencc
            _CC = opencc.OpenCC("s2tw")
        s = _CC.convert(s)
    s = s.lower()
    # 去掉 z-library 檔名慣有的尾巴與所有非字母數字漢字
    s = re.sub(r"z-?library|1lib|z-lib\.\w+", "", s)
    # 冠詞不算內容。《The Apocrypha…》與獵表的「Apocrypha…」是同一本，
    # 差一個 the 就前綴對不上。
    s = re.sub(r"^(the|a|an)\s+", "", s)
    return re.sub(r"[^0-9a-z一-鿿]", "", s)


def env() -> None:
    p = ROOT / ".env"
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def ebooks() -> list[dict]:
    """全部館藏（含全集），分頁撈完。

    🚨 PostgREST 不帶 limit 會靜默截在 1000 筆——那樣會少註銷，
       雖然方向安全，但數字會騙人，所以照樣要分頁撈到底。
    """
    env()
    base = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/ebooks"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    out: list[dict] = []
    step = 1000
    for off in range(0, 100_000, step):
        url = f"{base}?select=id,title,author,collection&limit={step}&offset={off}"
        req = urllib.request.Request(url, headers={
            "apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            page = json.loads(r.read().decode() or "[]")
        out.extend(page)
        if len(page) < step:
            break
    return out


def wanted() -> list[dict]:
    if not WANTED_MERGED.exists():
        raise SystemExit(f"✗ 找不到 {WANTED_MERGED}（先跑 scripts/zlib_wanted.py）")
    rows = []
    for line in WANTED_MERGED.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("key"):
            rows.append(r)
    return rows


def done_keys() -> set[str]:
    if not LEDGER.exists():
        return set()
    out = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("status") and r.get("status") != "dry" and r.get("key"):
            out.add(r["key"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=25)
    a = ap.parse_args()
    if not (a.audit or a.apply):
        ap.print_help()
        return

    books = ebooks()
    want = wanted()
    already = done_keys()
    print(f"館藏 {len(books):,} 本；獵表 {len(want):,} 筆（其中 {len(already):,} 筆帳本已處理）")

    # 館藏索引：正規化書名 → [(原書名, 作者)]
    idx: dict[str, list[tuple[str, str]]] = {}
    for b in books:
        t = norm(b.get("title") or "")
        if len(t) < MIN_CHARS:
            continue
        idx.setdefault(t, []).append((b.get("title") or "", b.get("author") or ""))
    keys = sorted(idx, key=len, reverse=True)

    hits: list[tuple[dict, str, str]] = []
    too_short = 0
    for w in want:
        if w["key"] in already:
            continue
        probe = norm(w.get("expect") or "") or norm(w.get("query") or "")
        if len(probe) < MIN_CHARS:
            too_short += 1
            continue
        who = norm(w.get("who") or "")
        for k in keys:
            # 🚨 只認**前綴**，不認任意子字串。實測任意子字串會把
            #    獵表「Colonial Encounter」配到館藏《The Bible and the Third
            #    World: Precolonial, Colonial and **Postcolonial Encounters**》
            #    ——完全是別本書，而註銷之後那本書再也不會被下載。
            #    反向（館藏書名比獵表短）另外要求長度不得低於八成，
            #    否則館藏裡一本叫《the World》的書會吃掉「The World's Religions」。
            if k.startswith(probe):
                pass
            elif probe.startswith(k) and len(k) >= 0.8 * len(probe):
                pass
            else:
                continue
            for title, author in idx[k]:
                # 🚨 想要中譯本、館藏卻只有英文原著，不算有。三筆 `-zh` 獵表
                #    就是這樣被英文本吃掉的——註銷之後中譯本永遠不會被抓。
                if w.get("lang") == "zh" and not re.search(r"[一-鿿]", title):
                    continue
                na = norm(author)
                # 🚨 書名相同、作者不同的書非常多，光靠書名長就放行會配錯人：
                #    Käsemann《Commentary on Romans》會配到賀智（Hodge）那本，
                #    Eichrodt《Theology of the Old Testament》會配到 Brueggemann 那本。
                #    兩邊都有作者時，作者就是硬條件。
                if who and na:
                    if who in na or na in who:
                        hits.append((w, title, author))
                        break
                    continue
                if len(probe) >= LONG_CHARS:
                    hits.append((w, title, author))
                    break
            else:
                continue
            break

    print(f"\n可註銷 {len(hits):,} 筆（書名太短不敢比的 {too_short:,} 筆略過）")
    for w, title, author in hits[:a.show]:
        print(f"  {w['key'][:42]:<44}獵表「{(w.get('expect') or '')[:26]}」")
        print(f"  {'':44}館藏《{title[:30]}》／{author[:20]}")
    if len(hits) > a.show:
        print(f"  …還有 {len(hits) - a.show:,} 筆（--show 看更多）")

    if not a.apply:
        print("\n（--audit 模式，沒有寫帳本）")
        return
    now = datetime.now(timezone.utc).isoformat()
    with LEDGER.open("a", encoding="utf-8") as f:
        for w, title, author in hits:
            f.write(json.dumps({
                "key": w["key"], "query": w.get("query", ""),
                "status": "already-owned", "owned_title": title,
                "owned_author": author, "at": now,
            }, ensure_ascii=False) + "\n")
    print(f"\n✓ 已在帳本補 {len(hits):,} 列 already-owned → {LEDGER}")


if __name__ == "__main__":
    main()
