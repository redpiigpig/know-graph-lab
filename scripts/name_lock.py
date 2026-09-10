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


# 日文新字體／簡體 → 繁體。只收「在繁中裡一定是錯的」那些，
# 有疑義的（例：齊克果的齊）一律不收 —— 這張表寧可漏也不可錯殺。
VARIANT_FORMS = {
    "内": "內", "薫": "薰", "彦": "彥", "証": "證", "説": "說", "会": "會",
    "徳": "德", "沢": "澤", "実": "實", "学": "學", "医": "醫", "図": "圖",
    "読": "讀", "変": "變", "戦": "戰", "経": "經", "関": "關", "駅": "驛",
}

_KANA_RE = re.compile(r"[ぁ-んァ-ヶー]")


def has_kana(text: str) -> bool:
    """段落裡有假名＝引用的日文原文。"""
    return bool(_KANA_RE.search(text or ""))


def normalize_forms(zh: str) -> tuple:
    """日文字形／簡體 → 繁體。回傳 (改寫後, 改動次數)。

    🚨 **段落裡有日文假名就整段不動**：那是引用的日文原文，
    「弁証の要なし、また教会の要なし」裡的 証／会 本來就該是日文字形，
    改成證／會等於把原文改壞。
    """
    if has_kana(zh):
        return zh, 0
    n = 0
    for bad, good in VARIANT_FORMS.items():
        c = zh.count(bad)
        if c:
            zh = zh.replace(bad, good)
            n += c
    return zh, n


def audit(pairs, locks) -> list:
    """找出「英文提到這個人、中文卻還留著變體」的段落。"""
    out = []
    for i, (src, zh) in enumerate(pairs):
        if not zh:
            continue          # 還沒翻到的段落（zh 是 None）不是名字問題
        for lk in locks:
            if not re.search(lk.en, src or ""):
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
        repl=[("貢德爾特", "貢德特"), ("根德特", "貢德特"),
              ("岡德特", "貢德特"), ("古德特", "貢德特"),
              ("格恩德爾特", "貢德特")],
        canon="貢德特",
        note="Wilhelm Gundert（1880-1971），德國宣教士、日本學者、赫塞的表兄。"
             "🚨 第一輪只抓到三種，因為我拿『貢／昆／根』猜首字去撈——"
             "『岡德特』『古德特』首字全不同就漏了。第三輪才發現還有『格恩德爾特』"
             "——它連共同尾字都不同（德爾特），從尾字反查一樣漏。"
             "🚨 六種寫法。真正可靠的做法是拿查得到的本名去對，不是從中譯自己找規律。",
    ),
    # ── 第二批（2026-09-07）：羅馬字日本人名被「音譯成漢字」而不是還原本字 ──
    #
    # 這一批比第一批更難發現：第一批是同一個人有好幾種寫法（自己就露餡），
    # 這一批是**每一處都寫得像個正常的日本名字**，只是全都不是那個人的名字。
    # 「高木貞幹」「正池目玉」看起來都毫無異狀 —— 除非你認得那個人。
    # 判準一律是查得到的本字，不是我覺得音近。
    Lock(
        key="takagi", en=r"\bTakagi\b",
        repl=[("高木貞幹", "高木八尺"), ("高木康麻", "高木八尺"), ("高木安高", "高木八尺")],
        canon="高木八尺",
        note="高木八尺（1889-1984），東京帝大美國研究講座首任教授、內村門下。"
             "全書八處只有兩處寫對，其餘拼出三種不同的假名字。",
    ),
    Lock(
        key="sakai", en=r"\bSakai\b",
        repl=[("坂井利彥", "堺利彥"), ("坂井利吉", "堺利彥"),
              ("坂井垣町", "堺利彥"), ("坂井藤吉", "堺利彥"), ("堺利彦", "堺利彥")],
        canon="堺利彥",
        note="堺利彥（號枯川），《萬朝報》專欄作者、後與幸德秋水同創社會主義運動。"
             "Sakai 的本字是『堺』不是『坂井』；「坂井垣町」「坂井藤吉」根本不是人名的樣子。"
             "同段的『幸德傳次郎（秋水）』反而是對的——那是他的本名，別一起改。",
    ),
    Lock(
        key="masaike", en=r"\bMasaike\b",
        repl=[("正池目玉", "政池仁")],
        canon="政池仁",
        note="政池仁（1900-1985），內村傳記作者、無教會第二代，本 portal 有他的 hub"
             "（slug masaike）。「目玉」是眼珠，這個譯名連字面都不成話。",
    ),
    Lock(
        key="azegami", en=r"\bAzegami\b",
        repl=[("畔上健三", "畔上賢造")],
        canon="畔上賢造",
        note="畔上賢造（1884-1938），本 portal 有他的 hub（slug azegami）。",
    ),
    Lock(
        key="nakada", en=r"\bNakada\b",
        repl=[("中田譲二", "中田重治")],
        canon="中田重治",
        note="中田重治（Nakada Jûji），日本聖潔教會創始者。重治讀作 Jūji，"
             "「譲二」是照音硬拼出來的。",
    ),
    Lock(
        key="saito", en=r"\bSait[ôo]\b",
        repl=[("齊藤", "齋藤")],
        canon="齋藤",
        note="齋藤宗次郎。齊與齋是兩個字，全書 55 處有 4 處寫成「齊藤」。",
    ),
    Lock(
        key="osanai", en=r"\bOsanai\b",
        repl=[("小山内薫", "小山內薰"), ("小山內薫", "小山內薰"),
              ("小山内薰", "小山內薰"), ("小山内", "小山內")],
        canon="小山內薰",
        note="小山內薰。混用了日文字形（内／薫）與繁體（內／薰）。",
    ),
    # ── 概念詞與敬稱：不是專名，但錯得夠明確，可以鎖 ──
    Lock(
        key="tenno", en=r"Imperial signature|\bEmperor\b.{0,40}(Japan|Meiji)",
        repl=[("皇帝的簽名", "天皇的簽名")],
        canon="天皇",
        note="教育敕語上的御署名（即內村不敬事件）。日本的是天皇不是皇帝。"
             "🚨 但同書另一處的『皇帝威廉』指德皇 Kaiser Wilhelm，那個是對的，"
             "所以這條鎖用英文佐證卡死在日本語境，不可放寬成整批換『皇帝』。",
    ),
    Lock(
        key="preacher", en=r"\bThe preacher\b",
        repl=[("那位傳教士", "那位牧師")],
        canon="牧師",
        note="英文是 preacher，指同段前面那位 a pastor in America。"
             "誤成「傳教士」既錯身分，也違反 missionary→宣教士 的定名"
             "（[[feedback_translation_candidates_not_one_to_one]]）。",
    ),
    Lock(
        key="constitutional", en=r"wrangle constitutionally|constitutional enthusiasm",
        repl=[("憲法性熱情", "與生俱來的熱情"), ("憲法地爭論", "依憲政程序爭論")],
        canon="（兩義按語境）",
        note="constitutional 的兩個非「憲法」義：體質上的（她天生的熱情）與"
             "依憲政程序的。🚨 全書另有 13 處『憲法』是真的明治憲法與 1947 年憲法，"
             "不可整批處理——這條鎖同樣靠英文佐證卡死。",
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
            new, nf = normalize_forms(new)
            if nf:
                per_key[("forms", "日文字形／簡體", "繁體")] =                     per_key.get(("forms", "日文字形／簡體", "繁體"), 0) + nf
            n += nf
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
