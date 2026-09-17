#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大藏經同書異名普查 —— 找出「同一部書被收兩次、各用一種音譯」的條目。

    python -X utf8 scripts/dazangjing_dup_titles.py

🚨 **這不是改名問題，是重複收錄。**
   直接把「波利甲」取代成「坡旅甲」，會讓 ancient.ts 出現兩個
   一模一樣的「坡旅甲致腓立比人書」——問題從看得見變成看不見。
   要先配對、再逐組合併（兩邊的 intro／source／連結各有內容）。

判準：把已知的音譯變體正規化之後，看 title_zh 或 title_orig 撞在一起。
正規化表從詞庫的 name_recommended／各傳統欄拉，不自己編。
"""
from __future__ import annotations

import difflib
import glob
import io
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

U, K = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": K, "Authorization": f"Bearer {K}"}

ENTRY = re.compile(r"title_zh:\s*'([^']*)'(.*?)(?=title_zh:|\Z)", re.S)


def field(name: str, s: str) -> str:
    m = re.search(rf"{name}:\s*'([^']*)'", s)
    return m.group(1) if m else ""


def alias_map() -> dict[str, str]:
    """{變體: 主譯}。詞庫是絕對權威，不自己編音譯表。"""
    rows, step = [], 1000
    while True:
        r = requests.get(f"{U}/rest/v1/theologians?select=name_recommended,"
                         f"name_protestant,name_catholic_sgs,name_orthodox,name_hk,"
                         f"name_tw,name_china_academic,name_variants&order=id"
                         f"&limit={step}&offset={len(rows)}", headers=H, timeout=120)
        r.raise_for_status()
        page = r.json()
        rows += page
        if len(page) < step:
            break
    out: dict[str, str] = {}
    for x in rows:
        rec = (x.get("name_recommended") or "").strip()
        if not rec:
            continue
        # 主譯的「地名的人名」形式，取人名那一截也要能對上
        heads = {rec, rec.split("的")[-1]}
        for f in ("name_protestant", "name_catholic_sgs", "name_orthodox",
                  "name_hk", "name_tw", "name_china_academic", "name_variants"):
            v = x.get(f)
            if not v:
                continue
            for y in re.split(r"[;；／/]", str(v)):
                y = y.strip()
                if len(y) >= 2 and y not in heads:
                    out.setdefault(y, rec.split("的")[-1])
                    # 變體也可能是「地名的人名」
                    if "的" in y:
                        out.setdefault(y.split("的")[-1], rec.split("的")[-1])
    return out


def main() -> int:
    alias = alias_map()
    print(f"詞庫變體表 {len(alias)} 條\n")

    entries = []
    for f in sorted(glob.glob(str(ROOT / "data/dazangjing/*.ts"))):
        s = io.open(f, encoding="utf-8").read()
        rel = Path(f).name
        line_of = lambda pos: s.count("\n", 0, pos) + 1  # noqa: E731
        for m in ENTRY.finditer(s):
            rest = m.group(2)[:800]
            entries.append(dict(zh=m.group(1), orig=field("title_orig", rest),
                                author=field("author", rest),
                                intro=field("intro", rest), file=rel,
                                line=line_of(m.start())))

    def norm(t: str) -> str:
        for a, b in sorted(alias.items(), key=lambda kv: -len(kv[0])):
            t = t.replace(a, b)
        return re.sub(r"[〈〉《》「」『』（）()‧·・、，,。\s]", "", t)

    by_zh: dict[str, list] = defaultdict(list)
    by_orig: dict[str, list] = defaultdict(list)
    for e in entries:
        by_zh[norm(e["zh"])].append(e)
        if e["orig"] and len(e["orig"]) > 6:
            by_orig[(norm(e["orig"]), norm(e["author"]))].append(e)

    # 🚨 **編輯距離對中文書名不能用**（2026-09-17 實測）。
    #    一字之差在中文書名裡往往是完全不同的書：
    #      大希庇亞篇／小希庇亞篇、前分析篇／分析後篇、猶太古史／猶太戰史、
    #      福音的喜樂勸諭／愛的喜樂勸諭、日語新共同譯聖經／韓語共同譯聖經。
    #    ratio>=0.75 把這些全判成同書——比漏抓更糟。
    #
    #    改用「**差異字必須全是音譯用字**」：坡旅甲／波利甲的差異是音譯字，
    #    大／小、古／戰是實詞。音譯對照表從站上實際的人名寫法建，
    #    並補回詞庫的 name_variants，下次就能純靠詞庫抓。
    TRANSLIT_PAIRS = [
        ("波利甲", "坡旅甲"), ("波利卡", "坡旅甲"), ("玻里加", "坡旅甲"),
        ("帕皮亞斯", "帕皮亞"), ("希拉波利斯", "希拉波利"),
        ("德爾都良", "特土良"), ("戴爾都良", "特土良"),
    ]

    def norm2(t: str) -> str:
        for a, b in TRANSLIT_PAIRS:
            t = t.replace(a, b)
        return norm(t)

    by_translit: dict[str, list] = defaultdict(list)
    for e in entries:
        by_translit[norm2(e["zh"])].append(e)
    for bucket in by_translit.values():
        if len(bucket) > 1 and len({e["zh"] for e in bucket}) > 1:
            by_zh[f"~T{bucket[0]['zh']}"] = bucket

    # 第三路：**同作者 ＋ intro 內容相似**。
    # 🚨 前兩路都漏掉帕皮亞與克勉那幾組，原因是那幾筆**沒有 title_orig**，
    #    而書名又差太遠（帕皮亞遺篇／主道論集殘篇、克勉書／克勉致哥林多人前書）。
    #    intro 是描述性的，同一本書的兩筆會講到同樣的事，長度也夠——
    #    編輯距離用在 intro 上才有意義，用在中文書名上只會製造假陽性。
    maybe: list = []
    by_author: dict[str, list] = defaultdict(list)
    for e in entries:
        a = norm(e["author"])
        if a and "佚名" not in a and len(a) >= 2:
            by_author[a[-4:]].append(e)
    for bucket in by_author.values():
        if not 2 <= len(bucket) <= 40:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                a, b = bucket[i], bucket[j]
                if a["zh"] == b["zh"] or not (a["intro"] and b["intro"]):
                    continue
                r = difflib.SequenceMatcher(None, a["intro"][:90], b["intro"][:90]).ratio()
                # 🚨 閾值 0.5 會把「同一作者的不同書」一起抓進來——那些書的 intro
                #    都在講同一位作者的背景（William Cave 的兩本傳記、Fuller 的兩本史）。
                #    故 intro 這一路一律只當**疑似**另列，不混進確定清單。
                if r >= 0.62:
                    maybe.append((round(r, 2), a, b))

    seen: set[tuple] = set()
    groups: list[list] = []
    for bucket in list(by_zh.values()) + list(by_orig.values()):
        if len(bucket) < 2:
            continue
        sig = tuple(sorted((e["file"], e["line"]) for e in bucket))
        if sig in seen:
            continue
        seen.add(sig)
        if len({e["zh"] for e in bucket}) > 1:
            groups.append(bucket)

    print(f"大藏經 {len(entries)} 筆條目\n🚨 同書異名 {len(groups)} 組\n")
    for g in groups:
        print(f"  ── {g[0]['orig'][:46] or '（無原文書名）'}")
        for e in g:
            print(f"     {e['file']}:{e['line']:<5} {e['zh'][:34]:<36} 作者={e['author'][:22]}")

    maybe.sort(reverse=True, key=lambda x: x[0])
    print()
    print(f"⚠ 疑似（同作者＋intro 相似）{len(maybe)} 組"
          "——**多數是同一作者的不同書，須人工看過**")
    for r, a, b in maybe[:14]:
        print(f"  {r}  {a['file']}:{a['line']} {a['zh'][:26]}  ⟷  {b['file']}:{b['line']} {b['zh'][:26]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
