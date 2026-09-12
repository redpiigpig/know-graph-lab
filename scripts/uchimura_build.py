"""Build Uchimura Kanzō (內村鑑三) Aozora Bunko works into reader books.

Uchimura (1861–1930) is public domain worldwide. First wave = the 11 texts
published on Aozora Bunko (person34) — clean digital XHTML, zero OCR. Each core
work = one ebooks row (ja ＋ 繁中 two-column, `sources={"ja":…}`,
`source_order=["ja"]`); the six short essays are bundled into ONE 雜文短篇集 row
(one piece = one section). This is the portal's first Japanese → 繁中 case.
See .claude/skills/ebook-collected-works/uchimura_collected_works.md.

Aozora XHTML quirks handled here (pure functions, locked by
scripts/tests/test_uchimura_build.py):
  - Shift_JIS (cp932) encoding, with utf-8 fallback
  - <ruby> reading annotations stripped (keep rb base text)
  - <span class="notes">［＃…］</span> editor notes dropped
  - gaiji <img alt="…U+XXXX"> → real Unicode char; alt="※(…)" → "※"
  - <h1-6 class="*midashi*"> headings → section boundaries
  - one <br/>-terminated line = one paragraph; leading U+3000 indent stripped
  - <div class="bibliographical_information"> (底本) excluded (outside main_text)

Old-orthography (旧字旧仮名) pieces are fed to the engine as-is per the
case-study md. Cache dir: c:/tmp/uchimura_cache/ (fetched 2026-07-16, throttled).

  python scripts/uchimura_build.py --dry             # parse all, counts only
  python scripts/uchimura_build.py --dry --work denmark-story
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):  # Windows console is cp950
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load .env before importing the engine module (it reads keys at import).
_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

CACHE_DIR = Path("c:/tmp/uchimura_cache")

# ── Registry: 6 ebook rows covering the 11 Aozora texts ──────────────────────
# deterministic namespace d0000000-… (a=印順 b=聖嚴 c=星雲 → d=內村鑑三).
# Mirrored in .claude/skills/ebook-collected-works/uchimura_registry.json.
REGISTRY: dict[str, dict] = {
    "denmark-story": {
        "ebook_id": "d0000000-0000-4000-8000-000000000003",
        "title": "丹麥國的故事",
        "original_title": "デンマルク国の話",
        "subtitle": "以信仰與樹木救國之話（日文原文＋繁中對照）",
        "year": 1911,
        "parent_volume": "講演與信仰文集",
        "files": ["233_43563.html"],
    },
    "how-to-read-bible": {
        "ebook_id": "d0000000-0000-4000-8000-000000000004",
        "title": "聖經的讀法",
        "original_title": "聖書の読方",
        "subtitle": "以來世為背景讀之（日文原文＋繁中對照）",
        "year": 1921,
        "parent_volume": "聖書研究",
        "files": ["1218_18404.html"],
    },
    "short-pieces": {
        "ebook_id": "d0000000-0000-4000-8000-000000000006",
        "title": "雜文短篇集",
        "original_title": "寡婦の除夜‧寒中の木の芽 ほか短篇六篇",
        "subtitle": "青空文庫所收短篇六篇（日文原文＋繁中對照）",
        "year": 1912,
        "parent_volume": "講演與信仰文集",
        # chronological-ish order; each file = one piece = one section
        "files": ["1216_19588.html", "1215_9222.html", "1212_19587.html",
                  "1214_19590.html", "1217_19583.html", "1213_19585.html"],
    },
    "greatest-legacy": {
        "ebook_id": "d0000000-0000-4000-8000-000000000002",
        "title": "留給後世的最大遺產",
        "original_title": "後世への最大遺物",
        "subtitle": "1894年箱根夏期學校講演（日文原文＋繁中對照）",
        "year": 1897,
        "parent_volume": "講演與信仰文集",
        "files": ["519_43561.html"],
    },
    "consolations": {
        "ebook_id": "d0000000-0000-4000-8000-000000000001",
        "title": "基督信徒的慰藉",
        "original_title": "基督信徒のなぐさめ",
        "subtitle": "處女作‧「無教會」一詞初出（日文原文＋繁中對照）",
        "year": 1893,
        "parent_volume": "信仰三部作",
        "files": ["55507_72651.html"],
    },
    "job-lectures": {
        "ebook_id": "d0000000-0000-4000-8000-000000000005",
        "title": "約伯記講演",
        "original_title": "ヨブ記講演",
        "subtitle": "1920年柏木聖書研究會講演（日文原文＋繁中對照）",
        "year": 1925,
        "parent_volume": "聖書研究",
        "files": ["56908_64142.html"],
    },
}

# Translate order: short works first (early wins), the huge Job lectures last.
QUEUE = ["denmark-story", "how-to-read-bible", "short-pieces",
         "greatest-legacy", "consolations", "job-lectures"]


# ── decoding ─────────────────────────────────────────────────────────────────
def decode_aozora(raw: bytes) -> str:
    """Aozora XHTML is Shift_JIS; newer files may be UTF-8. Try utf-8 strictly
    first (cp932 will happily mis-decode utf-8 bytes, not vice versa)."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp932", errors="replace")


