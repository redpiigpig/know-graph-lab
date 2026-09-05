# -*- coding: utf-8 -*-
"""千面上帝：逐章稽核，抓「看起來正常但其實錯了」的那一類。

這條管線會靜默出錯的地方就那幾個，一次全查：

  1. 節數對不上綱要 ── 模型漏寫一節，檔案照樣長得很正常
  2. 節名被改寫    ── 標題比對是靠字串，改了字就對不回目錄
  3. 殘留 〔註:E12〕 ── 解析漏掉，等於正文裡印出內部記號
  4. 註號不連續    ── 引用與註文對不起來
  5. 有引用卻沒註文／有註文卻沒人引用
  6. 殘留 markdown ── ** 或 * 會原樣印進 Word
  7. 篇幅異常      ── 明顯短於同批其他章的，多半是被壓縮或截斷

用法：python scripts/qianmian_check.py
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "output" / "qianmian" / "sources"
CH = ROOT / "output" / "qianmian" / "chapters"

FN_DEF = re.compile(r"^\[\^(\d+)\]:\s*(.+)$", re.M)
FN_REF = re.compile(r"\[\^(\d+)\]")


def check(no):
    meta = json.loads((SRC / f"ch{no:02d}.json").read_text(encoding="utf-8"))
    f = CH / f"ch{no:02d}.md"
    if not f.exists():
        return None, [f"第{no}章 尚未寫出"]
    text = f.read_text(encoding="utf-8")
    bad = []

    body = FN_DEF.sub("", text)
    heads = [m.group(1).strip() for m in re.finditer(r"(?m)^##\s+(.+)$", body)]
    want = list(meta["sections"])

    missing = [s for s in want if s not in heads]
    extra = [h for h in heads if h not in want and h != "結語"]
    if missing:
        bad.append(f"缺節 {len(missing)}／{len(want)}：{missing}")
    if extra:
        bad.append(f"多出或被改寫的節名：{extra}")
    if "結語" not in heads:
        bad.append("沒有結語")

    if "〔註" in body:
        bad.append(f"殘留未解析的註記號 {body.count('〔註')} 個")

    defs = {int(n): t for n, t in FN_DEF.findall(text)}
    refs = [int(n) for n in FN_REF.findall(body)]
    if refs and sorted(set(refs)) != list(range(1, max(refs) + 1)):
        bad.append("正文的註號不連續")
    orphan_ref = sorted(set(refs) - set(defs))
    orphan_def = sorted(set(defs) - set(refs))
    if orphan_ref:
        bad.append(f"引用了但沒有註文：{orphan_ref[:8]}")
    if orphan_def:
        bad.append(f"有註文但沒人引用：{orphan_def[:8]}")

    md = re.findall(r"\*\*[^*\n]+\*\*|(?<![*\w])\*[^*\n]+\*(?![*\w])", body)
    if md:
        bad.append(f"殘留 markdown 標記 {len(md)} 處，例：{md[0][:24]}")

    chars = len(re.sub(r"[#>\s\[\]\^\d]", "", body))
    return {"no": no, "title": meta["title"], "chars": chars,
            "sections": f"{len(want) - len(missing)}/{len(want)}",
            "notes": len(defs)}, bad


def main():
    rows, problems = [], {}
    for no in range(1, 29):
        row, bad = check(no)
        if row:
            rows.append(row)
        if bad:
            problems[no] = bad

    if rows:
        avg = sum(r["chars"] for r in rows) / len(rows)
        print(f"{'章':>3} {'節':>7} {'字數':>7} {'註':>4}  標題")
        for r in rows:
            flag = "  ← 明顯偏短" if r["chars"] < avg * 0.6 else ""
            print(f"{r['no']:3d} {r['sections']:>7} {r['chars']:7d} {r['notes']:4d}  {r['title']}{flag}")
        print(f"\n共 {len(rows)}/28 章、{sum(r['chars'] for r in rows):,} 字、"
              f"{sum(r['notes'] for r in rows):,} 個註，平均每章 {avg:,.0f} 字")

    if problems:
        print("\n=== 要處理的 ===")
        for no, bad in problems.items():
            for b in bad:
                print(f"  第{no}章：{b}")
    elif rows:
        print("\n稽核全過。")


if __name__ == "__main__":
    main()
