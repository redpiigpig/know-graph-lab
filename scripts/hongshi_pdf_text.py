"""印順學派／弘誓相關刊物的 PDF 抽字層。

四批期刊都是本專案自己抓下來的 PDF，逐頁抽文字存成 JSONL：

    弘誓雙月刊    117 期   研究資料/印順學派與弘誓/弘誓雙月刊
    玄奘佛學研究   304 期   研究資料/印順學派與弘誓/玄奘佛學研究
    法印學報       30 期   研究資料/印順學派與弘誓/法印學報
    福嚴會訊       71 期   研究資料/大愛道革命/論文資料/福嚴會訊

🚨 **不要 OCR。** 跟 J-Stage 那批一樣，這些 PDF 有文字層，PyMuPDF 直接抽得到。
   整批走 OCR 會白燒配額而且品質更差（見 [[feedback_ocr_strategy]]）。
   真的抽不到字的那幾期才退 OCR，本檔會把它們單獨列出來。

🚨 **一頁一筆，頁碼用 PDF 頁序，不自編流水號。** PDF 是一頁一 chunk 的那一類，
   頁序就是真頁碼（見 [[feedback_transcribe_page_numbers]]）。
   另外盡量抓出**印刷頁碼**（版心印的那個數字）——它跟 PDF 頁序常常差幾頁
   （封面、廣告、版權頁），而弘誓雙月刊的篇目表記的是印刷頁碼。
   兩個都存，缺一個就對不上篇目。

  python scripts/hongshi_pdf_text.py --survey            # 只看文字層狀況
  python scripts/hongshi_pdf_text.py --extract           # 抽字（可續跑）
  python scripts/hongshi_pdf_text.py --extract --set 弘誓雙月刊
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

R = Path("G:/我的雲端硬碟/資料/知識圖工作室/研究資料")
OUT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/hongshi")

SETS: dict[str, Path] = {
    "弘誓雙月刊":   R / "印順學派與弘誓" / "弘誓雙月刊",
    "玄奘佛學研究": R / "印順學派與弘誓" / "玄奘佛學研究",
    "法印學報":     R / "印順學派與弘誓" / "法印學報",
    "福嚴會訊":     R / "大愛道革命" / "論文資料" / "福嚴會訊",
    # 這兩批抓下來就是純文字（官網是 HTML），不必抽字，但要收進同一份
    # 語料格式才查得到——不然它們在 Drive 上有檔、在語料層卻不存在。
    "弘誓電子報":   R / "印順學派與弘誓" / "電子報",
    "學團日誌":     R / "印順學派與弘誓" / "學團日誌",
    "歷屆學術活動": R / "印順學派與弘誓" / "學術活動",
}
# 純文字的那幾批。PDF 一頁一筆，純文字一檔一筆（它們本來就是一期一篇）。
TEXT_SETS = {"弘誓電子報", "學團日誌", "歷屆學術活動"}

# 每頁少於這麼多字就當這一頁沒有文字層（圖版頁、廣告頁本來就少字，
# 所以判準放在「整份」而不是「單頁」，單頁只用來算比例）
PAGE_MIN = 80
# 整份平均每頁低於這個字數，或空白頁超過三成，就列為要 OCR
DOC_MIN_PER_PAGE = 300
EMPTY_RATIO = 0.30

# 版心的印刷頁碼：孤立出現在頁首或頁尾的數字
PRINTED_HEAD = re.compile(r"^\s*(\d{1,4})\s*$")


def clean(s: str) -> str:
    """只做機械性清理：正規化、收多重空白、去零寬字元。不改字。

    OCR 或抽字認錯的留著——看得見的錯遠好過被掩蓋的錯。
    """
    s = s.replace("\u00ad", "").replace("\u200b", "").replace("\ufeff", "")
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[ \t\u3000]+", " ", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def printed_page(text: str) -> int | None:
    """從頁首／頁尾撈印刷頁碼。撈不到回 None——**不要用 PDF 頁序頂替**，
    那會產生一個看起來像真頁碼的假頁碼。"""
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    for cand in (lines[:2] + lines[-2:]) if lines else []:
        m = PRINTED_HEAD.match(cand)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 2000:
                return n
    return None


def docs(name: str) -> list[Path]:
    d = SETS[name]
    if not d.exists():
        return []
    return sorted(d.glob("*.txt" if name in TEXT_SETS else "*.pdf"))


def scan(path: Path):
    """回 (頁數, [每頁文字])。開不起來就丟例外給呼叫端記錄。"""
    import fitz
    doc = fitz.open(path)
    pages = [p.get_text() for p in doc]
    doc.close()
    return len(pages), pages


def cmd_survey(only: str | None) -> None:
    for name in ([only] if only else list(SETS)):
        files = docs(name)
        if not files:
            print(f"\n━━ {name}：找不到檔（{SETS[name]}）")
            continue
        tot_p = tot_c = 0
        thin, broken, printed_ok = [], [], 0
        for f in files:
            try:
                n, pages = scan(f)
            except Exception as e:                # noqa: BLE001
                broken.append((f.name, type(e).__name__))
                continue
            chars = sum(len(p.strip()) for p in pages)
            empty = sum(1 for p in pages if len(p.strip()) < PAGE_MIN)
            printed_ok += sum(1 for p in pages if printed_page(p) is not None)
            tot_p += n
            tot_c += chars
            per = chars / n if n else 0
            if per < DOC_MIN_PER_PAGE or (n and empty / n > EMPTY_RATIO):
                thin.append((f.name, n, empty, per))
        print(f"\n━━ {name}　{len(files)} 檔・{tot_p:,} 頁・{tot_c:,} 字"
              f"（每頁均 {tot_c / max(1, tot_p):.0f} 字）")
        print(f"   撈得到印刷頁碼的頁：{printed_ok:,}／{tot_p:,}"
              f"（{printed_ok / max(1, tot_p) * 100:.0f}%）")
        if broken:
            print(f"   ✗ 開不起來 {len(broken)}：{broken[:5]}")
        if thin:
            print(f"   ⚠ 要 OCR 的 {len(thin)} 檔：")
            for nm, n, empty, per in sorted(thin, key=lambda x: x[3])[:12]:
                print(f"      {nm[:42]:<44}{n:>4} 頁  空白 {empty:>4}  每頁 {per:>6.0f} 字")
        else:
            print("   ✓ 全部都有文字層")


def cmd_extract(only: str | None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ([only] if only else list(SETS)):
        files = docs(name)
        if not files:
            print(f"{name}：找不到檔，略過")
            continue
        dst = OUT / f"{name}.jsonl"
        done: set[str] = set()
        if dst.exists():
            for line in dst.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        done.add(json.loads(line)["file"])
                    except (ValueError, KeyError):
                        pass
        todo = [f for f in files if f.name not in done]
        print(f"\n{name}：{len(files)} 檔，已抽 {len(done)}，本輪 {len(todo)}")
        if not todo:
            continue
        if name in TEXT_SETS:
            rows = 0
            with dst.open("a", encoding="utf-8") as fh:
                for f in todo:
                    t = clean(f.read_text(encoding="utf-8", errors="replace"))
                    if not t:
                        print(f"   ⚠ {f.name}：空檔，略過")
                        continue
                    # 首行通常是「弘誓電子報 第 529 期　2025/07/27」，留著當標頭
                    head = t.splitlines()[0][:80]
                    fh.write(json.dumps({
                        "set": name, "file": f.name, "head": head,
                        "chars": len(t), "text": t,
                    }, ensure_ascii=False) + "\n")
                    rows += 1
                fh.flush()
            print(f"   ✓ {rows} 篇 → {dst}")
            continue

        rows = wrote = skipped = 0
        # 🚨 逐檔 append 並 flush：522 個 PDF 從 Drive 讀要跑很久，
        #    筆電中途休眠是常態，不能等全部跑完才寫檔。
        with dst.open("a", encoding="utf-8") as fh:
            for i, f in enumerate(todo, 1):
                try:
                    n, pages = scan(f)
                except Exception as e:            # noqa: BLE001
                    print(f"   ✗ {f.name}：{type(e).__name__}")
                    skipped += 1
                    continue
                chars = sum(len(p.strip()) for p in pages)
                if n and chars / n < DOC_MIN_PER_PAGE:
                    # 文字層太薄，留給 OCR，別寫半份進來假裝抽好了
                    print(f"   ⚠ {f.name}：每頁僅 {chars / n:.0f} 字，留待 OCR")
                    skipped += 1
                    continue
                for k, raw in enumerate(pages, 1):
                    t = clean(raw)
                    if not t:
                        continue
                    fh.write(json.dumps({
                        "set": name, "file": f.name,
                        "pdf_page": k, "pages": n,
                        "printed_page": printed_page(raw),
                        "chars": len(t), "text": t,
                    }, ensure_ascii=False) + "\n")
                    rows += 1
                fh.flush()
                wrote += 1
                if i % 20 == 0:
                    print(f"   …{i}/{len(todo)}　{rows:,} 頁", flush=True)
        print(f"   ✓ {wrote} 檔・{rows:,} 頁 → {dst}"
              + (f"（{skipped} 檔留待 OCR）" if skipped else ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--survey", action="store_true")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--set", dest="only", choices=list(SETS))
    a = ap.parse_args()
    if a.survey:
        cmd_survey(a.only)
    elif a.extract:
        cmd_extract(a.only)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
