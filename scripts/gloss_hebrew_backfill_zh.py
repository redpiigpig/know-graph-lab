#!/usr/bin/env python3
"""Write Traditional-Chinese working glosses for vocabulary that has none yet.

The reader's gloss layer is keyed by ``(strong, pointed)`` so it survives a
re-ordering of the word list.  This script finds the entries in
``hebrew-1000.json`` that key into nothing, glosses only those, and merges the
result back.  Everything already reviewed is left untouched.

Engine chain follows the project default: Gemini first, NVIDIA next, and the
run stops rather than shipping a blank or an English gloss.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data/originalReaders/vocabulary/hebrew-1000.json"
GLOSSES = ROOT / "output/source-cache/original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json"
CACHE = ROOT / "output/source-cache/original-readers/hebrew-full/gloss-backfill-cache.json"
ENV_FILE = ROOT / ".env"

ENV: dict[str, str] = {}
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            ENV[key.strip()] = value.strip().strip('"').strip("'")


NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "deepseek-ai/deepseek-v4-flash-0731"


def nvidia_keys() -> list[str]:
    keys, seen = [], set()
    for index in range(1, 11):
        for name in (f"NVIDIA_API_Key_{index}", f"NVIDIA_API_KEY_{index}"):
            value = os.environ.get(name) or ENV.get(name)
            if value and value not in seen:
                seen.add(value)
                keys.append(value)
    single = os.environ.get("NVIDIA_API_KEY") or ENV.get("NVIDIA_API_KEY")
    if single and single not in seen:
        keys.append(single)
    return keys


def gemini_keys() -> list[str]:
    names = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    raw: list[str] = []
    for name in names:
        value = os.environ.get(name) or ENV.get(name)
        if value:
            raw.append(value)
            break
    for index in range(1, 11):
        for name in names:
            value = os.environ.get(f"{name}_{index}") or ENV.get(f"{name}_{index}")
            if value:
                raw.append(value)
                break
    keys, seen = [], set()
    for item in raw:
        for piece in item.split(","):
            key = piece.strip()
            if key and key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


PROMPT = """你在替一本《聖經希伯來文讀本》編寫詞彙表的繁體中文詞義。

每個詞給你附點原形、BBH2 音標、詞性與 Strong 詞典的英文釋義。請為每個詞寫出精簡的繁體中文詞義。

規則：
- 只輸出繁體中文，不得出現英文、簡體字、拼音、希伯來字母。
- 用分號「；」分隔多個義項，最多三個義項，由主要義排到次要義。
- 全長控制在 12 個字以內，是詞典式的詞義，不是句子，不加標點結尾。
- 動詞寫動作本身（例：「聆聽；聽從」），名詞寫事物本身（例：「城牆；圍牆」）。
- 專有名詞若確實是人名地名，用《和合本修訂版》通行譯名。
- 不要解釋、不要加註、不要輸出任何額外文字。

只輸出 JSON 物件，鍵是每筆的 id，值是繁體中文詞義：

{{"id1": "詞義", "id2": "詞義"}}

要翻的詞：
{payload}
"""

BAD_CHARS = re.compile(r"[A-Za-z֐-׿]")


def _post_json(url: str, body: dict, headers: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json", **headers}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse(text: str) -> dict[str, str]:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M)
    data = json.loads(text)
    return {k: v.strip() for k, v in data.items() if isinstance(v, str) and v.strip()}


def _payload(items: list[dict]) -> str:
    return json.dumps(
        [
            {
                "id": item["id"],
                "pointed": item["pointed"],
                "translit": item["textbookTransliteration"],
                "pos": item["partOfSpeech"],
                "en": item["glossEn"],
            }
            for item in items
        ],
        ensure_ascii=False,
        indent=1,
    )


def call_gemini(model: str, key: str, items: list[dict]) -> dict[str, str]:
    """Gemini over REST.

    The gRPC SDK retries a quota rejection until the process is killed, which is
    how an earlier run sat blocked for hours; REST surfaces the 429 immediately
    so the caller can rotate keys or fall back.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    data = _post_json(
        url,
        {
            "contents": [{"parts": [{"text": PROMPT.format(payload=_payload(items))}]}],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"},
        },
        {},
        90,
    )
    return _parse(data["candidates"][0]["content"]["parts"][0]["text"])


