"""Import full text of cited 印順／聖嚴 works from our OWN collected-works corpus
into a 研究回顧 paper's lit_review_sections (single-version 'zh', no translation).

Unlike ingest_lit_review.py --fetch-fulltext (which fetches *external* open-access
URLs and translates), this pulls text from chunks we already transcribed
(yinshun a0000000-… / shengyen b0000000-…), so the article's full text shows
inline in the /works research-review reader (single Chinese column).

Each entry is matched to one of:
  ('whole',)                  every content chunk of the ebook (skip header idx 0)
  ('idx', n[, n2, …])         explicit chunk_index list (one 篇 = one chunk)
  ('work', name)              all chunks whose chapter_path[0] startswith `name`

The chunk full text lives in local JSONL (translate_ebook_to_zh.CHUNKS_DIR).
Sections are written version_code='zh'; fulltext_status→'translated';
fulltext_url→ internal reader deep-link /ebook/{id}?page={firstChunk+1}.

  python -X utf8 scripts/import_corpus_fulltext.py --project yinshun-shengyan --dry-run
  python -X utf8 scripts/import_corpus_fulltext.py --project yinshun-shengyan
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_ebook_to_zh as te  # noqa: E402  (for CHUNKS_DIR)

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
     "Content-Type": "application/json"}
CHUNKS_DIR = Path(str(te.CHUNKS_DIR))


def ebid(prefix: str, n: int) -> str:
    return f"{prefix}0000000-0000-4000-8000-{n:012d}"


YS = "a"   # 印順 prefix
SY = "b"   # 聖嚴 prefix

# ref_key → (ebook_id, locator…). ref_key from lit_review_entries (zh<hash>[-year]).
# Matched against c12〈聖嚴法師與法鼓系統…〉by title — see import notes.
MAP: dict[str, tuple] = {
    # ── 印順導師全集（yinshun）──────────────────────────────────────────
    "zhc7d7462a-1971": (ebid(YS, 40), "whole"),                          # 中國禪宗史
    "zhed9e1729-2005": (ebid(YS, 41), "whole"),                          # 平凡的一生（重訂本）
    "zh4493222d-1993": (ebid(YS, 28), "work", "契理契機之人間佛教"),       # 華雨集（四）
    "zh92f0009d-2004": (ebid(YS, 43), "work", "為自己說幾句話"),          # 永光集
    "zh4e6dd6a3-1993": (ebid(YS, 29), "work", "為取得日本學位而要說的幾句話"),  # 華雨集（五）
    "zhef8bd2be-1992": (ebid(YS, 21), "work", "僧衣染色的論究"),          # 教制教典與教學
    # ── 聖嚴法師《法鼓全集 2020 紀念版》（shengyen）── 每篇 = 一 chunk ──
    "zhab3ec7ef-1960": (ebid(SY, 16), "idx", 11),   # 《成佛之道》讀後（評介）
    "zhe5af01c7-1973": (ebid(SY, 16), "idx", 3),    # 劃時代的博士比丘（評介）
    "zhfa5380c4-1977": (ebid(SY, 16), "idx", 1),    # 近代中國佛教史上的四位思想家（評介）
    "zh6dc0b981-1995": (ebid(SY, 15), "idx", 30),   # 序《…印順導師九秩華誕祝壽文集》（書序）
    "zhd2bd1eb5-2000": (ebid(SY, 11), "idx", 18),   # 印順長老著述中的真常唯心論（學術論考）
    "zhb84dccae-2020": (ebid(SY, 43), "idx", 12),   # 印順覆聖嚴的信（含於〈今後佛教的女眾問題〉）
    "zh8ca9baf7-2020": (ebid(SY, 43), "idx", 12),   # 今後佛教的女眾問題（學佛知津）
    "zh7dac7393-2020": (ebid(SY, 17), "idx", 52),   # 以研究「聖嚴」來推動淨化世界（致詞）
    "zh35e0667b-2020": (ebid(SY, 11), "idx", 7),    # 正法律中的僧尼衣制（學術論考）
    "zhec55f6e8-2020": (ebid(SY, 16), "idx", 4),    # 印順長老的佛學思想（評介）
    "zhea247bb5-2020": (ebid(SY, 11), "idx", 13),   # 印順長老的護教思想與現代社會（學術論考）
    "zh533e9498-2020": (ebid(SY, 17), "idx", 25),   # 印順導師思想與當代佛教（致詞）
    "zh047af07e-2020": (ebid(SY, 19), "idx", 16),   # 印順長老——劃時代的博士比丘（我的法門師友）
    "zhc5e83043-2020": (ebid(SY, 15), "idx", 12),   # 序宏印法師《怎樣讀妙雲集》（書序）
    "zhd98de390-2020": (ebid(SY, 19), "idx", 3),    # 東初老人——我的剃度恩師（我的法門師友）
    # ── 全集補充（論文未引用、主題高度相關）──────────────────────────────
    "zhd81842a8-2020": (ebid(SY, 16), "idx", 7),    # 《中國禪宗史》讀後（評介）
    "zh3eb1a001-2020": (ebid(SY, 16), "idx", 2),    # 太虛大師評傳（評介）
}


def load_ebook(ebook_id: str) -> list[dict]:
    p = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not p.exists():
        raise FileNotFoundError(p)
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def select_chunks(rows: list[dict], loc: tuple) -> list[dict]:
    kind = loc[1]
    if kind == "whole":
        return [r for r in rows if (r.get("chunk_index") or 0) > 0 and (r.get("content") or "").strip()]
    if kind == "idx":
        want = set(loc[2:])
        return [r for r in rows if r.get("chunk_index") in want]
    if kind == "work":
        name = loc[2]
        out = []
        for r in rows:
            segs = [s.strip() for s in (r.get("chapter_path") or "").split(" · ")]
            # chapter_path is `book · work · section…`; the work名 is a whole segment
            # (skip the bare book-title chunk where it'd be the only/first segment).
            if any(s.startswith(name) for s in segs[1:]):
                out.append(r)
        return out
    raise ValueError(loc)


_HEAD_RE = re.compile(r"^#{1,6}\s*")


def chunk_to_paragraphs(r: dict) -> list[str]:
    """One chunk's markdown content → reader paragraphs. Section heading kept as
    its own paragraph (markdown #'s stripped); body paragraphs split on blank lines."""
    content = (r.get("content") or "").strip()
    paras: list[str] = []
    for block in re.split(r"\n\s*\n", content):
        block = block.strip()
        if not block:
            continue
        block = _HEAD_RE.sub("", block).strip()
        if block:
            paras.append(block)
    return paras


def build_sections(loc: tuple) -> tuple[list[str], int]:
    """→ (paragraphs, first_chunk_index)."""
    rows = load_ebook(loc[0])
    chunks = select_chunks(rows, loc)
    if not chunks:
        return [], 0
    first = min(c.get("chunk_index") or 0 for c in chunks)
    paras: list[str] = []
    multi = len(chunks) > 1
    for c in sorted(chunks, key=lambda x: x.get("chunk_index") or 0):
        if multi:
            # prepend the section sub-title so multi-篇 works read with structure
            tail = (c.get("chapter_path") or "").split(" · ")
            sub = " · ".join(tail[1:]) if len(tail) > 1 else tail[0]
            sub = sub.strip()
        ps = chunk_to_paragraphs(c)
        if multi and sub and (not ps or sub not in ps[0]):
            paras.append(f"〔{sub}〕")
        paras.extend(ps)
    return paras, first


# ── REST ──────────────────────────────────────────────────────────────────────
def rest_get(table: str, params: str) -> list[dict]:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=H, timeout=60)
    r.raise_for_status()
    return r.json()


