#!/usr/bin/env python3
"""東方聖書（Sacred Books of the East）逐卷英→繁中轉錄 driver.

The 50-volume SBE is a separate corpus from Müller's own works (it lives in the
/sacred-books-east portal, store: stores/sacredBooksEast.ts), so it keeps its own
registry instead of polluting mueller_auto.WORKS. It otherwise reuses the whole
Müller pipeline: ingest_work / translate_work / assemble_and_upload / sync_previews
(now author-overridable) and the Haiku engine from mueller_haiku_pass.

Each volume is its own dict with an `author`/`author_en` of the actual translator
(Müller, Legge, Bühler, …), an archive.org `en_id` with a real `_djvu.txt`, and a
coarse split. ebook_id namespace: 555555NN-… where NN = volume number.

Usage:
  python scripts/sbe_translate.py --list
  python scripts/sbe_translate.py --ingest <slug>          # English-first, no LLM
  python scripts/sbe_translate.py --loop --only <slug>     # translate to done (resumable)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mueller_build as mb  # noqa: E402  (loads .env, glossary prompt)
import mueller_auto as ma  # noqa: E402
import translate_ebook_to_zh as te  # noqa: E402

# ── SBE registry — one dict per volume (vol 1 first; add the rest as sourced) ──
WORKS = [
    dict(slug="sbe-01-upanishads-1", eid="55555501-5555-4555-8555-555555555555",
         title="奧義書（上）", title_en="The Upanishads, Part I (Sacred Books of the East, Vol. 1)",
         year=1879, category="世界宗教", subcategory="東方聖書",
         author="弗里德里希‧馬克斯‧穆勒（譯）", author_en="F. Max Müller (trans.)",
         parent="東方聖書", en_id="upanishads01mluoft", de_id=None, split="coarse"),
    # ── 各傳統代表卷（驗證分組瀏覽，2026-06-12）──
    dict(slug="sbe-04-zend-avesta-1", eid="55555504-5555-4555-8555-555555555555",
         title="阿維斯陀（一）：祓魔法典", title_en="The Zend-Avesta, Part I — The Vendîdâd (Sacred Books of the East, Vol. 4)",
         year=1880, category="世界宗教", subcategory="東方聖書",
         author="達梅斯特（譯）", author_en="James Darmesteter (trans.)",
         parent="東方聖書", en_id="zendavesta00darmgoog", de_id=None, split="coarse"),
    dict(slug="sbe-06-quran-1", eid="55555506-5555-4555-8555-555555555555",
         title="古蘭經（上）", title_en="The Qur'ân, Part I (Sacred Books of the East, Vol. 6)",
         year=1880, category="世界宗教", subcategory="東方聖書",
         author="帕爾默（譯）", author_en="E. H. Palmer (trans.)",
         parent="東方聖書", en_id="mlbd.koransacredbooks0000unse_w1m9", de_id=None, split="coarse"),
    dict(slug="sbe-10-dhammapada", eid="55555510-5555-4555-8555-555555555555",
         title="法句經／經集", title_en="The Dhammapada and Sutta-Nipâta (Sacred Books of the East, Vol. 10)",
         year=1881, category="世界宗教", subcategory="東方聖書",
         author="穆勒、法斯伯爾（譯）", author_en="F. Max Müller & V. Fausböll (trans.)",
         parent="東方聖書", en_id="mlbd.dhammapadasuttni0000fmax", de_id=None, split="coarse"),
    dict(slug="sbe-16-yi-king", eid="55555516-5555-4555-8555-555555555555",
         title="儒家經籍（二）：易經", title_en="The Texts of Confucianism, Part II — The Yî King (Sacred Books of the East, Vol. 16)",
         year=1882, category="世界宗教", subcategory="東方聖書",
         author="理雅各（譯）", author_en="James Legge (trans.)",
         parent="東方聖書", en_id="sacredbooksofchi16conf", de_id=None, split="coarse"),
    dict(slug="sbe-22-jaina-1", eid="55555522-5555-4555-8555-555555555555",
         title="耆那教經典（一）", title_en="Jaina Sûtras, Part I — Âkârânga & Kalpa Sûtra (Sacred Books of the East, Vol. 22)",
         year=1884, category="世界宗教", subcategory="東方聖書",
         author="雅各比（譯）", author_en="Hermann Jacobi (trans.)",
         parent="東方聖書", en_id="mlbd.jainasutraspt1tr00vol-22.unse_m8x0", de_id=None, split="coarse"),
]


# slug → tradition (selects the glossary cheat-sheet injected into the prompt)
TRADITION = {
    "sbe-01-upanishads-1": "veda", "sbe-04-zend-avesta-1": "zoroastrian",
    "sbe-06-quran-1": "islam", "sbe-10-dhammapada": "buddhism",
    "sbe-16-yi-king": "china", "sbe-22-jaina-1": "jainism",
}

# Generic Sacred-Books-of-the-East translator prompt (the Müller one wrongly
# claims it is translating 《宗教學導論》). {glossary} is filled per-tradition.
SBE_PROMPT_TMPL = """你是世界宗教經典的專業譯者，正在翻譯馬克斯‧穆勒主編《東方聖書》(Sacred Books of the East) 中的一卷。把下列**英文原文**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；台灣用語；中間點用「‧」。
2. 忠實學術／經典語氣，長句順為通順中文；保留括號內的外文夾注（梵文/巴利文/阿拉伯文/中文原典等）。
3. 保留 Markdown（## 標題 / **粗體** / *斜體* / > 引文）。
4. 專名術語鎖定下列對照（英文轉寫→繁中），出現時務必沿用：
{glossary}
5. 只輸出翻譯後的繁體中文，不要前言、說明或英文。

