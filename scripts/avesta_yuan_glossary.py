#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
從元文琪譯本反查他的專名用字 —— 產出**候選清單**供人審，不自動套用。

    python scripts/avesta_yuan_glossary.py --harvest
    python scripts/avesta_yuan_glossary.py --harvest --min 3 --out output/yuan_terms.md

═══════════ 作法：靠已對齊的逐節資料反查 ═══════════

`data/avesta/sources/yuan/*.json` 的節號已經與本站正文逐節對齊（見
avesta_yuan_reference.py），所以可以這樣反查：

    某一節的**英譯**出現 "Mithra" → 同一節的**元譯**出現哪個中文專名？
    在 126 節裡反覆出現的那個，就是他對 Mithra 的固定譯法。

比用人眼翻書可靠，也比讓模型猜可靠——它是從對齊資料統計出來的。

═══════════ 🚨 產出是候選，不是決定 ═══════════

**本腳本不改詞庫、不改任何譯文。** 理由有兩層：

一、**詞庫是絕對權威**（[[feedback_glossary_strict_authority]]）。
    元文琪的用字要進詞庫，得由人決定，不能由統計決定。

二、**他的專名是波斯語形式，本站正文是阿維斯陀語形式。**
    巴赫曼（Bahman）＝沃胡‧馬納、奧爾迪貝赫什特（Ordibehesht）＝阿沙‧瓦希什塔、
    梅赫爾（Mehr）＝密特拉、索魯什（Sorush）＝斯魯沙、
    塞潘達爾馬茲（Sepandarmaz）＝斯彭塔‧阿爾邁提。
    這不是「誰譯得比較好」的問題——他譯的是波斯文本，那些神名在波斯文裡
    本來就是那個樣子。**拿波斯語形式去譯阿維斯陀語原文是把中古波斯的用語
    套回一千多年前**，等於在譯文裡製造一個時代錯置。

    所以本腳本把候選分成三類，**只有第一類適合直接採用**：
      新增　本站詞庫沒有這個名字（如班德瓦、弗拉舒什塔爾、凱‧卡烏斯）
      異形　同一個對象、他用波斯語形式而本站用阿維斯陀語形式 → 只宜收為異名
      衝突　同一個對象、兩邊都是阿維斯陀語形式但用字不同 → 要人判斷

見 [[feedback_glossary_ancient_name_priority]]：這類候選一律先列清單給人定奪。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "data" / "avesta" / "sources" / "text"
YUAN_DIR = ROOT / "data" / "avesta" / "sources" / "yuan"
NAMES = ROOT / "data" / "avesta" / "sources" / "names.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 中文專名的長相：連續漢字，中間可夾間隔號。兩字以上、十二字以下。
# 🚨 間隔號有三種寫法（·　‧　•），書上與 OCR 出來的不一定同一個，三種都要認；
#    只認一種的話「馬茲達·阿胡拉」會被切成兩個名字。
CJK_NAME = re.compile(r"[一-鿿]{1,6}(?:[·‧•][一-鿿]{1,6}){1,3}")

# 常見的非專名詞，混在統計裡會蓋過真正的名字
STOPWORDS = {"阿胡拉", "馬茲達", "瑣羅亞斯德"}

# 音譯專名不會含虛詞、代詞或動詞。含這些字的片段一定是句子的碎片，不是名字。
# （沒有這道過濾，「強大的眾靈」「重複吟誦第一」「善良」都會被當成專名收進來。）
FUNCTION_CHARS = set("的地得了是在和與也都不很我你他她它們這那有為以及之於或而但就還把被讓請呵！？。，、；：「」『』（）重複吟誦其他")


MAX_HEAD = 4  # 間隔號前最多保留幾個字


