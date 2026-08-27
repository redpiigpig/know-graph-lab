# -*- coding: utf-8 -*-
"""《法印學報》收錄 pipeline（弘誓學院學報，但檔案掛在玄奘大學佛教學系網站）。

弘誓官網 2026 改版後舊路徑（hongshi.org.tw/userfiles/file/faryin N-M.pdf）全數 404，
新站典藏改走 blog feed 且尚未搬完；Wayback 只存到第 1 期的少數幾篇。目前可穩定取得的
是 hcu.edu.tw 佛教學系頁面上的第九～十三期（86 篇 PDF），本流程即取自該處。
其餘期數需另向學團索取——見 [[project_hcu_phd_proposal]]。

與 [[xuanzang_journal]] 同屬「印順學派與弘誓研究資料」collection，流程與之相同：
PDF 有文字層就直接抽，掃描檔才退 OCR。

R2：yinshun-hongshi/法印學報/<檔>.pdf、yinshun-hongshi-fulltext/法印學報/<檔>.txt
Drive canonical：G:\\…\\印順學派與弘誓\\法印學報\\
index：public/content/research-data/yinshun-hongshi/faryin-index.json

  python -X utf8 scripts/faryin_journal.py --harvest
  python -X utf8 scripts/faryin_journal.py --process [--limit N]
  python -X utf8 scripts/faryin_journal.py --publish
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote

import fitz
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hongshi as h              # noqa: E402  pure: pdf_text_sufficient
import dadaodao_fulltext as df   # noqa: E402  .env / s3 / OCR

BASE = "https://www.hcu.edu.tw"
INDEX_URL = (BASE + "/buddhism/buddhism/zh-tw/43C51435624E43D583779C031ACF4E2F"
                    "/28B89E27932B43858992AAA73F397629/?sh=")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
HARVEST = Path(r"C:/tmp/faryin_journal.json")
STAGE = Path(r"C:/tmp/faryin_dl"); STAGE.mkdir(parents=True, exist_ok=True)
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\法印學報")
R2_PDF = "yinshun-hongshi/法印學報"
R2_TXT = "yinshun-hongshi-fulltext/法印學報"
INDEX_OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/yinshun-hongshi/faryin-index.json"

CN_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u3000", " ")).strip()


def parse_issue_no(label: str):
    """「第十三期法印學報」→ 13。中文數字只到二十幾期，不必寫通用轉換。"""
    m = re.search(r"第([一二三四五六七八九十]+)期", label or "")
    if not m:
        m2 = re.search(r"第?(\d+)期", label or "")
        return int(m2.group(1)) if m2 else None
    s = m.group(1)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN_DIGITS.get(s[1:], 0)
    if s.endswith("十"):
        return CN_DIGITS.get(s[0], 0) * 10
    if "十" in s:
        a, b = s.split("十", 1)
        return CN_DIGITS.get(a, 0) * 10 + CN_DIGITS.get(b, 0)
    return CN_DIGITS.get(s)


def parse_filename(fnm: str):
    """「13-1法印-釋昭慧-「光明相」….pdf」→ ('釋昭慧', '「光明相」…')。
    分隔符 - 與 ： 混用，作者後面偶爾還有空白。取不出來就整串當題名。"""
    stem = re.sub(r"\.pdf$", "", fnm, flags=re.I)
    m = re.match(r"\s*\d+[-－]\d+\s*法印\s*[-－：:]\s*([^-－：:]{2,12})\s*[-－：:]\s*(.+)$", stem)
    if m:
        return clean(m.group(1)), clean(m.group(2))[:100]
    return "", clean(stem)[:100]


def parse_label(label: str):
    """目次列「題名 作者 起始頁」→ (作者, 題名)。

    第九～十二期的檔名只是 faryin12-1.pdf 這種流水號，題名只能從目次列取；
    第十三期反過來——檔名帶題名，目次列反而空白。兩邊都要能解。
    """
    t = clean(label)
    m = re.match(r"^(?P<title>.+?)\s+(?P<author>[^\s\d]+(?:[、,][^\s\d]+)*)\s+(?P<page>\d{1,3})$", t)
    if not m:
        return "", ""
    title = re.sub(r"\s+", "", m.group("title"))   # PDF 換行造成的題名內空白
    return clean(m.group("author")), title[:100]


def get(url: str) -> requests.Response:
    last = None
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=90)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(4 * (attempt + 1))
    raise last


def stem_for(issue: int, pdf_url: str) -> str:
    return f"faryin-{issue:02d}-{hashlib.md5(unquote(pdf_url).encode('utf-8')).hexdigest()[:10]}"


def harvest():
    soup = BeautifulSoup(get(INDEX_URL).text, "html.parser")
    issues = []
    for a in soup.select(".item_list_div .sub_title a[href]"):
        label = clean(a.get_text())
        no = parse_issue_no(label)
        if no:
            url = a["href"] if a["href"].startswith("http") else BASE + a["href"]
            issues.append({"issue": no, "title": label, "url": url})
    issues = list({i["issue"]: i for i in issues}.values())
    issues.sort(key=lambda x: -x["issue"])
    print(f"目錄：{len(issues)} 期（{issues[-1]['issue']}–{issues[0]['issue']}）", flush=True)

    for it in issues:
        d = BeautifulSoup(get(it["url"]).text, "html.parser")
        arts, seen = [], set()
        for a in d.find_all("a", href=True):
            href = a["href"]
            if ".pdf" not in href.lower():
                continue
            # 第13期整期被貼成 file:///C:/…（檔案沒上傳）。PDF 拿不到，但檔名裡的
            # 作者與題名還在，仍記成「有目無文」，日後另行索取。
            broken = href.lower().startswith("file:")
            raw = href if (broken or href.startswith("http")) else BASE + href
            norm = unquote(raw)
            if norm in seen:
                continue
            seen.add(norm)
            par = a.find_parent(["tr", "li", "div"])
            label = clean(par.get_text(" ") if par else a.get_text())
            fnm = unquote(norm.rsplit("/", 1)[-1])
            author, title = parse_filename(fnm)
            # 檔名只是流水號時（faryin12-1.pdf），改由目次列取題名與作者
            if re.fullmatch(r"faryin\d+[-－]\d+", title, re.I):
                la, lt = parse_label(label)
                if lt:
                    author, title = la, lt
            arts.append({
                "pdf": raw,
                "broken": broken,
                "stem": stem_for(it["issue"], raw),
                "file": fnm,
                "label": label[:160],
                "author": author,
                "title": title,
            })
        it["articles"] = arts
        print(f"  第{it['issue']}期：{len(arts)} 篇", flush=True)
        time.sleep(0.3)

    HARVEST.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"合計 {sum(len(i['articles']) for i in issues)} 篇 → {HARVEST}")


def process(limit=0):
    issues = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    DRIVE.mkdir(parents=True, exist_ok=True)
    done = ocr = skip = fail = 0
    for it in issues:
        for art in it["articles"]:
            stem = art["stem"]
            txt_key = f"{R2_TXT}/{stem}.txt"
            if art.get("broken") or txt_key in have:
                skip += 1
                continue
            try:
                local = STAGE / f"{stem}.pdf"
                if not (local.exists() and local.stat().st_size > 5000):
                    data = get(art["pdf"]).content
                    local.write_bytes(data)
                    (DRIVE / f"{stem}.pdf").write_bytes(data)
                df.s3.upload_file(str(local), df.R2_BUCKET, f"{R2_PDF}/{stem}.pdf",
                                  ExtraArgs={"ContentType": "application/pdf"})
                doc = fitz.open(str(local))
                pages = doc.page_count
                txt = "".join(pg.get_text() for pg in doc)
                doc.close()
                if h.pdf_text_sufficient(txt, pages):
                    df.r2_put_text(txt_key, txt.strip())
                    done += 1
                    print(f"  ✓ 期{it['issue']} {art['title'][:30]} [text] {len(txt)}c", flush=True)
                else:
                    otext, eng = df.ocr_file(local, "application/pdf")
                    if not otext.strip():
                        fail += 1
                        print(f"  ∅ {stem} OCR 空白", flush=True)
                        continue
                    df.r2_put_text(txt_key, otext.strip())
                    ocr += 1
                    print(f"  ✓ 期{it['issue']} {art['title'][:30]} [ocr:{eng}]", flush=True)
                if limit and (done + ocr) >= limit:
                    print(f"--limit {limit} 到達", flush=True)
                    return
                time.sleep(0.6)
            except Exception as e:  # noqa: BLE001
                fail += 1
                print(f"  ✗ 期{it['issue']} {art['title'][:30]}: {type(e).__name__}: {str(e)[:100]}", flush=True)
    print(f"\n完成 文字層 {done}、OCR {ocr}、既有 {skip}、失敗 {fail}", flush=True)


def publish():
    issues = json.loads(HARVEST.read_text(encoding="utf-8"))
    have = df.r2_existing_keys(R2_TXT)
    out = []
    for it in sorted(issues, key=lambda x: -x["issue"]):
        arts = [{
            "title": a["title"],
            "author": a.get("author", ""),
            "pdfKey": "" if a.get("broken") else f"{R2_PDF}/{a['stem']}.pdf",
            "hasFulltext": f"{R2_TXT}/{a['stem']}.txt" in have,
            "note": "站上連結誤植為本機路徑，原檔未上傳" if a.get("broken") else "",
            "source": "" if a.get("broken") else a["pdf"],
        } for a in it["articles"]]
        out.append({"issue": str(it["issue"]), "title": it["title"], "articles": arts})
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(x["articles"]) for x in out)
    ok = sum(1 for x in out for a in x["articles"] if a["hasFulltext"])
    print(f"{len(out)} 期 / {n} 篇（{ok} 篇有全文）→ {INDEX_OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.harvest:
        harvest()
    if args.process:
        process(args.limit)
    if args.publish:
        publish()
    if not (args.harvest or args.process or args.publish):
        ap.print_help()


if __name__ == "__main__":
    main()
