# -*- coding: utf-8 -*-
"""胡塞爾《觀念一》→ en＋繁中逐段對照（帶原書頁碼與註腳）。

Edmund Husserl, 《Ideen zu einer reinen Phänomenologie und phänomenologischen
Philosophie. Erstes Buch》(1913)；本卷走 W. R. Boyce Gibson 1931 年英譯
《Ideas: General Introduction to Pure Phenomenology》(archive.org
`in.ernet.dli.2015.188260`，472 個掃描頁)。胡塞爾 1938 年卒、譯者 1935 年卒，
德文原著與這份英譯都已進入公有領域。

《西方現象學簡史》（/works western-phenomenology-history）第 4–6 章的底本，
其中第 5 章「本質直觀」是全書樞紐。

🚨 **為什麼不用 archive.org 現成的文字層**：這本的 `_djvu.txt` 全書
**零個希臘字母、零個德文變音字母**，而胡塞爾滿篇 ἐποχή／εἶδος／νόησις／
Wesensschau／Bewußtsein；英文本身也爛（實測 `{WesenserKemtm^Y'^S WsoTuteQ`）。
德文原著那份更糟——1913 年那版是**花體字排印**，OCR 把 Husserl 讀成 "Huffed"。
所以兩欄都得走 Gemini Vision 重 OCR。這條路的教訓寫在 [[archive_djvu]] 的
docstring 與 [[feedback_haiku_meta_reply_pollution]]：爛 OCR 餵進翻譯引擎，
出來的中文看起來很正常，內容是編的。

頁碼與註腳兩件事都由 Vision 在 OCR 當下標出來（`[[p N]]` 與 `[note] `），
不靠事後推：
  * `[[p N]]` = 該頁書眉印的頁碼；章首頁沒印就是 `[[p ?]]`，**不准猜**
    （[[feedback_transcribe_page_numbers]]：假頁碼比沒有更糟）。
  * `[note] ` = 頁末註腳，一條一行，絕不併進正文段落
    （[[feedback_transcribe_notes_and_bibliography]]）。
`fill_folios()` 只補 `[[p ?]]` 那幾頁，且只做阿拉伯數字的遞推。

OCR 是可續跑的：每批寫一份 `c:/tmp/husserl_cache/ocr/bNNN.json`，重跑自動跳過。
免費層額度很小（[[reference_gemini_free_tier_quotas]]），整本要跑好幾輪。

**OCR 完成之後到「可以翻譯」之間，還隔著六件事**（2026-09-12 全部做掉，每一件都是
「頁面完全正常而內容錯」那一類，肉眼看 --dry 看不出來）：

  1. `dedupe_pages` —— archive.org 這份掃描把印刷頁 176–177 **拍了兩次**，OCR 忠實地
     各轉錄一次。不去重站上就有一整頁重複，而且之後的頁碼整串對不上。
  2. `repair_folios` —— 書眉被讀成別的數字（scan100 讀成「4」）。`fill_folios` 只補
     「沒有值」的，補不到「值是錯的」。
  3. `split_glued` —— Vision 偶爾把整頁回成一行，章標題、§ 標題與正文黏成一串
     （`THIRD CHAPTER## THE REGION OF PURE CONSCIOUSNESS## § 47. …CONSCIOUSNESSIn`）。
     切不開就少一個章界，兩章併成一章。
  4. `strip_toc` —— p35–40 是目次。不丟掉就會把目次當正文翻掉兩百多段（而且每個
     「章」只有八到三十段，看起來還挺像的）。
  5. `restore_missing_heads` —— 章首頁沒有書眉，而 prompt 叫模型丟掉最上面那一行，
     模型就把章標題當書眉丟了（p171、p212 兩處）。缺的字一律**取自本書自己的目次**。
  6. `strip_back_matter` —— p429 起是 ANALYTICAL INDEX 與 INDEX TO PROPER NAMES，
     依既定政策只有 Index 可略（[[feedback_transcribe_notes_and_bibliography]]）。

目次是這本書自己的權威目錄，上面 4/5/6 三件都靠它判；`check_structure` 再拿它回頭
對帳一次——**目次說有幾章，切出來就該有幾章，順序也要一樣**（--dry 最後那一段）。

另加一道 OCR 閘門 `looks_page_collapsed`（一頁一段），與既有的 `looks_line_broken`
（一行一段）是同一個毛病的兩端。`--gates` 逐批複驗、`--redo` 重跑沒過的批。

  python scripts/husserl_build.py --ocr            # 續跑 OCR（可重複執行）
  python scripts/husserl_build.py --ocr --limit 5  # 只跑五批
  python scripts/husserl_build.py --gates          # 每批的段落切得對不對
  python scripts/husserl_build.py --redo           # 重跑沒過閘門的批（不過就不覆蓋）
  python scripts/husserl_build.py --dry            # 切出來的章節＋目次對帳
  python scripts/uchimura_auto.py --author husserl --run-queue
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from statistics import median

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import uchimura_build as ub  # noqa: E402  (loads .env, reconfigures stdout; clean_zh_output reused)
from archive_djvu import fill_folios, repair_folios  # noqa: E402

SOURCE_LANG = "en"
AUTHOR_ZH = "胡塞爾"
AUTHOR_EN = "Edmund Husserl"
CATEGORY = "哲學"
DATA_DIRNAME = "husserl_data"

CACHE = Path("c:/tmp/husserl_cache")
PDF_PATH = CACHE / "ideas_en.pdf"
OCR_DIR = CACHE / "ocr"
BATCH = 8            # 一次送幾個掃描頁；再大就會撞 32K 輸出上限
OCR_MODEL = "gemini-2.5-flash"   # 免費層唯一撐得住長批次的（3.5/3.6 只有 20 次／天／key）

REGISTRY: dict[str, dict] = {
    "husserl-ideas-i": {
        "ebook_id": "d0000000-0000-4000-8000-000000000021",
        "title": "純粹現象學通論：觀念一",
        "original_title": "Ideas: General Introduction to Pure Phenomenology (Ideen I)",
        "subtitle": "胡塞爾《觀念一》‧Boyce Gibson 英譯（英文＋繁中對照）",
        "year": 1913,
        "parent_volume": "現象學的建立",
        "archive_id": "in.ernet.dli.2015.188260",
        "pdf_pages": 472,
    },
}

QUEUE = ["husserl-ideas-i"]


# ── Vision OCR ───────────────────────────────────────────────────────────────

OCR_PROMPT = """\
This PDF is a scanned page range from W. R. Boyce Gibson's 1931 English translation of
Edmund Husserl's *Ideas: General Introduction to Pure Phenomenology* (Ideen I).

