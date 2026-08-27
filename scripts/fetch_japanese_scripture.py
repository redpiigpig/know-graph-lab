#!/usr/bin/env python3
"""Fetch the Bible and Buddhist texts the Japanese reader is required to carry.

The owner asked for 聖經與佛經的常用語句 on top of the religious-studies prose,
and the corpus survey showed why that is not just a nicety: 青空文庫 gives 334
eligible passages but they are almost all folklore and philosophy, and both
volumes come up short of their fifty readings. Scripture fills the gap with
exactly the register the reader is for.

**Bible — 文語訳 only.** The 1887 舊約 and 1917 新約改訳 are public domain; the
口語訳 (1954/55) and 新共同訳 (1987) are not, and 內村鑑三 and 矢內原忠雄 quote
the 文語訳 anyway, so the reader's Bible and its prose agree. Fetched from
Japanese Wikisource, which carries the 文語訳 text.

**Buddhist texts — the words themselves are ancient, the 訓讀 is not.** A
訓讀 or a 現代語訳 has its own translator and its own term, which is why each
piece here records where its reading came from and is marked
``rightsChecked: false`` until someone has looked. Do not let 「佛典是古籍」
stand in for that check — that is the shortcut the contract's stop conditions
name.

    python -X utf8 scripts/fetch_japanese_scripture.py            # 看清單
    python -X utf8 scripts/fetch_japanese_scripture.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full/scripture"
MANIFEST = CACHE / "manifest.json"

API = "https://ja.wikisource.org/w/api.php"
HEADERS = {"User-Agent": "know-graph-lab private reader build (contact: redpiigpig)"}

# 文語訳聖書：福音書、使徒行傳、保羅書信的主要幾卷，加上詩篇與創世記。
# 內村與矢內原引得最多的就是這幾卷。
# 文語訳聖書。維基文庫把它切成一章一頁——對這本讀本正好，因為一章就是文本
# 自己的一個完整段落，不必再切。頁名格式是「マタイ伝福音書-第五章 (文語訳)」。
# 選的是內村鑑三與矢內原忠雄講得最多、以及初學者最先讀的那些章。
CHAPTER_NUMERALS = {
    1: "一", 3: "三", 5: "五", 6: "六", 7: "七", 8: "八", 13: "十三", 15: "十五",
    23: "二十三", 51: "五十一", 53: "五十三", 90: "九十", 121: "百二十一",
}

BIBLE_CHAPTERS = [
    ("マタイ伝福音書", "馬太福音", [5, 6, 7, 13]),
    ("マルコ伝福音書", "馬可福音", [1]),
    ("ルカ伝福音書", "路加福音", [15]),
    ("ヨハネ伝福音書", "約翰福音", [1, 3, 15]),
    ("使徒行伝", "使徒行傳", [1]),
    ("ロマ書", "羅馬書", [8]),
    ("コリント前書", "哥林多前書", [13, 15]),
    ("ガラテヤ書", "加拉太書", [5]),
    ("ヨハネ黙示録", "啟示錄", [21]),
    ("創世記", "創世記", [1, 3]),
    ("詩篇", "詩篇", [23, 51, 90, 121]),
    ("イザヤ書", "以賽亞書", [53]),
]

BIBLE = [
    (f"{book}-第{CHAPTER_NUMERALS.get(chapter, chapter)}章 (文語訳)", f"{zh} {chapter}", "章")
    for book, zh, chapters in BIBLE_CHAPTERS
    for chapter in chapters
    if chapter in CHAPTER_NUMERALS
]

# 佛典：頁名是搜出來的，不是猜的。訓讀的權利狀態要逐篇確認。
BUDDHIST = [
    ("般若心経", "般若心經", "經"),
    ("観音経", "觀音經（普門品）", "經"),
    ("仏説阿弥陀経", "佛說阿彌陀經", "經"),
    ("正信念仏偈", "正信念佛偈", "偈"),
    ("歎異抄 (意訳聖典)", "歎異抄", "論"),
    ("十七条憲法", "十七條憲法", "史料"),
    ("立誓願文", "立誓願文", "願文"),
]


def api_extract(title: str) -> str | None:
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "titles": title,
            "format": "json",
            "redirects": 1,
        }
    )
    request = urllib.request.Request(f"{API}?{query}", headers=HEADERS)
    payload = json.loads(urllib.request.urlopen(request, timeout=90).read().decode("utf-8"))
    pages = payload.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" in page:
            return None
        text = page.get("extract", "")
        return text or None
    return None


def clean(text: str) -> str:
    # Wikisource keeps its own navigation headings; the running text is what is
    # left once those and the empty lines go.
    text = re.sub(r"^=+\s*[^=\n]+\s*=+$", "", text, flags=re.M)
    text = re.sub(r"\[\d+\]", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    plan = [(t, zh, kind, "bible") for t, zh, kind in BIBLE] + [
        (t, zh, kind, "buddhist") for t, zh, kind in BUDDHIST
    ]
    print(f"要抓 {len(plan)} 篇：文語訳聖書 {len(BIBLE)}、佛典 {len(BUDDHIST)}")

    if not args.write:
        for title, zh, kind, group in plan:
            print(f"  [{group}] {title} — {zh}（{kind}）")
        print("（未下載；加 --write）")
        return 0

    CACHE.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}

    for title, zh, kind, group in plan:
        if title in manifest:
            continue
        try:
            raw = api_extract(title)
        except Exception as error:  # noqa: BLE001 - re-runnable
            print(f"  ✗ {title}：{error}")
            continue
        if not raw:
            print(f"  ✗ {title}：維基文庫沒有這一頁")
            continue
        body = clean(raw)
        if len(body) < 200:
            print(f"  ✗ {title}：抓到的內容太短（{len(body)} 字），可能只是目錄頁")
            continue
        path = CACHE / f'{re.sub(r"[^0-9A-Za-zぁ-ゖァ-ヺ一-鿿]", "_", title)}.txt'
        path.write_text(body, encoding="utf-8")
        manifest[title] = {
            "titleZh": zh,
            "kind": kind,
            "group": group,
            "chars": len(body),
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sourceUrl": f"https://ja.wikisource.org/wiki/{urllib.parse.quote(title)}",
            # 文語訳聖書是公有領域；佛典的訓讀各有譯者，未查證前不得當成公有領域。
            "rightsChecked": group == "bible",
            "rightsNote": (
                "文語訳（1887 舊約／1917 新約改訳），公有領域"
                if group == "bible"
                else "訓讀／現代語譯各有譯者，收入前須逐篇查證譯者與年份"
            ),
        }
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  ✓ {title} — {zh}（{len(body):,} 字）")
        time.sleep(3.0)

    total = sum(item["chars"] for item in manifest.values())
    unchecked = [t for t, v in manifest.items() if not v["rightsChecked"]]
    print(f"完成 {len(manifest)} 篇，合計 {total:,} 字")
    if unchecked:
        print(f"  ⚠ 權利未查證 {len(unchecked)} 篇，入書前逐篇確認訓讀者：")
        for title in unchecked:
            print(f"      {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
