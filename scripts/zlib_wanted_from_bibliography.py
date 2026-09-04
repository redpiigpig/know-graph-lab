#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把所有論文與寫作計畫的參考書目變成 z-library 獵書清單。

四個來源，加起來三千多筆：
  1. `lit_review_entries`（2,748 筆）—— 各計畫的研究回顧書目，結構化欄位齊全
  2. `data/doctoral_thesis_references.json`（252 筆）—— 博論計畫的徵引，引文字串
  3. `public/content/works/degree-bibliographies.json` —— 碩士與學士論文的徵引，
     自由文本，分節（佛典／專書／期刊…）

🚨 書目不等於獵書目標。三類東西進了清單只會每天空跑：
  * **期刊論文**：z-library 是書庫。venue 是 Nature / Journal of… / Trends in… 的
    一律不收。判準是 venue 像期刊還是像出版社，不能只看「有沒有 venue」——
    這個欄位同時被拿來裝 Oxford University Press 和 Nature。
  * **線上百科**：Stanford Encyclopedia of Philosophy 一家就 371 筆，它沒有實體書。
  * **已經有的書**：先跟館藏 4,600 本與既有獵表 1,444 筆比對過再收。

  python scripts/zlib_wanted_from_bibliography.py --stats   # 只看會收幾筆
  python scripts/zlib_wanted_from_bibliography.py           # 寫出 data/zlib-wanted/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

_CJK = re.compile(r"[一-鿿]")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

from ingest_new_books import URL, SB_HEADERS

OUT = ROOT / "data" / "zlib-wanted" / "bibliography.jsonl"
THESIS_REFS = ROOT / "data" / "doctoral_thesis_references.json"
DEGREE_BIBS = ROOT / "public" / "content" / "works" / "degree-bibliographies.json"

# venue 看起來像期刊／百科／預印本 → 不是書，別收
_NOT_A_BOOK = re.compile(
    r"encyclopedia|journal|quarterly|review\b|bulletin|proceedings|annals|"
    r"\barxiv\b|biorxiv|preprint|newsletter|magazine|gazette|"
    r"nature|science$|^science\b|cell\b|lancet|trends in|"
    r"學報|期刊|雙月刊|季刊|月刊|通訊|會訊|論文集刊|研討會",
    re.I)

# venue 看起來像出版社 → 是書
_IS_PUBLISHER = re.compile(
    r"press\b|verlag|routledge|blackwell|brill|springer|wiley|palgrave|"
    r"harper|penguin|random house|norton|macmillan|sage|"
    r"books?$|publish|editions?\b|"
    r"出版|書局|文化|書店|書館|印經|叢書",
    re.I)

# 這些標題本身就不是可獵的書
_SKIP_TITLE = re.compile(
    r"^大[正藏]|大正新脩|卍新纂|^聲明書$|座談會|宣言書?$|新聞稿|"
    r"^https?://|\.html?$|維基|wikipedia",
    re.I)


def looks_like_book(title: str, venue: str | None) -> bool:
    """這一筆值不值得拿去 z-library 找。純函式，見 tests。"""
    t = (title or "").strip()
    if len(t) < 4:
        return False
    if _SKIP_TITLE.search(t):
        return False
    v = (venue or "").strip()
    if not v:
        return True                      # 沒填 venue 的多半是專書
    if _NOT_A_BOOK.search(v):
        return False
    if _IS_PUBLISHER.search(v):
        return True
    # 兩邊都不像：venue 很短（一兩個詞）通常是出版社縮寫，長的多半是期刊全名
    return len(v.split()) <= 3


def norm_key(*parts: str) -> str:
    s = unicodedata.normalize("NFKC", " ".join(p or "" for p in parts)).lower()
    s = re.sub(r"[\s　·‧・:：,，.。/／\-–—()（）\[\]「」《》〈〉'\"]+", "", s)
    return s


def stable_id(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]


# 作者欄常見的雜訊：書名跟在冒號後、頭銜與角色後綴、轉引註記
_AUTHOR_CUT = re.compile(r"[;；,，&：:／/。〈〉《》]|\s+and\s+|—\s*引自|引自")
_AUTHOR_TRAIL = re.compile(r"(著|編著|編譯|主編|編|譯注|譯註|譯|撰|輯|校注|校訂)+$")


MAX_AUTHOR = 30


def clean_author(a: str) -> str:
    """把作者欄裡的雜訊削掉，只留人名。

    🚨 中文書目常寫成「王明：《太平經合校》」——冒號當分隔，不切就會把書名
    當成作者，害 who 閘永遠對不上、每一筆都空跑。
    """
    a = re.sub(r"[（(].*?[)）]", "", str(a or ""))
    a = _AUTHOR_CUT.split(a)[0]
    a = _AUTHOR_TRAIL.sub("", a.strip())
    a = a.strip(" .。、·‧")
    # 切不乾淨的（整段引文、含標點）與其下一個錯的 who 閘，不如留空：
    # who 閘一錯就是每一筆都查無，白跑搜尋還看不出原因。
    return "" if len(a) > MAX_AUTHOR else a


