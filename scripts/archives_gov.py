# -*- coding: utf-8 -*-
"""國家檔案資訊網（檔案管理局 aa.archives.gov.tw）→ 政教關係史的一手公文書。

戒嚴時期國家如何處置宗教，證據不在報紙而在情治單位的公文裡：法務部調查局的
「佛、道、回教、一貫道情報案」、內政部警政署的「可疑分子考管」這類。這是論文
第四章（長老教會與國家）與第三章（佛教教團與國家）最硬的史料。

🚨 **一律透過 curl 送，不要用 Playwright 也不要用 requests**（2026-08/09 實測）。
   站方 WAF 認的是**客戶端指紋**，不是 IP：
   - Playwright：開 /ELK/SimpSearch 回一頁「The URL you requested has been blocked」
     （HTTP 仍是 200，所以只看狀態碼會誤判成成功）
   - Python requests：連 TLS 握手都被拒（SSLError / 連線重設）
   - curl：同一時間拿得到完整的 1.8 MB 搜尋頁
   先前誤判成「IP 被封鎖」而停跑一整天，其實是工具選錯。

🚨 **表單 36 個欄位要連同預設值一起送**。只挑幾個欄位 POST 的話，關鍵詞會被
   忽略而回傳整個資料庫（實測「長老教會」「佛教」「鰻魚養殖」都回 4,847,628 筆
   ——那是全站總數）。所以 payload 一律從實際表單解析出來再覆蓋 q1。
   驗法：拿一個不相干的詞（鰻魚養殖）當對照，數字不同才代表過濾生效。

🚨 **「已數位化」不等於「可以下載」**。單筆的「檔案形式/提供方式」欄常寫
   「數位化 (影像 N 頁) / 須提出申請」——那是要臨櫃或線上申請的，不是免費直取。
   本腳本只收書目與提供方式，不抓影像。

  python -X utf8 scripts/archives_gov.py --survey       # 各組筆數與提供方式分布
  python -X utf8 scripts/archives_gov.py --harvest      # 逐組翻頁取書目
"""
import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup

BASE = "https://aa.archives.gov.tw"
OUT = Path(__file__).resolve().parents[1] / "public/content/research-data"
HARVEST = Path(r"C:/tmp/archives_gov.json")
DELAY = 2.5          # 站方對密集請求敏感，慢慢來

# 每組＝(關鍵詞, 是否限政治檔案, 說明)。宗教管理類未必歸在政治檔案，
# 所以每個詞都跑「限政治檔案」與「不限」兩輪。
QUERIES = [
    ("長老教會", True,  "第四章：長老教會與國家"),
    ("長老教會", False, "第四章：長老教會與國家（不限政治檔案）"),
    ("佛教",     True,  "第三章：佛教教團與國家"),
    ("佛教",     False, "第三章：佛教教團與國家（不限政治檔案）"),
    ("一貫道",   True,  "一貫道：查禁至 1987 合法化"),
    ("一貫道",   False, "一貫道（不限政治檔案）"),
]

TOTAL_RE = re.compile(r"共為\s*([\d,]+)\s*筆")


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def curl(url, data=None, tries=3):
    """一律走 curl：站方擋 python 的 TLS 指紋（見檔頭）。

    POST 的 body 先在 Python 這邊 urlencode 好寫進暫存檔，用 --data @檔案 送，
    避免中文與 & = 在命令列上被殼層吃掉。
    """
    import subprocess, tempfile, os
    args = ["curl", "-s", "--max-time", "180",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/126 Safari/537.36",
            "-H", "Accept-Language: zh-TW,zh;q=0.9"]
    tmp = None
    if data is not None:
        body = urlencode(data, encoding="utf-8")
        fd, tmp = tempfile.mkstemp(suffix=".txt"); os.close(fd)
        Path(tmp).write_text(body, encoding="utf-8")
        args += ["-X", "POST",
                 "-H", "Content-Type: application/x-www-form-urlencoded",
                 "--data", "@" + tmp]
    args.append(url)
    try:
        for i in range(tries):
            r = subprocess.run(args, capture_output=True, timeout=200)
            out = r.stdout.decode("utf-8", "replace")
            if out.strip():
                return out
            time.sleep(2 ** i * 2)
        return ""
    finally:
        if tmp:
            try: os.unlink(tmp)
            except OSError: pass


def form_defaults():
    """把搜尋頁的表單原樣解析成 payload 骨架。

    🚨 一定要用這個而不是手寫欄位：少送欄位會讓關鍵詞被忽略（見檔頭）。
    """
    html = curl(f"{BASE}/ELK/SimpSearch")
    f = BeautifulSoup(html, "html.parser").find("form", {"id": "search-form"})
    if f is None:
        raise RuntimeError("找不到 search-form——多半是被擋了（回了 blocked 頁）")
    d = {}
    for el in f.find_all(["input", "select", "textarea"]):
        n = el.get("name")
        if not n:
            continue
        t = (el.get("type") or "").lower()
        if t in ("checkbox", "radio"):
            if el.has_attr("checked"):
                d[n] = el.get("value", "on")
        elif el.name == "select":
            sel = el.find("option", selected=True) or el.find("option")
            if sel is not None:
                d[n] = sel.get("value", "")
        elif t != "submit":
            d[n] = el.get("value", "")
    return d


