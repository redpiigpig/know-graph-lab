#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摩尼教經典取源管線 —— 逐段對齊後寫成 data/manichaean/sources/text/{slug}.json
（reader 直接吃）。

用法：
    python scripts/manichaean_fetch.py --chinese          # 漢文三經（敦煌）
    python scripts/manichaean_fetch.py --chinese --only xiabuzan
    python scripts/manichaean_fetch.py --list             # 列出已實作的取源

═══════════════ 動它之前先讀完這四件事 ═══════════════

一、**段號照抄，一個字都不要自己發明。**
    摩尼教沒有統一的引用式——原書的章節結構早隨殘片斷了，學界按材料各用各的：
      漢文寫卷    T54n2140_p1270b23   （大正藏冊．經號．頁欄行）
      吐魯番殘卷  M 470 R/ii/1-8      （館藏編號＋葉面＋欄＋行）
      科普特抄本  1 Ke 89.18-24       （抄本頁行號）
    自編段號會讓這裡的每一段都無法被外部引用，**而版面看起來完全正常**。
    這與 [[feedback_pdf_page_number]]「PDF 任何重整流程都要原樣保留 page_number」同理。

二、**漢文藏只出一欄，不要為了湊三欄而「翻譯」。**
    這三部本來就是唐代漢文寫的。把它再譯成現代白話不是對照，是改寫。
    故本管線寫出的漢文 JSON 只填 orig，zh 一律留空，pivot='native-chinese'。
    reader 依 SINGLE_COLUMN_CANON 決定欄數，見 data/manichaean/sources/index.ts。

三、**缺字方框 □ 要原樣保留。**
    敦煌三經是殘卷，CBETA 用 □ 標示無法辨識的字。那是**資料**不是雜訊：
    它標出了這一句殘到什麼程度。任何「清理」都會讓殘卷看起來比實際完整。

四、**本腳本不用 LLM。**
    漢文不需要翻譯；其餘各藏的繁中另走 manichaean_translate.py
    （Gemini → NVIDIA → Haiku，見 [[feedback_engine_nvidia_no_haiku]]）。

═══════════════ 資料從哪來 ═══════════════

漢文三經不必上網抓——**本專案的大正藏語料裡已經有了**：
    T2140  摩尼教下部讚      83 段 / 11,878 字
    T2141A 摩尼光佛教法儀略  40 段 /  1,790 字
    T2141B 波斯教殘經（摩尼教殘經）
CBETA TEI P5 原檔在 CBETA_XML_DIR（預設 C:/tmp/cbeta/xml-p5），
解析走既有的 scripts/tripitaka_cbeta.py，不另寫一套。

其餘各藏的取源（尚未實作，按優先序）：
    ① 東方語文藏 —— IAMS《東方摩尼教選輯》四冊（manichaeism.de，開放取用）
       原文轉寫與英譯逐行並排，是三欄 reader 的理想來源。PDF 需版面切欄。
    ② 敵證藏 —— 奧古斯丁諸書與《阿基勞斯行傳》，本站 /fathers 已有 ANF／NPNF 全文。
    ③ 地中海藏 —— 科普特文校本與英譯幾乎全在版權內，是最大的缺口。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Windows 主控台預設 cp950，印繁中以外的字元（⚠ □ 轉寫符號）會整支掛掉。
# 見 [[feedback_powershell_python_whisper_venv]]：這類環境問題會讓管線「不報錯地壞掉」。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

OUT_DIR = ROOT / "data" / "manichaean" / "sources" / "text"


# ────────────────────────── 純函式：段號解析 ──────────────────────────

# 大正藏行號：T54n2140_p1270b23 → 冊 54、經 2140、頁 1270、欄 b、行 23
#
# 🚨 尾碼 `.2` 不是雜訊，是 CBETA 的正式標記：同一行上起第二段（一行寫完前一段、
#    接著起新段時用）。第一版漏掉它，《下部讚》就從 83 段變成 72 段——
#    而頁面照樣好看，沒有任何地方看得出來少了 11 段。這正是
#    [[feedback_silent_zero_is_a_bug]] 說的那種錯：稽核要印分母。
TAISHO_UID = re.compile(r"^T(\d+)n(\d+[A-Z]?)_p(\d{4})([a-c])(\d{2})(?:\.(\d+))?$")


