"""建新約逐節索引：章節結構取自站上自己的經文資料（R2 bible-verses/{book}.json.gz），
並標出哪些節在希臘文校訂本（逐詞詞形分析）裡不存在。

    python scripts/genealogy_build_verse_index.py

為什麼不用希臘文那份當骨架：NA/UBS 略去 26 節存疑經節，其中約 7:53–8:11
（行淫時被拿的婦人）整段不在。那段偏偏是譜系上最有意思的一種材料——一段
在各抄本間漂浮、擺放位置不定的傳統。骨架若用校訂本，這 26 節就沒有列可掛。

輸出 data/christian-genealogy/nt-verse-index.json：
    { book: {code, name_zh, chapters: {ch: [verse, ...]}, verses: N, absent_in_na: [...]}}
"""
import gzip
import io
import json
import os
from pathlib import Path

import boto3
import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/christian-genealogy/nt-verse-index.json"
MORPH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\經典對照與註釋\聖經逐詞詞形分析\books")

# 站上 bible_books.code → 逐詞詞形分析的檔名
NT_BOOKS = [
    ("mat", "Matt"), ("mrk", "Mark"), ("luk", "Luke"), ("jhn", "John"), ("act", "Acts"),
    ("rom", "Rom"), ("1co", "1Cor"), ("2co", "2Cor"), ("gal", "Gal"), ("eph", "Eph"),
    ("php", "Phil"), ("col", "Col"), ("1th", "1Thess"), ("2th", "2Thess"),
    ("1ti", "1Tim"), ("2ti", "2Tim"), ("tit", "Titus"), ("phm", "Phlm"),
    ("heb", "Heb"), ("jas", "Jas"), ("1pe", "1Pet"), ("2pe", "2Pet"),
    ("1jn", "1John"), ("2jn", "2John"), ("3jn", "3John"), ("jud", "Jude"), ("rev", "Rev"),
]


def env():
    return dict(
        l.strip().split("=", 1)
        for l in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
        if "=" in l and not l.startswith("#")
    )


def r2_client(e):
    return boto3.client(
        "s3", endpoint_url=e["R2_ENDPOINT"].strip(),
        aws_access_key_id=e["R2_ACCESS_KEY"].strip(),
        aws_secret_access_key=e["R2_SECRET_KEY"].strip(), region_name="auto",
    )


def book_meta(e):
    url, key = e["SUPABASE_URL"].strip(), e["SUPABASE_SERVICE_ROLE_KEY"].strip()
    h = {"apikey": key, "Authorization": "Bearer " + key}
    r = requests.get(
        f"{url}/rest/v1/bible_books?select=code,name_zh,chapter_count&limit=200", headers=h)
    return {x["code"]: x for x in r.json()}


def na_verses(morph_name):
    """希臘文校訂本實際有的節（逐詞詞形分析的 byVerse 鍵）"""
    p = MORPH / f"{morph_name}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    out = set()
    for k in d["byVerse"]:
        parts = k.split(".")
        out.add((int(parts[1]), int(parts[2])))
    return out


def main():
    e = env()
    s3 = r2_client(e)
    bucket = e["R2_BUCKET"].strip()
    meta = book_meta(e)

    books = {}
    total = 0
    total_absent = 0
    total_ghost = 0
    for code, morph in NT_BOOKS:
        obj = s3.get_object(Bucket=bucket, Key=f"bible-verses/{code}.json.gz")
        doc = json.loads(gzip.decompress(obj["Body"].read()).decode("utf-8"))

        # 🚨 R2 的經文檔在「代號開頭是數字」的卷裡有鬼章：每章多一個
        #    「章號＋代號開頭數字」的重複鍵（1jn 第1章多一個 "11"、3jn 第1章多
        #    一個 "13"）。拿檔案直接統計會多算一倍。以 bible_books.chapter_count
        #    當白名單，只收真章號。1co 的 "11" 與 2co 的 "12" 兩個鬼鍵會撞到真章
        #    號，實測撞號時存的是真章內容（哥林多前書 11:1「你們該效法我」），
        #    故站上閱讀器顯示無誤，但計數必須濾。
        max_ch = meta[code]["chapter_count"]
        chapters, ghosts = {}, []
        for ch, entries in doc["chapters"].items():
            c = int(ch)
            if 1 <= c <= max_ch and str(c) == str(ch):
                chapters[str(c)] = sorted(x["v"] for x in entries)
            else:
                ghosts.append(ch)
        n = sum(len(v) for v in chapters.values())
        total_ghost += len(ghosts)

        na = na_verses(morph)
        absent = []
        if na is not None:
            for ch, vs in chapters.items():
                for v in vs:
                    if (int(ch), v) not in na:
                        absent.append(f"{ch}:{v}")

        books[code] = {
            "code": code, "morph": morph, "name_zh": meta[code]["name_zh"],
            "chapters": chapters, "verses": n,
            "absent_in_na": absent,
            "ghost_keys_filtered": ghosts,
        }
        total += n
        total_absent += len(absent)
        print(f"  {code:4s} {meta[code]['name_zh']:7s} {len(chapters):3d} 章 {n:5d} 節"
              f"{'  校訂本無 ' + str(len(absent)) + ' 節' if absent else '':>18s}"
              f"{'  濾掉鬼章 ' + str(len(ghosts)) if ghosts else ''}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "meta": {
            "title": "新約逐節索引（章節結構取自站上經文資料）",
            "skeleton_source": "R2 bible-verses/{book}.json.gz（與 /scripture 閱讀器同一份）",
            "na_source": "Drive 聖經逐詞詞形分析 byVerse（希臘文校訂本）",
            "generated_by": "scripts/genealogy_build_verse_index.py",
            "total_verses": total,
            "absent_in_na": total_absent,
            "ghost_keys_filtered": total_ghost,
            "ghost_key_bug": "R2 經文檔在代號開頭為數字的卷有重複鬼章（章號＋代號開頭數字）；本索引以 bible_books.chapter_count 白名單濾除，來源檔本身未修",
            "note": "absent_in_na 標的是校訂本略去、但站上閱讀器有的節；它們照樣要有歸屬列",
        },
        "books": books,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n新約合計 {total} 節；其中 {total_absent} 節不在希臘文校訂本裡")
    print("寫出 →", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
