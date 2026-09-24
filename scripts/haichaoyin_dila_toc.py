"""法鼓 DILA「民國佛教期刊文獻集成」資料庫 →《海潮音》全部篇目 TSV。

- 逐頁抓 search.php?journalName=海潮音&edition=MFQ&start=N（每頁 30 筆），HTML 才有「原刊卷號 v.／原刊頁碼」；
  dl.php 的整批匯出沒有卷號與原刊頁，不能用。
- 快取每頁 HTML 到 output/haichaoyin/dila_pages/（可中斷續跑）。
- 產出 Drive 正編夾 _篇目_海潮音_集成.tsv。
"""
import csv, html, re, sys, time, urllib.parse
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "haichaoyin" / "dila_pages"
OUT = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\正編\_篇目_海潮音_集成.tsv")
BASE = "http://buddhistinformatics.dila.edu.tw/minguofojiaoqikan/search.php"
UA = "know-graph-lab research (redpiigpig@gmail.com)"


def page(s, start):
    f = CACHE / f"{start:06d}.html"
    if f.exists() and f.stat().st_size > 2000:
        return f.read_text(encoding="utf-8")
    url = f"{BASE}?journalName={urllib.parse.quote('海潮音')}&edition=MFQ&start={start}"
    for i in range(5):
        try:
            r = s.get(url, timeout=60)
            r.raise_for_status()
            t = r.content.decode("utf-8", "replace")
            if "resultItem" not in t and "回傳結果" not in t:
                raise RuntimeError("頁面不含結果")
            f.write_text(t, encoding="utf-8")
            time.sleep(1.0)
            return t
        except Exception as e:
            print(f"  start={start} 失敗 {e}", flush=True)
            time.sleep(10 * (i + 1))
    raise RuntimeError(f"start={start} 抓不到")


def text(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()


def parse(t):
    out = []
    for blk in re.split(r'<div class="resultItem">', t)[1:]:
        blk = blk.split('<hr class="tailHr"')[0]
        idm = re.search(r'<a href="#top" title="(\d+)"', blk)
        title = re.search(r'<div class="paperTitle">(.*?)</div>', blk, re.S)
        infos = [text(x) for x in re.findall(r'<div class="showItemInfo">(.*?)</div>', blk, re.S)]
        d = {"dila_id": idm.group(1) if idm else ""}
        tt = text(title.group(1)) if title else ""
        m = re.match(r"(\d+)\s+(.*)", tt)
        d["序"], d["篇名"] = (m.group(1), m.group(2)) if m else ("", tt)
        d["篇名"] = d["篇名"].strip("『』")
        for inf in infos:
            if inf.startswith("叢刊資訊"):
                m = re.search(r"vol\.\s*(\d+)\s*,\s*p\.\s*([\w~\-?]+)", inf)
                d["集成冊"], d["集成頁"] = (m.group(1), m.group(2)) if m else ("", inf)
            elif inf.startswith("原書資訊"):
                body = inf.split("：", 1)[1]
                v = re.search(r"v\.\s*([\w\-]+)", body)
                n = re.search(r"no\.\s*([\w\-/~]+)", body)
                p = re.search(r"p\.\s*([\w~\-]+)", body)
                d["原刊卷"] = v.group(1) if v else ""
                d["原刊期"] = n.group(1) if n else ""
                d["原刊頁"] = p.group(1) if p else ""
                parts = [x.strip() for x in body.split(",")]
                d["日期"] = parts[-1] if parts and not re.match(r"(v\.|no\.|p\.|海潮音)", parts[-1]) else ""
                d["原書資訊原文"] = body
            elif inf.startswith("文章類別"):
                d["類別"] = inf.split("：", 1)[1].strip()
            elif inf.startswith("作者"):
                a = inf.split("：", 1)[1].strip()
                d["作者"] = "" if "無記作者" in a else a
        out.append(d)
    return out


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    s = requests.Session(); s.headers["User-Agent"] = UA
    first = page(s, 0)
    total = int(re.search(r"<span>(\d+)筆</span>", first).group(1))
    print(f"DILA《海潮音》共 {total} 筆", flush=True)
    rows = []
    for start in range(0, total, 30):
        rows += parse(page(s, start))
        if start % 1500 == 0:
            print(f"  {start}/{total}", flush=True)
    print(f"解析 {len(rows)} 筆（站上 {total}）", flush=True)
    if len(rows) != total:
        print("⚠ 筆數不符", flush=True)
    cols = ["dila_id", "序", "篇名", "作者", "集成冊", "集成頁", "原刊卷", "原刊期", "原刊頁", "日期", "類別", "原書資訊原文"]
    tmp = OUT.with_name(OUT.name + ".part")
    with open(tmp, "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    tmp.replace(OUT)
    print("寫出", OUT, flush=True)


if __name__ == "__main__":
    main()
