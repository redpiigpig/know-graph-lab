# -*- coding: utf-8 -*-
"""古希臘哲學經典（柏拉圖／亞里斯多德）→ 希臘/英/繁中三欄（collected-works 哲學群，pipeline ① 多語對照）。

來源＝Perseus canonical-greekLit Unicode TEI（希臘原文＝Burnet/Bywater… PD；英譯＝Fowler/Shorey/Rackham…，
多屬 PD，個別受版權者僅作私人研究庫參考欄，主欄是我自希臘原文的自譯 → [[feedback_jung_nonpd_english_first]]）。
兩版皆以同一 **錨點 milestone** 對齊：柏拉圖＝Stephanus 節（`unit="section" n="17a"`）、
亞里斯多德＝Bekker 頁（`unit="page" n="1094a"`）。逐節/逐頁翻繁中，段數必等於來源 → reader zipParallel 對齊。

用法：
  python scripts/plato_build.py <slug> --limit 1        # smoke
  python scripts/plato_build.py <slug> --upload         # 全跑 + R2 + DB + ensure row（resumable：逐節快取）
  python scripts/plato_build.py --list                  # 列出所有 slug
"""
from __future__ import annotations
import argparse, io, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import multilang_chunks as mc  # noqa: E402

CACHE = Path("c:/tmp/plato_cache")
RAW = "https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data"
_P, _A = "柏拉圖", "亞里斯多德"
_UNIT_LABEL = {"section": "斯提法努斯", "page": "貝克爾"}
_PARENT = {_P: "柏拉圖對話錄", _A: "亞里斯多德著作"}
_CJK = "一二三四五六七八九十十一十二十三十四"

# (slug, author, tlg, ebook_n, title_zh[對齊 store], title_orig, anchor, grc_kind[, eng_note])
_TABLE = [
    ("apology", _P, "tlg002", 1, "蘇格拉底的申辯", "Ἀπολογία Σωκράτους", "section", "grc2"),
    ("republic", _P, "tlg030", 2, "理想國", "Πολιτεία", "section", "grc2", "Shorey（Loeb 1935，受版權‧私人庫參考）"),
    ("euthyphro", _P, "tlg001", 3, "歐緒弗洛", "Εὐθύφρων", "section", "grc1"),
    ("crito", _P, "tlg003", 4, "克里同", "Κρίτων", "section", "grc2"),
    ("phaedo", _P, "tlg004", 5, "斐多", "Φαίδων", "section", "grc2"),
    ("cratylus", _P, "tlg005", 6, "克拉底魯", "Κρατύλος", "section", "grc2"),
    ("theaetetus", _P, "tlg006", 7, "泰阿泰德", "Θεαίτητος", "section", "grc2"),
    ("sophist", _P, "tlg007", 8, "智者", "Σοφιστής", "section", "grc2"),
    ("statesman", _P, "tlg008", 9, "政治家", "Πολιτικός", "section", "grc2"),
    ("parmenides-d", _P, "tlg009", 10, "巴門尼德", "Παρμενίδης", "section", "grc2"),
    ("philebus", _P, "tlg010", 11, "斐利布斯", "Φίληβος", "section", "grc2"),
    ("symposium", _P, "tlg011", 12, "會飲", "Συμπόσιον", "section", "grc2"),
    ("phaedrus", _P, "tlg012", 13, "斐德羅", "Φαῖδρος", "section", "grc2"),
    ("protagoras-d", _P, "tlg022", 22, "普羅塔哥拉", "Πρωταγόρας", "section", "grc2"),
    ("gorgias-d", _P, "tlg023", 23, "高爾吉亞", "Γοργίας", "section", "grc2"),
    ("meno", _P, "tlg024", 24, "美諾", "Μένων", "section", "grc2"),
    ("timaeus", _P, "tlg031", 31, "蒂邁歐", "Τίμαιος", "section", "grc2"),
    ("critias", _P, "tlg032", 32, "克里底亞", "Κριτίας", "section", "grc2"),
    ("laws", _P, "tlg034", 34, "法律篇", "Νόμοι", "section", "grc2"),
    ("letters", _P, "tlg036", 36, "書信集（含第七封信）", "Ἐπιστολαί", "section", "grc2"),
    # 亞里斯多德（Perseus 有 grc+eng 的 6 部；Bekker 頁錨點）
    ("nicomachean-ethics", _A, "tlg010", 51, "尼各馬可倫理學", "Ἠθικὰ Νικομάχεια", "page", "grc2", "Rackham（Loeb 1926，PD）"),
    ("eudemian-ethics", _A, "tlg009", 52, "歐德謨倫理學", "Ἠθικὰ Εὐδήμεια", "page", "grc2"),
    ("metaphysics", _A, "tlg025", 53, "形上學", "τὰ Μετὰ τὰ Φυσικά", "page", "grc2"),
    ("politics", _A, "tlg035", 54, "政治學", "Πολιτικά", "page", "grc2"),
    ("poetics", _A, "tlg034", 55, "詩學", "Περὶ ποιητικῆς", "page", "grc2"),
    ("rhetoric", _A, "tlg038", 56, "修辭學", "Ῥητορική", "page", "grc2"),
]


