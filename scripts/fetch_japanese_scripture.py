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
# 維基文庫的文語訳是「一卷一頁」，頁內用 `== 第N章 ==` 分章——比逐章頁好用：
# 抓一次就有整卷，章是它自己的分段，不必我來切。頁名的寫法不一致（伝／傳、
# 括號前有沒有空格），所以每卷列幾個候選寫法，取第一個抓得到內容的。
BIBLE_BOOKS = [
    (["創世記(文語訳)", "創世記 (文語訳)"], "創世記", "舊約"),
    (["出エジプト記(文語訳)", "出エジプト記 (文語訳)"], "出埃及記", "舊約"),
    (["詩篇(文語訳)", "詩篇 (文語訳)"], "詩篇", "舊約"),
    (["イザヤ書(文語訳)", "イザヤ書 (文語訳)"], "以賽亞書", "舊約"),
    (["マタイ傳福音書(文語訳)", "マタイ伝福音書 (文語訳)"], "馬太福音", "新約"),
    (["マルコ傳福音書 (文語訳)", "マルコ傳福音書(文語訳)"], "馬可福音", "新約"),
    (["ルカ傳福音書(文語訳)", "ルカ傳福音書 (文語訳)"], "路加福音", "新約"),
    (["ヨハネ傳福音書(文語訳)", "ヨハネ傳福音書 (文語訳)"], "約翰福音", "新約"),
    (["使徒行傳(文語訳)", "使徒行傳 (文語訳)"], "使徒行傳", "新約"),
    (["ロマ書(文語訳)", "ロマ書 (文語訳)"], "羅馬書", "新約"),
    (["コリント前書(文語訳)", "コリント前書 (文語訳)"], "哥林多前書", "新約"),
    (["ガラテヤ書(文語訳)", "ガラテヤ書 (文語訳)"], "加拉太書", "新約"),
    (["ヨハネ黙示録(文語訳)", "ヨハネ黙示録 (文語訳)"], "啟示錄", "新約"),
]

CHAPTER_HEAD = re.compile(r"^==+\s*第\s*(\d+)\s*章\s*==+$", re.M)

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


def split_chapters(text: str) -> dict[int, str]:
    """One book page, cut at its own `== 第N章 ==` headings."""

    marks = [(m.start(), m.end(), int(m.group(1))) for m in CHAPTER_HEAD.finditer(text)]
    chapters: dict[int, str] = {}
    for index, (_, end, number) in enumerate(marks):
        stop = marks[index + 1][0] if index + 1 < len(marks) else len(text)
        body = clean(text[end:stop])
        if len(body) > 120:
            chapters[number] = body
    return chapters


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--delay", type=float, default=6.0)
    args = parser.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}

    print(f"文語訳 {len(BIBLE_BOOKS)} 卷、佛典 {len(BUDDHIST)} 篇")
    if not args.write:
        print("（未下載；加 --write）")
        return 0

    for titles, zh, testament in BIBLE_BOOKS:
        if any(key.startswith(f"bible:{zh}:") for key in manifest):
            continue
        raw = None
        used = ""
        for title in titles:
            try:
                raw = api_extract(title)
            except Exception as error:  # noqa: BLE001
                print(f"  ✗ {title}：{error}")
                raw = None
            time.sleep(args.delay)
            if raw:
                used = title
                break
        if not raw:
            print(f"  ✗ {zh}：候選頁名都抓不到")
            continue
        chapters = split_chapters(raw)
        if not chapters:
            print(f"  ✗ {zh}：抓到頁面但切不出章（{len(raw)} 字）")
            continue
        for number, body in chapters.items():
            path = CACHE / f"bible_{zh}_{number:03d}.txt"
            path.write_text(body, encoding="utf-8")
            manifest[f"bible:{zh}:{number}"] = {
                "titleZh": f"{zh} {number}",
                "kind": "章",
                "group": "bible",
                "testament": testament,
                "chars": len(body),
                "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sourceUrl": f"https://ja.wikisource.org/wiki/{urllib.parse.quote(used)}",
                "rightsChecked": True,
                "rightsNote": "文語訳（明治元訳舊約／大正改訳新約），公有領域",
            }
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  ✓ {zh}：{len(chapters)} 章（{used}）")

    for title, zh, kind in BUDDHIST:
        if title in manifest:
            continue
        try:
            raw = api_extract(title)
        except Exception as error:  # noqa: BLE001
            print(f"  ✗ {title}：{error}")
            time.sleep(args.delay)
            continue
        time.sleep(args.delay)
        if not raw:
            print(f"  ✗ {title}：維基文庫沒有這一頁")
            continue
        body = clean(raw)
        if len(body) < 200:
            print(f"  ✗ {title}：內容太短（{len(body)} 字）")
            continue
        path = CACHE / f'{re.sub(r"[^0-9A-Za-zぁ-ゖァ-ヺ一-鿿]", "_", title)}.txt'
        path.write_text(body, encoding="utf-8")
        manifest[title] = {
            "titleZh": zh,
            "kind": kind,
            "group": "buddhist",
            "chars": len(body),
            "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sourceUrl": f"https://ja.wikisource.org/wiki/{urllib.parse.quote(title)}",
            "rightsChecked": False,
            "rightsNote": "訓讀／現代語譯各有譯者，收入前須逐篇查證譯者與年份",
        }
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  ✓ {title} — {zh}（{len(body):,} 字）")

    total = sum(item["chars"] for item in manifest.values())
    unchecked = [t for t, v in manifest.items() if not v["rightsChecked"]]
    print(f"完成 {len(manifest)} 篇，合計 {total:,} 字")
    if unchecked:
        print(f"  ⚠ 權利未查證 {len(unchecked)} 篇，入書前逐篇確認訓讀者")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
