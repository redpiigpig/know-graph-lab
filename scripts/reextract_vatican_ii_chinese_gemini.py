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

try:
    import anthropic as _anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

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
2. **段落編號**（PDF 中行首的數字,如 1, 2, 3, ..., 130）保留為 `數字.` 前綴 — 例如 `1.`、`2.`、`130.`，**不要寫成 `N. 1` 或 `N.1`**。每段獨立成行，段間空行
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

PROMPT_CHUNK_BODY = """以下是 vatican.va 中文 PDF 用 pdftotext -layout 抽字的繁體中文文本「**正文第 {part_idx}/{part_total} 部分**」。整份文件被切成多塊處理，這塊只包含正文段落（不含註腳定義區）。請重新整理為乾淨結構化 markdown 純文字。

嚴格規則：
1. **章節標題**（如「第一章 通論」「甲、總綱」）— 加 `## ` 前綴單獨成行
2. **段落編號**保留為 `數字.` 前綴（如 `1.` `30.` `93.`），**不要寫成 `N. 1`**，每段獨立、段間空行
3. **段落內被切斷的多行**合併為一段
4. **註腳 reference** 保留 inline `(1) (2) (3)` 格式
5. **不要**輸出 `## Footnotes` 區段（footnote 定義在另一個 chunk 處理）
6. **移除**：目錄頁、頁眉、頁尾、頁碼、語言切換 nav `[ AR - BE - CS - ... ]`、metadata 重複行
7. **不要翻譯**，不要新增 commentary
8. **保留段落順序與編號**，不可重新編號
9. **不要包裝**輸出於 ``` 區塊內，直接輸出純 markdown

輸入（第 {part_idx}/{part_total} 塊正文）：
---
{raw}
---

請直接輸出整理後的 markdown："""