def _mk(row) -> dict:
    slug, author, tlg, n, tz, to, anchor, grc = row[:8]
    note = row[8] if len(row) > 8 else None
    return {"slug": slug, "author": author, "author_en": "Plato" if author == _P else "Aristotle",
            "tlg": tlg, "ebook_id": f"70000000-0000-4000-8000-{n:012d}",
            "title_zh": tz, "title_orig": to, "anchor": anchor, "grc_kind": grc,
            "unit_label": _UNIT_LABEL[anchor], "parent_volume": _PARENT[author],
            "category": "世界宗教", "subcategory": "古希臘哲學",
            "file_path": f"PERSEUS/greek-{slug}-trilingual", "eng_note": note}


WORKS = {r[0]: _mk(r) for r in _TABLE}

_MS_RE = re.compile(r'<milestone\b([^>]*?)/?>')
_BOOK_RE = re.compile(r'<div\b[^>]*subtype="book"[^>]*?\bn="([^"]+)"')


def _attr(s: str, name: str):
    m = re.search(rf'\b{name}="([^"]+)"', s)
    return m.group(1) if m else None


PROMPT_TMPL = """你是古希臘哲學經典的專業譯者。把下列**古希臘文原典**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；學術散文語氣，忠實流暢，不加註不改寫。
2. 從希臘原文翻譯；附上的英文（既有英譯）僅供消歧義參考，**不要翻譯英文**。
3. 術語鎖定（希臘為準）：εἶδος/ἰδέα→理型、οὐσία→實體、λόγος→邏各斯（依文脈亦可話語/理性）、
   νοῦς→努斯/心智、ψυχή→靈魂、ἀρετή→德性、εὐδαιμονία→幸福、μεσότης→中庸、
   δύναμις/ἐνέργεια→潛能/實現、σοφία→智慧、δίκαιοσύνη→正義、ἔλεγχος→詰問、
   δαίμων/δαιμόνιον→神靈/靈異徵兆。人名：Σωκράτης→蘇格拉底、Πλάτων→柏拉圖、Ἀθηναῖοι→雅典人。
4. **只輸出一段連續的繁體中文譯文**，不要分段、不要節號、不要前言或說明。

{source}"""


def fetch(slug: str) -> tuple[str, str]:
    d = WORKS[slug]
    CACHE.mkdir(parents=True, exist_ok=True)
    auth_tlg = "tlg0059" if d["author"] == _P else "tlg0086"
    out = []
    for kind in (d["grc_kind"], "eng2"):
        fn = CACHE / f"{auth_tlg}.{d['tlg']}.perseus-{kind}.xml"
        if not fn.exists() or fn.stat().st_size < 2000:
            import requests
            url = f"{RAW}/{auth_tlg}/{d['tlg']}/{auth_tlg}.{d['tlg']}.perseus-{kind}.xml"
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


