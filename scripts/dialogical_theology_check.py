# -*- coding: utf-8 -*-
"""《諸宗教的對話神學》初稿品管閘。

機器寫的初稿最危險的不是寫得爛——爛看得出來——而是**看起來完全正常但內容錯位**：
卷名被自己改掉、例子照抄前一章、整章其實在寫別章的題目、或者開頭全部長一個樣。
這些在單章閱讀時毫無異狀，只有攤開全書比對才看得見。本檔就是做那個比對。

七項檢查：
  1. 格式      —— <section class="chapter"> 開頭、</section> 結尾、h2 標題與綱要相符
  2. 長度      —— 低於 6000 字視為沒寫完
  3. 禁止元素  —— 註釋、上標、參考書目（人手寫的 D1:1 例外）
  4. 捏造書目  —— 「出版社／年份／頁碼」樣式的字串（初稿階段一律不該有）
  5. 卷名幻覺  —— 「卷N《X》」的 X 與綱要對不上
  6. 抄範例    —— 整組沿用卷一第一章那個台灣餐桌場景（單一詞不算，兩個以上標記才算）
  6b. 填充語   —— 「你或許」「值得注意的是」這類 LLM 口頭禪，prompt 禁了但守不牢
  7. 開頭雷同  —— 各章前 60 字互相比對，太像表示模型在套同一個模板

  python -X utf8 scripts/dialogical_theology_check.py
  python -X utf8 scripts/dialogical_theology_check.py --volume D3
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

OUTLINE = ROOT / "scripts/data/dialogical_theology_outline.json"
BASE = ROOT / "public/content/works/dialogical-theology"
MIN_CHARS = 6000
HANDWRITTEN = {("D1", 1)}          # 人手寫的，帶註釋是正常的

# 🚨 只抓「書目樣式」，不要抓到普通詞。第一版拿「終極實在論」當卷名幻覺的關鍵詞，
#    結果把「其終極實在論的宣稱」這種正常片語全報成錯——粗糙的檢查比沒有檢查更糟，
#    因為它會訓練人忽略警告。
_CITE = re.compile(r"(出版社|Press|大學出版|頁\s*\d+|第\s*\d+\s*頁|pp?\.\s*\d+|,\s*(19|20)\d\d[.);])")
_VOLREF = re.compile(r"卷([一二三四五六七])《([^》]{1,12})》")
# 🚨 單一詞不能當「抄範例」的判準：「地基主」出現在講鬼神那一章是恰當用例，不是抄。
#    要抓的是那個**場景**被整組搬走，所以改成兩個以上標記同時出現才算。
_SAMPLE_MARKS = ("天公伯仔", "地基主", "長老教會的會友", "初一十五", "擲筊")
_FILLER = re.compile(r"你或許|你會發現|你可能|想像一下|值得注意的是|我們可以說|不難發現")


def text_of(html: str) -> str:
    return re.sub(r"\s", "", re.sub(r"<[^>]+>", "", html))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume")
    a = ap.parse_args()

    book = json.loads(OUTLINE.read_text(encoding="utf-8"))
    titles = {v["no"]: v["title"] for v in book["volumes"]}

    problems: list[str] = []
    openings: list[tuple[str, str]] = []
    total = chars = 0

    for vol in book["volumes"]:
        if a.volume and vol["id"] != a.volume:
            continue
        d = BASE / f"chapters-{vol['id'].lower()}"
        missing = []
        for ch in vol["chapters"]:
            f = d / f"ch{ch['n']:02d}.html"
            tag = f"{vol['id']}:{ch['n']:02d}"
            if not f.exists():
                missing.append(str(ch["n"]))
                continue
            s = f.read_text(encoding="utf-8")
            t = text_of(s)
            total += 1
            chars += len(t)

            if not s.startswith('<section class="chapter">'):
                problems.append(f"{tag} 開頭不是 <section class=\"chapter\">")
            if "</section>" not in s:
                problems.append(f"{tag} 沒有結尾 </section>")
            h2 = re.search(r"<h2>([^<]+)</h2>", s)
            if not h2:
                problems.append(f"{tag} 找不到 <h2>")
            elif ch["title"] not in h2.group(1):
                problems.append(f"{tag} 標題對不上綱要：{h2.group(1)!r} ≠ {ch['title']!r}")
            if len(t) < MIN_CHARS:
                problems.append(f"{tag} 只有 {len(t):,} 字")
            if (vol["id"], ch["n"]) not in HANDWRITTEN:
                if re.search(r"<sup|參考資料|參考書目", s):
                    problems.append(f"{tag} 混進了註釋或參考書目")
                m = _CITE.search(t)
                if m:
                    problems.append(f"{tag} 疑似捏造書目：…{t[max(0,m.start()-25):m.end()+15]}…")
            for no, name in _VOLREF.findall(t):
                if titles.get(no) and name != titles[no]:
                    problems.append(f"{tag} 卷名錯：寫成卷{no}《{name}》，應為《{titles[no]}》")
            if (vol["id"], ch["n"]) != ("D1", 1):
                hit = [k for k in _SAMPLE_MARKS if k in t]
                if len(hit) >= 2:
                    problems.append(f"{tag} 整組沿用卷一第一章的場景：{'、'.join(hit)}")
                fillers = sorted(set(_FILLER.findall(t)))
                if fillers:
                    problems.append(f"{tag} 有填充語：{'、'.join(fillers)}")
            openings.append((tag, t[:60]))
        if missing:
            problems.append(f"{vol['id']} 缺章：{'、'.join(missing)}")

    # 開頭雷同：模型套模板時，各章前幾句會長得極像
    for i, (ta, oa) in enumerate(openings):
        for tb, ob in openings[i + 1:]:
            r = difflib.SequenceMatcher(None, oa, ob).ratio()
            if r > 0.6:
                problems.append(f"{ta} 與 {tb} 開頭雷同（{r:.0%}）")

    print(f"檢查 {total} 章，共 {chars:,} 字"
          f"{f'，平均 {chars//total:,} 字' if total else ''}")
    if problems:
        print(f"\n發現 {len(problems)} 個問題：")
        for p in problems:
            print("  ⚠", p)
        sys.exit(1)
    print("✓ 七項檢查全過")


if __name__ == "__main__":
    main()
