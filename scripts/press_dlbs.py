# -*- coding: utf-8 -*-
"""臺大佛學數位圖書館（dlbs.liberal.ntu.edu.tw）→ 佛教期刊篇目。

全庫 520,393 筆、9,472 種期刊，是華藝與國圖之外量最大的一個，而且**開放取用**。
本檔只抓與博論章節對得上的那些刊（見 `JOURNALS`），不整庫鏡像。

🚨 **檢索走 Solr，不要爬 `search/default.jsp`。**
   那頁的 `<input id="q" value="">` 是空的——伺服器根本沒把查詢字串注進去，
   結果是前端 JS 讀 `location.search` 之後再打 Solr 填上去的。所以純 HTTP 打那支
   JSP **永遠回「0 筆查詢結果」，跟參數對不對無關**。這是我實測三輪才看穿的坑。

     GET https://dlbs.liberal.ntu.edu.tw/solr/mit/select
         ?q=SOURCETOPIC:"海潮音"&wt=json&rows=1000&start=0

🚨 **查詢字串要自己 percent-encode 再拼**。用 `requests` 的 `params=` 多半沒事，
   但 `curl -G --data-urlencode` 會讓它回 HTTP 500
   「URLDecoder: Invalid character encoding detected after position 2」。

🚨 這個 Solr 端點沒有任何 API 文件、沒有節流、直接暴露在外——**看起來是設定疏漏
   而不是有意開放的介面**。所以：一次性抓完落地，不要當成長期穩定的 API，
   也不要整庫鏡像後公開散布（站方版權聲明限個人及非商業使用）。

index：public/content/research-data/press/dlbs/<slug>.json

  python -X utf8 scripts/press_dlbs.py --harvest
  python -X utf8 scripts/press_dlbs.py --harvest --only 南瀛
"""
import argparse
import json
import re
import time
import urllib.parse
from pathlib import Path

import requests

SOLR = "https://dlbs.liberal.ntu.edu.tw/solr/mit/select"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "public/content/research-data/press/dlbs"
ROWS = 1000
DELAY = 1.5

# 按博論章節挑的刊。數字是 2026-09-06 用 facet.field=ST 實測的筆數。
JOURNALS = {
    # ── 第二章第五節　台灣（日治）：計畫書點名的南瀛佛教會就在這裡
    "nanying":        ("南瀛佛教", 10151),
    "nanying-hui":    ("南瀛佛教會會報", 1877),
    "taiwan-fojiao":  ("臺灣佛教", 2102),
    # ── 第二章第三節　中國（民國佛教）：太虛那一整圈
    "haichaoyin":     ("海潮音", 26220),
    "foxue-banyuekan": ("佛學半月刊", 20472),
    "jueyouqing":     ("覺有情", 6157),
    "honghua":        ("弘化月刊", 5949),
    "zhengxin":       ("正信", 5388),
    "zhongguo-fojiao": ("中國佛教", 3861),
    "jushilin":       ("世界佛教居士林林刊", 3826),
    "hongfashe":      ("弘法社刊", 3424),
    "juexun":         ("覺訊月刊", 3230),
    "sichuan":        ("四川佛教月刊", 2600),
    "zhongguo-fjh":   ("中國佛教會報", 2123),
    "renhaideng":     ("人海燈", 1925),
    "juequn":         ("覺群週報", 1546),
    "dayun":          ("大雲", 1496),
    "fojiao-gonglun": ("佛教公論", 1342),
    "weiyin":         ("威音", 1181),
    "fohua-xinqingnian": ("佛化新青年", 1103),
    # ── 第三章　戰後台灣佛教
    "rensheng":       ("人生", 8479),
    "putishu":        ("菩提樹", 3215),
    "xiangguang":     ("香光莊嚴", 2845),
    "huiju":          ("慧炬", 2769),
    "neiming":        ("內明", 2265),
    "hongshi":        ("弘誓", 1949),
    "shizihou":       ("獅子吼", 1557),
    "dasheng":        ("大乘", 1500),
    "faguang":        ("法光", 1319),
    "pumen":          ("普門學報", 1287),
    # ── 第五・六章　跨宗教與比較
    "bcs":            ("Buddhist-Christian Studies", 1188),
    "pew":            ("Philosophy East and West", 1170),
}

FIELDS = ("TOPIC,AUTHOR,SOURCETOPIC,ARCHIVE,PAGE,PRESSTIME,PRESSYEAR,"
          "BFULLTEXT,FULLTEXTPATH,SEQ,KEYWORD")


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s


