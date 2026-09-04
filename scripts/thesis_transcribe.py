# -*- coding: utf-8 -*-
"""把各校典藏下載到的學位論文 PDF 轉成逐頁全文，放 R2 私有區，網站只留索引。

為什麼全文不進 repo：這些是他人的學位論文，repo 是公開的
（github.com/redpiigpig/know-graph-lab）。把全文放 public/content/ 等於公開重製，
而且 git 歷史刪不掉。做法比照國史館那批——全文放 R2 `research-private/`，
由需驗證的端點供應，repo 只留書目與頁數。

🚨 有文字層不等於抽得出東西。掃描版 PDF 也開得起來、也回字串，只是回空的；
   所以每一本都要看「平均每頁字數」，過低的另外標出來，不要當成轉錄成功。

  python -X utf8 scripts/thesis_transcribe.py            # 轉錄尚未轉的
  python -X utf8 scripts/thesis_transcribe.py --rebuild  # 全部重轉
"""
import argparse
import gzip
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
LEDGER = Path("C:/tmp/thesis_fulltext.json")
SHORTLIST = REPO / "public/content/research-data/pct/thesis-shortlist.json"
INDEX = REPO / "public/content/research-data/pct/thesis-fulltext-index.json"
PREFIX = "research-private/theses"
# 每頁少於這個字數就當它其實是掃描版、沒有真的文字層
MIN_CHARS_PER_PAGE = 80
OUT = Path("G:/我的雲端硬碟/資料/知識圖工作室/研究資料/博論參考文獻/全文")


def find_pdf(title, rec):
    """帳本早期的紀錄沒存 path（只有 status 與 bytes），檔案卻在 Drive。
    先用 path，沒有就按檔名回推——下載時的檔名是題名去掉檔案系統禁用字元後截 70 字。"""
    import re as _re
    if rec.get("path") and Path(rec["path"]).exists():
        return Path(rec["path"])
    stem = _re.sub(r'[\/:*?"<>|]', "_", title)[:70]
    for cand in (OUT / f"{stem}.pdf", *OUT.glob(f"{stem[:24]}*.pdf")):
        if cand.exists():
            return cand
    return None


def slugify(title):
    """R2 的鍵不放中文——中文鍵在 S3 相容層要 URL 編碼，容易出錯又難查。"""
    import hashlib
    return hashlib.sha1(title.encode("utf-8")).hexdigest()[:16]


def extract(path):
    """逐頁抽文字。回 [(頁碼, 內文)]，頁碼從 1 起、保留 PDF 原頁序。"""
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc, 1):
        t = page.get_text().strip()
        # 頁首頁尾的孤行頁碼沒有意義，但不要動內文——這裡只清全空白
        t = re.sub(r"\n{3,}", "\n\n", t)
        pages.append((i, t))
    doc.close()
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()

    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    meta = {x["title"]: x for x in json.loads(SHORTLIST.read_text(encoding="utf-8"))["items"]}
    have = set() if a.rebuild else df.r2_existing_keys(PREFIX)
    out = []
    for title, rec in led.items():
        if rec.get("status") != "OK":
            continue
        p = find_pdf(title, rec)
        if p is None:
            print(f"  ✗ 找不到檔案：{title[:34]}", flush=True)
            continue
        sid = slugify(title)
        key = f"{PREFIX}/{sid}.jsonl.gz"
        m = meta.get(title, {})
        if key in have:                      # 續跑：已轉過的只補索引，不重抽
            pages = None
        else:
            pages = extract(p)
            body = "\n".join(json.dumps({"page": n, "text": t}, ensure_ascii=False)
                             for n, t in pages)
            df.r2_put_text_gz(key, body)
        n_pages = len(pages) if pages else m.get("pages", 0)
        chars = sum(len(t) for _, t in pages) if pages else 0
        row = {"id": sid, "title": title, "school": m.get("school", ""),
               "dept": m.get("dept", ""), "author": m.get("author", ""),
               "advisor": m.get("advisor", ""), "year": m.get("year", ""),
               "degree": m.get("degree", ""), "repoUrl": rec.get("repoUrl", ""),
               "bytes": rec.get("bytes", 0)}
        if pages:
            row |= {"pages": n_pages, "chars": chars,
                    "perPage": round(chars / n_pages) if n_pages else 0}
            row["scanned"] = row["perPage"] < MIN_CHARS_PER_PAGE
            mark = "⚠ 疑為掃描版" if row["scanned"] else "✔"
            print(f"  {mark} {n_pages:4d}頁 {chars:7,}字  {title[:36]}", flush=True)
        out.append(row)

    out.sort(key=lambda r: (r["school"], r["title"]))
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(
        {"count": len(out), "chars": sum(r.get("chars", 0) for r in out), "items": out},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(out)} 本 / {sum(r.get('chars',0) for r in out):,} 字 → {INDEX.name}")


if __name__ == "__main__":
    main()
