#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Migne《希臘教父學大全》(PG) 掃描本的希臘欄 OCR 成文字，供教父卷第三欄使用。

  python scripts/fathers_pg_ocr.py --pdf c:/tmp/pg48.pdf --first 103 --last 171 \
         --out c:/tmp/pg48_desacerdotio.jsonl
  python scripts/fathers_pg_ocr.py ... --limit 4        # 試跑
  python scripts/fathers_pg_ocr.py ... --status         # 只看進度

為什麼要自己 OCR：金口若望的希臘原典沒有免費的機讀本。First1KGreek 沒收（tlg2062
不在裡面）、Patristic Text Archive 只有偽金口若望、希臘 Wikisource 幾乎空的、
Myriobiblos 只有零星幾篇、earlychurchtexts 的希臘全文要訂閱。剩下的只有 Migne 的
頁面掃描。

🚨 archive.org 附的 OCR 不能用。那份是整卷用希臘模式跑的：καί 有 70% 被讀成 χαὶ，
   連 Google 的英文版權頁都被寫成希臘字母，相異詞／總詞數比高達 37%（乾淨希臘文
   約 10–15%）。

🚨 整頁一次送給 Gemini 也不行。實測會進重複迴圈——同一個子句反覆輸出、節號全掉，
   而且輸出讀起來像通順的希臘文，比明顯的亂碼更難察覺。**必須切成單欄的一半**，
   用全解析度送。切了之後同一頁就正常：29 行全不重複、καὶ 零誤讀、節號保住。

🚨 PG 是希臘、拉丁對照排版，而且不是簡單的奇偶交錯——PG 48 是「兩頁希臘、兩頁
   拉丁」輪替。所以不靠頁碼推，一律用文字層的希臘虛詞密度判（拉丁頁得 0–2 分、
   希臘頁得 100 分以上，分得很開）。
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

import fitz
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ai", ROOT / "scripts" / "dazangjing_catalog_ai.py")
AI = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AI)


# ── 希臘頁判別 ──────────────────────────────────────────────────────────────
# 文字層是整卷用希臘模式 OCR 的，拉丁頁也是希臘字母，所以字元集判不出來。
# 去掉音調後數希臘虛詞才分得開。
STOPWORDS = {"και", "γαρ", "τον", "την", "των", "του", "τους", "προς", "δε",
             "ουκ", "εστι", "θεου", "αυτου", "ταυτα", "μεν", "ουν", "ημας", "τω", "εις"}
GREEK_RUN = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff\\]+")


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def greek_score(text: str) -> int:
    """該頁文字層裡希臘虛詞的個數。希臘正文頁 100+，拉丁頁 0–2。"""
    n = 0
    for w in GREEK_RUN.findall(text):
        if strip_accents(w).lower().replace("\\", "") in STOPWORDS:
            n += 1
    return n


# ── 版面切割 ────────────────────────────────────────────────────────────────
# 頁首書眉與頁底的校勘註釋（小字，橫跨整頁）都要切掉；剩下的兩欄各切上下兩半。
# 半欄是實測可行的最大單位：整頁送會讓模型進重複迴圈。
HEADER = 0.055
FOOTER = 0.90
COLUMNS = ((0.050, 0.497), (0.503, 0.950))
# 上下兩半留 1.5% 重疊，免得剛好切在一行字中間把那一行弄丟；接稿時再去重。
HALVES = ((0.000, 0.515), (0.500, 1.000))


def crops(page: fitz.Page, dpi: int) -> list[tuple[str, bytes]]:
    im = Image.open(io.BytesIO(page.get_pixmap(dpi=dpi).tobytes("png")))
    w, h = im.size
    top, bot = h * HEADER, h * FOOTER
    span = bot - top
    out = []
    for ci, (x0, x1) in enumerate(COLUMNS):
        for hi, (y0, y1) in enumerate(HALVES):
            box = (int(w * x0), int(top + span * y0), int(w * x1), int(top + span * y1))
            buf = io.BytesIO()
            im.crop(box).save(buf, "JPEG", quality=93)
            out.append((f"c{ci}h{hi}", buf.getvalue()))
    return out


