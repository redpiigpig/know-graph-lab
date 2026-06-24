"""Ingest The Gnostic Society Library (gnosis.org) → gnostic_{documents,sections}.

Pipeline (see .claude/skills/scripture-gnostic/SKILL.md):
  fetch category index → parse_category_index → (dedup) → fetch each doc →
  parse_document → translate each EN paragraph → assert_aligned → upsert.

gnosis.org's HTTPS cert is expired, so we fetch with verify=False (insecure).
English is public-domain (Mead etc.); Chinese is our per-paragraph translation.
EN↔ZH align by order_index (one ZH paragraph per EN paragraph — the gate).

Examples:
  # one document
  python -X utf8 scripts/ingest_gnostic.py --category nag_hammadi \
      --url http://gnosis.org/naghamm/gosthom.html --title "The Gospel of Thomas" --engine gemini
  # whole category (lists docs; --limit-docs to cap; dedup auto for polemics/cac/dss)
  python -X utf8 scripts/ingest_gnostic.py --category hermetica --limit-docs 3 --engine gemini
  # just list a category's docs, translate nothing
  python -X utf8 scripts/ingest_gnostic.py --category nag_hammadi --list
"""
from __future__ import annotations
import os, sys, json, re, argparse, time
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gnostic_library as gl  # noqa: E402

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
PROJECT_REF = SUPABASE_URL.split("//")[1].split(".")[0]
ACCESS_TOKEN = os.environ["SUPABASE_ACCESS_TOKEN"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

MGMT_QUERY = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
H_MGMT = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
H_REST = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
          "Content-Type": "application/json", "Prefer": "return=minimal"}

GNOSTIC_PROMPT_TMPL = """你是諾斯底主義、赫密士、摩尼教等古典宗教文獻的專業譯者。
把以下文本翻成**繁體中文**（台灣用語、中間點用「‧」）。

要求：
1. **一律用白話文（現代漢語），語氣參照《和合本》聖經**——莊重、典雅、有神聖文體
   感，但**絕對不可用文言文**：不要「曰／其／之／乃／又聞昔有／二者不忍」這類古文
   句式與虛字。用和合本式的白話（如「耶穌說」「看哪」「他們就」「於是」）。忠實、
   可讀，保留原文語氣。
2. 專有名詞**務必照下表鎖定譯名**（首次出現可括註原文）：
   靈知 gnosis｜普累若麻 Pleroma｜移涌 Aeon｜流溢 emanation｜巨匠造物主 Demiurge｜
   執政者 Archon｜太一 Monad｜深淵 Bythos｜沉默 Sige｜努斯 Nous｜邏各斯 Logos｜
   配偶 syzygy｜界限 Horos｜索菲亞 Sophia｜阿卡摩特 Achamoth｜雅達巴沃 Yaldabaoth｜
   薩邁爾 Samael｜薩克拉斯 Saklas｜巴貝洛 Barbelo｜阿布拉克薩斯 Abraxas｜自生者 Autogenes｜
   塞特 Seth｜塞特派 Sethian｜瓦倫廷派 Valentinian｜俄斐特派 Ophite｜
   赫密士 Hermes｜三重至偉的赫密士 Hermes Trismegistus｜牧人者 Poimandres｜
   阿斯克勒庇俄斯 Asclepius｜密特拉 Mithra
   人名一律照權威譯名：耶穌 Jesus/Yeshua（不寫耶書亞／耶舒亞）｜多馬 Thomas｜
   馬利亞 Mary｜安得烈 Andrew｜腓力 Philip｜彼得 Peter｜約翰 John｜保羅 Paul｜
   司提反 Stephen｜西門 Simon｜馬吉安 Marcion｜革利免 Clement｜瓦倫廷 Valentinus｜
   巴西理德 Basilides｜摩尼 Mani／Manichaeus｜愛任紐 Irenaeus｜特土良 Tertullian。
3. **只輸出譯文本身**，不要任何前言、編號、道歉、拒絕、語言判斷、譯註，也不要
   「以下是」「以下為」「原文：」「翻譯：」「逐字翻譯」「我無法」「我注意到」
   「您提供的」「建議保留／譯為」這類字樣。不要逐字加註英文（如「光（Light）」）。
4. **若輸入是標題、章節名、簡短標籤或殘缺片段，只翻譯它本身，絕不可增補、擴寫、
   或自行創作任何句子或段落。** 內容多寡必須與原文相當，嚴禁無中生有。
5. 若原文不是英文（拉丁文、希臘文、奧克語、古普羅旺斯語等），同樣直接翻成繁體中文，
   不要說明原文是何種語言，也不要拒絕。

{source}"""


