#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/fathers 三欄的**填充率**：每一卷有多少段真的三欄都有東西。

  python scripts/audit_fathers_coverage.py           # 全部
  python scripts/audit_fathers_coverage.py --third   # 只看已補第三欄那 19 卷

與 `scripts/audit_fathers_columns.mjs` 分工：那一支查「排出來對不對齊」，這一支查
「有沒有東西」。兩個問題不一樣——一卷可以完全對齊而九成的段根本沒有原典欄。

🚨 **「有第三欄」不等於「三欄填滿」。** `/fathers` 首頁的「附原典」標籤是整卷層級的
布林值，只要那一卷有任何一段補了原典就會亮；實際填充率可能只有個位數百分比。
問「翻譯填滿了嗎」要看本表的「三欄齊」那一欄，不要看標籤。

取源與 reader 一致：先本機 Drive（`EBOOK_CHUNKS_DIR`），讀不到才算缺。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def fathers_books() -> list[dict]:
    """與 pages/fathers/index.vue 同一條查詢：subcategory 含 Schaff 或 ACCS。"""
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    q = urllib.parse.quote("subcategory.ilike.*Schaff*,subcategory.ilike.*ACCS*")
    req = urllib.request.Request(
        f"{url}/rest/v1/ebooks?or=({q})&select=id,title,chunk_count&limit=500",
        headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def third_column_ids() -> set[str]:
    vue = (ROOT / "pages" / "fathers" / "index.vue").read_text(encoding="utf-8")
    m = re.search(r"ORIGINAL_IDS\s*=\s*new Set\(\[(.*?)\]\)", vue, re.S)
    return set(re.findall(r"['\"]([0-9a-f-]{36})['\"]", m.group(1))) if m else set()


CJK = re.compile(r"[一-鿿]")
# 拒譯／道歉／後設回覆。實際污染過東方聖卷 2001 段、阿維斯陀 10.7%
# （[[feedback_haiku_meta_reply_pollution]]），一律當成「沒譯」。
META = re.compile(
    r"我注意到|您提供的|你提供的|抱歉[，,]|無法(?:翻譯|處理|完成)|請提供|"
    r"作為一(?:個|位)\s*AI|語言模型|I (?:notice|apologi[sz]e|cannot|'m sorry)|"
    r"as an AI|I need the (?:text|content)")
# 簡體獨有字。🚨 不可以用 OpenCC 轉換比對判繁簡——那會把「祢」判成簡體
# （[[feedback_reader_silent_failures]]）。改用「這些字出現就是簡體」的白名單。
SIMPLIFIED = set("们这来时说过对开关问题东车马书长风飞马纟讠讥认订计"
                 "національ无发国际会员现实师从业总统经济应该权强调"
                 "华严经论语录传记历国学术专题类别选择")


# 註腳分隔線，與 lib/ebook-render.ts 的 FOOTNOTE_SEP_RE 同一條。
FOOTNOTE_SEP = re.compile(r"^[—－\-]{15,}$", re.M)
LATIN = re.compile(r"[A-Za-z]")


def split_body(content: str) -> tuple[str, str]:
    """(正文, 註腳)。沒有分隔線就整段當正文。

    🚨 判「譯了沒」一定要先切開。教父卷的註腳大量是原樣保留的英文書目與經文出處，
    連同正文一起算漢字率，**正文明明譯好的段也會被判成未譯**——實測 ANF 第二卷
    #8 正文 483 個漢字、註腳 1,093 個拉丁字母，整段算下來只有 0.26。
    """
    parts = FOOTNOTE_SEP.split(content or "", maxsplit=1)
    return (parts[0], parts[1] if len(parts) > 1 else "")


def zh_flags(content: str, src_len: int) -> dict:
    """一段繁中譯文的四個毛病。都只看譯文本身，不看對齊。"""
    t = (content or "").strip()
    if not t:
        return {"empty": True, "untranslated": False, "notes_en": False,
                "meta": False, "simp": False}
    body, notes = split_body(t)
    body = body.strip()
    b_letters = [c for c in body if not c.isspace()]
    b_cjk = len(CJK.findall(body))
    b_lat = len(LATIN.findall(body))
    ratio = b_cjk / max(1, len(b_letters))
    # 🚨 非散文的段不算「未譯」：頁碼索引、目次那種只有數字的段本來就沒東西可譯
    #    （實測 #2033 整段 2,981 字只有 4 個拉丁字母，全是頁碼）。要有夠多的
    #    拉丁字母才談得上「這是一段沒譯的英文」。
    is_prose = b_lat >= 100
    return {
        "empty": False,
        "untranslated": len(body) > 200 and is_prose and ratio < 0.30,
        # 正文譯了、註腳還是英文——比整段未譯輕，但要分開數。
        "notes_en": bool(notes.strip()) and len(LATIN.findall(notes)) >= 100
                    and len(CJK.findall(notes)) < len(LATIN.findall(notes)) // 8,
        "meta": bool(META.search(t)),
        "simp": any(c in SIMPLIFIED for c in t),
    }


def count(chunks: list[dict]) -> dict:
    """一卷的填充統計。原典＝en 以外的任何來源語言。"""
    zh = en = orig = all3 = 0
    untr = meta = simp = notes_en = 0
    langs: set[str] = set()
    for c in chunks:
        src = c.get("sources") or {}
        f = zh_flags(c.get("content") or "", len(src.get("en") or ""))
        untr += f["untranslated"]
        notes_en += f["notes_en"]
        meta += f["meta"]
        simp += f["simp"]
        has_zh = not f["empty"]
        has_en = bool((src.get("en") or c.get("source_text") or "").strip())
        others = [k for k in src if k not in ("en", "zh") and (src.get(k) or "").strip()]
        langs.update(others)
        zh += has_zh
        en += has_en
        orig += bool(others)
        all3 += has_zh and has_en and bool(others)
    return {"n": len(chunks), "zh": zh, "en": en, "orig": orig, "all3": all3,
            "untr": untr, "notes_en": notes_en, "meta": meta, "simp": simp,
            "langs": "/".join(sorted(langs)) or "—"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--third", action="store_true", help="只看已補第三欄那幾卷")
    ap.add_argument("--json", help="把逐卷統計寫成 JSON 給 /fathers 首頁用")
    a = ap.parse_args()
    load_env()

    chunks_dir = Path(os.environ.get("EBOOK_CHUNKS_DIR", ""))
    have_third = third_column_ids()
    books = fathers_books()
    books.sort(key=lambda b: b.get("title") or "")

    stats: dict[str, dict] = {}
    print(f"{'卷':40} {'段':>5} {'繁中':>6} {'原典':>6} {'三欄齊':>7} "
          f"{'未譯':>5} {'註腳英':>6} {'拒譯':>5} {'簡體':>5}")
    tot = {"n": 0, "zh": 0, "en": 0, "orig": 0, "all3": 0, "untr": 0,
           "notes_en": 0, "meta": 0, "simp": 0}
    missing = []
    for b in books:
        if a.third and b["id"] not in have_third:
            continue
        f = chunks_dir / f"{b['id']}.jsonl"
        if not f.exists():
            missing.append(b)
            continue
        chunks = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        r = count(chunks)
        for k in tot:
            tot[k] += r[k]
        n_ = max(1, r["n"])
        stats[b["id"]] = {
            "n": r["n"],
            # 譯好的＝有中文欄、且不是「中文欄其實是英文」、也不是拒譯回覆
            "zh": round((r["n"] - r["untr"] - r["meta"]) / n_, 3),
            "orig": round(r["orig"] / n_, 3),
            "all3": round(r["all3"] / n_, 3),
        }
        pct = f"{r['all3'] / r['n']:.0%}" if r["n"] else "—"
        mark = "★" if b["id"] in have_third else " "
        print(f"{mark}{(b.get('title') or '')[:39]:39} {r['n']:5} {r['zh']:6} "
              f"{r['orig']:6} {r['all3']:5}{pct:>4} {r['untr']:5} {r['notes_en']:6} "
              f"{r['meta']:5} {r['simp']:5}")

    print(f"\n合計 {tot['n']} 段：繁中 {tot['zh']}（{tot['zh'] / max(1, tot['n']):.0%}）／"
          f"英 {tot['en']}（{tot['en'] / max(1, tot['n']):.0%}）／"
          f"原典 {tot['orig']}（{tot['orig'] / max(1, tot['n']):.0%}）／"
          f"三欄齊 {tot['all3']}（{tot['all3'] / max(1, tot['n']):.0%}）")
    n = max(1, tot["n"])
    print(f"中譯品質：整段未譯 {tot['untr']}（{tot['untr']/n:.1%}）／"
          f"註腳仍英文 {tot['notes_en']}（{tot['notes_en']/n:.1%}）／"
          f"拒譯污染 {tot['meta']}（{tot['meta']/n:.1%}）／"
          f"夾簡體 {tot['simp']}（{tot['simp']/n:.1%}）")
    if a.json:
        out = Path(a.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(stats, ensure_ascii=False, indent=1) + chr(10),
                       encoding="utf-8")
        print(f"逐卷統計 → {out}（{len(stats)} 卷）")
    print(f"★＝首頁標了「附原典」的卷，共 {len(have_third)} 卷")
    if missing:
        print(f"🚨 讀不到 JSONL 的卷：{len(missing)}（先確認 G: 有沒有掛載）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