def build(base_payload, kw, political, page=1, per=20):
    d = dict(base_payload)
    d["q1"] = kw
    d["QueryRange3"] = "QueryRange3"        # 已全文影像公開
    if political:
        d["QueryRange2"] = "1"
        d["IfQueryRange2"] = "1"            # 政治檔案：是
    d["PageNow"] = str(page)
    d["DisplayNumber"] = str(per)
    return d


def search(base_payload, kw, political, page=1, per=20):
    return curl(f"{BASE}/ELK/AdvSearchResult",
                build(base_payload, kw, political, page, per))


def parse_rows(html):
    """→ [{level, title, fonds, archiveNo, access, summary, subjects}]"""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for h3 in soup.select("h3.fs-6"):
        badge = h3.select_one("span.text-icon")
        level = clean(badge.get_text()) if badge else ""
        btn = h3.select_one("button.for-btn")
        title = clean(btn.get_text()) if btn else ""
        if not title:
            continue
        # 這一筆的資訊都掛在 h3 後面那個 <dl>
        dl = h3.find_next("dl")
        rec = {"level": level, "title": title, "fonds": "", "archiveNo": "",
               "access": "", "summary": "", "subjects": []}
        if dl:
            txt = clean(dl.get_text(" "))
            for label, key in (("全宗名", "fonds"), ("檔號", "archiveNo"),
                               ("檔案形式/提供方式", "access")):
                m = re.search(re.escape(label) + r"\s*(.{0,60}?)(?=\s(?:全宗名|檔號|檔案形式|全宗描述|內容摘要|展開|關閉)|$)", txt)
                if m:
                    rec[key] = clean(m.group(1))
            sm = dl.select_one("div.ellipsis-1")
            if sm:
                rec["summary"] = clean(sm.get_text(" "))[:400]
            kw_div = dl.select_one("div.collapse")
            if kw_div:
                rec["subjects"] = [x for x in clean(kw_div.get_text(" ")).split(" ") if x][:20]
        out.append(rec)
    return out


def survey():
    base = form_defaults()
    print(f"表單欄位 {len(base)} 個")
    # 對照組：不相干的詞。數字要與其他組不同，才代表過濾真的生效。
    ctrl = TOTAL_RE.search(search(base, "鰻魚養殖", False))
    print(f"對照組『鰻魚養殖』：{ctrl.group(1) if ctrl else '?'} 筆")
    time.sleep(DELAY)
    for kw, pol, note in QUERIES:
        html = search(base, kw, pol)
        m = TOTAL_RE.search(html)
        rows = parse_rows(html)
        acc = Counter(r["access"] or "(未標)" for r in rows)
        tag = "政治檔案" if pol else "不限    "
        print(f"  {kw:6s} {tag} 共 {m.group(1) if m else '?':>8s} 筆 ｜ 首頁提供方式：{dict(acc)}")
        time.sleep(DELAY)


def harvest(max_pages=30):
    base = form_defaults()
    store = {}
    if HARVEST.exists():
        store = json.loads(HARVEST.read_text(encoding="utf-8"))
    for kw, pol, note in QUERIES:
        gkey = f"{kw}|{'政治檔案' if pol else '不限'}"
        if store.get(gkey, {}).get("items"):
            print(f"  {gkey}：已有 {len(store[gkey]['items'])} 筆，跳過")
            continue
        html = search(base, kw, pol, page=1, per=100)
        m = TOTAL_RE.search(html)
        total = int(m.group(1).replace(",", "")) if m else 0
        items, seen = [], set()
        page = 1
        while page <= max_pages:
            rows = parse_rows(html)
            new = [r for r in rows if (r["archiveNo"], r["title"]) not in seen]
            for r in new:
                seen.add((r["archiveNo"], r["title"]))
            items += new
            # 終止條件看「這一頁有沒有帶回沒見過的筆」——站方翻過頭會重複回同一頁
            if not new or len(items) >= total:
                break
            page += 1
            time.sleep(DELAY)
            html = search(base, kw, pol, page=page, per=100)
        store[gkey] = {"query": kw, "political": pol, "note": note,
                       "total": total, "count": len(items), "items": items}
        print(f"  {gkey}：站上 {total} 筆，取回 {len(items)} 筆", flush=True)
        HARVEST.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(DELAY)
    print(f"\n{len(store)} 組 → {HARVEST}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--survey", action="store_true")
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--max-pages", type=int, default=30)
    a = ap.parse_args()
    if a.survey:
        survey()
    if a.harvest:
        harvest(a.max_pages)
    if not (a.survey or a.harvest):
        ap.print_help()


if __name__ == "__main__":
    main()
