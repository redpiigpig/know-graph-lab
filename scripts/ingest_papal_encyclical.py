"""
One-stop pipeline for ingesting a papal document from vatican.va into
data/encyclicals/{century}c-{pope_slug}/.

Workflow per doc:
  1. Try HTML scrape for all 3 langs (la / en / zh_tw).
  2. If Chinese HTML is empty or fails, fall back to downloading the official
     PDF from /content/dam/{pope}/pdf/{doctype}/documents/{url-key}_zh_tw.pdf
     and convert via postprocess_papal_chinese_pdf.py.
  3. Align headings: drop overdetected/under-detected headings in LA/ZH, then
     re-anchor them to EN heading positions (next-para-num).
  4. Normalize CJK Kangxi radicals (⼈ → 人, ⽣ → 生, ...) in Chinese.

Usage:
  python scripts/ingest_papal_encyclical.py \\
    --pope francesco \\
    --pope-slug francis \\
    --century 21 \\
    --doc-slug fratelli-tutti-2020 \\
    --url-key papa-francesco_20201003_enciclica-fratelli-tutti \\
    --doctype encyclicals

  # for documents in dam/ where the prefix differs (e.g. older URL conventions)
  --pdf-zh-url 'https://www.vatican.va/content/dam/.../...zh_tw.pdf'
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KANGXI_RANGE = (0x2F00, 0x2FDF)   # Kangxi Radicals
KANGXI_SUPP = (0x2E80, 0x2EFF)    # CJK Radicals Supplement


def _kangxi_to_cjk(s: str) -> str:
    """Map Kangxi radical block + CJK supplement to nearest Unified Ideograph.

    vatican.va's Chinese PDFs sometimes encode characters in the Kangxi radical
    block (e.g. ⼈ U+2F08 instead of 人 U+4EBA). We map known cases.
    """
    table = {
        '⼈': '人', '⽣': '生', '⼤': '大', '⼀': '一', '⼆': '二', '⼗': '十',
        '⼚': '厂', '⼝': '口', '⼟': '土', '⼠': '士', '⼥': '女', '⼦': '子',
        '⼩': '小', '⼭': '山', '⼯': '工', '⼰': '己', '⼸': '弓', '⼼': '心',
        '⼿': '手', '⽀': '支', '⽂': '文', '⽃': '斗', '⽅': '方', '⽇': '日',
        '⽉': '月', '⽊': '木', '⽋': '欠', '⽌': '止', '⽐': '比', '⽑': '毛',
        '⽒': '氏', '⽓': '气', '⽔': '水', '⽕': '火', '⽖': '爪', '⽗': '父',
        '⽚': '片', '⽛': '牙', '⽜': '牛', '⽝': '犬', '⽞': '玄', '⽟': '玉',
        '⽠': '瓜', '⽡': '瓦', '⽢': '甘', '⽤': '用', '⽥': '田', '⽩': '白',
        '⽪': '皮', '⽫': '皿', '⽬': '目', '⽭': '矛', '⽮': '矢', '⽯': '石',
        '⽰': '示', '⽲': '禾', '⽳': '穴', '⽴': '立', '⽵': '竹', '⽶': '米',
        '⽸': '缶', '⽹': '网', '⽺': '羊', '⽻': '羽', '⽼': '老', '⽽': '而',
        '⽿': '耳', '⾁': '肉', '⾃': '自', '⾄': '至', '⾅': '臼', '⾆': '舌',
        '⾈': '舟', '⾉': '艮', '⾊': '色', '⾋': '艸', '⾍': '虫', '⾎': '血',
        '⾏': '行', '⾐': '衣', '⾒': '見', '⾔': '言', '⾕': '谷', '⾖': '豆',
        '⾗': '豕', '⾘': '豸', '⾙': '貝', '⾚': '赤', '⾛': '走', '⾜': '足',
        '⾝': '身', '⾞': '車', '⾟': '辛', '⾠': '辰', '⾢': '邑', '⾣': '酉',
        '⾥': '里', '⾦': '金', '⾧': '長', '⾨': '門', '⾩': '阜', '⾪': '隶',
        '⾫': '隹', '⾬': '雨', '⾭': '青', '⾮': '非', '⾯': '面', '⾰': '革',
        '⾳': '音', '⾴': '頁', '⾵': '風', '⾶': '飛', '⾷': '食', '⾸': '首',
        '⾹': '香', '⾺': '馬', '⾻': '骨', '⾼': '高', '⿁': '鬼', '⿂': '魚',
        '⿃': '鳥', '⿄': '鹵', '⿅': '鹿', '⿆': '麥', '⿇': '麻', '⿈': '黃',
        '⿉': '黍', '⿊': '黑', '⿎': '鼓', '⿏': '鼠', '⿐': '鼻', '⿒': '齒',
        '⿓': '龍', '⿔': '龜',
    }
    return ''.join(table.get(c, c) for c in s)


def normalize_chinese_text(path: Path) -> int:
    """Normalize Kangxi radicals → CJK Unified Ideographs in a file. Returns
    the number of character substitutions made."""
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    new_text = _kangxi_to_cjk(text)
    diff = sum(1 for a, b in zip(text, new_text) if a != b)
    if diff:
        path.write_text(new_text, encoding="utf-8")
    return diff


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pope", required=True)
    ap.add_argument("--pope-slug", required=True)
    ap.add_argument("--century", type=int, required=True)
    ap.add_argument("--doc-slug", required=True)
    ap.add_argument("--url-key", required=True)
    ap.add_argument("--doctype", default="encyclicals",
                    choices=["encyclicals", "apost_constitutions",
                             "apost_exhortations", "apost_letters"])
    ap.add_argument("--pdf-zh-url", default=None,
                    help="explicit Chinese PDF URL (override the dam/ pattern)")
    ap.add_argument("--skip-zh", action="store_true",
                    help="skip Chinese fetch entirely (placeholder)")
    args = ap.parse_args()

    century_label = f"{args.century:02d}c"
    out_dir = ROOT / "data" / "encyclicals" / f"{century_label}-{args.pope_slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. scrape la + en
    scrape_cmd = [
        sys.executable, str(ROOT / "scripts" / "scrape_papal_encyclical.py"),
        "--pope", args.pope,
        "--pope-slug", args.pope_slug,
        "--century", str(args.century),
        "--doc-slug", args.doc_slug,
        "--url-key", args.url_key,
        "--doctype", args.doctype,
        "--langs", "la,en",
    ]
    print(f"\n[1/4] Scrape LA+EN: {' '.join(scrape_cmd)}", flush=True)
    r = subprocess.run(scrape_cmd, cwd=ROOT)
    if r.returncode != 0:
        print("WARNING: LA or EN scrape had failures (continuing)", flush=True)

    # 2. Chinese: try HTML first, fall back to PDF
    zh_path = out_dir / f"{args.doc_slug}-chinese.txt"
    if args.skip_zh:
        print("[2/4] Skipping Chinese fetch (--skip-zh)", flush=True)
        zh_path.write_text("⏳ 中譯待補\n", encoding="utf-8")
    else:
        # Try HTML first
        zh_html_url = (f"https://www.vatican.va/content/{args.pope}/zh_tw/"
                       f"{args.doctype}/documents/{args.url_key}.html")
        print(f"[2/4] Try Chinese HTML: {zh_html_url}", flush=True)
        zh_html_cmd = [
            sys.executable, str(ROOT / "scripts" / "scrape_papal_encyclical.py"),
            "--pope", args.pope,
            "--pope-slug", args.pope_slug,
            "--century", str(args.century),
            "--doc-slug", args.doc_slug,
            "--url-key", args.url_key,
            "--doctype", args.doctype,
            "--langs", "zh_tw",
        ]
        subprocess.run(zh_html_cmd, cwd=ROOT)
        zh_size = zh_path.stat().st_size if zh_path.exists() else 0
        if zh_size < 2000:
            # Try PDF fallback
            pdf_url = args.pdf_zh_url or (
                f"https://www.vatican.va/content/dam/{args.pope}/pdf/"
                f"{args.doctype}/documents/{args.url_key}_zh_tw.pdf"
            )
            print(f"  HTML too small ({zh_size}B); try PDF: {pdf_url}", flush=True)
            try:
                pdf_bytes = fetch(pdf_url)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                    f.write(pdf_bytes)
                    pdf_path = f.name
                txt_path = pdf_path + ".txt"
                subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", pdf_path, txt_path],
                    check=True,
                )
                subprocess.run(
                    [sys.executable,
                     str(ROOT / "scripts" / "postprocess_papal_chinese_pdf.py"),
                     txt_path, str(zh_path)],
                    check=True,
                )
                os.unlink(pdf_path)
                os.unlink(txt_path)
            except Exception as e:
                print(f"  PDF fallback FAILED: {e}", flush=True)
                zh_path.write_text("⏳ 中譯待補\n", encoding="utf-8")

    # 3. Normalize Chinese (Kangxi radicals → standard CJK)
    n_norm = normalize_chinese_text(zh_path)
    print(f"[3/4] Normalized {n_norm} Kangxi chars in Chinese", flush=True)

    # 4. Align headings across la/en/zh to EN spine
    print(f"[4/4] Align headings", flush=True)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "align_papal_headings.py"),
         str(args.century), args.pope_slug, args.doc_slug],
        cwd=ROOT,
    )

    # Final report: counts
    print("\n=== Final counts ===")
    for lang, suffix in [("EN", "english"), ("LA", "latin"), ("ZH", "chinese")]:
        p = out_dir / f"{args.doc_slug}-{suffix}.txt"
        if not p.exists():
            print(f"  {lang}: (missing)")
            continue
        text = p.read_text(encoding="utf-8")
        paras = re.findall(r"(?m)^(\d{1,3})\.\s", text)
        headings = re.findall(r"(?m)^## (.+)$", text)
        fns = re.findall(r"\[\^(\d+)\]:", text)
        print(f"  {lang}: paras={len(paras)} unique={len(set(paras))}; headings={len(headings)}; fns={len(fns)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
