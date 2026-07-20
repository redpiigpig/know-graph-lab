#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily z-lib ingest.

Watches the skill-local "z-lib" drop folder, and for each ebook file:
  1. Parses filename -> (author, title) using parse_drive_inventory.parse_filename
     (handles z-library pattern, "by Author", 全形 comma split, etc.)
  2. Asks Gemini to classify into one of the 10 main categories
     (with a fallback rule for English Christian-studies books -> 宗教學).
  3. Inserts an `ebooks` row with category set + future Drive path as file_path.
  4. Moves the local file from z-lib/ to
     G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館/{category}/{author}，{title}.{ext}
     Since G: is the Drive sync mount, the move IS the upload (sync client
     uploads in background) AND the local-delete in one filesystem rename.

After ingest, the new ebook row has parsed_at = NULL, so the next
parse_worker.py / ocr_with_gemini.py run picks it up automatically.

Usage:
  python scripts/ingest_new_books.py status
  python scripts/ingest_new_books.py run [--limit N] [--dry-run]
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

sys.path.insert(0, str(Path(__file__).parent))
from parse_drive_inventory import parse_filename, to_traditional, TITLE_AUTHOR_OVERRIDES
from file_validation import validate_ebook
import book_classifier


NEW_BOOK_DIR = Path(__file__).resolve().parent.parent / "z-lib"
DRIVE_ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/電子圖書館")
EBOOK_EXTS = {".pdf", ".epub", ".mobi", ".azw3", ".azw"}

# Broken / truncated downloads are held here, OUT of Drive, so they never
# produce empty chunks downstream. Reviewed manually.
CORRUPT_DIR = NEW_BOOK_DIR / "_corrupt"
# Books the classifiers can't place with confidence go to a review queue
# instead of being blind-dumped into a wrong category (the old 哲學 default).
REVIEW_CATEGORY = "_待審分類"
REVIEW_CONFIDENCE = 0.45  # Gemini confidence below this → seek a second opinion
INVALID_FNAME_CHARS = {
    "<": "＜", ">": "＞", ":": "：", '"': "＂", "|": "｜",
    "?": "？", "*": "＊", "\\": "＼", "/": "／",
}

CATEGORIES = [
    "哲學", "神學", "世界宗教", "宗教學", "人類生物學", "心理學",
    "文學", "自然科學", "歷史學", "社會政治學",
]


def load_env():
    env = {}
    with open(Path(__file__).parent.parent / ".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
SB_HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
}


def _find_gemini_keys() -> list[str]:
    """Return all usable Gemini API keys (in order). Supports bare-name slots
    (GEMINI_API_KEY / Gemini_API_Key / GOOGLE_API_KEY), numbered slots
    (Gemini_API_Key_1 .. _10), and comma-separated multi-key strings — the
    same .env layout `ocr_with_gemini.py` uses. Free-tier daily quota is
    per-key, so rotating lets ingest survive a single-key 429 lockout."""
    primary = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    raw_values: list[str] = []
    for name in primary:
        v = os.environ.get(name) or ENV.get(name)
        if v:
            raw_values.append(v); break
    for n in range(1, 11):
        for base in primary:
            v = os.environ.get(f"{base}_{n}") or ENV.get(f"{base}_{n}")
            if v:
                raw_values.append(v); break
    keys: list[str] = []
    seen: set[str] = set()
    for raw in raw_values:
        for piece in raw.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_gemini_keys()
GEMINI_KEY = GEMINI_KEYS[0] if GEMINI_KEYS else None  # back-compat
_gemini_key_idx = 0  # index into GEMINI_KEYS — advances only when current key hits 429


def sanitize_filename(name: str) -> str:
    for bad, good in INVALID_FNAME_CHARS.items():
        name = name.replace(bad, good)
    return name.strip()


_ZLIB_SUFFIX_RE = re.compile(r"\s*\([^()]*(?:z-lib|z-library|1lib)[^()]*\)\s*", re.I)