def fetch(s, name, start):
    q = f'SOURCETOPIC:"{name}"'
    url = (f"{SOLR}?q={urllib.parse.quote(q, safe='')}"
           f"&wt=json&rows={ROWS}&start={start}&fl={urllib.parse.quote(FIELDS)}")
    r = s.get(url, timeout=180)
    r.raise_for_status()
    return r.json()["response"]


def harvest(s, slug, name, expected):
    arts, start, total = [], 0, None
    while True:
        resp = fetch(s, name, start)
        total = resp["numFound"] if total is None else total
        docs = resp["docs"]
        if not docs:
            break
        for d in docs:
            # 🚨 `SOURCETOPIC:"南瀛佛教"` 是 phrase 比對，會**連《南瀛佛教會會報》
            #    一起撈進來**（12,028 vs facet 的 10,151，差的 1,877 正好是會報）。
            #    不逐筆核對刊名的話，兩份刊會互相灌水、合併時還會重複計一次。
            #    臺大的 SOURCETOPIC 寫成「菩提樹=Bodhedrum」，比對取「=」前那半。
            got = (d.get("SOURCETOPIC") or "").split("=")[0].strip()
            if got != name:
                continue
            path = d.get("FULLTEXTPATH") or ""
            # 🚨 FULLTEXTPATH **有時絕對有時相對**，兩種都要處理，
            #    不然相對那批會被拼成 https://…/FULLTEXT/http://…/x.pdf 而 404。
            if path and not path.startswith("http"):
                path = "https://buddhism.lib.ntu.edu.tw" + ("" if path.startswith("/") else "/") + path
            arts.append({
                "seq": d.get("SEQ"), "title": d.get("TOPIC", ""),
                "author": d.get("AUTHOR", ""), "journal": d.get("SOURCETOPIC", ""),
                "archive": d.get("ARCHIVE", ""), "page": d.get("PAGE", ""),
                "presstime": d.get("PRESSTIME", ""), "year": d.get("PRESSYEAR", ""),
                "fulltext": str(d.get("BFULLTEXT", "0")) == "1",
                "path": path, "keyword": d.get("KEYWORD", ""),
            })
        start += len(docs)          # 用原始 docs 數推進，不是過濾後的筆數
        if start >= total:
            break
        time.sleep(DELAY)
    # 🚨 對照 facet 當初量到的數字。少收了而清單看起來一樣漂亮，是最貴的那種錯。
    if expected and abs(len(arts) - expected) > max(5, expected * 0.02):
        print(f"  ⚠ {name}：預期約 {expected}，實得 {len(arts)}——差太多，查一下",
              flush=True)
    years = [int(a["year"]) for a in arts if str(a.get("year", "")).isdigit()]
    data = {"slug": slug, "name": name, "source": SOLR,
            "counts": {"篇目": len(arts), "站上總數": total,
                       "有全文": sum(1 for a in arts if a["fulltext"]),
                       "缺卷期": sum(1 for a in arts if not a["archive"]),
                       "缺頁次": sum(1 for a in arts if not a["page"])},
            "years": {"min": min(years) if years else None,
                      "max": max(years) if years else None},
            "articles": arts}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    c = data["counts"]
    print(f"  {name[:22]:<24} {c['篇目']:>6} 篇（全文 {c['有全文']:>5}）"
          f" 缺卷期 {c['缺卷期']:>5} 缺頁 {c['缺頁次']:>5}  "
          f"{data['years']['min']}–{data['years']['max']}", flush=True)
    return data



# ---------------------------------------------------------------- 南瀛全文

# 《南瀛佛教》與《南瀛佛教會會報》的全文在臺大的「數位典藏」那一區，
# 不在 Solr 的 FULLTEXTPATH 指的地方。
#
# 🚨 FULLTEXTPATH 指到的是一個 **HTML frameset 檢視器**（477 bytes），
#    直接抓會拿到一段 <FRAMESET> 而不是內文——看起來像「這篇壞掉了」。
#    真正的內文在同目錄的 `ny{卷}-{期}.htm`，frameset 是靠 JS 拼出來的。
# 🚨 **全文是期別層不是單篇層**：1,877 筆《會報》篇目的 path 全指向同一組期別檔。
#    所以篇目照收（有卷期頁碼可引用），全文按期收。
# 🚨 **Big5**。用 UTF-8 讀會整片亂碼而 HTTP 一樣 200，跟 laijohn 那個坑同一類。
NY_BASE = "https://buddhism.lib.ntu.edu.tw/museum/TAIWAN/ny/"
NY_PREFIX = "research-private/nanying"
NY_INDEX = REPO / "public/content/research-data/press/nanying-index.json"
NY_ID_RE = re.compile(r"[?](ny[0-9-]+)$")