def parse_taisho_uid(uid: str) -> tuple[str, str] | None:
    """把大正藏行號拆成（頁欄, 行）。拆不開回 None——**不猜、不自編**。

    >>> parse_taisho_uid('T54n2140_p1270b23')
    ('1270b', '23')
    >>> parse_taisho_uid('T54n2140_p1273a23.2')
    ('1273a', '23.2')
    >>> parse_taisho_uid('nonsense') is None
    True
    """
    m = TAISHO_UID.match(uid)
    if not m:
        return None
    _vol, _work, page, col, line, sub = m.groups()
    return f"{page}{col}", (f"{line}.{sub}" if sub else line)


def citation_of(uid: str) -> str:
    """學界引用式。大正藏一律用行號本身當引用座標，不改寫成別的格式。

    >>> citation_of('T54n2140_p1270b23')
    'T54n2140_p1270b23'
    """
    return uid


def is_heading(seg: dict) -> bool:
    """CBETA 標為 head 的段是原卷的篇題（如「讚夷數文　第二疊」），不是正文。
    保留為獨立段並加註，因為那也是寫卷上真實存在的字。"""
    return seg.get("kind") == "head"


def damaged_ratio(text: str) -> float:
    """缺字比例。□ 是 CBETA 標示無法辨識之字的符號。

    >>> damaged_ratio('□□禮稱讚')
    0.4
    >>> damaged_ratio('')
    0.0
    """
    if not text:
        return 0.0
    return text.count("□") / len(text)


# ────────────────────────── 漢文三經 ──────────────────────────

CHINESE_TEXTS: dict[str, dict] = {
    "xiabuzan": {
        "xml": "T/T54/T54n2140.xml",
        "siglum": "T2140（S.2659）",
        "title_zh": "下部讚",
        "title_en": "The Lower Section of the Manichaean Hymns",
        "volume": "dunhuang",
        "orig_source": "《大正新脩大藏經》第 54 冊 No. 2140（底本：敦煌寫卷 S.2659，今藏大英圖書館）；CBETA TEI P5",
        "orig_url": "https://cbetaonline.dila.edu.tw/zh/T2140",
        "en_source": "IAMS《東方摩尼教選輯》第四冊已刊部分讚詞的英譯與帕提亞語／粟特語／回鶻語對照（本站尚未接入）",
        "en_url": "https://www.manichaeism.de/other-resources-2/",
    },
    "yilue": {
        "xml": "T/T54/T54n2141A.xml",
        "siglum": "T2141A（S.3969＋P.3884）",
        "title_zh": "摩尼光佛教法儀略",
        "title_en": "Compendium of the Doctrines and Styles of the Teaching of Mani",
        "volume": "dunhuang",
        "orig_source": "《大正新脩大藏經》第 54 冊 No. 2141A（底本：敦煌寫卷 S.3969，另有 P.3884 可綴合）；CBETA TEI P5",
        "orig_url": "https://cbetaonline.dila.edu.tw/zh/T2141A",
        "en_source": "劉南強（S. N. C. Lieu）英譯，版權內，不作為對照欄底本",
    },
    "canjing": {
        "xml": "T/T54/T54n2141B.xml",
        "siglum": "T2141B（北 8470／BD00256）",
        "title_zh": "摩尼教殘經",
        "title_en": "The Chinese Manichaean Treatise (fragment)",
        "volume": "dunhuang",
        "orig_source": "《大正新脩大藏經》第 54 冊 No. 2141B（題《波斯教殘經》，底本：敦煌寫卷北 8470）；CBETA TEI P5",
        "orig_url": "https://cbetaonline.dila.edu.tw/zh/T2141B",
        "en_source": "劉南強（S. N. C. Lieu）英譯，版權內，不作為對照欄底本",
    },
}

LICENCE_ZH = (
    "原文出自《大正新脩大藏經》(1924–1934)，屬公有領域；"
    "電子文本由中華電子佛典協會 (CBETA) 製作，依其授權條款使用。"
)


