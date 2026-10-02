#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merged.json 裡出版年 ≤1930 的書：先找 archive.org（免額度），驗過 OCR 才下載到 z-lib/ drop 夾。
python -X utf8 scripts/god_books_archive.py [--dry]
結果寫 output/god_books/archive_result.json（status: downloaded / no-candidate / restricted / bad-ocr）
"""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import god_books_merge as gm
from archive_djvu_clean import quality
OUT = ROOT / "output" / "god_books"
DROP = ROOT / "z-lib"
UA = {"User-Agent": "Mozilla/5.0 (kglab-ingest)"}
MAXYEAR = 1930


def get(url, binary=False, timeout=40, rng=None):
    for i in range(3):
        try:
            h = dict(UA, **({"Range": rng} if rng else {}))
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                d = r.read()
            return d if binary else d.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            err = e
            if e.code == 416:
                rng = None
            time.sleep(2)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2)
    raise err


def search(title, sn):
    q = f'title:({gm.main_title(title)}) AND creator:({sn}) AND mediatype:texts'
    u = ("https://archive.org/advancedsearch.php?q=" + urllib.parse.quote(q) +
         "&fl[]=identifier&fl[]=title&fl[]=creator&fl[]=year&fl[]=downloads&rows=15&output=json&sort[]=downloads+desc")
    return json.loads(get(u))["response"]["docs"]


def pick(r):
    sn = r["author"].split(",")[0] if "," in r["author"] else r["author"].split()[-1]
    mt = gm.nk(gm.main_title(r["title"]))
    for d in search(r["title"], sn):
        t = d.get("title") or ""
        if isinstance(t, list):
            t = t[0]
        if mt[:12] not in gm.nk(t):
            continue
        try:
            m = json.loads(get(f"https://archive.org/metadata/{d['identifier']}"))
        except Exception:  # noqa: BLE001
            continue
        if m.get("metadata", {}).get("access-restricted-item") == "true":
            continue
        files = m.get("files", [])
        txt = next((f for f in files if f.get("format") == "DjVuTXT"), None)
        pdf = next((f for f in files if f.get("format") in ("Text PDF", "Additional Text PDF")), None) \
            or next((f for f in files if f["name"].lower().endswith(".pdf") and "_bw" not in f["name"]), None)
        if not (txt and pdf):
            continue
        sample = get(f"https://archive.org/download/{d['identifier']}/{urllib.parse.quote(txt['name'])}", rng="bytes=200000-500000")
        if len(sample) < 30000:
            continue  # 只有一小段或抽錯卷
        q = quality(sample, "en")
        yield d["identifier"], t, pdf, len(sample), q
    return


def main():
    dry = "--dry" in sys.argv
    rows = [r for r in json.loads((OUT / "merged.json").read_text(encoding="utf-8"))
            if r["status"] == "待抓" and r["year"] and int(r["year"]) <= MAXYEAR]
    res = []
    for r in rows:
        rec = {"author": r["author"], "title": r["title"], "status": "no-candidate"}
        try:
            for ident, t, pdf, n, q in pick(r):
                rec.update(ident=ident, found_title=t, chars=n, quality=q)
                if q.get("verdict") != "ok":
                    rec["status"] = "bad-ocr"; continue
                if int(pdf.get("size", 0)) > 200_000_000:
                    rec["status"] = "too-big"; continue
                name = re.sub(r'[\/:*?"<>|]', " ", f"{r['title'][:100]} ({r['author']}).pdf")
                dest = DROP / name
                if not dry:
                    data = get(f"https://archive.org/download/{ident}/{urllib.parse.quote(pdf['name'])}", True, 900)
                    if data[:4] != b"%PDF":
                        rec["status"] = "not-pdf"; continue
                    dest.write_bytes(data)
                rec.update(status="downloaded" if not dry else "would-download", file=name)
                if not dry:
                    import hashlib
                    from datetime import datetime, timezone
                    key = "godbib-" + hashlib.sha1(f"{r['author']}|{r['title']}".encode()).hexdigest()[:10]
                    with (ROOT / "scripts" / "state" / "zlib_ledger.jsonl").open("a", encoding="utf-8") as f:
                        f.write(json.dumps({"key": key, "query": r["title"], "status": "downloaded", "file": name,
                                            "pick": {"via": "archive.org", "ident": ident},
                                            "at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False) + chr(10))
                break
        except Exception as e:  # noqa: BLE001
            rec["status"] = f"error {type(e).__name__}: {str(e)[:60]}"
        print(rec["status"], "|", r["author"][:20], "|", r["title"][:40], "|", rec.get("ident", ""), flush=True)
        res.append(rec)
    (OUT / "archive_result.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


main()
