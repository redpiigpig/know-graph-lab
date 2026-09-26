#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「最有影響力 N 篇」清單 → 先去 archive.org 找能整本下載的，抓回電子圖書館並解析。

使用者 2026-09-26：「西文文獻先找 archive.org 看看」。校內 IP 對出版社走不通（見
research-data-top-papers SKILL），archive.org 是合法且免費的第一站：公有領域的老書
（威爾豪森、貢克爾、施特勞斯…）與少數上傳的現代書都能整檔下載。

兩段式：
  python -X utf8 scripts/top_papers_archive_org.py biblical-studies --scan
      逐筆 advancedsearch，把候選寫進 output/top-papers/<field>-archive.json（快取，不進版控）
  python -X utf8 scripts/top_papers_archive_org.py biblical-studies --fetch
      把 scan 判定「可下載」的抓回 Drive 電子圖書館/神學/<領域子夾>/，建 ebooks 列，最後批次 parse

判定規則（都是實測過的坑）：
* 🚨 archive.org 上大量現代書是**借閱制**（controlled digital lending）：metadata 有
  `access-restricted-item: true`，collection 含 `inlibrary`／`printdisabled`，files 裡只有
  `_meta.xml`。這些一律跳過，不要硬抓。
* 題名相似度 ≥ 0.8 且 creator 含作者姓才算同一本；年份差 ≤ 3（archive.org 的 date 常是重印年）。
  同名不同書（"Genesis"、"Paul"）靠這兩道閘擋。
* 檔案挑法沿用 archive_org_fetch.pick_file（goog／bsb 結尾取 djvu.txt）。
* 一本只抓一個版本；已在館內（in_library）的跳過。
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")
import archive_org_fetch as ao  # noqa: E402

SEARCH = "https://archive.org/advancedsearch.php"
OUT = ROOT / "output" / "top-papers"
CATEGORY = "神學"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9一-鿿 ]+", " ", s)).strip()


def main_title(t: str) -> str:
    return re.split(r"[:：]|\s[–—-]\s", t)[0].strip()


def sim(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    if len(short) >= 18 and short in long_:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def surname(author: str) -> str:
    a = re.sub(r"[（(].*?[)）]", "", author or "")
    a = re.split(r"[,&]| and | und ", a)[0].strip()
    parts = [p for p in re.split(r"\s+", a) if p]
    return norm(parts[-1]) if parts else ""


def search(item: dict) -> list[dict]:
    t = main_title(item["title"])
    sn = surname(item["author"])
    q = f'title:("{t}") AND mediatype:texts'
    if sn and len(sn) >= 3:
        q += f' AND creator:({sn})'
    params = {"q": q, "fl[]": ["identifier", "title", "creator", "year", "date", "collection",
                              "access-restricted-item", "language"],
              "rows": 8, "output": "json"}
    url = SEARCH + "?" + urllib.parse.urlencode(params, doseq=True)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ao.UA}), timeout=60) as r:
                docs = json.load(r).get("response", {}).get("docs", [])
                break
        except Exception as e:
            if attempt == 3:
                print(f"   搜尋失敗：{type(e).__name__}")
                return []
            time.sleep(5 * (attempt + 1))
    out = []
    for d in docs:
        coll = d.get("collection") or []
        coll = coll if isinstance(coll, list) else [coll]
        restricted = str(d.get("access-restricted-item", "")).lower() == "true" or \
            any(c in ("inlibrary", "printdisabled", "internetarchivebooks") and "opensource" not in coll for c in coll)
        y = None
        for k in ("year", "date"):
            m = re.search(r"\d{4}", str(d.get(k) or ""))
            if m:
                y = int(m.group(0)); break
        cr = d.get("creator") or ""
        cr = " ".join(cr) if isinstance(cr, list) else cr
        s = sim(t, d.get("title") or "")
        out.append({"ident": d["identifier"], "title": d.get("title"), "creator": cr, "year": y,
                    "restricted": restricted, "sim": round(s, 3),
                    "author_ok": bool(sn) and sn in norm(cr)})
    return out