def parse_units(xml: str, anchor: str) -> list[tuple]:
    """Ordered [(book_or_None, anchor_id, text)]；anchor＝section(Stephanus)/page(Bekker)。
    milestone 屬性順序不定 → 用 _attr 逐一取，別假設 unit 在 n 前。"""
    b = _body(xml)
    books = [(m.group(1), m.start()) for m in _BOOK_RE.finditer(b)]

    def book_of(pos):
        bk = None
        for n, st in books:
            if st < pos:
                bk = n
            else:
                break
        return bk

    marks = [(m.start(), m.end(), _attr(m.group(1), "n"))
             for m in _MS_RE.finditer(b) if _attr(m.group(1), "unit") == anchor]
    out = []
    for i, (st, en, n) in enumerate(marks):
        if not n:
            continue
        end = marks[i + 1][0] if i + 1 < len(marks) else len(b)
        txt = _clean(b[en:end])
        if txt:
            out.append((book_of(st), n, txt))
    return out


def _num(anchor_id: str) -> str:
    m = re.match(r'(\d+)', anchor_id)
    return m.group(1) if m else anchor_id


def _book_label(bk):
    if not bk:
        return None
    if bk.isdigit() and 1 <= int(bk) <= len(_CJK):
        return f"第{_CJK[int(bk) - 1]}卷"
    return f"卷{bk}"


def build_units(slug: str, grc: list, eng: list) -> list[dict]:
    from collections import OrderedDict
    d = WORKS[slug]
    eng_map = {aid: txt for _bk, aid, txt in eng}
    groups: "OrderedDict[tuple, list]" = OrderedDict()
    for bk, aid, g in grc:
        if aid not in eng_map:
            continue
        groups.setdefault((bk, _num(aid)), []).append((aid, g, eng_map[aid]))
    units = []
    for (bk, num), secs in groups.items():
        lbl = _book_label(bk)
        vol = f"{d['title_zh']}‧{lbl}" if lbl else d["title_zh"]
        cp = (f"{d['title_zh']} · {lbl} · {d['unit_label']} {num}" if lbl
              else f"{d['title_zh']} · {d['unit_label']} {num}")
        units.append({
            "chapter_path": cp, "page_number": int(num), "volume": vol,
            "parent_volume": d["parent_volume"],
            "title_en": f"{('Bk ' + bk + ' ') if bk else ''}{d['unit_label']} {num}",
            "sources": {"grc": "\n\n".join(g for _s, g, _e in secs),
                        "en": "\n\n".join(e for _s, _g, e in secs)},
            "anchors": [s for s, _g, _e in secs],  # 每段引用號（Stephanus 17a／Bekker 1094a）
            "_sections": [(s, g, e) for s, g, e in secs],
        })
    return units


def _prepend_cover(slug: str, content_chunks: list[dict]) -> list[dict]:
    d = WORKS[slug]
    cover = mc.build_multilang_chunk(
        chunk_index=0, chapter_path="封面", content_zh="## 封面", sources={}, source_order=[],
        volume=d["title_zh"], parent_volume=d["parent_volume"], chunk_type="cover", page_number=1)
    mc.validate_multilang_chunk(cover)
    for i, c in enumerate(content_chunks, start=1):
        c["chunk_index"] = i
    return [cover] + content_chunks