PROMPT = """這是 Migne《希臘教父學大全》一欄希臘原文的一半。逐字轉錄成多音調希臘文。

規矩：
1. 逐行照抄。行末的連字號要接回原詞（把被拆開的字接起來）。
2. 段首若有希臘數字節號（如 α΄. β΄. ζ΄.），原樣保留。
3. 若出現 ΛΟΓΟΣ ΠΡΩΤΟΣ、ΟΜΙΛΙΑ Δ΄ 這類標題，獨立成行保留。
4. 方括號裡的欄號（如 [58]）原樣保留。
5. κ 與 χ、β 與 δ、ν 與 υ 不可混淆。
6. 若出現字級明顯較小的校勘註釋（apparatus criticus），整段略過。
7. **只轉錄你確實看得見的文字。看不清就跳過那一行，絕對不要重複前面的句子來湊字數。**
8. 只輸出希臘文，不要任何說明。"""


def ocr(img: bytes, keys: list[str], cursor: dict) -> tuple[str, str] | None:
    """Gemini Vision，金鑰與模型輪替。回傳 (文字, 用了哪個模型)。"""
    from google import genai
    from google.genai import types

    models = ("gemini-flash-latest", "gemini-2.5-flash")
    n = len(keys)
    for attempt in range(n * len(models)):
        ki = (cursor.get("key", 0) + attempt // len(models)) % n
        model = models[attempt % len(models)]
        try:
            client = genai.Client(api_key=keys[ki])
            r = client.models.generate_content(
                model=model,
                contents=[types.Part.from_bytes(data=img, mime_type="image/jpeg"), PROMPT],
            )
            text = (r.text or "").strip()
            if text:
                cursor["key"] = ki
                return text, model
        except Exception as e:                                       # noqa: BLE001
            msg = str(e)[:60]
            if "RESOURCE_EXHAUSTED" not in msg and "429" not in msg:
                print(f"      key#{ki} {model}: {msg}")
    return None


# ── 品質閘 ──────────────────────────────────────────────────────────────────
def looks_degenerate(text: str) -> str | None:
    """整頁送時出現過的失敗模式：同一句反覆輸出。回傳原因，沒問題回 None。

    這一關非有不可。重複迴圈的輸出是通順的希臘文，貼進第三欄看起來完全正常，
    只有讀得懂希臘文的人才會發現同一段話講了五遍。
    """
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 12]
    if len(lines) < 6:
        return None
    uniq = len(set(lines)) / len(lines)
    if uniq < 0.75:
        return f"重複率過高（相異行僅 {uniq:.0%}）"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--first", type=int, required=True, help="起始 PDF 頁（0-based）")
    ap.add_argument("--last", type=int, required=True)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--limit", type=int, help="這一輪最多做幾個裁切")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()

    AI.load_dotenv()
    out = Path(a.out)
    done: dict[str, dict] = {}
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[f"{r['page']}:{r['crop']}"] = r

    doc = fitz.open(a.pdf)
    pages = [p for p in range(a.first, a.last + 1)
             if greek_score(doc[p].get_text()) >= 25]
    todo = [(p, c) for p in pages for c in ("c0h0", "c0h1", "c1h0", "c1h1")
            if f"{p}:{c}" not in done]
    print(f"頁 {a.first}–{a.last} 中希臘正文 {len(pages)} 頁 → 裁切 {len(pages) * 4} 塊；"
          f"已完成 {len(done)}，待做 {len(todo)}")
    if a.status:
        return 0

    keys = AI.env_keys(("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    if not keys:
        print("找不到 GEMINI_API_KEY")
        return 1
    print(f"金鑰 {len(keys)} 把")

    cursor: dict[str, int] = {}
    if a.limit:
        todo = todo[: a.limit]
    written = failed = 0
    cache: dict[int, dict[str, bytes]] = {}
    with out.open("a", encoding="utf-8") as fh:
        for page, crop in todo:
            if page not in cache:
                cache = {page: dict(crops(doc[page], a.dpi))}
            got = ocr(cache[page][crop], keys, cursor)
            if not got:
                print(f"  p{page} {crop} ✗ 所有金鑰皆失敗（多半是配額）")
                failed += 1
                continue
            text, model = got
            bad = looks_degenerate(text)
            if bad:
                print(f"  p{page} {crop} ⊘ 丟棄：{bad}")
                failed += 1
                continue
            fh.write(json.dumps({"page": page, "crop": crop, "model": model,
                                 "text": text}, ensure_ascii=False) + "\n")
            fh.flush()
            written += 1
            print(f"  p{page} {crop} ✓ {len(text):5} 字 ({model})")
    print(f"\n本輪寫入 {written}，失敗 {failed}；累計 {len(done) + written} / {len(pages) * 4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
