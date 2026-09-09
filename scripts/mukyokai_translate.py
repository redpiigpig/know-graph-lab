# -*- coding: utf-8 -*-
"""把無教會 collection 裡的日文研究論文做成「逐段對照」的全文。

為什麼要有這一支：collection 收的日文研究（赤江達也、呉敬姫、佐藤明…）現在只有
原文，讀者要自己啃日文。頁面（pages/research-data/mukyokai/index.vue）是單欄展開
純文字，所以對照不必改前端——把「原文段＋繁中段」交錯寫進同一份 txt 就成。

三個步驟，前兩個是純函式（測試鎖在 scripts/tests/test_mukyokai_translate.py）：

  1. paragraphs_from_pdf  版面幾何還原段落。J-STAGE 那批 2000 年代掃描本的文字層
     是舊 OCR：**同一個視覺行會被拆成好幾個片段**（括號一來就斷），所以要先按 y
     把片段併回一行，再看行首 x0——縮排（≥ INDENT_X）＝新段落，齊頭＝續行。
     直接用 get_text() 逐行讀會把一段切成幾十段。
  2. clean_ocr  這批 OCR 有一組固定誤字（もとつく／漢発／震署／答め…），字形相近
     而且會反覆出現。不修的話譯文會跟著錯，而且錯得很通順。
  3. 翻譯走既有的 Gemini→NVIDIA→Haiku 鏈（translate_ebook_to_zh），checkpoint 落
     c:/tmp/mukyokai_tr/<stem>.json，斷了可續跑。

  python -X utf8 scripts/mukyokai_translate.py --pdf C:/tmp/akae2004_fukei.pdf \
      --stem akae-2004-fukei --dry            # 只看分段結果
  python -X utf8 scripts/mukyokai_translate.py --pdf … --stem … --run
  python -X utf8 scripts/mukyokai_translate.py --stem … --emit   # 出對照 txt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CACHE = Path("c:/tmp/mukyokai_tr")

# 行首縮排門檻（實測：續行 x0≈50、段落首行 x0≈60，一個 8pt 全形字約 9px）
INDENT_X = 57.0
BODY_SIZE_MIN = 6.5          # 正文 8.0、註釋 7.0 都要（赤江最關鍵的判斷在註 16）；書眉 6.0 濾掉
SAME_LINE_TOL = 3.0          # y 差在這個範圍內視為同一視覺行


# ── 1. 版面幾何 → 段落 ───────────────────────────────────────────────────────
def visual_lines(page_dict: dict, size_min: float = BODY_SIZE_MIN) -> list[tuple[float, str]]:
    """一頁的 dict → [(行首 x0, 整行文字)]，已把 OCR 拆碎的片段按 y 併回。"""
    frags = []
    for b in page_dict.get("blocks", []):
        for l in b.get("lines", []):
            spans = [s for s in l.get("spans", []) if s.get("text", "").strip()]
            if not spans:
                continue
            if max(s["size"] for s in spans) < size_min:
                continue
            frags.append((round(l["bbox"][1], 1), l["bbox"][0],
                          "".join(s["text"] for s in spans)))
    frags.sort(key=lambda f: (f[0], f[1]))
    out: list[tuple[float, str]] = []
    for y, x0, txt in frags:
        if out and abs(y - out[-1][0]) <= SAME_LINE_TOL:
            out[-1] = (out[-1][0], out[-1][1], out[-1][2] + txt)
        else:
            out.append((y, x0, txt))
    return [(x0, txt) for _y, x0, txt in out]


_PAGENUM = re.compile(r"^[\s0-9０-９\-—―]+$")


def paragraphs_from_lines(lines: list[tuple[float, str]]) -> list[str]:
    """[(x0, 行)] → 段落。縮排＝新段落；純數字行（頁碼）丟掉。"""
    paras: list[str] = []
    for x0, txt in lines:
        t = txt.strip()
        if not t or _PAGENUM.match(t):
            continue
        if x0 >= INDENT_X or not paras:
            paras.append(t)
        else:
            paras[-1] += t
    return [p for p in paras if p.strip()]


_TERMINAL = ("。", "！", "？", "」", "』", "）", ")", "…", "―", "：", ":")


def heal(paras: list[str]) -> list[str]:
    """跨頁換段是假的：上一段沒有句末標點就把這一段接上去。

    段落首行的縮排在換頁處判不出來（新的一頁一律從版心起算），而且 OCR 偶爾把
    正文中段的行首讀得偏右。不接回去的話，一段會被切成兩段送進引擎，譯出來的
    後半會缺主詞——而且讀起來完全正常，不會被任何驗證抓到。"""
    out: list[str] = []
    for p in paras:
        if out and not out[-1].rstrip().endswith(_TERMINAL):
            out[-1] += p
        else:
            out.append(p)
    return out


def paragraphs_from_pdf(path: str | Path) -> list[str]:
    import fitz
    doc = fitz.open(str(path))
    paras: list[str] = []
    for pno in range(doc.page_count):
        paras.extend(paragraphs_from_lines(visual_lines(doc[pno].get_text("dict"))))
    doc.close()
    return heal(paras)


# ── 2. OCR 誤字 ─────────────────────────────────────────────────────────────
# 🚨 只收「字形相近且在本文脈絡下不可能是原字」的。寧可漏也不可錯殺——
#    例如「出張」在別的文章裡是真詞（出差），這裡只因與「主張」成對出現才收。
OCR_FIXES = [
    ("もとつく", "もとづく"), ("もとつい", "もとづい"),
    ("漢発", "渙発"), ("震署", "宸署"),
    ("良心の答め", "良心の咎め"), ("答めは", "咎めは"),
    ("はじある", "はじめる"),
    ("内村鑑―三", "内村鑑三"), ("内村鑑―", "内村鑑三"),
    ("―・学期", "一学期"), ("―・連", "一連"), ("―・高", "一高"),
    ("讃美", "讃美"),
    ("中途半4端", "中途半端"),
    ("戦懐", "戦慄"),
    ("ギリスト教", "キリスト教"),
    ("矛4先", "矛先"),
    ("ユ3", "13"),
]


def clean_ocr(text: str) -> str:
    t = text or ""
    for a, b in OCR_FIXES:
        t = t.replace(a, b)
    t = re.sub(r"\]0(?=\s|$)", "]。", t)          # 引用括號後的「。」被讀成 0
    t = re.sub(r"[ \t\u3000]+", "", t)             # OCR 在詞中插的空白
    return t.strip()


# ── 3. 翻譯 ────────────────────────────────────────────────────────────────
PROMPT_TMPL = """你是日文學術論文的中譯者。把下面這段社會學論文的日文譯成**繁體中文**。

