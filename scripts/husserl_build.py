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

  python scripts/husserl_build.py --ocr            # 續跑 OCR（可重複執行）
  python scripts/husserl_build.py --ocr --limit 5  # 只跑五批
  python scripts/husserl_build.py --dry            # 看切出來的章節與段落
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
from archive_djvu import fill_folios  # noqa: E402

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


def batches(total: int, size: int = BATCH) -> list[tuple[int, int]]:
    """(start, end) 逐批，1-based、含端點。"""
    return [(s, min(s + size - 1, total)) for s in range(1, total + 1, size)]


def batch_path(lo: int) -> Path:
    return OCR_DIR / f"b{lo:04d}.json"


def run_ocr(slug: str = "husserl-ideas-i", limit: int = 0) -> int:
    """續跑 Vision OCR，回傳這一輪新完成的批數。已有快取的批直接跳過。"""
    import ocr_pdf_to_text as o

    OCR_DIR.mkdir(parents=True, exist_ok=True)
    total = REGISTRY[slug]["pdf_pages"]
    todo = [(lo, hi) for lo, hi in batches(total) if not batch_path(lo).exists()]
    print(f"OCR {slug}：共 {len(batches(total))} 批，待跑 {len(todo)} 批", flush=True)
    done = 0
    for lo, hi in todo:
        if limit and done >= limit:
            break
        pages, broken = None, False
        for attempt, prompt in enumerate((OCR_PROMPT, OCR_PROMPT_STRICT), 1):
            try:
                pages = o.ocr_pdf(PDF_PATH, model=OCR_MODEL, pages=(lo, hi), prompt=prompt)
            except Exception as e:  # noqa: BLE001
                print(f"  ✗ pp{lo}-{hi} 停在：{str(e)[:120]}", flush=True)
                pages = None
                break
            units = [u for p in pages for u in parse_page(p.get("text") or "")[1]]
            broken = looks_line_broken(units)
            if not broken:
                break
            print(f"  ⚠ pp{lo}-{hi} 一行一段，重跑（第 {attempt} 次）", flush=True)
        if pages is None:
            break
        payload = {"pages": pages, "gate": "line-broken" if broken else "ok"}
        batch_path(lo).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        got = sum(1 for p in pages if (p.get("text") or "").strip())
        done += 1
        flag = "  ⚠ 仍一行一段" if broken else ""
        print(f"  ✓ pp{lo}-{hi}  {got}/{hi - lo + 1} 頁有內容{flag}", flush=True)
    left = sum(1 for lo, _hi in batches(total) if not batch_path(lo).exists())
    print(f"本輪完成 {done} 批，尚餘 {left} 批", flush=True)
    return done


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


# ── 頁碼／註腳／段落（純函式，測試在 scripts/tests/test_husserl_build.py）─────

_FOLIO_RE = re.compile(r"^\s*\[\[p\s*([0-9]+|\?)\s*\]\]\s*", re.M)
_NOTE_PREFIX = "[note]"
# 「experi- ence」這種殘留的行末斷詞。真正該留的連字號後面不會有空白
# （temporo-spatial、self-evidence），所以「小寫字母 + 連字號 + 空白 + 小寫字母」
# 是很乾淨的判準。
_SOFT_HYPHEN = re.compile(r"([a-zäöüß])-\s+([a-zäöüß])")


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
        line = _SOFT_HYPHEN.sub(r"\1\2", raw.strip())
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
    folios = fill_folios([f for f, _u in parsed])
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


def split_sections(units: list[dict]) -> list[dict]:
    """units → [{heading, paras, pages}]。章界＝章級標題；§ 小節標題留在正文裡
    當一行（reader 會照排），不另外切段——否則段落數會爆掉。"""
    secs: list[dict] = []
    cur = {"heading": "", "paras": [], "pages": []}
    for u in units:
        m = _HEADING.match(u["text"])
        title = m.group(1) if m else None
        if title and is_chapter_head(title):
            if cur["paras"]:
                secs.append(cur)
            cur = {"heading": title, "paras": [], "pages": []}
            continue
        cur["paras"].append(u["text"])
        cur["pages"].append(u["page"])
    if cur["paras"]:
        secs.append(cur)
    return secs


def load_work_sections(slug: str = "husserl-ideas-i") -> list[dict]:
    secs = split_sections(paged_units(load_ocr_pages(slug)))
    for i, s in enumerate(secs):
        s.setdefault("title_zh", s["heading"] or f"第 {i + 1} 節")
    return secs


# ── 翻譯 ─────────────────────────────────────────────────────────────────────

HUSSERL_PROMPT_TMPL = """你是現象學的專業譯者，正在翻譯胡塞爾《觀念一》（Ideen I）的 Boyce Gibson 英譯本。把下列英文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
1b. **西元年份一律用阿拉伯數字**：一八九三年→**1893 年**、一九二〇年代→**1920 年代**。🚨 年號紀年照漢數字不可改（明治二十四年、大正十二年），數量與序數也不改（三十年、第三章、二十世紀）。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。
3. 語域：哲學論著的說理散文。胡塞爾句子長、子句層層相扣，中譯要斷得開、讀得懂，但**不可拆掉論證的層次**，也不可把他的保留語氣（「就其本質而言」「原則上」「在某種意義下」）簡化掉。
4. `## ` 開頭的是標題，照留 `## `；以「§」起頭的小節標題同樣照留。
5. 🚨 **希臘文與德文原詞一律原樣保留，不要翻、不要轉寫**（ἐποχή、εἶδος、νόησις、νόημα、ὕλη、Wesen、Erlebnis、Bewußtsein）。首次出現可在其後加括號中譯，其餘照留原詞。
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
    ap.add_argument("--dry", action="store_true", help="看目前切出來的章節")
    args = ap.parse_args()

    if args.ocr:
        run_ocr(limit=args.limit)
        return

    pages = load_ocr_pages()
    units = paged_units(pages)
    secs = split_sections(units)
    body = [u for u in units if u["kind"] == "body"]
    notes = [u for u in units if u["kind"] == "note"]
    withpg = sum(1 for u in units if u["page"])
    print(f"OCR 頁 {len(pages)}／正文段 {len(body)}／註腳 {len(notes)}／"
          f"有頁碼 {withpg} ({withpg / max(1, len(units)):.0%})／章節 {len(secs)}")
    if args.dry:
        for i, s in enumerate(secs):
            print(f"  sec{i:2} 「{s['heading'][:60]}」 ¶={len(s['paras']):4} "
                  f"p{s['pages'][0]}–{s['pages'][-1]}")


if __name__ == "__main__":
    main()
