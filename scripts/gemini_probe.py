"""Gemini 生成額度探針：exit 0 = 至少一把 key 能真的產生內容（額度已恢復）；
exit 1 = 全部 key × 全部候選模型都 429/quota（尚未恢復）。

注意：不能用 models.list 之類端點探——那只驗 auth，額度乾時照樣 200。
必須送一次極小的 generateContent，看是否真能生成。

🚨 免費層日配額 2026-08 已被 Google 砍到 `GenerateRequestsPerDayPerProjectPerModel
-FreeTier = 20`（每 key 每模型每天 20 次）。但**配額是「每模型」獨立計算**，所以某個模型
乾掉不代表 Gemini 乾掉——換一個模型就有新的 20 次。本探針因此改為掃 MODELS 清單，找到第一個
還有額度的模型後把它印在 stdout 第一行（`MODEL=xxx`），呼叫端（fleet_keeper.ps1）據此設定
GEMINI_MODEL 再啟動實際的 worker。全部模型皆為已驗證可讀中文掃描頁的 vision 模型。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import os
import requests
from dotenv import load_dotenv
load_dotenv()

import translate_ebook_to_zh as te  # noqa: E402

# 依 OCR 品質排序；每個模型有各自獨立的日配額，前面乾了就往下換。
# 2026-08-17 實測：全部都能正確讀出中文掃描頁的字。
MODELS = [m for m in (
    os.environ.get("GEMINI_MODEL"),          # 顯式指定者優先
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
) if m]
BODY = {"contents": [{"parts": [{"text": "reply with: ok"}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 5}}
MODEL_FILE = Path(__file__).resolve().parent / "state" / "gemini_live_model.txt"


def main() -> int:
    keys = te.GEMINI_KEYS
    if not keys:
        print("no gemini key", file=sys.stderr)
        return 1
    seen = set()
    for model in MODELS:
        if model in seen:
            continue
        seen.add(model)
        base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for i, key in enumerate(keys):
            try:
                r = requests.post(f"{base}?key={key}", json=BODY, timeout=30)
            except requests.exceptions.RequestException as e:
                print(f"{model} key#{i} conn-err {type(e).__name__}", file=sys.stderr)
                continue
            if r.status_code == 200:
                print(f"MODEL={model}")          # stdout 第一行＝呼叫端要用的模型
                # 同時落檔：PS 5.1 讀原生指令的 stdout 有 ErrorRecord 包裝的雷，讀檔最穩。
                MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
                MODEL_FILE.write_text(model, encoding="ascii")
                print(f"{model} key#{i} ALIVE", file=sys.stderr)
                return 0
            print(f"{model} key#{i} {r.status_code}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