def first_author(authors) -> str:
    """作者欄可能是字串或陣列；取第一位，並剝掉括號裡的原文名。"""
    if isinstance(authors, list):
        a = authors[0] if authors else ""
    else:
        a = authors or ""
    return clean_author(a)


def parse_citation(text: str) -> tuple[str, str]:
    """從引文字串裡挖出 (書名, 作者)。中文用《》，西文用斜體無從辨識，退而取
    第一個逗號前的字串當作者、引號內或最長片段當書名。"""
    t = (text or "").strip()
    m = re.search(r"[《〈]([^》〉]{2,80})[》〉]", t)
    title = m.group(1).strip() if m else ""
    if not title:
        m2 = re.search(r"[“\"]([^”\"]{4,120})[”\"]", t)
        title = m2.group(1).strip() if m2 else ""
    author = clean_author(t) if t else ""
    if not title:
        # 西文引文：作者. 年. 書名. 出版社. → 取第二段
        segs = [s.strip() for s in re.split(r"\.\s+", t) if s.strip()]
        cand = [s for s in segs if len(s) > 12 and not re.match(r"^\(?\d{4}\)?$", s)]
        title = cand[1] if len(cand) > 1 else (cand[0] if cand else "")
    return title.strip(" .。"), author.strip(" .。")


# --------------------------------------------------------------------------- sources

def from_lit_review() -> list[dict]:
    rows, off = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/lit_review_entries"
                         f"?select=project_slug,title,authors,year,language,venue"
                         f"&offset={off}&limit=1000", headers=SB_HEADERS, timeout=90)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    out = []
    for x in rows:
        if not looks_like_book(x.get("title"), x.get("venue")):
            continue
        out.append({"title": (x.get("title") or "").strip(),
                    "author": first_author(x.get("authors")),
                    "lang": x.get("language") or "",
                    "source": f"biblio-{x['project_slug']}"})
    return out


def from_thesis_refs() -> list[dict]:
    if not THESIS_REFS.exists():
        return []
    d = json.loads(THESIS_REFS.read_text(encoding="utf-8"))
    out = []
    for x in d.get("references", []):
        title = (x.get("title") or "").strip()
        author = ""
        if x.get("citation"):
            t2, a2 = parse_citation(x["citation"])
            title = title or t2
            author = a2
        if not looks_like_book(title, None):
            continue
        out.append({"title": title, "author": author,
                    "lang": "zh" if x.get("language_group") == "中文" else "",
                    "source": "biblio-hcu-phd"})
    return out


def from_degree_bibs() -> list[dict]:
    if not DEGREE_BIBS.exists():
        return []
    d = json.loads(DEGREE_BIBS.read_text(encoding="utf-8"))
    out = []
    for g in d.get("groups", []):
        slug = g.get("key") or "degree"
        for it in g.get("items", []):
            # 佛典那一節是大藏經，站內 /tripitaka 已有全文，不必外求
            if (it.get("section") or "").strip() in ("佛典", "藏經", "經典"):
                continue
            title, author = parse_citation(it.get("text") or "")
            if not looks_like_book(title, None):
                continue
            out.append({"title": title, "author": author, "lang": "",
                        "source": f"biblio-{slug}"})
    return out


def parse_biblio_li(li_html: str) -> tuple[str, str]:
    """講義章節「參考資料」的一個 <li> → (書名, 作者)。

    兩種體例混在同一份清單裡：
      中文  林鴻信，《基督宗教思想史》下冊，臺北：國立臺灣大學出版中心，2017。
      西文  George M. Marsden, <em>Fundamentalism and American Culture</em>, 2nd ed. …
    西文靠 <em> 標書名（可靠）；中文靠《》。兩者都沒有就不是書目，跳過。
    """
    m = re.search(r"<em>(.*?)</em>", li_html, re.S)
    if m:
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        before = re.sub(r"<[^>]+>", "", li_html[: m.start()])
        author = clean_author(before)
        return title, author
    plain = re.sub(r"<[^>]+>", "", li_html).strip()
    m2 = re.search(r"《([^》]{2,80})》", plain)
    if m2:
        return m2.group(1).strip(), clean_author(plain.split("《")[0])
    return "", ""


_BIBLIO_H = re.compile(r"<h[1-6][^>]*>\s*(參考資料|參考書目|延伸閱讀|推薦閱讀|徵引書目)\s*</h[1-6]>", re.I)


