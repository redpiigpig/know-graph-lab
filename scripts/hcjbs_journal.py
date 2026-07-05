# -*- coding: utf-8 -*-
"""玄奘佛學研究學報 —— 公開官網 (/Hsuan_Chuang_Studies) 期刊資料 harvest。

來源：hcu.edu.tw religious-journal（非 Cloudflare，純 requests）。與 research-data 的
xuanzang_journal.py 不同：此處產出「公開站」用的 issues.json（含封面圖、篇名、作者、
頁數、官方 PDF 連結），並把每期封面縮圖下載到 public/ 自我 host。

輸出：
  public/Hsuan_Chuang_Studies/covers/vNN.jpg      每期封面 (400x560)
  public/content/Hsuan_Chuang_Studies/issues.json  期→[篇]

  python -X utf8 scripts/hcjbs_journal.py
"""
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xuanzang as xz  # noqa: E402  pure: parse_issue_no

BASE = "https://www.hcu.edu.tw"
INDEX = f"{BASE}/ird/ird/zh-tw/religious-journal/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 Safari/537.36"}
ROOT = Path(__file__).resolve().parents[1]
COVERS = ROOT / "public/Hsuan_Chuang_Studies/covers"
OUT = ROOT / "public/content/Hsuan_Chuang_Studies/issues.json"
COVERS.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)


def get(url: str) -> requests.Response:
    last = None
    for i in range(5):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(4 * (i + 1))
    raise last


def clean(s: str) -> str:
    return re.sub(r"[ \t　]+", " ", re.sub(r"[\r\n]+", " ", s or "")).strip()


_IDEO = re.compile(r"[一-鿿぀-ヿ]")  # 中日表意文字＋假名（不含標點）
# 中文題名尾端可接的標點／年代括號（裁切時一併保留，但遇拉丁字母即停）
_ZH_TAIL = re.compile(r"^[）】」』》〉。，、！？：；…\s\d\-–—－()（）]*")


def strip_en(title: str) -> str:
    """裁掉題名尾端的英文譯名：英譯永遠接在完整中文題名之後。
    以「最後一個中日表意字」為錨，再吞掉其後屬於中文題名的括號／年代
    （如「（1961-2016）」），一遇拉丁字母即停。純英文題名整條保留。"""
    ideo = list(_IDEO.finditer(title))
    if not ideo:
        return title.strip()  # 純英文題名
    end = ideo[-1].end()
    end += _ZH_TAIL.match(title[end:]).end()
    return title[:end].strip()


def abs_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return BASE + href


def harvest_index() -> list[dict]:
    soup = BeautifulSoup(get(INDEX).text, "html.parser")
    out = {}
    for a in soup.find_all("a", href=True):
        t = clean(a.get_text())
        if "religious-journal/" in a["href"] and "期" in t and "學報" in t:
            no = xz.parse_issue_no(t)
            if no and no not in out:
                out[no] = {"issue": no, "url": abs_url(a["href"])}
    return [out[k] for k in sorted(out, reverse=True)]


def cover_url(soup: BeautifulSoup) -> str | None:
    """第一張 cms 圖即封面縮圖；升到 400x560 portrait。"""
    for img in soup.find_all("img", src=True):
        m = re.search(r"/ird/img/cms/\d+/\d+/(\d+/\d{4}-\d{2}/\S+\.(?:jpg|jpeg|png))", img["src"], re.I)
        if m:
            return f"{BASE}/ird/img/cms/400/560/{m.group(1)}"
    return None


def parse_articles(soup: BeautifulSoup) -> list[dict]:
    det = soup.find("div", class_="detail")
    tbl = det.find("table") if det else None
    if not tbl:
        return []
    arts = []
    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) != 3:
            continue  # 略過章節標題(colspan)、出版日期、表頭
        title_td, author_td, page_td = tds
        page = clean(page_td.get_text())
        if page in ("頁數", "") or not re.search(r"\d", page):
            continue  # 表頭 or 無頁數
        anchors = title_td.find_all("a")
        # 中文題名 = 整格文字裁掉尾端英文譯名
        title = strip_en(clean(title_td.get_text(" ")))
        # 官方 PDF：跳過 file:/// 本機路徑，取第一個正常 .pdf
        pdf = ""
        for a in anchors:
            h = a.get("href", "")
            if ".pdf" in h.lower() and not h.lower().startswith("file:"):
                pdf = abs_url(h)
                break
        # 作者：CJK 名無內部空白 → 任何空白皆為多作者分隔，統一「、」
        author = "、".join(clean(author_td.get_text(" ")).replace("、", " ").split())
        arts.append({"title": title, "author": author, "page": page, "pdf": pdf})
    return arts


def main():
    issues = harvest_index()
    print(f"index: {len(issues)} issues ({issues[-1]['issue']}–{issues[0]['issue']})", flush=True)
    result = []
    for it in issues:
        soup = BeautifulSoup(get(it["url"]).text, "html.parser")
        cov = cover_url(soup)
        arts = parse_articles(soup)
        cover_path = ""
        if cov:
            ext = ".png" if cov.lower().endswith(".png") else ".jpg"
            fn = f"v{it['issue']:02d}{ext}"
            dest = COVERS / fn
            try:
                if not dest.exists():
                    dest.write_bytes(get(cov).content)
                cover_path = f"/Hsuan_Chuang_Studies/covers/{fn}"
            except Exception as e:  # noqa: BLE001
                print(f"  期{it['issue']} cover fail: {e}", flush=True)
        result.append({
            "issue": it["issue"],
            "url": it["url"],
            "cover": cover_path,
            "articles": arts,
        })
        print(f"  期{it['issue']:>2}: {len(arts)} 篇  cover={'✓' if cover_path else '✗'}", flush=True)
        time.sleep(1.2)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(r["articles"]) for r in result)
    print(f"\n→ {OUT}  ({len(result)} 期 / {n} 篇)", flush=True)


if __name__ == "__main__":
    main()
