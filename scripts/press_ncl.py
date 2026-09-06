# -*- coding: utf-8 -*-
"""國家圖書館「臺灣期刊論文索引系統」→ 佛教與宗教學期刊的**篇目索引**。

跟 `press_airiti.py` 是互補的兩半，不是二選一：

  華藝      有全文、有卷期頁碼，但**綁玄奘機構 IP**，且完全沒有戰後那批佛教老雜誌
  國圖      無全文（只有 9% 有 PDF），但**匿名可取、不綁 IP**，而且
            《海潮音》《人生》《獅子吼》《菩提樹》《香光莊嚴》《普門學報》
            這六份華藝一份都沒有的老雜誌，它全份收著且卷期頁碼一個不缺

最大的一份是《海潮音》4,995 筆、**1921–2026**（1920 年代就有 557 筆），
太虛創辦、橫跨百年——博論佛教軸源頭那一段的篇目，中文世界沒有第二個地方有。

index：public/content/research-data/press/ncl/<slug>.json

  python -X utf8 scripts/press_ncl.py --harvest
  python -X utf8 scripts/press_ncl.py --harvest --only 海潮音
  python -X utf8 scripts/press_ncl.py --summarize
"""
import argparse
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://tpl.ncl.edu.tw/NclService"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "public/content/research-data/press/ncl"
DELAY = 2.0

# slug → 刊名（就是 `書刊名` 欄位裡的精確值）
JOURNALS = {
    # ── 華藝完全沒有的佛教老雜誌，這一批是收國圖的全部理由
    "haichaoyin":     "海潮音",
    "rensheng":       "人生",
    "shizihou":       "獅子吼",
    "putishu":        "菩提樹",
    "xiangguang":     "香光莊嚴",
    "pumen":          "普門學報",
    "diguan":         "諦觀",
    "faguang":        "法光學壇",
    "dongfang":       "東方宗教研究",
    # ── 華藝也有，但國圖的 PDF 匿名可下載，取用成本低很多
    "chbs-journal":   "中華佛學學報",
    "chbs-studies":   "中華佛學研究",
    "ddbj":           "法鼓佛學學報",
    "ntu-buddhist":   "臺大佛學研究",
    "zhengguan":      "正觀",
    "yuanguang":      "圓光佛學學報",
    "fuyan":          "福嚴會訊",
    "fujen-religious": "輔仁宗教研究",
    "new-century":    "新世紀宗教研究",
    "religious-philosophy": "宗教哲學",
    "taiwan-religion": "臺灣宗教研究",
    "chinese-religions": "華人宗教研究",
    "folk-arts":      "民俗曲藝",
    "theology-church": "神學與教會",
    "taiwan-theology": "臺灣神學論刊",
    "yushan":         "玉山神學院學報",
    "ces-journal":    "華神期刊",
}

# 國圖**不收**的（各試過 3–4 種刊名寫法，全部真 0 筆）。
# 記在這裡是為了下次不要再查一遍，也為了別把「查不到」誤讀成「沒有這份刊」。
NOT_HELD = ["曠野", "新使者", "使者", "台灣教會公報", "臺灣教會公報",
            "基督教論壇報", "道雜誌"]


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": f"{BASE}/JournalQuery"})
    s.get(f"{BASE}/JournalQuery", timeout=60)      # 先建 session
    return s


def query(s, field, term, page_size=8000):
    """🚨 **整組表單參數都要帶**。只丟 `q[0].f` 與 `q[0].i` 會一律回 0 筆——
       看起來像「查無此刊」，其實是查詢根本沒成立。

       `pageSize` 沒有實質上限：送 8000 就一次把整刊拿回來，不必翻頁。
       （這也繞開了另一個坑：`page` 超過末頁會**夾到末頁而不是回空**，
       用「這頁有沒有新資料」當終止條件會無限迴圈。）
    """
    p = {"q[0].f": field, "q[0].i": term,
         "q[1].o": "0", "q[1].f": "*", "q[1].i": "",
         "lang": "", "mt": "", "pys": "", "pms": "", "pye": "", "pme": "",
         "pageSize": str(page_size)}
    return s.get(f"{BASE}/JournalContent", params=p, timeout=180).text


LABELS = [("title", "題　名："), ("author", "作　者："), ("journal", "書刊名："),
          ("vol", "卷　期："), ("page", "頁　次：")]
REC_MARK = "題　名："


def _fields(chunk_html):
    txt = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", chunk_html)
    txt = re.sub(r"(?s)<[^>]+>", "\n", txt)
    lines = [x.strip() for x in txt.split("\n") if x.strip()]
    rec = {}
    for key, lab in LABELS:
        try:
            rec[key] = lines[lines.index(lab) + 1]
        except (ValueError, IndexError):
            rec[key] = ""
    return rec