英文原文：
{source}"""

_CHEATSHEET_CACHE: dict[str, str] = {}


def tradition_glossary(tradition: str) -> str:
    """Build a compact 'English→繁中' cheat-sheet for the prompt from the live
    /translation-glossary deities table. Buddhist volumes get the 119-term
    Buddhist set (religion=佛教); others get a short tradition-appropriate stub."""
    if tradition in _CHEATSHEET_CACHE:
        return _CHEATSHEET_CACHE[tradition]
    religion = {"buddhism": "佛教"}.get(tradition)
    lines: list[str] = []
    if religion:
        import requests
        url = (f"{te.URL}/rest/v1/deities?religion=eq.{religion}"
               "&select=name_english,name_recommended,name_variants&order=sort_order")
        try:
            rows = requests.get(url, headers=te.H_GET, timeout=30).json()
        except Exception:  # noqa: BLE001
            rows = []
        for r in rows:
            en = r.get("name_english") or ""
            rec = r.get("name_recommended") or ""
            # surface the romanized variant (e.g. Pali) so the model matches both
            var = r.get("name_variants") or ""
            alt = ""
            m = re.search(r"\(巴\)([A-Za-zāīūṃṅñṭḍṇśṣ\-]+)", var)
            if m:
                alt = f"/{m.group(1)}"
            if en and rec:
                lines.append(f"{en}{alt}→{rec}")
    if not lines:
        return "（無專屬術語表，依通行學界譯名與既有古譯）"
    out = "；".join(lines)
    _CHEATSHEET_CACHE[tradition] = out
    return out


def _sonnet_translator():
    """Sonnet translate fn. If a dedicated PAID key is set (ANTHROPIC_SONNET_API_KEY,
    or ANTHROPIC_API_KEY) it builds a separate client so Sonnet truly bypasses the
    Claude Max rolling-window limit that throttles the free Haiku tier; otherwise it
    falls back to Max-Sonnet (te.sonnet_translate), which shares the Max account."""
    key = os.environ.get("ANTHROPIC_SONNET_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return te.sonnet_translate
    client = te._anthropic.Anthropic(api_key=key)

    def sonnet_paid(p: str) -> str:
        msg = client.messages.create(
            model=te.SONNET_MODEL, max_tokens=16000,
            messages=[{"role": "user", "content": te.PROMPT_TMPL.format(source=p)}])
        return "".join(b.text for b in msg.content if hasattr(b, "text")).strip()

    return sonnet_paid


def make_sbe_engine(tradition: str, backend: str = "cloud"):
    """translate_para with the SBE prompt + this tradition's glossary.
    Engine policy: 免費層 Haiku（Claude Max）優先且**快速失敗**（短 backoff），一旦
    免費層不動（429/連線/空回）→ 立刻改用 Sonnet 轉錄（user 2026-06-14 拍板）。
    這同時根治「Haiku 在 429 backoff 裡睡 ~30 分鐘像當機」的停滯。"""
    te.PROMPT_TMPL = SBE_PROMPT_TMPL.replace("{glossary}", tradition_glossary(tradition))
    sonnet_one = _sonnet_translator()

    def _clean(out: str) -> str:
        out = re.sub(r"(?m)^\s*#{1,6}\s.*$", "", out)
        return re.sub(r"\s*\n\s*", " ", out).strip()

    def _join(fn, pieces) -> str:
        return _clean(" ".join(fn(p) for p in pieces))

    def translate_para(en: str, de: str = "") -> str:
        src = en.strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)
        if backend == "ollama":
            return _join(te.ollama_translate, pieces)
        if backend == "gemini-first":
            return _join(te.gemini_with_nvidia_fallback, pieces)
        if backend == "haiku":
            # Direct Haiku with patient backoffs (waits out Max's rolling-window
            # 429s) — no Sonnet fallback. Much steadier than 'cloud' when the whole
            # backlog runs on Max: matches panikkar's fast --backend haiku path.
            return _join(te.haiku_translate, pieces)
        # 1) 免費層 Haiku — 快速失敗（backoffs 0,20）：免費池不動就在 ~20s 內升級，
        #    不再像舊版那樣在 30 分鐘的 429 backoff 裡靜默卡死。
        try:
            for _ in range(2):  # retry-on-empty（非例外的空回）
                out = _join(lambda p: te._anthropic_translate(
                    te.HAIKU_MODEL, "Haiku", p, backoffs=(0, 20)), pieces)
                if out:
                    return out
        except Exception as e:  # noqa: BLE001
            print(f"    ⚠ 免費層 Haiku 不動（{type(e).__name__}）→ 改用 Sonnet", flush=True)
        # 2) 升級 Sonnet（有 paid key 則繞過 Max 限制）
        try:
            for _ in range(2):
                out = _join(sonnet_one, pieces)
                if out:
                    return out
        except Exception as e:  # noqa: BLE001
            print(f"    ⚠ Sonnet 亦失敗（{type(e).__name__}）", flush=True)
        return ""

    return translate_para


def run_local_draft_step(max_total_paras: int) -> int:
    """Translate a bounded SBE draft batch via Ollama; checkpoint only."""
    for work in WORKS:
        if ma.is_done(work):
            continue
        tradition = TRADITION.get(work["slug"], "")
        engine = make_sbe_engine(tradition, backend="ollama")
        translated = ma.translate_work(
            work, engine, reupload_every=0,
            max_total_paras=max_total_paras, engine_name="ollama")
        print(f"SUPERVISOR_RESULT job=sbe-local-draft slug={work['slug']} "
              f"translated={translated}", flush=True)
        return translated
    print("SUPERVISOR_RESULT job=sbe-local-draft all-done translated=0", flush=True)
    return 0


def run_review_step(max_total_paras: int, backend: str, do_upload: bool) -> int:
    for work in WORKS:
        if not ma.count_local_drafts(work):
            continue
        tradition = TRADITION.get(work["slug"], "")
        engine = make_sbe_engine(tradition, backend=backend)
        reviewed = ma.review_local_drafts(
            work, engine, engine_name=backend,
            max_total_paras=max_total_paras)
        remaining = ma.count_local_drafts(work)
        if do_upload and remaining == 0:
            ma.assemble_and_upload(work)
        print(f"SUPERVISOR_RESULT job=sbe-online-review slug={work['slug']} "
              f"reviewed={reviewed} remaining={remaining}", flush=True)
        return reviewed
    print("SUPERVISOR_RESULT job=sbe-online-review no-local-drafts reviewed=0", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--ingest", default="", help="slug — English-first ingest, no LLM")
    ap.add_argument("--only", default="", help="comma-separated slugs to translate")
    ap.add_argument("--loop", action="store_true", help="self-restart until in scope is_done")
    ap.add_argument("--local-draft-step", action="store_true",
                    help="bounded Ollama pass; checkpoint only, never upload")
    ap.add_argument("--review-local-step", action="store_true",
                    help="bounded online replacement of provenance=ollama")
    ap.add_argument("--backend", choices=["cloud", "gemini-first", "haiku"], default="gemini-first")
    ap.add_argument("--max-total-paras", type=int, default=3)
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--local-draft-status", action="store_true")
    args = ap.parse_args()

    by_slug = {w["slug"]: w for w in WORKS}

    if args.list:
        for w in WORKS:
            print(f"  [{'✓' if ma.is_done(w) else ' '}] {w['slug']:24s} {w['title']}  ({w['en_id']})")
        return
    if args.local_draft_status:
        for work in WORKS:
            print(f"{work['slug']}\tollama_drafts={ma.count_local_drafts(work)}")
        return
    if args.local_draft_step:
        run_local_draft_step(max(1, args.max_total_paras))
        return
    if args.review_local_step:
        run_review_step(max(1, args.max_total_paras), args.backend, args.upload)
        return

    if args.ingest:
        ma.ingest_work(by_slug[args.ingest])
        return

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    scope = [w for w in WORKS if not only or w["slug"] in only]

    def one_pass():
        for w in scope:
            if ma.is_done(w):
                print(f"  ✓ {w['slug']} done — skip", flush=True)
                continue
            trad = TRADITION.get(w["slug"], "")
            tp = make_sbe_engine(trad)  # per-volume prompt: tradition glossary injected
            print(f"▶ translate {w['slug']} — {w['title']} [{trad}]", flush=True)
            ma.ingest_work(w)  # idempotent; keeps English readable + cache fresh
            ma.translate_work(w, tp)
            ma.assemble_and_upload(w)

    while True:
        try:
            one_pass()
        except BaseException as e:  # noqa: BLE001  (survive engine deaths / token expiry)
            print(f"  ⚠ pass error: {type(e).__name__}: {e}", flush=True)
        if not args.loop or all(ma.is_done(w) for w in scope):
            break
    print("sbe done", flush=True)


if __name__ == "__main__":
    main()
