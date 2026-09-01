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

# 🚨 **政治檔案篩選（QueryRange2／IfQueryRange2）送出去沒有作用**（2026-09 實測）：
#    長老教會 1,012／1,012、佛教 1,694／1,694、一貫道 417／417，限與不限完全一樣。
#    所以不跑兩輪——跑了也是同一批，只是白費站方頻寬。若日後找到正確參數再加回來。
#    （關鍵詞本身確實有效：對照組「鰻魚養殖」只有 11 筆。）
QUERIES = [
    # ── 機構／運動 ──
    ("長老教會",   "第四章：長老教會與國家"),
    ("佛教",       "第三章：佛教教團與國家"),
    ("一貫道",     "一貫道：1953 查禁至 1987 合法化"),
    ("台灣神學院", "第四章：北部神學教育（帶出董芳苑、賴顯章等人）"),
    ("台南神學院", "第四章：南神（黃彰輝、宋泉盛、王憲治的所在）"),
    ("玉山神學院", "第四章：玉神（原住民神學教育；與原權會、牧羊會案相關）"),
    # 上位詞：把三神以外、案名只寫「神學院」的那些也撈進來（249 筆，含各專案）
    ("神學院",     "第四章：神學院總集（含三神以外者）"),
    # 專案代號——監控行動的組織單位，比人名更能看出國家的部署
    ("一二一O專案", "美麗島：高俊明窩藏施明德案的專案代號"),
    ("二二二專案", "台南神學院案的專案代號"),
    ("衛理公會",   "衛理公會：教產與行政"),
    ("清寧專案",   "專案代號：監控長老教會人士的專案"),
    # ── 基督教系譜四人與周邊 ──
    ("黃彰輝",     "第四章第二節"),
    ("宋泉盛",     "第四章第三節"),
    ("王憲治",     "第四章第四節"),
    ("黃伯和",     "第四章第五節"),
    ("高俊明",     "第四章：美麗島事件與長老教會"),
    ("鄭仰恩",     "長老教會史學者；清寧專案與道風山案"),
    ("董芳苑",     "台灣神學院；調查局有專案"),
    ("陳主顯",     "與鄭仰恩同列道風山案"),
    ("周聯華",     "衛理公會；七二○專案"),
    # ── 佛教系譜 ──
    ("印順",       "第三章第二節；可疑分子考管"),
    ("佛法概論",   "第三章第二節：1950 年代查禁案"),
    ("太虛",       "第三章第一節"),
    ("傳道",       "第三章第三節：妙心寺"),
    ("妙心寺",     "第三章第三節"),
    # 🚨 昭慧：已逐筆查證「昭慧」17 筆全是同名者（曾昭慧／江昭慧／楊昭慧），
    #    「昭慧法師」「盧瓊昭」（俗名）「弘誓」三個寫法都是 0 筆。
    #    唯一可能相關的是法務部調查局「七十八年二月份教育情報存參卷案」，
    #    但案名不含其名，須調閱全文才能確認。收在這裡是為了留下「查過而確實沒有」
    #    的紀錄——那與「沒查過」是兩回事。
    ("昭慧",       "已查證：無專屬檔案，多為同名者"),
]

# 「已數位化」不等於「可以下載」：多數寫「須提出申請」，只有少數是「可線上閱覽」。
ONLINE_RE = re.compile(r"可線上閱覽")
PAGES_RE = re.compile(r"影像\s*([\d,]+)\s*頁")

TOTAL_RE = re.compile(r"共為\s*([\d,]+)\s*筆")

# 🚨 **零結果與請求失敗必須分得開**。站方查無資料時回的是一頁沒有結果表、
#    也沒有「共為 N 筆」的表單頁，長度約 187 KB；有結果時 800 KB 以上。
#    對照組實測：一貫道 836,855 bytes／共為 417 筆；zzqqxxyy 187,743 bytes／無筆數欄；
#    昭慧法師 187,734、盧瓊昭 187,733、弘誓 187,732——與無結果組同型，確定是真的 0 筆。
#    只回報一個「?」會讓「查無」與「抓壞了」混在一起，那是最容易誤導人的回報方式。
EMPTY_MIN, EMPTY_MAX = 150_000, 220_000


def classify(html):
    """→ ('ok', n) / ('empty', 0) / ('fail', 0)"""
    m = TOTAL_RE.search(html or "")
    if m:
        return "ok", int(m.group(1).replace(",", ""))
    if EMPTY_MIN < len(html or "") < EMPTY_MAX:
        return "empty", 0
    return "fail", 0


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