規矩：
- 只輸出譯文本身，不要加說明、不要加標題、不要重述原文。
- 學術用語按既有中譯慣例：不敬事件、教育敕語、御真影、可拜論／非拜論、
  無教會、組合教會（公理會）、日本基督一致教會（長老派）、愛國心、國體。
- 人名地名照漢字原樣：內村鑑三、植村正久、井上哲次郎、小崎弘道、木村駿吉。
- 書名與雜誌名用《》，引號用「」。
- 文獻引註（如 [鈴木1993a:79-80]）原樣保留，不要翻譯也不要刪。
- 原文若是節標題（如「1-はじめに」），就只譯標題本身。
- 這段是舊 OCR 的產物，可能有殘字；照語意通順地譯，不要因此拒譯或說明。

日文原文：
{source}"""


def make_engine(backend: str = "auto"):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = PROMPT_TMPL

    def translate_para(ja: str) -> str:
        src = (ja or "").strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)

        def one(piece: str) -> str:
            if backend == "haiku":
                return te.haiku_translate(piece)
            if backend == "gemini":
                return te.gemini_translate(piece)
            if backend == "nvidia":
                return te.nvidia_translate(piece)
            return te.gemini_with_nvidia_fallback(piece)

        for _ in range(4):
            out = " ".join(one(p) for p in pieces).strip()
            out = re.sub(r"\s+", " ", out.replace("\u3000", ""))
            if out:
                return out
        return ""

    return translate_para


def cp_path(stem: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / f"{stem}.json"


def run(stem: str, paras: list[str], backend: str, limit: int | None) -> None:
    p = cp_path(stem)
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    src = data.get("src") or paras
    zh = (list(data.get("zh") or []) + [None] * len(src))[:len(src)]
    engine = make_engine(backend)
    todo = [i for i in range(len(src)) if not zh[i]]
    if limit:
        todo = todo[:limit]
    print(f"{stem}: 共 {len(src)} 段，待譯 {len(todo)} 段", flush=True)
    for n, i in enumerate(todo, 1):
        zh[i] = engine(src[i])
        if True:  # 每段都存：NVIDIA 一段要十幾秒，逾時被砍就全丟了
            p.write_text(json.dumps({"src": src, "zh": zh}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
            print(f"  {n}/{len(todo)}", flush=True)
    p.write_text(json.dumps({"src": src, "zh": zh}, ensure_ascii=False, indent=1),
                 encoding="utf-8")
    done = sum(1 for z in zh if z)
    print(f"完成 {done}/{len(src)}")


def emit(stem: str, header: str = "") -> str:
    """checkpoint → 逐段對照純文字（原文段在上、繁中在下，空行分段）。"""
    data = json.loads(cp_path(stem).read_text(encoding="utf-8"))
    out = [header.strip(), ""] if header.strip() else []
    for a, b in zip(data["src"], data["zh"]):
        out.append(a)
        out.append(f"【中譯】{b}" if b else "【中譯】（未譯）")
        out.append("")
    return "\n".join(out).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf")
    ap.add_argument("--stem", required=True)
    ap.add_argument("--dry", action="store_true", help="只印分段結果")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--backend", default="auto",
                    choices=["auto", "gemini", "nvidia", "haiku"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--header", default="")
    args = ap.parse_args()

    paras: list[str] = []
    if args.pdf:
        paras = [clean_ocr(x) for x in paragraphs_from_pdf(args.pdf)]
        paras = [p for p in paras if len(p) > 1]

    if args.dry:
        print(f"段落數 {len(paras)}，字數 {sum(len(p) for p in paras):,}")
        for i, p in enumerate(paras[:12]):
            print(f"--- [{i}] {len(p)} 字\n{p[:200]}")
        return
    if args.run:
        run(args.stem, paras, args.backend, args.limit)
        return
    if args.emit:
        print(emit(args.stem, args.header))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