Extract the FULL text from EVERY page. Output ONLY a JSON object:
{"pages":[{"page":1,"text":"..."}]}

Rules:
- "page" is the 1-based PDF page number within THIS file.
- The FIRST LINE of each page's "text" must be ONLY the marker [[p 12]], where 12 is the
  PRINTED page number shown in that page's running head. Nothing else on that line.
  If the page carries no printed number (chapter openings, plates, blanks), write [[p ?]].
  NEVER invent or infer a number — [[p ?]] is correct there.
- 🚨 DROP THE RUNNING HEAD ENTIRELY. The running head is the topmost line, carrying the page
  number together with a book or chapter title in capitals ("FACT AND ESSENCE",
  "PURE PHENOMENOLOGY", "IDEAS"). Its title text must NOT appear in the output at all —
  not on the [[p N]] line, not at the start of the first paragraph. Body text begins on the
  line AFTER the running head.
- Then the body text, preserving paragraph breaks with \\n. Put every chapter or major
  section TITLE on its own line prefixed with "## " (e.g. "## FIRST CHAPTER",
  "## § 27. THE WORLD OF THE NATURAL STANDPOINT"). Husserl's section numbers (§ 1, § 24 …)
  belong on the same line as their title.
- FOOTNOTES: put every footnote at the END of that page's text, each on its own line,
  prefixed with "[note] " and keeping its marker (e.g. "[note] 1 Cf. Logische Untersuchungen II").
  Footnotes are NOT body text and must never be merged into a body paragraph.
- 🚨 PRESERVE NON-ENGLISH SCRIPT EXACTLY. This book is full of Greek (ἐποχή, εἶδος, νοῦς,
  νόησις, νόημα, ὕλη) and German (Wesen, Wesensschau, Erlebnis, Bewußtsein, Einklammerung,
  phänomenologisch). Reproduce Greek in Greek letters with its diacritics, and German with
  its umlauts and ß. Do NOT transliterate, romanise, translate, or drop them.
- 🚨 JOIN WORDS BROKEN ACROSS LINE ENDS. The typesetter hyphenates at the right margin
  ("con-/tinues", "Daseinsset-/zung", "character-/ized"). Output the whole word
  ("continues", "Daseinssetzung", "characterized") with NO hyphen and NO line break inside it.
  Keep hyphens that genuinely belong to the word ("temporo-spatial", "self-evidence").
