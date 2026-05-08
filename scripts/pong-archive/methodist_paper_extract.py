#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract 龐君華會督 articles from 中華衛訊 PDFs using Gemini.

Reads pre-extracted text from tmp_methodist/text/{NN}.txt, asks Gemini to
identify and clean the 會督的話 / 龐君華 article from each issue, and writes
JSON files to tmp_methodist/articles/{NN}.json.

Usage:
  python scripts/pong-archive/methodist_paper_extract.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from google import genai
from google.genai import types

TEXT_DIR = ROOT / "tmp_methodist" / "text"
OUT_DIR = ROOT / "tmp_methodist" / "articles"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Issues -> (publication date YYYY-MM-DD, issue number)
ISSUES = {
    "105": ("2019-08-01", 105),
    "106": ("2019-10-01", 106),
    "107": ("2019-12-01", 107),
    "108": ("2020-03-01", 108),  # 2020.02-04 combined
    "109": ("2020-06-01", 109),
    "110": ("2020-08-01", 110),
    "111": ("2020-10-01", 111),
    "112": ("2020-12-01", 112),
    "113": ("2022-08-01", 113),
    "114": ("2022-10-01", 114),
    "115": ("2022-12-01", 115),
}

PROMPT = """你會收到一份「中華衛訊」期刊的 PDF 全文（已用 PyMuPDF 抽出，含換行/表格殘留）。

請完成兩件事：
1. 找出本期由「龐君華會督」（或寫成 ◆龐君華 / 龐君華 / 會督的話 等署名）撰寫的「會督的話」社論文章。
2. 把文章內容整理成乾淨可讀的繁體中文逐字稿。

要求：
- 只輸出 JSON，不要任何其他文字。
- JSON schema：{"has_pong_article": bool, "title": string, "subtitle": string|null, "body": string, "notes": string}
- has_pong_article=false 時其他欄位填空字串 / null。
- title：文章標題（不含「會督的話」欄目名）。例如「有真實連結的年議會」、「徹底門徒運動下的蛻變」。
- body：完整文章內文，繁體中文。段落用兩個換行分隔，刪除頁碼/頁眉/欄位殘留/拉出引言重複文字/同一段不要硬斷行。
- 保留原文的小標題與引文標示，標題前後不要加 # 或 markdown。
- notes：一句話說明文章從哪幾頁、識別根據（署名/標題）。

PDF 全文如下：
---
{text}
---
"""


def find_keys() -> list[str]:
    keys = []
    seen = set()
    bases = ["GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY"]
    for base in bases:
        v = os.environ.get(base)
        if v and v not in seen:
            seen.add(v); keys.append(v)
    for n in range(1, 11):
        for base in bases:
            v = os.environ.get(f"{base}_{n}")
            if v and v not in seen:
                seen.add(v); keys.append(v); break
    return keys


def call_gemini(client: genai.Client, model: str, prompt: str) -> dict:
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=16384,
        ),
    )
    raw = resp.text or ""
    try:
        return json.loads(raw)
    except Exception:
        # Try to fix
        try:
            from json_repair import loads as repair_loads
            return repair_loads(raw)
        except Exception:
            print(f"  RAW response (failed to parse): {raw[:600]}", file=sys.stderr)
            raise


def main():
    keys = find_keys()
    if not keys:
        print("[FATAL] No Gemini key found", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(keys)} Gemini key(s)")

    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    key_idx = 0
    for issue, (pub_date, num) in ISSUES.items():
        out_path = OUT_DIR / f"{issue}.json"
        if out_path.exists():
            print(f"[skip] {issue}: already extracted")
            continue
        text_path = TEXT_DIR / f"{issue}.txt"
        if not text_path.exists():
            print(f"[skip] {issue}: no text file")
            continue

        text = text_path.read_text(encoding="utf-8")
        prompt = PROMPT.replace("{text}", text)

        for attempt in range(len(keys)):
            api_key = keys[(key_idx + attempt) % len(keys)]
            try:
                client = genai.Client(api_key=api_key)
                print(f"[issue {issue}] calling {model} (key #{(key_idx + attempt) % len(keys) + 1}/{len(keys)})...")
                data = call_gemini(client, model, prompt)
                key_idx = (key_idx + attempt) % len(keys)  # stick with working key
                # save with metadata
                data["_issue"] = num
                data["_published_date"] = pub_date
                data["_issue_label"] = f"中華衛訊第{num}期"
                out_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"  has_pong={data.get('has_pong_article')}  "
                      f"title={data.get('title','')[:30]}  "
                      f"body_len={len(data.get('body','') or '')}")
                break
            except Exception as e:
                msg = str(e)[:200]
                print(f"  [attempt {attempt+1}] failed: {msg}", file=sys.stderr)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper():
                    time.sleep(2)
                    continue
                else:
                    # Other error — retry with next key after short pause
                    time.sleep(3)
                    continue
        else:
            print(f"[FAIL] all keys exhausted for issue {issue}", file=sys.stderr)

        time.sleep(3)  # be polite

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
