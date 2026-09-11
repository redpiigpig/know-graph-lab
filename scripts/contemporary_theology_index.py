#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 /research-data/contemporary-theology（當代神學研究）那張卡片的資料。

這張卡片收二十世紀以來的神學研究，六區：

  神學方法論    策展書目（神學怎麼做這件事本身的討論）
  二十世紀神學史  策展書目（神學史的回顧與爭論）
  系統神學經典   策展書目（各傳統的大部頭教義學）
  各地的神學    策展書目（處境／解放／女性主義／後殖民／黑人／原住民⋯⋯，按地區分）
  吉福德講座    scraped（1888 迄今 210 場的講者與講題，見 gifford_lectures_fetch.py）
  館藏當代神學   電子圖書館既有（神學類底下屬近現代的那幾個 subcategory）

**與「基督教研究」那張卡片的分工**：那一張按時期與運動收教會史材料（教父、宗教改革、
普世運動、洛桑），這一張按學科收神學本身。依使用者定的邊界——系統神學與神學家著作
歸「神學」，教會史歸「基督教」。

策展書目的每一筆會回頭比對電子圖書館，標出「已入館／缺」，缺的那些可以直接倒進
z-lib 獵表（見 --wanted）。

輸出 public/content/research-data/contemporary-theology/index.json（進版控）。

用法：
  python scripts/contemporary_theology_index.py            # 建索引
  python scripts/contemporary_theology_index.py --wanted   # 另外吐出缺書的獵表
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
BIB = ROOT / "data" / "research-data" / "contemporary-theology" / "bibliography.jsonl"
DIR = ROOT / "public" / "content" / "research-data" / "contemporary-theology"
OUT = DIR / "index.json"
GIFFORD = DIR / "gifford.json"
WANTED = ROOT / "data" / "zlib-wanted" / "contemporary-theology.jsonl"

AREAS = [
    ("method", "神學方法論", "🧭",
     "神學怎麼做這件事本身的討論：從士萊馬赫的學科三分，到關聯法、後自由主義的文化語言進路、"
     "先驗方法與處境神學的模式論"),
    ("history", "二十世紀神學史", "📖",
     "神學史的回顧與爭論。注意這一區收的是「對神學史的討論」，不是神學史料本身"),
    ("biblical", "聖經神學", "📜",
     "舊約與新約神學，以及這門學科反覆的自我懷疑：艾希羅特與馮拉德的中心之爭、"
     "巴爾對字源式神學的清算、柴爾茲的正典進路、保羅新觀"),
    ("systematics", "系統神學經典", "🏛",
     "各傳統的大部頭教義學：新教、天主教、東正教並列，不以任一方為預設"),
    ("practical", "實踐神學", "🤲",
     "牧養神學、宗教教育、質性研究方法。這一區的主張是「整個神學都是實踐神學」，"
     "不是把它當成系統神學的應用"),
    ("liberal", "自由神學", "🕊",
     "士萊馬赫、立敕爾、哈納克一線，到社會福音、芝加哥學派與當代建構神學。"
     "收它是因為二十世紀大半的神學爭論是在回應它"),
    ("secular", "世俗神學", "🏙",
     "潘霍華的「無宗教的基督教」長出來的一支：戈加騰、羅賓遜、考克斯、死神神學，"
     "到泰勒《世俗時代》與弱神學。與自由神學相鄰但不是同一件事"),
    ("narrative", "敘事神學", "📖",
     "主張神學的基本形式是故事不是命題。尼布爾、克萊茨、傅萊、侯活士一線，"
     "哲學支柱在呂格爾與麥金泰爾"),
    ("liberation", "解放神學", "✊",
     "拉丁美洲這一支及其方法論爭議。⚠️ 黑人神學、女性主義神學也自稱解放神學，"
     "本卡片把它們分別放在「各地的神學」與「性別神學」，因為出發的處境不同"),
    ("gender", "性別神學", "⚧",
     "女性主義、婦女主義（womanist）、拉美裔（mujerista）、酷兒神學，"
     "以及性別議題回到教義學核心的嘗試"),
    ("contextual", "各地的神學", "🌏",
     "按處境分的其餘各支：非洲、亞洲各地、黑人神學、後殖民、原住民、巴勒斯坦、"
     "障礙與生態神學"),
    ("global", "全球神學的嘗試", "🌐",
     "世界基督教研究與「全球神學如何可能」這個問題：可譯性、新的大公性、重心南移及其爭議"),
]

