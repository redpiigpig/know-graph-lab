#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""電子圖書館外文書的中譯排程書單（2026-09-28 使用者定）。

使用者：「宗教學與宗教史先開始，然後如果跟我的博論碩論有關要最先。」
  博論《從彼岸向此岸的轉向：近代東亞宗教變革與戰後台灣佛教、基督教公共性之宗教史比較研究》
  碩論《當代的大愛道革命》（比丘尼傳承復興、佛教女性主義）
排序：
  第 0 級 論文相關（書名／作者命中 THESIS 關鍵字，不限類別）
  第 1 級 類別＝宗教學（含宗教史、宗教社會學、宗教現象學、宗教學史…）
  第 2 級 類別＝世界宗教 且子類是宗教史／佛教／比較宗教等（不含神學原典、ACCS 叢書）
同級內字數少的先翻（先出成果）。輸入 output/untranslated_inventory/untranslated_v2.tsv（未中譯／不是同一本）。
輸出 output/translation_queue/religion_queue.tsv：rank\tid\t書名\t類別\t子類\t字數\t命中關鍵字
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output/untranslated_inventory/untranslated_v2.tsv"
OUT = ROOT / "output/translation_queue/religion_queue.tsv"

THESIS = [
    # 博論：東亞宗教變革、公共性、入世轉向
    r"public (?:religion|theology|sphere)", r"civil (?:religion|society)", r"secular", r"modernit",
    r"humanistic buddhism", r"engaged buddhism", r"buddhist modernism", r"socially engaged",
    r"taixu|t'ai-hsü|yinshun|yin shun|venerable yin", r"tzu chi|fo guang|dharma drum|ciji",
    r"taiwan", r"formosa", r"east asia", r"chinese buddhism", r"japanese buddhism", r"korean",
    r"presbyterian", r"contextual theology", r"minjung", r"liberation theology", r"social gospel",
    r"church and state|religion and politics|religion and democracy|democracy",
    r"protestant.*(?:china|japan|korea|asia)", r"missionar", r"christianity in (?:china|japan|korea|asia)",
    r"this-worldly|worldly asceticism|disenchant", r"religious reform", r"new religious movement",
    # 碩論：比丘尼、佛教女性
    r"bhikkhun|bhiksun|nun", r"women|woman|gender|feminis", r"mahapajapati|mahāpajāpatī|garudhamma",
    r"ordination", r"vinaya",
]
THESIS_RX = [re.compile(p, re.I) for p in THESIS]
RELIGION_SUB = re.compile(r"宗教史|佛教|比較|宗教學|宗教社會|宗教現象|神話|印度教|伊斯蘭|猶太|波斯|其他宗教|道教|新興")
EXCLUDE_SUB = re.compile(r"神學原典|IVP|註釋叢書|東方教會原典|典外文獻")


def main() -> int:
    rows = list(csv.DictReader(SRC.open(encoding="utf-8"), delimiter="\t"))
    rows = [r for r in rows if r.get("狀態", "").strip() in ("未中譯", "不是同一本") and r.get("已轉錄") == "是"]
    out = []
    for r in rows:
        text = f"{r.get('書名', '')} {r.get('作者', '')}"
        hits = [p.pattern for p in THESIS_RX if p.search(text)]
        cat, sub = r.get("類別", ""), r.get("子類", "") or ""
        if hits and (cat in ("宗教學", "世界宗教", "歷史學", "社會政治學", "哲學") or len(hits) >= 2):
            rank = 0
        elif cat == "宗教學":
            rank = 1
        elif cat == "世界宗教" and RELIGION_SUB.search(sub) and not EXCLUDE_SUB.search(sub):
            rank = 2
        else:
            continue
        try:
            chars = int(r.get("字數") or 0)
        except ValueError:
            chars = 0
        out.append((rank, chars, r["id"], r.get("書名", "")[:60], cat, sub, chars, "｜".join(hits)[:80]))
    out.sort(key=lambda x: (x[0], x[1]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("rank\tid\t書名\t類別\t子類\t字數\t命中關鍵字\n")
        for rank, _, i, t, c, s, n, h in out:
            f.write(f"{rank}\t{i}\t{t}\t{c}\t{s}\t{n}\t{h}\n")
    from collections import Counter
    cnt = Counter(x[0] for x in out)
    chars = Counter()
    for x in out:
        chars[x[0]] += x[1]
    print({k: (cnt[k], f"{chars[k]:,} 字") for k in sorted(cnt)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
