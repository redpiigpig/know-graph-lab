#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""數位化本地「訪談錄」書頁照片 → 逐頁繁中全文（通用版，引擎 = Haiku 4.5 vision）。

泛化自 ocr_huimin.py，給多本法鼓山系訪談錄共用（惠敏《六十感恩紀》、
李志夫《浮塵掠影》…）。逐頁存 <out>/<stem>.txt，冪等可 --resume。

轉錄政策（依使用者）：從頁面有意義小標起、殘句可省略、逐字、保留印刷頁碼【頁 N】。

  python -X utf8 scripts/ocr_interview_book.py --src "<folder>" --out "<dir>" \
      --title "浮塵掠影：李志夫先生訪談錄" [--limit N] [--resume] [--pace 0.5]
"""
import argparse
import base64
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dadaodao_fulltext import anthropic_client, _is_quota

HAIKU = "claude-haiku-4-5"
PROMPT_TMPL = (
    "這是《{title}》的一張書頁照片。請完整轉錄頁面中的繁體中文文字，作為研究參考資料。\n"
    "要求：\n"
    "1. 大致從頁面上**有意義的小標題**開始轉錄；上一頁／上一段被切斷的殘句可省略。\n"
    "2. 逐字轉錄，保留段落與標題結構；不要翻譯、不要摘要、不要加任何說明或評論。\n"
    "3. **忽略頁面中的照片／插圖及其圖說（圖片標註文字）**，只轉錄正文。\n"
    "4. 若頁面看得到**印刷頁碼**，在最前面用「【頁 N】」標出；看不到頁碼就寫「【頁 ?】」。\n"
    "5. 若該頁整頁是照片、版權頁或無正文，就只輸出「【頁 ?】（無正文）」。\n"
    "只輸出轉錄文字（含開頭的頁碼標記），不要任何前言。"
)


def ocr_image(path: Path, prompt: str) -> str:
    b64 = base64.standard_b64encode(path.read_bytes()).decode()
    client = anthropic_client()
    msg = client.messages.create(
        model=HAIKU, max_tokens=8000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--pace", type=float, default=0.5)
    args = ap.parse_args()

    src, out = Path(args.src), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    prompt = PROMPT_TMPL.format(title=args.title)
    imgs = sorted(src.glob("*.jpg"))
    print(f"{len(imgs)} photos in {src.name}", flush=True)
    done = fail = strikes = 0
    for i, img in enumerate(imgs):
        dst = out / f"{img.stem}.txt"
        if args.resume and dst.exists() and dst.read_text(encoding="utf-8").strip():
            continue
        try:
            text = ocr_image(img, prompt)
            strikes = 0
            dst.write_text(text, encoding="utf-8")
            done += 1
            head = text.splitlines()[0] if text else ""
            print(f"  ✓ [{i+1}/{len(imgs)}] {img.name} → {len(text)} chars  {head[:36]}", flush=True)
            if args.limit and done >= args.limit:
                break
            time.sleep(args.pace)
        except Exception as e:  # noqa: BLE001
            if _is_quota(e):
                strikes += 1
                print(f"  ⏸ quota strike {strikes}/2 — {img.name}", flush=True)
                if strikes >= 2:
                    print("\n2-strike 停機；--resume 可接續。", flush=True)
                    break
                time.sleep(20)
            else:
                fail += 1
                print(f"  ✗ {img.name}: {type(e).__name__}: {str(e)[:160]}", flush=True)
    print(f"\nDONE — ocr {done}, failed {fail}; output → {out}", flush=True)


if __name__ == "__main__":
    main()
