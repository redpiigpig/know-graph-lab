"""Build Uchimura Kanzō (內村鑑三) Aozora Bunko works into reader books.

Uchimura (1861–1930) is public domain worldwide. First wave = the 11 texts
published on Aozora Bunko (person34) — clean digital XHTML, zero OCR. Each core
work = one ebooks row (ja ＋ 繁中 two-column, `sources={"ja":…}`,
`source_order=["ja"]`); the six short essays are bundled into ONE 雜文短篇集 row
(one piece = one section). This is the portal's first Japanese → 繁中 case.
See .claude/skills/ebook-collected-works/uchimura_collected_works.md.

Aozora XHTML quirks handled here (pure functions, locked by
scripts/tests/test_uchimura_build.py):
  - Shift_JIS (cp932) encoding, with utf-8 fallback
  - <ruby> reading annotations stripped (keep rb base text)
  - <span class="notes">［＃…］</span> editor notes dropped
  - gaiji <img alt="…U+XXXX"> → real Unicode char; alt="※(…)" → "※"
  - <h1-6 class="*midashi*"> headings → section boundaries
  - one <br/>-terminated line = one paragraph; leading U+3000 indent stripped
  - <div class="bibliographical_information"> (底本) excluded (outside main_text)

Old-orthography (旧字旧仮名) pieces are fed to the engine as-is per the
case-study md. Cache dir: c:/tmp/uchimura_cache/ (fetched 2026-07-16, throttled).

  python scripts/uchimura_build.py --dry             # parse all, counts only
  python scripts/uchimura_build.py --dry --work denmark-story
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):  # Windows console is cp950
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load .env before importing the engine module (it reads keys at import).
_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

CACHE_DIR = Path("c:/tmp/uchimura_cache")

# ── Registry: 6 ebook rows covering the 11 Aozora texts ──────────────────────
# deterministic namespace d0000000-… (a=印順 b=聖嚴 c=星雲 → d=內村鑑三).
# Mirrored in .claude/skills/ebook-collected-works/uchimura_registry.json.
REGISTRY: dict[str, dict] = {
    "denmark-story": {
        "ebook_id": "d0000000-0000-4000-8000-000000000003",
        "title": "丹麥國的故事",
        "original_title": "デンマルク国の話",
        "subtitle": "以信仰與樹木救國之話（日文原文＋繁中對照）",
        "year": 1911,
        "parent_volume": "講演與信仰文集",
        "files": ["233_43563.html"],
    },
    "how-to-read-bible": {
        "ebook_id": "d0000000-0000-4000-8000-000000000004",
        "title": "聖經的讀法",
        "original_title": "聖書の読方",
        "subtitle": "以來世為背景讀之（日文原文＋繁中對照）",
        "year": 1921,
        "parent_volume": "聖書研究",
        "files": ["1218_18404.html"],
    },
    "short-pieces": {
        "ebook_id": "d0000000-0000-4000-8000-000000000006",
        "title": "雜文短篇集",
        "original_title": "寡婦の除夜‧寒中の木の芽 ほか短篇六篇",
        "subtitle": "青空文庫所收短篇六篇（日文原文＋繁中對照）",
        "year": 1912,
        "parent_volume": "講演與信仰文集",
        # chronological-ish order; each file = one piece = one section
        "files": ["1216_19588.html", "1215_9222.html", "1212_19587.html",
                  "1214_19590.html", "1217_19583.html", "1213_19585.html"],
    },
    "greatest-legacy": {
        "ebook_id": "d0000000-0000-4000-8000-000000000002",
        "title": "給後世的最大遺物",
        "original_title": "後世への最大遺物",
        "subtitle": "一八九四年箱根夏期學校講演（日文原文＋繁中對照）",
        "year": 1897,
        "parent_volume": "講演與信仰文集",
        "files": ["519_43561.html"],
    },
    "consolations": {
        "ebook_id": "d0000000-0000-4000-8000-000000000001",
        "title": "基督信徒的安慰",
        "original_title": "基督信徒のなぐさめ",
        "subtitle": "處女作‧「無教會」一詞初出（日文原文＋繁中對照）",
        "year": 1893,
        "parent_volume": "信仰三部作",
        "files": ["55507_72651.html"],
    },
    "job-lectures": {
        "ebook_id": "d0000000-0000-4000-8000-000000000005",
        "title": "約伯記講演",
        "original_title": "ヨブ記講演",
        "subtitle": "一九二〇年柏木聖書研究會講演（日文原文＋繁中對照）",
        "year": 1925,
        "parent_volume": "聖書研究",
        "files": ["56908_64142.html"],
    },
}

# Translate order: short works first (early wins), the huge Job lectures last.
QUEUE = ["denmark-story", "how-to-read-bible", "short-pieces",
         "greatest-legacy", "consolations", "job-lectures"]


# ── decoding ─────────────────────────────────────────────────────────────────
def decode_aozora(raw: bytes) -> str:
    """Aozora XHTML is Shift_JIS; newer files may be UTF-8. Try utf-8 strictly
    first (cp932 will happily mis-decode utf-8 bytes, not vice versa)."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp932", errors="replace")


