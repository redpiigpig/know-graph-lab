#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衛報 Wesleyan News 掃描 PDF → 翻頁書電子化 + R2 原檔典藏。

對 `衛報/` 內每一份 `YYYY.MM.DD.pdf`（中華基督教衛理公會衛蘭中心刊物）：
  1. 偵測期號 — 用 Gemini OCR 封面抓「第 N 期 / No.N」、日期、節期/主日標題。
  2. 渲染每頁 → public/herald/{issue}/page-NN.jpg（掃描影像翻頁書，~1100px 寬）。
  3. 原始 PDF → R2 `herald/issue-{issue}.pdf`（供 /api 串流下載）。
  4. 寫 public/herald/{issue}/meta.json + 重建 public/herald/index.json。
  5. R2 上傳確認後，把原檔移出 git（搬到 SEALED_DIR）。

第 55 期（2002.11.30）早已做成「結構化純文字翻頁書」(mode=text)，本腳本
不重渲染、不覆蓋其影像/資料，只補上 meta.json（mode=text）並上傳 PDF + 列入索引。

引擎政策：Gemini（4 keys 輪流）只用在「封面期號偵測」，不做全文 OCR。

用法：
  python scripts/herald_ingest.py detect          # 只跑封面偵測，印出期號對照表（會快取）
  python scripts/herald_ingest.py status          # 看每期 render / R2 / meta 狀態
  python scripts/herald_ingest.py run             # 全部：render + 上傳 + meta + index
  python scripts/herald_ingest.py run --only 2001.04.22
  python scripts/herald_ingest.py run --no-seal   # 跑完不要把原檔移出 git
  python scripts/herald_ingest.py index           # 只重建 index.json
