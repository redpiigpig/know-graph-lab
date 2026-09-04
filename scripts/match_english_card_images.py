#!/usr/bin/env python3
"""替國小英語單字卡挑圖。**這副卡不留白**——一張都不行。

跟希伯來、希臘、拉丁三副的差別有兩個：

一、**這副卡的字頭本身就是英文**，而 OpenMoji 的本名也是英文，所以「本名精確
比對」在這裡是最強的一關。也因此 `AMBIGUOUS_EN` 那張表要換個用法：別副擋掉
watch、bear、star 是因為那是**翻譯**（希伯來文的某個詞譯成 bear，到底是熊還是
承受，看不出來）；這副卡的 bear 就是英文的 bear，旁邊還有中文說了是「熊」。
所以這裡不是擋掉，而是**降級**：這些詞不自動配，改由人工指名決定。

二、**留白不是選項**（使用者 2026-09-04：「國小單字卡不能留白」）。別副的最後
一關是「挑不到就空著」，這副的最後一關是**當場報錯**，逼人把它補完。所以層數
比別副多兩層：自己畫的圖，與 Iconify 的線條圖庫。

七關，由嚴到寬：

1. **自己畫的圖**（`english_picture_tiles.py`）：數字、星期、月份、上下午。
   這批詞任何圖庫都沒有，而近似的圖是錯的（`eleven o'clock` 是時鐘不是十一）。
2. **國旗**：國名卡要的正是國旗，而 `load_openmoji()` 刻意擋掉旗幟群組
   （別副的詞不該配到國旗），所以這裡自己讀原始清單。
3. **人工指名**（`OVERRIDES`）：以 OpenMoji 的本名指定，寫錯當場報錯。
4. **站上既有配圖**：`/english` 課程頁自己標好的 hexcode。
   🚨 那批是拿英文名自動配的，錯得很兇（見 OVERRIDES 的註解），所以排在人工之後。
5. **本名精確比對**，絕不比對標籤欄——比標籤會把「房屋」配成盆栽。
6. **繁中詞義轉移**：五副原文卡已經配過的中文詞義就沿用（「火」→ 同一張火）。
7. **Iconify 線條圖庫**（game-icons／Phosphor／MDI／Tabler），染成單一藍色。
   彩色 emoji 畫不出來的抽象詞靠這一層。

授權：OpenMoji 17.0.0（CC BY-SA 4.0）＋ game-icons（CC BY 3.0）、Phosphor（MIT）、
Material Design Icons（Apache 2.0）、Tabler（MIT）＋ 本專案自繪。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))

from match_flashcard_images import (  # noqa: E402
    AMBIGUOUS_EN,
    CACHE,
    OPENMOJI,
    ensure_openmoji,
    image_path,
    load_openmoji,
)

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data/originalReaders/vocabulary/english-1000.json"
OUTPUT = CACHE / "english-card-images.json"
TILE_DIR = CACHE / "english-tiles"
ICON_DIR = CACHE / "english-icons"
TRANSFER_MAPS = ("hebrew-card-images.json", "greek-card-images.json",
                 "latin-card-images.json")

API = "https://api.iconify.design"
USER_AGENT = {"User-Agent": "know-graph-lab/1.0 (private study flashcards)"}
# Iconify 那四個庫是單色線條圖，抓下來預設是黑的。這副卡是給小學生用的，
# 全黑線條擺在彩色 emoji 中間像沒畫完，所以統一染成一個藍。
ICON_COLOR = "1E6FD9"

# 人工指名的圖。左邊是卡上的字頭，右邊是 OpenMoji 的**本名**。
# 🚨 名字不等於圖，每一筆都先用 flashcard_contact_sheet.py 看過。
OVERRIDES: dict[str, str] = {
    # ── 一詞多義：英文字頭本身有兩三個義，中文詞義說了是哪一個 ──
    # 🚨 站上那 559 個 hexcode 正是「拿英文名自動比對」配出來的，這一批因此錯得
    # 最兇：order 點餐配到獅子（lion 的 order 是「目」）、spell 拼單字配到巫師、
    # fly 飛行配到蒼蠅、spring 春天配到蜜蜂、table 桌子配到桌球、cross 越過配到
    # 交叉手指。override 排在 preset 前面就是為了蓋掉它們。
    "fine": "OK hand",                        # 好的（站上是 😐）
    "wave": "waving hand",                    # 揮手
    "bow": "person bowing",                   # 鞠躬
    "count": "abacus",                        # 計算
    "star": "star",                           # 星形
    "box": "package",                         # 箱子（站上是 🍱 便當）
    "hand": "hand with fingers splayed",      # 手
    "point": "backhand index pointing up",    # 指出（站上是 💯）
    "sound": "speaker high volume",           # 聲音
    "read": "open book",                      # 閱讀
    "sorry": "confused face",                 # 對不起
    "bear": "bear",                           # 熊
    "order": "receipt",                       # 點餐（站上是 🦁）
    "school": "school",                       # 學校
    "ruler": "straight ruler",                # 尺
    "pen": "pen",                             # 原子筆
    "spell": "input latin letters",           # 拼單字（站上是 🧙 巫師的咒語）
    "mark": "hundred points",                 # 打分數
    "light": "light bulb",                    # 燈光（站上是淺藍色的心）
    "watch": "watch",                         # 錶
    "spring": "cherry blossom",               # 春天（站上是 🐝 蜜蜂）
    "wind": "wind face",                      # 風
    "rose": "rose",                           # 玫瑰花
    "ring": "ring",                           # 戒指
    "kind": "smiling face with smiling eyes",  # 親切的
    "draw": "artist palette",                 # 畫圖
    "band": "guitar",                         # 樂隊
    "story": "scroll",                        # 故事
    "fast": "dashing away",                   # 快速
    "hide": "see-no-evil monkey",             # 隱藏
    "cross": "children crossing",             # 越過（站上是 🤞 交叉手指）
    "left": "left arrow",                     # 左邊
    "right": "right arrow",                   # 右邊
    "back": "back arrow",                     # 後面的
    "bank": "bank",                           # 銀行
    "park": "national park",                  # 公園
    "train": "train",                         # 火車
    "fly": "airplane departure",              # 飛行（站上是 🪰 蒼蠅）
    "present": "wrapped gift",                # 禮物
    "table": "fork and knife with plate",     # 桌子（站上是 🏓 桌球）
    "fork": "fork and knife",                 # 叉子
    "knife": "kitchen knife",                 # 刀
    "fan": "folding hand fan",                # 電風扇
    "line": "straight ruler",                 # 線
    "head": "brain",                          # 頭
    
    "lead": "backhand index pointing right",  # 指導
    "season": "leaf fluttering in wind",      # 季節
    "space": "milky way",                     # 空間
    "part": "puzzle piece",                   # 部分
    "mean": "left speech bubble",             # 意思
    # ── 人稱、疑問與招呼 ──
    "it": "backhand index pointing down",
    "we": "people holding hands",
    "they": "family",
    "welcome": "open hands",
    "meet": "handshake",
    "with": "link",
    "what": "red question mark",
    "whose": "white question mark",
    "good morning": "sunrise",
    "good afternoon": "sun",
    "good evening": "sunset",
    "good night": "crescent moon",
    "shake hands": "raised back of hand",
    "thumbs up": "thumbs up",
    "clap": "clapping hands",
    "hug": "people hugging",
    "wink": "winking face",
    "whisper": "shushing face",
    "greeting": "waving hand",
    "introduce": "person raising hand",
    "nickname": "name badge",
    "birthday": "birthday cake",
    "hometown": "houses",
    "neighbor": "derelict house",
    "guest": "person tipping hand",
    "lady": "woman",
    # ── 數與量 ──
    "zero": "keycap: 0",
    "plus": "plus",
    "minus": "minus",
    "add": "abacus",
    "equal": "heavy equals sign",
    "size": "straight ruler",
    "pack": "package",
    "pair": "socks",
    "piece": "puzzle piece",
    # ── 形狀與顏色 ──
    "round": "black circle",
    "rectangle": "black rectangle",
    "oval": "white circle",
    "cube": "ice",           # 立方體（與 ice 冰塊同一張，OpenMoji 的 🧊 就是方塊冰）
    "silver": "2nd place medal",
    "wide": "left-right arrow",
    "narrow": "pinching hand",
    "thick": "books",
    "corner": "triangular ruler",
    "triangle": "triangular ruler",
    "heart shape": "red heart",
    "arrow": "right arrow",
    "gem": "gem stone",
    "brick": "brick",
    "puzzle": "puzzle piece",
    "balloon": "balloon",
    "ribbon": "ribbon",
    # ── 身體與動作 ──
    "take": "open hands",
    "party": "party popper",
    "sunny": "sun with face",
    "cold": "cold face",
    "excited": "grinning squinting face",
    "nervous": "grimacing face",
    "stupid": "woozy face",
    "time": "hourglass not done",
    "way": "compass",
    "play": "teddy bear",
    "serious": "neutral face",
    "work": "briefcase",
    "sweet": "honey pot",
    "gray": "grey heart",
    "black": "black heart",
    "white": "white heart",
    "circle": "hollow red circle",
    "round": "black circle",
    "dinner": "shallow pan of food",
    "movie": "clapper board",
    "pumpkin": "jack-o-lantern",
    "sand": "desert",
    "festival": "fireworks",
    "fix": "wrench",
    "funny": "face with tears of joy",
    "joy": "rolling on the floor laughing",
    "win": "sports medal",
    "beach": "beach with umbrella",
    "sir": "saluting face",
    "good": "thumbs up",
    "tell": "speaking head",
    "waiter": "man in tuxedo",
    "bag": "handbag",
    "strong": "person lifting weights",
    "juice": "cup with straw",
    "mind": "exploding head",
    "video": "movie camera",
    "game": "video game",
    "doctor": "man health worker",
    "nurse": "woman health worker",
    "worker": "construction worker",
    "build": "building construction",
    "no": "prohibited",
    "river": "water wave",
    "call": "mobile phone",
    "use": "hammer and wrench",
    "stop": "stop sign",
    # ── 家人與稱謂 ──
    "husband": "man",
    "uncle": "man: beard",
    "aunt": "older person",
    "cousin": "people with bunny ears",
    "classmate": "graduation cap",
    "nephew": "boy",
    "Mr.": "person in suit levitating",
    "Mrs.": "woman with veil",
    "Ms.": "woman with headscarf",
    "dear": "sparkling heart",
    "teenager": "backpack",
    "foreigner": "globe with meridians",
    "anyone/anybody": "busts in silhouette",
    "important": "red exclamation mark",
    # ── 食物 ──
    "menu": "clipboard",
    "dinner": "shallow pan of food",
    "noodles": "steaming bowl",
    "beef": "cut of meat",
    "ham": "poultry leg",
    "snack": "pretzel",
    "thirsty": "sweat droplets",
    "coke": "cup with straw",
    "guava(s)": "green apple",
    "papaya(s)": "mango",
    "oyster omelet": "oyster",
    "soy milk": "glass of milk",
    "stinky tofu": "steaming bowl",
    "egg pancake": "pancakes",
    "fried chicken": "poultry leg",
    "pearl milk tea": "bubble tea",
    "beef noodle(s)": "steaming bowl",
    "tofu pudding": "custard",
    "brown sugar cake": "moon cake",
    "oyster noodle(s)": "oyster",
    "squid soup": "squid",
    "fried bread stick(s)": "baguette bread",
    "handmade noodle(s)": "steaming bowl",
    "Taiwanese Snacks": "takeout box",
    # ── 學校 ──
    "classroom": "school",
    "elementary school": "backpack",
    "junior high school": "school",
    "senior high school": "graduation cap",
    "lesson": "open book",
    "program": "spiral notepad",
    "group": "busts in silhouette",
    "blackboard": "teacher",
    "chalk": "pencil",
    "eraser": "wastebasket",
    "dictionary": "closed book",
    "word": "input latin letters",
    "homework": "spiral notepad",
    "workbook": "notebook",
    "example": "bookmark tabs",
    "English": "input latin lowercase",
    "sentence": "page facing up",
    "history": "hourglass done",
    "language": "input latin letters",
    "glue": "adhesive bandage",
    "colored pencil": "crayon",
    "read": "open book",
    "cheat": "eyes",
    "prepare": "toolbox",
    "correct": "check mark button",
    "end": "end arrow",
    "borrow": "inbox tray",
    "lend": "outbox tray",
    "join": "plus",
    # ── 家 ──
    "apartment": "office building",
    "bedroom": "bed",
    "dining room": "fork and knife with plate",
    "living room": "couch and lamp",
    "knock": "oncoming fist",
    "towel": "person taking bath",
    "sofa": "couch and lamp",
    "desk": "desktop computer",
    "refrigerator/fridge": "ice",
    # ── 方位與時間 ──
    "in": "inbox tray",
    "on": "top arrow",
    "under": "down arrow",
    "near": "round pushpin",
    "beside": "left-right arrow",
    "below": "down-right arrow",
    "minute": "stopwatch",
    "hour": "one o’clock",
    "o clock": "three o’clock",
    "noon": "twelve o’clock",
    "afternoon": "sun behind cloud",
    "tonight": "night with stars",
    "eve": "confetti ball",
    "yesterday": "counterclockwise arrows button",
    "then": "last track button",
    "early": "sunrise over mountains",
    "late": "sunset",
    "before": "fast reverse button",
    "after": "fast-forward button",
    "soon": "soon arrow",
    "always": "infinity",
    "often": "repeat button",
    # ── 天氣與自然 ──
    "rainy": "cloud with rain",
    "windy": "leaf fluttering in wind",
    "warm": "hot face",
    "clear": "sun behind small cloud",
    "grass": "herb",
    "hill": "mount fuji",
    "land": "world map",
    "snowy": "cloud with snow",
    # ── 衣著與外表 ──
    "swimsuit": "one-piece swimsuit",
    "pocket": "jeans",
    "boots": "hiking boot",
    "slippers": "thong sandal",
    "belt": "jeans",
    "raincoat": "umbrella with rain drops",
    "beautiful": "smiling face with heart-eyes",
    "handsome": "smiling face with sunglasses",
    "tall": "giraffe",
    "thin": "pinching hand",
    "fat": "pig face",
    "friendly": "smiling face with open hands",
    "weak": "wilted flower",
    # ── 心情與行動 ──
    "try": "flexed biceps",
    "enjoy": "relieved face",
    "hope": "crossed fingers",
    "belong": "locked with key",
    "fun": "partying face",
    "cheer": "raising hands",
    "boring": "yawning face",
    "polite": "person bowing",
    "careful": "warning",
    "hobby": "artist palette",
    "team": "people holding hands",
    "jog": "person running",
    "show": "performing arts",
    "camp": "camping",
    "favorite": "star-struck",
    "noise": "loudspeaker",
    "interested": "star-struck",
    "dodge ball": "person playing handball",
    "exciting": "fire",
    "interesting": "thinking face",
    "lose": "crying face",
    "practice": "flexed biceps",
    "carry": "shopping bags",
    "put": "palm down hand",
    "find": "magnifying glass tilted left",
    # ── 方位副詞 ──
    "along": "right arrow curving up",
    "around": "counterclockwise arrows button",
    "up": "up arrow",
    "down": "down arrow",
    "front": "backhand index pointing right",
    "side": "left-right arrow",
    "inside": "inbox tray",
    "outside": "outbox tray",
    "low": "down-right arrow",
    # ── 職業與人 ──
    "driver": "man with veil",
    "leader": "person with crown",
    "shopkeeper": "convenience store",
    "waiter": "man in tuxedo",
    "waitress": "woman office worker",
    "fisherman": "fishing pole",
    "writer": "writing hand",
    "police man": "police officer",
    "businessman": "necktie",
    "experience": "military medal",
    "chance": "game die",
    "plan": "spiral calendar",
    "own": "key",
    "fireman": "firefighter",
    "possible": "white question mark",
    "salesman": "shopping cart",
    "mailman/mail carrier": "postbox",
    "stupid": "confused face",
    "successful": "trophy",
    "popular": "party popper",
    "strange": "alien",
    "able": "flexed biceps",
    "famous": "glowing star",
    "busy": "person running",
    
    "honest": "handshake",
    # ── 城鎮與地名 ──
    "street": "motorway",
    "bookstore": "books",
    "convenient store": "convenience store",
    "shop": "shopping bags",
    "supermarket": "shopping cart",
    "sale": "money with wings",
    "MRT": "metro",
    "airport": "airplane arrival",
    "visit": "luggage",
    # 台灣地名沒有各自的圖，用該地最具代表性的事物；卡面另有中文，不會誤讀成別的詞。
    "Taipei": "cityscape",
    "New Taipei": "houses",
    "Beitou": "hot springs",
    "Taoyuan": "peach",
    "Taichung": "ferris wheel",
    "Tainan": "classical building",
    "Kaohsiung": "ship",
    "Hualien": "snow-capped mountain",
    # ── 抽象詞：畫不出場景，就給一個符號 ──
    # 這一段是這副卡最難的十六張。圖庫裡沒有 understand、ready、basic 這種概念的
    # 圖示（Iconify 兩萬五千個名字裡一個都沒有），而使用者要的是不留白，所以照
    # 單字卡一貫的「虛詞給符號不給場景」處理：符號對抽象詞是誠實的，近似的場景圖
    # 不是。correct ✅／wrong ❎、mistake ❌ 成組，看得出關係。
    "last": "end arrow",                      # 最後的（與 end 最後同義，共用一張）
    "fact": "pushpin",                        # 事實＝釘住的那件事
    "understand": "OK button",                # 了解（fine 用的是 👌，不同張）
    "mistake": "cross mark",                  # 錯誤
    "wrong": "cross mark button",             # 錯誤的（與 correct ✅ 成組）
    "excellent": "1st place medal",           # 傑出的
    "ready": "green circle",                  # 準備好的＝綠燈
    "special": "sparkles",                    # 特別的
    "same": "heavy equals sign",              # 相同的（與 equal 等於同義，共用一張）
    "basic": "abacus",                        # 基本的（與 count 計算同一張，都是最基礎的算具）
    "become": "clockwise vertical arrows",    # 變成
    "give": "palm up hand",                    # 給
    "let": "unlocked",                        # 讓＝放行
    "want": "drooling face",                  # 要
    "east": "sunrise",
    "Chinese New Year": "red paper lantern",
    # ── 第三輪：逐張看樣張抓出來的（站上那批自動配圖的錯） ──
    "food": "bento box",                      # 食物（站上是 😋，那是 delicious）
    "summer": "sunflower",                    # 夏天（站上是 🍺 啤酒）
    "sea": "water wave",                      # 海洋（站上是 🧜 人魚）
    "cut": "scissors",                        # 割
    "nod": "head shaking vertically",         # 點頭
    "guess": "person shrugging",              # 猜想
    "gift": "wrapped gift",                   # 禮物（與 present 同一個中文，共用一張）
    # ── 節慶 ──
    "Dragon Boat Festival": "dragon",
    "Moon Festival": "moon cake",
}

# 有些概念 OpenMoji 根本沒有畫（不同的、圖書館、地板、不等於……），或者能用的那
# 張已經給了別的詞。這一批改指名 Iconify 的線條圖，抓下來染成同一個藍。
# 🚨 這裡指的是**確切的圖示 id**（`mdi:library`），不是關鍵詞搜尋——搜尋出來的
# 東西看起來像成功而畫的常是別的東西（`mdi:iron` 是熨斗不是鐵）。
ICONIFY_OVERRIDES: dict[str, str] = {
    # 疑問詞：五個字原本共用同一個 ❓，那等於教成同一件事。
    "what": "mdi:help-circle",
    "who": "mdi:account-question",
    "where": "mdi:map-marker-question",
    "when": "mdi:calendar-question",
    "why": "mdi:help-rhombus",
    "which": "mdi:progress-question",
    "whose": "mdi:account-key",
    "how": "mdi:head-question",
    # 大小、內外、前後這幾組是**語意相對**的，共用一張圖就是教錯。
    "large": "mdi:arrow-expand",
    "small": "mdi:arrow-collapse",
    "short": "mdi:arrow-collapse-vertical",
    "inside": "mdi:home-import-outline",
    "outside": "mdi:home-export-outline",
    "front": "mdi:arrange-bring-forward",
    "behind": "mdi:arrange-send-backward",
    "open": "mdi:door-open",
    "close": "mdi:door-closed",
    "he": "mdi:human-male",
    "she": "mdi:human-female",
    # OpenMoji 沒畫的概念
    "nobody": "mdi:account-off",
    "poor": "mdi:cash-remove",
    "sure": "mdi:shield-check",
    "easy": "ph:feather",
    "street": "mdi:road",
    "eraser": "mdi:eraser",
    "farm": "mdi:barn",
    "class": "ph:student",
    "button": "game-icons:shirt-button",
    "address": "mdi:home-map-marker",
    "block": "mdi:road-variant",
    "wait": "mdi:human-queue",
    "marker": "mdi:marker",
    "helpful": "mdi:hand-heart",
    "air": "ph:wind",
    "lake": "mdi:waves",
    "shape": "mdi:shape",
    "different": "mdi:not-equal-variant",
    "library": "mdi:library",
    "knowledge": "ph:lightbulb-filament",
    "lesson": "mdi:book-open-variant",
    "get": "mdi:tray-arrow-down",
    "bring": "mdi:tray-arrow-up",
    "know": "mdi:head-check",
    "come": "mdi:human-greeting",
    "enter": "mdi:location-enter",
    "into": "mdi:location-enter",
    "lead": "ph:hand-pointing",
    "yes/yeah": "mdi:check-bold",
    "OK": "mdi:emoticon-happy",
    "leave": "mdi:exit-run",
    "bright": "mdi:brightness-7",
    "question": "mdi:comment-question",
    "stranger": "mdi:incognito",
    "blackboard": "mdi:presentation",
    "ham": "game-icons:ham-shank",
    "true": "mdi:check-decagram",
    "agree": "mdi:thumb-up-outline",
    "make": "game-icons:anvil",
    "hard-working": "mdi:account-hard-hat",
    "try": "game-icons:target-dummy",
    "practice": "mdi:dumbbell",
    "able": "mdi:arm-flex",
    "country": "mdi:flag-variant",
    "floor": "mdi:floor-plan",
    "feel": "mdi:heart-pulse",
    "case": "mdi:folder-account",
    "cool": "mdi:air-conditioner",
    "early": "mdi:clock-fast",
    "dining room": "mdi:table-chair",
    "cousin": "game-icons:family-tree",
    "bottle": "mdi:bottle-soda-classic",
    "drink": "mdi:cup-water",
    "coke": "game-icons:soda-can",
    "born": "mdi:baby-carriage",
    "job": "mdi:badge-account-horizontal",
    "place": "mdi:map-marker",
    "popular": "mdi:heart-multiple",
    "restaurant": "game-icons:hot-meal",
    "skirt": "game-icons:skirt",
    "pretty": "mdi:flower-tulip",
    "morning": "mdi:weather-sunset-up",
    "oval": "mdi:ellipse-outline",
    # ── 第二輪：把「語意相對」或「不相干」還在共用同一張的拆開 ──
    "hungry": "mdi:stomach",
    "full": "mdi:gauge-full",
    "cheat": "game-icons:spy",
    "thick": "mdi:layers-triple",
    "rule": "mdi:gavel",
    "old": "mdi:human-cane",
    "wise": "game-icons:wisdom",
    "classmate": "mdi:human-male-female-child",
    "senior high school": "mdi:school",
    "elementary school": "mdi:school-outline",
    "teenager": "mdi:account-star",
    "fat": "game-icons:fat",
    "pocket": "mdi:pocket",
    "belt": "game-icons:belt-buckles",
    "spell": "mdi:spellcheck",
    "language": "mdi:translate",
    "here": "mdi:map-marker-radius",
    "there": "mdi:map-marker-distance",
    "collect": "mdi:collage",
    "common": "mdi:approximately-equal-box",
    "honest": "mdi:hand-heart-outline",
    "meeting": "mdi:presentation-play",
    "hobby": "mdi:heart-circle",
    "line": "mdi:vector-line",
    "size": "mdi:resize",
    "math/mathematics": "mdi:calculator",
    "idea": "ph:lightbulb",
    "dream": "mdi:sleep",
    "remember": "mdi:brain",
    "friend": "mdi:account-heart",
    "everyone/everybody": "mdi:account-multiple",
    "group": "mdi:account-group",
    "stinky tofu": "game-icons:cube",
    "oyster noodle(s)": "mdi:noodles",
    "brown sugar cake": "game-icons:cake-slice",
    "classroom": "mdi:google-classroom",
    "living room": "mdi:sofa-outline",
    "answer": "mdi:comment-check",
    "refrigerator/fridge": "mdi:fridge",
    "side": "mdi:page-layout-sidebar-right",
    "wide": "mdi:arrow-expand-horizontal",
    "late": "mdi:clock-alert",
    "west": "mdi:arrow-left-bold-circle",
    "north": "mdi:arrow-up-bold-circle",
    "how": "mdi:head-question",
    "pretty": "mdi:flower-tulip",
    "morning": "mdi:weather-sunset-up",
    # ── 第四輪：繁中詞義轉移那一層看過的 ──
    "touch": "mdi:gesture-tap-hold",          # 觸碰（原本與 point 指出共用 ☝️）
    "meal": "mdi:silverware-variant",         # 一餐（原本與 dinner 晚餐共用 🥘）
    "dark": "mdi:invert-colors",              # 深色的（原本與 round 圓的一樣是個黑圓）
    "simple": "ph:feather",                   # 簡單的（與 easy 同義，共用一張）
    "appear": "mdi:eye-plus-outline",         # 似乎（原本是一條波浪線）
    "problem": "mdi:alert-circle",            # 問題（原本是一顆石頭）
    "shoulder": "game-icons:shoulder-armor",  # 肩膀（原本是機械手臂）
    "matter": "mdi:file-question",            # 事情（原本與 work 工作共用公事包）
    "need": "mdi:priority-high",              # 需要（原本與 important 共用 ❗）
    "healthy": "game-icons:health-normal",    # 健康的（原本與 strong 共用舉重）
    "decide": "mdi:call-split",               # 決定（原本與 enjoy 共用 😌）
    "keep": "mdi:content-save",               # 保持（原本與 safe 安全的共用 🔒）
    # ── 第三輪：逐張看樣張抓出來的 ──
    # 🚨 you 站上配到的 `index pointing at the viewer` 印出來像一顆拳頭——
    # skill 早就記過這一張，這副卡又踩了一次。
    "you": "mdi:hand-pointing-right",
    "real": "mdi:diamond-stone",              # 真正的（原本與 have 有共用同一個 ✔️）
    # 站上那批自動配圖錯得離譜的幾張：body 身體配到骷髏、age 年紀配到 🔞、
    # comic 漫畫配到 💩、summer 夏天配到啤酒、soldier 軍人配到忍者。
    "body": "mdi:human",
    "age": "mdi:calendar-account",
    "care": "mdi:heart-plus",
    "new": "mdi:new-box",
    "Miss": "mdi:face-woman-outline",
    "pick": "mdi:gesture-tap",
    "help": "mdi:hand-extended",
    "medium": "mdi:alpha-m-box",
    "speak": "mdi:account-voice",
    "gold": "game-icons:gold-bar",
    "sugar": "game-icons:sugar-cane",
    "bite": "game-icons:tooth",
    "eat": "game-icons:eating",
    "fresh": "mdi:leaf",
    "grade": "mdi:certificate",
    "hard": "game-icons:stone-block",
    "difficult": "game-icons:mountain-climbing",
    "ground": "mdi:terrain",
    "home": "mdi:home-heart",
    "garden": "mdi:flower-outline",
    "machine": "mdi:cog",
    "test": "mdi:file-document-edit",
    "paper": "mdi:file-outline",
    "pass": "mdi:check-underline",
    "copy": "mdi:content-copy",
    "ask": "mdi:message-question",
    "room": "mdi:view-quilt",
    "lamp": "mdi:lamp",
    "kitchen": "mdi:countertop",
    "night": "mdi:weather-night",
    "change": "mdi:swap-horizontal",
    "burn": "mdi:fire-alert",
    "long": "mdi:tape-measure",
    "heavy": "mdi:weight",
    "notice": "mdi:eye-check",
    "comfortable": "mdi:seat-recline-extra",
    "excuse": "mdi:comment-alert-outline",
    "dry": "mdi:water-off",
    "forest": "mdi:forest",
    "believe": "mdi:hands-pray",
    "proud": "mdi:emoticon-cool-outline",
    "comic": "mdi:book-multiple",
    "sport": "mdi:whistle",
    "club": "mdi:account-group-outline",
    "out": "mdi:exit-to-app",
    "rich": "mdi:cash-multiple",
    "boss": "mdi:account-tie",
    "soldier": "game-icons:round-shield",
    "store": "mdi:store",
    "market": "mdi:storefront-outline",
    "officer": "mdi:account-tie-hat",
    "life": "mdi:sprout",
    "medicine": "mdi:pill",
    "health": "mdi:medical-bag",
    "public": "mdi:city-variant-outline",
}

# 國名與國籍卡直接用國旗。`load_openmoji()` 刻意擋掉旗幟群組（希伯來文的某個
# 詞不該配到國旗），所以這裡另外讀原始清單，只給這幾張卡用。
FLAGS: dict[str, str] = {
    "Taiwan": "flag: taiwan",
    "America": "flag: united states",
    "American": "flag: united states",
    "China": "flag: china",
    "Chinese": "flag: china",
    "Japan": "flag: japan",
    "Korea": "flag: south korea",
    "Singapore": "flag: singapore",
    "Hong Kong": "flag: hong kong sar china",
    "Vietnam": "flag: vietnam",
    "Thailand": "flag: thailand",
    "the Philippines": "flag: philippines",
    "Malaysia": "flag: malaysia",
    "Canada": "flag: canada",
    "Australia": "flag: australia",
    "England": "flag: england",
    "France": "flag: france",
    "Germany": "flag: germany",
    "India": "flag: india",
}

# 站上把冠詞、斜線變體混在字頭裡（`father/dad`、`eye(s)`），比對前要拆開。
SPLIT = re.compile(r"[/(),]")


def candidates(headword: str) -> list[str]:
    """`math/mathematics` 兩個都試；`eye(s)` 先試 eye 再試 eyes。"""

    out: list[str] = []
    for part in SPLIT.split(headword.lower()):
        part = part.strip()
        if not part:
            continue
        out.append(part)
        if part.endswith("es"):
            out.append(part[:-2])
        elif part.endswith("s"):
            out.append(part[:-1])
    if "(" in headword:                       # eye(s) -> eyes
        out.insert(1, re.sub(r"[()]", "", headword.lower()).strip())
    seen, unique = set(), []
    for item in out:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def senses(gloss: str) -> list[str]:
    return [key for key in (gloss.strip(), gloss.split("；")[0].strip()) if key]


def module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def all_openmoji() -> dict[str, str]:
    """含旗幟群組的完整本名索引，只給 FLAGS 用。"""

    index: dict[str, str] = {}
    for entry in json.loads(OPENMOJI.read_text(encoding="utf-8")):
        if entry.get("skintone"):
            continue
        name = (entry.get("annotation") or "").strip().lower()
        if name:
            index.setdefault(name, entry["hexcode"])
    return index


def transfer_table() -> dict[str, str]:
    """五副原文卡已經配好的「中文詞義 → 圖」，白撿的一層。"""

    table: dict[str, str] = {}
    for name in TRANSFER_MAPS:
        path = CACHE / name
        if not path.exists():
            continue
        for record in json.loads(path.read_text(encoding="utf-8"))["images"].values():
            for key in senses(record.get("glossZh") or ""):
                table.setdefault(key, record["hexcode"])
    return table


def icon_png(icon: str) -> Path:
    """抓 Iconify 圖示並染色。單色圖用 `?color=` 就上得了色，不必自己改 SVG。"""

    path = ICON_DIR / f"{icon.replace(':', '-')}.png"
    if path.exists():
        return path
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    prefix, name = icon.split(":", 1)
    svg = ICON_DIR / f"{icon.replace(':', '-')}.svg"
    if not svg.exists():
        request = urllib.request.Request(
            f"{API}/{prefix}/{name}.svg?height=618&color=%23{ICON_COLOR}",
            headers=USER_AGENT)
        svg.write_bytes(urllib.request.urlopen(request, timeout=60).read())
        time.sleep(0.2)
    page = fitz.open(svg)[0]
    scale = 618 / max(page.rect.width, page.rect.height)
    page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True).save(path)
    return path


def iconify_lookup(names: dict[str, str], word: str) -> Path | None:
    """線條圖庫的本名精確比對。只認本名，不做子字串——`ear` 不可以命中 `search`。"""

    for candidate in candidates(word):
        for form in (candidate, candidate.replace(" ", "-")):
            icon = names.get(form)
            if icon:
                return icon_png(icon)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="替國小英語單字卡挑圖；這副卡不留白")
    parser.add_argument("--uncovered", type=int, default=0,
                        help="列出前 N 張沒有配圖的卡，供人工挑圖")
    parser.add_argument("--allow-blank", action="store_true",
                        help="補圖過程中暫時允許留白；定稿不可以用")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    ensure_openmoji()
    entries = json.loads(VOCAB.read_text(encoding="utf-8"))["entries"]
    by_name = load_openmoji()
    by_hexcode = all_openmoji()
    by_meaning = transfer_table()
    tiles = module("english_picture_tiles").render_all(TILE_DIR)
    icon_names = module("iconify_card_images").icon_names()

    assigned: dict[str, dict] = {}
    unresolved: list[str] = []
    blank: list[dict] = []
    order = ("tile", "flag", "override", "preset", "annotation", "zh_transfer", "iconify")
    sources = dict.fromkeys(order + ("none",), 0)

    for entry in entries:
        word, gloss = entry["en"], entry["zh"]
        chosen: Path | None = None
        source = None

        if word in tiles:
            chosen, source = tiles[word], "tile"

        if not chosen and word in FLAGS:
            hexcode = by_hexcode.get(FLAGS[word].lower())
            if hexcode and image_path(hexcode):
                chosen, source = image_path(hexcode), "flag"
            else:
                unresolved.append(f"{word} -> {FLAGS[word]!r}（國旗）")

        if not chosen and ICONIFY_OVERRIDES.get(word):
            chosen, source = icon_png(ICONIFY_OVERRIDES[word]), "iconify"

        if not chosen and OVERRIDES.get(word):
            wanted = OVERRIDES[word]
            found = by_name.get(wanted.lower())
            if found and image_path(found["hexcode"]):
                chosen, source = image_path(found["hexcode"]), "override"
            else:
                unresolved.append(f"{word} -> {wanted!r}")

        if not chosen and entry.get("openmoji") and image_path(entry["openmoji"]):
            chosen, source = image_path(entry["openmoji"]), "preset"

        if not chosen:
            for candidate in candidates(word):
                # 一詞多義的字頭不自動配：要嘛人工指名，要嘛交給後面幾層。
                if candidate in AMBIGUOUS_EN:
                    continue
                found = by_name.get(candidate)
                if found and image_path(found["hexcode"]):
                    chosen, source = image_path(found["hexcode"]), "annotation"
                    break

        if not chosen:
            for key in senses(gloss):
                hexcode = by_meaning.get(key)
                if hexcode and image_path(hexcode):
                    chosen, source = image_path(hexcode), "zh_transfer"
                    break

        if not chosen:
            found = iconify_lookup(icon_names, word)
            if found:
                chosen, source = found, "iconify"

        sources[source or "none"] += 1
        if chosen:
            assigned[word] = {"file": chosen.relative_to(CACHE).as_posix(),
                              "source": source, "glossZh": gloss,
                              "lesson": entry["lesson"]}
        else:
            blank.append(entry)

    if unresolved:
        raise SystemExit("指名了不存在的圖（名字寫錯就會靜靜配錯）：\n  "
                         + "\n  ".join(unresolved))

    total = len(entries)
    print(f"  {len(assigned)}/{total} 張有圖（{len(assigned) / total:.0%}）")
    for name in order + ("none",):
        print(f"    {name:11s} {sources[name]}")
    if blank and args.uncovered:
        print("\n  尚未配圖：")
        for entry in blank[: args.uncovered]:
            print(f"    第 {entry['lesson']:2d} 課  {entry['en']:24s} {entry['zh']}")

    if args.write:
        OUTPUT.write_text(json.dumps(
            {"license": "OpenMoji 17.0.0 CC BY-SA 4.0；game-icons CC BY 3.0；"
                        "Phosphor MIT；Material Design Icons Apache 2.0；Tabler MIT；"
                        "數字與曆法圖為本專案自繪",
             "total": total, "matched": len(assigned), "sources": sources,
             "images": assigned},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\n  {OUTPUT}")

    if blank and not args.allow_blank:
        raise SystemExit(f"\n還有 {len(blank)} 張沒有圖。這副卡不留白——"
                         "補進 OVERRIDES 或畫一張，不要拿近似的圖充數。")


if __name__ == "__main__":
    main()