def parse(html):
    """逐筆切開再解析。

    🚨 **PDF 標記必須在原始 HTML 上判，不能在純文字化之後判**。
       那顆鈕的文字被包在圖片／樣式裡，`re.sub("<[^>]+>")` 之後就消失了——
       第一版在純文字上找「PDF全文」，442 筆全被判成沒有 PDF，
       而「0 篇有 PDF」看起來完全像個合理的結果。改成找 `pdfdownload` 連結。
    """
    parts = html.split(REC_MARK)[1:]          # 第 0 段是表頭
    recs = []
    for i, chunk in enumerate(parts):
        body = REC_MARK + chunk
        rec = _fields(body)
        if not rec.get("title"):
            continue
        rec["pdf"] = "pdfdownload" in chunk
        recs.append(rec)
    return recs


YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
MINGUO_RE = re.compile(r"民(\d{2,3})")


def year_of(vol):
    """卷期欄有三種寫法，**第三種只有民國年**。

    🚨 只抓西元四位數的話，《海潮音》早年那 2,900 多筆會全部被判成「沒有年份」，
       而 1920–40 年代正是太虛那一段——整批統計會安靜地少掉最要緊的部分。
    """
    m = YEAR_RE.search(vol or "")
    if m:
        return int(m.group(0))
    m = MINGUO_RE.search(vol or "")
    return int(m.group(1)) + 1911 if m else None


def harvest(s, slug, name):
    html = query(s, "JT", name)
    m = re.search(r"檢索結果筆數\s*\(([\d,]+)\)", re.sub(r"(?s)<[^>]+>", "", html))
    reported = int(m.group(1).replace(",", "")) if m else 0
    recs = parse(html)
    # 🚨 `JT` 是**子字串比對**：查「人生」會撈進《財富人生》《孔學與人生》，
    #    查「臺灣宗教研究」會混入《臺灣宗教研究通訊》。所以總筆數會灌水，
    #    一定要用 `書刊名` 精確過濾，不能直接信「檢索結果筆數」。
    # 🚨 站方會掛出「已超過系統最大設定值 (300)，系統僅顯示前面 300 筆」的警告。
    #    實測 pageSize 給足時那個警告**有顯示但沒有生效**（442 筆全數回傳），
    #    但不能靠這個假設過日子——比對「站上自報總數 vs 實際解析出的筆數」，
    #    短少就吼出來。少收了而清單看起來一樣漂亮，是這一類管線最貴的錯。
    if reported and len(recs) < reported:
        print(f"  ⚠ {name}：站上自報 {reported} 筆，只解析出 {len(recs)} 筆——被截斷了",
              flush=True)
    mine = [r for r in recs if (r.get("journal") or "").strip() == name]
    years = [y for y in (year_of(r.get("vol")) for r in mine) if y]
    data = {
        "slug": slug, "name": name, "source": f"{BASE}/JournalQuery",
        "counts": {"站上子字串命中": reported, "本刊實收": len(mine),
                   "有PDF": sum(1 for r in mine if r["pdf"]),
                   "缺卷期": sum(1 for r in mine if not r.get("vol")),
                   "缺頁次": sum(1 for r in mine if not r.get("page"))},
        "years": {"min": min(years) if years else None,
                  "max": max(years) if years else None},
        "articles": mine,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    c = data["counts"]
    print(f"  {name:<12} 實收 {c['本刊實收']:>5}"
          f"（站上子字串 {c['站上子字串命中']:>5}）"
          f" PDF {c['有PDF']:>4}  {data['years']['min']}–{data['years']['max']}", flush=True)
    return data


def summarize():
    rows = []
    for slug, name in JOURNALS.items():
        f = OUT / f"{slug}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        rows.append({"slug": slug, "name": name,
                     "articles": d["counts"]["本刊實收"], "pdf": d["counts"]["有PDF"],
                     "start": d["years"]["min"], "end": d["years"]["max"]})
    rows.sort(key=lambda r: -r["articles"])
    (OUT.parent / "ncl-index.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} 刊 / {sum(r['articles'] for r in rows):,} 篇目 "
          f"/ {sum(r['pdf'] for r in rows):,} 篇有 PDF → ncl-index.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--only", help="只抓刊名含這個字串的")
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    if a.harvest:
        s = session()
        for slug, name in JOURNALS.items():
            if a.only and a.only not in name:
                continue
            if (OUT / f"{slug}.json").exists() and not a.only:
                continue                      # 已抓過就跳過，可續跑
            time.sleep(DELAY)
            harvest(s, slug, name)
        summarize()
    elif a.summarize:
        summarize()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
