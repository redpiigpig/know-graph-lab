"""英文 B2–C2 六千字的 Quizlet 匯入檔（托福用，25 字一課、依主題分組）。

來源是語言教練的共用字庫 `lang_vocab_bank`（language=en，三萬字，依詞頻分帶：
A1 1–1000、A2 –2000、B1 –4000、B2 –8000、C1 –15000、C2 –30000；每字都有繁中釋義、
例句與 18 類語意主題）。使用者 2026-09-25 要「托福 B2–C2 的單字 6,000 字」：取詞頻
4001–10000，即 B2 全帶 4,000 字加 C1 前 2,000 字。

使用者同日再定：「托福的話，應該二十五個一組，算做一課，然後可能以相關的來分組」。
所以先按語意主題（THEME_ORDER，具體→抽象→宗教）把字排在一起，同主題內按詞頻，
再每 25 字切一課，共 240 課；一課跨兩個主題時課名兩個都寫。

Quizlet 一個學習集最多 2,000 詞，所以出三個大檔（各 80 課）；另外每課一個小檔放在
english-b2c2-lessons/，想一課一個學習集的人貼那個。格式同 export_quizlet_tsv.py：
一行一張、正面 Tab 背面；背面＝釋義　例：例句　（第 N 課·主題·分級）。

用法：python -X utf8 scripts/export_quizlet_english_b2c2.py
產物：output/flashcards/quizlet/english-b2c2-{1,2,3}.txt、english-b2c2-課次表.txt、
english-b2c2-lessons/lesson-NNN.txt，並複製到 Drive 單字卡 底下的 Quizlet匯入 子夾。
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "flashcards" / "quizlet"
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\語言\原文讀本\單字卡\Quizlet匯入")
FIRST, LAST, PER_SET, PER_LESSON = 4001, 15000, 2000, 25
TARGET = 6000
# 🚨 詞頻表混著人名、地名、姓氏（harris、wendy、sydney…），第一版第 1 課開頭就是
# graham、pierre、jen。釋義寫明是人名地名的、例句裡以大寫專名出現的，一律不收，
# 從後面的詞頻補到六千。
NAME_MARK = re.compile(r"人名|姓氏|名字|地名|國名|城市|州名|品牌|縮寫|姓（|名（")
# 字庫的 18 類語意主題（coach_vocab_bank.py theme），排課順序：具體→抽象→宗教。
THEME_ORDER = [
    "人‧身體‧家庭", "食物‧飲食", "自然‧動植物", "時間‧節期", "空間‧方位", "數量‧度量",
    "行動‧移動", "情感‧心智", "言語‧文書", "社會‧政治‧律法", "工藝‧器物‧建築", "性質‧抽象",
    "功能詞", "神‧神學", "聖經人物‧地名", "敬拜‧禮儀", "教會‧群體‧教派", "罪‧救恩‧倫理",
]
TAB, NL = "\t", "\n"


def env() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            out[key] = value.strip().strip('"').strip("'")
    return out


def fetch() -> list[dict]:
    config = env()
    url, key = config["SUPABASE_URL"], config["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows: list[dict] = []
    offset = 0
    # 🚨 PostgREST 沒帶 Range 會靜默截在 1000 筆，所以逐頁抓到不足一頁為止。
    while True:
        response = requests.get(
            f"{url}/rest/v1/lang_vocab_bank?language=eq.en&freq_rank=gte.{FIRST}"
            f"&freq_rank=lte.{LAST}&select=word,meaning,example,level,freq_rank,theme"
            "&order=freq_rank.asc",
            headers={**headers, "Range": f"{offset}-{offset + 999}"},
            timeout=60,
        )
        response.raise_for_status()
        batch = response.json()
        rows.extend(batch)
        offset += 1000
        if len(batch) < 1000:
            break
    expected = LAST - FIRST + 1
    if len(rows) != expected:
        raise SystemExit(f"字庫回了 {len(rows)} 筆，應為 {expected}")
    missing = [r["word"] for r in rows if not (r.get("meaning") or "").strip()]
    if missing:
        raise SystemExit(f"{len(missing)} 字沒有釋義：{missing[:10]}")
    kept = [r for r in rows if not is_proper_name(r)]
    dropped = len(rows) - len(kept)
    if len(kept) < TARGET:
        raise SystemExit(f"濾掉專名後只剩 {len(kept)} 字，不足 {TARGET}；把 LAST 往後放")
    kept = kept[:TARGET]
    print(f"  詞頻 {FIRST}–{LAST} 共 {len(rows)} 字，濾掉專名 {dropped}，取前 {TARGET}（最後一字詞頻 {kept[-1]['freq_rank']}）")
    return kept


def is_proper_name(row: dict) -> bool:
    meaning = row.get("meaning") or ""
    if NAME_MARK.search(meaning):
        return True
    word = row["word"]
    example = row.get("example") or ""
    # 例句裡這個字只以大寫形出現（且不在句首）＝專名或專名形容詞（Korean、Australia）。
    capitalised = re.search(r"(?<![.!?] )(?<!^)" + re.escape(word.capitalize()) + r"(?![a-z])", example)
    lower = re.search(r"(?<![A-Za-z])" + re.escape(word) + r"(?![a-z])", example)
    return bool(capitalised and not lower)


def theme_of(row: dict) -> str:
    return (row.get("theme") or "未分類").strip()


def theme_key(row: dict) -> int:
    theme = theme_of(row)
    return THEME_ORDER.index(theme) if theme in THEME_ORDER else len(THEME_ORDER)


def lessons_of(rows: list[dict]) -> list[dict]:
    """主題相近的排在一起，再每 PER_LESSON 字一課。"""
    ordered = sorted(rows, key=lambda r: (theme_key(r), r["freq_rank"]))
    out: list[dict] = []
    for index in range(0, len(ordered), PER_LESSON):
        words = ordered[index:index + PER_LESSON]
        themes: list[str] = []
        for r in words:
            if theme_of(r) not in themes:
                themes.append(theme_of(r))
        out.append({"lesson": index // PER_LESSON + 1, "themes": themes, "words": words})
    return out


def back(row: dict, lesson: dict) -> str:
    parts = [row["meaning"].strip()]
    if (row.get("example") or "").strip():
        parts.append("例：" + row["example"].strip())
    parts.append(f"（第 {lesson['lesson']} 課·{theme_of(row)}·{row.get('level') or ''}）")
    return "　".join(parts).replace(TAB, " ").replace(NL, " ")


def line(row: dict, lesson: dict) -> str:
    return row["word"].replace(TAB, " ") + TAB + back(row, lesson) + NL


def main() -> None:
    rows = fetch()
    lessons = lessons_of(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    per_lesson_dir = OUT / "english-b2c2-lessons"
    per_lesson_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    lessons_per_set = PER_SET // PER_LESSON
    for index in range(0, len(lessons), lessons_per_set):
        chunk = lessons[index:index + lessons_per_set]
        number = index // lessons_per_set + 1
        path = OUT / f"english-b2c2-{number}.txt"
        path.write_text("".join(line(r, L) for L in chunk for r in L["words"]), encoding="utf-8")
        words = sum(len(L["words"]) for L in chunk)
        print(f"  {path.name}：第 {chunk[0]['lesson']}–{chunk[-1]['lesson']} 課，{words} 字，"
              f"主題 {chunk[0]['themes'][0]} → {chunk[-1]['themes'][-1]}")
        paths.append(path)
    for L in lessons:
        path = per_lesson_dir / f"lesson-{L['lesson']:03d}.txt"
        path.write_text("".join(line(r, L) for r in L["words"]), encoding="utf-8")
        paths.append(path)
    index_lines = [
        f"第 {L['lesson']:3d} 課　{'／'.join(L['themes'])}　{L['words'][0]['word']} … {L['words'][-1]['word']}"
        for L in lessons
    ]
    index_path = OUT / "english-b2c2-課次表.txt"
    index_path.write_text(NL.join(index_lines) + NL, encoding="utf-8")
    paths.append(index_path)
    print(f"  共 {len(lessons)} 課、{len(rows)} 字；課次表 {index_path.name}")
    if DRIVE.parent.exists():
        (DRIVE / per_lesson_dir.name).mkdir(parents=True, exist_ok=True)
        for path in paths:
            shutil.copy2(path, DRIVE / path.relative_to(OUT))
        print(f"已複製到 {DRIVE}")


if __name__ == "__main__":
    main()