def _strip_zlib_suffix(name: str) -> str:
    """parse_drive_inventory.parse_filename only recognises '(z-lib.org)' / '(z-library)'.
    The newer mirror writes '(z-library.sk, 1lib.sk, z-lib.sk)' — internal commas
    confuse the comma-split fallback and produce nonsense author/title. Strip any
    paren containing a z-lib host before delegating to the shared parser."""
    stem = Path(name).stem
    ext = Path(name).suffix
    cleaned = _ZLIB_SUFFIX_RE.sub(" ", stem).strip()
    return f"{cleaned}{ext}"


def parse_book_meta(filename: str) -> dict:
    """Filename -> {author, title, ext}. Returns {} if parsing produced no usable title."""
    info = parse_filename(_strip_zlib_suffix(filename))
    title = (info.get("short") or info.get("full") or "").strip()
    author = (info.get("author") or "").strip()
    # Convert simplified -> traditional for Chinese; English passes through unchanged
    if title:
        title = to_traditional(title)
    if author:
        author = to_traditional(author)
    # Manual overrides for known patterns where author can't be parsed
    if not author:
        for pattern, ovr in TITLE_AUTHOR_OVERRIDES:
            if pattern in filename:
                author = ovr
                break
    # Strip leaked extension
    title = re.sub(r"\.(pdf|epub|mobi|azw3|azw)\b", "", title, flags=re.I).strip()
    author = re.sub(r"\.(pdf|epub|mobi|azw3|azw)\b", "", author, flags=re.I).strip()
    # Dedupe author "X [X]"
    author = re.sub(r"^(.+?)\s*\[\1\]$", r"\1", author).strip()
    if not title:
        return {}
    ext = Path(filename).suffix.lower().lstrip(".")
    return {"author": author or None, "title": title, "ext": ext}