"""
import io
import json
import re
import shutil
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import boto3
import fitz  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "衛報"
HERALD_DIR = ROOT / "public" / "herald"
SEALED_DIR = ROOT.parent / "衛報原檔"          # repo 外，移出 git
DETECT_CACHE = ROOT / "data" / "herald_detect_cache.json"  # 不放 public（避免被當靜態檔案外送）

RENDER_WIDTH = 1100      # 對齊既有第 55 期影像寬度
JPEG_QUALITY = 82
R2_PDF_PREFIX = "herald/"

# 既有第 55 期＝結構化純文字翻頁書，不動其影像/資料。
TEXT_ISSUES = {55}


# ── env / clients ─────────────────────────────────────────────
def load_env():
    env = {}
    with (ROOT / ".env").open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
R2_BUCKET = ENV["R2_BUCKET"]

_r2 = None
def r2():
    global _r2
    if _r2 is None:
        _r2 = boto3.client(
            "s3",
            region_name="auto",
            endpoint_url=ENV["R2_ENDPOINT"],
            aws_access_key_id=ENV["R2_ACCESS_KEY"],
            aws_secret_access_key=ENV["R2_SECRET_KEY"],
        )
    return _r2


def r2_head(key):
    try:
        return r2().head_object(Bucket=R2_BUCKET, Key=key)
    except Exception:
        return None


def gemini_keys():
    keys = []
    for n in [""] + [f"_{i}" for i in range(1, 11)]:
        for base in ("Gemini_API_Key", "GEMINI_API_KEY"):
            v = ENV.get(f"{base}{n}")
            if v and v not in keys:
                keys.append(v)
    if not keys:
        sys.exit("ERROR: 找不到 Gemini API key")
    return keys


# ── cover detection ───────────────────────────────────────────
COVER_PROMPT = """這是台灣《衛報 Wesleyan News》（中華基督教衛理公會衛蘭中心刊物）某一期的封面掃描。
請辨識並只回傳 JSON（不要 markdown 圍欄）：
{
  "issue": 0,          // 期號數字，封面通常印「第 N 期」或「No.N」；找不到填 0
  "date": "YYYY-MM-DD",// 封面日期；找不到填空字串
  "title": ""          // 封面主標題或節期/主日名稱（例如「將臨節第一主日」「聖靈降臨節」），找不到填空字串
}
全部繁體中文。只回傳 JSON。"""


def detect_cover(pdf_path, keys, key_idx):
    """OCR 封面 → {issue, date, title}。回傳 (result, new_key_idx)。"""
    from google import genai
    from google.genai import types

    doc = fitz.open(pdf_path)
    pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    img_bytes = pix.tobytes("jpeg")
    doc.close()

    last_err = ""
    for _ in range(len(keys) * 2):
        try:
            client = genai.Client(api_key=keys[key_idx])
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    COVER_PROMPT,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0, response_mime_type="application/json"
                ),
            )
            raw = (resp.text or "").strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw), key_idx
        except Exception as e:
            last_err = str(e)[:160]
            key_idx = (key_idx + 1) % len(keys)
            time.sleep(2)
    raise RuntimeError(f"cover detect failed: {last_err}")


def load_detect_cache():
    if DETECT_CACHE.exists():
        return json.loads(DETECT_CACHE.read_text(encoding="utf-8"))
    return {}


def save_detect_cache(cache):
    DETECT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    DETECT_CACHE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def date_from_name(pdf_path):
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})", pdf_path.stem)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def cmd_detect(force=False):
    pdfs = sorted(SRC_DIR.glob("*.pdf"))
    keys = gemini_keys()
    cache = load_detect_cache()
    key_idx = 0
    print(f"封面偵測 {len(pdfs)} 份（{len(keys)} keys）\n")
    for pdf in pdfs:
        name = pdf.name
        if not force and name in cache and cache[name].get("issue"):
            c = cache[name]
            print(f"  {name}  → 第 {c['issue']} 期  {c.get('date','')}  {c.get('title','')}  (cached)")
            continue
        try:
            res, key_idx = detect_cover(pdf, keys, key_idx)
        except Exception as e:
            print(f"  {name}  ✗ {e}")
            continue
        if not res.get("date"):
            res["date"] = date_from_name(pdf)
        cache[name] = res
        save_detect_cache(cache)
        print(f"  {name}  → 第 {res.get('issue')} 期  {res.get('date','')}  {res.get('title','')}")
        time.sleep(2)
    return cache


# ── render ────────────────────────────────────────────────────
def render_pages(pdf_path, out_dir):
    """每頁 → page-NN.jpg（已存在則跳過）。回傳頁數。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    n = len(doc)
    for i in range(n):
        out = out_dir / f"page-{i + 1:02d}.jpg"
        if out.exists() and out.stat().st_size > 1000:
            continue
        page = doc.load_page(i)
        zoom = RENDER_WIDTH / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        img.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True)
    doc.close()
    return n


def upload_pdf(pdf_path, issue):
    key = f"{R2_PDF_PREFIX}issue-{issue}.pdf"
    size = pdf_path.stat().st_size
    head = r2_head(key)
    if head and head.get("ContentLength") == size:
        print(f"    ✓ R2 已有 {key} ({size/1024/1024:.1f} MB)")
        return key
    print(f"    ↑ 上傳 {pdf_path.name} → {key} ({size/1024/1024:.1f} MB)…", end="", flush=True)
    with pdf_path.open("rb") as f:
        r2().put_object(Bucket=R2_BUCKET, Key=key, Body=f.read(), ContentType="application/pdf")
    print(" done")
    return key