- Run each paragraph together as ONE line. Only start a new line at a real paragraph break.
- Preserve italics as-is in plain text (no markdown emphasis), keep quotation marks.
- DO NOT translate, summarize, correct, or interpret. Output the original text only.
"""


# Vision 偶爾整批**一行一段**地回（照排印行斷，不照段落斷）。同一份 prompt、
# 同一個模型，換一批就可能犯——所以不能只靠 prompt，要靠閘門擋下來重跑。
OCR_PROMPT_STRICT = OCR_PROMPT + """
🚨🚨 CRITICAL — YOUR LAST ATTEMPT AT THIS PAGE RANGE FAILED THIS RULE:
You returned ONE LINE PER TYPESET LINE. That is wrong. The line breaks you see on the
scanned page are just where the typesetter ran out of margin; they are NOT paragraph breaks.
A paragraph in this book runs for many typeset lines and ends with a full stop.
Concatenate every typeset line of a paragraph into a SINGLE line of output, inserting a
space where the line broke (and NO space when a word was hyphenated across the break).
Emit a newline ONLY at a genuine paragraph break — i.e. where the printed text is indented,
or a heading starts. Most pages of this book contain between 1 and 5 paragraphs, not 30.
"""


def looks_line_broken(units: list[dict]) -> bool:
    """整批是不是「一行一段」地回來了。

    🚨 這是本管線最危險的一種錯：段數看起來很多、頁碼齊全、頁面完全正常，但每一
    「段」其實是半句話。逐句送進翻譯引擎，出來的中文是把殘句當完整句翻的胡話。

    判準要兩條**同時**成立，不能只看段長——扉頁、目錄、獻詞那幾頁本來就是短行，
    只看長度會把它們全誤判掉：
      1. 正文段的中位長度短於一條排印行的量級（< 150 字）
      2. 句尾完整率偏低（< 60%）。正常散文每段以句號收尾；跨頁續段會讓這個比率
         打折，所以門檻不設高。
    """
    body = [u["text"] for u in units
            if u["kind"] == "body" and not u["text"].startswith("##")]
    if len(body) < 20:
        return False
    med = median([len(t) for t in body])
    ends = sum(1 for t in body if t.rstrip().endswith((".", "?", "!", '"', "”", "’", ":", ";")))
    return med < 150 and (ends / len(body)) < 0.60


OCR_PROMPT_UNCOLLAPSE = OCR_PROMPT + """
🚨🚨 CRITICAL — YOUR LAST ATTEMPT AT THIS PAGE RANGE FAILED THIS RULE:
You returned EACH PAGE AS ONE SINGLE LINE, running every paragraph of the page together
with no break — "…as intentional unities.But we can go farther…". That is wrong.
A page of this book normally holds 2 to 5 paragraphs. A new paragraph is printed with its
first line INDENTED; that indent is the paragraph break, and it must become a newline in
your output. Emit each paragraph on its own line, and never let a sentence-ending full stop
sit directly against the next sentence's capital letter without a space.
"""

# 句號直接黏著下一句的大寫開頭（"unities.But"）＝段落界線在 OCR 那一步就沒了。
_SENTENCE_GLUE = re.compile(r"[a-z]{2}[.?!][”\"']?[A-Z][a-z]")


def looks_page_collapsed(pages: list[dict]) -> bool:
    """整頁被回成一則（段落界線全沒了）。

    🚨 這與 `looks_line_broken` 是同一個毛病的兩端：那邊把一行當一段（段太多），
    這邊把一頁當一段（段太少）。兩者都不會少字，頁碼也齊，所以肉眼看 --dry 看不出來
    ——但一段兩千字送進翻譯引擎會被 `split_oversized` 切在句子中間，而且英文欄讀起來
    是「unities.But」這種黏字。

    判準要兩條同時成立，且要有兩頁以上中鏢（單頁確實可能整頁只有一段）：
      1. 這一頁正文只有一兩則，卻超過 1200 字
      2. 那幾則裡「句號後沒有空白就接大寫」至少兩處
    """
    hits = 0
    for p in pages:
        _f, units = parse_page(p.get("text") or "")
        body = [u["text"] for u in units
                if u["kind"] == "body" and not u["text"].startswith("##")]
        if len(body) <= 2 and sum(len(t) for t in body) > 1200 \
                and sum(len(_SENTENCE_GLUE.findall(t)) for t in body) >= 2:
            hits += 1
    return hits >= 2


def batches(total: int, size: int = BATCH) -> list[tuple[int, int]]:
    """(start, end) 逐批，1-based、含端點。"""
    return [(s, min(s + size - 1, total)) for s in range(1, total + 1, size)]


def batch_path(lo: int) -> Path:
    return OCR_DIR / f"b{lo:04d}.json"


def batch_gate(pages: list[dict]) -> str | None:
    """這一批的段落切得對不對：'line-broken'（一行一段）／'collapsed'（一頁一段）／None。"""
    units = [u for p in pages for u in parse_page(p.get("text") or "")[1]]
    if looks_line_broken(units):
        return "line-broken"
    if looks_page_collapsed(pages):
        return "collapsed"
    return None


def run_ocr(slug: str = "husserl-ideas-i", limit: int = 0,
            redo: list[int] | None = None) -> int:
    """續跑 Vision OCR，回傳這一輪新完成的批數。已有快取的批直接跳過。

    `redo` 指定要重跑的批（批的起始掃描頁）。重跑只在**新的一批通過閘門**時才覆蓋
    舊快取——不然一次壞的重跑會把本來就不完美但可用的內容換掉。
    """
    import ocr_pdf_to_text as o

    OCR_DIR.mkdir(parents=True, exist_ok=True)
    total = REGISTRY[slug]["pdf_pages"]
    redo = set(redo or [])
    todo = [(lo, hi) for lo, hi in batches(total)
            if lo in redo or not batch_path(lo).exists()]
    print(f"OCR {slug}：共 {len(batches(total))} 批，待跑 {len(todo)} 批", flush=True)
    done = 0
    for lo, hi in todo:
        if limit and done >= limit:
            break
        pages, broken, prompt = None, None, OCR_PROMPT
        for attempt in (1, 2, 3):
            try:
                pages = o.ocr_pdf(PDF_PATH, model=OCR_MODEL, pages=(lo, hi), prompt=prompt)
            except Exception as e:  # noqa: BLE001
                print(f"  ✗ pp{lo}-{hi} 停在：{str(e)[:120]}", flush=True)
                pages = None
                break
            broken = batch_gate(pages)
            if not broken:
                break
            print(f"  ⚠ pp{lo}-{hi} {broken}，重跑（第 {attempt} 次）", flush=True)
            # 對症下藥：一行一段用 STRICT，一頁一段用 UNCOLLAPSE
            prompt = OCR_PROMPT_STRICT if broken == "line-broken" else OCR_PROMPT_UNCOLLAPSE
        if pages is None:
            break
        if lo in redo and broken:
            print(f"  · pp{lo}-{hi} 重跑仍 {broken}，保留舊快取", flush=True)
            continue
        payload = {"pages": pages, "gate": broken or "ok"}
        batch_path(lo).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        got = sum(1 for p in pages if (p.get("text") or "").strip())
        done += 1
        flag = f"  ⚠ 仍 {broken}" if broken else ""
        print(f"  ✓ pp{lo}-{hi}  {got}/{hi - lo + 1} 頁有內容{flag}", flush=True)
    left = sum(1 for lo, _hi in batches(total) if not batch_path(lo).exists())
    print(f"本輪完成 {done} 批，尚餘 {left} 批", flush=True)
    return done


def failed_batches(slug: str = "husserl-ideas-i") -> list[tuple[int, str]]:
    """已快取但沒過閘門的批 [(起始掃描頁, 毛病)]。閘門是後來才加的，所以不看快取裡
    存的 gate 欄位，一律當場重判。"""
    out = []
    for lo, _hi in batches(REGISTRY[slug]["pdf_pages"]):
        f = batch_path(lo)
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        pages = data["pages"] if isinstance(data, dict) else data
        why = batch_gate(pages)
        if why:
            out.append((lo, why))
    return out


def load_ocr_pages(slug: str = "husserl-ideas-i") -> list[dict]:
    """快取 → [{page(掃描頁), text}]，依掃描頁排序。缺的批直接跳過（可續跑）。"""
    out: list[dict] = []
    for lo, _hi in batches(REGISTRY[slug]["pdf_pages"]):
        f = batch_path(lo)
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        # 舊快取是純 list，新的是 {"pages": [...], "gate": "..."}
        out.extend(data["pages"] if isinstance(data, dict) else data)
    return sorted(out, key=lambda p: p.get("page", 0))


# ── 掃描頁去重（純函式）──────────────────────────────────────────────────────

_ALNUM = re.compile(r"[^a-z0-9]+")
FINGERPRINT_LEN = 400
MIN_FOLIOS_TO_REPAIR = 5


def page_fingerprint(text: str) -> str:
    """一頁的正規化指紋：去頁碼／標記／標點大小寫後的前 400 字。

    比不到 400 字就回空字串＝**不參與去重**。寧可漏掉一張重複的章首頁，也不要
    把兩張都很短、內容本來就相近的頁（扉頁、分部頁）誤判成重複而刪掉正文。
    """
    t = _FOLIO_RE.sub(" ", text or "").replace("##", " ").replace(_NOTE_PREFIX, " ")
    t = _ALNUM.sub(" ", t.lower()).strip()
    return t[:FINGERPRINT_LEN] if len(t) >= FINGERPRINT_LEN else ""


def dedupe_pages(pages: list[dict]) -> tuple[list[dict], list[int]]:
    """丟掉「同一頁被拍了兩次」的那一張，回傳 (留下的頁, 丟掉的掃描頁號)。

    🚨 這本 archive.org 掃描檔的 PDF 第 177、178 張，是印刷頁 176、177 的**第二次
    拍攝**（兩張照片、像素不同，所以雜湊比不出來；OCR 忠實地各轉錄一次）。不去重
    的話站上就會有整整兩頁一字不差的重複，而頁面完全正常、頁碼也齊——正是最難查覺
    的那一種（[[ebook-scan-transcribe]] 的重複頁）。之後的頁碼也會整串對不上：
    重複之前 folio＝掃描頁＋1，重複之後變成掃描頁－1。
    """
    seen: dict[str, int] = {}
    keep: list[dict] = []
    dropped: list[int] = []
    for p in pages:
        fp = page_fingerprint(p.get("text") or "")
        if fp and fp in seen:
            dropped.append(p.get("page"))
            continue
        if fp:
            seen[fp] = p.get("page")
        keep.append(p)
    return keep, dropped


# ── 頁碼／註腳／段落（純函式，測試在 scripts/tests/test_husserl_build.py）─────

_FOLIO_RE = re.compile(r"^\s*\[\[p\s*([0-9]+|\?)\s*\]\]\s*", re.M)
_NOTE_PREFIX = "[note]"
# 「experi- ence」這種殘留的行末斷詞。真正該留的連字號後面不會有空白
# （temporo-spatial、self-evidence），所以「小寫字母 + 連字號 + 空白 + 小寫字母」
# 是很乾淨的判準。
_SOFT_HYPHEN = re.compile(r"([a-zäöüß])-\s+([a-zäöüß])")
# 行內（不在行首）的標記＝Vision 把好幾件東西黏成一行了。
_INLINE_MARK = re.compile(r"##\s*|\[note\]\s+")
# 「…CORRELATE OF CONSCIOUSNESSIn connexion with…」：全大寫的標題直接黏著正文，
# 中間沒有任何分隔。大寫跑完接一個「大寫＋小寫」就是接縫。
_HEAD_BODY_SEAM = re.compile(r"(?<=[A-Z]{2})(?=[A-Z][a-z])")
SEAM_MIN_TAIL = 40


def _is_shouting(text: str) -> bool:
    """字母幾乎全大寫＝正文標題那一層（目次那一層是 Title Case）。"""
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 6:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.8


def split_head_from_body(piece: str) -> list[str]:
    """把黏在標題尾巴的正文拆出來。拆不出來就原樣回傳一則。

    只對**全大寫**的標題動手：目次那一層是 Title Case，照這個接縫去切會把
    「§ 29. The “other” Ego-subjects…」這種條目切爛。
    """
    if not piece.startswith("##"):
        return [piece]
    m = _HEAD_BODY_SEAM.search(piece)
    if not m or len(piece) - m.start() < SEAM_MIN_TAIL or not _is_shouting(piece[:m.start()]):
        return [piece]
    return [piece[:m.start()].strip(), piece[m.start():].strip()]


def split_glued(line: str) -> list[str]:
    """一行 → 多則。Vision 偶爾整頁回成一行，標題與正文全黏在一起。

    🚨 這與 `looks_line_broken` 是同一個毛病的兩個方向：那邊是把一行當一段，
    這邊是把一頁當一行。實測全書 7 行有行內殘留的 `##`，其中 scan146 一行裡黏了
    「THIRD CHAPTER」「THE REGION OF PURE CONSCIOUSNESS」「§ 47 標題」與正文四件事。
    切不開的話這一章的章界就消失，整章被併進上一章（頁面完全正常）。
    """
    s = (line or "").strip()
    if not s:
        return []
    cuts = [m.start() for m in _INLINE_MARK.finditer(s) if m.start() > 0]
    pieces, prev = [], 0
    for c in cuts:
        pieces.append(s[prev:c])
        prev = c
    pieces.append(s[prev:])
    out: list[str] = []
    for p in pieces:
        out.extend(split_head_from_body(p.strip()))
    return [p.strip() for p in out if p.strip()]


def parse_page(text: str) -> tuple[str | None, list[dict]]:
    """一頁的 OCR 文字 → (folio, units)。folio 為 None 代表該頁印刷頁碼不明。

    units 的 kind 只有 body 與 note 兩種；note 一律排在該頁 body 之後。
    """
    t = text or ""
    folio: str | None = None
    m = _FOLIO_RE.match(t)
    if m:
        folio = None if m.group(1) == "?" else m.group(1)
        t = t[m.end():]
    t = _FOLIO_RE.sub("", t)          # 同一批偶爾把兩頁併在一起，把殘留的標記清掉
    body, notes = [], []
    for raw in t.split("\n"):
        for piece in split_glued(raw):
            line = _SOFT_HYPHEN.sub(r"\1\2", piece)
            if not line:
                continue
            if line.startswith(_NOTE_PREFIX):
                note = line[len(_NOTE_PREFIX):].strip()
                if note:
                    notes.append(note)
            else:
                body.append(line)
    units = [{"kind": "body", "text": b} for b in body]
    units += [{"kind": "note", "text": n} for n in notes]
    return folio, units


def paged_units(pages: list[dict]) -> list[dict]:
    """全書 → [{kind, text, page}]，page 已補過章首頁那種沒印頁碼的。"""
    parsed = [parse_page(p.get("text") or "") for p in pages]
    # 🚨 先 repair 再 fill：`fill_folios` 只補「沒有值」的頁，補不到**值是錯的**那種
    # （實測 scan100 的書眉被讀成「4」，整章的頁碼範圍就長成 p4–111）。
    # repair 是靠鄰頁互相對帳的，頁數太少時沒有鄰頁可對，它會把僅有的那個頁碼也清掉
    # ——所以少於 MIN_FOLIOS_TO_REPAIR 個就不修（一兩頁的呼叫多半是測試或抽樣）。
    raw = [f for f, _u in parsed]
    if sum(1 for f in raw if f and f.isdigit()) >= MIN_FOLIOS_TO_REPAIR:
        raw = repair_folios(raw)
    folios = fill_folios(raw)
    out: list[dict] = []
    for (_f, units), folio in zip(parsed, folios):
        for u in units:
            out.append({**u, "page": folio})
    return out


_HEADING = re.compile(r"^##\s+(.*\S)\s*$")
# 章界只認「章」那一層（FIRST CHAPTER / SECOND SECTION / INTRODUCTION…），
# § 那一層是章內小節，拿它切章會切出兩百多個一段的「章」。
_CHAPTER_HEAD = re.compile(
    r"^(?:[A-Z]+\s+(?:CHAPTER|SECTION|PART)|CHAPTER|SECTION|PART|INTRODUCTION|PREFACE|"
    r"AUTHOR'S PREFACE|TRANSLATOR'S PREFACE|CONTENTS|INDEX)\b", re.I)


def is_chapter_head(title: str) -> bool:
    return bool(_CHAPTER_HEAD.match(title.strip()))


# ── 目次＝本書自己的權威目錄（純函式）────────────────────────────────────────
#
# 這本的 CONTENTS 印在 p35–40，**在作者序之後、正文之前**。它列出每一章的標題、
# 副標與起始頁，所以三件事都靠它判：
#   1. 哪一段 units 是目次（要整塊丟掉，否則會把目次當正文翻兩百多段）
#   2. OCR 在章首頁吞掉的章標題該補什麼、補在哪一頁
#   3. 後附索引從哪一頁開始（正文到哪裡為止）
# 補回去的字一律取自目次，不是自己編的。

_TOC_PAGE = re.compile(r"\s(\d{1,3})$")
_HEAD_WORD = re.compile(
    r"^(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH)\s+(?:SECTION|CHAPTER|PART)$", re.I)


def _bare(text: str) -> str:
    """去掉 `## ` 標記。"""
    m = _HEADING.match(text.strip())
    return (m.group(1) if m else text).strip()


def _tocish(text: str) -> bool:
    """看起來像目次的一行：標題行、帶尾端頁碼的條目、或「CONTENTS」「PAGE」這種欄頭。"""
    t = _bare(text)
    if text.strip().startswith("##"):
        return True
    if _TOC_PAGE.search(t) and len(t) < 200:
        return True
    return t.isupper() and len(t) <= 60


def toc_span(units: list[dict], min_entries: int = 20) -> tuple[int, int] | None:
    """目次區塊的 [起, 迄) unit 索引；找不到就回 None（寧可不丟，也不要丟錯）。

    自「CONTENTS」那一行往後吃，吃到最後一個**帶尾端頁碼**的條目為止。以「最後一個
    帶頁碼的條目」收尾，是為了不要順手把正文的第一個標題（`## INTRODUCTION`，它沒有
    尾端頁碼）也吃掉。
    """
    start = next((i for i, u in enumerate(units)
                  if _bare(u["text"]).upper() == "CONTENTS"), None)
    if start is None:
        return None
    last, entries, i = None, 0, start
    while i < len(units) and _tocish(units[i]["text"]):
        if _TOC_PAGE.search(_bare(units[i]["text"])):
            last, entries = i, entries + 1
        i += 1
    if last is None or entries < min_entries:
        return None
    return start, last + 1


def parse_toc(units: list[dict]) -> list[dict]:
    """目次 → [{title, subtitle, page}]，章級以上，依書中順序。

    § 那一層只拿來補頁碼：章的副標偶爾漏印頁碼（p36 的「THE THESIS OF THE NATURAL
    STANDPOINT…」就沒有），這時用該章第一個 § 的頁碼。
    """
    span = toc_span(units)
    if not span:
        return []
    lo, hi = span
    out: list[dict] = []
    pending = False          # 上一行是「FIRST CHAPTER」這種，下一行該是它的副標
    for u in units[lo:hi]:
        t = _bare(u["text"]).strip()
        if not t or t.upper() in ("CONTENTS", "PAGE"):
            continue
        m = _TOC_PAGE.search(t)
        page = int(m.group(1)) if m else None
        title = (t[:m.start()] if m else t).strip()
        if t.startswith("§"):
            if out and out[-1]["page"] is None and page is not None:
                out[-1]["page"] = page
            pending = False
            continue
        if _HEAD_WORD.match(title):
            out.append({"title": title.upper(), "subtitle": "", "page": page})
            pending = True
        elif pending and out:
            out[-1]["subtitle"] = title.upper()
            if page is not None:
                out[-1]["page"] = page
            pending = False
        else:
            out.append({"title": title.upper(), "subtitle": "", "page": page})
            pending = False
    return out


def strip_toc(units: list[dict]) -> tuple[list[dict], int]:
    """把目次那一塊整段拿掉，回傳 (剩下的 units, 丟掉幾則)。"""
    span = toc_span(units)
    if not span:
        return units, 0
    lo, hi = span
    return units[:lo] + units[hi:], hi - lo


def index_start_page(spec: list[dict]) -> int | None:
    """後附索引的起始印刷頁；判不出來就回 None（那就整本都當正文，不敢砍）。"""
    idx = [e["page"] for e in spec if "INDEX" in e["title"] and e["page"]]
    chapters = [e["page"] for e in spec if _HEAD_WORD.match(e["title"]) and e["page"]]
    if not idx:
        return None
    first = min(idx)
    if chapters and first <= max(chapters):
        return None      # 目次讀壞了（索引頁碼竟在最後一章之前）——不砍
    return first


def strip_back_matter(units: list[dict], spec: list[dict]) -> tuple[list[dict], int]:
    """砍掉後附索引起就不再是正文的部分，回傳 (正文 units, 砍掉幾則)。

    依既定政策只有 Index 可略（[[feedback_transcribe_notes_and_bibliography]]）；
    這本的兩份索引（ANALYTICAL INDEX p429、INDEX TO PROPER NAMES p466）之後就只剩
    出版社書目廣告。不砍的話最後一章會多出 616 段索引詞條——章數看起來對，內容是
    索引（`## ANALYTICAL INDEX` 不以 INDEX 起頭，切章那條規則抓不到它）。
    """
    p0 = index_start_page(spec)
    if p0 is None:
        return units, 0
    cut = next((i for i, u in enumerate(units)
                if (u["page"] or "").isdigit() and int(u["page"]) >= p0), None)
    if cut is None:
        return units, 0
    return units[:cut], len(units) - cut


def _norm_head(text: str) -> str:
    return re.sub(r"[^A-Z0-9§]+", "", _bare(text).upper())


def restore_missing_heads(units: list[dict],
                          spec: list[dict]) -> tuple[list[dict], list[str]]:
    """OCR 在章首頁吞掉的章標題，依目次補回原位；回傳 (units, 補了哪些)。

    🚨 這是**系統性**的漏，不是偶發：章首頁沒有書眉，而 OCR prompt 叫模型「把最上面
    那一行（書眉）整行丟掉」——模型於是把章標題當書眉丟了。實測漏兩處：p171 的
    「FOURTH CHAPTER」（副標還在）、p212 的「SECOND CHAPTER」連副標一起。少一個章界，
    兩章就併成一章，而頁面完全正常。

    補的位置用**印刷頁碼**對，不用段落序號對（段落序號會隨 OCR 重跑而變）。同一頁上
    已經有的標題不重複補。
    """
    out = list(units)
    log: list[str] = []
    for e in spec:
        if not e["page"]:
            continue
        page = str(e["page"])
        at = [i for i, u in enumerate(out) if u["page"] == page]
        if not at:
            continue
        heads = {_norm_head(out[i]["text"]): i for i in at
                 if out[i]["text"].strip().startswith("##")}
        ti, si = heads.get(_norm_head(e["title"])), heads.get(_norm_head(e["subtitle"]))
        if ti is None:
            out.insert(at[0], {"kind": "body", "text": f"## {e['title']}", "page": page})
            ti = at[0]
            log.append(f"p{page} 補回章標題「{e['title']}」")
            if si is not None and si >= ti:
                si += 1
        if e["subtitle"] and si is None:
            out.insert(ti + 1, {"kind": "body", "text": f"## {e['subtitle']}", "page": page})
            log.append(f"p{page} 補回副標「{e['subtitle']}」")
    return out, log


def check_structure(secs: list[dict], spec: list[dict]) -> list[str]:
    """切出來的章節 vs 目次宣告的章節，逐項比。回傳每一項的對帳字串。

    🚨 這條線上每一次出錯都是頁面完全正常而內容錯，所以不靠肉眼看 --dry，靠這支對帳：
    目次說有幾章，切出來就該有幾章，順序也要一樣。
    """
    want = [e for e in spec if "INDEX" not in e["title"]]
    got = [s for s in secs if s["heading"]]
    rows = []
    for i, e in enumerate(want):
        s = got[i] if i < len(got) else None
        ok = s is not None and _norm_head(s["heading"]) == _norm_head(e["title"]) \
            and _norm_head(s.get("subtitle", "")) == _norm_head(e["subtitle"])
        zh = title_zh_for(s) if s else None
        rows.append(f"{'✓' if ok else '✗'} {e['title']}"
                    f"{'／' + e['subtitle'] if e['subtitle'] else ''}"
                    f"{'　→ ' + zh if zh else '　⚠ 沒有寫死的中文章名'}"
                    f"{'' if ok else f'  ← 切出來的是「{s['heading'] if s else '—'}」'}")
    for extra in got[len(want):]:
        rows.append(f"✗ 目次沒有這一章：「{extra['heading']}」")
    return rows


def split_sections(units: list[dict]) -> list[dict]:
    """units → [{heading, subtitle, paras, pages}]。章界＝章級標題；§ 小節標題留在正文裡
    當一行（reader 會照排），不另外切段——否則段落數會爆掉。

    `subtitle` 是章標題下面那一行（「FIRST CHAPTER」之下的「FACT AND ESSENCE」）。
    要留著它，因為「FIRST CHAPTER」在這本書裡出現四次，只看它分不出是哪一章——
    reader 的目錄會變成四個「第一章」。副標本身仍留在 paras 裡（書上就印著）。
    """
    secs: list[dict] = []
    cur = {"heading": "", "subtitle": "", "paras": [], "pages": []}
    for u in units:
        m = _HEADING.match(u["text"])
        title = m.group(1) if m else None
        if title and is_chapter_head(title):
            if cur["paras"]:
                secs.append(cur)
            cur = {"heading": title, "subtitle": "", "paras": [], "pages": []}
            continue
        if title and not cur["paras"] and cur["heading"] and not title.startswith("§"):
            cur["subtitle"] = title
        cur["paras"].append(u["text"])
        cur["pages"].append(u["page"])
    if cur["paras"]:
        secs.append(cur)
    return secs


def build_units(pages: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """掃描頁 → (正文 units, 目次 spec, 對帳報告)。

    順序不可換：**去重 → 修頁碼 → 丟目次 → 砍後附索引 → 補章標題**。
    補章標題要在丟目次之後（否則會對到目次那幾頁），砍索引要在補之前（索引那兩筆
    spec 才不會去正文裡亂找）。
    """
    pages, dup = dedupe_pages(pages)
    units = paged_units(pages)
    spec = parse_toc(units)
    units, n_toc = strip_toc(units)
    units, n_back = strip_back_matter(units, spec)
    units, restored = restore_missing_heads(units, spec)
    return units, spec, {"dup_pages": dup, "toc_units": n_toc,
                         "back_units": n_back, "restored": restored}


# 章名的中譯**寫死**，不交給引擎。理由有二：
#   1. 「FIRST CHAPTER」在這本書裡出現四次，逐章送去翻只會得到四個「第一章」，
#      reader 的目錄與每段的 chapter_path 就分不出是哪一章。
#   2. 章名是全書最顯眼的十幾行字，術語要與正文 prompt 的對照表一致（本質直觀／
#      自然態度／懸置／能思／所思），交給引擎每次可能不一樣。
# key＝(章標題, 副標)，都取 OCR 出來的原樣。漏對到就退回引擎翻（--dry 會列出來）。
TITLES_ZH: dict[tuple[str, str], str] = {
    ("", ""): "叢書說明",
    ("AUTHOR'S PREFACE TO THE ENGLISH EDITION", ""): "英文版作者序",
    ("TRANSLATOR'S PREFACE", ""): "譯者序",
    ("INTRODUCTION", ""): "導論",
    ("FIRST SECTION", "THE NATURE AND KNOWLEDGE OF ESSENTIAL BEING"):
        "第一部分　本質與本質知識",
    ("FIRST CHAPTER", "FACT AND ESSENCE"): "第一章　事實與本質",
    ("SECOND CHAPTER", "NATURALISTIC MISCONSTRUCTIONS"): "第二章　自然主義的誤解",
    ("SECOND SECTION", "THE FUNDAMENTAL PHENOMENOLOGICAL OUTLOOK"):
        "第二部分　現象學的基本觀點",
    ("FIRST CHAPTER", "THE THESIS OF THE NATURAL STANDPOINT AND ITS SUSPENSION"):
        "第一章　自然態度的總設定及其懸置",
    ("SECOND CHAPTER", "CONSCIOUSNESS AND NATURAL REALITY"): "第二章　意識與自然實在",
    ("THIRD CHAPTER", "THE REGION OF PURE CONSCIOUSNESS"): "第三章　純粹意識的區域",
    ("FOURTH CHAPTER", "THE PHENOMENOLOGICAL REDUCTIONS"): "第四章　現象學還原",
    ("THIRD SECTION", "PROCEDURE OF PURE PHENOMENOLOGY IN RESPECT OF METHODS AND PROBLEMS"):
        "第三部分　純粹現象學的方法與問題",
    ("FIRST CHAPTER", "PRELIMINARY CONSIDERATIONS OF METHOD"): "第一章　方法的初步考察",
    ("SECOND CHAPTER", "GENERAL STRUCTURES OF PURE CONSCIOUSNESS"):
        "第二章　純粹意識的一般結構",
    ("THIRD CHAPTER", "NOESIS AND NOEMA"): "第三章　能思與所思",
    ("FOURTH CHAPTER", "THEORY OF THE NOETIC-NOEMATIC STRUCTURES: ELABORATION OF THE PROBLEMS"):
        "第四章　能思—所思結構論：問題的展開",
    ("FOURTH SECTION", "REASON AND REALITY (WIRKLICHKEIT)"): "第四部分　理性與實在",
    ("FIRST CHAPTER", "NOEMATIC MEANING AND RELATION TO THE OBJECT"):
        "第一章　所思意義與對象關係",
    ("SECOND CHAPTER", "PHENOMENOLOGY OF THE REASON"): "第二章　理性的現象學",
    ("THIRD CHAPTER",
     "GRADES OF GENERALITY IN THE ORDERING OF THE PROBLEMS OF THE THEORETIC REASON"):
        "第三章　理論理性問題編排的普遍性層級",
}


def title_zh_for(sec: dict) -> str | None:
    return TITLES_ZH.get((sec["heading"].strip(), sec.get("subtitle", "").strip()))


def load_work_sections(slug: str = "husserl-ideas-i") -> list[dict]:
    units, _spec, _report = build_units(load_ocr_pages(slug))
    secs = split_sections(units)
    for s in secs:
        zh = title_zh_for(s)
        if zh:                       # 對不到就不給值，讓 uchimura_auto 那邊去翻標題
            s["title_zh"] = zh
    return secs


# ── 翻譯 ─────────────────────────────────────────────────────────────────────

HUSSERL_PROMPT_TMPL = """你是現象學的專業譯者，正在翻譯胡塞爾《觀念一》（Ideen I）的 Boyce Gibson 英譯本。把下列英文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
1b. **西元年份一律用阿拉伯數字**：一八九三年→**1893 年**、一九二〇年代→**1920 年代**。🚨 年號紀年照漢數字不可改（明治二十四年、大正十二年），數量與序數也不改（三十年、第三章、二十世紀）。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。
3. 語域：哲學論著的說理散文。胡塞爾句子長、子句層層相扣，中譯要斷得開、讀得懂，但**不可拆掉論證的層次**，也不可把他的保留語氣（「就其本質而言」「原則上」「在某種意義下」）簡化掉。
4. `## ` 開頭的是標題，照留 `## `；以「§」起頭的小節標題同樣照留。
5. 🚨 **原文裡本來就印成希臘字母／德文的詞，一律原樣保留，不要翻、不要轉寫**（ἐποχή、εἶδος、νόησις、νόημα、ὕλη、Wesen、Erlebnis、Bewußtsein）。首次出現可在其後加括號中譯，其餘照留原詞。
5b. 🚨 **反過來也一樣：原文印成拉丁字母的英文術語就要譯成中文，不可以改寫成希臘字母。** `NOESIS AND NOEMA` 要譯成「能思與所思」，不是「νόησις AND νόημα」；noema／noesis／hyle／epoché／eidos 同理。標題尤其常犯這個錯，連中間的 and 都忘了譯。
6. **術語一對一，全書不得改口**：
   ‧ phenomenology→現象學；phenomenological reduction→現象學還原；transcendental→**超越論的**（不作「先驗的」，那是 a priori 的譯法）
   ‧ eidetic→**本質的**（eidetic science→本質科學、eidetic intuition→**本質直觀**）；essence→本質；Wesensschau→本質直觀
   ‧ epoché／suspension／bracketing→**懸置**（動詞用「予以懸置」）；Einklammerung→加括號
   ‧ the natural standpoint→**自然態度**；thesis of the natural standpoint→自然態度的總設定
   ‧ intentionality→意向性；intentional→意向的；noesis→**能思**（νόησις 照留）；noema→**所思**（νόημα 照留）；hyle→質料層（ὕλη 照留）
   ‧ consciousness→意識；stream of consciousness→意識流；Erlebnis／mental process／experience（指體驗時）→**體驗**；experience（指經驗時）→經驗
   ‧ intuition→直觀；originary／primordial dator intuition→**原初給予的直觀**；evidence→明證性
   ‧ constitution→構成；region／regional ontology→區域／區域存有論；horizon→視域
   ‧ fact→事實；matter of fact→事實性存在；immanent／transcendent→內在的／超越的
   ‧ Ego／pure Ego→自我／純粹自我；subjectivity→主體性