def fallback_category(title: str, author: str, filename: str = "") -> str | None:
    """Cheap keyword pre-classifier for common cases — saves Gemini calls.

    Includes the raw filename in the search text because parse_book_meta
    strips subtitle text after「：」 and converts simplified→traditional,
    which can lose critical theology keywords (e.g. 克尔恺郭尔 → 克爾愷郭爾).
    """
    text_raw = f"{title} {author} {filename}"
    text = text_raw.lower()
    christian_kw = [
        "christ", "christian", "christology", "church", "bonhoeffer", "syriac",
        "nestorius", "cyril", "monophysite", "chalcedon", "ephrem", "babai",
        "homilies", "patristic", "apostolic", "gospel", "biblical", "theology",
        # 教父名字（Schaff 等版本書名/作者欄會出現）
        "nicene", "ecumenical", "fathers", "schaff",
        "tertullian", "hippolytus", "cyprian", "origen", "novatian",
        "lactantius", "methodius", "aphrahat",
        "augustine", "jerome", "athanasius", "ambrose", "hilary",
        "basil", "chrysostom", "eusebius", "sulpitius", "theodoret",
        "sozomenus", "nazianzen", "leo the great", "gregory of nyssa",
        "gregory the great", "gregory thaumaturgus", "irenaeus", "justin martyr",
        "clement of alexandria",
    ]
    if any(k in text for k in christian_kw):
        # 教父名 / patristic / Augustine / Chrysostom / Aquinas / Barth 等
        # → 神學（基督教神學作為獨立學科）
        return "神學"

    # 中文神學關鍵字（簡繁通吃）— 涵蓋 ziliaozhan/神学 大批次的常見書名模式
    cn_theology_kw = [
        "神學", "神学",
        "教父", "教父學", "教父学", "教父原典",
        "信理", "信理神學", "信理神学",
        "阿奎那", "多瑪斯", "多玛斯",
        "奧古斯丁", "奥古斯丁",
        "三位一體", "三位一体", "三一論", "三一论", "三一神",
        "基督論", "基督论", "基督學", "基督学",
        "聖事", "圣事",
        "禮儀", "礼仪",
        "教宗", "教皇", "教會教義", "教会教义",
        "解放神學", "解放神学",
        "拉納", "拉纳",  # Rahner
        "莫爾特曼", "莫尔特曼",  # Moltmann
        "朋霍費爾", "朋霍费尔",  # Bonhoeffer
        "巴特", "卡尔巴特", "卡爾巴特",  # Barth
        "孔漢思", "孔汉思", "汉斯昆", "漢斯昆", "孔思昆",  # Hans Küng
        "利瑪竇", "利玛窦", "明清傳教",
        "梵二", "梵蒂岡第二", "梵蒂冈第二",
        "教義", "教义", "信經", "信经",
        "默觀", "默观", "默想", "靈修", "灵修",
        "神義論", "神义论",
        "末世論", "末世论",
        "聖母", "圣母", "瑪利亞", "玛利亚",
        "教父經注", "教父经注",
        "東正教神學", "东正教神学",
        "趙紫宸", "赵紫宸", "丁光訓", "丁光训",  # 漢語神學家
        "克爾凱郭爾", "克尔恺郭尔",  # Kierkegaard (when paired with 信仰/基督教)
        "潘霍華", "潘霍华",
        "信德與望德", "信德与望德",
        "天主教信", "天主教教義", "天主教教义", "天主教神",
        "上帝之城", "天主之城",  # Augustine
        "懺悔錄", "忏悔录",  # Augustine
        "神學大全", "神学大全", "駁異大全", "驳异大全",  # Aquinas
        "教父集成", "歷代基督教名著", "历代基督教名著",
        "金口若望", "屈梭多模",  # Chrysostom
        "安波羅修", "安波罗修", "安布罗斯",  # Ambrose
        "亞他那修", "亚他那修",  # Athanasius
        "德爾圖良", "德尔图良",  # Tertullian
        "游斯丁", "查士丁",  # Justin Martyr
        "俄利根",  # Origen
        "馬克西穆斯", "马克西穆斯",  # Maximus the Confessor
        "納西盎", "纳西盎",  # Nazianzen
        "格列高利", "大圣国瑞", "大聖國瑞",  # Gregory
        "波納文圖拉", "波纳文图拉",  # Bonaventure
        "牧靈", "牧灵",
        "宗徒",
        "罪與救贖", "罪与救赎",
        "苦難神學", "苦难神学",
        "親吻神學", "亲吻神学",
        "華夏與基督", "华夏与基督",
        "智慧叢書", "智慧丛书",
        "普及神學", "普及神学",
        "基督之律", "基督宗教倫理", "基督宗教伦理",
        "信仰", "啟示", "启示",
    ]
    if any(k in text_raw for k in cn_theology_kw):
        return "神學"

    # 中文「世界宗教」邊界（佛教史／伊斯蘭史／猶太教史等 — 不跨宗教，屬該宗教自身的研究）
    cn_world_religion_kw = [
        "佛教史", "佛經", "佛经", "中國佛教", "中国佛教", "藏傳", "藏传",
        "伊斯蘭教史", "伊斯兰教史", "可蘭經", "可兰经", "古蘭經", "古兰经",
        "猶太人", "犹太人", "猶太教", "犹太教", "希伯來", "希伯来",
        "印度教", "吠陀",
        "瑣羅亞斯德", "琐罗亚斯德", "祆教",
        "道教史", "道藏",
        "巴哈伊",
    ]
    if any(k in text_raw for k in cn_world_religion_kw):
        return "世界宗教"

    if "zoroastr" in text or "avesta" in text or "islam" in text or "buddhis" in text:
        return "世界宗教"

    # 中文「宗教學／哲學」優先 override（避免被下面 catch-all 誤抓進神學）
    cn_religious_studies_kw = [
        "宗教學導論", "宗教学导论", "後現代宗教", "后现代宗教",
        "跨宗教", "宗教對話", "宗教对话", "宗教比較", "宗教比较",
        "宗教社會學", "宗教社会学", "宗教現象學", "宗教现象学",
    ]
    if any(k in text_raw for k in cn_religious_studies_kw):
        return "宗教學"

    cn_philosophy_kw = [
        "士林哲學", "士林哲学",
        "現代西方倫理學", "现代西方伦理学",
    ]
    if any(k in text_raw for k in cn_philosophy_kw):
        return "哲學"

    # 神學 catch-all — 基督教/天主/聖/圣 + 教父/神學家／聖人翻譯名／聖事禮儀靈修術語
    # （順序很重要：宗教學／哲學 override 必須在這之前）
    cn_theology_catchall = [
        "基督",  # 廣譜 catch-all：基督教／基督徒／基督之友／基督之言／基督與人類痛苦／基督新教 — 對 ziliaozhan 批次全是神學
        "天主",  # 天主實義（利瑪竇）／天主論／天主降生／天主之城
        "圣域", "聖域",
        "圣事", "聖事",
        "圣秩", "聖秩",
        "圣女", "聖女",  # 大德蘭等聖人傳
        "圣方济各", "聖方濟各", "五伤方济各", "五傷方濟各",
        "圣十字若望", "聖十字若望", "十字若望",  # St John of the Cross
        "圣依纳爵", "聖依納爵", "神操",  # Ignatius《神操》
        "嘉默罗", "嘉默羅",  # Carmel
        "大德兰", "大德蘭",  # Teresa of Avila
        "德兰修女", "德蘭修女",  # Mother Teresa
        "师主篇", "師主篇",  # Imitation of Christ
        "登上嘉默罗", "登上嘉默羅",  # Ascent of Mount Carmel
        "灵歌", "靈歌",  # Spiritual Canticle
        "默想", "默观", "默觀",
        "圣周", "聖周",
        "圣经", "聖經", "聖言", "圣言",
        "圣徒", "聖徒",
        "卡斯培",  # Kasper
        "麦格拉思", "麥格拉思",  # McGrath
        "帕利坎",  # Pelikan
        "亨利樞機", "亨利枢机",
        "上帝观", "上帝觀", "上帝之城",
        "异端", "異端",
        "救赎", "救贖",
        "修女传", "修女傳", "圣人传", "聖人傳",
        "纳匝肋", "納匝肋",  # Nazareth (Benedict XVI)
        "现代基督教", "現代基督教",
        "驳赛尔修斯", "駁賽爾修斯",  # Origen Contra Celsum
        "勸勉希臘人", "劝勉希腊人",  # Clement of Alexandria
        "论责任", "論責任",  # Ambrose
        "论信望爱", "論信望愛",  # Augustine
        "论怀疑者", "論懷疑者",
        "论隐秘的上帝", "論隱秘的上帝",
        "道德论集", "道德論集",
        "隐修", "隱修",
        "汉斯昆", "漢斯昆",
        "卡尔·拉内",  # Rahner alt translit
        "海德格尔现象学及其神学", "海德格爾現象學及其神學",  # already would match 神學, but spell out
        "汉语景教", "漢語景教",  # 景教 (Christianity in China)
        "景教",
        "基督抹杀", "基督抹殺",  # 評/評基督抹殺論 — 反神論書，仍歸神學
        "神圣", "神聖",  # 神圣的根/神聖
        "神秘", "神祕",
        "神存在", "神不存在",
        "异教徒", "異教徒",
        "杜伊诺哀歌",  # Rilke 哀歌 + 基督教思想
        "墙上的书写", "牆上的書寫",  # 墙上的书写：尼采与基督教
        "门槛", "門檻",  # 跨越希望的门槛 (John Paul II)
        "希望的门槛", "希望的門檻",
        "诠释学-宗教",  # hermeneutics + religion + hope (Tracy)
        "安瑟伦", "安瑟莫", "安瑟倫",  # St Anselm (多個音譯)
        "有神论", "有神論",
        "天人之际", "天人之際",  # 何光沪 漢語神學
        "moltmann", "Moltmann",  # 「被钉十字架的上帝.Moltmann.pdf」 — author英文留檔
        "kierkegaard",
        "rahner",
        "kasper",
        "küng", "kung",
        "罪人的福音",  # 「現實的人類和理想的人類 一個貧苦罪人的福音」
        "贫苦罪人",
        "道与言", "道與言",
        "上帝",  # 上帝之城／神存在嗎／神聖的根 — 凡題目有上帝/神（在我們批次都是神學
        "神性",  # 莫扎特音乐的神性与超验
    ]
    if any(k in text_raw for k in cn_theology_catchall):
        return "神學"

    # 廣譜 last-resort 關鍵字 — 涵蓋非宗教學科，讓 Gemini 額度耗盡時仍能正確上架。
    # 順序＝優先序（神學/宗教已在上面先判，這裡只處理其餘人文社科）。
    broad = [
        ("歷史學", ["帝國史", "通史", "國史", "世界史", "近代史", "古代史", "中世紀史", "斷代",
                    "遠征記", "編年", "戰爭史", "戰史", "王朝", "雅典", "羅馬史", "十字軍",
                    "伯里克利", "亞歷山大", "亚历山大", "拿破崙", "革命史", "波斯帝國", "波斯帝国"]),
        ("人類生物學", ["考古", "人類學", "人类学", "原始思維", "原始思维", "原始社會", "圖騰", "图腾",
                        "巫術", "民族誌", "民族志", "演化", "進化論", "进化论", "體質人類", "尼安德"]),
        ("心理學", ["心理學", "心理学", "精神分析", "佛洛伊德", "弗洛伊德", "榮格", "荣格",
                    "皮亞傑", "皮亚杰", "認知科學", "认知科学", "潛意識", "潜意识"]),
        ("哲學", ["哲學", "哲学", "形上學", "形而上", "倫理學", "伦理学", "知識論", "知识论",
                  "認識論", "认识论", "本體論", "本体论", "現象學", "现象学", "邏輯", "逻辑",
                  "辯證", "辩证", "斯賓諾莎", "斯宾诺莎", "叔本華", "叔本华", "康德", "黑格爾",
                  "黑格尔", "尼采", "海德格", "胡塞爾", "胡塞尔", "維根斯坦", "维特根斯坦",
                  "柏拉圖", "柏拉图", "亞里士多德", "亚里士多德", "結構主義", "结构主义",
                  "意志和表象", "論靈魂", "论灵魂", "伊本·西那", "伊本西那", "存在主義", "存在主义"]),
        ("文學", ["小說", "小说", "詩集", "诗集", "文學史", "文学史", "戲劇", "戏剧", "史詩", "史诗", "悲劇"]),
        ("社會政治學", ["政治學", "政治学", "社會學", "社会学", "資本論", "资本论", "意識形態",
                        "意识形态", "主權", "主权", "政治秩序", "民主理論", "國家理論"]),
        ("自然科學", ["物理學", "物理学", "化學", "化学", "生物學", "生物学", "天文", "數學",
                      "数学", "量子", "相對論", "相对论"]),
    ]
    for cat, kws in broad:
        if any(k in text_raw for k in kws):
            return cat

    return None


