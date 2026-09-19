"""把《弘誓雙月刊》整期全文切成單篇，保留原書頁碼，並按主題分類。

現況是「一期一個 txt」（R2 `yinshun-hongshi-fulltext/弘誓雙月刊/`），
篇目層另有逐篇的標題、作者與起始頁（`magazine-toc.json`）。本腳本把兩者接起來。

🚨 **不能用「找到篇名就切」。** 這本雜誌的篇名是**逐頁眉標**，同一個篇名在該篇
每一頁（甚至隔頁）都會再出現一次；拿篇名當錨會切出一堆碎片，而且段數看起來還很合理。
切的依據是**頁碼**：篇目給起始頁，下一篇的起始頁前一頁就是本篇結尾。

🚨 **頁碼位移要逐期量，不可假設為 0。** 實測第 80 期印刷頁就等於 PDF 頁，但那是
這一期的事實，不是全刊的通則（有些期有夾頁、彩頁或封面計入差異）。作法是拿篇目的
頁碼到附近幾頁找篇名，投票取眾數位移，並印出同意比例；同意比例太低就不切這一期。

🚨 **對不上的篇目要逐篇點名。** 只報「覆蓋率 92%」等於把那 8% 藏起來
（[[feedback_coverage_metric_denominator]]、[[feedback_silent_zero_is_a_bug]]）。

分類分兩層，來源不同要分清楚：
  - `column`（欄目）＝**雜誌自己的分欄**（薪火相傳／輝映法界／人間探照燈／院務資訊…），
    從目次頁文字解析而來，是第一手事實。
  - `topics`（主題）＝**本專案用關鍵字規則貼的標籤**，是衍生物，會有誤差，
    因此另存欄位、不覆蓋 column。

    python scripts/hongshi_split_articles.py --dry-run            # 只看，逐期報表
    python scripts/hongshi_split_articles.py --dry-run --issue 80 # 只看一期
    python scripts/hongshi_split_articles.py --apply              # 寫 R2 + 索引 JSON
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import fitz

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\弘誓雙月刊")
TOC = REPO / "public/content/research-data/yinshun-hongshi/magazine-toc.json"
OUT = REPO / "public/content/research-data/yinshun-hongshi/magazine-articles.json"
R2_PREFIX = "yinshun-hongshi-fulltext/弘誓雙月刊-單篇"

_STRIP = re.compile(r"[\s　—－\-（）()／/、，。：:；;「」『』？?！!·．…]")

# 關鍵字 → 主題。一篇可以有多個主題；一個都沒中就是「其他」。
TOPIC_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("印順學", ("印順", "妙雲", "華雨", "契理契機")),
    ("戒律與僧制", ("戒律", "律典", "八敬法", "羯磨", "僧團", "比丘尼戒", "波羅提木叉", "結戒", "僧事")),
    ("性別", ("性別", "女性", "比丘尼", "婦女", "兩性", "同志", "父權", "沙文")),
    ("動物與護生", ("動物", "護生", "素食", "放生", "流浪狗", "實驗動物", "經濟動物")),
    ("環境與生態", ("環保", "生態", "土地", "核", "反污染")),
    ("政教關係", ("宗教法", "宗教立法", "宗教自由", "寺產", "政教", "稅", "法案", "釋憲")),
    ("佛教倫理學", ("倫理", "應用倫理", "生命倫理", "中道", "德行")),
    ("禪修與教理", ("禪", "止觀", "唯識", "阿含", "中觀", "般若", "空義", "緣起")),
    ("教育與學團", ("學院", "招生", "課程", "研究部", "專修部", "畢業", "結業", "師生")),
    ("社會運動", ("運動", "抗議", "遊行", "連署", "反賭", "廢死", "樂生", "人權")),
    ("紀念與追思", ("追思", "圓寂", "紀念", "傳供", "讚頌", "百秩", "誕辰")),
    ("學術活動", ("研討會", "學術會議", "論文", "發表", "座談", "講座")),
    ("院務資訊", ("徵信", "決算", "啟事", "公告", "近訊", "活動看板", "看版")),
]


def norm(text: str) -> str:
    return _STRIP.sub("", text or "")


def topics_of(title: str, column: str) -> list[str]:
    hay = f"{title}{column}"
    hits = [name for name, kws in TOPIC_RULES if any(k in hay for k in kws)]
    return hits or ["其他"]


def entries_from_toc_page(doc: fitz.Document, toc_page: int | None) -> list[dict]:
    """目次頁 → [{page, title, column}]。沒有頁碼的短行是欄目標題。

    🚨 目次通常**不只一個區塊**：正文篇章之外還有「院務資訊」那一欄（更正啟示、
    出版資訊、招生啟事、收支決算表…），而 `magazine-toc.json` 只收了正文篇章。
    不把這些收進來，每篇的結尾就會吃掉夾在中間的院務頁——第 80 期最後一篇因此
    多吞了 23 頁。它們也是內容單位，一併當切點。
    """
    if not toc_page or toc_page > doc.page_count:
        return []
    # 🚨 目次常常不只一頁：第 80 期正文篇章在第 2 頁、院務資訊那一欄在第 3 頁。
    #    只讀 toc_page 就會漏掉後半，而漏掉的部分正是夾在各篇之間的切點。
    #    判準是「這一頁有好幾行以頁碼開頭」，而不是硬吃固定頁數。
    lines: list[str] = []
    for p in range(toc_page, min(toc_page + 3, doc.page_count) + 1):
        text = doc[p - 1].get_text()
        numbered = len(re.findall(r"(?m)^\s*\d{1,3}[\s　]+\S", text))
        if p == toc_page or numbered >= 3:
            lines += text.splitlines()
        else:
            break
    out: list[dict] = []
    current = ""
    entry_re = re.compile(r"^\s*\d{1,3}[\s　]+\S")
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        nxt = next((x for x in lines[idx + 1:] if x.strip()), "")
        next_is_entry = bool(entry_re.match(nxt))
        m = re.match(r"^(\d{1,3})[\s　]+(.+)$", line)
        if m:
            out.append({"page": int(m.group(1)),
                        "title": m.group(2).strip("　 ／/"), "column": current})
            continue
        plain = norm(line)
        # 🚨 短行不一定是欄目，也可能是上一條篇名的**續行**（第 80 期的「議程」
        #    就是「第六屆…公告、邀請名冊、議程」被折到下一行，而它的下一行剛好
        #    又是一條帶頁碼的條目，所以光看「下一行是不是條目」擋不住）。
        #    真正分得開的是排版：欄目以全形空白起首，續行是四格以上的半形縮排。
        indented = raw.startswith("    ") and not raw.startswith("　")
        if 2 <= len(plain) <= 8 and not plain.isdigit() and next_is_entry and not indented:
            current = plain
    return out


def strip_boilerplate(pages: list[str]) -> list[str]:
    """逐行剝掉整期重複的裝飾與頁眉。

    🚨 **逐行剝、不整塊丟**（[[feedback_boilerplate_strip_lines_not_blocks]]）：
    第 80 期的側欄「◎本期專題：印順導師百秩晉一誕辰紀念特刊」被排版切成幾十個
    小片段混在正文區塊裡，整塊丟會連正文一起刪。判準是**同一短行在全期出現太多次**。
    """
    freq: Counter[str] = Counter()
    for t in pages:
        for line in {ln.strip() for ln in t.splitlines() if ln.strip()}:
            if len(line) <= 12:
                freq[line] += 1
    noisy = {ln for ln, n in freq.items() if n >= max(5, len(pages) // 4)}
    out = []
    for t in pages:
        out.append("\n".join(ln for ln in t.splitlines() if ln.strip() not in noisy))
    return out


def offset_is_sound(votes: Counter[int], total: int) -> tuple[bool, str]:
    """位移可不可信。

    🚨 判準不是「篇名對上率」。對上率量的是**篇名比對**成不成功——目次寫「玄奘大學
    宗教學系碩士班」而正文印的是招生海報，本來就對不上，但那不表示這一期的頁碼位移
    有問題。實測全刊位移一律 +0，而對上率在 53%–93% 之間跳。
    所以看的是：同意的票數夠不夠多、眾數夠不夠明確。
    """
    if not votes:
        return False, "一篇都沒對上，無從判斷位移"
    ranked = votes.most_common(2)
    top, agree = ranked[0]
    runner = ranked[1][1] if len(ranked) > 1 else 0
    if runner * 2 > agree:
        return False, f"位移莫衷一是（{top:+d} 得 {agree} 票、次高得 {runner} 票）"
    # 🚨 門檻不能只看絕對票數。第一版寫「少於 5 票就不切」，於是第 189 期
    #    4/5 篇（80%）一致同意位移 0 也被跳過——那一期篇目本來就只有 5 篇，
    #    永遠湊不到 5 票。小分母要看比例，大分母才看票數。
    if agree >= 5 or (agree >= 3 and agree / max(total, 1) >= 0.5):
        return True, ""
    if agree >= 2 and len(votes) == 1:
        return True, ""            # 票少但毫無異議
    return False, f"只有 {agree}/{total} 篇同意位移 {top:+d}，證據不足"


def find_offset(doc: fitz.Document, articles: list[dict],
                window: int = 5) -> tuple[int, int, list[dict], Counter]:
    """回傳 (位移, 同意篇數, 每篇的命中結果, 票數分布)。位移＝PDF 頁 − 印刷頁。"""
    votes: Counter[int] = Counter()
    marks: list[dict] = []
    for a in articles:
        needle = norm(a.get("title"))[:10]
        page = a.get("page")
        hit = None
        if needle and len(needle) >= 4 and isinstance(page, int):
            for delta in sorted(range(-window, window + 1), key=abs):
                p = page + delta
                if 1 <= p <= doc.page_count and needle in norm(doc[p - 1].get_text()):
                    hit = delta
                    break
        marks.append({**a, "delta": hit})
        if hit is not None:
            votes[hit] += 1
    if not votes:
        return 0, 0, marks, votes
    offset, agree = votes.most_common(1)[0]
    return offset, agree, marks, votes


def merge_entries(articles: list[dict], toc_entries: list[dict]) -> list[dict]:
    """篇目層（乾淨的標題與作者）＋ 目次頁（含院務資訊那一欄與欄目名）。

    同一頁兩邊都有時以篇目層為準、補上欄目；只有目次頁有的（院務項目）照收，
    標 `fromTocPage`，因為它們同樣是切點，少了它們前一篇就會吃掉它們的頁。
    """
    by_page = {a["page"]: dict(a) for a in articles if isinstance(a.get("page"), int)}
    for e in toc_entries:
        if e["page"] in by_page:
            by_page[e["page"]].setdefault("column", e["column"])
        else:
            by_page[e["page"]] = {"page": e["page"], "title": e["title"], "author": None,
                                  "column": e["column"], "fromTocPage": True}
    return [by_page[p] for p in sorted(by_page)]


def slice_issue(doc: fitz.Document, entries: list[dict], offset: int) -> list[dict]:
    """依頁碼切段。每頁前面加 [p.N] 標記，N 是**原書印刷頁**。"""
    usable = [a for a in entries if isinstance(a.get("page"), int)]
    usable.sort(key=lambda a: a["page"])
    pages = strip_boilerplate([pg.get_text() for pg in doc])
    out = []
    for i, a in enumerate(usable):
        start = a["page"] + offset
        end = (usable[i + 1]["page"] + offset - 1) if i + 1 < len(usable) else doc.page_count
        # 🚨 目次偶爾列出這份 PDF 裡沒有的頁（第 80 期目次到 95 頁、PDF 只有 93 頁）。
        #    那種條目沒有內容可切，丟掉並回報，不要硬夾成 p94–93 這種倒置頁段。
        if start > doc.page_count:
            out.append({**a, "pdf_start": None, "pdf_end": None,
                        "pageEnd": a["page"], "text": "", "beyondPdf": True})
            continue
        start = max(1, start)
        end = max(start, min(end, doc.page_count))
        parts = []
        for p in range(start, end + 1):
            body = pages[p - 1].strip()
            if body:
                parts.append(f"[p.{p - offset}]\n{body}")
        out.append({**a, "pdf_start": start, "pdf_end": end,
                    "pageEnd": end - offset, "text": "\n\n".join(parts)})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="寫 R2 與索引（預設只看）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--issue", type=int, action="append", help="只做某幾期")
    ap.add_argument("--merge", action="store_true",
                    help="把這次的結果併進既有索引（只重跑幾期時用），不要整份覆蓋")
    args = ap.parse_args()

    toc = json.loads(TOC.read_text(encoding="utf-8"))
    if args.issue:
        toc = [t for t in toc if t.get("issue") in args.issue]
    index_path = TOC.with_name("magazine-index.json")
    index_parts = {x["issue"]: x.get("parts") or []
                   for x in json.loads(index_path.read_text(encoding="utf-8"))} \
        if index_path.exists() else {}

    s3 = None
    if args.apply:
        import boto3
        from dotenv import load_dotenv
        load_dotenv(REPO / ".env")
        s3 = boto3.client("s3", region_name="auto", endpoint_url=os.environ["R2_ENDPOINT"],
                          aws_access_key_id=os.environ["R2_ACCESS_KEY"],
                          aws_secret_access_key=os.environ["R2_SECRET_KEY"])
        bucket = os.environ["R2_BUCKET"]

    index, skipped, unmatched_all = [], [], []
    total_articles = total_written = 0
    for entry in sorted(toc, key=lambda t: t.get("issue") or 0):
        issue = entry.get("issue")
        arts = entry.get("articles") or []
        # 🚨 少數幾期的原檔是分冊的（第 200 期切成 p1／p2）。只開第一冊的話，
        #    後半本的頁全部落在 PDF 之外，切出來會是一堆空篇而且看起來像「目次列到
        #    PDF 以外」。分冊要按順序接成一本再切。
        parts = [p["key"].split("/")[-1] for p in (index_parts.get(issue) or [])]
        files = parts or [entry.get("file") or f"弘誓雙月刊-{issue:03d}.pdf"]
        paths = [SRC / f for f in files]
        if not arts:
            skipped.append((issue, "篇目層是空的"))
            continue
        missing = [p.name for p in paths if not p.exists()]
        if missing:
            skipped.append((issue, f"PDF 不在：{'、'.join(missing)}"))
            continue
        try:
            doc = fitz.open(str(paths[0]))
            for extra_path in paths[1:]:
                with fitz.open(str(extra_path)) as nxt:
                    doc.insert_pdf(nxt)
        except Exception as e:
            skipped.append((issue, f"PDF 開不起來：{type(e).__name__}"))
            continue
        total_articles += len(arts)
        offset, agree, marks, votes = find_offset(doc, arts)
        rate = agree / len(arts)
        unmatched = [m for m in marks if m["delta"] is None]
        print(f"第 {issue:>3} 期　{len(arts):>2} 篇　位移 {offset:+d}　"
              f"對上 {agree}/{len(arts)}（{rate:.0%}）　{doc.page_count} 頁")
        for m in unmatched:
            print(f"      ✗ 對不上：印刷頁 {m.get('page')} 《{(m.get('title') or '')[:34]}》")
            unmatched_all.append({"issue": issue, **{k: m.get(k) for k in ('page', 'title', 'author')}})
        sound, why = offset_is_sound(votes, len(arts))
        if not sound:
            skipped.append((issue, why))
            doc.close()
            continue
        toc_entries = entries_from_toc_page(doc, entry.get("toc_page"))
        merged = merge_entries(arts, toc_entries)
        extra = len(merged) - len(arts)
        if extra:
            print(f"      ＋目次頁另有 {extra} 個切點（院務資訊等），一併切開")
        pieces = slice_issue(doc, merged, offset)
        arts_out = []
        for p in pieces:
            column = p.get("column") or ""
            title = (p.get("title") or "").strip()
            h = hashlib.sha1(f"{issue}-{p['page']}-{title}".encode()).hexdigest()[:8]
            safe = re.sub(r'[\\/:*?"<>|]', "", title)[:40]
            key = f"{R2_PREFIX}/{issue:03d}-{p['page']:03d}-{safe}-{h}.txt"
            rec = {"title": title, "author": p.get("author"), "column": column,
                   "page": p["page"], "pageEnd": p["pageEnd"],
                   "topics": topics_of(title, column), "chars": len(p["text"]),
                   "srcKey": key[len("yinshun-hongshi-fulltext/"):].rsplit(".txt", 1)[0]}
            if p.get("fromTocPage"):
                rec["fromTocPage"] = True          # 這筆的標題來自目次頁、不是篇目層
            if p.get("beyondPdf"):
                # 🚨 這個旗標第一版漏了複製進索引，於是「目次列到 PDF 以外」的條目
                #    在索引裡長得跟「切出來是空的」一模一樣，稽核分不出是來源缺頁
                #    還是切壞了。旗標要跟著資料走。
                rec["beyondPdf"] = True
            arts_out.append(rec)
            if args.apply and p["text"].strip():
                s3.put_object(Bucket=bucket, Key=key,
                              Body=p["text"].encode("utf-8"),
                              ContentType="text/plain; charset=utf-8")
                total_written += 1
        index.append({"issue": issue, "offset": offset, "matchRate": round(rate, 3),
                      "articles": arts_out})
        doc.close()

    print(f"\n處理 {len(index)} 期、{sum(len(e['articles']) for e in index)} 篇"
          f"（篇目分母 {total_articles}）")
    if unmatched_all:
        print(f"🚨 篇名對不上頁面的共 {len(unmatched_all)} 篇（已逐篇列於上）")
    if skipped:
        print(f"跳過 {len(skipped)} 期：")
        for issue, why in skipped:
            print(f"   第 {issue} 期：{why}")
    if args.apply:
        if args.merge and OUT.exists():
            old = {e["issue"]: e for e in json.loads(OUT.read_text(encoding="utf-8"))}
            for e in index:
                old[e["issue"]] = e
            index = [old[k] for k in sorted(old)]
            print(f"（併入既有索引，現共 {len(index)} 期）")
        OUT.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✓ 寫出 {total_written} 篇全文到 R2；索引 → {OUT}")
    else:
        print("\n（預設不寫。要寫加 --apply）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