# ── parsing ──────────────────────────────────────────────────────────────────
_GAIJI_U_RE = re.compile(r"U\+([0-9A-Fa-f]{4,6})")
_MIDASHI_MARK = "␟"  # ␟ unit separator — internal heading marker


def _gaiji_char(alt: str) -> str:
    """gaiji <img alt> → text: 'U+8AB6' form → that char; '※(…)' form → '※'."""
    m = _GAIJI_U_RE.search(alt or "")
    if m:
        return chr(int(m.group(1), 16))
    return "※" if (alt or "").startswith("※") else ""


def parse_aozora(html: str) -> dict:
    """Aozora XHTML → {title, subtitle, sections:[{heading, paras}]}.

    One <br/>-terminated line = one paragraph. Headings (class *midashi*) open a
    new section; text before the first heading is the '(front)' section."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.find(class_="title")
    sub_el = soup.find(class_="subtitle")
    title = title_el.get_text(strip=True) if title_el else ""
    subtitle = sub_el.get_text(strip=True) if sub_el else None

    main = soup.find("div", class_="main_text")
    if main is None:
        raise ValueError("no <div class='main_text'> — not an Aozora XHTML?")

    for el in main.find_all(["rt", "rp"]):
        el.decompose()
    for el in main.find_all("span", class_="notes"):
        el.decompose()
    for el in main.find_all("img"):
        el.replace_with(_gaiji_char(el.get("alt", "")))
    for el in main.find_all("br"):
        el.replace_with("\n")
    for el in main.find_all(re.compile(r"^h[1-6]$")):
        cls = " ".join(el.get("class") or [])
        if "midashi" in cls:
            el.replace_with(f"\n{_MIDASHI_MARK}{el.get_text(strip=True)}\n")

    sections: list[dict] = []
    cur: dict | None = None
    for line in main.get_text().split("\n"):
        s = line.strip().strip("　").strip()
        if not s:
            continue
        if s.startswith(_MIDASHI_MARK):
            cur = {"heading": s[1:].strip(), "paras": []}
            sections.append(cur)
            continue
        if cur is None:
            cur = {"heading": "(front)", "paras": []}
            sections.append(cur)
        cur["paras"].append(s)
    return {"title": title, "subtitle": subtitle, "sections": sections,
            "source_note": parse_source_note(soup)}


# ── 底本（版本資訊） ─────────────────────────────────────────────────────────
# 青空文庫是電子底本，**沒有頁碼**，`page_number` 只能留 null
# （[[feedback_transcribe_page_numbers]]）。但每篇末尾的
# <div class="bibliographical_information"> 記著它據以輸入的紙本版次與親本出處——
# 引用者至少標得出「據哪一個版本」。原本這一塊是被整個丟掉的
# （見本檔頂端的 "(底本) excluded"）。
#
# 🚨 只收「底本」與「底本の親本」兩項。入力／校正／公開日期是志工的作業紀錄，
#    不是版本資訊，收進來只會讓引註欄位長出雜訊。
_SOURCE_KEYS = ("底本：", "底本の親本：", "初出：")
# 這些一出現就停止收錄：志工作業紀錄，以及 ※ 開頭的校勘註記（ルビ補訂、誤植說明）
# ——後者是「這個電子檔怎麼做的」，不是「這篇文章出自哪個版本」。
_CREDIT_PREFIXES = ("入力", "校正", "青空文庫", "※", "この", "その他")


def parse_source_note(soup) -> str:
    """青空文庫 XHTML → 底本資訊（多行字串）。沒有這一塊就回空字串。

    例：
      底本：「内村鑑三全集3　1894-1896」岩波書店
      1982（昭和57）年12月20日発行
      底本の親本：「基督教新聞　578号」署名（内村生）
      1894（明治27）年8月24日発行
    """
    div = soup.find("div", class_="bibliographical_information")
    if div is None:
        return ""
    text = div.get_text(chr(10), strip=True)
    lines = [ln.strip() for ln in text.split(chr(10)) if ln.strip()]
    out: list[str] = []
    keep = False
    for ln in lines:
        if any(ln.startswith(k) for k in _SOURCE_KEYS):
            keep = True
        elif keep and (ln.startswith(_CREDIT_PREFIXES) or "公開" in ln or "修正" in ln):
            keep = False
        if keep:
            out.append(ln)
    return chr(10).join(out)


def split_long_paras(paras: list[str], max_chars: int = 1500) -> list[str]:
    """Split any paragraph longer than max_chars on Japanese sentence boundaries
    (。！？」) so each translate prompt stays bounded and zh rows stay 1:1."""
    out: list[str] = []
    for p in paras:
        if len(p) <= max_chars:
            out.append(p)
            continue
        parts = re.split(r"(?<=[。！？」])", p)
        buf = ""
        for part in parts:
            if buf and len(buf) + len(part) > max_chars:
                out.append(buf)
                buf = part
            else:
                buf += part
        if buf:
            out.append(buf)
    return out


def piece_as_section(doc: dict) -> dict:
    """Collapse one short piece (parsed doc) into ONE section headed by the piece
    title; internal headings are inlined as `## ` body lines."""
    paras: list[str] = []
    for s in doc["sections"]:
        if s["heading"] != "(front)":
            paras.append(f"## {s['heading']}")
        paras.extend(s["paras"])
    return {"heading": doc["title"], "paras": paras}


def work_source_note(slug: str, cache_dir: Path = CACHE_DIR) -> str:
    """一部作品的底本資訊。多檔作品（short-pieces）逐篇列出，每篇冠上篇名。

    青空文庫沒有頁碼，這是引用者唯一能標的版本依據
    （[[feedback_transcribe_page_numbers]]）。"""
    w = REGISTRY[slug]
    parts: list[str] = []
    for fname in w["files"]:
        doc = parse_aozora(decode_aozora((cache_dir / fname).read_bytes()))
        note = doc.get("source_note") or ""
        if not note:
            continue
        if len(w["files"]) > 1:
            parts.append(f"〈{doc['title']}〉")
        parts.append(note)
        parts.append("")
    return chr(10).join(parts).strip()


def load_work_sections(slug: str, cache_dir: Path = CACHE_DIR) -> list[dict]:
    """Registry slug → [{heading, paras}] ready for translation. Multi-file works
    (short-pieces) yield one section per piece; single-file works keep their own
    heading structure. Long paragraphs are split; headings keep the raw Aozora
    text (translated later as section titles)."""
    w = REGISTRY[slug]
    secs: list[dict] = []
    for fname in w["files"]:
        doc = parse_aozora(decode_aozora((cache_dir / fname).read_bytes()))
        if len(w["files"]) > 1:
            secs.append(piece_as_section(doc))
        else:
            secs.extend(doc["sections"])
    return [{"heading": s["heading"], "paras": split_long_paras(s["paras"])}
            for s in secs]


# ── translation engine (prod only) ───────────────────────────────────────────
UCHIMURA_PROMPT_TMPL = """你是明治—大正時代日本基督教文獻的專業譯者，正在翻譯內村鑑三（Uchimura Kanzō）的著作。把下列**日文原文**（文語與口語混合體，可能含舊字舊假名）翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
1b. **西元年份一律用阿拉伯數字**：一八九三年→**1893 年**、一九二〇年代→**1920 年代**。🚨 年號紀年照漢數字不可改（明治二十四年、大正十二年），數量與序數也不改（三十年、第三章、二十世紀）。
2. 只翻譯日文原文；不要加任何前言、說明或註解。
3. 語域：**現代白話文**（2026-09-10 使用者定調）。用「的、了、是、在、把、因為、所以」這類白話寫，保留講演體的呼告與反問語氣。
   **絕不可譯成文言**：不要用句末的「也／矣／乎／哉／焉／耳」，不要拿「之」當「的」用，不要寫成「為一婦人之心思所奪，而以餘生送於無益之悲哀中，其情可謂情矣」這種腔調——那句話該寫成「他為了一個女人失了魂，把後半生耗在無益的悲哀裡，說是深情也算深情，卻不是真正的勇氣」。
   3b. **這幾個詞是實際踩過的雷，逐一改掉**（2026-09-11 稽核《基督信徒的慰藉》抓出來的）：
   第二人稱**絕不可用「爾」「汝」**——對神說話用「祢」，對人說話用「你」（「爾卻奪去了我所愛的」→「祢卻奪走了我所愛的人」）；
   「何以……？」→「為什麼……？」（「他何以不幸而短命呢？」→「他為什麼這樣不幸、這樣短命呢？」）；
   「未嘗……」→「從來沒有……」（「未嘗有一日無心痛之日」→「沒有一天不心痛」）；
   「我欲知曉」→「我想知道」；「難以堪當」→「承受不住」；「……之際」→「……的時候」；
   「自……以至……為止」→「從……一直到……」。
   **原文是文語体（明治文語、舊字舊假名）也一樣譯成白話**：原文的古雅是日文那一邊的事，中譯要讓今天的讀者讀得懂。
   **唯一例外是詩詞韻文**——讚美詩、和歌、漢詩、引用的詩行照韻文體譯，那裡可以用文言。聖經引句用和合本語體。