CATEGORIZE_PROMPT = """你是書籍分類助手。請將下列書籍歸入恰好一個分類：

十大分類（擇一）：
- 哲學 — 哲學家、哲學流派、形上學、倫理學、邏輯學
- 神學 — 系統神學、教父著作（Augustine/Aquinas/Schaff 教父集等）、信理神學、神學概論、神學家著作與研究（Barth/Rahner/Moltmann/Küng/Bonhoeffer 等）、教父學、護教學
- 世界宗教 — 特定宗教的經典、教義、史實本身（基督教 Bible 翻譯／祈禱書、伊斯蘭可蘭經、佛經、印度教、瑣羅亞斯德教阿維斯塔、巴哈伊經典…）
- 宗教學 — 跨宗教學術研究：神話學、宗教史、宗教社會學、宗教比較、宗教對話、宗教現象學
- 人類生物學 — 人類學、生物人類學、演化、考古、體質
- 心理學 — 心理學、精神分析、認知科學
- 文學 — 小說、詩歌、散文、文學評論
- 自然科學 — 物理、化學、生物、地球科學、數學
- 歷史學 — 通史、斷代史、地區史、人物傳記（非宗教人物）
- 社會政治學 — 政治、經濟、社會學、法律、國際關係

辨別技巧（神學 vs 世界宗教 vs 宗教學 邊界）：
- 教父原典、系統神學、Augustine 懺悔錄 / Aquinas 神學大全 / Schaff NPNF / 基督論 / 三一論 → 神學
- 教會史人物傳、護教學、神學家研究、教父學概論 → 神學
- 各宗教自己的「經典／教義原本」（聖經中譯本、佛經、可蘭經、阿維斯塔、巴哈伊經典）→ 世界宗教
- 神話學、跨宗教比較研究、宗教社會學、宗教對話 → 宗教學
- 不確定基督教書要 神學 還是 世界宗教 時，「學術／系統／神學家著作」→ 神學；「Bible 譯本／祈禱書／信經中譯」→ 世界宗教

書名: {title}
作者: {author}

只回傳一行 JSON，無其他文字：
{{"category":"<從上面十個擇一>","subcategory":"<細分名稱或 null>","confidence":0.0-1.0}}
"""


