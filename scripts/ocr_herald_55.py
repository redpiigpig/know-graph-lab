#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 衛報第 55 期 22 個內頁掃描 → 繁體純文字。

來源：public/herald/55/page-02.jpg .. page-23.jpg
輸出：public/herald/55/text/page-02.txt .. page-23.txt
"""
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
IMG_DIR = REPO / "public" / "herald" / "55"
TXT_DIR = IMG_DIR / "text"
TXT_DIR.mkdir(exist_ok=True)

# ── .env ──
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

from google import genai  # type: ignore
from google.genai import types  # type: ignore

PROMPT = """這是一份雜誌《衛報 Wesleyan News》第 55 期的內頁掃描照片。
請把整頁中文字逐字 OCR 成 **繁體中文** 純文字輸出。

要求：
1. 只輸出文字內容，不要任何說明、不要 markdown 圍欄。
2. 保留段落分行。同一段落內請合併成一行（不要把長句斷成多行）。
3. 標題、小標題單獨成行。
4. 如果頁面有條列或編號，照原樣保留（「一、」「二、」「(1)」「1.」等）。
5. 頁尾頁碼、日期戳記（例如「2002-11-30」「24」）不要輸出。
6. 簡體字一律轉繁體。標點用全形。
7. 圖片裡桌面、鍵盤等雜物完全忽略。
8. 如果掃描內容只有空白頁或無法辨識，輸出空字串即可。
"""


def ocr_one(img: Path, key_idx: int = 0) -> str:
    client = genai.Client(api_key=KEYS[key_idx])
    img_bytes = img.read_bytes()
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            PROMPT,
        ],
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return (resp.text or "").strip()


def main() -> None:
    files = sorted([p for p in IMG_DIR.glob("page-*.jpg") if 2 <= int(p.stem.split("-")[1]) <= 23])
    print(f"OCR {len(files)} 頁，輸出 → {TXT_DIR}")
    key_idx = 0
    for i, img in enumerate(files, 1):
        out = TXT_DIR / f"{img.stem}.txt"
        if out.exists() and out.stat().st_size > 0:
            print(f"  [{i}/{len(files)}] {img.name} 已存在，跳過")
            continue
        # Try each key; if all 4 keys hit quota, wait 70s and try again (free tier RPM resets per minute)
        success = False
        for round_no in range(6):  # up to 6 rounds × 4 keys = up to ~7 min
            for _ in range(len(KEYS)):
                try:
                    text = ocr_one(img, key_idx)
                    out.write_text(text, encoding="utf-8")
                    print(f"  [{i}/{len(files)}] {img.name} ✓ {len(text)} chars", flush=True)
                    success = True
                    time.sleep(3)
                    break
                except Exception as e:
                    msg = str(e)[:200]
                    if "429" in msg or "quota" in msg.lower() or "RESOURCE_EXHAUSTED" in msg or "503" in msg:
                        key_idx = (key_idx + 1) % len(KEYS)
                        time.sleep(3)
                    else:
                        print(f"  [{i}/{len(files)}] {img.name} ✗ {msg}", flush=True)
                        time.sleep(5)
                        break
            if success:
                break
            wait_s = 70
            print(f"    all keys quota’d, wait {wait_s}s then retry (round {round_no+1}/6)", flush=True)
            time.sleep(wait_s)
        if not success:
            print(f"  [{i}/{len(files)}] {img.name} ✗ stop after 6 rounds", flush=True)
            break


if __name__ == "__main__":
    main()