4. 保留 Markdown（## 標題等）。聖經人名、地名、書卷名依和合本慣例（ヨブ→約伯、パウロ→保羅、ロマ書→羅馬書、エレミヤ→耶利米）。
5. **專名與固定術語——一對一，不可改**：無教会（主義）→無教會（主義）、贖罪→贖罪、（基督の）再臨→再臨、復活→復活、十字架→十字架、聖書→聖經（唯誌名《聖書之研究》保留原名）、神→神、イエス‧キリスト→耶穌‧基督、聖霊→聖靈、福音→福音、預言者→先知、使徒→使徒、信者→信徒、教会→教會、宣教師→宣教士（不可照抄日文的「宣教師」，也不用「傳教士」）、恩恵→恩典、艱難→患難、来世→來世、永生→永生、デンマルク→丹麥、ネルソン→納爾遜。
5b. **書名／專名的通則：原題本來就有的漢字照原漢字，只有假名（平假名／片假名）的部分才另外翻**。例：『基督信徒のなぐさめ』的「基督信徒」是漢字照留，「なぐさめ」是假名譯作「慰藉」→《基督信徒的慰藉》；『後世への最大遺物』全是漢字與助詞→《留給後世的最大遺產》；『帝国主義下の台湾』→《帝國主義下之台灣》（原題沒有「日本」，不可自行補上）；『地人論』→《地人論》（**不可意譯成「地球與人類」**）；『求安録』→《求安錄》（不可作「尋求和平」）；『流竄録』→〈流竄錄〉；『伝道之精神』→《傳道之精神》。
6. **概念層——給你候選，按語境擇一，不要一詞一譯到底**。挑哪一個由「這一句在講什麼」決定；同一段裡語意不同就可以用不同譯法：
   ‧ 教会→教會（信仰共同體或機構）／教堂（指建築物）
   ‧ 恩恵→恩典／恩寵；艱難→患難／苦難（依文氣）
   ‧ 信仰→信仰／信心（講個人與神的關係時）
   ‧ 罪→罪／罪愆（文言語氣需要時）
   ‧ 先生→先生（保留日式稱謂）／老師；弟子→弟子／門人
   ‧ 世界→世界／世間（文言脈絡）