def gemini_classify(title: str, author: str) -> dict:
    """Returns {category, subcategory, confidence}. Raises on hard error.

    Rotates through GEMINI_KEYS on 429 — free-tier RPD is per-key, so if
    key #1 is exhausted from earlier OCR runs, switching to #2/#3/#4 buys
    a fresh quota window without waiting for daily reset.
    """
    global _gemini_key_idx
    if not GEMINI_KEYS:
        raise RuntimeError("Gemini API key not found in env")
    prompt = CATEGORIZE_PROMPT.format(title=title, author=author or "(unknown)")
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }
    base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    # Per-key budget: 4 attempts with short backoff (transient spike). On
    # persistent 429 advance to next key and reset attempts.
    last_err: str | None = None
    while _gemini_key_idx < len(GEMINI_KEYS):
        key = GEMINI_KEYS[_gemini_key_idx]
        url = f"{base_url}?key={key}"
        rotated = False
        for attempt, wait in enumerate((0, 5, 15, 30), start=1):
            if wait:
                time.sleep(wait)
            r = requests.post(url, json=body, timeout=30)
            if r.status_code == 200:
                break
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code in (429, 503) and attempt < 4:
                print(f"    Gemini {r.status_code} on key #{_gemini_key_idx} — "
                      f"retry {attempt} after {wait + (5 if attempt == 1 else 15)}s",
                      file=sys.stderr)
                continue
            if r.status_code == 429:
                # Persistent 429 on this key — try the next one.
                if _gemini_key_idx + 1 < len(GEMINI_KEYS):
                    _gemini_key_idx += 1
                    print(f"    ⟳ Gemini 429 on key #{_gemini_key_idx - 1}; "
                          f"switching to key #{_gemini_key_idx} of {len(GEMINI_KEYS)}",
                          file=sys.stderr)
                    rotated = True
                    break  # re-enter outer while with new key
                raise RuntimeError(f"Gemini {last_err} (all {len(GEMINI_KEYS)} keys exhausted)")
            raise RuntimeError(f"Gemini {last_err}")
        if rotated:
            continue
        break
    data = r.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Be lenient with markdown fences
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.M).strip()
    parsed = json.loads(text)
    cat = parsed.get("category", "").strip()
    if cat not in CATEGORIES:
        # Map some common LLM mistakes
        if cat in {"聖經研究", "教父學", "系統神學", "信理神學", "基督論", "三一論"}:
            cat = "神學"
        elif cat in {"基督教", "伊斯蘭教", "佛教", "印度教", "瑣羅亞斯德教", "猶太教", "巴哈伊"}:
            cat = "世界宗教"
        elif cat in {"教會史", "宗教史", "神話學", "宗教比較", "宗教社會學", "宗教對話"}:
            cat = "宗教學"
        else:
            raise ValueError(f"Gemini returned non-category: {cat!r}")
    return {
        "category": cat,
        "subcategory": (parsed.get("subcategory") or None),
        "confidence": float(parsed.get("confidence", 0.5)),
    }


