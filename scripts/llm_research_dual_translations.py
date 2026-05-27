"""Use Haiku 4.5 to research the Protestant / Catholic Chinese translation
of every glossary entry (theologians + theological_terms) and backfill
name_protestant / name_catholic_sgs (or zh_*) where empty.

Haiku has knowledge of standard 思高（Catholic）and 新教（Protestant）naming
conventions through its training; this script asks it per entry and
applies returned values. Confidence-gated — entries marked 'low' are
skipped to avoid polluting the DB with guesses.

Cost: 408 entries × ~$0.005 = ~$2. Time: 4 workers ~15-30 min.

Usage:
    python scripts/llm_research_dual_translations.py            # apply
    python scripts/llm_research_dual_translations.py --limit 10 # smoke
    python scripts/llm_research_dual_translations.py --dry-run  # no write
    python scripts/llm_research_dual_translations.py --overwrite # touch
                                                                # even rows
                                                                # that have
                                                                # values
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
from translate_ebook_to_zh import (  # noqa: E402
    HAIKU_MODEL, _refresh_anthropic_client_if_creds_changed,
)
import translate_ebook_to_zh as tezh  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

PERSON_PROMPT = """請給出此教父／神學家／聖經人物的中文譯名兩個版本。

英文／拉丁名: {english}
原文（若有）: {original}
時代分類: {era_zh}

回應**嚴格 JSON**，欄位：
- "protestant": 新教華語圈常見譯法（華聯／證主／校園／改革宗系統，台灣中華福音神學院、香港建道、改革宗等出版社）
- "catholic":   天主教華語圈常見譯法（思高聖經學會／光啟／輔大／聞道等出版社）
- "confidence": "high" / "medium" / "low"
- "note":       可選簡短說明（不確定處）

兩種譯法相同時兩欄填一樣。confidence=low 表示不熟悉此人，無法可靠給譯名。

只輸出 JSON，不要 markdown 圍欄、不要解說。
"""

TERM_PROMPT = """請給出此{kind_zh}的中文譯名兩個版本（新教 vs 天主教）。

英文: {english}
原文（若有）: {original}
類別: {kind_zh}

回應**嚴格 JSON**：
- "protestant": 新教華語圈常見譯法
- "catholic":   天主教華語圈常見譯法（思高／光啟系統）
- "confidence": "high" / "medium" / "low"
- "note":       可選簡短說明

兩種譯法相同時兩欄填一樣（許多現代神學名詞兩個傳統用同樣譯法）。

