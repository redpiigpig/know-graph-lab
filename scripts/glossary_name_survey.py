#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
同名異譯普查 —— 把站上同一個來源名的各種中文寫法全部找出來，附脈絡。

    python scripts/glossary_name_survey.py --name Gregory
    python scripts/glossary_name_survey.py --all --out output/name_survey.md

═══════════ 為什麼需要這支 ═══════════

一個名字經不同語言傳到中文會有不同寫法，**那是功能**（見
.claude/skills/translation-glossary/naming_rules.md 的〈脈絡分辨〉）：
Gregorius→額我略、Γρηγόριος→格列高里、Grigor→格里高爾、英文 Gregory→貴格利。

但站上實際的情形是**同一個人也有好幾種寫法**，那就不是分辨而是 bug：
納西盎的那一位同時作「納西盎的格列高利」「拿先斯的格列高利」「納齊安的貴格利」
「格里高利納齊安」「託名拿先斯的格列高利」——同一人五種寫法。

🚨 **這種錯改不得用盲目取代。** 「額我略」有一大半是教宗聖號（額我略一世、
   額我略曆、額我略聖詠），動到就是另一個災難。所以本支**只普查、不改寫**，
   輸出報告供人逐條裁定。
"""
from __future__ import annotations

import argparse
import glob
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 各名字家族在中文裡可能的寫法。列得寬一點沒關係——普查階段寧可多抓。
FAMILIES: dict[str, list[str]] = {
    "Gregory": ["額我略", "國瑞", "格列高利", "格列高里", "格里高利", "格里高里",
                "格里高爾", "貴格利", "貴鉤利", "葛利果"],
    "John": ["約翰", "若望", "約安", "伊凡", "喬凡尼", "胡安", "讓", "揚",
             "漢斯", "尤哈尼斯", "約翰尼斯", "若翰"],
    "Michael": ["彌額爾", "米迦勒", "彌迦勒", "米海爾", "米凱爾", "麥可", "米歇爾",
                "米格爾", "邁克爾", "米哈伊爾", "彌格爾"],
    "Philip": ["腓力", "斐理伯", "菲利普", "腓利", "斐利伯", "費利佩", "菲力浦", "斐理博"],
    "Leo": ["利奧", "良", "列奧", "萊奧", "雷歐", "利奧一世", "李奧"],
    "Ignatius": ["依納爵", "依那爵", "伊納爵", "伊格那丟", "依格那丟", "伊格那修",
                 "伊格納修", "伊格納提烏斯", "伊格那提烏", "易格那丟"],
    "Origen": ["俄利根", "奧利金", "奧利振", "歐利根", "俄利振", "奧里根",
               "奧利根", "俄里根", "奧利根尼"],
    "Augustine": ["奧古斯丁", "奧思定", "奧斯定", "奧古斯汀", "奧古士丁", "奧古斯定"],
}

# 「良」「讓」「揚」這種單字會大量誤中，必須有前後文條件才算數。
NEEDS_CONTEXT = {"良", "讓", "揚"}
CONTEXT_HINT = re.compile(r"教宗|主教|聖|一世|二世|三世|四世|世紀|Leo|John|Pope")


def scan_files() -> list[str]:
    pats = ["data/**/*.ts", "data/**/*.json", "pages/**/*.vue", "pages/**/*.ts"]
    out: list[str] = []
    for p in pats:
        out += glob.glob(str(ROOT / p), recursive=True)
    return out


def survey(family: str) -> dict[str, list[tuple[str, str]]]:
    """回 {中文寫法: [(檔案, 脈絡), …]}。"""
    forms = FAMILIES[family]
    # 長的先比，免得「格列高利」被「格列高」之類的短詞先吃掉
    forms = sorted(forms, key=len, reverse=True)
    pat = re.compile(r".{0,16}(" + "|".join(map(re.escape, forms)) + r").{0,16}")
    hits: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for f in scan_files():
        try:
            s = io.open(f, encoding="utf-8").read()
        except OSError:
            continue
        rel = str(Path(f).relative_to(ROOT)).replace("\\", "/")
        for m in pat.finditer(s):
            form, ctx = m.group(1), " ".join(m.group(0).split())
            if form in NEEDS_CONTEXT and not CONTEXT_HINT.search(ctx):
                continue
            hits[form].append((rel, ctx))
    return hits


def report(families: list[str], out: Path) -> int:
    lines = ["# 同名異譯普查", "",
             "站上同一個來源名的各種中文寫法。**同名異譯不一定是錯**——",
             "經不同語言傳到中文本來就該不同（見 naming_rules.md〈脈絡分辨〉）；",
             "**但同一個人有好幾種寫法就是 bug**。", ""]
    for fam in families:
        hits = survey(fam)
        total = sum(len(v) for v in hits.values())
        lines += [f"## {fam}（{len(hits)} 種寫法，共 {total} 處）", ""]
        for form, rows in sorted(hits.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"### {form} —— {len(rows)} 處")
            lines.append("")
            seen = set()
            for rel, ctx in rows:
                key = ctx[:40]
                if key in seen:
                    continue
                seen.add(key)
                lines.append(f"- `{rel}` … {ctx}")
                if len(seen) >= 14:
                    lines.append(f"- …（另 {len(rows) - 14} 處）")
                    break
            lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"寫出 → {out}")
    for fam in families:
        h = survey(fam)
        print(f"  {fam:9s} {len(h)} 種寫法 / {sum(len(v) for v in h.values())} 處")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="同名異譯普查")
    ap.add_argument("--name", choices=list(FAMILIES))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="output/name_survey.md")
    a = ap.parse_args()
    fams = list(FAMILIES) if a.all else ([a.name] if a.name else [])
    if not fams:
        ap.print_help()
        return 1
    out = Path(a.out)
    if not out.is_absolute():
        out = ROOT / out
    return report(fams, out)


if __name__ == "__main__":
    raise SystemExit(main())
