# -*- coding: utf-8 -*-
"""千面上帝寫作用的 Gemini 呼叫器。

金鑰池沿用 translate_ebook_to_zh.GEMINI_KEYS（七把輪流）。模型固定 gemini-3.5-flash
——免費層拿不到 pro（全部 429，2026-09-05 實測），3.5-flash 是七把 key 都通的最好一檔。

兩種呼叫：
  ask(prompt)              純生成
  ask(prompt, search=True) 掛 Google Search grounding，用來查最新研究
"""
import json
import os
import random
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import translate_ebook_to_zh as engines  # noqa: E402

# 🚨 免費層是「每天每把 key 幾次請求」在管，不是每分鐘。2026-09-05 實測：
#    gemini-3.5-flash / 3.6-flash → GenerateRequestsPerDayPerProjectPerModel-FreeTier = 20
#    七把 key 合起來一天才 140 次，而一章要 ~15 次，整套書排不進一天。
#    gemini-2.5-flash 是穩定版、額度大得多，整套書要在一夜跑完只能走它。
#    要換型號設環境變數 QIANMIAN_MODEL。
MODEL = os.environ.get("QIANMIAN_MODEL", "gemini-2.5-flash")
URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"

_index = 0


def ask(prompt, *, search=False, temperature=0.85, max_tokens=32768, tries=None):
    """呼叫 Gemini，回 (文字, 出處清單)。出處只有 search=True 時才有東西。"""
    global _index
    keys = engines.GEMINI_KEYS
    if not keys:
        raise RuntimeError("找不到 Gemini API key")

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    if search:
        body["tools"] = [{"google_search": {}}]

    last = "?"
    for attempt in range(tries or len(keys) * 3):
        key = keys[_index % len(keys)]
        _index += 1
        try:
            r = requests.post(URL.format(m=MODEL), params={"key": key}, json=body, timeout=600)
        except requests.exceptions.RequestException as e:
            last = f"conn {type(e).__name__}"
            continue
        if r.status_code == 200:
            cands = r.json().get("candidates") or []
            if not cands:
                last = "no candidates"
                continue
            parts = cands[0].get("content", {}).get("parts") or []
            text = "".join(p.get("text", "") for p in parts).strip()
            if not text:
                last = f"empty text (finish={cands[0].get('finishReason')})"
                continue
            gm = cands[0].get("groundingMetadata") or {}
            srcs = [c.get("web", {}).get("title", "") for c in gm.get("groundingChunks", [])]
            return text, [s for s in srcs if s]
        last = f"HTTP {r.status_code}"
        if r.status_code in (429, 503, 500):
            time.sleep(min(60, 3 * (attempt + 1)) + random.random() * 2)
            continue
        if r.status_code == 400:
            raise RuntimeError(f"Gemini 400：{r.text[:300]}")
    raise RuntimeError(f"Gemini 全數失敗，最後：{last}")


def ask_json(prompt, **kw):
    """要求 JSON 輸出，容忍 ```json 圍欄。"""
    text, _ = ask(prompt, **kw)
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    start = min((i for i in (t.find("{"), t.find("[")) if i >= 0), default=0)
    return json.loads(t[start:])