# 館藏區：神學類底下屬於近現代的 subcategory（改革宗／清教徒那一大批歸「基督教研究」卡）
LIBRARY_SUBS = ["近現代著作", "本地化處境神學", "神學詮釋/哲學", "主題專論",
                "倫理神學", "神學家著作與研究", "教科書/概論", "靈修神學"]


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def library_titles(env: dict) -> list[tuple[str, str]]:
    """整個電子圖書館的（題名, 作者），供比對書目用（keyset 分頁，別靠預設 limit）。"""
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": key, "Authorization": f"Bearer {key}"}
    out, off = [], 0
    while True:
        r = requests.get(f'{env["SUPABASE_URL"]}/rest/v1/ebooks', headers=H,
                         params={"select": "title,author", "limit": "1000",
                                 "offset": str(off), "order": "id"}, timeout=90)
        d = r.json()
        if not isinstance(d, list):
            print(f"  ! 查詢失敗 {d}")
            break
        out += [((x.get("title") or "").lower(), (x.get("author") or "").lower()) for x in d]
        if len(d) < 1000:
            break
        off += 1000
    return out


def library_stats(env: dict, subs: list[str]) -> list[dict]:
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows = []
    for sub in subs:
        r = requests.get(f'{env["SUPABASE_URL"]}/rest/v1/ebooks', headers=H,
                         params={"select": "chunk_count", "category": "eq.神學",
                                 "subcategory": f"eq.{sub}", "limit": "5000"}, timeout=60)
        if r.status_code != 200:
            continue
        d = r.json()
        if d:
            rows.append({"name": sub, "books": len(d),
                         "chunks": sum(int(x.get("chunk_count") or 0) for x in d)})
    return sorted(rows, key=lambda x: -x["books"])


def key_words(title: str) -> str:
    """取題名裡最有辨識度的一段拿去比對——整串比對幾乎一定落空（副標、版次、冊數都會差）。"""
    t = re.split(r"[:：(（/]", title)[0]
    t = re.sub(r"[《》\"'’”]", "", t).strip().lower()
    return t


def in_library(b: dict, lib: list[tuple[str, str]]) -> bool:
    """書目的一筆在不在館裡。

    ⚠️ 這個比對有兩個相反的壞法，兩個都會看起來很正常：

    只拿**原文題名**比，會得出「114 本只有 2 本在館」——因為館內題名九成是中文。
    只拿**題名**比，又會把潘能伯格與田立克的《系統神學》判成在館，因為館裡有
    林鴻信那本《系統神學》。前者害我們重抓已有的書，後者害我們以為有而其實沒有。

    所以：題名關鍵詞命中之後，還要作者對得上才算。作者欄空白的（館內不少）
    只有在題名夠獨特（八字以上）時才採信。
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
            "items": items,
        })
        print(f'  {name}：{len(items)} 筆，已入館 {areas[-1]["in_library"]}')

    if GIFFORD.exists():
        g = json.loads(GIFFORD.read_text(encoding="utf-8"))
        areas.append({
            "slug": "gifford", "name": "吉福德講座", "icon": "🎓",
            "desc": "一八八八年起在蘇格蘭四所大學輪流舉辦的自然神學講座，多數講稿後來成書。"
                    "把歷屆名單當書目讀，等於一條橫跨一百四十年的神學與宗教哲學主軸——"
                    "詹姆斯《宗教經驗之種種》、巴特、田立克、尼布爾、鄂蘭、泰勒《世俗時代》都出自這裡。",
            "source": "gifford", "count": g["count"], "speakers": g["speakers"],
        })
        print(f'  吉福德講座：{g["count"]} 場、{g["speakers"]} 位講者')

    parts = library_stats(env, LIBRARY_SUBS)
    areas.append({
        "slug": "library", "name": "館藏當代神學", "icon": "📚",
        "desc": "電子圖書館「神學」類底下屬於近現代的那幾個分類。"
                "⚠️ 館內神學類逾三千本，但九成是改革宗與清教徒文獻（見「基督教研究」卡的宗教改革區），"
                "當代這一段其實很薄——這正是本卡片以策展書目為主的原因。",
        "source": "library",
        "books": sum(p["books"] for p in parts),
        "chunks": sum(p["chunks"] for p in parts),
        "parts": parts,
    })
    print(f'  館藏當代神學：{areas[-1]["books"]} 本、{areas[-1]["chunks"]:,} 段')

    DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"areas": areas}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")

    if args.wanted:
        miss = [b for b in bib if not b["in_library"]]
        with WANTED.open("w", encoding="utf-8") as f:
            for b in miss:
                slug = re.sub(r"[^a-z0-9]+", "-", key_words(b["title"]))[:40].strip("-")
                f.write(json.dumps({
                    "key": f"ct-{b['area']}-{slug}",
                    "query": f"{b['author'].split('(')[0].strip()} {key_words(b['title'])}",
                    "expect": key_words(b["title"]),
                    "who": b["author"],
                    "source": "contemporary-theology",
                    "zh": f"{b['author_zh']}《{b['title_zh']}》",
                }, ensure_ascii=False) + "\n")
        print(f"→ {WANTED}（{len(miss)} 筆缺書）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
