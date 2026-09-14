#!/usr/bin/env python
"""《印度學佛教學研究》(IBK) 全文收錄管線 —— 日本佛學研究史的骨幹語料。

日本印度学仏教学会的學會誌，1952 創刊至今，J-STAGE 開放取用。
宇井伯壽、平川彰、高崎直道、柳田聖山、水野弘元、袴谷憲昭、松本史朗、
下田正弘、佐佐木閑……戰後日本佛學的每一場論爭都在這裡留下過痕跡。

四個階段，各自可中斷可續跑（筆電會通勤休眠）：

    --toc     篇目層：J-STAGE API 分頁抓 metadata → toc.jsonl
    --fetch   全文層：下載 PDF → pdf/，帳本記錄，可續跑
    --text    抽字層：PyMuPDF 抽文字層 → text/
    --status  對帳：一律印分母

🚨 不要 OCR。舊卷（1952-2000s）看起來像掃描檔，其實有文字層，只是用
Shift-JIS 的 90ms-RKSJ-H CMap，pypdf 解不開而 PyMuPDF 解得開。實測 1952
年第一篇（鈴木大拙〈東西哲學と佛教〉）抽出 11,849 字，完全正確。整批走
OCR 會白燒配額且品質更差。只有抽不到字的那幾篇才退 OCR。
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API = "https://api.jstage.jst.go.jp/searchapi/do"
MATERIAL = "印度學佛教學研究"
UA = "Mozilla/5.0 (compatible; know-graph-lab/1.0; research use)"

ROOT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/jstage-ibk")
TOC = ROOT / "toc.jsonl"
PDF_DIR = ROOT / "pdf"
TEXT_DIR = ROOT / "text"
LEDGER = Path(__file__).parent / "state" / "jstage_ibk_ledger.jsonl"

PAGE = 1000          # API 單次上限
API_SLEEP = 1.5      # 對 API 客氣點
PDF_SLEEP = 2.0      # 下載更客氣：這是別人免費開放的東西
MIN_CHARS = 300      # 低於此視為抽字失敗，標記待 OCR


# ---------------------------------------------------------------- helpers

def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout).read()


def cdata(block, tag):
    """取 <tag> 底下的 <ja>/<en>。

    🚨 同一份 feed 裡兩種寫法都有：article_title／author 包 CDATA，
    article_link 卻是純文字。只認 CDATA 會靜默回 0 筆。
    """
    m = re.search(r"<" + tag + r">(.*?)</" + tag + r">", block, re.S)
    if not m:
        return {}
    inner = m.group(1)
    out = {}
    for lang in ("ja", "en"):
        mm = re.search(
            r"<" + lang + r">\s*(?:<name>)?\s*<!\[CDATA\[(.*?)\]\]>",
            inner, re.S,
        )
        if not mm:  # 沒有 CDATA 的純文字寫法
            mm = re.search(
                r"<" + lang + r">\s*(?:<name>)?\s*([^<]+?)\s*(?:</name>)?\s*</" + lang + r">",
                inner, re.S,
            )
        if mm:
            out[lang] = mm.group(1).strip()
    return out


def plain(block, tag):
    m = re.search(r"<" + tag + r">([^<]*)</" + tag + r">", block)
    return m.group(1).strip() if m else ""


def article_id(link):
    """https://.../article/ibk1952/1/1/1_1_1/_article → ibk1952/1/1/1_1_1"""
    m = re.search(r"/article/(.+?)/_article", link)
    return m.group(1) if m else ""


def slug(aid):
    return aid.replace("/", "_")


# ------------------------------------------------------------------- toc

def cmd_toc(args):
    ROOT.mkdir(parents=True, exist_ok=True)
    rows, start, total = [], 1, None

    while True:
        url = API + "?" + urllib.parse.urlencode(
            {"service": 3, "material": MATERIAL, "start": start, "count": PAGE}
        )
        xml = get(url).decode("utf-8", "replace")

        if total is None:
            m = re.search(r"<opensearch:totalResults>(\d+)", xml)
            total = int(m.group(1)) if m else 0
            print(f"總篇數 {total}")

        entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
        if not entries:
            break

        for e in entries:
            links = cdata(e, "article_link")
            link = links.get("ja") or links.get("en") or ""
            aid = article_id(link)
            if not aid:
                continue
            titles = cdata(e, "article_title")
            authors = cdata(e, "author")
            rows.append({
                "id": aid,
                "slug": slug(aid),
                "title_ja": titles.get("ja", ""),
                "title_en": titles.get("en", ""),
                "author_ja": authors.get("ja", ""),
                "author_en": authors.get("en", ""),
                "journal": plain(e, "cdjournal"),
                "volume": plain(e, "prism:volume"),
                "number": plain(e, "prism:number"),
                "page_start": plain(e, "prism:startingPage"),
                "page_end": plain(e, "prism:endingPage"),
                "year": plain(e, "pubyear"),
                "doi": plain(e, "prism:doi"),
                "url": link,
                "pdf_url": f"https://www.jstage.jst.go.jp/article/{aid}/_pdf",
            })

        print(f"  {start}–{start + len(entries) - 1} / {total}")
        start += len(entries)
        if start > total:
            break
        time.sleep(API_SLEEP)

    # 去重（同一篇可能跨頁重複），保序
    seen, uniq = set(), []
    for r in rows:
        if r["id"] not in seen:
            seen.add(r["id"])
            uniq.append(r)

    with TOC.open("w", encoding="utf-8") as f:
        for r in uniq:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\n寫入 {TOC}")
    print(f"抓到 {len(rows)}，去重後 {len(uniq)}，API 自報 {total}")
    if len(uniq) != total:
        print(f"🚨 差 {total - len(uniq)} 篇，分頁沒跑完或有重複 DOI，要查")


