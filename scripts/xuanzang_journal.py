# -*- coding: utf-8 -*-
"""玄奘佛學研究學報 收錄 pipeline（hcu.edu.tw，非 Cloudflare，純 requests）。

進「印順學派與弘誓研究資料」collection 的「玄奘佛學研究」子站。每期每篇一個 PDF
（hcu.edu.tw/Upload/TempFiles/<hex>.pdf，多為有文字層）→ 抽全文（掃描檔退 Gemini OCR）。

R2：yinshun-hongshi/玄奘佛學研究/<檔>.pdf（原檔）、yinshun-hongshi-fulltext/玄奘佛學研究/<檔>.txt
Drive canonical：G:\\…\\印順學派與弘誓研究資料\\玄奘佛學研究\\
index：public/content/research-data/yinshun-hongshi/xuanzang-index.json

  python -X utf8 scripts/xuanzang_journal.py --harvest        # 期/篇/pdf 清單
  python -X utf8 scripts/xuanzang_journal.py --process [--limit N]   # 下載+抽全文+上傳(冪等)
  python -X utf8 scripts/xuanzang_journal.py --publish        # 建 index.json
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

import requests
import fitz
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xuanzang as xz            # noqa: E402  pure: parse_issue_no
import hongshi as h              # noqa: E402  pure: pdf_text_sufficient
import dadaodao_fulltext as df   # noqa: E402  reuse .env / s3 / OCR engine

INDEX_URL = "https://www.hcu.edu.tw/ird/ird/zh-tw/religious-journal/"
BASE = "https://www.hcu.edu.tw"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/xuanzang_journal.json")
STAGE = Path(r"C:/tmp/xuanzang_dl"); STAGE.mkdir(parents=True, exist_ok=True)
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\玄奘佛學研究")
R2_PDF = "yinshun-hongshi/玄奘佛學研究"
R2_TXT = "yinshun-hongshi-fulltext/玄奘佛學研究"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/yinshun-hongshi/xuanzang-index.json"


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def get(url: str) -> requests.Response:
    last = None
    for attempt in range(5):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001  network/DNS blips → retry
            last = e
            time.sleep(5 * (attempt + 1))
    raise last


def harvest() -> list[dict]:
    soup = BeautifulSoup(get(INDEX_URL).text, "html.parser")
    issues = []
    for a in soup.find_all("a", href=True):
        t = clean(a.get_text())
        if "religious-journal/" in a["href"] and ("期" in t and "學報" in t):
            no = xz.parse_issue_no(t)
            if no:
                url = a["href"] if a["href"].startswith("http") else BASE + a["href"]
                issues.append({"issue": no, "title": t, "url": url})
    # dedupe by issue
    issues = list({i["issue"]: i for i in issues}.values())
    issues.sort(key=lambda x: -x["issue"])
    print(f"index: {len(issues)} issues ({issues[-1]['issue']}–{issues[0]['issue']})", flush=True)

    # resume: keep already-harvested issues (with articles) from a prior partial run
    prior = {}
    if HARVEST.exists():
        for x in json.loads(HARVEST.read_text(encoding="utf-8")):
            if x.get("articles"):
                prior[x["issue"]] = x
    for it in issues:
        if it["issue"] in prior:
            it["articles"] = prior[it["issue"]]["articles"]
            continue
        soup = BeautifulSoup(get(it["url"]).text, "html.parser")
        arts, seen = [], set()
        for a in soup.find_all("a", href=True):
            if ".pdf" not in a["href"].lower():
                continue
            if "file:" in a["href"].lower():        # editor-pasted local path, broken
                continue
            raw = a["href"] if a["href"].startswith("http") else BASE + a["href"]
            norm = unquote(raw)                       # %BD%9B… and readable form → same
            if norm in seen:
                continue
            seen.add(norm)
            pid = hashlib.md5(norm.encode("utf-8")).hexdigest()[:10]   # stable per real file
            par = a.find_parent(["tr", "li", "div"])
            label = clean(par.get_text(" ") if par else a.get_text())
            # descriptive filename (newer issues): NN-N類別：作者-題名.pdf → author/title
            fnm = unquote(norm.rsplit("/", 1)[-1])
            mf = re.match(r"\d+-\d+[^:：]*[:：]([^-]+)-(.+)\.pdf$", fnm, re.I)
            if mf:
                author, title = mf.group(1).strip(), mf.group(2).strip()
            else:
                author = ""
                title = re.split(r"[A-Za-z“\"]", label, 1)[0].strip(" —-‧·,，") or label
            arts.append({"pid": pid, "pdf": raw, "title": title[:80], "author": author[:30], "label": label[:160]})
        # collapse duplicate uploads: same article often appears as X.pdf AND X(1).pdf
        # (re-upload) plus encoded/decoded double-links → dedupe by normalised title.
        uniq = {}
        for a in arts:
            k = re.sub(r"[\(（]\s*\d+\s*[\)）]\s*$", "", a["title"]).strip()
            a["title"] = k
            if not k:
                continue
            # prefer a real http(s) link over an editor-pasted file:/// local path
            cur = uniq.get(k)
            if cur is None or (not cur["pdf"].lower().startswith("http") and a["pdf"].lower().startswith("http")):
                uniq[k] = a
        it["articles"] = list(uniq.values())
        print(f"  期{it['issue']}: {len(it['articles'])} articles ({len(arts)} raw)", flush=True)
        HARVEST.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")  # incremental
        time.sleep(1.0)
    HARVEST.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(i["articles"]) for i in issues)
    print(f"\nharvested {len(issues)} issues, {n} articles → {HARVEST}", flush=True)
    return issues


def fname(issue: int, pid: str) -> str:
    return f"玄奘佛學研究-v{issue:02d}-{pid}"


def drive_copy(stem: str, data: bytes) -> None:
    """Canonical copy to Drive — best-effort (G: streaming mount is flaky)."""
    try:
        DRIVE.mkdir(parents=True, exist_ok=True)
        (DRIVE / f"{stem}.pdf").write_bytes(data)
    except Exception:  # noqa: BLE001  G: not mounted → skip; R2 is the serving store
        pass


def process(limit: int = 0, no_ocr: bool = False):
    issues = json.loads(HARVEST.read_text(encoding="utf-8"))
    done = skip = ocr = fail = defer = 0
    strikes = 0
    for it in issues:
        for art in it["articles"]:
            stem = fname(it["issue"], art["pid"])
            txt_key = f"{R2_TXT}/{stem}.txt"
            if df.r2_exists(txt_key):
                skip += 1
                continue
            # skip broken source links (期45 has editor-pasted file:///C:/… local paths)
            if not re.match(r"https?://www\.hcu\.edu\.tw/.+\.pdf", art["pdf"], re.I):
                print(f"  ⏭ 期{it['issue']} {art['pid']} broken URL: {art['pdf'][:50]}", flush=True)
                fail += 1
                continue
            try:
                # download (canonical Drive + staging)
                local = STAGE / f"{stem}.pdf"
                if not (local.exists() and local.stat().st_size > 5000):
                    data = get(art["pdf"]).content
                    local.write_bytes(data)
                    drive_copy(stem, data)
                # upload original to R2
                df.s3.upload_file(str(local), df.R2_BUCKET, f"{R2_PDF}/{stem}.pdf",
                                  ExtraArgs={"ContentType": "application/pdf"})
                # extract text-layer / OCR
                doc = fitz.open(str(local)); n = doc.page_count
                txt = "".join(pg.get_text() for pg in doc); doc.close()
                if h.pdf_text_sufficient(txt, n):
                    df.r2_put_text(txt_key, txt.strip()); done += 1; strikes = 0
                    print(f"  ✓ 期{it['issue']} {art['pid']} [text] {len(txt)}c", flush=True)
                elif no_ocr:
                    defer += 1
                    print(f"  ⏭ 期{it['issue']} {art['pid']} 掃描檔，--no-ocr 延後 ({len(txt)}c text)", flush=True)
                else:
                    otext, eng = df.ocr_file(local, "application/pdf")
                    if not otext.strip():
                        print(f"  ∅ empty {stem}"); fail += 1; continue
                    df.r2_put_text(txt_key, otext.strip()); ocr += 1; strikes = 0
                    print(f"  ✓ 期{it['issue']} {art['pid']} [ocr:{eng}] {len(otext)}c", flush=True)
                if limit and (done + ocr) >= limit:
                    print(f"\n--limit {limit} reached", flush=True)
                    return
                time.sleep(0.8)
            except df.BothLimited:
                strikes += 1
                print(f"  ⏸ quota strike {strikes}/2", flush=True)
                if strikes >= 2:
                    print("2-strike 停機；重跑可接續。", flush=True); return
            except Exception as e:  # noqa: BLE001
                fail += 1
                print(f"  ✗ 期{it['issue']} {art['pid']}: {type(e).__name__}: {str(e)[:120]}", flush=True)
    print(f"\nDONE text {done}, ocr {ocr}, skipped {skip}, deferred {defer}, failed {fail}", flush=True)


def publish():
    issues = json.loads(HARVEST.read_text(encoding="utf-8"))
    out = []
    for it in issues:
        arts = []
        for art in it["articles"]:
            stem = fname(it["issue"], art["pid"])
            arts.append({
                "title": art["title"],
                "author": art.get("author", ""),
                "pdfKey": f"{R2_PDF}/{stem}.pdf",
                "hasFulltext": df.r2_exists(f"{R2_TXT}/{stem}.txt"),
            })
        out.append({"issue": it["issue"], "title": it["title"], "articles": arts})
    out.sort(key=lambda x: -x["issue"])
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    na = sum(len(i["articles"]) for i in out)
    nf = sum(1 for i in out for a in i["articles"] if a["hasFulltext"])
    print(f"index: {len(out)} issues, {na} articles, {nf} with fulltext → {INDEX_OUT.name}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-ocr", action="store_true", help="掃描檔（無文字層）延後，不跑 OCR")
    a = ap.parse_args()
    if a.harvest:
        harvest()
    if a.process:
        process(a.limit, a.no_ocr)
    if a.publish:
        publish()
    if not (a.harvest or a.process or a.publish):
        sys.exit("need --harvest / --process / --publish")
