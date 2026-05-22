#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衛報第 55 期結構化 OCR — 每頁輸出 JSON 描述標題/作者/欄位/段落。

來源：public/herald/55/page-02.jpg .. page-23.jpg
輸出：public/herald/55/data/page-02.json .. page-23.json
"""
import json
import re
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
IMG_DIR = REPO / "public" / "herald" / "55"
DATA_DIR = IMG_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

env: dict[str, str] = {}
for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"')

KEYS: list[str] = []
for n in [""] + [f"_{i}" for i in range(1, 11)]:
    for base in ("Gemini_API_Key", "GEMINI_API_KEY"):
        v = env.get(f"{base}{n}")
        if v and v not in KEYS:
            KEYS.append(v)
if not KEYS:
    sys.exit("ERROR: 找不到 GEMINI_API_KEY")

from google import genai
from google.genai import types

PROMPT = """這是雜誌《衛報 Wesleyan News》第 55 期內頁掃描照片。
請完整辨識頁面上所有中文／英文／數字，並以下列 JSON 格式輸出（**不要有 markdown 圍欄，純 JSON**）。
全部用繁體中文（簡體一律轉繁）。標點全形。

JSON 欄位（所有欄位都列出來；沒有的填空字串或空陣列）：

{
  "running_header": "文化取向的宣教 國度視野的牧養",  // 頁眉，整本期固定，可省略
  "section_marker": "",        // 頁面最上方的大段落標題，例如「四、衛理宗消息」「二、崇拜資源」「六、衛蘭專文」；置中、有橫線分隔
  "eyebrow": "",                // 小標題（在大標題上方的引文式短句），例如「根植傳統 回應當代」
  "title": "",                  // 文章主標題（最大字級）；例如「聯合衛理公會評論：對於全球愛滋病危機，約翰衛斯理會怎麼作？」「將臨節期」「經課介紹」
  "subtitle_en": "",            // 英文副標題（若有），例如「Commentary: What would Wesley do about global AIDS?」
  "author": "",                 // 作者/譯者署名行，例如「By Donald E. Messer 牧師* / 龐文翰 譯」「謝敏蘭」「衛報編輯群」
  "date_line": "",              // 日期行，例如「2002 年 12 月 1 日 將臨節第一主日」；若文章開頭有
  "scripture_ref": "",          // 經課經文行（如「賽 64:1-9; 詩 80:1-7、17-19; 林前 1:3-9; 可 13:24-37」），若有
  "columns": 1,                 // 主體文字排版欄位數：1 或 2（看頁面主體是單欄還是雙欄；上半單欄下半雙欄者以雙欄為主）
  "blocks": [                   // 主體內容，依視覺順序
    { "type": "subsection", "text": "經課綱要" },     // 段內小標題（粗體、置中或左對齊都歸為 subsection）
    { "type": "paragraph",  "text": "段落純文字…" },  // 一般段落（同段內視覺斷行請合併成一行）
    { "type": "separator" },                          // *** 或 ──── 等分隔列
    { "type": "blockquote", "text": "引述段落" },     // 縮排引文（少用）
    { "type": "scripture_attribution", "text": "—— 路加福音 10:25-37" }  // 經文末尾右對齊出處
  ]
}

要求：
1. 同一段落內視覺斷行請合併成一行（不要把長句斷成多行）。
2. 標題、副標題、作者署名、日期行不要塞進 blocks，要分別填到對應欄位。
3. blocks 不要含頁眉（running_header）或頁尾頁碼／日期戳記（例「2002-11-30」「24」）。
4. 圖片裡桌面、鍵盤雜物全部忽略；圖片下方的圖說也忽略（如果是小段獨立圖說就跳過）。
5. 不確定的欄位填空字串，不要瞎猜。
6. JSON 之外不要有任何其他文字。
"""


def ocr_one(img: Path, key_idx: int = 0) -> dict:
    client = genai.Client(api_key=KEYS[key_idx])
    img_bytes = img.read_bytes()
    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )
    raw = (resp.text or "").strip()
    # Strip ```json ... ``` fences if any
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # Strip unescaped control characters that break json.loads (CR/LF/TAB inside strings, etc.)
    raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", raw)
    # Replace literal newlines inside strings (Gemini sometimes emits \n raw rather than escaped)
    # but preserve newlines outside strings — easier: just remove them entirely; JSON ignores whitespace
    raw = raw.replace("\r", "").replace("\n", " ")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try with json-repair if available
        try:
            import json_repair
            return json_repair.loads(raw)
        except Exception:
            raise


def main() -> None:
    files = sorted([p for p in IMG_DIR.glob("page-*.jpg") if 2 <= int(p.stem.split("-")[1]) <= 23])
    print(f"OCR {len(files)} 頁 → {DATA_DIR}")
    key_idx = 0
    for i, img in enumerate(files, 1):
        out = DATA_DIR / f"{img.stem}.json"
        if out.exists() and out.stat().st_size > 50:
            print(f"  [{i}/{len(files)}] {img.name} 已存在，跳過")
            continue

        success = False
        for round_no in range(8):
            for _ in range(len(KEYS)):
                try:
                    data = ocr_one(img, key_idx)
                    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"  [{i}/{len(files)}] {img.name} ✓ "
                          f"title={(data.get('title') or '')[:20]} "
                          f"cols={data.get('columns')} blocks={len(data.get('blocks') or [])}", flush=True)
                    success = True
                    time.sleep(3)
                    break
                except Exception as e:
                    msg = str(e)[:200]
                    if any(s in msg for s in ("429", "quota", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")):
                        key_idx = (key_idx + 1) % len(KEYS)
                        time.sleep(3)
                    else:
                        print(f"  [{i}/{len(files)}] {img.name} ✗ {msg}", flush=True)
                        time.sleep(5)
                        break
            if success:
                break
            wait_s = 70
            print(f"    all keys throttled, wait {wait_s}s (round {round_no+1}/8)", flush=True)
            time.sleep(wait_s)
        if not success:
            print(f"  [{i}/{len(files)}] {img.name} ✗ stop after 8 rounds", flush=True)
            break


if __name__ == "__main__":
    main()