# ----------------------------------------------------------------- fetch

def load_toc():
    if not TOC.exists():
        sys.exit(f"沒有篇目檔，先跑 --toc：{TOC}")
    return [json.loads(l) for l in TOC.open(encoding="utf-8")]


def load_ledger():
    done = {}
    if LEDGER.exists():
        for line in LEDGER.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done[r["id"]] = r
    return done


def log(rec):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def cmd_fetch(args):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    toc = load_toc()
    done = load_ledger()

    todo = []
    for r in toc:
        p = PDF_DIR / (r["slug"] + ".pdf")
        if p.exists() and p.stat().st_size > 1000:
            continue
        if done.get(r["id"], {}).get("status") == "gone":
            continue
        todo.append(r)

    print(f"篇目 {len(toc)}，已有 PDF {len(toc) - len(todo)}，待抓 {len(todo)}")
    if args.limit:
        todo = todo[: args.limit]
        print(f"本輪只跑 {len(todo)}")

    ok = fail = 0
    for i, r in enumerate(todo, 1):
        p = PDF_DIR / (r["slug"] + ".pdf")
        try:
            blob = get(r["pdf_url"], timeout=120)
            if not blob.startswith(b"%PDF"):
                raise ValueError(f"不是 PDF（開頭 {blob[:12]!r}）")
            p.write_bytes(blob)
            log({"id": r["id"], "status": "ok", "bytes": len(blob)})
            ok += 1
        except Exception as exc:  # noqa: BLE001
            log({"id": r["id"], "status": "fail", "error": str(exc)[:200]})
            fail += 1
            print(f"  ✗ {r['id']}: {exc}")
        if i % 50 == 0:
            print(f"  {i}/{len(todo)}  成功 {ok} 失敗 {fail}")
        time.sleep(PDF_SLEEP)

    print(f"\n本輪 {len(todo)} 篇：成功 {ok}，失敗 {fail}")


# ------------------------------------------------------------------ text

def cmd_text(args):
    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("需要 PyMuPDF：pip install pymupdf")

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    toc = load_toc()

    have = short = missing = wrote = 0
    needs_ocr = []

    for r in toc:
        pdf = PDF_DIR / (r["slug"] + ".pdf")
        out = TEXT_DIR / (r["slug"] + ".txt")
        if not pdf.exists():
            missing += 1
            continue
        have += 1
        if out.exists() and not args.force:
            continue
        try:
            doc = fitz.open(pdf)
            text = "\n".join(p.get_text() for p in doc)
            doc.close()
        except Exception as exc:  # noqa: BLE001
            needs_ocr.append({"id": r["id"], "why": f"開檔失敗 {exc}"})
            continue
        if len(text.strip()) < MIN_CHARS:
            short += 1
            needs_ocr.append({"id": r["id"], "why": f"只有 {len(text.strip())} 字"})
            continue
        out.write_text(text, encoding="utf-8")
        wrote += 1

    print(f"篇目 {len(toc)}｜有 PDF {have}｜缺 PDF {missing}")
    print(f"本輪抽出 {wrote}｜字數過少 {short}")
    if needs_ocr:
        p = ROOT / "needs-ocr.json"
        p.write_text(json.dumps(needs_ocr, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"🚨 {len(needs_ocr)} 篇抽不出字，清單見 {p}（只有這些才需要 OCR）")


# ---------------------------------------------------------------- status

def cmd_status(args):
    if not TOC.exists():
        print(f"篇目檔還沒有：{TOC}")
        return
    toc = load_toc()
    pdfs = {p.stem for p in PDF_DIR.glob("*.pdf")} if PDF_DIR.exists() else set()
    txts = {p.stem for p in TEXT_DIR.glob("*.txt")} if TEXT_DIR.exists() else set()

    years = [int(r["year"]) for r in toc if r["year"].isdigit()]
    print(f"篇目　　{len(toc):>6}　（{min(years)}–{max(years)}）" if years else f"篇目 {len(toc)}")
    print(f"已下載　{len(pdfs):>6}　{len(pdfs) / len(toc) * 100:.1f}%")
    print(f"已抽字　{len(txts):>6}　{len(txts) / len(toc) * 100:.1f}%")

    by_decade = {}
    for r in toc:
        if r["year"].isdigit():
            d = int(r["year"]) // 10 * 10
            by_decade.setdefault(d, [0, 0])
            by_decade[d][0] += 1
            if r["slug"] in txts:
                by_decade[d][1] += 1
    print("\n年代　　篇目　已抽字")
    for d in sorted(by_decade):
        n, t = by_decade[d]
        print(f"{d}s　{n:>6}　{t:>6}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--toc", action="store_true", help="抓篇目")
    ap.add_argument("--fetch", action="store_true", help="下載 PDF")
    ap.add_argument("--text", action="store_true", help="抽文字層")
    ap.add_argument("--status", action="store_true", help="對帳")
    ap.add_argument("--limit", type=int, help="本輪上限（--fetch）")
    ap.add_argument("--force", action="store_true", help="重抽已有的 txt")
    a = ap.parse_args()

    if a.toc:
        cmd_toc(a)
    elif a.fetch:
        cmd_fetch(a)
    elif a.text:
        cmd_text(a)
    elif a.status:
        cmd_status(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
