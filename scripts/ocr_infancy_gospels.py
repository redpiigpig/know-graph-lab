"""把《基督教典外文獻》新約篇第 1 冊裡兩篇嬰孩福音重 OCR。

    python scripts/ocr_infancy_gospels.py --doc infancy-arabic --dry-run
    python scripts/ocr_infancy_gospels.py --doc infancy-arabic

🚨 為什麼要重 OCR：那四冊 PDF 確實有文字層，但那層本身是壞掉的 OCR
   （「阿倫德爾抄本404」讀成「間偏德爾砂m 404 個」、「摘錄」成「摘鋒」）。
   有文字層不等於文字層能用。

🚨 原書印刷頁碼必須留下來：每頁的書眉／頁腳帶著真頁碼（原書頁 110–132、
   150–154），OCR 之後要對回去，絕不可用流水號冒充。

引擎：Gemini Vision（gemini-flash-latest），多 key 輪流。連兩次 429 自動退場，
不在夜裡把整個免費額度燒光。
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
for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip().lstrip("\ufeff"), v.strip().strip("'\""))
sys.path.insert(0, str(ROOT / "scripts"))
from ocr_with_gemini import _find_gemini_keys  # noqa: E402

import fitz  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

DOCS = {
    "infancy-arabic": {"pdf": "C:/tmp/apocrypha-ocr/infancy-arabic.pdf",
                       "title": "阿拉伯語耶穌嬰孩時期福音", "printed_from": 110, "printed_to": 132},
    "infancy-latin": {"pdf": "C:/tmp/apocrypha-ocr/infancy-latin.pdf",
                      "title": "拉丁語耶穌嬰孩時期福音（阿倫德爾抄本404）", "printed_from": 150, "printed_to": 154},
}

PROMPT = """這是一本繁體中文學術書的一頁（《基督教典外文獻・新約篇》）。請把整頁正文逐字轉錄成繁體中文純文字。

規則：
1. 只回傳正文。書眉（如「第二部分：卷五 阿拉伯語耶穌嬰孩時期福音」「基督教典外文獻——新約篇」）一律刪去。
2. 頁碼單獨一行放在最前面，格式 `#PAGE:<數字>`。頁碼在頁面左上或右上角，是阿拉伯數字。找不到就寫 `#PAGE:?`。
3. 保留段落分行；保留章節號（如「一」「1」「第一章」）與經文小節編號。
4. 保留頁底的註腳，另起一行以 `#NOTE:` 開頭，一條一行。
5. 不要加任何說明、標題或 markdown 記號。不要翻譯，不要改寫，不要補字。
6. 原文若有缺損符號（〔〕［］……）照原樣保留。"""


def render(pdf: Path, i: int) -> bytes:
    doc = fitz.open(pdf)
    page = doc[i]
    scale = min(2000 / page.rect.width, 2000 / page.rect.height, 3.0)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    png = pix.tobytes("png")
    doc.close()
    return png


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, choices=list(DOCS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rpm", type=float, default=6.0)
    a = ap.parse_args()

    cfg = DOCS[a.doc]
    pdf = Path(cfg["pdf"])
    if not pdf.exists():
        sys.exit(f"找不到 {pdf}")
    n = fitz.open(pdf).page_count
    expect = cfg["printed_to"] - cfg["printed_from"] + 1
    print(f"{cfg['title']}：{n} 頁（原書頁 {cfg['printed_from']}–{cfg['printed_to']}，應為 {expect} 頁）")
    if n != expect:
        print(f"⚠️ 頁數與原書頁範圍不符（{n} vs {expect}），仍繼續，稍後以 #PAGE 對回")

    if a.dry_run:
        print("--dry-run：不呼叫 API")
        return

    keys = _find_gemini_keys()
    print(f"Gemini keys {len(keys)} 把，模型 gemini-flash-latest")
    out_dir = Path("C:/tmp/apocrypha-ocr") / a.doc
    out_dir.mkdir(parents=True, exist_ok=True)

    quota_streak = 0
    results = []
    for i in range(n):
        dst = out_dir / f"{i:03d}.txt"
        if dst.exists():
            results.append(dst.read_text(encoding="utf-8"))
            print(f"  p{i + 1:>3}  略過（已有）")
            continue
        png = render(pdf, i)
        txt, err = None, None
        for ki in range(len(keys)):
            key = keys[(i + ki) % len(keys)]
            try:
                c = genai.Client(api_key=key)
                r = c.models.generate_content(
                    model="gemini-flash-latest",
                    contents=[types.Part.from_bytes(data=png, mime_type="image/png"), PROMPT],
                )
                txt = (r.text or "").strip()
                break
            except Exception as ex:  # noqa: BLE001
                err = str(ex)
                if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                    continue
                break
        if txt is None:
            quota_streak += 1
            print(f"  p{i + 1:>3}  ✗ {(err or '')[:90]}")
            # 🚨 連兩次配額失敗就退場，不把整晚的免費額度燒光
            if quota_streak >= 2:
                print("\n✗ 連續兩次配額失敗，依規矩退場。已完成的頁留在 " + str(out_dir))
                sys.exit(2)
            continue
        quota_streak = 0
        dst.write_text(txt, encoding="utf-8")
        results.append(txt)
        m = re.search(r"#PAGE:(\S+)", txt)
        body = re.sub(r"^#(PAGE|NOTE):.*$", "", txt, flags=re.M).strip()
        print(f"  p{i + 1:>3}  原書頁 {m.group(1) if m else '?':>4}　{len(body):>4} 字　{body[:38]}")
        time.sleep(60.0 / a.rpm)

    print(f"\n完成 {len(results)} / {n} 頁 → {out_dir}")


if __name__ == "__main__":
    main()
