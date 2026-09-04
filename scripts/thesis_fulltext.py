# -*- coding: utf-8 -*-
"""依論文編號取碩博士論文全文 PDF（NDLTD → 各校機構典藏 → PDF）。

🚨 **碩博士論文網（ndltd.ncl.edu.tw）本身不放全文**。它的詳目頁只寫
   「連結至畢業學校之論文網頁　註：此連結為研究生畢業學校所提供，
     **不一定有電子全文可供下載**」
   全文的授權與存放都在各校手上，國圖只做書目與轉介。所以路徑是三段：

     論文編號 → NDLTD 詳目頁 → 各校典藏 handle → PDF

🚨 **NDLTD 的驗證碼只擋「檢索」，不擋「已知編號的詳目頁」**。
   `thesis_ndltd.py --search` 常年卡驗證碼，但帶 id 直接開詳目
   （`gsweb.cgi/login?o=dnclcdr&s=id="105NCCU5183008".&searchmode=basic`）
   完全暢通。要批次取全文就走這條，不要再去撞檢索。

🚨 **「有電子全文」不等於拿得到**。NDLTD 那個標記只代表檔案存在，實際分三種：
   ① 公開取用　② 校內限閱　③ 有償授權／未授權公開。
   實例：台大〈台灣基督長老教會政治論述之分析〉標有電子全文，詳目頁卻寫
   「全文授權：有償授權　ntu-99-1.pdf 未授權公開取用」——抓不到，而且不該抓。
   本腳本遇到這種一律記下原因跳過，不繞過。

🚨 **DSpace 的 PDF 網址陷阱**：政大是 `/bitstream/`，`/bitstream2/` 會回
   HTML 錯誤頁但狀態碼仍是 200——存下來是 33 KB 的假 PDF。所以下載後一定要
   驗 `%PDF` 開頭與頁數，不能只看 HTTP 200。

  python -X utf8 scripts/thesis_fulltext.py --id 105NCCU5183008
  python -X utf8 scripts/thesis_fulltext.py --shortlist --limit 5
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[1]
SHORTLIST = REPO / "public/content/research-data/pct/thesis-shortlist.json"
OUT = Path("G:/我的雲端硬碟/資料/知識圖工作室/研究資料/博論參考文獻/全文")
LEDGER = Path("C:/tmp/thesis_fulltext.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "Chrome/126 Safari/537.36")
DELAY = 3.0
# 🚨 這個直接網址「按題名查」也一樣不擋驗證碼，所以**不需要論文編號**。
#    （我們的書目是從結果頁的純文字解析出來的，本來就沒抓到編號。）
NDLTD_ID = ('https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login'
            '?o=dnclcdr&s=id=%22{q}%22.&searchmode=basic')
NDLTD_TI = ('https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login'
            '?o=dnclcdr&s=ti=%22{q}%22.&searchmode=basic')

# 詳目頁上代表「拿不到」的字樣。命中就跳過並記下原因。
BLOCKED = ["未授權公開取用", "有償授權", "校內電子全文", "不公開", "已授權校內"]

# curl -w 的輸出接在內容尾巴，用一個不會出現在網頁裡的標記切開
MARK = chr(10) + "__CURL_FINAL__"


# 各校機構典藏。**NDLTD 的轉介連結只有少數學校提供**（實測 9 筆只有政大那 1 筆有），
# 所以不要靠它——直接到各校典藏按題名查才是通例。
#
# 🚨 每一校的搜尋路徑與 PDF 路徑都不同，沒有共通規則：
#    南華 /simple-search?query= → 詳目頁的 PDF 在 /retrieve/
#    政大 handle 會 302 到 ah.lib.nccu.edu.tw，PDF 在 /bitstream/（不是 /bitstream2/）
# 🚨 台大等校即使有 PDF 連結，詳目頁可能寫「全文授權：有償授權　未授權公開取用」，
#    那種一律跳過不抓。
REPOS = {
    "南華大學":     {"base": "https://nhuir.nhu.edu.tw",     "search": "/simple-search?query="},
    # 🚨 政大 2026 已換新系統：舊的 /simple-search 回 200 但永遠 0 筆，
    #    要用 /browse-item?item_name=，詳目也不是 /handle/ 而是 /item?item_id=
    #    2026-09 又發現：browse-item 是對題名做**子字串**比對，題名裡有 ── 或
    #    (1945-2008) 就查不到，而且**查不到時不是回 0 筆，是回一批不相干的 25 筆**。
    #    所以政大這一路必須開詳目頁比對 <title> 的中文題名（verify_title），
    #    絕不可以拿搜尋結果第一筆就用。
    "國立政治大學": {"base": "https://ah.lib.nccu.edu.tw", "search": "/browse-item?item_name=",
                     "link": "item?item_id=", "verify_title": True},
    "國立臺灣大學": {"base": "https://tdr.lib.ntu.edu.tw",    "search": "/jspui/simple-search?query="},
    "國立中央大學": {"base": "https://ir.lib.ncu.edu.tw",     "search": "/simple-search?query="},
}


def norm(t):
    """比對用：去空白與各種標點，全形半形不計。"""
    return re.sub(r"[\s　~～—–\-－:：，,。、《》「」『』（）()【】\[\]〈〉·・.]+", "", t or "")


def repo_search(school, title):
    """在該校典藏按題名查，回詳目頁網址。查不到回空字串。

    🚨 比對不能用「前 N 字完全相同」。各校著錄的題名與 NDLTD 常有出入
    （破折號用 ~ 或 －、副標點號不同、空白位置不同），用嚴格比對會把
    找得到的也判成查無——實測 32 筆裡有 9 筆是這樣誤殺的。
    改成正規化後看「誰包含誰」，再退到前段字元重疊率。
    """
    from urllib.parse import quote
    r = REPOS.get(school)
    if not r:
        return ""
    key = norm(title)
    # 查詢詞也要挑：整句丟進去反而查不到，取前段最有辨識度的一段
    for q in (title[:24], title[:14], title[:8]):
        html = curl(r["base"] + r["search"] + quote(q))
        s = BeautifulSoup(html, "html.parser")
        best, cands = ("", 0.0), []
        pat = r.get("link", "/handle/")
        for a in s.find_all("a", href=True):
            if pat not in a["href"]:
                continue
            cand = norm(a.get_text(" ", strip=True))
            if not cand or len(cand) < 6:
                continue
            if r.get("verify_title"):
                # 連結文字是英文題名，比不了中文 → 收集起來待會逐一開詳目頁核對
                cands.append(a["href"] if a["href"].startswith("http") else r["base"] + a["href"])
                continue
            if key in cand or cand in key:
                score = 1.0
            else:
                n = min(len(key), len(cand), 20)
                score = sum(1 for i in range(n) if key[i] == cand[i]) / n if n else 0
            if score > best[1]:
                h = a["href"]
                best = (h if h.startswith("http") else r["base"] + h, score)
        # 政大：開詳目頁看 <title>，中文題名對得上才算。上限 8 筆免得白跑一輪 25 次
        for u in cands[:8]:
            t2 = BeautifulSoup(curl(u), "html.parser").title
            got = norm((t2.get_text(strip=True) if t2 else "").split("|")[0])
            if got and (key in got or got in key):
                return u
        if best[1] >= 0.75:
            return best[0]
    return ""


def curl(url, binary=False, referer=None, tries=3, want_final=False):
    """want_final=True 時另回「轉址後的最終網址」。

    🚨 相對路徑的 PDF 連結要用**轉址後**的網域來組。政大的 handle 掛在
       nccur.lib.nccu.edu.tw，但會 302 到 ah.lib.nccu.edu.tw；拿原始網域去組
       就得到不存在的位址，而站方對它回 HTML＋200，看起來像成功。
    """
    args = ["curl", "-sk", "-L", "--max-time", "180", "-A", UA,
            "-w", MARK + "%{url_effective}"]
    if referer:
        args += ["-e", referer]
    args.append(url)
    for i in range(tries):
        r = subprocess.run(args, capture_output=True)
        if r.stdout:
            raw = r.stdout
            idx = raw.rfind(MARK.encode())
            final = raw[idx + len(MARK):].decode("utf-8", "replace").strip() if idx >= 0 else url
            body = raw[:idx] if idx >= 0 else raw
            out = body if binary else body.decode("utf-8", "replace")
            return (out, final) if want_final else out
        time.sleep(2 ** i)
    empty = b"" if binary else ""
    return (empty, url) if want_final else empty


def ndltd_record(key, by="ti"):
    """→ {title, repoUrl, blocked}。key 可以是論文編號或題名。"""
    from urllib.parse import quote
    tmpl = NDLTD_ID if by == "id" else NDLTD_TI
    html = curl(tmpl.format(q=quote(key)))
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style"]):
        t.decompose()
    txt = re.sub(r"\s+", " ", s.get_text(" "))
    repo = ""
    for a in s.find_all("a", href=True):
        t = " ".join(a.get_text(" ", strip=True).split())
        if "點我開啟" in t or "畢業學校" in t:
            repo = a["href"]
            break
    return {"title": (s.title.get_text(strip=True).split("__")[0] if s.title else ""),
            "repoUrl": repo,
            "blocked": next((b for b in BLOCKED if b in txt), "")}


def find_pdf(repo_url):
    """在機構典藏詳目頁找 PDF。回 (pdf_url, 擋住的原因)。"""
    html, final = curl(repo_url, want_final=True)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style"]):
        t.decompose()
    txt = re.sub(r"\s+", " ", s.get_text(" "))
    blocked = next((b for b in BLOCKED if b in txt), "")
    m = re.match(r"(https?://[^/]+)", final or repo_url)   # 用轉址後的網域
    base = m.group(1) if m else ""
    for a in s.find_all("a", href=True):
        h = a["href"]
        if ".pdf" in h.lower() or "bitstream" in h.lower():
            # 🚨 /bitstream2/ 回 HTML 但狀態碼 200；一律改用 /bitstream/
            h = h.replace("/bitstream2/", "/bitstream/")
            return (h if h.startswith("http") else base + h), blocked
    return "", blocked


def is_pdf(blob):
    return len(blob) > 50_000 and blob[:4] == b"%PDF"


def fetch(tid, by="ti", school=""):
    # 先走各校典藏（通例），NDLTD 轉介只當備援（僅少數學校提供）
    if school and school in REPOS:
        repo = repo_search(school, tid)
        if repo:
            pdf, blocked = find_pdf(repo)
            if blocked:
                return {"id": tid, "title": tid, "repoUrl": repo,
                        "status": f"典藏頁標示：{blocked}"}
            if pdf:
                blob = curl(pdf, binary=True, referer=repo)
                if is_pdf(blob):
                    OUT.mkdir(parents=True, exist_ok=True)
                    name = re.sub(r'[\/:*?"<>|]', "_", tid)[:70]
                    path = OUT / f"{name}.pdf"
                    path.write_bytes(blob)
                    return {"id": tid, "title": tid, "repoUrl": repo, "status": "OK",
                            "bytes": len(blob), "path": str(path)}
    rec = ndltd_record(tid, by)
    if rec["blocked"]:
        return {**rec, "id": tid, "status": f"NDLTD 標示：{rec['blocked']}"}
    if not rec["repoUrl"]:
        return {**rec, "id": tid, "status": "NDLTD 未提供學校典藏連結"}
    pdf, blocked = find_pdf(rec["repoUrl"])
    if blocked:
        return {**rec, "id": tid, "status": f"典藏頁標示：{blocked}"}
    if not pdf:
        return {**rec, "id": tid, "status": "典藏頁找不到 PDF 連結"}
    blob = curl(pdf, binary=True, referer=rec["repoUrl"])
    if not is_pdf(blob):
        return {**rec, "id": tid, "status": f"抓到的不是 PDF（{len(blob)} bytes）"}
    OUT.mkdir(parents=True, exist_ok=True)
    name = re.sub(r'[\\/:*?"<>|]', "_", rec["title"])[:70] or tid
    path = OUT / f"{name}_{tid}.pdf"
    path.write_bytes(blob)
    return {**rec, "id": tid, "status": "OK", "bytes": len(blob), "path": str(path)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    ap.add_argument("--title")
    ap.add_argument("--shortlist", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    led = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
    ids = []
    if a.id:
        ids = [a.id]
    elif a.title:
        ids = [a.title]
    elif a.shortlist:
        d = json.loads(SHORTLIST.read_text(encoding="utf-8"))
        # 沒有論文編號就用題名查——直接網址對題名一樣不擋驗證碼
        ids = [(x["title"], x["school"]) for x in d["items"] if x.get("fulltext")]
    if not ids:
        ap.print_help()
        return
    for i, item in enumerate(ids, 1):
        if a.limit and i > a.limit:
            break
        tid, school = item if isinstance(item, tuple) else (item, "")
        if tid in led:
            continue
        r = fetch(tid, "id" if a.id else "ti", school)
        led[tid] = r
        LEDGER.write_text(json.dumps(led, ensure_ascii=False, indent=1), encoding="utf-8")
        mark = "✔" if r["status"] == "OK" else "✗"
        print(f"  {mark} {r.get('title','')[:38]}　{r['status']}", flush=True)
        time.sleep(DELAY)


if __name__ == "__main__":
    main()
