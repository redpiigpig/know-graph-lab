# -*- coding: utf-8 -*-
"""柏拉圖對話錄 → 希臘/英/繁中三欄（collected-works 哲學群，pipeline ① 多語對照）。

來源＝Perseus canonical-greekLit Unicode TEI（皆公有領域）：
  grc  = tlg0059.tlgNNN.perseus-grc2.xml（Unicode 希臘原文）
  eng  = tlg0059.tlgNNN.perseus-eng2.xml（Fowler 英譯，Loeb 1914，PD）
兩版皆以 **Stephanus 節（milestone unit="section" n="17a"…）** 為錨點 → 完美對齊。

對齊粒度＝Stephanus 節：每節 grc/en/繁中各一段，一個 Stephanus「頁」(17,18…) = 一個 reader chunk。
繁中**逐節**翻（從希臘、Fowler 英譯僅供消歧義），join('\\n\\n') → 段數必等於來源段數。

用法：
  python scripts/plato_build.py apology --limit 1            # smoke：只做第 17 頁
  python scripts/plato_build.py apology                      # 全 26 頁，寫 JSONL
  python scripts/plato_build.py apology --upload             # 全跑 + R2 + DB previews + ensure row
"""
from __future__ import annotations
import argparse, io, json, os, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import multilang_chunks as mc  # noqa: E402

CACHE = Path("c:/tmp/plato_cache")
BASE = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0059"

# ── 對話錄 registry（逐部擴充；ebook_id 命名空間 7000…＝哲學/柏拉圖）──────────────
DIALOGUES = {
    "apology": {
        "tlg": "tlg002",
        "ebook_id": "70000000-0000-4000-8000-000000000001",
        "title_zh": "蘇格拉底的申辯",
        "title_orig": "Ἀπολογία Σωκράτους",
        "author": "柏拉圖",
        "category": "世界宗教／哲學",
        "volume": "蘇格拉底的申辯",
        "parent_volume": "柏拉圖對話錄‧早期",
    },
}

SEC_RE = re.compile(r'<milestone[^>]*unit="section"[^>]*\bn="([^"]+)"[^>]*/>')

PLATO_PROMPT_TMPL = """你是古希臘哲學經典的專業譯者。把下列**古希臘文（阿提卡/柏拉圖）原典**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；學術散文語氣，忠實流暢，不加註不改寫。
2. 從希臘原文翻譯；附上的英文（Fowler 英譯）僅供消歧義參考，**不要翻譯英文**。
3. 術語鎖定（希臘為準）：εἶδος/ἰδέα→理型、λόγος→邏各斯（依文脈亦可「話語/理性」）、
   νοῦς→努斯/心智、ψυχή→靈魂、ἀρετή→德性、εὐδαιμονία→幸福、δαίμων/δαιμόνιον→神靈/靈異徵兆、
   ἀσέβεια→不敬神、σοφία→智慧、ἔλεγχος→詰問。人名／地名：Σωκράτης→蘇格拉底、
   Ἀθηναῖοι→雅典人、Μέλητος→美勒托、Ἄνυτος→阿尼圖斯、Δελφοί→德爾斐。
4. **只輸出一段連續的繁體中文譯文**，不要分段、不要節號、不要前言或說明。

{source}"""


def fetch(slug: str) -> tuple[str, str]:
    d = DIALOGUES[slug]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = []
    for kind in ("grc2", "eng2"):
        fn = CACHE / f"tlg0059.{d['tlg']}.perseus-{kind}.xml"
        if not fn.exists() or fn.stat().st_size < 2000:
            import requests
            url = f"{BASE}/{d['tlg']}/tlg0059.{d['tlg']}.perseus-{kind}.xml"
            fn.write_text(requests.get(url, timeout=60).text, encoding="utf-8")
        out.append(fn.read_text(encoding="utf-8"))
    return out[0], out[1]


def _body(xml: str) -> str:
    m = re.search(r'<body\b[^>]*>(.*)</body>', xml, re.S)
    return m.group(1) if m else xml


