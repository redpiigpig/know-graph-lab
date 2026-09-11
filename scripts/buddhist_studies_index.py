#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 /research-data/buddhist-studies（當代佛學研究）那張卡片的資料。

這張卡片收二十世紀以來的佛學研究，七個策展分區加一個館藏盤點：

  佛學研究方法論  策展書目（佛教研究這門學科本身怎麼形成的）
  經典批判與詮釋  策展書目（文獻學、寫本、漢巴對照、大乘起源、疑偽經、詮釋學）
  教史研究     策展書目，帶 region（印度／中國／日本／韓國／藏傳／東南亞／近代改革）
  性別研究     策展書目（比丘尼僧團、八敬法、女性成佛、佛教女性主義、酷兒佛教）
  社會研究     策展書目（入世佛教、人間佛教、佛教與民族主義、佛教經濟、環境）
  制度研究     策展書目（僧團律制、寺院經濟、國家與僧伽、僧教育、居士組織）
  教理研究     策展書目（阿毘達磨、中觀、唯識、如來藏、禪、淨土、密續的現代研究）
  館藏佛學     電子圖書館既有（世界宗教類底下與佛教相關的 subcategory）

**與 /tripitaka（佛教大藏經）的分工**：那邊收**原典**（大正藏、卍續藏、漢譯南傳共
3,784 部全文），這一張收**研究**——二十世紀以來學者對這些原典與這個宗教寫的東西。
**與 /research-data/yinshun-hongshi 的分工**：那張收印順學派與弘誓的**刊物典藏**
（弘誓雙月刊、玄奘佛學研究學報），這一張收**學術專著書目**。

策展書目的每一筆會回頭比對電子圖書館，標出「已入館／缺」，缺的那些可以直接倒進
z-lib 獵表（見 --wanted）。

輸出 public/content/research-data/buddhist-studies/index.json（進版控）。

用法：
  python scripts/buddhist_studies_index.py            # 建索引
  python scripts/buddhist_studies_index.py --wanted   # 另外吐出缺書的獵表
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "data" / "research-data" / "buddhist-studies" / "bibliography.jsonl"
DIR = ROOT / "public" / "content" / "research-data" / "buddhist-studies"
OUT = DIR / "index.json"
WANTED = ROOT / "data" / "zlib-wanted" / "buddhist-studies.jsonl"

AREAS = [
    ("method", "佛學研究方法論", "🧭",
     "佛教研究這門學科本身是怎麼形成的：歐洲文獻學派從寫本裡「發現」佛教、京都學派把佛教"
     "當哲學問題、批判佛教對本覺與如來藏的攻擊、以及後殖民視角下對整套學科預設的翻查"),
    ("textual", "經典批判與詮釋", "📜",
     "文獻學這一層：寫本與犍陀羅新材料、漢巴四部對照、大乘起源之爭、疑偽經、漢譯的生成過程，"
     "以及佛教自身的詮釋規則（四依、了義不了義）"),
    ("history", "教史研究", "🗺",
     "印度、中國、日本、韓國、藏傳、東南亞各區的佛教史，以及十九世紀以來的近代改革運動。"
     "這一區的 region 是地理軸，與「各地的神學」那種處境軸不同"),
    ("gender", "性別研究", "♀",
     "比丘尼僧團的成立史與八敬法之爭、女性成佛與轉女成男說、佛教女性主義的重構方案、"
     "以及酷兒視角下的戒律與性論述"),
    ("social", "社會研究", "🌏",
     "入世佛教與人間佛教、佛教與民族主義及暴力、達利特改宗運動、佛教經濟學與環境運動——"
     "把佛教當成社會事實而非教理體系來看"),
    ("institution", "制度研究", "🏛",
     "僧團律制與羯磨、寺院經濟與僧祇戶、國家與僧伽的關係、僧教育的實況、居士組織的興起"),
    ("doctrine", "教理研究", "☸",
     "阿毘達磨、中觀、唯識、如來藏、禪、淨土、密續的現代學術研究。"
     "注意這一區收的是「對教理的研究」，不是教理文獻本身（那些在 /tripitaka）"),
]

# 館藏區：要盤點哪些桶。⚠️ 這份清單是 2026-09-11 實際查 ebooks 表得出的，不是猜的——
# 世界宗教類底下與佛教相關的只有「佛教」與「佛教/觀音信仰史」兩個 subcategory，
# 另有一本被歸在 category「佛學」（昭慧法師那本）。「東亞宗教」那 42 本查過了，
# 幾乎全是儒教與道教，不收。
LIBRARY_BUCKETS = [("世界宗教", "佛教"), ("世界宗教", "佛教/觀音信仰史"), ("佛學", None)]


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _headers(env: dict) -> dict:
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    return {"apikey": key, "Authorization": f"Bearer {key}"}