# ── parsing ──────────────────────────────────────────────────────────────────
_GAIJI_U_RE = re.compile(r"U\+([0-9A-Fa-f]{4,6})")
_MIDASHI_MARK = "␟"  # ␟ unit separator — internal heading marker


def _gaiji_char(alt: str) -> str:
    """gaiji <img alt> → text: 'U+8AB6' form → that char; '※(…)' form → '※'."""
    m = _GAIJI_U_RE.search(alt or "")
    if m:
        return chr(int(m.group(1), 16))
    return "※" if (alt or "").startswith("※") else ""


def parse_aozora(html: str) -> dict:
    """Aozora XHTML → {title, subtitle, sections:[{heading, paras}]}.

    One <br/>-terminated line = one paragraph. Headings (class *midashi*) open a
    new section; text before the first heading is the '(front)' section."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.find(class_="title")
    sub_el = soup.find(class_="subtitle")
    title = title_el.get_text(strip=True) if title_el else ""
    subtitle = sub_el.get_text(strip=True) if sub_el else None

    main = soup.find("div", class_="main_text")
    if main is None:
        raise ValueError("no <div class='main_text'> — not an Aozora XHTML?")

    for el in main.find_all(["rt", "rp"]):
        el.decompose()
    for el in main.find_all("span", class_="notes"):
        el.decompose()
    for el in main.find_all("img"):
        el.replace_with(_gaiji_char(el.get("alt", "")))
    for el in main.find_all("br"):
        el.replace_with("\n")
    for el in main.find_all(re.compile(r"^h[1-6]$")):
        cls = " ".join(el.get("class") or [])
        if "midashi" in cls:
            el.replace_with(f"\n{_MIDASHI_MARK}{el.get_text(strip=True)}\n")

    sections: list[dict] = []
    cur: dict | None = None
    for line in main.get_text().split("\n"):
        s = line.strip().strip("　").strip()
        if not s:
            continue
        if s.startswith(_MIDASHI_MARK):
            cur = {"heading": s[1:].strip(), "paras": []}
            sections.append(cur)
            continue
        if cur is None:
            cur = {"heading": "(front)", "paras": []}
            sections.append(cur)
        cur["paras"].append(s)
    return {"title": title, "subtitle": subtitle, "sections": sections}


def split_long_paras(paras: list[str], max_chars: int = 1500) -> list[str]:
    """Split any paragraph longer than max_chars on Japanese sentence boundaries
    (。！？」) so each translate prompt stays bounded and zh rows stay 1:1."""
    out: list[str] = []
    for p in paras:
        if len(p) <= max_chars:
            out.append(p)
            continue
        parts = re.split(r"(?<=[。！？」])", p)
        buf = ""
        for part in parts:
            if buf and len(buf) + len(part) > max_chars:
                out.append(buf)
                buf = part
            else:
                buf += part
        if buf:
            out.append(buf)
    return out


def piece_as_section(doc: dict) -> dict:
    """Collapse one short piece (parsed doc) into ONE section headed by the piece
    title; internal headings are inlined as `## ` body lines."""
    paras: list[str] = []
    for s in doc["sections"]:
        if s["heading"] != "(front)":
            paras.append(f"## {s['heading']}")
        paras.extend(s["paras"])
    return {"heading": doc["title"], "paras": paras}


def load_work_sections(slug: str, cache_dir: Path = CACHE_DIR) -> list[dict]:
    """Registry slug → [{heading, paras}] ready for translation. Multi-file works
    (short-pieces) yield one section per piece; single-file works keep their own
    heading structure. Long paragraphs are split; headings keep the raw Aozora
    text (translated later as section titles)."""
    w = REGISTRY[slug]
    secs: list[dict] = []
    for fname in w["files"]:
        doc = parse_aozora(decode_aozora((cache_dir / fname).read_bytes()))
        if len(w["files"]) > 1:
            secs.append(piece_as_section(doc))
        else:
            secs.extend(doc["sections"])
    return [{"heading": s["heading"], "paras": split_long_paras(s["paras"])}
            for s in secs]


# ── translation engine (prod only) ───────────────────────────────────────────
UCHIMURA_PROMPT_TMPL = """你是明治—大正時代日本基督教文獻的專業譯者，正在翻譯內村鑑三（Uchimura Kanzō）的著作。把下列**日文原文**（文語與口語混合體，可能含舊字舊假名）翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯日文原文；不要加任何前言、說明或註解。
3. 語域：典雅但可讀的現代繁體中文書面語，保留講演體的呼告與反問語氣；文語聖句可譯為半文言。
4. 保留 Markdown（## 標題等）。聖經人名、地名、書卷名依和合本慣例（ヨブ→約伯、パウロ→保羅、ロマ書→羅馬書、エレミヤ→耶利米）。
5. 術語鎖死：無教会（主義）→無教會（主義）、贖罪→贖罪、（基督の）再臨→再臨、復活→復活、十字架→十字架、聖書→聖經（唯誌名《聖書之研究》保留原名）、神→神、イエス‧キリスト→耶穌‧基督、聖霊→聖靈、福音→福音、預言者→先知、使徒→使徒、信者→信徒、教会→教會、恩恵→恩典、艱難→患難、来世→來世、永生→永生、デンマルク→丹麥、ネルソン→納爾遜、後世への最大遺物→給後世的最大遺物。
6. 只輸出翻譯後的繁體中文。

