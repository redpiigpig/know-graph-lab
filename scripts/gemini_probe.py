"""Gemini 生成額度探針：exit 0 = 至少一把 key 能真的產生內容（額度已恢復）；
exit 1 = 全部仍 429/quota（尚未恢復）。

注意：不能用 models.list 之類端點探——那只驗 auth，額度乾時照樣 200。
必須送一次極小的 generateContent，看是否真能生成。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
from dotenv import load_dotenv
load_dotenv()

import translate_ebook_to_zh as te  # noqa: E402

MODEL = "gemini-2.5-flash"
BODY = {"contents": [{"parts": [{"text": "reply with: ok"}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 5}}


def main() -> int:
    keys = te.GEMINI_KEYS
    if not keys:
        print("no gemini key", file=sys.stderr)
        return 1
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    for i, key in enumerate(keys):
        try:
            r = requests.post(f"{base}?key={key}", json=BODY, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"key#{i} conn-err {type(e).__name__}", file=sys.stderr)
            continue
        if r.status_code == 200:
            print(f"key#{i} ALIVE")
            return 0
        print(f"key#{i} {r.status_code}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
