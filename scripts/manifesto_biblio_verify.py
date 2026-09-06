# -*- coding: utf-8 -*-
"""逐筆核實《神學研究宣言》研究資料庫的書目，並回填開放取用連結。

這份書目是照十二章章目策展出來的，不是從資料庫撈的——也就是說每一筆的年份、
出處、甚至「這本書存不存在」都還沒有外部依據。書目寫錯不像程式會報錯，它會安靜
地一路長到正文的註腳裡，所以入庫前一律先過這一關。

三段查核，先命中先算：
  1. Crossref   —— 出版社自己存的書目（DOI 齊、不限流）。
  2. Open Library —— 一九六〇年代以前的專書與非英語原版（Otto 1917、Caillois 1939
     這類）OpenAlex 常常沒有，但圖書館編目有。
  3. OpenAlex   —— 前兩者落空才問。它附 OA 全文連結，最值錢，但也**最容易把整批查詢
     打成 429**（實測連跑兩輪後整個 IP 進冷卻，一小時內每一筆都失敗）。排最後就是為了
     讓它只承擔少量請求。

🚨 查不到 ≠ 不存在。古典文獻（偽狄奧尼修斯）與非英語原版在這三個庫的覆蓋本來就薄，
   所以本檔只把結果分成「已核實／年份有出入／查無」三欄印出來，交人判讀，
   絕不自動刪改任何一筆。

  python -X utf8 scripts/manifesto_biblio_verify.py            # 核實並印報告
  python -X utf8 scripts/manifesto_biblio_verify.py --write-oa # 另把 OA 連結寫回 md
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import lit_review as lr  # noqa: E402

REPORT = ROOT / "scripts/data/lit_review_theological_studies_manifesto.md"
AUDIT = ROOT / "output/manifesto_biblio_audit.json"
MAIL = "redpiigpig@gmail.com"
# 題名相似度門檻：副標題常被各庫切掉或補上，比對只取主標的前段，0.72 是把
# 「Comparative Theology」對上「Comparative Theology: Deep Learning...」放行、
# 又不至於把同作者的另一本書誤判成同一本的位置。
SIM_OK = 0.72


# 各庫的編目慣例不一致，冠詞常被吃掉（Open Library 收的是 "Power of the Sacred"，
# 報告寫的是 "The Power of the Sacred"）。不剝掉冠詞，前綴比對整條失效，Joas 與
# Comte-Sponville 就是這樣被誤判成「查無此書」的。
_LEADING_ARTICLE = re.compile(
    r"^(the|a|an|le|la|les|l|der|die|das|il|lo|el|los|las|de|het)\s+")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return _LEADING_ARTICLE.sub("", s)


def _sim(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return 0.0
    # 一方是另一方的前綴（主標 vs 主標＋副標）就算滿分
    if a.startswith(b) or b.startswith(a):
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _titles(entry_title: str) -> list[str]:
    """主標＋全題兩式都試：各庫對副標的收錄不一致。"""
    out = [entry_title]
    head = entry_title.split(":", 1)[0].strip()
    if head and head != entry_title:
        out.append(head)
    return out


class LookupFailed(Exception):
    """查詢本身失敗（限流、逾時、非 JSON）——與「查無此書」是兩回事。"""


def _get(url: str, tries: int = 4) -> dict:
    """🚨 千萬不要把查詢失敗吞成空結果。三個庫都會在流量一大時回 429／503，
    而空結果與「這本書不存在」在下游長得一模一樣——上一版就是這樣把 Levinas
    《Totalité et infini》報成查無此書的。所以這裡退避重試，重試完還是失敗就拋，
    讓那一筆標成『查詢失敗』而不是『查無』。"""
    last = ""
    for i in range(tries):
        r = subprocess.run(
            ["curl", "-sk", "-m", "60", "-w", "\n%{http_code}",
             "-A", f"kgl-biblio ({MAIL})", url], capture_output=True)
        body, _, code = r.stdout.decode("utf-8", "replace").rpartition("\n")
        code = code.strip()
        if code == "200":
            try:
                return json.loads(body)
            except Exception:  # noqa: BLE001
                last = "回的不是 JSON"
        else:
            last = f"HTTP {code or '無回應'}"
        time.sleep(2 * (i + 1))
    raise LookupFailed(last)


def openalex(title: str) -> dict | None:
    q = urllib.parse.quote(title[:200])
    d = _get(f"https://api.openalex.org/works?search={q}&per-page=5&mailto={MAIL}")
    best = None
    for w in d.get("results", []) or []:
        s = _sim(title, w.get("title") or "")
        if s >= SIM_OK and (best is None or s > best[0]):
            oa = (w.get("best_oa_location") or {}) or {}
            best = (s, {
                "source": "openalex", "sim": round(s, 2),
                "title": w.get("title"), "year": w.get("publication_year"),
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                "oa_url": oa.get("pdf_url") or oa.get("landing_page_url") or "",
                "is_oa": bool((w.get("open_access") or {}).get("is_oa")),
            })
    return best[1] if best else None


def crossref(title: str) -> dict | None:
    q = urllib.parse.quote(title[:200])
    d = _get(f"https://api.crossref.org/works?query.bibliographic={q}&rows=5&mailto={MAIL}")
    for it in (d.get("message", {}) or {}).get("items", []) or []:
        t = (it.get("title") or [""])[0]
        s = _sim(title, t)
        if s >= SIM_OK:
            parts = (it.get("issued", {}) or {}).get("date-parts", [[None]])
            return {"source": "crossref", "sim": round(s, 2), "title": t,
                    "year": parts[0][0] if parts and parts[0] else None,
                    "doi": it.get("DOI", ""), "oa_url": "", "is_oa": False}
    return None


def openlibrary(title: str, author: str) -> dict | None:
    q = urllib.parse.quote(f"{title[:150]} {author.split(',')[0]}")
    d = _get(f"https://openlibrary.org/search.json?q={q}&limit=5"
             "&fields=title,first_publish_year,author_name,key")
    for doc in d.get("docs", []) or []:
        s = _sim(title, doc.get("title") or "")
        if s >= SIM_OK:
            return {"source": "openlibrary", "sim": round(s, 2),
                    "title": doc.get("title"), "year": doc.get("first_publish_year"),
                    "doi": "", "oa_url": "", "is_oa": False,
                    "olid": doc.get("key", "")}
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-oa", action="store_true",
                    help="把查到的開放取用連結寫回報告的『全文』行")
    a = ap.parse_args()

    md = REPORT.read_text(encoding="utf-8")
    entries = lr.parse_review_report(md)["entries"]
    print(f"書目 {len(entries)} 筆，開始核實……\n", flush=True)

    rows = []
    for i, e in enumerate(entries, 1):
        hit, failed = None, False
        for t in _titles(e["title"]):
            try:
                hit = (crossref(t) or openlibrary(t, e["authors"])
                       or openalex(t))
            except LookupFailed as exc:
                failed = True
                print(f"    ⚠ 查詢失敗（{exc}）：{t[:60]}", flush=True)
            if hit:
                break
        drift = None
        if hit and hit.get("year") and e.get("year"):
            drift = hit["year"] - e["year"]
        if hit:
            status = "版本年份不同" if drift and abs(drift) > 1 else "已核實"
        else:
            status = "查詢失敗" if failed else "查無"
        rows.append({**e, "hit": hit, "drift": drift, "status": status})
        mark = {"已核實": "✓", "版本年份不同": "~", "查無": "✗", "查詢失敗": "!"}[status]
        extra = ""
        if hit and hit.get("is_oa"):
            extra = "  [OA]"
        if drift and abs(drift) > 1:
            extra += f"  報告 {e['year']} → 查得 {hit['year']}"
        print(f"  {mark} [{i:3d}] {e['authors'][:28]:28s} {e['title'][:52]:52s}{extra}",
              flush=True)
        time.sleep(1.0)   # 三個庫都禮貌池，衝太快換來的是 429 不是速度

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    c = Counter(r["status"] for r in rows)
    oa = sum(1 for r in rows if (r["hit"] or {}).get("is_oa"))
    print(f"\n已核實 {c['已核實']}／版本年份不同 {c['版本年份不同']}／"
          f"查無 {c['查無']}／查詢失敗 {c['查詢失敗']}　　可直接取得全文 {oa}")
    if c["查無"]:
        print("\n查無的（古典文獻與非英語原版屬正常，其餘要人工確認）：")
        for r in rows:
            if r["status"] == "查無":
                print(f"  · {r['authors']}（{r['year']}）{r['title'][:70]}")
    if c["年份有出入"]:
        print("\n年份有出入的：")
        for r in rows:
            if r["status"] == "年份有出入":
                print(f"  · {r['authors']}：報告 {r['year']} → {r['hit']['year']}"
                      f"　{r['title'][:56]}")

    if a.write_oa:
        n = 0
        for r in rows:
            url = (r["hit"] or {}).get("oa_url")
            if not url or not (r["hit"] or {}).get("is_oa"):
                continue
            head = f"【{r['authors']}】"
            idx = md.find(head)
            if idx < 0:
                continue
            end = md.find("\n\n", idx)
            block = md[idx:end]
            if "全文" in block:
                continue
            md = md[:end] + f"\n- 全文：[開放取用]({url})" + md[end:]
            n += 1
        REPORT.write_text(md, encoding="utf-8")
        print(f"\n→ 回填 {n} 筆開放取用連結至 {REPORT.relative_to(ROOT)}")
    print(f"→ 稽核明細 {AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