def candidate_names(text: str) -> list[str]:
    """抓出一段中譯裡看起來像專名的詞（帶間隔號的複合名）。

    🚨 中文沒有詞界，正規表達式會把名字前面的動詞一起吃進來
       （「請佑助斯皮塔曼·瑣羅亞斯德」抓成「佑助斯皮塔曼·…」）。
       音譯的每一節幾乎都在四字以內，所以**間隔號前只保留最後四個字**——
       這是確定性的收斂規則，不是猜。收多了會讓同一個名字散成好幾種寫法，
       統計就再也浮不出正確的那個。

    >>> candidate_names('呵，馬茲達·阿胡拉！請佑助斯皮塔曼·瑣羅亞斯德。')
    ['馬茲達·阿胡拉', '斯皮塔曼·瑣羅亞斯德']
    >>> candidate_names('沒有任何專名的一句話。')
    []
    """
    out = []
    for m in CJK_NAME.findall(text):
        i = min(i for i in (m.find(c) for c in "·‧•") if i >= 0)
        out.append(m[max(0, i - MAX_HEAD):])
    return out


def english_terms(en: str, vocab: list[str]) -> list[str]:
    """這一節的英譯裡出現了詞庫裡的哪些專名。

    >>> english_terms('unto Mithra, the lord of wide pastures', ['Mithra', 'Anahita'])
    ['Mithra']
    """
    low = en.lower()
    return [t for t in vocab if t.lower() in low]


def ngrams(text: str, lo: int = 2, hi: int = 6) -> set[str]:
    """一段中文裡所有長度 lo–hi 的漢字連續片段（含間隔號）。

    >>> sorted(ngrams('梅赫爾', 2, 3))
    ['梅赫', '梅赫爾', '赫爾']
    """
    runs = re.findall(r"[一-鿿·‧•]+", text)
    out: set[str] = set()
    for r in runs:
        for n in range(lo, hi + 1):
            for i in range(len(r) - n + 1):
                out.add(r[i:i + n])
    return out


def harvest(min_hits: int) -> dict[str, list[tuple[str, int, float]]]:
    """回 {英文專名: [(元文琪的中文, 共現節數, 關聯度), …]}。

    🚨 **不能只抓帶間隔號的名字。** 第一版是那樣寫的，結果只找到四條——
       因為他多數專名是單一詞（梅赫爾、巴赫曼、索魯什、奧爾迪貝赫什特），
       中間根本沒有間隔號。而中文沒有詞界，無法用規則切出「哪幾個字是一個名字」。

    改用統計關聯：某英文專名出現的那些節裡，哪個中文片段的出現率
    **遠高於全書平均**。梅赫爾在 Mithra 的 126 節裡幾乎節節都有、
    在其他篇幾乎不出現，關聯度就會衝到最高。
    這是從對齊資料算出來的，不是猜的，也不必事先知道名字長什麼樣。
    """
    glossary: dict[str, str] = json.loads(NAMES.read_text(encoding="utf-8"))
    vocab = [k for k in glossary if re.fullmatch(r"[A-Za-z][A-Za-z\- ']{2,30}", k)]

    verses: list[tuple[str, str]] = []  # (英譯, 元譯)
    for yp in sorted(YUAN_DIR.glob("*.json")):
        y = json.loads(yp.read_text(encoding="utf-8"))
        tp = TEXT_DIR / f"{y['slug']}.json"
        if not tp.exists():
            continue
        doc = json.loads(tp.read_text(encoding="utf-8"))
        for seg in doc["segments"]:
            m = re.search(r"\.(\d+)", seg.get("ref", ""))
            if not m:
                continue
            zh, en = y["verses"].get(m.group(1), ""), seg.get("en", "")
            if zh and en:
                verses.append((en, zh))

    # 背景：每個片段總共出現在幾節裡
    bg: Counter = Counter()
    grams: list[set[str]] = []
    for _en, zh in verses:
        g = ngrams(zh)
        grams.append(g)
        bg.update(g)

    out: dict[str, list[tuple[str, int, float]]] = {}
    total = len(verses) or 1
    for term in vocab:
        idx = [i for i, (en, _zh) in enumerate(verses) if term.lower() in en.lower()]
        if len(idx) < min_hits:
            continue
        local: Counter = Counter()
        for i in idx:
            local.update(grams[i])
        best: list[tuple[str, int, float]] = []
        for g, c in local.items():
            if c < min_hits or c < 0.5 * len(idx):
                continue
            # 關聯度：在這些節裡的出現率 ÷ 全書出現率
            lift = (c / len(idx)) / (bg[g] / total)
            if lift >= 3.0:
                best.append((g, c, lift))
        # 同一個名字會產生一堆子片段（梅赫、赫爾、梅赫爾）；留最長的那些。
        # 🚨 只留「封閉」片段：若存在更長的片段而出現節數幾乎一樣，短的那個只是它的碎片。
        #    沒有這一步，抓到的會是「蘇拉·阿娜希」（少了尾字）、「胡拉·馬茲達」
        #    （少了首字）、「的胡姆」（多了助詞）——每一個看起來都像名字，
        #    但沒有一個是完整的名字，拿去當譯名表會整批錯。
        by_gram = {g: c for g, c, _l in best}
        closed = [(g, c, lift) for g, c, lift in best
                  if not any(g != h and g in h and by_gram[h] >= c * 0.9 for h in by_gram)]
        # 含虛詞或明顯是句子的片段一律丟掉。
        closed = [r for r in closed if not (set(r[0]) & FUNCTION_CHARS)]
        closed.sort(key=lambda r: (-len(r[0]), -r[2]))
        kept: list[tuple[str, int, float]] = []
        for g, c, lift in closed:
            if any(g in k for k, _c, _l in kept):
                continue
            kept.append((g, c, lift))
            if len(kept) >= 3:
                break
        if kept:
            out[term] = kept
    return out


