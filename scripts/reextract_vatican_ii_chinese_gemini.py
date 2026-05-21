"""
Re-extract Vatican II Chinese via Gemini — clean up pdftotext-layout damage.

Strategy:
  1. For each of 16 docs, read /c/tmp/vat2_pdf/{slug}.pdf
  2. pdftotext -layout to raw .txt
  3. Send raw txt to Gemini Flash with a prompt asking for structured markdown
     (## headings, N. paragraphs, [^N]: footnote defs, no preamble/toc/page nums)
  4. Write result to data/creeds/.../vatican-ii/{code}-chinese.txt

Skipped: IM (vatican.va Chinese PDF is broken upstream — Content-Length=0)

Run from project root:
  python scripts/reextract_vatican_ii_chinese_gemini.py [--codes SC,LG,...]
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Reuse the project's gemini key loader.
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
try:
    from ocr_with_gemini import ENV, _find_gemini_keys  # type: ignore
except Exception:
    ENV = {}
    def _find_gemini_keys():
        v = os.environ.get("GEMINI_API_KEY") or os.environ.get("Gemini_API_Key") or ""
        return [k.strip() for k in v.split(",") if k.strip()]

try:
    from google import genai
except ImportError:
    print("pip install google-genai", file=sys.stderr); sys.exit(1)

DOCS = [
    ("SC", "sacrosanctum-concilium"),
    # IM skipped (Vatican PDF Content-Length=0)
    ("LG", "lumen-gentium"),
    ("OE", "orientalium-ecclesiarum"),
    ("UR", "unitatis-redintegratio"),
    ("CD", "christus-dominus"),
    ("PC", "perfectae-caritatis"),
    ("OT", "optatam-totius"),
    ("GE", "gravissimum-educationis"),
    ("NA", "nostra-aetate"),
    ("DV", "dei-verbum"),
    ("AA", "apostolicam-actuositatem"),
    ("DH", "dignitatis-humanae"),
    ("AG", "ad-gentes"),
    ("PO", "presbyterorum-ordinis"),
    ("GS", "gaudium-et-spes"),
]

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = Path("c:/tmp/vat2_pdf")
OUT_DIR = ROOT / "data" / "creeds" / "ecumenical-councils" / "vatican-ii"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = """以下是 vatican.va 中文 PDF 用 pdftotext -layout 抽字的繁體中文文本，排版被破壞、段落被切碎、含有目錄/頁碼/語言切換 nav 噪音。請重新整理為乾淨結構化 markdown 純文字。

嚴格規則：
1. **章節標題**（出現於正文中，如「第一章 通論」「甲、總綱」「乙、禮儀本質是聖統與團體的行為」「壹、緒言」「各種非基督宗教」等中文短句）— 加 `## ` 前綴單獨成行
2. **段落編號**（PDF 中行首的數字，如 1, 2, 3, ..., 130）保留為 `數字.` 前綴 — 例如 `1.`、`2.`、`130.`，**不要寫成 `N. 1` 或 `N.1`**。每段獨立成行，段間空行
3. **段落內被切斷的多行**合併為一段（同段內無換行；段間用空行）
4. **註腳 reference**保留 inline `(1) (2) (3)` 格式（PDF 中是上標數字，破壞後可能變「一( )」「二( )」三( )」這種—請還原為純數字 `(1) (2) (3)`）
5. **註腳定義**（文末 numbered list，通常開頭 `1. Cf...` `2. 同前` `3. Cf. 羅...`）放在 `## Footnotes` 區段下，用 `[^N]: 內容` 格式
6. **移除**：目錄頁、頁眉、頁尾、頁碼（單獨數字一行）、語言切換 nav row `[ AR - BE - CS - ... ]`、文件 metadata 重複（如「梵蒂岡第二屆大公會議文獻」「教宗公佈令」「天主眾僕之僕，保祿主教...」可保留一次或移除）
7. **不要翻譯**，不要新增任何 commentary，只重整繁體中文文本
8. **保留段落順序與編號**，不可重新編號
9. **不要包裝**輸出於 ``` 區塊內，直接輸出純 markdown

輸入：
---
{raw}
---

請直接輸出整理後的 markdown："""


def pdftotext_layout(pdf_path: Path) -> str:
    txt_path = pdf_path.with_suffix(".txt")
    subprocess.run(
        ["pdftotext", "-enc", "UTF-8", "-layout", str(pdf_path), str(txt_path)],
        check=True,
    )
    return txt_path.read_text(encoding="utf-8")


def main():
    keys = _find_gemini_keys()
    if not keys:
        print("❌ No GEMINI_API_KEY found in env/.env", file=sys.stderr)
        sys.exit(1)
    print(f"loaded {len(keys)} Gemini key(s)")

    codes_arg = None
    for a in sys.argv[1:]:
        if a.startswith("--codes="):
            codes_arg = [c.strip().upper() for c in a.split("=", 1)[1].split(",")]
    selected = [(c, s) for (c, s) in DOCS if not codes_arg or c in codes_arg]

    client = genai.Client(api_key=keys[0])
    key_idx = 0

    failures: list[tuple[str, str]] = []
    for code, slug in selected:
        pdf = PDF_DIR / f"{slug}.pdf"
        if not pdf.exists():
            print(f"  [{code}] SKIP — no PDF at {pdf}")
            continue
        try:
            raw = pdftotext_layout(pdf)
            print(f"[{code}] pdftotext -> {len(raw)} chars; calling Gemini Flash...", flush=True)
            prompt = PROMPT.format(raw=raw)

            for attempt in range(3):
                try:
                    resp = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config={"temperature": 0.2, "max_output_tokens": 32000},
                    )
                    break
                except Exception as e:
                    msg = str(e).lower()
                    if ("429" in msg or "quota" in msg) and key_idx + 1 < len(keys):
                        key_idx += 1
                        print(f"  quota — rotating to key {key_idx + 1}/{len(keys)}", flush=True)
                        client = genai.Client(api_key=keys[key_idx])
                        time.sleep(2)
                        continue
                    raise

            text = (resp.text or "").strip()
            if not text or len(text) < 500:
                print(f"  [{code}] WARN — output too short ({len(text)} chars), skipping write")
                failures.append((code, "output_too_short"))
                continue
            # Strip accidental code-fence wrap
            text = re.sub(r"^```(?:markdown|md)?\s*\n", "", text)
            text = re.sub(r"\n```\s*$", "", text)
            out_path = OUT_DIR / f"{code.lower()}-chinese.txt"
            out_path.write_text(text, encoding="utf-8")
            print(f"  -> {out_path} ({len(text)} chars)", flush=True)
            time.sleep(4)  # be polite under flash free-tier 20 rpm
        except Exception as e:
            print(f"  [{code}] EXCEPTION: {e}", flush=True)
            failures.append((code, str(e)[:120]))

    if failures:
        print(f"\n=== {len(failures)} failures ===")
        for f in failures:
            print(f)
    else:
        print(f"\n=== {len(selected)} docs re-extracted successfully ===")


if __name__ == "__main__":
    main()