def _local_or_review(title: str, author: str, filename: str, conf_floor: float = 0.0) -> dict:
    """Deterministic local scorer, else the review queue.

    Used when Gemini is unavailable or unsure. The local book_classifier is
    explainable and offline; if it's confident we trust its category, otherwise
    we hold the book for human review rather than guess.
    """
    r = book_classifier.classify(title, author, filename)
    if r.category and not r.uncertain:
        return {"category": r.category, "subcategory": None,
                "confidence": max(conf_floor, r.confidence),
                "source": f"book_classifier ({r.reason})"}
    return {"category": REVIEW_CATEGORY, "subcategory": None,
            "confidence": r.confidence, "source": "review-queue"}


def classify(title: str, author: str, filename: str = "") -> dict:
    fb = fallback_category(title, author, filename)
    if fb:
        return {"category": fb, "subcategory": None, "confidence": 0.9, "source": "fallback"}
    try:
        g = gemini_classify(title, author)
        g["source"] = "gemini"
        # A low-confidence Gemini guess is exactly what mis-shelves books.
        # Get a deterministic second opinion before committing it.
        if g.get("confidence", 0) < REVIEW_CONFIDENCE:
            print(f"  ⚠ Gemini 信心低 ({g.get('confidence')}), 取本地評分器二判", file=sys.stderr)
            return _local_or_review(title, author, filename, conf_floor=g.get("confidence", 0))
        return g
    except Exception as e:
        # Gemini down (e.g. all keys 429) — NEVER skip the book over a quota
        # outage, but don't blind-dump into 哲學 either: score it locally and
        # only quarantine if genuinely ambiguous.
        print(f"  ⚠ Gemini 分類失敗，改用本地評分分類器: {str(e)[:60]}", file=sys.stderr)
        return _local_or_review(title, author, filename)