# ── Fetch (insecure — gnosis.org cert expired) ───────────────────────────────
def fetch(url: str, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, timeout=60, verify=False,
                             headers={"User-Agent": "Mozilla/5.0 (KGL gnostic ingest)"})
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


# ── Dedup: existing English titles already on the site ───────────────────────
def existing_en_titles() -> list[str]:
    """apocrypha_documents.title_en + gnostic_documents.title_en — the corpus we
    don't want to re-transcribe (per user: skip polemics/cac/dss overlaps)."""
    titles: list[str] = []
    for tbl in ("apocrypha_documents", "gnostic_documents"):
        r = requests.post(MGMT_QUERY, headers=H_MGMT,
                          json={"query": f"SELECT title_en FROM {tbl}"})
        if r.ok:
            titles += [row["title_en"] for row in r.json() if row.get("title_en")]
    return titles


# ── Translate (one call per paragraph → guaranteed 1:1 alignment) ────────────
def make_engine(engine: str):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = GNOSTIC_PROMPT_TMPL
    # 本工具預設 Gemini → NVIDIA fallback（per-tool 選擇，與全域 NVIDIA-first 不同；
    # Haiku 2026-06-04 已復活為全域第三層救急，但此 ingest 鏈未納入）。
    fn = {
        "gemini": te.gemini_with_nvidia_fallback,
        "nvidia": te.nvidia_translate,
        "sonnet": te.sonnet_translate,
        # Direct Haiku via Claude Max OAuth — use when the free pools (Gemini /
        # NVIDIA) are dry or busy and we'd rather burn Max quota than idle
        # (user 2026-06-05: 「免費的沒有或被佔用了，就去開 Haiku，我有訂閱 max」).
        "haiku": te.haiku_translate,
    }[engine]
    return te, fn


# Curated Chinese titles for well-known Gnostic / Hermetic works — higher quality
# than LLM for proper names. Unknown titles fall back to engine translation.
TITLE_ZH: dict[str, str] = {
    # ── Corpus Hermeticum (Mead) ──
    "Poemandres, the Shepherd of Men": "牧人者（人類的牧者）",
    "The Secret Sermon on the Mountain": "山上密訓",
    "The Gnosis of the Mind": "心智的靈知",
    "Commentary on the Pymander": "《牧人者》註釋",
    "An Introduction to G.R.S. Mead's translation of the Corpus Hermeticum": "G.R.S. 米德《赫密士文集》譯本導論",
    "On the Trail of the Winged God: Hermes and Hermeticism Throughout the Ages": "循翼神之蹤：赫密士與歷代赫密士主義",
    "To Asclepius": "致阿斯克勒庇俄斯",
    "The Sacred Sermon": "神聖講道",
    "The Cup or Monad": "聖杯，或太一",
    "Though Unmanifest God Is Most Manifest": "神雖未顯，卻最為彰顯",
    "In God Alone Is Good And Elsewhere Nowhere": "善唯在神，他處皆無",
    "The Greatest Ill Among Men is Ignorance of God": "人間至惡乃不識神",
    "That No One of Existing Things doth Perish": "存在之物無一消亡",
    "On Thought and Sense": "論思維與感覺",
    "The Key": "鑰匙",
    "Mind Unto Hermes": "心智致赫密士",
    "About the Common Mind": "論共通心智",
    "A Letter of Thrice-Greatest Hermes to Asclepius": "三重至偉的赫密士致阿斯克勒庇俄斯書",
    "The Definitions of Asclepius unto King Ammon": "阿斯克勒庇俄斯致阿蒙王的定義",
    "Of Asclepius to the King": "阿斯克勒庇俄斯致王書",
    "The Encomium of Kings": "諸王頌",
    "The Perfect Sermon (The Asclepius)": "完美講道（阿斯克勒庇俄斯篇）",
    "The Hymns of Hermes": "赫密士頌歌",
    "Asclepius (21-29)": "阿斯克勒庇俄斯篇（21–29）",
    "The Discourse on the Eighth and Ninth": "論第八與第九重天",
    "Prayer of Thanksgiving": "感恩禱文",
    "Text": "赫密士文集正文",
    # ── Nag Hammadi / Gnostic adjacents ──
    "The Authoritative Teaching": "權威教訓",
    "The Thunder, Perfect Mind": "雷霆，完全的心智",
    "The Acts of Peter and the Twelve Apostles": "彼得與十二使徒行傳",
    "The Gospel of Thomas": "多馬福音",
    "The Gospel of Philip": "腓力福音",
    "The Gospel of Truth": "真理福音",
    "The Gospel of Mary": "馬利亞福音",
    "The Apocryphon of John": "約翰密傳",
    "The Hypostasis of the Archons": "執政者的本質",
    "On the Origin of the World": "論世界起源",
    "The Sophia of Jesus Christ": "耶穌基督的智慧",
    "Pistis Sophia": "皮斯蒂斯‧索菲亞（信仰‧智慧）",
    # ── Mead collection ──
    "Brief Introduction": "簡短導論",
    "The Hymn of Jesus": "耶穌之頌歌",
    "The Hymn of the Robe of Glory": "榮耀之袍頌歌（珍珠之歌）",
    "Apollonius of Tyana": "提亞納的阿波羅尼烏斯",
    "Fragments of a Faith Forgotten": "被遺忘信仰的殘篇",
    "The Mysteries of Mithra": "密特拉密儀",
}