def _paged(env: dict, params: dict) -> list[dict]:
    """PostgREST 分頁。🚨 不帶 limit 會靜默截在 1000 筆，看起來像「全部跑完了」。"""
    out, off = [], 0
    while True:
        p = dict(params)
        p.update({"limit": "1000", "offset": str(off), "order": "id"})
        r = requests.get(f'{env["SUPABASE_URL"]}/rest/v1/ebooks', headers=_headers(env),
                         params=p, timeout=90)
        d = r.json()
        if not isinstance(d, list):
            print(f"  ! 查詢失敗 {d}")
            break
        out += d
        if len(d) < 1000:
            break
        off += 1000
    return out


def library_titles(env: dict) -> list[tuple[str, str]]:
    """整個電子圖書館的（題名, 作者），供比對書目用。

    ⚠️ 比的是**全館**不是只比佛教那幾個桶——館內分類本來就有誤，
    《漢魏兩晉南北朝佛教史》被歸到歷史學也很正常。
    """
    return [((x.get("title") or "").lower(), (x.get("author") or "").lower())
            for x in _paged(env, {"select": "title,author"})]


def library_stats(env: dict) -> list[dict]:
    """館藏盤點。全集（collection='collected-works'）與一般館藏分開報。

    🚨 佛教這一桶三百多本裡有九成是印順／太虛／聖嚴三套全集的個別卷，
    混在一起講「館藏三百本佛學研究」會嚴重灌水——那是原著不是研究，
    而且依 feedback_collected_works_not_in_library 全集本來就不算圖書館館藏。
    """
    rows = []
    for cat, sub in LIBRARY_BUCKETS:
        p = {"select": "chunk_count,collection", "category": f"eq.{cat}"}
        if sub:
            p["subcategory"] = f"eq.{sub}"
        d = _paged(env, p)
        if not d:
            continue
        for label, want_cw in ((sub or cat, False), (f"{sub or cat}‧全集", True)):
            part = [x for x in d if (x.get("collection") == "collected-works") is want_cw]
            if part:
                rows.append({"name": label, "books": len(part), "works": want_cw,
                             "chunks": sum(int(x.get("chunk_count") or 0) for x in part)})
    return sorted(rows, key=lambda x: -x["books"])


def key_words(title: str) -> str:
    """取題名裡最有辨識度的一段拿去比對——整串比對幾乎一定落空（副標、版次、冊數都會差）。

    ⚠️ 比神學那支多切了破折號。日文書名慣用「日本仏教史——思想史としてのアプローチ」
    這種長副標，館內中譯本卻只叫《日本佛教史》，不切破折號就整批對不上。
    """
    t = re.split(r"[:：(（/—–]", title)[0]
    t = re.sub(r"[《》\"'’”]", "", t).strip().lower()
    return t


