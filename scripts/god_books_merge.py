#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三本書的書目合併去重、對館藏、產抓書單。
讀 output/god_books/{aslan,armstrong,wright}.json →
  output/god_books/merged.json（每筆含 status）與 data/zlib-wanted/god-books-bibliography.jsonl
"""
import hashlib, json, re, sys, unicodedata
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import requests
from ingest_new_books import URL, SB_HEADERS
OUT = ROOT / "output" / "god_books"
WANTED = ROOT / "data" / "zlib-wanted" / "god-books-bibliography.jsonl"

# 不是可獵的書：聖經譯本、純古典原典（作者欄就是古人）、書評
DROP_AUTHOR = re.compile(r"^(herodotus|pausanias|cicero|tertullian|new oxford|muhammad ibn ishaq|meister eckhart|"
                         r"al-mundiqh|philo of|lucius apuleius|karen armstrong$)", re.I)
DROP_TITLE = re.compile(r"annotated bible|^the bible$|^koran|^qur.?an$|loeb", re.I)


def nk(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9一-鿿]+", "", s)


def main_title(t):
    return re.split(r"[:：;]", t)[0].strip()


def surname(a):
    a = re.sub(r"\b(jr|sr|ed|eds)\b\.?", "", a, flags=re.I)
    if "," in a:  # Chicago 體：姓, 名
        return nk(a.split(",")[0])
    parts = [p for p in re.split(r"\s+", a.strip()) if p]
    return nk(parts[-1]) if parts else ""


def fix_author(a):
    a = re.sub(r",\s*et al\.?", "", a)
    a = re.sub(r"^Mircea, et al Eliade$", "Mircea Eliade", a)
    if a == "W Smith":
        return "W. Robertson Smith"
    a = re.sub(r",?\s*\beds?\.?,?$", "", a.strip())
    if "," in a and not re.search(r"\band\b", a):
        last, first = [x.strip() for x in a.split(",", 1)]
        a = f"{first} {last}"
    return a.strip()


def load():
    rows = []
    for f in ("aslan", "armstrong", "wright"):
        for x in json.loads((OUT / f"{f}.json").read_text(encoding="utf-8")):
            if x.get("flag"):
                continue
            t = (x.get("title") or "").strip()
            a = (x.get("author") or "").strip()
            if not t or len(t) < 8 or "“" in t or re.match(r"^[A-Z][a-z]+\.\s", t) and "Press" in t:
                continue
            if t == "Robertson" and a.startswith("Smith"):
                a, t = "W. Robertson Smith", "Lectures on the Religion of the Semites"
            if nk(a) == nk(t):
                continue  # 經典本身（Bhagavad Gita 之類）
            if DROP_AUTHOR.search(a) or DROP_TITLE.search(t):
                continue
            rows.append({"author": fix_author(a), "title": re.sub(r"\.\s*\d+(rd|nd|th)? ed\.?$", "", t),
                         "year": str(x.get("year") or "")[:4] or None, "zh": x.get("zh"),
                         "from": x["from"]})
    return rows


def dedupe(rows):
    by = {}
    for r in rows:
        k = (surname(r["author"]), nk(main_title(r["title"]))[:40])
        if k in by:
            e = by[k]
            if r["from"] not in e["from"]:
                e["from"].append(r["from"])
            if len(r["title"]) > len(e["title"]):
                e["title"] = r["title"]
            e["year"] = e["year"] or r["year"]
            e["zh"] = e["zh"] or r["zh"]
        else:
            by[k] = dict(r, **{"from": [r["from"]]})
    return list(by.values())


def library():
    out, off = [], 0
    while True:
        b = requests.get(f"{URL}/rest/v1/ebooks?select=id,title,author,original_title,category&offset={off}&limit=1000",
                         headers=SB_HEADERS, timeout=90).json()
        out += b
        if len(b) < 1000:
            break
        off += 1000
    return out


def match(r, lib_idx):
    mt = nk(main_title(r["title"]))
    sn = surname(r["author"])
    if len(mt) < 6:
        return None
    for b in lib_idx:
        if mt in b["_k"]:
            # 書名主體相符：作者姓也要在作者欄或書名裡，或書名主體夠長（≥14）
            if sn and (sn in b["_a"] or sn in b["_k"]):
                return b
            if len(mt) >= 12 and mt in b["_o"]:
                return b
    return None


def main():
    rows = dedupe(load())
    lib = library()
    for b in lib:
        b["_k"] = nk((b.get("title") or "") + " " + (b.get("original_title") or ""))
        b["_a"] = nk(b.get("author") or "")
        b["_o"] = nk(b.get("original_title") or "")
    print("館藏", len(lib), "本；去重後", len(rows), "筆")
    for r in rows:
        b = match(r, lib)
        r["status"] = "館內已有" if b else "待抓"
        if b:
            r["library"] = f"{b['category']}｜{b['title'][:60]}"
    # 出版年 ≤1930 的先走 archive.org（god_books_archive.py）；它跑完、落空的才進獵表
    ar = OUT / "archive_result.json"
    arch = {(x["author"], x["title"]): x["status"] for x in json.loads(ar.read_text(encoding="utf-8"))} if ar.exists() else {}
    for r in rows:
        r["archive"] = arch.get((r["author"], r["title"]))
        if r["status"] == "待抓" and r["archive"] == "downloaded":
            r["status"] = "公開典藏已下載"
    todo = [r for r in rows if r["status"] == "待抓" and not (
        r["year"] and int(r["year"]) <= 1930 and r["archive"] is None)]
    (OUT / "merged.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with WANTED.open("w", encoding="utf-8") as f:
        for r in todo:
            sn = surname(r["author"])
            sur = r["author"].split(",")[0] if "," in r["author"] else r["author"].split()[-1]
            key = hashlib.sha1(f"{r['author']}|{r['title']}".encode()).hexdigest()[:10]
            f.write(json.dumps({
                "key": f"godbib-{key}", "query": f"{main_title(r['title'])} {sur}",
                "expect": main_title(r["title"]), "who": sur, "lang": "orig",
                "source": "god-books-bibliography",
                "zh": f"{r['author']}《{r['title']}》（出自{'、'.join(r['from'])}）"}, ensure_ascii=False) + "\n")
    from collections import Counter
    print(Counter(r["status"] for r in rows), "進獵表", len(todo))


if __name__ == "__main__":
    main()