def build_chinese(slug: str, spec: dict) -> dict:
    """由 CBETA TEI P5 產出一部漢文經的 reader JSON。"""
    import tripitaka_cbeta as tc  # 延後 import：--list 不必載整個解析器

    path = tc.CBETA_ROOT / spec["xml"]
    if not path.exists():
        raise SystemExit(
            f"找不到 CBETA 原檔：{path}\n"
            f"設 CBETA_XML_DIR 指向 xml-p5 目錄（預設 C:/tmp/cbeta/xml-p5）。")

    _meta, segs, _equivs = tc.parse_work(path.read_text(encoding="utf-8"))

    out_segs: list[dict] = []
    skipped: list[str] = []
    for s in segs:
        uid = s.get("uid") or s.get("seg") or ""
        text = (s.get("sources") or {}).get("lzh", "").strip()
        if not text:
            continue
        parsed = parse_taisho_uid(uid)
        if parsed is None:
            # 🚨 拆不開就不收，也不自編。少一段看得出來，段號錯了看不出來。
            skipped.append(uid or "(no uid)")
            continue
        page_col, line = parsed
        seg: dict = {
            "chapter": page_col,
            "verse": line,
            "ref": citation_of(uid),
            "orig": text,
        }
        if is_heading(s):
            seg["note"] = "原卷篇題"
        d = damaged_ratio(text)
        if d >= 0.10:
            pct = round(d * 100)
            seg["note"] = (seg.get("note", "") + f"　本段殘損嚴重，缺字約 {pct}%（□ 為原卷無法辨識之字）").strip()
        out_segs.append(seg)

    doc = {
        "slug": slug,
        "siglum": spec["siglum"],
        "title_zh": spec["title_zh"],
        "title_en": spec.get("title_en"),
        "canon": "chinese",
        "volume": spec["volume"],
        "script": "chinese",
        "orig_source": spec["orig_source"],
        "orig_url": spec.get("orig_url"),
        "en_source": spec.get("en_source"),
        "en_url": spec.get("en_url"),
        "licence": LICENCE_ZH,
        # 🚨 原文即中文：不譯、不填 zh 欄。見檔首第二條。
        "pivot": "native-chinese",
        "pivot_note": (
            "本篇原文即漢文，單欄原樣呈現，不另譯成現代中文。"
            "缺字方框 □ 為原卷無法辨識之字，照原樣保留——那標出了殘損程度，不是雜訊。"
        ),
        "segments": out_segs,
    }
    if skipped:
        print(f"  ⚠ {slug}：{len(skipped)} 段的行號拆不開，已跳過（不自編段號）：{skipped[:5]}")
    return doc


def cmd_chinese(only: list[str] | None) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = {k: v for k, v in CHINESE_TEXTS.items() if not only or k in only}
    if not targets:
        print(f"無此篇。可選：{', '.join(CHINESE_TEXTS)}")
        return 1
    for slug, spec in targets.items():
        doc = build_chinese(slug, spec)
        dst = OUT_DIR / f"{slug}.json"
        dst.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        chars = sum(len(s["orig"]) for s in doc["segments"])
        dmg = sum(s["orig"].count("□") for s in doc["segments"])
        print(f"✓ {slug:10s} {len(doc['segments']):4d} 段　{chars:6,} 字　"
              f"缺字 {dmg:,}（{dmg / chars * 100:.1f}%）　→ {dst.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="摩尼教經典取源管線")
    ap.add_argument("--chinese", action="store_true", help="建漢文三經（敦煌）")
    ap.add_argument("--only", nargs="*", help="只建指定的 slug")
    ap.add_argument("--list", action="store_true", help="列出已實作的取源")
    a = ap.parse_args()

    if a.list:
        print("已實作：")
        print("  --chinese   漢文三經（敦煌）—— 由本專案既有的 CBETA 大正藏語料建置")
        for k, v in CHINESE_TEXTS.items():
            print(f"      {k:10s} {v['siglum']:22s} {v['title_zh']}")
        print("\n尚未實作（按優先序）：")
        print("  東方語文藏  IAMS《東方摩尼教選輯》四冊 PDF，原文轉寫與英譯逐行並排")
        print("  敵證藏      奧古斯丁諸書與《阿基勞斯行傳》，本站 /fathers 已有全文")
        print("  地中海藏    科普特文校本與英譯幾乎全在版權內，最大的缺口")
        return 0

    if a.chinese:
        return cmd_chinese(a.only)

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