def in_library(b: dict, lib: list[tuple[str, str]]) -> bool:
    """書目的一筆在不在館裡。

    ⚠️ 這個比對有兩個相反的壞法，兩個都不會報錯、兩個都看起來很正常：

    只拿**原文題名**比，會得出「248 本只有個位數在館」——因為館內題名九成是中文，
    `Histoire du bouddhisme indien` 當然對不上《印度佛教史》。後果是把已經有的書
    全倒進獵表重抓。
    只拿**題名**比，又會把拉莫特、平川彰、沃德爾、聖嚴四本《印度佛教史》判成同一本；
    館裡光《中國佛教史》就有蔣維喬與鎌田茂雄兩種，《印度佛教思想史》也有兩筆。
    前者害我們重抓已有的書，後者害我們以為有而其實沒有。

    所以：題名關鍵詞命中之後，還要作者對得上才算。作者欄空白的（館內不少）
    只有在題名夠獨特（八字以上）時才採信。取寧可漏報的一側。
    """
    cands = {key_words(b["title"]), key_words(b.get("title_zh") or "")}
    cands = {c for c in cands if len(c) >= 4}
    surname = re.split(r"[ ,(&]", b["author"].strip())[-1].lower() if b["author"] else ""
    surname = re.sub(r"[^a-z一-鿿]", "", surname)
    who = {w for w in (surname, (b.get("author_zh") or "").lower()) if len(w) >= 2}
    for t, a in lib:
        for c in cands:
            if c not in t:
                continue
            if any(w in a or w in t for w in who):
                return True
            if not a.strip() and len(c) >= 8:
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wanted", action="store_true", help="另外吐出缺書的 z-lib 獵表")
    args = ap.parse_args()

    env = load_env()
    bib = [json.loads(l) for l in BIB.read_text(encoding="utf-8").splitlines() if l.strip()]
    titles = library_titles(env)
    print(f"書目 {len(bib)} 筆；電子圖書館 {len(titles)} 筆題名")

    for b in bib:
        b["in_library"] = in_library(b, titles)

    areas = []
    for slug, name, icon, desc in AREAS:
        items = [b for b in bib if b["area"] == slug]
        items.sort(key=lambda b: (b.get("region") or "", b.get("year") or 0))
        areas.append({
            "slug": slug, "name": name, "icon": icon, "desc": desc,
            "source": "bibliography",
            "count": len(items),
            "in_library": sum(1 for b in items if b["in_library"]),
            "regions": sorted({b["region"] for b in items if b.get("region")}),
            "langs": {k: sum(1 for b in items if b["lang"] == k)
                      for k in sorted({b["lang"] for b in items})},
            "items": items,
        })
        print(f'  {name}：{len(items)} 筆，已入館 {areas[-1]["in_library"]}')

    parts = library_stats(env)
    areas.append({
        "slug": "library", "name": "館藏佛學", "icon": "📚",
        "desc": "電子圖書館裡與佛教相關的分類盤點。"
                "⚠️ 這一桶三百多本，但九成是印順、太虛、聖嚴三套全集的個別卷——"
                "那是原著不是研究，且依慣例全集不算圖書館館藏，因此上表分開計。"
                "真正的二手研究只有三十餘本，這正是本卡片以策展書目為主的原因。",
        "source": "library",
        "books": sum(p["books"] for p in parts if not p["works"]),
        "chunks": sum(p["chunks"] for p in parts if not p["works"]),
        "works_books": sum(p["books"] for p in parts if p["works"]),
        "parts": parts,
    })
    print(f'  館藏佛學：一般館藏 {areas[-1]["books"]} 本、{areas[-1]["chunks"]:,} 段；'
          f'全集另有 {areas[-1]["works_books"]} 卷')

    langs = {}
    for b in bib:
        langs[b["lang"]] = langs.get(b["lang"], 0) + 1
    print("  語言分布：" + "、".join(f"{k} {v}" for k, v in
                                sorted(langs.items(), key=lambda x: -x[1])))

    DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"areas": areas, "langs": langs, "total": len(bib)},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")

    if args.wanted:
        # 🚨 這個檔名早就有人在用了：[[ebook-zlib-harvest]] 手工策展過一份同名獵表
        #    （2026 年那批 1,444 筆清單裡的 bs-* 段）。直接覆寫會把別人策的書默默刪掉，
        #    而且不會有任何錯誤訊息。所以這裡是**合併**：本輪重新產生的照新的寫，
        #    本輪沒產生到的舊 key 原樣留著。
        prior = {}
        if WANTED.exists():
            for line in WANTED.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    prior[row["key"]] = row

        miss = [b for b in bib if not b["in_library"]]
        fresh = {}
        for b in miss:
            # ⚠️ slug 只留 a-z0-9，所以日文與中文書名一律 slug 成空字串，會整批退到
            #    「區-年份」這個鍵上互撞（實測撞掉 11 筆，而且不會報錯，只是獵表少幾本）。
            #    退路改用作者的漢字，再不行才補流水號。
            slug = re.sub(r"[^a-z0-9]+", "-", key_words(b["title"]))[:40].strip("-")
            if not slug:
                slug = f'{b["year"]}-{re.sub(r"[^一-鿿]", "", b["author_zh"])}'
            key = f"bs-{b['area']}-{slug}"
            while key in fresh:
                key += "-2"
            fresh[key] = {
                "key": key,
                "query": f"{b['author'].split('(')[0].strip()} {key_words(b['title'])}",
                "expect": key_words(b["title"]),
                "who": b["author"],
                "source": "buddhist-studies",
                "zh": f"{b['author_zh']}《{b['title_zh']}》",
            }
        kept = [r for k, r in prior.items() if k not in fresh]

        WANTED.parent.mkdir(parents=True, exist_ok=True)
        with WANTED.open("w", encoding="utf-8") as f:
            for row in list(fresh.values()) + kept:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"→ {WANTED}（本輪缺書 {len(fresh)} 筆，另保留舊獵表 {len(kept)} 筆）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