def rest_delete(table: str, params: str) -> None:
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}?{params}",
                        headers={**H, "Prefer": "return=minimal"}, timeout=60)
    if r.status_code not in (200, 204):
        r.raise_for_status()


def rest_insert(table: str, rows: list[dict]) -> None:
    for i in range(0, len(rows), 500):
        batch = rows[i:i + 500]
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}",
                          headers={**H, "Prefer": "return=minimal"},
                          data=json.dumps(batch), timeout=120)
        if r.status_code not in (200, 201, 204):
            print(f"  ERROR insert {table}: {r.status_code} {r.text[:300]}")
            r.raise_for_status()


def rest_patch(table: str, params: str, body: dict) -> None:
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}",
                       headers={**H, "Prefer": "return=minimal"},
                       data=json.dumps(body), timeout=60)
    if r.status_code not in (200, 204):
        r.raise_for_status()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="ref_key substring filter")
    args = ap.parse_args()

    entries = rest_get("lit_review_entries",
                       f"project_slug=eq.{args.project}&select=id,ref_key,title&limit=500")
    by_key = {e["ref_key"]: e for e in entries}

    total_paras = 0
    done = 0
    for ref_key, loc in MAP.items():
        if args.only and args.only not in ref_key:
            continue
        e = by_key.get(ref_key)
        if not e:
            print(f"  ⚠ ref_key not in project: {ref_key}")
            continue
        paras, first = build_sections(loc)
        ebook_id = loc[0]
        url = f"/ebook/{ebook_id}?page={first + 1}"
        print(f"  {ref_key}  「{e['title']}」 → {len(paras)} paras  [{ebook_id[:1]}…{int(ebook_id[-3:])} #{first}]")
        if not paras:
            print("     ⚠ NO chunks matched — check locator")
            continue
        total_paras += len(paras)
        if args.dry_run:
            print("     ", paras[0][:60].replace("\n", " "), "…")
            continue
        rest_delete("lit_review_sections", f"entry_id=eq.{e['id']}")
        rows = [{"entry_id": e["id"], "version_code": "zh", "order_index": i,
                 "text": p, "char_count": len(p)} for i, p in enumerate(paras)]
        rest_insert("lit_review_sections", rows)
        rest_patch("lit_review_entries", f"id=eq.{e['id']}",
                   {"fulltext_status": "translated", "fulltext_url": url})
        done += 1
    print(f"\n{'DRY ' if args.dry_run else ''}done: {done} entries, {total_paras} paragraphs total")


if __name__ == "__main__":
    main()