def _decode(raw):
    """Big5 與 UTF-8 都試，取替換字元少的那個。"""
    if raw[:3] == b"\xef\xbb\xbf":
        return raw[3:].decode("utf-8", "replace")
    cands = [(raw.decode(e, "replace"), e) for e in ("big5", "utf-8")]
    return min(cands, key=lambda c: c[0].count("�"))[0]


def _plain(html):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", html)
    t = re.sub(r"(?s)<[^>]+>", "\n", t)
    # 這批頁面把日文假名與異體字寫成 &#x30CE; 這種數值實體，不還原的話正文會缺字
    t = re.sub(r"&#x([0-9A-Fa-f]+);", lambda m: chr(int(m.group(1), 16)), t)
    t = re.sub(r"[ \t　]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def issue_ids():
    """從已抓好的篇目裡把期別代碼收集出來，不要另外去猜編號。"""
    ids = set()
    for slug in ("nanying", "nanying-hui"):
        f = OUT / f"{slug}.json"
        if not f.exists():
            continue
        for a in json.loads(f.read_text(encoding="utf-8"))["articles"]:
            m = NY_ID_RE.search(a.get("path") or "")
            if m:
                ids.add(m.group(1))
    return sorted(ids)


def nanying_fulltext(s):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    import dadaodao_fulltext as df

    ids = issue_ids()
    have = df.r2_existing_keys(NY_PREFIX)
    old_chars = {}
    if NY_INDEX.exists():
        old_chars = {r["issue"]: r.get("chars")
                     for r in json.loads(NY_INDEX.read_text(encoding="utf-8"))["issues"]}
    print(f"{len(ids)} 期（R2 已有 {len(have)}）")
    rows = []
    for i, iid in enumerate(ids, 1):
        key = f"{NY_PREFIX}/{iid}.txt.gz"
        toc, chars = [], 0
        r = s.get(f"{NY_BASE}{iid}toc.htm", timeout=90)
        if r.status_code == 200:
            toc = [x for x in _plain(_decode(r.content)).split("\n")
                   if x.strip() and not x.strip().isdigit()][1:]
        if key in have:
            # 🚨 續跑時不能把字數留成 None。第一版這樣寫，結果是**已經抓過的那幾期
            #    字數從統計裡消失**，總字數安靜地少報——而索引看起來一切正常。
            #    先沿用上一版索引記的數字，沒有才回 R2 取一次。
            prev = old_chars.get(iid)
            if prev is None:
                try:
                    prev = len(df.r2_get_text(key))
                except Exception:                 # noqa: BLE001
                    prev = None
            rows.append({"issue": iid, "toc": toc, "key": key, "chars": prev})
            continue
        time.sleep(DELAY)
        r = s.get(f"{NY_BASE}{iid}.htm", timeout=120)
        if r.status_code != 200:
            print(f"  ✗ {iid} HTTP {r.status_code}", flush=True)
            continue
        text = _plain(_decode(r.content))
        # 🚨 驗內容不是只驗狀態碼：解錯碼或抓到 frameset 都會是 200 而內容沒用
        if len(text) < 500 or "FRAMESET" in text.upper():
            print(f"  ✗ {iid} 內容不像正文（{len(text)} 字）", flush=True)
            continue
        df.r2_put_text_gz(key, text)
        chars = len(text)
        rows.append({"issue": iid, "toc": toc, "key": key, "chars": chars})
        print(f"  ✓ [{i}/{len(ids)}] {iid} {chars:>7,} 字 / 目次 {len(toc)} 條", flush=True)
        time.sleep(DELAY)
    NY_INDEX.write_text(json.dumps(
        {"name": "南瀛佛教（含南瀛佛教會會報）",
         "note": "日治台灣佛教的官方機關刊物，1923–1943。全文是**期別層**，"
                 "單篇的卷期頁碼在 dlbs/nanying*.json 的篇目層。"
                 "原始頁面是 Big5，已轉為繁體 UTF-8 存 R2。",
         "counts": {"期": len(rows), "字": sum(r["chars"] or 0 for r in rows)},
         "issues": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} 期 / {sum(r['chars'] or 0 for r in rows):,} 字 → {NY_INDEX.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--nanying-fulltext", action="store_true",
                    help="抓《南瀛佛教》161 期的期別全文（Big5 → R2）")
    a = ap.parse_args()
    if not (a.harvest or a.nanying_fulltext):
        ap.print_help()
        return
    s = session()
    if a.nanying_fulltext:
        nanying_fulltext(s)
        return
    for slug, (name, exp) in JOURNALS.items():
        if a.only and a.only not in name:
            continue
        if (OUT / f"{slug}.json").exists() and not a.only:
            continue                       # 可續跑
        time.sleep(DELAY)
        harvest(s, slug, name, exp)


if __name__ == "__main__":
    main()
