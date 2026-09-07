# -*- coding: utf-8 -*-
"""專名一對一鎖 —— 把機器翻譯漂掉的人名收斂回單一寫法。

長篇逐段翻譯最典型的靜默失敗：同一個人在第三章叫「武子」、第五章叫「武江」、
第七章叫「武惠」。每一頁都通順，沒有任何東西會壞掉，只有拿原文交叉比對才看得出來。

核心規矩只有一條 —— **有英文佐證才動手**：某個中文變體要被改寫，該段的英文原文
必須真的提到那個人。少了這道閘，修「有島雄士→祐之」會順手毀掉真實存在的
有島武郎（全書 20 處）。

    python scripts/name_lock.py --dry            # 只報告
    python scripts/name_lock.py --apply          # 實際改寫 JSON
    python scripts/name_lock.py --audit          # 改完回頭驗殘留

見 .claude/skills/ebook-collected-works/howes_uchimura_biography.md。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class Lock:
    key: str
    en: str                      # 英文佐證（regex）
    repl: list                   # [(變體, 正名), ...]
    canon: str                   # 正名（稽核用）
    note: str = ""


@dataclass(frozen=True)
class Issue:
    index: int
    key: str
    variant: str
    zh: str


# ---------------------------------------------------------------- 純函式

def repair_paragraph(src: str, zh: str, locks, tally: dict = None) -> tuple:
    """回傳 (改寫後的 zh, 改動次數)。只在英文佐證成立時才動該條鎖。

    `tally` 給進來就順手記下每條替換實際發生幾次。次數必須在**替換過程中**數，
    不能事前各數各的 —— 「延子」本來就包在「淺田延子」裡面，分開數會重複計算。
    """
    total = 0
    for lk in locks:
        if not re.search(lk.en, src):
            continue
        # 長的先換，否則短變體會把長變體切成兩半
        for frm, to in sorted(lk.repl, key=lambda p: -len(p[0])):
            n = zh.count(frm)
            if n:
                zh = zh.replace(frm, to)
                total += n
                if tally is not None:
                    tally[(lk.key, frm, to)] = tally.get((lk.key, frm, to), 0) + n
    return zh, total


def audit(pairs, locks) -> list:
    """找出「英文提到這個人、中文卻還留著變體」的段落。"""
    out = []
    for i, (src, zh) in enumerate(pairs):
        for lk in locks:
            if not re.search(lk.en, src):
                continue
            for frm, _ in lk.repl:
                if frm in zh:
                    out.append(Issue(i, lk.key, frm, zh))
    return out


# ---------------------------------------------------------------- 豪斯傳記的鎖
#
# 譯名依據：內村鑑三的家族成員以日文正式名為準（ja.wikipedia 內村鑑三／內村祐之）。
# 片假名女性名依使用者 2026-09-07 定調走「漢字定名」（タケ→武、ノブ→信）。
# ノブ 一律寫全名「淺田信」不寫單字「信」—— 中文的「信」是書信／信仰，
# 單獨當人名在句子裡會讀不出來（原文那一段正好也在講她寄來的信）。

HOWES_LOCKS = [
    Lock(
        key="take", en=r"\bTake\b|\bAsada\b",
        repl=[("武江", "武"), ("武惠", "武"), ("武子", "武")],
        canon="武",
        note="浅田タケ，內村元配。英文全書一致作 Take，中譯卻有四種寫法。",
    ),
    Lock(
        key="yushi", en=r"\bY[uû]shi\b",
        repl=[("有島雄士", "祐之"), ("雄士", "祐之"), ("雄志", "祐之")],
        canon="祐之",
        note="內村祐之（1897-1980）。有島 是隔壁段落 有島武郎 的姓，被誤植。"
             "英文全書一律作裸名 Yûshi（首次登場即 his son Yûshi），中譯照樣用裸名 祐之。",
    ),
    Lock(
        key="nobu", en=r"\bNobu\b",
        repl=[("淺田延子", "淺田信"), ("延子", "淺田信")],
        canon="淺田信",
        note="浅田ノブ（1885-1967），內村與元配之女，後為日永信子。",
    ),
    Lock(
        key="parmalee", en=r"\bParmalee\b",
        repl=[("帕馬利", "帕瑪利"), ("帕邁利", "帕瑪利"), ("帕美利", "帕瑪利")],
        canon="帕瑪利",
    ),
    Lock(
        key="gundert", en=r"\bGundert\b",
        repl=[("貢德爾特", "貢德特"), ("根德特", "貢德特")],
        canon="貢德特",
    ),
    Lock(
        key="rutsuko", en=r"\bRuth\b",
        repl=[("魯茨子", "露絲子"), ("盧茨子", "露絲子")],
        canon="露絲",
        note="內村ルツ子（1894-1912）。與聖經《路得記》同源但**不可混用**："
             "女兒作 露絲，書卷作 路得記 —— 現況已正確，這條鎖只防新漂移。",
    ),
]

DEFAULT_GLOB = os.path.join(
    ".claude", "skills", "ebook-collected-works", "howes_data", "howes-prophet", "sec*.json")


def _sec_no(path: str) -> int:
    m = re.search(r"sec(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else -1


def load_sections(pattern: str):
    return sorted(glob.glob(pattern), key=_sec_no)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default=DEFAULT_GLOB)
    ap.add_argument("--apply", action="store_true", help="實際寫回 JSON")
    ap.add_argument("--audit", action="store_true", help="只查殘留變體")
    args = ap.parse_args()

    files = load_sections(args.glob)
    if not files:
        print("找不到任何 section：%s" % args.glob)
        return 1

    grand = 0
    per_key = {}
    for path in files:
        d = json.load(open(path, encoding="utf-8"))
        zh = d.get("zh") or []
        if not zh:
            continue
        pairs = list(zip(d["src"], zh))

        if args.audit:
            for iss in audit(pairs, HOWES_LOCKS):
                grand += 1
                print("%s #%d  %s 殘留「%s」" % (
                    os.path.basename(path), iss.index, iss.key, iss.variant))
            continue

        changed = 0
        for i, (src, z) in enumerate(pairs):
            new, n = repair_paragraph(src, z, HOWES_LOCKS, tally=per_key)
            if n:
                zh[i] = new
                changed += n
        grand += changed
        if changed:
            print("%-12s %3d 處" % (os.path.basename(path), changed))
        if changed and args.apply:
            d["zh"] = zh
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1)

    if args.audit:
        print("殘留 %d 處" % grand)
        return 1 if grand else 0

    print("-" * 46)
    for (key, frm, to), n in sorted(per_key.items()):
        print("  %-9s %s → %s   x%d" % (key, frm, to, n))
    print("合計 %d 處%s" % (grand, "（已寫回）" if args.apply else "（--dry，未寫回）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
