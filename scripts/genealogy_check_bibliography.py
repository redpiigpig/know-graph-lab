"""書目三方比對：bibliography.json × 電子圖書館(ebooks) × z-lib 獵表。

    python scripts/genealogy_check_bibliography.py            # 只比對
    python scripts/genealogy_check_bibliography.py --emit     # 缺書寫進獵表

比對靠書名關鍵詞，不是精確字串——館藏標題有各種版本、副標與中譯名。
命中一律列出實際標題供人工覆核，不直接當作「已有」下結論。
"""
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "data/christian-genealogy/bibliography.json"
WANTED = ROOT / "data/zlib-wanted/apostolic-genealogy.jsonl"

# 每筆書目的查找關鍵詞（英文書名主幹，去掉冠詞與副標）
KEYS = {
    "Dunn 2006": "Unity and Diversity in the New Testament",
    "Meeks 2006": "Cambridge History of Christianity",
    "Bauckham 2002": "Gospel Women",
    "Taylor 1997": "Immerser",
    "Pearson 2004": "A Q Community in Galilee",
    "Rollens 2012": "Failure and Nerve",
    "Brown 1979": "Community of the Beloved Disciple",
    "Brown 1984": "Churches the Apostles Left Behind",
    "Martyn 2003": "History and Theology in the Fourth Gospel",
    "DeConick 2005": "Recovering the Original Gospel of Thomas",
    "Layton 2021": "Gnostic Scriptures",
    "Bauckham 1997": "Gospels for All Christians",
    "Sim 2001": "Gospels for All Christians A Response",
    "Last 2012": "Communities That Write",
    "Trebilco 2004": "Early Christians in Ephesus",
    "Goodacre 2001": "Synoptic Problem",
    "Kloppenborg 2008": "Q, the Earliest Gospel",
    "Litwa 2023": "Early Christianity in Alexandria",
    "Brock 1992": "Luminous Eye",
    "Griffith 2010": "Christianity in Edessa",
    "Dunn G 2004": "Tertullian",
    "Burns 2002": "Cyprian the Bishop",
    "Louth 2004": "Cambridge History of Early Christian Literature",
    "Ayres 2004": "Nicaea and Its Legacy",
    "Parvis 2006": "Marcellus of Ancyra",
    "Gwynn 2007": "The Eusebians",
    "King 2003": "What Is Gnosticism",
    "Williams 1996": "Rethinking Gnosticism",
    "Lieu 2015": "Marcion and the Making of a Heretic",
    "Trevett 1996": "Montanism",
    "Bauer 1971": "Orthodoxy and Heresy in Earliest Christianity",
    "Mitchell & Young 2006": "Origins to Constantine",
    "Streeter 1924": "The Four Gospels A Study of Origins",
    "Hengel 1983": "Between Jesus and Paul",
    "Hill 1992": "Hellenists and Hebrews",
    "Bockmuehl 2012": "Simon Peter in Scripture and Memory",
    "Painter 2004": "Just James",
    "Attridge 1989": "Epistle to the Hebrews Hermeneia",
    "Koester 1990": "Ancient Christian Gospels",
    "Ehrman & Pleše 2011": "Apocryphal Gospels Texts and Translations",
    "Aune 1997": "Revelation Word Biblical Commentary",
}

STOP = {"the", "a", "an", "of", "in", "and", "to", "is", "its"}


def env():
    return dict(
        l.strip().split("=", 1)
        for l in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
        if "=" in l and not l.startswith("#")
    )


def fetch_ebooks(e):
    url, key = e["SUPABASE_URL"].strip(), e["SUPABASE_SERVICE_ROLE_KEY"].strip()
    h = {"apikey": key, "Authorization": "Bearer " + key}
    rows, offset = [], 0
    while True:
        # 🚨 PostgREST 沒帶 limit 會靜默截在 1000 筆——這裡逐頁抓到取不到為止
        r = requests.get(
            f"{url}/rest/v1/ebooks?select=id,title,original_title,author,author_en&order=id&limit=1000&offset={offset}",
            headers=h)
        batch = r.json()
        # 🚨 欄位名寫錯時 PostgREST 回 400 的 dict，不是空 list。若直接 break，
        #    分母會變成 0 而看起來像「館裡沒有這些書」——實際上是查詢本身壞了。
        if not isinstance(batch, list):
            raise SystemExit(f"ebooks 查詢失敗，不是清單：{batch}")
        if not batch:
            break
        rows += batch
        offset += len(batch)
        if len(batch) < 1000:
            break
    return rows


def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())


def main():
    e = env()
    books = fetch_ebooks(e)
    print(f"電子圖書館共 {len(books)} 本（分母）")

    # 🚨 substring 比對會誤判：「Tertullian」命中 ANF 的《拉丁基督教：特土良》，
    #    「Just James」命中「TheDoctrineofJustificationJamesBuchanan」。
    #    改為詞界比對，並要求作者姓氏也對得上。
    haystack = [(b,
                 " " + norm(b.get("title")) + " " + norm(b.get("original_title")) + " ",
                 " " + norm(b.get("author")) + " " + norm(b.get("author_en")) + " ")
                for b in books]

    existing_wanted = set()
    for p in (ROOT / "data/zlib-wanted").glob("*.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    existing_wanted.add(norm(json.loads(line).get("query")))
                except Exception:
                    pass

    bib = json.loads(BIB.read_text(encoding="utf-8"))["entries"]
    have, missing, weak = [], [], []
    for k, title in KEYS.items():
        toks = [t for t in norm(title).split() if t and t not in STOP]
        surname = norm(k.rsplit(" ", 1)[0].replace("&", " ").replace("G ", "")).split()[0]
        hits, near = [], []
        for b, hay, auth in haystack:
            if all(f" {t} " in hay for t in toks):
                (hits if f" {surname} " in auth else near).append(b)
        if hits:
            have.append((k, title, hits[:2]))
        else:
            missing.append((k, title))
            if near:
                weak.append((k, title, near[:2]))

    print(f"\n已在館 {len(have)} / {len(KEYS)}")
    for k, title, hits in have:
        print(f"  ✓ {k:22s} → {hits[0].get('title')[:56]}")
    print(f"\n不在館 {len(missing)} / {len(KEYS)}")
    for k, title in missing:
        dup = "（獵表已有）" if norm(title) in existing_wanted else ""
        print(f"  ✗ {k:22s} {title}{dup}")

    if "--emit" in sys.argv:
        WANTED.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for k, title in missing:
            ent = bib[k]
            who = k.rsplit(" ", 1)[0]
            lines.append(json.dumps({
                "key": "ag-" + re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-"),
                "query": title,
                "expect": title,
                "who": who,
                "source": "apostolic-genealogy",
                "priority": 1,
                "zh": ent["supports"],
                "ref": ent["ref"],
            }, ensure_ascii=False))
        WANTED.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n寫出獵表 → {WANTED.relative_to(ROOT)}（{len(lines)} 筆，priority=1）")


if __name__ == "__main__":
    main()
