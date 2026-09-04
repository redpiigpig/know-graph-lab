#!/usr/bin/env python3
"""從 /english 課程的一千字表，整出單字卡用的詞表：五十課，每課二十字。

站上那份是 20 課 × 50 字（`public/content/english/lessons.json`），詞是教育部
國中小基本字彙那一路。單字卡要的是 50 課 × 20 字，而且**配不出誠實圖的詞不收**
——使用者的話是「像是 a the to 這種沒有具體意思的就不要了」。

所以這支做三件事：

1. **抽掉沒有具體所指的詞。** 冠詞、對等連接詞、助動詞與情態動詞、指示詞、
   純數量詞、程度副詞。留下代名詞、疑問詞、介系詞與方位詞——那幾類畫得出來
   （you 👉、what ❓、up ⬆️），單字卡向來就是「虛詞給符號不給場景」。
2. **同主題補回等量的具體詞**，讓每個主題仍是 50 字、全書仍是 1000 字。抽掉
   42 個就補 42 個，不是把總數改小。
3. **順序切成 50 課、每課 20 字**，主題順序不動。一個主題跨兩課半，所以卡背
   同時印課次與主題。

`may/ might` 那一筆是站上把情態動詞跟五月併在一起了，抽掉情態動詞之後十二個月
會缺五月——所以補回的是月份 May，不是別的字。
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public/content/english/lessons.json"
TARGET = ROOT / "data/originalReaders/vocabulary/english-1000.json"

PER_LESSON = 20

# 沒有具體所指、配不出誠實圖的那些。留白的卡對這副牌沒有用——它的整個設計就是
# 背面一張圖加中文。
DROP = {
    "a/ an", "the", "and", "or", "but", "not", "very", "too", "also", "well",
    "be/am/is/are", "do/does", "can/could", "must", "will/would", "should",
    "this", "that", "these", "those",
    "all", "some", "many", "few", "more", "most", "less", "least", "each",
    "every", "only", "other", "several", "enough", "a lot", "a few",
    "a little", "little", "much", "any",
    "your", "may/ might",
}

# 補回的詞，掛在原主題底下，接在該主題末尾。挑的原則跟抽掉的相反：畫得出來、
# 國小教得到、且與該主題既有的詞不重複。
REFILL: dict[int, list[tuple[str, str]]] = {
    1: [
        ("good morning", "早安"), ("good afternoon", "午安"),
        ("good evening", "晚安（傍晚）"), ("good night", "晚安（睡前）"),
        ("hug", "擁抱"), ("wave", "揮手"), ("bow", "鞠躬"),
        ("shake hands", "握手"), ("clap", "拍手"), ("thumbs up", "比讚"),
        ("wink", "眨眼"), ("whisper", "悄悄說"), ("greeting", "問候"),
        ("introduce", "介紹"), ("nickname", "綽號"), ("birthday", "生日"),
        ("hometown", "家鄉"), ("neighbor", "鄰居"), ("guest", "客人"),
        ("lady", "女士"),
    ],
    2: [
        ("zero", "零"), ("plus", "加"), ("minus", "減"),
        ("add", "相加；增加"), ("equal", "等於"),
    ],
    3: [
        ("balloon", "氣球"), ("ribbon", "緞帶"), ("gem", "寶石"),
        ("brick", "磚塊"), ("puzzle", "拼圖"), ("arrow", "箭頭"),
        ("heart shape", "心形"), ("oval", "橢圓形"), ("cube", "立方體"),
        ("dark", "深色的；暗的"), ("silver", "銀色"), ("wide", "寬的"),
        ("narrow", "窄的"), ("thick", "厚的；粗的"), ("corner", "角落"),
    ],
    5: [("nephew", "姪子；外甥")],
    12: [("May", "五月")],
}

# 站上的寫法混了大小寫與空白（`Refrigerator / fridge`、`Anyone / anybody`）。
# 卡面要一致，但專有名詞不能一起壓成小寫。
KEEP_CAPITAL = {
    "English", "Taiwan", "Taipei", "New Taipei", "Beitou", "Taoyuan",
    "Taichung", "Tainan", "Kaohsiung", "Hualien", "America", "China",
    "Japan", "Korea", "Singapore", "Hong Kong", "Vietnam", "Thailand",
    "the Philippines", "Malaysia", "Canada", "Australia", "England",
    "France", "Germany", "India", "American", "Chinese",
    "Chinese New Year", "Dragon Boat Festival", "Moon Festival",
    "Halloween", "Christmas", "Santa Claus", "Taiwanese Snacks", "MRT",
    "Mr.", "Mrs.", "Miss", "Ms.", "May",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    "Sunday", "January", "February", "March", "April", "June", "July",
    "August", "September", "October", "November", "December",
}

THEME_ZH = {
    "Hello & Me": "問候與自我介紹",
    "Numbers & How Many": "數字與數量",
    "Colors & Shapes": "顏色與形狀",
    "My Body": "身體與動作",
    "My Family & Friends": "家人與朋友",
    "Animals & Pets": "動物與寵物",
    "Food & Meals": "食物與三餐",
    "Drinks, Fruits & Snacks": "飲料‧水果與小吃",
    "At School": "在學校",
    "Classroom Actions": "課堂上的事",
    "My House": "我的家",
    "Days, Months & Time": "日子‧月份與時間",
    "Weather, Seasons & Nature": "天氣‧季節與自然",
    "Clothes & How I Look": "衣著與外表",
    "Feelings & Thoughts": "心情與想法",
    "Sports & Hobbies": "運動與嗜好",
    "Things I Can Do": "我做得到的事",
    "Jobs & People": "職業與人物",
    "My Town & Country": "城鎮與國家",
    "Travel, Countries & Festivals": "旅行‧國家與節慶",
}


def headword(raw: str) -> str:
    """`math / mathematics` 與 `Refrigerator / fridge` 統一成 `math/mathematics`。

    🚨 只把「首字母大寫、其餘小寫」的普通詞壓成小寫。`I` 與 `OK` 不能碰——單字母
    的 I 會變成 i，全大寫的 OK 會變成 oK，兩個都會原封不動印在卡上，而且看起來
    只是「有點怪」，不像壞掉。
    """

    def fold(token: str) -> str:
        if token in KEEP_CAPITAL or len(token) < 2:
            return token
        return token[0].lower() + token[1:] if token[1:].islower() else token

    return "/".join(fold(part.strip()) for part in raw.split("/"))


def main() -> None:
    lessons = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries: list[dict] = []
    dropped: list[str] = []

    for theme in lessons:
        kept = []
        for word in theme["words"]:
            if word["en"] in DROP:
                dropped.append(word["en"])
                continue
            kept.append({"en": headword(word["en"]), "zh": word["zh"],
                         "openmoji": word.get("emoji")})
        for english, chinese in REFILL.get(theme["no"], []):
            kept.append({"en": headword(english), "zh": chinese, "openmoji": None})
        if len(kept) != 50:
            raise SystemExit(
                f"第 {theme['no']} 主題《{theme['title_en']}》抽掉 "
                f"{50 - len(kept) + len(REFILL.get(theme['no'], []))} 個、"
                f"只補了 {len(REFILL.get(theme['no'], []))} 個，剩 {len(kept)} 字")
        for item in kept:
            item["theme"] = theme["title_en"]
            item["themeZh"] = THEME_ZH[theme["title_en"]]
        entries.extend(kept)

    unknown = set(DROP) - set(dropped)
    if unknown:
        raise SystemExit(f"DROP 裡有詞表上沒有的詞（拼錯了？）：{sorted(unknown)}")
    seen: dict[str, int] = {}
    for index, item in enumerate(entries, start=1):
        if item["en"] in seen:
            raise SystemExit(f"{item['en']} 重複（第 {seen[item['en']]} 與第 {index} 筆）")
        seen[item["en"]] = index
        item["ordinal"] = index
        item["lesson"] = (index - 1) // PER_LESSON + 1

    payload = {
        "language": "en",
        "title": "國小英語單字卡",
        "perLesson": PER_LESSON,
        "lessons": entries[-1]["lesson"],
        "note": "由 public/content/english/lessons.json 抽掉純虛詞、同主題補回等量具體詞而成，"
                "見 scripts/build_english_vocabulary.py。",
        "entries": entries,
    }
    TARGET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    with_image = sum(1 for item in entries if item["openmoji"])
    print(f"  {len(entries)} 字／{payload['lessons']} 課（每課 {PER_LESSON} 字）")
    print(f"  抽掉 {len(dropped)} 個虛詞，同主題補回 {sum(len(v) for v in REFILL.values())} 個具體詞")
    print(f"  站上已有配圖 {with_image}，待配 {len(entries) - with_image}")
    print(TARGET)


if __name__ == "__main__":
    main()
