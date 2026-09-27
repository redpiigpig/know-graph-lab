#!/usr/bin/env python3
"""自撰練習題的「一題一句」檢查。

2026-09-27 擁有者定：每課二十詞全覆蓋不變，但每一題必須是一個連貫的句子。
在這之前的寫法為了湊覆蓋，把兩三個互不相干的短句用分號或句號拼成一題
（「Sacerdos sedet; Deus tuetur; chorus concinat.」「池を埋め立てます。木を彫ります。」），
三道語料閘與句型閘全都放行，覆核者也放行。這支只管形式上擋得住的那一半：

* 拉丁：自撰題不得有分號或冒號（一題一句；子句要靠 et／sed／quia／cum 之類接起來）。
* 日文：一題最多兩句；兩句時第一句必須是問句（以「か。」或「？」結尾），即一問一答。

語意是否連貫仍要人讀；這支擋不住「一句之內講不通」。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers"
LANGS = {
    "latin": ("latin-full", "latin"),
    "japanese": ("japanese-full", "japanese"),
}


def latin_problem(text: str) -> str | None:
    if re.search(r"[;:·]", text):
        return "拉丁自撰題含分號或冒號（一題應為一句）"
    return None


def japanese_problem(text: str) -> str | None:
    parts = [p for p in re.split(r"(?<=[。！？?!])", text.strip()) if p.strip()]
    if len(parts) <= 1:
        return None
    if len(parts) > 2:
        return f"日文自撰題拼了 {len(parts)} 句（最多兩句且須一問一答）"
    first = parts[0].strip()
    if not (first.endswith("か。") or first.endswith("？") or first.endswith("?")):
        return "日文自撰題兩句但第一句不是問句（兩句只允許一問一答）"
    return None


CHECKS = {"latin": latin_problem, "japanese": japanese_problem}


MAX_QUESTIONS_PER_LESSON = 2
"""一課自撰題最多幾題問句。

第一次照「一題一句或一問一答」改寫時，日文第一冊 351 句有 280 句變成問句——
把「A します。B します。」改成「A しますか、B しますか。」就過了形式檢查，
句子卻比原本更不自然（「兄とお兄さんは同じ人ですか」）。問句本身沒有錯，
一課兩題以內足夠練疑問句型。
"""


def is_question(text: str) -> bool:
    t = text.strip()
    return t.endswith(("か。", "？", "?", "か")) or "か。" in t or "？" in t or "?" in t


def scan(lang: str) -> list[dict]:
    folder, key = LANGS[lang]
    out = []
    for path in sorted((CACHE / folder).glob("composed-draft-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        questions = []
        for no, row in enumerate(data.get("sentences", []), 1):
            text = row.get(key, "")
            problem = CHECKS[lang](text)
            if problem:
                out.append({"file": path.name, "no": no, "text": text, "problem": problem})
            if is_question(text):
                questions.append(no)
        if len(questions) > MAX_QUESTIONS_PER_LESSON:
            out.append({"file": path.name, "no": questions[MAX_QUESTIONS_PER_LESSON],
                        "text": "", "problem": f"一課 {len(questions)} 題問句（上限 {MAX_QUESTIONS_PER_LESSON}）：第 {questions} 題"})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", choices=sorted(LANGS))
    parser.add_argument("--files", nargs="*", default=[], help="只看這些草稿檔名（例 composed-draft-v1-05.json）")
    args = parser.parse_args()
    rows = scan(args.language)
    if args.files:
        rows = [r for r in rows if r["file"] in set(args.files)]
    for r in rows:
        print(f"✘ {r['file']} #{r['no']}：{r['problem']}｜{r['text']}")
    folder, _ = LANGS[args.language]
    total = sum(len(json.loads(p.read_text(encoding='utf-8')).get('sentences', []))
                for p in (CACHE / folder).glob("composed-draft-*.json"))
    print(f"{args.language}：{len(rows)} 題違規／共 {total} 題" + ("　✔" if not rows else ""))
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
