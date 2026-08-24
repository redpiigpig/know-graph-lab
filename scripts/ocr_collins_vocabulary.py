#!/usr/bin/env python3
"""Recover Collins's vocabulary order from the back Latin-English Vocabulary.

The primer's per-unit vocabulary lists are scattered across thirty-five
sections, but its back matter already collects every one of them into a single
alphabetical list whose entries each carry the unit that introduced the word --
``ambo, ambonis, m. lectern, ambo (15)``.  Twenty-eight pages therefore hold the
whole curriculum order, and reading them is both cheaper and less error-prone
than stitching thirty-five sections back together.

What the pages cannot give up is the macrons.  The PDF's own text layer renders
``orare`` for ``orare``-with-macrons and turns final long o into d, b or 0
(``oro`` arrives as ``ord``, ``impono`` as ``impend``), which would poison every
principal part in the reader.  So the pages are re-read as images and the text
layer is kept only as an independent check on which entries exist.

Each page is cached as JSON on arrival, so a quota stop resumes rather than
restarts.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k = k.strip().lstrip("﻿")
            v = v.strip().strip("'\"")
            if k and k not in os.environ:
                os.environ[k] = v

sys.path.insert(0, str(ROOT / "scripts"))
from ocr_with_gemini import _find_gemini_keys  # type: ignore

import fitz  # type: ignore
from google import genai  # type: ignore
from google.genai import types  # type: ignore

import original_reader_llm as llm  # type: ignore

API_KEYS = _find_gemini_keys()
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

FENCE = chr(96) * 3
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full" / "collins-pages"

# Printed pp. 411-438; the PDF's front matter offsets them by seventeen.
FIRST_PAGE = 428
LAST_PAGE = 455

PROMPT = """這是 John F. Collins《A Primer of Ecclesiastical Latin》(CUA Press) 書末
"Latin-English Vocabulary" 的一頁掃描影像。版面為左右兩欄，請先讀完左欄再讀右欄。

每一條詞目的格式是：拉丁詞形（動詞為四個主要部分、名詞為主格＋屬格＋性、形容詞為三性詞尾）、
詞類或用法括號、英文釋義、最後一個括號內是該詞首次出現的 unit 編號。
例：`ambo, ambonis, m. lectern, ambo (15)`；`accuso, accusare, accusavi, accusatus accuse (E20)`。

**長音符號（macron）極為重要**：本書所有長母音都標了上橫線（ā ē ī ō ū ȳ），
請逐字看清影像並精確保留，不要用文字層的拼法，不要自行補上或省略任何 macron。

請輸出 JSON 陣列，每個元素一條詞目，欄位：
  "headword"  第一個拉丁詞形（含 macron）
  "forms"     完整的詞形部分，逗號分隔原樣照抄（含 macron）；若只有一個詞形就重複 headword
  "gram"      括號內的詞類／用法標記，沒有就空字串
  "gloss"     英文釋義原樣照抄
  "unit"      整數 unit 編號；若標記為 E 開頭（僅出現於習題）填 "E<數字>" 字串
  "under"     若該條是縮排列在某個簡單動詞底下的複合動詞，填那個簡單動詞的 headword，否則空字串

規則：
1. 只輸出 JSON 陣列本身，不要 markdown 圍欄、不要任何說明文字。
2. 跨行、跨欄斷開的詞條要接回成完整一條。
3. 頁首的 running header（如 "414 LATIN-ENGLISH VOCABULARY"）不是詞條，略過。
4. 一條詞目若標了兩個 unit 編號（例 `(1); by (the agency of) (7)`），unit 填第一個，
   釋義照抄完整。