7. **日本事物的專有譯法——用錯就是史實錯誤，優先於其他規則**：
   ‧ 日本君主一律「**天皇**」，**絕不可作「皇帝」**（Emperor Meiji→明治天皇、the Emperor→天皇）。
     只有中國、羅馬、俄國、德意志等的君主才譯「皇帝」。
   ‧ Crown Prince→皇太子（不作「太子」）；imperial court→朝廷；imperial household→皇室；
     imperial portrait→御真影。
   ‧ 佛教的 temple→**寺院／寺**；神道的 shrine→**神社**。兩者都**不作「廟」「寺廟」「廟宇」**
     （那是漢人民間信仰的用語，用在日本會失真）。僧侶→僧；住持→住持。
   ‧ daimyo／feudal lord→**大名**（不作「封建領主」）；藩主家臣之長→**家老**（不作「宰相」）；
     內閣總理大臣→**首相**（不作「宰相」）。
   ‧ 日本的**中央部會**才用「省」（文部省／外務省／內務省／農商務省／商工省）；
     Ministry of Education→**文部省**，不可作「教育省」。日本的**地方行政區是「縣」不是「省」**；
     provincial town→地方城市（不作「省城」）。
   ‧ 其他照日本原詞：元老、華族、士族、藩士、廢藩置縣、帝國議會、貴族院、樞密院、
     大政奉還、王政復古、御雇外國人。