def call_nvidia(key: str, items: list[dict]) -> dict[str, str]:
    data = _post_json(
        NVIDIA_URL,
        {
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": PROMPT.format(payload=_payload(items))}],
            "temperature": 0.0,
            "max_tokens": 4096,
        },
        {"Authorization": f"Bearer {key}"},
        600,
    )
    return _parse(data["choices"][0]["message"]["content"])


def gloss_batch(model: str, items: list[dict], skip_gemini: bool = False) -> dict[str, str]:
    """Gemini first, NVIDIA next; raise only when every key is exhausted."""

    for index, key in enumerate([] if skip_gemini else gemini_keys()):
        try:
            return call_gemini(model, key, items)
        except Exception as error:  # noqa: BLE001
            print(f"    Gemini key#{index + 1} 失敗：{str(error)[:90]}", flush=True)
    for index, key in enumerate(nvidia_keys()):
        try:
            return call_nvidia(key, items)
        except Exception as error:  # noqa: BLE001
            print(f"    NVIDIA key#{index + 1} 失敗：{str(error)[:90]}", flush=True)
            time.sleep(5)
    raise RuntimeError("Gemini 與 NVIDIA 的金鑰都失敗")


def main() -> None:
    parser = argparse.ArgumentParser(description="替尚無繁中義的希伯來詞彙補上詞義")
    parser.add_argument("--model", default="gemini-flash-latest")
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--skip-gemini", action="store_true", help="配額用盡時直接走 NVIDIA")
    args = parser.parse_args()

    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    gloss_doc = json.loads(GLOSSES.read_text(encoding="utf-8"))
    known = {(item["strong"], item["pointed"]) for item in gloss_doc["items"]}
    missing = [item for item in vocab if (item["strong"], item["pointed"]) not in known]
    print(f"  缺繁中義 {len(missing)} 筆")
    if not missing:
        return
    for item in missing:
        item["id"] = f"{item['strong']}|{item['pointed']}"

    if not gemini_keys() and not nvidia_keys():
        print("[ERR] 找不到 GEMINI_API_KEY 或 NVIDIA_API_Key_N", file=sys.stderr)
        sys.exit(1)

    # Each finished batch is cached, because a run that loses an hour of engine
    # calls to one interruption has to start the whole list over otherwise.
    results: dict[str, str] = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if results:
        print(f"  快取已有 {len(results)} 筆")
    for index in range(0, len(missing), args.batch):
        chunk = [item for item in missing[index : index + args.batch] if item["id"] not in results]
        if not chunk:
            continue
        try:
            results.update(gloss_batch(args.model, chunk, args.skip_gemini))
        except RuntimeError as error:
            print(f"[ERR] {error}", file=sys.stderr)
            sys.exit(1)
        CACHE.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"    {min(index + args.batch, len(missing))}/{len(missing)}", flush=True)
        time.sleep(2)

    rejected = []
    for item in missing:
        value = results.get(item["id"], "")
        if not value or BAD_CHARS.search(value) or len(value) > 16:
            rejected.append((item["id"], value))
    if rejected:
        for key, value in rejected:
            print(f"    退回 {key} -> {value!r}")
        print(f"[ERR] {len(rejected)} 筆詞義不合格", file=sys.stderr)
        sys.exit(1)

    for item in missing:
        print(f"  {item['pointed']:<12} {results[item['id']]}   ({item['glossEn'][:44]})")

    if not args.write:
        print("（未寫檔；加 --write 才會合併回註釋層）")
        return

    gloss_doc["items"].extend(
        {"strong": item["strong"], "pointed": item["pointed"], "glossZh": results[item["id"]]}
        for item in missing
    )
    order = {(item["strong"], item["pointed"]): item["ordinal"] for item in vocab}
    gloss_doc["items"].sort(key=lambda item: order.get((item["strong"], item["pointed"]), 10**6))
    GLOSSES.write_text(json.dumps(gloss_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已寫回 {GLOSSES}（共 {len(gloss_doc['items'])} 筆）")


if __name__ == "__main__":
    main()