PROMPT_CHUNK_TAIL = """以下是 vatican.va 中文 PDF 用 pdftotext -layout 抽字的繁體中文文本「**最後一部分**」，包含最後一些正文段落 + 註腳定義區 + 教宗公佈令。請整理為乾淨 markdown。

嚴格規則：
1. **章節標題**加 `## ` 前綴
2. **段落編號**保留為 `數字.` 前綴
3. **註腳 reference** inline 保留 `(N)` 格式
4. **註腳定義**放在 `## Footnotes` 區段，每條格式 `[^N]: 內容`
5. **教宗公佈令**保留為 `## 教宗公佈令` 段落 + 公佈內容 + 「公教會主教 保祿」+ 日期
6. **移除**：目錄頁、頁眉、頁尾、頁碼、語言切換 nav、metadata 重複行
7. **不要翻譯**，**不要包裝**於 ``` 區塊

輸入（最後一塊，含正文尾段 + footnotes + 公佈令）：
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


def _make_anthropic_client():
    """Build Anthropic client preferring API key, falling back to Claude Code OAuth."""
    if not _HAS_ANTHROPIC:
        raise RuntimeError("anthropic SDK not installed (pip install anthropic)")
    api_key = os.environ.get("ANTHROPIC_API_KEY") or ENV.get("ANTHROPIC_API_KEY")
    common = {"timeout": 600.0, "max_retries": 2}
    if api_key:
        return _anthropic.Anthropic(api_key=api_key, **common)
    # OAuth fallback: read accessToken from Claude Code credentials.json
    from pathlib import Path
    import json as _json
    cred_path = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred_path.exists():
        creds = _json.loads(cred_path.read_text(encoding="utf-8"))
        token = creds.get("claudeAiOauth", {}).get("accessToken", "")
        if token:
            return _anthropic.Anthropic(auth_token=token, **common)
    raise RuntimeError("No Anthropic credentials (set ANTHROPIC_API_KEY or login via Claude Code)")


def _haiku_call(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    client = _make_anthropic_client()
    resp = client.messages.create(
        model=model,
        max_tokens=64000,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts)


def _find_footnote_split(raw: str) -> int:
    """Locate where the footnote definition section begins in raw pdftotext.

    Returns the char offset of the start of the footnote area. Tries multiple
    heuristics that match vatican.va Chinese PDF layouts:
      - `•附注•` markers (LG, GS style)
      - `## 附註` / `附 註` heading
      - Standalone `1. Cf.` / `1. 參閱` numbered footnote
      - Fallback: last 25% of doc
    """
    # GS/LG style: multiple •附注• markers interspersed with body chapters.
    # Use the LAST •附注• marker so all body content lands in body chunks.
    fn_marker_re = re.compile(r'•\s*附\s*[註注]\s*•')
    matches = list(fn_marker_re.finditer(raw))
    if matches:
        return matches[-1].start()
    # Markdown-ish heading
    m = re.search(r'^\s*##?\s*附\s*[註注]\s*$', raw, re.MULTILINE)
    if m and m.start() > len(raw) * 0.4:
        return m.start()
    # Standalone numbered footnote near end
    cutoff = int(len(raw) * 0.6)
    fn_pat = re.compile(
        r'^\s*1\.\s+(?:Cf\.|AAS|Conc\.|S\.|Sancti|Const\.|Encyc|Litt|PL|PG|參閱|聖|宗|教|《)',
        re.MULTILINE,
    )
    m = fn_pat.search(raw, cutoff)
    if m:
        return m.start()
    # Fallback: last 25% of doc as 'tail'
    return int(len(raw) * 0.75)


def _split_by_chapters(body: str, max_chunk_chars: int) -> list[str]:
    """Split body text into chunks at chapter heading boundaries.

    Chapter headings in vatican.va Chinese: ^\\s*第[一二三四五六七八九十]+章
    or ^\\s*第[一二三四五六七八九十]+部分
    """
    if len(body) <= max_chunk_chars:
        return [body]
    chap_re = re.compile(r'^\s*第[一二三四五六七八九十]+(?:章|部分|編)', re.MULTILINE)
    starts = [0] + [m.start() for m in chap_re.finditer(body)]
    if len(starts) <= 1:
        # No chapter markers; split by paragraph numbers as fallback
        para_re = re.compile(r'^\s+(\d+)\s+[一-鿿]', re.MULTILINE)
        starts = [0] + [m.start() for m in para_re.finditer(body)]
    if len(starts) <= 1:
        # Last resort: split in halves
        return [body[: len(body) // 2], body[len(body) // 2 :]]
    starts.append(len(body))

    chunks: list[str] = []
    cur_start = starts[0]
    for nxt in starts[1:]:
        if nxt - cur_start >= max_chunk_chars and cur_start < nxt:
            # Close current chunk at the previous boundary if any
            chunks.append(body[cur_start:nxt])
            cur_start = nxt
    if cur_start < len(body):
        chunks.append(body[cur_start:])
    return chunks


def _haiku_chunked(raw: str, code: str, max_body_chunk: int = 25000) -> str:
    """Process long doc via multiple Haiku calls then concat outputs.

    Splits raw into [body chunks] + [tail chunk (footnotes + 公佈令)],
    each processed with a chunk-aware prompt, then concatenated.
    """
    split_at = _find_footnote_split(raw)
    body, tail = raw[:split_at], raw[split_at:]
    body_chunks = _split_by_chapters(body, max_body_chunk)
    part_total = len(body_chunks) + 1  # +1 for tail
    out_parts: list[str] = []
    for i, ch in enumerate(body_chunks):
        prompt = PROMPT_CHUNK_BODY.format(part_idx=i + 1, part_total=part_total, raw=ch)
        print(f"  [{code}] chunk {i + 1}/{part_total} body ({len(ch)} chars)...", flush=True)
        text = _haiku_call(prompt).strip()
        text = re.sub(r"^```(?:markdown|md)?\s*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
        out_parts.append(text)
        time.sleep(2)
    # Tail chunk
    prompt = PROMPT_CHUNK_TAIL.format(raw=tail)
    print(f"  [{code}] chunk {part_total}/{part_total} tail ({len(tail)} chars)...", flush=True)
    text = _haiku_call(prompt).strip()
    text = re.sub(r"^```(?:markdown|md)?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    out_parts.append(text)
    combined = "\n\n".join(out_parts)
    # Post-process: normalize paragraph numbers '^N ' → '^N. ' (chunked mode often leaves
    # raw '1 基督...' instead of '1. 基督...' despite prompt instruction)
    combined = re.sub(r"^(\d+) ([一-鿿])", r"\1. \2", combined, flags=re.MULTILINE)
    return combined


# Long docs that need chunked Haiku processing (force-chunk via env var if single-call truncates)
# After empirical test: pdftotext_layout produces ~73K chars for LG/GS — single Haiku 64K call is enough.
# Set env CHUNK_CODES=LG,GS to force chunked mode if truncation recurs.
CHUNK_CODES = set(filter(None, os.environ.get("CHUNK_CODES", "").split(",")))


def main():
    engine = "gemini"
    codes_arg = None
    for a in sys.argv[1:]:
        if a.startswith("--codes="):
            codes_arg = [c.strip().upper() for c in a.split("=", 1)[1].split(",")]
        elif a.startswith("--engine="):
            engine = a.split("=", 1)[1].strip().lower()

    selected = [(c, s) for (c, s) in DOCS if not codes_arg or c in codes_arg]

    if engine == "haiku":
        if not _HAS_ANTHROPIC:
            print("❌ Install: pip install anthropic", file=sys.stderr); sys.exit(1)
        try:
            _make_anthropic_client()  # verify auth (API key OR Claude Code OAuth)
        except Exception as e:
            print(f"❌ Anthropic auth failed: {e}", file=sys.stderr); sys.exit(1)
        print(f"engine: Haiku 4.5 (OAuth via Claude Code credentials.json)")
        client = None  # not used
        keys = []  # not used
        key_idx = 0
    else:
        keys = _find_gemini_keys()
        if not keys:
            print("❌ No GEMINI_API_KEY found in env/.env", file=sys.stderr); sys.exit(1)
        print(f"engine: Gemini Flash, {len(keys)} key(s)")
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
            print(f"[{code}] pdftotext -> {len(raw)} chars; calling {engine}...", flush=True)

            if engine == "haiku" and code in CHUNK_CODES:
                text = _haiku_chunked(raw, code).strip()
                # Skip the rest of single-call path
                if not text or len(text) < 500:
                    print(f"  [{code}] WARN — chunked output too short ({len(text)} chars), skipping write")
                    failures.append((code, "chunked_output_too_short"))
                    continue
                out_path = OUT_DIR / f"{code.lower()}-chinese.txt"
                out_path.write_text(text, encoding="utf-8")
                print(f"  -> {out_path} ({len(text)} chars, chunked)", flush=True)
                time.sleep(4)
                continue

            prompt = PROMPT.format(raw=raw)

            if engine == "haiku":
                text = _haiku_call(prompt).strip()
            else:
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