# Page / citation markers and number-only fragments must NOT be sent to the LLM —
# deepseek hallucinates plausible Gnostic prose for a bare "p. 126". Keep them
# verbatim instead (language-neutral citations).
# `page\b` not bare `page`: the citation marker is always a whole word — bare
# `page` false-matched prose starting "Pagels…" (Elaine Pagels, the prominent
# gnostic scholar) and skipped real content as if it were a page reference.
_TRIVIAL_RE = re.compile(r"^\(?\s*(text\s*:|p{1,2}\.|pp\.|page\b|pat\.|cf\.|\d+\s*[-–]\s*\d+)", re.I)


def is_trivial_source(s: str) -> bool:
    s = (s or "").strip()
    if len(s) < 4:
        return True
    if _TRIVIAL_RE.match(s):
        return True
    return sum(c.isalpha() and c.isascii() for c in s) < 3  # mostly digits/punct/roman


# Seconds to sleep between paragraph calls, to keep the single free NVIDIA key
# under its rate limit (set via --pace; 0 = full speed).
PACE = 0.0


def translate_title(title_en: str, te, engine_fn) -> str:
    """Chinese title: curated map first, else a short engine translation."""
    if title_en in TITLE_ZH:
        return TITLE_ZH[title_en]
    if te is None or engine_fn is None:
        return title_en
    prev = te.PROMPT_TMPL
    te.PROMPT_TMPL = ("把以下諾斯底／赫密士文獻的英文篇名翻成簡潔的繁體中文書名，"
                      "只輸出中文書名本身，不要引號、標點或說明：\n\n{source}")
    try:
        zh = engine_fn(title_en).strip().strip("「」\"'。 ")
        return zh or title_en
    finally:
        te.PROMPT_TMPL = prev


GATE_RETRIES = 2  # extra attempts when a paragraph fails the quality gate


def translate_one(p: str, te, engine_fn) -> tuple[str, str | None]:
    """Translate one paragraph THROUGH the quality gate (gl.classify_translation).

    This is the SOURCE↔OUTPUT invariant that assert_aligned (count-only) misses:
    it catches a short heading hallucinated into a fabricated essay, untranslated
    English, engine meta-commentary, and word-by-word gloss — AT translation time.
    On failure it retries, then for short structural markers (refs/headings) falls
    back to the verbatim source (language-neutral, beats a fabrication).
    Returns (zh, status) where status is None on a clean pass.
    """
    pieces = te.split_oversized(p)
    last, tag = "", None
    for _ in range(GATE_RETRIES + 1):
        last = "\n\n".join(engine_fn(piece) for piece in pieces).strip()
        tag = gl.classify_translation(p, last)
        if tag is None:
            return last, None
    if len(p.strip()) <= 80:                  # structural marker → keep verbatim
        return p.strip(), f"{tag}→verbatim"
    return last, tag                          # keep best effort, surface the tag