7. 人名依 `/translation-glossary` 的哲學家表：Husserl→胡塞爾、Brentano→布倫塔諾、Descartes→笛卡兒、Kant→康德、Hume→休謨、Locke→洛克、Berkeley→柏克萊、Leibniz→萊布尼茲、Bolzano→波爾查諾、Lotze→洛策、Dilthey→狄爾泰、Natorp→那托普、Riehl→里爾。
8. 書名：Logische Untersuchungen→《邏輯研究》；Ideen→《觀念》；Philosophie der Arithmetik→《算術哲學》。
9. 只輸出翻譯後的繁體中文。

英文原文：
{source}"""


def make_engine(backend: str = "auto"):
    """translate_para(en)->zh；引擎鏈沿用 uchimura_build，只換 prompt。"""
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = HUSSERL_PROMPT_TMPL

    def translate_para(en: str) -> str:
        src = (en or "").strip()
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
            return te.gemini_with_nvidia_fallback(piece)

        out = ""
        for _ in range(4):  # retry-on-empty
            out = ub.clean_zh_output(" ".join(translate_piece(p) for p in pieces))
            if out:
                break
        return out

    return translate_para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocr", action="store_true", help="續跑 Vision OCR")
    ap.add_argument("--limit", type=int, default=0, help="這一輪最多跑幾批")
    ap.add_argument("--redo", type=int, nargs="*", default=None,
                    help="重跑指定的批（批的起始掃描頁）；不給值就重跑所有沒過閘門的批")
    ap.add_argument("--gates", action="store_true", help="只檢查每一批有沒有過閘門")
    ap.add_argument("--dry", action="store_true", help="看目前切出來的章節")
    args = ap.parse_args()

    if args.gates or args.redo == []:
        bad = failed_batches()
        print(f"沒過閘門的批：{len(bad)}")
        for lo, why in bad:
            print(f"  b{lo:04d}（掃描頁 {lo}–{min(lo + BATCH - 1, 472)}）：{why}")
        if args.gates:
            return

    if args.ocr or args.redo is not None:
        redo = args.redo if args.redo else [lo for lo, _why in failed_batches()]
        run_ocr(limit=args.limit, redo=redo if args.redo is not None else None)
        return

    pages = load_ocr_pages()
    units, spec, report = build_units(pages)
    secs = split_sections(units)
    body = [u for u in units if u["kind"] == "body"]
    notes = [u for u in units if u["kind"] == "note"]
    withpg = sum(1 for u in units if u["page"])
    print(f"OCR 頁 {len(pages)}（重複丟掉 {len(report['dup_pages'])}）／正文段 {len(body)}／"
          f"註腳 {len(notes)}／有頁碼 {withpg} ({withpg / max(1, len(units)):.0%})／"
          f"章節 {len(secs)}")
    print(f"目次丟掉 {report['toc_units']} 則／後附索引丟掉 {report['back_units']} 則")
    if args.dry:
        if report["dup_pages"]:
            print("  重複掃描頁：" + "、".join(f"scan{p}" for p in report["dup_pages"]))
        for line in report["restored"]:
            print(f"  補回：{line}")
        for i, s in enumerate(secs):
            print(f"  sec{i:2} 「{s['heading'][:60]}」 ¶={len(s['paras']):4} "
                  f"p{s['pages'][0]}–{s['pages'][-1]}")
        print("\n目次對帳（目次宣告 vs 切出來的章節）：")
        for row in check_structure(secs, spec):
            print("  " + row)


if __name__ == "__main__":
    main()
