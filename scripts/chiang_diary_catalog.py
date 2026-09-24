# -*- coding: utf-8 -*-
"""兩蔣日記：抓國史館檔案史料文物查詢系統的「目錄節錄」（每日一件，內容描述照錄部分文字）。

    python -X utf8 scripts/chiang_diary_catalog.py            # 兩部都抓（已抓過的年份跳過）
    python -X utf8 scripts/chiang_diary_catalog.py --who 經國

只讀公開目錄，不碰影像。蔣經國日記影像標「僅供閱覽抄錄，禁止翻拍複製」，本腳本也不抓。
輸出：Drive 研究資料/政教關係/兩蔣日記目錄/<人>/<民國年>.jsonl（不進 git）
站方：ahonline.drnh.gov.tw；查詢參數是 JSON 以「Base64M」（標準 base64 把 / 換成 *）編進網址，
翻頁在網址後接 /<起>-<迄>，一次最多 100 件。每次請求間隔 2 秒。
"""
import argparse
import base64
import html
import json
import re
import subprocess
import tempfile
import time
import urllib.parse
from pathlib import Path

OUT = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/研究資料/政教關係/兩蔣日記目錄")
SITE = "https://ahonline.drnh.gov.tw/index.php"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
DIARIES = {"中正": ("蔣中正日記原本民國{}年", range(7, 44)),
           "經國": ("蔣經國日記原本民國{}年", range(26, 50))}
DELAY = 2.0


def b64m(s):
    return base64.b64encode(s.encode("utf-8")).decode().replace("/", "*")


class Client:
    def __init__(self):
        self.jar = Path(tempfile.gettempdir()) / "ahonline_jar.txt"
        self.get(f"{SITE}?act=Archive")

    def get(self, url):
        time.sleep(DELAY)
        r = subprocess.run(["curl", "-sSL", "-m", "120", "-c", str(self.jar), "-b", str(self.jar),
                            "-A", UA, url], capture_output=True)
        return r.stdout.decode("utf-8", "ignore")


def search_url(term, rng):
    q = {"accnum": None, "query": [{"field": "_all", "value": term}], "domconf": {}}
    return f"{SITE}?act=Archive/search/{urllib.parse.quote(b64m(json.dumps(q, ensure_ascii=False)))}/{rng}"


FIELD = re.compile(r"\n » (典藏號|本件日期|內容描述|卷名)\n(.*?)(?=\n » |\nTAG|\Z)", re.S)


def parse(page_html):
    t = html.unescape(re.sub(r"<[^>]+>", "\n", page_html))
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    rows = []
    for blk in re.split(r"\n\. \d+ \n", t)[1:]:
        kind = blk.split("\n", 1)[0].strip()
        if kind != "件":
            continue
        f = {}
        for k, v in FIELD.findall("\n" + blk):
            f.setdefault(k, re.sub(r"\s*\n\s*", "", v).strip())
        if f.get("典藏號"):
            rows.append({"id": f["典藏號"], "date": f.get("本件日期", ""),
                         "title": f.get("卷名", ""), "text": f.get("內容描述", "")})
    return rows


def harvest(c, who, tmpl, year):
    dest = OUT / who / f"{year:02d}.jsonl"
    if dest.exists() and dest.stat().st_size > 0:
        return None
    term = tmpl.format(year)
    seen, out, start = set(), [], 1
    while True:
        rows = parse(c.get(search_url(term, f"{start}-{start + 99}")))
        # 只收這一年這部日記的件（全欄位搜尋會混進別的卷）
        rows = [r for r in rows if term.replace("原本", "") in r["title"].replace("原本", "")
                or term in r["title"]]
        new = [r for r in rows if r["id"] not in seen]
        if not new:
            break
        for r in new:
            seen.add(r["id"])
        out += new
        start += 100
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        for r in sorted(out, key=lambda x: x["id"]):
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--who", choices=list(DIARIES))
    ap.add_argument("--years", help="只抓這些民國年，逗號分隔")
    a = ap.parse_args()
    c = Client()
    for who, (tmpl, years) in DIARIES.items():
        if a.who and who != a.who:
            continue
        for y in years:
            if a.years and str(y) not in a.years.split(","):
                continue
            n = harvest(c, who, tmpl, y)
            print(f"蔣{who} 民國{y}年：{'已有，跳過' if n is None else f'{n} 件'}", flush=True)


if __name__ == "__main__":
    main()