8. 只輸出翻譯後的繁體中文。

日文原文：
{source}"""


_KANA_RE = re.compile(r"[ぁ-ゟ゠-ヿ]")
# 內村書裡夾著彌爾頓英詩、德文詩句，還有「＊　＊　＊」分隔與表格框線。這些送進
# 日→中的 prompt，引擎會（正確地）回「這不是日文」——那句招呼語就被寫進譯文欄。
# 沒有假名也沒有漢字＝不是日文散文，整段跳過；reader 端未填的段落本來就顯示原文。
_JP_RE = re.compile(r"[ぁ-ゟ゠-ヿ一-鿿]")


def needs_translation(src: str) -> bool:
    return bool(_JP_RE.search(src or ""))


# 🚨 引擎偶爾不翻，改用對話語氣回「我已準備好，請提供日文原文」。那句會被原樣
# 當成譯文存進去，而且因為排在段首還會變成**章節標題**（chapter_path 就長成
# 「時論與信仰 · 我已準備」）。高發於原文是殘片時——只有「１」或「である。」，
# 引擎（合理地）要求補完整。已在矢內原《讀書與著書》《耶穌傳》與賀川《垂訓》
# 共 7 段上線後才抓到。正解是留白不是硬翻：reader 端未填的段落會顯示原文。
# 判元回覆要**兩個條件同時成立**：對話語氣＋談翻譯任務本身。只看語氣會誤殺
# 正文（「我已準備妥當，要往耶路撒冷去」整句被丟掉過）；只看任務詞會漏。
_META_TONE = re.compile(
    r"我已準備|我準備好|請提供|請貼上|請給我|我注意到您|您未提供|您提供的|"
    r"我理解您|我將按照|我會按照|親愛的使用者|作為.{0,8}(?:譯者|助手)|"
    r"無法翻譯|I'm ready|Please provide")
_META_TASK = re.compile(r"原文|翻譯|日文|文本|段落|規則|內容|片段")
_SENT_RE = re.compile(r"[^。．.!！?？\n]{0,160}[。．.!！?？\n]\s*")


def _is_meta(sent: str) -> bool:
    return bool(_META_TONE.search(sent) and _META_TASK.search(sent))


def strip_meta_reply(out: str, window: int = 6) -> str:
    """剝掉開頭的對話式元回覆；整段都是元回覆就回空字串。

    切點取**開頭 window 句裡最後一句**元回覆，不是第一句非元回覆就收手——
    引擎常在中間夾一句沒有語氣詞的解釋（「這似乎是片段。」），
    逐句就停會把後面真正的譯文一起丟掉。
    """
    s = (out or "").strip()
    if not s:
        return ""
    ends, pos = [], 0
    for _ in range(window):
        m = _SENT_RE.match(s, pos)
        if not m:
            break
        ends.append((m.end(), _is_meta(m.group(0))))
        pos = m.end()
    cut = max((e for e, meta in ends if meta), default=0)
    s = re.sub(r"^[）)』」】\s]+", "", s[cut:].lstrip())   # 剝完的孤兒右括號
    return "" if cut and not s else s


def clean_zh_output(out: str) -> str:
    """Engine output → exactly ONE zh paragraph (keep reader row counts equal).

    Fixes two observed NVIDIA artifacts: stray U+FFFD/BOM noise chars, and
    source-echo in the form 「日文原文 → 譯文」 on short lines (detected by kana
    in the left half). A genuine `## ` heading line passes through untouched;
    other model-added heading lines are dropped; newlines collapse to spaces."""
    out = strip_meta_reply((out or "").replace("�", "").replace("﻿", ""))
    m = re.match(r"^(.*?)\s*→\s*(.+)$", out.strip(), re.S)
    if m and _KANA_RE.search(m.group(1)):
        out = m.group(2)
    if out.strip().startswith("## "):
        return re.sub(r"\s*\n\s*", " ", out.strip())
    out = re.sub(r"(?m)^\s*#{1,6}\s.*$", "", out)
    return re.sub(r"\s*\n\s*", " ", out).strip()


def make_engine(backend: str = "auto"):
    """translate_para(ja)->zh using the unified Gemini→NVIDIA→Haiku chain from
    translate_ebook_to_zh, with the Uchimura prompt. Mirrors panikkar_build."""
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = UCHIMURA_PROMPT_TMPL

    _clean = clean_zh_output

    def translate_para(ja: str) -> str:
        src = (ja or "").strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)

        def translate_piece(piece: str) -> str:
            if backend == "haiku":
                return te.haiku_translate(piece)
            if backend == "gemini":
                return te.gemini_translate(piece)
            if backend == "nvidia":
                return te.nvidia_translate(piece)
            return te.gemini_with_nvidia_fallback(piece)  # unified default chain

        out = ""
        for _ in range(4):  # retry-on-empty
            out = _clean(" ".join(translate_piece(p) for p in pieces))
            if out:
                return out
        return out

    return translate_para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="parse + counts only, no LLM")
    ap.add_argument("--work", type=str, default=None)
    args = ap.parse_args()
    slugs = [args.work] if args.work else QUEUE
    for slug in slugs:
        secs = load_work_sections(slug)
        w = REGISTRY[slug]
        total = sum(len(s["paras"]) for s in secs)
        print(f"{slug:20} {w['title']:12} sections={len(secs):3} paras={total:4}")
        if args.dry and args.work:
            for i, s in enumerate(secs):
                print(f"  sec{i} 「{s['heading'][:28]}」 ¶={len(s['paras'])}")


if __name__ == "__main__":
    main()
