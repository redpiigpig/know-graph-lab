"""把 50 課課程資料轉成 /english 網站要的 lessons.json。

網站原本是 20 課 × 50 字，課本改成 50 課 × 20 字之後兩邊分課不一致；
使用者 2026-09-08 定案網站也跟著改。課程內容共用 course50，這支只做形狀轉換：

- exercises 從 {mcq, fill, translate, unscramble} 攤成網站的
  [{type, items}] 陣列（utils/englishQuiz.ts 靠 type 挑題）
- 補上網站要的 theme_emoji 與每個字的 emoji

emoji 不再自己拿英文名去猜——課本那批就是這樣配出 order→獅子、summer→啤酒的。
改讀單字卡人工校過的 english-card-images.json，其中來源是 OpenMoji 的那些直接
取檔名當碼位；來源是 iconify／自繪圖磚的沒有對應碼位，就留空（網站本來就容許 null）。

用法：
    python scripts/english_site_from_course50.py           # 寫入 lessons.json
    python scripts/english_site_from_course50.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "public" / "content" / "english" / "course50"
CARD_IMAGES = ROOT / "output" / "source-cache" / "flashcards" / "english-card-images.json"
SITE_LESSONS = ROOT / "public" / "content" / "english" / "lessons.json"

EXERCISE_TITLES = [
    ("mcq", "choice", "練習一：選擇題"),
    ("fill", "fill", "練習二：填空"),
    ("unscramble", "unscramble", "練習三：句子重組"),
    ("translate", "translate", "練習四：造句翻譯"),
]


def openmoji_codes() -> dict[str, str]:
    """單字 -> OpenMoji 碼位（只有來源真的是 OpenMoji 的才有）。"""
    images = json.loads(CARD_IMAGES.read_text(encoding="utf-8"))["images"]
    codes = {}
    for word, entry in images.items():
        match = re.match(r"^openmoji-\d+/([0-9A-Fa-f-]+)\.png$", entry["file"])
        if match:
            codes[word] = match.group(1).upper()
    return codes


def alternates(en: str):
    yield en.strip()
    yield en.strip().lower()
    for part in re.split(r"[/、]", en):
        part = part.strip()
        if part:
            yield part
            yield part.lower()


def code_for(en: str, codes: dict[str, str]) -> str | None:
    for cand in alternates(en):
        if cand in codes:
            return codes[cand]
    return None


def theme_emojis() -> dict[str, str]:
    """沿用舊 20 課那份的主題圖示（course50 的 theme 就是舊課的 title_en）。"""
    if not SITE_LESSONS.exists():
        return {}
    try:
        old = json.loads(SITE_LESSONS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {l.get("title_en"): l.get("theme_emoji") for l in old if l.get("theme_emoji")}


def to_site(lesson: dict, codes: dict[str, str], themes: dict[str, str]) -> dict:
    exercises = []
    for key, kind, title in EXERCISE_TITLES:
        items = lesson["exercises"].get(key) or []
        if items:
            exercises.append({"type": kind, "title_zh": title, "items": items})
    return {
        "no": lesson["no"],
        "title_en": lesson["title_en"],
        "title_zh": lesson["title_zh"],
        "grammar": lesson["grammar"],
        "theme_emoji": themes.get(lesson.get("theme", "")),
        "intro_zh": lesson["intro_zh"],
        "can_do": lesson["can_do"],
        "words": [{"en": w["en"], "zh": w["zh"],
                   "emoji": code_for(w["en"], codes)} for w in lesson["words"]],
        "reading": lesson["reading"],
        "grammar_points": lesson["grammar_points"],
        "dialogue": lesson["dialogue"],
        "sentences": lesson["sentences"],
        "exercises": exercises,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    codes = openmoji_codes()
    themes = theme_emojis()
    files = sorted(COURSE.glob("L*.json"))
    if len(files) != 50:
        raise SystemExit(f"course50 只有 {len(files)} 課，先跑 build_english_course50.py")

    lessons = [to_site(json.loads(f.read_text(encoding="utf-8")), codes, themes)
               for f in files]
    lessons.sort(key=lambda l: l["no"])

    words = sum(len(l["words"]) for l in lessons)
    with_emoji = sum(1 for l in lessons for w in l["words"] if w["emoji"])
    questions = sum(len(e["items"]) for l in lessons for e in l["exercises"])
    no_theme = [l["no"] for l in lessons if not l["theme_emoji"]]

    print(f"{len(lessons)} 課 / {words} 字 / {questions} 題")
    print(f"  單字有 emoji：{with_emoji}/{words}")
    print(f"  缺主題圖示的課：{no_theme or '無'}")
    if args.dry_run:
        return
    SITE_LESSONS.write_text(json.dumps(lessons, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    size = SITE_LESSONS.stat().st_size / 1024 / 1024
    print(f"寫出 {SITE_LESSONS}（{size:.1f} MB）")


if __name__ == "__main__":
    main()
