"""Create concise Traditional-Chinese working glosses for the 1,000-word Hebrew reader.

The authoritative ordering, pointed headwords, and Pratico–Van Pelt
transliteration stay in ``hebrew-1000.json``.  This script only generates a
separate editorial Chinese-gloss layer.  It uses the local Ollama service, so
no authorized textbook data leaves the computer.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-1000.json"
OUTPUT = (
    ROOT
    / "output"
    / "source-cache"
    / "original-readers"
    / "hebrew-full"
    / "hebrew-1000-gloss-zh.json"
)
MODEL = "qwen2.5:7b"
BATCH_SIZE = 5
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def request_batch(batch: list[dict]) -> list[dict]:
    compact = [
        {
            "ordinal": item["ordinal"],
            "hebrew": item["pointed"],
            "glossEn": item.get("glossEn", ""),
            "partOfSpeech": item.get("partOfSpeech", ""),
            "properNameTypes": item.get("properNameTypes", []),
        }
        for item in batch
    ]
    prompt = f"""你是聖經希伯來文詞典編輯。把下列 {len(compact)} 筆英語詞義譯成精簡、準確的繁體中文詞典義。

規則：
1. 只回傳一個 JSON 物件，格式必須是 {{\"items\":[{{\"ordinal\":1,\"glossZh\":\"……\"}}]}}。
2. 筆數、ordinal 與輸入完全相同，順序不變，不得遺漏或增加。
3. 一般詞保留主要義與必要分義，用「；」分隔，通常不超過 24 個中文字。
4. 人名、地名、民族名、神名採繁體中文聖經慣用譯名；若同一詞兼有普通義，兩義都保留。
5. 不翻譯希伯來字形，不評論音譯，不加入 Strong 編號，不寫任何 JSON 外文字。

輸入：
{json.dumps(compact, ensure_ascii=False, separators=(',', ':'))}
"""
    payload = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "keep_alive": "30m",
            "options": {
                "temperature": 0.05,
                "num_ctx": 4096,
                "num_predict": 700,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=240) as response:
        envelope = json.loads(response.read().decode("utf-8"))
    parsed = json.loads(envelope["response"])
    items = parsed.get("items") if isinstance(parsed, dict) else None
    if not isinstance(items, list):
        raise ValueError("model response has no items array")
    expected = [item["ordinal"] for item in batch]
    actual = [item.get("ordinal") for item in items]
    if actual != expected:
        raise ValueError(f"ordinal mismatch: expected {expected}, got {actual}")
    for item in items:
        gloss = item.get("glossZh")
        if not isinstance(gloss, str) or not gloss.strip():
            raise ValueError(f"empty Chinese gloss at ordinal {item.get('ordinal')}")
        item["glossZh"] = gloss.strip()
    return items


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    vocabulary = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(vocabulary) != 1000:
        raise SystemExit(f"expected 1000 vocabulary items, got {len(vocabulary)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    completed: dict[int, dict] = {}
    if OUTPUT.exists():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))
        completed = {int(item["ordinal"]): item for item in prior.get("items", [])}

    pending = [
        item for item in vocabulary if int(item["ordinal"]) not in completed
    ]
    for start in range(0, len(pending), BATCH_SIZE):
        batch = pending[start : start + BATCH_SIZE]
        for attempt in range(1, 4):
            try:
                translated = request_batch(batch)
                completed.update({int(item["ordinal"]): item for item in translated})
                ordered = [completed[i] for i in sorted(completed)]
                OUTPUT.write_text(
                    json.dumps(
                        {
                            "schemaVersion": 1,
                            "language": "zh-Hant",
                            "status": "editorial-working-gloss",
                            "model": MODEL,
                            "items": ordered,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                print(
                    f"translated ordinals {batch[0]['ordinal']:04d}-{batch[-1]['ordinal']:04d} "
                    f"({len(completed)}/1000)",
                    flush=True,
                )
                break
            except (ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError) as error:
                if attempt == 3:
                    raise
                print(
                    f"retry {attempt}/3 for ordinals "
                    f"{batch[0]['ordinal']}-{batch[-1]['ordinal']}: {error}",
                    flush=True,
                )
                time.sleep(attempt * 2)

    if sorted(completed) != list(range(1, 1001)):
        raise SystemExit("Chinese gloss layer is incomplete")
    print(OUTPUT)


if __name__ == "__main__":
    main()