def write_meta(issue, date, title, page_count, pdf_key, mode):
    issue_dir = HERALD_DIR / str(issue)
    issue_dir.mkdir(parents=True, exist_ok=True)
    y, m, d = date.split("-")
    meta = {
        "issue": issue,
        "date": date,
        "date_display": f"{y}/{m}/{d}",
        "title": title or "",
        "page_count": page_count,
        "mode": mode,
        "pdf_key": pdf_key,
        "running_header": "文化取向的宣教 國度視野的牧養",
    }
    (issue_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def rebuild_index():
    issues = []
    for meta_path in HERALD_DIR.glob("*/meta.json"):
        try:
            issues.append(json.loads(meta_path.read_text(encoding="utf-8")))
        except Exception:
            pass
    issues.sort(key=lambda x: x.get("issue", 0))
    (HERALD_DIR / "index.json").write_text(
        json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  index.json → {len(issues)} 期：{', '.join(str(i['issue']) for i in issues)}")


def seal_original(pdf_path):
    SEALED_DIR.mkdir(parents=True, exist_ok=True)
    dest = SEALED_DIR / pdf_path.name
    shutil.move(str(pdf_path), str(dest))
    print(f"    ⇒ 原檔移出 git → {dest}")


# ── run ───────────────────────────────────────────────────────
def cmd_run(only=None, seal=True):
    pdfs = sorted(SRC_DIR.glob("*.pdf")) if SRC_DIR.exists() else []
    cache = load_detect_cache()
    keys = gemini_keys()
    key_idx = 0

    # 確保第 55 期（已存在影像/資料）有 meta + PDF 上 R2 + 列入索引
    if (HERALD_DIR / "55").exists():
        p55 = SRC_DIR / "2002.11.30.pdf"
        existing_pages = len(list((HERALD_DIR / "55").glob("page-*.jpg"))) or 24
        pdf_key55 = f"{R2_PDF_PREFIX}issue-55.pdf"
        if p55.exists():
            print("[55] 2002.11.30.pdf（既有結構化純文字版）")
            pdf_key55 = upload_pdf(p55, 55)
        write_meta(55, "2002-11-30", "將臨節第一主日", existing_pages, pdf_key55, "text")

    for pdf in pdfs:
        name = pdf.name
        if only and only not in name:
            continue
        if name == "2002.11.30.pdf":
            # 第 55 期已單獨處理（mode=text），原檔仍 seal
            if seal:
                seal_original(pdf)
            continue

        info = cache.get(name) or {}
        if not info.get("issue"):
            try:
                info, key_idx = detect_cover(pdf, keys, key_idx)
                if not info.get("date"):
                    info["date"] = date_from_name(pdf)
                cache[name] = info
                save_detect_cache(cache)
            except Exception as e:
                print(f"[{name}] ✗ 封面偵測失敗，跳過：{e}")
                continue
        issue = info.get("issue")
        if not issue:
            print(f"[{name}] ✗ 無期號，跳過")
            continue
        date = info.get("date") or date_from_name(pdf)
        title = info.get("title", "")

        print(f"[{issue}] {name}  {date}  {title}")
        page_count = render_pages(pdf, HERALD_DIR / str(issue))
        print(f"    渲染 {page_count} 頁 → public/herald/{issue}/")
        pdf_key = upload_pdf(pdf, issue)
        write_meta(issue, date, title, page_count, pdf_key, "scan")
        if seal:
            seal_original(pdf)

    rebuild_index()
    print("\n完成。")


def cmd_status():
    cache = load_detect_cache()
    for meta_path in sorted(HERALD_DIR.glob("*/meta.json"), key=lambda p: int(p.parent.name)):
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        issue = m["issue"]
        n_img = len(list((HERALD_DIR / str(issue)).glob("page-*.jpg")))
        on_r2 = bool(r2_head(m["pdf_key"]))
        print(f"  第 {issue:>3} 期  {m['date']}  mode={m['mode']:<4}  "
              f"imgs={n_img:>2}/{m['page_count']:<2}  R2={'✓' if on_r2 else '✗'}  {m['title']}")
    src = sorted(SRC_DIR.glob("*.pdf")) if SRC_DIR.exists() else []
    print(f"\n衛報/ 待處理原檔：{len(src)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "detect":
        cmd_detect(force="--force" in args)
    elif cmd == "status":
        cmd_status()
    elif cmd == "index":
        rebuild_index()
    elif cmd == "run":
        only = args[args.index("--only") + 1] if "--only" in args else None
        cmd_run(only=only, seal="--no-seal" not in args)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