只輸出 JSON。
"""

ERA_LABELS = {
    "biblical": "聖經人物（新舊約時期）",
    "early": "初代教會（-638 教父／護教士）",
    "medieval": "中世紀教會（638-1517 經院神學）",
    "modern": "近代教會（1517-1910 宗改／覺醒）",
    "contemporary": "現代教會（1910+）",
}
ETYPE_LABELS = {
    "place": "地名",
    "work": "作品名／書名",
    "sect": "教派／異端派系",
    "term": "神學名詞／教義概念",
}


def fetch_all_entries() -> tuple[list[dict], list[dict]]:
    """Pull theologians + theological_terms; only the ones missing at
    least one translation slot are subject to research."""
    persons = requests.get(
        f"{URL}/rest/v1/theologians?select=id,name_english,name_original,name_protestant,name_catholic_sgs,person_era",
        headers=H_GET, timeout=60).json()
    terms = requests.get(
        f"{URL}/rest/v1/theological_terms?select=id,term_english,term_original,zh_protestant,zh_catholic_sgs,entity_type",
        headers=H_GET, timeout=60).json()
    return persons, terms


def llm_research_one(prompt: str) -> dict | None:
    """Single Haiku call; returns parsed dict or None on failure."""
    _refresh_anthropic_client_if_creds_changed()
    for attempt in range(3):
        try:
            msg = tezh._anthropic_client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```\s*$", "", text)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                m = re.search(r"\{[\s\S]*\}", text)
                if m:
                    return json.loads(m.group(0))
                return None
        except Exception as e:
            if attempt == 2:
                return {"error": str(e)}
            time.sleep(2 ** attempt * 3)
    return None


def research_person(p: dict, overwrite: bool) -> dict | None:
    if (p.get("name_protestant") and p.get("name_catholic_sgs")) and not overwrite:
        return None
    en = (p.get("name_english") or "").strip()
    if not en:
        return None
    prompt = PERSON_PROMPT.format(
        english=en,
        original=p.get("name_original") or "—",
        era_zh=ERA_LABELS.get(p.get("person_era") or "early", "—"),
    )
    res = llm_research_one(prompt)
    if not res or res.get("error"):
        return None
    if res.get("confidence") == "low":
        return None
    patch = {}
    if not p.get("name_protestant") or overwrite:
        v = (res.get("protestant") or "").strip()
        if v: patch["name_protestant"] = v
    if not p.get("name_catholic_sgs") or overwrite:
        v = (res.get("catholic") or "").strip()
        if v: patch["name_catholic_sgs"] = v
    return patch or None


def research_term(t: dict, overwrite: bool) -> dict | None:
    if (t.get("zh_protestant") and t.get("zh_catholic_sgs")) and not overwrite:
        return None
    en = (t.get("term_english") or "").strip()
    if not en:
        return None
    etype = t.get("entity_type") or "term"
    prompt = TERM_PROMPT.format(
        english=en,
        original=t.get("term_original") or "—",
        kind_zh=ETYPE_LABELS.get(etype, "神學名詞"),
    )
    res = llm_research_one(prompt)
    if not res or res.get("error"):
        return None
    if res.get("confidence") == "low":
        return None
    patch = {}
    if not t.get("zh_protestant") or overwrite:
        v = (res.get("protestant") or "").strip()
        if v: patch["zh_protestant"] = v
    if not t.get("zh_catholic_sgs") or overwrite:
        v = (res.get("catholic") or "").strip()
        if v: patch["zh_catholic_sgs"] = v
    return patch or None


def patch_person(pid: str, patch: dict) -> bool:
    r = requests.patch(f"{URL}/rest/v1/theologians?id=eq.{pid}",
                       headers=H_JSON, json=patch, timeout=30)
    return r.status_code in (200, 204)


def patch_term(tid: str, patch: dict) -> bool:
    r = requests.patch(f"{URL}/rest/v1/theological_terms?id=eq.{tid}",
                       headers=H_JSON, json=patch, timeout=30)
    return r.status_code in (200, 204)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true",
                    help="Touch rows that already have both translations.")
    ap.add_argument("--limit", type=int, default=None,
                    help="Cap entries to process (smoke test).")
    ap.add_argument("--only", choices=["persons", "terms"], default=None)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    persons, terms = fetch_all_entries()
    print(f"Loaded: {len(persons)} persons, {len(terms)} terms")

    # Pre-filter to ones that need research
    def needs_person(p):
        return args.overwrite or not (p.get("name_protestant") and p.get("name_catholic_sgs"))
    def needs_term(t):
        return args.overwrite or not (t.get("zh_protestant") and t.get("zh_catholic_sgs"))
    persons_todo = [p for p in persons if needs_person(p)]
    terms_todo = [t for t in terms if needs_term(t)]
    if args.limit:
        persons_todo = persons_todo[:args.limit]
        terms_todo = terms_todo[:args.limit]
    if args.only == "persons":
        terms_todo = []
    elif args.only == "terms":
        persons_todo = []
    print(f"To research: {len(persons_todo)} persons + {len(terms_todo)} terms")

    p_updated = 0
    t_updated = 0
    p_skipped = 0
    t_skipped = 0
    t0 = time.time()

    # ── Persons ──
    if persons_todo:
        print(f"\n=== Persons ({len(persons_todo)}) ===")
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(research_person, p, args.overwrite): p
                       for p in persons_todo}
            done = 0
            for fut in as_completed(futures):
                p = futures[fut]
                patch = fut.result()
                done += 1
                if patch:
                    if args.dry_run:
                        print(f"  ⊕ {p['name_english'][:45]:45s} → {patch}")
                    else:
                        ok = patch_person(p["id"], patch)
                        if ok:
                            p_updated += 1
                else:
                    p_skipped += 1
                if done % 20 == 0:
                    rate = done / max(time.time() - t0, 0.1)
                    eta = (len(persons_todo) + len(terms_todo) - done) / max(rate, 0.01)
                    print(f"  ... {done}/{len(persons_todo)} persons, "
                          f"{rate:.1f}/s, ETA {eta/60:.1f}m, "
                          f"updated={p_updated} skipped={p_skipped}")

    # ── Terms ──
    if terms_todo:
        print(f"\n=== Terms ({len(terms_todo)}) ===")
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(research_term, t, args.overwrite): t
                       for t in terms_todo}
            done = 0
            for fut in as_completed(futures):
                t = futures[fut]
                patch = fut.result()
                done += 1
                if patch:
                    if args.dry_run:
                        print(f"  ⊕ {t['term_english'][:45]:45s} → {patch}")
                    else:
                        ok = patch_term(t["id"], patch)
                        if ok:
                            t_updated += 1
                else:
                    t_skipped += 1
                if done % 20 == 0:
                    rate = done / max(time.time() - t0, 0.1)
                    print(f"  ... {done}/{len(terms_todo)} terms, "
                          f"{rate:.1f}/s, updated={t_updated} skipped={t_skipped}")

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed/60:.1f} min ===")
    print(f"Persons: {p_updated} updated, {p_skipped} skipped (low conf / no need / error)")
    print(f"Terms:   {t_updated} updated, {t_skipped} skipped")


if __name__ == "__main__":
    main()
