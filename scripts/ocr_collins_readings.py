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
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full" / "collins-readings"

# The Ordinary of the Mass, printed pp. 328-334.
FIRST_PAGE = 345
LAST_PAGE = 351

PROMPT = """這是 John F. Collins《A Primer of Ecclesiastical Latin》(CUA Press) 書末
"Further Readings" 的一頁掃描影像，內容是拉丁文的禮儀或教父文本。

請把整頁的拉丁正文逐行抄出來，保持原有的分段與對答結構。

規則：
1. 主祭與會眾的對答用原書的記號：主祭句前用 V.，會眾答句前用 R.。
   原書若印成 y. 或 X.（掃描誤形），一律還原為 V.。
2. 方括號內的拉丁文是禮儀動作指示（rubrica），照抄並保留方括號。
3. 章節或段落標題（如 LITURGIA VERBI、Prex Eucharistica III）獨立成行照抄。
4. 長音符號若有請保留；本頁多半不標長音，沒有就不要自行加。
5. 頁首頁尾的書名、頁碼、running header 一律略去。
6. 註腳號碼與註腳文字略去。
7. 不要翻譯、不要解釋、不要 markdown 圍欄。

輸出 JSON 物件：{"lines": [每行一個字串]}，不要任何其他文字。
"""


def render(pdf: fitz.Document, idx: int, max_dim: int = 2400) -> bytes:
    page = pdf.load_page(idx)
    zoom = max_dim / max(page.rect.width, page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return pix.tobytes("png")


def ocr(png: bytes) -> dict:
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


def ocr_anthropic(png: bytes) -> dict:
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
        print(f"page {idx}: {len(entries.get('lines', []))} 行", flush=True)
        time.sleep(1.0)
    print("完成")


if __name__ == "__main__":
    main()
