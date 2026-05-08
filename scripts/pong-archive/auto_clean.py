#!/usr/bin/env python3
"""
auto_clean.py — fast first-pass cleaning of a raw Whisper transcript.

Strategy (good-enough, not perfect):
1. Find the sermon greeting line (e.g. "邱牧師、各位弟兄姊妹大家平安")
2. Find the sermon end (closing prayer "阿們" before announcements)
3. Convert simplified → traditional Chinese (OpenCC s2t)
4. Group consecutive short lines into paragraphs (every ~6-12 lines, OR
   when topic shift markers appear: 「另一方面」「所以」「今天」「但是」「於是」...)
5. Add 「龐君華牧師：」 header
6. Apply common Whisper-error fixes (薄力人 → 伯利恆, 三個佛事 → 三個博士, etc.)

Usage:
  python auto_clean.py YYYY-MM-DD
"""
import re
import sys
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp_sermon"
cc = OpenCC("s2t")

# Common Whisper mistranscriptions for Chinese sermons
FIXES = {
    "薄力人": "伯利恆",
    "薄利恆": "伯利恆",
    "喜愛山": "錫安山",
    "喜安山": "錫安山",
    "希愛山": "錫安山",
    "灯山變象": "登山變像",
    "登山变象": "登山變像",
    "尼賽人": "彌賽亞",
    "尼賽特": "彌賽亞",
    "彌賽亞": "彌賽亞",
    "三個佛事": "三個博士",
    "依麗撒海": "伊麗莎白",
    "化石架": "畫十字架",
    "暴命": "奧秘",
    "灵形": "有形",
    "暴命": "奧秘",
    "非常小可": "非同小可",
    "在上主面前": "在上主面前",
    # Common preacher self-references / addresses
    "丘牧師": "邱牧師",
    "丘牧师": "邱牧師",
    "邱牧师": "邱牧師",
    "熊牧师": "邱牧師",
    "熊牧師": "邱牧師",
}

# Topic-shift markers that suggest paragraph break
PARA_MARKERS = ["所以", "今天", "另一方面", "但是", "於是", "於是呢",
                "我們看到", "那麼", "這個時候", "這時候", "因此",
                "我記得", "我曾", "好的", "好,", "好 我們", "如果說"]


def find_sermon_range(lines):
    """Returns (start_idx, end_idx) for the sermon body.

    Strategy: find the LAST "上主的道" / "上主的福音" / "感謝主" marker
    (which ends the lectionary readings), then sermon starts shortly after.
    """
    # Find LAST scripture-ending marker
    end_markers_for_readings = [
        r"這是上主的(道|福音)", r"这是上主的(道|福音)",
        r"感謝上主", r"感谢上主",
        r"願拜也會與主祈福", r"愿拜也会与主祈福",
    ]
    last_reading_end = -1
    end_re = re.compile("|".join(end_markers_for_readings))
    # Search only first 70% of file
    search_limit = int(len(lines) * 0.7)
    for i in range(min(search_limit, len(lines))):
        if end_re.search(lines[i]):
            last_reading_end = i

    if last_reading_end > 0:
        # Sermon usually starts within next 5 lines (greeting comes right after)
        start = last_reading_end + 1
    else:
        # Fallback: look for greeting pattern
        greet_re = re.compile(
            r"(牧師|牧师).{0,5}(各位|弟兄)|^各位.{0,3}弟兄.{0,3}(姊妹|姐妹)"
        )
        start = None
        for i, line in enumerate(lines):
            if greet_re.search(line) and i > 20:
                start = i
                break
        if start is None:
            start = 0

    # Sermon end: "阿們" followed by hymn/creed marker, OR "報告事項" / "周報第六頁"
    end_markers = ["請看周報", "请看周报", "報告事項", "报告事项",
                   "回應詩歌", "回应诗歌", "新普誦第", "新普诵第",
                   "使徒信經", "使徒信经", "聖餐", "圣餐",
                   "獻詩", "献诗", "奉獻", "奉献"]
    end = len(lines)
    # Find first "阿們" / "阿们" after start
    for i in range(len(lines) - 1, start, -1):
        if "阿們" in lines[i] or "阿们" in lines[i]:
            # Look forward for end marker
            for j in range(i, min(i + 30, len(lines))):
                if any(m in lines[j] for m in end_markers):
                    end = i + 1  # include the 阿們 line
                    break
            if end != len(lines):
                break

    return start, end


def regroup_paragraphs(lines):
    """Group lines into paragraphs ~8 lines or at topic shift markers.

    Joins consecutive lines with 「，」 separator, except at topic-shift
    markers where we use 「。」 (sentence end).
    """
    paragraphs = []
    current = []  # list of (line, is_sentence_end_after)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Detect if this line should start a new sentence (前一句結束)
        starts_new_sentence = any(line.startswith(m) for m in PARA_MARKERS)
        if current and starts_new_sentence and len(current) >= 4:
            # Mark current paragraph done
            paragraphs.append(_join_with_punct(current))
            current = []
        current.append(line)
        if len(current) >= 12:
            paragraphs.append(_join_with_punct(current))
            current = []
    if current:
        paragraphs.append(_join_with_punct(current))
    return paragraphs


def _join_with_punct(lines):
    """Join lines with appropriate punctuation: , for continuation, 。for sentence end."""
    out = []
    for i, line in enumerate(lines):
        # Already has terminal punct?
        if line and line[-1] in "。！？，；：、」』）":
            out.append(line)
            continue
        # Last line of paragraph → 。
        if i == len(lines) - 1:
            out.append(line + "。")
        # Next line starts with topic shift → end this with 。
        elif i + 1 < len(lines) and any(lines[i + 1].startswith(m) for m in PARA_MARKERS):
            out.append(line + "。")
        else:
            out.append(line + "，")
    return "".join(out)


def apply_fixes(text):
    for bad, good in FIXES.items():
        text = text.replace(bad, good)
    return text


def main():
    date = sys.argv[1]
    raw = (TMP / f"{date}_raw.txt").read_text(encoding="utf-8").splitlines()
    start, end = find_sermon_range(raw)
    print(f"sermon range: lines {start}-{end} (of {len(raw)})", file=sys.stderr)

    sermon_lines = raw[start:end]
    paragraphs = regroup_paragraphs(sermon_lines)

    # Convert each paragraph to traditional + apply fixes
    out_paragraphs = []
    for p in paragraphs:
        p = cc.convert(p)
        p = apply_fixes(p)
        out_paragraphs.append(p)

    body = "\n\n".join(out_paragraphs)
    final = "龐君華牧師：\n\n" + body + "\n"

    out_path = TMP / f"{date}_clean.txt"
    out_path.write_text(final, encoding="utf-8")
    print(f"wrote {len(final)} chars to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