5. 看不清楚的字元寧可照影像逐字寫出，不要用常識補字。
"""


def render(pdf: fitz.Document, idx: int, max_dim: int = 2400) -> bytes:
    page = pdf.load_page(idx)
    zoom = max_dim / max(page.rect.width, page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return pix.tobytes("png")


def ocr(png: bytes) -> list[dict]:
    """Sweep every key once; a single live key is enough.

    The two-strike quota rule governs whole sweeps, not individual keys.  Seven
    keys are shared with the overnight fleet, so on any given night most of them
    answer 429 or 503 while one or two still work; aborting on the second key's
    429 would stop a run that had a live lane two keys further down.
    """
    last = None
    for key in API_KEYS:
        for attempt in range(2):
            try:
                client = genai.Client(api_key=key)
                resp = client.models.generate_content(
                    model=MODEL,
                    contents=[types.Part.from_bytes(data=png, mime_type="image/png"), PROMPT],
                    config=types.GenerateContentConfig(temperature=0.0),
                )
                text = (resp.text or "").strip()
                if text.startswith("```"):
                    text = text.split(chr(10), 1)[-1]
                if text.endswith("```"):
                    text = text.rsplit(chr(10), 1)[0]
                text = text.strip()
                return json.loads(text)
            except json.JSONDecodeError as exc:
                last = exc
                continue
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                last = exc
                if "503" in msg or "UNAVAILABLE" in msg:
                    time.sleep(3)
                    continue
                break
    raise QuotaSweep(f"整輪金鑰都不通：{last}")


ANTHROPIC_MODELS = ("claude-sonnet-5", "claude-haiku-4-5-20251001")


def ocr_anthropic(png: bytes) -> list[dict]:
    """Second tier, used when every Gemini key is spoken for.

    Seven Gemini keys are shared with the overnight fleet and on a busy night
    all seven answer 429 or 503 at once.  The page still has to be read, and
    the macrons are the whole point of re-reading it, so the fallback is a
    vision model rather than the PDF text layer.
    """
    import base64

    payload = base64.standard_b64encode(png).decode("ascii")
    last = None
    for model in ANTHROPIC_MODELS:
        for attempt in range(3):
            try:
                resp = llm.client().messages.create(
                    model=model,
                    max_tokens=16000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": payload,
                                    },
                                },
                                {"type": "text", "text": PROMPT},
                            ],
                        }
                    ],
                )
                text = "".join(b.text for b in resp.content if b.type == "text").strip()
                if text.startswith(FENCE):
                    text = text.split(chr(10), 1)[-1]
                if text.endswith(FENCE):
                    text = text.rsplit(chr(10), 1)[0]
                return json.loads(text.strip())
            except Exception as exc:  # noqa: BLE001
                last = exc
                if "429" in str(exc) or "overloaded" in str(exc).lower():
                    time.sleep(20)
                    continue
                break
    raise QuotaSweep(f"Anthropic 也不通：{last}")


class QuotaSweep(RuntimeError):
    """Every key failed on one page; two of these in a row stops the run."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--first", type=int, default=FIRST_PAGE)
    ap.add_argument("--last", type=int, default=LAST_PAGE)
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    wanted = list(range(args.first, args.last + 1))
    done = {int(p.stem.split("-")[-1]) for p in CACHE.glob("page-*.json")}
    if args.status:
        print(f"cached {len(done)}/{len(wanted)}；缺 {sorted(set(wanted) - done)}")
        return

    pdf = fitz.open(args.pdf)
    sweeps = 0
    for idx in wanted:
        if idx in done:
            continue
        try:
            png = render(pdf, idx)
            try:
                entries = ocr(png)
            except QuotaSweep:
                entries = ocr_anthropic(png)
        except QuotaSweep as exc:
            sweeps += 1
            print(f"page {idx}: {exc}", flush=True)
            if sweeps >= 2:
                print("連兩頁整輪失敗，依規範退出", flush=True)
                return
            time.sleep(30)
            continue
        sweeps = 0
        (CACHE / f"page-{idx:03d}.json").write_text(
            json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"page {idx}: {len(entries)} 條", flush=True)
        time.sleep(1.0)
    print("完成")


if __name__ == "__main__":
    main()
