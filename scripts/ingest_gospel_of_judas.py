"""把《猶大福音》收進 /apocrypha。

    python scripts/ingest_gospel_of_judas.py --dry-run
    python scripts/ingest_gospel_of_judas.py --write

🚨 為什麼另立版本碼而不用 cct_zh：
   cct_zh 專指《基督教典外文獻》（黃根春主編，基督教文藝出版社），有版權標記。
   《猶大福音》不在那套書裡——該書第 2 冊 p53 只有一頁簡介，末句明寫「這書的
   文本已經失傳」，因為它出版早於 2006 年查科抄本公布。用 cct_zh 會張冠李戴。

來源：
   英文 gospelsnet_en — Andrew Bernhard 依 Codex Tchacos 3 所譯，譯者明文置於
                        公有領域（"committed to the public domain"）。
   繁中 kgl_zh       — 本站依上述英譯譯出，非譯自科普特原文，此點必須標明。

單位是抄本頁（33–58），因為學界引用此書的格式就是頁碼＋行號（如 45,6-7）。
校勘方括號 […] 與 [補字] 一律保留。
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SC = Path(r"C:\Users\user\AppData\Local\Temp\claude\c--Users-user-Desktop-know-graph-lab"
          r"\d58e3d0f-6f31-498e-b30f-2a931a54d6bc\scratchpad")
PARSED = Path("C:/tmp/gjudas/parsed.json")

VERSIONS = [
    {"code": "gospelsnet_en", "name_zh": "Gospels.net 公有領域英譯（Bernhard）",
     "name_en": "Andrew Bernhard, public-domain translation (gospels.net)",
     "language": "en", "language_zh": "英文", "category": "english",
     "public_domain": True, "is_redistributable": True,
     "copyright_notice": "Public domain — 譯者明文置於公有領域",
     "source_url": "https://www.gospels.net/judas", "display_order": 40,
     "is_default_zh": False, "is_default_en": False, "is_default_orig": False},
    {"code": "kgl_zh", "name_zh": "本站繁中譯", "name_en": "Know-Graph-Lab Chinese translation",
     "language": "zh-Hant", "language_zh": "繁體中文", "category": "chinese",
     "public_domain": False, "is_redistributable": False,
     "copyright_notice": "本站自譯；轉譯自英譯本而非原文，引用時請註明",
     "source_url": None, "display_order": 11,
     "is_default_zh": False, "is_default_en": False, "is_default_orig": False},
]


def env():
    return dict(l.strip().split("=", 1)
                for l in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
                if "=" in l and not l.startswith("#"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.write or a.dry_run):
        ap.error("要 --dry-run 或 --write")

    parsed = json.loads(PARSED.read_text(encoding="utf-8"))
    zh = json.loads((Path("C:/tmp/gjudas/zh.json")).read_text(encoding="utf-8"))
    notes = json.loads((SC / "gjudas_notes_zh.json").read_text(encoding="utf-8"))
    pages = parsed["pages"]

    # ── 閘：每頁都要有中英文，且中譯必須真的是中文 ──
    problems = []
    for p in pages:
        k = str(p["page"])
        if k not in zh:
            problems.append(f"p{k} 缺中譯")
            continue
        t = zh[k]
        han = len(re.findall(r"[\u4e00-\u9fff]", t))
        if han / max(1, len(t)) < 0.5:
            problems.append(f"p{k} 中譯漢字比例過低（{han}/{len(t)}）")
        if any(m in t for m in ("我注意到", "以下是翻譯", "As an AI", "<think>")):
            problems.append(f"p{k} 疑似 LLM 元回覆混入")
        r = len(t) / max(1, len(p["text"]))
        if not 0.25 < r < 1.1:
            problems.append(f"p{k} 中英長度比異常 {r:.2f}")
    if problems:
        print("✗ 閘未過：")
        for x in problems:
            print("   ", x)
        sys.exit(1)
    print(f"✓ 閘全過：{len(pages)} 頁，中譯 {sum(len(zh[str(p['page'])]) for p in pages)} 字、"
          f"英文 {sum(len(p['text']) for p in pages)} 字、註釋 {len(notes)} 條")

    rows = []
    for i, p in enumerate(pages, 1):
        k = str(p["page"])
        note = json.dumps([{"page": p["page"], "text": notes[k]}], ensure_ascii=False) if k in notes else None
        for code, text in (("kgl_zh", zh[k]), ("gospelsnet_en", p["text"])):
            rows.append({
                "doc_slug": "gjudas", "version_code": code, "order_index": i,
                "section_label": f"{p['page']}", "chapter": p["page"], "verse": 1,
                "page_number": p["page"], "text": text, "char_count": len(text),
                "footnote_defs": note if code == "kgl_zh" else None,
            })
    print(f"待寫入 {len(rows)} 列（{len(pages)} 頁 × 2 版本）")
    print(f"範例：{rows[0]['section_label']} / {rows[0]['version_code']} / {rows[0]['text'][:48]}…")

    if a.dry_run:
        print("\n--dry-run：未寫入")
        return

    e = env()
    url, key = e["SUPABASE_URL"].strip(), e["SUPABASE_SERVICE_ROLE_KEY"].strip()
    h = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"}

    for v in VERSIONS:
        r = requests.post(f"{url}/rest/v1/apocrypha_versions", headers={**h, "Prefer": "resolution=merge-duplicates"},
                          json=v)
        print(f"  版本 {v['code']}: {r.status_code}")

    r = requests.delete(f"{url}/rest/v1/apocrypha_sections?doc_slug=eq.gjudas", headers=h)
    print(f"  清舊列: {r.status_code}")
    for i in range(0, len(rows), 100):
        r = requests.post(f"{url}/rest/v1/apocrypha_sections", headers=h, json=rows[i:i + 100])
        if r.status_code >= 300:
            print("  ✗", r.status_code, r.text[:300])
            sys.exit(1)
    print(f"  寫入 {len(rows)} 列 ✓")

    r = requests.get(f"{url}/rest/v1/apocrypha_sections?select=version_code&doc_slug=eq.gjudas&limit=200", headers=h)
    from collections import Counter
    print("  覆核：", dict(Counter(x["version_code"] for x in r.json())))


if __name__ == "__main__":
    main()