def translate_paragraphs(paragraphs: list[str], te, engine_fn, limit: int | None = None) -> list[str]:
    todo = paragraphs[:limit] if limit else paragraphs
    out: list[str] = []
    for i, p in enumerate(todo):
        if is_trivial_source(p):       # page/citation markers → keep verbatim, no LLM
            out.append(p.strip())
            print(f"    · para {i + 1}/{len(todo)} (trivial, kept)", flush=True)
            continue
        if PACE and i > 0:
            time.sleep(PACE)
        zh, status = translate_one(p, te, engine_fn)
        out.append(zh)
        note = f" ⚠ {status}" if status else ""
        print(f"    · para {i + 1}/{len(todo)} ({len(p)}→{len(zh)} chars){note}", flush=True)
    return out


# ── Upsert ───────────────────────────────────────────────────────────────────
def upsert_document(meta: dict) -> None:
    requests.post(f"{SUPABASE_URL}/rest/v1/gnostic_documents",
                  headers={**H_REST, "Prefer": "resolution=merge-duplicates"},
                  data=json.dumps([meta]), timeout=60).raise_for_status()


def replace_sections(slug: str, rows: list[dict]) -> int:
    requests.delete(f"{SUPABASE_URL}/rest/v1/gnostic_sections?doc_slug=eq.{slug}",
                    headers=H_REST, timeout=60)
    BATCH = 100
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        for attempt in range(3):
            r = requests.post(f"{SUPABASE_URL}/rest/v1/gnostic_sections",
                              headers=H_REST, data=json.dumps(batch), timeout=180)
            if r.status_code in (200, 201, 204):
                break
            if r.status_code >= 500 and attempt < 2:
                time.sleep(2 * (attempt + 1)); continue
            print(f"  ERROR batch {i}: {r.status_code} {r.text[:300]}"); r.raise_for_status()
    return len(rows)


def ingest_doc(category: str, title: str, url: str, te, engine_fn, *,
               display_order: int = 0, limit_paras: int | None = None,
               dry_run: bool = False) -> dict | None:
    print(f"  → {title}  ({url})", flush=True)
    parsed = gl.parse_document(fetch(url))
    en = parsed["sections"]
    if not en:
        print("    ⚠ no sections parsed — skip"); return None
    title = title or parsed["title"] or "Untitled"
    slug = gl.make_slug(title)
    print(f"    slug={slug}  EN paras={len(en)}", flush=True)
    if dry_run:
        return {"slug": slug, "title_en": title, "en_paras": len(en)}

    zh = translate_paragraphs(en, te, engine_fn, limit=limit_paras)
    en_used = en[:len(zh)]
    gl.assert_aligned(en_used, zh)

    title_zh = translate_title(title, te, engine_fn)
    upsert_document({
        "slug": slug, "title_zh": title_zh, "title_en": title, "category": category,
        "source_url": url, "display_order": display_order,
    })
    rows = []
    for i, (e, c) in enumerate(zip(en_used, zh)):
        rows.append({"doc_slug": slug, "version_code": "gnosis_en", "order_index": i, "text": e, "char_count": len(e)})
        rows.append({"doc_slug": slug, "version_code": "zh", "order_index": i, "text": c, "char_count": len(c)})
    n = replace_sections(slug, rows)
    print(f"    ✓ upserted {n} section rows ({len(zh)} paras × 2 versions)", flush=True)
    return {"slug": slug, "title_en": title, "paras": len(zh)}


# Overnight order: public-domain-clean categories first (Mead/Hermetica),
# then core Gnostic, then related religions, then dedup/peripheral last.
ALL_ORDER = ["hermetica", "mead", "gnostic_scriptures", "nag_hammadi", "valentinus",
             "manichaean", "mandaean", "cathar", "alchemical", "modern",
             "polemics", "christian_apocrypha", "dead_sea"]
CONSEC_FAIL_ABORT = 4  # stop the whole run after this many docs fail in a row (quota dead)


def done_slugs() -> set[str]:
    """Doc slugs that already have ZH sections (for --resume skip)."""
    r = requests.post(MGMT_QUERY, headers=H_MGMT, json={
        "query": "SELECT DISTINCT doc_slug FROM gnostic_sections WHERE version_code = 'zh'"})
    return {row["doc_slug"] for row in r.json()} if r.ok else set()


