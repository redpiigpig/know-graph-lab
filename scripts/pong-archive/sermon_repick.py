#!/usr/bin/env python3
"""
sermon_repick.py — 2nd-pass classifier on saved triage texts.

The first triage pass conservatively defaulted to ⛔ when no strong signal
was found. This script re-scans all *_triage.txt files with a broader
regex covering Whisper's mis-transcriptions of "邱牧師" and the
characteristic 龐牧師 greeting pattern.

For each triage text, prints:
  STRONG_PONG  YYYY-MM-DD  matched_text
  WEAK_PONG    YYYY-MM-DD  matched_text  (some hint, less confident)
  -            YYYY-MM-DD  (no signal)

Usage:
  python sermon_repick.py [--year YYYY]
  python sermon_repick.py --revert STRONG  # revert STRONG hits in queue files
                                           # (mark them ⏳ 未完成 again)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = ROOT / "tmp_sermon"
QUEUE_DIR = ROOT / "pong-archive" / "stores" / "城中教會講道清單"

# ─── Patterns ───────────────────────────────────────────────────────────────
# NOTE: Whisper outputs SIMPLIFIED Chinese. All patterns must use simplified.
# 牧師→牧师, 證→证, 講→讲, 談→谈, 過→过, 還→还, 來→来, 時→时, 還→还,
# 蕢→蕢 (kept), 龐→庞, 邱→邱, 弟兄姊妹→弟兄姐妹

QIU_CHARS = "邱丘球秋仇裘琼瓊塞趋趨求修聖圣"
GUEST_PASTOR_CHARS = "蕢簣匱餽庞龐庬逄碰窺窥跨愧春秦祝桂貴贵"

# STRONG: 龐 greeting addresses 邱牧師 (or known Whisper variants of his name)
STRONG_GREETING = re.compile(
    rf"[{GUEST_PASTOR_CHARS}](牧师|牧師).{{0,5}}[{QIU_CHARS}](牧师|牧師).{{0,15}}各位"
    r"|"
    rf"[{QIU_CHARS}](牧师|牧師).{{0,8}}各位.{{0,5}}(弟兄|姊妹|姐妹|兄姊)"
    r"|"
    rf"[{QIU_CHARS}](会督|會督).{{0,8}}各位"
    r"|"
    rf"[{QIU_CHARS}](牧师|牧師).{{0,5}}(弟兄姐妹|弟兄姊妹)"
    r"|"
    # Generic guest-preacher greeting: address ANY 牧师 + 弟兄/各位 in OPENING line
    # Covers Whisper's many variants of 蕢/邱 names
    r"^[^\n]{1,30}(牧师|牧師).{0,3}(以及|和|還有|还有).{0,5}(诸位|諸位|各位).{0,8}(弟兄|姊妹|姐妹)"
    r"|"
    # Two pastor names in opening: "X牧師 Y牧師 各位/弟兄"
    r"^[^\n]{1,15}(牧师|牧師).{1,15}(牧师|牧師).{0,15}(各位|弟兄|姊妹|姐妹)"
    r"|"
    # Two 牧師 references on consecutive lines near a 弟兄/平安 line
    # Catches: "春牧師 聖牧師\n兄姐妹 大家平安" pattern
    r"(牧师|牧師)[\s\n]{0,3}[^\n]{0,5}(牧师|牧師)[\s\n]{0,5}(兄姐妹|弟兄|姊妹|姐妹)"
    r"|"
    # Announcement pattern: "邱牧師今天[在|到][外地]…請為他帶導/代禱"
    rf"[{QIU_CHARS}](牧师|牧師)今天.{{0,8}}(在|到|去).{{0,15}}(讲道|講道|证道|證道|主理|带领|帶領|聖餐|聖道|崇拜|衛理|衛禮|內湖|内湖|台北|台中|高雄)"
    r"|"
    rf"[{QIU_CHARS}](牧师|牧師).{{0,8}}今天.{{0,8}}(请|請).{{0,5}}(为他|為他).{{0,3}}(代禱|代祷|帶導|带导|纪念|紀念)"
)

# WEAK: 邱 mentioned 3rd-person doing other duties / external venue
WEAK_PONG_HINT = re.compile(
    rf"[{QIU_CHARS}](牧师|牧師).{{0,8}}今天.{{0,8}}(在|不在|主理|证道|證道|讲道|講道|布道|佈道|步道|外地|内湖|內湖|台中|高雄|香港)"
    r"|"
    r"我过去在总会|我以前在总会|我過去在總會|我以前在總會|当会督|當會督|做会督|做會督"
    r"|"
    r"(感谢|歡迎|感謝|欢迎).{0,5}(龐|庞).{0,5}(牧师|牧師|会督|會督).{0,8}(证道|證道|讲道|講道|信息)"
    r"|"
    r"(庞|龐).{0,2}(会督|會督).{0,5}回到我们"
    r"|"
    # 1st-person interaction with the resident pastor (=preacher is guest)
    r"(跟|和|向)(牧师|牧師).{0,5}(聊|说|說|提到|谈到|談到|商量|分享)"
    r"|"
    r"(牧师|牧師).{0,3}(也|又|还|還|剛剛|刚刚).{0,3}(谈到|談到|说|說|提到|分享|提及)"
    r"|"
    r"我早上来的时候.{0,15}(牧师|牧師)"
    r"|"
    r"我早上來的時候.{0,15}(牧师|牧師)"
    r"|"
    # 邱 mentioned by name in 3rd person ANYWHERE in text (likely guest preacher)
    rf"[{QIU_CHARS}](牧师|牧師)(把|為|为|跟|與|和|在|今|帶領|带领|主理)"
    r"|"
    rf"我.{{0,5}}聯絡.{{0,5}}[{QIU_CHARS}](牧师|牧師)"
    r"|"
    rf"我.{{0,5}}联络.{{0,5}}[{QIU_CHARS}](牧师|牧師)"
)

# Disqualifying: clear 邱 self-references (autobiographical)
NOT_PONG = re.compile(
    r"我从香港|我從香港|在香港的时候|在香港的時候|我家在香港|我们从香港|我們從香港"
    r"|"
    r"我们卫理公会在台湾|我們衛理公會在台灣"
)


def classify(text):
    if NOT_PONG.search(text):
        return ("not_pong", NOT_PONG.search(text).group(0))
    m = STRONG_GREETING.search(text)
    if m:
        return ("strong", m.group(0))
    m = WEAK_PONG_HINT.search(text)
    if m:
        return ("weak", m.group(0))
    return ("none", "")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", help="filter to a specific year (YYYY)")
    p.add_argument("--limit", type=int, help="show only first N matches per category")
    args = p.parse_args()

    year_filter = args.year

    triage_files = sorted(TMP_DIR.glob("*_triage.txt"))
    if year_filter:
        triage_files = [f for f in triage_files if f.name.startswith(year_filter)]

    strong = []
    weak = []
    not_pong = []
    none = []

    for f in triage_files:
        date = f.name.replace("_triage.txt", "")
        text = f.read_text(encoding="utf-8")
        decision, snippet = classify(text)
        if decision == "strong":
            strong.append((date, snippet))
        elif decision == "weak":
            weak.append((date, snippet))
        elif decision == "not_pong":
            not_pong.append((date, snippet))
        else:
            none.append(date)

    print(f"\n##### STRONG 龐 候選 ({len(strong)}) #####")
    for d, s in strong[: args.limit] if args.limit else strong:
        print(f"  {d}  「{s}」")

    print(f"\n##### WEAK 龐 候選 ({len(weak)}) #####")
    for d, s in weak[: args.limit] if args.limit else weak:
        print(f"  {d}  「{s}」")

    print(f"\n##### 確認非龐 ({len(not_pong)}) #####")
    for d, s in not_pong[: args.limit] if args.limit else not_pong:
        print(f"  {d}  「{s}」")

    print(f"\n##### 無訊號 ({len(none)}) #####")
    if args.limit:
        for d in none[: args.limit]:
            print(f"  {d}")
        if len(none) > args.limit:
            print(f"  ... 共 {len(none)} 個")
    else:
        for d in none:
            print(f"  {d}")


if __name__ == "__main__":
    main()