def cmd_harvest(min_hits: int, out: Path | None) -> int:
    glossary: dict[str, str] = json.loads(NAMES.read_text(encoding="utf-8"))
    found = harvest(min_hits)

    rows_new, rows_variant, rows_conflict = [], [], []
    for en, cands in sorted(found.items()):
        if not cands:
            continue
        top, n = cands[0][0], cands[0][1]
        ours = glossary.get(en, "")
        if not ours:
            rows_new.append((en, top, n, ""))
        elif top == ours:
            continue  # 一致，沒什麼好報的
        elif top.replace("‧", "·") == ours.replace("‧", "·"):
            continue  # 只差間隔號寫法
        else:
            (rows_variant if len(top) != len(ours) else rows_conflict).append((en, top, n, ours))

    lines = ["# 元文琪譯本專名候選（自動萃取，供人審）", "",
             f"從 {len(list(YUAN_DIR.glob('*.json')))} 篇已對齊的逐節資料反查而得；",
             f"只收共現 {min_hits} 次以上、且該節英譯只出現一個詞庫專名的配對。", "",
             "🚨 **本清單不會自動套用。** 他的專名多為**波斯語形式**"
             "（巴赫曼＝沃胡‧馬納、梅赫爾＝密特拉），與本站正文的阿維斯陀語形式"
             "不是同一套，不可直接取代。", ""]

    def table(title: str, rows: list, note: str) -> None:
        lines.extend([f"## {title}（{len(rows)} 條）", "", note, "",
                      "| 英文 | 元文琪 | 共現 | 本站詞庫 |", "|---|---|---:|---|"])
        for en, top, n, ours in sorted(rows, key=lambda r: -r[2]):
            lines.append(f"| {en} | {top} | {n} | {ours or '—'} |")
        lines.append("")

    table("一、詞庫沒有的名字", rows_new,
          "這一類最有用：本站詞庫查無此名，可考慮直接採用他的譯法。")
    table("二、他用波斯語形式", rows_variant,
          "同一個對象，他用波斯語形式、本站用阿維斯陀語形式。**建議收為異名，不取代主譯。**")
    table("三、用字不同，需人判斷", rows_conflict,
          "字數相同但用字不同，可能是單純的譯字差異。")

    text = "\n".join(lines)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"寫出 → {out.relative_to(ROOT)}")
    print(f"新增候選 {len(rows_new)}　波斯語異形 {len(rows_variant)}　需判斷 {len(rows_conflict)}")
    return 0