def process_category(key: str, te, engine_fn, *, resume: bool, done: set[str],
                     state: dict, limit_docs=None, limit_paras=None, dry_run=False) -> None:
    cat = gl.CATEGORY_BY_KEY[key]
    docs = gl.parse_category_index(fetch(gl.GNOSIS_ROOT + cat["index_path"]),
                                   base_path=cat["index_path"])
    if cat["dedup_against_existing"]:
        existing = existing_en_titles()
        before = len(docs)
        docs = [d for d in docs if not gl.is_duplicate(d["title"], existing)]
        print(f"[{key}] dedup: {before} → {len(docs)}", flush=True)
    if limit_docs:
        docs = docs[:limit_docs]
    print(f"=== {cat['label_zh']} ({key}): {len(docs)} docs ===", flush=True)
    for i, d in enumerate(docs):
        slug = gl.make_slug(d["title"])
        if resume and slug in done:
            print(f"  ⏭ skip (done): {d['title']}", flush=True)
            continue
        try:
            res = ingest_doc(key, d["title"], d["url"], te, engine_fn,
                             display_order=cat["display_order"] * 100 + i,
                             limit_paras=limit_paras, dry_run=dry_run)
            if res:
                done.add(res["slug"])
            state["consec_fail"] = 0
        except Exception as e:  # noqa: BLE001
            state["consec_fail"] += 1
            print(f"  ✗ FAIL {d['title']}: {e}  (consec={state['consec_fail']})", flush=True)
            if state["consec_fail"] >= CONSEC_FAIL_ABORT:
                raise SystemExit(f"aborting: {CONSEC_FAIL_ABORT} consecutive failures "
                                 "(quota likely exhausted) — re-run with --resume later")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", help="CATEGORIES key, e.g. nag_hammadi")
    ap.add_argument("--all", action="store_true", help="iterate every category (overnight)")
    ap.add_argument("--url", help="single document URL")
    ap.add_argument("--title", default="", help="document title (overrides parsed)")
    ap.add_argument("--list", action="store_true", help="list category docs and exit")
    ap.add_argument("--engine", default="gemini", choices=["gemini", "nvidia", "sonnet", "haiku"])
    ap.add_argument("--resume", action="store_true", help="skip docs already in DB")
    ap.add_argument("--limit-docs", type=int, default=None)
    ap.add_argument("--limit-paras", type=int, default=None, help="cap paragraphs per doc (pilot)")
    ap.add_argument("--pace", type=float, default=0.0, help="seconds to sleep between paragraphs (rate-limit pacing)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    global PACE
    PACE = args.pace

    # ── Overnight: every category ────────────────────────────────────────────
    if args.all:
        te, engine_fn = make_engine(args.engine)
        done = done_slugs() if args.resume else set()
        state = {"consec_fail": 0}
        print(f"OVERNIGHT run · resume={args.resume} · {len(done)} docs already done", flush=True)
        for key in ALL_ORDER:
            try:
                process_category(key, te, engine_fn, resume=args.resume, done=done,
                                 state=state, limit_docs=args.limit_docs,
                                 limit_paras=args.limit_paras, dry_run=args.dry_run)
            except SystemExit as e:
                print(str(e), flush=True); break
        print(f"OVERNIGHT done · {len(done)} docs total in DB", flush=True)
        return

    if not args.category:
        sys.exit("need --category KEY or --all")
    cat = gl.CATEGORY_BY_KEY.get(args.category)
    if not cat:
        sys.exit(f"unknown category {args.category}; valid: {list(gl.CATEGORY_BY_KEY)}")

    # List / whole-category mode → resolve doc links from the index page.
    if args.list or not args.url:
        if args.list:
            docs = gl.parse_category_index(fetch(gl.GNOSIS_ROOT + cat["index_path"]),
                                           base_path=cat["index_path"])
            if cat["dedup_against_existing"]:
                existing = existing_en_titles()
                docs = [d for d in docs if not gl.is_duplicate(d["title"], existing)]
            print(f"{cat['label_zh']} ({args.category}): {len(docs)} docs")
            for d in docs:
                print(f"  - {d['title']}  {d['url']}")
            return
        te, engine_fn = make_engine(args.engine)
        done = done_slugs() if args.resume else set()
        process_category(args.category, te, engine_fn, resume=args.resume, done=done,
                         state={"consec_fail": 0}, limit_docs=args.limit_docs,
                         limit_paras=args.limit_paras, dry_run=args.dry_run)
        return

    # Single-document mode
    te, engine_fn = make_engine(args.engine) if not args.dry_run else (None, None)
    ingest_doc(args.category, args.title, args.url, te, engine_fn,
               display_order=cat["display_order"] * 100,
               limit_paras=args.limit_paras, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