def from_lecture_chapters() -> list[dict]:
    """講義／專書章節 HTML 裡的「參考資料」清單。

    千面上帝、基督宗教概論、他者的上帝這幾個計畫在 lit_review_entries 是 0 筆，
    書目只存在於章節檔裡，不撈這裡就整個漏掉。
    """
    out = []
    base = ROOT / "public" / "content" / "works"
    for f in sorted(base.rglob("*.html")):
        try:
            s = f.read_text(encoding="utf-8")
        except Exception:
            continue
        slug = f.relative_to(base).parts[0]
        for m in _BIBLIO_H.finditer(s):
            tail = s[m.end(): m.end() + 20000]
            block = tail.split("</ul>")[0] if "<ul" in tail[:200] or "<li" in tail[:400] else ""
            for li in re.findall(r"<li[^>]*>(.*?)</li>", block, re.S):
                title, author = parse_biblio_li(li)
                if not looks_like_book(title, None):
                    continue
                out.append({"title": title, "author": author, "lang": "",
                            "source": f"biblio-{slug}"})
    return out


# --------------------------------------------------------------------------- dedupe

def held_titles() -> set[str]:
    """館藏（含全集）已有的書名，正規化後當作比對鍵。"""
    keys, off = set(), 0
    while True:
        r = requests.get(f"{URL}/rest/v1/ebooks?select=title,author&offset={off}&limit=1000",
                         headers=SB_HEADERS, timeout=90)
        r.raise_for_status()
        b = r.json()
        for x in b:
            keys.add(norm_key(x.get("title")))
        if len(b) < 1000:
            break
        off += 1000
    return keys


def existing_wanted() -> set[str]:
    p = ROOT / "output" / "zlib_wanted_all.jsonl"
    if not p.exists():
        return set()
    out = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        out.add(norm_key(d.get("expect") or "", d.get("who") or ""))
        out.add(norm_key(d.get("expect") or ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    import author_blacklist

    raw = (from_lit_review() + from_thesis_refs() + from_degree_bibs()
           + from_lecture_chapters())
    print(f"三個來源合計 {len(raw)} 筆（已濾掉期刊／百科／藏經）", flush=True)

    held = held_titles()
    wanted = existing_wanted()
    print(f"館藏 {len(held)} 種書名、既有獵表 {len(wanted)} 個鍵，開始比對…", flush=True)

    seen, out, drop = set(), [], {"重複": 0, "已有館藏": 0, "已在獵表": 0, "黑名單": 0}
    for x in raw:
        k = norm_key(x["title"], x["author"])
        if k in seen:
            drop["重複"] += 1
            continue
        seen.add(k)
        if norm_key(x["title"]) in held:
            drop["已有館藏"] += 1
            continue
        if k in wanted or norm_key(x["title"]) in wanted:
            drop["已在獵表"] += 1
            continue
        if author_blacklist.match(x["author"], x["title"]):
            drop["黑名單"] += 1
            continue
        # 一本書出兩個目標：中譯本與原文本。使用者的規矩是「有中譯就一起下載，
        # 沒有就只要原文」——語言閘（zlib_fetch.mjs 的 wantLang）會讓找不到中譯的
        # 那一格空手而回，而不是退而抓回同一本原文浪費額度。
        base = stable_id(x["title"], x["author"])
        label = f"{x['author']}《{x['title']}》" if x["author"] else x["title"]
        q = f"{x['title']} {x['author']}".strip()
        title_is_zh = bool(_CJK.search(x["title"]))
        out.append({
            "key": f"bib-{base}-orig",
            "query": q,
            # 書目本身是中文題名時，那就是中譯本的題名，拿它去比對原文版會全數落空，
            # 所以原文那一格不設 expect，只靠作者閘與語言閘把關。
            "expect": "" if title_is_zh else x["title"],
            "who": x["author"],
            "lang": "orig",
            "source": x["source"],
            "zh": label + "（原文）",
        })
        out.append({
            "key": f"bib-{base}-zh",
            "query": q,
            "expect": x["title"] if title_is_zh else "",
            "who": x["author"],
            "lang": "zh",
            "source": x["source"],
            "zh": label + "（中譯）",
        })

    print("\n濾掉：", "  ".join(f"{k} {v}" for k, v in drop.items()))
    print(f"新增可獵 {len(out)} 筆（{len(out)//2} 本書 × 中譯／原文各一格）")
    bysrc = {}
    for x in out:
        bysrc[x["source"]] = bysrc.get(x["source"], 0) + 1
    for s, n in sorted(bysrc.items(), key=lambda kv: -kv[1]):
        print(f"  {s:34} {n:>5}")

    if a.stats:
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"\n→ {OUT}")
    print("接著跑 python scripts/zlib_wanted.py 併進總清單")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