def build_target_path(meta: dict, category: str) -> Path:
    """Build the destination path under DRIVE_ROOT/{category}/."""
    title = meta["title"].strip()
    author = (meta.get("author") or "").strip()
    ext = meta["ext"]
    if author:
        new_name = f"{author}，{title}.{ext}"
    else:
        new_name = f"{title}.{ext}"
    new_name = sanitize_filename(new_name)
    if len(new_name) > 200:
        # Truncate title; keep author
        keep = 200 - len(author) - len(ext) - 4
        title = title[:max(20, keep)]
        new_name = sanitize_filename(f"{author}，{title}.{ext}" if author else f"{title}.{ext}")
    return DRIVE_ROOT / category / new_name


def supabase_insert(meta: dict, category: str, subcategory: str | None, target_path: Path) -> str | None:
    """Insert ebooks row, return id, or None on failure (already-exists by file_path is fine)."""
    payload = [{
        "title": meta["title"],
        "author": meta.get("author"),
        "file_type": meta["ext"],
        "category": category,
        "subcategory": subcategory,
        "file_path": str(target_path).replace("/", "\\"),
    }]
    r = requests.post(
        f"{URL}/rest/v1/ebooks",
        headers={**SB_HEADERS, "Prefer": "return=representation,resolution=ignore-duplicates"},
        json=payload,
        timeout=20,
    )
    if r.status_code in (200, 201):
        rows = r.json()
        if rows:
            return rows[0]["id"]
    print(f"    [DB] insert failed HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
    return None


def cmd_status():
    if not NEW_BOOK_DIR.exists():
        print(f"z-lib dir not found: {NEW_BOOK_DIR}")
        return
    files = [p for p in NEW_BOOK_DIR.iterdir() if p.is_file() and p.suffix.lower() in EBOOK_EXTS]
    junk = [p for p in NEW_BOOK_DIR.iterdir() if p.is_file() and p.suffix.lower() not in EBOOK_EXTS]
    print(f"Drop folder: {NEW_BOOK_DIR}")
    print(f"  ebooks waiting: {len(files)}")
    for p in files[:10]:
        print(f"    - {p.name}  ({p.stat().st_size//1024} KB)")
    if len(files) > 10:
        print(f"    ... +{len(files)-10} more")
    if junk:
        print(f"  non-ebook files (will be ignored): {len(junk)}")
        for p in junk:
            print(f"    - {p.name}")


def cmd_run(limit: int | None, dry_run: bool):
    if not NEW_BOOK_DIR.exists():
        print(f"z-lib dir missing: {NEW_BOOK_DIR}", file=sys.stderr)
        return 0
    files = sorted(p for p in NEW_BOOK_DIR.iterdir() if p.is_file() and p.suffix.lower() in EBOOK_EXTS)
    if limit:
        files = files[:limit]
    if not files:
        print("No new books to ingest.")
        return 0

    ok = 0
    fail = 0
    corrupt = 0
    for p in files:
        print(f"\n[{p.name}]")

        # Pre-ingest integrity gate: a broken/truncated/zero download must not
        # enter the pipeline (it would silently produce empty chunks).
        v = validate_ebook(p)
        if not v.ok:
            detail = f" ({v.detail})" if v.detail else ""
            print(f"  CORRUPT [{v.reason}]{detail} — 隔離到 _corrupt/，不入庫")
            if not dry_run:
                CORRUPT_DIR.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.move(str(p), str(CORRUPT_DIR / p.name))
                except Exception as e:
                    print(f"    (隔離搬移失敗，檔案留原處: {e})")
            corrupt += 1
            continue

        meta = parse_book_meta(p.name)
        if not meta:
            print("  SKIP: could not parse title from filename")
            fail += 1
            continue
        print(f"  parsed: title={meta['title']!r}  author={meta.get('author')!r}  ext={meta['ext']}")

        try:
            cls = classify(meta["title"], meta.get("author") or "", p.name)
        except Exception as e:
            print(f"  CLASSIFY FAILED: {e}")
            fail += 1
            continue
        print(f"  category: {cls['category']}  subcat: {cls.get('subcategory')}  ({cls['source']}, conf={cls['confidence']:.2f})")

        target = build_target_path(meta, cls["category"])
        print(f"  target: {target}")

        if dry_run:
            ok += 1
            continue

        # Pre-flight: ensure target dir exists & target file doesn't already exist
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            # Duplicate already on Drive — delete the z-lib/ copy so daily runs
            # don't keep scanning the same dupes. Log sizes for verification.
            try:
                z_size = p.stat().st_size
                t_size = target.stat().st_size
                print(f"  SKIP: target already exists on Drive "
                      f"(z-lib={z_size // 1024} KB, drive={t_size // 1024} KB) — deleting z-lib copy")
                p.unlink()
            except Exception as e:
                print(f"  SKIP: target already exists on Drive (delete failed: {e})")
            fail += 1
            continue

        ebook_id = supabase_insert(meta, cls["category"], cls.get("subcategory"), target)
        if not ebook_id:
            print("  ABORT: DB insert failed (file kept in z-lib/)")
            fail += 1
            continue
        print(f"  db: inserted ebook_id={ebook_id}")

        try:
            shutil.move(str(p), str(target))
        except Exception as e:
            print(f"  MOVE FAILED: {e} — DB row was inserted, file still in z-lib/")
            print(f"  manual fix: move file to {target} (Drive will sync), or delete row {ebook_id}")
            fail += 1
            continue
        print(f"  moved -> Drive ({cls['category']})")
        ok += 1
        time.sleep(0.5)  # gentle pacing for Gemini RPM

    print(f"\nDone: {ok} ingested, {fail} failed/skipped, {corrupt} corrupt-quarantined "
          f"(of {len(files)} processed)")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["status", "run"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "status":
        cmd_status()
    else:
        cmd_run(args.limit, args.dry_run)


if __name__ == "__main__":
    main()