日文原文：
{source}"""


def make_engine(backend: str = "auto"):
    """translate_para(ja)->zh using the unified Gemini→NVIDIA→Haiku chain from
    translate_ebook_to_zh, with the Uchimura prompt. Mirrors panikkar_build."""
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = UCHIMURA_PROMPT_TMPL

    def _clean(out: str) -> str:
        # one ja paragraph → exactly ONE zh paragraph (keep row counts equal);
        # a genuine `## ` heading line passes through untouched.
        out = out.replace("�", "").replace("﻿", "")  # NVIDIA 偶發雜訊字元
        if out.strip().startswith("## "):
            return re.sub(r"\s*\n\s*", " ", out.strip())
        out = re.sub(r"(?m)^\s*#{1,6}\s.*$", "", out)
        return re.sub(r"\s*\n\s*", " ", out).strip()

    def translate_para(ja: str) -> str:
        src = (ja or "").strip()
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
            return te.gemini_with_nvidia_fallback(piece)  # unified default chain

        out = ""
        for _ in range(4):  # retry-on-empty
            out = _clean(" ".join(translate_piece(p) for p in pieces))
            if out:
                return out
        return out

    return translate_para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="parse + counts only, no LLM")
    ap.add_argument("--work", type=str, default=None)
    args = ap.parse_args()
    slugs = [args.work] if args.work else QUEUE
    for slug in slugs:
        secs = load_work_sections(slug)
        w = REGISTRY[slug]
        total = sum(len(s["paras"]) for s in secs)
        print(f"{slug:20} {w['title']:12} sections={len(secs):3} paras={total:4}")
        if args.dry and args.work:
            for i, s in enumerate(secs):
                print(f"  sec{i} 「{s['heading'][:28]}」 ¶={len(s['paras'])}")


if __name__ == "__main__":
    main()