def choose(item: dict, cands: list[dict]) -> dict | None:
    good = [c for c in cands if not c["restricted"] and c["sim"] >= 0.8 and c["author_ok"]
            and (c["year"] is None or abs(c["year"] - int(item["year"])) <= 3 or c["year"] >= int(item["year"]))]
    # 同作者同書名的多個掃描版本：取年份最接近原版的
    good.sort(key=lambda c: (abs((c["year"] or item["year"]) - int(item["year"])), -c["sim"]))
    return good[0] if good else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("field")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--limit", type=int, default=9999)
    args = ap.parse_args()

    data = json.loads((ROOT / "public" / "content" / "research-data" / args.field / "top-papers.json").read_text(encoding="utf-8"))
    items = [i for g in data["groups"] for t in g["themes"] for i in t["items"]]
    OUT.mkdir(parents=True, exist_ok=True)
    cache_f = OUT / f"{args.field}-archive.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    key = lambda i: f'{i["title"]}|{i["year"]}'  # noqa: E731

    if args.scan:
        todo = [i for i in items if not i.get("in_library") and key(i) not in cache]
        print(f"待搜尋 {len(todo)}／全部 {len(items)}（館內已有 {sum(bool(i.get('in_library')) for i in items)}）")
        for n, it in enumerate(todo, 1):
            cands = search(it)
            pick = choose(it, cands)
            cache[key(it)] = {"cands": cands, "pick": pick}
            flag = f"✓ {pick['ident']}" if pick else ("借閱制" if any(c["restricted"] and c["sim"] >= 0.8 for c in cands) else "無")
            print(f"  [{n}/{len(todo)}] {it['year']} {it['title'][:48]:50} {flag}")
            if n % 20 == 0:
                cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
            time.sleep(1.2)
        cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")

    picks = [(it, cache[key(it)]["pick"]) for it in items if key(it) in cache and cache[key(it)].get("pick")]
    lend = sum(1 for it in items if key(it) in cache and not cache[key(it)].get("pick")
               and any(c["restricted"] and c["sim"] >= 0.8 for c in cache[key(it)]["cands"]))
    print(f"\n可整本下載 {len(picks)}；只有借閱制 {lend}；查過 {len(cache)}")

    if not args.fetch:
        for it, p in picks:
            print(f"  {it['group']} {it['year']} {it['author'][:22]:24} {it['title'][:44]:46} → {p['ident']}")
        return 0

    env = ao.load_env()
    sub = data["title"]
    done_f = OUT / f"{args.field}-archive-done.json"
    done = json.loads(done_f.read_text(encoding="utf-8")) if done_f.exists() else {}
    new_ids = []
    ok = fail = 0
    for it, p in picks[: args.limit]:
        k = key(it)
        if done.get(k, {}).get("ebook_id"):
            continue
        print(f"\n── {it['year']} {it['title'][:56]}  ({p['ident']})")
        try:
            meta = ao.fetch_json(ao.META.format(ident=p["ident"]))
        except Exception as e:
            print(f"   中繼取不到：{e}"); fail += 1; continue
        files = meta.get("files") or []
        pick = ao.pick_file(files, p["ident"])
        if not pick:
            print(f"   ✕ 沒有合用的內文檔（{len(files)} 個檔，可能是借閱制）")
            done[k] = {"ident": p["ident"], "error": "no file"}; fail += 1; continue
        name, ext, size = pick
        print(f"   選檔 {name}  {size/1024/1024:.1f} MB")
        safe = re.sub(r'[\\/:*?"<>|]+', "／", main_title(it["title"]))[:80]
        target = ao.DRIVE_ROOT / CATEGORY / sub / f"{it['author'][:40]}，{safe}{ext}"
        if not ao.download_resumable(ao.DL.format(ident=p["ident"], name=urllib.parse.quote(name)), target, size):
            fail += 1; continue
        row = {"title": it["title"], "author": it["author"], "category": CATEGORY, "sub": sub}
        eid = ao.insert_row(env, row, ext, target)
        done[k] = {"ident": p["ident"], "path": str(target), "ebook_id": eid}
        done_f.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
        if eid:
            new_ids.append(eid); ok += 1
        time.sleep(2)
    print(f"\n下載 {ok} 成功／{fail} 失敗；新列 {len(new_ids)}")
    if new_ids:
        import subprocess
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "scripts" / "parse_worker.py"), "run"]
        for i in new_ids:
            cmd += ["--book", i]
        print("解析：", " ".join(cmd[:6]), "…")
        subprocess.run(cmd, check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