def _clean(t: str) -> str:
    t = re.sub(r'<note\b[^>]*>.*?</note>', '', t, flags=re.S)
    t = re.sub(r'<(bibl|ref|cit)\b[^>]*>.*?</\1>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '', t)
    for a, b in (('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&apos;', "'")):
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


def parse_sections(xml: str) -> dict[str, str]:
    b = _body(xml)
    marks = list(SEC_RE.finditer(b))
    out: dict[str, str] = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(b)
        txt = _clean(b[m.end():end])
        if txt:
            out[m.group(1)] = txt
    return out


def _page(sec: str) -> str:
    m = re.match(r'(\d+)', sec)
    return m.group(1) if m else sec


def build_units(slug: str, grc: dict, eng: dict) -> list[dict]:
    """One unit per Stephanus page; carries per-section (grc,en) for aligned translation."""
    d = DIALOGUES[slug]
    common = [s for s in grc if s in eng]
    pages: dict[str, list[str]] = {}
    for s in common:
        pages.setdefault(_page(s), []).append(s)
    units = []
    for pg, secs in pages.items():
        units.append({
            "chapter_path": f"{d['title_zh']} · 斯提法努斯 {pg}",
            "page_number": int(pg),
            "volume": d["volume"],
            "parent_volume": d["parent_volume"],
            "title_en": f"Stephanus {pg}",
            "sources": {"grc": "\n\n".join(grc[s] for s in secs),
                        "en": "\n\n".join(eng[s] for s in secs)},
            "_sections": [(s, grc[s], eng[s]) for s in secs],
        })
    return units


def make_translate_fn(engine: str = "gemini"):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = PLATO_PROMPT_TMPL
    engine_fn = {"gemini": te.gemini_with_haiku_fallback,
                 "haiku": te.haiku_translate,
                 "sonnet": te.sonnet_translate}[engine]

    def translate_fn(unit: dict) -> str:
        zhs = []
        for _sec, g, e in unit["_sections"]:
            src = f"{g}\n\n[英文參考（Fowler，勿翻）]\n{e}"
            zhs.append(engine_fn(src).strip())
        return "\n\n".join(zhs)  # 段數 == 來源節數 → reader zip 對齊

    return translate_fn


def ensure_ebook_row(slug: str) -> None:
    import translate_ebook_to_zh as te
    import requests
    d = DIALOGUES[slug]
    r = requests.get(f"{te.URL}/rest/v1/ebooks?id=eq.{d['ebook_id']}&select=id",
                     headers=te.H_GET, timeout=30)
    if r.ok and r.json():
        return
    row = {"id": d["ebook_id"], "title": f"{d['title_zh']}（希英繁三欄）",
           "author": d["author"], "category": d["category"],
           "source_lang": "grc", "display_mode": "multilang", "status": "ready"}
    requests.post(f"{te.URL}/rest/v1/ebooks", headers=te.H_JSON, json=row, timeout=30)
    print(f"  ✓ inserted ebooks row {d['ebook_id']}")


def run(slug: str, *, engine="gemini", limit=None, upload=False) -> list[dict]:
    d = DIALOGUES[slug]
    grc_xml, eng_xml = fetch(slug)
    grc, eng = parse_sections(grc_xml), parse_sections(eng_xml)
    units = build_units(slug, grc, eng)
    print(f"[{slug}] {len(grc)} grc / {len(eng)} en sections → {len(units)} pages")
    if limit:
        units = units[:limit]
    tfn = make_translate_fn(engine)
    chunks = mc.assemble_multilang_chunks(units, tfn, ["grc", "en"], volume=d["volume"])
    for c, u in zip(chunks, units):  # assemble 不轉 page_number → 補回（Stephanus 頁）
        c["page_number"] = u["page_number"]
    # per-chunk 段數對齊閘
    for c in chunks:
        nz = len(c["content"].split("\n\n"))
        ng = len(c["sources"]["grc"].split("\n\n"))
        ne = len(c["sources"]["en"].split("\n\n"))
        if not (nz == ng == ne):
            print(f"  ⚠ chunk {c['chunk_index']} (p{c['page_number']}) 段數不齊 zh={nz} grc={ng} en={ne}")
    out = Path(f"c:/tmp/plato_{slug}.jsonl")
    mc.write_jsonl(chunks, out)
    print(f"  ✓ wrote {out}  ({len(chunks)} chunks, {sum(len(c['content']) for c in chunks)} 繁中字)")
    if upload:
        ensure_ebook_row(slug)
        from translate_collected_work import _upload
        _upload(d["ebook_id"], chunks, out)
    return chunks


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dialogue", choices=list(DIALOGUES))
    ap.add_argument("--engine", default="gemini")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()
    run(a.dialogue, engine=a.engine, limit=a.limit, upload=a.upload)
