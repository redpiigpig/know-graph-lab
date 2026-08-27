# -*- coding: utf-8 -*-
"""無教會主義研究資料的收錄 pipeline。

進 /research-data 第四個 collection。與另外三個 collection 以「機構」為單位不同，
這一個以「運動」為單位——無教會主義按其主張本來就沒有教會組織，沒有機構可掛。

收的是**關於**無教會的研究文獻與史料（學位論文、傳記、教會史著作）；內村鑑三、
矢內原忠雄本人的著作屬原典，另在 /collected-works 的無教會 hub（見
.claude/skills/ebook-collected-works/uchimura_collected_works.md）。

來源多是零星取得的 PDF，沒有統一站台可爬，所以本檔不做爬蟲，只做「收一件」：
給 PDF 路徑與書目欄位，抽全文、落 Drive、上 R2、寫進 index。

R2：mukyokai/<stem>.pdf、mukyokai-fulltext/<stem>.txt
Drive canonical：G:\\…\\研究資料\\無教會主義\\
index：public/content/research-data/mukyokai/index.json

  python -X utf8 scripts/mukyokai_sources.py --add "C:/path/x.pdf" \\
      --title "…" --author "…" --year 2005 --kind thesis --note "…"
  python -X utf8 scripts/mukyokai_sources.py --list
"""
import argparse
import hashlib
import json
import html
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hongshi as h              # noqa: E402  pure: pdf_text_sufficient
import dadaodao_fulltext as df   # noqa: E402  .env / s3 / OCR

DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\無教會主義")
R2_PDF = "mukyokai"
R2_TXT = "mukyokai-fulltext"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/mukyokai/index.json"

KINDS = {"thesis": "學位論文", "book": "專書", "article": "期刊論文",
         "archive": "檔案史料", "manifesto": "宣言與綱領"}

# 有假名就是日文；純漢字的中日文無法只靠字形分辨，故以 --lang 為準、此處只做預設值
JP_KANA = re.compile(r"[぀-ゟ゠-ヿ]")


def stem_for(title: str, author: str) -> str:
    digest = hashlib.md5(f"{author}/{title}".encode("utf-8")).hexdigest()[:8]
    safe = re.sub(r'[\\/:*?"<>|\s]+', "-", f"{author}-{title}")[:50].strip("-")
    return f"{safe}-{digest}"


def load_index():
    if INDEX_OUT.exists():
        return json.loads(INDEX_OUT.read_text(encoding="utf-8"))
    return []


def docx_text(path: Path) -> str:
    """.docx 純文字：段落界線用 </w:p> 還原，其餘標籤去掉。"""
    import zipfile
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8", "replace")
    txt = html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml)))
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def add(path, title, author, year, kind, note, publisher, title_original="", lang=""):
    src = Path(path)
    if not src.exists():
        raise SystemExit(f"找不到檔案：{src}")
    stem = stem_for(title, author)

    if src.suffix.lower() == ".docx":
        # 宣言、創刊宗旨這類原生 Word 檔沒有頁數概念，也不必 OCR
        text, pages, engine = docx_text(src), 0, "docx"
    else:
        doc = fitz.open(str(src))
        pages = doc.page_count
        text = "".join(p.get_text() for p in doc)
        doc.close()
        if h.pdf_text_sufficient(text, pages):
            engine = "text"
        else:
            text, engine = df.ocr_file(src, "application/pdf")
            if not text.strip():
                raise SystemExit("OCR 取不到文字，未入庫")

    DRIVE.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower()
    mime = ("application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if ext == ".docx" else "application/pdf")
    (DRIVE / f"{stem}{ext}").write_bytes(src.read_bytes())
    df.s3.upload_file(str(src), df.R2_BUCKET, f"{R2_PDF}/{stem}{ext}",
                      ExtraArgs={"ContentType": mime})
    df.r2_put_text(f"{R2_TXT}/{stem}.txt", text.strip())

    rows = [r for r in load_index() if r["stem"] != stem]
    rows.append({
        "stem": stem, "title": title, "titleOriginal": title_original,
        "lang": lang or ("ja" if JP_KANA.search(title_original or title) else "zh"),
        "author": author, "year": str(year),
        "kind": kind, "kindLabel": KINDS.get(kind, kind), "publisher": publisher,
        "note": note, "pages": pages, "chars": len(text),
        "pdfKey": f"{R2_PDF}/{stem}{ext}", "textKey": f"{R2_TXT}/{stem}.txt",
    })
    rows.sort(key=lambda r: (r["year"], r["author"]))
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已收：{author}，《{title}》（{year}）{pages} 頁 / {len(text):,} 字 [{engine}]")
    print(f"  → {INDEX_OUT}（共 {len(rows)} 件）")


def listing():
    rows = load_index()
    for r in rows:
        print(f"  {r['year']}  {r['author']}　{r['title'][:44]}　{r['kindLabel']}　{r['chars']:,} 字")
    print(f"共 {len(rows)} 件")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--year", default="")
    ap.add_argument("--kind", default="thesis", choices=sorted(KINDS))
    ap.add_argument("--note", default="")
    ap.add_argument("--publisher", default="")
    ap.add_argument("--title-original", default="", help="日文等原文題名；中譯放 --title")
    ap.add_argument("--lang", default="", choices=["", "zh", "ja", "en"])
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.add:
        if not (args.title and args.author):
            raise SystemExit("--add 需同時給 --title 與 --author")
        add(args.add, args.title, args.author, args.year, args.kind, args.note,
            args.publisher, args.title_original, args.lang)
    if args.list:
        listing()
    if not (args.add or args.list):
        ap.print_help()


if __name__ == "__main__":
    main()
