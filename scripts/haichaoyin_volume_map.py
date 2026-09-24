"""由 _篇目_海潮音_集成.tsv（DILA）＋已下載 PDF 產生「集成冊次 ↔《海潮音》卷期」對照表。

輸出 Drive 正編夾 _對照表_海潮音_集成冊次.tsv：
冊、原刊卷期（第一筆～最後一筆）、涵蓋卷、期數、篇目數、集成頁起訖（DILA 最小～最大頁）、PDF 頁數、
PDF 有無文字層（抽 3 頁）、檔名、備註（DILA 缺卷等）。
"""
import csv, re, sys
from collections import defaultdict
from pathlib import Path
import fitz

D = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\正編")
TOC = D / "_篇目_海潮音_集成.tsv"
OUT = D / "_對照表_海潮音_集成冊次.tsv"


def pnum(s):
    m = re.match(r"(\d+)", s or "")
    return int(m.group(1)) if m else None


def pend(s):
    nums = re.findall(r"\d+", s or "")
    return int(nums[-1]) if nums else None


def main():
    rows = list(csv.DictReader(open(TOC, encoding="utf-8-sig"), delimiter="\t"))
    by = defaultdict(list)
    for r in rows:
        if r["集成冊"].isdigit():
            by[int(r["集成冊"])].append(r)
    all_vols = set()
    out = []
    for vol in range(147, 205):
        rs = by.get(vol, [])
        issues = []
        for r in rs:
            k = (r["原刊卷"], r["原刊期"])
            if k not in issues:
                issues.append(k)
        juan = sorted({pnum(v) for v, _ in issues if pnum(v)})
        all_vols.update(juan)
        pages = [pnum(r["集成頁"]) for r in rs if pnum(r["集成頁"])]
        pends = [x for x in (pend(r["集成頁"]) for r in rs) if x and x <= 1000]   # DILA 偶有「5730574」這種黏字，濾掉
        dates = sorted(r["日期"] for r in rs if re.match(r"\d{4}", r["日期"] or ""))
        f = next(iter(D.glob(f"*正編 第{vol}卷 *.pdf")), None)
        npages, textlayer = "", ""
        if f:
            try:
                doc = fitz.open(f)
                npages = doc.page_count
                probe = [10, npages // 2, npages - 20]
                chars = sum(len(doc[p].get_text().strip()) for p in probe if 0 <= p < npages)
                textlayer = "有" if chars > 50 else "無（純影像）"
            except Exception as e:
                npages, textlayer = "", f"開檔失敗 {e}"
        first = f"卷{issues[0][0]}期{issues[0][1]}" if issues else ""
        last = f"卷{issues[-1][0]}期{issues[-1][1]}" if issues else ""
        out.append({"集成冊": vol, "原刊起": first, "原刊迄": last,
                    "涵蓋卷": "、".join(map(str, juan)), "期數": len(issues), "篇目數": len(rs),
                    "集成頁起": min(pages) if pages else "", "集成頁迄": max(pends) if pends else "",
                    "日期起": dates[0] if dates else "", "日期迄": dates[-1] if dates else "",
                    "PDF頁數": npages, "文字層": textlayer, "檔名": f.name if f else "（未下載）", "備註": ""})
    # DILA 沒收的卷：找集成冊裡篇目缺的、或卷號跳號
    lo, hi = min(all_vols), max(all_vols)
    missing = [v for v in range(lo, hi + 1) if v not in all_vols]
    for o in out:
        if o["篇目數"] == 0:
            o["備註"] = "DILA 此冊零篇目（疑為缺收卷所在，需讀 PDF 目錄頁）"
    # 跳號卷落在哪幾冊之間
    for m in missing:
        before = [o for o in out if o["涵蓋卷"] and max(map(int, o["涵蓋卷"].split("、"))) < m]
        after = [o for o in out if o["涵蓋卷"] and min(map(int, o["涵蓋卷"].split("、"))) > m]
        b = before[-1]["集成冊"] if before else None
        a = after[0]["集成冊"] if after else None
        for o in out:
            if b and a and b <= o["集成冊"] <= a:
                note = f"DILA 缺第 {m} 卷篇目"
                if note not in o["備註"]:
                    o["備註"] = (o["備註"] + "；" if o["備註"] else "") + note
    with open(OUT, "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0]), delimiter="\t")
        w.writeheader(); w.writerows(out)
    print(f"篇目 {len(rows)}；卷 {lo}–{hi}；DILA 缺卷 {missing}")
    for o in out:
        print(o["集成冊"], o["原刊起"], o["原刊迄"], o["涵蓋卷"], o["期數"], o["篇目數"], o["集成頁起"], o["集成頁迄"], o["PDF頁數"], o["文字層"], o["備註"])


if __name__ == "__main__":
    main()