def make_translate_fn(engine: str, slug: str):
    """逐節翻＋逐節快取（`c:/tmp/plato_cache/<slug>_zh/<id>.txt`）→ 大部中途掛掉重跑自動續。"""
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = PROMPT_TMPL
    engine_fn = {"gemini": te.gemini_with_haiku_fallback, "haiku": te.haiku_translate,
                 "sonnet": te.sonnet_translate, "nvidia": te.nvidia_translate}[engine]
    cdir = CACHE / f"{slug}_zh"
    cdir.mkdir(parents=True, exist_ok=True)

    def _flat(s: str) -> str:  # 一節＝一段：壓平內部換行，否則 reader zip 會錯位
        return re.sub(r'\s+', ' ', s).strip()

    def translate_fn(unit: dict) -> str:
        zhs, fresh = [], 0
        for sec, g, e in unit["_sections"]:
            cf = cdir / (re.sub(r'[^\w.-]', '_', sec) + ".txt")
            cached = cf.read_text(encoding="utf-8").strip() if cf.exists() else ""
            if cached:
                zhs.append(_flat(cached))
                continue
            zh = _flat(engine_fn(f"{g}\n\n[既有英譯參考（勿翻）]\n{e}"))
            cf.write_text(zh, encoding="utf-8")
            zhs.append(zh)
            fresh += 1
        if fresh:
            print(f"  ↳ {unit['chapter_path']} (+{fresh})")
        return "\n\n".join(zhs)

    return translate_fn


def ensure_ebook_row(slug: str) -> None:
    import translate_ebook_to_zh as te
    import requests
    d = WORKS[slug]
    r = requests.get(f"{te.URL}/rest/v1/ebooks?id=eq.{d['ebook_id']}&select=id", headers=te.H_GET, timeout=30)
    if r.ok and r.json():
        return
    row = {"id": d["ebook_id"], "title": f"{d['title_zh']}（希英繁三欄）",
           "author": d["author"], "author_en": d["author_en"], "file_type": "epub",
           "file_path": d["file_path"], "category": d["category"], "subcategory": d["subcategory"],
           "original_title": d["title_orig"], "translator": "Claude（希臘直譯）", "display_mode": "standard"}
    requests.post(f"{te.URL}/rest/v1/ebooks", headers=te.H_JSON, json=row, timeout=30).raise_for_status()
    print(f"  ✓ inserted ebooks row {d['ebook_id']}")


def run(slug: str, *, engine="haiku", limit=None, upload=False) -> list[dict]:
    d = WORKS[slug]
    grc_xml, eng_xml = fetch(slug)
    grc, eng = parse_units(grc_xml, d["anchor"]), parse_units(eng_xml, d["anchor"])
    units = build_units(slug, grc, eng)
    print(f"[{slug}] {d['author']}《{d['title_zh']}》 {len(grc)}/{len(eng)} {d['anchor']} → {len(units)} 頁"
          f"{' / eng=' + d['eng_note'] if d.get('eng_note') else ''}")
    if limit:
        units = units[:limit]
    tfn = make_translate_fn(engine, slug)
    chunks = mc.assemble_multilang_chunks(units, tfn, ["grc", "en"], volume=d["title_zh"])
    for c, u in zip(chunks, units):
        c["page_number"] = u["page_number"]
    chunks = _prepend_cover(slug, chunks)
    for c in chunks:
        if c.get("chunk_type") == "cover" or not c.get("sources"):
            continue
        nz, ng, ne = (len(c["content"].split("\n\n")), len(c["sources"]["grc"].split("\n\n")),
                      len(c["sources"]["en"].split("\n\n")))
        if not (nz == ng == ne):
            print(f"  ⚠ chunk {c['chunk_index']} (p{c['page_number']}) 段數不齊 zh={nz} grc={ng} en={ne}")
    out = Path(f"c:/tmp/plato_{slug}.jsonl")
    mc.write_jsonl(chunks, out)
    print(f"  ✓ {out.name}  {len(chunks)} chunks / {sum(len(c['content']) for c in chunks)} 繁中字")
    if upload:
        ensure_ebook_row(slug)
        from translate_collected_work import _upload
        _upload(d["ebook_id"], chunks, out)
    return chunks


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("work", nargs="?", choices=list(WORKS))
    ap.add_argument("--engine", default="haiku")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.work:
        for s, d in WORKS.items():
            print(f"  {s:22} {d['author']}《{d['title_zh']}》 {d['ebook_id']} anchor={d['anchor']}")
    else:
        run(a.work, engine=a.engine, limit=a.limit, upload=a.upload)
