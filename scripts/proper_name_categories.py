#!/usr/bin/env python3
"""替三種語言的專名附錄分類：地名、國名、神名，人名再分六類。

使用者 2026-08-27 定的分類，讀本附錄與單字卡都照它分組：

    地名／民族與國名／神名與稱號／
    族長與先知／君王／使徒與門徒／教宗與主教／教父與聖人／其他人名

**分類跟中文名字一樣，只從登錄取，不從模型取。** 這一系列已經為此付過代價：
信望愛那條路徑把字典釋義當成名字，49 筆錯的印在紙上看起來完全正常。分類錯一樣看不
出來——把巴西流標成君王，讀的人沒有辦法察覺。所以每一筆都記 `categoryRoute`，
查不到就留在「其他人名」，不硬分。

登錄與優先順序（先具體後籠統）：

1. `deities` → 神名與稱號
2. `place_names.place_type` → 國名／帝國／王國／政權…＝民族與國名；城市／地區／行省＝地名
3. 手列的**使徒與門徒**——十二使徒加保羅等，封閉集合，且要排在主教之前：
   伯多祿既是使徒也是羅馬座第一任，對讀本而言「使徒」才是有用的標籤
4. `episcopal_succession` → 教宗與主教（`see='羅馬'` 的是教宗）
5. `theologians.role` 含教父／聖人／護教士／隱修 → 教父與聖人
6. `historical_rulers` → 君王
7. 手列的**族長與先知**——同樣是封閉集合，且不含君王（大衛歸君王）
8. `biblical_people` → 其他人名
9. 原有的 `kind`／既有分組 → 地名／民族／神名／人名
10. 查不到 → 其他人名

比對的鍵有兩把：**原文字形**（去重音折疊）與**已定的中文名**。中文那把最強，因為
登錄本身是中文優先的；但同名不同人時（雅各既是族長也是使徒）會有兩個答案，那時
一律退回較籠統的類，不擲骰子。
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "flashcards" / "proper-name-registers.json"

PLACE = "地名"
NATION = "民族與國名"
DEITY = "神名與稱號"
PATRIARCH = "族長與先知"
KING = "君王"
APOSTLE = "使徒與門徒"
BISHOP = "教宗與主教"
FATHER = "教父與聖人"
PERSON = "其他人名"
# 登錄沒說話時的去處。倒進「其他人名」等於宣稱它是人名，而我們並不知道——
# 拉丁上冊 585 條裡有 523 條就是這樣被說成人名的。
UNSORTED = "待歸類"

ORDER = [PATRIARCH, KING, APOSTLE, BISHOP, FATHER, PERSON, NATION, PLACE, DEITY]
# 印出來的次序：先地理、再神名、再人名由具體到籠統，待歸類殿後。
PRINT_ORDER = [NATION, PLACE, DEITY, PATRIARCH, KING, APOSTLE, BISHOP, FATHER,
               PERSON, "節期與聖日", UNSORTED]

# 國名那一類收的 place_type
NATION_TYPES = {"國名", "帝國", "王國", "政權", "哈里發國", "城邦", "地區／王國"}

# 十二使徒與新約明載的門徒。封閉集合，逐個確認過，不是規則推的。
# 十二使徒與新約明載的門徒，**以原文字形為鍵**。中文不能當鍵：雅各同時是族長
# Ἰακώβ 與使徒 Ἰάκωβος，猶大同時是支派 Ἰούδας 與加略人，中文分不開而原文分得開。
APOSTLE_FORMS = {
    # 十二使徒
    "πετρος", "κηφας", "petrus", "cephas",
    "ανδρεας", "andreas",
    "ιακωβος", "iacobus",                     # 使徒雅各；族長是 Ἰακώβ，少一個 ς
    "ιωαννης", "iohannes", "ioannes",
    "φιλιππος", "philippus",
    "βαρθολομαιος", "bartholomaeus",
    "θωμας", "thomas",
    "μαθθαιος", "ματθαιος", "matthaeus",
    "θαδδαιος", "thaddaeus",
    "ισκαριωτης", "iscariotes", "iscariot",
    "ματθιας", "matthias",
    # 新約明載的其他門徒與同工
    "παυλος", "paulus", "σαυλος", "saulus",
    "βαρναβας", "barnabas",
    "σιλας", "silas", "σιλουανος", "silvanus",
    "τιμοθεος", "timotheus",
    "τιτος", "titus",
    "μαρκος", "marcus",
    "λουκας", "lucas",
    "στεφανος", "stephanus",
    "απολλως", "apollos",
    "πρισκα", "πρισκιλλα", "prisca", "priscilla",
    "ακυλας", "aquila",
}

# 族長、士師、先知。中文在這一類沒有歧義的風險（同名的使徒都另有原文形），
# 所以用中文當鍵可行；君王不列在這裡，大衛與所羅門歸君王。
PATRIARCHS = {
    "亞當", "夏娃", "厄娃", "挪亞", "諾厄", "亞伯拉罕", "亞巴郎", "撒拉", "撒辣",
    "以撒", "依撒格", "以掃", "厄撒烏", "約瑟", "若瑟", "摩西", "梅瑟",
    "亞倫", "亞郎", "約書亞", "若蘇厄", "基甸", "基德紅", "參孫", "三松",
    "撒母耳", "撒慕爾", "以利", "厄里", "拿單", "納堂", "以利亞", "厄里亞",
    "以利沙", "厄里叟", "以賽亞", "依撒意亞", "耶利米", "耶肋米亞",
    "以西結", "厄則克耳", "但以理", "達尼爾", "何西阿", "歐瑟亞", "約珥", "岳厄爾",
    "阿摩司", "亞毛斯", "俄巴底亞", "亞北底亞", "約拿", "約納", "彌迦", "米該亞",
    "那鴻", "納鴻", "哈巴谷", "西番雅", "索福尼亞", "哈該", "哈蓋",
    "撒迦利亞", "匝加利亞", "瑪拉基", "瑪拉基亞", "路得", "盧德", "以斯帖", "艾斯德爾",
    "約伯", "利未", "肋未", "便雅憫", "本雅明", "施洗約翰", "洗者若翰",
}

def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^0-9A-Za-zΑ-Ωα-ωΆ-ώ֐-׿]", "", text).lower()


def fold_latin(text: str) -> str:
    """拉丁字形的折疊：I／J 與 U／V 在古典拼法裡是同一個字母，ae／oe 折成 e。

    登錄存的是英文或希臘文拼法，拉丁附錄存的是武加大拼法，兩邊對不上就整批落空：
    `Ierusalem` 與 `Jerusalem`、`Iudaei` 與 `Judaei`、`Ægyptus` 與 `Aegyptus`。
    """
    folded = fold(text)
    folded = folded.replace("æ", "ae").replace("œ", "oe")
    folded = folded.replace("ae", "e").replace("oe", "e")
    return folded.replace("j", "i").replace("v", "u").replace("y", "i")


def bare_zh(text: str) -> str:
    """去掉族譜用的區別語，「比拉（比珥之子）」只留「比拉」。"""
    return re.sub(r"（.*?）", "", text or "").strip()


def _fetch_registers() -> dict:
    import requests
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        raise SystemExit("需要 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY 才能讀登錄")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}

    def rows(table: str, select: str) -> list[dict]:
        out: list[dict] = []
        offset = 0
        while True:
            response = requests.get(
                f"{url}/rest/v1/{table}",
                params={"select": select, "limit": "1000", "offset": str(offset)},
                headers=headers, timeout=90,
            )
            response.raise_for_status()
            batch = response.json()
            out += batch
            if len(batch) < 1000:
                return out
            offset += 1000

    return {
        "deities": rows("deities", "name_original,name_english,name_recommended"),
        "place_names": rows("place_names", "name_original,name_english,name_recommended,place_type"),
        "episcopal": rows("episcopal_succession", "name_zh,name_en,see,start_year"),
        "theologians": rows("theologians", "name_original,name_english,name_latin_std,name_catholic_sgs,name_protestant,role"),
        "rulers": rows("historical_rulers", "name_original,name_english,name_recommended"),
        "biblical_people": rows("biblical_people", "name_zh,name_en"),
    }


def load_registers(refresh: bool = False) -> dict:
    """線上抓一次就存檔；分類要跑三種語言好幾輪，不必每輪都連線。"""
    if CACHE.exists() and not refresh:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    payload = _fetch_registers()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload


class Classifier:
    """把一個專名歸到九類之一，並記下是哪一份登錄說的。"""

    def __init__(self, registers: dict | None = None) -> None:
        registers = registers or load_registers()
        # 中文名 -> {類別}，原文折疊 -> {類別}
        self.by_zh: dict[str, set[str]] = defaultdict(set)
        self.by_form: dict[str, set[str]] = defaultdict(set)
        self.route: dict[tuple[str, str], str] = {}

        def add(zh: str, forms: list[str], category: str, route: str) -> None:
            zh = bare_zh(zh)
            if zh:
                self.by_zh[zh].add(category)
                self.route.setdefault((zh, category), route)
            for form in forms:
                for folded in {fold(form), fold_latin(form)}:
                    if folded:
                        self.by_form[folded].add(category)
                        self.route.setdefault((folded, category), route)

        for row in registers["deities"]:
            add(row.get("name_recommended", ""),
                [row.get("name_original", ""), row.get("name_english", "")], DEITY, "deities")

        for row in registers["place_names"]:
            category = NATION if (row.get("place_type") or "") in NATION_TYPES else PLACE
            add(row.get("name_recommended", ""),
                [row.get("name_original", ""), row.get("name_english", "")], category, "place_names")

        # 主教表有五千多筆，絕大多數是近現代人。以中文當鍵時，任何常見的聖經名字
        # 都會被某位後世主教認走——實測把亞拿尼亞、拉撒路、腓力斯都判成了主教。
        # 因此只收古代教座、且只收讀本涵蓋的年代（至 800 年）。
        ancient_sees = {"羅馬", "君士坦丁堡", "亞歷山卓", "安提阿", "耶路撒冷",
                        "迦太基", "米蘭", "凱撒利亞", "希坡"}
        for row in registers["episcopal"]:
            if row.get("see") not in ancient_sees:
                continue
            start = row.get("start_year")
            if isinstance(start, int) and start > 800:
                continue
            add(row.get("name_zh", ""), [row.get("name_en", "")], BISHOP,
                "episcopal_succession" + ("／羅馬座" if row.get("see") == "羅馬" else ""))

        for row in registers["theologians"]:
            role = row.get("role") or ""
            if not re.search(r"教父|聖人|護教士|隱修|教會博士", role):
                continue
            add(row.get("name_catholic_sgs") or row.get("name_protestant") or "",
                [row.get("name_original", ""), row.get("name_english", ""),
                 row.get("name_latin_std", "")], FATHER, "theologians")

        for row in registers["rulers"]:
            add(row.get("name_recommended", ""),
                [row.get("name_original", ""), row.get("name_english", "")], KING, "historical_rulers")

        for row in registers["biblical_people"]:
            add(row.get("name_zh", ""), [row.get("name_en", "")], PERSON, "biblical_people")

    def classify(self, *, zh: str = "", form: str = "", english: str = "",
                 existing_kind: str = "") -> tuple[str, str]:
        """回傳 (類別, 依據)。判不出來就是 ("", "")，交給呼叫端決定放哪。"""
        zh = bare_zh(zh)

        # 手列的兩個封閉集合最先，且使徒排在主教之前。使徒以原文字形為鍵，
        # 族長以中文為鍵——兩邊各取沒有歧義的那一把。
        if APOSTLE_FORMS & {fold(form), fold_latin(form), fold(english), fold_latin(english)}:
            return APOSTLE, "手列使徒門徒（原文字形）"
        if zh in PATRIARCHS:
            return PATRIARCH, "手列族長先知"

        candidates: set[str] = set()
        if zh:
            candidates |= self.by_zh.get(zh, set())
        for key in (fold(form), fold_latin(form), fold(english), fold_latin(english)):
            if key:
                candidates |= self.by_form.get(key, set())

        if not candidates:
            # 沒有登錄說話時，退回原本那一欄粗的分類
            fallback = {"place": PLACE, "people": NATION, "deity": DEITY,
                        "person": PERSON}.get(existing_kind, "")
            return (fallback, "既有 kind 欄") if fallback else (UNSORTED, "")

        for category in ORDER:
            if category in candidates:
                route = (self.route.get((zh, category))
                         or self.route.get((fold(form), category))
                         or self.route.get((fold(english), category))
                         or "登錄")
                # 同名不同人：登錄同時說得出兩個「人」類，退回較籠統的
                person_hits = {c for c in candidates if c in
                               (PATRIARCH, KING, APOSTLE, BISHOP, FATHER)}
                if BISHOP in person_hits and PERSON in candidates:
                    # 聖經裡就有的名字，被後世某位主教同名撞到：讀本讀的是聖經。
                    return PERSON, "聖經人物與後世主教同名，取聖經人物"
                if len(person_hits) > 1:
                    return PERSON, "同名不同人，退回其他人名"
                return category, route
        return UNSORTED, ""