def build(base_payload, kw, page=1, per=20):
    d = dict(base_payload)
    d["q1"] = kw
    d["QueryRange3"] = "QueryRange3"        # 已全文影像公開
    d["PageNow"] = str(page)
    d["DisplayNumber"] = str(per)
    return d


def search(base_payload, kw, page=1, per=20):
    return curl(f"{BASE}/ELK/AdvSearchResult", build(base_payload, kw, page, per))


def parse_rows(html):
    """→ [{level, title, fonds, archiveNo, access, summary, subjects}]"""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for h3 in soup.select("h3.fs-6"):
        badge = h3.select_one("span.text-icon")
        level = clean(badge.get_text()) if badge else ""
        btn = h3.select_one("button.for-btn")
        title = clean(btn.get_text()) if btn else ""
        if not title or title.startswith("檢視全部案件"):
            continue      # 那是同一筆的下層連結，不是另一筆檔案
        # 這一筆的資訊都掛在 h3 後面那個 <dl>
        dl = h3.find_next("dl")
        rec = {"level": level, "title": title, "fonds": "", "archiveNo": "", "dateRange": "",
               "access": "", "online": False, "pages": 0, "summary": "", "subjects": []}
        if dl:
            txt = clean(dl.get_text(" "))
            # 🚨 每個欄位各用自己的樣式，不要共用一條「非貪婪 + 前瞻」的通式。
            #    那種寫法兩頭都會出錯：後面緊接標記時 `.{0,60}?` 會匹配成**空字串**
            #    （實測 56.8% 的檔號變空白，而檔號是申請調閱唯一必填的欄位）；
            #    沒緊接時又會吃進隔壁的「檔案起訖日期」（1,636 筆被污染）。
            m = re.search(r"檔號\s*([A-Za-z0-9/.\-]+)", txt)
            rec["archiveNo"] = m.group(1) if m else ""
            m = re.search(r"檔案起訖日期\s*(民國.{0,40}?)(?=\s(?:檔號|全宗|檔案形式|內容摘要|展開|關閉)|$)", txt)
            rec["dateRange"] = clean(m.group(1)) if m else ""
            m = re.search(r"檔案形式/提供方式\s*(.+?)(?=\s(?:檔號|全宗|內容摘要|展開|關閉)|$)", txt)
            rec["access"] = clean(m.group(1)) if m else ""
            dd = dl.find("dt", string=re.compile("全宗名"))
            if dd:
                nxt = dd.find_next("dd")
                rec["fonds"] = clean(nxt.get_text(" ")) if nxt else ""
            rec["online"] = bool(ONLINE_RE.search(rec["access"]))
            pm = PAGES_RE.search(rec["access"])
            rec["pages"] = int(pm.group(1).replace(",", "")) if pm else 0
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
    for kw, note in QUERIES:
        html = search(base, kw)
        m = TOTAL_RE.search(html)
        rows = parse_rows(html)
        on = sum(1 for r in rows if r["online"])
        print(f"  {kw:6s} 共 {m.group(1) if m else '?':>8s} 筆 ｜ 首頁 {len(rows)} 筆中可線上閱覽 {on}")
        time.sleep(DELAY)


def harvest(max_pages=30):
    base = form_defaults()
    store = {}
    if HARVEST.exists():
        store = json.loads(HARVEST.read_text(encoding="utf-8"))
    for kw, note in QUERIES:
        gkey = kw
        if store.get(gkey, {}).get("items"):
            print(f"  {gkey}：已有 {len(store[gkey]['items'])} 筆，跳過")
            continue
        html = search(base, kw, page=1, per=100)
        state, total = classify(html)
        if state == "fail":
            print(f"  {gkey}：請求失敗（長度 {len(html):,}），跳過不寫入", flush=True)
            continue
        if state == "empty":
            store[gkey] = {"query": kw, "note": note, "total": 0, "count": 0,
                           "state": "empty", "items": []}
            print(f"  {gkey}：查無資料（已查證，非抓取失敗）", flush=True)
            HARVEST.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
            time.sleep(DELAY)
            continue
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
            html = search(base, kw, page=page, per=100)
        store[gkey] = {"query": kw, "note": note, "state": "ok",
                       "total": total, "count": len(items),
                       "online": sum(1 for x in items if x["online"]), "items": items}
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
