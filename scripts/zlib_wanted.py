#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把各處的「想要的書」彙整成一份 zlib_fetch 吃得下的清單。

三個來源：
  1. data/zlib-wanted/*.jsonl —— 人工策展的主題書單（聖經研究、基督教史、神學方法
     論、宗教學、宗教史、佛教與性別、佛教史、佛學、佛典考據與批判研究，以及小黑書
     那一系列的英文原著）。這些直接就是目標格式。
  2. .claude/skills/ebook-collected-works/z-library_獵表_全集中譯.txt —— 全集作家
     尚未收錄的著作（1,100 餘筆），找的是**中譯本**。
  3. 同資料夾的 基督宗教研究_中譯獵表.txt —— 同格式。

輸出 output/zlib_wanted_all.jsonl（中繼，不進版控），交
`node scripts/zlib_fetch.mjs --list` 逐日消化。

  python scripts/zlib_wanted.py                # 產生合併清單
  python scripts/zlib_wanted.py --stats        # 只看統計
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import author_blacklist

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "zlib-wanted"
SKILL = ROOT / ".claude" / "skills" / "ebook-collected-works"
HUNT_FILES = [
    (SKILL / "z-library_獵表_全集中譯.txt", "collected-works-hunt"),
    (SKILL / "基督宗教研究_中譯獵表.txt", "christianity-studies-hunt"),
]
OUT = ROOT / "output" / "zlib_wanted_all.jsonl"

# 一天只抓得到十本，六千多筆照雜湊亂序排等於永遠輪不到正在寫的那幾本。
# 排序依據是「為什麼現在需要這本書」——有時程壓力的排前面：
#    3 本學期正在上的課的講義（每週一次，期限最硬）
#    5 本學期修課的指定用書（每週要讀）
#   10 學位論文（送件有期限）
#   15 正在轉錄的全集主線缺的上游專書（缺它，那條線這週就卡住）
#   20 正在轉錄的全集次線
#   30 正在動筆／待補註釋的書稿
#   40 長期改寫輪（沒有硬期限）
#   45 全集獵表（整組一千多筆，靠 FOCUS_AUTHORS 逐位插隊，不整批往前）
#   60 主題策展書單（想讀，但不擋任何進度）
# 數字留空隙，之後插新計畫不必重排。
#
# 2026-09-10 重排。改動的理由，逐條記在下面——這張表沒有註記就會退化成憑印象排。
PRIORITY = {
    # 開學了。四門課每週要上，講義的參考書從「開課前備齊」變成「這週就要用」，
    # 所以從 20 提到 3。原本 christianity-intro 與 sinographic-literature 排在
    # 第 152／153 本，前面壓著三份各上千筆的長期清單，一本都還沒輪到過。
    "biblio-christianity-intro": 3,
    "biblio-world-religions-intro": 3,
    "biblio-sinographic-literature": 3,
    "relstudy-course-hcu": 5,          # 12/12 已清空，留著給下學期換書用
    "biblio-hcu-phd": 10,              # 115/251，送件有期限，維持原級
    # 內村鑑三／矢內原忠雄那條全集線正在跑（10 卷有 8 卷過九成），缺的是研究它們
    # 的上游專書。兩份加起來只有 11 筆，一天就消化完，卻原本排在第 1,700／4,081
    # 本——等於永遠拿不到。這種「量小但正擋著工作」的清單就該提到最前面。
    "religious-studies-originals": 12,   # 宗教學者原著缺口，使用者 2026-09-11 點名優先
    "uchimura-biography": 15,
    "mukyokai-studies": 15,
    "mukyokai-chinese-translations": 15,   # REFERENCE-first：有中譯本就不自譯
    # 昭慧法師全集是第一個只有紙本掃描本的來源，正在 OCR；八敬法與印順／聖嚴
    # 是它的研究上游。原本排第 1,486 本（約 50 天後）。
    "biblio-bajingfa": 20,
    "biblio-yinshun-shengyan": 20,
    # 動筆中或待補註釋的書稿。《神學研究宣言》十二章目已備、正文未寫；
    # 《諸宗教的對話神學》84 章初稿完成但一條註釋都還沒有。
    "biblio-theological-studies-manifesto": 30,
    "biblio-mahaprajapati-revolution": 30,
    "biblio-pong-pastoral-spirituality": 30,
    # 創生哲學 15 卷正文已完工，現在是現象學改寫輪，沒有硬期限；但它一家 1,806 筆
    # 佔了整個佇列三分之一，擺在 40 以上會把上面每一層都餓死。
    "biblio-genesis-philosophy": 40,
    # 獵表兩份合計 1,223 筆、285 位作家。整組往前會淹掉佇列，所以留在低層，
    # 要哪一位就寫進 FOCUS_AUTHORS 插隊。
    "collected-works-hunt": 45,
    "collected-works-zh": 45,
    "christianity-studies-hunt": 45,
    "biblio-bachelor-evangelical": 50,
}
DEFAULT_PRIORITY = 60

# 正在做的那位全集作家，插到所有層之前。
#
# 為什麼要有這一條：PRIORITY 是「按來源」分層的，可是 collected-works-hunt 一個來源
# 就有 1,193 筆、285 位作家，整組提上來會把佇列淹掉；不提上來又全部落在最低層 60，
# 照現在一天十本的速度，指定「先做某某人」等於沒說——伊利亞德那 6 筆原本排在第
# 597 筆，而帳本才走到 167 筆。
#
# 所以插隊的單位是**作家**不是來源。填 who 欄位會出現的字串（中文名或英文姓皆可，
# 大小寫不拘、比對用包含）。做完一位就把他移掉，不要放著累積——留著等於沒有優先序。
FOCUS_AUTHORS = [
    "伊利亞德",   # 2026-09-08 宗教學全集主打；09-10 已下 6 本，剩下的多是同書異名
    "Eliade",
    # 赤江達也：2026-09-10 兩筆都回「沒有對得上的版本」，站上就是沒有，留著只會
    # 每天白花兩次搜尋。要它得走別的來源（NDL／日本古書店），不是 z-lib。
]


def _is_focus(it: dict) -> bool:
    hay = f"{it.get('who', '')} {it.get('zh', '')} {it.get('query', '')}".lower()
    return any(a.lower() in hay for a in FOCUS_AUTHORS)


# 每一輪各層分到幾個名額。層數愈小拿愈多，但沒有一層是零——
#
# 🚨 2026-09-10 從「嚴格層序」改成加權輪流。原本是把整層清空才輪到下一層，
# 結果是：把本學期三份講義書單（合計 1,337 筆）提到最前面之後，博班論文計畫
# 那 136 筆立刻被推到第 1,350 本、四十五天後才輪得到。一天只有幾十本額度時，
# 嚴格層序等於「除了第一名，其他全部餓死」，而實際需求從來不是「先把講義全部
# 拿齊」，是「每條活線每天都要有進帳」。
#
# 一輪 27 筆，對上三個帳號一天 30 本的天花板，大致就是一天的份。
TIER_QUOTA = {0: 8, 3: 6, 5: 6, 10: 4, 15: 3, 20: 2, 30: 2, 40: 1, 45: 1, 50: 1, 60: 1}
DEFAULT_QUOTA = 1


def prioritize(items: list[dict]) -> list[dict]:
    """依 PRIORITY 分層，各層按 TIER_QUOTA 加權輪流，層內在各來源之間輪流取。

    FOCUS_AUTHORS 命中的整批歸到第 0 層（拿最多名額，但不再獨佔整個佇列頭）。

    層內輪流是刻意的：genesis-philosophy 一家就佔了三分之一，照來源整批排會讓
    它獨吞好幾個月的額度，其餘計畫全部餓死。

    🚨 同一本書的兩格是「原文先、中譯後」，這一點跟直覺相反，是實測改過來的。
    原本讓中譯排前面（使用者讀中文最快），結果 2026-09-06 那一輪 21 次嘗試只
    下載 2 本、18 次「沒有對得上的版本」—— 西方近人學術著作多半沒有中譯本，
    語言閘正確地擋掉英文版而空手回來，於是每日額度全耗在必然落空的目標上。
    原文先抓，中譯那一格排在後面慢慢碰；晚幾天拿到中譯不影響閱讀，抓不到書才影響。
    """
    from collections import defaultdict, deque

    buckets: dict[int, dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
    for it in items:
        src = it.get("source", "")
        # 同一本書的兩格：-orig 先、-zh 後（理由見 docstring）
        lvl = 0 if _is_focus(it) else PRIORITY.get(src, DEFAULT_PRIORITY)
        buckets[lvl][src].append(it)
    for tier in buckets.values():
        for src, q in tier.items():
            ordered = sorted(q, key=lambda x: (1 if x["key"].endswith("-zh") else 0, x["key"]))
            tier[src] = deque(ordered)

    # 每層一個游標，記住上一輪停在哪個來源。
    #
    # 🚨 沒有游標的話，每一輪都從該層第一個來源重新數，而一輪只取 n 筆——
    # 第 60 層有 12 份書單、配額 1，等於永遠只餵第一份，其餘十一份要等它整份
    # 抽乾才輪得到（實測 zoroastrian-studies 排到第 3,053 本）。層內輪流要跨輪
    # 才成立。
    cursor: dict[int, int] = defaultdict(int)

    def take(lvl: int, n: int) -> list[dict]:
        """從某一層取最多 n 筆，層內在各來源之間輪流（跨輪接續）。"""
        tier = buckets[lvl]
        srcs = list(tier)
        got: list[dict] = []
        misses = 0
        while len(got) < n and misses < len(srcs):
            s = srcs[cursor[lvl] % len(srcs)]
            cursor[lvl] += 1
            if tier[s]:
                got.append(tier[s].popleft())
                misses = 0
            else:
                misses += 1
        return got

    out: list[dict] = []
    levels = sorted(buckets)
    while any(any(buckets[l][s] for s in buckets[l]) for l in levels):
        for lvl in levels:
            out.extend(take(lvl, TIER_QUOTA.get(lvl, DEFAULT_QUOTA)))
    return out

_AUTHOR_RE = re.compile(r"^\s*▍\s*(.+?)\s*(?:\((.+?)\))?\s*(?:約?\s*[前\d].*)?$")
_WANT_RE = re.compile(r"^\s*\[需獵\]\s*《(.+?)》(?:\s*（(.+?)）)?")
# 基督宗教研究那份是另一種排版：一行一本，[領域] 作者｜《書名》 譯者 / 出版社
_CHR_RE = re.compile(r"^\[(?P<field>[^\]]+)\]\s*(?P<author>[^｜|]+)[｜|]\s*《(?P<title>[^》]+)》")


def _stable_key(*parts: str) -> str:
    """内建 hash() 每次執行的結果都不一樣（PYTHONHASHSEED 隨機），拿來當帳本的鍵
    等於每天重抓同一批書。要用穩定雜湊。"""
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]


def parse_hunt(text: str, source: str) -> list[dict]:
    """獵表 txt → 目標格式。作家行以 ▍ 起頭，其下的 [需獵] 行是要找的書。"""
    out: list[dict] = []
    author_zh, author_en = "", ""
    for line in text.splitlines():
        if line.lstrip().startswith("▍"):
            m = _AUTHOR_RE.match(line)
            if m:
                author_zh = (m.group(1) or "").strip()
                author_en = (m.group(2) or "").strip()
            continue
        m = _WANT_RE.match(line)
        if not m or not author_zh:
            continue
        title_zh = m.group(1).strip()
        title_orig = (m.group(2) or "").strip()
        key = "hunt-" + _stable_key(author_zh, title_zh)
        out.append({
            "key": key,
            # 找的是中譯本，所以用中文書名＋作者名去搜
            "query": f"{title_zh} {author_zh}".strip(),
            "expect": title_zh,
            "who": author_zh,
            "source": source,
            "zh": f"{author_zh}《{title_zh}》",
            **({"orig": title_orig} if title_orig else {}),
        })
    return out


def parse_christianity(text: str, source: str) -> list[dict]:
    """基督宗教研究獵表 → 目標格式。這份的重點是「有沒有中譯本」，所以照樣搜中文。"""
    out: list[dict] = []
    for line in text.splitlines():
        m = _CHR_RE.match(line)
        if not m:
            continue
        author = re.sub(r"（.*?）", "", m.group("author")).strip()
        title = m.group("title").strip()
        out.append({
            "key": "chr-" + _stable_key(author, title),
            "query": f"{title} {author}".strip(),
            "expect": title,
            "who": author,
            "source": source,
            "zh": f"{author}《{title}》",
            "field": m.group("field"),
        })
    return out


def _t2s():
    """繁→簡轉換器；沒裝 opencc 就回 None（比對退回只比繁體，不會壞掉）。"""
    try:
        import opencc
    except ImportError:
        return None
    return opencc.OpenCC("t2s")


_T2S = _t2s()


def add_simplified(items: list[dict]) -> list[dict]:
    """替每一筆補上書名與作者的簡體版（expect_s／who_s）。

    🚨 這不是為了寫進資料庫——repo 一切中文都必須是繁體，這兩欄只給 zlib_fetch
    的比對用。z-library 的中文藏書幾乎全是簡體，而我們的清單一律繁體，沒有這一
    層「心靈的黑夜」永遠對不上站上的「心灵的黑夜」。2026-09-10 抽樣四十筆，
    命中率只有 2.5%，而落空的裡面至少三本站上明明就有，差的只是字體。
    """
    if _T2S is None:
        return items
    for it in items:
        for src, dst in (("expect", "expect_s"), ("who", "who_s")):
            v = it.get(src) or ""
            if not v:
                continue
            s = _T2S.convert(v)
            if s != v:                 # 一模一樣就不佔欄位
                it[dst] = s
    return items


def ledger_done() -> set[str]:
    """帳本裡已處理的 key。與 zlib_fetch.mjs 的 doneKeys() 同一套規則——
    🚨 --dry-run 寫進去的那些不算數，否則試跑一次就把清單永久封死。"""
    led = ROOT / "scripts" / "state" / "zlib_ledger.jsonl"
    if not led.exists():
        return set()
    out = set()
    for line in led.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("key") and r.get("status") != "dry":
            out.add(r["key"])
    return out


def load_curated() -> list[dict]:
    out = []
    for f in sorted(CURATED.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    items = load_curated()
    for path, source in HUNT_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        items += parse_hunt(text, source) + parse_christianity(text, source)

    # 帳本裡已經處理過的（抓到、或查無）先扣掉再排。
    #
    # 🚨 這一步不能省。配額是按「清單裡的位置」發的，已處理的那些仍然佔著位置，
    # 於是 biblio-hcu-phd 明明只剩 136 筆、又在第 10 層，卻因為前面 115 筆早就
    # 抓完而把它自己的名額用光，下一本新書要等到第 346 順位。fetch 端本來就會
    # 跳過它們（不花額度），所以濾掉純粹是讓配額對「還沒抓的」生效。
    done = ledger_done()
    seen, merged, banned = set(), [], []
    for it in items:
        if it["key"] in seen or it["key"] in done:
            continue
        seen.add(it["key"])
        # 使用者判定不值得讀的作者，連搜都不要搜（data/author-blacklist.json）
        hit = author_blacklist.match(it.get("who", ""), it.get("zh", ""), it.get("query", ""))
        if hit:
            banned.append((hit["name"], it.get("zh") or it.get("query", "")))
            continue
        merged.append(it)

    by_source: dict[str, int] = {}
    for it in merged:
        by_source[it["source"]] = by_source.get(it["source"], 0) + 1
    for s, n in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {s:28} {n:5}")
    print(f"  {'合計':28} {len(merged):5}")
    if banned:
        print(f"\n  黑名單濾掉 {len(banned)} 筆：")
        for who, what in banned[:10]:
            print(f"    [{who}] {what}")
        if len(banned) > 10:
            print(f"    …另 {len(banned) - 10} 筆")

    if a.stats:
        return
    merged = add_simplified(prioritize(merged))
    print("\n排序後前 12 筆（先做的）：")
    for it in merged[:12]:
        print(f"  [{it.get('source', '')[:28]:28}] {it.get('zh') or it.get('query', '')[:46]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for it in merged:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