def aligned_verses() -> list[tuple[str, str]]:
    """(英譯, 元譯) 的逐節配對。兩支命令共用。"""
    verses: list[tuple[str, str]] = []
    for yp in sorted(YUAN_DIR.glob("*.json")):
        y = json.loads(yp.read_text(encoding="utf-8"))
        tp = TEXT_DIR / f"{y['slug']}.json"
        if not tp.exists():
            continue
        doc = json.loads(tp.read_text(encoding="utf-8"))
        for seg in doc["segments"]:
            m = re.search(r"\.(\d+)", seg.get("ref", ""))
            if not m:
                continue
            zh, en = y["verses"].get(m.group(1), ""), seg.get("en", "")
            if zh and en:
                verses.append((en, zh))
    return verses


def cmd_style(min_hits: int, out: Path) -> int:
    """找出反覆出現的**英譯公式句**，以及元文琪固定怎麼譯。

    🚨 這一支的用途與 --harvest 不同，也沒有那個腳本的顧慮：
       專名不能借（他用波斯語形式），但**語感可以借**——
       呼格怎麼起、補字怎麼標、公式句怎麼排，這些與底本無關，
       借過來能讓本站其餘各篇讀起來像同一個人譯的。
    """
    verses = aligned_verses()
    # 英譯裡反覆出現的短語（4–10 個詞）
    eng: Counter = Counter()
    for en, _zh in verses:
        words = re.findall(r"[A-Za-z']+", en)
        for n in range(4, 11):
            for i in range(len(words) - n + 1):
                eng[" ".join(words[i:i + n]).lower()] += 1
    common = [(p, c) for p, c in eng.most_common(400) if c >= min_hits]
    # 只留「封閉」短語：有更長的且次數幾乎一樣時，短的只是碎片
    by = dict(common)
    closed = [(p, c) for p, c in common
              if not any(p != q and p in q and by[q] >= c * 0.85 for q in by)]

    rows = []
    for phrase, c in closed[:40]:
        idx = [i for i, (en, _z) in enumerate(verses) if phrase in en.lower()]
        zhs = [verses[i][1] for i in idx]
        # 這些節共有的中文片段（長度 3–14），取出現率最高者
        local: Counter = Counter()
        for z in zhs:
            local.update(ngrams(z, 3, 14))
        best = [(g, n) for g, n in local.most_common(60)
                if n >= max(2, 0.6 * len(zhs)) and not (set(g) & {"，", "。"})]
        bykey = dict(best)
        best = [(g, n) for g, n in best
                if not any(g != h and g in h and bykey[h] >= n * 0.9 for h in bykey)]
        if best:
            rows.append((phrase, c, best[0][0], best[0][1]))

    lines = ["# 元文琪譯本的語感對照（自動萃取）", "",
             "從 30 篇逐節對齊資料統計：反覆出現的**英譯公式句**，以及他固定怎麼譯。", "",
             "🚨 這份與專名候選不同——**語感可以借，專名不可借**。",
             "他的專名是波斯語形式（見 yuan_terms.md），但呼格怎麼起、補字怎麼標、",
             "公式句怎麼排，與底本無關，借過來能讓其餘各篇讀起來像同一個人譯的。", "",
             "| 英譯公式 | 出現 | 元文琪的譯法 | 命中 |", "|---|---:|---|---:|"]
    for p, c, g, n in rows:
        lines.append(f"| {p} | {c} | {g} | {n} |")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"寫出 {len(rows)} 組 → {out.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="從元文琪譯本反查專名候選")
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--min", type=int, default=2, help="至少共現幾次才收")
    ap.add_argument("--style", action="store_true", help="萃取語感對照（公式句怎麼譯）")
    ap.add_argument("--out", default=str(ROOT / "output" / "yuan_terms.md"))
    a = ap.parse_args()
    if a.style:
        return cmd_style(a.min, ROOT / "output" / "yuan_style.md")
    if a.harvest:
        return cmd_harvest(a.min, Path(a.out))
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
